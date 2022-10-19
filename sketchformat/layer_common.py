from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional, List, Union
from xml.dom.pulldom import default_bufsize
from .style import Style


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


class BooleanOperation(IntEnum):
    NONE = -1
    UNION = 0
    SUBTRACT = 1
    INTERSECT = 2
    DIFFERENCE = 3


class LayerListStatus(IntEnum):
    UNDECIDED = 0
    COLLAPSED = 1
    EXPANDED  = 2


class ClippingMaskMode(IntEnum):
    OUTLINE = 0
    ALPHA = 1


class ResizeType(IntEnum):
    STRETCH = 0
    PIN_TO_EDGE = 1
    RESIZE = 2
    FLOAT = 2


class AnimationType(IntEnum):
    NONE = 0
    SLIDE_FROM_LEFT = 1
    SLIDE_FROM_RIGHT = 2
    SLIDE_FROM_BOTTOM = 3
    SLIDE_FROM_TOP = 4


class LayoutAxis(IntEnum):
    HORIZONTAL = 0
    VERTICAL = 1


class LayoutAnchor(IntEnum):
    MIN = 0
    MIDDLE = 1
    MAX = 2


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


@dataclass(kw_only=True)
class Rect:
    _class: str = field(default='rect', init=False)
    constrainProportions: bool = False
    height: float
    width: float
    x: float
    y: float


@dataclass(kw_only=True)
class FlowConnection:
    _class: str = field(default='MSImmutableFlowConnection', init=False)
    destinationArtboardID: str
    animationType: AnimationType = AnimationType.NONE
    maintainScrollPosition: bool = False


@dataclass(kw_only=True)
class AbstractLayer:
    do_objectID: str
    booleanOperation: BooleanOperation = BooleanOperation.NONE
    exportOptions: ExportOptions = field(default_factory=ExportOptions)
    frame: Rect
    flow: Optional[FlowConnection] = None
    isFixedToViewport: bool = False
    isFlippedHorizontal: bool = False
    isFlippedVertical: bool = False
    isLocked: bool = False
    isTemplate: bool = False
    isVisible: bool = True
    layerListExpandedType: LayerListStatus = LayerListStatus.UNDECIDED
    name: str
    nameIsFixed: bool = False
    resizingConstraint: int
    resizingType: ResizeType = ResizeType.STRETCH
    rotation: float
    sharedStyleID: Optional[str] = None
    shouldBreakMaskChain: bool = False
    hasClippingMask: bool = False
    clippingMaskMode: ClippingMaskMode = ClippingMaskMode.OUTLINE
    style: Style = field(default_factory=Style)
    maintainScrollPosition: bool = False


@dataclass(kw_only=True)
class RulerData:
    _class: str = field(default='rulerData', init=False)
    base: int = 0
    guides: List[int] = field(default_factory=list)


@dataclass(kw_only=True)
class SimpleGrid:
    _class: str = field(default='simpleGrid', init=False)
    gridSize: int = 8
    thickGridTimes: int = 1
    isEnabled: bool = False


@dataclass(kw_only=True)
class LayoutGrid:
    _class: str = field(default='layoutGrid', init=False)
    columnWidth: int = 0
    gutterHeight: int = 0
    gutterWidth: int = 0
    horizontalOffset: int = 0
    numberOfColumns: int = 0
    rowHeightMultiplication: int = 0
    totalWidth: int = 0
    guttersOutside: bool = False
    drawHorizontal: bool = False
    drawHorizontalLines: bool = False
    drawVertical: bool = False


@dataclass(kw_only=True)
class FreeFormGroupLayout:
    _class: str = field(default='MSImmutableFreeformGroupLayout', init=False)


@dataclass(kw_only=True)
class InferredGroupLayout:
    _class: str = field(default='MSImmutableInferredGroupLayout', init=False)
    axis: LayoutAxis
    layoutAnchor: LayoutAnchor
    maxSize: int = 0
    minSize: int = 0


@dataclass(kw_only=True)
class AbstractRootLayer(AbstractLayer):
    hasClickThrough: bool = False
    horizontalRulerData: RulerData = field(default_factory=RulerData)
    verticalRulerData: RulerData = field(default_factory=RulerData)
    grid: Optional[SimpleGrid] = None
    layout: Optional[LayoutGrid] = None
    groupLayout: Union[FreeFormGroupLayout,InferredGroupLayout] = field(default_factory=FreeFormGroupLayout)
    layers: List[AbstractLayer] = field(default_factory=list)


@dataclass(kw_only=True)
class Page(AbstractRootLayer):
    _class: str = field(default='page', init=False)
