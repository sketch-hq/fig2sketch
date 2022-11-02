import io
from PIL import Image, UnidentifiedImageError
from . import decodefig, decodevectornetwork
import utils
import functools
import logging
import shutil


def convert_fig(reader, output):
    fig, figma_zip = decodefig.decode(reader)

    if figma_zip is not None:
        shutil.copyfileobj(
            figma_zip.open(f'thumbnail.png', 'r'),
            output.open(f'previews/preview.png', 'w')
        )

    # Load all nodes into a map
    id_map = {}
    root = None

    for node in fig['nodeChanges']:
        node = transform_node(fig, node, figma_zip, output)
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


def transform_node(fig, node, figma_zip, output):
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
        vector_network = decodevectornetwork.decode(fig, blob_id, scale, style_table_override)
        node['vectorNetwork'] = vector_network

    # Images
    for paint in node.get('fillPaints', []):
        if 'image' in paint:
            fname = bytes(paint['image']['hash']).hex()
            paint['image']['filename'] = convert_image(fname, figma_zip, output)

    if 'symbolData' in node:
        for override in node['symbolData'].get('symbolOverrides', []):
            for paint in override.get('fillPaints', []):
                if 'image' in paint:
                    fname = bytes(paint['image']['hash']).hex()
                    paint['image']['filename'] = convert_image(fname, figma_zip, output)

    return node


@functools.cache
def convert_image(fname, figma_zip, output):
    logging.info(f'Converting image {fname}')
    try:
        if figma_zip is not None:
            fd = figma_zip.open(f'images/{fname}')
        else:
            fd = io.BytesIO(bytes(fig['blobs'][paint['image']['dataBlob']]['bytes']))

        image = Image.open(fd)

        # Save to memory, calculate hash, and save
        out = io.BytesIO()
        if image.format == 'PNG':
            # No need to convert if it's already a PNG
            fd.seek(0)
            while buf := fd.read(16536):
                out.write(buf)
        else:
            image.save(out, format='png')

        fhash = utils.generate_file_ref(out.getbuffer())

        output.open(f'images/{fhash}.png', 'w').write(out.getbuffer())
        return fhash
    except UnidentifiedImageError as e:
        logging.critical(f"Could not convert image {fname}. It appears to be corrupted.")
        logging.critical(f"Try passing `--force-convert-images` to ignore this error and try to convert the image anyway.")
        exit(1)
