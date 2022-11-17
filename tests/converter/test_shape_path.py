from figformat import fig2tree
from converter import tree
from converter.context import context
from sketchformat.layer_shape import ShapePath
from sketchformat.layer_group import ShapeGroup
from sketchformat.style import FillType

def test_complex_vector():
    figtree, id_map = fig2tree.convert_fig('tests/data/vector.fig', None    )
    context.init(None, id_map)
    figpage = figtree['document']['children'][0]
    page = tree.convert_node(figpage, 'DOCUMENT')
    vector = page.layers[0].layers[0]

    assert len(vector.layers) == 7 # 6 color layers + segments
    paths = [l for l in vector.layers if isinstance(l, ShapePath)]
    groups = [l for l in vector.layers if isinstance(l, ShapeGroup)]
    assert len(paths) == 6
    assert len(groups) == 1

    for sp in paths:
        assert sp.isClosed == True
        assert len(sp.style.fills) == 1
        assert sp.style.fills[0].fillType == FillType.COLOR

    assert len(groups[0].style.fills) == 0
    for path in groups[0].layers:
        assert isinstance(sp, ShapePath) == True
