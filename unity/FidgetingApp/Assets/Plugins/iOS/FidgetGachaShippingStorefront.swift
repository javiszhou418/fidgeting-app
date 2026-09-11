import SwiftUI
import UIKit

public struct GachaStoreView: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @ObservedObject private var model = GachaStoreModel.shared

    @State private var selectedPack = GachaPackTier.standard
    @State private var gate = GachaSingleDrawGateState()
    @State private var tearProgress = 0.0
    @State private var packReleasePulseStrength = 0.0
    @State private var packRetreatProgress = 0.0
    @State private var packDeparted = false
    @State private var stageBackdropOpacity = 1.0
    @State private var showsCompletedOverlay = false
    @State private var frontRevealed = false
    @State private var mouthGapeScale = 1.0
    @State private var commitInstant: Date? = nil
    @State private var tearStartInstant: Date? = nil
    @State private var stageEntered = false
    /// User-facing draw failure (GachaPackPaymentRules.failureMessage); nil hides.
    @State private var drawFailureNotice: String? = nil
    /// One clock for the resting-Pack idle in the carousel and on the tear
    /// stage, so the float/yaw phase carries across selection.
    @State private var idleReference = Date()
    @Namespace private var packNamespace
    @State private var presentRequested = false
    @State private var automaticPreviewStarted = false
    @State private var acknowledgementState = ProductActionState.ready
    /// FDB-GAC-036: device motion for the Pack's holographic sheen. Started
    /// while a sealed Pack is on screen, stopped at case handoff.
    @StateObject private var motion = GachaPackMotionFeed()

    /// Device motion feeds the Pack foil, and from R053 the result sheet's
    /// foil too. The bridge shares one CMMotionManager with Unity's plate.
    private var packMotionPhase: Bool {
        switch gate.phase {
        case .choosingPack, .selectionRive, .tearPack,
             .waitingForReceipt, .preparingCase, .handoff, .complete:
            return true
        case .receiptRecovery:
            return false
        }
    }

    private var isGate12Preview: Bool {
        ProcessInfo.processInfo.arguments.contains(
            "--premium-display-case-gate12-preview")
    }

    /// Carousel-only rehearsal: step STANDARD → 1 OF 1, dwell on each, then
    /// back one step. Shows the tier ladder (wriggle bursts, arrival rise,
    /// snap weight) without drawing.
    private var isCarouselLadderPreview: Bool {
        ProcessInfo.processInfo.arguments.contains(
            "--gacha-carousel-ladder-preview")
    }

    private var isNativeHybridCandidate: Bool {
        GachaPackHandoffRules.isNativeHybridCandidatePreview
    }

    private var staticStage: GachaNativeHybridStaticStage? {
        GachaNativeHybridStaticStage.requested
    }

    private var activeSeries: GachaSeriesInfo? {
        model.series.first
    }

    private var usesPackHueBackdrop: Bool {
        switch gate.phase {
        case .choosingPack, .selectionRive, .tearPack,
             .waitingForReceipt, .preparingCase:
            return true
        case .handoff, .complete, .receiptRecovery:
            return false
        }
    }

    /// FDB-GAC-035 amended 2026-09-07: the arc bands are the backdrop from
    /// the carousel on, not only after selection.
    private var usesPackArcBackdrop: Bool {
        switch gate.phase {
        case .choosingPack, .selectionRive, .tearPack,
             .waitingForReceipt, .preparingCase:
            return true
        case .handoff, .complete, .receiptRecovery:
            return false
        }
    }

    private var packArcBackdropIntensity: Double {
        GachaPackArcBackdropRules.visibility(
            tearProgress: tearProgress,
            stageEligible: usesPackArcBackdrop)
    }

    /// R053: motes stay through tear, case rise and card back; they leave
    /// with the Unity stage light-up when the front face passes 90°.
    private var usesPackAmbience: Bool {
        switch gate.phase {
        case .choosingPack, .selectionRive, .tearPack,
             .waitingForReceipt, .preparingCase, .handoff, .complete:
            return true
        case .receiptRecovery:
            return false
        }
    }

    private var packAmbienceIntensity: Double {
        GachaPackArcBackdropRules.ambienceVisibility(
            stageEligible: usesPackAmbience,
            frontRevealed: frontRevealed)
    }

    private var liveCaseApertureAvailable: Bool {
        gate.allowsLiveCaseAperture
    }

    /// Wash and arcs change colour after the floor glow has begun to grow
    /// (GachaPackBackdropRippleRules), so a tier change reads bottom-up.
    private var backdropFollowAnimation: Animation {
        reduceMotion
            ? .easeOut(duration: 0.35)
            : .easeInOut(
                duration: GachaPackBackdropRippleRules.backdropFollowSeconds)
                .delay(GachaPackBackdropRippleRules.backdropFollowDelaySeconds)
    }

    private var showsPack: Bool {
        let settledRetreat = packDeparted ? 1.0 : 0.0
        if isNativeHybridCandidate {
            return GachaPackHandoffRules.packArtIsForeground(
                packVisible: gate.phase != .choosingPack,
                retreatProgress: settledRetreat)
        }
        return GachaPackHandoffRules.showsPack(
            revealComplete: gate.phase == .complete,
            retreatProgress: settledRetreat)
    }

    public init() {}

    public var body: some View {
        ZStack {
            // The Pack-hue backdrop belongs to the carousel only. Selecting a
            // Pack fades it out over the live Unity stage (cave at 25%), so
            // there is no black state anywhere in the flow (spec §1.3).
            if stageBackdropOpacity > 0.001 {
                ProductPackHueBackdrop(
                    accent: selectedPack.storefrontBackdropAccent,
                    strength: selectedPack.storefrontBackdropStrength)
                    .ignoresSafeArea()
                    .opacity(stageBackdropOpacity)
                    .animation(backdropFollowAnimation, value: selectedPack)
            }

            // FDB-GAC-035 (amended 2026-09-07): source arc structure from
            // the carousel on, one metallic colourway per selected Pack tier
            // — never the receipt. Switching Packs crossfades the colourway;
            // the layer leaves with the seal before case handoff.
            if usesPackArcBackdrop {
                ProductPackArcBandsBackdrop(
                    intensity: packArcBackdropIntensity,
                    colourway: GachaPackArcBackdropRules.Colourway
                        .forTier(selectedPack))
                    .ignoresSafeArea()
                    .animation(backdropFollowAnimation, value: selectedPack)

                // Recreated per tier: the selected colour visibly grows from
                // the floor first; the wash and arcs above follow after
                // `backdropFollowDelaySeconds`, then it settles into the
                // persistent bottom glow.
                ProductPackBottomGlowGrowth(
                    accent: selectedPack.storefrontBackdropAccent,
                    strength: selectedPack.storefrontBackdropStrength,
                    reduceMotion: reduceMotion)
                    .id(selectedPack)
                    .ignoresSafeArea()
                    .opacity(packArcBackdropIntensity)
            }

            // Fine dust rides above the arcs, below the Pack, and keeps
            // drifting over the rising case until the flip (R053).
            if usesPackAmbience {
                ProductPackBackdropAmbience(
                    tier: selectedPack,
                    accent: selectedPack.storefrontDustAccent,
                    reference: idleReference,
                    reduceMotion: reduceMotion)
                    .ignoresSafeArea()
                    .opacity(packAmbienceIntensity)
                    .allowsHitTesting(false)
            }

            if gate.phase == .choosingPack {
                packSelection
                    .transition(.opacity.animation(.linear(
                        duration: GachaPackHandoffRules.selectionFadeSeconds)))
            } else if showsPack {
                PackTearStage(
                    tier: selectedPack,
                    phase: gate.phase,
                    tearProgress: $tearProgress,
                    releasePulseStrength: packReleasePulseStrength,
                    retreatProgress: packRetreatProgress,
                    liveCaseReady: liveCaseApertureAvailable,
                    reduceMotion: reduceMotion,
                    mouthGapeScale: mouthGapeScale,
                    matchedGeometryNamespace: packNamespace,
                    idleReference: idleReference,
                    motion: motion,
                    onTearStarted: markTearStarted,
                    onCommit: commitPack)
            }

            if gate.phase == .complete,
               showsCompletedOverlay,
               !isNativeHybridCandidate,
               let receipt = model.pendingReceipt.first {
                completedOverlay(receipt)
                    .transition(.move(edge: .bottom).animation(
                        .timingCurve(
                            0.16, 1, 0.3, 1,
                            duration: GachaPackHandoffRules.resultPanelSlideSeconds)))
            } else if gate.phase != .choosingPack,
                      !isNativeHybridCandidate {
                progressChrome
            }
        }
        .productDesignSystem()
        .modifier(GachaTransparentPresentation())
        .interactiveDismissDisabled(gate.transactionID != nil)
        .onAppear {
            model.clearRevealState()
            model.requestState()
            motion.start(preferScripted: isGate12Preview)
            // The catalog can already be loaded before this view appears,
            // in which case onChange never fires.
            startAutomaticPreviewIfNeeded()
        }
        .onChange(of: gate.phase) { _ in
            if packMotionPhase {
                motion.start(preferScripted: isGate12Preview)
            } else {
                motion.stop()
            }
        }
        .onChange(of: model.series) { _ in
            startAutomaticPreviewIfNeeded()
        }
        .onChange(of: model.pendingReceipt) { _ in
            consumeAuthoritativeReceipt()
        }
        .onChange(of: model.lastFailureReason) { reason in
            handleDrawFailure(reason)
        }
        .onChange(of: model.receiptRequestID) { _ in
            consumeAuthoritativeReceipt()
        }
        .onChange(of: model.revealSetupSucceeded) { succeeded in
            handleUnitySetup(succeeded)
        }
        .onChange(of: model.revealPhase) { phase in
            handleUnityPhase(phase)
        }
        .onChange(of: model.revealCaseCrossedPackLip) { crossed in
            guard crossed, let transactionID = gate.transactionID else {
                return
            }
            beginNativeHybridPackDeparture(transactionID)
        }
        .onDisappear {
            motion.stop()
            if let transactionID = gate.transactionID,
               !gate.acknowledgementSent {
                model.interruptReveal(requestID: transactionID)
            }
            if stageEntered {
                model.leaveGachaStage()
            }
        }
    }

    private var packSelection: some View {
        VStack(spacing: FidgetUITokens.Spacing.standard) {
            HStack {
                ProductIconButton(
                    symbol: "chevron.left",
                    accessibilityLabel: "返回") {
                    dismiss()
                }
                Spacer()
                if let drawFailureNotice {
                    ProductStatusTag(title: drawFailureNotice)
                        .accessibilityIdentifier("gacha-draw-failure")
                }
            }
            .padding(.horizontal, FidgetUITokens.Spacing.section)
            .animation(.easeOut(duration: 0.25), value: drawFailureNotice)

            // Odds copy moved under the price (user 22:31); the heading is
            // the reversed-out emblem over the tier name.
            ProductScreenHeading(
                title: selectedPack.title,
                subtitle: "",
                centered: true,
                titleStyle: .title2,
                subtitleStyle: .footnote,
                emblemAssetName: selectedPack.emblemAssetName)
                .padding(.horizontal, FidgetUITokens.Spacing.section)
                .padding(.top, 16)
                .padding(.bottom, FidgetUITokens.Spacing.compact)
                .animation(
                    .easeOut(duration: FidgetUITokens.Motion.selectionDuration),
                    value: selectedPack)

            PackCarousel(
                selection: $selectedPack,
                matchedGeometryNamespace: packNamespace,
                idleReference: idleReference,
                reduceMotion: reduceMotion,
                motion: motion,
                onSnap: { tier in
                    model.emitCarouselSnap(
                        signal: GachaPackTierLadder.snapHapticSignal(for: tier))
                })
                .frame(maxHeight: .infinity)

            VStack(spacing: FidgetUITokens.Spacing.section) {
                ProductPageIndicator(
                    items: Array(GachaPackTier.allCases),
                    selection: selectedPack,
                    accessibilityLabel: { index, count in
                        "Pack 第 \(index) 档，共 \(count) 档"
                    })
                    .accessibilityIdentifier("gacha-pack-page-indicator")
                    // 16 pt higher than the caption spacing (user 22:31).
                    .padding(.bottom, 16)

                ProductPackTierCaption(
                    title: selectedPack.storefrontPriceLabel,
                    detail: selectedPack.storefrontOddsLine,
                    accent: .white,
                    itemSpacing: FidgetUITokens.Spacing.compact,
                    footnote: GachaPackPaymentRules.priceLine(
                        tickets: model.tickets, coins: model.coins))
                    .animation(
                        .easeOut(duration: FidgetUITokens.Motion.selectionDuration),
                        value: selectedPack)
                    .accessibilityIdentifier("gacha-pack-tier-caption")

                ProductPrimaryActionButton(
                    title: "购买",
                    accent: selectedPack.storefrontAccent,
                    surface: .filledWhite,
                    state: activeSeries == nil
                        ? .loading
                        : (drawPaymentMethod == nil ? .disabled : .ready)) {
                    beginSelection()
                }
                .accessibilityIdentifier("gacha-pack-select")
            }
            .padding(.horizontal, FidgetUITokens.Spacing.section)
            .padding(.bottom, FidgetUITokens.Spacing.standard)
        }
        .padding(.top, FidgetUITokens.Spacing.standard)
    }

    /// Only user-facing copy reaches this layer. Internal phases such as
    /// waiting for the receipt or staging the case have no label (spec §2.10).
    private var visibleStatusTitle: String? {
        switch gate.phase {
        case .tearPack where tearProgress < GachaPackOpeningRules.tearCommitProgress:
            return "沿封边撕开"
        case .receiptRecovery:
            return "等待权威结果"
        default:
            return nil
        }
    }

    private var progressChrome: some View {
        VStack {
            HStack {
                if let title = visibleStatusTitle {
                    ProductStatusTag(title: title)
                }
                Spacer()
            }
            .padding(.horizontal, FidgetUITokens.Spacing.section)
            .padding(.top, FidgetUITokens.Spacing.section)
            Spacer()
            if gate.phase == .receiptRecovery {
                ProductBottomActionDock {
                    ProductPrimaryActionButton(title: "刷新权威结果") {
                        model.requestState()
                    }
                }
            } else if gate.phase == .handoff {
                ProductBottomActionDock {
                    HStack {
                        Spacer()
                        ProductSecondaryActionButton(title: "跳过展示") {
                            skipReveal()
                        }
                    }
                }
            } else {
                // No dock while the Pack is torn and the case is staged; a
                // black placeholder here would be the "black state" §1.3 bans.
                Color.clear.frame(height: 0)
            }
        }
        .allowsHitTesting(
            gate.phase == .receiptRecovery || gate.phase == .handoff)
    }

    /// R053 (user 2026-09-09 18:58): English copy only, no level or id;
    /// the tag, heading and sheet carry the carousel's tilt-driven foil.
    private func completedOverlay(_ receipt: GachaReceiptRow) -> some View {
        TimelineView(.animation(paused: reduceMotion)) { context in
            let sample = motion.sample(at: context.date)
            let sheen = GachaPackHolographicSheenRules.pose(
                elapsed: context.date.timeIntervalSince(idleReference),
                idleAmplitude: 1,
                gravityX: sample.gravityX,
                gravityY: sample.gravityY,
                sweepProgress: sample.sweepProgress,
                reduceMotion: reduceMotion)
            VStack {
                HStack {
                    ProductStatusTag(
                        title: GachaRevealResultCopy.tag,
                        sheenPose: sheen)
                    Spacer()
                }
                .padding(.horizontal, FidgetUITokens.Spacing.section)
                .padding(.top, FidgetUITokens.Spacing.section)

                Spacer()

                ProductBottomActionDock(sheenPose: sheen) {
                    VStack(spacing: FidgetUITokens.Spacing.standard) {
                        ProductScreenHeading(
                            title: receipt.resultTitle,
                            subtitle: GachaRevealResultCopy.subtitle(
                                rarityTitle: receipt.rarity.plateTitle,
                                plateEdition: receipt.plateEdition),
                            centered: true,
                            titleSheenPose: sheen)
                        ProductPrimaryActionButton(
                            title: "收下",
                            state: acknowledgementState) {
                            acknowledge()
                        }
                        .accessibilityIdentifier("gacha-reveal-accept")
                    }
                }
            }
        }
    }

    private var statusTitle: String {
        switch gate.phase {
        case .choosingPack: return "选择 PACK"
        case .selectionRive: return "PACK 已选中"
        case .tearPack: return "沿封边撕开"
        case .waitingForReceipt: return "确认权威结果"
        case .preparingCase: return "准备真实收藏盒"
        case .handoff: return "收藏盒入场"
        case .complete: return "揭晓完成"
        case .receiptRecovery: return "等待权威结果"
        }
    }

    private func beginSelection() {
        guard activeSeries != nil, gate.transactionID == nil else { return }
        let transactionID = UUID()
        // The phase change swaps the carousel for the tear stage; inside one
        // animated transaction the shared-geometry Pack travels and grows
        // from its carousel slot to the stage instead of cutting.
        var began = false
        withAnimation(.timingCurve(
            0.16, 1, 0.3, 1,
            duration: GachaPackHandoffRules.selectionTravelSeconds)) {
            began = gate.begin(transactionID: transactionID)
            tearProgress = 0
            packReleasePulseStrength = 0
            mouthGapeScale = 1
            frontRevealed = false
        }
        guard began else { return }
        // The live stage (cave at 25%) is behind the Pack from here on.
        stageEntered = true
        model.enterGachaStage(
            tint: selectedPack.storefrontBackdropRGB,
            strength: selectedPack.storefrontBackdropStrength,
            backdropSnapshotPath: renderStageBackdropSnapshot())
        withAnimation(.linear(
            duration: GachaPackHandoffRules.selectionFadeSeconds)) {
            stageBackdropOpacity = 0
        }
        Task { @MainActor in
            do {
                try await Task.sleep(nanoseconds: 320_000_000)
            } catch {
                return
            }
            guard gate.markSelectionFinished(
                transactionID: transactionID) else { return }
            if isNativeHybridCandidate {
                await runNativeHybridCandidateTear(
                    transactionID: transactionID)
            } else if isGate12Preview {
                do {
                    // FDB-GAC-036 preview only: hold the staged Pack for one
                    // shake-driven laser sweep before the tear.
                    try await Task.sleep(nanoseconds: 500_000_000)
                    motion.simulateShake()
                    try await Task.sleep(nanoseconds: 1_300_000_000)
                    try await Task.sleep(
                        nanoseconds: GachaPackHandoffRules
                            .nativeHybridTearLeadInNanoseconds)
                } catch {
                    return
                }
                // One confident slice. A hesitate-and-retry rehearsal
                // misrepresents the shipping beat.
                markTearStarted()
                withAnimation(.timingCurve(
                    0.83, 0, 0.17, 1,
                    duration: GachaPackHandoffRules
                        .nativeHybridTearDurationSeconds)) {
                    tearProgress = GachaPackOpeningRules.tearCommitProgress
                }
                do {
                    try await Task.sleep(nanoseconds: UInt64(
                        GachaPackHandoffRules
                            .nativeHybridTearDurationSeconds
                            * 1_000_000_000))
                } catch {
                    return
                }
                commitPack()
            }
        }
    }

    private func runNativeHybridCandidateTear(
        transactionID: UUID
    ) async {
        guard gate.transactionID == transactionID,
              gate.phase == .tearPack else { return }
        if let staticStage {
            switch staticStage {
            case .sealed:
                return
            case .partial:
                tearProgress = 0.31
            case .emptyMouth, .containedCase, .caseCrossing:
                tearProgress = GachaPackOpeningRules.tearCommitProgress
                commitPack()
            }
            return
        }
        if reduceMotion {
            tearProgress = GachaPackOpeningRules.tearCommitProgress
            commitPack()
            return
        }

        do {
            try await Task.sleep(nanoseconds:
                GachaPackHandoffRules.nativeHybridTearLeadInNanoseconds)
        } catch {
            return
        }
        guard gate.transactionID == transactionID,
              gate.phase == .tearPack else { return }
        markTearStarted()
        withAnimation(.timingCurve(
            0.83, 0, 0.17, 1,
            duration: GachaPackHandoffRules
                .nativeHybridTearDurationSeconds)) {
            tearProgress = GachaPackOpeningRules.tearCommitProgress
        }
        do {
            try await Task.sleep(nanoseconds: UInt64(
                (GachaPackHandoffRules.nativeHybridTearDurationSeconds
                    + 0.02) * 1_000_000_000))
        } catch {
            return
        }
        guard gate.transactionID == transactionID,
              gate.phase == .tearPack else { return }
        commitPack()
    }

    /// Renders the native stage backdrop (arc bands + base) to a PNG so
    /// Unity can keep the identical image behind the rising case until the
    /// card flips (user: 卡片啪转过来那一刻再切场景). 1× scale: the
    /// gradients are smooth, so upscaling costs nothing visible.
    private func renderStageBackdropSnapshot() -> String? {
        let bounds = UIScreen.main.bounds
        // Arcs plus the settled floor glow: what the user saw behind the
        // Pack must be what Unity keeps behind the rising case (R053).
        let view = ZStack {
            ProductPackArcBandsBackdrop(
                intensity: GachaPackArcBackdropRules.visibility(
                    tearProgress: 0,
                    stageEligible: true),
                colourway: GachaPackArcBackdropRules.Colourway.forTier(selectedPack))
            ProductPackBottomGlowGrowth(
                accent: selectedPack.storefrontBackdropAccent,
                strength: selectedPack.storefrontBackdropStrength,
                settled: true)
        }
            .frame(width: bounds.width, height: bounds.height)
            .background(Color.black)
            .productDesignSystem()
        let image: UIImage?
        if #available(iOS 16.0, *) {
            let renderer = ImageRenderer(content: view)
            renderer.scale = 1
            renderer.proposedSize = ProposedViewSize(bounds.size)
            image = renderer.uiImage
        } else {
            let host = UIHostingController(rootView: view)
            host.view.bounds = bounds
            host.view.backgroundColor = .black
            let format = UIGraphicsImageRendererFormat()
            format.scale = 1
            image = UIGraphicsImageRenderer(bounds: bounds, format: format).image { _ in
                host.view.drawHierarchy(in: bounds, afterScreenUpdates: true)
            }
        }
        guard let data = image?.pngData() else { return nil }
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("gacha-stage-backdrop.png")
        do {
            try data.write(to: url, options: .atomic)
        } catch {
            return nil
        }
        return url.path
    }

    /// T0 of the reveal timeline. Commit follows 320 ms later.
    private func markTearStarted() {
        tearStartInstant = Date()
    }

    private func commitPack() {
        guard let transactionID = gate.transactionID,
              let series = activeSeries,
              gate.markPackCommitted(
                transactionID: transactionID) else { return }
        commitInstant = Date()
        model.emitTearSnap()
        // Seal flight: 480 ms EASE_OUT (spec §2.7). The pose maps progress to
        // lift, drift, rotation and fade.
        withAnimation(.timingCurve(
            0.16, 1, 0.3, 1,
            duration: GachaPackOpeningRules.flapExitDurationSeconds)) {
            tearProgress = 1
        }
        // Mouth gape: scaleY 1 → 1.06 with an overshoot (spec §2.8).
        withAnimation(.timingCurve(
            0.34, 1.56, 0.64, 1,
            duration: GachaPackHandoffRules.mouthGapeSeconds)) {
            mouthGapeScale = GachaPackHandoffRules.mouthGapeScale
        }
        if reduceMotion {
            packReleasePulseStrength = 0
        } else {
            withAnimation(.easeOut(
                duration: GachaPackOpeningRules.releasePulseRiseSeconds)) {
                packReleasePulseStrength = 1
            }
            Task { @MainActor in
                do {
                    try await Task.sleep(nanoseconds: UInt64(
                        GachaPackOpeningRules.releasePulsePeakSeconds
                            * 1_000_000_000))
                } catch {
                    return
                }
                withAnimation(.easeOut(
                    duration: GachaPackOpeningRules
                        .releasePulseDurationSeconds
                        - GachaPackOpeningRules.releasePulsePeakSeconds)) {
                    packReleasePulseStrength = 0
                }
            }
        }
        Task { @MainActor in
            if !reduceMotion {
                do {
                    try await Task.sleep(nanoseconds:
                        GachaPackHandoffRules.drawAfterLidClearNanoseconds)
                } catch {
                    return
                }
                guard gate.transactionID == transactionID else { return }
            }
            model.draw(
                requestID: transactionID,
                seriesId: series.id,
                count: 1,
                useCoins: drawPaymentMethod == .coins)
            do {
                try await Task.sleep(
                    nanoseconds: GachaSingleDrawGateState
                        .receiptTimeoutNanoseconds)
            } catch {
                return
            }
            _ = gate.markReceiptTimeout(transactionID: transactionID)
        }
    }

    private var drawPaymentMethod: GachaPackPaymentRules.Method? {
        GachaPackPaymentRules.method(tickets: model.tickets, coins: model.coins)
    }

    /// Unity refused the draw (no tickets/coins, transaction in flight…).
    /// Roll the Pack back to sealed at once, leave the stage, and say why —
    /// instead of sitting 20 s until the receipt timeout.
    private func handleDrawFailure(_ reason: String) {
        guard !reason.isEmpty, gate.transactionID != nil else { return }
        switch gate.phase {
        case .complete, .handoff:
            return
        default:
            break
        }
        model.lastFailureReason = ""
        withAnimation(.easeOut(duration: 0.35)) {
            gate.reset()
            tearProgress = 0
            mouthGapeScale = 1
            packReleasePulseStrength = 0
            packRetreatProgress = 0
            packDeparted = false
            stageBackdropOpacity = 1
            frontRevealed = false
        }
        commitInstant = nil
        tearStartInstant = nil
        if stageEntered {
            stageEntered = false
            model.leaveGachaStage()
        }
        let message = GachaPackPaymentRules.failureMessage(reason: reason)
        drawFailureNotice = message
        Task { @MainActor in
            try? await Task.sleep(nanoseconds: UInt64(
                GachaPackPaymentRules.failureNoticeSeconds * 1_000_000_000))
            if drawFailureNotice == message {
                drawFailureNotice = nil
            }
        }
    }

    private func consumeAuthoritativeReceipt() {
        guard let transactionID = gate.transactionID,
              model.pendingReceipt.count == 1,
              gate.markReceiptArrived(
                requestID: model.receiptRequestID) else {
            restorePendingReceiptIfNeeded()
            return
        }
        if staticStage == .emptyMouth {
            return
        }
        prepareUnityCase(transactionID)
    }

    private func restorePendingReceiptIfNeeded() {
        guard gate.transactionID == nil,
              model.pendingReceipt.count == 1,
              let transactionID = UUID(
                uuidString: model.receiptRequestID),
              model.transactionPhase != "completed" else { return }
        gate.restorePending(transactionID: transactionID)
        tearProgress = 1
        packReleasePulseStrength = 0
        prepareUnityCase(transactionID)
    }

    private func prepareUnityCase(_ transactionID: UUID) {
        guard gate.phase == .preparingCase,
              !presentRequested else { return }
        presentRequested = true
        model.presentReveal(
            requestID: transactionID,
            nativeHybridCandidate: isNativeHybridCandidate)
    }

    private func handleUnitySetup(_ succeeded: Bool) {
        guard let transactionID = gate.transactionID,
              model.revealRequestID
                == transactionID.uuidString.lowercased() else { return }
        guard succeeded else {
            presentRequested = false
            return
        }
        guard gate.markUnityCaseReady(
            transactionID: transactionID),
              gate.markRevealStarted(
                transactionID: transactionID) else { return }
        if let staticStage {
            switch staticStage {
            case .containedCase:
                return
            case .caseCrossing:
                model.setNativeHybridPreviewProgress(
                    requestID: transactionID,
                    progress: GachaPackHandoffRules
                        .nativeHybridPackLipCrossingProgress)
                return
            case .sealed, .partial, .emptyMouth:
                return
            }
        }
        if isNativeHybridCandidate {
            if reduceMotion {
                beginNativeHybridPackDeparture(transactionID)
                model.startReveal(requestID: transactionID)
                return
            }
            Task { @MainActor in
                do {
                    try await Task.sleep(nanoseconds:
                        GachaPackHandoffRules
                            .nativeHybridContainmentHoldNanoseconds)
                } catch {
                    return
                }
                guard gate.transactionID == transactionID,
                      gate.allowsLiveCaseAperture else { return }
                beginNativeHybridPackDeparture(transactionID)
                model.startReveal(requestID: transactionID)
            }
            return
        }
        // Shipping: the case is pulled out of the mouth no earlier than
        // T0 + 700 ms (commit + 380 ms), and the Pack drops only once Unity
        // reports the case has cleared the lip (`case-crossing-pack-lip`).
        if reduceMotion {
            beginNativeHybridPackDeparture(transactionID)
        }
        let elapsed = commitInstant.map { Date().timeIntervalSince($0) } ?? 0
        let minimum = Double(
            GachaPackHandoffRules.caseReadyMinimumAfterCommitNanoseconds)
            / 1_000_000_000
        let wait = max(0, minimum - elapsed)
        Task { @MainActor in
            if wait > 0 {
                do {
                    try await Task.sleep(nanoseconds: UInt64(wait * 1_000_000_000))
                } catch {
                    return
                }
            }
            guard gate.transactionID == transactionID else { return }
            model.startReveal(requestID: transactionID)
        }
    }

    /// `packRetreatProgress` becomes 1 as a model value on the first frame
    /// of the slide, so `showsPack` reads `packDeparted`, which flips only
    /// after the slide has run. Otherwise SwiftUI unmounts the Pack at
    /// once and the retreat never renders.
    private func retreatPack(_ animation: Animation, duration: Double) {
        guard packRetreatProgress < 1 else { return }
        if reduceMotion {
            packRetreatProgress = 1
            packDeparted = true
            return
        }
        withAnimation(animation) {
            packRetreatProgress = 1
        }
        let transactionID = gate.transactionID
        DispatchQueue.main.asyncAfter(deadline: .now() + duration) {
            guard gate.transactionID == transactionID else { return }
            packDeparted = true
        }
    }

    private func handleUnityPhase(_ phase: String) {
        guard let transactionID = gate.transactionID,
              model.revealRequestID
                == transactionID.uuidString.lowercased() else { return }
        if staticStage != nil {
            return
        }
        if phase == "case-crossing-pack-lip" {
            beginNativeHybridPackDeparture(transactionID)
        } else if phase == "front-revealed" {
            // Unity lights the environment over the same 0.35 s; the native
            // motes leave with it (R053).
            withAnimation(reduceMotion
                ? .linear(duration: 0)
                : .easeOut(
                    duration: GachaPackArcBackdropRules.ambienceFadeSeconds)) {
                frontRevealed = true
            }
        } else if phase == "complete" {
            beginNativeHybridPackDeparture(transactionID)
            if !frontRevealed {
                withAnimation(.easeOut(
                    duration: GachaPackArcBackdropRules.ambienceFadeSeconds)) {
                    frontRevealed = true
                }
            }
            _ = gate.markRevealCompleted(
                requestID: model.revealRequestID)
            // Let the front face and its light settle before the result
            // panel arrives.
            Task { @MainActor in
                do {
                    try await Task.sleep(nanoseconds:
                        GachaPackHandoffRules.resultPanelDelayNanoseconds)
                } catch {
                    return
                }
                guard gate.transactionID == transactionID else { return }
                withAnimation(.timingCurve(
                    0.16, 1, 0.3, 1,
                    duration: GachaPackHandoffRules.resultPanelSlideSeconds)) {
                    showsCompletedOverlay = true
                }
            }
        } else if phase == "acknowledged" {
            acknowledgementState = .ready
            model.pendingReceipt = []
            gate.reset()
            dismiss()
        } else if phase.hasPrefix("ack-rejected:") {
            acknowledgementState = .ready
        }
    }

    private func beginNativeHybridPackDeparture(_ transactionID: UUID) {
        guard gate.transactionID == transactionID,
              gate.allowsLiveCaseAperture,
              staticStage == nil,
              packRetreatProgress < 1 else { return }
        let departure = GachaPackHandoffRules
            .nativeHybridPackDepartureDurationSeconds
        retreatPack(
            .timingCurve(0.33, 0, 0.2, 1, duration: departure),
            duration: departure)
    }

    private func skipReveal() {
        guard let transactionID = gate.transactionID,
              gate.phase == .handoff else { return }
        let departure = GachaPackHandoffRules
            .nativeHybridPackDepartureDurationSeconds
        retreatPack(.easeIn(duration: departure), duration: departure)
        model.skipReveal(requestID: transactionID)
    }

    private func acknowledge() {
        guard let transactionID = gate.transactionID,
              gate.markAcknowledgementSent(
                transactionID: transactionID) else { return }
        acknowledgementState = .loading
        model.acknowledgeReveal(requestID: transactionID)
    }

    private func startAutomaticPreviewIfNeeded() {
        if isCarouselLadderPreview, !automaticPreviewStarted {
            automaticPreviewStarted = true
            Task { @MainActor in
                do {
                    try await Task.sleep(nanoseconds: 1_600_000_000)
                    for tier in GachaPackTier.allCases.dropFirst() {
                        withAnimation(.interpolatingSpring(stiffness: 280, damping: 29)) {
                            selectedPack = tier
                        }
                        try await Task.sleep(nanoseconds: 2_600_000_000)
                    }
                    withAnimation(.interpolatingSpring(stiffness: 280, damping: 29)) {
                        selectedPack = .grail
                    }
                } catch {
                    return
                }
            }
            return
        }
        guard (isGate12Preview || isNativeHybridCandidate),
              !automaticPreviewStarted,
              activeSeries != nil else { return }
        automaticPreviewStarted = true
        if staticStage == .sealed {
            return
        }
        Task { @MainActor in
            do {
                if isGate12Preview {
                    // Rehearse one carousel step and back so the settled-Pack
                    // idle (float + yaw ramp-in) is part of the evidence.
                    // FDB-GAC-036: the Simulator has no gyroscope, so the
                    // scripted hand tilts continuously and shakes once per
                    // Pack to fire the laser sweep through the real pipeline.
                    try await Task.sleep(nanoseconds: 900_000_000)
                    motion.simulateShake()
                    try await Task.sleep(nanoseconds: 1_300_000_000)
                    withAnimation(.interpolatingSpring(stiffness: 280, damping: 29)) {
                        selectedPack = .refined
                    }
                    try await Task.sleep(nanoseconds: 900_000_000)
                    motion.simulateShake()
                    try await Task.sleep(nanoseconds: 1_300_000_000)
                    withAnimation(.interpolatingSpring(stiffness: 280, damping: 29)) {
                        selectedPack = .standard
                    }
                    try await Task.sleep(nanoseconds: 1_400_000_000)
                } else {
                    try await Task.sleep(nanoseconds: 700_000_000)
                }
            } catch {
                return
            }
            beginSelection()
        }
    }
}

