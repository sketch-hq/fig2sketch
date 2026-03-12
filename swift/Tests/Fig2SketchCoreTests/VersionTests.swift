import Foundation
import XCTest
@testable import Fig2SketchCore

final class VersionTests: XCTestCase {
    func testResolvePrefersEnvironmentOverride() {
        let fileSystem = FakeFileSystem.repositoryFixture(version: "0.0.0")

        let environment = fileSystem.makeEnvironment(
            variables: ["FIG2SKETCH_VERSION": "1.2.3"],
            currentDirectoryPath: "/repo"
        )

        XCTAssertEqual(Version.resolve(environment: environment), "1.2.3")
    }

    func testResolvePrefersBundleVersionOverRepositoryMetadata() {
        let fileSystem = FakeFileSystem.repositoryFixture(version: "0.0.0")

        let environment = fileSystem.makeEnvironment(
            bundleVersion: "2.3.4",
            currentDirectoryPath: "/repo"
        )

        XCTAssertEqual(Version.resolve(environment: environment), "2.3.4")
    }

    func testResolveFallsBackToRepoPythonMetadataFromCurrentDirectory() {
        let fileSystem = FakeFileSystem.repositoryFixture(version: "0.0.0")

        let environment = fileSystem.makeEnvironment(
            currentDirectoryPath: "/repo/swift"
        )

        XCTAssertEqual(Version.resolve(environment: environment), "0.0.0")
    }

    func testResolveFallsBackToRepoPythonMetadataFromExecutablePath() {
        let fileSystem = FakeFileSystem.repositoryFixture(version: "0.0.0")

        let environment = fileSystem.makeEnvironment(
            currentDirectoryPath: "/outside",
            executablePath: "/repo/swift/.build/debug/fig2sketch"
        )

        XCTAssertEqual(Version.resolve(environment: environment), "0.0.0")
    }

    func testResolveReturnsUnknownVersionWhenRepositoryMetadataIsMissing() {
        var fileSystem = FakeFileSystem()
        fileSystem.addDirectory("/repo")
        fileSystem.addFile("/repo/pyproject.toml", contents: "[project]\nname = \"fig2sketch\"\n")
        fileSystem.addDirectory("/repo/src")
        fileSystem.addFile("/repo/src/fig2sketch.py", contents: "__version__ = '0.0.0'\n")

        let environment = fileSystem.makeEnvironment(
            currentDirectoryPath: "/repo"
        )

        XCTAssertEqual(Version.resolve(environment: environment), "unknown version")
    }

    func testResolveStopsAfterMaxAncestorDepth() {
        let fileSystem = FakeFileSystem.repositoryFixture(version: "0.0.0")
        let trace = LockedTrace()

        let environment = fileSystem.makeEnvironment(
            currentDirectoryPath: "/repo/swift/.build/debug/deep/nested",
            maxAncestorDepth: 2,
            trace: { message in
                trace.append(message)
            }
        )

        XCTAssertEqual(Version.resolve(environment: environment), "unknown version")
        XCTAssertTrue(
            trace.messages.contains(where: { $0.contains("version.resolve.ancestor-limit=") }),
            "expected trace to record the ancestor depth limit"
        )
    }
}

private struct FakeFileSystem: Sendable {
    private(set) var files: [String: String] = [:]
    private(set) var directories: Set<String> = ["/"]

    static func repositoryFixture(version: String, rootPath: String = "/repo") -> FakeFileSystem {
        var fileSystem = FakeFileSystem()
        fileSystem.addDirectory(rootPath)
        fileSystem.addFile("\(rootPath)/pyproject.toml", contents: "[project]\nname = \"fig2sketch\"\n")
        fileSystem.addDirectory("\(rootPath)/src")
        fileSystem.addFile("\(rootPath)/src/fig2sketch.py", contents: "__version__ = '\(version)'\n")
        fileSystem.addDirectory("\(rootPath)/.venv")
        fileSystem.addDirectory("\(rootPath)/.venv/lib")
        fileSystem.addDirectory("\(rootPath)/.venv/lib/python3.14")
        fileSystem.addDirectory("\(rootPath)/.venv/lib/python3.14/site-packages")
        fileSystem.addDirectory("\(rootPath)/.venv/lib/python3.14/site-packages/fig2sketch-\(version).dist-info")
        fileSystem.addFile(
            "\(rootPath)/.venv/lib/python3.14/site-packages/fig2sketch-\(version).dist-info/METADATA",
            contents: "Metadata-Version: 2.4\nName: fig2sketch\nVersion: \(version)\n"
        )
        fileSystem.addDirectory("\(rootPath)/swift")
        fileSystem.addDirectory("\(rootPath)/swift/.build")
        fileSystem.addDirectory("\(rootPath)/swift/.build/debug")
        return fileSystem
    }

