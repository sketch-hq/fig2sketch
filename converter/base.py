import utils
from . import positioning, style
from .context import context
from sketchformat.style import *
from sketchformat.layer_common import ExportOptions, ExportFormat, VisibleScaleType
from typing import TypedDict

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
        'isLocked': figma_node.locked,
        'isVisible': figma_node.visible,
        'layerListExpandedType': 0,
        'nameIsFixed': False,
        'resizingConstraint': resizing_constraint(figma_node),
        'resizingType': 0,
        **process_styles(figma_node),
        **prototyping_flow(figma_node),
        'isTemplate': False
    }


def process_styles(figma_node):
    style_attributes = {'style': style.convert(figma_node)}

    SUPPORTED_INHERIT_STYLES = {
        'inheritFillStyleID': ('fills',),
        'inheritFillStyleIDForStroke': ('borders',),
        'inheritStrokeStyleID': None,  # Unused in Figma?
        'inheritTextStyleID': ('textStyle',),
        'inheritExportStyleID': None,  # Unused in Figma?
        'inheritEffectStyleID': ('blur', 'shadows', 'innerShadows'),
        'inheritGridStyleID': (),  # TODO: Implement grid styles. Don't make it crash for now
        'inheritFillStyleIDForBackground': None,  # Unused in Figma?
    }

    for inherit_style, sketch_keys in SUPPORTED_INHERIT_STYLES.items():
        # MAX_INT = unset
        if inherit_style in figma_node and figma_node[inherit_style]['sessionID'] != 4294967295:
            if sketch_keys is None:
                raise Exception('Unhandled inherit style ', inherit_style)

            figma_style, shared_style = context.component(
                (figma_node[inherit_style]['sessionID'], figma_node[inherit_style]['localID']))

            if shared_style is not None:
                # At this moment, this is only styles that involve a single solid color
                # Look at component.convert for supported types
                assert len(sketch_keys) == 1
                getattr(style_attributes['style'], sketch_keys[0])[0].color = shared_style['value']
                # style_attributes['style'][sketch_keys[0]][0]['color']['swatchID'] = shared_style['do_objectID']
            else:
                # We don't support the shared style type, so we just copy the style
                # TODO: Should we add it as a preset?
                if inherit_style == 'inheritFillStyleIDForStroke':
                    # Copying fill to border, so copy fill properties from shared style into this
                    # node borders
                    converted_style = style.convert(figma_style)

                    base_border = {
                        'position': style_attributes['style'].borders[0].position,
                        'thickness': style_attributes['style'].borders[0].thickness
                    }

                    style_attributes['style'].borders = [
                        Border.from_fill(fill_style, **base_border) for fill_style in
                        converted_style.fills]
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
                            setattr(style_attributes['style'], sketch_key,
                                    getattr(style.convert(figma_style), sketch_key))

    return style_attributes


def export_options(figma_export_settings) -> ExportOptions:
    return ExportOptions(
        exportFormats=[
            ExportFormat(
                fileFormat=s['imageType'].lower(),
                name=s['suffix'],
                **export_scale(s['constraint']))
            for s in figma_export_settings])


class _ExportScale(TypedDict):
    absoluteSize: int
    scale: float
    visibleScaleType: VisibleScaleType


def export_scale(figma_constraint) -> _ExportScale:
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
        'cornerStyle': 0,
        'curveFrom': '{0, 0}',
        'curveMode': adjust_curve_mode(figma_point, 'STRAIGHT'),
        'curveTo': '{0, 0}',
        'hasCurveFrom': False,
        'hasCurveTo': False,
        'point': utils.x_y_to_string(x, y)
    }


def adjust_curve_mode(figma_point, default_value):
    if 'style' in figma_point and 'handleMirroring' in figma_point['style']:
        return CURVE_MODES[figma_point['style']['handleMirroring']]

    return CURVE_MODES[default_value]


def adjust_corner_radius(figma_node, figma_point):
    if 'style' in figma_point and 'cornerRadius' in figma_point['style']:
        return figma_point['style']['cornerRadius']

    return figma_node['cornerRadius']


