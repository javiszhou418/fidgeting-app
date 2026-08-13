import SwiftUI
import UIKit

private enum DemoRarity: Int, CaseIterable, Identifiable {
    case standard
    case refined
    case signature
    case heirloom

    var id: Int { rawValue }

    var title: String {
        switch self {
        case .standard: return "蓝"
        case .refined: return "绿"
        case .signature: return "紫"
        case .heirloom: return "金"
        }
    }

    var name: String {
        switch self {
        case .standard: return "标准"
        case .refined: return "精制"
        case .signature: return "典藏"
        case .heirloom: return "传世"
        }
    }

    var color: Color {
        switch self {
        case .standard: return Color(red: 0.24, green: 0.57, blue: 1.00)
        case .refined: return Color(red: 0.22, green: 0.83, blue: 0.58)
        case .signature: return Color(red: 0.66, green: 0.38, blue: 1.00)
        case .heirloom: return Color(red: 1.00, green: 0.70, blue: 0.20)
        }
    }

    var probability: String {
        switch self {
        case .standard: return "60.0%"
        case .refined: return "30.0%"
        case .signature: return "9.0%"
        case .heirloom: return "1.0%"
        }
    }
}

private enum DemoItemKind: String {
    case toy = "玩具"
    case blueprint = "图纸"
}

private struct DemoPrize: Identifiable, Equatable {
    let id: String
    let title: String
    let subtitle: String
    let imageAssetName: String
    let kind: DemoItemKind
    let rarity: DemoRarity
    let owned: Bool
    let fragmentCount: Int
}

private enum DemoCatalog {
    // The only animated reveal in this disposable demo reuses the repository's
    // evidenced HEIRLOOM/GOLD three-blade storyboard. Keep the result semantics
    // aligned with the artwork instead of pretending it is a blue-tier pull.
    static let revealPrize = DemoPrize(
        id: "metal-three-blade-reveal",
        title: "三叶金属",
        subtitle: "全尺寸旋转陀螺",
        imageAssetName: "product-thumbnail-metal-three-blade",
        kind: .toy,
        rarity: .heirloom,
        owned: true,
        fragmentCount: 0)

    static let prizes: [DemoPrize] = [
        DemoPrize(id: "metal-three-blade", title: "三叶金属", subtitle: "全尺寸旋转陀螺", imageAssetName: "product-thumbnail-metal-three-blade", kind: .toy, rarity: .standard, owned: true, fragmentCount: 0),
        DemoPrize(id: "magnetic-slide-tile", title: "磁吸推牌", subtitle: "六档线性磁吸结构", imageAssetName: "product-thumbnail-magnetic-slide-tile", kind: .toy, rarity: .refined, owned: true, fragmentCount: 0),
        DemoPrize(id: "magnetic-fan-card", title: "磁吸扇牌", subtitle: "四档三牌联动结构", imageAssetName: "product-thumbnail-magnetic-fan-card", kind: .toy, rarity: .signature, owned: true, fragmentCount: 0),
        DemoPrize(id: "gold-four-wing", title: "镜钢四翼", subtitle: "四翼机械陀螺", imageAssetName: "product-thumbnail-gold-four-wing", kind: .toy, rarity: .heirloom, owned: false, fragmentCount: 18),
        DemoPrize(id: "night-cyan-index-blueprint", title: "夜航刻度图纸", subtitle: "深海蓝钢外观配方", imageAssetName: "skin-thumbnail-night-cyan-index", kind: .blueprint, rarity: .standard, owned: true, fragmentCount: 0),
        DemoPrize(id: "tungsten-honeycomb-blueprint", title: "钨金蜂巢图纸", subtitle: "钨黑蜂巢外观配方", imageAssetName: "skin-thumbnail-tungsten-honeycomb", kind: .blueprint, rarity: .refined, owned: false, fragmentCount: 42),
        DemoPrize(id: "blue-damascus-blueprint", title: "蓝钢水波图纸", subtitle: "大马士革水波配方", imageAssetName: "skin-thumbnail-blue-damascus", kind: .blueprint, rarity: .signature, owned: false, fragmentCount: 25),
        DemoPrize(id: "mirror-aurora-blueprint", title: "镜铬极光图纸", subtitle: "镜面精钢外观配方", imageAssetName: "skin-thumbnail-mirror-aurora", kind: .blueprint, rarity: .heirloom, owned: false, fragmentCount: 7)
    ]

