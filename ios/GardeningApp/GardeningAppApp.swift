import SwiftUI

@main
struct GardeningAppApp: App {
    @StateObject private var authViewModel = AuthViewModel()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(authViewModel)
                .tint(.green)
        }
    }
}

struct RootView: View {
    @EnvironmentObject private var auth: AuthViewModel

    var body: some View {
        Group {
            switch auth.state {
            case .loading:
                ProgressView("Loading…")
                    .progressViewStyle(.circular)
            case .signedOut:
                AuthLandingView()
            case .signedIn:
                RootTabView()
            }
        }
        .task { await auth.bootstrap() }
        .animation(.easeInOut, value: auth.state)
    }
}
