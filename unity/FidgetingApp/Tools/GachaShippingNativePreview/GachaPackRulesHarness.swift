import Foundation

@main
struct GachaPackRulesHarness {
    static func main() {
        precondition(GachaPackTier.allCases.count == 6)
        precondition(Set(GachaPackTier.allCases.map(\.bodyAssetName)).count == 6)
        precondition(Set(GachaPackTier.allCases.map(\.flapAssetName)).count == 6)
        precondition(GachaPackTier.forSeriesId("launch-series") == .standard)
        precondition(GachaPackTier.forSeriesId("unknown-series") == .standard)

        precondition(GachaPackOpeningRules.normalizedProgress(
            translationPoints: -10) == 0)
        precondition(GachaPackOpeningRules.normalizedProgress(
            translationPoints: GachaPackOpeningRules.tearTravelPoints) == 1)
        precondition(!GachaPackOpeningRules.shouldCommit(progress: 0.619))
        precondition(GachaPackOpeningRules.shouldCommit(progress: 0.62))

        precondition(GachaPackCarouselRules.itemSpacingPoints == 160)
        precondition(GachaPackCarouselRules.unselectedPackScale == 0.66)
        precondition(GachaPackCarouselRules.selectedPackScale == 0.70)
        precondition(GachaPackCarouselRules.packScale(isSelected: false) == 0.66)
        precondition(GachaPackCarouselRules.packScale(isSelected: true) == 0.70)
        precondition(GachaPackCarouselRules.maximumSideDropPoints == 16)
        precondition(GachaPackCarouselRules.verticalOffset(
            continuousPosition: 0) == 0)
        precondition(GachaPackCarouselRules.verticalOffset(
            continuousPosition: 1) == 8)
        precondition(GachaPackCarouselRules.verticalOffset(
            continuousPosition: 2) == 16)
        precondition(GachaPackCarouselRules.tiltDegrees(
            continuousPosition: -1) == -3.5)
        precondition(GachaPackCarouselRules.tiltDegrees(
            continuousPosition: 1) == 3.5)
        precondition(GachaPackCarouselRules.stepForRelease(
            translationPoints: -55.999) == 0)
        precondition(GachaPackCarouselRules.stepForRelease(
            translationPoints: -56) == 1)
        precondition(GachaPackCarouselRules.stepForRelease(
            translationPoints: 56) == -1)
        precondition(GachaPackCarouselRules.nextIndex(
            selectedIndex: 2,
            itemCount: 6,
            translationPoints: -56) == 3)
        precondition(GachaPackCarouselRules.nextIndex(
            selectedIndex: 0,
            itemCount: 6,
            translationPoints: 80) == 0)

        print("GachaPackRulesHarness: 25/25 checks passed")
    }
}
