from . import decodefig
from .fignode import FigNode


def transform_node(node):
    # Extract ID
    guid = node.pop("guid")
    node["id"] = f"{guid['sessionID']}:{guid['localID']}"
    node["children"] = []

    # Extract parent ID
    if 'parentIndex' in node:
        parent = node.pop("parentIndex")
        node["parent"] = {
            "id": f"{parent['guid']['sessionID']}:{parent['guid']['localID']}",
            "position": parent["position"]
        }

    return FigNode(node)


def convert_fig(reader):
    fig = decodefig.decode(reader)

    # Load all nodes into a map
    id_map = {}
    root = None

    for node in fig["nodeChanges"]:
        node = transform_node(node)
        id = node["id"]
        id_map[id] = node

        if not root:
            root = id

    # Build the tree
    tree = {"document": id_map[root]}
    for node in id_map.values():
        if not "parent" in node:
            continue

        id_map[node["parent"]["id"]]["children"].append(node)

    # Sort children
    for node in id_map.values():
        node["children"].sort(key=lambda n: n["parent"]["position"])

    return tree
