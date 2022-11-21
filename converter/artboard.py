from converter import utils
from . import prototype, rectangle, style, base, group
from sketchformat.layer_group import Artboard
from sketchformat.style import BorderOptions, Fill, FillType


def convert(fig_frame: dict) -> Artboard:
    obj = Artboard(
        **base.base_styled(fig_frame), **prototype.prototyping_information(fig_frame)
    )

    return obj


def post_process_frame(fig_frame: dict, sketch_artboard: Artboard) -> Artboard:
    # Sketch only supports one custom color as an artboard background
    # If the frame has more than one color or other custom style we just create
    # the background rectangle with whatever style
    # If the frame/artboard has just one color (and not any other custom style)
    # we set the background color in sketch property
    # We could just always create the rectangle to simplify the logic, but I guess
    # adding always a background rectangle is an overhead for the document itself
    for corner in [
        "rectangleTopLeftCornerRadius",
        "rectangleTopLeftCornerRadius",
        "rectangleTopLeftCornerRadius",
        "rectangleTopLeftCornerRadius",
    ]:
        if fig_frame.get(corner, 0) != 0:
            utils.log_conversion_warning("ART001", fig_frame)
            break

    if sketch_artboard.rotation != 0:
        utils.log_conversion_warning("ART002", fig_frame)

    # Figma automatically clips overlays but not Sketch, so we need to add a mask
    if sketch_artboard.overlaySettings is not None:
        sketch_artboard.layers.insert(
            0, rectangle.make_clipping_rect(fig_frame, sketch_artboard.frame)
        )

    match sketch_artboard.style.fills:
        case [Fill(fillType=FillType.COLOR, color=color)]:
            # Single color, apply to artboard
            sketch_artboard.backgroundColor = color
            sketch_artboard.hasBackgroundColor = True
            sketch_artboard.style.fills = []

    if sketch_artboard.style.fills or sketch_artboard.style.borders:
        # Anything else, add a background rect
        utils.log_conversion_warning("ART003", fig_frame)
        group.convert_frame_style(fig_frame, sketch_artboard)

    return sketch_artboard
