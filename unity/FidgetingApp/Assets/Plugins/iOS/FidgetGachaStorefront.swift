import SwiftUI
import UIKit

// Shipping storefront presentation. Economy, ownership, transaction recovery,
// and the 3D reveal timeline stay owned by Unity. SwiftUI only hosts controls and
// a transparent accessibility/HUD surface above Unity's real presentation.
public struct GachaStoreView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject private var model = GachaStoreModel.shared
    @State private var selectedTab = 0
    @State private var showDisclosure = false

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
                .opacity(model.revealIsPresented ? 0 : 1)
                .allowsHitTesting(!model.revealIsPresented)
                .accessibilityHidden(model.revealIsPresented)

            if model.revealIsPresented,
               let transaction = model.pendingTransaction {
                GachaThreeDRevealOverlay(
                    model: model,
                    transaction: transaction)
                .transition(.opacity)
                .zIndex(20)
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
        HStack(spacing: 12) {
            Button {
                guard model.canStartSingleDraw else { return }
                model.draw(seriesId: series.id, count: 1, useCoins: false)
            } label: {
                VStack(spacing: 3) {
                    Text("单抽")
                        .font(.system(size: 17, weight: .bold))
                    Text(model.drawCostText)
                        .font(.system(size: 10, weight: .medium))
                        .opacity(0.58)
                }
                .foregroundColor(.black)
                .frame(maxWidth: .infinity)
                .frame(height: 62)
                .background(Color.white, in: RoundedRectangle(cornerRadius: 19))
            }
            .buttonStyle(.plain)
            .disabled(!model.canStartSingleDraw)
            .opacity(model.canStartSingleDraw ? 1 : 0.36)
            .accessibilityIdentifier("gacha-single-draw")

            VStack(spacing: 3) {
                Text("十抽")
                    .font(.system(size: 17, weight: .bold))
                Text("后续开放")
                    .font(.system(size: 10, weight: .medium))
            }
            .foregroundColor(.white.opacity(0.24))
            .frame(width: 116, height: 62)
            .background(Color.white.opacity(0.045), in: RoundedRectangle(cornerRadius: 19))
        }
        .padding(.horizontal, 18)
        .padding(.top, 13)
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
                        Button("收下") {
                            model.acknowledgeReveal()
                        }
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.black)
                        .frame(width: 214, height: 54)
                        .background(Color.white, in: RoundedRectangle(cornerRadius: 17))
                        .disabled(model.transactionPhase == .acknowledging)
                        .opacity(model.transactionPhase == .acknowledging ? 0.52 : 1)
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
