import SwiftUI

struct AddPlantToGardenSheet: View {
    let plant: Plant

    @Environment(\.dismiss) private var dismiss
    @State private var gardens: [UserGarden] = []
    @State private var selectedGardenId: Int?
    @State private var growthStage: GrowthStage = .seedling
    @State private var includeHarvestDate = false
    @State private var harvestDate: Date = Calendar.current.date(byAdding: .month, value: 2, to: Date()) ?? Date()
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var isSubmitting = false

    var body: some View {
        NavigationStack {
            Form {
                Section("Plant") {
                    HStack {
                        RemoteImage(urlString: plant.imageUrl)
                            .frame(width: 48, height: 48)
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                        VStack(alignment: .leading) {
                            Text(plant.name).font(.headline)
                            if let scientific = plant.scientificName {
                                Text(scientific).font(.caption).italic().foregroundStyle(.secondary)
                            }
                        }
                    }
                }

                Section("Garden") {
                    if gardens.isEmpty {
                        Text("Create a garden first.")
                            .foregroundStyle(.secondary)
                    } else {
                        Picker("Choose garden", selection: $selectedGardenId) {
                            Text("Select…").tag(Int?.none)
                            ForEach(gardens) { Text($0.gardenName).tag(Int?.some($0.id)) }
                        }
                    }
                }

                Section("Growth stage") {
                    Picker("Stage", selection: $growthStage) {
                        ForEach(GrowthStage.allCases) { stage in
                            Label(stage.rawValue, systemImage: stage.systemImage).tag(stage)
                        }
                    }
                }

                Section("Expected harvest") {
                    Toggle("Set harvest date", isOn: $includeHarvestDate)
                    if includeHarvestDate {
                        DatePicker("Date", selection: $harvestDate, in: Date()..., displayedComponents: .date)
                    }
                }

                if let errorMessage {
                    Section {
                        Label(errorMessage, systemImage: "exclamationmark.triangle")
                            .foregroundStyle(.red)
                    }
                }
            }
            .navigationTitle("Add to Garden")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: submit) {
                        if isSubmitting {
                            ProgressView()
                        } else {
                            Text("Add").fontWeight(.semibold)
                        }
                    }
                    .disabled(selectedGardenId == nil || isSubmitting)
                }
            }
            .overlay {
                if isLoading {
                    ProgressView()
                }
            }
            .task { await loadGardens() }
        }
    }

    private func loadGardens() async {
        isLoading = true
        defer { isLoading = false }
        do {
            gardens = try await GardenService.shared.listGardens()
            selectedGardenId = gardens.first?.id
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }

    private func submit() {
        guard let gardenId = selectedGardenId else { return }
        isSubmitting = true
        errorMessage = nil
        Task {
            defer { isSubmitting = false }
            let formatter = DateFormatter()
            formatter.dateFormat = "yyyy-MM-dd"
            let req = AddPlantToGardenRequest(
                gardenId: gardenId,
                plantId: plant.id,
                expectedHarvestDate: includeHarvestDate ? formatter.string(from: harvestDate) : nil,
                growthStage: growthStage.rawValue.uppercased()
            )
            do {
                _ = try await GardenService.shared.addPlantToGarden(req)
                dismiss()
            } catch {
                errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            }
        }
    }
}
