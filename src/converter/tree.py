from converter import (
    frame,
    group,
    page,
    rectangle,
    shape,
    shape_path,
    shape_group,
    text,
    slice,
    instance,
    symbol,
)
import logging
from sketchformat.layer_common import AbstractLayer
from sketchformat.layer_group import AbstractLayerGroup
from typing import Dict, Callable, Any
import traceback
from .errors import *
from . import utils


def ignored_layer_type(fig_layer: dict) -> AbstractLayer:
    raise Fig2SketchWarning("LAY001")


CONVERTERS: Dict[str, Callable[[dict], AbstractLayer]] = {
    "CANVAS": page.convert,
    "FRAME": frame.convert,
    "GROUP": group.convert,
    "ROUNDED_RECTANGLE": rectangle.convert,
    "RECTANGLE": rectangle.convert,
    "ELLIPSE": shape.convert_oval,
    "VECTOR": shape_path.convert,
    "STAR": shape.convert_star,
    "REGULAR_POLYGON": shape.convert_polygon,
    "TEXT": text.convert,
    "BOOLEAN_OPERATION": shape_group.convert,
    "LINE": shape_path.convert_line,
    "SLICE": slice.convert,
    "SYMBOL": symbol.convert,
    "INSTANCE": instance.convert,
    "STICKY": ignored_layer_type,
}

POST_PROCESSING: Dict[str, Callable[[dict, Any], AbstractLayer]] = {
    "CANVAS": page.add_page_background,
    "FRAME": frame.post_process_frame,
    "GROUP": group.post_process_frame,
    "BOOLEAN_OPERATION": shape_group.post_process,
    "SYMBOL": symbol.move_to_symbols_page,
    "INSTANCE": instance.post_process,
}


def convert_node(fig_node: dict, parent_type: str) -> AbstractLayer:
    name = fig_node["name"]
    type_ = get_node_type(fig_node, parent_type)
    logging.debug(f"{type_}: {name} {fig_node['guid']}")

    try:
        sketch_item = CONVERTERS[type_](fig_node)
    except Fig2SketchNodeChanged:
        # The fig_node was modified, retry converting with the new values
        # This happens on instance detaching
        return convert_node(fig_node, parent_type)

    if fig_node.get("layoutGrids", []) and type_ != "FRAME":
        utils.log_conversion_warning("GRD001", fig_node)

    children = []
    for child in fig_node.get("children", []):
        try:
            children.append(convert_node(child, fig_node["type"]))
        except Fig2SketchWarning as w:
            utils.log_conversion_warning(w.code, child)
        except Exception as e:
            logging.error(
                f'An unexpected error occurred when converting {child["type"]}: {child["name"]} ({child["guid"]}). It will be skipped\n'
                + "".join(traceback.format_exception(e))
            )

    if children and isinstance(sketch_item, AbstractLayerGroup):
        sketch_item.layers = children

    post_process = POST_PROCESSING.get(type_)
    if post_process:
        sketch_item = post_process(fig_node, sketch_item)

    return sketch_item


def get_node_type(fig_node: dict, parent_type: str) -> str:
    if fig_node["type"] in ["FRAME", "SECTION"]:
        if not fig_node.get("resizeToFit", False) or utils.has_auto_layout(fig_node):
            return "FRAME"
        else:
            return "GROUP"
    else:
        return fig_node["type"]
