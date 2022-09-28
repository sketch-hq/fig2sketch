from . import base
from math import sin, cos, pi
import numpy as np
import utils


def convert(figma_star):
    points = []
    for angle in np.arange(-pi / 2, 2 * pi - pi / 2, 2 * pi / figma_star.count):
        points += make_point_pair(angle, figma_star.count, figma_star.starInnerScale)

    return {
        '_class': 'star',
        **base.base_shape(figma_star),
        'name': figma_star.name,
        'edited': False,
        'isClosed': True,
        'pointRadiusBehaviour': 1,
        'numberOfPoints': figma_star.count,
        'points': points,
        'fixedRadius': 0,
        'hasConvertedToNewRoundCorners': True
    }


def make_point_pair(angle, number_points, scale):
    angle2 = angle + pi / number_points
    return [
        utils.make_point(0.5 + (cos(angle) * 0.5), 0.5 + (sin(angle) * 0.5)),
        utils.make_point(0.5 + (cos(angle2) * 0.5 * scale), 0.5 + (sin(angle2) * 0.5 * scale))
    ]
