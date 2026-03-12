import Foundation
import XCTest
import ZIPFoundation
@testable import Fig2SketchCore

final class IntegrationTest_structureTests: XCTestCase {
    func test__integration__test_structure__test_user() throws {
        // Port of tests/integration/test_structure.py::test_user
        do {
            try withStructureSketchArchive { archive in
                let user = try readJSONObject(path: "user.json", from: archive)
                guard user["8F292FCA-49C0-4E31-957E-93FB2D1A7231"] != nil else {
                    return XCTFail("Missing first page user entry")
                }
                guard user["A4E5259A-9CE6-49D9-B4A1-A8062C205347"] != nil else {
                    return XCTFail("Missing symbols page user entry")
                }

                let document = try XCTUnwrap(user["document"] as? [String: Any])
                XCTAssertEqual(document["pageListHeight"] as? Int, 200)
            }
        } catch {
            XCTFail("test_user setup/read failed: \(error)")
        }
    }

    func test__integration__test_structure__test_meta() throws {
        // Port of tests/integration/test_structure.py::test_meta
        do {
            try withStructureSketchArchive { archive in
                let meta = try readJSONObject(path: "meta.json", from: archive)
                XCTAssertEqual(meta["commit"] as? String, "1899e24f63af087a9dd3c66f73b492b72c27c2c8")
                XCTAssertEqual(meta["version"] as? Int, 164)
            }
        } catch {
            XCTFail("test_meta setup/read failed: \(error)")
        }
    }

    func test__integration__test_structure__test_document() throws {
        // Port of tests/integration/test_structure.py::test_document
        do {
            try withStructureSketchArchive { archive in
                let document = try readJSONObject(path: "document.json", from: archive)
                XCTAssertEqual(document["_class"] as? String, "document")

                let pages = try XCTUnwrap(document["pages"] as? [[String: Any]])
                guard pages.count == 2 else {
                    return XCTFail("Expected 2 pages, got \(pages.count)")
                }
                XCTAssertEqual(pages[0]["_ref"] as? String, "pages/8F292FCA-49C0-4E31-957E-93FB2D1A7231")
                XCTAssertEqual(pages[1]["_ref"] as? String, "pages/A4E5259A-9CE6-49D9-B4A1-A8062C205347")
            }
        } catch {
            XCTFail("test_document setup/read failed: \(error)")
        }
    }

    func test__integration__test_structure__test_file_hashes() throws {
        // Port of tests/integration/test_structure.py::test_file_hashes
        do {
            try withStructureSketchArchive { archive in
                let paths = [
                    "images/616d10a80971e08c6b43a164746afac1972c7ccc.png",
                    "images/92e4d5e0c24ffd632c3db3264e62cc907c2f5e29",
                ]

                for path in paths {
                    guard archive[path] != nil else {
                        return XCTFail("Missing file expected by parity test: \(path)")
                    }
                    let data = try readEntryData(path: path, from: archive)
                    let generated = ConverterUtils.generateFileRef(data)
                    let expected = String(path.split(separator: "/")[1].split(separator: ".")[0])
                    XCTAssertEqual(generated, expected, "Hash mismatch for \(path)")
                }

                for path in archive.map(\.path).filter({ $0.hasPrefix("fonts/") }) {
                    let data = try readEntryData(path: path, from: archive)
                    let generated = ConverterUtils.generateFileRef(data)
                    let expected = String(path.split(separator: "/")[1].split(separator: ".")[0])
                    XCTAssertEqual(generated, expected, "Hash mismatch for \(path)")
                }
            }
        } catch {
            XCTFail("test_file_hashes setup/read failed: \(error)")
        }
    }

