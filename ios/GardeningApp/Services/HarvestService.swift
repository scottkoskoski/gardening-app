import Foundation

struct HarvestCreateRequest: Encodable {
    let gardenId: Int
    let plantId: Int?
    let quantity: Double
    let unit: String?
    let harvestDate: String?
    let notes: String?

    enum CodingKeys: String, CodingKey {
        case quantity, unit, notes
        case gardenId = "garden_id"
        case plantId = "plant_id"
        case harvestDate = "harvest_date"
    }
}

@MainActor
final class HarvestService {
    static let shared = HarvestService()
    private init() {}

    private let api = APIClient.shared

    func harvests(gardenId: Int) async throws -> [Harvest] {
        struct Response: Codable {
            let harvests: [Harvest]?
        }
        do {
            let r: Response = try await api.get("harvests/\(gardenId)")
            return r.harvests ?? []
        } catch APIError.decoding {
            let r: [Harvest] = try await api.get("harvests/\(gardenId)")
            return r
        }
    }

    func summary() async throws -> HarvestSummary {
        try await api.get("harvests/summary")
    }

    func create(_ request: HarvestCreateRequest) async throws {
        struct OK: Decodable { let message: String }
        let _: OK = try await api.post("harvests", body: request)
    }

    func delete(harvestId: Int) async throws {
        try await api.deleteVoid("harvests/\(harvestId)")
    }
}
