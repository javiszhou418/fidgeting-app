import Foundation

@main
struct GachaPackRulesHarness {
    static func main() {
        precondition(GachaPackTier.allCases.count == 6)
        precondition(Set(GachaPackTier.allCases.map(\.bodyAssetName)).count == 6)
        precondition(Set(GachaPackTier.allCases.map(\.flapAssetName)).count == 6)
        precondition(GachaPackTier.forSeriesId("canyon-lode") == .standard)
        precondition(GachaPackTier.forSeriesId("unknown-series") == .standard)

        precondition(GachaPackOpeningRules.normalizedProgress(
            translationPoints: -10) == 0)
        precondition(GachaPackOpeningRules.normalizedProgress(
            translationPoints: GachaPackOpeningRules.tearTravelPoints) == 1)
        precondition(!GachaPackOpeningRules.shouldCommit(progress: 0.619))
        precondition(GachaPackOpeningRules.shouldCommit(progress: 0.62))

        print("GachaPackRulesHarness: 9/9 checks passed")
    }
}
