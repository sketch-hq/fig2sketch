from converter.rectangle import convert, make_clipping_rect
from .base import FIG_BASE
from sketchformat.layer_common import ClippingMaskMode, Rect
from sketchformat.layer_shape import PointRadiusBehaviour
from sketchformat.style import CornerStyle, StyleCorners


class TestCorners:
    def test_straight_corners(self):
        rect = convert({**FIG_BASE})
        assert rect.style.corners is None
        for p in rect.points:
            assert p.cornerRadius == 0

    def test_round_corners(self):
        rect = convert({**FIG_BASE, "cornerRadius": 5, "rectangleCornerRadiiIndependent": False})
        assert rect.style.corners == StyleCorners(
            radii=[5],
            style=CornerStyle.ROUNDED,
            prefersConcentric=False,
        )
        for p in rect.points:
            assert p.cornerRadius == 5

    def test_uneven_corners(self):
        rect = convert(
            {
                **FIG_BASE,
                "cornerRadius": 10,
                "rectangleTopLeftCornerRadius": 5,
                "rectangleBottomRightCornerRadius": 7,
                "rectangleCornerRadiiIndependent": True,
            }
        )
        assert rect.style.corners == StyleCorners(
            radii=[5, 0, 7, 0],
            style=CornerStyle.ROUNDED,
            prefersConcentric=False,
        )
        assert rect.points[0].cornerRadius == 5
        assert rect.points[1].cornerRadius == 0
        assert rect.points[2].cornerRadius == 7
        assert rect.points[3].cornerRadius == 0

    def test_nonzero_smoothing_marks_shape_as_smooth(self):
        rect = convert(
            {
                **FIG_BASE,
                "cornerRadius": 25,
                "cornerSmoothing": 0.2,
                "rectangleCornerRadiiIndependent": False,
            }
        )

        assert rect.pointRadiusBehaviour == PointRadiusBehaviour.V1_SMOOTH

    def test_float_noise_smoothing_does_not_mark_shape_as_smooth(self):
        rect = convert(
            {
                **FIG_BASE,
                "cornerRadius": 25,
                "cornerSmoothing": 0.0000001,
                "rectangleCornerRadiiIndependent": False,
            }
        )

        assert rect.style.corners.style == CornerStyle.ROUNDED
        assert rect.style.corners.smoothing is None
        assert rect.pointRadiusBehaviour == PointRadiusBehaviour.V1


class TestSyntheticRectangles:
    def test_clipping_rect_preserves_smoothing(self):
        rect = make_clipping_rect(
            {**FIG_BASE, "cornerRadius": 25, "cornerSmoothing": 0.2},
            Rect(height=100, width=200, x=0, y=0),
        )

        assert rect.hasClippingMask
        assert rect.clippingMaskMode == ClippingMaskMode.OUTLINE
        assert rect.style.corners.smoothing == 0.2
        assert rect.style.corners.style == CornerStyle.SMOOTH
        assert rect.pointRadiusBehaviour == PointRadiusBehaviour.V1_SMOOTH
