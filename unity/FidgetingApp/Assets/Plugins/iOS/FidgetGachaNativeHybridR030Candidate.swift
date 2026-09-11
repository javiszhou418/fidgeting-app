import Foundation
import SwiftUI
import UIKit

struct GachaNativeHybridR030LayerState: Equatable {
    let checkpoint: String
    let candidateSequenceStartedAtUnix: Double
    let phase: String
    let tearProgress: Double
    let retreatProgress: Double
    let rawRequestUUID: String
    let receiptUUID: String
    let stableFrameOrdinal: Int
    let unityFrameCount: Int
    let cameraInstanceID: Int64
    let cameraName: String
    let caseRootName: String
    let caseTypeName: String
    let caseEntityID: String
    let caseRendererCount: Int
    let foreignRendererCount: Int
    let caseStableFrame: Bool
    let cameraStableFrame: Bool
    let isolationActive: Bool
    let usesCavityClearBackdrop: Bool
    let publishSetupPublished: Bool
    let publishSetupSucceeded: Bool
    let publishSetupFailure: String
    let callbackResult: String
    let nativeUnityCaseReady: Bool
    let apertureAuthorized: Bool
    let packForeground: Bool
    let nativeHybridProgress: Double
    let caseIsCanonical: Bool
    let caseIsOnlyUnityRenderable: Bool
}

