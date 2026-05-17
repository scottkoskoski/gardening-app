import Foundation

struct TasksResponse: Codable {
    let tasks: [GardenTask]?
}

@MainActor
final class TaskService {
    static let shared = TaskService()
    private init() {}

    private let api = APIClient.shared

    func tasks() async throws -> [GardenTask] {
        // The backend returns either {tasks: [...]} or a bare list depending
        // on configuration. Try both.
        do {
            let response: TasksResponse = try await api.get("tasks")
            return response.tasks ?? []
        } catch APIError.decoding {
            let list: [GardenTask] = try await api.get("tasks")
            return list
        }
    }
}
