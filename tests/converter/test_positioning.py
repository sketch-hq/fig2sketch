import pytest
from converter import positioning
from converter.errors import Fig2SketchWarning
from math import nan


class TestConvert:
    def test_nan(self):
        fig = {
            "transform": positioning.Matrix([[nan, nan, nan], [nan, nan, nan]]),
            "size": {"x": 1, "y": 2},
        }
        with pytest.raises(Fig2SketchWarning) as e:
            positioning.convert(fig)

        assert e.value.code == "POS001"

    def test_0_size(self):
        """Sketch does not support 0-size layers (it crashes), so it must be converted to 0.1 pt

        0.1pt is the minimum which currently works (there are checks that round 0.1 to 0)
        The most common case is a horizontal/vertical line, which this test checks.
        """
        fig = {
            "transform": positioning.Matrix([[1, 0, 90], [0, 1, -50]]),
            "size": {"x": 50, "y": 0},
        }

        pos = positioning.convert(fig)
        assert pos["frame"].height == 0.1
