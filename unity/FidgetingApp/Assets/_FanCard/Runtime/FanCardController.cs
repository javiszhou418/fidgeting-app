using System;
using CodexUnityLab;
using FidgetingApp.EDC;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;
using UnityEngine.Serialization;

namespace FidgetingApp.FanCard
{
    [DisallowMultipleComponent]
    [DefaultExecutionOrder(-60)]
    public sealed class FanCardController : MonoBehaviour
    {
        [SerializeField] private Transform middleLayer;
        [FormerlySerializedAs("topLayer")]
        [SerializeField] private Transform outerLayer;
        [SerializeField] private Camera interactionCamera;
        [SerializeField] private Collider interactionSurface;
        [SerializeField] private Transform presentationFocus;
        [SerializeField] private FanCardDetentProfile detentProfile;
        [SerializeField] private FanCardFaceRankPresenter faceRankPresenter;
        [SerializeField, Min(0f)] private float maximumRayDistance = 5f;

        [SerializeField, HideInInspector]
        private Quaternion middleClosedRotation = Quaternion.identity;
        [SerializeField, HideInInspector]
        private Quaternion outerClosedRotation = Quaternion.identity;
        private FanCardMagneticTrack track;
        private FanCardDetentProfile ownedRuntimeProfile;
        private bool pointerWasPressed;
        private bool dragging;
        private bool interactionHapticsAuthorized;
        private bool gestureBrokeAway;
        private Vector2 pointerStartPosition;
        private Vector2 previousPointerPosition;
        private float pointerStartTarget;
        private float handTarget;
        private float pointerPressureBaseline;
        private float cumulativeGestureTravelPixels;
        private float cumulativeGestureProgress;
        private float filteredGestureSpeedScreenWidthsPerSecond;
        private float gestureSpeedNormalized;
        private float gestureDistanceNormalized;
        private float gestureIntensityNormalized;
        private float gestureFrequencyNormalized;
        private float lastGestureCompletionTime = float.NegativeInfinity;
        private float lastDirectionChangeTime = float.NegativeInfinity;
        private int previousGestureDirection;
        private float traversalAuthority;
        private float peakTraversalAuthority;
        private bool fastTraversalLatched;
        private float fastTraversalTarget;
        private int fastTraversalDirection;
        private bool flingDriveActive;
        private float flingDriveTarget;
        private float previousProgress;
        private float accumulatedActivityDegrees;
        private float activitySpeedRadians;
        private bool assistantDriveActive;
        private float assistantDirection = 1f;
        private float assistantSpeed = 0.20f;
        private bool libraryPreviewActive;

        public event Action<float> InteractionGestureCompleted;
        public event Action<FidgetSemanticEvent, float> SemanticEventRaised;

        public float Progress => track?.Position ?? 0f;
        public int CapturedDetentIndex => track?.CapturedDetentIndex ?? 0;
        public float MaximumRelativeAngleDegrees =>
            detentProfile != null
                ? detentProfile.MaximumRelativeAngleDegrees
                : FanCardDetentProfile.ReferenceMaximumRelativeAngleDegrees;
        public float MaximumTotalAngleDegrees =>
            detentProfile != null
                ? detentProfile.MaximumTotalAngleDegrees
                : FanCardDetentProfile.ReferenceMaximumTotalAngleDegrees;
        public bool IsDragging => dragging;
        public bool IsSettling => assistantDriveActive
            || flingDriveActive
            || (track != null && track.State == MagneticDetentState.Capturing);
        public bool IsDirectInteractionActive => dragging || flingDriveActive;
        public bool IsAssistantDriving => assistantDriveActive;
        public bool IsFlingDriving => flingDriveActive;
        public float TraversalAuthority => traversalAuthority;
        public float GestureSpeedNormalized => Mathf.Max(
            gestureSpeedNormalized,
            Mathf.Clamp01(GestureAngularSpeedDegreesPerSecond / 450f));
        public float GestureDistanceNormalized => gestureDistanceNormalized;
        public float GestureIntensityNormalized => gestureIntensityNormalized;
        public float GestureFrequencyNormalized => gestureFrequencyNormalized;
        public float GestureAngularSpeedDegreesPerSecond =>
            Mathf.Abs(activitySpeedRadians) * Mathf.Rad2Deg;
        public float AccumulatedActivityDegrees => accumulatedActivityDegrees;
        public float ActivitySpeedRadians => activitySpeedRadians;
        public MagneticDetentState MotionState =>
            track?.State ?? MagneticDetentState.Captured;
        public float MagneticLoad => track?.LoadNormalized ?? 0f;
        public Camera InteractionCamera => interactionCamera;
        public Collider InteractionSurface => interactionSurface;
        public FanCardDetentProfile Profile => detentProfile;
        public bool IsLibraryPreviewActive => libraryPreviewActive;

