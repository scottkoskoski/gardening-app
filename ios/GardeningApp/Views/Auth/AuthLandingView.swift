import SwiftUI

struct AuthLandingView: View {
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Spacer()
                VStack(spacing: 12) {
                    Image(systemName: "leaf.circle.fill")
                        .font(.system(size: 80))
                        .foregroundStyle(.green)
                    Text("Welcome to Gardening")
                        .font(.largeTitle.bold())
                    Text("Plan your garden, track plants, and get personalized recommendations for your hardiness zone.")
                        .multilineTextAlignment(.center)
                        .foregroundStyle(.secondary)
                        .padding(.horizontal, 32)
                }

                Spacer()

                VStack(spacing: 12) {
                    NavigationLink {
                        LoginView()
                    } label: {
                        Text("Sign In")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)

                    NavigationLink {
                        RegisterView()
                    } label: {
                        Text("Create Account")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                    .controlSize(.large)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 32)
            }
            .background(
                LinearGradient(
                    colors: [.green.opacity(0.08), .clear],
                    startPoint: .top,
                    endPoint: .bottom
                )
            )
        }
    }
}
