import json
import shutil
import os
import sys

import converter.document as Document
import converter.meta as Meta
import converter.user as User
import converter.tree as tree

components = []


def convert_pages(figma_pages):
    pages = []

    for figma_page in figma_pages:
        page = tree.convert_root_node(figma_page)
        json.dump(page, open(f'output/pages/{page["do_objectID"]}.json', 'w'), indent=2)
        pages.append(page)

    if components:
        components_page = convert_components()
        pages.append(components_page)

    return pages


def convert_components():
    components_page = tree.convert_root_node({"name": "Symbols", "type": "PAGE"})
    components_page['layers'] = components
    json.dump(components_page, open(f'output/pages/{components_page["do_objectID"]}.json', 'w'),
              indent=2)

    return components_page


figma = json.load(open(sys.argv[1]))

try:
    shutil.rmtree('output')
except:
    pass

os.mkdir('output')
os.mkdir('output/pages')

sketch_pages = convert_pages(figma['document']['children'])

json.dump(Document.convert(sketch_pages), open('output/document.json', 'w'), indent=2)
json.dump(User.convert(sketch_pages), open('output/user.json', 'w'), indent=2)
json.dump(Meta.convert(sketch_pages), open('output/meta.json', 'w'), indent=2)

os.system('cd output; zip -r ../output/output.sketch .')
