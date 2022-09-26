from . import positioning, style
import utils
import numpy as np
from math import sin, cos, pi


def convert(figma_polygon):
    points = [utils.make_point(0.5 + (cos(angle) * 0.5), 0.5 + (sin(angle) * 0.5)) for angle in
              np.arange(-pi / 2, 2 * pi - pi / 2, 2 * pi / figma_polygon.count)]

    return {
        '_class': 'polygon',
        'do_objectID': utils.gen_object_id(),
        'booleanOperation': -1,
        'exportOptions': {
            '_class': 'exportOptions',
            'exportFormats': [],
            'includedLayerIds': [],
            'layerOptions': 0,
            'shouldTrim': False
        },
        **positioning.convert(figma_polygon),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 1,
        'name': figma_polygon.name,
        'nameIsFixed': False,
        'resizingConstraint': 63,
        'resizingType': 0,
        'shouldBreakMaskChain': False,
        'style': style.convert(figma_polygon),
        'edited': False,
        'isClosed': True,
        'pointRadiusBehaviour': 1,
        'numberOfPoints': figma_polygon.count,
        'points': points,
        'fixedRadius': 0,
        'hasConvertedToNewRoundCorners': True
    }
