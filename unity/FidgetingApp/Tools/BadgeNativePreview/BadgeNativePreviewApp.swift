import SwiftUI

@_cdecl("UnitySendMessage")
public func BadgeNativePreviewUnitySendMessage(
    _ object: UnsafePointer<CChar>?,
    _ method: UnsafePointer<CChar>?,
    _ value: UnsafePointer<CChar>?) {
}

@main
struct BadgeNativePreviewApp: App {
    private let mode: BadgeNativePreviewRoot.Mode

    init() {
        ProductTypography.configureUIKitAppearance()
        let value = ProcessInfo.processInfo.arguments
            .first { $0.hasPrefix("--mode=") }?
            .replacingOccurrences(of: "--mode=", with: "") ?? "catalog"
        mode = BadgeNativePreviewRoot.Mode(rawValue: value) ?? .catalog
    }

    var body: some Scene {
        WindowGroup {
            BadgeNativePreviewRoot(mode: mode)
                .onAppear {
                    switch mode {
                    case .share:
                        BadgeNativePreviewRoot.renderShareCard { image in
                            guard let data = image?.pngData(),
                                  let documents = FileManager.default.urls(
                                    for: .documentDirectory,
                                    in: .userDomainMask).first else { return }
                            try? data.write(
                                to: documents.appendingPathComponent(
                                    "badge-share-card-1080.png"),
                                options: .atomic)
                        }
                    default:
                        break
                    }
                }
        }
    }
}
