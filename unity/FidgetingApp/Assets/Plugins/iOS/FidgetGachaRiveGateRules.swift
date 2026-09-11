import Foundation

struct GachaSingleDrawGateState {
    enum Phase: String {
        case choosingPack
        case selectionRive
        case tearPack
        case waitingForReceipt
        case preparingCase
        case handoff
        case complete
        case receiptRecovery
    }

    static let riveWatchdogNanoseconds: UInt64 = 8_000_000_000
    static let reduceMotionDelayNanoseconds: UInt64 = 120_000_000
    static let receiptTimeoutNanoseconds: UInt64 = 20_000_000_000

    private(set) var transactionID: UUID?
    private(set) var phase: Phase = .choosingPack
    private(set) var selectionFinished = false
    private(set) var packCommitted = false
    private(set) var receiptArrived = false
    private(set) var unityCaseReady = false
    private(set) var revealStarted = false
    private(set) var revealCompleted = false
    private(set) var acknowledgementSent = false

    var allowsLiveCaseAperture: Bool {
        GachaPackHandoffRules.canRevealLiveCase(
            hasAuthoritativeReceipt: receiptArrived,
            caseStableAfterTwoFrames: unityCaseReady,
            openingProgress: GachaPackOpeningRules.tearCommitProgress)
    }

    mutating func begin(transactionID: UUID) -> Bool {
        guard self.transactionID == nil else { return false }
        self.transactionID = transactionID
        phase = .selectionRive
        return true
    }

    mutating func restorePending(transactionID: UUID) {
        self.transactionID = transactionID
        selectionFinished = true
        packCommitted = true
        receiptArrived = true
        phase = .preparingCase
    }

    mutating func markSelectionFinished(transactionID: UUID) -> Bool {
        guard accepts(transactionID), !selectionFinished else { return false }
        selectionFinished = true
        phase = packCommitted ? .waitingForReceipt : .tearPack
        advanceIfReady()
        return true
    }

    mutating func markPackCommitted(transactionID: UUID) -> Bool {
        guard accepts(transactionID), !packCommitted else { return false }
        packCommitted = true
        phase = selectionFinished ? .waitingForReceipt : .selectionRive
        advanceIfReady()
        return true
    }

    mutating func markReceiptArrived(requestID: String) -> Bool {
        guard accepts(requestID), !receiptArrived else { return false }
        receiptArrived = true
        advanceIfReady()
        return true
    }

    mutating func markReceiptTimeout(transactionID: UUID) -> Bool {
        guard accepts(transactionID), !receiptArrived, !unityCaseReady else {
            return false
        }
        phase = .receiptRecovery
        return true
    }

    mutating func markUnityCaseReady(transactionID: UUID) -> Bool {
        guard accepts(transactionID),
              receiptArrived,
              packCommitted,
              selectionFinished,
              !unityCaseReady else { return false }
        unityCaseReady = true
        phase = .handoff
        return true
    }

    mutating func markRevealStarted(transactionID: UUID) -> Bool {
        guard accepts(transactionID),
              unityCaseReady,
              !revealStarted else { return false }
        revealStarted = true
        return true
    }

    mutating func markRevealCompleted(requestID: String) -> Bool {
        guard accepts(requestID),
              unityCaseReady,
              revealStarted,
              !revealCompleted else {
            return false
        }
        revealCompleted = true
        phase = .complete
        return true
    }

    mutating func markAcknowledgementSent(transactionID: UUID) -> Bool {
        guard accepts(transactionID),
              revealCompleted,
              !acknowledgementSent else { return false }
        acknowledgementSent = true
        return true
    }

    mutating func reset() {
        self = GachaSingleDrawGateState()
    }

    private func accepts(_ transactionID: UUID) -> Bool {
        self.transactionID == transactionID
    }

    private func accepts(_ requestID: String) -> Bool {
        transactionID?.uuidString.lowercased() == requestID.lowercased()
    }

    private mutating func advanceIfReady() {
        if selectionFinished && packCommitted && receiptArrived {
            phase = .preparingCase
        }
    }
}
