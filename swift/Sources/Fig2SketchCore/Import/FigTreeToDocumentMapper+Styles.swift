import FigFormat
import Foundation

extension FigTreeToDocumentMapper {
    static func effectiveStyle(for node: FigNode, context: MappingContext) -> FigLayerStyle? {
        var style = node.style ?? FigLayerStyle()
        var hadOverride = false

        if let inheritFillStyleID = node.inheritFillStyleID,
           let referenceStyle = context.node(for: inheritFillStyleID)?.style,
           !referenceStyle.fills.isEmpty {
            style.fills = referenceStyle.fills
            hadOverride = true
        }

        if let inheritFillStyleIDForStroke = node.inheritFillStyleIDForStroke,
           let referenceStyle = context.node(for: inheritFillStyleIDForStroke)?.style,
           !referenceStyle.fills.isEmpty {
            if style.borders.isEmpty {
                style.borders = referenceStyle.fills.map {
                    FigBorder(paint: $0, thickness: 1, position: .center)
                }
            } else {
                style.borders = style.borders.enumerated().map { index, border in
                    let paintIndex = min(index, referenceStyle.fills.count - 1)
                    return FigBorder(
                        paint: referenceStyle.fills[paintIndex],
                        thickness: border.thickness,
                        position: border.position
                    )
                }
            }
            hadOverride = true
        }

        if !hadOverride, node.style == nil {
            return nil
        }
        return style.isDefault ? nil : style
    }

    static func effectiveTextStyle(for node: FigNode, context: MappingContext) -> ResolvedTextStyle {
        var resolved = ResolvedTextStyle(
            family: node.fontFamily,
            style: node.fontStyle,
            postscript: node.fontPostscript,
            size: node.fontSize
        )

        if let inheritTextStyleID = node.inheritTextStyleID,
           let referenceNode = context.node(for: inheritTextStyleID) {
            if let family = referenceNode.fontFamily {
                resolved.family = family
            }
            if let style = referenceNode.fontStyle {
                resolved.style = style
            }
            if let postscript = referenceNode.fontPostscript {
                resolved.postscript = postscript
            }
        }

        return resolved
    }

    private struct TextRunStyle: Equatable {
        var fontName: String
        var fontSize: Double
        var color: ConversionColor
    }

    private static let emojiFontName = "AppleColorEmoji"

    private static let emojiSizeAdjust: [Int: Double] = [
        2: 1.5, 3: 2, 4: 3, 5: 4, 6: 5, 7: 5.5, 8: 6, 9: 7, 10: 7.5,
        11: 8, 12: 9, 13: 10, 14: 10.5, 15: 11, 16: 12, 17: 13, 18: 13.5,
        19: 14, 20: 15, 21: 16, 22: 18, 23: 20, 24: 22, 25: 24,
    ]

    private static let openTypeFeatureMapping: [String: (type: Int, on: Int, off: Int)] = [
        "ss03": (type: 35, on: 6, off: 7),
        "calt": (type: 36, on: 0, off: 1),
    ]

    static func resolvedFontName(for style: ResolvedTextStyle) -> String {
        if style.family == emojiFontName {
            return emojiFontName
        }
        if let postscript = style.postscript, !postscript.isEmpty {
            return postscript
        }
        let family = style.family ?? "Roboto"
        let face = style.style ?? "Regular"
        return "\(family)-\(face)"
    }

    static func textKerning(for node: FigNode, baseFontSize: Double) -> Double? {
        guard let spacing = node.letterSpacing else { return nil }
        switch spacing.units {
        case "PIXELS":
            return spacing.value == 0 ? nil : spacing.value
        case "PERCENT":
            return baseFontSize * spacing.value / 100
        default:
            return nil
        }
    }

    static func textFeatureSettings(
        for node: FigNode,
        context: inout MappingContext
    ) -> [ConversionTextFeatureSetting] {
        var settings: [ConversionTextFeatureSetting] = []
        var unsupported: [String] = []

        for feature in node.toggledOnOTFeatures {
            guard let mapping = openTypeFeatureMapping[feature.lowercased()] else {
                unsupported.append(feature)
                continue
            }
            settings.append(.init(typeIdentifier: mapping.type, selectorIdentifier: mapping.on))
        }

        for feature in node.toggledOffOTFeatures {
            guard let mapping = openTypeFeatureMapping[feature.lowercased()] else {
                unsupported.append(feature)
                continue
            }
            settings.append(.init(typeIdentifier: mapping.type, selectorIdentifier: mapping.off))
        }

        if !unsupported.isEmpty {
            context.emitWarning("TXT006", nodeGUID: node.guid)
        }

        return settings
    }

