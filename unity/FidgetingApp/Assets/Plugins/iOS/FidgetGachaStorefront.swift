import SwiftUI
import UIKit

#if LEGACY_GACHA_PRESENTATION
// Shipping storefront presentation. Economy, ownership, pity and receipts stay
// owned by GachaStoreModel/Unity; this file only replaces the native layout and
// the single-result reveal presentation.
public struct LegacyGachaStorefrontView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject private var model = GachaStoreModel.shared
    @State private var selectedTab = 0
    @State private var showDisclosure = false
    @State private var showMultiResults = false
    @State private var singleReveal: GachaReceiptRow?
    @State private var drawRequestInFlight = false

    public init() {}

    private var activeSeries: GachaSeriesInfo? { model.series.first }

    public var body: some View {
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
                drawDock(series)
            }

            if let receipt = singleReveal {
                GachaSingleDrawReveal(receipt: receipt) {
                    model.pendingReceipt = []
                    singleReveal = nil
                }
                .transition(.opacity)
                .zIndex(20)
            }
        }
        .preferredColorScheme(.dark)
        .interactiveDismissDisabled(
            drawRequestInFlight || singleReveal != nil || showMultiResults)
        .onAppear { model.requestState() }
        .onChange(of: model.pendingReceipt) { rows in
            guard !rows.isEmpty else { return }
            drawRequestInFlight = false
            if rows.count == 1 {
                singleReveal = rows[0]
            } else {
                showMultiResults = true
            }
        }
        .onChange(of: model.lastFailureReason) { reason in
            if !reason.isEmpty {
                drawRequestInFlight = false
            }
        }
        .onDisappear {
            guard !drawRequestInFlight else { return }
            model.pendingReceipt = []
            model.lastFailureReason = ""
        }
        .sheet(isPresented: $showDisclosure) {
            probabilityDisclosure
        }
        .sheet(isPresented: $showMultiResults) {
            multiResultSheet
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
            .disabled(drawRequestInFlight)
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
            }

            Spacer(minLength: 8)
            walletChip(symbol: "ticket.fill", value: model.tickets, title: "抽取券")
            walletChip(symbol: "gearshape.2.fill", value: model.coins, title: "齿轮币")
        }
        .padding(.horizontal, 18)
        .padding(.vertical, 12)
    }

    private func walletChip(symbol: String, value: Int, title: String) -> some View {
        HStack(spacing: 6) {
            Image(systemName: symbol)
                .font(.system(size: 12, weight: .semibold))
            VStack(alignment: .leading, spacing: 0) {
                Text("\(value)")
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
                guard !drawRequestInFlight else { return }
                drawRequestInFlight = true
                model.pendingReceipt = []
                model.lastFailureReason = ""
                model.draw(seriesId: series.id, count: 1, useCoins: false)
            } label: {
                VStack(spacing: 3) {
                    Text("单抽")
                        .font(.system(size: 17, weight: .bold))
                    Text("消耗 1 张抽取券")
                        .font(.system(size: 10, weight: .medium))
                        .opacity(0.58)
                }
                .foregroundColor(.black)
                .frame(maxWidth: .infinity)
                .frame(height: 62)
                .background(Color.white, in: RoundedRectangle(cornerRadius: 19))
            }
            .buttonStyle(.plain)
            .disabled(model.tickets < 1 || drawRequestInFlight)
            .opacity(model.tickets < 1 || drawRequestInFlight ? 0.36 : 1)
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

    private var multiResultSheet: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            VStack(spacing: 14) {
                Text("揭晓结果")
                    .font(.system(size: 23, weight: .black, design: .rounded))
                    .foregroundColor(.white)
                    .padding(.top, 20)
                ScrollView {
                    VStack(spacing: 9) {
                        ForEach(model.pendingReceipt) { row in
                            resultRow(row)
                        }
                    }
                    .padding(.horizontal, 18)
                }
                Button("收入囊中") {
                    model.pendingReceipt = []
                    showMultiResults = false
                }
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.black)
                .frame(maxWidth: .infinity)
                .frame(height: 56)
                .background(Color.white, in: RoundedRectangle(cornerRadius: 18))
                .padding(18)
            }
        }
        .interactiveDismissDisabled(true)
    }

    private func resultRow(_ row: GachaReceiptRow) -> some View {
        HStack(spacing: 10) {
            Capsule().fill(row.rarity.shippingTint).frame(width: 3, height: 34)
            VStack(alignment: .leading, spacing: 2) {
                Text(row.name).font(.system(size: 14, weight: .bold))
                Text(row.rarity.title)
                    .font(.system(size: 10, weight: .medium))
                    .foregroundColor(.white.opacity(0.44))
            }
            Spacer()
            Text(row.isNew ? "NEW" : "+\(row.shardsGained)")
                .font(.system(size: 11, weight: .bold, design: .monospaced))
                .foregroundColor(.white.opacity(0.68))
        }
        .foregroundColor(.white)
        .padding(13)
        .background(Color.white.opacity(0.055), in: RoundedRectangle(cornerRadius: 16))
    }
}

