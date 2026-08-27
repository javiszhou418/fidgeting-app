import SwiftUI
import UIKit

private func gachaSequenceLog(_ message: String) {
#if DEBUG
    NSLog("%@", message)
#endif
}

/// This file has no access to the storefront's own private `UnityBridge`
/// haptics helper (defined file-private in CodexSwiftUIOverlay.swift), so the
/// pack-opening ceremony drives `UIImpactFeedbackGenerator` directly. Kept
/// deliberately dumb: presentation-only, no bearing on draw economy or rarity.
private func gachaHaptic(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
    UIImpactFeedbackGenerator(style: style).impactOccurred()
}

/// Presents the storefront as a frosted-glass sheet with the system grabber
/// instead of an opaque black canvas and a hand-drawn "返回主页" row: swipe or
/// the native drag indicator dismiss it, matching Apple's own sheet chrome.
private struct GachaStorePresentationChrome: ViewModifier {
    let transparent: Bool

    @ViewBuilder
    func body(content: Content) -> some View {
        if #available(iOS 16.4, *) {
            if transparent {
                content
                    .presentationBackground(Color.clear)
                    .presentationDragIndicator(.hidden)
            } else {
                content
                    .presentationBackground(.regularMaterial)
                    .presentationDragIndicator(.visible)
            }
        } else {
            content
        }
    }
}

// Shipping storefront presentation. Economy, ownership, pity and receipts stay
// owned by GachaStoreModel/Unity; this file only replaces the native layout and
// the single-result reveal presentation.
public struct GachaStoreView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject private var model = GachaStoreModel.shared
    @State private var selectedTab = 0
    @State private var showDisclosure = false
    @State private var showMultiResults = false
    @State private var drawRequestInFlight = false
    @State private var singleDrawGate = GachaSingleDrawGateState()
    @State private var bufferedSingleReceipt: GachaReceiptRow?
    @State private var drawFailureMessage = ""
    @State private var applicationIsActive = false
#if DEBUG
    @State private var didRunDebugPreviewSingleDraw = false
