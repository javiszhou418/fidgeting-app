import Foundation
import SwiftUI
import UIKit

struct GachaNativeHybridR029LayerState: Equatable {
    let checkpoint: String
    let candidateSequenceStartedAtUnix: Double
    let phase: String
    let tearProgress: Double
    let retreatProgress: Double
    let rawRequestUUID: String
    let receiptUUID: String
    let unityFrameCount: Int
    let caseRootName: String
    let caseTypeName: String
    let caseEntityID: String
    let caseRendererCount: Int
    let foreignRendererCount: Int
    let caseStableFrame: Bool
    let cameraStableFrame: Bool
    let setupSucceeded: Bool
    let revealSetupFailure: String
    let nativeUnityCaseReady: Bool
    let apertureAuthorized: Bool
    let packForeground: Bool
    let nativeHybridProgress: Double
    let caseIsCanonical: Bool
    let caseIsOnlyUnityRenderable: Bool
    let unityClearBackdropIsolated: Bool
}

/// Isolated R029 proof that uses the production Unity bridge and its real
/// two-EndOfFrame readiness coroutine. This candidate owns no case pixels.
struct GachaNativeHybridR029CandidateView: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @ObservedObject private var model = GachaStoreModel.shared

    let reportLayerState: (GachaNativeHybridR029LayerState) -> Void

    @State private var gate = GachaSingleDrawGateState()
    @State private var tearProgress = 0.0
    @State private var packRetreatProgress = 0.0
    @State private var sequenceStarted = false
    @State private var presentRequested = false
    @State private var revealStartScheduled = false
    @State private var diagnosticFailure = ""
    @State private var candidateSequenceStartedAtUnix = 0.0

    init(
        reportLayerState: @escaping (GachaNativeHybridR029LayerState) -> Void
    ) {
        self.reportLayerState = reportLayerState
    }

    private var captureCheckpoint: GachaNativeHybridR029CaptureCheckpoint? {
        GachaNativeHybridR029Rules.requestedCaptureCheckpoint
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

    private var packIsForeground: Bool {
        GachaPackHandoffRules.packArtIsForeground(
            packVisible: gate.phase != .complete,
            retreatProgress: packRetreatProgress)
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
                    retreatProgress: effectiveRetreatProgress)
            }
        }
        .productDesignSystem()
        .accessibilityIdentifier("gacha-native-hybrid-r029-pack")
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
        .onChange(of: model.nativeHybridR029Trace) { trace in
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
        }
        .onDisappear {
            guard let transactionID = gate.transactionID else { return }
            model.interruptReveal(requestID: transactionID)
        }
    }

    private func startCandidate() {
        GachaNativeHybridR029Diagnostics.reset()
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
            previewToken: GachaNativeHybridR029Rules.previewToken)
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
        model.draw(
            requestID: transactionID,
            seriesId: seriesID,
            count: 1,
            useCoins: false)
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
        model.configureR029CaptureCheckpoint(
            requestID: transactionID,
            checkpoint: captureCheckpoint)
        model.presentR029NativeHybridReveal(requestID: transactionID)
    }

    private func handleUnitySetup() {
        guard let transactionID = gate.transactionID,
              model.revealRequestID
                == transactionID.uuidString.lowercased() else {
            recordFailure(
                checkpoint: "setup-callback-rejected",
                reason: "stale-setup-callback")
            return
        }
        guard model.revealSetupSucceeded else {
            presentRequested = false
            recordFailure(
                checkpoint: "setup-callback-failed",
                reason: model.revealSetupFailure.isEmpty
                    ? "native-setup-failed-without-reason"
                    : model.revealSetupFailure)
            return
        }
        guard gate.markUnityCaseReady(transactionID: transactionID),
              gate.markRevealStarted(transactionID: transactionID) else {
            recordFailure(
                checkpoint: "setup-callback-rejected",
                reason: "native-setup-gate-rejected")
            return
        }
        reportLayer(checkpoint: "F2")

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
            model.startReveal(requestID: transactionID)
        }
    }

    private func handleUnityTrace(_ trace: GachaNativeHybridR029TraceState) {
        guard !trace.checkpoint.isEmpty else { return }
        guard let transactionID = gate.transactionID,
              trace.rawRequestUUID
                == transactionID.uuidString.lowercased() else {
            recordFailure(
                checkpoint: "trace-rejected",
                reason: "stale-r029-trace")
            return
        }

        switch trace.checkpoint {
        case "F0", "F1":
            reportLayer(checkpoint: trace.checkpoint)
        case "F2":
            if gate.unityCaseReady {
                reportLayer(checkpoint: "F2")
            } else {
                reportLayer(checkpoint: "F2-unity-published")
            }
        case "F3":
            reportLayer(checkpoint: "F3")
        case "F4":
            reportLayer(checkpoint: "F4")
        default:
            recordFailure(
                checkpoint: "trace-rejected",
                reason: "unknown-r029-trace-checkpoint")
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
            return
        }
        withAnimation(.linear(
            duration: GachaPackHandoffRules
                .nativeHybridPackDepartureDurationSeconds)) {
            packRetreatProgress = 1
        }
    }

    private func recordFailure(checkpoint: String, reason: String) {
        diagnosticFailure = reason
        reportLayer(checkpoint: checkpoint, failure: reason)
    }

    private func reportLayer(
        checkpoint: String? = nil,
        failure: String? = nil
    ) {
        let trace = model.nativeHybridR029Trace
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
                : model.revealSetupFailure)
        reportLayerState(GachaNativeHybridR029LayerState(
            checkpoint: checkpoint ?? "layer-update",
            candidateSequenceStartedAtUnix: candidateSequenceStartedAtUnix,
            phase: gate.phase.rawValue,
            tearProgress: tearProgress,
            retreatProgress: effectiveRetreatProgress,
            rawRequestUUID: rawRequestUUID,
            receiptUUID: receiptUUID,
            unityFrameCount: trace.unityFrameCount,
            caseRootName: trace.caseRootName,
            caseTypeName: trace.caseTypeName,
            caseEntityID: trace.caseEntityID,
            caseRendererCount: trace.caseRendererCount,
            foreignRendererCount: trace.foreignRendererCount,
            caseStableFrame: trace.caseStableFrame,
            cameraStableFrame: trace.cameraStableFrame,
            setupSucceeded: trace.setupSucceeded,
            revealSetupFailure: resolvedFailure,
            nativeUnityCaseReady: gate.unityCaseReady,
            apertureAuthorized: liveCaseApertureAvailable,
            packForeground: packIsForeground,
            nativeHybridProgress: trace.nativeHybridProgress,
            caseIsCanonical: trace.caseIsCanonical,
            caseIsOnlyUnityRenderable: trace.caseIsOnlyUnityRenderable,
            unityClearBackdropIsolated: trace.unityClearBackdropIsolated))
    }
}

