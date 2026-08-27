import Foundation
import XCTest

@MainActor
final class GachaContinuousPreviewUITests: XCTestCase {
    private enum AX {
        static let storeEntry = "gacha-store-entry"
        static let storeRoot = "gacha-store-root"
        static let singleDraw = "gacha-single-draw"
        static let carousel = "gacha-pack-carousel"
        static let select = "gacha-pack-select"
        static let selectedTier = "gacha-pack-tier-signature"
        static let selectionRive = "gacha-selection-rive"
        static let tearTarget = "gacha-pack-tear-target"
        static let packState = "gacha-pack-state"
        static let packCaseTransition = "gacha-pack-case-transition"
        static let revealRoot = "gacha-3d-reveal-root"
        static let revealAccept = "gacha-reveal-accept"
    }

    private let bundleIdentifier = "com.jiaweizhou.fidgetspinner.codex"
    private let expectedWidth: CGFloat = 393
    private let expectedHeight: CGFloat = 852
    private let expectedModelID = "metal-three-blade"
    private let expectedPrizeID = "canyon-heir-metal-three-blade"
    private let expectedPrizeKind = "Toy"
    private let expectedContentReference = "toy/metal-three-blade"
    private var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testRecordShippingCarouselRivePackAndRealUnityReveal() throws {
        app = XCUIApplication(bundleIdentifier: bundleIdentifier)
        app.launchArguments = [
            "--gacha-pack-trace",
            "--preview-pack-tier=signature",
            "--preview-gacha-funding-token=metal-three-blade-v1",
            "--preview-authoritative-metal-three-blade",
            "--preview-continuous-gacha-evidence"
        ]
        app.launchEnvironment["FIDGET_GACHA_XCUI"] = "1"
        app.launch()

        XCTAssertTrue(app.wait(for: .runningForeground, timeout: 30))
        XCTAssertEqual(app.frame.width, expectedWidth, accuracy: 0.5)
        XCTAssertEqual(app.frame.height, expectedHeight, accuracy: 0.5)
        print("[ContinuousHarness] viewport=\(app.frame.width)x\(app.frame.height)")

        dismissOnboardingIfNeeded()
        let identifiedStoreEntry = element(AX.storeEntry)
        let labelledStoreEntry = app.buttons["盲盒"]
        waitUntil(timeout: 30, message: "shipping gacha entry is unavailable") {
            (identifiedStoreEntry.exists && identifiedStoreEntry.isHittable)
                || (labelledStoreEntry.exists && labelledStoreEntry.isHittable)
        }
        if identifiedStoreEntry.exists && identifiedStoreEntry.isHittable {
            identifiedStoreEntry.tap()
        } else {
            labelledStoreEntry.tap()
        }

        let storeRoot = element(AX.storeRoot)
        let storeReturn = element("gacha-return-home")
        waitUntil(timeout: 30, message: "shipping gacha storefront did not mount") {
            storeRoot.exists || storeReturn.exists
        }

        let singleDraw = element(AX.singleDraw)
        waitUntil(timeout: 20, message: "shipping single-draw action is unavailable") {
            singleDraw.exists && singleDraw.isHittable && singleDraw.isEnabled
        }
        singleDraw.tap()

        let carousel = element(AX.carousel)
        let carouselTitle = element(label: "选择 PACK")
        waitUntil(timeout: 10, message: "six-tier Pack carousel did not mount") {
            carousel.exists || carouselTitle.exists
        }
        let tierLabels = [
            "standard": "STANDARD Pack",
            "refined": "REFINED Pack",
            "signature": "SIGNATURE Pack",
            "chase": "CHASE Pack",
            "grail": "GRAIL Pack",
            "one-of-one": "1 OF 1 Pack"
        ]
        for tier in ["standard", "refined", "signature", "chase", "grail", "one-of-one"] {
            XCTAssertTrue(
                element("gacha-pack-tier-\(tier)").exists
                    || app.buttons[tierLabels[tier]!].exists,
                "Pack carousel is missing tier \(tier)")
        }
        let carouselFrame = carousel.exists ? carousel.frame : carouselTitle.frame
        print("[ContinuousHarness] carousel tiers=6 frame=\(carouselFrame)")

        let selectedTier = element(AX.selectedTier)
        let selectedTierLabel = app.buttons["SIGNATURE Pack"]
        waitUntil(timeout: 5, message: "preview-controlled signature tier is unavailable") {
            (selectedTier.exists && selectedTier.isHittable)
                || (selectedTierLabel.exists && selectedTierLabel.isHittable)
        }
        if selectedTier.exists && selectedTier.isHittable {
            selectedTier.tap()
        } else {
            selectedTierLabel.tap()
        }
        // Preserve a real, recordable carousel beat after SIGNATURE is
        // centered. This is deliberately longer than the 1.2 s visual gate so
        // the shipping video proves center + both neighbouring Packs, not only
        // an accessibility-tree snapshot.
        print("[ContinuousHarness] carousel-visible-hold=2.0 tier=SIGNATURE")
        sleep(2)
        let select = element(AX.select)
        let labelledSelect = app.buttons["选择 SIGNATURE"]
        waitUntil(timeout: 5, message: "Pack selection action is unavailable") {
            (select.exists && select.isHittable && select.isEnabled)
                || (labelledSelect.exists && labelledSelect.isHittable
                    && labelledSelect.isEnabled)
        }
        if select.exists && select.isHittable && select.isEnabled {
            select.tap()
        } else {
            labelledSelect.tap()
        }

        let selectionRive = element(AX.selectionRive)
        let selectionCue = element(label: "包装已选中")
        let selectionTitle = element(label: "PACK SELECTED")
        XCTAssertTrue(
            waitForAnyExistence(
                [selectionRive, selectionCue, selectionTitle],
                timeout: 5),
            "neutral selection Rive cue never mounted")
        waitUntil(timeout: 15, message: "neutral selection Rive cue did not complete") {
            !selectionRive.exists && !selectionCue.exists && !selectionTitle.exists
        }

        let identifiedPack = element(AX.tearTarget)
        let labelledPack = element(label: "SIGNATURE 抽取包装")
        waitUntil(timeout: 15, message: "selected shipping Pack never mounted") {
            (identifiedPack.exists && identifiedPack.isHittable)
                || labelledPack.exists
        }
        let pack = identifiedPack.exists ? identifiedPack : labelledPack
        print("[ContinuousHarness] sealed-pack-frame=\(pack.frame)")

        // 121 / 220 = 0.55: below the frozen 0.62 production threshold.
        let belowStart = pack.coordinate(
            withNormalizedOffset: CGVector(dx: 0.20, dy: 0.50))
        let belowEnd = belowStart.withOffset(CGVector(dx: 121, dy: 0))
        belowStart.press(
            forDuration: 0.08,
            thenDragTo: belowEnd,
            withVelocity: .slow,
            thenHoldForDuration: 0.10)
        sleep(1)
        XCTAssertTrue(pack.exists, "Pack committed below the 0.62 threshold")
        waitForMarker(
            AX.packState,
            fallbackLabel: "Pack state",
            equalTo: "sealed",
            timeout: 4,
            message: "Pack did not finish its one allowed rebound")
        print("[ContinuousHarness] tear-rebound progress=0.55 threshold=0.62")

        // 165 / 220 = 0.75: above the frozen 0.62 production threshold.
        let commitStart = pack.coordinate(
            withNormalizedOffset: CGVector(dx: 0.20, dy: 0.50))
        let commitEnd = commitStart.withOffset(CGVector(dx: 165, dy: 0))
        commitStart.press(
            forDuration: 0.08,
            thenDragTo: commitEnd,
            withVelocity: .slow,
            thenHoldForDuration: 0.10)
        XCTAssertTrue(
            element(AX.packCaseTransition).exists,
            "Pack-to-case transition surface disappeared before Unity was ready")
        XCTAssertTrue(
            pack.waitForNonExistence(timeout: 10),
            "Pack did not commit and exit above the 0.62 threshold")
        print("[ContinuousHarness] tear-commit progress=0.75 threshold=0.62")

        let revealRoot = element(AX.revealRoot)
        waitUntil(timeout: 15, message: "real Unity reveal root never mounted") {
            revealRoot.exists
        }
        let revealIdentity = accessibleText(revealRoot)
        XCTAssertTrue(
            revealIdentity.contains(expectedModelID),
            "real Unity root does not identify \(expectedModelID): \(revealIdentity)")
        XCTAssertTrue(
            revealIdentity.contains("prizeId=\(expectedPrizeID)"),
            "real Unity root does not identify authoritative prize \(expectedPrizeID): "
                + revealIdentity)
        print(
            "[ContinuousHarness] real3dRoot=true model=\(expectedModelID) "
                + "prize=\(expectedPrizeID) kind=\(expectedPrizeKind) "
                + "contentReference=\(expectedContentReference)")

        let accept = element(AX.revealAccept)
        waitUntil(timeout: 8, message: "standard 收下 action never became available") {
            accept.exists && accept.isHittable && accept.isEnabled
        }
        XCTAssertTrue(revealRoot.exists, "real Unity composition disappeared early")
        print("[ContinuousHarness] unity-reveal assembled=true accept-ready=true")
        accept.tap()
        XCTAssertTrue(
            revealRoot.waitForNonExistence(timeout: 8),
            "accepted Unity reveal did not close")
    }

