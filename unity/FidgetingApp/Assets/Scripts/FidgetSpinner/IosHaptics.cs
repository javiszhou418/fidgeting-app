using System.Runtime.InteropServices;
using UnityEngine;

namespace CodexUnityLab
{
    public enum IosHapticImpactStyle
    {
        Light = 0,
        Medium = 1,
        Heavy = 2,
        Soft = 3,
        Rigid = 4
    }

    public enum IosSystemHapticPreset
    {
        Selection = 0,
        ImpactLight = 1,
        ImpactMedium = 2,
        ImpactHeavy = 3,
        ImpactSoft = 4,
        ImpactRigid = 5,
        NotificationSuccess = 6,
        NotificationWarning = 7,
        NotificationError = 8
    }

    /// <summary>
    /// Product-level rhythm. The user chooses a recognizable cadence while
    /// individual semantic recipes keep ownership of their mechanical identity.
    /// </summary>
    public enum FidgetHapticRhythm
    {
        Single = 0,
        Double = 1,
        Burst = 2
    }

    public enum FidgetHapticWaveform
    {
        Transient = 0,
        Continuous = 1,
        Hybrid = 2
    }

    /// <summary>
    /// Mechanical meanings emitted by a fidget mechanism. These are app
    /// semantics, not Core Haptics event types.
    /// </summary>
    public enum FidgetSemanticEvent
    {
        Selection = 0,
        DetentCrossed = 1,
        Breakaway = 2,
        DetentCaptured = 3,
        Released = 4,
        DirectionReversed = 5,
        Reset = 6,
        ShakeBurst = 7,
        ButtonPressed = 8,
        ButtonReleased = 9,
        Pop = 10,
        Collision = 11,
        Preview = 12,
        InertiaShift = 13,
        MagneticEdgeProbe = 14,
        BadgeUnlocked = 15,
        /// <summary>
        /// The phone body crossed one detent of the Device Twist dial. This
        /// is a mechanism event from <c>DeviceTwistDial</c>, not a rotor detent.
        /// </summary>
        TwistDetentCrossed = 16
    }

    /// <summary>
    /// Isolated-transient values for the Device Twist dial. Softer than the
    /// rotor ratchet so the two tick sources stay distinguishable on device.
    /// </summary>
    public static class DeviceTwistHapticRecipe
    {
        public const float MinimumIntensity = 0.34f;
        public const float MaximumIntensity = 0.62f;
        public const float Sharpness = 0.56f;

        public static float ResolveIntensity(float normalizedRate)
        {
            return Mathf.Lerp(
                MinimumIntensity,
                MaximumIntensity,
                Mathf.Clamp01(normalizedRate));
        }
    }

    /// <summary>
    /// Product-level master controls applied above each semantic recipe.
    /// FrequencyFeel is perceived crispness/sharpness, not Hz. Physical decay,
    /// detent count, and ratchet strength live in the mechanism profile and are
    /// applied by FidgetAppCoordinator.
    /// </summary>
    public readonly struct FidgetHapticSettings
    {
        public FidgetHapticSettings(
            bool enabled,
            float intensity,
            float frequencyFeel,
            FidgetHapticRhythm rhythm,
            float speedFollow,
            int detentsPerTurn)
        {
            Enabled = enabled;
            Intensity = Mathf.Clamp01(intensity);
            FrequencyFeel = Mathf.Clamp01(frequencyFeel);
            Rhythm = rhythm;
            SpeedFollow = Mathf.Clamp01(speedFollow);
            DetentsPerTurn = Mathf.Clamp(detentsPerTurn, 1, 120);
        }

        public bool Enabled { get; }
        public float Intensity { get; }
        public float FrequencyFeel { get; }
        public FidgetHapticRhythm Rhythm { get; }
        public float SpeedFollow { get; }
        public int DetentsPerTurn { get; }

        public static FidgetHapticSettings Recommended => new FidgetHapticSettings(
            true,
            0.95f,
            0.88f,
            FidgetHapticRhythm.Single,
            0.35f,
            24);
    }

    /// <summary>
    /// Fully resolved haptic tuning owned by the linear magnetic mechanism.
    /// Values are final product values and do not inherit rotary detent presets.
    /// </summary>
    public readonly struct MagneticSliderHapticTuning
    {
        public MagneticSliderHapticTuning(
            float edgeMinimumIntensity,
            float edgeMaximumIntensity,
            float edgeMinimumSharpness,
            float edgeMaximumSharpness,
            float edgePulseDurationSeconds,
            float crossingPrimaryIntensity,
            float crossingPrimarySharpness,
            float crossingBodyIntensity,
            float crossingBodySharpness,
            float crossingBodyDurationSeconds,
            float crossingSecondaryIntensity,
            float crossingSecondarySharpness,
            float crossingPulseIntervalSeconds)
        {
            EdgeMinimumIntensity = Mathf.Clamp01(edgeMinimumIntensity);
            EdgeMaximumIntensity = Mathf.Clamp01(edgeMaximumIntensity);
            EdgeMinimumSharpness = Mathf.Clamp01(edgeMinimumSharpness);
            EdgeMaximumSharpness = Mathf.Clamp01(edgeMaximumSharpness);
            EdgePulseDurationSeconds = Mathf.Clamp(edgePulseDurationSeconds, 0.005f, 0.080f);
            CrossingPrimaryIntensity = Mathf.Clamp01(crossingPrimaryIntensity);
            CrossingPrimarySharpness = Mathf.Clamp01(crossingPrimarySharpness);
            CrossingBodyIntensity = Mathf.Clamp01(crossingBodyIntensity);
            CrossingBodySharpness = Mathf.Clamp01(crossingBodySharpness);
            CrossingBodyDurationSeconds = Mathf.Clamp(
                crossingBodyDurationSeconds,
                0.010f,
                0.080f);
            CrossingSecondaryIntensity = Mathf.Clamp01(crossingSecondaryIntensity);
            CrossingSecondarySharpness = Mathf.Clamp01(crossingSecondarySharpness);
            CrossingPulseIntervalSeconds = Mathf.Clamp(
                crossingPulseIntervalSeconds,
                0.010f,
                0.080f);
        }

        public float EdgeMinimumIntensity { get; }
        public float EdgeMaximumIntensity { get; }
        public float EdgeMinimumSharpness { get; }
        public float EdgeMaximumSharpness { get; }
        public float EdgePulseDurationSeconds { get; }
        public float CrossingPrimaryIntensity { get; }
        public float CrossingPrimarySharpness { get; }
        public float CrossingBodyIntensity { get; }
        public float CrossingBodySharpness { get; }
        public float CrossingBodyDurationSeconds { get; }
        public float CrossingSecondaryIntensity { get; }
        public float CrossingSecondarySharpness { get; }
        public float CrossingPulseIntervalSeconds { get; }
    }