@MainActor
enum GachaNativeHybridR029Diagnostics {
    private static let traceFileName =
        "gacha-native-hybrid-r029-trace.ndjson"

    static func reset() {
        guard GachaNativeHybridR029Rules.isIsolatedCandidate,
              let documentsURL = documentsURL() else {
            return
        }
        try? FileManager.default.removeItem(
            at: documentsURL.appendingPathComponent(traceFileName))
    }

    static func capture(
        overlayView: UIView,
        state: GachaNativeHybridR029LayerState
    ) {
        record(state)
        guard overlayView.bounds.width > 1,
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
            "gacha-native-hybrid-r029-\(name)-overlay.png")
        let jsonURL = documentsURL.appendingPathComponent(
            "gacha-native-hybrid-r029-\(name)-overlay.json")
        try? image.pngData()?.write(to: pngURL, options: .atomic)
        let payload: [String: Any] = [
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
            "unityFrameCount": state.unityFrameCount,
            "caseRootName": state.caseRootName,
            "caseEntityID": state.caseEntityID,
            "caseStableFrame": state.caseStableFrame,
            "cameraStableFrame": state.cameraStableFrame,
            "setupSucceeded": state.setupSucceeded,
            "revealSetupFailure": state.revealSetupFailure,
            "nativeUnityCaseReady": state.nativeUnityCaseReady,
            "apertureAuthorized": state.apertureAuthorized,
            "packForeground": state.packForeground,
            "nativeHybridProgress": state.nativeHybridProgress,
            "foreignRendererCount": state.foreignRendererCount,
            "caseIsCanonical": state.caseIsCanonical,
            "caseIsOnlyUnityRenderable": state.caseIsOnlyUnityRenderable,
            "unityClearBackdropIsolated": state.unityClearBackdropIsolated,
            "overlayAlphaPath": pngURL.lastPathComponent
        ]
        writeJSON(payload, to: jsonURL)
    }

    private static func record(_ state: GachaNativeHybridR029LayerState) {
        guard let documentsURL = documentsURL() else { return }
        let payload: [String: Any] = [
            "recordedAtUnix": Date().timeIntervalSince1970,
            "checkpoint": state.checkpoint,
            "candidateSequenceStartedAtUnix":
                state.candidateSequenceStartedAtUnix,
            "phase": state.phase,
            "tearProgress": state.tearProgress,
            "retreatProgress": state.retreatProgress,
            "rawRequestUUID": state.rawRequestUUID,
            "receiptUUID": state.receiptUUID,
            "unityFrameCount": state.unityFrameCount,
            "caseRootName": state.caseRootName,
            "caseTypeName": state.caseTypeName,
            "caseEntityID": state.caseEntityID,
            "caseRendererCount": state.caseRendererCount,
            "foreignRendererCount": state.foreignRendererCount,
            "caseStableFrame": state.caseStableFrame,
            "cameraStableFrame": state.cameraStableFrame,
            "setupSucceeded": state.setupSucceeded,
            "revealSetupFailure": state.revealSetupFailure,
            "nativeUnityCaseReady": state.nativeUnityCaseReady,
            "apertureAuthorized": state.apertureAuthorized,
            "packForeground": state.packForeground,
            "nativeHybridProgress": state.nativeHybridProgress,
            "caseIsCanonical": state.caseIsCanonical,
            "caseIsOnlyUnityRenderable": state.caseIsOnlyUnityRenderable,
            "unityClearBackdropIsolated": state.unityClearBackdropIsolated,
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
        guard GachaNativeHybridR029Rules.isIsolatedCandidate else {
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
