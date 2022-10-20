import os
from sketchformat.serialize import serialize
from . import document, meta, tree, user
from .context import context


def convert_json_to_sketch(figma, id_map, output):
    figma_pages, components_page = separate_pages(figma['document']['children'])

    # We should either bring the fonts to the same indexed_components to pass
    # them as parameter or move the indexed components to the component file
    # and store there the components, for consistency purposes
    context.init(components_page, id_map)
    sketch_pages = convert_pages(figma_pages, output)


    sketch_document = document.convert(sketch_pages, output)
    sketch_user = user.convert(sketch_pages)
    sketch_meta = meta.convert(sketch_pages)

    write_sketch_file(sketch_document, sketch_user, sketch_meta, output)


def separate_pages(figma_pages):
    component_page = None
    pages = []

    for figma_page in figma_pages:
        if 'internalOnly' in figma_page and figma_page['internalOnly']:
            component_page = figma_page
        else:
            pages.append(figma_page)

    return pages, component_page


def convert_pages(figma_pages, output):
    pages = []

    for figma_page in figma_pages:
        page = tree.convert_node(figma_page, 'DOCUMENT')
        serialize(page, output.open(f"pages/{page.do_objectID}.json", 'w'))
        pages.append(page)

    if context.symbols_page:
        page = context.symbols_page
        serialize(page, output.open(f"pages/{page.do_objectID}.json", 'w'))
        pages.append(page)

    return pages


def write_sketch_file(sketch_document, sketch_user, sketch_meta, output):
    serialize(sketch_document, output.open('document.json', 'w'))
    serialize(sketch_user, output.open('user.json', 'w'))
    serialize(sketch_meta, output.open('meta.json', 'w'))
