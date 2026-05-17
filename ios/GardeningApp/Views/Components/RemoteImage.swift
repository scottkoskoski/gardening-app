import SwiftUI

/// Async image with a tasteful placeholder when the URL is missing or fails.
struct RemoteImage: View {
    let urlString: String?
    var systemPlaceholder: String = "leaf"

    var body: some View {
        if let urlString,
           let url = URL(string: urlString),
           url.scheme != nil {
            AsyncImage(url: url) { phase in
                switch phase {
                case .empty:
                    ZStack {
                        Color.green.opacity(0.08)
                        ProgressView()
                    }
                case .success(let image):
                    image.resizable().scaledToFill()
                case .failure:
                    placeholder
                @unknown default:
                    placeholder
                }
            }
        } else {
            placeholder
        }
    }

    private var placeholder: some View {
        ZStack {
            LinearGradient(
                colors: [.green.opacity(0.25), .green.opacity(0.08)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            Image(systemName: systemPlaceholder)
                .font(.title)
                .foregroundStyle(.green)
        }
    }
}
