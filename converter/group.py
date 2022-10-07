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

    # TODO: Convert frame styles
    # - Fill/stroke/bgblur -> Rectangle on bottom with that style
    # - Layer blur -> Rectangle with bgblur on top
    # - Shadows -> If we have fill, add shadow to the fill. If not, add shadow to each child

    needs_clip_mask = not figma_group.get('frameMaskDisabled', False)
    if needs_clip_mask:
        # Add a clipping rectangle matching the frame size. No need to recalculate bounds
        # since the clipmask defines Sketch bounds (which match visible children)
        sketch_group['layers'].insert(0, make_clipping_rect(figma_group.id, sketch_group['frame']))
    else:
        # When converting from a frame to a group, the bounding box should be adjusted
        # In Figma the frame box can be smalled than the children bounds, but not so in Sketch
        # To do so, we resize the frame to match the children bbox and also move the children
        # so that the top-left corner sits at 0,0
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
        vector = [children_bbox[0], children_bbox[2]]

        for child in sketch_group['layers']:
            child['frame']['x'] -= vector[0]
            child['frame']['y'] -= vector[1]

        # TODO: This probably breaks with rotation of the group
        sketch_group['frame']['x'] += vector[0]
        sketch_group['frame']['y'] += vector[1]
        sketch_group['frame']['width'] = children_bbox[1] - children_bbox[0]
        sketch_group['frame']['height'] = children_bbox[3] - children_bbox[2]


    return sketch_group


# TODO: Extract this and share code with positioning
def bbox_from_frame(child):
    frame = child['frame']
    theta = np.radians(child['rotation'])
    c, s = np.cos(theta), np.sin(theta)
    matrix = np.array(((c, -s), (s, c)))
    # Rotate the frame to the original position and calculate corners
    x1 = frame['x']
    x2 = x1 + frame['width']
    y1 = frame['y']
    y2 = y1 + frame['height']

    w2 = frame['width'] / 2
    h2 = frame['height'] / 2
    points = [
        matrix.dot(np.array([-w2, -h2])) - np.array([-w2, -h2]) + np.array([x1, y1]),
        matrix.dot(np.array([ w2, -h2])) - np.array([ w2, -h2]) + np.array([x2, y1]),
        matrix.dot(np.array([ w2,  h2])) - np.array([ w2,  h2]) + np.array([x2, y2]),
        matrix.dot(np.array([-w2,  h2])) - np.array([-w2,  h2]) + np.array([x1, y2]),
    ]

    return [
        min(p[0] for p in points),
        max(p[0] for p in points),
        min(p[1] for p in points),
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
