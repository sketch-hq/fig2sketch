from figformat import fig2tree
from converter import tree, shape_path
from converter.context import context
from sketchformat.layer_shape import ShapePath
from sketchformat.layer_group import ShapeGroup
from sketchformat.layer_common import BooleanOperation
from sketchformat.style import FillType, MarkerType, WindingRule
from .base import FIG_BASE, warnings


def test_corrupted_images(warnings):
    figtree, id_map = fig2tree.convert_fig("tests/data/broken_images.fig", None)
    context.init(None, id_map)
    figpage = figtree["document"]["children"][0]
    page = tree.convert_node(figpage, "DOCUMENT")

    assert page.layers[0].layers[0].style.fills[0].image._ref == "images/f2s_missing"
    assert page.layers[0].layers[1].style.fills[0].image._ref == "images/f2s_corrupted"
    warnings.assert_any_call(
        "IMG003",
        {
            "type": "Image",
            "guid": "9c7285aaa9baf5368d9d47f60d521add5fa84567",
            "name": "9c7285aaa9baf5368d9d47f60d521add5fa84567",
        },
    )
    warnings.assert_any_call(
        "IMG001",
        {
            "type": "Image",
            "guid": "ebf82e54d840d6415a9c0aee2d04b472c30d15e9",
            "name": "ebf82e54d840d6415a9c0aee2d04b472c30d15e9",
        },
    )
