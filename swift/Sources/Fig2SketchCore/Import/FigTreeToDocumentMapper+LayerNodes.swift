import FigFormat
import Foundation

extension FigTreeToDocumentMapper {
    static func convertTextNode(
        node: FigNode,
        frame: NodeFrame,
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        guard let width = frame.width, let height = frame.height else { return [] }
        let effectiveFigStyle = effectiveStyle(for: node, context: context)
        var style = effectiveFigStyle.map(mapRenderableStyle)
        let textStyle = effectiveTextStyle(for: node, context: context)
        let characters = node.textCharacters ?? ""
        let baseFontName = resolvedFontName(for: textStyle)
        let baseFontSize = textStyle.size ?? 12
        let baseColor = textColor(from: effectiveFigStyle?.fills ?? []) ?? textBaseColor(style: style)
        let kerning = textKerning(for: node, baseFontSize: baseFontSize)
        let featureSettings = textFeatureSettings(for: node, context: &context)
        let runs = textAttributeRuns(
            for: node,
            characters: characters,
            baseFontName: baseFontName,
            baseFontSize: baseFontSize,
            baseColor: baseColor,
            kerning: kerning,
            featureSettings: featureSettings,
            context: &context
        )

        if hasMultipleRunColors(runs) {
            if style == nil {
                style = ConversionLayerStyle()
            }
            style?.fills = []
        }

        let adjustedWidth: Double
        if node.textAutoResize == "WIDTH_AND_HEIGHT", let kerning {
            adjustedWidth = width + kerning
        } else {
            adjustedWidth = width
        }

        return [.text(
            ConversionText(
                guid: node.guid,
                name: node.name,
                x: frame.x,
                y: frame.y,
                width: adjustedWidth,
                height: height,
                rotation: frame.rotation,
                style: style,
                characters: characters,
                attributeRuns: runs,
                fontFamily: textStyle.family,
                fontStyle: textStyle.style,
                fontSize: textStyle.size,
                warningCodes: context.warnings(for: node.guid)
            )
        )]
    }

    static func convertFrameNode(
        node: FigNode,
        frame: NodeFrame,
        childLayers: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        guard let width = frame.width, let height = frame.height else { return [] }
        let style = effectiveStyle(for: node, context: context).map(mapRenderableStyle)
        let groupLayout = convertGroupLayout(node: node)
        let clippingBehavior: ConversionClippingBehavior = node.frameMaskDisabled ? .none : .default
        let padding = convertPadding(node: node)
        let grid = convertGridAndLayout(node: node, width: width, height: height, context: &context)
        let flow = prototypeFlow(for: node, context: &context)
        let prototypeInfo = prototypeInformation(for: node, context: &context)
        let warningCodes = context.warnings(for: node.guid)

        return [.group(ConversionGroup(
            guid: node.guid,
            name: node.name,
            x: frame.x,
            y: frame.y,
            width: width,
            height: height,
            rotation: frame.rotation,
            layers: childLayers,
            style: style,
            groupLayout: groupLayout,
            clippingBehavior: clippingBehavior,
            topPadding: padding.top,
            rightPadding: padding.right,
            bottomPadding: padding.bottom,
            leftPadding: padding.left,
            paddingSelection: padding.selection,
            grid: grid,
            horizontalSizing: sizingBehaviour(for: node.horizontalConstraint),
            verticalSizing: sizingBehaviour(for: node.verticalConstraint),
            source: .frame,
            flow: flow,
            prototypeInfo: prototypeInfo,
            warningCodes: warningCodes
        ))]
    }

