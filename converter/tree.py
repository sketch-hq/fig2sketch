import converter.artboard as artboard
import converter.group as group
import converter.page as page
import converter.rectangle as rectangle
import utils

# import converter.vector as vector

# import regular_vector as regular_vector
# import text as text
# import instance as Instance

CONVERTERS = {
    'PAGE': page.convert,
    'RECTANGLE': rectangle.convert,
    'FRAME': artboard.convert,
    'GROUP': group.convert,
    # 'STAR': regular_vector.convert,
    # 'VECTOR': vector.convert,
    # 'ELLIPSE': vector.convert,
    # 'REGULAR_POLYGON': regular_vector.convert,
    # 'TEXT': text.convert,
    # 'COMPONENT': lambda a, b: instance.convert(a, b, components),
    # 'INSTANCE': lambda a, b: instance.convert(a, b, components),
}


def convert_root_node(figma_item):
    return convert_node(figma_item, {})


def convert_node(figma_item, parent_position):
    name = figma_item['name']
    type_ = figma_item['type']
    print(f'{type_}: {name}')

    sketch_item = CONVERTERS[type_](figma_item, parent_position)
    base_position = utils.get_base_position(figma_item)

    children = [convert_node(child, base_position) for child in
                figma_item.get('children', [])]
    sketch_item['layers'] = children

    return sketch_item
