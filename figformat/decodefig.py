import io
import zlib
import struct
import sys
from kiwi import *

figma = open(sys.argv[1], 'rb').read()

offset = 12
segments = []
while offset < len(figma):
    size = struct.unpack('<I', figma[offset:offset+4])[0]
    offset += 4
    data = figma[offset:offset+size]
    if not data.startswith(b'\x89PNG'):
        data = zlib.decompress(data, wbits=-15)
    offset += size
    segments.append(data)

schema = KiwiSchema(io.BytesIO(segments[0]))
print(KiwiDecoder(schema).decode(io.BytesIO(segments[1]), "Message"))
