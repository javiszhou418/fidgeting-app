using System;
using System.Runtime.InteropServices;
using UnityEngine;

namespace CodexUnityLab
{
    /// <summary>
    /// App-level phases for the speed-dependent spinner texture. These describe
    /// the mechanism/rendering policy and are not Core Haptics event types.
    /// </summary>
    public enum HapticSpeedTextureBand
    {
        Rest = 0,
        DiscreteDetents = 1,
        BearingContinuous = 2
    }

    public enum HapticSpeedTextureAction
    {
        None = 0,
        StartContinuous = 1,
        UpdateContinuous = 2,
        StopContinuous = 3
    }

    /// <summary>
    /// Versioned product recipe for mapping actual rotor speed to perceived
    /// texture. Rates are mechanical detents per second, never Taptic Engine Hz.
    /// </summary>
    public readonly struct HapticSpeedTextureProfile
    {
        public const int CurrentVersion = 1;

        public HapticSpeedTextureProfile(
            bool enabled,
            float enterContinuousDetentsPerSecond,
            float exitContinuousDetentsPerSecond,
            float fullScaleAngularSpeed,
            float slowDetentIntensityGain,
            float fastDetentIntensityGain,
            float minimumContinuousIntensity,
            float maximumContinuousIntensity,
            float minimumContinuousSharpness,
            float maximumContinuousSharpness,
            float responseExponent,
            float updateRateHz,
            float attack,
            float releaseSeconds)
        {
            Enabled = enabled;
            EnterContinuousDetentsPerSecond = Mathf.Clamp(
                FiniteOr(enterContinuousDetentsPerSecond, 30f),
                4f,
                80f);
            ExitContinuousDetentsPerSecond = Mathf.Clamp(
                FiniteOr(exitContinuousDetentsPerSecond, 27f),
                2f,
                EnterContinuousDetentsPerSecond - 0.5f);
            FullScaleAngularSpeed = Mathf.Clamp(
                FiniteOr(
                    fullScaleAngularSpeed,
                    global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed),
                1f,
                80f);
            SlowDetentIntensityGain = Mathf.Clamp01(
                FiniteOr(slowDetentIntensityGain, 1f));
            FastDetentIntensityGain = Mathf.Clamp01(
                FiniteOr(fastDetentIntensityGain, 0.42f));

            float minimumIntensity = Mathf.Clamp01(
                FiniteOr(minimumContinuousIntensity, 0.06f));
            float maximumIntensity = Mathf.Clamp01(
                FiniteOr(maximumContinuousIntensity, 0.16f));
            MinimumContinuousIntensity = Mathf.Min(minimumIntensity, maximumIntensity);
            MaximumContinuousIntensity = Mathf.Max(minimumIntensity, maximumIntensity);

            float minimumSharpness = Mathf.Clamp01(
                FiniteOr(minimumContinuousSharpness, 0.28f));
            float maximumSharpness = Mathf.Clamp01(
                FiniteOr(maximumContinuousSharpness, 0.48f));
            MinimumContinuousSharpness = Mathf.Min(minimumSharpness, maximumSharpness);
            MaximumContinuousSharpness = Mathf.Max(minimumSharpness, maximumSharpness);

            ResponseExponent = Mathf.Clamp(FiniteOr(responseExponent, 0.75f), 0.2f, 3f);
            UpdateRateHz = Mathf.Clamp(FiniteOr(updateRateHz, 30f), 10f, 60f);
            Attack = Mathf.Clamp01(FiniteOr(attack, 0.04f));
            ReleaseSeconds = Mathf.Clamp(FiniteOr(releaseSeconds, 0.10f), 0f, 1f);
        }

        public bool Enabled { get; }
        public float EnterContinuousDetentsPerSecond { get; }
        public float ExitContinuousDetentsPerSecond { get; }
        public float FullScaleAngularSpeed { get; }
        public float SlowDetentIntensityGain { get; }
        public float FastDetentIntensityGain { get; }
        public float MinimumContinuousIntensity { get; }
        public float MaximumContinuousIntensity { get; }
        public float MinimumContinuousSharpness { get; }
        public float MaximumContinuousSharpness { get; }
        public float ResponseExponent { get; }
        public float UpdateRateHz { get; }

        /// <summary>
        /// Normalized Core Haptics attack parameter, not seconds.
        /// </summary>
        public float Attack { get; }

        /// <summary>
        /// Real fade time used by the native parameter curve when stopping.
        /// </summary>
        public float ReleaseSeconds { get; }

        public static HapticSpeedTextureProfile Recommended => new HapticSpeedTextureProfile(
            true,
            30f,
            27f,
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed,
            1f,
            1f,
            0f,
            1f,
            0f,
            1f,
            1f,
            30f,
            0.025f,
            0.040f);

        private static float FiniteOr(float value, float fallback)
        {
            return float.IsNaN(value) || float.IsInfinity(value) ? fallback : value;
        }
    }

