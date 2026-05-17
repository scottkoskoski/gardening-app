import Foundation

enum GrowthStage: String, Codable, CaseIterable, Identifiable {
    case seedling = "Seedling"
    case vegetative = "Vegetative"
    case flowering = "Flowering"
    case fruiting = "Fruiting"

    var id: String { rawValue }

    var systemImage: String {
        switch self {
        case .seedling: "leaf"
        case .vegetative: "leaf.fill"
        case .flowering: "camera.macro"
        case .fruiting: "apple.logo"
        }
    }
}

struct AddPlantToGardenRequest: Encodable {
    let gardenId: Int
    let plantId: Int
    let expectedHarvestDate: String?
    let growthStage: String?

    enum CodingKeys: String, CodingKey {
        case gardenId = "garden_id"
        case plantId = "plant_id"
        case expectedHarvestDate = "expected_harvest_date"
        case growthStage = "growth_stage"
    }
}

struct AddPlantResponse: Codable {
    let message: String
    let gardenPlantId: Int

    enum CodingKeys: String, CodingKey {
        case message
        case gardenPlantId = "garden_plant_id"
    }
}
