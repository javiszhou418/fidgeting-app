using UnityEngine;
using UnityEngine.InputSystem;
using ThreeBladeEDC.Presentation;

namespace ThreeBladeEDC.Interaction
{
    /// <summary>
    /// Mobile-first spinner input. A generous circular screen region accepts
    /// both tangential drags and ordinary swipes, while taps and opposite
    /// swipes brake the rotor instead of snapping or reversing instantly.
    /// </summary>
    [DisallowMultipleComponent]
    [DefaultExecutionOrder(-50)]
    public sealed class RotorFlickInput : MonoBehaviour
    {
        private enum PointerSource
        {
            None,
            Mouse,
            Touch
        }

        [Header("References")]
        [SerializeField] private RotorRigidbodyController rotor;
        [SerializeField] private Camera interactionCamera;

        [Header("Interaction Area")]
        [SerializeField, Range(0.2f, 0.49f)]
        private float interactionRadiusScreenFraction = 0.44f;
        [SerializeField, Min(32f)] private float minimumInteractionRadiusPixels = 120f;
        [SerializeField, Min(0f)] private float minimumCircularRadiusPixels = 24f;

        [Header("Flick")]
        [SerializeField, Range(0f, 1f)] private float sensitivity =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultTouchResponse;
        [SerializeField, Min(0.1f)] private float maxFlickSpeed =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed;
        [SerializeField, Min(0f)] private float minimumAngleDegrees = 0.01f;
        [SerializeField, Min(0f)] private float minimumSwipeDistancePixels = 2f;
        [SerializeField, Min(0f)] private float smoothing =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultDragFollowResponse;
        [SerializeField, Min(0f)] private float brakingResponse =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultDragBrakeResponse;
        [SerializeField, Min(1f)] private float screenSpeedForFullSpin =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultScreenSpeedForFullSpin;
        [SerializeField, Min(0f)] private float fallbackDegreesPerPixel = 0.55f;
        [SerializeField] private bool driveRotorWhileDragging = true;

        [Header("Braking")]
        [SerializeField, Min(0f)] private float tapStopMovementPixels = 18f;
        [SerializeField, Min(0f)] private float reversalSpeedThreshold = 0.6f;
        [SerializeField, Min(0.05f)] private float reversalStopDuration = 0.3f;

        [Header("Keyboard")]
        [SerializeField] private bool enableKeyboardControls = true;

        private PointerSource _pointerSource;
        private Vector2 _previousScreenPosition;
        private Vector2 _currentScreenPosition;
        private Vector3 _previousWorldPoint;
        private double _previousSampleTime;
        private float _filteredFlickSpeed;
        private float _totalPointerTravel;
        private bool _hasWorldPoint;
        private bool _hasFlickSample;
        private bool _gestureLockedByReversal;
        private double _gestureStartTime;
        private float _gestureSignedTravel;
        private float _filteredReleasePixelVelocity;

        public RotorRigidbodyController Rotor => rotor;
        public bool IsPointerActive => _pointerSource != PointerSource.None;
        public float InteractionRadiusPixels => GetInteractionRadiusPixels();

        private void Awake()
        {
            ResolveReferences();
        }

        private void OnValidate()
        {
            sensitivity = Mathf.Clamp01(sensitivity);
            maxFlickSpeed = Mathf.Max(0.1f, maxFlickSpeed);
            interactionRadiusScreenFraction = Mathf.Clamp(
                interactionRadiusScreenFraction,
                0.2f,
                0.49f);
            minimumInteractionRadiusPixels = Mathf.Max(32f, minimumInteractionRadiusPixels);
            minimumCircularRadiusPixels = Mathf.Max(0f, minimumCircularRadiusPixels);
            minimumAngleDegrees = Mathf.Max(0f, minimumAngleDegrees);
            minimumSwipeDistancePixels = Mathf.Max(0f, minimumSwipeDistancePixels);
            smoothing = Mathf.Max(0f, smoothing);
            brakingResponse = Mathf.Max(0f, brakingResponse);
            screenSpeedForFullSpin = Mathf.Max(1f, screenSpeedForFullSpin);
            fallbackDegreesPerPixel = Mathf.Max(0f, fallbackDegreesPerPixel);
            tapStopMovementPixels = Mathf.Max(0f, tapStopMovementPixels);
            reversalSpeedThreshold = Mathf.Max(0f, reversalSpeedThreshold);
            reversalStopDuration = Mathf.Max(0.05f, reversalStopDuration);
        }

