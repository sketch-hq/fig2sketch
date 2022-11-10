from . import base
import utils
from sketchformat.layer_shape import Rectangle, PointRadiusBehaviour


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
    background_rect = convert(fig_frame)
    background_rect.frame.x = 0
    background_rect.frame.y = 0
    background_rect.rotation = 0
    background_rect.name = 'Frame background'
    background_rect.do_objectID = utils.gen_object_id(fig_frame['guid'], b'background')
    background_rect.resizingConstraint = 10 # Fixed to borders
    return background_rect
