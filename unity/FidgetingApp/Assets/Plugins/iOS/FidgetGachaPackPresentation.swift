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

    /// Holographic-foil mask: the centre emblem and the printed text only
    /// (FDB-GAC-036, user review 2026-09-07 17:22). Built by
    /// `Tools/GachaPackFoilMask/build_pack_foil_masks.py` from the body.
    public var foilAssetName: String {
        "gacha-pack-\(rawValue)-foil"
    }

    /// Reversed-out emblem (white on transparent) for the storefront heading.
    public var emblemAssetName: String {
        "gacha-pack-\(rawValue)-emblem"
    }

    /// Stamped print (emblem, type, panel rim) as its own RGBA layer so the
    /// runtime can parallax it against the bare foil (R051y, after holo-card).
    public var printAssetName: String {
        "gacha-pack-\(rawValue)-print"
    }

    /// The launch catalog has one approved Pack presentation. Future series
    /// may add explicit metadata; an unknown series safely remains Standard.
    public static func forSeriesId(_ seriesId: String) -> GachaPackTier {
        switch seriesId {
        case "canyon-lode": return .standard
        default: return .standard
        }
    }

    /// Low-saturation accent sampled from the approved six-tier pack palette.
    /// Used for storefront tinting only; it must not imply prize rarity.
    /// Neutral tiers (STANDARD silver) have no hue to show, so their glows
    /// run at reduced strength instead of turning into grey fog.
    public var storefrontBackdropStrength: Double {
        let rgb = storefrontAccentRGB
        let maxC = max(rgb.red, rgb.green, rgb.blue)
        let minC = min(rgb.red, rgb.green, rgb.blue)
        let saturation = maxC > 0.0001 ? (maxC - minC) / maxC : 0
        return saturation < GachaPackStorefrontBackdropRules.neutralSaturationThreshold
            ? GachaPackStorefrontBackdropRules.neutralGlowStrength
            : 1
    }

    /// Saturated accent for backdrops and the Unity stage tint (rev-006).
    public var storefrontBackdropRGB: (red: Double, green: Double, blue: Double) {
        let rgb = storefrontAccentRGB
        return GachaPackStorefrontBackdropRules.backdropRGB(
            red: rgb.red,
            green: rgb.green,
            blue: rgb.blue)
    }

    public var storefrontAccentRGB: (
        red: Double,
        green: Double,
        blue: Double
    ) {
        // R051 (user 2026-09-08 12:16): the six bags are now graded to
        // their arc colourways by `Tools/GachaPackArtwork/build_pack_artwork.py`;
        // the accents follow the same palette so backdrop, dust and print
        // agree. 1 OF 1 is obsidian with a full-spectrum sheen; its accent is
        // the rose-magenta the spectrum settles on at the label.
        switch self {
        case .standard:
            return (0.58, 0.60, 0.64)
        // R051p (user 2026-09-08 22:21 "饱和度过高，像零食"): muted metals —
        // steel blue, dusty rose, antique brass, aubergine, smoked mauve.
        // R051v (user 2026-09-09 08:39 "饱和度还是太高，大幅度降低"): pulled a
        // further ~35% toward their own luminance; hue carries the tier.
        case .refined:
            return (0.44, 0.52, 0.62)
        case .signature:
            return (0.63, 0.45, 0.46)
        case .chase:
            return (0.73, 0.65, 0.49)
        case .grail:
            return (0.48, 0.42, 0.57)
        case .oneOfOne:
            return (0.66, 0.51, 0.62)
        }
    }

    /// Presentation-only cash price (CNY). Pack tier does not enter the draw
    /// payload; this labels the storefront only (user 2026-09-08 15:43).
    public var storefrontCashPriceCNY: Int {
        switch self {
        case .standard: return 6
        case .refined: return 12
        case .signature: return 24
        case .chase: return 32
        case .grail: return 64
        case .oneOfOne: return 128
        }
    }

    public var storefrontPriceLabel: String {
        "¥\(storefrontCashPriceCNY)"
    }

    /// What this Pack edition might contain. Presentation-only; must not imply
    /// receipt rarity or tier-specific odds.
    public var storefrontOddsLine: String {
        switch self {
        case .standard:
            return "以常见涂装收藏盒为主，精制与签名款占余下机会"
        case .refined:
            return "精制涂装更常见，仍可能开到标准盒"
        case .signature:
            return "签名涂装、限定配色盒概率更高"
        case .chase:
            return "追猎配色、稀有机构与限定贴纸更常出现"
        case .grail:
            return "圣物级涂装与唯一编号盒概率最高"
        case .oneOfOne:
            return "唯一编号展示盒，全系列最稀有包装"
        }
    }
}

/// Deterministic pack-hue backdrop strengths for the shipping storefront.
public enum GachaPackStorefrontBackdropRules {
    /// rev-006 review: the Pack hue must read clearly behind the carousel
    /// and the selected Pack; tier accents are authored low-saturation, so
    /// the backdrop uses a saturated variant of the accent.
    public static let centerGlowOpacity = 0.42
    public static let midRingOpacity = 0.16
    public static let floorGlowOpacity = 0.24
    public static let topWashOpacity = 0.12
    // R051p: 2.4 / 0.85 read as candy; the floor glow now stays a muted
    // version of the metal.
    // R051v (user 09-09 08:39): 1.3 / 0.55 → 1.1 / 0.38.
    public static let saturationBoost = 1.1
    public static let maximumSaturation = 0.38
    public static let minimumValue = 0.52
    /// Below this the accent is a neutral (STANDARD silver-grey) and keeps
    /// its own hue and saturation: the boost must never invent a colour the
    /// tier does not have (rev-007 review: "这个蓝色哪来的，不对").
    public static let neutralSaturationThreshold = 0.2
    /// Glow strength multiplier for neutral tiers (keeps STANDARD dark).
    public static let neutralGlowStrength = 0.55

    /// HSV-saturated backdrop colour for a tier accent (0–1 RGB in/out).
    /// Coloured tiers (steel blue, copper, champagne) get `saturationBoost`;
    /// neutral tiers stay neutral.
    public static func backdropRGB(
        red: Double,
        green: Double,
        blue: Double
    ) -> (red: Double, green: Double, blue: Double) {
        let maxC = max(red, green, blue)
        let minC = min(red, green, blue)
        let delta = maxC - minC
        var hue = 0.0
        if delta > 0.0001 {
            if maxC == red {
                hue = ((green - blue) / delta).truncatingRemainder(dividingBy: 6)
            } else if maxC == green {
                hue = (blue - red) / delta + 2
            } else {
                hue = (red - green) / delta + 4
            }
            hue /= 6
            if hue < 0 { hue += 1 }
        }
        let saturation = maxC > 0.0001 ? delta / maxC : 0
        let boosted = saturation < neutralSaturationThreshold
            ? saturation
            : min(maximumSaturation, saturation * saturationBoost)
        let value = max(minimumValue, maxC)
        // HSV → RGB
        let h6 = hue * 6
        let i = Int(h6.rounded(.down)) % 6
        let f = h6 - h6.rounded(.down)
        let p = value * (1 - boosted)
        let q = value * (1 - boosted * f)
        let t = value * (1 - boosted * (1 - f))
        switch i {
        case 0: return (value, t, p)
        case 1: return (q, value, p)
        case 2: return (p, value, t)
        case 3: return (p, q, value)
        case 4: return (t, p, value)
        default: return (value, p, q)
        }
    }

    public static func centerGlowOpacity(for tier: GachaPackTier) -> Double {
        centerGlowOpacity
    }

    public static func midRingOpacity(for tier: GachaPackTier) -> Double {
        midRingOpacity
    }

    public static func floorGlowOpacity(for tier: GachaPackTier) -> Double {
        floorGlowOpacity
    }

    public static func topWashOpacity(for tier: GachaPackTier) -> Double {
        topWashOpacity
    }
}

/// Source-faithful native baseline of OpenSourceUI's MIT-licensed Dark Arc
/// Bands backdrop. The fixed palette is decorative and identical for every
/// Pack; it reads neither selected tier nor receipt rarity.
public enum GachaPackArcBackdropRules {
    public struct SourceColorStop {
        public let red: Double
        public let green: Double
        public let blue: Double
        public let opacity: Double
        public let location: Double

        public init(
            red: Double,
            green: Double,
            blue: Double,
            opacity: Double,
            location: Double
        ) {
            self.red = red
            self.green = green
            self.blue = blue
            self.opacity = opacity
            self.location = location
        }
    }

    public static let sourceCommit =
        "d239c3463c984a099dd2cb67817a41fc0bcc876f"
    public static let sourceBlob =
        "b13404dd73e02a4267b48ff1136aa3c1b2205827"
    public static let sourceLicense = "MIT"

    public static let baseTopRGB = (red: 16.0 / 255.0,
                                    green: 18.0 / 255.0,
                                    blue: 24.0 / 255.0)
    public static let baseBottomRGB = (red: 10.0 / 255.0,
                                       green: 11.0 / 255.0,
                                       blue: 14.0 / 255.0)
    /// The first review gate is a literal isolated baseline. Cave compositing
    /// is calibrated separately only after source fidelity is visually proven.
    public static let baseOpacity = 1.0
    public static let reducedTransparencyBaseOpacity = 1.0

    public static let primaryWidthFraction = 1.50
    public static let primaryHeightFraction = 0.92
    public static let primaryBottomOverflowFraction = 0.28
    public static let primaryXRadiusFraction = 1.20
    public static let primaryYRadiusFraction = 0.88
    public static let primaryStops = [
        SourceColorStop(
            red: 56.0 / 255.0, green: 189.0 / 255.0,
            blue: 248.0 / 255.0, opacity: 0.34, location: 0.0),
        SourceColorStop(
            red: 45.0 / 255.0, green: 212.0 / 255.0,
            blue: 191.0 / 255.0, opacity: 0.28, location: 0.18),
        SourceColorStop(
            red: 245.0 / 255.0, green: 158.0 / 255.0,
            blue: 11.0 / 255.0, opacity: 0.22, location: 0.40),
        SourceColorStop(
            red: 244.0 / 255.0, green: 63.0 / 255.0,
            blue: 94.0 / 255.0, opacity: 0.18, location: 0.62),
        SourceColorStop(
            red: 10.0 / 255.0, green: 11.0 / 255.0,
            blue: 14.0 / 255.0, opacity: 0.0, location: 0.82),
    ]

