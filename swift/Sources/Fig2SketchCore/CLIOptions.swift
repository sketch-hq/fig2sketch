import Foundation

public struct CLIOptions: Equatable, Sendable {
    public enum InstanceOverride: String, Equatable, Sendable {
        case detach
        case ignore
    }

    public var figFile: String
    public var sketchFile: String
    public var instanceOverride: InstanceOverride
    public var forceConvertImages: Bool
    public var compress: Bool
    public var verbosity: Int
    public var salt: String?
    public var dumpFigJSONPath: String?

    public init(
        figFile: String,
        sketchFile: String,
        instanceOverride: InstanceOverride = .detach,
        forceConvertImages: Bool = false,
        compress: Bool = false,
        verbosity: Int = 0,
        salt: String? = nil,
        dumpFigJSONPath: String? = nil
    ) {
        self.figFile = figFile
        self.sketchFile = sketchFile
        self.instanceOverride = instanceOverride
        self.forceConvertImages = forceConvertImages
        self.compress = compress
        self.verbosity = verbosity
        self.salt = salt
        self.dumpFigJSONPath = dumpFigJSONPath
    }
}
