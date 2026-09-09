import Foundation
import SwiftUI
import Combine

// MARK: - Unity bridge (send)

@_silgen_name("UnitySendMessage")
private func GachaUnitySendMessage(
    _ objectName: UnsafePointer<CChar>,
    _ methodName: UnsafePointer<CChar>,
    _ message: UnsafePointer<CChar>)

enum GachaUnityBridge {
    static func send(_ method: String, value: String = "") {
        "FidgetApp".withCString { objectName in
            method.withCString { methodName in
                value.withCString { message in
                    GachaUnitySendMessage(objectName, methodName, message)
                }
            }
        }
    }
}

// MARK: - Model

public enum GachaRarityTier: Int, CaseIterable {
    case standard = 0
    case refined = 1
    case signature = 2
    case heirloom = 3

    var title: String {
        switch self {
        case .standard: return "标准"
        case .refined: return "精制"
        case .signature: return "臻藏"
        case .heirloom: return "传世"
        }
    }

    /// Lining-language colors mirroring GachaRevealRules.
    var tint: Color {
        switch self {
        case .standard: return Color(red: 0.55, green: 0.55, blue: 0.58)
        case .refined: return Color(red: 0.45, green: 0.62, blue: 0.85)
        case .signature: return Color(red: 0.85, green: 0.55, blue: 0.30)
        case .heirloom: return Color(red: 0.55, green: 0.90, blue: 0.95)
        }
    }

    /// Display mirror of GachaEconomyRules.RedeemShardCost; Unity enforces.
    var redeemCost: Int? {
        switch self {
        case .standard: return 4
        case .refined: return 12
        case .signature: return 60
        case .heirloom: return nil
        }
    }
}

public struct GachaSeriesInfo: Equatable {
    public let id: String
    public let name: String
    public let rates: [Double]
}

public struct GachaPrizeInfo: Equatable, Identifiable {
    public let id: String
    public let seriesId: String
    public let rarity: GachaRarityTier
    public let kindIndex: Int
    public let name: String

    var kindTitle: String {
        switch kindIndex {
        case 1: return "贴纸"
        case 2: return "展示底座"
        case 3: return "环境色调"
        case 4: return "指尖玩具"
        default: return "限定皮肤"
        }
    }
}

public struct GachaReceiptRow: Equatable, Identifiable {
    public let id = UUID()
    public let prizeId: String
    public let name: String
    public let rarity: GachaRarityTier
    public let isNew: Bool
    public let shardsGained: Int
    public let forcedBySignaturePity: Bool
    public let forcedByHeirloomPity: Bool
    public let forcedByTenDraw: Bool
    public let firstObtainedAtUtc: String
    public let collectibleId: String
}

public struct GachaRevealCompositionState: Equatable {
    public static let empty = GachaRevealCompositionState(
        caseRootName: "",
        caseTypeName: "",
        caseEntityID: "",
        caseRendererCount: 0,
        caseIsCanonical: false,
        caseIsOnlyUnityRenderable: false,
        unityClearBackdropIsolated: false)

    public let caseRootName: String
    public let caseTypeName: String
    public let caseEntityID: String
    public let caseRendererCount: Int
    public let caseIsCanonical: Bool
    public let caseIsOnlyUnityRenderable: Bool
    public let unityClearBackdropIsolated: Bool
}

public struct GachaNativeHybridR029TraceState: Equatable {
    public static let empty = GachaNativeHybridR029TraceState(
        checkpoint: "",
        rawRequestUUID: "",
        receiptUUID: "",
        unityFrameCount: -1,
        caseRootName: "",
        caseTypeName: "",
        caseEntityID: "",
        caseRendererCount: 0,
        foreignRendererCount: -1,
        caseStableFrame: false,
        cameraStableFrame: false,
        setupSucceeded: false,
        revealSetupFailure: "",
        nativeHybridProgress: 0,
        caseIsCanonical: false,
        caseIsOnlyUnityRenderable: false,
        unityClearBackdropIsolated: false)

    public let checkpoint: String
    public let rawRequestUUID: String
    public let receiptUUID: String
    public let unityFrameCount: Int
    public let caseRootName: String
    public let caseTypeName: String
    public let caseEntityID: String
    public let caseRendererCount: Int
    public let foreignRendererCount: Int
    public let caseStableFrame: Bool
    public let cameraStableFrame: Bool
    public let setupSucceeded: Bool
    public let revealSetupFailure: String
    public let nativeHybridProgress: Double
    public let caseIsCanonical: Bool
    public let caseIsOnlyUnityRenderable: Bool
    public let unityClearBackdropIsolated: Bool
}

public struct GachaNativeHybridR030TraceState: Equatable {
    public static let empty = GachaNativeHybridR030TraceState(
        checkpoint: "",
        stableFrameOrdinal: 0,
        rawRequestUUID: "",
        receiptUUID: "",
        unityFrameCount: -1,
        cameraInstanceID: 0,
        cameraName: "",
        caseRootName: "",
        caseTypeName: "",
        caseEntityID: "",
        caseRendererCount: 0,
        foreignRendererCount: -1,
        caseStableFrame: false,
        cameraStableFrame: false,
        isolationActive: false,
        usesCavityClearBackdrop: false,
        publishSetupPublished: false,
        publishSetupSucceeded: false,
        publishSetupFailure: "",
        nativeHybridProgress: 0,
        caseIsCanonical: false,
        caseIsOnlyUnityRenderable: false)

