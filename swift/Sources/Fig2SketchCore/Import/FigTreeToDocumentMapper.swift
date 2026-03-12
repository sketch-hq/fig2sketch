import FigFormat
import Foundation

public enum FigTreeToDocumentMapperError: Error, Equatable {
    case noCanvasFound
    case noRectangleFound
    case invalidPositioning([UInt32])
    case shapePathWarning(String, [UInt32])
}

public struct FigTreeMappingOptions: Equatable, Sendable {
    public var detachUnsupportedInstanceOverrides: Bool

    public init(detachUnsupportedInstanceOverrides: Bool = true) {
        self.detachUnsupportedInstanceOverrides = detachUnsupportedInstanceOverrides
    }
}

struct NodeFrame {
    var x: Double
    var y: Double
    var width: Double?
    var height: Double?
    var rotation: Double
}

struct ResolvedTextStyle {
    var family: String?
    var style: String?
    var postscript: String?
    var size: Double?
}

protocol LayerNodeConverting {
    func convert(
        node: FigNode,
        frame: NodeFrame,
        childLayers: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer]
}

struct RectangleNodeConverter: LayerNodeConverting {
    func convert(
        node: FigNode,
        frame: NodeFrame,
        childLayers _: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        try FigTreeToDocumentMapper.convertRectangleNode(node: node, frame: frame, context: context)
    }
}

struct TextNodeConverter: LayerNodeConverting {
    func convert(
        node: FigNode,
        frame: NodeFrame,
        childLayers _: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        try FigTreeToDocumentMapper.convertTextNode(node: node, frame: frame, context: &context)
    }
}

struct FrameNodeConverter: LayerNodeConverting {
    func convert(
        node: FigNode,
        frame: NodeFrame,
        childLayers: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        try FigTreeToDocumentMapper.convertFrameNode(
            node: node,
            frame: frame,
            childLayers: childLayers,
            context: &context
        )
    }
}

struct GroupContainerNodeConverter: LayerNodeConverting {
    func convert(
        node: FigNode,
        frame: NodeFrame,
        childLayers: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        try FigTreeToDocumentMapper.convertGroupContainerNode(
            node: node,
            frame: frame,
            childLayers: childLayers,
            context: &context
        )
    }
}

struct SymbolNodeConverter: LayerNodeConverting {
    func convert(
        node: FigNode,
        frame: NodeFrame,
        childLayers: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        try FigTreeToDocumentMapper.convertSymbolNode(
            node: node,
            frame: frame,
            childLayers: childLayers,
            context: &context
        )
    }
}

struct InstanceNodeConverter: LayerNodeConverting {
    func convert(
        node: FigNode,
        frame: NodeFrame,
        childLayers _: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        try FigTreeToDocumentMapper.convertInstanceNode(
            node: node,
            frame: frame,
            context: &context
        )
    }
}

struct VectorNodeConverter: LayerNodeConverting {
    func convert(
        node: FigNode,
        frame: NodeFrame,
        childLayers _: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        try FigTreeToDocumentMapper.convertVectorNode(node: node, frame: frame, context: context)
    }
}

struct MappingContext {
    var nodesByID: [[UInt32]: FigNode]
    var nodesByGUID: [[UInt32]: FigNode]
    var convertersByType: [String: any LayerNodeConverting]
    var options: FigTreeMappingOptions
    var warningRecorder = WarningRecorder()
    var warningCodesByNode: [[UInt32]: [String]] = [:]
    var symbolMastersByGUID: [[UInt32]: ConversionSymbolMaster] = [:]
    var symbolMasterOrder: [[UInt32]] = []

    func converter(for nodeType: String) -> (any LayerNodeConverting)? {
        convertersByType[nodeType]
    }

    func node(for guid: [UInt32]) -> FigNode? {
        nodesByID[guid]
    }

    func childNodes(of parentGUID: [UInt32]) -> [FigNode] {
        nodesByGUID.values.filter { $0.parentGuid == parentGUID }
    }

    mutating func registerSymbolMaster(_ master: ConversionSymbolMaster) {
        if symbolMastersByGUID[master.guid] != nil {
            return
        }
        symbolMastersByGUID[master.guid] = master
        symbolMasterOrder.append(master.guid)
    }

    func symbolMaster(for guid: [UInt32]) -> ConversionSymbolMaster? {
        symbolMastersByGUID[guid]
    }

