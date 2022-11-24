from converter import user
from sketchformat.layer_group import Page, Rect, Style
from sketchformat.layer_shape import Oval


class TestDefaultViewport:
    def test_small_oval(self):
        p = Page(
            do_objectID="1234",
            frame=Rect(height=0, width=0, x=0, y=0),
            name="page",
            resizingConstraint=0,
            rotation=0,
            style=Style(do_objectID="style"),
            layers=[
                Oval(
                    do_objectID="oval",
                    frame=Rect(height=10, width=10, x=0, y=0),
                    name="oval",
                    resizingConstraint=0,
                    rotation=0,
                    style=Style(do_objectID="style"),
                )
            ],
        )

        view = user.default_viewport(p)

        assert view["zoomValue"] == 72
        assert view["scrollOrigin"].x == 240
        assert view["scrollOrigin"].y == 90

    def test_large_oval(self):
        p = Page(
            do_objectID="1234",
            frame=Rect(height=0, width=0, x=0, y=0),
            name="page",
            resizingConstraint=0,
            rotation=0,
            style=Style(do_objectID="style"),
            layers=[
                Oval(
                    do_objectID="oval",
                    frame=Rect(height=5000, width=10, x=0, y=0),
                    name="oval",
                    resizingConstraint=0,
                    rotation=0,
                    style=Style(do_objectID="style"),
                )
            ],
        )

        view = user.default_viewport(p)

        assert view["zoomValue"] == 0.144
        assert view["scrollOrigin"].x == 599.28
        assert view["scrollOrigin"].y == 90

    def test_empty_page(self):
        p = Page(
            do_objectID="1234",
            frame=Rect(height=0, width=0, x=0, y=0),
            name="page",
            resizingConstraint=0,
            rotation=0,
            style=Style(do_objectID="style"),
            layers=[],
        )

        view = user.default_viewport(p)

        assert view["zoomValue"] == 1
        assert view["scrollOrigin"].x == 0
        assert view["scrollOrigin"].y == 0
