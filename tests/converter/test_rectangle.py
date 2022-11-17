from converter.rectangle import convert
from sketchformat.style import *
from .base import FIG_BASE

def test_straight_corners():
    rect = convert({
        **FIG_BASE
    })
    for p in rect.points:
        assert p.cornerRadius == 0

def test_round_corners():
    rect = convert({
        **FIG_BASE,
        'cornerRadius': 5,
        'rectangleCornerRadiiIndependent': False
    })
    for p in rect.points:
        assert p.cornerRadius == 5

def test_uneven_corners():
    rect = convert({
        **FIG_BASE,
        'rectangleTopLeftCornerRadius': 5,
        'rectangleBottomRightCornerRadius': 7,
        'fixedRadius': 10,
        'rectangleCornerRadiiIndependent': True
    })
    assert rect.points[0].cornerRadius == 5
    assert rect.points[1].cornerRadius == 0
    assert rect.points[2].cornerRadius == 7
    assert rect.points[3].cornerRadius == 0