    private func dismissOnboardingIfNeeded() {
        let skip = app.buttons["跳过"]
        if skip.waitForExistence(timeout: 2), skip.isHittable {
            skip.tap()
        }
    }

    private func element(_ identifier: String) -> XCUIElement {
        app.descendants(matching: .any)
            .matching(identifier: identifier)
            .firstMatch
    }

    private func element(label: String) -> XCUIElement {
        app.descendants(matching: .any)
            .matching(NSPredicate(format: "label == %@", label))
            .firstMatch
    }

    private func waitForAnyExistence(
        _ elements: [XCUIElement],
        timeout: TimeInterval
    ) -> Bool {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline {
            if elements.contains(where: { $0.exists }) { return true }
            RunLoop.current.run(until: Date().addingTimeInterval(0.10))
        }
        return elements.contains(where: { $0.exists })
    }

    private func markerValue(_ identifier: String) -> String {
        let marker = element(identifier)
        guard marker.exists else { return "<missing>" }
        if let value = marker.value as? String { return value }
        guard let value = marker.value else { return "" }
        return String(describing: value)
    }

    private func accessibleText(_ element: XCUIElement) -> String {
        let value = element.value.map(String.init(describing:)) ?? ""
        return [element.label, value]
            .filter { !$0.isEmpty }
            .joined(separator: "|")
    }

    private func waitForMarker(
        _ identifier: String,
        fallbackLabel: String? = nil,
        equalTo expected: String,
        timeout: TimeInterval,
        message: String
    ) {
        waitUntil(timeout: timeout, message: message) {
            if self.markerValue(identifier) == expected { return true }
            guard let fallbackLabel else { return false }
            let fallback = self.element(label: fallbackLabel)
            guard fallback.exists else { return false }
            return (fallback.value.map(String.init(describing:)) ?? "") == expected
        }
    }

    private func waitUntil(
        timeout: TimeInterval,
        message: String,
        poll: TimeInterval = 0.10,
        condition: () -> Bool
    ) {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline {
            if condition() { return }
            RunLoop.current.run(until: Date().addingTimeInterval(poll))
        }
        XCTFail("\(message). Hierarchy:\n\(app.debugDescription)")
    }
}
