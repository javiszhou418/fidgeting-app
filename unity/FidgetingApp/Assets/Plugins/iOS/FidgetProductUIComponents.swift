import SwiftUI
import CoreText
import ImageIO
import UIKit

/// Shared visual tokens for the native product shell.
///
/// The values intentionally mirror the calm, dark, rounded hierarchy observed in
/// Opal without copying its artwork or product-specific layouts. Keep product
/// screens on these tokens so touch targets, glass fallbacks and motion timing do
/// not drift between features. Typography always uses the font's native spacing:
/// do not add tracking or kerning to create hierarchy.
enum FidgetUITokens {
    enum Size {
        static let minimumHitTarget: CGFloat = 44
        static let compactIconButton: CGFloat = 38
        static let primaryActionHeight: CGFloat = 52
        static let pageDot: CGFloat = 6
        static let selectedPageDotWidth: CGFloat = 18
        /// 28 read too small (user 2026-09-08 22:43 "icon 适当放大一点").
        static let headingEmblem: CGFloat = 36
    }

    enum Radius {
        static let compact: CGFloat = 16
        static let card: CGFloat = 22
        static let pill: CGFloat = 26
    }

    enum Spacing {
        static let compact: CGFloat = 4
        static let standard: CGFloat = 8
        static let section: CGFloat = 15
    }

    enum Opacity {
        static let primaryText = 0.92
        static let secondaryText = 0.58
        static let tertiaryText = 0.42
        static let selectedFill = 0.10
    }

    enum Motion {
        static let selectionDuration = 0.18
    }
}

/// One typography source for every native product surface.
///
/// Oxanium covers the product's Latin letters and numerals. Core Text keeps the
/// normal iOS cascade for glyphs the family does not ship (including Chinese),
/// so localized copy remains legible without mixing a second display face into
/// the Latin hierarchy.
enum ProductTypography {
    static let familyName = "Oxanium"
    static let resourceName = "Oxanium-VariableFont_wght"
    static let resourceExtension = "ttf"

    static func pointSize(for style: Font.TextStyle) -> CGFloat {
        switch style {
        case .largeTitle: return 34
        case .title: return 28
        case .title2: return 22
        case .title3: return 20
        case .headline, .body: return 17
        case .callout: return 16
        case .subheadline: return 15
        case .footnote: return 13
        case .caption: return 12
        case .caption2: return 11
        @unknown default: return 17
        }
    }

    static func registerBundledFontIfNeeded() {
        guard !UIFont.familyNames.contains(familyName),
              let url = Bundle.main.url(
                forResource: resourceName,
                withExtension: resourceExtension) else {
            return
        }
        CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
    }

    static func uiFont(size: CGFloat, weight: UIFont.Weight) -> UIFont {
        let descriptor = UIFontDescriptor(fontAttributes: [
            .family: familyName,
            .traits: [UIFontDescriptor.TraitKey.weight: weight]
        ])
        return UIFont(descriptor: descriptor, size: size)
    }

    static func configureUIKitAppearance() {
        registerBundledFontIfNeeded()
        UINavigationBar.appearance().barStyle = .black
        UINavigationBar.appearance().tintColor = .white
        UINavigationBar.appearance().titleTextAttributes = [
            .font: uiFont(size: 17, weight: .semibold),
            .foregroundColor: UIColor.white
        ]
        UINavigationBar.appearance().largeTitleTextAttributes = [
            .font: uiFont(size: 34, weight: .bold),
            .foregroundColor: UIColor.white
        ]
        UITabBar.appearance().barStyle = .black
        UITabBar.appearance().tintColor = .white
    }
}

extension Font {
    static func product(
        _ style: Font.TextStyle,
        weight: Font.Weight = .regular) -> Font {
        .custom(
            ProductTypography.familyName,
            size: ProductTypography.pointSize(for: style),
            relativeTo: style)
            .weight(weight)
    }

    static func product(
        size: CGFloat,
        relativeTo style: Font.TextStyle = .body,
        weight: Font.Weight = .regular) -> Font {
        .custom(
            ProductTypography.familyName,
            size: size,
            relativeTo: style)
            .weight(weight)
    }

    static func combo(
        size: CGFloat,
        relativeTo style: Font.TextStyle = .body,
        weight: Font.Weight = .regular) -> Font {
        .custom(
            ProductTypography.familyName,
            size: size,
            relativeTo: style)
            .weight(weight)
    }
}

private struct ProductDesignSystemModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .font(.product(.body))
            .foregroundStyle(Color.white)
            .environment(\.colorScheme, .dark)
            .onAppear {
                ProductTypography.registerBundledFontIfNeeded()
            }
    }
}

extension View {
    func productDesignSystem() -> some View {
        modifier(ProductDesignSystemModifier())
    }
}

struct ProductBackdrop: View {
    var body: some View {
        ZStack {
            Color.black
            RadialGradient(
                colors: [Color.white.opacity(0.035), Color.clear],
                center: .topTrailing,
                startRadius: 10,
                endRadius: 420)
            RadialGradient(
                colors: [Color.white.opacity(0.018), Color.clear],
                center: .bottomLeading,
                startRadius: 20,
                endRadius: 360)
        }
    }
}

struct ProductPackHueBackdrop: View {
    let accent: Color
    /// 1 for coloured tiers; neutral tiers pass a reduced strength.
    var strength: Double = 1

    var body: some View {
        ZStack {
            Color.black
            RadialGradient(
                colors: [
                    accent.opacity(
                        GachaPackStorefrontBackdropRules.centerGlowOpacity * strength),
                    accent.opacity(
                        GachaPackStorefrontBackdropRules.midRingOpacity * strength),
                    Color.clear,
                ],
                center: UnitPoint(x: 0.5, y: 0.42),
                startRadius: 24,
                endRadius: 420)
            RadialGradient(
                colors: [
                    accent.opacity(
                        GachaPackStorefrontBackdropRules.floorGlowOpacity * strength),
                    Color.clear,
                ],
                center: UnitPoint(x: 0.5, y: 0.94),
                startRadius: 12,
                endRadius: 280)
            LinearGradient(
                colors: [
                    accent.opacity(
                        GachaPackStorefrontBackdropRules.topWashOpacity * strength),
                    Color.black.opacity(0.88),
                    Color.black,
                ],
                startPoint: .top,
                endPoint: .bottom)
        }
    }
}

/// Source-faithful, iOS-native port of OpenSourceUI's Dark Arc Bands.
///
/// Source: `dark-arc-bands-background.tsx` at commit
/// `d239c3463c984a099dd2cb67817a41fc0bcc876f` (MIT, Bidyut Kundu).
/// The full notice is kept in `Docs/OpenSourceUI-DarkArcBands-MIT.md`.
/// Geometry, alpha profile, blur, lift and dot texture follow the source.
/// The four colour stops come from the Pack tier's colourway (FDB-GAC-035
/// amended 2026-09-07: present from the carousel, one metallic colourway per
/// Pack, the rarest keeps the source palette). Receipt and rarity never
/// reach it.
struct ProductPackArcBandsBackdrop: View {
    let intensity: Double
    /// `GachaPackArcBackdropRules.Colourway.forTier(selectedPack)`.
    var colourway: GachaPackArcBackdropRules.Colourway = .source

    @Environment(\.accessibilityReduceTransparency)
    private var reduceTransparency

    private var clampedIntensity: Double {
        min(max(intensity, 0), 1)
    }

    private var baseOpacity: Double {
        reduceTransparency
            ? GachaPackArcBackdropRules.reducedTransparencyBaseOpacity
            : GachaPackArcBackdropRules.baseOpacity
    }

    var body: some View {
        GeometryReader { proxy in
            let size = proxy.size
            let primaryHeight = size.height
                * CGFloat(GachaPackArcBackdropRules.primaryHeightFraction)
            let softHeight = size.height
                * CGFloat(GachaPackArcBackdropRules.softHeightFraction)
            let liftHeight = size.height
                * CGFloat(GachaPackArcBackdropRules.liftHeightFraction)

            ZStack {
                LinearGradient(
                    colors: [
                        sourceColor(
                            GachaPackArcBackdropRules.baseTopRGB,
                            opacity: baseOpacity),
                        sourceColor(
                            GachaPackArcBackdropRules.baseBottomRGB,
                            opacity: baseOpacity),
                    ],
                    startPoint: .top,
                    endPoint: .bottom)

                ProductPackArcBand(
                    width: size.width
                        * CGFloat(GachaPackArcBackdropRules.primaryWidthFraction),
                    height: primaryHeight,
                    xRadiusFraction: CGFloat(
                        GachaPackArcBackdropRules.primaryXRadiusFraction),
                    yRadiusFraction: CGFloat(
                        GachaPackArcBackdropRules.primaryYRadiusFraction),
                    stops: sourceStops(
                        GachaPackArcBackdropRules.primaryStops(for: colourway)),
                    blurPoints: 0)
                    .position(
                        x: size.width * 0.5,
                        y: size.height * CGFloat(
                            1 + GachaPackArcBackdropRules
                                .primaryBottomOverflowFraction)
                            - primaryHeight * 0.5)

                ProductPackArcBand(
                    width: size.width
                        * CGFloat(GachaPackArcBackdropRules.softWidthFraction),
                    height: softHeight,
                    xRadiusFraction: CGFloat(
                        GachaPackArcBackdropRules.softXRadiusFraction),
                    yRadiusFraction: CGFloat(
                        GachaPackArcBackdropRules.softYRadiusFraction),
                    stops: sourceStops(
                        GachaPackArcBackdropRules.softStops(for: colourway)),
                    blurPoints: CGFloat(
                        GachaPackArcBackdropRules.softBlurPoints))
                    .position(
                        x: size.width * 0.5,
                        y: size.height * CGFloat(
                            1 + GachaPackArcBackdropRules
                                .softBottomOverflowFraction)
                            - softHeight * 0.5)

                ProductPackArcBand(
                    width: size.width
                        * CGFloat(GachaPackArcBackdropRules.liftWidthFraction),
                    height: liftHeight,
                    xRadiusFraction: CGFloat(
                        GachaPackArcBackdropRules.liftXRadiusFraction),
                    yRadiusFraction: CGFloat(
                        GachaPackArcBackdropRules.liftYRadiusFraction),
                    stops: [
                        Gradient.Stop(
                            color: Color.white.opacity(
                                GachaPackArcBackdropRules.liftPeakOpacity),
                            location: 0),
                        Gradient.Stop(
                            color: Color.clear,
                            location: CGFloat(
                                GachaPackArcBackdropRules.liftEndLocation)),
                    ],
                    blurPoints: CGFloat(
                        GachaPackArcBackdropRules.liftBlurPoints))
                    .position(
                        x: size.width * 0.5,
                        y: size.height * CGFloat(
                            1 + GachaPackArcBackdropRules
                                .liftBottomOverflowFraction)
                            - liftHeight * 0.5)

                ProductPackArcDotField(
                    spacing: CGFloat(
                        GachaPackArcBackdropRules.dotSpacingPoints),
                    diameter: CGFloat(
                        GachaPackArcBackdropRules.dotDiameterPoints))
                    .fill(Color.white.opacity(
                        GachaPackArcBackdropRules.dotColorOpacity))
                    .opacity(GachaPackArcBackdropRules.dotLayerOpacity)
            }
            .frame(width: size.width, height: size.height)
            .clipped()
        }
        .opacity(clampedIntensity)
        .allowsHitTesting(false)
        .accessibilityHidden(true)
    }

    private func sourceColor(
        _ rgb: (red: Double, green: Double, blue: Double),
        opacity: Double
    ) -> Color {
        Color(
            .sRGB,
            red: rgb.red,
            green: rgb.green,
            blue: rgb.blue,
            opacity: opacity)
    }

    private func sourceStops(
        _ stops: [GachaPackArcBackdropRules.SourceColorStop]
    ) -> [Gradient.Stop] {
        stops.map { stop in
            Gradient.Stop(
                color: Color(
                    .sRGB,
                    red: stop.red,
                    green: stop.green,
                    blue: stop.blue,
                    opacity: stop.opacity),
                location: CGFloat(stop.location))
        }
    }
}

private struct ProductPackArcBand: View {
    let width: CGFloat
    let height: CGFloat
    let xRadiusFraction: CGFloat
    let yRadiusFraction: CGFloat
    let stops: [Gradient.Stop]
    let blurPoints: CGFloat

    var body: some View {
        let yRadius = max(height * yRadiusFraction, 1)
        let xScale = width * xRadiusFraction / yRadius
        RadialGradient(
                gradient: Gradient(stops: stops),
                center: .bottom,
                startRadius: 0,
                endRadius: yRadius)
            .frame(width: width, height: height)
            .scaleEffect(x: xScale, y: 1, anchor: .bottom)
            .frame(width: width, height: height)
            .clipShape(Ellipse())
            .blur(radius: blurPoints)
    }
}

/// One static path draw reproduces the source's 1 px-radius / 4 px dot tile
/// without importing a raster asset or running a time-based noise shader.
private struct ProductPackArcDotField: Shape {
    let spacing: CGFloat
    let diameter: CGFloat

    func path(in rect: CGRect) -> Path {
        var path = Path()
        guard spacing > 0, diameter > 0 else { return path }
        var y = rect.minY + spacing * 0.5
        while y < rect.maxY {
            var x = rect.minX + spacing * 0.5
            while x < rect.maxX {
                path.addEllipse(in: CGRect(
                    x: x - diameter * 0.5,
                    y: y - diameter * 0.5,
                    width: diameter,
                    height: diameter))
                x += spacing
            }
            y += spacing
        }
        return path
    }
}

struct ProductPackTierCaption: View {
    let title: String
    var price = ""
    let detail: String
    var accent = Color.white
    /// rev-006 review: the tier copy under the carousel is left-aligned.
    var alignment: HorizontalAlignment = .leading
    var itemSpacing = FidgetUITokens.Spacing.compact
    var includesHorizontalPadding = true
    /// Third, quieter line under `detail` (payment / shortfall).
    var footnote = ""

    private var frameAlignment: Alignment {
        alignment == .leading ? .leading : .center
    }

    private var textAlignment: TextAlignment {
        alignment == .leading ? .leading : .center
    }

    var body: some View {
        VStack(alignment: alignment, spacing: itemSpacing) {
            if !price.isEmpty {
                Text(price)
                    .font(.product(.footnote, weight: .semibold))
                    .foregroundStyle(accent.opacity(0.92))
            }
            Text(title)
                .font(.product(.title2, weight: .bold))
                .foregroundStyle(accent.opacity(0.96))
            if !detail.isEmpty {
                Text(detail)
                    .font(.product(.subheadline))
                    .foregroundStyle(
                        Color.white.opacity(FidgetUITokens.Opacity.secondaryText))
                    .multilineTextAlignment(textAlignment)
                    .lineLimit(3)
            }
            if !footnote.isEmpty {
                Text(footnote)
                    .font(.product(.footnote))
                    .foregroundStyle(
                        Color.white.opacity(FidgetUITokens.Opacity.tertiaryText))
                    .multilineTextAlignment(textAlignment)
                    .lineLimit(2)
            }
        }
        .frame(maxWidth: .infinity, alignment: frameAlignment)
        .padding(.horizontal, includesHorizontalPadding
            ? FidgetUITokens.Spacing.section : 0)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityLabelText)
    }

    private var accessibilityLabelText: String {
        [title, price, detail, footnote].filter { !$0.isEmpty }.joined(separator: "，")
    }
}

struct ProductRasterAssetImage: View {
    let name: String

    var body: some View {
        Group {
            if let url = Bundle.main.url(
                forResource: name,
                withExtension: "png"),
               let image = UIImage(contentsOfFile: url.path) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
            } else {
                Color.white.opacity(0.06)
            }
        }
    }
}

