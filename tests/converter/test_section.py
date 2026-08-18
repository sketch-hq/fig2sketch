from .base import *
from converter import tree
from sketchformat.layer_group import GroupBehavior

FIG_SECTION = {
    **FIG_BASE,
    "type": "SECTION",
    "resizeToFit": False,
    "children": [],
}


def test_section_uses_the_section_behavior():
    section = tree.convert_node(FIG_SECTION, "CANVAS")

    assert section._class == "group"
    assert section.groupBehavior == GroupBehavior.SECTION


def test_section_keeps_its_own_styling():
    """Figma gives a section a white background and a thin inside stroke, which we
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


def test_section_carries_no_frame_only_information():
    """Figma sections have no layout grids, and a section can be neither a prototype
    destination nor an overlay, so none of that is converted for one.

    Note this needs no prototyping fixture, unlike the frame tests: a section never
    consults the canvas for prototype information in the first place.
    """
    section = tree.convert_node(FIG_SECTION, "CANVAS")

    assert section.grid is None
    assert section.layout is None
    assert section.presentationStyle is None
    assert section.isFlowHome is None
    assert section.overlayBackgroundInteraction is None
    assert section.overlaySettings is None
    assert section.prototypeViewport is None