    static func textAttributeRuns(
        for node: FigNode,
        characters: String,
        baseFontName: String,
        baseFontSize: Double,
        baseColor: ConversionColor,
        kerning: Double?,
        featureSettings: [ConversionTextFeatureSetting],
        context: inout MappingContext
    ) -> [ConversionTextAttributeRun] {
        let scalars = Array(characters.unicodeScalars)
        guard !scalars.isEmpty else { return [] }

        var glyphs = node.textGlyphs.sorted(by: { $0.firstCharacter < $1.firstCharacter })
        if glyphs.isEmpty {
            if scalars.count != 1 {
                context.emitWarning("TXT001", nodeGUID: node.guid)
            }
            glyphs = [FigTextGlyph(firstCharacter: 0)]
        } else if glyphs[0].firstCharacter > 0 {
            glyphs.insert(FigTextGlyph(firstCharacter: 0), at: 0)
        }
        glyphs.append(FigTextGlyph(firstCharacter: Int.max))

        let overridesByID = Dictionary(uniqueKeysWithValues: node.textStyleOverrideTable.map { ($0.styleID, $0) })
        let styleIDs = node.textCharacterStyleIDs

        var glyphIndex = 0
        var currentGlyph = glyphs[glyphIndex]
        var nextGlyph = glyphs[glyphIndex + 1]

        func runStyle(at index: Int, glyph: FigTextGlyph) -> TextRunStyle {
            let styleID = index < styleIDs.count ? styleIDs[index] : 0
            let styleOverride = overridesByID[styleID]

            var fontName = baseFontName
            var fontSize = baseFontSize
            var color = baseColor

            if let override = styleOverride {
                if let overrideColor = textColor(from: override.fills) {
                    color = overrideColor
                }
                if let postscript = override.fontPostscript, !postscript.isEmpty {
                    fontName = postscript
                } else if let family = override.fontFamily {
                    fontName = "\(family)-\(override.fontStyle ?? "Regular")"
                }
                if let overrideSize = override.fontSize {
                    fontSize = overrideSize
                }
            }

            if glyph.isEmojiGlyph {
                fontName = emojiFontName
                if let adjusted = emojiSizeAdjust[Int(fontSize.rounded())] {
                    fontSize = adjusted
                }
            }

            return TextRunStyle(fontName: fontName, fontSize: fontSize, color: color)
        }

        var currentStyle = runStyle(at: 0, glyph: currentGlyph)
        var runStart = 0
        var sketchPosition = 0
        var runs: [ConversionTextAttributeRun] = []

        for (index, scalar) in scalars.enumerated() {
            while index == nextGlyph.firstCharacter {
                glyphIndex += 1
                currentGlyph = glyphs[glyphIndex]
                nextGlyph = glyphs[glyphIndex + 1]
            }

            let style = runStyle(at: index, glyph: currentGlyph)
            if index > 0, style != currentStyle {
                runs.append(ConversionTextAttributeRun(
                    location: runStart,
                    length: sketchPosition - runStart,
                    fontName: currentStyle.fontName,
                    fontSize: currentStyle.fontSize,
                    color: currentStyle.color,
                    kerning: kerning,
                    featureSettings: featureSettings
                ))
                runStart = sketchPosition
                currentStyle = style
            }

            sketchPosition += scalar.value > 0xFFFF ? 2 : 1
        }

        runs.append(ConversionTextAttributeRun(
            location: runStart,
            length: sketchPosition - runStart,
            fontName: currentStyle.fontName,
            fontSize: currentStyle.fontSize,
            color: currentStyle.color,
            kerning: kerning,
            featureSettings: featureSettings
        ))
        return runs
    }

    static func textBaseColor(style: ConversionLayerStyle?) -> ConversionColor {
        guard let style else {
            return .init(red: 0, green: 0, blue: 0, alpha: 0)
        }
        for fill in style.fills where fill.isEnabled {
            switch fill.kind {
            case .solid(let color):
                return color
            case .gradient(let gradient):
                if let first = gradient.stops.first?.color {
                    return first
                }
            case .image, .unsupported:
                continue
            }
        }
        return .init(red: 0, green: 0, blue: 0, alpha: 0)
    }

