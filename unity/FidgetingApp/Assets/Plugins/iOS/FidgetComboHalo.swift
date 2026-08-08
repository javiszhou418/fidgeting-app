import SwiftUI

/// Screen-space projection of the model's authored interaction plane. Unity
/// publishes these values from the live camera so the native halo shares the
/// model's center, tilt and perspective compression instead of facing screen.
struct ComboHaloProjectionState: Equatable {
    static let centered = ComboHaloProjectionState(
        available: false,
        centerX: 0.5,
        centerY: 0.5,
        rotationDegrees: 0,
        minorAxisRatio: 1)

    static let threeBladeHeroPreview = ComboHaloProjectionState(
        available: true,
        centerX: 0.5,
        centerY: 0.5,
        rotationDegrees: 0,
        minorAxisRatio: 0.67)

    var available: Bool
    var centerX: Double
    var centerY: Double
    var rotationDegrees: Double
    var minorAxisRatio: Double

    func clamped() -> ComboHaloProjectionState {
        ComboHaloProjectionState(
            available: available,
            centerX: min(1, max(0, centerX)),
            centerY: min(1, max(0, centerY)),
            rotationDegrees: min(180, max(-180, rotationDegrees)),
            minorAxisRatio: min(1, max(0.18, minorAxisRatio)))
    }
}

/// Count-derived visual tier for one-shot Combo milestone feedback. The tier
/// only changes presentation; it never changes Combo counting, XP or physics.
enum ComboHaloMilestoneStyle: Equatable {
    case standard
    case overdrive
    case apex

    static func forCount(_ count: Int) -> ComboHaloMilestoneStyle {
        if count >= 50 { return .apex }
        if count >= 30 { return .overdrive }
        return .standard
    }

    var speedLineCount: Int {
        switch self {
        case .standard: return 0
        case .overdrive: return 10
        case .apex: return 14
        }
    }

    var speedLinePeakScale: Double {
        switch self {
        case .standard: return 0
        case .overdrive: return 0.86
        case .apex: return 1.12
        }
    }

    var edgeBloomPeakScale: Double {
        switch self {
        case .standard: return 0
        case .overdrive: return 0.58
        case .apex: return 0.78
        }
    }
}

/// Native source of truth for the milestone halo and its editable timing curve.
/// The production overlay and the Combo Halo Lab both render this same type.
struct ComboHaloTuning: Codable, Equatable {
    static let recommended = ComboHaloTuning(
        firstMilestone: 10,
        repeatInterval: 10,
        durationSeconds: 0.92,
        endRadiusScale: 1.04,
        peakOpacity: 0.34,
        curveX1: 0.16,
        curveY1: 0.72,
        curveX2: 0.24,
        curveY2: 1.00)

    var firstMilestone: Int
    var repeatInterval: Int
    var durationSeconds: Double
    var endRadiusScale: Double
    var peakOpacity: Double
    var curveX1: Double
    var curveY1: Double
    var curveX2: Double
    var curveY2: Double

    mutating func clampValues() {
        firstMilestone = min(50, max(5, firstMilestone))
        repeatInterval = min(50, max(5, repeatInterval))
        durationSeconds = min(1.20, max(0.24, durationSeconds))
        endRadiusScale = min(1.20, max(0.72, endRadiusScale))
        peakOpacity = min(0.60, max(0.08, peakOpacity))
        curveX1 = min(0.98, max(0.02, curveX1))
        curveX2 = min(0.98, max(curveX1, curveX2))
        curveY1 = min(1.00, max(0.00, curveY1))
        curveY2 = min(1.00, max(0.00, curveY2))
    }

    func milestoneCrossed(previousCount: Int, newCount: Int) -> Bool {
        guard newCount > previousCount,
              newCount >= firstMilestone else { return false }
        if previousCount < firstMilestone { return true }

        let distance = max(0, previousCount + 1 - firstMilestone)
        let nextStep = firstMilestone
            + ((distance + repeatInterval - 1) / repeatInterval) * repeatInterval
        return nextStep <= newCount
    }

