using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.EDC
{
    /// <summary>
    /// Single source of truth for the fifth product's visible magnets,
    /// one-dimensional mechanics, visual settling and haptic texture.
    /// Distances are expressed in metres and forces in SI units.
    /// </summary>
    [CreateAssetMenu(
        fileName = "LinearMagneticDetentProfile",
        menuName = "Fidgeting/Linear Magnetic Detent Profile")]
    public sealed class LinearMagneticDetentProfile : ScriptableObject
    {
        public const int HeavyDetentCount = 6;
        public const float HeavyDetentPitchMeters = 0.0136f;
        public const float HeavyTravelMeters = 0.068f;
        public const int HeavyDefaultDetentIndex = 2;

        [Header("Detent geometry (metres)")]
        [SerializeField] private float[] detentPositionsMeters =
        {
            0f,
            0.0136f,
            0.0272f,
            0.0408f,
            0.0544f,
            0.068f
        };
        [SerializeField, Range(0, HeavyDetentCount - 1)] private int defaultDetentIndex =
            HeavyDefaultDetentIndex;

        [Header("Heavy magnetic mechanics")]
        [SerializeField, Min(0.001f)] private float movingMassKilograms = 0.055f;
        [SerializeField, Min(0f)] private float handSpringNewtonsPerMeter = 100f;
        [SerializeField, Min(0f)] private float handDampingNewtonSecondsPerMeter = 5.0f;
        [SerializeField, Min(0f)] private float breakawayForceNewtons = 0.44f;
        [SerializeField, Min(0f)] private float magneticPeakForceNewtons = 0.42f;
        [SerializeField, Min(0f)] private float railFrictionNewtons = 0.085f;
        [SerializeField, Min(0f)] private float railDampingNewtonSecondsPerMeter = 0.30f;
        [SerializeField, Min(0f)] private float captureSpringNewtonsPerMeter = 150f;
        [SerializeField, Min(0f)] private float captureDampingNewtonSecondsPerMeter = 5.8f;
        [SerializeField, Min(0f)] private float maximumVisiblePreloadMeters = 0.0009f;
        [SerializeField, Min(0f)] private float captureRadiusMeters = 0.0040f;
        [SerializeField, Min(0f)] private float captureEntrySpeedMetersPerSecond = 0.045f;
        [SerializeField, Min(0f)] private float lockPositionErrorMeters = 0.00010f;
        [SerializeField, Min(0f)] private float lockSpeedMetersPerSecond = 0.0045f;
        [SerializeField, Min(0f)] private float releasePredictionSeconds = 0.050f;
        [SerializeField, Min(0f)] private float barrierHysteresisMeters = 0.00020f;
        [SerializeField, Min(0.0001f)] private float maximumIntegrationStepSeconds = 1f / 240f;
        [SerializeField, Range(1, 16)] private int maximumSubstepsPerFrame = 8;

        [Header("Slow edge search")]
        [SerializeField, Min(0.001f)] private float fingerVelocityHalfLifeSeconds = 0.030f;
        [SerializeField, Min(0f)] private float slowIntentEnterSpeedMetersPerSecond = 0.025f;
        [SerializeField, Min(0f)] private float slowIntentExitSpeedMetersPerSecond = 0.040f;
        [SerializeField, Min(0f)] private float slowIntentEnterDurationSeconds = 0.080f;
        [SerializeField, Min(0f)] private float slowIntentExitDurationSeconds = 0.040f;
        [SerializeField, Min(0f)] private float stationarySpeedMetersPerSecond = 0.0008f;
        [SerializeField, Min(0f)] private float stationaryDurationSeconds = 0.045f;
        [SerializeField, Range(0f, 1f)] private float edgeGovernorStartProgress = 0.55f;
        [SerializeField, Range(0f, 1f)] private float edgeGovernorEndProgress = 0.95f;
        [SerializeField, Min(0f)] private float edgeGovernorStartSpeedMetersPerSecond = 0.022f;
        [SerializeField, Min(0f)] private float edgeGovernorEndSpeedMetersPerSecond = 0.0055f;

        [Header("Spatial edge haptic")]
        [SerializeField] private float[] edgeProbeLoads = { 0.72f, 0.84f, 0.94f };
        [SerializeField, Range(0f, 1f)] private float edgeProbeRearmLoad = 0.55f;
        [SerializeField, Range(0f, 1f)] private float edgeProbeMinimumIntensity = 0.08f;
        [SerializeField, Range(0f, 1f)] private float edgeProbeMaximumIntensity = 0.14f;
        [SerializeField, Range(0f, 1f)] private float edgeProbeMinimumSharpness = 0.14f;
        [SerializeField, Range(0f, 1f)] private float edgeProbeMaximumSharpness = 0.22f;
        [SerializeField, Min(0f)] private float edgeProbePulseDurationSeconds = 0.012f;
        [SerializeField, Range(0f, 1f)] private float detentHapticIntensity = 0.28f;
        [SerializeField, Range(0f, 1f)] private float detentHapticSharpness = 0.46f;
        [SerializeField, Range(0f, 1f)] private float detentHapticSecondaryIntensity = 0.14f;
        [SerializeField, Range(0f, 1f)] private float detentHapticSecondarySharpness = 0.28f;
        [SerializeField, Min(0f)] private float detentHapticPulseIntervalSeconds = 0.030f;

        [Header("Crossing-synchronized visual tremor")]
        [SerializeField, Min(0f)] private float crossingRailAmplitudeMeters = 0.00018f;
        [SerializeField, Min(0f)] private float crossingHeightAmplitudeMeters = 0.00005f;
        [SerializeField, Min(0f)] private float crossingAngleAmplitudeDegrees = 0.08f;
        [SerializeField, Min(0.1f)] private float crossingFrequencyHertz = 24f;
        [SerializeField, Min(0.001f)] private float crossingHalfLifeSeconds = 0.024f;
        [SerializeField, Min(0.001f)] private float crossingMaximumDurationSeconds = 0.080f;

        public IReadOnlyList<float> DetentPositionsMeters => detentPositionsMeters;
        public int DetentCount => detentPositionsMeters?.Length ?? 0;
        public int DefaultDetentIndex => DetentCount > 0
            ? Mathf.Clamp(defaultDetentIndex, 0, DetentCount - 1)
            : 0;
        public float DefaultPositionMeters => GetDetentPositionMeters(DefaultDetentIndex);
        public float TravelMeters => DetentCount > 0
            ? detentPositionsMeters[DetentCount - 1] - detentPositionsMeters[0]
            : 0f;
        public float MovingMassKilograms => movingMassKilograms;
        public float HandSpringNewtonsPerMeter => handSpringNewtonsPerMeter;
        public float HandDampingNewtonSecondsPerMeter => handDampingNewtonSecondsPerMeter;
        public float BreakawayForceNewtons => breakawayForceNewtons;
        public float MagneticPeakForceNewtons => magneticPeakForceNewtons;
        public float RailFrictionNewtons => railFrictionNewtons;
        public float RailDampingNewtonSecondsPerMeter => railDampingNewtonSecondsPerMeter;
        public float CaptureSpringNewtonsPerMeter => captureSpringNewtonsPerMeter;
        public float CaptureDampingNewtonSecondsPerMeter => captureDampingNewtonSecondsPerMeter;
        public float MaximumVisiblePreloadMeters => maximumVisiblePreloadMeters;
        public float CaptureRadiusMeters => captureRadiusMeters;
        public float CaptureEntrySpeedMetersPerSecond => captureEntrySpeedMetersPerSecond;
        public float LockPositionErrorMeters => lockPositionErrorMeters;
        public float LockSpeedMetersPerSecond => lockSpeedMetersPerSecond;
        public float ReleasePredictionSeconds => releasePredictionSeconds;
        public float BarrierHysteresisMeters => barrierHysteresisMeters;
        public float MaximumIntegrationStepSeconds => maximumIntegrationStepSeconds;
        public int MaximumSubstepsPerFrame => maximumSubstepsPerFrame;
        public float FingerVelocityHalfLifeSeconds => fingerVelocityHalfLifeSeconds;
        public float SlowIntentEnterSpeedMetersPerSecond => slowIntentEnterSpeedMetersPerSecond;
        public float SlowIntentExitSpeedMetersPerSecond => slowIntentExitSpeedMetersPerSecond;
        public float SlowIntentEnterDurationSeconds => slowIntentEnterDurationSeconds;
        public float SlowIntentExitDurationSeconds => slowIntentExitDurationSeconds;
        public float StationarySpeedMetersPerSecond => stationarySpeedMetersPerSecond;
        public float StationaryDurationSeconds => stationaryDurationSeconds;
        public float EdgeGovernorStartProgress => edgeGovernorStartProgress;
        public float EdgeGovernorEndProgress => edgeGovernorEndProgress;
        public float EdgeGovernorStartSpeedMetersPerSecond => edgeGovernorStartSpeedMetersPerSecond;
        public float EdgeGovernorEndSpeedMetersPerSecond => edgeGovernorEndSpeedMetersPerSecond;
        public IReadOnlyList<float> EdgeProbeLoads => edgeProbeLoads;
        public float EdgeProbeRearmLoad => edgeProbeRearmLoad;
        public float EdgeProbeMinimumIntensity => edgeProbeMinimumIntensity;
        public float EdgeProbeMaximumIntensity => edgeProbeMaximumIntensity;
        public float EdgeProbeMinimumSharpness => edgeProbeMinimumSharpness;
        public float EdgeProbeMaximumSharpness => edgeProbeMaximumSharpness;
        public float EdgeProbePulseDurationSeconds => edgeProbePulseDurationSeconds;
        public float DetentHapticIntensity => detentHapticIntensity;
        public float DetentHapticSharpness => detentHapticSharpness;
        public float DetentHapticSecondaryIntensity => detentHapticSecondaryIntensity;
        public float DetentHapticSecondarySharpness => detentHapticSecondarySharpness;
        public float DetentHapticPulseIntervalSeconds => detentHapticPulseIntervalSeconds;
        public float CrossingRailAmplitudeMeters => crossingRailAmplitudeMeters;
        public float CrossingHeightAmplitudeMeters => crossingHeightAmplitudeMeters;
        public float CrossingAngleAmplitudeDegrees => crossingAngleAmplitudeDegrees;
        public float CrossingFrequencyHertz => crossingFrequencyHertz;
        public float CrossingHalfLifeSeconds => crossingHalfLifeSeconds;
        public float CrossingMaximumDurationSeconds => crossingMaximumDurationSeconds;

        public float GetDetentPositionMeters(int index)
        {
            if (DetentCount == 0)
            {
                return 0f;
            }
            return detentPositionsMeters[Mathf.Clamp(index, 0, DetentCount - 1)];
        }

        public void ApplyHeavyDefaults()
        {
            detentPositionsMeters = new[]
            {
                0f,
                HeavyDetentPitchMeters,
                HeavyDetentPitchMeters * 2f,
                HeavyDetentPitchMeters * 3f,
                HeavyDetentPitchMeters * 4f,
                HeavyTravelMeters
            };
            defaultDetentIndex = HeavyDefaultDetentIndex;
            movingMassKilograms = 0.055f;
            handSpringNewtonsPerMeter = 100f;
            handDampingNewtonSecondsPerMeter = 5.0f;
            breakawayForceNewtons = 0.44f;
            magneticPeakForceNewtons = 0.42f;
            railFrictionNewtons = 0.085f;
            railDampingNewtonSecondsPerMeter = 0.30f;
            captureSpringNewtonsPerMeter = 150f;
            captureDampingNewtonSecondsPerMeter = 5.8f;
            maximumVisiblePreloadMeters = 0.0009f;
            captureRadiusMeters = 0.0040f;
            captureEntrySpeedMetersPerSecond = 0.045f;
            lockPositionErrorMeters = 0.00010f;
            lockSpeedMetersPerSecond = 0.0045f;
            releasePredictionSeconds = 0.050f;
            barrierHysteresisMeters = 0.00020f;
            maximumIntegrationStepSeconds = 1f / 240f;
            maximumSubstepsPerFrame = 8;
            fingerVelocityHalfLifeSeconds = 0.030f;
            slowIntentEnterSpeedMetersPerSecond = 0.025f;
            slowIntentExitSpeedMetersPerSecond = 0.040f;
            slowIntentEnterDurationSeconds = 0.080f;
            slowIntentExitDurationSeconds = 0.040f;
            stationarySpeedMetersPerSecond = 0.0008f;
            stationaryDurationSeconds = 0.045f;
            edgeGovernorStartProgress = 0.55f;
            edgeGovernorEndProgress = 0.95f;
            edgeGovernorStartSpeedMetersPerSecond = 0.022f;
            edgeGovernorEndSpeedMetersPerSecond = 0.0055f;
            edgeProbeLoads = new[] { 0.72f, 0.84f, 0.94f };
            edgeProbeRearmLoad = 0.55f;
            edgeProbeMinimumIntensity = 0.08f;
            edgeProbeMaximumIntensity = 0.14f;
            edgeProbeMinimumSharpness = 0.14f;
            edgeProbeMaximumSharpness = 0.22f;
            edgeProbePulseDurationSeconds = 0.012f;
            detentHapticIntensity = 0.28f;
            detentHapticSharpness = 0.46f;
            detentHapticSecondaryIntensity = 0.14f;
            detentHapticSecondarySharpness = 0.28f;
            detentHapticPulseIntervalSeconds = 0.030f;
            crossingRailAmplitudeMeters = 0.00018f;
            crossingHeightAmplitudeMeters = 0.00005f;
            crossingAngleAmplitudeDegrees = 0.08f;
            crossingFrequencyHertz = 24f;
            crossingHalfLifeSeconds = 0.024f;
            crossingMaximumDurationSeconds = 0.080f;
        }

        public bool IsValid(out string reason)
        {
            if (DetentCount < 2)
            {
                reason = "A magnetic track needs at least two detents.";
                return false;
            }

            for (int index = 1; index < DetentCount; index++)
            {
                if (detentPositionsMeters[index] <= detentPositionsMeters[index - 1])
                {
                    reason = "Detent positions must be strictly increasing.";
                    return false;
                }
            }

            reason = string.Empty;
            return true;
        }

        private void OnValidate()
        {
            maximumSubstepsPerFrame = Mathf.Clamp(maximumSubstepsPerFrame, 1, 16);
            defaultDetentIndex = Mathf.Clamp(
                defaultDetentIndex,
                0,
                Mathf.Max(0, DetentCount - 1));
            maximumIntegrationStepSeconds = Mathf.Max(0.0001f, maximumIntegrationStepSeconds);
            movingMassKilograms = Mathf.Max(0.001f, movingMassKilograms);
            fingerVelocityHalfLifeSeconds = Mathf.Max(0.001f, fingerVelocityHalfLifeSeconds);
            edgeGovernorEndProgress = Mathf.Max(
                edgeGovernorStartProgress,
                edgeGovernorEndProgress);
            if (edgeProbeLoads == null || edgeProbeLoads.Length == 0)
            {
                edgeProbeLoads = new[] { 0.72f, 0.84f, 0.94f };
            }
            for (int index = 0; index < edgeProbeLoads.Length; index++)
            {
                edgeProbeLoads[index] = Mathf.Clamp01(edgeProbeLoads[index]);
            }
        }
    }
}