    public static let softWidthFraction = 1.28
    public static let softHeightFraction = 0.78
    public static let softBottomOverflowFraction = 0.22
    public static let softXRadiusFraction = 1.10
    public static let softYRadiusFraction = 0.80
    public static let softBlurPoints = 40.0
    public static let softStops = [
        SourceColorStop(
            red: 56.0 / 255.0, green: 189.0 / 255.0,
            blue: 248.0 / 255.0, opacity: 0.18, location: 0.0),
        SourceColorStop(
            red: 45.0 / 255.0, green: 212.0 / 255.0,
            blue: 191.0 / 255.0, opacity: 0.15, location: 0.22),
        SourceColorStop(
            red: 251.0 / 255.0, green: 191.0 / 255.0,
            blue: 36.0 / 255.0, opacity: 0.12, location: 0.46),
        SourceColorStop(
            red: 251.0 / 255.0, green: 113.0 / 255.0,
            blue: 133.0 / 255.0, opacity: 0.10, location: 0.68),
        SourceColorStop(
            red: 0.0, green: 0.0, blue: 0.0,
            opacity: 0.0, location: 0.86),
    ]

    public static let liftWidthFraction = 1.04
    public static let liftHeightFraction = 0.58
    public static let liftBottomOverflowFraction = 0.18
    public static let liftXRadiusFraction = 1.00
    public static let liftYRadiusFraction = 0.70
    public static let liftBlurPoints = 64.0
    public static let liftPeakOpacity = 0.08
    public static let liftEndLocation = 0.68

    public static let dotSpacingPoints = 4.0
    /// CSS uses a one-pixel radius inside a four-pixel tile.
    public static let dotDiameterPoints = 2.0
    public static let dotColorOpacity = 0.70
    public static let dotLayerOpacity = 0.04

    public static var gradientStopsAreValid: Bool {
        validStops(primaryStops) && validStops(softStops)
    }

    /// Per-Pack colourway (FDB-GAC-035, user amendments 2026-09-07): the
    /// source structure (alpha profile, stop locations, ellipses, blur, lift,
    /// dots, midnight base) is shared by every Pack; only the four colour
    /// stops change. The ladder reads as metals — silver, sapphire, rose
    /// gold, champagne gold, amethyst with a gold core — and the rarest
    /// Pack keeps the full-spectrum source palette. The input is the Pack
    /// tier the user can already see; receipt rarity never enters.
    public enum Colourway: String, CaseIterable {
        /// OpenSourceUI sky / teal / amber / rose.
        case source
        case silver
        case sapphire
        case roseGold = "rose-gold"
        case champagneGold = "champagne-gold"
        case amethystGold = "amethyst-gold"

        public static func forTier(_ tier: GachaPackTier) -> Colourway {
            switch tier {
            case .standard: return .silver
            case .refined: return .sapphire
            case .signature: return .roseGold
            case .chase: return .champagneGold
            case .grail: return .amethystGold
            case .oneOfOne: return .source
            }
        }

        public var title: String {
            switch self {
            case .source: return "全光谱（源 palette）"
            case .silver: return "银"
            case .sapphire: return "蓝宝石"
            case .roseGold: return "玫瑰金"
            case .champagneGold: return "香槟金"
            case .amethystGold: return "紫晶 · 金心"
            }
        }

        /// Alpha profile multiplier (shape unchanged). The midnight base is
        /// blue-black, so low-alpha metals blend into olive or grey; each
        /// metal is lifted just enough to read, silver most of all because
        /// it has no hue to carry it.
        public var alphaScale: Double {
            switch self {
            case .source: return 1.0
            case .silver: return 1.8
            case .sapphire: return 1.2
            case .roseGold: return 1.25
            case .champagneGold: return 1.25
            case .amethystGold: return 1.2
            }
        }

        /// Opaque sRGB colours for the centre, ring, glow and band stops.
        /// Each metal is two-tone like real metal: a bright highlight core,
        /// a saturated mid ring / glow and a deeper band.
        public var colours: [(red: Double, green: Double, blue: Double)] {
            switch self {
            case .source:
                return GachaPackArcBackdropRules.primaryStops.prefix(4).map {
                    (red: $0.red, green: $0.green, blue: $0.blue)
                }
            case .silver:
                return [
                    GachaPackArcBackdropRules.rgb(0xFF, 0xFF, 0xFF),
                    GachaPackArcBackdropRules.rgb(0xDD, 0xE3, 0xEA),
                    GachaPackArcBackdropRules.rgb(0xB4, 0xBC, 0xC6),
                    GachaPackArcBackdropRules.rgb(0x6F, 0x7A, 0x88),
                ]
            case .sapphire:
                return [
                    GachaPackArcBackdropRules.rgb(0xE8, 0xEE, 0xF5),
                    GachaPackArcBackdropRules.rgb(0x8F, 0xB0, 0xD0),
                    GachaPackArcBackdropRules.rgb(0x3E, 0x6A, 0x96),
                    GachaPackArcBackdropRules.rgb(0x2A, 0x4A, 0x72),
                ]
            case .roseGold:
                return [
                    GachaPackArcBackdropRules.rgb(0xF7, 0xED, 0xE6),
                    GachaPackArcBackdropRules.rgb(0xD9, 0xA8, 0xA0),
                    GachaPackArcBackdropRules.rgb(0xB8, 0x73, 0x5E),
                    GachaPackArcBackdropRules.rgb(0x82, 0x48, 0x2E),
                ]
            case .champagneGold:
                return [
                    GachaPackArcBackdropRules.rgb(0xF8, 0xF2, 0xE2),
                    GachaPackArcBackdropRules.rgb(0xD8, 0xC0, 0x88),
                    GachaPackArcBackdropRules.rgb(0xBC, 0x9E, 0x4E),
                    GachaPackArcBackdropRules.rgb(0x8C, 0x74, 0x40),
                ]
            case .amethystGold:
                return [
                    GachaPackArcBackdropRules.rgb(0xF2, 0xE9, 0xD6),
                    GachaPackArcBackdropRules.rgb(0xC9, 0xA8, 0x5A),
                    GachaPackArcBackdropRules.rgb(0x7B, 0x5E, 0x9E),
                    GachaPackArcBackdropRules.rgb(0x4A, 0x34, 0x68),
                ]
            }
        }
    }

    /// Soft layer colours are the primary colours lifted toward white, the
    /// way the source's soft amber / rose are lighter than its primaries.
    public static let softLightenFraction = 0.22

    /// Primary stops for a colourway: source locations and alpha shape
    /// (scaled by `alphaScale`), palette RGB.
    public static func primaryStops(for colourway: Colourway) -> [SourceColorStop] {
        recolour(
            primaryStops,
            with: colourway.colours,
            alphaScale: colourway.alphaScale)
    }

    /// Soft stops for a colourway; the source keeps its exact soft stops.
    public static func softStops(for colourway: Colourway) -> [SourceColorStop] {
        guard colourway != .source else { return softStops }
        let lifted = colourway.colours.map { colour in
            (red: colour.red + (1 - colour.red) * softLightenFraction,
             green: colour.green + (1 - colour.green) * softLightenFraction,
             blue: colour.blue + (1 - colour.blue) * softLightenFraction)
        }
        return recolour(softStops, with: lifted, alphaScale: colourway.alphaScale)
    }

    public static func hueDegrees(
        red: Double,
        green: Double,
        blue: Double
    ) -> Double {
        hsv(red, green, blue).hue
    }

    public static func saturation(
        red: Double,
        green: Double,
        blue: Double
    ) -> Double {
        hsv(red, green, blue).saturation
    }

    public static func stopsAreValid(_ stops: [SourceColorStop]) -> Bool {
        validStops(stops)
    }

    static func rgb(_ red: Int, _ green: Int, _ blue: Int)
        -> (red: Double, green: Double, blue: Double) {
        (Double(red) / 255, Double(green) / 255, Double(blue) / 255)
    }

    /// Replaces the RGB of the four colour stops and scales their opacity
    /// uniformly, keeping every location; the transparent terminal stop is
    /// untouched.
    private static func recolour(
        _ stops: [SourceColorStop],
        with colours: [(red: Double, green: Double, blue: Double)],
        alphaScale: Double
    ) -> [SourceColorStop] {
        stops.enumerated().map { index, stop in
            guard index < colours.count else { return stop }
            let colour = colours[index]
            return SourceColorStop(
                red: colour.red,
                green: colour.green,
                blue: colour.blue,
                opacity: min(1, stop.opacity * alphaScale),
                location: stop.location)
        }
    }

    /// Present from the carousel on, holds through the user's tear, then
    /// follows the physical seal out. At progress 1 the view is fully
    /// transparent, so it cannot cover the real assembled case.
    public static func visibility(
        tearProgress: Double,
        stageEligible: Bool
    ) -> Double {
        guard stageEligible else { return 0 }
        return clamped(GachaPackOpeningRules.sealExitOpacity(
            progress: tearProgress))
    }

    /// R053 (user 2026-09-09 18:58: the carousel gradient and particles
    /// vanish the instant the Pack tears). The arc bands must still leave
    /// with the seal because the native layer sits above the Unity case;
    /// Unity carries the same arcs + settled floor glow as its stage
    /// backdrop until the flip. The motes are transparent, so they stay
    /// native through handoff and fade with the Unity stage light-up.
    public static func ambienceVisibility(
        stageEligible: Bool,
        frontRevealed: Bool
    ) -> Double {
        guard stageEligible, !frontRevealed else { return 0 }
        return 1
    }

    /// Matches `GachaShippingRevealChoreography.StageLightUpSeconds`.
    public static let ambienceFadeSeconds = 0.35

    private static func clamped(_ value: Double) -> Double {
        min(max(value, 0), 1)
    }

    private static func normalizedDegrees(_ degrees: Double) -> Double {
        let wrapped = degrees.truncatingRemainder(dividingBy: 360)
        return wrapped < 0 ? wrapped + 360 : wrapped
    }

    private static func hsv(
        _ red: Double,
        _ green: Double,
        _ blue: Double
    ) -> (hue: Double, saturation: Double, value: Double) {
        let maxC = max(red, green, blue)
        let minC = min(red, green, blue)
        let delta = maxC - minC
        guard delta > 0.000_001 else { return (0, 0, maxC) }
        var hue: Double
        if maxC == red {
            hue = (green - blue) / delta
        } else if maxC == green {
            hue = 2 + (blue - red) / delta
        } else {
            hue = 4 + (red - green) / delta
        }
        hue = normalizedDegrees(hue * 60)
        let saturation = maxC > 0.000_001 ? delta / maxC : 0
        return (hue, saturation, maxC)
    }

    private static func validStops(_ stops: [SourceColorStop]) -> Bool {
        guard stops.count >= 2,
              stops.allSatisfy({
                  (0...1).contains($0.red)
                      && (0...1).contains($0.green)
                      && (0...1).contains($0.blue)
                      && (0...1).contains($0.opacity)
                      && (0...1).contains($0.location)
              }) else {
            return false
        }
        return zip(stops, stops.dropFirst()).allSatisfy {
            lower, upper in lower.location < upper.location
        }
    }
}

/// R053 result-sheet copy (user 2026-09-09 18:58: English, one font, no
/// "LEVEL n", no collectible id). Mirrors the Unity plate authority.
public enum GachaRevealResultCopy {
    public static let tag = "IN COLLECTION"
    public static let separator = " · "

