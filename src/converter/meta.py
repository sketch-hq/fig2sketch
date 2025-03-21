from sketchformat.layer_group import Page, Frame, SymbolMaster
from typing import List


def convert(pages: List[Page]) -> dict:
    return {
        "commit": "1899e24f63af087a9dd3c66f73b492b72c27c2c8",
        "pagesAndArtboards": {
            page.do_objectID: {
                "name": page.name,
                "artboards": {
                    artboard.do_objectID: {"name": artboard.name}
                    for artboard in page.layers
                    if isinstance(artboard, Frame) or isinstance(artboard, SymbolMaster)
                },
            }
            for page in pages
        },
        "version": 156,
        "compatibilityVersion": 99,
        "coeditCompatibilityVersion": 156,
        "app": "com.bohemiancoding.sketch3",
        "autosaved": 0,
        "variant": "NONAPPSTORE",
        "created": {
            "commit": "1899e24f63af087a9dd3c66f73b492b72c27c2c8",
            "appVersion": "93",
            "build": 155335,
            "app": "com.bohemiancoding.sketch3",
            "compatibilityVersion": 99,
            "coeditCompatibilityVersion": 156,
            "version": 144,
            "variant": "NONAPPSTORE",
        },
        "saveHistory": ["NONAPPSTORE.155335"],
        "appVersion": "93",
        "build": 155335,
    }
