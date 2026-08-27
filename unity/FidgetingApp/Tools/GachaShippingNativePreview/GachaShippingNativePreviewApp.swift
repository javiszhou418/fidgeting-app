import SwiftUI
import UIKit

#if canImport(RiveRuntime)
import RiveRuntime
#endif

@_cdecl("UnitySendMessage")
public func PreviewUnitySendMessage(
    _ objectName: UnsafePointer<CChar>,
    _ methodName: UnsafePointer<CChar>,
    _ message: UnsafePointer<CChar>
) {
#if DEBUG
    let method = String(cString: methodName)
    guard method == "DrawGachaFromNativeUi",
          ProcessInfo.processInfo.arguments.contains(
            "--preview-authoritative-receipt") else { return }

    let payload = String(cString: message)
    guard let requestID = payload.split(separator: "|").first,
          !requestID.isEmpty else { return }

    Task { @MainActor in
        try? await Task.sleep(nanoseconds: 450_000_000)
        GachaStoreModel.shared.ingest(
            catalog: "",
            snapshot: "",
            receipt: """
            result\t\(requestID)\tok
            row\taurora-vein\t极光矿脉\t3\t0\t1\t0\t0\t0\t0
            """)
        print("[GachaPreview] authoritative-receipt request=\(requestID)")
    }
#endif
}

@main
struct GachaShippingNativePreviewApp: App {
    init() {
        ProductTypography.registerBundledFontIfNeeded()
#if DEBUG && canImport(RiveRuntime)
        if ProcessInfo.processInfo.arguments.contains("--preview-rive-diagnostics") {
            GachaRivePreviewDiagnostics.printCanonicalAssetInventory()
        }
#endif
    }

    var body: some Scene {
        WindowGroup {
            if Self.sharedSplitRiveDiagnosticRequested {
#if canImport(RiveRuntime)
                GachaSharedSplitRiveDiagnosticHost()
#else
                Text("RiveRuntime unavailable")
#endif
            } else if let diagnosticArtboards = Self.riveDiagnosticArtboards {
#if canImport(RiveRuntime)
                GachaSplitRiveDiagnosticHost(artboardNames: diagnosticArtboards)
#else
                Text("RiveRuntime unavailable")
#endif
            } else if let progress = Self.allTierComparisonProgress {
                GachaPackTierShippingComparison(tearProgress: progress)
            } else {
                GachaShippingPreviewHost()
            }
        }
    }

    private static var allTierComparisonProgress: CGFloat? {
        guard let argument = ProcessInfo.processInfo.arguments.first(
            where: { $0.hasPrefix("--preview-all-pack-tiers=") }),
            let rawProgress = Double(argument.split(separator: "=").last ?? "") else {
            return nil
        }
        return CGFloat(min(max(rawProgress, 0), 1))
    }

    private static var riveDiagnosticArtboards: [String]? {
        if let argument = ProcessInfo.processInfo.arguments.first(
            where: { $0.hasPrefix("--preview-rive-artboard=") }) {
            let name = String(argument.dropFirst("--preview-rive-artboard=".count))
            return name.isEmpty ? nil : [name]
        }
        if ProcessInfo.processInfo.arguments.contains("--preview-rive-background-only") {
            return ["background/mint-slab"]
        }
        if ProcessInfo.processInfo.arguments.contains("--preview-rive-foreground-only") {
            return ["foreground/mint-slab"]
        }
        return nil
    }

    private static var sharedSplitRiveDiagnosticRequested: Bool {
        ProcessInfo.processInfo.arguments.contains("--preview-rive-split-only")
    }
}

