import Foundation

extension SketchBundleBuilder {
    static func fillJSON(_ paint: ConversionPaint, imageRefs: [String: String]) -> SketchJSONValue? {
        switch paint.kind {
        case .solid(let color):
            return .object(SketchJSONObject([
                ("_class", .string("fill")),
                ("isEnabled", .bool(paint.isEnabled)),
                ("fillType", .int(0)),
                ("color", colorJSON(color)),
                ("contextSettings", contextSettingsJSON(
                    blendMode: paint.blendMode,
                    opacity: 1,
                    includeOpacityWhenDefaultBlend: false
                )),
            ]))
        case .gradient(let gradient):
            return .object(SketchJSONObject([
                ("_class", .string("fill")),
                ("isEnabled", .bool(paint.isEnabled)),
                ("fillType", .int(1)),
                ("gradient", gradientJSON(gradient)),
                ("contextSettings", contextSettingsJSON(
                    blendMode: paint.blendMode,
                    opacity: paint.opacity,
                    includeOpacityWhenDefaultBlend: true
                )),
            ]))
        case .image(let image):
            guard let refPath = imageRefs[image.sourceName] else { return nil }
            return .object(SketchJSONObject([
                ("_class", .string("fill")),
                ("isEnabled", .bool(paint.isEnabled)),
                ("fillType", .int(4)),
                ("patternFillType", .int(image.patternFillType.rawValue)),
                ("patternTileScale", .double(image.patternTileScale)),
                ("image", .object(SketchJSONObject([
                    ("_class", .string("MSJSONFileReference")),
                    ("_ref_class", .string("MSImageData")),
                    ("_ref", .string(refPath)),
                ]))),
                ("contextSettings", contextSettingsJSON(
                    blendMode: paint.blendMode,
                    opacity: paint.opacity,
                    includeOpacityWhenDefaultBlend: true
                )),
            ]))
        case .unsupported:
            return nil
        }
    }

    static func borderJSON(_ border: ConversionBorder, imageRefs: [String: String]) -> SketchJSONValue? {
        switch border.paint.kind {
        case .solid(let color):
            return .object(SketchJSONObject([
                ("_class", .string("border")),
                ("isEnabled", .bool(border.paint.isEnabled)),
                ("fillType", .int(0)),
                ("position", .int(borderPositionValue(border.position))),
                ("thickness", .double(border.thickness)),
                ("color", colorJSON(color)),
                ("contextSettings", contextSettingsJSON(
                    blendMode: border.paint.blendMode,
                    opacity: 1,
                    includeOpacityWhenDefaultBlend: false
                )),
            ]))
        case .gradient(let gradient):
            return .object(SketchJSONObject([
                ("_class", .string("border")),
                ("isEnabled", .bool(border.paint.isEnabled)),
                ("fillType", .int(1)),
                ("position", .int(borderPositionValue(border.position))),
                ("thickness", .double(border.thickness)),
                ("gradient", gradientJSON(gradient)),
                ("contextSettings", contextSettingsJSON(
                    blendMode: border.paint.blendMode,
                    opacity: border.paint.opacity,
                    includeOpacityWhenDefaultBlend: true
                )),
            ]))
        case .image(let image):
            guard let refPath = imageRefs[image.sourceName] else { return nil }
            return .object(SketchJSONObject([
                ("_class", .string("border")),
                ("isEnabled", .bool(border.paint.isEnabled)),
                ("fillType", .int(4)),
                ("position", .int(borderPositionValue(border.position))),
                ("thickness", .double(border.thickness)),
                ("patternFillType", .int(image.patternFillType.rawValue)),
                ("patternTileScale", .double(image.patternTileScale)),
                ("image", .object(SketchJSONObject([
                    ("_class", .string("MSJSONFileReference")),
                    ("_ref_class", .string("MSImageData")),
                    ("_ref", .string(refPath)),
                ]))),
                ("contextSettings", contextSettingsJSON(
                    blendMode: border.paint.blendMode,
                    opacity: border.paint.opacity,
                    includeOpacityWhenDefaultBlend: true
                )),
            ]))
        case .unsupported:
            return nil
        }
    }

