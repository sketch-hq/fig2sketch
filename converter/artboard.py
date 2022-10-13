from . import positioning, base
from .context import context
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
        'isTemplate': False,
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
        'resizesContent': True,
        **prototyping_information(figma_frame),
        **base.prototyping_flow(figma_frame),
    }


# TODO: Check isDeleted properties all over the code (prototyping, symbol properties, etc.)
def prototyping_information(figma_frame):
    # Some information about the prototypye is in the Figma page
    figma_canvas = context.figma_node(figma_frame['parent']['id'])
    if 'prototypeDevice' not in figma_canvas:
        return {}

    # TODO: Overflow scrolling means making the artboard bigger (fit the child bounds)
    if figma_frame.get('scrollDirection', 'NONE') != 'NONE':
        print('Scroll overflow direction not supported')

    obj = {
        'isFlowHome': figma_frame['prototypeStartingPoint']['name'] != '',
        'prototypeViewport': {
            '_class': 'MSImmutablePrototypeViewport',
            # 'libraryID': 'EB972BCC-0467-4E50-998E-0AC5A39517F0',
            'name': figma_canvas['prototypeDevice']['presetIdentifier'],
            'size': f"{{{figma_canvas['prototypeDevice']['size']['x']}, {figma_canvas['prototypeDevice']['size']['y']}}}",
            # 'templateID': '55992B99-92E5-4A93-AF90-B3A461675C05'
        },
    }

    return obj
