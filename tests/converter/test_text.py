import pytest
from .base import *
from converter.text import *
from converter.context import context

TEXT_BASE = {
    **FIG_BASE,
    "type": "TEXT",
    "fontName": {"family": "Roboto", "style": "Normal"},
    "fontSize": 12,
    "textAlignVertical": "CENTER",
    "textAlignHorizontal": "CENTER",
    "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[0], "opacity": 1, "visible": True}],
}

TEXT_PLAIN = {**TEXT_BASE, "textData": {"characters": "plain"}}


def build_emoji_text(chars: str, glyphs: List):
    return {
        **TEXT_BASE,
        "textData": {
            "characters": chars,
            "glyphs": glyphs,
            "styleOverrideTable": [{"styleID": 2, "fillPaints": [{"type": "EMOJI"}]}],
        },
    }


@pytest.fixture
def mock_fonts(monkeypatch):
    monkeypatch.setattr(context, "record_font", lambda _: "Roboto-Normal")


@pytest.mark.usefixtures("mock_fonts")
class TestOverrideStyles:
    def test_plain_text(self):
        text = override_characters_style(TEXT_PLAIN)
        assert len(text) == 1
        assert text[0].location == 0
        assert text[0].length == 5
        attr = text[0].attributes
        # Default attributes from layer
        assert attr.MSAttributedStringFontAttribute == FontDescriptor(
            name="Roboto-Normal", size=12
        )
        assert attr.MSAttributedStringColorAttribute == SKETCH_COLOR[0]

    def test_multi_color_text(self):
        text = override_characters_style(
            {
                **TEXT_BASE,
                "textData": {
                    "characters": "abcdefghijklmnñopqrstuvwxyz",
                    "characterStyleIDs": [0, 0, 0, 1, 1, 1, 2, 2, 2],
                    "styleOverrideTable": [
                        {
                            "styleID": 1,
                            "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[1]}],
                        },
                        {
                            "styleID": 2,
                            "fillPaints": [{"type": "SOLID", "color": FIG_COLOR[2]}],
                        },
                    ],
                },
            }
        )
        assert len(text) == 4
        [c0, c1, c2, c3] = text
        assert c0.location == 0
        assert c0.length == 3
        assert c0.attributes.MSAttributedStringColorAttribute == SKETCH_COLOR[0]

        assert c1.location == 3
        assert c1.length == 3
        assert c1.attributes.MSAttributedStringColorAttribute == SKETCH_COLOR[1]

        assert c2.location == 6
        assert c2.length == 3
        assert c2.attributes.MSAttributedStringColorAttribute == SKETCH_COLOR[2]

        assert c3.location == 9
        assert c3.length == 18
        assert c3.attributes.MSAttributedStringColorAttribute == SKETCH_COLOR[0]

    def test_emoji_text(self):
        chars = "Sketch ❤️ you"
        glyphs = [{"firstCharacter": i, "styleID": 0} for i in range(len(chars))]
        glyphs[7]["styleID"] = 2

        text = override_characters_style(build_emoji_text(chars, glyphs))

        assert len(text) == 3
        [c0, c1, c2] = text
        assert c0.location == 0
        assert c0.length == 7
        assert c0.attributes.MSAttributedStringFontAttribute == FontDescriptor(
            name="Roboto-Normal", size=12
        )

        assert c1.location == 7
        assert c1.length == 1
        assert c1.attributes.MSAttributedStringFontAttribute == FontDescriptor(
            name="AppleColorEmoji", size=9
        )

        assert c2.location == 8
        assert c2.length == 5
        assert c0.attributes.MSAttributedStringFontAttribute == FontDescriptor(
            name="Roboto-Normal", size=12
        )

    def test_multi_code_point_text(self):
        chars = "nice 🏳️‍🌈 flag"
        glyphs = [{"firstCharacter": i, "styleID": 0} for i in range(len(chars))]
        # Multi-codepoint flag is a single glyph
        glyphs[5]["styleID"] = 2
        glyphs.pop(6)
        glyphs.pop(6)
        glyphs.pop(6)

        text = override_characters_style(build_emoji_text(chars, glyphs))

        assert len(text) == 3
        [c0, c1, c2] = text
        assert c0.location == 0
        assert c0.length == 5
        assert c0.attributes.MSAttributedStringFontAttribute == FontDescriptor(
            name="Roboto-Normal", size=12
        )

        assert c1.location == 5
        assert c1.length == 6
        assert c1.attributes.MSAttributedStringFontAttribute == FontDescriptor(
            name="AppleColorEmoji", size=9
        )

        assert c2.location == 11
        assert c2.length == 5
        assert c0.attributes.MSAttributedStringFontAttribute == FontDescriptor(
            name="Roboto-Normal", size=12
        )


@pytest.mark.usefixtures("mock_fonts")
class TestConvert:
    def test_no_kerning(self):
        text = convert(TEXT_PLAIN)

        assert text.style.textStyle.encodedAttributes.kerning is None
        assert text.frame.width == FIG_BASE["size"]["x"]

    def test_zero_kerning(self):
        TEXT_PLAIN["letterSpacing"] = {"units": "PIXELS", "value": 0}
        text = convert(TEXT_PLAIN)

        assert text.style.textStyle.encodedAttributes.kerning is None
        assert text.frame.width == FIG_BASE["size"]["x"]

    def test_kerning_fixed_width(self):
        TEXT_PLAIN["letterSpacing"] = {"units": "PIXELS", "value": 10}
        TEXT_PLAIN["textAutoResize"] = "HEIGHT"

        text = convert(TEXT_PLAIN)

        assert text.style.textStyle.encodedAttributes.kerning == 10
        assert text.frame.width == FIG_BASE["size"]["x"]

    def test_kerning_flexible_width(self):
        TEXT_PLAIN["letterSpacing"] = {"units": "PERCENT", "value": 50}
        TEXT_PLAIN["textAutoResize"] = "WIDTH_AND_HEIGHT"

        text = convert(TEXT_PLAIN)

        assert text.style.textStyle.encodedAttributes.kerning == 6
        assert text.frame.width == FIG_BASE["size"]["x"] + 6