    private static func colorJSON(_ color: ConversionColor) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("color")),
            ("red", colorComponentJSON(color.red)),
            ("green", colorComponentJSON(color.green)),
            ("blue", colorComponentJSON(color.blue)),
            ("alpha", colorComponentJSON(color.alpha)),
        ]))
    }

    private static func colorComponentJSON(_ value: Double) -> SketchJSONValue {
        if value.rounded(.towardZero) == value,
           value >= Double(Int.min),
           value <= Double(Int.max) {
            return .int(Int(value))
        }
        return .double(value)
    }

    private static func gradientJSON(_ gradient: ConversionGradient) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("gradient")),
            ("gradientType", .int(gradient.type.rawValue)),
            ("elipseLength", .double(gradient.ellipseLength)),
            ("from", .string(sketchPointString(gradient.from))),
            ("to", .string(sketchPointString(gradient.to))),
            ("stops", .array(gradient.stops.map(gradientStopJSON))),
        ]))
    }

    private static func gradientStopJSON(_ stop: ConversionGradientStop) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("gradientStop")),
            ("color", colorJSON(stop.color)),
            ("position", .double(stop.position)),
        ]))
    }

    private static func sketchPointString(_ point: ConversionPoint) -> String {
        "{\(point.x), \(point.y)}"
    }

    static func shapePointJSON(_ point: ConversionShapePoint) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("curvePoint")),
            ("curveFrom", .string(sketchPointString(point.curveFrom))),
            ("curveTo", .string(sketchPointString(point.curveTo))),
            ("point", .string(sketchPointString(point.point))),
            ("cornerRadius", .double(point.cornerRadius)),
            ("cornerStyle", .int(point.cornerStyle.rawValue)),
            ("hasCurveFrom", .bool(point.hasCurveFrom)),
            ("hasCurveTo", .bool(point.hasCurveTo)),
            ("curveMode", .int(point.curveMode.rawValue)),
        ]))
    }

    static func attributedStringJSON(_ text: ConversionText) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("attributedString")),
            ("string", .string(text.characters)),
            ("attributes", .array(text.attributeRuns.map(textAttributeRunJSON))),
        ]))
    }

    private static func textAttributeRunJSON(_ run: ConversionTextAttributeRun) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("stringAttribute")),
            ("location", .int(run.location)),
            ("length", .int(run.length)),
            ("attributes", .object(SketchJSONObject([
                ("MSAttributedStringFontAttribute", fontDescriptorJSON(run)),
                ("MSAttributedStringColorAttribute", colorJSON(run.color)),
                ("kerning", run.kerning.map(SketchJSONValue.double)),
            ]))),
        ]))
    }

    private static func fontDescriptorJSON(_ run: ConversionTextAttributeRun) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("fontDescriptor")),
            ("attributes", .object(SketchJSONObject([
                ("name", .string(run.fontName)),
                ("size", .double(run.fontSize)),
                ("featureSettings", run.featureSettings.isEmpty ? nil : .array(run.featureSettings.map(featureSettingJSON))),
            ]))),
        ]))
    }

    private static func featureSettingJSON(_ feature: ConversionTextFeatureSetting) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("CTFeatureSelectorIdentifier", .int(feature.selectorIdentifier)),
            ("CTFeatureTypeIdentifier", .int(feature.typeIdentifier)),
        ]))
    }

    static func blurJSON(_ blur: ConversionBlur) -> SketchJSONValue {
        let progressiveGradient: SketchJSONValue? = ({ () -> SketchJSONValue? in
            guard blur.isProgressive,
                  let from = blur.progressiveFrom,
                  let to = blur.progressiveTo else { return nil }
            let startAlpha = blur.progressiveStartRadiusRatio ?? 0
            return .object(SketchJSONObject([
                ("_class", .string("gradient")),
                ("gradientType", .int(0)),
                ("elipseLength", .double(0)),
                ("from", .string(sketchPointString(from))),
                ("to", .string(sketchPointString(to))),
                ("stops", .array([
                    .object(SketchJSONObject([
                        ("_class", .string("gradientStop")),
                        ("color", colorJSON(.init(red: 0, green: 0, blue: 0, alpha: startAlpha))),
                        ("position", .double(0)),
                    ])),
                    .object(SketchJSONObject([
                        ("_class", .string("gradientStop")),
                        ("color", colorJSON(.init(red: 0, green: 0, blue: 0, alpha: 1))),
                        ("position", .double(1)),
                    ])),
                ])),
            ]))
        })()

        return .object(SketchJSONObject([
            ("_class", .string("blur")),
            ("isEnabled", .bool(blur.isEnabled)),
            ("center", .string("{0.5, 0.5}")),
            ("motionAngle", .double(0)),
            ("radius", .double(blur.radius)),
            ("saturation", .double(1)),
            ("brightness", .double(1)),
            ("type", .int(blur.type.rawValue)),
            ("isProgressive", blur.isProgressive ? .bool(true) : nil),
            ("gradient", progressiveGradient),
            ("isCustomGlass", blur.isCustomGlass ? .bool(true) : nil),
            ("distortion", blur.isCustomGlass ? .double(blur.glassDistortion) : nil),
            ("depth", blur.isCustomGlass ? .double(blur.glassDepth) : nil),
            ("chromaticAberrationMultiplier", blur.isCustomGlass ? .double(blur.glassChromaticAberrationMultiplier) : nil),
        ]))
    }

    static func shadowJSON(_ shadow: ConversionShadow) -> SketchJSONValue {
        .object(SketchJSONObject([
            ("_class", .string("shadow")),
            ("blurRadius", .double(shadow.blurRadius)),
            ("offsetX", .double(shadow.offsetX)),
            ("offsetY", .double(shadow.offsetY)),
            ("spread", .double(shadow.spread)),
            ("isInnerShadow", .bool(shadow.isInnerShadow)),
            ("isEnabled", .bool(shadow.isEnabled)),
            ("color", colorJSON(shadow.color)),
        ]))
    }

    static func borderOptionsJSON(_ options: ConversionBorderOptions) -> SketchJSONValue? {
        guard !options.isDefault else { return nil }
        return .object(SketchJSONObject([
            ("_class", .string("borderOptions")),
            ("isEnabled", .bool(true)),
            ("lineCapStyle", .int(options.lineCapStyle.rawValue)),
            ("lineJoinStyle", .int(options.lineJoinStyle.rawValue)),
            ("dashPattern", options.dashPattern.isEmpty ? nil : .array(options.dashPattern.map(SketchJSONValue.double))),
        ]))
    }

    static func cornersJSON(_ corners: ConversionStyleCorners?) -> SketchJSONValue? {
        guard let corners, !corners.isDefault else { return nil }
        return .object(SketchJSONObject([
            ("_class", .string("MSImmutableStyleCorners")),
            ("radii", .array(corners.radii.map(SketchJSONValue.double))),
            ("style", .int(corners.style.rawValue)),
        ]))
    }

    private static func borderPositionValue(_ position: ConversionBorderPosition) -> Int {
        switch position {
        case .center:
            return 0
        case .inside:
            return 1
        case .outside:
            return 2
        }
    }

    static func normalizedBlursForSketch(_ blurs: [ConversionBlur]) -> [ConversionBlur] {
        guard let first = blurs.first, first.isEnabled else { return blurs }
        // Match Python converter behavior: if the first blur is enabled, subsequent blur effects are skipped.
        return [first]
    }

    static func contextSettingsJSON(
        blendMode: ConversionBlendMode,
        opacity: Double,
        includeOpacityWhenDefaultBlend: Bool,
        forceNormalOpacityNudge: Bool = false
    ) -> SketchJSONValue? {
        var normalizedOpacity = max(0, min(1, opacity))
        if forceNormalOpacityNudge && blendMode == .normal && normalizedOpacity == 1 {
            normalizedOpacity = 0.99
        }
        let hasBlend = blendMode != .normal
        let hasOpacity = normalizedOpacity != 1

        if !hasBlend && !(includeOpacityWhenDefaultBlend && hasOpacity) {
            return nil
        }

        return .object(SketchJSONObject([
            ("_class", .string("graphicsContextSettings")),
            ("blendMode", .int(blendMode.rawValue)),
            ("opacity", .double(normalizedOpacity)),
        ]))
    }


}