    public let checkpoint: String
    public let stableFrameOrdinal: Int
    public let rawRequestUUID: String
    public let receiptUUID: String
    public let unityFrameCount: Int
    public let cameraInstanceID: Int64
    public let cameraName: String
    public let caseRootName: String
    public let caseTypeName: String
    public let caseEntityID: String
    public let caseRendererCount: Int
    public let foreignRendererCount: Int
    public let caseStableFrame: Bool
    public let cameraStableFrame: Bool
    public let isolationActive: Bool
    public let usesCavityClearBackdrop: Bool
    public let publishSetupPublished: Bool
    public let publishSetupSucceeded: Bool
    public let publishSetupFailure: String
    public let nativeHybridProgress: Double
    public let caseIsCanonical: Bool
    public let caseIsOnlyUnityRenderable: Bool
}

@MainActor
public final class GachaStoreModel: ObservableObject {
    public static let shared = GachaStoreModel()

    @Published public private(set) var series: [GachaSeriesInfo] = []
    @Published public private(set) var prizes: [GachaPrizeInfo] = []
    @Published public private(set) var tickets = 0
    @Published public private(set) var coins = 0
    @Published public private(set) var shardsBySeries: [String: Int] = [:]
    @Published public private(set) var signatureMisses: [String: Int] = [:]
    @Published public private(set) var heirloomMisses: [String: Int] = [:]
    @Published public private(set) var totalDraws: [String: Int] = [:]
    @Published public private(set) var owned: Set<String> = []
    @Published public var pendingReceipt: [GachaReceiptRow] = []
    @Published public var lastFailureReason = ""
    @Published public private(set) var receiptRequestID = ""
    @Published public private(set) var transactionPhase = "idle"
    @Published public private(set) var revealRequestID = ""
    @Published public private(set) var revealSetupSucceeded = false
    @Published public private(set) var revealSetupFailure = ""
    @Published public private(set) var revealSetupCallbackSerial = 0
    @Published public private(set) var revealHandoffDurationSeconds = 0.0
    @Published public private(set) var revealPhase = "idle"
    @Published public private(set) var revealCaseCrossedPackLip = false
    @Published public private(set) var revealComposition =
        GachaRevealCompositionState.empty
    @Published public private(set) var nativeHybridR029Trace =
        GachaNativeHybridR029TraceState.empty
    @Published public private(set) var nativeHybridR030Trace =
        GachaNativeHybridR030TraceState.empty

    public func requestState(previewToken: String? = nil) {
        let resolvedPreviewToken: String
        if let previewToken {
            resolvedPreviewToken = previewToken
        } else if GachaPackHandoffRules.isNativeHybridCandidatePreview {
            resolvedPreviewToken = GachaPackHandoffRules
                .nativeHybridCandidatePreviewToken
        } else if ProcessInfo.processInfo.arguments.contains(
            "--gacha-no-funds-preview") {
            // Device-parity rehearsal: no preview priming, so the store sees
            // the real (empty) wallet and must disable the CTA instead of
            // hanging on a refused draw.
            resolvedPreviewToken = ""
        } else if ProcessInfo.processInfo.arguments.contains(
            "--gacha-no-funds-preview") {
            // Device-parity rehearsal: no preview priming, so the store sees
            // the real (empty) wallet and must disable the CTA instead of
            // hanging on a refused draw.
            resolvedPreviewToken = ""
        } else if ProcessInfo.processInfo.arguments.contains(
            "--premium-display-case-gate12-preview") {
            resolvedPreviewToken = "premium-display-case-gate12-r4"
        } else {
            resolvedPreviewToken = ""
        }
        GachaUnityBridge.send(
            "RequestGachaStateFromNativeUi",
            value: resolvedPreviewToken)
    }

    public func beginNativeHybridCandidate(previewToken: String) {
        series = []
        prizes = []
        pendingReceipt = []
        lastFailureReason = ""
        receiptRequestID = ""
        transactionPhase = "idle"
        clearRevealState()
        requestState(previewToken: previewToken)
    }

    public func draw(
        requestID: UUID,
        seriesId: String,
        count: Int,
        useCoins: Bool
    ) {
        GachaUnityBridge.send(
            "DrawGachaFromNativeUi",
            value: "\(requestID.uuidString.lowercased())|\(seriesId)|\(count)|\(useCoins ? "coin" : "ticket")")
    }

    public func draw(seriesId: String, count: Int, useCoins: Bool) {
        draw(
            requestID: UUID(),
            seriesId: seriesId,
            count: count,
            useCoins: useCoins)
    }

    public func presentReveal(
        requestID: UUID,
        nativeHybridCandidate: Bool = false
    ) {
        GachaUnityBridge.send(
            nativeHybridCandidate
                ? "PresentGachaNativeHybridCandidateFromNativeUi"
                : "PresentGachaPrizeFromNativeUi",
            value: requestID.uuidString.lowercased())
    }

    public func presentR028NativeHybridReveal(requestID: UUID) {
        GachaUnityBridge.send(
            "PresentGachaNativeHybridR028CandidateFromNativeUi",
            value: requestID.uuidString.lowercased())
    }

    public func presentR029NativeHybridReveal(requestID: UUID) {
        GachaUnityBridge.send(
            "PresentGachaNativeHybridR029CandidateFromNativeUi",
            value: requestID.uuidString.lowercased())
    }

    public func presentR030NativeHybridReveal(requestID: UUID) {
        GachaUnityBridge.send(
            "PresentGachaNativeHybridR030CandidateFromNativeUi",
            value: requestID.uuidString.lowercased())
    }

