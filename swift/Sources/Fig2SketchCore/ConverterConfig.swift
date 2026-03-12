import Foundation

public struct ConversionConfig: Equatable, Sendable {
    public var canDetach: Bool
    public var salt: Data
    public var version: String

    public init(canDetach: Bool = true, salt: Data = Data(), version: String = "?") {
        self.canDetach = canDetach
        self.salt = salt
        self.version = version
    }
}