        public void Configure(
            Transform middle,
            Transform outer,
            Camera camera,
            Collider surface,
            FanCardDetentProfile profile,
            Transform focus = null)
        {
            middleLayer = middle;
            outerLayer = outer;
            interactionCamera = camera;
            interactionSurface = surface;
            detentProfile = profile;
            presentationFocus = focus;
            faceRankPresenter = GetComponent<FanCardFaceRankPresenter>();
            CacheClosedRotations();
            InitializeTrack(0f);
        }

        private void Awake()
        {
            faceRankPresenter = faceRankPresenter != null
                ? faceRankPresenter
                : GetComponent<FanCardFaceRankPresenter>();
            EnsureProfile();
            CacheClosedRotations();
            InitializeTrack(0f);
        }

        private void Update()
        {
            if (TryReadTouch(
                out Vector2 touchPosition,
                out bool touchPressed,
                out float touchPressure))
            {
                UpdatePointer(touchPosition, touchPressed, touchPressure);
            }
            else
            {
                ReadMouse();
            }

            float deltaTime = Mathf.Max(0f, Time.unscaledDeltaTime);
            bool handActive = dragging || flingDriveActive;
            bool hapticAuthorized = interactionHapticsAuthorized;
            float physicsTarget = flingDriveActive
                ? flingDriveTarget
                : handTarget;
            float physicsAuthority = flingDriveActive
                ? Mathf.Max(
                    traversalAuthority,
                    detentProfile.FastTraversalHoldAuthority)
                : traversalAuthority;
            if (assistantDriveActive && !dragging && !pointerWasPressed)
            {
                AdvanceAssistantTarget(deltaTime);
                handActive = true;
                hapticAuthorized = false;
                physicsTarget = handTarget;
                physicsAuthority = 0f;
            }

            AdvancePhysics(
                deltaTime,
                physicsTarget,
                handActive,
                physicsAuthority,
                hapticAuthorized);
            UpdateActivity(deltaTime);
            DecayGestureTelemetry(deltaTime);
        }

        private void OnDisable()
        {
            libraryPreviewActive = false;
            dragging = false;
            pointerWasPressed = false;
            assistantDriveActive = false;
            flingDriveActive = false;
            interactionHapticsAuthorized = false;
            gestureBrokeAway = false;
            ResetCurrentGestureTelemetry(false);
            ResetTraversalGesture();
            if (track != null && !track.IsAtRest)
            {
                track.Release();
            }
        }

        private void OnDestroy()
        {
            if (ownedRuntimeProfile == null)
            {
                return;
            }
#if UNITY_EDITOR
            if (!Application.isPlaying)
            {
                DestroyImmediate(ownedRuntimeProfile);
                return;
            }
#endif
            Destroy(ownedRuntimeProfile);
        }

        public bool ContainsScreenPoint(Vector2 screenPosition)
        {
            Camera camera = interactionCamera != null ? interactionCamera : Camera.main;
            if (camera == null || interactionSurface == null)
            {
                return false;
            }
            return interactionSurface.Raycast(
                camera.ScreenPointToRay(screenPosition),
                out _,
                maximumRayDistance);
        }

        public void ResetClosed()
        {
            EnsureTrack();
            dragging = false;
            pointerWasPressed = false;
            assistantDriveActive = false;
            flingDriveActive = false;
            interactionHapticsAuthorized = false;
            gestureBrokeAway = false;
            ResetCurrentGestureTelemetry(false);
            ResetTraversalGesture();
            track.ResetToDetent(0);
            handTarget = 0f;
            previousProgress = 0f;
            accumulatedActivityDegrees = 0f;
            activitySpeedRadians = 0f;
            ApplyVisualPose();
        }

