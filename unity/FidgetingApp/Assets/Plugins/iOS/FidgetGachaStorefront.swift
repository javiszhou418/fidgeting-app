import Foundation
import SwiftUI
import UIKit

private func gachaSequenceLog(_ message: String) {
#if DEBUG
    NSLog("%@", message)
#endif
}

// Shipping storefront presentation. Economy, ownership, transaction recovery,
// and the 3D reveal timeline stay owned by Unity. SwiftUI only hosts controls and
// a transparent accessibility/HUD surface above Unity's real presentation.
public struct GachaStoreView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject private var model = GachaStoreModel.shared
    @State private var selectedTab = 0
    @State private var showDisclosure = false
    // Presentation-only tier choice shown before the authoritative draw is
    // requested. Non-nil while the carousel is on screen; the model/Unity
    // transaction chain is untouched until the user confirms a tier.
    @State private var carouselSeries: GachaSeriesInfo?
    @State private var carouselSelectedTier: GachaPackTier = .standard
    @State private var confirmedPackTier: GachaPackTier = .standard

    public init() {}

    private var activeSeries: GachaSeriesInfo? { model.series.first }

    public var body: some View {
        ZStack(alignment: .bottom) {
            // Dedicated one-pixel markers keep every child control's own AX
            // identifier intact. Applying an identifier to this parent ZStack
            // would cause SwiftUI to propagate it over the full subtree.
            GachaAccessibilityStateMarkers(
                model: model,
                seriesId: activeSeries?.id ?? "")
                .zIndex(30)

            storefrontContent
                .opacity(model.revealIsPresented
                    || model.packIsPresented
                    || carouselSeries != nil ? 0 : 1)
                .allowsHitTesting(!model.revealIsPresented
                    && !model.packIsPresented
                    && carouselSeries == nil)
                .accessibilityHidden(model.revealIsPresented
                    || model.packIsPresented
                    || carouselSeries != nil)

            if model.packIsPresented,
               let transaction = model.pendingTransaction {
                GachaPackOpeningOverlay(
                    model: model,
                    transaction: transaction,
                    tier: confirmedPackTier)
                    .id(transaction.requestId)
                    .transition(.opacity)
                    .zIndex(25)
            }

            if model.revealIsPresented,
               let transaction = model.pendingTransaction {
                GachaThreeDRevealOverlay(
                    model: model,
                    transaction: transaction)
                .transition(.opacity)
                .zIndex(20)
            }

            if let series = carouselSeries {
                GachaPackTierCarouselOverlay(
                    selectedTier: $carouselSelectedTier,
                    onCancel: { carouselSeries = nil },
                    onConfirm: {
                        let tier = carouselSelectedTier
                        confirmedPackTier = tier
                        carouselSeries = nil
                        gachaSequenceLog(
                            "[GachaSequence] carousel-confirmed tier=\(tier.rawValue) presentationOnly=true")
                        model.draw(seriesId: series.id, count: 1, useCoins: false)
                    })
                    .accessibilityAddTraits(.isModal)
                    .transition(.opacity)
                    .zIndex(26)
            }
        }
        .background(GachaTransparentPresentationBackground())
        .preferredColorScheme(.dark)
        .interactiveDismissDisabled(!model.activeRequestId.isEmpty)
        .onAppear {
            model.requestState()
            model.requestRevealSetupIfNeeded()
        }
        .sheet(isPresented: $showDisclosure) {
            probabilityDisclosure
        }
    }

    private var storefrontContent: some View {
        ZStack(alignment: .bottom) {
            Color.black.ignoresSafeArea()

            VStack(spacing: 0) {
                navigation
                header
                tabs

                TabView(selection: $selectedTab) {
                    drawAndRedeem.tag(0)
                    collection.tag(1)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
            }

            if selectedTab == 0, let series = activeSeries {
                VStack(spacing: 0) {
                    transactionStatus
                    drawDock(series)
                }
            }
        }
    }

    private var navigation: some View {
        HStack {
            Button("返回主页") {
                dismiss()
            }
            .font(.system(size: 14, weight: .bold))
            .foregroundColor(.white.opacity(0.88))
            .buttonStyle(.plain)
            .disabled(!model.activeRequestId.isEmpty)
            .accessibilityIdentifier("gacha-return-home")

            Spacer()

            Text("机巧工坊")
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(.white.opacity(0.42))
        }
        .padding(.horizontal, 18)
        .padding(.top, 12)
        .padding(.bottom, 4)
    }

    private var header: some View {
        HStack(spacing: 10) {
            VStack(alignment: .leading, spacing: 3) {
                Text("抽取与收藏")
                    .font(.system(size: 27, weight: .black, design: .rounded))
                    .foregroundColor(.white)
                Text("票券抽取 · 外观收藏 · 图纸兑换")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.white.opacity(0.48))
                Text(model.runtimeMode.title)
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundColor(
                        model.runtimeMode == .internalUnlimited
                            ? .green.opacity(0.82)
                            : .white.opacity(0.38))
                    .accessibilityIdentifier("gacha-runtime-mode")
            }

            Spacer(minLength: 8)
            walletChip(
                symbol: "ticket.fill",
                value: model.ticketBalanceText,
                title: model.runtimeMode.title)
            walletChip(
                symbol: "gearshape.2.fill",
                value: "\(model.coins)",
                title: "齿轮币")
        }
        .padding(.horizontal, 18)
        .padding(.vertical, 12)
    }

    private func walletChip(
        symbol: String,
        value: String,
        title: String
    ) -> some View {
        HStack(spacing: 6) {
            Image(systemName: symbol)
                .font(.system(size: 12, weight: .semibold))
            VStack(alignment: .leading, spacing: 0) {
                Text(value)
                    .font(.system(size: 13, weight: .bold, design: .monospaced))
                Text(title)
                    .font(.system(size: 8, weight: .medium))
                    .foregroundColor(.white.opacity(0.45))
            }
        }
        .foregroundColor(.white.opacity(0.90))
        .padding(.horizontal, 10)
        .frame(height: 44)
        .background(Color.white.opacity(0.08), in: Capsule())
    }

    private var tabs: some View {
        HStack(spacing: 0) {
            tabButton("抽取 / 兑换", index: 0)
            tabButton("收藏", index: 1)
        }
        .padding(5)
        .background(Color.white.opacity(0.06), in: RoundedRectangle(cornerRadius: 18))
        .padding(.horizontal, 18)
        .padding(.bottom, 8)
    }

    private func tabButton(_ title: String, index: Int) -> some View {
        Button {
            withAnimation(.easeOut(duration: 0.20)) {
                selectedTab = index
            }
        } label: {
            Text(title)
                .font(.system(size: 14, weight: .bold))
                .foregroundColor(selectedTab == index ? .black : .white.opacity(0.58))
                .frame(maxWidth: .infinity)
                .frame(height: 43)
                .background(
                    selectedTab == index ? Color.white.opacity(0.90) : Color.clear,
                    in: RoundedRectangle(cornerRadius: 14))
        }
        .buttonStyle(.plain)
    }

    private var drawAndRedeem: some View {
        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 16) {
                featuredBanner
                relatedSkins
                economyNotice

                if let series = activeSeries {
                    drawPoolSummary(series)
                    redeemShop(series)
                } else {
                    ProgressView()
                        .tint(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.top, 50)
                }
            }
            .padding(.horizontal, 18)
            .padding(.bottom, 126)
        }
    }

    private var featuredBanner: some View {
        ZStack(alignment: .bottomLeading) {
            GachaBundleArtwork(name: "product-thumbnail-metal-three-blade")
                .scaledToFill()
                .frame(maxWidth: .infinity)
                .frame(height: 218)
                .clipped()

            LinearGradient(
                colors: [.clear, Color.black.opacity(0.28), Color.black.opacity(0.92)],
                startPoint: .top,
                endPoint: .bottom)

            VStack(alignment: .leading, spacing: 6) {
                HStack(spacing: 7) {
                    quietBadge("本期主推")
                    quietBadge("精选陀螺")
                }
                Text("三叶金属")
                    .font(.system(size: 27, weight: .black, design: .rounded))
                Text("全尺寸金属转子 · 十档同系列皮肤")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.white.opacity(0.72))
                Text("商品展示 · 尚未开放购买")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.white.opacity(0.55))
            }
            .foregroundColor(.white)
            .padding(18)
        }
        .frame(height: 218)
        .background(Color(white: 0.06))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(Color.white.opacity(0.10), lineWidth: 0.7)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("本期主推，三叶金属，商品展示尚未开放购买")
    }

    private func quietBadge(_ text: String) -> some View {
        Text(text)
            .font(.system(size: 10, weight: .bold))
            .padding(.horizontal, 9)
            .frame(height: 26)
            .background(Color.black.opacity(0.44), in: Capsule())
            .overlay { Capsule().stroke(Color.white.opacity(0.18), lineWidth: 0.7) }
    }

    private var relatedSkins: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("同系列皮肤")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(.white)
                Spacer()
                Text("三叶金属")
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(.white.opacity(0.36))
            }

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    skinCard("镜铬极光", subtitle: "LV.100 · 镜面精钢", image: "skin-thumbnail-mirror-aurora")
                    skinCard("星陨黑曜", subtitle: "LV.90 · 黑曜 DLC", image: "skin-thumbnail-meteor-obsidian")
                    skinCard("钛虹热变", subtitle: "LV.75 · 阳极氧化钛", image: "skin-thumbnail-titanium-heat")
                }
            }
        }
    }

    private func skinCard(_ title: String, subtitle: String, image: String) -> some View {
        VStack(alignment: .leading, spacing: 7) {
            GachaBundleArtwork(name: image)
                .scaledToFill()
                .frame(width: 144, height: 124)
                .clipped()
                .background(Color(white: 0.035))
            Text(title)
                .font(.system(size: 14, weight: .bold))
                .foregroundColor(.white)
            Text(subtitle)
                .font(.system(size: 10, weight: .medium))
                .foregroundColor(.white.opacity(0.42))
        }
        .padding(10)
        .frame(width: 164, alignment: .leading)
        .background(Color.white.opacity(0.055), in: RoundedRectangle(cornerRadius: 18))
        .overlay {
            RoundedRectangle(cornerRadius: 18)
                .stroke(Color.white.opacity(0.075), lineWidth: 0.7)
        }
    }

    private var economyNotice: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("齿轮币不用于抽取")
                .font(.system(size: 14, weight: .bold))
                .foregroundColor(.white)
            Text("抽取只消耗抽取券；齿轮币保留给打造和已拥有外观的定制。")
                .font(.system(size: 11, weight: .medium))
                .foregroundColor(.white.opacity(0.48))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(15)
        .background(Color.white.opacity(0.055), in: RoundedRectangle(cornerRadius: 18))
    }

    private func drawPoolSummary(_ series: GachaSeriesInfo) -> some View {
        Button {
            showDisclosure = true
        } label: {
            HStack {
                VStack(alignment: .leading, spacing: 3) {
                    Text("本期抽取内容")
                        .font(.system(size: 18, weight: .bold))
                    Text("\(series.name) · 查看概率、保底与重复兑换规则")
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.white.opacity(0.46))
                }
                Spacer()
                Text("查看规则")
                    .font(.system(size: 12, weight: .bold))
                    .foregroundColor(.white.opacity(0.72))
            }
            .foregroundColor(.white)
            .padding(15)
            .background(Color.white.opacity(0.055), in: RoundedRectangle(cornerRadius: 18))
        }
        .buttonStyle(.plain)
    }

    private func redeemShop(_ series: GachaSeriesInfo) -> some View {
        let shards = model.shardsBySeries[series.id] ?? 0
        let redeemables = model.prizes.filter {
            $0.seriesId == series.id
                && !model.owned.contains($0.id)
                && $0.rarity.redeemCost != nil
        }

        return VStack(alignment: .leading, spacing: 11) {
            HStack {
                Text("兑换")
                    .font(.system(size: 18, weight: .bold))
                Spacer()
                Text("合金屑 \(shards)")
                    .font(.system(size: 11, weight: .semibold, design: .monospaced))
                    .foregroundColor(.white.opacity(0.46))
            }
            .foregroundColor(.white)

            if redeemables.isEmpty {
                Text("本系列暂无可兑换项目")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.42))
            } else {
                ForEach(redeemables.prefix(4)) { prize in
                    redeemRow(prize, shards: shards)
                }
            }
        }
        .padding(15)
        .background(Color.white.opacity(0.045), in: RoundedRectangle(cornerRadius: 18))
    }

    private func redeemRow(_ prize: GachaPrizeInfo, shards: Int) -> some View {
        let cost = prize.rarity.redeemCost ?? Int.max
        return HStack(spacing: 10) {
            Capsule()
                .fill(prize.rarity.shippingTint)
                .frame(width: 3, height: 28)
            VStack(alignment: .leading, spacing: 2) {
                Text(prize.name)
                    .font(.system(size: 13, weight: .semibold))
                Text("\(prize.rarity.title) · \(prize.kindTitle)")
                    .font(.system(size: 10, weight: .medium))
                    .foregroundColor(.white.opacity(0.40))
            }
            Spacer()
            Button("\(cost)") {
                model.redeem(prizeId: prize.id)
            }
            .font(.system(size: 12, weight: .bold, design: .monospaced))
            .foregroundColor(shards >= cost ? .black : .white.opacity(0.28))
            .padding(.horizontal, 12)
            .frame(height: 32)
            .background(
                shards >= cost ? Color.white : Color.white.opacity(0.06),
                in: Capsule())
            .disabled(shards < cost)
        }
        .foregroundColor(.white)
    }

    private var collection: some View {
        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 12) {
                if let series = activeSeries {
                    Text("收藏 \(model.prizes.filter { model.owned.contains($0.id) }.count) / \(model.prizes.count)")
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(.white)

                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        ForEach(model.prizes.filter { $0.seriesId == series.id }) { prize in
                            collectionCard(prize)
                        }
                    }
                }
            }
            .padding(.horizontal, 18)
            .padding(.top, 8)
            .padding(.bottom, 30)
        }
    }

    private func collectionCard(_ prize: GachaPrizeInfo) -> some View {
        let owned = model.owned.contains(prize.id)
        return VStack(alignment: .leading, spacing: 8) {
            HStack {
                Capsule()
                    .fill(prize.rarity.shippingTint)
                    .frame(width: 22, height: 3)
                Spacer()
                Text(owned ? "已拥有" : "未获得")
                    .font(.system(size: 9, weight: .bold))
                    .foregroundColor(.white.opacity(owned ? 0.68 : 0.28))
            }
            Text(prize.name)
                .font(.system(size: 14, weight: .bold))
                .foregroundColor(owned ? .white : .white.opacity(0.42))
            Text("\(prize.rarity.title) · \(prize.kindTitle)")
                .font(.system(size: 10, weight: .medium))
                .foregroundColor(.white.opacity(0.38))
        }
        .frame(maxWidth: .infinity, minHeight: 92, alignment: .topLeading)
        .padding(13)
        .background(Color.white.opacity(owned ? 0.065 : 0.028), in: RoundedRectangle(cornerRadius: 17))
        .overlay {
            RoundedRectangle(cornerRadius: 17)
                .stroke(Color.white.opacity(owned ? 0.08 : 0.04), lineWidth: 0.7)
        }
    }

    private func drawDock(_ series: GachaSeriesInfo) -> some View {
        VStack(spacing: FidgetUITokens.Spacing.metadata) {
            HStack(alignment: .center, spacing: FidgetUITokens.Spacing.standard) {
                VStack(alignment: .leading, spacing: FidgetUITokens.Spacing.compact) {
                    Text(model.drawCostText)
                        .font(.product(.caption, weight: .semibold))
                        .foregroundColor(.white.opacity(FidgetUITokens.Opacity.secondaryText))
                }
                Spacer(minLength: FidgetUITokens.Spacing.standard)
                ProductStatusTag(title: "十抽后续开放")
            }

            ProductPrimaryActionButton(
                title: "单抽",
                state: model.canStartSingleDraw ? .rest : .disabled) {
                guard model.canStartSingleDraw else { return }
                carouselSelectedTier = .standard
                carouselSeries = series
                gachaSequenceLog(
                    "[GachaSequence] carousel-open seriesId=\(series.id)")
            }
            .accessibilityIdentifier("gacha-single-draw")
            .accessibilityHint("消耗一张抽取券")
        }
        .padding(.horizontal, FidgetUITokens.Spacing.pageInset)
        .padding(.top, FidgetUITokens.Spacing.metadata)
        .padding(.bottom, 12)
        .background(.ultraThinMaterial)
    }

    @ViewBuilder
    private var transactionStatus: some View {
        let failure = model.visibleFailureReason
        if !failure.isEmpty || model.requestStatus != "idle" {
            HStack(spacing: 10) {
                VStack(alignment: .leading, spacing: 2) {
                    if !failure.isEmpty {
                        Text(failure)
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.orange.opacity(0.92))
                            .accessibilityIdentifier("gacha-error")
                    }
                    Text(model.requestStatus)
                        .font(.system(size: 8, weight: .medium, design: .monospaced))
                        .foregroundColor(.white.opacity(0.36))
                        .lineLimit(1)
                        .accessibilityIdentifier("gacha-request-status")
                }
                Spacer(minLength: 8)
                if !model.activeRequestId.isEmpty {
                    Button("查询原交易") {
                        model.queryActiveTransaction()
                    }
                    .font(.system(size: 11, weight: .bold))
                    .foregroundColor(.white.opacity(0.82))
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("gacha-query-transaction")
                }
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 8)
            .background(Color.black.opacity(0.88))
        }
    }

    private var probabilityDisclosure: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Text("概率与保底")
                            .font(.system(size: 23, weight: .black, design: .rounded))
                        Spacer()
                        Button("完成") { showDisclosure = false }
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(.white.opacity(0.82))
                    }
                    .foregroundColor(.white)

                    if let series = activeSeries {
                        ForEach(GachaRarityTier.allCases, id: \.rawValue) { tier in
                            HStack {
                                Capsule().fill(tier.shippingTint).frame(width: 24, height: 3)
                                Text(tier.title).foregroundColor(.white)
                                Spacer()
                                Text(String(
                                    format: "%.2f%%",
                                    (series.rates.indices.contains(tier.rawValue)
                                        ? series.rates[tier.rawValue]
                                        : 0) * 100))
                                    .font(.system(size: 14, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.72))
                            }
                        }

                        let signature = model.signatureMisses[series.id] ?? 0
                        let heirloom = model.heirloomMisses[series.id] ?? 0
                        disclosureProgress("臻藏保底", current: signature, target: 51)
                        disclosureProgress("传世保底", current: heirloom, target: 90)
                    }

                    Divider().background(Color.white.opacity(0.12))
                    Group {
                        Text("十抽功能当前未开放。")
                        Text("连续 40 抽未出臻藏后，臻藏概率逐抽提升；第 51 抽必得臻藏或更高。")
                        Text("累计 90 抽内必得传世。")
                        Text("重复奖品转换为合金屑，可用于兑换指定奖品。")
                        Text("全部奖品只影响外观与收藏，不改变物理手感和成长速度。")
                    }
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.58))
                    .lineSpacing(4)
                }
                .padding(22)
            }
        }
        .interactiveDismissDisabled(true)
    }

    private func disclosureProgress(_ title: String, current: Int, target: Int) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(title)
                Spacer()
                Text("\(current) / \(target)")
                    .font(.system(size: 12, weight: .semibold, design: .monospaced))
            }
            .font(.system(size: 13, weight: .bold))
            .foregroundColor(.white)
            ProgressView(value: Double(min(current, target)), total: Double(target))
                .tint(.white.opacity(0.72))
        }
        .padding(14)
        .background(Color.white.opacity(0.05), in: RoundedRectangle(cornerRadius: 16))
    }

}

