import FigFormat
import Foundation
import ZIPFoundation

public enum CLIConversionRunner {
    @discardableResult
    public static func run(options: CLIOptions, output: inout some CLIOutput) -> Int32 {
        do {
            let inputURL = URL(fileURLWithPath: options.figFile)
            let outputURL = URL(fileURLWithPath: options.sketchFile)

            let decoded = try FigTreeDecoder.decodeFigFile(url: inputURL)
            if let warning = KiwiCanvasDecoder.warningMessage(forVersion: decoded.version),
               options.verbosity > 0 {
                output.writeErr("\(warning)\n")
            }

            if let dumpPath = options.dumpFigJSONPath {
                try FigDumpJSONWriter.write(decoded: decoded, to: URL(fileURLWithPath: dumpPath))
            }

            let tree = try FigTreeDecoder.buildTree(from: decoded.rootMessage)
            if options.verbosity > 0 {
                for warning in FigStyleWarningScanner.scan(tree: tree) {
                    output.writeErr(FigStyleWarningScanner.message(for: warning) + "\n")
                }
            }
            let mappingOptions = FigTreeMappingOptions(
                detachUnsupportedInstanceOverrides: options.instanceOverride == .detach
            )
            let document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree, options: mappingOptions)
            let resolvedAssets = FigImageAssetResolver.resolve(
                tree: tree,
                decoded: decoded,
                zipImagesBySourceName: extractArchiveImagesBySourceName(fromFigAt: inputURL)
            )
            if options.verbosity > 0 {
                for sourceName in resolvedAssets.missingSourceNames {
                    output.writeErr(SketchBundleBuildWarning(code: "IMG003", sourceName: sourceName).message + "\n")
                }
            }

            let salt = effectiveSalt(from: options)
            let buildResult = SketchBundleBuilder.buildResult(
                from: document,
                salt: salt,
                assets: resolvedAssets.assets,
                options: SketchBundleBuildOptions(forceConvertImages: options.forceConvertImages)
            )
            for warning in buildResult.fontWarningMessages {
                output.writeErr("\(warning)\n")
            }
            if options.verbosity > 0 {
                for warning in buildResult.warnings {
                    output.writeErr(warning.message + "\n")
                }
            }

            var bundle = buildResult.bundle
            if let preview = extractPreviewPNG(fromFigAt: inputURL) {
                bundle.entries.insert(.init(path: "previews/preview.png", data: preview), at: 0)
            }

            let writer = ZIPSketchArchiveWriter()
            let compression: SketchArchiveCompression = options.compress ? .deflated : .stored
            try writer.write(bundle: bundle, to: outputURL, compression: compression)

            if options.verbosity > 0 {
                output.writeOut("Wrote \(bundle.entries.count) entries to \(options.sketchFile)\n")
            }
            return EX_OK
        } catch KiwiDecoderError.unsupportedCanvasFigVersion(let version) {
            output.writeErr("\(KiwiCanvasDecoder.errorMessageForUnsupportedOldVersion(version))\n")
            return Int32(EX_DATAERR)
        } catch {
            output.writeErr("Swift converter error: \(error)\n")
            return Int32(EX_SOFTWARE)
        }
    }

    private static func effectiveSalt(from options: CLIOptions) -> Data {
        if let salt = options.salt {
            return Data(salt.utf8)
        }
        return Data(UUID().uuidString.utf8)
    }

    private static func extractPreviewPNG(fromFigAt url: URL) -> Data? {
        let archive: Archive
        do {
            archive = try Archive(url: url, accessMode: .read)
        } catch {
            return nil
        }

        guard let entry = archive["thumbnail.png"] else {
            return nil
        }

        var preview = Data()
        do {
            _ = try archive.extract(entry) { chunk in
                preview.append(chunk)
            }
            return preview
        } catch {
            return nil
        }
    }

    private static func extractArchiveImagesBySourceName(fromFigAt url: URL) -> [String: Data] {
        let archive: Archive
        do {
            archive = try Archive(url: url, accessMode: .read)
        } catch {
            return [:]
        }

        var images: [String: Data] = [:]
        for entry in archive where entry.type == .file && entry.path.hasPrefix("images/") {
            let sourceName = String(entry.path.dropFirst("images/".count))
            guard !sourceName.isEmpty else { continue }
            var data = Data()
            do {
                _ = try archive.extract(entry) { chunk in
                    data.append(chunk)
                }
                images[sourceName] = data
            } catch {
                continue
            }
        }
        return images
    }
}