struct ProductPackTearRevealLayer: View {
    let bodyAssetName: String
    let flapAssetName: String
    let tearProgress: Double
    let seamLightStrength: Double
    let releasePulseStrength: Double
    let liveCaseReady: Bool
    let retreatProgress: Double
    /// Idle loop before the tear starts (spec §1.4): vertical drift, a
    /// slow yaw about the vertical axis and a highlight sweeping the seal.
    var idleOffsetPoints: Double = 0
    var idleYawDegrees: Double = 0
    /// Device-tilt pitch about the horizontal axis (FDB-GAC-036).
    var idlePitchDegrees: Double = 0
    /// Tier-ladder wriggle (GachaPackTierLadder): sideways knock, roll and swell.
    var idleWriggleXPoints: Double = 0
    var idleWriggleRollDegrees: Double = 0
    var idleWriggleScale: Double = 1
    /// Holographic sheen pose; nil draws no sheen.
    var sheenPose: GachaPackHolographicSheenRules.SheenPose? = nil
    /// Foil mask (`GachaPackTier.foilAssetName`); defaults to the body.
    var sheenMaskAssetName: String? = nil
    /// R051y: stand-alone print raster parallaxed against the foil, and
    /// whether the view-following glare is drawn (off under Reduce Motion).
    var printAssetName: String? = nil
    var glareEnabled = false
    /// R051z: tier-tinted drop shadow behind the sealed Pack; nil draws none.
    var shadowTint: Color? = nil
    /// R052d: the torn mouth's interior takes the tier's foil shade; nil
    /// keeps the neutral dark cavity.
    var interiorTier: GachaPackTier? = nil
    /// 0…1 sweep position across the seal; nil hides the highlight.
    var idleSealSweepProgress: Double? = nil
    /// Mouth gape multiplier at commit (spec §2.8).
    var mouthGapeScale: Double = 1
    /// When set, the Pack artwork shares geometry with the carousel's
    /// selected Pack so the selection→tear change animates as one Pack
    /// moving and growing instead of a cut.
    var matchedGeometryID: String? = nil
    var matchedGeometryNamespace: Namespace.ID? = nil

    private var progress: CGFloat {
        CGFloat(min(max(tearProgress, 0), 1))
    }

    private var retreat: CGFloat {
        CGFloat(min(max(retreatProgress, 0), 1))
    }

    /// Seal hit area in stage coordinates: `sealHitAreaHeightPoints` tall,
    /// centred on the fin, full Pack width (spec §1.5).
    static func sealHitRect(in size: CGSize) -> CGRect {
        let frame = ProductPackTearLayout.frame(in: size, retreatProgress: 0)
        let finTop = frame.minY + frame.height
            * CGFloat(GachaPackOpeningRules.authoredPackTopYFraction)
        let seam = frame.minY + frame.height
            * CGFloat(GachaPackOpeningRules.authoredSeamYFraction)
        let height = CGFloat(GachaPackHandoffRules.sealHitAreaHeightPoints)
        return CGRect(
            x: frame.minX,
            y: (finTop + seam) * 0.5 - height * 0.5,
            width: frame.width,
            height: height)
    }

    var body: some View {
        GeometryReader { proxy in
            let packFrame = ProductPackTearLayout.frame(
                in: proxy.size,
                retreatProgress: retreat)

            ZStack {
                ProductTearablePackArtwork(
                    bodyAssetName: bodyAssetName,
                    flapAssetName: flapAssetName,
                    tearProgress: tearProgress,
                    seamLightStrength: seamLightStrength,
                    releasePulseStrength: releasePulseStrength,
                    caseReady: liveCaseReady,
                    sealSweepProgress: idleSealSweepProgress,
                    mouthGapeScale: mouthGapeScale,
                    interiorTier: interiorTier)
                .background {
                    if let sheenPose, let shadowTint, tearProgress <= 0.002 {
                        ProductPackTintedShadow(
                            maskAssetName: bodyAssetName,
                            pose: sheenPose,
                            accent: shadowTint)
                    }
                }
                .overlay {
                    // The print sits wholly below the flap rows, so it can
                    // ride above the tearable stack without covering the lid.
                    if let printAssetName {
                        ProductPackPrintLayer(
                            assetName: printAssetName,
                            pose: sheenPose ?? .rest)
                    }
                }
                .overlay {
                    if let sheenPose {
                        ProductPackHolographicSheen(
                            maskAssetName: sheenMaskAssetName ?? bodyAssetName,
                            pose: sheenPose)
                    }
                }
                .overlay {
                    if let sheenPose, let printAssetName, glareEnabled {
                        ProductPackGlare(maskAssetName: printAssetName, pose: sheenPose)
                    }
                }
                .modifier(ProductMatchedGeometry(
                    id: matchedGeometryID,
                    namespace: matchedGeometryNamespace))
                .scaleEffect(idleWriggleScale)
                .rotationEffect(.degrees(idleWriggleRollDegrees))
                .rotation3DEffect(
                    .degrees(idlePitchDegrees),
                    axis: (x: 1, y: 0, z: 0),
                    perspective: 0.6)
                .rotation3DEffect(
                    .degrees(idleYawDegrees),
                    axis: (x: 0, y: 1, z: 0),
                    perspective: 0.6)
                // Departure: drop, tilt back and fade as one rigid body. The
                // case behind stays fully opaque throughout (spec §3.14).
                .modifier(ProductPackDepartureEffect(retreat: Double(retreat)))
                .position(
                    x: packFrame.midX + CGFloat(idleWriggleXPoints),
                    y: packFrame.midY + CGFloat(idleOffsetPoints))

                ProductPackReleaseBurst(
                    strength: releasePulseStrength,
                    center: ProductPackTearLayout.seamCenter(in: proxy.size),
                    stageSize: proxy.size)
            }
            .frame(width: proxy.size.width, height: proxy.size.height)
        }
        .accessibilityHidden(true)
    }
}

/// R051y (after holo-card's layered depth): the stamped print as its own
/// raster, shifted by `GachaPackHolographicSheenRules.printParallax` so the
/// emblem, type and panel rim ride above the foil when the phone tilts.
struct ProductPackPrintLayer: View {
    let assetName: String
    let pose: GachaPackHolographicSheenRules.SheenPose

    var body: some View {
        GeometryReader { proxy in
            let shift = GachaPackHolographicSheenRules.printParallax(pose: pose)
            ProductRasterAssetImage(name: assetName)
                .frame(width: proxy.size.width, height: proxy.size.height)
                .offset(
                    x: proxy.size.width * CGFloat(shift.x),
                    y: proxy.size.height * CGFloat(shift.y))
        }
        .accessibilityHidden(true)
    }
}

/// View-following specular on the metal print (R051z, user 09-09 09:58: a
/// highlight needs a reflective surface to sit on). One broad soft gloss
/// with a faint chromatic fringe, masked to the print raster (rim, panel
/// frame, emblem, type) so the matte foil never shows a hot spot.
struct ProductPackGlare: View {
    /// Metal mask: `GachaPackTier.printAssetName`.
    let maskAssetName: String
    let pose: GachaPackHolographicSheenRules.SheenPose

    private typealias Rules = GachaPackHolographicSheenRules

    var body: some View {
        GeometryReader { proxy in
            let width = proxy.size.width
            let centre = Rules.glareCenter(pose: pose)
            let point = CGPoint(x: width * CGFloat(centre.x), y: proxy.size.height * CGFloat(centre.y))
            let radius = width * CGFloat(Rules.glareCoreRadiusFraction)
            ZStack {
                Circle()
                    .strokeBorder(
                        AngularGradient(
                            stops: ProductPackHolographicSheen.spectrumStops(offset: pose.offset),
                            center: .center),
                        lineWidth: radius * 0.6)
                    .frame(width: radius * 2.6, height: radius * 2.6)
                    .blur(radius: radius * 0.5)
                    .opacity(Rules.glareFringeOpacity)
                    .position(point)
                Circle()
                    .fill(RadialGradient(
                        colors: [
                            Color.white.opacity(Rules.glareCoreOpacity),
                            Color.white.opacity(Rules.glareCoreOpacity * 0.45),
                            Color.white.opacity(0),
                        ],
                        center: .center,
                        startRadius: 0,
                        endRadius: radius))
                    .frame(width: radius * 2, height: radius * 2)
                    .position(point)
            }
            .opacity(Rules.glareBoost(pose: pose))
            .blendMode(.plusLighter)
            .mask(
                ProductRasterAssetImage(name: maskAssetName)
                    .frame(width: proxy.size.width, height: proxy.size.height))
        }
        .accessibilityHidden(true)
    }
}

/// Tinted drop shadow behind the Pack (R051z, user 09-09 09:58 "drop shadow
/// 深一些、按 tier 颜色、subtle、再扩散"): the pouch silhouette filled with the
/// darkened tier accent, blurred wide and dropped a little. Deepens on a
/// sweep. Normal blend: this is shade, not glow.
struct ProductPackTintedShadow: View {
    let maskAssetName: String
    let pose: GachaPackHolographicSheenRules.SheenPose
    let accent: Color

    private typealias Rules = GachaPackHolographicSheenRules

    var body: some View {
        GeometryReader { proxy in
            Rectangle()
                .fill(accent)
                .mask(
                    ProductRasterAssetImage(name: maskAssetName)
                        .frame(width: proxy.size.width, height: proxy.size.height))
                .blur(radius: CGFloat(Rules.shadowBlurPoints))
                .opacity(Rules.shadowOpacity(pose: pose))
                .scaleEffect(CGFloat(Rules.shadowScale))
                .offset(y: CGFloat(Rules.shadowDropPoints))
        }
        .accessibilityHidden(true)
    }
}

extension GachaPackTier {
    /// Shadow tint: the storefront accent scaled to `shadowTintScale`.
    var shadowTint: Color {
        let rgb = storefrontAccentRGB
        let k = GachaPackHolographicSheenRules.shadowTintScale
        return Color(red: rgb.red * k, green: rgb.green * k, blue: rgb.blue * k)
    }
}

/// Holographic foil sheen on the sealed Pack (FDB-GAC-036; reference:
/// LerSentAI parallax laser card). A wide, soft iridescent band — cyan,
/// white, magenta, gold — plus a narrow laser core, composited additively so
/// it brightens the print instead of painting over it. `maskAssetName` is
/// the tier's foil mask (`GachaPackTier.foilAssetName`): only the centre
/// emblem and the text carry the foil, not the whole bag (user review
/// 2026-09-07 17:22). `pose` comes from `GachaPackHolographicSheenRules`.
struct ProductPackHolographicSheen: View {
    let maskAssetName: String
    let pose: GachaPackHolographicSheenRules.SheenPose

    private typealias Rules = GachaPackHolographicSheenRules

    /// Band envelope: clear → white → clear across the band frame.
    private static let bandEnvelope = LinearGradient(
        stops: [
            .init(color: Color.clear, location: 0),
            .init(color: Color.white.opacity(0.35), location: 0.22),
            .init(color: Color.white, location: 0.5),
            .init(color: Color.white.opacity(0.35), location: 0.78),
            .init(color: Color.clear, location: 1),
        ],
        startPoint: .leading,
        endPoint: .trailing)

    /// Diffraction stripes (R051x): cosine-palette rainbow, phase slides with
    /// the band offset so tilting re-colours the foil like a real hologram.
    static func spectrumStops(offset: Double) -> [Gradient.Stop] {
        let count = 48
        let phase = offset * Rules.spectrumPhaseGain
        return (0..<count).map { i in
            let t = Double(i) / Double(count - 1)
            let c = Rules.spectrum(t * Rules.spectrumCycles + phase)
            return .init(
                color: Color(red: c.red, green: c.green, blue: c.blue),
                location: t)
        }
    }

    var body: some View {
        GeometryReader { proxy in
            let width = proxy.size.width
            let height = proxy.size.height
            let bandWidth = width * CGFloat(Rules.bandWidthFraction)
            let bandCenterX = width * 0.5 + CGFloat(pose.offset) * width
            let angle = Rules.bandAngleDegrees * Double.pi / 180
            ZStack {
                ZStack {
                    Rectangle()
                        .fill(LinearGradient(
                            stops: Self.spectrumStops(offset: pose.offset),
                            startPoint: .leading,
                            endPoint: .trailing))
                        .opacity(Rules.spectrumOpacity)
                        .mask(Rectangle().fill(Self.bandEnvelope))
                        .frame(width: bandWidth * 2.0, height: height * 2.6)
                    // Laser core: the bright line that reads as the beam.
                    Rectangle()
                        .fill(LinearGradient(
                            colors: [
                                Color.white.opacity(0),
                                Color.white.opacity(0.85),
                                Color.white.opacity(0),
                            ],
                            startPoint: .leading,
                            endPoint: .trailing))
                        .frame(width: bandWidth * 0.18, height: height * 2.6)
                }
                .rotationEffect(.degrees(Rules.bandAngleDegrees))
                .position(x: bandCenterX, y: height * 0.5)

                // Glints stay fixed on the foil and flash as the band passes.
                Canvas { context, size in
                    let glintSize = CGFloat(Rules.glintSizePoints)
                    for i in 0..<Rules.glintCount {
                        let p = Rules.glintPosition(i)
                        let x = size.width * CGFloat(p.x)
                        let y = size.height * CGFloat(p.y)
                        // Signed distance to the band centre line along its normal.
                        let d = ((x - bandCenterX) * CGFloat(cos(angle))
                            + (y - size.height * 0.5) * CGFloat(sin(angle)))
                            / bandWidth
                        let strength = Rules.glintEnvelope(distanceFromBandCentre: Double(d))
                        if strength < 0.02 { continue }
                        let r = glintSize * CGFloat(0.6 + 0.4 * strength)
                        var star = Path()
                        star.move(to: CGPoint(x: x - r * 2.2, y: y))
                        star.addQuadCurve(to: CGPoint(x: x, y: y - r * 2.2), control: CGPoint(x: x, y: y))
                        star.addQuadCurve(to: CGPoint(x: x + r * 2.2, y: y), control: CGPoint(x: x, y: y))
                        star.addQuadCurve(to: CGPoint(x: x, y: y + r * 2.2), control: CGPoint(x: x, y: y))
                        star.addQuadCurve(to: CGPoint(x: x - r * 2.2, y: y), control: CGPoint(x: x, y: y))
                        context.fill(
                            star,
                            with: .color(Color.white.opacity(Rules.glintOpacity * strength)))
                    }
                }
            }
            .opacity(pose.opacity)
        }
        .mask(ProductRasterAssetImage(name: maskAssetName))
        .blendMode(.plusLighter)
        .allowsHitTesting(false)
        .accessibilityHidden(true)
    }
}

/// The selected tier's floor glow grows from a small seed into a broad
/// ellipse. Recreating this component with `.id(tier)` replays the growth on
/// every carousel snap. It replaces the R049 full-screen circular wipe,
/// which completed too quickly to read as a bottom-origin ripple.
struct ProductPackBottomGlowGrowth: View {
    let accent: Color
    let strength: Double
    var reduceMotion = false

    @State private var progress = 0.0

    var body: some View {
        GeometryReader { proxy in
            let size = proxy.size
            let xScale = CGFloat(
                GachaPackBackdropRippleRules.xScale(progress: progress))
            let yScale = CGFloat(
                GachaPackBackdropRippleRules.yScale(progress: progress))
            let echo = CGFloat(
                GachaPackBackdropRippleRules.echoProgress(progress: progress))
            let width = size.width
                * CGFloat(GachaPackBackdropRippleRules.widthFraction)
            let height = size.height
                * CGFloat(GachaPackBackdropRippleRules.heightFraction)
            let floorY = size.height
                * CGFloat(GachaPackBackdropRippleRules.originYFraction)
            // `.position` places the frame centre; put the frame's bottom
            // edge on the floor line so the gradient centre stays on screen.
            let glowCenter = CGPoint(x: size.width * 0.5, y: floorY - height * 0.5)
            let echoHeight = height * 0.48
            let echoCenter = CGPoint(x: size.width * 0.5, y: floorY - echoHeight * 0.5)

            ZStack {
                RadialGradient(
                    colors: [
                        accent.opacity(0.96),
                        accent.opacity(0.66),
                        accent.opacity(0.24),
                        Color.clear,
                    ],
                    center: .bottom,
                    startRadius: 0,
                    endRadius: max(width, height) * 0.55)
                    .frame(width: width, height: height)
                    .scaleEffect(
                        x: xScale,
                        y: yScale,
                        anchor: .bottom)
                    .opacity(
                        GachaPackBackdropRippleRules.opacity(progress: progress)
                            * strength)
                    .blur(radius: 14)
                    .position(glowCenter)

                Ellipse()
                    .stroke(
                        accent.opacity(
                            GachaPackBackdropRippleRules.echoOpacity(
                                progress: progress) * strength),
                        lineWidth: CGFloat(
                            GachaPackBackdropRippleRules.echoLineWidthPoints))
                    .frame(width: width, height: echoHeight)
                    .scaleEffect(
                        x: max(echo, 0.02),
                        y: max(echo, 0.02),
                        anchor: .bottom)
                    .blur(radius: CGFloat(
                        GachaPackBackdropRippleRules.echoBlurPoints))
                    .position(echoCenter)
                    .blendMode(.plusLighter)
            }
        }
        .allowsHitTesting(false)
        .accessibilityHidden(true)
        .onAppear {
            if reduceMotion {
                progress = 1
            } else {
                progress = 0
                // Linear clock: the rules' growth curve is the only easing.
                withAnimation(.linear(
                    duration: GachaPackBackdropRippleRules.seconds)) {
                    progress = 1
                }
            }
        }
    }
}

