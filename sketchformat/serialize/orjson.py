import orjson
import logging
from dataclasses import dataclass, field
from typing import Optional, IO
import io


def serialize(obj: object, file: IO[bytes]) -> None:
    file.write(orjson.dumps(obj, default=lambda x: x.to_json(), option=orjson.OPT_SERIALIZE_NUMPY))

# Check if orjson is patched
@dataclass
class Test:
    _class: str = field(default='rectangle')
    optional: Optional[str] = None

b = io.BytesIO()
serialize(Test(), b)
b.seek(0)
if b.read() != b'{"_class":"rectangle"}':
    b.seek(0)
    print(b.read())
    logging.debug("Unpatched orjson detected. Falling back to built-in json")
    raise Exception()