    /// Separating the layer envelopes creates a readable primary, secondary
    /// and tertiary hierarchy instead of fading one uniformly drawn ring.
    /// These rules are deterministic so production, the lab and native tests
    /// all share the exact same timing.
    func coreFlashOpacity(at progress: Double) -> Double {
        envelope(
            at: progress,
            start: 0.00,
            attackEnd: 0.035,
            releaseStart: 0.065,
            end: 0.20,
            peakScale: 0.72)
    }

    func primaryRingOpacity(at progress: Double) -> Double {
        envelope(
            at: progress,
            start: 0.00,
            attackEnd: 0.055,
            releaseStart: 0.12,
            end: 0.48,
            peakScale: 1.00)
    }

    func echoRingOpacity(at progress: Double) -> Double {
        envelope(
            at: progress,
            start: 0.05,
            attackEnd: 0.12,
            releaseStart: 0.20,
            end: 0.64,
            peakScale: 0.65)
    }

    func trailingRingOpacity(at progress: Double) -> Double {
        envelope(
            at: progress,
            start: 0.10,
            attackEnd: 0.18,
            releaseStart: 0.28,
            end: 0.80,
            peakScale: 0.38)
    }

    func mistOpacity(at progress: Double) -> Double {
        envelope(
            at: progress,
            start: 0.01,
            attackEnd: 0.10,
            releaseStart: 0.28,
            end: 1.00,
            peakScale: 0.78)
    }

    func speedTunnelOpacity(
        at progress: Double,
        style: ComboHaloMilestoneStyle) -> Double {
        envelope(
            at: progress,
            start: 0.035,
            attackEnd: 0.075,
            releaseStart: 0.14,
            end: 0.74,
            peakScale: style.speedLinePeakScale)
    }

    func edgeBloomOpacity(
        at progress: Double,
        style: ComboHaloMilestoneStyle) -> Double {
        envelope(
            at: progress,
            start: 0.00,
            attackEnd: 0.025,
            releaseStart: 0.055,
            end: 0.32,
            peakScale: style.edgeBloomPeakScale)
    }

    func phase(
        at progress: Double,
        start: Double,
        end: Double) -> Double {
        guard end > start else { return progress >= end ? 1 : 0 }
        return min(1, max(0, (progress - start) / (end - start)))
    }

    private func envelope(
        at progress: Double,
        start: Double,
        attackEnd: Double,
        releaseStart: Double,
        end: Double,
        peakScale: Double) -> Double {
        let clampedProgress = min(1, max(0, progress))
        guard clampedProgress >= start,
              clampedProgress < end else { return 0 }

        let attackPhase = phase(
            at: clampedProgress,
            start: start,
            end: attackEnd)
        let attack = smoothstep(attackPhase)
        let releasePhase = phase(
            at: clampedProgress,
            start: releaseStart,
            end: end)
        return peakOpacity * peakScale * attack * (1 - smoothstep(releasePhase))
    }

    private func smoothstep(_ progress: Double) -> Double {
        progress * progress * (3 - 2 * progress)
    }

    var animation: Animation {
        .timingCurve(
            curveX1,
            curveY1,
            curveX2,
            curveY2,
            duration: durationSeconds)
    }
}

/// A softly irregular cloud silhouette. It is intentionally not an annulus:
/// the reference's mist churns around the source instead of reading as one
/// more blurred concentric ring.
private struct ComboHaloMistCloud: Shape {
    var phase: CGFloat
    let rippleOffset: CGFloat

    var animatableData: CGFloat {
        get { phase }
        set { phase = newValue }
    }