private struct GachaTransparentPresentation: ViewModifier {
    @ViewBuilder
    func body(content: Content) -> some View {
        if #available(iOS 16.4, *) {
            content.presentationBackground(.clear)
        } else {
            content.background(GachaClearPresentationBackground())
        }
    }
}

private struct GachaClearPresentationBackground: UIViewRepresentable {
    func makeUIView(context: Context) -> UIView {
        let view = UIView()
        DispatchQueue.main.async {
            view.superview?.superview?.backgroundColor = .clear
        }
        return view
    }

    func updateUIView(_ uiView: UIView, context: Context) {}
}

private struct PackCarousel: View {
    /// Carousel Pack is the stage Pack ÷ 1.18, so selection grows it 1.18×
    /// (spec §1.1) into the fixed 280 pt tear artwork.
    static let packWidth = CGFloat(
        GachaPackOpeningRules.artworkWidthPoints
            / GachaPackHandoffRules.selectionScale)
    static let packHeight = CGFloat(
        GachaPackOpeningRules.artworkHeightPoints
            / GachaPackHandoffRules.selectionScale)

    @Binding var selection: GachaPackTier
    let matchedGeometryNamespace: Namespace.ID
    let idleReference: Date
    let reduceMotion: Bool
    var motion: GachaPackMotionFeed? = nil
    /// Snap detent through the semantic Haptic pipeline, weighted by tier.
    var onSnap: ((GachaPackTier) -> Void)? = nil
    @GestureState private var dragTranslation = 0.0
    /// Set when a swipe releases; the idle ramps in from here (user request:
    /// the 3D float appears once the carousel stops on a Pack).
    @State private var settledAt: Date? = nil
    /// True when the last change moved to a richer tier: the arriving Pack
    /// rises and settles (GachaPackTierLadder); stepping down just slides.
    @State private var steppedUp = false
    @State private var previousSelection: GachaPackTier? = nil

