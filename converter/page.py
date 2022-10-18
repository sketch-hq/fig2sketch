import utils
from sketchformat.style import Style


def convert(figma_canvas):
    return make_page(figma_canvas.id, figma_canvas.name)


def symbols_page():
    page = make_page((0, 0), 'Symbols', suffix=b'symbols_page')
    page['layers'] = []

    return page


def make_page(guid, name, suffix=b''):
    return {
        '_class': 'page',
        'do_objectID': utils.gen_object_id(guid, suffix),
        'booleanOperation': -1,
        'clippingMaskMode': 0,
        'exportOptions': {
            '_class': 'exportOptions',
            'exportFormats': [],
            'includedLayerIds': [],
            'layerOptions': 0,
            'shouldTrim': False
        },
        'frame': {
            '_class': 'rect',
            'constrainProportions': False,
            'height': 300,
            'width': 300,
            'x': 0,
            'y': 0
        },
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 0,
        'name': name,
        'nameIsFixed': False,
        'resizingConstraint': 63,
        'resizingType': 0,
        'rotation': 0,
        'shouldBreakMaskChain': False,
        'style': Style(do_objectID=utils.gen_object_id(guid, suffix + b'style')),
        'hasClickThrough': True,
        'isTemplate': False,
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
        'grid': {
            'isEnabled': False,
            'gridSize': 8,
            'thickGridTimes': 1,
            '_class': 'simpleGrid'
        },
        'groupLayout': {
            '_class': 'MSImmutableFreeformGroupLayout'
        },
        'hasClippingMask': False
    }
