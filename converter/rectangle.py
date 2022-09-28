from . import base

def convert(figma_rect):
    return {
        **base.base_shape(figma_rect),
        '_class': 'rectangle',
        'name': figma_rect.name,
        'edited': False,
        'isClosed': True,
        'pointRadiusBehaviour': 1,
        'points': [
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{0, 0}',
                'curveMode': 1,
                'curveTo': '{0, 0}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{0, 0}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{1, 0}',
                'curveMode': 1,
                'curveTo': '{1, 0}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{1, 0}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{1, 1}',
                'curveMode': 1,
                'curveTo': '{1, 1}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{1, 1}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{0, 1}',
                'curveMode': 1,
                'curveTo': '{0, 1}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{0, 1}'
            }
        ],
        'fixedRadius': 0,
        'hasConvertedToNewRoundCorners': True
    }
