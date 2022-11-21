from converter import utils
from . import base, positioning, rectangle
from sketchformat.layer_group import Group


def convert(fig_group):
    return Group(
        **base.base_styled(fig_group),
    )


def post_process_frame(fig_group, sketch_group):
    # Do nothing for fig groups, they translate directly to Sketch
    if fig_group["resizeToFit"]:
        return sketch_group

    convert_frame_style(fig_group, sketch_group)
    convert_frame_to_group(fig_group, sketch_group)

    return sketch_group


def convert_frame_to_group(fig_group, sketch_group):
    needs_clip_mask = not fig_group.get("frameMaskDisabled", False)
    if needs_clip_mask:
        # Add a clipping rectangle matching the frame size. No need to recalculate bounds
        # since the clipmask defines Sketch bounds (which match visible children)
        sketch_group.layers.insert(
            0, rectangle.make_clipping_rect(fig_group["guid"], sketch_group.frame)
        )
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
    bgrect = rectangle.convert(fig_group)
    sketch_group.layers.insert(0, rectangle.make_background_rect(fig_group["guid"], bgrect, "Frame Background"))