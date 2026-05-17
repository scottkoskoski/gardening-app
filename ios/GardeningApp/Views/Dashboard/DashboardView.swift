import SwiftUI

struct DashboardView: View {
    @EnvironmentObject private var auth: AuthViewModel
    @StateObject private var vm = DashboardViewModel()

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                greeting

                if let weather = vm.weather {
                    WeatherCard(weather: weather, profile: vm.profile)
                }

                if !vm.tasks.isEmpty {
                    sectionHeader("Today's Tasks", systemImage: "checklist")
                    VStack(spacing: 8) {
                        ForEach(vm.tasks.prefix(4)) { task in
                            DashboardTaskRow(task: task)
                        }
                        if vm.tasks.count > 4 {
                            NavigationLink(value: "all-tasks") {
                                HStack {
                                    Text("See all \(vm.tasks.count) tasks")
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                }
                                .font(.subheadline)
                                .padding(.horizontal)
                                .padding(.vertical, 12)
                            }
                            .foregroundStyle(.green)
                        }
                    }
                }

                if !vm.recommendations.isEmpty {
                    sectionHeader("Recommended for You", systemImage: "sparkles")
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            ForEach(vm.recommendations) { rec in
                                NavigationLink(value: rec.plant) {
                                    RecommendationCard(recommendation: rec)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        .padding(.horizontal)
                    }
                }

                if let error = vm.errorMessage {
                    Text(error)
                        .foregroundStyle(.red)
                        .font(.callout)
                        .padding(.horizontal)
                }
            }
            .padding(.vertical)
        }
        .navigationTitle("Dashboard")
        .refreshable { await vm.load() }
        .task { await vm.load() }
        .navigationDestination(for: Plant.self) { plant in
            PlantDetailView(plantId: plant.id, initialPlant: plant)
        }
        .navigationDestination(for: String.self) { route in
            if route == "all-tasks" {
                TasksView()
            }
        }
        .overlay {
            if vm.isLoading && vm.tasks.isEmpty {
                ProgressView()
            }
        }
    }

    private var greeting: some View {
        VStack(alignment: .leading, spacing: 4) {
            if case let .signedIn(user) = auth.state {
                Text("Hello, \(user.username) 🌱")
                    .font(.title2.bold())
            } else {
                Text("Hello there 🌱")
                    .font(.title2.bold())
            }
            if let zone = vm.profile?.plantHardinessZone, !zone.isEmpty {
                Text("USDA Hardiness Zone \(zone)")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            } else {
                Text("Set your ZIP code in Profile to unlock recommendations.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal)
    }

    private func sectionHeader(_ title: String, systemImage: String) -> some View {
        HStack {
            Label(title, systemImage: systemImage)
                .font(.headline)
            Spacer()
        }
        .padding(.horizontal)
    }
}

private struct DashboardTaskRow: View {
    let task: GardenTask

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: task.systemImage)
                .foregroundStyle(priorityColor)
                .frame(width: 28)
            VStack(alignment: .leading, spacing: 2) {
                Text(task.title)
                    .font(.subheadline.weight(.medium))
                Text(task.description)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            Spacer()
            Badge(task.dueLabel, tint: priorityColor)
        }
        .padding()
        .background(.background, in: RoundedRectangle(cornerRadius: 12))
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .strokeBorder(Color.gray.opacity(0.15))
        )
        .padding(.horizontal)
    }

    private var priorityColor: Color {
        switch task.priority {
        case "high": .red
        case "medium": .orange
        default: .green
        }
    }
}

private struct WeatherCard: View {
    let weather: WeatherResponse
    let profile: UserProfile?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Label("Local Weather", systemImage: "cloud.sun")
                    .font(.headline)
                Spacer()
                if let city = profile?.city, !city.isEmpty {
                    Text(city + (profile?.state.map { ", \($0)" } ?? ""))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            HStack(alignment: .firstTextBaseline) {
                if let temp = weather.current?.temperature {
                    Text("\(Int(temp))°")
                        .font(.system(size: 56, weight: .light))
                }
                Spacer()
                if let max = weather.daily?.temperatureMax?.first,
                   let min = weather.daily?.temperatureMin?.first {
                    VStack(alignment: .trailing) {
                        Label("\(Int(max))°", systemImage: "arrow.up")
                        Label("\(Int(min))°", systemImage: "arrow.down")
                    }
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                }
            }
        }
        .padding()
        .background(.green.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
        .padding(.horizontal)
    }
}

private struct RecommendationCard: View {
    let recommendation: Recommendation

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            RemoteImage(urlString: recommendation.plant.imageUrl)
                .frame(width: 160, height: 100)
                .clipShape(RoundedRectangle(cornerRadius: 10))
            Text(recommendation.plant.name)
                .font(.subheadline.weight(.semibold))
                .lineLimit(1)
            HStack(spacing: 4) {
                Image(systemName: "star.fill").foregroundStyle(.yellow)
                Text("\(recommendation.matchPercent)% match")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            if let reason = recommendation.reasons.first {
                Text(reason)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
        }
        .frame(width: 160)
        .padding(12)
        .background(.background, in: RoundedRectangle(cornerRadius: 14))
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .strokeBorder(Color.gray.opacity(0.15))
        )
    }
}
