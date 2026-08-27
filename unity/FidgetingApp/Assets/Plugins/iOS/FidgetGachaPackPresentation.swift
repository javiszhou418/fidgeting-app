import Foundation

/// Visual Pack editions are presentation/catalog metadata. They are not prize
/// rarity and must never be inferred from a receipt, otherwise the sealed Pack
/// would leak the result before reveal and silently change economy semantics.
public enum GachaPackTier: String, CaseIterable {
    case standard
    case refined
    case signature
    case chase
    case grail
    case oneOfOne = "one-of-one"

    public var title: String {
        switch self {
        case .standard: return "STANDARD"
        case .refined: return "REFINED"
        case .signature: return "SIGNATURE"
        case .chase: return "CHASE"
        case .grail: return "GRAIL"
        case .oneOfOne: return "1 OF 1"
        }
    }

    public var bodyAssetName: String {
        "gacha-pack-\(rawValue)-body"
    }

    public var flapAssetName: String {
        "gacha-pack-\(rawValue)-flap"
    }

    /// The launch catalog has one approved Pack presentation. Future series
    /// may add explicit metadata; an unknown series safely remains Standard.
    public static func forSeriesId(_ seriesId: String) -> GachaPackTier {
        switch seriesId {
        case "launch-series": return .standard
        default: return .standard
        }
    }
}

public enum GachaPackOpeningRules {
    public static let tearTravelPoints: Double = 220
    public static let tearCommitProgress: Double = 0.62
    public static let flapExitDurationSeconds: Double = 0.34

    public static func normalizedProgress(
        translationPoints: Double,
        travelPoints: Double = tearTravelPoints
    ) -> Double {
        guard travelPoints > 0 else { return 0 }
        return min(max(translationPoints / travelPoints, 0), 1)
    }

    public static func shouldCommit(progress: Double) -> Bool {
        progress >= tearCommitProgress
    }
}

/// Product-level geometry and release rules for the Pack tier carousel.
///
/// Every edition keeps the same authored Pack size. Dragging only changes the
/// continuous horizontal position, a restrained side drop, and a slight
/// outward lean. The selected Pack is the highest point; each tier steps down
/// as it moves away from center. Selection commits by actual travel rather than a
/// predicted fling so release below the fixed threshold always returns to the
/// current detent.
public enum GachaPackCarouselRules {
    public static let itemSpacingPoints: Double = 160
    public static let selectionCommitPoints: Double = 56
    public static let unselectedPackScale: Double = 0.66
    public static let selectedPackScale: Double = 0.70
    public static let maximumSideDropPoints: Double = 16
    public static let maximumSideTiltDegrees: Double = 3.5
    public static let selectionSnapResponseSeconds: Double = 0.28
    public static let selectionSnapDampingFraction: Double = 0.82

    public static func packScale(isSelected: Bool) -> Double {
        isSelected ? selectedPackScale : unselectedPackScale
    }

    public static func continuousPosition(
        itemIndex: Int,
        selectedIndex: Int,
        translationPoints: Double
    ) -> Double {
        Double(itemIndex - selectedIndex)
            + translationPoints / itemSpacingPoints
    }

    public static func horizontalOffset(
        continuousPosition: Double
    ) -> Double {
        continuousPosition * itemSpacingPoints
    }

    public static func verticalOffset(
        continuousPosition: Double
    ) -> Double {
        min(abs(continuousPosition), 2) * maximumSideDropPoints / 2
    }

    public static func tiltDegrees(
        continuousPosition: Double
    ) -> Double {
        min(
            max(
                continuousPosition * maximumSideTiltDegrees,
                -maximumSideTiltDegrees),
            maximumSideTiltDegrees)
    }

    public static func stepForRelease(
        translationPoints: Double
    ) -> Int {
        if translationPoints <= -selectionCommitPoints {
            return 1
        }
        if translationPoints >= selectionCommitPoints {
            return -1
        }
        return 0
    }

    public static func nextIndex(
        selectedIndex: Int,
        itemCount: Int,
        translationPoints: Double
    ) -> Int {
        guard itemCount > 0 else { return 0 }
        return min(
            max(
                selectedIndex + stepForRelease(
                    translationPoints: translationPoints),
                0),
            itemCount - 1)
    }
}
