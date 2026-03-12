import Foundation

public struct ConversionColor: Equatable, Sendable {
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

public struct ConversionPoint: Equatable, Sendable {
    public var x: Double
    public var y: Double

    public init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }
}

public enum ConversionCurveMode: Int, Equatable, Sendable {
    case undefined = 0
    case straight = 1
    case mirrored = 2
    case asymmetric = 3
    case disconnected = 4
}

public enum ConversionShapeCornerStyle: Int, Equatable, Sendable {
    case rounded = 0
    case roundedInverted = 1
    case angled = 2
    case squared = 3
}

public enum ConversionPointRadiusBehavior: Int, Equatable, Sendable {
    case v0 = 0
    case v1 = 1
    case v1Smooth = 2
}

public struct ConversionShapePoint: Equatable, Sendable {
    public var curveFrom: ConversionPoint
    public var curveTo: ConversionPoint
    public var point: ConversionPoint
    public var cornerRadius: Double
    public var cornerStyle: ConversionShapeCornerStyle
    public var hasCurveFrom: Bool
    public var hasCurveTo: Bool
    public var curveMode: ConversionCurveMode

    public init(
        curveFrom: ConversionPoint,
        curveTo: ConversionPoint,
        point: ConversionPoint,
        cornerRadius: Double = 0,
        cornerStyle: ConversionShapeCornerStyle = .rounded,
        hasCurveFrom: Bool = false,
        hasCurveTo: Bool = false,
        curveMode: ConversionCurveMode = .straight
    ) {
        self.curveFrom = curveFrom
        self.curveTo = curveTo
        self.point = point
        self.cornerRadius = cornerRadius
        self.cornerStyle = cornerStyle
        self.hasCurveFrom = hasCurveFrom
        self.hasCurveTo = hasCurveTo
        self.curveMode = curveMode
    }

    public static func straight(
        _ point: ConversionPoint,
        cornerRadius: Double = 0,
        cornerStyle: ConversionShapeCornerStyle = .rounded,
        curveMode: ConversionCurveMode = .straight
    ) -> ConversionShapePoint {
        ConversionShapePoint(
            curveFrom: point,
            curveTo: point,
            point: point,
            cornerRadius: cornerRadius,
            cornerStyle: cornerStyle,
            hasCurveFrom: false,
            hasCurveTo: false,
            curveMode: curveMode
        )
    }
}

public struct ConversionGradientStop: Equatable, Sendable {
    public var color: ConversionColor
    public var position: Double

    public init(color: ConversionColor, position: Double) {
        self.color = color
        self.position = position
    }
}

public enum ConversionGradientType: Int, Equatable, Sendable {
    case linear = 0
    case radial = 1
    case angular = 2
}

public struct ConversionGradient: Equatable, Sendable {
    public var type: ConversionGradientType
    public var from: ConversionPoint
    public var to: ConversionPoint
    public var ellipseLength: Double
    public var stops: [ConversionGradientStop]

    public init(
        type: ConversionGradientType,
        from: ConversionPoint,
        to: ConversionPoint,
        ellipseLength: Double = 0,
        stops: [ConversionGradientStop]
    ) {
        self.type = type
        self.from = from
        self.to = to
        self.ellipseLength = ellipseLength
        self.stops = stops
    }
}

public enum ConversionPatternFillType: Int, Equatable, Sendable {
    case tile = 0
    case fill = 1
    case stretch = 2
    case fit = 3
}

public struct ConversionImagePaint: Equatable, Sendable {
    public var sourceName: String
    public var patternFillType: ConversionPatternFillType
    public var patternTileScale: Double

    public init(sourceName: String, patternFillType: ConversionPatternFillType, patternTileScale: Double = 1) {
        self.sourceName = sourceName
        self.patternFillType = patternFillType
        self.patternTileScale = patternTileScale
    }
}

public enum ConversionBlurType: Int, Equatable, Sendable {
    case gaussian = 0
    case background = 3
}

