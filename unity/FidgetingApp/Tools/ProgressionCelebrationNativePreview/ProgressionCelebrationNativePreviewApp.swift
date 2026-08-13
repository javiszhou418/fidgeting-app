import SwiftUI

@_cdecl("UnitySendMessage")
public func ProgressionCelebrationPreviewUnitySendMessage(
    _ object: UnsafePointer<CChar>?,
    _ method: UnsafePointer<CChar>?,
    _ value: UnsafePointer<CChar>?) {
}

@main
struct ProgressionCelebrationNativePreviewApp: App {
    private let mode: ProgressionCelebrationNativePreviewRoot.Mode
    private let reduceMotion: Bool

    init() {
        ProductTypography.configureUIKitAppearance()
        let arguments = ProcessInfo.processInfo.arguments
        let rawValue = arguments
            .first { $0.hasPrefix("--mode=") }?
            .replacingOccurrences(of: "--mode=", with: "") ?? "offline"
        mode = ProgressionCelebrationNativePreviewRoot.Mode(rawValue: rawValue)
            ?? .offline
        reduceMotion = arguments.contains("--reduce-motion")
    }

    var body: some Scene {
        WindowGroup {
            ProgressionCelebrationNativePreviewRoot(mode: mode)
                .environment(\.progressionReduceMotionPreviewOverride, reduceMotion)
        }
    }
}