/// Fine dust in the tier colour (R050) drawn as soft glows and star
/// sparkles (R051, user 2026-09-08 12:16: no hard-edged discs, no halo
/// disc behind a core disc). Rise speed follows the tier; a tier change
/// carries the accumulated travel forward so the field never jumps.
struct ProductPackBackdropAmbience: View {
    let tier: GachaPackTier
    let accent: Color
    let reference: Date
    var reduceMotion = false

    @State private var travelAtChange = 0.0
    @State private var changedAt: Date? = nil
    @State private var previousTier: GachaPackTier? = nil

    var body: some View {
        TimelineView(.animation(paused: reduceMotion)) { context in
            Canvas { graphics, size in
                let elapsed = reduceMotion ? 0 : context.date.timeIntervalSince(reference)
                let travel = reduceMotion ? 0 : GachaPackBackdropAmbienceRules.travel(
                    travelAtChange: travelAtChange,
                    secondsSinceChange: context.date.timeIntervalSince(changedAt ?? reference),
                    tier: tier)
                for index in 0..<GachaPackBackdropAmbienceRules.moteCount(for: tier) {
                    let mote = GachaPackBackdropAmbienceRules.mote(
                        index: index, elapsed: elapsed, travel: travel, tier: tier)
                    let center = CGPoint(
                        x: CGFloat(mote.x) * size.width,
                        y: CGFloat(mote.y) * size.height)
                    let glowRadius = CGFloat(mote.radiusPoints) * 2.2
                    let core = mote.sparkle
                        ? Color.white.opacity(min(mote.alpha, 0.9))
                        : accent.opacity(mote.alpha)
                    // Soft glow: lit core fading to nothing, no edge anywhere.
                    graphics.fill(
                        Path(ellipseIn: CGRect(
                            x: center.x - glowRadius,
                            y: center.y - glowRadius,
                            width: glowRadius * 2,
                            height: glowRadius * 2)),
                        with: .radialGradient(
                            Gradient(stops: [
                                .init(color: core, location: 0),
                                .init(color: core, location: GachaPackBackdropAmbienceRules.glowCoreFraction),
                                .init(color: accent.opacity(mote.alpha * 0.35), location: 0.6),
                                .init(color: accent.opacity(0), location: 1),
                            ]),
                            center: center,
                            startRadius: 0,
                            endRadius: glowRadius))
                    if mote.sparkle {
                        graphics.fill(
                            Self.starPath(
                                center: center,
                                spike: CGFloat(mote.spikePoints),
                                waist: CGFloat(GachaPackBackdropAmbienceRules.sparkleSpikeWaistPoints)),
                            with: .radialGradient(
                                Gradient(colors: [
                                    Color.white.opacity(min(mote.alpha * 0.9, 0.85)),
                                    accent.opacity(mote.alpha * 0.5),
                                    accent.opacity(0),
                                ]),
                                center: center,
                                startRadius: 0,
                                endRadius: CGFloat(mote.spikePoints)))
                    }
                }
            }
            .blendMode(.plusLighter)
        }
        .onAppear { previousTier = tier }
        .onChange(of: tier) { next in
            // Freeze the travel reached at the old speed, then continue at
            // the new tier's speed from here.
            let now = Date()
            travelAtChange = GachaPackBackdropAmbienceRules.travel(
                travelAtChange: travelAtChange,
                secondsSinceChange: now.timeIntervalSince(changedAt ?? reference),
                tier: previousTier ?? next)
            changedAt = now
            previousTier = next
        }
        .allowsHitTesting(false)
        .accessibilityHidden(true)
    }

    /// Four-point star: long thin spikes meeting at a narrow waist.
    static func starPath(center: CGPoint, spike: CGFloat, waist: CGFloat) -> Path {
        var path = Path()
        let points: [CGPoint] = [
            CGPoint(x: 0, y: -spike), CGPoint(x: waist, y: -waist),
            CGPoint(x: spike, y: 0), CGPoint(x: waist, y: waist),
            CGPoint(x: 0, y: spike), CGPoint(x: -waist, y: waist),
            CGPoint(x: -spike, y: 0), CGPoint(x: -waist, y: -waist),
        ]
        path.move(to: CGPoint(x: center.x + points[0].x, y: center.y + points[0].y))
        for point in points.dropFirst() {
            path.addLine(to: CGPoint(x: center.x + point.x, y: center.y + point.y))
        }
        path.closeSubpath()
        return path
    }
}

/// Resting Pack idle: slow float and a yaw about the vertical axis, driven
/// by a shared clock so the carousel and the tear stage stay in phase.
/// `settledAt` ramps the amplitude in after a swipe settles; `nil` means
/// full amplitude immediately. With `motion` and `sheenMaskAssetName` the
/// Pack also tilts with the device and carries the holographic sheen.
///
/// The sheen overlay is always in the hierarchy when a mask is given: adding
/// and removing it on selection made SwiftUI fade a second copy in and out
/// during the snap (2026-09-08 12:16 "拖影"). `carouselPosition` couples the
/// band to the Pack's slide so the foil reads as attached to the print.
struct ProductPackIdleFloat: ViewModifier, Animatable {
    let active: Bool
    let reference: Date
    let settledAt: Date?
    var motion: GachaPackMotionFeed? = nil
    var sheenMaskAssetName: String? = nil
    var reduceMotion = false
    /// Tier ladder (GachaPackTierLadder): richer Packs wriggle in bursts and
    /// land heavier when the carousel steps up to them.
    var tier: GachaPackTier = .standard
    var steppedUp = false
    /// Continuous carousel slot (0 = centred) for sheen parallax. Animatable
    /// so the band follows the same snap spring as the Pack's offset instead
    /// of jumping when the selection index changes.
    var carouselPosition: Double = 0
    /// While the finger drags the carousel the body is already re-evaluated
    /// per touch sample; a live timeline on top doubled the render load.
    var suspended = false
    /// R051y/z: stand-alone print raster, parallaxed against the foil and
    /// also the metal mask for the specular; pouch raster for the shadow.
    var printAssetName: String? = nil
    var shadowMaskAssetName: String? = nil

    var animatableData: Double {
        get { carouselPosition }
        set { carouselPosition = newValue }
    }

    private var paused: Bool {
        suspended || (!active && (motion == nil || motion?.mode == .off))
    }

    func body(content: Content) -> some View {
        TimelineView(.animation(paused: paused)) { context in
            let elapsed = context.date.timeIntervalSince(reference)
            let amplitude = active
                ? (settledAt.map {
                    GachaPackIdleMotion.rampIn(
                        sinceSettle: context.date.timeIntervalSince($0))
                } ?? 1)
                : 0
            let sample = motion?.sample(at: context.date) ?? .still
            let pose = GachaPackHolographicSheenRules.pose(
                elapsed: elapsed,
                idleAmplitude: amplitude,
                gravityX: sample.gravityX,
                gravityY: sample.gravityY,
                sweepProgress: sample.sweepProgress,
                reduceMotion: reduceMotion,
                carouselPosition: carouselPosition)
            // Eagerness ladder: bursts of knocking that grow with tier, plus
            // a rise-and-settle when the carousel stepped up to this Pack.
            let eager = active && !reduceMotion ? amplitude : 0
            let wriggleX = GachaPackTierLadder.wriggleOffsetPoints(
                elapsed: elapsed, tier: tier) * eager
            let wriggleRoll = GachaPackTierLadder.wriggleDegrees(
                elapsed: elapsed, tier: tier) * eager
            let swell = 1 + (GachaPackTierLadder.wriggleScale(
                elapsed: elapsed, tier: tier) - 1) * eager
            let arrival = (active && !reduceMotion)
                ? (settledAt.map {
                    GachaPackTierLadder.arrivalOffsetPoints(
                        sinceSettle: context.date.timeIntervalSince($0),
                        steppedUp: steppedUp,
                        tier: tier)
                } ?? 0)
                : 0
            content
                .background {
                    // R051z tinted shadow behind the selected Pack only: the
                    // silhouette blur is the one costly layer in the carousel.
                    if let shadowMaskAssetName, active {
                        ProductPackTintedShadow(
                            maskAssetName: shadowMaskAssetName,
                            pose: pose,
                            accent: tier.shadowTint)
                    }
                }
                .overlay {
                    // R051y: the print floats above the foil and shifts with
                    // the tilt (holo-card foreground depth), then the sheen,
                    // then the view-following glare over the whole pouch.
                    if let printAssetName {
                        ProductPackPrintLayer(assetName: printAssetName, pose: pose)
                    }
                }
                .overlay {
                    if let sheenMaskAssetName {
                        ProductPackHolographicSheen(
                            maskAssetName: sheenMaskAssetName,
                            pose: pose)
                    }
                }
                .overlay {
                    // Selected Pack only: a fixed flare on every side Pack read
                    // as a crosshair (R051y review).
                    if let printAssetName, active, !reduceMotion {
                        ProductPackGlare(maskAssetName: printAssetName, pose: pose)
                    }
                }
                .scaleEffect(swell)
                .rotationEffect(.degrees(wriggleRoll))
                .rotation3DEffect(
                    .degrees(pose.tiltPitchDegrees),
                    axis: (x: 1, y: 0, z: 0),
                    perspective: 0.6)
                .rotation3DEffect(
                    .degrees(GachaPackIdleMotion.yawDegrees(
                        elapsed: elapsed,
                        amplitude: amplitude) + pose.tiltYawDegrees),
                    axis: (x: 0, y: 1, z: 0),
                    perspective: 0.6)
                .offset(
                    x: CGFloat(wriggleX),
                    y: CGFloat(GachaPackIdleMotion.offsetPoints(
                        elapsed: elapsed,
                        amplitude: amplitude) + arrival))
        }
    }
}

/// Pack departure as one rigid body: tilt back about the bottom edge and
/// fade. `retreat` is the animatable value, so the opacity shaping
/// (`packDepartureOpacity`: solid for the first 35%, then fade) is evaluated
/// per frame along the drop's timing curve instead of SwiftUI interpolating
/// the final opacity linearly.
struct ProductPackDepartureEffect: ViewModifier, Animatable {
    var retreat: Double

    var animatableData: Double {
        get { retreat }
        set { retreat = newValue }
    }

    func body(content: Content) -> some View {
        let clamped = min(max(retreat, 0), 1)
        content
            .rotation3DEffect(
                .degrees(GachaPackHandoffRules.packDepartureTiltDegrees * clamped),
                axis: (x: 1, y: 0, z: 0),
                anchor: .bottom,
                perspective: 0.6)
            .opacity(GachaPackHandoffRules.packDepartureOpacity(
                retreatProgress: clamped))
    }
}

/// Applies `matchedGeometryEffect` when an id and namespace exist.
///
/// The modifier keeps one view branch. A `nil` id falls back to
/// `fallbackID`, which no other view shares, so the effect is inert. Swapping
/// between an `if`/`else` branch changed the view identity whenever the
/// carousel selection moved; SwiftUI then crossfaded two copies of the Pack
/// during the snap — the "拖影" the user saw (2026-09-08 12:16).
struct ProductMatchedGeometry: ViewModifier {
    let id: String?
    let namespace: Namespace.ID?
    var fallbackID: String = "product-matched-geometry-inert"

    @ViewBuilder
    func body(content: Content) -> some View {
        if let namespace {
            content.matchedGeometryEffect(
                id: id ?? fallbackID,
                in: namespace,
                properties: .frame,
                anchor: .center,
                isSource: id != nil)
        } else {
            content
        }
    }
}

/// A transparent foreground Pack for a live Unity stage.
///
/// The Pack artwork remains opaque, while the shaped mouth is cut out of this
/// hosting view. The Unity view below owns any background or live case pixels.
struct ProductLiveUnityPackRevealLayer: View {
    let bodyAssetName: String
    let flapAssetName: String
    let tearProgress: Double
    let seamLightStrength: Double
    let liveCaseReady: Bool
    let retreatProgress: Double
    var releasePulseStrength: Double = 0

    private var retreat: CGFloat {
        CGFloat(min(max(retreatProgress, 0), 1))
    }

    var body: some View {
        GeometryReader { proxy in
            let packFrame = ProductPackTearLayout.frame(
                in: proxy.size,
                retreatProgress: retreat)

            ZStack {
                ProductTearablePackArtwork(
                    bodyAssetName: bodyAssetName,
                    flapAssetName: flapAssetName,
                    tearProgress: tearProgress,
                    seamLightStrength: seamLightStrength,
                    releasePulseStrength: releasePulseStrength,
                    caseReady: liveCaseReady)
                .modifier(ProductPackDepartureEffect(retreat: Double(retreat)))
                .position(x: packFrame.midX, y: packFrame.midY)

                // Full-stage flash and streaks. They sit above the live Unity
                // view for well under a second, the same way the Sweeps cut
                // washes the whole screen.
                ProductPackReleaseBurst(
                    strength: releasePulseStrength,
                    center: ProductPackTearLayout.seamCenter(in: proxy.size),
                    stageSize: proxy.size)
            }
            .frame(width: proxy.size.width, height: proxy.size.height)
        }
        .accessibilityHidden(true)
    }
}

struct ProductTearablePackArtwork: View {
    let bodyAssetName: String
    let flapAssetName: String
    let tearProgress: Double
    let seamLightStrength: Double
    let releasePulseStrength: Double
    let caseReady: Bool
    let sealSweepProgress: Double?
    let mouthGapeScale: Double
    let interiorTier: GachaPackTier?

    init(
        bodyAssetName: String,
        flapAssetName: String,
        tearProgress: Double,
        seamLightStrength: Double,
        releasePulseStrength: Double,
        caseReady: Bool = false,
        exposesLiveUnityBackground: Bool = false,
        sealSweepProgress: Double? = nil,
        mouthGapeScale: Double = 1,
        interiorTier: GachaPackTier? = nil
    ) {
        self.bodyAssetName = bodyAssetName
        self.flapAssetName = flapAssetName
        self.tearProgress = tearProgress
        self.seamLightStrength = seamLightStrength
        self.releasePulseStrength = releasePulseStrength
        self.caseReady = caseReady
        self.sealSweepProgress = sealSweepProgress
        self.mouthGapeScale = mouthGapeScale
        self.interiorTier = interiorTier
        // This compatibility input cannot authorize transparency. Only the
        // same-request receipt-and-readiness gate may open the aperture.
        _ = exposesLiveUnityBackground
    }

    private var progress: CGFloat {
        CGFloat(min(max(tearProgress, 0), 1))
    }

    private var tearFront: CGFloat {
        CGFloat(GachaPackOpeningRules.tearFrontProgress(
            progress: tearProgress))
    }

