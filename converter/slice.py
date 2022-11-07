import utils
from . import base, positioning
from sketchformat.layer_common import Slice


def convert(figma_slice):
    # TODO: Rotated slices. Ideally, we should calculate the bounding box of the
    # rotated rectangle and use that as the Sketch frame (and rotation = 0)
    # In any case, nobody should be rotating slices, it does not make sense.

    # Not using base because slices don't have many style/masking properties
    return Slice(
        **base.base_layer(figma_slice),
    )
