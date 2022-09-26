from . import positioning, style
from math import sin, cos, pi
import numpy as np
import utils


def make_point_pair(angle, number_points, scale):
    angle2 = angle + pi / number_points
    return [
        utils.make_point(0.5 + (cos(angle) * 0.5), 0.5 + (sin(angle) * 0.5)),
        utils.make_point(0.5 + (cos(angle2) * 0.5 * scale), 0.5 + (sin(angle2) * 0.5 * scale))
    ]


def convert(figma_star):
    points = []
    for angle in np.arange(-pi / 2, 2 * pi - pi / 2, 2 * pi / figma_star.count):
        points += make_point_pair(angle, figma_star.count, figma_star.starInnerScale)

    return {
        '_class': 'star',
        'do_objectID': utils.gen_object_id(),
        'booleanOperation': -1,
        'exportOptions': {
            '_class': 'exportOptions',
            'exportFormats': [],
            'includedLayerIds': [],
            'layerOptions': 0,
            'shouldTrim': False
        },
        **positioning.convert(figma_star),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 1,
        'name': figma_star.name,
        'nameIsFixed': False,
        'resizingConstraint': 63,
        'resizingType': 0,
        'shouldBreakMaskChain': False,
        'style': style.convert(figma_star),
        'edited': False,
        'isClosed': True,
        'pointRadiusBehaviour': 1,
        'numberOfPoints': figma_star.count,
        'points': points,
        'fixedRadius': 0,
        'hasConvertedToNewRoundCorners': True
    }
