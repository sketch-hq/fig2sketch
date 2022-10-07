import numpy as np


def convert(figma_item):
    flip, rotation = guess_flip(figma_item)
    coordinates = transform_frame(figma_item)

    return {
        'frame': {
            '_class': 'rect',
            'constrainProportions': False,
            'height': figma_item.size['y'],
            'width': figma_item.size['x'],
            'x': coordinates[0],
            'y': coordinates[1]
        },
        'rotation': rotation,
        'isFlippedHorizontal': flip[0],
        'isFlippedVertical': flip[1],
    }


def transform_frame(item):
    # Calculate relative position
    relative_position = np.array([item.x, item.y])

    # Vector from rotation center to origin (0,0)
    vco = np.array([item.size['x'] / 2, item.size['y'] / 2])

    # Apply rotation to vector
    vco_rotated = apply_transform(item, vco)

    # Calculate translation of origin
    origin_translation = vco_rotated - vco

    # Return origin coordinates after translation and relative to parent
    return relative_position + origin_translation


def apply_transform(item, vector):
    # Rotation/flip matrix
    matrix = np.array((
        (item['transform']['m00'], item['transform']['m01']),
        (item['transform']['m10'], item['transform']['m11'])
    ))

    return matrix.dot(vector)


def guess_flip(figma_item):
    tr = figma_item.transform

    # Use a diagonal with big numbers to check for sign flips, to avoid floating point weirdness
    flip = [False, False]
    if abs(tr['m11']) > 0.1:
        flip[1] = bool(np.sign(tr['m11']) != np.sign(tr['m00']))
    else:
        flip[1] = bool(np.sign(tr['m01']) == np.sign(tr['m10']))

    angle = figma_item.rotation
    if flip[1]:
        angle *= -1

    # It's impossible to know if the user intended a 180º rotation or two flips (H and V).
    # We've got a chance to invert both flips and add 180 to the angle, but we've got to guess
    # We guess that angles between -90 to 90 are OK. Angles of 180 are also OK if there is no flip
    # already applied. This makes sure our output angle is < 90 or that it's 180 with no flips.
    # Note: this heuristic is bound to be wrong a lot of the time, so maybe we can skip it completely
    if 90 < abs(angle) < 179 or (abs(angle) > 179 and flip[1]):
        flip[0] = not flip[0]
        flip[1] = not flip[1]
        angle = (angle + 180) % 360

    return flip, angle

