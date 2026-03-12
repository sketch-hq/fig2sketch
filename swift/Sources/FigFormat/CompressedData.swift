import CZstd
import Foundation
import zlib

enum RawDeflate {
    enum Error: Swift.Error, Equatable {
        case inflateInit(Int32)
        case inflateFailed(Int32)
    }

    static func decompress(data: Data) throws -> Data {
        if data.isEmpty { return Data() }

        var stream = z_stream()
        var status = inflateInit2_(&stream, -MAX_WBITS, ZLIB_VERSION, Int32(MemoryLayout<z_stream>.size))
        guard status == Z_OK else {
            throw Error.inflateInit(status)
        }
        defer { inflateEnd(&stream) }

        var output = Data()
        let chunkSize = 16 * 1024

        try data.withUnsafeBytes { (inputBuffer: UnsafeRawBufferPointer) in
            guard let baseAddress = inputBuffer.baseAddress else { return }
            stream.next_in = UnsafeMutablePointer<Bytef>(mutating: baseAddress.assumingMemoryBound(to: Bytef.self))
            stream.avail_in = uInt(inputBuffer.count)

            var chunk = [UInt8](repeating: 0, count: chunkSize)
            let chunkCount = chunk.count

            repeat {
                let produced: Int = try chunk.withUnsafeMutableBytes { outputBuffer in
                    guard let base = outputBuffer.baseAddress else { return 0 }
                    stream.next_out = base.assumingMemoryBound(to: Bytef.self)
                    stream.avail_out = uInt(chunkCount)

                    status = inflate(&stream, Z_NO_FLUSH)
                    if status != Z_OK && status != Z_STREAM_END {
                        throw Error.inflateFailed(status)
                    }

                    return chunkCount - Int(stream.avail_out)
                }
                if produced > 0 {
                    output.append(chunk, count: produced)
                }
            } while status != Z_STREAM_END
        }

        return output
    }
}

enum FramedZstd {
    enum Error: Swift.Error, Equatable {
        case invalidFrame
        case decompressFailed(String)
    }

    static func decompress(data: Data) throws -> Data {
        if data.isEmpty { return Data() }

        return try data.withUnsafeBytes { sourceBuffer in
            guard let sourceBase = sourceBuffer.baseAddress else { return Data() }

            let sourceSize = sourceBuffer.count
            let frameSize = ZSTD_getFrameContentSize(sourceBase, sourceSize)
            let contentSizeError = UInt64(ZSTD_CONTENTSIZE_ERROR)
            let contentSizeUnknown = UInt64(ZSTD_CONTENTSIZE_UNKNOWN)
            if frameSize == contentSizeError {
                throw Error.invalidFrame
            }

            let destinationCapacity: Int
            if frameSize == contentSizeUnknown {
                throw Error.decompressFailed("unknown frame content size")
            } else {
                destinationCapacity = Int(frameSize)
            }

            var output = Data(count: destinationCapacity)
            let written = output.withUnsafeMutableBytes { destinationBuffer -> size_t in
                guard let destinationBase = destinationBuffer.baseAddress else { return 0 }
                return ZSTD_decompress(destinationBase, destinationBuffer.count, sourceBase, sourceSize)
            }

            if ZSTD_isError(written) != 0 {
                throw Error.decompressFailed(zstdErrorString(written))
            }

            if written < output.count {
                output.removeSubrange(Int(written)..<output.count)
            }
            return output
        }
    }

    private static func zstdErrorString(_ code: size_t) -> String {
        if let cString = ZSTD_getErrorName(code) {
            return String(cString: cString)
        }
        return "unknown"
    }
}