    /// `HEIRLOOM · SATIN STEEL · DRAGON SCALE`; rarity alone when the prize
    /// has no plate edition. Never contains a level number or an id.
    public static func subtitle(rarityTitle: String, plateEdition: String) -> String {
        let edition = plateEdition.trimmingCharacters(in: .whitespacesAndNewlines)
        return edition.isEmpty ? rarityTitle : rarityTitle + separator + edition
    }
}

public enum GachaPackOpeningRules {
    /// Commit (0.62) lands at 40% of the Pack width: 0.62 × 181 ≈ 112 pt.
    public static let tearTravelPoints: Double = 181
    public static let tearCommitProgress: Double = 0.62
    /// Whole-lid fly-off after the tear commits (spec: 480 ms EASE_OUT,
    /// translateY -90, translateX +60 along the tear, rotateZ 14°, fades out).
    public static let flapExitDurationSeconds: Double = 0.48
    public static let sealExitLiftPoints: Double = 90
    public static let flapHorizontalTravelPoints: Double = 16
    public static let flapVerticalLiftPoints: Double = 10
    public static let flapRotationDegrees: Double = 4
    public static let authoredCanvasWidth: Double = 384
    public static let authoredCanvasHeight: Double = 512
    /// User 2026-09-08 15:28 "占比大一些": stage Pack width on a ~393 pt
    /// phone (selected carousel ≈ 237 pt ≈ 60% of screen width).
    public static let artworkWidthPoints: Double = 280
    public static let artworkHeightPoints: Double =
        artworkWidthPoints * authoredCanvasHeight / authoredCanvasWidth
    /// Just outside the authored pouch (columns 52–332 of 384, 0.135), so
    /// the tear removes the whole fin instead of leaving crimp ears.
    public static let openingInsetFraction: Double = 48.0 / 384.0
    /// R052f (user 09-09 17:09 "两边的角超出了 front 这一面"): the mouth
    /// sliver spans only the pouch interior between the welded side seals
    /// (columns 59–325 of 384), never the pouch edge or beyond it.
    public static let mouthInsetFraction: Double = 59.0 / 384.0
    /// Interior sliver between the front panel's torn edge and the back
    /// panel's lip, drawn in the space the lid vacates. The removed lid, not
    /// this band, is what reads as the opening.
    /// R052e (user 09-09 16:25): 10 → 5. The mouth is a slit between two
    /// foil layers, not a cavity; the rimmed body edge below it carries the
    /// "torn open" read on the Pack's own plane.
    public static let maximumOpeningHeightPoints: Double = 5
    public static let openingSealLiftPoints: Double = 2.4
    /// Commit beat. Gacha reveal v2 (FDB-GAC-033) puts the flash, streaks
    /// and particles on the reveal frame, not on the tear: the seal flies,
    /// the mouth gapes and one medium haptic fires. The pulse plumbing stays
    /// for the mouth gape timing; flash and streaks are zero here.
    public static let releasePulseDurationSeconds: Double = 0.60
    public static let releasePulseRiseSeconds: Double = 0.04
    public static let releasePulsePeakSeconds: Double = 0.06
    public static let releaseFlashPeakOpacity: Double = 0
    /// Flash opacity for a pulse strength in 0...1. Strength rises to 1 in
    /// `releasePulseRiseSeconds` and falls back over the rest of the pulse;
    /// the power keeps the flash short while the streaks outlive it.
    public static func releaseFlashOpacity(pulseStrength: Double) -> Double {
        let strength = clamped(pulseStrength)
        return releaseFlashPeakOpacity * pow(strength, 2.4)
    }
    public static let releaseBurstStreakCount = 0
    /// Streak start radius and travel, in fractions of the burst radius.
    public static let releaseBurstInnerRadiusFraction: Double = 0.16
    public static let releaseBurstTravelFraction: Double = 0.95
    public static let authoredPackInteriorWidthFraction: Double = 280.0 / 384.0
    /// Authored on a 384x512 canvas by Tools/GachaPackArtwork (rendered at
    /// 2x). The sealed Pack is body + flap: the flap (seal fin) occupies
    /// rows 45–101, the body starts at row 92, and the flap's bottom rows
    /// duplicate the body's top rows. The seam is row 92: the lid is the fin
    /// above it, the body below it stays authored and uncut. The headline
    /// text starts at row 108.
    public static let authoredPackTopYFraction: Double = 45.0 / 512.0
    public static let authoredPackFaceTopYFraction: Double = 92.0 / 512.0
    public static let authoredSeamYFraction: Double = 92.0 / 512.0
    /// Pouch and fin span columns 52–332 (0.135–0.865); the tear inset sits
    /// just outside so the lid takes the whole fin. The flat 280-wide pouch
    /// (user 2026-09-08 13:51) is close to the slab's 188:240 proportion.
    public static let authoredFlapSpanFraction: ClosedRange<Double> =
        (52.0 / 384.0)...(332.0 / 384.0)
    public static let tearFrontTransitionFraction: Double = 0.072
    public static let tornEdgeAmplitudePoints: Double = 1.6
    /// The mouth sliver shrinks to nothing over this fraction of its span at
    /// each end so it stays inside the Pack shoulders.
    public static let openingEndTaperFraction: Double = 0.07
    /// Mouth interior shades as multiples of the tier accent (R052d): the
    /// lit back lip, the middle, and the deepest point of the sliver.
    public static let interiorLipScale: Double = 1.0
    public static let interiorMidScale: Double = 0.84
    public static let interiorDepthScale: Double = 0.7
    /// R052g (user 09-09 17:52 "加点质感和纵深的阴影/高光，现在太平了"):
    /// the back panel's fold edge catches a hairline highlight, its foil
    /// carries a fine horizontal grain and one broad gloss, and the front
    /// panel's torn edge drops a shadow onto it just above the seam.
    public static let interiorLipHighlightOpacity: Double = 0.8
    public static let interiorLipHighlightWidthPoints: Double = 1.0
    public static let interiorGrainOpacity: Double = 0.16
    public static let interiorGlossOpacity: Double = 0.22
    public static let interiorEdgeShadowOpacity: Double = 0.45

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

    public static func isMouthOpen(progress: Double) -> Bool {
        openingMaskAreaSquarePoints(progress: progress) > 0.01
    }

    public static func tearFrontProgress(progress: Double) -> Double {
        clamped(progress / tearCommitProgress)
    }

    /// The tear starts at the left seal anchor and moves toward the right.
    public static func tearFrontXFraction(progress: Double) -> Double {
        tearFrontProgress(progress: progress)
    }

    /// Progress from commit through the top-tab exit beat.
    public static func sealExitProgress(progress: Double) -> Double {
        guard progress > tearCommitProgress else { return 0 }
        return clamped(
            (progress - tearCommitProgress)
                / max(1 - tearCommitProgress, 0.001))
    }

    /// The departing lid fades across its whole flight and is gone when it
    /// lands; it never hovers.
    public static func sealExitOpacity(progress: Double) -> Double {
        1 - sealExitProgress(progress: progress)
    }

    /// Returns how far a given horizontal Pack column has opened.
    public static func openingFraction(
        horizontalFraction: Double,
        progress: Double
    ) -> Double {
        let tear = tearFrontProgress(progress: progress)
        guard tear > 0 else { return 0 }
        let edge = tear
        let halfTransition = tearFrontTransitionFraction / 2
        return 1 - smoothstep(
            (clamped(horizontalFraction) - (edge - halfTransition))
                / (halfTransition * 2))
    }

    public static func flapHorizontalOffsetPoints(progress: Double) -> Double {
        tearFrontProgress(progress: progress) * flapHorizontalTravelPoints
    }

    public static func flapVerticalOffsetPoints(progress: Double) -> Double {
        -tearFrontProgress(progress: progress) * flapVerticalLiftPoints
    }

    public static func flapRotation(progress: Double) -> Double {
        tearFrontProgress(progress: progress) * flapRotationDegrees
    }

    public static func flapOpacity(progress: Double) -> Double {
        1
    }

    public static func openingHeightPoints(progress: Double) -> Double {
        tearFrontProgress(progress: progress) * maximumOpeningHeightPoints
    }

    public static func openingHeightPoints(
        horizontalFraction: Double,
        progress: Double
    ) -> Double {
        openingFraction(
            horizontalFraction: horizontalFraction,
            progress: progress)
            * openingHeightPoints(progress: progress)
            * openingEndTaper(horizontalFraction: horizontalFraction)
    }

    /// 0 at both ends of the mouth span, 1 across the middle.
    public static func openingEndTaper(horizontalFraction: Double) -> Double {
        let distanceToEnd = min(
            clamped(horizontalFraction),
            1 - clamped(horizontalFraction))
        return smoothstep(distanceToEnd / openingEndTaperFraction)
    }

    public static func openingMaskAreaSquarePoints(
        progress: Double
    ) -> Double {
        let samples = 96
        let width = artworkWidthPoints
            * (1 - mouthInsetFraction * 2)
        guard width > 0 else { return 0 }

        var heightSum = 0.0
        for sample in 0...samples {
            let fraction = Double(sample) / Double(samples)
            heightSum += openingHeightPoints(
                horizontalFraction: fraction,
                progress: progress)
        }
        return heightSum * width / Double(samples + 1)
    }

    public static func seamLightStrength(
        progress: Double,
        gestureActive: Bool,
        handoffActive: Bool,
        retreatProgress: Double
    ) -> Double {
        guard gestureActive, !handoffActive, retreatProgress <= 0 else {
            return 0
        }
        return sin(
            tearFrontProgress(progress: progress)
                * .pi / 2)
    }

    private static func clamped(_ value: Double) -> Double {
        min(max(value, 0), 1)
    }

    private static func smoothstep(_ value: Double) -> Double {
        let clampedValue = clamped(value)
        return clampedValue * clampedValue
            * (3 - 2 * clampedValue)
    }
}

public enum GachaPackMouthCavityMode: Equatable, Sendable {
    case opaqueLocalCavity
}

public struct GachaPackMouthRingGeometry: Equatable, Sendable {
    public let outerWidthPoints: Double
    public let outerHeightPoints: Double
    public let insetPoints: Double
    public let insetWidthPoints: Double
    public let insetHeightPoints: Double

    public var hasOuterAndInsetGeometry: Bool {
        outerWidthPoints > insetWidthPoints
            && outerHeightPoints > insetHeightPoints
            && insetWidthPoints > 0
            && insetHeightPoints > 0
            && insetPoints > 0
    }
}

/// R033 slit geometry. The live case is not composited through the Pack mouth.
public enum GachaPackMouthRingRules {
    public static func apertureAuthorized(
        caseReady: Bool,
        openingProgress: Double,
        legacyExposesLiveUnityBackground: Bool = false
    ) -> Bool {
        _ = caseReady
        _ = openingProgress
        _ = legacyExposesLiveUnityBackground
        return false
    }

