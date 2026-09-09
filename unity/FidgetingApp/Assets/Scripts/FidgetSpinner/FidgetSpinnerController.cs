using System;
using System.Globalization;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;
using UnityEngine.InputSystem.EnhancedTouch;
using EnhancedTouch = UnityEngine.InputSystem.EnhancedTouch.Touch;

namespace CodexUnityLab
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Rigidbody))]
    public sealed class FidgetSpinnerController : MonoBehaviour
    {
        [Header("Spin")]
        [SerializeField, Min(1f)] private float screenSpeedForFullSpin =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultScreenSpeedForFullSpin;
        [SerializeField, Min(0f)] private float fallbackDegreesPerPixel = 0.55f;
        [SerializeField, Range(0.05f, 1f)] private float gestureSpeedScale =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultTouchResponse;
        [SerializeField, Min(0f)] private float dragFollowResponse =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultDragFollowResponse;
        [SerializeField, Min(0f)] private float dragBrakeResponse =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultDragBrakeResponse;
        [SerializeField, Min(0.05f)] private float coastHalfLife =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultCoastHalfLife;
        [SerializeField, Min(1f)] private float maximumAngularSpeed =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed;
        [SerializeField, Min(1)] private int targetFrameRate = 60;

        [Header("Gestures")]
        [SerializeField, Min(0f)] private float tapMaximumDuration = 0.28f;
        [SerializeField, Min(0f)] private float dragActivationDistancePoints = 2.5f;
        [SerializeField, Min(0f)] private float pinchActivationDistancePoints = 6f;
        [SerializeField, Range(0.2f, 0.5f)] private float fallbackTouchRadius =
            global::ThreeBladeEDC.FidgetSpinnerMotion
                .DefaultFallbackTouchRadiusFraction;

        private Rigidbody spinnerBody;
        private PortraitCameraFramer cameraFramer;

        private bool mouseGestureActive;
        private Vector2 mouseStartPosition;
        private float mouseStartTime;
        private bool mouseDragged;

        private int primaryTouchIndex = -1;
        private Vector2 touchStartPosition;
        private float touchStartTime;
        private bool touchDragged;

        private bool pinchActive;
        private bool suppressTouchesUntilClear;
        private int pinchFirstIndex = -1;
        private int pinchSecondIndex = -1;
        private bool pinchRecognized;
        private float pinchStartDistance;
        private float previousPinchDistance;
        private bool enhancedTouchEnabledByController;

        private float filteredHorizontalVelocity;
        private float gestureSignedTravelPixels;
        private float gestureTotalTravelPixels;
        private bool detentHapticsEnabled;
        private int detentsPerTurn =
            DetentFeelPresetCatalog.Default.Config.DetentsPerRevolution;
        private float accumulatedRotationDegrees;
        private int lastDetentIndex;
        private bool hasDetentIndex;
        private bool assistantDriveActive;
        private float assistantTargetSpeed;
        private bool hasDeviceFrameSample;
        private float deviceFrameRate;
        private float deviceFrameRateApplied;

        public event Action<float> SpinGestureCompleted;

        public bool IsPinching => pinchActive;
        public bool IsFingerControlling => mouseGestureActive || primaryTouchIndex >= 0;
        public float AccumulatedRotationDegrees => accumulatedRotationDegrees;
        public float AngularSpeedRadians => spinnerBody != null
            ? Vector3.Dot(spinnerBody.angularVelocity, Vector3.up)
            : 0f;
        public bool IsAssistantDriving => assistantDriveActive;
        /// <summary>World spin axis of the classic rotor (Rigidbody constraint axis).</summary>
        public Vector3 SpinAxisWorld => Vector3.up;
        public float DeviceFrameRate => hasDeviceFrameSample ? deviceFrameRate : 0f;

        private void Awake()
        {
            spinnerBody = GetComponent<Rigidbody>();
            spinnerBody.angularDamping = 0f;
            spinnerBody.maxAngularVelocity = maximumAngularSpeed;
            cameraFramer = Camera.main != null ? Camera.main.GetComponent<PortraitCameraFramer>() : null;

            Application.targetFrameRate = targetFrameRate;
            Screen.sleepTimeout = SleepTimeout.SystemSetting;
        }

        private void Start()
        {
            // Product models never self-start; only touch input can add speed.
            spinnerBody.angularVelocity = Vector3.zero;
            ResetDetentTracking();
        }

        private void OnEnable()
        {
            if (!EnhancedTouchSupport.enabled)
            {
                EnhancedTouchSupport.Enable();
                enhancedTouchEnabledByController = true;
            }
        }

        private void OnDisable()
        {
            assistantDriveActive = false;
            ClearDeviceFrameRotation();
            ResetTouchState();

            if (enhancedTouchEnabledByController && EnhancedTouchSupport.enabled)
            {
                EnhancedTouchSupport.Disable();
                enhancedTouchEnabledByController = false;
            }
        }

        private void Update()
        {
            Keyboard keyboard = Keyboard.current;
            if (keyboard != null && keyboard.spaceKey.wasPressedThisFrame)
            {
                StopFromTap();
            }

            if (UpdateTouchInput())
            {
                CancelMouseGesture();
                return;
            }

            UpdateMouseInput();
        }

        private bool UpdateTouchInput()
        {
            Touchscreen touchscreen = Touchscreen.current;
            if (touchscreen == null)
            {
                ResetTouchState();
                return false;
            }

            if (TryGetFirstTwoEnhancedTouches(
                    out EnhancedTouch firstEnhancedTouch,
                    out EnhancedTouch secondEnhancedTouch,
                    out bool anyEnhancedTouchActivity))
            {
                UpdatePinch(
                    firstEnhancedTouch.screenPosition,
                    firstEnhancedTouch.touchId,
                    secondEnhancedTouch.screenPosition,
                    secondEnhancedTouch.touchId);
                return true;
            }

            FindFirstTwoPressedTouches(touchscreen, out int firstPressed, out int secondPressed, out bool anyTouchActivity);

            if (suppressTouchesUntilClear)
            {
                if (firstPressed < 0 && !anyTouchActivity && !anyEnhancedTouchActivity)
                {
                    suppressTouchesUntilClear = false;
                }

                return true;
            }

            if (secondPressed >= 0)
            {
                UpdatePinch(touchscreen, firstPressed, secondPressed);
                return true;
            }

            if (pinchActive)
            {
                EndPinch();
                suppressTouchesUntilClear = firstPressed >= 0 || anyTouchActivity;
                return true;
            }

            TouchControl primaryTouch = GetTouch(touchscreen, primaryTouchIndex);
            if (primaryTouch == null && primaryTouchIndex < 0)
            {
                for (int index = 0; index < touchscreen.touches.Count; index++)
                {
                    TouchControl candidate = touchscreen.touches[index];
                    if (!candidate.press.wasPressedThisFrame)
                    {
                        continue;
                    }

                    Vector2 position = candidate.position.ReadValue();
                    if (!ContainsScreenPoint(position))
                    {
                        continue;
                    }

                    BeginTouchGesture(index, position);
                    primaryTouch = candidate;
                    break;
                }
            }

            if (primaryTouch != null)
            {
                Vector2 position = primaryTouch.position.ReadValue();
                if (primaryTouch.press.isPressed)
                {
                    Vector2 totalMovement = position - touchStartPosition;
                    if (!touchDragged && totalMovement.magnitude >= PointsToPixels(dragActivationDistancePoints))
                    {
                        touchDragged = true;
                    }

                    if (touchDragged)
                    {
                        ApplyScreenDrag(
                            primaryTouch.delta.ReadValue(),
                            position,
                            primaryTouch.pressure.ReadValue());
                    }
                }

                if (primaryTouch.press.wasReleasedThisFrame || !primaryTouch.press.isPressed)
                {
                    float duration = Time.unscaledTime - touchStartTime;
                    if (!touchDragged && duration <= tapMaximumDuration)
                    {
                        StopFromTap();
                    }
                    else if (touchDragged)
                    {
                        CompleteDragRelease(duration);
                    }

                    EndTouchGesture();
                }

                return true;
            }

            if (primaryTouchIndex >= 0)
            {
                EndTouchGesture();
                return true;
            }

            return anyTouchActivity;
        }

        private void UpdatePinch(Touchscreen touchscreen, int firstIndex, int secondIndex)
        {
            TouchControl firstTouch = touchscreen.touches[firstIndex];
            TouchControl secondTouch = touchscreen.touches[secondIndex];
            UpdatePinch(
                firstTouch.position.ReadValue(),
                firstIndex,
                secondTouch.position.ReadValue(),
                secondIndex);
        }

        private void UpdatePinch(
            Vector2 firstPosition,
            int firstId,
            Vector2 secondPosition,
            int secondId)
        {
            float currentDistance = Vector2.Distance(firstPosition, secondPosition);

            if (!pinchActive || pinchFirstIndex != firstId || pinchSecondIndex != secondId)
            {
                pinchActive = true;
                pinchFirstIndex = firstId;
                pinchSecondIndex = secondId;
                pinchRecognized = false;
                pinchStartDistance = currentDistance;
                previousPinchDistance = currentDistance;
                EndTouchGesture();
                return;
            }

            float pinchDelta = currentDistance - previousPinchDistance;
            previousPinchDistance = currentDistance;

            if (!pinchRecognized)
            {
                float totalPinchDelta = currentDistance - pinchStartDistance;
                float activationDistance = PointsToPixels(pinchActivationDistancePoints);
                if (Mathf.Abs(totalPinchDelta) < activationDistance)
                {
                    return;
                }

                pinchRecognized = true;
                pinchDelta = totalPinchDelta - Mathf.Sign(totalPinchDelta) * activationDistance;
            }

            if (cameraFramer == null && Camera.main != null)
            {
                cameraFramer = Camera.main.GetComponent<PortraitCameraFramer>();
            }

            cameraFramer?.ApplyPinchDelta(pinchDelta);
        }

        private void UpdateMouseInput()
        {
            Mouse mouse = Mouse.current;
            if (mouse == null)
            {
                return;
            }

            Vector2 scroll = mouse.scroll.ReadValue();
            if (!Mathf.Approximately(scroll.y, 0f))
            {
                if (cameraFramer == null && Camera.main != null)
                {
                    cameraFramer = Camera.main.GetComponent<PortraitCameraFramer>();
                }

                cameraFramer?.ApplyPinchDelta(scroll.y * 0.08f);
            }

            Vector2 mousePosition = mouse.position.ReadValue();
            if (mouse.leftButton.wasPressedThisFrame && ContainsScreenPoint(mousePosition))
            {
                mouseGestureActive = true;
                mouseStartPosition = mousePosition;
                mouseStartTime = Time.unscaledTime;
                mouseDragged = false;
                ResetDragHaptics();
            }

            if (mouseGestureActive && mouse.leftButton.isPressed)
            {
                if (!mouseDragged
                    && Vector2.Distance(mouseStartPosition, mousePosition) >= PointsToPixels(dragActivationDistancePoints))
                {
                    mouseDragged = true;
                }

                if (mouseDragged)
                {
                    ApplyScreenDrag(mouse.delta.ReadValue(), mousePosition, 1f);
                }
            }

            if (mouseGestureActive && mouse.leftButton.wasReleasedThisFrame)
            {
                float duration = Time.unscaledTime - mouseStartTime;
                if (!mouseDragged && duration <= tapMaximumDuration)
                {
                    StopFromTap();
                }
                else if (mouseDragged)
                {
                    CompleteDragRelease(duration);
                }

                CancelMouseGesture();
            }
        }

        private void FixedUpdate()
        {
            bool fingerControlling = mouseGestureActive || primaryTouchIndex >= 0;
            if (assistantDriveActive && !fingerControlling)
            {
                float speed = Vector3.Dot(spinnerBody.angularVelocity, Vector3.up);
                float followed = Mathf.Lerp(
                    speed,
                    assistantTargetSpeed,
                    1f - Mathf.Exp(-Time.fixedUnscaledDeltaTime * 2.8f));
                spinnerBody.angularVelocity = Vector3.up * followed;
            }
            else if (!fingerControlling)
            {
                float speed = Vector3.Dot(spinnerBody.angularVelocity, Vector3.up);
                // Free rotor: the phone turning about the spin axis leaves the
                // rotor's world angular velocity alone, so its speed relative
                // to the phone changes by minus the phone-rate change. The
                // half-life below then acts as bearing friction.
                if (hasDeviceFrameSample)
                {
                    speed = global::ThreeBladeEDC.FidgetSpinnerMotion
                        .ApplyDeviceFrameCoupling(
                            speed,
                            deviceFrameRate,
                            deviceFrameRateApplied,
                            false,
                            false,
                            0f,
                            maximumAngularSpeed)
                        .AxialSpeed;
                }
                float decayed = global::ThreeBladeEDC.FidgetSpinnerMotion.ApplyCoastHalfLife(
                    speed,
                    Time.fixedUnscaledDeltaTime,
                    coastHalfLife);
                if (Mathf.Abs(decayed) < 0.02f)
                {
                    decayed = 0f;
                }
                spinnerBody.angularVelocity = Vector3.up * decayed;
            }

            // Finger and assistant own the rotor: track the phone so resuming
            // never replays the rate change that happened meanwhile.
            deviceFrameRateApplied = deviceFrameRate;
            TrackDetentCrossing();
        }

        /// <summary>
        /// Latest phone rotation rate about the spin axis (Unity sign, rad/s,
        /// already dead-zoned), published every frame by the motion controller.
        /// </summary>
        public void SetDeviceFrameRotationRate(float rateAboutSpinAxis)
        {
            float clamped = Mathf.Clamp(
                rateAboutSpinAxis,
                -maximumAngularSpeed,
                maximumAngularSpeed);
            if (!hasDeviceFrameSample)
            {
                deviceFrameRateApplied = clamped;
                hasDeviceFrameSample = true;
            }
            deviceFrameRate = clamped;
        }

        /// <summary>
        /// Drops the phone-frame sample so no stored rate can turn into an
        /// impulse after reset, suspension, or a scene change.
        /// </summary>
        public void ClearDeviceFrameRotation()
        {
            hasDeviceFrameSample = false;
            deviceFrameRate = 0f;
            deviceFrameRateApplied = 0f;
        }

        /// <summary>
        /// Device shake impulse. Finger and assistant keep authority. The
        /// rotor raises ShakeBurst itself because its state changed.
        /// </summary>
        public bool ApplyDeviceShakeImpulse(
            float deltaRadiansPerSecond,
            float normalizedStrength)
        {
            if (spinnerBody == null
                || IsFingerControlling
                || assistantDriveActive
                || Mathf.Approximately(deltaRadiansPerSecond, 0f))
            {
                return false;
            }

            float requested = Mathf.Clamp(
                AngularSpeedRadians + deltaRadiansPerSecond,
                -maximumAngularSpeed,
                maximumAngularSpeed);
            spinnerBody.angularVelocity = Vector3.up * requested;
            spinnerBody.WakeUp();
            FidgetHapticRouter.Emit(
                FidgetSemanticEvent.ShakeBurst,
                Mathf.Clamp01(normalizedStrength));
            return true;
        }

        private void StopFromTap()
        {
            // A tap is an explicit brake. It must never be interpreted as a
            // tiny high-speed flick or inject motion into a stationary rotor.
            spinnerBody.angularVelocity = Vector3.zero;
        }

        private void ApplyScreenDrag(
            Vector2 screenDelta,
            Vector2 screenPosition,
            float pressure)
        {
            if (screenDelta.sqrMagnitude <= Mathf.Epsilon)
            {
                return;
            }

            float deltaTime = Mathf.Max(Time.unscaledDeltaTime, 0.001f);
            float signedPixels = CalculateSignedDragPixels(screenDelta, screenPosition);
            float signedPixelVelocity = signedPixels / deltaTime;
            float targetSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion
                .MapGestureToAngularSpeed(
                    signedPixels * fallbackDegreesPerPixel,
                    screenDelta.magnitude,
                    deltaTime,
                    gestureSpeedScale,
                    maximumAngularSpeed,
                    screenSpeedForFullSpin,
                    pressure);
            float currentSpeed = Vector3.Dot(spinnerBody.angularVelocity, Vector3.up);
            float followedSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion
                .FollowDragSpeed(
                    currentSpeed,
                    targetSpeed,
                    deltaTime,
                    dragFollowResponse,
                    dragBrakeResponse,
                    maximumAngularSpeed);
            spinnerBody.angularVelocity = Vector3.up * Mathf.Clamp(
                followedSpeed,
                -maximumAngularSpeed,
                maximumAngularSpeed);

            float velocityBlend = 1f - Mathf.Exp(-18f * deltaTime);
            filteredHorizontalVelocity = Mathf.Lerp(
                filteredHorizontalVelocity,
                signedPixelVelocity,
                velocityBlend);
            gestureSignedTravelPixels += signedPixels;
            gestureTotalTravelPixels += screenDelta.magnitude;
        }

        private void TrackDetentCrossing()
        {
            float angularSpeed = AngularSpeedRadians;
            accumulatedRotationDegrees += angularSpeed
                * Time.fixedUnscaledDeltaTime
                * Mathf.Rad2Deg;
            int currentIndex = global::ThreeBladeEDC.FidgetSpinnerMotion.DetentIndex(
                accumulatedRotationDegrees,
                detentsPerTurn);
            if (!hasDetentIndex)
            {
                lastDetentIndex = currentIndex;
                hasDetentIndex = true;
                return;
            }

            bool crossed = currentIndex != lastDetentIndex;
            lastDetentIndex = currentIndex;
            if (crossed && detentHapticsEnabled)
            {
                FidgetHapticRouter.Emit(
                    FidgetSemanticEvent.DetentCrossed,
                    Mathf.Abs(angularSpeed) / Mathf.Max(1f, maximumAngularSpeed));
            }
        }

        private void ResetDetentTracking()
        {
            lastDetentIndex = global::ThreeBladeEDC.FidgetSpinnerMotion.DetentIndex(
                accumulatedRotationDegrees,
                detentsPerTurn);
            hasDetentIndex = true;
        }

        private Vector2 SpinnerScreenCenter()
        {
            Camera mainCamera = Camera.main;
            if (mainCamera == null || spinnerBody == null)
            {
                return new Vector2(Screen.width * 0.5f, Screen.height * 0.5f);
            }

            Vector3 center = mainCamera.WorldToScreenPoint(spinnerBody.worldCenterOfMass);
            return new Vector2(center.x, center.y);
        }

        private float CalculateSignedDragPixels(Vector2 delta, Vector2 currentPosition)
        {
            Vector2 radial = currentPosition - delta * 0.5f - SpinnerScreenCenter();
            if (radial.sqrMagnitude > 24f * 24f)
            {
                Vector2 tangent = new Vector2(-radial.y, radial.x).normalized;
                float tangential = Vector2.Dot(delta, tangent);
                if (Mathf.Abs(tangential) >= delta.magnitude * 0.25f)
                {
                    Camera mainCamera = Camera.main;
                    return global::ThreeBladeEDC.FidgetSpinnerMotion
                        .AlignScreenTangentToSpinAxis(
                            tangential,
                            mainCamera != null ? mainCamera.transform.forward : Vector3.zero,
                            Vector3.up);
                }
            }

            return Mathf.Abs(delta.x) >= Mathf.Abs(delta.y) ? delta.x : -delta.y;
        }

        private void CompleteDragRelease(float gestureDuration)
        {
            float currentSpeed = Vector3.Dot(
                spinnerBody.angularVelocity,
                Vector3.up);
            bool qualifiedFling = global::ThreeBladeEDC.FidgetSpinnerMotion
                .QualifiesReleaseFling(
                    filteredHorizontalVelocity,
                    gestureSignedTravelPixels,
                    gestureTotalTravelPixels,
                    gestureDuration);
            float releaseSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion
                .ResolveReleaseAngularSpeed(
                    currentSpeed,
                    filteredHorizontalVelocity,
                    gestureSignedTravelPixels,
                    gestureTotalTravelPixels,
                    gestureDuration,
                    gestureSpeedScale,
                    maximumAngularSpeed,
                    screenSpeedForFullSpin);
            spinnerBody.angularVelocity = Vector3.up * releaseSpeed;

            float normalizedForce = Mathf.Clamp01(Mathf.Max(
                Mathf.Abs(releaseSpeed) / Mathf.Max(1f, maximumAngularSpeed),
                gestureTotalTravelPixels / Mathf.Max(1f, Screen.width * 0.6f)));
            SpinGestureCompleted?.Invoke(normalizedForce);

            if (qualifiedFling)
            {
                FidgetHapticRouter.Emit(FidgetSemanticEvent.Released);
            }
        }

        private void BeginTouchGesture(int touchIndex, Vector2 startPosition)
        {
            primaryTouchIndex = touchIndex;
            touchStartPosition = startPosition;
            touchStartTime = Time.unscaledTime;
            touchDragged = false;
            filteredHorizontalVelocity = 0f;
            gestureSignedTravelPixels = 0f;
            gestureTotalTravelPixels = 0f;
            ResetDragHaptics();
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Selection, 0.4f);
        }

        private void EndTouchGesture()
        {
            primaryTouchIndex = -1;
            touchDragged = false;
            filteredHorizontalVelocity = 0f;
            gestureSignedTravelPixels = 0f;
            gestureTotalTravelPixels = 0f;
            ResetDragHaptics();
        }

        private void EndPinch()
        {
            pinchActive = false;
            pinchFirstIndex = -1;
            pinchSecondIndex = -1;
            pinchRecognized = false;
            pinchStartDistance = 0f;
            previousPinchDistance = 0f;
        }

        private static bool TryGetFirstTwoEnhancedTouches(
            out EnhancedTouch firstTouch,
            out EnhancedTouch secondTouch,
            out bool anyTouchActivity)
        {
            firstTouch = default;
            secondTouch = default;
            anyTouchActivity = false;
            int found = 0;
            var activeTouches = EnhancedTouch.activeTouches;

            for (int index = 0; index < activeTouches.Count; index++)
            {
                EnhancedTouch touch = activeTouches[index];
                if (touch.phase == UnityEngine.InputSystem.TouchPhase.Ended
                    || touch.phase == UnityEngine.InputSystem.TouchPhase.Canceled)
                {
                    continue;
                }

                anyTouchActivity = true;
                if (found == 0)
                {
                    firstTouch = touch;
                    found = 1;
                }
                else
                {
                    secondTouch = touch;
                    return true;
                }
            }

            return false;
        }

        private static float PointsToPixels(float points)
        {
            float pixelsPerPoint = Screen.dpi > 0f
                ? Mathf.Clamp(Screen.dpi / 160f, 1f, 4f)
                : 1f;
            return points * pixelsPerPoint;
        }

        private void ResetTouchState()
        {
            EndTouchGesture();
            EndPinch();
            suppressTouchesUntilClear = false;
        }

        private void CancelMouseGesture()
        {
            mouseGestureActive = false;
            mouseDragged = false;
            filteredHorizontalVelocity = 0f;
            gestureSignedTravelPixels = 0f;
            gestureTotalTravelPixels = 0f;
            ResetDragHaptics();
        }

        private void ResetDragHaptics()
        {
            ResetDetentTracking();
        }

        private static TouchControl GetTouch(Touchscreen touchscreen, int index)
        {
            return index >= 0 && index < touchscreen.touches.Count ? touchscreen.touches[index] : null;
        }

        private static void FindFirstTwoPressedTouches(
            Touchscreen touchscreen,
            out int firstPressed,
            out int secondPressed,
            out bool anyTouchActivity)
        {
            firstPressed = -1;
            secondPressed = -1;
            anyTouchActivity = false;

            for (int index = 0; index < touchscreen.touches.Count; index++)
            {
                TouchControl touch = touchscreen.touches[index];
                bool pressed = touch.press.isPressed;
                anyTouchActivity |= pressed || touch.press.wasPressedThisFrame || touch.press.wasReleasedThisFrame;

                if (!pressed)
                {
                    continue;
                }

                if (firstPressed < 0)
                {
                    firstPressed = index;
                }
                else if (secondPressed < 0)
                {
                    secondPressed = index;
                    return;
                }
            }
        }

        /// <summary>
        /// Uses the exact same collider and screen-radius rules as the spinner's
        /// own touch input so other product interactions cannot drift from it.
        /// </summary>
        public bool ContainsScreenPoint(Vector2 screenPosition)
        {
            Camera mainCamera = Camera.main;
            if (mainCamera == null)
            {
                return false;
            }

            Ray ray = mainCamera.ScreenPointToRay(screenPosition);
            if (Physics.Raycast(ray, out RaycastHit hit, 100f))
            {
                Rigidbody hitBody = hit.collider.attachedRigidbody;
                if (hitBody != null && hitBody.transform == transform)
                {
                    return true;
                }
            }

            Vector3 spinnerScreenPosition = mainCamera.WorldToScreenPoint(spinnerBody.worldCenterOfMass);
            if (spinnerScreenPosition.z <= 0f)
            {
                return false;
            }

            return global::ThreeBladeEDC.FidgetSpinnerMotion
                .IsWithinFallbackSpinTouchRegion(
                    screenPosition,
                    new Vector2(spinnerScreenPosition.x, spinnerScreenPosition.y),
                    Screen.width,
                    Screen.height,
                    fallbackTouchRadius);
        }

        public void SetGestureSpeedScale(float value)
        {
            SetTouchResponse(value);
        }

        public void SetTouchResponse(float normalizedResponse)
        {
            global::ThreeBladeEDC.FidgetSpinnerMotion.TouchResponseProfile profile =
                global::ThreeBladeEDC.FidgetSpinnerMotion.ResolveTouchResponse(
                    normalizedResponse);
            gestureSpeedScale = profile.NormalizedResponse;
            maximumAngularSpeed = profile.MaximumAngularSpeed;
            screenSpeedForFullSpin = profile.ScreenSpeedForFullSpin;
            dragFollowResponse = profile.DragFollowResponse;
            dragBrakeResponse = profile.DragBrakeResponse;
            if (spinnerBody != null)
            {
                spinnerBody.maxAngularVelocity = maximumAngularSpeed;
            }
        }

        public void SetCoastHalfLife(float value)
        {
            coastHalfLife = Mathf.Clamp(value, 0.05f, 30f);
        }

        public void SetMaximumAngularSpeed(float value)
        {
            maximumAngularSpeed = Mathf.Clamp(value, 1f, 80f);
            if (spinnerBody != null)
            {
                spinnerBody.maxAngularVelocity = maximumAngularSpeed;
            }
        }

        public void SetDetentHapticsEnabled(bool enabled)
        {
            detentHapticsEnabled = enabled;
            ResetDetentTracking();
        }

        public void SetDetentsPerTurn(int value)
        {
            detentsPerTurn = Mathf.Clamp(value, 1, 120);
            ResetDetentTracking();
        }

        public void SetAssistantDrive(bool active, float radiansPerSecond)
        {
            assistantDriveActive = active;
            assistantTargetSpeed = Mathf.Clamp(
                Mathf.Abs(radiansPerSecond),
                0.35f,
                Mathf.Max(0.35f, maximumAngularSpeed));
            if (!active)
            {
                filteredHorizontalVelocity = 0f;
            }
        }

        public void SetGestureSpeedScaleFromNativeUi(string value)
        {
            if (TryParseFloat(value, out float parsedValue))
            {
                SetGestureSpeedScale(parsedValue);
            }
        }

        private static bool TryParseFloat(string value, out float parsedValue)
        {
            return float.TryParse(
                value,
                NumberStyles.Float,
                CultureInfo.InvariantCulture,
                out parsedValue);
        }

        public void ResetFromNativeUi(string unused)
        {
            assistantDriveActive = false;
            filteredHorizontalVelocity = 0f;
            spinnerBody.angularVelocity = Vector3.zero;
            accumulatedRotationDegrees = 0f;
            ClearDeviceFrameRotation();
            ResetDetentTracking();
            cameraFramer?.ResetInteractiveView();
            FidgetHapticRouter.Emit(FidgetSemanticEvent.Reset);
        }

        public void RecenterMotionFromNativeUi(string unused)
        {
            if (Camera.main != null)
            {
                Camera.main.GetComponent<DeviceMotionController>()?.ResetReference();
            }

            FidgetHapticRouter.Emit(FidgetSemanticEvent.Selection);
        }
    }
}
