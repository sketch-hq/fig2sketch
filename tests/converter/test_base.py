import pytest
from .base import *
from converter import prototype, tree, base
from converter import utils
from sketchformat.layer_common import PrototypeScrolling
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

    def test_fixed_scroll_behavior_uses_sketch_viewport_flag(self):
        layer = base.base_layer(
            {**FIG_BASE, "scrollBehavior": "FIXED_WHEN_CHILD_OF_SCROLLING_FRAME"}
        )

        assert layer["isFixedToViewport"] is True
        assert "scrollBehavior" not in layer

    @pytest.mark.parametrize(
        ("fig_direction", "sketch_direction"),
        [
            ("HORIZONTAL", PrototypeScrolling.HORIZONTAL),
            ("VERTICAL", PrototypeScrolling.VERTICAL),
            ("BOTH", PrototypeScrolling.BOTH),
            ("HORIZONTAL_AND_VERTICAL", PrototypeScrolling.BOTH),
        ],
    )
    def test_scroll_direction_uses_sketch_prototype_scrolling_bitmask(
        self, fig_direction, sketch_direction
    ):
        layer = base.base_layer({**FIG_BASE, "scrollDirection": fig_direction})

        assert layer["prototypeScrolling"] == sketch_direction

    def test_unknown_scroll_direction_warns(self, warnings):
        base.base_layer({**FIG_BASE, "scrollDirection": "DIAGONAL"})

        warnings.assert_called_once_with("PRT005", ANY, props=["DIAGONAL"])


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