    /// Layer order, bottom to top:
    /// 1. body raster, never cut;
    /// 2. mouth sliver sitting on the body's top edge in freed columns;
    /// 3. the still-attached part of the seal fin;
    /// 4. the freed fin (lid) hinged at the tear front, later flying off;
    /// 5. release pulse.
    /// At progress 0 the fin is whole, so 1 + 3 is the authored sealed Pack.
    var body: some View {
        ZStack {
            ProductRasterAssetImage(name: bodyAssetName)
                .frame(
                    width: ProductPackTearLayout.artworkWidth,
                    height: ProductPackTearLayout.artworkHeight)

            // No lip line or outline: on the dark stage any stroke above the
            // body edge reads as a plate floating on the seal. Depth comes
            // from the sliver gradient once the case is behind it.
            ProductPackSlitCavity(
                progress: progress,
                seamLightStrength: seamLightStrength,
                tier: interiorTier)
                .scaleEffect(
                    x: 1,
                    y: CGFloat(mouthGapeScale),
                    anchor: UnitPoint(
                        x: 0.5,
                        y: GachaPackOpeningRules.authoredSeamYFraction))
                .opacity(tearFront > 0 ? 1 : 0)

            ProductRasterAssetImage(name: flapAssetName)
                .frame(
                    width: ProductPackTearLayout.artworkWidth,
                    height: ProductPackTearLayout.artworkHeight)
                .mask(ProductPackSlitBodyMask(progress: progress))

            // Idle hint: an 8 pt highlight sweeping along the seal (spec §1.4).
            if let sweep = sealSweepProgress, progress <= 0.002 {
                ProductPackSealSweep(progress: CGFloat(sweep))
            }

            // Tear front: 2 pt matte white edge that travels with the front
            // while the seal is being torn (spec §2.6).
            if tearFront > 0.0001, tearFront < 0.9999 {
                ProductPackTearFrontEdge(progress: progress)
            }

            ProductPackLid(
                assetName: flapAssetName,
                progress: progress,
                width: ProductPackTearLayout.artworkWidth,
                height: ProductPackTearLayout.artworkHeight)
        }
        .frame(
            width: ProductPackTearLayout.artworkWidth,
            height: ProductPackTearLayout.artworkHeight)
        .accessibilityHidden(true)
    }
}

/// Highlight band sweeping across the seal fin while the Pack waits.
private struct ProductPackSealSweep: View {
    let progress: CGFloat

    var body: some View {
        let width = ProductPackTearLayout.artworkWidth
        let height = ProductPackTearLayout.artworkHeight
        let finTop = height * CGFloat(GachaPackOpeningRules.authoredPackTopYFraction)
        let seam = height * CGFloat(GachaPackOpeningRules.authoredSeamYFraction)
        let span = GachaPackOpeningRules.authoredFlapSpanFraction
        let left = width * CGFloat(span.lowerBound)
        let right = width * CGFloat(span.upperBound)
        let band = CGFloat(GachaPackHandoffRules.idleSealSweepWidthPoints)
        let x = left + (right - left) * min(max(progress, 0), 1)
        Rectangle()
            .fill(
                LinearGradient(
                    colors: [
                        Color.white.opacity(0),
                        Color.white.opacity(0.55),
                        Color.white.opacity(0)
                    ],
                    startPoint: .leading,
                    endPoint: .trailing))
            .frame(width: band, height: seam - finTop)
            .position(x: x, y: (finTop + seam) * 0.5)
            .blendMode(.screen)
            .allowsHitTesting(false)
    }
}

/// Matte white edge at the tear front, from fin top to seam.
private struct ProductPackTearFrontEdge: View {
    let progress: CGFloat

    var body: some View {
        let width = ProductPackTearLayout.artworkWidth
        let height = ProductPackTearLayout.artworkHeight
        let finTop = height * CGFloat(GachaPackOpeningRules.authoredPackTopYFraction)
        let seam = height * CGFloat(GachaPackOpeningRules.authoredSeamYFraction)
        let inset = CGFloat(GachaPackOpeningRules.openingInsetFraction)
        let front = CGFloat(GachaPackOpeningRules.tearFrontProgress(
            progress: Double(progress)))
        let x = width * (inset + (1 - inset * 2) * front)
        Rectangle()
            .fill(Color(red: 0.93, green: 0.93, blue: 0.91).opacity(0.9))
            .frame(width: 2, height: seam - finTop)
            .position(x: x, y: (finTop + seam) * 0.5)
            .allowsHitTesting(false)
    }
}

/// Release beat drawn over the whole stage, not just the Pack artwork: a
/// full-frame flash that peaks at commit and a radial burst of streaks that
/// keeps travelling outward from the seam while the case comes up.
struct ProductPackReleaseBurst: View {
    let strength: Double
    let center: CGPoint
    let stageSize: CGSize

    var body: some View {
        let pulse = min(max(strength, 0), 1)
        let radius = max(stageSize.width, stageSize.height) * 0.5
        ZStack {
            Color.white
                .opacity(GachaPackOpeningRules.releaseFlashOpacity(
                    pulseStrength: pulse))
            ProductPackBurstStreaks(travel: CGFloat(1 - pulse))
                .stroke(
                    Color.white.opacity(0.95 * pulse),
                    style: StrokeStyle(lineWidth: 2.4, lineCap: .round))
                .frame(width: radius * 2, height: radius * 2)
                .position(center)
        }
        .frame(width: stageSize.width, height: stageSize.height)
        .opacity(pulse > 0.001 ? 1 : 0)
        .allowsHitTesting(false)
        .accessibilityHidden(true)
    }
}

/// Deterministic radial streaks. Each streak starts near the seam and moves
/// outward with `travel` (0 at the flash peak, 1 at the end of the pulse);
/// the ease-out makes them shoot then coast, like the Sweeps cut.
private struct ProductPackBurstStreaks: Shape {
    var travel: CGFloat

    var animatableData: CGFloat {
        get { travel }
        set { travel = newValue }
    }

    private func noise(_ index: Int, _ salt: Double) -> CGFloat {
        let value = sin(Double(index) * 12.9898 + salt * 78.233) * 43758.5453
        return CGFloat(value - floor(value))
    }

    func path(in rect: CGRect) -> Path {
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let radius = min(rect.width, rect.height) * 0.5
        let count = GachaPackOpeningRules.releaseBurstStreakCount
        let inner = CGFloat(GachaPackOpeningRules.releaseBurstInnerRadiusFraction)
        let reach = CGFloat(GachaPackOpeningRules.releaseBurstTravelFraction)
        let eased = 1 - (1 - travel) * (1 - travel)
        var result = Path()
        for index in 0..<count {
            let angle = (Double(index) + Double(noise(index, 1)) * 0.7)
                / Double(count) * 2 * Double.pi
            let direction = CGPoint(x: cos(angle), y: sin(angle))
            let start = radius * (inner + noise(index, 2) * 0.22)
                + radius * reach * eased * (0.7 + noise(index, 3) * 0.5)
            let length = radius * (0.035 + noise(index, 4) * 0.075)
                * (1 - 0.35 * eased)
            result.move(to: CGPoint(
                x: center.x + direction.x * start,
                y: center.y + direction.y * start))
            result.addLine(to: CGPoint(
                x: center.x + direction.x * (start + length),
                y: center.y + direction.y * (start + length)))
        }
        return result
    }
}

/// The sealed Pack as authored: body raster with the seal fin on top. Use
/// this wherever a closed Pack is shown so the carousel and the tear stage
/// start from the same pixels.
struct ProductPackSealedArtwork: View {
    let bodyAssetName: String
    let flapAssetName: String

    /// R051y: body/flap carry the bare foil; the print is its own raster.
    /// Callers that parallax the print (`ProductPackIdleFloat`) leave this
    /// nil and draw it themselves.
    var printAssetName: String? = nil

    var body: some View {
        ZStack {
            ProductRasterAssetImage(name: bodyAssetName)
            if let printAssetName {
                ProductRasterAssetImage(name: printAssetName)
            }
            ProductRasterAssetImage(name: flapAssetName)
        }
        .accessibilityHidden(true)
    }
}

private enum ProductPackTearLayout {
    static let artworkWidth = CGFloat(
        GachaPackOpeningRules.artworkWidthPoints)
    static let artworkHeight = CGFloat(
        GachaPackOpeningRules.artworkHeightPoints)

    /// Pack rests centred at (50%, 44%) of the stage. Departure drops it by
    /// `packDepartureDropFraction` of the stage height while it tilts, and
    /// it fades only near the bottom (rev-006 review).
    static func frame(
        in size: CGSize,
        retreatProgress: CGFloat
    ) -> CGRect {
        let centerY = size.height
            * CGFloat(GachaPackHandoffRules.stagePackCenterYFraction)
        return CGRect(
            x: (size.width - artworkWidth) * 0.5,
            y: centerY - artworkHeight * 0.5
                + size.height
                    * CGFloat(GachaPackHandoffRules.packDepartureDropFraction)
                    * retreatProgress,
            width: artworkWidth,
            height: artworkHeight)
    }

    /// Seam midpoint of the resting Pack; the release burst radiates from
    /// here and does not follow the retreat.
    static func seamCenter(in size: CGSize) -> CGPoint {
        let resting = frame(in: size, retreatProgress: 0)
        return CGPoint(
            x: resting.midX,
            y: resting.minY + artworkHeight
                * CGFloat(GachaPackOpeningRules.authoredSeamYFraction))
    }
}

/// Mask for the part of the seal fin that is still attached: the whole
/// canvas minus the freed columns, built as explicit non-overlapping
/// pieces so it does not depend on even-odd subtraction.
private struct ProductPackSlitBodyMask: View {
    let progress: CGFloat

    var body: some View {
        ProductPackSlitBodyShape(progress: progress)
            .fill(Color.white, style: FillStyle(eoFill: false))
    }
}

private struct ProductPackSlitBodyShape: Shape {
    var progress: CGFloat

    var animatableData: CGFloat {
        get { progress }
        set { progress = newValue }
    }

    func path(in rect: CGRect) -> Path {
        guard let freed = ProductPackTornAwayTopShape.freedColumns(
            progress: progress,
            in: rect) else {
            return Path(rect)
        }
        var result = Path()
        // Left of the freed span (the inset margin), full height.
        result.addRect(CGRect(
            x: rect.minX,
            y: rect.minY,
            width: max(0, freed.left - rect.minX),
            height: rect.height))
        // Right of the tear front, full height.
        result.addRect(CGRect(
            x: freed.right,
            y: rect.minY,
            width: max(0, rect.maxX - freed.right),
            height: rect.height))
        // Below the seam inside the freed span: the fin has no pixels here,
        // but keeping it makes the mask an exact complement.
        result.move(to: CGPoint(x: freed.left, y: rect.maxY))
        result.addLine(to: CGPoint(x: freed.right, y: rect.maxY))
        let samples = ProductPackTearPath.samples
        for sample in stride(from: samples, through: 0, by: -1) {
            let x = freed.left
                + (freed.right - freed.left) * CGFloat(sample) / CGFloat(samples)
            result.addLine(to: CGPoint(
                x: x,
                y: ProductPackTearPath.tornEdgeY(at: x, in: rect)))
        }
        result.closeSubpath()
        return result
    }
}

/// The part of the seal fin the tear front has freed: the columns from the
/// left inset to the front, from the canvas top down to the seam. The front
/// is a crisp vertical edge; because the lid hinges at that edge, the freed
/// and attached fin meet there with zero displacement. The same shape masks
/// the lid, so the piece that leaves is exactly the piece that was freed.
private struct ProductPackTornAwayTopShape: Shape {
    var progress: CGFloat

    var animatableData: CGFloat {
        get { progress }
        set { progress = newValue }
    }

    /// Horizontal span of the freed fin, or nil while nothing is freed.
    static func freedColumns(
        progress: CGFloat,
        in rect: CGRect
    ) -> (left: CGFloat, right: CGFloat)? {
        guard progress > 0.002 else { return nil }
        let tearFront = CGFloat(GachaPackOpeningRules.tearFrontProgress(
            progress: Double(progress)))
        guard tearFront > 0.0001 else { return nil }
        let inset = CGFloat(GachaPackOpeningRules.openingInsetFraction)
        let left = rect.minX + rect.width * inset
        let right = rect.minX
            + rect.width * (inset + (1 - inset * 2) * tearFront)
        guard right > left else { return nil }
        return (left, right)
    }

    func path(in rect: CGRect) -> Path {
        guard let freed = Self.freedColumns(progress: progress, in: rect)
        else {
            return Path()
        }
        var result = Path()
        result.move(to: CGPoint(x: freed.left, y: rect.minY))
        result.addLine(to: CGPoint(x: freed.right, y: rect.minY))
        let samples = ProductPackTearPath.samples
        for sample in stride(from: samples, through: 0, by: -1) {
            let x = freed.left
                + (freed.right - freed.left) * CGFloat(sample) / CGFloat(samples)
            result.addLine(to: CGPoint(
                x: x,
                y: ProductPackTearPath.tornEdgeY(at: x, in: rect)))
        }
        result.closeSubpath()
        return result
    }
}

/// One rigid lid: the freed seal fin. It must leave as a single body;
/// separately posed foil portions read as debris rather than a removed seal.
private struct ProductPackLid: View {
    let assetName: String
    let progress: CGFloat
    let width: CGFloat
    let height: CGFloat

    private var pose: GachaPackLidPose {
        GachaPackLidRules.pose(
            progress: Double(progress),
            artworkWidthPoints: Double(width),
            artworkHeightPoints: Double(height))
    }

    var body: some View {
        let pose = pose
        let shape = ProductPackTornAwayTopShape(progress: progress)
        let hinge = UnitPoint(
            x: pose.hingeXFraction,
            y: pose.hingeYFraction)
        ZStack {
            // Foil thickness: a darkened copy of the lid pixels shifted down,
            // so the underside has the lid silhouette and nothing more.
            ProductRasterAssetImage(name: assetName)
                .frame(width: width, height: height)
                .mask(shape)
                .colorMultiply(Color(red: 0.20, green: 0.21, blue: 0.21))
                .offset(y: CGFloat(pose.undersideDepthPoints))

            ProductRasterAssetImage(name: assetName)
                .frame(width: width, height: height)
                .mask(shape)
        }
        .frame(width: width, height: height)
        .shadow(
            color: Color.black.opacity(0.28 * pose.opacity),
            radius: 3,
            x: 0,
            y: 3)
        .rotationEffect(.degrees(pose.rotationDegrees), anchor: hinge)
        .offset(
            x: CGFloat(pose.offsetXPoints),
            y: CGFloat(pose.offsetYPoints))
        .opacity(pose.opacity)
        .allowsHitTesting(false)
    }
}

/// The interior sliver seen above the body's top edge once the fin is off.
/// Opaque local cavity (R033 contract): the stage must not show through the
/// pouch. It is attached to the body edge and has no outline, so it reads
/// as depth, not as an object; on the dark stage it simply disappears.
private struct ProductPackSlitCavity: View {
    let progress: CGFloat
    let seamLightStrength: Double
    var tier: GachaPackTier? = nil

    /// A touch lighter at the back lip while the tear gesture is live, so
    /// the freshly exposed gap under the lifting fin reads on the stage.
    /// R052d (user 09-09 15:23 "一块黑色的不明物体"): with a tier the cavity
    /// is the pouch's own foil seen from inside — the lit back lip at
    /// `interiorLipScale`, falling to `interiorDepthScale` — so it reads as
    /// the sachet's depth on a light stage instead of a black bar.
    private var cavityFill: LinearGradient {
        let light = min(max(seamLightStrength, 0), 1)
        guard let tier else {
            return LinearGradient(
                colors: [
                    Color(
                        red: 0.075 + 0.03 * light,
                        green: 0.08 + 0.03 * light,
                        blue: 0.085 + 0.03 * light),
                    Color(red: 0.04, green: 0.045, blue: 0.05),
                    Color(red: 0.055, green: 0.06, blue: 0.065)
                ],
                startPoint: .top,
                endPoint: .bottom)
        }
        typealias Rules = GachaPackOpeningRules
        let rgb = tier.storefrontAccentRGB
        func shade(_ k: Double) -> Color {
            Color(red: rgb.red * k, green: rgb.green * k, blue: rgb.blue * k)
        }
        return LinearGradient(
            stops: [
                .init(color: shade(Rules.interiorLipScale + 0.08 * light), location: 0),
                .init(color: shade(Rules.interiorMidScale), location: 0.22),
                .init(color: shade(Rules.interiorDepthScale), location: 0.72),
                .init(color: shade(Rules.interiorMidScale), location: 1),
            ],
            startPoint: .top,
            endPoint: .bottom)
    }

    private typealias Rules = GachaPackOpeningRules

