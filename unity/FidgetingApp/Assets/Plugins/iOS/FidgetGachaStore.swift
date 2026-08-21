import Foundation
import SwiftUI

// MARK: - Unity bridge (send)

@_silgen_name("UnitySendMessage")
private func GachaUnitySendMessage(
    _ objectName: UnsafePointer<CChar>,
    _ methodName: UnsafePointer<CChar>,
    _ message: UnsafePointer<CChar>)

private enum GachaUnityBridge {
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
    public var id: String { prizeId }
    public let prizeId: String
    public let name: String
    public let rarity: GachaRarityTier
    public let kindIndex: Int
    public let isNew: Bool
    public let shardsGained: Int
    public let forcedBySignaturePity: Bool
    public let forcedByHeirloomPity: Bool
    public let forcedByTenDraw: Bool
}

public enum GachaRuntimeMode: String, Equatable {
    case production
    case internalUnlimited

    public var balanceText: String {
        self == .internalUnlimited ? "∞" : ""
    }

    public var title: String {
        self == .internalUnlimited ? "内测无限" : "正式经济"
    }
}

public enum GachaTransactionPhase: String, Equatable {
    case idle
    case requesting
    case prepared
    case awaitingAcceptance
    case acknowledging
    case completed
    case failed
}

public enum GachaRevealPhase: String, Equatable {
    case back
    case front
    case readable
    case complete

    public var caption: String {
        switch self {
        case .back: return "收藏盒入场"
        case .front: return "收藏盒翻正"
        case .readable: return "奖品确认"
        case .complete: return "揭晓完成"
        }
    }
}

public struct GachaPendingTransaction: Equatable, Identifiable {
    public var id: String { requestId }
    public let requestId: String
    public let phase: GachaTransactionPhase
    public let seriesId: String
    public let count: Int
    public let payment: String
    public let receipt: [GachaReceiptRow]
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
    @Published public private(set) var runtimeMode: GachaRuntimeMode = .production
    @Published public private(set) var transactionPhase: GachaTransactionPhase = .idle
    @Published public private(set) var pendingTransaction: GachaPendingTransaction?
    @Published public private(set) var packGateRequestId = ""
    @Published public private(set) var activeRequestId = ""
    @Published public private(set) var requestStatus = "idle"
    @Published public private(set) var revealPhase: GachaRevealPhase?
    @Published public private(set) var revealPhaseHistory: [GachaRevealPhase] = []
    @Published public private(set) var revealIsPresented = false
    @Published public private(set) var revealStartAcknowledged = false
    @Published public var pendingReceipt: [GachaReceiptRow] = []
    @Published public var lastFailureReason = ""

    private var requestTimeoutTask: Task<Void, Never>?
    private var revealWatchdogTask: Task<Void, Never>?
    private var revealWatchdogGeneration = 0
    private var revealSetupRequestedId = ""
    private var revealStartRequestedId = ""
    private var revealPhaseHistoryRequestId = ""
    private var packOpenedRequestId = ""

    public var canStartSingleDraw: Bool {
        pendingTransaction == nil
            && activeRequestId.isEmpty
            && (runtimeMode == .internalUnlimited || tickets > 0)
    }

    public var ticketBalanceText: String {
        runtimeMode == .internalUnlimited ? "∞" : "\(tickets)"
    }

    public var packIsPresented: Bool {
        guard let transaction = pendingTransaction else { return false }
        return !revealIsPresented
            && packGateRequestId == transaction.requestId
    }

    public var drawCostText: String {
        runtimeMode == .internalUnlimited
            ? "内测无限 · 不消耗正式票券"
            : "消耗 1 张抽取券"
    }

    public var visibleFailureReason: String {
        if !lastFailureReason.isEmpty {
            return localizedFailure(lastFailureReason)
        }
        if runtimeMode == .production && tickets < 1 {
            return "抽取券不足，当前无法单抽。"
        }
        return ""
    }

    public func requestState() {
        GachaUnityBridge.send("RequestGachaStateFromNativeUi")
    }

