import Foundation
import SwiftUI

@main
enum ComboHaloRuleTests {
    static func main() {
        let recommended = ComboHaloTuning.recommended

        precondition(!recommended.milestoneCrossed(
            previousCount: 8,
            newCount: 9))
        precondition(recommended.milestoneCrossed(
            previousCount: 9,
            newCount: 10))
        precondition(!recommended.milestoneCrossed(
            previousCount: 10,
            newCount: 19))
        precondition(recommended.milestoneCrossed(
            previousCount: 19,
            newCount: 20))
        precondition(recommended.milestoneCrossed(
            previousCount: 18,
            newCount: 21))
        precondition(!recommended.milestoneCrossed(
            previousCount: 20,
            newCount: 0))
        precondition(recommended.coreFlashOpacity(at: 0) == 0)
        precondition(abs(recommended.coreFlashOpacity(at: 0.035)
            - recommended.peakOpacity * 0.72) < 0.000001)
        precondition(abs(recommended.coreFlashOpacity(at: 0.065)
            - recommended.peakOpacity * 0.72) < 0.000001)
        precondition(recommended.coreFlashOpacity(at: 0.20) == 0)

        precondition(recommended.primaryRingOpacity(at: 0) == 0)
        precondition(recommended.primaryRingOpacity(at: 0.055)
            == recommended.peakOpacity)
        precondition(recommended.primaryRingOpacity(at: 0.12)
            == recommended.peakOpacity)
        precondition(recommended.primaryRingOpacity(at: 0.48) == 0)

        precondition(recommended.echoRingOpacity(at: 0.05) == 0)
        precondition(abs(recommended.echoRingOpacity(at: 0.12)
            - recommended.peakOpacity * 0.65) < 0.000001)
        precondition(abs(recommended.echoRingOpacity(at: 0.20)
            - recommended.peakOpacity * 0.65) < 0.000001)
        precondition(recommended.echoRingOpacity(at: 0.64) == 0)

        precondition(recommended.trailingRingOpacity(at: 0.10) == 0)
        precondition(abs(recommended.trailingRingOpacity(at: 0.18)
            - recommended.peakOpacity * 0.38) < 0.000001)
        precondition(abs(recommended.trailingRingOpacity(at: 0.28)
            - recommended.peakOpacity * 0.38) < 0.000001)
        precondition(recommended.trailingRingOpacity(at: 0.80) == 0)

        precondition(recommended.mistOpacity(at: 0.01) == 0)
        precondition(abs(recommended.mistOpacity(at: 0.10)
            - recommended.peakOpacity * 0.78) < 0.000001)
        precondition(abs(recommended.mistOpacity(at: 0.28)
            - recommended.peakOpacity * 0.78) < 0.000001)
        precondition(recommended.mistOpacity(at: 1) == 0)

        precondition(recommended.phase(at: 0.08, start: 0.09, end: 0.84) == 0)
        precondition(recommended.phase(at: 0.465, start: 0.09, end: 0.84) == 0.5)
        precondition(recommended.phase(at: 0.90, start: 0.09, end: 0.84) == 1)

        var clamped = ComboHaloTuning(
            firstMilestone: 1,
            repeatInterval: 100,
            durationSeconds: 4,
            endRadiusScale: 4,
            peakOpacity: 2,
            curveX1: -1,
            curveY1: -1,
            curveX2: 2,
            curveY2: 2)
        clamped.clampValues()
        precondition(clamped.firstMilestone == 5)
        precondition(clamped.repeatInterval == 50)
        precondition(clamped.durationSeconds == 1.20)
        precondition(clamped.endRadiusScale == 1.20)
        precondition(clamped.peakOpacity == 0.60)
        precondition(clamped.curveX1 == 0.02)
        precondition(clamped.curveX2 == 0.98)
        precondition(clamped.curveY1 == 0)
        precondition(clamped.curveY2 == 1)

        let clampedProjection = ComboHaloProjectionState(
            available: true,
            centerX: -0.2,
            centerY: 1.4,
            rotationDegrees: 240,
            minorAxisRatio: 0.02).clamped()
        precondition(clampedProjection.available)
        precondition(clampedProjection.centerX == 0)
        precondition(clampedProjection.centerY == 1)
        precondition(clampedProjection.rotationDegrees == 180)
        precondition(clampedProjection.minorAxisRatio == 0.18)

        let heroProjection = ComboHaloProjectionState.threeBladeHeroPreview
        precondition(heroProjection.available)
        precondition(heroProjection.centerX == 0.5)
        precondition(heroProjection.centerY == 0.5)
        precondition(heroProjection.minorAxisRatio == 0.67)

        print("ComboHaloRuleTests: 47 assertions passed")
    }
}
