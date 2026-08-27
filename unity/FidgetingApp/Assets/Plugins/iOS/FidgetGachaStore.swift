import Foundation
import SwiftUI

// MARK: - Unity bridge (send)

@_silgen_name("UnitySendMessage")
private func GachaUnitySendMessage(
    _ objectName: UnsafePointer<CChar>,
    _ methodName: UnsafePointer<CChar>,
    _ message: UnsafePointer<CChar>)

private enum GachaUnityBridge {
    static func send(_ method: String, value: String = "") {
        "FidgetApp".withCString { objectName in
            method.withCString { methodName in
                value.withCString { message in
                    GachaUnitySendMessage(objectName, methodName, message)
                }
            }
        }
    }
}

@MainActor
enum GachaShippingRevealContinuation {
    static var preparePremiumDisplayCase:
        ((_ requestID: String, _ receipt: GachaReceiptRow) -> Void)?
    static var cancelPreparedDisplayCase: (() -> Void)?
}

// MARK: - Model

public enum GachaRarityTier: Int, CaseIterable {
    case standard = 0
    case refined = 1
    case signature = 2
    case heirloom = 3

    var title: String {
        switch self {
        case .standard: return "标准"
        case .refined: return "精制"
        case .signature: return "臻藏"
        case .heirloom: return "传世"
        }
    }

    /// Lining-language colors mirroring GachaRevealRules.
    var tint: Color {
        switch self {
        case .standard: return Color(red: 0.55, green: 0.55, blue: 0.58)
        case .refined: return Color(red: 0.45, green: 0.62, blue: 0.85)
        case .signature: return Color(red: 0.85, green: 0.55, blue: 0.30)
        case .heirloom: return Color(red: 0.55, green: 0.90, blue: 0.95)
        }
    }

    /// Display mirror of GachaEconomyRules.RedeemShardCost; Unity enforces.
    var redeemCost: Int? {
        switch self {
        case .standard: return 4
        case .refined: return 12
        case .signature: return 60
        case .heirloom: return nil
        }
    }
}

public struct GachaSeriesInfo: Equatable {
    public let id: String
    public let name: String
    public let rates: [Double]
}

public struct GachaPrizeInfo: Equatable, Identifiable {
    public let id: String
    public let seriesId: String
    public let rarity: GachaRarityTier
    public let kindIndex: Int
    public let name: String

    var kindTitle: String {
        switch kindIndex {
        case 1: return "贴纸"
        case 2: return "展示底座"
        case 3: return "环境色调"
        case 4: return "指尖玩具"
        default: return "限定皮肤"
        }
    }
}

public struct GachaReceiptRow: Equatable, Identifiable {
    public let id = UUID()
    public let prizeId: String
    public let name: String
    public let rarity: GachaRarityTier
    public let isNew: Bool
    public let shardsGained: Int
    public let forcedBySignaturePity: Bool
    public let forcedByHeirloomPity: Bool
    public let forcedByTenDraw: Bool
    public let firstObtainedAtUtc: String
}

@MainActor
public final class GachaStoreModel: ObservableObject {
    public static let shared = GachaStoreModel()

    @Published public private(set) var series: [GachaSeriesInfo] = []
    @Published public private(set) var prizes: [GachaPrizeInfo] = []
    @Published public private(set) var tickets = 0
    @Published public private(set) var coins = 0
    @Published public private(set) var shardsBySeries: [String: Int] = [:]
    @Published public private(set) var signatureMisses: [String: Int] = [:]
    @Published public private(set) var heirloomMisses: [String: Int] = [:]
    @Published public private(set) var totalDraws: [String: Int] = [:]
    @Published public private(set) var owned: Set<String> = []
    @Published public private(set) var firstObtainedAtUtcByPrize: [String: String] = [:]
    @Published public var pendingReceipt: [GachaReceiptRow] = []
    @Published public private(set) var pendingReceiptRequestID = ""
    @Published public var lastFailureReason = ""
    @Published public private(set) var lastFailureRequestID = ""
    @Published public private(set) var revealRequestID = ""
    @Published public private(set) var revealSetupSucceeded = false
    @Published public private(set) var revealSetupFailure = ""
    @Published public private(set) var revealPhase = "idle"
    @Published public private(set) var revealPhaseFailure = ""