    static let featuredSpinner = StoreProduct(
        id: "metal-three-blade",
        title: "三叶金属",
        subtitle: "全尺寸金属转子 · 十档同系列皮肤",
        imageAssetName: "product-thumbnail-metal-three-blade",
        category: .spinner,
        accent: Color(red: 0.32, green: 0.86, blue: 1.00))

    static let latestSkins: [StoreProduct] = [
        StoreProduct(id: "mirror-aurora", title: "镜铬极光", subtitle: "LV.100 · 镜面精钢", imageAssetName: "skin-thumbnail-mirror-aurora", category: .skin, accent: Color(red: 0.61, green: 0.96, blue: 1.00)),
        StoreProduct(id: "meteor-obsidian", title: "星陨黑曜", subtitle: "LV.90 · 黑曜 DLC", imageAssetName: "skin-thumbnail-meteor-obsidian", category: .skin, accent: Color(red: 0.78, green: 0.82, blue: 0.86)),
        StoreProduct(id: "titanium-heat", title: "钛虹热变", subtitle: "LV.75 · 阳极氧化钛", imageAssetName: "skin-thumbnail-titanium-heat", category: .skin, accent: Color(red: 0.85, green: 0.40, blue: 1.00))
    ]
}

private enum StoreProductCategory: String {
    case spinner = "陀螺"
    case skin = "皮肤"
}

private struct StoreProduct: Identifiable {
    let id: String
    let title: String
    let subtitle: String
    let imageAssetName: String
    let category: StoreProductCategory
    let accent: Color
}

private enum DemoRoute {
    case main
    case store
}

private enum DemoRevealPhase: Int, CaseIterable {
    case backFacing
    case flipToFront
    case prizeReadable
    case partsExploded
    case prizeOnly
    case lightPass
    case complete

    var assetName: String {
        switch self {
        case .backFacing: return "display-case-reveal-01-back-facing"
        case .flipToFront: return "display-case-reveal-02-flip-to-front"
        case .prizeReadable: return "display-case-reveal-03-prize-readable"
        case .partsExploded: return "display-case-reveal-04-parts-exploded"
        case .prizeOnly: return "display-case-reveal-05-prize-only"
        case .lightPass, .complete:
            return "display-case-reveal-06-light-pass-complete"
        }
    }

    var accessibilityTitle: String {
        switch self {
        case .backFacing: return "背面收藏盒"
        case .flipToFront: return "收藏盒翻正"
        case .prizeReadable: return "奖品揭晓"
        case .partsExploded: return "盒体散开"
        case .prizeOnly: return "奖品保留"
        case .lightPass: return "奖品过光"
        case .complete: return "揭晓完成"
        }
    }
}

private final class SingleDrawDemoState: ObservableObject {
    @Published var route: DemoRoute = .store
    @Published var tickets = 8
    @Published var gearCoins = 2_480
    @Published var selectedTab = 0
    @Published var lastPrize: DemoPrize?
    @Published var showingRechargeSheet = false
    @Published var showingProbabilitySheet = false
    @Published var showingFeaturedProductSheet = false
    @Published var drawSequence = 0
    let forcedRevealPhase: DemoRevealPhase?

    init() {
        let arguments = ProcessInfo.processInfo.arguments
        if arguments.contains("--preview-home") {
            route = .main
        }
        if let phase = Self.previewRevealPhase(arguments: arguments) {
            tickets = 7
            lastPrize = DemoCatalog.revealPrize
            drawSequence = 1
            forcedRevealPhase = phase
        } else if arguments.contains("--preview-collection") {
            selectedTab = 1
            forcedRevealPhase = nil
        } else {
            forcedRevealPhase = nil
        }
    }

