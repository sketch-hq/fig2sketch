import json
from zipfile import ZipFile

import fig2sketch
import pytest


@pytest.fixture(scope="module")
def stacks_wrap_doc(tmp_path_factory):
    out_path = f'{tmp_path_factory.mktemp("stacks_wrap")}/out.sketch'
    args = fig2sketch.parse_args(["tests/data/stacks_wrap.fig", out_path, "--salt=1234"])
    fig2sketch.run(args)

    with ZipFile(out_path) as sketch:
        yield sketch


@pytest.fixture(scope="module")
def stacks_wrap_page(stacks_wrap_doc):
    page_name = next(name for name in stacks_wrap_doc.namelist() if name.startswith("pages/"))
    with stacks_wrap_doc.open(page_name) as page_json:
        return json.load(page_json)


def test_stacks_wrap_page_layouts(stacks_wrap_page):
    assert stacks_wrap_page["name"] == "Page 1"
    assert len(stacks_wrap_page["layers"]) == 6

    layers_by_name = {layer["name"]: layer for layer in stacks_wrap_page["layers"]}

    assert layers_by_name["Horizontal wrap top left"]["groupLayout"] == {
        "_class": "MSImmutableFlexGroupLayout",
        "flexDirection": 0,
        "justifyContent": 0,
        "alignItems": 0,
        "allGuttersGap": 4.0,
        "crossAxisGutterGap": 0,
        "wrappingEnabled": True,
        "alignContent": 0,
    }
    assert layers_by_name["Horizontal wrap middle center"]["groupLayout"] == {
        "_class": "MSImmutableFlexGroupLayout",
        "flexDirection": 0,
        "justifyContent": 1,
        "alignItems": 1,
        "allGuttersGap": 4.0,
        "crossAxisGutterGap": 8.0,
        "wrappingEnabled": True,
        "alignContent": 1,
    }
    assert layers_by_name["Horizontal wrap bottom right"]["groupLayout"] == {
        "_class": "MSImmutableFlexGroupLayout",
        "flexDirection": 0,
        "justifyContent": 2,
        "alignItems": 2,
        "allGuttersGap": 4.0,
        "crossAxisGutterGap": 8.0,
        "wrappingEnabled": True,
        "alignContent": 2,
    }

    assert layers_by_name["Vertical top left"]["groupLayout"] == {
        "_class": "MSImmutableFlexGroupLayout",
        "flexDirection": 1,
        "justifyContent": 0,
        "alignItems": 0,
        "allGuttersGap": 8.0,
        "crossAxisGutterGap": 8.0,
        "wrappingEnabled": False,
        "alignContent": 0,
    }
    assert layers_by_name["Vertical middle center"]["groupLayout"] == {
        "_class": "MSImmutableFlexGroupLayout",
        "flexDirection": 1,
        "justifyContent": 1,
        "alignItems": 1,
        "allGuttersGap": 8.0,
        "crossAxisGutterGap": 8.0,
        "wrappingEnabled": False,
        "alignContent": 0,
    }
    assert layers_by_name["Vertical bottom right"]["groupLayout"] == {
        "_class": "MSImmutableFlexGroupLayout",
        "flexDirection": 1,
        "justifyContent": 2,
        "alignItems": 2,
        "allGuttersGap": 8.0,
        "crossAxisGutterGap": 8.0,
        "wrappingEnabled": False,
        "alignContent": 0,
    }
