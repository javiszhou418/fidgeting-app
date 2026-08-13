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
        let bundleRequestsCyberpunk = Bundle.main.bundleIdentifier?
            .hasSuffix(".cyberpunk") == true
        let environmentValue = ProcessInfo.processInfo.environment[
            "FIDGET_WALLPAPER_PREVIEW_MODE"]
        let argumentValue = ProcessInfo.processInfo.arguments
            .first { $0.hasPrefix("--mode=") }?
            .replacingOccurrences(of: "--mode=", with: "")
        let requestsCyberpunk = [environmentValue, argumentValue]
            .compactMap { $0?.lowercased() }
            .contains { $0.contains("cyberpunk") }
        mode = bundleRequestsCyberpunk || requestsCyberpunk
            ? .cyberpunk
            : .canyon
    }

    var body: some Scene {
        WindowGroup {
            EnvironmentWallpaperPickerNativePreviewRoot(mode: mode)
        }
    }
}
