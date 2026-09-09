using System;
using System.Collections.Generic;
using CodexUnityLab;
using FidgetingApp.EDC.Gate12R002;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;

namespace FidgetingApp.EDC
{
    [DisallowMultipleComponent]
    public sealed class EdcSliderController : MonoBehaviour
    {
        public static readonly Vector3 DefaultInteractionSurfaceSize =
            new(0.094f, 0.032f, 0.058f);

        [SerializeField] private Transform sliderGroup;
        [SerializeField] private Camera interactionCamera;
        [SerializeField] private Collider interactionSurface;
        [SerializeField] private MagneticSlideTileShippingCoordinator
            shippingCoordinator;
        [SerializeField] private SharedPresentationGestureController
            presentationGestures;
        [SerializeField] private LinearMagneticDetentProfile magneticProfile;
        [SerializeField, Min(0.001f)] private float travelDistance =
            LinearMagneticDetentProfile.HeavyTravelMeters;
        [SerializeField, Range(0f, 1f)] private float slideProgress;
        [SerializeField, Min(0f)] private float maximumRayDistance = 5f;

        private Vector3 closedLocalPosition;
        private Quaternion closedLocalRotation;
        private MagneticDetentTrack1D magneticTrack;
        private LinearMagneticDetentProfile ownedRuntimeProfile;
        private bool dragging;
        private bool pointerWasPressed;
        private Vector2 previousPointerPosition;
        private Vector2 pointerStartPosition;
        private float pointerStartTime;
        private float cumulativeGestureTravelPixels;
        private float gestureSpeedNormalized;
        private float gestureDistanceNormalized;
        private float gestureIntensityNormalized;
        private float gestureFrequencyNormalized;
        private float lastGestureCompletionTime = float.NegativeInfinity;
        private float handTargetMeters;
        private bool poweredDriveActive;
        private float poweredTargetMeters;
        private bool interactionHapticsAuthorized;
        private float previousHandTargetMeters;
        private float filteredFingerSpeedMetersPerSecond;
        private float slowIntentEnterElapsed;
        private float slowIntentExitElapsed;
        private float stationaryElapsed;
        private bool slowIntentActive;
        private bool fingerStationary;
        private readonly MagneticEdgeProbeSequence edgeProbeSequence = new();
        private float previousActivityProgress;
        private float accumulatedActivityDegrees;
        private float activitySpeedRadians;
        private bool assistantDriveActive;
        private float assistantDirection = 1f;
        private float assistantTargetSpeedMetersPerSecond;
        private float previousPhysicalPosition;
        private int lastTravelDirection;
        private int crossingTremorDirection;
        private float crossingTremorElapsed;
        private bool crossingTremorActive;
        private Transform[] recoilVisuals = Array.Empty<Transform>();
        private Vector3[] recoilClosedPositions = Array.Empty<Vector3>();
        private Quaternion[] recoilClosedRotations = Array.Empty<Quaternion>();
        private ShippingGestureMode shippingGestureMode;
        private float shippingGestureStartTravelMeters;
        private float shippingGestureStartAngleDegrees;
        private Vector3 shippingGestureStartRadialWorld;
        private Vector3 shippingGestureLastRadialWorld;
        private Vector3 shippingGestureRotationAxisWorld;
        private bool shippingGestureHasRotationSample;
        private float shippingGestureAccumulatedAngleDegrees;
        private float shippingGestureLastAngleDegrees;
        private float shippingGestureLastTime;
        private bool shippingWaitForTouchesToClear;
        private MagneticSlideTileShippingMechanism subscribedShippingMechanism;
        private bool lastPointerHitProduct;
        private bool lastPointerBlockedByUi;
        private readonly MagneticSlideTileDeviceDrive deviceDrive = new();
        private Vector3 deviceGravityWorld;
        private Vector3 deviceAccelerationWorld;
        private Vector3 devicePhoneAngularVelocityWorld;
        private bool deviceSampleAvailable;

        public event Action<float> InteractionGestureCompleted;
        public event Action<FidgetSemanticEvent, float> SemanticEventRaised;

        public float SlideProgress => shippingCoordinator != null
            ? shippingCoordinator.Mechanism.TravelMeters
                / shippingCoordinator.Settings.MaximumTravelMeters
            : slideProgress;
        public float TravelDistance => shippingCoordinator != null
            ? shippingCoordinator.Settings.MaximumTravelMeters
            : travelDistance;
        public bool IsDragging => dragging;
        public bool IsSettling => poweredDriveActive
            || (magneticTrack != null
                && magneticTrack.State == MagneticDetentState.Capturing);
        public float AccumulatedActivityDegrees => accumulatedActivityDegrees;
        public float ActivitySpeedRadians => activitySpeedRadians;
        public float GestureSpeedMillimetersPerSecond =>
            Mathf.Max(
                Mathf.Abs(filteredFingerSpeedMetersPerSecond),
                Mathf.Abs(magneticTrack?.VelocityMetersPerSecond ?? 0f)) * 1000f;
        public float GestureSpeedNormalized => Mathf.Max(
            gestureSpeedNormalized,
            Mathf.Clamp01(GestureSpeedMillimetersPerSecond / 120f));
        public float GestureIntensityNormalized => gestureIntensityNormalized;
        public float GestureFrequencyNormalized => gestureFrequencyNormalized;
        public Camera InteractionCamera => interactionCamera;
        public Collider InteractionSurface => interactionSurface;
        public MagneticSlideTileShippingCoordinator ShippingCoordinator =>
            shippingCoordinator;
        public bool UsesShippingMechanism => shippingCoordinator != null;
        public bool LastPointerHitProduct => lastPointerHitProduct;
        public bool LastPointerBlockedByUi => lastPointerBlockedByUi;
        public SharedPresentationGestureController PresentationGestures =>
            presentationGestures;
        public int TouchReceiptCount { get; private set; }
        public int InputUpdateCount { get; private set; }
        public int SlideInputCount { get; private set; }
        public int RotationInputCount { get; private set; }
        public int SemanticEventCount { get; private set; }
        public int LastSemanticDetentDirection { get; private set; }
        public int LastSemanticDetentIndex { get; private set; }
        public bool IsAssistantDriving => assistantDriveActive;
        public bool IsDeviceDriving => deviceDrive.IsActive;
        public MagneticSlideTileDeviceSample LastDeviceSample { get; private set; }
        public LinearMagneticDetentProfile Profile => magneticProfile;
        public MagneticDetentState MotionState => magneticTrack != null
            ? magneticTrack.State
            : MagneticDetentState.Captured;
        public float MagneticLoad => magneticTrack?.LoadNormalized ?? 0f;
        public bool HasSlowFingerIntent => slowIntentActive;
        public bool IsFingerStationary => fingerStationary;
        public int CapturedDetentIndex => magneticTrack?.CapturedDetentIndex
            ?? magneticProfile?.DefaultDetentIndex
            ?? 0;

