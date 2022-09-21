import json
import shutil
import os
import sys

import converter.artboard as Artboard
import converter.document as Document
import converter.group as Group
import converter.meta as Meta
import converter.page as Page
import converter.rectangle as Rectangle
import converter.user as User
import utils

# import vector as Vector
# import regular_vector as RegularVector
# import text as Text
# import instance as Instance


components = []

CONVERTERS = {
    'RECTANGLE': Rectangle.convert,
    'FRAME': Artboard.convert,
    'GROUP': Group.convert,
    # 'STAR': RegularVector.convert,
    # 'VECTOR': Vector.convert,
    # 'ELLIPSE': Vector.convert,
    # 'REGULAR_POLYGON': RegularVector.convert,
    # 'TEXT': Text.convert,
    # 'COMPONENT': lambda a, b: Instance.convert(a, b, components),
    # 'INSTANCE': lambda a, b: Instance.convert(a, b, components),
}


def convert_something(item, parent):
    name = item['name']
    type_ = item['type']
    print(f'{type_}: {name}')

    # blank fill-geometry = pain
    children = [convert_something(x, item) for x in item.get('children', []) if
                x['name'] not in ['Vector 3', 'Vector 4']]

    return CONVERTERS[type_](item, children, parent)


def convert_page(figma_page):
    converted_page = Page.convert(figma_page)

    children = []
    for child in figma_page['children']:
        children.append(convert_something(child, figma_page))

    converted_page['layers'] = children

    return converted_page


figma = json.load(open(sys.argv[1]))

try:
    shutil.rmtree('output')
except:
    pass

os.mkdir('output')
os.mkdir('output/pages')

pages = []
for figma_page in figma['document']['children']:
    page = convert_page(figma_page)
    json.dump(page, open(f'output/pages/{page["do_objectID"]}.json', 'w'), indent=2)
    pages.append(page)

if components:
    page = Page.convert({"name": "Symbols"}, components)
    json.dump(page, open(f'output/pages/{page["do_objectID"]}.json', 'w'), indent=2)
    pages.append(page)

json.dump(Document.convert(pages), open('output/document.json', 'w'), indent=2)
json.dump(User.convert(pages), open('output/user.json', 'w'), indent=2)
json.dump(Meta.convert(pages), open('output/meta.json', 'w'), indent=2)

os.system('cd output; zip -r ../output/output.sketch .')