    private var selectedIndex: Int {
        GachaPackTier.allCases.firstIndex(of: selection) ?? 0
    }

    private var isDragging: Bool {
        dragTranslation != 0
    }

    var body: some View {
        GeometryReader { proxy in
            ZStack {
                ForEach(
                    Array(GachaPackTier.allCases.enumerated()),
                    id: \.element.rawValue
                ) { index, tier in
                    let position =
                        GachaPackCarouselRules.continuousPosition(
                            itemIndex: index,
                            selectedIndex: selectedIndex,
                            translationPoints: GachaPackCarouselRules
                                .displayedTranslation(
                                    translationPoints: dragTranslation))
                    // One view branch per Pack, whatever is selected: every
                    // Pack keeps its matched-geometry modifier (inert id when
                    // not selected) and its sheen overlay. Toggling either on
                    // selection changed view identity and crossfaded a ghost
                    // copy during the snap (user 2026-09-08 12:16 "拖影").
                    PackArtwork(tier: tier)
                        .modifier(ProductMatchedGeometry(
                            id: index == selectedIndex
                                ? GachaPackHandoffRules.selectedPackGeometryID
                                : nil,
                            namespace: matchedGeometryNamespace,
                            fallbackID: "gacha-pack-slot-\(index)"))
                        .frame(
                            width: PackCarousel.packWidth,
                            height: PackCarousel.packHeight)
                        .modifier(ProductPackIdleFloat(
                            active: !reduceMotion
                                && !isDragging
                                && index == selectedIndex,
                            reference: idleReference,
                            settledAt: settledAt,
                            motion: index == selectedIndex ? motion : nil,
                            sheenMaskAssetName: tier.foilAssetName,
                            reduceMotion: reduceMotion,
                            tier: tier,
                            steppedUp: steppedUp,
                            carouselPosition: position,
                            suspended: isDragging,
                            printAssetName: tier.printAssetName,
                            shadowMaskAssetName: tier.bodyAssetName))
                        .scaleEffect(
                            GachaPackCarouselRules.packScale(
                                isSelected: index == selectedIndex))
                        .offset(
                            x: GachaPackCarouselRules.horizontalOffset(
                                continuousPosition: position),
                            y: GachaPackCarouselRules.verticalOffset(
                                continuousPosition: position))
                        .rotationEffect(.degrees(
                            GachaPackCarouselRules.tiltDegrees(
                                continuousPosition: position)))
                        .zIndex(index == selectedIndex ? 10 : 1)
                        .accessibilityLabel(tier.title)
                }
            }
            .frame(
                width: proxy.size.width,
                height: proxy.size.height)
            .contentShape(Rectangle())
            .gesture(
                // Dead travel before the Pack moves read as lag (user
                // 2026-09-08 18:48 / 22:31 "不太跟手"): 12 → 6 → 3 pt.
                DragGesture(minimumDistance: 3)
                    .updating($dragTranslation) { value, state, _ in
                        state = value.translation.width
                    }
                    .onEnded { value in
                        let next = GachaPackCarouselRules.nextIndex(
                            selectedIndex: selectedIndex,
                            itemCount: GachaPackTier.allCases.count,
                            translationPoints: value.translation.width,
                            predictedEndTranslationPoints:
                                value.predictedEndTranslation.width)
                        settledAt = Date()
                        withAnimation(.interpolatingSpring(
                            stiffness: GachaPackCarouselRules.snapStiffness,
                            damping: GachaPackCarouselRules.snapDamping)) {
                            selection = GachaPackTier.allCases[next]
                        }
                    })
        }
        .accessibilityIdentifier("gacha-pack-carousel")
        .onChange(of: selection) { next in
            let previousIndex = previousSelection.map(GachaPackTierLadder.index(of:)) ?? 0
            steppedUp = GachaPackTierLadder.index(of: next) > previousIndex
            previousSelection = next
            settledAt = Date()
            onSnap?(next)
        }
        .onAppear { previousSelection = selection }
    }
}