        public void SetFanProgress(float progress)
        {
            EnsureClosedRotations();
            EnsureTrack();
            dragging = false;
            pointerWasPressed = false;
            assistantDriveActive = false;
            flingDriveActive = false;
            interactionHapticsAuthorized = false;
            gestureBrokeAway = false;
            ResetCurrentGestureTelemetry(false);
            ResetTraversalGesture();
            track.ResetToPosition(progress);
            handTarget = track.Position;
            previousProgress = track.Position;
            accumulatedActivityDegrees = 0f;
            activitySpeedRadians = 0f;
            ApplyVisualPose();
        }

        public void SetLibraryPreviewActive(bool active)
        {
            bool enteringDetail = libraryPreviewActive && !active;
            libraryPreviewActive = active;
            if (enteringDetail && Application.isPlaying)
            {
                faceRankPresenter?.RandomizeForDetailEntry();
            }
            ApplyVisualPose();
        }

        public void ReleaseDrag()
        {
            dragging = false;
            flingDriveActive = false;
            ResetCurrentGestureTelemetry(false);
            interactionHapticsAuthorized = false;
            ResetTraversalGesture();
            track?.Release();
        }

        public void SetAssistantDrive(bool active, float sourceSpeedMetersPerSecond)
        {
            EnsureTrack();
            assistantDriveActive = active;
            flingDriveActive = false;
            interactionHapticsAuthorized = false;
            gestureBrokeAway = false;
            ResetTraversalGesture();
            assistantSpeed = Mathf.Clamp(
                Mathf.Abs(sourceSpeedMetersPerSecond) / 0.030f * 0.20f,
                0.08f,
                0.55f);
            handTarget = track.Position;
            if (track.Position >= 0.88f)
            {
                assistantDirection = -1f;
            }
            else if (track.Position <= 0.12f)
            {
                assistantDirection = 1f;
            }
            if (!active && !track.IsAtRest)
            {
                track.Release();
            }
        }

        private void EnsureProfile()
        {
            if (detentProfile != null)
            {
                return;
            }
            ownedRuntimeProfile = ScriptableObject.CreateInstance<
                FanCardDetentProfile>();
            ownedRuntimeProfile.name = "Runtime_FanCardDetentProfile";
            ownedRuntimeProfile.hideFlags = HideFlags.HideAndDontSave;
            ownedRuntimeProfile.ApplyReferenceDefaults();
            detentProfile = ownedRuntimeProfile;
        }

        private void EnsureTrack()
        {
            if (track == null)
            {
                InitializeTrack(0f);
            }
        }

        private void InitializeTrack(float progress)
        {
            EnsureProfile();
            track = new FanCardMagneticTrack(detentProfile);
            track.ResetToPosition(progress);
            handTarget = track.Position;
            previousProgress = track.Position;
            ApplyVisualPose();
        }

        private void CacheClosedRotations()
        {
            middleClosedRotation = middleLayer != null
                ? middleLayer.localRotation
                : Quaternion.identity;
            outerClosedRotation = outerLayer != null
                ? outerLayer.localRotation
                : Quaternion.identity;
        }

        private void EnsureClosedRotations()
        {
            if (Quaternion.Dot(middleClosedRotation, middleClosedRotation)
                    < 0.5f
                || Quaternion.Dot(outerClosedRotation, outerClosedRotation) < 0.5f)
            {
                CacheClosedRotations();
            }
        }

        private bool TryReadTouch(
            out Vector2 position,
            out bool pressed,
            out float pressure)
        {
            Touchscreen touchscreen = Touchscreen.current;
            if (touchscreen != null)
            {
                TouchControl first = null;
                int count = 0;
                foreach (TouchControl touch in touchscreen.touches)
                {
                    if (!touch.press.isPressed)
                    {
                        continue;
                    }
                    first ??= touch;
                    count++;
                    if (count >= 2)
                    {
                        dragging = false;
                        pointerWasPressed = false;
                        interactionHapticsAuthorized = false;
                        gestureBrokeAway = false;
                        ResetCurrentGestureTelemetry(false);
                        flingDriveActive = false;
                        ResetTraversalGesture();
                        track?.Release();
                        position = first.position.ReadValue();
                        pressed = false;
                        pressure = 0f;
                        return true;
                    }
                }
                if (first != null)
                {
                    position = first.position.ReadValue();
                    pressed = true;
                    pressure = first.pressure.ReadValue();
                    return true;
                }
            }

            if (pointerWasPressed && Mouse.current == null)
            {
                position = previousPointerPosition;
                pressed = false;
                pressure = 0f;
                return true;
            }
            position = default;
            pressed = false;
            pressure = 0f;
            return false;
        }

