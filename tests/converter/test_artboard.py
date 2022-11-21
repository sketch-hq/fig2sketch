from .base import *
from converter import prototype, tree
from converter.positioning import Matrix
from sketchformat.layer_common import ClippingMaskMode
from sketchformat.style import *
import pytest
from unittest.mock import ANY

FIG_ARTBOARD = {
    **FIG_BASE,
    "type": "FRAME",
    "resizeToFit": False,
    "children": [],
}


@pytest.fixture
def no_prototyping(monkeypatch):
    monkeypatch.setattr(prototype, "prototyping_information", lambda _: {})


@pytest.mark.usefixtures("no_prototyping")
class TestArtboardBackgroud:
    def test_no_background(self):
        ab = tree.convert_node(FIG_ARTBOARD, "CANVAS")

        assert ab.hasBackgroundColor == False

    def test_simple_background(self):
        ab = tree.convert_node(
            {
                **FIG_ARTBOARD,
                "fillPaints": [
                    {
                        "type": "SOLID",
                        "color": FIG_COLOR[0],
                        "opacity": 0.9,
                        "visible": True,
                    }
                ],
            },
            "CANVAS",
        )

        print(ab)
        assert ab.hasBackgroundColor == True
        assert ab.backgroundColor == SKETCH_COLOR[0]

    def test_gradient_background(self, warnings):
        ab = tree.convert_node(
            {
                **FIG_ARTBOARD,
                "fillPaints": [
                    {
                        "type": "GRADIENT_LINEAR",
                        "transform": Matrix(
                            [[0.7071, -0.7071, 0.6], [0.7071, 0.7071, -0.1]]
                        ),
                        "stops": [
                            {"color": FIG_COLOR[0], "position": 0},
                            {"color": FIG_COLOR[1], "position": 0.4},
                            {"color": FIG_COLOR[2], "position": 1},
                        ],
                        "visible": True,
                    }
                ],
            },
            "CANVAS",
        )

        assert ab.hasBackgroundColor == False
        assert len(ab.layers) == 1
        bg = ab.layers[0]
        assert len(bg.style.fills) == 1
        assert bg.style.fills[0].fillType == FillType.GRADIENT

        warnings.assert_any_call("ART003", ANY)
