import random
from dataclasses import dataclass


@dataclass
class Config:
    can_detach: bool = True
    import_variants: bool = False
    salt: bytes = random.randbytes(16)
    version: str = "?"


config = Config()
