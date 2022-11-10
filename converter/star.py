from . import base
from sketchformat.layer_shape import Star


def convert(fig_star):
    return Star(
        **base.base_shape(fig_star),
        numberOfPoints=fig_star['count'],
        radius=fig_star['starInnerScale']
    )
