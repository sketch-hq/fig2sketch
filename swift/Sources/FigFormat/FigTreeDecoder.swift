import Foundation
import ZIPFoundation

public struct FigColor: Equatable, Sendable {
    public var red: Double
    public var green: Double
    public var blue: Double
    public var alpha: Double

    public init(red: Double, green: Double, blue: Double, alpha: Double) {
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha
    }
}

public struct FigPoint: Equatable, Sendable {
    public var x: Double
    public var y: Double

    public init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }
}

public struct FigGradientStop: Equatable, Sendable {
    public var color: FigColor
    public var position: Double

    public init(color: FigColor, position: Double) {
        self.color = color
        self.position = position
    }
}

public enum FigGradientType: Int, Equatable, Sendable {
    case linear = 0
    case radial = 1
    case angular = 2
}

public struct FigGradient: Equatable, Sendable {
    public var type: FigGradientType
    public var from: FigPoint
    public var to: FigPoint
    public var ellipseLength: Double
    public var stops: [FigGradientStop]
    public var usesDiamondFallback: Bool

    public init(
        type: FigGradientType,
        from: FigPoint,
        to: FigPoint,
        ellipseLength: Double = 0,
        stops: [FigGradientStop],
        usesDiamondFallback: Bool = false
    ) {
        self.type = type
        self.from = from
        self.to = to
        self.ellipseLength = ellipseLength
        self.stops = stops
        self.usesDiamondFallback = usesDiamondFallback
    }
}

public enum FigPatternFillType: Int, Equatable, Sendable {
    case tile = 0
    case fill = 1
    case stretch = 2
    case fit = 3
}

public struct FigImagePaint: Equatable, Sendable {
    public var sourceName: String
    public var patternFillType: FigPatternFillType
    public var patternTileScale: Double
    public var embeddedBlobIndex: Int?
    public var transform: FigAffineTransform?
    public var originalImageWidth: Double?
    public var originalImageHeight: Double?
    public var hasPaintFilter: Bool

    public init(
        sourceName: String,
        patternFillType: FigPatternFillType,
        patternTileScale: Double = 1,
        embeddedBlobIndex: Int? = nil,
        transform: FigAffineTransform? = nil,
        originalImageWidth: Double? = nil,
        originalImageHeight: Double? = nil,
        hasPaintFilter: Bool = false
    ) {
        self.sourceName = sourceName
        self.patternFillType = patternFillType
        self.patternTileScale = patternTileScale
        self.embeddedBlobIndex = embeddedBlobIndex
        self.transform = transform
        self.originalImageWidth = originalImageWidth
        self.originalImageHeight = originalImageHeight
        self.hasPaintFilter = hasPaintFilter
    }

    public var hasCropTransform: Bool {
        guard let transform else { return false }
        return !transform.isIdentity
    }
}

public struct FigAffineTransform: Equatable, Sendable {
    public var m00: Double
    public var m01: Double
    public var m02: Double
    public var m10: Double
    public var m11: Double
    public var m12: Double

    public init(m00: Double, m01: Double, m02: Double, m10: Double, m11: Double, m12: Double) {
        self.m00 = m00
        self.m01 = m01
        self.m02 = m02
        self.m10 = m10
        self.m11 = m11
        self.m12 = m12
    }

    public static let identity = FigAffineTransform(m00: 1, m01: 0, m02: 0, m10: 0, m11: 1, m12: 0)

    public var isIdentity: Bool {
        self == .identity
    }
}

public enum FigBlurType: Int, Equatable, Sendable {
    case gaussian = 0
    case background = 3
}

public struct FigBlur: Equatable, Sendable {
    public var isEnabled: Bool
    public var radius: Double
    public var type: FigBlurType
    public var isProgressive: Bool
    public var progressiveFrom: FigPoint?
    public var progressiveTo: FigPoint?
    public var progressiveStartRadiusRatio: Double?
    public var isCustomGlass: Bool
    public var glassDistortion: Double
    public var glassDepth: Double
    public var glassChromaticAberrationMultiplier: Double

    public init(
        isEnabled: Bool = true,
        radius: Double,
        type: FigBlurType,
        isProgressive: Bool = false,
        progressiveFrom: FigPoint? = nil,
        progressiveTo: FigPoint? = nil,
        progressiveStartRadiusRatio: Double? = nil,
        isCustomGlass: Bool = false,
        glassDistortion: Double = 0,
        glassDepth: Double = 0,
        glassChromaticAberrationMultiplier: Double = 0
    ) {
        self.isEnabled = isEnabled
        self.radius = radius
        self.type = type
        self.isProgressive = isProgressive
        self.progressiveFrom = progressiveFrom
        self.progressiveTo = progressiveTo
        self.progressiveStartRadiusRatio = progressiveStartRadiusRatio
        self.isCustomGlass = isCustomGlass
        self.glassDistortion = glassDistortion
        self.glassDepth = glassDepth
        self.glassChromaticAberrationMultiplier = glassChromaticAberrationMultiplier
    }
}

public struct FigShadow: Equatable, Sendable {
    public var blurRadius: Double
    public var offsetX: Double
    public var offsetY: Double
    public var spread: Double
    public var isInnerShadow: Bool
    public var isEnabled: Bool
    public var color: FigColor

    public init(
        blurRadius: Double,
        offsetX: Double,
        offsetY: Double,
        spread: Double,
        isInnerShadow: Bool = false,
        isEnabled: Bool = true,
        color: FigColor
    ) {
        self.blurRadius = blurRadius
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.spread = spread
        self.isInnerShadow = isInnerShadow
        self.isEnabled = isEnabled
        self.color = color
    }
}

public enum FigCornerStyle: Int, Equatable, Sendable {
    case rounded = 0
    case smooth = 1
}

public struct FigStyleCorners: Equatable, Sendable {
    public var radii: [Double] // [topLeft, topRight, bottomRight, bottomLeft]
    public var style: FigCornerStyle

    public init(radii: [Double], style: FigCornerStyle) {
        self.radii = radii
        self.style = style
    }

    public var isDefault: Bool {
        radii.allSatisfy { $0 == 0 } && style == .rounded
    }
}

public enum FigLineCapStyle: Int, Equatable, Sendable {
    case butt = 0
    case round = 1
    case square = 2
}

public enum FigLineJoinStyle: Int, Equatable, Sendable {
    case miter = 0
    case round = 1
    case bevel = 2
}

public enum FigWindingRule: Int, Equatable, Sendable {
    case nonZero = 0
    case evenOdd = 1
}

public struct FigBorderOptions: Equatable, Sendable {
    public var lineCapStyle: FigLineCapStyle
    public var lineJoinStyle: FigLineJoinStyle
    public var dashPattern: [Double]

    public init(
        lineCapStyle: FigLineCapStyle = .butt,
        lineJoinStyle: FigLineJoinStyle = .miter,
        dashPattern: [Double] = []
    ) {
        self.lineCapStyle = lineCapStyle
        self.lineJoinStyle = lineJoinStyle
        self.dashPattern = dashPattern
    }

    public var isDefault: Bool {
        lineCapStyle == .butt && lineJoinStyle == .miter && dashPattern.isEmpty
    }
}

public enum FigBlendMode: Int, Equatable, Sendable {
    case normal = 0
    case darken = 1
    case multiply = 2
    case colorBurn = 3
    case lighten = 4
    case screen = 5
    case colorDodge = 6
    case overlay = 7
    case softLight = 8
    case hardLight = 9
    case difference = 10
    case exclusion = 11
    case hue = 12
    case saturation = 13
    case color = 14
    case luminosity = 15
    case plusDarker = 16
    case plusLighter = 17
}

public enum FigBorderPosition: String, Equatable, Sendable {
    case center
    case inside
    case outside
}

public enum FigPaintKind: Equatable, Sendable {
    case solid(FigColor)
    case gradient(FigGradient)
    case image(FigImagePaint)
    case unsupported(type: String)
}

public struct FigPaint: Equatable, Sendable {
    public var kind: FigPaintKind
    public var isEnabled: Bool
    public var blendMode: FigBlendMode
    public var opacity: Double
    public var sourceColorAlpha: Double?

    public init(
        kind: FigPaintKind,
        isEnabled: Bool = true,
        blendMode: FigBlendMode = .normal,
        opacity: Double = 1,
        sourceColorAlpha: Double? = nil
    ) {
        self.kind = kind
        self.isEnabled = isEnabled
        self.blendMode = blendMode
        self.opacity = opacity
        self.sourceColorAlpha = sourceColorAlpha
    }
}

public struct FigBorder: Equatable, Sendable {
    public var paint: FigPaint
    public var thickness: Double
    public var position: FigBorderPosition

    public init(paint: FigPaint, thickness: Double, position: FigBorderPosition) {
        self.paint = paint
        self.thickness = thickness
        self.position = position
    }
}

public struct FigLayerStyle: Equatable, Sendable {
    public var fills: [FigPaint]
    public var borders: [FigBorder]
    public var blurs: [FigBlur]
    public var shadows: [FigShadow]
    public var borderOptions: FigBorderOptions
    public var miterLimit: Double
    public var windingRule: FigWindingRule
    public var corners: FigStyleCorners?
    public var blendMode: FigBlendMode
    public var blendModeWasExplicit: Bool
    public var blendModeNeedsOpacityNudge: Bool
    public var opacity: Double

    public init(
        fills: [FigPaint] = [],
        borders: [FigBorder] = [],
        blurs: [FigBlur] = [],
        shadows: [FigShadow] = [],
        borderOptions: FigBorderOptions = .init(),
        miterLimit: Double = 10,
        windingRule: FigWindingRule = .nonZero,
        corners: FigStyleCorners? = nil,
        blendMode: FigBlendMode = .normal,
        blendModeWasExplicit: Bool = false,
        blendModeNeedsOpacityNudge: Bool? = nil,
        opacity: Double = 1
    ) {
        self.fills = fills
        self.borders = borders
        self.blurs = blurs
        self.shadows = shadows
        self.borderOptions = borderOptions
        self.miterLimit = miterLimit
        self.windingRule = windingRule
        self.corners = corners
        self.blendMode = blendMode
        self.blendModeWasExplicit = blendModeWasExplicit
        self.blendModeNeedsOpacityNudge = blendModeNeedsOpacityNudge ?? (blendModeWasExplicit && blendMode == .normal)
        self.opacity = opacity
    }

