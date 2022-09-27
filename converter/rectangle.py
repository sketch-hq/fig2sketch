from . import positioning, style
import utils

def convert(figma_rect):
    return {
        '_class': 'rectangle',
        'do_objectID': utils.gen_object_id(),
        'booleanOperation': -1,
        'exportOptions': {
            '_class': 'exportOptions',
            'exportFormats': [],
            'includedLayerIds': [],
            'layerOptions': 0,
            'shouldTrim': False
        },
        **positioning.convert(figma_rect),
        **utils.masking(figma_rect),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 0,
        'name': figma_rect.name,
        'nameIsFixed': False,
        'resizingConstraint': 9,
        'resizingType': 0,
        'shouldBreakMaskChain': False,
        'style': style.convert(figma_rect),
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
