import SwiftUI

@_cdecl("UnitySendMessage")
public func FanCardCatalogPreviewUnitySendMessage(
    _ object: UnsafePointer<CChar>?,
    _ method: UnsafePointer<CChar>?,
    _ value: UnsafePointer<CChar>?) {
}

@main
struct FanCardCatalogPreviewApp: App {
    var body: some Scene {
        WindowGroup {
            FanCardCatalogNativePreviewRoot()
        }
    }
}
