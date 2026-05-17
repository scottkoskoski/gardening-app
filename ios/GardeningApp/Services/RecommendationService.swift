import Foundation

@MainActor
final class RecommendationService {
    static let shared = RecommendationService()
    private init() {}

    private let api = APIClient.shared

    func getRecommendations() async throws -> RecommendationResponse {
        try await api.get("recommendations")
    }

    func getSeasonal() async throws -> RecommendationResponse {
        try await api.get("recommendations/seasonal")
    }
}
