import SwiftUI

@_cdecl("UnitySendMessage")
public func PreviewUnitySendMessage(
    _ objectName: UnsafePointer<CChar>,
    _ methodName: UnsafePointer<CChar>,
    _ message: UnsafePointer<CChar>) {}

@main
struct GachaShippingNativePreviewApp: App {
    var body: some Scene {
        WindowGroup {
            GachaShippingPreviewHost()
        }
    }
}

private struct GachaShippingPreviewHost: View {
    @State private var showingStore = true

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            Button("打开机巧工坊") { showingStore = true }
                .foregroundColor(.black)
                .padding(.horizontal, 22)
                .frame(height: 52)
                .background(Color.white, in: RoundedRectangle(cornerRadius: 17))
        }
        .sheet(isPresented: $showingStore) {
            GachaStoreView()
        }
        .onAppear {
            GachaStoreModel.shared.ingest(
                catalog: Self.catalog,
                snapshot: Self.snapshot,
                receipt: "")
            if ProcessInfo.processInfo.arguments.contains("--preview-reveal") {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.65) {
                    GachaStoreModel.shared.ingest(
                        catalog: "",
                        snapshot: "",
                        receipt: Self.receipt)
                }
            }
        }
    }

    private static let catalog = """
    series\tlaunch-series\t启航系列\t0.70\t0.24\t0.05\t0.01
    prize\tblue-steel\tlaunch-series\t1\t0\t蓝钢冲刷
    prize\tcopper-strata\tlaunch-series\t2\t0\t铜层岩理
    prize\taurora-vein\tlaunch-series\t3\t0\t极光矿脉
    prize\tmechanical-mark\tlaunch-series\t0\t1\t机巧标记
    prize\tgraphite-base\tlaunch-series\t1\t2\t石墨展示底座
    """

    private static let snapshot = """
    wallet\t8\t2480
    series-state\tlaunch-series\t18\t42\t24\t64
    owned\tblue-steel|mechanical-mark
    """

    private static let receipt = """
    result\tok
    row\taurora-vein\t极光矿脉\t3\t0\t1\t0\t0\t0\t0
    """
}
