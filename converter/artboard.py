from . import positioning, prototype, rectangle, style, base
from sketchformat.style import Style, BorderOptions, Fill, Color, FillType
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

def convert(figma_frame) -> Artboard:
    obj = Artboard(
        **base.base_shape(figma_frame),
        **prototype.prototyping_information(figma_frame)
    )

    # Remove style from artboards. TODO: Is this needed?
    obj.style.fills = []
    obj.style.borders = []
    obj.style.borderOptions = BorderOptions()

    return obj

def post_process_frame(figma_frame, sketch_artboard: Artboard) -> Artboard:
    # Sketch only supports one custom color as an artboard background
    # If the frame has more than one color or other custom style we just create
    # the background rectangle with whatever style
    # If the frame/artboard has just one color (and not any other custom style)
    # we set the background color in sketch property
    # We could just always create the rectangle to simplify the logic, but I guess
    # adding always a background rectangle is an overhead for the document itself
    artboard_style = style.convert(figma_frame)

    match artboard_style.fills:
        case [Fill(fillType=FillType.COLOR, color=color)]:
            # Single color, apply to artboard
            sketch_artboard.backgroundColor = color
            sketch_artboard.hasBackgroundColor = True
        case _:
            # Anything else, add a background rect
            sketch_artboard.layers.insert(0, rectangle.build_rectangle_for_frame(figma_frame))

    return sketch_artboard
