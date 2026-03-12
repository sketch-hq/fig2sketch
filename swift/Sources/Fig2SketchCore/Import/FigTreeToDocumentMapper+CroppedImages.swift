import FigFormat
import Foundation

extension FigTreeToDocumentMapper {
    static func rectangleOrCroppedImageGroup(
        for node: FigNode,
        effectiveStyle: FigLayerStyle?,
        x: Double,
        y: Double,
        width: Double,
        height: Double,
        rotation: Double
    ) -> [ConversionLayer] {
        guard let style = effectiveStyle else {
            return [.rectangle(
                ConversionRectangle(
                    guid: node.guid,
                    name: node.name,
                    x: x,
                    y: y,
                    width: width,
                    height: height,
                    rotation: rotation,
                    style: nil
                )
            )]
        }

        let croppedImageFills: [FigPaint] = style.fills.filter {
            if case .image(let image) = $0.kind { return image.hasCropTransform }
            return false
        }
        guard !croppedImageFills.isEmpty else {
            return [.rectangle(
                ConversionRectangle(
                    guid: node.guid,
                    name: node.name,
                    x: x,
                    y: y,
                    width: width,
                    height: height,
                    rotation: rotation,
                    style: mapRenderableStyle(style)
                )
            )]
        }

        let maskStyle = styleWithoutCroppedImageFills(style)
        let maskRect = ConversionRectangle(
            guid: derivedGUID(node.guid, extra: [0, 0]),
            name: node.name,
            x: 0,
            y: 0,
            width: width,
            height: height,
            hasClippingMask: true,
            clippingMaskMode: .outline,
            style: maskStyle.map(mapRenderableStyle)
        )

        let imageLayers: [ConversionLayer] = croppedImageFills.enumerated().map { index, paint in
            let imageGeometry = cropImageGeometry(
                nodeWidth: width,
                nodeHeight: height,
                paint: paint
            )
            return .rectangle(
                ConversionRectangle(
                    guid: derivedGUID(node.guid, extra: [1, UInt32(index)]),
                    name: "\(node.name) (cropped image)",
                    x: imageGeometry.x,
                    y: imageGeometry.y,
                    width: imageGeometry.width,
                    height: imageGeometry.height,
                    rotation: imageGeometry.rotationDegrees,
                    style: ConversionLayerStyle(
                        fills: [mapPaint(paint)],
                        blendMode: .normal,
                        blendModeWasExplicit: false,
                        blendModeNeedsOpacityNudge: false,
                        opacity: 1
                    )
                )
            )
        }

        let group = ConversionGroup(
            guid: node.guid,
            name: "\(node.name) (crop group)",
            x: x,
            y: y,
            width: width,
            height: height,
            rotation: rotation,
            layers: [.rectangle(maskRect)] + imageLayers
        )
        return [.group(group)]
    }

    private static func styleWithoutCroppedImageFills(_ style: FigLayerStyle) -> FigLayerStyle? {
        let remainingFills = style.fills.filter {
            if case .image(let image) = $0.kind { return !image.hasCropTransform }
            return true
        }
        let rewritten = FigLayerStyle(
            fills: remainingFills,
            borders: style.borders,
            blurs: style.blurs,
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
        return rewritten.isDefault ? nil : rewritten
    }

    private struct CropImageGeometry {
        var x: Double
        var y: Double
        var width: Double
        var height: Double
        var rotationDegrees: Double
    }

    private static func cropImageGeometry(nodeWidth: Double, nodeHeight: Double, paint: FigPaint) -> CropImageGeometry {
        guard case .image(let image) = paint.kind,
              let transform = image.transform,
              let inv = Affine2D(transform).inverted() else {
            return CropImageGeometry(x: 0, y: 0, width: nodeWidth, height: nodeHeight, rotationDegrees: 0)
        }

        let iw = image.originalImageWidth ?? nodeWidth
        let ih = image.originalImageHeight ?? nodeHeight
        if iw == 0 || ih == 0 {
            return CropImageGeometry(x: 0, y: 0, width: nodeWidth, height: nodeHeight, rotationDegrees: 0)
        }

        let layerScale = Affine2D.scale(x: nodeWidth, y: nodeHeight)
        let imageScale = Affine2D.scale(x: 1.0 / iw, y: 1.0 / ih)
        let transformed = layerScale.concatenating(inv).concatenating(imageScale)

        let width = hypot(transformed.m00 * iw, transformed.m10 * iw)
        let height = hypot(transformed.m01 * ih, transformed.m11 * ih)
        if width == 0 || height == 0 {
            return CropImageGeometry(x: 0, y: 0, width: nodeWidth, height: nodeHeight, rotationDegrees: 0)
        }

        let normalizeScale = Affine2D.scale(x: iw / width, y: ih / height)
        let final = transformed.concatenating(normalizeScale)

        let halfX = width / 2
        let halfY = height / 2
        let rotatedCenterToOriginX = (final.m00 * halfX) + (final.m01 * halfY)
        let rotatedCenterToOriginY = (final.m10 * halfX) + (final.m11 * halfY)
        let x = final.m02 + (rotatedCenterToOriginX - halfX)
        let y = final.m12 + (rotatedCenterToOriginY - halfY)
        let rotation = atan2(final.m10, final.m00) * 180 / .pi

        return CropImageGeometry(x: x, y: y, width: width, height: height, rotationDegrees: rotation)
    }

    static func derivedGUID(_ base: [UInt32], extra: [UInt32]) -> [UInt32] {
        base + extra
    }
}

private struct Affine2D {
    var m00: Double
    var m01: Double
    var m02: Double
    var m10: Double
    var m11: Double
    var m12: Double

    init(_ t: FigAffineTransform) {
        self.m00 = t.m00
        self.m01 = t.m01
        self.m02 = t.m02
        self.m10 = t.m10
        self.m11 = t.m11
        self.m12 = t.m12
    }

    static func scale(x: Double, y: Double) -> Affine2D {
        Affine2D(m00: x, m01: 0, m02: 0, m10: 0, m11: y, m12: 0)
    }

    init(m00: Double, m01: Double, m02: Double, m10: Double, m11: Double, m12: Double) {
        self.m00 = m00; self.m01 = m01; self.m02 = m02
        self.m10 = m10; self.m11 = m11; self.m12 = m12
    }

    func inverted() -> Affine2D? {
        let det = (m00 * m11) - (m01 * m10)
        guard det != 0 else { return nil }
        return Affine2D(
            m00: m11 / det,
            m01: -m01 / det,
            m02: ((m01 * m12) - (m11 * m02)) / det,
            m10: -m10 / det,
            m11: m00 / det,
            m12: ((m10 * m02) - (m00 * m12)) / det
        )
    }

    func concatenating(_ rhs: Affine2D) -> Affine2D {
        Affine2D(
            m00: (m00 * rhs.m00) + (m01 * rhs.m10),
            m01: (m00 * rhs.m01) + (m01 * rhs.m11),
            m02: (m00 * rhs.m02) + (m01 * rhs.m12) + m02,
            m10: (m10 * rhs.m00) + (m11 * rhs.m10),
            m11: (m10 * rhs.m01) + (m11 * rhs.m11),
            m12: (m10 * rhs.m02) + (m11 * rhs.m12) + m12
        )
    }
}
