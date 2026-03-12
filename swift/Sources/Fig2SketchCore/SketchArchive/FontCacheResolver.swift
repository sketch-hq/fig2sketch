import CoreText
import Foundation

struct PreparedFontAssets {
    var references: [SketchJSONValue]
    var entries: [SketchBundle.Entry]
    var warningMessages: [String]
}

enum FontCacheResolver {
    struct Environment: Sendable {
        struct FetchResponse: Sendable {
            var data: Data
            var statusCode: Int?
        }

        var cacheDirectoryURL: @Sendable () -> URL?
        var listDirectoryContents: @Sendable (URL) throws -> [URL]
        var createDirectory: @Sendable (URL) throws -> Void
        var fileExists: @Sendable (URL) -> Bool
        var readData: @Sendable (URL) throws -> Data
        var writeData: @Sendable (Data, URL) throws -> Void
        var fetch: @Sendable (URL) throws -> FetchResponse
        var fontMetadata: @Sendable (URL) -> (family: String?, style: String?, postscript: String?)

        static let live = Environment(
            cacheDirectoryURL: {
                FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first?
                    .appendingPathComponent("Fig2Sketch/fonts", isDirectory: true)
            },
            listDirectoryContents: { directory in
                try FileManager.default.contentsOfDirectory(
                    at: directory,
                    includingPropertiesForKeys: nil,
                    options: [.skipsHiddenFiles]
                )
            },
            createDirectory: { directory in
                try FileManager.default.createDirectory(
                    at: directory,
                    withIntermediateDirectories: true
                )
            },
            fileExists: { url in
                FileManager.default.fileExists(atPath: url.path)
            },
            readData: { url in
                try Data(contentsOf: url)
            },
            writeData: { data, url in
                try data.write(to: url, options: .atomic)
            },
            fetch: liveFetch(url:),
            fontMetadata: fontMetadata(for:)
        )
    }

    private struct FontResolutionWarning: Hashable {
        enum Kind: Hashable {
            case missingFromGoogleFonts
            case downloadFailed(detail: String)
        }

        var family: String
        var style: String
        var kind: Kind

        var message: String {
            let descriptor = "('\(family)', '\(style)')"
            switch kind {
            case .missingFromGoogleFonts:
                return "Could not find font \(descriptor) via Google Fonts"
            case .downloadFailed(let detail):
                return "Could not download font \(descriptor): \(detail)"
            }
        }
    }

    private struct GoogleFontsManifest: Decodable {
        struct Manifest: Decodable {
            var fileRefs: [FileRef]
        }

        struct FileRef: Decodable {
            var filename: String
            var url: String
        }

        var manifest: Manifest
    }

    private enum WebFontFetchError: Error, CustomStringConvertible {
        case httpStatus(Int)
        case invalidManifest
        case invalidDownloadURL(String)
        case noMatchingFont

        var description: String {
            switch self {
            case .httpStatus(let statusCode):
                return "HTTP \(statusCode)"
            case .invalidManifest:
                return "invalid Google Fonts manifest"
            case .invalidDownloadURL(let value):
                return "invalid download URL \(value)"
            case .noMatchingFont:
                return "requested font was not present in the Google Fonts family download"
            }
        }
    }