/// Presentation-only Pack tier picker shown before the authoritative draw is
/// requested. Selecting/scrubbing tiers here never touches `GachaStoreModel`
/// or Unity; only confirming a tier hands control back to the caller, which
/// fires the real (already-tested, idempotent) `model.draw(...)` call.
private struct GachaPackTierCarouselOverlay: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Binding var selectedTier: GachaPackTier
    let onCancel: () -> Void
    let onConfirm: () -> Void

    @State private var carouselDrag: CGFloat = 0

    var body: some View {
        GeometryReader { proxy in
            ZStack {
                Color.black.opacity(0.985).ignoresSafeArea()

                VStack(spacing: 0) {
                    VStack(spacing: 7) {
                        Text("选择 PACK")
                            .font(.product(size: 24, weight: .black))
                            .foregroundColor(.white)
                        Text("包装样式，不改变奖池、价格或概率")
                            .font(.product(size: 11, weight: .medium))
                            .foregroundColor(.white.opacity(0.48))
                    }
                    .padding(.top, 42)

                    tierStage

                    HStack(spacing: 12) {
                        ProductSecondaryActionButton(title: "取消", action: onCancel)
                            .frame(width: 84)
                        ProductPrimaryActionButton(
                            title: "选择 \(selectedTier.title)",
                            action: onConfirm)
                            .frame(maxWidth: min(240, proxy.size.width - 130))
                            .accessibilityIdentifier("gacha-pack-select")
                    }
                    .padding(.horizontal, 22)
                    .padding(.bottom, 28)
                }
            }
        }
    }

    private var tierStage: some View {
        let tiers = GachaPackTier.allCases
        let selectedIndex = tiers.firstIndex(of: selectedTier) ?? 0

        return ZStack {
            ForEach(Array(tiers.enumerated()), id: \.element.rawValue) {
                index, tier in
                let position = GachaPackCarouselRules.continuousPosition(
                    itemIndex: index,
                    selectedIndex: selectedIndex,
                    translationPoints: Double(carouselDrag))
                let x = GachaPackCarouselRules.horizontalOffset(
                    continuousPosition: position)
                let y = GachaPackCarouselRules.verticalOffset(
                    continuousPosition: position)
                let tilt = GachaPackCarouselRules.tiltDegrees(
                    continuousPosition: position)
                Button {
                    withAnimation(.spring(
                        response: GachaPackCarouselRules
                            .selectionSnapResponseSeconds,
                        dampingFraction: GachaPackCarouselRules
                            .selectionSnapDampingFraction)) {
                        carouselDrag = 0
                        selectedTier = tier
                    }
                } label: {
                    VStack(spacing: 2) {
                        GachaPackVisual(tier: tier, tearProgress: 0)
                            .frame(width: 244, height: 326)
                            .scaleEffect(CGFloat(
                                GachaPackCarouselRules.packScale(
                                    isSelected: index == selectedIndex)))
                            .frame(width: 166, height: 226)
                        Text(tier.title)
                            .font(.product(size: 10, weight: .bold))
                            .foregroundColor(.white.opacity(
                                index == selectedIndex ? 0.92 : 0.42))
                    }
                }
                .buttonStyle(.plain)
                .offset(x: CGFloat(x), y: CGFloat(y))
                .rotationEffect(.degrees(tilt), anchor: .bottom)
                .opacity(abs(position) > 2.6 ? 0 : 1)
                .zIndex(3 - abs(position))
                .accessibilityLabel("\(tier.title) Pack")
                .accessibilityAddTraits(index == selectedIndex ? .isSelected : [])
                .accessibilityIdentifier("gacha-pack-tier-\(tier.rawValue)")
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .clipped()
        .contentShape(Rectangle())
        .gesture(
            DragGesture(minimumDistance: 12)
                .onChanged { value in
                    carouselDrag = value.translation.width
                }
                .onEnded { value in
                    let next = GachaPackCarouselRules.nextIndex(
                        selectedIndex: selectedIndex,
                        itemCount: tiers.count,
                        translationPoints: Double(value.translation.width))
                    withAnimation(.spring(
                        response: GachaPackCarouselRules
                            .selectionSnapResponseSeconds,
                        dampingFraction: GachaPackCarouselRules
                            .selectionSnapDampingFraction)) {
                        carouselDrag = 0
                        selectedTier = tiers[next]
                    }
                })
    }
}

private struct GachaPackOpeningOverlay: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @ObservedObject var model: GachaStoreModel
    let transaction: GachaPendingTransaction
    // The tier the user actually picked in the carousel. Presentation only —
    // the transaction/economy remain unaware of it. Falls back to the old
    // series-derived default for any caller that predates the carousel.
    var tier: GachaPackTier?

    @State private var tearProgress: CGFloat = 0
    @State private var interactionState = "sealed"
    @State private var packOpenCommitted = false
    @State private var holderRevealStarted = false
    @State private var holderCompletionDispatched = false
    @State private var packVisible = true
    @State private var overlapStartedUptime: TimeInterval?
    // This build shows the real prize directly in the magnetic holder and
    // accepts it there; the Unity 3D PremiumDisplayCase handoff is
    // intentionally bypassed (see MarkGachaHolderRevealedFromNativeUi).
    @State private var holderRevealAcceptReady = false

    private static let invalidRequestFallback = UUID(
        uuidString: "00000000-0000-0000-0000-000000000000")!

    private var packTier: GachaPackTier {
        tier ?? GachaPackTier.forSeriesId(transaction.seriesId)
    }

    private var riveTransactionID: UUID {
        UUID(uuidString: transaction.requestId)
            ?? Self.invalidRequestFallback
    }

    private var packToHolderAnimation: Animation {
        .easeOut(duration: GachaSingleDrawGateState
            .packToHolderTransitionSeconds)
    }

    var body: some View {
        ZStack {
            Color.black.opacity(0.985).ignoresSafeArea()

            GachaSingleDrawRiveGate(
                transactionID: riveTransactionID,
                stage: .magneticHolder,
                playbackEnabled: holderRevealStarted,
                revealedPrize: transaction.receipt.first) { id, reason in
                    guard id == riveTransactionID else { return }
                    holderRiveFinished(reason: reason)
                }
                .opacity(holderRevealStarted ? 1 : 0)
                .animation(packToHolderAnimation, value: holderRevealStarted)
                .accessibilityHidden(!holderRevealStarted)
                .zIndex(1)

            packSurface
                .opacity(packVisible ? 1 : 0)
                .animation(packToHolderAnimation, value: packVisible)
                .allowsHitTesting(packVisible && !packOpenCommitted)
                .accessibilityHidden(!packVisible)
                .zIndex(2)

            if holderRevealAcceptReady {
                VStack {
                    Spacer()
                    ProductPrimaryActionButton(
                        title: "收下",
                        state: model.transactionPhase == .acknowledging
                            ? .loading("提交中") : .rest,
                        action: acceptHolderReveal)
                        .frame(width: 214)
                        .padding(.bottom, 48)
                        .accessibilityIdentifier("gacha-reveal-accept")
                }
                .transition(.opacity)
                .zIndex(4)
            }

            accessibilityMarkers
                .zIndex(3)
        }
        .animation(.easeOut(duration: 0.22), value: holderRevealAcceptReady)
        .accessibilityElement(children: .contain)
        .onAppear {
            GachaPackInteractionTrace.begin(requestId: transaction.requestId)
        }
    }

    private var packSurface: some View {
        VStack(spacing: 20) {
            Text("单抽封包")
                .font(.system(size: 11, weight: .bold, design: .monospaced))
                .foregroundColor(.white.opacity(0.52))
                .tracking(1.2)

            GachaPackVisual(tier: packTier, tearProgress: tearProgress)
                .frame(width: 244, height: 326)
                .contentShape(Rectangle())
                .gesture(tearGesture)
                .accessibilityLabel("\(packTier.title) 抽取包装")
                .accessibilityHint("沿顶部封边向右滑动，超过百分之六十二后松开")
                .accessibilityValue(
                    "\(interactionState), \(Int((tearProgress * 100).rounded())) percent")
                .accessibilityIdentifier("gacha-pack-tear-target")

            VStack(spacing: 6) {
                Text(packOpenCommitted ? "正在进入磁吸收藏夹" : "沿顶部封边向右撕开")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.white.opacity(0.62))

                Text("释放阈值 62%")
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.34))
            }

            if !model.visibleFailureReason.isEmpty {
                Text(model.visibleFailureReason)
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(.orange)
                    .multilineTextAlignment(.center)
                    .accessibilityIdentifier("gacha-error")

                Button("查询原交易") {
                    model.queryActiveTransaction()
                }
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(.white)
                .accessibilityIdentifier("gacha-query-transaction")
            } else {
                ProductPrimaryActionButton(
                    title: "撕开包装",
                    state: packOpenCommitted ? .loading("正在打开") : .rest) {
                    commitPackOpen(source: "accessible-button")
                }
                .frame(width: 214)
                .accessibilityIdentifier("gacha-pack-open")
            }
        }
        .padding(.horizontal, 24)
        .padding(.vertical, 30)
    }

    private var tearGesture: some Gesture {
        DragGesture(minimumDistance: 6, coordinateSpace: .local)
            .onChanged { value in
                guard !packOpenCommitted else { return }
                tearProgress = CGFloat(
                    GachaPackOpeningRules.normalizedProgress(
                        translationPoints: Double(value.translation.width)))
                interactionState = tearProgress > 0 ? "dragging" : "sealed"
            }
            .onEnded { _ in
                guard !packOpenCommitted else { return }
                let releasedProgress = tearProgress
                if GachaPackOpeningRules.shouldCommit(
                    progress: Double(releasedProgress)) {
                    GachaPackInteractionTrace.record(
                        requestId: transaction.requestId,
                        event: "release-commit",
                        progress: releasedProgress)
                    commitPackOpen(source: "threshold")
                } else {
                    interactionState = "rebounding"
                    GachaPackInteractionTrace.record(
                        requestId: transaction.requestId,
                        event: "release-rebound",
                        progress: releasedProgress)
                    withAnimation(.easeOut(duration: reduceMotion ? 0.01 : 0.18)) {
                        tearProgress = 0
                    }
                    DispatchQueue.main.asyncAfter(
                        deadline: .now() + (reduceMotion ? 0.02 : 0.20)) {
                        guard !packOpenCommitted else { return }
                        interactionState = "sealed"
                        GachaPackInteractionTrace.record(
                            requestId: transaction.requestId,
                            event: "rebound-complete",
                            progress: 0)
                    }
                }
            }
    }

    private var accessibilityMarkers: some View {
        VStack(spacing: 0) {
            marker(
                label: "封包入口",
                identifier: "gacha-pack-entry",
                value: "ready")
            marker(
                label: "封包状态",
                identifier: "gacha-pack-state",
                value: interactionState)
            marker(
                label: "封包撕开进度",
                identifier: "gacha-pack-progress",
                value: String(format: "%.3f", Double(tearProgress)))
            marker(
                label: "封包交易请求",
                identifier: "gacha-pack-request-id",
                value: transaction.requestId)
            marker(
                label: "封包到收藏夹连续转场",
                identifier: "gacha-pack-holder-transition",
                value: interactionState)
            marker(
                label: "磁吸收藏夹播放状态",
                identifier: "gacha-holder-playback-state",
                value: holderRevealStarted
                    ? (holderCompletionDispatched ? "completed" : "playing")
                    : "waiting")
        }
        .frame(width: 1, height: 1)
        .clipped()
    }

    private func marker(
        label: String,
        identifier: String,
        value: String
    ) -> some View {
        Text(label)
            .foregroundColor(.clear)
            .frame(width: 1, height: 1)
            .accessibilityIdentifier(identifier)
            .accessibilityValue(value)
    }

    @MainActor
    private func commitPackOpen(source: String) {
        guard !packOpenCommitted else { return }
        packOpenCommitted = true
        interactionState = "pack-holder-overlap"
        overlapStartedUptime = ProcessInfo.processInfo.systemUptime
        GachaPackInteractionTrace.record(
            requestId: transaction.requestId,
            event: "commit-start-\(source)",
            progress: tearProgress)
        gachaSequenceLog(
            "[GachaSequence] pack-holder-overlap-start request=\(transaction.requestId) reduceMotion=\(reduceMotion)")

        withAnimation(.easeOut(duration: reduceMotion
            ? 0.01
            : GachaPackOpeningRules.flapExitDurationSeconds)) {
            tearProgress = 1
        }

        if reduceMotion {
            var nativeTransition = Transaction()
            nativeTransition.disablesAnimations = true
            withTransaction(nativeTransition) {
                holderRevealStarted = true
            }
        } else {
            withAnimation(packToHolderAnimation) {
                holderRevealStarted = true
                packVisible = false
            }
        }

        Task { @MainActor in
            do {
                try await Task.sleep(
                    nanoseconds: UInt64(
                        GachaSingleDrawGateState
                            .packToHolderTransitionSeconds * 1_000_000_000))
            } catch {
                return
            }
            guard !Task.isCancelled,
                  model.packIsPresented,
                  model.pendingTransaction?.requestId == transaction.requestId
            else { return }
            if reduceMotion {
                var nativeTransition = Transaction()
                nativeTransition.disablesAnimations = true
                withTransaction(nativeTransition) {
                    packVisible = false
                }
            }
            interactionState = holderCompletionDispatched
                ? "holder-completed"
                : "holder-playing"
            gachaSequenceLog(
                "[GachaSequence] pack-holder-overlap-complete request=\(transaction.requestId)")
        }
    }

    @MainActor
    private func holderRiveFinished(reason: GachaRiveCompletionReason) {
        guard packOpenCommitted,
              holderRevealStarted,
              !holderCompletionDispatched
        else { return }

        holderCompletionDispatched = true
        let now = ProcessInfo.processInfo.systemUptime
        let elapsed = max(0, now - (overlapStartedUptime ?? now))
        let remaining = max(
            0,
            GachaSingleDrawGateState.packToHolderTransitionSeconds - elapsed)

        Task { @MainActor in
            if remaining > 0 {
                do {
                    try await Task.sleep(
                        nanoseconds: UInt64(remaining * 1_000_000_000))
                } catch {
                    return
                }
            }
            guard !Task.isCancelled,
                  model.packIsPresented,
                  model.pendingTransaction?.requestId == transaction.requestId
            else { return }

            interactionState = "holder-revealed"
            gachaSequenceLog(
                "[GachaSequence] holder-rive-completed request=\(transaction.requestId) reason=\(reason.rawValue)")
            gachaSequenceLog(
                "[GachaSequence] holder-reveal-accept-ready request=\(transaction.requestId)")
            GachaPackInteractionTrace.record(
                requestId: transaction.requestId,
                event: "holder-rive-complete-\(reason.rawValue)",
                progress: 1)
            GachaPackInteractionTrace.record(
                requestId: transaction.requestId,
                event: "holder-reveal-accept-ready",
                progress: 1)
            model.markHolderRevealed(requestId: transaction.requestId)
            holderRevealAcceptReady = true
        }
    }

    private func acceptHolderReveal() {
        model.acknowledgeHolderReveal(requestId: transaction.requestId)
    }
}

