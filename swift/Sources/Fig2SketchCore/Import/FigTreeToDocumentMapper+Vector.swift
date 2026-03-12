import FigFormat
import Foundation

extension FigTreeToDocumentMapper {
    static func convertVectorNode(
        node: FigNode,
        frame: NodeFrame,
        context: MappingContext
    ) throws -> [ConversionLayer] {
        guard let width = frame.width, let height = frame.height else { return [] }

        if let network = node.vectorNetwork {
            return try convertVectorNetworkNode(
                node: node,
                frame: frame,
                width: width,
                height: height,
                network: network,
                context: context
            )
        }

        if node.vectorHasExplicitNetwork, (node.vectorNetworkVertexCount ?? 0) == 0 {
            throw FigTreeToDocumentMapperError.shapePathWarning("SHP002", node.guid)
        }

        var pathStyle = effectiveStyle(for: node, context: context).map(mapRenderableStyle) ?? ConversionLayerStyle()
        applyMarkerOverrides(from: node, style: &pathStyle)

        let shapePath = ConversionShapePath(
            guid: derivedGUID(node.guid, extra: [7, 0]),
            name: node.name,
            x: 0,
            y: 0,
            width: width,
            height: height,
            style: pathStyle
        )

        let shapeGroup = ConversionGroup(
            guid: node.guid,
            name: node.name,
            x: frame.x,
            y: frame.y,
            width: width,
            height: height,
            rotation: frame.rotation,
            layers: [.shapePath(shapePath)],
            style: ConversionLayerStyle(fills: []),
            horizontalSizing: sizingBehaviour(for: node.horizontalConstraint),
            verticalSizing: sizingBehaviour(for: node.verticalConstraint),
            kind: .shapeGroup,
            windingRule: pathStyle.windingRule,
            warningCodes: context.warnings(for: node.guid)
        )
        return [.group(shapeGroup)]
    }

    private struct VectorRegionSegments {
        var loops: [[WorkingVectorSegment]]
        var styleOverride: FigVectorStyleOverride?
        var windingRule: ConversionWindingRule
    }

    private struct WorkingVectorSegment {
        var start: UInt32
        var end: UInt32
        var tangentStart: VectorVertex<NeverStyle>
        var tangentEnd: VectorVertex<NeverStyle>

        init(_ segment: VectorSegment) {
            start = segment.start
            end = segment.end
            tangentStart = segment.tangentStart
            tangentEnd = segment.tangentEnd
        }

        mutating func swapEndpoints() {
            let oldStart = start
            start = end
            end = oldStart

            let oldTangentStart = tangentStart
            tangentStart = tangentEnd
            tangentEnd = oldTangentStart
        }
    }

    private static func convertVectorNetworkNode(
        node: FigNode,
        frame: NodeFrame,
        width: Double,
        height: Double,
        network: VectorNetwork<FigVectorStyleOverride>,
        context: MappingContext
    ) throws -> [ConversionLayer] {
        if network.vertices.isEmpty {
            throw FigTreeToDocumentMapperError.shapePathWarning("SHP002", node.guid)
        }

        let regions = vectorRegions(from: network)
        let regionLayers: [ConversionLayer] = regions.enumerated().compactMap { index, region in
            convertVectorRegion(
                node: node,
                frame: frame,
                width: width,
                height: height,
                region: region,
                regionIndex: index,
                network: network,
                context: context
            )
        }

        guard !regionLayers.isEmpty else {
            throw FigTreeToDocumentMapperError.shapePathWarning("SHP003", node.guid)
        }

        if regionLayers.count > 1 {
            var groupStyle = mergedVectorStyle(
                node: node,
                styleOverride: nil,
                context: context
            ).map(mapRenderableStyle) ?? ConversionLayerStyle()
            groupStyle.fills = []
            applyMarkerOverrides(from: node, style: &groupStyle)

            let normalizedChildren = regionLayers.map { positionedLayer($0, x: 0, y: 0) }
            return [.group(ConversionGroup(
                guid: node.guid,
                name: node.name,
                x: frame.x,
                y: frame.y,
                width: width,
                height: height,
                rotation: frame.rotation,
                layers: normalizedChildren,
                style: groupStyle,
                horizontalSizing: sizingBehaviour(for: node.horizontalConstraint),
                verticalSizing: sizingBehaviour(for: node.verticalConstraint),
                warningCodes: context.warnings(for: node.guid)
            ))]
        }

        return [positionedLayer(regionLayers[0], x: frame.x, y: frame.y, rotation: frame.rotation)]
    }

