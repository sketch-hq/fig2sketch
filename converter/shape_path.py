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
        'shouldBreakMaskChain': False,
        'style': style.convert(figma_vector),
        'edited': True,
        'pointRadiusBehaviour': 1,
        **convert_points(figma_vector),
        "fixedRadius": 0,
        "needsConvertionToNewRoundCorners": False,
        "hasConvertedToNewRoundCorners": True
    }


def convert_line(figma_line):
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
        **positioning.convert(figma_line),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 0,
        'name': figma_line.name,
        'nameIsFixed': False,
        'resizingConstraint': 63,
        'resizingType': 0,
        'shouldBreakMaskChain': False,
        'style': style.convert(figma_line),
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
    points = {}
    segments, is_closed = get_segments(vector_network)

    for segment_id in segments:
        segment = vector_network['segments'][segment_id]

        point1, point2 = process_segment(segment, points, vector_network['vertices'])
        points[segment['start']] = point1
        points[segment['end']] = point2

    return {'points': list(points.values()), 'isClosed': is_closed}


def get_segments(vector_network):
    if vector_network['regions']:
        return vector_network['regions'][0]['loops'][0], True
    else:
        return range(len(vector_network['segments'])), False


def process_segment(segment, points, vertices):
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
        point = utils.make_point(vertices[index]['x'], vertices[index]['y'])

    return point


def get_curve_point(point_index, tangent, vertices):
    return utils.point_to_string(utils.add_points(vertices[point_index], tangent))
