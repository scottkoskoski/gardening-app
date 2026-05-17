import Foundation

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
}

enum APIError: LocalizedError {
    case invalidURL
    case unauthorized
    case server(status: Int, message: String?)
    case decoding(Error)
    case transport(Error)
    case empty

    var errorDescription: String? {
        switch self {
        case .invalidURL: "Invalid URL."
        case .unauthorized: "Your session has expired. Please sign in again."
        case .server(_, let message): message ?? "The server returned an error."
        case .decoding: "Unexpected response format."
        case .transport(let err): err.localizedDescription
        case .empty: "Empty response."
        }
    }
}

private struct ErrorBody: Decodable {
    let error: String?
    let message: String?
}

protocol TokenProviding: AnyObject {
    var token: String? { get }
    func clear() async
}

/// Generic JSON API client for the Flask backend.
@MainActor
final class APIClient {
    static let shared = APIClient()

    var tokenProvider: TokenProviding?
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    private let session: URLSession

    private init() {
        decoder = JSONDecoder()
        encoder = JSONEncoder()

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        session = URLSession(configuration: config)
    }

    func get<T: Decodable>(_ path: String, query: [String: String] = [:]) async throws -> T {
        try await request(path: path, method: .get, query: query, body: Optional<EmptyBody>.none)
    }

    func post<B: Encodable, T: Decodable>(_ path: String, body: B) async throws -> T {
        try await request(path: path, method: .post, query: [:], body: body)
    }

    func postExpectingNoBody<B: Encodable>(_ path: String, body: B) async throws {
        let _: EmptyResponse = try await request(path: path, method: .post, query: [:], body: body)
    }

    func put<B: Encodable, T: Decodable>(_ path: String, body: B) async throws -> T {
        try await request(path: path, method: .put, query: [:], body: body)
    }

    func delete<T: Decodable>(_ path: String) async throws -> T {
        try await request(path: path, method: .delete, query: [:], body: Optional<EmptyBody>.none)
    }

    func deleteVoid(_ path: String) async throws {
        let _: EmptyResponse = try await request(path: path, method: .delete, query: [:], body: Optional<EmptyBody>.none)
    }

    private func request<B: Encodable, T: Decodable>(
        path: String,
        method: HTTPMethod,
        query: [String: String],
        body: B?
    ) async throws -> T {
        guard var components = URLComponents(
            url: APIConfig.apiRoot.appendingPathComponent(path),
            resolvingAgainstBaseURL: false
        ) else { throw APIError.invalidURL }

        if !query.isEmpty {
            components.queryItems = query.map { URLQueryItem(name: $0.key, value: $0.value) }
        }

        guard let url = components.url else { throw APIError.invalidURL }

        var req = URLRequest(url: url)
        req.httpMethod = method.rawValue
        req.setValue("application/json", forHTTPHeaderField: "Accept")
        if let token = tokenProvider?.token {
            req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
            req.httpBody = try encoder.encode(body)
        }

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: req)
        } catch {
            throw APIError.transport(error)
        }

        guard let http = response as? HTTPURLResponse else {
            throw APIError.empty
        }

        if http.statusCode == 401 {
            await tokenProvider?.clear()
            throw APIError.unauthorized
        }

        guard (200..<300).contains(http.statusCode) else {
            let message = (try? decoder.decode(ErrorBody.self, from: data))?.error
                ?? (try? decoder.decode(ErrorBody.self, from: data))?.message
                ?? String(data: data, encoding: .utf8)
            throw APIError.server(status: http.statusCode, message: message)
        }

        if T.self == EmptyResponse.self {
            return EmptyResponse() as! T
        }

        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decoding(error)
        }
    }
}

struct EmptyBody: Encodable {}
struct EmptyResponse: Decodable {}
