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
    case settledHold
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

/// The real drawn prize's identity, captioned over the visible `.riv`
/// magnetic-holder artboard instead of replacing it. Built from the
/// transaction's real receipt row so the caption always names the actual
/// drawn prize instead of a fixed placeholder.
private struct GachaHolderIdentity {
    static let replacedRiveLogoAssetPrefix = "colographih-"
    static let paletteMarker = "neutralGraphiteSilver"
    static let surfaceMarker = "productOwnedIdentityCaption"
    static let accessibilityIdentifier = "gacha-holder-product-identity"

    let productName: String
    let tierAndLevelLabel: String
    let acquiredLabel: String
    let tint: SwiftUI.Color

    static let placeholder = GachaHolderIdentity(
        productName: "COLLECTOR EDITION",
        tierAndLevelLabel: "STANDARD",
        acquiredLabel: "揭晓中",
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
            tint: row.rarity.tint)
    }
}

private final class GachaHolderHiddenLayerAssetSentinel: NSObject {}

/// The `background/mint-slab` + `foreground/mint-slab` Rive layers now render
/// visibly and play their full authored motion; this asset only satisfies
/// Rive's internal embedded-image decode for the artboard's baked artwork —
/// it does not vary per prize (the real prize is named by the caption above).
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
    // The Pack's real on-screen frame at the moment of tear-commit, in this
    // view's own coordinate space (.zero if unknown). Lets the holder's
    // entrance animate from the exact spot the card/spinner just came out
    // of instead of a generic fixed offset.
    let entranceOriginFrame: CGRect
    let onFinished: (UUID, GachaRiveCompletionReason) -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    init(
        transactionID: UUID,
        stage: GachaRiveSequenceStage = .combined,
        playbackEnabled: Bool = true,
        revealedPrize: GachaReceiptRow? = nil,
        entranceOriginFrame: CGRect = .zero,
        onFinished: @escaping (UUID, GachaRiveCompletionReason) -> Void
    ) {
        self.entranceOriginFrame = entranceOriginFrame
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
                    entranceOriginFrame: entranceOriginFrame,
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
private struct GachaRiveCardFramePreferenceKey: PreferenceKey {
    static var defaultValue: CGRect = .zero
    static func reduce(value: inout CGRect, nextValue: () -> CGRect) {
        let next = nextValue()
        if next != .zero {
            value = next
        }
    }
}

// SwiftUI-declarative animation (ambient withAnimation{}, explicit
// .animation(value:), even a manually time-driven TimelineView) all failed
// to produce visible motion here: NSLog instrumentation proved the Rive
// engine's own rendering pins the main thread heavily enough during exactly
// the entrance window that SwiftUI's own re-render loop stalls for over a
// second (confirmed with video recording OFF too, ruling out capture
// overhead as the cause). Any animation technique that depends on SwiftUI
// re-invoking a view's body on the main thread will stall along with it.
// UIView.animate is different: Core Animation commits the start/end values
// once and interpolates on the render server, independent of whatever the
// main thread is doing afterward -- exactly what survives a busy main
// thread. This wrapper hosts the real content once, then drives its
// transform/alpha via a genuine UIKit animation the first time
// `isPresenting` flips true.
private struct GachaRiveEntranceAnimator<Content: View>: UIViewRepresentable {
    let isPresenting: Bool
    let startOffset: CGSize
    let duration: Double
    let content: () -> Content

    // Auto Layout constraints continuously re-solve on every layout pass,
    // which Rive's own frequent internal redraws can trigger many times a
    // second. Manually assigning .frame in layoutSubviews (only invoked when
    // the container's own bounds actually change) removes Auto Layout from
    // the picture entirely, in case the constraint solver was interacting
    // with the container's animated .transform in ways that fought the
    // in-flight animation.
    private final class ContainerView: UIView {
        var hostedView: UIView?
        override func layoutSubviews() {
            super.layoutSubviews()
            hostedView?.frame = bounds
        }
    }

    func makeUIView(context: Context) -> UIView {
        let container = ContainerView()
        container.clipsToBounds = false
        container.backgroundColor = .clear
        let hosting = UIHostingController(rootView: content())
        hosting.view.backgroundColor = .clear
        hosting.view.frame = container.bounds
        container.addSubview(hosting.view)
        container.hostedView = hosting.view
        context.coordinator.hostingController = hosting
        if !isPresenting {
            container.transform = CGAffineTransform(
                translationX: startOffset.width, y: startOffset.height)
            container.alpha = 0
        }
        return container
    }

    func updateUIView(_ uiView: UIView, context: Context) {
        context.coordinator.hostingController?.rootView = content()
        guard isPresenting, !context.coordinator.hasAnimated else { return }
        context.coordinator.hasAnimated = true
        gachaRiveRuntimeLog(
            "entrance-animator-starting startOffset=\(startOffset) duration=\(duration)")
        UIView.animate(
            withDuration: duration,
            delay: 0,
            options: [.curveEaseOut],
            animations: {
                uiView.transform = .identity
                uiView.alpha = 1
            },
            completion: { _ in
                gachaRiveRuntimeLog("entrance-animator-completed")
            })
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    final class Coordinator {
        var hostingController: UIHostingController<Content>?
        var hasAnimated = false
    }
}

private struct GachaRivePlaybackSurface: View {
    private static let artboardAspectRatio: CGFloat = 375.0 / 812.0

    let transactionID: UUID
    let stage: GachaRiveSequenceStage
    let playbackEnabled: Bool
    let revealedPrize: GachaReceiptRow?
    let entranceOriginFrame: CGRect
    let onFinished: (UUID, GachaRiveCompletionReason) -> Void

    @StateObject private var playback: GachaRivePlaybackCoordinator
    @StateObject private var background: GachaRiveLayerPlaybackModel
    @StateObject private var foreground: GachaRiveLayerPlaybackModel
    // The .riv artboard's own authored entrance slides in diagonally from a
    // fixed corner with no bindable property to redirect it (checked the
    // artboard's data-bind schema). Rather than fight that internal motion,
    // the whole assembly additionally rises from the Pack's real captured
    // tear-commit position (entranceOriginFrame) to its resting place, so
    // the dominant perceived motion is "this card just came out of that
    // Pack" instead of a generic fixed-offset slide.
    // Drives GachaRiveEntranceAnimator below -- a real UIView.animate call,
    // not a SwiftUI-observed value -- so flipping it true only needs to
    // happen once, ever.
    @State private var hasRisenIntoView = false
    private static let riseDuration: Double = 0.6

    // The card's *actual* rendered rect, captured via preference key rather
    // than read off the wrapping GeometryReader's own bounds. The reader
    // spans the full presentation (status-bar-to-home-indicator, ~402x812pt)
    // while the aspect-fit card only occupies a smaller region within it, so
    // using the reader's own frame as "resting position" produced a bogus
    // ~62pt offset instead of the real distance from the Pack's tear spot to
    // where the card visually sits -- confirmed via NSLog instrumentation
    // showing entrance-offset computing (0, -62) when the actual on-screen
    // gap was several hundred points, which is why three earlier attempts to
    // fix the *timing* of the rise never produced a visible motion: the
    // motion itself was too small to see, not merely mistimed.
    @State private var measuredRestingFrame: CGRect = .zero
    // Guards measuredRestingFrame so it is captured exactly once, before any
    // offset is ever applied to the measured view. The preference key is
    // attached to the SAME view the .offset(x:y:) modifier moves, so once an
    // offset is applied at all, every subsequent preference update reports
    // the *already-shifted* position -- a feedback loop confirmed via NSLog
    // instrumentation showing the resting frame's own Y drifting relative to
    // the very offset being computed from it, and the rise offset collapsing
    // back to the old bogus ~62pt value once the animation "settled" onto
    // its own moving target instead of the true rest position.
    @State private var hasCapturedRestingFrame = false

    init(
        transactionID: UUID,
        stage: GachaRiveSequenceStage,
        playbackEnabled: Bool,
        revealedPrize: GachaReceiptRow? = nil,
        entranceOriginFrame: CGRect = .zero,
        onFinished: @escaping (UUID, GachaRiveCompletionReason) -> Void
    ) {
        self.transactionID = transactionID
        self.stage = stage
        self.playbackEnabled = playbackEnabled
        self.revealedPrize = revealedPrize
        self.entranceOriginFrame = entranceOriginFrame
        self.onFinished = onFinished
        var requiredLayers: Set<GachaRiveLayer> = []
        if stage.includesBackground { requiredLayers.insert(.background) }
        if stage.includesForeground { requiredLayers.insert(.foreground) }
        let playback = GachaRivePlaybackCoordinator(
            requiredLayers: requiredLayers,
            // The magnetic-holder artboard's own authored timeline settles
            // its reveal (position/rotation/scale converge) by ~0.48s, then
            // spends the rest of its ~3.5s runtime on a decorative tail that
            // ends by fading the whole card to invisible. The state-machine
            // "in -> Idle" cycle this coordinator otherwise waits for only
            // completes at that full ~3.5s mark -- i.e. after the fade-out
            // already played. Freezing shortly after the measured settle
            // point instead holds the card at its fully-revealed frame.
            // Verified via direct parsing of the .riv file's keyframe data,
            // not guessed; see FidgetGachaRivePresentation git history for
            // the investigation this constant is based on.
            settleHoldSeconds: stage == .magneticHolder ? 0.55 : nil) {
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

    // Must match GachaPackOpeningOverlay.overlaySpaceName in
    // FidgetGachaStorefront.swift -- coordinate space names are plain
    // runtime string keys, not a shared compile-time symbol, since that
    // type is private to its own file.
    private static let entranceOriginSpaceName = "gachaPackOpeningOverlaySpace"

    private func entranceOffset(restingFrame: CGRect) -> CGSize {
        guard entranceOriginFrame != .zero else {
            // No captured Pack position (e.g. reduced-motion path never
            // populated it) -- fall back to the old generic rise-from-below.
            gachaRiveRuntimeLog(
                "entrance-offset-fallback restingFrame=\(restingFrame)")
            return CGSize(width: 0, height: 240)
        }
        // Anchor to the Pack's *bottom* edge -- the seam the tear opens
        // from -- rather than its center. Measured on a real device build,
        // the Pack's center and the holder's resting center land only ~45pt
        // apart (both sit roughly mid-screen in this layout), which reads as
        // no motion at all once blended with the fade. The user's ask was
        // specifically "the card emerges upward from the exact spot the tear
        // just opened" -- guarantee that reads as real, visible upward
        // travel by enforcing a minimum rise distance on top of the real
        // captured anchor, instead of only ever trusting whatever the raw
        // geometric gap happens to be.
        let minimumRiseDistance: CGFloat = 240
        let startY = max(
            entranceOriginFrame.maxY,
            restingFrame.midY + minimumRiseDistance)
        let offset = CGSize(
            width: entranceOriginFrame.midX - restingFrame.midX,
            height: startY - restingFrame.midY)
        gachaRiveRuntimeLog(
            "entrance-offset origin=\(entranceOriginFrame) resting=\(restingFrame) offset=\(offset)")
        return offset
    }

    @ViewBuilder
    private func cardContent() -> some View {
        ZStack {
            if stage.includesBackground {
                background
                    .view()
                    .allowsHitTesting(false)
            }
            if stage.includesForeground {
                foreground
                    .view()
                    .allowsHitTesting(false)
            }
            if stage == .magneticHolder {
                GachaProductOwnedIdentityCaption(
                    playbackEnabled: playbackEnabled,
                    identity: GachaHolderIdentity.resolve(from: revealedPrize))
                    .zIndex(10)
            }
        }
    }

    var body: some View {
        let riseOffset = entranceOffset(restingFrame: measuredRestingFrame)
        Group {
            // Only the magnetic-holder stage needs the entrance rise; every
            // other stage renders exactly as it did before this wrapper
            // existed, so this change can't regress the pack-selection halo
            // or any other caller of this surface.
            if stage == .magneticHolder {
                GachaRiveEntranceAnimator(
                    isPresenting: hasRisenIntoView,
                    startOffset: riseOffset,
                    duration: Self.riseDuration,
                    content: cardContent)
            } else {
                cardContent()
            }
        }
            .aspectRatio(Self.artboardAspectRatio, contentMode: .fit)
            // Captured on the aspect-fit-sized content itself, before the
            // .frame(maxWidth:.infinity...) below re-expands the layout
            // box back out to fill the presentation. Measuring after
            // that expansion would just reproduce the old
            // full-screen-bounds bug. This GeometryReader stays in the
            // plain SwiftUI tree (outside the UIHostingController the
            // animator wraps its content in above), so the named
            // coordinate-space lookup below keeps resolving against the
            // Pack's own capture in FidgetGachaStorefront.swift -- a
            // UIHostingController boundary would otherwise break that
            // lookup, since named spaces don't cross it.
            .background(
                GeometryReader { proxy in
                    Color.clear.preference(
                        key: GachaRiveCardFramePreferenceKey.self,
                        value: proxy.frame(in: .named(
                            Self.entranceOriginSpaceName)))
                }
            )
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .onPreferenceChange(GachaRiveCardFramePreferenceKey.self) { frame in
                guard !hasCapturedRestingFrame, frame != .zero else { return }
                measuredRestingFrame = frame
                hasCapturedRestingFrame = true
            }
            .onAppear {
                playback.attach(
                    background: background,
                    foreground: foreground)
                playback.setPresentationEnabled(playbackEnabled)
                let active = UIApplication.shared.applicationState == .active
                gachaRiveRuntimeLog(
                    "surface-appeared stage=\(stage.rawValue) applicationActive=\(active)")
                playback.setApplicationActive(active)
                if stage == .magneticHolder, playback.hasStartedPurchase {
                    riseIntoView()
                }
            }
            .onChange(of: playbackEnabled) { enabled in
                playback.setPresentationEnabled(enabled)
                if stage == .magneticHolder, !enabled {
                    hasRisenIntoView = false
                }
            }
            .onChange(of: playback.hasStartedPurchase) { started in
                // The rise must start together with the real Rive
                // triggerPurchase() call, not with playbackEnabled/onAppear --
                // those fire well before the .riv file has finished binding
                // and rendering its first frame, so the old triggers made the
                // container finish rising while the Rive canvas was still
                // blank underneath it.
                if stage == .magneticHolder, started {
                    riseIntoView()
                }
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

    private func riseIntoView() {
        gachaRiveRuntimeLog(
            "rise-into-view-called hasRisenIntoView=\(hasRisenIntoView) hasStartedPurchase=\(playback.hasStartedPurchase)")
        guard !hasRisenIntoView else { return }
        hasRisenIntoView = true
    }
}

/// The real `.riv` magnetic-holder artboard is now the visible card — this
/// caption only adds the real drawn prize's name/tier/acquired label as a
/// bottom-pinned strip so it never covers the Rive artwork or its motion.
private struct GachaProductOwnedIdentityCaption: View {
    let playbackEnabled: Bool
    let identity: GachaHolderIdentity

    @State private var isPresented = false

    var body: some View {
        VStack {
            Spacer()
            captionStrip
                .opacity(isPresented ? 1 : 0)
                .offset(y: isPresented ? 0 : 14)
                .padding(.bottom, 116)
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
                "holder-identity-caption-prepared product=\(identity.productName) surface=\(GachaHolderIdentity.surfaceMarker) playbackEnabled=\(playbackEnabled)")
            guard playbackEnabled else { return }
            DispatchQueue.main.async {
                presentCaption()
            }
        }
        .onChange(of: playbackEnabled) { enabled in
            if enabled {
                presentCaption()
            } else {
                var transaction = Transaction()
                transaction.disablesAnimations = true
                withTransaction(transaction) {
                    isPresented = false
                }
            }
        }
    }

    private var captionStrip: some View {
        VStack(spacing: 3) {
            Text(identity.productName)
                .font(.product(size: 13, weight: .bold))
                .tracking(0.3)
                .foregroundColor(.white.opacity(0.96))
                .lineLimit(1)
                .minimumScaleFactor(0.72)
            Text(identity.tierAndLevelLabel)
                .font(.product(size: 10, weight: .semibold))
                .foregroundColor(identity.tint.opacity(0.92))
        }
        .padding(.horizontal, 18)
        .padding(.vertical, 10)
        .background(
            Capsule().fill(Color.black.opacity(0.42)))
        .overlay(
            Capsule().stroke(Color.white.opacity(0.16), lineWidth: 1))
    }

    private func presentCaption() {
        guard !isPresented else { return }
        withAnimation(.spring(
            // Retimed to land close to the .riv artboard's own measured
            // ~0.48s reveal-settle point (see settleHoldSeconds above), so
            // the SwiftUI rise and the Rive-internal convergence finish
            // together instead of the SwiftUI motion lagging noticeably
            // behind an already-settled Rive card.
            response: 0.5,
            dampingFraction: 0.82,
            blendDuration: 0.08)) {
            isPresented = true
        }
        gachaRiveRuntimeLog(
            "holder-identity-caption-visible surface=\(GachaHolderIdentity.surfaceMarker) product=\(identity.productName) tier=\(identity.tierAndLevelLabel)")
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
    private let settleHoldSeconds: Double?
    private var settleHoldTask: Task<Void, Never>?
    // Published (not just a plain flag) so GachaRivePlaybackSurface can key
    // its entrance rise off the *real* moment triggerPurchase() fires, rather
    // than off view-appear. Binding + first-frame readiness is asynchronous
    // (.riv file load, autoBind's dispatched callback) and was consistently
    // slower than the SwiftUI rise's own ~550ms timeline, so the container
    // was finishing its rise-and-fade while the Rive canvas was still blank
    // -- confirmed by two rounds of frame-by-frame capture that both showed
    // the card already fully settled the instant it became visible at all.
    @Published private(set) var hasStartedPurchase = false

    init(
        requiredLayers: Set<GachaRiveLayer>,
        settleHoldSeconds: Double? = nil,
        completion: @escaping (GachaRiveCompletionReason) -> Void
    ) {
        self.requiredLayers = requiredLayers
        self.settleHoldSeconds = settleHoldSeconds
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
        settleHoldTask?.cancel()
        settleHoldTask = nil
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
        hasStartedPurchase = true
        gachaRiveRuntimeLog(
            "purchase-trigger synchronizedLayers=\(requiredLayers.count)")
        if requiredLayers.contains(.background) { background?.triggerPurchase() }
        if requiredLayers.contains(.foreground) { foreground?.triggerPurchase() }
        if let settleHoldSeconds {
            settleHoldTask = Task { @MainActor [weak self] in
                do {
                    try await Task.sleep(
                        nanoseconds: UInt64(settleHoldSeconds * 1_000_000_000))
                } catch {
                    return
                }
                self?.finish(reason: .settledHold)
            }
        }
    }

    private func finish(reason: GachaRiveCompletionReason) {
        guard !isCancelled, !didFinish else { return }
        didFinish = true
        settleHoldTask?.cancel()
        settleHoldTask = nil
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
    var entranceOriginFrame: CGRect = .zero
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
