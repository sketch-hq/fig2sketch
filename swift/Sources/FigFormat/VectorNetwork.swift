import Foundation

public struct VectorScale: Equatable, Sendable {
    public var x: Double
    public var y: Double

    public init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }
}

public enum VectorResolvedStyle<Payload: Equatable & Sendable>: Equatable, Sendable {
    case override(Payload)
    case styleID(UInt32)
}

public struct VectorVertex<Payload: Equatable & Sendable>: Equatable, Sendable {
    public var x: Double
    public var y: Double
    public var style: VectorResolvedStyle<Payload>?

    public init(x: Double, y: Double, style: VectorResolvedStyle<Payload>? = nil) {
        self.x = x
        self.y = y
        self.style = style
    }
}

public struct VectorSegment: Equatable, Sendable {
    public var start: UInt32
    public var end: UInt32
    public var tangentStart: VectorVertex<NeverStyle>
    public var tangentEnd: VectorVertex<NeverStyle>

    public init(start: UInt32, end: UInt32, tangentStart: VectorVertex<NeverStyle>, tangentEnd: VectorVertex<NeverStyle>) {
        self.start = start
        self.end = end
        self.tangentStart = tangentStart
        self.tangentEnd = tangentEnd
    }
}

public enum VectorWindingRule: String, Equatable, Sendable {
    case odd = "ODD"
    case nonzero = "NONZERO"
}

public struct VectorRegion<Payload: Equatable & Sendable>: Equatable, Sendable {
    public var loops: [[UInt32]]
    public var style: VectorResolvedStyle<Payload>
    public var windingRule: VectorWindingRule

    public init(loops: [[UInt32]], style: VectorResolvedStyle<Payload>, windingRule: VectorWindingRule) {
        self.loops = loops
        self.style = style
        self.windingRule = windingRule
    }
}

public struct VectorNetwork<Payload: Equatable & Sendable>: Equatable, Sendable {
    public var regions: [VectorRegion<Payload>]
    public var segments: [VectorSegment]
    public var vertices: [VectorVertex<Payload>]

    public init(regions: [VectorRegion<Payload>], segments: [VectorSegment], vertices: [VectorVertex<Payload>]) {
        self.regions = regions
        self.segments = segments
        self.vertices = vertices
    }
}

// Marker payload used by tangent vertices, which never carry style data.
public enum NeverStyle: Equatable, Sendable {}

public enum VectorNetworkDecoder {
    public enum Error: Swift.Error, Equatable {
        case truncated(expectedAtLeast: Int, actual: Int)
    }

    public static func decode<Payload: Equatable & Sendable>(
        networkData: Data,
        scale: VectorScale,
        styleOverrideTable: [UInt32: Payload]
    ) throws -> VectorNetwork<Payload> {
        var cursor = ByteCursor(data: networkData)

        let numVertices = try cursor.readUInt32()
        let numSegments = try cursor.readUInt32()
        let numRegions = try cursor.readUInt32()

        var vertices: [VectorVertex<Payload>] = []
        vertices.reserveCapacity(Int(numVertices))

        for _ in 0..<numVertices {
            let styleID = try cursor.readUInt32()
            let x = try cursor.readFloat32()
            let y = try cursor.readFloat32()
            vertices.append(decodeVertex(x: x, y: y, scale: scale, styleOverrideTable: styleOverrideTable, styleID: styleID))
        }

        var segments: [VectorSegment] = []
        segments.reserveCapacity(Int(numSegments))

        for _ in 0..<numSegments {
            _ = try cursor.readUInt32() // style ID is currently unused, same as Python
            let v1 = try cursor.readUInt32()
            let t1x = try cursor.readFloat32()
            let t1y = try cursor.readFloat32()
            let v2 = try cursor.readUInt32()
            let t2x = try cursor.readFloat32()
            let t2y = try cursor.readFloat32()

            segments.append(
                decodeSegment(
                    v1: v1,
                    v2: v2,
                    t1x: t1x,
                    t1y: t1y,
                    t2x: t2x,
                    t2y: t2y,
                    scale: scale
                )
            )
        }

        var regions: [VectorRegion<Payload>] = []
        regions.reserveCapacity(Int(numRegions))

        for _ in 0..<numRegions {
            let flags = try cursor.readUInt32()
            let numLoops = try cursor.readUInt32()

            let windingRule: VectorWindingRule = (flags % 2 == 1) ? .nonzero : .odd
            let styleID = flags >> 1

            var loops: [[UInt32]] = []
            loops.reserveCapacity(Int(numLoops))
            for _ in 0..<numLoops {
                let numLoopVertices = try cursor.readUInt32()
                var loopVertices: [UInt32] = []
                loopVertices.reserveCapacity(Int(numLoopVertices))
                for _ in 0..<numLoopVertices {
                    loopVertices.append(try cursor.readUInt32())
                }
                loops.append(loopVertices)
            }

            let style: VectorResolvedStyle<Payload>
            if let override = styleOverrideTable[styleID] {
                style = .override(override)
            } else {
                style = .styleID(styleID)
            }

            regions.append(VectorRegion(loops: loops, style: style, windingRule: windingRule))
        }

        return VectorNetwork(regions: regions, segments: segments, vertices: vertices)
    }

