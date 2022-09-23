from . import positioning, style
import utils


def convert(figma_ellipse):
    return {
        '_class': 'oval',
        'do_objectID': utils.gen_object_id(),
        'booleanOperation': -1,
        'exportOptions': {
            '_class': 'exportOptions',
            'exportFormats': [],
            'includedLayerIds': [],
            'layerOptions': 0,
            'shouldTrim': False
        },
        **positioning.convert(figma_ellipse),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 1,
        'name': figma_ellipse['name'],
        'nameIsFixed': False,
        'resizingConstraint': 63,
        'resizingType': 0,
        'shouldBreakMaskChain': False,
        'style': style.convert(figma_ellipse),
        'edited': False,
        'isClosed': True,
        'pointRadiusBehaviour': 1,
        'points': [
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
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
                'curveFrom': '{0, 0.77614237490000004}',
                'curveMode': 2,
                'curveTo': '{0, 0.22385762510000001}',
                'hasCurveFrom': True,
                'hasCurveTo': True,
                'point': '{0, 0.5}'
            }
        ],
        'fixedRadius': 0,
        'hasConvertedToNewRoundCorners': True
    }
