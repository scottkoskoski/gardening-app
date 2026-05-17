import SwiftUI

struct LoginView: View {
    @EnvironmentObject private var auth: AuthViewModel
    @State private var username = ""
    @State private var password = ""
    @FocusState private var focusedField: Field?

    enum Field { case username, password }

    var body: some View {
        Form {
            Section("Sign In") {
                TextField("Username", text: $username)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .focused($focusedField, equals: .username)
                    .submitLabel(.next)
                    .onSubmit { focusedField = .password }

                SecureField("Password", text: $password)
                    .focused($focusedField, equals: .password)
                    .submitLabel(.go)
                    .onSubmit { submit() }
            }

            if let error = auth.errorMessage {
                Section {
                    Label(error, systemImage: "exclamationmark.triangle")
                        .foregroundStyle(.red)
                        .font(.callout)
                }
            }

            Section {
                Button(action: submit) {
                    HStack {
                        Spacer()
                        if auth.isWorking {
                            ProgressView()
                        } else {
                            Text("Sign In")
                                .fontWeight(.semibold)
                        }
                        Spacer()
                    }
                }
                .disabled(auth.isWorking || username.isEmpty || password.isEmpty)
            }
        }
        .navigationTitle("Sign In")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func submit() {
        Task { await auth.login(username: username, password: password) }
    }
}
