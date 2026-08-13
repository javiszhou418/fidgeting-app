import SwiftUI

@_cdecl("UnitySendMessage")
public func HapticSettingsPreviewUnitySendMessage(
    _ object: UnsafePointer<CChar>?,
    _ method: UnsafePointer<CChar>?,
    _ value: UnsafePointer<CChar>?) {
}

@main
struct HapticSettingsNativePreviewApp: App {
    var body: some Scene {
        WindowGroup {
            HapticSettingsSaveNativePreviewRoot()
        }
    }
}