    public var revealIsComplete: Bool {
        revealPhase == "complete" && revealPhaseFailure.isEmpty
    }

    public func requestState() {
#if DEBUG
        let fundingArgument =
            "--preview-gacha-funding-token=metal-three-blade-v1"
        if ProcessInfo.processInfo.arguments.contains(fundingArgument) {
            GachaUnityBridge.send(
                "RequestGachaStateFromNativeUi",
                value: "metal-three-blade-v1")
            return
        }
#endif
        GachaUnityBridge.send("RequestGachaStateFromNativeUi")
    }

    public func draw(
        requestID: UUID,
        seriesId: String,
        count: Int,
        useCoins: Bool
    ) {
        var payload =
            "\(requestID.uuidString.lowercased())|\(seriesId)|\(count)|\(useCoins ? "coin" : "ticket")"
#if DEBUG
        if ProcessInfo.processInfo.arguments.contains(
            "--preview-authoritative-metal-three-blade") {
            payload += "|preview-metal-three-blade"
        }
#endif
        GachaUnityBridge.send(
            "DrawGachaFromNativeUi",
            value: payload)
    }

    public func draw(seriesId: String, count: Int, useCoins: Bool) {
        draw(
            requestID: UUID(),
            seriesId: seriesId,
            count: count,
            useCoins: useCoins)
    }

    public func requestReceipt(requestID: UUID) {
        GachaUnityBridge.send(
            "RequestGachaReceiptFromNativeUi",
            value: requestID.uuidString.lowercased())
    }

    public func acknowledgeReceipt(requestID: UUID) {
        GachaUnityBridge.send(
            "AcknowledgeGachaReceiptFromNativeUi",
            value: requestID.uuidString.lowercased())
        pendingReceipt = []
        pendingReceiptRequestID = ""
        lastFailureReason = ""
        lastFailureRequestID = ""
        resetRevealPresentation()
    }

    public func beginRevealSetup(requestID: String) {
        revealRequestID = requestID.lowercased()
        revealSetupSucceeded = false
        revealSetupFailure = ""
        revealPhase = "preparing"
        revealPhaseFailure = ""
    }

    public func resetRevealPresentation() {
        revealRequestID = ""
        revealSetupSucceeded = false
        revealSetupFailure = ""
        revealPhase = "idle"
        revealPhaseFailure = ""
    }

    fileprivate func ingestRevealSetup(
        requestID: String,
        succeeded: Bool,
        failureReason: String
    ) {
        let normalized = requestID.lowercased()
        guard normalized == revealRequestID else { return }
        revealSetupSucceeded = succeeded
        revealSetupFailure = failureReason
        if !succeeded {
            revealPhase = "idle"
        }
    }

    fileprivate func ingestRevealPhase(
        requestID: String,
        phase: String,
        failureReason: String
    ) {
        let normalized = requestID.lowercased()
        guard normalized == revealRequestID else { return }
        revealPhase = phase
        revealPhaseFailure = failureReason
    }

    public func redeem(prizeId: String) {
        GachaUnityBridge.send("RedeemGachaShardsFromNativeUi", value: prizeId)
    }

    // MARK: TSV ingestion (called from the Unity bridge)

    public func ingest(catalog: String, snapshot: String, receipt: String) {
        if !catalog.isEmpty { parseCatalog(catalog) }
        if !snapshot.isEmpty { parseSnapshot(snapshot) }
        parseReceipt(receipt)
    }

