import XCTest
@testable import Fig2SketchCore

final class CLIParserTests: XCTestCase {
    private let parser = CLIParser(versionString: "1.2.3")

    func testParsesRequiredPositionalsWithDefaults() throws {
        let result = try parser.parse(["input.fig", "output.sketch"])

        guard case .run(let options) = result else {
            return XCTFail("Expected .run")
        }

        XCTAssertEqual(options.figFile, "input.fig")
        XCTAssertEqual(options.sketchFile, "output.sketch")
        XCTAssertEqual(options.instanceOverride, .detach)
        XCTAssertFalse(options.forceConvertImages)
        XCTAssertFalse(options.compress)
        XCTAssertEqual(options.verbosity, 0)
        XCTAssertNil(options.salt)
        XCTAssertNil(options.dumpFigJSONPath)
    }

    func testParsesInstanceOverride() throws {
        let result = try parser.parse(["--instance-override", "ignore", "a.fig", "b.sketch"])
        guard case .run(let options) = result else {
            return XCTFail("Expected .run")
        }
        XCTAssertEqual(options.instanceOverride, .ignore)
    }

    func testParsesLongOptionsAndEqualsSyntax() throws {
        let result = try parser.parse([
            "--force-convert-images",
            "--compress",
            "--salt=1234",
            "--dump-fig-json=debug.json",
            "a.fig",
            "b.sketch",
        ])
        guard case .run(let options) = result else {
            return XCTFail("Expected .run")
        }
        XCTAssertTrue(options.forceConvertImages)
        XCTAssertTrue(options.compress)
        XCTAssertEqual(options.salt, "1234")
        XCTAssertEqual(options.dumpFigJSONPath, "debug.json")
    }

    func testParsesVerbosityCountedFlags() throws {
        let one = try parser.parse(["-v", "a.fig", "b.sketch"])
        let two = try parser.parse(["-vv", "a.fig", "b.sketch"])
        let three = try parser.parse(["-v", "-vv", "a.fig", "b.sketch"])

        guard case .run(let oneOptions) = one,
              case .run(let twoOptions) = two,
              case .run(let threeOptions) = three else {
            return XCTFail("Expected .run")
        }

        XCTAssertEqual(oneOptions.verbosity, 1)
        XCTAssertEqual(twoOptions.verbosity, 2)
        XCTAssertEqual(threeOptions.verbosity, 3)
    }

    func testVersionAction() throws {
        let result = try parser.parse(["--version"])
        XCTAssertEqual(result, .version("fig2sketch 1.2.3"))
    }

    func testHelpAction() throws {
        let result = try parser.parse(["--help"])
        guard case .help(let text) = result else {
            return XCTFail("Expected .help")
        }
        XCTAssertTrue(text.contains("usage: fig2sketch"))
        XCTAssertTrue(text.contains("positional arguments:"))
        XCTAssertTrue(text.contains("--dump-fig-json"))
    }

    func testInvalidInstanceOverrideThrows() throws {
        XCTAssertThrowsError(
            try parser.parse(["--instance-override", "whatever", "a.fig", "b.sketch"])
        ) { error in
            XCTAssertEqual(
                error as? CLIParseError,
                .invalidValue(option: "--instance-override", value: "whatever", allowed: ["detach", "ignore"])
            )
        }
    }

    func testMissingPositionalsThrows() throws {
        XCTAssertThrowsError(try parser.parse([])) { error in
            XCTAssertEqual(
                error as? CLIParseError,
                .missingPositionals(["fig_file", "sketch_file"])
            )
        }
        XCTAssertThrowsError(try parser.parse(["a.fig"])) { error in
            XCTAssertEqual(error as? CLIParseError, .missingPositionals(["sketch_file"]))
        }
    }

    func testUnknownOptionThrows() throws {
        XCTAssertThrowsError(try parser.parse(["--wat", "a.fig", "b.sketch"])) { error in
            XCTAssertEqual(error as? CLIParseError, .unknownOption("--wat"))
        }
    }
}