private enum GachaPackInteractionTrace {
    private static let defaultsKey = "gacha.pack.build42.trace.v1"

    static func begin(requestId: String) {
#if DEBUG
        guard ProcessInfo.processInfo.arguments.contains("--gacha-pack-trace") else {
            return
        }
        UserDefaults.standard.set([], forKey: defaultsKey)
        record(requestId: requestId, event: "sealed", progress: 0)
#endif
    }

    static func record(requestId: String, event: String, progress: CGFloat) {
#if DEBUG
        guard ProcessInfo.processInfo.arguments.contains("--gacha-pack-trace") else {
            return
        }
        let normalized = Double(min(max(progress, 0), 1))
        var events = UserDefaults.standard.array(forKey: defaultsKey)
            as? [[String: Any]] ?? []
        events.append([
            "requestId": requestId,
            "event": event,
            "progress": normalized,
            "threshold": GachaPackOpeningRules.tearCommitProgress,
            "uptime": ProcessInfo.processInfo.systemUptime
        ])
        UserDefaults.standard.set(events, forKey: defaultsKey)
        UserDefaults.standard.synchronize()
        print(String(
            format: "[GachaPackTrace] %@ %@ progress=%.4f threshold=%.4f",
            requestId,
            event,
            normalized,
            GachaPackOpeningRules.tearCommitProgress))
#endif
    }
}

