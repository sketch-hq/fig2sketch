from . import base
import utils
import numpy as np

def convert(figma_group):
    return {
        **base.base_shape(figma_group),
        '_class': 'group',
        'name': figma_group.name,
    }

def post_process_frame(figma_group, sketch_group):
    # Do nothing fro Figma groups, they translate directly to Sketch
    if figma_group['resizeToFit']:
        return sketch_group

    # Convert Figma frame to Sketch group. Figma frames clip children,
    # so if the children bbox is larger than the group, then we need
    # to add a clipping mask to the group. We don't need to recalculate
    # group bounds because in Sketch, the bounds would match those of the
    # clipping mask (i.e: group bounds = bounds of visible children)
    child_bboxes = [
        bbox_from_frame(child)
        for child in sketch_group['layers']
    ]
    children_bbox = [
        min([b[0] for b in child_bboxes]),
        max([b[1] for b in child_bboxes]),
        min([b[2] for b in child_bboxes]),
        max([b[3] for b in child_bboxes]),
    ]
    if children_bbox[0] < 0 or children_bbox[1] > sketch_group['frame']['width'] or children_bbox[2] < 0 or children_bbox[3] > sketch_group['frame']['height']:
        # Add a clipping rectangle matching the frame size
        sketch_group['layers'].insert(0, make_clipping_rect(figma_group.id, sketch_group['frame']))

    return sketch_group


def bbox_from_frame(child):
    frame = child['frame']
    theta = np.radians(-child['rotation'])
    c, s = np.cos(theta), np.sin(theta)
    matrix = np.array(((c, -s), (s, c)))
    # Rotate the frame to the original position and calculate corners
    points = [
        matrix.dot(np.array([0, 0])),
        matrix.dot(np.array([frame['width'], 0])),
        matrix.dot(np.array([frame['width'], frame['height']])),
        matrix.dot(np.array([0, frame['height']])),
    ]

    return [
        min(p[0] for p in points),
        max(p[1] for p in points),
        min(p[0] for p in points),
        max(p[1] for p in points),
    ]


def make_clipping_rect(guid, frame):
    return {
        '_class': 'rectangle',
        'do_objectID': utils.gen_object_id(guid, b'frame_mask'),
        'booleanOperation': -1,
        'exportOptions': {
            "_class": "exportOptions",
            "includedLayerIds": [],
            "layerOptions": 0,
            "shouldTrim": False,
            "exportFormats": []
        },
        'frame': {
            '_class': 'rect',
            'constrainProportions': False,
            'height': frame['height'],
            'width':frame['width'],
            'x': 0,
            'y': 0
        },
        'rotation': 0,
        'hasClippingMask': True,
        'clippingMaskMode': 0,
        'isFixedToViewport': False,
        'isFlippedHorizontal': False,
        'isFlippedVertical': False,
        'isLocked': False,
        'isVisible': True,
        'layerListExpandedType': 0,
        'nameIsFixed': False,
        'resizingConstraint': 0,
        'resizingType': 0,
        'style': {
            '_class': 'style',
            'do_objectID': utils.gen_object_id(guid, b'frame_mask_style'),
            # TODO: Border options
            'borders': [],
            'fills': [],
            'miterLimit': 10,
            'windingRule': 0,
            # TODO: Effects
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
        },
        'edited': False,
        'isClosed': True,
        'pointRadiusBehaviour': 0,
        'points': [
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{0, 0}',
                'curveMode': 1,
                'curveTo': '{0, 0}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{0, 0}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{1, 0}',
                'curveMode': 1,
                'curveTo': '{1, 0}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{1, 0}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{1, 1}',
                'curveMode': 1,
                'curveTo': '{1, 1}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{1, 1}'
            },
            {
                '_class': 'curvePoint',
                'cornerRadius': 0,
                'curveFrom': '{0, 1}',
                'curveMode': 1,
                'curveTo': '{0, 1}',
                'hasCurveFrom': False,
                'hasCurveTo': False,
                'point': '{0, 1}'
            }
        ],
        'fixedRadius': 0,
        'hasConvertedToNewRoundCorners': True
    }