    func path(in rect: CGRect) -> Path {
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let baseRadius = min(rect.width, rect.height) * 0.5
        let steps = 96
        var path = Path()

        for index in 0...steps {
            let angle = CGFloat(index) / CGFloat(steps) * .pi * 2
            let ripple = radialRipple(at: angle)
            let radius = baseRadius * (1 + ripple)
            let point = CGPoint(
                x: center.x + cos(angle) * radius,
                y: center.y + sin(angle) * radius)
            index == 0 ? path.move(to: point) : path.addLine(to: point)
        }
        path.closeSubpath()
        return path
    }

    private func radialRipple(at angle: CGFloat) -> CGFloat {
        let animatedPhase = phase * .pi * 0.86
        return sin(angle * 5 + animatedPhase + rippleOffset) * 0.034
            + sin(angle * 9 - animatedPhase * 0.72 - rippleOffset) * 0.024
            + sin(angle * 13 + animatedPhase * 0.38) * 0.012
    }
}

/// Three uneven arc groups form a burst ring. The gaps, unequal brightness and
/// slightly different rotations keep a packet of rings from reading as a HUD
/// target or a loading indicator.
private struct ComboHaloBrokenRing: View {
    let lineWidth: CGFloat
    let gapRotation: Double

    var body: some View {
        ZStack {
            arc(from: 0.01, to: 0.23, opacity: 0.92)
            arc(from: 0.31, to: 0.50, opacity: 0.58)
            arc(from: 0.57, to: 0.78, opacity: 0.78)
            arc(from: 0.86, to: 0.97, opacity: 0.42)
        }
        .rotationEffect(.degrees(gapRotation))
    }

    private func arc(
        from start: CGFloat,
        to end: CGFloat,
        opacity: Double) -> some View {
        Circle()
            .trim(from: start, to: end)
            .stroke(
                Color.white.opacity(opacity),
                style: StrokeStyle(
                    lineWidth: lineWidth,
                    lineCap: .round))
    }
}

/// Thin radial wisps make the cloud feel like it is releasing and curling in
/// space. They stay soft and monochrome, and are part of the model-plane group.
private struct ComboHaloMistWisps: View {
    let phase: CGFloat

    var body: some View {
        GeometryReader { proxy in
            let width = proxy.size.width
            ZStack {
                ForEach(0..<9, id: \.self) { index in
                    let angle = Double(index) * 40.0
                        + Double(phase) * (index.isMultiple(of: 2) ? 34.0 : -27.0)
                    let orbit = width
                        * CGFloat(0.065 + Double(index % 3) * 0.025)

                    Ellipse()
                        .fill(RadialGradient(
                            stops: [
                                .init(color: .white.opacity(
                                    index.isMultiple(of: 3) ? 0.48 : 0.30), location: 0.00),
                                .init(color: .white.opacity(0.16), location: 0.38),
                                .init(color: .clear, location: 1.00)
                            ],
                            center: .center,
                            startRadius: 0,
                            endRadius: width * 0.11))
                        .frame(
                            width: width * CGFloat(0.16 + Double(index % 4) * 0.018),
                            height: width * CGFloat(0.09 + Double(index % 3) * 0.014))
                        .offset(x: orbit)
                        .rotationEffect(.degrees(angle))
                        .blur(radius: index.isMultiple(of: 2) ? 7 : 11)

                }

                ForEach(0..<7, id: \.self) { index in
                    Capsule(style: .continuous)
                        .fill(LinearGradient(
                            stops: [
                                .init(color: .clear, location: 0.00),
                                .init(color: .white.opacity(
                                    index.isMultiple(of: 2) ? 0.34 : 0.20), location: 0.46),
                                .init(color: .clear, location: 1.00)
                            ],
                            startPoint: .leading,
                            endPoint: .trailing))
                        .frame(
                            width: width * CGFloat(0.28 + Double(index % 3) * 0.045),
                            height: max(2, width * CGFloat(0.010 + Double(index % 2) * 0.006)))
                        .offset(x: width * CGFloat(0.12 + Double(index % 2) * 0.025))
                        .rotationEffect(.degrees(
                            Double(index) * 51.0
                                + Double(phase) * 42.0))
                        .blur(radius: index.isMultiple(of: 2) ? 5 : 8)
                }
            }
            .frame(width: proxy.size.width, height: proxy.size.height)
        }
    }
}

