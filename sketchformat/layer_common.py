from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional, List


class ExportLayerOptions(IntEnum):
    ALL = 0
    SELECTED = 1
    IN_GROUP = 2


class ExportNamingScheme(IntEnum):
    SUFFIX = 0
    SECONDARY_PREFIX = 1
    PRIMARY_PREFIX = 2


class VisibleScaleType(IntEnum):
    SCALE = 0
    WIDTH = 1
    HEIGHT = 2


@dataclass(kw_only=True)
class ExportFormat:
    _class: str = field(default='exportFormat', init=False)
    absoluteSize: int = 0
    fileFormat: str
    name: str
    namingScheme: ExportNamingScheme = ExportNamingScheme.PRIMARY_PREFIX
    scale: float = 1
    visibleScaleType: VisibleScaleType


@dataclass(kw_only=True)
class ExportOptions:
    _class: str = field(default='exportOptions', init=False)
    exportFormats: List[ExportFormat] = field(default_factory=list)
    includedLayerIds: List[str] = field(default_factory=list)
    layerOptions: ExportLayerOptions = ExportLayerOptions.ALL
    shouldTrim: bool = False


# class AbstractLayer:
#   do_objectID: str
#   booleanOperation: { $ref: ../enums/boolean-operation.schema.yaml }
#   exportOptions: { $ref: ../objects/export-options.schema.yaml }
#   frame: { $ref: ../objects/rect.schema.yaml }
#   flow: { $ref: ../objects/flow-connection.schema.yaml }
#   isFixedToViewport: bool
#   isFlippedHorizontal: bool
#   isFlippedVertical: bool
#   isLocked: bool
#   isTemplate: bool
#   isVisible: bool
#   layerListExpandedType: { $ref: ../enums/layer-list-expanded.schema.yaml }
#   name: { type: string }
#   nameIsFixed: bool
#   resizingConstraint: int
#   resizingType: { $ref: ../enums/resize-type.schema.yaml }
#   rotation: { type: number }
#   sharedStyleID: { $ref: ../utils/uuid.schema.yaml }
#   shouldBreakMaskChain: bool
#   hasClippingMask: bool
#   clippingMaskMode: { type: integer }
#   userInfo:
#     type: object
#     additionalProperties: true
#   style: { $ref: ../objects/style.schema.yaml }
#   maintainScrollPosition: bool

# class AbstractRootLayer:
#       hasClickThrough: bool
#       horizontalRulerData: { $ref: ../objects/ruler-data.schema.yaml }
#       verticalRulerData: { $ref: ../objects/ruler-data.schema.yaml }
#       layout: { $ref: ../objects/layout-grid.schema.yaml }
#       grid: { $ref: ../objects/simple-grid.schema.yaml }
#       groupLayout:
#         oneOf:
#           - { $ref: ../objects/freeform-group-layout.schema.yaml }
#           - { $ref: ../objects/inferred-group-layout.schema.yaml }

# class Page:
#           _class: { const: page }
#       layers:
