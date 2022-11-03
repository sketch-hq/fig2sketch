from enum import IntEnum
from dataclasses import dataclass


class WindingRule(IntEnum):
    NON_ZERO = 0
    EVEN_ODD = 1


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def to_json(self) -> str:
        return f"{{{self.x}, {self.y}}}"

    @staticmethod
    def from_array(array) -> 'Point':
        return Point(x=array[0], y=array[1])

    @staticmethod
    def from_dict(dict) -> 'Point':
        return Point(dict['x'], dict['y'])

    def __eq__(self, other) -> bool:
        if (isinstance(other, Point)):
            return self.x == other.x and self.y == other.y
        return False

    def __add__(self, other) -> 'Point':
        return Point(
            self.x + other.x,
            self.y + other.y
        )