#endif

    public init() {}

    private var activeSeries: GachaSeriesInfo? { model.series.first }

    public var body: some View {
        ZStack(alignment: .bottom) {
            VStack(spacing: 0) {
                header
                tabs

                TabView(selection: $selectedTab) {
                    drawAndRedeem.tag(0)
                    collection.tag(1)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
            }
            .opacity(singleDrawGate.phase == .handoff ? 0 : 1)
            .accessibilityHidden(
                singleDrawGate.transactionID != nil)

            if selectedTab == 0, let series = activeSeries {
                drawDock(series)
                    .opacity(singleDrawGate.phase == .handoff ? 0 : 1)
                    .accessibilityHidden(
                        singleDrawGate.transactionID != nil)
            }

            if let transactionID = singleDrawGate.transactionID {
                if singleDrawGate.awaitingReceiptRecovery {
                    GachaSingleDrawReceiptRecoveryView {
                        model.requestReceipt(requestID: transactionID)
                    }
                    .accessibilityAddTraits(.isModal)
                    .transition(.opacity)
                    .zIndex(30)
                } else {
                    GachaSingleDrawSequenceOverlay(
                        transactionID: transactionID,
                        phase: singleDrawGate.phase,
                        selectedTier: singleDrawGate.selectedPackTier,
                        receiptReady: singleDrawGate.authoritativeReceiptArrived,
                        onSelectTier: { tier in
                            selectPackTier(tier, transactionID: transactionID)
                        },
                        onConfirmTier: {
                            confirmPackSelection(transactionID: transactionID)
                        },
                        onCancel: {
                            cancelPackSelection(transactionID: transactionID)
                        },
                        onSelectionRiveFinished: { reason in
                            finishSelectionAnimation(
                                transactionID: transactionID,
                                reason: reason)
                        },
                        onPackCommitted: {
                            commitPackForCase(transactionID: transactionID)
                        })
                        .accessibilityAddTraits(.isModal)
                        .id(transactionID)
                        .transition(.opacity)
                        .zIndex(30)
                }

                VStack(spacing: 0) {
                    Text(transactionID.uuidString.lowercased())
                        .accessibilityIdentifier("gacha-active-request-id")
                        .accessibilityValue(
                            transactionID.uuidString.lowercased())
                    Text(bufferedSingleReceipt?.prizeId ?? "pending")
                        .accessibilityIdentifier("gacha-pending-prize-id")
                        .accessibilityValue(
                            bufferedSingleReceipt?.prizeId ?? "pending")
                }
                .font(.product(size: 1, weight: .regular))
                .foregroundColor(.clear)
                .frame(width: 1, height: 1)
                .zIndex(31)
            }

        }
        .productDesignSystem()
        .modifier(GachaStorePresentationChrome(
            transparent: singleDrawGate.phase == .handoff))
        .preferredColorScheme(.dark)
        .interactiveDismissDisabled(
            drawRequestInFlight
                || singleDrawGate.transactionID != nil
                || showMultiResults)
        .onAppear {
            applicationIsActive = UIApplication.shared.applicationState == .active
            model.requestState()
        }
        .onChange(of: model.pendingReceipt) { rows in
            guard !rows.isEmpty else { return }
            if let transactionID = singleDrawGate.transactionID {
                guard model.pendingReceiptRequestID
                        == transactionID.uuidString.lowercased() else {
                    drawFailureMessage =
                        "收到不属于当前抽取请求的结果，已保持当前流程等待权威匹配。"
                    return
                }
                guard rows.count == 1 else {
                    abortSingleDraw(
                        transactionID: transactionID,
                        reason: "单抽返回了非单条权威结果，未展示任何替代奖品。")
                    return
                }
                bufferedSingleReceipt = rows[0]
                _ = singleDrawGate.markReceiptArrived(
                    transactionID: transactionID)
                gachaSequenceLog(
                    "[GachaSequence] receipt-matched request=\(transactionID.uuidString.lowercased()) prize=\(rows[0].prizeId)")
                advanceSingleDrawIfReady(transactionID: transactionID)
            } else {
                drawRequestInFlight = false
                if rows.count > 1 {
                    showMultiResults = true
                } else if rows.count == 1,
                          let recoveredID = UUID(
                            uuidString: model.pendingReceiptRequestID) {
                    // A process/background interruption may outlive native
                    // presentation state. Re-enter the visual sequence with
                    // the same durable request id; confirming the Pack sends
                    // an idempotent duplicate request and cannot charge twice.
                    singleDrawGate.begin(transactionID: recoveredID)
                    bufferedSingleReceipt = rows[0]
                    _ = singleDrawGate.markReceiptArrived(
                        transactionID: recoveredID)
                    gachaSequenceLog(
                        "[GachaSequence] receipt-recovered request=\(recoveredID.uuidString.lowercased()) prize=\(rows[0].prizeId)")
                } else {
                    drawFailureMessage =
                        "收到未关联的单抽结果；为避免绕过动画门控，本界面没有自动展示。"
                }
            }
        }
        .onChange(of: model.lastFailureReason) { reason in
            if !reason.isEmpty {
                if let transactionID = singleDrawGate.transactionID {
                    guard model.lastFailureRequestID.isEmpty
                            || model.lastFailureRequestID
                                == transactionID.uuidString.lowercased() else {
                        return
                    }
                    model.acknowledgeReceipt(requestID: transactionID)
                    abortSingleDraw(
                        transactionID: transactionID,
                        reason: reason)
                } else {
                    drawRequestInFlight = false
                    drawFailureMessage = reason
                }
            }
        }
        .onChange(of: model.revealSetupSucceeded) { succeeded in
            guard succeeded,
                  let transactionID = singleDrawGate.transactionID,
                  model.revealRequestID
                    == transactionID.uuidString.lowercased(),
                  singleDrawGate.markUnityCaseReady(
                    transactionID: transactionID) else { return }
            gachaSequenceLog(
                "[GachaSequence] unity-case-ready request=\(transactionID.uuidString.lowercased())")
            DispatchQueue.main.asyncAfter(
                deadline: .now()
                    + GachaSingleDrawGateState.packToCaseTransitionSeconds) {
                guard singleDrawGate.transactionID == transactionID,
                      singleDrawGate.unityCaseReady else { return }
                gachaSequenceLog(
                    "[GachaSequence] pack-case-overlap-complete request=\(transactionID.uuidString.lowercased())")
                singleDrawGate.clear()
                bufferedSingleReceipt = nil
                drawRequestInFlight = false
                dismiss()
            }
        }
        .onChange(of: model.revealSetupFailure) { reason in
            guard !reason.isEmpty,
                  let transactionID = singleDrawGate.transactionID,
                  model.revealRequestID
                    == transactionID.uuidString.lowercased() else { return }
            GachaShippingRevealContinuation.cancelPreparedDisplayCase?()
            model.resetRevealPresentation()
            abortSingleDraw(
                transactionID: transactionID,
                reason: "真实收藏盒准备失败：\(reason)")
        }
        .onReceive(NotificationCenter.default.publisher(
            for: UIApplication.didBecomeActiveNotification)) { _ in
            applicationIsActive = true
            guard let transactionID = singleDrawGate.transactionID else { return }
            advanceSingleDrawIfReady(transactionID: transactionID)
        }
        .onReceive(NotificationCenter.default.publisher(
            for: UIApplication.willResignActiveNotification)) { _ in
            applicationIsActive = false
        }
        .onDisappear {
            guard !drawRequestInFlight,
                  model.revealRequestID.isEmpty else { return }
            model.pendingReceipt = []
            model.lastFailureReason = ""
        }
        .sheet(isPresented: $showDisclosure) {
            probabilityDisclosure
        }
        .sheet(isPresented: $showMultiResults) {
            multiResultSheet
        }
        .alert(
            "抽取未完成",
            isPresented: Binding(
                get: { !drawFailureMessage.isEmpty },
                set: { showing in
                    if !showing { drawFailureMessage = "" }
                })) {
            Button("知道了") { drawFailureMessage = "" }
        } message: {
            Text(drawFailureMessage)
        }
        .task(id: singleDrawGate.drawRequested
            ? singleDrawGate.transactionID
            : nil) {
            guard singleDrawGate.drawRequested,
                  let transactionID = singleDrawGate.transactionID else { return }
            do {
                try await Task.sleep(
                    nanoseconds: GachaSingleDrawGateState
                        .receiptTimeoutNanoseconds)
            } catch {
                return
            }
            guard !Task.isCancelled,
                  singleDrawGate.transactionID == transactionID,
                  !singleDrawGate.authoritativeReceiptArrived else { return }
            guard singleDrawGate.markReceiptTimedOut(
                transactionID: transactionID) else { return }
            drawFailureMessage =
                "等待权威抽取结果超时（20 秒）。本次抽取仍在等待恢复，不会重抽或展示替代奖品。"
            model.requestState()
        }
#if DEBUG
        .task {
            await runDebugPreviewSingleDrawIfRequested()
        }
#endif
    }

    private var header: some View {
        HStack(spacing: 10) {
            VStack(alignment: .leading, spacing: 3) {
                Text("抽取与收藏")
                    .font(.product(size: 27, weight: .black))
                    .foregroundColor(.white)
                Text("票券抽取 · 外观收藏 · 图纸兑换")
                    .font(.product(size: 11, weight: .medium))
                    .foregroundColor(.white.opacity(0.48))
            }

            Spacer(minLength: 8)
            walletChip(symbol: "ticket.fill", value: model.tickets, title: "抽取券")
            walletChip(symbol: "gearshape.2.fill", value: model.coins, title: "齿轮币")
        }
        .padding(.horizontal, FidgetUITokens.Spacing.pageInset)
        .padding(.top, 20)
        .padding(.bottom, 12)
    }

    private func walletChip(symbol: String, value: Int, title: String) -> some View {
        HStack(spacing: 6) {
            Image(systemName: symbol)
                .font(.product(size: 12, weight: .semibold))
            VStack(alignment: .leading, spacing: 0) {
                Text("\(value)")
                    .font(.product(size: 13, weight: .bold).monospacedDigit())
                Text(title)
                    .font(.product(size: 9, weight: .medium))
                    .foregroundColor(.white.opacity(0.45))
            }
        }
        .foregroundColor(.white.opacity(0.90))
        .padding(.horizontal, 10)
        .frame(height: 44)
        .background(Color.white.opacity(0.08), in: Capsule())
    }

    private var tabs: some View {
        HStack(spacing: FidgetUITokens.Spacing.standard) {
            ProductFilterChip(
                title: "抽取 / 兑换",
                selected: selectedTab == 0) {
                    selectTab(0)
                }
            ProductFilterChip(
                title: "收藏",
                selected: selectedTab == 1) {
                    selectTab(1)
                }
            Spacer(minLength: 0)
        }
        .padding(.horizontal, FidgetUITokens.Spacing.pageInset)
        .padding(.bottom, 8)
    }

    private func selectTab(_ index: Int) {
        withAnimation(.easeOut(duration: FidgetUITokens.Motion.selectionDuration)) {
            selectedTab = index
        }
    }

    private var drawAndRedeem: some View {
        ScrollView(showsIndicators: false) {
            VStack(
                alignment: .leading,
                spacing: FidgetUITokens.Spacing.sectionGroup) {
                if let series = activeSeries {
                    packEntry(series)
                }
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
            .padding(.horizontal, FidgetUITokens.Spacing.pageInset)
            .padding(.bottom, 126)
        }
    }

    private func packEntry(_ series: GachaSeriesInfo) -> some View {
        let tier = GachaPackTier.forSeriesId(series.id)
        return VStack(alignment: .leading, spacing: FidgetUITokens.Spacing.standard) {
            VStack(alignment: .leading, spacing: 6) {
                Text("FIDGET ARCHIVE")
                    .font(.product(size: 13, weight: .semibold))
                    .foregroundColor(.white.opacity(0.55))
                Text(series.name)
                    .font(.product(size: 25, weight: .black))
                    .foregroundColor(.white)
                Text("\(tier.title) PACK · 1 张抽取券 · 向右撕开封边")
                    .font(.product(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.52))
            }

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 16) {
                    ForEach(GachaPackTier.allCases, id: \.self) { packTier in
                        VStack(spacing: 8) {
                            GachaPackVisual(tier: packTier, tearProgress: 0)
                                .frame(width: 108, height: 144)
                            Text(packTier.title)
                                .font(.product(size: 10, weight: .bold))
                                .foregroundColor(
                                    .white.opacity(packTier == tier ? 0.88 : 0.42))
                        }
                    }
                }
                .padding(.vertical, 2)
            }
        }
        .padding(FidgetUITokens.Spacing.section)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(series.name)，\(tier.title) 抽取包装，消耗一张抽取券")
        .accessibilityIdentifier("gacha-pack-entry")
    }

    private var featuredBanner: some View {
        GachaBundleArtwork(name: "product-banner-magnetic-fan-card")
            .scaledToFit()
            .aspectRatio(1179.0 / 654.0, contentMode: .fit)
            .frame(maxWidth: .infinity)
            .background(Color(white: 0.06))
            .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(
                "本期主推，磁吸扇牌，超现实悬浮卡牌场景，商品展示尚未开放购买")
    }

    private func quietBadge(_ text: String) -> some View {
        ProductStatusTag(
            title: text,
            accent: .white,
            emphasized: true,
            font: .product(size: 10, weight: .bold))
    }

    private var relatedSkins: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("同系列皮肤")
                    .font(.product(size: 18, weight: .bold))
                    .foregroundColor(.white)
                Spacer()
                Text("三叶金属")
                    .font(.product(size: 11, weight: .semibold))
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
                .background(.ultraThinMaterial)
            Text(title)
                .font(.product(size: 14, weight: .bold))
                .foregroundColor(.white)
            Text(subtitle)
                .font(.product(size: 10, weight: .medium))
                .foregroundColor(.white.opacity(0.42))
        }
        .padding(10)
        .frame(width: 164, alignment: .leading)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18))
    }

    private var economyNotice: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("齿轮币不用于抽取")
                .font(.product(size: 14, weight: .bold))
                .foregroundColor(.white)
            Text("抽取只消耗抽取券；齿轮币保留给打造和已拥有外观的定制。")
                .font(.product(size: 11, weight: .medium))
                .foregroundColor(.white.opacity(0.48))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(FidgetUITokens.Spacing.section)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18))
    }

    private func drawPoolSummary(_ series: GachaSeriesInfo) -> some View {
        let signature = model.signatureMisses[series.id] ?? 0
        let heirloom = model.heirloomMisses[series.id] ?? 0
        return VStack(alignment: .leading, spacing: FidgetUITokens.Spacing.standard) {
            HStack(spacing: FidgetUITokens.Spacing.standard) {
                ProductFilterChip(title: "概率与保底") {
                    showDisclosure = true
                }
                Spacer(minLength: 0)
                ProductStatusTag(title: series.name)
            }

            HStack(spacing: 10) {
                compactPityMeter(
                    title: "臻藏保底",
                    current: signature,
                    target: 51,
                    tint: GachaRarityTier.signature.shippingTint)
                compactPityMeter(
                    title: "传世保底",
                    current: heirloom,
                    target: 90,
                    tint: GachaRarityTier.heirloom.shippingTint)
            }
        }
        .padding(FidgetUITokens.Spacing.section)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18))
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            "概率与保底，臻藏保底 \(signature) / 51，传世保底 \(heirloom) / 90")
    }

    private func compactPityMeter(
        title: String,
        current: Int,
        target: Int,
        tint: Color
    ) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 4) {
                Text(title)
                    .font(.product(size: 11, weight: .bold))
                    .foregroundColor(.white.opacity(0.72))
                Spacer(minLength: 4)
                Text("\(min(current, target))/\(target)")
                    .font(.product(size: 11, weight: .semibold).monospacedDigit())
                    .foregroundColor(.white.opacity(0.52))
            }
            GeometryReader { proxy in
                let fraction = target > 0
                    ? min(1, Double(current) / Double(target))
                    : 0
                Capsule()
                    .fill(Color.white.opacity(0.12))
                    .overlay(alignment: .leading) {
                        Capsule()
                            .fill(tint.opacity(0.85))
                            .frame(width: proxy.size.width * fraction)
                    }
            }
            .frame(height: 4)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
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
                    .font(.product(size: 18, weight: .bold))
                Spacer()
                Text("合金屑 \(shards)")
                    .font(.product(size: 11, weight: .semibold).monospacedDigit())
                    .foregroundColor(.white.opacity(0.46))
            }
            .foregroundColor(.white)

            if redeemables.isEmpty {
                Text("本系列暂无可兑换项目")
                    .font(.product(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.42))
            } else {
                ForEach(redeemables.prefix(4)) { prize in
                    redeemRow(prize, shards: shards)
                }
            }
        }
        .padding(FidgetUITokens.Spacing.section)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18))
    }

    private func redeemRow(_ prize: GachaPrizeInfo, shards: Int) -> some View {
        let cost = prize.rarity.redeemCost ?? Int.max
        return HStack(spacing: 10) {
            Capsule()
                .fill(prize.rarity.shippingTint)
                .frame(width: 3, height: 28)
            VStack(alignment: .leading, spacing: 2) {
                Text(prize.name)
                    .font(.product(size: 13, weight: .semibold))
                Text("\(prize.rarity.title) · \(prize.kindTitle)")
                    .font(.product(size: 10, weight: .medium))
                    .foregroundColor(.white.opacity(0.40))
            }
            Spacer()
            Button("\(cost)") {
                model.redeem(prizeId: prize.id)
            }
            .font(.product(size: 12, weight: .bold).monospacedDigit())
            .foregroundColor(shards >= cost ? .black : .white.opacity(0.28))
            .padding(.horizontal, 12)
            .frame(minWidth: 44, minHeight: 44)
            .background(
                (shards >= cost ? Color.white : Color.white.opacity(0.06)),
                in: Capsule(style: .continuous))
            .disabled(shards < cost)
        }
        .foregroundColor(.white)
    }

    private var collection: some View {
        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: 12) {
                if let series = activeSeries {
                    Text("收藏 \(model.prizes.filter { model.owned.contains($0.id) }.count) / \(model.prizes.count)")
                        .font(.product(size: 18, weight: .bold))
                        .foregroundColor(.white)

                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        ForEach(model.prizes.filter { $0.seriesId == series.id }) { prize in
                            collectionCard(prize)
                        }
                    }
                }
            }
            .padding(.horizontal, FidgetUITokens.Spacing.pageInset)
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
                ProductStatusTag(
                    title: owned ? "已拥有" : "未获得",
                    accent: .white,
                    emphasized: owned,
                    font: .product(size: 9, weight: .bold))
                    .opacity(owned ? 1 : 0.58)
            }
            Text(prize.name)
                .font(.product(size: 14, weight: .bold))
                .foregroundColor(owned ? .white : .white.opacity(0.42))
            Text("\(prize.rarity.title) · \(prize.kindTitle)")
                .font(.product(size: 10, weight: .medium))
                .foregroundColor(.white.opacity(0.38))
        }
        .frame(maxWidth: .infinity, minHeight: 92, alignment: .topLeading)
        .padding(13)
        .background(Color.white.opacity(owned ? 0.065 : 0.028), in: RoundedRectangle(cornerRadius: 17))
    }

    private func drawDock(_ series: GachaSeriesInfo) -> some View {
        VStack(spacing: FidgetUITokens.Spacing.metadata) {
            HStack(alignment: .center, spacing: FidgetUITokens.Spacing.standard) {
                VStack(alignment: .leading, spacing: FidgetUITokens.Spacing.compact) {
                    Text("消耗 1 张抽取券")
                        .font(.product(.caption, weight: .semibold))
                        .foregroundColor(.white.opacity(0.76))
                    Text("剩余 \(model.tickets) 张")
                        .font(.product(.caption2, weight: .medium).monospacedDigit())
                        .foregroundColor(.white.opacity(0.52))
                }
                Spacer(minLength: FidgetUITokens.Spacing.standard)
                ProductStatusTag(title: "十抽后续开放")
            }

            ProductPrimaryActionButton(
                title: "单抽",
                state: singleDrawActionState) {
                startSingleDraw(series)
            }
            .accessibilityIdentifier("gacha-single-draw")
            .accessibilityHint("消耗一张抽取券")
        }
        .padding(.horizontal, FidgetUITokens.Spacing.pageInset)
        .padding(.top, FidgetUITokens.Spacing.metadata)
        .padding(.bottom, 12)
        .background(.ultraThinMaterial)
    }

    private var singleDrawActionState: ProductActionState {
        if drawRequestInFlight || singleDrawGate.transactionID != nil {
            return .loading("抽取中")
        }
        if model.tickets < 1 {
            return .disabled
        }
        return .rest
    }

