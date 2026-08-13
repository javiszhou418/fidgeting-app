import SwiftUI

@_cdecl("UnitySendMessage")
public func DisplayCasePreviewUnitySendMessage(
    _ object: UnsafePointer<CChar>?,
    _ method: UnsafePointer<CChar>?,
    _ value: UnsafePointer<CChar>?) {
}

@main
struct DisplayCaseNativePreviewApp: App {
    var body: some Scene {
        WindowGroup {
            PremiumDisplayCaseNativePreviewRoot()
        }
    }
}
