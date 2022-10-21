from .layer_common import AbstractRootLayer
from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Page(AbstractRootLayer):
    _class: str = field(default='page', init=False)
