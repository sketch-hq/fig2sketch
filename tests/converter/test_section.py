from .base import *
from converter import tree
from converter.context import context
from sketchformat.layer_group import GroupBehavior

FIG_SECTION = {
    **FIG_BASE,
    "type": "SECTION",
    "resizeToFit": False,
    "children": [],
}

# The destination link is the only prototyping information a fig section can carry.
FIG_SECTION_WITH_DESTINATION_LINK = {
    **FIG_SECTION,
    "guid": (0, 2),
    "parent": {"guid": (0, 1)},
    "prototypeInteractions": [
        {
            "isDeleted": False,
            "event": {"interactionType": "ON_CLICK"},
            "actions": [
                {
                    "navigationType": "NAVIGATE",
                    "connectionType": "INTERNAL_NODE",
                    "transitionNodeID": (0, 9),
                    "transitionType": "INSTANT_TRANSITION",
                }
            ],
        }
    ],
}

FIG_LINK_TARGET = {**FIG_BASE, "type": "FRAME", "guid": (0, 9), "children": []}

FIG_LINK_CANVAS = {
    **FIG_BASE,
    "type": "CANVAS",
    "guid": (0, 1),
    "resizeToFit": False,
    "children": [FIG_SECTION_WITH_DESTINATION_LINK, FIG_LINK_TARGET],
}


@pytest.fixture
def linked_section():
    context.init(
        None,
        {
            (0, 1): FIG_LINK_CANVAS,
            (0, 2): FIG_SECTION_WITH_DESTINATION_LINK,
            (0, 9): FIG_LINK_TARGET,
        },
        "DISPLAY_P3",
    )


def test_section_uses_the_section_behavior():
    section = tree.convert_node(FIG_SECTION, "CANVAS")

    assert section._class == "group"
    assert section.groupBehavior == GroupBehavior.SECTION


def test_section_keeps_its_own_styling():
    """A fig section carries a white background and a thin inside stroke, which we
    preserve, so the fill and border stay on the section's own style rather than
    moving to a background rect."""
    fig_section = {
        **FIG_SECTION,
        "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[0], "opacity": 0.9, "visible": True}],
        "strokePaints": [
            {"type": "SOLID", "color": FIG_COLOR[1], "opacity": 0.7, "visible": True}
        ],
        "strokeWeight": 1,
        "strokeAlign": "INSIDE",
        "children": [{**FIG_BASE, "type": "ROUNDED_RECTANGLE"}],
    }

    section = tree.convert_node(fig_section, "CANVAS")

    assert section.style.fills[0].color == SKETCH_COLOR[0]
    assert section.style.borders[0].color == SKETCH_COLOR[1]


def test_section_keeps_behavior_when_resizing_to_fit():
    """resizeToFit chooses between frame and group for a frame, but a section is a
    container kind, so it stays a section either way."""
    for resize_to_fit in (True, False):
        section = tree.convert_node({**FIG_SECTION, "resizeToFit": resize_to_fit}, "CANVAS")

        assert section.groupBehavior == GroupBehavior.SECTION


def test_section_ignores_the_destination_link(linked_section):
    """Sketch allows a section to be neither a prototype source nor a destination, so
    the link is dropped rather than converted.

    The same node as a frame keeps it, which is what makes the assertion worth making
    and would catch the fixture going stale.
    """
    section = tree.convert_node(FIG_SECTION_WITH_DESTINATION_LINK, "CANVAS")

    assert section.flow is None

    frame = tree.convert_node({**FIG_SECTION_WITH_DESTINATION_LINK, "type": "FRAME"}, "CANVAS")

    assert frame.flow is not None
