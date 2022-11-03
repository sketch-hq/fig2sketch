from .layer_common import *
from dataclasses import dataclass, field
from .common import WindingRule


@dataclass(kw_only=True)
class RulerData:
    _class: str = field(default='rulerData')
    base: int = 0
    guides: List[int] = field(default_factory=list)


@dataclass(kw_only=True)
class SimpleGrid:
    _class: str = field(default='simpleGrid')
    gridSize: int = 8
    thickGridTimes: int = 1
    isEnabled: bool = False


@dataclass(kw_only=True)
class LayoutGrid:
    _class: str = field(default='layoutGrid')
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
    _class: str = field(default='MSImmutableFreeformGroupLayout')


@dataclass(kw_only=True)
class InferredGroupLayout:
    _class: str = field(default='MSImmutableInferredGroupLayout')
    axis: LayoutAxis
    layoutAnchor: LayoutAnchor
    maxSize: int = 0
    minSize: int = 0


@dataclass(kw_only=True)
class AbstractLayerGroup(AbstractStyledLayer):
    hasClickThrough: bool = False
    groupLayout: Union[FreeFormGroupLayout, InferredGroupLayout] = field(
        default_factory=FreeFormGroupLayout)
    layers: List[AbstractLayer] = field(default_factory=list)


@dataclass(kw_only=True)
class Page(AbstractLayerGroup):
    _class: str = field(default='page')
    horizontalRulerData: RulerData = field(default_factory=RulerData)
    verticalRulerData: RulerData = field(default_factory=RulerData)
    grid: SimpleGrid = field(default_factory=SimpleGrid)
    layout: Optional[LayoutGrid] = None


@dataclass(kw_only=True)
class ShapeGroup(AbstractLayerGroup):
    _class: str = field(default='shapeGroup')
    windingRule: WindingRule = WindingRule.NON_ZERO # Legacy, should match style.windingRule
