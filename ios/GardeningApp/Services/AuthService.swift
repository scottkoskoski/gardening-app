import Foundation

struct LoginRequest: Encodable {
    let username: String
    let password: String
}

struct RegisterRequest: Encodable {
    let username: String
    let email: String
    let password: String
}

@MainActor
final class AuthService {
    static let shared = AuthService()
    private init() {}

    private let api = APIClient.shared

    func login(username: String, password: String) async throws -> String {
        let response: AuthResponse = try await api.post(
            "users/login",
            body: LoginRequest(username: username, password: password)
        )
        return response.token
    }

    func register(username: String, email: String, password: String) async throws {
        let _: RegisterResponse = try await api.post(
            "users/register",
            body: RegisterRequest(username: username, email: email, password: password)
        )
    }

    func currentUser() async throws -> User {
        try await api.get("users/get_user")
    }
}
