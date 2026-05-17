import SwiftUI

struct JournalView: View {
    @StateObject private var vm: JournalViewModel
    @State private var showingNew = false

    init(gardenId: Int) {
        _vm = StateObject(wrappedValue: JournalViewModel(gardenId: gardenId))
    }

    var body: some View {
        AsyncContentView(
            isLoading: vm.isLoading && vm.entries.isEmpty,
            errorMessage: vm.entries.isEmpty ? vm.errorMessage : nil,
            onRetry: { Task { await vm.load() } }
        ) {
            List {
                ForEach(vm.entries) { entry in
                    JournalRow(entry: entry)
                }
                .onDelete { offsets in
                    let toDelete = offsets.map { vm.entries[$0] }
                    Task {
                        for entry in toDelete {
                            await vm.delete(entry)
                        }
                    }
                }
            }
            .overlay {
                if vm.entries.isEmpty && !vm.isLoading {
                    ContentUnavailableView(
                        "No journal entries",
                        systemImage: "book",
                        description: Text("Log observations, watering, and harvests.")
                    )
                }
            }
        }
        .navigationTitle(vm.gardenName ?? "Journal")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    showingNew = true
                } label: {
                    Image(systemName: "plus")
                }
            }
        }
        .sheet(isPresented: $showingNew) {
            NewJournalEntryView { type, title, notes, date in
                await vm.create(entryType: type, title: title, notes: notes, date: date)
            }
        }
        .task { await vm.load() }
        .refreshable { await vm.load() }
    }
}

private struct JournalRow: View {
    let entry: JournalEntry

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Label(entry.entryType.replacingOccurrences(of: "_", with: " ").capitalized,
                      systemImage: JournalEntryType(rawValue: entry.entryType)?.systemImage ?? "note.text")
                    .font(.caption.weight(.medium))
                    .foregroundStyle(.green)
                Spacer()
                if let date = entry.entryDate {
                    Text(formatDate(date))
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
            Text(entry.title).font(.headline)
            if let notes = entry.notes, !notes.isEmpty {
                Text(notes)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 4)
    }

    private func formatDate(_ iso: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = formatter.date(from: iso) ?? ISO8601DateFormatter().date(from: iso) {
            return date.formatted(date: .abbreviated, time: .omitted)
        }
        return iso
    }
}

private struct NewJournalEntryView: View {
    let onSave: (JournalEntryType, String, String, Date) async -> Bool

    @Environment(\.dismiss) private var dismiss
    @State private var type: JournalEntryType = .observation
    @State private var title = ""
    @State private var notes = ""
    @State private var date = Date()
    @State private var isSaving = false

    var body: some View {
        NavigationStack {
            Form {
                Section("Type") {
                    Picker("Type", selection: $type) {
                        ForEach(JournalEntryType.allCases) { t in
                            Label(t.displayName, systemImage: t.systemImage).tag(t)
                        }
                    }
                }
                Section("Entry") {
                    TextField("Title", text: $title)
                    DatePicker("Date", selection: $date)
                    TextField("Notes", text: $notes, axis: .vertical)
                        .lineLimit(4...8)
                }
            }
            .navigationTitle("New Entry")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        Task {
                            isSaving = true
                            defer { isSaving = false }
                            if await onSave(type, title, notes, date) {
                                dismiss()
                            }
                        }
                    } label: {
                        if isSaving { ProgressView() }
                        else { Text("Save").fontWeight(.semibold) }
                    }
                    .disabled(title.isEmpty || isSaving)
                }
            }
        }
    }
}
