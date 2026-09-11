import Foundation
import SwiftUI
import UIKit

struct GachaNativeHybridR028LayerState: Equatable {
    let stage: String
    let tearProgress: Double
    let hasAuthoritativeReceipt: Bool
    let hasStableUnityCase: Bool
    let apertureAuthorized: Bool
    let retreatProgress: Double
    let composition: GachaRevealCompositionState
}

/// Simulator-only proof of an opaque Pack above a camera-isolated live case.
///
/// Static proof stages prepare the same authoritative case before visual tearing
/// begins. Their aperture hold keeps the native Pack cavity opaque until the
/// normal receipt-and-two-frame readiness gate would authorize the cutout.
struct GachaNativeHybridR028CandidateView: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @ObservedObject private var model = GachaStoreModel.shared

    let reportLayerState: (GachaNativeHybridR028LayerState) -> Void

    @State private var gate = GachaSingleDrawGateState()
    @State private var tearProgress = 0.0
    @State private var packRetreatProgress = 0.0
    @State private var sequenceStarted = false
    @State private var presentRequested = false

    init(
        reportLayerState: @escaping (GachaNativeHybridR028LayerState) -> Void
    ) {
        self.reportLayerState = reportLayerState
    }

    private var staticStage: GachaNativeHybridR028StaticStage? {
        GachaNativeHybridR028Rules.requestedStaticStage
    }

    private var activeSeries: GachaSeriesInfo? {
        model.series.first
    }

    private var holdsApertureClosed: Bool {
        staticStage?.holdsApertureClosed ?? false
    }

    private var liveCaseApertureAvailable: Bool {
        guard !holdsApertureClosed else { return false }
        return GachaPackHandoffRules.canRevealLiveCase(
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
        .accessibilityIdentifier("gacha-native-hybrid-r028-pack")
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
        .onChange(of: model.revealComposition) { _ in
            reportLayer()
        }
        .onChange(of: tearProgress) { _ in
            reportLayer()
        }
        .onChange(of: packRetreatProgress) { _ in
            reportLayer()
        }
        .onDisappear {
            guard let transactionID = gate.transactionID else { return }
            model.setNativeHybridApertureHold(
                requestID: transactionID,
                hold: false)
            model.interruptReveal(requestID: transactionID)
        }
    }

    private func startCandidate() {
        model.beginNativeHybridCandidate(
            previewToken: GachaNativeHybridR028Rules.previewToken)
    }

    private func beginRequestIfPossible() {
        guard !sequenceStarted,
              let series = activeSeries else {
            return
        }
        sequenceStarted = true
        let transactionID = UUID()
        guard gate.begin(transactionID: transactionID),
              gate.markSelectionFinished(transactionID: transactionID) else {
            return
        }

        if staticStage != nil {
            stageRealCaseBeforeStaticTear(
                transactionID: transactionID,
                seriesID: series.id)
            return
        }
        animateTear(
            transactionID: transactionID,
            seriesID: series.id)
    }

    private func stageRealCaseBeforeStaticTear(
        transactionID: UUID,
        seriesID: String
    ) {
        guard gate.markPackCommitted(transactionID: transactionID) else {
            return
        }
        model.draw(
            requestID: transactionID,
            seriesId: seriesID,
            count: 1,
            useCoins: false)
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
        if holdsApertureClosed {
            model.setNativeHybridApertureHold(
                requestID: transactionID,
                hold: true)
        }
        model.presentR028NativeHybridReveal(requestID: transactionID)
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
        case .packDeparted:
            model.setNativeHybridPreviewProgress(
                requestID: transactionID,
                progress: 1)
            packRetreatProgress = 1
            return
        case .sealed, .partial, .preReadyMouth:
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
                  liveCaseApertureAvailable else {
                return
            }
            model.startReveal(requestID: transactionID)
        }
    }

    private func handleUnityPhase(_ phase: String) {
        guard let transactionID = gate.transactionID,
              model.revealRequestID
                == transactionID.uuidString.lowercased() else {
            return
        }
        if phase == "native-hybrid-case-staged" {
            stageStaticFrameIfNeeded()
            return
        }
        guard staticStage == nil else { return }

        if phase == "case-crossing-pack-lip" {
            beginPackDeparture(transactionID)
        } else if phase == "complete" {
            _ = gate.markRevealCompleted(requestID: model.revealRequestID)
            beginPackDeparture(transactionID)
        }
    }

    private func stageStaticFrameIfNeeded() {
        guard let staticStage else { return }
        switch staticStage {
        case .sealed:
            tearProgress = 0
        case .partial:
            tearProgress = 0.31
        case .preReadyMouth, .containedCase, .caseCrossing, .packDeparted:
            tearProgress = GachaPackOpeningRules.tearCommitProgress
        }
        reportLayer()
    }

    private func beginPackDeparture(_ transactionID: UUID) {
        guard gate.transactionID == transactionID,
              liveCaseApertureAvailable,
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
        reportLayerState(GachaNativeHybridR028LayerState(
            stage: staticStage?.rawValue ?? "normal",
            tearProgress: tearProgress,
            hasAuthoritativeReceipt: gate.receiptArrived,
            hasStableUnityCase: gate.unityCaseReady,
            apertureAuthorized: liveCaseApertureAvailable,
            retreatProgress: effectiveRetreatProgress,
            composition: model.revealComposition))
    }
}

