from sketchformat.layer_group import Page
from typing import List

def convert(pages: List[Page]) -> dict:
    return {
        'document': {
            'pageListHeight': 200,
            'pageListCollapsed': 0,
            'expandedSymbolPathsInSidebar': [],
            'expandedTextStylePathsInPopover': [],
            'libraryListCollapsed': 0
        },
        **{page.do_objectID: {
            'scrollOrigin': '{1000, 500}',
            'zoomValue': 0.5
        } for page in pages}
    }
