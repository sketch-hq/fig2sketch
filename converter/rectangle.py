from . import base
from sketchformat.layer_shape import Rectangle, PointRadiusBehaviour


def convert(figma_rect) -> Rectangle:
    return Rectangle(
        **base.base_shape(figma_rect), # TODO: Type annotations
        name=figma_rect.name, # TODO: Move to base
        # Sketch smooth corners are a boolean, Figma is a percent. I picked an arbitrary threshold
        pointRadiusBehaviour=PointRadiusBehaviour.V1_SMOOTH if figma_rect.cornerSmoothing > 0.4 else PointRadiusBehaviour.V1,
        fixedRadius=figma_rect.cornerRadius,
        corners=Rectangle.Corners(
            figma_rect.get('rectangleTopLeftCornerRadius', 0),
            figma_rect.get('rectangleTopRightCornerRadius', 0),
            figma_rect.get('rectangleBottomRightCornerRadius', 0),
            figma_rect.get('rectangleBottomLeftCornerRadius', 0)
        ),
    )