private struct PackTearStage: View {
    let tier: GachaPackTier
    let phase: GachaSingleDrawGateState.Phase
    @Binding var tearProgress: Double
    let releasePulseStrength: Double
    let retreatProgress: Double
    let liveCaseReady: Bool
    let reduceMotion: Bool
    let mouthGapeScale: Double
    let matchedGeometryNamespace: Namespace.ID
    let idleReference: Date
    var motion: GachaPackMotionFeed? = nil
    let onTearStarted: () -> Void
    let onCommit: () -> Void

    @State private var longPressArmed = false

    private var effectiveRetreatProgress: Double {
        reduceMotion && retreatProgress > 0 ? 1 : retreatProgress
    }

    /// The sealed Pack drifts, yaws and shows a seal highlight while it waits
    /// for the tear (spec §1.4). Everything stops the moment the tear moves.
    private var isIdle: Bool {
        !reduceMotion
            && tearProgress <= 0.0001
            && (phase == .selectionRive || phase == .tearPack)
    }

    var body: some View {
        TimelineView(.animation(paused: !isIdle)) { context in
            let t = context.date.timeIntervalSince(idleReference)
            let idle = isIdle
            let float = idle ? GachaPackIdleMotion.offsetPoints(elapsed: t) : 0
            let yaw = idle ? GachaPackIdleMotion.yawDegrees(elapsed: t) : 0
            // Tier ladder: the sealed Pack keeps knocking from inside while
            // it waits for the tear; richer tiers knock harder and more often.
            let wriggleX = idle
                ? GachaPackTierLadder.wriggleOffsetPoints(elapsed: t, tier: tier) : 0
            let wriggleRoll = idle
                ? GachaPackTierLadder.wriggleDegrees(elapsed: t, tier: tier) : 0
            let wriggleScale = idle
                ? GachaPackTierLadder.wriggleScale(elapsed: t, tier: tier) : 1
            let sweep: Double? = idle
                ? GachaPackIdleMotion.sealSweepProgress(elapsed: t)
                : nil
            // FDB-GAC-036: device tilt slides the foil sheen and tilts the
            // Pack; a shake fires one laser sweep. Frozen once the tear moves.
            let sample = idle ? (motion?.sample(at: context.date) ?? .still) : .still
            let sheen = GachaPackHolographicSheenRules.pose(
                elapsed: t,
                idleAmplitude: idle ? 1 : 0,
                gravityX: sample.gravityX,
                gravityY: sample.gravityY,
                sweepProgress: sample.sweepProgress,
                reduceMotion: reduceMotion)

            GeometryReader { proxy in
                ZStack {
                    ProductPackTearRevealLayer(
                        bodyAssetName: tier.bodyAssetName,
                        flapAssetName: tier.flapAssetName,
                        tearProgress: tearProgress,
                        seamLightStrength:
                            GachaPackOpeningRules.seamLightStrength(
                                progress: tearProgress,
                                gestureActive: phase == .tearPack,
                                handoffActive: phase == .handoff,
                                retreatProgress: effectiveRetreatProgress),
                        releasePulseStrength: releasePulseStrength,
                        liveCaseReady: liveCaseReady,
                        retreatProgress: effectiveRetreatProgress,
                        idleOffsetPoints: float,
                        idleYawDegrees: yaw + sheen.tiltYawDegrees,
                        idlePitchDegrees: sheen.tiltPitchDegrees,
                        idleWriggleXPoints: wriggleX,
                        idleWriggleRollDegrees: wriggleRoll,
                        idleWriggleScale: wriggleScale,
                        sheenPose: sheen,
                        sheenMaskAssetName: tier.foilAssetName,
                        printAssetName: tier.printAssetName,
                        glareEnabled: !reduceMotion,
                        shadowTint: tier.shadowTint,
                        interiorTier: tier,
                        idleSealSweepProgress: sweep,
                        mouthGapeScale: mouthGapeScale,
                        matchedGeometryID:
                            GachaPackHandoffRules.selectedPackGeometryID,
                        matchedGeometryNamespace: matchedGeometryNamespace)

                    // Seal hit area (72 pt, spec §1.5): drag ≥ 40% of the
                    // Pack width along the seal, or hold 450 ms.
                    let hit = ProductPackTearRevealLayer.sealHitRect(
                        in: proxy.size)
                    Color.clear
                        .contentShape(Rectangle())
                        .frame(width: hit.width, height: hit.height)
                        .position(x: hit.midX, y: hit.midY + float)
                        .gesture(tearDrag)
                        .simultaneousGesture(sealLongPress)
                        .allowsHitTesting(phase == .tearPack)
                        .accessibilityIdentifier("gacha-pack-tear")
                        .accessibilityLabel("沿封边撕开")
                        .accessibilityAction(named: "撕开") { autoTear() }
                }
            }
        }
    }