/// R030 keeps Pack pixels native and requires the real Unity readiness
/// callback before its mouth exposes the isolated live case.
struct GachaNativeHybridR030CandidateView: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @ObservedObject private var model = GachaStoreModel.shared

    let reportLayerState: (GachaNativeHybridR030LayerState) -> Void

    @State private var gate = GachaSingleDrawGateState()
    @State private var tearProgress = 0.0
    @State private var releasePulseStrength = 0.0
    @State private var packRetreatProgress = 0.0
    @State private var packDeparted = false
    @State private var sequenceStarted = false
    @State private var presentRequested = false
    @State private var revealStartScheduled = false
    @State private var diagnosticFailure = ""
    @State private var candidateSequenceStartedAtUnix = 0.0
    @State private var setupCallbackResult = "pending"
    @State private var reportedF2AfterCallback = false
    @State private var pendingF4Trace = false

    init(
        reportLayerState: @escaping (GachaNativeHybridR030LayerState) -> Void
    ) {
        self.reportLayerState = reportLayerState
    }

    private var captureCheckpoint: GachaNativeHybridR030CaptureCheckpoint? {
        GachaNativeHybridR030Rules.requestedCaptureCheckpoint
    }

    private var activeSeries: GachaSeriesInfo? {
        model.series.first
    }

    private var liveCaseApertureAvailable: Bool {
        GachaPackHandoffRules.canRevealLiveCase(
            hasAuthoritativeReceipt: gate.receiptArrived,
            caseStableAfterTwoFrames: gate.unityCaseReady,
            openingProgress: tearProgress)
    }

    /// `packRetreatProgress` jumps to 1 as a model value the moment the
    /// departure animation starts, so the layer stays mounted until the
    /// slide has actually finished; otherwise SwiftUI removes the Pack on
    /// the first frame and the retreat is never seen.
    private var packIsForeground: Bool {
        GachaPackHandoffRules.packArtIsForeground(
            packVisible: gate.phase != .complete,
            retreatProgress: packDeparted ? 1 : 0)
    }

    private var effectiveRetreatProgress: Double {
        reduceMotion && packRetreatProgress > 0 ? 1 : packRetreatProgress
    }

    var body: some View {
        Group {
            if packIsForeground {
                ProductLiveUnityPackRevealLayer(
                    bodyAssetName: GachaPackTier.standard.bodyAssetName,
                    flapAssetName: GachaPackTier.standard.flapAssetName,
                    tearProgress: tearProgress,
                    seamLightStrength: GachaPackOpeningRules.seamLightStrength(
                        progress: tearProgress,
                        gestureActive: gate.phase == .tearPack,
                        handoffActive: gate.phase == .handoff,
                        retreatProgress: effectiveRetreatProgress),
                    liveCaseReady: liveCaseApertureAvailable,
                    retreatProgress: effectiveRetreatProgress,
                    releasePulseStrength: releasePulseStrength)
            }
        }
        .productDesignSystem()
        .onAppear {
            startCandidate()
            reportLayer(checkpoint: "candidate-start")
        }
        .onChange(of: model.series) { _ in
            beginRequestIfPossible()
        }
        .onChange(of: model.pendingReceipt) { _ in
            consumeAuthoritativeReceipt()
        }
        .onChange(of: model.receiptRequestID) { _ in
            consumeAuthoritativeReceipt()
        }
        .onChange(of: model.revealSetupCallbackSerial) { _ in
            handleUnitySetup()
        }
        .onChange(of: model.nativeHybridR030Trace) { trace in
            handleUnityTrace(trace)
        }
        .onChange(of: model.revealPhase) { phase in
            handleUnityPhase(phase)
        }
        .onChange(of: tearProgress) { _ in
            reportLayer()
        }
        .onChange(of: packRetreatProgress) { _ in
            reportLayer()
            reportF4AfterDeparture()
        }
        .onChange(of: packDeparted) { _ in
            reportLayer()
            reportF4AfterDeparture()
        }
        .onDisappear {
            guard let transactionID = gate.transactionID else { return }
            model.interruptReveal(requestID: transactionID)
        }
    }

    private func startCandidate() {
        GachaNativeHybridR030Diagnostics.reset()
        switch captureCheckpoint {
        case .sealed:
            reportLayer(checkpoint: "sealed")
            return
        case .partial:
            tearProgress = 0.31
            reportLayer(checkpoint: "partial")
            return
        case .f0, .f1, .f2, .f3, .f4, nil:
            break
        }
        model.beginNativeHybridCandidate(
            previewToken: GachaNativeHybridR030Rules.previewToken)
    }

    private func beginRequestIfPossible() {
        guard !sequenceStarted,
              let series = activeSeries else {
            return
        }
        sequenceStarted = true
        candidateSequenceStartedAtUnix = Date().timeIntervalSince1970
        let transactionID = UUID()
        guard gate.begin(transactionID: transactionID),
              gate.markSelectionFinished(transactionID: transactionID) else {
            recordFailure(
                checkpoint: "request-rejected",
                reason: "candidate-request-gate-rejected")
            return
        }
        animateTear(transactionID: transactionID, seriesID: series.id)
    }

    private func animateTear(
        transactionID: UUID,
        seriesID: String
    ) {
        if reduceMotion {
            tearProgress = GachaPackOpeningRules.tearCommitProgress
            commitPack(transactionID: transactionID, seriesID: seriesID)
            return
        }

        DispatchQueue.main.asyncAfter(
            deadline: .now()
                + Double(GachaPackHandoffRules
                    .nativeHybridTearLeadInNanoseconds)
                / 1_000_000_000
        ) {
            guard gate.transactionID == transactionID,
                  gate.phase == .tearPack else {
                return
            }
            withAnimation(.linear(
                duration: GachaPackHandoffRules
                    .nativeHybridTearDurationSeconds)) {
                tearProgress = GachaPackOpeningRules.tearCommitProgress
            }
            DispatchQueue.main.asyncAfter(
                deadline: .now()
                    + GachaPackHandoffRules
                        .nativeHybridTearDurationSeconds
            ) {
                guard gate.transactionID == transactionID,
                      gate.phase == .tearPack else {
                    return
                }
                commitPack(
                    transactionID: transactionID,
                    seriesID: seriesID)
            }
        }
    }

    private func commitPack(
        transactionID: UUID,
        seriesID: String
    ) {
        guard gate.transactionID == transactionID,
              gate.markPackCommitted(transactionID: transactionID) else {
            recordFailure(
                checkpoint: "pack-commit-rejected",
                reason: "pack-commit-not-exact-once")
            return
        }
        playLidRelease()
        let draw = {
            guard gate.transactionID == transactionID else { return }
            model.draw(
                requestID: transactionID,
                seriesId: seriesID,
                count: 1,
                useCoins: false)
        }
        guard captureCheckpoint == nil, !reduceMotion else {
            draw()
            return
        }
        DispatchQueue.main.asyncAfter(
            deadline: .now()
                + Double(GachaPackHandoffRules.drawAfterLidClearNanoseconds)
                / 1_000_000_000,
            execute: draw)
    }

    /// Full-sequence runs share the shipping commit beat: the lid leaves as
    /// one rigid piece and the release pulse fires. Capture checkpoints keep
    /// the tear parked at commit so F0–F4 overlays stay comparable.
    private func playLidRelease() {
        guard captureCheckpoint == nil, !reduceMotion else { return }
        // Linear drive: the lid pose smoothsteps internally, and a second
        // easing on top reads as a jump cut at commit.
        withAnimation(.linear(
            duration: GachaPackOpeningRules.flapExitDurationSeconds)) {
            tearProgress = 1
        }
        withAnimation(.easeOut(
            duration: GachaPackOpeningRules.releasePulseRiseSeconds)) {
            releasePulseStrength = 1
        }
        DispatchQueue.main.asyncAfter(
            deadline: .now()
                + GachaPackOpeningRules.releasePulsePeakSeconds
        ) {
            withAnimation(.easeOut(
                duration: GachaPackOpeningRules.releasePulseDurationSeconds
                    - GachaPackOpeningRules.releasePulsePeakSeconds)) {
                releasePulseStrength = 0
            }
        }
    }

    private func consumeAuthoritativeReceipt() {
        guard let transactionID = gate.transactionID,
              model.pendingReceipt.count == 1,
              gate.markReceiptArrived(
                requestID: model.receiptRequestID) else {
            return
        }
        prepareUnityCase(transactionID)
    }

    private func prepareUnityCase(_ transactionID: UUID) {
        guard gate.phase == .preparingCase,
              !presentRequested else {
            return
        }
        presentRequested = true
        model.configureR030CaptureCheckpoint(
            requestID: transactionID,
            checkpoint: captureCheckpoint)
        model.presentR030NativeHybridReveal(requestID: transactionID)
    }

    private func handleUnitySetup() {
        guard let transactionID = gate.transactionID,
              model.revealRequestID
                == transactionID.uuidString.lowercased() else {
            setupCallbackResult = "rejected:stale-setup-callback"
            recordFailure(
                checkpoint: "setup-callback-rejected",
                reason: "stale-setup-callback")
            return
        }
        guard model.revealSetupSucceeded else {
            let failure = model.revealSetupFailure.isEmpty
                ? "native-setup-failed-without-reason"
                : model.revealSetupFailure
            setupCallbackResult = "failed:\(failure)"
            presentRequested = false
            recordFailure(
                checkpoint: "setup-callback-failed",
                reason: failure)
            return
        }
        guard gate.markUnityCaseReady(transactionID: transactionID),
              gate.markRevealStarted(transactionID: transactionID) else {
            setupCallbackResult = "rejected:native-setup-gate-rejected"
            recordFailure(
                checkpoint: "setup-callback-rejected",
                reason: "native-setup-gate-rejected")
            return
        }
        setupCallbackResult = "accepted"
        reportF2AfterAcceptedCallback()

        switch captureCheckpoint {
        case .sealed, .partial, .f0, .f1:
            recordFailure(
                checkpoint: "capture-checkpoint-failed",
                reason: "readiness-advanced-past-capture-checkpoint")
        case .f2:
            return
        case .f3:
            model.setNativeHybridPreviewProgress(
                requestID: transactionID,
                progress: GachaPackHandoffRules
                    .nativeHybridPackLipCrossingProgress)
        case .f4, nil:
            scheduleRevealStart(transactionID)
        }
    }

    private func reportF2AfterAcceptedCallback() {
        let trace = model.nativeHybridR030Trace
        guard !reportedF2AfterCallback,
              setupCallbackResult == "accepted",
              trace.checkpoint == "F2",
              trace.publishSetupPublished,
              trace.publishSetupSucceeded else {
            return
        }
        reportedF2AfterCallback = true
        reportLayer(checkpoint: "F2")
    }

    private func scheduleRevealStart(_ transactionID: UUID) {
        guard !revealStartScheduled else { return }
        revealStartScheduled = true
        DispatchQueue.main.asyncAfter(
            deadline: .now()
                + Double(GachaPackHandoffRules
                    .nativeHybridContainmentHoldNanoseconds)
                / 1_000_000_000
        ) {
            guard gate.transactionID == transactionID,
                  liveCaseApertureAvailable else {
                recordFailure(
                    checkpoint: "reveal-start-rejected",
                    reason: "live-case-aperture-not-authorized")
                return
            }
            beginPackDeparture(transactionID)
            model.startReveal(requestID: transactionID)
        }
    }

    private func handleUnityTrace(_ trace: GachaNativeHybridR030TraceState) {
        guard !trace.checkpoint.isEmpty else { return }
        guard let transactionID = gate.transactionID,
              trace.rawRequestUUID
                == transactionID.uuidString.lowercased() else {
            recordFailure(
                checkpoint: "trace-rejected",
                reason: "stale-r030-trace")
            return
        }

        switch trace.checkpoint {
        case "F0", "F1":
            reportLayer(checkpoint: trace.checkpoint)
        case "F2":
            reportF2AfterAcceptedCallback()
        case "F3":
            reportLayer(checkpoint: "F3")
        case "F4":
            pendingF4Trace = true
            reportF4AfterDeparture()
        default:
            recordFailure(
                checkpoint: "trace-rejected",
                reason: "unknown-r030-trace-checkpoint")
        }
    }

    private func handleUnityPhase(_ phase: String) {
        guard let transactionID = gate.transactionID,
              model.revealRequestID
                == transactionID.uuidString.lowercased() else {
            return
        }
        if phase == "case-crossing-pack-lip" {
            DispatchQueue.main.async {
                guard gate.transactionID == transactionID else { return }
                beginPackDeparture(transactionID)
            }
        } else if phase == "complete" {
            _ = gate.markRevealCompleted(requestID: model.revealRequestID)
            beginPackDeparture(transactionID)
            reportF4AfterDeparture()
        }
    }

    private func beginPackDeparture(_ transactionID: UUID) {
        guard gate.transactionID == transactionID,
              liveCaseApertureAvailable,
              packRetreatProgress < 1,
              captureCheckpoint != .f3 else {
            return
        }
        if reduceMotion || captureCheckpoint == .f4 {
            packRetreatProgress = 1
            packDeparted = true
            return
        }
        let departure = GachaPackHandoffRules
            .nativeHybridPackDepartureDurationSeconds
        withAnimation(.easeIn(duration: departure)) {
            packRetreatProgress = 1
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + departure) {
            guard gate.transactionID == transactionID else { return }
            packDeparted = true
        }
    }

    private func reportF4AfterDeparture() {
        guard pendingF4Trace,
              packRetreatProgress >= 1,
              packDeparted else {
            return
        }
        pendingF4Trace = false
        reportLayer(checkpoint: "F4")
    }

    private func recordFailure(checkpoint: String, reason: String) {
        diagnosticFailure = reason
        reportLayer(checkpoint: checkpoint, failure: reason)
    }

    private func reportLayer(
        checkpoint: String? = nil,
        failure: String? = nil
    ) {
        let trace = model.nativeHybridR030Trace
        let requestID = gate.transactionID?.uuidString.lowercased() ?? ""
        let rawRequestUUID = trace.rawRequestUUID.isEmpty
            ? requestID
            : trace.rawRequestUUID
        let receiptUUID = trace.receiptUUID.isEmpty
            ? model.receiptRequestID
            : trace.receiptUUID
        let resolvedFailure = failure
            ?? (!diagnosticFailure.isEmpty
                ? diagnosticFailure
                : trace.publishSetupFailure)
        reportLayerState(GachaNativeHybridR030LayerState(
            checkpoint: checkpoint ?? "layer-update",
            candidateSequenceStartedAtUnix: candidateSequenceStartedAtUnix,
            phase: gate.phase.rawValue,
            tearProgress: tearProgress,
            retreatProgress: effectiveRetreatProgress,
            rawRequestUUID: rawRequestUUID,
            receiptUUID: receiptUUID,
            stableFrameOrdinal: trace.stableFrameOrdinal,
            unityFrameCount: trace.unityFrameCount,
            cameraInstanceID: trace.cameraInstanceID,
            cameraName: trace.cameraName,
            caseRootName: trace.caseRootName,
            caseTypeName: trace.caseTypeName,
            caseEntityID: trace.caseEntityID,
            caseRendererCount: trace.caseRendererCount,
            foreignRendererCount: trace.foreignRendererCount,
            caseStableFrame: trace.caseStableFrame,
            cameraStableFrame: trace.cameraStableFrame,
            isolationActive: trace.isolationActive,
            usesCavityClearBackdrop: trace.usesCavityClearBackdrop,
            publishSetupPublished: trace.publishSetupPublished,
            publishSetupSucceeded: trace.publishSetupSucceeded,
            publishSetupFailure: resolvedFailure,
            callbackResult: setupCallbackResult,
            nativeUnityCaseReady: gate.unityCaseReady,
            apertureAuthorized: liveCaseApertureAvailable,
            packForeground: packIsForeground,
            nativeHybridProgress: trace.nativeHybridProgress,
            caseIsCanonical: trace.caseIsCanonical,
            caseIsOnlyUnityRenderable: trace.caseIsOnlyUnityRenderable))
    }
}

