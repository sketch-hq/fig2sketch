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
    section,
    symbol,
)
import logging
from sketchformat.layer_common import AbstractLayer
from sketchformat.layer_group import AbstractLayerGroup
from typing import Dict, Callable, Any
import traceback
from .errors import *
from . import utils
from .config import config
from .context import context


def ignored_layer_type(fig_layer: dict) -> AbstractLayer:
    raise Fig2SketchWarning("LAY001")


# Group-like types that can take on the section behavior if they have to contain one
PROMOTABLE_TO_SECTION = ("FRAME", "GROUP")

# A page may hold a section as it is, so it ends the chain without being promoted. The
# other legal container, a section, ends it by already being one
SECTION_CONTAINERS = ("CANVAS",)


def will_be_section(fig_node: dict) -> bool:
    if fig_node["type"] == "SECTION":
        return True

    # A variant set is a section in Sketch, so it is bound by the same nesting rule
    return bool(config.import_variants and fig_node.get("isStateGroup", False))


def mark_promoted_sections(fig_node: dict) -> bool:
    """Finds sections nested in frames and promotes the frames above them.

    Sketch only allows a section on a page or inside another section, while the fig
    format lets a variant set sit inside a frame. Rather than dropping the section
    behavior, the frames above it become sections too, which keeps the variant set
    intact.

    Run this over a page before converting it: conversion visits a parent before its
    children, so the frames have already been built by the time their descendants
    would reveal that they need to be sections.

    Returns whether the node is, or was promoted to, a section. Walking bottom-up like
    this promotes the whole chain up to the nearest container that may already hold a
    section, so a page or an enclosing section stops it rather than being warned about.
    """
    if will_be_section(fig_node):
        # The chain ends here, since a section may sit in a section. Its descendants
        # are still searched on their own: a frame below it may hold a variant set,
        # which is no more legal for being inside a section further up
        for child in fig_node.get("children", []):
            mark_promoted_sections(child)

        return True

    # Every branch has to be walked, so collect the results rather than short-circuit
    contains_section = [mark_promoted_sections(child) for child in fig_node.get("children", [])]
    if not any(contains_section) or fig_node["type"] in SECTION_CONTAINERS:
        return False

    if fig_node["type"] not in PROMOTABLE_TO_SECTION:
        # A symbol master cannot become a section, and Sketch does not allow a section
        # inside one, so warn rather than emit a shape we cannot fix
        utils.log_conversion_warning("SEC002", fig_node)
        return False

    context.promote_to_section(fig_node["guid"])
    utils.log_conversion_warning("SEC001", fig_node)

    return True


CONVERTERS: Dict[str, Callable[[dict], AbstractLayer]] = {
    "CANVAS": page.convert,
    "FRAME": frame.convert,
    "SECTION": section.convert,
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
    "SECTION": section.post_process,
    "GROUP": group.post_process_frame,
    "BOOLEAN_OPERATION": shape_group.post_process,
    "SYMBOL": symbol.post_process_symbol,
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
    if context.is_promoted_to_section(fig_node["guid"]):
        # Promoted by mark_promoted_sections so it can hold a section or variant set
        return "SECTION"

    if fig_node["type"] == "SECTION":
        # A section stays a section whatever its resize behavior, since in Sketch it
        # is a container kind rather than a way of sizing one
        return "SECTION"

    if fig_node["type"] == "FRAME":
        if not fig_node.get("resizeToFit", False) or utils.has_auto_layout(fig_node):
            return "FRAME"
        else:
            return "GROUP"

    return fig_node["type"]
