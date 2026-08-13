using System;
using System.Runtime.InteropServices;
using UnityEngine;

namespace FidgetingApp.Product
{
    public enum SpinnerComboTier
    {
        None = 0,
        Flow = 1,
        Drive = 2,
        Overdrive = 3
    }

    public readonly struct SpinnerComboSnapshot : IEquatable<SpinnerComboSnapshot>
    {
        public SpinnerComboSnapshot(
            SpinnerComboTier tier,
            int count,
            float normalizedSpeed,
            float normalizedIntensity,
            float normalizedFrequency,
            float experienceMultiplier)
        {
            Tier = tier;
            Count = Mathf.Max(0, count);
            NormalizedSpeed = Mathf.Clamp01(normalizedSpeed);
            NormalizedIntensity = Mathf.Clamp01(normalizedIntensity);
            NormalizedFrequency = Mathf.Clamp01(normalizedFrequency);
            ExperienceMultiplier = Mathf.Max(1f, experienceMultiplier);
        }

        public SpinnerComboTier Tier { get; }
        public int Count { get; }
        public float NormalizedSpeed { get; }
        public float NormalizedIntensity { get; }
        public float NormalizedFrequency { get; }
        public float ExperienceMultiplier { get; }
        public bool IsActive => Tier != SpinnerComboTier.None && Count >= 2;

        public string Title
        {
            get
            {
                switch (Tier)
                {
                    case SpinnerComboTier.Flow:
                        return "顺流";
                    case SpinnerComboTier.Drive:
                        return "强驱";
                    case SpinnerComboTier.Overdrive:
                        return "超频";
                    default:
                        return string.Empty;
                }
            }
        }

        public bool Equals(SpinnerComboSnapshot other)
        {
            return Tier == other.Tier
                && Count == other.Count
                && Mathf.Approximately(NormalizedSpeed, other.NormalizedSpeed)
                && Mathf.Approximately(NormalizedIntensity, other.NormalizedIntensity)
                && Mathf.Approximately(NormalizedFrequency, other.NormalizedFrequency)
                && Mathf.Approximately(ExperienceMultiplier, other.ExperienceMultiplier);
        }

        public override bool Equals(object obj)
        {
            return obj is SpinnerComboSnapshot other && Equals(other);
        }

        public override int GetHashCode()
        {
            unchecked
            {
                int hash = (int)Tier;
                hash = (hash * 397) ^ Count;
                hash = (hash * 397) ^ NormalizedSpeed.GetHashCode();
                hash = (hash * 397) ^ NormalizedIntensity.GetHashCode();
                hash = (hash * 397) ^ NormalizedFrequency.GetHashCode();
                hash = (hash * 397) ^ ExperienceMultiplier.GetHashCode();
                return hash;
            }
        }

        public static SpinnerComboSnapshot Rest => new SpinnerComboSnapshot(
            SpinnerComboTier.None,
            0,
            0f,
            0f,
            0f,
            1f);
    }

    /// <summary>
    /// Product combo rules. Speed is real rotor angular speed, intensity is
    /// the completed swipe force, and frequency is recent swipe cadence. This
    /// keeps all three inputs independent: detent density is never counted as
    /// a second copy of rotor speed.
    /// </summary>
    public static class SpinnerComboRules
    {
        public const float FullScaleAngularSpeed = 30f;
        public const float MinimumSwipeFrequency = 0.25f;
        public const float FullScaleSwipeFrequency = 1.5f;
        public const float ComboTimeoutSeconds = 2.4f;
        public const float HudUpdateIntervalSeconds = 0.05f;
        public const float CountPulseDegrees = 120f;
        public const float MinimumCountPulseIntervalSeconds = 0.16f;
        public const float MinimumCountPulseAngularSpeed = 4f;

