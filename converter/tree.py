from converter import artboard, group, oval, page, rectangle, shape_path, polygon, star, \
    shape_group, text, slice, instance, symbol
from dataclasses import is_dataclass
import logging
from sketchformat.layer_common import AbstractLayer
from sketchformat.layer_group import AbstractLayerGroup
from typing import Dict, Callable, Any


CONVERTERS: Dict[str,Callable[[dict], AbstractLayer]] = {
    'CANVAS': page.convert,
    'ARTBOARD': artboard.convert,
    'GROUP': group.convert,
    'ROUNDED_RECTANGLE': rectangle.convert,
    'RECTANGLE': rectangle.convert,
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

POST_PROCESSING: Dict[str,Callable[[dict, Any], AbstractLayer]] = {
    'BOOLEAN_OPERATION': shape_group.post_process,
    'SYMBOL': symbol.move_to_symbols_page,
    'GROUP': group.post_process_frame,
    'ARTBOARD': artboard.post_process_frame,
    'INSTANCE': instance.post_process,
    'CANVAS': page.add_page_background
}


def convert_node(fig_node: dict, parent_type: str) -> AbstractLayer:
    name = fig_node['name']
    type_ = get_node_type(fig_node, parent_type)
    logging.info(f'{type_}: {name}')

    sketch_item = CONVERTERS[type_](fig_node)
    children = [convert_node(child, fig_node['type']) for child in
                fig_node.get('children', [])]

    # TODO: Determine who needs layers per node type
    # e.g: rectangles never have children, groups do
    if children and isinstance(sketch_item, AbstractLayerGroup):
        sketch_item.layers = children

    post_process = POST_PROCESSING.get(type_)
    if post_process:
        sketch_item = post_process(fig_node, sketch_item)

    return sketch_item


def get_node_type(fig_node: dict, parent_type: str) -> str:
    # We do this because Sketch does not support nested artboards
    # If a Frame is detected inside another Frame, the internal one
    # is considered a group
    if fig_node['type'] == 'FRAME':
        if parent_type == 'CANVAS' and not fig_node['resizeToFit']:
            return 'ARTBOARD'
        else:
            return 'GROUP'
    else:
        return fig_node['type']
