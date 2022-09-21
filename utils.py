import uuid

import numpy


def gen_object_id():
    return str(uuid.uuid4()).upper()


def get_base_position(item):
    if item['type'] == "GROUP":
        base_coordinates = (item['x'], item['y'])
        base_rotation = item['rotation']
    else:
        base_coordinates = (0, 0)
        base_rotation = 0

    return {'coordinates': base_coordinates, 'rotation': base_rotation}


def transform_relative_coordinates(item):
    matrix = numpy.array(item['relativeTransform'] + [[0, 0, 1]])

    origin = numpy.array([item['width'] / 2, item['height'] / 2, 1])
    mapped_origin = matrix.dot(origin)

    return mapped_origin - origin
