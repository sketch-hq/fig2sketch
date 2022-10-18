import io
from PIL import Image
from . import decodefig, decodevectornetwork
from .fignode import FigNode
import utils


def convert_fig(reader):
    fig, figma_zip = decodefig.decode(reader)

    # Load all nodes into a map
    id_map = {}
    root = None

    for node in fig['nodeChanges']:
        node = transform_node(fig, node, figma_zip)
        node_id = node['id']
        id_map[node_id] = node

        if not root:
            root = node_id

    # Build the tree
    tree = {'document': id_map[root]}
    for node in id_map.values():
        if 'parent' not in node:
            continue

        id_map[node['parent']['id']]['children'].append(node)

    # Sort children
    for node in id_map.values():
        node['children'].sort(key=lambda n: n['parent']['position'])

    return tree, id_map


def transform_node(fig, node, figma_zip):
    # Extract ID
    guid = node.pop('guid')
    node['id'] = (guid['sessionID'], guid['localID'])
    node['children'] = []

    # Extract parent ID
    if 'parentIndex' in node:
        parent = node.pop('parentIndex')
        node['parent'] = {
            'id': (parent['guid']['sessionID'], parent['guid']['localID']),
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

            if figma_zip is not None:
                image = Image.open(figma_zip.open(f'images/{fname}'))
            else:
                image = Image.open(
                    io.BytesIO(bytes(fig['blobs'][paint['image']['dataBlob']]['bytes'])))

            # Save to memory, calculate hash, and save
            out = io.BytesIO()
            image.save(out, format='png')
            fhash = utils.generate_file_ref(out.getbuffer())
            open(f'output/images/{fhash}.png', 'wb').write(out.getbuffer())
            paint['image']['filename'] = fhash

    return FigNode(node)