    /// <summary>
    /// Final fan-card crossing values. They remain independent from rotary
    /// detent presets so a four-step card keeps its authored tactile contrast.
    /// </summary>
    public readonly struct FanCardHapticTuning
    {
        public FanCardHapticTuning(
            float minimumIntensity,
            float maximumIntensity,
            float minimumSharpness,
            float maximumSharpness,
            float bodyIntensity,
            float bodySharpness,
            float bodyDurationSeconds,
            float tailIntensity,
            float tailSharpness,
            float tailDelaySeconds)
        {
            MinimumIntensity = Mathf.Clamp01(minimumIntensity);
            MaximumIntensity = Mathf.Clamp(
                maximumIntensity,
                MinimumIntensity,
                1f);
            MinimumSharpness = Mathf.Clamp01(minimumSharpness);
            MaximumSharpness = Mathf.Clamp(
                maximumSharpness,
                MinimumSharpness,
                1f);
            BodyIntensity = Mathf.Clamp01(bodyIntensity);
            BodySharpness = Mathf.Clamp01(bodySharpness);
            BodyDurationSeconds = Mathf.Clamp(bodyDurationSeconds, 0.010f, 0.080f);
            TailIntensity = Mathf.Clamp01(tailIntensity);
            TailSharpness = Mathf.Clamp01(tailSharpness);
            TailDelaySeconds = Mathf.Clamp(tailDelaySeconds, 0.010f, 0.080f);
        }

        public float MinimumIntensity { get; }
        public float MaximumIntensity { get; }
        public float MinimumSharpness { get; }
        public float MaximumSharpness { get; }
        public float BodyIntensity { get; }
        public float BodySharpness { get; }
        public float BodyDurationSeconds { get; }
        public float TailIntensity { get; }
        public float TailSharpness { get; }
        public float TailDelaySeconds { get; }
    }

    /// <summary>
    /// Fully resolved low-level recipe sent to the iOS renderer. The native
    /// editor can override these values per semantic event without bypassing
    /// the input -> mechanism -> semantic event -> recipe -> renderer pipeline.
    /// </summary>
    public readonly struct HapticRecipe
    {
        public HapticRecipe(
            FidgetSemanticEvent semanticEvent,
            FidgetHapticWaveform waveform,
            float intensity,
            float sharpness,
            float duration,
            float attack,
            float decay,
            float release,
            bool sustained,
            float endIntensity,
            float endSharpness,
            int pulseCount,
            float pulseInterval,
            float impactLayers,
            float dynamicIntensity,
            float dynamicSharpness,
            float dynamicAttack,
            float dynamicDecay,
            float dynamicRelease)
        {
            SemanticEvent = semanticEvent;
            Waveform = waveform;
            Intensity = Mathf.Clamp01(intensity);
            Sharpness = Mathf.Clamp01(sharpness);
            Duration = Mathf.Clamp(duration, 0.01f, 5f);
            Attack = Mathf.Clamp01(attack);
            Decay = Mathf.Clamp01(decay);
            Release = Mathf.Clamp01(release);
            Sustained = sustained;
            EndIntensity = Mathf.Clamp01(endIntensity);
            EndSharpness = Mathf.Clamp01(endSharpness);
            PulseCount = Mathf.Clamp(pulseCount, 1, 12);
            PulseInterval = Mathf.Clamp(pulseInterval, 0.01f, 0.5f);
            ImpactLayers = Mathf.Clamp(impactLayers, 1f, 4f);
            DynamicIntensity = Mathf.Clamp01(dynamicIntensity);
            DynamicSharpness = Mathf.Clamp(dynamicSharpness, -1f, 1f);
            DynamicAttack = Mathf.Clamp(dynamicAttack, -1f, 1f);
            DynamicDecay = Mathf.Clamp(dynamicDecay, -1f, 1f);
            DynamicRelease = Mathf.Clamp(dynamicRelease, -1f, 1f);
        }

        public FidgetSemanticEvent SemanticEvent { get; }
        public FidgetHapticWaveform Waveform { get; }
        public float Intensity { get; }
        public float Sharpness { get; }
        public float Duration { get; }
        public float Attack { get; }
        public float Decay { get; }
        public float Release { get; }
        public bool Sustained { get; }
        public float EndIntensity { get; }
        public float EndSharpness { get; }
        public int PulseCount { get; }
        public float PulseInterval { get; }
        public float ImpactLayers { get; }
        public float DynamicIntensity { get; }
        public float DynamicSharpness { get; }
        public float DynamicAttack { get; }
        public float DynamicDecay { get; }
        public float DynamicRelease { get; }
    }