    static func prepareFontAssets(
        for document: ConversionDocument,
        environment: Environment = .live
    ) -> PreparedFontAssets {
        let requests = collectFontRequests(in: document)
        guard !requests.isEmpty else {
            return .init(references: [], entries: [], warningMessages: [])
        }

        guard let fontsDirectory = environment.cacheDirectoryURL() else {
            return .init(references: [], entries: [], warningMessages: [])
        }
        try? environment.createDirectory(fontsDirectory)

        var records = loadCachedFontRecords(in: fontsDirectory, environment: environment)
        var warningMessages: [String] = []
        var fetchedFamilies: Set<String> = []

        var selected: [String: SelectedFont] = [:]
        for request in requests {
            var record = matchRecord(for: request, in: records)
            if record == nil,
               let family = request.family,
               let style = request.style {
                let normalizedFamily = normalized(family)
                if !fetchedFamilies.contains(normalizedFamily) {
                    do {
                        let downloadedRecords = try fetchGoogleFontRecords(
                            family: family,
                            style: style,
                            into: fontsDirectory,
                            environment: environment
                        )
                        if !downloadedRecords.isEmpty {
                            records.append(contentsOf: downloadedRecords)
                            fetchedFamilies.insert(normalizedFamily)
                        }
                    } catch {
                        warningMessages.append(
                            warningMessage(for: error, family: family, style: style)
                        )
                    }
                    record = matchRecord(for: request, in: records)
                    if record == nil, fetchedFamilies.contains(normalizedFamily) {
                        warningMessages.append(
                            FontResolutionWarning(
                                family: family,
                                style: style,
                                kind: .missingFromGoogleFonts
                            ).message
                        )
                    }
                }
            }

            guard let record else { continue }
            guard selected[record.hash] == nil else { continue }
            let naming = naming(for: request, record: record)
            let postscript = request.postscript ?? record.postscript ?? "\(naming.family)-\(naming.style)"
            selected[record.hash] = .init(
                hash: record.hash,
                data: record.data,
                family: naming.family,
                style: naming.style,
                postscript: postscript
            )
        }

        let sortedFonts = selected.values.sorted { lhs, rhs in
            if lhs.objectID == rhs.objectID {
                return lhs.hash < rhs.hash
            }
            return lhs.objectID < rhs.objectID
        }

        let references = sortedFonts.map(fontReferenceJSON)
        let entries = sortedFonts
            .sorted(by: { $0.hash < $1.hash })
            .map { SketchBundle.Entry(path: "fonts/\($0.hash)", data: $0.data) }

        return .init(
            references: references,
            entries: entries,
            warningMessages: orderedUnique(warningMessages)
        )
    }

    private struct FontRequest: Hashable {
        var family: String?
        var style: String?
        var postscript: String?
    }

    private struct CachedFontRecord {
        var url: URL
        var data: Data
        var hash: String
        var family: String?
        var style: String?
        var postscript: String?
    }

    private struct SelectedFont {
        var hash: String
        var data: Data
        var family: String
        var style: String
        var postscript: String

        var objectID: String {
            let salt = Data(hexString: hash) ?? Data(hash.utf8)
            return ConverterUtils.genObjectID(figID: [0, 0], salt: salt)
        }
    }

    private static func collectFontRequests(in document: ConversionDocument) -> [FontRequest] {
        var requests: Set<FontRequest> = []
        for page in document.pages {
            for layer in page.layers {
                collectFontRequests(in: layer, into: &requests)
            }
        }
        return requests.sorted(by: fontRequestSortKey)
    }

    private static func collectFontRequests(in layer: ConversionLayer, into requests: inout Set<FontRequest>) {
        switch layer {
        case .group(let group):
            for child in group.layers {
                collectFontRequests(in: child, into: &requests)
            }
        case .artboard(let artboard):
            for child in artboard.layers {
                collectFontRequests(in: child, into: &requests)
            }
        case .symbolMaster(let master):
            for child in master.layers {
                collectFontRequests(in: child, into: &requests)
            }
        case .text(let text):
            if let family = text.fontFamily, !isEmojiFont(family) {
                let style = text.fontStyle?.trimmingCharacters(in: .whitespacesAndNewlines)
                requests.insert(.init(
                    family: family,
                    style: style?.isEmpty == false ? style : "Regular",
                    postscript: nil
                ))
            }
            for run in text.attributeRuns {
                insertRunFontRequest(fontName: run.fontName, into: &requests)
            }
        case .rectangle, .shapePath, .symbolInstance:
            break
        }
    }

    private static func insertRunFontRequest(fontName: String, into requests: inout Set<FontRequest>) {
        let trimmed = fontName.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty, !isEmojiFont(trimmed) else { return }

        if let parsed = parseFamilyAndStyle(fromFontName: trimmed) {
            requests.insert(.init(
                family: parsed.family,
                style: parsed.style,
                postscript: trimmed
            ))
            return
        }

        requests.insert(.init(
            family: nil,
            style: nil,
            postscript: trimmed
        ))
    }

