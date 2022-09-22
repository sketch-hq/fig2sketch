import struct

network = b'\x05\x00\x00\x00\x05\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9c \x12\x84fA\x00\x00\x00\x00\x00\x00\x1cB\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9cB\x12\x84fA\x00\x00\x00\x00\x00\x00\x9cB\x82\xd0\xa2B\x00\x00\x00\x00\x00\x00\x9c \x82\xd0\xa2B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x03?\xbe\xc1\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x03?\xbeA\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00'

i = 0
num_vertices = struct.unpack('<I', network[i:i + 4])[0]
i += 4
num_segments = struct.unpack('<I', network[i:i + 4])[0]
i += 4
num_regions = struct.unpack('<I', network[i:i + 4])[0]
i += 4

for vertex in range(num_vertices):
    # Should include stroke cap/limit, corner radius, mirroring, etc.
    flags = struct.unpack('<I', network[i:i + 4])[0]

    # Coordinates
    x, y = struct.unpack('<ff', network[i + 4:i + 12])

    print('VERTEX', x, y, flags)
    i += 12

for segment in range(num_segments):
    # No idea what it's for
    flags = struct.unpack('<I', network[i:i + 4])[0]

    # Start vertex + tangent vector
    v1 = struct.unpack('<I', network[i + 4:i + 8])[0]
    t1x, t1y = struct.unpack('<ff', network[i + 8:i + 16])

    # End vertex + tangent vector
    v2 = struct.unpack('<I', network[i + 16:i + 20])[0]
    t2x, t2y = struct.unpack('<ff', network[i + 20:i + 28])

    print('SEGMENT', v1, v2, t1x, t1y, t2x, t2y, flags)
    i += 28

for region in range(num_regions):
    # Flags should include winding rule
    flags, num_loops = struct.unpack('<II', network[i:i + 8])
    i += 8
    loops = []
    for loop in range(num_loops):
        num_loop_vertices = struct.unpack('<I', network[i:i + 4])[0]
        i += 4
        loop_vertices = []
        for vertex in range(num_loop_vertices):
            loop_vertices.append(struct.unpack('<I', network[i:i + 4])[0])
            i += 4
        loops.append(loop_vertices)
    print('REGION', loops)