    public static func cavityMode(
        caseReady: Bool,
        openingProgress: Double,
        legacyExposesLiveUnityBackground: Bool = false
    ) -> GachaPackMouthCavityMode {
        _ = caseReady
        _ = openingProgress
        _ = legacyExposesLiveUnityBackground
        return .opaqueLocalCavity
    }

    public static func geometry(
        openingProgress: Double
    ) -> GachaPackMouthRingGeometry {
        let outerWidth = GachaPackOpeningRules.artworkWidthPoints
            * (1 - GachaPackOpeningRules.mouthInsetFraction * 2)
        let outerHeight = GachaPackOpeningRules.openingHeightPoints(
            progress: openingProgress)
        return GachaPackMouthRingGeometry(
            outerWidthPoints: outerWidth,
            outerHeightPoints: outerHeight,
            insetPoints: 0,
            insetWidthPoints: outerWidth,
            insetHeightPoints: outerHeight)
    }
}

public struct GachaPackLidPose: Equatable, Sendable {
    public let isVisible: Bool
    /// Torn span in artwork-width fractions. The lid owns exactly the Pack
    /// top pixels the tear front has already passed.
    public let leadingFraction: Double
    public let trailingFraction: Double
    /// Hinge sits on the seam at the tear front. Columns joining the lid at
    /// the hinge have zero displacement, so the mask can grow without a pop.
    public let hingeXFraction: Double
    public let hingeYFraction: Double
    public let rotationDegrees: Double
    public let offsetXPoints: Double
    public let offsetYPoints: Double
    public let undersideDepthPoints: Double
    public let opacity: Double
    public let usesCrossfade: Bool
}

/// One rigid lid: the authored seal fin (flap raster) cut along the seam.
///
/// While the seam is tearing, the freed part of the fin hangs from the tear
/// front and lifts by a small hinge angle; the rest of the fin stays attached
/// in place. After commit the whole fin leaves upward as one body and fades
/// only once it has cleared the Pack outline. The body raster is never cut.
public enum GachaPackLidRules {
    public static let crossfadeEnabled = false
    /// Positive degrees lift the freed left end when anchored at the front.
    /// Kept small: the fin is 47 rows tall, so a 3.5° hinge shears its top
    /// edge at the front by under 2 pt.
    public static let peelHingeDegrees: Double = 3.5
    public static let exitRotationDegrees: Double = 14
    /// Positive drifts along the tear direction (left → right).
    public static let exitDriftPoints: Double = 60
    public static let undersideDepthPoints: Double = 2.4
    /// Seam (0.180) plus torn-edge texture and foil thickness.
    public static let compactTopAreaBottomFraction = 0.21

    public static func pose(
        progress: Double,
        artworkWidthPoints: Double = GachaPackOpeningRules.artworkWidthPoints,
        artworkHeightPoints: Double = GachaPackOpeningRules.artworkHeightPoints
    ) -> GachaPackLidPose {
        let tearFront = clamped(
            GachaPackOpeningRules.tearFrontProgress(progress: progress))
        let exit = GachaPackOpeningRules.sealExitProgress(progress: progress)
        let inset = GachaPackOpeningRules.openingInsetFraction
        let front = inset + (1 - inset * 2) * tearFront
        let easedExit = exit * exit * (3 - 2 * exit)
        return GachaPackLidPose(
            isVisible: tearFront > 0.0001,
            leadingFraction: inset,
            trailingFraction: front,
            hingeXFraction: front,
            hingeYFraction: GachaPackOpeningRules.authoredSeamYFraction,
            rotationDegrees: peelHingeDegrees * tearFront
                + exitRotationDegrees * easedExit,
            offsetXPoints: exitDriftPoints * easedExit,
            offsetYPoints: -GachaPackOpeningRules.sealExitLiftPoints
                * easedExit,
            undersideDepthPoints: undersideDepthPoints,
            opacity: GachaPackOpeningRules.sealExitOpacity(progress: progress),
            usesCrossfade: crossfadeEnabled)
    }

    /// Lowest lid point after the hinge transform, in artwork points.
    public static func lowestEdgePoints(
        progress: Double,
        artworkWidthPoints: Double = GachaPackOpeningRules.artworkWidthPoints,
        artworkHeightPoints: Double = GachaPackOpeningRules.artworkHeightPoints
    ) -> Double {
        let pose = pose(
            progress: progress,
            artworkWidthPoints: artworkWidthPoints,
            artworkHeightPoints: artworkHeightPoints)
        let seamY = artworkHeightPoints * pose.hingeYFraction
        let radians = pose.rotationDegrees * .pi / 180
        let span = (pose.trailingFraction - pose.leadingFraction)
            * artworkWidthPoints
        // Points left of the hinge move up for positive rotation; the hinge
        // column itself is the lowest edge unless the lid rotates backward.
        let farEndDrop = -span * sin(radians)
        return seamY + GachaPackOpeningRules.tornEdgeAmplitudePoints
            + max(0, farEndDrop)
            + pose.undersideDepthPoints
            + pose.offsetYPoints
    }

    /// Highest lid point after the hinge transform, in artwork points.
    public static func highestEdgePoints(
        progress: Double,
        artworkWidthPoints: Double = GachaPackOpeningRules.artworkWidthPoints,
        artworkHeightPoints: Double = GachaPackOpeningRules.artworkHeightPoints
    ) -> Double {
        let pose = pose(
            progress: progress,
            artworkWidthPoints: artworkWidthPoints,
            artworkHeightPoints: artworkHeightPoints)
        let packTop = artworkHeightPoints
            * GachaPackOpeningRules.authoredPackTopYFraction
        let radians = pose.rotationDegrees * .pi / 180
        let span = (pose.trailingFraction - pose.leadingFraction)
            * artworkWidthPoints
        let farEndLift = span * sin(radians)
        return packTop - max(0, farEndLift) + pose.offsetYPoints
    }

    /// The attached peel must stay a compact top-edge event. It may lift a
    /// little above the Pack top, but never reach into the artwork body.
    public static func staysWithinCompactTopArea(
        progress: Double,
        artworkWidthPoints: Double = GachaPackOpeningRules.artworkWidthPoints,
        artworkHeightPoints: Double = GachaPackOpeningRules.artworkHeightPoints
    ) -> Bool {
        guard GachaPackOpeningRules.sealExitProgress(progress: progress) <= 0
        else {
            return lidClearsPackOutline(
                progress: progress,
                artworkWidthPoints: artworkWidthPoints,
                artworkHeightPoints: artworkHeightPoints)
        }
        let pose = pose(
            progress: progress,
            artworkWidthPoints: artworkWidthPoints,
            artworkHeightPoints: artworkHeightPoints)
        let lowest = lowestEdgePoints(
            progress: progress,
            artworkWidthPoints: artworkWidthPoints,
            artworkHeightPoints: artworkHeightPoints)
        let highest = highestEdgePoints(
            progress: progress,
            artworkWidthPoints: artworkWidthPoints,
            artworkHeightPoints: artworkHeightPoints)
        return pose.leadingFraction >= 0
            && pose.trailingFraction <= 1
            && lowest <= artworkHeightPoints * compactTopAreaBottomFraction
            && highest >= -artworkHeightPoints * 0.08
    }

    /// True once every lid point is above the Pack top edge.
    public static func lidClearsPackOutline(
        progress: Double,
        artworkWidthPoints: Double = GachaPackOpeningRules.artworkWidthPoints,
        artworkHeightPoints: Double = GachaPackOpeningRules.artworkHeightPoints
    ) -> Bool {
        lowestEdgePoints(
            progress: progress,
            artworkWidthPoints: artworkWidthPoints,
            artworkHeightPoints: artworkHeightPoints) < 0
    }

    /// A single lid is rigid by construction; keep the contract explicit.
    public static func departsAsRigidLid(progress: Double) -> Bool {
        GachaPackOpeningRules.sealExitProgress(progress: progress) >= 1
            && pose(progress: progress).isVisible
    }

    private static func clamped(_ value: Double) -> Double {
        min(max(value, 0), 1)
    }
}

public enum GachaPackHandoffRules {
    public static let nativeHybridCandidateLaunchArgument =
        "--premium-display-case-gate04-native-hybrid-candidate"
    public static let nativeHybridCandidatePreviewToken =
        "premium-display-case-gate04-native-hybrid-r026"
    public static let nativeHybridTearLeadInNanoseconds: UInt64 =
        80_000_000
    public static let nativeHybridTearDurationSeconds = 0.32
    /// The authoritative draw is requested at commit so the case is staged
    /// before the pull starts at T0 + 0.70 s.
    public static let drawAfterLidClearNanoseconds: UInt64 = 0
    /// Pull may not start before this much time after commit
    /// (T0 + 700 ms − 320 ms tear), even if Unity is ready earlier.
    public static let caseReadyMinimumAfterCommitNanoseconds: UInt64 =
        380_000_000
    /// Beat between Unity readiness and the case starting to rise. Kept at
    /// 120 ms: with 40 ms the case's first frames still block the main
    /// thread and the native Pack drop freezes into a hard cut.
    public static let nativeHybridContainmentHoldNanoseconds: UInt64 =
        120_000_000
    public static let nativeHybridCaseRiseDurationSeconds = 0.64
    public static let nativeHybridPackLipCrossingProgress = 0.58
    public static let nativeHybridSequenceDurationSeconds =
        0.08 + nativeHybridTearDurationSeconds
            + GachaPackOpeningRules.flapExitDurationSeconds + 0.12
            + nativeHybridCaseRiseDurationSeconds
    /// Pack exit, released on the first case frame so it leads the pull.
    /// rev-006 review (2026-09-06): the Pack must complete its fall — down
    /// to near the bottom of the stage — and only fade once it is almost
    /// there. rev-009 review (gacha-reveal-timeline canvas): 1.0 → 0.58 s
    /// `cubic-bezier(0.33, 0, 0.2, 1)`, rotateX +14°.
    public static let nativeHybridPackDepartureDurationSeconds = 0.58
    /// Fall distance as a fraction of the stage height (centre 44% → 94%).
    public static let packDepartureDropFraction = 0.50
    public static let packDepartureTiltDegrees = 14.0
    /// Solid for most of the fall; the fade only starts near the bottom.
    public static let packDepartureFadeStartProgress = 0.78