        public static SpinnerComboTier ResolveTier(
            float normalizedSpeed,
            float normalizedIntensity,
            float normalizedFrequency)
        {
            float speed = Mathf.Clamp01(normalizedSpeed);
            float intensity = Mathf.Clamp01(normalizedIntensity);
            float frequency = Mathf.Clamp01(normalizedFrequency);

            if (speed >= 0.72f && intensity >= 0.72f && frequency >= 0.70f)
            {
                return SpinnerComboTier.Overdrive;
            }

            if (speed >= 0.45f && intensity >= 0.50f && frequency >= 0.45f)
            {
                return SpinnerComboTier.Drive;
            }

            if (speed >= 0.22f && intensity >= 0.25f && frequency >= 0.20f)
            {
                return SpinnerComboTier.Flow;
            }

            return SpinnerComboTier.None;
        }

        public static float ExperienceMultiplier(SpinnerComboTier tier)
        {
            switch (tier)
            {
                case SpinnerComboTier.Flow:
                    return 1.08f;
                case SpinnerComboTier.Drive:
                    return 1.18f;
                case SpinnerComboTier.Overdrive:
                    return 1.30f;
                default:
                    return 1f;
            }
        }

        public static float NormalizeSpeed(float angularSpeedRadians)
        {
            return Mathf.Clamp01(Mathf.Abs(angularSpeedRadians) / FullScaleAngularSpeed);
        }

        public static float NormalizeFrequency(float gesturesPerSecond)
        {
            return Mathf.InverseLerp(
                MinimumSwipeFrequency,
                FullScaleSwipeFrequency,
                Mathf.Max(0f, gesturesPerSecond));
        }
    }

    public enum SpinnerSpeedBand
    {
        Calm = 0,
        Engaged = 1,
        Fast = 2,
        Peak = 3
    }

    /// <summary>
    /// Presentation-only speed bands for the read-only dashboard. The bands
    /// never write motion, award progression, or emit Haptics. A four-percent
    /// exit hysteresis prevents color chatter around the three enter thresholds.
    /// </summary>
    public static class SpinnerSpeedDashboardRules
    {
        public const float EngagedEnter = 0.25f;
        public const float FastEnter = 0.55f;
        public const float PeakEnter = 0.80f;
        public const float ExitHysteresis = 0.04f;

        public static SpinnerSpeedBand ResolveBand(
            float normalizedSpeed,
            SpinnerSpeedBand current)
        {
            float speed = Mathf.Clamp01(normalizedSpeed);
            if (current == SpinnerSpeedBand.Peak
                && speed >= PeakEnter - ExitHysteresis)
            {
                return SpinnerSpeedBand.Peak;
            }

            if (current == SpinnerSpeedBand.Fast
                && speed >= FastEnter - ExitHysteresis
                && speed < PeakEnter)
            {
                return SpinnerSpeedBand.Fast;
            }

            if (current == SpinnerSpeedBand.Engaged
                && speed >= EngagedEnter - ExitHysteresis
                && speed < FastEnter)
            {
                return SpinnerSpeedBand.Engaged;
            }

            if (speed >= PeakEnter)
            {
                return SpinnerSpeedBand.Peak;
            }

            if (speed >= FastEnter)
            {
                return SpinnerSpeedBand.Fast;
            }

            return speed >= EngagedEnter
                ? SpinnerSpeedBand.Engaged
                : SpinnerSpeedBand.Calm;
        }
    }

    /// <summary>
    /// Allocation-free session tracker. A combo starts on the second timely
    /// qualifying swipe and expires after a real-time pause. It never writes
    /// rotor velocity, resistance, or any other physics state.
    /// </summary>
    public sealed class SpinnerComboRuntime
    {
        private float lastGestureTime = float.NegativeInfinity;
        private float lastQualifiedTime = float.NegativeInfinity;
        private float lastCountPulseTime = float.NegativeInfinity;
        private float accumulatedCountPulseDegrees;
        private SpinnerComboSnapshot snapshot = SpinnerComboSnapshot.Rest;

        public SpinnerComboSnapshot Snapshot => snapshot;

