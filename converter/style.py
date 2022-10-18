import numpy as np
import math
import utils
from sketchformat.style import *

BORDER_POSITION = {
    'CENTER': 0,
    'INSIDE': 1,
    'OUTSIDE': 2
}

LINE_CAP_STYLE = {
    'NONE': 0,
    'ROUND': 1,
    'SQUARE': 2,
    'LINE_ARROW': 2,
    'ARROW_LINES': 2,
    'TRIANGLE_ARROW': 2,
    'TRIANGLE_FILLED': 2
}

LINE_JOIN_STYLE = {
    'MITER': 0,
    'ROUND': 1,
    'BEVEL': 2
}

PATTERN_FILL_TYPE = {
    'STRETCH': 2,
    'FIT': 3,
    'FILL': 1,
    'TILE': 0
}

BLEND_MODE = {
  'PASS_THROUGH': 0,
  'NORMAL': 0,
  'DARKEN': 1,
  'MULTIPLY': 2,
  # 'LINEAR_BURN': , Cannot be set on Figma UI?
  'COLOR_BURN': 3,
  'LIGHTEN': 4,
  'SCREEN': 5,
  # 'LINEAR_DODGE': , Cannot be set on Figma UI?
  'COLOR_DODGE': 6,
  'OVERLAY': 7,
  'SOFT_LIGHT': 8,
  'HARD_LIGHT': 9,
  'DIFFERENCE': 10,
  'EXCLUSION': 11,
  'HUE': 12,
  'SATURATION': 13,
  'COLOR': 14,
  'LUMINOSITY': 15,
}

def convert(figma_node):
    return {
        '_class': 'style',
        'do_objectID': utils.gen_object_id(figma_node.id, b'style'),
        'borderOptions': {
            '_class': 'borderOptions',
            'isEnabled': True,
            'lineCapStyle': LINE_CAP_STYLE[figma_node.strokeCap],
            'lineJoinStyle': LINE_JOIN_STYLE[figma_node.strokeJoin],
            "dashPattern": figma_node.dashPattern
        },
        'borders': [convert_border(figma_node, b) for b in figma_node['strokePaints']],
        'fills': [convert_fill(figma_node, f) for f in figma_node['fillPaints']],
        'miterLimit': 10,
        'windingRule': 0,
        **convert_effects(figma_node.get('effects', [])),
        'contextSettings': context_settings(figma_node),
        'colorControls': {
            '_class': 'colorControls',
            'isEnabled': True,
            'brightness': 0,
            'contrast': 1,
            'hue': 0,
            'saturation': 1
        },
        'startMarkerType': 0,
        'endMarkerType': 0,
    }


def convert_border(figma_node, figma_border):
    return Border.from_fill(
        convert_fill(figma_node, figma_border),
        position=BORDER_POSITION[figma_node['strokeAlign']],
        thickness=figma_node['strokeWeight'],
    )


def convert_fill(figma_node, figma_fill):
    kw = {
        'contextSettings': ContextSettings(opacity=figma_fill.get('opacity', 1)),
        'isEnabled': figma_fill['visible']
    }

    match figma_fill:
        case {'type': 'EMOJI'}:
            raise Exception("Unsupported fill: EMOJI")
        case {'type': 'SOLID'}:
            return Fill.Color(convert_color(figma_fill['color'], figma_fill['opacity']), **kw)
        case {'type': 'IMAGE'}:
            return Fill.Image(
                f'images/{figma_fill["image"]["filename"]}.png',
                patternFillType=PATTERN_FILL_TYPE[figma_fill['imageScaleMode']],
                **kw
            )
        case _:
            return Fill.Gradient(convert_gradient(figma_node, figma_fill))


def convert_color(color, opacity=None):
    return Color(
        red=color['r'],
        green=color['g'],
        blue=color['b'],
        alpha=color['a'] if opacity is None else opacity,
    )


def convert_gradient(figma_node, figma_fill):
    # Convert positions depending on the gradient type
    mat = np.array([
        [figma_fill['transform']['m00'], figma_fill['transform']['m01'],
         figma_fill['transform']['m02']],
        [figma_fill['transform']['m10'], figma_fill['transform']['m11'],
         figma_fill['transform']['m12']],
        [0, 0, 1]
    ])

    invmat = np.linalg.inv(mat)

    rotation_offset = 0
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
        x_scale = figma_node.size['x'] / figma_node.size['y']
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
        rotation_offset = math.atan2(-figma_fill['transform']['m10'],
                                     figma_fill['transform']['m00']) / 2 / math.pi

        return Gradient.Angular(
            stops=convert_stops(figma_fill['stops'], rotation_offset)
        )

