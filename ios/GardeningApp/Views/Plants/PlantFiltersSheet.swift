import SwiftUI

struct PlantFiltersSheet: View {
    @Binding var filters: PlantFilters
    let onApply: () -> Void
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form {
                Section("Location") {
                    TextField("Hardiness Zone (e.g. 7a)", text: zoneBinding)
                        .textInputAutocapitalization(.never)
                }

                Section("Conditions") {
                    Picker("Sunlight", selection: $filters.sunlight) {
                        Text("Any").tag(SunlightLevel?.none)
                        ForEach(SunlightLevel.allCases) { Text($0.rawValue).tag(SunlightLevel?.some($0)) }
                    }
                    Picker("Water needs", selection: $filters.waterNeeds) {
                        Text("Any").tag(WaterNeeds?.none)
                        ForEach(WaterNeeds.allCases) { Text($0.rawValue).tag(WaterNeeds?.some($0)) }
                    }
                    Picker("Season", selection: $filters.growingSeason) {
                        Text("Any").tag(GrowingSeason?.none)
                        ForEach(GrowingSeason.allCases) { Text($0.rawValue).tag(GrowingSeason?.some($0)) }
                    }
                    Picker("Space", selection: $filters.spaceRequired) {
                        Text("Any").tag(SpaceRequirement?.none)
                        ForEach(SpaceRequirement.allCases) { Text($0.rawValue).tag(SpaceRequirement?.some($0)) }
                    }
                }

                Section("Garden type") {
                    Toggle("Greenhouse only", isOn: $filters.greenhouse)
                    Toggle("Container-friendly", isOn: $filters.containers)
                }

                Section {
                    Button("Reset all filters", role: .destructive) {
                        filters = PlantFilters(search: filters.search)
                    }
                }
            }
            .navigationTitle("Filter Plants")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Apply") {
                        onApply()
                        dismiss()
                    }
                    .fontWeight(.semibold)
                }
            }
        }
        .presentationDetents([.medium, .large])
    }

    private var zoneBinding: Binding<String> {
        Binding(
            get: { filters.zone ?? "" },
            set: { filters.zone = $0.isEmpty ? nil : $0 }
        )
    }
}
