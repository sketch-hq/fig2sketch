import pytest
from sketchformat.common import Size
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

    def test_layout_wrap_enabled(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "HORIZONTAL",
                "stackWrap": "WRAP",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.HORIZONTAL,
            wrappingEnabled=True,
            alignContent=FlexJustify.START,
        )

    def test_layout_borders_take_space(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "bordersTakeSpace": True,
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout.bordersAffectLayout is True

    def test_layout_wrap_cross_axis_spacing(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "HORIZONTAL",
                "stackWrap": "WRAP",
                "stackCounterSpacing": 12,
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.HORIZONTAL,
            crossAxisGutterGap=12,
            wrappingEnabled=True,
            alignContent=FlexJustify.START,
        )

    def test_layout_wrap_cross_axis_spacing_nan(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "HORIZONTAL",
                "stackWrap": "WRAP",
                "stackCounterSpacing": float("nan"),
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.HORIZONTAL,
            wrappingEnabled=True,
            alignContent=FlexJustify.START,
        )

    def test_layout_wrap_align_content_center(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "HORIZONTAL",
                "stackWrap": "WRAP",
                "stackCounterAlignItems": "CENTER",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.HORIZONTAL,
            alignItems=FlexAlign.CENTER,
            wrappingEnabled=True,
            alignContent=FlexJustify.CENTER,
        )

    def test_layout_wrap_align_content_end(self):
        sketch_frame = tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "HORIZONTAL",
                "stackWrap": "WRAP",
                "stackCounterAlignItems": "MAX",
                "children": [],
            },
            "CANVAS",
        )

        assert sketch_frame.groupLayout == FlexGroupLayout(
            flexDirection=FlexDirection.HORIZONTAL,
            alignItems=FlexAlign.END,
            wrappingEnabled=True,
            alignContent=FlexJustify.END,
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


@pytest.mark.usefixtures("no_prototyping")
class TestMinMaxSize:
    def _frame(self, **extra):
        return tree.convert_node(
            {
                **FIG_BASE,
                "type": "FRAME",
                "resizeToFit": False,
                "stackMode": "VERTICAL",
                "children": [],
                **extra,
            },
            "CANVAS",
        )

    def test_no_constraints(self):
        # A plain frame without min/max fields defaults to {0, 0}.
        sketch_frame = self._frame()

        assert sketch_frame.minSize == Size(0, 0)
        assert sketch_frame.maxSize == Size(0, 0)

    def test_min_and_max(self):
        sketch_frame = self._frame(
            minSize={"value": {"x": 10, "y": 20}},
            maxSize={"value": {"x": 200, "y": 300}},
        )

        assert sketch_frame.minSize == Size(10, 20)
        assert sketch_frame.maxSize == Size(200, 300)

    def test_min_only(self):
        sketch_frame = self._frame(minSize={"value": {"x": 10, "y": 20}})

        assert sketch_frame.minSize == Size(10, 20)
        assert sketch_frame.maxSize == Size(0, 0)

    def test_max_only(self):
        sketch_frame = self._frame(maxSize={"value": {"x": 200, "y": 300}})

        assert sketch_frame.minSize == Size(0, 0)
        assert sketch_frame.maxSize == Size(200, 300)

    def test_single_axis_min(self):
        # Figma leaves the unset axis at 0 for a minimum.
        sketch_frame = self._frame(minSize={"value": {"x": 10, "y": 0}})

        assert sketch_frame.minSize == Size(10, 0)

    def test_infinite_max_axis_is_zeroed(self):
        # Figma uses Infinity for an unconstrained maximum axis; Sketch expects 0.
        sketch_frame = self._frame(maxSize={"value": {"x": float("inf"), "y": 500}})

        assert sketch_frame.maxSize == Size(0, 500)

    def test_serializes_as_sketch_string(self):
        sketch_frame = self._frame(minSize={"value": {"x": 10, "y": 0}})

        assert sketch_frame.minSize.to_json() == "{10, 0}"
        assert sketch_frame.maxSize.to_json() == "{0, 0}"
