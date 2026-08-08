import Foundation
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
        .magneticSlideTile
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
        payload.split(separator: "\n").compactMap { row in
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
        payload.split(separator: "\n").compactMap { row in
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

private enum ProgressionAchievementMetric: String, CaseIterable, Equatable {
    case peakRimSpeedKmh = "PeakRimSpeedKmh"
    case lifetimeGestures = "LifetimeGestures"
    case activeInteractionSeconds = "ActiveInteractionSeconds"
    case lifetimeOfflineExperience = "LifetimeOfflineExperience"

    var title: String {
        switch self {
        case .peakRimSpeedKmh: return "最高速度"
        case .lifetimeGestures: return "累计滑动"
        case .activeInteractionSeconds: return "实际交互"
        case .lifetimeOfflineExperience: return "离线经验"
        }
    }

    var symbol: String {
        switch self {
        case .peakRimSpeedKmh: return "speedometer"
        case .lifetimeGestures: return "hand.draw.fill"
        case .activeInteractionSeconds: return "timer"
        case .lifetimeOfflineExperience: return "moon.stars.fill"
        }
    }

    var accent: Color {
        switch self {
        case .peakRimSpeedKmh: return .cyan
        case .lifetimeGestures: return .orange
        case .activeInteractionSeconds: return .green
        case .lifetimeOfflineExperience: return .purple
        }
    }
}

private struct ProgressionAchievementDetail: Identifiable, Equatable {
    let id: String
    let metric: ProgressionAchievementMetric
    let threshold: Double
    let title: String
    let unlocked: Bool

    var milestoneText: String {
        switch metric {
        case .peakRimSpeedKmh:
            return String(format: "%.1f km/h", threshold)
        case .lifetimeGestures:
            return threshold >= 1000
                ? String(format: threshold >= 10000 ? "%.0fK 次滑动" : "%.1fK 次滑动", threshold / 1000)
                : String(format: "%.0f 次滑动", threshold)
        case .activeInteractionSeconds:
            return threshold >= 3600
                ? String(format: "%.0f 小时交互", threshold / 3600)
                : String(format: "%.0f 分钟交互", threshold / 60)
        case .lifetimeOfflineExperience:
            return threshold >= 1000
                ? String(format: threshold >= 10000 ? "%.0fK 离线 XP" : "%.1fK 离线 XP", threshold / 1000)
                : String(format: "%.0f 离线 XP", threshold)
        }
    }

    static func parse(_ payload: String) -> [ProgressionAchievementDetail] {
        payload.split(separator: "\n").compactMap { row in
            let fields = row.split(separator: "\t", omittingEmptySubsequences: false)
            guard fields.count >= 4,
                  let metric = ProgressionAchievementMetric(rawValue: String(fields[1])),
                  let threshold = Double(fields[2]) else { return nil }
            return ProgressionAchievementDetail(
                id: String(fields[0]),
                metric: metric,
                threshold: threshold,
                title: String(fields[3]),
                unlocked: fields.count >= 5 && fields[4] == "1")
        }
    }
}

private enum CollectorAchievementMetric: String, Equatable {
    case completedRhythmWeeks = "CompletedRhythmWeeks"
    case discoveredModels = "DiscoveredModels"
    case toyLevel20Count = "ToyLevel20Count"
    case toyLevel100Count = "ToyLevel100Count"
    case collectedCosmetics = "CollectedCosmetics"

    var title: String {
        switch self {
        case .completedRhythmWeeks: return "节奏"
        case .discoveredModels: return "探索"
        case .toyLevel20Count, .toyLevel100Count: return "精通"
        case .collectedCosmetics: return "收藏"
        }
    }

    var symbol: String {
        switch self {
        case .completedRhythmWeeks: return "calendar.badge.checkmark"
        case .discoveredModels: return "square.grid.2x2"
        case .toyLevel20Count: return "dial.medium"
        case .toyLevel100Count: return "seal.fill"
        case .collectedCosmetics: return "circle.hexagongrid.fill"
        }
    }
}

private struct CollectorAchievementDetail: Identifiable, Equatable {
    let id: String
    let metric: CollectorAchievementMetric
    let threshold: Int
    let title: String
    let unlocked: Bool

    static func parse(_ payload: String) -> [CollectorAchievementDetail] {
        payload.split(separator: "\n").compactMap { row in
            let fields = row.split(separator: "\t", omittingEmptySubsequences: false)
            guard fields.count >= 5,
                  let metric = CollectorAchievementMetric(rawValue: String(fields[1])),
                  let threshold = Int(fields[2]) else { return nil }
            return CollectorAchievementDetail(
                id: String(fields[0]),
                metric: metric,
                threshold: threshold,
                title: String(fields[3]),
                unlocked: fields[4] == "1")
        }
    }
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

private struct ProductMotionTelemetryState: Equatable {
    var available = false
    var normalizedSpeed = 0.0
    var angularSpeedRadians = 0.0
    var speedBand = ProductSpeedBand.calm

    var rpm: Double {
        abs(angularSpeedRadians) * 60.0 / (2.0 * .pi)
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
    }

    @Published var selectedTab: ProductTab = .spinners
    @Published var isLibraryVisible = true
    @Published var selectedModel: SpinnerModel
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
    @Published var progressionUnlockedAchievementCount = 0
    @Published var progressionTotalAchievementCount = 0
    @Published var progressionAchievements: [ProgressionAchievementDetail] = []
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
    @Published var collectorUnlockedAchievementCount = 0
    @Published var collectorTotalAchievementCount = 0
    @Published var collectorDiscoveredModelIds: Set<String> = []
    @Published var collectorAchievements: [CollectorAchievementDetail] = []
    @Published var collectorUnlockNotice: CollectorAchievementDetail?
    @Published var showingCollectorUnlockNotice = false
    @Published var collectorRankUp = CollectorRankUp()
    @Published var showingCollectorRankUp = false
    @Published var badgeUnlockNotice: ProgressionAchievementDetail?
    @Published var showingBadgeUnlockNotice = false
    @Published var showingSpinnerOnboarding = false
    @Published var offlineProgressionReward = OfflineProgressionReward()
    @Published var showingOfflineProgressionReward = false
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
    private var spinRewardDismissWorkItem: DispatchWorkItem?
    private var badgeUnlockDismissWorkItem: DispatchWorkItem?
    private var collectorUnlockDismissWorkItem: DispatchWorkItem?
    private var pendingBadgeUnlocks: [ProgressionAchievementDetail] = []
    private var pendingCollectorUnlocks: [CollectorAchievementDetail] = []
    private var seenBadgeIdsByModel: [String: Set<String>] = [:]
    private var seenCollectorAchievementIds: Set<String>?

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
        selectedModel = model
        UserDefaults.standard.set(model.rawValue, forKey: Key.selectedModel)
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
        UnityBridge.send("SetDetentFeelPresetFromNativeUi", value: String(index))
    }

    func setDetentIntensityOverride(_ value: Double) {
        detentTuningIntensity = min(1, max(0, value))
        UnityBridge.send(
            "SetDetentIntensityOverrideFromNativeUi",
            value: String(detentTuningIntensity))
    }

    func setDetentSharpnessOverride(_ value: Double) {
        detentTuningSharpness = min(1, max(0, value))
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
        unlockedAchievementCount: Int,
        totalAchievementCount: Int,
        discoveredModelIds: Set<String>,
        achievements: [CollectorAchievementDetail],
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
        collectorUnlockedAchievementCount = max(0, unlockedAchievementCount)
        collectorTotalAchievementCount = max(0, totalAchievementCount)
        collectorDiscoveredModelIds = discoveredModelIds
        detectNewCollectorUnlocks(achievements)
        collectorAchievements = achievements

        if previousRank > 0 && collectorRank > previousRank {
            collectorRankUp = CollectorRankUp(
                previousRank: previousRank,
                newRank: collectorRank)
            showingCollectorRankUp = true
        }
    }

    private func detectNewCollectorUnlocks(_ achievements: [CollectorAchievementDetail]) {
        let storageKey = "fidgeting.collector.seenAchievements.v1"
        let unlocked = Set(achievements.filter(\.unlocked).map(\.id))
        if seenCollectorAchievementIds == nil {
            let defaults = UserDefaults.standard
            if defaults.object(forKey: storageKey) == nil {
                seenCollectorAchievementIds = unlocked
                defaults.set(Array(unlocked).sorted(), forKey: storageKey)
                return
            }
            seenCollectorAchievementIds = Set(
                defaults.stringArray(forKey: storageKey) ?? [])
        }

        let seen = seenCollectorAchievementIds ?? []
        let newlyUnlocked = achievements.filter {
            $0.unlocked && !seen.contains($0.id)
        }
        seenCollectorAchievementIds = unlocked
        UserDefaults.standard.set(Array(unlocked).sorted(), forKey: storageKey)
        enqueueCollectorUnlocks(newlyUnlocked)
    }

    private func enqueueCollectorUnlocks(_ achievements: [CollectorAchievementDetail]) {
        let existingIds = Set(
            pendingCollectorUnlocks.map(\.id)
                + [collectorUnlockNotice?.id].compactMap { $0 })
        pendingCollectorUnlocks.append(contentsOf: achievements.filter {
            !existingIds.contains($0.id)
        })
        guard !showingCollectorUnlockNotice else { return }
        presentNextCollectorUnlock()
    }

    private func presentNextCollectorUnlock() {
        collectorUnlockDismissWorkItem?.cancel()
        guard !pendingCollectorUnlocks.isEmpty else {
            collectorUnlockNotice = nil
            showingCollectorUnlockNotice = false
            return
        }

        collectorUnlockNotice = pendingCollectorUnlocks.removeFirst()
        withAnimation(.spring(response: 0.38, dampingFraction: 0.76)) {
            showingCollectorUnlockNotice = true
        }
        let dismiss = DispatchWorkItem { [weak self] in
            guard let self else { return }
            withAnimation(.easeOut(duration: 0.28)) {
                self.showingCollectorUnlockNotice = false
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.34) { [weak self] in
                self?.presentNextCollectorUnlock()
            }
        }
        collectorUnlockDismissWorkItem = dismiss
        DispatchQueue.main.asyncAfter(deadline: .now() + 3.2, execute: dismiss)
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
        unlockedAchievementCount: Int,
        totalAchievementCount: Int,
        achievements: [ProgressionAchievementDetail],
        threeBladeMetalSkins: [ThreeBladeMetalSkinDetail],
        equippedThreeBladeMetalSkinId: String,
        productStickers: [ProductStickerDetail],
        equippedProductStickerId: String,
        offlineReward: OfflineProgressionReward?,
        liveLevelUp: LiveProgressionLevelUp?) {
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
        progressionUnlockedAchievementCount = max(0, unlockedAchievementCount)
        progressionTotalAchievementCount = max(0, totalAchievementCount)
        detectNewBadgeUnlocks(model: model, achievements: achievements)
        progressionAchievements = achievements
        self.threeBladeMetalSkins = threeBladeMetalSkins
        self.equippedThreeBladeMetalSkinId = equippedThreeBladeMetalSkinId
        self.productStickers = productStickers
        self.equippedProductStickerId = equippedProductStickerId

        if let offlineReward, offlineReward.experience >= 1 {
            offlineProgressionReward = offlineReward
            showingOfflineProgressionReward = true
        }
        if let liveLevelUp, liveLevelUp.newLevel > liveLevelUp.previousLevel {
            liveProgressionLevelUp = liveLevelUp
            showingLiveProgressionLevelUp = true
        }
    }

    private func detectNewBadgeUnlocks(
        model: SpinnerModel,
        achievements: [ProgressionAchievementDetail]) {
        let modelId = model.rawValue
        let storageKey = "fidgeting.progression.seenBadges.v1.\(modelId)"
        let unlocked = Set(achievements.filter(\.unlocked).map(\.id))

        if seenBadgeIdsByModel[modelId] == nil {
            let defaults = UserDefaults.standard
            if defaults.object(forKey: storageKey) == nil {
                seenBadgeIdsByModel[modelId] = unlocked
                defaults.set(Array(unlocked).sorted(), forKey: storageKey)
                return
            }
            seenBadgeIdsByModel[modelId] = Set(
                defaults.stringArray(forKey: storageKey) ?? [])
        }

        let seen = seenBadgeIdsByModel[modelId] ?? []
        let newlyUnlocked = achievements.filter {
            $0.unlocked && !seen.contains($0.id)
        }
        seenBadgeIdsByModel[modelId] = unlocked
        UserDefaults.standard.set(Array(unlocked).sorted(), forKey: storageKey)
        enqueueBadgeUnlocks(newlyUnlocked)
    }

    private func enqueueBadgeUnlocks(_ badges: [ProgressionAchievementDetail]) {
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

private struct ProductTopBar: View {
    @ObservedObject var state: ProductUiState

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

    private var offlineRewardMessage: String {
        let reward = state.offlineProgressionReward
        let source = reward.assistantEnabled ? "代盘秘书" : "陀螺"
        let levelText = reward.newLevel > reward.previousLevel
            ? "\nLv.\(reward.previousLevel) → Lv.\(reward.newLevel)"
            : ""
        return String(
            format: "%@在你离开时继续运转了 %.1f 小时，为 %@ 收集了 %.0f 成长值。%@",
            source,
            reward.elapsedHours,
            reward.model.title,
            reward.experience,
            levelText)
    }

    var body: some View {
        VStack {
            Spacer(minLength: 0)
            ZStack {
                if showsProductIdentity {
                    VStack(spacing: 1) {
                        Text("LV \(state.displayedProgressionLevel)")
                            .font(.product(size: 9, weight: .semibold))
                            .monospacedDigit()
                            .foregroundStyle(Color.white.opacity(0.42))
                        Text(state.selectedModel.title)
                            .font(.product(.headline, weight: .semibold))
                            .foregroundStyle(Color.white.opacity(0.92))
                        Text(state.currentAppearanceName)
                            .font(.product(size: 10, weight: .medium))
                            .foregroundStyle(state.currentAppearanceAccent.opacity(0.78))
                            .lineLimit(1)
                            .minimumScaleFactor(0.74)
                    }
                    .frame(maxWidth: 170)
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(
                        "等级 \(state.displayedProgressionLevel)，\(state.selectedModel.title)，当前皮肤 \(state.currentAppearanceName)")
                } else {
                    Text(pageTitle)
                        .font(.product(.headline, weight: .semibold))
                        .foregroundStyle(Color.white.opacity(0.86))
                }

                HStack {
                    if showsBackButton {
                        ProductIconButton(
                            symbol: "chevron.left",
                            accessibilityLabel: "返回",
                            accent: state.currentAppearanceAccent) {
                            UnityBridge.feedback()
                            CodexSwiftUIOverlayManager.shared.showMySpinners()
                        }
                    } else {
                        topDestinationButton(
                            .collector,
                            label: "藏家档案",
                            symbol: "person.crop.circle")
                    }

                    Spacer()

                    HStack(spacing: 6) {
                        topDestinationButton(
                            .settings,
                            label: "设置",
                            symbol: "gearshape")
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
        .alert("离线收获", isPresented: $state.showingOfflineProgressionReward) {
            Button("收下", role: .cancel) {
                UnityBridge.feedback(.medium)
            }
        } message: {
            Text(offlineRewardMessage)
        }
        .alert(
            "LEVEL UP · LV.\(state.liveProgressionLevelUp.newLevel)",
            isPresented: $state.showingLiveProgressionLevelUp) {
            Button("继续转", role: .cancel) {
                UnityBridge.feedback(.heavy)
            }
        } message: {
            Text("成长罐已装满。获得：\(state.liveProgressionLevelUp.rewardName)")
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

                Button {
                    UnityBridge.feedback(.medium)
                    if page < 2 {
                        withAnimation(.easeOut(duration: 0.24)) { page += 1 }
                    } else {
                        state.completeSpinnerOnboarding()
                    }
                } label: {
                    ProductPrimaryActionLabel(
                        title: page < 2 ? "下一步" : "开始玩",
                        symbol: page < 2 ? "arrow.right" : "hand.draw.fill",
                        accent: accent)
                }
                .buttonStyle(.plain)
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
                        value: String(format: "%.0f", combo.intensity * 100),
                        unit: "%",
                        fraction: combo.intensity,
                        accent: telemetry.speedBand.accent,
                        accessibilityLabel: "操作强度",
                        accessibilityValue: String(
                            format: "%.0f%%",
                            combo.intensity * 100))
                        .frame(width: sideWidth)

                    ProductSpeedDashboard(
                        title: "SPEED",
                        value: String(format: "%.0f", telemetry.rpm),
                        unit: "RPM",
                        fraction: telemetry.normalizedSpeed,
                        accent: telemetry.speedBand.accent,
                        isPeak: telemetry.speedBand == .peak,
                        stateLabel: telemetry.speedBand.title,
                        accessibilityLabel: "转速",
                        accessibilityValue: String(
                            format: "%.0f RPM，%@",
                            telemetry.rpm,
                            telemetry.speedBand.title))
                        .frame(width: mainWidth)

                    ProductSideMetricDashboard(
                        title: "FREQUENCY",
                        value: String(format: "%.0f", combo.frequency * 100),
                        unit: "%",
                        fraction: combo.frequency,
                        accent: telemetry.speedBand.accent,
                        accessibilityLabel: "操作频率",
                        accessibilityValue: String(
                            format: "%.0f%%",
                            combo.frequency * 100))
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
                    projection: state.comboHaloProjection)

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

    var body: some View {
        GeometryReader { proxy in
            VStack {
                if state.showingBadgeUnlockNotice,
                   let badge = state.badgeUnlockNotice {
                    ProductNoticeBanner(
                        kicker: "BADGE UNLOCKED",
                        title: badge.title,
                        detail: "\(badge.milestoneText) · 已加入 Badge 图鉴",
                        symbol: "star.fill",
                        accent: badge.metric.accent,
                        accessibilityLabel: "Badge 解锁，\(badge.title)，\(badge.milestoneText)")
                    .transition(.move(edge: .top).combined(with: .opacity))
                }
                Spacer()
            }
            .frame(maxWidth: .infinity)
            .padding(.horizontal, 16)
            .padding(.top, max(166, proxy.safeAreaInsets.top + 112))
            .animation(
                .spring(response: 0.38, dampingFraction: 0.76),
                value: state.showingBadgeUnlockNotice)
        }
        .ignoresSafeArea()
        .productDesignSystem()
        .preferredColorScheme(.dark)
    }
}

private struct CollectorUnlockOverlay: View {
    @ObservedObject var state: ProductUiState

    var body: some View {
        GeometryReader { proxy in
            VStack {
                if state.showingCollectorUnlockNotice,
                   let achievement = state.collectorUnlockNotice {
                    ProductNoticeBanner(
                        kicker: "藏家成就解锁",
                        title: achievement.title,
                        detail: "\(achievement.metric.title) · 已加入藏家档案",
                        symbol: "trophy.fill",
                        accent: Color.white.opacity(0.82),
                        accessibilityLabel: "藏家成就解锁，\(achievement.title)")
                    .transition(.move(edge: .top).combined(with: .opacity))
                }
                Spacer()
            }
            .frame(maxWidth: .infinity)
            .padding(.horizontal, 16)
            .padding(.top, max(238, proxy.safeAreaInsets.top + 184))
            .animation(
                .spring(response: 0.38, dampingFraction: 0.76),
                value: state.showingCollectorUnlockNotice)
        }
        .ignoresSafeArea()
        .productDesignSystem()
        .preferredColorScheme(.dark)
    }
}

private struct SpinnerProgressionHUD: View {
    @ObservedObject var state: ProductUiState
    @State private var showingLevelDetails = false

    private var accent: Color { state.currentAppearanceAccent }
    private let autoMultipliers = [1.0, 1.5, 2.0, 3.0]

    private var autoMultiplierText: String {
        String(format: "%.1fx", state.progressionAssistantMultiplier)
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
        ZStack(alignment: .leading) {
            Button {
                UnityBridge.feedback()
                showingLevelDetails = true
            } label: {
                HStack(spacing: 10) {
                    Color.clear
                        .frame(width: 68, height: 68)

                    VStack(alignment: .leading, spacing: 5) {
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

                        ProgressionMilestoneGauge(
                            previousLevel: previousMilestoneLevel,
                            currentLevel: state.progressionLevel,
                            nextLevel: nextMilestoneLevel,
                            progress: milestoneProgress,
                            accent: accent)

                        Text(experienceText)
                            .font(.product(.caption2).monospacedDigit())
                            .foregroundStyle(Color.white.opacity(0.58))
                    }

                    VStack(spacing: 1) {
                        ProgressionUnlockThumbnail(
                            model: state.selectedModel,
                            skin: nextPreviewSkin,
                            accent: accent,
                            unlocked: true,
                            showsLock: state.progressionLevel < 100,
                            shimmers: true)
                            .frame(width: 48, height: 48)

                        Text(state.progressionLevel >= 100
                             ? "MAX"
                             : "LV.\(state.progressionNextUnlockLevel)")
                            .font(.product(size: 8, weight: .black))
                            .monospacedDigit()
                            .foregroundStyle(accent.opacity(0.78))
                    }
                    .frame(width: 58)
                }
                .padding(.horizontal, 13)
                .padding(.vertical, 10)
                .frame(maxWidth: .infinity, alignment: .leading)
                .contentShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            }
            .buttonStyle(.plain)
            .frame(maxWidth: .infinity)
            .accessibilityLabel("成长详情，等级 \(state.progressionLevel)")
            .accessibilityHint("打开成长详情")

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
                VStack(spacing: 6) {
                    AutoSpeedRotorBadge(
                        multiplierText: autoMultiplierText,
                        angularSpeedRadians: state.motionTelemetry.angularSpeedRadians,
                        active: state.progressionAssistantEnabled,
                        accent: accent)
                        .frame(width: 36, height: 36)
                    Text("AUTO")
                        .font(.product(.caption2, weight: .semibold))
                }
                .foregroundStyle(state.progressionAssistantEnabled
                                 ? accent.opacity(0.84)
                                 : Color.white.opacity(0.72))
                .padding(.horizontal, 14)
                .padding(.vertical, 7)
                .background(
                    Color.white.opacity(state.progressionAssistantEnabled ? 0.10 : 0.04),
                    in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            }
            .accessibilityLabel("AUTO 菜单")
            .accessibilityValue(
                state.progressionAssistantEnabled
                    ? "已开启，\(autoMultiplierText)"
                    : "已关闭")
            .accessibilityHint("打开向上的倍率选择菜单")
            .padding(.leading, 13)
        }
        .productGlass(
            cornerRadius: 22,
            tint: accent.opacity(state.progressionCombo.isActive ? 0.075 : 0.035),
            interactive: true)
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .sheet(isPresented: $showingLevelDetails) {
            ProgressionLevelDetailsSheet(state: state)
        }
    }
}

private struct ProgressionMilestoneGauge: View {
    let previousLevel: Int
    let currentLevel: Int
    let nextLevel: Int
    let progress: Double
    let accent: Color

    private var clampedProgress: Double {
        min(1, max(0, progress))
    }

    var body: some View {
        GeometryReader { proxy in
            let width = max(1, proxy.size.width)
            let markerX = width * CGFloat(clampedProgress)
            let labelX = min(width - 25, max(25, markerX))

            ZStack(alignment: .topLeading) {
                Text("\(previousLevel)")
                    .font(.product(size: 7, weight: .bold).monospacedDigit())
                    .foregroundStyle(Color.white.opacity(0.44))
                    .position(x: 8, y: 5)

                Text("LV.\(currentLevel)")
                    .font(.product(size: 8, weight: .black).monospacedDigit())
                    .foregroundStyle(.white)
                    .padding(.horizontal, 4)
                    .padding(.vertical, 1)
                    .background(accent.opacity(0.22), in: Capsule())
                    .position(x: labelX, y: 5)

                Text("\(nextLevel)")
                    .font(.product(size: 7, weight: .bold).monospacedDigit())
                    .foregroundStyle(Color.white.opacity(0.58))
                    .position(x: width - 8, y: 5)

                ProductProgressGauge(value: clampedProgress, accent: accent)
                    .frame(height: 5)
                    .position(x: width / 2, y: 18)

                Circle()
                    .fill(Color.white)
                    .frame(width: 7, height: 7)
                    .overlay(Circle().stroke(accent.opacity(0.72), lineWidth: 2))
                    .shadow(color: accent.opacity(0.46), radius: 4)
                    .position(x: markerX, y: 18)
            }
        }
        .frame(height: 23)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("成长里程碑")
        .accessibilityValue(
            "上一级 \(previousLevel)，当前 \(currentLevel)，下一级 \(nextLevel)")
    }
}

private final class AutoSpeedRotorAnimator: NSObject, ObservableObject {
    @Published private(set) var rotationDegrees = 0.0

    private var angularSpeedRadians = 0.0
    private var displayLink: CADisplayLink?
    private var previousTimestamp: CFTimeInterval = 0

    func update(angularSpeedRadians: Double, paused: Bool) {
        self.angularSpeedRadians = max(0, angularSpeedRadians)
        guard !paused, self.angularSpeedRadians > 0.01 else {
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
        active ? accent.opacity(0.90) : Color.white.opacity(0.62)
    }

    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.white.opacity(0.12), lineWidth: 1)

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
                        .offset(y: -15)
                        .rotationEffect(.degrees(Double(index) * 90))
                }
            }
            .rotationEffect(.degrees(animator.rotationDegrees))

            Text(multiplierText)
                .font(.product(size: 9, weight: .black).monospacedDigit())
                .foregroundStyle(Color.white.opacity(0.88))
        }
        .onAppear {
            updateAnimator()
        }
        .onChange(of: angularSpeedRadians) { _ in
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
        .animation(
            .linear(duration: 2.6).repeatForever(autoreverses: false),
            value: shimmerAtRight)
        .accessibilityHidden(true)
    }
}

private struct ProgressionLevelDetailsSheet: View {
    @ObservedObject var state: ProductUiState
    @State private var selectedSection = 0

    var body: some View {
        ProductBottomSheetShell(title: "成长图鉴") {
            VStack(spacing: 0) {
                Picker("成长栏目", selection: $selectedSection) {
                    Text("成就").tag(0)
                    Text("Badge").tag(1)
                    Text("外观").tag(2)
                }
                .pickerStyle(.segmented)
                .padding(.horizontal, 18)
                .padding(.vertical, 12)

                switch selectedSection {
                case 0:
                    ProgressionLevelTimeline(state: state)
                case 1:
                    ProgressionBadgeAchievements(state: state)
                default:
                    ProgressionCosmeticsCatalog(state: state)
                }
            }
        }
    }
}

private struct ProgressionLevelTimeline: View {
    @ObservedObject var state: ProductUiState
    private var accent: Color { state.currentAppearanceAccent }

    private func unlockSkin(for level: Int) -> ThreeBladeMetalSkinDetail? {
        guard state.selectedModel == .metalThreeBlade,
              state.progressionModel == .metalThreeBlade else { return nil }
        return state.threeBladeMetalSkins.first { $0.level == level }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("LV.\(state.progressionLevel) · \(state.progressionLevelTitle)")
                            .font(.product(.title2, weight: .bold).monospacedDigit())
                    }
                    Spacer()
                    Text("\(state.progressionLevel)%")
                        .font(.product(.headline, weight: .black).monospacedDigit())
                        .foregroundStyle(accent)
                }
                .padding(16)
                .productGlass(cornerRadius: 22, tint: accent.opacity(0.08))

                HStack(alignment: .top, spacing: 10) {
                    ProgressionVerticalRail(
                        progress: Double(state.progressionLevel) / 100.0,
                        accent: accent)
                        .frame(width: 24)

                    VStack(spacing: 12) {
                        ProgressionLevelRow(
                            levelLabel: "LV.0",
                            title: "START",
                            unlockName: "选择玩具并开始第一次滑动",
                            level: 0,
                            model: state.selectedModel,
                            skin: nil,
                            unlocked: true,
                            current: state.progressionLevel == 0,
                            accent: accent)

                        ForEach(Array(state.progressionLevelCatalog.enumerated()), id: \.element.id) { index, detail in
                            let nextLevel = index + 1 < state.progressionLevelCatalog.count
                                ? state.progressionLevelCatalog[index + 1].level - 1
                                : detail.level
                            ProgressionLevelRow(
                                levelLabel: detail.level == nextLevel
                                    ? "LV.\(detail.level)"
                                    : "LV.\(detail.level)–\(nextLevel)",
                                title: detail.title,
                                unlockName: detail.unlockName,
                                level: detail.level,
                                model: state.selectedModel,
                                skin: unlockSkin(for: detail.level),
                                unlocked: state.progressionLevel >= detail.level,
                                current: state.progressionLevel >= detail.level
                                    && state.progressionLevel <= nextLevel,
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

private struct ProgressionCosmeticsCatalog: View {
    @ObservedObject var state: ProductUiState
    private var accent: Color { state.currentAppearanceAccent }

    private var equippedSkin: ThreeBladeMetalSkinDetail? {
        state.threeBladeMetalSkins.first {
            $0.id == state.equippedThreeBladeMetalSkinId
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
                    } else if state.progressionModel == .metalThreeBlade {
                        Label("正在确认 Unity Renderer 的实际材质", systemImage: "arrow.triangle.2.circlepath")
                            .font(.product(.caption, weight: .semibold))
                            .foregroundStyle(.orange)
                    }
                }
                .padding(16)
                .productGlass(cornerRadius: 22, tint: accent.opacity(0.08))

                if state.progressionModel == .metalThreeBlade,
                   !state.threeBladeMetalSkins.isEmpty {
                    ForEach(state.threeBladeMetalSkins) { skin in
                        ThreeBladeMetalSkinRow(
                            skin: skin,
                            unlocked: state.progressionLevel >= skin.level,
                            equipped: state.equippedThreeBladeMetalSkinId == skin.id,
                            accent: accent,
                            onEquip: { state.equipThreeBladeMetalSkin(skin) })
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
    static func image(named assetName: String) -> UIImage? {
        guard !assetName.isEmpty else { return nil }
        if let image = UIImage(
            named: assetName,
            in: .main,
            compatibleWith: nil) {
            return image
        }
        guard let url = Bundle.main.url(
            forResource: assetName,
            withExtension: "png") else {
            return nil
        }
        return UIImage(contentsOfFile: url.path)
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
    @State private var shimmerAtBottom = false

    var body: some View {
        GeometryReader { geometry in
            let fillHeight = max(10, geometry.size.height * max(0, min(1, progress)))
            ZStack(alignment: .top) {
                Capsule(style: .continuous)
                    .fill(Color.white.opacity(0.11))
                    .frame(width: 7)
                Capsule(style: .continuous)
                    .fill(LinearGradient(
                        colors: [accent.opacity(0.95), accent.opacity(0.52)],
                        startPoint: .top,
                        endPoint: .bottom))
                    .frame(width: 7, height: fillHeight)
                Capsule(style: .continuous)
                    .fill(Color.white.opacity(0.92))
                    .shadow(color: accent, radius: 8)
                    .frame(width: 11, height: 26)
                    .offset(y: shimmerAtBottom ? max(0, fillHeight - 26) : 0)
                    .opacity(progress > 0 ? 0.82 : 0)
                    .animation(
                        .linear(duration: 1.8).repeatForever(autoreverses: false),
                        value: shimmerAtBottom)
            }
            .frame(maxWidth: .infinity, alignment: .center)
        }
        .onAppear { shimmerAtBottom = true }
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
            selected: current,
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
                            ProductInlineTag(
                                title: "CURRENT",
                                accent: accent,
                                filled: true)
                        }
                    }
                    Text("解锁：\(unlockName)")
                        .font(.product(.caption))
                        .foregroundStyle(Color.white.opacity(unlocked ? 0.66 : 0.32))
                }
                Spacer(minLength: 0)
            }
        }
    }
}

private struct ProgressionBadgeAchievements: View {
    @ObservedObject var state: ProductUiState
    private var accent: Color { state.currentAppearanceAccent }
    private let columns = [
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10)
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                ProductScreenHeading(
                    title: "BADGE ACHIEVEMENTS",
                    subtitle: "\(state.progressionUnlockedAchievementCount) / \(state.progressionTotalAchievementCount) 已点亮",
                    symbol: "seal.fill",
                    accent: accent)
                .padding(16)
                .productGlass(cornerRadius: 22, tint: accent.opacity(0.08))

                LazyVGrid(columns: columns, spacing: 10) {
                    ProductMetricCard(
                        title: "最高速度",
                        value: String(format: "%.2f km/h", state.progressionPeakRimSpeedKmh),
                        symbol: "speedometer")
                    ProductMetricCard(
                        title: "今日滑动",
                        value: "\(state.progressionTodayGestures) 次",
                        symbol: "hand.draw.fill")
                    ProductMetricCard(
                        title: "实际交互",
                        value: durationText(state.progressionActiveInteractionSeconds),
                        symbol: "timer")
                    ProductMetricCard(
                        title: "离线累计",
                        value: compactNumber(state.progressionLifetimeOfflineExperience) + " XP",
                        symbol: "moon.stars.fill")
                }

                ForEach(ProgressionAchievementMetric.allCases, id: \.rawValue) { metric in
                    let achievements = state.progressionAchievements.filter { $0.metric == metric }
                    if !achievements.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            Label(metric.title, systemImage: metric.symbol)
                                .font(.product(.headline))
                                .foregroundStyle(metric.accent)
                            LazyVGrid(columns: columns, spacing: 10) {
                                ForEach(achievements) { achievement in
                                    ProductBadgeTile(
                                        title: achievement.title,
                                        symbol: achievement.metric.symbol,
                                        unlocked: achievement.unlocked,
                                        accent: achievement.metric.accent)
                                }
                            }
                        }
                    }
                }
            }
            .padding(18)
        }
    }

    private func compactNumber(_ value: Double) -> String {
        if value >= 100000 { return String(format: "%.0fK", value / 1000) }
        if value >= 1000 { return String(format: "%.1fK", value / 1000) }
        return String(format: "%.0f", value)
    }

    private func durationText(_ seconds: Double) -> String {
        if seconds >= 3600 { return String(format: "%.1f h", seconds / 3600) }
        if seconds >= 60 { return String(format: "%.0f min", seconds / 60) }
        return String(format: "%.0f sec", seconds)
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
                    Text("成就").tag(1)
                    Text("收藏").tag(2)
                }
                .pickerStyle(.segmented)

                switch selectedSection {
                case 0:
                    rankOverview
                case 1:
                    achievements
                default:
                    collection
                }
            }
            .padding(.horizontal, 18)
            .padding(.top, 16)
            .padding(.bottom, 28)
        }
        .background(ProductBackdrop().ignoresSafeArea())
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

    private var achievements: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("藏家成就")
                    .font(.product(.title3, weight: .bold))
                Spacer()
                Text("\(state.collectorUnlockedAchievementCount)/\(state.collectorTotalAchievementCount)")
                    .font(.product(.subheadline, weight: .semibold).monospacedDigit())
                    .foregroundStyle(Color.white.opacity(0.48))
            }

            ForEach(state.collectorAchievements) { achievement in
                HStack(spacing: 12) {
                    ZStack {
                        Circle()
                            .fill(Color.white.opacity(achievement.unlocked ? 0.10 : 0.025))
                            .background(.ultraThinMaterial, in: Circle())
                        Image(systemName: achievement.unlocked
                              ? achievement.metric.symbol
                              : "lock.fill")
                            .font(.product(.subheadline, weight: .semibold))
                            .foregroundStyle(Color.white.opacity(
                                achievement.unlocked ? 0.84 : 0.22))
                    }
                    .frame(width: 42, height: 42)

                    VStack(alignment: .leading, spacing: 3) {
                        Text(achievement.title)
                            .font(.product(.subheadline, weight: .semibold))
                            .foregroundStyle(Color.white.opacity(
                                achievement.unlocked ? 0.92 : 0.38))
                        Text("\(achievement.metric.title) · 里程碑 \(achievement.threshold)")
                            .font(.product(.caption))
                            .foregroundStyle(Color.white.opacity(
                                achievement.unlocked ? 0.50 : 0.24))
                    }
                    Spacer()
                    Text(achievement.unlocked ? "已获得" : "未点亮")
                        .font(.product(.caption2, weight: .semibold))
                        .foregroundStyle(Color.white.opacity(
                            achievement.unlocked ? 0.62 : 0.22))
                }
                .padding(13)
                .background(
                    Color.white.opacity(achievement.unlocked ? 0.035 : 0.012),
                    in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                .productGlass(
                    cornerRadius: 18,
                    tint: Color.white.opacity(achievement.unlocked ? 0.022 : 0.006))
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

private struct SpinnerLibrary: View {
    @ObservedObject var state: ProductUiState

    private func select(_ model: SpinnerModel) {
        guard state.selectedModel != model else { return }
        UnityBridge.feedback()
        state.select(model)
        CodexSwiftUIOverlayManager.shared.previewModel(model)
    }

    var body: some View {
        VStack(spacing: 0) {
            ProductScreenHeading(
                title: state.selectedModel.title,
                subtitle: "\(state.currentAppearanceName) · LV.\(state.displayedProgressionLevel)",
                centered: true)
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

            Button {
                UnityBridge.feedback(.medium)
                CodexSwiftUIOverlayManager.shared.enterSelectedModel()
            } label: {
                ProductPrimaryActionLabel(
                    title: "进入 \(state.selectedModel.title)",
                    symbol: "arrow.right")
            }
            .buttonStyle(.plain)
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
    }
}

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

            Button {
                state.saveCurrentSpeedTextureSlot()
                UnityBridge.feedback(.medium)
            } label: {
                ProductActionLabel(
                    title: "保存当前参数到 \(state.selectedSpeedTextureSlot.title) 槽",
                    symbol: "tray.and.arrow.down.fill")
            }
            .buttonStyle(.plain)

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
                        projection: .threeBladeHeroPreview)

                    Circle()
                        .fill(Color.black.opacity(0.82))
                        .frame(width: 70, height: 70)
                        .overlay {
                            VStack(spacing: -2) {
                                Text("×20")
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
                    Button {
                        playPreview()
                    } label: {
                        ProductActionLabel(title: "播放预演", symbol: "play.fill")
                    }
                    .buttonStyle(.plain)

                    Button {
                        state.restoreRecommendedComboHaloTuning()
                        playPreview()
                    } label: {
                        ProductActionLabel(
                            title: "恢复推荐",
                            symbol: "arrow.uturn.backward")
                    }
                    .buttonStyle(.plain)
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
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        isComboHaloLabVisible.toggle()
                    }
                } label: {
                    ProductActionLabel(
                        title: isComboHaloLabVisible
                            ? "收起 Combo 光晕工具"
                            : "打开 Combo 光晕工具",
                        symbol: isComboHaloLabVisible
                            ? "chevron.up"
                            : "circle.circle")
                }
                .buttonStyle(.plain)

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

                    Button {
                        state.applyAndPersist()
                        UnityBridge.send("PreviewHapticFromNativeUi")
                    } label: {
                        ProductActionLabel(title: "试听当前组合", symbol: "play.fill")
                    }
                    .buttonStyle(.plain)
                }

                DetentTuningPanel(state: state)

                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        isHapticLabVisible.toggle()
                    }
                } label: {
                    ProductActionLabel(
                        title: isHapticLabVisible ? "收起触觉实验室" : "打开触觉实验室",
                        symbol: isHapticLabVisible ? "chevron.up" : "wrench.and.screwdriver.fill")
                }
                .buttonStyle(.plain)

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
                        Button {
                            state.previewSelectedAdvancedRecipe()
                        } label: {
                            ProductActionLabel(title: "试听当前事件", symbol: "play.fill")
                        }
                        .buttonStyle(.plain)

                        Button {
                            state.resetSelectedAdvancedRecipe()
                            UnityBridge.feedback()
                        } label: {
                            ProductActionLabel(title: "恢复此事件", symbol: "arrow.uturn.backward")
                        }
                        .buttonStyle(.plain)
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

                    Button {
                        UnityBridge.feedback()
                        UnityBridge.send("RecenterMotionFromNativeUi")
                    } label: {
                        ProductActionLabel(title: "重新校准设备姿态", symbol: "scope")
                    }
                    .buttonStyle(.plain)
                }

                Button {
                    state.restoreRecommendedValues()
                    UnityBridge.feedback(.medium)
                } label: {
                    ProductActionLabel(title: "恢复推荐参数", symbol: "arrow.uturn.backward")
                }
                .buttonStyle(.plain)

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

    private let previewCombo = ProgressionComboState(
        tier: 3,
        count: 20,
        title: "OVERDRIVE",
        speed: 0.92,
        angularSpeedRadians: 42,
        intensity: 0.88,
        frequency: 0.84,
        experienceMultiplier: 1.45)

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
                            projection: sceneView.projection)

                        VStack(spacing: 0) {
                            RewardingComboLockup(combo: previewCombo)
                                .padding(.top, 176)
                            Spacer(minLength: 0)

                            Text(mode == .motion
                                 ? "NATIVE IMPLEMENTATION · LIVE LOOP"
                                 : "NATIVE IMPLEMENTATION · 38% FRAME")
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
        case sheet
    }

    @StateObject private var state = ProductUiState()
    let mode: Mode

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
            case .hud:
                ZStack {
                    ProductBackdrop().ignoresSafeArea()
                    VStack(spacing: 0) {
                        Spacer(minLength: 0)
                        SpinnerProgressionHUD(state: state)
                            .padding(.horizontal, 14)
                            .padding(.bottom, 28)
                    }
                }
            case .sheet:
                ProgressionLevelDetailsSheet(state: state)
            }
        }
        .productDesignSystem()
        .preferredColorScheme(.dark)
        .onAppear(perform: configurePreviewState)
    }

    private func configurePreviewState() {
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
            speedBand: .engaged)
        state.progressionNextUnlockLevel = 50
        state.progressionNextUnlockName = "双列辅助轴承"
        state.progressionAssistantEnabled = true
        state.progressionAssistantMultiplier = 1.0
        state.progressionLevelCatalog = ProgressionLevelDetail.fallback
        state.threeBladeMetalSkins = ThreeBladeMetalSkinDetail.parse(
            Self.skinCatalogPayload)
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

