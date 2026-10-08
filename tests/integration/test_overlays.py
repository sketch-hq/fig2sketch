import json
from zipfile import ZipFile

import fig2sketch
import pytest
from sketchformat.prototype import OverlayBackgroundInteraction, OverlayType, PresentationStyle
from sketchformat.style import LayeringType

SCREENS = ["Positions", "Manual", "Behaviours", "Section screen"]

OVERLAYS = [
    "Overlay top left",
    "Overlay top center",
    "Overlay top right",
    "Overlay centered",
    "Overlay bottom left",
    "Overlay bottom center",
    "Overlay bottom right",
    "Overlay manual",
    "Overlay dismissable",
    "Overlay sticky",
    "Overlay swapped",
    "Overlay defaults",
    "Overlay in section",
]

POSITIONS = [
    ("Open top left", "{0, 0}"),
    ("Open top center", "{0.5, 0}"),
    ("Open top right", "{1, 0}"),
    ("Open centered", "{0.5, 0.5}"),
    ("Open bottom left", "{0, 1}"),
    ("Open bottom center", "{0.5, 1}"),
    ("Open bottom right", "{1, 1}"),
    ("Open in section", "{0.5, 0}"),
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


def object_id(page: dict, name: str) -> str:
    return layer_by_name(page, name)["do_objectID"]


@pytest.mark.parametrize("name", OVERLAYS)
def test_frames_opened_as_overlays_are_overlays(overlays_page, name):
    """Including those with every overlay setting at its default, which the fig format
    leaves out, and the one inside a section."""
    frame = layer_by_name(overlays_page, name)

    assert frame["presentationStyle"] == PresentationStyle.OVERLAY
    assert frame["isFlowHome"] is False


@pytest.mark.parametrize("name", SCREENS)
def test_screens_stay_screens(overlays_page, name):
    """The one inside a section included, which keeps the page's device and its own
    starting point."""
    frame = layer_by_name(overlays_page, name)

    assert frame["presentationStyle"] == PresentationStyle.SCREEN
    assert frame["isFlowHome"] is True
    assert frame["prototypeViewport"]["name"] == "APPLE_IPHONE_16_WHITE"


@pytest.mark.parametrize("name, anchor", POSITIONS)
def test_named_positions_anchor_to_the_screen(overlays_page, name, anchor):
    settings = flow_of(overlays_page, name)["overlaySettings"]

    assert settings["overlayType"] == OverlayType.ABSOLUTE
    assert settings["overlayAnchor"] == anchor
    assert settings["offset"] == "{0, 0}"


@pytest.mark.parametrize(
    "name, offset",
    [
        # Below the button, left edges aligned: the button is 40 high
        ("Open manual below", "{0.0, 40.0}"),
        # Above the button, right edges aligned: the button is 80 wide, the overlay
        # 160 x 100
        ("Open manual above", "{-80.0, -100.0}"),
    ],
)
def test_manual_position_is_relative_to_the_link(overlays_page, name, offset):
    """Both links open the same overlay, each at its own spot next to the button."""
    flow = flow_of(overlays_page, name)
    settings = flow["overlaySettings"]

    assert flow["destinationArtboardID"] == object_id(overlays_page, "Overlay manual")
    assert settings["overlayType"] == OverlayType.RELATIVE
    assert settings["sourceAnchor"] == "{0, 0}"
    assert settings["overlayAnchor"] == "{0, 0}"
    assert settings["offset"] == offset


@pytest.mark.parametrize(
    "name, interaction",
    [
        ("Overlay dismissable", OverlayBackgroundInteraction.CLOSES_OVERLAY),
        ("Overlay top left", OverlayBackgroundInteraction.CLOSES_OVERLAY),
        ("Overlay sticky", OverlayBackgroundInteraction.NONE),
        ("Overlay defaults", OverlayBackgroundInteraction.NONE),
    ],
)
def test_close_on_click_outside(overlays_page, name, interaction):
    assert layer_by_name(overlays_page, name)["overlayBackgroundInteraction"] == interaction


def test_background_becomes_a_backdrop_fill(overlays_page):
    fills = layer_by_name(overlays_page, "Overlay dismissable")["style"]["fills"]
    backdrops = [f for f in fills if f.get("layeringType") == LayeringType.BACKDROP]

    assert len(backdrops) == 1
    color = backdrops[0]["color"]
    assert (color["red"], color["green"], color["blue"]) == (0.0, 0.0, 0.0)
    assert color["alpha"] == pytest.approx(0.4)


@pytest.mark.parametrize("name", ["Overlay sticky", "Overlay defaults", "Overlay centered"])
def test_overlays_without_a_background_have_no_backdrop(overlays_page, name):
    fills = layer_by_name(overlays_page, name)["style"]["fills"]

    assert all("layeringType" not in f for f in fills)


def test_swap_closes_the_open_overlays(overlays_page):
    flow = flow_of(overlays_page, "Swap")

    assert flow["destinationArtboardID"] == object_id(overlays_page, "Overlay swapped")
    assert flow["shouldCloseExistingOverlays"] is True
    assert flow["overlaySettings"]["overlayType"] == OverlayType.ABSOLUTE


def test_opening_an_overlay_keeps_the_open_ones(overlays_page):
    assert flow_of(overlays_page, "Open sticky")["shouldCloseExistingOverlays"] is False


@pytest.mark.parametrize("name", ["Close sticky", "Close swapped", "Close defaults"])
def test_close_is_a_back_link(overlays_page, name):
    flow = flow_of(overlays_page, name)

    assert flow["destinationArtboardID"] == "back"
    assert "overlaySettings" not in flow


def test_navigating_to_an_overlay_has_no_overlay_settings(overlays_page):
    flow = flow_of(overlays_page, "Go to dismissable")

    assert flow["destinationArtboardID"] == object_id(overlays_page, "Overlay dismissable")
    assert "overlaySettings" not in flow