        private void ReadMouse()
        {
            Mouse mouse = Mouse.current;
            if (mouse != null)
            {
                UpdatePointer(
                    mouse.position.ReadValue(),
                    mouse.leftButton.isPressed,
                    0f);
            }
        }

        private void UpdatePointer(
            Vector2 position,
            bool pressed,
            float pressure)
        {
            if (pressed && !pointerWasPressed)
            {
                BeginPointer(position, pressure);
            }
            else if (pressed && pointerWasPressed && dragging)
            {
                float deltaTime = Mathf.Max(
                    Time.unscaledDeltaTime,
                    detentProfile.MaximumSubstepSeconds);
                Vector2 screenDelta = position - previousPointerPosition;
                ResolveProjectedGestureDelta(
                    screenDelta,
                    out float progressStep,
                    out float signedTravelPixels);
                cumulativeGestureProgress += progressStep;
                cumulativeGestureTravelPixels += Mathf.Abs(signedTravelPixels);
                float referencePixels = Mathf.Max(1f, Screen.width);
                float rawScreenSpeed = Mathf.Abs(signedTravelPixels)
                    / deltaTime;
                float rawWidthsPerSecond = rawScreenSpeed / referencePixels;
                float speedBlend = 1f - Mathf.Pow(
                    0.5f,
                    deltaTime
                        / FanCardSpecifications.GestureSpeedFilterHalfLifeSeconds);
                filteredGestureSpeedScreenWidthsPerSecond = Mathf.Lerp(
                    filteredGestureSpeedScreenWidthsPerSecond,
                    rawWidthsPerSecond,
                    speedBlend);
                gestureSpeedNormalized = Mathf.InverseLerp(
                    detentProfile.FastTraversalStartScreenWidthsPerSecond,
                    detentProfile.FastTraversalFullScreenWidthsPerSecond,
                    filteredGestureSpeedScreenWidthsPerSecond);
                gestureDistanceNormalized = Mathf.InverseLerp(
                    FanCardSpecifications.GestureDistanceStartScreenWidths,
                    FanCardSpecifications.GestureDistanceFullScreenWidths,
                    cumulativeGestureTravelPixels / referencePixels);
                float pressureDelta = Mathf.Max(
                    0f,
                    pressure - pointerPressureBaseline);
                float pressureAuthority = Mathf.InverseLerp(
                    detentProfile.FastPressureDeltaStart,
                    detentProfile.FastPressureDeltaFull,
                    pressureDelta);
                UpdateGestureFrequency(progressStep);
                gestureIntensityNormalized = ResolveGestureIntensity(
                    gestureSpeedNormalized,
                    gestureDistanceNormalized,
                    pressureAuthority,
                    track?.LoadNormalized ?? 0f);
                float rawAuthority = ResolveTraversalAuthority(
                    rawScreenSpeed,
                    referencePixels,
                    pressureDelta,
                    detentProfile.FastTraversalStartScreenWidthsPerSecond,
                    detentProfile.FastTraversalFullScreenWidthsPerSecond,
                    detentProfile.FastPressureDeltaStart,
                    detentProfile.FastPressureDeltaFull,
                    gestureDistanceNormalized,
                    gestureFrequencyNormalized);
                UpdateTraversalAuthority(rawAuthority, deltaTime);
                peakTraversalAuthority = Mathf.Max(
                    peakTraversalAuthority,
                    rawAuthority);
                UpdateFastTraversalLatch(
                    progressStep,
                    rawAuthority,
                    gestureDistanceNormalized);

                handTarget = ResolveHandTargetForProjectedTravel(
                    pointerStartTarget,
                    cumulativeGestureProgress);
            }
            else if (!pressed && pointerWasPressed)
            {
                EndPointer(position);
            }

            previousPointerPosition = position;
            pointerWasPressed = pressed;
        }

        private void BeginPointer(Vector2 position, float pressure)
        {
            if (EventSystem.current != null
                && EventSystem.current.IsPointerOverGameObject())
            {
                return;
            }
            if (!ContainsScreenPoint(position))
            {
                return;
            }

            EnsureTrack();
            dragging = true;
            assistantDriveActive = false;
            flingDriveActive = false;
            interactionHapticsAuthorized = true;
            gestureBrokeAway = false;
            ResetTraversalGesture();
            handTarget = track.Position;
            pointerStartTarget = handTarget;
            ResetCurrentGestureTelemetry(true);
            pointerStartPosition = position;
            previousPointerPosition = position;
            pointerPressureBaseline = pressure;
        }

