import numpy as np
import math
from sketchformat.layer_common import Rect


def convert(figma_item):
    flip, rotation = guess_flip(figma_item)
    coordinates = transform_frame(figma_item)

    return {
        'frame': Rect(
            constrainProportions=figma_item.get('proportionsConstrained', False),
            height=figma_item['size']['y'],
            width=figma_item['size']['x'],
            x=coordinates[0],
            y=coordinates[1]
        ),
        'rotation': rotation or 0,
        'isFlippedHorizontal': flip[0],
        'isFlippedVertical': flip[1],
    }


def transform_frame(item):
    # Calculate relative position
    relative_position = item['transform'][:2,2]

    # Vector from rotation center to origin (0,0)
    vco = np.array([item['size']['x'] / 2, item['size']['y'] / 2])

    # Apply rotation to vector
    vco_rotated = apply_transform(item, vco)

    # Calculate translation of origin
    origin_translation = vco_rotated - vco

    # Return origin coordinates after translation and relative to parent
    return relative_position + origin_translation


def apply_transform(item, vector):
    # Rotation/flip matrix
    matrix = item['transform'][:2,:2]

    return matrix.dot(vector)


def guess_flip(figma_item):
    tr = figma_item['transform']

    # Use a diagonal with big numbers to check for sign flips, to avoid floating point weirdness
    flip = [False, False]
    if abs(tr[1,1]) > 0.1:
        flip[1] = bool(np.sign(tr[1,1]) != np.sign(tr[0,0]))
    else:
        flip[1] = bool(np.sign(tr[0,1]) == np.sign(tr[1,0]))

    angle = math.degrees(math.atan2(
        -figma_item['transform'][1,0],
        figma_item['transform'][0,0]
    ))
    if flip[1]:
        angle *= -1

    # It's impossible to know if the user intended a 180º rotation or two flips (H and V).
    # We've got a chance to invert both flips and add 180 to the angle, but we've got to guess
    # We guess that angles between -90 to 90 are OK. Angles of 180 are also OK if there is no flip
    # already applied. This makes sure our output angle is < 90 or that it's 180 with no flips.
    # Note: this heuristic is bound to be wrong lots of times, so maybe we can skip it completely
    if 90 < abs(angle) < 179 or (abs(angle) > 179 and flip[1]):
        flip[0] = not flip[0]
        flip[1] = not flip[1]
        angle = (angle + 180) % 360

    return flip, angle
