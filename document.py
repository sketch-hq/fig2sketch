import uuid


def gen_uuid():
    return str(uuid.uuid4()).upper()


def convert(pages):
    return {
        "_class": "document",
        "do_objectID": gen_uuid(),
        "assets": {
            "_class": "assetCollection",
            "do_objectID": gen_uuid(),
            "imageCollection": {
                "_class": "imageCollection",
                "images": {}
            },
            "colorAssets": [],
            "gradientAssets": [],
            "images": [],
            "colors": [],
            "gradients": [],
            "exportPresets": []
        },
        "colorSpace": 0,
        "currentPageIndex": 0,
        "foreignLayerStyles": [],
        "foreignSymbols": [],
        "foreignTextStyles": [],
        "foreignSwatches": [],
        "layerStyles": {
            "_class": "sharedStyleContainer",
            "do_objectID": gen_uuid(),
            "objects": []
        },
        "layerSymbols": {
            "_class": "symbolContainer",
            "do_objectID": gen_uuid(),
            "objects": []
        },
        "layerTextStyles": {
            "_class": "sharedTextStyleContainer",
            "do_objectID": gen_uuid(),
            "objects": []
        },
        "sharedSwatches": {
            "_class": "swatchContainer",
            "do_objectID": gen_uuid(),
            "objects": []
        },
        "fontReferences": [],
        "documentState": {
            "_class": "documentState"
        },
        "pages": [
            {
                "_class": "MSJSONFileReference",
                "_ref_class": "MSImmutablePage",
                "_ref": f"pages/{page['do_objectID']}"
            } for page in pages
        ]
    }
