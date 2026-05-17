import Foundation
import SwiftUI

enum AuthState: Equatable {
    case loading
    case signedOut
    case signedIn(User)
}

@MainActor
final class AuthViewModel: ObservableObject, TokenProviding {
    @Published var state: AuthState = .loading
    @Published var isWorking = false
    @Published var errorMessage: String?

    private let tokenAccount = "authToken"
    private let keychain = KeychainHelper.shared

    private(set) var token: String?

    init() {
        APIClient.shared.tokenProvider = self
    }

    func bootstrap() async {
        if let saved = keychain.read(account: tokenAccount) {
            token = saved
            do {
                let user = try await AuthService.shared.currentUser()
                state = .signedIn(user)
            } catch {
                await clear()
                state = .signedOut
            }
        } else {
            state = .signedOut
        }
    }

    func login(username: String, password: String) async {
        guard !isWorking else { return }
        isWorking = true
        errorMessage = nil
        defer { isWorking = false }
        do {
            let received = try await AuthService.shared.login(username: username, password: password)
            keychain.save(received, account: tokenAccount)
            token = received
            let user = try await AuthService.shared.currentUser()
            state = .signedIn(user)
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }

    func register(username: String, email: String, password: String) async -> Bool {
        guard !isWorking else { return false }
        isWorking = true
        errorMessage = nil
        defer { isWorking = false }
        do {
            try await AuthService.shared.register(username: username, email: email, password: password)
            await login(username: username, password: password)
            return state != .signedOut
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            return false
        }
    }

    func signOut() {
        keychain.delete(account: tokenAccount)
        token = nil
        state = .signedOut
    }

    /// `TokenProviding` conformance — called when the API gets a 401.
    func clear() async {
        keychain.delete(account: tokenAccount)
        token = nil
        state = .signedOut
    }
}
