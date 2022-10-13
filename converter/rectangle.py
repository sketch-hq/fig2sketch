from . import base


def convert(figma_rect):
    return {
        **base.base_shape(figma_rect),
        '_class': 'rectangle',
        'name': figma_rect.name,
        'edited': False,
        'isClosed': True,
        # Sketch smooth corners are a boolean, Figma is a percent. I picked an arbitrary threshold
        'pointRadiusBehaviour': 2 if figma_rect.cornerSmoothing > 0.4 else 0,
        'points': [
            {
                '_class': 'curvePoint',
                'cornerRadius': figma_rect.get('rectangleTopLeftCornerRadius', 0),
                'cornerStyle': 0,
                'curveFrom': '{0, 0}',
                'curveMode': 1,
                'curveTo': '{0, 0}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{0, 0}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': figma_rect.get('rectangleTopRightCornerRadius', 0),
                'cornerStyle': 0,
                'curveFrom': '{1, 0}',
                'curveMode': 1,
                'curveTo': '{1, 0}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{1, 0}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': figma_rect.get('rectangleBottomRightCornerRadius', 0),
                'cornerStyle': 0,
                'curveFrom': '{1, 1}',
                'curveMode': 1,
                'curveTo': '{1, 1}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{1, 1}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': figma_rect.get('rectangleBottomLeftCornerRadius', 0),
                'cornerStyle': 0,
                'curveFrom': '{0, 1}',
                'curveMode': 1,
                'curveTo': '{0, 1}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{0, 1}'
            }
        ],
        'fixedRadius': figma_rect.cornerRadius,
        'hasConvertedToNewRoundCorners': True,
        'needsConvertionToNewRoundCorners': False
    }
