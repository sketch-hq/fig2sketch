from .base import *
from converter import symbol, tree
from converter.prototype import *
from sketchformat.layer_common import Rect
from sketchformat.layer_group import Group
from sketchformat.prototype import *
from sketchformat.serialize.json import convert_object
from unittest.mock import ANY

FIG_ARTBOARD_NO_PROTOTYPE = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 2),
    "resizeToFit": False,
    "children": [],
    "parent": {"guid": (0, 1)},
}

FIG_CANVAS_NO_PROTOTYPE = {
    **FIG_BASE,
    "type": "CANVAS",
    "guid": (0, 1),
    "resizeToFit": False,
    "children": [FIG_ARTBOARD_NO_PROTOTYPE],
}

FIG_ARTBOARD = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 4),
    "children": [],
    "parent": {"guid": (0, 3)},
}

FIG_OVERLAY = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 5),
    "overlayPositionType": "BOTTOM_CENTER",
    "overlayBackgroundInteraction": "CLOSE_ON_CLICK_OUTSIDE",
    "children": [],
    "parent": {"guid": (0, 3)},
}

FIG_MANUAL_OVERLAY = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 6),
    "overlayPositionType": "MANUAL",
    "overlayBackgroundInteraction": "CLOSE_ON_CLICK_OUTSIDE",
    "children": [],
    "parent": {"guid": (0, 3)},
}

FIG_CANVAS = {
    **FIG_BASE,
    "type": "CANVAS",
    "guid": (0, 1),
    "resizeToFit": False,
    "children": [FIG_ARTBOARD, FIG_OVERLAY],
    "prototypeDevice": {
        "type": "PRESET",
        "size": {"x": 393.0, "y": 852.0},
        "presetIdentifier": "APPLE_IPHONE_14_PRO_SPACEBLACK",
        "rotation": "NONE",
    },
}


def interaction(*actions: dict, trigger: str = "ON_CLICK", deleted: bool = False) -> dict:
    return {
        "isDeleted": deleted,
        "event": {"interactionType": trigger},
        "actions": list(actions),
    }


def interactions(*actions: dict, trigger: str = "ON_CLICK", deleted: bool = False) -> dict:
    return {"prototypeInteractions": [interaction(*actions, trigger=trigger, deleted=deleted)]}


def link(destination, navigation: str = "OVERLAY", **extra) -> dict:
    return {
        "navigationType": navigation,
        "connectionType": "INTERNAL_NODE",
        "transitionNodeID": destination,
        **extra,
    }


FIG_SECTION = {
    **FIG_BASE,
    "type": "SECTION",
    "guid": (0, 20),
    "children": [],
    "parent": {"guid": (0, 3)},
}

FIG_FRAME_IN_SECTION = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 21),
    "prototypeStartingPoint": {"name": "Flow 1", "description": ""},
    "children": [],
    "parent": {"guid": (0, 20)},
}

FIG_FRAME_IN_FRAME = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 22),
    "children": [],
    "parent": {"guid": (0, 4)},
}

# The fig format leaves out overlay settings that hold their defaults, so an overlay
# that is centered and does not close on a click outside carries none of them
FIG_DEFAULT_OVERLAY = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 23),
    "children": [],
    "parent": {"guid": (0, 3)},
}

# Overlay settings stay on a frame after the links that opened it as one are gone
FIG_UNLINKED_OVERLAY = {
    **FIG_OVERLAY,
    "guid": (0, 24),
}

FIG_OVERLAY_OPENER = {
    **FIG_BASE,
    "type": "ROUNDED_RECTANGLE",
    "guid": (0, 30),
    "parent": {"guid": (0, 4)},
    **interactions(link((0, 5)), link((0, 23), navigation="SWAP")),
}


@pytest.fixture
def canvas(monkeypatch):
    context.init(
        None,
        {
            (0, 1): FIG_CANVAS_NO_PROTOTYPE,
            (0, 2): FIG_ARTBOARD_NO_PROTOTYPE,
            (0, 3): FIG_CANVAS,
            (0, 4): FIG_ARTBOARD,
            (0, 5): FIG_OVERLAY,
            (0, 20): FIG_SECTION,
            (0, 21): FIG_FRAME_IN_SECTION,
            (0, 22): FIG_FRAME_IN_FRAME,
            (0, 23): FIG_DEFAULT_OVERLAY,
            (0, 24): FIG_UNLINKED_OVERLAY,
            (0, 30): FIG_OVERLAY_OPENER,
        },
        "DISPLAY_P3",
    )
    mark_overlay_destinations([FIG_OVERLAY_OPENER])


