import Foundation

public protocol CLIOutput {
    mutating func writeOut(_ text: String)
    mutating func writeErr(_ text: String)
}

public struct StandardStreams: CLIOutput, Sendable {
    public init() {}

    public mutating func writeOut(_ text: String) {
        fputs(text, stdout)
    }

    public mutating func writeErr(_ text: String) {
        fputs(text, stderr)
    }
}