    func performSingleDraw() {
        guard tickets > 0 else { return }
        tickets -= 1
        // This disposable Demo has one real, fully evidenced reveal asset.
        // Keep the outcome aligned with that asset instead of faking another prize.
        lastPrize = DemoCatalog.revealPrize
        drawSequence += 1
    }

    private static func previewRevealPhase(
        arguments: [String]) -> DemoRevealPhase? {
        if arguments.contains("--preview-reveal-back") { return .backFacing }
        if arguments.contains("--preview-reveal-front") { return .prizeReadable }
        if arguments.contains("--preview-reveal-exploded") { return .partsExploded }
        if arguments.contains("--preview-reveal-complete") { return .complete }
        return nil
    }
}

struct SingleDrawStoreDemoRoot: View {
    @StateObject private var state = SingleDrawDemoState()
    @State private var didStartAutoPreview = false

    var body: some View {
        Group {
            if state.route == .main {
                DemoMainEntryPage {
                    withAnimation(.easeOut(duration: 0.24)) {
                        state.route = .store
                    }
                }
            } else {
                storeRoot
            }
        }
        .preferredColorScheme(.dark)
        .sheet(isPresented: $state.showingProbabilitySheet) {
            ProbabilityDetailSheet()
        }
        .sheet(isPresented: $state.showingRechargeSheet) {
            RechargeBoundarySheet()
        }
        .sheet(isPresented: $state.showingFeaturedProductSheet) {
            FeaturedProductDetailSheet(product: DemoCatalog.featuredSpinner)
        }
        .overlay {
            if let prize = state.lastPrize {
                DrawRevealOverlay(
                    prize: prize,
                    sequence: state.drawSequence,
                    forcedPhase: state.forcedRevealPhase) {
                    state.lastPrize = nil
                }
            }
        }
        .onAppear(perform: runAutoPreviewIfNeeded)
    }