@MainActor
enum GachaNativeHybridR030Diagnostics {
    private static let traceFileName =
        "gacha-native-hybrid-r030-trace.ndjson"

    static func reset() {
        guard GachaNativeHybridR030Rules.isIsolatedCandidate,
              let documentsURL = documentsURL() else {
            return
        }
        try? FileManager.default.removeItem(
            at: documentsURL.appendingPathComponent(traceFileName))
    }

    static func capture(
        overlayView: UIView,
        state: GachaNativeHybridR030LayerState
    ) {
        record(state)
        // Pixel overlays exist for checkpoint runs only. In a full-sequence
        // run the 3x full-screen render + PNG encode on the main thread
        // starves the SwiftUI animation at commit, F1 and F2, so the lid
        // flight and the Pack retreat render at ~10 fps.
        guard GachaNativeHybridR030Rules.requestedCaptureCheckpoint != nil,
              overlayView.bounds.width > 1,
              overlayView.bounds.height > 1,
              let documentsURL = documentsURL() else {
            return
        }

        let scale = UIScreen.main.scale
        let width = Int((overlayView.bounds.width * scale).rounded(.up))
        let height = Int((overlayView.bounds.height * scale).rounded(.up))
        guard width > 1, height > 1 else { return }

        var pixels = [UInt8](repeating: 0, count: width * height * 4)
        let colorSpace = CGColorSpaceCreateDeviceRGB()
        let bitmapInfo = CGImageAlphaInfo.premultipliedLast.rawValue
            | CGBitmapInfo.byteOrder32Big.rawValue
        let image = pixels.withUnsafeMutableBytes { buffer -> UIImage? in
            guard let context = CGContext(
                data: buffer.baseAddress,
                width: width,
                height: height,
                bitsPerComponent: 8,
                bytesPerRow: width * 4,
                space: colorSpace,
                bitmapInfo: bitmapInfo) else {
                return nil
            }
            context.clear(CGRect(x: 0, y: 0, width: width, height: height))
            context.scaleBy(x: scale, y: scale)
            overlayView.layer.render(in: context)
            guard let cgImage = context.makeImage() else { return nil }
            return UIImage(cgImage: cgImage, scale: scale, orientation: .up)
        }
        guard let image else { return }

        let mouthBounds = mouthBounds(
            overlayBounds: overlayView.bounds,
            retreatProgress: state.retreatProgress)
        let protectedOuterBounds = protectedOuterBounds(
            overlayBounds: overlayView.bounds,
            retreatProgress: state.retreatProgress)
        let transparentMouthPixels = transparentPixelCount(
            in: mouthBounds,
            pixels: pixels,
            width: width,
            height: height,
            scale: scale)
        let protectedOuterMinimumAlpha = minimumAlpha(
            in: protectedOuterBounds,
            pixels: pixels,
            width: width,
            height: height,
            scale: scale)
        let name = safeCheckpointName(state.checkpoint)
        let pngURL = documentsURL.appendingPathComponent(
            "gacha-native-hybrid-r030-\(name)-overlay.png")
        let jsonURL = documentsURL.appendingPathComponent(
            "gacha-native-hybrid-r030-\(name)-overlay.json")
        try? image.pngData()?.write(to: pngURL, options: .atomic)
        let payload: [String: Any] = [
            "candidateRevision": "R030",
            "checkpoint": state.checkpoint,
            "tearProgress": state.tearProgress,
            "retreatProgress": state.retreatProgress,
            "hostIsOpaque": overlayView.isOpaque,
            "hostBackgroundAlpha": Double(
                overlayView.backgroundColor?.cgColor.alpha ?? 0),
            "overlayPixelWidth": width,
            "overlayPixelHeight": height,
            "overlayDisplayScale": Double(scale),
            "mouthBoundsPoints": [
                "x": Double(mouthBounds.minX),
                "y": Double(mouthBounds.minY),
                "width": Double(mouthBounds.width),
                "height": Double(mouthBounds.height)
            ],
            "transparentMouthPixels": transparentMouthPixels,
            "protectedOuterMinimumAlpha": protectedOuterMinimumAlpha,
            "apertureAlphaIsZero": !state.apertureAuthorized
                && transparentMouthPixels == 0,
            "apertureIsShapedAndBounded": state.apertureAuthorized
                && transparentMouthPixels > 300
                && protectedOuterMinimumAlpha >= 240,
            "rawRequestUUID": state.rawRequestUUID,
            "receiptUUID": state.receiptUUID,
            "stableFrameOrdinal": state.stableFrameOrdinal,
            "unityFrameCount": state.unityFrameCount,
            "cameraInstanceID": state.cameraInstanceID,
            "cameraName": state.cameraName,
            "caseRootName": state.caseRootName,
            "caseTypeName": state.caseTypeName,
            "caseEntityID": state.caseEntityID,
            "caseRendererCount": state.caseRendererCount,
            "foreignRendererCount": state.foreignRendererCount,
            "caseStableFrame": state.caseStableFrame,
            "cameraStableFrame": state.cameraStableFrame,
            "isolationActive": state.isolationActive,
            "usesCavityClearBackdrop": state.usesCavityClearBackdrop,
            "publishSetupPublished": state.publishSetupPublished,
            "publishSetupSucceeded": state.publishSetupSucceeded,
            "publishSetupFailure": state.publishSetupFailure,
            "callbackResult": state.callbackResult,
            "nativeUnityCaseReady": state.nativeUnityCaseReady,
            "apertureAuthorized": state.apertureAuthorized,
            "packForeground": state.packForeground,
            "nativeHybridProgress": state.nativeHybridProgress,
            "caseIsCanonical": state.caseIsCanonical,
            "caseIsOnlyUnityRenderable": state.caseIsOnlyUnityRenderable,
            "segmentedSealSelected": true,
            "overlayAlphaPath": pngURL.lastPathComponent
        ]
        writeJSON(payload, to: jsonURL)
    }

