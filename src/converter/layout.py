import math
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
    FlexStackingOrder,
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

    # Convert Wrap properties
    wrap_mode = fig_frame.get("stackWrap")
    wrapping_enabled = wrap_mode == "WRAP"
    align_content = convert_flex_justify(counter_align) if wrapping_enabled else FlexJustify.START
    cross_axis_gutter_gap = fig_frame.get("stackCounterSpacing", 0)
    # stackCounterSpacing can be NaN when the value is not set; Sketch expects 0.
    if math.isnan(cross_axis_gutter_gap):
        cross_axis_gutter_gap = 0

    # Advanced stack settings
    borders_affect_layout = fig_frame.get("bordersTakeSpace", False)
    # Interpreting stack item order, and stackReverseZIndex is a bit confusing.
    # Figma reverse the LL order for stack items, but the model stays the same.
    # If this was all they did the canvas would look out of sync with the UI,
    # but they also set a z-index ordering mode labelled as "last on top". So
    # the item at the bottom of the LL (top of the model) is rendered on top.
    # When stackReverseZIndex is true (which corresponds to the mode labelled
    # "first on top") this means to use the reverse of the model order (the top
    # item in the LL since, remember, it has been reversed). What this means for
    # us is that once we've reversed the layer order in our post-processing (so
    # that what the user saw in the Figma LL matches what they'll see in Sketch)
    # we interpret a false or absent stackReverseZIndex as  "backwards", and
    # true as "forwards".
    stacking_order = (
        FlexStackingOrder.FORWARDS
        if fig_frame.get("stackReverseZIndex")
        else FlexStackingOrder.BACKWARDS
    )

    return FlexGroupLayout(
        flexDirection=flex_direction,
        justifyContent=justify,
        alignItems=align,
        allGuttersGap=all_gutters_gap,
        crossAxisGutterGap=cross_axis_gutter_gap,
        wrappingEnabled=wrapping_enabled,
        alignContent=align_content,
        bordersAffectLayout=borders_affect_layout,
        stackingOrder=stacking_order,
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


def post_process_group_layout(layer_group: Frame) -> Frame:
    # Figma displays stack items in reverse order compared to its other
    # containers in the LL. We want to take the LL order here so what the user
    # will see in Sketch will match what they saw in Figma. The other half of
    # handling this is our interpretation of stackReverseZIndex (see
    # convert_group_layout).
    layer_group.layers.reverse()
    return layer_group