#if DEBUG
    @MainActor
    private func runDebugPreviewSingleDrawIfRequested() async {
        guard ProcessInfo.processInfo.arguments.contains(
                "--preview-auto-single-draw"),
              !didRunDebugPreviewSingleDraw else { return }

        didRunDebugPreviewSingleDraw = true
        try? await Task.sleep(nanoseconds: 800_000_000)

        for _ in 0..<20 {
            if let series = activeSeries {
                // Preview automation must exercise the production gate and
                // authoritative draw request; it never duplicates draw logic.
                startSingleDraw(series)
                return
            }
            try? await Task.sleep(nanoseconds: 100_000_000)
        }
    }
#endif

    @MainActor
    private func startSingleDraw(_ series: GachaSeriesInfo) {
        guard !drawRequestInFlight,
              singleDrawGate.transactionID == nil else { return }

        let transactionID = UUID()
        singleDrawGate.begin(transactionID: transactionID)
        bufferedSingleReceipt = nil
        drawFailureMessage = ""
        drawRequestInFlight = false
        model.pendingReceipt = []
        model.lastFailureReason = ""
        gachaSequenceLog(
            "[GachaSequence] carousel-open request=\(transactionID.uuidString.lowercased())")
    }

    @MainActor
    private func selectPackTier(
        _ tier: GachaPackTier,
        transactionID: UUID
    ) {
        guard singleDrawGate.selectPack(
            tier,
            transactionID: transactionID) else { return }
        gachaSequenceLog(
            "[GachaSequence] pack-selected tier=\(tier.rawValue) presentationOnly=true")
    }

    @MainActor
    private func confirmPackSelection(transactionID: UUID) {
        guard let series = activeSeries,
              singleDrawGate.commitPackSelection(
                transactionID: transactionID) else { return }
        drawRequestInFlight = true
        gachaSequenceLog(
            "[GachaSequence] draw-requested request=\(transactionID.uuidString.lowercased())")
        model.draw(
            requestID: transactionID,
            seriesId: series.id,
            count: 1,
            useCoins: false)
    }

    @MainActor
    private func cancelPackSelection(transactionID: UUID) {
        guard singleDrawGate.transactionID == transactionID,
              !singleDrawGate.drawRequested else { return }
        singleDrawGate.clear()
        bufferedSingleReceipt = nil
        drawRequestInFlight = false
    }

    @MainActor
    private func finishSelectionAnimation(
        transactionID: UUID,
        reason: GachaRiveCompletionReason
    ) {
        guard singleDrawGate.markSelectionAnimationFinished(
            transactionID: transactionID) else { return }
        gachaSequenceLog(
            "[GachaSequence] selection-rive-completed reason=\(reason.rawValue)")
    }

    @MainActor
    private func commitPackForCase(transactionID: UUID) {
        guard singleDrawGate.markPackCommitted(
            transactionID: transactionID) else { return }
        gachaSequenceLog(
            "[GachaSequence] pack-committed request=\(transactionID.uuidString.lowercased())")
        advanceSingleDrawIfReady(transactionID: transactionID)
    }

    @MainActor
    private func advanceSingleDrawIfReady(transactionID: UUID) {
        guard applicationIsActive,
              singleDrawGate.decision(transactionID: transactionID) == .reveal,
              let receipt = bufferedSingleReceipt,
              let continuation =
                GachaShippingRevealContinuation.preparePremiumDisplayCase,
              singleDrawGate.markHandoffDispatched(
                transactionID: transactionID) else { return }

        gachaSequenceLog(
            "[GachaSequence] unity-case-prepare-requested request=\(transactionID.uuidString.lowercased()) prize=\(receipt.prizeId) count=1")
        let requestID = transactionID.uuidString.lowercased()
        model.beginRevealSetup(requestID: requestID)
        continuation(requestID, receipt)
    }

    @MainActor
    private func abortSingleDraw(transactionID: UUID, reason: String) {
        guard singleDrawGate.fail(
            transactionID: transactionID,
            reason: reason) else { return }

        if model.revealRequestID == transactionID.uuidString.lowercased() {
            GachaShippingRevealContinuation.cancelPreparedDisplayCase?()
            model.resetRevealPresentation()
        }
        singleDrawGate.clear()
        bufferedSingleReceipt = nil
        drawRequestInFlight = false
        model.pendingReceipt = []
        drawFailureMessage = reason
    }

    private var probabilityDisclosure: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Text("概率与保底")
                            .font(.product(size: 23, weight: .black))
                        Spacer()
                        Button("完成") { showDisclosure = false }
                            .font(.product(size: 14, weight: .bold))
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
                                    .font(.product(size: 14, weight: .semibold).monospacedDigit())
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
                    .font(.product(size: 12, weight: .medium))
                    .foregroundColor(.white.opacity(0.58))
                    .lineSpacing(4)
                }
                .padding(FidgetUITokens.Spacing.section)
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
                    .font(.product(size: 12, weight: .semibold).monospacedDigit())
            }
            .font(.product(size: 13, weight: .bold))
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
                    .font(.product(size: 23, weight: .black))
                    .foregroundColor(.white)
                    .padding(.top, 20)
                ScrollView {
                    VStack(spacing: 9) {
                        ForEach(model.pendingReceipt) { row in
                            resultRow(row)
                        }
                    }
                    .padding(.horizontal, FidgetUITokens.Spacing.section)
                }
                ProductPrimaryActionButton(title: "收入囊中") {
                        model.pendingReceipt = []
                        showMultiResults = false
                }
                .padding(FidgetUITokens.Spacing.section)
            }
        }
        .interactiveDismissDisabled(true)
    }

    private func resultRow(_ row: GachaReceiptRow) -> some View {
        HStack(spacing: 10) {
            Capsule().fill(row.rarity.shippingTint).frame(width: 3, height: 34)
            VStack(alignment: .leading, spacing: 2) {
                Text(row.name).font(.product(size: 14, weight: .bold))
                Text(row.rarity.title)
                    .font(.product(size: 10, weight: .medium))
                    .foregroundColor(.white.opacity(0.44))
            }
            Spacer()
            Text(row.isNew ? "NEW" : "+\(row.shardsGained)")
                .font(.product(size: 11, weight: .bold).monospacedDigit())
                .foregroundColor(.white.opacity(0.68))
        }
        .foregroundColor(.white)
        .padding(13)
        .background(Color.white.opacity(0.055), in: RoundedRectangle(cornerRadius: 16))
    }
}

