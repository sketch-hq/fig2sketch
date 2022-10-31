from . import base, positioning
import utils
import numpy as np
import dataclasses
import logging
import itertools

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
    regions = figma_vector['vectorNetwork']['regions']
    if len(regions) > 1:
        logging.warning("Multi-region shapes are not supported. Only the first region will be converted.")

    if not regions or len(regions[0]['loops']) == 1:
        # A single loop, or just segments. Convert as a shapePath
        return convert_shape_path(figma_vector)
    else:
        # Multiple loops, convert as a shape group with shape paths as children (will happen in post process)
        shape_paths = [convert_shape_path(figma_vector, loop) for loop in range(len(regions[0]['loops']))]

        # Ignore positioning for childs. TODO: We should probably be building these shapePaths by hand, instead
        # of relying on the generic convert_shape_path function
        for i, s in enumerate(shape_paths):
            s['frame']['x'] = 0
            s['frame']['y'] = 0
            s['do_objectID'] = utils.gen_object_id(figma_vector['guid'], f"loop{i}".encode())

        return {
            '_class': 'shapeGroup',
            **base.base_shape(figma_vector),
            'shouldBreakMaskChain': True,
            'hasClickThrough': False,
            'groupLayout': {
                '_class': 'MSImmutableFreeformGroupLayout'
            },
            'windingRule': 0,
            'layers': shape_paths
        }

    return obj


def convert_shape_path(figma_vector, loop=0):
    points, styles = convert_points(figma_vector, loop)

    obj = {
        '_class': 'shapePath',
        **base.base_shape(figma_vector),
        'edited': True,
        'pointRadiusBehaviour': 1,
        **points,
    }

    if styles:
        obj['style'].set_markers(styles['startMarkerType'], styles['endMarkerType'])

    return obj


def convert_line(figma_line):
    # Shift line by half its width
    vt = np.array([0, -figma_line['strokeWeight'] / 2])
    vtr = positioning.apply_transform(figma_line, vt)
    figma_line['transform'][0][2] += vtr[0]
    figma_line['transform'][1][2] += vtr[1]

    return {
        '_class': 'shapePath',
        **base.base_shape(figma_line),
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


def convert_points(figma_vector, loop):
    vector_network = figma_vector['vectorNetwork']
    segments = vector_network['segments']
    vertices = vector_network['vertices']

    segment_ids, is_closed = get_segments(vector_network, loop)
    ordered_segments = [segments[i] for i in segment_ids]

    points_style = {}

    if not is_closed:
        first_point = vertices[ordered_segments[0]['start']]
        last_point = vertices[ordered_segments[-1]['end']]
        points_style = points_marker_types(figma_vector, first_point, last_point)

    # Make sure segment[0].end == segment[1].start, etc.
    # From VectorNetwork docs:
    #   However, the order of the start and end points in the segments do not matter,
    #   i.e. the end vertex of one segment does not need to match the start vertex of the next segment in the loop,
    #   but can instead match the end vertex of that segment."
    reorder_segments(ordered_segments)

    points = {}
    for segment in ordered_segments:
        point1, point2 = process_segment(figma_vector, vertices, segment, points)
        points[segment['start']] = point1
        points[segment['end']] = point2

    return {'points': list(points.values()), 'isClosed': is_closed}, points_style


def get_segments(vector_network, loop):
    if vector_network['regions']:
        return vector_network['regions'][0]['loops'][loop], True
    else:
        segments = vector_network['segments']
        # A polygon is closed if the first point is the same as the last point
        is_closed = segments[0]['start'] == segments[-1]['end']
        return range(len(segments)), is_closed


def swap_segment(segment):
    segment['start'], segment['end'] = segment['end'], segment['start']
    segment['tangentStart'], segment['tangentEnd'] = segment['tangentEnd'], segment['tangentStart']


def reorder_segments(segments):
    if segments[0]['end'] not in (segments[1]['start'], segments[1]['end']):
        swap_segment(segments[0])

    for prev, cur in itertools.pairwise(segments):
        if prev['end'] != cur['start']:
            swap_segment(cur)


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
    start_marker_type = STROKE_CAP_TO_MARKER_TYPE[figma_vector['strokeCap']]
    end_marker_type = STROKE_CAP_TO_MARKER_TYPE[figma_vector['strokeCap']]

    if ('style' in start_point) and ('strokeCap' in start_point['style']):
        start_marker_type = STROKE_CAP_TO_MARKER_TYPE[start_point['style']['strokeCap']]

    if ('style' in end_point) and ('strokeCap' in end_point['style']):
        end_marker_type = STROKE_CAP_TO_MARKER_TYPE[end_point['style']['strokeCap']]

    return {
        'startMarkerType': start_marker_type,
        'endMarkerType': end_marker_type
    }
