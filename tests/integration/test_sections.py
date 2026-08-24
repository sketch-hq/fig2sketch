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


def test_section_keeps_its_styling(sections_page):
    """A section's styling is preserved as-is, on the section's own style rather than
    on a background rect. The fill and border checked here are the ones a fig section
    carries by default, but nothing about the conversion is specific to them."""
    section = layer_by_name(sections_page, "Section")

    fill = section["style"]["fills"][0]
    assert (fill["color"]["red"], fill["color"]["green"], fill["color"]["blue"]) == (1.0, 1.0, 1.0)

    border = section["style"]["borders"][0]
    assert border["thickness"] == 1.0
    assert border["color"]["alpha"] == pytest.approx(0.1)

    assert section["layers"][0]["name"] != "Frame Background"


def test_variant_set_default_styling_stripped(sections_page):
    """The unstyled component set carries the fig default purple stroke, which Sketch's
    overlay draws itself."""
    section = layer_by_name(sections_page, "Section")
    variant_set = layer_by_name(section, "Component")

    assert variant_set["groupBehavior"] == GroupBehavior.VARIANT_SET.value
    assert variant_set["style"]["borders"] == []


def test_variant_set_custom_styling_kept(sections_page):
    """The styled component set keeps the stroke the user chose."""
    section = layer_by_name(sections_page, "Section")
    variant_set = layer_by_name(section, "Component Styled")

    assert variant_set["groupBehavior"] == GroupBehavior.VARIANT_SET.value

    border = variant_set["style"]["borders"][0]
    assert border["thickness"] == 13.0
    assert border["color"]["red"] == pytest.approx(1.0)


def test_variant_sets_hold_their_masters(sections_page):
    section = layer_by_name(sections_page, "Section")
    variant_set = layer_by_name(section, "Component")

    assert [layer["_class"] for layer in variant_set["layers"]] == ["symbolMaster"] * 2


def test_frames_above_a_variant_set_are_promoted(sections_page):
    """Sketch allows a variant set only on a page or in a section, so the whole chain
    of frames above one becomes sections rather than losing the variant behavior."""
    outer = layer_by_name(sections_page, "Outer section frame")
    inner = layer_by_name(outer, "Inner section frame")

    assert outer["groupBehavior"] == GroupBehavior.SECTION.value
    assert inner["groupBehavior"] == GroupBehavior.SECTION.value

    variant_set = layer_by_name(inner, "Component Styled")
    assert variant_set["groupBehavior"] == GroupBehavior.VARIANT_SET.value


def test_no_promotion_without_the_variants_flag(sections_page_without_variants):
    """With the flag off those frames hold no variant set, so there is nothing to
    make room for and they stay frames."""
    outer = layer_by_name(sections_page_without_variants, "Outer section frame")
    inner = layer_by_name(outer, "Inner section frame")

    assert outer["groupBehavior"] == GroupBehavior.FRAME.value
    assert inner["groupBehavior"] == GroupBehavior.FRAME.value


def test_section_converts_without_the_variants_flag(sections_page_without_variants):
    """Sections are not gated, so they convert either way, while the component sets
    stay plain frames with their styling untouched."""
    section = layer_by_name(sections_page_without_variants, "Section")

    assert section["groupBehavior"] == GroupBehavior.SECTION.value

    component = layer_by_name(section, "Component")
    assert component["groupBehavior"] == GroupBehavior.FRAME.value
    assert len(component["style"]["borders"]) == 1