private struct GachaThreeDRevealOverlay: View {
    @ObservedObject var model: GachaStoreModel
    let transaction: GachaPendingTransaction

    private var receipt: GachaReceiptRow? {
        transaction.receipt.first
    }

    private var phaseCaption: String {
        model.revealPhase?.caption ?? "正在装载真实 3D 收藏盒"
    }

    var body: some View {
        ZStack {
            Color.clear.ignoresSafeArea()

            Text("3d-reveal-root")
                .foregroundColor(.clear)
                .frame(width: 1, height: 1)
                .clipped()
                .accessibilityLabel("真实 3D 揭晓场景")
                .accessibilityIdentifier("gacha-3d-reveal-root")

            VStack(spacing: 0) {
                Text("真实 3D 揭晓")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(.white.opacity(0.62))
                    .padding(.horizontal, 11)
                    .frame(height: 28)
                    .background(Color.black.opacity(0.52), in: Capsule())
                    .padding(.top, 18)

                Spacer()

                VStack(spacing: 8) {
                    if let receipt,
                       model.revealPhase == .readable
                            || model.revealPhase == .exploded
                            || model.revealPhase == .prizeOnly
                            || model.revealPhase == .sheen
                            || model.revealPhase == .complete {
                        Text(receipt.name)
                            .font(.system(size: 22, weight: .black, design: .rounded))
                            .foregroundColor(.white)
                        Text("\(receipt.rarity.title) · \(receipt.isNew ? "NEW" : "+\(receipt.shardsGained) 合金屑")")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.white.opacity(0.66))
                    }

                    Text(phaseCaption)
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.white.opacity(0.72))
                        .accessibilityIdentifier("gacha-reveal-phase")
                        .accessibilityValue(model.revealPhase?.rawValue ?? "preparing")

                    if !model.visibleFailureReason.isEmpty {
                        Text(model.visibleFailureReason)
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.orange)
                            .multilineTextAlignment(.center)
                            .accessibilityIdentifier("gacha-error")

                        Button("查询原交易") {
                            model.queryActiveTransaction()
                        }
                        .font(.system(size: 12, weight: .bold))
                        .foregroundColor(.white)
                        .accessibilityIdentifier("gacha-query-transaction")
                    }

                    if model.revealPhase == .complete,
                       transaction.phase == .awaitingAcceptance {
                        ProductPrimaryActionButton(
                            title: "收下",
                            state: model.transactionPhase == .acknowledging
                                ? .loading("提交中") : .rest) {
                            model.acknowledgeReveal()
                        }
                        .frame(width: 214)
                        .accessibilityIdentifier("gacha-reveal-accept")
                    }
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 18)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 24))
                .padding(.horizontal, 18)
                .padding(.bottom, 18)
            }
        }
        .accessibilityElement(children: .contain)
        .onAppear {
            model.startRevealIfNeeded(requestId: transaction.requestId)
        }
    }
}

