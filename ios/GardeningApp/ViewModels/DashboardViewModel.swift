import Foundation

@MainActor
final class DashboardViewModel: ObservableObject {
    @Published var tasks: [GardenTask] = []
    @Published var weather: WeatherResponse?
    @Published var profile: UserProfile?
    @Published var recommendations: [Recommendation] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        async let profileFetch = try? ProfileService.shared.getProfile()
        async let tasksFetch = try? TaskService.shared.tasks()
        async let recsFetch = try? RecommendationService.shared.getRecommendations()

        let (p, t, r) = await (profileFetch, tasksFetch, recsFetch)
        self.profile = p
        self.tasks = t ?? []
        self.recommendations = (r?.recommendations ?? []).prefix(5).map { $0 }

        if let zip = p?.zipCode, !zip.isEmpty {
            self.weather = try? await WeatherService.shared.getWeather(zip: zip)
        }
    }
}
