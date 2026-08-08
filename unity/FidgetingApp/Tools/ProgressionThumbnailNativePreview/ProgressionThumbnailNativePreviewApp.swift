import SwiftUI

@_cdecl("UnitySendMessage")
public func ProgressionThumbnailPreviewUnitySendMessage(
    _ object: UnsafePointer<CChar>?,
    _ method: UnsafePointer<CChar>?,
    _ value: UnsafePointer<CChar>?) {
}

@main
struct ProgressionThumbnailNativePreviewApp: App {
    private let mode: ProgressionThumbnailNativePreviewRoot.Mode

    init() {
        ProductTypography.configureUIKitAppearance()
        let modeValue = ProcessInfo.processInfo.arguments
            .first { $0.hasPrefix("--mode=") }?
            .replacingOccurrences(of: "--mode=", with: "") ?? "hud"
        mode = ProgressionThumbnailNativePreviewRoot.Mode(
            rawValue: modeValue) ?? .hud
    }

    var body: some Scene {
        WindowGroup {
            ProgressionThumbnailNativePreviewRoot(mode: mode)
        }
    }
}
