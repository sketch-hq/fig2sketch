import math
from . import base, group, prototype, rectangle, layout, symbol
from .config import config
from converter import utils
from sketchformat.layer_group import (
    ClippingBehavior,
    Group,
    GroupBehavior,
    FlexGroupLayout,
    FlexDirection,
    FlexJustify,
    FlexAlign,
    FreeFormGroupLayout,
    SimpleGrid,
    LayoutGrid,
    Rect,
)
from typing import Optional
from collections import namedtuple

# The stroke a variant set carries in the fig file unless the user styles it: solid
# #9747FF at full opacity, one unit wide and inside the bounds. Taken from a .fig
# export.
DEFAULT_VARIANT_SET_STROKE_COLOR = {
    "r": 0.5921568870544434,
    "g": 0.27843138575553894,
    "b": 1.0,
    "a": 1.0,
}
DEFAULT_VARIANT_SET_STROKE_WEIGHT = 1.0


def convert(fig_frame: dict) -> Group:
    obj = Group(
        **base.base_styled(fig_frame),
        **layout.layout_information(fig_frame),
        **prototype.prototyping_information(fig_frame),
        **base.container_information(fig_frame),
        grid=convert_grid(fig_frame),
        groupBehavior=GroupBehavior.FRAME,
    )

    obj.layout = convert_layout(fig_frame, obj.frame)

    return obj


def post_process_frame(fig_frame: dict, sketch_frame: Group) -> Group:
    # The .fig file clips overlays implicitly but .sketch doesn't, so we must add a mask
    if sketch_frame.overlaySettings is not None:
        sketch_frame.layers.insert(0, rectangle.make_clipping_rect(fig_frame, sketch_frame.frame))

    if utils.has_auto_layout(fig_frame):
        sketch_frame = layout.post_process_group_layout(sketch_frame)

    if config.import_variants and fig_frame.get("isStateGroup", False):
        sketch_frame.groupBehavior = GroupBehavior.VARIANT_SET
        sketch_frame.variantProperties = symbol.build_variant_properties(fig_frame)

        if has_default_variant_set_styling(fig_frame):
            # Sketch's overlay draws this appearance for an unstyled variant set, so
            # dropping it is visually neutral and leaves the layer clean. Styling the
            # user chose themselves is left alone.
            sketch_frame.style.borders = []

    return sketch_frame


def has_default_variant_set_styling(fig_frame: dict) -> bool:
    """Whether a variant set carries only the styling it has by default.

    The fig file holds that default as a real stroke rather than leaving it out, so it
    has to be recognized rather than assumed absent. Anything else, including keeping
    the default color but widening the stroke, is styling the user applied, which we
    keep.
    """
    if fig_frame.get("fillPaints"):
        return False

    strokes = fig_frame.get("strokePaints", [])
    if len(strokes) != 1:
        return False

    stroke = strokes[0]
    if stroke.get("type") != "SOLID" or not stroke.get("visible", True):
        return False

    if not _is_close(stroke.get("opacity", 1.0), 1.0):
        return False

    if not _is_close(fig_frame.get("strokeWeight", 0), DEFAULT_VARIANT_SET_STROKE_WEIGHT):
        return False

    color = stroke.get("color", {})
    return all(
        _is_close(color.get(channel), value)
        for channel, value in DEFAULT_VARIANT_SET_STROKE_COLOR.items()
    )


def _is_close(value: Optional[float], expected: float) -> bool:
    """Compares against values read out of a .fig, so exact equality is too brittle."""
    if value is None:
        return False

    return math.isclose(value, expected, abs_tol=1e-6)


def convert_grid(fig_frame: dict) -> Optional[SimpleGrid]:
    grids = sorted(
        [g for g in fig_frame.get("layoutGrids", []) if g["pattern"] == "GRID"],
        key=lambda x: x["sectionSize"],
    )
    if not grids:
        return None

    primary = grids[0]["sectionSize"]
    secondary = None
    for g in grids[1:]:
        size = g["sectionSize"]
        if size % primary == 0:
            if secondary:
                utils.log_conversion_warning("GRD003", fig_frame)
            else:
                secondary = size
        else:
            utils.log_conversion_warning("GRD002", fig_frame)

    return SimpleGrid(
        gridSize=primary,
        thickGridTimes=secondary / primary if secondary else 0,
        isEnabled=True,
    )


def convert_layout(fig_frame: dict, frame: Rect) -> Optional[LayoutGrid]:
    layouts = [g for g in fig_frame.get("layoutGrids", []) if g["pattern"] == "STRIPES"]

    if not layouts:
        return None

    columns = [l for l in layouts if l["axis"] == "X"]
    if len(columns) > 1:
        utils.log_conversion_warning("GRD004", fig_frame)

    col_config = {}
    if columns:
        sizes = calculate_layout(columns[0], frame.width)

        col_config = {
            "columnWidth": sizes.item_size,
            "gutterWidth": columns[0]["gutterSize"],
            "numberOfColumns": sizes.item_count,
            "totalWidth": sizes.size,
            "drawVertical": True,
            "horizontalOffset": sizes.offset,
        }

    rows = [l for l in layouts if l["axis"] == "Y"]
    if len(rows) > 1:
        utils.log_conversion_warning("GRD004", fig_frame)

    row_config = {}
    if rows:
        gutter_size = rows[0]["gutterSize"]
        sizes = calculate_layout(rows[0], frame.height)

        if sizes.size != frame.height:
            utils.log_conversion_warning("GRD005", fig_frame)

        if sizes.offset != 0:
            utils.log_conversion_warning("GRD006", fig_frame)

        if gutter_size <= 0:
            utils.log_conversion_warning("GRD007", fig_frame)
            gutter_size = 1

        row_scale = sizes.item_size / gutter_size
        int_row_scale = round(row_scale)
        if abs(row_scale - int_row_scale) > 0.01:
            utils.log_conversion_warning("GRD007", fig_frame)
        else:
            row_config = {
                "drawHorizontal": True,
                "gutterHeight": gutter_size,
                "rowHeightMultiplication": int_row_scale,
            }

            if col_config:
                utils.log_conversion_warning("GRD007", fig_frame)
            else:
                row_config["totalWidth"] = frame.width

    if not col_config and not row_config:
        return None

    return LayoutGrid(**col_config, **row_config)


LayoutSizes = namedtuple("LayoutSizes", ["size", "offset", "item_count", "item_size"])


def calculate_layout(layout: dict, size: float) -> LayoutSizes:
    item_num = layout["numSections"]
    gutter_width = layout["gutterSize"]
    item_width = layout["sectionSize"]
    offset = layout["offset"]

    if layout["type"] == "STRETCH":
        if item_num == 2147483647:
            item_num = 1
        total_gutter = (item_num - 1) * gutter_width
        item_width = (size - total_gutter - 2 * offset) / item_num
        if item_width < 0:
            item_width = 0
        layout_size = size
    else:
        if item_num == 2147483647:
            item_num = math.ceil(size / item_width)

        layout_size = item_width * item_num + gutter_width * (item_num - 1)
        if layout["type"] == "MAX":
            offset = size - layout_size
        elif layout["type"] == "CENTER":
            offset = (size - layout_size) / 2

    return LayoutSizes(layout_size, offset, item_num, item_width)
