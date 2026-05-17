import Foundation

@MainActor
final class GardenService {
    static let shared = GardenService()
    private init() {}

    private let api = APIClient.shared

    func listGardens() async throws -> [UserGarden] {
        try await api.get("user_gardens")
    }

    func getGarden(id: Int) async throws -> UserGarden {
        try await api.get("user_gardens/\(id)")
    }

    func createGarden(_ request: GardenCreateRequest) async throws -> Int {
        let response: GardenIDResponse = try await api.post("user_gardens", body: request)
        return response.gardenId
    }

    func updateGarden(id: Int, request: GardenCreateRequest) async throws {
        struct OK: Decodable { let message: String }
        let _: OK = try await api.put("user_gardens/\(id)", body: request)
    }

    func deleteGarden(id: Int) async throws {
        try await api.deleteVoid("user_gardens/\(id)")
    }

    func listGardenTypes() async throws -> [GardenType] {
        try await api.get("garden_types")
    }

    func addPlantToGarden(_ request: AddPlantToGardenRequest) async throws -> Int {
        let response: AddPlantResponse = try await api.post("user_garden_plants", body: request)
        return response.gardenPlantId
    }

    func removeGardenPlant(gardenPlantId: Int) async throws {
        try await api.deleteVoid("user_garden_plants/\(gardenPlantId)")
    }
}