        public bool RecordGesture(
            float unscaledTime,
            float angularSpeedRadians,
            float normalizedIntensity)
        {
            float speed = SpinnerComboRules.NormalizeSpeed(angularSpeedRadians);
            float intensity = Mathf.Clamp01(normalizedIntensity);
            bool baseQuality = speed >= 0.22f && intensity >= 0.25f;
            float interval = unscaledTime - lastGestureTime;
            float gesturesPerSecond = !baseQuality
                || float.IsNegativeInfinity(lastGestureTime)
                || interval <= Mathf.Epsilon
                ? 0f
                : 1f / interval;
            lastGestureTime = baseQuality
                ? unscaledTime
                : float.NegativeInfinity;
            float frequency = SpinnerComboRules.NormalizeFrequency(gesturesPerSecond);
            SpinnerComboTier tier = SpinnerComboRules.ResolveTier(
                speed,
                intensity,
                frequency);

            SpinnerComboSnapshot previous = snapshot;
            if (tier == SpinnerComboTier.None)
            {
                snapshot = SpinnerComboSnapshot.Rest;
                lastQualifiedTime = float.NegativeInfinity;
                lastCountPulseTime = float.NegativeInfinity;
                accumulatedCountPulseDegrees = 0f;
                return !snapshot.Equals(previous);
            }

            bool continues = !float.IsNegativeInfinity(lastQualifiedTime)
                && unscaledTime - lastQualifiedTime <= SpinnerComboRules.ComboTimeoutSeconds;
            if (!continues)
            {
                lastCountPulseTime = float.NegativeInfinity;
                accumulatedCountPulseDegrees = 0f;
            }
            int count = continues ? snapshot.Count + 1 : 2;
            lastQualifiedTime = unscaledTime;
            snapshot = new SpinnerComboSnapshot(
                tier,
                count,
                speed,
                intensity,
                frequency,
                SpinnerComboRules.ExperienceMultiplier(tier));
            return !snapshot.Equals(previous);
        }

        /// <summary>
        /// Converts real post-gesture mechanism travel into a faster visual
        /// count cadence. One pulse requires 120 degrees of actual rotary (or
        /// EDC-equivalent) travel and is capped at 6.25 Hz for legibility.
        /// It never awards XP, changes tier, or writes mechanism motion.
        /// </summary>
        public bool RecordMechanicalActivity(
            float unscaledTime,
            float absoluteActivityDegrees,
            float angularSpeedRadians)
        {
            if (!snapshot.IsActive
                || Mathf.Abs(angularSpeedRadians)
                    < SpinnerComboRules.MinimumCountPulseAngularSpeed)
            {
                accumulatedCountPulseDegrees = 0f;
                return false;
            }

            accumulatedCountPulseDegrees += Mathf.Max(
                0f,
                absoluteActivityDegrees);
            if (accumulatedCountPulseDegrees
                    < SpinnerComboRules.CountPulseDegrees
                || (!float.IsNegativeInfinity(lastCountPulseTime)
                    && unscaledTime - lastCountPulseTime
                        < SpinnerComboRules.MinimumCountPulseIntervalSeconds))
            {
                return false;
            }

            // This counter is presentation feedback, so discard excess travel
            // instead of queueing stale pulses behind a fast rotor.
            accumulatedCountPulseDegrees = 0f;
            lastCountPulseTime = unscaledTime;
            lastQualifiedTime = unscaledTime;
            snapshot = new SpinnerComboSnapshot(
                snapshot.Tier,
                snapshot.Count + 1,
                SpinnerComboRules.NormalizeSpeed(angularSpeedRadians),
                snapshot.NormalizedIntensity,
                snapshot.NormalizedFrequency,
                snapshot.ExperienceMultiplier);
            return true;
        }

        public bool Tick(float unscaledTime)
        {
            if (!snapshot.IsActive
                || unscaledTime - lastQualifiedTime <= SpinnerComboRules.ComboTimeoutSeconds)
            {
                return false;
            }

            Reset();
            return true;
        }

