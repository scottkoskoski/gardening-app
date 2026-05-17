import SwiftUI

struct GardenFormView: View {
    enum Mode: Equatable {
        case create
        case edit(UserGarden)
    }

    var mode: Mode = .create
    let gardenTypes: [GardenType]
    var onSaved: (Int) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var name: String = ""
    @State private var typeName: String = ""
    @State private var size: String = ""
    @State private var dimensions: String = ""
    @State private var soilType: String = ""
    @State private var waterSource: String = ""
    @State private var hardinessZone: String = ""
    @State private var pestProtection: Bool = false
    @State private var isCommunity: Bool = false
    @State private var isRooftop: Bool = false
    @State private var gridRows: Int = 8
    @State private var gridCols: Int = 10
    @State private var isSaving = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            Form {
                Section("Basics") {
                    TextField("Garden name", text: $name)
                        .autocorrectionDisabled()
                    Picker("Type", selection: $typeName) {
                        Text("Select…").tag("")
                        ForEach(gardenTypes) {
                            Text($0.name).tag($0.name)
                        }
                    }
                    TextField("Hardiness zone (e.g. 7a)", text: $hardinessZone)
                        .textInputAutocapitalization(.never)
                }

                Section("Layout") {
                    Stepper("Rows: \(gridRows)", value: $gridRows, in: 1...30)
                    Stepper("Columns: \(gridCols)", value: $gridCols, in: 1...30)
                }

                Section("Conditions") {
                    TextField("Size (e.g. 10x10 ft)", text: $size)
                    TextField("Dimensions", text: $dimensions)
                    TextField("Soil type", text: $soilType)
                    TextField("Water source", text: $waterSource)
                    Toggle("Pest protection", isOn: $pestProtection)
                }

                Section("Style") {
                    Toggle("Community garden", isOn: $isCommunity)
                    Toggle("Rooftop garden", isOn: $isRooftop)
                }

                if let errorMessage {
                    Section {
                        Label(errorMessage, systemImage: "exclamationmark.triangle")
                            .foregroundStyle(.red)
                    }
                }
            }
            .navigationTitle(navigationTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: save) {
                        if isSaving { ProgressView() }
                        else { Text("Save").fontWeight(.semibold) }
                    }
                    .disabled(!canSave || isSaving)
                }
            }
            .onAppear(perform: populateInitial)
        }
    }

    private var navigationTitle: String {
        if case .edit = mode { return "Edit Garden" }
        return "New Garden"
    }

    private var canSave: Bool {
        !name.isEmpty && !typeName.isEmpty
    }

    private func populateInitial() {
        if case let .edit(garden) = mode {
            name = garden.gardenName
            typeName = garden.gardenType ?? ""
            size = garden.gardenSize ?? ""
            dimensions = garden.gardenDimensions ?? ""
            soilType = garden.soilType ?? ""
            waterSource = garden.waterSource ?? ""
            hardinessZone = garden.plantHardinessZone ?? ""
            pestProtection = garden.pestProtection ?? false
            isCommunity = garden.isCommunityGarden ?? false
            isRooftop = garden.isRooftopGarden ?? false
            gridRows = garden.gridRows ?? 8
            gridCols = garden.gridCols ?? 10
        }
    }

    private func save() {
        isSaving = true
        errorMessage = nil
        Task {
            defer { isSaving = false }
            let request = GardenCreateRequest(
                gardenName: name,
                gardenType: typeName,
                isCommunityGarden: isCommunity,
                isRooftopGarden: isRooftop,
                gardenSize: size.isEmpty ? nil : size,
                gardenDimensions: dimensions.isEmpty ? nil : dimensions,
                soilType: soilType.isEmpty ? nil : soilType,
                waterSource: waterSource.isEmpty ? nil : waterSource,
                pestProtection: pestProtection,
                plantHardinessZone: hardinessZone.isEmpty ? nil : hardinessZone,
                preferredPlants: nil,
                currentPlants: nil,
                gridRows: gridRows,
                gridCols: gridCols
            )
            do {
                switch mode {
                case .create:
                    let id = try await GardenService.shared.createGarden(request)
                    onSaved(id)
                case let .edit(garden):
                    try await GardenService.shared.updateGarden(id: garden.id, request: request)
                    onSaved(garden.id)
                }
                dismiss()
            } catch {
                errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            }
        }
    }
}
