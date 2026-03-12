import FigFormat
import Foundation

extension FigTreeToDocumentMapper {
    struct ConvertedPadding {
        var top: Double
        var right: Double
        var bottom: Double
        var left: Double
        var selection: ConversionPaddingSelection
    }

    static func convertPadding(node: FigNode) -> ConvertedPadding {
        guard hasAutoLayout(node) else {
            return ConvertedPadding(top: 0, right: 0, bottom: 0, left: 0, selection: .paired)
        }

        let top = node.stackVerticalPadding ?? 0
        let right = node.stackPaddingRight ?? 0
        let bottom = node.stackPaddingBottom ?? 0
        let left = node.stackHorizontalPadding ?? 0
        let isAsymmetrical = top != bottom || left != right
        return ConvertedPadding(
            top: top,
            right: right,
            bottom: bottom,
            left: left,
            selection: isAsymmetrical ? .individual : .paired
        )
    }

    static func convertGroupLayout(node: FigNode) -> ConversionGroupLayout {
        guard hasAutoLayout(node) else {
            return .freeform
        }

        let isVertical = node.stackMode == "VERTICAL"
        let flexDirection = isVertical ? 1 : 0
        let justify = mapJustify(node.stackPrimaryAlignItems ?? "MIN")
        let align = mapAlign(node.stackCounterAlignItems ?? "MIN")
        return .inferred(
            flexDirection: flexDirection,
            justifyContent: justify,
            alignItems: align,
            allGuttersGap: node.stackSpacing ?? 0
        )
    }

    private static func mapJustify(_ value: String) -> Int {
        switch value {
        case "CENTER":
            return 1
        case "MAX":
            return 2
        case "SPACE_EVENLY":
            return 3
        default:
            return 0
        }
    }

    private static func mapAlign(_ value: String) -> Int {
        switch value {
        case "CENTER":
            return 1
        case "MAX":
            return 2
        default:
            return 0
        }
    }

    static func sizingBehaviour(for constraint: String?) -> Int {
        guard let constraint else { return 1 }
        return constraint == "SCALE" ? 1 : 0
    }

    static func prototypeFlow(
        for node: FigNode,
        context: inout MappingContext
    ) -> ConversionFlowConnection? {
        var flow: ConversionFlowConnection?

        for interaction in node.prototypeInteractions {
            if interaction.isDeleted {
                continue
            }

            guard let interactionType = interaction.interactionType else {
                continue
            }

            guard interactionType == "ON_CLICK" else {
                context.emitWarning("PRT001", nodeGUID: node.guid)
                continue
            }

            for action in interaction.actions {
                if flow != nil {
                    context.emitWarning("PRT002", nodeGUID: node.guid)
                    continue
                }

                if action.isEmpty {
                    continue
                }

                let navigationType = action.navigationType ?? "NAVIGATE"
                if navigationType != "NAVIGATE" && navigationType != "SCROLL" && navigationType != "OVERLAY" {
                    context.emitWarning("PRT003", nodeGUID: node.guid)
                    continue
                }

                switch destinationSettings(for: action, context: context) {
                case .none:
                    continue
                case .invalidConnectionType:
                    context.emitWarning("PRT004", nodeGUID: node.guid)
                    continue
                case .resolved(let destination, let overlaySettings):
                    flow = ConversionFlowConnection(
                        destination: destination,
                        overlaySettings: overlaySettings,
                        animationType: prototypeAnimationType(for: action.transitionType),
                        maintainScrollPosition: action.transitionPreserveScroll,
                        shouldCloseExistingOverlays: false
                    )
                }
            }
        }

        return flow
    }

    static func prototypeInformation(
        for frameNode: FigNode,
        context: inout MappingContext
    ) -> ConversionPrototypeInfo {
        guard let canvas = prototypeCanvas(for: frameNode, context: context),
              let prototypeDevice = canvas.prototypeDevice else {
            return ConversionPrototypeInfo(
                isFlowHome: false,
                overlayBackgroundInteraction: 0,
                presentationStyle: 0
            )
        }

        if (frameNode.scrollDirection ?? "NONE") != "NONE" {
            context.emitWarning("PRT005", nodeGUID: frameNode.guid)
        }

        if let overlayBackgroundInteraction = frameNode.overlayBackgroundInteraction {
            return ConversionPrototypeInfo(
                isFlowHome: false,
                overlayBackgroundInteraction: overlayBackgroundInteractionValue(overlayBackgroundInteraction),
                presentationStyle: 1,
                overlaySettings: positionedOverlaySettings(
                    positionType: frameNode.overlayPositionType ?? "CENTER"
                )
            )
        }

        return ConversionPrototypeInfo(
            isFlowHome: !(frameNode.prototypeStartingPointName ?? "").isEmpty,
            overlayBackgroundInteraction: 0,
            presentationStyle: 0,
            overlaySettings: regularArtboardOverlaySettings(),
            prototypeViewport: ConversionPrototypeViewport(
                name: prototypeDevice.presetIdentifier,
                size: ConversionPoint(
                    x: prototypeDevice.size.x,
                    y: prototypeDevice.size.y
                )
            )
        )
    }

