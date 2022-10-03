import utils
from . import positioning, style
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
        'inheritFillStyleID': 'fills',
        'inheritFillStyleIDForStroke': 'borders',
    }

    for inherit_style, sketch_key in SUPPORTED_INHERIT_STYLES.items():
        if inherit_style in figma_node and figma_node[inherit_style]['sessionID'] != 4294967295: # MAX_INT = unset
            figma_style, shared_style = context.component((figma_node[inherit_style]['sessionID'], figma_node[inherit_style]['localID']))

            if shared_style is not None:
                # At some point we'll need to handle styles with multiple colors which
                # are not supported by sketch. This is just using the first color of
                # the array
                style_attributes['style'][sketch_key][0]['color'] = shared_style['value']
                style_attributes['style'][sketch_key][0]['color']['swatchID'] = shared_style['do_objectID']
            else:
                # We don't support the shared style type, so we just copy the style
                # TODO: Should we add it as a preset
                if inherit_style == 'inheritFillStyleIDForStroke':
                    # Copying fill to border, so copy fill properties from shared style into this node borders
                    converted_style = style.convert(figma_style)
                    for i in range(len(style_attributes['style'][sketch_key])):
                        style_attributes['style']['borders'][i].update(converted_style['fills'][i])
                        style_attributes['style']['borders'][i]['_class'] = 'border'
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