def convert_stops(figma_stops, rotation_offset=0):
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


def scaled_distance(a, b, x_scale):
    v = a - b
    return np.hypot(v[0] * x_scale, v[1])


def rotated_stop(position, offset):
    pos = position + offset
    if pos > 1:
        pos -= 1
    elif pos < 0:
        pos += 1
    if pos < 0:
        pos += 1
    return pos


def convert_effects(effects):
    sketch = {
        'blur': {
            '_class': 'blur',
            'isEnabled': False,
            'center': '{0.5, 0.5}',
            'motionAngle': 0,
            'radius': 10,
            'saturation': 1,
            'type': 0
        },
        'shadows': [],
        'innerShadows': []
    }

    for e in effects:
        if e['type'] == 'INNER_SHADOW':
            sketch['innerShadows'].append({
                '_class': 'innerShadow',
                'isEnabled': True,
                'blurRadius': e['radius'],
                'offsetX': e['offset']['x'],
                'offsetY': e['offset']['y'],
                'spread': e['spread'],
                'color': {
                    '_class': 'color',
                    'alpha': e['color']['a'],
                    'blue': e['color']['b'],
                    'green': e['color']['g'],
                    'red': e['color']['r']
                },
                'contextSettings': {
                    '_class': 'graphicsContextSettings',
                    'blendMode': 0,
                    'opacity': 1
                }
            })

        elif e['type'] == 'DROP_SHADOW':
            sketch['shadows'].append({
                '_class': 'shadow',
                'isEnabled': True,
                'blurRadius': e['radius'],
                'offsetX': e['offset']['x'],
                'offsetY': e['offset']['y'],
                'spread': e['spread'],
                'color': {
                    '_class': 'color',
                    'alpha': e['color']['a'],
                    'blue': e['color']['b'],
                    'green': e['color']['g'],
                    'red': e['color']['r']
                },
                'contextSettings': {
                    '_class': 'graphicsContextSettings',
                    'blendMode': 0,
                    'opacity': 1
                }
            })

        elif e['type'] == 'FOREGROUND_BLUR':
            if sketch['blur']['isEnabled']:
                raise Exception(f'Cannot support multuple blurs')

            sketch['blur'] = {
                '_class': 'blur',
                'isEnabled': True,
                'center': '{0.5, 0.5}',
                'motionAngle': 0,
                'radius': e['radius'] / 2,  # Looks best dividing by 2, no idea why,
                'saturation': 1,
                'type': 0
            }

        elif e['type'] == 'BACKGROUND_BLUR':
            if sketch['blur']['isEnabled']:
                raise Exception(f'Cannot support multiple blurs')

            sketch['blur'] = {
                '_class': 'blur',
                'isEnabled': True,
                'center': '{0.5, 0.5}',
                'motionAngle': 0,
                'radius': e['radius'] / 2,  # Looks best dividing by 2, no idea why
                'saturation': 1,
                'type': 3
            }

        else:
            raise Exception(f'Unsupported effect: {e["type"]}')

    return sketch


def context_settings(figma_node):
    blend_mode = BLEND_MODE[figma_node['blendMode']]
    opacity = figma_node['opacity']

    if figma_node['blendMode'] == 'NORMAL' and opacity == 1:
        # Sketch interprets normal at 100% opacity as pass-through
        opacity = 0.99

    return {
        '_class': 'graphicsContextSettings',
        'blendMode': blend_mode,
        'opacity': opacity
    }


DEFAULT_STYLE = {
    '_class': 'style',
    'blur': {
        '_class': 'blur',
        'center': '{0.5, 0.5}',
        'isEnabled': False,
        'motionAngle': 0,
        'radius': 10,
        'saturation': 1,
        'type': 0
    },
    'borderOptions': {
        '_class': 'borderOptions',
        'dashPattern': [],
        'isEnabled': True,
        'lineCapStyle': 0,
        'lineJoinStyle': 0
    },
    'borders': [],
    'colorControls': {
        '_class': 'colorControls',
        'brightness': 0,
        'contrast': 1,
        'hue': 0,
        'isEnabled': False,
        'saturation': 1
    },
    'contextSettings': {
        '_class': 'graphicsContextSettings',
        'blendMode': 0,
        'opacity': 1
    },
    'do_objectID': 'A51794A6-A9E5-4E68-911B-99269CFAC3B9',
    'endMarkerType': 0,
    'fills': [],
    'innerShadows': [],
    'miterLimit': 10,
    'shadows': [],
    'startMarkerType': 0,
    'windingRule': 1
}
