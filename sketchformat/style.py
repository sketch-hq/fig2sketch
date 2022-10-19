from dataclasses import dataclass, field, asdict
from enum import IntEnum
from typing import Optional, List


class LineCapStyle(IntEnum):
    BUTT = 0
    ROUND = 1
    SQUARE = 2


class LineJoinStyle(IntEnum):
    MITER = 0
    ROUND = 1
    BEVEL = 2


class FillType(IntEnum):
    COLOR = 0
    GRADIENT = 1
    PATTERN = 4


class BorderPosition(IntEnum):
    CENTER = 0
    INSIDE = 1
    OUTSIDE = 2


class BlendMode(IntEnum):
    NORMAL = 0
    DARKEN = 1
    MULTIPLY = 2
    COLOR_BURN = 3
    LIGHTEN = 4
    SCREEN = 5
    COLOR_DODGE = 6
    OVERLAY = 7
    SOFT_LIGHT = 8
    HARD_LIGHT = 9
    DIFFERENCE = 10
    EXCLUSION = 11
    HUE = 12
    SATURATION = 13
    COLOR = 14
    LUMINOSITY = 15
    PLUS_DARKER = 16
    PLUS_LIGHTER = 17


class GradientType(IntEnum):
    LINEAR = 0
    RADIAL = 1
    ANGULAR = 2


class PatternFillType(IntEnum):
    TILE = 0
    FILL = 1
    STRETCH = 2
    FIT = 3


class WindingRule(IntEnum):
    NON_ZERO = 0
    EVEN_ODD = 1


class MarkerType(IntEnum):
    NONE = 0
    OPEN_ARROW = 1
    FILLED_ARROW = 2
    LINE = 3
    OPEN_CIRCLE = 4
    FILLED_CIRCLE = 5
    OPEN_SQUARE = 6
    FILLED_SQUARE = 7


class BlurType(IntEnum):
    GAUSSIAN = 0
    MOTION = 1
    ZOOM = 2
    BACKGROUND = 3


@dataclass(kw_only=True)
class Color:
    _class: str = field(default='color', init=False)
    red: float
    green: float
    blue: float
    alpha: float
    swatchID: Optional[str] = None

    @staticmethod
    def Black():
        return Color(red=0, green=0, blue=0, alpha=1)

    @staticmethod
    def White():
        return Color(red=1, green=1, blue=1, alpha=1)

    @staticmethod
    def Translucent():
        return Color(red=0, green=0, blue=0, alpha=0.5)

    @staticmethod
    def DefaultFill():
        return Color(red=0.847, green=0.847, blue=0.847, alpha=1)

    @staticmethod
    def DefaultBorder():
        return Color(red=0.592, green=0.592, blue=0.592, alpha=1)


@dataclass(kw_only=True)
class GradientStop:
    _class: str = field(default='gradientStop', init=False)
    color: Color
    position: float


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_json(self):
        return f"{{{self.x}, {self.y}}}"

    def from_array(array):
        return Point(x=array[0], y=array[1])


@dataclass(kw_only=True)
class Gradient:
    _class: str = field(default='gradient', init=False)
    gradientType: GradientType = GradientType.LINEAR
    elipseLength: float = 0
    from_: Point = Point(0.5, 0)
    to: Point = Point(0.5, 1)
    stops: List[GradientStop] = field(
        default_factory=lambda: [GradientStop(color=Color.White(), position=0),
                                 GradientStop(color=Color.Black(), position=1)])

    @staticmethod
    def Linear(from_: Point, to: Point, stops: List[GradientStop]):
        return Gradient(
            gradientType=GradientType.LINEAR,
            from_=from_,
            to=to,
            stops=stops
        )

    @staticmethod
    def Radial(from_: Point, to: Point, elipseLength: float, stops: List[GradientStop]):
        return Gradient(
            gradientType=GradientType.RADIAL,
            from_=from_,
            to=to,
            elipseLength=elipseLength,
            stops=stops
        )

    @staticmethod
    def Angular(stops: List[GradientStop]):
        return Gradient(
            gradientType=GradientType.ANGULAR,
            stops=stops
        )


@dataclass(kw_only=True)
class ContextSettings:
    _class: str = field(default='graphicsContextSettings', init=False)
    blendMode: BlendMode = BlendMode.NORMAL
    opacity: float = 1


@dataclass
class Image:
    _class: str = field(default='MSJSONFileReference', init=False)
    _ref_class: str = field(default='MSImageData', init=False)
    _ref: str