    public readonly struct HapticRecipeOverride
    {
        public HapticRecipeOverride(
            FidgetHapticWaveform waveform,
            float intensity,
            float sharpness,
            float duration,
            float attack,
            float decay,
            float release,
            bool sustained,
            float endIntensity,
            float endSharpness,
            int pulseCount,
            float pulseInterval,
            float impactLayers,
            float dynamicIntensity,
            float dynamicSharpness,
            float dynamicAttack,
            float dynamicDecay,
            float dynamicRelease)
        {
            Waveform = waveform;
            Intensity = Mathf.Clamp01(intensity);
            Sharpness = Mathf.Clamp01(sharpness);
            Duration = Mathf.Clamp(duration, 0.01f, 5f);
            Attack = Mathf.Clamp01(attack);
            Decay = Mathf.Clamp01(decay);
            Release = Mathf.Clamp01(release);
            Sustained = sustained;
            EndIntensity = Mathf.Clamp01(endIntensity);
            EndSharpness = Mathf.Clamp01(endSharpness);
            PulseCount = Mathf.Clamp(pulseCount, 1, 12);
            PulseInterval = Mathf.Clamp(pulseInterval, 0.01f, 0.5f);
            ImpactLayers = Mathf.Clamp(impactLayers, 1f, 4f);
            DynamicIntensity = Mathf.Clamp01(dynamicIntensity);
            DynamicSharpness = Mathf.Clamp(dynamicSharpness, -1f, 1f);
            DynamicAttack = Mathf.Clamp(dynamicAttack, -1f, 1f);
            DynamicDecay = Mathf.Clamp(dynamicDecay, -1f, 1f);
            DynamicRelease = Mathf.Clamp(dynamicRelease, -1f, 1f);
        }

        public FidgetHapticWaveform Waveform { get; }
        public float Intensity { get; }
        public float Sharpness { get; }
        public float Duration { get; }
        public float Attack { get; }
        public float Decay { get; }
        public float Release { get; }
        public bool Sustained { get; }
        public float EndIntensity { get; }
        public float EndSharpness { get; }
        public int PulseCount { get; }
        public float PulseInterval { get; }
        public float ImpactLayers { get; }
        public float DynamicIntensity { get; }
        public float DynamicSharpness { get; }
        public float DynamicAttack { get; }
        public float DynamicDecay { get; }
        public float DynamicRelease { get; }
    }

    public static class FidgetHapticRecipeLibrary
    {
        private static readonly System.Collections.Generic.Dictionary<
            FidgetSemanticEvent,
            HapticRecipeOverride> Overrides = new();

        public static void SetOverride(
            FidgetSemanticEvent semanticEvent,
            HapticRecipeOverride recipeOverride)
        {
            Overrides[semanticEvent] = recipeOverride;
        }

        public static void ClearOverride(FidgetSemanticEvent semanticEvent)
        {
            Overrides.Remove(semanticEvent);
        }

        public static void ClearOverrides()
        {
            Overrides.Clear();
        }