    private static func record(_ state: GachaNativeHybridR030LayerState) {
        guard let documentsURL = documentsURL() else { return }
        let payload: [String: Any] = [
            "recordedAtUnix": Date().timeIntervalSince1970,
            "candidateRevision": "R030",
            "checkpoint": state.checkpoint,
            "candidateSequenceStartedAtUnix":
                state.candidateSequenceStartedAtUnix,
            "phase": state.phase,
            "tearProgress": state.tearProgress,
            "retreatProgress": state.retreatProgress,
            "rawRequestUUID": state.rawRequestUUID,
            "receiptUUID": state.receiptUUID,
            "stableFrameOrdinal": state.stableFrameOrdinal,
            "unityFrameCount": state.unityFrameCount,
            "cameraInstanceID": state.cameraInstanceID,
            "cameraName": state.cameraName,
            "caseRootName": state.caseRootName,
            "caseTypeName": state.caseTypeName,
            "caseEntityID": state.caseEntityID,
            "caseRendererCount": state.caseRendererCount,
            "foreignRendererCount": state.foreignRendererCount,
            "caseStableFrame": state.caseStableFrame,
            "cameraStableFrame": state.cameraStableFrame,
            "isolationActive": state.isolationActive,
            "usesCavityClearBackdrop": state.usesCavityClearBackdrop,
            "publishSetupPublished": state.publishSetupPublished,
            "publishSetupSucceeded": state.publishSetupSucceeded,
            "publishSetupFailure": state.publishSetupFailure,
            "callbackResult": state.callbackResult,
            "nativeUnityCaseReady": state.nativeUnityCaseReady,
            "apertureAuthorized": state.apertureAuthorized,
            "packForeground": state.packForeground,
            "nativeHybridProgress": state.nativeHybridProgress,
            "caseIsCanonical": state.caseIsCanonical,
            "caseIsOnlyUnityRenderable": state.caseIsOnlyUnityRenderable,
            "segmentedSealSelected": true,
            "crossfadeEnabled": false
        ]
        guard var data = try? JSONSerialization.data(
            withJSONObject: payload,
            options: [.sortedKeys]) else {
            return
        }
        data.append(0x0A)
        let url = documentsURL.appendingPathComponent(traceFileName)
        if FileManager.default.fileExists(atPath: url.path) {
            guard let handle = try? FileHandle(forWritingTo: url) else {
                return
            }
            defer { try? handle.close() }
            _ = try? handle.seekToEnd()
            try? handle.write(contentsOf: data)
        } else {
            try? data.write(to: url, options: .atomic)
        }
    }

