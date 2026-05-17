import Foundation

struct GardenTask: Codable, Identifiable, Equatable, Hashable {
    let id: String
    let type: String
    let priority: String
    let title: String
    let description: String
    let gardenName: String?
    let gardenId: Int?
    let plantName: String?
    let due: String

    enum CodingKeys: String, CodingKey {
        case id, type, priority, title, description, due
        case gardenName = "garden_name"
        case gardenId = "garden_id"
        case plantName = "plant_name"
    }

    var dueLabel: String {
        switch due {
        case "today": "Today"
        case "this_week": "This Week"
        case "upcoming": "Upcoming"
        default: due.capitalized
        }
    }

    var priorityColor: String { priority }
    var systemImage: String {
        switch type {
        case "watering": "drop.fill"
        case "harvest": "basket.fill"
        case "growth_stage": "arrow.up.right.circle"
        case "frost_warning": "snowflake"
        case "seasonal": "calendar"
        default: "leaf"
        }
    }
}
