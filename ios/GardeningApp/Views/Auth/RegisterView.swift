import SwiftUI

struct RegisterView: View {
    @EnvironmentObject private var auth: AuthViewModel
    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @State private var confirm = ""

    private var passwordsMatch: Bool { password == confirm }
    private var canSubmit: Bool {
        !username.isEmpty
        && !email.isEmpty
        && password.count >= 8
        && passwordsMatch
        && !auth.isWorking
    }

    var body: some View {
        Form {
            Section("Account") {
                TextField("Username", text: $username)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                TextField("Email", text: $email)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
            }

            Section("Password") {
                SecureField("Password (min 8 chars)", text: $password)
                SecureField("Confirm Password", text: $confirm)
                if !confirm.isEmpty && !passwordsMatch {
                    Label("Passwords don't match", systemImage: "xmark.circle")
                        .foregroundStyle(.red)
                        .font(.caption)
                }
            } footer: {
                Text("Must contain upper and lower case letters, a number, and a special character.")
                    .font(.caption)
            }

            if let error = auth.errorMessage {
                Section {
                    Label(error, systemImage: "exclamationmark.triangle")
                        .foregroundStyle(.red)
                        .font(.callout)
                }
            }

            Section {
                Button {
                    Task { await auth.register(username: username, email: email, password: password) }
                } label: {
                    HStack {
                        Spacer()
                        if auth.isWorking {
                            ProgressView()
                        } else {
                            Text("Create Account").fontWeight(.semibold)
                        }
                        Spacer()
                    }
                }
                .disabled(!canSubmit)
            }
        }
        .navigationTitle("Create Account")
        .navigationBarTitleDisplayMode(.inline)
    }
}
