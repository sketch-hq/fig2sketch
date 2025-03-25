import pytest
import tempfile
import fig2sketch
from zipfile import ZipFile
import json
from converter import utils
from unittest.mock import ANY
import re


@pytest.fixture(scope="module")
def sketch_doc(tmp_path_factory):
    out_path = f'{tmp_path_factory.mktemp("structure")}/out.sketch'
    args = fig2sketch.parse_args(["tests/data/structure.fig", out_path, "--salt=1234"])
    fig2sketch.run(args)

    with ZipFile(out_path) as sketch:
        yield sketch


def test_user(sketch_doc):
    with sketch_doc.open("user.json") as user_json:
        user = json.load(user_json)
        assert "8F292FCA-49C0-4E31-957E-93FB2D1A7231" in user
        assert "A4E5259A-9CE6-49D9-B4A1-A8062C205347" in user
        assert user["document"] == {
            "expandedSymbolPathsInSidebar": [],
            "expandedTextStylePathsInPopover": [],
            "libraryListCollapsed": 0,
            "pageListCollapsed": 0,
            "pageListHeight": 200,
        }


def test_meta(sketch_doc):
    with sketch_doc.open("meta.json") as meta_json:
        meta = json.load(meta_json)
        assert meta == {
            "commit": "1899e24f63af087a9dd3c66f73b492b72c27c2c8",
            "pagesAndArtboards": {
                "8F292FCA-49C0-4E31-957E-93FB2D1A7231": {
                    "name": "Page 1",
                    "artboards": {
                        "60CDCBD8-345A-4796-804B-C6A97C9C0587": {"name": "Groups"},
                        "B4AC371F-D026-411F-985B-F92A86A928F6": {"name": "Symbols and images"},
                    },
                },
                "A4E5259A-9CE6-49D9-B4A1-A8062C205347": {
                    "name": "Symbols",
                    "artboards": {"FA7E522B-5FF7-4393-AD4D-44C2A82CF837": {"name": "Component 1"}},
                },
            },
            "version": 162,
            "compatibilityVersion": 99,
            "coeditCompatibilityVersion": 162,
            "app": "com.bohemiancoding.sketch3",
            "autosaved": 0,
            "variant": "NONAPPSTORE",
            "created": {
                "commit": "1899e24f63af087a9dd3c66f73b492b72c27c2c8",
                "appVersion": "2025.1",
                "build": 199630,
                "app": "com.bohemiancoding.sketch3",
                "compatibilityVersion": 99,
                "coeditCompatibilityVersion": 162,
                "version": 162,
                "variant": "NONAPPSTORE",
            },
            "saveHistory": ["NONAPPSTORE.199630"],
            "appVersion": "2025.1",
            "build": 199630,
        }


def test_document(sketch_doc):
    with sketch_doc.open("document.json") as doc_json:
        doc = json.load(doc_json)
        assert doc["_class"] == "document"
        assert doc["pages"] == [
            {
                "_class": "MSJSONFileReference",
                "_ref_class": "MSImmutablePage",
                "_ref": "pages/8F292FCA-49C0-4E31-957E-93FB2D1A7231",
            },
            {
                "_class": "MSJSONFileReference",
                "_ref_class": "MSImmutablePage",
                "_ref": "pages/A4E5259A-9CE6-49D9-B4A1-A8062C205347",
            },
        ]
        assert doc["fontReferences"] == [
            {
                "_class": "fontReference",
                "do_objectID": "CC5A46C8-DB4E-4481-A0D9-7F1971488367",
                "fontData": {
                    "_class": "MSJSONFileReference",
                    "_ref_class": "MSFontData",
                    "_ref": "fonts/f0b7cea3f659e72f3ea9285a4d60712878169c07",
                },
                "fontFamilyName": "Inter",
                "fontFileName": "Inter-Regular.ttf",
                "postscriptNames": ["Inter-Regular"],
                "options": 3,
            }
        ]
        assert doc["userInfo"] == {
            "fig2sketch": {"can_detach": True, "salt": "31323334", "version": ANY}
        }

        # Version looks like a version number
        assert re.match(r"\d+\.\d+\.\d+.*", doc["userInfo"]["fig2sketch"]["version"])


