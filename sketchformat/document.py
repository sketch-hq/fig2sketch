from dataclasses import dataclass, field
from typing import List
from .style import Color


@dataclass(kw_only=True)
class JsonFileReference:
    _class: str = field(default='MSJSONFileReference')
    _ref_class: str
    _ref: str


@dataclass(kw_only=True)
class FontReference:
    _class: str = field(default='fontReference')
    do_objectID: str
    fontData: JsonFileReference
    fontFamilyName: str
    fontFileName: str
    options: int = 3 # Embedded and used
    postscriptNames: List[str]


@dataclass(kw_only=True)
class Swatch:
    _class: str = field(default='swatch')
    do_objectID: str
    name: str
    value: Color
