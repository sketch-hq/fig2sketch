from converter import artboard, group, oval, page, rectangle, shape_path

CONVERTERS = {
    'CANVAS': page.convert,
    'ARTBOARD': artboard.convert,
    'GROUP': group.convert,
    'ROUNDED_RECTANGLE': rectangle.convert,
    'ELLIPSE': oval.convert,
    'VECTOR': shape_path.convert,
    # 'STAR': regular_vector.convert,
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