    public var isDefault: Bool {
        fills.isEmpty &&
            borders.isEmpty &&
            blurs.isEmpty &&
            shadows.isEmpty &&
            borderOptions.isDefault &&
            miterLimit == 10 &&
            windingRule == .nonZero &&
            (corners == nil || corners?.isDefault == true) &&
            blendMode == .normal &&
            !blendModeWasExplicit &&
            !blendModeNeedsOpacityNudge &&
            opacity == 1
    }
}

public struct FigNode: Equatable, Sendable {
    public var guid: [UInt32]
    public var type: String
    public var name: String
    public var parentGuid: [UInt32]?
    public var parentPosition: UInt32?
    public var x: Double?
    public var y: Double?
    public var width: Double?
    public var height: Double?
    public var transform: FigAffineTransform?
    public var style: FigLayerStyle?
    public var inheritFillStyleID: [UInt32]?
    public var inheritFillStyleIDForStroke: [UInt32]?
    public var inheritTextStyleID: [UInt32]?
    public var fontFamily: String?
    public var fontStyle: String?
    public var fontPostscript: String?
    public var fontSize: Double?
    public var resizeToFit: Bool
    public var frameMaskDisabled: Bool
    public var scrollDirection: String?
    public var overlayPositionType: String?
    public var overlayBackgroundInteraction: String?
    public var horizontalConstraint: String?
    public var verticalConstraint: String?
    public var stackMode: String?
    public var stackSpacing: Double?
    public var stackPrimaryAlignItems: String?
    public var stackCounterAlignItems: String?
    public var stackVerticalPadding: Double?
    public var stackPaddingRight: Double?
    public var stackPaddingBottom: Double?
    public var stackHorizontalPadding: Double?
    public var layoutGrids: [FigLayoutGrid]
    public var vectorHasExplicitNetwork: Bool
    public var vectorNetworkVertexCount: Int?
    public var vectorHasNetworkBlob: Bool
    public var vectorNetwork: VectorNetwork<FigVectorStyleOverride>?
    public var vectorOverrideStrokeCap: String?
    public var strokeCap: String?
    public var overrideKey: [UInt32]?
    public var textCharacters: String?
    public var textCharacterStyleIDs: [Int]
    public var textStyleOverrideTable: [FigTextStyleOverride]
    public var textGlyphs: [FigTextGlyph]
    public var letterSpacing: FigLetterSpacing?
    public var textAutoResize: String?
    public var toggledOnOTFeatures: [String]
    public var toggledOffOTFeatures: [String]
    public var prototypeDevice: FigPrototypeDevice?
    public var prototypeStartingPointName: String?
    public var prototypeInteractions: [FigPrototypeInteraction]
    public var symbolData: FigSymbolData?
    public var componentPropAssignments: [FigComponentPropAssignment]
    public var componentPropRefs: [FigComponentPropRef]
    public var isStateGroup: Bool

    public init(
        guid: [UInt32],
        type: String,
        name: String,
        parentGuid: [UInt32]? = nil,
        parentPosition: UInt32? = nil,
        x: Double? = nil,
        y: Double? = nil,
        width: Double? = nil,
        height: Double? = nil,
        transform: FigAffineTransform? = nil,
        style: FigLayerStyle? = nil,
        inheritFillStyleID: [UInt32]? = nil,
        inheritFillStyleIDForStroke: [UInt32]? = nil,
        inheritTextStyleID: [UInt32]? = nil,
        fontFamily: String? = nil,
        fontStyle: String? = nil,
        fontPostscript: String? = nil,
        fontSize: Double? = nil,
        resizeToFit: Bool = false,
        frameMaskDisabled: Bool = false,
        scrollDirection: String? = nil,
        overlayPositionType: String? = nil,
        overlayBackgroundInteraction: String? = nil,
        horizontalConstraint: String? = nil,
        verticalConstraint: String? = nil,
        stackMode: String? = nil,
        stackSpacing: Double? = nil,
        stackPrimaryAlignItems: String? = nil,
        stackCounterAlignItems: String? = nil,
        stackVerticalPadding: Double? = nil,
        stackPaddingRight: Double? = nil,
        stackPaddingBottom: Double? = nil,
        stackHorizontalPadding: Double? = nil,
        layoutGrids: [FigLayoutGrid] = [],
        vectorHasExplicitNetwork: Bool = false,
        vectorNetworkVertexCount: Int? = nil,
        vectorHasNetworkBlob: Bool = false,
        vectorNetwork: VectorNetwork<FigVectorStyleOverride>? = nil,
        vectorOverrideStrokeCap: String? = nil,
        strokeCap: String? = nil,
        overrideKey: [UInt32]? = nil,
        textCharacters: String? = nil,
        textCharacterStyleIDs: [Int] = [],
        textStyleOverrideTable: [FigTextStyleOverride] = [],
        textGlyphs: [FigTextGlyph] = [],
        letterSpacing: FigLetterSpacing? = nil,
        textAutoResize: String? = nil,
        toggledOnOTFeatures: [String] = [],
        toggledOffOTFeatures: [String] = [],
        prototypeDevice: FigPrototypeDevice? = nil,
        prototypeStartingPointName: String? = nil,
        prototypeInteractions: [FigPrototypeInteraction] = [],
        symbolData: FigSymbolData? = nil,
        componentPropAssignments: [FigComponentPropAssignment] = [],
        componentPropRefs: [FigComponentPropRef] = [],
        isStateGroup: Bool = false
    ) {
        self.guid = guid
        self.type = type
        self.name = name
        self.parentGuid = parentGuid
        self.parentPosition = parentPosition
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.transform = transform
        self.style = style
        self.inheritFillStyleID = inheritFillStyleID
        self.inheritFillStyleIDForStroke = inheritFillStyleIDForStroke
        self.inheritTextStyleID = inheritTextStyleID
        self.fontFamily = fontFamily
        self.fontStyle = fontStyle
        self.fontPostscript = fontPostscript
        self.fontSize = fontSize
        self.resizeToFit = resizeToFit
        self.frameMaskDisabled = frameMaskDisabled
        self.scrollDirection = scrollDirection
        self.overlayPositionType = overlayPositionType
        self.overlayBackgroundInteraction = overlayBackgroundInteraction
        self.horizontalConstraint = horizontalConstraint
        self.verticalConstraint = verticalConstraint
        self.stackMode = stackMode
        self.stackSpacing = stackSpacing
        self.stackPrimaryAlignItems = stackPrimaryAlignItems
        self.stackCounterAlignItems = stackCounterAlignItems
        self.stackVerticalPadding = stackVerticalPadding
        self.stackPaddingRight = stackPaddingRight
        self.stackPaddingBottom = stackPaddingBottom
        self.stackHorizontalPadding = stackHorizontalPadding
        self.layoutGrids = layoutGrids
        self.vectorHasExplicitNetwork = vectorHasExplicitNetwork
        self.vectorNetworkVertexCount = vectorNetworkVertexCount
        self.vectorHasNetworkBlob = vectorHasNetworkBlob
        self.vectorNetwork = vectorNetwork
        self.vectorOverrideStrokeCap = vectorOverrideStrokeCap
        self.strokeCap = strokeCap
        self.overrideKey = overrideKey
        self.textCharacters = textCharacters
        self.textCharacterStyleIDs = textCharacterStyleIDs
        self.textStyleOverrideTable = textStyleOverrideTable
        self.textGlyphs = textGlyphs
        self.letterSpacing = letterSpacing
        self.textAutoResize = textAutoResize
        self.toggledOnOTFeatures = toggledOnOTFeatures
        self.toggledOffOTFeatures = toggledOffOTFeatures
        self.prototypeDevice = prototypeDevice
        self.prototypeStartingPointName = prototypeStartingPointName
        self.prototypeInteractions = prototypeInteractions
        self.symbolData = symbolData
        self.componentPropAssignments = componentPropAssignments
        self.componentPropRefs = componentPropRefs
        self.isStateGroup = isStateGroup
    }
}

public struct FigVectorStyleOverride: Equatable, Sendable {
    public var style: FigLayerStyle?
    public var strokeCap: String?
    public var handleMirroring: String?
    public var cornerRadius: Double?
    public var overridesFills: Bool
    public var overridesBorders: Bool
    public var overridesEffects: Bool
    public var overridesWindingRule: Bool
    public var overridesBlendMode: Bool
    public var overridesOpacity: Bool

    public init(
        style: FigLayerStyle? = nil,
        strokeCap: String? = nil,
        handleMirroring: String? = nil,
        cornerRadius: Double? = nil,
        overridesFills: Bool = false,
        overridesBorders: Bool = false,
        overridesEffects: Bool = false,
        overridesWindingRule: Bool = false,
        overridesBlendMode: Bool = false,
        overridesOpacity: Bool = false
    ) {
        self.style = style
        self.strokeCap = strokeCap
        self.handleMirroring = handleMirroring
        self.cornerRadius = cornerRadius
        self.overridesFills = overridesFills
        self.overridesBorders = overridesBorders
        self.overridesEffects = overridesEffects
        self.overridesWindingRule = overridesWindingRule
        self.overridesBlendMode = overridesBlendMode
        self.overridesOpacity = overridesOpacity
    }

    public var hasStyleOverrides: Bool {
        overridesFills || overridesBorders || overridesEffects || overridesWindingRule || overridesBlendMode || overridesOpacity
    }
}

public struct FigLetterSpacing: Equatable, Sendable {
    public var units: String
    public var value: Double

    public init(units: String, value: Double) {
        self.units = units
        self.value = value
    }
}