    private var tearDrag: some Gesture {
        DragGesture(minimumDistance: 4)
            .onChanged { value in
                guard phase == .tearPack else { return }
                if tearProgress <= 0.0001 { onTearStarted() }
                tearProgress = GachaPackOpeningRules
                    .normalizedProgress(
                        translationPoints: value.translation.width)
            }
            .onEnded { _ in
                guard phase == .tearPack else { return }
                if GachaPackOpeningRules.shouldCommit(
                    progress: tearProgress) {
                    onCommit()
                } else {
                    withAnimation(.easeOut(
                        duration: FidgetUITokens
                            .Motion.selectionDuration)) {
                        tearProgress = 0
                    }
                }
            }
    }

    private var sealLongPress: some Gesture {
        LongPressGesture(
            minimumDuration: GachaPackHandoffRules.sealLongPressSeconds)
            .onEnded { _ in
                guard phase == .tearPack, tearProgress <= 0.0001 else { return }
                autoTear()
            }
    }

    /// One confident tear from the left seal anchor to the right:
    /// 320 ms EASE_IN_OUT, then commit (spec §2.6).
    private func autoTear() {
        guard phase == .tearPack, !longPressArmed else { return }
        longPressArmed = true
        onTearStarted()
        withAnimation(.timingCurve(
            0.83, 0, 0.17, 1,
            duration: GachaPackHandoffRules.nativeHybridTearDurationSeconds)) {
            tearProgress = GachaPackOpeningRules.tearCommitProgress
        }
        Task { @MainActor in
            do {
                try await Task.sleep(nanoseconds: UInt64(
                    GachaPackHandoffRules.nativeHybridTearDurationSeconds
                        * 1_000_000_000))
            } catch {
                return
            }
            longPressArmed = false
            guard phase == .tearPack else { return }
            onCommit()
        }
    }
}

