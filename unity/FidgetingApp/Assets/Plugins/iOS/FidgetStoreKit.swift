import Foundation
import Combine
import StoreKit
import SwiftUI

// MARK: - Unity bridge (send)

@_silgen_name("UnitySendMessage")
private func StoreKitUnitySendMessage(
    _ objectName: UnsafePointer<CChar>,
    _ methodName: UnsafePointer<CChar>,
    _ message: UnsafePointer<CChar>)

private enum StoreKitUnityBridge {
    static func send(_ method: String, value: String = "") {
        "FidgetApp".withCString { objectName in
            method.withCString { methodName in
                value.withCString { message in
                    StoreKitUnitySendMessage(objectName, methodName, message)
                }
            }
        }
    }
}

// MARK: - Catalog

/// Product identifiers registered in App Store Connect. Coin amounts are the
/// single Swift-side source of truth for what a verified purchase credits;
/// Unity's inventory only ever receives already-verified credits.
public enum GachaIapProduct: String, CaseIterable {
    case coinsSmall = "com.jiaweizhou.fidgetspinner.codex.coins.small"
    case coinsMedium = "com.jiaweizhou.fidgetspinner.codex.coins.medium"
    case coinsLarge = "com.jiaweizhou.fidgetspinner.codex.coins.large"
    case monthlyPass = "com.jiaweizhou.fidgetspinner.codex.pass.monthly"

    var coinAmount: Int {
        switch self {
        case .coinsSmall: return 480
        case .coinsMedium: return 1640
        case .coinsLarge: return 3360
        case .monthlyPass: return 0
        }
    }

    var isConsumable: Bool { self != .monthlyPass }
}

// MARK: - StoreKit 2 runtime

@MainActor
public final class GachaStoreKit: ObservableObject {
    public static let shared = GachaStoreKit()

    @Published public private(set) var products: [Product] = []
    @Published public private(set) var monthlyPassActive = false
    @Published public private(set) var busy = false
    @Published public private(set) var lastError = ""

    private var updatesTask: Task<Void, Never>?
    private let dailyTicketKey = "fidgeting.gacha.pass.lastDailyTicketGrant"

    /// Call once from the overlay when the store surface first appears.
    public func start() {
        guard updatesTask == nil else { return }
        updatesTask = Task { [weak self] in
            for await update in StoreKit.Transaction.updates {
                await self?.handle(update: update)
            }
        }
        Task { await loadProducts() }
        Task { await refreshEntitlements() }
    }

    public func loadProducts() async {
        do {
            let identifiers = GachaIapProduct.allCases.map(\.rawValue)
            products = try await Product.products(for: identifiers)
                .sorted { $0.price < $1.price }
            lastError = ""
        } catch {
            lastError = "load-products-failed"
        }
    }

    public func purchase(_ product: Product) async {
        busy = true
        defer { busy = false }
        do {
            let result = try await product.purchase()
            switch result {
            case .success(let verification):
                await handle(update: verification)
            case .userCancelled, .pending:
                break
            @unknown default:
                break
            }
        } catch {
            lastError = "purchase-failed"
        }
    }

    /// Restore is a pass over current entitlements; consumables are finished
    /// at credit time and never reappear here.
    public func restore() async {
        busy = true
        defer { busy = false }
        try? await AppStore.sync()
        await refreshEntitlements()
    }

    public func refreshEntitlements() async {
        var passActive = false
        for await entitlement in StoreKit.Transaction.currentEntitlements {
            guard case .verified(let transaction) = entitlement else { continue }
            if transaction.productID == GachaIapProduct.monthlyPass.rawValue,
                transaction.revocationDate == nil {
                passActive = true
            }
        }
        monthlyPassActive = passActive
        grantDailyPassTicketIfDue()
    }

    private func handle(update: VerificationResult<StoreKit.Transaction>) async {
        guard case .verified(let transaction) = update else {
            lastError = "verification-failed"
            return
        }

        guard let product = GachaIapProduct(rawValue: transaction.productID) else {
            await transaction.finish()
            return
        }

        if transaction.revocationDate != nil {
            if product == .monthlyPass {
                monthlyPassActive = false
            }
            await transaction.finish()
            return
        }

        if product.isConsumable {
            // Credit only after verification, then finish so the consumable
            // cannot be replayed on a later launch.
            StoreKitUnityBridge.send(
                "CreditGachaFundsFromNativeUi",
                value: "coins|\(product.coinAmount)")
        } else {
            monthlyPassActive = true
            grantDailyPassTicketIfDue()
        }

        await transaction.finish()
        lastError = ""
    }

    /// The monthly pass grants one draw ticket per calendar day. The grant is
    /// keyed to the local date so backgrounding or relaunching cannot
    /// double-grant, and it deliberately never touches XP or physics.
    public func grantDailyPassTicketIfDue() {
        guard monthlyPassActive else { return }
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        formatter.locale = Locale(identifier: "en_US_POSIX")
        let today = formatter.string(from: Date())
        let defaults = UserDefaults.standard
        guard defaults.string(forKey: dailyTicketKey) != today else { return }
        defaults.set(today, forKey: dailyTicketKey)
        StoreKitUnityBridge.send("CreditGachaFundsFromNativeUi", value: "tickets|1")
    }
}

// MARK: - Coin shop view

public struct GachaCoinShopView: View {
    @ObservedObject private var storeKit = GachaStoreKit.shared

    public init() {}

    public var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("齿轮币")
                .font(.headline)
                .foregroundColor(.white)
            if storeKit.products.isEmpty {
                HStack {
                    ProgressView().tint(.white)
                    Text("正在连接 App Store…")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.55))
                }
            } else {
                ForEach(storeKit.products, id: \.id) { product in
                    productRow(product)
                }
            }
            Button {
                Task { await storeKit.restore() }
            } label: {
                Text("恢复购买")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
            }
            .padding(.top, 2)
            if !storeKit.lastError.isEmpty {
                Text("出了点问题，请稍后再试")
                    .font(.caption2)
                    .foregroundColor(.red.opacity(0.8))
            }
        }
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20))
        .onAppear { storeKit.start() }
        .disabled(storeKit.busy)
    }

    private func productRow(_ product: Product) -> some View {
        let catalogEntry = GachaIapProduct(rawValue: product.id)
        let isPass = catalogEntry == .monthlyPass
        return HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text(product.displayName.isEmpty
                    ? fallbackName(for: catalogEntry)
                    : product.displayName)
                    .font(.subheadline)
                    .foregroundColor(.white)
                Text(isPass
                    ? "每日 1 张抽取券 · 不改变任何盘玩收益"
                    : "+\(catalogEntry?.coinAmount ?? 0) 齿轮币")
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.5))
            }
            Spacer()
            if isPass && storeKit.monthlyPassActive {
                Text("已开通")
                    .font(.caption.bold())
                    .foregroundColor(.white.opacity(0.6))
            } else {
                Button {
                    Task { await storeKit.purchase(product) }
                } label: {
                    Text(product.displayPrice)
                        .font(.caption.bold())
                        .foregroundColor(.black)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.white, in: Capsule())
                }
            }
        }
    }

    private func fallbackName(for product: GachaIapProduct?) -> String {
        switch product {
        case .coinsSmall: return "齿轮币 · 小"
        case .coinsMedium: return "齿轮币 · 中"
        case .coinsLarge: return "齿轮币 · 大"
        case .monthlyPass: return "藏家月卡"
        case nil: return "商品"
        }
    }
}