private enum GachaRevealPhase: Int {
    case back
    case front
    case readable
    case exploded
    case prizeOnly
    case sheen
    case complete
}

private struct GachaSingleDrawReveal: View {
    let receipt: GachaReceiptRow
    let completion: () -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var phase: GachaRevealPhase = .back
    @State private var sheenOffset: CGFloat = -260

    var body: some View {
        ZStack {
            Color.black.opacity(0.975).ignoresSafeArea()

            VStack(spacing: 24) {
                Text("单抽揭晓")
                    .font(.system(size: 12, weight: .bold))
                    .foregroundColor(.white.opacity(0.55))

                GachaCaseRevealVisual(
                    phase: phase,
                    rarity: receipt.rarity,
                    title: receipt.name,
                    sheenOffset: sheenOffset)
                    .frame(width: 290, height: 390)

                VStack(spacing: 7) {
                    Text(receipt.name)
                        .font(.system(size: 24, weight: .black, design: .rounded))
                        .foregroundColor(.white)
                    HStack(spacing: 7) {
                        Capsule()
                            .fill(receipt.rarity.shippingTint)
                            .frame(width: 24, height: 3)
                        Text(receipt.rarity.title)
                        Text(receipt.isNew ? "NEW" : "+\(receipt.shardsGained) 合金屑")
                    }
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(.white.opacity(0.52))
                }
                .opacity(phase.rawValue >= GachaRevealPhase.readable.rawValue ? 1 : 0)

                if phase == .complete {
                    Button("收下") { completion() }
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.black)
                        .frame(width: 214, height: 54)
                        .background(Color.white, in: RoundedRectangle(cornerRadius: 17))
                        .transition(.opacity.combined(with: .scale(scale: 0.96)))
                        .accessibilityIdentifier("gacha-reveal-accept")
                } else {
                    Text(phaseCaption)
                        .font(.system(size: 11, weight: .medium))
                        .foregroundColor(.white.opacity(0.34))
                        .frame(height: 54)
                }
            }
            .padding(.vertical, 32)
        }
        .task { await play() }
    }

    private var phaseCaption: String {
        switch phase {
        case .back: return "收藏盒入场"
        case .front: return "收藏盒翻正"
        case .readable: return "奖品确认"
        case .exploded: return "盒体散开"
        case .prizeOnly: return "奖品保留"
        case .sheen: return "完成过光"
        case .complete: return ""
        }
    }

    @MainActor
    private func setPhase(_ next: GachaRevealPhase, duration: Double) async {
        withAnimation(.easeInOut(duration: duration)) {
            phase = next
        }
    }

    private func pause(_ nanoseconds: UInt64) async -> Bool {
        do {
            try await Task.sleep(nanoseconds: nanoseconds)
            return !Task.isCancelled
        } catch {
            return false
        }
    }

    @MainActor
    private func play() async {
        if reduceMotion {
            phase = .complete
            return
        }
        guard await pause(650_000_000) else { return }
        await setPhase(.front, duration: 0.72)
        guard await pause(800_000_000) else { return }
        await setPhase(.readable, duration: 0.32)
        guard await pause(760_000_000) else { return }
        await setPhase(.exploded, duration: 0.78)
        guard await pause(1_000_000_000) else { return }
        await setPhase(.prizeOnly, duration: 0.38)
        guard await pause(480_000_000) else { return }
        await setPhase(.sheen, duration: 0.22)
        sheenOffset = -260
        withAnimation(.easeInOut(duration: 0.92)) {
            sheenOffset = 260
        }
        guard await pause(980_000_000) else { return }
        await setPhase(.complete, duration: 0.28)
    }
}