public struct FigTextStyleOverride: Equatable, Sendable {
    public var styleID: Int
    public var fills: [FigPaint]
    public var fontFamily: String?
    public var fontStyle: String?
    public var fontPostscript: String?
    public var fontSize: Double?

    public init(
        styleID: Int,
        fills: [FigPaint] = [],
        fontFamily: String? = nil,
        fontStyle: String? = nil,
        fontPostscript: String? = nil,
        fontSize: Double? = nil
    ) {
        self.styleID = styleID
        self.fills = fills
        self.fontFamily = fontFamily
        self.fontStyle = fontStyle
        self.fontPostscript = fontPostscript
        self.fontSize = fontSize
    }
}

public struct FigTextGlyph: Equatable, Sendable {
    public var firstCharacter: Int
    public var emojiCodePoints: [UInt32]

    public init(firstCharacter: Int, emojiCodePoints: [UInt32] = []) {
        self.firstCharacter = firstCharacter
        self.emojiCodePoints = emojiCodePoints
    }

    public var isEmojiGlyph: Bool {
        !emojiCodePoints.isEmpty
    }
}

public struct FigLayoutGrid: Equatable, Sendable {
    public var pattern: String
    public var axis: String
    public var type: String
    public var numSections: Double
    public var offset: Double
    public var sectionSize: Double
    public var gutterSize: Double
    public var visible: Bool

    public init(
        pattern: String,
        axis: String,
        type: String,
        numSections: Double,
        offset: Double,
        sectionSize: Double,
        gutterSize: Double,
        visible: Bool
    ) {
        self.pattern = pattern
        self.axis = axis
        self.type = type
        self.numSections = numSections
        self.offset = offset
        self.sectionSize = sectionSize
        self.gutterSize = gutterSize
        self.visible = visible
    }
}

public struct FigSymbolData: Equatable, Sendable {
    public var symbolID: [UInt32]
    public var symbolOverrides: [FigSymbolOverride]

    public init(symbolID: [UInt32], symbolOverrides: [FigSymbolOverride]) {
        self.symbolID = symbolID
        self.symbolOverrides = symbolOverrides
    }
}

public struct FigSymbolOverride: Equatable, Sendable {
    public var guidPath: [[UInt32]]
    public var textCharacters: String?
    public var overriddenSymbolID: [UInt32]?
    public var fillPaints: [FigPaint]
    public var hasFillPaints: Bool
    public var unsupportedProperties: [String]

    public init(
        guidPath: [[UInt32]],
        textCharacters: String? = nil,
        overriddenSymbolID: [UInt32]? = nil,
        fillPaints: [FigPaint] = [],
        hasFillPaints: Bool = false,
        unsupportedProperties: [String] = []
    ) {
        self.guidPath = guidPath
        self.textCharacters = textCharacters
        self.overriddenSymbolID = overriddenSymbolID
        self.fillPaints = fillPaints
        self.hasFillPaints = hasFillPaints
        self.unsupportedProperties = unsupportedProperties
    }
}

public struct FigComponentPropAssignment: Equatable, Sendable {
    public var defID: [UInt32]
    public var textCharacters: String?
    public var boolValue: Bool?
    public var guidValue: [UInt32]?

    public init(
        defID: [UInt32],
        textCharacters: String? = nil,
        boolValue: Bool? = nil,
        guidValue: [UInt32]? = nil
    ) {
        self.defID = defID
        self.textCharacters = textCharacters
        self.boolValue = boolValue
        self.guidValue = guidValue
    }
}

public struct FigComponentPropRef: Equatable, Sendable {
    public var defID: [UInt32]?
    public var nodeField: String
    public var isDeleted: Bool

    public init(defID: [UInt32]?, nodeField: String, isDeleted: Bool) {
        self.defID = defID
        self.nodeField = nodeField
        self.isDeleted = isDeleted
    }
}

public struct FigPrototypeDevice: Equatable, Sendable {
    public var presetIdentifier: String
    public var size: FigPoint

    public init(presetIdentifier: String, size: FigPoint) {
        self.presetIdentifier = presetIdentifier
        self.size = size
    }
}

public struct FigPrototypeAction: Equatable, Sendable {
    public var navigationType: String?
    public var connectionType: String?
    public var transitionNodeID: [UInt32]?
    public var transitionType: String?
    public var transitionPreserveScroll: Bool
    public var overlayRelativePosition: FigPoint?
    public var isEmpty: Bool

    public init(
        navigationType: String? = nil,
        connectionType: String? = nil,
        transitionNodeID: [UInt32]? = nil,
        transitionType: String? = nil,
        transitionPreserveScroll: Bool = false,
        overlayRelativePosition: FigPoint? = nil,
        isEmpty: Bool = false
    ) {
        self.navigationType = navigationType
        self.connectionType = connectionType
        self.transitionNodeID = transitionNodeID
        self.transitionType = transitionType
        self.transitionPreserveScroll = transitionPreserveScroll
        self.overlayRelativePosition = overlayRelativePosition
        self.isEmpty = isEmpty
    }
}

public struct FigPrototypeInteraction: Equatable, Sendable {
    public var isDeleted: Bool
    public var interactionType: String?
    public var actions: [FigPrototypeAction]

    public init(isDeleted: Bool, interactionType: String?, actions: [FigPrototypeAction]) {
        self.isDeleted = isDeleted
        self.interactionType = interactionType
        self.actions = actions
    }
}

public struct FigTreeNode: Equatable, Sendable {
    public var node: FigNode
    public var children: [FigTreeNode]

    public init(node: FigNode, children: [FigTreeNode]) {
        self.node = node
        self.children = children
    }
}

public struct FigTree: Equatable, Sendable {
    public var root: FigTreeNode

    public init(root: FigTreeNode) {
        self.root = root
    }
}

public enum FigTreeDecoder {
    public static func decodeFigFile(url: URL) throws -> DecodedCanvasFig {
        let fileData = try Data(contentsOf: url)
        if fileData.starts(with: Data([0x50, 0x4B])) {
            let archive = try Archive(url: url, accessMode: .read)
            guard let entry = archive["canvas.fig"] else {
                throw KiwiDecoderError.invalidCanvasFig
            }
            var canvas = Data()
            _ = try archive.extract(entry) { chunk in
                canvas.append(chunk)
            }
            return try KiwiCanvasDecoder.decodeCanvasFig(data: canvas)
        } else {
            return try KiwiCanvasDecoder.decodeCanvasFig(data: fileData)
        }
    }

    public static func buildTree(from rootMessage: KiwiValue) throws -> FigTree {
        guard let rootObject = rootMessage.objectValue,
              let nodeChanges = rootObject["nodeChanges"]?.arrayValue else {
            throw KiwiDecoderError.malformedRootMessage
        }

        var byID: [[UInt32]: FigNode] = [:]
        var childrenByParent: [[UInt32]: [(positionKey: ParentPositionKey, order: Int, childID: [UInt32])]] = [:]
        var rootID: [UInt32]?

        for (index, nodeValue) in nodeChanges.enumerated() {
            guard let object = nodeValue.objectValue,
                  let guid = parseGuid(object["guid"]),
                  let type = object["type"]?.stringValue,
                  let name = object["name"]?.stringValue else {
                throw KiwiDecoderError.malformedNodeChange(index)
            }

            let parentInfo = parseParentInfo(object)
            let frame = parseFrame(object)
            let style = parseLayerStyle(object)
            let textStyle = parseTextStyleInfo(object)
            let layoutGrids = parseLayoutGrids(object["layoutGrids"])
            let symbolData = parseSymbolData(object["symbolData"])
            let componentPropAssignments = parseComponentPropAssignments(object["componentPropAssignments"])
            let componentPropRefs = parseComponentPropRefs(object["componentPropRefs"])
            let vectorHasExplicitNetwork = object["vectorNetwork"] != nil
            let vectorNetworkVertexCount = parseVectorNetworkVertexCount(object["vectorNetwork"])
            let vectorHasNetworkBlob = parseVectorHasNetworkBlob(object["vectorData"])
            let vectorNetwork = parseVectorNetwork(
                networkValue: object["vectorNetwork"],
                vectorDataValue: object["vectorData"],
                rootObject: rootObject
            )
            let vectorOverrideStrokeCap = parseVectorOverrideStrokeCap(object["vectorData"])
            let overrideKey = parseOverrideKey(object["overrideKey"])
            let textCharacters = parseTextCharacters(object["textData"])
            let textCharacterStyleIDs = parseTextCharacterStyleIDs(object["textData"])
            let textStyleOverrideTable = parseTextStyleOverrideTable(object["textData"])
            let textGlyphs = parseTextGlyphs(object["textData"])
            let letterSpacing = parseLetterSpacing(object["letterSpacing"])
            let toggledOnOTFeatures = parseStringArray(object["toggledOnOTFeatures"])
            let toggledOffOTFeatures = parseStringArray(object["toggledOffOTFeatures"])
            let prototypeDevice = parsePrototypeDevice(object["prototypeDevice"])
            let prototypeStartingPointName = parsePrototypeStartingPointName(object["prototypeStartingPoint"])
            let prototypeInteractions = parsePrototypeInteractions(object["prototypeInteractions"])
            if rootID == nil { rootID = guid }

            let node = FigNode(
                guid: guid,
                type: type,
                name: name,
                parentGuid: parentInfo.guid,
                parentPosition: parentInfo.position,
                x: frame.x,
                y: frame.y,
                width: frame.width,
                height: frame.height,
                transform: parseAffineTransform(object["transform"]).map(figTransform),
                style: style,
                inheritFillStyleID: parseGuid(object["inheritFillStyleID"]),
                inheritFillStyleIDForStroke: parseGuid(object["inheritFillStyleIDForStroke"]),
                inheritTextStyleID: parseGuid(object["inheritTextStyleID"]),
                fontFamily: textStyle.family,
                fontStyle: textStyle.style,
                fontPostscript: textStyle.postscript,
                fontSize: textStyle.size,
                resizeToFit: parseBool(object["resizeToFit"]) ?? false,
                frameMaskDisabled: parseBool(object["frameMaskDisabled"]) ?? false,
                scrollDirection: object["scrollDirection"]?.stringValue,
                overlayPositionType: object["overlayPositionType"]?.stringValue,
                overlayBackgroundInteraction: object["overlayBackgroundInteraction"]?.stringValue,
                horizontalConstraint: object["horizontalConstraint"]?.stringValue,
                verticalConstraint: object["verticalConstraint"]?.stringValue,
                stackMode: object["stackMode"]?.stringValue,
                stackSpacing: parseDouble(object["stackSpacing"]),
                stackPrimaryAlignItems: object["stackPrimaryAlignItems"]?.stringValue,
                stackCounterAlignItems: object["stackCounterAlignItems"]?.stringValue,
                stackVerticalPadding: parseDouble(object["stackVerticalPadding"]),
                stackPaddingRight: parseDouble(object["stackPaddingRight"]),
                stackPaddingBottom: parseDouble(object["stackPaddingBottom"]),
                stackHorizontalPadding: parseDouble(object["stackHorizontalPadding"]),
                layoutGrids: layoutGrids,
                vectorHasExplicitNetwork: vectorHasExplicitNetwork,
                vectorNetworkVertexCount: vectorNetworkVertexCount,
                vectorHasNetworkBlob: vectorHasNetworkBlob,
                vectorNetwork: vectorNetwork,
                vectorOverrideStrokeCap: vectorOverrideStrokeCap,
                strokeCap: object["strokeCap"]?.stringValue,
                overrideKey: overrideKey,
                textCharacters: textCharacters,
                textCharacterStyleIDs: textCharacterStyleIDs,
                textStyleOverrideTable: textStyleOverrideTable,
                textGlyphs: textGlyphs,
                letterSpacing: letterSpacing,
                textAutoResize: object["textAutoResize"]?.stringValue,
                toggledOnOTFeatures: toggledOnOTFeatures,
                toggledOffOTFeatures: toggledOffOTFeatures,
                prototypeDevice: prototypeDevice,
                prototypeStartingPointName: prototypeStartingPointName,
                prototypeInteractions: prototypeInteractions,
                symbolData: symbolData,
                componentPropAssignments: componentPropAssignments,
                componentPropRefs: componentPropRefs,
                isStateGroup: parseBool(object["isStateGroup"]) ?? false
            )
            byID[guid] = node

            if let parentGuid = parentInfo.guid {
                childrenByParent[parentGuid, default: []].append((parentInfo.sortPosition, index, guid))
            }
        }

        guard let resolvedRootID = rootID else {
            throw KiwiDecoderError.noRootNode
        }

        func buildNode(_ id: [UInt32]) throws -> FigTreeNode {
            guard let node = byID[id] else {
                throw KiwiDecoderError.missingParent(id.last ?? 0)
            }
            let unsortedChildren: [(positionKey: ParentPositionKey, order: Int, childID: [UInt32])] = childrenByParent[id] ?? []
            let childrenTuples = unsortedChildren.sorted(by: { lhs, rhs in
                if lhs.positionKey == rhs.positionKey { return lhs.order < rhs.order }
                return lhs.positionKey < rhs.positionKey
            })
            let children = try childrenTuples.map { try buildNode($0.childID) }
            return FigTreeNode(node: node, children: children)
        }

        return try FigTree(root: buildNode(resolvedRootID))
    }