    var body: some View {
        let mouth = ProductPackMouthMask(progress: progress)
        ZStack {
            mouth.fill(cavityFill)
            if tier != nil {
                // R052g: foil grain, one broad gloss, the front edge's shadow
                // above the seam, and a lit hairline on the back fold.
                ProductPackFoilGrain(opacity: Rules.interiorGrainOpacity)
                    .mask(mouth)
                mouth.fill(LinearGradient(
                    colors: [
                        .white.opacity(0),
                        .white.opacity(Rules.interiorGlossOpacity),
                        .white.opacity(Rules.interiorGlossOpacity * 0.35),
                        .white.opacity(0),
                    ],
                    startPoint: .leading,
                    endPoint: .trailing))
                mouth.fill(LinearGradient(
                    stops: [
                        .init(color: .black.opacity(0), location: 0.4),
                        .init(color: .black.opacity(Rules.interiorEdgeShadowOpacity), location: 1),
                    ],
                    startPoint: .top,
                    endPoint: .bottom))
                ProductPackMouthLipEdge(progress: progress)
                    .stroke(
                        Color.white.opacity(Rules.interiorLipHighlightOpacity),
                        style: StrokeStyle(
                            lineWidth: CGFloat(Rules.interiorLipHighlightWidthPoints),
                            lineCap: .round))
            }
        }
    }
}

/// Fine horizontal streaks, deterministic, for the foil seen through the
/// mouth. Drawn once per size; no motion.
private struct ProductPackFoilGrain: View {
    let opacity: Double

    var body: some View {
        Canvas { context, size in
            var seed: UInt32 = 0x9E37_79B9
            var y: CGFloat = 0
            while y < size.height {
                seed = seed &* 1_664_525 &+ 1_013_904_223
                let noise = Double(seed >> 8) / Double(1 << 24)
                let alpha = opacity * (0.25 + 0.75 * noise)
                let light = noise > 0.5
                var line = Path()
                line.move(to: CGPoint(x: 0, y: y))
                line.addLine(to: CGPoint(x: size.width, y: y))
                context.stroke(
                    line,
                    with: .color((light ? Color.white : Color.black).opacity(alpha)),
                    lineWidth: 0.7)
                y += 1
            }
        }
        .allowsHitTesting(false)
    }
}

/// The back panel's fold edge: the mouth's upper curve as an open path.
private struct ProductPackMouthLipEdge: Shape {
    var progress: CGFloat

    var animatableData: CGFloat {
        get { progress }
        set { progress = newValue }
    }

    func path(in rect: CGRect) -> Path {
        guard GachaPackOpeningRules.isMouthOpen(
            progress: Double(progress)) else {
            return Path()
        }
        var result = Path()
        let inset = rect.width * CGFloat(GachaPackOpeningRules.mouthInsetFraction)
        let left = rect.minX + inset
        let right = rect.maxX - inset
        guard right > left else { return result }
        for sample in 0...ProductPackTearPath.samples {
            let fraction = CGFloat(sample) / CGFloat(ProductPackTearPath.samples)
            let x = left + (right - left) * fraction
            let point = CGPoint(
                x: x,
                y: ProductPackTearPath.openingTopY(at: x, in: rect, progress: progress))
            if sample == 0 { result.move(to: point) } else { result.addLine(to: point) }
        }
        return result
    }
}

private enum ProductPackTearPath {
    static let samples = 48
    static let openingCenterSag: CGFloat = 0.8
    static let edgeOffsets: [CGFloat] = [
        0, -0.35, 0.18, -0.22, 0.42, -0.12, 0.25, -0.40, 0.10,
        -0.18, 0.30, -0.08, 0.16
    ]

    /// Overlap into the body so the sliver's bottom never shows an
    /// anti-aliased hairline gap above the authored top edge.
    static let bodyOverlapPoints: CGFloat = 0.6

    static func faceTopY(in rect: CGRect) -> CGFloat {
        rect.minY + rect.height * CGFloat(
            GachaPackOpeningRules.authoredPackFaceTopYFraction)
    }

    /// Seam between the seal fin and the body: the body's authored top edge.
    static func seamY(in rect: CGRect) -> CGFloat {
        rect.minY + rect.height * CGFloat(
            GachaPackOpeningRules.authoredSeamYFraction)
    }

    static func interiorFraction(at x: CGFloat, in rect: CGRect) -> CGFloat {
        let canvasFraction = (x - rect.minX) / max(rect.width, 1)
        let insetFraction = CGFloat(
            GachaPackOpeningRules.mouthInsetFraction)
        return min(
            max(
                (canvasFraction - insetFraction)
                    / (1 - insetFraction * 2),
                0),
            1)
    }

    static func openingFactor(
        at x: CGFloat,
        in rect: CGRect,
        progress: CGFloat
    ) -> CGFloat {
        guard rect.width > 0 else { return 0 }
        let canvasFraction = (x - rect.minX) / rect.width
        let insetFraction = CGFloat(
            GachaPackOpeningRules.mouthInsetFraction)
        guard canvasFraction >= insetFraction,
              canvasFraction <= 1 - insetFraction else {
            return 0
        }
        return CGFloat(GachaPackOpeningRules.openingFraction(
            horizontalFraction: Double(interiorFraction(at: x, in: rect)),
            progress: Double(progress)))
    }

    /// Back-panel lip: the upper edge of the interior sliver, above the
    /// body's top edge in the space the fin vacates. Tapered to zero at both
    /// ends so it stays inside the Pack shoulders.
    static func openingTopY(
        at x: CGFloat,
        in rect: CGRect,
        progress: CGFloat
    ) -> CGFloat {
        let factor = openingFactor(at: x, in: rect, progress: progress)
        let interior = interiorFraction(at: x, in: rect)
        let height = CGFloat(GachaPackOpeningRules.openingHeightPoints(
            horizontalFraction: Double(interior),
            progress: Double(progress)))
        let taper = CGFloat(GachaPackOpeningRules.openingEndTaper(
            horizontalFraction: Double(interior)))
        let sag = sin(interior * .pi) * openingCenterSag * factor * taper
        return seamY(in: rect)
            - CGFloat(GachaPackOpeningRules.openingSealLiftPoints)
                * factor * taper
            - height - sag
    }

    /// Lower edge of the freed fin: the seam with a little torn-foil texture.
    /// The body below keeps its authored straight edge.
    static func tornEdgeY(at x: CGFloat, in rect: CGRect) -> CGFloat {
        let column = Int(((x - rect.minX) / max(rect.width, 1))
            * CGFloat(samples))
        let texture = edgeOffsets[abs(column) % edgeOffsets.count]
            * CGFloat(GachaPackOpeningRules.tornEdgeAmplitudePoints)
        return seamY(in: rect) + texture
    }
}

private struct ProductPackMouthMask: Shape {
    var progress: CGFloat
    var inset: CGFloat = 0

    var animatableData: AnimatablePair<CGFloat, CGFloat> {
        get { AnimatablePair(progress, inset) }
        set {
            progress = newValue.first
            inset = newValue.second
        }
    }

    func path(in rect: CGRect) -> Path {
        guard GachaPackOpeningRules.isMouthOpen(
            progress: Double(progress)) else {
            return Path()
        }

        var result = Path()
        let horizontalInset = min(
            inset,
            rect.width * 0.035)
        let left = rect.minX
            + rect.width * CGFloat(
                GachaPackOpeningRules.mouthInsetFraction)
            + horizontalInset
        let right = rect.maxX
            - rect.width * CGFloat(
                GachaPackOpeningRules.mouthInsetFraction)
            - horizontalInset
        guard right > left else { return result }

        for sample in 0...ProductPackTearPath.samples {
            let fraction = CGFloat(sample)
                / CGFloat(ProductPackTearPath.samples)
            let x = left + (right - left) * fraction
            let point = CGPoint(
                x: x,
                y: ProductPackTearPath.openingTopY(
                    at: x,
                    in: rect,
                    progress: progress) + inset)
            if sample == 0 {
                result.move(to: point)
            } else {
                result.addLine(to: point)
            }
        }
        // Bottom edge: the body's authored top edge, straight. A small
        // overlap into the body hides the anti-aliased hairline between the
        // two, and fades out where the sliver has no height.
        let seam = ProductPackTearPath.seamY(in: rect)
        for sample in stride(
            from: ProductPackTearPath.samples,
            through: 0,
            by: -1
        ) {
            let fraction = CGFloat(sample)
                / CGFloat(ProductPackTearPath.samples)
            let x = left + (right - left) * fraction
            let top = ProductPackTearPath.openingTopY(
                at: x,
                in: rect,
                progress: progress)
            let overlap = ProductPackTearPath.bodyOverlapPoints
                * min(max((seam - top) / 2, 0), 1)
            result.addLine(to: CGPoint(x: x, y: seam + overlap - inset))
        }
        result.closeSubpath()
        return result
    }
}

private struct ProductStaticSurfaceModeKey: EnvironmentKey {
    static let defaultValue = false
}

extension EnvironmentValues {
    var productUsesStaticSurfaces: Bool {
        get { self[ProductStaticSurfaceModeKey.self] }
        set { self[ProductStaticSurfaceModeKey.self] = newValue }
    }
}

struct ProductGlassModifier: ViewModifier {
    let cornerRadius: CGFloat
    let tint: Color
    let interactive: Bool
    @Environment(\.productUsesStaticSurfaces) private var usesStaticSurfaces

    @ViewBuilder
    func body(content: Content) -> some View {
        let shape = RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
        if usesStaticSurfaces {
            content
                .background(tint, in: shape)
                .background(Color.white.opacity(0.032), in: shape)
        } else if #available(iOS 26.0, *) {
            content
                .glassEffect(
                    .regular.tint(tint).interactive(interactive),
                    in: shape)
        } else {
            content
                .background(tint, in: shape)
                .background(.ultraThinMaterial, in: shape)
        }
    }
}

extension View {
    func productStaticSurfaceMode(_ enabled: Bool = true) -> some View {
        environment(\.productUsesStaticSurfaces, enabled)
    }

    func productGlass(
        cornerRadius: CGFloat = 20,
        tint: Color = Color.white.opacity(0.014),
        interactive: Bool = false) -> some View {
        modifier(ProductGlassModifier(
            cornerRadius: cornerRadius,
            tint: tint,
            interactive: interactive))
    }
}

struct ProductIconButton: View {
    let symbol: String
    let accessibilityLabel: String
    var selected = false
    var accent = Color.white
    var size = FidgetUITokens.Size.compactIconButton
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Image(systemName: symbol)
                .font(.product(size: 15, weight: .semibold))
                .foregroundStyle(selected
                                 ? Color.white
                                 : Color.white.opacity(FidgetUITokens.Opacity.tertiaryText))
                .frame(width: size, height: size)
                .background(
                    Color.white.opacity(selected ? FidgetUITokens.Opacity.selectedFill : 0.012),
                    in: RoundedRectangle(cornerRadius: size / 2, style: .continuous))
                .contentShape(RoundedRectangle(cornerRadius: size / 2, style: .continuous))
        }
        .buttonStyle(.plain)
        .productGlass(
            cornerRadius: size / 2,
            tint: accent.opacity(selected ? 0.045 : 0.018),
            interactive: true)
        .frame(minWidth: FidgetUITokens.Size.minimumHitTarget,
               minHeight: FidgetUITokens.Size.minimumHitTarget)
        .accessibilityLabel(accessibilityLabel)
        .accessibilityAddTraits(selected ? .isSelected : [])
    }
}

struct ProductIconSegmentedControl<Option: Identifiable & Equatable>: View {
    let options: [Option]
    let selection: Option
    let accent: Color
    let symbol: (Option) -> String
    let title: (Option) -> String
    let hint: (Option) -> String
    let onSelect: (Option) -> Void

    var body: some View {
        HStack(spacing: FidgetUITokens.Spacing.compact) {
            ForEach(options) { option in
                let selected = selection == option
                Button {
                    onSelect(option)
                } label: {
                    Image(systemName: symbol(option))
                        .font(.product(size: 17, weight: .semibold))
                        .frame(width: FidgetUITokens.Size.minimumHitTarget)
                        .frame(height: 40)
                        .foregroundStyle(selected
                                         ? Color.white
                                         : Color.white.opacity(0.36))
                        .background {
                            if selected {
                                RoundedRectangle(cornerRadius: 18, style: .continuous)
                                    .fill(Color.white.opacity(FidgetUITokens.Opacity.selectedFill))
                            }
                        }
                }
                .buttonStyle(.plain)
                .accessibilityLabel(title(option))
                .accessibilityHint(hint(option))
                .accessibilityAddTraits(selected ? .isSelected : [])
            }
        }
        .padding(FidgetUITokens.Spacing.compact)
        .fixedSize()
        .productGlass(
            cornerRadius: 24,
            tint: accent.opacity(0.035),
            interactive: true)
    }
}

struct ProductPageIndicator<Item: Hashable>: View {
    let items: [Item]
    let selection: Item
    let accessibilityLabel: (Int, Int) -> String

    private var selectedIndex: Int {
        items.firstIndex(of: selection) ?? 0
    }

    var body: some View {
        HStack(spacing: 7) {
            ForEach(items, id: \.self) { item in
                Capsule(style: .continuous)
                    .fill(selection == item
                          ? Color.white
                          : Color.white.opacity(0.28))
                    .frame(
                        width: selection == item
                            ? FidgetUITokens.Size.selectedPageDotWidth
                            : FidgetUITokens.Size.pageDot,
                        height: FidgetUITokens.Size.pageDot)
                    .animation(
                        .easeOut(duration: FidgetUITokens.Motion.selectionDuration),
                        value: selection)
                    .accessibilityHidden(true)
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(accessibilityLabel(selectedIndex + 1, items.count))
    }
}

struct ProductPrimaryActionLabel: View {
    enum Surface {
        case glass
        case filledWhite
    }

    let title: String
    var accent = Color.white
    var surface: Surface = .glass
    var titleGradient: LinearGradient? = nil
    /// Disabled/loading dim the title only; a `.filledWhite` plate stays
    /// pure white in every state (user 2026-09-08 18:48).
    var titleOpacity = 1.0

    var body: some View {
        Text(title)
            .font(.product(.headline, weight: .semibold))
            .foregroundStyle(titleForeground)
            .opacity(titleOpacity)
            .frame(maxWidth: .infinity)
            .frame(height: FidgetUITokens.Size.primaryActionHeight)
            .background {
                if surface == .filledWhite {
                    RoundedRectangle(
                        cornerRadius: FidgetUITokens.Radius.pill,
                        style: .continuous)
                        .fill(Color.white)
                } else {
                    Color.clear
                        .productGlass(
                            cornerRadius: FidgetUITokens.Radius.pill,
                            tint: accent.opacity(0.16),
                            interactive: true)
                }
            }
            .contentShape(RoundedRectangle(
                cornerRadius: FidgetUITokens.Radius.pill,
                style: .continuous))
    }

    private var titleForeground: some ShapeStyle {
        if let titleGradient {
            return AnyShapeStyle(titleGradient)
        }
        return AnyShapeStyle(surface == .filledWhite ? accent : Color.white)
    }
}

enum ProductActionState: Equatable {
    case ready
    case loading
    case disabled

    var isEnabled: Bool { self == .ready }
}

struct ProductPrimaryActionButton: View {
    let title: String
    var accent = Color.white
    var surface: ProductPrimaryActionLabel.Surface = .glass
    var titleGradient: LinearGradient? = nil
    var state: ProductActionState = .ready
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            ProductPrimaryActionLabel(
                title: title,
                accent: accent,
                surface: surface,
                titleGradient: titleGradient,
                titleOpacity: state == .ready ? 1 : (state == .loading ? 0 : 0.42))
                .overlay {
                    if state == .loading {
                        ProgressView()
                            .tint(surface == .filledWhite ? accent : .white)
                            .accessibilityHidden(true)
                    }
                }
                .opacity(state == .disabled && surface == .glass ? 0.42 : 1)
        }
        .buttonStyle(.plain)
        .disabled(!state.isEnabled)
        .accessibilityValue(state == .loading ? "处理中" : "")
    }
}

