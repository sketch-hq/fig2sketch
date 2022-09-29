import utils
from . import positioning, style


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
        'style': style.convert(figma_node),
    }


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
