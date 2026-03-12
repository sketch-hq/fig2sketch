import Foundation
import XCTest
import ZIPFoundation
@testable import Fig2SketchCore

final class ConverterTest_imageTests: XCTestCase {
    func test__converter__test_image__test_corrupted_images() throws {
        // Port of tests/converter/test_image.py::test_corrupted_images
        let fixtureURL = brokenImagesFigURL()
        let tempRoot = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempRoot, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempRoot) }

        let outURL = tempRoot.appendingPathComponent("out.sketch")
        var output = RecordingOutput()
        let exitCode = CLIConversionRunner.run(
            options: CLIOptions(
                figFile: fixtureURL.path,
                sketchFile: outURL.path,
                verbosity: 1,
                salt: "1234"
            ),
            output: &output
        )

        XCTAssertEqual(exitCode, 0, "Conversion failed. stderr: \(output.stderr)")
        XCTAssertTrue(output.stderr.contains("[IMG003]"))
        XCTAssertTrue(output.stderr.contains("[IMG001]"))

        let archive = try Archive(url: outURL, accessMode: .read)
        let pagePaths = archive.map(\.path).filter { $0.hasPrefix("pages/") && $0.hasSuffix(".json") }
        XCTAssertFalse(pagePaths.isEmpty)

        var mergedPageJSON = ""
        for path in pagePaths {
            guard let entry = archive[path] else { continue }
            var data = Data()
            _ = try archive.extract(entry) { chunk in
                data.append(chunk)
            }
            mergedPageJSON += String(decoding: data, as: UTF8.self)
        }

        XCTAssertTrue(mergedPageJSON.contains("images/f2s_missing"))
        XCTAssertTrue(mergedPageJSON.contains("images/f2s_corrupted"))
    }

    private func brokenImagesFigURL() -> URL {
        let file = URL(fileURLWithPath: #filePath)
        let repoRoot = file
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
        return repoRoot.appendingPathComponent("tests/data/broken_images.fig")
    }
}

private struct RecordingOutput: CLIOutput {
    var stdout = ""
    var stderr = ""

    mutating func writeOut(_ message: String) {
        stdout.append(message)
    }

    mutating func writeErr(_ message: String) {
        stderr.append(message)
    }
}
