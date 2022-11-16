import io
import zipfile
import zlib
import struct
from .kiwi import *
from converter.positioning import Matrix
import logging

SUPPORTED_VERSIONS = [15, 20]

def decode(path):
    type_converters = {
        'GUID': lambda x: (x['sessionID'], x['localID']),
        'Matrix': lambda m: Matrix(
            [[m['m00'], m['m01'], m['m02']], [m['m10'], m['m11'], m['m12']], [0, 0, 1]])
    }

    # Open file and check if it's a zip
    fig_zip = None
    reader = open(path, 'rb')
    header = reader.read(2)
    reader.seek(0)
    if header == b'PK':
        fig_zip = zipfile.ZipFile(reader)

    try:
        import fig_kiwi
        logging.debug("Using fast (rust) kiwi reader")
        return fig_kiwi.decode(path, type_converters), fig_zip

    except ImportError:
        logging.debug("Falling back to slow (python) kiwi reader")


    if fig_zip:
        reader = fig_zip.open('canvas.fig')

    fig = reader.read()
    fig_version = struct.unpack('<I', fig[8:12])[0]
    if fig_version not in SUPPORTED_VERSIONS:
        raise Exception(
            f"Unsupported .fig version. File = {fig_version} / Supported = {SUPPORTED_VERSIONS}")

    offset = 12
    segments = []
    while offset < len(fig):
        size = struct.unpack('<I', fig[offset:offset + 4])[0]
        offset += 4
        data = fig[offset:offset + size]
        if not data.startswith(b'\x89PNG'):
            data = zlib.decompress(data, wbits=-15)
        offset += size
        segments.append(data)


    schema = KiwiSchema(io.BytesIO(segments[0]))
    return KiwiDecoder(schema, type_converters).decode(io.BytesIO(segments[1]), 'Message'), fig_zip
