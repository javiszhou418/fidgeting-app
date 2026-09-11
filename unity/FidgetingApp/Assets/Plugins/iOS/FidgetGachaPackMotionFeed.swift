import Foundation

// Shared CMMotionManager bridge (CodexIosDeviceMotion.mm). The native UI is
// the second client next to the Unity spinner controllers; the bridge only
// stops updates when both clients have left.
@_silgen_name("CodexIosDeviceMotionNativeUiStart")
private func codexIosDeviceMotionNativeUiStart() -> Int32

@_silgen_name("CodexIosDeviceMotionNativeUiStop")
private func codexIosDeviceMotionNativeUiStop()

@_silgen_name("CodexIosDeviceMotionRead")
private func codexIosDeviceMotionRead(
    _ roll: UnsafeMutablePointer<Double>,
    _ pitch: UnsafeMutablePointer<Double>,
    _ yaw: UnsafeMutablePointer<Double>,
    _ rotationRateX: UnsafeMutablePointer<Double>,
    _ rotationRateY: UnsafeMutablePointer<Double>,
    _ rotationRateZ: UnsafeMutablePointer<Double>,
    _ gravityX: UnsafeMutablePointer<Double>,
    _ gravityY: UnsafeMutablePointer<Double>,
    _ gravityZ: UnsafeMutablePointer<Double>,
    _ userAccelerationX: UnsafeMutablePointer<Double>,
    _ userAccelerationY: UnsafeMutablePointer<Double>,
    _ userAccelerationZ: UnsafeMutablePointer<Double>
) -> Int32

/// One frame of motion for the Pack sheen: smoothed gravity relative to the
/// resting pose, plus the running laser sweep if a shake fired one.
public struct GachaPackMotionSample: Equatable {
    public var gravityX: Double
    public var gravityY: Double
    public var sweepProgress: Double?

    public static let still = GachaPackMotionSample(
        gravityX: 0,
        gravityY: 0,
        sweepProgress: nil)
}

/// Pull-based device-motion feed for the sealed Pack (FDB-GAC-036).
///
/// `sample(at:)` is called from the Pack's `TimelineView` once per frame, so
/// no timer or `@Published` per-frame state is needed. Lifecycle: `start`
/// when the Pack is on screen, `stop` when it hands off to the case or the
/// storefront disappears. The Simulator has no gyroscope; the Gate 12 preview
/// asks for a scripted feed that runs the same smoothing, shake detector and
/// sweep pipeline on synthetic gravity, so the recording exercises the real
/// path. Device acceptance stays pending until an iPhone run.
@MainActor
public final class GachaPackMotionFeed: ObservableObject {
    public enum Mode: Equatable {
        case off
        case device
        case scripted
    }

    @Published public private(set) var mode = Mode.off

    /// Scripted hand: slow figure-eight tilt (period 3.6 s / 5.3 s).
    public static let scriptedTiltXAmplitudeG = 0.55
    public static let scriptedTiltXPeriodSeconds = 3.6
    public static let scriptedTiltYAmplitudeG = 0.30
    public static let scriptedTiltYPeriodSeconds = 5.3
    /// Slow re-centering so the sheen settles when the hand settles.
    public static let baselineSmoothingSeconds = 3.0

    private var detector = GachaPackShakeDetector()
    private var smoothedX = 0.0
    private var smoothedY = 0.0
    private var baselineX = 0.0
    private var baselineY = 0.0
    private var hasSample = false
    private var lastSampleTime: Date?
    private var sweepStartedAt: Date?
    private var scriptedStart: Date?
    private var pendingShake = false

    public init() {}

    /// Starts the shared device-motion updates. When the device has no
    /// motion hardware (Simulator) and `preferScripted` is set, runs the
    /// scripted hand instead; otherwise the sheen only rides the idle clock.
    public func start(preferScripted: Bool) {
        guard mode == .off else { return }
        if codexIosDeviceMotionNativeUiStart() != 0 {
            mode = .device
        } else if preferScripted {
            mode = .scripted
            scriptedStart = Date()
        }
        resetFilters()
    }

    public func stop() {
        if mode == .device {
            codexIosDeviceMotionNativeUiStop()
        }
        mode = .off
        scriptedStart = nil
        resetFilters()
    }

    /// Injects one shake sample (preview script / accessibility action).
    public func simulateShake() {
        pendingShake = true
    }

    public var isSweeping: Bool {
        guard let sweepStartedAt else { return false }
        return GachaPackHolographicSheenRules.sweepProgress(
            sinceTrigger: Date().timeIntervalSince(sweepStartedAt)) != nil
    }

    public func sample(at date: Date) -> GachaPackMotionSample {
        let delta = lastSampleTime.map { date.timeIntervalSince($0) } ?? 0
        lastSampleTime = date

        var gravityX = 0.0
        var gravityY = 0.0
        var shakeG = 0.0
        var haveGravity = false
        switch mode {
        case .off:
            break
        case .device:
            var roll = 0.0, pitch = 0.0, yaw = 0.0
            var rateX = 0.0, rateY = 0.0, rateZ = 0.0
            var gx = 0.0, gy = 0.0, gz = 0.0
            var ax = 0.0, ay = 0.0, az = 0.0
            if codexIosDeviceMotionRead(
                &roll, &pitch, &yaw,
                &rateX, &rateY, &rateZ,
                &gx, &gy, &gz,
                &ax, &ay, &az) != 0 {
                gravityX = gx
                gravityY = gy
                shakeG = (ax * ax + ay * ay + az * az).squareRoot()
                haveGravity = true
            }
        case .scripted:
            let t = date.timeIntervalSince(scriptedStart ?? date)
            gravityX = Self.scriptedTiltXAmplitudeG
                * sin(2 * Double.pi * t / Self.scriptedTiltXPeriodSeconds)
            gravityY = Self.scriptedTiltYAmplitudeG
                * sin(2 * Double.pi * t / Self.scriptedTiltYPeriodSeconds + 1.0)
            haveGravity = true
        }
        if pendingShake {
            shakeG = max(shakeG, 1.0)
            pendingShake = false
        }

        if haveGravity {
            if !hasSample || delta <= 0 {
                if !hasSample {
                    smoothedX = gravityX
                    smoothedY = gravityY
                    baselineX = gravityX
                    baselineY = gravityY
                    hasSample = true
                }
            } else {
                let weight = GachaPackHolographicSheenRules.smoothingWeight(
                    deltaSeconds: delta)
                smoothedX += (gravityX - smoothedX) * weight
                smoothedY += (gravityY - smoothedY) * weight
                let baselineWeight = 1 - exp(-delta / Self.baselineSmoothingSeconds)
                baselineX += (smoothedX - baselineX) * baselineWeight
                baselineY += (smoothedY - baselineY) * baselineWeight
            }
        }

        if detector.ingest(
            userAccelerationG: shakeG,
            time: date.timeIntervalSinceReferenceDate) {
            sweepStartedAt = date
        }

        return GachaPackMotionSample(
            gravityX: haveGravity ? smoothedX - baselineX : 0,
            gravityY: haveGravity ? smoothedY - baselineY : 0,
            sweepProgress: GachaPackHolographicSheenRules.sweepProgress(
                sinceTrigger: sweepStartedAt.map { date.timeIntervalSince($0) }))
    }

    private func resetFilters() {
        detector = GachaPackShakeDetector()
        smoothedX = 0
        smoothedY = 0
        baselineX = 0
        baselineY = 0
        hasSample = false
        lastSampleTime = nil
        sweepStartedAt = nil
        pendingShake = false
    }
}