    static func textColor(from fills: [FigPaint]) -> ConversionColor? {
        guard let first = fills.first else { return nil }
        switch first.kind {
        case .solid(let color):
            return .init(
                red: color.red,
                green: color.green,
                blue: color.blue,
                alpha: first.sourceColorAlpha ?? color.alpha
            )
        case .gradient(let gradient):
            guard let stop = gradient.stops.first else { return nil }
            return .init(
                red: stop.color.red,
                green: stop.color.green,
                blue: stop.color.blue,
                alpha: stop.color.alpha
            )
        case .image, .unsupported:
            return nil
        }
    }

    static func hasMultipleRunColors(_ runs: [ConversionTextAttributeRun]) -> Bool {
        guard let first = runs.first else { return false }
        return runs.dropFirst().contains(where: { $0.color != first.color })
    }

    static func mapStyle(_ style: FigLayerStyle) -> ConversionLayerStyle {
        ConversionLayerStyle(
            fills: style.fills.map(mapPaint),
            borders: style.borders.map(mapBorder),
            blurs: style.blurs.map(mapBlur),
            shadows: style.shadows.map(mapShadow),
            borderOptions: mapBorderOptions(style.borderOptions),
            miterLimit: style.miterLimit,
            windingRule: mapWindingRule(style.windingRule),
            corners: style.corners.map(mapCorners),
            blendMode: mapBlendMode(style.blendMode),
            blendModeWasExplicit: style.blendModeWasExplicit,
            blendModeNeedsOpacityNudge: style.blendModeNeedsOpacityNudge,
            opacity: style.opacity
        )
    }

    static func mapRenderableStyle(_ style: FigLayerStyle) -> ConversionLayerStyle {
        var mapped = mapStyle(style)
        mapped.miterLimit = 10
        mapped.windingRule = .nonZero
        return mapped
    }

    private static func mapBorder(_ border: FigBorder) -> ConversionBorder {
        ConversionBorder(
            paint: mapPaint(border.paint),
            thickness: border.thickness,
            position: mapBorderPosition(border.position)
        )
    }

    static func mapPaint(_ paint: FigPaint) -> ConversionPaint {
        ConversionPaint(
            kind: mapPaintKind(paint.kind),
            isEnabled: paint.isEnabled,
            blendMode: mapBlendMode(paint.blendMode),
            opacity: paint.opacity
        )
    }

    static func mapPaintKind(_ kind: FigPaintKind) -> ConversionPaintKind {
        switch kind {
        case .solid(let color):
            return .solid(ConversionColor(red: color.red, green: color.green, blue: color.blue, alpha: color.alpha))
        case .gradient(let gradient):
            return .gradient(mapGradient(gradient))
        case .image(let image):
            return .image(mapImagePaint(image))
        case .unsupported(let type):
            return .unsupported(type: type)
        }
    }

    private static func mapImagePaint(_ image: FigImagePaint) -> ConversionImagePaint {
        ConversionImagePaint(
            sourceName: image.sourceName,
            patternFillType: mapPatternFillType(image.patternFillType),
            patternTileScale: image.patternTileScale
        )
    }

    private static func mapPatternFillType(_ type: FigPatternFillType) -> ConversionPatternFillType {
        switch type {
        case .tile:
            return .tile
        case .fill:
            return .fill
        case .stretch:
            return .stretch
        case .fit:
            return .fit
        }
    }

    private static func mapGradient(_ gradient: FigGradient) -> ConversionGradient {
        ConversionGradient(
            type: mapGradientType(gradient.type),
            from: ConversionPoint(x: gradient.from.x, y: gradient.from.y),
            to: ConversionPoint(x: gradient.to.x, y: gradient.to.y),
            ellipseLength: gradient.ellipseLength,
            stops: gradient.stops.map { stop in
                ConversionGradientStop(
                    color: ConversionColor(
                        red: stop.color.red,
                        green: stop.color.green,
                        blue: stop.color.blue,
                        alpha: stop.color.alpha
                    ),
                    position: stop.position
                )
            }
        )
    }

    private static func mapGradientType(_ type: FigGradientType) -> ConversionGradientType {
        switch type {
        case .linear:
            return .linear
        case .radial:
            return .radial
        case .angular:
            return .angular
        }
    }