private struct GachaCaseRevealVisual: View {
    let phase: GachaRevealPhase
    let rarity: GachaRarityTier
    let title: String
    let sheenOffset: CGFloat

    private var isExploded: Bool {
        phase == .exploded
    }

    private var shellVisible: Bool {
        phase.rawValue < GachaRevealPhase.prizeOnly.rawValue
    }

    var body: some View {
        ZStack {
            ForEach(0..<3, id: \.self) { layer in
                RoundedRectangle(cornerRadius: 30 - CGFloat(layer * 3))
                    .stroke(
                        Color.white.opacity(0.20 - Double(layer) * 0.035),
                        lineWidth: layer == 0 ? 5 : 2)
                    .frame(
                        width: 218 - CGFloat(layer * 18),
                        height: 302 - CGFloat(layer * 22))
                    .offset(explodedOffset(layer))
                    .opacity(shellVisible ? 1 : 0)
            }

            if shellVisible {
                cornerPins
                    .offset(explodedOffset(0))
            }

            rewardCard
                .scaleEffect(
                    phase.rawValue >= GachaRevealPhase.prizeOnly.rawValue
                        ? 1.16
                        : 1)
                .opacity(
                    phase.rawValue >= GachaRevealPhase.readable.rawValue
                        ? 1
                        : 0.12)
        }
        .rotation3DEffect(
            .degrees(phase == .back ? 180 : 0),
            axis: (x: 0, y: 1, z: 0),
            perspective: 0.62)
    }

    private var rewardCard: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .fill(Color(white: 0.075))

            VStack(spacing: 14) {
                Capsule()
                    .fill(rarity.shippingTint)
                    .frame(width: 34, height: 4)

                ZStack {
                    Circle()
                        .fill(Color.white.opacity(0.055))
                        .frame(width: 78, height: 78)
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(Color.white.opacity(0.18), lineWidth: 1.2)
                        .frame(width: 48, height: 48)
                        .rotationEffect(.degrees(45))
                    Circle()
                        .fill(Color.white.opacity(0.82))
                        .frame(width: 10, height: 10)
                }

                Text(title)
                    .font(.system(size: 16, weight: .bold, design: .rounded))
                    .foregroundColor(.white.opacity(0.92))
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                    .frame(width: 142)

                Text("COLLECTED")
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .tracking(1.4)
                    .foregroundColor(.white.opacity(0.30))
            }

            if phase == .sheen || phase == .complete {
                LinearGradient(
                    colors: [.clear, .white.opacity(0.34), .clear],
                    startPoint: .top,
                    endPoint: .bottom)
                    .frame(width: 36, height: 250)
                    .rotationEffect(.degrees(18))
                    .offset(x: sheenOffset)
            }
        }
        .frame(width: 166, height: 224)
        .clipShape(RoundedRectangle(cornerRadius: 26, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .stroke(Color.white.opacity(0.12), lineWidth: 0.8)
        }
        .shadow(color: .black.opacity(0.46), radius: 24, y: 14)
    }

    private var cornerPins: some View {
        ZStack {
            ForEach(0..<4, id: \.self) { index in
                let points = [
                    CGPoint(x: -98, y: -140),
                    CGPoint(x: 98, y: -140),
                    CGPoint(x: -98, y: 140),
                    CGPoint(x: 98, y: 140)
                ]
                let point = points[index]
                Circle()
                    .fill(Color(white: 0.72))
                    .frame(width: 13, height: 13)
                    .overlay { Circle().stroke(Color.white.opacity(0.60), lineWidth: 1) }
                    .offset(x: point.x, y: point.y)
            }
        }
    }

    private func explodedOffset(_ layer: Int) -> CGSize {
        guard isExploded else { return .zero }
        switch layer {
        case 0: return CGSize(width: -44, height: -18)
        case 1: return CGSize(width: 38, height: 18)
        default: return CGSize(width: 0, height: 54)
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
#endif
