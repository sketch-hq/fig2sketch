def convert(pages):
    return {
        "document": {
            "pageListHeight": "200",
            "pageListCollapsed": 0,
            "expandedSymbolPathsInSidebar": [],
            "expandedTextStylePathsInPopover": [],
            "libraryListCollapsed": 0
        },
        **{page['do_objectID']: {
            "scrollOrigin": "{0, 0}",
            "zoomValue": 1
        } for page in pages}
    }