    private struct ParentInfo {
        var guid: [UInt32]?
        var position: UInt32?
        var sortPosition: ParentPositionKey
    }

    private enum ParentPositionKey: Comparable {
        case numeric(UInt64)
        case string(String)

        static func < (lhs: ParentPositionKey, rhs: ParentPositionKey) -> Bool {
            switch (lhs, rhs) {
            case let (.numeric(left), .numeric(right)):
                return left < right
            case let (.string(left), .string(right)):
                return left < right
            case (.numeric, .string):
                return true
            case (.string, .numeric):
                return false
            }
        }
    }

    private struct FrameInfo {
        var x: Double?
        var y: Double?
        var width: Double?
        var height: Double?
    }

    private struct TextStyleInfo {
        var family: String?
        var style: String?
        var postscript: String?
        var size: Double?
    }

    private static func parseParentInfo(_ object: [String: KiwiValue]) -> ParentInfo {
        if let parentIndex = object["parentIndex"]?.objectValue {
            let positionValue = parentIndex["position"]
            return ParentInfo(
                guid: parseGuid(parentIndex["guid"]),
                position: parseUInt32(positionValue),
                sortPosition: parseParentPositionKey(positionValue)
            )
        }

        let positionValue = object["parentPosition"]
        return ParentInfo(
            guid: parseGuid(object["parentGuid"]),
            position: parseUInt32(positionValue),
            sortPosition: parseParentPositionKey(positionValue)
        )
    }

    private static func parseParentPositionKey(_ value: KiwiValue?) -> ParentPositionKey {
        guard let value else { return .numeric(0) }
        switch value {
        case .uint(let v):
            return .numeric(UInt64(v))
        case .int(let v):
            return .numeric(v >= 0 ? UInt64(v) : 0)
        case .uint64(let v):
            return .numeric(v)
        case .int64(let v):
            return .numeric(v >= 0 ? UInt64(v) : 0)
        case .string(let value):
            return .string(value)
        default:
            return .numeric(0)
        }
    }

    private static func parseFrame(_ object: [String: KiwiValue]) -> FrameInfo {
        if let x = parseDouble(object["x"]),
           let y = parseDouble(object["y"]),
           let width = parseDouble(object["width"]),
           let height = parseDouble(object["height"]) {
            return FrameInfo(x: x, y: y, width: width, height: height)
        }

        guard let size = object["size"]?.objectValue,
              let width = parseDouble(size["x"]),
              let height = parseDouble(size["y"]) else {
            return FrameInfo(x: nil, y: nil, width: nil, height: nil)
        }

        if let transform = object["transform"]?.objectValue,
           let m00 = parseDouble(transform["m00"]),
           let m01 = parseDouble(transform["m01"]),
           let m02 = parseDouble(transform["m02"]),
           let m10 = parseDouble(transform["m10"]),
           let m11 = parseDouble(transform["m11"]),
           let m12 = parseDouble(transform["m12"]) {
            let halfX = width / 2
            let halfY = height / 2
            let rotatedCenterToOriginX = (m00 * halfX) + (m01 * halfY)
            let rotatedCenterToOriginY = (m10 * halfX) + (m11 * halfY)
            let x = m02 + (rotatedCenterToOriginX - halfX)
            let y = m12 + (rotatedCenterToOriginY - halfY)
            return FrameInfo(x: x, y: y, width: width, height: height)
        }

        return FrameInfo(x: nil, y: nil, width: width, height: height)
    }

    private static func parseTextStyleInfo(_ object: [String: KiwiValue]) -> TextStyleInfo {
        let fontObject = object["fontName"]?.objectValue
        return TextStyleInfo(
            family: fontObject?["family"]?.stringValue,
            style: fontObject?["style"]?.stringValue,
            postscript: fontObject?["postscript"]?.stringValue,
            size: parseDouble(object["fontSize"])
        )
    }

    private static func parseLayoutGrids(_ value: KiwiValue?) -> [FigLayoutGrid] {
        guard let items = value?.arrayValue else { return [] }
        return items.compactMap(parseLayoutGrid)
    }

    private static func parseLayoutGrid(_ value: KiwiValue) -> FigLayoutGrid? {
        guard let object = value.objectValue,
              let pattern = object["pattern"]?.stringValue,
              let axis = object["axis"]?.stringValue,
              let type = object["type"]?.stringValue,
              let numSections = parseDouble(object["numSections"]),
              let offset = parseDouble(object["offset"]),
              let sectionSize = parseDouble(object["sectionSize"]),
              let gutterSize = parseDouble(object["gutterSize"]) else {
            return nil
        }

        return FigLayoutGrid(
            pattern: pattern,
            axis: axis,
            type: type,
            numSections: numSections,
            offset: offset,
            sectionSize: sectionSize,
            gutterSize: gutterSize,
            visible: parseBool(object["visible"]) ?? true
        )
    }

    private static func parseOverrideKey(_ value: KiwiValue?) -> [UInt32]? {
        guard let parsed = parseGuid(value) else { return nil }
        if parsed.first == UInt32.max {
            return nil
        }
        return parsed
    }

    private static func parseTextCharacters(_ value: KiwiValue?) -> String? {
        guard let object = value?.objectValue else { return nil }
        return object["characters"]?.stringValue
    }

    private static func parseTextCharacterStyleIDs(_ value: KiwiValue?) -> [Int] {
        guard let object = value?.objectValue,
              let ids = object["characterStyleIDs"]?.arrayValue else {
            return []
        }
        return ids.compactMap(parseInt)
    }

    private static func parseTextStyleOverrideTable(_ value: KiwiValue?) -> [FigTextStyleOverride] {
        guard let object = value?.objectValue,
              let table = object["styleOverrideTable"]?.arrayValue else {
            return []
        }
        return table.compactMap(parseTextStyleOverride)
    }

    private static func parseTextStyleOverride(_ value: KiwiValue) -> FigTextStyleOverride? {
        guard let object = value.objectValue,
              let styleID = parseInt(object["styleID"]) else {
            return nil
        }
        let fontObject = object["fontName"]?.objectValue
        return FigTextStyleOverride(
            styleID: styleID,
            fills: parsePaintArray(object["fillPaints"], nodeObject: object),
            fontFamily: fontObject?["family"]?.stringValue,
            fontStyle: fontObject?["style"]?.stringValue,
            fontPostscript: fontObject?["postscript"]?.stringValue,
            fontSize: parseDouble(object["fontSize"])
        )
    }

    private static func parseTextGlyphs(_ value: KiwiValue?) -> [FigTextGlyph] {
        guard let object = value?.objectValue,
              let glyphValues = object["glyphs"]?.arrayValue else {
            return []
        }
        return glyphValues.compactMap(parseTextGlyph)
    }

