import XCTest
@testable import Fig2SketchCore

final class SketchJSONWriterTests: XCTestCase {
    func testObjectOmitsNilFieldsAndStripsTrailingUnderscore() {
        let value: SketchJSONValue = .object(
            SketchJSONObject([
                ("_class", .string("rectangle")),
                ("from_", .string("A")),
                ("optional", nil),
                ("count", .int(2)),
            ])
        )

        XCTAssertEqual(
            SketchJSONWriter.serializeString(value),
            "{\"_class\":\"rectangle\",\"from\":\"A\",\"count\":2}"
        )
    }

    func testPreservesFieldOrderAndNestedStructures() {
        let value: SketchJSONValue = .object(
            SketchJSONObject([
                ("z", .int(1)),
                ("a", .array([.bool(true), .null, .double(0.25)])),
                ("nested", .object(SketchJSONObject([
                    ("x_", .int(9)),
                    ("y", .string("ok")),
                ]))),
            ])
        )

        XCTAssertEqual(
            SketchJSONWriter.serializeString(value),
            "{\"z\":1,\"a\":[true,null,0.25],\"nested\":{\"x\":9,\"y\":\"ok\"}}"
        )
    }

    func testWritesUnicodeWithoutEscapingToSurrogatePairs() {
        let value: SketchJSONValue = .object(
            SketchJSONObject([
                ("text", .string("Hello 😀 café")),
            ])
        )

        let output = SketchJSONWriter.serializeString(value)
        XCTAssertTrue(output.contains("😀"))
        XCTAssertTrue(output.contains("café"))
        XCTAssertFalse(output.lowercased().contains("\\ud83d"))
    }

    func testEscapesControlCharactersAndQuotes() {
        let value: SketchJSONValue = .string("line1\n\"q\"\t\\")
        XCTAssertEqual(
            SketchJSONWriter.serializeString(value),
            "\"line1\\n\\\"q\\\"\\t\\\\\""
        )
    }
}