    private static func convertVectorRegion(
        node: FigNode,
        frame: NodeFrame,
        width: Double,
        height: Double,
        region: VectorRegionSegments,
        regionIndex: Int,
        network: VectorNetwork<FigVectorStyleOverride>,
        context: MappingContext
    ) -> ConversionLayer? {
        let loopLayers: [ConversionLayer] = region.loops.enumerated().map { loopIndex, loop in
            convertVectorLoop(
                node: node,
                width: width,
                height: height,
                loop: loop,
                regionIndex: regionIndex,
                loopIndex: loopIndex,
                region: region,
                network: network,
                context: context
            )
        }
        guard !loopLayers.isEmpty else { return nil }

        if loopLayers.count > 1 {
            let shapeGroupID = derivedGUID(node.guid, extra: [7, UInt32(regionIndex)])
            let style = mergedVectorStyle(
                node: node,
                styleOverride: region.styleOverride,
                context: context
            ).map(mapRenderableStyle)
            let normalizedChildren = loopLayers.map { positionedLayer($0, x: 0, y: 0) }
            return .group(ConversionGroup(
                guid: shapeGroupID,
                name: node.name,
                x: frame.x,
                y: frame.y,
                width: width,
                height: height,
                rotation: frame.rotation,
                layers: normalizedChildren,
                style: style,
                horizontalSizing: sizingBehaviour(for: node.horizontalConstraint),
                verticalSizing: sizingBehaviour(for: node.verticalConstraint),
                kind: .shapeGroup,
                windingRule: region.windingRule,
                warningCodes: context.warnings(for: node.guid)
            ))
        }

        return positionedLayer(loopLayers[0], x: frame.x, y: frame.y, rotation: frame.rotation)
    }

    private static func convertVectorLoop(
        node: FigNode,
        width: Double,
        height: Double,
        loop: [WorkingVectorSegment],
        regionIndex: Int,
        loopIndex: Int,
        region: VectorRegionSegments,
        network: VectorNetwork<FigVectorStyleOverride>,
        context: MappingContext
    ) -> ConversionLayer {
        var pathStyle = mergedVectorStyle(
            node: node,
            styleOverride: region.styleOverride,
            context: context
        ).map(mapRenderableStyle) ?? ConversionLayerStyle()
        let defaultCornerRadius = defaultVectorCornerRadius(for: node, context: context)
        let geometry = vectorLoopGeometry(
            loop: loop,
            network: network,
            defaultCornerRadius: defaultCornerRadius
        )

        applyMarkerOverrides(from: node, style: &pathStyle)
        applyEndpointMarkerOverrides(loop: loop, network: network, node: node, style: &pathStyle)
        pathStyle.windingRule = region.windingRule

        let path = ConversionShapePath(
            guid: derivedGUID(node.guid, extra: [7, UInt32(regionIndex), UInt32(loopIndex)]),
            name: node.name,
            x: 0,
            y: 0,
            width: width,
            height: height,
            isClosed: geometry.isClosed,
            points: geometry.points,
            style: pathStyle,
            warningCodes: context.warnings(for: node.guid)
        )
        return .shapePath(path)
    }

    private struct VectorLoopGeometry {
        var points: [ConversionShapePoint]
        var isClosed: Bool
    }