private struct GachaAccessibilityStateMarkers: View {
    @ObservedObject var model: GachaStoreModel
    let seriesId: String

    private var requestId: String {
        model.pendingTransaction?.requestId ?? model.activeRequestId
    }

    private var prizeId: String {
        model.pendingTransaction?.receipt.first?.prizeId ?? ""
    }

    private var drawCount: Int {
        model.totalDraws[seriesId] ?? 0
    }

    private var revealPhaseHistory: String {
        model.revealPhaseHistory
            .map(\.rawValue)
            .joined(separator: "|")
    }

    var body: some View {
        VStack(spacing: 0) {
            marker(
                label: "抽卡商店根节点",
                identifier: "gacha-store-root",
                value: "ready")
            marker(
                label: "抽卡余额",
                identifier: "gacha-ticket-balance",
                value: model.ticketBalanceText)
            marker(
                label: "当前抽取请求",
                identifier: "gacha-active-request-id",
                value: requestId)
            marker(
                label: "待确认奖品",
                identifier: "gacha-pending-prize-id",
                value: prizeId)
            marker(
                label: "揭晓阶段历史",
                identifier: "gacha-reveal-phase-history",
                value: revealPhaseHistory)
            marker(
                label: "已收藏数量",
                identifier: "gacha-owned-count",
                value: String(model.owned.count))
            marker(
                label: "系列累计抽数",
                identifier: "gacha-total-draws",
                value: String(drawCount))
        }
        .frame(width: 1, height: 1)
        .clipped()
    }

