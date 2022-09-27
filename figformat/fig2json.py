from . import decodefig, decodevectornetwork
from .fignode import FigNode


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

    return tree


def transform_node(fig, node, figma_zip):
    # Extract ID
    guid = node.pop('guid')
    node['id'] = f"{guid['sessionID']}:{guid['localID']}"
    node['children'] = []

    # Extract parent ID
    if 'parentIndex' in node:
        parent = node.pop('parentIndex')
        node['parent'] = {
            'id': f"{parent['guid']['sessionID']}:{parent['guid']['localID']}",
            'position': parent['position']
        }

    if 'vectorData' in node:
        blob_id = node['vectorData']['vectorNetworkBlob']
        scale = node['vectorData']['normalizedSize']
        vector_network = decodevectornetwork.decode(fig, blob_id, scale)
        node['vectorNetwork'] = vector_network

    # Images
    # TODO: Convert to .png
    for paint in node.get('fillPaints', []):
        if 'image' in paint:
            hash = bytes(paint['image']['hash']).hex()
            paint['image']['hash'] = hash
            with open(f"output/images/{hash}.png", 'wb') as f:
                if figma_zip is not None:
                    f.write(figma_zip.open(f'images/{hash}').read())
                else:
                    f.write(bytes(fig['blobs'][paint['image']['dataBlob']]['bytes']))

    return FigNode(node)
