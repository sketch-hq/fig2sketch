import pytest
from sketchformat.layer_common import FlexAlign, FlexDirection, FlexJustify, PaddingSelection
from sketchformat.layer_group import ClippingBehavior, FlexGroupLayout, FreeFormGroupLayout
from .base import *
from converter import tree, frame


@pytest.fixture
def no_prototyping(monkeypatch):
    monkeypatch.setattr(prototype, "prototyping_information", lambda _: {})


@pytest.mark.usefixtures("no_prototyping")
class TestLayout:
    def test_no_layout(self):
        sketch_frame = tree.convert_node(
            {**FIG_BASE, "type": "FRAME", "resizeToFit": False, "children": []},
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FreeFormGroupLayout()

    def test_horizontal_layout(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "HORIZONTAL",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(flexDirection=FlexDirection.HORIZONTAL)

    def test_vertical_layout(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(flexDirection=FlexDirection.VERTICAL)

    def test_layout_spacing(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "stackSpacing": 10,
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.VERTICAL, allGuttersGap=10
        )


@pytest.mark.usefixtures("no_prototyping")
class TestLayoutJustify:
    def test_layout_justify_min(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "stackPrimaryAlignItems": "MIN",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.VERTICAL, justifyContent=FlexJustify.START
        )

    def test_layout_justify_center(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "stackPrimaryAlignItems": "CENTER",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.VERTICAL, justifyContent=FlexJustify.CENTER
        )

    def test_layout_justify_max(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "stackPrimaryAlignItems": "MAX",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.VERTICAL, justifyContent=FlexJustify.END
        )

    def test_layout_justify_space_evenly(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "stackPrimaryAlignItems": "SPACE_EVENLY",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.VERTICAL, justifyContent=FlexJustify.SPACE_BETWEEN
        )


@pytest.mark.usefixtures("no_prototyping")
class TestLayoutAlignment:
    def test_layout_alignment_min(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "stackCounterAlignItems": "MIN",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.VERTICAL, alignItems=FlexAlign.START
        )

    def test_layout_alignment_center(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "stackCounterAlignItems": "CENTER",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.VERTICAL, alignItems=FlexAlign.CENTER
        )

    def test_layout_alignment_max(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "stackCounterAlignItems": "MAX",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.VERTICAL, alignItems=FlexAlign.END
        )

    def test_layout_alignment_not_set(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.VERTICAL, alignItems=FlexAlign.START
        )


@pytest.mark.usefixtures("no_prototyping")
class TestClipping:
    def test_behaviour_default_when_not_set_explicitly(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(flexDirection=FlexDirection.VERTICAL)
        assert sketch_frame.clippingBehavior == ClippingBehavior.DEFAULT

    def test_behaviour_none_when_mask_disabled(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "frameMaskDisabled": True,
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(flexDirection=FlexDirection.VERTICAL)
        assert sketch_frame.clippingBehavior == ClippingBehavior.NONE

    def test_behaviour_default_when_mask_enabled(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "frameMaskDisabled": False,
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(flexDirection=FlexDirection.VERTICAL)
        assert sketch_frame.clippingBehavior == ClippingBehavior.DEFAULT


@pytest.mark.usefixtures("no_prototyping")
class TestPadding:
    def test_padding(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "children": [],
                "stackVerticalPadding": 5,
                "stackPaddingRight": 10,
                "stackPaddingBottom": 15,
                "stackHorizontalPadding": 20,
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(flexDirection=FlexDirection.VERTICAL)
        assert sketch_frame.topPadding == 5
        assert sketch_frame.rightPadding == 10
        assert sketch_frame.bottomPadding == 15
        assert sketch_frame.leftPadding == 20

    def test_asymetrical_padding(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "children": [],
                "stackVerticalPadding": 5,
                "stackPaddingRight": 10,
                "stackPaddingBottom": 15,
                "stackHorizontalPadding": 20,
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(flexDirection=FlexDirection.VERTICAL)
        assert sketch_frame.topPadding == 5
        assert sketch_frame.rightPadding == 10
        assert sketch_frame.bottomPadding == 15
        assert sketch_frame.leftPadding == 20
        assert sketch_frame.paddingSelection == PaddingSelection.INDIVIDUAL

    def test_symetrical_padding(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "children": [],
                "stackVerticalPadding": 5,
                "stackPaddingRight": 10,
                "stackPaddingBottom": 5,
                "stackHorizontalPadding": 10,
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(flexDirection=FlexDirection.VERTICAL)
        assert sketch_frame.topPadding == 5
        assert sketch_frame.rightPadding == 10
        assert sketch_frame.bottomPadding == 5
        assert sketch_frame.leftPadding == 10
        assert sketch_frame.paddingSelection == PaddingSelection.PAIRED