    static func convertGroupContainerNode(
        node: FigNode,
        frame: NodeFrame,
        childLayers: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        guard let width = frame.width, let height = frame.height else { return [] }

        var groupLayers = childLayers
        var style = mapRenderableStyle(effectiveStyle(for: node, context: context) ?? FigLayerStyle())

        let hasFills = style.fills.contains(where: \.isEnabled)
        let hasBorders = style.borders.contains(where: { $0.paint.isEnabled })
        let firstEnabledBlur = style.blurs.first(where: \.isEnabled)
        let hasBackgroundBlur = firstEnabledBlur?.type == .background
        let hasForegroundBlur = firstEnabledBlur?.type == .gaussian

        if hasFills || hasBorders || hasBackgroundBlur {
            var backgroundStyle = ConversionLayerStyle(
                fills: style.fills,
                borders: style.borders,
                blurs: [],
                shadows: style.shadows,
                borderOptions: style.borderOptions,
                miterLimit: style.miterLimit,
                windingRule: style.windingRule,
                corners: style.corners,
                blendMode: style.blendMode,
                blendModeWasExplicit: style.blendModeWasExplicit,
                blendModeNeedsOpacityNudge: style.blendModeNeedsOpacityNudge,
                opacity: style.opacity
            )

            if hasBackgroundBlur, let blur = firstEnabledBlur {
                backgroundStyle.blurs = [
                    ConversionBlur(
                        isEnabled: true,
                        radius: blur.radius,
                        type: .background
                    )
                ]
            }

            let backgroundLayer = ConversionShapePath(
                guid: derivedGUID(node.guid, extra: [9, 0]),
                name: "Frame Background",
                x: frame.x,
                y: frame.y,
                width: width,
                height: height,
                style: backgroundStyle
            )
            groupLayers.insert(.shapePath(backgroundLayer), at: 0)

            style.fills = []
            style.borders = []
            style.blurs = []
            style.shadows = style.shadows.filter { !$0.isInnerShadow }
        }

        if hasForegroundBlur, let blur = firstEnabledBlur {
            let blurLayer = ConversionShapePath(
                guid: derivedGUID(node.guid, extra: [9, 1]),
                name: "\(node.name) blur",
                x: frame.x,
                y: frame.y,
                width: width,
                height: height,
                style: ConversionLayerStyle(
                    blurs: [
                        ConversionBlur(
                            isEnabled: true,
                            radius: blur.radius,
                            type: .background
                        )
                    ]
                )
            )
            groupLayers.append(.shapePath(blurLayer))
            style.blurs = []
        }

        let childNodes = context.childNodes(of: node.guid)
        let childHorizontal = childNodes.map { sizingBehaviour(for: $0.horizontalConstraint) }
        let childVertical = childNodes.map { sizingBehaviour(for: $0.verticalConstraint) }
        let horizontalSizing = childHorizontal.first ?? sizingBehaviour(for: node.horizontalConstraint)
        let verticalSizing = childVertical.first ?? sizingBehaviour(for: node.verticalConstraint)
        if !childHorizontal.allSatisfy({ $0 == horizontalSizing }) || !childVertical.allSatisfy({ $0 == verticalSizing }) {
            context.emitWarning("GRP002", nodeGUID: node.guid)
        }

        let warningCodes = context.warnings(for: node.guid)
        return [.group(ConversionGroup(
            guid: node.guid,
            name: node.name,
            x: frame.x,
            y: frame.y,
            width: width,
            height: height,
            rotation: frame.rotation,
            layers: groupLayers,
            style: style,
            groupLayout: .freeform,
            clippingBehavior: node.frameMaskDisabled ? .none : .default,
            horizontalSizing: horizontalSizing,
            verticalSizing: verticalSizing,
            warningCodes: warningCodes
        ))]
    }