        /// <summary>
        /// Uses the slider's authoritative interaction surface for secondary
        /// product gestures such as the appearance-editor long press.
        /// </summary>
        public bool ContainsScreenPoint(Vector2 screenPosition)
        {
            Camera camera = interactionCamera != null ? interactionCamera : Camera.main;
            if (camera == null || interactionSurface == null)
            {
                return false;
            }

            Ray ray = camera.ScreenPointToRay(screenPosition);
            return interactionSurface.Raycast(ray, out _, maximumRayDistance);
        }

        public void Configure(
            Transform movableGroup,
            Camera camera,
            Collider surface,
            LinearMagneticDetentProfile profile)
        {
            sliderGroup = movableGroup;
            interactionCamera = camera;
            interactionSurface = surface;
            SetProfile(profile);
            closedLocalPosition = sliderGroup != null
                ? sliderGroup.localPosition
                : Vector3.zero;
            closedLocalRotation = sliderGroup != null
                ? sliderGroup.localRotation
                : Quaternion.identity;
            CacheRecoilVisuals();
            InitializeTrack(slideProgress);
        }

        public void ConfigureShipping(
            MagneticSlideTileShippingCoordinator coordinator,
            Camera camera,
            Collider surface,
            LinearMagneticDetentProfile hapticProfile,
            SharedPresentationGestureController sharedPresentationGestures)
        {
            UnsubscribeShippingMechanism();
            shippingCoordinator = coordinator;
            sliderGroup = coordinator != null
                ? coordinator.Mechanism.transform
                : null;
            interactionCamera = camera;
            interactionSurface = surface;
            magneticProfile = hapticProfile;
            presentationGestures = sharedPresentationGestures;
            dragging = false;
            pointerWasPressed = false;
            shippingWaitForTouchesToClear = false;
            shippingGestureMode = ShippingGestureMode.None;
            ResetGestureTelemetry(false);
            SubscribeShippingMechanism();
        }

        private void Awake()
        {
            if (shippingCoordinator != null)
            {
                dragging = false;
                pointerWasPressed = false;
                shippingGestureMode = ShippingGestureMode.None;
                SubscribeShippingMechanism();
                Debug.Log(
                    "[MagneticSlideRuntime] input-ready "
                    + $"surface={interactionSurface?.name ?? "missing"} "
                    + $"profile={magneticProfile?.name ?? "missing"}");
                return;
            }
            if (sliderGroup != null)
            {
                closedLocalPosition = sliderGroup.localPosition;
                closedLocalRotation = sliderGroup.localRotation;
            }
            EnsureProfile();
            CacheRecoilVisuals();
            InitializeTrack(slideProgress);
        }

        private void OnEnable()
        {
            SubscribeShippingMechanism();
        }

        private void Update()
        {
            if (shippingCoordinator != null)
            {
                InputUpdateCount++;
                UpdateShippingInput();
                AdvanceShippingDeviceDrive(Mathf.Max(0f, Time.unscaledDeltaTime));
                DecayGestureTelemetry(Mathf.Max(0f, Time.unscaledDeltaTime));
                if (!dragging)
                {
                    activitySpeedRadians = Mathf.Lerp(
                        activitySpeedRadians,
                        0f,
                        1f - Mathf.Exp(-Time.unscaledDeltaTime / 0.22f));
                }
                return;
            }
            if (TryReadTouch(out Vector2 touchPosition, out bool touchPressed))
            {
                UpdatePointer(touchPosition, touchPressed);
            }
            else
            {
                ReadMouse();
            }

            float deltaTime = Mathf.Max(0f, Time.unscaledDeltaTime);
            UpdateFingerIntent(deltaTime);
            bool handActive = dragging;
            float target = handTargetMeters;
            bool hapticAuthorized = interactionHapticsAuthorized;

            if (assistantDriveActive && !dragging && !pointerWasPressed)
            {
                AdvanceAssistantTarget(deltaTime);
                handActive = true;
                target = handTargetMeters;
                hapticAuthorized = false;
            }
            else if (poweredDriveActive && !dragging)
            {
                handActive = true;
                target = poweredTargetMeters;
            }

            AdvancePhysics(
                deltaTime,
                target,
                handActive,
                hapticAuthorized,
                dragging && slowIntentActive);
            AdvanceCrossingTremor(deltaTime);
            UpdateActivity(deltaTime);
            DecayGestureTelemetry(deltaTime);
        }

