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

# import converter.vector as Vector

# import regular_vector as RegularVector
# import text as Text
# import instance as Instance


components = []

CONVERTERS = {
    'PAGE': Page.convert,
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


def convert_something(figma_item, parent_position):
    name = figma_item['name']
    type_ = figma_item['type']
    print(f'{type_}: {name}')

    sketch_item = CONVERTERS[type_](figma_item, parent_position)
    base_position = utils.get_base_position(figma_item)

    children = [convert_something(child, base_position) for child in
                figma_item.get('children', [])]
    sketch_item['layers'] = children

    return sketch_item


def convert_pages(figma_pages):
    pages = []

    for figma_page in figma_pages:
        page = convert_something(figma_page, {})
        json.dump(page, open(f'output/pages/{page["do_objectID"]}.json', 'w'), indent=2)
        pages.append(page)

    if components:
        components_page = convert_components()
        pages.append(components_page)

    return pages


def convert_components():
    components_page = convert_something({"name": "Symbols", "type": "PAGE"}, {})
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
