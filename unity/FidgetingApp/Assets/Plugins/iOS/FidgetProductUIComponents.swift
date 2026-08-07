import SwiftUI
import CoreText
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

struct ProductGlassModifier: ViewModifier {
    let cornerRadius: CGFloat
    let tint: Color
    let interactive: Bool

    @ViewBuilder
    func body(content: Content) -> some View {
        let shape = RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
        if #available(iOS 26.0, *) {
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
    let title: String
    let symbol: String
    var accent = Color.white

    var body: some View {
        HStack(spacing: FidgetUITokens.Spacing.standard) {
            Text(title)
            Image(systemName: symbol)
        }
        .font(.product(.headline))
        .foregroundStyle(.white)
        .frame(maxWidth: .infinity)
        .frame(height: FidgetUITokens.Size.primaryActionHeight)
        .contentShape(RoundedRectangle(
            cornerRadius: FidgetUITokens.Radius.pill,
            style: .continuous))
        .productGlass(
            cornerRadius: FidgetUITokens.Radius.pill,
            tint: accent.opacity(0.16),
            interactive: true)
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

    var body: some View {
        HStack(alignment: .top, spacing: FidgetUITokens.Spacing.standard) {
            VStack(
                alignment: centered ? .center : .leading,
                spacing: FidgetUITokens.Spacing.compact) {
                Text(title)
                    .font(.product(.title3, weight: .bold))
                    .foregroundStyle(.white)
                Text(subtitle)
                    .font(.product(.subheadline))
                    .foregroundStyle(
                        Color.white.opacity(FidgetUITokens.Opacity.secondaryText))
                    .multilineTextAlignment(centered ? .center : .leading)
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

    var body: some View {
        VStack(spacing: FidgetUITokens.Spacing.standard) {
            ZStack {
                Circle()
                    .fill(unlocked
                          ? accent.opacity(0.18)
                          : Color.white.opacity(0.035))
                    .background(.ultraThinMaterial, in: Circle())
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