    @discardableResult
    public func draw(seriesId: String, count: Int, useCoins: Bool) -> String? {
        guard count == 1 else {
            lastFailureReason = "ten-draw-disabled"
            return nil
        }
        guard canStartSingleDraw else {
            if pendingTransaction != nil || !activeRequestId.isEmpty {
                lastFailureReason = "transaction-already-pending"
            } else if runtimeMode == .production && tickets < 1 {
                lastFailureReason = "insufficient-tickets"
            }
            return nil
        }

        let requestId = UUID().uuidString.lowercased()
        resetPackState()
        beginRevealPhaseHistory(requestId: requestId)
        activeRequestId = requestId
        transactionPhase = .requesting
        requestStatus = "requesting:\(requestId)"
        lastFailureReason = ""
        pendingReceipt = []
        GachaUnityBridge.send(
            "DrawGachaFromNativeUi",
            value: "\(seriesId)|1|ticket|\(requestId)")
        scheduleQueryTimeout(requestId: requestId, status: "requesting")
        return requestId
    }

    public func queryActiveTransaction() {
        let requestId = pendingTransaction?.requestId ?? activeRequestId
        guard !requestId.isEmpty else {
            requestState()
            return
        }
        requestStatus = "querying:\(requestId)"
        GachaUnityBridge.send(
            "QueryGachaTransactionFromNativeUi",
            value: requestId)
        scheduleQueryTimeout(requestId: requestId, status: "querying")
    }

    public func requestRevealSetupIfNeeded() {
        guard let transaction = pendingTransaction,
              transaction.phase == .awaitingAcceptance
                || (transaction.phase == .prepared
                    && packOpenedRequestId == transaction.requestId),
              revealSetupRequestedId != transaction.requestId,
              !revealIsPresented
        else { return }

        // A fresh setup replays the real six-stage sequence for this durable
        // request (including process-recovery and explicit retry paths), so its
        // ordered AX history must begin from an empty state as well.
        beginRevealPhaseHistory(requestId: transaction.requestId)
        revealSetupRequestedId = transaction.requestId
        requestStatus = "preparing-reveal:\(transaction.requestId)"
        GachaUnityBridge.send(
            "RequestGachaRevealFromNativeUi",
            value: transaction.requestId)
        scheduleRevealWatchdog(
            requestId: transaction.requestId,
            stage: "setup")
    }

    /// The Pack is presentation-only. Crossing the tear threshold authorizes
    /// mounting this request's existing durable receipt in Unity; it never
    /// generates, replaces, or acknowledges a transaction.
    public func commitPackOpening(requestId: String) {
        guard let transaction = pendingTransaction,
              transaction.requestId == requestId,
              packGateRequestId == requestId,
              packOpenedRequestId != requestId,
              transaction.phase == .prepared
        else { return }

        packOpenedRequestId = requestId
        requestStatus = "pack-opened:\(requestId)"
        requestRevealSetupIfNeeded()
    }

    public func startRevealIfNeeded(requestId: String) {
        guard revealIsPresented,
              pendingTransaction?.requestId == requestId,
              revealStartRequestedId != requestId
        else { return }

        revealStartRequestedId = requestId
        requestStatus = "starting-reveal:\(requestId)"
        GachaUnityBridge.send(
            "StartGachaRevealFromNativeUi",
            value: requestId)
        scheduleRevealWatchdog(requestId: requestId, stage: "start")
    }

    public func acknowledgeReveal() {
        guard let transaction = pendingTransaction,
              revealPhase == .complete,
              transaction.phase == .awaitingAcceptance,
              transactionPhase != .acknowledging
        else { return }

        // Leave the completed reveal synchronously so the tap always has a
        // visible result. The durable transaction remains authoritative: if
        // Unity does not confirm the idempotent ACK, the recovery query below
        // restores this same reward instead of starting another draw.
        transactionPhase = .acknowledging
        requestStatus = "acknowledging:\(transaction.requestId)"
        lastFailureReason = ""
        revealIsPresented = false
        CodexSetGachaRevealNativeChromeHidden(false)
        GachaUnityBridge.send(
            "AcknowledgeGachaRevealFromNativeUi",
            value: transaction.requestId)
        scheduleAcknowledgementRecovery(requestId: transaction.requestId)
    }

    public func redeem(prizeId: String) {
        GachaUnityBridge.send("RedeemGachaShardsFromNativeUi", value: prizeId)
    }

    // MARK: TSV ingestion (called from the Unity bridge)

