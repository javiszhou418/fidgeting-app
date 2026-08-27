import SwiftUI

@_cdecl("UnitySendMessage")
public func EnvironmentWallpaperPickerPreviewUnitySendMessage(
    _ object: UnsafePointer<CChar>?,
    _ method: UnsafePointer<CChar>?,
    _ value: UnsafePointer<CChar>?) {
}

@main
struct EnvironmentWallpaperPickerNativePreviewApp: App {
    private let mode: EnvironmentWallpaperPickerNativePreviewRoot.Mode

    init() {
        ProductTypography.configureUIKitAppearance()
        let bundleMode = Bundle.main.bundleIdentifier?
            .split(separator: ".")
            .last
            .flatMap { EnvironmentWallpaperPickerNativePreviewRoot.Mode(
                rawValue: String($0)) }
        let environmentValue = ProcessInfo.processInfo.environment[
            "FIDGET_WALLPAPER_PREVIEW_MODE"]
        let argumentValue = ProcessInfo.processInfo.arguments
            .first { $0.hasPrefix("--mode=") }?
            .replacingOccurrences(of: "--mode=", with: "")
        let requestedMode = [environmentValue, argumentValue]
            .compactMap { $0?.lowercased() }
            .compactMap(EnvironmentWallpaperPickerNativePreviewRoot.Mode.init(rawValue:))
            .first
        mode = requestedMode ?? bundleMode ?? .adaptive
    }

    var body: some Scene {
        WindowGroup {
            EnvironmentWallpaperPickerNativePreviewRoot(mode: mode)
        }
    }
}
