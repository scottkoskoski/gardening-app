import Foundation

@MainActor
final class ProfileViewModel: ObservableObject {
    @Published var profile: UserProfile = .empty
    @Published var isLoading = false
    @Published var isSaving = false
    @Published var errorMessage: String?
    @Published var successMessage: String?

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            profile = try await ProfileService.shared.getProfile()
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }

    func save() async {
        isSaving = true
        successMessage = nil
        errorMessage = nil
        defer { isSaving = false }
        do {
            let response = try await ProfileService.shared.updateProfile(profile)
            if let zone = response.plantHardinessZone, !zone.isEmpty {
                profile.plantHardinessZone = zone
            }
            successMessage = response.message
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }
}
