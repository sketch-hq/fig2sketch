import uuid


def gen_object_id():
    return str(uuid.uuid4()).upper()


def add_points(point1, point2):
    return {'x': point1['x'] + point2['x'], 'y': point1['y'] + point2['y']}


def point_to_string(point):
    return f"{{{point['x']}, {point['y']}}}"


def resizing_constraints(figma_item):
    # TODO: Figma is returning MIN so I assigned it to the defaults (TOP & LEFT respectively)
    v = {
        'MIN': 32,
        'BOTTOM': 8,
        'CENTER': 16,
        'TOP_BOTTOM': 40,
        'SCALE': 0,
    }
    h = {
        'MIN': 4,
        'RIGHT': 1,
        'CENTER': 2,
        'LEFT_RIGHT': 5,
        'SCALE': 0,
    }
    return h[figma_item['horizontalConstraint']] + v[figma_item['verticalConstraint']]