    public func configureR029CaptureCheckpoint(
        requestID: UUID,
        checkpoint: GachaNativeHybridR029CaptureCheckpoint?
    ) {
        guard let checkpoint else { return }
        GachaUnityBridge.send(
            "ConfigureGachaNativeHybridR029CaptureCheckpointFromNativeUi",
            value: "\(requestID.uuidString.lowercased())|\(checkpoint.rawValue)")
    }

    public func configureR030CaptureCheckpoint(
        requestID: UUID,
        checkpoint: GachaNativeHybridR030CaptureCheckpoint?
    ) {
        guard let checkpoint else { return }
        GachaUnityBridge.send(
            "ConfigureGachaNativeHybridR030CaptureCheckpointFromNativeUi",
            value: "\(requestID.uuidString.lowercased())|\(checkpoint.rawValue)")
    }

    public func startReveal(requestID: UUID) {
        GachaUnityBridge.send(
            "StartGachaRevealFromNativeUi",
            value: requestID.uuidString.lowercased())
    }

    public func setNativeHybridPreviewProgress(
        requestID: UUID,
        progress: Double
    ) {
        let value = String(format: "%.3f", locale: Locale(
            identifier: "en_US_POSIX"), progress)
        GachaUnityBridge.send(
            "SetGachaNativeHybridPreviewProgressFromNativeUi",
            value: "\(requestID.uuidString.lowercased())|\(value)")
    }

    public func setNativeHybridApertureHold(
        requestID: UUID,
        hold: Bool
    ) {
        GachaUnityBridge.send(
            "SetGachaNativeHybridApertureHoldFromNativeUi",
            value: "\(requestID.uuidString.lowercased())|\(hold ? "1" : "0")")
    }

    public func skipReveal(requestID: UUID) {
        GachaUnityBridge.send(
            "SkipGachaRevealFromNativeUi",
            value: requestID.uuidString.lowercased())
    }

    public func acknowledgeReveal(requestID: UUID) {
        GachaUnityBridge.send(
            "AcknowledgeGachaRevealFromNativeUi",
            value: requestID.uuidString.lowercased())
    }

    public func interruptReveal(requestID: UUID) {
        GachaUnityBridge.send(
            "InterruptGachaRevealFromNativeUi",
            value: requestID.uuidString.lowercased())
    }

    /// Pack selected: Unity hides the spinner cameras and dims the cave to
    /// 25% behind the sealed Pack, so the stage never cuts to black.
    /// `tint` and `strength` describe the Pack-hue backdrop Unity keeps in
    /// front of the environment until the card flips.
    public func enterGachaStage(
        tint: (red: Double, green: Double, blue: Double)? = nil,
        strength: Double = 1,
        backdropSnapshotPath: String? = nil
    ) {
        var payload = tint.map {
            String(
                format: "%.3f,%.3f,%.3f,%.3f",
                min(max($0.red, 0), 1),
                min(max($0.green, 0), 1),
                min(max($0.blue, 0), 1),
                min(max(strength, 0), 1))
        } ?? ""
        // A PNG of the native backdrop lets Unity hold the exact same image
        // behind the case until the flip, whatever the native design is.
        if let path = backdropSnapshotPath, !path.isEmpty {
            payload += "|" + path
        }
        GachaUnityBridge.send("EnterGachaStageFromNativeUi", value: payload)
    }

    /// Storefront closed without a reveal; Unity restores the library view.
    public func leaveGachaStage() {
        GachaUnityBridge.send("LeaveGachaStageFromNativeUi")
    }

    /// Seal finished tearing: one medium transient via the semantic Haptic
    /// pipeline (mechanism state → semantic event → recipe → renderer).
    public func emitTearSnap() {
        GachaUnityBridge.send("EmitGachaTearSnapFromNativeUi")
    }

    /// Carousel settled on a tier: one detent through the semantic pipeline,
    /// weighted by the tier ladder (0…1).
    public func emitCarouselSnap(signal: Double) {
        GachaUnityBridge.send(
            "EmitGachaCarouselSnapFromNativeUi",
            value: String(format: "%.3f", min(max(signal, 0), 1)))
    }

    public func redeem(prizeId: String) {
        GachaUnityBridge.send("RedeemGachaShardsFromNativeUi", value: prizeId)
    }

    // MARK: TSV ingestion (called from the Unity bridge)

    public func ingest(catalog: String, snapshot: String, receipt: String) {
        if !catalog.isEmpty { parseCatalog(catalog) }
        if !snapshot.isEmpty { parseSnapshot(snapshot) }
        parseReceipt(receipt)
    }

    private func parseCatalog(_ payload: String) {
        var nextSeries: [GachaSeriesInfo] = []
        var nextPrizes: [GachaPrizeInfo] = []
        for line in payload.split(separator: "\n") {
            let cells = line.split(separator: "\t", omittingEmptySubsequences: false)
                .map(String.init)
            if cells.count >= 7, cells[0] == "series" {
                nextSeries.append(GachaSeriesInfo(
                    id: cells[1],
                    name: cells[2],
                    rates: cells[3...6].map { Double($0) ?? 0 }))
            } else if cells.count >= 6, cells[0] == "prize" {
                nextPrizes.append(GachaPrizeInfo(
                    id: cells[1],
                    seriesId: cells[2],
                    rarity: GachaRarityTier(rawValue: Int(cells[3]) ?? 0) ?? .standard,
                    kindIndex: Int(cells[4]) ?? 0,
                    name: cells[5]))
            }
        }
        series = nextSeries
        prizes = nextPrizes
    }

