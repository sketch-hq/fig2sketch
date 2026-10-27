import dataclasses
import pytest
from .base import *
from converter import base, style, text, variable
from converter.context import context

FIG_THEME = {
    "type": "VARIABLE_SET",
    "guid": (1, 0),
    "name": "Theme",
    "variableSetModes": [
        {"id": (1, 1), "name": "Light"},
        {"id": (1, 2), "name": "Dark"},
    ],
}

FIG_PALETTE = {
    "type": "VARIABLE_SET",
    "guid": (2, 0),
    "name": "Palette",
    "key": "palette-key",
    "variableSetModes": [{"id": (2, 1), "name": "Mode 1"}],
}


def color_value(color: dict) -> dict:
    return {"value": {"colorValue": color}, "dataType": "COLOR"}


def alias_value(guid) -> dict:
    return {"value": {"alias": {"guid": guid}}, "dataType": "ALIAS"}


FIG_BLUE = {
    "type": "VARIABLE",
    "guid": (2, 2),
    "name": "Blue",
    "key": "blue-key",
    "variableSetID": {"assetRef": {"key": "palette-key", "version": "1:1"}},
    "variableResolvedType": "COLOR",
    "variableDataValues": {
        "entries": [{"modeID": (2, 1), "variableData": color_value(FIG_COLOR[2])}],
    },
}

FIG_SURFACE = {
    "type": "VARIABLE",
    "guid": (1, 3),
    "name": "Schemes/Surface",
    "variableSetID": {"guid": (1, 0)},
    "variableResolvedType": "COLOR",
    "variableDataValues": {
        "entries": [
            {"modeID": (1, 1), "variableData": color_value(FIG_COLOR[0])},
            {"modeID": (1, 2), "variableData": color_value(FIG_COLOR[1])},
        ],
    },
}

FIG_PRIMARY = {
    "type": "VARIABLE",
    "guid": (1, 4),
    "name": "Schemes/Primary",
    "variableSetID": {"guid": (1, 0)},
    "variableResolvedType": "COLOR",
    "variableDataValues": {
        "entries": [
            {"modeID": (1, 1), "variableData": alias_value((2, 2))},
            {"modeID": (1, 2), "variableData": alias_value((1, 3))},
        ],
    },
}

FIG_DARK_FRAME = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (3, 0),
    "variableModeBySetMap": {
        "entries": [{"variableSetID": {"guid": (1, 0)}, "variableModeID": (1, 2)}],
    },
}

LIGHT = (1, 1)
DARK = (1, 2)


def bound_paint(color: dict, opacity: float, alias: dict) -> dict:
    return {
        "type": "SOLID",
        "color": color,
        "opacity": opacity,
        "visible": True,
        "colorVar": {"value": {"alias": alias}, "dataType": "ALIAS", "resolvedDataType": "COLOR"},
    }


@pytest.fixture(autouse=True)
def variables():
    context.init(
        None,
        {
            node["guid"]: node
            for node in [
                FIG_THEME,
                FIG_PALETTE,
                FIG_BLUE,
                FIG_SURFACE,
                FIG_PRIMARY,
                FIG_DARK_FRAME,
            ]
        },
        "DISPLAY_P3",
    )


def unlinked(color: Color) -> Color:
    return dataclasses.replace(color, swatchID=None)


class TestSwatches:
    def test_swatch_per_mode(self):
        swatches = context.variable_swatches(FIG_SURFACE)

        assert list(swatches) == [LIGHT, DARK]
        assert swatches[LIGHT].name == "Light/Schemes/Surface"
        assert swatches[DARK].name == "Dark/Schemes/Surface"
        assert unlinked(swatches[LIGHT].value) == SKETCH_COLOR[0]
        assert unlinked(swatches[DARK].value) == SKETCH_COLOR[1]
        assert all(s.value.swatchID == s.do_objectID for s in swatches.values())

    def test_single_mode_keeps_variable_name(self):
        swatches = list(context.variable_swatches(FIG_BLUE).values())

        assert [s.name for s in swatches] == ["Blue"]
        assert unlinked(swatches[0].value) == SKETCH_COLOR[2]

    def test_aliases_resolve_per_collection(self):
        """Light aliases into another collection, which resolves in that collection's
        default mode. Dark aliases within the collection, which keeps the mode."""
        swatches = context.variable_swatches(FIG_PRIMARY)

        assert unlinked(swatches[LIGHT].value) == SKETCH_COLOR[2]
        assert unlinked(swatches[DARK].value) == SKETCH_COLOR[1]

    def test_swatches_are_added_to_document(self):
        surface = list(context.variable_swatches(FIG_SURFACE).values())
        blue = list(context.variable_swatches(FIG_BLUE).values())

        assert context.sketch_components() == surface + blue


