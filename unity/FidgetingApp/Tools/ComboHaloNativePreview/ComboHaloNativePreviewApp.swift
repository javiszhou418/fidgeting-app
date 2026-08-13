import SwiftUI

@_cdecl("UnitySendMessage")
public func ComboHaloPreviewUnitySendMessage(
    _ object: UnsafePointer<CChar>?,
    _ method: UnsafePointer<CChar>?,
    _ value: UnsafePointer<CChar>?) {
}

@main
struct ComboHaloNativePreviewApp: App {
    private let mode: ComboHaloNativePreviewRoot.Mode
    private let frozenProgress: CGFloat
    private let sceneView: ComboHaloNativePreviewRoot.SceneView
    private let comboCount: Int

    init() {
        let arguments = ProcessInfo.processInfo.arguments
        let modeValue = arguments
            .first { $0.hasPrefix("--mode=") }?
            .replacingOccurrences(of: "--mode=", with: "") ?? "effect"
        mode = ComboHaloNativePreviewRoot.Mode(rawValue: modeValue) ?? .effect

        let progressValue = arguments
            .first { $0.hasPrefix("--progress=") }?
            .replacingOccurrences(of: "--progress=", with: "") ?? "0.38"
        frozenProgress = CGFloat(Double(progressValue) ?? 0.38)

        let sceneViewValue = arguments
            .first { $0.hasPrefix("--view=") }?
            .replacingOccurrences(of: "--view=", with: "") ?? "hero"
        sceneView = ComboHaloNativePreviewRoot.SceneView(
            rawValue: sceneViewValue) ?? .hero

        let comboValue = arguments
            .first { $0.hasPrefix("--combo=") }?
            .replacingOccurrences(of: "--combo=", with: "") ?? "30"
        comboCount = max(10, Int(comboValue) ?? 30)
    }

    var body: some Scene {
        WindowGroup {
            ComboHaloNativePreviewRoot(
                mode: mode,
                frozenProgress: frozenProgress,
                sceneView: sceneView,
                comboCount: comboCount)
        }
    }
}