    func test__integration__test_structure__test_page() throws {
        // Port of tests/integration/test_structure.py::test_page
        do {
            try withStructureSketchArchive { archive in
                let page = try readJSONObject(path: "pages/8F292FCA-49C0-4E31-957E-93FB2D1A7231.json", from: archive)
                XCTAssertEqual(page["name"] as? String, "Page 1")

                let layers = try XCTUnwrap(page["layers"] as? [[String: Any]])
                guard layers.count == 2 else {
                    return XCTFail("Expected 2 top-level layers, got \(layers.count)")
                }

                let groups = layers[0]
                XCTAssertEqual(groups["_class"] as? String, "group")
                XCTAssertEqual(groups["name"] as? String, "Groups")

                let syms = layers[1]
                XCTAssertEqual(syms["_class"] as? String, "group")
                XCTAssertEqual(syms["name"] as? String, "Symbols and images")

                let symsLayers = try XCTUnwrap(syms["layers"] as? [[String: Any]])
                guard symsLayers.count >= 2 else {
                    return XCTFail("Expected at least 2 symbol layers")
                }
                XCTAssertEqual(symsLayers[0]["_class"] as? String, "symbolInstance")
                XCTAssertEqual(symsLayers[1]["_class"] as? String, "symbolInstance")
            }
        } catch {
            XCTFail("test_page setup/read failed: \(error)")
        }
    }

    func test__integration__test_structure__test_symbols_page() throws {
        // Port of tests/integration/test_structure.py::test_symbols_page
        do {
            try withStructureSketchArchive { archive in
                let page = try readJSONObject(path: "pages/A4E5259A-9CE6-49D9-B4A1-A8062C205347.json", from: archive)
                XCTAssertEqual(page["name"] as? String, "Symbols")

                let layers = try XCTUnwrap(page["layers"] as? [[String: Any]])
                guard let symbol = layers.first else {
                    return XCTFail("Expected one symbol layer")
                }
                XCTAssertEqual(symbol["name"] as? String, "Component 1")
                XCTAssertEqual(symbol["_class"] as? String, "symbolMaster")
                XCTAssertEqual((symbol["layers"] as? [[String: Any]])?.count, 2)
            }
        } catch {
            XCTFail("test_symbols_page setup/read failed: \(error)")
        }
    }

    func test__integration__test_structure__test_files() throws {
        // Port of tests/integration/test_structure.py::test_files
        do {
            try withStructureSketchArchive { archive in
                let names = archive.map(\.path)
                XCTAssertEqual(names.filter { !$0.hasPrefix("fonts/") }, [
                    "previews/preview.png",
                    "images/616d10a80971e08c6b43a164746afac1972c7ccc.png",
                    "images/92e4d5e0c24ffd632c3db3264e62cc907c2f5e29",
                    "pages/8F292FCA-49C0-4E31-957E-93FB2D1A7231.json",
                    "pages/A4E5259A-9CE6-49D9-B4A1-A8062C205347.json",
                    "document.json",
                    "user.json",
                    "meta.json",
                ])
                XCTAssertTrue(names.filter { $0.hasPrefix("fonts/") }.allSatisfy { $0.split(separator: "/").count == 2 })
            }
        } catch {
            XCTFail("test_files setup/read failed: \(error)")
        }
    }

    private func withStructureSketchArchive(_ body: (Archive) throws -> Void) throws {
        let fixtureURL = structureFigURL()
        let tempRoot = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempRoot, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempRoot) }

        let outURL = tempRoot.appendingPathComponent("out.sketch")
        var output = RecordingOutput()
        let exitCode = CLIConversionRunner.run(
            options: CLIOptions(
                figFile: fixtureURL.path,
                sketchFile: outURL.path,
                salt: "1234"
            ),
            output: &output
        )

        guard exitCode == 0 else {
            throw NSError(domain: "IntegrationTest_structureTests", code: Int(exitCode), userInfo: [
                NSLocalizedDescriptionKey: "Conversion failed: \(output.stderr)",
            ])
        }

        let archive = try Archive(url: outURL, accessMode: .read)
        try body(archive)
    }

    private func structureFigURL() -> URL {
        let file = URL(fileURLWithPath: #filePath)
        let repoRoot = file
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
        return repoRoot.appendingPathComponent("tests/data/structure.fig")
    }

    private func readJSONObject(path: String, from archive: Archive) throws -> [String: Any] {
        let data = try readEntryData(path: path, from: archive)
        let object = try JSONSerialization.jsonObject(with: data)
        return try XCTUnwrap(object as? [String: Any], "Expected JSON object at \(path)")
    }

    private func readEntryData(path: String, from archive: Archive) throws -> Data {
        guard let entry = archive[path] else {
            throw NSError(domain: "IntegrationTest_structureTests", code: 1, userInfo: [
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
