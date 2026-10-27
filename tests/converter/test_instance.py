from .base import *
import copy
import pytest
from converter import tree
from converter import style as style_converter
from converter.config import config
from converter.context import context
from sketchformat.layer_group import Group, GroupBehavior, SymbolInstance, OverrideValue
from unittest.mock import ANY
from .test_variable import (
    DARK, FIG_BLUE, FIG_DARK_FRAME, FIG_PALETTE, FIG_SURFACE, FIG_THEME, LIGHT, bound_paint
)

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

FIG_FILL_STYLE = {
    **FIG_BASE,
    "type": "ROUNDED_RECTANGLE",
    "guid": (0, 5),
    "key": "red-fill",
    "styleType": "FILL",
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

FIG_BOUND_FILL_STYLE = {
    **FIG_BASE,
    "type": "ROUNDED_RECTANGLE",
    "guid": (0, 7),
    "key": "bound-fill",
    "styleType": "FILL",
    "fillPaints": [
        {
            "type": "SOLID",
            "color": FIG_COLOR[1],
            "opacity": 0.9,
            "visible": True,
            "colorVar": {
                "value": {"alias": {"assetRef": {"key": "color-variable", "version": "1:1"}}},
                "dataType": "ALIAS",
                "resolvedDataType": "COLOR",
            },
            "authoredColor": {"space": "DEFAULT", "c0": 0, "c1": 1, "c2": 0.5, "c3": 0.7},
        }
    ],
}

FIG_VECTOR = {
    **FIG_BASE,
    "type": "VECTOR",
    "guid": (0, 6),
    "overrideKey": (1, 10),
    "cornerRadius": 0,
    "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[0], "opacity": 0.9, "visible": True}],
    "vectorNetwork": {
        "regions": [
            {
                "loops": [[0, 1, 2]],
                "style": {
                    "fillPaints": [
                        {
                            "type": "SOLID",
                            "color": FIG_COLOR[0],
                            "opacity": 0.9,
                            "visible": True,
                        }
                    ]
                },
                "windingRule": "NONZERO",
            }
        ],
        "segments": [
            {
                "start": 0,
                "end": 1,
                "tangentStart": {"x": 0, "y": 0},
                "tangentEnd": {"x": 0, "y": 0},
            },
            {
                "start": 1,
                "end": 2,
                "tangentStart": {"x": 0, "y": 0},
                "tangentEnd": {"x": 0, "y": 0},
            },
            {
                "start": 2,
                "end": 0,
                "tangentStart": {"x": 0, "y": 0},
                "tangentEnd": {"x": 0, "y": 0},
            },
        ],
        "vertices": [{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 0, "y": 10}],
    },
}

FIG_SPLIT_VECTOR = {
    **FIG_VECTOR,
    "guid": (0, 8),
    "overrideKey": (1, 11),
    "vectorNetwork": {
        **FIG_VECTOR["vectorNetwork"],
        "regions": [
            *FIG_VECTOR["vectorNetwork"]["regions"],
            {"loops": [[0, 1, 2]], "style": {}, "windingRule": "NONZERO"},
        ],
    },
}

FIG_CANVAS = {**FIG_BASE, "type": "CANVAS", "guid": (0, 0)}

FIG_SYMBOL = {
    **FIG_BASE,
    "type": "SYMBOL",
    "guid": (0, 3),
    "children": [FIG_TEXT, FIG_RECT, FIG_VECTOR],
    "parent": {"guid": FIG_CANVAS["guid"]},
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
        {
            (0, 0): FIG_CANVAS,
            (0, 3): FIG_SYMBOL,
            (0, 1): FIG_TEXT,
            (0, 2): FIG_RECT,
            (0, 5): FIG_FILL_STYLE,
            (0, 6): FIG_VECTOR,
            (0, 7): FIG_BOUND_FILL_STYLE,
            (1, 9): FIG_TEXT,
            (1, 10): FIG_VECTOR,
            (1, 11): FIG_SPLIT_VECTOR,
        },
        "DISPLAY_P3",
    )
    context._component_symbols = {(0, 3): False}


def init_with_variables(*fig_nodes: dict) -> None:
    """Sets up the symbol fixture's nodes, along with colour variables and any others."""
    context.init(
        None,
        {
            (0, 0): FIG_CANVAS,
            (0, 3): FIG_SYMBOL,
            (0, 1): FIG_TEXT,
            (0, 2): FIG_RECT,
            (0, 5): FIG_FILL_STYLE,
            (0, 6): FIG_VECTOR,
            (1, 9): FIG_TEXT,
            (1, 10): FIG_VECTOR,
            **{
                node["guid"]: node
                for node in [FIG_THEME, FIG_SURFACE, FIG_PALETTE, FIG_BLUE, *fig_nodes]
            },
        },
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
        fig["symbolData"]["uniformScaleFactor"] = 0.5

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.frame.width == 50
        assert i.frame.height == 50
        assert i.scale == 0.5

    def test_scaled_and_resized_instance(self):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["size"] = {"x": 80, "y": 30}
        fig["symbolData"]["uniformScaleFactor"] = 0.5

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.frame.width == 80
        assert i.frame.height == 30
        assert i.scale == 0.5

    def test_resized_instance_is_not_scaled(self):
        # Even a proportional resize only changes the size the master is laid out at
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["size"] = {"x": 50, "y": 50}

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.frame.width == 50
        assert i.frame.height == 50
        assert i.scale == 1

    def test_stretched_instance_is_not_scaled(self):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["size"] = {"x": 300, "y": 120}

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.frame.width == 300
        assert i.frame.height == 120
        assert i.scale == 1

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

    def test_instance_of_translucent_master(self, monkeypatch, warnings):
        monkeypatch.setitem(FIG_SYMBOL, "opacity", 0.5)
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["opacity"] = 0.5

        i = tree.convert_node(fig, "")

        # Sketch already draws the instance with the master's opacity
        assert isinstance(i, SymbolInstance)
        assert i.style.contextSettings.opacity == 1
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_instance_more_transparent_than_master(self, monkeypatch):
        monkeypatch.setitem(FIG_SYMBOL, "opacity", 0.5)
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["opacity"] = 0.25

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.style.contextSettings.opacity == 0.5

    def test_instance_more_opaque_than_master_detaches(self, monkeypatch, warnings):
        monkeypatch.setitem(FIG_SYMBOL, "opacity", 0.5)
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["opacity"] = 1
        context.add_fig_node(fig)

        i = tree.convert_node(fig, "")

        assert isinstance(i, Group)
        warnings.assert_any_call("SYM003", ANY, props=["opacity"], layers={"opacity": ["thing"]})

    def test_root_fill_override_matching_master_preserves_instance(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 3)]},
                "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[1], "visible": True}],
            }
        ]

        i = tree.convert_node(fig, "")

        # The instance node still has the master's paints, which is what gets drawn
        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == []
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_root_fill_override_restyling_instance_detaches(self, warnings):
        paints = [{"type": "SOLID", "color": FIG_COLOR[1], "opacity": 1, "visible": True}]
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["fillPaints"] = paints
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(0, 3)]}, "fillPaints": paints}
        ]
        context.add_fig_node(fig)

        i = tree.convert_node(fig, "")

        assert isinstance(i, Group)
        warnings.assert_any_call(
            "SYM003", ANY, props=["fillPaints"], layers={"fillPaints": ["thing"]}
        )

    def test_root_stack_positioning_override_preserves_instance(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(0, 3)]}, "stackPositioning": "ABSOLUTE"}
        ]

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.flexItem.ignoreLayout is True
        assert i.overrideValues == []
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_text_metadata_overrides_preserve_instance(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "textExplicitLayoutVersion": 1,
                "hyperlink": {"url": "https://example.com", "openInNewTab": True},
            }
        ]

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == []
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_nested_opacity_override_detaches(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [{"guidPath": {"guids": [(1, 9)]}, "opacity": 0.7}]
        context.add_fig_node(fig)

        i = tree.convert_node(fig, "")

        assert isinstance(i, Group)
        warnings.assert_any_call(
            "SYM003", ANY, props=["opacity"], layers={"opacity": ["thing/thing"]}
        )

    def test_detach_warning_lists_each_prop_once_with_its_layers(self, monkeypatch, warnings):
        monkeypatch.setitem(FIG_TEXT, "name", "Label")
        monkeypatch.setitem(FIG_RECT, "name", "Box")
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["name"] = "Card"
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(1, 9)]}, "fontSize": 16},
            {"guidPath": {"guids": [(0, 2)]}, "fontSize": 16, "visible": False},
        ]

        i = tree.convert_node(fig, "")

        assert isinstance(i, Group)
        warnings.assert_any_call(
            "SYM003",
            ANY,
            props=["fontSize", "visible"],
            layers={"fontSize": ["Card/Label", "Card/Box"], "visible": ["Card/Box"]},
        )

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
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_fill_override_folds_opacity_into_color(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[1],
                        "opacity": 1,
                        "blendMode": "NORMAL",
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
            OverrideValue(
                overrideName=f"{symbol_text_id}_color:fill-0",
                value=Color(red=0, green=1, blue=0.5, alpha=1),
            ),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_fill_override_omits_values_matching_master(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[1],
                        "opacity": 0.9,
                        "blendMode": "NORMAL",
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
            OverrideValue(
                overrideName=f"{symbol_text_id}_color:fill-0",
                value=Color(red=0, green=1, blue=0.5, alpha=0.9),
            )
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_fill_override_keeps_translucent_opacity_of_new_color(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "fillPaints": [
                    {"type": "SOLID", "color": FIG_COLOR[2], "opacity": 0.9, "visible": True}
                ],
            }
        ]

        i = tree.convert_node(fig, "")
        symbol_text_id = context.symbols_page.layers[0].layers[0].do_objectID

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(
                overrideName=f"{symbol_text_id}_color:fill-0",
                value=Color(red=0, green=0, blue=1, alpha=0.9),
            )
        ]

    def test_fill_override_of_opacity_only_overrides_color(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "fillPaints": [
                    {"type": "SOLID", "color": FIG_COLOR[0], "opacity": 0.5, "visible": True}
                ],
            }
        ]

        i = tree.convert_node(fig, "")
        symbol_text_id = context.symbols_page.layers[0].layers[0].do_objectID

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(
                overrideName=f"{symbol_text_id}_color:fill-0",
                value=Color(red=1, green=0, blue=0.5, alpha=0.5),
            )
        ]

    def test_fill_override_emits_normal_blend_when_master_differs(self, warnings):
        text = copy.deepcopy(FIG_TEXT)
        text["fillPaints"][0]["blendMode"] = "MULTIPLY"
        symbol = {**copy.deepcopy(FIG_SYMBOL), "children": [text, FIG_RECT, FIG_VECTOR]}
        context.init(
            None,
            {
                (0, 0): FIG_CANVAS,
                (0, 3): symbol,
                (0, 1): text,
                (0, 2): FIG_RECT,
                (0, 5): FIG_FILL_STYLE,
                (0, 6): FIG_VECTOR,
                (1, 9): text,
                (1, 10): FIG_VECTOR,
            },
            "DISPLAY_P3",
        )
        context._component_symbols = {(0, 3): False}

        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[0],
                        "opacity": 0.9,
                        "blendMode": "NORMAL",
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
            OverrideValue(
                overrideName=f"{symbol_text_id}_blendMode:fill-0", value=BlendMode.NORMAL
            )
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
            OverrideValue(
                overrideName=f"{symbol_rect_id}_color:border-0",
                value=Color(red=0, green=1, blue=0.5, alpha=0.5),
            ),
            OverrideValue(
                overrideName=f"{symbol_rect_id}_blendMode:border-0", value=BlendMode.SCREEN
            ),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_gradient_border_override(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 2)]},
                "strokePaints": [
                    {
                        "type": "GRADIENT_LINEAR",
                        "transform": Matrix([[1, 0, 0], [0, 1, 0]]),
                        "stops": [
                            {"color": FIG_COLOR[0], "position": 0},
                            {"color": FIG_COLOR[1], "position": 1},
                        ],
                        "opacity": 0.38,
                        "blendMode": "NORMAL",
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
            OverrideValue(
                overrideName=f"{symbol_rect_id}_color:border-0",
                value=style_converter.convert_gradient(
                    FIG_RECT, fig["symbolData"]["symbolOverrides"][0]["strokePaints"][0]
                ),
            ),
            OverrideValue(overrideName=f"{symbol_rect_id}_opacity:border-0", value=0.38),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_matching_gradient_border_override_is_omitted(self, warnings):
        rect = copy.deepcopy(FIG_RECT)
        rect["strokePaints"] = [
            {
                "type": "GRADIENT_LINEAR",
                "transform": Matrix([[1, 0, 0], [0, 1, 0]]),
                "stops": [
                    {"color": FIG_COLOR[0], "position": 0},
                    {"color": FIG_COLOR[1], "position": 1},
                ],
                "opacity": 0.38,
                "blendMode": "NORMAL",
                "visible": True,
            }
        ]
        symbol = {**copy.deepcopy(FIG_SYMBOL), "children": [FIG_TEXT, rect, FIG_VECTOR]}
        context.init(
            None,
            {
                (0, 0): FIG_CANVAS,
                (0, 3): symbol,
                (0, 1): FIG_TEXT,
                (0, 2): rect,
                (0, 5): FIG_FILL_STYLE,
                (0, 6): FIG_VECTOR,
                (1, 9): FIG_TEXT,
                (1, 10): FIG_VECTOR,
            },
            "DISPLAY_P3",
        )
        context._component_symbols = {(0, 3): False}

        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(0, 2)]}, "strokePaints": copy.deepcopy(rect["strokePaints"])}
        ]

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == []
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_gradient_border_opacity_override_without_gradient_fields(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 2)]},
                "strokePaints": [
                    {
                        "type": "GRADIENT_LINEAR",
                        "opacity": 0.38,
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
            OverrideValue(overrideName=f"{symbol_rect_id}_opacity:border-0", value=0.38),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_shadow_override(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 2)]},
                "effects": [
                    {
                        "type": "DROP_SHADOW",
                        "offset": {"x": 3, "y": 6},
                        "radius": 5,
                        "spread": 2,
                        "color": FIG_COLOR[1],
                        "visible": True,
                        "blendMode": "NORMAL",
                    },
                    {
                        "type": "INNER_SHADOW",
                        "offset": {"x": 1, "y": 2},
                        "radius": 3,
                        "spread": 4,
                        "color": FIG_COLOR[2],
                        "visible": True,
                        "blendMode": "NORMAL",
                    },
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
            OverrideValue(overrideName=f"{symbol_rect_id}_color:shadow-0", value=SKETCH_COLOR[1]),
            OverrideValue(
                overrideName=f"{symbol_rect_id}_color:innershadow-0", value=SKETCH_COLOR[2]
            ),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_fill_style_override(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "styleIdForFill": {"assetRef": {"key": "red-fill", "version": "1:1"}},
            }
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]
        symbol_text_id = symbol.layers[0].do_objectID
        _, red_fill = context.component(FIG_FILL_STYLE["guid"])

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_text_id}_color:fill-0", value=red_fill.value),
            OverrideValue(
                overrideName=f"{symbol_text_id}_blendMode:fill-0", value=BlendMode.MULTIPLY
            ),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_variable_bound_fill_style_override(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "styleIdForFill": {"assetRef": {"key": "bound-fill", "version": "1:1"}},
            }
        ]

        i = tree.convert_node(fig, "")
        symbol_text_id = context.symbols_page.layers[0].layers[0].do_objectID
        _, bound_fill = context.component(FIG_BOUND_FILL_STYLE["guid"])

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_text_id}_color:fill-0", value=bound_fill.value),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_stroke_style_override(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 2)]},
                "styleIdForStrokeFill": {"assetRef": {"key": "red-fill", "version": "1:1"}},
            }
        ]

        i = tree.convert_node(fig, "")
        symbol_rect_id = context.symbols_page.layers[0].layers[1].do_objectID
        _, red_fill = context.component(FIG_FILL_STYLE["guid"])

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_rect_id}_color:border-0", value=red_fill.value),
            OverrideValue(
                overrideName=f"{symbol_rect_id}_blendMode:border-0", value=BlendMode.MULTIPLY
            ),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_vector_fill_style_override_uses_shape_path_id(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 10)]},
                "styleIdForFill": {"assetRef": {"key": "red-fill", "version": "1:1"}},
            }
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]
        symbol_vector_id = symbol.layers[2].do_objectID

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues[0] == OverrideValue(
            overrideName=f"{symbol_vector_id}_color:fill-0",
            value=context.component(FIG_FILL_STYLE["guid"])[1].value,
        )
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_fill_override_on_vector_with_regions_detaches(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 11)]},
                "fillPaints": [
                    {"type": "SOLID", "color": FIG_COLOR[1], "opacity": 0.9, "visible": True}
                ],
            }
        ]
        context.add_fig_node(fig)

        i = tree.convert_node(fig, "")

        assert isinstance(i, Group)
        warnings.assert_any_call(
            "SYM003",
            ANY,
            props=["fillPaints.regions"],
            layers={"fillPaints.regions": ["thing/thing"]},
        )

    def test_unchanged_fill_override_on_vector_with_regions(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(1, 11)]}, "fillPaints": FIG_SPLIT_VECTOR["fillPaints"]}
        ]

        i = tree.convert_node(fig, "")

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == []
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_stroke_style_override_by_guid(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(0, 2)]}, "styleIdForStrokeFill": {"guid": (0, 5)}}
        ]

        i = tree.convert_node(fig, "")
        assert len(context.symbols_page.layers) == 1
        symbol = context.symbols_page.layers[0]
        symbol_rect_id = symbol.layers[1].do_objectID
        _, red_fill = context.component(FIG_FILL_STYLE["guid"])

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_rect_id}_color:border-0", value=red_fill.value),
            OverrideValue(
                overrideName=f"{symbol_rect_id}_blendMode:border-0", value=BlendMode.MULTIPLY
            ),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_style_override_links_style_swatch_over_variable(self, warnings):
        """The style's paint is bound to a variable and carries the colour as authored,
        but the override links to the style's own swatch, as a layer using it would."""
        fig_style = {
            **FIG_BASE,
            "type": "ROUNDED_RECTANGLE",
            "guid": (0, 7),
            "styleType": "FILL",
            "fillPaints": [
                {
                    **bound_paint(FIG_COLOR[2], 1, {"guid": FIG_BLUE["guid"]}),
                    "authoredColor": {"space": "DEFAULT", "c0": 0, "c1": 0, "c2": 1, "c3": 1},
                }
            ],
        }
        init_with_variables(fig_style)

        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [(0, 2)]}, "styleIdForStrokeFill": {"guid": (0, 7)}}
        ]

        i = tree.convert_node(fig, "")
        symbol = context.symbols_page.layers[0]
        symbol_rect_id = symbol.layers[1].do_objectID
        _, style_swatch = context.component((0, 7))

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(
                overrideName=f"{symbol_rect_id}_color:border-0", value=style_swatch.value
            ),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_paint_override_bound_to_variable(self, warnings):
        """The paint holds a cached colour from the Dark mode, but nothing sets a mode,
        so the override links to the default Light mode's swatch."""
        init_with_variables()

        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 2)]},
                "strokePaints": [bound_paint(FIG_COLOR[1], 1, {"guid": FIG_SURFACE["guid"]})],
            }
        ]

        i = tree.convert_node(fig, "")
        symbol = context.symbols_page.layers[0]
        symbol_rect_id = symbol.layers[1].do_objectID
        light = context.variable_swatches(FIG_SURFACE)[LIGHT]

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_rect_id}_color:border-0", value=light.value),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_paint_override_bound_to_variable_in_instance_mode(self, warnings):
        """The instance sits in a Dark frame, so the override resolves the variable in
        the Dark mode, whatever mode the master is in."""
        init_with_variables(FIG_DARK_FRAME)

        fig = copy.deepcopy(FIG_INSTANCE)
        fig["parent"] = {"guid": FIG_DARK_FRAME["guid"]}
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 2)]},
                "strokePaints": [bound_paint(FIG_COLOR[1], 1, {"guid": FIG_SURFACE["guid"]})],
            }
        ]

        i = tree.convert_node(fig, "")
        symbol_rect_id = context.symbols_page.layers[0].layers[1].do_objectID
        dark = context.variable_swatches(FIG_SURFACE)[DARK]

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_rect_id}_color:border-0", value=dark.value),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_paint_override_bound_to_variable_in_mode_set_on_instance(self, warnings):
        init_with_variables()

        fig = copy.deepcopy(FIG_INSTANCE)
        fig["variableModeBySetMap"] = FIG_DARK_FRAME["variableModeBySetMap"]
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 2)]},
                "strokePaints": [bound_paint(FIG_COLOR[1], 1, {"guid": FIG_SURFACE["guid"]})],
            }
        ]

        i = tree.convert_node(fig, "")
        symbol_rect_id = context.symbols_page.layers[0].layers[1].do_objectID
        dark = context.variable_swatches(FIG_SURFACE)[DARK]

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_rect_id}_color:border-0", value=dark.value),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_paint_override_bound_to_variable_in_mode_set_within_master(self, warnings):
        """A mode set on a layer within the master applies to the layers inside it, even
        in an instance that sits in another mode."""
        light_frame = {
            **FIG_DARK_FRAME,
            "guid": (3, 1),
            "parent": {"guid": FIG_SYMBOL["guid"]},
            "variableModeBySetMap": {
                "entries": [
                    {"variableSetID": {"guid": FIG_THEME["guid"]}, "variableModeID": LIGHT}
                ],
            },
        }
        rect = {**FIG_RECT, "parent": {"guid": light_frame["guid"]}}
        init_with_variables(FIG_DARK_FRAME, light_frame, rect)

        fig = copy.deepcopy(FIG_INSTANCE)
        fig["parent"] = {"guid": FIG_DARK_FRAME["guid"]}
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 2)]},
                "strokePaints": [bound_paint(FIG_COLOR[1], 1, {"guid": FIG_SURFACE["guid"]})],
            }
        ]

        i = tree.convert_node(fig, "")
        symbol_rect_id = context.symbols_page.layers[0].layers[1].do_objectID
        light = context.variable_swatches(FIG_SURFACE)[LIGHT]

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_rect_id}_color:border-0", value=light.value),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_style_ref_replaces_override_paints(self, warnings):
        """An override applying a style carries a copy of its paints too, which can be
        out of date, so only the style converts."""
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "styleIdForFill": {"guid": FIG_FILL_STYLE["guid"]},
                "fillPaints": [
                    {"type": "SOLID", "color": FIG_COLOR[2], "opacity": 1, "visible": True}
                ],
            }
        ]

        i = tree.convert_node(fig, "")
        symbol = context.symbols_page.layers[0]
        symbol_text_id = symbol.layers[0].do_objectID
        _, red_fill = context.component(FIG_FILL_STYLE["guid"])

        assert isinstance(i, SymbolInstance)
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_text_id}_color:fill-0", value=red_fill.value),
            OverrideValue(
                overrideName=f"{symbol_text_id}_blendMode:fill-0", value=BlendMode.MULTIPLY
            ),
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_detached_fill_style_override_with_paints(self, warnings):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 10)]},
                "styleIdForFill": {"guid": [(2**32) - 1, (2**32) - 1]},
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
        symbol_vector_id = symbol.layers[2].do_objectID

        assert isinstance(i, SymbolInstance)
        assert i.symbolID == symbol.symbolID
        assert i.overrideValues == [
            OverrideValue(overrideName=f"{symbol_vector_id}_color:fill-0", value=SKETCH_COLOR[1]),
            OverrideValue(
                overrideName=f"{symbol_vector_id}_blendMode:fill-0", value=BlendMode.MULTIPLY
            ),
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

        warnings.assert_any_call(
            "SYM002", ANY, props=["fontSize"], layers={"fontSize": ["thing/thing"]}
        )

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
        context.add_fig_node(fig)

        i = tree.convert_node(fig, "")
        assert isinstance(i, Group)

    def test_nested_instance_keeps_scale_of_detached_instance(self, monkeypatch):
        rect = {**FIG_RECT, "guid": (0, 22)}
        nested = copy.deepcopy(FIG_INSTANCE)
        nested["guid"] = (0, 21)
        nested["symbolData"]["uniformScaleFactor"] = 0.5
        outer_symbol = {**FIG_SYMBOL, "guid": (0, 20), "children": [rect, nested]}
        monkeypatch.setitem(context._node_by_id, (0, 20), outer_symbol)
        monkeypatch.setitem(context._node_by_id, (0, 22), rect)
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolID"] = (0, 20)
        fig["symbolData"]["uniformScaleFactor"] = 3
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(0, 22)]},
                "opacity": 0.5,
            }
        ]
        context.add_fig_node(fig)

        i = tree.convert_node(fig, "")

        assert isinstance(i, Group)
        assert isinstance(i.layers[1], SymbolInstance)
        assert i.layers[1].scale == 1.5

    def test_detached_layers_resolve_variables_in_instance_mode(self, warnings):
        """The copies of the master's layers sit in the instance, so they resolve
        variables in the modes where the instance is."""
        rect = {
            **FIG_RECT,
            "guid": (0, 22),
            "strokePaints": [bound_paint(FIG_COLOR[0], 1, {"guid": FIG_SURFACE["guid"]})],
        }
        master = {**FIG_SYMBOL, "guid": (0, 20), "children": [rect]}
        init_with_variables(FIG_DARK_FRAME, master, rect)

        fig = copy.deepcopy(FIG_INSTANCE)
        fig["parent"] = {"guid": FIG_DARK_FRAME["guid"]}
        fig["symbolData"]["symbolID"] = master["guid"]
        fig["symbolData"]["symbolOverrides"] = [
            {"guidPath": {"guids": [rect["guid"]]}, "opacity": 0.5}
        ]
        context.add_fig_node(fig)

        i = tree.convert_node(fig, "")
        dark = context.variable_swatches(FIG_SURFACE)[DARK]

        assert isinstance(i, Group)
        assert i.layers[0].style.borders[0].color == dark.value
        warnings.assert_any_call("SYM003", ANY, props=["opacity"])

    def test_convert_to_artboard(self):
        fig = copy.deepcopy(FIG_INSTANCE)
        fig["symbolData"]["symbolOverrides"] = [
            {
                "guidPath": {"guids": [(1, 9)]},
                "opacity": 0.5,
            }
        ]
        fig["resizeToFit"] = False
        context.add_fig_node(fig)

        i = tree.convert_node(fig, "CANVAS")
        assert isinstance(i, Group)
        assert i.groupBehavior == GroupBehavior.FRAME