@MainActor
private final class CodexSwiftUIOverlayManager {
    static let shared = CodexSwiftUIOverlayManager()

    let state = ProductUiState()
    private var feedbackController: UIHostingController<SpinnerExperienceFeedbackLayer>?
    private var badgeController: UIHostingController<BadgeUnlockOverlay>?
    private var collectorNoticeController: UIHostingController<CollectorUnlockOverlay>?
    private var topController: UIHostingController<ProductTopBar>?
    private var modeController: UIHostingController<ProductModeBar>?
    private var progressionController: UIHostingController<SpinnerProgressionHUD>?
    private var panelController: UIHostingController<ProductPanel>?
    private var appearanceController: UIHostingController<ProductAppearanceEditor>?

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
        let collectorNotice = UIHostingController(
            rootView: CollectorUnlockOverlay(state: state))
        let top = UIHostingController(rootView: ProductTopBar(state: state))
        let mode = UIHostingController(rootView: ProductModeBar(state: state))
        let progression = UIHostingController(rootView: SpinnerProgressionHUD(state: state))
        configure(feedback, in: rootController)
        feedback.view.isUserInteractionEnabled = false
        configure(badge, in: rootController)
        badge.view.isUserInteractionEnabled = false
        configure(collectorNotice, in: rootController)
        collectorNotice.view.isUserInteractionEnabled = false
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

