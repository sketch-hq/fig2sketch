import functools
import io
import logging
import shutil
from typing import Tuple, Sequence, Dict, IO
from converter import utils
from zipfile import ZipFile
from . import decodefig, vector_network
from PIL import Image, UnidentifiedImageError


def convert_fig(path: str, output: ZipFile) -> Tuple[dict, Dict[Sequence[int], dict]]:
    fig, fig_zip = decodefig.decode(path)

    if fig_zip and output:
        shutil.copyfileobj(
            fig_zip.open(f'thumbnail.png', 'r'),
            output.open(f'previews/preview.png', 'w')
        )

    # Load all nodes into a map
    id_map = {}
    root = None

    for node in fig['nodeChanges']:
        node = transform_node(fig, node, fig_zip, output)
        node_id = node['guid']
        id_map[node_id] = node

        if not root:
            root = node_id

    # Build the tree
    tree = {'document': id_map[root]}
    for node in id_map.values():
        if 'parent' not in node:
            continue

        id_map[node['parent']['guid']]['children'].append(node)

    # Sort children
    for node in id_map.values():
        node['children'].sort(key=lambda n: n['parent']['position'])

    return tree, id_map


def transform_node(fig, node, fig_zip, output):
    node['children'] = []

    # Extract parent ID
    if 'parentIndex' in node:
        parent = node.pop('parentIndex')
        node['parent'] = {
            'guid': parent['guid'],
            'position': parent['position']
        }

    if 'vectorData' in node:
        blob_id = node['vectorData']['vectorNetworkBlob']
        scale = node['vectorData']['normalizedSize']
        style_table_override = utils.get_style_table_override(node['vectorData'])
        network = vector_network.decode(fig, blob_id, scale, style_table_override)
        node['vectorNetwork'] = network

    # Images
    for paint in node.get('fillPaints', []):
        if 'image' in paint:
            fname = bytes(paint['image']['hash']).hex()
            blob_id = paint['image'].get('dataBlob')
            blob = bytes(fig['blobs'][blob_id]['bytes']) if blob_id else None
            paint['image']['filename'] = convert_image(fname, blob, fig_zip, output)

    if 'symbolData' in node:
        for override in node['symbolData'].get('symbolOverrides', []):
            for paint in override.get('fillPaints', []):
                if 'image' in paint:
                    fname = bytes(paint['image']['hash']).hex()
                    blob_id = paint['image'].get('dataBlob')
                    blob = bytes(fig['blobs'][blob_id]['bytes']) if blob_id else None
                    paint['image']['filename'] = convert_image(fname, blob, fig_zip, output)

    return node


converted_images: Dict[str, str] = {}
def convert_image(fname, blob, fig_zip, output):
    img = converted_images.get(fname)
    if img:
        return img

    logging.info(f'Converting image {fname}')
    try:
        if fig_zip is not None:
            fd = fig_zip.open(f'images/{fname}')
        else:
            fd = io.BytesIO(blob)

        image = Image.open(fd)

        # Save to memory, calculate hash, and save
        out = io.BytesIO()
        if image.format in ['PNG', 'JPEG']:
            # No need to convert if it's already a PNG or JPEG
            fd.seek(0)
            while buf := fd.read(16536):
                out.write(buf)
            extension = '' if image.format == 'JPEG' else '.png'
        else:
            image.save(out, format='png')
            extension = '.png'

        fhash = utils.generate_file_ref(out.getbuffer())
        output.open(f'images/{fhash}{extension}', 'w').write(out.getbuffer())
        converted_images[fname] = f'{fhash}{extension}'
        return f'{fhash}{extension}'
    except UnidentifiedImageError as e:
        logging.critical(f"Could not convert image {fname}. It appears to be corrupted.")
        logging.critical(
            f"Try passing `--force-convert-images` to ignore this error and try to convert the image anyway.")
        exit(1)
