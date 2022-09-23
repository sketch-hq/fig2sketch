from . import positioning, style
import utils


def convert(figma_vector):
    return {
        '_class': 'shapePath',
        'do_objectID': utils.gen_object_id(),
        'booleanOperation': -1,
        'exportOptions': {
            '_class': 'exportOptions',
            'exportFormats': [],
            'includedLayerIds': [],
            'layerOptions': 0,
            'shouldTrim': False
        },
        **positioning.convert(figma_vector),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 0,
        'name': figma_vector.name,
        'nameIsFixed': False,
        'resizingConstraint': 63,
        'resizingType': 0,
        'rotation': 0,
        'shouldBreakMaskChain': False,
        'style': style.convert(figma_vector),
        'edited': True,
        'isClosed': True,
        'pointRadiusBehaviour': 1,
        'points': convert_points(figma_vector),
        "fixedRadius": 0,
        "needsConvertionToNewRoundCorners": False,
        "hasConvertedToNewRoundCorners": True
    }


def convert_points(figma_vector):
    vector_network = figma_vector['vectorNetwork']
    scale = figma_vector['vectorData']['normalizedSize']
    points = {}

    for segment_id in vector_network['regions'][0]['loops'][0]:
        segment = vector_network['segments'][segment_id]

        point1, point2 = process_segment(segment, points, vector_network['vertices'], scale)
        points[segment['start']] = point1
        points[segment['end']] = point2

    return list(points.values())


def process_segment(segment, points, vertices, scale):
    point1 = get_or_create_point(points, segment['start'], vertices, scale)
    point2 = get_or_create_point(points, segment['end'], vertices, scale)

    if segment['tangentStart']['x'] != 0.0 or segment['tangentStart']['y'] != 0.0:
        point1['curveFrom'] = get_curve_point(segment['start'], segment['tangentStart'], vertices,
                                              scale)
        point1['hasCurveFrom'] = True
        point1['curveMode'] = 2  # TODO: Extract mode from vertices when parsing vertices

    if segment['tangentEnd']['x'] != 0.0 or segment['tangentEnd']['y'] != 0.0:
        point2['curveTo'] = get_curve_point(segment['end'], segment['tangentEnd'], vertices, scale)
        point2['hasCurveTo'] = True
        point2['curveMode'] = 2  # TODO: Extract mode from vertices when parsing vertices

    return point1, point2


def get_or_create_point(points, index, vertices, scale):
    if index in points:
        point = points[index]
    else:
        point = {
            '_class': 'curvePoint',
            'cornerRadius': 0,
            'cornerStyle': 0,
            'curveFrom': '{0.0, 0.0}',
            'curveMode': 1,
            'curveTo': '{0.0, 0.0}',
            'hasCurveFrom': False,
            'hasCurveTo': False,
            'point': normalize_point(vertices[index], scale)
        }

    return point


def get_curve_point(point_index, tangent, vertices, scale):
    return normalize_point(add_points(vertices[point_index], tangent), scale)


def add_points(point1, point2):
    return {'x': point1['x'] + point2['x'], 'y': point1['y'] + point2['y']}


def normalize_point(point, scale):
    return f"{{{point['x'] / scale['x']}, {point['y'] / scale['y']}}}"
