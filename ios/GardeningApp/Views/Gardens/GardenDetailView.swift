import SwiftUI

struct GardenDetailView: View {
    let garden: UserGarden
    var onChanged: () -> Void
    var onDelete: () -> Void

    @State private var currentGarden: UserGarden
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showingEdit = false
    @State private var pendingDelete = false
    @State private var gardenTypes: [GardenType] = []

    init(garden: UserGarden, onChanged: @escaping () -> Void, onDelete: @escaping () -> Void) {
        self.garden = garden
        self.onChanged = onChanged
        self.onDelete = onDelete
        _currentGarden = State(initialValue: garden)
    }

    var body: some View {
        List {
            Section {
                summaryHeader
            }

            Section("Plants") {
                if let plants = currentGarden.gardenPlants, !plants.isEmpty {
                    ForEach(plants) { plant in
                        gardenPlantRow(plant)
                    }
                    .onDelete(perform: removePlant)
                } else {
                    Text("No plants yet — open the Plants tab to add one.")
                        .foregroundStyle(.secondary)
                }
            }

            Section("Garden Map") {
                NavigationLink {
                    GardenMapView(garden: currentGarden)
                } label: {
                    Label("View Layout", systemImage: "square.grid.3x3")
                }
            }

            Section("Journal") {
                NavigationLink {
                    JournalView(gardenId: currentGarden.id)
                } label: {
                    Label("Open Journal", systemImage: "book")
                }
            }

            Section("Details") {
                detailRow("Type", currentGarden.gardenType)
                detailRow("Zone", currentGarden.plantHardinessZone)
                detailRow("Size", currentGarden.gardenSize)
                detailRow("Soil", currentGarden.soilType)
                detailRow("Water", currentGarden.waterSource)
                detailRow("Pest protection", flag(currentGarden.pestProtection))
                detailRow("Community", flag(currentGarden.isCommunityGarden))
                detailRow("Rooftop", flag(currentGarden.isRooftopGarden))
            }

            Section {
                Button(role: .destructive) {
                    pendingDelete = true
                } label: {
                    Label("Delete Garden", systemImage: "trash")
                }
            }
        }
        .navigationTitle(currentGarden.gardenName)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    showingEdit = true
                } label: {
                    Image(systemName: "pencil")
                }
            }
        }
        .sheet(isPresented: $showingEdit) {
            GardenFormView(mode: .edit(currentGarden), gardenTypes: gardenTypes) { _ in
                Task { await reload() }
                onChanged()
            }
        }
        .confirmationDialog(
            "Delete \(currentGarden.gardenName)?",
            isPresented: $pendingDelete,
            titleVisibility: .visible
        ) {
            Button("Delete", role: .destructive) {
                onDelete()
            }
            Button("Cancel", role: .cancel) {}
        }
        .task {
            async let _ = reload()
            gardenTypes = (try? await GardenService.shared.listGardenTypes()) ?? []
        }
        .refreshable { await reload() }
        .overlay { if isLoading { ProgressView() } }
    }

    private var summaryHeader: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "tree.fill")
                    .foregroundStyle(.green)
                Text(currentGarden.gardenName).font(.title3.bold())
            }
            HStack(spacing: 8) {
                if let type = currentGarden.gardenType {
                    Badge(type, tint: .green)
                }
                if let plants = currentGarden.gardenPlants {
                    Badge("\(plants.count) plants", systemImage: "leaf", tint: .mint)
                }
            }
        }
    }

    private func gardenPlantRow(_ plant: GardenPlantSummary) -> some View {
        HStack {
            Image(systemName: GrowthStage(rawValue: plant.growthStage)?.systemImage ?? "leaf")
                .foregroundStyle(.green)
            VStack(alignment: .leading) {
                Text(plant.plantName).font(.subheadline.weight(.medium))
                Text(plant.growthStage).font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            if let date = plant.expectedHarvestDate {
                Text("Harvest: \(formatDate(date))")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private func formatDate(_ iso: String) -> String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: iso) {
            return date.formatted(date: .abbreviated, time: .omitted)
        }
        return iso
    }

    private func detailRow(_ label: String, _ value: String?) -> some View {
        HStack {
            Text(label).foregroundStyle(.secondary)
            Spacer()
            Text((value?.isEmpty == false ? value : nil) ?? "—")
                .multilineTextAlignment(.trailing)
        }
    }

    private func flag(_ value: Bool?) -> String {
        guard let value else { return "—" }
        return value ? "Yes" : "No"
    }

    private func removePlant(at offsets: IndexSet) {
        guard let plants = currentGarden.gardenPlants else { return }
        let toDelete = offsets.map { plants[$0] }
        Task {
            for plant in toDelete {
                try? await GardenService.shared.removeGardenPlant(gardenPlantId: plant.id)
            }
            await reload()
            onChanged()
        }
    }

    private func reload() async {
        isLoading = true
        defer { isLoading = false }
        do {
            currentGarden = try await GardenService.shared.getGarden(id: currentGarden.id)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }
}
