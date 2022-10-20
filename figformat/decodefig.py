import io
import zlib
import zipfile
import struct
from .kiwi import *
import numpy as np

SUPPORTED_VERSION = 20


def decode(reader):
    figma_zip = None

    header = reader.read(2)
    reader.seek(0)
    if header == b'PK':
        figma_zip = zipfile.ZipFile(reader)
        reader = figma_zip.open('canvas.fig')

    figma = reader.read()
    fig_version = struct.unpack('<I', figma[8:12])[0]
    if fig_version != SUPPORTED_VERSION:
        raise Exception(
            f"Unsupported Figma version. File = {fig_version} / Supported = {SUPPORTED_VERSION}")

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

    type_converters = {
        'GUID': lambda x: (x['sessionID'], x['localID']),
        'Matrix': lambda m: np.array([[m['m00'], m['m01'], m['m02']], [m['m10'], m['m11'], m['m12']], [0, 0, 1]])
    }
    schema = KiwiSchema(io.BytesIO(segments[0]))
    return KiwiDecoder(schema, type_converters).decode(io.BytesIO(segments[1]), 'Message'), figma_zip
