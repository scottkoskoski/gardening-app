import Foundation

/// Models the raw Open-Meteo forecast response that the backend
/// proxies through `/api/weather/get_weather`.
struct WeatherResponse: Codable {
    let latitude: Double?
    let longitude: Double?
    let timezone: String?
    let current: WeatherCurrent?
    let daily: WeatherDaily?
    let hourly: WeatherHourly?
}

struct WeatherCurrent: Codable {
    let time: String?
    let temperature: Double?
    let precipitation: Double?
    let weatherCode: Int?
    let humidity: Double?
    let windSpeed: Double?

    enum CodingKeys: String, CodingKey {
        case time, precipitation
        case temperature = "temperature_2m"
        case weatherCode = "weathercode"
        case humidity = "relative_humidity_2m"
        case windSpeed = "wind_speed_10m"
    }
}

struct WeatherDaily: Codable {
    let time: [String]?
    let temperatureMax: [Double]?
    let temperatureMin: [Double]?
    let precipitationSum: [Double]?
    let weatherCode: [Int]?

    enum CodingKeys: String, CodingKey {
        case time
        case temperatureMax = "temperature_2m_max"
        case temperatureMin = "temperature_2m_min"
        case precipitationSum = "precipitation_sum"
        case weatherCode = "weathercode"
    }
}

struct WeatherHourly: Codable {
    let time: [String]?
    let temperature: [Double]?
    let precipitation: [Double]?

    enum CodingKeys: String, CodingKey {
        case time, precipitation
        case temperature = "temperature_2m"
    }
}

struct HardinessZoneResponse: Codable {
    let zone: String?
    let zip: String?
}

struct FrostDates: Codable {
    let zone: String?
    let lastFrost: String?
    let firstFrost: String?
    let growingSeasonDays: Int?
    let yearRound: Bool?

    enum CodingKeys: String, CodingKey {
        case zone
        case lastFrost = "last_frost"
        case firstFrost = "first_frost"
        case growingSeasonDays = "growing_season_days"
        case yearRound = "year_round"
    }
}