        private void Update()
        {
            if (rotor == null)
            {
                ResolveReferences();
                if (rotor == null)
                {
                    return;
                }
            }

            ReadKeyboard();
            ReadPointer();
        }

        private void OnDisable()
        {
            CancelPointer();
            if (rotor != null)
            {
                rotor.SetMotorActive(false);
            }
        }

        public void Configure(
            RotorRigidbodyController rotorController,
            Camera camera = null)
        {
            rotor = rotorController;
            interactionCamera = camera;
            CancelPointer();
        }

        private void ReadKeyboard()
        {
            if (!enableKeyboardControls || Keyboard.current == null)
            {
                return;
            }

            rotor.SetMotorActive(Keyboard.current.spaceKey.isPressed);

            if (Keyboard.current.rKey.wasPressedThisFrame)
            {
                CancelPointer();
                rotor.ResetRotor();
            }
        }

        private void ReadPointer()
        {
            if (_pointerSource == PointerSource.Touch)
            {
                ReadActiveTouch();
                return;
            }

            if (_pointerSource == PointerSource.Mouse)
            {
                ReadActiveMouse();
                return;
            }

            Touchscreen touchscreen = Touchscreen.current;
            if (touchscreen != null
                && touchscreen.primaryTouch.press.wasPressedThisFrame)
            {
                BeginPointer(
                    PointerSource.Touch,
                    touchscreen.primaryTouch.position.ReadValue());
                return;
            }

            Mouse mouse = Mouse.current;
            if (mouse != null && mouse.leftButton.wasPressedThisFrame)
            {
                BeginPointer(PointerSource.Mouse, mouse.position.ReadValue());
            }
        }

        private void ReadActiveTouch()
        {
            Touchscreen touchscreen = Touchscreen.current;
            if (touchscreen == null)
            {
                EndPointer();
                return;
            }

            Vector2 position = touchscreen.primaryTouch.position.ReadValue();
            if (touchscreen.primaryTouch.press.isPressed)
            {
                UpdatePointer(position);
            }

            if (touchscreen.primaryTouch.press.wasReleasedThisFrame)
            {
                EndPointer();
            }
        }

        private void ReadActiveMouse()
        {
            Mouse mouse = Mouse.current;
            if (mouse == null)
            {
                EndPointer();
                return;
            }

            Vector2 position = mouse.position.ReadValue();
            if (mouse.leftButton.isPressed)
            {
                UpdatePointer(position);
            }

            if (mouse.leftButton.wasReleasedThisFrame)
            {
                EndPointer();
            }
        }

        private void BeginPointer(PointerSource source, Vector2 screenPosition)
        {
            ResolveReferences();
            if (rotor == null
                || !IsInsideInteractionArea(screenPosition)
                || SpinnerVariantSwitcher.IsScreenPointOverControls(screenPosition))
            {
                return;
            }

            _pointerSource = source;
            _previousScreenPosition = screenPosition;
            _currentScreenPosition = screenPosition;
            _previousSampleTime = Time.unscaledTimeAsDouble;
            _filteredFlickSpeed = 0f;
            _totalPointerTravel = 0f;
            _hasFlickSample = false;
            _gestureLockedByReversal = false;
            _gestureStartTime = _previousSampleTime;
            _gestureSignedTravel = 0f;
            _filteredReleasePixelVelocity = 0f;
            _hasWorldPoint = TryProjectToRotorPlane(
                screenPosition,
                out _previousWorldPoint);
            if (driveRotorWhileDragging)
            {
                rotor.BeginFingerControl();
            }
        }