        private void EndPointer(Vector2 position)
        {
            if (!dragging)
            {
                return;
            }
            dragging = false;
            if (fastTraversalLatched
                && (!track.IsAtRest
                    || Mathf.Abs(track.Position - fastTraversalTarget) > 0.0001f))
            {
                flingDriveActive = true;
                flingDriveTarget = fastTraversalTarget;
                handTarget = flingDriveTarget;
                traversalAuthority = Mathf.Max(
                    traversalAuthority,
                    detentProfile.FastTraversalHoldAuthority);
            }
            else if (track.IsAtRest)
            {
                interactionHapticsAuthorized = false;
            }
            else
            {
                track.Release();
            }
            float travelPixels = Vector2.Distance(pointerStartPosition, position);
            float normalizedForce = Mathf.Clamp01(
                travelPixels / Mathf.Max(1f, Screen.width * 0.34f));
            InteractionGestureCompleted?.Invoke(Mathf.Max(
                0.18f,
                normalizedForce,
                gestureIntensityNormalized,
                peakTraversalAuthority));
            UpdateCompletedGestureFrequency(Time.unscaledTime);
            fastTraversalLatched = false;
            fastTraversalDirection = 0;
        }

        public static float ResolveTraversalAuthority(
            float screenSpeedPixelsPerSecond,
            float screenReferencePixels,
            float pressureDelta,
            float speedStartScreenWidthsPerSecond,
            float speedFullScreenWidthsPerSecond,
            float pressureStart,
            float pressureFull)
        {
            return ResolveTraversalAuthority(
                screenSpeedPixelsPerSecond,
                screenReferencePixels,
                pressureDelta,
                speedStartScreenWidthsPerSecond,
                speedFullScreenWidthsPerSecond,
                pressureStart,
                pressureFull,
                0f,
                0f);
        }

        public static float ResolveTraversalAuthority(
            float screenSpeedPixelsPerSecond,
            float screenReferencePixels,
            float pressureDelta,
            float speedStartScreenWidthsPerSecond,
            float speedFullScreenWidthsPerSecond,
            float pressureStart,
            float pressureFull,
            float normalizedDistance,
            float normalizedFrequency)
        {
            float safeReference = Mathf.Max(1f, screenReferencePixels);
            float widthsPerSecond = Mathf.Abs(screenSpeedPixelsPerSecond)
                / safeReference;
            float speedAuthority = Mathf.InverseLerp(
                speedStartScreenWidthsPerSecond,
                Mathf.Max(
                    speedStartScreenWidthsPerSecond + 0.01f,
                    speedFullScreenWidthsPerSecond),
                widthsPerSecond);
            float pressureAuthority = Mathf.InverseLerp(
                pressureStart,
                Mathf.Max(pressureStart + 0.01f, pressureFull),
                Mathf.Max(0f, pressureDelta));
            float distanceAuthority = Mathf.Clamp01(normalizedDistance) * 0.78f;
            float frequencyAuthority = Mathf.Clamp01(normalizedFrequency) * 0.38f;
            return Mathf.Clamp01(Mathf.Max(
                Mathf.Max(speedAuthority, pressureAuthority),
                Mathf.Max(distanceAuthority, frequencyAuthority)));
        }

        public static float ResolveGestureIntensity(
            float normalizedSpeed,
            float normalizedDistance,
            float normalizedPressure,
            float normalizedMagneticLoad)
        {
            return Mathf.Clamp01(
                Mathf.Clamp01(normalizedSpeed) * 0.46f
                + Mathf.Clamp01(normalizedDistance) * 0.30f
                + Mathf.Clamp01(normalizedPressure) * 0.12f
                + Mathf.Clamp01(normalizedMagneticLoad) * 0.12f);
        }

        private void UpdateTraversalAuthority(float target, float deltaTime)
        {
            float response = target > traversalAuthority
                ? detentProfile.TraversalAuthorityRise
                : detentProfile.TraversalAuthorityFall;
            float blend = response <= Mathf.Epsilon
                ? 1f
                : 1f - Mathf.Exp(-response * Mathf.Max(0f, deltaTime));
            traversalAuthority = Mathf.Lerp(
                traversalAuthority,
                Mathf.Clamp01(target),
                blend);
        }

