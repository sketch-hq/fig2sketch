from . import base, positioning
from converter import utils
import itertools
from sketchformat.layer_group import ShapeGroup, Group
from sketchformat.layer_shape import ShapePath, CurvePoint, CurveMode
from sketchformat.common import WindingRule, Point
from collections import defaultdict
import copy

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

WINDING_RULE = {
    'NONZERO': WindingRule.NON_ZERO,
    'ODD': WindingRule.EVEN_ODD
}


def convert(fig_vector):
    regions = get_all_segments(fig_vector['vectorNetwork'])
    regions = [convert_region(fig_vector, region, i) for i, region in enumerate(regions)]

    if len(regions) > 1:
        # Ignore positioning for children. TODO: We should probably be building these shapePaths by
        # hand, instead of relying on the generic convert_shape_path function
        for s in regions:
            s.frame.x = 0
            s.frame.y = 0

        obj = Group(**base.base_styled(fig_vector), layers=regions)
        obj.style.fills = []

        return obj
    else:
        return regions[0]


def convert_region(fig_vector, region, region_index=0):
    loops = [convert_shape_path(fig_vector, region['style'], loop, region_index, i) for i, loop in
             enumerate(region['loops'])]

    if len(loops) > 1:
        # Ignore positioning for children.
        for s in loops:
            s.frame.x = 0
            s.frame.y = 0

        obj = ShapeGroup(
            **base.base_styled({**fig_vector, **region['style']}),
            layers=loops,
            windingRule=WINDING_RULE[region['windingRule']],
        )
        obj.do_objectID = utils.gen_object_id(fig_vector['guid'], f"region{region_index}".encode())

        # obj.style.windingRule = obj.windingRule
        return obj
    else:
        return loops[0]


def convert_shape_path(fig_vector, style, segments, region=0, loop=0):
    points, styles = convert_points(fig_vector, segments)

    obj = ShapePath(
        **base.base_shape({**fig_vector, **style}),
        **points,
    )
    obj.do_objectID = utils.gen_object_id(fig_vector['guid'], f"region{region}loop{loop}".encode())

    if styles:
        obj.style.set_markers(styles['startMarkerType'], styles['endMarkerType'])

    return obj


def convert_line(fig_line):
    # Shift line by half its width
    vt = [0, -fig_line['strokeWeight'] / 2, 1]
    vtr = positioning.apply_transform(fig_line, vt)
    fig_line['transform'][0][2] += vtr[0]
    fig_line['transform'][1][2] += vtr[1]

    return ShapePath(
        **base.base_shape(fig_line),
        isClosed=False,
        points=[
            CurvePoint.Straight(Point(0, 0)),
            CurvePoint.Straight(Point(1, 1))
        ]
    )


def convert_points(fig_vector, ordered_segments):
    vertices = fig_vector['vectorNetwork']['vertices']

    is_closed = ordered_segments[0]['start'] == ordered_segments[-1]['end']

    points_style = {}

    if not is_closed:
        first_point = vertices[ordered_segments[0]['start']]
        last_point = vertices[ordered_segments[-1]['end']]
        points_style = points_marker_types(fig_vector, first_point, last_point)

    points = {}
    for segment in ordered_segments:
        point1, point2 = process_segment(fig_vector, vertices, segment, points)
        points[segment['start']] = point1
        points[segment['end']] = point2

    return {'points': list(points.values()), 'isClosed': is_closed}, points_style


def get_all_segments(vector_network):
    unused_segments = set(range(len(vector_network['segments'])))

    def use_segment(i):
        unused_segments.discard(i)
        return i

    regions = [{
        'loops': [reorder_segment_points([
            vector_network['segments'][use_segment(i)] for i in loop
        ]) for loop in region['loops']],
        'style': region['style'],
        'windingRule': region['windingRule']
    } for region in vector_network['regions']]

    if unused_segments:
        regions += [{
            'style': {'fillPaints': []},
            'windingRule': 'NONZERO',
            'loops': reorder_segments([vector_network['segments'][i] for i in unused_segments]),
        }]

    return regions


def swap_segment(segment):
    segment['start'], segment['end'] = segment['end'], segment['start']
    segment['tangentStart'], segment['tangentEnd'] = segment['tangentEnd'], segment['tangentStart']


def reorder_segments(segments):
    """
    Order segments so that they are continuous

    The input can be in an arbitrary order. This function will try to put the
    segments in order such as seg[n].end == seg[n+1].start.
    """
    # Track which segments are still unordered and start/end on a given point
    segments_with_point = defaultdict(list)
    for s in segments:
        segments_with_point[s['start']].append(s)
        segments_with_point[s['end']].append(s)

    total_segments = len(segments)
    count = 0
    runs = []
    while count < total_segments:
        ordered_run, run_count = reorder_single_segment(segments_with_point)
        count += run_count
        runs.append(ordered_run)

    return runs


