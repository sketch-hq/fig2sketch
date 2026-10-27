import pytest
from .base import *
from converter import prototype, tree, base
from converter import utils
from sketchformat.layer_common import PrototypeScrolling, SizingBehaviour
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
    "guid": (0, 2),
    "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[1], "opacity": 0.7, "visible": True}],
}

FIG_TEXT_STYLE = {
    **FIG_BASE,
    "type": "TEXT",
    "fontName": {"family": "CustomFont", "style": "Normal"},
}

FIG_SWATCH_STYLE = {
    **FIG_BASE,
    "type": "ROUNDED_RECTANGLE",
    "guid": (0, 3),
    "key": "swatch-key",
    "styleType": "FILL",
    "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[2], "opacity": 1, "visible": True}],
}


FIG_VERTICAL_STACK = {**FIG_BASE, "type": "FRAME", "guid": (5, 5), "stackMode": "VERTICAL"}


@pytest.fixture
def vertical_stack():
    context.init(None, {(5, 5): FIG_VERTICAL_STACK}, "DISPLAY_P3")


@pytest.mark.usefixtures("vertical_stack")
class TestTextSizing:
    def stacked_text(self, text_auto_resize):
        return {
            **FIG_TEXT,
            "horizontalConstraint": "MIN",
            "verticalConstraint": "MIN",
            "parent": {"guid": (5, 5)},
            "textAutoResize": text_auto_resize,
        }

    def test_auto_width_text_fits_width(self):
        fig_text = self.stacked_text("WIDTH_AND_HEIGHT")

        assert base.horizontal_sizing_behaviour(fig_text) == SizingBehaviour.FIT

    def test_auto_height_text_fits_height_only(self):
        fig_text = self.stacked_text("HEIGHT")

        assert base.horizontal_sizing_behaviour(fig_text) == SizingBehaviour.FIXED
        assert base.vertical_sizing_behaviour(fig_text) == SizingBehaviour.FIT


@pytest.fixture
def style_overrides(monkeypatch):
    context.init(
        None,
        {(0, 1): FIG_TEXT_STYLE, (0, 2): FIG_COLOR_STYLE, (0, 3): FIG_SWATCH_STYLE},
        "DISPLAY_P3",
    )


@pytest.mark.usefixtures("style_overrides")
class TestInheritStyle:
    def test_apply_fill_override(self):
        style = base.process_styles({**FIG_TEXT, "inheritFillStyleID": (0, 2)})
        assert style.fills[0].color == SKETCH_COLOR[1]

    def test_apply_border_override(self):
        style = base.process_styles({**FIG_TEXT, "inheritFillStyleIDForStroke": (0, 2)})
        assert style.borders[0].color == SKETCH_COLOR[1]

    def test_apply_fill_style_ref(self):
        style = base.process_styles({**FIG_TEXT, "styleIdForFill": {"guid": (0, 2)}})
        assert style.fills[0].color == SKETCH_COLOR[1]

    def test_apply_border_style_ref(self):
        style = base.process_styles({**FIG_TEXT, "styleIdForStrokeFill": {"guid": (0, 2)}})
        assert style.borders[0].color == SKETCH_COLOR[1]

    def test_fill_style_ref_links_swatch(self):
        style_ref = {"assetRef": {"key": "swatch-key", "version": "1:1"}}

        style = base.process_styles({**FIG_TEXT, "styleIdForFill": style_ref})
        _, swatch = context.component((0, 3))

        assert style.fills[0].color == swatch.value

    def test_detached_style_ref_keeps_paints(self, warnings):
        style_ref = {"guid": (utils.UINT_MAX, utils.UINT_MAX)}

        style = base.process_styles({**FIG_TEXT, "styleIdForFill": style_ref})

        assert style.fills[0].color == Color(red=1, green=0, blue=0.5, alpha=1)
        warnings.assert_not_called()

    def test_missing_style_ref_warns(self, warnings):
        fig = {**FIG_TEXT, "styleIdForFill": {"guid": (9, 9)}}

        style = base.process_styles(fig)

        assert style.fills[0].color == Color(red=1, green=0, blue=0.5, alpha=1)
        warnings.assert_called_once_with("CMP001", fig)

    def test_apply_text_override(self):
        fig = {**FIG_TEXT, "inheritTextStyleID": (0, 1)}

        # Fig will be modified in place with text styles, to be processed by text
        base.process_styles(fig)

        assert fig["fontName"] == FIG_TEXT_STYLE["fontName"]
        assert fig["fontSize"] == 12
