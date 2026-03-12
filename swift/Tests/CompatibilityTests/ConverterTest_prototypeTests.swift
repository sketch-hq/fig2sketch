import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_prototypeTests: XCTestCase {
    func test__converter__test_prototype__TestPrototypeInformation__test_no_prototype() throws {
        // Port of tests/converter/test_prototype.py::TestPrototypeInformation.test_no_prototype
        let pageJSON = try pageJSONForPrototypeSlice(frameExtra: [:], additionalNodes: [])

        XCTAssertTrue(pageJSON.contains("\"isFlowHome\":false"))
        XCTAssertTrue(pageJSON.contains("\"overlayBackgroundInteraction\":0"))
        XCTAssertTrue(pageJSON.contains("\"presentationStyle\":0"))
    }

    func test__converter__test_prototype__TestPrototypeInformation__test_scroll_direction_warning() throws {
        // Port of tests/converter/test_prototype.py::TestPrototypeInformation.test_scroll_direction_warning
        let pageJSON = try pageJSONForPrototypeSlice(frameExtra: [
            "scrollDirection": .string("HORIZONTAL"),
        ], additionalNodes: [])

        XCTAssertTrue(pageJSON.contains("PRT005"))
    }

    func test__converter__test_prototype__TestPrototypeInformation__test_prototype_information_with_no_overlay() throws {
        // Port of tests/converter/test_prototype.py::TestPrototypeInformation.test_prototype_information_with_no_overlay
        let pageJSON = try pageJSONForPrototypeSlice(frameExtra: [:], additionalNodes: [])

        XCTAssertTrue(pageJSON.contains("\"prototypeViewport\""))
        XCTAssertTrue(pageJSON.contains("APPLE_IPHONE_14_PRO_SPACEBLACK"))
        XCTAssertTrue(pageJSON.contains("\"overlayAnchor\":\"{0.5, 0.5}\""))
        XCTAssertTrue(pageJSON.contains("\"sourceAnchor\":\"{0.5, 0.5}\""))
    }

    func test__converter__test_prototype__TestPrototypeInformation__test_prototype_information_with_overlay() throws {
        // Port of tests/converter/test_prototype.py::TestPrototypeInformation.test_prototype_information_with_overlay
        let overlay: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 3),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 1),
            "type": .string("FRAME"),
            "name": .string("Overlay"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "overlayPositionType": .string("BOTTOM_CENTER"),
            "overlayBackgroundInteraction": .string("CLOSE_ON_CLICK_OUTSIDE"),
        ]
        let pageJSON = try pageJSONForPrototypeSlice(frameExtra: [:], additionalNodes: [overlay])

        XCTAssertTrue(pageJSON.contains("\"presentationStyle\":1"))
        XCTAssertTrue(pageJSON.contains("\"overlayType\":0"))
        XCTAssertTrue(pageJSON.contains("\"overlayAnchor\":\"{0.5, 1}\""))
        XCTAssertTrue(pageJSON.contains("\"sourceAnchor\":\"{0.5, 1}\""))
    }

    func test__converter__test_prototype__TestConvertFlow__test_discarding_of_problematic_interactions() throws {
        // Port of tests/converter/test_prototype.py::TestConvertFlow.test_discarding_of_problematic_interactions
        let pageJSON = try pageJSONForPrototypeSlice(frameExtra: [
            "prototypeInteractions": .array([
                .object(["isDeleted": .bool(true), "event": .object([:])]),
                .object([
                    "isDeleted": .bool(false),
                    "actions": .array([.object([
                        "navigationType": .string("NAVIGATE"),
                        "connectionType": .string("BACK"),
                    ])]),
                ]),
                .object([
                    "isDeleted": .bool(false),
                    "event": .object(["interactionType": .string("DRAG")]),
                    "actions": .array([.object([
                        "navigationType": .string("NAVIGATE"),
                        "connectionType": .string("BACK"),
                    ])]),
                ]),
                .object([
                    "isDeleted": .bool(false),
                    "event": .object(["interactionType": .string("ON_CLICK")]),
                    "actions": .array([
                        .object([:]),
                        .object(["navigationType": .string("BACK"), "connectionType": .string("BACK")]),
                        .object(["navigationType": .string("SCROLL"), "connectionType": .string("FAKE_TYPE")]),
                        .object(["navigationType": .string("NAVIGATE"), "connectionType": .string("BACK")]),
                    ]),
                ]),
            ]),
        ], additionalNodes: [])

        XCTAssertTrue(pageJSON.contains("PRT001"))
        XCTAssertTrue(pageJSON.contains("PRT003"))
        XCTAssertTrue(pageJSON.contains("PRT004"))
        XCTAssertTrue(pageJSON.contains("\"destinationArtboardID\":\"back\""))
        XCTAssertTrue(pageJSON.contains("\"animationType\":0"))
    }

    func test__converter__test_prototype__TestConvertFlow__test_multiple_valid_actions_warning() throws {
        // Port of tests/converter/test_prototype.py::TestConvertFlow.test_multiple_valid_actions_warning
        let pageJSON = try pageJSONForPrototypeSlice(frameExtra: [
            "prototypeInteractions": .array([
                .object([
                    "isDeleted": .bool(false),
                    "event": .object(["interactionType": .string("ON_CLICK")]),
                    "actions": .array([
                        .object(["navigationType": .string("NAVIGATE"), "connectionType": .string("BACK")]),
                        .object(["navigationType": .string("SCROLL"), "connectionType": .string("NONE")]),
                    ]),
                ]),
            ]),
        ], additionalNodes: [])

        XCTAssertTrue(pageJSON.contains("PRT002"))
        XCTAssertTrue(pageJSON.contains("\"destinationArtboardID\":\"back\""))
    }

    func test__converter__test_prototype__TestConvertFlow__test_overlay_flow() throws {
        // Port of tests/converter/test_prototype.py::TestConvertFlow.test_overlay_flow
        let overlay: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 5),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 1),
            "type": .string("FRAME"),
            "name": .string("Overlay"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "overlayPositionType": .string("BOTTOM_CENTER"),
            "overlayBackgroundInteraction": .string("CLOSE_ON_CLICK_OUTSIDE"),
        ]
        let frameExtra: [String: KiwiValue] = [
            "prototypeInteractions": .array([
                .object([
                    "isDeleted": .bool(false),
                    "event": .object(["interactionType": .string("ON_CLICK")]),
                    "actions": .array([
                        .object([
                            "navigationType": .string("OVERLAY"),
                            "connectionType": .string("INTERNAL_NODE"),
                            "transitionNodeID": FixtureSupport.guid(0, 5),
                            "transitionType": .string("SLIDE_FROM_LEFT"),
                        ]),
                    ]),
                ]),
            ]),
        ]

        let pageJSON = try pageJSONForPrototypeSlice(frameExtra: frameExtra, additionalNodes: [overlay])
        let overlayID = ConverterUtils.genObjectID(figID: [0, 5], salt: Data("compat-tests".utf8))

        XCTAssertTrue(pageJSON.contains("\"destinationArtboardID\":\"\(overlayID)\""))
        XCTAssertTrue(pageJSON.contains("\"animationType\":5"))
        XCTAssertTrue(pageJSON.contains("\"overlayAnchor\":\"{0.5, 1}\""))
        XCTAssertTrue(pageJSON.contains("\"sourceAnchor\":\"{0.5, 1}\""))
    }

    func test__converter__test_prototype__TestConvertFlow__test_overly_with_manual_position() throws {
        // Port of tests/converter/test_prototype.py::TestConvertFlow.test_overly_with_manual_position
        let overlay: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 6),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 1),
            "type": .string("FRAME"),
            "name": .string("Overlay"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "overlayPositionType": .string("MANUAL"),
            "overlayBackgroundInteraction": .string("CLOSE_ON_CLICK_OUTSIDE"),
        ]
        let frameExtra: [String: KiwiValue] = [
            "prototypeInteractions": .array([
                .object([
                    "isDeleted": .bool(false),
                    "event": .object(["interactionType": .string("ON_CLICK")]),
                    "actions": .array([
                        .object([
                            "navigationType": .string("OVERLAY"),
                            "connectionType": .string("INTERNAL_NODE"),
                            "transitionNodeID": FixtureSupport.guid(0, 6),
                            "transitionType": .string("SLIDE_FROM_TOP"),
                            "overlayRelativePosition": .object([
                                "x": .float(19.6),
                                "y": .float(85.0),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ]

        let pageJSON = try pageJSONForPrototypeSlice(frameExtra: frameExtra, additionalNodes: [overlay])
        let overlayID = ConverterUtils.genObjectID(figID: [0, 6], salt: Data("compat-tests".utf8))

        XCTAssertTrue(pageJSON.contains("\"destinationArtboardID\":\"\(overlayID)\""))
        XCTAssertTrue(pageJSON.contains("\"animationType\":3"))
        XCTAssertTrue(pageJSON.contains("\"overlayAnchor\":\"{0, 0}\""))
        XCTAssertTrue(pageJSON.contains("\"sourceAnchor\":\"{0, 0}\""))
        XCTAssertTrue(pageJSON.contains("\"offset\":\"{19.6, 85}\""))
    }

    private func pageJSONForPrototypeSlice(
        frameExtra: [String: KiwiValue],
        additionalNodes: [[String: KiwiValue]]
    ) throws -> String {
        var frame: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("FRAME"),
            "name": .string("Artboard"),
            "size": .object(["x": .float(393), "y": .float(852)]),
        ]
        for (key, value) in frameExtra {
            frame[key] = value
        }

        // Keep one rectangle in the document so current mapper returns a document.
        let fallbackRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 99),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 99),
            "type": .string("RECTANGLE"),
            "name": .string("Fallback"),
            "size": .object(["x": .float(1), "y": .float(1)]),
        ]

        let root = FixtureSupport.makeRootMessage(
            nodes: [frame] + additionalNodes + [fallbackRect],
            canvasExtra: [
                "prototypeDevice": .object([
                    "type": .string("PRESET"),
                    "size": .object(["x": .float(393), "y": .float(852)]),
                    "presetIdentifier": .string("APPLE_IPHONE_14_PRO_SPACEBLACK"),
                    "rotation": .string("NONE"),
                ]),
            ]
        )
        let document = try FixtureSupport.mapDocument(from: root)
        return try FixtureSupport.pageJSONString(from: document)
    }
}
