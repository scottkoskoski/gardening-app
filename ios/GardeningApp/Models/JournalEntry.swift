import Foundation

struct JournalEntry: Codable, Identifiable, Equatable, Hashable {
    let id: Int
    let gardenId: Int
    let userId: Int
    let entryType: String
    let title: String
    let notes: String?
    let entryDate: String?
    let createdAt: String?

    enum CodingKeys: String, CodingKey {
        case id, title, notes
        case gardenId = "garden_id"
        case userId = "user_id"
        case entryType = "entry_type"
        case entryDate = "entry_date"
        case createdAt = "created_at"
    }
}

struct JournalEntryList: Codable {
    let entries: [JournalEntry]
    let gardenName: String?

    enum CodingKeys: String, CodingKey {
        case entries
        case gardenName = "garden_name"
    }
}

struct JournalEntryCreateRequest: Encodable {
    let gardenId: Int
    let entryType: String
    let title: String
    let notes: String?
    let entryDate: String?

    enum CodingKeys: String, CodingKey {
        case gardenId = "garden_id"
        case entryType = "entry_type"
        case title, notes
        case entryDate = "entry_date"
    }
}

enum JournalEntryType: String, CaseIterable, Identifiable {
    case observation = "observation"
    case watering = "watering"
    case fertilizing = "fertilizing"
    case pestDisease = "pest_disease"
    case harvest = "harvest"
    case planting = "planting"
    case maintenance = "maintenance"
    case note = "note"

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .observation: "Observation"
        case .watering: "Watering"
        case .fertilizing: "Fertilizing"
        case .pestDisease: "Pest / Disease"
        case .harvest: "Harvest"
        case .planting: "Planting"
        case .maintenance: "Maintenance"
        case .note: "Note"
        }
    }

    var systemImage: String {
        switch self {
        case .observation: "eye"
        case .watering: "drop.fill"
        case .fertilizing: "leaf.arrow.triangle.circlepath"
        case .pestDisease: "ladybug"
        case .harvest: "basket"
        case .planting: "shovel"
        case .maintenance: "wrench.and.screwdriver"
        case .note: "note.text"
        }
    }
}