/// Receipt-free shipping sequence. Pack edition is presentation-only and the
/// authoritative receipt never enters either Rive surface.
private struct GachaSingleDrawSequenceOverlay: View {
    let transactionID: UUID
    let phase: GachaSingleDrawGateState.Phase
    let selectedTier: GachaPackTier
    let receiptReady: Bool
    let onSelectTier: (GachaPackTier) -> Void
    let onConfirmTier: () -> Void
    let onCancel: () -> Void
    let onSelectionRiveFinished: (GachaRiveCompletionReason) -> Void
    let onPackCommitted: () -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var carouselDrag: CGFloat = 0
    @State private var tearProgress: CGFloat = 0
    @State private var packExitOffset: CGFloat = 0
    @State private var packOpenCommitted = false
    @State private var packState = "sealed"

    var body: some View {
        ZStack {
            Group {
                if phase == .handoff {
                    Color.clear
                } else {
                    Color.black.opacity(0.985)
                }
            }
            .ignoresSafeArea()

            switch phase {
            case .choosingPack:
                packCarousel
            case .selectionRive:
                selectionCue
            case .tearPack, .preparingCase, .waitingForReceipt, .handoff:
                packToCaseSurface
            case .receiptRecovery:
                receiptWait
            case .idle:
                Color.black.ignoresSafeArea()
            }
        }
        .accessibilityIdentifier("gacha-single-draw-sequence")
        .onChange(of: phase) { nextPhase in
            guard nextPhase == .handoff else { return }
            packState = "case-ready"
            gachaSequenceLog(
                "[GachaSequence] pack-case-overlap-start request=\(transactionID.uuidString.lowercased())")
            withAnimation(.easeOut(duration: reduceMotion
                ? 0.01
                : GachaSingleDrawGateState.packToCaseTransitionSeconds)) {
                packExitOffset = 720
            }
        }
        .task(id: phase) {
            await runPreviewAutomationIfRequested()
        }
    }

