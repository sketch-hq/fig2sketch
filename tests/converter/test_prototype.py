from .base import *
from converter import tree
from converter.prototype import *
from sketchformat.layer_common import Rect
from sketchformat.layer_group import Group
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
        "DISPLAY_P3",
    )


@pytest.fixture
def overlay(monkeypatch):
    context.init(None, {(0, 5): FIG_OVERLAY}, "DISPLAY_P3")


@pytest.fixture
def manual_overlay(monkeypatch):
    context.init(None, {(0, 6): FIG_MANUAL_OVERLAY}, "DISPLAY_P3")


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
        assert flow["flow"].overlaySettings.overlayType == 0
        assert flow["flow"].overlaySettings.overlayAnchor == Point(0, 0)
        assert flow["flow"].overlaySettings.sourceAnchor == Point(0, 0)
        assert flow["flow"].overlaySettings.offset == Point(19.6, 85.0)


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

    def test_nested_layers_are_reached(self, warnings):
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

    def test_link_to_another_page_is_kept(self):
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


def test_convert_flow_registers_the_link(canvas):
    """The pass that validates links later needs the fig node each one came from."""
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