    private static func mapBlur(_ blur: FigBlur) -> ConversionBlur {
        ConversionBlur(
            isEnabled: blur.isEnabled,
            radius: blur.radius,
            type: mapBlurType(blur.type),
            isProgressive: blur.isProgressive,
            progressiveFrom: blur.progressiveFrom.map { ConversionPoint(x: $0.x, y: $0.y) },
            progressiveTo: blur.progressiveTo.map { ConversionPoint(x: $0.x, y: $0.y) },
            progressiveStartRadiusRatio: blur.progressiveStartRadiusRatio,
            isCustomGlass: blur.isCustomGlass,
            glassDistortion: blur.glassDistortion,
            glassDepth: blur.glassDepth,
            glassChromaticAberrationMultiplier: blur.glassChromaticAberrationMultiplier
        )
    }

    private static func mapBlurType(_ type: FigBlurType) -> ConversionBlurType {
        switch type {
        case .gaussian:
            return .gaussian
        case .background:
            return .background
        }
    }

    private static func mapShadow(_ shadow: FigShadow) -> ConversionShadow {
        ConversionShadow(
            blurRadius: shadow.blurRadius,
            offsetX: shadow.offsetX,
            offsetY: shadow.offsetY,
            spread: shadow.spread,
            isInnerShadow: shadow.isInnerShadow,
            isEnabled: shadow.isEnabled,
            color: ConversionColor(
                red: shadow.color.red,
                green: shadow.color.green,
                blue: shadow.color.blue,
                alpha: shadow.color.alpha
            )
        )
    }

    private static func mapBorderOptions(_ options: FigBorderOptions) -> ConversionBorderOptions {
        ConversionBorderOptions(
            lineCapStyle: mapLineCapStyle(options.lineCapStyle),
            lineJoinStyle: mapLineJoinStyle(options.lineJoinStyle),
            dashPattern: options.dashPattern
        )
    }

    private static func mapLineCapStyle(_ style: FigLineCapStyle) -> ConversionLineCapStyle {
        switch style {
        case .butt:
            return .butt
        case .round:
            return .round
        case .square:
            return .square
        }
    }

    private static func mapLineJoinStyle(_ style: FigLineJoinStyle) -> ConversionLineJoinStyle {
        switch style {
        case .miter:
            return .miter
        case .round:
            return .round
        case .bevel:
            return .bevel
        }
    }

    private static func mapWindingRule(_ rule: FigWindingRule) -> ConversionWindingRule {
        switch rule {
        case .nonZero:
            return .nonZero
        case .evenOdd:
            return .evenOdd
        }
    }

    private static func mapCorners(_ corners: FigStyleCorners) -> ConversionStyleCorners {
        ConversionStyleCorners(
            radii: corners.radii,
            style: corners.style == .smooth ? .smooth : .rounded
        )
    }

    private static func mapBlendMode(_ blendMode: FigBlendMode) -> ConversionBlendMode {
        guard let mapped = ConversionBlendMode(rawValue: blendMode.rawValue) else {
            return .normal
        }
        return mapped
    }

    private static func mapBorderPosition(_ position: FigBorderPosition) -> ConversionBorderPosition {
        switch position {
        case .center:
            return .center
        case .inside:
            return .inside
        case .outside:
            return .outside
        }
    }

    static func applyMarkerOverrides(from node: FigNode, style: inout ConversionLayerStyle) {
        guard let overrideStrokeCap = node.vectorOverrideStrokeCap else { return }
        applyMarkerOverrides(startStrokeCap: "NONE", endStrokeCap: overrideStrokeCap, style: &style)
    }

    static func applyMarkerOverrides(
        startStrokeCap: String,
        endStrokeCap: String,
        style: inout ConversionLayerStyle
    ) {
        let startMarker = markerType(for: startStrokeCap)
        let endMarker = markerType(for: endStrokeCap)
        style.startMarkerType = startMarker
        style.endMarkerType = endMarker

        if startMarker > 0 || endMarker > 0 {
            if startMarker < 4 {
                style.startDecorationType = startMarker
            }
            if endMarker < 4 {
                style.endDecorationType = endMarker
            }
        }
    }

    private static func markerType(for strokeCap: String) -> Int {
        switch strokeCap {
        case "ARROW_LINES":
            return 1
        case "ARROW_EQUILATERAL":
            return 2
        case "TRIANGLE_FILLED":
            return 3
        case "OPEN_CIRCLE":
            return 4
        case "CIRCLE_FILLED":
            return 5
        case "OPEN_SQUARE":
            return 6
        case "DIAMOND_FILLED":
            return 7
        default:
            return 0
        }
    }

}