    private var storeRoot: some View {
        ZStack(alignment: .bottom) {
            DemoBackground()

            VStack(spacing: 0) {
                storeNavigation
                header
                segmentedTabs

                TabView(selection: $state.selectedTab) {
                    drawAndRedeem
                        .tag(0)
                    collection
                        .tag(1)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
            }

            if state.selectedTab == 0 {
                drawDock
            }
        }
    }

    private func runAutoPreviewIfNeeded() {
        let arguments = ProcessInfo.processInfo.arguments
        guard !didStartAutoPreview else { return }
        if arguments.contains("--preview-probability") {
            didStartAutoPreview = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) {
                state.showingProbabilitySheet = true
            }
            return
        }
        guard arguments.contains("--auto-demo") else { return }
        didStartAutoPreview = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.7) {
            state.performSingleDraw()
        }
    }

    private var storeNavigation: some View {
        HStack {
            Button("返回主页面") {
                withAnimation(.easeOut(duration: 0.24)) {
                    state.route = .main
                }
            }
            .font(.system(size: 13, weight: .bold))
            .foregroundStyle(.white.opacity(0.86))
            .buttonStyle(.plain)
            .accessibilityIdentifier("single-draw-back-main")
            Spacer()
            Text("商店 Demo")
                .font(.system(size: 10, weight: .bold))
                .foregroundStyle(.white.opacity(0.38))
        }
        .padding(.horizontal, 18)
        .padding(.top, 10)
        .padding(.bottom, 2)
    }

    private var header: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 3) {
                Text("机巧工坊")
                    .font(.system(size: 25, weight: .black, design: .rounded))
                Text("抽取全新结构 · 收集打造图纸")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(.white.opacity(0.48))
            }
            Spacer()
            walletChip(symbol: "ticket.fill", value: state.tickets, title: "抽取券")
            Button {
                state.showingRechargeSheet = true
            } label: {
                walletChip(symbol: "gearshape.2.fill", value: state.gearCoins, title: "齿轮币")
            }
            .buttonStyle(.plain)
            .accessibilityHint("打开充值说明；演示不会连接 App Store")
        }
        .padding(.horizontal, 18)
        .padding(.top, 14)
        .padding(.bottom, 12)
    }

    private func walletChip(symbol: String, value: Int, title: String) -> some View {
        HStack(spacing: 6) {
            Image(systemName: symbol)
                .font(.system(size: 11, weight: .bold))
                .foregroundStyle(.white.opacity(0.76))
            VStack(alignment: .leading, spacing: 0) {
                Text(value.formatted())
                    .font(.system(size: 11, weight: .bold, design: .rounded))
                Text(title)
                    .font(.system(size: 8, weight: .medium))
                    .foregroundStyle(.white.opacity(0.42))
            }
        }
        .padding(.horizontal, 10)
        .frame(height: 38)
        .background(.ultraThinMaterial, in: Capsule())
    }

    private var segmentedTabs: some View {
        HStack(spacing: 4) {
            tabButton("抽取 / 兑换", index: 0)
            tabButton("收藏", index: 1)
        }
        .padding(4)
        .background(Color.white.opacity(0.055), in: RoundedRectangle(cornerRadius: 15, style: .continuous))
        .padding(.horizontal, 18)
        .padding(.bottom, 10)
    }

    private func tabButton(_ title: String, index: Int) -> some View {
        Button {
            withAnimation(.easeOut(duration: 0.22)) {
                state.selectedTab = index
            }
        } label: {
            Text(title)
                .font(.system(size: 13, weight: .bold))
                .foregroundStyle(state.selectedTab == index ? Color.black.opacity(0.86) : Color.white.opacity(0.54))
                .frame(maxWidth: .infinity, minHeight: 38)
                .background(state.selectedTab == index ? Color.white.opacity(0.88) : Color.clear, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private var drawAndRedeem: some View {
        ScrollView(showsIndicators: false) {
            VStack(spacing: 14) {
                featuredBanner
                latestSkinShelf
                currencyExplanation
                previewGrid
                redeemCard
            }
            .padding(.horizontal, 18)
            .padding(.bottom, 142)
        }
    }

    private var featuredBanner: some View {
        GeometryReader { proxy in
            ZStack(alignment: .bottomLeading) {
                DemoArtwork(assetName: DemoCatalog.featuredSpinner.imageAssetName)
                    .scaledToFill()
                    .frame(width: proxy.size.width, height: proxy.size.height)
                    .clipped()
                LinearGradient(
                    colors: [.black.opacity(0.80), .black.opacity(0.34), .clear],
                    startPoint: .leading,
                    endPoint: .trailing)
                VStack(alignment: .leading, spacing: 6) {
                    HStack(spacing: 6) {
                        promotionalPill("本期主推", color: .white)
                        promotionalPill("精选陀螺", color: .white.opacity(0.76))
                    }
                    Text(DemoCatalog.featuredSpinner.title)
                        .font(.system(size: 25, weight: .black, design: .rounded))
                    Text(DemoCatalog.featuredSpinner.subtitle + "\n商品演示 · 尚未开放购买")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundStyle(.white.opacity(0.68))
                        .lineSpacing(3)
                    Button("查看详情") {
                        state.showingFeaturedProductSheet = true
                    }
                    .font(.system(size: 11, weight: .bold))
                    .foregroundStyle(.white.opacity(0.92))
                    .buttonStyle(.plain)
                    .padding(.top, 4)
                }
                .padding(18)
            }
        }
        .frame(height: 216)
        .clipShape(RoundedRectangle(cornerRadius: 26, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .stroke(Color.white.opacity(0.10), lineWidth: 1)
        }
    }

    private func promotionalPill(_ title: String, color: Color) -> some View {
        Text(title)
            .font(.system(size: 9, weight: .black))
            .foregroundStyle(color)
            .padding(.horizontal, 9)
            .frame(height: 24)
            .background(Color.black.opacity(0.50), in: Capsule())
            .overlay { Capsule().stroke(Color.white.opacity(0.18), lineWidth: 1) }
    }

    private var latestSkinShelf: some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeader(title: "同系列皮肤", category: "三叶金属")
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(DemoCatalog.latestSkins) { product in
                        StoreProductCard(product: product)
                    }
                }
            }
        }
    }

    private func sectionHeader(title: String, category: String) -> some View {
        HStack {
            Text(title)
                .font(.system(size: 15, weight: .bold))
            Spacer()
            Text(category)
                .font(.system(size: 9, weight: .bold))
                .foregroundStyle(.white.opacity(0.40))
        }
    }

    private var currencyExplanation: some View {
        HStack(spacing: 12) {
            Image(systemName: "gearshape.2.fill")
                .font(.system(size: 18, weight: .bold))
                .frame(width: 40, height: 40)
                .background(Color.white.opacity(0.08), in: RoundedRectangle(cornerRadius: 13, style: .continuous))
            VStack(alignment: .leading, spacing: 3) {
                Text("齿轮币不用于抽取")
                    .font(.system(size: 13, weight: .bold))
                Text("仅用于图纸打造费与已拥有陀螺的外观定制")
                    .font(.system(size: 10, weight: .medium))
                    .foregroundStyle(.white.opacity(0.48))
            }
            Spacer()
        }
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 19, style: .continuous))
    }

    private var previewGrid: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("本期抽取内容")
                    .font(.system(size: 15, weight: .bold))
                Spacer()
                Text("陀螺 + 图纸")
                    .font(.system(size: 10, weight: .medium))
                    .foregroundStyle(.white.opacity(0.42))
            }
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                ForEach(DemoCatalog.prizes.prefix(4)) { prize in
                    PrizeCell(prize: prize, compact: true)
                }
            }
        }
    }

    private var redeemCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("碎片兑换")
                    .font(.system(size: 15, weight: .bold))
                Spacer()
                Text("收集重复物后开放")
                    .font(.system(size: 9, weight: .medium))
                    .foregroundStyle(.white.opacity(0.40))
            }
            HStack(spacing: 12) {
                DemoArtwork(assetName: "skin-thumbnail-tungsten-honeycomb")
                    .scaledToFit()
                    .frame(width: 52, height: 52)
                    .background(DemoRarity.refined.color.opacity(0.11), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
                VStack(alignment: .leading, spacing: 3) {
                    Text("钨金蜂巢图纸")
                        .font(.system(size: 13, weight: .bold))
                    Text("42 / 80 碎片")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundStyle(.white.opacity(0.44))
                }
                Spacer()
                Text("尚未满足")
                    .font(.system(size: 10, weight: .bold))
                    .foregroundStyle(.white.opacity(0.28))
            }
        }
        .padding(15)
        .background(Color.white.opacity(0.045), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private var collection: some View {
        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 14) {
                HStack {
                    VStack(alignment: .leading, spacing: 3) {
                        Text("收藏图鉴")
                            .font(.system(size: 18, weight: .black))
                        Text("已拥有 4 / 8")
                            .font(.system(size: 10, weight: .medium))
                            .foregroundStyle(.white.opacity(0.44))
                    }
                    Spacer()
                    HStack(spacing: 5) {
                        ForEach(DemoRarity.allCases) { rarity in
                            Circle().fill(rarity.color).frame(width: 8, height: 8)
                        }
                    }
                }
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 11) {
                    ForEach(DemoCatalog.prizes) { prize in
                        PrizeCell(prize: prize, compact: false)
                    }
                }
            }
            .padding(.horizontal, 18)
            .padding(.bottom, 24)
        }
    }

    private var drawDock: some View {
        VStack(spacing: 10) {
            HStack(spacing: 10) {
                Button {
                    state.performSingleDraw()
                } label: {
                    VStack(spacing: 2) {
                        Text("单抽")
                            .font(.system(size: 16, weight: .black))
                        Text("消耗 1 张抽取券")
                            .font(.system(size: 9, weight: .medium))
                            .opacity(0.64)
                    }
                    .foregroundStyle(Color.black.opacity(0.88))
                    .frame(maxWidth: .infinity, minHeight: 54)
                    .background(Color.white.opacity(0.92), in: RoundedRectangle(cornerRadius: 17, style: .continuous))
                }
                .buttonStyle(.plain)
                .disabled(state.tickets < 1)

                VStack(spacing: 2) {
                    Text("十抽")
                        .font(.system(size: 15, weight: .bold))
                    Text("后续开放")
                        .font(.system(size: 9, weight: .medium))
                }
                .foregroundStyle(.white.opacity(0.30))
                .frame(width: 112, height: 54)
                .background(Color.white.opacity(0.04), in: RoundedRectangle(cornerRadius: 17, style: .continuous))
                .overlay { RoundedRectangle(cornerRadius: 17).stroke(Color.white.opacity(0.06), lineWidth: 1) }
            }
            Text("本 Demo 使用本地预览券，不连接真实抽卡或 App Store")
                .font(.system(size: 9, weight: .medium))
                .foregroundStyle(.white.opacity(0.36))
        }
        .padding(.horizontal, 18)
        .padding(.top, 12)
        .padding(.bottom, 12)
        .background(.ultraThinMaterial)
    }
}

