from . import positioning, prototype, rectangle, style, base
from sketchformat.style import Style, BorderOptions
from sketchformat.layer_group import Artboard
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
    obj = Artboard(
        **base.base_shape(figma_frame),
        **prototype.prototyping_information(figma_frame)
    )

    # Remove style from artboards. TODO: Is this needed?
    obj.style.fills = []
    obj.style.borders = []
    obj.style.borderOptions = BorderOptions()

    return obj

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
                sketch_artboard.backgroundColor = style.convert_color(figma_frame['fillPaints'][0]['color'])
                sketch_artboard.hasBackgroundColor = True
            else:
                sketch_artboard.layers.insert(0, rectangle.build_rectangle_for_frame(figma_frame))
    else:
        sketch_artboard.layers.insert(0, rectangle.build_rectangle_for_frame(figma_frame))
    return sketch_artboard
