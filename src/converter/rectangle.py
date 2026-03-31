from . import base, style as converter_style
from converter import utils
from sketchformat.layer_common import Rect, ClippingMaskMode
from sketchformat.layer_shape import Rectangle
from sketchformat.style import Style


def convert(fig_rect: dict) -> Rectangle:
    return Rectangle(
        **base.base_shape(fig_rect),
        corners=convert_corners(fig_rect),
    )


def convert_corners(fig_rect: dict) -> Rectangle.Corners:
    radius = fig_rect.get("cornerRadius", 0)
    fixed = not fig_rect.get("rectangleCornerRadiiIndependent", True)
    return Rectangle.Corners(
        radius if fixed else fig_rect.get("rectangleTopLeftCornerRadius", 0),
        radius if fixed else fig_rect.get("rectangleTopRightCornerRadius", 0),
        radius if fixed else fig_rect.get("rectangleBottomRightCornerRadius", 0),
        radius if fixed else fig_rect.get("rectangleBottomLeftCornerRadius", 0),
    )


def make_clipping_rect(fig: dict, frame: Rect) -> Rectangle:
    obj = make_background_rect(fig, frame, "Clip")
    obj.hasClippingMask = True
    obj.clippingMaskMode = ClippingMaskMode.OUTLINE
    return obj


def make_background_rect(fig: dict, frame: Rect, name: str) -> Rectangle:
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
        corners=convert_corners(fig),
        pointRadiusBehaviour=base.point_radius_behaviour(fig),
    )
