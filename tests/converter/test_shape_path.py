from figformat import fig2tree
from converter import tree, shape_path
from converter.context import context
from sketchformat.layer_shape import ShapePath
from sketchformat.layer_group import ShapeGroup
from sketchformat.layer_common import BooleanOperation
from sketchformat.style import FillType, MarkerType, WindingRule
from .base import FIG_BASE
from converter.errors import Fig2SketchWarning
import pytest

FIG_VECTOR = {
    **FIG_BASE,
    "type": "VECTOR",
    "strokeCap": "ROUND",
    "cornerRadius": 0,
}


class TestGeometry:
    def test_winding_rule_odd(self):
        fig = {
            **FIG_VECTOR,
            "vectorData": {"styleOverrideTable": [{"styleID": 1, "strokeCap": "ARROW_LINES"}]},
            "vectorNetwork": {
                "regions": [
                    {
                        "windingRule": "ODD",
                        "loops": [[0, 1, 2], [3, 5, 4]],
                        "style": {},
                    }
                ],
                "segments": [
                    {
                        "start": 0,
                        "end": 1,
                        "tangentStart": {"x": 0, "y": 0},
                        "tangentEnd": {"x": 0, "y": 0},
                    },
                    {
                        "start": 1,
                        "end": 2,
                        "tangentStart": {"x": 0, "y": 0},
                        "tangentEnd": {"x": 0, "y": 0},
                    },
                    {
                        "start": 2,
                        "end": 0,
                        "tangentStart": {"x": 0, "y": 0},
                        "tangentEnd": {"x": 0, "y": 0},
                    },
                    {
                        "start": 3,
                        "end": 4,
                        "tangentStart": {"x": 0, "y": 0},
                        "tangentEnd": {"x": 0, "y": 0},
                    },
                    {
                        "start": 4,
                        "end": 5,
                        "tangentStart": {"x": 0, "y": 0},
                        "tangentEnd": {"x": 0, "y": 0},
                    },
                    {
                        "start": 5,
                        "end": 3,
                        "tangentStart": {"x": 0, "y": 0},
                        "tangentEnd": {"x": 0, "y": 0},
                    },
                ],
                "vertices": [
                    {
                        "x": 8.5,
                        "y": 0,
                    },
                    {
                        "x": 24.5,
                        "y": 16,
                    },
                    {
                        "x": 0,
                        "y": 22,
                    },
                    {
                        "x": 10.5,
                        "y": 9,
                    },
                    {
                        "x": 12.5,
                        "y": 14,
                    },
                    {
                        "x": 8.5,
                        "y": 14,
                    },
                ],
            },
        }

        sketch = shape_path.convert(fig)

        assert isinstance(sketch, ShapeGroup) == True
        assert sketch.windingRule == WindingRule.EVEN_ODD
        assert sketch.style.windingRule == WindingRule.EVEN_ODD

        assert len(sketch.layers) == 2
        for sp in sketch.layers:
            assert isinstance(sp, ShapePath) == True
            assert sp.booleanOperation == BooleanOperation.NONE


class TestArrows:
    def test_arrow_override(self):
        fig = {
            **FIG_VECTOR,
            "vectorData": {"styleOverrideTable": [{"styleID": 1, "strokeCap": "ARROW_LINES"}]},
            "vectorNetwork": {
                "regions": [],
                "segments": [
                    {
                        "start": 0,
                        "end": 1,
                        "tangentStart": {"x": 0, "y": 0},
                        "tangentEnd": {"x": 0, "y": 0},
                    }
                ],
                "vertices": [
                    {"x": 0, "y": 0},
                    {"x": 1, "y": 0, "style": {"strokeCap": "ARROW_LINES"}},
                ],
            },
        }

        sp = shape_path.convert(fig)

        assert sp.style.startMarkerType == MarkerType.NONE
        assert sp.style.endMarkerType == MarkerType.OPEN_ARROW


def test_complex_vector():
    figtree, id_map = fig2tree.convert_fig("tests/data/vector.fig", None)
    context.init(None, id_map, "DISPLAY_P3")
    figpage = figtree["document"]["children"][0]
    page = tree.convert_node(figpage, "DOCUMENT")
    vector = page.layers[0].layers[0]

    assert len(vector.layers) == 7  # 6 color layers + segments
    paths = [l for l in vector.layers if isinstance(l, ShapePath)]
    groups = [l for l in vector.layers if isinstance(l, ShapeGroup)]
    assert len(paths) == 6
    assert len(groups) == 1

    # All IDs are unique
    assert len(set([x.do_objectID for x in vector.layers])) == 7
    assert len(set([x.style.do_objectID for x in vector.layers])) == 7

    for sp in paths:
        assert sp.isClosed == True
        assert len(sp.style.fills) == 1
        assert sp.style.fills[0].fillType == FillType.COLOR

    assert len(groups[0].style.fills) == 0
    for path in groups[0].layers:
        assert isinstance(sp, ShapePath) == True


def test_empty_path():
    fig = {
        **FIG_VECTOR,
        "vectorNetwork": {
            "regions": [],
            "segments": [],
            "vertices": [],
        },
    }

    with pytest.raises(Fig2SketchWarning) as e:
        tree.convert_node(fig, "DOCUMENT")

    assert e.value.code == "SHP002"
