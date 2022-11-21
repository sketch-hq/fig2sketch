from converter import positioning
from converter.errors import Fig2SketchWarning
from math import nan
import pytest


def test_nan():
    fig = {
        "transform": positioning.Matrix([[nan, nan, nan], [nan, nan, nan]]),
        "size": {"x": 1, "y": 2},
    }
    with pytest.raises(Fig2SketchWarning) as e:
        positioning.convert(fig)

    assert e.value.code == "POS001"
