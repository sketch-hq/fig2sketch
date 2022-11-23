from converter.style import *
from sketchformat.style import *
import dataclasses
from .base import *


class TestConvertColor:
    def test_color(self):
        color = convert_color(FIG_COLOR[0])
        assert color == SKETCH_COLOR[0]

    def test_opacity(self):
        color = convert_color(FIG_COLOR[0], 0.3)
        assert color == dataclasses.replace(SKETCH_COLOR[0], alpha=0.3)


class TestConvertFill:
    def test_solid(self):
        fill = convert_fill(
            {},
            {"type": "SOLID", "color": FIG_COLOR[0], "visible": True, "opacity": 0.9},
        )
        assert fill.color == SKETCH_COLOR[0]
        assert fill.fillType == FillType.COLOR

    def test_disabled(self):
        fill = convert_fill(
            {},
            {"type": "SOLID", "color": FIG_COLOR[0], "visible": False, "opacity": 0.9},
        )
        assert fill.isEnabled == False

    def test_image(self):
        fill = convert_fill(
            {},
            {
                "type": "IMAGE",
                "image": {"filename": "abcdef"},
                "visible": True,
                "imageScaleMode": "FIT",
            },
        )
        assert fill.fillType == FillType.PATTERN
        assert fill.isEnabled
        assert fill.image._ref == "images/abcdef"
        assert fill.patternFillType == PatternFillType.FIT

    def test_linear_gradient(self):
        fill = convert_fill(
            {},
            {
                "type": "GRADIENT_LINEAR",
                "transform": Matrix([[0.7071, -0.7071, 0.6], [0.7071, 0.7071, -0.1]]),
                "stops": [
                    {"color": FIG_COLOR[0], "position": 0},
                    {"color": FIG_COLOR[1], "position": 0.4},
                    {"color": FIG_COLOR[2], "position": 1},
                ],
                "visible": True,
            },
        )
        assert fill.fillType == FillType.GRADIENT
        assert fill.isEnabled
        assert fill.gradient.gradientType == GradientType.LINEAR
        assert fill.gradient.to == Point(0.7071135624381276, 0.1414227124876255)
        assert getattr(fill.gradient, "from") == Point(0, 0.8485362749257531)

        assert fill.gradient.stops == [
            GradientStop(color=SKETCH_COLOR[0], position=0),
            GradientStop(color=SKETCH_COLOR[1], position=0.4),
            GradientStop(color=SKETCH_COLOR[2], position=1),
        ]

    def test_radial_gradient(self):
        fill = convert_fill(
            {"size": {"x": 10, "y": 5}},
            {
                "type": "GRADIENT_RADIAL",
                "transform": Matrix([[0.7071, -0.7071, 0.6], [0.7071, 0.7071, -0.1]]),
                "stops": [
                    {"color": FIG_COLOR[0], "position": 0},
                    {"color": FIG_COLOR[1], "position": 0.4},
                    {"color": FIG_COLOR[2], "position": 1},
                ],
                "visible": True,
            },
        )
        assert fill.fillType == FillType.GRADIENT
        assert fill.isEnabled
        assert fill.gradient.gradientType == GradientType.RADIAL
        assert fill.gradient.to == Point(0.7071135624381276, 0.1414227124876255)
        assert getattr(fill.gradient, "from") == Point(0.3535567812190638, 0.4949794937066893)
        assert fill.gradient.elipseLength == 1
        assert fill.gradient.stops == [
            GradientStop(color=SKETCH_COLOR[0], position=0),
            GradientStop(color=SKETCH_COLOR[1], position=0.4),
            GradientStop(color=SKETCH_COLOR[2], position=1),
        ]

    def test_angular_gradient(self):
        fill = convert_fill(
            {"size": {"x": 10, "y": 5}},
            {
                "type": "GRADIENT_ANGULAR",
                "transform": Matrix([[0.7071, -0.7071, 0.6], [0.7071, 0.7071, -0.1]]),
                "stops": [
                    {"color": FIG_COLOR[0], "position": 0},
                    {"color": FIG_COLOR[1], "position": 0.4},
                    {"color": FIG_COLOR[2], "position": 1},
                ],
                "visible": True,
            },
        )
        assert fill.fillType == FillType.GRADIENT
        assert fill.isEnabled
        assert fill.gradient.gradientType == GradientType.ANGULAR
        assert fill.gradient.stops == [
            GradientStop(color=SKETCH_COLOR[0], position=0.875),
            GradientStop(color=SKETCH_COLOR[1], position=0.275),
            GradientStop(color=SKETCH_COLOR[2], position=0.87499),
        ]

    def test_offset_gradient(self):
        """A gradient with the first stop position != 0 or last stop != 1.

        In .fig this is interpreted as stretching that color up to the start, while in
        Sketch this causes the size of the gradient to change. We fix it by adding a fake
        stop at 0. Same for the last position
        """
        fill = convert_fill(
            {"size": {"x": 10, "y": 5}},
            {
                "type": "GRADIENT_RADIAL",
                "transform": Matrix([[0.7071, -0.7071, 0.6], [0.7071, 0.7071, -0.1]]),
                "stops": [
                    {"color": FIG_COLOR[1], "position": 0.4},
                    {"color": FIG_COLOR[2], "position": 0.8},
                ],
                "visible": True,
            },
        )
        assert fill.gradient.stops == [
            GradientStop(color=SKETCH_COLOR[1], position=0),
            GradientStop(color=SKETCH_COLOR[1], position=0.4),
            GradientStop(color=SKETCH_COLOR[2], position=0.8),
            GradientStop(color=SKETCH_COLOR[2], position=1),
        ]


