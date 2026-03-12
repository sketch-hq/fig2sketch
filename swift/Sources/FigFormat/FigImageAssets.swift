import Foundation

public struct FigImageAssetReference: Equatable, Sendable {
    public var sourceName: String
    public var embeddedBlobIndex: Int?
    public var hasCropTransform: Bool

    public init(sourceName: String, embeddedBlobIndex: Int?, hasCropTransform: Bool) {
        self.sourceName = sourceName
        self.embeddedBlobIndex = embeddedBlobIndex
        self.hasCropTransform = hasCropTransform
    }
}

public enum FigImageAssetScanner {
    public static func collectReferences(from tree: FigTree) -> [FigImageAssetReference] {
        var refsBySource: [String: FigImageAssetReference] = [:]

        func visit(_ node: FigTreeNode) {
            if let style = node.node.style {
                for paint in style.fills {
                    merge(referenceForPaint(paint), into: &refsBySource)
                }
                for border in style.borders {
                    merge(referenceForPaint(border.paint), into: &refsBySource)
                }
            }
            for child in node.children {
                visit(child)
            }
        }

        visit(tree.root)
        return refsBySource.values.sorted { $0.sourceName < $1.sourceName }
    }

    public static func extractEmbeddedBlobs(from decoded: DecodedCanvasFig) -> [Int: Data] {
        guard let root = decoded.rootMessage.objectValue,
              let blobs = root["blobs"]?.arrayValue else {
            return [:]
        }

        var output: [Int: Data] = [:]
        output.reserveCapacity(blobs.count)

        for (index, blobValue) in blobs.enumerated() {
            guard let blob = blobValue.objectValue,
                  let bytes = blob["bytes"]?.arrayValue,
                  let data = decodeByteArray(bytes) else {
                continue
            }
            output[index] = data
        }

        return output
    }

    private static func referenceForPaint(_ paint: FigPaint) -> FigImageAssetReference? {
        guard case .image(let image) = paint.kind else { return nil }
        return FigImageAssetReference(
            sourceName: image.sourceName,
            embeddedBlobIndex: image.embeddedBlobIndex,
            hasCropTransform: image.hasCropTransform
        )
    }

    private static func merge(_ ref: FigImageAssetReference?, into output: inout [String: FigImageAssetReference]) {
        guard let ref else { return }
        if let existing = output[ref.sourceName] {
            output[ref.sourceName] = FigImageAssetReference(
                sourceName: ref.sourceName,
                embeddedBlobIndex: existing.embeddedBlobIndex ?? ref.embeddedBlobIndex,
                hasCropTransform: existing.hasCropTransform || ref.hasCropTransform
            )
        } else {
            output[ref.sourceName] = ref
        }
    }

    private static func decodeByteArray(_ values: [KiwiValue]) -> Data? {
        var bytes: [UInt8] = []
        bytes.reserveCapacity(values.count)
        for value in values {
            switch value {
            case .byte(let v):
                bytes.append(v)
            case .uint(let v) where v <= UInt32(UInt8.max):
                bytes.append(UInt8(v))
            case .int(let v) where v >= 0 && v <= Int32(UInt8.max):
                bytes.append(UInt8(v))
            default:
                return nil
            }
        }
        return Data(bytes)
    }
}
