import Foundation

struct PlantFilters: Equatable {
    var search: String = ""
    var zone: String?
    var greenhouse: Bool = false
    var containers: Bool = false
    var sunlight: SunlightLevel?
    var waterNeeds: WaterNeeds?
    var growingSeason: GrowingSeason?
    var spaceRequired: SpaceRequirement?

    var queryItems: [String: String] {
        var q: [String: String] = [:]
        if !search.isEmpty { q["search"] = search }
        if let zone, !zone.isEmpty { q["zone"] = zone }
        if greenhouse { q["greenhouse"] = "true" }
        if containers { q["containers"] = "true" }
        if let sunlight { q["sunlight"] = sunlight.rawValue }
        if let waterNeeds { q["water_needs"] = waterNeeds.rawValue }
        if let growingSeason { q["growing_season"] = growingSeason.rawValue }
        if let spaceRequired { q["space_required"] = spaceRequired.rawValue }
        return q
    }
}

@MainActor
final class PlantService {
    static let shared = PlantService()
    private init() {}

    private let api = APIClient.shared

    func listPlants(filters: PlantFilters) async throws -> [Plant] {
        try await api.get("plants/get_plants", query: filters.queryItems)
    }

    func getPlant(id: Int) async throws -> Plant {
        try await api.get("plants/\(id)")
    }
}
