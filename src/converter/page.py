from typing import Sequence

from converter import utils
from sketchformat.layer_group import *
from sketchformat.style import Fill

from . import style


def convert(fig_canvas: dict) -> Page:
    return make_page(fig_canvas["guid"], fig_canvas["name"])


def symbols_page() -> Page:
    page = make_page((0, 0), "Symbols", suffix=b"symbols_page")

    return page


def make_page(guid: Sequence[int], name: str, suffix: bytes = b"") -> Page:
    return Page(
        do_objectID=utils.gen_object_id(guid, suffix),
        frame=Rect(height=0, width=0, x=0, y=0),
        name=name,
        rotation=0.0,
        style=Style(do_objectID=utils.gen_object_id(guid, suffix + b"style")),
        hasClickThrough=True,
    )


DEFAULT_CANVAS_BACKGROUND = Color(
    red=0.9607843160629272, green=0.9607843160629272, blue=0.9607843160629272, alpha=1
)


def add_page_background(fig_canvas, sketch_page):
    if "backgroundColor" not in fig_canvas or fig_canvas["backgroundColor"] is None:
        return sketch_page

    background_color = style.convert_color(
        fig_canvas["backgroundColor"],
        fig_canvas.get("backgroundOpacity"),
    )
    if background_color != DEFAULT_CANVAS_BACKGROUND:
        sketch_page.style.fills = [Fill.Color(background_color)]

    return sketch_page
