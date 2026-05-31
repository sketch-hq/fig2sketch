from .base import *
import copy
import pytest
from converter import tree
from converter import style as style_converter
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

FIG_SYMBOL = {
    **FIG_BASE,
    "type": "SYMBOL",
    "guid": (0, 3),
    "children": [FIG_TEXT, FIG_RECT, FIG_VECTOR],
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
        {
            (0, 3): FIG_SYMBOL,
            (0, 1): FIG_TEXT,
            (0, 2): FIG_RECT,
            (0, 5): FIG_FILL_STYLE,
            (0, 6): FIG_VECTOR,
            (1, 9): FIG_TEXT,
            (1, 10): FIG_VECTOR,
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

    def test_fill_override_emits_default_opacity_when_master_differs(self, warnings):
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
            OverrideValue(overrideName=f"{symbol_text_id}_color:fill-0", value=SKETCH_COLOR[1]),
            OverrideValue(overrideName=f"{symbol_text_id}_opacity:fill-0", value=1),
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
            OverrideValue(overrideName=f"{symbol_text_id}_color:fill-0", value=SKETCH_COLOR[1])
        ]
        assert not any(call.args[0] == "SYM003" for call in warnings.call_args_list)

    def test_fill_override_emits_normal_blend_when_master_differs(self, warnings):
        text = copy.deepcopy(FIG_TEXT)
        text["fillPaints"][0]["blendMode"] = "MULTIPLY"
        symbol = {**copy.deepcopy(FIG_SYMBOL), "children": [text, FIG_RECT, FIG_VECTOR]}
        context.init(
            None,
            {
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
            OverrideValue(overrideName=f"{symbol_rect_id}_color:border-0", value=SKETCH_COLOR[1]),
            OverrideValue(
                overrideName=f"{symbol_rect_id}_blendMode:border-0", value=BlendMode.SCREEN
            ),
            OverrideValue(overrideName=f"{symbol_rect_id}_opacity:border-0", value=0.5),
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
            overrideName=f"{symbol_vector_id}_color:fill-0", value=SKETCH_COLOR[1]
        )
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
            OverrideValue(overrideName=f"{symbol_vector_id}_opacity:fill-0", value=0.7),
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
