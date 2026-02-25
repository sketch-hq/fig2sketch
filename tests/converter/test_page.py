from converter import page
from sketchformat.style import Color


class TestAddPageBackground:
    def test_skip_background_fill_when_background_color_is_missing(self):
        sketch_page = page.make_page((0, 1), "Page 1")

        page.add_page_background({"guid": (0, 1)}, sketch_page)

        assert len(sketch_page.style.fills) == 0
        assert len(sketch_page.layers) == 0

    def test_skip_background_fill_for_default_canvas_background_color(self):
        sketch_page = page.make_page((0, 1), "Page 1")
        default_color = page.DEFAULT_CANVAS_BACKGROUND

        page.add_page_background(
            {
                "guid": (0, 1),
                "backgroundColor": {
                    "r": default_color.red,
                    "g": default_color.green,
                    "b": default_color.blue,
                    "a": default_color.alpha,
                },
                "backgroundOpacity": 1,
            },
            sketch_page,
        )

        assert len(sketch_page.style.fills) == 0
        assert len(sketch_page.layers) == 0

    def test_add_background_fill_for_non_default_canvas_background_color(self):
        sketch_page = page.make_page((0, 1), "Page 1")

        page.add_page_background(
            {
                "guid": (0, 1),
                "backgroundColor": {"r": 1, "g": 0, "b": 0, "a": 1},
                "backgroundOpacity": 0.5,
            },
            sketch_page,
        )

        assert len(sketch_page.layers) == 0
        assert len(sketch_page.style.fills) == 1
        assert sketch_page.style.fills[0].color == Color(red=1, green=0, blue=0, alpha=0.5)

    def test_add_background_fill_uses_background_color_alpha_when_opacity_is_omitted(self):
        sketch_page = page.make_page((0, 1), "Page 1")

        page.add_page_background(
            {
                "guid": (0, 1),
                "backgroundColor": {"r": 1, "g": 0, "b": 0, "a": 0.4},
            },
            sketch_page,
        )

        assert len(sketch_page.style.fills) == 1
        assert sketch_page.style.fills[0].color == Color(red=1, green=0, blue=0, alpha=0.4)
