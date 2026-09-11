using System;
using System.Linq;
using CodexUnityLab;
using UnityEngine;

namespace FidgetingApp.EDC.Gate12R002
{
    [DisallowMultipleComponent]
    public sealed class MagneticSlideTileShippingMechanism : MonoBehaviour
    {
        [SerializeField] private MagneticSlideTileMechanismSettings settings;
        [SerializeField] private Transform bottomExterior;
        [SerializeField] private Transform fixedAxis;
        [SerializeField] private Transform rotatingCarrier;
        [SerializeField] private Transform movingTop;
        [SerializeField] private Transform topLocalSlide;

        private Vector3 closedSlidePosition;
        private Quaternion closedCarrierRotation;
        private Quaternion closedTopRotation;
        private Matrix4x4 bottomBaseline;
        private Matrix4x4 axisBaseline;
        private float topStackBaselineWorldY;
        private Renderer[] renderersBaseline = Array.Empty<Renderer>();
        private Renderer[] movingTopRenderers = Array.Empty<Renderer>();
        private bool rotationBrokenAway;
        private bool endpointUnlockAnnounced;
        private bool baselinesCaptured;
        private int unwrappedDetentIndex;

        public event Action<FidgetSemanticEvent, float> SemanticEventRaised;

        public MagneticSlideTileMechanismSettings Settings => settings;
        public Transform FixedAxis => fixedAxis;
        public Transform RotatingCarrier => rotatingCarrier;
        public Transform MovingTop => movingTop;
        public Transform TopLocalSlide => topLocalSlide;
        public float TravelMeters { get; private set; }
        public float AngleDegrees { get; private set; }
        public float UnwrappedAngleDegrees { get; private set; }
        public float LinearVelocityMetersPerSecond { get; private set; }
        public float AngularVelocityDegreesPerSecond { get; private set; }
        public float TopStackHeightResidualMeters =>
            Mathf.Abs(topLocalSlide.position.y - topStackBaselineWorldY);
        public float FixedAxisConstraintResidual =>
            MatrixMaximumDifference(fixedAxis.localToWorldMatrix, axisBaseline);
        public float OutOfPlaneSlideResidualMeters
        {
            get
            {
                Vector3 offset = topLocalSlide.localPosition - closedSlidePosition;
                return Mathf.Max(Mathf.Abs(offset.x), Mathf.Abs(offset.z));
            }
        }
        public bool AtMaximumTravel => IsAtMaximumTravel();
        public bool RenderersRemainAttached =>
            renderersBaseline.All(renderer =>
                renderer != null && renderer.transform.IsChildOf(transform));
        public int CurrentDetentIndex => PositiveModulo(
            unwrappedDetentIndex,
            settings.DetentCount);
        public int UnwrappedDetentIndex => unwrappedDetentIndex;
        public int LastDetentCrossingDirection { get; private set; }
        public int LastDetentCrossingUnwrappedIndex { get; private set; }
        public string LastTransition { get; private set; } = "closed-zero-motion";
        public bool RotationBrokenAway => rotationBrokenAway;
        public bool IsAngleAligned => IsAligned(AngleDegrees);
        /// <summary>World rotation axis of the carrier and moving top.</summary>
        public Vector3 RotationAxisWorld => rotatingCarrier != null
            ? rotatingCarrier.TransformDirection(Vector3.forward).normalized
            : transform.forward;
        /// <summary>World direction of increasing slide travel.</summary>
        public Vector3 SlideDirectionWorld => topLocalSlide != null
            && topLocalSlide.parent != null
            ? topLocalSlide.parent.TransformDirection(Vector3.down).normalized
            : Vector3.down;

        /// <summary>
        /// Lever from the fixed axis to the moving top's renderer centroid, in
        /// world space at the current pose. Gravity torque acts on this arm.
        /// </summary>
        public Vector3 ResolveMovingTopLeverWorld()
        {
            if (movingTop == null || fixedAxis == null)
            {
                return Vector3.zero;
            }

            if (!baselinesCaptured)
            {
                CaptureBaselines();
            }
            if (movingTopRenderers.Length == 0)
            {
                return movingTop.position - fixedAxis.position;
            }

            Bounds bounds = movingTopRenderers[0].bounds;
            for (int index = 1; index < movingTopRenderers.Length; index++)
            {
                bounds.Encapsulate(movingTopRenderers[index].bounds);
            }
            return bounds.center - fixedAxis.position;
        }

