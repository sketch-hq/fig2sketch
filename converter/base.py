import utils
from . import positioning, style

CURVE_MODES = {
    'STRAIGHT': 1,
    'ANGLE_AND_LENGTH': 2,
    'ANGLE': 3,
    'NONE': 4
}


def base_shape(figma_node, indexed_components):
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
        **process_styles(figma_node, indexed_components)
    }


def process_styles(figma_node, indexed_components):
    style_attributes = {'style': style.convert(figma_node)}

    if 'inheritFillStyleID' in figma_node:
        shared_style = get_shared_style(figma_node['inheritFillStyleID'], indexed_components)

        if shared_style != {}:
            style_attributes['style']['fills'][0]['color']['swatchID'] = shared_style[
                'do_objectID']

    # if 'inheritEffectStyleID' in figma_node:
    #     shared_style = get_shared_style(figma_node['inheritEffectStyleID'], indexed_components)
    #
    #     style_attributes['style'][]

    return style_attributes


def get_shared_style(item, indexed_components):
    node_id = (item['sessionID'], item['localID'])

    if node_id in indexed_components:
        return indexed_components[node_id]

    return {}


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
