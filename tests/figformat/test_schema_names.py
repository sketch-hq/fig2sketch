"""Check that fig field names and enum values the converter matches on exist in a real
fig file's schema. Unit test fixtures are handwritten dicts, so a misspelled name passes
them while never matching a real file."""

import pytest
from zipfile import ZipFile
from figformat import kiwi
from converter import instance, text

# Newest fig version in tests/data
SCHEMA_FILE = "tests/data/prototyping.fig"

KIND_ENUM = 0


@pytest.fixture(scope="module")
def schema():
    with ZipFile(SCHEMA_FILE).open("canvas.fig") as reader:
        _, schema = kiwi.read_schema(reader)

    return {t["name"]: t for t in schema.types}, schema.types


def field(schema, message, name):
    by_name, _ = schema
    fields = {f["name"]: f for f in by_name[message]["fields"].values()}
    assert name in fields, f"{message} has no field {name!r}"
    return fields[name]


def enum_values(schema, message, name):
    _, types = schema
    type_id = field(schema, message, name)["type"]
    assert type_id >= 0 and types[type_id]["kind"] == KIND_ENUM, f"{message}.{name} is not an enum"
    return {v["name"] for v in types[type_id]["fields"].values()}


NODE_CHANGE_FIELDS = sorted(
    {
        # Overrides handled by instance.convert_override
        "guidPath",
        "textData",
        "overriddenSymbolID",
        "effects",
        # Derived symbol data applied by instance.apply_overrides
        "transform",
        "strokeWeight",
        # Read by base and layout
        "stackMode",
        "stackPositioning",
        "stackChildAlignSelf",
        "stackChildPrimaryGrow",
        "stackCounterSizing",
        "stackPrimarySizing",
        "stackSpacing",
        "stackPrimaryAlignItems",
        "stackCounterAlignItems",
        "stackWrap",
        "stackCounterSpacing",
        "stackReverseZIndex",
        "bordersTakeSpace",
        "textAutoResize",
        "horizontalConstraint",
        "verticalConstraint",
    }
    | instance.IGNORED_OVERRIDE_PROPS
    | instance.INSTANCE_LAYER_PROPS
    | set(instance.PAINT_PROPS)
)

PAINT_FIELDS = sorted(
    instance.IGNORED_PAINT_PROPS | instance.GRADIENT_PAINT_PROPS | instance.IMAGE_PAINT_PROPS
)

ENUM_VALUES = sorted(
    {
        # text.py, base.py
        *(("NodeChange", "textAutoResize", v) for v in text.TEXT_BEHAVIOUR),
        *(("NodeChange", "textAutoResize", v) for v in text.CONSTRAINT_MASK_FOR_AUTO_RESIZE),
        # base.py
        ("NodeChange", "stackMode", "HORIZONTAL"),
        ("NodeChange", "stackMode", "VERTICAL"),
        ("NodeChange", "stackPositioning", "ABSOLUTE"),
        ("NodeChange", "stackChildAlignSelf", "STRETCH"),
        ("NodeChange", "stackCounterSizing", "RESIZE_TO_FIT_WITH_IMPLICIT_SIZE"),
        ("NodeChange", "stackPrimarySizing", "FIXED"),
        ("NodeChange", "horizontalConstraint", "SCALE"),
        ("NodeChange", "verticalConstraint", "SCALE"),
        # layout.py
        ("NodeChange", "stackWrap", "WRAP"),
        ("NodeChange", "stackPrimaryAlignItems", "MIN"),
        ("NodeChange", "stackPrimaryAlignItems", "CENTER"),
        ("NodeChange", "stackPrimaryAlignItems", "MAX"),
        ("NodeChange", "stackPrimaryAlignItems", "SPACE_EVENLY"),
        ("NodeChange", "stackCounterAlignItems", "MIN"),
        ("NodeChange", "stackCounterAlignItems", "CENTER"),
        ("NodeChange", "stackCounterAlignItems", "MAX"),
        # instance.py
        ("Paint", "type", "SOLID"),
        *(("Paint", "type", v) for v in instance.GRADIENT_PAINT_TYPES),
        ("Effect", "type", "DROP_SHADOW"),
        ("Effect", "type", "INNER_SHADOW"),
    }
)


@pytest.mark.parametrize("name", NODE_CHANGE_FIELDS)
def test_node_change_field_exists(schema, name):
    field(schema, "NodeChange", name)


@pytest.mark.parametrize("name", PAINT_FIELDS)
def test_paint_field_exists(schema, name):
    field(schema, "Paint", name)


@pytest.mark.parametrize("message,name,value", ENUM_VALUES)
def test_enum_value_exists(schema, message, name, value):
    assert value in enum_values(schema, message, name)
