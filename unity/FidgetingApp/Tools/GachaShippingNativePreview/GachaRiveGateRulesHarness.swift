import Foundation

@main
struct GachaRiveGateRulesHarness {
    private static var assertions = 0

    static func main() throws {
        let transactionA = UUID(uuidString: "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA")!
        let transactionB = UUID(uuidString: "BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB")!

        var continuousPackToHolder = GachaSingleDrawGateState()
        continuousPackToHolder.begin(transactionID: transactionA)
        try expect(continuousPackToHolder.selectPack(
            .signature,
            transactionID: transactionA))
        try expect(continuousPackToHolder.commitPackSelection(
            transactionID: transactionA))
        try expect(continuousPackToHolder.markSelectionAnimationFinished(
            transactionID: transactionA))
        try expect(continuousPackToHolder.phase == .tearPack)
        try expect(!continuousPackToHolder.markHolderAnimationFinished(
            transactionID: transactionA))
        try expect(continuousPackToHolder.markPackCommitted(
            transactionID: transactionA))
        try expect(continuousPackToHolder.phase == .holderRive)
        try expect(continuousPackToHolder.transactionID == transactionA)
        try expect(continuousPackToHolder.selectedPackTier == .signature)
        try expect(continuousPackToHolder.markReceiptArrived(
            transactionID: transactionA))
        try expect(continuousPackToHolder.markHolderAnimationFinished(
            transactionID: transactionA))
        try expect(!continuousPackToHolder.markHolderAnimationFinished(
            transactionID: transactionA))
        try expect(continuousPackToHolder.decision(
            transactionID: transactionA) == .reveal)

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
            .holderRive,
            .waitingForReceipt
        ]
        for checkpoint in recoveryCheckpoints {
            var recovery = GachaSingleDrawGateState()
            recovery.begin(transactionID: transactionA)
            try expect(recovery.commitPackSelection(
                transactionID: transactionA))
            if checkpoint == .tearPack
                || checkpoint == .holderRive
                || checkpoint == .waitingForReceipt {
                try expect(recovery.markSelectionAnimationFinished(
                    transactionID: transactionA))
            }
            if checkpoint == .holderRive || checkpoint == .waitingForReceipt {
                try expect(recovery.markPackCommitted(
                    transactionID: transactionA))
            }
            if checkpoint == .waitingForReceipt {
                try expect(recovery.markAnimationFinished(
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
                try expect(recovery.phase == .handoff)
            } else {
                try expect(recovery.phase == visualPhaseBeforeTimeout)
                try expect(recovery.markAnimationFinished(
                    transactionID: transactionA))
            }
            try expect(recovery.decision(transactionID: transactionA) == .reveal)
        }

        try expect(GachaSingleDrawGateState.receiptTimeoutNanoseconds == 20_000_000_000)
        try expect(GachaSingleDrawGateState.riveWatchdogNanoseconds == 12_000_000_000)
        try expect(GachaSingleDrawGateState.packToHolderTransitionSeconds == 0.28)

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