        public static HapticRecipe Resolve(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal,
            FidgetHapticSettings settings)
        {
            float signal = Mathf.Clamp01(normalizedSignal);
            FidgetHapticWaveform waveform = FidgetHapticWaveform.Transient;
            float baseIntensity;
            float baseSharpness;
            float endIntensity;
            float endSharpness;
            float duration = 0.04f;
            float attack = 0f;
            float decay = 0.04f;
            float release = 0.03f;
            bool sustained = false;
            int pulseCount = 1;
            float pulseInterval = 0.04f;
            float impactLayers = 1f;
            float dynamicIntensity = 1f;
            float dynamicSharpness = 0f;
            float dynamicAttack = 0f;
            float dynamicDecay = 0f;
            float dynamicRelease = 0f;
            bool followsSpeed = false;
            float speedMinimumGain = 1f;
            bool acceptsProductRhythm = false;
            bool usesFinalIsolatedValues = false;

            switch (semanticEvent)
            {
                case FidgetSemanticEvent.Selection:
                    baseIntensity = 0.40f;
                    baseSharpness = 0.88f;
                    endIntensity = baseIntensity;
                    endSharpness = baseSharpness;
                    break;
                case FidgetSemanticEvent.DetentCrossed:
                    DetentFeelConfig detent =
                        DetentFeelPresetCatalog.Default.Config;
                    baseIntensity = detent.Intensity;
                    baseSharpness = detent.Sharpness;
                    endIntensity = baseIntensity;
                    endSharpness = baseSharpness;
                    impactLayers = 1f;
                    usesFinalIsolatedValues = true;
                    break;
                case FidgetSemanticEvent.Breakaway:
                    baseIntensity = 0.78f;
                    baseSharpness = 0.94f;
                    endIntensity = 0.34f;
                    endSharpness = 0.68f;
                    impactLayers = 1.55f;
                    break;
                case FidgetSemanticEvent.DetentCaptured:
                    waveform = FidgetHapticWaveform.Hybrid;
                    baseIntensity = 0.95f;
                    baseSharpness = 0.90f;
                    endIntensity = 0.42f;
                    endSharpness = 0.58f;
                    duration = 0.055f;
                    decay = 0.08f;
                    pulseCount = 2;
                    pulseInterval = 0.036f;
                    impactLayers = 1.75f;
                    break;
                case FidgetSemanticEvent.Released:
                    baseIntensity = 0.55f;
                    baseSharpness = 0.62f;
                    endIntensity = 0.24f;
                    endSharpness = 0.38f;
                    release = 0.06f;
                    break;
                case FidgetSemanticEvent.DirectionReversed:
                    baseIntensity = 0.82f;
                    baseSharpness = 0.82f;
                    endIntensity = 0.30f;
                    endSharpness = 0.44f;
                    pulseCount = 3;
                    pulseInterval = 0.045f;
                    impactLayers = 1.55f;
                    break;
                case FidgetSemanticEvent.Reset:
                    baseIntensity = 0.84f;
                    baseSharpness = 0.94f;
                    endIntensity = 0.22f;
                    endSharpness = 1f;
                    pulseCount = 2;
                    pulseInterval = 0.032f;
                    impactLayers = 1.45f;
                    break;
                case FidgetSemanticEvent.ShakeBurst:
                    baseIntensity = 0.72f;
                    baseSharpness = 0.92f;
                    endIntensity = 0.42f;
                    endSharpness = 0.76f;
                    pulseCount = 3;
                    pulseInterval = 0.034f;
                    impactLayers = 1.2f;
                    followsSpeed = true;
                    speedMinimumGain = 0.38f / 0.72f;
                    break;
                case FidgetSemanticEvent.InertiaShift:
                    baseIntensity = Mathf.Lerp(0.25f, 0.40f, signal);
                    baseSharpness = Mathf.Lerp(0.20f, 0.35f, signal);
                    endIntensity = baseIntensity;
                    endSharpness = baseSharpness;
                    usesFinalIsolatedValues = true;
                    break;
                case FidgetSemanticEvent.MagneticEdgeProbe:
                    baseIntensity = Mathf.Lerp(0.08f, 0.14f, signal);
                    baseSharpness = Mathf.Lerp(0.14f, 0.22f, signal);
                    endIntensity = baseIntensity;
                    endSharpness = baseSharpness;
                    duration = 0.012f;
                    usesFinalIsolatedValues = true;
                    break;
                case FidgetSemanticEvent.TwistDetentCrossed:
                    baseIntensity = DeviceTwistHapticRecipe.ResolveIntensity(signal);
                    baseSharpness = DeviceTwistHapticRecipe.Sharpness;
                    endIntensity = baseIntensity;
                    endSharpness = baseSharpness;
                    usesFinalIsolatedValues = true;
                    break;
                case FidgetSemanticEvent.ButtonPressed:
                    baseIntensity = 0.55f;
                    baseSharpness = 0.88f;
                    endIntensity = 0.28f;
                    endSharpness = 0.50f;
                    acceptsProductRhythm = true;
                    break;
                case FidgetSemanticEvent.ButtonReleased:
                    baseIntensity = 0.24f;
                    baseSharpness = 0.48f;
                    endIntensity = baseIntensity;
                    endSharpness = baseSharpness;
                    break;
                case FidgetSemanticEvent.Pop:
                    baseIntensity = 0.72f;
                    baseSharpness = 0.96f;
                    endIntensity = 0.20f;
                    endSharpness = 0.62f;
                    pulseCount = 2;
                    pulseInterval = 0.028f;
                    impactLayers = 1.2f;
                    break;
                case FidgetSemanticEvent.Collision:
                    baseIntensity = 0.90f;
                    baseSharpness = 0.82f;
                    endIntensity = baseIntensity * 0.45f;
                    endSharpness = baseSharpness * 0.70f;
                    followsSpeed = true;
                    speedMinimumGain = 0.25f / 0.90f;
                    break;
                case FidgetSemanticEvent.Preview:
                    waveform = FidgetHapticWaveform.Hybrid;
                    baseIntensity = 0.92f;
                    baseSharpness = 0.94f;
                    endIntensity = 0.38f;
                    endSharpness = 0.60f;
                    duration = 0.05f;
                    decay = 0.06f;
                    pulseCount = 2;
                    pulseInterval = 0.034f;
                    impactLayers = 1.65f;
                    break;
                case FidgetSemanticEvent.BadgeUnlocked:
                    waveform = FidgetHapticWaveform.Hybrid;
                    baseIntensity = 0.78f;
                    baseSharpness = 0.72f;
                    endIntensity = 0.34f;
                    endSharpness = 0.96f;
                    duration = 0.09f;
                    decay = 0.07f;
                    release = 0.05f;
                    pulseCount = 3;
                    pulseInterval = 0.042f;
                    impactLayers = 1.55f;
                    break;
                default:
                    baseIntensity = 0.55f;
                    baseSharpness = 0.85f;
                    endIntensity = 0.25f;
                    endSharpness = 0.62f;
                    acceptsProductRhythm = true;
                    break;
            }

            if (Overrides.TryGetValue(semanticEvent, out HapticRecipeOverride recipeOverride))
            {
                waveform = recipeOverride.Waveform;
                baseIntensity = recipeOverride.Intensity;
                baseSharpness = recipeOverride.Sharpness;
                duration = recipeOverride.Duration;
                attack = recipeOverride.Attack;
                decay = recipeOverride.Decay;
                release = recipeOverride.Release;
                sustained = recipeOverride.Sustained;
                endIntensity = recipeOverride.EndIntensity;
                endSharpness = recipeOverride.EndSharpness;
                pulseCount = recipeOverride.PulseCount;
                pulseInterval = recipeOverride.PulseInterval;
                impactLayers = recipeOverride.ImpactLayers;
                dynamicIntensity = recipeOverride.DynamicIntensity;
                dynamicSharpness = recipeOverride.DynamicSharpness;
                dynamicAttack = recipeOverride.DynamicAttack;
                dynamicDecay = recipeOverride.DynamicDecay;
                dynamicRelease = recipeOverride.DynamicRelease;
            }

            if (!usesFinalIsolatedValues)
            {
                float speedGain = followsSpeed
                    ? Mathf.Lerp(
                        1f,
                        Mathf.Lerp(speedMinimumGain, 1f, signal),
                        settings.SpeedFollow)
                    : 1f;
                float frequencyOffset = (settings.FrequencyFeel - 0.5f) * 0.44f;
                baseIntensity *= settings.Intensity * speedGain;
                endIntensity *= settings.Intensity * speedGain;
                baseSharpness = Mathf.Clamp01(baseSharpness + frequencyOffset);
                endSharpness = Mathf.Clamp01(endSharpness + frequencyOffset);
            }

            if (acceptsProductRhythm)
            {
                switch (settings.Rhythm)
                {
                    case FidgetHapticRhythm.Double:
                        pulseCount = Mathf.Max(pulseCount, 2);
                        pulseInterval = 0.038f;
                        endIntensity = Mathf.Min(endIntensity, baseIntensity * 0.55f);
                        break;
                    case FidgetHapticRhythm.Burst:
                        pulseCount = Mathf.Max(pulseCount, 3);
                        pulseInterval = 0.032f;
                        endIntensity = Mathf.Min(endIntensity, baseIntensity * 0.48f);
                        break;
                }
            }

            return new HapticRecipe(
                semanticEvent,
                waveform,
                baseIntensity,
                baseSharpness,
                duration,
                attack,
                decay,
                release,
                sustained,
                endIntensity,
                endSharpness,
                pulseCount,
                pulseInterval,
                impactLayers,
                dynamicIntensity,
                dynamicSharpness,
                dynamicAttack,
                dynamicDecay,
                dynamicRelease);
        }
    }