        private void OnDisable()
        {
            dragging = false;
            pointerWasPressed = false;
            poweredDriveActive = false;
            assistantDriveActive = false;
            interactionHapticsAuthorized = false;
            shippingGestureMode = ShippingGestureMode.None;
            shippingWaitForTouchesToClear = false;
            deviceDrive.Cancel();
            deviceSampleAvailable = false;
            UnsubscribeShippingMechanism();
            ResetEdgeProbeState();
            ResetFingerIntent();
            ResetGestureTelemetry(false);
            if (magneticTrack != null && !magneticTrack.IsAtRest)
            {
                magneticTrack.Release();
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

        public void Toggle()
        {
            float reference = poweredDriveActive
                ? poweredTargetMeters
                : magneticTrack?.PositionMeters ?? slideProgress * travelDistance;
            BeginPoweredTravel(reference >= travelDistance * 0.5f ? 0f : travelDistance, false);
        }

        public void SetSlideProgress(float progress)
        {
            if (shippingCoordinator != null)
            {
                shippingCoordinator.TryApplySlideInput(
                    Mathf.Clamp01(progress)
                    * shippingCoordinator.Settings.MaximumTravelMeters,
                    false);
                return;
            }
            EnsureProfile();
            EnsureTrack();
            dragging = false;
            poweredDriveActive = false;
            assistantDriveActive = false;
            interactionHapticsAuthorized = false;
            ResetEdgeProbeState();
            ResetFingerIntent();
            ResetGestureTelemetry(false);
            float clamped = Mathf.Clamp01(progress);
            magneticTrack.ResetToPosition(clamped * travelDistance);
            slideProgress = magneticTrack.PositionMeters / travelDistance;
            handTargetMeters = magneticTrack.PositionMeters;
            previousPhysicalPosition = magneticTrack.PositionMeters;
            ResetCrossingTremor();
            ApplyVisualPosition();
            previousActivityProgress = slideProgress;
            accumulatedActivityDegrees = 0f;
            activitySpeedRadians = 0f;
        }

        /// <summary>
        /// Returns to the authored interior rest detent. This is instantaneous
        /// and silent, and leaves a real magnetic well reachable on both sides.
        /// </summary>
        public void ResetToDefaultDetent()
        {
            if (shippingCoordinator != null)
            {
                shippingCoordinator.ResetShippingPose();
                accumulatedActivityDegrees = 0f;
                activitySpeedRadians = 0f;
                dragging = false;
                pointerWasPressed = false;
                shippingGestureMode = ShippingGestureMode.None;
                ResetGestureTelemetry(false);
                return;
            }
            EnsureProfile();
            SetSlideProgress(magneticProfile.DefaultPositionMeters / travelDistance);
        }

        public void SetAssistantDrive(bool active, float targetSpeedMetersPerSecond)
        {
            if (shippingCoordinator != null)
                return;
            assistantDriveActive = active;
            assistantTargetSpeedMetersPerSecond = Mathf.Clamp(
                Mathf.Abs(targetSpeedMetersPerSecond),
                0.005f,
                0.12f);
            interactionHapticsAuthorized = false;
            ResetEdgeProbeState();
            if (active)
            {
                poweredDriveActive = false;
                EnsureTrack();
                handTargetMeters = magneticTrack.PositionMeters;
                if (slideProgress >= 0.88f)
                {
                    assistantDirection = -1f;
                }
                else if (slideProgress <= 0.12f)
                {
                    assistantDirection = 1f;
                }
                return;
            }

            if (magneticTrack != null && !magneticTrack.IsAtRest)
            {
                magneticTrack.Release();
            }
        }

        public void ReleaseDrag()
        {
            dragging = false;
            poweredDriveActive = false;
            ResetEdgeProbeState();
            ResetFingerIntent();
            ResetGestureTelemetry(false);
            shippingGestureMode = ShippingGestureMode.None;
            magneticTrack?.Release();
        }

        /// <summary>
        /// World-space Core Motion sample (gravity and user acceleration in g,
        /// phone angular velocity in Unity sign) from the device motion
        /// controller. The controller only supplies samples; the shipping
        /// mechanism keeps pose, interlock, and semantic-event authority.
        /// </summary>
        public void SetDeviceMotionSample(
            Vector3 gravityWorld,
            Vector3 userAccelerationWorld,
            Vector3 phoneAngularVelocityWorld,
            bool available)
        {
            deviceGravityWorld = gravityWorld;
            deviceAccelerationWorld = userAccelerationWorld;
            devicePhoneAngularVelocityWorld = phoneAngularVelocityWorld;
            if (deviceSampleAvailable && !available)
            {
                deviceDrive.Cancel();
            }
            deviceSampleAvailable = available;
        }

        /// <summary>
        /// Maps the world sample onto the mechanism: gravity torque on the
        /// moving top about the carrier axis, phone twist about that axis in
        /// the mechanism's angle sign, and acceleration along the slide.
        /// </summary>
        public static MagneticSlideTileDeviceSample ResolveDeviceSample(
            Vector3 gravityWorld,
            Vector3 userAccelerationWorld,
            Vector3 phoneAngularVelocityWorld,
            Vector3 rotationAxisWorld,
            Vector3 movingTopLeverWorld,
            Vector3 slideDirectionWorld)
        {
            float torque = FidgetingApp.Product.DeviceMotionMechanismCoupling
                .ResolveGravityTorqueNormalized(
                    movingTopLeverWorld,
                    gravityWorld,
                    rotationAxisWorld);
            torque = FidgetingApp.Product.DeviceMotionMechanismCoupling.ApplyDeadZone(
                torque,
                FidgetingApp.Product.DeviceMotionMechanismCoupling.GravityTorqueDeadZone);
            float phoneRate = rotationAxisWorld.sqrMagnitude > Mathf.Epsilon
                ? Vector3.Dot(phoneAngularVelocityWorld, rotationAxisWorld.normalized)
                : 0f;
            phoneRate = Mathf.Clamp(
                FidgetingApp.Product.DeviceMotionMechanismCoupling.ApplyDeadZone(
                    phoneRate,
                    FidgetingApp.Product.DeviceMotionMechanismCoupling
                        .RotationRateDeadZoneRadians),
                -FidgetingApp.Product.DeviceMotionMechanismCoupling.MaximumRotationRateRadians,
                FidgetingApp.Product.DeviceMotionMechanismCoupling.MaximumRotationRateRadians);
            float slideAcceleration = slideDirectionWorld.sqrMagnitude > Mathf.Epsilon
                ? Vector3.Dot(userAccelerationWorld, slideDirectionWorld.normalized)
                : 0f;
            return new MagneticSlideTileDeviceSample(
                torque,
                phoneRate * Mathf.Rad2Deg,
                slideAcceleration);
        }

        private void AdvanceShippingDeviceDrive(float deltaTime)
        {
            if (shippingCoordinator == null
                || shippingCoordinator.Mechanism == null
                || !shippingCoordinator.CandidatePreviewEnabled)
            {
                return;
            }
            if (!deviceSampleAvailable
                || dragging
                || pointerWasPressed
                || shippingWaitForTouchesToClear
                || presentationGestures?.IsPinching == true
                || presentationGestures?.IsOrbiting == true)
            {
                deviceDrive.Cancel();
                return;
            }

            MagneticSlideTileShippingMechanism mechanism = shippingCoordinator.Mechanism;
            MagneticSlideTileMechanismSettings settings = shippingCoordinator.Settings;
            MagneticSlideTileDeviceSample sample = ResolveDeviceSample(
                deviceGravityWorld,
                deviceAccelerationWorld,
                devicePhoneAngularVelocityWorld,
                mechanism.RotationAxisWorld,
                mechanism.ResolveMovingTopLeverWorld(),
                mechanism.SlideDirectionWorld);
            LastDeviceSample = sample;
            MagneticSlideTileDeviceState state = new(
                mechanism.TravelMeters,
                settings.MaximumTravelMeters,
                mechanism.AtMaximumTravel,
                mechanism.IsAngleAligned,
                mechanism.RotationBrokenAway,
                mechanism.UnwrappedAngleDegrees,
                settings.DetentStepDegrees,
                settings.BreakawayDegrees,
                settings.CaptureRadiusDegrees);
            MagneticSlideTileDeviceCommand command = deviceDrive.Step(deltaTime, sample, state);
            ApplyDeviceCommand(command);
        }

        private void ApplyDeviceCommand(in MagneticSlideTileDeviceCommand command)
        {
            // Device tilt, twist, and flick are explicit user input, so every
            // resulting pose change is user-authorized and may emit semantics.
            switch (command.Kind)
            {
                case MagneticSlideTileDeviceCommandKind.BeginRotation:
                    shippingCoordinator.Mechanism.TryBeginRotation(
                        command.BreakawaySignDegrees,
                        true);
                    break;
                case MagneticSlideTileDeviceCommandKind.SetAngle:
                    shippingCoordinator.Mechanism.TrySetAngle(command.Value, true);
                    break;
                case MagneticSlideTileDeviceCommandKind.CaptureAngle:
                    shippingCoordinator.Mechanism.TryCaptureNearestDetent(command.Value, true);
                    break;
                case MagneticSlideTileDeviceCommandKind.SetTravel:
                    shippingCoordinator.Mechanism.TrySetTravel(command.Value, true);
                    break;
            }
        }

        private void SetProfile(LinearMagneticDetentProfile profile)
        {
            if (profile == null)
            {
                EnsureProfile();
                return;
            }
            magneticProfile = profile;
            travelDistance = Mathf.Max(0.001f, profile.TravelMeters);
        }

        private void EnsureProfile()
        {
            if (magneticProfile != null)
            {
                travelDistance = Mathf.Max(0.001f, magneticProfile.TravelMeters);
                return;
            }

            ownedRuntimeProfile = ScriptableObject.CreateInstance<LinearMagneticDetentProfile>();
            ownedRuntimeProfile.name = "Runtime_HeavyMagneticDetentProfile";
            ownedRuntimeProfile.hideFlags = HideFlags.HideAndDontSave;
            ownedRuntimeProfile.ApplyHeavyDefaults();
            magneticProfile = ownedRuntimeProfile;
            travelDistance = magneticProfile.TravelMeters;
        }

        private void InitializeTrack(float initialProgress)
        {
            EnsureProfile();
            magneticTrack = new MagneticDetentTrack1D(magneticProfile);
            magneticTrack.ResetToPosition(Mathf.Clamp01(initialProgress) * travelDistance);
            slideProgress = magneticTrack.PositionMeters / travelDistance;
            handTargetMeters = magneticTrack.PositionMeters;
            previousPhysicalPosition = magneticTrack.PositionMeters;
            ApplyVisualPosition();
            previousActivityProgress = slideProgress;
        }

        private void EnsureTrack()
        {
            if (magneticTrack == null)
            {
                InitializeTrack(slideProgress);
            }
        }

        private void UpdateShippingInput()
        {
            Touchscreen touchscreen = Touchscreen.current;
            if (touchscreen != null)
            {
                TouchControl firstPressedTouch = null;
                int pressedTouchCount = 0;
                foreach (TouchControl touch in touchscreen.touches)
                {
                    if (!touch.press.isPressed)
                        continue;
                    pressedTouchCount++;
                    firstPressedTouch ??= touch;
                }

                if (pressedTouchCount >= 2
                    || presentationGestures?.IsPinching == true)
                {
                    shippingWaitForTouchesToClear = true;
                    CancelShippingPointerForPresentation();
                    return;
                }

                if (shippingWaitForTouchesToClear)
                {
                    if (pressedTouchCount == 0)
                        shippingWaitForTouchesToClear = false;
                    else
                        return;
                }

                if (firstPressedTouch != null)
                {
                    UpdateShippingPointer(
                        firstPressedTouch.position.ReadValue(),
                        true);
                    return;
                }

                if (pointerWasPressed)
                {
                    UpdateShippingPointer(previousPointerPosition, false);
                    return;
                }
            }

            if (shippingWaitForTouchesToClear)
                return;

            Mouse mouse = Mouse.current;
            if (mouse != null)
            {
                UpdateShippingPointer(
                    mouse.position.ReadValue(),
                    mouse.leftButton.isPressed);
                return;
            }

            if (pointerWasPressed)
                UpdateShippingPointer(previousPointerPosition, false);
        }

        private void CancelShippingPointerForPresentation()
        {
            bool hadToyPointer = dragging || pointerWasPressed;
            dragging = false;
            pointerWasPressed = false;
            shippingGestureMode = ShippingGestureMode.None;
            activitySpeedRadians = 0f;
            ResetGestureTelemetry(false);
            if (hadToyPointer)
            {
                Debug.Log(
                    "[MagneticSlideRuntime] toy-input-cancelled-for-pinch");
            }
        }

        private void UpdateShippingPointer(Vector2 position, bool pressed)
        {
            if (pressed && !pointerWasPressed)
            {
                BeginShippingPointer(position);
            }
            else if (pressed && pointerWasPressed && dragging)
            {
                MoveShippingPointer(position);
            }
            else if (!pressed && pointerWasPressed)
            {
                EndShippingPointer(position);
            }

            previousPointerPosition = position;
            pointerWasPressed = pressed;
        }

        private void BeginShippingPointer(Vector2 position)
        {
            lastPointerBlockedByUi = EventSystem.current != null
                && EventSystem.current.IsPointerOverGameObject();
            lastPointerHitProduct = ContainsScreenPoint(position);
            bool presentationOwnsPointer =
                presentationGestures?.IsOrbiting == true
                || presentationGestures?.IsPinching == true;
            TouchReceiptCount++;
            Debug.Log(
                "[MagneticSlideRuntime] touch-begin "
                + $"x={position.x:F1} y={position.y:F1} "
                + $"hit={lastPointerHitProduct} "
                + $"ui={lastPointerBlockedByUi} "
                + $"presentation={presentationGestures?.CurrentMode}");
            if (lastPointerBlockedByUi
                || !lastPointerHitProduct
                || presentationOwnsPointer)
                return;

            MagneticSlideTileShippingMechanism mechanism =
                shippingCoordinator.Mechanism;
            deviceDrive.Cancel();
            dragging = true;
            pointerStartPosition = position;
            previousPointerPosition = position;
            pointerStartTime = Time.unscaledTime;
            shippingGestureStartTravelMeters = mechanism.TravelMeters;
            shippingGestureStartAngleDegrees =
                mechanism.UnwrappedAngleDegrees;
            shippingGestureHasRotationSample = TryShippingRotationSample(
                position,
                out shippingGestureRotationAxisWorld,
                out shippingGestureStartRadialWorld);
            shippingGestureLastRadialWorld =
                shippingGestureStartRadialWorld;
            shippingGestureAccumulatedAngleDegrees = 0f;
            shippingGestureLastAngleDegrees =
                mechanism.UnwrappedAngleDegrees;
            shippingGestureLastTime = Time.unscaledTime;
            shippingGestureMode = mechanism.AtMaximumTravel
                ? Mathf.Abs(Mathf.DeltaAngle(
                    mechanism.AngleDegrees, 0f)) <= 0.001f
                    ? ShippingGestureMode.Undecided
                    : ShippingGestureMode.Rotate
                : ShippingGestureMode.Slide;
            ResetGestureTelemetry(true);
            Debug.Log(
                "[MagneticSlideRuntime] toy-gesture-begin "
                + $"mode={shippingGestureMode} "
                + $"travel={mechanism.TravelMeters:F6} "
                + $"angle={mechanism.AngleDegrees:F1}");
        }

        private void MoveShippingPointer(Vector2 position)
        {
            if (shippingGestureMode == ShippingGestureMode.Undecided)
            {
                float slidePixels = SignedShippingSlidePixels(
                    position - pointerStartPosition);
                float rotationDegrees = 0f;
                bool rotationIntentDominates = false;
                if (shippingGestureHasRotationSample
                    && TryShippingRotationSample(
                    position,
                    out Vector3 currentAxis,
                    out Vector3 currentRadial))
                {
                    rotationDegrees = Mathf.Abs(Vector3.SignedAngle(
                        shippingGestureStartRadialWorld,
                        currentRadial,
                        currentAxis));
                    float tangentialTravel = rotationDegrees
                        * Mathf.Deg2Rad
                        * Mathf.Min(
                            shippingGestureStartRadialWorld.magnitude,
                            currentRadial.magnitude);
                    float radialTravel = Mathf.Abs(
                        currentRadial.magnitude
                        - shippingGestureStartRadialWorld.magnitude);
                    rotationIntentDominates = rotationDegrees >= 2f
                        && tangentialTravel
                            > Mathf.Max(0.0001f, radialTravel * 1.25f);
                }
                if (rotationIntentDominates)
                {
                    shippingGestureMode = ShippingGestureMode.Rotate;
                    Debug.Log(
                        "[MagneticSlideRuntime] toy-gesture-mode=rotate");
                }
                else if (slidePixels <= -8f)
                {
                    shippingGestureMode = ShippingGestureMode.Slide;
                    Debug.Log(
                        "[MagneticSlideRuntime] toy-gesture-mode=slide");
                }
                else
                    return;
            }

            if (shippingGestureMode == ShippingGestureMode.Slide)
            {
                float screenTravel = ShippingScreenTravelPixels();
                float slidePixels = SignedShippingSlidePixels(
                    position - pointerStartPosition);
                float requested = shippingGestureStartTravelMeters
                    + slidePixels / screenTravel
                    * shippingCoordinator.Settings.MaximumTravelMeters;
                float previousTravel =
                    shippingCoordinator.Mechanism.TravelMeters;
                shippingCoordinator.TryApplySlideInput(requested);
                float travelDelta = Mathf.Abs(
                    shippingCoordinator.Mechanism.TravelMeters
                    - previousTravel);
                if (travelDelta > 0.0000001f)
                {
                    SlideInputCount++;
                    float now = Time.unscaledTime;
                    float elapsed = Mathf.Max(
                        0.0001f,
                        now - shippingGestureLastTime);
                    filteredFingerSpeedMetersPerSecond =
                        travelDelta / elapsed;
                    gestureSpeedNormalized = Mathf.Clamp01(
                        filteredFingerSpeedMetersPerSecond / 0.12f);
                    accumulatedActivityDegrees += travelDelta
                        / shippingCoordinator.Settings.MaximumTravelMeters
                        * 360f;
                    activitySpeedRadians = travelDelta
                        / shippingCoordinator.Settings.MaximumTravelMeters
                        * Mathf.PI * 2f
                        / elapsed;
                    shippingGestureLastTime = now;
                }
            }
            else if (shippingGestureMode == ShippingGestureMode.Rotate)
            {
                if (!TryShippingRotationSample(
                    position,
                    out Vector3 currentAxis,
                    out Vector3 currentRadial))
                {
                    return;
                }
                if (!shippingGestureHasRotationSample)
                {
                    shippingGestureRotationAxisWorld = currentAxis;
                    shippingGestureStartRadialWorld = currentRadial;
                    shippingGestureLastRadialWorld = currentRadial;
                    shippingGestureHasRotationSample = true;
                    return;
                }
                shippingGestureAccumulatedAngleDegrees += Vector3.SignedAngle(
                    shippingGestureLastRadialWorld,
                    currentRadial,
                    shippingGestureRotationAxisWorld);
                shippingGestureLastRadialWorld = currentRadial;
                float requested = shippingGestureStartAngleDegrees
                    + shippingGestureAccumulatedAngleDegrees;
                shippingCoordinator.TryApplyRotationInput(requested);
                float now = Time.unscaledTime;
                float elapsed = Mathf.Max(0.0001f, now - shippingGestureLastTime);
                float angleDelta = Mathf.Abs(
                    shippingCoordinator.Mechanism.UnwrappedAngleDegrees
                    - shippingGestureLastAngleDegrees);
                activitySpeedRadians = angleDelta * Mathf.Deg2Rad / elapsed;
                accumulatedActivityDegrees += angleDelta;
                shippingGestureLastAngleDegrees =
                    shippingCoordinator.Mechanism.UnwrappedAngleDegrees;
                shippingGestureLastTime = now;
                if (angleDelta > 0.001f)
                    RotationInputCount++;
            }
        }

        private void EndShippingPointer(Vector2 position)
        {
            if (!dragging)
                return;
            if (shippingGestureMode == ShippingGestureMode.Rotate)
            {
                shippingCoordinator.TryCaptureRotationInput(
                    shippingCoordinator.Mechanism.UnwrappedAngleDegrees);
            }
            dragging = false;
            shippingGestureMode = ShippingGestureMode.None;
            float travelPixels = Vector2.Distance(pointerStartPosition, position);
            gestureIntensityNormalized = Mathf.Clamp01(
                travelPixels / Mathf.Max(1f, Screen.width * 0.34f));
            InteractionGestureCompleted?.Invoke(
                Mathf.Max(0.18f, gestureIntensityNormalized));
            UpdateCompletedGestureFrequency(Time.unscaledTime);
        }

        private float SignedShippingSlidePixels(Vector2 screenDelta)
        {
            Vector2 screenDirection = ShippingScreenDirection();
            return Vector2.Dot(screenDelta, screenDirection);
        }

        private float ShippingScreenTravelPixels()
        {
            MagneticSlideTileShippingMechanism mechanism =
                shippingCoordinator.Mechanism;
            Camera camera = interactionCamera != null
                ? interactionCamera
                : Camera.main;
            if (camera == null || mechanism.TopLocalSlide == null)
                return Mathf.Max(1f, Screen.height * 0.28f);
            Transform slide = mechanism.TopLocalSlide;
            Vector3 origin = slide.position;
            Vector3 offset = slide.parent != null
                ? slide.parent.TransformVector(
                    Vector3.down
                    * shippingCoordinator.Settings.MaximumTravelMeters)
                : Vector3.down
                    * shippingCoordinator.Settings.MaximumTravelMeters;
            Vector2 start = camera.WorldToScreenPoint(origin);
            Vector2 end = camera.WorldToScreenPoint(origin + offset);
            return Mathf.Max(1f, Vector2.Distance(start, end));
        }

        private Vector2 ShippingScreenDirection()
        {
            MagneticSlideTileShippingMechanism mechanism =
                shippingCoordinator.Mechanism;
            Camera camera = interactionCamera != null
                ? interactionCamera
                : Camera.main;
            if (camera == null || mechanism.TopLocalSlide == null)
                return Vector2.down;
            Transform slide = mechanism.TopLocalSlide;
            Vector3 origin = slide.position;
            Vector3 offset = slide.parent != null
                ? slide.parent.TransformVector(Vector3.down)
                : Vector3.down;
            Vector2 start = camera.WorldToScreenPoint(origin);
            Vector2 end = camera.WorldToScreenPoint(origin + offset);
            Vector2 direction = end - start;
            return direction.sqrMagnitude >= 0.0001f
                ? direction.normalized
                : Vector2.down;
        }

        private bool TryShippingRotationSample(
            Vector2 position,
            out Vector3 orientedAxisWorld,
            out Vector3 radialWorld)
        {
            Camera camera = interactionCamera != null
                ? interactionCamera
                : Camera.main;
            MagneticSlideTileShippingMechanism mechanism =
                shippingCoordinator?.Mechanism;
            orientedAxisWorld = mechanism?.RotatingCarrier != null
                ? mechanism.RotatingCarrier.TransformDirection(Vector3.forward)
                    .normalized
                : Vector3.forward;
            radialWorld = Vector3.zero;
            if (camera == null || mechanism?.FixedAxis == null)
                return false;

            Vector3 pivotWorld = mechanism.FixedAxis.position;
            Plane interactionPlane =
                new(orientedAxisWorld, pivotWorld);
            Ray ray = camera.ScreenPointToRay(position);
            if (!interactionPlane.Raycast(ray, out float distance))
                return false;
            radialWorld = Vector3.ProjectOnPlane(
                ray.GetPoint(distance) - pivotWorld,
                orientedAxisWorld);
            return radialWorld.sqrMagnitude >= 0.00000001f;
        }

        private void SubscribeShippingMechanism()
        {
            MagneticSlideTileShippingMechanism mechanism =
                shippingCoordinator?.Mechanism;
            if (mechanism == null
                || subscribedShippingMechanism == mechanism)
            {
                return;
            }
            UnsubscribeShippingMechanism();
            subscribedShippingMechanism = mechanism;
            subscribedShippingMechanism.SemanticEventRaised +=
                HandleShippingSemanticEvent;
        }

        private void UnsubscribeShippingMechanism()
        {
            if (subscribedShippingMechanism == null)
                return;
            subscribedShippingMechanism.SemanticEventRaised -=
                HandleShippingSemanticEvent;
            subscribedShippingMechanism = null;
        }

        private void HandleShippingSemanticEvent(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal)
        {
            if (semanticEvent == FidgetSemanticEvent.DetentCrossed
                && subscribedShippingMechanism != null)
            {
                LastSemanticDetentDirection =
                    subscribedShippingMechanism.LastDetentCrossingDirection;
                LastSemanticDetentIndex =
                    subscribedShippingMechanism
                        .LastDetentCrossingUnwrappedIndex;
            }
            SemanticEventCount++;
            SemanticEventRaised?.Invoke(
                semanticEvent,
                normalizedSignal);
        }

        private bool TryReadTouch(out Vector2 position, out bool pressed)
        {
            Touchscreen touchscreen = Touchscreen.current;
            if (touchscreen != null)
            {
                TouchControl firstPressedTouch = null;
                int pressedTouchCount = 0;
                foreach (TouchControl touch in touchscreen.touches)
                {
                    if (!touch.press.isPressed)
                    {
                        continue;
                    }

                    pressedTouchCount++;
                    firstPressedTouch ??= touch;
                    if (pressedTouchCount >= 2)
                    {
                        // Two fingers are reserved for the shared pinch
                        // presentation gesture and must never load the rail.
                        dragging = false;
                        pointerWasPressed = false;
                        interactionHapticsAuthorized = false;
                        ResetEdgeProbeState();
                        ResetFingerIntent();
                        ResetGestureTelemetry(false);
                        magneticTrack?.Release();
                        position = firstPressedTouch.position.ReadValue();
                        pressed = false;
                        return true;
                    }
                }

                if (firstPressedTouch != null)
                {
                    position = firstPressedTouch.position.ReadValue();
                    pressed = true;
                    return true;
                }
            }

            if (pointerWasPressed && Mouse.current == null)
            {
                position = previousPointerPosition;
                pressed = false;
                return true;
            }

            position = default;
            pressed = false;
            return false;
        }

        private enum ShippingGestureMode
        {
            None,
            Undecided,
            Slide,
            Rotate,
        }

        private void ReadMouse()
        {
            Mouse mouse = Mouse.current;
            if (mouse == null)
            {
                return;
            }
            UpdatePointer(mouse.position.ReadValue(), mouse.leftButton.isPressed);
        }

        private void UpdatePointer(Vector2 position, bool pressed)
        {
            if (pressed && !pointerWasPressed)
            {
                BeginPointer(position);
            }
            else if (pressed && pointerWasPressed && dragging)
            {
                float screenTravel = ResolveScreenTravelPixels();
                float signedPixels = position.x - previousPointerPosition.x;
                cumulativeGestureTravelPixels += Mathf.Abs(signedPixels);
                float deltaMeters = signedPixels
                    / screenTravel
                    * travelDistance;
                handTargetMeters = Mathf.Clamp(
                    handTargetMeters + deltaMeters,
                    0f,
                    travelDistance);
            }
            else if (!pressed && pointerWasPressed)
            {
                EndPointer(position);
            }

            previousPointerPosition = position;
            pointerWasPressed = pressed;
        }

        private void BeginPointer(Vector2 position)
        {
            if (EventSystem.current != null && EventSystem.current.IsPointerOverGameObject())
            {
                return;
            }
            if (!ContainsScreenPoint(position))
            {
                return;
            }

            EnsureTrack();
            dragging = true;
            poweredDriveActive = false;
            assistantDriveActive = false;
            interactionHapticsAuthorized = true;
            handTargetMeters = magneticTrack.PositionMeters;
            ResetEdgeProbeState();
            ResetFingerIntent();
            ResetGestureTelemetry(true);
            previousHandTargetMeters = handTargetMeters;
            pointerStartPosition = position;
            previousPointerPosition = position;
            pointerStartTime = Time.unscaledTime;
        }

        private void EndPointer(Vector2 position)
        {
            if (!dragging)
            {
                return;
            }

            dragging = false;
            ResetEdgeProbeState();
            float travelPixels = Vector2.Distance(pointerStartPosition, position);
            float duration = Time.unscaledTime - pointerStartTime;
            if (travelPixels <= 6f && duration <= 0.35f)
            {
                float target = slideProgress >= 0.5f ? 0f : travelDistance;
                BeginPoweredTravel(target, true);
                InteractionGestureCompleted?.Invoke(Mathf.Max(
                    0.28f,
                    gestureIntensityNormalized));
                UpdateCompletedGestureFrequency(Time.unscaledTime);
                ResetFingerIntent();
                return;
            }

            magneticTrack.Release();
            float normalizedForce = Mathf.Clamp01(
                travelPixels / Mathf.Max(1f, Screen.width * 0.34f));
            InteractionGestureCompleted?.Invoke(Mathf.Max(
                0.18f,
                Mathf.Max(normalizedForce, gestureIntensityNormalized)));
            UpdateCompletedGestureFrequency(Time.unscaledTime);
            ResetFingerIntent();
        }

        private float ResolveScreenTravelPixels()
        {
            Camera camera = interactionCamera != null ? interactionCamera : Camera.main;
            if (camera == null || sliderGroup == null)
            {
                return Screen.width * EdcSliderMotion.ScreenTravelFallbackFactor;
            }

            Transform parent = sliderGroup.parent;
            Vector3 closedWorld = parent != null
                ? parent.TransformPoint(closedLocalPosition)
                : closedLocalPosition;
            Vector3 openLocal = closedLocalPosition + Vector3.right * travelDistance;
            Vector3 openWorld = parent != null ? parent.TransformPoint(openLocal) : openLocal;
            Vector3 closedScreen = camera.WorldToScreenPoint(closedWorld);
            Vector3 openScreen = camera.WorldToScreenPoint(openWorld);
            float signedTravel = openScreen.x - closedScreen.x;
            if (Mathf.Abs(signedTravel) < 1f)
            {
                return signedTravel < 0f ? -1f : 1f;
            }
            return signedTravel;
        }

        private void BeginPoweredTravel(float targetMeters, bool hapticAuthorized)
        {
            EnsureTrack();
            dragging = false;
            assistantDriveActive = false;
            poweredDriveActive = true;
            poweredTargetMeters = Mathf.Clamp(targetMeters, 0f, travelDistance);
            handTargetMeters = poweredTargetMeters;
            interactionHapticsAuthorized = hapticAuthorized;
        }

        private void AdvanceAssistantTarget(float deltaTime)
        {
            handTargetMeters = Mathf.Clamp(
                handTargetMeters
                    + assistantDirection
                        * assistantTargetSpeedMetersPerSecond
                        * deltaTime,
                0f,
                travelDistance);
            if (magneticTrack.IsAtRest)
            {
                if (magneticTrack.CapturedDetentIndex == magneticProfile.DetentCount - 1)
                {
                    assistantDirection = -1f;
                }
                else if (magneticTrack.CapturedDetentIndex == 0)
                {
                    assistantDirection = 1f;
                }
            }
        }

        private void UpdateFingerIntent(float deltaTime)
        {
            if (!dragging || deltaTime <= 0f)
            {
                ResetFingerIntent();
                previousHandTargetMeters = handTargetMeters;
                return;
            }

            float rawSpeed = Mathf.Abs(
                (handTargetMeters - previousHandTargetMeters) / deltaTime);
            previousHandTargetMeters = handTargetMeters;
            float blend = 1f - Mathf.Exp(
                -Mathf.Log(2f)
                * deltaTime
                / magneticProfile.FingerVelocityHalfLifeSeconds);
            filteredFingerSpeedMetersPerSecond = Mathf.Lerp(
                filteredFingerSpeedMetersPerSecond,
                rawSpeed,
                blend);
            gestureSpeedNormalized = Mathf.Clamp01(
                filteredFingerSpeedMetersPerSecond / 0.12f);
            gestureDistanceNormalized = Mathf.InverseLerp(
                0.018f,
                0.28f,
                cumulativeGestureTravelPixels / Mathf.Max(1f, Screen.width));
            gestureIntensityNormalized = Mathf.Clamp01(
                gestureSpeedNormalized * 0.48f
                + gestureDistanceNormalized * 0.34f
                + (magneticTrack?.LoadNormalized ?? 0f) * 0.18f);

            if (!slowIntentActive)
            {
                slowIntentExitElapsed = 0f;
                slowIntentEnterElapsed = filteredFingerSpeedMetersPerSecond
                        <= magneticProfile.SlowIntentEnterSpeedMetersPerSecond
                    ? slowIntentEnterElapsed + deltaTime
                    : 0f;
                if (slowIntentEnterElapsed
                    >= magneticProfile.SlowIntentEnterDurationSeconds)
                {
                    slowIntentActive = true;
                    slowIntentEnterElapsed = 0f;
                }
            }
            else
            {
                slowIntentEnterElapsed = 0f;
                slowIntentExitElapsed = filteredFingerSpeedMetersPerSecond
                        > magneticProfile.SlowIntentExitSpeedMetersPerSecond
                    ? slowIntentExitElapsed + deltaTime
                    : 0f;
                if (slowIntentExitElapsed >= magneticProfile.SlowIntentExitDurationSeconds)
                {
                    slowIntentActive = false;
                    slowIntentExitElapsed = 0f;
                }
            }

            stationaryElapsed = filteredFingerSpeedMetersPerSecond
                    <= magneticProfile.StationarySpeedMetersPerSecond
                ? stationaryElapsed + deltaTime
                : 0f;
            fingerStationary = stationaryElapsed
                >= magneticProfile.StationaryDurationSeconds;
        }

        private void ResetFingerIntent()
        {
            filteredFingerSpeedMetersPerSecond = 0f;
            slowIntentEnterElapsed = 0f;
            slowIntentExitElapsed = 0f;
            stationaryElapsed = 0f;
            slowIntentActive = false;
            fingerStationary = false;
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
                        Mathf.InverseLerp(0.25f, 2.20f, 1f / interval));
                }
            }
            lastGestureCompletionTime = completionTime;
        }

