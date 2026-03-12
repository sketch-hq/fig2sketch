import XCTest

final class SemanticOracleTests: XCTestCase {
    func testStructureFixtureMatchesPythonOracle() throws {
        try SemanticOracleSupport.assertFixtureMatchesPython(named: "structure.fig")
    }

    func testVectorFixtureMatchesPythonOracle() throws {
        try SemanticOracleSupport.assertFixtureMatchesPython(named: "vector.fig")
    }

    func testBrokenImagesFixtureMatchesPythonOracle() throws {
        try SemanticOracleSupport.assertFixtureMatchesPython(named: "broken_images.fig")
    }
}