    public readonly struct HapticSpeedTextureSample
    {
        public HapticSpeedTextureSample(
            HapticSpeedTextureBand band,
            HapticSpeedTextureAction action,
            float angularSpeedRadians,
            float detentsPerSecond,
            float normalizedSpeed,
            float detentIntensityGain,
            float continuousIntensity,
            float continuousSharpness,
            bool suppressDetentTransients)
        {
            Band = band;
            Action = action;
            AngularSpeedRadians = angularSpeedRadians;
            DetentsPerSecond = detentsPerSecond;
            NormalizedSpeed = normalizedSpeed;
            DetentIntensityGain = detentIntensityGain;
            ContinuousIntensity = continuousIntensity;
            ContinuousSharpness = continuousSharpness;
            SuppressDetentTransients = suppressDetentTransients;
        }

        public HapticSpeedTextureBand Band { get; }
        public HapticSpeedTextureAction Action { get; }
        public float AngularSpeedRadians { get; }
        public float DetentsPerSecond { get; }
        public float NormalizedSpeed { get; }
        public float DetentIntensityGain { get; }
        public float ContinuousIntensity { get; }
        public float ContinuousSharpness { get; }
        public bool SuppressDetentTransients { get; }

        public static HapticSpeedTextureSample Rest => new HapticSpeedTextureSample(
            HapticSpeedTextureBand.Rest,
            HapticSpeedTextureAction.None,
            0f,
            0f,
            0f,
            1f,
            0f,
            0f,
            false);
    }

    /// <summary>
    /// Deterministic hysteresis and update-throttling state machine. It never
    /// writes to a Rigidbody; it only translates a mechanism sample into an
    /// output policy for the semantic haptic router.
    /// </summary>
    public sealed class HapticSpeedTextureStateMachine
    {
        private const float RestAngularSpeed = 0.02f;

        private bool continuousActive;
        private double lastContinuousUpdateTime = double.NegativeInfinity;

        public bool ContinuousActive => continuousActive;

        public HapticSpeedTextureSample Step(
            float angularSpeedRadians,
            int detentsPerTurn,
            double unscaledTime,
            bool outputAllowed,
            HapticSpeedTextureProfile profile)
        {
            return Step(
                angularSpeedRadians,
                detentsPerTurn,
                unscaledTime,
                outputAllowed,
                profile,
                DetentFeelPresetCatalog.Default.Config);
        }