    private static func parseTextGlyph(_ value: KiwiValue) -> FigTextGlyph? {
        guard let object = value.objectValue,
              let firstCharacter = parseInt(object["firstCharacter"]) else {
            return nil
        }
        let emoji = object["emojiCodePoints"]?.arrayValue?.compactMap(parseUInt32) ?? []
        return FigTextGlyph(firstCharacter: firstCharacter, emojiCodePoints: emoji)
    }

    private static func parseLetterSpacing(_ value: KiwiValue?) -> FigLetterSpacing? {
        guard let object = value?.objectValue,
              let units = object["units"]?.stringValue,
              let spacingValue = parseDouble(object["value"]) else {
            return nil
        }
        return FigLetterSpacing(units: units, value: spacingValue)
    }

    private static func parseStringArray(_ value: KiwiValue?) -> [String] {
        guard let values = value?.arrayValue else { return [] }
        return values.compactMap(\.stringValue)
    }

    private static func parseVectorNetworkVertexCount(_ value: KiwiValue?) -> Int? {
        guard let object = value?.objectValue else { return nil }
        guard let vertices = object["vertices"]?.arrayValue else { return 0 }
        return vertices.count
    }

    private static func parseVectorHasNetworkBlob(_ value: KiwiValue?) -> Bool {
        guard let object = value?.objectValue else { return false }
        return object["vectorNetworkBlob"] != nil
    }

    private static func parseVectorNetwork(
        networkValue: KiwiValue?,
        vectorDataValue: KiwiValue?,
        rootObject: [String: KiwiValue]
    ) -> VectorNetwork<FigVectorStyleOverride>? {
        let styleOverrideTable = parseVectorStyleOverrideTable(vectorDataValue)
        if let decoded = parseVectorNetworkFromBlob(
            vectorDataValue: vectorDataValue,
            rootObject: rootObject,
            styleOverrideTable: styleOverrideTable
        ) {
            return decoded
        }
        return parseVectorNetworkObject(networkValue, styleOverrideTable: styleOverrideTable)
    }

    private static func parseVectorNetworkFromBlob(
        vectorDataValue: KiwiValue?,
        rootObject: [String: KiwiValue],
        styleOverrideTable: [UInt32: FigVectorStyleOverride]
    ) -> VectorNetwork<FigVectorStyleOverride>? {
        guard let networkData = parseVectorNetworkBlobData(vectorDataValue, rootObject: rootObject) else {
            return nil
        }
        let scale = parseVectorScale(vectorDataValue)
        return try? VectorNetworkDecoder.decode(
            networkData: networkData,
            scale: scale,
            styleOverrideTable: styleOverrideTable
        )
    }

    private static func parseVectorNetworkBlobData(
        _ vectorDataValue: KiwiValue?,
        rootObject: [String: KiwiValue]
    ) -> Data? {
        guard let vectorData = vectorDataValue?.objectValue,
              let blobIndex = parseInt(vectorData["vectorNetworkBlob"]),
              blobIndex >= 0,
              let blobs = rootObject["blobs"]?.arrayValue,
              blobIndex < blobs.count,
              let blobObject = blobs[blobIndex].objectValue,
              let bytes = parseByteArray(blobObject["bytes"]) else {
            return nil
        }
        return Data(bytes)
    }

    private static func parseVectorScale(_ vectorDataValue: KiwiValue?) -> VectorScale {
        guard let vectorData = vectorDataValue?.objectValue,
              let normalizedSize = vectorData["normalizedSize"]?.objectValue else {
            return VectorScale(x: 1, y: 1)
        }
        return VectorScale(
            x: parseDouble(normalizedSize["x"]) ?? 1,
            y: parseDouble(normalizedSize["y"]) ?? 1
        )
    }

    private static func parseVectorStyleOverrideTable(
        _ vectorDataValue: KiwiValue?
    ) -> [UInt32: FigVectorStyleOverride] {
        guard let vectorData = vectorDataValue?.objectValue,
              let styleTable = vectorData["styleOverrideTable"]?.arrayValue else {
            return [:]
        }
        var output: [UInt32: FigVectorStyleOverride] = [:]
        output.reserveCapacity(styleTable.count)
        for entry in styleTable {
            guard let object = entry.objectValue,
                  let styleID = parseUInt32(object["styleID"]) else {
                continue
            }
            output[styleID] = parseVectorStyleOverride(object)
        }
        return output
    }

    private static func parseVectorStyleOverride(_ object: [String: KiwiValue]) -> FigVectorStyleOverride {
        FigVectorStyleOverride(
            style: parseLayerStyle(object),
            strokeCap: object["strokeCap"]?.stringValue,
            handleMirroring: object["handleMirroring"]?.stringValue,
            cornerRadius: parseDouble(object["cornerRadius"]),
            overridesFills: object["fillPaints"] != nil,
            overridesBorders: object["strokePaints"] != nil ||
                object["strokeWeight"] != nil ||
                object["strokeAlign"] != nil ||
                object["strokeDashes"] != nil ||
                object["strokeCap"] != nil ||
                object["strokeJoin"] != nil ||
                object["strokeMiterAngle"] != nil,
            overridesEffects: object["effects"] != nil,
            overridesWindingRule: object["fillRule"] != nil,
            overridesBlendMode: object["blendMode"] != nil,
            overridesOpacity: object["opacity"] != nil
        )
    }

    private static func parseVectorNetworkObject(
        _ value: KiwiValue?,
        styleOverrideTable: [UInt32: FigVectorStyleOverride]
    ) -> VectorNetwork<FigVectorStyleOverride>? {
        guard let object = value?.objectValue,
              let vertexValues = object["vertices"]?.arrayValue,
              let segmentValues = object["segments"]?.arrayValue,
              let regionValues = object["regions"]?.arrayValue else {
            return nil
        }

        let vertices = vertexValues.compactMap {
            parseVectorVertex($0, styleOverrideTable: styleOverrideTable)
        }
        let segments = segmentValues.compactMap(parseVectorSegment)
        let regions = regionValues.compactMap {
            parseVectorRegion($0, styleOverrideTable: styleOverrideTable)
        }

        return VectorNetwork(regions: regions, segments: segments, vertices: vertices)
    }

    private static func parseVectorVertex(
        _ value: KiwiValue,
        styleOverrideTable: [UInt32: FigVectorStyleOverride]
    ) -> VectorVertex<FigVectorStyleOverride>? {
        guard let object = value.objectValue,
              let x = parseDouble(object["x"]),
              let y = parseDouble(object["y"]) else {
            return nil
        }
        return VectorVertex(
            x: x,
            y: y,
            style: parseVectorResolvedStyle(object["style"], styleOverrideTable: styleOverrideTable)
        )
    }

    private static func parseVectorResolvedStyle(
        _ value: KiwiValue?,
        styleOverrideTable: [UInt32: FigVectorStyleOverride]
    ) -> VectorResolvedStyle<FigVectorStyleOverride>? {
        guard let object = value?.objectValue else { return nil }

        if let styleID = parseUInt32(object["styleID"]) {
            if let resolved = styleOverrideTable[styleID] {
                return .override(resolved)
            }
            return .styleID(styleID)
        }

        return .override(parseVectorStyleOverride(object))
    }

    private static func parseVectorSegment(_ value: KiwiValue) -> VectorSegment? {
        guard let object = value.objectValue,
              let start = parseUInt32(object["start"]),
              let end = parseUInt32(object["end"]) else {
            return nil
        }

        let tangentStart = object["tangentStart"]?.objectValue
        let tangentEnd = object["tangentEnd"]?.objectValue

        return VectorSegment(
            start: start,
            end: end,
            tangentStart: VectorVertex<NeverStyle>(
                x: parseDouble(tangentStart?["x"]) ?? 0,
                y: parseDouble(tangentStart?["y"]) ?? 0
            ),
            tangentEnd: VectorVertex<NeverStyle>(
                x: parseDouble(tangentEnd?["x"]) ?? 0,
                y: parseDouble(tangentEnd?["y"]) ?? 0
            )
        )
    }

    private static func parseVectorRegion(
        _ value: KiwiValue,
        styleOverrideTable: [UInt32: FigVectorStyleOverride]
    ) -> VectorRegion<FigVectorStyleOverride>? {
        guard let object = value.objectValue,
              let loopsValue = object["loops"]?.arrayValue else {
            return nil
        }

        let loops: [[UInt32]] = loopsValue.map { loop in
            (loop.arrayValue ?? []).compactMap(parseUInt32)
        }

        let style = parseVectorResolvedStyle(object["style"], styleOverrideTable: styleOverrideTable)
            ?? styleOverrideTable[0].map { VectorResolvedStyle.override($0) }
            ?? .styleID(0)

        let windingRule: VectorWindingRule
        if let raw = object["windingRule"]?.stringValue,
           let parsed = VectorWindingRule(rawValue: raw) {
            windingRule = parsed
        } else {
            windingRule = .nonzero
        }

        return VectorRegion(loops: loops, style: style, windingRule: windingRule)
    }

    private static func parseVectorOverrideStrokeCap(_ value: KiwiValue?) -> String? {
        guard let object = value?.objectValue,
              let styleTable = object["styleOverrideTable"]?.arrayValue else {
            return nil
        }
        for entry in styleTable {
            guard let style = entry.objectValue else { continue }
            if let strokeCap = style["strokeCap"]?.stringValue {
                return strokeCap
            }
        }
        return nil
    }

    private static func parsePrototypeDevice(_ value: KiwiValue?) -> FigPrototypeDevice? {
        guard let object = value?.objectValue,
              let presetIdentifier = object["presetIdentifier"]?.stringValue,
              let sizeObject = object["size"]?.objectValue,
              let width = parseDouble(sizeObject["x"]),
              let height = parseDouble(sizeObject["y"]) else {
            return nil
        }
        return FigPrototypeDevice(
            presetIdentifier: presetIdentifier,
            size: FigPoint(x: width, y: height)
        )
    }

    private static func parsePrototypeStartingPointName(_ value: KiwiValue?) -> String? {
        guard let object = value?.objectValue else { return nil }
        return object["name"]?.stringValue
    }

