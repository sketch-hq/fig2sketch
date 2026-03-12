import Foundation

public struct KiwiBinaryReader {
    public enum Error: Swift.Error, Equatable {
        case unexpectedEOF
        case invalidUTF8
    }

    private let bytes: [UInt8]
    private(set) var offset: Int = 0

    public init(data: Data) {
        self.bytes = [UInt8](data)
    }

    public mutating func byte() throws -> UInt8 {
        guard offset < bytes.count else {
            throw Error.unexpectedEOF
        }
        defer { offset += 1 }
        return bytes[offset]
    }

    public mutating func bool() throws -> Bool {
        try byte() > 0
    }

    public mutating func uint() throws -> UInt32 {
        var value: UInt32 = 0
        for shift in stride(from: 0, through: 35, by: 7) {
            let b = try UInt32(byte())
            value |= (b & 127) << UInt32(shift)
            if b < 128 {
                break
            }
        }
        return value
    }

    public mutating func uint64() throws -> UInt64 {
        var value: UInt64 = 0
        for shift in stride(from: 0, through: 63, by: 7) {
            let b = try UInt64(byte())
            value |= (b & 127) << UInt64(shift)
            if b < 128 {
                break
            }
        }
        return value
    }

    public mutating func int() throws -> Int32 {
        let v = try uint()
        return (v & 1) == 1 ? Int32(bitPattern: ~(v >> 1)) : Int32(v >> 1)
    }

    public mutating func int64() throws -> Int64 {
        let v = try uint64()
        return (v & 1) == 1 ? Int64(bitPattern: ~(v >> 1)) : Int64(v >> 1)
    }

    public mutating func float() throws -> Float {
        let first = try byte()
        if first == 0 {
            return 0
        }

        let b1 = try UInt32(byte())
        let b2 = try UInt32(byte())
        let b3 = try UInt32(byte())

        var bits = UInt32(first) | (b1 << 8) | (b2 << 16) | (b3 << 24)
        bits = ((bits << 23) | (bits >> 9))
        return Float(bitPattern: bits)
    }

    public mutating func string() throws -> String {
        var collected: [UInt8] = []
        while true {
            let b = try byte()
            if b == 0 {
                break
            }
            collected.append(b)
        }

        guard let string = String(bytes: collected, encoding: .utf8) else {
            throw Error.invalidUTF8
        }
        return string
    }
}
