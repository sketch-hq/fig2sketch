import pytest
from .base import *
from converter import prototype, tree
from converter.config import config
from converter.context import context
from sketchformat.layer_group import GroupBehavior
from unittest.mock import ANY


@pytest.fixture
def no_prototyping(monkeypatch):
    monkeypatch.setattr(prototype, "prototyping_information", lambda _: {})


@pytest.fixture
def empty_context():
    context.init(None, {}, "DISPLAY_P3")


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


@pytest.mark.usefixtures("no_prototyping", "empty_context")
class TestSectionPromotion:
    """Sketch only allows a section on a page or inside another section, so frames
    above one are promoted to sections rather than dropping the section behavior."""

    def _page(self, *children):
        return {**FIG_BASE, "type": "CANVAS", "guid": (99, 99), "children": list(children)}

    def _frame(self, guid, *children):
        return {
            **FIG_BASE,
            "type": "FRAME",
            "guid": guid,
            "resizeToFit": False,
            "children": list(children),
        }

    def _section(self, guid):
        return {**FIG_BASE, "type": "SECTION", "guid": guid, "children": []}

    def test_frame_around_section_is_promoted(self, warnings):
        outer = self._frame((1, 1), self._section((2, 2)))
        tree.mark_promoted_sections(self._page(outer))

        converted = tree.convert_node(outer, "CANVAS")

        assert converted.groupBehavior == GroupBehavior.SECTION
        warnings.assert_any_call("SEC001", ANY)

    def test_whole_ancestor_chain_is_promoted(self):
        """Promoting only the innermost frame would still leave a section in a frame."""
        inner = self._frame((2, 2), self._section((3, 3)))
        outer = self._frame((1, 1), inner)
        tree.mark_promoted_sections(self._page(outer))

        assert tree.get_node_type(outer, "CANVAS") == "SECTION"
        assert tree.get_node_type(inner, "FRAME") == "SECTION"

    def test_frame_without_section_is_untouched(self):
        plain = self._frame((1, 1), {**FIG_BASE, "type": "ROUNDED_RECTANGLE"})
        tree.mark_promoted_sections(self._page(plain))

        converted = tree.convert_node(plain, "CANVAS")

        assert converted.groupBehavior == GroupBehavior.FRAME

    def test_sibling_frame_is_untouched(self):
        """Only the chain above a section is affected, not frames beside it."""
        with_section = self._frame((1, 1), self._section((2, 2)))
        sibling = self._frame((3, 3))
        tree.mark_promoted_sections(self._page(with_section, sibling))

        assert tree.get_node_type(with_section, "CANVAS") == "SECTION"
        assert tree.get_node_type(sibling, "CANVAS") == "FRAME"

    def test_section_on_a_page_is_left_alone(self, warnings):
        """A page may hold a section, so it ends the chain without being warned about."""
        tree.mark_promoted_sections(self._page(self._section((1, 1))))

        assert not context.is_promoted_to_section((99, 99))
        warnings.assert_not_called()

    def test_section_inside_section_needs_no_promotion(self, warnings):
        """A section may contain a section, so nothing above it has to change."""
        outer = {
            **FIG_BASE,
            "type": "SECTION",
            "guid": (1, 1),
            "children": [self._section((2, 2))],
        }
        tree.mark_promoted_sections(self._page(outer))

        assert not context.is_promoted_to_section((1, 1))
        assert tree.get_node_type(outer, "CANVAS") == "SECTION"
        warnings.assert_not_called()

    def test_frame_below_a_section_is_untouched(self):
        """Promotion runs above a section, never into what it contains."""
        inner = self._frame((2, 2))
        outer = {**FIG_BASE, "type": "SECTION", "guid": (1, 1), "children": [inner]}
        tree.mark_promoted_sections(self._page(outer))

        assert tree.get_node_type(inner, "SECTION") == "FRAME"

    def test_frames_below_a_section_still_promote(self, monkeypatch):
        """Sitting under a section does not make a frame a legal home for a variant
        set, so the subtree below one is searched on its own."""
        monkeypatch.setattr(config, "import_variants", True)
        variant_set = {
            **FIG_BASE,
            "type": "FRAME",
            "guid": (4, 4),
            "isStateGroup": True,
            "resizeToFit": False,
            "children": [],
        }
        inner = self._frame((3, 3), variant_set)
        outer = self._frame((2, 2), inner)
        section = {**FIG_BASE, "type": "SECTION", "guid": (1, 1), "children": [outer]}
        tree.mark_promoted_sections(self._page(section))

        assert tree.get_node_type(outer, "SECTION") == "SECTION"
        assert tree.get_node_type(inner, "SECTION") == "SECTION"
        assert not context.is_promoted_to_section((1, 1))

    def test_symbol_master_cannot_be_promoted(self, warnings):
        """A symbol master cannot become a section, so the nesting stays illegal."""
        master = {
            **FIG_BASE,
            "type": "SYMBOL",
            "guid": (1, 1),
            "children": [self._section((2, 2))],
        }
        tree.mark_promoted_sections(self._page(master))

        assert not context.is_promoted_to_section((1, 1))
        warnings.assert_called_once_with("SEC002", master)

    def test_variant_set_in_frame_promotes(self, monkeypatch):
        """The case this exists for: the fig format allows a variant set in a frame."""
        monkeypatch.setattr(config, "import_variants", True)
        variant_set = {
            **FIG_BASE,
            "type": "FRAME",
            "guid": (2, 2),
            "isStateGroup": True,
            "resizeToFit": False,
            "children": [],
        }
        outer = self._frame((1, 1), variant_set)
        tree.mark_promoted_sections(self._page(outer))

        assert tree.get_node_type(outer, "CANVAS") == "SECTION"

    def test_variant_set_in_frame_ignored_when_variants_disabled(self):
        """With the flag off the frame is not a variant set, so nothing is promoted."""
        variant_set = {
            **FIG_BASE,
            "type": "FRAME",
            "guid": (2, 2),
            "isStateGroup": True,
            "resizeToFit": False,
            "children": [],
        }
        outer = self._frame((1, 1), variant_set)
        tree.mark_promoted_sections(self._page(outer))

        assert tree.get_node_type(outer, "CANVAS") == "FRAME"