    private func parseCatalog(_ payload: String) {
        var nextSeries: [GachaSeriesInfo] = []
        var nextPrizes: [GachaPrizeInfo] = []
        for line in payload.split(separator: "\n") {
            let cells = line.split(separator: "\t", omittingEmptySubsequences: false)
                .map(String.init)
            if cells.count >= 7, cells[0] == "series" {
                nextSeries.append(GachaSeriesInfo(
                    id: cells[1],
                    name: cells[2],
                    rates: cells[3...6].map { Double($0) ?? 0 }))
            } else if cells.count >= 6, cells[0] == "prize" {
                nextPrizes.append(GachaPrizeInfo(
                    id: cells[1],
                    seriesId: cells[2],
                    rarity: GachaRarityTier(rawValue: Int(cells[3]) ?? 0) ?? .standard,
                    kindIndex: Int(cells[4]) ?? 0,
                    name: cells[5]))
            }
        }
        series = nextSeries
        prizes = nextPrizes
    }

    private func parseSnapshot(_ payload: String) {
        for line in payload.split(separator: "\n") {
            let cells = line.split(separator: "\t", omittingEmptySubsequences: false)
                .map(String.init)
            if cells.count >= 3, cells[0] == "wallet" {
                tickets = Int(cells[1]) ?? 0
                coins = Int(cells[2]) ?? 0
            } else if cells.count >= 6, cells[0] == "series-state" {
                signatureMisses[cells[1]] = Int(cells[2]) ?? 0
                heirloomMisses[cells[1]] = Int(cells[3]) ?? 0
                shardsBySeries[cells[1]] = Int(cells[4]) ?? 0
                totalDraws[cells[1]] = Int(cells[5]) ?? 0
            } else if cells.count >= 3, cells[0] == "owned-meta" {
                firstObtainedAtUtcByPrize[cells[1]] = cells[2]
            } else if cells.count >= 2, cells[0] == "owned" {
                owned = Set(cells[1].split(separator: "|").map(String.init))
                firstObtainedAtUtcByPrize = firstObtainedAtUtcByPrize.filter {
                    owned.contains($0.key)
                }
            } else if cells.count >= 1, cells[0] == "owned" {
                owned = []
                firstObtainedAtUtcByPrize = [:]
            }
        }
    }

    private func parseReceipt(_ payload: String) {
        guard !payload.isEmpty else { return }
        var rows: [GachaReceiptRow] = []
        var failure = ""
        var requestID = ""
        for line in payload.split(separator: "\n") {
            let cells = line.split(separator: "\t", omittingEmptySubsequences: false)
                .map(String.init)
            if cells.count >= 3, cells[0] == "result" {
                requestID = cells[1].lowercased()
                failure = cells[2] == "ok" ? "" : cells[2]
            } else if cells.count >= 2, cells[0] == "result" {
                // Compatibility with pre-request-id receipts used by old builds.
                failure = cells[1] == "ok" ? "" : cells[1]
            } else if cells.count >= 10, cells[0] == "row" {
                rows.append(GachaReceiptRow(
                    prizeId: cells[1],
                    name: cells[2],
                    rarity: GachaRarityTier(rawValue: Int(cells[3]) ?? 0) ?? .standard,
                    isNew: cells[5] == "1",
                    shardsGained: Int(cells[6]) ?? 0,
                    forcedBySignaturePity: cells[7] == "1",
                    forcedByHeirloomPity: cells[8] == "1",
                    forcedByTenDraw: cells[9] == "1",
                    firstObtainedAtUtc: cells.count >= 11 ? cells[10] : ""))
            }
        }
        lastFailureReason = failure
        lastFailureRequestID = failure.isEmpty ? "" : requestID
        // A non-empty receipt payload is authoritative for the latest request.
        // Clear stale rows on failures as well as replacing them on success.
        pendingReceipt = rows
        pendingReceiptRequestID = rows.isEmpty ? "" : requestID
    }
}

@_cdecl("CodexGachaReceiveState")
public func CodexGachaReceiveState(
    _ catalogPayload: UnsafePointer<CChar>?,
    _ snapshotPayload: UnsafePointer<CChar>?,
    _ receiptPayload: UnsafePointer<CChar>?) {
    let catalog = catalogPayload.map { String(cString: $0) } ?? ""
    let snapshot = snapshotPayload.map { String(cString: $0) } ?? ""
    let receipt = receiptPayload.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.ingest(
            catalog: catalog,
            snapshot: snapshot,
            receipt: receipt)
    }
}