        public void Configure(
            MagneticSlideTileMechanismSettings sharedSettings,
            Transform bottom,
            Transform axis,
            Transform carrier,
            Transform top,
            Transform slide)
        {
            settings = sharedSettings;
            bottomExterior = bottom;
            fixedAxis = axis;
            rotatingCarrier = carrier;
            movingTop = top;
            topLocalSlide = slide;
            CaptureBaselines();
            ResetPose(false);
        }

        private void Awake()
        {
            if (settings != null && topLocalSlide != null)
            {
                CaptureBaselines();
                ResetPose(false);
            }
        }

        public void ResetPose(bool emitSemantic = true)
        {
            if (!baselinesCaptured)
                CaptureBaselines();
            TravelMeters = 0f;
            AngleDegrees = 0f;
            UnwrappedAngleDegrees = 0f;
            LinearVelocityMetersPerSecond = 0f;
            AngularVelocityDegreesPerSecond = 0f;
            rotationBrokenAway = false;
            endpointUnlockAnnounced = false;
            unwrappedDetentIndex = 0;
            LastDetentCrossingDirection = 0;
            LastDetentCrossingUnwrappedIndex = 0;
            LastTransition = "closed-zero-motion";
            ApplyPose();
            if (emitSemantic)
                SemanticEventRaised?.Invoke(FidgetSemanticEvent.Reset, 0f);
        }

        public bool TrySetTravel(
            float requestedTravelMeters,
            bool userAuthorized = false)
        {
            float requested = Mathf.Clamp(
                requestedTravelMeters, 0f, settings.MaximumTravelMeters);
            if (!IsAligned(AngleDegrees)
                && Mathf.Abs(requested - settings.MaximumTravelMeters)
                    > settings.EndpointToleranceMeters)
            {
                StopMotion("slide-locked-until-angle-aligns");
                return false;
            }

            float previousTravel = TravelMeters;
            bool wasAtMaximum = IsAtMaximumTravel();
            TravelMeters = requested;
            StopVelocities();
            rotationBrokenAway = false;
            LastTransition =
                requested >= settings.MaximumTravelMeters
                    - settings.EndpointToleranceMeters
                ? "maximum-travel-rotation-unlocked"
                : requested <= settings.EndpointToleranceMeters
                    ? "closed-zero-motion"
                    : "mid-travel-rotation-locked";
            ApplyPose();
            EmitSlideSteps(previousTravel, requested, userAuthorized);

            bool isAtMaximum = IsAtMaximumTravel();
            if (isAtMaximum && !wasAtMaximum)
            {
                endpointUnlockAnnounced = userAuthorized;
                EmitIfAuthorized(
                    FidgetSemanticEvent.Breakaway,
                    1f,
                    userAuthorized);
            }
            else if (!isAtMaximum && wasAtMaximum)
            {
                endpointUnlockAnnounced = false;
                EmitIfAuthorized(
                    FidgetSemanticEvent.DetentCaptured,
                    1f,
                    userAuthorized);
            }
            return true;
        }

        public bool TryBeginRotation(
            float accumulatedDegrees,
            bool userAuthorized = false)
        {
            if (!IsAtMaximumTravel())
            {
                StopMotion("rotation-locked-until-maximum-travel");
                return false;
            }
            if (!rotationBrokenAway
                && Mathf.Abs(accumulatedDegrees) < settings.BreakawayDegrees)
            {
                StopMotion("endpoint-detent-captured");
                return false;
            }
            if (!rotationBrokenAway)
            {
                rotationBrokenAway = true;
                if (!endpointUnlockAnnounced)
                {
                    endpointUnlockAnnounced = true;
                    EmitIfAuthorized(
                        FidgetSemanticEvent.Breakaway,
                        1f,
                        userAuthorized);
                }
            }
            return true;
        }

