import SwiftUI

struct PlantDetailView: View {
    let plantId: Int
    let initialPlant: Plant?

    @State private var plant: Plant?
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showingAddToGarden = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if let plant = plant ?? initialPlant {
                    RemoteImage(urlString: plant.imageUrl)
                        .frame(height: 240)
                        .frame(maxWidth: .infinity)
                        .clipShape(RoundedRectangle(cornerRadius: 16))
                        .padding(.horizontal)

                    VStack(alignment: .leading, spacing: 4) {
                        Text(plant.name).font(.largeTitle.bold())
                        if let scientific = plant.scientificName, !scientific.isEmpty {
                            Text(scientific).italic().foregroundStyle(.secondary)
                        }
                    }
                    .padding(.horizontal)

                    badges(plant: plant)

                    if let description = plant.description, !description.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("About").font(.headline)
                            Text(description)
                                .font(.body)
                                .foregroundStyle(.secondary)
                        }
                        .padding(.horizontal)
                    }

                    growingInfo(plant: plant)

                    Button {
                        showingAddToGarden = true
                    } label: {
                        Label("Add to Garden", systemImage: "plus.circle.fill")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    .padding(.horizontal)
                    .padding(.bottom)
                }

                if let errorMessage {
                    Text(errorMessage)
                        .foregroundStyle(.red)
                        .padding()
                }
            }
        }
        .navigationTitle(plant?.name ?? initialPlant?.name ?? "Plant")
        .navigationBarTitleDisplayMode(.inline)
        .overlay {
            if isLoading && plant == nil && initialPlant == nil {
                ProgressView()
            }
        }
        .sheet(isPresented: $showingAddToGarden) {
            if let plant = plant ?? initialPlant {
                AddPlantToGardenSheet(plant: plant)
            }
        }
        .task { await load() }
    }

    private func badges(plant: Plant) -> some View {
        HStack(spacing: 8) {
            if let season = plant.growingSeason {
                Badge(season, systemImage: "calendar", tint: .orange)
            }
            if let sun = plant.sunlight {
                Badge(sun, systemImage: "sun.max", tint: .yellow)
            }
            if let water = plant.waterNeeds {
                Badge(water, systemImage: "drop", tint: .blue)
            }
            if plant.suitableForContainers == true {
                Badge("Containers", systemImage: "cylinder", tint: .brown)
            }
        }
        .padding(.horizontal)
    }

    @ViewBuilder
    private func growingInfo(plant: Plant) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Growing Info").font(.headline)
            VStack(spacing: 0) {
                InfoRow(label: "Hardiness zones",
                        value: hardinessRange(plant))
                InfoRow(label: "Best temperature",
                        value: temperatureRange(plant))
                if let method = plant.sowingMethod {
                    InfoRow(label: "Sowing method", value: method)
                }
                if let space = plant.spaceRequired {
                    InfoRow(label: "Space required", value: space)
                }
                if let spread = plant.spread {
                    InfoRow(label: "Spread", value: "\(Int(spread)) cm")
                }
                if let row = plant.rowSpacing {
                    InfoRow(label: "Row spacing", value: "\(Int(row)) cm")
                }
                if let height = plant.height {
                    InfoRow(label: "Height", value: "\(Int(height)) cm")
                }
            }
            .background(Color(.secondarySystemBackground), in: RoundedRectangle(cornerRadius: 12))
        }
        .padding(.horizontal)
    }

    private func hardinessRange(_ plant: Plant) -> String {
        switch (plant.hardinessMin, plant.hardinessMax) {
        case let (min?, max?): "\(min) – \(max)"
        case let (min?, nil): "≥ \(min)"
        case let (nil, max?): "≤ \(max)"
        default: "—"
        }
    }

    private func temperatureRange(_ plant: Plant) -> String {
        switch (plant.bestTemperatureMin, plant.bestTemperatureMax) {
        case let (min?, max?): "\(Int(min))°F – \(Int(max))°F"
        case let (min?, nil): "≥ \(Int(min))°F"
        case let (nil, max?): "≤ \(Int(max))°F"
        default: "—"
        }
    }

    private func load() async {
        guard plant == nil else { return }
        isLoading = true
        defer { isLoading = false }
        do {
            plant = try await PlantService.shared.getPlant(id: plantId)
        } catch {
            if initialPlant == nil {
                errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            }
        }
    }
}

private struct InfoRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
                .fontWeight(.medium)
        }
        .padding(.horizontal)
        .padding(.vertical, 10)
        .overlay(alignment: .bottom) {
            Divider().padding(.leading)
        }
    }
}
