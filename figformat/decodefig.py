import zlib
import struct
import sys

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

for i, s in enumerate(segments):
    open(f'segment{i}.data', 'wb').write(s)