    private enum DestinationSettingsResult {
        case none
        case invalidConnectionType
        case resolved(ConversionFlowDestination, ConversionFlowOverlaySettings?)
    }

    private static func destinationSettings(
        for action: FigPrototypeAction,
        context: MappingContext
    ) -> DestinationSettingsResult {
        let connectionType = action.connectionType
        let transitionNodeID = action.transitionNodeID

        if connectionType == "BACK" {
            return .resolved(.back, nil)
        }

        if connectionType == "INTERNAL_NODE" {
            guard let transitionNodeID else {
                return .none
            }
            if isInvalidRef(transitionNodeID) {
                return .none
            }

            var overlaySettings: ConversionFlowOverlaySettings?
            if let transitionNode = context.node(for: transitionNodeID),
               transitionNode.overlayBackgroundInteraction != nil {
                let offset = action.overlayRelativePosition.map {
                    ConversionPoint(x: $0.x, y: $0.y)
                } ?? ConversionPoint(x: 0, y: 0)
                overlaySettings = positionedOverlaySettings(
                    positionType: transitionNode.overlayPositionType ?? "CENTER",
                    offset: offset
                )
            }

            return .resolved(.node(transitionNodeID), overlaySettings)
        }

        if connectionType == "NONE" {
            return .none
        }

        return .invalidConnectionType
    }

    private static func prototypeCanvas(for node: FigNode, context: MappingContext) -> FigNode? {
        var currentParent = node.parentGuid
        while let parentGUID = currentParent,
              let parentNode = context.node(for: parentGUID) {
            if parentNode.type == "CANVAS" {
                return parentNode
            }
            currentParent = parentNode.parentGuid
        }
        return nil
    }

    private static func prototypeAnimationType(for transitionType: String?) -> Int {
        switch transitionType ?? "INSTANT_TRANSITION" {
        case "SLIDE_FROM_BOTTOM", "PUSH_FROM_BOTTOM", "MOVE_FROM_BOTTOM", "SLIDE_OUT_TO_BOTTOM", "MOVE_OUT_TO_BOTTOM":
            return 2
        case "SLIDE_FROM_TOP", "PUSH_FROM_TOP", "MOVE_FROM_TOP", "SLIDE_OUT_TO_TOP", "MOVE_OUT_TO_TOP":
            return 3
        case "SLIDE_FROM_RIGHT", "PUSH_FROM_RIGHT", "MOVE_FROM_RIGHT", "SLIDE_OUT_TO_RIGHT", "MOVE_OUT_TO_RIGHT":
            return 4
        case "SLIDE_FROM_LEFT", "PUSH_FROM_LEFT", "MOVE_FROM_LEFT", "SLIDE_OUT_TO_LEFT", "MOVE_OUT_TO_LEFT":
            return 5
        case "INSTANT_TRANSITION", "MAGIC_MOVE", "SMART_ANIMATE", "SCROLL_ANIMATE", "DISSOLVE":
            return 0
        default:
            return 0
        }
    }

    private static func overlayBackgroundInteractionValue(_ value: String) -> Int {
        switch value {
        case "CLOSE_ON_CLICK_OUTSIDE":
            return 1
        default:
            return 0
        }
    }

    private static func regularArtboardOverlaySettings() -> ConversionFlowOverlaySettings {
        let anchor = ConversionPoint(x: 0.5, y: 0.5)
        return ConversionFlowOverlaySettings(
            overlayAnchor: anchor,
            sourceAnchor: anchor,
            offset: ConversionPoint(x: 0, y: 0),
            overlayType: 0
        )
    }

    private static func positionedOverlaySettings(
        positionType: String,
        offset: ConversionPoint = ConversionPoint(x: 0, y: 0)
    ) -> ConversionFlowOverlaySettings {
        let anchor = overlayAnchor(for: positionType)
        return ConversionFlowOverlaySettings(
            overlayAnchor: anchor,
            sourceAnchor: anchor,
            offset: offset,
            overlayType: 0
        )
    }

    private static func overlayAnchor(for positionType: String) -> ConversionPoint {
        switch positionType {
        case "TOP_LEFT":
            return ConversionPoint(x: 0, y: 0)
        case "TOP_CENTER":
            return ConversionPoint(x: 0.5, y: 0)
        case "TOP_RIGHT":
            return ConversionPoint(x: 1, y: 0)
        case "BOTTOM_LEFT":
            return ConversionPoint(x: 0, y: 1)
        case "BOTTOM_CENTER":
            return ConversionPoint(x: 0.5, y: 1)
        case "BOTTOM_RIGHT":
            return ConversionPoint(x: 1, y: 1)
        case "MANUAL":
            return ConversionPoint(x: 0, y: 0)
        default:
            return ConversionPoint(x: 0.5, y: 0.5)
        }
    }

