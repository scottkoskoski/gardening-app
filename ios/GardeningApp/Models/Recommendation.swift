import Foundation

/// One entry in the recommendations endpoint. The backend returns a flat
/// dict (a subset of plant fields plus scoring metadata), not a nested
/// `plant` object, so we decode it here directly and expose a derived
/// `Plant` for navigation.
struct Recommendation: Codable, Identifiable, Equatable, Hashable {
    let plantId: Int
    let name: String
    let scientificName: String?
    let imageUrl: String?
    let description: String?
    let score: Int
    let maxScore: Int
    let reasons: [String]
    let warnings: [String]
    let growingSeason: String?
    let sunlight: String?
    let waterNeeds: String?
    let spaceRequired: String?

    var id: Int { plantId }

    enum CodingKeys: String, CodingKey {
        case name, description, score, reasons, warnings, sunlight
        case plantId = "plant_id"
        case scientificName = "scientific_name"
        case imageUrl = "image_url"
        case maxScore = "max_score"
        case growingSeason = "growing_season"
        case waterNeeds = "water_needs"
        case spaceRequired = "space_required"
    }

    var matchPercent: Int {
        guard maxScore > 0 else { return 0 }
        return Int(Double(score) / Double(maxScore) * 100)
    }

    /// A `Plant` view suitable for navigating into `PlantDetailView`.
    /// Only the basics are populated — the detail view fetches the full
    /// record by id.
    var plant: Plant {
        Plant(
            id: plantId,
            name: name,
            scientificName: scientificName,
            hardinessMin: nil, hardinessMax: nil,
            bestTemperatureMin: nil, bestTemperatureMax: nil,
            requiresGreenhouse: nil, suitableForContainers: nil,
            growingSeason: growingSeason,
            waterNeeds: waterNeeds,
            sunlight: sunlight,
            spaceRequired: spaceRequired,
            sowingMethod: nil,
            spread: nil, rowSpacing: nil, height: nil,
            description: description,
            imageUrl: imageUrl
        )
    }
}

struct RecommendationResponse: Codable {
    let recommendations: [Recommendation]
    let season: String?
    let zone: String?
}
