from . import base


def convert(figma_ellipse):
    return {
        '_class': 'oval',
        **base.base_shape(figma_ellipse),
        'name': figma_ellipse.name,
        'edited': False,
        'isClosed': True,
        'pointRadiusBehaviour': 1,
        'points': [
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'cornerStyle': 0,
                'curveFrom': '{0.77614237490000004, 1}',
                'curveMode': 2,
                'curveTo': '{0.22385762510000001, 1}',
                'hasCurveFrom': True,
                'hasCurveTo': True,
                'point': '{0.5, 1}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'cornerStyle': 0,
                'curveFrom': '{1, 0.22385762510000001}',
                'curveMode': 2,
                'curveTo': '{1, 0.77614237490000004}',
                'hasCurveFrom': True,
                'hasCurveTo': True,
                'point': '{1, 0.5}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'cornerStyle': 0,
                'curveFrom': '{0.22385762510000001, 0}',
                'curveMode': 2,
                'curveTo': '{0.77614237490000004, 0}',
                'hasCurveFrom': True,
                'hasCurveTo': True,
                'point': '{0.5, 0}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'cornerStyle': 0,
                'curveFrom': '{0, 0.77614237490000004}',
                'curveMode': 2,
                'curveTo': '{0, 0.22385762510000001}',
                'hasCurveFrom': True,
                'hasCurveTo': True,
                'point': '{0, 0.5}'
            }
        ],
        'fixedRadius': 0
    }