@pytest.fixture
def overlay(monkeypatch):
    context.init(None, {(0, 5): FIG_OVERLAY}, "DISPLAY_P3")


@pytest.fixture
def manual_overlay(monkeypatch):
    context.init(None, {(0, 6): FIG_MANUAL_OVERLAY}, "DISPLAY_P3")


FIG_COMPONENT = {
    **FIG_BASE,
    "type": "SYMBOL",
    "guid": (0, 25),
    "resizeToFit": False,
    "children": [],
    "parent": {"guid": (0, 3)},
}


@pytest.fixture
def component(monkeypatch):
    context.init(None, {(0, 3): FIG_CANVAS, (0, 25): FIG_COMPONENT}, "DISPLAY_P3")


@pytest.mark.usefixtures("canvas")
class TestPrototypeInformation:
    def test_no_prototype(self):
        info = prototyping_information(FIG_ARTBOARD_NO_PROTOTYPE)

        assert info["isFlowHome"] is False
        assert info["overlayBackgroundInteraction"] == OverlayBackgroundInteraction.NONE
        assert info["presentationStyle"] == PresentationStyle.SCREEN

    def test_prototype_information_with_no_overlay(self):
        info = prototyping_information(FIG_ARTBOARD)

        assert info["isFlowHome"] is False
        assert info["prototypeViewport"].name == FIG_CANVAS["prototypeDevice"]["presetIdentifier"]
        assert info["prototypeViewport"].size == Point(393.0, 852.0)
        assert info["overlayBackgroundInteraction"] == OverlayBackgroundInteraction.NONE
        assert info["presentationStyle"] == PresentationStyle.SCREEN
        assert info["overlaySettings"].overlayAnchor == Point(0.5, 0.5)
        assert info["overlaySettings"].sourceAnchor == Point(0.5, 0.5)

    def test_prototype_information_with_overlay(self):
        info = prototyping_information(FIG_OVERLAY)

        assert info["isFlowHome"] is False
        assert info["overlayBackgroundInteraction"] == OverlayBackgroundInteraction.CLOSES_OVERLAY
        assert info["presentationStyle"] == PresentationStyle.OVERLAY
        assert info["overlaySettings"].overlayType == OverlayType.ABSOLUTE
        assert info["overlaySettings"].overlayAnchor == Point(0.5, 1)
        assert info["overlaySettings"].sourceAnchor == Point(0.5, 1)
        assert info["overlaySettings"].offset == Point(0, 0)

    def test_overlay_with_default_settings(self):
        """A frame opened as an overlay is one, even with no overlay settings of its
        own to show it, since the fig format leaves out the ones at their defaults."""
        info = prototyping_information(FIG_DEFAULT_OVERLAY)

        assert info["presentationStyle"] == PresentationStyle.OVERLAY
        assert info["overlayBackgroundInteraction"] == OverlayBackgroundInteraction.NONE
        assert info["overlaySettings"].overlayType == OverlayType.ABSOLUTE
        assert info["overlaySettings"].overlayAnchor == Point(0.5, 0.5)

    def test_overlay_settings_without_an_overlay_link_make_a_screen(self):
        """Leftover settings do not make an overlay: what matters is how links open it."""
        info = prototyping_information(FIG_UNLINKED_OVERLAY)

        assert info["presentationStyle"] == PresentationStyle.SCREEN
        assert info["overlayBackgroundInteraction"] == OverlayBackgroundInteraction.NONE
        assert "prototypeViewport" in info

    def test_frame_in_a_section_belongs_to_the_page(self):
        """A section only groups frames, so the page's device and the frame's starting
        point still apply to a frame inside one."""
        info = prototyping_information(FIG_FRAME_IN_SECTION)

        assert info["isFlowHome"] is True
        assert info["prototypeViewport"].name == FIG_CANVAS["prototypeDevice"]["presetIdentifier"]
        assert info["presentationStyle"] == PresentationStyle.SCREEN

    def test_frame_in_a_promoted_section_belongs_to_the_page(self):
        context.promote_to_section(FIG_ARTBOARD["guid"])

        info = prototyping_information(FIG_FRAME_IN_FRAME)

        assert info["prototypeViewport"].name == FIG_CANVAS["prototypeDevice"]["presetIdentifier"]

    def test_frame_in_a_frame_is_not_a_screen_of_the_page(self):
        info = prototyping_information(FIG_FRAME_IN_FRAME)

        assert info["isFlowHome"] is False
        assert info["presentationStyle"] == PresentationStyle.SCREEN
        assert "prototypeViewport" not in info