        public bool TrySetAngle(
            float requestedAngleDegrees,
            bool userAuthorized = false)
        {
            int requestedDetentIndex = Mathf.RoundToInt(
                requestedAngleDegrees / settings.DetentStepDegrees);
            float snappedUnwrapped =
                requestedDetentIndex * settings.DetentStepDegrees;
            float snapped = NormalizeDegrees(snappedUnwrapped);
            if (!IsAtMaximumTravel() && !IsAligned(snapped))
            {
                StopMotion("rotation-locked-until-maximum-travel");
                return false;
            }

            int priorUnwrappedDetentIndex = unwrappedDetentIndex;
            unwrappedDetentIndex = requestedDetentIndex;
            UnwrappedAngleDegrees = snappedUnwrapped;
            AngleDegrees = snapped;
            StopVelocities();
            LastTransition = IsAligned(snapped)
                ? "angle-aligned-slide-unlocked"
                : $"endpoint-detent-{CurrentDetentIndex:D2}";
            ApplyPose();
            int crossedDetents = Mathf.Abs(
                requestedDetentIndex - priorUnwrappedDetentIndex);
            int crossingDirection = Math.Sign(
                requestedDetentIndex - priorUnwrappedDetentIndex);
            for (int index = 0; index < crossedDetents; index++)
            {
                LastDetentCrossingDirection = crossingDirection;
                LastDetentCrossingUnwrappedIndex =
                    priorUnwrappedDetentIndex
                    + crossingDirection * (index + 1);
                EmitIfAuthorized(
                    FidgetSemanticEvent.DetentCrossed,
                    1f,
                    userAuthorized);
            }
            if (crossedDetents > 0)
            {
                Debug.Log(
                    "[MagneticSlideRuntime] angle-update "
                    + $"unwrapped={UnwrappedAngleDegrees:F1} "
                    + $"angle={AngleDegrees:F1} "
                    + $"detent={CurrentDetentIndex:D2}");
            }
            return true;
        }

        public bool TryCaptureNearestDetent(
            float requestedAngleDegrees,
            bool userAuthorized = false)
        {
            if (!IsAtMaximumTravel())
                return false;
            float snapped = Mathf.Round(
                requestedAngleDegrees / settings.DetentStepDegrees)
                * settings.DetentStepDegrees;
            float error = Mathf.Abs(Mathf.DeltaAngle(requestedAngleDegrees, snapped));
            if (error > settings.CaptureRadiusDegrees)
                return false;
            bool result = TrySetAngle(snapped, userAuthorized);
            rotationBrokenAway = false;
            if (result)
            {
                EmitIfAuthorized(
                    FidgetSemanticEvent.DetentCaptured,
                    1f,
                    userAuthorized);
            }
            return result;
        }

        public bool TrySetEndpointDetent(
            int detentIndex,
            bool userAuthorized = false)
        {
            if (!IsAtMaximumTravel())
            {
                StopMotion("rotation-locked-until-maximum-travel");
                return false;
            }
            return TrySetAngle(
                detentIndex * settings.DetentStepDegrees,
                userAuthorized);
        }

        public bool IsPoseLegal()
        {
            bool aligned = IsAligned(AngleDegrees);
            return TravelMeters >= -settings.EndpointToleranceMeters
                && TravelMeters <= settings.MaximumTravelMeters
                    + settings.EndpointToleranceMeters
                && (aligned || IsAtMaximumTravel())
                && Mathf.Abs(
                    AngleDegrees / settings.DetentStepDegrees
                    - Mathf.Round(AngleDegrees / settings.DetentStepDegrees))
                    <= 0.001f
                && MatrixApproximately(
                    bottomExterior.localToWorldMatrix, bottomBaseline)
                && MatrixApproximately(fixedAxis.localToWorldMatrix, axisBaseline)
                && TopStackHeightResidualMeters <= 0.000001f
                && RenderersRemainAttached
                && HasPositiveScale(transform);
        }

