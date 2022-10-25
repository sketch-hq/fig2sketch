from . import base
import numpy as np
from math import sin, cos, pi


def convert(figma_polygon):
    points = [base.make_point(figma_polygon, 0.5 + (cos(angle) * 0.5), 0.5 + (sin(angle) * 0.5))
              for angle in
              np.arange(-pi / 2, 2 * pi - pi / 2, 2 * pi / figma_polygon['count'])]

    return {
        '_class': 'polygon',
        **base.base_shape(figma_polygon),
        'edited': False,
        'isClosed': True,
        'pointRadiusBehaviour': 1,
        'numberOfPoints': figma_polygon['count'],
        'points': points
    }