    func orderedSymbolMasters() -> [ConversionSymbolMaster] {
        symbolMasterOrder.compactMap { symbolMastersByGUID[$0] }
    }

    mutating func emitWarning(_ code: String, nodeGUID: [UInt32]) {
        let nodeID = nodeGUID.map(String.init).joined(separator: ":")
        guard warningRecorder.shouldEmit(warningCode: code, nodeID: nodeID) else {
            return
        }
        warningCodesByNode[nodeGUID, default: []].append(code)
    }

    func warnings(for nodeGUID: [UInt32]) -> [String] {
        warningCodesByNode[nodeGUID] ?? []
    }
}

public enum FigTreeToDocumentMapper {
    public static func makeConversionDocument(
        from tree: FigTree,
        options: FigTreeMappingOptions = .init()
    ) throws -> ConversionDocument {
        let canvases = collectCanvases(in: tree.root)
        guard let canvas = canvases.first else {
            throw FigTreeToDocumentMapperError.noCanvasFound
        }

        var context = makeMappingContext(from: tree, options: options)
        var layers: [ConversionLayer] = []
        for child in orderedChildren(in: canvas) {
            layers.append(contentsOf: try convertNode(
                child,
                context: &context
            ))
        }
        guard !layers.isEmpty else {
            throw FigTreeToDocumentMapperError.noRectangleFound
        }

        let page = ConversionPage(
            guid: canvas.node.guid,
            name: canvas.node.name,
            layers: layers
        )

        var pages = [page]
        let symbolMasters = positionedSymbolMastersForSymbolsPage(context.orderedSymbolMasters())
        if !symbolMasters.isEmpty {
            pages.append(ConversionPage(
                guid: [0, 0],
                name: "Symbols",
                layers: symbolMasters.map(ConversionLayer.symbolMaster),
                idSuffix: Data("symbols_page".utf8)
            ))
        }
        return ConversionDocument(pages: pages)
    }

    private static func positionedSymbolMastersForSymbolsPage(
        _ symbolMasters: [ConversionSymbolMaster]
    ) -> [ConversionSymbolMaster] {
        var columns: [Double: (x: Double, nextY: Double)] = [0: (x: 0, nextY: 0)]

        return symbolMasters.map { master in
            var positioned = master
            if var column = columns[master.width] {
                positioned.x = column.x
                positioned.y = column.nextY
                column.nextY += master.height + 100
                columns[master.width] = column
            } else {
                let lastColumn = columns.max(by: { $0.value.x < $1.value.x }) ?? (key: 0, value: (x: 0, nextY: 0))
                let newX = lastColumn.value.x + lastColumn.key + 100
                positioned.x = newX
                positioned.y = 0
                columns[master.width] = (x: newX, nextY: master.height + 100)
            }
            return positioned
        }
    }

    private static func makeMappingContext(
        from tree: FigTree,
        options: FigTreeMappingOptions
    ) -> MappingContext {
        let nodes = allNodes(in: tree.root)
        var byGUID: [[UInt32]: FigNode] = [:]
        var byID: [[UInt32]: FigNode] = [:]
        for node in nodes {
            byGUID[node.guid] = node
            byID[node.guid] = node
            if let overrideKey = node.overrideKey {
                byID[overrideKey] = node
            }
        }
        return MappingContext(
            nodesByID: byID,
            nodesByGUID: byGUID,
            convertersByType: [
                "RECTANGLE": RectangleNodeConverter(),
                "ROUNDED_RECTANGLE": RectangleNodeConverter(),
                "ELLIPSE": RectangleNodeConverter(),
                "TEXT": TextNodeConverter(),
                "FRAME_CONTAINER": FrameNodeConverter(),
                "GROUP_CONTAINER": GroupContainerNodeConverter(),
                "SYMBOL": SymbolNodeConverter(),
                "INSTANCE": InstanceNodeConverter(),
                "VECTOR": VectorNodeConverter(),
                "LINE": VectorNodeConverter(),
            ],
            options: options
        )
    }

    private static func allNodes(in treeNode: FigTreeNode) -> [FigNode] {
        [treeNode.node] + treeNode.children.flatMap(allNodes)
    }

