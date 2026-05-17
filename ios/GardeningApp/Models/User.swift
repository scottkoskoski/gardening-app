import Foundation

struct User: Codable, Identifiable, Equatable, Hashable {
    let id: Int
    let username: String
    let email: String
    let isAdmin: Bool
    let createdAt: String?
    let lastLoginAt: String?

    enum CodingKeys: String, CodingKey {
        case id, username, email
        case isAdmin = "is_admin"
        case createdAt = "created_at"
        case lastLoginAt = "last_login_at"
    }
}

struct AuthResponse: Codable {
    let token: String
    let message: String?
}

struct RegisterResponse: Codable {
    let message: String
    let userId: Int

    enum CodingKeys: String, CodingKey {
        case message
        case userId = "user_id"
    }
}