@dataclass(kw_only=True)
class Fill:
    _class: str = field(default='fill', init=False)
    fillType: FillType
    isEnabled: bool = True
    color: Color = field(default_factory=Color.DefaultFill)
    noiseIndex: int = 0
    noiseIntensity: float = 0
    patternFillType: PatternFillType = PatternFillType.TILE
    patternTileScale: float = 1
    contextSettings: ContextSettings = field(default_factory=ContextSettings)
    gradient: Gradient = field(default_factory=Gradient)
    image: Optional[Image] = None

    @staticmethod
    def Color(color: Color, isEnabled: bool):
        return Fill(
            color=color,
            fillType=FillType.COLOR,
            isEnabled=isEnabled
        )

    @staticmethod
    def Gradient(gradient: Gradient, isEnabled: bool):
        return Fill(
            gradient=gradient,
            fillType=FillType.GRADIENT,
            isEnabled=isEnabled
        )

    @staticmethod
    def Image(path: str, patternFillType: PatternFillType, isEnabled: bool):
        return Fill(
            image=Image(path),
            fillType=FillType.PATTERN,
            patternFillType=patternFillType,
            isEnabled=isEnabled
        )


@dataclass(kw_only=True)
class Border:
    _class: str = field(default='border', init=False)
    fillType: FillType
    position: BorderPosition
    thickness: int
    isEnabled: bool = True
    color: Color = field(default_factory=Color.DefaultBorder)
    contextSettings: ContextSettings = field(default_factory=ContextSettings)
    gradient: Gradient = field(default_factory=Gradient)

    @staticmethod
    def from_fill(fill: Fill, position: BorderPosition, thickness: int) -> 'Border':
        return Border(
            fillType=fill.fillType,
            color=fill.color,
            gradient=fill.gradient,
            contextSettings=fill.contextSettings,

            position=position,
            thickness=thickness
        )


@dataclass(kw_only=True)
class ColorControls:
    _class: str = field(default='colorControls', init=False)
    isEnabled: bool = False
    brightness: float = 0
    contrast: float = 1
    hue: float = 0
    saturation: float = 1


@dataclass(kw_only=True)
class BorderOptions:
    _class: str = field(default='borderOptions', init=False)
    isEnabled: bool = True
    lineCapStyle: LineCapStyle = LineCapStyle.BUTT
    lineJoinStyle: LineJoinStyle = LineJoinStyle.MITER
    dashPattern: List[int] = field(default_factory=list)


@dataclass(kw_only=True)
class Blur:
    _class: str = field(default='blur', init=False)
    isEnabled: bool = True
    center: Point = field(default_factory=lambda: Point(0.5, 0.5))
    motionAngle: float = 0
    radius: float = 10
    saturation: float = 1
    type: BlurType = BlurType.GAUSSIAN

    @staticmethod
    def Disabled():
        return Blur(isEnabled=False)


@dataclass(kw_only=True)
class Shadow:
    _class: str = field(default='shadow', init=False)
    blurRadius: float
    offsetX: float
    offsetY: float
    spread: float
    isEnabled: bool = True
    color: Color = field(default_factory=Color.Translucent)
    contextSettings: ContextSettings = field(default_factory=ContextSettings)


@dataclass(kw_only=True)
class InnerShadow(Shadow):
    _class: str = field(default='innerShadow', init=False)


@dataclass(kw_only=True)
class TextStyle:
    pass


@dataclass(kw_only=True)
class Style:
    _class: str = field(default='style', init=False)
    do_objectID: str
    borderOptions: BorderOptions = field(default_factory=BorderOptions)
    borders: List[Border] = field(default_factory=list)
    fills: List[Fill] = field(default_factory=list)
    miterLimit: int = 10
    windingRule: WindingRule = WindingRule.NON_ZERO
    contextSettings: ContextSettings = field(default_factory=ContextSettings)
    colorControls: ColorControls = field(default_factory=ColorControls)
    startMarkerType: MarkerType = MarkerType.NONE
    endMarkerType: MarkerType = MarkerType.NONE
    blur: Blur = field(default_factory=Blur.Disabled)
    textStyle: Optional[TextStyle] = None
    shadows: List[Shadow] = field(default_factory=list)
    innerShadows: List[InnerShadow] = field(default_factory=list)
    startDecorationType: Optional[MarkerType] = None
    endDecorationType: Optional[MarkerType] = None

    def set_markers(self, startMarkerType: MarkerType, endMarkerType: MarkerType):
        self.startMarkerType = startMarkerType
        self.endMarkerType = endMarkerType

        # Legacy properties, can be skipped. Doing this to match Sketch exactly
        # TODO: Should we remove this?
        if startMarkerType > 0 or endMarkerType > 0:
            if startMarkerType < 4:
                self.startDecorationType = startMarkerType
            if endMarkerType < 4:
                self.endDecorationType = endMarkerType