        private void UpdatePointer(Vector2 screenPosition)
        {
            double now = Time.unscaledTimeAsDouble;
            float deltaTime = (float)(now - _previousSampleTime);
            if (deltaTime <= 0.0001f)
            {
                return;
            }

            _currentScreenPosition = screenPosition;
            float frameTravel = Vector2.Distance(
                _previousScreenPosition,
                screenPosition);
            _totalPointerTravel += frameTravel;

            if (_gestureLockedByReversal)
            {
                StorePointerSample(screenPosition, now, default, false);
                return;
            }

            Vector3 currentWorldPoint;
            bool hasCurrentWorldPoint = TryProjectToRotorPlane(
                screenPosition,
                out currentWorldPoint);
            bool canUseCircularSample = IsOutsideCircularDeadZone(
                _previousScreenPosition)
                && IsOutsideCircularDeadZone(screenPosition);

            float angleDegrees;
            if (_hasWorldPoint && hasCurrentWorldPoint && canUseCircularSample)
            {
                Vector3 pivot = rotor.PivotWorld;
                Vector3 previousRadius = Vector3.ProjectOnPlane(
                    _previousWorldPoint - pivot,
                    rotor.SpinAxisWorld);
                Vector3 currentRadius = Vector3.ProjectOnPlane(
                    currentWorldPoint - pivot,
                    rotor.SpinAxisWorld);

                angleDegrees = previousRadius.sqrMagnitude > 0.000001f
                    && currentRadius.sqrMagnitude > 0.000001f
                    ? Vector3.SignedAngle(
                        previousRadius,
                        currentRadius,
                        rotor.SpinAxisWorld)
                    : CalculateScreenFallbackAngle(
                        _previousScreenPosition,
                        screenPosition);
            }
            else
            {
                angleDegrees = CalculateScreenFallbackAngle(
                    _previousScreenPosition,
                    screenPosition);
            }

            if (frameTravel >= minimumSwipeDistancePixels
                && Mathf.Abs(angleDegrees) >= minimumAngleDegrees)
            {
                float rawSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion
                    .MapGestureToAngularSpeed(
                        angleDegrees,
                        frameTravel,
                        deltaTime,
                        sensitivity,
                        maxFlickSpeed,
                        screenSpeedForFullSpin);
                float currentSpeed = rotor.AngularSpeedRadians;
                float signedTravel = Mathf.Sign(angleDegrees) * frameTravel;
                _gestureSignedTravel += signedTravel;
                float releaseSampleVelocity = signedTravel / deltaTime;
                float releaseBlend = 1f - Mathf.Exp(-18f * deltaTime);
                _filteredReleasePixelVelocity = Mathf.Lerp(
                    _filteredReleasePixelVelocity,
                    releaseSampleVelocity,
                    releaseBlend);

                bool reversed = Mathf.Abs(currentSpeed) >= reversalSpeedThreshold
                    && Mathf.Abs(rawSpeed) >= reversalSpeedThreshold
                    && Mathf.Sign(rawSpeed) != Mathf.Sign(currentSpeed);
                if (reversed)
                {
                    rotor.SmoothStop(reversalStopDuration);
                    _gestureLockedByReversal = true;
                    StorePointerSample(
                        screenPosition,
                        now,
                        currentWorldPoint,
                        hasCurrentWorldPoint);
                    return;
                }

                float sourceSpeed = _hasFlickSample
                    ? _filteredFlickSpeed
                    : currentSpeed;
                _filteredFlickSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion
                    .FollowDragSpeed(
                        sourceSpeed,
                        rawSpeed,
                        deltaTime,
                        smoothing,
                        brakingResponse,
                        maxFlickSpeed);
                _hasFlickSample = true;

                if (driveRotorWhileDragging)
                {
                    rotor.SetSpinVelocity(_filteredFlickSpeed);
                }
            }

            StorePointerSample(
                screenPosition,
                now,
                currentWorldPoint,
                hasCurrentWorldPoint);
        }

        private void EndPointer()
        {
            bool wasTap = _totalPointerTravel <= tapStopMovementPixels;
            if (!_gestureLockedByReversal && wasTap)
            {
                rotor.EndFingerControl();
                rotor.SmoothStop(reversalStopDuration);
            }
            else if (_hasFlickSample)
            {
                float duration = (float)(Time.unscaledTimeAsDouble - _gestureStartTime);
                float releaseSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion
                    .ResolveReleaseAngularSpeed(
                        _filteredFlickSpeed,
                        _filteredReleasePixelVelocity,
                        _gestureSignedTravel,
                        _totalPointerTravel,
                        duration,
                        sensitivity,
                        maxFlickSpeed,
                        screenSpeedForFullSpin);
                rotor.DriveFromFinger(releaseSpeed);
                rotor.EndFingerControl();
            }
            else
            {
                rotor.EndFingerControl();
            }

            CancelPointer();
        }

        private void CancelPointer()
        {
            if (_pointerSource != PointerSource.None
                && rotor != null
                && rotor.IsFingerControlling)
            {
                rotor.EndFingerControl();
            }
            _pointerSource = PointerSource.None;
            _hasWorldPoint = false;
            _hasFlickSample = false;
            _gestureLockedByReversal = false;
            _filteredFlickSpeed = 0f;
            _totalPointerTravel = 0f;
            _gestureStartTime = 0d;
            _gestureSignedTravel = 0f;
            _filteredReleasePixelVelocity = 0f;
        }