    mutating func addDirectory(_ path: String) {
        let normalized = Self.normalize(path: path)
        directories.insert(normalized)

        var current = normalized
        while current != "/" {
            current = parentPath(of: current)
            directories.insert(current)
        }
    }

    mutating func addFile(_ path: String, contents: String) {
        let normalized = Self.normalize(path: path)
        files[normalized] = contents
        addDirectory(parentPath(of: normalized))
    }

    func makeEnvironment(
        variables: [String: String] = [:],
        bundleVersion: String? = nil,
        currentDirectoryPath: String,
        executablePath: String? = nil,
        maxAncestorDepth: Int = 128,
        trace: (@Sendable (String) -> Void)? = nil
    ) -> Version.Environment {
        let files = self.files
        let directories = self.directories

        return Version.Environment(
            variables: variables,
            bundleVersion: bundleVersion,
            currentDirectoryURL: URL(fileURLWithPath: Self.normalize(path: currentDirectoryPath), isDirectory: true),
            executableURL: executablePath.map { URL(fileURLWithPath: Self.normalize(path: $0), isDirectory: false) },
            fileExists: { url in
                let path = Self.normalize(url: url)
                return directories.contains(path) || files[path] != nil
            },
            listDirectoryContents: { url in
                let directory = Self.normalize(url: url)
                guard directories.contains(directory) else {
                    throw CocoaError(.fileNoSuchFile)
                }

                return Self.immediateChildren(
                    in: directory,
                    directories: directories,
                    files: files
                ).map { child in
                    let isDirectory = directories.contains(child)
                    return URL(fileURLWithPath: child, isDirectory: isDirectory)
                }.sorted(by: { $0.path < $1.path })
            },
            readFile: { url in
                let path = Self.normalize(url: url)
                guard let contents = files[path] else {
                    throw CocoaError(.fileReadNoSuchFile)
                }
                return contents
            },
            maxAncestorDepth: maxAncestorDepth,
            trace: trace
        )
    }

    private func parentPath(of path: String) -> String {
        guard path != "/" else { return "/" }
        let url = URL(fileURLWithPath: path, isDirectory: directories.contains(path))
        let parent = url.deletingLastPathComponent().standardizedFileURL.path
        return parent.isEmpty ? "/" : parent
    }

    private static func normalize(path: String) -> String {
        let url = URL(fileURLWithPath: path, isDirectory: path == "/" || path.hasSuffix("/"))
        let normalized = url.standardizedFileURL.path
        return normalized.isEmpty ? "/" : normalized
    }

    private static func normalize(url: URL) -> String {
        let normalized = url.standardizedFileURL.path
        return normalized.isEmpty ? "/" : normalized
    }

    private static func immediateChildren(
        in directory: String,
        directories: Set<String>,
        files: [String: String]
    ) -> [String] {
        let prefix = directory == "/" ? "/" : "\(directory)/"
        var children: Set<String> = []

        for candidate in directories where candidate != directory && candidate.hasPrefix(prefix) {
            let remainder = String(candidate.dropFirst(prefix.count))
            guard let nextComponent = remainder.split(separator: "/").first else { continue }
            children.insert(prefix + nextComponent)
        }

        for candidate in files.keys where candidate.hasPrefix(prefix) {
            let remainder = String(candidate.dropFirst(prefix.count))
            guard let nextComponent = remainder.split(separator: "/").first else { continue }
            children.insert(prefix + nextComponent)
        }

        return children.sorted()
    }
}

private final class LockedTrace: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String] = []

    var messages: [String] {
        lock.lock()
        defer { lock.unlock() }
        return storage
    }

    func append(_ message: String) {
        lock.lock()
        storage.append(message)
        lock.unlock()
    }
}
