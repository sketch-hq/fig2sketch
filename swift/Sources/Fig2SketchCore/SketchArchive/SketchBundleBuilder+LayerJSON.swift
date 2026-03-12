import Foundation

extension SketchBundleBuilder {
    static func layerJSON(_ layer: ConversionLayer, salt: Data, imageRefs: [String: String]) -> SketchJSONValue {
        switch layer {
        case .rectangle(let rect):
            let objectID = ConverterUtils.genObjectID(figID: rect.guid, salt: salt)
            let styleID = ConverterUtils.genObjectID(figID: rect.guid, salt: salt, suffix: Data("style".utf8))
            let styleValue = rectangleStyleJSON(rect, styleID: styleID, imageRefs: imageRefs)
            return .object(
                SketchJSONObject([
                    ("_class", .string("rectangle")),
                    ("do_objectID", .string(objectID)),
                    ("name", .string(rect.name)),
                    ("frame", frameJSON(x: rect.x, y: rect.y, width: rect.width, height: rect.height)),
                    ("rotation", rect.rotation == 0 ? nil : .double(rect.rotation)),
                    ("hasClippingMask", rect.hasClippingMask ? .bool(true) : nil),
                    ("clippingMaskMode", rect.hasClippingMask ? .int(rect.clippingMaskMode.rawValue) : nil),
                    ("style", styleValue),
                ])
            )
        case .shapePath(let shape):
            let objectID = ConverterUtils.genObjectID(figID: shape.guid, salt: salt)
            let styleID = ConverterUtils.genObjectID(figID: shape.guid, salt: salt, suffix: Data("style".utf8))
            let styleValue = shape.style.flatMap { groupStyleJSON($0, styleID: styleID, imageRefs: imageRefs) }
            return .object(
                SketchJSONObject([
                    ("_class", .string("shapePath")),
                    ("do_objectID", .string(objectID)),
                    ("name", .string(shape.name)),
                    ("frame", frameJSON(x: shape.x, y: shape.y, width: shape.width, height: shape.height)),
                    ("rotation", shape.rotation == 0 ? nil : .double(shape.rotation)),
                    ("booleanOperation", .int(shape.booleanOperation)),
                    ("isClosed", shape.points.isEmpty ? nil : .bool(shape.isClosed)),
                    ("points", shape.points.isEmpty ? nil : .array(shape.points.map(shapePointJSON))),
                    ("edited", shape.points.isEmpty ? nil : .bool(shape.edited)),
                    ("pointRadiusBehaviour", shape.points.isEmpty ? nil : .int(shape.pointRadiusBehavior.rawValue)),
                    ("style", styleValue),
                    ("f2sWarnings", shape.warningCodes.isEmpty ? nil : .array(shape.warningCodes.map(SketchJSONValue.string))),
                ])
            )
        case .group(let group):
            let objectID = ConverterUtils.genObjectID(figID: group.guid, salt: salt)
            let styleID = ConverterUtils.genObjectID(figID: group.guid, salt: salt, suffix: Data("style".utf8))
            let styleValue = group.style.flatMap { groupStyleJSON($0, styleID: styleID, imageRefs: imageRefs) }
            let prototypeInfo = group.prototypeInfo
            return .object(SketchJSONObject([
                ("_class", .string(group.kind == .shapeGroup ? "shapeGroup" : "group")),
                ("do_objectID", .string(objectID)),
                ("name", .string(group.name)),
                ("frame", frameJSON(x: group.x, y: group.y, width: group.width, height: group.height)),
                ("rotation", group.rotation == 0 ? nil : .double(group.rotation)),
                ("layers", .array(group.layers.map { layerJSON($0, salt: salt, imageRefs: imageRefs) })),
                ("style", styleValue),
                ("groupLayout", groupLayoutJSON(group.groupLayout)),
                ("clippingBehavior", .int(group.clippingBehavior.rawValue)),
                ("windingRule", group.windingRule.map { .int($0.rawValue) }),
                ("topPadding", group.topPadding == 0 ? nil : .double(group.topPadding)),
                ("rightPadding", group.rightPadding == 0 ? nil : .double(group.rightPadding)),
                ("bottomPadding", group.bottomPadding == 0 ? nil : .double(group.bottomPadding)),
                ("leftPadding", group.leftPadding == 0 ? nil : .double(group.leftPadding)),
                ("paddingSelection", .int(group.paddingSelection.rawValue)),
                ("grid", group.grid.map(gridJSON)),
                ("horizontalSizing", .int(group.horizontalSizing)),
                ("verticalSizing", .int(group.verticalSizing)),
                ("flow", group.flow.map { flowConnectionJSON($0, salt: salt) }),
                ("isFlowHome", prototypeInfo.map { .bool($0.isFlowHome) }),
                ("overlayBackgroundInteraction", prototypeInfo.map { .int($0.overlayBackgroundInteraction) }),
                ("presentationStyle", prototypeInfo.map { .int($0.presentationStyle) }),
                ("overlaySettings", prototypeInfo?.overlaySettings.map(flowOverlaySettingsJSON)),
                ("prototypeViewport", prototypeInfo?.prototypeViewport.map(prototypeViewportJSON)),
                ("f2sWarnings", group.warningCodes.isEmpty ? nil : .array(group.warningCodes.map(SketchJSONValue.string))),
            ]))
        case .artboard(let artboard):
            let objectID = ConverterUtils.genObjectID(figID: artboard.guid, salt: salt)
            let styleID = ConverterUtils.genObjectID(figID: artboard.guid, salt: salt, suffix: Data("style".utf8))
            let styleValue = artboard.style.flatMap { groupStyleJSON($0, styleID: styleID, imageRefs: imageRefs) }
            return .object(SketchJSONObject([
                ("_class", .string("artboard")),
                ("do_objectID", .string(objectID)),
                ("name", .string(artboard.name)),
                ("frame", frameJSON(x: artboard.x, y: artboard.y, width: artboard.width, height: artboard.height)),
                ("rotation", artboard.rotation == 0 ? nil : .double(artboard.rotation)),
                ("layers", .array(artboard.layers.map { layerJSON($0, salt: salt, imageRefs: imageRefs) })),
                ("style", styleValue),
                ("f2sWarnings", artboard.warningCodes.isEmpty ? nil : .array(artboard.warningCodes.map(SketchJSONValue.string))),
            ]))
        case .symbolMaster(let master):
            let objectID = ConverterUtils.genObjectID(figID: master.guid, salt: salt, suffix: Data("symbol_master".utf8))
            let symbolID = ConverterUtils.genObjectID(figID: master.symbolIDGUID, salt: salt)
            let styleID = ConverterUtils.genObjectID(figID: master.guid, salt: salt, suffix: Data("symbol_master_style".utf8))
            let styleValue = master.style.flatMap { groupStyleJSON($0, styleID: styleID, imageRefs: imageRefs) }
            let prototypeInfo = master.prototypeInfo
            return .object(SketchJSONObject([
                ("_class", .string("symbolMaster")),
                ("do_objectID", .string(objectID)),
                ("name", .string(master.name)),
                ("symbolID", .string(symbolID)),
                ("allowsOverrides", .bool(true)),
                ("includeBackgroundColorInInstance", .bool(true)),
                ("frame", frameJSON(x: master.x, y: master.y, width: master.width, height: master.height)),
                ("rotation", master.rotation == 0 ? nil : .double(master.rotation)),
                ("layers", .array(master.layers.map { layerJSON($0, salt: salt, imageRefs: imageRefs) })),
                ("style", styleValue),
                ("groupLayout", groupLayoutJSON(master.groupLayout)),
                ("clippingBehavior", .int(master.clippingBehavior.rawValue)),
                ("topPadding", master.topPadding == 0 ? nil : .double(master.topPadding)),
                ("rightPadding", master.rightPadding == 0 ? nil : .double(master.rightPadding)),
                ("bottomPadding", master.bottomPadding == 0 ? nil : .double(master.bottomPadding)),
                ("leftPadding", master.leftPadding == 0 ? nil : .double(master.leftPadding)),
                ("paddingSelection", .int(master.paddingSelection.rawValue)),
                ("grid", master.grid.map(gridJSON)),
                ("horizontalSizing", .int(master.horizontalSizing)),
                ("verticalSizing", .int(master.verticalSizing)),
                ("flow", master.flow.map { flowConnectionJSON($0, salt: salt) }),
                ("isFlowHome", prototypeInfo.map { .bool($0.isFlowHome) }),
                ("overlayBackgroundInteraction", prototypeInfo.map { .int($0.overlayBackgroundInteraction) }),
                ("presentationStyle", prototypeInfo.map { .int($0.presentationStyle) }),
                ("overlaySettings", prototypeInfo?.overlaySettings.map(flowOverlaySettingsJSON)),
                ("prototypeViewport", prototypeInfo?.prototypeViewport.map(prototypeViewportJSON)),
                ("f2sWarnings", master.warningCodes.isEmpty ? nil : .array(master.warningCodes.map(SketchJSONValue.string))),
            ]))
        case .symbolInstance(let instance):
            let objectID = ConverterUtils.genObjectID(figID: instance.guid, salt: salt)
            let styleID = ConverterUtils.genObjectID(figID: instance.guid, salt: salt, suffix: Data("style".utf8))
            let symbolID = ConverterUtils.genObjectID(figID: instance.symbolIDGUID, salt: salt)
            let styleValue = instance.style.flatMap { groupStyleJSON($0, styleID: styleID, imageRefs: imageRefs) }
            let overrideValues = instance.overrideValues.map { overrideValue -> SketchJSONValue in
                let path = overrideValue.guidPath.map { ConverterUtils.genObjectID(figID: $0, salt: salt) }.joined(separator: "/")
                let overrideName: String
                let value: String
                switch overrideValue.kind {
                case .stringValue:
                    overrideName = "\(path)_stringValue"
                    value = overrideValue.stringValue ?? ""
                case .symbolID:
                    overrideName = "\(path)_symbolID"
                    if let guidValue = overrideValue.guidValue {
                        value = ConverterUtils.genObjectID(figID: guidValue, salt: salt)
                    } else {
                        value = ""
                    }
                }
                return .object(SketchJSONObject([
                    ("_class", .string("overrideValue")),
                    ("overrideName", .string(overrideName)),
                    ("value", .string(value)),
                ]))
            }
            return .object(SketchJSONObject([
                ("_class", .string("symbolInstance")),
                ("do_objectID", .string(objectID)),
                ("name", .string(instance.name)),
                ("symbolID", .string(symbolID)),
                ("frame", frameJSON(x: instance.x, y: instance.y, width: instance.width, height: instance.height)),
                ("rotation", instance.rotation == 0 ? nil : .double(instance.rotation)),
                ("horizontalSizing", .int(instance.horizontalSizing)),
                ("verticalSizing", .int(instance.verticalSizing)),
                ("overrideValues", .array(overrideValues)),
                ("style", styleValue),
                ("f2sWarnings", instance.warningCodes.isEmpty ? nil : .array(instance.warningCodes.map(SketchJSONValue.string))),
            ]))
        case .text(let text):
            let objectID = ConverterUtils.genObjectID(figID: text.guid, salt: salt)
            let styleID = ConverterUtils.genObjectID(figID: text.guid, salt: salt, suffix: Data("style".utf8))
            let styleValue = text.style.flatMap { groupStyleJSON($0, styleID: styleID, imageRefs: imageRefs) }
            let attributed = attributedStringJSON(text)
            return .object(SketchJSONObject([
                ("_class", .string("text")),
                ("do_objectID", .string(objectID)),
                ("name", .string(text.name)),
                ("frame", frameJSON(x: text.x, y: text.y, width: text.width, height: text.height)),
                ("rotation", text.rotation == 0 ? nil : .double(text.rotation)),
                ("style", styleValue),
                ("attributedString", attributed),
                ("fontFamily", text.fontFamily.map(SketchJSONValue.string)),
                ("fontStyle", text.fontStyle.map(SketchJSONValue.string)),
                ("fontSize", text.fontSize.map(SketchJSONValue.double)),
                ("f2sWarnings", text.warningCodes.isEmpty ? nil : .array(text.warningCodes.map(SketchJSONValue.string))),
            ]))
        }
    }

