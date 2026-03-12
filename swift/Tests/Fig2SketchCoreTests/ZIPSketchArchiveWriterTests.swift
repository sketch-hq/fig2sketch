import Foundation
import XCTest
import ZIPFoundation
@testable import Fig2SketchCore

final class ZIPSketchArchiveWriterTests: XCTestCase {
    func testWritesSketchBundleAsZipArchive() throws {
        let document = ConversionDocument(
            pages: [
                ConversionPage(
                    guid: [1, 2],
                    name: "Page 1",
                    layers: [
                        .rectangle(.init(guid: [3, 4], name: "Rectangle", x: 0, y: 0, width: 10, height: 20))
                    ]
                )
            ]
        )
        let bundle = SketchBundleBuilder.build(from: document, salt: Data("1234".utf8))

        let outputURL = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathExtension("sketch")
        defer { try? FileManager.default.removeItem(at: outputURL) }

        try ZIPSketchArchiveWriter().write(bundle: bundle, to: outputURL, compression: .stored)

        XCTAssertTrue(FileManager.default.fileExists(atPath: outputURL.path))

        let archive = try Archive(url: outputURL, accessMode: .read)

        let paths = Set(archive.map(\.path))
        XCTAssertTrue(paths.contains("document.json"))
        XCTAssertTrue(paths.contains("meta.json"))
        XCTAssertTrue(paths.contains("user.json"))
        XCTAssertEqual(paths.filter { $0.hasPrefix("pages/") && $0.hasSuffix(".json") }.count, 1)
    }
}
