import Foundation

@main
struct GachaRiveGateRulesHarness {
    private static var assertions = 0

    static func main() throws {
        let transactionA = UUID(uuidString: "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA")!
        let transactionB = UUID(uuidString: "BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB")!

        var continuousPackToCase = GachaSingleDrawGateState()
        continuousPackToCase.begin(transactionID: transactionA)
        try expect(continuousPackToCase.selectPack(
            .signature,
            transactionID: transactionA))
        try expect(continuousPackToCase.commitPackSelection(
            transactionID: transactionA))
        try expect(continuousPackToCase.markSelectionAnimationFinished(
            transactionID: transactionA))
        try expect(continuousPackToCase.phase == .tearPack)
        try expect(!continuousPackToCase.markUnityCaseReady(
            transactionID: transactionA))
        try expect(continuousPackToCase.markPackCommitted(
            transactionID: transactionA))
        try expect(continuousPackToCase.phase == .waitingForReceipt)
        try expect(continuousPackToCase.transactionID == transactionA)
        try expect(continuousPackToCase.selectedPackTier == .signature)
        try expect(continuousPackToCase.markReceiptArrived(
            transactionID: transactionA))
        try expect(continuousPackToCase.phase == .preparingCase)
        try expect(continuousPackToCase.decision(
            transactionID: transactionA) == .reveal)
        try expect(continuousPackToCase.markHandoffDispatched(
            transactionID: transactionA))
        try expect(continuousPackToCase.markUnityCaseReady(
            transactionID: transactionA))
        try expect(continuousPackToCase.phase == .handoff)
        try expect(!continuousPackToCase.markUnityCaseReady(
            transactionID: transactionA))

        var receiptFirst = GachaSingleDrawGateState()
        receiptFirst.begin(transactionID: transactionA)
        try expect(receiptFirst.commitPackSelection(transactionID: transactionA))
        try expect(receiptFirst.markReceiptArrived(transactionID: transactionA))
        try expect(receiptFirst.decision(transactionID: transactionA) == .waiting)
        try expect(receiptFirst.markAnimationFinished(transactionID: transactionA))
        try expect(receiptFirst.decision(transactionID: transactionA) == .reveal)

        var animationFirst = GachaSingleDrawGateState()
        animationFirst.begin(transactionID: transactionA)
        try expect(animationFirst.commitPackSelection(transactionID: transactionA))
        try expect(animationFirst.markAnimationFinished(transactionID: transactionA))
        try expect(animationFirst.decision(transactionID: transactionA) == .waiting)
        try expect(animationFirst.markReceiptArrived(transactionID: transactionA))
        try expect(animationFirst.decision(transactionID: transactionA) == .reveal)

        var staleCallback = GachaSingleDrawGateState()
        staleCallback.begin(transactionID: transactionA)
        try expect(staleCallback.commitPackSelection(transactionID: transactionA))
        try expect(!staleCallback.markAnimationFinished(transactionID: transactionB))
        try expect(!staleCallback.markReceiptArrived(transactionID: transactionB))
        try expect(staleCallback.decision(transactionID: transactionA) == .waiting)

        var failure = GachaSingleDrawGateState()
        failure.begin(transactionID: transactionA)
        try expect(failure.commitPackSelection(transactionID: transactionA))
        try expect(failure.fail(transactionID: transactionA, reason: "authoritative failure"))
        try expect(
            failure.decision(transactionID: transactionA)
                == .failure("authoritative failure"))
        try expect(!failure.markAnimationFinished(transactionID: transactionA))
        try expect(!failure.markReceiptArrived(transactionID: transactionA))

        failure.clear()
        try expect(failure.decision(transactionID: transactionA) == .idle)

        let recoveryCheckpoints: [GachaSingleDrawGateState.Phase] = [
            .selectionRive,
            .tearPack,
            .waitingForReceipt
        ]
        for checkpoint in recoveryCheckpoints {
            var recovery = GachaSingleDrawGateState()
            recovery.begin(transactionID: transactionA)
            try expect(recovery.commitPackSelection(
                transactionID: transactionA))
            if checkpoint == .tearPack || checkpoint == .waitingForReceipt {
                try expect(recovery.markSelectionAnimationFinished(
                    transactionID: transactionA))
            }
            if checkpoint == .waitingForReceipt {
                try expect(recovery.markPackCommitted(
                    transactionID: transactionA))
            }

            let visualPhaseBeforeTimeout = recovery.phase
            try expect(recovery.markReceiptTimedOut(
                transactionID: transactionA))
            try expect(recovery.awaitingReceiptRecovery)
            try expect(recovery.phase == visualPhaseBeforeTimeout)
            try expect(recovery.markReceiptArrived(
                transactionID: transactionA))
            try expect(!recovery.awaitingReceiptRecovery)
            if checkpoint == .waitingForReceipt {
                try expect(recovery.phase == .preparingCase)
            } else {
                try expect(recovery.phase == visualPhaseBeforeTimeout)
                try expect(recovery.markAnimationFinished(
                    transactionID: transactionA))
            }
            try expect(recovery.decision(transactionID: transactionA) == .reveal)
            try expect(recovery.markHandoffDispatched(
                transactionID: transactionA))
            try expect(recovery.markUnityCaseReady(
                transactionID: transactionA))
            try expect(recovery.phase == .handoff)
        }

        try expect(GachaSingleDrawGateState.receiptTimeoutNanoseconds == 20_000_000_000)
        try expect(GachaSingleDrawGateState.riveWatchdogNanoseconds == 12_000_000_000)
        try expect(GachaSingleDrawGateState.packToCaseTransitionSeconds == 0.28)

        print("Gacha Rive gate harness: \(assertions)/\(assertions) passed")
    }

    private static func expect(
        _ condition: @autoclosure () -> Bool,
        file: StaticString = #filePath,
        line: UInt = #line
    ) throws {
        assertions += 1
        guard condition() else {
            throw HarnessError.assertionFailed("\(file):\(line)")
        }
    }

    private enum HarnessError: Error {
        case assertionFailed(String)
    }
}