        public bool Reset()
        {
            bool changed = snapshot.IsActive;
            snapshot = SpinnerComboSnapshot.Rest;
            lastGestureTime = float.NegativeInfinity;
            lastQualifiedTime = float.NegativeInfinity;
            lastCountPulseTime = float.NegativeInfinity;
            accumulatedCountPulseDegrees = 0f;
            return changed;
        }
    }

    public enum SpinnerSpinRewardKind
    {
        None = 0,
        CleanSpin = 1,
        PowerSpin = 2,
        SpeedRun = 3,
        Endurance = 4,
        PerfectSpin = 5
    }

    public readonly struct SpinnerSpinRewardSnapshot
    {
        public SpinnerSpinRewardSnapshot(
            SpinnerSpinRewardKind kind,
            float normalizedForce,
            float peakAngularSpeedRadians,
            double revolutions)
        {
            Kind = kind;
            NormalizedForce = Mathf.Clamp01(normalizedForce);
            PeakAngularSpeedRadians = Mathf.Max(0f, peakAngularSpeedRadians);
            Revolutions = Math.Max(0d, revolutions);
        }

        public SpinnerSpinRewardKind Kind { get; }
        public float NormalizedForce { get; }
        public float PeakAngularSpeedRadians { get; }
        public double Revolutions { get; }
        public bool IsReward => Kind != SpinnerSpinRewardKind.None;

        public string Title
        {
            get
            {
                switch (Kind)
                {
                    case SpinnerSpinRewardKind.CleanSpin:
                        return "CLEAN SPIN";
                    case SpinnerSpinRewardKind.PowerSpin:
                        return "POWER SPIN";
                    case SpinnerSpinRewardKind.SpeedRun:
                        return "SPEED RUN";
                    case SpinnerSpinRewardKind.Endurance:
                        return "ENDURANCE";
                    case SpinnerSpinRewardKind.PerfectSpin:
                        return "PERFECT SPIN";
                    default:
                        return string.Empty;
                }
            }
        }

        public string Subtitle
        {
            get
            {
                switch (Kind)
                {
                    case SpinnerSpinRewardKind.CleanSpin:
                        return "干净起转";
                    case SpinnerSpinRewardKind.PowerSpin:
                        return "高力度启动";
                    case SpinnerSpinRewardKind.SpeedRun:
                        return "高速峰值";
                    case SpinnerSpinRewardKind.Endurance:
                        return "长程续转";
                    case SpinnerSpinRewardKind.PerfectSpin:
                        return "力度 × 速度 × 圈数";
                    default:
                        return string.Empty;
                }
            }
        }

        public static SpinnerSpinRewardSnapshot None => new SpinnerSpinRewardSnapshot(
            SpinnerSpinRewardKind.None,
            0f,
            0f,
            0d);
    }

    /// <summary>
    /// Read-only evaluation of one user-powered spin. It consumes the same
    /// explicit gesture, angular speed, and accumulated rotation already used
    /// by progression, but never writes to spinner physics or the XP economy.
    /// </summary>
    public static class SpinnerSpinRewardRules
    {
        public static SpinnerSpinRewardKind Resolve(
            float normalizedForce,
            float peakAngularSpeedRadians,
            double revolutions)
        {
            float force = Mathf.Clamp01(normalizedForce);
            float speed = SpinnerComboRules.NormalizeSpeed(peakAngularSpeedRadians);
            double turns = Math.Max(0d, revolutions);

            if (force >= 0.72f && speed >= 0.72f && turns >= 6d)
            {
                return SpinnerSpinRewardKind.PerfectSpin;
            }

            if (force >= 0.35f && speed >= 0.40f && turns >= 12d)
            {
                return SpinnerSpinRewardKind.Endurance;
            }

            if (force >= 0.50f && speed >= 0.86f && turns >= 4d)
            {
                return SpinnerSpinRewardKind.SpeedRun;
            }

            if (force >= 0.82f && speed >= 0.50f && turns >= 3d)
            {
                return SpinnerSpinRewardKind.PowerSpin;
            }

            if (force >= 0.35f && speed >= 0.30f && turns >= 2.5d)
            {
                return SpinnerSpinRewardKind.CleanSpin;
            }

            return SpinnerSpinRewardKind.None;
        }
    }