    static func convertSymbolNode(
        node: FigNode,
        frame: NodeFrame,
        childLayers: [ConversionLayer],
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        guard let width = frame.width, let height = frame.height else { return [] }
        let style = effectiveStyle(for: node, context: context).map(mapRenderableStyle)
        let masterName = symbolDisplayName(for: node, context: context)
        let groupLayout = convertGroupLayout(node: node)
        let clippingBehavior: ConversionClippingBehavior = node.frameMaskDisabled ? .none : .default
        let padding = convertPadding(node: node)
        let grid = convertGridAndLayout(node: node, width: width, height: height, context: &context)
        let flow = prototypeFlow(for: node, context: &context)
        let prototypeInfo = prototypeInformation(for: node, context: &context)
        let warningCodes = context.warnings(for: node.guid)

        let master = ConversionSymbolMaster(
            guid: node.guid,
            name: masterName,
            x: frame.x,
            y: frame.y,
            width: width,
            height: height,
            rotation: frame.rotation,
            groupLayout: groupLayout,
            clippingBehavior: clippingBehavior,
            topPadding: padding.top,
            rightPadding: padding.right,
            bottomPadding: padding.bottom,
            leftPadding: padding.left,
            paddingSelection: padding.selection,
            grid: grid,
            horizontalSizing: sizingBehaviour(for: node.horizontalConstraint),
            verticalSizing: sizingBehaviour(for: node.verticalConstraint),
            flow: flow,
            prototypeInfo: prototypeInfo,
            symbolIDGUID: node.guid,
            layers: childLayers,
            style: style,
            warningCodes: warningCodes
        )
        context.registerSymbolMaster(master)

        return [.symbolInstance(ConversionSymbolInstance(
            guid: derivedGUID(node.guid, extra: [8, 0]),
            name: node.name,
            x: frame.x,
            y: frame.y,
            width: width,
            height: height,
            rotation: frame.rotation,
            horizontalSizing: sizingBehaviour(for: node.horizontalConstraint),
            verticalSizing: sizingBehaviour(for: node.verticalConstraint),
            symbolIDGUID: node.guid,
            overrideValues: [],
            style: ConversionLayerStyle(),
            warningCodes: warningCodes
        ))]
    }

    static func convertInstanceNode(
        node: FigNode,
        frame: NodeFrame,
        context: inout MappingContext
    ) throws -> [ConversionLayer] {
        guard let width = frame.width, let height = frame.height else { return [] }
        guard let symbolData = node.symbolData else {
            return [groupFallbackLayer(for: node, frame: frame, context: context)]
        }
        guard !isInvalidRef(symbolData.symbolID) else {
            context.emitWarning("SYM001", nodeGUID: node.guid)
            return [groupFallbackLayer(for: node, frame: frame, context: context)]
        }
        guard let master = context.symbolMaster(for: symbolData.symbolID) else {
            context.emitWarning("SYM001", nodeGUID: node.guid)
            return [groupFallbackLayer(for: node, frame: frame, context: context)]
        }

        var allOverrides = symbolData.symbolOverrides.map(normalizedOverride(from:))
        let assignmentOverrides = propertyOverrides(
            assignments: node.componentPropAssignments,
            symbolMasterGUID: symbolData.symbolID,
            context: context
        )
        allOverrides = mergedOverrides(assignmentOverrides + allOverrides)

        var convertedOverrides: [ConversionSymbolOverrideValue] = []
        var unsupportedProps: Set<String> = []
        var detachedFillOverrides: [NormalizedSymbolOverride] = []

        for override in allOverrides {
            guard override.guidPath.allSatisfy({ context.node(for: $0) != nil }) else {
                context.emitWarning("SYM004", nodeGUID: node.guid)
                continue
            }
            let resolvedGuidPath = override.guidPath.compactMap { context.node(for: $0)?.guid }
            guard resolvedGuidPath.count == override.guidPath.count else {
                context.emitWarning("SYM004", nodeGUID: node.guid)
                continue
            }

            if let textCharacters = override.textCharacters {
                convertedOverrides.append(ConversionSymbolOverrideValue(
                    guidPath: resolvedGuidPath,
                    kind: .stringValue,
                    stringValue: textCharacters
                ))
            }
            if let overriddenSymbolID = override.overriddenSymbolID {
                let resolvedSymbolID = context.node(for: overriddenSymbolID)?.guid ?? overriddenSymbolID
                convertedOverrides.append(ConversionSymbolOverrideValue(
                    guidPath: resolvedGuidPath,
                    kind: .symbolID,
                    guidValue: resolvedSymbolID
                ))
            }

            if override.hasFillPaints {
                unsupportedProps.insert("fillPaints")
                var detachedOverride = override
                detachedOverride.guidPath = resolvedGuidPath
                detachedFillOverrides.append(detachedOverride)
            }
            for prop in override.unsupportedProperties {
                unsupportedProps.insert(prop)
            }
        }

        if !unsupportedProps.isEmpty {
            if context.options.detachUnsupportedInstanceOverrides {
                context.emitWarning("SYM003", nodeGUID: node.guid)
                return [detachedLayer(
                    from: node,
                    frame: frame,
                    symbolMaster: master,
                    fillOverrides: detachedFillOverrides,
                    context: &context
                )]
            }
            context.emitWarning("SYM002", nodeGUID: node.guid)
        }

        return [.symbolInstance(ConversionSymbolInstance(
            guid: node.guid,
            name: node.name,
            x: frame.x,
            y: frame.y,
            width: width,
            height: height,
            rotation: frame.rotation,
            horizontalSizing: sizingBehaviour(for: node.horizontalConstraint),
            verticalSizing: sizingBehaviour(for: node.verticalConstraint),
            symbolIDGUID: symbolData.symbolID,
            overrideValues: convertedOverrides,
            style: ConversionLayerStyle(),
            warningCodes: context.warnings(for: node.guid)
        ))]
    }

