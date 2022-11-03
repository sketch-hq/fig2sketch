from . import base
from sketchformat.layer_shape import Polygon


def convert(figma_polygon):
    return Polygon(
        **base.base_shape(figma_polygon),
        numberOfPoints=figma_polygon['count']
    )
