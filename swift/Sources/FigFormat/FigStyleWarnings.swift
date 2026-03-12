import Foundation

public struct FigStyleWarning: Equatable, Sendable {
    public var code: String
    public var nodeName: String
    public var nodeGUID: [UInt32]

    public init(code: String, nodeName: String, nodeGUID: [UInt32]) {
        self.code = code
        self.nodeName = nodeName
        self.nodeGUID = nodeGUID
    }
}

public enum FigStyleWarningScanner {
    public static func scan(tree: FigTree) -> [FigStyleWarning] {
        var warnings: [FigStyleWarning] = []
        var seen: Set<String> = []

        func emit(_ code: String, node: FigNode) {
            let key = "\(code):" + node.guid.map(String.init).joined(separator: "-")
            guard seen.insert(key).inserted else { return }
            warnings.append(FigStyleWarning(code: code, nodeName: node.name, nodeGUID: node.guid))
        }

        func visit(_ treeNode: FigTreeNode) {
            if let style = treeNode.node.style {
                if style.blurs.count > 1, style.blurs.first?.isEnabled == true {
                    emit("STY001", node: treeNode.node)
                }

                for paint in style.fills {
                    scanPaintWarnings(paint, node: treeNode.node, emit: emit)
                }
                for border in style.borders {
                    scanPaintWarnings(border.paint, node: treeNode.node, emit: emit)
                }
            }

            for child in treeNode.children {
                visit(child)
            }
        }

        func scanPaintWarnings(_ paint: FigPaint, node: FigNode, emit: (String, FigNode) -> Void) {
            switch paint.kind {
            case .gradient(let gradient):
                if gradient.usesDiamondFallback {
                    emit("STY002", node)
                }
            case .image(let image):
                if image.hasPaintFilter {
                    emit("STY005", node)
                }
            default:
                break
            }
        }

        visit(tree.root)
        return warnings
    }

    public static func message(for warning: FigStyleWarning) -> String {
        switch warning.code {
        case "STY001":
            return "[STY001] \(warning.nodeName) contains a layer blur and a background blur. Only one will be converted"
        case "STY002":
            return "[STY002] \(warning.nodeName) uses a diamond gradient. It will be converted as a radial gradient"
        case "STY005":
            return "[STY005] \(warning.nodeName) contains an image paint filter which is not supported"
        default:
            return "[\(warning.code)] \(warning.nodeName)"
        }
    }
}
