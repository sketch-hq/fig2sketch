import utils


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
        'style': {
            '_class': 'style',
            'windingRule': 1,
            'blur': {
                '_class': 'blur',
                'center': '{0.5, 0.5}',
                'isEnabled': False,
                'motionAngle': 0,
                'radius': 10,
                'saturation': 1,
                'type': 0
            },
            'borderOptions': {
                '_class': 'borderOptions',
                'dashPattern': [],
                'isEnabled': True,
                'lineCapStyle': 0,
                'lineJoinStyle': 0
            },
            'borders': [],
            'colorControls': {
                '_class': 'colorControls',
                'brightness': 0,
                'contrast': 1,
                'hue': 0,
                'isEnabled': False,
                'saturation': 1
            },
            'contextSettings': {
                '_class': 'graphicsContextSettings',
                'blendMode': 0,
                'opacity': 1
            },
            'do_objectID': utils.gen_object_id(guid, suffix + b'style'),
            'fills': [],
            'innerShadows': [],
            'miterLimit': 10,
            'startMarkerType': 0,
            'endMarkerType': 0,
            'shadows': [],
        },
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
