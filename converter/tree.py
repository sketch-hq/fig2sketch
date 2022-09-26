from converter import artboard, group, oval, page, rectangle, shape_path, polygon, star, shape_group

CONVERTERS = {
    'CANVAS': page.convert,
    'ARTBOARD': artboard.convert,
    'GROUP': group.convert,
    'ROUNDED_RECTANGLE': rectangle.convert,
    'ELLIPSE': oval.convert,
    'VECTOR': shape_path.convert,
    'STAR': star.convert,
    'REGULAR_POLYGON': polygon.convert,
    'TEXT': rectangle.convert,
    'BOOLEAN_OPERATION': shape_group.convert,
    # 'COMPONENT': lambda a, b: instance.convert(a, b, components),
    # 'INSTANCE': lambda a, b: instance.convert(a, b, components),
}

POST_PROCESSING = {
    'BOOLEAN_OPERATION': shape_group.post_process,
}

def convert_node(figma_item):
    name = figma_item['name']
    type_ = get_node_type(figma_item)
    print(f'{type_}: {name}')

    sketch_item = CONVERTERS[type_](figma_item)

    children = [convert_node(child) for child in figma_item.get('children', [])]
    sketch_item['layers'] = children

    post_process = POST_PROCESSING.get(type_)
    if post_process:
        post_process(figma_item, sketch_item)

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
