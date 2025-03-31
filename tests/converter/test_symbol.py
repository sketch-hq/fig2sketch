from .base import *
from converter import tree, symbol
from sketchformat.layer_shape import Rectangle
import pytest
from converter.context import context

FIG_SYMBOL = {
    **FIG_BASE,
    "type": "SYMBOL",
    "children": [],
}


@pytest.fixture
def empty_context(monkeypatch):
    context.init(None, {}, "DISPLAY_P3")


def test_rounded_corners(no_prototyping, empty_context):
    instance = tree.convert_node(
        {**FIG_SYMBOL, "rectangleTopLeftCornerRadius": 5},
        "",
    )

    symbol = context.symbols_page.layers[0]

    assert instance.symbolID == symbol.symbolID

    assert isinstance(symbol.layers[0], Rectangle)
    assert symbol.layers[0].hasClippingMask
    assert symbol.layers[0].points[0].cornerRadius == 5


def test_inner_shadows_children_of_symbol(no_prototyping, empty_context):
    g = tree.convert_node(
        {
            **FIG_SYMBOL,
            "effects": [
                {
                    "type": "INNER_SHADOW",
                    "radius": 4,
                    "spread": 0,
                    "offset": {"x": 1, "y": 3},
                    "color": FIG_COLOR[1],
                    "visible": True,
                }
            ],
            "children": [{**FIG_BASE, "type": "ROUNDED_RECTANGLE"}],
        },
        "",
    )

    symbol = context.symbols_page.layers[0]
    assert symbol.style.shadows == []

    [child] = symbol.layers
    assert child.style.shadows == [
        Shadow(
            blurRadius=4, offsetX=1, offsetY=3, spread=0, color=SKETCH_COLOR[1], isInnerShadow=True
        )
    ]


def test_variant_name():
    variants = {
        **FIG_BASE,
        "type": "FRAME",
        "name": "Starch",
        "guid": (22, 22),
        "isStateGroup": True,
        "stateGroupPropertyValueOrders": [
            {"property": "Property 1", "values": ["Potato", "Orange"]},
            {"property": "Property 2", "values": ["Something", "Another"]},
        ],
        "children": [{**FIG_SYMBOL, "name": "Property 1=Potato, Property 2=Another"}],
        "parent": {"guid": (22, 22)},
    }
    assert symbol.symbol_variant_name(variants, variants["children"][0]) == "Starch/Potato/Another"