private struct PrizeCell: View {
    let prize: DemoPrize
    let compact: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            ZStack {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(Color.white.opacity(0.04))
                DemoArtwork(assetName: prize.imageAssetName)
                    .scaledToFit()
                    .opacity(prize.owned || compact ? 1 : 0.38)
            }
            .frame(height: compact ? 76 : 100)
            HStack(spacing: 5) {
                Capsule().fill(prize.rarity.color).frame(width: 14, height: 4)
                Text(prize.rarity.name)
                    .font(.system(size: 8, weight: .bold))
                    .foregroundStyle(prize.rarity.color)
                Spacer()
                Text(prize.kind.rawValue)
                    .font(.system(size: 8, weight: .medium))
                    .foregroundStyle(.white.opacity(0.38))
            }
            Text(prize.title)
                .font(.system(size: 12, weight: .bold))
                .lineLimit(1)
            if !compact {
                Text(prize.owned ? "已拥有" : "碎片 " + String(prize.fragmentCount))
                    .font(.system(size: 9, weight: .medium))
                    .foregroundStyle(prize.owned ? Color.white.opacity(0.54) : Color.white.opacity(0.30))
            }
        }
        .padding(10)
        .background(Color.white.opacity(0.03), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay { RoundedRectangle(cornerRadius: 20).stroke(Color.white.opacity(0.09), lineWidth: 1) }
        .opacity(prize.owned || compact ? 1 : 0.72)
    }
}