        private void UpdateFastTraversalLatch(
            float signedProgressStep,
            float rawAuthority,
            float distanceNormalized)
        {
            if (Mathf.Abs(signedProgressStep) < 0.0005f)
            {
                return;
            }

            int direction = signedProgressStep > 0f ? 1 : -1;
            if (!fastTraversalLatched)
            {
                if (rawAuthority < detentProfile.FastTraversalLatchThreshold
                    || distanceNormalized
                        < FanCardSpecifications.FastTraversalMinimumDistance)
                {
                    return;
                }
                fastTraversalLatched = true;
                fastTraversalDirection = direction;
                fastTraversalTarget = direction > 0 ? 1f : 0f;
                traversalAuthority = Mathf.Max(
                    traversalAuthority,
                    detentProfile.FastTraversalHoldAuthority);
                return;
            }

            if (direction == fastTraversalDirection)
            {
                return;
            }

            if (rawAuthority >= detentProfile.FastTraversalReverseThreshold)
            {
                fastTraversalDirection = direction;
                fastTraversalTarget = direction > 0 ? 1f : 0f;
                traversalAuthority = Mathf.Max(
                    traversalAuthority,
                    detentProfile.FastTraversalHoldAuthority);
                return;
            }

            // A deliberate slow reversal exits ballistic traversal and
            // re-bases the hand servo at the current mechanism position.
            fastTraversalLatched = false;
            fastTraversalDirection = 0;
            pointerStartTarget = track.Position;
            cumulativeGestureProgress = 0f;
        }

        private void ResetTraversalGesture()
        {
            pointerPressureBaseline = 0f;
            traversalAuthority = 0f;
            peakTraversalAuthority = 0f;
            fastTraversalLatched = false;
            fastTraversalTarget = 0f;
            fastTraversalDirection = 0;
        }

        private void ResolveProjectedGestureDelta(
            Vector2 screenDelta,
            out float progressDelta,
            out float signedTravelPixels)
        {
            Camera camera = interactionCamera != null ? interactionCamera : Camera.main;
            if (camera == null || screenDelta.sqrMagnitude <= Mathf.Epsilon)
            {
                progressDelta = 0f;
                signedTravelPixels = 0f;
                return;
            }

            float progress = track?.VisualPosition ?? handTarget;
            float sampleStep = progress >= 0.985f ? -0.0125f : 0.0125f;
            float sampledProgress = Mathf.Clamp01(progress + sampleStep);
            sampleStep = sampledProgress - progress;
            if (Mathf.Abs(sampleStep) <= 0.0001f)
            {
                progressDelta = 0f;
                signedTravelPixels = 0f;
                return;
            }

            Vector3 currentWorld = transform.TransformPoint(
                ResolveFanCentroidLocal(progress));
            Vector3 sampledWorld = transform.TransformPoint(
                ResolveFanCentroidLocal(sampledProgress));
            Vector2 currentScreen = camera.WorldToScreenPoint(currentWorld);
            Vector2 sampledScreen = camera.WorldToScreenPoint(sampledWorld);
            Vector2 pixelsPerProgress = (sampledScreen - currentScreen) / sampleStep;
            float scale = pixelsPerProgress.magnitude;
            if (scale < 8f)
            {
                Vector3 pivotScreen = camera.WorldToScreenPoint(transform.position);
                Vector2 radial = currentScreen - (Vector2)pivotScreen;
                pixelsPerProgress = radial.sqrMagnitude > 1f
                    ? new Vector2(-radial.y, radial.x).normalized
                        * Mathf.Max(Screen.width, Screen.height) * 0.34f
                    : Vector2.right * Mathf.Max(Screen.width, Screen.height) * 0.34f;
                scale = pixelsPerProgress.magnitude;
            }

            Vector2 tangent = pixelsPerProgress / scale;
            signedTravelPixels = Vector2.Dot(screenDelta, tangent);
            progressDelta = Mathf.Clamp(
                signedTravelPixels / scale * FanCardSpecifications.GestureTravelGain,
                -FanCardSpecifications.MaximumGestureProgressPerFrame,
                FanCardSpecifications.MaximumGestureProgressPerFrame);
        }