    private static func collectCanvases(in node: FigTreeNode) -> [FigTreeNode] {
        var result: [FigTreeNode] = []
        if node.node.type == "CANVAS" {
            result.append(node)
        }
        for child in node.children {
            result.append(contentsOf: collectCanvases(in: child))
        }
        return result
    }

    private static func convertNode(
        _ node: FigTreeNode,
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        let frame = try frameForNode(node.node)
        var childLayers: [ConversionLayer] = []
        for child in orderedChildren(in: node) {
            childLayers.append(contentsOf: try convertNode(
                child,
                context: &context
            ))
        }

        let resolvedType = resolvedConverterType(for: node.node)
        guard let converter = context.converter(for: resolvedType) else {
            return childLayers
        }
        let converted = try converter.convert(
            node: node.node,
            frame: frame,
            childLayers: childLayers,
            context: &context
        )
        if converted.isEmpty, !childLayers.isEmpty {
            return childLayers
        }
        return converted
    }

    private static func resolvedConverterType(for node: FigNode) -> String {
        if node.type == "FRAME" || node.type == "SECTION" {
            if !node.resizeToFit || hasAutoLayout(node) {
                return "FRAME_CONTAINER"
            }
            return "GROUP_CONTAINER"
        }
        return node.type
    }

    static func hasAutoLayout(_ node: FigNode) -> Bool {
        guard let stackMode = node.stackMode else { return false }
        return !stackMode.isEmpty
    }

    private static func orderedChildren(in node: FigTreeNode) -> [FigTreeNode] {
        node.children
    }

    private static func frameForNode(
        _ node: FigNode
    ) throws -> NodeFrame {
        let x = node.x ?? 0
        let y = node.y ?? 0
        guard x.isFinite, y.isFinite else {
            throw FigTreeToDocumentMapperError.invalidPositioning(node.guid)
        }

        if let width = node.width, !width.isFinite {
            throw FigTreeToDocumentMapperError.invalidPositioning(node.guid)
        }
        if let height = node.height, !height.isFinite {
            throw FigTreeToDocumentMapperError.invalidPositioning(node.guid)
        }

        return NodeFrame(
            x: x,
            y: y,
            width: node.width.map(clampedSketchDimension),
            height: node.height.map(clampedSketchDimension),
            rotation: try rotationForNode(node)
        )
    }

    private static func clampedSketchDimension(_ value: Double) -> Double {
        value == 0 ? 0.1 : value
    }

    fileprivate static func convertRectangleNode(
        node: FigNode,
        frame: NodeFrame,
        context: MappingContext
    ) throws -> [ConversionLayer] {
        guard let width = frame.width, let height = frame.height else { return [] }
        let style = effectiveStyle(for: node, context: context)
        return rectangleOrCroppedImageGroup(
            for: node,
            effectiveStyle: style,
            x: frame.x,
            y: frame.y,
            width: width,
            height: height,
            rotation: frame.rotation
        )
    }

    private static func rotationForNode(_ node: FigNode) throws -> Double {
        let rotation = nodeTransformSemantics(node.transform).rotation
        guard rotation.isFinite else {
            throw FigTreeToDocumentMapperError.invalidPositioning(node.guid)
        }
        return abs(rotation) <= 0.000_000_1 ? 0 : rotation
    }

    private static func nodeTransformSemantics(_ transform: FigAffineTransform?) -> (
        isFlippedHorizontal: Bool,
        isFlippedVertical: Bool,
        rotation: Double
    ) {
        guard let transform else {
            return (false, false, 0)
        }

        var isFlippedHorizontal = false
        var isFlippedVertical: Bool

        if abs(transform.m11) > 0.1 {
            isFlippedVertical = sign(of: transform.m11) != sign(of: transform.m00)
        } else {
            isFlippedVertical = sign(of: transform.m01) == sign(of: transform.m10)
        }

        var rotation = atan2(-transform.m10, transform.m00) * 180 / .pi
        if isFlippedVertical {
            rotation *= -1
        }

        if (90 < abs(rotation) && abs(rotation) < 179) || (abs(rotation) > 179 && isFlippedVertical) {
            isFlippedHorizontal.toggle()
            isFlippedVertical.toggle()
            rotation = (rotation + 180).truncatingRemainder(dividingBy: 360)
        }

        return (isFlippedHorizontal, isFlippedVertical, rotation)
    }

    private static func sign(of value: Double) -> Double {
        value.sign == .minus ? -1 : 1
    }


}
