import Foundation

public struct SketchBundleBuildOptions: Equatable, Sendable {
    public var forceConvertImages: Bool

    public init(forceConvertImages: Bool = false) {
        self.forceConvertImages = forceConvertImages
    }
}

public struct SketchBundleBuildWarning: Equatable, Sendable {
    public var code: String
    public var sourceName: String
    public var detail: String?

    public init(code: String, sourceName: String, detail: String? = nil) {
        self.code = code
        self.sourceName = sourceName
        self.detail = detail
    }

    public var message: String {
        switch code {
        case "IMG001":
            return "[IMG001] \(sourceName) appears to be corrupted in the .fig file, it will not be converted. Try passing --force-convert-images to try to convert it anyway"
        case "IMG002":
            return "[IMG002] \(sourceName) appears to be corrupted in the .fig file, it will not be converted"
        case "IMG003":
            return "[IMG003] \(sourceName) is missing from the .fig file, it will not be converted"
        case "IMG004":
            if let detail, !detail.isEmpty {
                return "[IMG004] \(sourceName) appears to be corrupted in the .fig file (\(detail)), it will not be converted"
            }
            return "[IMG004] \(sourceName) appears to be corrupted in the .fig file, it will not be converted"
        default:
            return "[\(code)] \(sourceName)"
        }
    }
}

public struct SketchBundleBuildResult: Equatable, Sendable {
    public var bundle: SketchBundle
    public var warnings: [SketchBundleBuildWarning]
    public var fontWarningMessages: [String]

    public init(
        bundle: SketchBundle,
        warnings: [SketchBundleBuildWarning],
        fontWarningMessages: [String] = []
    ) {
        self.bundle = bundle
        self.warnings = warnings
        self.fontWarningMessages = fontWarningMessages
    }
}

public enum SketchBundleBuilder {
    public static func build(
        from document: ConversionDocument,
        salt: Data,
        assets: ConversionAssets = .init()
    ) -> SketchBundle {
        buildResult(from: document, salt: salt, assets: assets).bundle
    }

    public static func buildResult(
        from document: ConversionDocument,
        salt: Data,
        assets: ConversionAssets = .init(),
        options: SketchBundleBuildOptions = .init()
    ) -> SketchBundleBuildResult {
        buildResult(
            from: document,
            salt: salt,
            assets: assets,
            options: options,
            fontResolverEnvironment: .live
        )
    }