class TestMarkOverlayDestinations:
    @pytest.fixture(autouse=True)
    def empty_context(self):
        context.init(None, {}, "DISPLAY_P3")

    def test_overlay_and_swap_destinations_are_marked(self):
        mark_overlay_destinations(
            [
                {**FIG_BASE, **interactions(link((1, 1)))},
                {**FIG_BASE, **interactions(link((1, 2), navigation="SWAP"))},
            ]
        )

        assert context.is_overlay_destination((1, 1))
        assert context.is_overlay_destination((1, 2))

    def test_navigation_destinations_are_not_marked(self):
        mark_overlay_destinations(
            [{**FIG_BASE, **interactions(link((1, 1), navigation="NAVIGATE"))}]
        )

        assert not context.is_overlay_destination((1, 1))

    def test_deleted_interactions_are_ignored(self):
        mark_overlay_destinations([{**FIG_BASE, **interactions(link((1, 1)), deleted=True)}])

        assert not context.is_overlay_destination((1, 1))

    def test_interactions_that_are_not_converted_still_count(self):
        """A link after a delay is dropped, but still shows the frame is meant as an
        overlay."""
        fig_node = {**FIG_BASE, **interactions(link((1, 1)), trigger="AFTER_TIMEOUT")}

        mark_overlay_destinations([fig_node])

        assert context.is_overlay_destination((1, 1))

    def test_links_added_to_layers_inside_an_instance_count(self):
        """The fig format stores them as overrides on the instance, not on the layer."""
        override = {"guidPath": {"guids": [(2, 2)]}, **interactions(link((1, 1)))}
        fig_instance = {
            **FIG_BASE,
            "type": "INSTANCE",
            "symbolData": {"symbolID": (2, 1), "symbolOverrides": [override]},
        }

        mark_overlay_destinations([fig_instance])

        assert context.is_overlay_destination((1, 1))


# Step 1 opens as an overlay. A button inside it, in a group, swaps Step 2 in, and a
# button inside Step 2 swaps Step 3 in
FIG_STEPS_CANVAS = {**FIG_BASE, "type": "CANVAS", "guid": (0, 40)}
FIG_STEP_1_OPENER = {
    **FIG_BASE,
    "guid": (0, 41),
    "parent": {"guid": (0, 40)},
    **interactions(link((0, 42))),
}
FIG_STEP_1 = {**FIG_BASE, "type": "FRAME", "guid": (0, 42), "parent": {"guid": (0, 40)}}
FIG_STEP_1_GROUP = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 43),
    "parent": {"guid": (0, 42)},
    "transform": Matrix([[1, 0, 10], [0, 1, 20]]),
}
FIG_STEP_1_NEXT = {
    **FIG_BASE,
    "guid": (0, 44),
    "parent": {"guid": (0, 43)},
    "transform": Matrix([[1, 0, 5], [0, 1, 6]]),
    **interactions(link((0, 45), navigation="SWAP")),
}
FIG_STEP_2 = {**FIG_BASE, "type": "FRAME", "guid": (0, 45), "parent": {"guid": (0, 40)}}
FIG_STEP_2_NEXT = {
    **FIG_BASE,
    "guid": (0, 46),
    "parent": {"guid": (0, 45)},
    "transform": Matrix([[1, 0, 30], [0, 1, 40]]),
    **interactions(link((0, 47), navigation="SWAP")),
}
FIG_STEP_3 = {**FIG_BASE, "type": "FRAME", "guid": (0, 47), "parent": {"guid": (0, 40)}}


def init_steps(step_1_position: str) -> None:
    fig_nodes = [
        FIG_STEPS_CANVAS,
        FIG_STEP_1_OPENER,
        {**FIG_STEP_1, "overlayPositionType": step_1_position},
        FIG_STEP_1_GROUP,
        FIG_STEP_1_NEXT,
        FIG_STEP_2,
        FIG_STEP_2_NEXT,
        FIG_STEP_3,
    ]
    context.init(None, {n["guid"]: n for n in fig_nodes}, "DISPLAY_P3")
    mark_overlay_destinations(fig_nodes)