        public void SetTouchResponse(float normalizedResponse)
        {
            global::ThreeBladeEDC.FidgetSpinnerMotion.TouchResponseProfile profile =
                global::ThreeBladeEDC.FidgetSpinnerMotion.ResolveTouchResponse(
                    normalizedResponse);
            sensitivity = profile.NormalizedResponse;
            maxFlickSpeed = profile.MaximumAngularSpeed;
            screenSpeedForFullSpin = profile.ScreenSpeedForFullSpin;
            smoothing = profile.DragFollowResponse;
            brakingResponse = profile.DragBrakeResponse;
            rotor?.SetMaximumAngularSpeed(maxFlickSpeed);
        }

        private void StorePointerSample(
            Vector2 screenPosition,
            double sampleTime,
            Vector3 worldPoint,
            bool hasWorldPoint)
        {
            _previousScreenPosition = screenPosition;
            _previousWorldPoint = worldPoint;
            _hasWorldPoint = hasWorldPoint;
            _previousSampleTime = sampleTime;
        }

        private bool TryProjectToRotorPlane(
            Vector2 screenPosition,
            out Vector3 worldPoint)
        {
            worldPoint = default;
            Camera camera = ResolveCamera();
            if (camera == null || rotor == null)
            {
                return false;
            }

            Plane rotorPlane = new Plane(rotor.SpinAxisWorld, rotor.PivotWorld);
            Ray ray = camera.ScreenPointToRay(screenPosition);
            if (!rotorPlane.Raycast(ray, out float enter) || enter < 0f)
            {
                return false;
            }

            worldPoint = ray.GetPoint(enter);
            return true;
        }

        private bool IsInsideInteractionArea(Vector2 screenPosition)
        {
            return Vector2.Distance(screenPosition, GetInteractionCenter())
                <= GetInteractionRadiusPixels();
        }

        private bool IsOutsideCircularDeadZone(Vector2 screenPosition)
        {
            return Vector2.Distance(screenPosition, GetInteractionCenter())
                >= minimumCircularRadiusPixels;
        }

        private Vector2 GetInteractionCenter()
        {
            Camera camera = ResolveCamera();
            if (camera == null || rotor == null)
            {
                return new Vector2(Screen.width * 0.5f, Screen.height * 0.5f);
            }

            Vector3 pivot = camera.WorldToScreenPoint(rotor.PivotWorld);
            return new Vector2(pivot.x, pivot.y);
        }

        private float GetInteractionRadiusPixels()
        {
            float shortSide = Mathf.Min(Screen.width, Screen.height);
            return Mathf.Max(
                minimumInteractionRadiusPixels,
                shortSide * interactionRadiusScreenFraction);
        }

        private float CalculateScreenFallbackAngle(
            Vector2 previous,
            Vector2 current)
        {
            Vector2 pivot = GetInteractionCenter();
            Vector2 delta = current - previous;
            Vector2 radial = ((previous + current) * 0.5f) - pivot;

            float signedPixels;
            if (radial.sqrMagnitude
                >= minimumCircularRadiusPixels * minimumCircularRadiusPixels)
            {
                Vector2 tangent = new Vector2(-radial.y, radial.x).normalized;
                signedPixels = Vector2.Dot(delta, tangent);
                if (Mathf.Abs(signedPixels) < delta.magnitude * 0.25f)
                {
                    signedPixels = Mathf.Abs(delta.x) >= Mathf.Abs(delta.y)
                        ? delta.x
                        : -delta.y;
                }
            }
            else
            {
                signedPixels = Mathf.Abs(delta.x) >= Mathf.Abs(delta.y)
                    ? delta.x
                    : -delta.y;
            }

            Camera camera = ResolveCamera();
            float axisViewDot = camera == null
                ? 0f
                : Vector3.Dot(camera.transform.forward, rotor.SpinAxisWorld);
            float viewSign = Mathf.Abs(axisViewDot) <= 0.001f
                ? 1f
                : -Mathf.Sign(axisViewDot);
            return signedPixels * fallbackDegreesPerPixel * viewSign;
        }

        private void ResolveReferences()
        {
            if (rotor == null)
            {
                rotor = GetComponent<RotorRigidbodyController>();
            }

            if (rotor == null)
            {
                rotor = GetComponentInParent<RotorRigidbodyController>();
            }

            ResolveCamera();
        }

        private Camera ResolveCamera()
        {
            if (interactionCamera == null)
            {
                interactionCamera = Camera.main;
            }

            return interactionCamera;
        }

    }
}