    /// <summary>
    /// Allocation-free live spin evaluator. It collects one final result while
    /// the spinner moves, then releases it only after two uninterrupted seconds
    /// at rest. A new explicit gesture cancels a pending result.
    /// </summary>
    public sealed class SpinnerSpinRewardRuntime
    {
        public const float RevealDelaySeconds = 2f;

        private bool armed;
        private bool pending;
        private float maximumForce;
        private float peakAngularSpeedRadians;
        private double revolutions;
        private float revealAt;
        private SpinnerSpinRewardSnapshot pendingReward =
            SpinnerSpinRewardSnapshot.None;

        public void RecordGesture(float normalizedForce, float angularSpeedRadians)
        {
            if (pending)
            {
                Reset();
            }

            armed = true;
            maximumForce = Mathf.Max(maximumForce, Mathf.Clamp01(normalizedForce));
            peakAngularSpeedRadians = Mathf.Max(
                peakAngularSpeedRadians,
                Mathf.Abs(angularSpeedRadians));
        }

        public void RecordRotation(double absoluteDegrees, float angularSpeedRadians)
        {
            if (!armed || absoluteDegrees <= 0d)
            {
                return;
            }

            revolutions += Math.Max(0d, absoluteDegrees) / 360d;
            peakAngularSpeedRadians = Mathf.Max(
                peakAngularSpeedRadians,
                Mathf.Abs(angularSpeedRadians));
        }

        public bool EndSpin(float unscaledTime)
        {
            if (!armed)
            {
                return false;
            }

            armed = false;
            SpinnerSpinRewardKind kind = SpinnerSpinRewardRules.Resolve(
                maximumForce,
                peakAngularSpeedRadians,
                revolutions);
            if (kind == SpinnerSpinRewardKind.None)
            {
                Reset();
                return false;
            }

            pendingReward = new SpinnerSpinRewardSnapshot(
                kind,
                maximumForce,
                peakAngularSpeedRadians,
                revolutions);
            pending = true;
            revealAt = unscaledTime + RevealDelaySeconds;
            return true;
        }

        public bool TryReveal(float unscaledTime, out SpinnerSpinRewardSnapshot reward)
        {
            reward = SpinnerSpinRewardSnapshot.None;
            if (!pending || unscaledTime < revealAt)
            {
                return false;
            }

            reward = pendingReward;
            Reset();
            return true;
        }

        public void Reset()
        {
            armed = false;
            pending = false;
            maximumForce = 0f;
            peakAngularSpeedRadians = 0f;
            revolutions = 0d;
            revealAt = 0f;
            pendingReward = SpinnerSpinRewardSnapshot.None;
        }
    }

    public readonly struct ComboHaloProjection
    {
        public ComboHaloProjection(
            float centerX,
            float centerY,
            float rotationDegrees,
            float minorAxisRatio)
        {
            CenterX = Mathf.Clamp01(centerX);
            CenterY = Mathf.Clamp01(centerY);
            RotationDegrees = Mathf.Clamp(rotationDegrees, -180f, 180f);
            MinorAxisRatio = Mathf.Clamp(minorAxisRatio, 0.18f, 1f);
        }

        public float CenterX { get; }
        public float CenterY { get; }
        public float RotationDegrees { get; }
        public float MinorAxisRatio { get; }
    }

    /// <summary>
    /// Projects a circle in the model's interaction plane into the native
    /// overlay. The resulting singular values describe the perspective ellipse
    /// without changing the underlying product, camera, physics, or input.
    /// </summary>
    public static class ComboHaloProjectionRules
    {
        public const float MinimumAxisRatio = 0.18f;

