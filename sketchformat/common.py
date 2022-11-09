from enum import IntEnum
from dataclasses import dataclass
from typing import Sequence, Dict, TypedDict


class WindingRule(IntEnum):
    NON_ZERO = 0
    EVEN_ODD = 1


class Point:
    class _DictXY(TypedDict, total=False):
        x: float
        y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def to_json(self) -> str:
        return f"{{{self.x}, {self.y}}}"

    @staticmethod
    def from_array(array: Sequence[float]) -> 'Point':
        return Point(x=array[0], y=array[1])

    @staticmethod
    def from_dict(dict: _DictXY) -> 'Point':
        return Point(dict['x'], dict['y'])

    def __eq__(self, other: object) -> bool:
        if (isinstance(other, Point)):
            return self.x == other.x and self.y == other.y
        return False

    def __add__(self, other: 'Point') -> 'Point':
        return Point(
            self.x + other.x,
            self.y + other.y
        )