/// A restrained camera-space speed tunnel for rare high Combo milestones.
/// Every streak begins outside the model silhouette so the material remains
/// readable; the softened model-plane compression keeps the burst attached to
/// the live object without turning it into a flat HUD starburst.
private struct ComboHaloSpeedTunnel: View {
    let phase: CGFloat
    let style: ComboHaloMilestoneStyle

    var body: some View {
        GeometryReader { proxy in
            let diameter = min(proxy.size.width, proxy.size.height)
            let lineCount = style.speedLineCount

            ZStack {
                ForEach(0..<lineCount, id: \.self) { index in
                    let variation = CGFloat(index % 4) * 0.022
                    let length = diameter * (0.19 + variation)
                    let innerRadius = diameter
                        * (0.17 + CGFloat(index % 3) * 0.012)
                    let travel = diameter * phase
                        * (0.18 + CGFloat(index % 5) * 0.010)
                    let angle = Double(index) / Double(max(1, lineCount)) * 360
                        + Double((index * 17) % 23) - 11

                    Capsule(style: .continuous)
                        .fill(LinearGradient(
                            stops: [
                                .init(color: .clear, location: 0.00),
                                .init(color: .white.opacity(
                                    index.isMultiple(of: 3) ? 0.86 : 0.58), location: 0.28),
                                .init(color: .white.opacity(0.16), location: 0.72),
                                .init(color: .clear, location: 1.00)
                            ],
                            startPoint: .leading,
                            endPoint: .trailing))
                        .frame(
                            width: length,
                            height: max(
                                1.2,
                                diameter * (index.isMultiple(of: 3)
                                    ? 0.009
                                    : 0.006)))
                        .offset(x: innerRadius + length * 0.5 + travel)
                        .rotationEffect(.degrees(angle))
                        .blur(radius: index.isMultiple(of: 3) ? 1.6 : 0.7)
                        .shadow(
                            color: .white.opacity(0.34),
                            radius: index.isMultiple(of: 3) ? 4 : 2)
                        .opacity(index.isMultiple(of: 4) ? 0.70 : 1.00)
                }
            }
            .frame(width: proxy.size.width, height: proxy.size.height)
        }
    }
}

/// A neutral-white layered pulse that expands in the live model plane.
/// `progress` drives the authored primary curve; `opacityProgress` is a linear
/// clock used to offset the core flash, primary ring, echo ring and mist.
struct ComboCenterHalo: View, Animatable {
    var progress: CGFloat
    var opacityProgress: CGFloat
    let tuning: ComboHaloTuning
    let reduceMotion: Bool
    let projection: ComboHaloProjectionState
    var milestoneCount: Int = 10

    var animatableData: AnimatablePair<CGFloat, CGFloat> {
        get { AnimatablePair(progress, opacityProgress) }
        set {
            progress = newValue.first
            opacityProgress = newValue.second
        }
    }

    private var clampedProgress: CGFloat {
        min(1, max(0, progress))
    }

    private var linearProgress: Double {
        Double(min(1, max(0, opacityProgress)))
    }

    private func easeOutCubic(_ progress: Double) -> CGFloat {
        let inverse = 1 - min(1, max(0, progress))
        return CGFloat(1 - inverse * inverse * inverse)
    }