class TestSwappedOverlayPosition:
    """The fig format gives a swapped-in overlay no position of its own: it appears
    where the overlay it replaces was."""

    def test_named_position_is_reused(self):
        init_steps("BOTTOM_CENTER")

        settings = convert_flow(FIG_STEP_1_NEXT)["flow"].overlaySettings

        assert settings.overlayType == OverlayType.ABSOLUTE
        assert settings.overlayAnchor == Point(0.5, 1)

    def test_manual_position_lines_up_the_top_left_corners(self):
        """The new overlay is placed relative to the link's own layer, back by where
        that layer sits in the replaced overlay: 10 + 5 across and 20 + 6 down."""
        init_steps("MANUAL")

        settings = convert_flow(FIG_STEP_1_NEXT)["flow"].overlaySettings

        assert settings.overlayType == OverlayType.RELATIVE
        assert settings.sourceAnchor == Point(0, 0)
        assert settings.overlayAnchor == Point(0, 0)
        assert settings.offset == Point(-15, -26)

    @pytest.mark.parametrize(
        "position, anchor", [("BOTTOM_CENTER", Point(0.5, 1)), ("CENTER", Point(0.5, 0.5))]
    )
    def test_named_position_carries_through_a_chain_of_swaps(self, position, anchor):
        """Step 2 is only ever swapped in, so it has no position of its own, and is
        shown where Step 1 was."""
        init_steps(position)

        settings = convert_flow(FIG_STEP_2_NEXT)["flow"].overlaySettings

        assert settings.overlayType == OverlayType.ABSOLUTE
        assert settings.overlayAnchor == anchor

    def test_manual_position_carries_through_a_chain_of_swaps(self):
        init_steps("MANUAL")

        settings = convert_flow(FIG_STEP_2_NEXT)["flow"].overlaySettings

        assert settings.overlayType == OverlayType.RELATIVE
        assert settings.offset == Point(-30, -40)

    def test_overlays_that_only_swap_each_other_in(self):
        """With nothing that opens either of them, there is no position to follow, and
        following the swaps must not go round in circles."""
        fig_back = {
            **FIG_BASE,
            "guid": (0, 48),
            "parent": {"guid": (0, 47)},
            **interactions(link((0, 45), navigation="SWAP")),
        }
        fig_nodes = [FIG_STEPS_CANVAS, FIG_STEP_2, FIG_STEP_2_NEXT, FIG_STEP_3, fig_back]
        context.init(None, {n["guid"]: n for n in fig_nodes}, "DISPLAY_P3")
        mark_overlay_destinations(fig_nodes)

        settings = convert_flow(FIG_STEP_2_NEXT)["flow"].overlaySettings

        assert settings.overlayType == OverlayType.ABSOLUTE
        assert settings.overlayAnchor == Point(0.5, 0.5)


@pytest.mark.usefixtures("canvas")
class TestOverlayBackdrop:
    BACKDROP = {
        "backgroundType": "SOLID_COLOR",
        "backgroundColor": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 0.5},
    }

    def test_solid_background_becomes_a_backdrop_fill(self):
        backdrop = overlay_backdrop({**FIG_OVERLAY, "overlayBackgroundAppearance": self.BACKDROP})

        assert backdrop.layeringType == LayeringType.BACKDROP
        assert backdrop.fillType == FillType.COLOR
        assert backdrop.color == Color(red=1.0, green=0.0, blue=0.0, alpha=0.5)

    def test_no_background(self):
        appearance = {**self.BACKDROP, "backgroundType": "NONE"}

        assert overlay_backdrop({**FIG_OVERLAY, "overlayBackgroundAppearance": appearance}) is None
        assert overlay_backdrop(FIG_OVERLAY) is None

    def test_frame_that_is_not_an_overlay_has_no_backdrop(self):
        fig_frame = {**FIG_UNLINKED_OVERLAY, "overlayBackgroundAppearance": self.BACKDROP}

        assert overlay_backdrop(fig_frame) is None

    def test_backdrop_is_added_after_the_frame_fills(self):
        fig_frame = {
            **FIG_OVERLAY,
            "resizeToFit": False,
            "overlayBackgroundAppearance": self.BACKDROP,
            "fillPaints": [
                {"type": "SOLID", "color": FIG_COLOR[2], "opacity": 1, "visible": True}
            ],
        }

        sketch_frame = tree.convert_node(fig_frame, "")

        assert [f.layeringType for f in sketch_frame.style.fills] == [None, LayeringType.BACKDROP]