    private static func parsePrototypeInteractions(_ value: KiwiValue?) -> [FigPrototypeInteraction] {
        guard let interactions = value?.arrayValue else { return [] }
        return interactions.compactMap(parsePrototypeInteraction)
    }

    private static func parsePrototypeInteraction(_ value: KiwiValue) -> FigPrototypeInteraction? {
        guard let object = value.objectValue else { return nil }
        let event = object["event"]?.objectValue
        let interactionType = event?["interactionType"]?.stringValue
        let actions = parsePrototypeActions(object["actions"])
        return FigPrototypeInteraction(
            isDeleted: parseBool(object["isDeleted"]) ?? false,
            interactionType: interactionType,
            actions: actions
        )
    }

    private static func parsePrototypeActions(_ value: KiwiValue?) -> [FigPrototypeAction] {
        guard let actions = value?.arrayValue else { return [] }
        return actions.compactMap(parsePrototypeAction)
    }

    private static func parsePrototypeAction(_ value: KiwiValue) -> FigPrototypeAction? {
        guard let object = value.objectValue else { return nil }
        let overlayRelativePosition: FigPoint?
        if let pointObject = object["overlayRelativePosition"]?.objectValue,
           let x = parseDouble(pointObject["x"]),
           let y = parseDouble(pointObject["y"]) {
            overlayRelativePosition = FigPoint(x: x, y: y)
        } else {
            overlayRelativePosition = nil
        }
        return FigPrototypeAction(
            navigationType: object["navigationType"]?.stringValue,
            connectionType: object["connectionType"]?.stringValue,
            transitionNodeID: parseGuid(object["transitionNodeID"]),
            transitionType: object["transitionType"]?.stringValue,
            transitionPreserveScroll: parseBool(object["transitionPreserveScroll"]) ?? false,
            overlayRelativePosition: overlayRelativePosition,
            isEmpty: object.isEmpty
        )
    }

    private static func parseSymbolData(_ value: KiwiValue?) -> FigSymbolData? {
        guard let object = value?.objectValue,
              let symbolID = parseGuid(object["symbolID"]) else {
            return nil
        }
        let symbolOverrides = parseSymbolOverrides(object["symbolOverrides"])
        return FigSymbolData(symbolID: symbolID, symbolOverrides: symbolOverrides)
    }

    private static func parseSymbolOverrides(_ value: KiwiValue?) -> [FigSymbolOverride] {
        guard let items = value?.arrayValue else { return [] }
        return items.compactMap(parseSymbolOverride)
    }

    private static func parseSymbolOverride(_ value: KiwiValue) -> FigSymbolOverride? {
        guard let object = value.objectValue,
              let guidPathObject = object["guidPath"]?.objectValue,
              let guidItems = guidPathObject["guids"]?.arrayValue else {
            return nil
        }

        let guidPath = guidItems.compactMap(parseGuid)
        guard !guidPath.isEmpty else { return nil }

        let textCharacters = parseTextCharacters(object["textData"])
        let overriddenSymbolID = parseGuid(object["overriddenSymbolID"])
        let hasFillPaints = object["fillPaints"] != nil
        let fillPaints = parsePaintArray(object["fillPaints"], nodeObject: [:])

        var unsupported: [String] = []
        for key in object.keys {
            switch key {
            case "guidPath", "textData", "overriddenSymbolID", "fillPaints",
                 "size", "pluginData", "name", "exportSettings", "componentPropAssignments":
                continue
            default:
                unsupported.append(key)
            }
        }
        unsupported.sort()

        return FigSymbolOverride(
            guidPath: guidPath,
            textCharacters: textCharacters,
            overriddenSymbolID: overriddenSymbolID,
            fillPaints: fillPaints,
            hasFillPaints: hasFillPaints,
            unsupportedProperties: unsupported
        )
    }

    private static func parseComponentPropAssignments(_ value: KiwiValue?) -> [FigComponentPropAssignment] {
        guard let items = value?.arrayValue else { return [] }
        return items.compactMap(parseComponentPropAssignment)
    }

    private static func parseComponentPropAssignment(_ value: KiwiValue) -> FigComponentPropAssignment? {
        guard let object = value.objectValue,
              let defID = parseGuid(object["defID"]),
              let valueObject = object["value"]?.objectValue else {
            return nil
        }

        let textCharacters = parseTextCharacters(valueObject["textValue"])
        let boolValue = parseBool(valueObject["boolValue"])
        let guidValue = parseGuid(valueObject["guidValue"])
        return FigComponentPropAssignment(
            defID: defID,
            textCharacters: textCharacters,
            boolValue: boolValue,
            guidValue: guidValue
        )
    }

    private static func parseComponentPropRefs(_ value: KiwiValue?) -> [FigComponentPropRef] {
        guard let items = value?.arrayValue else { return [] }
        return items.compactMap(parseComponentPropRef)
    }

    private static func parseComponentPropRef(_ value: KiwiValue) -> FigComponentPropRef? {
        guard let object = value.objectValue,
              let nodeField = object["componentPropNodeField"]?.stringValue else {
            return nil
        }
        return FigComponentPropRef(
            defID: parseGuid(object["defID"]),
            nodeField: nodeField,
            isDeleted: parseBool(object["isDeleted"]) ?? false
        )
    }

    private static func parseGuid(_ value: KiwiValue?) -> [UInt32]? {
        guard let value else { return nil }
        switch value {
        case .uint(let v):
            return [v]
        case .array(let values):
            let parsed = values.compactMap(parseUInt32)
            return parsed.isEmpty ? nil : parsed
        case .object(let object):
            if let sessionID = parseUInt32(object["sessionID"]),
               let localID = parseUInt32(object["localID"]) {
                return [sessionID, localID]
            }
            return nil
        default:
            return nil
        }
    }

    private static func parseLayerStyle(_ object: [String: KiwiValue]) -> FigLayerStyle? {
        let fills = parsePaintArray(object["fillPaints"], nodeObject: object)
        let strokePaints = parsePaintArray(object["strokePaints"], nodeObject: object)
        let strokeWeight = parseDouble(object["strokeWeight"]) ?? 1
        let strokePosition = parseBorderPosition(object["strokeAlign"]) ?? .center
        let borders = strokePaints.map { FigBorder(paint: $0, thickness: strokeWeight, position: strokePosition) }
        let effects = parseEffects(object["effects"])
        let borderOptions = FigBorderOptions(
            lineCapStyle: parseLineCapStyle(object["strokeCap"]) ?? .butt,
            lineJoinStyle: parseLineJoinStyle(object["strokeJoin"]) ?? .miter,
            dashPattern: parseNumberArray(object["dashPattern"])
        )
        let miterLimit = parseDouble(object["miterLimit"]) ?? 10
        let windingRule = parseWindingRule(object["fillRule"]) ?? .nonZero
        let corners = parseStyleCorners(object)
        let blendModeRaw = object["blendMode"]
        let blendMode = parseBlendMode(blendModeRaw) ?? .normal
        let opacity = parseDouble(object["opacity"]) ?? 1

        let style = FigLayerStyle(
            fills: fills,
            borders: borders,
            blurs: effects.blurs,
            shadows: effects.shadows,
            borderOptions: borderOptions,
            miterLimit: miterLimit,
            windingRule: windingRule,
            corners: corners,
            blendMode: blendMode,
            blendModeWasExplicit: blendModeRaw != nil,
            blendModeNeedsOpacityNudge: blendModeRaw?.stringValue == "NORMAL",
            opacity: opacity
        )
        return style.isDefault ? nil : style
    }

    private static func parsePaintArray(_ value: KiwiValue?, nodeObject: [String: KiwiValue]) -> [FigPaint] {
        guard let paints = value?.arrayValue else { return [] }
        return paints.compactMap { parsePaint($0, nodeObject: nodeObject) }
    }

    private static func parsePaint(_ value: KiwiValue, nodeObject: [String: KiwiValue]) -> FigPaint? {
        guard let object = value.objectValue else { return nil }
        let isEnabled = parseBool(object["visible"]) ?? true
        let blendMode = parseBlendMode(object["blendMode"]) ?? .normal
        let paintOpacity = parseDouble(object["opacity"]) ?? 1
        let type = object["type"]?.stringValue ?? "UNKNOWN"

        if type == "SOLID",
           let color = parseSolidPaintColor(object) {
            return FigPaint(
                kind: .solid(color),
                isEnabled: isEnabled,
                blendMode: blendMode,
                opacity: 1,
                sourceColorAlpha: parseSolidPaintSourceAlpha(object)
            )
        }

        if let gradientType = parseGradientType(type),
           let gradient = parseGradientPaint(object, nodeObject: nodeObject, gradientType: gradientType) {
            return FigPaint(kind: .gradient(gradient), isEnabled: isEnabled, blendMode: blendMode, opacity: paintOpacity)
        }

        if type == "IMAGE",
           let imagePaint = parseImagePaint(object) {
            return FigPaint(kind: .image(imagePaint), isEnabled: isEnabled, blendMode: blendMode, opacity: paintOpacity)
        }

        return FigPaint(kind: .unsupported(type: type), isEnabled: isEnabled, blendMode: blendMode, opacity: paintOpacity)
    }

    private static func parseSolidPaintColor(_ object: [String: KiwiValue]) -> FigColor? {
        guard let color = object["color"]?.objectValue,
              let red = parseDouble(color["r"]),
              let green = parseDouble(color["g"]),
              let blue = parseDouble(color["b"]) else {
            return nil
        }
        let colorAlpha = parseDouble(color["a"]) ?? 1.0
        let opacity = parseDouble(object["opacity"]) ?? colorAlpha
        return FigColor(red: red, green: green, blue: blue, alpha: opacity)
    }

    private static func parseSolidPaintSourceAlpha(_ object: [String: KiwiValue]) -> Double? {
        guard let color = object["color"]?.objectValue else { return nil }
        return parseDouble(color["a"])
    }

