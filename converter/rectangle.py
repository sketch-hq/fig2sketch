import utils
from . import base
from sketchformat.layer_common import Rect
from sketchformat.layer_shape import Rectangle
from sketchformat.style import Style


def convert(fig_rect: dict) -> Rectangle:
    corner_radius = fig_rect.get('cornerRadius', 0)
    independent = fig_rect.get('rectangleCornerRadiiIndependent', True)

    return Rectangle(
        **base.base_shape(fig_rect),
        fixedRadius=corner_radius,
        corners=Rectangle.Corners(
            fig_rect.get('rectangleTopLeftCornerRadius', 0) if independent else corner_radius,
            fig_rect.get('rectangleTopRightCornerRadius', 0) if independent else corner_radius,
            fig_rect.get('rectangleBottomRightCornerRadius', 0) if independent else corner_radius,
            fig_rect.get('rectangleBottomLeftCornerRadius', 0) if independent else corner_radius
        ),
    )


def build_rectangle_for_frame(fig_frame: dict) -> Rectangle:
    rectangle = convert(fig_frame)
    return make_background_rect(fig_frame['guid'], rectangle, 'Frame Background')


def make_background_rect(guid, frame, name) -> Rectangle:
    if type(frame) == Rectangle:
        rectangle = frame
        rectangle.name = name
    else:
        rectangle = Rectangle(
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

    rectangle.frame.x = 0
    rectangle.frame.y = 0
    rectangle.resizingConstraint = 10
    rectangle.rotation = 0

    return rectangle