    private static func fontRequestSortKey(_ lhs: FontRequest, _ rhs: FontRequest) -> Bool {
        let left = [
            lhs.family ?? "",
            lhs.style ?? "",
            lhs.postscript ?? "",
        ].joined(separator: "|")
        let right = [
            rhs.family ?? "",
            rhs.style ?? "",
            rhs.postscript ?? "",
        ].joined(separator: "|")
        return left < right
    }

    private static func loadCachedFontRecords(
        in fontsDirectory: URL,
        environment: Environment
    ) -> [CachedFontRecord] {
        guard let urls = try? environment.listDirectoryContents(fontsDirectory) else {
            return []
        }

        return loadCachedFontRecords(from: urls, environment: environment)
    }

    private static func loadCachedFontRecords(
        from urls: [URL],
        environment: Environment
    ) -> [CachedFontRecord] {
        let fontURLs = urls
            .filter(isSupportedFontURL(_:))
            .sorted(by: { $0.lastPathComponent < $1.lastPathComponent })

        var records: [CachedFontRecord] = []
        records.reserveCapacity(fontURLs.count)
        for url in fontURLs {
            guard let data = try? environment.readData(url) else { continue }
            let metadata = environment.fontMetadata(url)
            records.append(.init(
                url: url,
                data: data,
                hash: ConverterUtils.generateFileRef(data),
                family: metadata.family,
                style: metadata.style,
                postscript: metadata.postscript
            ))
        }
        return records
    }

    private static func fetchGoogleFontRecords(
        family: String,
        style: String,
        into fontsDirectory: URL,
        environment: Environment
    ) throws -> [CachedFontRecord] {
        let listURL = googleFontsListURL(for: family)
        let manifestResponse = try environment.fetch(listURL)
        if let statusCode = manifestResponse.statusCode, statusCode >= 400 {
            throw WebFontFetchError.httpStatus(statusCode)
        }

        let manifest = try decodeGoogleFontsManifest(from: manifestResponse.data)
        let downloadedURLs = try downloadGoogleFontFiles(
            from: manifest.manifest.fileRefs,
            into: fontsDirectory,
            environment: environment
        )
        let downloadedRecords = loadCachedFontRecords(from: downloadedURLs, environment: environment)

        let requestedStyle = canonicalStyle(style)
        let matchingRecords = downloadedRecords.filter { record in
            if let recordStyle = record.style, styleMatches(recordStyle: recordStyle, requestedStyle: requestedStyle) {
                return true
            }
            guard let parsed = parseFamilyAndStyle(fromFilename: record.url.lastPathComponent) else {
                return false
            }
            return styleMatches(recordStyle: parsed.style, requestedStyle: requestedStyle)
        }

        guard !matchingRecords.isEmpty else {
            throw WebFontFetchError.noMatchingFont
        }
        return downloadedRecords
    }

    private static func googleFontsListURL(for family: String) -> URL {
        var components = URLComponents(string: "https://fonts.google.com/download/list")!
        components.queryItems = [
            URLQueryItem(name: "family", value: family),
        ]
        return components.url!
    }

    private static func decodeGoogleFontsManifest(from data: Data) throws -> GoogleFontsManifest {
        let prefix = Data(")]}'\n".utf8)
        let payload = data.starts(with: prefix)
            ? Data(data.dropFirst(prefix.count))
            : data
        do {
            return try JSONDecoder().decode(GoogleFontsManifest.self, from: payload)
        } catch {
            throw WebFontFetchError.invalidManifest
        }
    }

    private static func downloadGoogleFontFiles(
        from fileRefs: [GoogleFontsManifest.FileRef],
        into fontsDirectory: URL,
        environment: Environment
    ) throws -> [URL] {
        var urls: [URL] = []

        for fileRef in fileRefs {
            guard let filename = cacheFilename(fromGoogleFontsPath: fileRef.filename) else {
                throw WebFontFetchError.invalidManifest
            }
            let ext = URL(fileURLWithPath: filename).pathExtension.lowercased()
            guard ext == "ttf" || ext == "otf" else { continue }

            let destinationURL = fontsDirectory.appendingPathComponent(filename)
            if !environment.fileExists(destinationURL) {
                guard let remoteURL = URL(string: fileRef.url) else {
                    throw WebFontFetchError.invalidDownloadURL(fileRef.url)
                }
                let response = try environment.fetch(remoteURL)
                if let statusCode = response.statusCode, statusCode >= 400 {
                    throw WebFontFetchError.httpStatus(statusCode)
                }
                try environment.writeData(response.data, destinationURL)
            }
            urls.append(destinationURL)
        }

        return urls
    }

