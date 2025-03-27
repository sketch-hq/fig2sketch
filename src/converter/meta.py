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
        "version": 164,
        "compatibilityVersion": 99,
        "coeditCompatibilityVersion": 164,
        "app": "com.bohemiancoding.sketch3",
        "autosaved": 0,
        "variant": "NONAPPSTORE",
        "created": {
            "commit": "1899e24f63af087a9dd3c66f73b492b72c27c2c8",
            "appVersion": "2025.1",
            "build": 199630,
            "app": "com.bohemiancoding.sketch3",
            "compatibilityVersion": 99,
            "coeditCompatibilityVersion": 164,
            "version": 164,
            "variant": "NONAPPSTORE",
        },
        "saveHistory": ["NONAPPSTORE.199630"],
        "appVersion": "2025.1",
        "build": 199630,
    }
