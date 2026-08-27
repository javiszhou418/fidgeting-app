import Foundation
import QuartzCore
import SwiftUI
import UIKit

@_silgen_name("UnitySendMessage")
private func UnitySendMessage(
    _ objectName: UnsafePointer<CChar>,
    _ methodName: UnsafePointer<CChar>,
    _ message: UnsafePointer<CChar>)

private enum UnityBridge {
    static let hapticsEnabledKey = "fidgeting.settings.hapticsEnabled"
    static let hapticIntensityKey = "fidgeting.settings.hapticIntensity"

    static func send(_ method: String, value: String = "") {
        "FidgetApp".withCString { objectName in
            method.withCString { methodName in
                value.withCString { message in
                    UnitySendMessage(objectName, methodName, message)
                }
            }
        }
    }

    static func feedback(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .light) {
        let defaults = UserDefaults.standard
        let enabled = defaults.object(forKey: hapticsEnabledKey) == nil
            ? true
            : defaults.bool(forKey: hapticsEnabledKey)
        guard enabled else { return }

        let intensity = defaults.object(forKey: hapticIntensityKey) == nil
            ? 1.0
            : defaults.double(forKey: hapticIntensityKey)
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.prepare()
        generator.impactOccurred(intensity: CGFloat(max(0, min(1, intensity))))
    }
}

private enum ProductTab: Equatable {
    case spinners
    case collector
    case settings
}

private enum EnvironmentTheme: String, CaseIterable, Identifiable, Equatable {
    case adaptive
    case canyon
    case cyberpunk
    case mineralRidge = "mineral-ridge"

    var id: String { rawValue }

    var title: String {
        switch self {
        case .adaptive: return "随形微光"
        case .canyon: return "星岩峡谷"
        case .cyberpunk: return "霓虹都市"
        case .mineralRidge: return "矿脊台座"
        }
    }

    var subtitle: String {
        switch self {
        case .adaptive: return "深色底 · 随当前玩具偏色"
        case .canyon: return "粗粝岩层 · 双层星空"
        case .cyberpunk: return "未来建筑 · 霓虹纵深"
        case .mineralRidge: return "远景拼贴 · 不规则矿脊承托"
        }
    }

    func wallpaperAssetName(for model: SpinnerModel) -> String {
        "scene-wallpaper-\(rawValue)-\(model.rawValue)"
    }
}

private enum ProductAppearanceSection: String, CaseIterable, Identifiable, Equatable {
    case skins
    case stickers

    var id: String { rawValue }
    var title: String { self == .skins ? "皮肤" : "贴纸" }
    var symbol: String { self == .skins ? "paintbrush.fill" : "seal.fill" }
    var hint: String { "显示\(title)选择" }
}

private enum SpinnerInteractionMode: String, CaseIterable, Identifiable, Equatable {
    case smooth
    case ratchet

    var id: String { rawValue }
    var title: String { self == .smooth ? "平滑" : "棘轮" }
    var subtitle: String {
        self == .smooth ? "自由滑行" : "可调机械档位"
    }
    var symbol: String {
        self == .smooth ? "arrow.triangle.2.circlepath" : "gearshape.fill"
    }
}

private enum MotionSensitivityPreset: String, CaseIterable, Identifiable, Equatable {
    case low
    case medium
    case high

    var id: String { rawValue }

    var title: String {
        switch self {
        case .low: return "低"
        case .medium: return "中"
        case .high: return "高"
        }
    }

    var maximumInputAngle: Double {
        switch self {
        case .low: return 18
        case .medium: return 10
        case .high: return 7
        }
    }

    var motionResponse: Double {
        switch self {
        case .low: return 8
        case .medium: return 15
        case .high: return 22
        }
    }

    var gyroscopeLead: Double {
        switch self {
        case .low: return 0.035
        case .medium: return 0.060
        case .high: return 0.100
        }
    }

    var maximumMotionOrbit: Double {
        switch self {
        case .low: return 6.5
        case .medium: return 11
        case .high: return 16
        }
    }

    var parameterSummary: String {
        String(
            format: "Input %.0f° · Response %.0f · Gyro %.3f · Orbit %.1f°",
            maximumInputAngle,
            motionResponse,
            gyroscopeLead,
            maximumMotionOrbit)
    }

    static func closest(
        maximumInputAngle: Double,
        motionResponse: Double,
        gyroscopeLead: Double,
        maximumMotionOrbit: Double
    ) -> MotionSensitivityPreset {
        if maximumInputAngle <= 8
            || motionResponse >= 19
            || gyroscopeLead >= 0.085
            || maximumMotionOrbit >= 14 {
            return .high
        }
        if maximumInputAngle <= 13
            || motionResponse >= 11
            || gyroscopeLead >= 0.0475
            || maximumMotionOrbit >= 8.5 {
            return .medium
        }
        return .low
    }
}

private enum SpinnerModel: String, CaseIterable, Identifiable, Equatable {
    case pointedThreeBlade = "pointed-three-blade"
    case metalThreeBlade = "metal-three-blade"
    case goldFourWing = "gold-four-wing"
    case graphiteTwoLobe = "graphite-two-lobe"
    case magneticSlideTile = "magnetic-slide-tile"
    case magneticFanCard = "magnetic-fan-card"

    var id: String { rawValue }

    static let shippingCases: [SpinnerModel] = [
        .pointedThreeBlade,
        .metalThreeBlade,
        .goldFourWing,
        .graphiteTwoLobe,
        .magneticSlideTile,
        .magneticFanCard
    ]

    var title: String {
        switch self {
        case .pointedThreeBlade: return "三叶尖金属"
        case .metalThreeBlade: return "三叶金属"
        case .goldFourWing: return "镜钢四翼"
        case .graphiteTwoLobe: return "石墨双叶"
        case .magneticSlideTile: return "磁吸推牌"
        case .magneticFanCard: return "磁吸扇牌"
        }
    }

    var subtitle: String {
        switch self {
        case .pointedThreeBlade: return "锋锐轮廓 · 一体金属三叶"
        case .metalThreeBlade: return "精密结构 · 金属三叶模型"
        case .goldFourWing: return "镜面不锈钢 · 四翼模型"
        case .graphiteTwoLobe: return "50 mm 横杆 · 珠砂石墨金属"
        case .magneticSlideTile: return "侧推滑盖 · 磁吸限位"
        case .magneticFanCard: return "三层扇形 · 四档磁吸"
        }
    }

    var symbol: String {
        switch self {
        case .pointedThreeBlade: return "triangle.fill"
        case .metalThreeBlade: return "gearshape.2.fill"
        case .goldFourWing: return "sparkles"
        case .graphiteTwoLobe: return "capsule.fill"
        case .magneticSlideTile: return "rectangle.on.rectangle"
        case .magneticFanCard: return "square.stack.3d.up.fill"
        }
    }

    var thumbnailAssetName: String {
        "product-thumbnail-\(rawValue)"
    }

    var accent: Color {
        switch self {
        case .pointedThreeBlade: return Color(white: 0.82)
        case .metalThreeBlade: return Color(white: 0.72)
        case .goldFourWing: return Color(red: 0.72, green: 0.76, blue: 0.82)
        case .graphiteTwoLobe: return Color(red: 0.30, green: 0.32, blue: 0.34)
        case .magneticSlideTile: return Color(red: 0.36, green: 0.72, blue: 0.78)
        case .magneticFanCard: return Color(red: 0.72, green: 0.58, blue: 0.38)
        }
    }
}

private struct OfflineProgressionReward: Equatable {
    var model: SpinnerModel = .pointedThreeBlade
    var experience = 0.0
    var elapsedHours = 0.0
    var previousLevel = 1
    var newLevel = 1
    var previousLevelProgress = 0.0
    var newLevelProgress = 0.0
    var assistantEnabled = false
}

private struct LiveProgressionLevelUp: Equatable {
    var previousLevel = 1
    var newLevel = 1
    var rewardName = "成长罐容量提升"
}

private struct ProgressionLevelDetail: Identifiable, Equatable {
    let level: Int
    let title: String
    let unlockName: String

    var id: Int { level }

    static let fallback: [ProgressionLevelDetail] = [
        .init(level: 1, title: "初转学徒", unlockName: "标准单列轴承与基础成长罐"),
        .init(level: 5, title: "磨合新手", unlockName: "磨合完成贴纸"),
        .init(level: 10, title: "夜光巡航者", unlockName: "夜光刻度"),
        .init(level: 20, title: "稳态工匠", unlockName: "精钢配重环与强化不锈钢"),
        .init(level: 35, title: "静音调校师", unlockName: "静音缓冲垫圈"),
        .init(level: 50, title: "双轴领航员", unlockName: "双列辅助轴承与精密轴承钢"),
        .init(level: 65, title: "蓝钢技师", unlockName: "蓝钢锁环"),
        .init(level: 75, title: "轻量竞速者", unlockName: "低阻保持架与航空钛合金"),
        .init(level: 90, title: "典藏大师", unlockName: "收藏铭牌"),
        .init(level: 100, title: "镜钢宗师", unlockName: "陶瓷主轴承与终极镜钢完成体")
    ]

    static func parse(_ payload: String) -> [ProgressionLevelDetail] {
        let parsed = payload.split(separator: "\n").compactMap { row -> ProgressionLevelDetail? in
            let fields = row.split(separator: "\t", omittingEmptySubsequences: false)
            guard fields.count == 3, let level = Int(fields[0]) else { return nil }
            return ProgressionLevelDetail(
                level: level,
                title: String(fields[1]),
                unlockName: String(fields[2]))
        }
        return parsed.isEmpty ? fallback : parsed
    }
}

private struct ThreeBladeMetalSkinDetail: Identifiable, Equatable {
    let id: String
    let level: Int
    let displayName: String
    let metalName: String
    let patternName: String
    let decorationName: String
    let modificationName: String
    let baseHex: String
    let accentHex: String

    var thumbnailAssetName: String {
        "skin-thumbnail-\(id)"
    }

    static func parse(_ payload: String) -> [ThreeBladeMetalSkinDetail] {
        return payload.split(separator: "\n").compactMap { row in
            let fields = row.split(separator: "\t", omittingEmptySubsequences: false)
            guard fields.count == 9, let level = Int(fields[1]) else { return nil }
            return ThreeBladeMetalSkinDetail(
                id: String(fields[0]),
                level: level,
                displayName: String(fields[2]),
                metalName: String(fields[3]),
                patternName: String(fields[4]),
                decorationName: String(fields[5]),
                modificationName: String(fields[6]),
                baseHex: String(fields[7]),
                accentHex: String(fields[8]))
        }
    }
}

private struct ProductStickerDetail: Identifiable, Equatable {
    let id: String
    let displayName: String
    let thumbnailAssetName: String
    let symbolName: String
    let tintHex: String

    static func parse(_ payload: String) -> [ProductStickerDetail] {
        return payload.split(separator: "\n").compactMap { row in
            let fields = row.split(separator: "\t", omittingEmptySubsequences: false)
            guard fields.count == 5 else { return nil }
            return ProductStickerDetail(
                id: String(fields[0]),
                displayName: String(fields[1]),
                thumbnailAssetName: String(fields[2]),
                symbolName: String(fields[3]),
                tintHex: String(fields[4]))
        }
    }
}

private extension Color {
    init(productHex: String) {
        let cleaned = productHex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var value: UInt64 = 0
        Scanner(string: cleaned).scanHexInt64(&value)
        let red = Double((value >> 16) & 0xFF) / 255.0
        let green = Double((value >> 8) & 0xFF) / 255.0
        let blue = Double(value & 0xFF) / 255.0
        self.init(red: red, green: green, blue: blue)
    }
}

private enum ProductBadgeScope: String, Decodable, CaseIterable, Identifiable {
    case toy = "Toy"
    case collector = "Collector"
    case challenge = "Challenge"
    case legacy = "Legacy"

    var id: String { rawValue }

    var title: String {
        switch self {
        case .toy: return "玩具"
        case .collector: return "藏家"
        case .challenge: return "挑战"
        case .legacy: return "Legacy"
        }
    }
}

private enum ProductBadgeGrade: String, Decodable, CaseIterable {
    case ignition = "Ignition"
    case overdrive = "Overdrive"
    case apex = "Apex"
    case singularity = "Singularity"
}

private enum ProductBadgeState: String, Decodable {
    case locked = "Locked"
    case inProgress = "InProgress"
    case hidden = "Hidden"
    case unlocked = "Unlocked"
}

private struct ProductBadgeCatalogEnvelope: Decodable {
    let version: Int
    let modelId: String?
    let shardBalance: Int?
    let badges: [ProductBadgeDetail]
}

private struct ProductBadgeDetail: Identifiable, Equatable, Decodable {
    let id: String
    let scope: ProductBadgeScope
    let category: String
    let mechanism: String
    let metric: String
    let currentValue: Double
    let targetValue: Double
    let progress: Double
    let state: ProductBadgeState
    let unlockedAtUtc: String
    let rewardClaimed: Bool
    let grade: ProductBadgeGrade
    let visibility: String
    let title: String
    let description: String
    let assetName: String
    let displayToken: String
    let displayUnit: String
    let shortName: String
    let experienceReward: Int
    let shardReward: Int
    let displayOrder: Int
    let cycleIndex: Int64

    var unlocked: Bool { state == .unlocked }
    var hidden: Bool { state == .hidden }
    var unlockIdentity: String {
        scope == .challenge ? "\(id)@\(cycleIndex)" : id
    }

    var tokenLine: String {
        displayUnit.isEmpty
            ? displayToken
            : "\(displayToken) \(displayUnit)"
    }

    static func parse(_ payload: String) -> [ProductBadgeDetail] {
        parseEnvelope(payload)?.badges ?? []
    }

    static func parseEnvelope(_ payload: String) -> ProductBadgeCatalogEnvelope? {
        guard payload.trimmingCharacters(in: .whitespacesAndNewlines)
            .hasPrefix("{") else { return nil }
        guard let data = payload.data(using: .utf8),
              let envelope = try? JSONDecoder().decode(
                ProductBadgeCatalogEnvelope.self,
                from: data),
              envelope.version == 2 else { return nil }
        return ProductBadgeCatalogEnvelope(
            version: envelope.version,
            modelId: envelope.modelId,
            shardBalance: envelope.shardBalance,
            badges: envelope.badges.sorted {
            if $0.scope == $1.scope { return $0.displayOrder < $1.displayOrder }
            return $0.scope.rawValue < $1.scope.rawValue
        })
    }
}

private struct ProductBadgeUnlockEvent: Identifiable, Equatable {
    let id: String
    let badge: ProductBadgeDetail
    let sourceTitle: String
}

private struct CollectorRankUp: Equatable {
    var previousRank = 1
    var newRank = 1
}

private struct ProgressionComboState: Equatable {
    var tier = 0
    var count = 0
    var title = ""
    var speed = 0.0
    var angularSpeedRadians = 0.0
    var intensity = 0.0
    var frequency = 0.0
    var experienceMultiplier = 1.0

    var isActive: Bool { tier > 0 && count >= 2 }
    var rpm: Double { abs(angularSpeedRadians) * 60.0 / (2.0 * .pi) }

    var accent: Color {
        switch tier {
        case 1: return Color(red: 0.20, green: 0.92, blue: 0.78)
        case 2: return Color(red: 1.00, green: 0.62, blue: 0.18)
        case 3: return Color(red: 1.00, green: 0.28, blue: 0.72)
        default: return .cyan
        }
    }
}

private enum ProductSpeedBand: Int, Equatable {
    case calm = 0
    case engaged = 1
    case fast = 2
    case peak = 3

    var title: String {
        switch self {
        case .calm: return "CALM"
        case .engaged: return "FLOW"
        case .fast: return "DRIVE"
        case .peak: return "PEAK"
        }
    }

    var accent: Color {
        switch self {
        case .calm: return Color.white.opacity(0.58)
        case .engaged: return Color(red: 0.20, green: 0.92, blue: 0.78)
        case .fast: return Color(red: 1.00, green: 0.62, blue: 0.18)
        case .peak: return Color(red: 1.00, green: 0.18, blue: 0.08)
        }
    }
}

private enum ProductMotionKind: Int, Equatable {
    case rotary = 0
    case linearPush = 1
    case fanCard = 2
}

private struct ProductMotionTelemetryState: Equatable {
    var available = false
    var kind = ProductMotionKind.rotary
    var normalizedSpeed = 0.0
    var angularSpeedRadians = 0.0
    var motionRate = 0.0
    var speedBand = ProductSpeedBand.calm
    var intensity = 0.0
    var frequency = 0.0

    var rpm: Double {
        abs(angularSpeedRadians) * 60.0 / (2.0 * .pi)
    }

    var displayedSpeed: Double {
        switch kind {
        case .rotary: return rpm
        case .linearPush, .fanCard: return motionRate
        }
    }

    var displayedUnit: String {
        switch kind {
        case .rotary: return "RPM"
        case .linearPush: return "MM/S"
        case .fanCard: return "°/S"
        }
    }

    var speedAccessibilityLabel: String {
        switch kind {
        case .rotary: return "转速"
        case .linearPush: return "推牌速度"
        case .fanCard: return "扇牌展开速度"
        }
    }
}

private struct SpinRewardState: Equatable {
    var kind = 0
    var title = "PERFECT SPIN"
    var subtitle = "力度 × 速度 × 圈数"
    var force = 0.0
    var peakAngularSpeedRadians = 0.0
    var revolutions = 0.0

    var rpm: Double {
        peakAngularSpeedRadians * 60.0 / (2.0 * .pi)
    }

    var accent: Color {
        switch kind {
        case 1: return Color(red: 0.28, green: 0.88, blue: 0.78)
        case 2: return Color(red: 1.00, green: 0.62, blue: 0.18)
        case 3: return Color(red: 0.32, green: 0.76, blue: 1.00)
        case 4: return Color(red: 0.70, green: 0.52, blue: 1.00)
        case 5: return Color(red: 1.00, green: 0.34, blue: 0.72)
        default: return .cyan
        }
    }
}

private enum HapticReturnWeight: String, CaseIterable, Identifiable {
    case soft
    case balanced
    case heavy

    var id: String { rawValue }

    var title: String {
        switch self {
        case .soft: return "轻"
        case .balanced: return "均衡"
        case .heavy: return "重"
        }
    }
}

private enum HapticWaveform: String, CaseIterable, Identifiable, Codable {
    case transient
    case continuous
    case hybrid

    var id: String { rawValue }

    var title: String {
        switch self {
        case .transient: return "瞬态"
        case .continuous: return "连续"
        case .hybrid: return "混合"
        }
    }

    var bridgeValue: Int {
        switch self {
        case .transient: return 0
        case .continuous: return 1
        case .hybrid: return 2
        }
    }
}

private enum EditableHapticSemantic: Int, CaseIterable, Identifiable, Codable {
    case selection = 0
    case tick = 1
    case breakaway = 2
    case capture = 3
    case released = 4
    case reversed = 5
    case reset = 6
    case preview = 12

    var id: Int { rawValue }

    static var generalTuningCases: [Self] {
        allCases.filter { $0 != .tick }
    }

    var title: String {
        switch self {
        case .selection: return "选择"
        case .tick: return "段落 Tick"
        case .breakaway: return "脱档 Breakaway"
        case .capture: return "吸附 Capture"
        case .released: return "松手 Release"
        case .reversed: return "反转制动"
        case .reset: return "复位"
        case .preview: return "试听"
        }
    }

    var explanation: String {
        switch self {
        case .selection: return "普通 UI 或模式选中的确认触点"
        case .tick: return "真实跨过一个机械档位时触发"
        case .breakaway: return "输入超过磁吸阈值并脱离当前档位"
        case .capture: return "低速回吸并最终停在最近档位"
        case .released: return "手指释放并进入自由滑行"
        case .reversed: return "反向输入触发制动与方向切换"
        case .reset: return "陀螺复位并回到零角速度"
        case .preview: return "设置页专用试听，不代表新的 Apple 事件类型"
        }
    }
}

private struct EditableHapticRecipe: Codable, Equatable {
    var waveform: HapticWaveform
    var intensity: Double
    var sharpness: Double
    var duration: Double
    var attack: Double
    var decay: Double
    var release: Double
    var sustained: Bool
    var endIntensity: Double
    var endSharpness: Double
    var pulseCount: Double
    var pulseInterval: Double
    var impactLayers: Double
    var dynamicIntensity: Double
    var dynamicSharpness: Double
    var dynamicAttack: Double
    var dynamicDecay: Double
    var dynamicRelease: Double

    static func recommended(for semantic: EditableHapticSemantic) -> Self {
        switch semantic {
        case .selection:
            return .init(
                waveform: .transient, intensity: 0.40, sharpness: 0.88,
                duration: 0.04, attack: 0, decay: 0.04, release: 0.03,
                sustained: false, endIntensity: 0.40, endSharpness: 0.88,
                pulseCount: 1, pulseInterval: 0.04, impactLayers: 1,
                dynamicIntensity: 1, dynamicSharpness: 0,
                dynamicAttack: 0, dynamicDecay: 0, dynamicRelease: 0)
        case .tick:
            return .init(
                waveform: .transient, intensity: 0.84, sharpness: 0.98,
                duration: 0.04, attack: 0, decay: 0.04, release: 0.03,
                sustained: false, endIntensity: 0.62, endSharpness: 0.82,
                pulseCount: 1, pulseInterval: 0.04, impactLayers: 1.65,
                dynamicIntensity: 1, dynamicSharpness: 0,
                dynamicAttack: 0, dynamicDecay: 0, dynamicRelease: 0)
        case .breakaway:
            return .init(
                waveform: .transient, intensity: 0.78, sharpness: 0.94,
                duration: 0.04, attack: 0, decay: 0.04, release: 0.03,
                sustained: false, endIntensity: 0.34, endSharpness: 0.68,
                pulseCount: 1, pulseInterval: 0.04, impactLayers: 1.55,
                dynamicIntensity: 1, dynamicSharpness: 0,
                dynamicAttack: 0, dynamicDecay: 0, dynamicRelease: 0)
        case .capture:
            return .init(
                waveform: .hybrid, intensity: 0.95, sharpness: 0.90,
                duration: 0.055, attack: 0, decay: 0.08, release: 0.03,
                sustained: false, endIntensity: 0.42, endSharpness: 0.58,
                pulseCount: 2, pulseInterval: 0.036, impactLayers: 1.75,
                dynamicIntensity: 1, dynamicSharpness: 0,
                dynamicAttack: 0, dynamicDecay: 0, dynamicRelease: 0)
        case .released:
            return .init(
                waveform: .transient, intensity: 0.55, sharpness: 0.62,
                duration: 0.04, attack: 0, decay: 0.04, release: 0.06,
                sustained: false, endIntensity: 0.24, endSharpness: 0.38,
                pulseCount: 1, pulseInterval: 0.04, impactLayers: 1,
                dynamicIntensity: 1, dynamicSharpness: 0,
                dynamicAttack: 0, dynamicDecay: 0, dynamicRelease: 0)
        case .reversed:
            return .init(
                waveform: .transient, intensity: 0.82, sharpness: 0.82,
                duration: 0.04, attack: 0, decay: 0.04, release: 0.03,
                sustained: false, endIntensity: 0.30, endSharpness: 0.44,
                pulseCount: 3, pulseInterval: 0.045, impactLayers: 1.55,
                dynamicIntensity: 1, dynamicSharpness: 0,
                dynamicAttack: 0, dynamicDecay: 0, dynamicRelease: 0)
        case .reset:
            return .init(
                waveform: .transient, intensity: 0.84, sharpness: 0.94,
                duration: 0.04, attack: 0, decay: 0.04, release: 0.03,
                sustained: false, endIntensity: 0.22, endSharpness: 1,
                pulseCount: 2, pulseInterval: 0.032, impactLayers: 1.45,
                dynamicIntensity: 1, dynamicSharpness: 0,
                dynamicAttack: 0, dynamicDecay: 0, dynamicRelease: 0)
        case .preview:
            return .init(
                waveform: .hybrid, intensity: 0.92, sharpness: 0.94,
                duration: 0.05, attack: 0, decay: 0.06, release: 0.03,
                sustained: false, endIntensity: 0.38, endSharpness: 0.60,
                pulseCount: 2, pulseInterval: 0.034, impactLayers: 1.65,
                dynamicIntensity: 1, dynamicSharpness: 0,
                dynamicAttack: 0, dynamicDecay: 0, dynamicRelease: 0)
        }
    }

    func bridgePayload(for semantic: EditableHapticSemantic) -> String {
        [
            String(semantic.rawValue),
            String(waveform.bridgeValue),
            String(intensity),
            String(sharpness),
            String(duration),
            String(attack),
            String(decay),
            String(release),
            sustained ? "1" : "0",
            String(endIntensity),
            String(endSharpness),
            String(Int(pulseCount.rounded())),
            String(pulseInterval),
            String(impactLayers),
            String(dynamicIntensity),
            String(dynamicSharpness),
            String(dynamicAttack),
            String(dynamicDecay),
            String(dynamicRelease)
        ].joined(separator: "|")
    }
}

private enum ProductHapticRhythm: String, CaseIterable, Identifiable {
    case single
    case double
    case burst

    var id: String { rawValue }

    var title: String {
        switch self {
        case .single: return "单击"
        case .double: return "双击"
        case .burst: return "连击"
        }
    }
}

private enum ProductRatchetFeel: String, CaseIterable, Identifiable {
    case freewheel
    case light
    case mechanical
    case heavy

    var id: String { rawValue }

    static let tuningCases: [ProductRatchetFeel] = [.light, .mechanical, .heavy]

    var title: String {
        switch self {
        case .freewheel: return "自由"
        case .light: return "轻"
        case .mechanical: return "机械"
        case .heavy: return "重"
        }
    }
}

private enum SpinnerResistance: String, CaseIterable, Identifiable {
    case freewheel
    case magnetic

    var id: String { rawValue }
    var title: String { self == .freewheel ? "自由轮" : "磁吸棘轮" }
}

private enum SystemHapticPreset: Int, CaseIterable, Identifiable {
    case selection = 0
    case light
    case medium
    case heavy
    case soft
    case rigid
    case success
    case warning
    case error

    var id: Int { rawValue }

    var title: String {
        switch self {
        case .selection: return "Selection"
        case .light: return "Light"
        case .medium: return "Medium"
        case .heavy: return "Heavy"
        case .soft: return "Soft"
        case .rigid: return "Rigid"
        case .success: return "Success"
        case .warning: return "Warning"
        case .error: return "Error"
        }
    }
}

private enum HapticSpeedTexturePreset: String, CaseIterable, Identifiable {
    case cleanMetal
    case heavySteel
    case softBearing

    var id: String { rawValue }

    var title: String {
        switch self {
        case .cleanMetal: return "清脆金属"
        case .heavySteel: return "厚重钢件"
        case .softBearing: return "柔顺轴承"
        }
    }
}

private enum HapticTuningSlot: String, CaseIterable, Identifiable {
    case a
    case b

    var id: String { rawValue }
    var title: String { rawValue.uppercased() }
}

private struct EditableSpeedTextureProfile: Codable, Equatable {
    var enabled: Bool
    var enterDetentsPerSecond: Double
    var exitDetentsPerSecond: Double
    var fullScaleAngularSpeed: Double
    var slowDetentGain: Double
    var fastDetentGain: Double
    var minimumContinuousIntensity: Double
    var maximumContinuousIntensity: Double
    var minimumContinuousSharpness: Double
    var maximumContinuousSharpness: Double
    var responseExponent: Double
    var updateRate: Double
    var attack: Double
    var releaseSeconds: Double

    static let recommended = EditableSpeedTextureProfile(
        enabled: true,
        enterDetentsPerSecond: 30,
        exitDetentsPerSecond: 24,
        fullScaleAngularSpeed: 24,
        slowDetentGain: 1,
        fastDetentGain: 0.42,
        minimumContinuousIntensity: 0.06,
        maximumContinuousIntensity: 0.16,
        minimumContinuousSharpness: 0.28,
        maximumContinuousSharpness: 0.48,
        responseExponent: 0.75,
        updateRate: 30,
        attack: 0.04,
        releaseSeconds: 0.10)

    static func preset(_ preset: HapticSpeedTexturePreset) -> Self {
        switch preset {
        case .cleanMetal:
            return .recommended
        case .heavySteel:
            return .init(
                enabled: true,
                enterDetentsPerSecond: 28,
                exitDetentsPerSecond: 22,
                fullScaleAngularSpeed: 18,
                slowDetentGain: 1,
                fastDetentGain: 0.50,
                minimumContinuousIntensity: 0.08,
                maximumContinuousIntensity: 0.20,
                minimumContinuousSharpness: 0.22,
                maximumContinuousSharpness: 0.40,
                responseExponent: 0.65,
                updateRate: 30,
                attack: 0.08,
                releaseSeconds: 0.14)
        case .softBearing:
            return .init(
                enabled: true,
                enterDetentsPerSecond: 26,
                exitDetentsPerSecond: 20,
                fullScaleAngularSpeed: 20,
                slowDetentGain: 0.72,
                fastDetentGain: 0.30,
                minimumContinuousIntensity: 0.04,
                maximumContinuousIntensity: 0.12,
                minimumContinuousSharpness: 0.18,
                maximumContinuousSharpness: 0.34,
                responseExponent: 0.90,
                updateRate: 30,
                attack: 0.10,
                releaseSeconds: 0.16)
        }
    }

    mutating func clampValues() {
        enterDetentsPerSecond = min(80, max(4, enterDetentsPerSecond))
        exitDetentsPerSecond = min(
            enterDetentsPerSecond - 0.5,
            max(2, exitDetentsPerSecond))
        fullScaleAngularSpeed = min(80, max(1, fullScaleAngularSpeed))
        slowDetentGain = min(1, max(0, slowDetentGain))
        fastDetentGain = min(1, max(0, fastDetentGain))
        minimumContinuousIntensity = min(1, max(0, minimumContinuousIntensity))
        maximumContinuousIntensity = min(1, max(
            minimumContinuousIntensity,
            maximumContinuousIntensity))
        minimumContinuousSharpness = min(1, max(0, minimumContinuousSharpness))
        maximumContinuousSharpness = min(1, max(
            minimumContinuousSharpness,
            maximumContinuousSharpness))
        responseExponent = min(3, max(0.2, responseExponent))
        updateRate = min(60, max(10, updateRate))
        attack = min(1, max(0, attack))
        releaseSeconds = min(1, max(0, releaseSeconds))
    }

    var bridgePayload: String {
        [
            enabled ? "1" : "0",
            String(enterDetentsPerSecond),
            String(exitDetentsPerSecond),
            String(fullScaleAngularSpeed),
            String(slowDetentGain),
            String(fastDetentGain),
            String(minimumContinuousIntensity),
            String(maximumContinuousIntensity),
            String(minimumContinuousSharpness),
            String(maximumContinuousSharpness),
            String(responseExponent),
            String(updateRate),
            String(attack),
            String(releaseSeconds)
        ].joined(separator: "|")
    }
}

private struct HapticLabTelemetrySnapshot: Equatable {
    var angularSpeedRadians: Double = 0
    var rpm: Double = 0
    var detentsPerSecond: Double = 0
    var detentIntensityGain: Double = 1
    var continuousIntensity: Double = 0
    var continuousSharpness: Double = 0
    var speedBand: Int = 0
    var continuousActive = false
    var renderedEventCount = 0
    var suppressedEventCount = 0
    var lastSemanticEvent = 0
    var nativeStatus = 0

    var bandTitle: String {
        switch speedBand {
        case 1: return "低/中速 Tick"
        case 2: return "高速 Bearing"
        default: return "静止"
        }
    }

    var engineTitle: String {
        guard nativeStatus & 1 != 0 else { return "等待真机" }
        guard nativeStatus & 2 != 0 else { return "不支持 Core Haptics" }
        return nativeStatus & 4 != 0 ? "Engine 已启动" : "Engine 待启动"
    }

    var lastSemanticTitle: String {
        switch lastSemanticEvent {
        case 1: return "Detent"
        case 2: return "Breakaway"
        case 3: return "Capture"
        case 4: return "Release"
        case 5: return "Reversal"
        case 6: return "Reset"
        case 7: return "Shake"
        case 10: return "Pop"
        case 11: return "Collision"
        case 12: return "Preview"
        case 13: return "Inertia"
        case 14: return "Magnetic Edge"
        default: return "Selection"
        }
    }
}

@MainActor
private final class ProductUiState: ObservableObject {
    private enum Key {
        static let selectedModel = "fidgeting.selectedModel"
        static let interactionMode = "fidgeting.interactionMode"
        static let hapticIntensity = UnityBridge.hapticIntensityKey
        static let hapticsEnabled = UnityBridge.hapticsEnabledKey
        static let hapticSharpness = "fidgeting.settings.hapticSharpness"
        static let hapticSpeedInfluence = "fidgeting.settings.hapticSpeedInfluence"
        static let hapticReturnWeight = "fidgeting.settings.hapticReturnWeight"
        static let hapticWaveform = "fidgeting.settings.hapticWaveform"
        static let hapticDuration = "fidgeting.settings.hapticDuration"
        static let hapticAttack = "fidgeting.settings.hapticAttack"
        static let hapticDecay = "fidgeting.settings.hapticDecay"
        static let hapticRelease = "fidgeting.settings.hapticRelease"
        static let hapticSustained = "fidgeting.settings.hapticSustained"
        static let hapticEndIntensity = "fidgeting.settings.hapticEndIntensity"
        static let hapticEndSharpness = "fidgeting.settings.hapticEndSharpness"
        static let hapticPulseCount = "fidgeting.settings.hapticPulseCount"
        static let hapticPulseInterval = "fidgeting.settings.hapticPulseInterval"
        static let hapticMinimumDetentIntensity =
            "fidgeting.settings.hapticMinimumDetentIntensity"
        static let hapticImpactBoost = "fidgeting.settings.hapticImpactBoost"
        static let selectedAdvancedHapticSemantic =
            "fidgeting.settings.selectedAdvancedHapticSemantic"
        static let advancedHapticRecipes = "fidgeting.settings.advancedHapticRecipes"
        static let hapticTuningVersion = "fidgeting.settings.hapticTuningVersion"
        static let hapticRhythm = "fidgeting.settings.productHapticRhythm"
        static let detentPresetIndex = "fidgeting.settings.detentPresetIndex"
        static let detentIntensity = "fidgeting.settings.detentIntensity"
        static let detentSharpness = "fidgeting.settings.detentSharpness"
        static let ratchetFeel = "fidgeting.settings.productRatchetFeel"
        static let spinResponseLevel = "fidgeting.settings.spinResponseLevel"
        static let spinResistanceLevel = "fidgeting.settings.spinResistanceLevel"
        static let spinnerResistance = "fidgeting.settings.spinnerResistance"
        static let magneticBreakaway = "fidgeting.settings.magneticBreakaway"
        static let magneticCapture = "fidgeting.settings.magneticCapture"
        static let magneticSnapResponse = "fidgeting.settings.magneticSnapResponse"
        static let motionSensitivityPreset =
            "fidgeting.settings.motionSensitivityPreset.v1"
        static let maximumInputAngle = "fidgeting.settings.maximumInputAngle"
        static let motionResponse = "fidgeting.settings.motionResponse"
        static let gyroscopeLead = "fidgeting.settings.gyroscopeLead"
        static let maximumMotionOrbit = "fidgeting.settings.maximumMotionOrbit"
        static let reversalStopDuration = "fidgeting.settings.reversalStopDuration"
        static let flipDuration = "fidgeting.settings.flipDuration"
        static let flipOvershoot = "fidgeting.settings.flipOvershoot"
        static let flipOnRelease = "fidgeting.settings.flipOnRelease"
        static let speedTextureProfile = "fidgeting.hapticLab.speedTextureProfile.v1"
        static let speedTextureSlotA = "fidgeting.hapticLab.speedTextureSlotA.v1"
        static let speedTextureSlotB = "fidgeting.hapticLab.speedTextureSlotB.v1"
        static let selectedSpeedTextureSlot = "fidgeting.hapticLab.selectedSlot"
        static let comboHaloTuning = "fidgeting.comboHalo.tuning.v1"
        static let spinnerOnboardingCompleted = "fidgeting.onboarding.spinner.v1.completed"
        static let environmentTheme = "fidgeting.environment.theme.v1"
    }

    @Published var selectedTab: ProductTab = .spinners
    @Published var isLibraryVisible = true
    @Published var selectedModel: SpinnerModel
    @Published var environmentTheme: EnvironmentTheme
    @Published var environmentThemePreview: EnvironmentTheme
    @Published var isEnvironmentPickerPresented = false
    @Published var interactionMode: SpinnerInteractionMode
    @Published var hapticsEnabled: Bool
    @Published var hapticIntensity: Double
    @Published var hapticSharpness: Double
    @Published var hapticSpeedInfluence: Double
    @Published var hapticReturnWeight: HapticReturnWeight
    @Published var hapticWaveform: HapticWaveform
    @Published var hapticDuration: Double
    @Published var hapticAttack: Double
    @Published var hapticDecay: Double
    @Published var hapticRelease: Double
    @Published var hapticSustained: Bool
    @Published var hapticEndIntensity: Double
    @Published var hapticEndSharpness: Double
    @Published var hapticPulseCount: Double
    @Published var hapticPulseInterval: Double
    @Published var hapticMinimumDetentIntensity: Double
    @Published var hapticImpactBoost: Double
    @Published var selectedAdvancedHapticSemantic: EditableHapticSemantic
    @Published var advancedHapticRecipes: [String: EditableHapticRecipe]
    @Published var hapticRhythm: ProductHapticRhythm
    @Published var ratchetFeel: ProductRatchetFeel
    @Published var spinResponseLevel: Double
    @Published var spinResistanceLevel: Double
    @Published var spinnerResistance: SpinnerResistance
    @Published var magneticBreakaway: Double
    @Published var magneticCapture: Double
    @Published var magneticSnapResponse: Double
    @Published var motionSensitivityPreset: MotionSensitivityPreset
    @Published var maximumInputAngle: Double
    @Published var motionResponse: Double
    @Published var gyroscopeLead: Double
    @Published var maximumMotionOrbit: Double
    @Published var reversalStopDuration: Double
    @Published var flipDuration: Double
    @Published var flipOvershoot: Double
    @Published var flipOnRelease: Bool
    @Published var speedTextureProfile: EditableSpeedTextureProfile
    @Published var speedTextureSlotA: EditableSpeedTextureProfile
    @Published var speedTextureSlotB: EditableSpeedTextureProfile
    @Published var selectedSpeedTextureSlot: HapticTuningSlot
    @Published var comboHaloTuning = ComboHaloTuning.recommended
    @Published var hapticTelemetry = HapticLabTelemetrySnapshot()
    @Published var detentPresetIndex = 0
    @Published var detentPresetCount = 0
    @Published var detentPresetName = "正在读取…"
    @Published var detentPresetDetents = 0
    @Published var detentTuningIntensity = 0.0
    @Published var detentTuningSharpness = 0.0
    @Published var progressionModel: SpinnerModel = .pointedThreeBlade
    @Published var progressionLevel = 1
    @Published var progressionTotalExperience = 0.0
    @Published var progressionLevelStartExperience = 0.0
    @Published var progressionNextLevelExperience = 1.0
    @Published var progressionFraction = 0.0
    @Published var progressionLevelTitle = "初转学徒"
    @Published var progressionLevelCatalog = ProgressionLevelDetail.fallback
    @Published var threeBladeMetalSkins: [ThreeBladeMetalSkinDetail] = []
    @Published var equippedThreeBladeMetalSkinId = ""
    @Published var productStickers: [ProductStickerDetail] = []
    @Published var equippedProductStickerId = ""
    @Published var progressionStageName = "初始装配"
    @Published var progressionStageComponent = "标准单列轴承"
    @Published var progressionStageMaterial = "基础合金"
    @Published var progressionNextUnlockLevel = 20
    @Published var progressionNextUnlockName = "静态配重"
    @Published var progressionAssistantEnabled = false
    @Published var progressionAssistantMultiplier = 1.0
    @Published var progressionPeakRimSpeedKmh = 0.0
    @Published var progressionLifetimeGestures: Int64 = 0
    @Published var progressionTodayGestures = 0
    @Published var progressionActiveInteractionSeconds = 0.0
    @Published var progressionLifetimeOfflineExperience = 0.0
    @Published var progressionUnlockedBadgeCount = 0
    @Published var progressionTotalBadgeCount = 0
    @Published var badgeShardBalance = 0
    @Published var toyBadgeCatalog: [ProductBadgeDetail] = []
    @Published var collectorRank = 1
    @Published var collectorTotalExperience = 0.0
    @Published var collectorRankStartExperience = 0.0
    @Published var collectorNextRankExperience = 1.0
    @Published var collectorFraction = 0.0
    @Published var collectorFocusModel: SpinnerModel = .pointedThreeBlade
    @Published var collectorCanChangeFocus = true
    @Published var collectorGlobalBonus = 0.0
    @Published var collectorFocusBonus = 0.05
    @Published var collectorValidDays = 0
    @Published var collectorCompletedWeeks = 0
    @Published var collectorDiscoveredModelCount = 0
    @Published var collectorCosmeticCount = 0
    @Published var collectorUnlockedBadgeCount = 0
    @Published var collectorTotalBadgeCount = 0
    @Published var collectorDiscoveredModelIds: Set<String> = []
    @Published var collectorBadgeCatalog: [ProductBadgeDetail] = []
    @Published var challengeBadgeCatalog: [ProductBadgeDetail] = []
    @Published var legacyBadgeCatalog: [ProductBadgeDetail] = []
    @Published var collectorRankUp = CollectorRankUp()
    @Published var showingCollectorRankUp = false
    @Published var badgeUnlockNotice: ProductBadgeUnlockEvent?
    @Published var showingBadgeUnlockNotice = false
    @Published var showingSpinnerOnboarding = false
    @Published var offlineProgressionReward = OfflineProgressionReward()
    @Published var showingOfflineProgressionReward = false
    @Published var progressionTopAvatarFrame = CGRect.zero
    @Published var progressionSheetAvatarFrame = CGRect.zero
    @Published var progressionTopAvatarLevelOverride: Int?
    @Published var progressionTopAvatarProgressOverride: Double?
    @Published var progressionTopAvatarPulseToken = 0
    @Published var liveProgressionLevelUp = LiveProgressionLevelUp()
    @Published var showingLiveProgressionLevelUp = false
    @Published var progressionCombo = ProgressionComboState()
    @Published var motionTelemetry = ProductMotionTelemetryState()
    @Published var comboHaloProjection = ComboHaloProjectionState.centered
    @Published var spinReward = SpinRewardState()
    @Published var showingSpinReward = false

    var displayedProgressionLevel: Int {
        progressionModel == selectedModel ? progressionLevel : 1
    }

    var progressionTopAvatarLevel: Int {
        progressionTopAvatarLevelOverride ?? displayedProgressionLevel
    }

    var progressionTopAvatarProgress: Double {
        progressionTopAvatarProgressOverride
            ?? (progressionModel == selectedModel ? progressionFraction : 0)
    }

    var currentEquippedThreeBladeSkin: ThreeBladeMetalSkinDetail? {
        guard selectedModel == .metalThreeBlade,
              progressionModel == .metalThreeBlade else { return nil }
        return threeBladeMetalSkins.first {
            $0.id == equippedThreeBladeMetalSkinId
        }
    }

    var currentAppearanceName: String {
        if let skin = currentEquippedThreeBladeSkin {
            return "\(skin.displayName) · \(skin.metalName)"
        }
        guard progressionModel == selectedModel,
              !progressionStageMaterial.isEmpty else {
            return "默认材质"
        }
        return progressionStageMaterial
    }

    var currentAppearanceAccent: Color {
        if let skin = currentEquippedThreeBladeSkin {
            return Color(productHex: skin.accentHex)
        }
        return selectedModel.accent
    }

    private var previewWorkItem: DispatchWorkItem?
    private var hasPersistedDetentTuning = false
    private var hasSynchronizedInitialUnityModel = false
    private var userSelectedModelSinceLaunch = false
    private var spinRewardDismissWorkItem: DispatchWorkItem?
    private var badgeUnlockDismissWorkItem: DispatchWorkItem?
    private var pendingBadgeUnlocks: [ProductBadgeUnlockEvent] = []
    private var seenBadgeIdsByContext: [String: Set<String>] = [:]
    private var progressionTopAvatarRewardPending = false

    init() {
        let defaults = UserDefaults.standard
        let tuningVersion = defaults.integer(forKey: Key.hapticTuningVersion)
        let needsStrongHapticMigration = tuningVersion < 2
        let needsProductControlMigration = tuningVersion < 3
        let needsInteractionModeMigration = tuningVersion < 4
        let needsPerceptibilityMigration = tuningVersion < 5
        let needsGestureResponsivenessMigration = tuningVersion < 6
        let needsSpeedTextureMigration = tuningVersion < 7
        let needsIndependentControlMigration = tuningVersion < 8
        let persistedModelId = defaults.string(forKey: Key.selectedModel) ?? ""
        let migratedModel = persistedModelId == "blue-classic"
            ? .pointedThreeBlade
            : (SpinnerModel(rawValue: persistedModelId) ?? .pointedThreeBlade)
        selectedModel = migratedModel
        if persistedModelId != migratedModel.rawValue {
            defaults.set(migratedModel.rawValue, forKey: Key.selectedModel)
        }
        let persistedEnvironmentTheme = EnvironmentTheme(
            rawValue: defaults.string(forKey: Key.environmentTheme) ?? "")
            ?? .adaptive
        environmentTheme = persistedEnvironmentTheme
        environmentThemePreview = persistedEnvironmentTheme
        interactionMode = SpinnerInteractionMode(
            rawValue: defaults.string(forKey: Key.interactionMode) ?? "") ?? .smooth
        hapticsEnabled = defaults.object(forKey: Key.hapticsEnabled) == nil
            ? true
            : defaults.bool(forKey: Key.hapticsEnabled)
        hapticIntensity = needsProductControlMigration
            ? 0.72
            : Self.value(Key.hapticIntensity, fallback: 0.72)
        hapticSharpness = needsProductControlMigration
            ? 0.68
            : Self.value(Key.hapticSharpness, fallback: 0.68)
        hapticSpeedInfluence = needsProductControlMigration
            ? 0.65
            : Self.value(Key.hapticSpeedInfluence, fallback: 0.65)
        hapticReturnWeight = needsStrongHapticMigration
            ? .heavy
            : (HapticReturnWeight(
                rawValue: defaults.string(forKey: Key.hapticReturnWeight) ?? "") ?? .heavy)
        hapticWaveform = needsStrongHapticMigration
            ? .hybrid
            : (HapticWaveform(
                rawValue: defaults.string(forKey: Key.hapticWaveform) ?? "") ?? .hybrid)
        hapticDuration = needsStrongHapticMigration
            ? 0.09
            : Self.value(Key.hapticDuration, fallback: 0.09)
        hapticAttack = needsStrongHapticMigration
            ? 0
            : Self.value(Key.hapticAttack, fallback: 0)
        hapticDecay = needsStrongHapticMigration
            ? 0.12
            : Self.value(Key.hapticDecay, fallback: 0.12)
        hapticRelease = needsStrongHapticMigration
            ? 0.08
            : Self.value(Key.hapticRelease, fallback: 0.08)
        hapticSustained = needsStrongHapticMigration
            ? false
            : (defaults.object(forKey: Key.hapticSustained) == nil
                ? false
                : defaults.bool(forKey: Key.hapticSustained))
        hapticEndIntensity = needsStrongHapticMigration
            ? 0.55
            : Self.value(Key.hapticEndIntensity, fallback: 0.55)
        hapticEndSharpness = needsStrongHapticMigration
            ? 0.18
            : Self.value(Key.hapticEndSharpness, fallback: 0.18)
        hapticPulseCount = needsStrongHapticMigration
            ? 1
            : Self.value(Key.hapticPulseCount, fallback: 1)
        hapticPulseInterval = needsStrongHapticMigration
            ? 0.035
            : Self.value(Key.hapticPulseInterval, fallback: 0.035)
        hapticMinimumDetentIntensity = needsStrongHapticMigration
            ? 0.85
            : Self.value(Key.hapticMinimumDetentIntensity, fallback: 0.85)
        hapticImpactBoost = needsStrongHapticMigration
            ? 2.4
            : Self.value(Key.hapticImpactBoost, fallback: 2.4)
        let storedAdvancedSemantic = EditableHapticSemantic(
            rawValue: defaults.integer(forKey: Key.selectedAdvancedHapticSemantic))
        selectedAdvancedHapticSemantic = defaults.object(
            forKey: Key.selectedAdvancedHapticSemantic) == nil
            ? .selection
            : (storedAdvancedSemantic == .tick ? .selection : storedAdvancedSemantic ?? .selection)
        advancedHapticRecipes = Self.loadAdvancedRecipes(defaults: defaults)
        hapticRhythm = needsProductControlMigration
            ? .single
            : (ProductHapticRhythm(
                rawValue: defaults.string(forKey: Key.hapticRhythm) ?? "") ?? .single)
        let storedRatchetFeel = ProductRatchetFeel(
            rawValue: defaults.string(forKey: Key.ratchetFeel) ?? "") ?? .mechanical
        ratchetFeel = needsIndependentControlMigration || storedRatchetFeel == .freewheel
            ? .mechanical
            : storedRatchetFeel
        spinResponseLevel = needsIndependentControlMigration ? 0.55
            : Self.value(Key.spinResponseLevel, fallback: 0.55)
        spinResistanceLevel = needsIndependentControlMigration ? 0.58
            : Self.value(Key.spinResistanceLevel, fallback: 0.58)
        spinnerResistance = SpinnerResistance(
            rawValue: defaults.string(forKey: Key.spinnerResistance) ?? "") ?? .freewheel
        magneticBreakaway = Self.value(Key.magneticBreakaway, fallback: 2.2)
        magneticCapture = Self.value(Key.magneticCapture, fallback: 1.2)
        magneticSnapResponse = Self.value(Key.magneticSnapResponse, fallback: 16)
        let legacyMaximumInputAngle = Self.value(
            Key.maximumInputAngle,
            fallback: 18)
        let legacyMotionResponse = Self.value(
            Key.motionResponse,
            fallback: 8)
        let legacyGyroscopeLead = Self.value(
            Key.gyroscopeLead,
            fallback: 0.035)
        let legacyMaximumMotionOrbit = Self.value(
            Key.maximumMotionOrbit,
            fallback: 6.5)
        let resolvedMotionSensitivityPreset = MotionSensitivityPreset(
            rawValue: defaults.string(forKey: Key.motionSensitivityPreset) ?? "")
            ?? MotionSensitivityPreset.closest(
                maximumInputAngle: legacyMaximumInputAngle,
                motionResponse: legacyMotionResponse,
                gyroscopeLead: legacyGyroscopeLead,
                maximumMotionOrbit: legacyMaximumMotionOrbit)
        motionSensitivityPreset = resolvedMotionSensitivityPreset
        maximumInputAngle = resolvedMotionSensitivityPreset.maximumInputAngle
        motionResponse = resolvedMotionSensitivityPreset.motionResponse
        gyroscopeLead = resolvedMotionSensitivityPreset.gyroscopeLead
        maximumMotionOrbit = resolvedMotionSensitivityPreset.maximumMotionOrbit
        reversalStopDuration = Self.value(Key.reversalStopDuration, fallback: 0.3)
        flipDuration = Self.value(Key.flipDuration, fallback: 0.4)
        flipOvershoot = Self.value(Key.flipOvershoot, fallback: 0.1)
        flipOnRelease = defaults.object(forKey: Key.flipOnRelease) == nil
            ? false
            : defaults.bool(forKey: Key.flipOnRelease)
        speedTextureProfile = needsSpeedTextureMigration
            ? .recommended
            : Self.loadSpeedTextureProfile(
                defaults: defaults,
                key: Key.speedTextureProfile,
                fallback: .recommended)
        speedTextureSlotA = Self.loadSpeedTextureProfile(
            defaults: defaults,
            key: Key.speedTextureSlotA,
            fallback: .recommended)
        speedTextureSlotB = Self.loadSpeedTextureProfile(
            defaults: defaults,
            key: Key.speedTextureSlotB,
            fallback: .preset(.heavySteel))
        selectedSpeedTextureSlot = HapticTuningSlot(
            rawValue: defaults.string(forKey: Key.selectedSpeedTextureSlot) ?? "") ?? .a
        hasPersistedDetentTuning = defaults.object(forKey: Key.detentPresetIndex) != nil
            && defaults.object(forKey: Key.detentIntensity) != nil
            && defaults.object(forKey: Key.detentSharpness) != nil
        if hasPersistedDetentTuning {
            detentPresetIndex = max(0, defaults.integer(forKey: Key.detentPresetIndex))
            detentTuningIntensity = min(
                1,
                max(0, defaults.double(forKey: Key.detentIntensity)))
            detentTuningSharpness = min(
                1,
                max(0, defaults.double(forKey: Key.detentSharpness)))
        }
        comboHaloTuning = Self.loadComboHaloTuning(defaults: defaults)
        if needsInteractionModeMigration
            || needsPerceptibilityMigration
            || needsGestureResponsivenessMigration {
            applyInteractionModePreset()
        }
        applyProductControlMappings()
        defaults.set(8, forKey: Key.hapticTuningVersion)
    }

    func select(_ model: SpinnerModel) {
        userSelectedModelSinceLaunch = true
        selectedModel = model
        UserDefaults.standard.set(model.rawValue, forKey: Key.selectedModel)
    }

    func beginEnvironmentThemePreview() {
        environmentThemePreview = environmentTheme
        isEnvironmentPickerPresented = true
    }

    func cancelEnvironmentThemePreview() {
        environmentThemePreview = environmentTheme
        isEnvironmentPickerPresented = false
    }

    func selectEnvironmentTheme(_ theme: EnvironmentTheme) {
        environmentTheme = theme
        environmentThemePreview = theme
        isEnvironmentPickerPresented = false
        UserDefaults.standard.set(theme.rawValue, forKey: Key.environmentTheme)
        UnityBridge.send(
            "SetEnvironmentThemeFromNativeUi",
            value: theme.rawValue)
    }

    func applyAndPersist(includeMode: Bool = false) {
        applyProductControlMappings()
        let defaults = UserDefaults.standard
        defaults.set(interactionMode.rawValue, forKey: Key.interactionMode)
        defaults.set(hapticsEnabled, forKey: Key.hapticsEnabled)
        defaults.set(hapticIntensity, forKey: Key.hapticIntensity)
        defaults.set(hapticSharpness, forKey: Key.hapticSharpness)
        defaults.set(hapticSpeedInfluence, forKey: Key.hapticSpeedInfluence)
        defaults.set(hapticRhythm.rawValue, forKey: Key.hapticRhythm)
        if hasPersistedDetentTuning || detentPresetCount > 0 {
            persistDetentTuning(defaults: defaults)
        }
        defaults.set(ratchetFeel.rawValue, forKey: Key.ratchetFeel)
        defaults.set(8, forKey: Key.hapticTuningVersion)
        defaults.set(spinResponseLevel, forKey: Key.spinResponseLevel)
        defaults.set(spinResistanceLevel, forKey: Key.spinResistanceLevel)
        defaults.set(spinnerResistance.rawValue, forKey: Key.spinnerResistance)
        defaults.set(magneticBreakaway, forKey: Key.magneticBreakaway)
        defaults.set(magneticCapture, forKey: Key.magneticCapture)
        defaults.set(magneticSnapResponse, forKey: Key.magneticSnapResponse)
        defaults.set(
            motionSensitivityPreset.rawValue,
            forKey: Key.motionSensitivityPreset)
        defaults.set(maximumInputAngle, forKey: Key.maximumInputAngle)
        defaults.set(motionResponse, forKey: Key.motionResponse)
        defaults.set(gyroscopeLead, forKey: Key.gyroscopeLead)
        defaults.set(maximumMotionOrbit, forKey: Key.maximumMotionOrbit)
        defaults.set(reversalStopDuration, forKey: Key.reversalStopDuration)
        defaults.set(flipDuration, forKey: Key.flipDuration)
        defaults.set(flipOvershoot, forKey: Key.flipOvershoot)
        defaults.set(flipOnRelease, forKey: Key.flipOnRelease)
        defaults.set(environmentTheme.rawValue, forKey: Key.environmentTheme)
        persistSpeedTextureProfiles(defaults: defaults)
        persistAdvancedRecipes(defaults: defaults)

        if includeMode {
            UnityBridge.send("SetInteractionModeFromNativeUi", value: interactionMode.rawValue)
        }
        UnityBridge.send("SetHapticsEnabledFromNativeUi", value: String(hapticsEnabled))
        UnityBridge.send("SetHapticIntensityFromNativeUi", value: String(hapticIntensity))
        UnityBridge.send("SetHapticFrequencyFromNativeUi", value: String(hapticSharpness))
        UnityBridge.send("SetHapticRhythmFromNativeUi", value: hapticRhythm.rawValue)
        UnityBridge.send("SetHapticSpeedFollowFromNativeUi", value: String(hapticSpeedInfluence))
        UnityBridge.send("SetRatchetFeelFromNativeUi", value: ratchetFeel.rawValue)
        UnityBridge.send("SetSpinResponseFromNativeUi", value: String(spinResponseLevel))
        UnityBridge.send("SetSpinResistanceFromNativeUi", value: String(spinResistanceLevel))
        UnityBridge.send(
            "SetMotionSensitivityPresetFromNativeUi",
            value: motionSensitivityPreset.rawValue)
        UnityBridge.send("SetReversalStopDurationFromNativeUi", value: String(reversalStopDuration))
        UnityBridge.send("SetFlipDurationFromNativeUi", value: String(flipDuration))
        UnityBridge.send("SetFlipOvershootFromNativeUi", value: String(flipOvershoot))
        UnityBridge.send("SetFlipOnReleaseFromNativeUi", value: String(flipOnRelease))
        UnityBridge.send(
            "SetEnvironmentThemeFromNativeUi",
            value: environmentTheme.rawValue)
        UnityBridge.send(
            "SetHapticSpeedTextureProfileFromNativeUi",
            value: speedTextureProfile.bridgePayload)
        sendAllAdvancedRecipes()
    }

    func selectInteractionMode(_ mode: SpinnerInteractionMode) {
        guard interactionMode != mode else { return }
        interactionMode = mode
        applyInteractionModePreset()
        applyAndPersist(includeMode: true)
    }

    func applyRatchetFeelSelection() {
        applyAndPersist()
    }

    func applyMotionSensitivityPresetSelection() {
        maximumInputAngle = motionSensitivityPreset.maximumInputAngle
        motionResponse = motionSensitivityPreset.motionResponse
        gyroscopeLead = motionSensitivityPreset.gyroscopeLead
        maximumMotionOrbit = motionSensitivityPreset.maximumMotionOrbit
        applyAndPersist()
        UnityBridge.feedback()
    }

    func applyHapticsAndPreview() {
        applyAndPersist()
        previewWorkItem?.cancel()
        let workItem = DispatchWorkItem {
            UnityBridge.send("PreviewHapticFromNativeUi")
        }
        previewWorkItem = workItem
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.045, execute: workItem)
    }

    func restoreRecommendedValues() {
        hapticsEnabled = true
        interactionMode = .smooth
        hapticIntensity = 0.62
        hapticSharpness = 0.62
        hapticSpeedInfluence = 0.20
        hapticRhythm = .single
        ratchetFeel = .mechanical
        spinResponseLevel = 0.55
        spinResistanceLevel = 0.58
        spinnerResistance = .freewheel
        magneticBreakaway = 2.2
        magneticCapture = 1.2
        magneticSnapResponse = 16
        motionSensitivityPreset = .medium
        maximumInputAngle = motionSensitivityPreset.maximumInputAngle
        motionResponse = motionSensitivityPreset.motionResponse
        gyroscopeLead = motionSensitivityPreset.gyroscopeLead
        maximumMotionOrbit = motionSensitivityPreset.maximumMotionOrbit
        reversalStopDuration = 0.3
        flipDuration = 0.4
        flipOvershoot = 0.1
        flipOnRelease = false
        speedTextureProfile = .recommended
        speedTextureSlotA = .recommended
        speedTextureSlotB = .preset(.heavySteel)
        selectedSpeedTextureSlot = .a
        advancedHapticRecipes = Self.recommendedAdvancedRecipes()
        applyAndPersist(includeMode: true)
    }

    var selectedAdvancedRecipe: EditableHapticRecipe {
        advancedHapticRecipes[String(selectedAdvancedHapticSemantic.rawValue)]
            ?? EditableHapticRecipe.recommended(for: selectedAdvancedHapticSemantic)
    }

    func advancedBinding(
        _ keyPath: WritableKeyPath<EditableHapticRecipe, Double>) -> Binding<Double> {
        Binding(
            get: { self.selectedAdvancedRecipe[keyPath: keyPath] },
            set: { newValue in
                self.updateSelectedAdvancedRecipe { recipe in
                    recipe[keyPath: keyPath] = newValue
                }
            })
    }

    var advancedWaveformBinding: Binding<HapticWaveform> {
        Binding(
            get: { self.selectedAdvancedRecipe.waveform },
            set: { waveform in
                self.updateSelectedAdvancedRecipe { $0.waveform = waveform }
                self.persistSelectedAdvancedRecipe()
            })
    }

    var advancedSustainedBinding: Binding<Bool> {
        Binding(
            get: { self.selectedAdvancedRecipe.sustained },
            set: { sustained in
                self.updateSelectedAdvancedRecipe { $0.sustained = sustained }
                self.persistSelectedAdvancedRecipe()
            })
    }

    func selectAdvancedSemantic(_ semantic: EditableHapticSemantic) {
        selectedAdvancedHapticSemantic = semantic
        UserDefaults.standard.set(
            semantic.rawValue,
            forKey: Key.selectedAdvancedHapticSemantic)
    }

    func persistSelectedAdvancedRecipe() {
        let defaults = UserDefaults.standard
        persistAdvancedRecipes(defaults: defaults)
        sendAdvancedRecipe(selectedAdvancedHapticSemantic)
    }

    func previewSelectedAdvancedRecipe() {
        persistSelectedAdvancedRecipe()
        UnityBridge.send(
            "PreviewHapticRecipeFromNativeUi",
            value: String(selectedAdvancedHapticSemantic.rawValue))
    }

    func resetSelectedAdvancedRecipe() {
        let semantic = selectedAdvancedHapticSemantic
        updateSelectedAdvancedRecipe { recipe in
            recipe = EditableHapticRecipe.recommended(for: semantic)
        }
        persistSelectedAdvancedRecipe()
    }

    func speedTextureBinding(
        _ keyPath: WritableKeyPath<EditableSpeedTextureProfile, Double>) -> Binding<Double> {
        Binding(
            get: { self.speedTextureProfile[keyPath: keyPath] },
            set: { newValue in
                self.speedTextureProfile[keyPath: keyPath] = newValue
            })
    }

    var speedTextureEnabledBinding: Binding<Bool> {
        Binding(
            get: { self.speedTextureProfile.enabled },
            set: { enabled in
                self.speedTextureProfile.enabled = enabled
                self.applySpeedTextureAndPersist()
            })
    }

    func applySpeedTextureAndPersist() {
        speedTextureProfile.clampValues()
        let defaults = UserDefaults.standard
        persistSpeedTextureProfiles(defaults: defaults)
        UnityBridge.send(
            "SetHapticSpeedTextureProfileFromNativeUi",
            value: speedTextureProfile.bridgePayload)
    }

    func applySpeedTexturePreset(_ preset: HapticSpeedTexturePreset) {
        speedTextureProfile = .preset(preset)
        applySpeedTextureAndPersist()
        UnityBridge.send("PreviewHapticSpeedTextureFromNativeUi", value: "0.72")
    }

    func selectSpeedTextureSlot(_ slot: HapticTuningSlot) {
        selectedSpeedTextureSlot = slot
        speedTextureProfile = slot == .a ? speedTextureSlotA : speedTextureSlotB
        applySpeedTextureAndPersist()
    }

    func saveCurrentSpeedTextureSlot() {
        if selectedSpeedTextureSlot == .a {
            speedTextureSlotA = speedTextureProfile
        } else {
            speedTextureSlotB = speedTextureProfile
        }
        persistSpeedTextureProfiles(defaults: UserDefaults.standard)
    }

    func previewSpeedTexture(_ signal: Double) {
        applySpeedTextureAndPersist()
        UnityBridge.send(
            "PreviewHapticSpeedTextureFromNativeUi",
            value: String(min(1, max(0, signal))))
    }

    func updateHapticTelemetry(_ snapshot: HapticLabTelemetrySnapshot) {
        hapticTelemetry = snapshot
    }

    func selectDetentPreset(_ index: Int) {
        detentPresetIndex = index
        persistDetentTuning(defaults: UserDefaults.standard)
        UnityBridge.send("SetDetentFeelPresetFromNativeUi", value: String(index))
    }

    func setDetentIntensityOverride(_ value: Double) {
        detentTuningIntensity = min(1, max(0, value))
        persistDetentTuning(defaults: UserDefaults.standard)
        UnityBridge.send(
            "SetDetentIntensityOverrideFromNativeUi",
            value: String(detentTuningIntensity))
    }

    func setDetentSharpnessOverride(_ value: Double) {
        detentTuningSharpness = min(1, max(0, value))
        persistDetentTuning(defaults: UserDefaults.standard)
        UnityBridge.send(
            "SetDetentSharpnessOverrideFromNativeUi",
            value: String(detentTuningSharpness))
    }

    func updateDetentTuning(
        presetIndex: Int,
        presetCount: Int,
        presetName: String,
        detents: Int,
        intensity: Double,
        sharpness: Double) {
        detentPresetIndex = presetIndex
        detentPresetCount = presetCount
        detentPresetName = presetName
        detentPresetDetents = detents
        detentTuningIntensity = intensity
        detentTuningSharpness = sharpness
        persistDetentTuning(defaults: UserDefaults.standard)
    }

    func restorePersistedDetentTuningIfAvailable() {
        guard hasPersistedDetentTuning else { return }
        UnityBridge.send(
            "SetDetentFeelPresetFromNativeUi",
            value: String(detentPresetIndex))
        UnityBridge.send(
            "SetDetentIntensityOverrideFromNativeUi",
            value: String(detentTuningIntensity))
        UnityBridge.send(
            "SetDetentSharpnessOverrideFromNativeUi",
            value: String(detentTuningSharpness))
    }

    func setProgressionAssistantMultiplier(_ multiplier: Double) {
        let supportedMultipliers = [1.0, 1.5, 2.0, 3.0]
        guard supportedMultipliers.contains(where: {
            abs($0 - multiplier) < 0.001
        }) else { return }
        progressionAssistantEnabled = true
        progressionAssistantMultiplier = multiplier
        UnityBridge.send(
            "SetProgressionAssistantFromNativeUi",
            value: String(
                format: "%.1f",
                locale: Locale(identifier: "en_US_POSIX"),
                multiplier))
    }

    func stopProgressionAssistant() {
        progressionAssistantEnabled = false
        progressionAssistantMultiplier = 1.0
        UnityBridge.send("SetProgressionAssistantFromNativeUi", value: "0")
    }

    func equipThreeBladeMetalSkin(_ skin: ThreeBladeMetalSkinDetail) {
        guard progressionModel == .metalThreeBlade,
              progressionLevel >= skin.level else { return }
        UnityBridge.send("SetThreeBladeMetalSkinFromNativeUi", value: skin.id)
    }

    func equipProductSticker(_ sticker: ProductStickerDetail) {
        UnityBridge.send("SetProductStickerFromNativeUi", value: sticker.id)
    }

    func setCollectorFocus(_ model: SpinnerModel) {
        guard model != collectorFocusModel, collectorCanChangeFocus else { return }
        UnityBridge.feedback(.medium)
        UnityBridge.send("SetCollectorFocusFromNativeUi", value: model.rawValue)
    }

    func presentSpinnerOnboardingIfNeeded() {
        guard !UserDefaults.standard.bool(forKey: Key.spinnerOnboardingCompleted) else {
            return
        }
        showingSpinnerOnboarding = true
    }

    func completeSpinnerOnboarding() {
        UserDefaults.standard.set(true, forKey: Key.spinnerOnboardingCompleted)
        showingSpinnerOnboarding = false
    }

    func updateCollector(
        rank: Int,
        totalExperience: Double,
        rankStartExperience: Double,
        nextRankExperience: Double,
        fraction: Double,
        focusModel: SpinnerModel,
        canChangeFocus: Bool,
        globalBonus: Double,
        focusBonus: Double,
        validDays: Int,
        completedWeeks: Int,
        discoveredModelCount: Int,
        cosmeticCount: Int,
        discoveredModelIds: Set<String>,
        badges: [ProductBadgeDetail],
        shardBalance: Int,
        previousRank: Int) {
        collectorRank = max(1, min(30, rank))
        collectorTotalExperience = max(0, totalExperience)
        collectorRankStartExperience = max(0, rankStartExperience)
        collectorNextRankExperience = max(
            collectorRankStartExperience,
            nextRankExperience)
        collectorFraction = max(0, min(1, fraction))
        collectorFocusModel = focusModel
        collectorCanChangeFocus = canChangeFocus
        collectorGlobalBonus = max(0, globalBonus)
        collectorFocusBonus = max(collectorGlobalBonus, focusBonus)
        collectorValidDays = max(0, min(7, validDays))
        collectorCompletedWeeks = max(0, completedWeeks)
        collectorDiscoveredModelCount = max(0, discoveredModelCount)
        collectorCosmeticCount = max(0, cosmeticCount)
        collectorDiscoveredModelIds = discoveredModelIds
        collectorBadgeCatalog = badges.filter { $0.scope == .collector }
        challengeBadgeCatalog = badges.filter { $0.scope == .challenge }
        legacyBadgeCatalog = badges.filter { $0.scope == .legacy }
        collectorUnlockedBadgeCount = collectorBadgeCatalog.filter(\.unlocked).count
        collectorTotalBadgeCount = collectorBadgeCatalog.count
        badgeShardBalance = max(badgeShardBalance, max(0, shardBalance))
        detectNewBadgeUnlocks(
            contextKey: "global",
            sourceTitle: "藏家档案",
            badges: collectorBadgeCatalog + challengeBadgeCatalog + legacyBadgeCatalog)

        if previousRank > 0 && collectorRank > previousRank {
            collectorRankUp = CollectorRankUp(
                previousRank: previousRank,
                newRank: collectorRank)
            showingCollectorRankUp = true
        }
    }

    func updateProgression(
        model: SpinnerModel,
        level: Int,
        totalExperience: Double,
        levelStartExperience: Double,
        nextLevelExperience: Double,
        fraction: Double,
        stageName: String,
        stageComponent: String,
        stageMaterial: String,
        levelTitle: String,
        levelCatalog: [ProgressionLevelDetail],
        nextUnlockLevel: Int,
        nextUnlockName: String,
        assistantEnabled: Bool,
        assistantMultiplier: Double,
        peakRimSpeedKmh: Double,
        lifetimeGestures: Int64,
        todayGestures: Int,
        activeInteractionSeconds: Double,
        lifetimeOfflineExperience: Double,
        badges: [ProductBadgeDetail],
        shardBalance: Int,
        threeBladeMetalSkins: [ThreeBladeMetalSkinDetail],
        equippedThreeBladeMetalSkinId: String,
        productStickers: [ProductStickerDetail],
        equippedProductStickerId: String,
        offlineReward: OfflineProgressionReward?,
        liveLevelUp: LiveProgressionLevelUp?) {
        if !hasSynchronizedInitialUnityModel {
            hasSynchronizedInitialUnityModel = true
            if !userSelectedModelSinceLaunch && selectedModel != model {
                selectedModel = model
                UserDefaults.standard.set(
                    model.rawValue,
                    forKey: Key.selectedModel)
            }
        }
        progressionModel = model
        progressionLevel = max(1, min(100, level))
        progressionTotalExperience = max(0, totalExperience)
        progressionLevelStartExperience = max(0, levelStartExperience)
        progressionNextLevelExperience = max(
            progressionLevelStartExperience,
            nextLevelExperience)
        progressionFraction = max(0, min(1, fraction))
        progressionLevelTitle = levelTitle
        progressionLevelCatalog = levelCatalog
        progressionStageName = stageName
        progressionStageComponent = stageComponent
        progressionStageMaterial = stageMaterial
        progressionNextUnlockLevel = max(progressionLevel, nextUnlockLevel)
        progressionNextUnlockName = nextUnlockName
        progressionAssistantEnabled = assistantEnabled
        progressionAssistantMultiplier = assistantEnabled
            ? max(1, min(3, assistantMultiplier))
            : 1
        progressionPeakRimSpeedKmh = max(0, peakRimSpeedKmh)
        progressionLifetimeGestures = max(0, lifetimeGestures)
        progressionTodayGestures = max(0, todayGestures)
        progressionActiveInteractionSeconds = max(0, activeInteractionSeconds)
        progressionLifetimeOfflineExperience = max(0, lifetimeOfflineExperience)
        toyBadgeCatalog = badges.filter { $0.scope == .toy }
        progressionUnlockedBadgeCount = toyBadgeCatalog.filter(\.unlocked).count
        progressionTotalBadgeCount = toyBadgeCatalog.count
        badgeShardBalance = max(badgeShardBalance, max(0, shardBalance))
        detectNewBadgeUnlocks(
            contextKey: "toy.\(model.rawValue)",
            sourceTitle: model.title,
            badges: toyBadgeCatalog)
        self.threeBladeMetalSkins = threeBladeMetalSkins
        self.equippedThreeBladeMetalSkinId = equippedThreeBladeMetalSkinId
        self.productStickers = productStickers
        self.equippedProductStickerId = equippedProductStickerId

        if let offlineReward, offlineReward.experience >= 1 {
            offlineProgressionReward = offlineReward
            progressionTopAvatarRewardPending = true
            progressionTopAvatarLevelOverride = offlineReward.previousLevel
            progressionTopAvatarProgressOverride = min(
                1,
                max(0, offlineReward.previousLevelProgress))
            showingOfflineProgressionReward = true
        } else if !progressionTopAvatarRewardPending {
            progressionTopAvatarLevelOverride = nil
            progressionTopAvatarProgressOverride = nil
        }
        if let liveLevelUp, liveLevelUp.newLevel > liveLevelUp.previousLevel {
            liveProgressionLevelUp = liveLevelUp
            if !showingOfflineProgressionReward {
                showingLiveProgressionLevelUp = true
            }
        }
    }

    func dismissOfflineProgressionReward() {
        showingOfflineProgressionReward = false
        guard liveProgressionLevelUp.newLevel > liveProgressionLevelUp.previousLevel else {
            return
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.34) { [weak self] in
            self?.showingLiveProgressionLevelUp = true
        }
    }

    func dismissLiveProgressionLevelUp() {
        showingLiveProgressionLevelUp = false
        liveProgressionLevelUp = LiveProgressionLevelUp()
    }

    func updateProgressionTopAvatarFrame(_ frame: CGRect) {
        guard frame.width > 1, frame.height > 1,
              !progressionTopAvatarFrame.approximatelyEquals(frame) else { return }
        progressionTopAvatarFrame = frame
    }

    func updateProgressionSheetAvatarFrame(_ frame: CGRect) {
        guard frame.width > 1, frame.height > 1,
              !progressionSheetAvatarFrame.approximatelyEquals(frame) else { return }
        progressionSheetAvatarFrame = frame
    }

    func commitProgressionTopAvatar(_ reward: OfflineProgressionReward) {
        progressionTopAvatarRewardPending = false
        progressionTopAvatarLevelOverride = max(1, reward.newLevel)
        progressionTopAvatarProgressOverride = min(
            1,
            max(0, reward.newLevelProgress))
        progressionTopAvatarPulseToken &+= 1
    }

    private func detectNewBadgeUnlocks(
        contextKey: String,
        sourceTitle: String,
        badges: [ProductBadgeDetail]) {
        let storageKey = "fidgeting.badges.seen.v2.\(contextKey)"
        let unlocked = Set(
            badges.filter(\.unlocked).map(\.unlockIdentity))

        if seenBadgeIdsByContext[contextKey] == nil {
            let defaults = UserDefaults.standard
            if defaults.object(forKey: storageKey) == nil {
                seenBadgeIdsByContext[contextKey] = unlocked
                defaults.set(Array(unlocked).sorted(), forKey: storageKey)
                return
            }
            seenBadgeIdsByContext[contextKey] = Set(
                defaults.stringArray(forKey: storageKey) ?? [])
        }

        let seen = seenBadgeIdsByContext[contextKey] ?? []
        let newlyUnlocked = badges.filter {
            $0.unlocked && !seen.contains($0.unlockIdentity)
        }.map { badge in
            ProductBadgeUnlockEvent(
                id: "\(contextKey):\(badge.unlockIdentity)",
                badge: badge,
                sourceTitle: sourceTitle)
        }
        seenBadgeIdsByContext[contextKey] = unlocked
        UserDefaults.standard.set(Array(unlocked).sorted(), forKey: storageKey)
        enqueueBadgeUnlocks(newlyUnlocked)
    }

    private func enqueueBadgeUnlocks(_ badges: [ProductBadgeUnlockEvent]) {
        let existingIds = Set(
            pendingBadgeUnlocks.map(\.id)
                + [badgeUnlockNotice?.id].compactMap { $0 })
        pendingBadgeUnlocks.append(contentsOf: badges.filter {
            !existingIds.contains($0.id)
        })
        guard !showingBadgeUnlockNotice else { return }
        presentNextBadgeUnlock()
    }

    private func presentNextBadgeUnlock() {
        badgeUnlockDismissWorkItem?.cancel()
        guard !pendingBadgeUnlocks.isEmpty else {
            badgeUnlockNotice = nil
            showingBadgeUnlockNotice = false
            return
        }

        badgeUnlockNotice = pendingBadgeUnlocks.removeFirst()
        withAnimation(.spring(response: 0.38, dampingFraction: 0.76)) {
            showingBadgeUnlockNotice = true
        }

        let dismiss = DispatchWorkItem { [weak self] in
            guard let self else { return }
            withAnimation(.easeOut(duration: 0.28)) {
                self.showingBadgeUnlockNotice = false
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.34) { [weak self] in
                self?.presentNextBadgeUnlock()
            }
        }
        badgeUnlockDismissWorkItem = dismiss
        DispatchQueue.main.asyncAfter(deadline: .now() + 3.2, execute: dismiss)
    }

    func updateProgressionCombo(_ combo: ProgressionComboState) {
        // The dedicated combo view owns its cancellable number/effect timeline.
        // Publishing without an inherited animation lets rapid updates chase the
        // latest snapshot instead of queueing whole-pill spring transactions.
        progressionCombo = combo
    }

    func comboHaloDoubleBinding(
        _ keyPath: WritableKeyPath<ComboHaloTuning, Double>) -> Binding<Double> {
        Binding(
            get: { self.comboHaloTuning[keyPath: keyPath] },
            set: { value in
                var tuning = self.comboHaloTuning
                tuning[keyPath: keyPath] = value
                self.setComboHaloTuning(tuning)
            })
    }

    func comboHaloIntegerBinding(
        _ keyPath: WritableKeyPath<ComboHaloTuning, Int>) -> Binding<Int> {
        Binding(
            get: { self.comboHaloTuning[keyPath: keyPath] },
            set: { value in
                var tuning = self.comboHaloTuning
                tuning[keyPath: keyPath] = value
                self.setComboHaloTuning(tuning)
            })
    }

    func restoreRecommendedComboHaloTuning() {
        setComboHaloTuning(.recommended)
    }

    private func setComboHaloTuning(_ value: ComboHaloTuning) {
        var tuning = value
        tuning.clampValues()
        comboHaloTuning = tuning
        if let data = try? JSONEncoder().encode(tuning) {
            UserDefaults.standard.set(data, forKey: Key.comboHaloTuning)
        }
    }

    func updateMotionTelemetry(_ telemetry: ProductMotionTelemetryState) {
        motionTelemetry = telemetry
    }

    func updateComboHaloProjection(_ projection: ComboHaloProjectionState) {
        comboHaloProjection = projection.clamped()
    }

    func presentSpinReward(_ reward: SpinRewardState) {
        spinRewardDismissWorkItem?.cancel()
        withAnimation(.spring(response: 0.34, dampingFraction: 0.70)) {
            spinReward = reward
            showingSpinReward = true
        }

        let workItem = DispatchWorkItem { [weak self] in
            guard let self else { return }
            withAnimation(.easeOut(duration: 0.32)) {
                self.showingSpinReward = false
            }
        }
        spinRewardDismissWorkItem = workItem
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.4, execute: workItem)
    }

    func dismissSpinReward() {
        spinRewardDismissWorkItem?.cancel()
        spinRewardDismissWorkItem = nil
        withAnimation(.easeOut(duration: 0.18)) {
            showingSpinReward = false
        }
    }

    var rhythmDescription: String {
        switch hapticRhythm {
        case .single: return "每次机械事件一个清晰触点"
        case .double: return "主触点后增加一次较轻回声"
        case .burst: return "三个短脉冲组成快速连击"
        }
    }

    var ratchetDescription: String {
        switch ratchetFeel {
        case .freewheel: return "松手后按衰减自然滑行，不吸附档位"
        case .light: return "较容易脱档，低速轻柔回吸"
        case .mechanical: return "明确的脱档、跨档与吸附段落"
        case .heavy: return "需要更大输入才能脱档，回吸更强"
        }
    }

    private func applyProductControlMappings() {

        switch hapticRhythm {
        case .single:
            hapticPulseCount = 1
            hapticPulseInterval = 0.040
        case .double:
            hapticPulseCount = 2
            hapticPulseInterval = 0.038
        case .burst:
            hapticPulseCount = 3
            hapticPulseInterval = 0.032
        }

        switch ratchetFeel {
        case .freewheel:
            spinnerResistance = .freewheel
            magneticBreakaway = 2.2
            magneticCapture = 1.2
            magneticSnapResponse = 16
        case .light:
            spinnerResistance = .magnetic
            magneticBreakaway = 1.4
            magneticCapture = 0.8
            magneticSnapResponse = 10
        case .mechanical:
            spinnerResistance = .magnetic
            magneticBreakaway = 2.2
            magneticCapture = 1.2
            magneticSnapResponse = 16
        case .heavy:
            spinnerResistance = .magnetic
            magneticBreakaway = 3.4
            magneticCapture = 1.6
            magneticSnapResponse = 24
        }
    }

    private func applyInteractionModePreset() {
        hapticRhythm = .single
        spinResponseLevel = 0.55
        spinResistanceLevel = 0.58

        switch interactionMode {
        case .smooth:
            hapticIntensity = 0.62
            hapticSharpness = 0.62
            hapticSpeedInfluence = 0.20
            ratchetFeel = .mechanical
        case .ratchet:
            hapticIntensity = 0.95
            hapticSharpness = 0.88
            hapticSpeedInfluence = 0.35
            ratchetFeel = .mechanical
        }
    }

    private func updateSelectedAdvancedRecipe(
        _ update: (inout EditableHapticRecipe) -> Void) {
        let key = String(selectedAdvancedHapticSemantic.rawValue)
        var recipe = selectedAdvancedRecipe
        update(&recipe)
        var recipes = advancedHapticRecipes
        recipes[key] = recipe
        advancedHapticRecipes = recipes
    }

    private func sendAdvancedRecipe(_ semantic: EditableHapticSemantic) {
        let recipe = advancedHapticRecipes[String(semantic.rawValue)]
            ?? EditableHapticRecipe.recommended(for: semantic)
        UnityBridge.send(
            "SetHapticRecipeOverrideFromNativeUi",
            value: recipe.bridgePayload(for: semantic))
    }

    private func persistDetentTuning(defaults: UserDefaults) {
        hasPersistedDetentTuning = true
        defaults.set(detentPresetIndex, forKey: Key.detentPresetIndex)
        defaults.set(detentTuningIntensity, forKey: Key.detentIntensity)
        defaults.set(detentTuningSharpness, forKey: Key.detentSharpness)
    }

    private func sendAllAdvancedRecipes() {
        for semantic in EditableHapticSemantic.allCases {
            sendAdvancedRecipe(semantic)
        }
    }

    private func persistAdvancedRecipes(defaults: UserDefaults) {
        defaults.set(
            selectedAdvancedHapticSemantic.rawValue,
            forKey: Key.selectedAdvancedHapticSemantic)
        if let data = try? JSONEncoder().encode(advancedHapticRecipes) {
            defaults.set(data, forKey: Key.advancedHapticRecipes)
        }
    }

    private func persistSpeedTextureProfiles(defaults: UserDefaults) {
        defaults.set(selectedSpeedTextureSlot.rawValue, forKey: Key.selectedSpeedTextureSlot)
        if let profile = try? JSONEncoder().encode(speedTextureProfile) {
            defaults.set(profile, forKey: Key.speedTextureProfile)
        }
        if let slotA = try? JSONEncoder().encode(speedTextureSlotA) {
            defaults.set(slotA, forKey: Key.speedTextureSlotA)
        }
        if let slotB = try? JSONEncoder().encode(speedTextureSlotB) {
            defaults.set(slotB, forKey: Key.speedTextureSlotB)
        }
    }

    private static func loadAdvancedRecipes(
        defaults: UserDefaults) -> [String: EditableHapticRecipe] {
        var recipes = recommendedAdvancedRecipes()
        if let data = defaults.data(forKey: Key.advancedHapticRecipes),
           let saved = try? JSONDecoder().decode(
               [String: EditableHapticRecipe].self,
               from: data) {
            for (key, recipe) in saved {
                recipes[key] = recipe
            }
        }
        return recipes
    }

    private static func recommendedAdvancedRecipes() -> [String: EditableHapticRecipe] {
        Dictionary(uniqueKeysWithValues: EditableHapticSemantic.allCases.map {
            (String($0.rawValue), EditableHapticRecipe.recommended(for: $0))
        })
    }

    private static func loadSpeedTextureProfile(
        defaults: UserDefaults,
        key: String,
        fallback: EditableSpeedTextureProfile) -> EditableSpeedTextureProfile {
        guard let data = defaults.data(forKey: key),
              var profile = try? JSONDecoder().decode(
                  EditableSpeedTextureProfile.self,
                  from: data) else {
            return fallback
        }
        profile.clampValues()
        return profile
    }

    private static func loadComboHaloTuning(
        defaults: UserDefaults) -> ComboHaloTuning {
        guard let data = defaults.data(forKey: Key.comboHaloTuning),
              var tuning = try? JSONDecoder().decode(
                  ComboHaloTuning.self,
                  from: data) else {
            return .recommended
        }
        tuning.clampValues()
        return tuning
    }

    private static func value(_ key: String, fallback: Double) -> Double {
        let defaults = UserDefaults.standard
        return defaults.object(forKey: key) == nil ? fallback : defaults.double(forKey: key)
    }
}

private enum ProgressionCelebrationKind: Equatable {
    case offline
    case liveLevelUp
}

private struct ProgressionReduceMotionPreviewOverrideKey: EnvironmentKey {
    static let defaultValue = false
}

extension EnvironmentValues {
    var progressionReduceMotionPreviewOverride: Bool {
        get { self[ProgressionReduceMotionPreviewOverrideKey.self] }
        set { self[ProgressionReduceMotionPreviewOverrideKey.self] = newValue }
    }
}

private extension CGRect {
    func approximatelyEquals(_ other: CGRect, tolerance: CGFloat = 0.5) -> Bool {
        abs(minX - other.minX) <= tolerance
            && abs(minY - other.minY) <= tolerance
            && abs(width - other.width) <= tolerance
            && abs(height - other.height) <= tolerance
    }
}

private struct ProductWindowFrameReader: UIViewRepresentable {
    let onChange: (CGRect) -> Void

    func makeUIView(context: Context) -> UIView {
        let view = UIView(frame: .zero)
        view.isUserInteractionEnabled = false
        view.isAccessibilityElement = false
        return view
    }

    func updateUIView(_ uiView: UIView, context: Context) {
        DispatchQueue.main.async {
            guard let window = uiView.window else { return }
            onChange(uiView.convert(uiView.bounds, to: window))
        }
    }
}

private struct ProgressionRewardCelebrationView: View {
    @ObservedObject var state: ProductUiState
    let kind: ProgressionCelebrationKind
    let animationDelay: Double
    let onComplete: () -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.progressionReduceMotionPreviewOverride)
    private var reduceMotionPreviewOverride
    @State private var cardVisible = false
    @State private var animatedExperience = 0.0
    @State private var ringProgress = 0.0
    @State private var displayedRingLevel = 1
    @State private var levelReveal = false
    @State private var rewardDetailsVisible = true
    @State private var didStart = false
    @State private var isCompleting = false

    init(
        state: ProductUiState,
        kind: ProgressionCelebrationKind,
        animationDelay: Double = 0,
        onComplete: @escaping () -> Void) {
        _state = ObservedObject(wrappedValue: state)
        self.kind = kind
        self.animationDelay = max(0, animationDelay)
        self.onComplete = onComplete
    }

    private var offlineReward: OfflineProgressionReward {
        state.offlineProgressionReward
    }

    private var previousLevel: Int {
        switch kind {
        case .offline: return offlineReward.previousLevel
        case .liveLevelUp: return state.liveProgressionLevelUp.previousLevel
        }
    }

    private var newLevel: Int {
        switch kind {
        case .offline: return offlineReward.newLevel
        case .liveLevelUp: return state.liveProgressionLevelUp.newLevel
        }
    }

    private var showsLevelUp: Bool {
        newLevel > previousLevel
    }

    private var accent: Color {
        kind == .offline ? offlineReward.model.accent : state.currentAppearanceAccent
    }

    private var levelTitle: String {
        state.progressionLevelTitle
    }

    private var elapsedText: String {
        let totalMinutes = max(1, Int((offlineReward.elapsedHours * 60).rounded()))
        let hours = totalMinutes / 60
        let minutes = totalMinutes % 60
        if hours == 0 { return "\(minutes) 分钟" }
        if minutes == 0 { return "\(hours) 小时" }
        return "\(hours) 小时 \(minutes) 分"
    }

    private var hourlyGrowthText: String {
        let hourly = offlineReward.elapsedHours > 0
            ? offlineReward.experience / offlineReward.elapsedHours
            : offlineReward.experience
        return "+\(Int(hourly.rounded()).formatted()) / 小时"
    }

    private var initialRingProgress: Double {
        min(1, max(0, offlineReward.previousLevelProgress))
    }

    private var finalRingProgress: Double {
        min(1, max(0, offlineReward.newLevelProgress))
    }

    private var shouldReduceMotion: Bool {
        reduceMotion || reduceMotionPreviewOverride
    }

    var body: some View {
        ZStack {
            Color.black.opacity(0.34)
                .ignoresSafeArea()

            RadialGradient(
                colors: [accent.opacity(levelReveal ? 0.20 : 0.08), .clear],
                center: .bottom,
                startRadius: 12,
                endRadius: 420)
                .ignoresSafeArea()
                .animation(.easeOut(duration: 0.8), value: levelReveal)

            VStack(spacing: 0) {
                Spacer(minLength: 64)

                ScrollView(showsIndicators: false) {
                    VStack(spacing: 16) {
                        celebrationHeader

                        if kind == .offline {
                            ProgressionAvatarLevelRing(
                                level: displayedRingLevel,
                                progress: ringProgress,
                                accent: accent,
                                showsLevelUp: showsLevelUp && levelReveal)
                                .background(
                                    ProductWindowFrameReader { frame in
                                        state.updateProgressionSheetAvatarFrame(frame)
                                    })
                        } else {
                            ProgressionLevelUpHalo(
                                previousLevel: previousLevel,
                                newLevel: newLevel,
                                levelTitle: levelTitle,
                                accent: accent,
                                revealed: levelReveal)
                        }

                        if kind == .offline {
                            offlineMetrics

                            HStack {
                                Text("平均每小时")
                                Spacer()
                                Text(hourlyGrowthText)
                                    .foregroundStyle(accent.opacity(0.88))
                            }
                            .font(.product(.caption, weight: .bold))
                            .foregroundStyle(Color.white.opacity(0.50))
                            .padding(.horizontal, 4)
                            .opacity(rewardDetailsVisible ? 1 : 0.24)

                            if showsLevelUp {
                                levelJourney
                            }
                        } else {
                            liveReward

                            Button(action: complete) {
                                Text("继续转")
                                    .font(.product(.headline, weight: .black))
                                    .foregroundStyle(Color.black.opacity(0.88))
                                    .frame(maxWidth: .infinity, minHeight: 54)
                                    .background(
                                        Color.white,
                                        in: RoundedRectangle(
                                            cornerRadius: 18,
                                            style: .continuous))
                            }
                            .buttonStyle(.plain)
                            .contentShape(
                                RoundedRectangle(cornerRadius: 18, style: .continuous))
                            .allowsHitTesting(true)
                            .zIndex(10)
                            .accessibilityIdentifier("progression-reward-primary-action")
                            .accessibilityHint("关闭成长反馈并返回陀螺")
                        }
                    }
                    .padding(22)
                }
                .frame(maxWidth: 430, maxHeight: 660)
                .background(
                    Color.black.opacity(0.58),
                    in: RoundedRectangle(cornerRadius: 32, style: .continuous))
                .productGlass(
                    cornerRadius: 32,
                    tint: Color.white.opacity(0.040),
                    interactive: false)
                .padding(.horizontal, 12)
                .padding(.bottom, 8)
                .offset(y: cardVisible ? 0 : 96)
                .opacity(cardVisible ? 1 : 0)
            }
        }
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .interactiveDismissDisabled()
        .accessibilityElement(children: .contain)
        .onAppear(perform: startAnimation)
    }

    private func complete() {
        guard !isCompleting else { return }
        isCompleting = true
        onComplete()
        if kind == .liveLevelUp {
            UnityBridge.feedback(showsLevelUp ? .heavy : .medium)
        }
    }

    private var celebrationHeader: some View {
        HStack(spacing: 10) {
            Image(systemName: kind == .offline ? "moon.stars.fill" : "arrow.up.forward")
                .font(.product(size: 14, weight: .bold))
                .foregroundStyle(accent.opacity(0.90))
                .frame(width: 30, height: 30)
                .background(
                    accent.opacity(0.12),
                    in: RoundedRectangle(cornerRadius: 10, style: .continuous))

            VStack(alignment: .leading, spacing: 2) {
                Text(kind == .offline ? "离线成长结算" : "成长升级")
                    .font(.product(.headline, weight: .bold))
                    .foregroundStyle(.white)
                Text(kind == .offline ? offlineReward.model.title : "实时成长已到账")
                    .font(.product(.caption, weight: .medium))
                    .foregroundStyle(Color.white.opacity(0.52))
            }

            Spacer(minLength: 0)

            if kind == .offline, offlineReward.assistantEnabled {
                ProductInlineTag(
                    title: "AUTO 持续运行",
                    accent: accent,
                    filled: true)
            }
        }
    }

    private var offlineMetrics: some View {
        HStack(spacing: 10) {
            ProgressionTimeMetric(
                elapsedText: elapsedText,
                accent: accent,
                revealed: rewardDetailsVisible)

            ProgressionExperienceMetric(
                experience: animatedExperience,
                accent: accent,
                revealed: rewardDetailsVisible)
        }
    }

    private var levelJourney: some View {
        HStack(spacing: 12) {
            Text("LV.\(previousLevel)")
                .font(.product(.subheadline, weight: .bold))
                .monospacedDigit()
                .foregroundStyle(Color.white.opacity(0.46))
            Image(systemName: "arrow.right")
                .font(.product(.caption, weight: .bold))
                .foregroundStyle(accent.opacity(0.76))
            Text("LV.\(newLevel)")
                .font(.product(.title3, weight: .black))
                .monospacedDigit()
                .foregroundStyle(.white)
            Spacer(minLength: 0)
            Text("连升 \(newLevel - previousLevel) 级")
                .font(.product(.caption, weight: .bold))
                .foregroundStyle(accent.opacity(0.86))
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 12)
        .background(
            Color.white.opacity(0.035),
            in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        .opacity(levelReveal ? 1 : 0)
        .offset(y: levelReveal ? 0 : 10)
        .animation(.spring(response: 0.46, dampingFraction: 0.78), value: levelReveal)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("等级从 \(previousLevel) 提升到 \(newLevel)")
    }

    private var liveReward: some View {
        HStack(spacing: 12) {
            Image(systemName: "shippingbox.fill")
                .font(.product(size: 17, weight: .semibold))
                .foregroundStyle(accent.opacity(0.88))
                .frame(width: 38, height: 38)
                .background(
                    accent.opacity(0.11),
                    in: RoundedRectangle(cornerRadius: 12, style: .continuous))
            VStack(alignment: .leading, spacing: 3) {
                Text("本级奖励")
                    .font(.product(.caption2, weight: .bold))
                    .foregroundStyle(Color.white.opacity(0.46))
                Text(state.liveProgressionLevelUp.rewardName)
                    .font(.product(.subheadline, weight: .bold))
                    .foregroundStyle(.white)
            }
            Spacer(minLength: 0)
        }
        .padding(13)
        .background(
            Color.white.opacity(0.035),
            in: RoundedRectangle(cornerRadius: 17, style: .continuous))
        .opacity(levelReveal ? 1 : 0)
        .offset(y: levelReveal ? 0 : 10)
        .animation(.spring(response: 0.46, dampingFraction: 0.78), value: levelReveal)
    }

    private func startAnimation() {
        guard !didStart else { return }
        didStart = true
        displayedRingLevel = previousLevel
        ringProgress = initialRingProgress

        if shouldReduceMotion {
            cardVisible = true
            animatedExperience = offlineReward.experience
            displayedRingLevel = newLevel
            ringProgress = finalRingProgress
            levelReveal = showsLevelUp
            if kind == .offline {
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.35) {
                    complete()
                }
            }
            return
        }

        if animationDelay > 0 {
            DispatchQueue.main.asyncAfter(deadline: .now() + animationDelay) {
                runAnimatedSequence()
            }
        } else {
            runAnimatedSequence()
        }
    }

    private func runAnimatedSequence() {
        withAnimation(.spring(response: 0.48, dampingFraction: 0.84)) {
            cardVisible = true
        }
        guard kind == .offline else {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.82) {
                withAnimation(.spring(response: 0.58, dampingFraction: 0.67)) {
                    levelReveal = showsLevelUp
                }
                if showsLevelUp { UnityBridge.feedback(.heavy) }
            }
            return
        }

        withAnimation(.easeOut(duration: 1.30).delay(0.22)) {
            animatedExperience = offlineReward.experience
        }

        if showsLevelUp {
            withAnimation(.easeInOut(duration: 0.72).delay(0.18)) {
                ringProgress = 1
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.96) {
                displayedRingLevel = newLevel
                ringProgress = 0
                withAnimation(.easeOut(duration: 0.72)) {
                    ringProgress = finalRingProgress
                    levelReveal = true
                }
                UnityBridge.feedback(.heavy)
            }
        } else {
            withAnimation(.easeOut(duration: 1.30).delay(0.22)) {
                ringProgress = finalRingProgress
            }
        }

        let settlementEnd = showsLevelUp ? 2.20 : 1.82
        DispatchQueue.main.asyncAfter(deadline: .now() + settlementEnd) {
            withAnimation(.easeIn(duration: 0.28)) {
                cardVisible = false
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.30) {
                complete()
            }
        }
    }
}

private struct ProgressionAnimatedValue: View, Animatable {
    var value: Double
    let prefix: String
    let suffix: String

    var animatableData: Double {
        get { value }
        set { value = newValue }
    }

    var body: some View {
        Text(prefix + NumberFormatter.localizedString(
            from: NSNumber(value: Int(value.rounded())),
            number: .decimal) + suffix)
    }
}

private struct ProgressionTimeMetric: View {
    let elapsedText: String
    let accent: Color
    let revealed: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("离线时长", systemImage: "clock.fill")
                .font(.product(.caption2, weight: .bold))
                .foregroundStyle(Color.white.opacity(0.48))
            Text(elapsedText)
                .font(.product(.title3, weight: .black))
                .monospacedDigit()
                .foregroundStyle(.white)
                .lineLimit(1)
                .minimumScaleFactor(0.74)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(13)
        .background(
            Color.white.opacity(0.032),
            in: RoundedRectangle(cornerRadius: 17, style: .continuous))
        .overlay(alignment: .topTrailing) {
            Circle()
                .fill(accent.opacity(0.72))
                .frame(width: 5, height: 5)
                .padding(12)
        }
        .opacity(revealed ? 1 : 0.36)
        .offset(y: revealed ? 0 : 8)
    }
}

private struct ProgressionExperienceMetric: View {
    let experience: Double
    let accent: Color
    let revealed: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("收集成长值", systemImage: "sparkles")
                .font(.product(.caption2, weight: .bold))
                .foregroundStyle(Color.white.opacity(0.48))
            ProgressionAnimatedValue(value: experience, prefix: "+", suffix: "")
                .font(.product(.title3, weight: .black))
                .monospacedDigit()
                .foregroundStyle(.white)
                .lineLimit(1)
                .minimumScaleFactor(0.74)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(13)
        .background(
            Color.white.opacity(0.032),
            in: RoundedRectangle(cornerRadius: 17, style: .continuous))
        .overlay(alignment: .topTrailing) {
            Image(systemName: "sparkle")
                .font(.product(size: 9, weight: .bold))
                .foregroundStyle(accent.opacity(0.80))
                .padding(10)
        }
        .opacity(revealed ? 1 : 0.36)
        .offset(y: revealed ? 0 : 8)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("收集成长值 \(Int(experience.rounded()))")
    }
}

private struct ProgressionAvatarLevelRing: View {
    let level: Int
    let progress: Double
    let accent: Color
    let showsLevelUp: Bool

    var body: some View {
        ZStack {
            Circle()
                .fill(
                    RadialGradient(
                        colors: [accent.opacity(showsLevelUp ? 0.28 : 0.16), .clear],
                        center: .center,
                        startRadius: 2,
                        endRadius: 108))
                .frame(width: 214, height: 214)

            Circle()
                .stroke(Color.white.opacity(0.10), lineWidth: 7)
                .frame(width: 142, height: 142)

            Circle()
                .trim(from: 0, to: min(1, max(0, progress)))
                .stroke(
                    AngularGradient(
                        colors: [
                            Color.white.opacity(0.42),
                            accent.opacity(0.92),
                            Color.white.opacity(0.82)
                        ],
                        center: .center),
                    style: StrokeStyle(lineWidth: 8, lineCap: .round))
                .rotationEffect(.degrees(-90))
                .frame(width: 142, height: 142)
                .shadow(color: accent.opacity(0.44), radius: 10)

            VStack(spacing: 5) {
                Image(systemName: "person.crop.circle")
                    .font(.product(size: 55, weight: .medium))
                    .foregroundStyle(Color.white.opacity(0.92))
                Text("LV.\(level)")
                    .font(.product(.headline, weight: .black))
                    .monospacedDigit()
                    .foregroundStyle(.white)
                Text(showsLevelUp ? "LEVEL UP" : "当前等级")
                    .font(.product(.caption2, weight: .bold))
                    .foregroundStyle(accent.opacity(showsLevelUp ? 0.94 : 0.64))
            }

        }
        .frame(height: 190)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(
            "当前用户头像，等级 \(level)，本级进度 \(Int(progress * 100))%")
    }
}

private struct ProgressionRewardFlightEffect: GeometryEffect {
    var progress: CGFloat
    let start: CGPoint
    let end: CGPoint
    let arcOffset: CGFloat

    var animatableData: CGFloat {
        get { progress }
        set { progress = newValue }
    }

    func effectValue(size: CGSize) -> ProjectionTransform {
        let t = min(1, max(0, progress))
        let inverse = 1 - t
        let control = CGPoint(
            x: (start.x + end.x) * 0.5 + arcOffset,
            y: min(start.y, end.y) - 72 - abs(start.x - end.x) * 0.08)
        let point = CGPoint(
            x: inverse * inverse * start.x
                + 2 * inverse * t * control.x
                + t * t * end.x,
            y: inverse * inverse * start.y
                + 2 * inverse * t * control.y
                + t * t * end.y)
        return ProjectionTransform(CGAffineTransform(
            translationX: point.x - start.x,
            y: point.y - start.y))
    }
}

private struct ProgressionRewardFlightFade: AnimatableModifier {
    var progress: CGFloat
    let scaleReduction: CGFloat

    var animatableData: CGFloat {
        get { progress }
        set { progress = newValue }
    }

    func body(content: Content) -> some View {
        let fade = min(1, max(0, (1 - progress) / 0.18))
        content
            .scaleEffect(1 - progress * scaleReduction)
            .opacity(Double(fade))
    }
}

private struct ProgressionPageRewardFlightView: View {
    let experience: Double
    let accent: Color
    let sourceFrame: CGRect
    let targetFrame: CGRect
    let onArrive: () -> Void
    let onComplete: () -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.progressionReduceMotionPreviewOverride)
    private var reduceMotionPreviewOverride
    @State private var travelProgress: CGFloat = 0
    @State private var didStart = false

    private var source: CGPoint {
        CGPoint(x: sourceFrame.midX, y: sourceFrame.midY)
    }

    private var target: CGPoint {
        CGPoint(x: targetFrame.midX, y: targetFrame.midY)
    }

    private var shouldReduceMotion: Bool {
        reduceMotion || reduceMotionPreviewOverride
    }

    var body: some View {
        ZStack {
            if !shouldReduceMotion {
                ForEach(0..<9, id: \.self) { index in
                    let angle = Double(index) * .pi * 2 / 9
                    let particleStart = CGPoint(
                        x: source.x + cos(angle) * 38,
                        y: source.y + sin(angle) * 28)
                    Image(systemName: index.isMultiple(of: 3) ? "sparkle" : "circle.fill")
                        .font(.product(
                            size: index.isMultiple(of: 3) ? 13 : 7,
                            weight: .bold))
                        .foregroundStyle(
                            index.isMultiple(of: 2)
                                ? Color.white.opacity(0.94)
                                : accent.opacity(0.92))
                        .position(particleStart)
                        .modifier(ProgressionRewardFlightEffect(
                            progress: travelProgress,
                            start: particleStart,
                            end: target,
                            arcOffset: CGFloat(index - 4) * 9))
                        .modifier(ProgressionRewardFlightFade(
                            progress: travelProgress,
                            scaleReduction: 0.68))
                        .shadow(color: accent.opacity(0.46), radius: 7)
                }

                ProgressionAnimatedValue(
                    value: experience,
                    prefix: "+",
                    suffix: " XP")
                    .font(.product(.subheadline, weight: .black))
                    .monospacedDigit()
                    .foregroundStyle(.white)
                    .padding(.horizontal, 11)
                    .frame(height: 32)
                    .background(Color.black.opacity(0.84), in: Capsule())
                    .position(source)
                    .modifier(ProgressionRewardFlightEffect(
                        progress: travelProgress,
                        start: source,
                        end: target,
                        arcOffset: 22))
                    .modifier(ProgressionRewardFlightFade(
                        progress: travelProgress,
                        scaleReduction: 0.62))
                    .shadow(color: accent.opacity(0.40), radius: 9)
            }
        }
        .ignoresSafeArea()
        .allowsHitTesting(false)
        .accessibilityHidden(true)
        .onAppear(perform: startAnimation)
    }

    private func startAnimation() {
        guard !didStart else { return }
        didStart = true
        if shouldReduceMotion {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.08) {
                onArrive()
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.58) {
                onComplete()
            }
            return
        }

        withAnimation(.timingCurve(0.30, 0.04, 0.16, 1, duration: 1.16)) {
            travelProgress = 1
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.98) {
            onArrive()
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.30) {
            onComplete()
        }
    }
}

private struct ProgressionLevelUpHalo: View {
    let previousLevel: Int
    let newLevel: Int
    let levelTitle: String
    let accent: Color
    let revealed: Bool

    var body: some View {
        ZStack {
            Circle()
                .fill(
                    RadialGradient(
                        colors: [accent.opacity(revealed ? 0.30 : 0.08), .clear],
                        center: .center,
                        startRadius: 6,
                        endRadius: 128))
                .frame(width: 250, height: 250)

            ForEach(0..<3, id: \.self) { index in
                Circle()
                    .stroke(
                        index == 0
                            ? Color.white.opacity(revealed ? 0.44 : 0.10)
                            : accent.opacity(revealed ? 0.30 - Double(index) * 0.07 : 0.06),
                        lineWidth: index == 0 ? 1.4 : 1)
                    .frame(
                        width: CGFloat(118 + index * 38),
                        height: CGFloat(118 + index * 38))
                    .scaleEffect(revealed ? 1 : 0.58)
            }

            ForEach(0..<6, id: \.self) { index in
                Image(systemName: index.isMultiple(of: 2) ? "sparkle" : "diamond.fill")
                    .font(.product(size: index.isMultiple(of: 2) ? 11 : 6, weight: .bold))
                    .foregroundStyle(
                        index.isMultiple(of: 3)
                            ? Color.white.opacity(0.84)
                            : accent.opacity(0.78))
                    .offset(
                        x: cos(Double(index) * .pi / 3) * (revealed ? 102 : 34),
                        y: sin(Double(index) * .pi / 3) * (revealed ? 82 : 28))
                    .opacity(revealed ? 1 : 0)
            }

            VStack(spacing: 4) {
                Text("LEVEL UP")
                    .font(.product(.caption, weight: .black))
                    .foregroundStyle(Color.white.opacity(0.58))
                Text("LV.\(newLevel)")
                    .font(.product(size: 46, weight: .black))
                    .monospacedDigit()
                    .foregroundStyle(.white)
                Text(levelTitle)
                    .font(.product(.subheadline, weight: .bold))
                    .foregroundStyle(accent.opacity(0.86))
            }
            .scaleEffect(revealed ? 1 : 0.82)
        }
        .frame(height: 224)
        .animation(.spring(response: 0.62, dampingFraction: 0.64), value: revealed)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("LEVEL UP，等级 \(previousLevel) 提升到 \(newLevel)，\(levelTitle)")
    }
}

#if DEBUG
struct ProgressionCelebrationNativePreviewRoot: View {
    enum Mode: String {
        case offline
        case offlineNoLevel
        case live
    }

    @StateObject private var state: ProductUiState
    @State private var showingCelebration = true
    @State private var showingPageFlight = false
    @State private var acceptedReward = false
    @State private var previewRootWindowFrame = CGRect.zero
    let mode: Mode

    init(mode: Mode) {
        self.mode = mode
        let previewState = ProductUiState()
        previewState.selectedModel = .metalThreeBlade
        previewState.progressionModel = .metalThreeBlade
        previewState.progressionLevel = 42
        previewState.progressionLevelTitle = "蓝钢技师"
        previewState.progressionFraction = 0.62
        previewState.progressionTotalExperience = 1680
        previewState.offlineProgressionReward = OfflineProgressionReward(
            model: .metalThreeBlade,
            experience: 1680,
            elapsedHours: 7.75,
            previousLevel: mode == .offlineNoLevel ? 42 : 39,
            newLevel: 42,
            previousLevelProgress: mode == .offlineNoLevel ? 0.18 : 0.74,
            newLevelProgress: 0.62,
            assistantEnabled: true)
        previewState.progressionTopAvatarLevelOverride =
            mode == .offlineNoLevel ? 42 : 39
        previewState.progressionTopAvatarProgressOverride =
            mode == .offlineNoLevel ? 0.18 : 0.74
        previewState.liveProgressionLevelUp = LiveProgressionLevelUp(
            previousLevel: 39,
            newLevel: 40,
            rewardName: "夜航蓝钢刻度")
        _state = StateObject(wrappedValue: previewState)
    }

    var body: some View {
        ZStack {
            ProgressionCelebrationPreviewContext(state: state)
                .allowsHitTesting(!showingCelebration)
                .accessibilityHidden(showingCelebration)
                .accessibilityIdentifier(
                    acceptedReward
                        ? "progression-reward-auto-dismissed"
                        : "progression-preview-context")
            if showingCelebration {
                ProgressionRewardCelebrationView(
                    state: state,
                    kind: mode == .live ? .liveLevelUp : .offline,
                    animationDelay: 0.8,
                    onComplete: {
                        showingCelebration = false
                        guard mode != .live else {
                            acceptedReward = true
                            return
                        }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.42) {
                            showingPageFlight = true
                        }
                    })
            }

            if showingPageFlight,
               state.progressionSheetAvatarFrame.width > 1,
               state.progressionTopAvatarFrame.width > 1 {
                ProgressionPageRewardFlightView(
                    experience: state.offlineProgressionReward.experience,
                    accent: state.offlineProgressionReward.model.accent,
                    sourceFrame: localFrame(state.progressionSheetAvatarFrame),
                    targetFrame: localFrame(state.progressionTopAvatarFrame),
                    onArrive: {
                        state.commitProgressionTopAvatar(
                            state.offlineProgressionReward)
                    },
                    onComplete: {
                        showingPageFlight = false
                        acceptedReward = true
                    })
            }
        }
        .background(
            ProductWindowFrameReader { frame in
                previewRootWindowFrame = frame
            })
    }

    private func localFrame(_ windowFrame: CGRect) -> CGRect {
        windowFrame.offsetBy(
            dx: -previewRootWindowFrame.minX,
            dy: -previewRootWindowFrame.minY)
    }
}

private struct ProgressionCelebrationPreviewContext: View {
    @ObservedObject var state: ProductUiState

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.025, green: 0.13, blue: 0.16),
                    Color(red: 0.015, green: 0.025, blue: 0.04),
                    Color(red: 0.12, green: 0.055, blue: 0.025)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing)
                .ignoresSafeArea()

            Circle()
                .fill(state.currentAppearanceAccent.opacity(0.28))
                .frame(width: 330, height: 330)
                .blur(radius: 72)
                .offset(y: -44)

            VStack(spacing: 0) {
                ProductTopBar(state: state)
                    .frame(height: 108)

                Spacer()

                Image(systemName: state.selectedModel.symbol)
                    .font(.product(size: 128, weight: .ultraLight))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.white, state.currentAppearanceAccent.opacity(0.78)],
                            startPoint: .top,
                            endPoint: .bottom))
                    .shadow(color: state.currentAppearanceAccent.opacity(0.42), radius: 26)
                    .accessibilityHidden(true)

                Spacer()

                VStack(spacing: 8) {
                    Button {} label: {
                        Text("查看收藏盒")
                            .font(.product(.subheadline, weight: .bold))
                            .foregroundStyle(Color.white.opacity(0.84))
                            .frame(maxWidth: .infinity, minHeight: 44)
                            .background(Color.black.opacity(0.32), in:
                                RoundedRectangle(cornerRadius: 14, style: .continuous))
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("preview-display-case-action")

                    ProductPrimaryActionButton(
                        title: "进入 \(state.selectedModel.title)") {}
                    .accessibilityIdentifier("preview-enter-model-action")
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 24)
            }
        }
    }
}
#endif

private struct CollectorProfileAvatar: View {
    @ObservedObject var state: ProductUiState

    var body: some View {
        Button {
            UnityBridge.feedback()
            CodexSwiftUIOverlayManager.shared.selectTab(.collector)
        } label: {
            Text("\(state.collectorRank)")
                .font(.product(size: 17, weight: .bold).monospacedDigit())
                .foregroundStyle(Color.white.opacity(0.84))
                .frame(minWidth: 44, minHeight: 44, alignment: .leading)
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("collector-profile-avatar")
        .accessibilityLabel("藏家档案，等级 \(state.collectorRank)")
        .accessibilityHint("打开藏家档案")
    }
}

private struct ProductProgressionTopAvatar: View {
    @ObservedObject var state: ProductUiState
    @State private var pulsing = false

    private var progress: Double {
        min(1, max(0, state.progressionTopAvatarProgress))
    }

    var body: some View {
        ZStack {
            Circle()
                .fill(Color.black.opacity(0.28))
            Circle()
                .stroke(Color.white.opacity(0.12), lineWidth: 2)

            Circle()
                .trim(from: 0, to: progress)
                .stroke(
                    AngularGradient(
                        colors: [
                            Color.white.opacity(0.44),
                            state.currentAppearanceAccent.opacity(0.94),
                            Color.white.opacity(0.82)
                        ],
                        center: .center),
                    style: StrokeStyle(lineWidth: 2, lineCap: .round))
                .rotationEffect(.degrees(-90))

            VStack(spacing: -1) {
                Text("LV")
                    .font(.product(size: 5, weight: .bold))
                    .foregroundStyle(Color.white.opacity(0.46))
                Text("\(state.progressionTopAvatarLevel)")
                    .font(.product(size: 10, weight: .black).monospacedDigit())
                    .foregroundStyle(.white)
            }
        }
        .frame(width: 32, height: 32)
        .background(
            ProductWindowFrameReader { frame in
                state.updateProgressionTopAvatarFrame(frame)
            })
        .scaleEffect(pulsing ? 1.12 : 1)
        .shadow(
            color: state.currentAppearanceAccent.opacity(pulsing ? 0.72 : 0.18),
            radius: pulsing ? 14 : 4)
        .accessibilityIdentifier("progression-top-avatar")
        .accessibilityLabel(
            "当前玩具等级 \(state.progressionTopAvatarLevel)，本级进度 \(Int(progress * 100))%")
        .onChange(of: state.progressionTopAvatarPulseToken) { _ in
            withAnimation(.spring(response: 0.26, dampingFraction: 0.54)) {
                pulsing = true
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.34) {
                withAnimation(.easeOut(duration: 0.30)) {
                    pulsing = false
                }
            }
        }
    }
}

private struct ProductToyIdentityLockup: View {
    @ObservedObject var state: ProductUiState

    var body: some View {
        HStack(spacing: 8) {
            ProductProgressionTopAvatar(state: state)

            VStack(alignment: .leading, spacing: 0) {
                Text(state.selectedModel.title)
                    .font(.product(.headline, weight: .semibold))
                    .foregroundStyle(Color.white.opacity(0.94))
                    .lineLimit(1)
                    .minimumScaleFactor(0.82)

                Text(state.currentAppearanceName)
                    .font(.product(size: 10, weight: .medium))
                    .foregroundStyle(state.currentAppearanceAccent.opacity(0.76))
                    .lineLimit(1)
                    .minimumScaleFactor(0.72)
                    .padding(.top, 4)
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            "\(state.selectedModel.title)，玩具等级 \(state.displayedProgressionLevel)，当前皮肤 \(state.currentAppearanceName)")
    }
}

private struct ProductTopBar: View {
    @ObservedObject var state: ProductUiState
    @State private var showGachaStore = false

    private var pageTitle: String {
        if state.selectedTab == .collector { return "藏家档案" }
        if state.selectedTab == .settings { return "设置" }
        return "Fidgeting"
    }

    private var showsProductIdentity: Bool {
        state.selectedTab == .spinners && !state.isLibraryVisible
    }

    private var showsBackButton: Bool {
        showsProductIdentity || state.selectedTab != .spinners
    }

    var body: some View {
        VStack {
            Spacer(minLength: 0)
            ZStack {
                if showsProductIdentity {
                    ProductToyIdentityLockup(state: state)
                        .frame(maxWidth: showsBackButton ? 156 : 176)
                        .offset(y: 4)
                } else {
                    Text(pageTitle)
                        .font(.product(.headline, weight: .semibold))
                        .foregroundStyle(Color.white.opacity(0.86))
                }

                HStack {
                    HStack(spacing: 4) {
                        if showsBackButton {
                            ProductIconButton(
                                symbol: "chevron.left",
                                accessibilityLabel: "返回",
                                accent: state.currentAppearanceAccent) {
                                UnityBridge.feedback()
                                CodexSwiftUIOverlayManager.shared.showMySpinners()
                            }
                        }

                        CollectorProfileAvatar(state: state)
                    }

                    Spacer()

                    HStack(spacing: 6) {
                        if state.selectedTab == .settings {
                            ProductIconButton(
                                symbol: "checkmark",
                                accessibilityLabel: "保存并返回 \(state.selectedModel.title)",
                                selected: true,
                                accent: state.currentAppearanceAccent) {
                                state.applyAndPersist()
                                UnityBridge.feedback(.medium)
                                CodexSwiftUIOverlayManager.shared
                                    .dismissPanelToSelectedModel()
                            }
                        } else {
                            if !showsBackButton {
                                ProductIconButton(
                                    symbol: "shippingbox",
                                    accessibilityLabel: "盲盒",
                                    accent: state.currentAppearanceAccent) {
                                    UnityBridge.feedback()
                                    showGachaStore = true
                                }
                            }
                            topDestinationButton(
                                .settings,
                                label: "设置",
                                symbol: "gearshape")
                        }
                    }
                }
            }
            .padding(.horizontal, 12)
            .frame(height: 58)
            .padding(.horizontal, 8)
            .padding(.bottom, 6)
        }
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .fullScreenCover(isPresented: $state.showingSpinnerOnboarding) {
            SpinnerOnboardingView(state: state)
        }
        .alert(
            "藏家等级提升 · \(state.collectorRankUp.newRank)",
            isPresented: $state.showingCollectorRankUp) {
            Button("继续把玩", role: .cancel) {
                UnityBridge.feedback(.heavy)
            }
        } message: {
            Text(
                "藏家等级 \(state.collectorRankUp.previousRank) → \(state.collectorRankUp.newRank)\n"
                + "全局 +\(Int((state.collectorGlobalBonus * 100).rounded()))% · "
                + "主玩 +\(Int((state.collectorFocusBonus * 100).rounded()))%")
        }
        .sheet(isPresented: $showGachaStore) {
            GachaStoreView()
        }
    }

    private func topDestinationButton(
        _ tab: ProductTab,
        label: String,
        symbol: String) -> some View {
        let selected = state.selectedTab == tab
        return ProductIconButton(
            symbol: symbol,
            accessibilityLabel: label,
            selected: selected,
            accent: state.currentAppearanceAccent) {
            UnityBridge.feedback()
            if tab == .spinners {
                CodexSwiftUIOverlayManager.shared.showMySpinners()
            } else {
                CodexSwiftUIOverlayManager.shared.selectTab(tab)
            }
        }
    }
}

private struct SpinnerOnboardingView: View {
    @ObservedObject var state: ProductUiState
    @State private var page = 0

    private var accent: Color { state.currentAppearanceAccent }

    private var primaryAction: String {
        state.selectedModel == .magneticSlideTile
            ? "横向推动滑盖"
            : state.selectedModel == .magneticFanCard
                ? "围绕右上轴孔扇形拖动顶牌"
                : "用一根手指滑动陀螺"
    }

    var body: some View {
        ZStack {
            ProductBackdrop().ignoresSafeArea()
            LinearGradient(
                colors: [accent.opacity(0.07), Color.clear, Color.black.opacity(0.72)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing)
                .ignoresSafeArea()

            VStack(spacing: 16) {
                HStack {
                    Text("QUICK START")
                        .font(.product(.caption, weight: .black))
                        .foregroundStyle(Color.white.opacity(0.58))
                    Spacer()
                    Button("跳过") {
                        UnityBridge.feedback()
                        state.completeSpinnerOnboarding()
                    }
                    .foregroundStyle(Color.white.opacity(0.68))
                }
                .padding(.horizontal, 24)

                TabView(selection: $page) {
                    onboardingPage(
                        index: 0,
                        symbol: "rectangle.3.group.fill",
                        title: "先认识常驻 UI",
                        subtitle: "顶部：当前等级、皮肤、左上返回与右上角玩具/设置入口 · 上方：两枚机制图标 · 底部：等级成长卡与 AUTO。",
                        callout: "现在需要：\(primaryAction)")
                    onboardingPage(
                        index: 1,
                        symbol: "arrow.up.left.and.arrow.down.right",
                        title: "观察每一个细节",
                        subtitle: "双指捏合控制放大缩小；在模型外的空白处拖动，可以调整观察角度。",
                        callout: "一指操作玩具 · 双指缩放画面")
                    onboardingPage(
                        index: 2,
                        symbol: "waveform.path.ecg.rectangle.fill",
                        title: "力度会被看见",
                        subtitle: "滑动速度与力度会驱动实时动态和触感反馈。停止交互并停稳约 2 秒后，会根据力度、峰值速度和真实圈数给上一次动作评分。",
                        callout: "滑动还会积累 XP、解锁皮肤与 Badge")
                }
                .tabViewStyle(.page(indexDisplayMode: .never))

                ProductPageIndicator(
                    items: Array(0..<3),
                    selection: page,
                    accessibilityLabel: { index, count in
                        "快速开始第 \(index) 页，共 \(count) 页"
                    })

                ProductPrimaryActionButton(
                    title: page < 2 ? "下一步" : "开始玩",
                    accent: accent) {
                    UnityBridge.feedback(.medium)
                    if page < 2 {
                        withAnimation(.easeOut(duration: 0.24)) { page += 1 }
                    } else {
                        state.completeSpinnerOnboarding()
                    }
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 14)
            }
            .padding(.top, 18)
        }
        .preferredColorScheme(.dark)
        .interactiveDismissDisabled()
    }

    private func onboardingPage(
        index: Int,
        symbol: String,
        title: String,
        subtitle: String,
        callout: String) -> some View {
        VStack(spacing: 24) {
            Spacer(minLength: 20)
            ZStack {
                Circle()
                    .fill(accent.opacity(0.08))
                    .frame(width: 154, height: 154)
                    .blur(radius: 1)
                Circle()
                    .stroke(accent.opacity(0.28), lineWidth: 1)
                    .frame(width: 122, height: 122)
                Image(systemName: symbol)
                    .font(.product(size: 48, weight: .light))
                    .foregroundStyle(accent.opacity(0.74))
            }
            VStack(spacing: 11) {
                Text(title)
                    .font(.product(.title, weight: .bold))
                    .multilineTextAlignment(.center)
                Text(subtitle)
                    .font(.product(.body))
                    .foregroundStyle(Color.white.opacity(0.66))
                    .multilineTextAlignment(.center)
                    .lineSpacing(5)
                ProductStatusPill(
                    title: callout,
                    symbol: "hand.draw.fill",
                    accent: accent,
                    selected: true)
                    .padding(.top, 8)
            }
            .padding(22)
            .productGlass(cornerRadius: 28, tint: Color.black.opacity(0.12))
            .padding(.horizontal, 22)
            Spacer(minLength: 10)
        }
        .tag(index)
    }
}

private struct ExperienceJar: View {
    let progress: Double
    let accent: Color

    var body: some View {
        VStack(spacing: 2) {
            Capsule(style: .continuous)
                .fill(Color.white.opacity(0.7))
                .frame(width: 22, height: 5)

            GeometryReader { proxy in
                let fraction = max(0, min(1, progress))
                let fillHeight = max(3, (proxy.size.height - 6) * fraction)
                ZStack(alignment: .bottom) {
                    RoundedRectangle(cornerRadius: 9, style: .continuous)
                        .fill(Color.black.opacity(0.28))
                    RoundedRectangle(cornerRadius: 7, style: .continuous)
                        .fill(LinearGradient(
                            colors: [accent, accent.opacity(0.54)],
                            startPoint: .top,
                            endPoint: .bottom))
                        .frame(height: fillHeight)
                        .padding(3)
                    RoundedRectangle(cornerRadius: 9, style: .continuous)
                        .stroke(Color.white.opacity(0.58), lineWidth: 1)
                }
                .animation(.easeOut(duration: 0.28), value: fraction)
            }
        }
        .frame(width: 38, height: 52)
        .accessibilityLabel("成长罐")
        .accessibilityValue("已填充 \(Int(max(0, min(1, progress)) * 100))%")
    }
}

private enum ProductOverlayLayout {
    static let detailEntranceDuration: TimeInterval = 0.68
    static let detailControlsRevealDelay: TimeInterval = 0.48
    static let topBarHeight: CGFloat = 108
    static let modeBarTop: CGFloat = topBarHeight
    static let modeBarHeight: CGFloat = 58
    static let progressionHeight: CGFloat = 96
    static let progressionBottomInset: CGFloat = 12
    static let feedbackGap: CGFloat = 14
    static let comboTopMinimum: CGFloat = 190
    static let comboTopSafeAreaOffset: CGFloat = 132
    static let feedbackBottomClearance =
        progressionHeight + progressionBottomInset + feedbackGap
}

private struct SpinnerMetricCluster: View {
    let telemetry: ProductMotionTelemetryState
    let combo: ProgressionComboState
    let reward: SpinRewardState?

    @Environment(\.sizeCategory) private var sizeCategory

    @ViewBuilder
    private var rewardFooter: some View {
        if let reward {
            ProductStatusPill(
                title: reward.title + String(
                    format: " · %.0f RPM · %.1f REV",
                    reward.rpm,
                    reward.revolutions),
                symbol: "sparkles",
                accent: reward.accent,
                selected: true)
                .transition(.opacity)
        }
    }

    var body: some View {
        VStack(spacing: 7) {
            rewardFooter

            GeometryReader { proxy in
                let sideWidth = min(74, max(64, proxy.size.width * 0.23))
                let mainWidth = min(
                    160,
                    max(124, proxy.size.width - sideWidth * 2 - 20))

                HStack(alignment: .bottom, spacing: 10) {
                    ProductSideMetricDashboard(
                        title: "INTENSITY",
                        value: String(format: "%.0f", telemetry.intensity * 100),
                        unit: "%",
                        fraction: telemetry.intensity,
                        accent: telemetry.speedBand.accent,
                        accessibilityLabel: "操作强度",
                        accessibilityValue: String(
                            format: "%.0f%%",
                            telemetry.intensity * 100))
                        .frame(width: sideWidth)

                    ProductSpeedDashboard(
                        title: "SPEED",
                        value: String(format: "%.0f", telemetry.displayedSpeed),
                        unit: telemetry.displayedUnit,
                        fraction: telemetry.normalizedSpeed,
                        accent: telemetry.speedBand.accent,
                        isPeak: telemetry.speedBand == .peak,
                        stateLabel: telemetry.speedBand.title,
                        accessibilityLabel: telemetry.speedAccessibilityLabel,
                        accessibilityValue: String(
                            format: "%.0f %@，%@",
                            telemetry.displayedSpeed,
                            telemetry.displayedUnit,
                            telemetry.speedBand.title))
                        .frame(width: mainWidth)

                    ProductSideMetricDashboard(
                        title: "FREQUENCY",
                        value: String(format: "%.0f", telemetry.frequency * 100),
                        unit: "%",
                        fraction: telemetry.frequency,
                        accent: telemetry.speedBand.accent,
                        accessibilityLabel: "操作频率",
                        accessibilityValue: String(
                            format: "%.0f%%",
                            telemetry.frequency * 100))
                        .frame(width: sideWidth)
                }
                .frame(maxWidth: 320)
            }
            .frame(height: sizeCategory.isAccessibilityCategory ? 148 : 118)
        }
        .frame(maxWidth: 320)
    }
}

private enum ComboPresentationLevel: Int, Equatable {
    case ignition
    case boost
    case burst
    case peak

    static func resolve(count: Int) -> ComboPresentationLevel {
        switch count {
        case 2...4: return .ignition
        case 5...9: return .boost
        case 10...19: return .burst
        default: return count >= 20 ? .peak : .ignition
        }
    }

    var numberPeakScale: CGFloat {
        switch self {
        case .ignition: return 1.14
        case .boost: return 1.20
        case .burst: return 1.27
        case .peak: return 1.32
        }
    }

    var numberPointSize: CGFloat {
        switch self {
        case .ignition: return 42
        case .boost: return 47
        case .burst: return 52
        case .peak: return 58
        }
    }

    var numberGlowOpacity: Double {
        switch self {
        case .ignition: return 0.20
        case .boost: return 0.28
        case .burst: return 0.38
        case .peak: return 0.48
        }
    }

    var numberGlowRadius: CGFloat {
        switch self {
        case .ignition: return 5
        case .boost: return 7
        case .burst: return 10
        case .peak: return 13
        }
    }
}

private enum ComboMilestoneEffect: Equatable {
    case none
    case sweep
    case echo
    case peakBurst

    static func resolve(count: Int) -> ComboMilestoneEffect {
        if count == 5 { return .sweep }
        if count == 10 { return .echo }
        if count >= 20 && count % 10 == 0 { return .peakBurst }
        return .none
    }
}

private enum ComboChangePriority: Int {
    case settle
    case increment
    case tierRise
    case milestone

    static func resolve(
        previousCount: Int,
        previousTier: Int,
        combo: ProgressionComboState) -> ComboChangePriority {
        if ComboMilestoneEffect.resolve(count: combo.count) != .none {
            return .milestone
        }
        if combo.tier > previousTier { return .tierRise }
        if combo.count > previousCount { return .increment }
        return .settle
    }
}

private enum ComboMotionTiming {
    static let windUpSeconds = 0.045
    static let handoffSeconds = 0.085
    static let settleSeconds = 0.13
    static let eventEffectSeconds = 0.32
    static let reducedMotionCrossfadeSeconds = 0.11
    static let breakFadeSeconds = 0.22
}

private struct ComboPresentationKey: Equatable {
    let count: Int
    let tier: Int
}

private struct ComboMilestoneSweep: View {
    let progress: CGFloat

    var body: some View {
        LinearGradient(
            colors: [Color.clear, Color.white.opacity(0.72), Color.clear],
            startPoint: .top,
            endPoint: .bottom)
            .frame(width: 34, height: 70)
            .rotationEffect(.degrees(18))
            .offset(x: -82 + progress * 164)
            .blendMode(.screen)
            .accessibilityHidden(true)
    }
}

private struct ComboMilestoneSparks: View {
    let count: Int
    let progress: CGFloat

    private static let offsets: [CGSize] = [
        CGSize(width: -54, height: -20),
        CGSize(width: -43, height: 30),
        CGSize(width: 49, height: -27),
        CGSize(width: 56, height: 18),
        CGSize(width: -19, height: -36),
        CGSize(width: 21, height: 37),
        CGSize(width: -58, height: 5),
        CGSize(width: 58, height: -5)
    ]

    var body: some View {
        ZStack {
            ForEach(0..<min(count, Self.offsets.count), id: \.self) { index in
                let destination = Self.offsets[index]
                Capsule(style: .continuous)
                    .fill(Color.white.opacity(index.isMultiple(of: 2) ? 1 : 0.62))
                    .frame(width: 2.4, height: index.isMultiple(of: 2) ? 7 : 5)
                    .rotationEffect(.degrees(Double(index * 47)))
                    .offset(
                        x: destination.width * (0.34 + progress * 0.66),
                        y: destination.height * (0.34 + progress * 0.66))
                    .opacity(Double(max(0, 1 - progress)))
            }
        }
        .frame(width: 124, height: 82)
        .accessibilityHidden(true)
    }
}

/// Product-only combo presentation. Combo judgement, rewards and semantic
/// feedback remain owned by Unity; this view only stages the received snapshot.
private struct RewardingComboLockup: View {
    let combo: ProgressionComboState

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency

    @State private var displayedCount = 0
    @State private var displayedTier = 0
    @State private var outgoingCount: Int?
    @State private var incomingOpacity = 1.0
    @State private var incomingOffset: CGFloat = 0
    @State private var outgoingOpacity = 0.0
    @State private var outgoingOffset: CGFloat = 0
    @State private var numberScale: CGFloat = 1
    @State private var numberWidthScale: CGFloat = 1
    @State private var numberHeightScale: CGFloat = 1
    @State private var numberGlowPulse: CGFloat = 0
    @State private var labelScale: CGFloat = 1
    @State private var sweepProgress: CGFloat = 0
    @State private var effectProgress: CGFloat = 1
    @State private var activeEffect = ComboMilestoneEffect.none
    @State private var animationGeneration = 0

    private var level: ComboPresentationLevel {
        ComboPresentationLevel.resolve(count: combo.count)
    }

    private var presentationKey: ComboPresentationKey {
        ComboPresentationKey(count: combo.count, tier: combo.tier)
    }

    private var peakNumberScale: CGFloat {
        activeEffect == .peakBurst ? 1.40 : level.numberPeakScale
    }

    private var numberFont: Font {
        .combo(
            size: level.numberPointSize,
            relativeTo: .largeTitle,
            weight: .heavy).monospacedDigit()
    }

    private var numberLayer: some View {
        ZStack {
            if let outgoingCount {
                Text("\(outgoingCount)")
                    .opacity(outgoingOpacity)
                    .offset(y: outgoingOffset)
            }

            Text("\(displayedCount)")
                .opacity(incomingOpacity)
                .offset(y: incomingOffset)
        }
        .font(numberFont)
        .foregroundStyle(LinearGradient(
            colors: [Color.white, Color.white.opacity(0.86)],
            startPoint: .top,
            endPoint: .bottom))
        .frame(width: 112, height: 62, alignment: .center)
        .scaleEffect(
            x: numberScale * numberWidthScale,
            y: numberScale * numberHeightScale)
        .shadow(
            color: Color.white.opacity(
                level.numberGlowOpacity + Double(numberGlowPulse) * 0.34),
            radius: level.numberGlowRadius + numberGlowPulse * 8)
        .overlay {
            if !reduceMotion && activeEffect == .sweep {
                ComboMilestoneSweep(
                    progress: sweepProgress)
                    .mask(
                        Text("\(displayedCount)")
                            .font(numberFont))
            }
        }
        .minimumScaleFactor(0.72)
        .lineLimit(1)
    }

    private var lockupContent: some View {
        VStack(spacing: -4) {
            HStack(alignment: .lastTextBaseline, spacing: 0) {
                Text("×")
                    .font(.combo(size: 20, weight: .bold))
                    .foregroundStyle(Color.white.opacity(0.72))

                numberLayer
            }

            HStack(spacing: 5) {
                Text("COMBO")
                    .foregroundStyle(Color.white.opacity(0.62))
                Text("·")
                    .foregroundStyle(Color.white.opacity(0.34))
                Text(combo.title.uppercased())
                    .foregroundStyle(Color.white.opacity(0.88))
            }
            .font(.combo(size: 17, relativeTo: .headline, weight: .bold))
            .lineLimit(1)
            .scaleEffect(labelScale)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 4)
        .background {
            RadialGradient(
                colors: [
                    Color.black.opacity(reduceTransparency ? 0.72 : 0.48),
                    Color.black.opacity(reduceTransparency ? 0.44 : 0.16),
                    Color.clear
                ],
                center: .center,
                startRadius: 4,
                endRadius: 92)
                .frame(width: 184, height: 94)
                .accessibilityHidden(true)
        }
    }

    var body: some View {
        ZStack {
            if !reduceMotion && (activeEffect == .echo || activeEffect == .peakBurst) {
                Text("\(displayedCount)")
                    .font(numberFont)
                    .foregroundStyle(Color.white.opacity(0.68))
                    .scaleEffect(0.96 + effectProgress * 0.48)
                    .opacity(Double(max(0, 1 - effectProgress)))
                    .blur(radius: effectProgress * 1.5)
                    .accessibilityHidden(true)

                ComboMilestoneSparks(
                    count: activeEffect == .echo ? 4 : 8,
                    progress: effectProgress)
            }

            lockupContent
        }
        .frame(minWidth: 198, minHeight: 104)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(combo.count) 连击，\(combo.title)")
        .onAppear {
            normalizePresentation(count: combo.count, tier: combo.tier)
        }
        .onChange(of: presentationKey) { _ in
            playChange(to: combo)
        }
        .onChange(of: reduceMotion) { _ in
            cancelAndNormalize(to: combo)
        }
    }

    private func playChange(to newCombo: ProgressionComboState) {
        let oldCount = displayedCount
        let oldTier = displayedTier
        let priority = ComboChangePriority.resolve(
            previousCount: oldCount,
            previousTier: oldTier,
            combo: newCombo)
        displayedTier = newCombo.tier

        if newCombo.count == oldCount {
            playTierChange(to: newCombo, priority: priority)
            return
        }

        if reduceMotion {
            playReducedMotionChange(to: newCombo.count)
            return
        }

        let token = beginNewAnimation()
        let eventEffect = ComboMilestoneEffect.resolve(count: newCombo.count)
        activeEffect = priority == .milestone ? eventEffect : .none

        withAnimation(.easeIn(duration: ComboMotionTiming.windUpSeconds)) {
            numberScale = 0.88
            numberWidthScale = 1.08
            numberHeightScale = 0.82
            numberGlowPulse = 0.22
            labelScale = 0.96
        }

        DispatchQueue.main.asyncAfter(
            deadline: .now() + ComboMotionTiming.windUpSeconds) {
            guard animationGeneration == token else { return }

            var transaction = Transaction()
            transaction.disablesAnimations = true
            withTransaction(transaction) {
                outgoingCount = displayedCount
                displayedCount = newCombo.count
                outgoingOpacity = 1
                outgoingOffset = 0
                incomingOpacity = 0
                incomingOffset = 14
                sweepProgress = 0
                effectProgress = 0
            }

            DispatchQueue.main.async {
                guard animationGeneration == token else { return }
                withAnimation(.easeOut(duration: ComboMotionTiming.handoffSeconds)) {
                    outgoingOpacity = 0
                    outgoingOffset = -12
                    incomingOpacity = 1
                    incomingOffset = -2
                    numberScale = peakNumberScale
                    numberWidthScale = 0.94
                    numberHeightScale = 1.10
                    numberGlowPulse = 1
                    labelScale = priority.rawValue
                        >= ComboChangePriority.tierRise.rawValue ? 1.10 : 1.04
                }

                if activeEffect == .sweep {
                    withAnimation(.easeInOut(duration: ComboMotionTiming.eventEffectSeconds)) {
                        sweepProgress = 1
                    }
                } else if activeEffect == .echo || activeEffect == .peakBurst {
                    withAnimation(.easeOut(duration: ComboMotionTiming.eventEffectSeconds)) {
                        effectProgress = 1
                    }
                }
            }
        }

        DispatchQueue.main.asyncAfter(
            deadline: .now()
                + ComboMotionTiming.windUpSeconds
                + ComboMotionTiming.handoffSeconds) {
            guard animationGeneration == token else { return }
            withAnimation(.interpolatingSpring(stiffness: 300, damping: 18)) {
                incomingOffset = 0
                numberScale = 1
                numberWidthScale = 1
                numberHeightScale = 1
                numberGlowPulse = 0
                labelScale = 1
            }
        }

        DispatchQueue.main.asyncAfter(
            deadline: .now()
                + ComboMotionTiming.windUpSeconds
                + ComboMotionTiming.handoffSeconds
                + ComboMotionTiming.settleSeconds) {
            guard animationGeneration == token else { return }
            outgoingCount = nil
        }

        DispatchQueue.main.asyncAfter(
            deadline: .now()
                + ComboMotionTiming.windUpSeconds
                + ComboMotionTiming.eventEffectSeconds
                + 0.02) {
            guard animationGeneration == token else { return }
            activeEffect = .none
        }
    }

    private func playTierChange(
        to newCombo: ProgressionComboState,
        priority: ComboChangePriority) {
        let token = beginNewAnimation()
        displayedTier = newCombo.tier

        guard !reduceMotion else {
            normalizePresentation(count: newCombo.count, tier: newCombo.tier)
            return
        }

        withAnimation(.easeOut(duration: 0.10)) {
            numberScale = priority == .tierRise ? 1.18 : 1.08
            numberHeightScale = priority == .tierRise ? 1.10 : 1.04
            numberGlowPulse = priority == .tierRise ? 1 : 0.44
            labelScale = priority == .tierRise ? 1.12 : 1.04
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.10) {
            guard animationGeneration == token else { return }
            withAnimation(.interpolatingSpring(stiffness: 300, damping: 19)) {
                numberScale = 1
                numberHeightScale = 1
                numberGlowPulse = 0
                labelScale = 1
            }
        }
    }

    private func playReducedMotionChange(to count: Int) {
        let token = beginNewAnimation()
        var transaction = Transaction()
        transaction.disablesAnimations = true
        withTransaction(transaction) {
            outgoingCount = displayedCount
            displayedCount = count
            outgoingOpacity = 1
            outgoingOffset = 0
            incomingOpacity = 0
            incomingOffset = 0
            numberScale = 1
            numberWidthScale = 1
            numberHeightScale = 1
            numberGlowPulse = 0
            labelScale = 1
            activeEffect = .none
        }

        withAnimation(.linear(duration: ComboMotionTiming.reducedMotionCrossfadeSeconds)) {
            outgoingOpacity = 0
            incomingOpacity = 1
        }

        DispatchQueue.main.asyncAfter(
            deadline: .now() + ComboMotionTiming.reducedMotionCrossfadeSeconds) {
            guard animationGeneration == token else { return }
            outgoingCount = nil
        }
    }

    private func beginNewAnimation() -> Int {
        animationGeneration += 1
        let token = animationGeneration
        var transaction = Transaction()
        transaction.disablesAnimations = true
        withTransaction(transaction) {
            outgoingCount = nil
            incomingOpacity = 1
            incomingOffset = 0
            outgoingOpacity = 0
            outgoingOffset = 0
            numberScale = 1
            numberWidthScale = 1
            numberHeightScale = 1
            numberGlowPulse = 0
            labelScale = 1
            sweepProgress = 0
            effectProgress = 1
            activeEffect = .none
        }
        return token
    }

    private func cancelAndNormalize(to combo: ProgressionComboState) {
        animationGeneration += 1
        normalizePresentation(count: combo.count, tier: combo.tier)
    }

    private func normalizePresentation(count: Int, tier: Int) {
        var transaction = Transaction()
        transaction.disablesAnimations = true
        withTransaction(transaction) {
            displayedCount = count
            displayedTier = tier
            outgoingCount = nil
            incomingOpacity = 1
            incomingOffset = 0
            outgoingOpacity = 0
            outgoingOffset = 0
            numberScale = 1
            numberWidthScale = 1
            numberHeightScale = 1
            numberGlowPulse = 0
            labelScale = 1
            sweepProgress = 0
            effectProgress = 1
            activeEffect = .none
        }
    }
}

private struct SpinnerExperienceFeedbackLayer: View {
    @ObservedObject var state: ProductUiState
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var haloProgress: CGFloat = 1
    @State private var haloOpacityProgress: CGFloat = 1
    @State private var lastHaloObservedCount = 0
    @State private var haloMilestoneCount = 10

    private var comboTransition: AnyTransition {
        if reduceMotion {
            return .opacity.animation(.linear(
                duration: ComboMotionTiming.reducedMotionCrossfadeSeconds))
        }
        return .asymmetric(
            insertion: .move(edge: .top).combined(with: .opacity),
            removal: .opacity.animation(.easeOut(
                duration: ComboMotionTiming.breakFadeSeconds)))
    }

    var body: some View {
        GeometryReader { proxy in
            ZStack {
                ComboCenterHalo(
                    progress: haloProgress,
                    opacityProgress: haloOpacityProgress,
                    tuning: state.comboHaloTuning,
                    reduceMotion: reduceMotion,
                    projection: state.comboHaloProjection,
                    milestoneCount: haloMilestoneCount)

                VStack(spacing: 0) {
                    if state.progressionCombo.isActive {
                        RewardingComboLockup(combo: state.progressionCombo)
                            .transition(comboTransition)
                    }

                    Spacer(minLength: 0)
                }
                .frame(maxWidth: .infinity)
                .padding(.horizontal, 24)
                .padding(
                    .top,
                    max(
                        ProductOverlayLayout.comboTopMinimum,
                        proxy.safeAreaInsets.top
                            + ProductOverlayLayout.comboTopSafeAreaOffset))

                VStack(spacing: 0) {
                    Spacer(minLength: 0)

                    if state.motionTelemetry.available {
                        SpinnerMetricCluster(
                            telemetry: state.motionTelemetry,
                            combo: state.progressionCombo,
                            reward: state.showingSpinReward ? state.spinReward : nil)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding(.horizontal, 24)
                .padding(
                    .bottom,
                    proxy.safeAreaInsets.bottom
                        + ProductOverlayLayout.feedbackBottomClearance)
            }
            .animation(
                reduceMotion
                    ? .linear(duration: ComboMotionTiming.reducedMotionCrossfadeSeconds)
                    : .easeOut(duration: ComboMotionTiming.breakFadeSeconds),
                value: state.progressionCombo.isActive)
            .animation(.easeOut(duration: 0.20), value: state.showingSpinReward)
            .onAppear {
                lastHaloObservedCount = state.progressionCombo.count
            }
            .onChange(of: state.progressionCombo.count) { newCount in
                let previousCount = lastHaloObservedCount
                lastHaloObservedCount = newCount
                playCenterHaloIfNeeded(
                    previousCount: previousCount,
                    newCount: newCount)
            }
        }
        .ignoresSafeArea()
        .allowsHitTesting(false)
        .productDesignSystem()
        .preferredColorScheme(.dark)
    }

    private func playCenterHaloIfNeeded(
        previousCount: Int,
        newCount: Int) {
        guard state.comboHaloTuning.milestoneCrossed(
            previousCount: previousCount,
            newCount: newCount) else { return }

        var transaction = Transaction()
        transaction.disablesAnimations = true
        withTransaction(transaction) {
            haloMilestoneCount = newCount
            haloProgress = 0
            haloOpacityProgress = 0
        }

        DispatchQueue.main.async {
            let duration = reduceMotion
                ? min(0.18, state.comboHaloTuning.durationSeconds)
                : state.comboHaloTuning.durationSeconds
            withAnimation(
                reduceMotion
                    ? .linear(duration: duration)
                    : state.comboHaloTuning.animation) {
                haloProgress = 1
            }
            withAnimation(.linear(duration: duration)) {
                haloOpacityProgress = 1
            }
        }
    }
}

private struct BadgeUnlockOverlay: View {
    @ObservedObject var state: ProductUiState

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        GeometryReader { proxy in
            VStack {
                if state.showingBadgeUnlockNotice,
                   let event = state.badgeUnlockNotice {
                    ProductBadgeUnlockBanner(event: event)
                        .transition(
                            .move(edge: .top)
                                .combined(with: .scale(scale: 0.94, anchor: .top))
                                .combined(with: .opacity))
                }
                Spacer()
            }
            .frame(maxWidth: .infinity)
            .padding(.horizontal, 16)
            .padding(
                .top,
                max(
                    ProductOverlayLayout.comboTopMinimum,
                    proxy.safeAreaInsets.top
                        + ProductOverlayLayout.comboTopSafeAreaOffset))
            .animation(
                reduceMotion
                    ? nil
                    : .spring(response: 0.38, dampingFraction: 0.76),
                value: state.showingBadgeUnlockNotice)
        }
        .ignoresSafeArea()
        .productDesignSystem()
        .preferredColorScheme(.dark)
    }
}

private struct ProductBadgeUnlockBanner: View {
    let event: ProductBadgeUnlockEvent

    private var badge: ProductBadgeDetail { event.badge }

    var body: some View {
        HStack(spacing: 14) {
            ProductRarityBadge(
                assetName: badge.assetName,
                token: badge.tokenLine,
                shortName: badge.shortName,
                grade: badge.grade.rawValue,
                state: badge.state.rawValue,
                progress: badge.progress)
                .frame(width: 78)
                .accessibilityHidden(true)

            VStack(alignment: .leading, spacing: 5) {
                Text("BADGE UNLOCKED · \(event.sourceTitle)")
                    .font(.product(.caption2, weight: .bold))
                    .foregroundStyle(Color.white.opacity(0.56))
                    .lineLimit(1)
                Text(badge.title)
                    .font(.product(.headline, weight: .bold))
                    .foregroundStyle(.white)
                    .lineLimit(1)
                Text(badge.description)
                    .font(.product(.caption))
                    .foregroundStyle(Color.white.opacity(0.60))
                    .lineLimit(2)
                HStack(spacing: 8) {
                    ProductInlineTag(
                        title: "+\(badge.experienceReward) XP",
                        accent: Color.white.opacity(0.84),
                        filled: true)
                    ProductInlineTag(
                        title: "+\(badge.shardReward) 徽记碎片",
                        accent: Color.white.opacity(0.70))
                }
            }

            Spacer(minLength: 0)
        }
        .padding(.horizontal, 15)
        .padding(.vertical, 13)
        .frame(maxWidth: 380)
        .background(
            Color.black.opacity(0.26),
            in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .productGlass(cornerRadius: 24, tint: Color.white.opacity(0.035))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(
            "Badge 解锁，\(badge.title)，奖励 \(badge.experienceReward) XP 和 \(badge.shardReward) 徽记碎片")
    }
}

private struct SpinnerProgressionHUD: View {
    @ObservedObject var state: ProductUiState
    @State private var showingLevelDetails = false
    @State private var presentedCatalogSnapshot: ProgressionCatalogSnapshot?

    private var accent: Color { state.currentAppearanceAccent }
    private let autoMultipliers = [1.0, 1.5, 2.0, 3.0]
    private let controlHeight: CGFloat = 64
    private let thumbnailIconSize: CGFloat = 48

    private var autoMultiplierText: String {
        String(format: "%.1fx", state.progressionAssistantMultiplier)
    }

    private var autoEnabledColor: Color {
        Color(red: 0.30, green: 0.92, blue: 0.80)
    }

    private var autoControlForegroundColor: Color {
        state.progressionAssistantEnabled
            ? autoEnabledColor.opacity(0.96)
            : Color.white.opacity(0.48)
    }

    private var nextPreviewSkin: ThreeBladeMetalSkinDetail? {
        guard state.selectedModel == .metalThreeBlade,
              state.progressionModel == .metalThreeBlade else { return nil }
        let targetLevel = state.progressionNextUnlockLevel
        return state.threeBladeMetalSkins.first { $0.level >= targetLevel }
            ?? state.threeBladeMetalSkins.last
    }

    private var experienceText: String {
        let current = max(
            0,
            state.progressionTotalExperience - state.progressionLevelStartExperience)
        let required = max(
            1,
            state.progressionNextLevelExperience - state.progressionLevelStartExperience)
        if state.progressionLevel >= 100 {
            return "最终装配完成"
        }
        return String(format: "%.0f / %.0f XP", current, required)
    }

    private var previousMilestoneLevel: Int {
        let levels = state.progressionLevelCatalog
            .map(\.level)
            .filter { $0 <= state.progressionLevel }
        return levels.max() ?? 0
    }

    private var nextMilestoneLevel: Int {
        let levels = state.progressionLevelCatalog
            .map(\.level)
            .filter { $0 > state.progressionLevel }
        return levels.min() ?? 100
    }

    private var milestoneProgress: Double {
        let start = Double(previousMilestoneLevel)
        let end = Double(max(previousMilestoneLevel + 1, nextMilestoneLevel))
        let liveLevel = min(end, Double(state.progressionLevel) + state.progressionFraction)
        return min(1, max(0, (liveLevel - start) / (end - start)))
    }

    var body: some View {
        HStack(spacing: 10) {
            Menu {
                ForEach(autoMultipliers, id: \.self) { multiplier in
                    let selected = state.progressionAssistantEnabled
                        && abs(state.progressionAssistantMultiplier - multiplier) < 0.001
                    Button {
                        UnityBridge.feedback(.medium)
                        state.setProgressionAssistantMultiplier(multiplier)
                    } label: {
                        Label(
                            String(format: "%.1fx", multiplier)
                                + (selected ? " · 运行中" : ""),
                            systemImage: selected
                                ? "checkmark.circle.fill"
                                : "play.circle.fill")
                    }
                }

                if state.progressionAssistantEnabled {
                    Divider()
                    Button(role: .destructive) {
                        UnityBridge.feedback()
                        state.stopProgressionAssistant()
                    } label: {
                        Label("停止 AUTO", systemImage: "stop.circle.fill")
                    }
                }
            } label: {
                VStack(spacing: 8) {
                    AutoSpeedRotorBadge(
                        multiplierText: autoMultiplierText,
                        angularSpeedRadians: state.motionTelemetry.angularSpeedRadians,
                        active: state.progressionAssistantEnabled
                            && !showingLevelDetails,
                        accent: autoEnabledColor)
                        .frame(width: 29, height: 29)
                    Text("AUTO")
                        .font(.product(.caption2, weight: .semibold))
                }
                .foregroundStyle(autoControlForegroundColor)
                .padding(.horizontal, 11)
                .padding(.vertical, 8)
                .frame(
                    width: controlHeight,
                    height: controlHeight)
                .background {
                    AutoControlGlassSurface(
                        active: state.progressionAssistantEnabled,
                        tint: autoEnabledColor)
                }
                .animation(
                    .easeOut(duration: FidgetUITokens.Motion.selectionDuration),
                    value: state.progressionAssistantEnabled)
            }
            .accessibilityLabel("AUTO 菜单")
            .accessibilityValue(
                state.progressionAssistantEnabled
                    ? "已开启，\(autoMultiplierText)"
                    : "已关闭")
            .accessibilityHint("打开向上的倍率选择菜单")

            Button {
                UnityBridge.feedback()
                presentedCatalogSnapshot = ProgressionCatalogSnapshot(state: state)
                showingLevelDetails = true
            } label: {
                HStack(spacing: 8) {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(spacing: 6) {
                            Text("LV.\(state.progressionLevel)")
                                .font(.product(.subheadline, weight: .black).monospacedDigit())
                            Text(state.progressionLevelTitle)
                                .font(.product(.caption, weight: .semibold))
                                .lineLimit(1)
                            Image(systemName: "chevron.right.circle.fill")
                                .font(.product(.caption2))
                                .foregroundStyle(Color.white.opacity(0.48))
                        }
                        .foregroundStyle(.white)

                        ProductMilestoneProgressGauge(
                            previousLevel: previousMilestoneLevel,
                            currentLevel: state.progressionLevel,
                            nextLevel: nextMilestoneLevel,
                            progress: milestoneProgress,
                            accent: accent)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)

                    VStack(spacing: 1) {
                        ProgressionUnlockThumbnail(
                            model: state.selectedModel,
                            skin: nextPreviewSkin,
                            accent: accent,
                            unlocked: true,
                            showsLock: state.progressionLevel < 100,
                            shimmers: !showingLevelDetails)
                            .frame(
                                width: thumbnailIconSize,
                                height: thumbnailIconSize)

                        Text(state.progressionLevel >= 100
                             ? "MAX"
                             : "LV.\(state.progressionNextUnlockLevel)")
                            .font(.product(size: 7, weight: .black))
                            .monospacedDigit()
                            .foregroundStyle(accent.opacity(0.78))
                    }
                    .frame(width: 52, height: controlHeight)
                }
                .padding(.leading, 12)
                .padding(.trailing, 8)
                .frame(maxWidth: .infinity, alignment: .leading)
                .frame(height: controlHeight)
                .contentShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
            }
            .buttonStyle(.plain)
            .frame(maxWidth: .infinity)
            .productGlass(
                cornerRadius: 20,
                tint: accent.opacity(state.progressionCombo.isActive ? 0.075 : 0.035),
                interactive: true)
            .accessibilityLabel(
                "成长详情，等级 \(state.progressionLevel)，\(state.progressionLevelTitle)")
            .accessibilityValue(
                "\(experienceText)，上一个里程碑 \(previousMilestoneLevel)，下一个里程碑 \(nextMilestoneLevel)")
            .accessibilityHint("打开成长详情")
        }
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .sheet(
            isPresented: $showingLevelDetails,
            onDismiss: { presentedCatalogSnapshot = nil }
        ) {
            if let presentedCatalogSnapshot {
                ProgressionLevelDetailsSheet(
                    state: state,
                    snapshot: presentedCatalogSnapshot)
                    .equatable()
            }
        }
    }
}

private struct AutoControlGlassSurface: View {
    let active: Bool
    let tint: Color

    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency

    private var coolReflection: Color {
        Color(red: 0.42, green: 0.62, blue: 1.00)
    }

    var body: some View {
        let shape = RoundedRectangle(cornerRadius: 15, style: .continuous)

        ZStack {
            shape
                .fill(.ultraThinMaterial)

            shape
                .fill(
                    LinearGradient(
                        colors: active
                            ? [
                                Color.white.opacity(0.10),
                                tint.opacity(reduceTransparency ? 0.42 : 0.28),
                                coolReflection.opacity(reduceTransparency ? 0.20 : 0.11),
                                Color.black.opacity(0.06)
                            ]
                            : [
                                Color.white.opacity(reduceTransparency ? 0.12 : 0.07),
                                Color.white.opacity(0.025),
                                Color.black.opacity(0.08)
                            ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing))

            shape
                .fill(
                    RadialGradient(
                        colors: [
                            Color.white.opacity(active ? 0.14 : 0.065),
                            Color.clear
                        ],
                        center: .topLeading,
                        startRadius: 0,
                        endRadius: 74))

            if active {
                shape
                    .fill(
                        RadialGradient(
                            colors: [
                                coolReflection.opacity(0.12),
                                Color.clear
                            ],
                            center: .bottomTrailing,
                            startRadius: 0,
                            endRadius: 68))
            }
        }
        .compositingGroup()
        .clipShape(shape)
        .accessibilityHidden(true)
    }
}

private final class AutoSpeedRotorAnimator: NSObject, ObservableObject {
    @Published private(set) var rotationDegrees = 0.0

    private var angularSpeedRadians = 0.0
    private var displayLink: CADisplayLink?
    private var previousTimestamp: CFTimeInterval = 0

    func update(active: Bool, angularSpeedRadians: Double, paused: Bool) {
        self.angularSpeedRadians = max(0, angularSpeedRadians)
        guard active, !paused, self.angularSpeedRadians > 0.01 else {
            stop()
            return
        }
        guard displayLink == nil else { return }
        let link = CADisplayLink(target: self, selector: #selector(step(_:)))
        link.add(to: .main, forMode: .common)
        displayLink = link
    }

    func stop() {
        displayLink?.invalidate()
        displayLink = nil
        previousTimestamp = 0
    }

    @objc private func step(_ link: CADisplayLink) {
        guard previousTimestamp > 0 else {
            previousTimestamp = link.timestamp
            return
        }
        let delta = min(0.05, max(0, link.timestamp - previousTimestamp))
        previousTimestamp = link.timestamp
        rotationDegrees = (rotationDegrees
            + angularSpeedRadians * delta * 180 / .pi)
            .truncatingRemainder(dividingBy: 360)
    }

    deinit {
        displayLink?.invalidate()
    }
}

private struct AutoSpeedRotorBadge: View {
    let multiplierText: String
    let angularSpeedRadians: Double
    let active: Bool
    let accent: Color

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @StateObject private var animator = AutoSpeedRotorAnimator()

    private var ringColor: Color {
        active ? accent.opacity(0.98) : Color.white.opacity(0.46)
    }

    private var trackColor: Color {
        active ? accent.opacity(0.24) : Color.white.opacity(0.10)
    }

    private var multiplierColor: Color {
        active ? accent.opacity(0.98) : Color.white.opacity(0.58)
    }

    var body: some View {
        ZStack {
            Circle()
                .stroke(trackColor, lineWidth: 1)

            ZStack {
                Circle()
                    .trim(from: 0.03, to: 0.76)
                    .stroke(
                        ringColor,
                        style: StrokeStyle(lineWidth: 2, lineCap: .round))

                ForEach(0..<4, id: \.self) { index in
                    Capsule(style: .continuous)
                        .fill(ringColor.opacity(index == 0 ? 1 : 0.46))
                        .frame(width: 2, height: index == 0 ? 5 : 3)
                        .offset(y: -12)
                        .rotationEffect(.degrees(Double(index) * 90))
                }
            }
            .rotationEffect(.degrees(animator.rotationDegrees))

            Text(multiplierText)
                .font(.product(size: 9, weight: .black).monospacedDigit())
                .foregroundStyle(multiplierColor)
        }
        .onAppear {
            updateAnimator()
        }
        .onChange(of: angularSpeedRadians) { _ in
            updateAnimator()
        }
        .onChange(of: active) { _ in
            updateAnimator()
        }
        .onChange(of: reduceMotion) { _ in
            updateAnimator()
        }
        .onDisappear(perform: animator.stop)
        .accessibilityHidden(true)
    }

    private func updateAnimator() {
        animator.update(
            active: active,
            angularSpeedRadians: angularSpeedRadians,
            paused: reduceMotion)
    }
}

private struct ProgressionUnlockThumbnail: View {
    let model: SpinnerModel
    let skin: ThreeBladeMetalSkinDetail?
    let accent: Color
    let unlocked: Bool
    let showsLock: Bool
    var shimmers = false
    @State private var shimmerAtRight = false

    var body: some View {
        ZStack {
            if let skin {
                ThreeBladeMetalSkinSwatch(skin: skin, unlocked: true)
            } else {
                NativeSquareArtwork(
                    assetName: model.thumbnailAssetName,
                    fallbackSymbol: model.symbol,
                    colors: [Color(white: 0.18), accent.opacity(0.48)],
                    cornerRadius: 13)
            }

            if shimmers {
                LinearGradient(
                    colors: [.clear, Color.white.opacity(0.28), .clear],
                    startPoint: .leading,
                    endPoint: .trailing)
                    .frame(width: 18)
                    .rotationEffect(.degrees(17))
                    .offset(x: shimmerAtRight ? 48 : -48)
                    .blendMode(.screen)
            }

            if showsLock {
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        Image(systemName: "lock.fill")
                            .font(.product(size: 7, weight: .black))
                            .foregroundStyle(.white)
                            .padding(4)
                            .background(Color.black.opacity(0.62), in: Circle())
                    }
                }
                .padding(4)
            }
        }
        .saturation(unlocked ? 1 : 0)
        .opacity(unlocked ? 1 : 0.42)
        .clipShape(RoundedRectangle(cornerRadius: 13, style: .continuous))
        .shadow(color: Color.black.opacity(0.22), radius: 8, y: 4)
        .onAppear { shimmerAtRight = shimmers }
        .onChange(of: shimmers) { enabled in
            if enabled {
                shimmerAtRight = false
                DispatchQueue.main.async {
                    shimmerAtRight = true
                }
            } else {
                var transaction = Transaction()
                transaction.disablesAnimations = true
                withTransaction(transaction) {
                    shimmerAtRight = false
                }
            }
        }
        .animation(
            shimmers
                ? .linear(duration: 2.6).repeatForever(autoreverses: false)
                : nil,
            value: shimmerAtRight)
        .accessibilityHidden(true)
    }
}

private struct ProgressionCatalogSnapshot: Equatable {
    private let sessionID: UUID
    let selectedModel: SpinnerModel
    let progressionModel: SpinnerModel
    let progressionLevel: Int
    let progressionLevelTitle: String
    let progressionLevelCatalog: [ProgressionLevelDetail]
    let threeBladeMetalSkins: [ThreeBladeMetalSkinDetail]
    let equippedThreeBladeMetalSkinId: String
    let currentAppearanceName: String
    let toyBadges: [ProductBadgeDetail]
    let collectorBadges: [ProductBadgeDetail]
    let challengeBadges: [ProductBadgeDetail]
    let legacyBadges: [ProductBadgeDetail]
    let badgeShardBalance: Int

    @MainActor
    init(state: ProductUiState) {
        sessionID = UUID()
        selectedModel = state.selectedModel
        progressionModel = state.progressionModel
        progressionLevel = state.progressionLevel
        progressionLevelTitle = state.progressionLevelTitle
        progressionLevelCatalog = state.progressionLevelCatalog
        threeBladeMetalSkins = state.threeBladeMetalSkins
        equippedThreeBladeMetalSkinId = state.equippedThreeBladeMetalSkinId
        currentAppearanceName = state.currentAppearanceName
        toyBadges = state.toyBadgeCatalog
        collectorBadges = state.collectorBadgeCatalog
        challengeBadges = state.challengeBadgeCatalog
        legacyBadges = state.legacyBadgeCatalog
        badgeShardBalance = state.badgeShardBalance
        ProductRarityBadge.prewarmCatalogArtwork(
            assetNames: state.toyBadgeCatalog.map(\.assetName))
    }

    static func == (
        lhs: ProgressionCatalogSnapshot,
        rhs: ProgressionCatalogSnapshot
    ) -> Bool {
        lhs.sessionID == rhs.sessionID
    }

    var accent: Color {
        if selectedModel == .metalThreeBlade,
           progressionModel == .metalThreeBlade,
           let skin = threeBladeMetalSkins.first(where: {
               $0.id == equippedThreeBladeMetalSkinId
           }) {
            return Color(productHex: skin.accentHex)
        }
        return selectedModel.accent
    }
}

private struct ProgressionLevelDetailsSheet: View, Equatable {
    // This sheet deliberately owns one immutable catalog session. ProductUiState
    // publishes motion telemetry at 20 Hz; observing it here would rebuild the
    // sheet while the user scrolls even though none of that data is displayed.
    let state: ProductUiState
    let snapshot: ProgressionCatalogSnapshot
    @State private var selectedSection: Int
    @Environment(\.dismiss) private var dismiss

    init(
        state: ProductUiState,
        snapshot: ProgressionCatalogSnapshot,
        initialSection: Int = 0
    ) {
        self.state = state
        self.snapshot = snapshot
        _selectedSection = State(initialValue: min(2, max(0, initialSection)))
    }

    static func == (
        lhs: ProgressionLevelDetailsSheet,
        rhs: ProgressionLevelDetailsSheet
    ) -> Bool {
        lhs.snapshot == rhs.snapshot
    }

    var body: some View {
        VStack(spacing: 0) {
            ProductSheetDragHandle(closeTitle: "完成") { dismiss() }

            ProgressionCatalogHeader(
                selectedSection: $selectedSection,
                onDone: { dismiss() })
                .padding(.horizontal, 14)
                .padding(.bottom, 10)

            switch selectedSection {
            case 0:
                ProgressionLevelTimeline(snapshot: snapshot)
                    .equatable()
            case 1:
                ProgressionBadgeAchievements(snapshot: snapshot)
                    .equatable()
            default:
                ProgressionCosmeticsCatalog(
                    state: state,
                    snapshot: snapshot)
                    .equatable()
            }
        }
        .productStaticSurfaceMode()
        .background(ProgressionCatalogSheetBackdrop())
        .modifier(ProgressionCatalogPresentationBackground())
        .productDesignSystem()
        .preferredColorScheme(.dark)
    }
}

private struct ProgressionCatalogSheetBackdrop: View {
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency

    var body: some View {
        ZStack {
            if reduceTransparency {
                Color.black.opacity(0.94)
            } else {
                Rectangle()
                    .fill(.ultraThinMaterial)
                    .opacity(0.78)
                Color.black.opacity(0.24)
                LinearGradient(
                    colors: [
                        Color.white.opacity(0.025),
                        Color.black.opacity(0.18)
                    ],
                    startPoint: .top,
                    endPoint: .bottom)
            }
        }
        .ignoresSafeArea()
        .accessibilityHidden(true)
    }
}

private struct ProgressionCatalogPresentationBackground: ViewModifier {
    @ViewBuilder
    func body(content: Content) -> some View {
        if #available(iOS 16.4, *) {
            content.presentationBackground(.clear)
        } else {
            content
        }
    }
}

private struct ProgressionCatalogHeader: View {
    @Binding var selectedSection: Int
    let onDone: () -> Void

    var body: some View {
        VStack(spacing: 13) {
            ZStack {
                Text("成长图鉴")
                    .font(.product(.title3, weight: .bold))
                    .foregroundStyle(Color.white.opacity(0.96))
                    .frame(maxWidth: .infinity)

                HStack {
                    Spacer()
                    Button("完成", action: onDone)
                        .font(.product(.subheadline, weight: .semibold))
                        .foregroundStyle(Color.white.opacity(0.84))
                        .padding(.horizontal, 12)
                        .frame(minHeight: 36)
                        .background(
                            Color.white.opacity(0.07),
                            in: Capsule(style: .continuous))
                }
            }

            Picker("成长栏目", selection: $selectedSection) {
                Text("等级").tag(0)
                Text("Badge").tag(1)
                Text("外观").tag(2)
            }
            .pickerStyle(.segmented)
        }
        .padding(.horizontal, 14)
        .padding(.top, 12)
        .padding(.bottom, 14)
        .background(
            Color.white.opacity(0.014),
            in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .productGlass(
            cornerRadius: 24,
            tint: Color.white.opacity(0.014))
    }
}

private struct ProgressionLevelTimeline: View, Equatable {
    let snapshot: ProgressionCatalogSnapshot
    private var accent: Color { snapshot.accent }

    private func unlockSkin(for level: Int) -> ThreeBladeMetalSkinDetail? {
        guard snapshot.selectedModel == .metalThreeBlade,
              snapshot.progressionModel == .metalThreeBlade else { return nil }
        return snapshot.threeBladeMetalSkins.first { $0.level == level }
    }

    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 16) {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("LV.\(snapshot.progressionLevel) · \(snapshot.progressionLevelTitle)")
                            .font(.product(.title2, weight: .bold).monospacedDigit())
                    }
                    Spacer()
                    Text("\(snapshot.progressionLevel)%")
                        .font(.product(.headline, weight: .black).monospacedDigit())
                        .foregroundStyle(accent)
                }
                .padding(16)
                .productGlass(cornerRadius: 22, tint: accent.opacity(0.08))

                HStack(alignment: .top, spacing: 8) {
                    ProgressionVerticalRail(
                        progress: Double(snapshot.progressionLevel) / 100.0,
                        accent: accent)
                        .frame(width: 12)

                    VStack(spacing: 10) {
                        ProgressionLevelRow(
                            levelLabel: "LV.0",
                            title: "START",
                            unlockName: "选择玩具并开始第一次滑动",
                            level: 0,
                            model: snapshot.selectedModel,
                            skin: nil,
                            unlocked: true,
                            current: snapshot.progressionLevel == 0,
                            accent: accent)

                        ForEach(Array(snapshot.progressionLevelCatalog.enumerated()), id: \.element.id) { index, detail in
                            let nextLevel = index + 1 < snapshot.progressionLevelCatalog.count
                                ? snapshot.progressionLevelCatalog[index + 1].level - 1
                                : detail.level
                            ProgressionLevelRow(
                                levelLabel: detail.level == nextLevel
                                    ? "LV.\(detail.level)"
                                    : "LV.\(detail.level)–\(nextLevel)",
                                title: detail.title,
                                unlockName: detail.unlockName,
                                level: detail.level,
                                model: snapshot.selectedModel,
                                skin: unlockSkin(for: detail.level),
                                unlocked: snapshot.progressionLevel >= detail.level,
                                current: snapshot.progressionLevel >= detail.level
                                    && snapshot.progressionLevel <= nextLevel,
                                accent: accent)
                        }
                    }
                }

                VStack(alignment: .leading, spacing: 7) {
                    Label("COMBO 如何触发", systemImage: "bolt.fill")
                        .font(.product(.headline))
                    Text("Speed 使用真实转子角速度，Intensity 使用本次滑动力度，Frequency 使用最近连续滑动节奏。第二次连续合格动作开始连击；停顿 2.4 秒自动断连。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.58))
                    Text("顺流 +8% XP · 强驱 +18% XP · 超频 +30% XP")
                        .font(.product(.caption, weight: .semibold))
                        .foregroundStyle(accent)
                }
                .padding(16)
                .productGlass(cornerRadius: 20, tint: accent.opacity(0.06))
            }
            .padding(18)
        }
    }
}

private struct ProgressionCosmeticsCatalog: View, Equatable {
    let state: ProductUiState
    let snapshot: ProgressionCatalogSnapshot
    @State private var equippedSkinId: String

    init(state: ProductUiState, snapshot: ProgressionCatalogSnapshot) {
        self.state = state
        self.snapshot = snapshot
        _equippedSkinId = State(
            initialValue: snapshot.equippedThreeBladeMetalSkinId)
    }

    static func == (
        lhs: ProgressionCosmeticsCatalog,
        rhs: ProgressionCosmeticsCatalog) -> Bool {
        lhs.snapshot == rhs.snapshot
    }

    private var accent: Color {
        equippedSkin.map { Color(productHex: $0.accentHex) }
            ?? snapshot.accent
    }

    private var equippedSkin: ThreeBladeMetalSkinDetail? {
        snapshot.threeBladeMetalSkins.first {
            $0.id == equippedSkinId
        }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                VStack(alignment: .leading, spacing: 12) {
                    ProductScreenHeading(
                        title: "皮肤 · 配件 · 贴纸",
                        subtitle: "解锁后点击条目，立即应用到 3D 玩具",
                        symbol: "paintpalette.fill",
                        accent: accent)

                    HStack(spacing: 8) {
                        ProductStatusPill(title: "皮肤", symbol: "paintbrush.fill")
                        ProductStatusPill(title: "配件", symbol: "gearshape.fill")
                        ProductStatusPill(title: "贴纸", symbol: "seal.fill")
                    }

                    if let equippedSkin {
                        Label(
                            "3D 已应用：\(equippedSkin.displayName) · \(equippedSkin.metalName)",
                            systemImage: "checkmark.circle.fill")
                            .font(.product(.caption, weight: .semibold))
                            .foregroundStyle(accent)
                    } else if snapshot.progressionModel == .metalThreeBlade {
                        Label("正在确认 Unity Renderer 的实际材质", systemImage: "arrow.triangle.2.circlepath")
                            .font(.product(.caption, weight: .semibold))
                            .foregroundStyle(.orange)
                    }
                }
                .padding(16)
                .productGlass(cornerRadius: 22, tint: accent.opacity(0.08))

                if snapshot.progressionModel == .metalThreeBlade,
                   !snapshot.threeBladeMetalSkins.isEmpty {
                    ForEach(snapshot.threeBladeMetalSkins) { skin in
                        ThreeBladeMetalSkinRow(
                            skin: skin,
                            unlocked: snapshot.progressionLevel >= skin.level,
                            equipped: equippedSkinId == skin.id,
                            accent: accent,
                            onEquip: {
                                equippedSkinId = skin.id
                                state.equipThreeBladeMetalSkin(skin)
                            })
                    }
                } else {
                    ProductEmptyState(
                        title: "该玩具的外观收藏尚未开放",
                        detail: "三叶金属陀螺已经接入 10 套可解锁材质、配件和纹饰。",
                        symbol: "shippingbox.fill",
                        accent: accent)
                }
            }
            .padding(18)
        }
        .onChange(of: snapshot.equippedThreeBladeMetalSkinId) { newValue in
            equippedSkinId = newValue
        }
    }
}

private struct ThreeBladeMetalSkinRow: View {
    let skin: ThreeBladeMetalSkinDetail
    let unlocked: Bool
    let equipped: Bool
    let accent: Color
    let onEquip: () -> Void

    var body: some View {
        Button(action: onEquip) {
            ProductSelectionCard(
                selected: equipped,
                enabled: unlocked,
                accent: accent) {
                HStack(alignment: .top, spacing: 12) {
                    ThreeBladeMetalSkinSwatch(skin: skin, unlocked: unlocked)
                        .frame(width: 68, height: 68)

                    VStack(alignment: .leading, spacing: 4) {
                        HStack(spacing: 7) {
                            Text("LV.\(skin.level)")
                                .font(.product(.caption, weight: .bold).monospacedDigit())
                                .foregroundStyle(equipped ? accent : Color.white.opacity(0.52))
                            Text(skin.displayName)
                                .font(.product(.subheadline, weight: .bold))
                            if equipped {
                                ProductInlineTag(
                                    title: "EQUIPPED",
                                    accent: accent,
                                    filled: true)
                            }
                        }
                        Text("\(skin.metalName) · \(skin.patternName)")
                            .font(.product(.caption))
                            .foregroundStyle(Color.white.opacity(unlocked ? 0.72 : 0.32))
                        Text("贴纸 / 纹饰：\(skin.decorationName)")
                            .font(.product(.caption2))
                            .foregroundStyle(Color.white.opacity(unlocked ? 0.54 : 0.26))
                        Text("配件：\(skin.modificationName)")
                            .font(.product(.caption2))
                            .foregroundStyle(Color.white.opacity(unlocked ? 0.54 : 0.26))
                    }
                    Spacer(minLength: 0)
                    Image(systemName: unlocked ? (equipped ? "checkmark.circle.fill" : "chevron.right") : "lock.fill")
                        .font(.product(.caption, weight: .bold))
                        .foregroundStyle(equipped ? accent : Color.white.opacity(0.30))
                        .padding(.top, 2)
                }
            }
        }
        .buttonStyle(.plain)
        .disabled(!unlocked)
    }
}

private struct ThreeBladeMetalSkinSwatch: View {
    let skin: ThreeBladeMetalSkinDetail
    let unlocked: Bool

    private var patternSymbol: String {
        if skin.id.contains("honeycomb") { return "hexagon.fill" }
        if skin.id.contains("circuit") { return "cpu.fill" }
        if skin.id.contains("damascus") { return "water.waves" }
        if skin.id.contains("meteor") { return "sparkles" }
        if skin.id.contains("index") { return "clock.fill" }
        if skin.id.contains("guilloche") { return "circle.hexagongrid.fill" }
        if skin.id.contains("titanium") { return "flame.fill" }
        if skin.id.contains("aurora") { return "diamond.fill" }
        return "line.3.horizontal"
    }

    var body: some View {
        ZStack {
            NativeSquareArtwork(
                assetName: skin.thumbnailAssetName,
                fallbackSymbol: patternSymbol,
                colors: [
                    Color(productHex: skin.baseHex),
                    Color(productHex: skin.accentHex)
                ],
                cornerRadius: 15)
                .saturation(unlocked ? 1 : 0)
                .opacity(unlocked ? 1 : 0.42)

            if !unlocked {
                Image(systemName: "lock.fill")
                    .font(.product(.caption, weight: .black))
                    .foregroundStyle(Color.white.opacity(0.72))
                    .padding(7)
                    .background(Color.black.opacity(0.58), in: Circle())
            }
        }
        .shadow(color: Color.black.opacity(unlocked ? 0.22 : 0.10), radius: 8, y: 4)
        .clipped()
    }
}

private enum NativeArtworkLoader {
    private static let cache: NSCache<NSString, UIImage> = {
        let cache = NSCache<NSString, UIImage>()
        cache.countLimit = 96
        return cache
    }()

    static func image(named assetName: String) -> UIImage? {
        guard !assetName.isEmpty else { return nil }
        let key = assetName as NSString
        if let cached = cache.object(forKey: key) {
            return cached
        }
        if let image = UIImage(
            named: assetName,
            in: .main,
            compatibleWith: nil) {
            cache.setObject(image, forKey: key)
            return image
        }
        guard let url = Bundle.main.url(
            forResource: assetName,
            withExtension: "png") else {
            return nil
        }
        guard let image = UIImage(contentsOfFile: url.path) else { return nil }
        cache.setObject(image, forKey: key)
        return image
    }
}

private struct NativeSquareArtwork: View {
    let assetName: String
    let fallbackSymbol: String
    let colors: [Color]
    let cornerRadius: CGFloat
    var fitsInside = false

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                .fill(LinearGradient(
                    colors: colors,
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing))

            if let image = NativeArtworkLoader.image(named: assetName) {
                if fitsInside {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFit()
                        .padding(10)
                } else {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFill()
                }
            } else {
                Image(systemName: fallbackSymbol)
                    .font(.product(.title3, weight: .black))
                    .foregroundStyle(Color.white.opacity(0.86))
                    .shadow(color: .black.opacity(0.25), radius: 3, y: 2)
            }
        }
        .aspectRatio(1, contentMode: .fit)
        .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
        .accessibilityHidden(true)
    }
}

private struct ProductAppearanceEditor: View {
    @ObservedObject var state: ProductUiState
    let onClose: () -> Void
    @State private var section: ProductAppearanceSection = .skins

    private let columns = [
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10)
    ]

    private var accent: Color { state.currentAppearanceAccent }

    private var selectedStickerName: String {
        state.productStickers.first {
            $0.id == state.equippedProductStickerId
        }?.displayName ?? "正在确认"
    }

    var body: some View {
        ZStack(alignment: .bottom) {
            Color.black.opacity(0.12)
                .ignoresSafeArea()

            VStack(spacing: 0) {
                ProductSheetDragHandle(closeTitle: "关闭外观选择") {
                    onClose()
                }

                HStack(alignment: .top, spacing: 10) {
                    ProductScreenHeading(
                        title: "外观",
                        subtitle: "长按模型可再次打开；选择会直接同步到当前 3D 玩具",
                        symbol: "paintpalette.fill",
                        accent: accent)
                    Spacer(minLength: 0)
                    ProductIconButton(
                        symbol: "xmark",
                        accessibilityLabel: "关闭外观选择",
                        accent: accent,
                        action: onClose)
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 10)

                HStack {
                    ProductIconSegmentedControl(
                        options: ProductAppearanceSection.allCases,
                        selection: section,
                        accent: accent,
                        symbol: { $0.symbol },
                        title: { $0.title },
                        hint: { $0.hint },
                        onSelect: { selected in
                            withAnimation(.easeOut(
                                duration: FidgetUITokens.Motion.selectionDuration)) {
                                section = selected
                            }
                        })

                    Spacer()

                    ProductStatusPill(
                        title: section == .skins
                            ? state.currentAppearanceName
                            : selectedStickerName,
                        symbol: "checkmark.circle.fill",
                        accent: accent,
                        selected: true)
                        .lineLimit(1)
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 12)

                ScrollView {
                    LazyVGrid(columns: columns, spacing: 10) {
                        if section == .skins {
                            skinGrid
                        } else {
                            stickerGrid
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 18)
                }
            }
            .frame(maxHeight: 570)
            .background(
                Color.black.opacity(0.32),
                in: RoundedRectangle(cornerRadius: 26, style: .continuous))
            .productGlass(cornerRadius: 26, tint: accent.opacity(0.035))
            .clipShape(RoundedRectangle(cornerRadius: 26, style: .continuous))
            .padding(.horizontal, 8)
            .padding(.bottom, 8)
        }
        .productDesignSystem()
        .preferredColorScheme(.dark)
    }

    @ViewBuilder
    private var skinGrid: some View {
        if state.progressionModel == .metalThreeBlade,
           !state.threeBladeMetalSkins.isEmpty {
            ForEach(state.threeBladeMetalSkins) { skin in
                let unlocked = state.progressionLevel >= skin.level
                ProductAppearanceGridCard(
                    title: skin.displayName,
                    subtitle: unlocked ? skin.metalName : "LV.\(skin.level) 解锁",
                    selected: state.equippedThreeBladeMetalSkinId == skin.id,
                    enabled: unlocked,
                    accent: Color(productHex: skin.accentHex),
                    onSelect: { state.equipThreeBladeMetalSkin(skin) }) {
                        ThreeBladeMetalSkinSwatch(skin: skin, unlocked: unlocked)
                    }
            }
        } else {
            ProductAppearanceGridCard(
                title: state.currentAppearanceName,
                subtitle: "当前默认皮肤",
                selected: true,
                enabled: true,
                accent: accent,
                onSelect: {}) {
                    NativeSquareArtwork(
                        assetName: state.selectedModel.thumbnailAssetName,
                        fallbackSymbol: state.selectedModel.symbol,
                        colors: [
                            state.selectedModel.accent.opacity(0.90),
                            Color.white.opacity(0.18)
                        ],
                        cornerRadius: 15)
                }
        }
    }

    @ViewBuilder
    private var stickerGrid: some View {
        if state.productStickers.isEmpty {
            ProductEmptyState(
                title: "正在读取默认贴纸",
                detail: "贴纸目录由 Unity 运行时统一发布。",
                symbol: "seal.fill",
                accent: accent)
        } else {
            ForEach(state.productStickers) { sticker in
                let selected = state.equippedProductStickerId == sticker.id
                let stickerAccent = Color(productHex: sticker.tintHex)
                ProductAppearanceGridCard(
                    title: sticker.displayName,
                    subtitle: sticker.id == "none" ? "保持原始材质" : "默认贴纸",
                    selected: selected,
                    enabled: true,
                    accent: stickerAccent,
                    onSelect: { state.equipProductSticker(sticker) }) {
                        NativeSquareArtwork(
                            assetName: sticker.thumbnailAssetName,
                            fallbackSymbol: sticker.symbolName,
                            colors: [
                                stickerAccent.opacity(sticker.id == "none" ? 0.18 : 0.88),
                                Color.white.opacity(sticker.id == "none" ? 0.04 : 0.20)
                            ],
                            cornerRadius: 15,
                            fitsInside: sticker.id != "none")
                    }
            }
        }
    }
}

private struct ProductAppearanceGridCard<Preview: View>: View {
    let title: String
    let subtitle: String
    let selected: Bool
    let enabled: Bool
    let accent: Color
    let onSelect: () -> Void
    let preview: Preview

    init(
        title: String,
        subtitle: String,
        selected: Bool,
        enabled: Bool,
        accent: Color,
        onSelect: @escaping () -> Void,
        @ViewBuilder preview: () -> Preview) {
        self.title = title
        self.subtitle = subtitle
        self.selected = selected
        self.enabled = enabled
        self.accent = accent
        self.onSelect = onSelect
        self.preview = preview()
    }

    var body: some View {
        Button(action: onSelect) {
            ProductSelectionCard(
                selected: selected,
                enabled: enabled,
                accent: accent) {
                    VStack(alignment: .leading, spacing: 9) {
                        preview
                            .frame(maxWidth: .infinity)
                            .frame(height: 108)

                        HStack(alignment: .firstTextBaseline, spacing: 5) {
                            Text(title)
                                .font(.product(.caption, weight: .bold))
                                .foregroundStyle(Color.white.opacity(enabled ? 0.90 : 0.38))
                                .lineLimit(1)
                            Spacer(minLength: 0)
                            if selected {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundStyle(accent)
                                    .accessibilityHidden(true)
                            }
                        }

                        Text(subtitle)
                            .font(.product(.caption2))
                            .foregroundStyle(Color.white.opacity(enabled ? 0.50 : 0.26))
                            .lineLimit(1)
                    }
                }
        }
        .buttonStyle(.plain)
        .disabled(!enabled)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title)，\(subtitle)")
        .accessibilityAddTraits(selected ? .isSelected : [])
    }
}

private struct ProgressionVerticalRail: View {
    let progress: Double
    let accent: Color

    var body: some View {
        GeometryReader { geometry in
            let clampedProgress = max(0, min(1, progress))
            let lineWidth: CGFloat = 3
            let segmentGap: CGFloat = 4
            let currentLength = min(14, max(8, geometry.size.height * 0.025))
            let currentCenter = geometry.size.height * clampedProgress
            let currentOffset = min(
                max(0, geometry.size.height - currentLength),
                max(0, currentCenter - currentLength * 0.5))
            let completedHeight = max(0, currentOffset - segmentGap)
            let futureOffset = min(
                geometry.size.height,
                currentOffset + currentLength + segmentGap)
            let futureHeight = max(0, geometry.size.height - futureOffset)

            ZStack(alignment: .top) {
                if completedHeight > 0 {
                    Capsule(style: .continuous)
                        .fill(accent.opacity(0.42))
                        .frame(width: lineWidth, height: completedHeight)
                }

                Capsule(style: .continuous)
                    .fill(accent.opacity(0.92))
                    .frame(width: lineWidth, height: currentLength)
                    .offset(y: currentOffset)

                if futureHeight > 0 {
                    Capsule(style: .continuous)
                        .fill(Color.white.opacity(0.10))
                        .frame(width: lineWidth, height: futureHeight)
                        .offset(y: futureOffset)
                }
            }
            .frame(maxWidth: .infinity, alignment: .center)
        }
    }
}

private struct ProgressionLevelRow: View {
    let levelLabel: String
    let title: String
    let unlockName: String
    let level: Int
    let model: SpinnerModel
    let skin: ThreeBladeMetalSkinDetail?
    let unlocked: Bool
    let current: Bool
    let accent: Color

    var body: some View {
        ProductSelectionCard(
            selected: false,
            enabled: unlocked,
            accent: accent) {
            HStack(alignment: .center, spacing: 12) {
                ProgressionUnlockThumbnail(
                    model: model,
                    skin: skin,
                    accent: accent,
                    unlocked: unlocked,
                    showsLock: !unlocked)
                    .frame(width: 58, height: 58)

                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 7) {
                        Text(levelLabel)
                            .font(.product(.caption, weight: .bold).monospacedDigit())
                            .foregroundStyle(current ? accent : Color.white.opacity(0.52))
                        Text(title)
                            .font(.product(.subheadline, weight: .bold))
                        if current {
                            Circle()
                                .fill(accent.opacity(0.88))
                                .frame(width: 7, height: 7)
                                .accessibilityHidden(true)
                        } else if unlocked {
                            Circle()
                                .fill(accent.opacity(0.22))
                                .overlay {
                                    Circle()
                                        .stroke(accent.opacity(0.24), lineWidth: 0.5)
                                }
                                .frame(width: 7, height: 7)
                                .accessibilityHidden(true)
                        }
                    }
                    Text("解锁：\(unlockName)")
                        .font(.product(.caption))
                        .foregroundStyle(Color.white.opacity(unlocked ? 0.66 : 0.32))
                }
                Spacer(minLength: 0)
            }
        }
        .accessibilityValue(
            current ? "当前级别" : (unlocked ? "已完成" : "未解锁"))
    }
}

private struct ProgressionBadgeAchievements: View, Equatable {
    let snapshot: ProgressionCatalogSnapshot
    @State private var selectedScope: ProductBadgeScope = .toy
    @State private var selectedBadge: ProductBadgeDetail?

    static func == (
        lhs: ProgressionBadgeAchievements,
        rhs: ProgressionBadgeAchievements) -> Bool {
        lhs.snapshot == rhs.snapshot
    }

    private var accent: Color { snapshot.accent }
    private var columns: [GridItem] {
        ProductBadgeLayoutTokens.catalogColumns
    }

    private var badges: [ProductBadgeDetail] {
        switch selectedScope {
        case .toy: return snapshot.toyBadges
        case .collector: return snapshot.collectorBadges
        case .challenge: return snapshot.challengeBadges
        case .legacy: return snapshot.legacyBadges
        }
    }

    private var recentTarget: ProductBadgeDetail? {
        badges.first { $0.state == .inProgress }
            ?? badges.first { $0.state == .locked }
            ?? badges.first { $0.state == .hidden }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                VStack(alignment: .leading, spacing: 13) {
                    HStack(alignment: .top, spacing: 10) {
                        ProductScreenHeading(
                            title: "BADGES",
                            subtitle: "独立目标、真实进度与可收藏奖励",
                            symbol: "seal.fill",
                            accent: accent)
                        Spacer(minLength: 0)
                        ProductInlineTag(
                            title: "◆ \(snapshot.badgeShardBalance)",
                            accent: Color.white.opacity(0.72))
                    }

                    if let recentTarget {
                        Divider().overlay(Color.white.opacity(0.08))
                        Button {
                            selectedBadge = recentTarget
                        } label: {
                            HStack(spacing: 13) {
                                ProductRarityBadge(
                                    assetName: recentTarget.assetName,
                                    token: recentTarget.tokenLine,
                                    shortName: recentTarget.shortName,
                                    grade: recentTarget.grade.rawValue,
                                    state: recentTarget.state.rawValue,
                                    progress: recentTarget.progress,
                                    renderingMode: .catalog)
                                    .frame(width: ProductBadgeLayoutTokens.recentTargetWidth)
                                VStack(alignment: .leading, spacing: 5) {
                                    Text("最近目标")
                                        .font(.product(.caption, weight: .bold))
                                        .foregroundStyle(Color.white.opacity(0.44))
                                    Text(recentTarget.hidden ? "加密核心" : recentTarget.title)
                                        .font(.product(.headline, weight: .bold))
                                        .foregroundStyle(Color.white.opacity(0.92))
                                    Text(recentTarget.hidden
                                         ? "继续真实盘玩以解密条件"
                                         : recentTarget.description)
                                        .font(.product(.caption))
                                        .foregroundStyle(Color.white.opacity(0.50))
                                        .lineLimit(2)
                                }
                                Spacer(minLength: 0)
                                Image(systemName: "chevron.right")
                                    .foregroundStyle(Color.white.opacity(0.30))
                            }
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(16)
                .productGlass(cornerRadius: 22, tint: accent.opacity(0.08))

                Picker("Badge 分类", selection: $selectedScope) {
                    ForEach(ProductBadgeScope.allCases) { scope in
                        Text(scope.title).tag(scope)
                    }
                }
                .pickerStyle(.segmented)

                if badges.isEmpty {
                    ProductEmptyState(
                        title: "正在同步 Badge",
                        detail: "目录由 Unity 运行时发布。",
                        symbol: "seal",
                        accent: accent)
                } else {
                    LazyVGrid(
                        columns: columns,
                        spacing: ProductBadgeLayoutTokens.catalogRowSpacing) {
                        ForEach(badges) { badge in
                            Button {
                                selectedBadge = badge
                            } label: {
                                ProductRarityBadge(
                                    assetName: badge.assetName,
                                    token: badge.tokenLine,
                                    shortName: badge.shortName,
                                    grade: badge.grade.rawValue,
                                    state: badge.state.rawValue,
                                    progress: badge.progress,
                                    renderingMode: .catalog)
                                    .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(.plain)
                            .accessibilityHint("打开 Badge 详情")
                        }
                    }
                }
            }
            .padding(.horizontal, ProductBadgeLayoutTokens.catalogHorizontalPadding)
            .padding(.vertical, 18)
        }
        .sheet(item: $selectedBadge) { badge in
            ProductBadgeDetailSheet(
                badge: badge,
                accent: accent,
                toyName: selectedScope == .toy
                    ? snapshot.progressionModel.title
                    : selectedScope.title)
        }
    }
}

private struct ProductBadgeDetailSheet: View {
    let badge: ProductBadgeDetail
    let accent: Color
    let toyName: String
    @Environment(\.dismiss) private var dismiss
    @State private var shareImage: UIImage?
    @State private var showsShareSheet = false

    private var statusTitle: String {
        switch badge.state {
        case .locked: return "尚未开始"
        case .inProgress: return "进行中"
        case .hidden: return "隐藏成就"
        case .unlocked: return "已获得"
        }
    }

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 18) {
                    ProductRarityBadge(
                        assetName: badge.assetName,
                        token: badge.tokenLine,
                        shortName: badge.shortName,
                        grade: badge.grade.rawValue,
                        state: badge.state.rawValue,
                        progress: badge.progress)
                        .frame(width: ProductBadgeLayoutTokens.detailWidth)
                        .padding(.top, 12)

                    VStack(alignment: .leading, spacing: 14) {
                        HStack {
                            Text(badge.hidden ? "加密核心" : badge.title)
                                .font(.product(.title2, weight: .bold))
                            Spacer()
                            ProductInlineTag(
                                title: statusTitle,
                                accent: accent,
                                filled: badge.unlocked)
                        }
                        Text(badge.hidden
                             ? "继续真实盘玩以解密名称和条件。"
                             : badge.description)
                            .font(.product(.body))
                            .foregroundStyle(Color.white.opacity(0.62))
                        if !badge.hidden {
                            ProductProgressGauge(
                                value: badge.progress,
                                accent: Color.white.opacity(0.76))
                            HStack {
                                Text(String(
                                    format: "%.0f / %.0f",
                                    badge.currentValue,
                                    badge.targetValue))
                                Spacer()
                                Text("难度等级 · \(badge.grade.rawValue)")
                            }
                            .font(.product(.caption).monospacedDigit())
                            .foregroundStyle(Color.white.opacity(0.48))
                        }
                    }
                    .padding(16)
                    .productGlass(cornerRadius: 22)

                    ProductSectionCard("奖励", symbol: "sparkles") {
                        HStack(spacing: 12) {
                            ProductCompactMetric(
                                title: "XP",
                                value: "+\(badge.experienceReward)")
                            ProductCompactMetric(
                                title: "徽记碎片",
                                value: "+\(badge.shardReward)")
                        }
                    }

                    if badge.unlocked {
                        ProductSecondaryActionButton(
                            title: "生成 1:1 分享卡",
                            symbol: "square.and.arrow.up") {
                            ProductBadgeShareRenderer.render(
                                badge: badge,
                                toyName: toyName) { image in
                                shareImage = image
                                showsShareSheet = image != nil
                            }
                        }
                        .accessibilityHint("生成不包含个人信息的 1080 方形图片")
                    }
                }
                .padding(18)
            }
            .background(ProductBackdrop().ignoresSafeArea())
            .navigationTitle("Badge")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("完成") { dismiss() }
                }
            }
        }
        .navigationViewStyle(.stack)
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .sheet(isPresented: $showsShareSheet) {
            if let shareImage {
                ProductBadgeActivitySheet(items: [shareImage])
            }
        }
    }
}

private struct ProductBadgeShareCard: View {
    let badge: ProductBadgeDetail
    let toyName: String

    var body: some View {
        ZStack {
            Color(red: 0.025, green: 0.032, blue: 0.034)
            ProductBadgeLeatherTexture(grainScale: 0.45)
                .opacity(0.55)
            VStack(spacing: 11) {
                HStack {
                    Text("FIDGETING")
                        .font(.product(size: 13, weight: .bold))
                    Spacer()
                    Text("BADGE")
                        .font(.product(size: 11, weight: .bold))
                        .foregroundStyle(Color.white.opacity(0.48))
                }

                ProductRarityBadge(
                    assetName: badge.assetName,
                    token: badge.tokenLine,
                    shortName: badge.shortName,
                    grade: badge.grade.rawValue,
                    state: ProductBadgeState.unlocked.rawValue,
                    progress: 1)
                    .frame(width: ProductBadgeLayoutTokens.shareCardWidth)

                VStack(spacing: 6) {
                    Text(badge.title)
                        .font(.product(size: 22, weight: .bold))
                        .foregroundStyle(Color.white.opacity(0.96))
                        .lineLimit(1)
                        .minimumScaleFactor(0.72)
                    Text(toyName)
                        .font(.product(size: 13, weight: .semibold))
                        .foregroundStyle(Color.white.opacity(0.58))
                    Text(badge.description)
                        .font(.product(size: 11, weight: .medium))
                        .foregroundStyle(Color.white.opacity(0.46))
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                }

                HStack {
                    Text(badge.grade.rawValue.uppercased())
                    Spacer()
                    Text(ProductBadgeShareRenderer.dateText(badge.unlockedAtUtc))
                }
                .font(.product(size: 9, weight: .bold).monospacedDigit())
                .foregroundStyle(Color.white.opacity(0.36))
            }
            .padding(20)
        }
        .aspectRatio(1, contentMode: .fit)
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .accessibilityElement(children: .combine)
    }
}

@MainActor
private enum ProductBadgeShareRenderer {
    static func render(
        badge: ProductBadgeDetail,
        toyName: String,
        completion: @escaping (UIImage?) -> Void) {
        // The badge face loads its artwork asynchronously off a background
        // decode queue; without prewarming, the snapshot below can fire
        // before that completes and capture the empty-artwork placeholder.
        // Forcing the image into cache first guarantees `onAppear` resolves
        // it synchronously via the artwork cache's synchronous cache-hit path.
        ProductRarityBadge.prewarmFullArtwork(assetName: badge.assetName) {
            renderAfterArtworkIsCached(
                badge: badge,
                toyName: toyName,
                completion: completion)
        }
    }

    private static func renderAfterArtworkIsCached(
        badge: ProductBadgeDetail,
        toyName: String,
        completion: @escaping (UIImage?) -> Void) {
        let size = CGSize(width: 360, height: 360)
        let controller = UIHostingController(
            rootView: ProductBadgeShareCard(badge: badge, toyName: toyName)
                .frame(width: size.width, height: size.height))
        let window: UIWindow
        if let scene = UIApplication.shared.connectedScenes
            .compactMap({ $0 as? UIWindowScene })
            .first {
            window = UIWindow(windowScene: scene)
        } else {
            window = UIWindow(frame: CGRect(origin: .zero, size: size))
        }
        window.frame = CGRect(origin: .zero, size: size)
        window.rootViewController = controller
        window.windowLevel = .alert + 1
        window.alpha = 0.01
        window.isHidden = false
        controller.view.frame = window.bounds
        controller.view.backgroundColor = .black
        controller.beginAppearanceTransition(true, animated: false)
        controller.endAppearanceTransition()
        controller.view.setNeedsLayout()
        DispatchQueue.main.async {
            controller.view.layoutIfNeeded()
            let format = UIGraphicsImageRendererFormat()
            format.scale = 3
            format.opaque = true
            let image = UIGraphicsImageRenderer(
                size: size,
                format: format).image { _ in
                controller.view.drawHierarchy(
                    in: controller.view.bounds,
                    afterScreenUpdates: true)
            }
            window.isHidden = true
            completion(image)
        }
    }

    static func dateText(_ iso8601: String) -> String {
        guard let date = ISO8601DateFormatter().date(from: iso8601) else {
            return "LOCAL COLLECTION"
        }
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy.MM.dd"
        return formatter.string(from: date)
    }
}

private struct ProductBadgeActivitySheet: UIViewControllerRepresentable {
    let items: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: items, applicationActivities: nil)
    }

    func updateUIViewController(
        _ uiViewController: UIActivityViewController,
        context: Context) {
    }
}

private struct LibraryToyBadgeRow: View {
    @ObservedObject var state: ProductUiState
    let onOpenCatalog: () -> Void

    private var spotlightBadges: [ProductBadgeDetail] {
        let unlocked = state.toyBadgeCatalog
            .filter(\.unlocked)
            .sorted { $0.displayOrder > $1.displayOrder }
        let currentTarget = state.toyBadgeCatalog.first {
            $0.state == .inProgress
        }
        var selection = Array(unlocked.prefix(currentTarget == nil ? 3 : 2))
        if let currentTarget,
           !selection.contains(where: { $0.id == currentTarget.id }) {
            selection.append(currentTarget)
        }
        if selection.count < 3 {
            let selectedIDs = Set(selection.map(\.id))
            selection.append(contentsOf: state.toyBadgeCatalog
                .filter { !selectedIDs.contains($0.id) }
                .prefix(3 - selection.count))
        }
        return Array(selection.prefix(3))
    }

    var body: some View {
        Button(action: onOpenCatalog) {
            HStack(spacing: 16) {
                ForEach(spotlightBadges) { badge in
                    ProductRarityBadge(
                        assetName: badge.assetName,
                        token: badge.tokenLine,
                        shortName: badge.shortName,
                        grade: badge.grade.rawValue,
                        state: badge.state.rawValue,
                        progress: badge.progress,
                        renderingMode: .catalog)
                        .frame(width: 42)
                        .accessibilityHidden(true)
                }

                if spotlightBadges.isEmpty {
                    Image(systemName: "seal")
                        .font(.product(size: 18, weight: .light))
                        .foregroundStyle(Color.white.opacity(0.22))
                        .frame(width: 44, height: 44)
                        .accessibilityHidden(true)
                }
            }
            .frame(minWidth: 52, minHeight: 44)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("library-toy-badge-row")
        .accessibilityLabel(
            "打开 \(state.selectedModel.title) 的 Badge 图鉴")
        .accessibilityHint("打开当前陀螺的 Badge 成就目录")
        .onAppear {
            ProductRarityBadge.prewarmCatalogArtwork(
                assetNames: spotlightBadges.map(\.assetName))
        }
        .onChange(of: state.toyBadgeCatalog) { _ in
            ProductRarityBadge.prewarmCatalogArtwork(
                assetNames: spotlightBadges.map(\.assetName))
        }
    }
}

private struct ProductModeBar: View {
    @ObservedObject var state: ProductUiState

    var body: some View {
        ProductIconSegmentedControl(
            options: SpinnerInteractionMode.allCases,
            selection: state.interactionMode,
            accent: state.currentAppearanceAccent,
            symbol: { $0.symbol },
            title: { $0.title },
            hint: { $0.subtitle }) { mode in
                let selected = state.interactionMode == mode
                UnityBridge.feedback(selected ? .light : .medium)
                state.selectInteractionMode(mode)
        }
        .frame(maxWidth: .infinity)
        .padding(.top, 4)
        .productDesignSystem()
        .preferredColorScheme(.dark)
    }
}

private struct DetentTuningPanel: View {
    @ObservedObject var state: ProductUiState
    private var accent: Color { state.currentAppearanceAccent }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 1) {
                    Text("DETENT LAB · \(state.detentPresetName)")
                        .font(.product(.caption, weight: .bold))
                        .foregroundStyle(.white)
                    if state.detentPresetDetents > 0 {
                        Text(String(
                            format: "%d 段/圈 · %.0f°",
                            state.detentPresetDetents,
                            360.0 / Double(state.detentPresetDetents)))
                            .font(.product(.caption2).monospacedDigit())
                            .foregroundStyle(Color.white.opacity(0.55))
                    }
                }
                Spacer()
                ProductInlineTag(title: "LIVE", accent: accent)
            }

            if state.detentPresetCount > 0 {
                HStack(spacing: 3) {
                    ForEach(Array(0..<state.detentPresetCount), id: \.self) { index in
                        let selected = index == state.detentPresetIndex
                        Button {
                            UnityBridge.feedback(selected ? .light : .medium)
                            state.selectDetentPreset(index)
                        } label: {
                            Text("\(index + 1)")
                                .font(.product(.caption, weight: .bold))
                                .frame(maxWidth: .infinity)
                                .frame(height: 26)
                                .foregroundStyle(
                                    selected ? Color.white : Color.white.opacity(0.48))
                                .background {
                                    if selected {
                                        RoundedRectangle(cornerRadius: 9, style: .continuous)
                                            .fill(accent.opacity(0.18))
                                    }
                                }
                        }
                        .buttonStyle(.plain)
                        .accessibilityLabel("Detent preset \(index + 1)")
                    }
                }
                .padding(3)
                .background(Color.black.opacity(0.26), in: RoundedRectangle(
                    cornerRadius: 12,
                    style: .continuous))
            } else {
                ProgressView().tint(.white)
            }

            tuningRow(
                title: "Intensity",
                value: state.detentTuningIntensity,
                set: state.setDetentIntensityOverride)
            tuningRow(
                title: "Sharpness",
                value: state.detentTuningSharpness,
                set: state.setDetentSharpnessOverride)
        }
        .padding(11)
        .productGlass(
            cornerRadius: 18,
            tint: Color.black.opacity(0.24),
            interactive: true)
        .preferredColorScheme(.dark)
    }

    private func tuningRow(
        title: String,
        value: Double,
        set: @escaping (Double) -> Void) -> some View {
        HStack(spacing: 7) {
            Text(title)
                .font(.product(.caption2, weight: .semibold))
                .foregroundStyle(Color.white.opacity(0.72))
                .frame(width: 58, alignment: .leading)
            Slider(
                value: Binding(
                    get: { value },
                    set: set),
                in: 0...1,
                step: 0.01)
                .tint(accent)
            Text(String(format: "%.2f", value))
                .font(.product(.caption2, weight: .semibold).monospacedDigit())
                .foregroundStyle(.white)
                .frame(width: 30, alignment: .trailing)
        }
        .frame(height: 22)
    }
}

private struct CollectorBonusTier: Identifiable {
    let rank: Int
    let global: Int
    let focus: Int

    var id: Int { rank }
}

private struct CollectorProfile: View {
    @ObservedObject var state: ProductUiState
    @State private var selectedSection = 0
    @State private var selectedCollectorBadge: ProductBadgeDetail?

    private let bonusTiers = [
        CollectorBonusTier(rank: 1, global: 0, focus: 5),
        CollectorBonusTier(rank: 5, global: 2, focus: 7),
        CollectorBonusTier(rank: 10, global: 4, focus: 10),
        CollectorBonusTier(rank: 15, global: 6, focus: 13),
        CollectorBonusTier(rank: 20, global: 8, focus: 16),
        CollectorBonusTier(rank: 25, global: 9, focus: 18),
        CollectorBonusTier(rank: 30, global: 10, focus: 20)
    ]

    private var accent: Color { state.currentAppearanceAccent }

    private var rankExperienceText: String {
        let current = max(
            0,
            state.collectorTotalExperience - state.collectorRankStartExperience)
        let required = max(
            1,
            state.collectorNextRankExperience - state.collectorRankStartExperience)
        if state.collectorRank >= 30 { return "最高藏家等级" }
        return String(format: "%.0f / %.0f 藏家经验", current, required)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 12) {
                    HStack(alignment: .top) {
                        VStack(alignment: .leading, spacing: 3) {
                            Text("藏家 · \(state.collectorRank)")
                                .font(.product(.title, weight: .bold).monospacedDigit())
                                .foregroundStyle(Color.white.opacity(0.94))
                            Text("实际盘玩提升等级，收藏仅提供少量经验")
                                .font(.product(.caption))
                                .foregroundStyle(Color.white.opacity(0.50))
                        }
                        Spacer()
                        Image(systemName: "person.crop.circle")
                            .font(.product(size: 32, weight: .light))
                            .foregroundStyle(Color.white.opacity(0.62))
                    }

                    ProductProgressGauge(
                        value: state.collectorFraction,
                        accent: accent)
                    HStack {
                        Text(rankExperienceText)
                        Spacer()
                        Text("节奏 \(state.collectorValidDays)/5")
                    }
                    .font(.product(.caption).monospacedDigit())
                    .foregroundStyle(Color.white.opacity(0.54))
                }
                .padding(17)
                .productGlass(cornerRadius: 23, tint: accent.opacity(0.035))

                Picker("藏家栏目", selection: $selectedSection) {
                    Text("等级").tag(0)
                    Text("Badge").tag(1)
                    Text("收藏").tag(2)
                }
                .pickerStyle(.segmented)

                switch selectedSection {
                case 0:
                    rankOverview
                case 1:
                    badgeCollection
                default:
                    collection
                }
            }
            .padding(.horizontal, 18)
            .padding(.top, 16)
            .padding(.bottom, 28)
        }
        .background(ProductBackdrop().ignoresSafeArea())
        .sheet(item: $selectedCollectorBadge) { badge in
            ProductBadgeDetailSheet(
                badge: badge,
                accent: accent,
                toyName: "藏家")
        }
    }

    private var rankOverview: some View {
        VStack(alignment: .leading, spacing: 14) {
            Menu {
                ForEach(SpinnerModel.shippingCases) { model in
                    Button {
                        state.setCollectorFocus(model)
                    } label: {
                        Label(
                            model == state.collectorFocusModel
                                ? "\(model.title) · 当前主玩"
                                : model.title,
                            systemImage: model == state.collectorFocusModel
                                ? "checkmark.circle.fill"
                                : model.symbol)
                    }
                    .disabled(
                        model != state.collectorFocusModel
                            && !state.collectorCanChangeFocus)
                }
            } label: {
                HStack(spacing: 12) {
                    Image(systemName: state.collectorFocusModel.symbol)
                        .font(.product(.title3, weight: .semibold))
                        .foregroundStyle(Color.white.opacity(0.82))
                        .frame(width: 38, height: 38)
                        .background(Color.white.opacity(0.06), in: Circle())
                    VStack(alignment: .leading, spacing: 3) {
                        Text("主玩")
                            .font(.product(.caption))
                            .foregroundStyle(Color.white.opacity(0.44))
                        Text(state.collectorFocusModel.title)
                            .font(.product(.headline))
                            .foregroundStyle(Color.white.opacity(0.92))
                    }
                    Spacer()
                    VStack(alignment: .trailing, spacing: 3) {
                        Text("+\(Int((state.collectorFocusBonus * 100).rounded()))%")
                            .font(.product(.headline).monospacedDigit())
                        Text(state.collectorCanChangeFocus ? "可更换" : "明日可更换")
                            .font(.product(.caption2))
                            .foregroundStyle(Color.white.opacity(0.42))
                    }
                    .foregroundStyle(Color.white.opacity(0.84))
                    Image(systemName: "chevron.up.chevron.down")
                        .font(.product(.caption2, weight: .bold))
                        .foregroundStyle(Color.white.opacity(0.34))
                }
                .padding(15)
                .productGlass(cornerRadius: 20, tint: accent.opacity(0.025), interactive: true)
            }
            .accessibilityLabel("主玩，\(state.collectorFocusModel.title)")
            .accessibilityHint(state.collectorCanChangeFocus ? "打开主玩选择" : "明日可以更换")

            HStack(spacing: 10) {
                ProductMetricCard(
                    title: "全局加成",
                    value: "+\(Int((state.collectorGlobalBonus * 100).rounded()))%",
                    symbol: "square.grid.2x2")
                ProductMetricCard(
                    title: "主玩加成",
                    value: "+\(Int((state.collectorFocusBonus * 100).rounded()))%",
                    symbol: "scope")
            }

            VStack(alignment: .leading, spacing: 0) {
                Text("加成节点")
                    .font(.product(.headline))
                    .padding(.bottom, 10)
                ForEach(bonusTiers) { tier in
                    HStack {
                        Text("藏家 \(tier.rank)")
                            .font(.product(.subheadline, weight: .semibold).monospacedDigit())
                        Spacer()
                        Text("全局 +\(tier.global)% · 主玩 +\(tier.focus)%")
                            .font(.product(.caption).monospacedDigit())
                            .foregroundStyle(Color.white.opacity(0.54))
                        Image(systemName: state.collectorRank >= tier.rank
                              ? "checkmark.circle.fill"
                              : "circle")
                            .foregroundStyle(Color.white.opacity(
                                state.collectorRank >= tier.rank ? 0.76 : 0.20))
                    }
                    .padding(.vertical, 9)
                    if tier.rank != bonusTiers.last?.rank {
                        Divider().overlay(Color.white.opacity(0.07))
                    }
                }
            }
            .padding(16)
            .productGlass(cornerRadius: 21)

            Text("藏家加成只作用于真实手动互动，并与 Combo 相加后封顶 1.50×；离线经验和 AUTO 不享受加成。")
                .font(.product(.footnote))
                .foregroundStyle(Color.white.opacity(0.48))
                .padding(.horizontal, 3)
        }
    }

    private var badgeCollection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("藏家 Badge")
                    .font(.product(.title3, weight: .bold))
                Spacer()
                Text("\(state.collectorUnlockedBadgeCount)/\(state.collectorTotalBadgeCount)")
                    .font(.product(.subheadline, weight: .semibold).monospacedDigit())
                    .foregroundStyle(Color.white.opacity(0.48))
                ProductInlineTag(
                    title: "◆ \(state.badgeShardBalance)",
                    accent: Color.white.opacity(0.72))
            }

            if state.collectorBadgeCatalog.isEmpty {
                ProductEmptyState(
                    title: "正在同步 Badge",
                    detail: "藏家目录由 Unity 运行时发布。",
                    symbol: "seal",
                    accent: accent)
            } else {
                LazyVGrid(
                    columns: ProductBadgeLayoutTokens.catalogColumns,
                    spacing: ProductBadgeLayoutTokens.catalogRowSpacing) {
                    ForEach(state.collectorBadgeCatalog) { badge in
                        Button {
                            selectedCollectorBadge = badge
                        } label: {
                            ProductRarityBadge(
                                assetName: badge.assetName,
                                token: badge.tokenLine,
                                shortName: badge.shortName,
                                grade: badge.grade.rawValue,
                                state: badge.state.rawValue,
                                progress: badge.progress,
                                renderingMode: .catalog)
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.plain)
                        .accessibilityHint("打开 Badge 详情")
                    }
                }
            }
        }
    }

    private var collection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 10) {
                ProductMetricCard(
                    title: "已把玩",
                    value: "\(state.collectorDiscoveredModelCount) 件",
                    symbol: "square.grid.2x2")
                ProductMetricCard(
                    title: "外观收藏",
                    value: "\(state.collectorCosmeticCount) 件",
                    symbol: "circle.hexagongrid.fill")
            }

            VStack(alignment: .leading, spacing: 0) {
                Text("我的收藏")
                    .font(.product(.headline))
                    .padding(.bottom, 8)
                ForEach(SpinnerModel.shippingCases) { model in
                    let discovered = state.collectorDiscoveredModelIds.contains(model.rawValue)
                    HStack(spacing: 11) {
                        Image(systemName: model.symbol)
                            .frame(width: 28)
                            .foregroundStyle(Color.white.opacity(discovered ? 0.78 : 0.20))
                        Text(model.title)
                            .font(.product(.subheadline, weight: .medium))
                            .foregroundStyle(Color.white.opacity(discovered ? 0.88 : 0.34))
                        Spacer()
                        Text(discovered ? "已加入" : "待发现")
                            .font(.product(.caption))
                            .foregroundStyle(Color.white.opacity(discovered ? 0.54 : 0.22))
                        Image(systemName: discovered ? "checkmark.circle.fill" : "circle")
                            .foregroundStyle(Color.white.opacity(discovered ? 0.70 : 0.16))
                    }
                    .padding(.vertical, 11)
                    if model != SpinnerModel.shippingCases.last {
                        Divider().overlay(Color.white.opacity(0.07))
                    }
                }
            }
            .padding(16)
            .productGlass(cornerRadius: 21)

            Text("首次真实把玩一款玩具会将它加入收藏；购买或解锁外观只提供少量一次性藏家经验。")
                .font(.product(.footnote))
                .foregroundStyle(Color.white.opacity(0.48))
                .padding(.horizontal, 3)
        }
    }
}

private struct EnvironmentWallpaperImage: View {
    let theme: EnvironmentTheme
    let model: SpinnerModel
    let showsAppChrome: Bool

    private var image: UIImage? {
        let modelAssetName = theme.wallpaperAssetName(for: model)
        if let bundled = UIImage(named: modelAssetName) {
            return bundled
        }
        guard let path = Bundle.main.path(
            forResource: modelAssetName,
            ofType: "png") else { return nil }
        return UIImage(contentsOfFile: path)
    }

    private var fallbackColors: [Color] {
        switch theme {
        case .adaptive:
            return [
                Color(red: 0.015, green: 0.017, blue: 0.022),
                model.accent.opacity(0.16),
                Color.black
            ]
        case .canyon:
            return [Color.black, Color(red: 0.08, green: 0.13, blue: 0.12)]
        case .cyberpunk:
            return [Color.black, Color(red: 0.02, green: 0.17, blue: 0.23)]
        case .mineralRidge:
            return [
                Color(red: 0.24, green: 0.24, blue: 0.23),
                Color(red: 0.08, green: 0.085, blue: 0.08),
                Color.black
            ]
        }
    }

    var body: some View {
        ZStack {
            if let image {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
            } else {
                LinearGradient(
                    colors: fallbackColors,
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing)
                    .overlay {
                        Image(systemName: "photo.on.rectangle.angled")
                            .font(.system(size: 34, weight: .thin))
                            .foregroundStyle(Color.white.opacity(0.25))
                    }
            }

            if showsAppChrome {
                VStack(spacing: 0) {
                    Text("我的陀螺")
                        .font(.product(.caption, weight: .bold))
                        .foregroundStyle(.white)
                        .padding(.top, 28)

                    Text("选择一个陀螺")
                        .font(.product(.headline, weight: .bold))
                        .foregroundStyle(.white)
                        .padding(.top, 14)
                    Text("左右滑动查看 45° 实时模型")
                        .font(.product(size: 9, weight: .medium))
                        .foregroundStyle(Color.white.opacity(0.52))
                        .padding(.top, 3)

                    Spacer(minLength: 0)

                    Text(model.title)
                        .font(.product(.subheadline, weight: .bold))
                        .foregroundStyle(.white)
                    Text(model.subtitle)
                        .font(.product(size: 9, weight: .medium))
                        .foregroundStyle(Color.white.opacity(0.56))
                        .padding(.top, 3)
                        .padding(.bottom, 24)
                }
            }
        }
    }
}

private final class SceneWallpaperPickerTransition: ObservableObject {
    static let scaleDuration = 0.52

    @Published private(set) var entered: Bool

    init(startsEntered: Bool) {
        entered = startsEntered
    }

    func begin(reduceMotion: Bool) {
        guard !entered else { return }
        entered = true
    }
}

private struct SceneWallpaperPicker: View {
    @ObservedObject var state: ProductUiState
    @ObservedObject private var transition: SceneWallpaperPickerTransition
    let capturedScreen: UIImage?
    let capturedTheme: EnvironmentTheme
    let onSelect: (EnvironmentTheme) -> Void

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var dragOffset: CGFloat = 0
    @State private var isSettling = false

    private let previewScale = 0.66
    private let neighborSpacing: CGFloat = 22
    private let swipeThreshold: CGFloat = 48
    private let carouselSettleDuration = 0.24

    private var entered: Bool { transition.entered }

    private var activeWindowSafeAreaInsets: UIEdgeInsets {
        UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .flatMap(\.windows)
            .first(where: { $0.isKeyWindow })?
            .safeAreaInsets ?? .zero
    }

    init(
        state: ProductUiState,
        capturedScreen: UIImage?,
        capturedTheme: EnvironmentTheme,
        startsEntered: Bool = false,
        transition: SceneWallpaperPickerTransition? = nil,
        onSelect: @escaping (EnvironmentTheme) -> Void
    ) {
        self.state = state
        self.capturedScreen = capturedScreen
        self.capturedTheme = capturedTheme
        self.onSelect = onSelect
        _transition = ObservedObject(wrappedValue:
            transition ?? SceneWallpaperPickerTransition(
                startsEntered: startsEntered))
    }

    private func themeIndex(_ theme: EnvironmentTheme) -> Int {
        let themes = EnvironmentTheme.allCases
        return themes.firstIndex(of: theme) ?? 0
    }

    private func slotOffset(
        for theme: EnvironmentTheme,
        relativeTo selection: EnvironmentTheme
    ) -> Int {
        themeIndex(theme) - themeIndex(selection)
    }

    private func adjacentTheme(
        relativeTo selection: EnvironmentTheme,
        offset: Int
    ) -> EnvironmentTheme? {
        let themes = EnvironmentTheme.allCases
        let candidateIndex = themeIndex(selection) + offset
        guard themes.indices.contains(candidateIndex) else { return nil }
        return themes[candidateIndex]
    }

    private func boundedDragOffset(
        _ horizontal: CGFloat,
        pitch: CGFloat
    ) -> CGFloat {
        let selection = state.environmentThemePreview
        if horizontal > 0,
           adjacentTheme(relativeTo: selection, offset: -1) == nil {
            return 0
        }
        if horizontal < 0,
           adjacentTheme(relativeTo: selection, offset: 1) == nil {
            return 0
        }
        return min(pitch, max(-pitch, horizontal))
    }

    @ViewBuilder
    private func wallpaperSurface(
        theme: EnvironmentTheme,
        size: CGSize
    ) -> some View {
        if theme == capturedTheme, let capturedScreen {
            Image(uiImage: capturedScreen)
                .resizable()
                .scaledToFill()
        } else {
            EnvironmentWallpaperImage(
                theme: theme,
                model: state.selectedModel,
                showsAppChrome: true)
        }
    }

    private func wallpaperCard(
        theme: EnvironmentTheme,
        size: CGSize,
        isCenterCard: Bool,
        physicalCenterYOffset: CGFloat
    ) -> some View {
        wallpaperSurface(theme: theme, size: size)
            .frame(width: size.width, height: size.height)
            .clipped()
            .clipShape(RoundedRectangle(
                cornerRadius: entered ? 30 : 0,
                style: .continuous))
            .overlay {
                RoundedRectangle(
                    cornerRadius: entered ? 30 : 0,
                    style: .continuous)
                    .stroke(Color.white.opacity(0.16), lineWidth: 1)
            }
            .shadow(color: .black.opacity(0.56), radius: 28, y: 18)
            .scaleEffect(
                entered ? previewScale : 1,
                anchor: .center)
            // The captured live page occupies the exact same physical plane
            // before and after the shrink. It remains the current theme's
            // card instead of fading into a generic wallpaper asset.
            .offset(y:
                !entered && isCenterCard && theme == capturedTheme &&
                    capturedScreen != nil
                    ? physicalCenterYOffset
                    : 0)
    }

    private func carouselDragGesture(pitch: CGFloat) -> some Gesture {
        DragGesture(minimumDistance: 8, coordinateSpace: .local)
            .onChanged { value in
                guard entered, !isSettling else { return }
                let horizontal = value.translation.width
                dragOffset = boundedDragOffset(horizontal, pitch: pitch)
            }
            .onEnded { value in
                settleCarousel(value, pitch: pitch)
            }
    }

    private func settleCarousel(
        _ value: DragGesture.Value,
        pitch: CGFloat
    ) {
        guard entered, !isSettling else { return }
        let horizontal = value.translation.width
        let projected = value.predictedEndTranslation.width
        let resolved = abs(projected) > abs(horizontal) ? projected : horizontal
        let isHorizontal = abs(horizontal) >= abs(value.translation.height)

        guard isHorizontal, abs(resolved) >= swipeThreshold else {
            withAnimation(.easeOut(duration: 0.18)) {
                dragOffset = 0
            }
            return
        }

        let themeOffset = resolved < 0 ? 1 : -1
        guard let nextTheme = adjacentTheme(
            relativeTo: state.environmentThemePreview,
            offset: themeOffset) else {
            withAnimation(.easeOut(duration: 0.18)) {
                dragOffset = 0
            }
            return
        }

        if reduceMotion {
            var transaction = Transaction()
            transaction.disablesAnimations = true
            withTransaction(transaction) {
                state.environmentThemePreview = nextTheme
                dragOffset = 0
            }
            return
        }

        isSettling = true
        withAnimation(.easeOut(duration: carouselSettleDuration)) {
            dragOffset = themeOffset > 0 ? -pitch : pitch
        }
        DispatchQueue.main.asyncAfter(
            deadline: .now() + carouselSettleDuration) {
            var transaction = Transaction()
            transaction.disablesAnimations = true
            withTransaction(transaction) {
                state.environmentThemePreview = nextTheme
                dragOffset = 0
                isSettling = false
            }
        }
    }

    var body: some View {
        GeometryReader { proxy in
            let size = proxy.size
            let windowInsets = activeWindowSafeAreaInsets
            let horizontalBackdropScale =
                (size.width + 90) / max(size.width, 1)
            // The outer SwiftUI safe-area proposal and PageTabViewController
            // each contribute half of the same vertical-center displacement.
            // Use the complete inset difference to cancel both layers.
            let physicalCenterYOffset =
                windowInsets.bottom - windowInsets.top
            let carouselPitch =
                size.width * previewScale + neighborSpacing
            ZStack {
                EnvironmentWallpaperImage(
                    theme: state.environmentThemePreview,
                    model: state.selectedModel,
                    showsAppChrome: false)
                    // Keep the backdrop's layout width equal to the screen.
                    // Its former `width + 90` frame enlarged the whole ZStack
                    // and shifted every centered element 45 pt to the right.
                    // transform-based bleed stays visually symmetric without
                    // participating in layout.
                    .frame(width: size.width, height: size.height + 90)
                    .clipped()
                    .scaleEffect(
                        x: horizontalBackdropScale,
                        y: 1,
                        anchor: .center)
                    .blur(radius: 34)
                    .saturation(0.72)
                    .opacity(0.42)
                    .animation(.easeInOut(duration: 0.36), value: state.environmentThemePreview)

                Color.black.opacity(0.68)
                    .ignoresSafeArea()

                ZStack {
                    ForEach(EnvironmentTheme.allCases) { theme in
                        let slot = slotOffset(
                            for: theme,
                            relativeTo: state.environmentThemePreview)
                        wallpaperCard(
                            theme: theme,
                            size: size,
                            isCenterCard: slot == 0,
                            physicalCenterYOffset: physicalCenterYOffset)
                            .offset(
                                x: CGFloat(slot) * carouselPitch +
                                    (entered ? dragOffset : 0))
                            .opacity(entered || slot == 0 ? 1 : 0)
                            .zIndex(slot == 0 ? 2 : 1)
                    }
                }
                .contentShape(Rectangle())
                .gesture(carouselDragGesture(pitch: carouselPitch))
                .animation(
                    reduceMotion
                        ? nil
                        : .timingCurve(
                            0.20,
                            0.80,
                            0.20,
                            1.00,
                            duration: SceneWallpaperPickerTransition.scaleDuration),
                    value: entered)
                .offset(y: entered ? physicalCenterYOffset : 0)

                VStack(spacing: 0) {
                    VStack(spacing: 3) {
                        Text(state.environmentThemePreview.title)
                            .font(.product(.headline, weight: .bold))
                            .foregroundStyle(.white)
                        Text(state.environmentThemePreview.subtitle)
                            .font(.product(.caption))
                            .foregroundStyle(Color.white.opacity(0.55))
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, max(12, proxy.safeAreaInsets.top + 8))
                    .opacity(entered ? 1 : 0)

                    Spacer()

                    ProductPageIndicator(
                        items: EnvironmentTheme.allCases,
                        selection: state.environmentThemePreview,
                        accessibilityLabel: { index, count in
                            "第 \(index) 个，共 \(count) 个场景"
                        })
                    .padding(.bottom, 14)

                    ProductPrimaryActionButton(
                        title: "选择当前场景",
                        state: !entered || isSettling
                            ? .disabled(reason: "场景仍在加载")
                            : .rest) {
                        guard entered, !isSettling else { return }
                        onSelect(state.environmentThemePreview)
                    }
                    .accessibilityHint("应用当前居中的场景")
                    .padding(.horizontal, 24)
                    .padding(.bottom, max(14, windowInsets.bottom + 10))
                }
                .opacity(entered ? 1 : 0)
                .animation(
                    reduceMotion ? nil : .easeOut(duration: 0.30).delay(0.16),
                    value: entered)
            }
            .ignoresSafeArea()
        }
        .background(Color.black)
        .preferredColorScheme(.dark)
        .productDesignSystem()
        .onChange(of: state.environmentThemePreview) { _ in
            UnityBridge.feedback()
        }
    }
}

private struct SpinnerLibrary: View {
    @ObservedObject var state: ProductUiState
    @State private var activeSwipeSession: Int64?
    @State private var swipeStartModel: SpinnerModel?
    @State private var showingBadgeCatalog = false
    @State private var presentedCatalogSnapshot: ProgressionCatalogSnapshot?

    private static let swipeCommitViewportFraction: CGFloat = 0.18

    private func select(_ model: SpinnerModel) {
        guard state.selectedModel != model else { return }
        UnityBridge.feedback()
        state.select(model)
        CodexSwiftUIOverlayManager.shared.previewModel(model)
    }

    private func beginSwipeIfNeeded() -> Int64 {
        if let activeSwipeSession {
            return activeSwipeSession
        }

        let session = Int64(CACurrentMediaTime() * 1_000_000)
        activeSwipeSession = session
        swipeStartModel = state.selectedModel
        UnityBridge.send(
            "BeginLibrarySwipeFromNativeUi",
            value: String(session))
        return session
    }

    private func targetModel(
        from start: SpinnerModel,
        translation: CGFloat,
        predictedTranslation: CGFloat,
        viewportWidth: CGFloat
    ) -> SpinnerModel? {
        let projected = abs(predictedTranslation) > abs(translation)
            ? predictedTranslation
            : translation
        guard abs(projected)
                >= viewportWidth * Self.swipeCommitViewportFraction,
              let startIndex = SpinnerModel.shippingCases.firstIndex(of: start)
        else { return nil }

        let targetIndex = startIndex + (projected < 0 ? 1 : -1)
        guard SpinnerModel.shippingCases.indices.contains(targetIndex) else {
            return nil
        }
        return SpinnerModel.shippingCases[targetIndex]
    }

    var body: some View {
        VStack(spacing: 0) {
            ProductToyIdentityLockup(state: state)
                .frame(maxWidth: .infinity)
                .padding(.top, 18)
                .padding(.horizontal, 24)

            TabView(selection: Binding(
                get: { state.selectedModel },
                set: select)) {
                ForEach(SpinnerModel.shippingCases) { model in
                    Spacer(minLength: 270)
                    .tag(model)
                    .padding(.bottom, 16)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .always))
            .indexViewStyle(.page(backgroundDisplayMode: .never))
            .contentShape(Rectangle())
            .highPriorityGesture(
                DragGesture(minimumDistance: 2, coordinateSpace: .global)
                    .onChanged { value in
                        let width = max(UIScreen.main.bounds.width, 1)
                        let session = beginSwipeIfNeeded()
                        let progress = max(
                            -1,
                            min(1, value.translation.width / width))
                        UnityBridge.send(
                            "SetLibrarySwipeProgressFromNativeUi",
                            value: String(
                                format: "%lld|%.4f",
                                session,
                                progress))
                    }
                    .onEnded { value in
                        guard let session = activeSwipeSession,
                              let start = swipeStartModel else { return }
                        let width = max(UIScreen.main.bounds.width, 1)
                        if let target = targetModel(
                            from: start,
                            translation: value.translation.width,
                            predictedTranslation:
                                value.predictedEndTranslation.width,
                            viewportWidth: width
                        ) {
                            UnityBridge.send(
                                "CommitLibrarySwipeFromNativeUi",
                                value: String(session))
                            withAnimation(.easeOut(duration: 0.22)) {
                                select(target)
                            }
                        }

                        UnityBridge.send(
                            "EndLibrarySwipeFromNativeUi",
                            value: String(session))
                        activeSwipeSession = nil
                        swipeStartModel = nil
                    })
            .simultaneousGesture(
                LongPressGesture(minimumDuration: 0.55, maximumDistance: 14)
                    .onEnded { _ in
                        CodexSwiftUIOverlayManager.shared.presentEnvironmentPicker()
                    })
            .overlay(alignment: .bottom) {
                LibraryToyBadgeRow(state: state) {
                    UnityBridge.feedback()
                    presentedCatalogSnapshot = ProgressionCatalogSnapshot(state: state)
                    showingBadgeCatalog = true
                }
                .padding(.bottom, 60)
            }
            .accessibilityIdentifier("library-model-carousel")
            .accessibilityHint("左右滑动选择陀螺；长按背景选择场景")

            Button {
                UnityBridge.feedback(.medium)
                CodexSwiftUIOverlayManager.shared.presentDisplayCase()
            } label: {
                Text("查看收藏盒")
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(.white.opacity(0.82))
                .frame(maxWidth: .infinity)
                .frame(height: 42)
                .background(.ultraThinMaterial, in:
                    RoundedRectangle(cornerRadius: 14, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .stroke(.white.opacity(0.09), lineWidth: 0.7)
                }
            }
            .buttonStyle(.plain)
            .padding(.horizontal, 24)
            .padding(.bottom, 8)

            ProductPrimaryActionButton(
                title: "进入 \(state.selectedModel.title)") {
                UnityBridge.feedback(.medium)
                CodexSwiftUIOverlayManager.shared.enterSelectedModel()
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 14)
        }
        .background {
            LinearGradient(
                colors: [Color.clear, Color.clear, Color.black.opacity(0.52)],
                startPoint: .top,
                endPoint: .bottom)
                .allowsHitTesting(false)
        }
        .onAppear {
            CodexSwiftUIOverlayManager.shared.beginLibraryPreview()
        }
        .sheet(
            isPresented: $showingBadgeCatalog,
            onDismiss: { presentedCatalogSnapshot = nil }
        ) {
            if let presentedCatalogSnapshot {
                ProgressionLevelDetailsSheet(
                    state: state,
                    snapshot: presentedCatalogSnapshot,
                    initialSection: 1)
                    .equatable()
            }
        }
    }
}

private struct PremiumDisplayCaseExperienceView: View {
    let gachaRequestId: String?
    let gachaReceipt: GachaReceiptRow?
    let onClose: () -> Void
    let onAccept: (() -> Void)?

    init(
        gachaRequestId: String? = nil,
        gachaReceipt: GachaReceiptRow? = nil,
        onClose: @escaping () -> Void,
        onAccept: (() -> Void)? = nil
    ) {
        self.gachaRequestId = gachaRequestId
        self.gachaReceipt = gachaReceipt
        self.onClose = onClose
        self.onAccept = onAccept
    }

    @ObservedObject private var gachaModel = GachaStoreModel.shared
    @State private var orbitYaw = 0.0
    @State private var orbitPitch = 0.0
    @State private var orbitStart = CGSize.zero
    @State private var zoom = 1.0
    @State private var zoomStart = 1.0
    @State private var acceptingGachaResult = false

    private var orbitGesture: some Gesture {
        DragGesture(minimumDistance: 0)
            .onChanged { value in
                orbitYaw = min(34, max(-34,
                    orbitStart.width - value.translation.width * 0.16))
                orbitPitch = min(22, max(-22,
                    orbitStart.height - value.translation.height * 0.16))
                UnityBridge.send(
                    "SetDisplayCaseOrbitFromNativeUi",
                    value: String(
                        format: "%.3f,%.3f",
                        locale: Locale(identifier: "en_US_POSIX"),
                        orbitYaw,
                        orbitPitch))
            }
            .onEnded { _ in
                orbitStart = CGSize(width: orbitYaw, height: orbitPitch)
            }
    }

    private var zoomGesture: some Gesture {
        MagnificationGesture()
            .onChanged { value in
                zoom = min(1.18, max(0.84, zoomStart * value))
                UnityBridge.send(
                    "SetDisplayCaseZoomFromNativeUi",
                    value: String(
                        format: "%.4f",
                        locale: Locale(identifier: "en_US_POSIX"),
                        zoom))
            }
            .onEnded { _ in
                zoomStart = zoom
            }
    }

    var body: some View {
        ZStack {
            Color.clear

            VStack(spacing: 0) {
                if gachaReceipt == nil {
                    HStack(spacing: 12) {
                        ProductIconButton(
                            symbol: "chevron.left",
                            accessibilityLabel: "关闭收藏盒") {
                                UnityBridge.feedback(.medium)
                                onClose()
                            }

                        VStack(alignment: .leading, spacing:
                            FidgetUITokens.Spacing.compact) {
                            Text("DISPLAY CASE")
                                .font(.product(.caption, weight: .semibold))
                                .foregroundStyle(.white.opacity(0.76))
                            Text("透明亚克力 · 收藏内容槽")
                                .font(.product(.caption2))
                                .foregroundStyle(.white.opacity(0.52))
                        }

                        Spacer()

                        ProductIconButton(
                            symbol: "view.3d",
                            accessibilityLabel: "重置视角") {
                                orbitYaw = 0
                                orbitPitch = 0
                                orbitStart = .zero
                                zoom = 1
                                zoomStart = 1
                                UnityBridge.feedback()
                                UnityBridge.send(
                                    "SetDisplayCaseOrbitFromNativeUi",
                                    value: "0,0")
                                UnityBridge.send(
                                    "SetDisplayCaseZoomFromNativeUi",
                                    value: "1")
                            }
                    }
                    .padding(.horizontal, FidgetUITokens.Spacing.section)
                    .padding(.top, FidgetUITokens.Spacing.metadata)
                }

                Rectangle()
                    .fill(Color.white.opacity(0.001))
                    .contentShape(Rectangle())
                    .gesture(orbitGesture)
                    .simultaneousGesture(zoomGesture)
                    .allowsHitTesting(gachaReceipt == nil)
                    .accessibilityLabel("收藏盒三维视图")
                    .accessibilityHint(gachaReceipt == nil
                        ? "单指拖动旋转，双指捏合缩放"
                        : "抽取结果展示")

            }

            if let receipt = gachaReceipt {
                VStack(spacing: 0) {
                    Spacer()
                    ProductBottomActionDock {
                        ProductScreenHeading(
                            title: receipt.name,
                            subtitle: "真实收藏品已进入展示盒",
                            centered: true)

                        HStack(spacing: FidgetUITokens.Spacing.standard) {
                            ProductStatusTag(
                                title: receipt.rarity.title,
                                accent: receipt.rarity.tint,
                                emphasized: true)
                            ProductStatusTag(
                                title: receipt.isNew
                                    ? "NEW"
                                    : "+\(receipt.shardsGained) 合金屑")
                        }

                        if gachaModel.revealIsComplete {
                            ProductPrimaryActionButton(
                                title: "收下",
                                state: acceptingGachaResult
                                    ? .loading("正在收下")
                                    : .rest) {
                                guard !acceptingGachaResult else { return }
                                acceptingGachaResult = true
                                UnityBridge.feedback(.medium)
                                onAccept?()
                            }
                            .accessibilityIdentifier("gacha-reveal-accept")
                        } else {
                            HStack(spacing: FidgetUITokens.Spacing.standard) {
                                ProgressView().tint(.white)
                                Text("正在完成高光")
                                    .font(.product(.subheadline, weight: .semibold))
                                    .foregroundStyle(.white.opacity(
                                        FidgetUITokens.Opacity.secondaryText))
                            }
                            .frame(height: FidgetUITokens.Size.primaryActionHeight)
                            .accessibilityIdentifier("gacha-reveal-in-progress")
                        }
                    }
                }
            }

            if let gachaRequestId, let gachaReceipt {
                VStack(spacing: 0) {
                    Text(gachaRequestId)
                        .accessibilityIdentifier("gacha-active-request-id")
                        .accessibilityValue(gachaRequestId)
                    Text(gachaReceipt.prizeId)
                        .accessibilityIdentifier("gacha-pending-prize-id")
                        .accessibilityValue(gachaReceipt.prizeId)
                }
                .font(.product(size: 1, weight: .regular))
                .foregroundStyle(.clear)
                .frame(width: 1, height: 1)
            }
        }
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .accessibilityIdentifier(gachaReceipt == nil
            ? "premium-display-case-experience"
            : "gacha-3d-reveal-root")
        .accessibilityValue(gachaReceipt.map {
            "modelId=metal-three-blade;prizeId=\($0.prizeId)"
        } ?? "modelId=current")
    }
}

#if DEBUG
struct PremiumDisplayCaseNativePreviewRoot: View {
    var body: some View {
        PremiumDisplayCaseExperienceView(onClose: {})
            .background {
                if let image = UIImage(named: "premium-display-case-unity-hero.png") {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFill()
                        .ignoresSafeArea()
                } else {
                    LinearGradient(
                        colors: [.black, Color(white: 0.07), .black],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing)
                        .ignoresSafeArea()
                }
            }
    }
}
#endif

private struct HapticSpeedTextureLab: View {
    @ObservedObject var state: ProductUiState

    private var telemetry: HapticLabTelemetrySnapshot { state.hapticTelemetry }
    private var accent: Color { state.currentAppearanceAccent }

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Label("触觉实验室 · 转速质感", systemImage: "waveform.path.badge.magnifyingglass")
                .font(.product(.headline))
                .foregroundStyle(.white)
            Divider().overlay(Color.white.opacity(0.12))

            Text("以真实转子角速度和同一份每圈段落数计算“触点/秒”。低速保留独立 Tick，高速切换为 Bearing Continuous；这里不是马达 Hz 或 G 值。")
                .font(.product(.footnote))
                .foregroundStyle(Color.white.opacity(0.56))

            LazyVGrid(
                columns: [GridItem(.flexible()), GridItem(.flexible())],
                spacing: 8) {
                ProductCompactMetric(
                    title: "转速",
                    value: String(format: "%.1f RPM", telemetry.rpm))
                ProductCompactMetric(
                    title: "角速度",
                    value: String(format: "%.2f rad/s", telemetry.angularSpeedRadians))
                ProductCompactMetric(
                    title: "机械事件率",
                    value: String(format: "%.1f 触点/s", telemetry.detentsPerSecond))
                ProductCompactMetric(title: "当前阶段", value: telemetry.bandTitle)
                ProductCompactMetric(
                    title: "有效 Continuous",
                    value: String(
                        format: "I %.2f · S %.2f",
                        telemetry.continuousIntensity,
                        telemetry.continuousSharpness))
                ProductCompactMetric(
                    title: "事件统计",
                    value: "\(telemetry.renderedEventCount) 播放 · \(telemetry.suppressedEventCount) 合并")
            }

            HStack(spacing: 7) {
                Image(systemName: telemetry.nativeStatus & 2 != 0
                      ? "iphone.radiowaves.left.and.right"
                      : "iphone.slash")
                Text(telemetry.engineTitle)
                Spacer()
                Text("最近：\(telemetry.lastSemanticTitle)")
            }
            .font(.product(.caption))
            .foregroundStyle(Color.white.opacity(0.58))

            ProductToggleRow(
                title: "启用高速轴承纹理",
                symbol: "circle.hexagongrid.fill",
                isOn: state.speedTextureEnabledBinding)

            HStack(spacing: 10) {
                Menu {
                    ForEach(HapticSpeedTexturePreset.allCases) { preset in
                        Button(preset.title) {
                            state.applySpeedTexturePreset(preset)
                        }
                    }
                } label: {
                    ProductActionLabel(title: "载入质感预设", symbol: "square.stack.3d.up.fill")
                }

                Picker("A/B", selection: Binding(
                    get: { state.selectedSpeedTextureSlot },
                    set: { state.selectSpeedTextureSlot($0) })) {
                    ForEach(HapticTuningSlot.allCases) { slot in
                        Text(slot.title).tag(slot)
                    }
                }
                .pickerStyle(.segmented)
                .frame(width: 96)
                .colorScheme(.dark)
            }

            ProductSecondaryActionButton(
                title: "保存当前参数到 \(state.selectedSpeedTextureSlot.title) 槽",
                symbol: "tray.and.arrow.down.fill") {
                state.saveCurrentSpeedTextureSlot()
                UnityBridge.feedback(.medium)
            }

            Group {
                Text("阶段切换")
                    .font(.product(.subheadline, weight: .semibold))
                ProductSliderRow(
                    title: "进入 Continuous", symbol: "arrow.up.right.circle",
                    range: 12...48, step: 1,
                    valueText: { String(format: "%.0f 触点/s", $0) },
                    value: state.speedTextureBinding(\.enterDetentsPerSecond),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "退出 Continuous", symbol: "arrow.down.left.circle",
                    range: 8...42, step: 1,
                    valueText: { String(format: "%.0f 触点/s", $0) },
                    value: state.speedTextureBinding(\.exitDetentsPerSecond),
                    apply: state.applySpeedTextureAndPersist)
                Text("进入值必须高于退出值；回差可以避免临界转速附近反复启停。24 段时，30 触点/s 约等于 75 RPM。")
                    .font(.product(.footnote))
                    .foregroundStyle(Color.white.opacity(0.48))
            }

            Group {
                Text("低速 Tick")
                    .font(.product(.subheadline, weight: .semibold))
                ProductSliderRow(
                    title: "慢速 Tick 力度", symbol: "tortoise.fill",
                    range: 0...1, step: 0.01,
                    valueText: { String(format: "%.2f×", $0) },
                    value: state.speedTextureBinding(\.slowDetentGain),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "融合前 Tick 力度", symbol: "hare.fill",
                    range: 0...1, step: 0.01,
                    valueText: { String(format: "%.2f×", $0) },
                    value: state.speedTextureBinding(\.fastDetentGain),
                    apply: state.applySpeedTextureAndPersist)
            }

            Group {
                Text("高速 Bearing Continuous")
                    .font(.product(.subheadline, weight: .semibold))
                ProductSliderRow(
                    title: "最小 Intensity", symbol: "waveform",
                    range: 0...0.30, step: 0.01,
                    valueText: { String(format: "%.2f", $0) },
                    value: state.speedTextureBinding(\.minimumContinuousIntensity),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "最大 Intensity", symbol: "waveform.badge.plus",
                    range: 0.02...0.40, step: 0.01,
                    valueText: { String(format: "%.2f", $0) },
                    value: state.speedTextureBinding(\.maximumContinuousIntensity),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "最小 Sharpness", symbol: "dial.low.fill",
                    range: 0...1, step: 0.01,
                    valueText: { String(format: "%.2f", $0) },
                    value: state.speedTextureBinding(\.minimumContinuousSharpness),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "最大 Sharpness", symbol: "dial.high.fill",
                    range: 0...1, step: 0.01,
                    valueText: { String(format: "%.2f", $0) },
                    value: state.speedTextureBinding(\.maximumContinuousSharpness),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "满量程角速度", symbol: "gauge.with.dots.needle.100percent",
                    range: 6...48, step: 1,
                    valueText: { String(format: "%.0f rad/s", $0) },
                    value: state.speedTextureBinding(\.fullScaleAngularSpeed),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "速度曲线", symbol: "point.topleft.down.curvedto.point.bottomright.up",
                    range: 0.2...2, step: 0.05,
                    valueText: { String(format: "γ %.2f", $0) },
                    value: state.speedTextureBinding(\.responseExponent),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "动态更新率", symbol: "metronome.fill",
                    range: 10...60, step: 5,
                    valueText: { String(format: "%.0f Hz", $0) },
                    value: state.speedTextureBinding(\.updateRate),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "Attack（归一化）", symbol: "arrow.up.forward",
                    range: 0...1, step: 0.01,
                    valueText: { String(format: "%.2f", $0) },
                    value: state.speedTextureBinding(\.attack),
                    apply: state.applySpeedTextureAndPersist)
                ProductSliderRow(
                    title: "退出淡出", symbol: "arrow.down.right",
                    range: 0...0.5, step: 0.01,
                    valueText: { String(format: "%.0f ms", $0 * 1000) },
                    value: state.speedTextureBinding(\.releaseSeconds),
                    apply: state.applySpeedTextureAndPersist)
            }

            Text("这里的动态更新率是 App 向播放器发送参数的频率；它不是 Taptic Engine 的振动频率。Attack 是 Apple 的归一化包络参数，淡出才以真实毫秒显示。")
                .font(.product(.footnote))
                .foregroundStyle(Color.white.opacity(0.48))

            HStack(spacing: 8) {
                ForEach([(0.35, "低速"), (0.68, "中速"), (1.0, "高速")], id: \.0) { item in
                    Button {
                        state.previewSpeedTexture(item.0)
                    } label: {
                        Text(item.1)
                            .font(.product(.caption, weight: .semibold))
                            .foregroundStyle(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 42)
                            .productGlass(
                                cornerRadius: 14,
                                tint: accent.opacity(0.10),
                                interactive: true)
                    }
                    .buttonStyle(.plain)
                }
            }
            .accessibilityLabel("试听低速、中速或高速轴承纹理")
        }
        .foregroundStyle(.white)
        .padding(16)
        .productGlass(cornerRadius: 22)
    }
}

private struct ComboHaloTuningPanel: View {
    @ObservedObject var state: ProductUiState
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var previewProgress: CGFloat = 1
    @State private var previewOpacityProgress: CGFloat = 1

    var body: some View {
        ProductSectionCard("COMBO 分层光晕", symbol: "circle.circle") {
            VStack(alignment: .leading, spacing: 12) {
                ZStack {
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .fill(Color.black.opacity(0.56))

                    ComboCenterHalo(
                        progress: previewProgress,
                        opacityProgress: previewOpacityProgress,
                        tuning: state.comboHaloTuning,
                        reduceMotion: reduceMotion,
                        projection: .threeBladeHeroPreview,
                        milestoneCount: 30)

                    Circle()
                        .fill(Color.black.opacity(0.82))
                        .frame(width: 70, height: 70)
                        .overlay {
                            VStack(spacing: -2) {
                                Text("×30")
                                    .font(.product(size: 24, weight: .black))
                                    .monospacedDigit()
                                Text("MODEL CENTER")
                                    .font(.product(size: 7, weight: .bold))
                                    .foregroundStyle(Color.white.opacity(0.52))
                            }
                        }
                }
                .frame(height: 164)
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Combo 二十次时的主环、回声环与能量雾预演")

                HStack(spacing: 10) {
                    Stepper(
                        value: state.comboHaloIntegerBinding(\.firstMilestone),
                        in: 5...50,
                        step: 5) {
                        VStack(alignment: .leading, spacing: 1) {
                            Text("首次")
                                .font(.product(.caption2))
                                .foregroundStyle(Color.white.opacity(0.52))
                            Text("×\(state.comboHaloTuning.firstMilestone)")
                                .font(.product(.subheadline, weight: .bold))
                                .monospacedDigit()
                        }
                    }

                    Stepper(
                        value: state.comboHaloIntegerBinding(\.repeatInterval),
                        in: 5...50,
                        step: 5) {
                        VStack(alignment: .leading, spacing: 1) {
                            Text("之后每")
                                .font(.product(.caption2))
                                .foregroundStyle(Color.white.opacity(0.52))
                            Text("+\(state.comboHaloTuning.repeatInterval)")
                                .font(.product(.subheadline, weight: .bold))
                                .monospacedDigit()
                        }
                    }
                }
                .padding(10)
                .background(
                    Color.white.opacity(0.045),
                    in: RoundedRectangle(cornerRadius: 14, style: .continuous))

                VStack(alignment: .leading, spacing: 7) {
                    HStack {
                        Text("动画曲线")
                            .font(.product(.subheadline, weight: .semibold))
                        Spacer()
                        Text(String(
                            format: "%.2f,%.2f  %.2f,%.2f",
                            state.comboHaloTuning.curveX1,
                            state.comboHaloTuning.curveY1,
                            state.comboHaloTuning.curveX2,
                            state.comboHaloTuning.curveY2))
                            .font(.product(.caption2).monospacedDigit())
                            .foregroundStyle(Color.white.opacity(0.48))
                    }

                    ComboBezierCurveEditor(
                        x1: state.comboHaloDoubleBinding(\.curveX1),
                        y1: state.comboHaloDoubleBinding(\.curveY1),
                        x2: state.comboHaloDoubleBinding(\.curveX2),
                        y2: state.comboHaloDoubleBinding(\.curveY2))
                        .frame(height: 138)

                    Text("拖动两个白点控制主环起势与收势；回声环和能量雾会按错拍自动跟随。横向是时间，纵向是扩散进度。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.50))
                }

                ProductSliderRow(
                    title: "持续时间",
                    symbol: "timer",
                    range: 0.24...1.20,
                    step: 0.01,
                    valueText: { String(format: "%.0f ms", $0 * 1000) },
                    value: state.comboHaloDoubleBinding(\.durationSeconds),
                    apply: {})

                ProductSliderRow(
                    title: "扩散范围",
                    symbol: "arrow.up.left.and.arrow.down.right",
                    range: 0.72...1.20,
                    step: 0.01,
                    valueText: { String(format: "%.0f%%", $0 * 100) },
                    value: state.comboHaloDoubleBinding(\.endRadiusScale),
                    apply: {})

                ProductSliderRow(
                    title: "峰值亮度",
                    symbol: "sun.max.fill",
                    range: 0.08...0.60,
                    step: 0.01,
                    valueText: { String(format: "%.0f%%", $0 * 100) },
                    value: state.comboHaloDoubleBinding(\.peakOpacity),
                    apply: {})

                HStack(spacing: 8) {
                    ProductSecondaryActionButton(
                        title: "播放预演",
                        symbol: "play.fill") {
                        playPreview()
                    }

                    ProductSecondaryActionButton(
                        title: "恢复推荐",
                        symbol: "arrow.uturn.backward") {
                        state.restoreRecommendedComboHaloTuning()
                        playPreview()
                    }
                }
            }
        }
        .onAppear {
            playPreview()
        }
    }

    private func playPreview() {
        var transaction = Transaction()
        transaction.disablesAnimations = true
        withTransaction(transaction) {
            previewProgress = 0
            previewOpacityProgress = 0
        }
        DispatchQueue.main.async {
            let duration = reduceMotion
                ? min(0.18, state.comboHaloTuning.durationSeconds)
                : state.comboHaloTuning.durationSeconds
            withAnimation(
                reduceMotion
                    ? .linear(duration: duration)
                    : state.comboHaloTuning.animation) {
                previewProgress = 1
            }
            withAnimation(.linear(duration: duration)) {
                previewOpacityProgress = 1
            }
        }
    }
}

private struct SettingsPanel: View {
    @ObservedObject var state: ProductUiState
    @State private var isHapticLabVisible = false
#if DEBUG
    @State private var isComboHaloLabVisible = false
#endif

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text("日常设置只保留产品级手感；需要逐阶段、逐事件调试时，可进入触觉实验室。")
                    .font(.product(.subheadline))
                    .foregroundStyle(Color.white.opacity(0.62))

#if DEBUG
                ProductSecondaryActionButton(
                    title: isComboHaloLabVisible
                        ? "收起 Combo 光晕工具"
                        : "打开 Combo 光晕工具",
                    symbol: isComboHaloLabVisible
                        ? "chevron.up"
                        : "circle.circle") {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        isComboHaloLabVisible.toggle()
                    }
                }

                if isComboHaloLabVisible {
                    ComboHaloTuningPanel(state: state)
                        .transition(.opacity.combined(with: .move(edge: .top)))
                }
#endif

                ProductSectionCard("触觉", symbol: "waveform") {
                    ProductToggleRow(
                        title: "启用触感",
                        symbol: "iphone.radiowaves.left.and.right",
                        isOn: $state.hapticsEnabled,
                        onChange: { _ in state.applyAndPersist() })

                    ProductSliderRow(
                        title: "其他事件力度", symbol: "hand.tap.fill", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.0f%%", $0 * 100) },
                        value: $state.hapticIntensity,
                        apply: state.applyHapticsAndPreview)
                    ProductSliderRow(
                        title: "其他事件锐度", symbol: "waveform.path.ecg", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.0f%%", $0 * 100) },
                        value: $state.hapticSharpness,
                        apply: state.applyHapticsAndPreview)

                    Text("这里调节 UI、脱档、吸附等其他事件；棘轮跨档只由设置页中的 DETENT LAB 控制，避免参数重叠。Sharpness 不是可直接指定的马达 Hz。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.5))

                    ProductSecondaryActionButton(
                        title: "试听当前组合",
                        symbol: "play.fill") {
                        state.applyAndPersist()
                        UnityBridge.send("PreviewHapticFromNativeUi")
                    }
                }

                DetentTuningPanel(state: state)

                ProductSecondaryActionButton(
                    title: isHapticLabVisible ? "收起触觉实验室" : "打开触觉实验室",
                    symbol: isHapticLabVisible ? "chevron.up" : "wrench.and.screwdriver.fill") {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        isHapticLabVisible.toggle()
                    }
                }

                if isHapticLabVisible {
                    ProductSectionCard("触觉映射 · 高级", symbol: "slider.horizontal.3") {
                        VStack(alignment: .leading, spacing: 8) {
                            Label("脉冲节奏", systemImage: "metronome.fill")
                                .font(.product(.subheadline, weight: .medium))
                                .foregroundStyle(.white)
                            Picker("脉冲节奏", selection: $state.hapticRhythm) {
                                ForEach(ProductHapticRhythm.allCases) { rhythm in
                                    Text(rhythm.title).tag(rhythm)
                                }
                            }
                            .pickerStyle(.segmented)
                            .colorScheme(.dark)
                            .onChange(of: state.hapticRhythm) { _ in
                                state.applyHapticsAndPreview()
                            }
                            Text(state.rhythmDescription)
                                .font(.product(.footnote))
                                .foregroundStyle(Color.white.opacity(0.5))
                        }

                        ProductSliderRow(
                            title: "速度调制", symbol: "gauge.with.dots.needle.50percent",
                            range: 0...1, step: 0.01,
                            valueText: { String(format: "%.0f%%", $0 * 100) },
                            value: $state.hapticSpeedInfluence,
                            apply: state.applyHapticsAndPreview)

                        Text("只调制 Haptic 力度，不改变陀螺转速、阻力或甩动阈值。")
                            .font(.product(.footnote))
                            .foregroundStyle(Color.white.opacity(0.5))
                    }

                    ProductSectionCard("Core Haptics · 事件配方", symbol: "waveform.path.ecg.rectangle") {
                    VStack(alignment: .leading, spacing: 8) {
                        Label("机械语义", systemImage: "point.3.connected.trianglepath.dotted")
                            .font(.product(.subheadline, weight: .medium))
                        Picker("机械语义", selection: Binding(
                            get: { state.selectedAdvancedHapticSemantic },
                            set: { state.selectAdvancedSemantic($0) })) {
                            ForEach(EditableHapticSemantic.generalTuningCases) { semantic in
                                Text(semantic.title).tag(semantic)
                            }
                        }
                        .pickerStyle(.menu)
                        .tint(state.currentAppearanceAccent)
                        Text(state.selectedAdvancedHapticSemantic.explanation)
                            .font(.product(.footnote))
                            .foregroundStyle(Color.white.opacity(0.52))
                        Text("跨档 Detent 的 Transient、Intensity 与 Sharpness 已由 DETENT LAB 独占，因此不在这里重复出现。")
                            .font(.product(.footnote))
                            .foregroundStyle(state.currentAppearanceAccent.opacity(0.62))
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Label("事件波形", systemImage: "waveform.badge.plus")
                            .font(.product(.subheadline, weight: .medium))
                        Picker("事件波形", selection: state.advancedWaveformBinding) {
                            ForEach(HapticWaveform.allCases) { waveform in
                                Text(waveform.title).tag(waveform)
                            }
                        }
                        .pickerStyle(.segmented)
                        .colorScheme(.dark)
                    }

                    Text("瞬态是一个短触点；连续会使用 Duration 与 ADSR 包络；混合会叠加瞬态与连续事件。‘混合’是本 App 的配方概念，不是 Apple 事件类型。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.5))

                    ProductSliderRow(
                        title: "事件力度 Intensity", symbol: "hand.tap.fill", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.2f", $0) },
                        value: state.advancedBinding(\.intensity),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "事件锐度 Sharpness", symbol: "dial.high.fill", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.2f", $0) },
                        value: state.advancedBinding(\.sharpness),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "持续时间 Duration", symbol: "timer", range: 0.01...1, step: 0.005,
                        valueText: { String(format: "%.0f ms", $0 * 1000) },
                        value: state.advancedBinding(\.duration),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "起振 Attack", symbol: "arrow.up.forward", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.2f", $0) },
                        value: state.advancedBinding(\.attack),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "衰落 Decay", symbol: "arrow.down.right", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.2f", $0) },
                        value: state.advancedBinding(\.decay),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "释振 Release", symbol: "arrow.right.to.line", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.2f", $0) },
                        value: state.advancedBinding(\.release),
                        apply: state.persistSelectedAdvancedRecipe)

                    ProductToggleRow(
                        title: "保持 Sustained",
                        symbol: "waveform.path",
                        isOn: state.advancedSustainedBinding)

                    Text("Apple 的 Decay 只有在 Sustained 关闭时才形成衰落段；这些包络参数主要影响连续与混合波形，纯瞬态本身很短。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.5))
                }

                    ProductSectionCard("动态控制与组合层", symbol: "slider.horizontal.3") {
                    Text("尾部、脉冲和叠层由 App 组合多个事件；Dynamic Controls 是 Core Haptics 在整个 Pattern 上施加的即时调制。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.52))

                    ProductSliderRow(
                        title: "尾部力度", symbol: "waveform.path.badge.minus", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.2f", $0) },
                        value: state.advancedBinding(\.endIntensity),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "尾部锐度", symbol: "dial.low.fill", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.2f", $0) },
                        value: state.advancedBinding(\.endSharpness),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "脉冲数量", symbol: "ellipsis", range: 1...6, step: 1,
                        valueText: { String(format: "%.0f 次", $0) },
                        value: state.advancedBinding(\.pulseCount),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "脉冲间隔", symbol: "metronome", range: 0.01...0.12, step: 0.002,
                        valueText: { String(format: "%.0f ms", $0 * 1000) },
                        value: state.advancedBinding(\.pulseInterval),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "冲击叠层", symbol: "square.3.layers.3d", range: 1...3, step: 0.05,
                        valueText: { String(format: "%.2f×", $0) },
                        value: state.advancedBinding(\.impactLayers),
                        apply: state.persistSelectedAdvancedRecipe)

                    ProductSliderRow(
                        title: "动态力度", symbol: "waveform.and.magnifyingglass", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.2f", $0) },
                        value: state.advancedBinding(\.dynamicIntensity),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "动态锐度", symbol: "dial.medium.fill", range: -1...1, step: 0.01,
                        valueText: { String(format: "%+.2f", $0) },
                        value: state.advancedBinding(\.dynamicSharpness),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "动态 Attack", symbol: "arrow.up.right", range: -1...1, step: 0.01,
                        valueText: { String(format: "%+.2f", $0) },
                        value: state.advancedBinding(\.dynamicAttack),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "动态 Decay", symbol: "arrow.down.right", range: -1...1, step: 0.01,
                        valueText: { String(format: "%+.2f", $0) },
                        value: state.advancedBinding(\.dynamicDecay),
                        apply: state.persistSelectedAdvancedRecipe)
                    ProductSliderRow(
                        title: "动态 Release", symbol: "arrow.right", range: -1...1, step: 0.01,
                        valueText: { String(format: "%+.2f", $0) },
                        value: state.advancedBinding(\.dynamicRelease),
                        apply: state.persistSelectedAdvancedRecipe)

                    Text("Dynamic Intensity 的 1.00 是不衰减；其余动态控制以 0 为中性、-1 到 +1 调制。速度跟随仍由语义映射层负责。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.5))

                    HStack(spacing: 10) {
                        ProductSecondaryActionButton(
                            title: "试听当前事件",
                            symbol: "play.fill") {
                            state.previewSelectedAdvancedRecipe()
                        }

                        ProductSecondaryActionButton(
                            title: "恢复此事件",
                            symbol: "arrow.uturn.backward") {
                            state.resetSelectedAdvancedRecipe()
                            UnityBridge.feedback()
                        }
                    }
                    }
                }

                ProductSectionCard("旋转手感", symbol: "gearshape.2.fill") {
                    ProductSliderRow(
                        title: "拖动响应", symbol: "hand.draw.fill", range: 0...1, step: 0.01,
                        valueText: { String(format: "%.0f%%", $0 * 100) },
                        value: $state.spinResponseLevel,
                        apply: { state.applyAndPersist() })

                    Text("只影响手指拖住时的速度与跟随响应；松手后的滑行由惯性阻力单独控制。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.5))

                    ProductSliderRow(
                        title: "惯性阻力", symbol: "gauge.with.dots.needle.50percent",
                        range: 0...1, step: 0.01,
                        valueText: { String(format: "%.0f%%", $0 * 100) },
                        value: $state.spinResistanceLevel,
                        apply: { state.applyAndPersist() })

                    Text("只影响松手后的减速：0% 长滑行，100% 明显制动；不会放大小范围拖动。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.5))

                    if state.interactionMode == .ratchet {
                        VStack(alignment: .leading, spacing: 8) {
                            Label("棘轮咬合", systemImage: "gearshape.arrow.triangle.2.circlepath")
                                .font(.product(.subheadline, weight: .medium))
                                .foregroundStyle(.white)
                            Picker("棘轮咬合", selection: $state.ratchetFeel) {
                                ForEach(ProductRatchetFeel.tuningCases) { feel in
                                    Text(feel.title).tag(feel)
                                }
                            }
                            .pickerStyle(.segmented)
                            .colorScheme(.dark)
                            .onChange(of: state.ratchetFeel) { _ in
                                state.applyRatchetFeelSelection()
                            }
                            Text(state.ratchetDescription)
                                .font(.product(.footnote))
                                .foregroundStyle(Color.white.opacity(0.5))
                        }
                    }
                }

                ProductSectionCard("设备动作", symbol: "gyroscope") {
                    VStack(alignment: .leading, spacing: 8) {
                        Label("陀螺仪灵敏度", systemImage: "move.3d")
                            .font(.product(.subheadline, weight: .medium))
                            .foregroundStyle(.white)
                        Picker("陀螺仪灵敏度", selection: $state.motionSensitivityPreset) {
                            ForEach(MotionSensitivityPreset.allCases) { preset in
                                Text(preset.title).tag(preset)
                            }
                        }
                        .pickerStyle(.segmented)
                        .colorScheme(.dark)
                        .onChange(of: state.motionSensitivityPreset) { _ in
                            state.applyMotionSensitivityPresetSelection()
                        }
                        Text(state.motionSensitivityPreset.parameterSummary)
                            .font(.product(.caption).monospaced())
                            .foregroundStyle(state.currentAppearanceAccent.opacity(0.78))
                        Text("档位越高，模型偏转越大、跟随越快。Input Angle 是反向参数，因此高档数值更小。切档会以当前持机姿态重新归零。")
                            .font(.product(.footnote))
                            .foregroundStyle(Color.white.opacity(0.54))
                    }

                    Text("倾斜继续控制视差；userAcceleration 达到 0.3g 会触发低锐度的惯性重量触点，最多每秒 8 次。原有明确甩动驱动陀螺的物理规则保持不变。")
                        .font(.product(.footnote))
                        .foregroundStyle(Color.white.opacity(0.54))

                    ProductSecondaryActionButton(
                        title: "重新校准设备姿态",
                        symbol: "scope") {
                        UnityBridge.feedback()
                        UnityBridge.send("RecenterMotionFromNativeUi")
                    }
                }

                ProductSecondaryActionButton(
                    title: "恢复推荐参数",
                    symbol: "arrow.uturn.backward") {
                    state.restoreRecommendedValues()
                    UnityBridge.feedback(.medium)
                }

                Text("触感需要在支持 Taptic Engine 的真机上判断；模拟器无法还原力度与锐度。")
                    .font(.product(.footnote))
                    .foregroundStyle(Color.white.opacity(0.48))
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding(.top, 2)
            }
            .padding(18)
        }
        .background(ProductBackdrop().ignoresSafeArea())
    }

}

#if DEBUG
/// Simulator-only entry point used by the visual push gate. It renders the
/// shipping native views over a Unity-captured shipping-scene frame.
struct ComboHaloNativePreviewRoot: View {
    enum Mode: String {
        case effect
        case motion
        case tool
    }

    enum SceneView: String {
        case hero
        case top
        case left
        case right
        case low

        var imageResource: String {
            switch self {
            case .hero: return "UnityHero"
            case .top: return "UnityTop"
            case .left: return "UnityLeft"
            case .right: return "UnityRight"
            case .low: return "UnityLow"
            }
        }

        var projection: ComboHaloProjectionState {
            let axisRatio: Double
            switch self {
            case .hero: axisRatio = 0.67
            case .top: axisRatio = 1.00
            case .left, .right: axisRatio = 0.57
            case .low: axisRatio = 0.26
            }
            return ComboHaloProjectionState(
                available: true,
                centerX: 0.5,
                centerY: 0.5,
                rotationDegrees: 0,
                minorAxisRatio: axisRatio)
        }
    }

    @StateObject private var state = ProductUiState()
    @State private var motionProgress: CGFloat = 1
    @State private var motionOpacityProgress: CGFloat = 1
    let mode: Mode
    let frozenProgress: CGFloat
    let sceneView: SceneView
    let comboCount: Int

    private var previewCombo: ProgressionComboState {
        ProgressionComboState(
            tier: 3,
            count: comboCount,
            title: "OVERDRIVE",
            speed: 0.92,
            angularSpeedRadians: 42,
            intensity: 0.88,
            frequency: 0.84,
            experienceMultiplier: 1.45)
    }

    var body: some View {
        Group {
            if mode == .tool {
                ScrollView {
                    ComboHaloTuningPanel(state: state)
                        .padding(16)
                }
                .background(ProductBackdrop().ignoresSafeArea())
            } else {
                GeometryReader { proxy in
                    ZStack {
                        if let imagePath = Bundle.main.path(
                            forResource: sceneView.imageResource,
                            ofType: "png"),
                           let image = UIImage(contentsOfFile: imagePath) {
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFill()
                                .frame(
                                    width: proxy.size.width,
                                    height: proxy.size.height)
                                .clipped()
                        } else {
                            Color.black
                        }

                        ComboCenterHalo(
                            progress: mode == .motion
                                ? motionProgress
                                : frozenProgress,
                            opacityProgress: mode == .motion
                                ? motionOpacityProgress
                                : frozenProgress,
                            tuning: state.comboHaloTuning,
                            reduceMotion: false,
                            projection: sceneView.projection,
                            milestoneCount: comboCount)

                        VStack(spacing: 0) {
                            RewardingComboLockup(combo: previewCombo)
                                .padding(.top, 176)
                            Spacer(minLength: 0)

                            Text(mode == .motion
                                 ? "NATIVE IMPLEMENTATION · ×\(comboCount) LIVE LOOP"
                                 : "NATIVE IMPLEMENTATION · ×\(comboCount) · 38% FRAME")
                                .font(.product(size: 9, weight: .bold))
                                .foregroundStyle(Color.white.opacity(0.54))
                                .padding(.bottom, 34)
                        }
                        .frame(maxWidth: .infinity)
                    }
                }
                .ignoresSafeArea()
            }
        }
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .onAppear {
            if mode == .motion {
                playMotionLoop()
            }
        }
    }

    private func playMotionLoop() {
        var transaction = Transaction()
        transaction.disablesAnimations = true
        withTransaction(transaction) {
            motionProgress = 0
            motionOpacityProgress = 0
        }

        // Keep the first burst inside screen recording even when Simulator
        // launch and video encoder startup complete on different frames.
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.92) {
            withAnimation(state.comboHaloTuning.animation) {
                motionProgress = 1
            }
            withAnimation(.linear(
                duration: state.comboHaloTuning.durationSeconds)) {
                motionOpacityProgress = 1
            }
        }
        DispatchQueue.main.asyncAfter(
            deadline: .now() + state.comboHaloTuning.durationSeconds + 1.34) {
            guard mode == .motion else { return }
            playMotionLoop()
        }
    }
}

/// Simulator-only visual gate for the progression thumbnail surfaces. It uses
/// the shipping HUD, Bottom Sheet, artwork loader, and bundled thumbnail names.
struct ProgressionThumbnailNativePreviewRoot: View {
    enum Mode: String {
        case hud
        case hudOff = "hud-off"
        case sheet
        case sheetBadge = "sheet-badge"
        case sheetAppearance = "sheet-appearance"
        case top
    }

    @StateObject private var state = ProductUiState()
    @State private var showingCatalogSheet = false
    @State private var previewCatalogSnapshot: ProgressionCatalogSnapshot?
    let mode: Mode

    private var previewCatalogSection: Int {
        switch mode {
        case .sheetBadge: return 1
        case .sheetAppearance: return 2
        default: return 0
        }
    }

    private static let skinCatalogPayload = """
    factory-silver\t1\t原生雾银\t雾面航空铝\t微珠喷砂\t原厂抛光倒角\t标准单列轴承\tAEB3B6\tE5E9EC
    gunmetal-brush\t5\t枪灰拉丝\t枪灰不锈钢\t纵向细拉丝\t黑铬边线\t磨合配平\t4A5158\tAEB7BF
    night-cyan-index\t10\t夜航刻度\t深海蓝钢\t十二段夜光刻度\t齐平青蓝蚀刻\t表面平衡刻线\t142A36\t4FF5E7
    tungsten-honeycomb\t20\t钨金蜂巢\t钨黑 PVD × 香槟金\t微蚀刻蜂巢\t香槟金凹槽\t精钢配重环\t17191B\tD7A84B
    ice-guilloche\t35\t冰银回纹\t冷银镍铬\t机刻交错回纹\t冰蓝抛光边\t静音缓冲垫圈\tA9B6BE\t8DE9FF
    blue-damascus\t50\t蓝钢水波\t回火蓝钢\t大马士革水波纹\t银蓝刃线\t双列辅助轴承\t203E5A\tA9D8EE
    copper-circuit\t65\t赤铜回路\t烟熏铜合金\t精密电路蚀刻\t齐平赤铜节点\t蓝钢冠环表面\t5E3027\tF0A65B
    titanium-heat\t75\t钛虹热变\t阳极氧化钛\t热变虹彩渐层\t紫金倒角\t低阻保持架\t445A73\tD966FF
    meteor-obsidian\t90\t星陨黑曜\t黑曜 DLC\t陨石颗粒与银屑\t齐平典藏铭纹\t黑曜凹槽处理\t101215\tC7D0D8
    mirror-aurora\t100\t镜铬极光\t镜面精钢\t极光镜切纹\t陶瓷白冠环\t陶瓷主轴承 + 镜钢完成体\tDDE4EA\t9BF4FF
    """

    var body: some View {
        Group {
            switch mode {
            case .hud, .hudOff:
                ZStack {
                    ProductBackdrop().ignoresSafeArea()
                    VStack(spacing: 0) {
                        Spacer(minLength: 0)
                        SpinnerProgressionHUD(state: state)
                            .padding(.horizontal, 14)
                            .padding(.bottom, 28)
                    }
                }
            case .sheet, .sheetBadge, .sheetAppearance:
                ProgressionCatalogPreviewScene()
                    .sheet(isPresented: $showingCatalogSheet) {
                        if let previewCatalogSnapshot {
                            ProgressionLevelDetailsSheet(
                                state: state,
                                snapshot: previewCatalogSnapshot,
                                initialSection: previewCatalogSection)
                                .equatable()
                        }
                    }
            case .top:
                ZStack {
                    ProductBackdrop().ignoresSafeArea()
                    VStack(spacing: 0) {
                        ProductTopBar(state: state)
                            .frame(maxWidth: .infinity)
                            .frame(height: 82)
                        Spacer(minLength: 0)
                    }
                }
            }
        }
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .onAppear {
            configurePreviewState()
            if mode == .sheet
                || mode == .sheetBadge
                || mode == .sheetAppearance {
                previewCatalogSnapshot = ProgressionCatalogSnapshot(state: state)
                DispatchQueue.main.async {
                    showingCatalogSheet = true
                }
            }
        }
    }

    private func configurePreviewState() {
        state.isLibraryVisible = false
        state.selectedModel = .metalThreeBlade
        state.progressionModel = .metalThreeBlade
        state.progressionLevel = 39
        state.progressionLevelTitle = "静音调校师"
        state.progressionFraction = 0.62
        state.progressionTotalExperience = 682
        state.progressionLevelStartExperience = 535
        state.progressionNextLevelExperience = 821
        state.motionTelemetry = ProductMotionTelemetryState(
            available: true,
            normalizedSpeed: 0.54,
            angularSpeedRadians: 12,
            motionRate: 12,
            speedBand: .engaged,
            intensity: 0.68,
            frequency: 0.42)
        state.progressionNextUnlockLevel = 50
        state.progressionNextUnlockName = "双列辅助轴承"
        state.progressionAssistantEnabled = mode == .hud
        state.progressionAssistantMultiplier = 1.0
        state.progressionLevelCatalog = ProgressionLevelDetail.fallback
        state.threeBladeMetalSkins = ThreeBladeMetalSkinDetail.parse(
            Self.skinCatalogPayload)
        state.toyBadgeCatalog = BadgeNativePreviewRoot.catalogBadges
    }
}

/// Simulator-only visual gate for the shipping Library selection page. It
/// keeps the real carousel, CTAs, global Collector profile, per-toy identity,
/// and the direct three-Badge horizontal row in one full-screen context.
struct ProductIdentityNativePreviewRoot: View {
    enum Mode: String {
        case gold
        case metal

        fileprivate var model: SpinnerModel {
            self == .gold ? .goldFourWing : .metalThreeBlade
        }

        var backgroundResource: String {
            self == .gold
                ? "product-identity-gold-background"
                : "product-identity-metal-background"
        }
    }

    @StateObject private var state: ProductUiState
    let mode: Mode

    init(mode: Mode) {
        self.mode = mode
        let previewState = ProductUiState()
        previewState.selectedTab = .spinners
        previewState.isLibraryVisible = true
        previewState.selectedModel = mode.model
        previewState.progressionModel = mode.model
        previewState.progressionLevel = mode == .gold ? 27 : 39
        previewState.progressionLevelTitle = mode == .gold
            ? "镜面装配师"
            : "静音调校师"
        previewState.progressionFraction = mode == .gold ? 0.46 : 0.62
        previewState.progressionTotalExperience = mode == .gold ? 438 : 682
        previewState.progressionLevelStartExperience = mode == .gold ? 361 : 535
        previewState.progressionNextLevelExperience = mode == .gold ? 529 : 821
        previewState.progressionStageMaterial = mode == .gold
            ? "基础合金"
            : "冷银镍铬"
        if mode == .metal {
            previewState.threeBladeMetalSkins = ThreeBladeMetalSkinDetail.parse(
                "ice-guilloche\t35\t冰银回纹\t冷银镍铬\t机刻交错回纹\t冰蓝抛光边\t静音缓冲垫圈\tA9B6BE\t8DE9FF")
            previewState.equippedThreeBladeMetalSkinId = "ice-guilloche"
        }
        previewState.collectorRank = 12
        previewState.collectorFraction = 0.58
        previewState.collectorTotalExperience = 2680
        previewState.collectorRankStartExperience = 2400
        previewState.collectorNextRankExperience = 2880
        previewState.toyBadgeCatalog = BadgeNativePreviewRoot.catalogBadges
        previewState.progressionUnlockedBadgeCount =
            previewState.toyBadgeCatalog.filter(\.unlocked).count
        previewState.progressionTotalBadgeCount = previewState.toyBadgeCatalog.count
        previewState.motionTelemetry = ProductMotionTelemetryState(
            available: true,
            normalizedSpeed: 0.52,
            angularSpeedRadians: 11,
            motionRate: 11,
            speedBand: .engaged,
            intensity: 0.64,
            frequency: 0.40)
        _state = StateObject(wrappedValue: previewState)
    }

    var body: some View {
        GeometryReader { proxy in
            ZStack {
                if let imagePath = Bundle.main.path(
                    forResource: mode.backgroundResource,
                    ofType: "png"),
                   let image = UIImage(contentsOfFile: imagePath) {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFill()
                        .frame(width: proxy.size.width, height: proxy.size.height)
                        .clipped()
                } else {
                    ProductBackdrop()
                }

                LinearGradient(
                    colors: [
                        Color.black.opacity(0.26),
                        Color.clear,
                        Color.black.opacity(0.16)
                    ],
                    startPoint: .top,
                    endPoint: .bottom)
                    .accessibilityHidden(true)

                VStack(spacing: 0) {
                    ProductTopBar(state: state)
                        .frame(height: ProductOverlayLayout.topBarHeight)
                    ProductPanel(state: state)
                }
            }
        }
        .ignoresSafeArea()
        .productDesignSystem()
        .preferredColorScheme(.dark)
    }
}

private struct ProgressionCatalogPreviewScene: View {
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.025, green: 0.12, blue: 0.15),
                    Color(red: 0.02, green: 0.025, blue: 0.035),
                    Color(red: 0.17, green: 0.065, blue: 0.025)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing)

            Circle()
                .fill(Color.cyan.opacity(0.56))
                .frame(width: 590, height: 590)
                .blur(radius: 82)
                .offset(x: -120, y: -260)

            Circle()
                .fill(Color.orange.opacity(0.48))
                .frame(width: 560, height: 560)
                .blur(radius: 92)
                .offset(x: 210, y: 540)
        }
        .ignoresSafeArea()
        .accessibilityHidden(true)
    }
}

/// Simulator-only visual gate for the shipping product catalog. The preview
/// deliberately selects the final shipping case so a missing sixth page is
/// visible before a device build is allowed.
struct FanCardCatalogNativePreviewRoot: View {
    @StateObject private var state = ProductUiState()

    var body: some View {
        GeometryReader { proxy in
            ZStack {
                if let imagePath = Bundle.main.path(
                    forResource: "UnityFanCardHero",
                    ofType: "png"),
                   let image = UIImage(contentsOfFile: imagePath) {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFill()
                        .frame(width: proxy.size.width, height: proxy.size.height)
                        .clipped()
                } else {
                    Color.black
                }

                VStack(spacing: 0) {
                    Color.clear.frame(height: 108)
                    ProductPanel(state: state)
                }
            }
        }
        .ignoresSafeArea()
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .onAppear {
            state.select(.magneticFanCard)
        }
    }
}

/// Simulator-only visual gate for the approved B8 production Badge system.
/// It renders the shipping catalog, card component, detail sheet and share card.
private struct BadgeThumbnailManifest: Decodable {
    let assets: [BadgeThumbnailManifestAsset]
}

private struct BadgeThumbnailManifestAsset: Decodable {
    let id: String
    let assetName: String
    let category: String
    let grade: String
    let displayToken: String
    let shortName: String
}

private struct ProductBadgeThumbnailCategoryPage: View {
    let title: String
    let subtitle: String
    let badges: [ProductBadgeDetail]

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 3) {
                HStack(alignment: .firstTextBaseline) {
                    Text(title)
                        .font(.product(size: 17, weight: .bold))
                        .foregroundStyle(Color.white.opacity(0.94))
                    Spacer()
                    Text(String(format: "%02d", badges.count))
                        .font(.product(size: 11, weight: .bold).monospacedDigit())
                        .foregroundStyle(Color.white.opacity(0.40))
                }
                Text(subtitle)
                    .font(.product(size: 8.5, weight: .semibold))
                    .foregroundStyle(Color.white.opacity(0.44))
                    .lineLimit(1)
            }

            LazyVGrid(
                columns: ProductBadgeLayoutTokens.catalogColumns,
                spacing: ProductBadgeLayoutTokens.catalogRowSpacing) {
                ForEach(badges) { badge in
                    ProductRarityBadge(
                        assetName: badge.assetName,
                        token: badge.tokenLine,
                        shortName: badge.shortName,
                        grade: badge.grade.rawValue,
                        state: ProductBadgeState.unlocked.rawValue,
                        progress: 1,
                        renderingMode: .catalog)
                        .frame(maxWidth: .infinity)
                }
            }

            Spacer(minLength: 0)
        }
        .padding(.horizontal, ProductBadgeLayoutTokens.catalogHorizontalPadding)
        .padding(.vertical, 18)
    }
}

struct BadgeNativePreviewRoot: View {
    enum Mode: String {
        case catalog
        case detail
        case states
        case unlock
        case share
        case reference
        case thumbnailPower
        case thumbnailPulse
        case thumbnailTechnique
        case thumbnailCombo
        case thumbnailFocus
        case thumbnailCollectorFoundation
        case thumbnailCollectorCollection
        case thumbnailChallengeLegacy
    }

    @StateObject private var state = ProductUiState()
    let mode: Mode

    private static let unlocked = badge(
        id: "toy_pulse_100k",
        asset: "badge-b10-toy-pulse-100k",
        token: "100K",
        shortName: "PULSE",
        grade: .singularity,
        state: .unlocked,
        current: 100000,
        target: 100000,
        title: "十万脉冲",
        description: "完成 100,000 次真实手势")

    fileprivate static let catalogBadges: [ProductBadgeDetail] = [
        badge(
            id: "toy_power_ignition",
            asset: "badge-b10-toy-power-ignition",
            token: "1.0 KM/H",
            shortName: "POWER",
            grade: .ignition,
            state: .unlocked,
            current: 1.2,
            target: 1,
            title: "动力点火",
            description: "达到第一档动力门槛"),
        badge(
            id: "toy_pulse_1k",
            asset: "badge-b10-toy-pulse-1k",
            token: "1K",
            shortName: "PULSE",
            grade: .overdrive,
            state: .inProgress,
            current: 680,
            target: 1000,
            title: "千次脉冲",
            description: "完成 1,000 次真实手势"),
        badge(
            id: "toy_combo_20",
            asset: "badge-b10-toy-combo-20",
            token: "×20",
            shortName: "CHAIN",
            grade: .apex,
            state: .inProgress,
            current: 12,
            target: 20,
            title: "Chain 20",
            description: "单次达到 20 Combo"),
        badge(
            id: "toy_technique_speed",
            asset: "badge-b10-toy-technique-speed",
            token: "SPEED",
            shortName: "CONTROL",
            grade: .apex,
            state: .hidden,
            current: 0,
            target: 1,
            title: "Speed",
            description: "完成一次高速技巧",
            visibility: "Hidden"),
        unlocked,
        badge(
            id: "toy_focus_10h",
            asset: "badge-b10-toy-focus-10h",
            token: "10H",
            shortName: "FOCUS",
            grade: .singularity,
            state: .locked,
            current: 0,
            target: 36000,
            title: "专注 10 小时",
            description: "真实触摸累计 10 小时")
    ]

    private static let referenceBadges: [ProductBadgeDetail] = [
        badge(
            id: "toy_pulse_1k",
            asset: "badge-b10-toy-pulse-1k",
            token: "1K",
            shortName: "PULSE",
            grade: .overdrive,
            state: .unlocked,
            current: 1000,
            target: 1000,
            title: "千次脉冲",
            description: "完成 1,000 次真实手势"),
        badge(
            id: "toy_pulse_10k",
            asset: "badge-b10-toy-pulse-10k",
            token: "10K",
            shortName: "PULSE",
            grade: .apex,
            state: .unlocked,
            current: 10000,
            target: 10000,
            title: "万次脉冲",
            description: "完成 10,000 次真实手势"),
        badge(
            id: "toy_technique_speed",
            asset: "badge-b10-toy-technique-speed",
            token: "SPEED",
            shortName: "CONTROL",
            grade: .apex,
            state: .unlocked,
            current: 1,
            target: 1,
            title: "Speed",
            description: "完成一次高速技巧"),
        badge(
            id: "toy_technique_endurance",
            asset: "badge-b10-toy-technique-endurance",
            token: "ENDURE",
            shortName: "CONTROL",
            grade: .apex,
            state: .unlocked,
            current: 1,
            target: 1,
            title: "Endurance",
            description: "完成一次耐力技巧"),
        badge(
            id: "toy_combo_20",
            asset: "badge-b10-toy-combo-20",
            token: "×20",
            shortName: "CHAIN",
            grade: .apex,
            state: .unlocked,
            current: 20,
            target: 20,
            title: "Chain 20",
            description: "单次达到 20 Combo"),
        badge(
            id: "toy_combo_50",
            asset: "badge-b10-toy-combo-50",
            token: "×50",
            shortName: "CHAIN",
            grade: .singularity,
            state: .unlocked,
            current: 50,
            target: 50,
            title: "Chain 50",
            description: "单次达到 50 Combo"),
        badge(
            id: "toy_focus_30m",
            asset: "badge-b10-toy-focus-30m",
            token: "30M",
            shortName: "FOCUS",
            grade: .overdrive,
            state: .unlocked,
            current: 1800,
            target: 1800,
            title: "专注 30 分钟",
            description: "真实触摸累计 30 分钟"),
        badge(
            id: "toy_focus_2h",
            asset: "badge-b10-toy-focus-2h",
            token: "2H",
            shortName: "FOCUS",
            grade: .apex,
            state: .unlocked,
            current: 7200,
            target: 7200,
            title: "专注 2 小时",
            description: "真实触摸累计 2 小时")
    ]

    private static let allThumbnailBadges: [ProductBadgeDetail] = {
        guard let url = Bundle.main.url(
            forResource: "badge-b10-manifest",
            withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let manifest = try? JSONDecoder().decode(
                BadgeThumbnailManifest.self,
                from: data) else { return [] }

        return manifest.assets.enumerated().compactMap { index, asset in
            let grade: ProductBadgeGrade
            switch asset.grade.lowercased() {
            case "ignition": grade = .ignition
            case "overdrive": grade = .overdrive
            case "apex": grade = .apex
            case "singularity": grade = .singularity
            default: return nil
            }

            let scope: ProductBadgeScope
            if asset.id.hasPrefix("toy_") {
                scope = .toy
            } else if asset.id.hasPrefix("collector_") {
                scope = .collector
            } else if asset.id.hasPrefix("challenge_") {
                scope = .challenge
            } else if asset.id.hasPrefix("legacy_") {
                scope = .legacy
            } else {
                return nil
            }

            let token = asset.category == "power"
                ? "\(asset.displayToken) KM/H"
                : asset.displayToken
            let rewards: (experience: Int, shards: Int)
            switch grade {
            case .ignition: rewards = (5, 1)
            case .overdrive: rewards = (10, 2)
            case .apex: rewards = (20, 3)
            case .singularity: rewards = (40, 5)
            }
            return ProductBadgeDetail(
                id: asset.id,
                scope: scope,
                category: asset.category,
                mechanism: "ThumbnailCatalog",
                metric: "ThumbnailCatalog",
                currentValue: 1,
                targetValue: 1,
                progress: 1,
                state: .unlocked,
                unlockedAtUtc: "2026-08-17T00:00:00Z",
                rewardClaimed: true,
                grade: grade,
                visibility: "Standard",
                title: asset.id,
                description: asset.id,
                assetName: asset.assetName,
                displayToken: token,
                displayUnit: "",
                shortName: asset.shortName,
                experienceReward: rewards.experience,
                shardReward: rewards.shards,
                displayOrder: index,
                cycleIndex: 0)
        }
    }()

    private static func thumbnailPageSpec(
        for mode: Mode
    ) -> (title: String, subtitle: String, badges: [ProductBadgeDetail]) {
        let categories: Set<String>
        let title: String
        let subtitle: String
        switch mode {
        case .thumbnailPower:
            categories = ["power"]
            title = "TOY · POWER"
            subtitle = "1.0 · 2.0 · 3.5 · 4.5 KM/H"
        case .thumbnailPulse:
            categories = ["pulse"]
            title = "TOY · PULSE"
            subtitle = "100 · 1K · 10K · 100K"
        case .thumbnailTechnique:
            categories = ["technique"]
            title = "TOY · CONTROL"
            subtitle = "CLEAN · POWER · SPEED · ENDURE · PERFECT"
        case .thumbnailCombo:
            categories = ["combo"]
            title = "TOY · CHAIN"
            subtitle = "×5 · ×10 · ×20 · ×50"
        case .thumbnailFocus:
            categories = ["focus"]
            title = "TOY · FOCUS"
            subtitle = "5M · 30M · 2H · 10H"
        case .thumbnailCollectorFoundation:
            categories = ["rhythm", "explore"]
            title = "COLLECTOR · RHYTHM / EXPLORE"
            subtitle = "VALID WEEKS · DISCOVERED MODELS"
        case .thumbnailCollectorCollection:
            categories = ["mastery", "collection"]
            title = "COLLECTOR · MASTERY / VAULT"
            subtitle = "TOY LEVELS · APPEARANCE COLLECTION"
        case .thumbnailChallengeLegacy:
            categories = ["challenge", "legacy"]
            title = "CHALLENGE + LEGACY"
            subtitle = "WEEKLY · CYCLE · FOUNDER"
        default:
            categories = []
            title = "BADGE THUMBNAILS"
            subtitle = "SHIPPING MANIFEST"
        }
        return (
            title,
            subtitle,
            allThumbnailBadges.filter { categories.contains($0.category) })
    }

    var body: some View {
        Group {
            switch mode {
            case .catalog:
                ProgressionBadgeAchievements(
                    snapshot: ProgressionCatalogSnapshot(state: state))
                    .background(ProductBackdrop().ignoresSafeArea())
            case .detail:
                ProductBadgeDetailSheet(
                    badge: Self.unlocked,
                    accent: Color(red: 0.72, green: 0.82, blue: 0.88),
                    toyName: "三叶金属")
            case .states:
                ScrollView {
                    VStack(alignment: .leading, spacing: 14) {
                        ProductScreenHeading(
                            title: "BADGE STATES",
                            subtitle: "Locked · In progress · Hidden · Unlocked",
                            symbol: "seal.fill",
                            accent: Color.white.opacity(0.78))
                        LazyVGrid(
                            columns: ProductBadgeLayoutTokens.catalogColumns,
                            spacing: ProductBadgeLayoutTokens.catalogRowSpacing) {
                            ForEach(Self.catalogBadges.prefix(4)) { badge in
                                ProductRarityBadge(
                                    assetName: badge.assetName,
                                    token: badge.tokenLine,
                                    shortName: badge.shortName,
                                    grade: badge.grade.rawValue,
                                    state: badge.state.rawValue,
                                    progress: badge.progress,
                                    renderingMode: .catalog)
                                    .frame(maxWidth: .infinity)
                            }
                        }
                    }
                    .padding(.horizontal, ProductBadgeLayoutTokens.catalogHorizontalPadding)
                    .padding(.vertical, 18)
                }
                .background(ProductBackdrop().ignoresSafeArea())
            case .unlock:
                ZStack {
                    ProductBackdrop().ignoresSafeArea()
                    BadgeUnlockOverlay(state: state)
                }
            case .share:
                ZStack {
                    Color.black.ignoresSafeArea()
                    ProductBadgeShareCard(
                        badge: Self.unlocked,
                        toyName: "三叶金属")
                        .frame(width: 360, height: 360)
                }
            case .reference:
                ScrollView {
                    VStack(alignment: .leading, spacing: 12) {
                        ProductScreenHeading(
                            title: "B10 · CHALLENGE + LEGACY MASTER",
                            subtitle: "rounded satin frame · recessed leather · pearl relief",
                            symbol: "sparkles",
                            accent: Color.white.opacity(0.82))
                        LazyVGrid(
                            columns: ProductBadgeLayoutTokens.catalogColumns,
                            spacing: ProductBadgeLayoutTokens.catalogRowSpacing) {
                            ForEach(Self.referenceBadges) { badge in
                                ProductRarityBadge(
                                    assetName: badge.assetName,
                                    token: badge.tokenLine,
                                    shortName: badge.shortName,
                                    grade: badge.grade.rawValue,
                                    state: badge.state.rawValue,
                                    progress: 1,
                                    renderingMode: .catalog)
                                    .frame(maxWidth: .infinity)
                            }
                        }
                    }
                    .padding(.horizontal, ProductBadgeLayoutTokens.catalogHorizontalPadding)
                    .padding(.vertical, 18)
                }
                .background(ProductBackdrop().ignoresSafeArea())
            case .thumbnailPower,
                 .thumbnailPulse,
                 .thumbnailTechnique,
                 .thumbnailCombo,
                 .thumbnailFocus,
                 .thumbnailCollectorFoundation,
                 .thumbnailCollectorCollection,
                 .thumbnailChallengeLegacy:
                let spec = Self.thumbnailPageSpec(for: mode)
                ProductBadgeThumbnailCategoryPage(
                    title: spec.title,
                    subtitle: spec.subtitle,
                    badges: spec.badges)
                .background(ProductBackdrop().ignoresSafeArea())
            }
        }
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .onAppear {
            state.progressionModel = .metalThreeBlade
            state.toyBadgeCatalog = Self.catalogBadges
            if mode == .unlock {
                state.badgeUnlockNotice = ProductBadgeUnlockEvent(
                    id: "preview:\(Self.unlocked.unlockIdentity)",
                    badge: Self.unlocked,
                    sourceTitle: "三叶金属")
                state.showingBadgeUnlockNotice = true
            }
            let thumbnailSpec = Self.thumbnailPageSpec(for: mode)
            if !thumbnailSpec.badges.isEmpty {
                ProductRarityBadge.prewarmCatalogArtwork(
                    assetNames: thumbnailSpec.badges.map(\.assetName))
            }
        }
    }

    @MainActor
    static func renderShareCard(completion: @escaping (UIImage?) -> Void) {
        ProductBadgeShareRenderer.render(
            badge: unlocked,
            toyName: "三叶金属",
            completion: completion)
    }

    private static func badge(
        id: String,
        asset: String,
        token: String,
        shortName: String,
        grade: ProductBadgeGrade,
        state: ProductBadgeState,
        current: Double,
        target: Double,
        title: String,
        description: String,
        visibility: String = "Standard") -> ProductBadgeDetail {
        let experience: Int
        let shards: Int
        switch grade {
        case .ignition: experience = 5; shards = 1
        case .overdrive: experience = 10; shards = 2
        case .apex: experience = 20; shards = 3
        case .singularity: experience = 40; shards = 5
        }
        return ProductBadgeDetail(
            id: id,
            scope: .toy,
            category: "Preview",
            mechanism: "Rotor",
            metric: "Preview",
            currentValue: current,
            targetValue: target,
            progress: target <= 0 ? 0 : min(1, current / target),
            state: state,
            unlockedAtUtc: state == .unlocked
                ? "2026-08-08T10:00:00Z"
                : "",
            rewardClaimed: state == .unlocked,
            grade: grade,
            visibility: visibility,
            title: title,
            description: description,
            assetName: asset,
            displayToken: token,
            displayUnit: "",
            shortName: shortName,
            experienceReward: experience,
            shardReward: shards,
            displayOrder: 0,
            cycleIndex: 0)
    }
}

/// Simulator-only visual gate for the wallpaper-style environment picker.
/// It renders the same terminal 66% card, title and pager used in-app.
struct EnvironmentWallpaperPickerNativePreviewRoot: View {
    enum Mode: String {
        case adaptive
        case canyon
        case cyberpunk
        case mineralRidge = "mineral-ridge"
    }

    @StateObject private var state: ProductUiState
    let mode: Mode

    init(mode: Mode) {
        self.mode = mode
        let initialTheme: EnvironmentTheme
        switch mode {
        case .adaptive: initialTheme = .adaptive
        case .canyon: initialTheme = .canyon
        case .cyberpunk: initialTheme = .cyberpunk
        case .mineralRidge: initialTheme = .mineralRidge
        }
        let initialState = ProductUiState()
        initialState.environmentTheme = initialTheme
        initialState.environmentThemePreview = initialTheme
        initialState.isEnvironmentPickerPresented = true
        _state = StateObject(wrappedValue: initialState)
    }

    private var previewTheme: EnvironmentTheme {
        switch mode {
        case .adaptive: return .adaptive
        case .canyon: return .canyon
        case .cyberpunk: return .cyberpunk
        case .mineralRidge: return .mineralRidge
        }
    }

    var body: some View {
        SceneWallpaperPicker(
            state: state,
            capturedScreen: nil,
            capturedTheme: previewTheme,
            startsEntered: true,
            onSelect: { _ in })
    }
}

#endif

private struct ProductPanel: View {
    @ObservedObject var state: ProductUiState

    private var showsLiveModelStage: Bool {
        state.selectedTab == .spinners
    }

    var body: some View {
        VStack(spacing: 0) {
            Group {
                if state.selectedTab == .settings {
                    SettingsPanel(state: state)
                } else if state.selectedTab == .collector {
                    CollectorProfile(state: state)
                } else {
                    SpinnerLibrary(state: state)
                }
            }
        }
        .background {
            if showsLiveModelStage {
                // The library previews the live Unity renderer. Its center must
                // stay transparent instead of placing an opaque dark page over it.
                Color.clear
            } else {
                ProductBackdrop().ignoresSafeArea()
            }
        }
        .clipShape(RoundedRectangle(cornerRadius: 26, style: .continuous))
        .productDesignSystem()
        .preferredColorScheme(.dark)
    }
}

#if DEBUG
/// Simulator-only visual gate for the shipping Haptic settings navigation.
/// It composes the real top bar and settings panel at the same heights used by
/// the UIKit overlay manager, so the save-and-return affordance is reviewed
/// before an updated native shell is installed on an iPhone.
struct HapticSettingsSaveNativePreviewRoot: View {
    @StateObject private var state = ProductUiState()

    var body: some View {
        VStack(spacing: 0) {
            ProductTopBar(state: state)
                .frame(height: 108)
            SettingsPanel(state: state)
        }
        .background(ProductBackdrop().ignoresSafeArea())
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .onAppear {
            state.selectedTab = .settings
            state.isLibraryVisible = false
            state.detentPresetIndex = 1
            state.detentPresetCount = 4
            // Preview-only placeholder: shipping preset labels are supplied by
            // the managed runtime catalog and must not be duplicated in Swift.
            state.detentPresetName = "预设 2"
            state.detentPresetDetents = 12
            state.detentTuningIntensity = 1
            state.detentTuningSharpness = 0.72
        }
    }
}
#endif

@MainActor
private final class CodexSwiftUIOverlayManager {
    static let shared = CodexSwiftUIOverlayManager()

    let state = ProductUiState()
    private var feedbackController: UIHostingController<SpinnerExperienceFeedbackLayer>?
    private var badgeController: UIHostingController<BadgeUnlockOverlay>?
    private var topController: UIHostingController<ProductTopBar>?
    private var modeController: UIHostingController<ProductModeBar>?
    private var progressionController: UIHostingController<SpinnerProgressionHUD>?
    private var panelController: UIHostingController<ProductPanel>?
    private var appearanceController: UIHostingController<ProductAppearanceEditor>?
    private var environmentPickerController: UIHostingController<SceneWallpaperPicker>?
    private var displayCaseController: UIHostingController<PremiumDisplayCaseExperienceView>?
    private var progressionRewardController: UIViewController?
    private var progressionRewardFlightController: UIViewController?
    private var pendingOfflineRewardFlight = false

    func install(retryCount: Int = 0) {
        guard topController == nil else {
            return
        }
        guard let rootController = activeRootViewController() else {
            // Unity can invoke the application-level bootstrap one run-loop
            // before its UIWindow becomes key. Retry briefly instead of
            // permanently dropping the only native-UI installation request.
            guard retryCount < 12 else { return }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.10) { [weak self] in
                self?.install(retryCount: retryCount + 1)
            }
            return
        }

        ProductTypography.configureUIKitAppearance()

        let feedback = UIHostingController(
            rootView: SpinnerExperienceFeedbackLayer(state: state))
        let badge = UIHostingController(rootView: BadgeUnlockOverlay(state: state))
        let top = UIHostingController(rootView: ProductTopBar(state: state))
        let mode = UIHostingController(rootView: ProductModeBar(state: state))
        let progression = UIHostingController(rootView: SpinnerProgressionHUD(state: state))
        configure(feedback, in: rootController)
        feedback.view.isUserInteractionEnabled = false
        configure(badge, in: rootController)
        badge.view.isUserInteractionEnabled = false
        configure(top, in: rootController)
        configure(mode, in: rootController)
        configure(progression, in: rootController)
        mode.view.isHidden = true
        progression.view.isHidden = true
        feedback.view.isHidden = true

        NSLayoutConstraint.activate([
            feedback.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            feedback.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            feedback.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            feedback.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor),

            badge.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            badge.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            badge.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            badge.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor),

            top.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            top.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            top.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            top.view.heightAnchor.constraint(
                equalToConstant: ProductOverlayLayout.topBarHeight),

            mode.view.topAnchor.constraint(
                equalTo: rootController.view.topAnchor,
                constant: ProductOverlayLayout.modeBarTop),
            mode.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            mode.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            mode.view.heightAnchor.constraint(
                equalToConstant: ProductOverlayLayout.modeBarHeight),

            progression.view.leadingAnchor.constraint(
                equalTo: rootController.view.leadingAnchor,
                constant: 12),
            progression.view.trailingAnchor.constraint(
                equalTo: rootController.view.trailingAnchor,
                constant: -12),
            progression.view.bottomAnchor.constraint(
                equalTo: rootController.view.safeAreaLayoutGuide.bottomAnchor,
                constant: -ProductOverlayLayout.progressionBottomInset),
            progression.view.heightAnchor.constraint(
                equalToConstant: ProductOverlayLayout.progressionHeight)
        ])

        feedbackController = feedback
        badgeController = badge
        topController = top
        modeController = mode
        progressionController = progression
        state.applyAndPersist(includeMode: true)
        state.restorePersistedDetentTuningIfAvailable()
        GachaShippingRevealContinuation.preparePremiumDisplayCase = {
            [weak self] requestID, receipt in
            self?.presentGachaPrizeDisplayCase(
                requestID: requestID,
                receipt: receipt)
        }
        GachaShippingRevealContinuation.cancelPreparedDisplayCase = {
            [weak self] in
            self?.dismissDisplayCase()
        }
        UnityBridge.send("RequestDetentFeelStateFromNativeUi")
        UnityBridge.send("RequestProgressionStateFromNativeUi")
        showPanel()
    }

    func selectTab(_ tab: ProductTab) {
        dismissEnvironmentPicker(resetPreview: true, animated: false)
        dismissAppearanceEditorIfNeeded()
        state.selectedTab = tab
        let showsSpinnerControls = tab == .spinners
            && !state.isLibraryVisible
        setModeBarVisible(showsSpinnerControls)
        UnityBridge.send(
            "SetLibraryPreviewActiveFromNativeUi",
            value: String(tab == .spinners && state.isLibraryVisible))
        if tab != .spinners || state.isLibraryVisible {
            showPanel()
        } else {
            hidePanel()
        }
    }

    func presentProgressionRewardIfNeeded() {
        guard progressionRewardController == nil,
              !pendingOfflineRewardFlight,
              progressionRewardFlightController == nil,
              let rootController = activeRootViewController() else { return }

        let kind: ProgressionCelebrationKind
        if state.showingOfflineProgressionReward {
            kind = .offline
        } else if state.showingLiveProgressionLevelUp {
            kind = .liveLevelUp
        } else {
            return
        }

        let controller = UIHostingController(
            rootView: ProgressionRewardCelebrationView(
                state: state,
                kind: kind,
                onComplete: { [weak self] in
                    self?.dismissProgressionReward(kind: kind)
                }))
        configure(controller, in: rootController, background: .clear)
        controller.view.isUserInteractionEnabled = true
        controller.view.isMultipleTouchEnabled = true
        controller.view.accessibilityViewIsModal = true
        controller.view.alpha = 0
        NSLayoutConstraint.activate([
            controller.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            controller.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            controller.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            controller.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor)
        ])
        rootController.view.layoutIfNeeded()
        rootController.view.bringSubviewToFront(controller.view)
        progressionRewardController = controller
        UIView.animate(withDuration: 0.18) {
            controller.view.alpha = 1
        }
    }

    private func dismissProgressionReward(kind: ProgressionCelebrationKind) {
        guard let controller = progressionRewardController else { return }
        progressionRewardController = nil
        controller.view.isUserInteractionEnabled = false
        let offlineReward = kind == .offline
            ? state.offlineProgressionReward
            : nil
        let sheetAvatarFrame = state.progressionSheetAvatarFrame
        if offlineReward != nil {
            pendingOfflineRewardFlight = true
        }

        switch kind {
        case .offline:
            state.dismissOfflineProgressionReward()
        case .liveLevelUp:
            state.dismissLiveProgressionLevelUp()
        }

        controller.willMove(toParent: nil)
        UIView.animate(
            withDuration: 0.18,
            animations: { controller.view.alpha = 0 },
            completion: { [weak self] _ in
                controller.view.removeFromSuperview()
                controller.removeFromParent()
                guard let self,
                      let offlineReward else { return }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.42) {
                    self.presentOfflineProgressionFlight(
                        reward: offlineReward,
                        sourceWindowFrame: sheetAvatarFrame)
                }
            })
    }

    private func presentOfflineProgressionFlight(
        reward: OfflineProgressionReward,
        sourceWindowFrame: CGRect,
        retryCount: Int = 0
    ) {
        guard progressionRewardFlightController == nil,
              let rootController = activeRootViewController(),
              let window = rootController.view.window else {
            retryOfflineProgressionFlight(
                reward: reward,
                sourceWindowFrame: sourceWindowFrame,
                retryCount: retryCount)
            return
        }

        let targetWindowFrame = state.progressionTopAvatarFrame
        guard sourceWindowFrame.width > 1,
              sourceWindowFrame.height > 1,
              targetWindowFrame.width > 1,
              targetWindowFrame.height > 1 else {
            retryOfflineProgressionFlight(
                reward: reward,
                sourceWindowFrame: sourceWindowFrame,
                retryCount: retryCount)
            return
        }

        let sourceFrame = rootController.view.convert(sourceWindowFrame, from: window)
        let targetFrame = rootController.view.convert(targetWindowFrame, from: window)
        let controller = UIHostingController(
            rootView: ProgressionPageRewardFlightView(
                experience: reward.experience,
                accent: reward.model.accent,
                sourceFrame: sourceFrame,
                targetFrame: targetFrame,
                onArrive: { [weak self] in
                    self?.state.commitProgressionTopAvatar(reward)
                    UnityBridge.feedback(.medium)
                },
                onComplete: { [weak self] in
                    self?.finishOfflineProgressionFlight()
                }))
        configure(controller, in: rootController, background: .clear)
        controller.view.isUserInteractionEnabled = false
        controller.view.accessibilityElementsHidden = true
        NSLayoutConstraint.activate([
            controller.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            controller.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            controller.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            controller.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor)
        ])
        rootController.view.layoutIfNeeded()
        rootController.view.bringSubviewToFront(controller.view)
        if let topController {
            rootController.view.bringSubviewToFront(topController.view)
        }
        progressionRewardFlightController = controller
    }

    private func retryOfflineProgressionFlight(
        reward: OfflineProgressionReward,
        sourceWindowFrame: CGRect,
        retryCount: Int
    ) {
        guard retryCount < 12 else {
            state.commitProgressionTopAvatar(reward)
            pendingOfflineRewardFlight = false
            presentProgressionRewardIfNeeded()
            return
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) { [weak self] in
            self?.presentOfflineProgressionFlight(
                reward: reward,
                sourceWindowFrame: sourceWindowFrame,
                retryCount: retryCount + 1)
        }
    }

    private func finishOfflineProgressionFlight() {
        guard let controller = progressionRewardFlightController else { return }
        progressionRewardFlightController = nil
        pendingOfflineRewardFlight = false
        controller.willMove(toParent: nil)
        controller.view.removeFromSuperview()
        controller.removeFromParent()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.22) { [weak self] in
            self?.presentProgressionRewardIfNeeded()
        }
    }

    func showMySpinners() {
        dismissEnvironmentPicker(resetPreview: true, animated: false)
        dismissAppearanceEditorIfNeeded()
        state.selectedTab = .spinners
        state.isLibraryVisible = true
        setModeBarVisible(false)
        showPanel()
        beginLibraryPreview()
    }

    func previewModel(_ model: SpinnerModel) {
        state.select(model)
        UnityBridge.send("SetLibraryPreviewActiveFromNativeUi", value: "true")
        UnityBridge.send("SelectModelFromNativeUi", value: model.rawValue)
    }

    func beginLibraryPreview() {
        guard state.selectedTab == .spinners && state.isLibraryVisible else { return }
        UnityBridge.send("SetLibraryPreviewActiveFromNativeUi", value: "true")
    }

    func enterSelectedModel() {
        dismissEnvironmentPicker(resetPreview: true, animated: false)
        dismissAppearanceEditorIfNeeded()
        state.selectedTab = .spinners
        state.isLibraryVisible = false
        UnityBridge.send("SetLibraryPreviewActiveFromNativeUi", value: "false")
        UnityBridge.send("SelectModelFromNativeUi", value: state.selectedModel.rawValue)
        setModeBarVisible(false)
        hidePanel(forDetailEntrance: true)
        DispatchQueue.main.asyncAfter(
            deadline: .now() + ProductOverlayLayout.detailControlsRevealDelay) {
            [weak self] in
            guard let self,
                  self.state.selectedTab == .spinners,
                  !self.state.isLibraryVisible else { return }
            self.setModeBarVisible(true)
        }
        DispatchQueue.main.asyncAfter(
            deadline: .now() + ProductOverlayLayout.detailEntranceDuration) {
            [weak self] in
            guard let self,
                  self.state.selectedTab == .spinners,
                  !self.state.isLibraryVisible else { return }
            self.state.presentSpinnerOnboardingIfNeeded()
        }
    }

    func presentEnvironmentPicker() {
        guard environmentPickerController == nil,
              state.selectedTab == .spinners,
              state.isLibraryVisible,
              let rootController = activeRootViewController() else { return }

        let capturedTheme = state.environmentTheme
        let capturedScreen = captureScreen(from: rootController.view)
        state.beginEnvironmentThemePreview()
        UnityBridge.feedback(.medium)
        let transition = SceneWallpaperPickerTransition(
            startsEntered: false)

        let picker = UIHostingController(
            rootView: SceneWallpaperPicker(
                state: state,
                capturedScreen: capturedScreen,
                capturedTheme: capturedTheme,
                transition: transition,
                onSelect: { [weak self] theme in
                    self?.selectEnvironmentTheme(theme)
                }))
        // Keep the hosting view transparent until SwiftUI has drawn the frozen
        // current screen. An outer alpha fade would insert a black dissolve
        // before the scale and break the one-surface wallpaper transition.
        configure(picker, in: rootController, background: .clear)
        picker.view.alpha = 1
        NSLayoutConstraint.activate([
            picker.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            picker.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            picker.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            picker.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor)
        ])
        rootController.view.layoutIfNeeded()
        rootController.view.bringSubviewToFront(picker.view)
        environmentPickerController = picker
        DispatchQueue.main.async { [weak transition] in
            transition?.begin(
                reduceMotion: UIAccessibility.isReduceMotionEnabled)
        }
    }

    func presentDisplayCase() {
        guard displayCaseController == nil,
              let rootController = activeRootViewController() else { return }
        dismissEnvironmentPicker(resetPreview: true, animated: false)
        dismissAppearanceEditorIfNeeded()
        UnityBridge.send("SetDisplayCasePresentedFromNativeUi", value: "true")

        let controller = UIHostingController(
            rootView: PremiumDisplayCaseExperienceView(onClose: { [weak self] in
                self?.dismissDisplayCase()
            }))
        configure(controller, in: rootController, background: .clear)
        NSLayoutConstraint.activate([
            controller.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            controller.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            controller.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            controller.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor)
        ])
        topController?.view.isHidden = true
        modeController?.view.isHidden = true
        progressionController?.view.isHidden = true
        panelController?.view.isHidden = true
        rootController.view.bringSubviewToFront(controller.view)
        displayCaseController = controller
    }

    func presentGachaPrizeDisplayCase(
        requestID: String,
        receipt: GachaReceiptRow
    ) {
        guard displayCaseController == nil,
              let rootController = activeRootViewController() else { return }
        dismissEnvironmentPicker(resetPreview: true, animated: false)
        dismissAppearanceEditorIfNeeded()
        UnityBridge.send(
            "PresentGachaPrizeFromNativeUi",
            value: "\(requestID.lowercased())|\(receipt.prizeId)")

        let controller = UIHostingController(
            rootView: PremiumDisplayCaseExperienceView(
                gachaRequestId: requestID.lowercased(),
                gachaReceipt: receipt,
                onClose: { [weak self] in
                    self?.dismissDisplayCase()
                },
                onAccept: { [weak self] in
                    self?.acceptGachaReveal(requestID: requestID)
                }))
        configure(controller, in: rootController, background: .clear)
        NSLayoutConstraint.activate([
            controller.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            controller.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            controller.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            controller.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor)
        ])
        topController?.view.isHidden = true
        modeController?.view.isHidden = true
        progressionController?.view.isHidden = true
        panelController?.view.isHidden = true
        rootController.view.bringSubviewToFront(controller.view)
        displayCaseController = controller
    }

    private func acceptGachaReveal(requestID: String) {
        UnityBridge.send(
            "AcknowledgeGachaReceiptFromNativeUi",
            value: requestID.lowercased())
        GachaStoreModel.shared.resetRevealPresentation()
        dismissDisplayCase(notifyUnity: false)
    }

    private func dismissDisplayCase(notifyUnity: Bool = true) {
        if notifyUnity {
            UnityBridge.send("SetDisplayCasePresentedFromNativeUi", value: "false")
        }
        guard let controller = displayCaseController else { return }
        displayCaseController = nil
        controller.willMove(toParent: nil)
        controller.view.removeFromSuperview()
        controller.removeFromParent()
        topController?.view.isHidden = false
        panelController?.view.isHidden = false
        setModeBarVisible(false)
        showPanel()
    }

    private func selectEnvironmentTheme(_ theme: EnvironmentTheme) {
        UnityBridge.feedback(.medium)
        state.selectEnvironmentTheme(theme)
        // Keep the frozen picker above Unity while its renderer swaps the
        // environment, then reveal the newly selected live scene.
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.18) { [weak self] in
            self?.dismissEnvironmentPicker(
                resetPreview: false,
                animated: true)
        }
    }

    private func dismissEnvironmentPicker(
        resetPreview: Bool,
        animated: Bool
    ) {
        if resetPreview {
            state.cancelEnvironmentThemePreview()
        } else {
            state.isEnvironmentPickerPresented = false
        }
        guard let picker = environmentPickerController else { return }
        environmentPickerController = nil
        picker.willMove(toParent: nil)

        let removePicker = {
            picker.view.removeFromSuperview()
            picker.removeFromParent()
        }
        guard animated else {
            removePicker()
            return
        }

        UIView.animate(
            withDuration: 0.24,
            delay: 0,
            options: [.curveEaseInOut, .beginFromCurrentState]) {
                picker.view.alpha = 0
            } completion: { _ in
                removePicker()
            }
    }

    private func captureScreen(from view: UIView) -> UIImage? {
        guard view.bounds.width > 0, view.bounds.height > 0 else { return nil }
        let format = UIGraphicsImageRendererFormat.default()
        format.scale = view.window?.screen.scale ?? UIScreen.main.scale
        format.opaque = true
        return UIGraphicsImageRenderer(bounds: view.bounds, format: format).image { _ in
            if !view.drawHierarchy(in: view.bounds, afterScreenUpdates: false) {
                view.layer.render(in: UIGraphicsGetCurrentContext()!)
            }
        }
    }

    func dismissPanelToSelectedModel() {
        enterSelectedModel()
    }

    func setAppearanceEditorPresented(_ presented: Bool) {
        if presented {
            presentAppearanceEditor()
        } else {
            dismissAppearanceEditor(notifyUnity: false)
        }
    }

    private func presentAppearanceEditor() {
        guard appearanceController == nil,
              state.selectedTab == .spinners,
              !state.isLibraryVisible,
              let rootController = activeRootViewController() else {
            UnityBridge.send(
                "SetAppearanceEditorPresentedFromNativeUi",
                value: "false")
            return
        }

        let appearance = UIHostingController(
            rootView: ProductAppearanceEditor(state: state) { [weak self] in
                self?.dismissAppearanceEditor(notifyUnity: true)
            })
        configure(appearance, in: rootController, background: .clear)
        appearance.view.alpha = 0
        appearance.view.transform = CGAffineTransform(translationX: 0, y: 54)
        NSLayoutConstraint.activate([
            appearance.view.topAnchor.constraint(
                equalTo: rootController.view.topAnchor,
                constant: 108),
            appearance.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            appearance.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            appearance.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor)
        ])

        setModeBarVisible(false)
        rootController.view.bringSubviewToFront(appearance.view)
        if let topController {
            rootController.view.bringSubviewToFront(topController.view)
        }
        appearanceController = appearance
        UIView.animate(
            withDuration: 0.28,
            delay: 0,
            usingSpringWithDamping: 0.90,
            initialSpringVelocity: 0.10,
            options: [.curveEaseOut, .beginFromCurrentState]) {
                appearance.view.alpha = 1
                appearance.view.transform = .identity
            }
    }

    private func dismissAppearanceEditorIfNeeded() {
        guard appearanceController != nil else { return }
        dismissAppearanceEditor(notifyUnity: true)
    }

    private func dismissAppearanceEditor(notifyUnity: Bool) {
        guard let appearance = appearanceController else {
            if notifyUnity {
                UnityBridge.send(
                    "SetAppearanceEditorPresentedFromNativeUi",
                    value: "false")
            }
            return
        }

        appearanceController = nil
        appearance.willMove(toParent: nil)
        UIView.animate(
            withDuration: 0.24,
            delay: 0,
            options: [.curveEaseIn, .beginFromCurrentState]) {
                appearance.view.alpha = 0
                appearance.view.transform = CGAffineTransform(translationX: 0, y: 46)
            } completion: { _ in
                appearance.view.removeFromSuperview()
                appearance.removeFromParent()
            }

        let showsSpinnerControls = state.selectedTab == .spinners
            && !state.isLibraryVisible
        setModeBarVisible(showsSpinnerControls)
        if notifyUnity {
            UnityBridge.send(
                "SetAppearanceEditorPresentedFromNativeUi",
                value: "false")
        }
    }

    private func showPanel() {
        guard panelController == nil,
              let rootController = activeRootViewController() else {
            return
        }

        let panel = UIHostingController(rootView: ProductPanel(state: state))
        configure(panel, in: rootController, background: .clear)
        panel.view.alpha = 0
        panel.view.transform = CGAffineTransform(translationX: 0, y: 24)
        NSLayoutConstraint.activate([
            panel.view.topAnchor.constraint(equalTo: rootController.view.topAnchor, constant: 108),
            panel.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            panel.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            panel.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor)
        ])

        if let topController,
           let modeController,
           let progressionController,
           let badgeController {
            rootController.view.bringSubviewToFront(topController.view)
            rootController.view.bringSubviewToFront(modeController.view)
            rootController.view.bringSubviewToFront(progressionController.view)
            rootController.view.bringSubviewToFront(badgeController.view)
        }
        panelController = panel
        UIView.animate(
            withDuration: 0.34,
            delay: 0,
            usingSpringWithDamping: 0.88,
            initialSpringVelocity: 0.12,
            options: [.curveEaseOut, .beginFromCurrentState]) {
            panel.view.alpha = 1
            panel.view.transform = .identity
        }
    }

    private func hidePanel(forDetailEntrance: Bool = false) {
        guard let panel = panelController else { return }
        panel.willMove(toParent: nil)
        let duration = forDetailEntrance ? 0.52 : 0.30
        let targetTransform = forDetailEntrance
            ? CGAffineTransform(scaleX: 1.045, y: 1.045)
                .translatedBy(x: 0, y: 12)
            : CGAffineTransform(translationX: 0, y: 28)
        UIView.animate(
            withDuration: duration,
            delay: 0,
            options: [.curveEaseIn, .beginFromCurrentState]) {
                panel.view.alpha = 0
                panel.view.transform = targetTransform
            } completion: { _ in
                panel.view.removeFromSuperview()
                panel.removeFromParent()
            }
        panelController = nil
    }

    private func setModeBarVisible(_ visible: Bool) {
        guard let view = modeController?.view else { return }
        // The fifth product is always a six-step magnetic mechanism. Rotary
        // smooth/ratchet controls must neither appear nor override its profile.
        view.isHidden = !visible
            || state.selectedModel == .magneticSlideTile
            || state.selectedModel == .magneticFanCard
        progressionController?.view.isHidden = !visible
        feedbackController?.view.isHidden = !visible
        if visible, let parent = view.superview {
            parent.bringSubviewToFront(view)
            if let progressionView = progressionController?.view {
                parent.bringSubviewToFront(progressionView)
            }
            if let badgeView = badgeController?.view {
                parent.bringSubviewToFront(badgeView)
            }
        }
    }

    private func configure<Content: View>(
        _ controller: UIHostingController<Content>,
        in parent: UIViewController,
        background: UIColor = .clear) {
        controller.overrideUserInterfaceStyle = .dark
        controller.view.translatesAutoresizingMaskIntoConstraints = false
        controller.view.backgroundColor = background
        controller.view.isOpaque = background != .clear
        controller.view.clipsToBounds = false
        parent.addChild(controller)
        parent.view.addSubview(controller.view)
        controller.didMove(toParent: parent)
    }

    private func activeRootViewController() -> UIViewController? {
        let scenes = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
        let scene = scenes.first { $0.activationState == .foregroundActive } ?? scenes.first
        let window = scene?.windows.first { $0.isKeyWindow } ?? scene?.windows.first
        return window?.rootViewController
    }
}

@_cdecl("CodexSwiftUiOverlayInstall")
public func CodexSwiftUiOverlayInstall() {
    DispatchQueue.main.async {
        CodexSwiftUIOverlayManager.shared.install()
    }
}

@_cdecl("CodexAppearanceEditorSetPresented")
public func CodexAppearanceEditorSetPresented(_ presented: Int32) {
    DispatchQueue.main.async {
        CodexSwiftUIOverlayManager.shared.setAppearanceEditorPresented(
            presented != 0)
    }
}

@_cdecl("CodexHapticLabReceiveTelemetry")
public func CodexHapticLabReceiveTelemetry(
    _ angularSpeedRadians: Float,
    _ rpm: Float,
    _ detentsPerSecond: Float,
    _ detentIntensityGain: Float,
    _ continuousIntensity: Float,
    _ continuousSharpness: Float,
    _ speedBand: Int32,
    _ continuousActive: Int32,
    _ renderedEventCount: Int32,
    _ suppressedEventCount: Int32,
    _ lastSemanticEvent: Int32,
    _ nativeStatus: Int32) {
    let snapshot = HapticLabTelemetrySnapshot(
        angularSpeedRadians: Double(angularSpeedRadians),
        rpm: Double(rpm),
        detentsPerSecond: Double(detentsPerSecond),
        detentIntensityGain: Double(detentIntensityGain),
        continuousIntensity: Double(continuousIntensity),
        continuousSharpness: Double(continuousSharpness),
        speedBand: Int(speedBand),
        continuousActive: continuousActive != 0,
        renderedEventCount: Int(renderedEventCount),
        suppressedEventCount: Int(suppressedEventCount),
        lastSemanticEvent: Int(lastSemanticEvent),
        nativeStatus: Int(nativeStatus))
    Task { @MainActor in
        CodexSwiftUIOverlayManager.shared.state.updateHapticTelemetry(snapshot)
    }
}

@_cdecl("CodexDetentTuningReceiveState")
public func CodexDetentTuningReceiveState(
    _ presetIndex: Int32,
    _ presetCount: Int32,
    _ presetName: UnsafePointer<CChar>?,
    _ detentsPerRevolution: Int32,
    _ intensity: Float,
    _ sharpness: Float) {
    let name = presetName.map { String(cString: $0) } ?? "—"
    Task { @MainActor in
        CodexSwiftUIOverlayManager.shared.state.updateDetentTuning(
            presetIndex: Int(presetIndex),
            presetCount: Int(presetCount),
            presetName: name,
            detents: Int(detentsPerRevolution),
            intensity: Double(intensity),
            sharpness: Double(sharpness))
    }
}

@_cdecl("CodexProgressionReceiveState")
public func CodexProgressionReceiveState(
    _ modelId: UnsafePointer<CChar>?,
    _ level: Int32,
    _ totalExperience: Float,
    _ levelStartExperience: Float,
    _ nextLevelExperience: Float,
    _ levelProgress: Float,
    _ stageName: UnsafePointer<CChar>?,
    _ stageComponent: UnsafePointer<CChar>?,
    _ stageMaterial: UnsafePointer<CChar>?,
    _ levelTitle: UnsafePointer<CChar>?,
    _ levelCatalog: UnsafePointer<CChar>?,
    _ nextUnlockLevel: Int32,
    _ nextUnlockName: UnsafePointer<CChar>?,
    _ assistantEnabled: Int32,
    _ assistantSpeedMultiplier: Float,
    _ offlineModelId: UnsafePointer<CChar>?,
    _ offlineAssistantEnabled: Int32,
    _ offlineExperience: Float,
    _ offlineHours: Float,
    _ previousLevel: Int32,
    _ offlineNewLevel: Int32,
    _ offlinePreviousLevelProgress: Float,
    _ offlineNewLevelProgress: Float,
    _ livePreviousLevel: Int32,
    _ liveRewardName: UnsafePointer<CChar>?,
    _ peakRimSpeedKmh: Float,
    _ lifetimeGestureCount: Int64,
    _ todayGestureCount: Int32,
    _ activeInteractionSeconds: Float,
    _ lifetimeOfflineExperience: Float,
    _ unlockedAchievementCount: Int32,
    _ totalAchievementCount: Int32,
    _ achievementCatalog: UnsafePointer<CChar>?,
    _ threeBladeMetalSkinCatalog: UnsafePointer<CChar>?,
    _ equippedThreeBladeMetalSkinId: UnsafePointer<CChar>?,
    _ productStickerCatalog: UnsafePointer<CChar>?,
    _ equippedProductStickerId: UnsafePointer<CChar>?) {
    let modelRawValue = modelId.map { String(cString: $0) } ?? "pointed-three-blade"
    let model = SpinnerModel(rawValue: modelRawValue) ?? .pointedThreeBlade
    let offlineModelRawValue = offlineModelId.map { String(cString: $0) }
        ?? modelRawValue
    let offlineModel = SpinnerModel(rawValue: offlineModelRawValue) ?? model
    let resolvedStageName = stageName.map { String(cString: $0) } ?? "初始装配"
    let resolvedStageComponent = stageComponent.map { String(cString: $0) }
        ?? "标准单列轴承"
    let resolvedStageMaterial = stageMaterial.map { String(cString: $0) }
        ?? "基础合金"
    let resolvedLevelTitle = levelTitle.map { String(cString: $0) }
        ?? "初转学徒"
    let resolvedLevelCatalog = ProgressionLevelDetail.parse(
        levelCatalog.map { String(cString: $0) } ?? "")
    let resolvedNextUnlock = nextUnlockName.map { String(cString: $0) }
        ?? "已完成全部升级"
    let offlineReward: OfflineProgressionReward? = offlineExperience >= 1
        ? OfflineProgressionReward(
            model: offlineModel,
            experience: Double(offlineExperience),
            elapsedHours: Double(offlineHours),
            previousLevel: Int(previousLevel),
            newLevel: Int(offlineNewLevel),
            previousLevelProgress: Double(offlinePreviousLevelProgress),
            newLevelProgress: Double(offlineNewLevelProgress),
            assistantEnabled: offlineAssistantEnabled != 0)
        : nil
    let resolvedLiveReward = liveRewardName.map { String(cString: $0) }
        ?? "成长罐容量提升"
    let liveLevelUp: LiveProgressionLevelUp? = livePreviousLevel > 0
        && level > livePreviousLevel
        ? LiveProgressionLevelUp(
            previousLevel: Int(livePreviousLevel),
            newLevel: Int(level),
            rewardName: resolvedLiveReward)
        : nil
    let resolvedAchievementPayload = achievementCatalog.map {
        String(cString: $0)
    } ?? ""
    let resolvedBadgeEnvelope = ProductBadgeDetail.parseEnvelope(
        resolvedAchievementPayload)
    let resolvedBadges = resolvedBadgeEnvelope?.badges ?? []
    let resolvedThreeBladeMetalSkins = ThreeBladeMetalSkinDetail.parse(
        threeBladeMetalSkinCatalog.map { String(cString: $0) } ?? "")
    let resolvedEquippedThreeBladeMetalSkinId = equippedThreeBladeMetalSkinId.map {
        String(cString: $0)
    } ?? ""
    let resolvedProductStickers = ProductStickerDetail.parse(
        productStickerCatalog.map { String(cString: $0) } ?? "")
    let resolvedEquippedProductStickerId = equippedProductStickerId.map {
        String(cString: $0)
    } ?? ""

    Task { @MainActor in
        let manager = CodexSwiftUIOverlayManager.shared
        manager.state.updateProgression(
            model: model,
            level: Int(level),
            totalExperience: Double(totalExperience),
            levelStartExperience: Double(levelStartExperience),
            nextLevelExperience: Double(nextLevelExperience),
            fraction: Double(levelProgress),
            stageName: resolvedStageName,
            stageComponent: resolvedStageComponent,
            stageMaterial: resolvedStageMaterial,
            levelTitle: resolvedLevelTitle,
            levelCatalog: resolvedLevelCatalog,
            nextUnlockLevel: Int(nextUnlockLevel),
            nextUnlockName: resolvedNextUnlock,
            assistantEnabled: assistantEnabled != 0,
            assistantMultiplier: Double(assistantSpeedMultiplier),
            peakRimSpeedKmh: Double(peakRimSpeedKmh),
            lifetimeGestures: lifetimeGestureCount,
            todayGestures: Int(todayGestureCount),
            activeInteractionSeconds: Double(activeInteractionSeconds),
            lifetimeOfflineExperience: Double(lifetimeOfflineExperience),
            badges: resolvedBadges,
            shardBalance: resolvedBadgeEnvelope?.shardBalance ?? 0,
            threeBladeMetalSkins: resolvedThreeBladeMetalSkins,
            equippedThreeBladeMetalSkinId: resolvedEquippedThreeBladeMetalSkinId,
            productStickers: resolvedProductStickers,
            equippedProductStickerId: resolvedEquippedProductStickerId,
            offlineReward: offlineReward,
            liveLevelUp: liveLevelUp)
        manager.presentProgressionRewardIfNeeded()
    }
}

@_cdecl("CodexCollectorReceiveState")
public func CodexCollectorReceiveState(
    _ rank: Int32,
    _ totalExperience: Float,
    _ rankStartExperience: Float,
    _ nextRankExperience: Float,
    _ rankProgress: Float,
    _ focusModelId: UnsafePointer<CChar>?,
    _ canChangeFocus: Int32,
    _ globalActiveBonus: Float,
    _ focusActiveBonus: Float,
    _ validDaysInWindow: Int32,
    _ completedRhythmWeeks: Int32,
    _ discoveredModelCount: Int32,
    _ collectedCosmeticCount: Int32,
    _ unlockedAchievementCount: Int32,
    _ totalAchievementCount: Int32,
    _ discoveredModelPayload: UnsafePointer<CChar>?,
    _ achievementCatalogPayload: UnsafePointer<CChar>?,
    _ previousRank: Int32) {
    let focusRawValue = focusModelId.map { String(cString: $0) } ?? "pointed-three-blade"
    let focusModel = SpinnerModel(rawValue: focusRawValue) ?? .pointedThreeBlade
    let discoveredPayload = discoveredModelPayload.map { String(cString: $0) } ?? ""
    let discoveredIds = Set(discoveredPayload.split(separator: "|").map(String.init))
    let resolvedAchievementPayload = achievementCatalogPayload.map {
        String(cString: $0)
    } ?? ""
    let badgeEnvelope = ProductBadgeDetail.parseEnvelope(resolvedAchievementPayload)
    let badges = badgeEnvelope?.badges ?? []

    Task { @MainActor in
        CodexSwiftUIOverlayManager.shared.state.updateCollector(
            rank: Int(rank),
            totalExperience: Double(totalExperience),
            rankStartExperience: Double(rankStartExperience),
            nextRankExperience: Double(nextRankExperience),
            fraction: Double(rankProgress),
            focusModel: focusModel,
            canChangeFocus: canChangeFocus != 0,
            globalBonus: Double(globalActiveBonus),
            focusBonus: Double(focusActiveBonus),
            validDays: Int(validDaysInWindow),
            completedWeeks: Int(completedRhythmWeeks),
            discoveredModelCount: Int(discoveredModelCount),
            cosmeticCount: Int(collectedCosmeticCount),
            discoveredModelIds: discoveredIds,
            badges: badges,
            shardBalance: badgeEnvelope?.shardBalance ?? 0,
            previousRank: Int(previousRank))
    }
}

@_cdecl("CodexComboReceiveState")
public func CodexComboReceiveState(
    _ tier: Int32,
    _ count: Int32,
    _ title: UnsafePointer<CChar>?,
    _ normalizedSpeed: Float,
    _ angularSpeedRadians: Float,
    _ normalizedIntensity: Float,
    _ normalizedFrequency: Float,
    _ experienceMultiplier: Float) {
    let snapshot = ProgressionComboState(
        tier: Int(tier),
        count: Int(count),
        title: title.map { String(cString: $0) } ?? "",
        speed: Double(normalizedSpeed),
        angularSpeedRadians: Double(angularSpeedRadians),
        intensity: Double(normalizedIntensity),
        frequency: Double(normalizedFrequency),
        experienceMultiplier: Double(experienceMultiplier))
    Task { @MainActor in
        CodexSwiftUIOverlayManager.shared.state.updateProgressionCombo(snapshot)
    }
}

@_cdecl("CodexComboHaloReceiveProjection")
public func CodexComboHaloReceiveProjection(
    _ available: Int32,
    _ centerX: Float,
    _ centerY: Float,
    _ rotationDegrees: Float,
    _ minorAxisRatio: Float) {
    let projection = ComboHaloProjectionState(
        available: available != 0,
        centerX: Double(centerX),
        centerY: Double(centerY),
        rotationDegrees: Double(rotationDegrees),
        minorAxisRatio: Double(minorAxisRatio)).clamped()
    Task { @MainActor in
        CodexSwiftUIOverlayManager.shared.state.updateComboHaloProjection(
            projection)
    }
}

@_cdecl("CodexMotionTelemetryReceiveState")
public func CodexMotionTelemetryReceiveState(
    _ available: Int32,
    _ kind: Int32,
    _ normalizedSpeed: Float,
    _ motionRate: Float,
    _ speedBand: Int32,
    _ normalizedIntensity: Float,
    _ normalizedFrequency: Float) {
    let resolvedKind = ProductMotionKind(rawValue: Int(kind)) ?? .rotary
    let liveMotionRate = max(0, Double(motionRate))
    let telemetry = ProductMotionTelemetryState(
        available: available != 0,
        kind: resolvedKind,
        normalizedSpeed: min(1, max(0, Double(normalizedSpeed))),
        angularSpeedRadians: resolvedKind == .rotary ? liveMotionRate : 0,
        motionRate: liveMotionRate,
        speedBand: ProductSpeedBand(rawValue: Int(speedBand)) ?? .calm,
        intensity: min(1, max(0, Double(normalizedIntensity))),
        frequency: min(1, max(0, Double(normalizedFrequency))))
    Task { @MainActor in
        CodexSwiftUIOverlayManager.shared.state.updateMotionTelemetry(telemetry)
    }
}

@_cdecl("CodexSpinRewardReceiveState")
public func CodexSpinRewardReceiveState(
    _ kind: Int32,
    _ title: UnsafePointer<CChar>?,
    _ subtitle: UnsafePointer<CChar>?,
    _ normalizedForce: Float,
    _ peakAngularSpeedRadians: Float,
    _ revolutions: Float) {
    if kind <= 0 {
        Task { @MainActor in
            CodexSwiftUIOverlayManager.shared.state.dismissSpinReward()
        }
        return
    }

    let reward = SpinRewardState(
        kind: Int(kind),
        title: title.map { String(cString: $0) } ?? "PERFECT SPIN",
        subtitle: subtitle.map { String(cString: $0) } ?? "力度 × 速度 × 圈数",
        force: Double(normalizedForce),
        peakAngularSpeedRadians: Double(peakAngularSpeedRadians),
        revolutions: Double(revolutions))
    Task { @MainActor in
        CodexSwiftUIOverlayManager.shared.state.presentSpinReward(reward)
    }
}
