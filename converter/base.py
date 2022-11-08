import logging
import utils
from sketchformat.layer_common import *
from sketchformat.style import *
from typing import TypedDict

from . import positioning, style, prototype
from .context import context


SUPPORTED_INHERIT_STYLES = {
    'inheritFillStyleID': ('fillPaints',),
    'inheritFillStyleIDForStroke': None, # Special cased below
    'inheritStrokeStyleID': None,  # Unused in Figma?
    'inheritTextStyleID': (
        'fontName',
        'textCase',
        'fontSize',
        'textDecoration',
        'letterSpacing',
        'lineHeight',
        'paragraphSpacing'
    ),
    'inheritExportStyleID': None,  # Unused in Figma?
    'inheritEffectStyleID': ('blur', 'shadows', 'innerShadows'),
    'inheritGridStyleID': ('layoutGrids'),
    'inheritFillStyleIDForBackground': None,  # Unused in Figma?
}

def base_layer(figma_node):
    return {
        'do_objectID': utils.gen_object_id(figma_node['guid']),
        'name': figma_node['name'],
        'booleanOperation': -1,
        'exportOptions': export_options(figma_node.get('exportSettings', [])),
        **positioning.convert(figma_node),
        'isFixedToViewport': False,
        'isLocked': figma_node['locked'],
        'isVisible': figma_node['visible'],
        'layerListExpandedType': 0,
        'nameIsFixed': False,
        'resizingConstraint': resizing_constraint(figma_node),
        'resizingType': 0,
        **prototype.convert_flow(figma_node),
        'isTemplate': False
    }


def base_shape(figma_node):
    obj = {
        **base_layer(figma_node),
        **masking(figma_node),
        'style': process_styles(figma_node),
    }

    if obj['hasClippingMask'] and obj['clippingMaskMode'] == 0:
        # Outline mask behave differently in Figma and Sketch in regards to fill/stroke colors
        # Remove fill
        obj['style'].fills = []
        # TODO: If we have stroke, we should remove it and enlarge ourselves to occupy that space
        # which is quite tricky in things like shapePaths. This should be pretty rare in practice

    return obj


def process_styles(figma_node) -> Style:
    # First we apply any overrides that we may have (from inherit* properties)
    # If any of them can be linked as a shared style, we keep track of them to add the IDs at the end
    components = {}
    for inherit_style, copy_keys in SUPPORTED_INHERIT_STYLES.items():
        inherit_node_id = figma_node.get(inherit_style)
        if not inherit_node_id or inherit_node_id[0] == 4294967295:
            continue

        inherit_node, sketch_component = context.component(inherit_node_id)
        if inherit_style == 'inheritFillStyleIDForStroke':
            figma_node['strokePaints'] = inherit_node['fillPaints']
        elif inherit_style is not None:
            for key in copy_keys:
                if key in inherit_node:
                    figma_node[key] = inherit_node[key]
                else:
                    figma_node.pop(key, None)
        else:
            logger.warning(f"Unsupported {inherit_style}, it will not be copied")

        if sketch_component:
            components[inherit_style] = sketch_component

    st = style.convert(figma_node)

    for key, value in components.items():
        if key == 'inheritFillStyleID':
            st.fills[0].color = value.value
        elif key == 'inheritFillStyleIDForStroke':
            st.borders[0].color = value.value
        else:
            logger.error(f"Unexpected component for {key}")

    return st


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
                'visibleScaleType': VisibleScaleType.SCALE
            }
        case {'type': 'CONTENT_WIDTH', 'value': size}:
            return {
                'absoluteSize': size,
                'scale': 0,
                'visibleScaleType': VisibleScaleType.WIDTH
            }
        case {'type': 'CONTENT_HEIGHT', 'value': size}:
            return {
                'absoluteSize': size,
                'scale': 0,
                'visibleScaleType': VisibleScaleType.HEIGHT
            }
        case _:
            logging.warning("Unknown export scale")
            return {
                'absoluteSize': 0,
                'scale': 1,
                'visibleScaleType': VisibleScaleType.SCALE
            }


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
    h = HORIZONTAL_CONSTRAINT[figma_node['horizontalConstraint']]
    v = HORIZONTAL_CONSTRAINT[figma_node['verticalConstraint']] << 3
    return h + v


# TODO: Call this function from every shape/image/etc
# TODO: Check if image masks work
def masking(figma):
    CLIPPING_MODE = {
        'ALPHA': 1,
        'OUTLINE': 0,  # TODO This works differently in Sketch vs Figma
        # Sketch masks only the fill and draws border normally and fill as background
        # Figma masks including the borders and ignores the stroke/fill properties
        # 'LUMINANCE': UNSUPPORTED
    }
    sketch = {
        'shouldBreakMaskChain': False
    }
    if figma['mask']:
        sketch['hasClippingMask'] = True
        sketch['clippingMaskMode'] = CLIPPING_MODE[figma['maskType']]
    else:
        sketch['hasClippingMask'] = False
        sketch['clippingMaskMode'] = 0

    return sketch
