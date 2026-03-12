import Foundation

public enum CLIParseResult: Equatable, Sendable {
    case run(CLIOptions)
    case help(String)
    case version(String)
}

public enum CLIParseError: Error, Equatable, CustomStringConvertible, Sendable {
    case unknownOption(String)
    case missingValue(String)
    case invalidValue(option: String, value: String, allowed: [String])
    case missingPositionals([String])
    case tooManyPositionals([String])

    public var description: String {
        switch self {
        case .unknownOption(let option):
            return "unrecognized arguments: \(option)"
        case .missingValue(let option):
            return "argument \(option): expected one argument"
        case .invalidValue(let option, let value, let allowed):
            return "argument \(option): invalid choice: '\(value)' (choose from \(allowed.joined(separator: ", ")))"
        case .missingPositionals(let names):
            return "the following arguments are required: \(names.joined(separator: ", "))"
        case .tooManyPositionals(let values):
            return "unrecognized arguments: \(values.joined(separator: " "))"
        }
    }
}

public struct CLIParser: Sendable {
    public let versionString: String

    public init(versionString: String) {
        self.versionString = versionString
    }

    public func parse<S>(_ args: S) throws -> CLIParseResult where S: Sequence, S.Element == String {
        var positionals: [String] = []
        var instanceOverride: CLIOptions.InstanceOverride = .detach
        var forceConvertImages = false
        var compress = false
        var verbosity = 0
        var salt: String?
        var dumpFigJSONPath: String?
        var parsingOptions = true

        var iterator = args.makeIterator()
        while let arg = iterator.next() {
            if parsingOptions && arg == "--" {
                parsingOptions = false
                continue
            }

            if parsingOptions && (arg == "--help" || arg == "-h") {
                return .help(Self.helpText(versionString: versionString))
            }

            if parsingOptions && arg == "--version" {
                return .version("fig2sketch \(versionString)")
            }

            if parsingOptions && arg.hasPrefix("--") {
                let (name, inlineValue) = splitLongOption(arg)
                switch name {
                case "--instance-override":
                    let raw = try requireValue(for: name, inlineValue: inlineValue, iterator: &iterator)
                    guard let parsed = CLIOptions.InstanceOverride(rawValue: raw) else {
                        throw CLIParseError.invalidValue(
                            option: name,
                            value: raw,
                            allowed: [CLIOptions.InstanceOverride.detach.rawValue, CLIOptions.InstanceOverride.ignore.rawValue]
                        )
                    }
                    instanceOverride = parsed
                case "--force-convert-images":
                    try rejectInlineValue(on: name, inlineValue: inlineValue)
                    forceConvertImages = true
                case "--compress":
                    try rejectInlineValue(on: name, inlineValue: inlineValue)
                    compress = true
                case "--salt":
                    salt = try requireValue(for: name, inlineValue: inlineValue, iterator: &iterator)
                case "--dump-fig-json":
                    dumpFigJSONPath = try requireValue(for: name, inlineValue: inlineValue, iterator: &iterator)
                default:
                    throw CLIParseError.unknownOption(name)
                }
                continue
            }

            if parsingOptions && arg.hasPrefix("-") && arg != "-" {
                if arg.allSatisfy({ $0 == "-" || $0 == "v" }) && arg.first == "-" {
                    verbosity += arg.dropFirst().count
                    continue
                }
                throw CLIParseError.unknownOption(arg)
            }

            positionals.append(arg)
        }

        let expectedPositionals = ["fig_file", "sketch_file"]
        let missingPositionals = Array(expectedPositionals.dropFirst(positionals.count))
        if !missingPositionals.isEmpty {
            throw CLIParseError.missingPositionals(missingPositionals)
        }
        if positionals.count > 2 {
            throw CLIParseError.tooManyPositionals(Array(positionals.dropFirst(2)))
        }

        return .run(
            CLIOptions(
                figFile: positionals[0],
                sketchFile: positionals[1],
                instanceOverride: instanceOverride,
                forceConvertImages: forceConvertImages,
                compress: compress,
                verbosity: verbosity,
                salt: salt,
                dumpFigJSONPath: dumpFigJSONPath
            )
        )
    }

    public static func helpText(versionString: String) -> String {
        """
        usage: fig2sketch [-h] [--instance-override {detach,ignore}]
                          [--force-convert-images] [--compress] [-v] [--salt SALT]
                          [--dump-fig-json DUMP_FIG_JSON] [--version]
                          fig_file sketch_file

        Converts a .fig document to .sketch

        positional arguments:
          fig_file
          sketch_file

        options:
          -h, --help            show this help message and exit
          --version             show program's version number and exit

        conversion options:
          --instance-override {detach,ignore}
                                what to do when converting unsupported instance
                                override (default = detach)
          --force-convert-images
                                try to convert corrupted images
          --compress            compress the output sketch file

        debug options:
          -v                    return more details, can be repeated
          --salt SALT           salt used to generate ids, defaults to random
          --dump-fig-json DUMP_FIG_JSON
                                output a fig representation in json for debugging
                                purposes
        """
    }

    public static func usageText() -> String {
        """
        usage: fig2sketch [-h] [--instance-override {detach,ignore}]
                          [--force-convert-images] [--compress] [-v] [--salt SALT]
                          [--dump-fig-json DUMP_FIG_JSON] [--version]
                          fig_file sketch_file
        """
    }

    private func splitLongOption(_ arg: String) -> (String, String?) {
        guard let idx = arg.firstIndex(of: "=") else {
            return (arg, nil)
        }
        return (String(arg[..<idx]), String(arg[arg.index(after: idx)...]))
    }

    private func rejectInlineValue(on name: String, inlineValue: String?) throws {
        if inlineValue != nil {
            throw CLIParseError.unknownOption(name)
        }
    }

    private func requireValue<I: IteratorProtocol>(
        for option: String,
        inlineValue: String?,
        iterator: inout I
    ) throws -> String where I.Element == String {
        if let inlineValue {
            return inlineValue
        }
        guard let next = iterator.next() else {
            throw CLIParseError.missingValue(option)
        }
        return next
    }
}