        public static bool TryProject(
            Camera camera,
            Vector3 modelCenterWorld,
            Vector3 planeNormalWorld,
            float sampleRadiusWorld,
            out ComboHaloProjection projection)
        {
            projection = default;
            if (camera == null
                || planeNormalWorld.sqrMagnitude <= 0.000001f
                || sampleRadiusWorld <= 0.000001f)
            {
                return false;
            }

            Vector3 normal = planeNormalWorld.normalized;
            Vector3 reference = Mathf.Abs(Vector3.Dot(
                    normal,
                    camera.transform.up)) < 0.95f
                ? camera.transform.up
                : camera.transform.right;
            Vector3 tangentU = Vector3.Cross(normal, reference).normalized;
            if (tangentU.sqrMagnitude <= 0.000001f)
            {
                return false;
            }
            Vector3 tangentV = Vector3.Cross(normal, tangentU).normalized;

            Vector3 centerViewport = camera.WorldToViewportPoint(modelCenterWorld);
            Vector3 sampleUViewport = camera.WorldToViewportPoint(
                modelCenterWorld + tangentU * sampleRadiusWorld);
            Vector3 sampleVViewport = camera.WorldToViewportPoint(
                modelCenterWorld + tangentV * sampleRadiusWorld);
            Vector2 viewportPixels = new Vector2(
                Mathf.Max(1f, camera.pixelWidth),
                Mathf.Max(1f, camera.pixelHeight));
            return TryResolveProjectedEllipse(
                centerViewport,
                sampleUViewport,
                sampleVViewport,
                viewportPixels,
                out projection);
        }

        public static bool TryResolveProjectedEllipse(
            Vector3 centerViewport,
            Vector3 sampleUViewport,
            Vector3 sampleVViewport,
            Vector2 viewportPixels,
            out ComboHaloProjection projection)
        {
            projection = default;
            if (centerViewport.z <= 0f
                || sampleUViewport.z <= 0f
                || sampleVViewport.z <= 0f
                || viewportPixels.x <= 0f
                || viewportPixels.y <= 0f)
            {
                return false;
            }

            // SwiftUI's screen Y grows downward, so flip the Unity viewport Y
            // before deriving the ellipse angle.
            Vector2 axisU = new Vector2(
                (sampleUViewport.x - centerViewport.x) * viewportPixels.x,
                -(sampleUViewport.y - centerViewport.y) * viewportPixels.y);
            Vector2 axisV = new Vector2(
                (sampleVViewport.x - centerViewport.x) * viewportPixels.x,
                -(sampleVViewport.y - centerViewport.y) * viewportPixels.y);

            float xx = axisU.x * axisU.x + axisV.x * axisV.x;
            float xy = axisU.x * axisU.y + axisV.x * axisV.y;
            float yy = axisU.y * axisU.y + axisV.y * axisV.y;
            float trace = xx + yy;
            float discriminant = Mathf.Sqrt(Mathf.Max(
                0f,
                (xx - yy) * (xx - yy) + 4f * xy * xy));
            float majorSquared = 0.5f * (trace + discriminant);
            float minorSquared = 0.5f * (trace - discriminant);
            if (majorSquared <= 0.000001f)
            {
                return false;
            }

            float minorAxisRatio = Mathf.Sqrt(
                Mathf.Max(0f, minorSquared) / majorSquared);
            float rotationDegrees = 0.5f
                * Mathf.Atan2(2f * xy, xx - yy)
                * Mathf.Rad2Deg;
            projection = new ComboHaloProjection(
                centerViewport.x,
                1f - centerViewport.y,
                rotationDegrees,
                Mathf.Max(MinimumAxisRatio, minorAxisRatio));
            return true;
        }
    }

