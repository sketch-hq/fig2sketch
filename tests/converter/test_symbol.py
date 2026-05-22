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
    "componentPropDefs": [
        {"id": (100, 1), "name": "Size", "type": "VARIANT"},
        {"id": (100, 2), "name": "State", "type": "VARIANT"},
    ],
    "children": [
        {
            **FIG_BASE,
            "type": "SYMBOL",
            "name": "Size=Small, State=Default",
            "guid": (11, 11),
            "children": [],
            "parent": {"guid": (10, 10)},
            "variantPropSpecs": [
                {"propDefId": (100, 1), "value": "Small"},
                {"propDefId": (100, 2), "value": "Default"},
            ],
        },
        {
            **FIG_BASE,
            "type": "SYMBOL",
            "name": "Size=Large, State=Hover",
            "guid": (12, 12),
            "children": [],
            "parent": {"guid": (10, 10)},
            "variantPropSpecs": [
                {"propDefId": (100, 1), "value": "Large"},
                {"propDefId": (100, 2), "value": "Hover"},
            ],
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


def test_variant_name_uses_fig_name_as_is(no_prototyping, empty_context):
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
    context._node_by_id[(22, 22)] = variants

    master = tree.convert_node(variants["children"][0], "FRAME")

    assert master.name == "Property 1=Potato, Property 2=Another"


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


def test_variant_specs_from_variantPropSpecs(no_prototyping, component_set_context):
    """variantSpecs are built from variantPropSpecs + componentPropDefs, not name parsing."""
    master = tree.convert_node(FIG_COMPONENT_SET["children"][0], "FRAME")
    props = symbol.build_variant_properties(FIG_COMPONENT_SET)

    prop_by_name = {p.name: p for p in props}
    val_by_name = {(p.name, v.name): v for p in props for v in p.values}

    size_prop_id = prop_by_name["Size"].do_objectID
    small_val_id = val_by_name[("Size", "Small")].do_objectID
    state_prop_id = prop_by_name["State"].do_objectID
    default_val_id = val_by_name[("State", "Default")].do_objectID

    assert master.variantSpecs[size_prop_id] == small_val_id
    assert master.variantSpecs[state_prop_id] == default_val_id


def test_non_variant_frame_keeps_default_group_behavior(no_prototyping, empty_context):
    fig_frame = {**FIG_BASE, "type": "FRAME", "resizeToFit": False, "children": []}
    sketch_frame = tree.convert_node(fig_frame, "CANVAS")

    assert sketch_frame.groupBehavior == 1