    public static class FidgetHapticRouter
    {
        private const double MinimumDetentInterval = 0.025;
        private static readonly HapticSpeedTextureStateMachine SpeedTextureState = new();

        private static double lastDetentTime = double.NegativeInfinity;
        private static HapticSpeedTextureProfile speedTextureProfile =
            HapticSpeedTextureProfile.Recommended;
        private static HapticSpeedTextureSample speedTextureSample =
            HapticSpeedTextureSample.Rest;
        private static DetentFeelConfig detentFeel =
            DetentFeelPresetCatalog.Default.Config;
        private static int renderedEventCount;
        private static int suppressedEventCount;
        private static FidgetSemanticEvent lastSemanticEvent = FidgetSemanticEvent.Selection;
        private static bool speedTexturePreviewActive;

        public static HapticSpeedTextureProfile SpeedTextureProfile => speedTextureProfile;
        public static HapticSpeedTextureSample SpeedTextureSample => speedTextureSample;
        public static DetentFeelConfig DetentFeel => detentFeel;
        public static int LastMagneticSliderDirection { get; private set; }
        public static int LastMagneticSliderDetentIndex { get; private set; }

        public static void ConfigureDetentFeel(DetentFeelConfig config)
        {
            detentFeel = config;
            ResetRateLimits();
        }

        public static void ConfigureSpeedTexture(HapticSpeedTextureProfile profile)
        {
            StopSpeedTexture(true);
            speedTextureProfile = profile;
        }

        /// <summary>
        /// Feeds actual mechanism state into the semantic speed-texture layer.
        /// This method only renders haptics; it never drives rotor physics.
        /// </summary>
        public static void UpdateSpeedTexture(
            float angularSpeedRadians,
            int detentsPerTurn,
            bool outputAllowed = true)
        {
            if (speedTexturePreviewActive)
            {
                return;
            }

            speedTextureSample = SpeedTextureState.Step(
                angularSpeedRadians,
                detentsPerTurn,
                Time.unscaledTimeAsDouble,
                outputAllowed && IosHaptics.Enabled,
                speedTextureProfile,
                detentFeel);

            switch (speedTextureSample.Action)
            {
                case HapticSpeedTextureAction.StartContinuous:
                    IosHaptics.StartDetentContinuousResolved(
                        speedTextureSample.ContinuousIntensity,
                        speedTextureSample.ContinuousSharpness,
                        speedTextureProfile.Attack,
                        speedTextureProfile.ReleaseSeconds);
                    break;
                case HapticSpeedTextureAction.UpdateContinuous:
                    IosHaptics.UpdateDetentContinuousResolved(
                        speedTextureSample.ContinuousIntensity,
                        speedTextureSample.ContinuousSharpness);
                    break;
                case HapticSpeedTextureAction.StopContinuous:
                    IosHaptics.StopContinuous(speedTextureProfile.ReleaseSeconds);
                    break;
            }
        }

        public static void PreviewSpeedTexture(float normalizedSignal)
        {
            StopSpeedTexture(true);
            speedTexturePreviewActive = true;
            float signal = Mathf.Pow(
                Mathf.Clamp01(normalizedSignal),
                speedTextureProfile.ResponseExponent);
            float intensity = signal * detentFeel.Intensity;
            float sharpness = detentFeel.Sharpness;
            speedTextureSample = new HapticSpeedTextureSample(
                HapticSpeedTextureBand.BearingContinuous,
                HapticSpeedTextureAction.StartContinuous,
                speedTextureProfile.FullScaleAngularSpeed * signal,
                speedTextureProfile.EnterContinuousDetentsPerSecond,
                signal,
                speedTextureProfile.FastDetentIntensityGain,
                intensity,
                sharpness,
                true);
            IosHaptics.StartDetentContinuousResolved(
                intensity,
                sharpness,
                speedTextureProfile.Attack,
                speedTextureProfile.ReleaseSeconds);
        }

        public static void StopSpeedTexture(bool immediate = false)
        {
            bool hadContinuousOutput = SpeedTextureState.ForceStop()
                || speedTexturePreviewActive
                || speedTextureSample.SuppressDetentTransients;
            speedTexturePreviewActive = false;
            speedTextureSample = HapticSpeedTextureSample.Rest;
            if (hadContinuousOutput)
            {
                IosHaptics.StopContinuous(
                    immediate ? 0f : speedTextureProfile.ReleaseSeconds);
            }
        }

