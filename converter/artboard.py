from . import positioning, base
from .context import context
from sketchformat.prototype import *
from sketchformat.style import Style
import utils

OVERLAY_INTERACTION = {
    'NONE': OverlayBackgroundInteraction.NONE,
    'CLOSE_ON_CLICK_OUTSIDE': OverlayBackgroundInteraction.CLOSES_OVERLAY
}


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
        **prototyping_information(figma_frame),
        **base.prototyping_flow(figma_frame),
    }


def prototyping_information(figma_frame):
    # Some information about the prototype is in the Figma page
    figma_canvas = context.figma_node(figma_frame['parent']['guid'])
    if 'prototypeDevice' not in figma_canvas:
        return {
            'isFlowHome': False,
            'overlayBackgroundInteraction': 0,
            'presentationStyle': 0
        }

    # TODO: Overflow scrolling means making the artboard bigger (fit the child bounds)
    if figma_frame.get('scrollDirection', 'NONE') != 'NONE':
        print('Scroll overflow direction not supported')

    obj = {
        'isFlowHome': figma_frame['prototypeStartingPoint']['name'] != '',
        'prototypeViewport': PrototypeViewport(
            name=figma_canvas['prototypeDevice']['presetIdentifier'],
            size=utils.point_to_string(figma_canvas['prototypeDevice']['size'])
        ),
        'overlayBackgroundInteraction': OverlayBackgroundInteraction.NONE,
        'presentationStyle': PrototypePresentationStyle.SCREEN
    }

    if 'overlayBackgroundInteraction' in figma_frame:
        obj['overlayBackgroundInteraction'] = OVERLAY_INTERACTION[
            figma_frame['overlayBackgroundInteraction']]
        obj['presentationStyle'] = PrototypePresentationStyle.OVERLAY
        obj['overlaySettings'] = FlowOverlaySettings.Centered()

    return obj