    private static func vectorLoopGeometry(
        loop: [WorkingVectorSegment],
        network: VectorNetwork<FigVectorStyleOverride>,
        defaultCornerRadius: Double
    ) -> VectorLoopGeometry {
        let isClosed = loop.first?.start == loop.last?.end
        var pointsByVertex: [UInt32: ConversionShapePoint] = [:]
        var orderedVertexIDs: [UInt32] = []

        for segment in loop {
            var startPoint = getOrCreateVectorPoint(
                for: segment.start,
                pointsByVertex: &pointsByVertex,
                orderedVertexIDs: &orderedVertexIDs,
                network: network,
                defaultCornerRadius: defaultCornerRadius
            )
            var endPoint = getOrCreateVectorPoint(
                for: segment.end,
                pointsByVertex: &pointsByVertex,
                orderedVertexIDs: &orderedVertexIDs,
                network: network,
                defaultCornerRadius: defaultCornerRadius
            )

            if segment.tangentStart.x != 0 || segment.tangentStart.y != 0,
               let startVertex = vectorVertexPoint(for: Int(segment.start), in: network) {
                startPoint.hasCurveFrom = true
                startPoint.curveFrom = ConversionPoint(
                    x: startVertex.x + segment.tangentStart.x,
                    y: startVertex.y + segment.tangentStart.y
                )
                startPoint.curveMode = curveMode(
                    forHandleMirroring: handleMirroring(forVertexAt: Int(segment.start), in: network) ?? "NONE"
                )
            }

            if segment.tangentEnd.x != 0 || segment.tangentEnd.y != 0,
               let endVertex = vectorVertexPoint(for: Int(segment.end), in: network) {
                endPoint.hasCurveTo = true
                endPoint.curveTo = ConversionPoint(
                    x: endVertex.x + segment.tangentEnd.x,
                    y: endVertex.y + segment.tangentEnd.y
                )
                endPoint.curveMode = curveMode(
                    forHandleMirroring: handleMirroring(forVertexAt: Int(segment.end), in: network) ?? "NONE"
                )
            }

            pointsByVertex[segment.start] = startPoint
            pointsByVertex[segment.end] = endPoint
        }

        for vertexID in orderedVertexIDs {
            guard var point = pointsByVertex[vertexID] else { continue }
            if !point.hasCurveFrom && !point.hasCurveTo {
                point.curveMode = .straight
            }
            pointsByVertex[vertexID] = point
        }

        return VectorLoopGeometry(
            points: orderedVertexIDs.compactMap { pointsByVertex[$0] },
            isClosed: isClosed
        )
    }

    private static func getOrCreateVectorPoint(
        for vertexID: UInt32,
        pointsByVertex: inout [UInt32: ConversionShapePoint],
        orderedVertexIDs: inout [UInt32],
        network: VectorNetwork<FigVectorStyleOverride>,
        defaultCornerRadius: Double
    ) -> ConversionShapePoint {
        if let existing = pointsByVertex[vertexID] {
            return existing
        }

        let point = vectorVertexPoint(for: Int(vertexID), in: network) ?? ConversionPoint(x: 0, y: 0)
        let handleMode = handleMirroring(forVertexAt: Int(vertexID), in: network) ?? "NONE"
        let cornerRadius = cornerRadius(forVertexAt: Int(vertexID), in: network) ?? defaultCornerRadius

        let created = ConversionShapePoint.straight(
            point,
            cornerRadius: cornerRadius,
            curveMode: curveMode(forHandleMirroring: handleMode)
        )
        pointsByVertex[vertexID] = created
        orderedVertexIDs.append(vertexID)
        return created
    }

    private static func vectorVertexPoint(
        for index: Int,
        in network: VectorNetwork<FigVectorStyleOverride>
    ) -> ConversionPoint? {
        guard network.vertices.indices.contains(index) else { return nil }
        return ConversionPoint(
            x: network.vertices[index].x,
            y: network.vertices[index].y
        )
    }

    private static func vectorRegions(
        from network: VectorNetwork<FigVectorStyleOverride>
    ) -> [VectorRegionSegments] {
        var unused = Set(network.segments.indices)
        var output: [VectorRegionSegments] = []

        for region in network.regions {
            var loops: [[WorkingVectorSegment]] = []
            for loopIndices in region.loops {
                var loopSegments: [WorkingVectorSegment] = []
                for segmentIndex in loopIndices {
                    let index = Int(segmentIndex)
                    guard network.segments.indices.contains(index) else { continue }
                    unused.remove(index)
                    loopSegments.append(WorkingVectorSegment(network.segments[index]))
                }
                let ordered = reorderSegmentPoints(loopSegments)
                if !ordered.isEmpty {
                    loops.append(ordered)
                }
            }

            if !loops.isEmpty {
                output.append(VectorRegionSegments(
                    loops: loops,
                    styleOverride: resolvedVectorStyleOverride(region.style),
                    windingRule: mapVectorWindingRule(region.windingRule)
                ))
            }
        }

        if !unused.isEmpty {
            let remainingSegments = unused.sorted().map { WorkingVectorSegment(network.segments[$0]) }
            let restLoops = reorderSegments(remainingSegments)
            if !restLoops.isEmpty {
                let isClosedSingleLoop = restLoops.count == 1 &&
                    restLoops[0].first?.start == restLoops[0].last?.end
                let restStyle = isClosedSingleLoop ? nil : FigVectorStyleOverride(
                    style: FigLayerStyle(fills: []),
                    overridesFills: true
                )
                output.append(VectorRegionSegments(
                    loops: restLoops,
                    styleOverride: restStyle,
                    windingRule: .nonZero
                ))
            }
        }

        return output
    }

