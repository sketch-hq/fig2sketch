from .base import *
from converter.prototype import *
from sketchformat.prototype import *
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
        },
    )


@pytest.fixture
def overlay(monkeypatch):
    context.init(None, {(0, 5): FIG_OVERLAY})


@pytest.fixture
def manual_overlay(monkeypatch):
    context.init(None, {(0, 6): FIG_MANUAL_OVERLAY})


@pytest.mark.usefixtures("canvas")
class TestPrototypeInformation:
    def test_no_prototype(self):
        info = prototyping_information(FIG_ARTBOARD_NO_PROTOTYPE)

        assert info["isFlowHome"] is False
        assert info["overlayBackgroundInteraction"] == OverlayBackgroundInteraction.NONE
        assert info["presentationStyle"] == PresentationStyle.SCREEN

    def test_scroll_direction_warning(self, warnings):
        prototyping_information({**FIG_ARTBOARD, "scrollDirection": "HORIZONTAL"})

        warnings.assert_any_call("PRT005", ANY)

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
        assert info["overlaySettings"].overlayType == 0
        assert info["overlaySettings"].overlayAnchor == Point(0.5, 1)
        assert info["overlaySettings"].sourceAnchor == Point(0.5, 1)
        assert info["overlaySettings"].offset == Point(0, 0)


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

        fig_artboard = {**FIG_BASE, **fig_flow}

        flow = convert_flow(fig_artboard)

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

        fig_artboard = {**FIG_BASE, **overlay_flow}

        flow = convert_flow(fig_artboard)

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

        fig_artboard = {**FIG_BASE, **overlay_flow}

        flow = convert_flow(fig_artboard)

        assert flow["flow"].destinationArtboardID == utils.gen_object_id((0, 6))
        assert flow["flow"].animationType == AnimationType.SLIDE_FROM_TOP
        assert flow["flow"].maintainScrollPosition is False
        assert flow["flow"].overlaySettings.overlayType == 0
        assert flow["flow"].overlaySettings.overlayAnchor == Point(0, 0)
        assert flow["flow"].overlaySettings.sourceAnchor == Point(0, 0)
        assert flow["flow"].overlaySettings.offset == Point(19.6, 85.0)