    private static func documentsURL() -> URL? {
        guard GachaNativeHybridR030Rules.isIsolatedCandidate else {
            return nil
        }
        return FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask).first
    }

    private static func writeJSON(_ payload: [String: Any], to url: URL) {
        guard let data = try? JSONSerialization.data(
            withJSONObject: payload,
            options: [.prettyPrinted, .sortedKeys]) else {
            return
        }
        try? data.write(to: url, options: .atomic)
    }

    private static func mouthBounds(
        overlayBounds: CGRect,
        retreatProgress: Double
    ) -> CGRect {
        let packWidth = CGFloat(GachaPackOpeningRules.artworkWidthPoints)
        let packHeight = CGFloat(GachaPackOpeningRules.artworkHeightPoints)
        let retreat = CGFloat(min(max(retreatProgress, 0), 1))
        let departureDistance = max(
            packHeight * 1.25,
            overlayBounds.height * 0.72)
        let packFrame = CGRect(
            x: (overlayBounds.width - packWidth) * 0.5,
            y: (overlayBounds.height - packHeight) * 0.5
                + departureDistance * retreat,
            width: packWidth,
            height: packHeight)
        let seamY = packFrame.minY + packHeight * CGFloat(
            GachaPackOpeningRules.authoredSeamYFraction)
        return CGRect(
            x: packFrame.minX + packWidth * CGFloat(
                GachaPackOpeningRules.openingInsetFraction),
            y: seamY - 4,
            width: packWidth * CGFloat(
                1 - GachaPackOpeningRules.openingInsetFraction * 2),
            height: CGFloat(
                GachaPackOpeningRules.maximumOpeningHeightPoints) + 10)
    }

    private static func protectedOuterBounds(
        overlayBounds: CGRect,
        retreatProgress: Double
    ) -> CGRect {
        let packWidth = CGFloat(GachaPackOpeningRules.artworkWidthPoints)
        let packHeight = CGFloat(GachaPackOpeningRules.artworkHeightPoints)
        let retreat = CGFloat(min(max(retreatProgress, 0), 1))
        let departureDistance = max(
            packHeight * 1.25,
            overlayBounds.height * 0.72)
        let packFrame = CGRect(
            x: (overlayBounds.width - packWidth) * 0.5,
            y: (overlayBounds.height - packHeight) * 0.5
                + departureDistance * retreat,
            width: packWidth,
            height: packHeight)
        return CGRect(
            x: packFrame.midX - packWidth * 0.20,
            y: packFrame.minY + packHeight * 0.42,
            width: packWidth * 0.40,
            height: packHeight * 0.30)
    }

    private static func transparentPixelCount(
        in bounds: CGRect,
        pixels: [UInt8],
        width: Int,
        height: Int,
        scale: CGFloat
    ) -> Int {
        let clipped = bounds.intersection(CGRect(
            x: 0,
            y: 0,
            width: CGFloat(width) / scale,
            height: CGFloat(height) / scale))
        guard !clipped.isNull else { return 0 }
        let xStart = max(0, Int((clipped.minX * scale).rounded(.down)))
        let xEnd = min(width, Int((clipped.maxX * scale).rounded(.up)))
        let yStart = max(0, Int((clipped.minY * scale).rounded(.down)))
        let yEnd = min(height, Int((clipped.maxY * scale).rounded(.up)))
        var count = 0
        for y in yStart..<yEnd {
            for x in xStart..<xEnd {
                if pixels[(y * width + x) * 4 + 3] <= 8 {
                    count += 1
                }
            }
        }
        return count
    }

    private static func minimumAlpha(
        in bounds: CGRect,
        pixels: [UInt8],
        width: Int,
        height: Int,
        scale: CGFloat
    ) -> Int {
        let clipped = bounds.intersection(CGRect(
            x: 0,
            y: 0,
            width: CGFloat(width) / scale,
            height: CGFloat(height) / scale))
        guard !clipped.isNull else { return 0 }
        let xStart = max(0, Int((clipped.minX * scale).rounded(.down)))
        let xEnd = min(width, Int((clipped.maxX * scale).rounded(.up)))
        let yStart = max(0, Int((clipped.minY * scale).rounded(.down)))
        let yEnd = min(height, Int((clipped.maxY * scale).rounded(.up)))
        var minimum = 255
        for y in yStart..<yEnd {
            for x in xStart..<xEnd {
                minimum = min(minimum, Int(pixels[(y * width + x) * 4 + 3]))
            }
        }
        return minimum
    }

    private static func safeCheckpointName(_ checkpoint: String) -> String {
        checkpoint.isEmpty
            ? "state"
            : checkpoint
                .replacingOccurrences(of: "/", with: "-")
                .replacingOccurrences(of: " ", with: "-")
    }
}
