import utils
from sketchformat.style import Style
from sketchformat.layer_common import *


def convert(figma_canvas):
    return make_page(figma_canvas['guid'], figma_canvas['name'])


def symbols_page():
    page = make_page((0, 0), 'Symbols', suffix=b'symbols_page')

    return page


def make_page(guid, name, suffix=b''):
    return Page(
        do_objectID=utils.gen_object_id(guid, suffix),
        frame=Rect(
            height=300,
            width=300,
            x=0,
            y=0
        ),
        name=name,
        resizingConstraint=63,
        rotation=0.0,
        style=Style(do_objectID=utils.gen_object_id(guid, suffix + b'style')),
        hasClickThrough=True
    )
