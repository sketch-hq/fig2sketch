import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_userTests: XCTestCase {
    func test__converter__test_user__TestDefaultViewport__test_small_oval() throws {
        // Port of tests/converter/test_user.py::TestDefaultViewport.test_small_oval
        let user = try makeUserJSON(for: [
            .rectangle(.init(
                guid: [0, 2],
                name: "oval",
                x: 0,
                y: 0,
                width: 10,
                height: 10
            )),
        ])

        let pageID = try XCTUnwrap(user.keys.first(where: { $0 != "document" }))
        let view = try XCTUnwrap(user[pageID] as? [String: Any], "Expected per-page viewport settings")
        XCTAssertEqual(view["zoomValue"] as? Double, 72)

        let origin = try XCTUnwrap(view["scrollOrigin"] as? [String: Any], "Expected scrollOrigin")
        XCTAssertEqual(origin["x"] as? Double, 240)
        XCTAssertEqual(origin["y"] as? Double, 90)
    }

    func test__converter__test_user__TestDefaultViewport__test_large_oval() throws {
        // Port of tests/converter/test_user.py::TestDefaultViewport.test_large_oval
        let user = try makeUserJSON(for: [
            .rectangle(.init(
                guid: [0, 2],
                name: "oval",
                x: 0,
                y: 0,
                width: 10,
                height: 5_000
            )),
        ])

        let pageID = try XCTUnwrap(user.keys.first(where: { $0 != "document" }))
        let view = try XCTUnwrap(user[pageID] as? [String: Any], "Expected per-page viewport settings")
        let zoom = try XCTUnwrap(view["zoomValue"] as? Double, "Expected zoomValue")
        XCTAssertEqual(zoom, 0.144, accuracy: 0.000_001)

        let origin = try XCTUnwrap(view["scrollOrigin"] as? [String: Any], "Expected scrollOrigin")
        let originX = try XCTUnwrap(origin["x"] as? Double, "Expected scrollOrigin.x")
        let originY = try XCTUnwrap(origin["y"] as? Double, "Expected scrollOrigin.y")
        XCTAssertEqual(originX, 599.28, accuracy: 0.000_001)
        XCTAssertEqual(originY, 90, accuracy: 0.000_001)
    }

    func test__converter__test_user__TestDefaultViewport__test_empty_page() throws {
        // Port of tests/converter/test_user.py::TestDefaultViewport.test_empty_page
        let user = try makeUserJSON(for: [])

        let pageID = try XCTUnwrap(user.keys.first(where: { $0 != "document" }))
        let view = try XCTUnwrap(user[pageID] as? [String: Any], "Expected per-page viewport settings")
        XCTAssertEqual(view["zoomValue"] as? Double, 1)

        let origin = try XCTUnwrap(view["scrollOrigin"] as? [String: Any], "Expected scrollOrigin")
        XCTAssertEqual(origin["x"] as? Double, 0)
        XCTAssertEqual(origin["y"] as? Double, 0)
    }

    private func makeUserJSON(for layers: [ConversionLayer]) throws -> [String: Any] {
        let pageGUID: [UInt32] = [0, 1]
        let document = ConversionDocument(
            pages: [
                .init(guid: pageGUID, name: "page", layers: layers),
            ]
        )

        let bundle = SketchBundleBuilder.build(from: document, salt: Data("compat-tests".utf8))
        let userData = try XCTUnwrap(bundle["user.json"], "Missing user.json")
        return try FixtureSupport.parseJSONObject(data: userData)
    }
}