    private var packCarousel: some View {
        GeometryReader { _ in
            let tiers = GachaPackTier.allCases
            let selectedIndex = tiers.firstIndex(of: selectedTier) ?? 0

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

                ZStack {
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
                            if index != selectedIndex {
                                gachaHaptic(.light)
                            }
                            withAnimation(.spring(
                                response: GachaPackCarouselRules
                                    .selectionSnapResponseSeconds,
                                dampingFraction: GachaPackCarouselRules
                                    .selectionSnapDampingFraction)) {
                                carouselDrag = 0
                                onSelectTier(tier)
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
                        .offset(
                            x: CGFloat(x),
                            y: CGFloat(y))
                        .rotationEffect(
                            .degrees(tilt),
                            anchor: .bottom)
                        .opacity(abs(position) > 2.6 ? 0 : 1)
                        .zIndex(3 - abs(position))
                        .accessibilityLabel("\(tier.title) Pack")
                        .accessibilityAddTraits(
                            index == selectedIndex ? .isSelected : [])
                        .accessibilityIdentifier(
                            "gacha-pack-tier-\(tier.rawValue)")
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
                            if next != selectedIndex {
                                gachaHaptic(.light)
                            }
                            withAnimation(.spring(
                                response: GachaPackCarouselRules
                                    .selectionSnapResponseSeconds,
                                dampingFraction: GachaPackCarouselRules
                                    .selectionSnapDampingFraction)) {
                                carouselDrag = 0
                                onSelectTier(tiers[next])
                            }
                        })
                .accessibilityIdentifier("gacha-pack-carousel")

                VStack(spacing: FidgetUITokens.Spacing.standard) {
                    ProductPrimaryActionButton(title: "选择 \(selectedTier.title)") {
                        onConfirmTier()
                    }
                    .accessibilityIdentifier("gacha-pack-select")

                    ProductSecondaryActionButton(
                        title: "取消",
                        action: onCancel)
                }
                .padding(.horizontal, FidgetUITokens.Spacing.pageInset)
                .padding(.bottom, FidgetUITokens.Spacing.sectionGroup)
            }
        }
    }

    private var selectionCue: some View {
        VStack(spacing: 18) {
            Text("PACK SELECTED")
                .font(.product(size: 12, weight: .bold))
                .foregroundColor(.white.opacity(0.52))
            ZStack {
                GachaSingleDrawRiveGate(
                    transactionID: transactionID,
                    stage: .packSelection) { id, reason in
                        guard id == transactionID else { return }
                        onSelectionRiveFinished(reason)
                    }
                    // Keep the authored rotate-line trajectory behind the Pack
                    // while exposing its upper arc and side halo to the eye.
                    .offset(y: -42)
                GachaPackVisual(tier: selectedTier, tearProgress: 0)
                    .frame(width: 244, height: 326)
                    .scaleEffect(0.72)
                    .allowsHitTesting(false)
            }
            .frame(width: 270, height: 360)
            Text(selectedTier.title)
                .font(.product(size: 13, weight: .bold))
                .foregroundColor(.white.opacity(0.76))
        }
    }

    private var packToCaseSurface: some View {
        ZStack {
            tearSurface
                .allowsHitTesting(phase == .tearPack && !packOpenCommitted)

            if phase == .preparingCase || phase == .waitingForReceipt {
                VStack(spacing: 8) {
                    ProgressView().tint(.white)
                    Text(phase == .preparingCase
                        ? "正在准备真实收藏盒"
                        : "正在确认权威结果")
                        .font(.product(size: 12, weight: .semibold))
                        .foregroundColor(.white.opacity(0.62))
                }
                .offset(y: 260)
                .accessibilityIdentifier("gacha-authoritative-receipt-wait")
            }

            Text(packState)
                .font(.product(size: 1, weight: .regular))
                .foregroundColor(.clear)
                .accessibilityLabel("Pack state")
                .accessibilityValue(packState)
                .accessibilityIdentifier("gacha-pack-state")
        }
        .accessibilityIdentifier("gacha-pack-case-transition")
    }

    private var tearSurface: some View {
        VStack(spacing: 18) {
            Text("撕开包装")
                .font(.product(size: 13, weight: .bold))
                .foregroundColor(.white.opacity(0.58))

            GachaPackVisual(tier: selectedTier, tearProgress: tearProgress)
                .frame(width: 244, height: 326)
                .offset(y: packExitOffset)
                .opacity(packExitOffset > 480 ? 0 : 1)
                .contentShape(Rectangle())
                .gesture(
                    DragGesture(minimumDistance: 6, coordinateSpace: .local)
                        .onChanged { value in
                            guard !packOpenCommitted else { return }
                            tearProgress = CGFloat(
                                GachaPackOpeningRules.normalizedProgress(
                                    translationPoints: Double(
                                        value.translation.width)))
                        }
                        .onEnded { _ in
                            releaseTear(at: tearProgress)
                        })
                .accessibilityLabel("\(selectedTier.title) 抽取包装")
                .accessibilityHint("沿顶部封边向右滑动以撕开")
                .accessibilityIdentifier("gacha-pack-tear-target")

            if !packOpenCommitted {
                ProductPrimaryActionButton(title: "撕开包装") {
                    tearProgress = 1
                    commitPackOpen()
                }
                .accessibilityIdentifier("gacha-pack-open")
                .padding(.horizontal, FidgetUITokens.Spacing.pageInset)
            } else {
                Color.clear
                    .frame(height: FidgetUITokens.Size.primaryActionHeight)
            }
        }
        .frame(maxWidth: .infinity)
    }

    private var receiptWait: some View {
        VStack(spacing: 16) {
            ProgressView().tint(.white)
            Text(receiptReady ? "正在交接收藏品" : "正在确认权威结果")
                .font(.product(size: 13, weight: .semibold))
                .foregroundColor(.white.opacity(0.62))
        }
        .accessibilityIdentifier("gacha-authoritative-receipt-wait")
    }

    @MainActor
    private func releaseTear(at progress: CGFloat) {
        guard !packOpenCommitted else { return }
        if GachaPackOpeningRules.shouldCommit(progress: Double(progress)) {
            GachaPackInteractionTrace.record(
                event: "release-commit",
                progress: progress)
            commitPackOpen()
        } else {
            GachaPackInteractionTrace.record(
                event: "release-rebound",
                progress: progress)
            withAnimation(.easeOut(duration: reduceMotion ? 0.01 : 0.18)) {
                tearProgress = 0
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.20) {
                GachaPackInteractionTrace.record(
                    event: "rebound-complete",
                    progress: 0)
            }
        }
    }

    @MainActor
    private func commitPackOpen() {
        guard !packOpenCommitted else { return }
        packOpenCommitted = true
        packState = "committed"
        gachaHaptic(.heavy)
        GachaPackInteractionTrace.record(
            event: "commit-start",
            progress: tearProgress)
        gachaSequenceLog(
            "[GachaSequence] tear-commit request=\(transactionID.uuidString.lowercased()) progress=\(tearProgress)")
        withAnimation(.easeOut(duration: reduceMotion
            ? 0.01
            : GachaPackOpeningRules.flapExitDurationSeconds)) {
            tearProgress = 1
        }
        packState = "opened-awaiting-case"
        onPackCommitted()
    }

    @MainActor
    private func runPreviewAutomationIfRequested() async {
#if DEBUG
        let arguments = ProcessInfo.processInfo.arguments
        if phase == .choosingPack,
           let carouselTierArgument = arguments.first(where: {
               $0.hasPrefix("--preview-carousel-tier=")
           }) {
            let rawTier = carouselTierArgument
                .split(separator: "=").last.map(String.init) ?? "signature"
            onSelectTier(GachaPackTier(rawValue: rawTier) ?? .signature)
            if arguments.contains("--preview-auto-confirm-pack") {
                do { try await Task.sleep(nanoseconds: 700_000_000) } catch {
                    return
                }
                guard !Task.isCancelled else { return }
                onConfirmTier()
            }
        } else if phase == .choosingPack,
           arguments.contains("--preview-auto-select-pack") {
            let rawTier = arguments.first(where: {
                $0.hasPrefix("--preview-pack-tier=")
            })?.split(separator: "=").last.map(String.init) ?? "signature"
            let tier = GachaPackTier(rawValue: rawTier) ?? .signature
            onSelectTier(tier)
            do { try await Task.sleep(nanoseconds: 420_000_000) } catch { return }
            guard !Task.isCancelled else { return }
            onConfirmTier()
        } else if phase == .tearPack,
                  arguments.contains("--preview-auto-open-pack") {
            GachaPackInteractionTrace.beginIfRequested()
            do { try await Task.sleep(nanoseconds: 520_000_000) } catch { return }
            guard !Task.isCancelled, !packOpenCommitted else { return }
            tearProgress = 0.55
            releaseTear(at: 0.55)
            gachaSequenceLog(
                "[GachaSequence] tear-rebound request=\(transactionID.uuidString.lowercased()) progress=0.55")
            do { try await Task.sleep(nanoseconds: 420_000_000) } catch { return }
            guard !Task.isCancelled, !packOpenCommitted else { return }
            tearProgress = 0.75
            releaseTear(at: 0.75)
        }
#endif
    }
}