    private static func parseGradientType(_ type: String) -> FigGradientType? {
        switch type {
        case "GRADIENT_LINEAR":
            return .linear
        case "GRADIENT_RADIAL", "GRADIENT_DIAMOND":
            return .radial
        case "GRADIENT_ANGULAR":
            return .angular
        default:
            return nil
        }
    }

    private static func parseImagePaint(_ object: [String: KiwiValue]) -> FigImagePaint? {
        guard let image = object["image"]?.objectValue,
              let sourceName = parseImageSourceName(image) else {
            return nil
        }

        return FigImagePaint(
            sourceName: sourceName,
            patternFillType: parsePatternFillType(object["imageScaleMode"]) ?? .tile,
            patternTileScale: parseDouble(object["scale"]) ?? 1,
            embeddedBlobIndex: parseEmbeddedBlobIndex(image["dataBlob"]),
            transform: parseAffineTransform(object["transform"]).map(figTransform),
            originalImageWidth: parseDouble(object["originalImageWidth"]),
            originalImageHeight: parseDouble(object["originalImageHeight"]),
            hasPaintFilter: object["paintFilter"] != nil
        )
    }

    private static func parseEmbeddedBlobIndex(_ value: KiwiValue?) -> Int? {
        guard let value else { return nil }
        switch value {
        case .uint(let v):
            return Int(v)
        case .int(let v):
            return v >= 0 ? Int(v) : nil
        case .uint64(let v):
            return v <= UInt64(Int.max) ? Int(v) : nil
        case .int64(let v):
            return v >= 0 && v <= Int64(Int.max) ? Int(v) : nil
        default:
            return nil
        }
    }

    private static func parseImageSourceName(_ image: [String: KiwiValue]) -> String? {
        if let filename = image["filename"]?.stringValue, !filename.isEmpty {
            return filename
        }

        if let hashBytes = parseByteArray(image["hash"]), !hashBytes.isEmpty {
            return hashBytes.map { String(format: "%02x", $0) }.joined()
        }

        return nil
    }

    private static func parsePatternFillType(_ value: KiwiValue?) -> FigPatternFillType? {
        guard let string = value?.stringValue else { return nil }
        switch string {
        case "TILE":
            return .tile
        case "FILL":
            return .fill
        case "STRETCH":
            return .stretch
        case "FIT":
            return .fit
        default:
            return nil
        }
    }

    private static func parseGradientPaint(
        _ paintObject: [String: KiwiValue],
        nodeObject: [String: KiwiValue],
        gradientType: FigGradientType
    ) -> FigGradient? {
        guard let transform = parseAffineTransform(paintObject["transform"]),
              let inverse = transform.inverted(),
              let rawStops = paintObject["stops"]?.arrayValue else {
            return nil
        }

        let rotationOffset = gradientType == .angular
            ? atan2(-transform.m10, transform.m00) / (2 * .pi)
            : 0

        let stops = parseGradientStops(rawStops, rotationOffset: rotationOffset)
        guard !stops.isEmpty else { return nil }

        switch gradientType {
        case .linear:
            let pointFrom = inverse.applying(x: 0, y: 0.5)
            let pointTo = inverse.applying(x: 1, y: 0.5)
            return FigGradient(
                type: .linear,
                from: FigPoint(x: pointFrom.x, y: pointFrom.y),
                to: FigPoint(x: pointTo.x, y: pointTo.y),
                stops: stops,
                usesDiamondFallback: false
            )

        case .radial:
            let pointFrom = inverse.applying(x: 0.5, y: 0.5)
            let pointTo = inverse.applying(x: 1, y: 0.5)
            let pointEllipse = inverse.applying(x: 0.5, y: 1)
            let xScale = radialEllipseXScale(nodeObject: nodeObject)
            let ellipseLength = safeDivide(
                scaledDistance(from: pointFrom, to: pointEllipse, xScale: xScale),
                by: scaledDistance(from: pointFrom, to: pointTo, xScale: xScale),
                fallback: 0
            )

            return FigGradient(
                type: .radial,
                from: FigPoint(x: pointFrom.x, y: pointFrom.y),
                to: FigPoint(x: pointTo.x, y: pointTo.y),
                ellipseLength: ellipseLength,
                stops: stops,
                usesDiamondFallback: paintObject["type"]?.stringValue == "GRADIENT_DIAMOND"
            )

        case .angular:
            return FigGradient(
                type: .angular,
                from: FigPoint(x: 0.5, y: 0),
                to: FigPoint(x: 0.5, y: 1),
                ellipseLength: 0,
                stops: stops,
                usesDiamondFallback: false
            )
        }
    }

    private static func parseGradientStops(_ values: [KiwiValue], rotationOffset: Double) -> [FigGradientStop] {
        var stops = values.compactMap(parseGradientStop)
        guard !stops.isEmpty else { return [] }

        if rotationOffset != 0 {
            for index in stops.indices {
                stops[index].position = rotatedStopPosition(stops[index].position, offset: rotationOffset)
            }
            if let lastIndex = stops.indices.last {
                stops[lastIndex].position -= 0.00001
            }
            return stops
        }

        if stops[0].position != 0 {
            stops.insert(FigGradientStop(color: stops[0].color, position: 0), at: 0)
        }
        if let last = stops.last, last.position != 1 {
            stops.append(FigGradientStop(color: last.color, position: 1))
        }
        return stops
    }

    private static func parseGradientStop(_ value: KiwiValue) -> FigGradientStop? {
        guard let object = value.objectValue,
              let color = parseGradientStopColor(object["color"]),
              let position = parseDouble(object["position"]) else {
            return nil
        }
        return FigGradientStop(color: color, position: position)
    }

    private static func parseGradientStopColor(_ value: KiwiValue?) -> FigColor? {
        guard let color = value?.objectValue,
              let red = parseDouble(color["r"]),
              let green = parseDouble(color["g"]),
              let blue = parseDouble(color["b"]) else {
            return nil
        }
        let alpha = parseDouble(color["a"]) ?? 1
        return FigColor(red: red, green: green, blue: blue, alpha: alpha)
    }

    private static func radialEllipseXScale(nodeObject: [String: KiwiValue]) -> Double {
        let stroke = parseDouble(nodeObject["strokeWeight"]) ?? 0
        let width = parseNodeDimension(nodeObject, key: "x")
        let height = parseNodeDimension(nodeObject, key: "y")
        guard let width, let height else { return 1 }
        let numerator = width + (2 * stroke)
        let denominator = height + (2 * stroke)
        return safeDivide(numerator, by: denominator, fallback: 1)
    }

    private static func parseNodeDimension(_ object: [String: KiwiValue], key: String) -> Double? {
        if let size = object["size"]?.objectValue, let value = parseDouble(size[key]) {
            return value
        }
        switch key {
        case "x":
            return parseDouble(object["width"])
        case "y":
            return parseDouble(object["height"])
        default:
            return nil
        }
    }

    private static func parseStyleCorners(_ object: [String: KiwiValue]) -> FigStyleCorners? {
        let hasBase = object["cornerRadius"] != nil
        let hasPerCorner = object["rectangleTopLeftCornerRadius"] != nil ||
            object["rectangleTopRightCornerRadius"] != nil ||
            object["rectangleBottomRightCornerRadius"] != nil ||
            object["rectangleBottomLeftCornerRadius"] != nil
        guard hasBase || hasPerCorner else { return nil }

        let base = parseDouble(object["cornerRadius"]) ?? 0
        let topLeft = parseDouble(object["rectangleTopLeftCornerRadius"]) ?? base
        let topRight = parseDouble(object["rectangleTopRightCornerRadius"]) ?? base
        let bottomRight = parseDouble(object["rectangleBottomRightCornerRadius"]) ?? base
        let bottomLeft = parseDouble(object["rectangleBottomLeftCornerRadius"]) ?? base
        let smoothing = parseDouble(object["cornerSmoothing"]) ?? 0
        let style: FigCornerStyle = smoothing > 0 ? .smooth : .rounded
        let corners = FigStyleCorners(radii: [topLeft, topRight, bottomRight, bottomLeft], style: style)
        return corners.isDefault ? nil : corners
    }

    private struct ParsedEffects {
        var blurs: [FigBlur] = []
        var shadows: [FigShadow] = []
    }

    private static func parseEffects(_ value: KiwiValue?) -> ParsedEffects {
        guard let effects = value?.arrayValue else { return ParsedEffects() }
        var parsed = ParsedEffects()

        for effectValue in effects {
            guard let effect = effectValue.objectValue,
                  let type = effect["type"]?.stringValue else {
                continue
            }

            switch type {
            case "INNER_SHADOW", "DROP_SHADOW":
                if let shadow = parseShadow(effect, isInner: type == "INNER_SHADOW") {
                    parsed.shadows.append(shadow)
                }
            case "FOREGROUND_BLUR", "BACKGROUND_BLUR":
                if let blur = parseBlur(effect, isBackground: type == "BACKGROUND_BLUR") {
                    parsed.blurs.append(blur)
                }
            case "GLASS":
                if let blur = parseGlassBlur(effect) {
                    parsed.blurs.append(blur)
                }
            default:
                continue
            }
        }

        return parsed
    }

    private static func parseShadow(_ effect: [String: KiwiValue], isInner: Bool) -> FigShadow? {
        guard let blurRadius = parseDouble(effect["radius"]),
              let offset = effect["offset"]?.objectValue,
              let offsetX = parseDouble(offset["x"]),
              let offsetY = parseDouble(offset["y"]),
              let color = parseGradientStopColor(effect["color"]) else {
            return nil
        }

        return FigShadow(
            blurRadius: blurRadius,
            offsetX: offsetX,
            offsetY: offsetY,
            spread: parseDouble(effect["spread"]) ?? 0,
            isInnerShadow: isInner,
            isEnabled: parseBool(effect["visible"]) ?? true,
            color: color
        )
    }

    private static func parsePoint(_ value: KiwiValue?) -> FigPoint? {
        guard let object = value?.objectValue,
              let x = parseDouble(object["x"]),
              let y = parseDouble(object["y"]) else {
            return nil
        }
        return FigPoint(x: x, y: y)
    }