            collectorNotice.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            collectorNotice.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            collectorNotice.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            collectorNotice.view.bottomAnchor.constraint(equalTo: rootController.view.bottomAnchor),

            top.view.topAnchor.constraint(equalTo: rootController.view.topAnchor),
            top.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            top.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            top.view.heightAnchor.constraint(equalToConstant: 108),

            mode.view.topAnchor.constraint(equalTo: rootController.view.topAnchor, constant: 108),
            mode.view.leadingAnchor.constraint(equalTo: rootController.view.leadingAnchor),
            mode.view.trailingAnchor.constraint(equalTo: rootController.view.trailingAnchor),
            mode.view.heightAnchor.constraint(equalToConstant: 58),

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
        collectorNoticeController = collectorNotice
        topController = top
        modeController = mode
        progressionController = progression
        state.applyAndPersist(includeMode: true)
        UnityBridge.send("RequestDetentFeelStateFromNativeUi")
        UnityBridge.send("RequestProgressionStateFromNativeUi")
        showPanel()
    }

    func selectTab(_ tab: ProductTab) {
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

    func showMySpinners() {
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
        UnityBridge.send("SelectModelFromNativeUi", value: state.selectedModel.rawValue)
    }

    func enterSelectedModel() {
        dismissAppearanceEditorIfNeeded()
        state.selectedTab = .spinners
        state.isLibraryVisible = false
        UnityBridge.send("SetLibraryPreviewActiveFromNativeUi", value: "false")
        UnityBridge.send("SelectModelFromNativeUi", value: state.selectedModel.rawValue)
        hidePanel()
        setModeBarVisible(true)
        DispatchQueue.main.async { [weak self] in
            self?.state.presentSpinnerOnboardingIfNeeded()
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
           let badgeController,
           let collectorNoticeController {
            rootController.view.bringSubviewToFront(topController.view)
            rootController.view.bringSubviewToFront(modeController.view)
            rootController.view.bringSubviewToFront(progressionController.view)
            rootController.view.bringSubviewToFront(badgeController.view)
            rootController.view.bringSubviewToFront(collectorNoticeController.view)
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

    private func hidePanel() {
        guard let panel = panelController else { return }
        panel.willMove(toParent: nil)
        UIView.animate(
            withDuration: 0.30,
            delay: 0,
            options: [.curveEaseIn, .beginFromCurrentState]) {
                panel.view.alpha = 0
                panel.view.transform = CGAffineTransform(translationX: 0, y: 28)
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
            if let collectorNoticeView = collectorNoticeController?.view {
                parent.bringSubviewToFront(collectorNoticeView)
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
    let resolvedAchievements = ProgressionAchievementDetail.parse(
        achievementCatalog.map { String(cString: $0) } ?? "")
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
        CodexSwiftUIOverlayManager.shared.state.updateProgression(
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
            unlockedAchievementCount: Int(unlockedAchievementCount),
            totalAchievementCount: Int(totalAchievementCount),
            achievements: resolvedAchievements,
            threeBladeMetalSkins: resolvedThreeBladeMetalSkins,
            equippedThreeBladeMetalSkinId: resolvedEquippedThreeBladeMetalSkinId,
            productStickers: resolvedProductStickers,
            equippedProductStickerId: resolvedEquippedProductStickerId,
            offlineReward: offlineReward,
            liveLevelUp: liveLevelUp)
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
    let achievements = CollectorAchievementDetail.parse(
        achievementCatalogPayload.map { String(cString: $0) } ?? "")

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
            unlockedAchievementCount: Int(unlockedAchievementCount),
            totalAchievementCount: Int(totalAchievementCount),
            discoveredModelIds: discoveredIds,
            achievements: achievements,
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
    _ normalizedSpeed: Float,
    _ angularSpeedRadians: Float,
    _ speedBand: Int32) {
    let telemetry = ProductMotionTelemetryState(
        available: available != 0,
        normalizedSpeed: min(1, max(0, Double(normalizedSpeed))),
        angularSpeedRadians: max(0, Double(angularSpeedRadians)),
        speedBand: ProductSpeedBand(rawValue: Int(speedBand)) ?? .calm)
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
