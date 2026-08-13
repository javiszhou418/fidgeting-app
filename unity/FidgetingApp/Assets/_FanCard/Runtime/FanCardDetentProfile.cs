using UnityEngine;

namespace FidgetingApp.FanCard
{
    /// <summary>
    /// Authoritative geometry and normalized feel copied from the approved
    /// interactive prototype. The values are deliberately independent from
    /// the rotary and linear-slider settings panels.
    /// </summary>
    [CreateAssetMenu(
        fileName = "FanCardDetentProfile",
        menuName = "Fidgeting/Fan Card Detent Profile")]
    public sealed class FanCardDetentProfile : ScriptableObject
    {
        public const int ReferenceDetentCount = 4;
        public const float ReferenceMaximumRelativeAngleDegrees = 45f;
        public const float ReferenceMaximumTotalAngleDegrees = 90f;

        [Header("Kinematics")]
        [SerializeField] private int detentCount = ReferenceDetentCount;
        [SerializeField] private float maximumRelativeAngleDegrees =
            ReferenceMaximumRelativeAngleDegrees;

        [Header("Controlled detent feel")]
        [SerializeField] private float breakawayLoad = 0.050f;
        [SerializeField] private float handSpring = 96f;
        [SerializeField] private float handDamping = 6.0f;
        [SerializeField] private float magneticForcePeak = 6.4f;
        [SerializeField] private float railFriction = 0.38f;
        [SerializeField] private float captureSpring = 118f;
        [SerializeField] private float captureDamping = 14.2f;
        [SerializeField] private float breakawayImpulse = 0.95f;
        [SerializeField] private float capturePredictionSeconds = 0.070f;
        [SerializeField] private float visiblePreloadScale = 0.24f;
        [SerializeField] private float maximumHeldSpeed = 2.4f;

        [Header("Fast traversal feel")]
        [SerializeField] private float fastBreakawayLoad = 0.024f;
        [SerializeField] private float fastHandSpring = 220f;
        [SerializeField] private float fastHandDamping = 5.2f;
        [SerializeField] private float fastMagneticForceScale = 0.50f;
        [SerializeField] private float fastRailFriction = 0.16f;
        [SerializeField] private float fastBreakawayImpulse = 1.8f;
        [SerializeField] private float fastMaximumHeldSpeed = 5.0f;
        [SerializeField] private float fastTraversalHoldAuthority = 0.72f;

        [Header("Gesture classification")]
        [SerializeField] private float fastTraversalStartScreenWidthsPerSecond =
            0.55f;
        [SerializeField] private float fastTraversalFullScreenWidthsPerSecond =
            1.30f;
        [SerializeField] private float fastPressureDeltaStart = 0.10f;
        [SerializeField] private float fastPressureDeltaFull = 0.45f;
        [SerializeField] private float fastTraversalLatchThreshold = 0.60f;
        [SerializeField] private float fastTraversalReverseThreshold = 0.35f;
        [SerializeField] private float traversalAuthorityRise = 32f;
        [SerializeField] private float traversalAuthorityFall = 10f;

        [Header("Fan-card haptics")]
        [SerializeField] private float detentHapticMinimumIntensity = 0.92f;
        [SerializeField] private float detentHapticMaximumIntensity = 1.0f;
        [SerializeField] private float detentHapticMinimumSharpness = 0.76f;
        [SerializeField] private float detentHapticMaximumSharpness = 0.90f;
        [SerializeField] private float detentHapticBodyIntensity = 0.64f;
        [SerializeField] private float detentHapticBodySharpness = 0.24f;
        [SerializeField] private float detentHapticBodyDurationSeconds = 0.032f;
        [SerializeField] private float detentHapticTailIntensity = 0.56f;
        [SerializeField] private float detentHapticTailSharpness = 0.42f;
        [SerializeField] private float detentHapticTailDelaySeconds = 0.022f;

        [Header("Capture")]
        [SerializeField] private float heldCapturePositionError = 0.004f;
        [SerializeField] private float heldCaptureSpeed = 0.065f;
        [SerializeField] private float heldTargetError = 0.026f;
        [SerializeField] private float releaseCapturePositionError = 0.0012f;
        [SerializeField] private float releaseCaptureSpeed = 0.018f;
        [SerializeField] private float maximumSubstepSeconds = 1f / 240f;
        [SerializeField] private float maximumFrameStepSeconds = 1f / 20f;

