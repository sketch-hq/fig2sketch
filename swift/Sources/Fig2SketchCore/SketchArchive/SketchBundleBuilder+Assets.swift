import Foundation
import ImageIO
import UniformTypeIdentifiers

extension SketchBundleBuilder {
    struct PreparedImageAssets {
        var refsBySourceName: [String: String]
        var entries: [SketchBundle.Entry]
        var warnings: [SketchBundleBuildWarning]
    }

    static func prepareImageAssets(
        for document: ConversionDocument,
        assets: ConversionAssets,
        options: SketchBundleBuildOptions
    ) -> PreparedImageAssets {
        let referenced = referencedImageSourceNames(in: document)
        var refsBySourceName: [String: String] = [:]
        var entries: [SketchBundle.Entry] = []
        var emittedByOutputPath: Set<String> = []
        var warnings: [SketchBundleBuildWarning] = []

        for sourceName in referenced.sorted() {
            guard let sourceData = assets.imagesBySourceName[sourceName] else {
                refsBySourceName[sourceName] = "images/f2s_missing"
                continue
            }

            let prepared: PreparedSketchImageData
            switch prepareImageDataForSketch(sourceData, forceConvertImages: options.forceConvertImages) {
            case .success(let value):
                prepared = value
            case .corrupted:
                refsBySourceName[sourceName] = "images/f2s_corrupted"
                warnings.append(.init(
                    code: options.forceConvertImages ? "IMG002" : "IMG001",
                    sourceName: sourceName
                ))
                continue
            case .processingError(let detail):
                refsBySourceName[sourceName] = "images/f2s_corrupted"
                warnings.append(.init(code: "IMG004", sourceName: sourceName, detail: detail))
                continue
            }

            let fileRef = ConverterUtils.generateFileRef(prepared.data)
            let outputPath = "images/\(fileRef)\(prepared.fileExtension)"
            refsBySourceName[sourceName] = outputPath

            if emittedByOutputPath.insert(outputPath).inserted {
                entries.append(.init(path: outputPath, data: prepared.data))
            }
        }

        return PreparedImageAssets(refsBySourceName: refsBySourceName, entries: entries, warnings: warnings)
    }

    private static func referencedImageSourceNames(in document: ConversionDocument) -> Set<String> {
        var names: Set<String> = []
        for page in document.pages {
            for layer in page.layers {
                collectReferencedImageSourceNames(in: layer, output: &names)
            }
        }
        return names
    }

    private static func collectReferencedImageSourceNames(in layer: ConversionLayer, output: inout Set<String>) {
        switch layer {
        case .rectangle(let rect):
            guard let style = rect.style else { return }
            for paint in style.fills {
                if case .image(let image) = paint.kind { output.insert(image.sourceName) }
            }
            for border in style.borders {
                if case .image(let image) = border.paint.kind { output.insert(image.sourceName) }
            }
        case .shapePath(let shape):
            guard let style = shape.style else { return }
            for paint in style.fills {
                if case .image(let image) = paint.kind { output.insert(image.sourceName) }
            }
            for border in style.borders {
                if case .image(let image) = border.paint.kind { output.insert(image.sourceName) }
            }
        case .group(let group):
            if let style = group.style {
                for paint in style.fills {
                    if case .image(let image) = paint.kind { output.insert(image.sourceName) }
                }
                for border in style.borders {
                    if case .image(let image) = border.paint.kind { output.insert(image.sourceName) }
                }
            }
            for child in group.layers {
                collectReferencedImageSourceNames(in: child, output: &output)
            }
        case .artboard(let artboard):
            if let style = artboard.style {
                for paint in style.fills {
                    if case .image(let image) = paint.kind { output.insert(image.sourceName) }
                }
                for border in style.borders {
                    if case .image(let image) = border.paint.kind { output.insert(image.sourceName) }
                }
            }
            for child in artboard.layers {
                collectReferencedImageSourceNames(in: child, output: &output)
            }
        case .symbolMaster(let master):
            if let style = master.style {
                for paint in style.fills {
                    if case .image(let image) = paint.kind { output.insert(image.sourceName) }
                }
                for border in style.borders {
                    if case .image(let image) = border.paint.kind { output.insert(image.sourceName) }
                }
            }
            for child in master.layers {
                collectReferencedImageSourceNames(in: child, output: &output)
            }
        case .symbolInstance(let instance):
            if let style = instance.style {
                for paint in style.fills {
                    if case .image(let image) = paint.kind { output.insert(image.sourceName) }
                }
                for border in style.borders {
                    if case .image(let image) = border.paint.kind { output.insert(image.sourceName) }
                }
            }
        case .text(let text):
            guard let style = text.style else { return }
            for paint in style.fills {
                if case .image(let image) = paint.kind { output.insert(image.sourceName) }
            }
            for border in style.borders {
                if case .image(let image) = border.paint.kind { output.insert(image.sourceName) }
            }
        }
    }

    private struct PreparedSketchImageData {
        var data: Data
        var fileExtension: String
    }

    private enum PreparedSketchImageResult {
        case success(PreparedSketchImageData)
        case corrupted
        case processingError(String)
    }

    private static func prepareImageDataForSketch(_ sourceData: Data, forceConvertImages: Bool) -> PreparedSketchImageResult {
        let sourceIsPNG = isPNG(sourceData)
        let sourceIsJPEG = isJPEG(sourceData)

        guard imageCanBeDecoded(sourceData) else {
            // Best-effort parity with Python's force flag: preserve raw PNG/JPEG bytes when forced.
            if forceConvertImages, sourceIsPNG {
                return .success(PreparedSketchImageData(data: sourceData, fileExtension: ".png"))
            }
            if forceConvertImages, sourceIsJPEG {
                return .success(PreparedSketchImageData(data: sourceData, fileExtension: ""))
            }
            return .corrupted
        }

        if sourceIsPNG {
            return .success(PreparedSketchImageData(data: sourceData, fileExtension: ".png"))
        }
        if sourceIsJPEG {
            return .success(PreparedSketchImageData(data: sourceData, fileExtension: ""))
        }
        guard let transcoded = transcodeToPNG(sourceData) else {
            return .processingError("ImageIO failed to transcode image to PNG")
        }
        return .success(PreparedSketchImageData(data: transcoded, fileExtension: ".png"))
    }

    private static func isPNG(_ data: Data) -> Bool {
        data.starts(with: Data([0x89, 0x50, 0x4E, 0x47]))
    }

    private static func isJPEG(_ data: Data) -> Bool {
        data.count >= 2 && data[data.startIndex] == 0xFF && data[data.startIndex.advanced(by: 1)] == 0xD8
    }

    private static func transcodeToPNG(_ data: Data) -> Data? {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil),
              let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
            return nil
        }

        let out = NSMutableData()
        guard let destination = CGImageDestinationCreateWithData(
            out as CFMutableData,
            UTType.png.identifier as CFString,
            1,
            nil
        ) else {
            return nil
        }

        CGImageDestinationAddImage(destination, image, nil)
        guard CGImageDestinationFinalize(destination) else { return nil }
        return out as Data
    }

    private static func imageCanBeDecoded(_ data: Data) -> Bool {
        guard let source = CGImageSourceCreateWithData(data as CFData, nil),
              CGImageSourceGetCount(source) > 0,
              CGImageSourceCreateImageAtIndex(source, 0, nil) != nil else {
            return false
        }
        return true
    }
}