    private static func cacheFilename(fromGoogleFontsPath path: String) -> String? {
        let components = path.split(separator: "/", omittingEmptySubsequences: true)
        guard let last = components.last else { return nil }
        let filename = String(last)
        return filename.isEmpty ? nil : filename
    }

    private static func warningMessage(for error: Error, family: String, style: String) -> String {
        let warning: FontResolutionWarning
        if let fetchError = error as? WebFontFetchError {
            switch fetchError {
            case .httpStatus(let statusCode) where statusCode == 400 || statusCode == 404:
                warning = .init(
                    family: family,
                    style: style,
                    kind: .missingFromGoogleFonts
                )
            case .noMatchingFont:
                warning = .init(
                    family: family,
                    style: style,
                    kind: .missingFromGoogleFonts
                )
            default:
                warning = .init(
                    family: family,
                    style: style,
                    kind: .downloadFailed(detail: fetchError.description)
                )
            }
        } else {
            warning = .init(
                family: family,
                style: style,
                kind: .downloadFailed(detail: error.localizedDescription)
            )
        }
        return warning.message
    }

    private static func orderedUnique(_ values: [String]) -> [String] {
        var seen: Set<String> = []
        var result: [String] = []
        for value in values where seen.insert(value).inserted {
            result.append(value)
        }
        return result
    }

    private static func fontMetadata(for url: URL) -> (family: String?, style: String?, postscript: String?) {
        guard let descriptors = CTFontManagerCreateFontDescriptorsFromURL(url as CFURL) as? [CTFontDescriptor],
              let descriptor = descriptors.first else {
            return (nil, nil, nil)
        }
        let family = CTFontDescriptorCopyAttribute(descriptor, kCTFontFamilyNameAttribute) as? String
        let style = CTFontDescriptorCopyAttribute(descriptor, kCTFontStyleNameAttribute) as? String
        let postscript = CTFontDescriptorCopyAttribute(descriptor, kCTFontNameAttribute) as? String
        return (family, style, postscript)
    }

    private static func matchRecord(for request: FontRequest, in records: [CachedFontRecord]) -> CachedFontRecord? {
        if let postscript = request.postscript {
            if let exactPostscript = records.first(where: { normalized($0.postscript) == normalized(postscript) }) {
                return exactPostscript
            }
        }

        if let family = request.family {
            let normalizedFamily = normalized(family)
            if let style = request.style {
                let normalizedStyle = canonicalStyle(style)
                if let exactFamilyStyle = records.first(where: { record in
                    normalized(record.family) == normalizedFamily &&
                        styleMatches(recordStyle: record.style, requestedStyle: normalizedStyle)
                }) {
                    return exactFamilyStyle
                }
            }
        }

        return nil
    }

    private static func naming(for request: FontRequest, record: CachedFontRecord) -> (family: String, style: String) {
        let parsedFromFilename = parseFamilyAndStyle(fromFilename: record.url.lastPathComponent)
        let family = request.family ??
            record.family ??
            parsedFromFilename?.family ??
            "Unknown"
        let style = request.style ??
            record.style ??
            parsedFromFilename?.style ??
            "Regular"
        return (family, style)
    }

