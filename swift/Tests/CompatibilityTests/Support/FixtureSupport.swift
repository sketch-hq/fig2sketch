import FigFormat
import Foundation
import XCTest
import ZIPFoundation
@testable import Fig2SketchCore

enum FixtureSupport {
    static func repositoryRoot(filePath: StaticString = #filePath) throws -> URL {
        var candidate = URL(fileURLWithPath: "\(filePath)")
        candidate.deleteLastPathComponent()

        while candidate.path != "/" {
            let fixturesPath = candidate.appendingPathComponent("tests/data").path
            if FileManager.default.fileExists(atPath: fixturesPath) {
                return candidate
            }
            candidate.deleteLastPathComponent()
        }

        throw NSError(domain: "FixtureSupport", code: 1, userInfo: [
            NSLocalizedDescriptionKey: "Could not locate repository root from \(filePath)",
        ])
    }

    static func fixtureURL(named name: String, filePath: StaticString = #filePath) throws -> URL {
        try repositoryRoot(filePath: filePath).appendingPathComponent("tests/data/\(name)")
    }

    static func guid(_ sessionID: UInt32, _ localID: UInt32) -> KiwiValue {
        .object([
            "sessionID": .uint(sessionID),
            "localID": .uint(localID),
        ])
    }

    static func parentIndex(_ sessionID: UInt32, _ localID: UInt32, position: UInt32 = 0) -> KiwiValue {
        .object([
            "guid": guid(sessionID, localID),
            "position": .uint(position),
        ])
    }

    static func figColor(red: Double, green: Double, blue: Double, alpha: Double) -> KiwiValue {
        .object([
            "r": .float(red),
            "g": .float(green),
            "b": .float(blue),
            "a": .float(alpha),
        ])
    }

    static func matrix(
        m00: Double,
        m01: Double,
        m02: Double,
        m10: Double,
        m11: Double,
        m12: Double
    ) -> KiwiValue {
        .object([
            "m00": .float(m00),
            "m01": .float(m01),
            "m02": .float(m02),
            "m10": .float(m10),
            "m11": .float(m11),
            "m12": .float(m12),
        ])
    }

    static func makeRootMessage(
        nodes: [[String: KiwiValue]],
        canvasType: String = "CANVAS",
        canvasName: String = "Page 1",
        canvasGUID: (UInt32, UInt32) = (0, 1),
        canvasExtra: [String: KiwiValue] = [:]
    ) -> KiwiValue {
        var canvas: [String: KiwiValue] = [
            "guid": guid(canvasGUID.0, canvasGUID.1),
            "parentIndex": parentIndex(0, 0, position: 0),
            "type": .string(canvasType),
            "name": .string(canvasName),
        ]
        for (key, value) in canvasExtra {
            canvas[key] = value
        }

        let changes: [KiwiValue] = [
            .object([
                "guid": guid(0, 0),
                "type": .string("DOCUMENT"),
                "name": .string("Document"),
            ]),
            .object(canvas),
        ] + nodes.map { .object($0) }

        return .object([
            "nodeChanges": .array(changes),
        ])
    }

    static func decodeTree(from rootMessage: KiwiValue) throws -> FigTree {
        try FigTreeDecoder.buildTree(from: rootMessage)
    }

    static func firstCanvasNode(in tree: FigTree) throws -> FigTreeNode {
        try XCTUnwrap(tree.root.children.first, "Expected a canvas node under root document")
    }

    static func firstChildNode(in tree: FigTree) throws -> FigTreeNode {
        let canvas = try firstCanvasNode(in: tree)
        return try XCTUnwrap(canvas.children.first, "Expected at least one node under canvas")
    }

    static func decodeSingleNode(
        _ node: [String: KiwiValue],
        canvasType: String = "CANVAS",
        canvasExtra: [String: KiwiValue] = [:]
    ) throws -> FigNode {
        let tree = try decodeTree(from: makeRootMessage(
            nodes: [node],
            canvasType: canvasType,
            canvasExtra: canvasExtra
        ))
        return try firstChildNode(in: tree).node
    }

    static func decodeSingleNodeStyle(
        _ node: [String: KiwiValue],
        canvasType: String = "CANVAS",
        canvasExtra: [String: KiwiValue] = [:]
    ) throws -> FigLayerStyle {
        let decoded = try decodeSingleNode(node, canvasType: canvasType, canvasExtra: canvasExtra)
        return try XCTUnwrap(decoded.style, "Expected decoded style")
    }

    static func mapDocument(
        from rootMessage: KiwiValue,
        options: FigTreeMappingOptions = .init()
    ) throws -> ConversionDocument {
        try FigTreeToDocumentMapper.makeConversionDocument(from: decodeTree(from: rootMessage), options: options)
    }

    static func mapDocumentFromSingleNode(
        _ node: [String: KiwiValue],
        canvasType: String = "CANVAS",
        canvasExtra: [String: KiwiValue] = [:],
        options: FigTreeMappingOptions = .init()
    ) throws -> ConversionDocument {
        try mapDocument(from: makeRootMessage(
            nodes: [node],
            canvasType: canvasType,
            canvasExtra: canvasExtra
        ), options: options)
    }

    static func pageJSONString(
        from document: ConversionDocument,
        pageIndex: Int = 0,
        salt: String = "compat-tests"
    ) throws -> String {
        let saltData = Data(salt.utf8)
        let bundle = SketchBundleBuilder.build(from: document, salt: saltData)
        let page = try XCTUnwrap(document.pages[safe: pageIndex], "Expected page at index \(pageIndex)")
        let pageID = ConverterUtils.genObjectID(figID: page.guid, salt: saltData, suffix: page.idSuffix)
        let pageData = try XCTUnwrap(bundle["pages/\(pageID).json"], "Expected page entry in bundle")
        return String(decoding: pageData, as: UTF8.self)
    }

    static func parseJSONObject(_ json: String) throws -> [String: Any] {
        let object = try JSONSerialization.jsonObject(with: Data(json.utf8))
        return try XCTUnwrap(object as? [String: Any], "Expected top-level JSON object")
    }

    static func parseJSONObject(data: Data) throws -> [String: Any] {
        let object = try JSONSerialization.jsonObject(with: data)
        return try XCTUnwrap(object as? [String: Any], "Expected top-level JSON object")
    }

    static func extractArchiveEntry(path: String, from archive: Archive) throws -> Data {
        guard let entry = archive[path] else {
            throw NSError(domain: "FixtureSupport", code: 2, userInfo: [
                NSLocalizedDescriptionKey: "Missing archive entry: \(path)",
            ])
        }

        var data = Data()
        _ = try archive.extract(entry) { chunk in
            data.append(chunk)
        }
        return data
    }
}

struct TestCLIOutputBuffer: CLIOutput {
    var stdout = ""
    var stderr = ""

    mutating func writeOut(_ message: String) {
        stdout.append(message)
    }

    mutating func writeErr(_ message: String) {
        stderr.append(message)
    }
}

private extension Collection {
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
