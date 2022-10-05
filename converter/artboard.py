from . import positioning
import utils


def convert(figma_frame):
    return {
        '_class': 'artboard',
        'do_objectID': utils.gen_object_id(figma_frame.id),
        'booleanOperation': -1,
        'exportOptions': {
            '_class': 'exportOptions',
            'exportFormats': [],
            'includedLayerIds': [],
            'layerOptions': 0,
            'shouldTrim': False
        },
        **positioning.convert(figma_frame),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 2,
        'name': figma_frame.name,
        'nameIsFixed': False,
        'resizingConstraint': 9,
        'resizingType': 0,
        'shouldBreakMaskChain': True,
        'style': {
            '_class': 'style',
            'do_objectID': utils.gen_object_id(figma_frame.id, b'style'),
            'borders': [],
            'borderOptions': {
                '_class': 'borderOptions',
                'isEnabled': True,
                'lineCapStyle': 0,
                'lineJoinStyle': 0
            },
            'fills': [],
            'startMarkerType': 0,
            'endMarkerType': 0,
            'miterLimit': 10,
            'windingRule': 0,
            'shadows': [],
            'innerShadows': [],
            'contextSettings': {
                '_class': 'graphicsContextSettings',
                'blendMode': 0,
                'opacity': 1
            },
            'colorControls': {
                '_class': 'colorControls',
                'isEnabled': True,
                'brightness': 0,
                'contrast': 1,
                'hue': 0,
                'saturation': 1
            }
        },
        'hasClickThrough': False,
        'resizesContent': True
    }
