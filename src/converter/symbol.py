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
            master.name = fig_symbol["name"]
            master.variantSpecs = build_variant_specs(parent, fig_symbol)

    except Exception as e:
        print(e)

    return master


def post_process_symbol(fig_symbol, sketch_symbol):
    """Finalize a converted symbol and decide where its master should live.

    Symbols from Figma's hidden components page are moved to Sketch's Symbols page
    and replaced at the original site with an instance. Symbols from visible Figma
    pages are returned unchanged so they stay in place. The hidden-page check is
    based on the component symbol IDs collected when the conversion context is
    initialized.
    """
    # Figma stores its stack children in bottom up order, but Sketch uses top down
    if utils.has_auto_layout(fig_symbol):
        sketch_symbol = layout.post_process_group_layout(fig_symbol, sketch_symbol)

    if context.is_component_page_symbol(fig_symbol["guid"]):
        # Symbol lives on Figma's hidden components page — move it to the Symbols page
        context.add_symbol(sketch_symbol)
        return instance.master_instance(fig_symbol)

    # Symbol lives on a visible page — keep it in place
    return sketch_symbol


def build_variant_properties(parent: dict) -> Optional[List[VariantProperty]]:
    orderedPropertyValues = parent.get("stateGroupPropertyValueOrders", [])
    if not orderedPropertyValues:
        utils.log_conversion_warning("VAR001", parent)
        return None
    return _variant_properties_from_orders(parent["guid"], orderedPropertyValues)


def _variant_properties_from_orders(
    parent_guid: Sequence[int], orderedPropertyValues: list
) -> List[VariantProperty]:
    properties = []
    for orderedPropertyValue in orderedPropertyValues:
        prop_name = orderedPropertyValue["property"]
        prop_id = utils.gen_object_id(
            parent_guid, b"variant_property:" + prop_name.encode("utf-8")
        )
        values = []
        for val_name in orderedPropertyValue["values"]:
            val_id = utils.gen_object_id(
                parent_guid,
                b"variant_value:" + prop_name.encode("utf-8") + b":" + val_name.encode("utf-8"),
            )
            values.append(VariantPropertyValue(do_objectID=val_id, name=val_name))
        properties.append(VariantProperty(do_objectID=prop_id, name=prop_name, values=values))
    return properties


def build_variant_specs(parent: dict, fig_symbol: dict) -> Optional[Dict[str, str]]:
    """Map VariantProperty objectID → VariantPropertyValue objectID for this symbol."""
    parent_guid = parent["guid"]
    prop_specs = fig_symbol.get("variantPropSpecs", [])

    pairs = _pairs_from_prop_specs(parent, prop_specs)

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


def _pairs_from_prop_specs(parent: dict, prop_specs: list) -> List[Tuple[str, str]]:
    """Resolve variantPropSpecs entries to (property_name, value) pairs via componentPropDefs."""
    prop_defs = {
        tuple(d["id"]): d["name"]
        for d in parent.get("componentPropDefs", [])
        if d.get("type") == "VARIANT"
    }

    pairs = []
    for spec in prop_specs:
        prop_name = prop_defs.get(tuple(spec["propDefId"]))
        if prop_name is not None:
            pairs.append((prop_name, spec["value"]))
    return pairs