    struct NormalizedSymbolOverride {
        var guidPath: [[UInt32]]
        var textCharacters: String?
        var overriddenSymbolID: [UInt32]?
        var fillPaints: [FigPaint]
        var hasFillPaints: Bool
        var unsupportedProperties: [String]
    }

    static func normalizedOverride(from override: FigSymbolOverride) -> NormalizedSymbolOverride {
        NormalizedSymbolOverride(
            guidPath: override.guidPath,
            textCharacters: override.textCharacters,
            overriddenSymbolID: override.overriddenSymbolID,
            fillPaints: override.fillPaints,
            hasFillPaints: override.hasFillPaints,
            unsupportedProperties: override.unsupportedProperties
        )
    }

    static func mergedOverrides(_ overrides: [NormalizedSymbolOverride]) -> [NormalizedSymbolOverride] {
        var merged: [NormalizedSymbolOverride] = []
        for override in overrides.sorted(by: { $0.guidPath.count < $1.guidPath.count }) {
            if let index = merged.firstIndex(where: { $0.guidPath == override.guidPath }) {
                if merged[index].textCharacters == nil {
                    merged[index].textCharacters = override.textCharacters
                }
                if merged[index].overriddenSymbolID == nil {
                    merged[index].overriddenSymbolID = override.overriddenSymbolID
                }
                if merged[index].fillPaints.isEmpty {
                    merged[index].fillPaints = override.fillPaints
                }
                if override.hasFillPaints {
                    merged[index].hasFillPaints = true
                }
                for prop in override.unsupportedProperties where !merged[index].unsupportedProperties.contains(prop) {
                    merged[index].unsupportedProperties.append(prop)
                }
            } else {
                merged.append(override)
            }
        }
        return merged
    }