@pytest.mark.parametrize(
    "img",
    [
        "images/616d10a80971e08c6b43a164746afac1972c7ccc.png",
        "images/92e4d5e0c24ffd632c3db3264e62cc907c2f5e29",
        "fonts/f0b7cea3f659e72f3ea9285a4d60712878169c07",
    ],
)
def test_file_hashes(sketch_doc, img):
    with sketch_doc.open(img) as data:
        x = utils.generate_file_ref(data.read())
        assert x == img.split(".")[0].split("/")[1]


def test_page(sketch_doc):
    with sketch_doc.open("pages/8F292FCA-49C0-4E31-957E-93FB2D1A7231.json") as page_json:
        page = json.load(page_json)
        assert page["name"] == "Page 1"
        assert len(page["layers"]) == 2
        groups, syms = page["layers"]

        # Groups artboard
        assert groups["_class"] == "group"
        assert groups["name"] == "Groups"
        assert len(groups["layers"]) == 1

        g2 = groups["layers"][0]
        assert g2["_class"] == "group"
        assert len(g2["layers"]) == 2

        g1 = g2["layers"][1]
        assert g1["_class"] == "group"
        assert len(g1["layers"]) == 2

        r = g1["layers"][0]
        assert r["_class"] == "rectangle"
        assert "layers" not in r

        # Symbols artboard
        assert syms["_class"] == "group"
        assert syms["name"] == "Symbols and images"
        i1, i2, i3, jpg, png, svg = syms["layers"]

        # Master instance
        assert i1["_class"] == "symbolInstance"
        assert i1["overrideValues"] == []

        # Instance with text override
        assert i2["_class"] == "symbolInstance"
        assert i2["overrideValues"] == [
            {
                "_class": "overrideValue",
                "overrideName": "659F77C5-AF49-4288-8C6C-C1CE6684C282_stringValue",
                "value": "XYZ",
            }
        ]

        # Instance with color override (detached)
        assert i3["_class"] == "group"
        assert len(i3["layers"]) == 2
        assert i3["layers"][0]["_class"] == "rectangle"
        assert i3["layers"][0]["style"]["fills"][0]["color"] == {
            "_class": "color",
            "alpha": 1.0,
            "blue": 0.0,
            "green": 0.0,
            "red": 1.0,
        }

        # JPG image
        assert jpg["_class"] == "rectangle"
        assert jpg["style"]["fills"][0]["fillType"] == 4
        assert (
            jpg["style"]["fills"][0]["image"]["_ref"]
            == "images/92e4d5e0c24ffd632c3db3264e62cc907c2f5e29"
        )

        # PNG image
        assert png["_class"] == "rectangle"
        assert png["style"]["fills"][0]["fillType"] == 4
        assert (
            png["style"]["fills"][0]["image"]["_ref"]
            == "images/616d10a80971e08c6b43a164746afac1972c7ccc.png"
        )

        # SVG image
        assert svg["_class"] == "group"
        for l in svg["layers"][1:]:
            assert l["_class"] in ["shapePath", "shapeGroup"]


def test_symbols_page(sketch_doc):
    with sketch_doc.open("pages/A4E5259A-9CE6-49D9-B4A1-A8062C205347.json") as page_json:
        page = json.load(page_json)
        assert page["name"] == "Symbols"
        assert len(page["layers"]) == 1

        symbol = page["layers"][0]
        assert symbol["name"] == "Component 1"
        assert symbol["_class"] == "symbolMaster"

        assert len(symbol["layers"]) == 2


def test_files(sketch_doc):
    assert sketch_doc.namelist() == [
        "previews/preview.png",
        "images/616d10a80971e08c6b43a164746afac1972c7ccc.png",
        "images/92e4d5e0c24ffd632c3db3264e62cc907c2f5e29",
        "pages/8F292FCA-49C0-4E31-957E-93FB2D1A7231.json",
        "pages/A4E5259A-9CE6-49D9-B4A1-A8062C205347.json",
        "fonts/f0b7cea3f659e72f3ea9285a4d60712878169c07",
        "document.json",
        "user.json",
        "meta.json",
    ]
