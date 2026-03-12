import FigFormat
import Foundation

struct FigImageAssetResolutionResult: Equatable {
    var assets: ConversionAssets
    var missingSourceNames: [String]
    var croppedSourceNames: [String]
}

enum FigImageAssetResolver {
    static func resolve(
        tree: FigTree,
        decoded: DecodedCanvasFig,
        zipImagesBySourceName: [String: Data]
    ) -> FigImageAssetResolutionResult {
        let refs = FigImageAssetScanner.collectReferences(from: tree)
        let embeddedBlobs = FigImageAssetScanner.extractEmbeddedBlobs(from: decoded)

        var resolved = zipImagesBySourceName
        var missing: [String] = []
        var cropped: [String] = []

        for ref in refs {
            if ref.hasCropTransform {
                cropped.append(ref.sourceName)
            }

            if resolved[ref.sourceName] != nil {
                continue
            }

            if let blobIndex = ref.embeddedBlobIndex,
               let blob = embeddedBlobs[blobIndex] {
                resolved[ref.sourceName] = blob
            } else {
                missing.append(ref.sourceName)
            }
        }

        return FigImageAssetResolutionResult(
            assets: ConversionAssets(imagesBySourceName: resolved),
            missingSourceNames: missing.sorted(),
            croppedSourceNames: Array(Set(cropped)).sorted()
        )
    }
}