    public static func packDepartureOpacity(retreatProgress: Double) -> Double {
        let start = packDepartureFadeStartProgress
        guard retreatProgress > start else { return 1 }
        let t = min(1, (retreatProgress - start) / (1 - start))
        return 1 - t * t * (3 - 2 * t)
    }
    /// Shared-geometry id: the carousel's selected Pack and the tear stage
    /// Pack are one view to SwiftUI, so selection animates as travel.
    public static let selectedPackGeometryID = "gacha-selected-pack"
    /// Shipping stage handoff: the Pack-hue backdrop fades into the live
    /// Unity stage once the case is staged behind the Pack.
    public static let stageBackdropFadeSeconds = 0.28
    /// Unity publishes `complete` as the label lands (T0 + 3.96 s with the
    /// 0.24 s Pack lead); the result panel slides in 300 ms later.
    public static let resultPanelDelayNanoseconds: UInt64 = 300_000_000
    public static let resultPanelSlideSeconds = 0.42
    /// Idle loop while the sealed Pack waits for the tear (spec §1.4).
    /// R051 (user 2026-09-08 12:16 "太有漂浮感"): halved from 6 pt / 4° so
    /// the Pack rests on the stage instead of hovering; the tier wriggle and
    /// the foil parallax now carry the life.
    public static let idleFloatAmplitudePoints = 3.0
    public static let idleFloatPeriodSeconds = 3.0
    public static let idleYawDegrees = 2.0
    public static let idleYawPeriodSeconds = 3.6
    public static let idleSealSweepIntervalSeconds = 1.8
    public static let idleSealSweepSeconds = 0.7
    public static let idleSealSweepWidthPoints = 8.0
    /// Seal hit area and triggers (spec §1.5).
    public static let sealHitAreaHeightPoints = 72.0
    public static let sealLongPressSeconds = 0.45
    /// Selection → tear stage: the Pack travels to (50%, 44%) and grows
    /// 1.18× over 600 ms; the rest of the carousel fades in 250 ms.
    public static let selectionTravelSeconds = 0.6
    public static let selectionFadeSeconds = 0.25
    public static let selectionScale = 1.18
    public static let stagePackCenterYFraction = 0.44
    /// Mouth gape at commit: scaleY 1 → 1.06, 180 ms overshoot.
    public static let mouthGapeScale = 1.06
    public static let mouthGapeSeconds = 0.18

    public static var isNativeHybridCandidatePreview: Bool {
#if FIDGET_GATE04_NATIVE_HYBRID_CANDIDATE
        return true
#else
        return ProcessInfo.processInfo.arguments.contains(
            nativeHybridCandidateLaunchArgument)
            || ProcessInfo.processInfo.environment[
                "FIDGET_GATE04_NATIVE_HYBRID"] == "1"
#endif
    }

    public static func showsPack(
        revealComplete: Bool,
        retreatProgress: Double
    ) -> Bool {
        !revealComplete && retreatProgress < 1
    }

    public static func hasVisibleForeground(
        packVisible: Bool,
        realCaseReady: Bool
    ) -> Bool {
        packVisible || realCaseReady
    }

    public static func canRevealLiveCase(
        hasAuthoritativeReceipt: Bool,
        caseStableAfterTwoFrames: Bool,
        openingProgress: Double
    ) -> Bool {
        hasAuthoritativeReceipt
            && caseStableAfterTwoFrames
            && GachaPackOpeningRules.shouldCommit(progress: openingProgress)
    }

    public static func packArtIsForeground(
        packVisible: Bool,
        retreatProgress: Double
    ) -> Bool {
        packVisible && retreatProgress < 1
    }
}

public enum GachaNativeHybridStaticStage: String {
    case sealed
    case partial
    case emptyMouth = "empty-mouth"
    case containedCase = "contained-case"
    case caseCrossing = "case-crossing"

    private static let launchArgumentPrefix =
        "--premium-display-case-gate04-native-hybrid-static="

    public static var requested: Self? {
        guard GachaPackHandoffRules.isNativeHybridCandidatePreview else {
            return nil
        }
        return parse(arguments: ProcessInfo.processInfo.arguments)
    }

