import Foundation

enum SHAKE128 {
    private static let rateBytes = 168 // 1344-bit rate for SHAKE128

    private static let roundConstants: [UInt64] = [
        0x0000000000000001, 0x0000000000008082,
        0x800000000000808A, 0x8000000080008000,
        0x000000000000808B, 0x0000000080000001,
        0x8000000080008081, 0x8000000000008009,
        0x000000000000008A, 0x0000000000000088,
        0x0000000080008009, 0x000000008000000A,
        0x000000008000808B, 0x800000000000008B,
        0x8000000000008089, 0x8000000000008003,
        0x8000000000008002, 0x8000000000000080,
        0x000000000000800A, 0x800000008000000A,
        0x8000000080008081, 0x8000000000008080,
        0x0000000080000001, 0x8000000080008008,
    ]

    // Indexed as x + 5*y
    private static let rhoOffsets: [UInt64] = [
        0, 1, 62, 28, 27,
        36, 44, 6, 55, 20,
        3, 10, 43, 25, 39,
        41, 45, 15, 21, 8,
        18, 2, 61, 56, 14,
    ]

    static func digest(data: Data, outputByteCount: Int) -> Data {
        precondition(outputByteCount >= 0)
        var state = [UInt64](repeating: 0, count: 25)
        absorb(data, into: &state)
        return squeeze(from: &state, outputByteCount: outputByteCount)
    }

    private static func absorb(_ data: Data, into state: inout [UInt64]) {
        let bytes = [UInt8](data)
        var offset = 0

        while offset + rateBytes <= bytes.count {
            xorBlock(bytes[offset..<(offset + rateBytes)], into: &state)
            keccakF1600(&state)
            offset += rateBytes
        }

        var finalBlock = [UInt8](repeating: 0, count: rateBytes)
        let remaining = bytes.count - offset
        if remaining > 0 {
            for i in 0..<remaining {
                finalBlock[i] = bytes[offset + i]
            }
        }

        // SHAKE domain suffix = 0x1F, then pad10*1
        finalBlock[remaining] ^= 0x1F
        finalBlock[rateBytes - 1] ^= 0x80
        xorBlock(finalBlock[0..<rateBytes], into: &state)
        keccakF1600(&state)
    }

    private static func squeeze(from state: inout [UInt64], outputByteCount: Int) -> Data {
        if outputByteCount == 0 { return Data() }

        var output = [UInt8]()
        output.reserveCapacity(outputByteCount)

        while output.count < outputByteCount {
            for laneIndex in 0..<(rateBytes / 8) {
                let lane = state[laneIndex]
                for byteOffset in 0..<8 {
                    if output.count == outputByteCount { break }
                    output.append(UInt8((lane >> (8 * byteOffset)) & 0xFF))
                }
                if output.count == outputByteCount { break }
            }

            if output.count < outputByteCount {
                keccakF1600(&state)
            }
        }

        return Data(output)
    }

    private static func xorBlock<C: Collection>(_ block: C, into state: inout [UInt64]) where C.Element == UInt8 {
        var iterator = block.makeIterator()
        for laneIndex in 0..<(rateBytes / 8) {
            var lane: UInt64 = 0
            for shift in stride(from: 0, to: 64, by: 8) {
                guard let byte = iterator.next() else { break }
                lane |= UInt64(byte) << UInt64(shift)
            }
            state[laneIndex] ^= lane
        }
    }

    private static func keccakF1600(_ a: inout [UInt64]) {
        precondition(a.count == 25)
        var b = [UInt64](repeating: 0, count: 25)
        var c = [UInt64](repeating: 0, count: 5)
        var d = [UInt64](repeating: 0, count: 5)

        @inline(__always)
        func idx(_ x: Int, _ y: Int) -> Int { x + 5 * y }

        for rc in roundConstants {
            // Theta
            for x in 0..<5 {
                c[x] = a[idx(x, 0)] ^ a[idx(x, 1)] ^ a[idx(x, 2)] ^ a[idx(x, 3)] ^ a[idx(x, 4)]
            }
            for x in 0..<5 {
                d[x] = c[(x + 4) % 5] ^ rotateLeft(c[(x + 1) % 5], by: 1)
            }
            for y in 0..<5 {
                for x in 0..<5 {
                    a[idx(x, y)] ^= d[x]
                }
            }

            // Rho + Pi
            for y in 0..<5 {
                for x in 0..<5 {
                    let sourceIndex = idx(x, y)
                    let targetIndex = idx(y, (2 * x + 3 * y) % 5)
                    b[targetIndex] = rotateLeft(a[sourceIndex], by: rhoOffsets[sourceIndex])
                }
            }

            // Chi
            for y in 0..<5 {
                for x in 0..<5 {
                    a[idx(x, y)] = b[idx(x, y)] ^ ((~b[idx((x + 1) % 5, y)]) & b[idx((x + 2) % 5, y)])
                }
            }

            // Iota
            a[idx(0, 0)] ^= rc
        }
    }

    @inline(__always)
    private static func rotateLeft(_ value: UInt64, by amount: UInt64) -> UInt64 {
        let n = amount & 63
        if n == 0 { return value }
        return (value << n) | (value >> (64 - n))
    }
}
