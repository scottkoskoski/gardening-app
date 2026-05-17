import XCTest
@testable import GardeningApp

final class RecommendationTests: XCTestCase {
    private func makeRec(score: Int, maxScore: Int) -> Recommendation {
        Recommendation(
            plantId: 1,
            name: "Tomato",
            scientificName: nil,
            imageUrl: nil,
            description: nil,
            score: score,
            maxScore: maxScore,
            reasons: [],
            warnings: [],
            growingSeason: nil,
            sunlight: nil,
            waterNeeds: nil,
            spaceRequired: nil
        )
    }

    func testMatchPercentRoundsScoreToMax() {
        XCTAssertEqual(makeRec(score: 75, maxScore: 100).matchPercent, 75)
    }

    func testZeroMaxScoreIsSafe() {
        XCTAssertEqual(makeRec(score: 0, maxScore: 0).matchPercent, 0)
    }
}
