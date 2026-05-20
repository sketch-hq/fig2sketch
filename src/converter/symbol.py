from . import instance, group, base, prototype, layout
from .context import context
from converter import utils
from sketchformat.layer_group import *

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

    # Use better names for variants if possible
    try:
        parent = context.fig_node(fig_symbol["parent"]["guid"])
        if parent and parent.get("isStateGroup", False):
            master.name = symbol_variant_name(parent, fig_symbol)

    except Exception as e:
        print(e)

    return master


def move_to_symbols_page_if_needed(fig_symbol, sketch_symbol):
    # Figma stores its stack children in bottom up order, but Sketch uses top down
    if utils.has_auto_layout(fig_symbol):
        sketch_symbol = layout.post_process_group_layout(fig_symbol, sketch_symbol)

    if context.is_component_page_symbol(fig_symbol["guid"]):
        # Symbol lives on Figma's hidden components page — move it to the Symbols page
        context.add_symbol(sketch_symbol)
        return instance.master_instance(fig_symbol)

    # Symbol lives on a visible page — keep it in place
    return sketch_symbol


def symbol_variant_name(parent, symbol):
    property_values = [x.strip().split("=")[1] for x in symbol["name"].split(",")]
    ordered_values = [parent["name"]] + property_values
    return "/".join(ordered_values)
