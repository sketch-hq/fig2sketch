import numpy as np
import math
import utils


def convert(figma):
    fills = [convert_fill(f, figma) for f in figma['fillPaints']]
    borders = [
        {
            '_class': 'border',
            'isEnabled': True,
            'color': {
                '_class': 'color',
                'red': b['color']['r'],
                'green': b['color']['g'],
                'blue': b['color']['b'],
                'alpha': b['opacity']
            },
            'fillType': 0,  # TODO b['type']
            'position': 0 if figma['strokeAlign'] == 'CENTER' else (
                1 if figma['strokeAlign'] == 'INSIDE' else 2),
            'thickness': figma['strokeWeight'],
            'contextSettings': {
                '_class': 'graphicsContextSettings',
                'blendMode': 0,  # TODO b['blendMode'] enum
                'opacity': b.get('opacity', 1)
            },
            'gradient': {  # TODO b['type'] // How to do type == IMAGE / EMOJI ???
                '_class': 'gradient',
                'elipseLength': 0,
                'from': '{0.5, 0}',
                'to': '{0.5, 1}',
                'gradientType': 1,
                'stops': []
            }
        } for b in figma['strokePaints']
    ]

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

    return {
        '_class': 'style',
        'do_objectID': utils.gen_object_id(),
        'borders': borders,
        'borderOptions': {
            '_class': 'borderOptions',
            'isEnabled': True,
            'lineCapStyle': LINE_CAP_STYLE[figma.strokeCap],
            'lineJoinStyle': LINE_JOIN_STYLE[figma.strokeJoin],
            "dashPattern": figma.dashPattern
        },
        'fills': fills,
        'miterLimit': 10,
        'windingRule': 0,
        **convert_effects(figma.get('effects', [])),
        'contextSettings': {
            '_class': 'graphicsContextSettings',
            'blendMode': 0,
            'opacity': 1
        },
        'colorControls': {
            '_class': 'colorControls',
            'isEnabled': True,
            'brightness': 0,
            'contrast': 1,
            'hue': 0,
            'saturation': 1
        }
    }


def convert_fill(figma, figma_node):
    PATTERN_FILL_TYPE = {
        'STRETCH': 2,
        'FIT': 3,
        'FILL': 1,
        'TILE': 0
    }

    sketch = {
        '_class': 'fill',
        'isEnabled': figma['visible'],
        'noiseIndex': 0,
        'noiseIntensity': 0,
        'patternFillType': 0,
        'patternTileScale': 1,
        'contextSettings': {
            '_class': 'graphicsContextSettings',
            'blendMode': 0,
            'opacity': figma.get('opacity', 1)
        }
    }

    if figma['type'] == 'SOLID':
        sketch['fillType'] = 0
        sketch['color'] = {
            '_class': 'color',
            'red': figma['color']['r'],
            'green': figma['color']['g'],
            'blue': figma['color']['b'],
            'alpha': figma['opacity'],
        }

    elif figma['type'] == 'IMAGE':
        sketch['fillType'] = 4
        sketch['image'] = {
            '_class': 'MSJSONFileReference',
            '_ref_class': 'MSImageData',
            '_ref': f'images/{figma["image"]["hash"]}.png'
        }
        sketch['noiseIndex'] = 0
        sketch['noiseIntensity'] = 0
        sketch['patternFillType'] = PATTERN_FILL_TYPE[figma['imageScaleMode']]
        sketch['patternTileScale'] = 1

    elif figma['type'] == 'EMOJI':
        raise Exception("Unsupported fill: EMOJI")

    else:
        # Gradients
        GRADIENT_TYPE = {
            'GRADIENT_LINEAR': 0,
            'GRADIENT_RADIAL': 1,
            'GRADIENT_ANGULAR': 2,  # TODO: Sketch does not support positioning angular gradients
            'GRADIENT_DIAMOND': 1,  # Unsupported by Sketch, most similar is radial
        }

        # Convert positions depending on the gradient type
        mat = np.array([
            [figma['transform']['m00'], figma['transform']['m01'], figma['transform']['m02']],
            [figma['transform']['m10'], figma['transform']['m11'], figma['transform']['m12']],
            [0, 0, 1]
        ])

        invmat = np.linalg.inv(mat)

        rotation_offset = 0
        if figma['type'] == 'GRADIENT_LINEAR':
            # Linear gradients always go from (0, .5) to (1, .5)
            # We just apply the transform to get the coordinates (in a 1x1 square)
            point_from = invmat.dot([0, 0.5, 1])
            point_to = invmat.dot([1, 0.5, 1])
            ellipse_ratio = 0  # Doesn't matter
        elif figma['type'] in ['GRADIENT_RADIAL', 'GRADIENT_DIAMOND']:
            # Figma angular gradients have the center at (.5, .5), the vertex at (1, .5)
            # and the co-vertex at (.5, 1). We transform them to the coordinates in a 1x1 square
            point_from = invmat.dot([0.5, 0.5, 1])  # Center
            point_to = invmat.dot([1, 0.5, 1])
            point_ellipse = invmat.dot([0.5, 1, 1])

            # Sketch defines the ratio between axis in the item reference point (not the 1x1 square)
            # So we scale the 1x1 square coordinates to fit the ratio of the item frame before calculating
            # the ellipse's ratio
            x_scale = figma_node.size['x'] / figma_node.size['y']
            ellipse_ratio = scaled_distance(point_from, point_ellipse, x_scale) / scaled_distance(
                point_from, point_to, x_scale)
        else:
            # Angular gradients don't allow positioning, but we can at least rotate them
            point_from = [0, 0]
            point_to = [0, 0]
            ellipse_ratio = 0
            rotation_offset = math.atan2(-figma['transform']['m10'],
                                         figma['transform']['m00']) / 2 / math.pi

        sketch['fillType'] = 1
        sketch['gradient'] = {
            '_class': 'gradient',
            'gradientType': GRADIENT_TYPE[figma['type']],
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
                } for stop in figma['stops']
            ]
        }

        if rotation_offset:
            # When we have a rotated angular grandient, stops at 0 and 1 both convert
            # to the exact same position and that confuses Sketch. Force a small difference
            sketch['gradient']['stops'][-1]['position'] -= 0.00001

    return sketch


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
                'radius': e['radius'] / 2, # Looks best dividing by 2, no idea why,
                'saturation': 1,
                'type': 0
            }

        elif e['type'] == 'BACKGROUND_BLUR':
            if sketch['blur']['isEnabled']:
                raise Exception(f'Cannot support multuple blurs')

            sketch['blur'] = {
                '_class': 'blur',
                'isEnabled': True,
                'center': '{0.5, 0.5}',
                'motionAngle': 0,
                'radius': e['radius'] / 2, # Looks best dividing by 2, no idea why
                'saturation': 1,
                'type': 3
            }

        else:
            raise Exception(f'Unsupported effect: {e["type"]}')

    return sketch