        /// <summary>
        /// Renders semantic events emitted by the linear magnetic mechanism.
        /// Its isolated detent values deliberately do not inherit the rotary
        /// detent preset, so spinner settings cannot overwrite the six-step tile.
        /// </summary>
        public static void EmitMagneticSlider(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal,
            MagneticSliderHapticTuning tuning,
            int direction = 0,
            int detentIndex = 0)
        {
            lastSemanticEvent = semanticEvent;
            if (semanticEvent == FidgetSemanticEvent.DetentCrossed)
            {
                LastMagneticSliderDirection = direction < 0
                    ? -1
                    : direction > 0
                        ? 1
                        : 0;
                LastMagneticSliderDetentIndex = detentIndex;
            }
            if (semanticEvent == FidgetSemanticEvent.MagneticEdgeProbe)
            {
                float signal = Mathf.Clamp01(normalizedSignal);
                renderedEventCount++;
                IosHaptics.PlayMagneticEdgeProbeResolved(
                    Mathf.Lerp(
                        tuning.EdgeMinimumIntensity,
                        tuning.EdgeMaximumIntensity,
                        signal),
                    Mathf.Lerp(
                        tuning.EdgeMinimumSharpness,
                        tuning.EdgeMaximumSharpness,
                        signal),
                    tuning.EdgePulseDurationSeconds);
                return;
            }

            if (semanticEvent == FidgetSemanticEvent.DetentCrossed)
            {
                renderedEventCount++;
                IosHaptics.PlayPushDetentPacketResolved(
                    tuning.CrossingPrimaryIntensity,
                    tuning.CrossingPrimarySharpness,
                    tuning.CrossingBodyIntensity,
                    tuning.CrossingBodySharpness,
                    tuning.CrossingBodyDurationSeconds,
                    tuning.CrossingSecondaryIntensity,
                    tuning.CrossingSecondarySharpness,
                    tuning.CrossingPulseIntervalSeconds);
                return;
            }

            // The mechanism still emits Breakaway and DetentCaptured for state,
            // telemetry and tests. The magnetic tile deliberately renders no
            // second impact for them: one spatial edge cue and one crossing
            // weighted packet are the complete tactile sentence for a manual detent.
            if (semanticEvent == FidgetSemanticEvent.Breakaway
                || semanticEvent == FidgetSemanticEvent.DetentCaptured)
            {
                suppressedEventCount++;
                return;
            }

            renderedEventCount++;
            IosHaptics.Play(semanticEvent, normalizedSignal, 1f);
        }

        public static void StopAllContinuous(bool immediate = false)
        {
            StopSpeedTexture(immediate);
        }

        /// <summary>
        /// Renders one short weighted packet for each physical fan-card detent.
        /// Slow crossings retain a low-sharpness body; ballistic crossings make
        /// the leading impact harder without inheriting a rotary preset.
        /// </summary>
        public static void EmitFanCard(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal,
            FanCardHapticTuning tuning)
        {
            lastSemanticEvent = semanticEvent;
            if (semanticEvent == FidgetSemanticEvent.DetentCrossed)
            {
                float signal = Mathf.Clamp01(normalizedSignal);
                renderedEventCount++;
                IosHaptics.PlayPushDetentPacketResolved(
                    Mathf.Lerp(
                        tuning.MinimumIntensity,
                        tuning.MaximumIntensity,
                        signal),
                    Mathf.Lerp(
                        tuning.MinimumSharpness,
                        tuning.MaximumSharpness,
                        signal),
                    tuning.BodyIntensity,
                    tuning.BodySharpness,
                    tuning.BodyDurationSeconds,
                    tuning.TailIntensity,
                    tuning.TailSharpness,
                    tuning.TailDelaySeconds);
                return;
            }

            // Breakaway and capture remain available to mechanics, visuals and
            // telemetry, but the card's complete tactile sentence is the one
            // weighted packet emitted at the real detent crossing.
            if (semanticEvent == FidgetSemanticEvent.Breakaway
                || semanticEvent == FidgetSemanticEvent.DetentCaptured)
            {
                suppressedEventCount++;
                return;
            }

            Emit(semanticEvent, normalizedSignal);
        }

        public static FidgetHapticTelemetry GetTelemetry()
        {
            return new FidgetHapticTelemetry(
                speedTextureSample,
                renderedEventCount,
                suppressedEventCount,
                lastSemanticEvent,
                IosHaptics.NativeStatus);
        }

        public static void Emit(FidgetSemanticEvent semanticEvent, float normalizedSignal = 0f)
        {
            lastSemanticEvent = semanticEvent;
            if (semanticEvent == FidgetSemanticEvent.DetentCaptured
                || semanticEvent == FidgetSemanticEvent.Reset)
            {
                StopSpeedTexture(false);
            }

            float intensityMultiplier = 1f;
            if (semanticEvent == FidgetSemanticEvent.DetentCrossed)
            {
                if (speedTextureSample.SuppressDetentTransients)
                {
                    suppressedEventCount++;
                    return;
                }

                double now = Time.unscaledTimeAsDouble;
                if (now - lastDetentTime < MinimumDetentInterval)
                {
                    suppressedEventCount++;
                    return;
                }
                lastDetentTime = now;
                renderedEventCount++;
                IosHaptics.PlayDetentTransientResolved(
                    detentFeel.Intensity,
                    detentFeel.Sharpness);
                return;
            }

            if (semanticEvent == FidgetSemanticEvent.InertiaShift)
            {
                renderedEventCount++;
                IosHaptics.PlayInertiaTransientResolved(normalizedSignal);
                return;
            }

            if (semanticEvent == FidgetSemanticEvent.TwistDetentCrossed)
            {
                // The dial rate-limits itself (30 ms) and must not share the
                // rotor detent gate, so a phone twist during rotor coasting
                // never steals or delays a real ratchet tick.
                renderedEventCount++;
                IosHaptics.PlayDetentTransientResolved(
                    DeviceTwistHapticRecipe.ResolveIntensity(normalizedSignal),
                    DeviceTwistHapticRecipe.Sharpness);
                return;
            }

            renderedEventCount++;
            IosHaptics.Play(semanticEvent, normalizedSignal, intensityMultiplier);
        }

