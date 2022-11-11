from . import positioning, prototype, rectangle, style, base
from sketchformat.style import Style, BorderOptions, Fill, Color, FillType
from sketchformat.layer_group import Artboard
import utils


def convert(fig_frame: dict) -> Artboard:
    obj = Artboard(
        **base.base_styled(fig_frame),
        **prototype.prototyping_information(fig_frame)
    )

    # Remove style from artboards. TODO: Is this needed?
    obj.style.fills = []
    obj.style.borders = []
    obj.style.borderOptions = BorderOptions()

    return obj

def post_process_frame(fig_frame: dict, sketch_artboard: Artboard) -> Artboard:
    # Sketch only supports one custom color as an artboard background
    # If the frame has more than one color or other custom style we just create
    # the background rectangle with whatever style
    # If the frame/artboard has just one color (and not any other custom style)
    # we set the background color in sketch property
    # We could just always create the rectangle to simplify the logic, but I guess
    # adding always a background rectangle is an overhead for the document itself
    artboard_style = style.convert(fig_frame)

    for corner in ['rectangleTopLeftCornerRadius',
        'rectangleTopLeftCornerRadius',
        'rectangleTopLeftCornerRadius',
        'rectangleTopLeftCornerRadius']:
        if fig_frame.get(corner, 0) != 0:
            utils.log_conversion_warning("ART001", fig_frame)
            break

    if sketch_artboard.rotation != 0:
        utils.log_conversion_warning("ART002", fig_frame)

    match artboard_style.fills:
        case [Fill(fillType=FillType.COLOR, color=color)]:
            # Single color, apply to artboard
            sketch_artboard.backgroundColor = color
            sketch_artboard.hasBackgroundColor = True
        case _:
            # Anything else, add a background rect
            sketch_artboard.layers.insert(0, rectangle.build_rectangle_for_frame(fig_frame))

    return sketch_artboard
