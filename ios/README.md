# Gardening iOS App

A native SwiftUI iOS app that consumes the existing Flask backend. It mirrors
and extends the React frontend: auth, plant browsing, garden management,
journal entries, tasks, recommendations, and weather/hardiness zone info.

## Requirements

- Xcode 15+ (iOS 17 SDK)
- iOS 17 device or simulator
- [XcodeGen](https://github.com/yonaskolb/XcodeGen) (only to generate the
  Xcode project — `brew install xcodegen`)
- The Flask backend running locally (see top-level README) at
  `http://127.0.0.1:5000`

## Quick start

```bash
cd ios
xcodegen generate          # creates GardeningApp.xcodeproj from project.yml
open GardeningApp.xcodeproj
```

Pick the *GardeningApp* scheme and a simulator, then ⌘R.

### Pointing at a non-default backend

`API_BASE_URL` is read at launch. The simulator can hit `127.0.0.1` directly,
but a real device on Wi-Fi needs your Mac's LAN IP:

1. *Product → Scheme → Edit Scheme → Run → Arguments → Environment Variables*
2. Add `API_BASE_URL` = `http://192.168.1.42:5000` (your IP)

You can also set `APIBaseURL` in `Info.plist` for a fixed default.

## Project layout

```
GardeningApp/
├── GardeningAppApp.swift       # App entry, AuthViewModel injection
├── Configuration/APIConfig.swift
├── Models/                     # Codable types matching backend schemas
├── Services/                   # API client, Keychain, per-domain services
├── ViewModels/                 # ObservableObject layer (Auth, Dashboard, …)
└── Views/
    ├── Auth/                   # Login, Register, landing
    ├── Dashboard/              # Tab container + home dashboard
    ├── Plants/                 # Catalog, filters, detail, add-to-garden
    ├── Gardens/                # List, detail, form, map
    ├── Journal/                # Per-garden journal
    ├── Tasks/                  # Smart task list
    ├── Weather/                # Current + forecast + frost dates
    ├── Profile/                # Account + preferences
    └── Components/             # Reusable UI bits (badges, async images…)
```

## Features

- **Auth**: register, login, JWT stored in Keychain. 401s clear the session
  automatically.
- **Dashboard**: greeting, weather snapshot, top tasks, recommended plants.
- **Plants**: search, filter by zone/sunlight/water/season/space/greenhouse/
  container, detail view with full growing info.
- **Add-to-garden**: pick garden, growth stage, optional harvest date.
- **Gardens**: CRUD with form, swipe-to-delete, detail page with plants list,
  garden map (grid view), journal entry point.
- **Tasks**: smart recurring + frost/seasonal reminders with priority +
  due-date filter.
- **Weather**: current conditions, 7-day forecast, frost dates, hardiness
  zone lookup.
- **Profile**: zip/city/state, sunlight hours, soil pH, irrigation toggle.
  Saving the ZIP triggers a hardiness-zone lookup on the backend.

## Testing

Unit tests live in `GardeningAppTests/`. Run with `⌘U` in Xcode, or:

```bash
xcodebuild -project GardeningApp.xcodeproj -scheme GardeningApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' test
```

## Notes

- All networking goes through `APIClient` which prepends `/api` and the
  bearer token.
- Date strings from the backend are kept as `String` and formatted at the
  display layer; this keeps the JSON decoder strategy uniform.
- The garden map view is read-only on iOS for now — placement edits remain
  on the web. The cell grid renders existing assignments from the backend.
- The simulator can talk to `127.0.0.1` (the host loopback), but ATS allows
  local networking via `NSAllowsLocalNetworking = true` in `Info.plist`.
