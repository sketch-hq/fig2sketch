import pytest
from .base import *
from converter import prototype, tree, base
from sketchformat.style import *
from unittest.mock import ANY
from converter.context import context

FIG_ARTBOARD = {
    **FIG_BASE,
    "type": "FRAME",
    "resizeToFit": False,
    "children": [],
}


@pytest.fixture
def no_prototyping(monkeypatch):
    monkeypatch.setattr(prototype, "prototyping_information", lambda _: {})


@pytest.mark.usefixtures("no_prototyping")
class TestIDs:
    def test_avoid_duplicated_ids(self):
        ab = tree.convert_node({**FIG_ARTBOARD, "overrideKey": (789, 112)}, "CANVAS")

        assert ab.do_objectID == utils.gen_object_id(FIG_ARTBOARD["guid"])


@pytest.mark.usefixtures("no_prototyping")
class TestFrameBackgroud:
    def test_no_background(self):
        ab = tree.convert_node(FIG_ARTBOARD, "CANVAS")

        assert ab.hasBackgroundColor == False

    def test_disabled_background(self):
        ab = tree.convert_node(
            {
                **FIG_ARTBOARD,
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[0],
                        "opacity": 0.9,
                        "visible": False,
                    }
                ],
            },
            "CANVAS",
        )

        assert ab.hasBackgroundColor == False

    def test_simple_background(self):
        ab = tree.convert_node(
            {
                **FIG_ARTBOARD,
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[0],
                        "opacity": 0.9,
                        "visible": True,
                    }
                ],
            },
            "CANVAS",
        )

        assert ab.hasBackgroundColor == False
        assert ab.style.fills[0].fillType == FillType.COLOR
        assert ab.style.fills[0].color == SKETCH_COLOR[0]

    def test_gradient_background(self, warnings):
        ab = tree.convert_node(
            {**FIG_ARTBOARD, **FIG_GRADIENT_FILL_PAINTS},
            "CANVAS",
        )

        assert ab.hasBackgroundColor == False
        assert len(ab.style.fills) == 1
        assert ab.style.fills[0].fillType == FillType.GRADIENT


FIG_TEXT = {
    **FIG_BASE,
    "type": "TEXT",
    "fontName": {"family": "Roboto", "style": "Normal"},
    "fontSize": 12,
    "textAlignVertical": "CENTER",
    "textAlignHorizontal": "CENTER",
    "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[0], "opacity": 1, "visible": True}],
    "strokeAlign": "CENTER",
    "strokeWeight": 1,
}

FIG_COLOR_STYLE = {
    **FIG_BASE,
    "type": "ROUNDED_RECTANGLE",
    "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[1], "opacity": 0.7, "visible": True}],
}

FIG_TEXT_STYLE = {
    **FIG_BASE,
    "type": "TEXT",
    "fontName": {"family": "CustomFont", "style": "Normal"},
}


@pytest.fixture
def style_overrides(monkeypatch):
    context.init(None, {(0, 1): FIG_TEXT_STYLE, (0, 2): FIG_COLOR_STYLE}, "DISPLAY_P3")


@pytest.mark.usefixtures("style_overrides")
class TestInheritStyle:
    def test_apply_fill_override(self):
        style = base.process_styles({**FIG_TEXT, "inheritFillStyleID": (0, 2)})
        assert style.fills[0].color == SKETCH_COLOR[1]

    def test_apply_border_override(self):
        style = base.process_styles({**FIG_TEXT, "inheritFillStyleIDForStroke": (0, 2)})
        assert style.borders[0].color == SKETCH_COLOR[1]

    def test_apply_text_override(self):
        fig = {**FIG_TEXT, "inheritTextStyleID": (0, 1)}

        # Fig will be modified in place with text styles, to be processed by text
        base.process_styles(fig)

        assert fig["fontName"] == FIG_TEXT_STYLE["fontName"]
        assert fig["fontSize"] == 12
