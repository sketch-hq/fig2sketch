from . import base
import utils
from sketchformat.layer_shape import Rectangle, PointRadiusBehaviour


def convert(figma_rect) -> Rectangle:
    corner_radius = figma_rect.get('cornerRadius', 0)

    return Rectangle(
        **base.base_shape(figma_rect),  # TODO: Type annotations
        # Sketch smooth corners are a boolean, Figma is a percent. I picked an arbitrary threshold
        pointRadiusBehaviour=PointRadiusBehaviour.V1_SMOOTH if figma_rect.get('cornerSmoothing', 0) > 0.4 else PointRadiusBehaviour.V1,
        fixedRadius=corner_radius,
        corners=Rectangle.Corners(
            figma_rect.get('rectangleTopLeftCornerRadius', corner_radius),
            figma_rect.get('rectangleTopRightCornerRadius', corner_radius),
            figma_rect.get('rectangleBottomRightCornerRadius', corner_radius),
            figma_rect.get('rectangleBottomLeftCornerRadius', corner_radius)
        ),
    )

def build_rectangle_for_frame(figma_frame):
    background_rect = convert(figma_frame)
    background_rect['frame']['x'] = 0
    background_rect['frame']['y'] = 0
    background_rect['rotation'] = 0
    background_rect['name'] = 'Frame background'
    background_rect['do_objectID'] = utils.gen_object_id(figma_frame['guid'], b'background')
    background_rect['resizingConstraint'] = 63
    return background_rect
