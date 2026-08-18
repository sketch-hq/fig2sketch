from . import base, layout, utils
from sketchformat.layer_group import Group, GroupBehavior


def convert(fig_section: dict) -> Group:
    """Converts a Figma section.

    A section shares the frame representation, since both serialize as a "group" whose
    groupBehavior tells Sketch which traits to derive. It carries less than a frame
    though: Figma sections have no layout grids, and a section cannot be a prototype
    destination or an overlay, so neither grid nor prototyping information applies.

    Figma gives a section a white background and a thin inside stroke, which we keep.
    Those arrive as ordinary fills and borders, and stay on the section's own style
    because a section does not take the GROUP path that moves them to a background
    rect.
    """
    return Group(
        **base.base_styled(fig_section),
        **layout.layout_information(fig_section),
        **base.container_information(fig_section),
        groupBehavior=GroupBehavior.SECTION,
    )


def post_process(fig_section: dict, sketch_section: Group) -> Group:
    # Sections support stacks, so they need the same child reordering as a frame
    if utils.has_auto_layout(fig_section):
        sketch_section = layout.post_process_group_layout(sketch_section)

    return sketch_section