        public static void ResetRateLimits()
        {
            lastDetentTime = double.NegativeInfinity;
        }
    }

    public static class IosHaptics
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexIosHapticsPrepare();

        [DllImport("__Internal")]
        private static extern int CodexIosHapticsGetStatus();

        [DllImport("__Internal")]
        private static extern void CodexIosHapticsPlayPattern(
            int pattern,
            float intensity,
            float sharpness,
            int waveform,
            float duration,
            float attack,
            float decay,
            float release,
            int sustained,
            float endIntensity,
            float endSharpness,
            int pulseCount,
            float pulseInterval,
            float impactBoost,
            float dynamicIntensity,
            float dynamicSharpness,
            float dynamicAttack,
            float dynamicDecay,
            float dynamicRelease);

        [DllImport("__Internal")]
        private static extern void CodexIosHapticsPlayIsolatedTransient(
            float intensity,
            float sharpness);

        [DllImport("__Internal")]
        private static extern void CodexIosHapticsStartContinuous(
            float intensity,
            float sharpness,
            float attack,
            float release);

        [DllImport("__Internal")]
        private static extern void CodexIosHapticsUpdateContinuous(
            float intensity,
            float sharpness);

        [DllImport("__Internal")]
        private static extern void CodexIosHapticsStopContinuous(float release);

        [DllImport("__Internal")]
        private static extern void CodexIosHapticsPlayMagneticEdgeProbe(
            float intensity,
            float sharpness,
            float duration);

        [DllImport("__Internal")]
        private static extern void CodexIosHapticsPlayMagneticCrossingTremor(
            float primaryIntensity,
            float primarySharpness,
            float secondaryIntensity,
            float secondarySharpness,
            float pulseInterval);

        [DllImport("__Internal")]
        private static extern void CodexIosHapticsPlayPushDetentPacket(
            float primaryIntensity,
            float primarySharpness,
            float bodyIntensity,
            float bodySharpness,
            float bodyDuration,
            float tailIntensity,
            float tailSharpness,
            float tailDelay);

        [DllImport("__Internal")]
        private static extern void CodexIosHapticsPlaySystemPreset(
            int preset,
            float intensity);
#endif

        private static FidgetHapticSettings settings = FidgetHapticSettings.Recommended;

        public static bool IsSupported => Application.platform == RuntimePlatform.IPhonePlayer;
        public static bool Enabled => settings.Enabled;
        public static float Intensity => settings.Intensity;
        public static float FrequencyFeel => settings.FrequencyFeel;
        public static float SpeedFollow => settings.SpeedFollow;
        public static int DetentsPerTurn => settings.DetentsPerTurn;
        public static FidgetHapticRhythm Rhythm => settings.Rhythm;
        public static FidgetHapticSettings Settings => settings;
        public static int NativeStatus
        {
            get
            {
#if UNITY_IOS && !UNITY_EDITOR
                return CodexIosHapticsGetStatus();
#else
                return 0;
#endif
            }
        }

        public static void Prepare()
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsPrepare();
#endif
        }

        public static void Configure(FidgetHapticSettings newSettings)
        {
            settings = newSettings;
            if (!settings.Enabled)
            {
                StopContinuous();
            }
        }

        public static void Play(FidgetSemanticEvent semanticEvent, float normalizedSignal = 0f)
        {
            Play(semanticEvent, normalizedSignal, 1f);
        }

        internal static void Play(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal,
            float intensityMultiplier)
        {
            if (!settings.Enabled)
            {
                return;
            }

            HapticRecipe recipe = FidgetHapticRecipeLibrary.Resolve(
                semanticEvent,
                normalizedSignal,
                settings);

#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsPlayPattern(
                (int)recipe.SemanticEvent,
                recipe.Intensity * Mathf.Clamp01(intensityMultiplier),
                recipe.Sharpness,
                (int)recipe.Waveform,
                recipe.Duration,
                recipe.Attack,
                recipe.Decay,
                recipe.Release,
                recipe.Sustained ? 1 : 0,
                recipe.EndIntensity * Mathf.Clamp01(intensityMultiplier),
                recipe.EndSharpness,
                recipe.PulseCount,
                recipe.PulseInterval,
                recipe.ImpactLayers,
                recipe.DynamicIntensity,
                recipe.DynamicSharpness,
                recipe.DynamicAttack,
                recipe.DynamicDecay,
                recipe.DynamicRelease);
#endif
        }

        public static void StartContinuous(float normalizedSignal = 0f)
        {
            float signal = Mathf.Clamp01(normalizedSignal);
            StartContinuousResolved(
                Mathf.Lerp(0.06f, 0.16f, signal),
                Mathf.Lerp(0.28f, 0.48f, signal),
                0.04f,
                0.10f);
        }

        internal static void StartContinuousResolved(
            float intensity,
            float sharpness,
            float attack,
            float releaseSeconds)
        {
            if (!settings.Enabled)
            {
                return;
            }

            float resolvedIntensity = settings.Intensity * Mathf.Clamp01(intensity);
            float frequencyOffset = (settings.FrequencyFeel - 0.5f) * 0.20f;
            float resolvedSharpness = Mathf.Clamp01(sharpness + frequencyOffset);
#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsStartContinuous(
                resolvedIntensity,
                resolvedSharpness,
                Mathf.Clamp01(attack),
                Mathf.Clamp(releaseSeconds, 0f, 1f));