    static func convertGridAndLayout(
        node: FigNode,
        width: Double,
        height: Double,
        context: inout MappingContext
    ) -> ConversionLayoutGrid? {
        let grids = node.layoutGrids.filter { $0.pattern == "GRID" }.sorted { $0.sectionSize < $1.sectionSize }
        var gridSize: Double?
        var thickGridTimes: Double?

        if let primary = grids.first {
            gridSize = primary.sectionSize
            var secondary: Double?
            for grid in grids.dropFirst() {
                if grid.sectionSize.truncatingRemainder(dividingBy: primary.sectionSize) == 0 {
                    if secondary != nil {
                        context.emitWarning("GRD003", nodeGUID: node.guid)
                    } else {
                        secondary = grid.sectionSize
                    }
                } else {
                    context.emitWarning("GRD002", nodeGUID: node.guid)
                }
            }
            thickGridTimes = secondary.map { $0 / primary.sectionSize } ?? 0
        }

        let layouts = node.layoutGrids.filter { $0.pattern == "STRIPES" }
        let columns = layouts.filter { $0.axis == "X" }
        let rows = layouts.filter { $0.axis == "Y" }

        if columns.count > 1 || rows.count > 1 {
            context.emitWarning("GRD004", nodeGUID: node.guid)
        }

        var drawVertical = false
        var totalWidth: Double?
        var gutterWidth: Double?
        var columnWidth: Double?
        var numberOfColumns: Double?
        var horizontalOffset: Double?

        if let column = columns.first {
            let columnSizeBasis = column.type == "STRETCH" ? height : width
            let sizes = calculateLayout(column, size: columnSizeBasis)
            drawVertical = true
            totalWidth = sizes.size
            gutterWidth = column.gutterSize
            columnWidth = sizes.itemSize
            numberOfColumns = sizes.itemCount
            horizontalOffset = sizes.offset
        }

        var drawHorizontal = false
        var gutterHeight: Double?
        var rowHeightMultiplication: Double?
        if let row = rows.first {
            let sizes = calculateLayout(row, size: height)
            if sizes.size != height {
                context.emitWarning("GRD005", nodeGUID: node.guid)
            }
            if sizes.offset != 0 {
                context.emitWarning("GRD006", nodeGUID: node.guid)
            }

            var gutter = row.gutterSize
            if gutter <= 0 {
                context.emitWarning("GRD007", nodeGUID: node.guid)
                gutter = 1
            }
            let rowScale = sizes.itemSize / gutter
            let roundedScale = rowScale.rounded()
            if abs(rowScale - roundedScale) > 0.01 {
                context.emitWarning("GRD007", nodeGUID: node.guid)
            } else {
                drawHorizontal = true
                gutterHeight = gutter
                rowHeightMultiplication = roundedScale
                if drawVertical {
                    context.emitWarning("GRD007", nodeGUID: node.guid)
                } else {
                    totalWidth = width
                }
            }
        }

        if gridSize == nil && !drawVertical && !drawHorizontal {
            return nil
        }

        return ConversionLayoutGrid(
            isEnabled: true,
            gridSize: gridSize,
            thickGridTimes: thickGridTimes,
            drawVertical: drawVertical,
            totalWidth: totalWidth,
            gutterWidth: gutterWidth,
            columnWidth: columnWidth,
            numberOfColumns: numberOfColumns,
            horizontalOffset: horizontalOffset,
            drawHorizontal: drawHorizontal,
            gutterHeight: gutterHeight,
            rowHeightMultiplication: rowHeightMultiplication
        )
    }

    private struct LayoutSizes {
        var size: Double
        var offset: Double
        var itemCount: Double
        var itemSize: Double
    }

    private static func calculateLayout(_ layout: FigLayoutGrid, size: Double) -> LayoutSizes {
        var itemCount = layout.numSections
        let gutter = layout.gutterSize
        var itemSize = layout.sectionSize
        var offset = layout.offset
        let layoutSize: Double

        if layout.type == "STRETCH" {
            if itemCount == 2_147_483_647 {
                itemCount = 1
            }
            let totalGutter = (itemCount - 1) * gutter
            itemSize = (size - totalGutter - (2 * offset)) / itemCount
            if itemSize < 0 { itemSize = 0 }
            layoutSize = size
        } else {
            if itemCount == 2_147_483_647 {
                itemCount = ceil(size / itemSize)
            }

            layoutSize = (itemSize * itemCount) + (gutter * (itemCount - 1))
            if layout.type == "MAX" {
                offset = size - layoutSize
            } else if layout.type == "CENTER" {
                offset = (size - layoutSize) / 2
            }
        }

        return LayoutSizes(size: layoutSize, offset: offset, itemCount: itemCount, itemSize: itemSize)
    }

}
