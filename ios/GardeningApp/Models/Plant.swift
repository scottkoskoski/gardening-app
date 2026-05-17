import Foundation

struct Plant: Codable, Identifiable, Equatable, Hashable {
    let id: Int
    let name: String
    let scientificName: String?
    let hardinessMin: String?
    let hardinessMax: String?
    let bestTemperatureMin: Double?
    let bestTemperatureMax: Double?
    let requiresGreenhouse: Bool?
    let suitableForContainers: Bool?
    let growingSeason: String?
    let waterNeeds: String?
    let sunlight: String?
    let spaceRequired: String?
    let sowingMethod: String?
    let spread: Double?
    let rowSpacing: Double?
    let height: Double?
    let description: String?
    let imageUrl: String?

    enum CodingKeys: String, CodingKey {
        case id, name, sunlight, spread, height, description
        case scientificName = "scientific_name"
        case hardinessMin = "hardiness_min"
        case hardinessMax = "hardiness_max"
        case bestTemperatureMin = "best_temperature_min"
        case bestTemperatureMax = "best_temperature_max"
        case requiresGreenhouse = "requires_greenhouse"
        case suitableForContainers = "suitable_for_containers"
        case growingSeason = "growing_season"
        case waterNeeds = "water_needs"
        case spaceRequired = "space_required"
        case sowingMethod = "sowing_method"
        case rowSpacing = "row_spacing"
        case imageUrl = "image_url"
    }
}

enum GrowingSeason: String, CaseIterable, Identifiable {
    case spring = "Spring"
    case summer = "Summer"
    case fall = "Fall"
    case winter = "Winter"
    var id: String { rawValue }
}

enum WaterNeeds: String, CaseIterable, Identifiable {
    case low = "Low"
    case medium = "Medium"
    case high = "High"
    var id: String { rawValue }
}

enum SunlightLevel: String, CaseIterable, Identifiable {
    case fullSun = "Full Sun"
    case partialSun = "Partial Sun"
    case partialShade = "Partial Shade"
    case fullShade = "Full Shade"
    var id: String { rawValue }
}

enum SpaceRequirement: String, CaseIterable, Identifiable {
    case small = "Small"
    case medium = "Medium"
    case large = "Large"
    var id: String { rawValue }
}