        public int DetentCount => Mathf.Max(2, detentCount);
        public int DetentIntervals => DetentCount - 1;
        public float MaximumRelativeAngleDegrees => maximumRelativeAngleDegrees;
        public float MaximumTotalAngleDegrees => maximumRelativeAngleDegrees * 2f;
        public float BreakawayLoad => breakawayLoad;
        public float HandSpring => handSpring;
        public float HandDamping => handDamping;
        public float MagneticForcePeak => magneticForcePeak;
        public float RailFriction => railFriction;
        public float CaptureSpring => captureSpring;
        public float CaptureDamping => captureDamping;
        public float BreakawayImpulse => breakawayImpulse;
        public float CapturePredictionSeconds => capturePredictionSeconds;
        public float VisiblePreloadScale => visiblePreloadScale;
        public float MaximumHeldSpeed => maximumHeldSpeed;
        public float FastBreakawayLoad => fastBreakawayLoad;
        public float FastHandSpring => fastHandSpring;
        public float FastHandDamping => fastHandDamping;
        public float FastMagneticForceScale => fastMagneticForceScale;
        public float FastRailFriction => fastRailFriction;
        public float FastBreakawayImpulse => fastBreakawayImpulse;
        public float FastMaximumHeldSpeed => fastMaximumHeldSpeed;
        public float FastTraversalHoldAuthority => fastTraversalHoldAuthority;
        public float FastTraversalStartScreenWidthsPerSecond =>
            fastTraversalStartScreenWidthsPerSecond;
        public float FastTraversalFullScreenWidthsPerSecond =>
            fastTraversalFullScreenWidthsPerSecond;
        public float FastPressureDeltaStart => fastPressureDeltaStart;
        public float FastPressureDeltaFull => fastPressureDeltaFull;
        public float FastTraversalLatchThreshold => fastTraversalLatchThreshold;
        public float FastTraversalReverseThreshold => fastTraversalReverseThreshold;
        public float TraversalAuthorityRise => traversalAuthorityRise;
        public float TraversalAuthorityFall => traversalAuthorityFall;
        public float DetentHapticMinimumIntensity => detentHapticMinimumIntensity;
        public float DetentHapticMaximumIntensity => detentHapticMaximumIntensity;
        public float DetentHapticMinimumSharpness => detentHapticMinimumSharpness;
        public float DetentHapticMaximumSharpness => detentHapticMaximumSharpness;
        public float DetentHapticBodyIntensity => detentHapticBodyIntensity;
        public float DetentHapticBodySharpness => detentHapticBodySharpness;
        public float DetentHapticBodyDurationSeconds => detentHapticBodyDurationSeconds;
        public float DetentHapticTailIntensity => detentHapticTailIntensity;
        public float DetentHapticTailSharpness => detentHapticTailSharpness;
        public float DetentHapticTailDelaySeconds => detentHapticTailDelaySeconds;
        public float HeldCapturePositionError => heldCapturePositionError;
        public float HeldCaptureSpeed => heldCaptureSpeed;
        public float HeldTargetError => heldTargetError;
        public float ReleaseCapturePositionError => releaseCapturePositionError;
        public float ReleaseCaptureSpeed => releaseCaptureSpeed;
        public float MaximumSubstepSeconds => maximumSubstepSeconds;
        public float MaximumFrameStepSeconds => maximumFrameStepSeconds;

        public void ApplyReferenceDefaults()
        {
            detentCount = ReferenceDetentCount;
            maximumRelativeAngleDegrees = ReferenceMaximumRelativeAngleDegrees;
            breakawayLoad = 0.050f;
            handSpring = 96f;
            handDamping = 6.0f;
            magneticForcePeak = 6.4f;
            railFriction = 0.38f;
            captureSpring = 118f;
            captureDamping = 14.2f;
            breakawayImpulse = 0.95f;
            capturePredictionSeconds = 0.070f;
            visiblePreloadScale = 0.24f;
            maximumHeldSpeed = 2.4f;
            fastBreakawayLoad = 0.024f;
            fastHandSpring = 220f;
            fastHandDamping = 5.2f;
            fastMagneticForceScale = 0.50f;
            fastRailFriction = 0.16f;
            fastBreakawayImpulse = 1.8f;
            fastMaximumHeldSpeed = 5.0f;
            fastTraversalHoldAuthority = 0.72f;
            fastTraversalStartScreenWidthsPerSecond = 0.55f;
            fastTraversalFullScreenWidthsPerSecond = 1.30f;
            fastPressureDeltaStart = 0.10f;
            fastPressureDeltaFull = 0.45f;
            fastTraversalLatchThreshold = 0.60f;
            fastTraversalReverseThreshold = 0.35f;
            traversalAuthorityRise = 32f;
            traversalAuthorityFall = 10f;
            detentHapticMinimumIntensity = 0.92f;
            detentHapticMaximumIntensity = 1.0f;
            detentHapticMinimumSharpness = 0.76f;
            detentHapticMaximumSharpness = 0.90f;
            detentHapticBodyIntensity = 0.64f;
            detentHapticBodySharpness = 0.24f;
            detentHapticBodyDurationSeconds = 0.032f;
            detentHapticTailIntensity = 0.56f;
            detentHapticTailSharpness = 0.42f;
            detentHapticTailDelaySeconds = 0.022f;
            heldCapturePositionError = 0.004f;
            heldCaptureSpeed = 0.065f;
            heldTargetError = 0.026f;
            releaseCapturePositionError = 0.0012f;
            releaseCaptureSpeed = 0.018f;
            maximumSubstepSeconds = 1f / 240f;
            maximumFrameStepSeconds = 1f / 20f;
        }

