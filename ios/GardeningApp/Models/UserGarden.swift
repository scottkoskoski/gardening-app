import Foundation

struct UserGarden: Codable, Identifiable, Equatable, Hashable {
    let id: Int
    var gardenName: String
    var gardenType: String?
    var isCommunityGarden: Bool?
    var isRooftopGarden: Bool?
    var gardenSize: String?
    var gardenDimensions: String?
    var soilType: String?
    var waterSource: String?
    var pestProtection: Bool?
    var plantHardinessZone: String?
    var preferredPlants: [String]?
    var currentPlants: [String]?
    var gridRows: Int?
    var gridCols: Int?
    var gardenPlants: [GardenPlantSummary]?

    enum CodingKeys: String, CodingKey {
        case id
        case gardenName = "garden_name"
        case gardenType = "garden_type"
        case isCommunityGarden = "is_community_garden"
        case isRooftopGarden = "is_rooftop_garden"
        case gardenSize = "garden_size"
        case gardenDimensions = "garden_dimensions"
        case soilType = "soil_type"
        case waterSource = "water_source"
        case pestProtection = "pest_protection"
        case plantHardinessZone = "plant_hardiness_zone"
        case preferredPlants = "preferred_plants"
        case currentPlants = "current_plants"
        case gridRows = "grid_rows"
        case gridCols = "grid_cols"
        case gardenPlants = "garden_plants"
    }
}

struct GardenPlantSummary: Codable, Identifiable, Equatable, Hashable {
    let id: Int
    let plantId: Int
    let plantName: String
    let growthStage: String
    let expectedHarvestDate: String?
    let row: Int?
    let col: Int?

    enum CodingKeys: String, CodingKey {
        case id, row, col
        case plantId = "plant_id"
        case plantName = "plant_name"
        case growthStage = "growth_stage"
        case expectedHarvestDate = "expected_harvest_date"
    }
}

struct GardenType: Codable, Identifiable, Equatable, Hashable {
    let id: Int
    let name: String
    let description: String?
    let idealSoilType: String?
    let spaceRequirements: String?
    let maintenanceLevel: String?

    enum CodingKeys: String, CodingKey {
        case id, name, description
        case idealSoilType
        case spaceRequirements
        case maintenanceLevel
    }
}

struct GardenCreateRequest: Encodable {
    let gardenName: String
    let gardenType: String
    let isCommunityGarden: Bool?
    let isRooftopGarden: Bool?
    let gardenSize: String?
    let gardenDimensions: String?
    let soilType: String?
    let waterSource: String?
    let pestProtection: Bool?
    let plantHardinessZone: String?
    let preferredPlants: [String]?
    let currentPlants: [String]?
    let gridRows: Int?
    let gridCols: Int?

    enum CodingKeys: String, CodingKey {
        case gardenName = "garden_name"
        case gardenType = "garden_type"
        case isCommunityGarden = "is_community_garden"
        case isRooftopGarden = "is_rooftop_garden"
        case gardenSize = "garden_size"
        case gardenDimensions = "garden_dimensions"
        case soilType = "soil_type"
        case waterSource = "water_source"
        case pestProtection = "pest_protection"
        case plantHardinessZone = "plant_hardiness_zone"
        case preferredPlants = "preferred_plants"
        case currentPlants = "current_plants"
        case gridRows = "grid_rows"
        case gridCols = "grid_cols"
    }
}

struct GardenIDResponse: Codable {
    let message: String
    let gardenId: Int

    enum CodingKeys: String, CodingKey {
        case message
        case gardenId = "garden_id"
    }
}
