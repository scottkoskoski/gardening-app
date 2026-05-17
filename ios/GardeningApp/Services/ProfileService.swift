import Foundation

@MainActor
final class ProfileService {
    static let shared = ProfileService()
    private init() {}

    private let api = APIClient.shared

    func getProfile() async throws -> UserProfile {
        try await api.get("users/profile")
    }

    func updateProfile(_ profile: UserProfile) async throws -> ProfileUpdateResponse {
        try await api.post("users/profile", body: profile)
    }
}
