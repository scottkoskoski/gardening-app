import Foundation

@MainActor
final class GardensViewModel: ObservableObject {
    @Published var gardens: [UserGarden] = []
    @Published var gardenTypes: [GardenType] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            async let g = GardenService.shared.listGardens()
            async let t = GardenService.shared.listGardenTypes()
            gardens = try await g
            gardenTypes = (try? await t) ?? []
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }

    func delete(garden: UserGarden) async {
        do {
            try await GardenService.shared.deleteGarden(id: garden.id)
            gardens.removeAll { $0.id == garden.id }
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }

    func refresh(gardenId: Int) async {
        guard let updated = try? await GardenService.shared.getGarden(id: gardenId) else { return }
        if let idx = gardens.firstIndex(where: { $0.id == gardenId }) {
            gardens[idx] = updated
        } else {
            gardens.append(updated)
        }
    }
}
