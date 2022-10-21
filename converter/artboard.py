from . import positioning, prototype
from sketchformat.style import Style
import utils


def convert(figma_frame):
    return {
        '_class': 'artboard',
        'do_objectID': utils.gen_object_id(figma_frame['guid']),
        'booleanOperation': -1,
        'clippingMaskMode': 0,
        'exportOptions': {
            '_class': 'exportOptions',
            'exportFormats': [],
            'includedLayerIds': [],
            'layerOptions': 0,
            'shouldTrim': False
        },
        # TODO: Get this from Figma
        'backgroundColor': {
            '_class': 'color',
            'alpha': 1,
            'blue': 1,
            'green': 1,
            'red': 1
        },
        **positioning.convert(figma_frame),
        'includeBackgroundColorInExport': False,
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isTemplate': False,
        'isVisible': True,
        'groupLayout': {
            '_class': 'MSImmutableFreeformGroupLayout'
        },
        'hasBackgroundColor': False,
        'hasClippingMask': False,
        'horizontalRulerData': {
            '_class': 'rulerData',
            'base': 0,
            'guides': []
        },
        'verticalRulerData': {
            '_class': 'rulerData',
            'base': 0,
            'guides': []
        },
        'layerListExpandedType': 2,
        'name': figma_frame['name'],
        'nameIsFixed': False,
        'resizingConstraint': 9,
        'resizingType': 0,
        'shouldBreakMaskChain': True,
        'style': Style(do_objectID=utils.gen_object_id(figma_frame['guid'], b'style')),
        'hasClickThrough': False,
        'resizesContent': True,
        **prototype.convert_flow(figma_frame),
        **prototype.prototyping_information(figma_frame)
    }
