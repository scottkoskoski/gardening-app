import Foundation

@MainActor
final class WeatherService {
    static let shared = WeatherService()
    private init() {}

    private let api = APIClient.shared

    func getWeather(zip: String? = nil, lat: Double? = nil, lon: Double? = nil) async throws -> WeatherResponse {
        var query: [String: String] = [:]
        if let zip { query["zip"] = zip }
        if let lat { query["lat"] = String(lat) }
        if let lon { query["lon"] = String(lon) }
        return try await api.get("weather/get_weather", query: query)
    }

    func getHardinessZone(zip: String) async throws -> HardinessZoneResponse {
        try await api.get("hardiness/get_hardiness_zone", query: ["zip": zip])
    }

    func getFrostDates(zip: String? = nil, zone: String? = nil) async throws -> FrostDates {
        var query: [String: String] = [:]
        if let zip { query["zip"] = zip }
        if let zone { query["zone"] = zone }
        return try await api.get("frost_dates", query: query)
    }
}