    static func propertyOverrides(
        assignments: [FigComponentPropAssignment],
        symbolMasterGUID: [UInt32],
        context: MappingContext
    ) -> [NormalizedSymbolOverride] {
        guard let symbolMaster = context.node(for: symbolMasterGUID) else { return [] }
        var overrides: [NormalizedSymbolOverride] = []

        for assignment in assignments {
            let refs = componentPropRefTargets(in: symbolMaster.guid, defID: assignment.defID, context: context)
            for ref in refs {
                if let textCharacters = assignment.textCharacters {
                    overrides.append(NormalizedSymbolOverride(
                        guidPath: [ref],
                        textCharacters: textCharacters,
                        overriddenSymbolID: nil,
                        fillPaints: [],
                        hasFillPaints: false,
                        unsupportedProperties: []
                    ))
                } else if let guidValue = assignment.guidValue {
                    overrides.append(NormalizedSymbolOverride(
                        guidPath: [ref],
                        textCharacters: nil,
                        overriddenSymbolID: guidValue,
                        fillPaints: [],
                        hasFillPaints: false,
                        unsupportedProperties: []
                    ))
                } else if assignment.boolValue != nil {
                    overrides.append(NormalizedSymbolOverride(
                        guidPath: [ref],
                        textCharacters: nil,
                        overriddenSymbolID: nil,
                        fillPaints: [],
                        hasFillPaints: false,
                        unsupportedProperties: ["visible"]
                    ))
                }
            }
        }

        return overrides
    }

    static func componentPropRefTargets(
        in rootGUID: [UInt32],
        defID: [UInt32],
        context: MappingContext
    ) -> [[UInt32]] {
        guard let node = context.node(for: rootGUID) else { return [] }
        var refs: [[UInt32]] = []
        for ref in node.componentPropRefs where !ref.isDeleted && ref.defID == defID {
            refs.append(node.overrideKey ?? node.guid)
        }
        for child in context.childNodes(of: rootGUID) {
            refs.append(contentsOf: componentPropRefTargets(in: child.guid, defID: defID, context: context))
        }
        return refs
    }

    static func detachedLayer(
        from instanceNode: FigNode,
        frame: NodeFrame,
        symbolMaster: ConversionSymbolMaster,
        fillOverrides: [NormalizedSymbolOverride],
        context: inout MappingContext
    ) -> ConversionLayer {
        var layers = symbolMaster.layers
        for fillOverride in fillOverrides {
            applyFillOverride(
                paints: fillOverride.fillPaints,
                guidPath: fillOverride.guidPath,
                layers: &layers
            )
        }

        let width = frame.width ?? symbolMaster.width
        let height = frame.height ?? symbolMaster.height
        let style = effectiveStyle(for: instanceNode, context: context).map(mapRenderableStyle)
        let groupLayout = convertGroupLayout(node: instanceNode)
        let padding = convertPadding(node: instanceNode)
        let grid = convertGridAndLayout(node: instanceNode, width: width, height: height, context: &context)
        let flow = prototypeFlow(for: instanceNode, context: &context)
        let prototypeInfo = prototypeInformation(for: instanceNode, context: &context)

        return .group(ConversionGroup(
            guid: instanceNode.guid,
            name: instanceNode.name,
            x: frame.x,
            y: frame.y,
            width: width,
            height: height,
            rotation: frame.rotation,
            layers: layers,
            style: style,
            groupLayout: groupLayout,
            clippingBehavior: instanceNode.frameMaskDisabled ? .none : .default,
            topPadding: padding.top,
            rightPadding: padding.right,
            bottomPadding: padding.bottom,
            leftPadding: padding.left,
            paddingSelection: padding.selection,
            grid: grid,
            horizontalSizing: sizingBehaviour(for: instanceNode.horizontalConstraint),
            verticalSizing: sizingBehaviour(for: instanceNode.verticalConstraint),
            source: .frame,
            flow: flow,
            prototypeInfo: prototypeInfo,
            warningCodes: context.warnings(for: instanceNode.guid)
        ))
    }

    static func applyFillOverride(
        paints: [FigPaint],
        guidPath: [[UInt32]],
        layers: inout [ConversionLayer]
    ) {
        guard let targetGUID = guidPath.last else { return }
        let fills = paints.map(mapPaint)
        guard !fills.isEmpty else { return }
        for index in layers.indices {
            if applyFillOverride(to: &layers[index], targetGUID: targetGUID, fills: fills) {
                return
            }
        }
    }