def reorder_single_segment(segments_with_point):
    # In case the path is open, we try to find an end (a point with a single segment)
    # If we don't, the path should be closed and can choose an arbitrary one by default
    start_segment = [s[0] for s in segments_with_point.values() if s][0]
    for v in segments_with_point.values():
        if len(v) == 1:
            start_segment = v[0]
            break

    # Start with this segment and remove it from consideration
    ordered = [start_segment]
    segments_with_point[start_segment['start']].remove(start_segment)
    segments_with_point[start_segment['end']].remove(start_segment)

    # See if we will be able to continue, if not, swap the start segment
    if not segments_with_point[start_segment['end']]:
        swap_segment(start_segment)

    # Loop until we walked through all the segments or we close the loop
    start_point = ordered[0]['start']
    count = 1
    while ordered[-1]['end'] != start_point:
        ss = segments_with_point[ordered[-1]['end']]
        # We should get a single candidate segment for a given point.
        if len(ss) == 0:
            # Cannot continue (open path ends)
            break

        # Remove the segment from future consideration
        segment = ss[0]
        segments_with_point[segment['start']].remove(segment)
        segments_with_point[segment['end']].remove(segment)

        # Add the segment to our list, swapping start/end if needed
        if segment['start'] != ordered[-1]['end']:
            swap_segment(segment)

        ordered.append(segment)
        count += 1

    return ordered, count


def reorder_segment_points(segments):
    """
    Make sure segment[0].end == segment[1].start, etc.

    From VectorNetwork docs:
      However, the order of the start and end points in the segments do not matter,
      i.e. the end vertex of one segment does not need to match the start vertex of the next
      segment in the loop, but can instead match the end vertex of that segment.
    """

    # Segments may be reused by other regions in other orders, so let's grab a copy
    segments = copy.deepcopy(segments)

    if len(segments) < 2:
        return segments

    if segments[0]['end'] not in (segments[1]['start'], segments[1]['end']):
        swap_segment(segments[0])

    for prev, cur in itertools.pairwise(segments):
        if prev['end'] != cur['start']:
            swap_segment(cur)

    return segments


def process_segment(fig_vector, vertices, segment, points):
    point1 = get_or_create_point(fig_vector, points, segment['start'], vertices)
    point2 = get_or_create_point(fig_vector, points, segment['end'], vertices)

    if segment['tangentStart']['x'] != 0.0 or segment['tangentStart']['y'] != 0.0:
        vertex1 = vertices[segment['start']]
        point1.hasCurveFrom = True
        point1.curveFrom = Point.from_dict(vertex1) + Point.from_dict(segment['tangentStart'])
        point1.curveMode = CURVE_MODES[
            vertex1.get('style', {}).get('handleMirroring', fig_vector['handleMirroring'])]

    if segment['tangentEnd']['x'] != 0.0 or segment['tangentEnd']['y'] != 0.0:
        vertex2 = vertices[segment['end']]
        point2.hasCurveTo = True
        point2.curveTo = Point.from_dict(vertex2) + Point.from_dict(segment['tangentEnd'])
        point2.curveMode = CURVE_MODES[
            vertex2.get('style', {}).get('handleMirroring', fig_vector['handleMirroring'])]

    return point1, point2


CURVE_MODES = {
    'STRAIGHT': CurveMode.STRAIGHT,
    'ANGLE_AND_LENGTH': CurveMode.MIRRORED,
    'ANGLE': CurveMode.ASYMMETRIC,
    'NONE': CurveMode.DISCONNECTED
}


def get_or_create_point(fig_vector, points, index, vertices):
    if index in points:
        point = points[index]
    else:
        fig_point = vertices[index]
        point = CurvePoint.Straight(Point(fig_point['x'], fig_point['y']))
        point.curveMode = CURVE_MODES[
            fig_point.get('style', {}).get('handleMirroring', 'STRAIGHT')]
        point.cornerRadius = fig_point.get('style', {}).get('cornerRadius',
                                                            fig_vector['cornerRadius'])

    return point


def points_marker_types(fig_vector, start_point, end_point):
    start_marker_type = STROKE_CAP_TO_MARKER_TYPE[fig_vector['strokeCap']]
    end_marker_type = STROKE_CAP_TO_MARKER_TYPE[fig_vector['strokeCap']]

    if ('style' in start_point) and ('strokeCap' in start_point['style']):
        start_marker_type = STROKE_CAP_TO_MARKER_TYPE[start_point['style']['strokeCap']]

    if ('style' in end_point) and ('strokeCap' in end_point['style']):
        end_marker_type = STROKE_CAP_TO_MARKER_TYPE[end_point['style']['strokeCap']]

    if STROKE_CAP_TO_MARKER_TYPE['TRIANGLE_FILLED'] in [start_marker_type, end_marker_type]:
        utils.log_conversion_warning('SHP001', fig_vector)

    return {
        'startMarkerType': start_marker_type,
        'endMarkerType': end_marker_type
    }
