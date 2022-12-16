from .base import *
from converter import tree, prototype
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
    context.init(None, {})


@pytest.fixture
def no_prototyping(monkeypatch):
    monkeypatch.setattr(prototype, "prototyping_information", lambda _: {})


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