    var body: some View {
        GeometryReader { proxy in
            let stageDiameter = min(proxy.size.width, proxy.size.height)
            let liveProjection = projection.clamped()
            let axisRatio = CGFloat(
                liveProjection.available
                    ? liveProjection.minorAxisRatio
                    : 1)
            let centerX = CGFloat(
                liveProjection.available ? liveProjection.centerX : 0.5)
            let centerY = CGFloat(
                liveProjection.available ? liveProjection.centerY : 0.5)
            let rotation = liveProjection.available
                ? liveProjection.rotationDegrees
                : 0
            let milestoneStyle = ComboHaloMilestoneStyle.forCount(
                milestoneCount)
            let speedAxisRatio = CGFloat(0.82) + axisRatio * 0.18

            let primaryExpansion = reduceMotion
                ? CGFloat(0.68)
                : CGFloat(0.24)
                    + clampedProgress
                    * CGFloat(tuning.endRadiusScale - 0.24)
            let echoPhase = easeOutCubic(tuning.phase(
                at: linearProgress,
                start: 0.05,
                end: 0.64))
            let echoExpansion = reduceMotion
                ? CGFloat(0.62)
                : CGFloat(0.22)
                    + echoPhase
                    * CGFloat(tuning.endRadiusScale * 0.88 - 0.22)
            let trailingPhase = easeOutCubic(tuning.phase(
                at: linearProgress,
                start: 0.10,
                end: 0.80))
            let trailingExpansion = reduceMotion
                ? CGFloat(0.56)
                : CGFloat(0.18)
                    + trailingPhase
                    * CGFloat(tuning.endRadiusScale * 0.74 - 0.18)
            let mistPhase = easeOutCubic(tuning.phase(
                at: linearProgress,
                start: 0.01,
                end: 1.00))
            let mistExpansion = reduceMotion
                ? CGFloat(0.66)
                : CGFloat(0.30)
                    + mistPhase
                    * CGFloat(tuning.endRadiusScale * 0.82 - 0.30)
            let corePhase = easeOutCubic(tuning.phase(
                at: linearProgress,
                start: 0.00,
                end: 0.20))
            let coreExpansion = reduceMotion
                ? CGFloat(0.52)
                : CGFloat(0.26) + corePhase * 0.42
            let speedPhase = easeOutCubic(tuning.phase(
                at: linearProgress,
                start: 0.035,
                end: 0.74))
            let speedExpansion = CGFloat(0.86) + speedPhase * 0.28

            ZStack {
                if milestoneStyle != .standard && !reduceMotion {
                    ComboHaloSpeedTunnel(
                        phase: speedPhase,
                        style: milestoneStyle)
                        .frame(
                            width: stageDiameter * 1.10,
                            height: stageDiameter * 1.10)
                        .scaleEffect(
                            x: speedExpansion,
                            y: speedExpansion * speedAxisRatio)
                        .rotationEffect(.degrees(rotation))
                        .opacity(tuning.speedTunnelOpacity(
                            at: linearProgress,
                            style: milestoneStyle))

                    ZStack {
                        ComboHaloBrokenRing(lineWidth: 13, gapRotation: -4)
                            .opacity(0.34)
                            .blur(radius: 12)
                        ComboHaloBrokenRing(lineWidth: 2.1, gapRotation: -4)
                            .opacity(0.74)
                            .blur(radius: 1.2)
                    }
                    .frame(
                        width: stageDiameter * 0.54,
                        height: stageDiameter * 0.54)
                    .scaleEffect(
                        x: 0.74 + speedPhase * 0.18,
                        y: (0.74 + speedPhase * 0.18) * axisRatio)
                    .rotationEffect(.degrees(rotation))
                    .opacity(tuning.edgeBloomOpacity(
                        at: linearProgress,
                        style: milestoneStyle))
                }

                ZStack {
                    ComboHaloMistCloud(
                        phase: CGFloat(linearProgress),
                        rippleOffset: 0.0)
                        .fill(RadialGradient(
                            stops: [
                                .init(color: .clear, location: 0.00),
                                .init(color: .white.opacity(0.62), location: 0.26),
                                .init(color: .white.opacity(0.38), location: 0.52),
                                .init(color: .white.opacity(0.12), location: 0.76),
                                .init(color: .clear, location: 1.00)
                            ],
                            center: .center,
                            startRadius: 0,
                            endRadius: stageDiameter * 0.34))
                        .blur(radius: 13)

                    ComboHaloMistCloud(
                        phase: CGFloat(linearProgress * 0.72),
                        rippleOffset: 1.7)
                        .fill(AngularGradient(
                            stops: [
                                .init(color: .white.opacity(0.10), location: 0.00),
                                .init(color: .white.opacity(0.42), location: 0.22),
                                .init(color: .white.opacity(0.14), location: 0.48),
                                .init(color: .white.opacity(0.36), location: 0.73),
                                .init(color: .white.opacity(0.10), location: 1.00)
                            ],
                            center: .center))
                        .scaleEffect(0.84)
                        .blur(radius: 14)

                    ComboHaloMistWisps(phase: CGFloat(linearProgress))
                        .opacity(0.90)
                }
                .frame(width: stageDiameter * 0.78, height: stageDiameter * 0.78)
                .scaleEffect(
                    x: mistExpansion,
                    y: mistExpansion * axisRatio)
                .rotationEffect(.degrees(rotation))
                .opacity(tuning.mistOpacity(at: linearProgress))

                ZStack {
                    ComboHaloBrokenRing(lineWidth: 5.2, gapRotation: -13)
                        .opacity(0.28)
                        .blur(radius: 7)
                    ComboHaloBrokenRing(lineWidth: 1.10, gapRotation: -13)
                        .opacity(0.74)
                        .blur(radius: 0.8)
                }
                .frame(width: stageDiameter * 0.96, height: stageDiameter * 0.96)
                .scaleEffect(
                    x: echoExpansion,
                    y: echoExpansion * axisRatio)
                .rotationEffect(.degrees(rotation))
                .opacity(tuning.echoRingOpacity(at: linearProgress))

                ZStack {
                    ComboHaloBrokenRing(lineWidth: 7.0, gapRotation: 4)
                        .opacity(0.30)
                        .blur(radius: 8)
                    ComboHaloBrokenRing(lineWidth: 1.65, gapRotation: 4)
                        .opacity(0.94)
                        .blur(radius: 0.35)
                }
                .frame(width: stageDiameter * 1.02, height: stageDiameter * 1.02)
                .scaleEffect(
                    x: primaryExpansion,
                    y: primaryExpansion * axisRatio)
                .rotationEffect(.degrees(rotation))
                .opacity(tuning.primaryRingOpacity(at: linearProgress))

                ZStack {
                    ComboHaloBrokenRing(lineWidth: 4.0, gapRotation: 19)
                        .opacity(0.22)
                        .blur(radius: 7)
                    ComboHaloBrokenRing(lineWidth: 0.82, gapRotation: 19)
                        .opacity(0.58)
                        .blur(radius: 1.0)
                }
                .frame(width: stageDiameter * 0.94, height: stageDiameter * 0.94)
                .scaleEffect(
                    x: trailingExpansion,
                    y: trailingExpansion * axisRatio)
                .rotationEffect(.degrees(rotation))
                .opacity(tuning.trailingRingOpacity(at: linearProgress))

                Circle()
                    .fill(RadialGradient(
                        stops: [
                            .init(color: .white.opacity(0.56), location: 0.00),
                            .init(color: .white.opacity(0.24), location: 0.22),
                            .init(color: .white.opacity(0.07), location: 0.58),
                            .init(color: .clear, location: 1.00)
                        ],
                        center: .center,
                        startRadius: 0,
                        endRadius: stageDiameter * 0.18))
                    .frame(width: stageDiameter * 0.38, height: stageDiameter * 0.38)
                    .scaleEffect(
                        x: coreExpansion,
                        y: coreExpansion * axisRatio)
                    .rotationEffect(.degrees(rotation))
                    .blur(radius: 12)
                    .opacity(tuning.coreFlashOpacity(at: linearProgress))
            }
            .frame(width: stageDiameter, height: stageDiameter)
            .position(
                x: proxy.size.width * centerX,
                y: proxy.size.height * centerY)
            .compositingGroup()
            .blendMode(.screen)
        }
        .allowsHitTesting(false)
        .accessibilityHidden(true)
    }
}