# resizingConstraint is a bitfield:
#  1: right sizeable
#  2: width sizeable
#  4: left sizeable
#  8: bottom sizeable
# 16: height sizeable
# 32: top sizeable
# 64: all fixed (should be 0 but it's overridden to mean all sizeable, same as 63). Impossible
HORIZONTAL_CONSTRAINT = {
    'MIN': 1,  # Fixed left + width
    'CENTER': 5,  # Fixed width
    'MAX': 4,  # Fixed right + width
    'STRETCH': 2,  # Fixed left and right
    'SCALE': 7,  # All free
    # 'FIXED_MIN': 0, # Unused?
    # 'FIXED_MAX': 0, # Unused?
}


# Vertical constraints are equivalent to horizontal ones, with a 3 bit shift
def resizing_constraint(figma_node):
    h = HORIZONTAL_CONSTRAINT[figma_node.horizontalConstraint]
    v = HORIZONTAL_CONSTRAINT[figma_node.verticalConstraint] << 3
    return h + v


ANIMATION_TYPE = {
    'INSTANT_TRANSITION': -1,
    'SLIDE_FROM_LEFT': 1,
    'SLIDE_FROM_RIGHT': 0,
    'SLIDE_FROM_TOP': 3,
    'SLIDE_FROM_BOTTOM': 2,
    'PUSH_FROM_LEFT': 1,
    'PUSH_FROM_RIGHT': 0,
    'PUSH_FROM_TOP': 3,
    'PUSH_FROM_BOTTOM': 2,
    'MOVE_FROM_LEFT': 1,
    'MOVE_FROM_RIGHT': 0,
    'MOVE_FROM_TOP': 3,
    'MOVE_FROM_BOTTOM': 2,
    'SLIDE_OUT_TO_LEFT': 1,
    'SLIDE_OUT_TO_RIGHT': 0,
    'SLIDE_OUT_TO_TOP': 3,
    'SLIDE_OUT_TO_BOTTOM': 2,
    'MOVE_OUT_TO_LEFT': 1,
    'MOVE_OUT_TO_RIGHT': 0,
    'MOVE_OUT_TO_TOP': 3,
    'MOVE_OUT_TO_BOTTOM': 2,
    'MAGIC_MOVE': -1,
    'SMART_ANIMATE': -1,
    'SCROLL_ANIMATE': -1,
}


# TODO: Is this called from every node type (groups?)
def prototyping_flow(figma_node):
    # TODO: Overlays
    # TODO: What happens with multiple actions?
    flow = None
    for interaction in figma_node.get('prototypeInteractions', []):
        if interaction['isDeleted']:
            continue

        if interaction['event']['interactionType'] != 'ON_CLICK':
            print('Unsupported interaction type')
            continue

        for action in interaction['actions']:
            # TODO: Back is SCROLL for some reason??? or just irrelevant?
            if action['navigationType'] not in ['NAVIGATE', 'SCROLL']:
                print('Unsupported action type')
                continue

            if flow is not None:
                print('Unsupported multiple actions per layer')
                continue

            # TODO: Connection type
            if action['connectionType'] == 'BACK':
                destination = 'back'
            elif action['connectionType'] == 'INTERNAL_NODE':
                if 'transitionNodeID' in action:
                    destination = utils.gen_object_id((action['transitionNodeID']['sessionID'],
                                                       action['transitionNodeID']['localID']))
                else:
                    destination = None
            elif action['connectionType'] == 'NONE':
                destination = None
            else:
                print(f"Unsupported connection type {action['connectionType']}")
                continue

            flow = {
                '_class': 'MSImmutableFlowConnection',
                'animationType': ANIMATION_TYPE[
                    action.get('transitionType', 'INSTANT_TRANSITION')],
                'maintainScrollPosition': action.get('transitionPreserveScroll', False),
                'shouldCloseExistingOverlays': False  # TODO ???
            }

            if destination is not None:
                flow['destinationArtboardID'] = destination

    return {'flow': flow} if flow else {}