#if DEBUG && canImport(RiveRuntime)
private enum GachaRivePreviewDiagnostics {
    static func printCanonicalAssetInventory() {
        RiveLogger.isEnabled = true
        RiveLogger.categories = .all
        RiveLogger.levels = .all

        let viewModel = RiveViewModel(
            fileName: "gacha-single-draw-jumbotron",
            stateMachineName: nil,
            autoPlay: false,
            loadCdn: true)
        guard let model = viewModel.riveModel else {
            print("[GachaRiveDiagnostic] missing-model")
            return
        }
        let file = model.riveFile
        print("[GachaRiveDiagnostic] artboards=\(viewModel.artboardNames())")
        print("[GachaRiveDiagnostic] selected-artboard=\(model.artboard.name()) bounds=\(model.artboard.bounds())")
        print("[GachaRiveDiagnostic] state-machines=\(model.artboard.stateMachineNames())")
        print("[GachaRiveDiagnostic] animations=\(model.artboard.animationNames())")
        print("[GachaRiveDiagnostic] selected-state-machine=\(model.stateMachine?.name() ?? "nil")")
        print("[GachaRiveDiagnostic] view-model-count=\(file.viewModelCount)")

        for index in 0..<file.viewModelCount {
            guard let definition = file.viewModel(at: index) else { continue }
            let properties = definition.properties.map {
                "\($0.name):\($0.type.rawValue)"
            }
            print("[GachaRiveDiagnostic] view-model[\(index)]=\(definition.name) instances=\(definition.instanceNames) properties=\(properties)")
        }

        for artboardName in file.artboardNames() {
            if let artboard = try? file.artboard(fromName: artboardName) {
                print("[GachaRiveDiagnostic] artboard=\(artboardName) bounds=\(artboard.bounds()) state-machines=\(artboard.stateMachineNames()) animations=\(artboard.animationNames())")
            }
        }

        if let definition = file.defaultViewModel(for: model.artboard),
           let instance = definition.createDefaultInstance() {
            print("[GachaRiveDiagnostic] default-view-model=\(definition.name) instance=\(instance.name)")
            print("[GachaRiveDiagnostic] root-purchase=\(instance.triggerProperty(fromPath: "purchase") != nil)")
            print("[GachaRiveDiagnostic] root-animationEnded=\(instance.triggerProperty(fromPath: "animationEnded") != nil)")
            print("[GachaRiveDiagnostic] nested-animationEnded=\(instance.triggerProperty(fromPath: "internalViewModel/animationEnded") != nil)")
        } else {
            print("[GachaRiveDiagnostic] default-view-model=nil")
        }
    }
}

@MainActor
private final class GachaSplitRiveDiagnosticLayer: RiveViewModel {
    private var instance: RiveDataBindingViewModel.Instance?
    private var endedProperty: RiveDataBindingViewModel.Instance.TriggerProperty?
    private var endedListener: UUID?
    private var backgroundBindableArtboard: RiveBindableArtboard?
    private var foregroundBindableArtboard: RiveBindableArtboard?
    private let layerName: String