    private func parseSnapshot(_ payload: String) {
        for line in payload.split(separator: "\n") {
            let cells = line.split(separator: "\t", omittingEmptySubsequences: false)
                .map(String.init)
            if cells.count >= 3, cells[0] == "wallet" {
                tickets = Int(cells[1]) ?? 0
                coins = Int(cells[2]) ?? 0
            } else if cells.count >= 6, cells[0] == "series-state" {
                signatureMisses[cells[1]] = Int(cells[2]) ?? 0
                heirloomMisses[cells[1]] = Int(cells[3]) ?? 0
                shardsBySeries[cells[1]] = Int(cells[4]) ?? 0
                totalDraws[cells[1]] = Int(cells[5]) ?? 0
            } else if cells.count >= 2, cells[0] == "owned" {
                owned = Set(cells[1].split(separator: "|").map(String.init))
            } else if cells.count >= 1, cells[0] == "owned" {
                owned = []
            } else if cells.count >= 3, cells[0] == "transaction" {
                receiptRequestID = cells[1]
                transactionPhase = cells[2]
            }
        }
    }

    private func parseReceipt(_ payload: String) {
        guard !payload.isEmpty else { return }
        var rows: [GachaReceiptRow] = []
        var failure = ""
        for line in payload.split(separator: "\n") {
            let cells = line.split(separator: "\t", omittingEmptySubsequences: false)
                .map(String.init)
            if cells.count >= 2, cells[0] == "result" {
                failure = cells[1] == "ok" ? "" : cells[1]
                if cells.count >= 3 {
                    receiptRequestID = cells[2]
                }
            } else if cells.count >= 10, cells[0] == "row" {
                rows.append(GachaReceiptRow(
                    prizeId: cells[1],
                    name: cells[2],
                    rarity: GachaRarityTier(rawValue: Int(cells[3]) ?? 0) ?? .standard,
                    isNew: cells[5] == "1",
                    shardsGained: Int(cells[6]) ?? 0,
                    forcedBySignaturePity: cells[7] == "1",
                    forcedByHeirloomPity: cells[8] == "1",
                    forcedByTenDraw: cells[9] == "1",
                    firstObtainedAtUtc: cells.count >= 12 ? cells[10] : "",
                    collectibleId: cells.count >= 12 ? cells[11] : ""))
            }
        }
        lastFailureReason = failure
        // A non-empty receipt payload is authoritative for the latest request.
        // Clear stale rows on failures as well as replacing them on success.
        pendingReceipt = rows
    }

    public func ingestRevealSetup(
        requestID: String,
        succeeded: Bool,
        failureReason: String,
        handoffDurationSeconds: Float
    ) {
        revealRequestID = requestID
        revealSetupFailure = failureReason
        revealHandoffDurationSeconds = succeeded
            ? max(0, Double(handoffDurationSeconds))
            : 0
        revealSetupSucceeded = succeeded
        revealSetupCallbackSerial &+= 1
    }

    public func ingestRevealPhase(requestID: String, phase: String) {
        revealRequestID = requestID
        revealPhase = phase
        if phase == "case-crossing-pack-lip" {
            revealCaseCrossedPackLip = true
        }
    }

    public func ingestRevealComposition(
        requestID: String,
        caseRootName: String,
        caseTypeName: String,
        caseEntityID: String,
        caseRendererCount: Int,
        caseIsCanonical: Bool,
        caseIsOnlyUnityRenderable: Bool,
        unityClearBackdropIsolated: Bool
    ) {
        guard requestID == revealRequestID || revealRequestID.isEmpty else {
            return
        }
        revealRequestID = requestID
        revealComposition = GachaRevealCompositionState(
            caseRootName: caseRootName,
            caseTypeName: caseTypeName,
            caseEntityID: caseEntityID,
            caseRendererCount: max(0, caseRendererCount),
            caseIsCanonical: caseIsCanonical,
            caseIsOnlyUnityRenderable: caseIsOnlyUnityRenderable,
            unityClearBackdropIsolated: unityClearBackdropIsolated)
    }

    public func ingestNativeHybridR029Trace(
        checkpoint: String,
        rawRequestUUID: String,
        receiptUUID: String,
        unityFrameCount: Int,
        caseRootName: String,
        caseTypeName: String,
        caseEntityID: String,
        caseRendererCount: Int,
        foreignRendererCount: Int,
        caseStableFrame: Bool,
        cameraStableFrame: Bool,
        setupSucceeded: Bool,
        revealSetupFailure: String,
        nativeHybridProgress: Float,
        caseIsCanonical: Bool,
        caseIsOnlyUnityRenderable: Bool,
        unityClearBackdropIsolated: Bool
    ) {
        guard GachaNativeHybridR029Rules.isIsolatedCandidate else {
            return
        }
        nativeHybridR029Trace = GachaNativeHybridR029TraceState(
            checkpoint: checkpoint,
            rawRequestUUID: rawRequestUUID,
            receiptUUID: receiptUUID,
            unityFrameCount: unityFrameCount,
            caseRootName: caseRootName,
            caseTypeName: caseTypeName,
            caseEntityID: caseEntityID,
            caseRendererCount: max(0, caseRendererCount),
            foreignRendererCount: foreignRendererCount,
            caseStableFrame: caseStableFrame,
            cameraStableFrame: cameraStableFrame,
            setupSucceeded: setupSucceeded,
            revealSetupFailure: revealSetupFailure,
            nativeHybridProgress: max(0, Double(nativeHybridProgress)),
            caseIsCanonical: caseIsCanonical,
            caseIsOnlyUnityRenderable: caseIsOnlyUnityRenderable,
            unityClearBackdropIsolated: unityClearBackdropIsolated)
    }