class TestConvertFlow:
    def test_discarding_of_problematic_interactions(self, warnings):
        fig_flow = {
            "prototypeInteractions": [
                {"isDeleted": True, "event": {}},
                {
                    "isDeleted": False,
                    "actions": [{"navigationType": "NAVIGATE", "connectionType": "BACK"}],
                },
                {
                    "isDeleted": False,
                    "event": {"interactionType": "DRAG"},
                    "actions": [{"navigationType": "NAVIGATE", "connectionType": "BACK"}],
                },
                {
                    "isDeleted": False,
                    "event": {"interactionType": "ON_CLICK"},
                    "actions": [
                        {},
                        {"navigationType": "BACK", "connectionType": "BACK"},
                        {"navigationType": "SCROLL", "connectionType": "FAKE_TYPE"},
                        {"navigationType": "NAVIGATE", "connectionType": "BACK"},
                    ],
                },
            ]
        }

        flow = convert_flow({**FIG_BASE, **fig_flow})

        warnings.assert_any_call("PRT001", ANY, props=["DRAG"])
        warnings.assert_any_call("PRT003", ANY, props=["BACK"])
        warnings.assert_any_call("PRT004", ANY, props=["FAKE_TYPE"])

        assert flow["flow"].destinationArtboardID == "back"
        assert flow["flow"].animationType == AnimationType.NONE
        assert flow["flow"].maintainScrollPosition is False
        assert flow["flow"].overlaySettings is None

    def test_multiple_valid_actions_warning(self, warnings):
        multiple_actions_flow = {
            "prototypeInteractions": [
                {
                    "isDeleted": False,
                    "event": {"interactionType": "ON_CLICK"},
                    "actions": [
                        {"navigationType": "NAVIGATE", "connectionType": "BACK"},
                        {"navigationType": "SCROLL", "connectionType": "NONE"},
                    ],
                }
            ]
        }

        fig_artboard = {**FIG_BASE, **multiple_actions_flow}

        flow = convert_flow(fig_artboard)

        warnings.assert_any_call("PRT002", ANY)

        assert flow["flow"].destinationArtboardID == "back"

    def test_overlay_flow(self, overlay):
        overlay_flow = {
            "prototypeInteractions": [
                {
                    "isDeleted": False,
                    "event": {"interactionType": "ON_CLICK"},
                    "actions": [
                        {
                            "navigationType": "OVERLAY",
                            "connectionType": "INTERNAL_NODE",
                            "transitionNodeID": (0, 5),
                            "transitionType": "SLIDE_FROM_LEFT",
                        }
                    ],
                }
            ]
        }

        flow = convert_flow({**FIG_BASE, **overlay_flow})

        assert flow["flow"].destinationArtboardID == utils.gen_object_id((0, 5))
        assert flow["flow"].animationType == AnimationType.SLIDE_FROM_LEFT
        assert flow["flow"].maintainScrollPosition is False
        assert flow["flow"].overlaySettings.overlayType == 0
        assert flow["flow"].overlaySettings.overlayAnchor == Point(0.5, 1)
        assert flow["flow"].overlaySettings.sourceAnchor == Point(0.5, 1)
        assert flow["flow"].overlaySettings.offset == Point(0, 0)

    def test_overly_with_manual_position(self, manual_overlay):
        overlay_flow = {
            "prototypeInteractions": [
                {
                    "isDeleted": False,
                    "event": {"interactionType": "ON_CLICK"},
                    "actions": [
                        {
                            "navigationType": "OVERLAY",
                            "connectionType": "INTERNAL_NODE",
                            "transitionNodeID": (0, 6),
                            "transitionType": "SLIDE_FROM_TOP",
                            "overlayRelativePosition": {"x": 19.6, "y": 85.0},
                        }
                    ],
                }
            ]
        }

        flow = convert_flow({**FIG_BASE, **overlay_flow})

        assert flow["flow"].destinationArtboardID == utils.gen_object_id((0, 6))
        assert flow["flow"].animationType == AnimationType.SLIDE_FROM_TOP
        assert flow["flow"].maintainScrollPosition is False
        assert flow["flow"].overlaySettings.overlayType == OverlayType.RELATIVE
        assert flow["flow"].overlaySettings.overlayAnchor == Point(0, 0)
        assert flow["flow"].overlaySettings.sourceAnchor == Point(0, 0)
        assert flow["flow"].overlaySettings.offset == Point(19.6, 85.0)

    def test_offset_is_ignored_unless_the_position_is_manual(self, overlay):
        flow = convert_flow(
            {**FIG_BASE, **interactions(link((0, 5), overlayRelativePosition={"x": 4, "y": 2}))}
        )

        assert flow["flow"].overlaySettings.overlayType == OverlayType.ABSOLUTE
        assert flow["flow"].overlaySettings.offset == Point(0, 0)

    def test_swap_closes_the_open_overlays(self, overlay):
        flow = convert_flow({**FIG_BASE, **interactions(link((0, 5), navigation="SWAP"))})

        assert flow["flow"].destinationArtboardID == utils.gen_object_id((0, 5))
        assert flow["flow"].shouldCloseExistingOverlays is True
        assert flow["flow"].overlaySettings.overlayAnchor == Point(0.5, 1)

    def test_opening_an_overlay_keeps_the_open_ones(self, overlay):
        flow = convert_flow({**FIG_BASE, **interactions(link((0, 5)))})

        assert flow["flow"].shouldCloseExistingOverlays is False

    def test_close_becomes_a_back_link(self, warnings):
        """Sketch closes an overlay when a back link inside it is followed."""
        flow = convert_flow({**FIG_BASE, **interactions({"connectionType": "CLOSE"})})

        assert flow["flow"].destinationArtboardID == BACK_DESTINATION
        assert flow["flow"].overlaySettings is None
        warnings.assert_not_called()

    def test_navigating_to_an_overlay_warns(self, overlay, warnings):
        context.mark_overlay_destination((0, 5))

        flow = convert_flow({**FIG_BASE, **interactions(link((0, 5), navigation="NAVIGATE"))})

        assert flow["flow"].destinationArtboardID == utils.gen_object_id((0, 5))
        assert flow["flow"].overlaySettings is None
        warnings.assert_called_once_with("PRT008", ANY)

    def test_navigating_to_a_screen_does_not_warn(self, overlay, warnings):
        flow = convert_flow({**FIG_BASE, **interactions(link((0, 5), navigation="NAVIGATE"))})

        assert flow["flow"].overlaySettings is None
        warnings.assert_not_called()

    def test_click_leaves_the_trigger_out(self, overlay):
        """Sketch reads a missing trigger as a click."""
        flow = convert_flow({**FIG_BASE, **interactions(link((0, 5)))})["flow"]

        assert flow.interactionTrigger is None
        assert "interactionTrigger" not in convert_object(flow)

    @pytest.mark.parametrize(
        "fig_trigger, trigger",
        [
            ("ON_HOVER", InteractionTrigger.HOVER),
            ("MOUSE_IN", InteractionTrigger.HOVER),
            ("MOUSE_ENTER", InteractionTrigger.HOVER),
            ("ON_PRESS", InteractionTrigger.PRESS),
        ],
    )
    def test_trigger(self, overlay, warnings, fig_trigger, trigger):
        fig_node = {**FIG_BASE, **interactions(link((0, 5)), trigger=fig_trigger)}

        flow = convert_flow(fig_node)["flow"]

        assert flow.destinationArtboardID == utils.gen_object_id((0, 5))
        assert flow.interactionTrigger == trigger
        assert convert_object(flow)["interactionTrigger"] == trigger
        warnings.assert_not_called()

    @pytest.mark.parametrize(
        "fig_trigger",
        ["AFTER_TIMEOUT", "MOUSE_OUT", "MOUSE_LEAVE", "MOUSE_DOWN", "MOUSE_UP", "ON_KEY_DOWN"],
    )
    def test_triggers_sketch_does_not_have_are_dropped(self, overlay, warnings, fig_trigger):
        fig_node = {**FIG_BASE, **interactions(link((0, 5)), trigger=fig_trigger)}

        assert convert_flow(fig_node) == {}
        warnings.assert_called_once_with("PRT001", ANY, props=[fig_trigger])

    def test_click_is_kept_over_an_earlier_hover(self, overlay, warnings):
        """Sketch keeps one link per layer. A click is what moves the prototype between
        screens, so it is kept whichever order the links come in."""
        fig_node = {
            **FIG_BASE,
            "prototypeInteractions": [
                interaction(link((0, 5)), trigger="MOUSE_ENTER"),
                interaction({"connectionType": "BACK"}),
            ],
        }

        flow = convert_flow(fig_node)["flow"]

        assert flow.destinationArtboardID == BACK_DESTINATION
        assert flow.interactionTrigger is None
        warnings.assert_called_once_with("PRT002", ANY)

    @pytest.mark.parametrize("navigation", ["NAVIGATE", "OVERLAY"])
    def test_link_to_a_component_goes_to_its_master(self, component, warnings, navigation):
        """The component's own ID is the symbolID its instances refer to, and no layer
        has it."""
        flow = convert_flow({**FIG_BASE, **interactions(link((0, 25), navigation=navigation))})

        master = symbol.convert(FIG_COMPONENT)
        assert flow["flow"].destinationArtboardID == master.do_objectID
        assert flow["flow"].destinationArtboardID != master.symbolID
        warnings.assert_not_called()

    def test_link_to_a_missing_layer_keeps_its_id(self, component, warnings):
        """drop_invalid_flows removes the link once every page is converted."""
        flow = convert_flow({**FIG_BASE, **interactions(link((9, 9), navigation="NAVIGATE"))})

        assert flow["flow"].destinationArtboardID == utils.gen_object_id((9, 9))
        warnings.assert_not_called()


