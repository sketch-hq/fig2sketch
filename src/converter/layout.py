from typing import TypedDict, Union
from converter import utils
from sketchformat.layer_common import PaddingSelection
from sketchformat.layer_group import (
    ClippingBehavior,
    Frame,
    FlexGroupLayout,
    FreeFormGroupLayout,
    InferredGroupLayout,
    FlexDirection,
    FlexJustify,
    FlexAlign,
)


class _LayoutInformation(TypedDict, total=False):
    groupLayout: Union[FreeFormGroupLayout, InferredGroupLayout, FlexGroupLayout]
    clippingBehavior: ClippingBehavior
    leftPadding: float
    topPadding: float
    rightPadding: float
    bottomPadding: float
    paddingSelection: PaddingSelection


def layout_information(fig_frame: dict) -> _LayoutInformation:
    layout = _LayoutInformation()

    layout["clippingBehavior"] = (
        ClippingBehavior.NONE if fig_frame.get("frameMaskDisabled") else ClippingBehavior.DEFAULT
    )

    if not utils.has_auto_layout(fig_frame):
        return layout

    layout["groupLayout"] = convert_group_layout(fig_frame)

    # Set padding values from Figma frame
    layout["topPadding"] = fig_frame.get("stackVerticalPadding", 0)
    layout["rightPadding"] = fig_frame.get("stackPaddingRight", 0)
    layout["bottomPadding"] = fig_frame.get("stackPaddingBottom", 0)
    layout["leftPadding"] = fig_frame.get("stackHorizontalPadding", 0)

    # Determine padding selection type based on symmetry
    has_asymmetric_padding = (
        layout["topPadding"] != layout["bottomPadding"]
        or layout["leftPadding"] != layout["rightPadding"]
    )

    layout["paddingSelection"] = (
        PaddingSelection.INDIVIDUAL if has_asymmetric_padding else PaddingSelection.PAIRED
    )

    return layout


def convert_group_layout(fig_frame: dict) -> FlexGroupLayout:
    # Determine stack direction
    is_vertical = fig_frame["stackMode"] == "VERTICAL"
    flex_direction = FlexDirection.VERTICAL if is_vertical else FlexDirection.HORIZONTAL

    # Get spacing between items
    all_gutters_gap = fig_frame.get("stackSpacing", 0)

    # Convert alignment properties
    primary_align = fig_frame.get("stackPrimaryAlignItems", "MIN")
    counter_align = fig_frame.get("stackCounterAlignItems", "MIN")

    justify = convert_flex_justify(primary_align)
    align = convert_flex_align(counter_align)

    return FlexGroupLayout(
        flexDirection=flex_direction,
        justifyContent=justify,
        alignItems=align,
        allGuttersGap=all_gutters_gap,
    )


def convert_flex_justify(justify: str) -> FlexJustify:
    justify_mapping = {
        "MIN": FlexJustify.START,
        "CENTER": FlexJustify.CENTER,
        "MAX": FlexJustify.END,
        # We seem to have a different interpretation of "SPACE_EVENLY"
        "SPACE_EVENLY": FlexJustify.SPACE_BETWEEN,
    }

    return justify_mapping.get(justify, FlexJustify.START)


def convert_flex_align(alignment: str) -> FlexAlign:
    align_mapping = {
        "MIN": FlexAlign.START,
        "CENTER": FlexAlign.CENTER,
        "MAX": FlexAlign.END,
    }

    return align_mapping.get(alignment, FlexAlign.NONE)


def post_process_group_layout(fig_node: dict, layer_group: Frame) -> Frame:
    # If the layout has a child which is ignoring the Stack layout, and the stack
    # has a "Last on top" z-index order, we'll remove the stack layout.
    has_child_ignoring_layout = False

    for layer in layer_group.layers:
        if (
            hasattr(layer, "flexItem")
            and layer.flexItem
            and getattr(layer.flexItem, "ignoreLayout", False)
        ):
            has_child_ignoring_layout = True
            break

    if has_child_ignoring_layout and not fig_node.get("stackReverseZIndex"):
        layer_group.groupLayout = FreeFormGroupLayout()
        utils.log_conversion_warning("STK001", fig_node)
    else:
        layer_group.layers.reverse()

    return layer_group
