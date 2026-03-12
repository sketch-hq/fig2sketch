import Foundation

public struct SketchBundle: Equatable, Sendable {
    public struct Entry: Equatable, Sendable {
        public var path: String
        public var data: Data

        public init(path: String, data: Data) {
            self.path = path
            self.data = data
        }
    }

    public var entries: [Entry]

    public init(entries: [Entry]) {
        self.entries = entries
    }

    public subscript(path: String) -> Data? {
        entries.first(where: { $0.path == path })?.data
    }

    public var paths: [String] {
        entries.map(\.path)
    }
}