@_cdecl("CodexGachaRevealReceiveSetup")
public func CodexGachaRevealReceiveSetup(
    _ requestID: UnsafePointer<CChar>?,
    _ succeeded: Int32,
    _ failureReason: UnsafePointer<CChar>?) {
    let request = requestID.map { String(cString: $0) } ?? ""
    let failure = failureReason.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.ingestRevealSetup(
            requestID: request,
            succeeded: succeeded != 0,
            failureReason: failure)
    }
}

@_cdecl("CodexGachaRevealReceivePhase")
public func CodexGachaRevealReceivePhase(
    _ requestID: UnsafePointer<CChar>?,
    _ phase: UnsafePointer<CChar>?,
    _ failureReason: UnsafePointer<CChar>?) {
    let request = requestID.map { String(cString: $0) } ?? ""
    let phaseToken = phase.map { String(cString: $0) } ?? "idle"
    let failure = failureReason.map { String(cString: $0) } ?? ""
    Task { @MainActor in
        GachaStoreModel.shared.ingestRevealPhase(
            requestID: request,
            phase: phaseToken,
            failureReason: failure)
    }
}

// MARK: - Store view

struct LegacyGachaStoreView: View {
    @ObservedObject private var model = GachaStoreModel.shared
    @State private var showOdds = false
    @State private var showResults = false

    public init() {}

    private var activeSeries: GachaSeriesInfo? { model.series.first }

