import utils

def convert_fill(figma):
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
        },
        'gradient': {
            '_class': 'gradient',
            'elipseLength': 0,
            'from': '{0.5, 0}',
            'to': '{0.5, 1}',
            'gradientType': 1,
            'stops': []
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
    
    else:
        # 'GRADIENT_LINEAR'
        # 'GRADIENT_RADIAL'
        # 'GRADIENT_ANGULAR'
        # 'GRADIENT_DIAMOND'
        # 'EMOJI'
        raise f"Fill type not implemented {figma['type']}"

    return sketch

def convert(figma):
    fills = [convert_fill(f) for f in figma['fillPaints']
    ]
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

    return {
        '_class': 'style',
        'do_objectID': utils.gen_object_id(),
        'borders': borders,
        'borderOptions': {
            '_class': 'borderOptions',
            'isEnabled': True,
            'lineCapStyle': 0,
            'lineJoinStyle': 0
        },
        'fills': fills,
        'startMarkerType': 0,
        'endMarkerType': 0,
        'miterLimit': 10,
        'windingRule': 0,
        'shadows': [  # TODO figma['effects'] type = DROP_SHADOW
        ],
        'innerShadows': [],  # TODO figma['effects'] type = INNER_SHADOW
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