    private static func frameJSON(x: Double, y: Double, width: Double, height: Double) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("rect")),
            ("x", .double(x)),
            ("y", .double(y)),
            ("width", .double(width)),
            ("height", .double(height)),
        ]))
    }

    private static func rectangleStyleJSON(
        _ rect: ConversionRectangle,
        styleID: String,
        imageRefs: [String: String]
    ) -> SketchJSONValue? {
        guard let style = rect.style else { return nil }

        let fills = style.fills.compactMap { fillJSON($0, imageRefs: imageRefs) }
        let borders = style.borders.compactMap { borderJSON($0, imageRefs: imageRefs) }
        let blurs = normalizedBlursForSketch(style.blurs).map(blurJSON)
        let shadows = style.shadows.map(shadowJSON)
        let borderOptions = borderOptionsJSON(style.borderOptions)
        let corners = cornersJSON(style.corners)
        let markerFieldsRequired = style.startMarkerType != 0 ||
            style.endMarkerType != 0 ||
            style.startDecorationType != nil ||
            style.endDecorationType != nil
        let layerContextSettings = contextSettingsJSON(
            blendMode: style.blendMode,
            opacity: style.opacity,
            includeOpacityWhenDefaultBlend: true,
            forceNormalOpacityNudge: style.blendModeNeedsOpacityNudge && style.blendMode == .normal && style.opacity == 1
        )

        if fills.isEmpty &&
            borders.isEmpty &&
            blurs.isEmpty &&
            shadows.isEmpty &&
            borderOptions == nil &&
            style.miterLimit == 10 &&
            style.windingRule == .nonZero &&
            !markerFieldsRequired &&
            corners == nil &&
            layerContextSettings == nil {
            return nil
        }

        return .object(SketchJSONObject([
            ("_class", .string("style")),
            ("do_objectID", .string(styleID)),
            ("borderOptions", borderOptions),
            ("fills", fills.isEmpty ? nil : .array(fills)),
            ("borders", borders.isEmpty ? nil : .array(borders)),
            ("miterLimit", style.miterLimit == 10 ? nil : .double(style.miterLimit)),
            ("windingRule", style.windingRule == .nonZero ? nil : .int(style.windingRule.rawValue)),
            ("startMarkerType", markerFieldsRequired ? .int(style.startMarkerType) : nil),
            ("endMarkerType", markerFieldsRequired ? .int(style.endMarkerType) : nil),
            ("startDecorationType", style.startDecorationType.map(SketchJSONValue.int)),
            ("endDecorationType", style.endDecorationType.map(SketchJSONValue.int)),
            ("corners", corners),
            ("blurs", blurs.isEmpty ? nil : .array(blurs)),
            ("shadows", shadows.isEmpty ? nil : .array(shadows)),
            ("contextSettings", layerContextSettings),
        ]))
    }

    private static func groupStyleJSON(
        _ style: ConversionLayerStyle,
        styleID: String,
        imageRefs: [String: String]
    ) -> SketchJSONValue? {
        let fills = style.fills.compactMap { fillJSON($0, imageRefs: imageRefs) }
        let borders = style.borders.compactMap { borderJSON($0, imageRefs: imageRefs) }
        let blurs = normalizedBlursForSketch(style.blurs).map(blurJSON)
        let shadows = style.shadows.map(shadowJSON)
        let borderOptions = borderOptionsJSON(style.borderOptions)
        let corners = cornersJSON(style.corners)
        let markerFieldsRequired = style.startMarkerType != 0 ||
            style.endMarkerType != 0 ||
            style.startDecorationType != nil ||
            style.endDecorationType != nil
        let layerContextSettings = contextSettingsJSON(
            blendMode: style.blendMode,
            opacity: style.opacity,
            includeOpacityWhenDefaultBlend: true,
            forceNormalOpacityNudge: style.blendModeNeedsOpacityNudge && style.blendMode == .normal && style.opacity == 1
        )

        return .object(SketchJSONObject([
            ("_class", .string("style")),
            ("do_objectID", .string(styleID)),
            ("borderOptions", borderOptions),
            ("fills", .array(fills)),
            ("borders", .array(borders)),
            ("miterLimit", style.miterLimit == 10 ? nil : .double(style.miterLimit)),
            ("windingRule", style.windingRule == .nonZero ? nil : .int(style.windingRule.rawValue)),
            ("startMarkerType", markerFieldsRequired ? .int(style.startMarkerType) : nil),
            ("endMarkerType", markerFieldsRequired ? .int(style.endMarkerType) : nil),
            ("startDecorationType", style.startDecorationType.map(SketchJSONValue.int)),
            ("endDecorationType", style.endDecorationType.map(SketchJSONValue.int)),
            ("corners", corners),
            ("blurs", .array(blurs)),
            ("shadows", .array(shadows)),
            ("contextSettings", layerContextSettings),
        ]))
    }

    private static func groupLayoutJSON(_ layout: ConversionGroupLayout) -> SketchJSONValue {
        switch layout {
        case .freeform:
            return .object(SketchJSONObject([
                ("_class", .string("MSImmutableFreeformGroupLayout")),
            ]))
        case .inferred(let flexDirection, let justifyContent, let alignItems, let allGuttersGap):
            return .object(SketchJSONObject([
                ("_class", .string("MSImmutableInferredGroupLayout")),
                ("axis", .int(1)),
                ("layoutAnchor", .int(0)),
                ("minSize", .double(10)),
                ("maxSize", .double(10_000)),
                ("flexDirection", .int(flexDirection)),
                ("justifyContent", .int(justifyContent)),
                ("alignItems", .int(alignItems)),
                ("allGuttersGap", .double(allGuttersGap)),
            ]))
        }
    }

    private static func gridJSON(_ grid: ConversionLayoutGrid) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("layoutGrid")),
            ("isEnabled", .bool(grid.isEnabled)),
            ("gridSize", grid.gridSize.map(SketchJSONValue.double)),
            ("thickGridTimes", grid.thickGridTimes.map(SketchJSONValue.double)),
            ("drawVertical", grid.drawVertical ? .bool(true) : nil),
            ("totalWidth", grid.totalWidth.map(SketchJSONValue.double)),
            ("gutterWidth", grid.gutterWidth.map(SketchJSONValue.double)),
            ("columnWidth", grid.columnWidth.map(SketchJSONValue.double)),
            ("numberOfColumns", grid.numberOfColumns.map(SketchJSONValue.double)),
            ("horizontalOffset", grid.horizontalOffset.map(SketchJSONValue.double)),
            ("drawHorizontal", grid.drawHorizontal ? .bool(true) : nil),
            ("gutterHeight", grid.gutterHeight.map(SketchJSONValue.double)),
            ("rowHeightMultiplication", grid.rowHeightMultiplication.map(SketchJSONValue.double)),
        ]))
    }

    private static func flowConnectionJSON(_ flow: ConversionFlowConnection, salt: Data) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("MSImmutableFlowConnection")),
            ("destinationArtboardID", .string(flowDestinationArtboardID(flow.destination, salt: salt))),
            ("overlaySettings", flow.overlaySettings.map(flowOverlaySettingsJSON)),
            ("animationType", .int(flow.animationType)),
            ("maintainScrollPosition", .bool(flow.maintainScrollPosition)),
            ("shouldCloseExistingOverlays", .bool(flow.shouldCloseExistingOverlays)),
        ]))
    }

    private static func flowDestinationArtboardID(_ destination: ConversionFlowDestination, salt: Data) -> String {
        switch destination {
        case .back:
            return "back"
        case .node(let guid):
            return ConverterUtils.genObjectID(figID: guid, salt: salt)
        }
    }

    private static func flowOverlaySettingsJSON(_ settings: ConversionFlowOverlaySettings) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("MSImmutableFlowOverlaySettings")),
            ("overlayAnchor", .string(prototypePointString(settings.overlayAnchor))),
            ("sourceAnchor", .string(prototypePointString(settings.sourceAnchor))),
            ("offset", .string(prototypePointString(settings.offset))),
            ("overlayType", .int(settings.overlayType)),
        ]))
    }

    private static func prototypeViewportJSON(_ viewport: ConversionPrototypeViewport) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("MSImmutablePrototypeViewport")),
            ("name", .string(viewport.name)),
            ("size", .string(prototypePointString(viewport.size))),
        ]))
    }

    private static func prototypePointString(_ point: ConversionPoint) -> String {
        "{\(compactPointNumber(point.x)), \(compactPointNumber(point.y))}"
    }

    private static func compactPointNumber(_ value: Double) -> String {
        var output = String(value)
        if output.contains(".") {
            while output.last == "0" {
                output.removeLast()
            }
            if output.last == "." {
                output.removeLast()
            }
        }
        if output == "-0" {
            return "0"
        }
        return output
    }


}
