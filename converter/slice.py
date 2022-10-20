import utils
from . import base, positioning


def convert(figma_slice):
    # TODO: Rotated slices. Ideally, we should calculate the bounding box of the
    # rotated rectangle and use that as the Sketch frame (and rotation = 0)
    # In any case, nobody should be rotating slices, it does not make sense.

    # Not using base because slices don't have many style/masking properties
    return {
        '_class': 'slice',
        'name': figma_slice['name'],
        'do_objectID': utils.gen_object_id(figma_slice['guid']),
        'booleanOperation': -1,
        'exportOptions': base.export_options(figma_slice['exportSettings']),
        **positioning.convert(figma_slice),
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 0,
        'nameIsFixed': False,
        'resizingConstraint': 9,
        'resizingType': 0,
        'hasBackgroundColor': False,
        'shouldBreakMaskChain': False,
        'isTemplate': False,
        'backgroundColor': {
            '_class': 'color',
            'alpha': 1,
            'blue': 1,
            'green': 1,
            'red': 1
        }
    }
