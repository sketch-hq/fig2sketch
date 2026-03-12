import Foundation
import XCTest
import ZIPFoundation
@testable import Fig2SketchCore

enum SemanticOracleSupport {
    private static let salt = "1234"

    static func assertFixtureMatchesPython(
        named fixtureName: String,
        filePath: StaticString = #filePath
    ) throws {
        let repoRoot = try FixtureSupport.repositoryRoot(filePath: filePath)
        let fixtureURL = try FixtureSupport.fixtureURL(named: fixtureName, filePath: filePath)
        let pythonOracle = try pythonOracle(in: repoRoot)

        let tempRoot = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempRoot, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempRoot) }

        let pythonOutputURL = tempRoot.appendingPathComponent("python.sketch")
        let swiftOutputURL = tempRoot.appendingPathComponent("swift.sketch")

        try pythonOracle.convert(figURL: fixtureURL, outputURL: pythonOutputURL)
        try runSwiftOracle(figURL: fixtureURL, outputURL: swiftOutputURL)

        let pythonArchive = try archiveEntries(from: pythonOutputURL)
        let swiftArchive = try archiveEntries(from: swiftOutputURL)
        try compareEntryPathSet(
            expected: Set(pythonArchive.keys.filter { !shouldIgnoreEntryPath($0) }),
            actual: Set(swiftArchive.keys.filter { !shouldIgnoreEntryPath($0) }),
            fixtureName: fixtureName
        )

        for path in pythonArchive.keys.sorted() {
            if shouldIgnoreEntryPath(path) {
                continue
            }

            let pythonData = try XCTUnwrap(pythonArchive[path], "Missing Python archive entry \(path)")
            let swiftData = try XCTUnwrap(swiftArchive[path], "Missing Swift archive entry \(path)")

            if isBinaryAsset(path: path) {
                guard pythonData == swiftData else {
                    throw OracleFailure(
                        fixtureName: fixtureName,
                        entryPath: path,
                        jsonPath: "$",
                        message: "binary asset contents differ"
                    )
                }
                continue
            }

            guard path.hasSuffix(".json") else { continue }
            let expected = try normalizedJSONEntry(path: path, data: pythonData)
            let actual = try normalizedJSONEntry(path: path, data: swiftData)
            try compare(expected, actual, fixtureName: fixtureName, entryPath: path, jsonPath: "$")
        }
    }

    private struct PythonOracle {
        var executableURL: URL
        var argumentsPrefix: [String]
        var workingDirectoryURL: URL

        func convert(figURL: URL, outputURL: URL) throws {
            let arguments = argumentsPrefix + [figURL.path, outputURL.path, "--salt", SemanticOracleSupport.salt]
            let result = try runProcess(
                executableURL: executableURL,
                arguments: arguments,
                currentDirectoryURL: workingDirectoryURL
            )
            guard result.status == 0 else {
                throw OracleFailure(
                    fixtureName: figURL.lastPathComponent,
                    entryPath: "<python>",
                    jsonPath: "$",
                    message: "python oracle failed with exit code \(result.status): \(result.stderr)"
                )
            }
        }
    }

    private struct ProcessResult {
        var status: Int32
        var stdout: String
        var stderr: String
    }

    private struct OracleFailure: LocalizedError {
        var fixtureName: String
        var entryPath: String
        var jsonPath: String
        var message: String

        var errorDescription: String? {
            "\(fixtureName) \(entryPath) \(jsonPath): \(message)"
        }
    }

    private static func pythonOracle(in repoRoot: URL) throws -> PythonOracle {
        let fileManager = FileManager.default
        let directCLI = repoRoot.appendingPathComponent(".venv/bin/fig2sketch")
        if fileManager.isExecutableFile(atPath: directCLI.path) {
            return PythonOracle(executableURL: directCLI, argumentsPrefix: [], workingDirectoryURL: repoRoot)
        }

        let python = repoRoot.appendingPathComponent(".venv/bin/python")
        let script = repoRoot.appendingPathComponent("src/fig2sketch.py")
        if fileManager.isExecutableFile(atPath: python.path),
           fileManager.fileExists(atPath: script.path) {
            return PythonOracle(
                executableURL: python,
                argumentsPrefix: [script.path],
                workingDirectoryURL: repoRoot
            )
        }

        throw XCTSkip("Python oracle unavailable: expected either \(directCLI.path) or \(python.path) + \(script.path)")
    }

    private static func runSwiftOracle(figURL: URL, outputURL: URL) throws {
        var output = TestCLIOutputBuffer()
        let exitCode = CLIConversionRunner.run(
            options: CLIOptions(
                figFile: figURL.path,
                sketchFile: outputURL.path,
                salt: salt
            ),
            output: &output
        )

        guard exitCode == 0 else {
            throw OracleFailure(
                fixtureName: figURL.lastPathComponent,
                entryPath: "<swift>",
                jsonPath: "$",
                message: "swift conversion failed with exit code \(exitCode): \(output.stderr)"
            )
        }
    }

    private static func runProcess(
        executableURL: URL,
        arguments: [String],
        currentDirectoryURL: URL
    ) throws -> ProcessResult {
        let process = Process()
        process.executableURL = executableURL
        process.arguments = arguments
        process.currentDirectoryURL = currentDirectoryURL

        let stdoutPipe = Pipe()
        let stderrPipe = Pipe()
        process.standardOutput = stdoutPipe
        process.standardError = stderrPipe

        try process.run()
        process.waitUntilExit()

        let stdout = String(decoding: stdoutPipe.fileHandleForReading.readDataToEndOfFile(), as: UTF8.self)
        let stderr = String(decoding: stderrPipe.fileHandleForReading.readDataToEndOfFile(), as: UTF8.self)
        return ProcessResult(status: process.terminationStatus, stdout: stdout, stderr: stderr)
    }

    private static func archiveEntries(from outputURL: URL) throws -> [String: Data] {
        let archive = try Archive(url: outputURL, accessMode: .read)
        var entries: [String: Data] = [:]
        for entry in archive {
            entries[entry.path] = try FixtureSupport.extractArchiveEntry(path: entry.path, from: archive)
        }
        return entries
    }

    private static func compareEntryPathSet(
        expected: Set<String>,
        actual: Set<String>,
        fixtureName: String
    ) throws {
        guard expected == actual else {
            let missing = expected.subtracting(actual).sorted()
            let extra = actual.subtracting(expected).sorted()
            let message = [
                missing.isEmpty ? nil : "missing: \(missing.joined(separator: ", "))",
                extra.isEmpty ? nil : "extra: \(extra.joined(separator: ", "))",
            ]
            .compactMap { $0 }
            .joined(separator: "; ")

            throw OracleFailure(
                fixtureName: fixtureName,
                entryPath: "<archive>",
                jsonPath: "$",
                message: message
            )
        }
    }

    private static func isBinaryAsset(path: String) -> Bool {
        path.hasPrefix("images/") || path.hasPrefix("previews/")
    }

    private static func shouldIgnoreEntryPath(_ path: String) -> Bool {
        path == "user.json" || path.hasPrefix("fonts/")
    }

    private static func normalizedJSONEntry(path: String, data: Data) throws -> OracleValue {
        let json = try JSONSerialization.jsonObject(with: data)
        let object = try XCTUnwrap(json as? [String: Any], "Expected JSON object at \(path)")

        switch path {
        case "document.json":
            return normalizeDocument(object)
        case "meta.json":
            return normalizeMeta(object)
        case let pagePath where pagePath.hasPrefix("pages/"):
            return normalizePage(object)
        case "user.json":
            return .object([:])
        default:
            return normalizeValue(object)
        }
    }

    private static func normalizeDocument(_ object: [String: Any]) -> OracleValue {
        let pages = (object["pages"] as? [[String: Any]] ?? []).map { normalizeFileReference($0) }
        return .object([
            "pages": .array(pages),
        ])
    }

    private static func normalizeMeta(_ object: [String: Any]) -> OracleValue {
        let pages = object["pagesAndArtboards"] as? [String: Any] ?? [:]
        var normalizedPages: [String: OracleValue] = [:]

        for pageID in pages.keys.sorted() {
            let page = pages[pageID] as? [String: Any] ?? [:]
            let artboards = page["artboards"] as? [String: Any] ?? [:]
            var normalizedArtboards: [String: OracleValue] = [:]
            for artboardID in artboards.keys.sorted() {
                let artboard = artboards[artboardID] as? [String: Any] ?? [:]
                normalizedArtboards[artboardID] = .object([
                    "name": normalizeValue(artboard["name"] as Any),
                ])
            }

            normalizedPages[pageID] = .object([
                "name": normalizeValue(page["name"] as Any),
                "artboards": .object(normalizedArtboards),
            ])
        }

        return .object(normalizedPages)
    }

    private static func normalizePage(_ object: [String: Any]) -> OracleValue {
        let layers = (object["layers"] as? [[String: Any]] ?? []).map { normalizeLayer($0) }
        return .object([
            "name": normalizeValue(object["name"] as Any),
            "layers": .array(layers),
        ])
    }

    private static func normalizeLayer(_ object: [String: Any]) -> OracleValue {
        let layerClass = object["_class"] as? String ?? ""
        let layers = (object["layers"] as? [[String: Any]] ?? []).map { normalizeLayer($0) }
        let overrides = (object["overrideValues"] as? [[String: Any]] ?? []).map { normalizeValue($0) }
        let points = (object["points"] as? [Any] ?? []).map { normalizeValue($0) }
        let isContainerLayer = layerClass == "group" || layerClass == "symbolMaster" || layerClass == "symbolInstance" || layerClass == "artboard"
        let isShapePath = layerClass == "shapePath"

        var snapshot: [String: OracleValue] = [:]
        add(snapshot: &snapshot, key: "_class", value: object["_class"])
        add(snapshot: &snapshot, key: "name", value: object["name"])
        add(snapshot: &snapshot, key: "frame", value: normalizeFrame(object["frame"] as? [String: Any]))
        add(snapshot: &snapshot, key: "rotation", value: normalizeNonDefaultNumber(object["rotation"], defaultValue: 0))
        add(snapshot: &snapshot, key: "clippingBehavior", value: object["clippingBehavior"])
        add(snapshot: &snapshot, key: "hasClippingMask", value: normalizeTrueBool(object["hasClippingMask"]))
        add(snapshot: &snapshot, key: "clippingMaskMode", value: normalizeMaskMode(object))
        add(snapshot: &snapshot, key: "shouldBreakMaskChain", value: normalizeTrueBool(object["shouldBreakMaskChain"]))
        if isContainerLayer {
            add(snapshot: &snapshot, key: "horizontalSizing", value: object["horizontalSizing"])
            add(snapshot: &snapshot, key: "verticalSizing", value: object["verticalSizing"])
        }
        add(snapshot: &snapshot, key: "paddingSelection", value: object["paddingSelection"])
        add(snapshot: &snapshot, key: "topPadding", value: normalizeNonDefaultNumber(object["topPadding"], defaultValue: 0))
        add(snapshot: &snapshot, key: "rightPadding", value: normalizeNonDefaultNumber(object["rightPadding"], defaultValue: 0))
        add(snapshot: &snapshot, key: "bottomPadding", value: normalizeNonDefaultNumber(object["bottomPadding"], defaultValue: 0))
        add(snapshot: &snapshot, key: "leftPadding", value: normalizeNonDefaultNumber(object["leftPadding"], defaultValue: 0))
        add(snapshot: &snapshot, key: "groupLayout", value: normalizeGroupLayout(object["groupLayout"] as? [String: Any]))
        add(snapshot: &snapshot, key: "grid", value: normalizeLayoutGrid(object["grid"] as? [String: Any]))
        add(snapshot: &snapshot, key: "layout", value: normalizeValueIfPresent(object["layout"]))
        add(snapshot: &snapshot, key: "windingRule", value: object["windingRule"])
        add(snapshot: &snapshot, key: "symbolID", value: object["symbolID"])
        if !overrides.isEmpty {
            snapshot["overrideValues"] = .array(overrides)
        }
        add(snapshot: &snapshot, key: "isFlowHome", value: object["isFlowHome"])
        add(snapshot: &snapshot, key: "overlayBackgroundInteraction", value: object["overlayBackgroundInteraction"])
        add(snapshot: &snapshot, key: "presentationStyle", value: object["presentationStyle"])
        add(snapshot: &snapshot, key: "flow", value: normalizeValueIfPresent(object["flow"]))
        add(snapshot: &snapshot, key: "attributedString", value: normalizeValueIfPresent(object["attributedString"]))
        add(snapshot: &snapshot, key: "resizesContent", value: normalizeFalseBool(object["resizesContent"]))
        if isShapePath {
            add(snapshot: &snapshot, key: "isClosed", value: object["isClosed"])
            add(snapshot: &snapshot, key: "edited", value: object["edited"])
            add(snapshot: &snapshot, key: "pointRadiusBehaviour", value: object["pointRadiusBehaviour"])
        }
        if isShapePath && !points.isEmpty {
            snapshot["points"] = .array(points)
        }
        if let style = normalizeStyle(object["style"] as? [String: Any]) {
            snapshot["style"] = style
        }
        if !layers.isEmpty {
            snapshot["layers"] = .array(layers)
        }

        return .object(snapshot)
    }

    private static func normalizeStyle(_ object: [String: Any]?) -> OracleValue? {
        guard let object else { return nil }
        var snapshot: [String: OracleValue] = [:]

        let fills = (object["fills"] as? [[String: Any]] ?? []).compactMap(normalizeFill)
        let borders = (object["borders"] as? [[String: Any]] ?? []).compactMap(normalizeBorder)
        let blurs = (object["blurs"] as? [[String: Any]] ?? []).compactMap(normalizeEffect)
        let shadows = (object["shadows"] as? [[String: Any]] ?? []).compactMap(normalizeEffect)

        if !fills.isEmpty {
            snapshot["fills"] = .array(fills)
        }
        if !borders.isEmpty {
            snapshot["borders"] = .array(borders)
        }
        if let borderOptions = normalizeBorderOptions(object["borderOptions"] as? [String: Any]) {
            snapshot["borderOptions"] = borderOptions
        }
        if let contextSettings = normalizeContextSettings(object["contextSettings"] as? [String: Any]) {
            snapshot["contextSettings"] = contextSettings
        }
        if let miterLimit = normalizeNonDefaultNumber(object["miterLimit"], defaultValue: 10) {
            snapshot["miterLimit"] = miterLimit
        }
        if !blurs.isEmpty {
            snapshot["blurs"] = .array(blurs)
        }
        if !shadows.isEmpty {
            snapshot["shadows"] = .array(shadows)
        }
        add(snapshot: &snapshot, key: "startMarkerType", value: normalizeNonDefaultNumber(object["startMarkerType"], defaultValue: 0))
        add(snapshot: &snapshot, key: "endMarkerType", value: normalizeNonDefaultNumber(object["endMarkerType"], defaultValue: 0))
        add(snapshot: &snapshot, key: "corners", value: normalizeValueIfPresent(object["corners"]))

        return snapshot.isEmpty ? nil : .object(snapshot)
    }

    private static func normalizeFill(_ object: [String: Any]) -> OracleValue? {
        var snapshot: [String: OracleValue] = [:]
        let fillType = numberValue(object["fillType"])
        add(snapshot: &snapshot, key: "fillType", value: object["fillType"])
        add(snapshot: &snapshot, key: "isEnabled", value: object["isEnabled"])
        if fillType == 0 {
            add(snapshot: &snapshot, key: "color", value: normalizeValueIfPresent(object["color"]))
        }
        if fillType == 1 {
            add(snapshot: &snapshot, key: "gradient", value: normalizeValueIfPresent(object["gradient"]))
        }
        if fillType == 4 {
            add(snapshot: &snapshot, key: "patternFillType", value: object["patternFillType"])
            add(snapshot: &snapshot, key: "patternTileScale", value: object["patternTileScale"])
        }
        if fillType == 4, let image = object["image"] as? [String: Any] {
            add(snapshot: &snapshot, key: "imageRef", value: image["_ref"])
        }
        if let contextSettings = normalizeContextSettings(object["contextSettings"] as? [String: Any]) {
            snapshot["contextSettings"] = contextSettings
        }
        return snapshot.isEmpty ? nil : .object(snapshot)
    }

    private static func normalizeBorder(_ object: [String: Any]) -> OracleValue? {
        var snapshot: [String: OracleValue] = [:]
        let fillType = numberValue(object["fillType"])
        add(snapshot: &snapshot, key: "fillType", value: object["fillType"])
        add(snapshot: &snapshot, key: "isEnabled", value: object["isEnabled"])
        add(snapshot: &snapshot, key: "position", value: object["position"])
        add(snapshot: &snapshot, key: "thickness", value: object["thickness"])
        if fillType == 0 {
            add(snapshot: &snapshot, key: "color", value: normalizeValueIfPresent(object["color"]))
        }
        if fillType == 1 {
            add(snapshot: &snapshot, key: "gradient", value: normalizeValueIfPresent(object["gradient"]))
        }
        if fillType == 4 {
            add(snapshot: &snapshot, key: "patternFillType", value: object["patternFillType"])
            add(snapshot: &snapshot, key: "patternTileScale", value: object["patternTileScale"])
        }
        if fillType == 4, let image = object["image"] as? [String: Any] {
            add(snapshot: &snapshot, key: "imageRef", value: image["_ref"])
        }
        if let contextSettings = normalizeContextSettings(object["contextSettings"] as? [String: Any]) {
            snapshot["contextSettings"] = contextSettings
        }
        return snapshot.isEmpty ? nil : .object(snapshot)
    }

    private static func normalizeEffect(_ object: [String: Any]) -> OracleValue? {
        var snapshot: [String: OracleValue] = [:]
        add(snapshot: &snapshot, key: "type", value: object["type"])
        add(snapshot: &snapshot, key: "isEnabled", value: object["isEnabled"])
        add(snapshot: &snapshot, key: "radius", value: object["radius"])
        add(snapshot: &snapshot, key: "blurRadius", value: object["blurRadius"])
        add(snapshot: &snapshot, key: "offsetX", value: object["offsetX"])
        add(snapshot: &snapshot, key: "offsetY", value: object["offsetY"])
        add(snapshot: &snapshot, key: "spread", value: object["spread"])
        add(snapshot: &snapshot, key: "isInnerShadow", value: object["isInnerShadow"])
        add(snapshot: &snapshot, key: "color", value: normalizeValueIfPresent(object["color"]))
        add(snapshot: &snapshot, key: "gradient", value: normalizeValueIfPresent(object["gradient"]))
        return snapshot.isEmpty ? nil : .object(snapshot)
    }

    private static func normalizeBorderOptions(_ object: [String: Any]?) -> OracleValue? {
        guard let object else { return nil }
        let lineCapStyle = numberValue(object["lineCapStyle"]) ?? 0
        let lineJoinStyle = numberValue(object["lineJoinStyle"]) ?? 0
        let dashPattern = (object["dashPattern"] as? [Any] ?? []).map { normalizeValue($0) }
        if lineCapStyle == 0, lineJoinStyle == 0, dashPattern.isEmpty {
            return nil
        }

        var snapshot: [String: OracleValue] = [:]
        add(snapshot: &snapshot, key: "lineCapStyle", value: object["lineCapStyle"])
        add(snapshot: &snapshot, key: "lineJoinStyle", value: object["lineJoinStyle"])
        if !dashPattern.isEmpty {
            snapshot["dashPattern"] = .array(dashPattern)
        }
        return snapshot.isEmpty ? nil : .object(snapshot)
    }

    private static func normalizeContextSettings(_ object: [String: Any]?) -> OracleValue? {
        guard let object else { return nil }
        let blendMode = numberValue(object["blendMode"])
        let opacity = numberValue(object["opacity"])
        if blendMode == 0, opacity == 1 {
            return nil
        }
        return .object([
            "blendMode": normalizeValue(object["blendMode"] as Any),
            "opacity": normalizeValue(object["opacity"] as Any),
        ])
    }

    private static func normalizeFrame(_ object: [String: Any]?) -> OracleValue? {
        guard let object else { return nil }
        var snapshot: [String: OracleValue] = [:]
        add(snapshot: &snapshot, key: "x", value: object["x"])
        add(snapshot: &snapshot, key: "y", value: object["y"])
        add(snapshot: &snapshot, key: "width", value: object["width"])
        add(snapshot: &snapshot, key: "height", value: object["height"])
        add(snapshot: &snapshot, key: "constrainProportions", value: object["constrainProportions"])
        return snapshot.isEmpty ? nil : .object(snapshot)
    }

    private static func normalizeGroupLayout(_ object: [String: Any]?) -> OracleValue? {
        guard let object else { return nil }
        var snapshot: [String: OracleValue] = [:]
        add(snapshot: &snapshot, key: "_class", value: object["_class"])
        add(snapshot: &snapshot, key: "axis", value: object["axis"])
        add(snapshot: &snapshot, key: "layoutAnchor", value: object["layoutAnchor"])
        add(snapshot: &snapshot, key: "justifyContent", value: object["justifyContent"])
        add(snapshot: &snapshot, key: "alignItems", value: object["alignItems"])
        add(snapshot: &snapshot, key: "allGuttersGap", value: normalizeNonDefaultNumber(object["allGuttersGap"], defaultValue: 0))
        return snapshot.isEmpty ? nil : .object(snapshot)
    }

    private static func normalizeLayoutGrid(_ object: [String: Any]?) -> OracleValue? {
        guard let object else { return nil }
        var snapshot: [String: OracleValue] = [:]
        add(snapshot: &snapshot, key: "_class", value: object["_class"])
        add(snapshot: &snapshot, key: "gridSize", value: normalizeNonDefaultNumber(object["gridSize"], defaultValue: 8))
        add(snapshot: &snapshot, key: "thickGridTimes", value: normalizeNonDefaultNumber(object["thickGridTimes"], defaultValue: 1))
        add(snapshot: &snapshot, key: "isEnabled", value: object["isEnabled"])
        add(snapshot: &snapshot, key: "drawHorizontal", value: object["drawHorizontal"])
        add(snapshot: &snapshot, key: "drawVertical", value: object["drawVertical"])
        add(snapshot: &snapshot, key: "gutterWidth", value: normalizeNonDefaultNumber(object["gutterWidth"], defaultValue: 0))
        add(snapshot: &snapshot, key: "gutterHeight", value: normalizeNonDefaultNumber(object["gutterHeight"], defaultValue: 0))
        add(snapshot: &snapshot, key: "columnWidth", value: normalizeNonDefaultNumber(object["columnWidth"], defaultValue: 0))
        add(snapshot: &snapshot, key: "numberOfColumns", value: normalizeNonDefaultNumber(object["numberOfColumns"], defaultValue: 0))
        add(snapshot: &snapshot, key: "horizontalOffset", value: normalizeNonDefaultNumber(object["horizontalOffset"], defaultValue: 0))
        add(snapshot: &snapshot, key: "rowHeightMultiplication", value: normalizeNonDefaultNumber(object["rowHeightMultiplication"], defaultValue: 0))
        add(snapshot: &snapshot, key: "totalWidth", value: normalizeNonDefaultNumber(object["totalWidth"], defaultValue: 0))
        return snapshot.isEmpty ? nil : .object(snapshot)
    }

    private static func normalizeFileReference(_ object: [String: Any]) -> OracleValue {
        .object([
            "_ref": normalizeValue(object["_ref"] as Any),
            "_ref_class": normalizeValue(object["_ref_class"] as Any),
        ])
    }

    private static func add(snapshot: inout [String: OracleValue], key: String, value: Any?) {
        if let normalized = normalizeValueIfPresent(value) {
            snapshot[key] = normalized
        }
    }

    private static func normalizeValueIfPresent(_ value: Any?) -> OracleValue? {
        guard let value else { return nil }
        return normalizeValue(value)
    }

    private static func normalizeNonDefaultNumber(_ value: Any?, defaultValue: Double) -> OracleValue? {
        guard let numeric = numberValue(value) else { return nil }
        return abs(numeric - defaultValue) <= 0.000_000_1 ? nil : .number(numeric)
    }

    private static func normalizeTrueBool(_ value: Any?) -> OracleValue? {
        guard let value else { return nil }
        let normalized = normalizeValue(value)
        if case .bool(true) = normalized {
            return normalized
        }
        return nil
    }

    private static func normalizeFalseBool(_ value: Any?) -> OracleValue? {
        guard let value else { return nil }
        let normalized = normalizeValue(value)
        if case .bool(false) = normalized {
            return normalized
        }
        return nil
    }

    private static func normalizeMaskMode(_ object: [String: Any]) -> OracleValue? {
        guard let hasMask = normalizeTrueBool(object["hasClippingMask"]) else { return nil }
        _ = hasMask
        return normalizeValueIfPresent(object["clippingMaskMode"])
    }

    private static func normalizeValue(_ value: Any) -> OracleValue {
        if let string = value as? String {
            if let point = parsePoint(string) {
                return .point(point.x, point.y)
            }
            return .string(string)
        }

        if let number = value as? NSNumber {
            if CFGetTypeID(number) == CFBooleanGetTypeID() {
                return .bool(number.boolValue)
            }
            return .number(number.doubleValue)
        }

        if let array = value as? [Any] {
            return .array(array.map(normalizeValue))
        }

        if let object = value as? [String: Any] {
            var normalized: [String: OracleValue] = [:]
            for key in object.keys.sorted() {
                normalized[key] = normalizeValue(object[key] as Any)
            }
            return .object(normalized)
        }

        return .null
    }

    private static func numberValue(_ value: Any?) -> Double? {
        guard let value else { return nil }
        if let number = value as? NSNumber, CFGetTypeID(number) != CFBooleanGetTypeID() {
            return number.doubleValue
        }
        return nil
    }

    private static func parsePoint(_ string: String) -> (x: Double, y: Double)? {
        guard string.first == "{", string.last == "}" else { return nil }
        let body = string.dropFirst().dropLast()
        let parts = body.split(separator: ",", omittingEmptySubsequences: false).map {
            $0.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        guard parts.count == 2,
              let x = Double(parts[0]),
              let y = Double(parts[1]) else {
            return nil
        }
        return (x, y)
    }

    private static func compare(
        _ expected: OracleValue,
        _ actual: OracleValue,
        fixtureName: String,
        entryPath: String,
        jsonPath: String
    ) throws {
        switch (expected, actual) {
        case (.null, .null):
            return
        case (.bool(let lhs), .bool(let rhs)):
            guard lhs == rhs else {
                throw OracleFailure(fixtureName: fixtureName, entryPath: entryPath, jsonPath: jsonPath, message: "expected \(lhs), got \(rhs)")
            }
        case (.string(let lhs), .string(let rhs)):
            guard lhs == rhs else {
                throw OracleFailure(fixtureName: fixtureName, entryPath: entryPath, jsonPath: jsonPath, message: "expected \(lhs), got \(rhs)")
            }
        case (.number(let lhs), .number(let rhs)):
            guard abs(lhs - rhs) <= 0.000_000_1 else {
                throw OracleFailure(fixtureName: fixtureName, entryPath: entryPath, jsonPath: jsonPath, message: "expected \(lhs), got \(rhs)")
            }
        case (.point(let lhsX, let lhsY), .point(let rhsX, let rhsY)):
            guard abs(lhsX - rhsX) <= 0.000_000_1, abs(lhsY - rhsY) <= 0.000_000_1 else {
                throw OracleFailure(
                    fixtureName: fixtureName,
                    entryPath: entryPath,
                    jsonPath: jsonPath,
                    message: "expected {\(lhsX), \(lhsY)}, got {\(rhsX), \(rhsY)}"
                )
            }
        case (.array(let lhs), .array(let rhs)):
            guard lhs.count == rhs.count else {
                throw OracleFailure(
                    fixtureName: fixtureName,
                    entryPath: entryPath,
                    jsonPath: jsonPath,
                    message: "expected array count \(lhs.count), got \(rhs.count)"
                )
            }
            for index in lhs.indices {
                try compare(lhs[index], rhs[index], fixtureName: fixtureName, entryPath: entryPath, jsonPath: "\(jsonPath)[\(index)]")
            }
        case (.object(let lhs), .object(let rhs)):
            let lhsKeys = Set(lhs.keys)
            let rhsKeys = Set(rhs.keys)
            guard lhsKeys == rhsKeys else {
                let missing = lhsKeys.subtracting(rhsKeys).sorted()
                let extra = rhsKeys.subtracting(lhsKeys).sorted()
                let message = [
                    missing.isEmpty ? nil : "missing keys: \(missing.joined(separator: ", "))",
                    extra.isEmpty ? nil : "extra keys: \(extra.joined(separator: ", "))",
                ]
                .compactMap { $0 }
                .joined(separator: "; ")

                throw OracleFailure(
                    fixtureName: fixtureName,
                    entryPath: entryPath,
                    jsonPath: jsonPath,
                    message: message
                )
            }

            for key in lhs.keys.sorted() {
                try compare(
                    lhs[key]!,
                    rhs[key]!,
                    fixtureName: fixtureName,
                    entryPath: entryPath,
                    jsonPath: "\(jsonPath).\(key)"
                )
            }
        default:
            throw OracleFailure(
                fixtureName: fixtureName,
                entryPath: entryPath,
                jsonPath: jsonPath,
                message: "type mismatch: expected \(expected.kindDescription), got \(actual.kindDescription)"
            )
        }
    }
}

private indirect enum OracleValue: Equatable {
    case null
    case bool(Bool)
    case number(Double)
    case string(String)
    case point(Double, Double)
    case array([OracleValue])
    case object([String: OracleValue])

    var kindDescription: String {
        switch self {
        case .null:
            return "null"
        case .bool:
            return "bool"
        case .number:
            return "number"
        case .string:
            return "string"
        case .point:
            return "point"
        case .array:
            return "array"
        case .object:
            return "object"
        }
    }
}