        private void OnValidate()
        {
            detentCount = Mathf.Max(2, detentCount);
            maximumRelativeAngleDegrees = Mathf.Clamp(
                maximumRelativeAngleDegrees,
                1f,
                ReferenceMaximumRelativeAngleDegrees);
            breakawayLoad = Mathf.Max(0.001f, breakawayLoad);
            maximumHeldSpeed = Mathf.Max(0.1f, maximumHeldSpeed);
            fastBreakawayLoad = Mathf.Clamp(
                fastBreakawayLoad,
                0.001f,
                breakawayLoad);
            fastHandSpring = Mathf.Max(handSpring, fastHandSpring);
            fastHandDamping = Mathf.Max(0f, fastHandDamping);
            fastMagneticForceScale = Mathf.Clamp01(fastMagneticForceScale);
            fastRailFriction = Mathf.Max(0f, fastRailFriction);
            fastBreakawayImpulse = Mathf.Max(
                breakawayImpulse,
                fastBreakawayImpulse);
            fastMaximumHeldSpeed = Mathf.Max(
                maximumHeldSpeed,
                fastMaximumHeldSpeed);
            fastTraversalHoldAuthority = Mathf.Clamp01(
                fastTraversalHoldAuthority);
            fastTraversalStartScreenWidthsPerSecond = Mathf.Max(
                0f,
                fastTraversalStartScreenWidthsPerSecond);
            fastTraversalFullScreenWidthsPerSecond = Mathf.Max(
                fastTraversalStartScreenWidthsPerSecond + 0.01f,
                fastTraversalFullScreenWidthsPerSecond);
            fastPressureDeltaStart = Mathf.Max(0f, fastPressureDeltaStart);
            fastPressureDeltaFull = Mathf.Max(
                fastPressureDeltaStart + 0.01f,
                fastPressureDeltaFull);
            fastTraversalLatchThreshold = Mathf.Clamp01(
                fastTraversalLatchThreshold);
            fastTraversalReverseThreshold = Mathf.Clamp(
                fastTraversalReverseThreshold,
                0f,
                fastTraversalLatchThreshold);
            traversalAuthorityRise = Mathf.Max(0f, traversalAuthorityRise);
            traversalAuthorityFall = Mathf.Max(0f, traversalAuthorityFall);
            detentHapticMinimumIntensity = Mathf.Clamp01(
                detentHapticMinimumIntensity);
            detentHapticMaximumIntensity = Mathf.Clamp(
                detentHapticMaximumIntensity,
                detentHapticMinimumIntensity,
                1f);
            detentHapticMinimumSharpness = Mathf.Clamp01(
                detentHapticMinimumSharpness);
            detentHapticMaximumSharpness = Mathf.Clamp(
                detentHapticMaximumSharpness,
                detentHapticMinimumSharpness,
                1f);
            detentHapticBodyIntensity = Mathf.Clamp01(
                detentHapticBodyIntensity);
            detentHapticBodySharpness = Mathf.Clamp01(
                detentHapticBodySharpness);
            detentHapticBodyDurationSeconds = Mathf.Clamp(
                detentHapticBodyDurationSeconds,
                0.010f,
                0.080f);
            detentHapticTailIntensity = Mathf.Clamp01(
                detentHapticTailIntensity);
            detentHapticTailSharpness = Mathf.Clamp01(
                detentHapticTailSharpness);
            detentHapticTailDelaySeconds = Mathf.Clamp(
                detentHapticTailDelaySeconds,
                0.010f,
                0.080f);
            maximumSubstepSeconds = Mathf.Clamp(
                maximumSubstepSeconds,
                1f / 1000f,
                1f / 60f);
            maximumFrameStepSeconds = Mathf.Max(
                maximumSubstepSeconds,
                maximumFrameStepSeconds);
        }
    }
}
