import SwiftUI

struct GardensView: View {
    @StateObject private var vm = GardensViewModel()
    @State private var showingNewGarden = false
    @State private var pendingDelete: UserGarden?

    var body: some View {
        AsyncContentView(
            isLoading: vm.isLoading && vm.gardens.isEmpty,
            errorMessage: vm.gardens.isEmpty ? vm.errorMessage : nil,
            onRetry: { Task { await vm.load() } }
        ) {
            List {
                ForEach(vm.gardens) { garden in
                    NavigationLink(value: garden) {
                        GardenRow(garden: garden)
                    }
                    .swipeActions {
                        Button(role: .destructive) {
                            pendingDelete = garden
                        } label: { Label("Delete", systemImage: "trash") }
                    }
                }
            }
            .overlay {
                if vm.gardens.isEmpty && !vm.isLoading {
                    ContentUnavailableView {
                        Label("No gardens yet", systemImage: "tree")
                    } description: {
                        Text("Add a garden to start tracking plants.")
                    } actions: {
                        Button("Add Garden") { showingNewGarden = true }
                            .buttonStyle(.borderedProminent)
                    }
                }
            }
        }
        .navigationTitle("My Gardens")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button { showingNewGarden = true } label: {
                    Image(systemName: "plus")
                }
            }
        }
        .sheet(isPresented: $showingNewGarden) {
            GardenFormView(gardenTypes: vm.gardenTypes) { newId in
                Task {
                    await vm.refresh(gardenId: newId)
                }
            }
        }
        .navigationDestination(for: UserGarden.self) { garden in
            GardenDetailView(garden: garden) {
                Task {
                    await vm.refresh(gardenId: garden.id)
                }
            } onDelete: {
                Task { await vm.delete(garden: garden) }
            }
        }
        .confirmationDialog(
            "Delete this garden?",
            isPresented: Binding(
                get: { pendingDelete != nil },
                set: { if !$0 { pendingDelete = nil } }
            ),
            titleVisibility: .visible,
            presenting: pendingDelete
        ) { garden in
            Button("Delete \(garden.gardenName)", role: .destructive) {
                Task { await vm.delete(garden: garden) }
                pendingDelete = nil
            }
            Button("Cancel", role: .cancel) { pendingDelete = nil }
        }
        .task { await vm.load() }
        .refreshable { await vm.load() }
    }
}

private struct GardenRow: View {
    let garden: UserGarden

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(garden.gardenName).font(.headline)
            HStack(spacing: 8) {
                if let type = garden.gardenType {
                    Badge(type, systemImage: "tree", tint: .green)
                }
                if let zone = garden.plantHardinessZone, !zone.isEmpty {
                    Badge("Zone \(zone)", systemImage: "globe.americas", tint: .blue)
                }
                if let count = garden.gardenPlants?.count, count > 0 {
                    Badge("\(count) plants", systemImage: "leaf", tint: .mint)
                }
            }
        }
        .padding(.vertical, 4)
    }
}