    public var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            ScrollView {
                VStack(spacing: 14) {
                    walletHeader
                    if let series = activeSeries {
                        seriesBanner(series)
                        pityCard(series)
                        drawButtons(series)
                        GachaCoinShopView()
                        redeemShop(series)
                        collectionGrid(series)
                    } else {
                        ProgressView().tint(.white).padding(.top, 80)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 24)
            }
        }
        .onAppear { model.requestState() }
        .onChange(of: model.pendingReceipt) { rows in
            showResults = !rows.isEmpty
        }
        .sheet(isPresented: $showOdds) { oddsSheet }
        .sheet(isPresented: $showResults) {
            resultsSheet
        }
    }

    private var walletHeader: some View {
        HStack(spacing: 10) {
            walletChip(icon: "ticket", value: model.tickets, label: "抽取券")
            walletChip(icon: "gearshape.2", value: model.coins, label: "齿轮币")
            Spacer()
            Button {
                showOdds = true
            } label: {
                Label("概率公示", systemImage: "doc.text.magnifyingglass")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
            }
        }
        .padding(.top, 12)
    }

    private func walletChip(icon: String, value: Int, label: String) -> some View {
        HStack(spacing: 6) {
            Image(systemName: icon).font(.caption)
            Text("\(value)")
                .font(.product(.subheadline, weight: .bold).monospacedDigit())
            Text(label).font(.caption2).opacity(0.7)
        }
        .foregroundColor(.white)
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(.ultraThinMaterial, in: Capsule())
    }

    private func seriesBanner(_ series: GachaSeriesInfo) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("当前系列")
                .font(.caption2)
                .foregroundColor(.white.opacity(0.55))
            Text(series.name)
                .font(.title2.bold())
                .foregroundColor(.white)
            Text("盲盒限定外观 · 不含任何成长或物理加成")
                .font(.caption)
                .foregroundColor(.white.opacity(0.6))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private func pityCard(_ series: GachaSeriesInfo) -> some View {
        let signatureMisses = model.signatureMisses[series.id] ?? 0
        let heirloomMisses = model.heirloomMisses[series.id] ?? 0
        return VStack(spacing: 10) {
            pityRow(
                title: "臻藏保底",
                tint: GachaRarityTier.signature.tint,
                current: signatureMisses,
                target: 50,
                caption: "50 次未出即第 51 抽必得臻藏或更高")
            pityRow(
                title: "传世保底",
                tint: GachaRarityTier.heirloom.tint,
                current: heirloomMisses,
                target: 89,
                caption: "累计 90 抽内必得传世")
        }
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private func pityRow(
        title: String,
        tint: Color,
        current: Int,
        target: Int,
        caption: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(title).font(.caption.bold()).foregroundColor(.white)
                Spacer()
                Text("\(current) / \(target + 1)")
                    .font(.product(.caption).monospacedDigit())
                    .foregroundColor(tint)
            }
            ProgressView(value: Double(min(current, target)), total: Double(target))
                .tint(tint)
            Text(caption)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.45))
        }
    }

    private func drawButtons(_ series: GachaSeriesInfo) -> some View {
        HStack(spacing: 12) {
            drawButton(
                title: "单抽",
                subtitle: "1 券 / 160 币",
                seriesId: series.id,
                count: 1)
            drawButton(
                title: "十连",
                subtitle: "10 券 / 1440 币 · 必出精制+",
                seriesId: series.id,
                count: 10)
        }
    }

    private func drawButton(
        title: String,
        subtitle: String,
        seriesId: String,
        count: Int) -> some View {
        Button {
            let ticketCost = count
            model.draw(
                seriesId: seriesId,
                count: count,
                useCoins: model.tickets < ticketCost)
        } label: {
            VStack(spacing: 4) {
                Text(title).font(.headline)
                Text(subtitle).font(.caption2).opacity(0.65)
            }
            .foregroundColor(.black)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(Color.white, in: RoundedRectangle(cornerRadius: 16))
        }
    }

    private func redeemShop(_ series: GachaSeriesInfo) -> some View {
        let shards = model.shardsBySeries[series.id] ?? 0
        let redeemables = model.prizes.filter {
            $0.seriesId == series.id
                && !model.owned.contains($0.id)
                && $0.rarity.redeemCost != nil
        }
        return VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("兑换所").font(.headline).foregroundColor(.white)
                Spacer()
                Label("\(shards)", systemImage: "sparkles")
                    .font(.product(.caption).monospacedDigit())
                    .foregroundColor(.white.opacity(0.8))
            }
            if redeemables.isEmpty {
                Text("本系列可兑换奖品均已入库")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.5))
            } else {
                ForEach(redeemables) { prize in
                    redeemRow(prize: prize, shards: shards)
                }
            }
        }
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private func redeemRow(prize: GachaPrizeInfo, shards: Int) -> some View {
        let cost = prize.rarity.redeemCost ?? Int.max
        return HStack {
            Circle().fill(prize.rarity.tint).frame(width: 8, height: 8)
            VStack(alignment: .leading, spacing: 2) {
                Text(prize.name).font(.subheadline).foregroundColor(.white)
                Text("\(prize.rarity.title) · \(prize.kindTitle)")
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.5))
            }
            Spacer()
            Button {
                model.redeem(prizeId: prize.id)
            } label: {
                Label("\(cost)", systemImage: "sparkles")
                    .font(.caption.bold())
                    .foregroundColor(shards >= cost ? .black : .white.opacity(0.35))
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(
                        shards >= cost ? Color.white : Color.white.opacity(0.08),
                        in: Capsule())
            }
            .disabled(shards < cost)
        }
    }

    private func collectionGrid(_ series: GachaSeriesInfo) -> some View {
        let seriesPrizes = model.prizes.filter { $0.seriesId == series.id }
        let columns = [GridItem(.adaptive(minimum: 150), spacing: 10)]
        return VStack(alignment: .leading, spacing: 10) {
            Text("收藏库 \(seriesPrizes.filter { model.owned.contains($0.id) }.count)"
                + " / \(seriesPrizes.count)")
                .font(.headline)
                .foregroundColor(.white)
            LazyVGrid(columns: columns, spacing: 10) {
                ForEach(seriesPrizes) { prize in
                    collectionCell(prize)
                }
            }
        }
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }

    private func collectionCell(_ prize: GachaPrizeInfo) -> some View {
        let isOwned = model.owned.contains(prize.id)
        return VStack(alignment: .leading, spacing: 4) {
            HStack {
                Circle().fill(prize.rarity.tint).frame(width: 8, height: 8)
                Text(prize.rarity.title)
                    .font(.caption2)
                    .foregroundColor(prize.rarity.tint)
                Spacer()
                Image(systemName: isOwned ? "checkmark.seal.fill" : "lock")
                    .font(.caption2)
                    .foregroundColor(isOwned ? prize.rarity.tint : .white.opacity(0.3))
            }
            Text(prize.name)
                .font(.footnote.bold())
                .foregroundColor(isOwned ? .white : .white.opacity(0.45))
            Text(prize.kindTitle)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.4))
        }
        .padding(10)
        .background(
            Color.white.opacity(isOwned ? 0.10 : 0.04),
            in: RoundedRectangle(cornerRadius: 12))
    }

    private var oddsSheet: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    Text("概率公示")
                        .font(.title3.bold())
                        .foregroundColor(.white)
                    if let series = activeSeries {
                        ForEach(GachaRarityTier.allCases, id: \.rawValue) { tier in
                            HStack {
                                Circle().fill(tier.tint).frame(width: 8, height: 8)
                                Text(tier.title).foregroundColor(.white)
                                Spacer()
                                Text(String(
                                    format: "%.2f%%",
                                    (series.rates[safe: tier.rawValue] ?? 0) * 100))
                                    .font(.product(.body).monospacedDigit())
                                    .foregroundColor(tier.tint)
                            }
                            .font(.subheadline)
                        }
                    }
                    Divider().background(Color.white.opacity(0.2))
                    Group {
                        Text("· 十连抽保证至少 1 件精制或更高品质")
                        Text("· 连续 40 抽未出臻藏后，臻藏概率逐抽提升；第 51 抽必得臻藏或更高")
                        Text("· 累计 90 抽内必得传世")
                        Text("· 重复奖品自动转换为合金屑，可在兑换所直接兑换指定奖品")
                        Text("· 全部奖品仅为外观与收藏用途，不改变任何玩具的物理手感、成长速度或经验")
                    }
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
                }
                .padding(20)
            }
        }
    }

    private var resultsSheet: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            VStack(spacing: 12) {
                Text("揭晓结果")
                    .font(.title3.bold())
                    .foregroundColor(.white)
                    .padding(.top, 18)
                ScrollView {
                    VStack(spacing: 8) {
                        ForEach(model.pendingReceipt) { row in
                            receiptRow(row)
                        }
                    }
                    .padding(.horizontal, 16)
                }
                Button {
                    model.pendingReceipt = []
                    showResults = false
                } label: {
                    Text("收入囊中")
                        .font(.headline)
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.white, in: RoundedRectangle(cornerRadius: 16))
                }
                .padding(16)
            }
        }
    }

    private func receiptRow(_ row: GachaReceiptRow) -> some View {
        HStack {
            Circle().fill(row.rarity.tint).frame(width: 10, height: 10)
            VStack(alignment: .leading, spacing: 2) {
                Text(row.name).font(.subheadline.bold()).foregroundColor(.white)
                HStack(spacing: 6) {
                    Text(row.rarity.title)
                        .font(.caption2)
                        .foregroundColor(row.rarity.tint)
                    if row.forcedBySignaturePity || row.forcedByHeirloomPity {
                        Text("保底")
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.6))
                    }
                    if row.forcedByTenDraw {
                        Text("十连保障")
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.6))
                    }
                }
            }
            Spacer()
            if row.isNew {
                Text("NEW")
                    .font(.caption2.bold())
                    .foregroundColor(.black)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(row.rarity.tint, in: Capsule())
            } else {
                Label("+\(row.shardsGained)", systemImage: "sparkles")
                    .font(.caption.bold())
                    .foregroundColor(.white.opacity(0.75))
            }
        }
        .padding(12)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 14))
    }
}

private extension Array where Element == Double {
    subscript(safe index: Int) -> Double? {
        indices.contains(index) ? self[index] : nil
    }
}