private struct StoreProductCard: View {
    let product: StoreProduct

    var body: some View {
        VStack(alignment: .leading, spacing: 7) {
            DemoArtwork(assetName: product.imageAssetName)
                .scaledToFit()
                .frame(width: 126, height: 96)
                .background(Color.white.opacity(0.04), in: RoundedRectangle(cornerRadius: 17, style: .continuous))
            Text(product.title)
                .font(.system(size: 12, weight: .bold))
            Text(product.subtitle)
                .font(.system(size: 9, weight: .medium))
                .foregroundStyle(.white.opacity(0.44))
        }
        .padding(10)
        .frame(width: 146, alignment: .leading)
        .background(Color.white.opacity(0.04), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay { RoundedRectangle(cornerRadius: 20).stroke(Color.white.opacity(0.10), lineWidth: 1) }
    }
}

private struct FeaturedProductDetailSheet: View {
    @Environment(\.dismiss) private var dismiss
    let product: StoreProduct

    var body: some View {
        VStack(spacing: 14) {
            DemoArtwork(assetName: product.imageAssetName)
                .scaledToFit()
                .frame(height: 220)
                .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
            Text("本期主推 · 精选陀螺")
                .font(.system(size: 11, weight: .black))
                .foregroundStyle(product.accent)
            Text(product.title)
                .font(.system(size: 25, weight: .black, design: .rounded))
            Text(product.subtitle)
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(.white.opacity(0.56))
            Text("这是独立 UI Demo 的商品信息层。正式商品 ID、地区价格、恢复购买和权益规则确认前，不初始化 App Store，也不模拟购买成功。")
                .font(.system(size: 11, weight: .medium))
                .foregroundStyle(.white.opacity(0.48))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 22)
            Button("返回商品页") { dismiss() }
                .font(.system(size: 15, weight: .bold))
                .foregroundStyle(Color.black.opacity(0.86))
                .frame(maxWidth: .infinity, minHeight: 52)
                .background(Color.white, in: RoundedRectangle(cornerRadius: 17, style: .continuous))
                .padding(.top, 4)
        }
        .padding(18)
        .presentationDetents([.large])
        .presentationDragIndicator(.visible)
    }
}

