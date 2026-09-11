import Foundation

@main
enum GachaGate12RulesHarness {
    static func main() {
        var assertions = 0

        func expect(
            _ condition: @autoclosure () -> Bool,
            _ message: String
        ) {
            assertions += 1
            guard condition() else {
                fputs("FAIL: \(message)\n", stderr)
                exit(1)
            }
        }

        let request = UUID(
            uuidString: "F6217A76-B92D-43FD-8D25-17F9E707C1AF")!
        let stale = UUID(
            uuidString: "A5B147A0-3782-44EF-A40B-30D71DD1A8EA")!
        var gate = GachaSingleDrawGateState()

        expect(gate.phase == .choosingPack, "starts at Pack selection")
        expect(gate.begin(transactionID: request), "starts one request")
        expect(!gate.begin(transactionID: stale), "blocks re-entry")
        expect(gate.phase == .selectionRive, "selection cue precedes tear")
        expect(
            gate.markSelectionFinished(transactionID: request),
            "finishes selection once")
        expect(gate.phase == .tearPack, "tear follows selection")
        expect(
            !gate.markReceiptArrived(
                requestID: stale.uuidString.lowercased()),
            "rejects stale receipt")
        expect(
            gate.markPackCommitted(transactionID: request),
            "commits Pack once")
        expect(
            !gate.markPackCommitted(transactionID: request),
            "Pack commit is exact-once")
        expect(gate.phase == .waitingForReceipt, "waits for authority")
        expect(
            gate.markReceiptArrived(
                requestID: request.uuidString.lowercased()),
            "accepts same-request receipt")
        expect(gate.phase == .preparingCase, "prepares real case")
        expect(
            gate.markUnityCaseReady(transactionID: request),
            "real case unlocks handoff")
        expect(gate.phase == .handoff, "Pack hands off after readiness")
        expect(
            !gate.markRevealStarted(transactionID: stale),
            "stale request cannot start reveal")
        expect(
            gate.markRevealStarted(transactionID: request),
            "Pack retreat starts the same-request Unity reveal")
        expect(
            !gate.markRevealStarted(transactionID: request),
            "Unity reveal starts exactly once")
        expect(
            gate.markRevealCompleted(
                requestID: request.uuidString.lowercased()),
            "Unity completion unlocks result")
        expect(gate.phase == .complete, "ends in static complete")
        expect(
            gate.markAcknowledgementSent(transactionID: request),
            "acknowledges once")
        expect(
            !gate.markAcknowledgementSent(transactionID: request),
            "duplicate acknowledgement is blocked")
        expect(
            !GachaPackOpeningRules.shouldCommit(progress: 0.619),
            "tear below threshold rebounds")
        let reboundProgress = GachaPackOpeningRules.shouldCommit(
            progress: 0.619) ? 0.619 : 0
        expect(
            GachaPackOpeningRules.openingMaskAreaSquarePoints(
                progress: reboundProgress) == 0,
            "precommit rebound restores the sealed mouth")
        expect(
            GachaPackOpeningRules.shouldCommit(progress: 0.62),
            "tear threshold commits")
        expect(
            GachaPackOpeningRules.openingMaskAreaSquarePoints(
                progress: GachaPackOpeningRules.tearCommitProgress) > 300,
            "committed tear creates a nonzero aperture area")
        expect(
            GachaPackOpeningRules.isMouthOpen(
                progress: GachaPackOpeningRules.tearCommitProgress),
            "committed tear opens the reusable mouth mask")
        expect(
            !GachaPackOpeningRules.isMouthOpen(progress: reboundProgress),
            "rebound closes the reusable mouth mask")
        expect(
            !GachaPackHandoffRules.canRevealLiveCase(
                hasAuthoritativeReceipt: false,
                caseStableAfterTwoFrames: true,
                openingProgress: GachaPackOpeningRules.tearCommitProgress),
            "case stays hidden without an authoritative receipt")
        expect(
            !GachaPackHandoffRules.canRevealLiveCase(
                hasAuthoritativeReceipt: true,
                caseStableAfterTwoFrames: false,
                openingProgress: GachaPackOpeningRules.tearCommitProgress),
            "case stays hidden before two stable Unity frames")
        expect(
            GachaPackHandoffRules.canRevealLiveCase(
                hasAuthoritativeReceipt: true,
                caseStableAfterTwoFrames: true,
                openingProgress: GachaPackOpeningRules.tearCommitProgress),
            "committed tear authorizes the live case handoff")
        expect(
            !GachaPackHandoffRules.canRevealLiveCase(
                hasAuthoritativeReceipt: true,
                caseStableAfterTwoFrames: true,
                openingProgress: 0.61),
            "precommit tear blocks the live case handoff")
        expect(
            GachaPackHandoffRules.packArtIsForeground(
                packVisible: true,
                retreatProgress: 0),
            "Pack art remains foreground before the case handoff")
        expect(
            GachaPackHandoffRules.nativeHybridSequenceDurationSeconds
                >= 1.0
                && GachaPackHandoffRules.nativeHybridSequenceDurationSeconds
                    <= 1.8,
            "isolated hybrid motion stays within 1.0 to 1.8 seconds")
        expect(
            GachaPackHandoffRules.nativeHybridCaseRiseDurationSeconds == 0.64,
            "the live case has one bounded rise through the mouth")
        expect(
            GachaPackHandoffRules.nativeHybridContainmentHoldNanoseconds
                == 120_000_000
                && GachaPackHandoffRules.drawAfterLidClearNanoseconds == 0
                && GachaPackHandoffRules.caseReadyMinimumAfterCommitNanoseconds
                    == 380_000_000,
            "v2: draw at commit; the pull starts no earlier than T0 + 700 ms")
        expect(
            GachaPackHandoffRules.nativeHybridTearDurationSeconds == 0.32
                && GachaPackOpeningRules.flapExitDurationSeconds == 0.48
                && GachaPackOpeningRules.sealExitLiftPoints == 90
                && GachaPackHandoffRules.nativeHybridPackDepartureDurationSeconds
                    == 0.58
                && GachaPackHandoffRules.packDepartureDropFraction == 0.5
                && GachaPackHandoffRules.packDepartureTiltDegrees == 14,
            "v2 beats: tear 320 ms, seal flight 480 ms / -90 pt, Pack falls 0.58 s / 50% stage / 14°")
        expect(
            GachaPackHandoffRules.packDepartureOpacity(retreatProgress: 0) == 1
                && GachaPackHandoffRules.packDepartureOpacity(retreatProgress: 0.78) == 1
                && GachaPackHandoffRules.packDepartureOpacity(retreatProgress: 0.9) > 0.3
                && GachaPackHandoffRules.packDepartureOpacity(retreatProgress: 0.9) < 0.7
                && GachaPackHandoffRules.packDepartureOpacity(retreatProgress: 1) == 0,
            "the Pack stays solid through the first third of its drop, then fades out")
        expect(
            GachaPackIdleMotion.offsetPoints(elapsed: 0) == 0
                && abs(GachaPackIdleMotion.offsetPoints(elapsed: 1.5) + 3) < 0.001
                && abs(GachaPackIdleMotion.yawDegrees(elapsed: 0.9) - 2) < 0.001
                && GachaPackIdleMotion.yawDegrees(elapsed: 0, amplitude: 0) == 0
                && GachaPackIdleMotion.rampIn(sinceSettle: 0) == 0
                && GachaPackIdleMotion.rampIn(sinceSettle: 0.6) == 1
                && GachaPackIdleMotion.sealSweepProgress(elapsed: 0.3) == nil
                && GachaPackIdleMotion.sealSweepProgress(elapsed: 1.8 + 0.35) != nil
                && GachaPackIdleMotion.sealSweepProgress(elapsed: 1.8 + 0.9) == nil,
            "idle loop: -3 pt at half the float period, +2° at a quarter yaw period, ramp-in, sweep windows")
        expect(
            abs(GachaPackOpeningRules.tearCommitProgress
                * GachaPackOpeningRules.tearTravelPoints
                - 0.40 * GachaPackOpeningRules.artworkWidthPoints) < 1.0,
            "commit lands at 40% of the Pack width")
        expect(
            GachaPackOpeningRules.sealExitOpacity(progress: 0.62) == 1
                && GachaPackOpeningRules.sealExitOpacity(progress: 1) == 0
                && GachaPackOpeningRules.sealExitOpacity(progress: 0.81) > 0.4
                && GachaPackOpeningRules.sealExitOpacity(progress: 0.81) < 0.6,
            "the seal fades across its flight and never hovers")
        expect(
            GachaPackHandoffRules.resultPanelDelayNanoseconds == 300_000_000
                && GachaPackHandoffRules.sealLongPressSeconds == 0.45
                && GachaPackHandoffRules.sealHitAreaHeightPoints == 72
                && GachaPackHandoffRules.selectionScale == 1.18
                && GachaPackHandoffRules.stagePackCenterYFraction == 0.44,
            "v2 triggers and layout: 72 pt seal, 450 ms hold, 1.18× to (50%, 44%)")
        expect(
            GachaNativeHybridStaticStage.parse(arguments: [
                "--premium-display-case-gate04-native-hybrid-static=contained-case"
            ]) == .containedCase,
            "static review can hold the real case inside the mouth")
        expect(
            GachaNativeHybridStaticStage.parse(arguments: [
                "--premium-display-case-gate04-native-hybrid-static=invalid"
            ]) == nil,
            "unknown static review stages remain disabled")
        expect(
            GachaPackOpeningRules.normalizedProgress(
                translationPoints: 90.5) == 0.5,
            "tear progress follows gesture travel (181 pt full travel)")
        expect(
            abs(GachaPackOpeningRules.flapHorizontalOffsetPoints(progress: 0.4)
                - 10.3225806452) < 0.0001,
            "narrow seal peel follows the horizontal seam")
        expect(
            abs(GachaPackOpeningRules.flapVerticalOffsetPoints(progress: 0.4)
                + 6.4516129032) < 0.0001,
            "narrow seal peel lifts from the seam")
        expect(
            abs(GachaPackOpeningRules.flapRotation(progress: 0.4)
                - 2.5806451613) < 0.0001,
            "narrow seal peel curls from the trailing anchor")
        expect(
            GachaPackOpeningRules.flapHorizontalOffsetPoints(progress: 1)
                <= 16,
            "committed peel stays rooted near the Pack edge")
        expect(
            abs(GachaPackOpeningRules.openingHeightPoints(progress: 0.4)
                - 3.2258064516) < 0.0001,
            "opening depth tracks the tear front")
        expect(
            GachaPackOpeningRules.maximumOpeningHeightPoints == 5
                && GachaPackOpeningRules.openingSealLiftPoints == 2.4,
            "mouth is a thin interior sliver; the removed lid is the opening")
        expect(
            abs(GachaPackOpeningRules.tearFrontXFraction(progress: 0.31)
                - 0.5) < 0.0001,
            "tear front moves from the left edge toward the right")
        expect(
            GachaPackOpeningRules.openingFraction(
                horizontalFraction: 0.1,
                progress: 0.31) > 0.9,
            "left side opens behind the tear front")
        expect(
            GachaPackOpeningRules.openingFraction(
                horizontalFraction: 0.95,
                progress: 0.31) == 0,
            "sealed right side stays closed before the front reaches it")
        expect(
            GachaPackOpeningRules.openingHeightPoints(
                horizontalFraction: 0.1,
                progress: 0.31)
                > GachaPackOpeningRules.openingHeightPoints(
                    horizontalFraction: 0.95,
                    progress: 0.31),
            "opening depth is localized to the torn side")
        expect(
            GachaPackOpeningRules.flapOpacity(progress: 0.4) == 1,
            "partial tear keeps the flap readable")
        expect(
            GachaPackOpeningRules.flapOpacity(progress: 1) == 1,
            "committed flap stays physical instead of fading into a sliver")
        expect(
            GachaPackOpeningRules.authoredCanvasWidth
                / GachaPackOpeningRules.authoredCanvasHeight == 0.75,
            "Pack body and flap keep the authored aspect")
        expect(
            GachaPackOpeningRules.releasePulseDurationSeconds == 0.60
                && GachaPackOpeningRules.releaseFlashPeakOpacity == 0
                && GachaPackOpeningRules.releaseBurstStreakCount == 0
                && GachaPackOpeningRules.releaseFlashOpacity(pulseStrength: 1) == 0,
            "v2: no flash or streaks at the tear; the reveal frame owns the burst")
        expect(
            GachaPackOpeningRules.seamLightStrength(
                progress: 0,
                gestureActive: true,
                handoffActive: false,
                retreatProgress: 0) == 0,
            "sealed Pack has no seam leak")
        expect(
            GachaPackOpeningRules.seamLightStrength(
                progress: 0.4,
                gestureActive: true,
                handoffActive: false,
                retreatProgress: 0) > 0.8,
            "partial tear exposes the seam light")
        expect(
            GachaPackOpeningRules.seamLightStrength(
                progress: 1,
                gestureActive: false,
                handoffActive: false,
                retreatProgress: 0) == 0,
            "receipt wait has no persistent light")
        expect(
            GachaPackOpeningRules.seamLightStrength(
                progress: 1,
                gestureActive: false,
                handoffActive: true,
                retreatProgress: 0.5) == 0,
            "handoff does not restart the seam cue")
        expect(
            GachaPackHandoffRules.showsPack(
                revealComplete: false,
                retreatProgress: 0.999),
            "Pack remains foreground until retreat completes")
        expect(
            !GachaPackHandoffRules.showsPack(
                revealComplete: false,
                retreatProgress: 1),
            "Pack leaves after the real-case handoff")
        expect(
            GachaPackHandoffRules.hasVisibleForeground(
                packVisible: false,
                realCaseReady: true),
            "ready case prevents an empty handoff frame")
        expect(
            GachaPackCarouselRules.nextIndex(
                selectedIndex: 2,
                itemCount: 6,
                translationPoints: -56) == 3,
            "carousel advances one Pack")
        expect(
            GachaPackCarouselRules.nextIndex(
                selectedIndex: 2,
                itemCount: 6,
                translationPoints: -500) == 3,
            "carousel cannot skip Packs")
        expect(
            GachaNativeHybridR027StaticStage.parse(arguments: [
                "--premium-display-case-gate04-native-hybrid-r027-static=empty-mouth"
            ]) == .emptyMouth,
            "R027 static empty mouth stays explicit")
        expect(
            GachaNativeHybridR027StaticStage.parse(arguments: [
                "--premium-display-case-gate04-native-hybrid-r027-static=invalid"
            ]) == nil,
            "R027 ignores unknown static stages")
        expect(
            GachaNativeHybridR027Rules.previewToken
                == "premium-display-case-gate04-native-hybrid-r027",
            "R027 owns a separate preview transaction namespace")
        expect(
            GachaNativeHybridR028StaticStage.parse(arguments: [
                "--premium-display-case-gate04-native-hybrid-r028-static=pre-ready-mouth"
            ]) == .preReadyMouth,
            "R028 exposes a held pre-ready cavity proof stage")
        expect(
            GachaNativeHybridR028StaticStage.parse(arguments: [
                "--premium-display-case-gate04-native-hybrid-r028-static=pack-departed"
            ]) == .packDeparted,
            "R028 exposes a Pack-departed case proof stage")
        expect(
            GachaNativeHybridR028StaticStage.preReadyMouth
                .holdsApertureClosed,
            "R028 pre-ready cavity blocks aperture transparency")
        expect(
            !GachaNativeHybridR028StaticStage.containedCase
                .holdsApertureClosed,
            "R028 contained case permits the readiness gate")
        expect(
            GachaNativeHybridR028Rules.previewToken
                == "premium-display-case-gate04-native-hybrid-r028",
            "R028 owns a separate preview transaction namespace")
        let sealedLid = GachaPackLidRules.pose(progress: 0)
        let partialLid = GachaPackLidRules.pose(progress: 0.31)
        let committedLid = GachaPackLidRules.pose(progress: 0.62)
        let departedLid = GachaPackLidRules.pose(progress: 1)
        expect(
            !sealedLid.isVisible,
            "sealed Pack has no detached lid")
        expect(
            partialLid == GachaPackLidRules.pose(progress: 0.31),
            "lid rules are reversible and deterministic")
        expect(
            abs(partialLid.leadingFraction
                - GachaPackOpeningRules.openingInsetFraction) < 0.000001
                && abs(partialLid.trailingFraction
                    - GachaPackOpeningRules.openingInsetFraction
                    - (1 - GachaPackOpeningRules.openingInsetFraction * 2)
                        * 0.5) < 0.000001,
            "lid owns exactly the top pixels behind the tear front")
        expect(
            abs(partialLid.hingeXFraction - partialLid.trailingFraction)
                < 0.000001
                && abs(partialLid.hingeYFraction
                    - GachaPackOpeningRules.authoredSeamYFraction) < 0.000001,
            "lid hinges on the seam at the tear front")
        expect(
            partialLid.offsetXPoints == 0 && partialLid.offsetYPoints == 0
                && partialLid.rotationDegrees > 0
                && partialLid.rotationDegrees
                    < committedLid.rotationDegrees,
            "attached peel only lifts by the hinge angle")
        expect(
            GachaPackLidRules.staysWithinCompactTopArea(progress: 0.31)
                && GachaPackLidRules.staysWithinCompactTopArea(progress: 0.62),
            "attached lid stays a compact top-edge event")
        expect(
            departedLid.offsetYPoints
                == -GachaPackOpeningRules.sealExitLiftPoints
                && departedLid.rotationDegrees
                    > committedLid.rotationDegrees,
            "committed lid leaves upward as one body")
        expect(
            GachaPackLidRules.departsAsRigidLid(progress: 1),
            "the committed seal leaves as one lid, not loose scraps")
        expect(
            GachaPackLidRules.lidClearsPackOutline(progress: 1)
                && !GachaPackLidRules.lidClearsPackOutline(progress: 0.62),
            "the departing lid clears the Pack outline only after commit")
        expect(
            GachaPackOpeningRules.sealExitOpacity(progress: 0.62) == 1
                && GachaPackOpeningRules.sealExitOpacity(progress: 0.8) < 1
                && GachaPackOpeningRules.sealExitOpacity(progress: 1) == 0,
            "the lid fades across its flight and is gone when it lands")
        expect(
            !GachaPackLidRules.crossfadeEnabled && !departedLid.usesCrossfade,
            "lid never crossfades the Pack or case")
        // R035: the lid is the authored seal fin (flap raster). The seam is
        // the body's top edge, so the body is never cut and the sealed Pack
        // is body + fin, pixel-identical to the authored composite.
        expect(
            GachaPackOpeningRules.authoredSeamYFraction
                == GachaPackOpeningRules.authoredPackFaceTopYFraction
                && abs(GachaPackOpeningRules.authoredSeamYFraction
                    - 92.0 / 512.0) < 0.000001
                && abs(GachaPackOpeningRules.authoredPackTopYFraction
                    - 45.0 / 512.0) < 0.000001,
            "seam sits on the fin/body boundary and the fin top is the Pack top")
        expect(
            GachaPackOpeningRules.openingInsetFraction
                <= GachaPackOpeningRules.authoredFlapSpanFraction.lowerBound
                && 1 - GachaPackOpeningRules.openingInsetFraction
                    >= GachaPackOpeningRules.authoredFlapSpanFraction.upperBound,
            "the committed lid takes the whole fin, leaving no crimp ears")
        expect(
            abs(GachaPackOpeningRules.mouthInsetFraction - 59.0 / 384.0) < 0.000001
                && GachaPackOpeningRules.mouthInsetFraction
                    >= GachaPackOpeningRules.authoredFlapSpanFraction.lowerBound
                        + 7.0 / 384.0,
            "R052f mouth sliver stays between the 7-unit side seals, inside the front face")
        // R051f: flat 280-wide pouch drawn by Tools/GachaPackArtwork
        // (POUCH_X 52…332, inset 48). Python and Swift must agree.
        expect(
            abs(GachaPackOpeningRules.authoredFlapSpanFraction.lowerBound
                - 52.0 / 384.0) < 0.000001
                && abs(GachaPackOpeningRules.authoredFlapSpanFraction.upperBound
                    - 332.0 / 384.0) < 0.000001
                && abs(GachaPackOpeningRules.openingInsetFraction - 48.0 / 384.0)
                    < 0.000001
                && abs(GachaPackOpeningRules.authoredPackInteriorWidthFraction
                    - 280.0 / 384.0) < 0.000001,
            "pouch columns 52–332 match the artwork generator's POUCH_X")
        expect(
            GachaPackOpeningRules.openingEndTaper(horizontalFraction: 0) == 0
                && GachaPackOpeningRules.openingEndTaper(horizontalFraction: 1)
                    == 0
                && GachaPackOpeningRules.openingEndTaper(horizontalFraction: 0.5)
                    == 1
                && GachaPackOpeningRules.openingHeightPoints(
                    horizontalFraction: 0.5,
                    progress: GachaPackOpeningRules.tearCommitProgress)
                    == GachaPackOpeningRules.maximumOpeningHeightPoints,
            "mouth sliver tapers to nothing inside the Pack shoulders")
        expect(
            GachaPackLidRules.highestEdgePoints(progress: 0.62)
                <= GachaPackOpeningRules.artworkHeightPoints
                    * GachaPackOpeningRules.authoredPackTopYFraction
                && GachaPackLidRules.lowestEdgePoints(progress: 0.62)
                    >= GachaPackOpeningRules.artworkHeightPoints
                        * GachaPackOpeningRules.authoredSeamYFraction,
            "attached fin spans from the Pack top down to the seam")
        expect(
            !GachaPackHandoffRules.canRevealLiveCase(
                hasAuthoritativeReceipt: true,
                caseStableAfterTwoFrames: false,
                openingProgress: GachaPackOpeningRules.tearCommitProgress),
            "pre-ready cavity stays opaque")
        let ringGeometry = GachaPackMouthRingRules.geometry(
            openingProgress: GachaPackOpeningRules.tearCommitProgress)
        expect(
            ringGeometry.outerHeightPoints <= 10.0001,
            "ready mouth stays within the authored top band")
        expect(
            GachaPackMouthRingRules.cavityMode(
                caseReady: false,
                openingProgress: GachaPackOpeningRules.tearCommitProgress)
                == .opaqueLocalCavity,
            "R033 keeps the slit cavity opaque to Unity")
        expect(
            !GachaPackMouthRingRules.apertureAuthorized(
                caseReady: true,
                openingProgress: GachaPackOpeningRules.tearCommitProgress,
                legacyExposesLiveUnityBackground: true),
            "R033 never punches a Unity aperture through the Pack")
        expect(
            GachaPackMouthRingRules.cavityMode(
                caseReady: true,
                openingProgress: GachaPackOpeningRules.tearCommitProgress)
                == .opaqueLocalCavity,
            "readiness does not switch the slit to a transparent inset ring")
        expect(
            GachaNativeHybridR029CaptureCheckpoint(rawValue: "F3") == .f3
                && GachaNativeHybridR029CaptureCheckpoint(
                    rawValue: "invalid") == nil,
            "R029 accepts only named frame checkpoints")
        expect(
            GachaNativeHybridR029Rules.previewToken
                == "premium-display-case-gate04-native-hybrid-r029",
            "R029 owns a separate preview transaction namespace")
        expect(
            GachaNativeHybridR030CaptureCheckpoint(rawValue: "F3") == .f3
                && GachaNativeHybridR030CaptureCheckpoint(
                    rawValue: "invalid") == nil,
            "R030 accepts only named frame checkpoints")
        expect(
            GachaNativeHybridR030Rules.previewToken
                == "premium-display-case-gate04-native-hybrid-r030",
            "R030 owns a separate preview transaction namespace")
        for tier in GachaPackTier.allCases {
            let rgb = tier.storefrontAccentRGB
            expect(
                rgb.red >= 0 && rgb.red <= 1
                    && rgb.green >= 0 && rgb.green <= 1
                    && rgb.blue >= 0 && rgb.blue <= 1,
                "\(tier.title) storefront accent stays in sRGB")
            expect(
                tier.storefrontPriceLabel == "¥\(tier.storefrontCashPriceCNY)",
                "\(tier.title) storefront cash price is ¥\(tier.storefrontCashPriceCNY)")
            expect(
                !tier.storefrontOddsLine.contains("四档奖品池不变"),
                "\(tier.title) pool hint does not repeat the old fixed-pool line")
            expect(
                !tier.storefrontOddsLine.isEmpty,
                "\(tier.title) exposes a storefront odds line")
            expect(
                GachaPackStorefrontBackdropRules.centerGlowOpacity(for: tier)
                    <= 0.5,
                "\(tier.title) center glow reads but never washes the Pack out")
            let backdrop = tier.storefrontBackdropRGB
            let maxC = max(backdrop.red, backdrop.green, backdrop.blue)
            let minC = min(backdrop.red, backdrop.green, backdrop.blue)
            let saturation = maxC > 0 ? (maxC - minC) / maxC : 0
            let accent = tier.storefrontAccentRGB
            let accentMax = max(accent.red, accent.green, accent.blue)
            let accentMin = min(accent.red, accent.green, accent.blue)
            let accentSaturation = accentMax > 0 ? (accentMax - accentMin) / accentMax : 0
            let isNeutral = accentSaturation
                < GachaPackStorefrontBackdropRules.neutralSaturationThreshold
            expect(
                saturation <= GachaPackStorefrontBackdropRules.maximumSaturation + 0.001
                    && maxC >= GachaPackStorefrontBackdropRules.minimumValue - 0.001
                    && (isNeutral
                        ? abs(saturation - accentSaturation) < 0.001
                        : saturation > accentSaturation),
                "\(tier.title) backdrop keeps a neutral tier neutral and boosts coloured tiers (rev-007)")
        }
        let standard = GachaPackTier.standard.storefrontBackdropRGB
        let standardMax = max(standard.red, standard.green, standard.blue)
        let standardMin = min(standard.red, standard.green, standard.blue)
        expect(
            (standardMax - standardMin) / standardMax < 0.12,
            "STANDARD backdrop stays silver-grey, never blue")
        // R051 (user 2026-09-08 12:16): six prices need six clearly different
        // hues. Every pair of coloured tiers sits ≥ 40° apart on the hue
        // wheel and ≥ 0.15 apart in RGB (R051p muted metals sit closer in
        // RGB; hue carries the difference).
        func hueDegreesOf(_ rgb: (red: Double, green: Double, blue: Double)) -> Double {
            let maxC = max(rgb.red, rgb.green, rgb.blue)
            let minC = min(rgb.red, rgb.green, rgb.blue)
            let delta = maxC - minC
            guard delta > 0.000_001 else { return 0 }
            var hue: Double
            if maxC == rgb.red {
                hue = (rgb.green - rgb.blue) / delta
            } else if maxC == rgb.green {
                hue = 2 + (rgb.blue - rgb.red) / delta
            } else {
                hue = 4 + (rgb.red - rgb.green) / delta
            }
            hue *= 60
            return hue < 0 ? hue + 360 : hue
        }
        let coloured = GachaPackTier.allCases.filter { $0 != .standard }
        for (i, lhs) in coloured.enumerated() {
            for rhs in coloured.dropFirst(i + 1) {
                let a = lhs.storefrontAccentRGB, b = rhs.storefrontAccentRGB
                let hueGap = abs(hueDegreesOf(a) - hueDegreesOf(b))
                let wrapped = min(hueGap, 360 - hueGap)
                let distance = (
                    pow(a.red - b.red, 2) + pow(a.green - b.green, 2) + pow(a.blue - b.blue, 2)
                ).squareRoot()
                // R051v: deeply muted accents sit within ~0.12 in RGB; the
                // 40° hue gap is the guard that matters.
                expect(
                    wrapped >= 40 && distance >= 0.10,
                    "\(lhs.title) vs \(rhs.title) accents are clearly different hues")
            }
        }

        expect(
            GachaPackArcBackdropRules.sourceCommit
                == "d239c3463c984a099dd2cb67817a41fc0bcc876f"
                && GachaPackArcBackdropRules.sourceBlob
                    == "b13404dd73e02a4267b48ff1136aa3c1b2205827"
                && GachaPackArcBackdropRules.sourceLicense == "MIT",
            "arc backdrop pins its audited MIT source")
        expect(
            GachaPackArcBackdropRules.gradientStopsAreValid,
            "arc backdrop stop arrays stay aligned, bounded and ordered")
        let primaryArcStops = GachaPackArcBackdropRules.primaryStops
        expect(
            primaryArcStops.count == 5
                && primaryArcStops.map(\.location) == [0, 0.18, 0.40, 0.62, 0.82]
                && primaryArcStops.map(\.opacity) == [0.34, 0.28, 0.22, 0.18, 0],
            "primary arc keeps the source five-stop continuous alpha profile")
        let softArcStops = GachaPackArcBackdropRules.softStops
        expect(
            softArcStops.count == 5
                && softArcStops.map(\.location) == [0, 0.22, 0.46, 0.68, 0.86]
                && softArcStops.map(\.opacity) == [0.18, 0.15, 0.12, 0.10, 0],
            "soft arc keeps the source five-stop continuous alpha profile")
        expect(
            abs(primaryArcStops[0].red - 56.0 / 255.0) < 0.000_001
                && abs(primaryArcStops[1].green - 212.0 / 255.0) < 0.000_001
                && abs(primaryArcStops[2].red - 245.0 / 255.0) < 0.000_001
                && abs(primaryArcStops[3].blue - 94.0 / 255.0) < 0.000_001,
            "primary arc preserves source sky, teal, amber and rose colours")
        expect(
            GachaPackArcBackdropRules.primaryXRadiusFraction == 1.20
                && GachaPackArcBackdropRules.primaryYRadiusFraction == 0.88
                && GachaPackArcBackdropRules.softXRadiusFraction == 1.10
                && GachaPackArcBackdropRules.softYRadiusFraction == 0.80
                && GachaPackArcBackdropRules.baseOpacity == 1
                && GachaPackArcBackdropRules.liftPeakOpacity == 0.08
                && GachaPackArcBackdropRules.dotSpacingPoints == 4
                && GachaPackArcBackdropRules.dotDiameterPoints == 2
                && GachaPackArcBackdropRules.dotColorOpacity == 0.70
                && GachaPackArcBackdropRules.dotLayerOpacity == 0.04,
            "native baseline preserves source geometry, base, lift and dots")
        // 2026-09-07 user amendment: the arc bands are the carousel backdrop
        // too, so there is no crossfade-in after selection any more.
        expect(
            GachaPackArcBackdropRules.visibility(
                tearProgress: 0,
                stageEligible: true) == 1,
            "arc backdrop is fully present in the carousel and through the tear stage")
        expect(
            GachaPackArcBackdropRules.visibility(
                tearProgress: GachaPackOpeningRules.tearCommitProgress,
                stageEligible: true) == 1,
            "arc backdrop holds through the exact-once tear commit")
        let arcFadeMidpoint = GachaPackOpeningRules.tearCommitProgress
            + (1 - GachaPackOpeningRules.tearCommitProgress) * 0.5
        expect(
            abs(GachaPackArcBackdropRules.visibility(
                tearProgress: arcFadeMidpoint,
                stageEligible: true) - 0.5) < 0.001
                && GachaPackArcBackdropRules.visibility(
                    tearProgress: 1,
                    stageEligible: true) == 0,
            "arc backdrop follows the physical seal out before case handoff")
        expect(
            GachaPackArcBackdropRules.visibility(
                tearProgress: 0,
                stageEligible: false) == 0,
            "arc backdrop cannot escape its Pack-stage phase gate")

        // Per-Pack colourway (user review 2026-09-07 11:49: colours were too
        // close, add gold / silver for a premium read): one metallic palette
        // per tier on the untouched source structure; 1 OF 1 keeps the
        // full-spectrum source palette.
        typealias Colourway = GachaPackArcBackdropRules.Colourway
        let sourcePrimary = GachaPackArcBackdropRules.primaryStops
        let sourceSoft = GachaPackArcBackdropRules.softStops
        expect(
            Colourway.forTier(.standard) == .silver
                && Colourway.forTier(.refined) == .sapphire
                && Colourway.forTier(.signature) == .roseGold
                && Colourway.forTier(.chase) == .champagneGold
                && Colourway.forTier(.grail) == .amethystGold
                && Colourway.forTier(.oneOfOne) == .source,
            "tier ladder: silver → sapphire → rose gold → champagne gold → amethyst+gold → full-spectrum source")
        expect(
            GachaPackArcBackdropRules.primaryStops(for: .source).map(\.red)
                == sourcePrimary.map(\.red)
                && GachaPackArcBackdropRules.softStops(for: .source).map(\.green)
                    == sourceSoft.map(\.green),
            "the source colourway is the untouched OpenSourceUI palette")
        func hueOf(_ stop: GachaPackArcBackdropRules.SourceColorStop) -> Double {
            GachaPackArcBackdropRules.hueDegrees(
                red: stop.red, green: stop.green, blue: stop.blue)
        }
        func hueDistance(_ a: Double, _ b: Double) -> Double {
            let d = abs(a - b).truncatingRemainder(dividingBy: 360)
            return min(d, 360 - d)
        }
        func rgbDistance(
            _ a: GachaPackArcBackdropRules.SourceColorStop,
            _ b: GachaPackArcBackdropRules.SourceColorStop
        ) -> Double {
            let dr = a.red - b.red, dg = a.green - b.green, db = a.blue - b.blue
            return (dr * dr + dg * dg + db * db).squareRoot()
        }
        for colourway in Colourway.allCases {
            let primary = GachaPackArcBackdropRules.primaryStops(for: colourway)
            let soft = GachaPackArcBackdropRules.softStops(for: colourway)
            let scale = colourway.alphaScale
            func scaled(_ stops: [GachaPackArcBackdropRules.SourceColorStop]) -> [Double] {
                stops.enumerated().map { index, stop in
                    index < 4 ? min(1, stop.opacity * scale) : stop.opacity
                }
            }
            expect(
                primary.count == sourcePrimary.count
                    && soft.count == sourceSoft.count
                    && zip(primary.map(\.opacity), scaled(sourcePrimary)).allSatisfy { abs($0 - $1) < 0.000_001 }
                    && primary.map(\.location) == sourcePrimary.map(\.location)
                    && zip(soft.map(\.opacity), scaled(sourceSoft)).allSatisfy { abs($0 - $1) < 0.000_001 }
                    && soft.map(\.location) == sourceSoft.map(\.location)
                    && GachaPackArcBackdropRules.stopsAreValid(primary)
                    && GachaPackArcBackdropRules.stopsAreValid(soft)
                    && (colourway == .source ? scale == 1 : scale >= 1.2 && scale <= 1.8),
                "\(colourway.title) keeps the source alpha shape (metals lifted ×1.2–1.8), locations and validity")
            expect(
                primary[0].red + primary[0].green + primary[0].blue
                    > primary[3].red + primary[3].green + primary[3].blue,
                "\(colourway.title) is brightest at the centre and deepest on the band")
            if colourway != .source {
                expect(
                    zip(soft.prefix(4), primary.prefix(4)).allSatisfy {
                        $0.red >= $1.red - 0.000_001
                            && $0.green >= $1.green - 0.000_001
                            && $0.blue >= $1.blue - 0.000_001
                    },
                    "\(colourway.title) soft layer is lifted toward white like the source's soft amber / rose")
            }
        }
        // Metals: silver is near-neutral and bright; the golds sit in the
        // 30°–50° hue band; rose gold is a redder copper; sapphire is blue;
        // amethyst carries a gold core.
        let silver = GachaPackArcBackdropRules.primaryStops(for: .silver)
        let sapphire = GachaPackArcBackdropRules.primaryStops(for: .sapphire)
        let roseGold = GachaPackArcBackdropRules.primaryStops(for: .roseGold)
        let champagne = GachaPackArcBackdropRules.primaryStops(for: .champagneGold)
        let amethyst = GachaPackArcBackdropRules.primaryStops(for: .amethystGold)
        func sat(_ stop: GachaPackArcBackdropRules.SourceColorStop) -> Double {
            GachaPackArcBackdropRules.saturation(
                red: stop.red, green: stop.green, blue: stop.blue)
        }
        expect(
            silver.prefix(4).allSatisfy { sat($0) < 0.35 }
                && silver[0].red > 0.9 && silver[0].green > 0.9 && silver[0].blue > 0.9
                && Colourway.silver.alphaScale == 1.8,
            "silver stays a bright, near-neutral metal (saturation < 0.35, white centre, ×1.8 alpha)")
        expect(
            (200.0...245.0).contains(hueOf(sapphire[3]))
                && (195.0...230.0).contains(hueOf(sapphire[2]))
                && sat(sapphire[3]) > 0.6,
            "sapphire band and glow are saturated blues")
        expect(
            (15.0...30.0).contains(hueOf(roseGold[3]))
                && (10.0...25.0).contains(hueOf(roseGold[2]))
                && roseGold[2].red > 0.6,
            "rose gold reads as a copper band with a dusty-rose glow (R051p muted)")
        expect(
            (30.0...50.0).contains(hueOf(champagne[3]))
                && (35.0...50.0).contains(hueOf(champagne[2]))
                && champagne[0].red > 0.9,
            "champagne gold band and glow sit in the gold hue band with a pale champagne centre")
        expect(
            (250.0...275.0).contains(hueOf(amethyst[3]))
                && (255.0...275.0).contains(hueOf(amethyst[2]))
                && (35.0...50.0).contains(hueOf(amethyst[1])),
            "amethyst band and glow are violet with a gold ring at the core")
        // Every pair of colourways is clearly apart on both the band and the
        // glow (the two rings the phone actually shows).
        let all = Colourway.allCases.map {
            ($0, GachaPackArcBackdropRules.primaryStops(for: $0))
        }
        for (i, lhs) in all.enumerated() {
            for rhs in all.dropFirst(i + 1) {
                expect(
                    rgbDistance(lhs.1[3], rhs.1[3]) >= 0.15
                        && rgbDistance(lhs.1[2], rhs.1[2]) >= 0.15,
                    "\(lhs.0.title) vs \(rhs.0.title) differ clearly on band and glow")
            }
        }

        // FDB-GAC-036: holographic sheen coupled to device motion.
        typealias Sheen = GachaPackHolographicSheenRules
        expect(
            Sheen.tiltOffset(gravityX: 0, gravityY: 0) == 0
                && Sheen.tiltOffset(gravityX: 1, gravityY: 0) == Sheen.tiltTravelFraction
                && Sheen.tiltOffset(gravityX: -1, gravityY: 0) == -Sheen.tiltTravelFraction
                && abs(Sheen.tiltOffset(gravityX: 0.25, gravityY: 0)
                    - 0.25 * Sheen.tiltGain * Sheen.tiltTravelFraction) < 0.000_001
                && Sheen.tiltOffset(gravityX: 0, gravityY: 0.5)
                    < Sheen.tiltOffset(gravityX: 0.5, gravityY: 0),
            "tilt slides the sheen with the gravity vector, clamped to ±0.60 width, vertical tilt weaker")
        // R051y (user 09-09 09:06, after holo-card's ±28° card): near 1:1 with
        // the hand tilt (gravity ≈ sin θ) and clamped before edge-on.
        expect(
            Sheen.tiltYawDegrees(gravityX: 0.5) == 17
                && Sheen.tiltYawDegrees(gravityX: 3) == Sheen.tiltYawClampDegrees
                && Sheen.tiltYawClampDegrees >= 20 && Sheen.tiltYawClampDegrees <= 28
                && Sheen.tiltPitchDegrees(gravityY: -0.5) == -11
                && Sheen.tiltPitchDegrees(gravityY: -3) == -Sheen.tiltPitchClampDegrees
                && Sheen.tiltPitchClampDegrees < Sheen.tiltYawClampDegrees,
            "the Pack tilts with the device like a card in the hand, clamped to ±22° / ±14°")
        let tiltedForPrint = Sheen.pose(
            elapsed: 0, idleAmplitude: 0, gravityX: 1, gravityY: 0,
            sweepProgress: nil, reduceMotion: false)
        let pitchedForPrint = Sheen.pose(
            elapsed: 0, idleAmplitude: 0, gravityX: 0, gravityY: -1,
            sweepProgress: nil, reduceMotion: false)
        let printShift = Sheen.printParallax(pose: tiltedForPrint)
        let printPitchShift = Sheen.printParallax(pose: pitchedForPrint)
        expect(
            Sheen.printParallax(pose: .rest).x == 0 && Sheen.printParallax(pose: .rest).y == 0
                && abs(printShift.x - Sheen.printParallaxFraction) < 0.000_001
                && printShift.y == 0
                && printPitchShift.x == 0
                && printPitchShift.y > 0 && printPitchShift.y < printShift.x
                && Sheen.printParallaxFraction >= 0.02 && Sheen.printParallaxFraction <= 0.06,
            "print layer rides the tilt (holo-card depth): full yaw = 3.5% width, pitch weaker")
        let glareRest = Sheen.glareCenter(pose: .rest)
        let glareTilted = Sheen.glareCenter(pose: tiltedForPrint)
        expect(
            abs(glareRest.x - 0.5) < 0.000_001 && glareRest.y > 0.5 && glareRest.y < 0.7
                && glareTilted.x > glareRest.x && glareTilted.x <= 1
                && Sheen.glareCoreOpacity >= 0.4 && Sheen.glareCoreOpacity <= 0.7
                && Sheen.glareCoreRadiusFraction >= 0.12 && Sheen.glareCoreRadiusFraction <= 0.25
                && Sheen.glareFringeOpacity < Sheen.glareCoreOpacity,
            "specular follows the view as one broad soft gloss for the metal print (user 09-09 09:58)")
        expect(
            Sheen.bandWidthFraction >= 0.8,
            "sheen band is wide and diffuse, not a focused stripe (user 09:58 扩散再宽)")
        let sweepPeakPose = Sheen.pose(
            elapsed: 0, idleAmplitude: 0, gravityX: 0, gravityY: 0,
            sweepProgress: Sheen.sweepPeakProgress, reduceMotion: false)
        expect(
            Sheen.sweepEnergy(pose: .rest) == 0
                && abs(Sheen.sweepEnergy(pose: sweepPeakPose) - 1) < 0.000_001
                && Sheen.glareBoost(pose: .rest) == 1
                && abs(Sheen.glareBoost(pose: sweepPeakPose) - Sheen.glareSweepBoost) < 0.000_001
                && Sheen.glareSweepBoost > 1 && Sheen.glareSweepBoost <= 1.6
                && Sheen.shadowOpacity(pose: .rest) == Sheen.shadowRestOpacity
                && abs(Sheen.shadowOpacity(pose: sweepPeakPose) - Sheen.shadowSweepOpacity) < 0.000_001
                && Sheen.shadowRestOpacity >= 0.5 && Sheen.shadowSweepOpacity <= 1
                && Sheen.shadowBlurPoints >= 30 && Sheen.shadowBlurPoints <= 48
                && Sheen.shadowScale > 1 && Sheen.shadowScale <= 1.12
                && Sheen.shadowDropPoints > 0 && Sheen.shadowDropPoints <= 20
                && Sheen.shadowTintScale > 0.5 && Sheen.shadowTintScale < 1,
            "tinted shadow is deep, wide, dropped and tier-coloured; it and the gloss rise with a sweep")
        expect(
            GachaPackTier.allCases.allSatisfy {
                $0.printAssetName == "gacha-pack-\($0.rawValue)-print"
            },
            "each tier exposes a stand-alone print raster for parallax")
        expect(
            GachaPackOpeningRules.interiorDepthScale > 0.3
                && GachaPackOpeningRules.interiorDepthScale
                    < GachaPackOpeningRules.interiorMidScale
                && GachaPackOpeningRules.interiorMidScale
                    < GachaPackOpeningRules.interiorLipScale
                && GachaPackOpeningRules.interiorLipScale <= 1.0,
            "R052d/e mouth interior is the tier foil seen from inside: lit lip, darker depth, never black")
        expect(
            GachaPackOpeningRules.interiorLipHighlightOpacity > 0.5
                && GachaPackOpeningRules.interiorLipHighlightWidthPoints >= 0.75
                && GachaPackOpeningRules.interiorLipHighlightWidthPoints <= 1.5
                && GachaPackOpeningRules.interiorGrainOpacity > 0.05
                && GachaPackOpeningRules.interiorGrainOpacity < 0.3
                && GachaPackOpeningRules.interiorGlossOpacity > 0.1
                && GachaPackOpeningRules.interiorGlossOpacity < 0.4
                && GachaPackOpeningRules.interiorEdgeShadowOpacity > 0.3
                && GachaPackOpeningRules.interiorEdgeShadowOpacity < 0.6,
            "R052g mouth foil has a lit fold hairline, subtle grain, one gloss and a front-edge shadow")
        expect(
            abs(Sheen.idleOffset(elapsed: 0)) < 0.000_001
                && abs(Sheen.idleOffset(elapsed: GachaPackHandoffRules.idleYawPeriodSeconds / 4)
                    - Sheen.idleTravelFraction) < 0.000_001
                && Sheen.idleOffset(elapsed: 0.8, amplitude: 0) == 0,
            "without motion the sheen rides the idle yaw clock and ramps in with it")
        expect(
            Sheen.smoothingWeight(deltaSeconds: 0) == 0
                && Sheen.smoothingWeight(deltaSeconds: 1.0 / 60) > 0.1
                && Sheen.smoothingWeight(deltaSeconds: 1.0 / 60) < 0.2
                && Sheen.smoothingWeight(deltaSeconds: 1) > 0.99,
            "gravity is low-passed with a 100 ms time constant")
        expect(
            Sheen.sweepProgress(sinceTrigger: nil) == nil
                && Sheen.sweepProgress(sinceTrigger: -0.1) == nil
                && Sheen.sweepProgress(sinceTrigger: 0) == 0
                && abs((Sheen.sweepProgress(sinceTrigger: Sheen.sweepSeconds / 2) ?? -1) - 0.5) < 0.000_001
                && Sheen.sweepProgress(sinceTrigger: Sheen.sweepSeconds) == nil,
            "a sweep lasts 850 ms and then releases the sheen back to tilt control")
        expect(
            Sheen.sweepOffset(progress: 0) == Sheen.sweepStartOffset
                && Sheen.sweepOffset(progress: 1) == Sheen.sweepEndOffset
                && abs(Sheen.sweepOffset(progress: 0.5)) < 0.000_001
                && Sheen.sweepOffset(progress: 0.25) < Sheen.sweepOffset(progress: 0.5),
            "the laser sweep crosses the whole Pack from off-left to off-right, eased")
        expect(
            abs(Sheen.sweepOpacity(progress: 0) - Sheen.restOpacity) < 0.000_001
                && abs(Sheen.sweepOpacity(progress: Sheen.sweepPeakProgress) - Sheen.sweepOpacity) < 0.000_001
                && abs(Sheen.sweepOpacity(progress: 1) - Sheen.restOpacity) < 0.000_001
                && Sheen.sweepOpacity > Sheen.restOpacity * 2,
            "the sweep peaks at 22% of its run and falls back to the resting sheen")
        let restPose = Sheen.pose(
            elapsed: 0, idleAmplitude: 1, gravityX: 0, gravityY: 0,
            sweepProgress: nil, reduceMotion: false)
        let tiltedPose = Sheen.pose(
            elapsed: 0, idleAmplitude: 1, gravityX: 0.5, gravityY: -0.5,
            sweepProgress: nil, reduceMotion: false)
        let sweepingPose = Sheen.pose(
            elapsed: 0, idleAmplitude: 1, gravityX: 0.5, gravityY: 0,
            sweepProgress: Sheen.sweepPeakProgress, reduceMotion: false)
        let reducedPose = Sheen.pose(
            elapsed: 1.0, idleAmplitude: 1, gravityX: 0.5, gravityY: -0.5,
            sweepProgress: Sheen.sweepPeakProgress, reduceMotion: true)
        expect(
            restPose == .rest
                && tiltedPose.offset > 0 && tiltedPose.tiltYawDegrees == 17
                && tiltedPose.tiltPitchDegrees == -11
                && tiltedPose.opacity == Sheen.restOpacity,
            "pose: rest is neutral; tilt moves the band and the Pack, opacity stays at rest")
        expect(
            abs(sweepingPose.offset - Sheen.sweepOffset(progress: Sheen.sweepPeakProgress)) < 0.000_001
                && abs(sweepingPose.opacity - Sheen.sweepOpacity) < 0.000_001
                && sweepingPose.tiltYawDegrees == 17,
            "pose: a running sweep owns the band position but not the Pack tilt")
        expect(
            reducedPose.offset == 0 && reducedPose.tiltYawDegrees == 0
                && reducedPose.tiltPitchDegrees == 0
                && abs(reducedPose.opacity - Sheen.sweepOpacity) < 0.000_001,
            "Reduce Motion: no tilt coupling, band stays put, a shake becomes a brightness pulse")
        // R051: the band follows the Pack's carousel slide (fixed light,
        // moving print) so the foil never looks detached while swiping.
        expect(
            Sheen.carouselOffset(continuousPosition: 0) == 0
                && abs(Sheen.carouselOffset(continuousPosition: 1) + Sheen.carouselTravelFraction) < 0.000_001
                && abs(Sheen.carouselOffset(continuousPosition: -0.5) - 0.5 * Sheen.carouselTravelFraction) < 0.000_001
                && Sheen.carouselOffset(continuousPosition: 5) == -Sheen.carouselTravelClamp
                && Sheen.carouselTravelFraction <= 0.5,
            "sliding one slot right moves the highlight 0.45 widths left, clamped at ±0.90")
        let slidPose = Sheen.pose(
            elapsed: 0, idleAmplitude: 0, gravityX: 0, gravityY: 0,
            sweepProgress: nil, reduceMotion: false, carouselPosition: 0.5)
        let slidReduced = Sheen.pose(
            elapsed: 0, idleAmplitude: 0, gravityX: 0, gravityY: 0,
            sweepProgress: nil, reduceMotion: true, carouselPosition: 0.5)
        expect(
            abs(slidPose.offset - Sheen.carouselOffset(continuousPosition: 0.5)) < 0.000_001
                && slidPose.offset == slidReduced.offset
                && slidPose.tiltYawDegrees == 0,
            "carousel parallax shifts the band, also under Reduce Motion, without tilting the Pack")
        expect(
            GachaPackHandoffRules.idleFloatAmplitudePoints <= 3
                && GachaPackHandoffRules.idleYawDegrees <= 2
                && abs(GachaPackIdleMotion.offsetPoints(
                    elapsed: GachaPackHandoffRules.idleFloatPeriodSeconds / 2)
                    + GachaPackHandoffRules.idleFloatAmplitudePoints) < 0.000_001,
            "idle float is a rest, not a hover: ≤ 3 pt and ≤ 2° (R051)")
        var shake = GachaPackShakeDetector()
        expect(
            !shake.ingest(userAccelerationG: 0.3, time: 0)
                && shake.ingest(userAccelerationG: 0.6, time: 0.1)
                && !shake.ingest(userAccelerationG: 0.9, time: 0.15)
                && !shake.ingest(userAccelerationG: 0.3, time: 0.2)
                && !shake.ingest(userAccelerationG: 0.9, time: 0.25),
            "shake needs ≥ 0.55 g, fires once, and stays disarmed until the hand calms below 0.18 g")
        expect(
            !shake.ingest(userAccelerationG: 0.1, time: 0.3)
                && !shake.ingest(userAccelerationG: 0.9, time: 0.4)
                && shake.ingest(userAccelerationG: 0.9, time: 1.4),
            "re-armed shakes still wait out the 1.2 s cooldown before the next sweep")
        expect(
            GachaPackMotionFeedRulesProbe.scriptedTiltStaysInsideTravel,
            "scripted preview hand never exceeds the tilt travel")
        expect(
            GachaPackTier.allCases.allSatisfy {
                $0.foilAssetName == "gacha-pack-\($0.rawValue)-foil"
            },
            "every tier has a foil mask asset next to its body / flap rasters")

        // Tier ladder (2026-09-07): richer Packs wriggle more and land heavier;
        // STANDARD stays calm; everything is deterministic in time.
        let ladder = GachaPackTier.allCases
        expect(
            GachaPackTierLadder.burstIntervalSeconds(for: .standard) == nil
                && GachaPackTierLadder.wriggleOffsetPoints(elapsed: 1.23, tier: .standard) == 0
                && GachaPackTierLadder.arrivalRisePoints(for: .standard) == 0,
            "STANDARD has no wriggle and no arrival rise")
        for pair in zip(ladder.dropFirst(), ladder.dropLast()) {
            let (richer, poorer) = pair
            let intervalRicher = GachaPackTierLadder.burstIntervalSeconds(for: richer) ?? .infinity
            let intervalPoorer = GachaPackTierLadder.burstIntervalSeconds(for: poorer) ?? .infinity
            expect(
                intervalRicher < intervalPoorer
                    && GachaPackTierLadder.jitterPoints(for: richer) > GachaPackTierLadder.jitterPoints(for: poorer)
                    && GachaPackTierLadder.jitterDegrees(for: richer) > GachaPackTierLadder.jitterDegrees(for: poorer)
                    && GachaPackTierLadder.arrivalRisePoints(for: richer) > GachaPackTierLadder.arrivalRisePoints(for: poorer)
                    && GachaPackTierLadder.snapHapticSignal(for: richer) > GachaPackTierLadder.snapHapticSignal(for: poorer),
                "\(richer.title) is more eager and heavier than \(poorer.title)")
        }
        expect(
            GachaPackTierLadder.jitterPoints(for: .oneOfOne) <= 6.0
                && GachaPackTierLadder.jitterDegrees(for: .oneOfOne) <= 5.0
                && GachaPackTierLadder.scalePulse(for: .oneOfOne) <= 0.02,
            "the richest wriggle stays contained (≤ 6 pt, ≤ 5°, ≤ 2% swell)")
        let burst = GachaPackTierLadder.burstDurationSeconds(for: .oneOfOne)
        let interval = GachaPackTierLadder.burstIntervalSeconds(for: .oneOfOne) ?? 0
        var peak = 0.0
        var quietSample = 0.0
        for step in 0..<400 {
            let t = Double(step) / 400 * interval
            let x = abs(GachaPackTierLadder.wriggleOffsetPoints(elapsed: t, tier: .oneOfOne))
            peak = max(peak, x)
            if t > burst + 0.05 && t < interval - 0.5 { quietSample = max(quietSample, x) }
        }
        expect(
            peak > 2.0 && quietSample == 0,
            "1 OF 1 knocks in bursts and is still between bursts")
        expect(
            GachaPackTierLadder.arrivalOffsetPoints(sinceSettle: 0.1, steppedUp: true, tier: .grail) < 0
                && GachaPackTierLadder.arrivalOffsetPoints(sinceSettle: 0.1, steppedUp: false, tier: .grail) == 0
                && GachaPackTierLadder.arrivalOffsetPoints(sinceSettle: 0.6, steppedUp: true, tier: .grail) == 0,
            "stepping up rises then settles; stepping down does not")

        // Payment / failure (device hang 2026-09-07 19:39).
        expect(
            GachaPackPaymentRules.method(tickets: 1, coins: 0) == .ticket
                && GachaPackPaymentRules.method(tickets: 0, coins: 160) == .coins
                && GachaPackPaymentRules.method(tickets: 0, coins: 159) == nil
                && GachaPackPaymentRules.method(tickets: 2, coins: 999) == .ticket,
            "tickets pay first, then 160 coins, else nothing can pay")
        expect(
            GachaPackPaymentRules.priceLine(tickets: 0, coins: 40).contains("抽取券不足")
                && GachaPackPaymentRules.priceLine(tickets: 3, coins: 0).contains("余 3 张")
                && GachaPackPaymentRules.priceLine(tickets: 0, coins: 320).contains("160 硬币"),
            "price line states what will be spent or why nothing can")
        expect(
            GachaPackPaymentRules.failureMessage(reason: "insufficient-tickets").contains("抽取券不足")
                && GachaPackPaymentRules.failureMessage(reason: "transaction-in-flight").contains("稍后再试")
                && GachaPackPaymentRules.failureMessage(reason: "weird").contains("weird"),
            "every Unity failure code maps to user-facing copy")

        // Detent snap.
        let spacing = GachaPackCarouselRules.itemSpacingPoints
        expect(
            abs(GachaPackCarouselRules.displayedTranslation(translationPoints: 0.2 * spacing))
                <= 0.2 * spacing + 0.001
                && abs(GachaPackCarouselRules.displayedTranslation(translationPoints: spacing) - spacing) < 0.001
                && GachaPackCarouselRules.displayedTranslation(translationPoints: 2 * spacing)
                    < 1.3 * spacing,
            "drag is held near the detent, reaches the neighbour exactly, rubber-bands beyond")
        var monotonic = true
        var last = -Double.infinity
        for step in 0...80 {
            let d = GachaPackCarouselRules.displayedTranslation(
                translationPoints: Double(step) / 40 * spacing)
            if d < last { monotonic = false }
            last = d
        }
        expect(monotonic, "shaped drag never reverses under the finger")
        expect(
            GachaPackCarouselRules.detentHoldGain >= 0.9
                && GachaPackCarouselRules.displayedTranslation(translationPoints: 0.1 * spacing)
                    >= 0.09 * spacing,
            "detent hold tracks the finger near 1:1 (user 18:48 不跟手)")
        expect(
            GachaPackCarouselRules.stepForRelease(translationPoints: -60, predictedEndTranslationPoints: -60) == 0
                && GachaPackCarouselRules.stepForRelease(translationPoints: -90, predictedEndTranslationPoints: -90) == 1
                && GachaPackCarouselRules.stepForRelease(translationPoints: -30, predictedEndTranslationPoints: -200) == 1
                && GachaPackCarouselRules.stepForRelease(translationPoints: 30, predictedEndTranslationPoints: -300) == 0
                && GachaPackCarouselRules.stepForRelease(translationPoints: -900, predictedEndTranslationPoints: -2000) == 1
                && GachaPackCarouselRules.nextIndex(
                    selectedIndex: 5, itemCount: 6, translationPoints: -400,
                    predictedEndTranslationPoints: -900) == 5,
            "release commits at most one step: 42% travel or a same-direction flick")
        expect(
            GachaPackCarouselRules.snapDamping / (2 * GachaPackCarouselRules.snapStiffness.squareRoot()) > 0.85,
            "snap spring is near critically damped")
        // R051q (user 22:31): 1:1 tracking, heavy over-damped landing, and the
        // floor glow finishes inside ~2× the snap settle instead of 1.3 s.
        expect(
            GachaPackCarouselRules.detentHoldGain == 1
                && GachaPackCarouselRules.snapDamping
                    / (2 * GachaPackCarouselRules.snapStiffness.squareRoot()) >= 1.05
                && GachaPackCarouselRules.snapStiffness <= 320,
            "detent hold is 1:1 and the snap is over-damped and soft (user 22:31 阻尼感)")
        expect(
            GachaPackBackdropRippleRules.seconds <= 0.8
                && GachaPackBackdropRippleRules.backdropFollowDelaySeconds <= 0.15,
            "floor glow and backdrop crossfade run in step with the snap (user 22:31 再同步)")
        expect(
            GachaPackTier.allCases.allSatisfy {
                $0.emblemAssetName == "gacha-pack-\($0.rawValue)-emblem"
            },
            "each tier exposes a reversed-out emblem asset for the heading")
        // R051x holographic model (after LerSent001/holo-card).
        let spectrumSamples = stride(from: 0.0, through: 2.0, by: 0.05).map {
            GachaPackHolographicSheenRules.spectrum($0)
        }
        expect(
            spectrumSamples.allSatisfy {
                $0.red >= 0.03 && $0.red <= 1 && $0.green >= 0.03 && $0.green <= 1
                    && $0.blue >= 0.03 && $0.blue <= 1
            }
                && spectrumSamples.contains { $0.red > 0.95 && $0.green < 0.4 }
                && spectrumSamples.contains { $0.blue > 0.95 && $0.red < 0.4 },
            "sheen spectrum is a bounded cosine palette that reaches red and blue")
        expect(
            GachaPackHolographicSheenRules.spectrum(0.3).red
                != GachaPackHolographicSheenRules.spectrum(
                    0.3 + 0.5 * GachaPackHolographicSheenRules.spectrumPhaseGain).red,
            "tilting the band re-colours the spectrum")
        expect(
            GachaPackHolographicSheenRules.glintEnvelope(distanceFromBandCentre: 0) == 1
                && GachaPackHolographicSheenRules.glintEnvelope(distanceFromBandCentre: 0.5) == 0
                && GachaPackHolographicSheenRules.glintEnvelope(distanceFromBandCentre: -0.25) > 0.2
                && (0..<GachaPackHolographicSheenRules.glintCount).allSatisfy {
                    let p = GachaPackHolographicSheenRules.glintPosition($0)
                    return p.x > 0.05 && p.x < 0.95 && p.y > 0.05 && p.y < 0.95
                },
            "glints sit inside the Pack and flash only inside the band")
        expect(
            GachaPackHolographicSheenRules.restOpacity >= 0.45
                && GachaPackHolographicSheenRules.sweepOpacity > GachaPackHolographicSheenRules.restOpacity
                && GachaPackHolographicSheenRules.sweepOpacity <= 1,
            "sheen reads at rest and peaks on the sweep (user 09-09 08:54 镭射感更强)")

        // R053: motes outlive the seal and leave with the Unity stage light-up.
        expect(
            GachaPackArcBackdropRules.ambienceVisibility(stageEligible: true, frontRevealed: false) == 1
                && GachaPackArcBackdropRules.ambienceVisibility(stageEligible: true, frontRevealed: true) == 0
                && GachaPackArcBackdropRules.ambienceVisibility(stageEligible: false, frontRevealed: false) == 0
                && GachaPackArcBackdropRules.visibility(tearProgress: 1, stageEligible: true) == 0
                && GachaPackArcBackdropRules.ambienceFadeSeconds == 0.35,
            "arc bands still leave with the seal; motes stay until front-revealed (user 09-09 18:58)")
        expect(
            GachaRevealResultCopy.subtitle(
                rarityTitle: "HEIRLOOM", plateEdition: "SATIN STEEL · DRAGON SCALE")
                == "HEIRLOOM · SATIN STEEL · DRAGON SCALE"
                && GachaRevealResultCopy.subtitle(rarityTitle: "STANDARD", plateEdition: "  ")
                    == "STANDARD"
                && !GachaRevealResultCopy.subtitle(
                    rarityTitle: "HEIRLOOM", plateEdition: "X").contains("LEVEL")
                && GachaRevealResultCopy.tag == "IN COLLECTION",
            "result sheet copy is English only, no LEVEL, no collectible id")

        // Backdrop ripple + ambience.
        expect(
            GachaPackBackdropRippleRules.xScale(progress: 0)
                == GachaPackBackdropRippleRules.initialXScale
                && GachaPackBackdropRippleRules.yScale(progress: 0)
                    == GachaPackBackdropRippleRules.initialYScale
                && abs(GachaPackBackdropRippleRules.xScale(progress: 1) - 1)
                    < 0.000_001
                && abs(GachaPackBackdropRippleRules.yScale(progress: 1) - 1)
                    < 0.000_001
                && GachaPackBackdropRippleRules.echoOpacity(progress: 0) == 0
                && abs(GachaPackBackdropRippleRules.echoOpacity(progress: 1))
                    < 0.000_001,
            "bottom glow grows from a small floor seed and its echo clears")
        expect(
            GachaPackBackdropRippleRules.backdropFollowDelaySeconds > 0
                && GachaPackBackdropRippleRules.backdropFollowDelaySeconds
                    + GachaPackBackdropRippleRules.backdropFollowSeconds
                    <= GachaPackBackdropRippleRules.seconds
                && GachaPackBackdropRippleRules.originYFraction > 0.9
                && GachaPackBackdropRippleRules.originYFraction <= 1
                && GachaPackBackdropRippleRules.opacity(progress: 0.29)
                    > GachaPackBackdropRippleRules.opacity(progress: 1),
            "wash and arcs follow the floor glow and finish inside its growth; glow launches brighter than it settles")
        for pair in zip(ladder.dropFirst(), ladder.dropLast()) {
            let (richer, poorer) = pair
            expect(
                GachaPackBackdropAmbienceRules.moteCount(for: richer)
                    > GachaPackBackdropAmbienceRules.moteCount(for: poorer)
                    && GachaPackBackdropAmbienceRules.moteBaseAlpha(for: richer)
                        > GachaPackBackdropAmbienceRules.moteBaseAlpha(for: poorer)
                    && GachaPackBackdropAmbienceRules.riseSpeedScale(for: richer)
                        > GachaPackBackdropAmbienceRules.riseSpeedScale(for: poorer),
                "\(richer.title) backdrop has more dust, stronger depth and a faster rise")
        }
        expect(
            GachaPackBackdropAmbienceRules.riseSpeedScale(for: .standard) == 1
                && GachaPackBackdropAmbienceRules.riseSpeedScale(for: .oneOfOne) <= 3,
            "STANDARD is the reference rise speed; 1 OF 1 stays below 3× (urgent, not frantic)")
        let moteA = GachaPackBackdropAmbienceRules.mote(index: 3, elapsed: 2.5, tier: .grail)
        let moteB = GachaPackBackdropAmbienceRules.mote(index: 3, elapsed: 2.5, tier: .grail)
        expect(
            moteA.x == moteB.x && moteA.y == moteB.y
                && (0...1).contains(moteA.x) && (0...1).contains(moteA.y)
                && moteA.radiusPoints <= GachaPackBackdropAmbienceRules.maxRadiusPoints,
            "motes are deterministic, on screen, and capped at the bokeh radius")
        let motes = (0..<80).map {
            GachaPackBackdropAmbienceRules.mote(index: $0, elapsed: 0, tier: .oneOfOne)
        }
        let radii = motes.map(\.radiusPoints)
        let fine = radii.filter { $0 <= 1.3 }.count
        let bokeh = radii.filter { $0 >= 2.0 }.count
        expect(
            radii.allSatisfy { $0 >= GachaPackBackdropAmbienceRules.minRadiusPoints - 0.000_001 }
                && fine >= 20 && bokeh >= 6 && bokeh <= 30,
            "most motes are fine dust (≤ 1.3 pt), only a few are 2 pt+ bokeh")
        let sparkles = motes.filter(\.sparkle)
        expect(
            sparkles.count >= 6 && sparkles.count <= 30
                && sparkles.allSatisfy { $0.spikePoints > $0.radiusPoints * 1.5 }
                && motes.filter { !$0.sparkle }.allSatisfy { $0.spikePoints == 0 },
            "only the nearest motes are star sparkles, with spikes well past their glow")
        expect(
            GachaPackBackdropAmbienceRules.glowCoreFraction < 0.5
                && GachaPackBackdropAmbienceRules.sparkleSpikeWaistPoints < 1,
            "glows have no hard edge; star spikes stay thin")
        // Tier change keeps the field continuous: travel integrates.
        let before = GachaPackBackdropAmbienceRules.travel(
            travelAtChange: 0, secondsSinceChange: 4, tier: .standard)
        let after = GachaPackBackdropAmbienceRules.travel(
            travelAtChange: before, secondsSinceChange: 0, tier: .oneOfOne)
        let later = GachaPackBackdropAmbienceRules.travel(
            travelAtChange: before, secondsSinceChange: 1, tier: .oneOfOne)
        expect(
            before == 4 && after == before && later - after
                == GachaPackBackdropAmbienceRules.riseSpeedScale(for: .oneOfOne),
            "switching tier carries the travel forward, then rises at the new speed")
        let slow = GachaPackBackdropAmbienceRules.mote(index: 7, elapsed: 3, travel: 3, tier: .standard)
        let fast = GachaPackBackdropAmbienceRules.mote(index: 7, elapsed: 3, travel: 9, tier: .standard)
        expect(
            slow.x == fast.x && slow.y != fast.y,
            "travel moves the rise only; sway and twinkle follow the clock")
        expect(
            GachaPackBackdropAmbienceRules.mote(index: 3, elapsed: 0, tier: .standard).alpha
                >= 0.72 * 0.38 * 0.3,
            "even the faintest STANDARD mote stays above the h264/3× visibility floor")
        let dust = GachaPackBackdropAmbienceRules.dustRGB(red: 0.58, green: 0.60, blue: 0.64)
        expect(
            dust.red > 0.75 && dust.green > 0.75 && dust.blue > 0.75
                && dust.blue > dust.red,
            "dust lifts the tier colour toward white but keeps its hue bias")

        print("PASS \(assertions)/\(assertions)")
    }
}

/// Static checks on scripted-hand amplitudes (the feed itself is @MainActor
/// and reads the device bridge, so the harness only checks its constants).
enum GachaPackMotionFeedRulesProbe {
    static var scriptedTiltStaysInsideTravel: Bool {
        let peak = GachaPackHolographicSheenRules.tiltOffset(
            gravityX: 0.55, gravityY: 0.30)
        return peak <= GachaPackHolographicSheenRules.tiltTravelFraction
            && peak > GachaPackHolographicSheenRules.tiltTravelFraction * 0.8
    }
}