    public func ingestNativeHybridR030Trace(
        checkpoint: String,
        stableFrameOrdinal: Int,
        rawRequestUUID: String,
        receiptUUID: String,
        unityFrameCount: Int,
        cameraInstanceID: Int64,
        cameraName: String,
        caseRootName: String,
        caseTypeName: String,
        caseEntityID: String,
        caseRendererCount: Int,
        foreignRendererCount: Int,
        caseStableFrame: Bool,
        cameraStableFrame: Bool,
        isolationActive: Bool,
        usesCavityClearBackdrop: Bool,
        publishSetupPublished: Bool,
        publishSetupSucceeded: Bool,
        publishSetupFailure: String,
        nativeHybridProgress: Float,
        caseIsCanonical: Bool,
        caseIsOnlyUnityRenderable: Bool
    ) {
        guard GachaNativeHybridR030Rules.isIsolatedCandidate else {
            return
        }
        nativeHybridR030Trace = GachaNativeHybridR030TraceState(
            checkpoint: checkpoint,
            stableFrameOrdinal: max(0, stableFrameOrdinal),
            rawRequestUUID: rawRequestUUID,
            receiptUUID: receiptUUID,
            unityFrameCount: unityFrameCount,
            cameraInstanceID: cameraInstanceID,
            cameraName: cameraName,
            caseRootName: caseRootName,
            caseTypeName: caseTypeName,
            caseEntityID: caseEntityID,
            caseRendererCount: max(0, caseRendererCount),
            foreignRendererCount: foreignRendererCount,
            caseStableFrame: caseStableFrame,
            cameraStableFrame: cameraStableFrame,
            isolationActive: isolationActive,
            usesCavityClearBackdrop: usesCavityClearBackdrop,
            publishSetupPublished: publishSetupPublished,
            publishSetupSucceeded: publishSetupSucceeded,
            publishSetupFailure: publishSetupFailure,
            nativeHybridProgress: max(0, Double(nativeHybridProgress)),
            caseIsCanonical: caseIsCanonical,
            caseIsOnlyUnityRenderable: caseIsOnlyUnityRenderable)
    }

    public func clearRevealState() {
        revealRequestID = ""
        revealSetupSucceeded = false
        revealSetupFailure = ""
        revealSetupCallbackSerial = 0
        revealHandoffDurationSeconds = 0
        revealPhase = "idle"
        revealCaseCrossedPackLip = false
        revealComposition = .empty
        nativeHybridR029Trace = .empty
        nativeHybridR030Trace = .empty
    }
}

@_cdecl("CodexGachaReceiveState")
public func CodexGachaReceiveState(
    _ catalogPayload: UnsafePointer<CChar>?,
    _ snapshotPayload: UnsafePointer<CChar>?,
    _ receiptPayload: UnsafePointer<CChar>?) {
    let catalog = catalogPayload.map { String(cString: $0) } ?? ""
    let snapshot = snapshotPayload.map { String(cString: $0) } ?? ""
    let receipt = receiptPayload.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.ingest(
            catalog: catalog,
            snapshot: snapshot,
            receipt: receipt)
    }
}

@_cdecl("CodexGachaRevealReceiveSetup")
public func CodexGachaRevealReceiveSetup(
    _ requestID: UnsafePointer<CChar>?,
    _ succeeded: Int32,
    _ failureReason: UnsafePointer<CChar>?,
    _ handoffDurationSeconds: Float
) {
    let id = requestID.map { String(cString: $0) } ?? ""
    let reason = failureReason.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.ingestRevealSetup(
            requestID: id,
            succeeded: succeeded != 0,
            failureReason: reason,
            handoffDurationSeconds: handoffDurationSeconds)
    }
}

@_cdecl("CodexGachaRevealReceivePhase")
public func CodexGachaRevealReceivePhase(
    _ requestID: UnsafePointer<CChar>?,
    _ phase: UnsafePointer<CChar>?
) {
    let id = requestID.map { String(cString: $0) } ?? ""
    let token = phase.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.ingestRevealPhase(
            requestID: id,
            phase: token)
    }
}

@_cdecl("CodexGachaRevealReceiveComposition")
public func CodexGachaRevealReceiveComposition(
    _ requestID: UnsafePointer<CChar>?,
    _ caseRootName: UnsafePointer<CChar>?,
    _ caseTypeName: UnsafePointer<CChar>?,
    _ caseEntityID: UnsafePointer<CChar>?,
    _ caseRendererCount: Int32,
    _ caseIsCanonical: Int32,
    _ caseIsOnlyUnityRenderable: Int32,
    _ unityClearBackdropIsolated: Int32
) {
    let id = requestID.map { String(cString: $0) } ?? ""
    let rootName = caseRootName.map { String(cString: $0) } ?? ""
    let typeName = caseTypeName.map { String(cString: $0) } ?? ""
    let entityID = caseEntityID.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.ingestRevealComposition(
            requestID: id,
            caseRootName: rootName,
            caseTypeName: typeName,
            caseEntityID: entityID,
            caseRendererCount: Int(caseRendererCount),
            caseIsCanonical: caseIsCanonical != 0,
            caseIsOnlyUnityRenderable: caseIsOnlyUnityRenderable != 0,
            unityClearBackdropIsolated: unityClearBackdropIsolated != 0)
    }
}

