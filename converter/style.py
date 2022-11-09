import numpy as np
import math
import utils
from sketchformat.style import *
from typing import List, TypedDict, Sequence
import numpy.typing as npt


BORDER_POSITION = {
    'CENTER': BorderPosition.CENTER,
    'INSIDE': BorderPosition.INSIDE,
    'OUTSIDE': BorderPosition.OUTSIDE
}

LINE_CAP_STYLE = {
    'NONE': LineCapStyle.BUTT,
    'ROUND': LineCapStyle.ROUND,
    'SQUARE': LineCapStyle.SQUARE,
    'LINE_ARROW': LineCapStyle.SQUARE,
    'ARROW_LINES': LineCapStyle.SQUARE,
    'TRIANGLE_ARROW': LineCapStyle.SQUARE,
    'TRIANGLE_FILLED': LineCapStyle.SQUARE
}

LINE_JOIN_STYLE = {
    'MITER': LineJoinStyle.MITER,
    'ROUND': LineJoinStyle.ROUND,
    'BEVEL': LineJoinStyle.BEVEL
}

PATTERN_FILL_TYPE = {
    'STRETCH': PatternFillType.STRETCH,
    'FIT': PatternFillType.FIT,
    'FILL': PatternFillType.FILL,
    'TILE': PatternFillType.TILE
}

BLEND_MODE = {
    'PASS_THROUGH': BlendMode.NORMAL,
    'NORMAL': BlendMode.NORMAL,
    'DARKEN': BlendMode.DARKEN,
    'MULTIPLY': BlendMode.MULTIPLY,
    # 'LINEAR_BURN': , Cannot be set on Figma
    'COLOR_BURN': BlendMode.COLOR_BURN,
    'LIGHTEN': BlendMode.LIGHTEN,
    'SCREEN': BlendMode.SCREEN,
    # 'LINEAR_DODGE': , Cannot be set on Figma
    'COLOR_DODGE': BlendMode.COLOR_DODGE,
    'OVERLAY': BlendMode.OVERLAY,
    'SOFT_LIGHT': BlendMode.SOFT_LIGHT,
    'HARD_LIGHT': BlendMode.HARD_LIGHT,
    'DIFFERENCE': BlendMode.DIFFERENCE,
    'EXCLUSION': BlendMode.EXCLUSION,
    'HUE': BlendMode.HUE,
    'SATURATION': BlendMode.SATURATION,
    'COLOR': BlendMode.COLOR,
    'LUMINOSITY': BlendMode.LUMINOSITY,
}


def convert(figma_node: dict) -> Style:
    sketch_style = Style(
        do_objectID=utils.gen_object_id(figma_node['guid'], b'style'),
        borderOptions=BorderOptions(
            lineCapStyle=LINE_CAP_STYLE[figma_node['strokeCap']] if 'strokeCap' in figma_node else BorderOptions.__dict__['lineCapStyle'],
            lineJoinStyle=LINE_JOIN_STYLE[figma_node['strokeJoin']] if 'strokeJoin' in figma_node else BorderOptions.__dict__['lineCapStyle'],
            dashPattern=figma_node.get('dashPattern', [])
        ),
        borders=[convert_border(figma_node, b) for b in figma_node['strokePaints']] if 'strokePaints' in figma_node else [],
        fills=[convert_fill(figma_node, f) for f in figma_node['fillPaints']] if 'fillPaints' in figma_node else [],
        **convert_effects(figma_node),
        contextSettings=context_settings(figma_node)
    )
    return sketch_style


def convert_border(figma_node: dict, figma_border: dict) -> Border:
    return Border.from_fill(
        convert_fill(figma_node, figma_border),
        position=BORDER_POSITION[figma_node['strokeAlign']],
        thickness=figma_node['strokeWeight'],
    )


def convert_fill(figma_node: dict, figma_fill: dict) -> Fill:
    match figma_fill:
        case {'type': 'EMOJI'}:
            raise Exception("Unsupported fill: EMOJI")
        case {'type': 'SOLID'}:
            return Fill.Color(convert_color(figma_fill['color'], figma_fill['opacity']),
                              isEnabled=figma_fill['visible'])
        case {'type': 'IMAGE'}:
            return Fill.Image(
                f'images/{figma_fill["image"]["filename"]}',
                patternFillType=PATTERN_FILL_TYPE[figma_fill['imageScaleMode']],
                patternTileScale=figma_fill.get('scale', 1),
                isEnabled=figma_fill['visible']
            )
        case _:
            return Fill.Gradient(convert_gradient(figma_node, figma_fill),
                                 isEnabled=figma_fill['visible'])


def convert_color(color: dict, opacity: Optional[float]=None) -> Color:
    return Color(
        red=color['r'],
        green=color['g'],
        blue=color['b'],
        alpha=color['a'] if opacity is None else opacity,
    )