#endif
        }

        internal static void StartDetentContinuousResolved(
            float intensity,
            float sharpness,
            float attack,
            float releaseSeconds)
        {
            if (!settings.Enabled)
            {
                return;
            }

#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsStartContinuous(
                Mathf.Clamp01(intensity),
                Mathf.Clamp01(sharpness),
                Mathf.Clamp01(attack),
                Mathf.Clamp(releaseSeconds, 0f, 1f));
#endif
        }

        public static void UpdateContinuous(float normalizedSignal)
        {
            float signal = Mathf.Clamp01(normalizedSignal);
            UpdateContinuousResolved(
                Mathf.Lerp(0.06f, 0.16f, signal),
                Mathf.Lerp(0.28f, 0.48f, signal));
        }

        internal static void UpdateContinuousResolved(float intensity, float sharpness)
        {
            if (!settings.Enabled)
            {
                return;
            }

            float resolvedIntensity = settings.Intensity * Mathf.Clamp01(intensity);
            float frequencyOffset = (settings.FrequencyFeel - 0.5f) * 0.20f;
            float resolvedSharpness = Mathf.Clamp01(sharpness + frequencyOffset);
#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsUpdateContinuous(resolvedIntensity, resolvedSharpness);
#endif
        }

        internal static void UpdateDetentContinuousResolved(
            float intensity,
            float sharpness)
        {
            if (!settings.Enabled)
            {
                return;
            }

#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsUpdateContinuous(
                Mathf.Clamp01(intensity),
                Mathf.Clamp01(sharpness));
#endif
        }

        internal static void PlayDetentTransientResolved(
            float intensity,
            float sharpness)
        {
            if (!settings.Enabled)
            {
                return;
            }

#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsPlayIsolatedTransient(
                Mathf.Clamp01(intensity),
                Mathf.Clamp01(sharpness));
#endif
        }

        internal static void PlayMagneticEdgeProbeResolved(
            float intensity,
            float sharpness,
            float durationSeconds)
        {
            if (!settings.Enabled)
            {
                return;
            }

#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsPlayMagneticEdgeProbe(
                Mathf.Clamp01(intensity),
                Mathf.Clamp01(sharpness),
                Mathf.Clamp(durationSeconds, 0.005f, 0.080f));
#endif
        }

        internal static void PlayMagneticCrossingTremorResolved(
            float primaryIntensity,
            float primarySharpness,
            float secondaryIntensity,
            float secondarySharpness,
            float pulseIntervalSeconds)
        {
            if (!settings.Enabled)
            {
                return;
            }

#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsPlayMagneticCrossingTremor(
                Mathf.Clamp01(primaryIntensity),
                Mathf.Clamp01(primarySharpness),
                Mathf.Clamp01(secondaryIntensity),
                Mathf.Clamp01(secondarySharpness),
                Mathf.Clamp(pulseIntervalSeconds, 0.010f, 0.080f));
#endif
        }

        internal static void PlayPushDetentPacketResolved(
            float primaryIntensity,
            float primarySharpness,
            float bodyIntensity,
            float bodySharpness,
            float bodyDurationSeconds,
            float tailIntensity,
            float tailSharpness,
            float tailDelaySeconds)
        {
            if (!settings.Enabled)
            {
                return;
            }

#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsPlayPushDetentPacket(
                Mathf.Clamp01(primaryIntensity),
                Mathf.Clamp01(primarySharpness),
                Mathf.Clamp01(bodyIntensity),
                Mathf.Clamp01(bodySharpness),
                Mathf.Clamp(bodyDurationSeconds, 0.010f, 0.080f),
                Mathf.Clamp01(tailIntensity),
                Mathf.Clamp01(tailSharpness),
                Mathf.Clamp(tailDelaySeconds, 0.010f, 0.080f));
#endif
        }

        internal static void PlayInertiaTransientResolved(float normalizedSignal)
        {
            if (!settings.Enabled)
            {
                return;
            }

            float signal = Mathf.Clamp01(normalizedSignal);
#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsPlayIsolatedTransient(
                Mathf.Lerp(0.25f, 0.40f, signal),
                Mathf.Lerp(0.20f, 0.35f, signal));
#endif
        }

        public static void StopContinuous(float release = 0.060f)
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsStopContinuous(Mathf.Clamp(release, 0f, 1f));
#endif
        }

        public static void PlayImpact(IosHapticImpactStyle style)
        {
            switch (style)
            {
                case IosHapticImpactStyle.Heavy:
                    Play(FidgetSemanticEvent.DetentCaptured, 1f);
                    break;
                case IosHapticImpactStyle.Soft:
                    Play(FidgetSemanticEvent.Released, 0.4f);
                    break;
                case IosHapticImpactStyle.Rigid:
                    Play(FidgetSemanticEvent.Breakaway, 0.8f);
                    break;
                default:
                    Play(FidgetSemanticEvent.Selection, 0.5f);
                    break;
            }
        }

        public static void PlaySelectionTick()
        {
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Selection);
        }

        public static void PlayDetent(float normalizedSpeed)
        {
            FidgetHapticRouter.Emit(FidgetSemanticEvent.DetentCrossed, normalizedSpeed);
        }

        public static void PlayRelease()
        {
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Released);
        }

        public static void PlayReversal()
        {
            FidgetHapticRouter.Emit(FidgetSemanticEvent.DirectionReversed);
        }

        public static void PlayReset()
        {
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Reset);
        }

        public static void PlayPreview()
        {
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Preview, 0.7f);
        }

        public static void PlaySystemPreset(IosSystemHapticPreset preset)
        {
            if (!settings.Enabled)
            {
                return;
            }

#if UNITY_IOS && !UNITY_EDITOR
            CodexIosHapticsPlaySystemPreset((int)preset, settings.Intensity);
#endif
        }
    }
}
