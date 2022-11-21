from converter.positioning import Matrix
from sketchformat.style import *
import pytest
from converter import utils
from unittest.mock import create_autospec


FIG_BASE = {
    "size": {"x": 100, "y": 100},
    "guid": (123, 456),
    "name": "thing",
    "transform": Matrix([[1, 0, 0], [0, 1, 0]]),
    "locked": False,
    "visible": True,
    "horizontalConstraint": "SCALE",
    "verticalConstraint": "SCALE",
    "blendMode": "NORMAL",
    "opacity": 1,
}

FIG_COLOR = [
    {"r": 1, "g": 0, "b": 0.5, "a": 0.9},
    {"r": 0, "g": 1, "b": 0.5, "a": 0.7},
    {"r": 0, "g": 0, "b": 1, "a": 1},
]

SKETCH_COLOR = [
    Color(red=1, green=0, blue=0.5, alpha=0.9),
    Color(red=0, green=1, blue=0.5, alpha=0.7),
    Color(red=0, green=0, blue=1, alpha=1),
]


@pytest.fixture
def warnings(monkeypatch):
    mock = create_autospec(utils.log_conversion_warning)
    monkeypatch.setattr(utils, "log_conversion_warning", mock)
    return mock
