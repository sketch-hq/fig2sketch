from operator import is_
from converter import utils
from . import base, positioning, rectangle
from sketchformat.layer_group import (
    Group,
    Rect,
    AbstractStyledLayer,
    AbstractLayerGroup,
)
from sketchformat.style import *


def convert(fig_group):
    return Group(
        **base.base_styled(fig_group),
    )


def post_process_frame(fig_group: dict, sketch_group: Group) -> Group:
    convert_frame_style(fig_group, sketch_group)
    adjust_group_resizing_constraint(fig_group, sketch_group)

    return sketch_group


def adjust_group_resizing_constraint(fig_group: dict, sketch_group: Group) -> None:
    """Adjust the resizing constraint of the group to better match the .fig doc.
    Groups in .fig don't really have a resizing constraint. Instead, the children of the group resize
    relative to the parent of the group.
    If all childs have the same constraint, we can have the same behaviour in Sketch, by setting the group
    constraints to be equal to the sublayers.
    However, if there is a mix, we cannot replicate the behaviour, so we just choose some constraint and throw
    a warning"""
    if not sketch_group.layers:
        return

    first_layer_constraint = [
        sketch_group.layers[0].horizontalPins,
        sketch_group.layers[0].verticalPins,
    ]

    constraints_are_inconsistent = False
    for layer in sketch_group.layers[1:]:
        current_constraint = [layer.horizontalPins, layer.verticalPins]
        if current_constraint != first_layer_constraint:
            constraints_are_inconsistent = True
            break

    if constraints_are_inconsistent:
        utils.log_conversion_warning("GRP002", fig_group)

    sketch_group.horizontalPins = sketch_group.layers[0].horizontalPins
    sketch_group.verticalPins = sketch_group.layers[0].verticalPins


def convert_frame_style(fig_group: dict, sketch_group: AbstractLayerGroup) -> AbstractLayerGroup:
    # Convert frame styles
    # - Fill/stroke/bgblur -> Rectangle on bottom with that style
    # - Layer blur -> Rectangle with bgblur on top
    # - Shadows -> Keep in the group
    # TODO: This is one case where we could have both background blur and layer blur
    style = sketch_group.style

    # Fill and borders go on a rectangle on the bottom
    has_fills = any([f.isEnabled for f in style.fills])
    has_borders = any([b.isEnabled for b in style.borders])
    has_inner_shadows = any([b.isEnabled and b.isInnerShadow for b in style.shadows])
    has_bgblur = (
        len(style.blurs)
        and style.blurs[0].isEnabled
        and style.blurs[0].type == BlurType.BACKGROUND
    )
    has_blur = (
        len(style.blurs) and style.blurs[0].isEnabled and style.blurs[0].type == BlurType.GAUSSIAN
    )

    if has_fills or has_borders or has_bgblur:
        bgrect = rectangle.make_background_rect(fig_group, sketch_group.frame, "Frame Background")
        bgrect.style.fills = style.fills
        bgrect.style.borders = style.borders
        if has_bgblur:
            bgrect.style.blurs.append(Blur(type=BlurType.BACKGROUND, radius=style.blurs[0].radius))
        bgrect.style.shadows = style.shadows

        sketch_group.layers.insert(0, bgrect)

        style.fills = []
        style.borders = []
        style.blurs = []
        style.shadows = [s for s in style.shadows if not s.isInnerShadow]

    # Blur goes in a rectangle with bgblur at the top
    if has_blur:
        blur = rectangle.make_background_rect(
            fig_group, sketch_group.frame, f"{sketch_group.name} blur"
        )
        blur.style.blurs.append(Blur(type=BlurType.BACKGROUND, radius=style.blurs[0].radius))

        # Foreground blur, add as a layer at the top of the group
        sketch_group.layers.append(blur)
        style.blurs = []

    # Inner shadows apply to each child (if they were not put in the background rect earlier)
    # Normal shadows are untouched
    for shadow in style.shadows:
        if shadow.isInnerShadow:
            utils.log_conversion_warning("GRP001", fig_group)
            apply_inner_shadow(sketch_group, shadow)

    style.shadows = [s for s in style.shadows if not s.isInnerShadow]

    return sketch_group


def apply_inner_shadow(layer: AbstractLayerGroup, shadow: Shadow) -> None:
    for child in layer.layers:
        if isinstance(child, AbstractLayerGroup):
            apply_inner_shadow(child, shadow)
        elif isinstance(child, AbstractStyledLayer):
            child.style.shadows.append(shadow)
