import utils
from . import positioning, style, text
from .context import context

CURVE_MODES = {
    'STRAIGHT': 1,
    'ANGLE_AND_LENGTH': 2,
    'ANGLE': 3,
    'NONE': 4
}


def base_shape(figma_node):
    return {
        'do_objectID': utils.gen_object_id(figma_node.id),
        'booleanOperation': -1,
        'exportOptions': export_options(figma_node.get('exportSettings', [])),
        **positioning.convert(figma_node),
        **utils.masking(figma_node),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 0,
        'nameIsFixed': False,
        'resizingConstraint': 9,
        'resizingType': 0,
        **process_styles(figma_node)
    }


def process_styles(figma_node):
    style_attributes = {'style': style.convert(figma_node)}

    SUPPORTED_INHERIT_STYLES = {
        'inheritFillStyleID': ('fills',),
        'inheritFillStyleIDForStroke': ('borders', ),
        'inheritStrokeStyleID': None, # Unused in Figma?
        'inheritTextStyleID': ('textStyle',),
        'inheritExportStyleID': None, # Unused in Figma?
        'inheritEffectStyleID': ('blur', 'shadows', 'innerShadows'),
        'inheritGridStyleID': (), # TODO: Implement grid styles. Don't make it crash for now
        'inheritFillStyleIDForBackground': None, # Unused in Figma?
    }

    for inherit_style, sketch_keys in SUPPORTED_INHERIT_STYLES.items():
        if inherit_style in figma_node and figma_node[inherit_style]['sessionID'] != 4294967295: # MAX_INT = unset
            if sketch_keys is None:
                raise Exception("Unhandled inherit style ", inherit_style)

            figma_style, shared_style = context.component((figma_node[inherit_style]['sessionID'], figma_node[inherit_style]['localID']))

            if shared_style is not None:
                # At this moment, this is only styles that involve a single solid color
                # Look at component.convert for supported types
                assert len(sketch_keys) == 1
                style_attributes['style'][sketch_keys[0]][0]['color'] = shared_style['value']
                style_attributes['style'][sketch_keys[0]][0]['color']['swatchID'] = shared_style['do_objectID']
            else:
                # We don't support the shared style type, so we just copy the style
                # TODO: Should we add it as a preset?
                if inherit_style == 'inheritFillStyleIDForStroke':
                    # Copying fill to border, so copy fill properties from shared style into this node borders
                    converted_style = style.convert(figma_style)

                    base_border = {
                        '_class': 'border',
                        'position': style_attributes['style']['borders'][0]['position'],
                        'thickness': style_attributes['style']['borders'][0]['thickness']
                    }

                    style_attributes['style']['borders'] = [
                        {
                            **fill_style,
                            **base_border
                        } for fill_style in converted_style['fills']
                    ]
                else:
                    for sketch_key in sketch_keys:
                        # Text style are dealt with in text.py, so just change the figma node
                        # with the overrides and let that module deal with it
                        # TODO: Should we use this approach for everything else too?
                        if sketch_key == 'textStyle':
                            TEXT_PROPERTIES = [
                                'fontName',
                                'textCase',
                                'fontSize',
                                'textAlignVertical',
                                'textAlignHorizontal',
                                'textDecoration',
                                'letterSpacing',
                                'lineHeight',
                                'paragraphSpacing'
                            ]
                            for p in TEXT_PROPERTIES:
                                if p in figma_style:
                                    figma_node[p] = figma_style[p]
                        else:
                            style_attributes['style'][sketch_key] = style.convert(figma_style)[sketch_key]

    return style_attributes


def export_options(figma_export_settings):
    return {
        "_class": "exportOptions",
        "includedLayerIds": [],
        "layerOptions": 0,
        "shouldTrim": False,
        "exportFormats": [
            {
                "_class": "exportFormat",
                "fileFormat": s['imageType'].lower(),
                "name": s['suffix'],
                "namingScheme": 2,
                **export_scale(s['constraint'])
            } for s in figma_export_settings]
    }


def export_scale(figma_constraint):
    match figma_constraint:
        case {'type': 'CONTENT_SCALE', 'value': scale}:
            return {
                'absoluteSize': 0,
                'scale': scale,
                'visibleScaleType': 0
            }
        case {'type': 'CONTENT_WIDTH', 'value': size}:
            return {
                'absoluteSize': size,
                'scale': 0,
                'visibleScaleType': 1
            }
        case {'type': 'CONTENT_HEIGHT', 'value': size}:
            return {
                'absoluteSize': size,
                'scale': 0,
                'visibleScaleType': 2
            }


def make_point(figma_node, x, y, figma_point={}):
    return {
        '_class': 'curvePoint',
        'cornerRadius': adjust_corner_radius(figma_node, figma_point),
        'curveFrom': '{0, 0}',
        'curveMode': adjust_curve_mode(figma_point, 'STRAIGHT'),
        'curveTo': '{0, 0}',
        'hasCurveFrom': False,
        'hasCurveTo': False,
        'point': f'{{{x}, {y}}}'
    }


def adjust_curve_mode(figma_point, default_value):
    if 'style' in figma_point and 'handleMirroring' in figma_point['style']:
        return CURVE_MODES[figma_point['style']['handleMirroring']]

    return CURVE_MODES[default_value]


def adjust_corner_radius(figma_node, figma_point):
    if 'style' in figma_point and 'cornerRadius' in figma_point['style']:
        return figma_point['style']['cornerRadius']

    return figma_node['cornerRadius']
