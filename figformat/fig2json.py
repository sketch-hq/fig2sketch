from . import decodefig, decodevectornetwork
from .fignode import FigNode


def transform_node(fig, node):
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

    return FigNode(node)


def convert_fig(reader):
    fig = decodefig.decode(reader)

    # Load all nodes into a map
    id_map = {}
    root = None

    for node in fig['nodeChanges']:
        node = transform_node(fig, node)
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