@MainActor
enum GachaNativeHybridR028OverlayDiagnostics {
    static func capture(
        overlayView: UIView,
        state: GachaNativeHybridR028LayerState
    ) {
        guard GachaNativeHybridR028Rules.isIsolatedCandidate,
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
        let mouthBounds = CGRect(
            x: packFrame.minX
                + packWidth * CGFloat(
                    GachaPackOpeningRules.openingInsetFraction),
            y: seamY - 4,
            width: packWidth * CGFloat(
                1 - GachaPackOpeningRules.openingInsetFraction * 2),
            height: CGFloat(
                GachaPackOpeningRules.maximumOpeningHeightPoints) + 10)
        let protectedOuterBounds = CGRect(
            x: packFrame.midX - packWidth * 0.20,
            y: packFrame.minY + packHeight * 0.42,
            width: packWidth * 0.40,
            height: packHeight * 0.30)
        let transparentMouthPixels = transparentPixelCount(
            in: mouthBounds,
            pixels: pixels,
            width: width,
            height: height,
            scale: scale)
        let transparentOutsideMouthPixels = transparentPixelCount(
            in: packFrame,
            excluding: mouthBounds,
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
        let stage = state.stage.replacingOccurrences(
            of: "/",
            with: "-")
        let pngURL = documentsURL.appendingPathComponent(
            "gacha-native-hybrid-r028-\(stage)-overlay.png")
        let jsonURL = documentsURL.appendingPathComponent(
            "gacha-native-hybrid-r028-\(stage)-overlay.json")
        try? image.pngData()?.write(to: pngURL, options: .atomic)

        let payload: [String: Any] = [
            "stage": state.stage,
            "tearProgress": state.tearProgress,
            "hasAuthoritativeReceipt": state.hasAuthoritativeReceipt,
            "hasStableUnityCase": state.hasStableUnityCase,
            "apertureAuthorized": state.apertureAuthorized,
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
            "transparentOutsideMouthPixels": transparentOutsideMouthPixels,
            "protectedOuterMinimumAlpha": protectedOuterMinimumAlpha,
            "apertureAlphaIsZero": !state.apertureAuthorized
                && transparentMouthPixels == 0,
            "apertureIsShapedAndBounded": state.apertureAuthorized
                && transparentMouthPixels > 300
                && protectedOuterMinimumAlpha >= 240,
            "caseRootName": state.composition.caseRootName,
            "caseTypeName": state.composition.caseTypeName,
            "caseEntityID": state.composition.caseEntityID,
            "caseRendererCount": state.composition.caseRendererCount,
            "caseIsCanonical": state.composition.caseIsCanonical,
            "caseIsOnlyUnityRenderable": state.composition
                .caseIsOnlyUnityRenderable,
            "unityClearBackdropIsolated": state.composition
                .unityClearBackdropIsolated,
            "overlayAlphaPath": pngURL.lastPathComponent
        ]
        guard let data = try? JSONSerialization.data(
            withJSONObject: payload,
            options: [.prettyPrinted, .sortedKeys]) else {
            return
        }
        try? data.write(to: jsonURL, options: .atomic)
    }

    private static func transparentPixelCount(
        in bounds: CGRect,
        excluding excluded: CGRect? = nil,
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
                let point = CGPoint(
                    x: CGFloat(x) / scale,
                    y: CGFloat(y) / scale)
                guard excluded?.contains(point) != true,
                      pixels[(y * width + x) * 4 + 3] <= 8 else {
                    continue
                }
                count += 1
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
}
