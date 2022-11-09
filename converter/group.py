from . import base, rectangle, positioning
import utils
import numpy as np
from sketchformat.style import Style
from sketchformat.layer_group import Group
from sketchformat.layer_common import Rect, ClippingMaskMode
from sketchformat.layer_shape import Rectangle


def convert(figma_group):
    return Group(
        **base.base_shape(figma_group),
    )


def post_process_frame(figma_group, sketch_group):
    # Do nothing for Figma groups, they translate directly to Sketch
    if figma_group['resizeToFit']:
        return sketch_group

    # Convert frame styles
    # - Fill/stroke/bgblur -> Rectangle on bottom with that style
    # - Layer blur -> Rectangle with bgblur on top
    # - Shadows -> If we have fill, add shadow to the fill. If not, add shadow to each child
    # TODO: Fix this and make it way less hacky
    sketch_group.layers.insert(0, rectangle.build_rectangle_for_frame(figma_group))

    sketch_group.style = Style(do_objectID=utils.gen_object_id(figma_group['guid'], b'style'))
    sketch_group.style.contextSettings.opacity = figma_group['opacity']

    needs_clip_mask = not figma_group.get('frameMaskDisabled', False)
    if needs_clip_mask:
        # Add a clipping rectangle matching the frame size. No need to recalculate bounds
        # since the clipmask defines Sketch bounds (which match visible children)
        sketch_group.layers.insert(0, make_clipping_rect(figma_group['guid'],
                                                            sketch_group.frame))
    else:
        # When converting from a frame to a group, the bounding box should be adjusted
        # In Figma the frame box can be smalled than the children bounds, but not so in Sketch
        # To do so, we resize the frame to match the children bbox and also move the children
        # so that the top-left corner sits at 0,0
        children_bbox = positioning.group_bbox(sketch_group.layers)
        vector = [children_bbox[0], children_bbox[2]]

        for child in sketch_group.layers:
            child.frame.x -= vector[0]
            child.frame.y -= vector[1]

        # TODO: This probably breaks with rotation of the group
        sketch_group.frame.x += vector[0]
        sketch_group.frame.y += vector[1]
        sketch_group.frame.width = children_bbox[1] - children_bbox[0]
        sketch_group.frame.height = children_bbox[3] - children_bbox[2]

    return sketch_group


def make_clipping_rect(guid, frame):
    return Rectangle(
        do_objectID=utils.gen_object_id(guid, b'frame_mask'),
        name='Clip',
        frame=Rect(
            height=frame.height,
            width=frame.width,
            x=0,
            y=0
        ),
        hasClippingMask=True,
        clippingMaskMode=ClippingMaskMode.OUTLINE,
        style=Style(do_objectID=utils.gen_object_id(guid, b'frame_mask_style')),
        resizingConstraint=0,
        rotation=0,
    )
