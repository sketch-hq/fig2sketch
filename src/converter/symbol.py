from . import instance, group, base, prototype, layout
from .context import context
from converter import utils
from sketchformat.layer_group import *
from typing import Dict, List, Optional, Sequence, Tuple

# LAYOUT_AXIS = {
#     "NONE": None,
#     "HORIZONTAL": LayoutAxis.HORIZONTAL,
#     "VERTICAL": LayoutAxis.VERTICAL,
# }

# LAYOUT_ANCHOR = {
#     "MIN": LayoutAnchor.MIN,
#     "CENTER": LayoutAnchor.MIDDLE,
#     "MAX": LayoutAnchor.MAX,
#     "BASELINE": LayoutAnchor.MIDDLE,
#     "SPACE_EVENLY": LayoutAnchor.MIDDLE,
# }


def convert(fig_symbol):
    # A symbol is an artboard with a symbolID
    master = SymbolMaster(
        **base.base_styled(fig_symbol),
        **layout.layout_information(fig_symbol),
        **prototype.prototyping_information(fig_symbol),
        symbolID=utils.gen_object_id(fig_symbol["guid"]),
    )

    # Keep the base ID as the symbol reference, create a new one for the container
    master.do_objectID = utils.gen_object_id(fig_symbol["guid"], b"symbol_master")

    try:
        parent = context.fig_node(fig_symbol["parent"]["guid"])
        if parent and parent.get("isStateGroup", False):
            master.name = symbol_variant_name(parent, fig_symbol)
            master.variantSpecs = build_variant_specs(parent["guid"], fig_symbol)

    except Exception as e:
        print(e)

    return master


def move_to_symbols_page(fig_symbol, sketch_symbol):
    # After the entire symbol is converted, move it to the Symbols page
    context.add_symbol(sketch_symbol)

    # Figma stores its stack children in bottom up order, but Sketch uses top down
    if utils.has_auto_layout(fig_symbol):
        sketch_symbol = layout.post_process_group_layout(fig_symbol, sketch_symbol)

    # Since we put the Symbol in a different page in Sketch, leave an instance where the
    # master used to be
    return instance.master_instance(fig_symbol)


def parse_variant_values(symbol_name: str) -> List[Tuple[str, str]]:
    pairs = []
    for part in symbol_name.split(","):
        part = part.strip()
        if "=" not in part:
            continue
        prop, _, val = part.partition("=")
        pairs.append((prop.strip(), val.strip()))
    return pairs


def symbol_variant_name(parent, symbol):
    pairs = parse_variant_values(symbol["name"])
    ordered_values = [parent["name"]] + [val for _, val in pairs]
    return "/".join(ordered_values)


def build_variant_properties(parent: dict) -> Optional[List[VariantProperty]]:
    parent_guid = parent["guid"]
    orders = parent.get("stateGroupPropertyValueOrders", [])

    if orders:
        return _variant_properties_from_orders(parent_guid, orders)

    return _variant_properties_from_children(parent)


def _variant_properties_from_orders(
    parent_guid: Sequence[int], orders: list
) -> List[VariantProperty]:
    properties = []
    for order in orders:
        prop_name = order["property"]
        prop_id = utils.gen_object_id(
            parent_guid, b"variant_property:" + prop_name.encode("utf-8")
        )
        values = []
        for val_name in order["values"]:
            val_id = utils.gen_object_id(
                parent_guid,
                b"variant_value:" + prop_name.encode("utf-8") + b":" + val_name.encode("utf-8"),
            )
            values.append(VariantPropertyValue(do_objectID=val_id, name=val_name))
        properties.append(VariantProperty(do_objectID=prop_id, name=prop_name, values=values))
    return properties


def _variant_properties_from_children(parent: dict) -> Optional[List[VariantProperty]]:
    from collections import OrderedDict

    prop_values: OrderedDict[str, list] = OrderedDict()
    for child in parent.get("children", []):
        if child.get("type") != "SYMBOL":
            continue
        for prop_name, val_name in parse_variant_values(child["name"]):
            if prop_name not in prop_values:
                prop_values[prop_name] = []
            if val_name not in prop_values[prop_name]:
                prop_values[prop_name].append(val_name)

    if not prop_values:
        utils.log_conversion_warning("VAR001", parent)
        return None

    parent_guid = parent["guid"]
    properties = []
    for prop_name, val_names in prop_values.items():
        prop_id = utils.gen_object_id(
            parent_guid, b"variant_property:" + prop_name.encode("utf-8")
        )
        values = []
        for val_name in val_names:
            val_id = utils.gen_object_id(
                parent_guid,
                b"variant_value:" + prop_name.encode("utf-8") + b":" + val_name.encode("utf-8"),
            )
            values.append(VariantPropertyValue(do_objectID=val_id, name=val_name))
        properties.append(VariantProperty(do_objectID=prop_id, name=prop_name, values=values))
    return properties


def build_variant_specs(parent_guid: Sequence[int], fig_symbol: dict) -> Optional[Dict[str, str]]:
    """Map VariantProperty objectID → VariantPropertyValue objectID for this symbol."""
    pairs = parse_variant_values(fig_symbol["name"])
    if not pairs:
        utils.log_conversion_warning("VAR002", fig_symbol)
        return None

    specs = {}
    for prop_name, val_name in pairs:
        prop_id = utils.gen_object_id(
            parent_guid, b"variant_property:" + prop_name.encode("utf-8")
        )
        val_id = utils.gen_object_id(
            parent_guid,
            b"variant_value:" + prop_name.encode("utf-8") + b":" + val_name.encode("utf-8"),
        )
        specs[prop_id] = val_id
    return specs
