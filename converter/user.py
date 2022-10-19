def convert(pages):
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
