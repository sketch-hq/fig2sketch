from .base import *
from converter import tree, symbol, utils
from sketchformat.layer_group import VariantProperty, VariantPropertyValue
from sketchformat.layer_shape import Rectangle
import pytest
from converter.context import context

FIG_SYMBOL = {
    **FIG_BASE,
    "type": "SYMBOL",
    "children": [],
}

FIG_COMPONENT_SET = {
    **FIG_BASE,
    "type": "FRAME",
    "name": "Button",
    "guid": (10, 10),
    "isStateGroup": True,
    "resizeToFit": False,
    "stateGroupPropertyValueOrders": [
        {"property": "Size", "values": ["Small", "Large"]},
        {"property": "State", "values": ["Default", "Hover"]},
    ],
    "children": [
        {
            **FIG_BASE,
            "type": "SYMBOL",
            "name": "Size=Small, State=Default",
            "guid": (11, 11),
            "children": [],
            "parent": {"guid": (10, 10)},
        },
        {
            **FIG_BASE,
            "type": "SYMBOL",
            "name": "Size=Large, State=Hover",
            "guid": (12, 12),
            "children": [],
            "parent": {"guid": (10, 10)},
        },
    ],
    "parent": {"guid": (1, 1)},
}


@pytest.fixture
def empty_context(monkeypatch):
    context.init(None, {}, "DISPLAY_P3")


def test_rounded_corners(no_prototyping, empty_context):
    master = tree.convert_node(
        {**FIG_SYMBOL, "rectangleTopLeftCornerRadius": 5},
        "",
    )

    assert master._class == "symbolMaster"
    assert master.style.corners.radii[0] == 5


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

    assert g._class == "symbolMaster"
    assert g.style.shadows == [
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
    assert (
        symbol.symbol_variant_name(variants, variants["children"][0])
        == "Property 1=Potato, Property 2=Another"
    )


# --- parse_variant_values ---


def test_parse_variant_values():
    assert symbol.parse_variant_values("Size=Small, State=Default") == [
        ("Size", "Small"),
        ("State", "Default"),
    ]


def test_parse_variant_values_single():
    assert symbol.parse_variant_values("Tinted=True") == [("Tinted", "True")]


def test_parse_variant_values_malformed():
    assert symbol.parse_variant_values("NoEquals") == []


def test_parse_variant_values_empty_value():
    assert symbol.parse_variant_values("A=1, B=, C=3") == [("A", "1"), ("B", ""), ("C", "3")]


# --- build_variant_properties ---


def test_build_variant_properties():
    props = symbol.build_variant_properties(FIG_COMPONENT_SET)

    assert len(props) == 2
    assert props[0].name == "Size"
    assert [v.name for v in props[0].values] == ["Small", "Large"]
    assert props[1].name == "State"
    assert [v.name for v in props[1].values] == ["Default", "Hover"]


def test_build_variant_properties_ids_are_deterministic():
    props_a = symbol.build_variant_properties(FIG_COMPONENT_SET)
    props_b = symbol.build_variant_properties(FIG_COMPONENT_SET)

    assert props_a[0].do_objectID == props_b[0].do_objectID
    assert props_a[0].values[0].do_objectID == props_b[0].values[0].do_objectID


def test_build_variant_properties_fallback(warnings):
    parent = {
        **FIG_BASE,
        "type": "FRAME",
        "name": "Fallback",
        "guid": (20, 20),
        "isStateGroup": True,
        "children": [
            {**FIG_BASE, "type": "SYMBOL", "name": "Color=Red, Size=Big", "guid": (21, 21)},
            {**FIG_BASE, "type": "SYMBOL", "name": "Color=Blue, Size=Small", "guid": (22, 22)},
        ],
    }
    props = symbol.build_variant_properties(parent)

    assert len(props) == 2
    assert props[0].name == "Color"
    assert [v.name for v in props[0].values] == ["Red", "Blue"]
    assert props[1].name == "Size"
    assert [v.name for v in props[1].values] == ["Big", "Small"]


def test_build_variant_properties_fallback_no_children(warnings):
    parent = {
        **FIG_BASE,
        "type": "FRAME",
        "name": "Empty",
        "guid": (30, 30),
        "isStateGroup": True,
        "children": [],
    }
    assert symbol.build_variant_properties(parent) is None
    warnings.assert_called_with("VAR001", parent)


# --- Full pipeline: variant data on converted layers ---


@pytest.fixture
def component_set_context(monkeypatch):
    page = {
        **FIG_BASE,
        "type": "CANVAS",
        "name": "Page",
        "guid": (1, 1),
        "children": [FIG_COMPONENT_SET],
        "parent": {"guid": (0, 0)},
        "backgroundEnabled": False,
        "backgrounds": [],
    }
    id_map = {}
    _collect_ids(page, id_map)
    context.init(None, id_map, "DISPLAY_P3")


def _collect_ids(node, id_map):
    id_map[tuple(node["guid"])] = node
    for child in node.get("children", []):
        _collect_ids(child, id_map)


def test_variant_specs_on_symbol_master(no_prototyping, component_set_context):
    master = tree.convert_node(FIG_COMPONENT_SET["children"][0], "FRAME")

    assert master.variantSpecs is not None
    assert len(master.variantSpecs) == 2


def test_variant_ids_match(no_prototyping, component_set_context):
    master = tree.convert_node(FIG_COMPONENT_SET["children"][0], "FRAME")

    props = symbol.build_variant_properties(FIG_COMPONENT_SET)

    prop_ids = {p.do_objectID for p in props}
    val_ids = {v.do_objectID for p in props for v in p.values}

    for prop_id, val_id in master.variantSpecs.items():
        assert prop_id in prop_ids
        assert val_id in val_ids


def test_variant_name_preserved(no_prototyping, component_set_context):
    master = tree.convert_node(FIG_COMPONENT_SET["children"][0], "FRAME")

    assert master.name == "Size=Small, State=Default"


def test_non_variant_symbol_unaffected(no_prototyping, empty_context):
    master = tree.convert_node({**FIG_SYMBOL}, "")

    assert master.variantSpecs is None


def test_variant_properties_on_frame(no_prototyping, component_set_context):
    sketch_frame = tree.convert_node(FIG_COMPONENT_SET, "CANVAS")

    assert sketch_frame.groupBehavior == 3
    assert sketch_frame.variantProperties is not None
    assert len(sketch_frame.variantProperties) == 2
    assert sketch_frame.variantProperties[0].name == "Size"
    assert sketch_frame.variantProperties[1].name == "State"


def test_non_variant_frame_keeps_default_group_behavior(no_prototyping, empty_context):
    fig_frame = {**FIG_BASE, "type": "FRAME", "resizeToFit": False, "children": []}
    sketch_frame = tree.convert_node(fig_frame, "CANVAS")

    assert sketch_frame.groupBehavior == 1