        public HapticSpeedTextureSample Step(
            float angularSpeedRadians,
            int detentsPerTurn,
            double unscaledTime,
            bool outputAllowed,
            HapticSpeedTextureProfile profile,
            DetentFeelConfig detentFeel)
        {
            float finiteSpeed = float.IsNaN(angularSpeedRadians)
                || float.IsInfinity(angularSpeedRadians)
                    ? 0f
                    : angularSpeedRadians;
            float absoluteSpeed = Mathf.Abs(finiteSpeed);
            float detentRate = DetentsPerSecond(finiteSpeed, detentsPerTurn);
            float normalizedSpeed = Mathf.Pow(
                Mathf.Clamp01(absoluteSpeed / profile.FullScaleAngularSpeed),
                profile.ResponseExponent);
            float detentGain = 1f;
            float continuousIntensity = normalizedSpeed * detentFeel.Intensity;
            float continuousSharpness = detentFeel.Sharpness;

            bool isResting = absoluteSpeed < RestAngularSpeed;
            bool wantsContinuous = outputAllowed && profile.Enabled && !isResting
                && (continuousActive
                    ? detentRate > profile.ExitContinuousDetentsPerSecond
                    : detentRate >= profile.EnterContinuousDetentsPerSecond);

            HapticSpeedTextureAction action = HapticSpeedTextureAction.None;
            if (wantsContinuous && !continuousActive)
            {
                continuousActive = true;
                lastContinuousUpdateTime = unscaledTime;
                action = HapticSpeedTextureAction.StartContinuous;
            }
            else if (!wantsContinuous && continuousActive)
            {
                continuousActive = false;
                lastContinuousUpdateTime = double.NegativeInfinity;
                action = HapticSpeedTextureAction.StopContinuous;
            }
            else if (continuousActive
                && unscaledTime - lastContinuousUpdateTime >= 1.0 / profile.UpdateRateHz)
            {
                lastContinuousUpdateTime = unscaledTime;
                action = HapticSpeedTextureAction.UpdateContinuous;
            }

            if (continuousActive
                && detentRate < profile.EnterContinuousDetentsPerSecond)
            {
                float fade = Mathf.InverseLerp(
                    profile.ExitContinuousDetentsPerSecond,
                    profile.EnterContinuousDetentsPerSecond,
                    detentRate);
                continuousIntensity = Mathf.Min(
                    0.05f,
                    continuousIntensity * fade);
            }

            HapticSpeedTextureBand band = isResting
                ? HapticSpeedTextureBand.Rest
                : (continuousActive
                    ? HapticSpeedTextureBand.BearingContinuous
                    : HapticSpeedTextureBand.DiscreteDetents);
            return new HapticSpeedTextureSample(
                band,
                action,
                finiteSpeed,
                detentRate,
                normalizedSpeed,
                detentGain,
                continuousIntensity,
                continuousSharpness,
                continuousActive
                    && detentRate >= profile.EnterContinuousDetentsPerSecond);
        }

        public bool ForceStop()
        {
            bool wasActive = continuousActive;
            continuousActive = false;
            lastContinuousUpdateTime = double.NegativeInfinity;
            return wasActive;
        }

        public static float DetentsPerSecond(float angularSpeedRadians, int detentsPerTurn)
        {
            if (float.IsNaN(angularSpeedRadians) || float.IsInfinity(angularSpeedRadians))
            {
                return 0f;
            }

            return Mathf.Abs(angularSpeedRadians)
                * Mathf.Clamp(detentsPerTurn, 1, 120)
                / (2f * Mathf.PI);
        }
    }

    public readonly struct FidgetHapticTelemetry
    {
        public FidgetHapticTelemetry(
            HapticSpeedTextureSample speedTexture,
            int renderedEventCount,
            int suppressedEventCount,
            FidgetSemanticEvent lastSemanticEvent,
            int nativeStatus)
        {
            SpeedTexture = speedTexture;
            RenderedEventCount = renderedEventCount;
            SuppressedEventCount = suppressedEventCount;
            LastSemanticEvent = lastSemanticEvent;
            NativeStatus = nativeStatus;
        }

        public HapticSpeedTextureSample SpeedTexture { get; }
        public int RenderedEventCount { get; }
        public int SuppressedEventCount { get; }
        public FidgetSemanticEvent LastSemanticEvent { get; }
        public int NativeStatus { get; }
    }

    public static class HapticLabTelemetryBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexHapticLabReceiveTelemetry(
            float angularSpeedRadians,
            float rpm,
            float detentsPerSecond,
            float detentIntensityGain,
            float continuousIntensity,
            float continuousSharpness,
            int speedBand,
            int continuousActive,
            int renderedEventCount,
            int suppressedEventCount,
            int lastSemanticEvent,
            int nativeStatus);
#endif

        public static void Publish(FidgetHapticTelemetry telemetry)
        {
#if UNITY_IOS && !UNITY_EDITOR
            HapticSpeedTextureSample sample = telemetry.SpeedTexture;
            CodexHapticLabReceiveTelemetry(
                sample.AngularSpeedRadians,
                Mathf.Abs(sample.AngularSpeedRadians) * 60f / (2f * Mathf.PI),
                sample.DetentsPerSecond,
                sample.DetentIntensityGain,
                sample.ContinuousIntensity,
                sample.ContinuousSharpness,
                (int)sample.Band,
                sample.SuppressDetentTransients ? 1 : 0,
                telemetry.RenderedEventCount,
                telemetry.SuppressedEventCount,
                (int)telemetry.LastSemanticEvent,
                telemetry.NativeStatus);
#endif
        }
    }
}
