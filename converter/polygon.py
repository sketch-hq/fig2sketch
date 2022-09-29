from . import base
import numpy as np
from math import sin, cos, pi
import utils


def convert(figma_polygon):
    points = [utils.make_point(0.5 + (cos(angle) * 0.5), 0.5 + (sin(angle) * 0.5)) for angle in
              np.arange(-pi / 2, 2 * pi - pi / 2, 2 * pi / figma_polygon.count)]

    return {
        '_class': 'polygon',
        **base.base_shape(figma_polygon),
        'name': figma_polygon.name,
        'edited': False,
        'isClosed': True,
        'pointRadiusBehaviour': 1,
        'numberOfPoints': figma_polygon.count,
        'points': points,
        'fixedRadius': 0,
        'hasConvertedToNewRoundCorners': True
    }