class TestLinkedColor:
    def test_links_default_mode(self):
        paint = bound_paint(FIG_COLOR[0], 1, {"guid": (1, 3)})
        light = context.variable_swatches(FIG_SURFACE)[LIGHT]

        color = variable.linked_color(style.convert_color(FIG_COLOR[0]), paint, FIG_BASE)

        assert color == light.value

    def test_links_mode_set_above_layer(self):
        paint = bound_paint(FIG_COLOR[1], 1, {"guid": (1, 3)})
        fig = {**FIG_BASE, "parent": {"guid": FIG_DARK_FRAME["guid"]}}
        dark = context.variable_swatches(FIG_SURFACE)[DARK]

        color = variable.linked_color(style.convert_color(FIG_COLOR[1]), paint, fig)

        assert color == dark.value

    def test_ignores_stale_paint_color(self):
        """The colour on a paint is only a cache of the last one resolved, which can be
        another mode's, so the mode in effect for the layer picks the swatch."""
        paint = bound_paint(FIG_COLOR[1], 1, {"guid": (1, 3)})
        light = context.variable_swatches(FIG_SURFACE)[LIGHT]

        color = variable.linked_color(style.convert_color(FIG_COLOR[1]), paint, FIG_BASE)

        assert color == light.value

    def test_links_library_variable_by_key(self):
        paint = bound_paint(FIG_COLOR[2], 1, {"assetRef": {"key": "blue-key", "version": "1:1"}})
        blue = context.variable_swatches(FIG_BLUE)[(2, 1)]

        color = variable.linked_color(style.convert_color(FIG_COLOR[2]), paint, FIG_BASE)

        assert color == blue.value

    def test_paint_with_opacity_stays_unlinked(self):
        paint = bound_paint(FIG_COLOR[0], 0.5, {"guid": (1, 3)})
        color = style.convert_color(FIG_COLOR[0], 0.5)

        assert variable.linked_color(color, paint, FIG_BASE) == color

    def test_unbound_paint_stays_unlinked(self):
        paint = {"type": "SOLID", "color": FIG_COLOR[0], "opacity": 1, "visible": True}
        color = style.convert_color(FIG_COLOR[0])

        assert variable.linked_color(color, paint, FIG_BASE) == color
        assert context.sketch_components() == []


class TestStyles:
    def test_fill_and_border_link_to_swatches(self):
        fig = {
            **FIG_BASE,
            "fillPaints": [bound_paint(FIG_COLOR[0], 1, {"guid": (1, 3)})],
            "strokePaints": [bound_paint(FIG_COLOR[0], 1, {"guid": (1, 3)})],
            "strokeWeight": 1,
        }
        light = context.variable_swatches(FIG_SURFACE)[LIGHT]

        st = base.process_styles(fig)

        assert st.fills[0].color == light.value
        assert st.borders[0].color == light.value

    def test_fill_with_own_opacity_stays_unlinked(self):
        fig = {**FIG_BASE, "fillPaints": [bound_paint(FIG_COLOR[0], 0.5, {"guid": (1, 3)})]}

        st = base.process_styles(fig)

        assert st.fills[0].color == Color(red=1, green=0, blue=0.5, alpha=0.5)

    def test_text_color_links_to_swatch(self, monkeypatch):
        monkeypatch.setattr(context, "record_font", lambda _: "Roboto-Normal")
        fig = {
            **FIG_BASE,
            "type": "TEXT",
            "parent": {"guid": FIG_DARK_FRAME["guid"]},
            "fontName": {"family": "Roboto", "style": "Normal"},
            "fontSize": 12,
            "fillPaints": [bound_paint(FIG_COLOR[1], 1, {"guid": (1, 3)})],
        }
        dark = context.variable_swatches(FIG_SURFACE)[DARK]

        text_style = text.text_style(fig)

        assert text_style.encodedAttributes.MSAttributedStringColorAttribute == dark.value