        private void ResetGestureTelemetry(bool preserveFrequency)
        {
            cumulativeGestureTravelPixels = 0f;
            gestureSpeedNormalized = 0f;
            gestureDistanceNormalized = 0f;
            gestureIntensityNormalized = 0f;
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
            gestureDistanceNormalized = Mathf.Lerp(
                gestureDistanceNormalized,
                0f,
                fastDecay);
            gestureIntensityNormalized = Mathf.Lerp(
                gestureIntensityNormalized,
                0f,
                fastDecay);
            float cadenceDecay = 1f - Mathf.Pow(0.5f, deltaTime / 1.10f);
            gestureFrequencyNormalized = Mathf.Lerp(
                gestureFrequencyNormalized,
                0f,
                cadenceDecay);
        }

        private void AdvancePhysics(
            float deltaTime,
            float targetMeters,
            bool handActive,
            bool hapticAuthorized,
            bool manualSlowIntent)
        {
            EnsureTrack();
            int loadingDirection = Math.Sign(targetMeters - magneticTrack.PositionMeters);
            MagneticDetentStepResult result = magneticTrack.Step(
                deltaTime,
                targetMeters,
                handActive,
                manualSlowIntent);
            float currentPosition = magneticTrack.PositionMeters;
            float delta = currentPosition - previousPhysicalPosition;
            if (Mathf.Abs(delta) > 0.000001f)
            {
                lastTravelDirection = Math.Sign(delta);
            }
            previousPhysicalPosition = currentPosition;
            slideProgress = Mathf.Clamp01(currentPosition / travelDistance);

            bool loading = handActive
                && (magneticTrack.State == MagneticDetentState.Loading
                    || result.BrokeAway);
            float spatialLoad = result.BrokeAway
                ? 1f
                : magneticTrack.LoadNormalized;
            UpdateEdgeProbeMilestones(
                spatialLoad,
                loadingDirection,
                loading && manualSlowIntent,
                hapticAuthorized);

            if (result.BrokeAway)
            {
                EmitSemanticIfAuthorized(
                    FidgetSemanticEvent.Breakaway,
                    1f,
                    hapticAuthorized);
            }
            for (int crossing = 0; crossing < result.CrossedDetentCount; crossing++)
            {
                BeginCrossingTremor(result.CrossingDirection);
                float normalizedSpeed = Mathf.Clamp01(
                    Mathf.Abs(magneticTrack.VelocityMetersPerSecond) / 0.24f);
                EmitSemanticIfAuthorized(
                    FidgetSemanticEvent.DetentCrossed,
                    normalizedSpeed,
                    hapticAuthorized);
            }
            if (result.Captured)
            {
                ResetEdgeProbeState();
                EmitSemanticIfAuthorized(
                    FidgetSemanticEvent.DetentCaptured,
                    1f,
                    hapticAuthorized);
                if (poweredDriveActive
                    && Mathf.Abs(magneticTrack.PositionMeters - poweredTargetMeters)
                        <= magneticProfile.LockPositionErrorMeters)
                {
                    poweredDriveActive = false;
                    interactionHapticsAuthorized = false;
                }
                else if (!dragging && !poweredDriveActive && !assistantDriveActive)
                {
                    interactionHapticsAuthorized = false;
                }
            }
            ApplyVisualPosition();
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

        private void UpdateEdgeProbeMilestones(
            float normalizedLoad,
            int direction,
            bool active,
            bool authorized)
        {
            MagneticEdgeProbeResult result = edgeProbeSequence.Step(
                normalizedLoad,
                direction,
                active && authorized,
                magneticProfile);
            if (!result.ShouldEmit)
            {
                return;
            }
            SemanticEventRaised?.Invoke(
                FidgetSemanticEvent.MagneticEdgeProbe,
                result.NormalizedSignal);
        }

        private void ResetEdgeProbeState()
        {
            edgeProbeSequence.Reset();
        }

        private void BeginCrossingTremor(int direction)
        {
            crossingTremorDirection = direction != 0 ? direction : lastTravelDirection;
            if (crossingTremorDirection == 0)
            {
                crossingTremorDirection = 1;
            }
            crossingTremorElapsed = 0f;
            crossingTremorActive = true;
        }

        private void AdvanceCrossingTremor(float deltaTime)
        {
            if (!crossingTremorActive)
            {
                return;
            }

            crossingTremorElapsed += deltaTime;
            if (crossingTremorElapsed >= magneticProfile.CrossingMaximumDurationSeconds)
            {
                ResetCrossingTremor();
                ApplyVisualPosition();
                return;
            }
            ApplyVisualPosition();
        }

        private void ResetCrossingTremor()
        {
            crossingTremorDirection = 0;
            crossingTremorElapsed = 0f;
            crossingTremorActive = false;
        }

        private void ResolveCrossingTremor(
            out float railOffsetMeters,
            out float heightMeters,
            out float angleDegrees)
        {
            if (!crossingTremorActive)
            {
                railOffsetMeters = 0f;
                heightMeters = 0f;
                angleDegrees = 0f;
                return;
            }

            float envelope = Mathf.Pow(
                0.5f,
                crossingTremorElapsed / magneticProfile.CrossingHalfLifeSeconds);
            float wave = Mathf.Sin(
                2f
                * Mathf.PI
                * magneticProfile.CrossingFrequencyHertz
                * crossingTremorElapsed);
            railOffsetMeters = crossingTremorDirection
                * magneticProfile.CrossingRailAmplitudeMeters
                * envelope
                * wave;
            heightMeters = magneticProfile.CrossingHeightAmplitudeMeters
                * envelope
                * Mathf.Abs(wave);
            angleDegrees = -crossingTremorDirection
                * magneticProfile.CrossingAngleAmplitudeDegrees
                * envelope
                * wave;
        }

        private void ApplyVisualPosition()
        {
            if (sliderGroup == null || magneticTrack == null)
            {
                return;
            }

            ResolveCrossingTremor(
                out float railOffsetMeters,
                out float heightMeters,
                out float angleDegrees);
            float visualMeters = Mathf.Clamp(
                magneticTrack.PositionMeters
                    + magneticTrack.VisiblePreloadMeters
                    + railOffsetMeters,
                -magneticProfile.CrossingRailAmplitudeMeters,
                travelDistance + magneticProfile.CrossingRailAmplitudeMeters);
            sliderGroup.localPosition = closedLocalPosition
                + Vector3.right * (visualMeters - magneticProfile.DefaultPositionMeters);
            sliderGroup.localRotation = closedLocalRotation;
            for (int index = 0; index < recoilVisuals.Length; index++)
            {
                Transform visual = recoilVisuals[index];
                if (visual == null)
                {
                    continue;
                }
                visual.localPosition = recoilClosedPositions[index]
                    + Vector3.up * heightMeters;
                visual.localRotation = recoilClosedRotations[index]
                    * Quaternion.Euler(0f, 0f, angleDegrees);
            }
        }

        private void CacheRecoilVisuals()
        {
            if (sliderGroup == null)
            {
                recoilVisuals = Array.Empty<Transform>();
                recoilClosedPositions = Array.Empty<Vector3>();
                recoilClosedRotations = Array.Empty<Quaternion>();
                return;
            }

            var visuals = new List<Transform>(2);
            for (int index = 0; index < sliderGroup.childCount; index++)
            {
                Transform child = sliderGroup.GetChild(index);
                if (child == interactionSurface?.transform)
                {
                    continue;
                }
                if (child.GetComponentInChildren<Renderer>(true) != null)
                {
                    visuals.Add(child);
                }
            }

            recoilVisuals = visuals.ToArray();
            recoilClosedPositions = new Vector3[recoilVisuals.Length];
            recoilClosedRotations = new Quaternion[recoilVisuals.Length];
            for (int index = 0; index < recoilVisuals.Length; index++)
            {
                recoilClosedPositions[index] = recoilVisuals[index].localPosition;
                recoilClosedRotations[index] = recoilVisuals[index].localRotation;
            }
        }

        private void UpdateActivity(float deltaTime)
        {
            float safeDeltaTime = Mathf.Max(0.0001f, deltaTime);
            float progressDelta = slideProgress - previousActivityProgress;
            previousActivityProgress = slideProgress;
            if (Mathf.Abs(progressDelta) > 0.00001f)
            {
                accumulatedActivityDegrees += progressDelta * 360f;
                float rawSpeed = progressDelta * Mathf.PI * 2f / safeDeltaTime;
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
