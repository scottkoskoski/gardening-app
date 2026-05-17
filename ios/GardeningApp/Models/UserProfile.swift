import Foundation

struct UserProfile: Codable, Equatable {
    var zipCode: String?
    var plantHardinessZone: String?
    var city: String?
    var state: String?
    var hasIrrigation: Bool?
    var sunlightHours: Double?
    var soilPh: Double?

    enum CodingKeys: String, CodingKey {
        case zipCode = "zip_code"
        case plantHardinessZone = "plant_hardiness_zone"
        case city, state
        case hasIrrigation = "has_irrigation"
        case sunlightHours = "sunlight_hours"
        case soilPh = "soil_ph"
    }

    static let empty = UserProfile(
        zipCode: "",
        plantHardinessZone: "",
        city: "",
        state: "",
        hasIrrigation: false,
        sunlightHours: nil,
        soilPh: nil
    )
}

struct ProfileUpdateResponse: Codable {
    let message: String
    let plantHardinessZone: String?

    enum CodingKeys: String, CodingKey {
        case message
        case plantHardinessZone = "plant_hardiness_zone"
    }
}
