import XCTest
@testable import GardeningApp

final class PlantFiltersTests: XCTestCase {
    func testEmptyFiltersProduceEmptyQuery() {
        let filters = PlantFilters()
        XCTAssertTrue(filters.queryItems.isEmpty)
    }

    func testSearchIsForwarded() {
        var filters = PlantFilters()
        filters.search = "tomato"
        XCTAssertEqual(filters.queryItems["search"], "tomato")
    }

    func testFlagsOnlyEmittedWhenTrue() {
        var filters = PlantFilters()
        XCTAssertNil(filters.queryItems["greenhouse"])
        filters.greenhouse = true
        XCTAssertEqual(filters.queryItems["greenhouse"], "true")
    }

    func testEnumValuesUseBackendStrings() {
        var filters = PlantFilters()
        filters.sunlight = .partialShade
        filters.waterNeeds = .high
        filters.growingSeason = .summer
        filters.spaceRequired = .small
        XCTAssertEqual(filters.queryItems["sunlight"], "Partial Shade")
        XCTAssertEqual(filters.queryItems["water_needs"], "High")
        XCTAssertEqual(filters.queryItems["growing_season"], "Summer")
        XCTAssertEqual(filters.queryItems["space_required"], "Small")
    }
}
