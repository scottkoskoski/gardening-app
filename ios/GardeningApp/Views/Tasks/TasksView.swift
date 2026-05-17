import SwiftUI

struct TasksView: View {
    @State private var tasks: [GardenTask] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var filter: Filter = .all

    enum Filter: String, CaseIterable, Identifiable {
        case all = "All"
        case today = "Today"
        case thisWeek = "This Week"
        case upcoming = "Upcoming"
        var id: String { rawValue }
    }

    private var filteredTasks: [GardenTask] {
        switch filter {
        case .all: tasks
        case .today: tasks.filter { $0.due == "today" }
        case .thisWeek: tasks.filter { $0.due == "this_week" }
        case .upcoming: tasks.filter { $0.due == "upcoming" }
        }
    }

    var body: some View {
        AsyncContentView(
            isLoading: isLoading && tasks.isEmpty,
            errorMessage: tasks.isEmpty ? errorMessage : nil,
            onRetry: { Task { await load() } }
        ) {
            VStack(spacing: 0) {
                Picker("Filter", selection: $filter) {
                    ForEach(Filter.allCases) { Text($0.rawValue).tag($0) }
                }
                .pickerStyle(.segmented)
                .padding()

                List(filteredTasks) { task in
                    TaskRow(task: task)
                }
                .listStyle(.plain)
                .overlay {
                    if filteredTasks.isEmpty && !isLoading {
                        ContentUnavailableView(
                            "All caught up!",
                            systemImage: "checkmark.circle",
                            description: Text("You have no tasks for this filter.")
                        )
                    }
                }
            }
        }
        .navigationTitle("Tasks")
        .task { await load() }
        .refreshable { await load() }
    }

    private func load() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            tasks = try await TaskService.shared.tasks()
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }
}

private struct TaskRow: View {
    let task: GardenTask

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: task.systemImage)
                .foregroundStyle(priorityColor)
                .frame(width: 32, height: 32)
                .background(priorityColor.opacity(0.12), in: Circle())

            VStack(alignment: .leading, spacing: 4) {
                Text(task.title).font(.headline)
                Text(task.description)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                HStack(spacing: 6) {
                    Badge(task.dueLabel, tint: priorityColor)
                    if let garden = task.gardenName {
                        Badge(garden, systemImage: "tree", tint: .green)
                    }
                }
            }
        }
        .padding(.vertical, 4)
    }

    private var priorityColor: Color {
        switch task.priority {
        case "high": .red
        case "medium": .orange
        default: .green
        }
    }
}