private enum GachaRevealPhase: Int {
    case back
    case front
    case readable
    case sheen
    case complete
}

private struct GachaSingleDrawReveal: View {
    let receipt: GachaReceiptRow
    let packTier: GachaPackTier
    let enterPremiumDisplayCase: () -> Bool
    let completion: () -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var phase: GachaRevealPhase = .back
    @State private var sheenOffset: CGFloat = -260
    @State private var tearProgress: CGFloat = 0
    @State private var packOpened = false
    @State private var packOpenCommitted = false

    var body: some View {
        ZStack {
            Color.black.opacity(0.975).ignoresSafeArea()

            VStack(spacing: 24) {
                Text("单抽揭晓")
                    .font(.product(size: 12, weight: .bold))
                    .foregroundColor(.white.opacity(0.55))

                Group {
                    if packOpened {
                        GachaCaseRevealVisual(
                            phase: phase,
                            rarity: receipt.rarity,
                            title: receipt.name,
                            sheenOffset: sheenOffset)
                            .transition(.opacity.combined(with: .scale(scale: 0.97)))
                    } else {
                        GachaPackVisual(tier: packTier, tearProgress: tearProgress)
                            .frame(width: 244, height: 326)
                            .contentShape(Rectangle())
                            .gesture(
                                DragGesture(minimumDistance: 6, coordinateSpace: .local)
                                    .onChanged { value in
                                        guard !packOpenCommitted else { return }
                                        tearProgress = CGFloat(
                                            GachaPackOpeningRules.normalizedProgress(
                                                translationPoints: Double(value.translation.width)))
                                    }
                                    .onEnded { _ in
                                        guard !packOpenCommitted else { return }
                                        let releasedProgress = tearProgress
                                        if GachaPackOpeningRules.shouldCommit(
                                            progress: Double(tearProgress)) {
                                            GachaPackInteractionTrace.record(
                                                event: "release-commit",
                                                progress: releasedProgress)
                                            commitPackOpen()
                                        } else {
                                            GachaPackInteractionTrace.record(
                                                event: "release-rebound",
                                                progress: releasedProgress)
                                            withAnimation(.easeOut(duration: 0.18)) {
                                                tearProgress = 0
                                            }
                                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.20) {
                                                GachaPackInteractionTrace.record(
                                                    event: "rebound-complete",
                                                    progress: 0)
                                            }
                                        }
                                    })
                            .accessibilityLabel("\(packTier.title) 抽取包装")
                            .accessibilityHint("沿顶部封边向右滑动以撕开")
                            .accessibilityIdentifier("gacha-pack-tear-target")
                    }
                }
                .frame(width: 290, height: 390)

                Group {
                    if packOpened
                        && phase.rawValue >= GachaRevealPhase.readable.rawValue {
                        VStack(spacing: 7) {
                            Text(receipt.name)
                                .font(.product(size: 24, weight: .black))
                                .foregroundColor(.white)
                            HStack(spacing: 7) {
                                Capsule()
                                    .fill(receipt.rarity.shippingTint)
                                    .frame(width: 24, height: 3)
                                Text(receipt.rarity.title)
                                Text(receipt.isNew
                                    ? "NEW"
                                    : "+\(receipt.shardsGained) 合金屑")
                            }
                            .font(.product(size: 11, weight: .semibold))
                            .foregroundColor(.white.opacity(0.52))
                        }
                    } else {
                        Color.clear.frame(height: 44)
                    }
                }

                if !packOpened {
                    ProductPrimaryActionButton(
                        title: "撕开包装",
                        state: packOpenCommitted ? .loading("正在打开") : .rest) {
                            commitPackOpen()
                        }
                        .frame(width: 214)
                        .accessibilityIdentifier("gacha-pack-open")
                } else if phase == .complete {
                    ProductPrimaryActionButton(title: "收下", action: completion)
                        .frame(width: 214)
                        .transition(.opacity.combined(with: .scale(scale: 0.96)))
                        .accessibilityIdentifier("gacha-reveal-accept")
                } else {
                    Text(phaseCaption)
                        .font(.product(size: 11, weight: .medium))
                        .foregroundColor(.white.opacity(0.34))
                        .frame(height: 54)
                }
            }
            .padding(.vertical, 32)
        }
        .task {
#if DEBUG
            GachaPackInteractionTrace.beginIfRequested()
            if let progressArgument = ProcessInfo.processInfo.arguments.first(
                where: { $0.hasPrefix("--preview-pack-progress=") }),
               let rawProgress = Double(progressArgument.split(separator: "=").last ?? "") {
                tearProgress = CGFloat(min(max(rawProgress, 0), 1))
            } else if ProcessInfo.processInfo.arguments.contains("--preview-pack-opened") {
                packOpened = true
            } else if ProcessInfo.processInfo.arguments.contains("--preview-auto-open-pack") {
                do {
                    try await Task.sleep(nanoseconds: 1_200_000_000)
                } catch {
                    return
                }
                guard !Task.isCancelled,
                      !packOpenCommitted,
                      !packOpened else { return }
                // Preview automation preserves the sealed-Pack beat and then
                // enters the same production threshold/commit path as a drag.
                commitPackOpen()
            }
#endif
        }
    }

    private var phaseCaption: String {
        if !packOpened {
            return "沿顶部封边向右撕开"
        }
        switch phase {
        case .back: return "收藏盒入场"
        case .front: return "收藏盒翻正"
        case .readable: return "奖品确认"
        case .sheen: return "完成过光"
        case .complete: return ""
        }
    }

    @MainActor
    private func commitPackOpen() {
        guard !packOpened, !packOpenCommitted else { return }
        packOpenCommitted = true
        GachaPackInteractionTrace.record(event: "commit-start", progress: tearProgress)
        withAnimation(.easeOut(duration: reduceMotion
            ? 0.01
            : GachaPackOpeningRules.flapExitDurationSeconds)) {
            tearProgress = 1
        }

        Task { @MainActor in
            let delay: UInt64 = reduceMotion ? 10_000_000 : 360_000_000
            guard await pause(delay) else { return }
            withAnimation(.easeOut(duration: reduceMotion ? 0.01 : 0.24)) {
                packOpened = true
            }
            if enterPremiumDisplayCase() {
                GachaPackInteractionTrace.record(
                    event: "premium-display-case-entry",
                    progress: 1)
                return
            }
            await play()
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

private enum GachaPackInteractionTrace {
    private static let defaultsKey = "gacha.pack.shipping.trace.v1"

    static func beginIfRequested() {
#if DEBUG
        guard ProcessInfo.processInfo.arguments.contains("--gacha-pack-trace") else {
            return
        }
        UserDefaults.standard.set([], forKey: defaultsKey)
        record(event: "sealed", progress: 0)
#endif
    }

    static func record(event: String, progress: CGFloat) {
#if DEBUG
        guard ProcessInfo.processInfo.arguments.contains("--gacha-pack-trace") else {
            return
        }
        let value = Double(min(max(progress, 0), 1))
        var events = UserDefaults.standard.array(forKey: defaultsKey)
            as? [[String: Any]] ?? []
        events.append([
            "event": event,
            "progress": value,
            "threshold": GachaPackOpeningRules.tearCommitProgress,
            "uptime": ProcessInfo.processInfo.systemUptime
        ])
        UserDefaults.standard.set(events, forKey: defaultsKey)
        UserDefaults.standard.synchronize()
        print(String(format: "[GachaPackTrace] %@ progress=%.4f threshold=%.4f",
            event,
            value,
            GachaPackOpeningRules.tearCommitProgress))
#endif
    }
}

private struct GachaCaseRevealVisual: View {
    let phase: GachaRevealPhase
    let rarity: GachaRarityTier
    let title: String
    let sheenOffset: CGFloat

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
            }

            cornerPins

            rewardCard
                .scaleEffect(
                    phase.rawValue >= GachaRevealPhase.sheen.rawValue
                        ? 1.04
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
                    .font(.product(size: 16, weight: .bold))
                    .foregroundColor(.white.opacity(0.92))
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                    .frame(width: 142)

                Text("COLLECTED")
                    .font(.product(size: 9, weight: .bold))
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

            LinearGradient(
                colors: [.clear, .white.opacity(0.58), .clear],
                startPoint: .leading,
                endPoint: .trailing)
                .frame(width: 202, height: 1.2)
                .offset(y: -133)
                .opacity(Double(progress) * 0.72)
                .accessibilityHidden(true)
        }
        .aspectRatio(384.0 / 512.0, contentMode: .fit)
        .shadow(color: .black.opacity(0.52), radius: 18, y: 11)
    }
}

