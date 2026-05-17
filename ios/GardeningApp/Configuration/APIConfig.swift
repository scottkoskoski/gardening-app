import Foundation

enum APIConfig {
    /// Base URL of the Flask backend. Override at launch via the
    /// `API_BASE_URL` environment variable (Xcode scheme) or
    /// `Info.plist` key `APIBaseURL`. Defaults to the typical Flask
    /// dev server reachable from the simulator.
    static var baseURL: URL {
        if let env = ProcessInfo.processInfo.environment["API_BASE_URL"],
           let url = URL(string: env) {
            return url
        }
        if let plistValue = Bundle.main.object(forInfoDictionaryKey: "APIBaseURL") as? String,
           let url = URL(string: plistValue) {
            return url
        }
        return URL(string: "http://127.0.0.1:5000")!
    }

    static var apiRoot: URL { baseURL.appendingPathComponent("api") }
}
