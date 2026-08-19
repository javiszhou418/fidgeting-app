import SwiftUI
import UIKit

#if canImport(RiveRuntime)
import RiveRuntime
#endif

enum GachaRiveCompletionReason: String {
    case animationSignal
    case watchdog
    case reducedMotion
    case runtimeUnavailable
}

enum GachaRiveSequenceStage: String {
    case combined
    case packSelection
    case magneticHolder

    fileprivate var includesBackground: Bool {
        true
    }

    fileprivate var includesForeground: Bool {
        true
    }

    fileprivate var animationType: String {
        switch self {
        case .packSelection: return "T2_COIN_FLIP_JUMBOTRON"
        case .combined, .magneticHolder: return "T2_SPORTS_CARD_JUMBOTRON"
        }
    }

    var accessibilityIdentifier: String {
        switch self {
        case .combined: return "gacha-rive-gate"
        case .packSelection: return "gacha-selection-rive"
        case .magneticHolder: return "gacha-holder-rive"
        }
    }
}

/// Product-owned replacement for the auction branding baked into the reviewed
/// holder motion asset. Built from the transaction's real receipt row so the
/// holder shows the actual drawn prize instead of a fixed placeholder; none
/// of the 8 launch prizes have real bitmap art yet, so the "artwork" is a
/// procedural rarity-tinted glyph keyed by prize kind (fast-follow: real
/// per-prize thumbnails via a Unity snapshot tool + their own visual
/// approval round).
private struct GachaHolderIdentity {
    static let replacedRiveLogoAssetPrefix = "colographih-"
    static let paletteMarker = "neutralGraphiteSilver"
    static let surfaceMarker = "productOwnedMagneticHolderSurface"
    static let accessibilityIdentifier = "gacha-holder-product-identity"
    static let hiddenRiveCompletionOpacity = 0.001
    static let entranceOffsetX: CGFloat = 96
    static let entranceTiltDegrees = -38.0

    let productName: String
    let tierAndLevelLabel: String
    let acquiredLabel: String
    let glyphSystemName: String
    let tint: SwiftUI.Color

    static let placeholder = GachaHolderIdentity(
        productName: "COLLECTOR EDITION",
        tierAndLevelLabel: "STANDARD",
        acquiredLabel: "揭晓中",
        glyphSystemName: "sparkles",
        tint: GachaRarityTier.standard.tint)

    /// `row` is nil only for the reduce-motion path, which never shows the
    /// holder surface at all — the placeholder is a safe fallback, not a
    /// user-visible guess.
    static func resolve(from row: GachaReceiptRow?) -> GachaHolderIdentity {
        guard let row else { return .placeholder }
        return GachaHolderIdentity(
            productName: row.name.uppercased(),
            tierAndLevelLabel: row.isNew
                ? "\(row.rarity.title) · NEW"
                : "\(row.rarity.title) · +\(row.shardsGained)",
            acquiredLabel: "GEM/MINT",
            glyphSystemName: glyphSystemName(forKindIndex: row.kindIndex),
            tint: row.rarity.tint)
    }

    private static func glyphSystemName(forKindIndex kindIndex: Int) -> String {
        switch kindIndex {
        case 1: return "seal" // Sticker
        case 2: return "square.stack.3d.up" // DisplayBase
        case 3: return "paintpalette" // EnvironmentTint
        case 4: return "hand.raised" // Toy
        default: return "sparkles" // ToySkin
        }
    }
}

private final class GachaHolderHiddenLayerAssetSentinel: NSObject {}

/// The `background/mint-slab` + `foreground/mint-slab` Rive layers render at
/// `hiddenRiveCompletionOpacity` and are never seen — every visible holder
/// pixel is `GachaProductOwnedMagneticHolderSurface` below. This constant
/// only satisfies Rive's internal embedded-image decode for that invisible
/// layer; it is never displayed and does not vary per prize.
private enum GachaHolderHiddenLayerAsset {
    static let assetName = "product-thumbnail-metal-three-blade"

    static let data: Data? = {
        let bundles = [
            Bundle.main,
            Bundle(for: GachaHolderHiddenLayerAssetSentinel.self)
        ]
        for bundle in bundles {
            guard let url = bundle.url(
                forResource: assetName,
                withExtension: "png") else { continue }
            if let data = try? Data(contentsOf: url), !data.isEmpty {
                return data
            }
        }
        return nil
    }()
}

