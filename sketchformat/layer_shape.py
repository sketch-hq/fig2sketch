from .layer_common import AbstractLayer
from .common import Point
from enum import IntEnum
from typing import List, NamedTuple
from dataclasses import dataclass, field, InitVar


class PointRadiusBehaviour(IntEnum):
    V0 = 0
    V1 = 1
    V1_SMOOTH = 2


class CornerStyle(IntEnum):
    ROUNDED = 0
    ROUNDED_INVERTED = 1
    ANGLED = 2
    SQUARED = 3


class CurveMode(IntEnum):
    UNDEFINED = 0
    STRAIGHT = 1
    MIRRORED = 2
    ASYMMETRIC = 3
    DISCONNECTED = 4


@dataclass(kw_only=True)
class CurvePoint:
    _class: str = field(default='curvePoint')
    curveFrom: Point
    curveTo: Point
    point: Point
    cornerRadius: float = 0.0
    cornerStyle: CornerStyle = CornerStyle.ROUNDED
    hasCurveFrom: bool = False
    hasCurveTo: bool = False
    curveMode: CurveMode = CurveMode.UNDEFINED

    @staticmethod
    def Straight(point: Point, radius: float = 0.0) -> 'CurvePoint':
        return CurvePoint(
            curveFrom=point,
            curveTo=point,
            point=point,
            cornerRadius=radius,
            curveMode=CurveMode.STRAIGHT
        )


@dataclass(kw_only=True)
class AbstractShapeLayer(AbstractLayer):
    isClosed: bool
    points: List[CurvePoint]
    edited: bool = False
    pointRadiusBehaviour: PointRadiusBehaviour = PointRadiusBehaviour.V1


@dataclass(kw_only=True)
class Rectangle(AbstractShapeLayer):
    class Corners(NamedTuple):
        topLeft: float
        topRight: float
        bottomRight: float
        bottomLeft: float

    corners: InitVar[Corners]
    _class: str = field(default='rectangle')
    fixedRadius: float = 0.0
    hasConvertedToNewRoundCorners: bool = True
    needsConvertionToNewRoundCorners: bool = False
    isClosed: bool = True
    # Override points with fixed rectangle coordinates
    points: List[CurvePoint] = field(default_factory=list)

    def __post_init__(self, corners):
        self.points = [
            CurvePoint.Straight(Point(0, 0), corners.topLeft),
            CurvePoint.Straight(Point(0, 1), corners.topRight),
            CurvePoint.Straight(Point(1, 1), corners.bottomRight),
            CurvePoint.Straight(Point(1, 0), corners.bottomLeft),
        ]
