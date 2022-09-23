import converter.artboard as artboard
import converter.group as group
import converter.oval as oval
import converter.page as page
import converter.rectangle as rectangle

# import converter.vector as vector

# import regular_vector as regular_vector
# import text as text
# import instance as instance

CONVERTERS = {
    'CANVAS': page.convert,
    'ARTBOARD': artboard.convert,
    'GROUP': group.convert,
    'ROUNDED_RECTANGLE': rectangle.convert,
    'ELLIPSE': oval.convert,
    # 'STAR': regular_vector.convert,
    # 'VECTOR': vector.convert,
    # 'REGULAR_POLYGON': regular_vector.convert,
    # 'TEXT': text.convert,
    # 'COMPONENT': lambda a, b: instance.convert(a, b, components),
    # 'INSTANCE': lambda a, b: instance.convert(a, b, components),
}


def convert_node(figma_item):
    name = figma_item['name']
    type_ = get_node_type(figma_item)
    print(f'{type_}: {name}')

    sketch_item = CONVERTERS[type_](figma_item)

    children = [convert_node(child) for child in figma_item.get('children', [])]
    sketch_item['layers'] = children

    return sketch_item


def get_node_type(figma_item):
    match figma_item['type']:
        case 'FRAME':
            if figma_item['resizeToFit']:
                node_type = 'GROUP'
            else:
                node_type = 'ARTBOARD'
        case type_:
            node_type = type_

    return node_type