import Foundation

public enum Version {
    public static let current: String = resolve()

    struct Environment: Sendable {
        var variables: [String: String]
        var bundleVersion: String?
        var currentDirectoryURL: URL
        var executableURL: URL?
        var fileExists: @Sendable (URL) -> Bool
        var listDirectoryContents: @Sendable (URL) throws -> [URL]
        var readFile: @Sendable (URL) throws -> String
        var maxAncestorDepth: Int = 128
        var trace: (@Sendable (String) -> Void)? = nil

        static var live: Environment {
            let currentDirectoryURL = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
            let executableURL = URL(fileURLWithPath: CommandLine.arguments.first ?? "")
            return Environment(
                variables: ProcessInfo.processInfo.environment,
                bundleVersion: Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String,
                currentDirectoryURL: currentDirectoryURL,
                executableURL: executableURL.path.isEmpty ? nil : executableURL,
                fileExists: { url in
                    FileManager.default.fileExists(atPath: url.path)
                },
                listDirectoryContents: { directory in
                    try FileManager.default.contentsOfDirectory(
                        at: directory,
                        includingPropertiesForKeys: nil,
                        options: [.skipsHiddenFiles]
                    )
                },
                readFile: { url in
                    try String(contentsOf: url, encoding: .utf8)
                },
                maxAncestorDepth: 128,
                trace: nil
            )
        }
    }

    static func resolve(environment: Environment = .live) -> String {
        if let envVersion = environment.variables["FIG2SKETCH_VERSION"],
           !envVersion.isEmpty {
            return envVersion
        }

        if let bundleVersion = environment.bundleVersion,
           !bundleVersion.isEmpty {
            return bundleVersion
        }

        for root in candidateRepositoryRoots(environment: environment) {
            if let metadataVersion = pythonPackageVersion(inRepositoryRoot: root, environment: environment) {
                return metadataVersion
            }
        }

        return "unknown version"
    }

    private static func candidateRepositoryRoots(environment: Environment) -> [URL] {
        let seeds = [environment.currentDirectoryURL, environment.executableURL].compactMap { $0 }
        var seen: Set<String> = []
        var roots: [URL] = []

        trace("version.resolve.seeds=\(seeds.map(\.path).joined(separator: ","))", environment: environment)
        for seed in seeds {
            trace("version.resolve.seed=\(seed.path)", environment: environment)
            for candidate in ancestorChain(startingAt: seed, environment: environment) {
                let standardized = candidate.standardizedFileURL.path
                guard seen.insert(standardized).inserted else { continue }
                guard looksLikeRepositoryRoot(candidate, environment: environment) else { continue }
                trace("version.resolve.root=\(standardized)", environment: environment)
                roots.append(candidate)
            }
        }

        return roots
    }

    private static func ancestorChain(startingAt url: URL, environment: Environment) -> [URL] {
        var current = url.hasDirectoryPath ? url : url.deletingLastPathComponent()
        var ancestors: [URL] = []
        var seen: Set<String> = []

        for _ in 0..<environment.maxAncestorDepth {
            let standardized = current.standardizedFileURL.path
            guard seen.insert(standardized).inserted else {
                trace("version.resolve.repeat-ancestor=\(standardized)", environment: environment)
                break
            }
            ancestors.append(current)
            let parent = current.deletingLastPathComponent()
            if parent.path == current.path {
                break
            }
            current = parent
        }

        if ancestors.count == environment.maxAncestorDepth {
            trace("version.resolve.ancestor-limit=\(current.path)", environment: environment)
        }

        return ancestors
    }

    private static func looksLikeRepositoryRoot(_ url: URL, environment: Environment) -> Bool {
        environment.fileExists(url.appendingPathComponent("pyproject.toml")) &&
            environment.fileExists(url.appendingPathComponent("src/fig2sketch.py"))
    }

    private static func pythonPackageVersion(
        inRepositoryRoot root: URL,
        environment: Environment
    ) -> String? {
        trace("version.resolve.scan-root=\(root.path)", environment: environment)
        let venvLibURL = root.appendingPathComponent(".venv/lib", isDirectory: true)
        guard environment.fileExists(venvLibURL) else { return nil }

        guard let pythonLibDirectories = try? environment.listDirectoryContents(venvLibURL) else {
            return nil
        }

        for pythonLib in pythonLibDirectories.sorted(by: { $0.lastPathComponent < $1.lastPathComponent }) {
            let sitePackages = pythonLib.appendingPathComponent("site-packages", isDirectory: true)
            guard environment.fileExists(sitePackages) else { continue }
            guard let entries = try? environment.listDirectoryContents(sitePackages) else { continue }

            let metadataCandidates = entries
                .filter { entry in
                    let name = entry.lastPathComponent
                    return name.hasPrefix("fig2sketch-") && name.hasSuffix(".dist-info")
                        || name == "fig2sketch.egg-info"
                }
                .sorted(by: { $0.lastPathComponent < $1.lastPathComponent })

            for metadataDirectory in metadataCandidates {
                for fileName in ["METADATA", "PKG-INFO"] {
                    let metadataURL = metadataDirectory.appendingPathComponent(fileName)
                    guard environment.fileExists(metadataURL) else { continue }
                    guard let version = parseVersionField(
                        from: (try? environment.readFile(metadataURL)) ?? ""
                    ) else {
                        continue
                    }
                    trace("version.resolve.version=\(version) from \(metadataURL.path)", environment: environment)
                    return version
                }
            }
        }

        return nil
    }

    private static func trace(_ message: String, environment: Environment) {
        environment.trace?(message)
    }

    private static func parseVersionField(from metadata: String) -> String? {
        for line in metadata.split(whereSeparator: \.isNewline) {
            guard line.hasPrefix("Version:") else { continue }
            let version = line.dropFirst("Version:".count).trimmingCharacters(in: .whitespaces)
            return version.isEmpty ? nil : version
        }
        return nil
    }
}