    private static func fontReferenceJSON(_ font: SelectedFont) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("fontReference")),
            ("do_objectID", .string(font.objectID)),
            ("fontData", .object(SketchJSONObject([
                ("_class", .string("MSJSONFileReference")),
                ("_ref_class", .string("MSFontData")),
                ("_ref", .string("fonts/\(font.hash)")),
            ]))),
            ("fontFamilyName", .string(font.family)),
            ("fontFileName", .string("\(font.family)-\(font.style).ttf")),
            ("postscriptNames", .array([.string(font.postscript)])),
        ]))
    }

    private static func parseFamilyAndStyle(fromFontName fontName: String) -> (family: String, style: String)? {
        let components = fontName.split(separator: "-", maxSplits: 1, omittingEmptySubsequences: false)
        guard components.count == 2 else { return nil }
        let family = components[0].trimmingCharacters(in: .whitespacesAndNewlines)
        let style = components[1].trimmingCharacters(in: .whitespacesAndNewlines)
        guard !family.isEmpty else { return nil }
        return (family, style.isEmpty ? "Regular" : style)
    }

    private static func parseFamilyAndStyle(fromFilename filename: String) -> (family: String, style: String)? {
        let basename = URL(fileURLWithPath: filename).deletingPathExtension().lastPathComponent
        if basename.contains("VariableFont") {
            let family = basename.split(separator: "-", maxSplits: 1, omittingEmptySubsequences: false).first.map(String.init) ?? basename
            let style = basename.lowercased().contains("italic") ? "Italic" : "Regular"
            return (family, style)
        }

        if let dash = basename.firstIndex(of: "-") {
            let rawFamily = String(basename[..<dash])
            let style = String(basename[basename.index(after: dash)...]).trimmingCharacters(in: .whitespacesAndNewlines)
            let family = rawFamily
                .split(separator: "_", maxSplits: 1, omittingEmptySubsequences: true)
                .first
                .map(String.init) ?? rawFamily
            return (family, style.isEmpty ? "Regular" : style)
        }

        return nil
    }

    private static func styleMatches(recordStyle: String?, requestedStyle: String) -> Bool {
        let normalizedRecordStyle = canonicalStyle(recordStyle)
        guard !normalizedRecordStyle.isEmpty else { return false }
        return normalizedRecordStyle == requestedStyle ||
            normalizedRecordStyle.contains(requestedStyle) ||
            requestedStyle.contains(normalizedRecordStyle)
    }

    private static func canonicalStyle(_ style: String?) -> String {
        let normalizedStyle = normalized(style)
        switch normalizedStyle {
        case "normal":
            return "regular"
        default:
            return normalizedStyle
        }
    }

    private static func isSupportedFontURL(_ url: URL) -> Bool {
        let ext = url.pathExtension.lowercased()
        return ext == "ttf" || ext == "otf"
    }

    private static func normalized(_ value: String?) -> String {
        guard let value else { return "" }
        return value
            .lowercased()
            .replacingOccurrences(of: " ", with: "")
            .replacingOccurrences(of: "-", with: "")
            .replacingOccurrences(of: "_", with: "")
    }

    private static func isEmojiFont(_ fontName: String) -> Bool {
        normalized(fontName) == "applecoloremoji"
    }

    private static func liveFetch(url: URL) throws -> Environment.FetchResponse {
        final class FetchResultBox: @unchecked Sendable {
            var result: Result<Environment.FetchResponse, Error>?
        }

        let semaphore = DispatchSemaphore(value: 0)
        let box = FetchResultBox()

        URLSession.shared.dataTask(with: url) { data, response, error in
            defer { semaphore.signal() }
            if let error {
                box.result = .failure(error)
                return
            }

            box.result = .success(.init(
                data: data ?? Data(),
                statusCode: (response as? HTTPURLResponse)?.statusCode
            ))
        }.resume()

        semaphore.wait()
        guard let result = box.result else {
            struct MissingResponseError: LocalizedError {
                var errorDescription: String? { "request finished without a response" }
            }
            throw MissingResponseError()
        }
        return try result.get()
    }
}

private extension Data {
    init?(hexString: String) {
        guard hexString.count.isMultiple(of: 2) else { return nil }
        var data = Data(capacity: hexString.count / 2)
        var index = hexString.startIndex
        while index < hexString.endIndex {
            let next = hexString.index(index, offsetBy: 2)
            let byteString = hexString[index..<next]
            guard let byte = UInt8(byteString, radix: 16) else { return nil }
            data.append(byte)
            index = next
        }
        self = data
    }
}
