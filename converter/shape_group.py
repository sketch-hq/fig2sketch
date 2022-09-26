from . import positioning, style
import utils

BOOLEAN_OPERATIONS = {
    'UNION': 0,
    'INTERSECT': 2,
    'SUBTRACT': 1,
    'XOR': 3
}

def convert(figma_bool_ops):
    return {
        '_class': 'shapeGroup',
        'do_objectID': utils.gen_object_id(),
        'booleanOperation': -1,
        'exportOptions': {
            '_class': 'exportOptions',
            'exportFormats': [],
            'includedLayerIds': [],
            'layerOptions': 0,
            'shouldTrim': False
        },
        **positioning.convert(figma_bool_ops),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 2,
        'name': figma_bool_ops.name,
        'nameIsFixed': False,
        'resizingConstraint': 9,
        'resizingType': 0,
        'shouldBreakMaskChain': True,
        'style': style.convert(figma_bool_ops),
        'hasClickThrough': False,
        "groupLayout": {
            "_class": "MSImmutableFreeformGroupLayout"
        },
    }

def post_process(figma_bool_ops, sketch_bool_ops):
    op = BOOLEAN_OPERATIONS[figma_bool_ops.booleanOperation]
    for l in sketch_bool_ops['layers']:
        l['booleanOperation'] = op