        private bool IsAtMaximumTravel() =>
            Mathf.Abs(TravelMeters - settings.MaximumTravelMeters)
                <= settings.EndpointToleranceMeters;

        private void ApplyPose()
        {
            Quaternion yaw = Quaternion.AngleAxis(AngleDegrees, Vector3.forward);
            rotatingCarrier.localRotation = closedCarrierRotation * yaw;
            movingTop.localRotation = closedTopRotation * yaw;
            topLocalSlide.localPosition =
                closedSlidePosition + Vector3.down * TravelMeters;
        }

        private void CaptureBaselines()
        {
            closedSlidePosition = topLocalSlide.localPosition;
            closedCarrierRotation = rotatingCarrier.localRotation;
            closedTopRotation = movingTop.localRotation;
            bottomBaseline = bottomExterior.localToWorldMatrix;
            axisBaseline = fixedAxis.localToWorldMatrix;
            topStackBaselineWorldY = topLocalSlide.position.y;
            renderersBaseline = GetComponentsInChildren<Renderer>(true);
            movingTopRenderers = movingTop != null
                ? movingTop.GetComponentsInChildren<Renderer>(true)
                : Array.Empty<Renderer>();
            baselinesCaptured = true;
        }

        private void StopMotion(string transition)
        {
            StopVelocities();
            LastTransition = transition;
        }

        private void StopVelocities()
        {
            LinearVelocityMetersPerSecond = 0f;
            AngularVelocityDegreesPerSecond = 0f;
        }

        private void EmitSlideSteps(
            float previousTravel,
            float currentTravel,
            bool userAuthorized)
        {
            if (!userAuthorized
                || Mathf.Approximately(previousTravel, currentTravel))
            {
                return;
            }

            int previousStep = SlideStepIndex(previousTravel);
            int currentStep = SlideStepIndex(currentTravel);
            int direction = Math.Sign(currentStep - previousStep);
            for (int step = previousStep + direction;
                direction != 0 && step != currentStep + direction;
                step += direction)
            {
                float normalized = Mathf.Clamp01(
                    (float)step / settings.SlideStepCount);
                SemanticEventRaised?.Invoke(
                    FidgetSemanticEvent.MagneticEdgeProbe,
                    normalized);
            }
        }

        private int SlideStepIndex(float travelMeters)
        {
            return Mathf.Clamp(
                Mathf.FloorToInt(
                    (travelMeters + settings.EndpointToleranceMeters)
                    / settings.SlideStepMeters),
                0,
                settings.SlideStepCount);
        }

        private void EmitIfAuthorized(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal,
            bool userAuthorized)
        {
            if (userAuthorized)
            {
                SemanticEventRaised?.Invoke(
                    semanticEvent,
                    normalizedSignal);
            }
        }

        private static bool IsAligned(float angle) =>
            NormalizeDegrees(angle) <= 0.001f;

        private static float NormalizeDegrees(float angle)
        {
            float normalized = angle % 360f;
            return normalized < 0f ? normalized + 360f : normalized;
        }

        private static int PositiveModulo(int value, int modulus)
        {
            int result = value % modulus;
            return result < 0 ? result + modulus : result;
        }

        private static bool MatrixApproximately(Matrix4x4 a, Matrix4x4 b)
        {
            for (int row = 0; row < 4; row++)
            for (int column = 0; column < 4; column++)
            {
                if (Mathf.Abs(a[row, column] - b[row, column]) > 0.000001f)
                    return false;
            }
            return true;
        }

        private static float MatrixMaximumDifference(Matrix4x4 a, Matrix4x4 b)
        {
            float maximum = 0f;
            for (int row = 0; row < 4; row++)
            for (int column = 0; column < 4; column++)
                maximum = Mathf.Max(maximum, Mathf.Abs(a[row, column] - b[row, column]));
            return maximum;
        }

        private static bool HasPositiveScale(Transform item)
        {
            Vector3 scale = item.lossyScale;
            return scale.x > 0f && scale.y > 0f && scale.z > 0f;
        }
    }
}
