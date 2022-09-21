import uuid


def gen_uuid():
    return str(uuid.uuid4()).upper()


def convert(page, base_position):
    return {
        "_class": "page",
        "do_objectID": gen_uuid(),
        "booleanOperation": -1,
        "clippingMaskMode": 0,
        "exportOptions": {
            "_class": "exportOptions",
            "exportFormats": [],
            "includedLayerIds": [],
            "layerOptions": 0,
            "shouldTrim": False
        },
        "frame": {
            "_class": "rect",
            "constrainProportions": False,
            "height": 300,
            "width": 300,
            "x": 0,
            "y": 0
        },
        "isFixedToViewport": False,
        "isFlippedHorizontal": False,
        "isFlippedVertical": False,
        "isLocked": False,
        "isVisible": True,
        "layerListExpandedType": 0,
        "name": page['name'],
        "nameIsFixed": False,
        "resizingConstraint": 63,
        "resizingType": 0,
        "rotation": 0,
        "shouldBreakMaskChain": False,
        "style": {
            "_class": "style",
            "endDecorationType": 0,
            "miterLimit": 10,
            "startDecorationType": 0,
            "startMarkerType": 0,
            "endMarkerType": 0,
            "windingRule": 1
        },
        "hasClickThrough": True,
        "includeInCloudUpload": True,
        "horizontalRulerData": {
            "_class": "rulerData",
            "base": 0,
            "guides": []
        },
        "verticalRulerData": {
            "_class": "rulerData",
            "base": 0,
            "guides": []
        },
        "grid": {
            "isEnabled": False,
            "gridSize": 8,
            "thickGridTimes": 1,
            "_class": "simpleGrid"
        },
        "groupLayout": {
            "_class": "MSImmutableFreeformGroupLayout"
        },
        "hasClippingMask": False
    }
