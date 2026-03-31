from . import base, style as converter_style
from converter import utils
from sketchformat.layer_common import Rect, ClippingMaskMode
from sketchformat.layer_shape import Rectangle
from sketchformat.style import Style
from typing import Tuple


def convert(fig_rect: dict) -> Rectangle:
    _, corners = convert_corners(fig_rect)
    return Rectangle(
        **base.base_shape(fig_rect),
        corners=corners,
    )


def convert_corners(fig_rect: dict) -> Tuple[float, Rectangle.Corners]:
    radius = fig_rect.get("cornerRadius", 0)
    fixed = not fig_rect.get("rectangleCornerRadiiIndependent", True)
    corners = Rectangle.Corners(
        radius if fixed else fig_rect.get("rectangleTopLeftCornerRadius", 0),
        radius if fixed else fig_rect.get("rectangleTopRightCornerRadius", 0),
        radius if fixed else fig_rect.get("rectangleBottomRightCornerRadius", 0),
        radius if fixed else fig_rect.get("rectangleBottomLeftCornerRadius", 0),
    )
    # Mixed corners must keep `fixedRadius` at zero so Sketch shows them as "Mixed".
    fixed_radius = float(corners[0]) if len(set(corners)) == 1 else 0
    return fixed_radius, corners


def make_clipping_rect(fig: dict, frame: Rect) -> Rectangle:
    obj = make_background_rect(fig, frame, "Clip")
    obj.hasClippingMask = True
    obj.clippingMaskMode = ClippingMaskMode.OUTLINE
    return obj


def make_background_rect(fig: dict, frame: Rect, name: str) -> Rectangle:
    _, corners = convert_corners(fig)
    return Rectangle(
        do_objectID=utils.gen_object_id(fig["guid"], name.encode()),
        name=name,
        frame=Rect(height=frame.height, width=frame.width, x=0, y=0),
        style=Style(
            do_objectID=utils.gen_object_id(fig["guid"], f"{name}_style".encode()),
            corners=converter_style.convert_corners(fig),
        ),
        horizontalPins=2,
        verticalPins=2,
        rotation=0,
        corners=corners,
        pointRadiusBehaviour=base.point_radius_behaviour(fig),
    )