struct ProductSecondaryActionButton: View {
    let title: String
    var state: ProductActionState = .ready
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.product(.subheadline, weight: .semibold))
                .foregroundStyle(Color.white.opacity(0.82))
                .frame(
                    minWidth: FidgetUITokens.Size.minimumHitTarget,
                    minHeight: FidgetUITokens.Size.minimumHitTarget)
                .padding(.horizontal, FidgetUITokens.Spacing.standard)
                .productGlass(
                    cornerRadius: FidgetUITokens.Radius.compact,
                    tint: Color.white.opacity(0.018),
                    interactive: true)
        }
        .buttonStyle(.plain)
        .disabled(!state.isEnabled)
        .opacity(state == .disabled ? 0.42 : 1)
        .accessibilityValue(state == .loading ? "处理中" : "")
    }
}

struct ProductBottomActionDock<Content: View>: View {
    var tint = Color.white.opacity(0.025)
    let content: Content

    init(
        tint: Color = Color.white.opacity(0.025),
        @ViewBuilder content: () -> Content) {
        self.tint = tint
        self.content = content()
    }

    var body: some View {
        content
            .padding(FidgetUITokens.Spacing.section)
            .productGlass(
                cornerRadius: FidgetUITokens.Radius.card,
                tint: tint,
                interactive: false)
            .padding(.horizontal, FidgetUITokens.Spacing.section)
            .padding(.bottom, FidgetUITokens.Spacing.standard)
    }
}

struct ProductStatusTag: View {
    let title: String
    var accent = Color.white

    var body: some View {
        ProductInlineTag(title: title, accent: accent)
    }
}

struct ProductActionLabel: View {
    let title: String
    let symbol: String
    var accent = Color.white

    var body: some View {
        Label(title, systemImage: symbol)
            .font(.product(.subheadline, weight: .semibold))
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity)
            .frame(height: FidgetUITokens.Size.minimumHitTarget)
            .contentShape(RoundedRectangle(
                cornerRadius: FidgetUITokens.Radius.compact,
                style: .continuous))
            .productGlass(
                cornerRadius: FidgetUITokens.Radius.compact,
                tint: accent.opacity(0.10),
                interactive: true)
    }
}

struct ProductSectionCard<Content: View>: View {
    let title: String
    let symbol: String
    let content: Content

    init(
        _ title: String,
        symbol: String,
        @ViewBuilder content: () -> Content) {
        self.title = title
        self.symbol = symbol
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: FidgetUITokens.Spacing.section) {
            Label(title, systemImage: symbol)
                .font(.product(.headline))
                .foregroundStyle(.white)
            Divider().overlay(Color.white.opacity(0.12))
            content
        }
        .foregroundStyle(.white)
        .padding(16)
        .productGlass(cornerRadius: FidgetUITokens.Radius.card)
    }
}

struct ProductSheetDragHandle: View {
    let closeTitle: String
    let onClose: () -> Void

    var body: some View {
        Capsule(style: .continuous)
            .fill(Color.white.opacity(0.30))
            .frame(width: 38, height: 5)
            .frame(maxWidth: .infinity)
            .frame(height: 28)
            .contentShape(Rectangle())
            .onTapGesture(perform: onClose)
            .accessibilityElement()
            .accessibilityLabel(closeTitle)
            .accessibilityAddTraits(.isButton)
            .accessibilityAction(named: Text(closeTitle), onClose)
    }
}

struct ProductBottomSheetShell<Content: View>: View {
    let title: String
    let closeTitle: String
    let content: Content
    @Environment(\.dismiss) private var dismiss

    init(
        title: String,
        closeTitle: String = "完成",
        @ViewBuilder content: () -> Content) {
        self.title = title
        self.closeTitle = closeTitle
        self.content = content()
    }

    var body: some View {
        VStack(spacing: 0) {
            ProductSheetDragHandle(closeTitle: closeTitle) { dismiss() }
            NavigationView {
                content
                    .background(ProductBackdrop().ignoresSafeArea())
                    .navigationTitle(title)
                    .navigationBarTitleDisplayMode(.inline)
                    .navigationBarItems(trailing: Button(closeTitle) { dismiss() })
            }
            .navigationViewStyle(.stack)
        }
        .background(ProductBackdrop().ignoresSafeArea())
        .preferredColorScheme(.dark)
    }
}

struct ProductStatusPill: View {
    let title: String
    let symbol: String
    var accent = Color.white
    var selected = false
    var font = Font.product(.caption2, weight: .bold)

    var body: some View {
        Label(title, systemImage: symbol)
            .font(font)
            .foregroundStyle(accent.opacity(selected ? 0.94 : 0.76))
            .padding(.horizontal, 9)
            .padding(.vertical, 6)
            .background(
                accent.opacity(selected ? 0.14 : 0.06),
                in: Capsule())
            .accessibilityLabel(title)
            .accessibilityAddTraits(selected ? .isSelected : [])
    }
}

struct ProductProgressGauge: View {
    let value: Double
    var accent = Color.white

    private var clampedValue: Double {
        min(1, max(0, value))
    }

    var body: some View {
        GeometryReader { proxy in
            ZStack(alignment: .leading) {
                Capsule(style: .continuous)
                    .fill(Color.white.opacity(0.10))
                Capsule(style: .continuous)
                    .fill(accent.opacity(0.76))
                    .frame(width: proxy.size.width * clampedValue)
            }
        }
        .frame(height: 5)
        .animation(
            .easeOut(duration: FidgetUITokens.Motion.selectionDuration),
            value: clampedValue)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("进度")
        .accessibilityValue("\(Int((clampedValue * 100).rounded()))%")
    }
}

/// Shared compact milestone gauge for the persistent product chrome.
///
/// Endpoint numerals use the product caption-2 type ramp (11 pt at the default
/// content size) instead of feature-local microtype so the same values remain
/// legible in both top-level and tab-bar-adjacent placements.
struct ProductMilestoneProgressGauge: View {
    let previousLevel: Int
    let currentLevel: Int
    let nextLevel: Int
    let progress: Double
    var accent = Color.white

    private var clampedProgress: Double {
        min(1, max(0, progress))
    }

    var body: some View {
        HStack(spacing: 7) {
            endpointLabel(previousLevel, opacity: 0.58)

            GeometryReader { proxy in
                let width = max(1, proxy.size.width)
                let markerX = min(
                    width - 3,
                    max(3, width * CGFloat(clampedProgress)))

                ZStack(alignment: .leading) {
                    ProductProgressGauge(value: clampedProgress, accent: accent)
                        .frame(height: 4)

                    Circle()
                        .fill(Color.white)
                        .frame(width: 6, height: 6)
                        .overlay(Circle().stroke(accent.opacity(0.72), lineWidth: 1.5))
                        .shadow(color: accent.opacity(0.42), radius: 3)
                        .position(x: markerX, y: 6)
                }
            }
            .frame(height: 12)

            endpointLabel(nextLevel, opacity: 0.72)
        }
        .frame(minHeight: 16)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("成长里程碑")
        .accessibilityValue(
            "上一级 \(previousLevel)，当前 \(currentLevel)，下一级 \(nextLevel)")
    }

    private func endpointLabel(_ level: Int, opacity: Double) -> some View {
        Text("\(level)")
            .font(.product(.caption2, weight: .bold).monospacedDigit())
            .foregroundStyle(Color.white.opacity(opacity))
            .lineLimit(1)
            .fixedSize(horizontal: true, vertical: false)
    }
}

private struct ProductDashboardArc: Shape {
    func path(in rect: CGRect) -> Path {
        let radius = min(rect.width * 0.46, rect.height - 10)
        let center = CGPoint(x: rect.midX, y: rect.maxY - 10)
        var path = Path()
        path.addArc(
            center: center,
            radius: radius,
            startAngle: .radians(.pi),
            endAngle: .radians(.pi * 2),
            clockwise: false)
        return path
    }
}

/// The colored sweep is the dashboard indicator. Its radial edge is the current
/// value, so the center-to-rim gradient and the pointer can never drift into
/// separate layers.
private struct ProductDashboardSweepField: Shape {
    var fraction: Double

    var animatableData: Double {
        get { fraction }
        set { fraction = newValue }
    }

    func path(in rect: CGRect) -> Path {
        let progress = min(1, max(0, fraction))
        guard progress > 0.001 else { return Path() }

        let radius = min(rect.width * 0.46, rect.height - 10)
        let center = CGPoint(x: rect.midX, y: rect.maxY - 10)
        let startAngle = Angle.radians(.pi)
        let endAngle = Angle.radians(.pi + progress * .pi)
        let start = CGPoint(x: center.x - radius, y: center.y)
        let endpoint = CGPoint(
            x: center.x + CGFloat(cos(endAngle.radians)) * radius,
            y: center.y + CGFloat(sin(endAngle.radians)) * radius)

        var path = Path()
        path.move(to: center)
        path.addLine(to: start)
        path.addArc(
            center: center,
            radius: radius,
            startAngle: startAngle,
            endAngle: endAngle,
            clockwise: false)
        path.addLine(to: endpoint)
        path.addLine(to: center)
        path.closeSubpath()
        return path
    }
}

private func productDashboardGradientStops(
    accent: Color,
    outerOpacity: Double) -> [Gradient.Stop] {
    [
        .init(color: accent.opacity(0.00), location: 0.00),
        .init(color: accent.opacity(outerOpacity * 0.01), location: 0.20),
        .init(color: accent.opacity(outerOpacity * 0.05), location: 0.40),
        .init(color: accent.opacity(outerOpacity * 0.15), location: 0.56),
        .init(color: accent.opacity(outerOpacity * 0.34), location: 0.70),
        .init(color: accent.opacity(outerOpacity * 0.58), location: 0.82),
        .init(color: accent.opacity(outerOpacity * 0.78), location: 0.92),
        .init(color: accent.opacity(outerOpacity), location: 1.00)
    ]
}

private struct ProductDashboardTicks: View {
    let count: Int
    let majorEvery: Int

    var body: some View {
        Canvas { context, size in
            let center = CGPoint(x: size.width * 0.5, y: size.height - 10)
            let radius = min(size.width * 0.46, size.height - 10)
            let tickCount = max(2, count)

            for index in 0..<tickCount {
                let fraction = Double(index) / Double(tickCount - 1)
                let angle = Double.pi + fraction * Double.pi
                let major = index % max(1, majorEvery) == 0
                let outerRadius = radius - 1
                let innerRadius = radius - (major ? 10 : 5)
                var tick = Path()
                tick.move(to: CGPoint(
                    x: center.x + CGFloat(cos(angle)) * innerRadius,
                    y: center.y + CGFloat(sin(angle)) * innerRadius))
                tick.addLine(to: CGPoint(
                    x: center.x + CGFloat(cos(angle)) * outerRadius,
                    y: center.y + CGFloat(sin(angle)) * outerRadius))
                context.stroke(
                    tick,
                    with: .color(Color.white.opacity(major ? 0.72 : 0.28)),
                    style: StrokeStyle(
                        lineWidth: major ? 1.6 : 0.9,
                        lineCap: .round))
            }
        }
        .accessibilityHidden(true)
    }
}

private struct ProductDashboardCaption: View {
    let title: String
    let detail: String?

    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency

    var body: some View {
        HStack(spacing: 4) {
            Text(title)
                .foregroundStyle(Color.white)
            if let detail, !detail.isEmpty {
                Text(detail)
                    .foregroundStyle(Color.white.opacity(0.78))
            }
        }
        .font(.product(.caption2, weight: .bold))
        .lineLimit(1)
        .minimumScaleFactor(0.72)
        .allowsTightening(true)
        .padding(.horizontal, 7)
        .frame(height: 20)
        .background(
            Color.black.opacity(reduceTransparency ? 0.98 : 0.90),
            in: Capsule())
        .fixedSize(horizontal: false, vertical: true)
        .layoutPriority(2)
        .compositingGroup()
        .zIndex(5)
    }
}

/// A read-only automotive speed instrument. The caller owns telemetry,
/// normalization, speed-band hysteresis and semantic reward events.
struct ProductSpeedDashboard: View {
    let title: String
    let value: String
    let unit: String
    let fraction: Double
    let accent: Color
    let isPeak: Bool
    let stateLabel: String
    let accessibilityLabel: String
    let accessibilityValue: String

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @Environment(\.sizeCategory) private var sizeCategory
    @ScaledMetric(relativeTo: .title2) private var valueSize: CGFloat = 25

    private var clampedFraction: Double {
        min(1, max(0, fraction))
    }

    private var isAccessibilityCategory: Bool {
        sizeCategory.isAccessibilityCategory
    }

    var body: some View {
        GeometryReader { proxy in
            let gaugeHeight = min(84, max(68, proxy.size.width * 0.525))

            VStack(spacing: 2) {
                GeometryReader { gaugeProxy in
                    let gaugeRadius = min(
                        gaugeProxy.size.width * 0.46,
                        gaugeProxy.size.height - 10)
                    let gradientCenter = UnitPoint(
                        x: 0.5,
                        y: (gaugeProxy.size.height - 10) / gaugeProxy.size.height)

                    ZStack {
                        if reduceTransparency {
                            RoundedRectangle(cornerRadius: 18, style: .continuous)
                                .fill(Color.black.opacity(0.82))
                        }

                        ProductDashboardArc()
                            .stroke(
                                Color.white.opacity(0.13),
                                style: StrokeStyle(lineWidth: 2.5, lineCap: .round))

                        ProductDashboardSweepField(fraction: clampedFraction)
                            .fill(RadialGradient(
                                stops: productDashboardGradientStops(
                                    accent: accent,
                                    outerOpacity: isPeak ? 0.98 : 0.92),
                                center: gradientCenter,
                                startRadius: 0,
                                endRadius: gaugeRadius))
                            .shadow(
                                color: accent.opacity(
                                    reduceTransparency ? 0 : (isPeak ? 0.46 : 0.18)),
                                radius: reduceTransparency ? 0 : (isPeak ? 7 : 4))
                            .accessibilityHidden(true)

                        ProductDashboardTicks(
                            count: isAccessibilityCategory ? 7 : 13,
                            majorEvery: 3)

                        HStack(alignment: .firstTextBaseline, spacing: 3) {
                            Text(value)
                                .font(.product(
                                    size: valueSize,
                                    relativeTo: .largeTitle,
                                    weight: .bold).monospacedDigit())
                                .foregroundStyle(.white)
                                .minimumScaleFactor(0.72)
                                .lineLimit(1)

                            Text(unit)
                                .font(.product(.caption2, weight: .semibold))
                                .foregroundStyle(Color.white.opacity(0.54))
                        }
                        .padding(.horizontal, 5)
                        .padding(.vertical, 1)
                        .background(
                            Color.black.opacity(reduceTransparency ? 0.92 : 0.58),
                            in: Capsule())
                        .position(
                            x: gaugeProxy.size.width * 0.5,
                            y: gaugeProxy.size.height * 0.62)
                    }
                }
                .frame(height: gaugeHeight)

                ProductDashboardCaption(
                    title: title,
                    detail: stateLabel)
            }
            .frame(maxHeight: .infinity, alignment: .bottom)
        }
        .frame(height: isAccessibilityCategory ? 148 : 118)
        .animation(
            reduceMotion ? nil : .easeOut(duration: 0.10),
            value: clampedFraction)
        .animation(
            reduceMotion ? nil : .easeOut(duration: 0.18),
            value: accent)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(accessibilityLabel)
        .accessibilityValue(accessibilityValue)
    }
}

/// A subordinate wing instrument for secondary live metrics. It deliberately
/// inherits the Hero dashboard accent while using lower visual weight.
struct ProductSideMetricDashboard: View {
    let title: String
    let value: String
    let unit: String
    let fraction: Double
    let accent: Color
    let accessibilityLabel: String
    let accessibilityValue: String

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @Environment(\.sizeCategory) private var sizeCategory
    @ScaledMetric(relativeTo: .headline) private var valueSize: CGFloat = 17

    private var clampedFraction: Double {
        min(1, max(0, fraction))
    }