    init(artboardName: String) {
        layerName = artboardName
        super.init(
            fileName: "gacha-single-draw-jumbotron",
            stateMachineName: nil,
            fit: .contain,
            alignment: .center,
            autoPlay: true,
            artboardName: artboardName,
            loadCdn: false,
            customLoader: { asset, embeddedData, factory in
                print(
                    "[GachaRiveSplitDiagnostic] asset name=\(asset.name()) "
                    + "file=\(asset.uniqueFilename()) embeddedBytes=\(embeddedData.count) "
                    + "cdn=\(asset.cdnBaseUrl())/\(asset.cdnUuid())")
                if let imageAsset = asset as? RiveImageAsset,
                   !embeddedData.isEmpty {
                    imageAsset.renderImage(factory.decodeImage(embeddedData))
                    print("[GachaRiveSplitDiagnostic] decoded-embedded-image name=\(asset.name())")
                    return true
                }
                return false
            })
        riveModel?.enableAutoBind { [weak self] instance in
            guard let self else { return }
            self.instance = instance
            self.endedProperty = instance.triggerProperty(fromPath: "animationEnded")
            self.endedListener = self.endedProperty?.addListener { [weak self] in
                guard let self else { return }
                print("[GachaRiveSplitDiagnostic] animation-ended layer=\(self.layerName)")
            }
            instance.stringProperty(fromPath: "titleName")?.value = "FIDGET ARCHIVE"
            instance.stringProperty(fromPath: "subtitle")?.value = "COLLECTION UNLOCKING"
            instance.stringProperty(fromPath: "promoteTag")?.value = "FIDGETING APP"
            instance.booleanProperty(fromPath: "isSelfBuyer")?.value = false
            instance.booleanProperty(fromPath: "isPromoted")?.value = false
            instance.booleanProperty(fromPath: "isReferral")?.value = false
            instance.booleanProperty(fromPath: "isNewBuyer")?.value = false
            instance.booleanProperty(fromPath: "isLooping")?.value = false
            instance.enumProperty(fromPath: "animationType")?.value =
                "T2_SPORTS_CARD_JUMBOTRON"
            if self.layerName == "background/mint-slab"
                || self.layerName == "foreground/mint-slab",
               let riveFile = self.riveModel?.riveFile,
               let backgroundArtboard = try? riveFile.bindableArtboard(
                    withName: "Slab-rotate-v01"),
               let foregroundArtboard = try? riveFile.bindableArtboard(
                    withName: "Coin_Slab_v09-sm") {
                self.backgroundBindableArtboard = backgroundArtboard
                self.foregroundBindableArtboard = foregroundArtboard
                let backgroundProperty = instance.artboardProperty(
                    fromPath: "backgroundArtboard")
                backgroundProperty?.setValue(backgroundArtboard)
                backgroundProperty?.setViewModelInstance(instance)
                let foregroundProperty = instance.artboardProperty(
                    fromPath: "foregroundArtboard")
                foregroundProperty?.setValue(foregroundArtboard)
                foregroundProperty?.setViewModelInstance(instance)
                print(
                    "[GachaRiveSplitDiagnostic] root-bindable-artboards "
                    + "layer=\(self.layerName) background=\(backgroundArtboard.name) "
                    + "foreground=\(foregroundArtboard.name)")
            }
            print("[GachaRiveSplitDiagnostic] bound layer=\(self.layerName)")
        }
    }

    func triggerPurchase() {
        guard let purchase = instance?.triggerProperty(fromPath: "purchase") else {
            print("[GachaRiveSplitDiagnostic] missing-purchase layer=\(layerName)")
            return
        }
        print("[GachaRiveSplitDiagnostic] purchase layer=\(layerName)")
        purchase.trigger()
    }
}

private struct GachaSplitRiveDiagnosticHost: View {
    @StateObject private var primary: GachaSplitRiveDiagnosticLayer
    @StateObject private var secondary = GachaSplitRiveDiagnosticLayer(
        artboardName: "foreground/mint-slab")
    private let showsSecondary: Bool

    init(artboardNames: [String]) {
        let primaryName = artboardNames.first ?? "background/mint-slab"
        _primary = StateObject(wrappedValue: GachaSplitRiveDiagnosticLayer(
            artboardName: primaryName))
        showsSecondary = artboardNames.count > 1
    }

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            primary.view().ignoresSafeArea().allowsHitTesting(false)
            if showsSecondary {
                secondary.view().ignoresSafeArea().allowsHitTesting(false)
            }
        }
        .task {
            try? await Task.sleep(nanoseconds: 1_500_000_000)
            guard !Task.isCancelled else { return }
            primary.triggerPurchase()
            if showsSecondary {
                secondary.triggerPurchase()
            }
        }
    }
}

@MainActor
private final class GachaSharedSplitRiveDiagnosticCoordinator: ObservableObject {
    let background: RiveViewModel
    let foreground: RiveViewModel

    private var instance: RiveDataBindingViewModel.Instance?
    private var endedProperty: RiveDataBindingViewModel.Instance.TriggerProperty?
    private var endedListener: UUID?
    private var playStateProperty: RiveDataBindingViewModel.Instance.EnumProperty?
    private var playStateListener: UUID?
    private var backgroundBindableArtboard: RiveBindableArtboard?
    private var foregroundBindableArtboard: RiveBindableArtboard?