    static func buildResult(
        from document: ConversionDocument,
        salt: Data,
        assets: ConversionAssets = .init(),
        options: SketchBundleBuildOptions = .init(),
        fontResolverEnvironment: FontCacheResolver.Environment
    ) -> SketchBundleBuildResult {
        precondition(!document.pages.isEmpty, "ConversionDocument must contain at least one page")

        var pageEntries: [SketchBundle.Entry] = []
        var documentPageRefs: [SketchJSONValue] = []
        var metaPageEntries: [(String, SketchJSONValue?)] = []
        var userPageViewports: [(String, SketchJSONValue?)] = []
        let preparedImages = prepareImageAssets(for: document, assets: assets, options: options)
        let preparedFonts = FontCacheResolver.prepareFontAssets(
            for: document,
            environment: fontResolverEnvironment
        )

        for page in document.pages {
            let pageID = ConverterUtils.genObjectID(figID: page.guid, salt: salt, suffix: page.idSuffix)
            let pagePathWithExtension = "pages/\(pageID).json"
            let pageRefPath = "pages/\(pageID)"

            let pageValue: SketchJSONValue = .object(
                SketchJSONObject([
                    ("_class", .string("page")),
                    ("do_objectID", .string(pageID)),
                    ("name", .string(page.name)),
                    ("layers", .array(page.layers.map { layerJSON($0, salt: salt, imageRefs: preparedImages.refsBySourceName) })),
                ])
            )

            pageEntries.append(
                .init(path: pagePathWithExtension, data: SketchJSONWriter.serialize(pageValue))
            )

            documentPageRefs.append(
                .object(SketchJSONObject([
                    ("_class", .string("MSJSONFileReference")),
                    ("_ref_class", .string("MSImmutablePage")),
                    ("_ref", .string(pageRefPath)),
                ]))
            )

            metaPageEntries.append(
                (pageID, .object(SketchJSONObject([
                    ("name", .string(page.name)),
                    ("artboards", .object(SketchJSONObject(metaArtboardsJSON(for: page.layers, salt: salt)))),
                ])))
            )

            userPageViewports.append((pageID, defaultViewportJSON(for: page.layers)))
        }

        let documentValue: SketchJSONValue = .object(
            SketchJSONObject([
                ("_class", .string("document")),
                ("do_objectID", .string(ConverterUtils.genObjectID(figID: [0, 0], salt: salt, suffix: Data("document".utf8)))),
                ("assets", .object(SketchJSONObject([
                    ("_class", .string("assetCollection")),
                    ("do_objectID", .string(ConverterUtils.genObjectID(figID: [0, 0], salt: salt, suffix: Data("assetCollection".utf8)))),
                    ("imageCollection", .object(SketchJSONObject([
                        ("_class", .string("imageCollection")),
                        ("images", .object(SketchJSONObject([]))),
                    ]))),
                    ("colorAssets", .array([])),
                    ("gradientAssets", .array([])),
                    ("images", .array([])),
                    ("colors", .array([])),
                    ("gradients", .array([])),
                    ("exportPresets", .array([])),
                ]))),
                ("colorSpace", .int(1)),
                ("currentPageIndex", .int(0)),
                ("foreignLayerStyles", .array([])),
                ("foreignSymbols", .array([])),
                ("foreignTextStyles", .array([])),
                ("foreignSwatches", .array([])),
                ("layerStyles", .object(SketchJSONObject([
                    ("_class", .string("sharedStyleContainer")),
                    ("do_objectID", .string(ConverterUtils.genObjectID(figID: [0, 0], salt: salt, suffix: Data("sharedStyleContainer".utf8)))),
                    ("objects", .array([])),
                ]))),
                ("layerSymbols", .object(SketchJSONObject([
                    ("_class", .string("symbolContainer")),
                    ("do_objectID", .string(ConverterUtils.genObjectID(figID: [0, 0], salt: salt, suffix: Data("symbolContainer".utf8)))),
                    ("objects", .array([])),
                ]))),
                ("layerTextStyles", .object(SketchJSONObject([
                    ("_class", .string("sharedTextStyleContainer")),
                    ("do_objectID", .string(ConverterUtils.genObjectID(figID: [0, 0], salt: salt, suffix: Data("sharedTextStyleContainer".utf8)))),
                    ("objects", .array([])),
                ]))),
                ("perDocumentLibraries", .array([])),
                ("sharedSwatches", .object(SketchJSONObject([
                    ("_class", .string("swatchContainer")),
                    ("do_objectID", .string(ConverterUtils.genObjectID(figID: [0, 0], salt: salt, suffix: Data("swatchContainer".utf8)))),
                    ("objects", .array([])),
                ]))),
                ("fontReferences", .array(preparedFonts.references)),
                ("documentState", .object(SketchJSONObject([
                    ("_class", .string("documentState")),
                ]))),
                ("pages", .array(documentPageRefs)),
            ])
        )

        let userValue: SketchJSONValue = .object(
            SketchJSONObject([
                ("document", .object(SketchJSONObject([
                    ("pageListHeight", .int(200)),
                    ("pageListCollapsed", .int(0)),
                    ("expandedSymbolPathsInSidebar", .array([])),
                    ("expandedTextStylePathsInPopover", .array([])),
                    ("libraryListCollapsed", .int(0)),
                ]))),
            ] + userPageViewports)
        )

        let createdMetaValue: SketchJSONValue = .object(
            SketchJSONObject([
                ("commit", .string("1899e24f63af087a9dd3c66f73b492b72c27c2c8")),
                ("appVersion", .string("2025.1")),
                ("build", .int(199630)),
                ("app", .string("com.bohemiancoding.sketch3")),
                ("compatibilityVersion", .int(99)),
                ("coeditCompatibilityVersion", .int(164)),
                ("version", .int(164)),
                ("variant", .string("NONAPPSTORE")),
            ])
        )

        let metaValue: SketchJSONValue = .object(
            SketchJSONObject([
                ("commit", .string("1899e24f63af087a9dd3c66f73b492b72c27c2c8")),
                ("pagesAndArtboards", .object(SketchJSONObject(metaPageEntries))),
                ("version", .int(164)),
                ("compatibilityVersion", .int(99)),
                ("coeditCompatibilityVersion", .int(164)),
                ("app", .string("com.bohemiancoding.sketch3")),
                ("autosaved", .int(0)),
                ("variant", .string("NONAPPSTORE")),
                ("created", createdMetaValue),
                ("saveHistory", .array([.string("NONAPPSTORE.199630")])),
                ("appVersion", .string("2025.1")),
                ("build", .int(199630)),
            ])
        )

        let bundle = SketchBundle(entries:
            preparedImages.entries.sorted(by: { $0.path < $1.path }) +
            pageEntries +
            preparedFonts.entries +
            [
            .init(path: "document.json", data: SketchJSONWriter.serialize(documentValue)),
            .init(path: "user.json", data: SketchJSONWriter.serialize(userValue)),
            .init(path: "meta.json", data: SketchJSONWriter.serialize(metaValue)),
            ]
        )
        return SketchBundleBuildResult(
            bundle: bundle,
            warnings: preparedImages.warnings,
            fontWarningMessages: preparedFonts.warningMessages
        )
    }


}
