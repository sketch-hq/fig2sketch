import Foundation
import ZIPFoundation

public enum SketchArchiveCompression: Sendable {
    case stored
    case deflated
}

public protocol SketchArchiveWriting: Sendable {
    func write(bundle: SketchBundle, to outputURL: URL, compression: SketchArchiveCompression) throws
}

public enum SketchArchiveWriterError: Error, Equatable {
    case couldNotCreateArchive(URL)
}

public struct ZIPSketchArchiveWriter: SketchArchiveWriting {
    public init() {}

    public func write(bundle: SketchBundle, to outputURL: URL, compression: SketchArchiveCompression) throws {
        let fileManager = FileManager.default
        if fileManager.fileExists(atPath: outputURL.path) {
            try fileManager.removeItem(at: outputURL)
        }

        let archive: Archive
        do {
            archive = try Archive(url: outputURL, accessMode: .create)
        } catch {
            throw SketchArchiveWriterError.couldNotCreateArchive(outputURL)
        }

        let method: CompressionMethod = switch compression {
        case .stored:
            .none
        case .deflated:
            .deflate
        }

        for entry in bundle.entries {
            let data = entry.data
            try archive.addEntry(
                with: entry.path,
                type: .file,
                uncompressedSize: Int64(data.count),
                compressionMethod: method,
                provider: { position, size in
                    let start = Int(position)
                    let end = min(start + size, data.count)
                    return data.subdata(in: start..<end)
                }
            )
        }
    }
}
