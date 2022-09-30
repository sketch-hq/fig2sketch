from . import base
from math import sin, cos, pi
import numpy as np


def convert(figma_star):
    points = []
    for angle in np.arange(-pi / 2, 2 * pi - pi / 2, 2 * pi / figma_star.count):
        points += make_point_pair(figma_star, angle)

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


def make_point_pair(figma_star, angle):
    angle2 = angle + pi / figma_star.count
    scale = figma_star.starInnerScale

    x1 = 0.5 + (cos(angle) * 0.5)
    y1 = 0.5 + (sin(angle) * 0.5)

    x2 = 0.5 + (cos(angle2) * 0.5 * scale)
    y2 = 0.5 + (sin(angle2) * 0.5 * scale)

    return [
        base.make_point(figma_star, x1, y1),
        base.make_point(figma_star, x2, y2)
    ]
