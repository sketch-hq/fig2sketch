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
    # Undo parent's rotation to measure distances in cartesian space
    theta = np.radians(base_position['rotation'])
    c, s = np.cos(theta), np.sin(theta)
    matrix = np.array(((c,-s),(s,c)))

    base_abs = matrix.dot(np.array(base_position['coordinates']))
    item_abs = matrix.dot(np.array([item['x'],item['y']]))

    relative_positions = item_abs - base_abs
    
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
    return relative_positions + origin_translation
