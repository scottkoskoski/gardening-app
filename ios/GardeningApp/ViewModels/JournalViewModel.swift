import Foundation

@MainActor
final class JournalViewModel: ObservableObject {
    @Published var entries: [JournalEntry] = []
    @Published var gardenName: String?
    @Published var isLoading = false
    @Published var errorMessage: String?

    let gardenId: Int

    init(gardenId: Int) {
        self.gardenId = gardenId
    }

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            let result = try await JournalService.shared.entries(gardenId: gardenId)
            entries = result.entries
            gardenName = result.gardenName
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }

    func create(entryType: JournalEntryType, title: String, notes: String, date: Date) async -> Bool {
        let iso = ISO8601DateFormatter()
        let req = JournalEntryCreateRequest(
            gardenId: gardenId,
            entryType: entryType.rawValue,
            title: title,
            notes: notes.isEmpty ? nil : notes,
            entryDate: iso.string(from: date)
        )
        do {
            let entry = try await JournalService.shared.create(req)
            entries.insert(entry, at: 0)
            return true
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            return false
        }
    }

    func delete(_ entry: JournalEntry) async {
        do {
            try await JournalService.shared.delete(entryId: entry.id)
            entries.removeAll { $0.id == entry.id }
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }
}
