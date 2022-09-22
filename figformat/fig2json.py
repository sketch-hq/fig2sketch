import figformat.decodefig as decodefig
import sys
import math


def transform_node(node):
    # Extract ID
    guid = node.pop("guid")
    node["id"] = f"{guid['sessionID']}:{guid['localID']}"
    node["children"] = []

    # Extract parent ID
    parent = None
    if 'parentIndex' in node:
        parent = node.pop("parentIndex")
        # TODO: parent.position?
        parent = f"{parent['guid']['sessionID']}:{parent['guid']['localID']}"

    # Transform properties to be more similar to JSON Exporter output
    node["x"] = node["transform"]["m02"]
    node["y"] = node["transform"]["m12"]
    node["relativeTransform"] = [
        [node["transform"]["m00"], node["transform"]["m01"], node["transform"]["m02"]],
        [node["transform"]["m10"], node["transform"]["m11"], node["transform"]["m12"]],
    ]
    node["rotation"] = math.degrees(
        math.atan2(-node["transform"]["m10"], node["transform"]["m00"]))
    
    if "size" in node:
        node["width"] = node["size"]["x"]
        node["height"] = node["size"]["y"]

    if "fillPaints" in node:
        node["fills"] = node["fillPaints"]
    if "strokePaints" in node:
        node["strokes"] = node["strokePaints"]

    return node, parent


def convert_fig(reader):
    fig = decodefig.decode(reader)

    # Load all nodes into a map
    id_map = {}
    root = None

    for node in fig["nodeChanges"]:
        node, parent = transform_node(node)
        id = node["id"]
        id_map[id] = (node, parent)

        if not root:
            root = id

    # Build the tree
    tree = {"document": id_map[root][0]}
    for (id, (node, parent)) in id_map.items():
        if not parent:
            continue

        id_map[parent][0]["children"].append(node)

    return tree


if __name__ == '__main__':
    import json

    print(json.dumps(convert_fig(open(sys.argv[1], 'rb')), indent=2))