class TestDropInvalidFlows:
    """Prototype links are converted from the destination's id alone, so a link can
    point at a section, which Sketch refuses as a destination, or at a layer that
    never reached the output. Both are removed once every page is converted."""

    @pytest.fixture(autouse=True)
    def empty_context(self):
        context.init(None, {}, "DISPLAY_P3")

    def _rect(self):
        return Rect(x=0, y=0, width=100, height=100)

    def _group(self, object_id, *, behavior=GroupBehavior.FRAME, layers=None, flow=None):
        return Group(
            do_objectID=object_id,
            frame=self._rect(),
            name=object_id,
            rotation=0,
            style=Style(do_objectID="style"),
            groupBehavior=behavior,
            layers=list(layers or []),
            flow=flow,
        )

    def _page(self, *layers, object_id="page"):
        return Page(
            do_objectID=object_id,
            frame=self._rect(),
            name=object_id,
            rotation=0,
            style=Style(do_objectID="style"),
            layers=list(layers),
        )

    def _flow(self, destination):
        """Registers the link as convert_flow would, so a warning can name its source."""
        flow = FlowConnection(destinationArtboardID=destination, overlaySettings=None)
        context.register_flow({**FIG_BASE, "type": "FRAME"}, flow)
        return flow

    def test_link_to_a_frame_is_kept(self):
        source = self._group("source", flow=self._flow("target"))
        page = self._page(source, self._group("target"))

        drop_invalid_flows([page])

        assert source.flow is not None

    def test_link_to_a_section_is_dropped(self, warnings):
        source = self._group("source", flow=self._flow("target"))
        target = self._group("target", behavior=GroupBehavior.SECTION)
        page = self._page(source, target)

        drop_invalid_flows([page])

        assert source.flow is None
        warnings.assert_called_once_with("PRT006", ANY)

    def test_link_to_a_missing_layer_is_dropped(self, warnings):
        source = self._group("source", flow=self._flow("gone"))
        page = self._page(source)

        drop_invalid_flows([page])

        assert source.flow is None
        warnings.assert_called_once_with("PRT007", ANY)

    def test_link_back_is_kept(self):
        """ "back" names no layer, so it must not be mistaken for a dangling id."""
        source = self._group("source", flow=self._flow(BACK_DESTINATION))
        page = self._page(source)

        drop_invalid_flows([page])

        assert source.flow is not None

    def test_link_to_a_page_is_dropped(self, warnings):
        """A page is not a destination, so naming one is as broken as naming nothing."""
        source = self._group("source", flow=self._flow("page"))
        page = self._page(source)

        drop_invalid_flows([page])

        assert source.flow is None
        warnings.assert_called_once_with("PRT007", ANY)

    def test_nested_layers_are_validated(self, warnings):
        """Both the link and its destination can sit at any depth."""
        source = self._group("source", flow=self._flow("nested_section"))
        section = self._group("nested_section", behavior=GroupBehavior.SECTION)
        page = self._page(
            self._group("outer", layers=[self._group("inner", layers=[source])]),
            self._group("holder", layers=[section]),
        )

        drop_invalid_flows([page])

        assert source.flow is None
        warnings.assert_called_once_with("PRT006", ANY)

    def test_link_to_layer_on_another_page_is_kept(self):
        """Symbols move to the Symbols page while their destinations stay behind, so
        validity is a question about the document rather than about one page."""
        source = self._group("source", flow=self._flow("target"))
        pages = [
            self._page(source, object_id="page"),
            self._page(self._group("target"), object_id="symbols"),
        ]

        drop_invalid_flows(pages)

        assert source.flow is not None

    def test_the_warning_names_the_layer_that_links(self, warnings):
        fig_source = {**FIG_BASE, "type": "FRAME", "guid": (7, 7), "name": "links here"}
        flow = FlowConnection(destinationArtboardID="target", overlaySettings=None)
        context.register_flow(fig_source, flow)
        page = self._page(
            self._group("source", flow=flow),
            self._group("target", behavior=GroupBehavior.SECTION),
        )

        drop_invalid_flows([page])

        warnings.assert_called_once_with("PRT006", fig_source)


