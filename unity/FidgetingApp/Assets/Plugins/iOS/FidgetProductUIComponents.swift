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
        static let filterChipHeight: CGFloat = 32
        static let statusTagHeight: CGFloat = 26
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
        static let metadata: CGFloat = 12
        static let section: CGFloat = 16
        static let pageInset: CGFloat = 20
        static let sectionGroup: CGFloat = 24
        static let majorGroup: CGFloat = 32
    }

    enum Opacity {
        static let primaryText = 0.92
        static let secondaryText = 0.58
        static let tertiaryText = 0.42
        static let selectedFill = 0.10
        static let disabledAction = 0.40
        static let primaryActionSurface = 0.96
        static let primaryActionInk = 0.90
    }

    enum Motion {
        static let selectionDuration = 0.18
        static let pressedDuration = 0.12
        static let pressedScale = 0.98
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

enum ProductActionState: Equatable {
    case rest
    case loading(String)
    case disabledValue(String?)
    case success(String)
    case error(String)

    /// Keeps existing `.disabled` call sites source-compatible while allowing
    /// new actions to explain why they are unavailable with
    /// `.disabled(reason: "...")`.
    static var disabled: Self {
        .disabledValue(nil)
    }

    static func disabled(reason: String) -> Self {
        .disabledValue(reason)
    }

    var disablesInteraction: Bool {
        switch self {
        case .loading, .disabledValue, .success:
            return true
        case .rest, .error:
            return false
        }
    }

    var accessibilityValue: String? {
        switch self {
        case .rest:
            return nil
        case .loading:
            return "处理中"
        case .disabledValue(let reason):
            guard let reason = Self.normalized(reason) else {
                return "不可用"
            }
            return "不可用，\(reason)"
        case .success:
            return "已完成"
        case .error:
            return "失败，可重试"
        }
    }

    func visibleTitle(default title: String) -> String {
        switch self {
        case .rest, .disabledValue:
            return title
        case .loading(let statusTitle),
             .success(let statusTitle),
             .error(let statusTitle):
            return statusTitle
        }
    }

    var isLoading: Bool {
        if case .loading = self { return true }
        return false
    }

    var isDisabled: Bool {
        if case .disabledValue = self { return true }
        return false
    }

    var disabledReason: String? {
        guard case .disabledValue(let reason) = self else { return nil }
        return Self.normalized(reason)
    }

    private static func normalized(_ value: String?) -> String? {
        guard let value else { return nil }
        let normalized = value.trimmingCharacters(in: .whitespacesAndNewlines)
        return normalized.isEmpty ? nil : normalized
    }
}

struct ProductActionButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed
                         ? FidgetUITokens.Motion.pressedScale
                         : 1)
            .animation(
                .easeOut(duration: FidgetUITokens.Motion.pressedDuration),
                value: configuration.isPressed)
    }
}

struct ProductPrimaryActionLabel: View {
    let title: String
    var accent = Color.white
    var state = ProductActionState.rest

    var body: some View {
        HStack(spacing: FidgetUITokens.Spacing.standard) {
            if state.isLoading {
                ProgressView()
                    .controlSize(.small)
                    .tint(Color.black.opacity(
                        FidgetUITokens.Opacity.primaryActionInk))
            }
            Text(state.visibleTitle(default: title))
                .font(.product(.headline, weight: .semibold))
        }
        .foregroundStyle(Color.black.opacity(
            FidgetUITokens.Opacity.primaryActionInk))
        .frame(maxWidth: .infinity)
        .frame(height: FidgetUITokens.Size.primaryActionHeight)
        .background(
            Color.white.opacity(FidgetUITokens.Opacity.primaryActionSurface),
            in: RoundedRectangle(
                cornerRadius: FidgetUITokens.Radius.pill,
                style: .continuous))
        .contentShape(RoundedRectangle(
            cornerRadius: FidgetUITokens.Radius.pill,
            style: .continuous))
        .opacity(state.isDisabled
                 ? FidgetUITokens.Opacity.disabledAction
                 : 1)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(state.visibleTitle(default: title))
        .accessibilityValue(state.accessibilityValue ?? "")
    }
}

struct ProductPrimaryActionButton: View {
    let title: String
    var accent = Color.white
    var state = ProductActionState.rest
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            ProductPrimaryActionLabel.init(
                title: title,
                accent: accent,
                state: state)
        }
        .buttonStyle(ProductActionButtonStyle())
        .disabled(state.disablesInteraction)
    }
}