@_cdecl("CodexGachaRevealReceiveR029Trace")
public func CodexGachaRevealReceiveR029Trace(
    _ checkpoint: UnsafePointer<CChar>?,
    _ rawRequestUUID: UnsafePointer<CChar>?,
    _ receiptUUID: UnsafePointer<CChar>?,
    _ unityFrameCount: Int32,
    _ caseRootName: UnsafePointer<CChar>?,
    _ caseTypeName: UnsafePointer<CChar>?,
    _ caseEntityID: UnsafePointer<CChar>?,
    _ caseRendererCount: Int32,
    _ foreignRendererCount: Int32,
    _ caseStableFrame: Int32,
    _ cameraStableFrame: Int32,
    _ setupSucceeded: Int32,
    _ revealSetupFailure: UnsafePointer<CChar>?,
    _ nativeHybridProgress: Float,
    _ caseIsCanonical: Int32,
    _ caseIsOnlyUnityRenderable: Int32,
    _ unityClearBackdropIsolated: Int32
) {
    let checkpointValue = checkpoint.map { String(cString: $0) } ?? ""
    let requestValue = rawRequestUUID.map { String(cString: $0) } ?? ""
    let receiptValue = receiptUUID.map { String(cString: $0) } ?? ""
    let rootName = caseRootName.map { String(cString: $0) } ?? ""
    let typeName = caseTypeName.map { String(cString: $0) } ?? ""
    let entityID = caseEntityID.map { String(cString: $0) } ?? ""
    let failure = revealSetupFailure.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.ingestNativeHybridR029Trace(
            checkpoint: checkpointValue,
            rawRequestUUID: requestValue,
            receiptUUID: receiptValue,
            unityFrameCount: Int(unityFrameCount),
            caseRootName: rootName,
            caseTypeName: typeName,
            caseEntityID: entityID,
            caseRendererCount: Int(caseRendererCount),
            foreignRendererCount: Int(foreignRendererCount),
            caseStableFrame: caseStableFrame != 0,
            cameraStableFrame: cameraStableFrame != 0,
            setupSucceeded: setupSucceeded != 0,
            revealSetupFailure: failure,
            nativeHybridProgress: nativeHybridProgress,
            caseIsCanonical: caseIsCanonical != 0,
            caseIsOnlyUnityRenderable: caseIsOnlyUnityRenderable != 0,
            unityClearBackdropIsolated: unityClearBackdropIsolated != 0)
    }
}

@_cdecl("CodexGachaRevealReceiveR030Trace")
public func CodexGachaRevealReceiveR030Trace(
    _ checkpoint: UnsafePointer<CChar>?,
    _ stableFrameOrdinal: Int32,
    _ rawRequestUUID: UnsafePointer<CChar>?,
    _ receiptUUID: UnsafePointer<CChar>?,
    _ unityFrameCount: Int32,
    _ cameraInstanceID: Int64,
    _ cameraName: UnsafePointer<CChar>?,
    _ caseRootName: UnsafePointer<CChar>?,
    _ caseTypeName: UnsafePointer<CChar>?,
    _ caseEntityID: UnsafePointer<CChar>?,
    _ caseRendererCount: Int32,
    _ foreignRendererCount: Int32,
    _ caseStableFrame: Int32,
    _ cameraStableFrame: Int32,
    _ isolationActive: Int32,
    _ usesCavityClearBackdrop: Int32,
    _ publishSetupPublished: Int32,
    _ publishSetupSucceeded: Int32,
    _ publishSetupFailure: UnsafePointer<CChar>?,
    _ nativeHybridProgress: Float,
    _ caseIsCanonical: Int32,
    _ caseIsOnlyUnityRenderable: Int32
) {
    let checkpointValue = checkpoint.map { String(cString: $0) } ?? ""
    let requestValue = rawRequestUUID.map { String(cString: $0) } ?? ""
    let receiptValue = receiptUUID.map { String(cString: $0) } ?? ""
    let cameraNameValue = cameraName.map { String(cString: $0) } ?? ""
    let rootName = caseRootName.map { String(cString: $0) } ?? ""
    let typeName = caseTypeName.map { String(cString: $0) } ?? ""
    let entityID = caseEntityID.map { String(cString: $0) } ?? ""
    let failure = publishSetupFailure.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.ingestNativeHybridR030Trace(
            checkpoint: checkpointValue,
            stableFrameOrdinal: Int(stableFrameOrdinal),
            rawRequestUUID: requestValue,
            receiptUUID: receiptValue,
            unityFrameCount: Int(unityFrameCount),
            cameraInstanceID: cameraInstanceID,
            cameraName: cameraNameValue,
            caseRootName: rootName,
            caseTypeName: typeName,
            caseEntityID: entityID,
            caseRendererCount: Int(caseRendererCount),
            foreignRendererCount: Int(foreignRendererCount),
            caseStableFrame: caseStableFrame != 0,
            cameraStableFrame: cameraStableFrame != 0,
            isolationActive: isolationActive != 0,
            usesCavityClearBackdrop: usesCavityClearBackdrop != 0,
            publishSetupPublished: publishSetupPublished != 0,
            publishSetupSucceeded: publishSetupSucceeded != 0,
            publishSetupFailure: failure,
            nativeHybridProgress: nativeHybridProgress,
            caseIsCanonical: caseIsCanonical != 0,
            caseIsOnlyUnityRenderable: caseIsOnlyUnityRenderable != 0)
    }
}