    public static class ComboHaloProjectionNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexComboHaloReceiveProjection(
            int available,
            float centerX,
            float centerY,
            float rotationDegrees,
            float minorAxisRatio);
#endif

        public static void Publish(ComboHaloProjection projection)
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexComboHaloReceiveProjection(
                1,
                projection.CenterX,
                projection.CenterY,
                projection.RotationDegrees,
                projection.MinorAxisRatio);
#endif
        }

        public static void Clear()
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexComboHaloReceiveProjection(0, 0.5f, 0.5f, 0f, 1f);
#endif
        }
    }

    public static class SpinnerComboNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexComboReceiveState(
            int tier,
            int count,
            string title,
            float normalizedSpeed,
            float angularSpeedRadians,
            float normalizedIntensity,
            float normalizedFrequency,
            float experienceMultiplier);
#endif

        public static void Publish(
            SpinnerComboSnapshot snapshot,
            float angularSpeedRadians = 0f)
        {
#if UNITY_IOS && !UNITY_EDITOR
            float liveAngularSpeed = snapshot.IsActive
                ? Mathf.Abs(angularSpeedRadians)
                : 0f;
            CodexComboReceiveState(
                (int)snapshot.Tier,
                snapshot.Count,
                snapshot.Title,
                SpinnerComboRules.NormalizeSpeed(liveAngularSpeed),
                liveAngularSpeed,
                snapshot.NormalizedIntensity,
                snapshot.NormalizedFrequency,
                snapshot.ExperienceMultiplier);
#endif
        }
    }

    public enum ProductMotionTelemetryKind
    {
        Rotary = 0,
        LinearPush = 1,
        FanCard = 2
    }

    public static class ProductMotionTelemetryNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexMotionTelemetryReceiveState(
            int available,
            int kind,
            float normalizedSpeed,
            float motionRate,
            int speedBand,
            float normalizedIntensity,
            float normalizedFrequency);
#endif

        public static void Publish(
            bool available,
            float angularSpeedRadians,
            SpinnerSpeedBand speedBand)
        {
            Publish(
                available,
                ProductMotionTelemetryKind.Rotary,
                SpinnerComboRules.NormalizeSpeed(angularSpeedRadians),
                Mathf.Abs(angularSpeedRadians),
                speedBand,
                0f,
                0f);
        }

        public static void Publish(
            bool available,
            ProductMotionTelemetryKind kind,
            float normalizedSpeed,
            float motionRate,
            SpinnerSpeedBand speedBand,
            float normalizedIntensity,
            float normalizedFrequency)
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexMotionTelemetryReceiveState(
                available ? 1 : 0,
                (int)kind,
                available ? Mathf.Clamp01(normalizedSpeed) : 0f,
                available ? Mathf.Max(0f, motionRate) : 0f,
                (int)(available ? speedBand : SpinnerSpeedBand.Calm),
                available ? Mathf.Clamp01(normalizedIntensity) : 0f,
                available ? Mathf.Clamp01(normalizedFrequency) : 0f);
#endif
        }

        public static void Clear()
        {
            Publish(false, 0f, SpinnerSpeedBand.Calm);
        }
    }

    public static class SpinnerSpinRewardNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexSpinRewardReceiveState(
            int kind,
            string title,
            string subtitle,
            float normalizedForce,
            float peakAngularSpeedRadians,
            float revolutions);
#endif

        public static void Publish(SpinnerSpinRewardSnapshot reward)
        {
#if UNITY_IOS && !UNITY_EDITOR
            if (!reward.IsReward)
            {
                return;
            }

            CodexSpinRewardReceiveState(
                (int)reward.Kind,
                reward.Title,
                reward.Subtitle,
                reward.NormalizedForce,
                reward.PeakAngularSpeedRadians,
                (float)reward.Revolutions);
#endif
        }

        public static void Clear()
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexSpinRewardReceiveState(
                0,
                string.Empty,
                string.Empty,
                0f,
                0f,
                0f);
#endif
        }
    }
}
