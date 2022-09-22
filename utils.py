import uuid

import numpy as np


def gen_object_id():
    return str(uuid.uuid4()).upper()


def apply_transform(item):
    #  Calculate relative position
    relative_position = np.array([item['x'], item['y']])

    # Vector from rotation center to origin (0,0)
    vco = np.array([item['width'] / 2, item['height'] / 2])

    # Rotation matrix
    theta = np.radians(-item['rotation'])
    c, s = np.cos(theta), np.sin(theta)
    matrix = np.array(((c, -s), (s, c)))

    #  Rotate
    vco_rotated = matrix.dot(vco)

    # Calculate translation of origin
    origin_translation = vco_rotated - vco

    # Return origin coordinates after translation and relative to parent
    return relative_position + origin_translation
