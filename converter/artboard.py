from . import positioning, prototype, rectangle, style
from sketchformat.style import Style
import utils
import copy

DEFAULT_FIGMA_ARTBOARD_FILL = {
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": {
                            "r": 1.0,
                            "g": 1.0,
                            "b": 1.0,
                            "a": 1.0
                        },
                        "opacity": 1.0,
                        "visible": True,
                        "blendMode": "NORMAL"
                    }
                ]
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
        **prototype.convert_flow(figma_frame),
        **prototype.prototyping_information(figma_frame)
    }

def post_process_frame(figma_frame, sketch_artboard):
    # TODO: This is kind of messy. Surely it can be improved
    # TODO: This will require a proper test
    # Sketch only supports one custom color as an artboard background
    # If the frame has more than one color or other custom style we just create
    # the bacground rectangle with whatever style
    # If the frame/artboard has just one color (and not any other custom style)
    # we set the background color in sketch property
    # We could just always create the rectangle to simplify the logic, but I guess
    # adding always a background rectangle is an overhead for the document itself
    if len(figma_frame['fillPaints']) == 1:
        artboard_style = style.convert(figma_frame)
        default_artboard_style = Style(
            do_objectID=utils.gen_object_id(figma_frame['guid'], b'style'),
            fills=[style.convert_fill(None, f) for f in DEFAULT_FIGMA_ARTBOARD_FILL['fillPaints']]
        )
        if artboard_style != default_artboard_style:
            artboard_style_copy = copy.deepcopy(artboard_style)
            artboard_style_copy.fills[0].color = None
            default_artboard_style.fills[0].color = None
            if artboard_style_copy == default_artboard_style:
                sketch_artboard['backgroundColor']['alpha'] = figma_frame['fillPaints'][0]['color']['a']
                sketch_artboard['backgroundColor']['blue'] = figma_frame['fillPaints'][0]['color']['b']
                sketch_artboard['backgroundColor']['green'] = figma_frame['fillPaints'][0]['color']['g']
                sketch_artboard['backgroundColor']['red'] = figma_frame['fillPaints'][0]['color']['r']
                sketch_artboard['hasBackgroundColor'] = True
            else:
                if 'layers' not in sketch_artboard:
                    sketch_artboard['layers'] = []
                sketch_artboard['layers'].insert(0, rectangle.build_rectangle_for_frame(figma_frame))
    else:
        if 'layers' not in sketch_artboard:
            sketch_artboard['layers'] = []
        sketch_artboard['layers'].insert(0, rectangle.build_rectangle_for_frame(figma_frame))
    return sketch_artboard