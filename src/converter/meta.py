from sketchformat.layer_group import AbstractLayerGroup, GroupBehavior, Page, SymbolMaster
from typing import List


def is_frame(layer: object) -> bool:
    """Whether a layer belongs in the pagesAndArtboards index.

    Frames replaced artboards, so this index lists them. Checking groupBehavior
    rather than the type keeps sections and variant sets out, since those carry the
    section trait rather than the frame one.
    """
    return isinstance(layer, AbstractLayerGroup) and layer.groupBehavior == GroupBehavior.FRAME


def convert(pages: List[Page]) -> dict:
    return {
        "commit": "1899e24f63af087a9dd3c66f73b492b72c27c2c8",
        "pagesAndArtboards": {
            page.do_objectID: {
                "name": page.name,
                "artboards": {
                    artboard.do_objectID: {"name": artboard.name}
                    for artboard in page.layers
                    if isinstance(artboard, SymbolMaster) or is_frame(artboard)
                },
            }
            for page in pages
        },
        "version": 196,
        "compatibilityVersion": 99,
        "coeditCompatibilityVersion": 196,
        "app": "com.bohemiancoding.sketch3",
        "autosaved": 0,
        "variant": "NONAPPSTORE",
        "created": {
            "commit": "1899e24f63af087a9dd3c66f73b492b72c27c2c8",
            "appVersion": "2025.1",
            "build": 199630,
            "app": "com.bohemiancoding.sketch3",
            "compatibilityVersion": 99,
            "coeditCompatibilityVersion": 196,
            "version": 196,
            "variant": "NONAPPSTORE",
        },
        "saveHistory": ["NONAPPSTORE.199630"],
        "appVersion": "2025.1",
        "build": 199630,
    }
