from . import base
from sketchformat.layer_shape import Star


def convert(figma_star):
    return Star(
        **base.base_shape(figma_star),
        numberOfPoints=figma_star['count'],
        radius=figma_star['starInnerScale']
    )
