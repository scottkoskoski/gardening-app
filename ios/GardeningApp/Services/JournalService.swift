import Foundation

@MainActor
final class JournalService {
    static let shared = JournalService()
    private init() {}

    private let api = APIClient.shared

    func entries(gardenId: Int) async throws -> JournalEntryList {
        try await api.get("journal/\(gardenId)")
    }

    func recentEntries(gardenId: Int) async throws -> JournalEntryList {
        try await api.get("journal/\(gardenId)/recent")
    }

    func create(_ request: JournalEntryCreateRequest) async throws -> JournalEntry {
        struct CreateResponse: Codable {
            let message: String
            let entry: JournalEntry
        }
        let res: CreateResponse = try await api.post("journal", body: request)
        return res.entry
    }

    func delete(entryId: Int) async throws {
        try await api.deleteVoid("journal/\(entryId)")
    }
}
