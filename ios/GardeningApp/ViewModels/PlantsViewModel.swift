import Foundation
import Combine

@MainActor
final class PlantsViewModel: ObservableObject {
    @Published var plants: [Plant] = []
    @Published var filters = PlantFilters()
    @Published var isLoading = false
    @Published var errorMessage: String?

    private var searchTask: Task<Void, Never>?

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            plants = try await PlantService.shared.listPlants(filters: filters)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            plants = []
        }
    }

    /// Debounced reload, useful while the user types in the search field.
    func reloadDebounced() {
        searchTask?.cancel()
        searchTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: 350_000_000)
            guard !Task.isCancelled else { return }
            await self?.load()
        }
    }
}
