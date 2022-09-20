import json
import shutil
import os
import sys

import artboard as Artboard
import document as Document
import group as Group
import meta as Meta
import page as Page
import rectangle as Rectangle
import user as User

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


def convert_page(page):
    children = []
    for child in page['children']:
        # if child['name'] not in ['Frame 1', 'Frame 2', 'Frame 3']: continue
        # if child['name'] not in ['Text']: continue
        children.append(convert_something(child, page))

    return Page.convert(page, children)


figma = json.load(open(sys.argv[1]))

try:
    shutil.rmtree('output')
except:
    pass

os.mkdir('output')
os.mkdir('output/pages')

pages = []
for page in figma['document']['children']:
    # if page['name'] != 'Component text': continue
    page = convert_page(page)
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