private struct ProbabilityDetailSheet: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationView {
            List {
                Section("稀有度概率") {
                    ForEach(DemoRarity.allCases) { rarity in
                        HStack {
                            Circle().fill(rarity.color).frame(width: 9, height: 9)
                            Text(rarity.title + " · " + rarity.name)
                            Spacer()
                            Text(rarity.probability).monospacedDigit()
                        }
                    }
                }
                Section("规则说明") {
                    Text("抽取只消耗抽取券；齿轮币不参与抽取。")
                    Text("重复物在正式方案中计划转化为对应蓝图碎片。")
                    Text("保底次数、重复转化率和图纸兑换成本仍待产品确认。")
                }
            }
            .navigationTitle("概率与规则")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("完成") { dismiss() }
                }
            }
        }
    }
}

private struct RechargeBoundarySheet: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(spacing: 16) {
            Spacer()
            Image(systemName: "cart.badge.questionmark")
                .font(.system(size: 44, weight: .light))
            Text("充值入口尚未连接")
                .font(.system(size: 22, weight: .black))
            Text("正式产品只有在用户点击充值后，才会初始化并加载 App Store 商品。本隔离 Demo 不 import StoreKit，也不会发起网络或购买请求。")
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(.white.opacity(0.55))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 30)
            Spacer()
            Button("返回 Demo") { dismiss() }
                .font(.system(size: 15, weight: .bold))
                .foregroundStyle(Color.black.opacity(0.86))
                .frame(maxWidth: .infinity, minHeight: 52)
                .background(Color.white, in: RoundedRectangle(cornerRadius: 17, style: .continuous))
                .padding(18)
        }
        .presentationDetents([.medium])
        .presentationDragIndicator(.visible)
    }
}

private struct DrawRevealOverlay: View {
    let prize: DemoPrize
    let sequence: Int
    let forcedPhase: DemoRevealPhase?
    let dismiss: () -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var phase: DemoRevealPhase = .backFacing
    @State private var lightPassOffset: CGFloat = -230
    @State private var timelineTask: Task<Void, Never>?

