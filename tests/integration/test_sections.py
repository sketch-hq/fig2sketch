import json
from zipfile import ZipFile

import fig2sketch
import pytest
from sketchformat.layer_group import GroupBehavior


def _convert(tmp_path_factory, *extra_args):
    out_path = f'{tmp_path_factory.mktemp("sections")}/out.sketch'
    args = fig2sketch.parse_args(["tests/data/sections.fig", out_path, "--salt=1234", *extra_args])
    fig2sketch.run(args)

    with ZipFile(out_path) as sketch:
        with sketch.open("document.json") as document_json:
            document = json.load(document_json)

        page_ref = document["pages"][0]["_ref"] + ".json"
        with sketch.open(page_ref) as page_json:
            return json.load(page_json)


@pytest.fixture(scope="module")
def sections_page(tmp_path_factory):
    return _convert(tmp_path_factory, "--import-variants")


@pytest.fixture(scope="module")
def sections_page_without_variants(tmp_path_factory):
    return _convert(tmp_path_factory)


def layer_by_name(parent: dict, name: str) -> dict:
    return next(layer for layer in parent["layers"] if layer["name"] == name)


def test_section_uses_section_behavior(sections_page):
    section = layer_by_name(sections_page, "Section")

    assert section["_class"] == "group"
    assert section["groupBehavior"] == GroupBehavior.SECTION.value


def test_section_keeps_figma_default_styling(sections_page):
    """Figma gives a section a white background and a thin inside stroke, and we keep
    both on the section's own style rather than on a background rect."""
    section = layer_by_name(sections_page, "Section")

    fill = section["style"]["fills"][0]
    assert (fill["color"]["red"], fill["color"]["green"], fill["color"]["blue"]) == (1.0, 1.0, 1.0)

    border = section["style"]["borders"][0]
    assert border["thickness"] == 1.0
    assert border["color"]["alpha"] == pytest.approx(0.1)

    assert section["layers"][0]["name"] != "Frame Background"


def test_variant_sets_hold_their_masters(sections_page):
    section = layer_by_name(sections_page, "Section")
    variant_set = layer_by_name(section, "Component")

    assert [layer["_class"] for layer in variant_set["layers"]] == ["symbolMaster"] * 2


def test_section_converts_without_the_variants_flag(sections_page_without_variants):
    """Sections are not gated, so they convert either way, while the component sets
    stay plain frames with their styling untouched."""
    section = layer_by_name(sections_page_without_variants, "Section")

    assert section["groupBehavior"] == GroupBehavior.SECTION.value

    component = layer_by_name(section, "Component")
    assert component["groupBehavior"] == GroupBehavior.FRAME.value
    assert len(component["style"]["borders"]) == 1