    public func ingest(catalog: String, snapshot: String, receipt: String) {
        let requestBeforeSnapshot = pendingTransaction?.requestId
            ?? activeRequestId
        if !catalog.isEmpty { parseCatalog(catalog) }
        if !snapshot.isEmpty { parseSnapshot(snapshot) }
        let requestAfterSnapshot = pendingTransaction?.requestId
            ?? activeRequestId
        if !receipt.isEmpty {
            let acceptedRequestIds = Set(
                [requestBeforeSnapshot, requestAfterSnapshot]
                    .filter { !$0.isEmpty })
            parseTransactionPayload(
                receipt,
                acceptedRequestIds: acceptedRequestIds)
        }
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
            }
        }
        parseTransactionPayload(payload)
    }

    private func parseTransactionPayload(
        _ payload: String,
        acceptedRequestIds: Set<String>? = nil
    ) {
        guard !payload.isEmpty else { return }
        var rows: [GachaReceiptRow] = []
        var result = ""
        var transactionCells: [String]?
        var sawRuntimeMode = false
        for line in payload.split(separator: "\n") {
            let cells = line.split(separator: "\t", omittingEmptySubsequences: false)
                .map(String.init)
            if cells.count >= 2, cells[0] == "runtime-mode" {
                runtimeMode = GachaRuntimeMode(rawValue: cells[1]) ?? .production
                sawRuntimeMode = true
            } else if cells.count >= 6, cells[0] == "transaction" {
                transactionCells = cells
            } else if cells.count >= 2, cells[0] == "result" {
                result = cells[1]
            } else if cells.count >= 10, cells[0] == "row" {
                rows.append(GachaReceiptRow(
                    prizeId: cells[1],
                    name: cells[2],
                    rarity: GachaRarityTier(rawValue: Int(cells[3]) ?? 0) ?? .standard,
                    kindIndex: Int(cells[4]) ?? 0,
                    isNew: cells[5] == "1",
                    shardsGained: Int(cells[6]) ?? 0,
                    forcedBySignaturePity: cells[7] == "1",
                    forcedByHeirloomPity: cells[8] == "1",
                    forcedByTenDraw: cells[9] == "1"))
            }
        }

        guard let cells = transactionCells else {
            // Older production snapshots do not publish a runtime marker. Keep
            // their economy behavior intact while Build 42 migrates the bridge.
            if !sawRuntimeMode { runtimeMode = .production }
            return
        }

        let requestId = cells[1]
        let phase = GachaTransactionPhase(rawValue: cells[2]) ?? .failed
        let seriesId = cells[3]
        let count = Int(cells[4]) ?? 0
        let payment = cells[5]

        // The snapshot in the same bridge envelope is authoritative. A late
        // query/ACK for historical request A may legally arrive while current
        // request B is pending; that stale receipt must never clear B.
        if let acceptedRequestIds,
           !requestId.isEmpty,
           !acceptedRequestIds.contains(requestId) {
            return
        }

        let wasAcknowledgingHiddenReveal = transactionPhase == .acknowledging
            && !revealIsPresented
        requestTimeoutTask?.cancel()
        requestTimeoutTask = nil
        transactionPhase = phase

        if result == "ok" || result == "none" || result.isEmpty {
            lastFailureReason = ""
        } else {
            lastFailureReason = result
        }

        if phase == .idle || phase == .completed || requestId.isEmpty {
            let wasPresenting = revealIsPresented
            pendingTransaction = nil
            pendingReceipt = []
            activeRequestId = ""
            requestStatus = "idle"
            lastFailureReason = ""
            resetPackState()
            resetRevealState()
            if wasPresenting {
                CodexSetGachaRevealNativeChromeHidden(false)
            }
            return
        }

        if phase == .failed {
            let wasPresenting = revealIsPresented
            pendingTransaction = nil
            pendingReceipt = []
            activeRequestId = ""
            requestStatus = "failed:\(requestId)"
            if lastFailureReason.isEmpty { lastFailureReason = "transaction-failed" }
            resetPackState()
            resetRevealState()
            if wasPresenting {
                CodexSetGachaRevealNativeChromeHidden(false)
            }
            return
        }

        ensureRevealPhaseHistory(requestId: requestId)
        activeRequestId = requestId
        let transaction = GachaPendingTransaction(
            requestId: requestId,
            phase: phase,
            seriesId: seriesId,
            count: count,
            payment: payment,
            receipt: rows)
        pendingTransaction = transaction
        pendingReceipt = rows

        // Only a newly prepared draw is Pack-gated. An awaiting-acceptance
        // transaction has already completed Unity's reveal and must restore
        // that exact reward directly instead of replaying presentation gates.
        if phase == .prepared
            && !revealIsPresented
            && packOpenedRequestId != requestId {
            packGateRequestId = requestId
            requestStatus = "pack-awaiting-open:\(requestId)"
            return
        }

        switch phase {
        case .prepared:
            requestStatus = "prepared:\(requestId)"
            if revealIsPresented && revealPhase != .complete {
                revealStartRequestedId = ""
                startRevealIfNeeded(requestId: requestId)
            } else {
                requestRevealSetupIfNeeded()
            }
        case .awaitingAcceptance:
            packGateRequestId = ""
            requestStatus = "awaiting-acceptance:\(requestId)"
            if wasAcknowledgingHiddenReveal {
                // The ACK was not committed (or Unity explicitly republished
                // awaitingAcceptance). Put back the exact completed reward so
                // the user can retry without rerolling or double-committing.
                revealIsPresented = true
                revealPhase = .complete
                revealStartAcknowledged = true
                lastFailureReason = "acceptance-response-timeout"
                CodexSetGachaRevealNativeChromeHidden(true)
            } else if revealIsPresented && revealStartAcknowledged {
                revealPhase = .complete
                revealWatchdogTask?.cancel()
                revealWatchdogTask = nil
            } else {
                requestRevealSetupIfNeeded()
            }
        default:
            requestStatus = "\(phase.rawValue):\(requestId)"
        }
    }

    public func receiveRevealSetup(
        requestId: String,
        succeeded: Bool,
        failureReason: String
    ) {
        guard pendingTransaction?.requestId == requestId,
              revealSetupRequestedId == requestId
        else { return }

        revealWatchdogTask?.cancel()
        revealWatchdogTask = nil

        guard succeeded else {
            revealSetupRequestedId = ""
            lastFailureReason = failureReason.isEmpty
                ? "reveal-setup-failed"
                : failureReason
            requestStatus = "reveal-setup-failed:\(requestId)"
            return
        }

        packGateRequestId = ""
        revealIsPresented = true
        revealPhase = nil
        revealStartAcknowledged = false
        requestStatus = "reveal-mounted:\(requestId)"
        CodexSetGachaRevealNativeChromeHidden(true)
    }

    public func receiveRevealPhase(
        requestId: String,
        phaseToken: String,
        failureReason: String
    ) {
        guard pendingTransaction?.requestId == requestId,
              revealIsPresented
        else { return }

        guard failureReason.isEmpty,
              let phase = GachaRevealPhase(rawValue: phaseToken)
        else {
            revealWatchdogTask?.cancel()
            revealWatchdogTask = nil
            lastFailureReason = failureReason.isEmpty
                ? "invalid-reveal-phase:\(phaseToken)"
                : failureReason
            requestStatus = "reveal-failed:\(requestId)"
            resetRevealState()
            CodexSetGachaRevealNativeChromeHidden(false)
            return
        }

        revealWatchdogTask?.cancel()
        revealWatchdogTask = nil
        revealStartAcknowledged = true
        recordRevealPhase(phase, requestId: requestId)
        revealPhase = phase
        requestStatus = "reveal-\(phase.rawValue):\(requestId)"
        if phase != .complete {
            scheduleRevealWatchdog(requestId: requestId, stage: "complete")
        }
    }

    private func scheduleQueryTimeout(requestId: String, status: String) {
        requestTimeoutTask?.cancel()
        requestTimeoutTask = Task { [weak self] in
            do {
                try await Task.sleep(nanoseconds: 8_000_000_000)
            } catch {
                return
            }
            guard !Task.isCancelled,
                  let self,
                  self.activeRequestId == requestId,
                  self.requestStatus.hasPrefix(status)
            else { return }

            self.requestStatus = "querying:\(requestId)"
            GachaUnityBridge.send(
                "QueryGachaTransactionFromNativeUi",
                value: requestId)
            self.lastFailureReason = "transaction-response-timeout"
        }
    }

    private func scheduleAcknowledgementRecovery(requestId: String) {
        requestTimeoutTask?.cancel()
        requestTimeoutTask = Task { [weak self] in
            do {
                try await Task.sleep(nanoseconds: 1_000_000_000)
            } catch {
                return
            }
            guard !Task.isCancelled,
                  let self,
                  self.activeRequestId == requestId,
                  self.transactionPhase == .acknowledging,
                  !self.revealIsPresented
            else { return }

            self.requestStatus = "querying:\(requestId)"
            GachaUnityBridge.send(
                "QueryGachaTransactionFromNativeUi",
                value: requestId)
            self.scheduleQueryTimeout(
                requestId: requestId,
                status: "querying")
        }
    }

    private func scheduleRevealWatchdog(requestId: String, stage: String) {
        revealWatchdogTask?.cancel()
        revealWatchdogGeneration += 1
        let generation = revealWatchdogGeneration
        revealWatchdogTask = Task { [weak self] in
            do {
                try await Task.sleep(nanoseconds: 8_000_000_000)
            } catch {
                return
            }
            guard !Task.isCancelled,
                  let self,
                  self.revealWatchdogGeneration == generation,
                  self.pendingTransaction?.requestId == requestId,
                  self.activeRequestId == requestId
            else { return }

            switch stage {
            case "setup":
                guard !self.revealIsPresented,
                      self.revealSetupRequestedId == requestId
                else { return }
                self.revealSetupRequestedId = ""
            case "start":
                guard self.revealIsPresented,
                      !self.revealStartAcknowledged,
                      self.revealStartRequestedId == requestId
                else { return }
                self.revealStartRequestedId = ""
            default:
                guard self.revealIsPresented,
                      self.revealPhase != .complete
                else { return }
            }

            self.lastFailureReason = "reveal-\(stage)-timeout"
            self.requestStatus = "querying:\(requestId)"
            GachaUnityBridge.send(
                "QueryGachaTransactionFromNativeUi",
                value: requestId)
            self.scheduleQueryTimeout(
                requestId: requestId,
                status: "querying")
        }
    }

    private func resetRevealState() {
        revealWatchdogTask?.cancel()
        revealWatchdogTask = nil
        revealWatchdogGeneration += 1
        revealPhase = nil
        revealIsPresented = false
        revealStartAcknowledged = false
        revealSetupRequestedId = ""
        revealStartRequestedId = ""
        revealPhaseHistory = []
        revealPhaseHistoryRequestId = ""
    }

    private func resetPackState() {
        packGateRequestId = ""
        packOpenedRequestId = ""
    }

    private func beginRevealPhaseHistory(requestId: String) {
        revealPhaseHistoryRequestId = requestId
        revealPhaseHistory = []
    }

    private func ensureRevealPhaseHistory(requestId: String) {
        if revealPhaseHistoryRequestId != requestId {
            beginRevealPhaseHistory(requestId: requestId)
        }
    }

    private func recordRevealPhase(
        _ phase: GachaRevealPhase,
        requestId: String
    ) {
        ensureRevealPhaseHistory(requestId: requestId)
        // Unity may republish its current phase while the native watchdog
        // queries the same transaction. Consecutive duplicates are transport
        // retries, not a second animation stage.
        if revealPhaseHistory.last != phase {
            revealPhaseHistory.append(phase)
        }
    }

    private func localizedFailure(_ reason: String) -> String {
        switch reason {
        case "insufficient-tickets": return "抽取券不足，当前无法单抽。"
        case "ten-draw-disabled": return "十抽尚未开放。"
        case "transaction-already-pending": return "上一笔抽取尚未确认，请先完成揭晓。"
        case "transaction-response-timeout": return "抽取响应超时；只会查询原交易，不会重新抽取。"
        case "acceptance-response-timeout": return "收下确认未完成，已恢复本次奖励，可再次尝试。"
        case "reveal-setup-failed": return "3D 揭晓准备失败，可查询原交易后重试。"
        case "reveal-setup-timeout": return "3D 揭晓准备超时；正在查询原交易。"
        case "reveal-start-timeout": return "3D 揭晓启动超时；正在恢复同一笔交易。"
        case "reveal-complete-timeout": return "3D 揭晓完成回包超时；正在查询同一笔交易。"
        case "scene-changed", "model-selection-changed":
            return "模型场景已变化；请查询原交易后重新揭晓。"
        default: return "抽取未完成：\(reason)"
        }
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
    _ requestId: UnsafePointer<CChar>?,
    _ succeeded: Int32,
    _ failureReason: UnsafePointer<CChar>?
) {
    let decodedRequestId = requestId.map { String(cString: $0) } ?? ""
    let decodedFailure = failureReason.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.receiveRevealSetup(
            requestId: decodedRequestId,
            succeeded: succeeded != 0,
            failureReason: decodedFailure)
    }
}

@_cdecl("CodexGachaRevealReceivePhase")
public func CodexGachaRevealReceivePhase(
    _ requestId: UnsafePointer<CChar>?,
    _ phase: UnsafePointer<CChar>?,
    _ failureReason: UnsafePointer<CChar>?
) {
    let decodedRequestId = requestId.map { String(cString: $0) } ?? ""
    let decodedPhase = phase.map { String(cString: $0) } ?? ""
    let decodedFailure = failureReason.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.receiveRevealPhase(
            requestId: decodedRequestId,
            phaseToken: decodedPhase,
            failureReason: decodedFailure)
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