    private func marker(
        label: String,
        identifier: String,
        value: String
    ) -> some View {
        Text(label)
            .foregroundColor(.clear)
            .frame(width: 1, height: 1)
            .accessibilityIdentifier(identifier)
            .accessibilityValue(value)
    }
}

private struct GachaTransparentPresentationBackground: UIViewRepresentable {
    func makeUIView(context: Context) -> UIView {
        let view = GachaTransparentPresentationView()
        view.isUserInteractionEnabled = false
        return view
    }

    func updateUIView(_ uiView: UIView, context: Context) {
        (uiView as? GachaTransparentPresentationView)?.clearPresentationBackgrounds()
    }
}

private final class GachaTransparentPresentationView: UIView {
    override func didMoveToWindow() {
        super.didMoveToWindow()
        clearPresentationBackgrounds()
    }

    func clearPresentationBackgrounds() {
        var ancestor = superview
        while let view = ancestor, !(view is UIWindow) {
            view.backgroundColor = .clear
            view.isOpaque = false
            ancestor = view.superview
        }
    }
}

private struct GachaPackVisual: View {
    let tier: GachaPackTier
    let tearProgress: CGFloat

    private var progress: CGFloat {
        min(max(tearProgress, 0), 1)
    }

    var body: some View {
        ZStack {
            GachaBundleArtwork(name: tier.bodyAssetName)
                .scaledToFit()
                .accessibilityHidden(true)

            GachaBundleArtwork(name: tier.flapAssetName)
                .scaledToFit()
                .offset(x: progress * 132, y: progress * -34)
                .rotationEffect(.degrees(Double(progress) * 7), anchor: .topTrailing)
                .opacity(1 - Double(progress) * 0.12)
                .accessibilityHidden(true)
        }
        .aspectRatio(384.0 / 512.0, contentMode: .fit)
        .shadow(color: .black.opacity(0.52), radius: 18, y: 11)
    }
}

private struct GachaBundleArtwork: View {
    let name: String

    var body: some View {
        Group {
            if let url = Bundle.main.url(forResource: name, withExtension: "png"),
               let image = UIImage(contentsOfFile: url.path) {
                Image(uiImage: image).resizable()
            } else {
                Color(white: 0.05)
            }
        }
    }
}

private extension GachaRarityTier {
    var shippingTint: Color {
        switch self {
        case .standard: return Color(red: 0.20, green: 0.60, blue: 1.00)
        case .refined: return Color(red: 0.20, green: 0.88, blue: 0.58)
        case .signature: return Color(red: 0.64, green: 0.36, blue: 1.00)
        case .heirloom: return Color(red: 1.00, green: 0.64, blue: 0.16)
        }
    }
}
