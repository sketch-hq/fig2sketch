from . import base, positioning
import utils
import numpy as np
import dataclasses

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
    }

    if styles:
        obj['style'].set_markers(styles['startMarkerType'], styles['endMarkerType'])

    return obj


def convert_line(figma_line):
    # Shift line by half its width
    vt = np.array([0, -figma_line.strokeWeight / 2])
    vtr = positioning.apply_transform(figma_line, vt)
    figma_line.transform['m02'] += vtr[0]
    figma_line.transform['m12'] += vtr[1]

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
                'cornerStyle': 0,
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
                'cornerStyle': 0,
                'curveFrom': '{1, 0}',
                'curveMode': 1,
                'curveTo': '{1, 0}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{1, 1}'
            }],
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
        point1, point2 = process_segment(figma_vector, vertices, segment, points)
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


def process_segment(figma_vector, vertices, segment, points):
    point1 = get_or_create_point(figma_vector, points, segment['start'], vertices)
    point2 = get_or_create_point(figma_vector, points, segment['end'], vertices)

    if segment['tangentStart']['x'] != 0.0 or segment['tangentStart']['y'] != 0.0:
        vertex1 = vertices[segment['start']]
        point1['hasCurveFrom'] = True
        point1['curveFrom'] = get_point_curve(vertex1, segment['tangentStart'])
        point1['curveMode'] = base.adjust_curve_mode(vertex1, figma_vector['handleMirroring'])

    if segment['tangentEnd']['x'] != 0.0 or segment['tangentEnd']['y'] != 0.0:
        vertex2 = vertices[segment['end']]
        point2['hasCurveTo'] = True
        point2['curveTo'] = get_point_curve(vertex2, segment['tangentEnd'])
        point2['curveMode'] = base.adjust_curve_mode(vertex2, figma_vector['handleMirroring'])

    return point1, point2


def get_or_create_point(figma_vector, points, index, vertices):
    if index in points:
        point = points[index]
    else:
        figma_point = vertices[index]
        point = base.make_point(figma_vector, figma_point['x'], figma_point['y'], figma_point)

    return point


def get_point_curve(figma_point, tangent):
    return utils.point_to_string(utils.add_points(figma_point, tangent))


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
