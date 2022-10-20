import io
from PIL import Image
from . import decodefig, decodevectornetwork
import utils


def convert_fig(reader, output):
    fig, figma_zip = decodefig.decode(reader)

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


converted_images = {}
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
            if fname not in converted_images:
                if figma_zip is not None:
                    image = Image.open(figma_zip.open(f'images/{fname}'))
                else:
                    image = Image.open(
                        io.BytesIO(bytes(fig['blobs'][paint['image']['dataBlob']]['bytes'])))

                # Save to memory, calculate hash, and save
                out = io.BytesIO()
                image.save(out, format='png')
                fhash = utils.generate_file_ref(out.getbuffer())

                output.open(f'images/{fhash}.png', 'w').write(out.getbuffer())
                converted_images[fname] = fhash

            paint['image']['filename'] = converted_images[fname]

    return node