/// Receipt-free presentation shown immediately after the user taps Single Draw.
/// This layer is intentionally unaware of prize id, kind, name and rarity.
struct GachaSingleDrawRiveGate: View {
    let transactionID: UUID
    let stage: GachaRiveSequenceStage
    let playbackEnabled: Bool
    // Only meaningful for `stage == .magneticHolder`: the real drawn prize,
    // shown directly in the holder instead of a fixed placeholder.
    let revealedPrize: GachaReceiptRow?
    let onFinished: (UUID, GachaRiveCompletionReason) -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    init(
        transactionID: UUID,
        stage: GachaRiveSequenceStage = .combined,
        playbackEnabled: Bool = true,
        revealedPrize: GachaReceiptRow? = nil,
        onFinished: @escaping (UUID, GachaRiveCompletionReason) -> Void
    ) {
        self.transactionID = transactionID
        self.stage = stage
        self.playbackEnabled = playbackEnabled
        self.revealedPrize = revealedPrize
        self.onFinished = onFinished
    }

    var body: some View {
        Group {
            if stage == .packSelection {
                selectionCue
            } else {
                fullScreenPresentation
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(stage == .packSelection
            ? "包装已选中"
            : "抽取动画正在播放")
        .accessibilityIdentifier(stage.accessibilityIdentifier)
    }

    private var fullScreenPresentation: some View {
        ZStack {
            Color.black.opacity(0.985).ignoresSafeArea()

            if reduceMotion {
                VStack(spacing: 18) {
                    Text("COLLECTION DROP")
                        .font(.product(size: 12, weight: .bold))
                        .foregroundColor(.white.opacity(0.48))
                    reducedMotionSurface
                    Text("正在开启收藏")
                        .font(.product(size: 13, weight: .semibold))
                        .foregroundColor(.white.opacity(0.58))
                }
                .padding(.vertical, 34)
            } else {
                GachaRivePlaybackSurface(
                    transactionID: transactionID,
                    stage: stage,
                    playbackEnabled: playbackEnabled,
                    revealedPrize: revealedPrize,
                    onFinished: onFinished)
                    .ignoresSafeArea()

                VStack {
                    Text("COLLECTION DROP")
                        .font(.product(size: 12, weight: .bold))
                        .foregroundColor(.white.opacity(0.48))
                    Spacer()
                    Text("正在开启收藏")
                        .font(.product(size: 13, weight: .semibold))
                        .foregroundColor(.white.opacity(0.58))
                }
                .padding(.vertical, 34)
                .allowsHitTesting(false)
            }
        }
    }

    private var selectionCue: some View {
        Group {
            if reduceMotion {
                Circle()
                    .stroke(Color.white.opacity(0.42), lineWidth: 2)
                    .overlay { Circle().fill(Color.white.opacity(0.08)).padding(10) }
                    .task(id: playbackEnabled) {
                        guard playbackEnabled else { return }
                        do {
                            try await Task.sleep(
                                nanoseconds: GachaSingleDrawGateState
                                    .reduceMotionDelayNanoseconds)
                        } catch { return }
                        guard !Task.isCancelled else { return }
                        onFinished(transactionID, .reducedMotion)
                    }
            } else {
                ZStack {
                    Circle()
                        .fill(
                            RadialGradient(
                                colors: [
                                    Color.white.opacity(0.15),
                                    Color.white.opacity(0.035),
                                    .clear
                                ],
                                center: .center,
                                startRadius: 56,
                                endRadius: 120))

                    // `rotate-line` is a brand-free authored child artboard in
                    // the canonical file. It remains visibly outside the Pack
                    // silhouette while the full holder layers run at nearly
                    // transparent opacity only to preserve their authored
                    // completion signal for the existing gate.
#if canImport(RiveRuntime)
                    GachaRiveSelectionHaloSurface()
                        .frame(width: 240, height: 240)
                        .clipShape(Circle())
                        .saturation(0)
                        .blendMode(.plusLighter)
                        .accessibilityIdentifier(
                            "gacha-selection-rive-visible-halo")
#else
                    Circle()
                        .stroke(Color.white.opacity(0.28), lineWidth: 2)
                        .frame(width: 220, height: 220)
                        .accessibilityIdentifier(
                            "gacha-selection-rive-visible-halo-fallback")
#endif

                    Circle()
                        .stroke(
                            AngularGradient(
                                colors: [
                                    .clear,
                                    Color.white.opacity(0.50),
                                    Color(white: 0.66).opacity(0.52),
                                    Color.white.opacity(0.18),
                                    .clear
                                ],
                                center: .center),
                            lineWidth: 2.5)
                        .padding(8)
                        .shadow(color: .white.opacity(0.22), radius: 8)

                    GachaRivePlaybackSurface(
                        transactionID: transactionID,
                        stage: stage,
                        playbackEnabled: playbackEnabled,
                        onFinished: onFinished)
                        .frame(width: 64, height: 64)
                        .opacity(0.001)
                        .accessibilityHidden(true)
                }
            }
        }
        .frame(width: 240, height: 240)
        .clipShape(Circle())
        .allowsHitTesting(false)
    }

    private var reducedMotionSurface: some View {
        ProgressView()
            .tint(.white)
            .frame(width: 290, height: 390)
            .task(id: playbackEnabled) {
                guard playbackEnabled else { return }
                do {
                    try await Task.sleep(
                        nanoseconds: GachaSingleDrawGateState
                            .reduceMotionDelayNanoseconds)
                } catch {
                    return
                }
                guard !Task.isCancelled else { return }
                onFinished(transactionID, .reducedMotion)
            }
            .accessibilityLabel("已启用减少动态效果，正在确认抽取结果")
    }
}

/// Timeout does not end the authoritative draw. Without an end-to-end request
/// id, the safest state is to keep this transaction pending and accept only its
/// eventual receipt instead of allowing another draw or reclassifying it as a
/// multi-draw response.
struct GachaSingleDrawReceiptRecoveryView: View {
    let retry: () -> Void

    var body: some View {
        ZStack {
            Color.black.opacity(0.985).ignoresSafeArea()
            VStack(spacing: 18) {
                Image(systemName: "clock.badge.exclamationmark")
                    .font(.product(size: 28, weight: .semibold))
                    .foregroundColor(.white.opacity(0.74))
                Text("仍在等待权威结果")
                    .font(.product(size: 18, weight: .bold))
                    .foregroundColor(.white)
                Text("本次抽取不会重试，也不会生成替代奖品。\n结果恢复前暂时不能再次抽取。")
                    .font(.product(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.52))
                    .multilineTextAlignment(.center)
                Button("刷新结果") { retry() }
                    .font(.product(size: 14, weight: .bold))
                    .foregroundColor(.black)
                    .frame(width: 180, height: 50)
                    .background(Color.white, in: RoundedRectangle(cornerRadius: 16))
            }
            .padding(.horizontal, 30)
        }
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("gacha-receipt-recovery")
    }
}

#if canImport(RiveRuntime)
private struct GachaRivePlaybackSurface: View {
    private static let artboardAspectRatio: CGFloat = 375.0 / 812.0

    let transactionID: UUID
    let stage: GachaRiveSequenceStage
    let playbackEnabled: Bool
    let revealedPrize: GachaReceiptRow?
    let onFinished: (UUID, GachaRiveCompletionReason) -> Void

    @StateObject private var playback: GachaRivePlaybackCoordinator
    @StateObject private var background: GachaRiveLayerPlaybackModel
    @StateObject private var foreground: GachaRiveLayerPlaybackModel

    init(
        transactionID: UUID,
        stage: GachaRiveSequenceStage,
        playbackEnabled: Bool,
        revealedPrize: GachaReceiptRow? = nil,
        onFinished: @escaping (UUID, GachaRiveCompletionReason) -> Void
    ) {
        self.transactionID = transactionID
        self.stage = stage
        self.playbackEnabled = playbackEnabled
        self.revealedPrize = revealedPrize
        self.onFinished = onFinished
        var requiredLayers: Set<GachaRiveLayer> = []
        if stage.includesBackground { requiredLayers.insert(.background) }
        if stage.includesForeground { requiredLayers.insert(.foreground) }
        let playback = GachaRivePlaybackCoordinator(
            requiredLayers: requiredLayers) {
            reason in
            onFinished(transactionID, reason)
        }
        _playback = StateObject(wrappedValue: playback)
        _background = StateObject(wrappedValue: GachaRiveLayerPlaybackModel(
            layer: .background,
            animationType: stage.animationType,
            coordinator: playback))
        _foreground = StateObject(wrappedValue: GachaRiveLayerPlaybackModel(
            layer: .foreground,
            animationType: stage.animationType,
            coordinator: playback))
    }

    var body: some View {
        ZStack {
            if stage.includesBackground {
                background
                    .view()
                    .opacity(stage == .magneticHolder
                        ? GachaHolderIdentity.hiddenRiveCompletionOpacity
                        : 1)
                    .allowsHitTesting(false)
            }
            if stage.includesForeground {
                foreground
                    .view()
                    .opacity(stage == .magneticHolder
                        ? GachaHolderIdentity.hiddenRiveCompletionOpacity
                        : 1)
                    .allowsHitTesting(false)
            }
            if stage == .magneticHolder {
                GachaProductOwnedMagneticHolderSurface(
                    playbackEnabled: playbackEnabled,
                    identity: GachaHolderIdentity.resolve(from: revealedPrize))
                    .zIndex(10)
            }
        }
            .aspectRatio(Self.artboardAspectRatio, contentMode: .fit)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .onAppear {
                playback.attach(
                    background: background,
                    foreground: foreground)
                playback.setPresentationEnabled(playbackEnabled)
                let active = UIApplication.shared.applicationState == .active
                gachaRiveRuntimeLog(
                    "surface-appeared stage=\(stage.rawValue) applicationActive=\(active)")
                playback.setApplicationActive(active)
            }
            .onChange(of: playbackEnabled) { enabled in
                playback.setPresentationEnabled(enabled)
            }
            .onReceive(NotificationCenter.default.publisher(
                for: UIApplication.didBecomeActiveNotification)) { _ in
                playback.setApplicationActive(true)
            }
            .onReceive(NotificationCenter.default.publisher(
                for: UIApplication.willResignActiveNotification)) { _ in
                playback.setApplicationActive(false)
            }
            .onDisappear {
                playback.cancel()
            }
            .task(id: playbackEnabled) {
                guard playbackEnabled else { return }
                do {
                    try await Task.sleep(
                        nanoseconds: GachaSingleDrawGateState
                            .riveWatchdogNanoseconds)
                } catch {
                    return
                }
                guard !Task.isCancelled else { return }
                playback.finishFromWatchdog()
            }
    }
}

/// The Rive holder remains a hidden completion clock. Every visible holder
/// pixel is product-owned SwiftUI, so embedded third-party art can never flash
/// during the entrance, tilt, settle or exit choreography.
private struct GachaProductOwnedMagneticHolderSurface: View {
    let playbackEnabled: Bool
    let identity: GachaHolderIdentity

    @State private var isPresented = false

    var body: some View {
        ZStack {
            holderSlab
                .scaleEffect(isPresented ? 1 : 0.84)
                .rotationEffect(.degrees(isPresented ? -1.2 : 4.5))
                .rotation3DEffect(
                    .degrees(isPresented
                        ? -3
                        : GachaHolderIdentity.entranceTiltDegrees),
                    axis: (x: 0.08, y: 1, z: 0),
                    anchor: .center,
                    perspective: 0.72)
                .offset(
                    x: isPresented
                        ? 0
                        : GachaHolderIdentity.entranceOffsetX,
                    y: isPresented ? -160 : -146)
                .opacity(playbackEnabled ? 1 : 0)
                .animation(nil, value: playbackEnabled)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .allowsHitTesting(false)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(
            "\(identity.productName)，\(identity.tierAndLevelLabel)")
        .accessibilityIdentifier(
            GachaHolderIdentity.accessibilityIdentifier)
        .accessibilityHidden(!playbackEnabled)
        .onAppear {
            gachaRiveRuntimeLog(
                "holder-product-surface-prepared product=\(identity.productName) surface=\(GachaHolderIdentity.surfaceMarker) playbackEnabled=\(playbackEnabled)")
            guard playbackEnabled else { return }
            DispatchQueue.main.async {
                presentHolder()
            }
        }
        .onChange(of: playbackEnabled) { enabled in
            if enabled {
                presentHolder()
            } else {
                var transaction = Transaction()
                transaction.disablesAnimations = true
                withTransaction(transaction) {
                    isPresented = false
                }
            }
        }
    }

    private var holderSlab: some View {
        VStack(spacing: 12) {
            identityHeader
            productWindow

            HStack(spacing: 7) {
                Capsule()
                    .fill(Color.white.opacity(0.24))
                    .frame(height: 1)
                Text("MAGNETIC HOLDER")
                    .font(.product(size: 7, weight: .bold))
                    .tracking(1.1)
                    .foregroundColor(.white.opacity(0.52))
                    .fixedSize()
                Capsule()
                    .fill(Color.white.opacity(0.24))
                    .frame(height: 1)
            }
        }
        .padding(.horizontal, 15)
        .padding(.vertical, 14)
        .frame(width: 218, height: 318)
        .background(
            LinearGradient(
                colors: [
                    Color(white: 0.29).opacity(0.93),
                    Color(white: 0.10).opacity(0.96),
                    Color(white: 0.20).opacity(0.94)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing),
            in: RoundedRectangle(cornerRadius: 31, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 31, style: .continuous)
                .stroke(
                    LinearGradient(
                        colors: [
                            Color.white.opacity(0.82),
                            Color.white.opacity(0.18),
                            Color.white.opacity(0.54)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing),
                    lineWidth: 2.2)
        }
        .overlay {
            RoundedRectangle(cornerRadius: 25, style: .continuous)
                .stroke(Color.white.opacity(0.16), lineWidth: 0.8)
                .padding(7)
        }
        .shadow(color: .black.opacity(0.58), radius: 24, x: 12, y: 18)
        .shadow(color: .white.opacity(0.10), radius: 7, x: -3, y: -5)
    }

    private var identityHeader: some View {
        HStack(alignment: .top, spacing: 8) {
            VStack(alignment: .leading, spacing: 4) {
                Text(identity.productName)
                    .font(.product(size: 10, weight: .bold))
                    .tracking(0.25)
                    .foregroundColor(.white.opacity(0.94))
                    .lineLimit(1)
                    .minimumScaleFactor(0.72)

                Text(identity.tierAndLevelLabel)
                    .font(.product(size: 8, weight: .semibold))
                    .foregroundColor(.white.opacity(0.58))
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            VStack(alignment: .trailing, spacing: 0) {
                Text(identity.acquiredLabel)
                    .font(.product(size: 7, weight: .bold))
                    .foregroundColor(.white.opacity(0.72))
            }
        }
        .padding(.horizontal, 2)
        .frame(height: 48)
    }

    private var productWindow: some View {
        ZStack {
            Circle()
                .fill(
                    RadialGradient(
                        colors: [
                            identity.tint.opacity(0.55),
                            Color.black.opacity(0.78)
                        ],
                        center: .center,
                        startRadius: 4,
                        endRadius: 90))

            Image(systemName: identity.glyphSystemName)
                .font(.system(size: 56, weight: .semibold))
                .foregroundColor(.white.opacity(0.92))
        }
        .frame(width: 164, height: 164)
        .overlay {
            Circle()
                .stroke(
                    AngularGradient(
                        colors: [
                            Color.white.opacity(0.84),
                            identity.tint.opacity(0.55),
                            Color.white.opacity(0.22),
                            identity.tint.opacity(0.70),
                            Color.white.opacity(0.84)
                        ],
                        center: .center),
                    lineWidth: 4)
        }
        .overlay {
            Circle()
                .stroke(Color.black.opacity(0.54), lineWidth: 1)
                .padding(7)
        }
        .shadow(color: .black.opacity(0.62), radius: 14, x: 7, y: 10)
        .accessibilityHidden(true)
    }

    private func presentHolder() {
        guard !isPresented else { return }
        withAnimation(.spring(
            response: 0.58,
            dampingFraction: 0.82,
            blendDuration: 0.08)) {
            isPresented = true
        }
        gachaRiveRuntimeLog(
            "holder-product-surface-visible surface=\(GachaHolderIdentity.surfaceMarker) product=\(identity.productName) tier=\(identity.tierAndLevelLabel)")
    }
}

/// A presentation-only child artboard from the same reviewed `.riv`. Unlike
/// the full split composition, `rotate-line` contains no holder, third-party mark,
/// grade copy, receipt data or rarity input, so it is safe before the tear.
@MainActor
private struct GachaRiveSelectionHaloSurface: View {
    @StateObject private var halo = GachaRiveSelectionHaloPlaybackModel()

    var body: some View {
        halo.view()
            .aspectRatio(1, contentMode: .fit)
            .allowsHitTesting(false)
            .onDisappear {
                halo.pause()
            }
    }
}

private enum GachaRiveLayer: String, CaseIterable {
    case background = "background/mint-slab"
    case foreground = "foreground/mint-slab"
}

private func gachaRiveRuntimeLog(_ message: String) {
#if DEBUG
    // `print` from Swift compiled into UnityFramework does not reliably enter
    // Simulator unified logs. NSLog keeps shipping-source smoke evidence tied
    // to the actual main-app process.
    NSLog("%@", "[GachaRiveRuntime] \(message)")
#endif
}

/// This file contains four embedded image payloads and one intentionally empty
/// avatar slot. With CDN loading disabled, Rive requires the app-provided
/// loader to decode and attach those embedded bytes explicitly.
private func loadGachaRiveEmbeddedAsset(
    asset: RiveFileAsset,
    data: Data,
    factory: RiveFactory
) -> Bool {
    let filename = asset.uniqueFilename()
    guard !data.isEmpty else {
        gachaRiveRuntimeLog("embedded-asset-empty name=\(filename)")
        return false
    }
    guard let imageAsset = asset as? RiveImageAsset else {
        gachaRiveRuntimeLog(
            "embedded-asset-unsupported name=\(filename) bytes=\(data.count)")
        return false
    }

    let renderedData: Data
    if filename.hasPrefix(GachaHolderIdentity.replacedRiveLogoAssetPrefix) {
        guard let replacement = GachaHolderHiddenLayerAsset.data else {
            gachaRiveRuntimeLog(
                "holder-hidden-layer-asset-missing asset=\(GachaHolderHiddenLayerAsset.assetName)")
            return false
        }
        renderedData = replacement
        gachaRiveRuntimeLog(
            "holder-hidden-layer-asset-loaded asset=\(GachaHolderHiddenLayerAsset.assetName) bytes=\(replacement.count)")
    } else {
        renderedData = data
    }

    imageAsset.renderImage(factory.decodeImage(renderedData))
    gachaRiveRuntimeLog(
        "embedded-image-loaded name=\(filename) bytes=\(renderedData.count)")
    return true
}

@MainActor
private final class GachaRivePlaybackCoordinator: ObservableObject {
    private let requiredLayers: Set<GachaRiveLayer>
    private weak var background: GachaRiveLayerPlaybackModel?
    private weak var foreground: GachaRiveLayerPlaybackModel?
    private var readyLayers: Set<GachaRiveLayer> = []
    private var renderedLayers: Set<GachaRiveLayer> = []
    private var endedLayers: Set<GachaRiveLayer> = []
    private var completion: ((GachaRiveCompletionReason) -> Void)?
    private var isApplicationActive = false
    private var isPresentationEnabled = false
    private var didStart = false
    private var didFinish = false
    private var isCancelled = false

    init(
        requiredLayers: Set<GachaRiveLayer>,
        completion: @escaping (GachaRiveCompletionReason) -> Void
    ) {
        self.requiredLayers = requiredLayers
        self.completion = completion
    }

    func attach(
        background: GachaRiveLayerPlaybackModel,
        foreground: GachaRiveLayerPlaybackModel
    ) {
        self.background = background
        self.foreground = foreground
        startIfReady()
    }

    func layerDidRenderFirstFrame(_ layer: GachaRiveLayer) {
        guard !isCancelled, !didFinish else { return }
        renderedLayers.insert(layer)
        gachaRiveRuntimeLog("first-frame-ready artboard=\(layer.rawValue)")
        startIfReady()
    }

    func layerDidBind(_ layer: GachaRiveLayer) {
        guard !isCancelled, !didFinish else { return }
        readyLayers.insert(layer)
        gachaRiveRuntimeLog(
            "bound artboard=\(layer.rawValue) stateMachine=Main")
        startIfReady()
    }

    func layerDidEnd(_ layer: GachaRiveLayer, source: String) {
        guard !isCancelled, !didFinish, didStart else { return }
        endedLayers.insert(layer)
        gachaRiveRuntimeLog(
            "layer-completed artboard=\(layer.rawValue) source=\(source)")
        guard requiredLayers.isSubset(of: endedLayers) else {
            return
        }
        finish(reason: .animationSignal)
    }

    func setPresentationEnabled(_ enabled: Bool) {
        guard !isCancelled, !didFinish else { return }
        guard isPresentationEnabled != enabled || !didStart else { return }
        isPresentationEnabled = enabled
        gachaRiveRuntimeLog("presentation-enabled=\(enabled)")
        if enabled {
            startIfReady()
        }
    }

    func setApplicationActive(_ active: Bool) {
        guard !isCancelled, !didFinish else { return }
        guard isApplicationActive != active || !didStart else { return }
        isApplicationActive = active
        gachaRiveRuntimeLog("application-active=\(active)")
        if active {
            if requiredLayers.contains(.background) { background?.play() }
            if requiredLayers.contains(.foreground) { foreground?.play() }
            startIfReady()
        } else {
            background?.pause()
            foreground?.pause()
        }
    }

    func finishFromWatchdog() {
        gachaRiveRuntimeLog(
            "watchdog ready=\(readyLayers.count)/\(requiredLayers.count) firstFrames=\(renderedLayers.count)/\(requiredLayers.count) ended=\(endedLayers.count)/\(requiredLayers.count) applicationActive=\(isApplicationActive)")
        finish(reason: .watchdog)
    }

    func cancel() {
        guard !isCancelled else { return }
        isCancelled = true
        background?.cancel()
        foreground?.cancel()
        completion = nil
    }

    private func startIfReady() {
        guard !isCancelled,
              !didFinish,
              !didStart,
              isPresentationEnabled,
              isApplicationActive,
              requiredLayers.isSubset(of: readyLayers),
              requiredLayers.isSubset(of: renderedLayers) else { return }
        didStart = true
        gachaRiveRuntimeLog(
            "purchase-trigger synchronizedLayers=\(requiredLayers.count)")
        if requiredLayers.contains(.background) { background?.triggerPurchase() }
        if requiredLayers.contains(.foreground) { foreground?.triggerPurchase() }
    }

    private func finish(reason: GachaRiveCompletionReason) {
        guard !isCancelled, !didFinish else { return }
        didFinish = true
        gachaRiveRuntimeLog("completed reason=\(reason.rawValue)")
        background?.pause()
        foreground?.pause()
        let callback = completion
        completion = nil
        callback?(reason)
    }
}

@MainActor
private final class GachaRiveLayerPlaybackModel: RiveViewModel {
    static let assetName = GachaRiveAssetLocator.assetName

    private let layer: GachaRiveLayer
    private let animationType: String
    private weak var coordinator: GachaRivePlaybackCoordinator?
    private var instance: RiveDataBindingViewModel.Instance?
    private var animationEndedProperty:
        RiveDataBindingViewModel.Instance.TriggerProperty?
    private var animationEndedListener: UUID?
    private var internalPlaybackTrigger:
        RiveDataBindingViewModel.Instance.TriggerProperty?
    private var backgroundBindableArtboard: RiveBindableArtboard?
    private var foregroundBindableArtboard: RiveBindableArtboard?
    private var isCancelled = false
    private var didLogFirstFrame = false
    private var sawActiveState = false

    init(
        layer: GachaRiveLayer,
        animationType: String,
        coordinator: GachaRivePlaybackCoordinator
    ) {
        self.layer = layer
        self.animationType = animationType
        self.coordinator = coordinator
        let assetBundle = GachaRiveAssetLocator.resolveBundle()
        super.init(
            fileName: Self.assetName,
            in: assetBundle,
            stateMachineName: "Main",
            fit: .contain,
            alignment: .center,
            autoPlay: true,
            artboardName: layer.rawValue,
            loadCdn: false,
            customLoader: loadGachaRiveEmbeddedAsset)

        riveModel?.enableAutoBind { [weak self] instance in
            DispatchQueue.main.async { [weak self] in
                self?.bind(instance: instance)
            }
        }
    }

    private func bind(instance: RiveDataBindingViewModel.Instance) {
        guard !isCancelled else { return }
        detachAnimationEndedListener()
        self.instance = instance

        let ended = instance.triggerProperty(fromPath: "animationEnded")
        animationEndedProperty = ended
        animationEndedListener = ended?.addListener { [weak self] in
            DispatchQueue.main.async { [weak self] in
                guard let self else { return }
                self.coordinator?.layerDidEnd(
                    self.layer,
                    source: "animationEnded")
            }
        }

        // Replace the auction-specific copy before the first rendered frame.
        // None of these values contain receipt, prize or rarity information.
        instance.stringProperty(fromPath: "titleName")?.value = "FIDGET ARCHIVE"
        instance.stringProperty(fromPath: "subtitle")?.value = "COLLECTION UNLOCKING"
        instance.stringProperty(fromPath: "promoteTag")?.value = "FIDGETING APP"
        instance.booleanProperty(fromPath: "isSelfBuyer")?.value = false
        instance.booleanProperty(fromPath: "isPromoted")?.value = false
        instance.booleanProperty(fromPath: "isReferral")?.value = false
        instance.booleanProperty(fromPath: "isNewBuyer")?.value = false
        instance.booleanProperty(fromPath: "isLooping")?.value = false
        if let animationType = instance.enumProperty(fromPath: "animationType"),
           animationType.values.contains(self.animationType) {
            animationType.value = self.animationType
            gachaRiveRuntimeLog(
                "animationType artboard=\(layer.rawValue) value=\(animationType.value)")
        } else {
            gachaRiveRuntimeLog(
                "missing-animationType value=\(self.animationType)")
        }

        do {
            guard let riveFile = riveModel?.riveFile else {
                throw GachaRiveBindingError.missingFile
            }
            let backgroundArtboard = try riveFile.bindableArtboard(
                withName: "Slab-rotate-v01")
            let foregroundArtboard = try riveFile.bindableArtboard(
                withName: "Coin_Slab_v09-sm")
            backgroundBindableArtboard = backgroundArtboard
            foregroundBindableArtboard = foregroundArtboard
            let backgroundProperty = instance.artboardProperty(
                fromPath: "backgroundArtboard")
            backgroundProperty?.setValue(backgroundArtboard)
            let foregroundProperty = instance.artboardProperty(
                fromPath: "foregroundArtboard")
            foregroundProperty?.setValue(foregroundArtboard)
            gachaRiveRuntimeLog(
                "bindable-artboards artboard=\(layer.rawValue) background=\(backgroundArtboard.name) foreground=\(foregroundArtboard.name)")
        } catch {
            gachaRiveRuntimeLog(
                "bindable-artboards-failed artboard=\(layer.rawValue) error=\(error)")
        }

        let internalTriggerPath = layer == .background
            ? "internalViewModel/playBackground"
            : "internalViewModel/playForeground"
        internalPlaybackTrigger = instance.triggerProperty(
            fromPath: internalTriggerPath)
        let playState = instance.enumProperty(
            fromPath: "internalViewModel/playState")?.value ?? "missing"
        gachaRiveRuntimeLog(
            "internal-path artboard=\(layer.rawValue) trigger=\(internalTriggerPath) found=\(internalPlaybackTrigger != nil) playState=\(playState)")

        coordinator?.layerDidBind(layer)
    }

    func triggerPurchase() {
        guard !isCancelled, let internalPlaybackTrigger else {
            gachaRiveRuntimeLog(
                "missing-internal-playback artboard=\(layer.rawValue)")
            return
        }
        internalPlaybackTrigger.trigger()
        // Data-binding triggers do not restart an idle Rive player. Mirror
        // RiveViewModel.triggerInput(_:)'s behavior so the queued trigger is
        // consumed immediately instead of waiting for a later lifecycle call.
        play()
    }

    override func player(
        didAdvanceby seconds: Double,
        riveModel: RiveModel?
    ) {
        guard seconds > 0 else { return }
        Task { @MainActor [weak self] in
            self?.logFirstFrame()
        }
    }

    private func logFirstFrame() {
        guard !didLogFirstFrame else { return }
        didLogFirstFrame = true
        gachaRiveRuntimeLog("first-frame artboard=\(layer.rawValue)")
        coordinator?.layerDidRenderFirstFrame(layer)
    }

    @objc func stateMachine(
        _ stateMachine: RiveStateMachineInstance,
        didChangeState stateName: String
    ) {
        gachaRiveRuntimeLog(
            "state artboard=\(layer.rawValue) name=\(stateName)")
        if stateName.caseInsensitiveCompare("in") == .orderedSame {
            sawActiveState = true
        } else if sawActiveState,
                  stateName.caseInsensitiveCompare("Idle") == .orderedSame {
            sawActiveState = false
            coordinator?.layerDidEnd(
                layer,
                source: "stateMachineCycle")
        }
    }

    func cancel() {
        guard !isCancelled else { return }
        isCancelled = true
        detachAnimationEndedListener()
        riveModel?.disableAutoBind()
        pause()
        instance = nil
        internalPlaybackTrigger = nil
        backgroundBindableArtboard = nil
        foregroundBindableArtboard = nil
        coordinator = nil
    }

    private func detachAnimationEndedListener() {
        if let animationEndedProperty, let animationEndedListener {
            animationEndedProperty.removeListener(animationEndedListener)
        }
        animationEndedListener = nil
        animationEndedProperty = nil
    }

    private enum GachaRiveBindingError: Error {
        case missingFile
    }
}

@MainActor
private final class GachaRiveSelectionHaloPlaybackModel: RiveViewModel {
    private var didLogFirstFrame = false

    init() {
        let assetBundle = GachaRiveAssetLocator.resolveBundle()
        super.init(
            fileName: GachaRiveAssetLocator.assetName,
            in: assetBundle,
            stateMachineName: "State Machine 1",
            fit: .contain,
            alignment: .center,
            autoPlay: true,
            artboardName: "rotate-line",
            loadCdn: false,
            customLoader: loadGachaRiveEmbeddedAsset)
        gachaRiveRuntimeLog(
            "selection-halo-bound artboard=rotate-line stateMachine=State Machine 1")
    }

    override func player(
        didAdvanceby seconds: Double,
        riveModel: RiveModel?
    ) {
        guard seconds > 0 else { return }
        Task { @MainActor [weak self] in
            self?.logFirstFrame()
        }
    }

    private func logFirstFrame() {
        guard !didLogFirstFrame else { return }
        didLogFirstFrame = true
        gachaRiveRuntimeLog(
            "selection-halo-first-frame artboard=rotate-line")
    }
}

private final class GachaRiveBundleSentinel: NSObject {}

private enum GachaRiveAssetLocator {
    static let assetName = "gacha-single-draw-jumbotron"

    static func resolveBundle() -> Bundle {
        let candidates = [
            Bundle.main,
            Bundle(for: GachaRiveBundleSentinel.self)
        ]
        for bundle in candidates {
            if let url = bundle.url(
                forResource: assetName,
                withExtension: "riv") {
                gachaRiveRuntimeLog(
                    "asset-resolved bundle=\(bundle.bundleURL.lastPathComponent) path=\(url.lastPathComponent)")
                return bundle
            }
        }
        gachaRiveRuntimeLog(
            "asset-missing main=\(Bundle.main.bundleURL.lastPathComponent) framework=\(Bundle(for: GachaRiveBundleSentinel.self).bundleURL.lastPathComponent)")
        // RiveViewModel's local-file initializer is fail-fast. Returning the
        // main bundle preserves that behavior while leaving a durable log that
        // distinguishes bundle lookup from animation/lifecycle failures.
        return .main
    }
}
#else
/// Standalone source previews do not resolve app Swift packages. Shipping
/// Xcode projects always take the RiveRuntime branch configured by the build
/// pipeline; this neutral branch keeps local layout harnesses compilable.
private struct GachaRivePlaybackSurface: View {
    let transactionID: UUID
    let stage: GachaRiveSequenceStage
    let playbackEnabled: Bool
    var revealedPrize: GachaReceiptRow?
    let onFinished: (UUID, GachaRiveCompletionReason) -> Void

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 32, style: .continuous)
                .fill(Color.white.opacity(0.055))
            ProgressView().tint(.white)
        }
        .frame(width: 330, height: 390)
        .task(id: playbackEnabled) {
            guard playbackEnabled else { return }
            do {
                try await Task.sleep(nanoseconds: 1_500_000_000)
            } catch {
                return
            }
            guard !Task.isCancelled else { return }
            onFinished(transactionID, .runtimeUnavailable)
        }
    }
}
#endif
