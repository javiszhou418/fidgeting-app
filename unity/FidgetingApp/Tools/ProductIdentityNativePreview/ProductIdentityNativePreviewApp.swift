import SwiftUI

@_cdecl("UnitySendMessage")
public func ProductIdentityPreviewUnitySendMessage(
    _ object: UnsafePointer<CChar>?,
    _ method: UnsafePointer<CChar>?,
    _ value: UnsafePointer<CChar>?) {
}

@main
struct ProductIdentityNativePreviewApp: App {
    private let mode: ProductIdentityNativePreviewRoot.Mode

    init() {
        ProductTypography.configureUIKitAppearance()
        let modeValue = ProcessInfo.processInfo.arguments
            .first { $0.hasPrefix("--model=") }?
            .replacingOccurrences(of: "--model=", with: "") ?? "gold"
        mode = ProductIdentityNativePreviewRoot.Mode(rawValue: modeValue) ?? .gold
    }

    var body: some Scene {
        WindowGroup {
            ProductIdentityNativePreviewRoot(mode: mode)
        }
    }
}
