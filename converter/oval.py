from . import base
from sketchformat.layer_shape import Oval


def convert(figma_ellipse):
    return Oval(**base.base_shape(figma_ellipse))
