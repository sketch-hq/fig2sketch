from . import base, rectangle, positioning
import utils
import numpy as np
from sketchformat.style import Style
from sketchformat.layer_group import Group
from sketchformat.layer_common import Rect, ClippingMaskMode
from sketchformat.layer_shape import Rectangle


def convert(fig_group):
    return Group(
        **base.base_styled(fig_group),
    )


def post_process_frame(fig_group, sketch_group):
    # Do nothing for fig groups, they translate directly to Sketch
    if fig_group['resizeToFit']:
        return sketch_group

    convert_frame_style(fig_group, sketch_group)
    convert_frame_to_group(fig_group, sketch_group)

    return sketch_group


def convert_frame_to_group(fig_group, sketch_group):
    needs_clip_mask = not fig_group.get('frameMaskDisabled', False)
    if needs_clip_mask:
        # Add a clipping rectangle matching the frame size. No need to recalculate bounds
        # since the clipmask defines Sketch bounds (which match visible children)
        sketch_group.layers.insert(0, make_clipping_rect(fig_group['guid'],
                                                            sketch_group.frame))
    else:
        # When converting from a frame to a group, the bounding box should be adjusted
        # The frame box in a fig doc can be smalled than the children bounds, but not so in Sketch
        # To do so, we resize the frame to match the children bbox and also move the children
        # so that the top-left corner sits at 0,0
        children_bbox = positioning.group_bbox(sketch_group.layers)
        vector = [children_bbox[0], children_bbox[2]]

        for child in sketch_group.layers:
            child.frame.x -= vector[0]
            child.frame.y -= vector[1]

        sketch_group.frame.x += vector[0]
        sketch_group.frame.y += vector[1]
        sketch_group.frame.width = children_bbox[1] - children_bbox[0]
        sketch_group.frame.height = children_bbox[3] - children_bbox[2]


def convert_frame_style(fig_group, sketch_group):
    # Convert frame styles
    # - Fill/stroke/bgblur -> Rectangle on bottom with that style
    # - Layer blur -> Rectangle with bgblur on top
    # - Shadows -> Keep in the group
    # TODO: This is one case where we could have both background blur and layer blur
    style = sketch_group.style
    has_fills = any([f.isEnabled for f in style.fills])
    has_borders = any([b.isEnabled for b in style.borders])
    has_bgblur = style.blur.isEnabled and style.blur.type == BlurType.BACKGROUND
    has_blur = style.blur.isEnabled and style.blur.type == BlurType.BACKGROUND

    if has_fills or has_borders or has_bgblur:
        bgrect = make_background_rect(fig_group['guid'], sketch_group.frame, 'Frame Background')
        bgrect.style.fills = style.fills
        bgrect.style.borders = style.borders
        if has_bgblur:
            bgrect.style.blur = style.blur

        sketch_group.layers.insert(0, bgrect)
    elif has_blur:
        blurrect = make_background_rect(fig_group['guid'], sketch_group.frame, 'Frame Blur')
        bgrect.style.blur = style.blur

        sketch_group.layers.insert(0, bgrect)

    style.fills = []
    style.borders = []
    style.blur.isEnabled = False


def make_background_rect(guid, frame, name):
     return Rectangle(
        do_objectID=utils.gen_object_id(guid, name.encode()),
        name=name,
        frame=Rect(
            height=frame.height,
            width=frame.width,
            x=0,
            y=0
        ),
        style=Style(do_objectID=utils.gen_object_id(guid, f'{name}_style'.encode())),
        resizingConstraint=10,
        rotation=0,
    )


def make_clipping_rect(guid, frame):
    obj = make_background_rect(guid, frame, "Clip")
    obj.hasClippingMask = True
    obj.clippingMaskMode = ClippingMaskMode.OUTLINE
    return obj