struct ProductBottomActionDock<Content: View>: View {
    private let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        VStack(spacing: FidgetUITokens.Spacing.section) {
            content
        }
        .padding(.horizontal, FidgetUITokens.Spacing.pageInset)
        .padding(.top, FidgetUITokens.Spacing.sectionGroup)
        .padding(.bottom, FidgetUITokens.Spacing.section)
        .background {
            LinearGradient(
                colors: [
                    Color.black.opacity(0),
                    Color.black.opacity(0.72),
                    Color.black.opacity(0.92)
                ],
                startPoint: .top,
                endPoint: .bottom)
                .ignoresSafeArea(edges: .bottom)
        }
    }
}

struct ProductActionLabel: View {
    let title: String
    /// Source-compatible label metadata for older callers. Product-level text
    /// actions intentionally do not render decorative symbols.
    var symbol: String? = nil
    var accent = Color.white
    var state = ProductActionState.rest

    var body: some View {
        HStack(spacing: FidgetUITokens.Spacing.standard) {
            if state.isLoading {
                ProgressView()
                    .controlSize(.small)
                    .tint(.white)
            }
            Text(state.visibleTitle(default: title))
        }
            .font(.product(.subheadline, weight: .semibold))
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity)
            .frame(height: FidgetUITokens.Size.primaryActionHeight)
            .contentShape(RoundedRectangle(
                cornerRadius: FidgetUITokens.Radius.compact,
                style: .continuous))
            .productGlass(
                cornerRadius: FidgetUITokens.Radius.compact,
                tint: accent.opacity(0.10),
                interactive: true)
            .opacity(state.isDisabled
                     ? FidgetUITokens.Opacity.disabledAction
                     : 1)
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(state.visibleTitle(default: title))
            .accessibilityValue(state.accessibilityValue ?? "")
    }
}

struct ProductSecondaryActionButton: View {
    let title: String
    /// Preserved for call-site compatibility only; decorative symbols are not
    /// rendered beside product-level action copy.
    var symbol: String? = nil
    var accent = Color.white
    var state = ProductActionState.rest
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            ProductActionLabel(
                title: title,
                symbol: symbol,
                accent: accent,
                state: state)
        }
        .buttonStyle(ProductActionButtonStyle())
        .disabled(state.disablesInteraction)
    }
}

struct ProductFilterChip: View {
    let title: String
    var selected = false
    var enabled = true
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: FidgetUITokens.Spacing.compact) {
                if selected {
                    Image(systemName: "checkmark")
                        .font(.product(size: 11, weight: .bold))
                }
                Text(title)
                    .font(.product(.caption, weight: .semibold))
            }
            .foregroundStyle(selected
                             ? Color.black.opacity(0.90)
                             : Color.white.opacity(0.76))
            .padding(.horizontal, FidgetUITokens.Spacing.metadata)
            .frame(height: FidgetUITokens.Size.filterChipHeight)
            .background(
                selected
                    ? Color.white.opacity(0.92)
                    : Color.white.opacity(0.08),
                in: Capsule(style: .continuous))
        }
        .buttonStyle(ProductActionButtonStyle())
        .frame(minHeight: FidgetUITokens.Size.minimumHitTarget)
        .disabled(!enabled)
        .opacity(enabled ? 1 : FidgetUITokens.Opacity.disabledAction)
        .accessibilityAddTraits(selected ? .isSelected : [])
    }
}

struct ProductStatusTag: View {
    let title: String
    var symbol: String? = nil
    var accent = Color.white
    var emphasized = false
    var font = Font.product(.caption2, weight: .bold)

    @ViewBuilder
    private var content: some View {
        if let symbol {
            Label(title, systemImage: symbol)
        } else {
            Text(title)
        }
    }