    private static func resolvedVectorStyleOverride(
        _ style: VectorResolvedStyle<FigVectorStyleOverride>
    ) -> FigVectorStyleOverride? {
        switch style {
        case .override(let override):
            return override
        case .styleID:
            return nil
        }
    }

    private static func mapVectorWindingRule(_ rule: VectorWindingRule) -> ConversionWindingRule {
        switch rule {
        case .odd:
            return .evenOdd
        case .nonzero:
            return .nonZero
        }
    }

    private static func reorderSegmentPoints(_ segments: [WorkingVectorSegment]) -> [WorkingVectorSegment] {
        guard segments.count > 1 else { return segments }
        var output = segments

        if output[0].end != output[1].start, output[0].end != output[1].end {
            output[0].swapEndpoints()
        }

        for index in 1..<output.count {
            if output[index - 1].end != output[index].start {
                output[index].swapEndpoints()
            }
        }

        return output
    }

    private static func reorderSegments(_ segments: [WorkingVectorSegment]) -> [[WorkingVectorSegment]] {
        guard !segments.isEmpty else { return [] }

        var remaining = segments
        var runs: [[WorkingVectorSegment]] = []

        while !remaining.isEmpty {
            let startIndex = startSegmentIndex(for: remaining)
            var current = remaining.remove(at: startIndex)

            if !remaining.contains(where: { $0.start == current.end || $0.end == current.end }),
               remaining.contains(where: { $0.start == current.start || $0.end == current.start }) {
                current.swapEndpoints()
            }

            var run = [current]
            let startPoint = run[0].start

            while run.last?.end != startPoint {
                guard let previous = run.last,
                      let nextIndex = remaining.firstIndex(where: {
                          $0.start == previous.end || $0.end == previous.end
                      }) else {
                    break
                }

                var next = remaining.remove(at: nextIndex)
                if next.start != previous.end {
                    next.swapEndpoints()
                }
                run.append(next)
            }

            runs.append(run)
        }

        return runs
    }

    private static func startSegmentIndex(for segments: [WorkingVectorSegment]) -> Int {
        var degreeByVertex: [UInt32: Int] = [:]
        for segment in segments {
            degreeByVertex[segment.start, default: 0] += 1
            degreeByVertex[segment.end, default: 0] += 1
        }

        if let index = segments.firstIndex(where: {
            degreeByVertex[$0.start] == 1 || degreeByVertex[$0.end] == 1
        }) {
            return index
        }

        return 0
    }

    private static func mergedVectorStyle(
        node: FigNode,
        styleOverride: FigVectorStyleOverride?,
        context: MappingContext
    ) -> FigLayerStyle? {
        let baseStyle = effectiveStyle(for: node, context: context)
        var merged = baseStyle ?? FigLayerStyle()
        var hasAnyStyle = baseStyle != nil

        guard let styleOverride else {
            return hasAnyStyle && !merged.isDefault ? merged : nil
        }

        if let overrideStyle = styleOverride.style {
            if styleOverride.overridesFills {
                merged.fills = overrideStyle.fills
                hasAnyStyle = true
            }
            if styleOverride.overridesBorders {
                merged.borders = overrideStyle.borders
                merged.borderOptions = overrideStyle.borderOptions
                merged.miterLimit = overrideStyle.miterLimit
                hasAnyStyle = true
            }
            if styleOverride.overridesEffects {
                merged.blurs = overrideStyle.blurs
                merged.shadows = overrideStyle.shadows
                hasAnyStyle = true
            }
            if styleOverride.overridesWindingRule {
                merged.windingRule = overrideStyle.windingRule
                hasAnyStyle = true
            }
            if styleOverride.overridesBlendMode {
                merged.blendMode = overrideStyle.blendMode
                merged.blendModeWasExplicit = overrideStyle.blendModeWasExplicit
                merged.blendModeNeedsOpacityNudge = overrideStyle.blendModeNeedsOpacityNudge
                hasAnyStyle = true
            }
            if styleOverride.overridesOpacity {
                merged.opacity = overrideStyle.opacity
                hasAnyStyle = true
            }
            if let corners = overrideStyle.corners {
                merged.corners = corners
                hasAnyStyle = true
            }
        }

        return hasAnyStyle && !merged.isDefault ? merged : nil
    }

