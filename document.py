import utils


def convert(pages):
    return {
        "_class": "document",
        "do_objectID": utils.gen_object_id(),
        "assets": {
            "_class": "assetCollection",
            "do_objectID": utils.gen_object_id(),
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
            "do_objectID": utils.gen_object_id(),
            "objects": []
        },
        "layerSymbols": {
            "_class": "symbolContainer",
            "do_objectID": utils.gen_object_id(),
            "objects": []
        },
        "layerTextStyles": {
            "_class": "sharedTextStyleContainer",
            "do_objectID": utils.gen_object_id(),
            "objects": []
        },
        "sharedSwatches": {
            "_class": "swatchContainer",
            "do_objectID": utils.gen_object_id(),
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
