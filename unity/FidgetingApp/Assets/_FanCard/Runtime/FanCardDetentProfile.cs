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

        [Header("Prototype-normalized magnetic feel")]
        [SerializeField] private float breakawayLoad = 0.067f;
        [SerializeField] private float handSpring = 52f;
        [SerializeField] private float handDamping = 8.7f;
        [SerializeField] private float magneticForcePeak = 7.8f;
        [SerializeField] private float railFriction = 0.72f;
        [SerializeField] private float captureSpring = 92f;
        [SerializeField] private float captureDamping = 13.6f;
        [SerializeField] private float breakawayImpulse = 0.72f;
        [SerializeField] private float capturePredictionSeconds = 0.055f;
        [SerializeField] private float visiblePreloadScale = 0.28f;

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
            breakawayLoad = 0.067f;
            handSpring = 52f;
            handDamping = 8.7f;
            magneticForcePeak = 7.8f;
            railFriction = 0.72f;
            captureSpring = 92f;
            captureDamping = 13.6f;
            breakawayImpulse = 0.72f;
            capturePredictionSeconds = 0.055f;
            visiblePreloadScale = 0.28f;
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
