import SwiftUI

struct WeatherView: View {
    let zip: String

    @State private var weather: WeatherResponse?
    @State private var frostDates: FrostDates?
    @State private var hardiness: HardinessZoneResponse?
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                if let current = weather?.current {
                    currentCard(current: current)
                }

                if let daily = weather?.daily, let times = daily.time {
                    Section {
                        Text("Forecast").font(.headline).padding(.horizontal)
                        VStack(spacing: 0) {
                            ForEach(Array(times.enumerated()), id: \.offset) { idx, time in
                                forecastRow(
                                    time: time,
                                    high: daily.temperatureMax?[safe: idx],
                                    low: daily.temperatureMin?[safe: idx],
                                    precip: daily.precipitationSum?[safe: idx]
                                )
                            }
                        }
                        .background(.background, in: RoundedRectangle(cornerRadius: 12))
                        .padding(.horizontal)
                    }
                }

                if let frost = frostDates {
                    frostCard(frost: frost)
                }

                if let errorMessage {
                    Text(errorMessage).foregroundStyle(.red).padding()
                }
            }
            .padding(.vertical)
        }
        .navigationTitle("Weather")
        .navigationBarTitleDisplayMode(.inline)
        .task { await loadAll() }
        .refreshable { await loadAll() }
        .overlay { if isLoading && weather == nil { ProgressView() } }
    }

    private func currentCard(current: WeatherCurrent) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            if let zone = hardiness?.zone {
                Label("USDA Zone \(zone)", systemImage: "globe.americas")
                    .font(.headline)
            }
            HStack(alignment: .firstTextBaseline) {
                if let temp = current.temperature {
                    Text("\(Int(temp))°")
                        .font(.system(size: 64, weight: .light))
                }
                VStack(alignment: .leading, spacing: 4) {
                    if let humidity = current.humidity {
                        Label("\(Int(humidity))% humidity", systemImage: "humidity")
                    }
                    if let wind = current.windSpeed {
                        Label("\(Int(wind)) mph", systemImage: "wind")
                    }
                }
                .font(.subheadline)
                .foregroundStyle(.secondary)
            }
        }
        .padding()
        .background(.green.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
        .padding(.horizontal)
    }

    private func frostCard(frost: FrostDates) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Frost Dates").font(.headline)
            if frost.yearRound == true {
                Label("Year-round growing season", systemImage: "leaf.fill")
            } else {
                if let last = frost.lastFrost {
                    Label("Last frost: \(formatISO(last))", systemImage: "snowflake")
                }
                if let first = frost.firstFrost {
                    Label("First frost: \(formatISO(first))", systemImage: "snowflake")
                }
                if let days = frost.growingSeasonDays {
                    Label("\(days) growing days", systemImage: "calendar")
                }
            }
        }
        .padding()
        .background(.blue.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
        .padding(.horizontal)
    }

    private func forecastRow(time: String, high: Double?, low: Double?, precip: Double?) -> some View {
        HStack {
            Text(formatISO(time))
                .frame(width: 110, alignment: .leading)
            if let precip, precip > 0 {
                Label("\(Int(precip * 100))%", systemImage: "drop.fill")
                    .foregroundStyle(.blue)
                    .font(.caption)
            }
            Spacer()
            if let high { Text("\(Int(high))°").fontWeight(.medium) }
            if let low {
                Text("/ \(Int(low))°").foregroundStyle(.secondary)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .overlay(alignment: .bottom) { Divider().padding(.leading) }
    }

    private func formatISO(_ iso: String) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        if let date = formatter.date(from: iso) {
            return date.formatted(date: .abbreviated, time: .omitted)
        }
        let isoFormatter = ISO8601DateFormatter()
        if let date = isoFormatter.date(from: iso) {
            return date.formatted(date: .abbreviated, time: .omitted)
        }
        return iso
    }

    private func loadAll() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        async let w = try? await WeatherService.shared.getWeather(zip: zip)
        async let f = try? await WeatherService.shared.getFrostDates(zip: zip)
        async let h = try? await WeatherService.shared.getHardinessZone(zip: zip)

        let (weatherResp, frostResp, hardinessResp) = await (w, f, h)
        weather = weatherResp
        frostDates = frostResp
        hardiness = hardinessResp

        if weather == nil && frostDates == nil && hardiness == nil {
            errorMessage = "Couldn't load weather. Check your ZIP code."
        }
    }
}

private extension Array {
    subscript(safe index: Int) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
