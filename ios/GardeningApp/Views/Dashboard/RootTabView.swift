import SwiftUI

struct RootTabView: View {
    @State private var selectedTab: Tab = .dashboard

    enum Tab: Hashable {
        case dashboard, plants, gardens, tasks, profile
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationStack {
                DashboardView()
            }
            .tabItem { Label("Home", systemImage: "house.fill") }
            .tag(Tab.dashboard)

            NavigationStack {
                PlantsView()
            }
            .tabItem { Label("Plants", systemImage: "leaf.fill") }
            .tag(Tab.plants)

            NavigationStack {
                GardensView()
            }
            .tabItem { Label("Gardens", systemImage: "tree.fill") }
            .tag(Tab.gardens)

            NavigationStack {
                TasksView()
            }
            .tabItem { Label("Tasks", systemImage: "checklist") }
            .tag(Tab.tasks)

            NavigationStack {
                ProfileView()
            }
            .tabItem { Label("Profile", systemImage: "person.crop.circle") }
            .tag(Tab.profile)
        }
    }
}