    public static func parse(arguments: [String]) -> Self? {
        guard let argument = arguments.last(where: {
            $0.hasPrefix(launchArgumentPrefix)
        }) else {
            return nil
        }
        return Self(rawValue: String(argument.dropFirst(
            launchArgumentPrefix.count)))
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
    // itemSpacingPoints is close to a phone's half-width so a neighbor's
    // center sits near the screen edge, leaving roughly half of it visible
    // (peeking in), not a fully-shown smaller card beside the selection.
    public static let itemSpacingPoints: Double = 200
    public static let selectionCommitPoints: Double = 56
    // A wide gap between selected/unselected scale so the spring transition
    // reads as a clear "center pops up, sides get pushed away" motion
    // instead of the ~6% size delta the original 0.66/0.70 pair produced.
    public static let unselectedPackScale: Double = 0.62
    public static let selectedPackScale: Double = 1.0
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

    // Detent snap (user 2026-09-07 19:39: "吸附效果不够强，一滑就滑两档").
    // The drag is shaped like a magnetic detent: held near the current Pack,
    // then accelerating past the midpoint, never travelling beyond the
    // neighbour. Release commits one step only, by distance or by flick.
    /// Fraction of `itemSpacingPoints` the finger must travel to commit.
    public static let detentCommitFraction = 0.42
    /// Predicted extra travel (flick) that commits a step on its own.
    public static let flickCommitPoints = 140.0
    /// Displayed travel per finger travel while inside the detent hold.
    /// 0.7 → 0.92 → 1.0 (user 2026-09-08 18:48 / 22:31 "不太跟手"): the
    /// one-step release rule prevents skipping, so the Pack tracks 1:1.
    public static let detentHoldGain = 1.0
    /// Beyond the neighbour the carousel only rubber-bands this much.
    public static let overshootGain = 0.25
    /// Snap spring: ζ ≈ 1.15, slightly over-damped and softer (k 420 → 300)
    /// so the landing reads heavy (user 22:31 "snap 的阻尼感不够强").
    public static let snapStiffness = 300.0
    public static let snapDamping = 40.0

    /// Finger travel → displayed travel (points).
    public static func displayedTranslation(translationPoints: Double) -> Double {
        let p = translationPoints / itemSpacingPoints
        let magnitude = abs(p)
        let sign: Double = p < 0 ? -1 : 1
        if magnitude > 1 {
            return sign * (1 + (magnitude - 1) * overshootGain) * itemSpacingPoints
        }
        // smoothstep(0.3, 0.8): held at 0.7× until 30%, unity gain by 80%.
        let w = min(max((magnitude - 0.3) / 0.5, 0), 1)
        let weight = w * w * (3 - 2 * w)
        let gain = detentHoldGain + (1 - detentHoldGain) * weight
        return sign * magnitude * gain * itemSpacingPoints
    }

    /// One step at most per release; a flick counts when the predicted end
    /// travel adds `flickCommitPoints` in the same direction.
    public static func stepForRelease(
        translationPoints: Double,
        predictedEndTranslationPoints: Double
    ) -> Int {
        let commit = itemSpacingPoints * detentCommitFraction
        let flick = predictedEndTranslationPoints - translationPoints
        let sameDirectionFlick = flick * translationPoints > 0 && abs(flick) >= flickCommitPoints
        if translationPoints <= -commit || (translationPoints < 0 && sameDirectionFlick) {
            return 1
        }
        if translationPoints >= commit || (translationPoints > 0 && sameDirectionFlick) {
            return -1
        }
        return 0
    }

    public static func nextIndex(
        selectedIndex: Int,
        itemCount: Int,
        translationPoints: Double,
        predictedEndTranslationPoints: Double
    ) -> Int {
        guard itemCount > 0 else { return 0 }
        return min(
            max(
                selectedIndex + stepForRelease(
                    translationPoints: translationPoints,
                    predictedEndTranslationPoints: predictedEndTranslationPoints),
                0),
            itemCount - 1)
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

public enum GachaNativeHybridR027StaticStage: String {
    case sealed
    case partial
    case emptyMouth = "empty-mouth"
    case containedCase = "contained-case"
    case caseCrossing = "case-crossing"

    static func parse(arguments: [String]) -> Self? {
        let prefix =
            "--premium-display-case-gate04-native-hybrid-r027-static="
        guard let argument = arguments.last(where: {
            $0.hasPrefix(prefix)
        }) else {
            return nil
        }
        return Self(rawValue: String(argument.dropFirst(prefix.count)))
    }
}

public enum GachaNativeHybridR027Rules {
    public static let launchArgument =
        "--premium-display-case-gate04-native-hybrid-r027"
    public static let previewToken =
        "premium-display-case-gate04-native-hybrid-r027"

    public static var isIsolatedCandidate: Bool {
        ProcessInfo.processInfo.arguments.contains(launchArgument)
            || ProcessInfo.processInfo.environment[
                "FIDGET_GATE04_NATIVE_HYBRID_R027"] == "1"
    }

    public static var requestedStaticStage:
        GachaNativeHybridR027StaticStage? {
        guard isIsolatedCandidate else { return nil }
        return GachaNativeHybridR027StaticStage.parse(
            arguments: ProcessInfo.processInfo.arguments)
    }
}

public enum GachaNativeHybridR028StaticStage: String {
    case sealed
    case partial
    case preReadyMouth = "pre-ready-mouth"
    case containedCase = "contained-case"
    case caseCrossing = "case-crossing"
    case packDeparted = "pack-departed"

    private static let launchArgumentPrefix =
        "--premium-display-case-gate04-native-hybrid-r028-static="

    public static func parse(arguments: [String]) -> Self? {
        guard let argument = arguments.last(where: {
            $0.hasPrefix(launchArgumentPrefix)
        }) else {
            return nil
        }
        return Self(rawValue: String(argument.dropFirst(
            launchArgumentPrefix.count)))
    }

    var holdsApertureClosed: Bool {
        switch self {
        case .sealed, .partial, .preReadyMouth:
            return true
        case .containedCase, .caseCrossing, .packDeparted:
            return false
        }
    }
}

public enum GachaNativeHybridR028Rules {
    public static let launchArgument =
        "--premium-display-case-gate04-native-hybrid-r028"
    public static let previewToken =
        "premium-display-case-gate04-native-hybrid-r028"

    public static var isIsolatedCandidate: Bool {
        ProcessInfo.processInfo.arguments.contains(launchArgument)
            || ProcessInfo.processInfo.environment[
                "FIDGET_GATE04_NATIVE_HYBRID_R028"] == "1"
    }

    public static var requestedStaticStage:
        GachaNativeHybridR028StaticStage? {
        guard isIsolatedCandidate else { return nil }
        return GachaNativeHybridR028StaticStage.parse(
            arguments: ProcessInfo.processInfo.arguments)
    }
}

public enum GachaNativeHybridR029CaptureCheckpoint: String, CaseIterable {
    case sealed
    case partial
    case f0 = "F0"
    case f1 = "F1"
    case f2 = "F2"
    case f3 = "F3"
    case f4 = "F4"
}

public enum GachaNativeHybridR029Rules {
    public static let launchArgument =
        "--premium-display-case-gate04-native-hybrid-r029"
    public static let previewToken =
        "premium-display-case-gate04-native-hybrid-r029"
    private static let captureArgumentPrefix =
        "--premium-display-case-gate04-native-hybrid-r029-capture="

    public static var isIsolatedCandidate: Bool {
        ProcessInfo.processInfo.arguments.contains(launchArgument)
            || ProcessInfo.processInfo.environment[
                "FIDGET_GATE04_NATIVE_HYBRID_R029"] == "1"
    }

    public static var requestedCaptureCheckpoint:
        GachaNativeHybridR029CaptureCheckpoint? {
        guard isIsolatedCandidate,
              let argument = ProcessInfo.processInfo.arguments.last(where: {
                  $0.hasPrefix(captureArgumentPrefix)
              }) else {
            return nil
        }
        return GachaNativeHybridR029CaptureCheckpoint(rawValue: String(
            argument.dropFirst(captureArgumentPrefix.count)))
    }
}

public enum GachaNativeHybridR030CaptureCheckpoint: String, CaseIterable {
    case sealed
    case partial
    case f0 = "F0"
    case f1 = "F1"
    case f2 = "F2"
    case f3 = "F3"
    case f4 = "F4"
}

public enum GachaNativeHybridR030Rules {
    public static let launchArgument =
        "--premium-display-case-gate04-native-hybrid-r030"
    public static let previewToken =
        "premium-display-case-gate04-native-hybrid-r030"
    private static let captureArgumentPrefix =
        "--premium-display-case-gate04-native-hybrid-r030-capture="

    public static var isIsolatedCandidate: Bool {
        ProcessInfo.processInfo.arguments.contains(launchArgument)
            || ProcessInfo.processInfo.environment[
                "FIDGET_GATE04_NATIVE_HYBRID_R030"] == "1"
    }

    public static var requestedCaptureCheckpoint:
        GachaNativeHybridR030CaptureCheckpoint? {
        guard isIsolatedCandidate,
              let argument = ProcessInfo.processInfo.arguments.last(where: {
                  $0.hasPrefix(captureArgumentPrefix)
              }) else {
            return nil
        }
        return GachaNativeHybridR030CaptureCheckpoint(rawValue: String(
            argument.dropFirst(captureArgumentPrefix.count)))
    }
}

/// Idle loop shared by the carousel's resting Pack and the sealed Pack on the
/// tear stage (spec §1.4). Both evaluate the same clock, so selecting a Pack
/// keeps its float and yaw phase across the matched-geometry move.
/// Holographic ("镭射") foil sheen on the sealed Pack, coupled to device
/// motion (user request 2026-09-07 16:57; reference: LerSentAI parallax
/// laser card, x.com/LerSentAI/status/2096554307235590208). Tilting the
/// phone slides a wide iridescent band across the foil and tilts the Pack
/// like a card in the hand; a shake fires one full laser sweep. The only
/// inputs are device motion and the idle clock — never receipt or rarity.
public enum GachaPackHolographicSheenRules {
    /// Sheen travel (fraction of Pack width) at full tilt (|gravity| = 1 g).
    public static let tiltTravelFraction = 0.60
    /// Gain on the gravity vector before clamping to the travel.
    public static let tiltGain = 1.6
    /// Vertical tilt moves the band less than horizontal tilt.
    public static let verticalTiltWeight = 0.35
    /// The Pack itself follows the tilt (card-in-hand parallax). R051y (user
    /// 2026-09-09 09:06, after holo-card's ±28° card): 9/6 °/g read as a
    /// sticker; gravity is ≈ sin(tilt), so 34 °/g is close to 1:1 for hand
    /// tilts, clamped so the sachet never turns edge-on.
    public static let tiltYawDegreesPerG = 34.0
    public static let tiltPitchDegreesPerG = 22.0
    public static let tiltYawClampDegrees = 22.0
    public static let tiltPitchClampDegrees = 14.0
    /// Print-layer parallax (fraction of Pack width at full yaw clamp;
    /// vertical uses `verticalTiltWeight` of it). holo-card moves its
    /// foreground `view·0.08·depth`; this is the sachet-scale equivalent.
    /// R051z (user 09:58 "彼此独立"): 0.035 → 0.02 so the print reads as part
    /// of the same object, not a third thing moving.
    public static let printParallaxFraction = 0.02
    /// View-following specular (holo-card `glare`). R051z (user 09-09 09:58
    /// "高光点要有强反光材质承载；雾面不会有横线高光"): no streak, no halo on
    /// the matte body. One broad soft gloss, masked to the metal print (rim,
    /// panel frame, emblem, type) so it lands only where metal is.
    public static let glareCoreOpacity = 0.55
    public static let glareCoreRadiusFraction = 0.16
    public static let glareFringeOpacity = 0.22
    public static let glareTravelFraction = 0.45
    /// Whole-glare gain: 1 at rest, `glareSweepBoost` at the sweep peak.
    public static let glareSweepBoost = 1.35
    /// Tinted drop shadow behind the Pack (R051z, replaces the white contour
    /// glow): the pouch silhouette in the tier accent, darkened, wide blur,
    /// dropped a little; deeper and wider on a sweep.
    public static let shadowRestOpacity = 0.62
    public static let shadowSweepOpacity = 0.85
    public static let shadowBlurPoints = 36.0
    public static let shadowScale = 1.08
    public static let shadowDropPoints = 12.0
    /// Accent luminance multiplier for the shadow colour (subtle, not neon).
    public static let shadowTintScale = 0.7
    /// Low-pass time constant on gravity; removes hand jitter at 60 Hz.
    public static let tiltSmoothingSeconds = 0.10
    /// Without device motion the band rides the idle yaw.
    public static let idleTravelFraction = 0.22
    /// Carousel parallax (user 2026-09-08 12:16: the foil looked detached
    /// from the print while swiping). The light stays fixed to the screen, so
    /// as a Pack slides one slot to the right its highlight moves this far
    /// left across the print, clamped at `carouselTravelClamp`.
    public static let carouselTravelFraction = 0.45
    public static let carouselTravelClamp = 0.90
    /// Band geometry relative to the Pack width.
    /// R051z (user 09:58 "扩散面积再宽一些，太聚焦"): 0.55 → 0.85.
    public static let bandWidthFraction = 0.85
    public static let bandAngleDegrees = -26.0
    // R051x (user 2026-09-09 08:54 "太哑光，镭射感更强"): 0.30 / 0.78 → 0.45 / 0.95.
    public static let restOpacity = 0.45
    public static let sweepOpacity = 0.95

    // R051x diffraction model, after LerSent001/holo-card `renderer.js`:
    // a cosine-palette rainbow whose phase slides with the view, a light band
    // envelope on top, and sparse glints that only flash inside the band.
    /// Rainbow cycles across the band width.
    public static let spectrumCycles = 2.4
    /// Rainbow phase advance per unit of band offset (fraction of Pack width).
    public static let spectrumPhaseGain = 1.9
    /// Stripe strength inside the band; the white band core stays on top.
    public static let spectrumOpacity = 0.62
    /// Glints on the foil (deterministic positions); size in points.
    public static let glintCount = 26
    public static let glintSizePoints = 3.2
    public static let glintOpacity = 0.9

    /// `.52 + .48·cos(2π(t + (0, ⅓, ⅔)))`: a smooth spectrum in 0.04…1.
    public static func spectrum(_ t: Double) -> (red: Double, green: Double, blue: Double) {
        func channel(_ shift: Double) -> Double {
            0.52 + 0.48 * cos(2 * Double.pi * (t + shift))
        }
        return (channel(0), channel(1.0 / 3.0), channel(2.0 / 3.0))
    }

    /// Deterministic glint position (fractions of the Pack frame) for index `i`.
    public static func glintPosition(_ i: Int) -> (x: Double, y: Double) {
        func hash(_ v: Double) -> Double {
            let s = sin(v * 127.1 + 311.7) * 43758.5453
            return s - s.rounded(.down)
        }
        let seed = Double(i) + 1
        return (0.08 + 0.84 * hash(seed), 0.10 + 0.80 * hash(seed * 7.3))
    }

    /// Brightness 0…1 of a glint at `distanceFromBandCentre` (band widths).
    public static func glintEnvelope(distanceFromBandCentre: Double) -> Double {
        let d = max(0, 1 - abs(distanceFromBandCentre) * 2)
        return d * d
    }
    /// Laser sweep: one pass across the Pack after a shake.
    public static let sweepSeconds = 0.85
    public static let sweepPeakProgress = 0.22
    public static let sweepStartOffset = -1.25
    public static let sweepEndOffset = 1.25
    /// Shake detection on user acceleration magnitude (g), with hysteresis
    /// and a cooldown so a continuous shake fires at most one sweep per
    /// cooldown (repository invariant for shake input).
    public static let shakeEnterG = 0.55
    public static let shakeExitG = 0.18
    public static let sweepCooldownSeconds = 1.2

    public static func tiltOffset(gravityX: Double, gravityY: Double) -> Double {
        let raw = (gravityX + gravityY * verticalTiltWeight) * tiltGain
            * tiltTravelFraction
        return min(max(raw, -tiltTravelFraction), tiltTravelFraction)
    }

    public static func tiltYawDegrees(gravityX: Double) -> Double {
        min(max(gravityX * tiltYawDegreesPerG, -tiltYawClampDegrees),
            tiltYawClampDegrees)
    }

    public static func tiltPitchDegrees(gravityY: Double) -> Double {
        min(max(gravityY * tiltPitchDegreesPerG, -tiltPitchClampDegrees),
            tiltPitchClampDegrees)
    }

    /// Print-layer shift (fractions of Pack width / height) for a pose. The
    /// print rides toward the tilt like a raised foreground in holo-card, so
    /// the emblem reads as embossed above the foil, not printed on it.
    public static func printParallax(pose: SheenPose) -> (x: Double, y: Double) {
        let yaw = pose.tiltYawDegrees / tiltYawClampDegrees
        let pitch = pose.tiltPitchDegrees / tiltPitchClampDegrees
        return (yaw * printParallaxFraction,
                -pitch * printParallaxFraction * verticalTiltWeight)
    }

    /// 0…1 how far the pose's brightness sits between rest and sweep peak.
    public static func sweepEnergy(pose: SheenPose) -> Double {
        let span = sweepOpacity - restOpacity
        guard span > 0 else { return 0 }
        return min(max((pose.opacity - restOpacity) / span, 0), 1)
    }

    public static func glareBoost(pose: SheenPose) -> Double {
        1 + (glareSweepBoost - 1) * sweepEnergy(pose: pose)
    }

    public static func shadowOpacity(pose: SheenPose) -> Double {
        shadowRestOpacity + (shadowSweepOpacity - shadowRestOpacity) * sweepEnergy(pose: pose)
    }

    /// Glare centre (unit coordinates) for a pose: rides the band offset
    /// horizontally and the pitch vertically, like holo-card's
    /// `glare` at `(.5 + view.x, .6 + view.y)`.
    public static func glareCenter(pose: SheenPose) -> (x: Double, y: Double) {
        let x = 0.5 + min(max(pose.offset, -1), 1) * glareTravelFraction
        let y = 0.58 - pose.tiltPitchDegrees / tiltPitchClampDegrees * 0.22
        return (x, y)
    }

    /// In phase with `GachaPackIdleMotion.yawDegrees`.
    public static func idleOffset(elapsed: Double, amplitude: Double = 1) -> Double {
        let period = GachaPackHandoffRules.idleYawPeriodSeconds
        return idleTravelFraction * sin(2 * Double.pi * elapsed / period) * amplitude
    }

    /// Band shift from the Pack's continuous carousel slot (0 = centred).
    public static func carouselOffset(continuousPosition: Double) -> Double {
        let raw = -continuousPosition * carouselTravelFraction
        return min(max(raw, -carouselTravelClamp), carouselTravelClamp)
    }

    /// Exponential smoothing weight for one frame of `deltaSeconds`.
    public static func smoothingWeight(deltaSeconds: Double) -> Double {
        guard deltaSeconds > 0 else { return 0 }
        return 1 - exp(-deltaSeconds / tiltSmoothingSeconds)
    }

    /// 0…1 while a sweep is running, nil before the trigger or after it ends.
    public static func sweepProgress(sinceTrigger seconds: Double?) -> Double? {
        guard let seconds, seconds >= 0, seconds < sweepSeconds else { return nil }
        return seconds / sweepSeconds
    }

    /// Band offset during a sweep: eased pass from off-left to off-right.
    public static func sweepOffset(progress: Double) -> Double {
        let t = min(max(progress, 0), 1)
        let eased = t < 0.5 ? 2 * t * t : 1 - pow(-2 * t + 2, 2) / 2
        return sweepStartOffset + (sweepEndOffset - sweepStartOffset) * eased
    }

    /// Opacity during a sweep: quick rise to the laser peak, long fall back.
    public static func sweepOpacity(progress: Double) -> Double {
        let t = min(max(progress, 0), 1)
        if t < sweepPeakProgress {
            return restOpacity + (sweepOpacity - restOpacity) * (t / sweepPeakProgress)
        }
        let fall = (t - sweepPeakProgress) / (1 - sweepPeakProgress)
        return sweepOpacity + (restOpacity - sweepOpacity) * fall
    }

    /// Per-frame sheen and Pack tilt.
    public struct SheenPose: Equatable {
        /// Band centre as a fraction of the Pack width (negative = left).
        public var offset: Double
        public var opacity: Double
        public var tiltYawDegrees: Double
        public var tiltPitchDegrees: Double

        public init(
            offset: Double,
            opacity: Double,
            tiltYawDegrees: Double,
            tiltPitchDegrees: Double
        ) {
            self.offset = offset
            self.opacity = opacity
            self.tiltYawDegrees = tiltYawDegrees
            self.tiltPitchDegrees = tiltPitchDegrees
        }

        public static let rest = SheenPose(
            offset: 0,
            opacity: GachaPackHolographicSheenRules.restOpacity,
            tiltYawDegrees: 0,
            tiltPitchDegrees: 0)
    }

    /// Combines the idle clock, device tilt and a running sweep. Reduce
    /// Motion keeps the band still and turns the sweep into a brightness
    /// pulse; the Pack never tilts with the device.
    public static func pose(
        elapsed: Double,
        idleAmplitude: Double,
        gravityX: Double,
        gravityY: Double,
        sweepProgress: Double?,
        reduceMotion: Bool,
        carouselPosition: Double = 0
    ) -> SheenPose {
        var offset = reduceMotion ? 0 : idleOffset(elapsed: elapsed, amplitude: idleAmplitude)
        var opacity = restOpacity
        var yaw = 0.0
        var pitch = 0.0
        // Carousel parallax applies under Reduce Motion too: it is not
        // motion of its own, it follows a slide the user already made.
        offset += carouselOffset(continuousPosition: carouselPosition)
        if !reduceMotion {
            offset += tiltOffset(gravityX: gravityX, gravityY: gravityY)
            yaw = tiltYawDegrees(gravityX: gravityX)
            pitch = tiltPitchDegrees(gravityY: gravityY)
        }
        if let sweepProgress {
            opacity = sweepOpacity(progress: sweepProgress)
            if !reduceMotion {
                offset = sweepOffset(progress: sweepProgress)
            }
        }
        return SheenPose(
            offset: offset,
            opacity: opacity,
            tiltYawDegrees: yaw,
            tiltPitchDegrees: pitch)
    }
}

/// Shake detector on user-acceleration magnitude with hysteresis and cooldown.
/// Never uses attitude deltas (raw wrapped Euler subtraction is invalid).
public struct GachaPackShakeDetector {
    public private(set) var armed = true
    public private(set) var lastTriggerTime: Double? = nil

    public init() {}

    /// Feed one sample; returns true exactly when a sweep should fire.
    public mutating func ingest(userAccelerationG magnitude: Double, time: Double) -> Bool {
        if !armed && magnitude < GachaPackHolographicSheenRules.shakeExitG {
            armed = true
        }
        guard armed, magnitude >= GachaPackHolographicSheenRules.shakeEnterG else {
            return false
        }
        if let last = lastTriggerTime,
           time - last < GachaPackHolographicSheenRules.sweepCooldownSeconds {
            return false
        }
        armed = false
        lastTriggerTime = time
        return true
    }
}

/// Draw funding for the shipping storefront. Device bug 2026-09-07 19:39
/// ("每次一开包就卡住了"): with 0 tickets Unity answered the ticket draw with
/// `insufficient-tickets`, the storefront never read the failure and sat
/// 20 s until the receipt timeout. The storefront now pays with what the
/// player has, disables the CTA when nothing can pay, and aborts the tear
/// the moment Unity reports a failure.
public enum GachaPackPaymentRules {
    public enum Method: Equatable {
        case ticket
        case coins
    }

    /// Mirrors `GachaEconomyRules.SingleDrawTicketCost` / `SingleDrawCoinCost`.
    public static let singleDrawTicketCost = 1
    public static let singleDrawCoinCost = 160
    public static let failureNoticeSeconds = 3.2

    public static func method(tickets: Int, coins: Int) -> Method? {
        if tickets >= singleDrawTicketCost { return .ticket }
        if coins >= singleDrawCoinCost { return .coins }
        return nil
    }

    public static func priceLine(tickets: Int, coins: Int) -> String {
        switch method(tickets: tickets, coins: coins) {
        case .ticket?:
            return "一张抽取券 · 余 \(tickets) 张"
        case .coins?:
            return "\(singleDrawCoinCost) 硬币 · 余 \(coins)"
        case nil:
            return "抽取券不足 · 硬币 \(coins)/\(singleDrawCoinCost)"
        }
    }

    public static func failureMessage(reason: String) -> String {
        switch reason {
        case "insufficient-tickets": return "抽取券不足，这次没有开包"
        case "insufficient-coins": return "硬币不足，这次没有开包"
        case "transaction-in-flight": return "上一次抽取还没结束，稍后再试"
        case "unknown-series": return "这个系列暂时不可抽取"
        default: return "开包失败（\(reason)）"
        }
    }
}

/// Bottom glow growth when the carousel changes tier (user 2026-09-07
/// 19:39: "从底部向上扩散的 ripple effect"; 22:41: the first full-screen
/// circular wipe was not visible). The coloured floor glow now grows upward
/// as a wide ellipse. A soft echo follows the leading edge.
public enum GachaPackBackdropRippleRules {
    /// Growth runs linear in time; `growth(progress:)` owns the whole curve.
    /// 1.3 s trailed the 0.3 s snap (user 22:31 "圆形渐变再同步一些").
    public static let seconds = 0.7
    /// The rest of the backdrop (hue wash, arc bands) crossfades only after
    /// the floor glow has started to grow, so the new colour is first seen
    /// rising from the bottom rather than switching everywhere at once.
    public static let backdropFollowDelaySeconds = 0.12
    public static let backdropFollowSeconds = 0.5
    /// Floor line (fraction of height) the glow grows from.
    public static let originYFraction = 0.96
    public static let widthFraction = 1.6
    public static let heightFraction = 0.8
    public static let initialXScale = 0.16
    public static let initialYScale = 0.035
    public static let peakOpacity = 0.92
    public static let settledOpacity = 0.46
    public static let echoDelayProgress = 0.16
    public static let echoLineWidthPoints = 1.2
    public static let echoBlurPoints = 3.0

    public static func growth(progress: Double) -> Double {
        let p = min(max(progress, 0), 1)
        return 1 - pow(1 - p, 3)
    }

    public static func xScale(progress: Double) -> Double {
        initialXScale + (1 - initialXScale) * growth(progress: progress)
    }

    public static func yScale(progress: Double) -> Double {
        initialYScale + (1 - initialYScale) * growth(progress: progress)
    }

    /// Bright at launch, then settles into the persistent floor glow.
    public static func opacity(progress: Double) -> Double {
        let p = min(max(progress, 0), 1)
        let launch = sin(Double.pi * min(p / 0.58, 1))
        return settledOpacity + (peakOpacity - settledOpacity) * launch
    }

    public static func echoProgress(progress: Double) -> Double {
        min(max(
            (progress - echoDelayProgress) / (1 - echoDelayProgress),
            0), 1)
    }

    public static func echoOpacity(progress: Double) -> Double {
        let e = echoProgress(progress: progress)
        return 0.34 * sin(Double.pi * e)
    }
}

/// Ambient life in the backdrop (user 2026-09-07 19:39: "背景不应该有点效果
/// 吗，比如粒子或者过光"). R050 removes the full-screen diagonal sweep:
/// it read as a fake overlay. Fine dust now carries the ambient detail.
///
/// R051 (user 2026-09-08 12:16): hard-edged tier-colour discs with a
/// halo disc behind them read as "大圆套小圆" and set off trypophobia. Every
/// mote is now a soft radial glow with no hard edge; the nearest ones are
/// four-point star sparkles (星芒). Rise speed climbs with tier so richer
/// Packs feel more urgent, not just denser.
public enum GachaPackBackdropAmbienceRules {
    public struct Mote {
        public var x: Double
        public var y: Double
        /// Glow radius (the visible core is ~40 % of this).
        public var radiusPoints: Double
        public var alpha: Double
        /// Nearest motes render as a star sparkle instead of a plain glow.
        public var sparkle: Bool
        /// Star spike length in points (0 for plain glows); twinkles.
        public var spikePoints: Double
    }

    public static func moteCount(for tier: GachaPackTier) -> Int {
        [36, 44, 52, 62, 72, 84][GachaPackTierLadder.index(of: tier)]
    }

    /// Alpha scale per tier. R050's 0.13–0.34 with sub-point radii vanished
    /// on a 3× screen and in h264 (user 2026-09-08 07:13 "粒子效果又没了").
    public static func moteBaseAlpha(for tier: GachaPackTier) -> Double {
        [0.72, 0.78, 0.84, 0.90, 0.95, 1.0][GachaPackTierLadder.index(of: tier)]
    }

    /// Rise-speed multiplier per tier: 1 OF 1 drifts 2.8× faster than
    /// STANDARD. The view integrates travel across tier changes so a swipe
    /// never teleports the field.
    public static func riseSpeedScale(for tier: GachaPackTier) -> Double {
        [1.0, 1.25, 1.55, 1.9, 2.3, 2.8][GachaPackTierLadder.index(of: tier)]
    }

    /// Travel accumulated since `travelAtChange` at the tier's speed.
    public static func travel(
        travelAtChange: Double,
        secondsSinceChange: Double,
        tier: GachaPackTier
    ) -> Double {
        travelAtChange + max(secondsSinceChange, 0) * riseSpeedScale(for: tier)
    }

    /// Glow radius by depth: most motes stay fine (0.8–1.3 pt); only the
    /// nearest ~15 % reach `maxRadiusPoints` as soft bokeh.
    public static let minRadiusPoints = 0.8
    public static let maxRadiusPoints = 2.6
    public static func radiusPoints(depth: Double) -> Double {
        minRadiusPoints + (maxRadiusPoints - minRadiusPoints) * pow(depth, 2.4)
    }

    /// Nearest motes render as star sparkles.
    public static let sparkleDepthThreshold = 0.8
    /// Star spike length relative to the glow radius, at full twinkle.
    public static let sparkleSpikeScale = 3.2
    /// Star spike half-width at the core, in points.
    public static let sparkleSpikeWaistPoints = 0.45
    /// Fraction of the glow radius that is fully lit before the falloff.
    public static let glowCoreFraction = 0.35

    /// Dust is drawn in the tier colour lifted toward white so it separates
    /// from the near-black wash; STANDARD's silver (0.58/0.60/0.64) on the
    /// dark floor was otherwise invisible.
    public static let dustWhiteMix = 0.45
    public static func dustRGB(
        red: Double, green: Double, blue: Double
    ) -> (red: Double, green: Double, blue: Double) {
        (red + (1 - red) * dustWhiteMix,
         green + (1 - green) * dustWhiteMix,
         blue + (1 - blue) * dustWhiteMix)
    }

    static func hash(_ seed: Double) -> Double {
        let v = sin(seed * 12.9898) * 43758.5453
        return v - v.rounded(.down)
    }

    /// Mote `index` at `elapsed` seconds with STANDARD's rise speed.
    public static func mote(index: Int, elapsed: Double, tier: GachaPackTier) -> Mote {
        mote(
            index: index,
            elapsed: elapsed,
            travel: elapsed * riseSpeedScale(for: tier),
            tier: tier)
    }

    /// Mote `index`: `elapsed` drives sway and twinkle (tier-independent, so
    /// they never jump); `travel` drives the rise and is integrated by the
    /// view at the tier's speed. A mote leaving the top re-enters from the
    /// floor.
    public static func mote(
        index: Int,
        elapsed: Double,
        travel: Double,
        tier: GachaPackTier
    ) -> Mote {
        let i = Double(index)
        let h0 = hash(i + 1), h1 = hash(i + 17), h3 = hash(i + 73)
        // Golden-ratio stratification: any prefix of indices (a low tier's
        // smaller count) still spans the full depth and width evenly, so
        // STANDARD gets its share of near sparkles instead of only far dust.
        let h2 = (i * 0.618_033_988_7 + 0.31).truncatingRemainder(dividingBy: 1)
        let h4 = (i * 0.381_966_011_3 + 0.17).truncatingRemainder(dividingBy: 1)
        let depth = 0.35 + 0.65 * h4
        let speed = (0.007 + 0.014 * h1) * depth
        let swayPeriod = 3 + 3 * h2
        let sway = 0.010 * depth
            * sin(2 * Double.pi * elapsed / swayPeriod + h3 * 6.283)
        let y = 1 - ((h0 + travel * speed).truncatingRemainder(dividingBy: 1))
        let twinkle = 0.65 + 0.35 * sin(2 * Double.pi * elapsed / (1.5 + 1.5 * h4) + h0 * 6.283)
        let radius = radiusPoints(depth: depth)
        let sparkle = depth > sparkleDepthThreshold
        return Mote(
            x: min(max(0.05 + 0.90 * h2 + sway, 0), 1),
            y: y,
            radiusPoints: radius,
            alpha: moteBaseAlpha(for: tier) * (0.38 + 0.5 * depth) * twinkle,
            sparkle: sparkle,
            spikePoints: sparkle ? radius * sparkleSpikeScale * (0.55 + 0.45 * twinkle) : 0)
    }
}

/// Tier ladder for the carousel (user, 2026-09-07 18:54): the further right
/// you swipe, the more the Pack feels ready — a calm float at STANDARD, then
/// short bursts of wriggling/knocking that grow with tier, as if the prize
/// inside cannot wait to break out. Stepping up to a richer Pack also lands
/// heavier: the arriving Pack rises and settles, and the snap haptic gains
/// weight. Stepping down is a plain slide. Backdrop and foil are governed
/// elsewhere (FDB-GAC-035/036); this ladder is motion and touch only.
public enum GachaPackTierLadder {
    public static func index(of tier: GachaPackTier) -> Int {
        GachaPackTier.allCases.firstIndex(of: tier) ?? 0
    }

    /// Seconds between wriggle bursts; nil = never (STANDARD stays calm).
    public static func burstIntervalSeconds(for tier: GachaPackTier) -> Double? {
        [nil, 4.2, 3.2, 2.4, 1.8, 1.3][index(of: tier)]
    }

    public static func burstDurationSeconds(for tier: GachaPackTier) -> Double {
        [0, 0.55, 0.62, 0.70, 0.78, 0.85][index(of: tier)]
    }

    /// Peak sideways knock in points.
    public static func jitterPoints(for tier: GachaPackTier) -> Double {
        [0, 1.2, 2.0, 3.0, 4.2, 6.0][index(of: tier)]
    }

    /// Peak roll in degrees.
    public static func jitterDegrees(for tier: GachaPackTier) -> Double {
        [0, 0.8, 1.5, 2.4, 3.5, 5.0][index(of: tier)]
    }

    /// Peak scale swell (the Pack "breathes out" while it knocks).
    public static func scalePulse(for tier: GachaPackTier) -> Double {
        [0, 0.004, 0.008, 0.012, 0.016, 0.020][index(of: tier)]
    }

    /// Knock frequency: reads as knocking from inside, not a buzz.
    public static let jitterHertz = 11.0

    /// Points the arriving Pack rises before settling when stepping up.
    public static func arrivalRisePoints(for tier: GachaPackTier) -> Double {
        [0, 3, 4, 5, 6, 8][index(of: tier)]
    }

    public static let arrivalSettleSeconds = 0.55

    /// Semantic snap weight 0…1 for the Haptic recipe.
    public static func snapHapticSignal(for tier: GachaPackTier) -> Double {
        [0.30, 0.42, 0.56, 0.70, 0.85, 1.0][index(of: tier)]
    }

    /// 0…1 burst envelope × decaying knock at `elapsed` seconds; 0 between bursts.
    /// Deterministic: depends only on time and tier.
    public static func wriggle(elapsed: Double, tier: GachaPackTier) -> Double {
        guard let interval = burstIntervalSeconds(for: tier), elapsed > 0 else { return 0 }
        // Offset per tier so neighbouring Packs never knock in unison.
        let phase = (elapsed + Double(index(of: tier)) * 0.37)
            .truncatingRemainder(dividingBy: interval)
        let duration = burstDurationSeconds(for: tier)
        guard phase < duration else { return 0 }
        let t = phase / duration
        let envelope = sin(Double.pi * t)
        let decay = 1 - 0.5 * t
        return envelope * decay * sin(2 * Double.pi * jitterHertz * phase)
    }

    /// Sideways knock in points.
    public static func wriggleOffsetPoints(elapsed: Double, tier: GachaPackTier) -> Double {
        jitterPoints(for: tier) * wriggle(elapsed: elapsed, tier: tier)
    }

    /// Roll in degrees, a quarter-cycle behind the knock so it reads as a body, not a slide.
    public static func wriggleDegrees(elapsed: Double, tier: GachaPackTier) -> Double {
        jitterDegrees(for: tier)
            * wriggle(elapsed: elapsed + 0.25 / jitterHertz, tier: tier)
    }

    /// Scale swell 0…pulse following the burst envelope only.
    public static func wriggleScale(elapsed: Double, tier: GachaPackTier) -> Double {
        guard let interval = burstIntervalSeconds(for: tier), elapsed > 0 else { return 1 }
        let phase = (elapsed + Double(index(of: tier)) * 0.37)
            .truncatingRemainder(dividingBy: interval)
        let duration = burstDurationSeconds(for: tier)
        guard phase < duration else { return 1 }
        return 1 + scalePulse(for: tier) * sin(Double.pi * phase / duration)
    }

    /// Vertical arrival offset (negative is up) after a step up; 0 for a step down.
    public static func arrivalOffsetPoints(
        sinceSettle seconds: Double,
        steppedUp: Bool,
        tier: GachaPackTier
    ) -> Double {
        guard steppedUp, seconds >= 0, seconds < arrivalSettleSeconds else { return 0 }
        let t = seconds / arrivalSettleSeconds
        // Quick rise (first 30%), eased return.
        let rise = t < 0.3 ? sin(Double.pi * 0.5 * t / 0.3) : cos(Double.pi * 0.5 * (t - 0.3) / 0.7)
        return -arrivalRisePoints(for: tier) * rise
    }
}

public enum GachaPackIdleMotion {
    /// Amplitude ramps in over this long after the carousel settles.
    public static let rampInSeconds = 0.6

    public static func rampIn(sinceSettle seconds: Double) -> Double {
        guard seconds > 0 else { return 0 }
        let t = min(1, seconds / rampInSeconds)
        return t * t * (3 - 2 * t)
    }

    /// Vertical drift in points (negative is up), 0 ↔ -3 pt over 3.0 s.
    public static func offsetPoints(elapsed: Double, amplitude: Double = 1) -> Double {
        let period = GachaPackHandoffRules.idleFloatPeriodSeconds
        let phase = 0.5 - 0.5 * cos(2 * Double.pi * elapsed / period)
        return -GachaPackHandoffRules.idleFloatAmplitudePoints * phase * amplitude
    }

    /// Yaw about the vertical axis, ±2° over 3.6 s.
    public static func yawDegrees(elapsed: Double, amplitude: Double = 1) -> Double {
        let period = GachaPackHandoffRules.idleYawPeriodSeconds
        return GachaPackHandoffRules.idleYawDegrees
            * sin(2 * Double.pi * elapsed / period) * amplitude
    }

    /// 0…1 while the seal highlight is sweeping, nil between sweeps.
    public static func sealSweepProgress(elapsed: Double) -> Double? {
        guard elapsed >= GachaPackHandoffRules.selectionTravelSeconds else { return nil }
        let cycle = elapsed.truncatingRemainder(
            dividingBy: GachaPackHandoffRules.idleSealSweepIntervalSeconds)
        guard cycle < GachaPackHandoffRules.idleSealSweepSeconds else { return nil }
        return cycle / GachaPackHandoffRules.idleSealSweepSeconds
    }
}