        public static Vector3 ResolveFanCentroidLocal(float progress)
        {
            float clamped = Mathf.Clamp01(progress);
            Vector3 cardCenter = FanCardSpecifications.CardCenterFromPivot;
            Vector3 fixedCenter = cardCenter;
            Vector3 middleCenter = Vector3.up * FanCardSpecifications.LayerPitch
                + Quaternion.Euler(
                    0f,
                    FanCardSpecifications.OpeningRotationSign
                        * FanCardDetentProfile.ReferenceMaximumRelativeAngleDegrees
                        * clamped,
                    0f) * cardCenter;
            Vector3 outerCenter = Vector3.up * FanCardSpecifications.LayerPitch * 2f
                + Quaternion.Euler(
                    0f,
                    FanCardSpecifications.OpeningRotationSign
                        * FanCardDetentProfile.ReferenceMaximumTotalAngleDegrees
                        * clamped,
                    0f) * cardCenter;
            return (fixedCenter + middleCenter + outerCenter) / 3f;
        }

        public static float ResolveHandTargetForProjectedTravel(
            float startTarget,
            float cumulativeProgress)
        {
            return Mathf.Clamp01(startTarget + cumulativeProgress);
        }

        private void UpdateGestureFrequency(float progressStep)
        {
            if (Mathf.Abs(progressStep) < 0.0005f)
            {
                return;
            }

            int direction = progressStep > 0f ? 1 : -1;
            if (previousGestureDirection == 0)
            {
                previousGestureDirection = direction;
                lastDirectionChangeTime = Time.unscaledTime;
                return;
            }
            if (direction == previousGestureDirection)
            {
                return;
            }

            float interval = Time.unscaledTime - lastDirectionChangeTime;
            if (interval > 0.04f)
            {
                float hertz = 1f / interval;
                gestureFrequencyNormalized = Mathf.Max(
                    gestureFrequencyNormalized,
                    Mathf.InverseLerp(
                        FanCardSpecifications.GestureFrequencyMinimumHertz,
                        FanCardSpecifications.GestureFrequencyFullHertz,
                        hertz));
            }
            previousGestureDirection = direction;
            lastDirectionChangeTime = Time.unscaledTime;
        }

        private void UpdateCompletedGestureFrequency(float completionTime)
        {
            if (!float.IsNegativeInfinity(lastGestureCompletionTime))
            {
                float interval = completionTime - lastGestureCompletionTime;
                if (interval > 0.04f)
                {
                    gestureFrequencyNormalized = Mathf.Max(
                        gestureFrequencyNormalized,
                        Mathf.InverseLerp(
                            FanCardSpecifications.GestureFrequencyMinimumHertz,
                            FanCardSpecifications.GestureFrequencyFullHertz,
                            1f / interval));
                }
            }
            lastGestureCompletionTime = completionTime;
        }

        private void ResetCurrentGestureTelemetry(bool preserveFrequency)
        {
            cumulativeGestureTravelPixels = 0f;
            cumulativeGestureProgress = 0f;
            filteredGestureSpeedScreenWidthsPerSecond = 0f;
            gestureSpeedNormalized = 0f;
            gestureDistanceNormalized = 0f;
            gestureIntensityNormalized = 0f;
            previousGestureDirection = 0;
            lastDirectionChangeTime = float.NegativeInfinity;
            if (!preserveFrequency)
            {
                gestureFrequencyNormalized = 0f;
                lastGestureCompletionTime = float.NegativeInfinity;
            }
        }

        private void DecayGestureTelemetry(float deltaTime)
        {
            if (dragging || deltaTime <= 0f)
            {
                return;
            }
            float fastDecay = 1f - Mathf.Pow(0.5f, deltaTime / 0.12f);
            gestureSpeedNormalized = Mathf.Lerp(
                gestureSpeedNormalized,
                0f,
                fastDecay);
            gestureIntensityNormalized = Mathf.Lerp(
                gestureIntensityNormalized,
                0f,
                fastDecay);
            gestureDistanceNormalized = Mathf.Lerp(
                gestureDistanceNormalized,
                0f,
                fastDecay);
            float frequencyDecay = 1f - Mathf.Pow(
                0.5f,
                deltaTime
                    / FanCardSpecifications.GestureFrequencyDecayHalfLifeSeconds);
            gestureFrequencyNormalized = Mathf.Lerp(
                gestureFrequencyNormalized,
                0f,
                frequencyDecay);
        }

        public static float ResolveHandTargetForPointerArc(
            float startTarget,
            float accumulatedArcDegrees,
            float totalTravelDegrees)
        {
            float safeTravel = Mathf.Max(1f, Mathf.Abs(totalTravelDegrees));
            return Mathf.Clamp01(
                startTarget
                    + accumulatedArcDegrees
                    * FanCardSpecifications.PointerAngularGain
                    / safeTravel);
        }