    private static func decodeVertex<Payload: Equatable & Sendable>(
        x: Float,
        y: Float,
        scale: VectorScale,
        styleOverrideTable: [UInt32: Payload],
        styleID: UInt32? = nil
    ) -> VectorVertex<Payload> {
        let outX = (x == 0 || scale.x == 0) ? 0 : Double(x) / scale.x
        let outY = (y == 0 || scale.y == 0) ? 0 : Double(y) / scale.y

        guard let styleID, styleID != 0 else {
            return VectorVertex(x: outX, y: outY, style: nil)
        }

        if let override = styleOverrideTable[styleID] {
            return VectorVertex(x: outX, y: outY, style: .override(override))
        }
        return VectorVertex(x: outX, y: outY, style: .styleID(styleID))
    }

    private static func decodeSegment(
        v1: UInt32,
        v2: UInt32,
        t1x: Float,
        t1y: Float,
        t2x: Float,
        t2y: Float,
        scale: VectorScale
    ) -> VectorSegment {
        VectorSegment(
            start: v1,
            end: v2,
            tangentStart: decodeTangentVertex(x: t1x, y: t1y, scale: scale),
            tangentEnd: decodeTangentVertex(x: t2x, y: t2y, scale: scale)
        )
    }

    private static func decodeTangentVertex(x: Float, y: Float, scale: VectorScale) -> VectorVertex<NeverStyle> {
        let outX = (x == 0 || scale.x == 0) ? 0 : Double(x) / scale.x
        let outY = (y == 0 || scale.y == 0) ? 0 : Double(y) / scale.y
        return VectorVertex<NeverStyle>(x: outX, y: outY, style: nil)
    }
}

private struct ByteCursor {
    let data: [UInt8]
    private(set) var offset: Int = 0

    init(data: Data) {
        self.data = [UInt8](data)
    }

    mutating func readUInt32() throws -> UInt32 {
        let bytes = Array(try read(count: 4))
        return UInt32(bytes[0])
            | (UInt32(bytes[1]) << 8)
            | (UInt32(bytes[2]) << 16)
            | (UInt32(bytes[3]) << 24)
    }

    mutating func readFloat32() throws -> Float {
        Float(bitPattern: try readUInt32())
    }

    private mutating func read(count: Int) throws -> ArraySlice<UInt8> {
        guard offset + count <= data.count else {
            throw VectorNetworkDecoder.Error.truncated(expectedAtLeast: offset + count, actual: data.count)
        }
        let slice = data[offset..<(offset + count)]
        offset += count
        return slice
    }
}