    var body: some View {
        content
            .font(font)
            .foregroundStyle(accent.opacity(emphasized ? 0.94 : 0.76))
            .padding(.horizontal, emphasized ? 10 : 8)
            .frame(height: FidgetUITokens.Size.statusTagHeight)
            .background(
                accent.opacity(emphasized ? 0.14 : 0.06),
                in: Capsule(style: .continuous))
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(title)
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
        ProductStatusTag(
            title: title,
            symbol: symbol,
            accent: accent,
            emphasized: selected,
            font: font)
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
    static let milestoneFontSize: CGFloat = 8.5
    static let milestoneSlotHeight: CGFloat = 22
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
            CGPoint(x: rect.minX + rect.width * 0.90, y: rect.minY + rect.height * 0.27),
            CGPoint(x: rect.minX + rect.width * 0.90, y: rect.minY + rect.height * 0.73),
            CGPoint(x: rect.midX, y: rect.minY + rect.height * 0.96),
            CGPoint(x: rect.minX + rect.width * 0.10, y: rect.minY + rect.height * 0.73),
            CGPoint(x: rect.minX + rect.width * 0.10, y: rect.minY + rect.height * 0.27)
        ]
        let cornerFraction: CGFloat = 0.25

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
            .scaleEffect(grainScale < 1 ? 1.65 : 1.35)
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
                        .saturation(isUnlocked ? 0.86 : 0)
                        .brightness(isUnlocked ? 0.018 : -0.36)
                        .contrast(isUnlocked ? 1.02 : 0.72)
                        .opacity(isUnlocked ? 1 : 0.24)
                } else {
                    ZStack {
                        Image(uiImage: artwork)
                            .resizable()
                            .scaledToFit()
                            .saturation(0.62)
                            .contrast(1.02)
                            .blur(radius: width * 0.020)
                            .opacity(isUnlocked ? 0.14 : 0)
                            .blendMode(.screen)
                        Image(uiImage: artwork)
                            .resizable()
                            .scaledToFit()
                            .saturation(isUnlocked ? 0.86 : 0)
                            .brightness(isUnlocked ? 0.018 : -0.36)
                            .contrast(isUnlocked ? 1.03 : 0.72)
                            .opacity(isUnlocked ? 1 : 0.24)
                            .shadow(
                                color: Color.black.opacity(isUnlocked ? 0.58 : 0.30),
                                radius: width * 0.018,
                                x: width * 0.012,
                                y: width * 0.018)
                            .shadow(
                                color: Color.white.opacity(isUnlocked ? 0.10 : 0),
                                radius: width * 0.010,
                                x: -width * 0.004,
                                y: -width * 0.006)
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

    /// Forces full-resolution (`.full` rendering mode) artwork into cache and
    /// calls back once it resolves. Callers that snapshot a badge off-screen
    /// (for example the share-card renderer) must await this first, since the
    /// artwork otherwise decodes asynchronously after the snapshot is taken.
    static func prewarmFullArtwork(assetName: String, completion: @escaping () -> Void) {
        ProductBadgeArtworkCache.load(named: assetName, catalog: false) { _ in
            completion()
        }
    }

    private var shape: ProductBadgeShellShape {
        ProductBadgeShellShape()
    }

    private var isUnlocked: Bool { state == "Unlocked" }
    private var isHidden: Bool { state == "Hidden" }
    private var isInProgress: Bool { state == "InProgress" }

    private var externalMilestoneTitle: String {
        guard !isHidden else { return "ENCRYPTED" }
        return "\(shortName) \(token)"
    }

    private var milestoneName: some View {
        Text(externalMilestoneTitle)
            .font(.product(
                size: ProductBadgeLayoutTokens.milestoneFontSize,
                weight: .semibold).monospacedDigit())
            .foregroundStyle(Color.white.opacity(isUnlocked ? 0.54 : 0.24))
            .multilineTextAlignment(.center)
            .lineLimit(2)
            .minimumScaleFactor(0.68)
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
                ZStack {
                    if isHidden {
                        // Hidden Badges never reveal artwork, so they still need a
                        // plain hexagon shell to seat the placeholder glyph in.
                        shape
                            .fill(LinearGradient(
                                colors: [
                                    Color(red: 0.22, green: 0.22, blue: 0.25),
                                    Color(red: 0.17, green: 0.17, blue: 0.20),
                                    Color(red: 0.09, green: 0.09, blue: 0.11)
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing))
                            .overlay(
                                shape.strokeBorder(
                                    Color.white.opacity(0.10),
                                    lineWidth: max(0.9, width * 0.006)))
                        Image(systemName: "questionmark")
                            .font(.product(size: width * 0.23, weight: .bold))
                            .foregroundStyle(Color.white.opacity(0.25))
                    } else {
                        // The approved 2026-08-21 Challenge+Legacy master bakes its
                        // own pearl-silver satin hexagon shell, recessed well and
                        // bevel directly into the artwork, so the artwork fills the
                        // cell edge-to-edge instead of sitting inset inside a second
                        // shell drawn here — nesting both produced a double frame.
                        ProductBadgeArtworkLayer(
                            assetName: assetName,
                            isUnlocked: isUnlocked,
                            renderingMode: renderingMode,
                            width: width)
                            .frame(width: width, height: width)
                    }

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
                        renderingMode == .catalog ? 0.34 : 0.58),
                    radius: width * (renderingMode == .catalog ? 0.018 : 0.044),
                    y: width * (renderingMode == .catalog ? 0.012 : 0.028))
                .modifier(ProductBadgeCatalogCompositingModifier(
                    enabled: renderingMode == .catalog))
            }
            .aspectRatio(1, contentMode: .fit)

            // The reference language keeps every token and milestone label
            // outside the 1:1 metal object; the recessed face contains icon only.
            milestoneName
                .padding(.top, 6)
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
