from email.mime import base
import uuid

import numpy as np


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


def transform_relative_coordinates(item, base_position):
    # 1. Calculate positions relative to parent
    # Calculate relative position
    relative_position = np.array([item['x'],item['y']]) - np.array(base_position['coordinates'])

    # Undo parent's rotation to measure distances in cartesian space
    theta = np.radians(base_position['rotation'])
    c, s = np.cos(theta), np.sin(theta)
    matrix = np.array(((c,-s),(s,c)))

    relative_position = matrix.dot(relative_position)
    
    # 2. Calculate offset in item relative rotation to parent (where the origin is pre-rotation)
    # Vector from rotation center to origin (0,0)
    vco = np.array([item['width'] / 2, item['height'] / 2])

    # Rotation matrix
    theta = np.radians(-item['rotation'] + base_position['rotation'])
    c, s = np.cos(theta), np.sin(theta)
    matrix = np.array(((c,-s),(s,c)))

    # Rotate
    vco_rotated = matrix.dot(vco)

    # Calculate translation of origin
    origin_translation = vco_rotated - vco

    # Return origin coordinates after translation and relative to parent
    return relative_position + origin_translation
