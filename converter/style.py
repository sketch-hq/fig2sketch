def convert(figma):
    fills = [
        {
            "_class": "fill",
            "isEnabled": True,
            "color": {
                "_class": "color",
                "red": f['color']['r'],
                "green": f['color']['g'],
                "blue": f['color']['b'],
                "alpha": f['opacity'],
            },
            "fillType": 0,
            "noiseIndex": 0,
            "noiseIntensity": 0,
            "patternFillType": 0,
            "patternTileScale": 1,
            "contextSettings": {
                "_class": "graphicsContextSettings",
                "blendMode": 0,
                "opacity": f.get('opacity', 1)
            },
            "gradient": {
                "_class": "gradient",
                "elipseLength": 0,
                "from": "{0.5, 0}",
                "to": "{0.5, 1}",
                "gradientType": 1,
                "stops": []
            }
        } for f in figma['fills']
    ]
    borders = [
        {
            "_class": "border",
            "isEnabled": True,
            "color": {
                "_class": "color",
                "red": b['color']['r'],
                "green": b['color']['g'],
                "blue": b['color']['b'],
                "alpha": b['opacity']
            },
            "fillType": 0,  # TODO b['type']
            "position": 0 if figma['strokeAlign'] == 'CENTER' else (
                1 if figma['strokeAlign'] == 'INSIDE' else 2),
            "thickness": figma['strokeWeight'],
            "contextSettings": {
                "_class": "graphicsContextSettings",
                "blendMode": 0,  # TODO b['blendMode'] enum
                "opacity": b.get('opacity', 1)
            },
            "gradient": {  # TODO b['type'] // How to do type == IMAGE / EMOJI ???
                "_class": "gradient",
                "elipseLength": 0,
                "from": "{0.5, 0}",
                "to": "{0.5, 1}",
                "gradientType": 1,
                "stops": []
            }
        } for b in figma['strokes']
    ]

    return {
        "_class": "style",
        "do_objectID": "49818921-5C49-492C-810F-00AB552E03BC",
        "borders": borders,
        "borderOptions": {
            "_class": "borderOptions",
            "isEnabled": True,
            "lineCapStyle": 0,
            "lineJoinStyle": 0
        },
        "fills": fills,
        "startMarkerType": 0,
        "endMarkerType": 0,
        "miterLimit": 10,
        "windingRule": 0,
        "shadows": [  # TODO figma['effects'] type = DROP_SHADOW
        ],
        "innerShadows": [],  # TODO figma['effects'] type = INNER_SHADOW
        "contextSettings": {
            "_class": "graphicsContextSettings",
            "blendMode": 0,
            "opacity": 1
        },
        "colorControls": {
            "_class": "colorControls",
            "isEnabled": True,
            "brightness": 0,
            "contrast": 1,
            "hue": 0,
            "saturation": 1
        }
    }
