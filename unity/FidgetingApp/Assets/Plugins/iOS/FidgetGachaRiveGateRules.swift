import Foundation

/// Pure, deterministic coordination for a single draw. Pack selection is only
/// presentation metadata: it never enters the Unity draw request and therefore
/// cannot select prize rarity, pool, price or odds.
struct GachaSingleDrawGateState: Equatable {
    enum Phase: Equatable {
        case idle
        case choosingPack
        case selectionRive
        case tearPack
        case preparingCase
        case waitingForReceipt
        case receiptRecovery
        case handoff
    }

    enum Decision: Equatable {
        case idle
        case waiting
        case reveal
        case failure(String)
    }

    static let receiptTimeoutNanoseconds: UInt64 = 20_000_000_000
    static let riveWatchdogNanoseconds: UInt64 = 12_000_000_000
    static let reduceMotionDelayNanoseconds: UInt64 = 120_000_000
    static let packToCaseTransitionSeconds: Double = 0.28

    private(set) var transactionID: UUID?
    private(set) var phase: Phase = .idle
    private(set) var selectedPackTier: GachaPackTier = .standard
    private(set) var drawRequested = false
    private(set) var selectionAnimationFinished = false
    private(set) var packCommitted = false
    private(set) var authoritativeReceiptArrived = false
    private(set) var awaitingReceiptRecovery = false
    private(set) var handoffDispatched = false
    private(set) var unityCaseReady = false
    private(set) var failureReason: String?

    var animationFinished: Bool { packCommitted }

    mutating func begin(transactionID: UUID) {
        self.transactionID = transactionID
        phase = .choosingPack
        selectedPackTier = .standard
        drawRequested = false
        selectionAnimationFinished = false
        packCommitted = false
        authoritativeReceiptArrived = false
        awaitingReceiptRecovery = false
        handoffDispatched = false
        unityCaseReady = false
        failureReason = nil
    }

    @discardableResult
    mutating func selectPack(
        _ tier: GachaPackTier,
        transactionID: UUID
    ) -> Bool {
        guard self.transactionID == transactionID,
              phase == .choosingPack,
              failureReason == nil else { return false }
        selectedPackTier = tier
        return true
    }

    /// Returns true exactly once. The caller must send the authoritative Unity
    /// draw only when this transition succeeds.
    @discardableResult
    mutating func commitPackSelection(transactionID: UUID) -> Bool {
        guard self.transactionID == transactionID,
              phase == .choosingPack,
              !drawRequested,
              failureReason == nil else { return false }
        drawRequested = true
        phase = .selectionRive
        return true
    }

    @discardableResult
    mutating func markSelectionAnimationFinished(
        transactionID: UUID
    ) -> Bool {
        guard self.transactionID == transactionID,
              drawRequested,
              phase == .selectionRive,
              failureReason == nil else { return false }
        selectionAnimationFinished = true
        phase = .tearPack
        return true
    }

    @discardableResult
    mutating func markPackCommitted(transactionID: UUID) -> Bool {
        guard self.transactionID == transactionID,
              selectionAnimationFinished,
              phase == .tearPack,
              !packCommitted,
              failureReason == nil else { return false }
        packCommitted = true
        phase = authoritativeReceiptArrived ? .preparingCase : .waitingForReceipt
        return true
    }

    @discardableResult
    mutating func markAnimationFinished(transactionID: UUID) -> Bool {
        guard self.transactionID == transactionID,
              drawRequested,
              failureReason == nil else {
            return false
        }
        // Older deterministic callers do not model the two visual stages. Keep
        // that API safe by advancing through neutral presentation milestones;
        // shipping code calls each explicit transition above.
        if phase == .selectionRive {
            selectionAnimationFinished = true
            phase = .tearPack
        }
        if phase == .tearPack {
            packCommitted = true
            phase = authoritativeReceiptArrived
                ? .preparingCase
                : .waitingForReceipt
        }
        return packCommitted
    }

    @discardableResult
    mutating func markReceiptArrived(transactionID: UUID) -> Bool {
        guard self.transactionID == transactionID, failureReason == nil else {
            return false
        }
        authoritativeReceiptArrived = true
        awaitingReceiptRecovery = false
        if packCommitted && !handoffDispatched {
            phase = .preparingCase
        }
        return true
    }

    @discardableResult
    mutating func markReceiptTimedOut(transactionID: UUID) -> Bool {
        guard self.transactionID == transactionID,
              !authoritativeReceiptArrived,
              failureReason == nil else { return false }
        awaitingReceiptRecovery = true
        // Recovery is orthogonal to the visible Pack. Keep the same object on
        // screen until Unity confirms that the real case is ready behind it.
        return true
    }

    @discardableResult
    mutating func markHandoffDispatched(transactionID: UUID) -> Bool {
        guard self.transactionID == transactionID,
              decision(transactionID: transactionID) == .reveal,
              !handoffDispatched else { return false }
        handoffDispatched = true
        return true
    }

    @discardableResult
    mutating func markUnityCaseReady(transactionID: UUID) -> Bool {
        guard self.transactionID == transactionID,
              handoffDispatched,
              !unityCaseReady,
              failureReason == nil else { return false }
        unityCaseReady = true
        phase = .handoff
        return true
    }

    @discardableResult
    mutating func fail(transactionID: UUID, reason: String) -> Bool {
        guard self.transactionID == transactionID else { return false }
        failureReason = reason
        return true
    }

    func decision(transactionID: UUID) -> Decision {
        guard self.transactionID == transactionID else { return .idle }
        if let failureReason, !failureReason.isEmpty {
            return .failure(failureReason)
        }
        return packCommitted
            && authoritativeReceiptArrived
            && !handoffDispatched
            ? .reveal
            : .waiting
    }

    mutating func clear() {
        transactionID = nil
        phase = .idle
        selectedPackTier = .standard
        drawRequested = false
        selectionAnimationFinished = false
        packCommitted = false
        authoritativeReceiptArrived = false
        awaitingReceiptRecovery = false
        handoffDispatched = false
        unityCaseReady = false
        failureReason = nil
    }
}