    private static func applyEndpointMarkerOverrides(
        loop: [WorkingVectorSegment],
        network: VectorNetwork<FigVectorStyleOverride>,
        node: FigNode,
        style: inout ConversionLayerStyle
    ) {
        guard let first = loop.first,
              let last = loop.last,
              first.start != last.end else {
            return
        }

        let startStrokeCap = strokeCap(forVertexAt: Int(first.start), in: network) ??
            node.strokeCap ??
            node.vectorOverrideStrokeCap ??
            "NONE"
        let endStrokeCap = strokeCap(forVertexAt: Int(last.end), in: network) ??
            node.strokeCap ??
            node.vectorOverrideStrokeCap ??
            "NONE"

        applyMarkerOverrides(startStrokeCap: startStrokeCap, endStrokeCap: endStrokeCap, style: &style)
    }

    private static func defaultVectorCornerRadius(for node: FigNode, context: MappingContext) -> Double {
        guard let corners = effectiveStyle(for: node, context: context)?.corners,
              let first = corners.radii.first else {
            return 0
        }
        return first
    }

    private static func strokeCap(
        forVertexAt index: Int,
        in network: VectorNetwork<FigVectorStyleOverride>
    ) -> String? {
        vectorStyleOverride(forVertexAt: index, in: network)?.strokeCap
    }

    private static func handleMirroring(
        forVertexAt index: Int,
        in network: VectorNetwork<FigVectorStyleOverride>
    ) -> String? {
        vectorStyleOverride(forVertexAt: index, in: network)?.handleMirroring
    }

    private static func cornerRadius(
        forVertexAt index: Int,
        in network: VectorNetwork<FigVectorStyleOverride>
    ) -> Double? {
        vectorStyleOverride(forVertexAt: index, in: network)?.cornerRadius
    }

    private static func vectorStyleOverride(
        forVertexAt index: Int,
        in network: VectorNetwork<FigVectorStyleOverride>
    ) -> FigVectorStyleOverride? {
        guard network.vertices.indices.contains(index),
              let style = network.vertices[index].style else {
            return nil
        }
        switch style {
        case .override(let payload):
            return payload
        case .styleID:
            return nil
        }
    }

    private static func curveMode(forHandleMirroring handleMirroring: String) -> ConversionCurveMode {
        switch handleMirroring {
        case "STRAIGHT":
            return .straight
        case "ANGLE_AND_LENGTH":
            return .mirrored
        case "ANGLE":
            return .asymmetric
        default:
            return .disconnected
        }
    }

    private static func positionedLayer(
        _ layer: ConversionLayer,
        x: Double,
        y: Double,
        rotation: Double? = nil
    ) -> ConversionLayer {
        switch layer {
        case .rectangle(var rectangle):
            rectangle.x = x
            rectangle.y = y
            if let rotation {
                rectangle.rotation = rotation
            }
            return .rectangle(rectangle)
        case .shapePath(var shapePath):
            shapePath.x = x
            shapePath.y = y
            if let rotation {
                shapePath.rotation = rotation
            }
            return .shapePath(shapePath)
        case .group(var group):
            group.x = x
            group.y = y
            if let rotation {
                group.rotation = rotation
            }
            return .group(group)
        case .artboard(var artboard):
            artboard.x = x
            artboard.y = y
            if let rotation {
                artboard.rotation = rotation
            }
            return .artboard(artboard)
        case .symbolMaster(var master):
            master.x = x
            master.y = y
            if let rotation {
                master.rotation = rotation
            }
            return .symbolMaster(master)
        case .symbolInstance(var instance):
            instance.x = x
            instance.y = y
            if let rotation {
                instance.rotation = rotation
            }
            return .symbolInstance(instance)
        case .text(var text):
            text.x = x
            text.y = y
            if let rotation {
                text.rotation = rotation
            }
            return .text(text)
        }
    }

}