    var body: some View {
        ZStack {
            Color.black.opacity(0.94).ignoresSafeArea()
            VStack(spacing: 12) {
                Text("单抽揭晓")
                    .font(.system(size: 12, weight: .bold))
                    .foregroundStyle(.white.opacity(0.55))
                revealArtwork
                if phase.rawValue >= DemoRevealPhase.prizeReadable.rawValue {
                    Text(prize.title)
                        .font(.system(size: 24, weight: .black, design: .rounded))
                    HStack(spacing: 6) {
                        Capsule().fill(prize.rarity.color).frame(width: 16, height: 4)
                        Text(prize.rarity.name + " · " + prize.kind.rawValue)
                            .font(.system(size: 11, weight: .bold))
                            .foregroundStyle(.white.opacity(0.62))
                    }
                    .transition(.opacity.combined(with: .move(edge: .bottom)))
                }
                Text(phase.accessibilityTitle)
                    .font(.system(size: 10, weight: .medium))
                    .foregroundStyle(.white.opacity(0.34))
                    .accessibilityIdentifier("single-draw-reveal-phase")
                if phase == .complete {
                    Button("收下") { dismiss() }
                        .font(.system(size: 15, weight: .bold))
                        .foregroundStyle(Color.black.opacity(0.86))
                        .frame(width: 210, height: 50)
                        .background(Color.white, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
                        .accessibilityIdentifier("single-draw-reveal-dismiss")
                        .transition(.opacity.combined(with: .move(edge: .bottom)))
                }
            }
            .padding(.horizontal, 22)
            .animation(.easeOut(duration: 0.25), value: phase)
        }
        .onAppear {
            beginTimeline()
        }
        .onDisappear { timelineTask?.cancel() }
        .id(sequence)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("单抽揭晓，" + phase.accessibilityTitle)
    }

    private var revealArtwork: some View {
        ZStack {
            DemoArtwork(assetName: phase.assetName)
                .scaledToFit()
                .saturation(0.22)
                .frame(maxWidth: 330, maxHeight: 440)
            if phase == .lightPass || phase == .complete {
                LinearGradient(
                    colors: [.clear, .white.opacity(0.72), .clear],
                    startPoint: .top,
                    endPoint: .bottom)
                    .frame(width: 68, height: 390)
                    .rotationEffect(.degrees(18))
                    .offset(x: lightPassOffset)
                    .blendMode(.screen)
                    .mask {
                        DemoArtwork(assetName: phase.assetName)
                            .scaledToFit()
                            .saturation(0.22)
                            .frame(maxWidth: 330, maxHeight: 440)
                    }
            }
        }
        .frame(maxWidth: .infinity, minHeight: 450, maxHeight: 450)
        .clipped()
    }

    private func beginTimeline() {
        if let forcedPhase {
            phase = forcedPhase
            lightPassOffset = forcedPhase == .complete ? 230 : -230
            return
        }
        if reduceMotion {
            phase = .complete
            lightPassOffset = 230
            return
        }
        timelineTask?.cancel()
        timelineTask = Task { @MainActor in
            phase = .backFacing
            try? await Task.sleep(nanoseconds: 800_000_000)
            guard !Task.isCancelled else { return }
            phase = .flipToFront
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            guard !Task.isCancelled else { return }
            phase = .prizeReadable
            try? await Task.sleep(nanoseconds: 900_000_000)
            guard !Task.isCancelled else { return }
            phase = .partsExploded
            try? await Task.sleep(nanoseconds: 1_400_000_000)
            guard !Task.isCancelled else { return }
            phase = .prizeOnly
            try? await Task.sleep(nanoseconds: 350_000_000)
            guard !Task.isCancelled else { return }
            phase = .lightPass
            lightPassOffset = -230
            withAnimation(.easeInOut(duration: 1.3)) {
                lightPassOffset = 230
            }
            try? await Task.sleep(nanoseconds: 1_300_000_000)
            guard !Task.isCancelled else { return }
            phase = .complete
        }
    }
}

private struct DemoBackground: View {
    var body: some View {
        LinearGradient(
            colors: [Color(white: 0.065), .black, Color(white: 0.035)],
            startPoint: .top,
            endPoint: .bottom)
            .ignoresSafeArea()
    }
}

private struct DemoMainEntryPage: View {
    let enterStore: () -> Void

    var body: some View {
        ZStack {
            DemoBackground()
            VStack(alignment: .leading, spacing: 18) {
                Spacer()
                Text("fidgeting")
                    .font(.system(size: 13, weight: .black))
                    .foregroundStyle(.white.opacity(0.42))
                Text("主页面")
                    .font(.system(size: 34, weight: .black, design: .rounded))
                Text("这是隔离 Demo 的简洁入口页。返回后可以重新进入商店，正式 App 页面没有被替换。")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(.white.opacity(0.52))
                    .lineSpacing(4)
                Button("进入机巧工坊") { enterStore() }
                    .font(.system(size: 16, weight: .bold))
                    .foregroundStyle(Color.black.opacity(0.88))
                    .frame(maxWidth: .infinity, minHeight: 54)
                    .background(Color.white, in: RoundedRectangle(cornerRadius: 17, style: .continuous))
                    .accessibilityIdentifier("single-draw-enter-store")
                Spacer()
            }
            .padding(24)
        }
    }
}

private struct DemoArtwork: View {
    let assetName: String

    var body: some View {
        Group {
            if let url = Bundle.main.url(forResource: assetName, withExtension: "png"),
               let image = UIImage(contentsOfFile: url.path) {
                Image(uiImage: image)
                    .resizable()
            } else {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(Color.white.opacity(0.035))
                    .overlay {
                        Text("预览图缺失")
                            .font(.system(size: 9, weight: .bold))
                            .foregroundStyle(.white.opacity(0.28))
                    }
            }
        }
        .accessibilityHidden(true)
    }
}
