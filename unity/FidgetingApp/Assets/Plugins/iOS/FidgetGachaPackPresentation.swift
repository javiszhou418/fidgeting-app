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
        case "canyon-lode": return .standard
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
