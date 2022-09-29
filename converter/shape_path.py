from . import base, style
import utils

STROKE_CAP_TO_MARKER_TYPE = {
    'NONE': 0,
    'ARROW_LINES': 1,
    'ARROW_EQUILATERAL': 2,
    'TRIANGLE_FILLED': 3,
    'CIRCLE_FILLED': 5,
    'DIAMOND_FILLED': 7,
    'ROUND': 0,
    'SQUARE': 0
}


def convert(figma_vector):
    points, styles = convert_points(figma_vector)

    obj = {
        '_class': 'shapePath',
        **base.base_shape(figma_vector),
        'name': figma_vector.name,
        'edited': True,
        'pointRadiusBehaviour': 1,
        **points,
        "fixedRadius": 0,
        "needsConvertionToNewRoundCorners": False,
        "hasConvertedToNewRoundCorners": True
    }

    obj['style'].update(styles)

    return obj


def convert_line(figma_line):
    return {
        '_class': 'shapePath',
        **base.base_shape(figma_line),
        'name': figma_line.name,
        'edited': True,
        'isClosed': False,
        'pointRadiusBehaviour': 1,
        'points': [
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{0, 0}',
                'curveMode': 1,
                'curveTo': '{0, 0}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{0, 0}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{1, 0}',
                'curveMode': 1,
                'curveTo': '{1, 0}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{1, 1}'
            }],
        "fixedRadius": 0,
        "needsConvertionToNewRoundCorners": False,
        "hasConvertedToNewRoundCorners": True
    }


def convert_points(figma_vector):
    vector_network = figma_vector['vectorNetwork']
    segments = vector_network['segments']
    vertices = vector_network['vertices']

    segment_ids, is_closed = get_segments(vector_network)
    ordered_segments = [segments[i] for i in segment_ids]

    points_style = {}

    if not is_closed:
        first_point = vertices[ordered_segments[0]['start']]
        last_point = vertices[ordered_segments[-1]['end']]
        points_style = points_marker_types(figma_vector, first_point, last_point)

    points = {}

    for segment in ordered_segments:
        point1, point2 = process_segment(vertices, segment, points)
        points[segment['start']] = point1
        points[segment['end']] = point2

    return {'points': list(points.values()), 'isClosed': is_closed}, points_style


def get_segments(vector_network):
    if vector_network['regions']:
        return vector_network['regions'][0]['loops'][0], True
    else:
        segments = vector_network['segments']
        # A polygon is closed if the first point is the same as the last point
        is_closed = segments[0]['start'] == segments[-1]['end']
        return range(len(segments)), is_closed


def process_segment(vertices, segment, points):
    point1 = get_or_create_point(points, segment['start'], vertices)
    point2 = get_or_create_point(points, segment['end'], vertices)

    if segment['tangentStart']['x'] != 0.0 or segment['tangentStart']['y'] != 0.0:
        point1['curveFrom'] = get_curve_point(segment['start'], segment['tangentStart'], vertices)
        point1['hasCurveFrom'] = True
        point1['curveMode'] = 2  # TODO: Extract from vertex['handleMirroring'] once we have it

    if segment['tangentEnd']['x'] != 0.0 or segment['tangentEnd']['y'] != 0.0:
        point2['curveTo'] = get_curve_point(segment['end'], segment['tangentEnd'], vertices)
        point2['hasCurveTo'] = True
        point2['curveMode'] = 2  # TODO: Extract from vertex['handleMirroring'] once we have it

    return point1, point2


def get_or_create_point(points, index, vertices):
    if index in points:
        point = points[index]
    else:
        point = utils.make_point(vertices[index]['x'], vertices[index]['y'], vertices[index])

    return point


def get_curve_point(point_index, tangent, vertices):
    return utils.point_to_string(utils.add_points(vertices[point_index], tangent))


def points_marker_types(figma_vector, start_point, end_point):
    start_marker_type = STROKE_CAP_TO_MARKER_TYPE[figma_vector.strokeCap]
    end_marker_type = STROKE_CAP_TO_MARKER_TYPE[figma_vector.strokeCap]

    if ('style' in start_point) and ('strokeCap' in start_point['style']):
        start_marker_type = STROKE_CAP_TO_MARKER_TYPE[start_point['style']['strokeCap']]

    if ('style' in end_point) and ('strokeCap' in end_point['style']):
        end_marker_type = STROKE_CAP_TO_MARKER_TYPE[end_point['style']['strokeCap']]

    return {
        'startMarkerType': start_marker_type,
        'endMarkerType': end_marker_type
    }