class TestConvertBorder:
    def test_convert_border(self):
        border = convert_border(
            {
                "strokeAlign": "CENTER",
                "strokeWeight": 5,
            },
            {"type": "SOLID", "color": FIG_COLOR[0], "visible": True, "opacity": 0.9},
        )
        assert border.fillType == FillType.COLOR
        assert border.isEnabled
        assert border.color == SKETCH_COLOR[0]
        assert border.thickness == 5
        assert border.position == BorderPosition.CENTER

    def test_disabled_border(self):
        border = convert_border(
            {
                "strokeAlign": "CENTER",
                "strokeWeight": 5,
            },
            {"type": "SOLID", "color": FIG_COLOR[0], "visible": False, "opacity": 0.9},
        )
        assert border.isEnabled == False

    def test_border_gradient(self):
        border = convert_border(
            {
                "size": {"x": 50, "y": 0},
                "strokeAlign": "CENTER",
                "strokeWeight": 1,
            },
            {
                "type": "GRADIENT_RADIAL",
                "transform": Matrix([[1, 0, 0.5], [0, 1, 2]]),
                "stops": [
                    {"color": FIG_COLOR[0], "position": 0},
                    {"color": FIG_COLOR[1], "position": 1},
                ],
                "visible": True,
            },
        )
        assert border.fillType == FillType.GRADIENT
        assert border.isEnabled
        assert border.gradient.gradientType == GradientType.RADIAL
        assert border.gradient.to == Point(0.5, -1.5)
        assert getattr(border.gradient, "from") == Point(0, -1.5)

        # (width+2*stroke) / (height+2*stroke)
        assert border.gradient.elipseLength == 2 / 52


class TestConvertContextSettings:
    def test_blend(self):
        cs = context_settings({"blendMode": "DARKEN", "opacity": 0.7})
        assert cs.blendMode == BlendMode.DARKEN
        assert cs.opacity == 0.7

    def test_pass_through(self):
        cs = context_settings({"blendMode": "NORMAL", "opacity": 0.5})
        assert cs.blendMode == BlendMode.NORMAL
        assert cs.opacity == 0.5

    def test_solid(self):
        cs = context_settings({"blendMode": "NORMAL", "opacity": 1})
        assert cs.blendMode == BlendMode.NORMAL
        assert cs.opacity == 0.99


class TestConvertEffects:
    def test_inner_shadow(self):
        effects = convert_effects(
            {
                "effects": [
                    {
                        "type": "INNER_SHADOW",
                        "radius": 5,
                        "offset": {"x": 3, "y": 6},
                        "spread": 2,
                        "color": FIG_COLOR[1],
                    }
                ]
            }
        )
        [shadow] = effects["innerShadows"]
        assert shadow.blurRadius == 5
        assert shadow.offsetX == 3
        assert shadow.offsetY == 6
        assert shadow.spread == 2
        assert shadow.color == SKETCH_COLOR[1]

    def test_shadow(self):
        effects = convert_effects(
            {
                "effects": [
                    {
                        "type": "DROP_SHADOW",
                        "radius": 5,
                        "offset": {"x": 3, "y": 6},
                        "spread": 2,
                        "color": FIG_COLOR[1],
                    }
                ]
            }
        )
        [shadow] = effects["shadows"]
        assert shadow.blurRadius == 5
        assert shadow.offsetX == 3
        assert shadow.offsetY == 6
        assert shadow.spread == 2
        assert shadow.color == SKETCH_COLOR[1]

    def test_blur(self):
        effects = convert_effects(
            {
                "effects": [
                    {
                        "type": "FOREGROUND_BLUR",
                        "radius": 5,
                    }
                ]
            }
        )
        blur = effects["blur"]
        assert blur.isEnabled
        assert blur.type == BlurType.GAUSSIAN
        assert blur.radius == 2.5

    def test_bg_blur(self):
        effects = convert_effects(
            {
                "effects": [
                    {
                        "type": "BACKGROUND_BLUR",
                        "radius": 5,
                    }
                ]
            }
        )
        blur = effects["blur"]
        assert blur.isEnabled
        assert blur.type == BlurType.BACKGROUND
        assert blur.radius == 2.5