    init() {
        let fileModel = try! RiveModel(
            fileName: "gacha-single-draw-jumbotron",
            loadCdn: false,
            customLoader: { asset, embeddedData, factory in
                guard let imageAsset = asset as? RiveImageAsset,
                      !embeddedData.isEmpty else { return false }
                imageAsset.renderImage(factory.decodeImage(embeddedData))
                print("[GachaRiveSharedDiagnostic] decoded-image name=\(asset.name()) bytes=\(embeddedData.count)")
                return true
            })
        let file = fileModel.riveFile
        let backgroundModel = RiveModel(riveFile: file)
        let foregroundModel = RiveModel(riveFile: file)
        background = RiveViewModel(
            backgroundModel,
            stateMachineName: "Main",
            fit: .cover,
            alignment: .center,
            autoPlay: true,
            artboardName: "background/mint-slab")
        foreground = RiveViewModel(
            foregroundModel,
            stateMachineName: "Main",
            fit: .cover,
            alignment: .center,
            autoPlay: true,
            artboardName: "foreground/mint-slab")

        guard let definition = file.viewModelNamed("MainViewModel"),
              let instance = definition.createDefaultInstance() else {
            print("[GachaRiveSharedDiagnostic] missing-main-instance")
            return
        }
        self.instance = instance
        backgroundModel.stateMachine?.bind(viewModelInstance: instance)
        foregroundModel.stateMachine?.bind(viewModelInstance: instance)
        endedProperty = instance.triggerProperty(fromPath: "animationEnded")
        endedListener = endedProperty?.addListener {
            print("[GachaRiveSharedDiagnostic] animation-ended")
        }
        instance.stringProperty(fromPath: "titleName")?.value = "FIDGET ARCHIVE"
        instance.stringProperty(fromPath: "subtitle")?.value = "COLLECTION UNLOCKING"
        instance.stringProperty(fromPath: "promoteTag")?.value = "FIDGETING APP"
        instance.booleanProperty(fromPath: "isSelfBuyer")?.value = false
        instance.booleanProperty(fromPath: "isPromoted")?.value = false
        instance.booleanProperty(fromPath: "isReferral")?.value = false
        instance.booleanProperty(fromPath: "isNewBuyer")?.value = false
        instance.booleanProperty(fromPath: "isLooping")?.value = false
        if let animationType = instance.enumProperty(fromPath: "animationType") {
            print(
                "[GachaRiveSharedDiagnostic] animation-type-before "
                + "value=\(animationType.value) values=\(animationType.values)")
            animationType.value = "T2_SPORTS_CARD_JUMBOTRON"
            print(
                "[GachaRiveSharedDiagnostic] animation-type-after "
                + "value=\(animationType.value) index=\(animationType.valueIndex)")
        } else {
            print("[GachaRiveSharedDiagnostic] missing-animation-type")
        }
        if let backgroundArtboard = try? file.bindableArtboard(
                withName: "Slab-rotate-v01"),
           let foregroundArtboard = try? file.bindableArtboard(
                withName: "Coin_Slab_v09-sm") {
            backgroundBindableArtboard = backgroundArtboard
            foregroundBindableArtboard = foregroundArtboard
            let backgroundProperty = instance.artboardProperty(
                fromPath: "backgroundArtboard")
            backgroundProperty?.setValue(backgroundArtboard)
            backgroundProperty?.setViewModelInstance(instance)
            let foregroundProperty = instance.artboardProperty(
                fromPath: "foregroundArtboard")
            foregroundProperty?.setValue(foregroundArtboard)
            foregroundProperty?.setViewModelInstance(instance)
            print(
                "[GachaRiveSharedDiagnostic] bindable-artboards "
                + "background=\(backgroundArtboard.name) "
                + "foreground=\(foregroundArtboard.name)")
        }
        if let internalViewModel = instance.viewModelInstanceProperty(
            fromPath: "internalViewModel"),
           let playState = internalViewModel.enumProperty(fromPath: "playState") {
            playStateProperty = playState
            playStateListener = playState.addListener { value in
                print("[GachaRiveSharedDiagnostic] play-state-changed value=\(value)")
            }
            print(
                "[GachaRiveSharedDiagnostic] internal-play-state "
                + "value=\(playState.value) values=\(playState.values)")
        }
        print("[GachaRiveSharedDiagnostic] bound-shared-instance")
    }

    func triggerPurchase() {
        print("[GachaRiveSharedDiagnostic] purchase")
        instance?.triggerProperty(fromPath: "purchase")?.trigger()
    }
}