def test_convert_flow_records_the_node_the_link_came_from(canvas):
    """Each link is stored in the context next to its fig node as it is converted.

    drop_invalid_flows only runs once every page is done, and by then the link is a
    plain destination id, so it needs this to name the layer it warns about.
    """
    fig_source = {
        **FIG_BASE,
        "guid": (0, 7),
        "prototypeInteractions": [
            {
                "isDeleted": False,
                "event": {"interactionType": "ON_CLICK"},
                "actions": [
                    {
                        "navigationType": "NAVIGATE",
                        "connectionType": "INTERNAL_NODE",
                        "transitionNodeID": (0, 2),
                        "transitionType": "INSTANT_TRANSITION",
                    }
                ],
            }
        ],
    }

    flow = convert_flow(fig_source)["flow"]

    assert (fig_source, flow) in context.flows()


FIG_PROMOTED_TARGET = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 10),
    "resizeToFit": False,
    "parent": {"guid": (0, 12)},
    "children": [
        {
            **FIG_BASE,
            "type": "SECTION",
            "guid": (0, 11),
            "parent": {"guid": (0, 10)},
            "children": [],
        }
    ],
}

FIG_PROMOTED_SOURCE = {
    **FIG_BASE,
    "type": "FRAME",
    "guid": (0, 13),
    "resizeToFit": False,
    "parent": {"guid": (0, 12)},
    "children": [],
    "prototypeInteractions": [
        {
            "isDeleted": False,
            "event": {"interactionType": "ON_CLICK"},
            "actions": [
                {
                    "navigationType": "NAVIGATE",
                    "connectionType": "INTERNAL_NODE",
                    "transitionNodeID": (0, 10),
                    "transitionType": "INSTANT_TRANSITION",
                }
            ],
        }
    ],
}

FIG_PROMOTED_CANVAS = {
    **FIG_BASE,
    "type": "CANVAS",
    "guid": (0, 12),
    "resizeToFit": False,
    "children": [FIG_PROMOTED_TARGET, FIG_PROMOTED_SOURCE],
}


def test_link_to_a_promoted_frame_is_dropped(warnings):
    """The case this pass exists for: the destination was a frame in the fig file and
    became a section because it holds one, which Sketch cannot navigate to."""
    context.init(
        None,
        {
            (0, 12): FIG_PROMOTED_CANVAS,
            (0, 10): FIG_PROMOTED_TARGET,
            (0, 11): FIG_PROMOTED_TARGET["children"][0],
            (0, 13): FIG_PROMOTED_SOURCE,
        },
        "DISPLAY_P3",
    )
    tree.mark_promoted_sections(FIG_PROMOTED_CANVAS)
    page = tree.convert_node(FIG_PROMOTED_CANVAS, "DOCUMENT")
    source = page.layers[1]

    assert source.flow is not None

    drop_invalid_flows([page])

    assert source.flow is None
    warnings.assert_any_call("PRT006", FIG_PROMOTED_SOURCE)