private struct PackArtwork: View {
    let tier: GachaPackTier

    var body: some View {
        ProductPackSealedArtwork(
            bodyAssetName: tier.bodyAssetName,
            flapAssetName: tier.flapAssetName)
            .scaledToFit()
            .accessibilityHidden(true)
    }
}

private extension GachaPackTier {
    var storefrontBackdropAccent: Color {
        let rgb = storefrontBackdropRGB
        return Color(red: rgb.red, green: rgb.green, blue: rgb.blue)
    }

    var storefrontAccent: Color {
        let rgb = storefrontAccentRGB
        return Color(red: rgb.red, green: rgb.green, blue: rgb.blue)
    }

    var storefrontDustAccent: Color {
        let base = storefrontBackdropRGB
        let rgb = GachaPackBackdropAmbienceRules.dustRGB(
            red: base.red, green: base.green, blue: base.blue)
        return Color(red: rgb.red, green: rgb.green, blue: rgb.blue)
    }

    /// Matches the tier arc-band gradient used under the carousel.
    var storefrontPrimaryGradient: LinearGradient {
        let stops = GachaPackArcBackdropRules.primaryStops(
            for: GachaPackArcBackdropRules.Colourway.forTier(self))
        let colors = stops.prefix(4).map { stop in
            Color(red: stop.red, green: stop.green, blue: stop.blue)
        }
        return LinearGradient(
            colors: colors,
            startPoint: .leading,
            endPoint: .trailing)
    }
}
