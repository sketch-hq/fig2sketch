import io
import zlib
import zipfile
import struct
from .kiwi import *


def decode(reader):
    figma_zip = None
    figma = reader.read()

    if figma.startswith(b'PK'):
        figma_zip = zipfile.ZipFile(io.BytesIO(figma))
        figma = figma_zip.open('canvas.fig').read()

    offset = 12
    segments = []
    while offset < len(figma):
        size = struct.unpack('<I', figma[offset:offset + 4])[0]
        offset += 4
        data = figma[offset:offset + size]
        if not data.startswith(b'\x89PNG'):
            data = zlib.decompress(data, wbits=-15)
        offset += size
        segments.append(data)

    schema = KiwiSchema(io.BytesIO(segments[0]))
    return KiwiDecoder(schema).decode(io.BytesIO(segments[1]), 'Message'), figma_zip
