import Foundation
import XCTest
@testable import Fig2SketchCore

final class FontCacheResolverTests: XCTestCase {
    func testPrepareFontAssetsDownloadsGoogleFontOnCacheMiss() throws {
        let root = try makeTemporaryRoot()
        defer { try? FileManager.default.removeItem(at: root) }

        let fontsDirectory = root.appendingPathComponent("fonts", isDirectory: true)
        let fontData = Data("inter-regular-font".utf8)
        let environment = makeEnvironment(fontsDirectory: fontsDirectory) { url in
            if url.host == "fonts.google.com" {
                return .init(data: Data(googleFontsManifest.utf8), statusCode: 200)
            }
            if url.lastPathComponent == "Inter-Regular.ttf" {
                return .init(data: fontData, statusCode: 200)
            }

            XCTFail("Unexpected font fetch URL: \(url)")
            return .init(data: Data(), statusCode: 404)
        }

        let prepared = FontCacheResolver.prepareFontAssets(
            for: makeDocument(fontFamily: "Inter", fontStyle: "Regular"),
            environment: environment
        )

        let expectedHash = ConverterUtils.generateFileRef(fontData)
        XCTAssertEqual(prepared.warningMessages, [])
        XCTAssertEqual(prepared.entries.map(\.path), ["fonts/\(expectedHash)"])
        XCTAssertEqual(prepared.entries.first?.data, fontData)
        XCTAssertTrue(
            FileManager.default.fileExists(
                atPath: fontsDirectory.appendingPathComponent("Inter-Regular.ttf").path
            )
        )

        let referencesJSON = String(
            decoding: SketchJSONWriter.serialize(.array(prepared.references)),
            as: UTF8.self
        )
        XCTAssertTrue(referencesJSON.contains("\"fontFamilyName\":\"Inter\""))
        XCTAssertTrue(referencesJSON.contains("\"fontFileName\":\"Inter-Regular.ttf\""))
        XCTAssertTrue(referencesJSON.contains("\"postscriptNames\":[\"Inter-Regular\"]"))
        XCTAssertTrue(referencesJSON.contains("\"_ref\":\"fonts/\(expectedHash)\""))
    }

    func testPrepareFontAssetsWarnsWhenGoogleFontsDoesNotHaveRequestedFont() throws {
        let root = try makeTemporaryRoot()
        defer { try? FileManager.default.removeItem(at: root) }

        let environment = makeEnvironment(fontsDirectory: root.appendingPathComponent("fonts")) { _ in
            .init(data: Data(), statusCode: 404)
        }

        let prepared = FontCacheResolver.prepareFontAssets(
            for: makeDocument(fontFamily: "Inter", fontStyle: "Regular"),
            environment: environment
        )

        XCTAssertEqual(prepared.references, [])
        XCTAssertEqual(prepared.entries, [])
        XCTAssertEqual(
            prepared.warningMessages,
            ["Could not find font ('Inter', 'Regular') via Google Fonts"]
        )
    }

    func testBuildResultCarriesFontWarningsForDownloadFailures() throws {
        let root = try makeTemporaryRoot()
        defer { try? FileManager.default.removeItem(at: root) }

        let environment = makeEnvironment(fontsDirectory: root.appendingPathComponent("fonts")) { _ in
            throw URLError(.notConnectedToInternet)
        }

        let result = SketchBundleBuilder.buildResult(
            from: makeDocument(fontFamily: "Inter", fontStyle: "Regular"),
            salt: Data("1234".utf8),
            fontResolverEnvironment: environment
        )

        XCTAssertEqual(result.warnings, [])
        XCTAssertEqual(result.fontWarningMessages.count, 1)
        XCTAssertTrue(
            result.fontWarningMessages[0].hasPrefix(
                "Could not download font ('Inter', 'Regular'):"
            )
        )

        let documentJSON = try XCTUnwrap(result.bundle["document.json"]).utf8String
        XCTAssertTrue(documentJSON.contains("\"fontReferences\":[]"))
    }

    func testPrepareFontAssetsDoesNotUseLooseFamilyFallbacks() throws {
        let root = try makeTemporaryRoot()
        defer { try? FileManager.default.removeItem(at: root) }

        let fontsDirectory = root.appendingPathComponent("fonts", isDirectory: true)
        try FileManager.default.createDirectory(at: fontsDirectory, withIntermediateDirectories: true)
        try Data("cached-thin-font".utf8).write(
            to: fontsDirectory.appendingPathComponent("Inter_18pt-Thin.ttf")
        )

        let environment = makeEnvironment(fontsDirectory: fontsDirectory) { _ in
            throw URLError(.notConnectedToInternet)
        } fontMetadata: { url in
            if url.lastPathComponent == "Inter_18pt-Thin.ttf" {
                return ("Inter", "Thin", "Inter-Regular_Thin")
            }
            return (nil, nil, nil)
        }

        let prepared = FontCacheResolver.prepareFontAssets(
            for: makeDocument(fontFamily: "Inter", fontStyle: "Regular"),
            environment: environment
        )

        XCTAssertEqual(prepared.references, [])
        XCTAssertEqual(prepared.entries, [])
        XCTAssertEqual(prepared.warningMessages.count, 1)
    }

    private func makeTemporaryRoot() throws -> URL {
        let root = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)
        return root
    }

    private func makeDocument(fontFamily: String, fontStyle: String) -> ConversionDocument {
        ConversionDocument(
            pages: [
                ConversionPage(
                    guid: [1, 2],
                    name: "Page 1",
                    layers: [
                        .text(
                            ConversionText(
                                guid: [3, 4],
                                name: "Title",
                                x: 0,
                                y: 0,
                                width: 120,
                                height: 20,
                                characters: "Hello",
                                fontFamily: fontFamily,
                                fontStyle: fontStyle,
                                fontSize: 12
                            )
                        )
                    ]
                )
            ]
        )
    }

    private func makeEnvironment(
        fontsDirectory: URL,
        fetch: @escaping @Sendable (URL) throws -> FontCacheResolver.Environment.FetchResponse,
        fontMetadata: @escaping @Sendable (URL) -> (String?, String?, String?) = { url in
            if url.lastPathComponent == "Inter-Regular.ttf" {
                return ("Inter", "Regular", "Inter-Regular")
            }
            return (nil, nil, nil)
        }
    ) -> FontCacheResolver.Environment {
        .init(
            cacheDirectoryURL: { fontsDirectory },
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
            fetch: fetch,
            fontMetadata: fontMetadata
        )
    }
}

private extension Data {
    var utf8String: String {
        String(decoding: self, as: UTF8.self)
    }
}

private let googleFontsManifest = """
)]}'
{"manifest":{"fileRefs":[{"filename":"ofl/inter/Inter-Regular.ttf","url":"https://fonts.gstatic.com/s/inter/v1/Inter-Regular.ttf"},{"filename":"ofl/inter/OFL.txt","url":"https://fonts.gstatic.com/s/inter/v1/OFL.txt"}]}}
"""
