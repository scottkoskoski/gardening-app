import SwiftUI

struct GardenMapView: View {
    let garden: UserGarden

    var body: some View {
        let rows = garden.gridRows ?? 8
        let cols = garden.gridCols ?? 10
        let plantsByCell: [String: GardenPlantSummary] = Dictionary(
            uniqueKeysWithValues: (garden.gardenPlants ?? []).compactMap { plant in
                guard let r = plant.row, let c = plant.col else { return nil }
                return ("\(r),\(c)", plant)
            }
        )

        ScrollView([.horizontal, .vertical], showsIndicators: true) {
            VStack(spacing: 4) {
                ForEach(0..<rows, id: \.self) { r in
                    HStack(spacing: 4) {
                        ForEach(0..<cols, id: \.self) { c in
                            cell(plant: plantsByCell["\(r),\(c)"])
                        }
                    }
                }
            }
            .padding()
        }
        .navigationTitle("\(garden.gardenName) — Map")
        .navigationBarTitleDisplayMode(.inline)
        .overlay(alignment: .bottom) {
            VStack {
                Text("Tap-to-place editing isn't wired up yet — use the web to assign cells, or sync via the journal.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(8)
            }
            .frame(maxWidth: .infinity)
            .background(.ultraThinMaterial)
        }
    }

    @ViewBuilder
    private func cell(plant: GardenPlantSummary?) -> some View {
        ZStack {
            RoundedRectangle(cornerRadius: 6)
                .fill(plant == nil ? Color(.tertiarySystemBackground) : Color.green.opacity(0.25))
            if let plant {
                VStack(spacing: 2) {
                    Image(systemName: GrowthStage(rawValue: plant.growthStage)?.systemImage ?? "leaf")
                        .foregroundStyle(.green)
                        .font(.caption)
                    Text(plant.plantName.prefix(6))
                        .font(.system(size: 8))
                        .lineLimit(1)
                }
            }
        }
        .frame(width: 56, height: 56)
        .overlay(
            RoundedRectangle(cornerRadius: 6)
                .strokeBorder(Color.gray.opacity(0.2))
        )
    }
}