#if DEBUG
/// Release-gate evidence surface for comparing every approved Pack edition.
///
/// This view deliberately composes `GachaPackVisual` rather than recreating its
/// layers so simulator evidence exercises the exact body/flap renderer used by
/// the single-draw shipping flow. It is excluded from Release builds.
struct GachaPackTierShippingComparison: View {
    let tearProgress: CGFloat

    private let columns = [
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10)
    ]

    private var normalizedProgress: CGFloat {
        min(max(tearProgress, 0), 1)
    }

    private var stateTitle: String {
        normalizedProgress == 0
            ? "SEALED"
            : "TEAR \(Int((normalizedProgress * 100).rounded()))%"
    }

    private var visualScale: CGFloat {
        normalizedProgress == 0 ? 0.54 : 0.43
    }

    var body: some View {
        ZStack {
            ProductBackdrop().ignoresSafeArea()

            VStack(alignment: .leading, spacing: 13) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("PACK MATERIAL PROOF")
                        .font(.product(size: 21, relativeTo: .title3, weight: .semibold))
                    HStack(spacing: 7) {
                        Text("SHIPPING SWIFTUI · BODY + FLAP")
                            .foregroundStyle(Color.white.opacity(0.48))
                        Spacer(minLength: 8)
                        Text(stateTitle)
                            .foregroundStyle(Color.white.opacity(0.82))
                    }
                    .font(.product(size: 10, relativeTo: .caption2, weight: .medium))
                }

                LazyVGrid(columns: columns, spacing: 11) {
                    ForEach(GachaPackTier.allCases, id: \.rawValue) { tier in
                        VStack(spacing: 6) {
                            GachaPackVisual(tier: tier, tearProgress: normalizedProgress)
                                .frame(width: 244, height: 326)
                                .scaleEffect(visualScale)
                                .frame(width: 154, height: 185)

                            Text(tier.title)
                                .font(.product(size: 13, relativeTo: .caption, weight: .semibold))
                                .foregroundStyle(Color.white.opacity(0.88))
                                .lineLimit(1)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 7)
                        .background(
                            Color.white.opacity(0.025),
                            in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                        .accessibilityElement(children: .combine)
                        .accessibilityLabel("\(tier.title) Pack, \(stateTitle)")
                        .accessibilityIdentifier("gacha-pack-tier-\(tier.rawValue)")
                    }
                }

                HStack(spacing: 7) {
                    Circle()
                        .fill(Color.green.opacity(0.78))
                        .frame(width: 6, height: 6)
                    Text("EXACT GachaPackVisual · IDENTICAL SCALE PER TIER")
                        .font(.product(size: 9, relativeTo: .caption2, weight: .medium))
                        .foregroundStyle(Color.white.opacity(0.42))
                }
            }
            .padding(.horizontal, 17)
            .padding(.top, 12)
            .padding(.bottom, 10)
        }
        .productDesignSystem()
        .productStaticSurfaceMode()
        .accessibilityIdentifier("gacha-pack-six-tier-shipping-comparison")
    }
}
#endif

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

/// A restrained gacha "legendary pull" card treatment: a diagonal shimmer
/// sweep plus two corner sparkles in the featured item's rarity tint. Layered
/// above the product photo and below its text, purely decorative chrome.
private struct GachaRarityCardGlints: View {
    let tint: Color

    var body: some View {
        GeometryReader { proxy in
            let size = proxy.size
            ZStack {
                LinearGradient(
                    colors: [.clear, Color.white.opacity(0.20), .clear],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing)
                    .rotationEffect(.degrees(22))
                    .frame(width: size.width * 1.6, height: size.height * 0.55)
                    .position(x: size.width * 0.24, y: size.height * 0.26)
                    .blendMode(.screen)

                Image(systemName: "sparkle")
                    .font(.product(size: 13, weight: .semibold))
                    .foregroundStyle(tint.opacity(0.65))
                    .position(x: size.width - 24, y: 24)
            }
        }
        .allowsHitTesting(false)
        .accessibilityHidden(true)
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
