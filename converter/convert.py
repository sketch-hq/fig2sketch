import json
import os
import shutil
import sys

from . import document, meta, tree, user

components = []


def convert_pages(figma_pages):
    pages = []

    for figma_page in figma_pages:
        page = tree.convert_node(figma_page)
        json.dump(page, open(f"output/pages/{page['do_objectID']}.json", 'w'), indent=2)
        pages.append(page)

    if components:
        components_page = convert_components()
        pages.append(components_page)

    return pages


def convert_components():
    components_page = tree.convert_node({'name': 'Symbols', 'type': 'PAGE'})
    components_page['layers'] = components
    json.dump(components_page, open(f"output/pages/{components_page['do_objectID']}.json", 'w'),
              indent=2)

    return components_page


def convert_json_to_sketch(figma):
    clean_output()

    sketch_pages = convert_pages(figma['document']['children'])

    sketch_document = document.convert(sketch_pages)
    sketch_user = user.convert(sketch_pages)
    sketch_meta = meta.convert(sketch_pages)

    write_sketch_file(sketch_document, sketch_user, sketch_meta)


def clean_output():
    try:
        shutil.rmtree('output')
    except:
        pass

    os.mkdir('output')
    os.mkdir('output/pages')


def write_sketch_file(sketch_document, sketch_user, sketch_meta):
    json.dump(sketch_document, open('output/document.json', 'w'), indent=2)
    json.dump(sketch_user, open('output/user.json', 'w'), indent=2)
    json.dump(sketch_meta, open('output/meta.json', 'w'), indent=2)

    os.system('cd output; zip -r ../output/output.sketch .')


if __name__ == '__main__':
    convert_json_to_sketch(json.load(open(sys.argv[1])))
