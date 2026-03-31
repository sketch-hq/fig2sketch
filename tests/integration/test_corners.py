import json
from zipfile import ZipFile

import fig2sketch
import pytest
from sketchformat.layer_shape import PointRadiusBehaviour
from sketchformat.style import CornerStyle


@pytest.fixture(scope="module")
def corners_page(tmp_path_factory):
    out_path = f'{tmp_path_factory.mktemp("corners")}/out.sketch'
    args = fig2sketch.parse_args(["tests/data/corners.fig", out_path, "--salt=1234"])
    fig2sketch.run(args)

    with ZipFile(out_path) as sketch:
        with sketch.open("document.json") as document_json:
            document = json.load(document_json)

        page_ref = document["pages"][0]["_ref"] + ".json"
        with sketch.open(page_ref) as page_json:
            return json.load(page_json)


def layer_by_name(page: dict, name: str) -> dict:
    return next(layer for layer in page["layers"] if layer["name"] == name)


def assert_corners(layer: dict, *, radii, style, smoothing=None) -> None:
    corners = layer["style"]["corners"]
    assert corners["radii"] == radii
    assert corners["style"] == style.value
    if smoothing is None:
        assert "smoothing" not in corners
    else:
        assert corners["smoothing"] == smoothing


def test_corner_fixture_layer_names(corners_page):
    assert [layer["name"] for layer in corners_page["layers"]] == [
        "shape radius=4:8:12:16",
        "shape radius=12, smoothing=1.0",
        "rect radius=4:8:12:16",
        "rect radius=0:12:0:0",
        "rect radius=12, smoothing=0.6",
        "rect radius=12, smoothing=none",
        "frame radius=0:12:0:0",
        "frame radius=4:8:12:16",
        "frame radius=12, smoothing=0.6",
        "frame radius=12, smoothing=none",
    ]


def test_shape_mixed_corner_radii(corners_page):
    layer = layer_by_name(corners_page, "shape radius=4:8:12:16")

    assert layer["_class"] == "shapePath"
    assert layer["pointRadiusBehaviour"] == PointRadiusBehaviour.V1.value
    assert [point["cornerRadius"] for point in layer["points"]] == [8.0, 12.0, 16.0, 4.0]
    assert_corners(layer, radii=[8.0, 12.0, 16.0, 4.0], style=CornerStyle.ROUNDED)


def test_shape_uniform_smoothing(corners_page):
    layer = layer_by_name(corners_page, "shape radius=12, smoothing=1.0")

    assert layer["_class"] == "shapePath"
    assert layer["pointRadiusBehaviour"] == PointRadiusBehaviour.V1_SMOOTH.value
    assert [point["cornerRadius"] for point in layer["points"]] == [12.0, 12.0, 12.0, 12.0]
    assert_corners(layer, radii=[12.0], style=CornerStyle.SMOOTH, smoothing=1.0)


def test_rect_mixed_corner_radii(corners_page):
    layer = layer_by_name(corners_page, "rect radius=4:8:12:16")

    assert layer["_class"] == "shapePath"
    assert layer["pointRadiusBehaviour"] == PointRadiusBehaviour.V1.value
    assert [point["cornerRadius"] for point in layer["points"]] == [4.0, 8.0, 12.0, 16.0]
    assert_corners(layer, radii=[4.0, 8.0, 12.0, 16.0], style=CornerStyle.ROUNDED)


def test_rect_single_corner_radius(corners_page):
    layer = layer_by_name(corners_page, "rect radius=0:12:0:0")

    assert layer["_class"] == "shapePath"
    assert layer["pointRadiusBehaviour"] == PointRadiusBehaviour.V1.value
    assert [point["cornerRadius"] for point in layer["points"]] == [0.0, 12.0, 0.0, 0.0]
    assert_corners(layer, radii=[0.0, 12.0, 0.0, 0.0], style=CornerStyle.ROUNDED)


def test_rect_uniform_smoothing(corners_page):
    layer = layer_by_name(corners_page, "rect radius=12, smoothing=0.6")

    assert layer["_class"] == "rectangle"
    assert layer["pointRadiusBehaviour"] == PointRadiusBehaviour.V1_SMOOTH.value
    assert [point["cornerRadius"] for point in layer["points"]] == [12.0, 12.0, 12.0, 12.0]
    assert_corners(layer, radii=[12.0], style=CornerStyle.SMOOTH, smoothing=0.6)


def test_rect_uniform_rounded(corners_page):
    layer = layer_by_name(corners_page, "rect radius=12, smoothing=none")

    assert layer["_class"] == "rectangle"
    assert layer["pointRadiusBehaviour"] == PointRadiusBehaviour.V1.value
    assert [point["cornerRadius"] for point in layer["points"]] == [12.0, 12.0, 12.0, 12.0]
    assert_corners(layer, radii=[12.0], style=CornerStyle.ROUNDED)


def test_frame_single_corner_radius(corners_page):
    layer = layer_by_name(corners_page, "frame radius=0:12:0:0")

    assert layer["_class"] == "group"
    assert_corners(layer, radii=[0.0, 12.0, 0.0, 0.0], style=CornerStyle.ROUNDED)


def test_frame_mixed_corner_radii(corners_page):
    layer = layer_by_name(corners_page, "frame radius=4:8:12:16")

    assert layer["_class"] == "group"
    assert_corners(layer, radii=[4.0, 8.0, 16.0, 12.0], style=CornerStyle.ROUNDED)


def test_frame_uniform_smoothing(corners_page):
    layer = layer_by_name(corners_page, "frame radius=12, smoothing=0.6")

    assert layer["_class"] == "group"
    assert_corners(layer, radii=[12.0], style=CornerStyle.SMOOTH, smoothing=0.6)


def test_frame_uniform_rounded(corners_page):
    layer = layer_by_name(corners_page, "frame radius=12, smoothing=none")

    assert layer["_class"] == "group"
    assert_corners(layer, radii=[12.0], style=CornerStyle.ROUNDED)
