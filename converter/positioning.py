import numpy as np


def convert(figma_item):
    coordinates = apply_transform(figma_item)

    return {
        'frame': {
            '_class': 'rect',
            'constrainProportions': False,
            'height': figma_item.size['y'],
            'width': figma_item.size['x'],
            'x': coordinates[0],
            'y': coordinates[1]
        },
        'rotation': figma_item.rotation
    }


def apply_transform(item):
    # Calculate relative position
    relative_position = np.array([item.x, item.y])

    # Vector from rotation center to origin (0,0)
    vco = np.array([item.size['x'] / 2, item.size['y'] / 2])

    # Rotation matrix
    theta = np.radians(-item.rotation)
    c, s = np.cos(theta), np.sin(theta)
    matrix = np.array(((c, -s), (s, c)))

    # Rotate
    vco_rotated = matrix.dot(vco)

    # Calculate translation of origin
    origin_translation = vco_rotated - vco

    # Return origin coordinates after translation and relative to parent
    return relative_position + origin_translation
