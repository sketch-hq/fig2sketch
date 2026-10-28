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
        assert swatches[LIGHT].name == "Theme/Schemes/Light/Surface"
        assert swatches[DARK].name == "Theme/Schemes/Dark/Surface"
        assert unlinked(swatches[LIGHT].value) == SKETCH_COLOR[0]
        assert unlinked(swatches[DARK].value) == SKETCH_COLOR[1]
        assert all(s.value.swatchID == s.do_objectID for s in swatches.values())

    def test_ungrouped_variable_has_mode_under_collection(self):
        fig_variable = {**FIG_SURFACE, "guid": (1, 9), "name": "Accent"}
        swatches = context.variable_swatches(fig_variable)

        assert [s.name for s in swatches.values()] == ["Theme/Light/Accent", "Theme/Dark/Accent"]

    def test_single_mode_leaves_out_mode_name(self):
        swatches = list(context.variable_swatches(FIG_BLUE).values())

        assert [s.name for s in swatches] == ["Palette/Blue"]
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

    def test_all_colour_variables_convert(self):
        fig_spacing = {
            **FIG_BLUE,
            "guid": (2, 3),
            "name": "Spacing",
            "variableResolvedType": "FLOAT",
            "variableDataValues": {"entries": []},
        }

        variable.convert_all([FIG_THEME, FIG_SURFACE, fig_spacing, FIG_BLUE, FIG_PRIMARY])

        assert context.sketch_components() == [
            *context.variable_swatches(FIG_SURFACE).values(),
            *context.variable_swatches(FIG_BLUE).values(),
            *context.variable_swatches(FIG_PRIMARY).values(),
        ]


class TestLinkedColor:
    def test_links_default_mode(self):
        paint = bound_paint(FIG_COLOR[0], 1, {"guid": (1, 3)})
        light = context.variable_swatches(FIG_SURFACE)[LIGHT]

        color = variable.linked_color(
            style.convert_color(FIG_COLOR[0]), paint, variable.ancestors(FIG_BASE)
        )

        assert color == light.value

    def test_default_mode_is_first_in_figma_order(self, monkeypatch):
        """The modes can be stored out of the order Figma shows them in, which is the
        order that picks the default and lists the swatches."""
        monkeypatch.setitem(
            FIG_THEME,
            "variableSetModes",
            [
                {"id": DARK, "name": "Dark", "sortPosition": '"'},
                {"id": LIGHT, "name": "Light", "sortPosition": "!"},
            ],
        )
        paint = bound_paint(FIG_COLOR[1], 1, {"guid": FIG_SURFACE["guid"]})
        swatches = context.variable_swatches(FIG_SURFACE)

        color = variable.linked_color(
            style.convert_color(FIG_COLOR[1]), paint, variable.ancestors(FIG_BASE)
        )

        assert list(swatches) == [LIGHT, DARK]
        assert color == swatches[LIGHT].value

    def test_links_mode_set_above_layer(self):
        paint = bound_paint(FIG_COLOR[1], 1, {"guid": (1, 3)})
        fig = {**FIG_BASE, "parent": {"guid": FIG_DARK_FRAME["guid"]}}
        dark = context.variable_swatches(FIG_SURFACE)[DARK]

        color = variable.linked_color(
            style.convert_color(FIG_COLOR[1]), paint, variable.ancestors(fig)
        )

        assert color == dark.value

    def test_mode_cleared_by_override_inherits_mode_above(self):
        """An instance override that clears a layer's mode leaves an entry with no mode,
        so the layer takes the mode set above it."""
        paint = bound_paint(FIG_COLOR[1], 1, {"guid": (1, 3)})
        fig = {
            **FIG_BASE,
            "parent": {"guid": FIG_DARK_FRAME["guid"]},
            "variableModeBySetMap": {"entries": [{"variableSetID": {"guid": (1, 0)}}]},
        }
        dark = context.variable_swatches(FIG_SURFACE)[DARK]

        color = variable.linked_color(
            style.convert_color(FIG_COLOR[1]), paint, variable.ancestors(fig)
        )

        assert color == dark.value

    def test_mode_cleared_by_override_falls_back_to_default(self):
        paint = bound_paint(FIG_COLOR[1], 1, {"guid": (1, 3)})
        fig = {
            **FIG_BASE,
            "variableModeBySetMap": {"entries": [{"variableSetID": {"guid": (1, 0)}}]},
        }
        light = context.variable_swatches(FIG_SURFACE)[LIGHT]

        color = variable.linked_color(
            style.convert_color(FIG_COLOR[1]), paint, variable.ancestors(fig)
        )

        assert color == light.value

    def test_ignores_stale_paint_color(self):
        """The colour on a paint is only a cache of the last one resolved, which can be
        another mode's, so the mode in effect for the layer picks the swatch."""
        paint = bound_paint(FIG_COLOR[1], 1, {"guid": (1, 3)})
        light = context.variable_swatches(FIG_SURFACE)[LIGHT]

        color = variable.linked_color(
            style.convert_color(FIG_COLOR[1]), paint, variable.ancestors(FIG_BASE)
        )

        assert color == light.value

    def test_links_library_variable_by_key(self):
        paint = bound_paint(FIG_COLOR[2], 1, {"assetRef": {"key": "blue-key", "version": "1:1"}})
        blue = context.variable_swatches(FIG_BLUE)[(2, 1)]

        color = variable.linked_color(
            style.convert_color(FIG_COLOR[2]), paint, variable.ancestors(FIG_BASE)
        )

        assert color == blue.value

    def test_paint_with_opacity_stays_unlinked(self):
        paint = bound_paint(FIG_COLOR[0], 0.5, {"guid": (1, 3)})
        color = style.convert_color(FIG_COLOR[0], 0.5)

        assert variable.linked_color(color, paint, variable.ancestors(FIG_BASE)) == color

    def test_unbound_paint_stays_unlinked(self):
        paint = {"type": "SOLID", "color": FIG_COLOR[0], "opacity": 1, "visible": True}
        color = style.convert_color(FIG_COLOR[0])

        assert variable.linked_color(color, paint, variable.ancestors(FIG_BASE)) == color
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

    def test_fill_style_bound_to_variable_links_variable(self):
        """A style whose colour is a variable's has no swatch of its own, so a layer
        using it links to the variable's swatch for the layer's mode."""
        fig_style = {
            **FIG_BASE,
            "type": "ROUNDED_RECTANGLE",
            "guid": (4, 0),
            "styleType": "FILL",
            "fillPaints": [bound_paint(FIG_COLOR[0], 1, {"guid": FIG_SURFACE["guid"]})],
        }
        context.add_fig_node(fig_style)
        fig = {
            **FIG_BASE,
            "parent": {"guid": FIG_DARK_FRAME["guid"]},
            "styleIdForFill": {"guid": fig_style["guid"]},
        }
        dark = context.variable_swatches(FIG_SURFACE)[DARK]

        st = base.process_styles(fig)

        assert st.fills[0].color == dark.value
        assert context.component(fig_style["guid"]) == (fig_style, None)

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