    var body: some View {
        GeometryReader { proxy in
            let gaugeHeight = min(54, max(48, proxy.size.width * 0.73))

            VStack(spacing: 2) {
                GeometryReader { gaugeProxy in
                    let gaugeRadius = min(
                        gaugeProxy.size.width * 0.46,
                        gaugeProxy.size.height - 10)
                    let gradientCenter = UnitPoint(
                        x: 0.5,
                        y: (gaugeProxy.size.height - 10) / gaugeProxy.size.height)

                    ZStack {
                        if reduceTransparency {
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(Color.black.opacity(0.76))
                        }

                        ProductDashboardArc()
                            .stroke(
                                Color.white.opacity(0.09),
                                style: StrokeStyle(lineWidth: 2, lineCap: .round))

                        ProductDashboardSweepField(fraction: clampedFraction)
                            .fill(RadialGradient(
                                stops: productDashboardGradientStops(
                                    accent: accent,
                                    outerOpacity: reduceTransparency ? 0.78 : 0.72),
                                center: gradientCenter,
                                startRadius: 0,
                                endRadius: gaugeRadius))
                            .shadow(
                                color: accent.opacity(
                                    reduceTransparency ? 0 : 0.12),
                                radius: reduceTransparency ? 0 : 2)
                            .accessibilityHidden(true)

                        ProductDashboardTicks(count: 7, majorEvery: 3)
                            .opacity(0.72)

                        HStack(alignment: .firstTextBaseline, spacing: 1) {
                            Text(value)
                                .font(.product(
                                    size: valueSize,
                                    relativeTo: .headline,
                                    weight: .bold).monospacedDigit())
                                .foregroundStyle(Color.white.opacity(0.84))
                                .minimumScaleFactor(0.72)
                                .lineLimit(1)

                            Text(unit)
                                .font(.product(.caption2, weight: .semibold))
                                .foregroundStyle(Color.white.opacity(0.40))
                        }
                        .padding(.horizontal, 3)
                        .background(
                            Color.black.opacity(reduceTransparency ? 0.90 : 0.54),
                            in: Capsule())
                        .position(
                            x: gaugeProxy.size.width * 0.5,
                            y: gaugeProxy.size.height * 0.64)
                    }
                }
                .frame(height: gaugeHeight)

                ProductDashboardCaption(
                    title: title,
                    detail: nil)
            }
            .frame(maxHeight: .infinity, alignment: .bottom)
        }
        .frame(height: sizeCategory.isAccessibilityCategory ? 98 : 78)
        .animation(
            reduceMotion ? nil : .easeOut(duration: 0.10),
            value: clampedFraction)
        .animation(
            reduceMotion ? nil : .easeOut(duration: 0.18),
            value: accent)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(accessibilityLabel)
        .accessibilityValue(accessibilityValue)
    }
}

struct ProductMetricCard: View {
    let title: String
    let value: String
    let symbol: String
    var accent = Color.white

    var body: some View {
        VStack(alignment: .leading, spacing: FidgetUITokens.Spacing.standard) {
            Image(systemName: symbol)
                .foregroundStyle(accent)
            Text(value)
                .font(.product(.title3, weight: .bold).monospacedDigit())
                .minimumScaleFactor(0.72)
                .lineLimit(1)
            Text(title)
                .font(.product(.caption))
                .foregroundStyle(Color.white.opacity(0.52))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(13)
        .productGlass(cornerRadius: 17, tint: Color.white.opacity(0.025))
    }
}

struct ProductScreenHeading: View {
    let title: String
    let subtitle: String
    var symbol: String? = nil
    var accent = Color.white
    var centered = false
    var titleStyle: Font.TextStyle = .title3
    var subtitleStyle: Font.TextStyle = .subheadline
    /// Small reversed-out raster mark above the title (user 2026-09-08
    /// 22:31: the Pack emblem, white, small and fine, over "CHASE").
    var emblemAssetName: String? = nil

    var body: some View {
        HStack(alignment: .top, spacing: FidgetUITokens.Spacing.standard) {
            VStack(
                alignment: centered ? .center : .leading,
                spacing: FidgetUITokens.Spacing.compact) {
                if let emblemAssetName {
                    ProductRasterAssetImage(name: emblemAssetName)
                        .frame(
                            width: FidgetUITokens.Size.headingEmblem,
                            height: FidgetUITokens.Size.headingEmblem)
                        .opacity(0.92)
                        .padding(.bottom, FidgetUITokens.Spacing.compact)
                        .accessibilityHidden(true)
                }
                Text(title)
                    .font(.product(titleStyle, weight: .bold))
                    .foregroundStyle(.white)
                if !subtitle.isEmpty {
                    Text(subtitle)
                        .font(.product(subtitleStyle))
                        .foregroundStyle(
                            Color.white.opacity(FidgetUITokens.Opacity.secondaryText))
                        .multilineTextAlignment(centered ? .center : .leading)
                }
            }
            .frame(maxWidth: .infinity, alignment: centered ? .center : .leading)

            if let symbol, !centered {
                Image(systemName: symbol)
                    .font(.product(.title2, weight: .medium))
                    .foregroundStyle(accent.opacity(0.76))
                    .accessibilityHidden(true)
            }
        }
        .accessibilityElement(children: .combine)
    }
}

struct ProductInlineTag: View {
    let title: String
    var accent = Color.white
    var filled = false

    var body: some View {
        Text(title)
            .font(.product(.caption2, weight: .bold))
            .foregroundStyle(filled ? Color.black.opacity(0.86) : accent.opacity(0.86))
            .padding(.horizontal, 6)
            .padding(.vertical, 3)
            .background(
                accent.opacity(filled ? 0.92 : 0.10),
                in: Capsule())
            .accessibilityLabel(title)
    }
}

struct ProductNoticeBanner: View {
    let kicker: String
    let title: String
    let detail: String
    let symbol: String
    var accent = Color.white
    var accessibilityLabel: String? = nil

    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency

    var body: some View {
        HStack(spacing: 13) {
            ZStack {
                Circle()
                    .fill(accent.opacity(0.13))
                    .background(.ultraThinMaterial, in: Circle())
                Image(systemName: symbol)
                    .font(.product(.title3, weight: .semibold))
                    .symbolVariant(.fill)
                    .foregroundStyle(accent.opacity(0.92))
            }
            .frame(width: 48, height: 48)
            .accessibilityHidden(true)

            VStack(alignment: .leading, spacing: 3) {
                Text(kicker)
                    .font(.product(.caption2, weight: .bold))
                    .foregroundStyle(accent.opacity(0.72))
                Text(title)
                    .font(.product(.headline, weight: .bold))
                    .foregroundStyle(.white)
                Text(detail)
                    .font(.product(.caption))
                    .foregroundStyle(
                        Color.white.opacity(FidgetUITokens.Opacity.secondaryText))
                    .lineLimit(2)
            }

            Spacer(minLength: 0)

            Image(systemName: "checkmark.circle.fill")
                .font(.product(.title2))
                .foregroundStyle(accent.opacity(0.78))
                .accessibilityHidden(true)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 13)
        .frame(maxWidth: 370)
        .background(
            Color.black.opacity(reduceTransparency ? 0.94 : 0.18),
            in: RoundedRectangle(
                cornerRadius: FidgetUITokens.Radius.card,
                style: .continuous))
        .productGlass(
            cornerRadius: FidgetUITokens.Radius.card,
            tint: accent.opacity(0.040))
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityLabel ?? "\(kicker)，\(title)，\(detail)")
    }
}

struct ProductSelectionCard<Content: View>: View {
    let selected: Bool
    let enabled: Bool
    var accent = Color.white
    let content: Content

    init(
        selected: Bool = false,
        enabled: Bool = true,
        accent: Color = .white,
        @ViewBuilder content: () -> Content) {
        self.selected = selected
        self.enabled = enabled
        self.accent = accent
        self.content = content()
    }

    var body: some View {
        content
            .padding(12)
            .background(
                Color.white.opacity(enabled ? 0.018 : 0.008),
                in: RoundedRectangle(cornerRadius: 17, style: .continuous))
            .productGlass(
                cornerRadius: 17,
                tint: selected
                    ? accent.opacity(0.075)
                    : Color.white.opacity(0.012))
            .opacity(enabled ? 1 : 0.62)
    }
}

struct ProductBadgeTile: View {
    let title: String
    let symbol: String
    let unlocked: Bool
    var accent = Color.white
    @Environment(\.productUsesStaticSurfaces) private var usesStaticSurfaces

    var body: some View {
        VStack(spacing: FidgetUITokens.Spacing.standard) {
            ZStack {
                Circle()
                    .fill(unlocked
                          ? accent.opacity(0.18)
                          : Color.white.opacity(0.035))
                    .background {
                        if usesStaticSurfaces {
                            Circle().fill(Color.white.opacity(0.035))
                        } else {
                            Circle().fill(.ultraThinMaterial)
                        }
                    }
                Image(systemName: unlocked ? symbol : "lock.fill")
                    .font(.product(.title3, weight: .semibold))
                    .foregroundStyle(unlocked
                                     ? accent.opacity(0.92)
                                     : Color.white.opacity(0.24))
            }
            .frame(width: 46, height: 46)
            .accessibilityHidden(true)

            Text(title)
                .font(.product(.caption, weight: .semibold))
                .foregroundStyle(Color.white.opacity(unlocked ? 0.88 : 0.34))
                .multilineTextAlignment(.center)
                .lineLimit(2)
                .frame(minHeight: 30)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 13)
        .background(
            Color.white.opacity(unlocked ? 0.046 : 0.016),
            in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .productGlass(
            cornerRadius: 18,
            tint: unlocked
                ? accent.opacity(0.040)
                : Color.white.opacity(0.008))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title)，\(unlocked ? "已点亮" : "未点亮")")
    }
}

enum ProductBadgeLayoutTokens {
    static let recentTargetWidth: CGFloat = 54
    static let detailWidth: CGFloat = 154
    static let shareCardWidth: CGFloat = 122

    // Shipping phone catalog: 375 - (20 * 2) - (14 * 2) = 307;
    // 307 / 3 = 102.333 pt per square Badge cell.
    static let catalogColumnCount = 3
    static let catalogHorizontalPadding: CGFloat = 20
    static let catalogColumnSpacing: CGFloat = 14
    static let catalogRowSpacing: CGFloat = 16
    static let iconSlotFraction: CGFloat = 0.46
    static let centeredContentHeightFraction: CGFloat = 0.64
    static let tokenSlotHeightFraction: CGFloat = 0.165
    static let tokenFontFraction: CGFloat = 0.124
    static let unitFontFraction: CGFloat = 0.048
    static let milestoneFontSize: CGFloat = 9.5
    static let milestoneSlotHeight: CGFloat = 13
    static let normalizedArtworkVisibleFraction: CGFloat = 0.74

    static var catalogColumns: [GridItem] {
        Array(
            repeating: GridItem(
                .flexible(minimum: 0, maximum: .infinity),
                spacing: catalogColumnSpacing,
                alignment: .top),
            count: catalogColumnCount)
    }

    static func catalogCellWidth(containerWidth: CGFloat) -> CGFloat {
        let gaps = CGFloat(catalogColumnCount - 1) * catalogColumnSpacing
        let content = containerWidth - catalogHorizontalPadding * 2 - gaps
        return max(0, content / CGFloat(catalogColumnCount))
    }

    // Every state and rarity uses one rounded-hexagon construction. Unlock state
    // controls luminance; grade must never change silhouette or measurements.
    static let outerRimFraction: CGFloat = 0.027
    static let rimGapFraction: CGFloat = 0.031
    static let innerRimFraction: CGFloat = 0.0045
}

private struct ProductBadgeShellShape: InsettableShape {
    var insetAmount: CGFloat = 0

    func inset(by amount: CGFloat) -> ProductBadgeShellShape {
        var copy = self
        copy.insetAmount += amount
        return copy
    }

    func path(in rect: CGRect) -> Path {
        let target = rect.insetBy(dx: insetAmount, dy: insetAmount)
        guard target.width > 0, target.height > 0 else { return Path() }
        return roundedHexagonPath(in: target)
    }

    private func roundedHexagonPath(in rect: CGRect) -> Path {
        // Point-up orientation: the endpoints sit at the top and bottom while
        // all six corners retain the same continuous rounding treatment.
        let vertices = [
            CGPoint(x: rect.midX, y: rect.minY + rect.height * 0.04),
            CGPoint(x: rect.minX + rect.width * 0.92, y: rect.minY + rect.height * 0.27),
            CGPoint(x: rect.minX + rect.width * 0.92, y: rect.minY + rect.height * 0.73),
            CGPoint(x: rect.midX, y: rect.minY + rect.height * 0.96),
            CGPoint(x: rect.minX + rect.width * 0.08, y: rect.minY + rect.height * 0.73),
            CGPoint(x: rect.minX + rect.width * 0.08, y: rect.minY + rect.height * 0.27)
        ]
        let cornerFraction: CGFloat = 0.16

        func point(_ vertex: CGPoint, toward neighbor: CGPoint) -> CGPoint {
            CGPoint(
                x: vertex.x + (neighbor.x - vertex.x) * cornerFraction,
                y: vertex.y + (neighbor.y - vertex.y) * cornerFraction)
        }

        var path = Path()
        path.move(to: point(vertices[0], toward: vertices[5]))
        for index in vertices.indices {
            let previous = vertices[(index + vertices.count - 1) % vertices.count]
            let current = vertices[index]
            let next = vertices[(index + 1) % vertices.count]
            let before = point(current, toward: previous)
            let after = point(current, toward: next)
            if index > 0 { path.addLine(to: before) }
            path.addQuadCurve(to: after, control: current)
        }
        path.closeSubpath()
        return path
    }
}

struct ProductBadgeLeatherTexture: View {
    var grainScale: CGFloat = 1

    var body: some View {
        Image("badge-leather-texture")
            .resizable()
            .interpolation(.high)
            .scaledToFill()
            .opacity(grainScale < 1 ? 0.78 : 1)
        .accessibilityHidden(true)
    }
}

private enum ProductBadgeArtworkCache {
    private static let catalogMaxPixelSize = 256
    private static let detailMaxPixelSize = 512
    private static let images: NSCache<NSString, UIImage> = {
        let cache = NSCache<NSString, UIImage>()
        cache.countLimit = 64
        cache.totalCostLimit = 24 * 1024 * 1024
        return cache
    }()
    private static let decodeQueue = DispatchQueue(
        label: "com.jiaweizhou.fidgetspinner.badge-artwork-decode",
        qos: .userInitiated)

    static func cachedImage(
        named assetName: String,
        catalog: Bool
    ) -> UIImage? {
        let maxPixelSize = catalog ? catalogMaxPixelSize : detailMaxPixelSize
        return images.object(forKey: cacheKey(
            assetName: assetName,
            maxPixelSize: maxPixelSize))
    }

    static func load(
        named assetName: String,
        catalog: Bool,
        completion: @escaping (UIImage?) -> Void
    ) {
        guard !assetName.isEmpty else {
            completion(nil)
            return
        }
        let maxPixelSize = catalog ? catalogMaxPixelSize : detailMaxPixelSize
        let key = cacheKey(assetName: assetName, maxPixelSize: maxPixelSize)
        if let cached = images.object(forKey: key) {
            completion(cached)
            return
        }

        decodeQueue.async {
            if let cached = images.object(forKey: key) {
                DispatchQueue.main.async { completion(cached) }
                return
            }
            let image = downsampledImage(
                named: assetName,
                maxPixelSize: maxPixelSize)
            if let image, let cgImage = image.cgImage {
                images.setObject(
                    image,
                    forKey: key,
                    cost: cgImage.bytesPerRow * cgImage.height)
            }
            DispatchQueue.main.async { completion(image) }
        }
    }

    static func prewarmCatalog(assetNames: [String]) {
        for assetName in assetNames where !assetName.isEmpty {
            load(named: assetName, catalog: true) { _ in }
        }
    }

    private static func cacheKey(
        assetName: String,
        maxPixelSize: Int
    ) -> NSString {
        "\(assetName)-\(maxPixelSize)" as NSString
    }