    private static func parseBlur(_ effect: [String: KiwiValue], isBackground: Bool) -> FigBlur? {
        guard let figmaRadius = parseDouble(effect["radius"]) else {
            return nil
        }

        let radius = figmaRadius / 2
        let isProgressive = effect["blurOpType"]?.stringValue == "PROGRESSIVE"
        let progressiveFrom = parsePoint(effect["startOffset"]) ?? FigPoint(x: 0, y: 0)
        let progressiveTo = parsePoint(effect["endOffset"]) ?? FigPoint(x: 0, y: 0)
        let startRadius = (parseDouble(effect["startRadius"]) ?? 0) / 2
        let progressiveStartRatio = radius == 0 ? 0 : (startRadius / radius)

        return FigBlur(
            isEnabled: parseBool(effect["visible"]) ?? true,
            radius: radius,
            type: isBackground ? .background : .gaussian,
            isProgressive: isProgressive,
            progressiveFrom: isProgressive ? progressiveFrom : nil,
            progressiveTo: isProgressive ? progressiveTo : nil,
            progressiveStartRadiusRatio: isProgressive ? progressiveStartRatio : nil
        )
    }

    private static func parseGlassBlur(_ effect: [String: KiwiValue]) -> FigBlur? {
        let radius = parseDouble(effect["radius"]) ?? 4.0
        let refractionRadius = parseDouble(effect["refractionRadius"]) ?? 20.0
        let chromaticAberration = parseDouble(effect["chromaticAberration"]) ?? 1.0

        return FigBlur(
            isEnabled: parseBool(effect["visible"]) ?? true,
            radius: radius * 0.5,
            type: .gaussian,
            isCustomGlass: true,
            glassDistortion: refractionRadius * 0.01,
            glassDepth: refractionRadius * 0.02,
            glassChromaticAberrationMultiplier: max(0, chromaticAberration - 1)
        )
    }

    private static func rotatedStopPosition(_ position: Double, offset: Double) -> Double {
        var output = position + offset
        if output > 1 { output -= 1 }
        else if output < 0 { output += 1 }
        if output < 0 { output += 1 }
        return output
    }

    private static func scaledDistance(from a: _Point2D, to b: _Point2D, xScale: Double) -> Double {
        let dx = (a.x - b.x) * xScale
        let dy = a.y - b.y
        return (dx * dx + dy * dy).squareRoot()
    }

    private static func safeDivide(_ numerator: Double, by denominator: Double, fallback: Double) -> Double {
        guard denominator != 0 else { return fallback }
        return numerator / denominator
    }

    private static func parseAffineTransform(_ value: KiwiValue?) -> _AffineTransform2D? {
        guard let value else { return nil }
        if let object = value.objectValue,
           let m00 = parseDouble(object["m00"]),
           let m01 = parseDouble(object["m01"]),
           let m02 = parseDouble(object["m02"]),
           let m10 = parseDouble(object["m10"]),
           let m11 = parseDouble(object["m11"]),
           let m12 = parseDouble(object["m12"]) {
            return _AffineTransform2D(m00: m00, m01: m01, m02: m02, m10: m10, m11: m11, m12: m12)
        }

        if let rows = value.arrayValue, rows.count >= 2,
           let row0 = rows[0].arrayValue, row0.count >= 3,
           let row1 = rows[1].arrayValue, row1.count >= 3,
           let m00 = parseDouble(row0[0]), let m01 = parseDouble(row0[1]), let m02 = parseDouble(row0[2]),
           let m10 = parseDouble(row1[0]), let m11 = parseDouble(row1[1]), let m12 = parseDouble(row1[2]) {
            return _AffineTransform2D(m00: m00, m01: m01, m02: m02, m10: m10, m11: m11, m12: m12)
        }

        return nil
    }

    private static func figTransform(_ transform: _AffineTransform2D) -> FigAffineTransform {
        FigAffineTransform(
            m00: transform.m00,
            m01: transform.m01,
            m02: transform.m02,
            m10: transform.m10,
            m11: transform.m11,
            m12: transform.m12
        )
    }

    private static func parseBorderPosition(_ value: KiwiValue?) -> FigBorderPosition? {
        guard let string = value?.stringValue else { return nil }
        switch string {
        case "CENTER":
            return .center
        case "INSIDE":
            return .inside
        case "OUTSIDE":
            return .outside
        default:
            return nil
        }
    }

    private static func parseLineCapStyle(_ value: KiwiValue?) -> FigLineCapStyle? {
        guard let string = value?.stringValue else { return nil }
        switch string {
        case "NONE":
            return .butt
        case "ROUND":
            return .round
        case "SQUARE", "LINE_ARROW", "ARROW_LINES", "TRIANGLE_ARROW", "TRIANGLE_FILLED":
            return .square
        default:
            return nil
        }
    }

    private static func parseLineJoinStyle(_ value: KiwiValue?) -> FigLineJoinStyle? {
        guard let string = value?.stringValue else { return nil }
        switch string {
        case "MITER":
            return .miter
        case "ROUND":
            return .round
        case "BEVEL":
            return .bevel
        default:
            return nil
        }
    }

    private static func parseWindingRule(_ value: KiwiValue?) -> FigWindingRule? {
        guard let string = value?.stringValue else { return nil }
        switch string {
        case "NONZERO":
            return .nonZero
        case "ODD", "EVENODD", "EVEN_ODD":
            return .evenOdd
        default:
            return nil
        }
    }

    private static func parseNumberArray(_ value: KiwiValue?) -> [Double] {
        guard let array = value?.arrayValue else { return [] }
        return array.compactMap(parseDouble)
    }

    private static func parseBlendMode(_ value: KiwiValue?) -> FigBlendMode? {
        guard let string = value?.stringValue else { return nil }
        switch string {
        case "PASS_THROUGH", "NORMAL":
            return .normal
        case "DARKEN":
            return .darken
        case "MULTIPLY":
            return .multiply
        case "COLOR_BURN":
            return .colorBurn
        case "LIGHTEN":
            return .lighten
        case "SCREEN":
            return .screen
        case "COLOR_DODGE":
            return .colorDodge
        case "OVERLAY":
            return .overlay
        case "SOFT_LIGHT":
            return .softLight
        case "HARD_LIGHT":
            return .hardLight
        case "DIFFERENCE":
            return .difference
        case "EXCLUSION":
            return .exclusion
        case "HUE":
            return .hue
        case "SATURATION":
            return .saturation
        case "COLOR":
            return .color
        case "LUMINOSITY":
            return .luminosity
        case "LINEAR_BURN":
            return .plusDarker
        case "LINEAR_DODGE":
            return .plusLighter
        default:
            return nil
        }
    }

    private static func parseUInt32(_ value: KiwiValue?) -> UInt32? {
        guard let value else { return nil }
        switch value {
        case .uint(let v):
            return v
        case .int(let v):
            return v >= 0 ? UInt32(v) : nil
        case .uint64(let v):
            return v <= UInt64(UInt32.max) ? UInt32(v) : nil
        case .int64(let v):
            return v >= 0 && v <= Int64(UInt32.max) ? UInt32(v) : nil
        case .string(let v):
            guard v.unicodeScalars.count == 1, let scalar = v.unicodeScalars.first else { return nil }
            return UInt32(scalar.value)
        default:
            return nil
        }
    }

    private static func parseInt(_ value: KiwiValue?) -> Int? {
        guard let value else { return nil }
        switch value {
        case .int(let v):
            return Int(v)
        case .uint(let v):
            return Int(v)
        case .int64(let v):
            guard v >= Int64(Int.min), v <= Int64(Int.max) else { return nil }
            return Int(v)
        case .uint64(let v):
            guard v <= UInt64(Int.max) else { return nil }
            return Int(v)
        default:
            return nil
        }
    }

    private static func parseByteArray(_ value: KiwiValue?) -> [UInt8]? {
        guard let value else { return nil }
        switch value {
        case .array(let values):
            let bytes = values.compactMap(parseUInt8)
            return bytes.count == values.count ? bytes : nil
        default:
            return nil
        }
    }

    private static func parseUInt8(_ value: KiwiValue) -> UInt8? {
        switch value {
        case .byte(let v):
            return v
        case .uint(let v):
            return v <= UInt32(UInt8.max) ? UInt8(v) : nil
        case .int(let v):
            return v >= 0 && v <= Int32(UInt8.max) ? UInt8(v) : nil
        default:
            return nil
        }
    }

    private static func parseDouble(_ value: KiwiValue?) -> Double? {
        guard let value else { return nil }
        switch value {
        case .float(let v):
            return v
        case .int(let v):
            return Double(v)
        case .uint(let v):
            return Double(v)
        case .int64(let v):
            return Double(v)
        case .uint64(let v):
            return Double(v)
        default:
            return nil
        }
    }

    private static func parseBool(_ value: KiwiValue?) -> Bool? {
        guard let value else { return nil }
        if case .bool(let v) = value { return v }
        return nil
    }

}

private struct _Point2D {
    var x: Double
    var y: Double
}

private struct _AffineTransform2D {
    var m00: Double
    var m01: Double
    var m02: Double
    var m10: Double
    var m11: Double
    var m12: Double

    func inverted() -> _AffineTransform2D? {
        let det = (m00 * m11) - (m01 * m10)
        guard det != 0 else { return nil }

        let inv00 = m11 / det
        let inv01 = -m01 / det
        let inv10 = -m10 / det
        let inv11 = m00 / det
        let inv02 = ((m01 * m12) - (m11 * m02)) / det
        let inv12 = ((m10 * m02) - (m00 * m12)) / det

        return _AffineTransform2D(
            m00: inv00,
            m01: inv01,
            m02: inv02,
            m10: inv10,
            m11: inv11,
            m12: inv12
        )
    }

    func applying(x: Double, y: Double) -> _Point2D {
        _Point2D(
            x: (m00 * x) + (m01 * y) + m02,
            y: (m10 * x) + (m11 * y) + m12
        )
    }
}
