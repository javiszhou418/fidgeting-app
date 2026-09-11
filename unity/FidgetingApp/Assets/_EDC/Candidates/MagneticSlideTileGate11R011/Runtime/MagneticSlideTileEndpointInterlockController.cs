using System;
using UnityEngine;

namespace FidgetingApp.EDC.Candidates
{
    public sealed class MagneticSlideTileEndpointInterlockController : MonoBehaviour
    {
        private const float PositionTolerance = 0.000001f;
        private const float AngleTolerance = 0.001f;

        [SerializeField] private Transform bottomExterior;
        [SerializeField] private Transform fixedAxis;
        [SerializeField] private Transform rotatingCarrier;
        [SerializeField] private Transform movingTop;
        [SerializeField] private Transform topLocalSlide;
        [SerializeField] private float maximumTravelMeters = 0.018076433f;
        [SerializeField] private float detentStepDegrees = 12f;

        private Vector3 slideClosedLocalPosition;
        private Quaternion carrierClosedLocalRotation;
        private Quaternion topClosedLocalRotation;
        private Matrix4x4 bottomBaseline;
        private Matrix4x4 axisBaseline;

        public Transform BottomExterior => bottomExterior;
        public Transform FixedAxis => fixedAxis;
        public Transform RotatingCarrier => rotatingCarrier;
        public Transform MovingTop => movingTop;
        public Transform TopLocalSlide => topLocalSlide;
        public float MaximumTravelMeters => maximumTravelMeters;
        public float TravelMeters { get; private set; }
        public float AngleDegrees { get; private set; }
        public float LinearVelocityMetersPerSecond { get; private set; }
        public float AngularVelocityDegreesPerSecond { get; private set; }
        public string LastTransition { get; private set; } = "closed-zero-motion";

        public void Configure(
            Transform bottom,
            Transform axis,
            Transform carrier,
            Transform top,
            Transform slide,
            float maximumTravel,
            float detentStep)
        {
            bottomExterior = bottom;
            fixedAxis = axis;
            rotatingCarrier = carrier;
            movingTop = top;
            topLocalSlide = slide;
            maximumTravelMeters = maximumTravel;
            detentStepDegrees = detentStep;
            CaptureBaselines();
            ResetPose();
        }

        private void Awake()
        {
            if (topLocalSlide != null)
            {
                CaptureBaselines();
                ResetPose();
            }
        }

        private void CaptureBaselines()
        {
            slideClosedLocalPosition = topLocalSlide.localPosition;
            carrierClosedLocalRotation = rotatingCarrier.localRotation;
            topClosedLocalRotation = movingTop.localRotation;
            bottomBaseline = bottomExterior.localToWorldMatrix;
            axisBaseline = fixedAxis.localToWorldMatrix;
        }

        public void ResetPose()
        {
            TravelMeters = 0f;
            AngleDegrees = 0f;
            LinearVelocityMetersPerSecond = 0f;
            AngularVelocityDegreesPerSecond = 0f;
            LastTransition = "closed-zero-motion";
            ApplyPose();
        }

        public bool TrySetTravel(float requestedTravelMeters)
        {
            float requested = Mathf.Clamp(
                requestedTravelMeters, 0f, maximumTravelMeters);
            if (!IsAligned(AngleDegrees)
                && Mathf.Abs(requested - maximumTravelMeters) > PositionTolerance)
            {
                LastTransition = "slide-locked-until-angle-aligns";
                LinearVelocityMetersPerSecond = 0f;
                return false;
            }

            TravelMeters = requested;
            LinearVelocityMetersPerSecond = 0f;
            AngularVelocityDegreesPerSecond = 0f;
            LastTransition = requested >= maximumTravelMeters - PositionTolerance
                ? "maximum-travel-rotation-unlocked"
                : requested <= PositionTolerance
                    ? "closed-zero-motion"
                    : "mid-travel-rotation-locked";
            ApplyPose();
            return true;
        }

        public bool TrySetAngle(float requestedAngleDegrees)
        {
            float normalized = NormalizeDegrees(requestedAngleDegrees);
            float snapped = Mathf.Round(normalized / detentStepDegrees)
                * detentStepDegrees;
            snapped = NormalizeDegrees(snapped);
            if (TravelMeters < maximumTravelMeters - PositionTolerance
                && !IsAligned(snapped))
            {
                LastTransition = "rotation-locked-until-maximum-travel";
                AngularVelocityDegreesPerSecond = 0f;
                return false;
            }

            AngleDegrees = snapped;
            LinearVelocityMetersPerSecond = 0f;
            AngularVelocityDegreesPerSecond = 0f;
            LastTransition = IsAligned(snapped)
                ? "angle-aligned-slide-unlocked"
                : $"endpoint-detent-{Mathf.RoundToInt(snapped / detentStepDegrees):D2}";
            ApplyPose();
            return true;
        }

        public bool TrySetEndpointDetent(int detentIndex)
        {
            if (TravelMeters < maximumTravelMeters - PositionTolerance)
            {
                LastTransition = "rotation-locked-until-maximum-travel";
                return false;
            }
            int wrapped = ((detentIndex % 30) + 30) % 30;
            return TrySetAngle(wrapped * detentStepDegrees);
        }

        public bool IsPoseLegal()
        {
            bool angleAligned = IsAligned(AngleDegrees);
            bool travelAtMaximum =
                Mathf.Abs(TravelMeters - maximumTravelMeters) <= PositionTolerance;
            return TravelMeters >= -PositionTolerance
                && TravelMeters <= maximumTravelMeters + PositionTolerance
                && (angleAligned || travelAtMaximum)
                && IsDetent(AngleDegrees)
                && MatrixApproximately(bottomExterior.localToWorldMatrix, bottomBaseline)
                && MatrixApproximately(fixedAxis.localToWorldMatrix, axisBaseline)
                && HasPositiveScale(transform)
                && HasPositiveScale(bottomExterior)
                && HasPositiveScale(movingTop);
        }

        private void ApplyPose()
        {
            Quaternion yaw = Quaternion.AngleAxis(AngleDegrees, Vector3.up);
            rotatingCarrier.localRotation = carrierClosedLocalRotation * yaw;
            movingTop.localRotation = topClosedLocalRotation * yaw;
            topLocalSlide.localPosition =
                slideClosedLocalPosition + Vector3.forward * TravelMeters;
        }

        private bool IsDetent(float angle)
        {
            float steps = angle / detentStepDegrees;
            return Mathf.Abs(steps - Mathf.Round(steps)) <= AngleTolerance;
        }

        private static bool IsAligned(float angle)
        {
            float normalized = NormalizeDegrees(angle);
            return normalized <= AngleTolerance
                || Mathf.Abs(normalized - 360f) <= AngleTolerance;
        }

        private static float NormalizeDegrees(float angle)
        {
            float normalized = angle % 360f;
            return normalized < 0f ? normalized + 360f : normalized;
        }

        private static bool MatrixApproximately(Matrix4x4 first, Matrix4x4 second)
        {
            for (int row = 0; row < 4; row++)
            for (int column = 0; column < 4; column++)
            {
                if (Mathf.Abs(first[row, column] - second[row, column]) > 0.000001f)
                    return false;
            }
            return true;
        }

        private static bool HasPositiveScale(Transform item)
        {
            Vector3 scale = item.lossyScale;
            return scale.x > 0f && scale.y > 0f && scale.z > 0f;
        }
    }
}
