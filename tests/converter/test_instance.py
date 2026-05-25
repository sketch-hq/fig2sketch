from .base import *
import copy
import pytest
from converter import tree
from converter.config import config
from converter.context import context
from sketchformat.layer_group import Group, SymbolInstance, OverrideValue, Frame
from unittest.mock import ANY

FIG_TEXT = {
    **FIG_BASE,
    "type": "TEXT",
    "fontName": {"family": "Roboto", "style": "Normal", "postscript": "Roboto-Normal"},
    "fontSize": 12,
    "textAlignVertical": "CENTER",
    "textAlignHorizontal": "CENTER",
    "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[0], "opacity": 0.9, "visible": True}],
    "textData": {"characters": "original"},
    "guid": (0, 1),
    "overrideKey": (1, 9),
    "componentPropRefs": [
        {
            "defID": (1, 0),
            "componentPropNodeField": "TEXT_DATA",
            "isDeleted": False,
        }
    ],
}

FIG_RECT = {
    **FIG_BASE,
    "type": "ROUNDED_RECTANGLE",
    "guid": (0, 2),
    "strokePaints": [{"type": "SOLID", "color": FIG_COLOR[0], "opacity": 0.9, "visible": True}],
    "strokeWeight": 1,
}

FIG_SYMBOL = {
    **FIG_BASE,
    "type": "SYMBOL",
    "guid": (0, 3),
    "children": [FIG_TEXT, FIG_RECT],
    "parent": {"guid": (0, 3)},
}

FIG_INSTANCE = {
    **FIG_BASE,
    "type": "INSTANCE",
    "guid": (0, 4),
    "symbolData": {"symbolID": (0, 3), "symbolOverrides": []},
    "derivedSymbolData": [],
    "resizeToFit": True,
}


@pytest.fixture
def symbol(monkeypatch):
    context.init(
        None,
        {(0, 3): FIG_SYMBOL, (0, 1): FIG_TEXT, (0, 2): FIG_RECT, (1, 9): FIG_TEXT},
        "DISPLAY_P3",
    )
    context._component_symbols = {(0, 3): False}


@pytest.fixture
def mock_fonts(monkeypatch):
    monkeypatch.setattr(context, "record_font", lambda _: "Roboto-Normal")


@pytest.fixture
def no_detach(monkeypatch):
    monkeypatch.setattr(config, "can_detach", False)


@pytest.mark.usefixtures("symbol", "mock_fonts")
class TestOverrides:
    def test_plain_instance(self):
        i = tree.convert_node(FIG_INSTANCE, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.scale == 1
        assert i.overrideValues == []

    def test_scaled_instance(self):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["size"] = {"x": 50, "y": 50}

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.frame.width == 50
        assert i.frame.height == 50
        assert i.scale == 0.5

    def test_text_override(self):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(1, 9)]}, "textData": {"characters": "modified"}}
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]
        symbol_text_id = symbol.layers[0].do_objectID

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_text_id}_stringValue", value="modified")
        ]

    def test_text_prop_assignment(self):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["componentPropAssignments"] = [
            {"defID": (1, 0), "value": {"textValue": {"characters": "modified"}}}
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]
        symbol_text_id = symbol.layers[0].do_objectID

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_text_id}_stringValue", value="modified")
        ]

    def test_root_opacity_override_preserves_instance(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(0, 3)]}, "opacity": 0.7, "targetAspectRatio": {}}
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.style.contextSettings.opacity == 0.7
        assert i.overrideValues == []
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_nested_opacity_override_detaches(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [{"guidPath": {"guids": [(1, 9)]}, "opacity": 0.7}]

        i = tree.convert_node(fig, "")

        assert isinstance(i, Group)
        warnings.assert_any_call("SYM003", ANY, props=["opacity"])

    def test_fill_override(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[1],
                        "opacity": 0.7,
                        "blendMode": "MULTIPLY",
                        "visible": True,
                    }
                ],
            }
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]
        symbol_text_id = symbol.layers[0].do_objectID

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_text_id}_color:fill-0", value=SKETCH_COLOR[1]),
            OverrideValue(
                overrideName=f"{symbol_text_id}_blendMode:fill-0", value=BlendMode.MULTIPLY
            ),
            OverrideValue(overrideName=f"{symbol_text_id}_opacity:fill-0", value=0.7),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_border_override(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 2)]},
                "strokePaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[1],
                        "opacity": 0.5,
                        "blendMode": "SCREEN",
                        "visible": True,
                    }
                ],
            }
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]
        symbol_rect_id = symbol.layers[1].do_objectID

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_rect_id}_color:border-0", value=SKETCH_COLOR[1]),
            OverrideValue(
                overrideName=f"{symbol_rect_id}_blendMode:border-0", value=BlendMode.SCREEN
            ),
            OverrideValue(overrideName=f"{symbol_rect_id}_opacity:border-0", value=0.5),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_color_override_ignored(self, no_detach, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 1)]},
                "fontSize": 16,
            }
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues == []

        warnings.assert_any_call("SYM002", ANY, props=["fontSize"])

    def test_prop_and_symbol_override(self):
        """When a property and an override are specified for the same thing, we want
        to keep the value of the property (it always takes priority over overrides)"""

        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(1, 9)]}, "textData": {"characters": "override"}}
        ]
        fig["componentPropAssignments"] = [
            {"defID": (1, 0), "value": {"textValue": {"characters": "property"}}}
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]
        symbol_text_id = symbol.layers[0].do_objectID

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_text_id}_stringValue", value="property")
        ]


@pytest.mark.usefixtures("symbol", "no_prototyping")
class TestDetach:
    def test_convert_to_group(self):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "opacity": 0.5,
            }
        ]
        fig["resizeToFit"] = True

        i = tree.convert_node(fig, "")
        assert isinstance(i, Group)

    def test_convert_to_artboard(self):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "opacity": 0.5,
            }
        ]
        fig["resizeToFit"] = False

        i = tree.convert_node(fig, "CANVAS")
        assert isinstance(i, Frame)