/// Compact two-handle cubic Bézier editor used by the native Combo Halo Lab.
struct ComboBezierCurveEditor: View {
    @Binding var x1: Double
    @Binding var y1: Double
    @Binding var x2: Double
    @Binding var y2: Double

    private let inset: CGFloat = 14

    var body: some View {
        GeometryReader { proxy in
            let width = max(1, proxy.size.width - inset * 2)
            let height = max(1, proxy.size.height - inset * 2)
            let start = CGPoint(x: inset, y: inset + height)
            let end = CGPoint(x: inset + width, y: inset)
            let control1 = CGPoint(
                x: inset + width * CGFloat(x1),
                y: inset + height * CGFloat(1 - y1))
            let control2 = CGPoint(
                x: inset + width * CGFloat(x2),
                y: inset + height * CGFloat(1 - y2))

            ZStack {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(Color.black.opacity(0.32))

                Path { path in
                    for index in 0...4 {
                        let fraction = CGFloat(index) / 4
                        path.move(to: CGPoint(
                            x: inset + width * fraction,
                            y: inset))
                        path.addLine(to: CGPoint(
                            x: inset + width * fraction,
                            y: inset + height))
                        path.move(to: CGPoint(
                            x: inset,
                            y: inset + height * fraction))
                        path.addLine(to: CGPoint(
                            x: inset + width,
                            y: inset + height * fraction))
                    }
                }
                .stroke(Color.white.opacity(0.07), lineWidth: 1)

                Path { path in
                    path.move(to: start)
                    path.addLine(to: control1)
                    path.move(to: end)
                    path.addLine(to: control2)
                }
                .stroke(
                    Color.white.opacity(0.24),
                    style: StrokeStyle(lineWidth: 1, dash: [4, 4]))

                Path { path in
                    path.move(to: start)
                    path.addCurve(
                        to: end,
                        control1: control1,
                        control2: control2)
                }
                .stroke(
                    Color.white.opacity(0.92),
                    style: StrokeStyle(lineWidth: 2.5, lineCap: .round))

                curveHandle(at: control1, label: "起势")
                    .gesture(curveDrag(
                        proxySize: proxy.size,
                        isFirstHandle: true))

                curveHandle(at: control2, label: "收势")
                    .gesture(curveDrag(
                        proxySize: proxy.size,
                        isFirstHandle: false))
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Combo 光晕动画曲线")
    }

    private func curveHandle(at point: CGPoint, label: String) -> some View {
        Circle()
            .fill(Color.white)
            .frame(width: 18, height: 18)
            .overlay(Circle().fill(Color.black).frame(width: 6, height: 6))
            .position(point)
            .accessibilityLabel(label)
    }

    private func curveDrag(
        proxySize: CGSize,
        isFirstHandle: Bool) -> some Gesture {
        DragGesture(minimumDistance: 0)
            .onChanged { value in
                let width = max(1, proxySize.width - inset * 2)
                let height = max(1, proxySize.height - inset * 2)
                let normalizedX = Double(min(
                    1,
                    max(0, (value.location.x - inset) / width)))
                let normalizedY = Double(min(
                    1,
                    max(0, 1 - (value.location.y - inset) / height)))

                if isFirstHandle {
                    x1 = min(x2, normalizedX)
                    y1 = normalizedY
                } else {
                    x2 = max(x1, normalizedX)
                    y2 = normalizedY
                }
            }
    }
}
