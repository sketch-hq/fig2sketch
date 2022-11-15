from converter.style import *
from sketchformat.style import *

FIG_COLOR = {"r": 1,"g": 0,"b": 0.5,"a": 0.9}
SKETCH_COLOR = Color(red=1, green=0, blue=0.5, alpha=0.9)

class TestConvertColor:
    def test_color(self):
        color = convert_color(FIG_COLOR)
        assert color == SKETCH_COLOR

    def test_opacity(self):
        color = convert_color(FIG_COLOR, 0.3)
        assert color == Color(red=1, green=0, blue=0.5, alpha=0.3)


class TestConvertFill:
    fig_color = {"r": 1,"g": 0,"b": 0.5,"a": 0.9}
    sketch_color = Color(red=1, green=0, blue=0.5, alpha=0.9)

    def test_solid(self):
        fill = convert_fill({}, {
            'type': 'SOLID',
            'color': FIG_COLOR,
            'visible': True,
            'opacity': 0.9
        })
        assert fill.color == SKETCH_COLOR
        assert fill.fillType == FillType.COLOR
