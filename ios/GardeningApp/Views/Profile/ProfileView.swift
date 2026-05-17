import SwiftUI

struct ProfileView: View {
    @EnvironmentObject private var auth: AuthViewModel
    @StateObject private var vm = ProfileViewModel()

    var body: some View {
        Form {
            if case let .signedIn(user) = auth.state {
                Section("Account") {
                    LabeledContent("Username", value: user.username)
                    LabeledContent("Email", value: user.email)
                    if user.isAdmin {
                        Label("Admin", systemImage: "checkmark.shield.fill")
                            .foregroundStyle(.purple)
                    }
                }
            }

            Section("Location") {
                TextField("ZIP code", text: stringBinding(\.zipCode))
                    .keyboardType(.numberPad)
                TextField("City", text: stringBinding(\.city))
                TextField("State", text: stringBinding(\.state))
                if let zone = vm.profile.plantHardinessZone, !zone.isEmpty {
                    LabeledContent("Hardiness zone", value: zone)
                }
            }

            Section("Garden Conditions") {
                Toggle("Has irrigation", isOn: boolBinding(\.hasIrrigation))
                HStack {
                    Text("Sunlight (hrs/day)")
                    Spacer()
                    TextField("0–24", value: $vm.profile.sunlightHours, format: .number)
                        .multilineTextAlignment(.trailing)
                        .keyboardType(.decimalPad)
                        .frame(width: 80)
                }
                HStack {
                    Text("Soil pH")
                    Spacer()
                    TextField("0–14", value: $vm.profile.soilPh, format: .number)
                        .multilineTextAlignment(.trailing)
                        .keyboardType(.decimalPad)
                        .frame(width: 80)
                }
            }

            if let zip = vm.profile.zipCode, !zip.isEmpty {
                Section {
                    NavigationLink {
                        WeatherView(zip: zip)
                    } label: {
                        Label("Local Weather", systemImage: "cloud.sun.fill")
                    }
                }
            }

            if let success = vm.successMessage {
                Section {
                    Label(success, systemImage: "checkmark.circle.fill")
                        .foregroundStyle(.green)
                }
            }
            if let error = vm.errorMessage {
                Section {
                    Label(error, systemImage: "exclamationmark.triangle")
                        .foregroundStyle(.red)
                }
            }

            Section {
                Button {
                    Task { await vm.save() }
                } label: {
                    HStack {
                        Spacer()
                        if vm.isSaving {
                            ProgressView()
                        } else {
                            Text("Save Profile").fontWeight(.semibold)
                        }
                        Spacer()
                    }
                }
                .disabled(vm.isSaving)
            }

            Section {
                Button(role: .destructive) {
                    auth.signOut()
                } label: {
                    Label("Sign Out", systemImage: "rectangle.portrait.and.arrow.right")
                }
            }
        }
        .navigationTitle("Profile")
        .task { await vm.load() }
        .overlay {
            if vm.isLoading && vm.profile == .empty {
                ProgressView()
            }
        }
    }

    private func stringBinding(_ keyPath: WritableKeyPath<UserProfile, String?>) -> Binding<String> {
        Binding(
            get: { vm.profile[keyPath: keyPath] ?? "" },
            set: { vm.profile[keyPath: keyPath] = $0 }
        )
    }

    private func boolBinding(_ keyPath: WritableKeyPath<UserProfile, Bool?>) -> Binding<Bool> {
        Binding(
            get: { vm.profile[keyPath: keyPath] ?? false },
            set: { vm.profile[keyPath: keyPath] = $0 }
        )
    }
}