    static func applyFillOverride(
        to layer: inout ConversionLayer,
        targetGUID: [UInt32],
        fills: [ConversionPaint]
    ) -> Bool {
        switch layer {
        case .rectangle(var rect):
            guard rect.guid == targetGUID else { return false }
            if var style = rect.style {
                style.fills = fills
                rect.style = style
            } else {
                rect.style = ConversionLayerStyle(fills: fills)
            }
            layer = .rectangle(rect)
            return true
        case .text(var text):
            guard text.guid == targetGUID else { return false }
            if var style = text.style {
                style.fills = fills
                text.style = style
            } else {
                text.style = ConversionLayerStyle(fills: fills)
            }
            layer = .text(text)
            return true
        case .group(var group):
            if group.guid == targetGUID {
                if var style = group.style {
                    style.fills = fills
                    group.style = style
                } else {
                    group.style = ConversionLayerStyle(fills: fills)
                }
                layer = .group(group)
                return true
            }
            for idx in group.layers.indices {
                if applyFillOverride(to: &group.layers[idx], targetGUID: targetGUID, fills: fills) {
                    layer = .group(group)
                    return true
                }
            }
            return false
        case .artboard(var artboard):
            if artboard.guid == targetGUID {
                if var style = artboard.style {
                    style.fills = fills
                    artboard.style = style
                } else {
                    artboard.style = ConversionLayerStyle(fills: fills)
                }
                layer = .artboard(artboard)
                return true
            }
            for idx in artboard.layers.indices {
                if applyFillOverride(to: &artboard.layers[idx], targetGUID: targetGUID, fills: fills) {
                    layer = .artboard(artboard)
                    return true
                }
            }
            return false
        case .symbolMaster(var master):
            if master.guid == targetGUID {
                if var style = master.style {
                    style.fills = fills
                    master.style = style
                } else {
                    master.style = ConversionLayerStyle(fills: fills)
                }
                layer = .symbolMaster(master)
                return true
            }
            for idx in master.layers.indices {
                if applyFillOverride(to: &master.layers[idx], targetGUID: targetGUID, fills: fills) {
                    layer = .symbolMaster(master)
                    return true
                }
            }
            return false
        case .shapePath(var shapePath):
            guard shapePath.guid == targetGUID else { return false }
            if var style = shapePath.style {
                style.fills = fills
                shapePath.style = style
            } else {
                shapePath.style = ConversionLayerStyle(fills: fills)
            }
            layer = .shapePath(shapePath)
            return true
        case .symbolInstance:
            return false
        }
    }

    static func isInvalidRef(_ ref: [UInt32]) -> Bool {
        ref.first == UInt32.max
    }

    static func groupFallbackLayer(
        for node: FigNode,
        frame: NodeFrame,
        context: MappingContext
    ) -> ConversionLayer {
        .group(ConversionGroup(
            guid: node.guid,
            name: node.name,
            x: frame.x,
            y: frame.y,
            width: frame.width ?? 0.1,
            height: frame.height ?? 0.1,
            rotation: frame.rotation,
            layers: [],
            style: effectiveStyle(for: node, context: context).map(mapRenderableStyle),
            clippingBehavior: node.frameMaskDisabled ? .none : .default,
            horizontalSizing: sizingBehaviour(for: node.horizontalConstraint),
            verticalSizing: sizingBehaviour(for: node.verticalConstraint),
            warningCodes: context.warnings(for: node.guid)
        ))
    }

    static func symbolDisplayName(for symbol: FigNode, context: MappingContext) -> String {
        guard let parentGUID = symbol.parentGuid,
              let parent = context.node(for: parentGUID),
              parent.isStateGroup else {
            return symbol.name
        }
        let propertyValues = symbol.name
            .split(separator: ",")
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .compactMap { part -> String? in
                if let index = part.firstIndex(of: "=") {
                    return String(part[part.index(after: index)...]).trimmingCharacters(in: .whitespaces)
                }
                return part.isEmpty ? nil : part
            }
        if propertyValues.isEmpty {
            return parent.name
        }
        return ([parent.name] + propertyValues).joined(separator: "/")
    }

}
