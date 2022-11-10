from . import base
from sketchformat.layer_shape import Polygon


def convert(fig_polygon):
    return Polygon(
        **base.base_shape(fig_polygon),
        numberOfPoints=fig_polygon['count']
    )
