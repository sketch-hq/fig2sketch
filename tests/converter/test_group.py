from .base import *
from converter import group, tree
from sketchformat.layer_common import ClippingMaskMode
from sketchformat.style import *
import copy
from unittest.mock import ANY

FIG_GROUP = {
    **FIG_BASE,
    "type": "FRAME",
    "resizeToFit": True,
    "children": [{**FIG_BASE, "type": "ROUNDED_RECTANGLE"}],
}


class TestFrameStyles:
    def test_no_style(self):
        g = tree.convert_node({**FIG_GROUP, "frameMaskDisabled": True}, "")

        assert len(g.layers) == 1
        assert g.style.fills == []
        assert g.style.borders == []
        assert g.style.blurs == []

    def test_background(self):
        g = tree.convert_node(
            {
                **FIG_GROUP,
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[0],
                        "opacity": 0.9,
                        "visible": True,
                    }
                ],
            },
            "",
        )

        assert len(g.layers) == 2
        assert g.style.fills == []
        assert g.style.borders == []
        assert g.style.blurs == []

        bg = g.layers[0]
        assert len(bg.style.fills) == 1
        assert bg.style.fills[0].fillType == FillType.COLOR
        assert bg.style.fills[0].color == SKETCH_COLOR[0]

        assert bg.style.blurs == []

    def test_fg_blur(self):
        g = tree.convert_node(
            {
                **FIG_GROUP,
                "effects": [
                    {
                        "type": "FOREGROUND_BLUR",
                        "radius": 4,
                    }
                ],
            },
            "",
        )

        assert len(g.layers) == 2  # child, blur
        assert g.style.fills == []
        assert g.style.borders == []
        assert g.style.blurs == []

        blur = g.layers[1]
        assert blur.style.blurs[0].isEnabled
        assert blur.style.blurs[0].type == BlurType.BACKGROUND
        assert blur.style.blurs[0].radius == 2

    def test_bg_blur(self):
        g = tree.convert_node(
            {
                **FIG_GROUP,
                "effects": [
                    {
                        "type": "BACKGROUND_BLUR",
                        "radius": 4,
                    }
                ],
            },
            "",
        )

        assert len(g.layers) == 2  # bg_blur, child
        assert g.style.fills == []
        assert g.style.borders == []
        assert g.style.blurs == []

        blur = g.layers[0]
        assert blur.style.blurs[0].isEnabled
        assert blur.style.blurs[0].type == BlurType.BACKGROUND
        assert blur.style.blurs[0].radius == 2

    def test_shadows(self):
        g = tree.convert_node(
            {
                **FIG_GROUP,
                "effects": [
                    {
                        "type": "DROP_SHADOW",
                        "radius": 4,
                        "spread": 0,
                        "offset": {"x": 1, "y": 3},
                        "color": FIG_COLOR[1],
                        "visible": True,
                    }
                ],
            },
            "",
        )

        assert len(g.layers) == 1  # child
        assert g.style.fills == []
        assert g.style.borders == []
        assert g.style.blurs == []

        assert g.style.shadows == [
            Shadow(blurRadius=4, offsetX=1, offsetY=3, spread=0, color=SKETCH_COLOR[1])
        ]

    def test_inner_shadows_children(self):
        g = tree.convert_node(
            {
                **FIG_GROUP,
                "effects": [
                    {
                        "type": "INNER_SHADOW",
                        "radius": 4,
                        "spread": 0,
                        "offset": {"x": 1, "y": 3},
                        "color": FIG_COLOR[1],
                        "visible": True,
                    }
                ],
            },
            "",
        )

        assert len(g.layers) == 1  # child
        assert g.style.fills == []
        assert g.style.borders == []
        assert g.style.blurs == []

        child = g.layers[0]
        assert child.style.shadows == [
            Shadow(
                blurRadius=4,
                offsetX=1,
                offsetY=3,
                spread=0,
                color=SKETCH_COLOR[1],
                isInnerShadow=True,
            )
        ]

    def test_inner_shadows_background(self):
        g = tree.convert_node(
            {
                **FIG_GROUP,
                "effects": [
                    {
                        "type": "INNER_SHADOW",
                        "radius": 4,
                        "spread": 0,
                        "offset": {"x": 1, "y": 3},
                        "color": FIG_COLOR[1],
                        "visible": True,
                    }
                ],
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[0],
                        "opacity": 0.9,
                        "visible": True,
                    }
                ],
            },
            "",
        )

        assert len(g.layers) == 2  # background, child
        assert g.style.fills == []
        assert g.style.borders == []
        assert g.style.blurs == []

        bg = g.layers[0]
        assert len(bg.style.fills) == 1
        assert bg.style.fills[0].fillType == FillType.COLOR
        assert bg.style.fills[0].color == SKETCH_COLOR[0]

        assert bg.style.shadows == [
            Shadow(
                blurRadius=4,
                offsetX=1,
                offsetY=3,
                spread=0,
                color=SKETCH_COLOR[1],
                isInnerShadow=True,
            )
        ]


class TestResizingConstraints:
    def test_equal_resizing_constraints(self, warnings):
        fig = copy.deepcopy(FIG_GROUP)
        fig["resizeToFit"] = True
        fig["children"].append({**FIG_BASE, "type": "ROUNDED_RECTANGLE"})
        g = tree.convert_node(fig, "")

        assert [g.horizontalSizing, g.verticalSizing] == [
            g.layers[0].horizontalSizing,
            g.layers[0].verticalSizing,
        ]
        assert [g.horizontalSizing, g.verticalSizing] == [
            g.layers[1].horizontalSizing,
            g.layers[1].verticalSizing,
        ]

        warnings.assert_not_called()

    def test_mixed_resizing_constraints(self, warnings):
        fig = copy.deepcopy(FIG_GROUP)
        fig["resizeToFit"] = True
        fig["children"].append(
            {**FIG_BASE, "type": "ROUNDED_RECTANGLE", "horizontalConstraint": "MIN"}
        )
        g = tree.convert_node(fig, "")

        assert [g.horizontalSizing, g.verticalSizing] == [
            g.layers[0].horizontalSizing,
            g.layers[0].verticalSizing,
        ]
        assert [g.horizontalSizing, g.verticalSizing] != [
            g.layers[1].horizontalSizing,
            g.layers[1].verticalSizing,
        ]

        warnings.assert_any_call("GRP002", ANY)