def convert_gradient(figma_node: dict, figma_fill: dict) -> Gradient:
    # Convert positions depending on the gradient type
    mat = figma_fill['transform']

    invmat = np.linalg.inv(mat)

    rotation_offset = 0.0
    if figma_fill['type'] == 'GRADIENT_LINEAR':
        # Linear gradients always go from (0, .5) to (1, .5)
        # We just apply the transform to get the coordinates (in a 1x1 square)
        return Gradient.Linear(
            from_=Point.from_array(invmat.dot([0, 0.5, 1])),
            to=Point.from_array(invmat.dot([1, 0.5, 1])),
            stops=convert_stops(figma_fill['stops'])
        )
    elif figma_fill['type'] in ['GRADIENT_RADIAL', 'GRADIENT_DIAMOND']:
        # Figma angular gradients have the center at (.5, .5), the vertex at (1, .5)
        # and the co-vertex at (.5, 1). We transform them to the coordinates in a 1x1 square
        point_from = invmat.dot([0.5, 0.5, 1])  # Center
        point_to = invmat.dot([1, 0.5, 1])
        point_ellipse = invmat.dot([0.5, 1, 1])

        # Sketch defines the ratio between axis in the item reference point (not the 1x1 square)
        # So we scale the 1x1 square coordinates to fit the ratio of the item frame before
        # calculating the ellipse's ratio
        x_scale = figma_node['size']['x'] / figma_node['size']['y']
        ellipse_ratio = scaled_distance(point_from, point_ellipse, x_scale) / scaled_distance(
            point_from, point_to, x_scale)

        return Gradient.Radial(
            from_=Point.from_array(point_from),
            to=Point.from_array(point_to),
            elipseLength=ellipse_ratio,
            stops=convert_stops(figma_fill['stops'])
        )
    else:
        # Angular gradients don't allow positioning, but we can at least rotate them
        rotation_offset = math.atan2(-figma_fill['transform'][1,0],
                                     figma_fill['transform'][0,0]) / 2 / math.pi

        return Gradient.Angular(
            stops=convert_stops(figma_fill['stops'], rotation_offset)
        )


def convert_stops(figma_stops: List[dict], rotation_offset: float=0.0) -> List[GradientStop]:
    stops = [
        GradientStop(
            color=convert_color(stop['color']),
            position=rotated_stop(stop['position'], rotation_offset),
        )
        for stop in figma_stops
    ]

    if rotation_offset:
        # When we have a rotated angular gradient, stops at 0 and 1 both convert
        # to the exact same position and that confuses Sketch. Force a small difference
        stops[-1].position -= 0.00001

    return stops


def scaled_distance(a: npt.NDArray[np.float64], b: npt.NDArray[np.float64], x_scale: float) -> float:
    v = a - b
    return np.hypot(v[0] * x_scale, v[1])


def rotated_stop(position: float, offset: float) -> float:
    pos = position + offset
    if pos > 1:
        pos -= 1
    elif pos < 0:
        pos += 1
    if pos < 0:
        pos += 1
    return pos


class _Effects(TypedDict):
    blur: Blur
    shadows: List[Shadow]
    innerShadows: List[InnerShadow]


def convert_effects(figma_node: dict) -> _Effects:
    sketch: _Effects = {
        'blur': Blur.Disabled(),
        'shadows': [],
        'innerShadows': []
    }

    for e in figma_node.get('effects', []):
        if e['type'] == 'INNER_SHADOW':
            sketch['innerShadows'].append(InnerShadow(
                blurRadius=e['radius'],
                offsetX=e['offset']['x'],
                offsetY=e['offset']['y'],
                spread=e['spread'],
                color=convert_color(e['color'])
            ))

        elif e['type'] == 'DROP_SHADOW':
            sketch['shadows'].append(Shadow(
                blurRadius=e['radius'],
                offsetX=e['offset']['x'],
                offsetY=e['offset']['y'],
                spread=e['spread'],
                color=convert_color(e['color'])
            ))

        elif e['type'] == 'FOREGROUND_BLUR':
            if sketch['blur'].isEnabled:
                utils.log_conversion_warning("STY001", figma_node)
                continue

            sketch['blur'] = Blur(
                radius=e['radius'] / 2,  # Looks best dividing by 2, no idea why,
                type=BlurType.GAUSSIAN
            )

        elif e['type'] == 'BACKGROUND_BLUR':
            if sketch['blur'].isEnabled:
                utils.log_conversion_warning("STY001", figma_node)
                continue

            sketch['blur'] = Blur(
                radius=e['radius'] / 2,  # Looks best dividing by 2, no idea why,
                type=BlurType.BACKGROUND
            )

        else:
            raise Exception(f'Unsupported effect: {e["type"]}')

    return sketch


def context_settings(figma_node: dict) -> ContextSettings:
    blend_mode = BLEND_MODE[figma_node['blendMode']]
    opacity = figma_node['opacity']

    if figma_node['blendMode'] == 'NORMAL' and opacity == 1:
        # Sketch interprets normal at 100% opacity as pass-through
        opacity = 0.99

    return ContextSettings(blendMode=blend_mode, opacity=opacity)
