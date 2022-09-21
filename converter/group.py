import utils


def convert(group, children, parent):
    base_position = utils.get_base_position(parent)
    coordinates = utils.transform_relative_coordinates(group)

    return {
        "_class": 'group',
        "do_objectID": utils.gen_object_id(),
        "booleanOperation": -1,
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
            "height": group['absoluteRenderBounds']['height'],
            "width": group['absoluteRenderBounds']['width'],
            "x": coordinates[0] - base_position['coordinates'][0],
            "y": coordinates[1] - base_position['coordinates'][1]
        },
        "isFixedToViewport": False,
        "isFlippedHorizontal": False,
        "isFlippedVertical": False,
        "isLocked": False,
        "isVisible": True,
        "layerListExpandedType": 2,
        "name": group['name'],
        "nameIsFixed": False,
        "resizingConstraint": 9,
        "resizingType": 0,
        "rotation": group['rotation'] - base_position['rotation'],
        "shouldBreakMaskChain": True,
        "style": {
            "_class": "style",
            "do_objectID": utils.gen_object_id(),
            "borders": [],
            "borderOptions": {
                "_class": "borderOptions",
                "isEnabled": True,
                "lineCapStyle": 0,
                "lineJoinStyle": 0
            },
            "fills": [],
            "startMarkerType": 0,
            "endMarkerType": 0,
            "miterLimit": 10,
            "windingRule": 0,
            "shadows": [],
            "innerShadows": [],
            "contextSettings": {
                "_class": "graphicsContextSettings",
                "blendMode": 0,
                "opacity": 1
            },
            "colorControls": {
                "_class": "colorControls",
                "isEnabled": True,
                "brightness": 0,
                "contrast": 1,
                "hue": 0,
                "saturation": 1
            }
        },
        "hasClickThrough": False,
        "layers": children
    }
