import json
from zipfile import ZipFile

import fig2sketch
import pytest
from sketchformat.prototype import OverlayBackgroundInteraction, OverlayType, PresentationStyle
from sketchformat.style import LayeringType

OVERLAYS = [
    "Overlay centre",
    "Overlay top right",
    "Overlay manual",
    "Overlay bottom",
    "Overlay defaults",
    "Overlay in section",
]


@pytest.fixture(scope="module")
def overlays_page(tmp_path_factory):
    out_path = f'{tmp_path_factory.mktemp("overlays")}/out.sketch'
    args = fig2sketch.parse_args(["tests/data/prototyping.fig", out_path, "--salt=1234"])
    fig2sketch.run(args)

    with ZipFile(out_path) as sketch:
        with sketch.open("document.json") as document_json:
            document = json.load(document_json)

        for page_ref in document["pages"]:
            with sketch.open(page_ref["_ref"] + ".json") as page_json:
                page = json.load(page_json)
            if page["name"] == "Overlays":
                return page

    raise AssertionError("No Overlays page in the converted document")


def layer_by_name(parent: dict, name: str) -> dict:
    for layer in parent.get("layers", []):
        if layer["name"] == name:
            return layer
        found = layer_by_name(layer, name)
        if found is not None:
            return found

    return None


def flow_of(page: dict, name: str) -> dict:
    return layer_by_name(page, name)["flow"]


@pytest.mark.parametrize("name", OVERLAYS)
def test_frames_opened_as_overlays_are_overlays(overlays_page, name):
    """Including those with every overlay setting at its default, which the fig format
    leaves out, and the one inside a section."""
    frame = layer_by_name(overlays_page, name)

    assert frame["presentationStyle"] == PresentationStyle.OVERLAY


@pytest.mark.parametrize("name", ["Home", "Section screen"])
def test_screens_stay_screens(overlays_page, name):
    frame = layer_by_name(overlays_page, name)

    assert frame["presentationStyle"] == PresentationStyle.SCREEN
    assert frame["isFlowHome"] is True
    assert frame["prototypeViewport"]["name"] == "APPLE_IPHONE_16_WHITE"


def test_close_on_click_outside(overlays_page):
    assert (
        layer_by_name(overlays_page, "Overlay centre")["overlayBackgroundInteraction"]
        == OverlayBackgroundInteraction.CLOSES_OVERLAY
    )
    assert (
        layer_by_name(overlays_page, "Overlay defaults")["overlayBackgroundInteraction"]
        == OverlayBackgroundInteraction.NONE
    )


def test_background_becomes_a_backdrop_fill(overlays_page):
    fills = layer_by_name(overlays_page, "Overlay centre")["style"]["fills"]
    backdrops = [f for f in fills if f.get("layeringType") == LayeringType.BACKDROP]

    assert len(backdrops) == 1
    assert backdrops[0]["color"] == {
        "_class": "color",
        "red": 1.0,
        "green": 0.0,
        "blue": 0.0,
        "alpha": 0.5,
    }


def test_overlays_without_a_background_have_no_backdrop(overlays_page):
    fills = layer_by_name(overlays_page, "Overlay defaults")["style"]["fills"]

    assert all("layeringType" not in f for f in fills)


def test_position_comes_from_the_overlay(overlays_page):
    settings = flow_of(overlays_page, "Open top right")["overlaySettings"]

    assert settings["overlayType"] == OverlayType.ABSOLUTE
    assert settings["overlayAnchor"] == "{1, 0}"


def test_manual_position_is_relative_to_the_link(overlays_page):
    settings = flow_of(overlays_page, "Open manual")["overlaySettings"]

    assert settings["overlayType"] == OverlayType.RELATIVE
    assert settings["sourceAnchor"] == "{0, 0}"
    assert settings["overlayAnchor"] == "{0, 0}"
    assert settings["offset"] == "{20.0, 30.0}"


def test_swap_closes_the_open_overlays(overlays_page):
    flow = flow_of(overlays_page, "Swap to bottom")

    assert (
        flow["destinationArtboardID"]
        == layer_by_name(overlays_page, "Overlay bottom")["do_objectID"]
    )
    assert flow["shouldCloseExistingOverlays"] is True


def test_opening_an_overlay_keeps_the_open_ones(overlays_page):
    assert flow_of(overlays_page, "Open centre")["shouldCloseExistingOverlays"] is False


def test_close_is_a_back_link(overlays_page):
    assert flow_of(overlays_page, "Close")["destinationArtboardID"] == "back"


def test_navigating_to_an_overlay_has_no_overlay_settings(overlays_page):
    flow = flow_of(overlays_page, "Go to centre")

    assert (
        flow["destinationArtboardID"]
        == layer_by_name(overlays_page, "Overlay centre")["do_objectID"]
    )
    assert "overlaySettings" not in flow