private struct GachaSharedSplitRiveDiagnosticHost: View {
    @StateObject private var playback = GachaSharedSplitRiveDiagnosticCoordinator()

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            playback.background.view().ignoresSafeArea().allowsHitTesting(false)
            playback.foreground.view().ignoresSafeArea().allowsHitTesting(false)
        }
        .task {
            try? await Task.sleep(nanoseconds: 1_500_000_000)
            guard !Task.isCancelled else { return }
            playback.triggerPurchase()
        }
    }
}
#endif

private struct GachaShippingPreviewHost: View {
    @State private var showingStore = true
    @State private var premiumHandoffPrizeID: String?

    var body: some View {
        previewContent
            .sheet(isPresented: $showingStore) {
                GachaStoreView()
            }
            .onAppear(perform: configurePreview)
            .onDisappear {
                GachaShippingRevealContinuation.preparePremiumDisplayCase = nil
                GachaShippingRevealContinuation.cancelPreparedDisplayCase = nil
            }
    }

    @ViewBuilder
    private var previewContent: some View {
        ZStack {
            // Standing in for the real Library/scene background so the
            // storefront sheet's frosted-material chrome has something
            // behind it to actually blur — flat black makes any Material
            // look identical to a plain opacity fill.
            if let url = Bundle.main.url(
                forResource: "scene-wallpaper-adaptive-metal-three-blade",
                withExtension: "png"),
               let uiImage = UIImage(contentsOfFile: url.path) {
                Image(uiImage: uiImage)
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()
            } else {
                Color.black.ignoresSafeArea()
            }
            if let prizeID = premiumHandoffPrizeID {
                GachaPremiumDisplayCaseHandoffBoundary(prizeID: prizeID)
            } else {
                Button("打开机巧工坊") { showingStore = true }
                    .foregroundColor(.black)
                    .padding(.horizontal, 22)
                    .frame(height: 52)
                    .background(Color.white, in: RoundedRectangle(cornerRadius: 17))
            }
        }
    }

    private func configurePreview() {
        // Exercise the same shipping handoff closure used by the Unity
        // overlay, but stop at an explicit boundary. A standalone SwiftUI
        // host must never render GachaCaseRevealVisual as if it were the
        // real Unity PremiumDisplayCase.
        GachaShippingRevealContinuation.preparePremiumDisplayCase = {
            _, receipt in
#if DEBUG
            print("[GachaPreview] premium-handoff prize=\(receipt.prizeId)")
#endif
            premiumHandoffPrizeID = receipt.prizeId
        }
        GachaShippingRevealContinuation.cancelPreparedDisplayCase = {
            premiumHandoffPrizeID = nil
        }
        GachaStoreModel.shared.ingest(
            catalog: Self.catalog,
            snapshot: Self.snapshot,
            receipt: "")
        if ProcessInfo.processInfo.arguments.contains("--preview-reveal") {
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                GachaStoreModel.shared.ingest(
                    catalog: "",
                    snapshot: "",
                    receipt: Self.receipt)
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

/// Truthful endpoint for standalone evidence. The actual 3D case belongs to
/// the Unity main app and is separately covered by Build 42 main-app evidence.
private struct GachaPremiumDisplayCaseHandoffBoundary: View {
    let prizeID: String

    var body: some View {
        VStack(spacing: 18) {
            Image(systemName: "cube.transparent")
                .font(.product(size: 38, weight: .medium))
                .foregroundColor(.white.opacity(0.78))
            Text("UNITY 3D HANDOFF")
                .font(.product(size: 18, weight: .bold))
                .foregroundColor(.white)
            Text("当前 Simulator host 已完成真实交接\n3D 展示由 Unity PremiumDisplayCase 接续")
                .font(.product(size: 12, weight: .medium))
                .foregroundColor(.white.opacity(0.52))
                .multilineTextAlignment(.center)
            Text(prizeID)
                .font(.product(size: 10, weight: .medium))
                .foregroundColor(.white.opacity(0.30))
        }
        .padding(.horizontal, 30)
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("gacha-preview-real-3d-handoff-boundary")
    }
}
