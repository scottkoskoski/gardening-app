import SwiftUI

struct PlantsView: View {
    @StateObject private var vm = PlantsViewModel()
    @State private var showingFilters = false

    var body: some View {
        AsyncContentView(
            isLoading: vm.isLoading && vm.plants.isEmpty,
            errorMessage: vm.plants.isEmpty ? vm.errorMessage : nil,
            onRetry: { Task { await vm.load() } }
        ) {
            List(vm.plants) { plant in
                NavigationLink(value: plant) {
                    PlantRow(plant: plant)
                }
            }
            .listStyle(.plain)
            .overlay {
                if vm.plants.isEmpty && !vm.isLoading {
                    ContentUnavailableView(
                        "No plants found",
                        systemImage: "leaf",
                        description: Text("Try adjusting your filters or search.")
                    )
                }
            }
        }
        .navigationTitle("Plants")
        .searchable(text: $vm.filters.search, placement: .navigationBarDrawer(displayMode: .always))
        .onChange(of: vm.filters.search) { _, _ in vm.reloadDebounced() }
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    showingFilters = true
                } label: {
                    Image(systemName: "line.3.horizontal.decrease.circle")
                        .symbolVariant(filtersActive ? .fill : .none)
                }
            }
        }
        .sheet(isPresented: $showingFilters) {
            PlantFiltersSheet(filters: $vm.filters) {
                Task { await vm.load() }
            }
        }
        .navigationDestination(for: Plant.self) { plant in
            PlantDetailView(plantId: plant.id, initialPlant: plant)
        }
        .task { await vm.load() }
        .refreshable { await vm.load() }
    }

    private var filtersActive: Bool {
        vm.filters.zone != nil
        || vm.filters.greenhouse
        || vm.filters.containers
        || vm.filters.sunlight != nil
        || vm.filters.waterNeeds != nil
        || vm.filters.growingSeason != nil
        || vm.filters.spaceRequired != nil
    }
}

struct PlantRow: View {
    let plant: Plant

    var body: some View {
        HStack(spacing: 12) {
            RemoteImage(urlString: plant.imageUrl)
                .frame(width: 60, height: 60)
                .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(alignment: .leading, spacing: 4) {
                Text(plant.name)
                    .font(.headline)
                if let scientific = plant.scientificName, !scientific.isEmpty {
                    Text(scientific)
                        .font(.caption)
                        .italic()
                        .foregroundStyle(.secondary)
                }
                HStack(spacing: 6) {
                    if let sun = plant.sunlight {
                        Badge(sun, systemImage: "sun.max", tint: .yellow)
                    }
                    if let water = plant.waterNeeds {
                        Badge(water, systemImage: "drop", tint: .blue)
                    }
                }
            }
            Spacer()
        }
        .padding(.vertical, 4)
    }
}
