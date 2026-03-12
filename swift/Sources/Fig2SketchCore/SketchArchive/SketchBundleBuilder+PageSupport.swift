import Foundation

extension SketchBundleBuilder {
    static func metaArtboardsJSON(for layers: [ConversionLayer], salt: Data) -> [(String, SketchJSONValue?)] {
        var entries: [(String, SketchJSONValue?)] = []
        entries.reserveCapacity(layers.count)
        for layer in layers {
            switch layer {
            case .artboard(let artboard):
                let objectID = ConverterUtils.genObjectID(figID: artboard.guid, salt: salt)
                entries.append((objectID, .object(SketchJSONObject([
                    ("name", .string(artboard.name)),
                ]))))
            case .group(let group) where group.source == .frame:
                let objectID = ConverterUtils.genObjectID(figID: group.guid, salt: salt)
                entries.append((objectID, .object(SketchJSONObject([
                    ("name", .string(group.name)),
                ]))))
            case .symbolMaster(let master):
                let objectID = ConverterUtils.genObjectID(figID: master.guid, salt: salt, suffix: Data("symbol_master".utf8))
                entries.append((objectID, .object(SketchJSONObject([
                    ("name", .string(master.name)),
                ]))))
            case .rectangle, .shapePath, .group, .symbolInstance, .text:
                continue
            }
        }
        return entries
    }

    static func defaultViewportJSON(for layers: [ConversionLayer]) -> SketchJSONValue {
        guard let bounds = pageBounds(for: layers) else {
            return .object(SketchJSONObject([
                ("scrollOrigin", .object(SketchJSONObject([
                    ("x", .double(0)),
                    ("y", .double(0)),
                ]))),
                ("zoomValue", .double(1)),
            ]))
        }

        let width = bounds.maxX - bounds.minX
        let height = bounds.maxY - bounds.minY
        guard width > 0, height > 0 else {
            return .object(SketchJSONObject([
                ("scrollOrigin", .object(SketchJSONObject([
                    ("x", .double(0)),
                    ("y", .double(0)),
                ]))),
                ("zoomValue", .double(1)),
            ]))
        }

        let canvasWidth = 1200.0
        let canvasHeight = 900.0
        let scale = min(canvasWidth / width, canvasHeight / height) * 0.8

        let x = bounds.minX - ((canvasWidth - width * scale) / scale / 2)
        let y = bounds.minY - ((canvasHeight - height * scale) / scale / 2)
        let originX = -x * scale
        let originY = -y * scale

        return .object(SketchJSONObject([
            ("scrollOrigin", .object(SketchJSONObject([
                ("x", .double(originX)),
                ("y", .double(originY)),
            ]))),
            ("zoomValue", .double(scale)),
        ]))
    }

    private static func pageBounds(for layers: [ConversionLayer]) -> (minX: Double, maxX: Double, minY: Double, maxY: Double)? {
        var bounds: (minX: Double, maxX: Double, minY: Double, maxY: Double)?
        for layer in layers {
            guard let layerBounds = layerBounds(layer) else { continue }
            if let existing = bounds {
                bounds = (
                    min(existing.minX, layerBounds.minX),
                    max(existing.maxX, layerBounds.maxX),
                    min(existing.minY, layerBounds.minY),
                    max(existing.maxY, layerBounds.maxY)
                )
            } else {
                bounds = layerBounds
            }
        }
        return bounds
    }

    private static func layerBounds(_ layer: ConversionLayer) -> (minX: Double, maxX: Double, minY: Double, maxY: Double)? {
        let frame: (x: Double, y: Double, width: Double, height: Double)
        switch layer {
        case .rectangle(let rect):
            frame = (rect.x, rect.y, rect.width, rect.height)
        case .shapePath(let shape):
            frame = (shape.x, shape.y, shape.width, shape.height)
        case .group(let group):
            frame = (group.x, group.y, group.width, group.height)
        case .artboard(let artboard):
            frame = (artboard.x, artboard.y, artboard.width, artboard.height)
        case .symbolMaster(let master):
            frame = (master.x, master.y, master.width, master.height)
        case .symbolInstance(let instance):
            frame = (instance.x, instance.y, instance.width, instance.height)
        case .text(let text):
            frame = (text.x, text.y, text.width, text.height)
        }
        guard frame.width.isFinite, frame.height.isFinite, frame.x.isFinite, frame.y.isFinite else { return nil }
        return (
            minX: frame.x,
            maxX: frame.x + frame.width,
            minY: frame.y,
            maxY: frame.y + frame.height
        )
    }


}