// MARK: - Store view

struct LegacyGachaStoreView: View {
    @ObservedObject private var model = GachaStoreModel.shared
    @State private var showOdds = false
    @State private var showResults = false

    public init() {}

    private var activeSeries: GachaSeriesInfo? { model.series.first }

    public var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            ScrollView {
                VStack(spacing: 14) {
                    walletHeader
                    if let series = activeSeries {
                        seriesBanner(series)
                        pityCard(series)
                        drawButtons(series)
                        GachaCoinShopView()
                        redeemShop(series)
                        collectionGrid(series)
                    } else {
                        ProgressView().tint(.white).padding(.top, 80)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 24)
            }
        }
        .onAppear { model.requestState() }
        .onChange(of: model.pendingReceipt) { rows in
            showResults = !rows.isEmpty
        }
        .sheet(isPresented: $showOdds) { oddsSheet }
        .sheet(isPresented: $showResults) {
            resultsSheet
        }
    }

    private var walletHeader: some View {
        HStack(spacing: 10) {
            walletChip(icon: "ticket", value: model.tickets, label: "抽取券")
            walletChip(icon: "gearshape.2", value: model.coins, label: "齿轮币")
            Spacer()
            Button {
                showOdds = true
            } label: {
                Label("概率公示", systemImage: "doc.text.magnifyingglass")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
            }
        }
        .padding(.top, 12)
    }

    private func walletChip(icon: String, value: Int, label: String) -> some View {
        HStack(spacing: 6) {
            Image(systemName: icon).font(.caption)
            Text("\(value)")
                .font(.system(.subheadline, design: .monospaced).bold())
            Text(label).font(.caption2).opacity(0.7)
        }
        .foregroundColor(.white)
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(.ultraThinMaterial, in: Capsule())
    }

    private func seriesBanner(_ series: GachaSeriesInfo) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("当前系列")
                .font(.caption2)
                .foregroundColor(.white.opacity(0.55))
            Text(series.name)
                .font(.title2.bold())
                .foregroundColor(.white)
            Text("盲盒限定外观 · 不含任何成长或物理加成")
                .font(.caption)
                .foregroundColor(.white.opacity(0.6))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private func pityCard(_ series: GachaSeriesInfo) -> some View {
        let signatureMisses = model.signatureMisses[series.id] ?? 0
        let heirloomMisses = model.heirloomMisses[series.id] ?? 0
        return VStack(spacing: 10) {
            pityRow(
                title: "臻藏保底",
                tint: GachaRarityTier.signature.tint,
                current: signatureMisses,
                target: 50,
                caption: "50 次未出即第 51 抽必得臻藏或更高")
            pityRow(
                title: "传世保底",
                tint: GachaRarityTier.heirloom.tint,
                current: heirloomMisses,
                target: 89,
                caption: "累计 90 抽内必得传世")
        }
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private func pityRow(
        title: String,
        tint: Color,
        current: Int,
        target: Int,
        caption: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(title).font(.caption.bold()).foregroundColor(.white)
                Spacer()
                Text("\(current) / \(target + 1)")
                    .font(.system(.caption, design: .monospaced))
                    .foregroundColor(tint)
            }
            ProgressView(value: Double(min(current, target)), total: Double(target))
                .tint(tint)
            Text(caption)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.45))
        }
    }

    private func drawButtons(_ series: GachaSeriesInfo) -> some View {
        HStack(spacing: 12) {
            drawButton(
                title: "单抽",
                subtitle: "1 券 / 160 币",
                seriesId: series.id,
                count: 1)
            drawButton(
                title: "十连",
                subtitle: "10 券 / 1440 币 · 必出精制+",
                seriesId: series.id,
                count: 10)
        }
    }

    private func drawButton(
        title: String,
        subtitle: String,
        seriesId: String,
        count: Int) -> some View {
        Button {
            let ticketCost = count
            model.draw(
                seriesId: seriesId,
                count: count,
                useCoins: model.tickets < ticketCost)
        } label: {
            VStack(spacing: 4) {
                Text(title).font(.headline)
                Text(subtitle).font(.caption2).opacity(0.65)
            }
            .foregroundColor(.black)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(Color.white, in: RoundedRectangle(cornerRadius: 16))
        }
    }

    private func redeemShop(_ series: GachaSeriesInfo) -> some View {
        let shards = model.shardsBySeries[series.id] ?? 0
        let redeemables = model.prizes.filter {
            $0.seriesId == series.id
                && !model.owned.contains($0.id)
                && $0.rarity.redeemCost != nil
        }
        return VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("兑换所").font(.headline).foregroundColor(.white)
                Spacer()
                Label("\(shards)", systemImage: "sparkles")
                    .font(.system(.caption, design: .monospaced))
                    .foregroundColor(.white.opacity(0.8))
            }
            if redeemables.isEmpty {
                Text("本系列可兑换奖品均已入库")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.5))
            } else {
                ForEach(redeemables) { prize in
                    redeemRow(prize: prize, shards: shards)
                }
            }
        }
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private func redeemRow(prize: GachaPrizeInfo, shards: Int) -> some View {
        let cost = prize.rarity.redeemCost ?? Int.max
        return HStack {
            Circle().fill(prize.rarity.tint).frame(width: 8, height: 8)
            VStack(alignment: .leading, spacing: 2) {
                Text(prize.name).font(.subheadline).foregroundColor(.white)
                Text("\(prize.rarity.title) · \(prize.kindTitle)")
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.5))
            }
            Spacer()
            Button {
                model.redeem(prizeId: prize.id)
            } label: {
                Label("\(cost)", systemImage: "sparkles")
                    .font(.caption.bold())
                    .foregroundColor(shards >= cost ? .black : .white.opacity(0.35))
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(
                        shards >= cost ? Color.white : Color.white.opacity(0.08),
                        in: Capsule())
            }
            .disabled(shards < cost)
        }
    }

    private func collectionGrid(_ series: GachaSeriesInfo) -> some View {
        let seriesPrizes = model.prizes.filter { $0.seriesId == series.id }
        let columns = [GridItem(.adaptive(minimum: 150), spacing: 10)]
        return VStack(alignment: .leading, spacing: 10) {
            Text("收藏库 \(seriesPrizes.filter { model.owned.contains($0.id) }.count)"
                + " / \(seriesPrizes.count)")
                .font(.headline)
                .foregroundColor(.white)
            LazyVGrid(columns: columns, spacing: 10) {
                ForEach(seriesPrizes) { prize in
                    collectionCell(prize)
                }
            }
        }
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private func collectionCell(_ prize: GachaPrizeInfo) -> some View {
        let isOwned = model.owned.contains(prize.id)
        return VStack(alignment: .leading, spacing: 4) {
            HStack {
                Circle().fill(prize.rarity.tint).frame(width: 8, height: 8)
                Text(prize.rarity.title)
                    .font(.caption2)
                    .foregroundColor(prize.rarity.tint)
                Spacer()
                Image(systemName: isOwned ? "checkmark.seal.fill" : "lock")
                    .font(.caption2)
                    .foregroundColor(isOwned ? prize.rarity.tint : .white.opacity(0.3))
            }
            Text(prize.name)
                .font(.footnote.bold())
                .foregroundColor(isOwned ? .white : .white.opacity(0.45))
            Text(prize.kindTitle)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.4))
        }
        .padding(10)
        .background(
            Color.white.opacity(isOwned ? 0.10 : 0.04),
            in: RoundedRectangle(cornerRadius: 12))
    }

    private var oddsSheet: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    Text("概率公示")
                        .font(.title3.bold())
                        .foregroundColor(.white)
                    if let series = activeSeries {
                        ForEach(GachaRarityTier.allCases, id: \.rawValue) { tier in
                            HStack {
                                Circle().fill(tier.tint).frame(width: 8, height: 8)
                                Text(tier.title).foregroundColor(.white)
                                Spacer()
                                Text(String(
                                    format: "%.2f%%",
                                    (series.rates[safe: tier.rawValue] ?? 0) * 100))
                                    .font(.system(.body, design: .monospaced))
                                    .foregroundColor(tier.tint)
                            }
                            .font(.subheadline)
                        }
                    }
                    Divider().background(Color.white.opacity(0.2))
                    Group {
                        Text("· 十连抽保证至少 1 件精制或更高品质")
                        Text("· 连续 40 抽未出臻藏后，臻藏概率逐抽提升；第 51 抽必得臻藏或更高")
                        Text("· 累计 90 抽内必得传世")
                        Text("· 重复奖品自动转换为合金屑，可在兑换所直接兑换指定奖品")
                        Text("· 全部奖品仅为外观与收藏用途，不改变任何玩具的物理手感、成长速度或经验")
                    }
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
                }
                .padding(20)
            }
        }
    }

    private var resultsSheet: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            VStack(spacing: 12) {
                Text("揭晓结果")
                    .font(.title3.bold())
                    .foregroundColor(.white)
                    .padding(.top, 18)
                ScrollView {
                    VStack(spacing: 8) {
                        ForEach(model.pendingReceipt) { row in
                            receiptRow(row)
                        }
                    }
                    .padding(.horizontal, 16)
                }
                Button {
                    model.pendingReceipt = []
                    showResults = false
                } label: {
                    Text("收入囊中")
                        .font(.headline)
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.white, in: RoundedRectangle(cornerRadius: 16))
                }
                .padding(16)
            }
        }
    }

    private func receiptRow(_ row: GachaReceiptRow) -> some View {
        HStack {
            Circle().fill(row.rarity.tint).frame(width: 10, height: 10)
            VStack(alignment: .leading, spacing: 2) {
                Text(row.name).font(.subheadline.bold()).foregroundColor(.white)
                HStack(spacing: 6) {
                    Text(row.rarity.title)
                        .font(.caption2)
                        .foregroundColor(row.rarity.tint)
                    if row.forcedBySignaturePity || row.forcedByHeirloomPity {
                        Text("保底")
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.6))
                    }
                    if row.forcedByTenDraw {
                        Text("十连保障")
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.6))
                    }
                }
            }
            Spacer()
            if row.isNew {
                Text("NEW")
                    .font(.caption2.bold())
                    .foregroundColor(.black)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(row.rarity.tint, in: Capsule())
            } else {
                Label("+\(row.shardsGained)", systemImage: "sparkles")
                    .font(.caption.bold())
                    .foregroundColor(.white.opacity(0.75))
            }
        }
        .padding(12)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 14))
    }
}

private extension Array where Element == Double {
    subscript(safe index: Int) -> Double? {
        indices.contains(index) ? self[index] : nil
    }
}
