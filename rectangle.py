import uuid
import fsl.transform.affine
import numpy
import math
import style


def gen_uuid():
    return str(uuid.uuid4()).upper()


def convert(rect, children, parent):
    matrix = numpy.array(rect['relativeTransform']+[[0,0,1]])

    origin = numpy.array([rect['width'] / 2, rect['height'] / 2, 1])
    mapped_origin = matrix.dot(origin)

    if parent['type'] == "GROUP":
        parent_coord = (parent['x'], parent['y'])
        parent_rotation = parent['rotation']
    else:
        parent_coord = (0, 0)
        parent_rotation = 0

    return {
        "_class": "rectangle",
        "do_objectID": gen_uuid(),
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
            "x": (mapped_origin - origin)[0] - parent_coord[0],
            "y": (mapped_origin - origin)[1] - parent_coord[1]
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
        "rotation": rect['rotation'] - parent_rotation,
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
