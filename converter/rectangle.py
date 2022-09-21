import style
import utils


def convert(rect, children, parent):
    base_position = utils.get_base_position(parent)
    coordinates = utils.transform_relative_coordinates(rect)

    return {
        "_class": "rectangle",
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
            "height": rect['height'],
            "width": rect['width'],
            "x": coordinates[0] - base_position['coordinates'][0],
            "y": coordinates[1] - base_position['coordinates'][1]
        },
        "isFixedToViewport": False,
        "isFlippedHorizontal": False,
        "isFlippedVertical": False,
        "isLocked": False,
        "isVisible": True,
        "layerListExpandedType": 0,
        "name": rect['name'],
        "nameIsFixed": False,
        "resizingConstraint": 9,
        "resizingType": 0,
        "rotation": rect['rotation'] - base_position['rotation'],
        "shouldBreakMaskChain": False,
        "style": style.convert(rect),
        "edited": False,
        "isClosed": True,
        "pointRadiusBehaviour": 1,
        "points": [
            {
                "_class": "curvePoint",
                "cornerRadius": 0,
                "curveFrom": "{0, 0}",
                "curveMode": 1,
                "curveTo": "{0, 0}",
                "hasCurveFrom": False,
                "hasCurveTo": False,
                "point": "{0, 0}"
            },
            {
                "_class": "curvePoint",
                "cornerRadius": 0,
                "curveFrom": "{1, 0}",
                "curveMode": 1,
                "curveTo": "{1, 0}",
                "hasCurveFrom": False,
                "hasCurveTo": False,
                "point": "{1, 0}"
            },
            {
                "_class": "curvePoint",
                "cornerRadius": 0,
                "curveFrom": "{1, 1}",
                "curveMode": 1,
                "curveTo": "{1, 1}",
                "hasCurveFrom": False,
                "hasCurveTo": False,
                "point": "{1, 1}"
            },
            {
                "_class": "curvePoint",
                "cornerRadius": 0,
                "curveFrom": "{0, 1}",
                "curveMode": 1,
                "curveTo": "{0, 1}",
                "hasCurveFrom": False,
                "hasCurveTo": False,
                "point": "{0, 1}"
            }
        ],
        "fixedRadius": 0,
        "hasConvertedToNewRoundCorners": True
    }
