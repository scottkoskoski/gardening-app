import SwiftUI

/// Reusable shell that shows a loading spinner, error message, or content.
struct AsyncContentView<Content: View>: View {
    let isLoading: Bool
    let errorMessage: String?
    let onRetry: (() -> Void)?
    @ViewBuilder let content: Content

    init(
        isLoading: Bool,
        errorMessage: String?,
        onRetry: (() -> Void)? = nil,
        @ViewBuilder content: () -> Content
    ) {
        self.isLoading = isLoading
        self.errorMessage = errorMessage
        self.onRetry = onRetry
        self.content = content()
    }

    var body: some View {
        ZStack {
            content

            if isLoading {
                ProgressView()
                    .controlSize(.large)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(.ultraThinMaterial)
            } else if let errorMessage {
                VStack(spacing: 12) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                        .foregroundStyle(.orange)
                    Text(errorMessage)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(.secondary)
                        .padding(.horizontal)
                    if let onRetry {
                        Button("Try Again", action: onRetry)
                            .buttonStyle(.borderedProminent)
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
    }
}