    private static func downsampledImage(
        named assetName: String,
        maxPixelSize: Int
    ) -> UIImage? {
        guard let url = Bundle.main.url(
            forResource: assetName,
            withExtension: "png"),
              let source = CGImageSourceCreateWithURL(
                url as CFURL,
                [kCGImageSourceShouldCache: false] as CFDictionary) else {
            return nil
        }
        let options: [CFString: Any] = [
            kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceCreateThumbnailWithTransform: true,
            kCGImageSourceThumbnailMaxPixelSize: maxPixelSize,
            kCGImageSourceShouldCacheImmediately: true
        ]
        guard let cgImage = CGImageSourceCreateThumbnailAtIndex(
            source,
            0,
            options as CFDictionary) else {
            return nil
        }
        return UIImage(
            cgImage: cgImage,
            scale: 1,
            orientation: .up)
    }
}

enum ProductBadgeRenderingMode {
    case catalog
    case full
}

private struct ProductBadgeArtworkLayer: View {
    let assetName: String
    let isUnlocked: Bool
    let renderingMode: ProductBadgeRenderingMode
    let width: CGFloat
    @State private var artwork: UIImage?

    private var usesCatalogRendering: Bool {
        renderingMode == .catalog
    }

    var body: some View {
        Group {
            if let artwork {
                if usesCatalogRendering {
                    Image(uiImage: artwork)
                        .resizable()
                        .scaledToFit()
                        .saturation(isUnlocked ? 1 : 0)
                        .brightness(isUnlocked ? 0.015 : -0.34)
                        .contrast(isUnlocked ? 1.06 : 0.74)
                        .opacity(isUnlocked ? 1 : 0.24)
                } else {
                    ZStack {
                        Image(uiImage: artwork)
                            .resizable()
                            .scaledToFit()
                            .saturation(0.70)
                            .contrast(1.12)
                            .blur(radius: width * 0.032)
                            .opacity(isUnlocked ? 0.34 : 0)
                            .blendMode(.screen)
                        Image(uiImage: artwork)
                            .resizable()
                            .scaledToFit()
                            .saturation(isUnlocked ? 1 : 0)
                            .brightness(isUnlocked ? 0.025 : -0.34)
                            .contrast(isUnlocked ? 1.12 : 0.74)
                            .opacity(isUnlocked ? 1 : 0.24)
                            .shadow(
                                color: Color.white.opacity(isUnlocked ? 0.22 : 0),
                                radius: width * 0.018,
                                x: -width * 0.006,
                                y: -width * 0.006)
                            .shadow(
                                color: Color(red: 0.72, green: 0.86, blue: 0.94)
                                    .opacity(isUnlocked ? 0.46 : 0),
                                radius: width * 0.052)
                    }
                }
            } else {
                Image(systemName: "seal")
                    .font(.product(size: width * 0.20, weight: .light))
                    .foregroundStyle(Color.white.opacity(0.20))
            }
        }
        .onAppear(perform: requestArtwork)
        .onChange(of: assetName) { _ in
            artwork = nil
            requestArtwork()
        }
    }

    private func requestArtwork() {
        if let cached = ProductBadgeArtworkCache.cachedImage(
            named: assetName,
            catalog: usesCatalogRendering) {
            artwork = cached
            return
        }
        ProductBadgeArtworkCache.load(
            named: assetName,
            catalog: usesCatalogRendering) { loaded in
            artwork = loaded
        }
    }
}

private struct ProductBadgeCatalogCompositingModifier: ViewModifier {
    let enabled: Bool

    @ViewBuilder
    func body(content: Content) -> some View {
        if enabled {
            content.drawingGroup(opaque: false, colorMode: .nonLinear)
        } else {
            content
        }
    }
}

struct ProductRarityBadge: View {
    let assetName: String
    let token: String
    let shortName: String
    let grade: String
    let state: String
    let progress: Double
    var renderingMode: ProductBadgeRenderingMode = .full

    static func prewarmCatalogArtwork(assetNames: [String]) {
        ProductBadgeArtworkCache.prewarmCatalog(assetNames: assetNames)
    }

    private var shape: ProductBadgeShellShape {
        ProductBadgeShellShape()
    }

    private var isUnlocked: Bool { state == "Unlocked" }
    private var isHidden: Bool { state == "Hidden" }
    private var isInProgress: Bool { state == "InProgress" }

    @ViewBuilder
    private func badgeToken(width: CGFloat) -> some View {
        if isHidden {
            Text("•••")
                .font(.product(
                    size: width * ProductBadgeLayoutTokens.tokenFontFraction,
                    weight: .black).monospacedDigit())
        } else if token.hasSuffix(" KM/H") {
            HStack(alignment: .lastTextBaseline, spacing: width * 0.020) {
                Text(String(token.dropLast(" KM/H".count)))
                    .font(.product(
                        size: width * ProductBadgeLayoutTokens.tokenFontFraction,
                        weight: .black).monospacedDigit())
                Text("KM/H")
                    .font(.product(
                        size: width * ProductBadgeLayoutTokens.unitFontFraction,
                        weight: .black).monospacedDigit())
                    .padding(.bottom, width * 0.011)
            }
        } else {
            Text(token)
                .font(.product(
                    size: width * ProductBadgeLayoutTokens.tokenFontFraction,
                    weight: .black).monospacedDigit())
        }
    }

    private var milestoneName: some View {
        Text(isHidden ? "ENCRYPTED" : shortName)
            .font(.product(
                size: ProductBadgeLayoutTokens.milestoneFontSize,
                weight: .bold))
            .foregroundStyle(Color.white.opacity(isUnlocked ? 0.72 : 0.28))
            .lineLimit(1)
            .minimumScaleFactor(0.72)
            .frame(
                maxWidth: .infinity,
                minHeight: ProductBadgeLayoutTokens.milestoneSlotHeight,
                maxHeight: ProductBadgeLayoutTokens.milestoneSlotHeight,
                alignment: .center)
    }

    private var externalProgressBar: some View {
        GeometryReader { gauge in
            let trackWidth = gauge.size.width * 0.72
            Capsule(style: .continuous)
                .fill(Color.white.opacity(0.10))
                .overlay(alignment: .leading) {
                    Capsule(style: .continuous)
                        .fill(Color.white.opacity(0.64))
                        .frame(width: trackWidth * max(0, min(1, progress)))
                }
                .frame(width: trackWidth, height: 3)
                .position(x: gauge.size.width * 0.5, y: 1.5)
        }
        .frame(height: 3)
        // Reserve the same slot for every state so all three catalog columns
        // keep matching row baselines even when only one Badge is in progress.
        .opacity(isInProgress ? 1 : 0)
        .accessibilityHidden(!isInProgress)
    }

    var body: some View {
        VStack(spacing: 0) {
            GeometryReader { proxy in
                let width = proxy.size.width
                let outerRim = max(2.1, width * ProductBadgeLayoutTokens.outerRimFraction)
                let rimGap = max(1.2, width * ProductBadgeLayoutTokens.rimGapFraction)
                let innerRim = max(0.7, width * ProductBadgeLayoutTokens.innerRimFraction)
                let innerInset = outerRim + rimGap
                let shellColors: [Color] = isUnlocked
                    ? [
                        Color(red: 0.090, green: 0.100, blue: 0.102),
                        Color(red: 0.038, green: 0.045, blue: 0.047),
                        Color(red: 0.015, green: 0.019, blue: 0.020)
                    ]
                    : [
                        Color(red: 0.030, green: 0.033, blue: 0.034),
                        Color(red: 0.014, green: 0.016, blue: 0.017),
                        Color(red: 0.006, green: 0.007, blue: 0.008)
                    ]
                let outerRimColors: [Color] = isUnlocked
                    ? [
                        Color(red: 0.72, green: 0.75, blue: 0.76),
                        Color(red: 0.32, green: 0.35, blue: 0.36),
                        Color(red: 0.82, green: 0.84, blue: 0.85)
                    ]
                    : [
                        Color(red: 0.18, green: 0.19, blue: 0.20),
                        Color(red: 0.070, green: 0.076, blue: 0.080),
                        Color(red: 0.22, green: 0.23, blue: 0.24)
                    ]
                let rimStops: [Gradient.Stop] = isUnlocked
                    ? [
                        .init(color: Color(red: 0.56, green: 0.59, blue: 0.60), location: 0.00),
                        .init(color: Color(red: 0.88, green: 0.90, blue: 0.91), location: 0.18),
                        .init(color: Color.white, location: 0.31),
                        .init(color: Color(red: 0.50, green: 0.53, blue: 0.54), location: 0.48),
                        .init(color: Color(red: 0.94, green: 0.96, blue: 0.96), location: 0.64),
                        .init(color: Color(red: 0.66, green: 0.69, blue: 0.70), location: 0.80),
                        .init(color: Color(red: 0.56, green: 0.59, blue: 0.60), location: 1.00)
                    ]
                    : [
                        .init(color: Color(red: 0.14, green: 0.15, blue: 0.16), location: 0.00),
                        .init(color: Color(red: 0.25, green: 0.26, blue: 0.27), location: 0.24),
                        .init(color: Color(red: 0.090, green: 0.096, blue: 0.100), location: 0.50),
                        .init(color: Color(red: 0.22, green: 0.23, blue: 0.24), location: 0.72),
                        .init(color: Color(red: 0.14, green: 0.15, blue: 0.16), location: 1.00)
                    ]
                let innerLineOpacity = isUnlocked ? 0.34 : 0.12
                ZStack {
                    shape
                        .fill(LinearGradient(
                            colors: shellColors,
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing))
                    shape
                        .fill(RadialGradient(
                            colors: [
                                Color.white.opacity(isUnlocked ? 0.060 : 0.020),
                                Color.white.opacity(0.010),
                                Color.black.opacity(isUnlocked ? 0.18 : 0.28)
                            ],
                            center: .topLeading,
                            startRadius: width * 0.02,
                            endRadius: width * 0.92))
                    ProductBadgeLeatherTexture()
                        .opacity(isUnlocked ? 1 : 0.58)
                        .clipShape(shape)
                    // One milled rim: a dark structural band with a narrower metal
                    // crest embedded inside it. The two strokes touch, so this reads
                    // as one bevelled object rather than two decorative outlines.
                    shape
                        .strokeBorder(
                            LinearGradient(
                                colors: outerRimColors,
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing),
                            lineWidth: outerRim)
                        .shadow(color: Color.black.opacity(0.64), radius: width * 0.015, y: width * 0.010)
                    shape
                        .inset(by: outerRim * 0.20)
                        .strokeBorder(
                            AngularGradient(
                                stops: rimStops,
                                center: .center),
                            lineWidth: outerRim * 0.58)
                        .shadow(
                            color: Color.white.opacity(isUnlocked ? 0.11 : 0),
                            radius: width * 0.010)
                    shape
                        .inset(by: innerInset)
                        .strokeBorder(
                            AngularGradient(
                                stops: [
                                    .init(color: Color.white.opacity(innerLineOpacity * 0.48), location: 0.00),
                                    .init(color: Color.white.opacity(innerLineOpacity), location: 0.31),
                                    .init(color: Color.white.opacity(innerLineOpacity * 0.38), location: 0.50),
                                    .init(color: Color.white.opacity(innerLineOpacity), location: 0.66),
                                    .init(color: Color.white.opacity(innerLineOpacity * 0.48), location: 1.00)
                                ],
                                center: .center),
                            lineWidth: innerRim)

                    VStack(spacing: width * 0.010) {
                        ZStack {
                            if isHidden {
                                Image(systemName: "questionmark")
                                    .font(.product(size: width * 0.23, weight: .bold))
                                    .foregroundStyle(Color.white.opacity(0.25))
                            } else {
                                ProductBadgeArtworkLayer(
                                    assetName: assetName,
                                    isUnlocked: isUnlocked,
                                    renderingMode: renderingMode,
                                    width: width)
                            }
                        }
                        .frame(
                            width: width * ProductBadgeLayoutTokens.iconSlotFraction,
                            height: width * ProductBadgeLayoutTokens.iconSlotFraction)

                        badgeToken(width: width)
                            .foregroundStyle(Color.white.opacity(isUnlocked ? 0.96 : 0.28))
                            .lineLimit(1)
                            .minimumScaleFactor(0.62)
                            .frame(
                                maxWidth: .infinity,
                                minHeight: width * ProductBadgeLayoutTokens.tokenSlotHeightFraction,
                                maxHeight: width * ProductBadgeLayoutTokens.tokenSlotHeightFraction,
                                alignment: .center)
                    }
                    // The icon and token are one fixed-height object pinned to
                    // the exact shell center. Individual glyph bounds or text
                    // ascenders can no longer move the group vertically.
                    .frame(
                        width: width * 0.74,
                        height: width * ProductBadgeLayoutTokens.centeredContentHeightFraction,
                        alignment: .center)
                    .position(x: width * 0.5, y: width * 0.5)

                    if !isUnlocked && !isHidden && !isInProgress {
                        Image(systemName: "lock.fill")
                            .font(.product(size: width * 0.075, weight: .bold))
                            .foregroundStyle(Color.white.opacity(0.34))
                            .padding(width * 0.055)
                            .background(Color.black.opacity(0.50), in: Circle())
                            .offset(y: width * 0.39)
                    }
                }
                .shadow(
                    color: Color.black.opacity(
                        renderingMode == .catalog ? 0.38 : 0.62),
                    radius: width * (renderingMode == .catalog ? 0.020 : 0.050),
                    y: width * (renderingMode == .catalog ? 0.014 : 0.032))
                .modifier(ProductBadgeCatalogCompositingModifier(
                    enabled: renderingMode == .catalog))
            }
            .aspectRatio(1, contentMode: .fit)

            // Milestone metadata belongs to the catalog tile, not the metal
            // object. Keep the shell itself a strict 1:1 artwork surface.
            milestoneName
                .padding(.top, 5)
            externalProgressBar
                .padding(.top, 5)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(token)，\(shortName)，\(state)")
    }
}

struct ProductCompactMetric: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: FidgetUITokens.Spacing.compact) {
            Text(title)
                .font(.product(.caption))
                .foregroundStyle(
                    Color.white.opacity(FidgetUITokens.Opacity.tertiaryText))
            Text(value)
                .font(.product(.subheadline, weight: .semibold).monospacedDigit())
                .foregroundStyle(.white)
                .lineLimit(1)
                .minimumScaleFactor(0.72)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(11)
        .background(
            Color.white.opacity(0.042),
            in: RoundedRectangle(cornerRadius: 13, style: .continuous))
    }
}

struct ProductSliderRow: View {
    let title: String
    let symbol: String
    let range: ClosedRange<Double>
    let step: Double
    let valueText: (Double) -> String
    @Binding var value: Double
    let apply: () -> Void
    var accent = Color.white

    var body: some View {
        VStack(alignment: .leading, spacing: FidgetUITokens.Spacing.standard) {
            HStack {
                Label(title, systemImage: symbol)
                    .font(.product(.subheadline, weight: .medium))
                    .foregroundStyle(.white)
                Spacer()
                Text(valueText(value))
                    .font(.product(.subheadline).monospacedDigit())
                    .foregroundStyle(
                        Color.white.opacity(FidgetUITokens.Opacity.secondaryText))
            }

            Slider(
                value: Binding(
                    get: { value },
                    set: {
                        value = $0
                        apply()
                    }),
                in: range,
                step: step)
                .tint(accent)
        }
    }
}

struct ProductToggleRow: View {
    let title: String
    let symbol: String
    @Binding var isOn: Bool
    var accent = Color.white
    var onChange: ((Bool) -> Void)? = nil

    var body: some View {
        Toggle(isOn: $isOn) {
            Label(title, systemImage: symbol)
                .foregroundStyle(.white)
        }
        .tint(accent)
        .onChange(of: isOn) { newValue in
            onChange?(newValue)
        }
    }
}

struct ProductEmptyState: View {
    let title: String
    let detail: String
    let symbol: String
    var accent = Color.white

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: symbol)
                .font(.product(.largeTitle))
                .foregroundStyle(accent.opacity(0.42))
                .accessibilityHidden(true)
            Text(title)
                .font(.product(.headline))
                .foregroundStyle(.white)
            Text(detail)
                .font(.product(.caption))
                .multilineTextAlignment(.center)
                .foregroundStyle(
                    Color.white.opacity(FidgetUITokens.Opacity.secondaryText))
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 30)
        .padding(.horizontal, 18)
        .productGlass(cornerRadius: FidgetUITokens.Radius.card)
        .accessibilityElement(children: .combine)
    }
}
