from . import base
from sketchformat.layer_shape import Oval


def convert(fig_ellipse):
    return Oval(**base.base_shape(fig_ellipse))
