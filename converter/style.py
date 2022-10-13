import numpy as np
import math
import utils

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

GRADIENT_TYPE = {
    'GRADIENT_LINEAR': 0,
    'GRADIENT_RADIAL': 1,
    'GRADIENT_ANGULAR': 2,  # TODO: Sketch does not support positioning angular gradients
    'GRADIENT_DIAMOND': 1,  # Unsupported by Sketch, most similar is radial
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
    return {
        **convert_fill(figma_node, figma_border),
        '_class': 'border',
        'position': BORDER_POSITION[figma_node['strokeAlign']],
        'thickness': figma_node['strokeWeight'],
    }


def convert_fill(figma_node, figma_fill):
    return {
        '_class': 'fill',
        'isEnabled': figma_fill['visible'],
        'noiseIndex': 0,
        'noiseIntensity': 0,
        'patternFillType': 0,
        'patternTileScale': 1,
        'contextSettings': {
            '_class': 'graphicsContextSettings',
            'blendMode': 0,
            'opacity': figma_fill.get('opacity', 1)
        },
        **fill_type_specific_attributes(figma_node, figma_fill)
    }

DISABLED_GRADIENT = {
    'gradient': {
        '_class': 'gradient',
        'elipseLength': 0,
        'from': '{0.5, 0}',
        'gradientType': 0,
        'stops': [
        {
            '_class': 'gradientStop',
            'color': {
            '_class': 'color',
            'alpha': 1,
            'blue': 1,
            'green': 1,
            'red': 1
            },
            'position': 0
        },
        {
            '_class': 'gradientStop',
            'color': {
            '_class': 'color',
            'alpha': 1,
            'blue': 0,
            'green': 0,
            'red': 0
            },
            'position': 1
        }
        ],
        'to': '{0.5, 1}'
    }
}

def fill_type_specific_attributes(figma_node, figma_fill):
    match figma_fill:
        case {'type': 'EMOJI'}:
            raise Exception("Unsupported fill: EMOJI")
        case {'type': 'SOLID'}:
            return {
                'fillType': 0,
                'color': convert_color(figma_fill),
                **DISABLED_GRADIENT
            }
        case {'type': 'IMAGE'}:
            return {
                'fillType': 4,
                'image': {
                    '_class': 'MSJSONFileReference',
                    '_ref_class': 'MSImageData',
                    '_ref': f'images/{figma_fill["image"]["filename"]}.png'
                },
                'noiseIndex': 0,
                'noiseIntensity': 0,
                'patternFillType': PATTERN_FILL_TYPE[figma_fill['imageScaleMode']],
                'patternTileScale': 1,
                **DISABLED_GRADIENT
            }
        case _:
            return convert_gradient(figma_node, figma_fill)


def convert_color(figma_fill):
    return {
        '_class': 'color',
        'red': figma_fill['color']['r'],
        'green': figma_fill['color']['g'],
        'blue': figma_fill['color']['b'],
        'alpha': figma_fill['opacity'],
    }


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
        point_from = invmat.dot([0, 0.5, 1])
        point_to = invmat.dot([1, 0.5, 1])
        ellipse_ratio = 0  # Doesn't matter
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
    else:
        # Angular gradients don't allow positioning, but we can at least rotate them
        point_from = [0, 0]
        point_to = [0, 0]
        ellipse_ratio = 0
        rotation_offset = math.atan2(-figma_fill['transform']['m10'],
                                     figma_fill['transform']['m00']) / 2 / math.pi

    gradient_fill = {
        'fillType': 1,
        'gradient': {
            '_class': 'gradient',
            'gradientType': GRADIENT_TYPE[figma_fill['type']],
            'from': utils.np_point_to_string(point_from),
            'to': utils.np_point_to_string(point_to),
            'elipseLength': ellipse_ratio,
            'stops': [
                {
                    '_class': 'gradientStop',
                    'position': rotated_stop(stop['position'], rotation_offset),
                    'color': {
                        '_class': 'color',
                        'red': stop['color']['r'],
                        'green': stop['color']['g'],
                        'blue': stop['color']['b'],
                        'alpha': stop['color']['a'],
                    }
                } for stop in figma_fill['stops']
            ]
        }
    }

    if rotation_offset:
        # When we have a rotated angular gradient, stops at 0 and 1 both convert
        # to the exact same position and that confuses Sketch. Force a small difference
        gradient_fill['gradient']['stops'][-1]['position'] -= 0.00001

    return gradient_fill


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
