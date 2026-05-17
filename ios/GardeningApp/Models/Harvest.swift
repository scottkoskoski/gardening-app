import Foundation

struct Harvest: Codable, Identifiable, Equatable, Hashable {
    let id: Int
    let gardenId: Int
    let plantId: Int?
    let plantName: String?
    let gardenName: String?
    let quantity: Double?
    let unit: String?
    let harvestDate: String?
    let notes: String?

    enum CodingKeys: String, CodingKey {
        case id, quantity, unit, notes
        case gardenId = "garden_id"
        case plantId = "plant_id"
        case plantName = "plant_name"
        case gardenName = "garden_name"
        case harvestDate = "harvest_date"
    }
}

struct HarvestSummary: Codable {
    let totalHarvests: Int?
    let totalQuantity: Double?
    let byPlant: [String: Double]?

    enum CodingKeys: String, CodingKey {
        case totalHarvests = "total_harvests"
        case totalQuantity = "total_quantity"
        case byPlant = "by_plant"
    }
}
