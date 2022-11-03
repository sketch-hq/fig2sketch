from .style import Color
from dataclasses import dataclass, field, InitVar
from enum import IntEnum
from typing import Optional, List, Dict
from .layer_common import AbstractStyledLayer
from .common import Point


class TextVerticalAlignment(IntEnum):
    TOP = 0
    MIDDLE = 1
    BOTTOM = 2


class TextAlignment(IntEnum):
    LEFT = 0
    RIGHT = 1
    CENTER = 2
    JUSTIFIED = 3


class TextTransform(IntEnum):
    NONE = 0
    UPPERCASE = 1
    LOWERCASE = 2


class UnderlineStyle(IntEnum):
    NONE = 0
    SINGLE = 1


class TextBehaviour(IntEnum):
    FLEXIBLE_WIDTH = 0
    FIXED_WIDTH = 1
    FIXED_WIDTH_AND_HEIGHT = 2


class Bounds:
    def __init__(self, pos: Point, size: Point):
        self.pos = pos
        self.size = size

    def to_json(self):
        return f"{{{self.pos.to_json()}, {self.size.to_json()}}}"


@dataclass(kw_only=True)
class ParagraphStyle:
    _class: str = field(default='paragraphStyle')
    alignment: TextAlignment
    minimumLineHeight: Optional[float] = None
    maximumLineHeight: Optional[float] = None


@dataclass(kw_only=True)
class FontDescriptor:
    _class: str = field(default='fontDescriptor')
    attributes: Dict = field(default_factory=dict)
    name: InitVar[str]
    size: InitVar[float]

    def __post_init__(self, name, size):
        self.attributes = {
            'name': name,
            'size': size
        }


@dataclass(kw_only=True)
class EncodedAttributes:
    MSAttributedStringFontAttribute: FontDescriptor
    MSAttributedStringColorAttribute: Color
    textStyleVerticalAlignmentKey: TextVerticalAlignment
    MSAttributedStringTextTransformAttribute: Optional[TextTransform] = None
    underlineStyle: Optional[UnderlineStyle] = None
    strikethroughStyle: Optional[UnderlineStyle] = None
    kerning: float
    paragraphStyle: ParagraphStyle


@dataclass(kw_only=True)
class StringAttribute:
    _class: str = field(default='stringAttribute')
    location: int
    length: int
    attributes: EncodedAttributes


@dataclass(kw_only=True)
class AttributedString:
    _class: str = field(default='attributedString')
    string: str
    attributes: List[StringAttribute]


@dataclass(kw_only=True)
class Text(AbstractStyledLayer):
    _class: str = field(default='text')
    automaticallyDrawOnUnderlyingPath: bool = False
    dontSynchroniseWithSymbol: bool = False
    attributedString: AttributedString
    glyphBounds: Bounds
    lineSpacingBehaviour: int = 2 # This is more or less a version number
    textBehaviour: TextBehaviour


@dataclass(kw_only=True)
class TextStyle:
    _class: str = field(default='textStyle')
    encodedAttributes: EncodedAttributes
    verticalAlignment: TextVerticalAlignment
