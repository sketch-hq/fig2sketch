from converter import artboard, group, oval, page, rectangle, shape_path, polygon, star, \
    shape_group, text, slice, context, instance, symbol

CONVERTERS = {
    'CANVAS': page.convert,
    'ARTBOARD': artboard.convert,
    'GROUP': group.convert,
    'ROUNDED_RECTANGLE': rectangle.convert,
    'ELLIPSE': oval.convert,
    'VECTOR': shape_path.convert,
    'STAR': star.convert,
    'REGULAR_POLYGON': polygon.convert,
    'TEXT': text.convert,
    'BOOLEAN_OPERATION': shape_group.convert,
    'LINE': shape_path.convert_line,
    'SLICE': slice.convert,
    'SYMBOL': symbol.convert,
    'INSTANCE': instance.convert,
}

POST_PROCESSING = {
    'BOOLEAN_OPERATION': shape_group.post_process,
    'SYMBOL': symbol.move_to_symbols_page,
    'GROUP': group.post_process_frame,
}


def convert_node(figma_node, parent_type):
    name = figma_node['name']
    type_ = get_node_type(figma_node, parent_type)
    print(f'{type_}: {name}')

    sketch_item = CONVERTERS[type_](figma_node)

    # TODO: Symbol dettaching hack
    if 'layers' not in sketch_item:
        children = [convert_node(child, figma_node['type']) for child in
                    figma_node.get('children', [])]
        sketch_item['layers'] = children

    post_process = POST_PROCESSING.get(type_)
    if post_process:
        sketch_item = post_process(figma_node, sketch_item)

    return sketch_item


def get_node_type(figma_node, parent_type):
    if figma_node['type'] == 'FRAME':
        return 'ARTBOARD' if parent_type == 'CANVAS' else 'GROUP'
    else:
        return figma_node['type']


def find_shared_style(figma_node):
    match figma_node:
        case {'inheritFillStyleID': shared_style}:
            node_id = (shared_style['sessionID'], shared_style['localID'])
            return context.component(node_id)
        case _:
            return {}