        private void AdvanceAssistantTarget(float deltaTime)
        {
            handTarget = Mathf.Clamp01(
                handTarget + assistantDirection * assistantSpeed * deltaTime);
            if (track.IsAtRest)
            {
                if (track.CapturedDetentIndex >= detentProfile.DetentCount - 1)
                {
                    assistantDirection = -1f;
                }
                else if (track.CapturedDetentIndex <= 0)
                {
                    assistantDirection = 1f;
                }
            }
        }

        private void AdvancePhysics(
            float deltaTime,
            float target,
            bool handActive,
            float physicsAuthority,
            bool hapticAuthorized)
        {
            EnsureTrack();
            FanCardStepResult result = track.Step(
                deltaTime,
                target,
                handActive,
                physicsAuthority);
            if (result.BrokeAway)
            {
                gestureBrokeAway = true;
                EmitSemanticIfAuthorized(
                    FidgetSemanticEvent.Breakaway,
                    1f,
                    hapticAuthorized);
            }
            for (int crossing = 0; crossing < result.CrossedDetentCount; crossing++)
            {
                EmitSemanticIfAuthorized(
                    FidgetSemanticEvent.DetentCrossed,
                    Mathf.Clamp01(
                        Mathf.Abs(track.Velocity)
                        / detentProfile.FastMaximumHeldSpeed),
                    hapticAuthorized);
            }
            if (result.Captured)
            {
                if (gestureBrokeAway)
                {
                    EmitSemanticIfAuthorized(
                        FidgetSemanticEvent.DetentCaptured,
                        1f,
                        hapticAuthorized);
                }
                gestureBrokeAway = false;
                if (flingDriveActive
                    && Mathf.Abs(track.Position - flingDriveTarget) < 0.0001f)
                {
                    flingDriveActive = false;
                    handTarget = track.Position;
                    ResetTraversalGesture();
                }
                if (!dragging && !assistantDriveActive && !flingDriveActive)
                {
                    interactionHapticsAuthorized = false;
                    ResetTraversalGesture();
                }
            }
            ApplyVisualPose();
        }

        private void EmitSemanticIfAuthorized(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal,
            bool authorized)
        {
            if (authorized)
            {
                SemanticEventRaised?.Invoke(semanticEvent, normalizedSignal);
            }
        }

        private void ApplyVisualPose()
        {
            if (middleLayer == null || outerLayer == null || track == null)
            {
                return;
            }
            float visual = libraryPreviewActive
                ? FanCardSpecifications.LibraryPreviewProgress
                : track.VisualPosition;
            if (presentationFocus != null)
            {
                presentationFocus.localPosition = ResolveFanCentroidLocal(visual);
            }
            middleLayer.localRotation = middleClosedRotation
                * Quaternion.Euler(
                    0f,
                    FanCardSpecifications.OpeningRotationSign
                        * detentProfile.MaximumRelativeAngleDegrees * visual,
                    0f);
            outerLayer.localRotation = outerClosedRotation
                * Quaternion.Euler(
                    0f,
                    FanCardSpecifications.OpeningRotationSign
                        * detentProfile.MaximumTotalAngleDegrees * visual,
                    0f);
        }

        private void UpdateActivity(float deltaTime)
        {
            float current = track?.Position ?? 0f;
            float delta = current - previousProgress;
            previousProgress = current;
            float safeDeltaTime = Mathf.Max(0.0001f, deltaTime);
            if (Mathf.Abs(delta) > 0.00001f)
            {
                float degrees = delta * detentProfile.MaximumTotalAngleDegrees;
                accumulatedActivityDegrees += degrees;
                float rawSpeed = degrees * Mathf.Deg2Rad / safeDeltaTime;
                activitySpeedRadians = Mathf.Lerp(
                    activitySpeedRadians,
                    rawSpeed,
                    1f - Mathf.Exp(-18f * safeDeltaTime));
                return;
            }
            activitySpeedRadians = Mathf.Lerp(
                activitySpeedRadians,
                0f,
                1f - Mathf.Exp(-safeDeltaTime / 0.22f));
            if (Mathf.Abs(activitySpeedRadians) < 0.02f)
            {
                activitySpeedRadians = 0f;
            }
        }
    }
}