public struct ConversionBlur: Equatable, Sendable {
    public var isEnabled: Bool
    public var radius: Double
    public var type: ConversionBlurType
    public var isProgressive: Bool
    public var progressiveFrom: ConversionPoint?
    public var progressiveTo: ConversionPoint?
    public var progressiveStartRadiusRatio: Double?
    public var isCustomGlass: Bool
    public var glassDistortion: Double
    public var glassDepth: Double
    public var glassChromaticAberrationMultiplier: Double

    public init(
        isEnabled: Bool = true,
        radius: Double,
        type: ConversionBlurType,
        isProgressive: Bool = false,
        progressiveFrom: ConversionPoint? = nil,
        progressiveTo: ConversionPoint? = nil,
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

public struct ConversionShadow: Equatable, Sendable {
    public var blurRadius: Double
    public var offsetX: Double
    public var offsetY: Double
    public var spread: Double
    public var isInnerShadow: Bool
    public var isEnabled: Bool
    public var color: ConversionColor

    public init(
        blurRadius: Double,
        offsetX: Double,
        offsetY: Double,
        spread: Double,
        isInnerShadow: Bool = false,
        isEnabled: Bool = true,
        color: ConversionColor
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

public enum ConversionCornerStyle: Int, Equatable, Sendable {
    case rounded = 0
    case smooth = 1
}

public struct ConversionStyleCorners: Equatable, Sendable {
    public var radii: [Double] // [topLeft, topRight, bottomRight, bottomLeft]
    public var style: ConversionCornerStyle

    public init(radii: [Double], style: ConversionCornerStyle) {
        self.radii = radii
        self.style = style
    }

    public var isDefault: Bool {
        radii.allSatisfy { $0 == 0 } && style == .rounded
    }
}

public enum ConversionLineCapStyle: Int, Equatable, Sendable {
    case butt = 0
    case round = 1
    case square = 2
}

public enum ConversionLineJoinStyle: Int, Equatable, Sendable {
    case miter = 0
    case round = 1
    case bevel = 2
}

public enum ConversionWindingRule: Int, Equatable, Sendable {
    case nonZero = 0
    case evenOdd = 1
}

public struct ConversionBorderOptions: Equatable, Sendable {
    public var lineCapStyle: ConversionLineCapStyle
    public var lineJoinStyle: ConversionLineJoinStyle
    public var dashPattern: [Double]

    public init(
        lineCapStyle: ConversionLineCapStyle = .butt,
        lineJoinStyle: ConversionLineJoinStyle = .miter,
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

public enum ConversionBlendMode: Int, Equatable, Sendable {
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

public enum ConversionBorderPosition: Equatable, Sendable {
    case center
    case inside
    case outside
}

public enum ConversionPaintKind: Equatable, Sendable {
    case solid(ConversionColor)
    case gradient(ConversionGradient)
    case image(ConversionImagePaint)
    case unsupported(type: String)
}

public struct ConversionPaint: Equatable, Sendable {
    public var kind: ConversionPaintKind
    public var isEnabled: Bool
    public var blendMode: ConversionBlendMode
    public var opacity: Double

    public init(
        kind: ConversionPaintKind,
        isEnabled: Bool = true,
        blendMode: ConversionBlendMode = .normal,
        opacity: Double = 1
    ) {
        self.kind = kind
        self.isEnabled = isEnabled
        self.blendMode = blendMode
        self.opacity = opacity
    }
}

public struct ConversionBorder: Equatable, Sendable {
    public var paint: ConversionPaint
    public var thickness: Double
    public var position: ConversionBorderPosition

    public init(paint: ConversionPaint, thickness: Double, position: ConversionBorderPosition) {
        self.paint = paint
        self.thickness = thickness
        self.position = position
    }
}

public struct ConversionLayerStyle: Equatable, Sendable {
    public var fills: [ConversionPaint]
    public var borders: [ConversionBorder]
    public var blurs: [ConversionBlur]
    public var shadows: [ConversionShadow]
    public var borderOptions: ConversionBorderOptions
    public var miterLimit: Double
    public var windingRule: ConversionWindingRule
    public var startMarkerType: Int
    public var endMarkerType: Int
    public var startDecorationType: Int?
    public var endDecorationType: Int?
    public var corners: ConversionStyleCorners?
    public var blendMode: ConversionBlendMode
    public var blendModeWasExplicit: Bool
    public var blendModeNeedsOpacityNudge: Bool
    public var opacity: Double

    public init(
        fills: [ConversionPaint] = [],
        borders: [ConversionBorder] = [],
        blurs: [ConversionBlur] = [],
        shadows: [ConversionShadow] = [],
        borderOptions: ConversionBorderOptions = .init(),
        miterLimit: Double = 10,
        windingRule: ConversionWindingRule = .nonZero,
        startMarkerType: Int = 0,
        endMarkerType: Int = 0,
        startDecorationType: Int? = nil,
        endDecorationType: Int? = nil,
        corners: ConversionStyleCorners? = nil,
        blendMode: ConversionBlendMode = .normal,
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
        self.startMarkerType = startMarkerType
        self.endMarkerType = endMarkerType
        self.startDecorationType = startDecorationType
        self.endDecorationType = endDecorationType
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
            startMarkerType == 0 &&
            endMarkerType == 0 &&
            startDecorationType == nil &&
            endDecorationType == nil &&
            (corners == nil || corners?.isDefault == true) &&
            blendMode == .normal &&
            !blendModeWasExplicit &&
            !blendModeNeedsOpacityNudge &&
            opacity == 1
    }
}

public struct ConversionAssets: Equatable, Sendable {
    public var imagesBySourceName: [String: Data]

    public init(imagesBySourceName: [String: Data] = [:]) {
        self.imagesBySourceName = imagesBySourceName
    }
}

public struct ConversionDocument: Equatable, Sendable {
    public var pages: [ConversionPage]

    public init(pages: [ConversionPage]) {
        self.pages = pages
    }
}

public struct ConversionPage: Equatable, Sendable {
    public var guid: [UInt32]
    public var name: String
    public var layers: [ConversionLayer]
    public var idSuffix: Data

    public init(
        guid: [UInt32],
        name: String,
        layers: [ConversionLayer],
        idSuffix: Data = Data()
    ) {
        self.guid = guid
        self.name = name
        self.layers = layers
        self.idSuffix = idSuffix
    }
}

public enum ConversionLayer: Equatable, Sendable {
    case rectangle(ConversionRectangle)
    case shapePath(ConversionShapePath)
    case group(ConversionGroup)
    case artboard(ConversionArtboard)
    case symbolMaster(ConversionSymbolMaster)
    case symbolInstance(ConversionSymbolInstance)
    case text(ConversionText)
}

public enum ConversionClippingMaskMode: Int, Equatable, Sendable {
    case outline = 0
    case alpha = 1
}

public struct ConversionRectangle: Equatable, Sendable {
    public var guid: [UInt32]
    public var name: String
    public var x: Double
    public var y: Double
    public var width: Double
    public var height: Double
    public var rotation: Double
    public var hasClippingMask: Bool
    public var clippingMaskMode: ConversionClippingMaskMode
    public var style: ConversionLayerStyle?

    public init(
        guid: [UInt32],
        name: String,
        x: Double,
        y: Double,
        width: Double,
        height: Double,
        rotation: Double = 0,
        hasClippingMask: Bool = false,
        clippingMaskMode: ConversionClippingMaskMode = .outline,
        style: ConversionLayerStyle? = nil
    ) {
        self.guid = guid
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.hasClippingMask = hasClippingMask
        self.clippingMaskMode = clippingMaskMode
        self.style = style
    }
}

public struct ConversionPrototypeViewport: Equatable, Sendable {
    public var name: String
    public var size: ConversionPoint

    public init(name: String, size: ConversionPoint) {
        self.name = name
        self.size = size
    }
}

public struct ConversionFlowOverlaySettings: Equatable, Sendable {
    public var overlayAnchor: ConversionPoint
    public var sourceAnchor: ConversionPoint
    public var offset: ConversionPoint
    public var overlayType: Int

    public init(
        overlayAnchor: ConversionPoint,
        sourceAnchor: ConversionPoint,
        offset: ConversionPoint = .init(x: 0, y: 0),
        overlayType: Int = 0
    ) {
        self.overlayAnchor = overlayAnchor
        self.sourceAnchor = sourceAnchor
        self.offset = offset
        self.overlayType = overlayType
    }
}

public enum ConversionFlowDestination: Equatable, Sendable {
    case back
    case node([UInt32])
}

public struct ConversionFlowConnection: Equatable, Sendable {
    public var destination: ConversionFlowDestination
    public var overlaySettings: ConversionFlowOverlaySettings?
    public var animationType: Int
    public var maintainScrollPosition: Bool
    public var shouldCloseExistingOverlays: Bool

    public init(
        destination: ConversionFlowDestination,
        overlaySettings: ConversionFlowOverlaySettings? = nil,
        animationType: Int = 0,
        maintainScrollPosition: Bool = false,
        shouldCloseExistingOverlays: Bool = false
    ) {
        self.destination = destination
        self.overlaySettings = overlaySettings
        self.animationType = animationType
        self.maintainScrollPosition = maintainScrollPosition
        self.shouldCloseExistingOverlays = shouldCloseExistingOverlays
    }
}

public struct ConversionPrototypeInfo: Equatable, Sendable {
    public var isFlowHome: Bool
    public var overlayBackgroundInteraction: Int
    public var presentationStyle: Int
    public var overlaySettings: ConversionFlowOverlaySettings?
    public var prototypeViewport: ConversionPrototypeViewport?

    public init(
        isFlowHome: Bool = false,
        overlayBackgroundInteraction: Int = 0,
        presentationStyle: Int = 0,
        overlaySettings: ConversionFlowOverlaySettings? = nil,
        prototypeViewport: ConversionPrototypeViewport? = nil
    ) {
        self.isFlowHome = isFlowHome
        self.overlayBackgroundInteraction = overlayBackgroundInteraction
        self.presentationStyle = presentationStyle
        self.overlaySettings = overlaySettings
        self.prototypeViewport = prototypeViewport
    }
}

public struct ConversionGroup: Equatable, Sendable {
    public var guid: [UInt32]
    public var name: String
    public var x: Double
    public var y: Double
    public var width: Double
    public var height: Double
    public var rotation: Double
    public var layers: [ConversionLayer]
    public var style: ConversionLayerStyle?
    public var groupLayout: ConversionGroupLayout
    public var clippingBehavior: ConversionClippingBehavior
    public var topPadding: Double
    public var rightPadding: Double
    public var bottomPadding: Double
    public var leftPadding: Double
    public var paddingSelection: ConversionPaddingSelection
    public var grid: ConversionLayoutGrid?
    public var horizontalSizing: Int
    public var verticalSizing: Int
    public var kind: ConversionGroupKind
    public var source: ConversionGroupSource
    public var windingRule: ConversionWindingRule?
    public var flow: ConversionFlowConnection?
    public var prototypeInfo: ConversionPrototypeInfo?
    public var warningCodes: [String]

    public init(
        guid: [UInt32],
        name: String,
        x: Double,
        y: Double,
        width: Double,
        height: Double,
        rotation: Double = 0,
        layers: [ConversionLayer],
        style: ConversionLayerStyle? = nil,
        groupLayout: ConversionGroupLayout = .freeform,
        clippingBehavior: ConversionClippingBehavior = .default,
        topPadding: Double = 0,
        rightPadding: Double = 0,
        bottomPadding: Double = 0,
        leftPadding: Double = 0,
        paddingSelection: ConversionPaddingSelection = .paired,
        grid: ConversionLayoutGrid? = nil,
        horizontalSizing: Int = 1,
        verticalSizing: Int = 1,
        kind: ConversionGroupKind = .group,
        source: ConversionGroupSource = .group,
        windingRule: ConversionWindingRule? = nil,
        flow: ConversionFlowConnection? = nil,
        prototypeInfo: ConversionPrototypeInfo? = nil,
        warningCodes: [String] = []
    ) {
        self.guid = guid
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.layers = layers
        self.style = style
        self.groupLayout = groupLayout
        self.clippingBehavior = clippingBehavior
        self.topPadding = topPadding
        self.rightPadding = rightPadding
        self.bottomPadding = bottomPadding
        self.leftPadding = leftPadding
        self.paddingSelection = paddingSelection
        self.grid = grid
        self.horizontalSizing = horizontalSizing
        self.verticalSizing = verticalSizing
        self.kind = kind
        self.source = source
        self.windingRule = windingRule
        self.flow = flow
        self.prototypeInfo = prototypeInfo
        self.warningCodes = warningCodes
    }
}

public struct ConversionText: Equatable, Sendable {
    public var guid: [UInt32]
    public var name: String
    public var x: Double
    public var y: Double
    public var width: Double
    public var height: Double
    public var rotation: Double
    public var style: ConversionLayerStyle?
    public var characters: String
    public var attributeRuns: [ConversionTextAttributeRun]
    public var fontFamily: String?
    public var fontStyle: String?
    public var fontSize: Double?
    public var warningCodes: [String]

    public init(
        guid: [UInt32],
        name: String,
        x: Double,
        y: Double,
        width: Double,
        height: Double,
        rotation: Double = 0,
        style: ConversionLayerStyle? = nil,
        characters: String = "",
        attributeRuns: [ConversionTextAttributeRun] = [],
        fontFamily: String? = nil,
        fontStyle: String? = nil,
        fontSize: Double? = nil,
        warningCodes: [String] = []
    ) {
        self.guid = guid
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.style = style
        self.characters = characters
        self.attributeRuns = attributeRuns
        self.fontFamily = fontFamily
        self.fontStyle = fontStyle
        self.fontSize = fontSize
        self.warningCodes = warningCodes
    }
}

public struct ConversionTextFeatureSetting: Equatable, Sendable {
    public var typeIdentifier: Int
    public var selectorIdentifier: Int

    public init(typeIdentifier: Int, selectorIdentifier: Int) {
        self.typeIdentifier = typeIdentifier
        self.selectorIdentifier = selectorIdentifier
    }
}

public struct ConversionTextAttributeRun: Equatable, Sendable {
    public var location: Int
    public var length: Int
    public var fontName: String
    public var fontSize: Double
    public var color: ConversionColor
    public var kerning: Double?
    public var featureSettings: [ConversionTextFeatureSetting]

    public init(
        location: Int,
        length: Int,
        fontName: String,
        fontSize: Double,
        color: ConversionColor,
        kerning: Double? = nil,
        featureSettings: [ConversionTextFeatureSetting] = []
    ) {
        self.location = location
        self.length = length
        self.fontName = fontName
        self.fontSize = fontSize
        self.color = color
        self.kerning = kerning
        self.featureSettings = featureSettings
    }
}

public struct ConversionArtboard: Equatable, Sendable {
    public var guid: [UInt32]
    public var name: String
    public var x: Double
    public var y: Double
    public var width: Double
    public var height: Double
    public var rotation: Double
    public var layers: [ConversionLayer]
    public var style: ConversionLayerStyle?
    public var warningCodes: [String]

    public init(
        guid: [UInt32],
        name: String,
        x: Double,
        y: Double,
        width: Double,
        height: Double,
        rotation: Double = 0,
        layers: [ConversionLayer],
        style: ConversionLayerStyle? = nil,
        warningCodes: [String] = []
    ) {
        self.guid = guid
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.layers = layers
        self.style = style
        self.warningCodes = warningCodes
    }
}

public struct ConversionSymbolMaster: Equatable, Sendable {
    public var guid: [UInt32]
    public var name: String
    public var x: Double
    public var y: Double
    public var width: Double
    public var height: Double
    public var rotation: Double
    public var groupLayout: ConversionGroupLayout
    public var clippingBehavior: ConversionClippingBehavior
    public var topPadding: Double
    public var rightPadding: Double
    public var bottomPadding: Double
    public var leftPadding: Double
    public var paddingSelection: ConversionPaddingSelection
    public var grid: ConversionLayoutGrid?
    public var horizontalSizing: Int
    public var verticalSizing: Int
    public var flow: ConversionFlowConnection?
    public var prototypeInfo: ConversionPrototypeInfo?
    public var symbolIDGUID: [UInt32]
    public var layers: [ConversionLayer]
    public var style: ConversionLayerStyle?
    public var warningCodes: [String]

    public init(
        guid: [UInt32],
        name: String,
        x: Double,
        y: Double,
        width: Double,
        height: Double,
        rotation: Double = 0,
        groupLayout: ConversionGroupLayout = .freeform,
        clippingBehavior: ConversionClippingBehavior = .default,
        topPadding: Double = 0,
        rightPadding: Double = 0,
        bottomPadding: Double = 0,
        leftPadding: Double = 0,
        paddingSelection: ConversionPaddingSelection = .paired,
        grid: ConversionLayoutGrid? = nil,
        horizontalSizing: Int = 1,
        verticalSizing: Int = 1,
        flow: ConversionFlowConnection? = nil,
        prototypeInfo: ConversionPrototypeInfo? = nil,
        symbolIDGUID: [UInt32],
        layers: [ConversionLayer],
        style: ConversionLayerStyle? = nil,
        warningCodes: [String] = []
    ) {
        self.guid = guid
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.groupLayout = groupLayout
        self.clippingBehavior = clippingBehavior
        self.topPadding = topPadding
        self.rightPadding = rightPadding
        self.bottomPadding = bottomPadding
        self.leftPadding = leftPadding
        self.paddingSelection = paddingSelection
        self.grid = grid
        self.horizontalSizing = horizontalSizing
        self.verticalSizing = verticalSizing
        self.flow = flow
        self.prototypeInfo = prototypeInfo
        self.symbolIDGUID = symbolIDGUID
        self.layers = layers
        self.style = style
        self.warningCodes = warningCodes
    }
}

public struct ConversionSymbolOverrideValue: Equatable, Sendable {
    public var guidPath: [[UInt32]]
    public var kind: ConversionSymbolOverrideKind
    public var stringValue: String?
    public var guidValue: [UInt32]?

    public init(
        guidPath: [[UInt32]],
        kind: ConversionSymbolOverrideKind,
        stringValue: String? = nil,
        guidValue: [UInt32]? = nil
    ) {
        self.guidPath = guidPath
        self.kind = kind
        self.stringValue = stringValue
        self.guidValue = guidValue
    }
}

public enum ConversionSymbolOverrideKind: Equatable, Sendable {
    case stringValue
    case symbolID
}

public struct ConversionSymbolInstance: Equatable, Sendable {
    public var guid: [UInt32]
    public var name: String
    public var x: Double
    public var y: Double
    public var width: Double
    public var height: Double
    public var rotation: Double
    public var horizontalSizing: Int
    public var verticalSizing: Int
    public var symbolIDGUID: [UInt32]
    public var overrideValues: [ConversionSymbolOverrideValue]
    public var style: ConversionLayerStyle?
    public var warningCodes: [String]

    public init(
        guid: [UInt32],
        name: String,
        x: Double,
        y: Double,
        width: Double,
        height: Double,
        rotation: Double = 0,
        horizontalSizing: Int = 1,
        verticalSizing: Int = 1,
        symbolIDGUID: [UInt32],
        overrideValues: [ConversionSymbolOverrideValue] = [],
        style: ConversionLayerStyle? = nil,
        warningCodes: [String] = []
    ) {
        self.guid = guid
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.horizontalSizing = horizontalSizing
        self.verticalSizing = verticalSizing
        self.symbolIDGUID = symbolIDGUID
        self.overrideValues = overrideValues
        self.style = style
        self.warningCodes = warningCodes
    }
}

public struct ConversionShapePath: Equatable, Sendable {
    public var guid: [UInt32]
    public var name: String
    public var x: Double
    public var y: Double
    public var width: Double
    public var height: Double
    public var rotation: Double
    public var booleanOperation: Int
    public var isClosed: Bool
    public var points: [ConversionShapePoint]
    public var edited: Bool
    public var pointRadiusBehavior: ConversionPointRadiusBehavior
    public var style: ConversionLayerStyle?
    public var warningCodes: [String]

    public init(
        guid: [UInt32],
        name: String,
        x: Double,
        y: Double,
        width: Double,
        height: Double,
        rotation: Double = 0,
        booleanOperation: Int = -1,
        isClosed: Bool = true,
        points: [ConversionShapePoint] = [],
        edited: Bool = true,
        pointRadiusBehavior: ConversionPointRadiusBehavior = .v1,
        style: ConversionLayerStyle? = nil,
        warningCodes: [String] = []
    ) {
        self.guid = guid
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.booleanOperation = booleanOperation
        self.isClosed = isClosed
        self.points = points
        self.edited = edited
        self.pointRadiusBehavior = pointRadiusBehavior
        self.style = style
        self.warningCodes = warningCodes
    }
}

public enum ConversionGroupKind: Equatable, Sendable {
    case group
    case shapeGroup
}

public enum ConversionGroupSource: Equatable, Sendable {
    case group
    case frame
}

public enum ConversionGroupLayout: Equatable, Sendable {
    case freeform
    case inferred(
        flexDirection: Int,
        justifyContent: Int,
        alignItems: Int,
        allGuttersGap: Double
    )
}

public enum ConversionClippingBehavior: Int, Equatable, Sendable {
    case `default` = 0
    case clipToBounds = 1
    case none = 2
}

public enum ConversionPaddingSelection: Int, Equatable, Sendable {
    case paired = 0
    case individual = 1
}

public struct ConversionLayoutGrid: Equatable, Sendable {
    public var isEnabled: Bool
    public var gridSize: Double?
    public var thickGridTimes: Double?
    public var drawVertical: Bool
    public var totalWidth: Double?
    public var gutterWidth: Double?
    public var columnWidth: Double?
    public var numberOfColumns: Double?
    public var horizontalOffset: Double?
    public var drawHorizontal: Bool
    public var gutterHeight: Double?
    public var rowHeightMultiplication: Double?

    public init(
        isEnabled: Bool = true,
        gridSize: Double? = nil,
        thickGridTimes: Double? = nil,
        drawVertical: Bool = false,
        totalWidth: Double? = nil,
        gutterWidth: Double? = nil,
        columnWidth: Double? = nil,
        numberOfColumns: Double? = nil,
        horizontalOffset: Double? = nil,
        drawHorizontal: Bool = false,
        gutterHeight: Double? = nil,
        rowHeightMultiplication: Double? = nil
    ) {
        self.isEnabled = isEnabled
        self.gridSize = gridSize
        self.thickGridTimes = thickGridTimes
        self.drawVertical = drawVertical
        self.totalWidth = totalWidth
        self.gutterWidth = gutterWidth
        self.columnWidth = columnWidth
        self.numberOfColumns = numberOfColumns
        self.horizontalOffset = horizontalOffset
        self.drawHorizontal = drawHorizontal
        self.gutterHeight = gutterHeight
        self.rowHeightMultiplication = rowHeightMultiplication
    }
}
