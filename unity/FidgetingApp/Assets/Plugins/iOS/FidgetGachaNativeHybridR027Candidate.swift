import Foundation
import SwiftUI
import UIKit

struct GachaNativeHybridR027LayerState: Equatable {
    let stage: String
    let tearProgress: Double
    let hasAuthoritativeReceipt: Bool
    let hasStableUnityCase: Bool
    let retreatProgress: Double
}

/// Simulator-only proof of a transparent Pack above the production Unity view.
///
/// The view owns no case art. Unity creates one assembled case after the
/// authoritative receipt and reports readiness only after two rendered frames.
struct GachaNativeHybridR027CandidateView: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @ObservedObject private var model = GachaStoreModel.shared

    let reportLayerState: (GachaNativeHybridR027LayerState) -> Void

    @State private var gate = GachaSingleDrawGateState()
    @State private var tearProgress = 0.0
    @State private var packRetreatProgress = 0.0
    @State private var sequenceStarted = false
    @State private var presentRequested = false

    init(
        reportLayerState: @escaping (GachaNativeHybridR027LayerState) -> Void
    ) {
        self.reportLayerState = reportLayerState
    }

    private var staticStage: GachaNativeHybridR027StaticStage? {
        GachaNativeHybridR027Rules.requestedStaticStage
    }

    private var activeSeries: GachaSeriesInfo? {
        model.series.first
    }

    private var liveCaseApertureAvailable: Bool {
        gate.allowsLiveCaseAperture
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
        .accessibilityIdentifier("gacha-native-hybrid-r027-pack")
        .onAppear {
            startCandidate()
            reportLayer()
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
        .onChange(of: model.revealSetupSucceeded) { succeeded in
            handleUnitySetup(succeeded)
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
        model.beginNativeHybridCandidate(
            previewToken: GachaNativeHybridR027Rules.previewToken)
        guard staticStage != .sealed else { return }
        beginRequestIfPossible()
    }

    private func beginRequestIfPossible() {
        guard !sequenceStarted,
              staticStage != .sealed,
              let series = activeSeries else {
            return
        }
        sequenceStarted = true
        let transactionID = UUID()
        guard gate.begin(transactionID: transactionID),
              gate.markSelectionFinished(transactionID: transactionID) else {
            return
        }

        switch staticStage {
        case .partial:
            tearProgress = 0.31
        case .emptyMouth:
            tearProgress = GachaPackOpeningRules.tearCommitProgress
        case .containedCase, .caseCrossing:
            tearProgress = GachaPackOpeningRules.tearCommitProgress
            commitPack(transactionID: transactionID, seriesID: series.id)
        case .sealed:
            break
        case nil:
            animateTear(
                transactionID: transactionID,
                seriesID: series.id)
        }
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

        Task { @MainActor in
            try? await Task.sleep(nanoseconds:
                GachaPackHandoffRules.nativeHybridTearLeadInNanoseconds)
            guard gate.transactionID == transactionID,
                  gate.phase == .tearPack else {
                return
            }
            withAnimation(.linear(
                duration: GachaPackHandoffRules
                    .nativeHybridTearDurationSeconds)) {
                tearProgress = GachaPackOpeningRules.tearCommitProgress
            }
            try? await Task.sleep(nanoseconds: UInt64(
                (GachaPackHandoffRules.nativeHybridTearDurationSeconds + 0.02)
                    * 1_000_000_000))
            guard gate.transactionID == transactionID,
                  gate.phase == .tearPack else {
                return
            }
            commitPack(transactionID: transactionID, seriesID: seriesID)
        }
    }

    private func commitPack(
        transactionID: UUID,
        seriesID: String
    ) {
        guard gate.transactionID == transactionID,
              gate.markPackCommitted(transactionID: transactionID) else {
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
        model.presentReveal(
            requestID: transactionID,
            nativeHybridCandidate: true)
    }

    private func handleUnitySetup(_ succeeded: Bool) {
        guard let transactionID = gate.transactionID,
              model.revealRequestID
                == transactionID.uuidString.lowercased(),
              succeeded,
              gate.markUnityCaseReady(transactionID: transactionID),
              gate.markRevealStarted(transactionID: transactionID) else {
            return
        }
        reportLayer()

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
        case nil:
            break
        }

        if reduceMotion {
            beginPackDeparture(transactionID)
            model.startReveal(requestID: transactionID)
            return
        }

        Task { @MainActor in
            try? await Task.sleep(nanoseconds:
                GachaPackHandoffRules.nativeHybridContainmentHoldNanoseconds)
            guard gate.transactionID == transactionID,
                  gate.allowsLiveCaseAperture else {
                return
            }
            model.startReveal(requestID: transactionID)
        }
    }

    private func handleUnityPhase(_ phase: String) {
        guard let transactionID = gate.transactionID,
              model.revealRequestID
                == transactionID.uuidString.lowercased(),
              staticStage == nil else {
            return
        }

        if phase == "case-crossing-pack-lip" {
            beginPackDeparture(transactionID)
        } else if phase == "complete" {
            _ = gate.markRevealCompleted(requestID: model.revealRequestID)
            beginPackDeparture(transactionID)
        }
    }

    private func beginPackDeparture(_ transactionID: UUID) {
        guard gate.transactionID == transactionID,
              gate.allowsLiveCaseAperture,
              packRetreatProgress < 1 else {
            return
        }
        if reduceMotion {
            packRetreatProgress = 1
            return
        }
        withAnimation(.linear(
            duration: GachaPackHandoffRules
                .nativeHybridPackDepartureDurationSeconds)) {
            packRetreatProgress = 1
        }
    }

    private func reportLayer() {
        reportLayerState(GachaNativeHybridR027LayerState(
            stage: staticStage?.rawValue ?? "normal",
            tearProgress: tearProgress,
            hasAuthoritativeReceipt: gate.receiptArrived,
            hasStableUnityCase: gate.unityCaseReady,
            retreatProgress: effectiveRetreatProgress))
    }
}

@MainActor
enum GachaNativeHybridR027OverlayDiagnostics {
    static func capture(
        overlayView: UIView,
        state: GachaNativeHybridR027LayerState
    ) {
        guard GachaNativeHybridR027Rules.isIsolatedCandidate,
              overlayView.bounds.width > 1,
              overlayView.bounds.height > 1,
              let documentsURL = FileManager.default.urls(
                for: .documentDirectory,
                in: .userDomainMask).first else {
            return
        }

        let scale = UIScreen.main.scale
        let width = Int((overlayView.bounds.width * scale).rounded(.up))
        let height = Int((overlayView.bounds.height * scale).rounded(.up))
        guard width > 1, height > 1 else { return }

        var pixels = [UInt8](
            repeating: 0,
            count: width * height * 4)
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

        let packWidth = CGFloat(GachaPackOpeningRules.artworkWidthPoints)
        let packHeight = CGFloat(GachaPackOpeningRules.artworkHeightPoints)
        let retreat = CGFloat(min(max(state.retreatProgress, 0), 1))
        let departureDistance = max(
            packHeight * 1.25,
            overlayView.bounds.height * 0.72)
        let packFrame = CGRect(
            x: (overlayView.bounds.width - packWidth) * 0.5,
            y: (overlayView.bounds.height - packHeight) * 0.5
                + departureDistance * retreat,
            width: packWidth,
            height: packHeight)
        let seamY = packFrame.minY + packHeight * CGFloat(
            GachaPackOpeningRules.authoredSeamYFraction)
        let mouthProbe = CGPoint(
            x: packFrame.midX,
            y: seamY + 14)
        let frontLipProbe = CGPoint(
            x: packFrame.midX,
            y: seamY + CGFloat(
                GachaPackOpeningRules.maximumOpeningHeightPoints) + 6)
        let mouthAlpha = alpha(
            at: mouthProbe,
            pixels: pixels,
            width: width,
            height: height,
            scale: scale)
        let frontLipAlpha = alpha(
            at: frontLipProbe,
            pixels: pixels,
            width: width,
            height: height,
            scale: scale)
        let stage = state.stage.replacingOccurrences(
            of: "/",
            with: "-")
        let pngURL = documentsURL.appendingPathComponent(
            "gacha-native-hybrid-r027-\(stage)-overlay.png")
        let jsonURL = documentsURL.appendingPathComponent(
            "gacha-native-hybrid-r027-\(stage)-overlay.json")
        try? image.pngData()?.write(to: pngURL, options: .atomic)

        let payload: [String: Any] = [
            "stage": state.stage,
            "tearProgress": state.tearProgress,
            "hasAuthoritativeReceipt": state.hasAuthoritativeReceipt,
            "hasStableUnityCase": state.hasStableUnityCase,
            "retreatProgress": state.retreatProgress,
            "hostIsOpaque": overlayView.isOpaque,
            "hostBackgroundAlpha": Double(
                overlayView.backgroundColor?.cgColor.alpha ?? 0),
            "mouthAlpha": mouthAlpha,
            "frontLipAlpha": frontLipAlpha,
            "mouthCutoutPasses": state.tearProgress
                < GachaPackOpeningRules.tearCommitProgress
                || mouthAlpha <= 8,
            "frontLipRemainsOpaque": state.tearProgress
                < GachaPackOpeningRules.tearCommitProgress
                || frontLipAlpha >= 180,
            "overlayAlphaPath": pngURL.lastPathComponent
        ]
        guard let data = try? JSONSerialization.data(
            withJSONObject: payload,
            options: [.prettyPrinted, .sortedKeys]) else {
            return
        }
        try? data.write(to: jsonURL, options: .atomic)
    }

    private static func alpha(
        at point: CGPoint,
        pixels: [UInt8],
        width: Int,
        height: Int,
        scale: CGFloat
    ) -> Int {
        let x = min(max(Int((point.x * scale).rounded()), 0), width - 1)
        let y = min(max(Int((point.y * scale).rounded()), 0), height - 1)
        return Int(pixels[(y * width + x) * 4 + 3])
    }
}
