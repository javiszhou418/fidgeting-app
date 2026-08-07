using System;
using ThreeBladeEDC.Presentation;
using CodexUnityLab;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;

namespace ThreeBladeEDC.Interaction
{
    public enum MobileGestureMode
    {
        None,
        Spin,
        Orbit,
        Pinch
    }

    /// <summary>
    /// Owns all pointer gestures so rotor flick, camera orbit and pinch zoom
    /// cannot compete for the same touch stream.
    /// </summary>
    [DisallowMultipleComponent]
    [DefaultExecutionOrder(-40)]
    public sealed class MobileGestureController : MonoBehaviour
    {
        [SerializeField] private RotorRigidbodyController rotor;
        [SerializeField] private Camera interactionCamera;
        [SerializeField] private OrbitPresentationCamera orbitCamera;
        [SerializeField, Range(0.05f, 1f)] private float spinSensitivity =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultTouchResponse;
        [SerializeField, Min(0.1f)] private float maxSpinSpeed =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed;
        [SerializeField, Min(0f)] private float spinSmoothing =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultDragFollowResponse;
        [SerializeField, Min(0f)] private float spinBrakeResponse =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultDragBrakeResponse;
        [SerializeField, Min(1f)] private float screenSpeedForFullSpin =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultScreenSpeedForFullSpin;
        [SerializeField, Min(0f)] private float fallbackDegreesPerPixel = 0.55f;
        [SerializeField, Min(0.01f)] private float maxRayDistance = 5f;
        [SerializeField, Range(0.2f, 0.5f)] private float fallbackTouchRadius = 0.48f;
        [SerializeField, Min(0.05f)] private float reversalStopDuration = 0.3f;
        [SerializeField, Min(0f)] private float reversalMinimumSpeed = 1.5f;
        [SerializeField, Min(0f)] private float reversalConfirmationPixels = 18f;
        [SerializeField] private bool flipOnRelease;
        [SerializeField, Min(0.001f)] private float minimumWorldRadius = 0.008f;
        [SerializeField, Range(4f, 45f)] private float maximumSampleAngleDegrees = 24f;
        [SerializeField, Min(0f)] private float minimumScreenDelta = 0.35f;

        private MobileGestureMode _mode;
        private Vector2 _previousPosition;
        private Vector3 _previousWorldPoint;
        private double _previousSampleTime;
        private float _filteredSpinSpeed;
        private float _previousPinchDistance;
        private bool _hasWorldPoint;
        private bool _hasSpinSample;
        private bool _waitForAllTouchesToLift;
        private float _oppositeDirectionTravel;
        private double _gestureStartTime;
        private float _gestureSignedTravel;
        private float _gestureTotalTravel;
        private float _filteredReleasePixelVelocity;

        public event Action<float> SpinGestureCompleted;

        public MobileGestureMode CurrentMode => _mode;
        public bool IsInteracting => _mode != MobileGestureMode.None;
        public RotorRigidbodyController Rotor => rotor;
        public OrbitPresentationCamera OrbitCamera => orbitCamera;

        public void SetSpinSensitivity(float value)
        {
            SetTouchResponse(value);
        }

        public void SetTouchResponse(float normalizedResponse)
        {
            global::ThreeBladeEDC.FidgetSpinnerMotion.TouchResponseProfile profile =
                global::ThreeBladeEDC.FidgetSpinnerMotion.ResolveTouchResponse(
                    normalizedResponse);
            spinSensitivity = profile.NormalizedResponse;
            maxSpinSpeed = profile.MaximumAngularSpeed;
            screenSpeedForFullSpin = profile.ScreenSpeedForFullSpin;
            spinSmoothing = profile.DragFollowResponse;
            spinBrakeResponse = profile.DragBrakeResponse;
            rotor?.SetMaximumAngularSpeed(maxSpinSpeed);
        }

        public void SetMaximumSpinSpeed(float value)
        {
            maxSpinSpeed = Mathf.Clamp(value, 0.1f, 80f);
        }

        public void SetReversalStopDuration(float value)
        {
            reversalStopDuration = Mathf.Clamp(value, 0.05f, 1.5f);
        }

        public void SetFlipOnRelease(bool value)
        {
            flipOnRelease = value;
        }

        public void Configure(
            RotorRigidbodyController rotorController,
            Camera camera,
            OrbitPresentationCamera presentationCamera)
        {
            rotor = rotorController;
            interactionCamera = camera;
            orbitCamera = presentationCamera;
            CancelAll();
        }

        private void Awake()
        {
            ResolveReferences();
        }

        private void Update()
        {
            if (Touchscreen.current != null)
            {
                ReadTouches(Touchscreen.current);
                return;
            }

            ReadMouseFallback();
        }

        private void OnDisable()
        {
            CancelAll();
            if (rotor != null)
            {
                rotor.SetMotorActive(false);
            }
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                CancelAll();
                if (rotor != null)
                {
                    rotor.SetMotorActive(false);
                }
            }
        }

        public MobileGestureMode ClassifyScreenPoint(Vector2 screenPosition)
        {
            Camera camera = ResolveCamera();
            if (camera == null)
            {
                return MobileGestureMode.Orbit;
            }

            Ray ray = camera.ScreenPointToRay(screenPosition);
            if (Physics.Raycast(ray, out RaycastHit hit, maxRayDistance)
                && (hit.collider.GetComponentInParent<SpinnerTouchSurface>() != null
                    || hit.collider.GetComponentInParent<RotorRigidbodyController>() == rotor))
            {
                return MobileGestureMode.Spin;
            }

            if (rotor != null)
            {
                Vector3 center = camera.WorldToScreenPoint(rotor.PivotWorld);
                float radius = Mathf.Min(Screen.width, Screen.height) * fallbackTouchRadius;
                if (center.z > 0f && Vector2.Distance(screenPosition, center) <= radius)
                {
                    return MobileGestureMode.Spin;
                }
            }

            return MobileGestureMode.Orbit;
        }

        public void CancelAll()
        {
            if (rotor != null && rotor.IsFingerControlling)
            {
                rotor.EndFingerControl();
            }
            _mode = MobileGestureMode.None;
            _hasWorldPoint = false;
            _hasSpinSample = false;
            _filteredSpinSpeed = 0f;
            _previousPinchDistance = 0f;
            _oppositeDirectionTravel = 0f;
            _gestureStartTime = 0d;
            _gestureSignedTravel = 0f;
            _gestureTotalTravel = 0f;
            _filteredReleasePixelVelocity = 0f;
        }

        private void ReadTouches(Touchscreen touchscreen)
        {
            TouchControl first = null;
            TouchControl second = null;
            foreach (TouchControl touch in touchscreen.touches)
            {
                if (!touch.press.isPressed)
                {
                    continue;
                }

                if (first == null)
                {
                    first = touch;
                }
                else
                {
                    second = touch;
                    break;
                }
            }

            if (first == null)
            {
                CompleteActiveGesture();
                _waitForAllTouchesToLift = false;
                return;
            }

            if (_waitForAllTouchesToLift)
            {
                return;
            }

            if (second != null)
            {
                Vector2 firstPosition = first.position.ReadValue();
                Vector2 secondPosition = second.position.ReadValue();
                float pinchDistance = Vector2.Distance(firstPosition, secondPosition);
                if (_mode != MobileGestureMode.Pinch)
                {
                    _mode = MobileGestureMode.Pinch;
                    _previousPinchDistance = pinchDistance;
                    _hasSpinSample = false;
                    return;
                }

                if (_previousPinchDistance > 1f && pinchDistance > 1f)
                {
                    orbitCamera?.ZoomByScale(pinchDistance / _previousPinchDistance);
                }
                _previousPinchDistance = pinchDistance;
                return;
            }

            if (_mode == MobileGestureMode.Pinch)
            {
                CancelAll();
                _waitForAllTouchesToLift = true;
                return;
            }

            Vector2 position = first.position.ReadValue();
            int touchId = first.touchId.ReadValue();
            if (_mode == MobileGestureMode.None)
            {
                if (IsPointerOverUi(touchId))
                {
                    _waitForAllTouchesToLift = true;
                    return;
                }

                BeginSinglePointer(position);
                return;
            }

            UpdateSinglePointer(position, first.pressure.ReadValue());
        }

        private void ReadMouseFallback()
        {
            Mouse mouse = Mouse.current;
            if (mouse == null)
            {
                return;
            }

            float scroll = mouse.scroll.ReadValue().y;
            if (Mathf.Abs(scroll) > Mathf.Epsilon)
            {
                orbitCamera?.ZoomByScale(Mathf.Exp(scroll * 0.0012f));
            }

            if (mouse.leftButton.wasPressedThisFrame)
            {
                if (!IsPointerOverUi(-1))
                {
                    BeginSinglePointer(mouse.position.ReadValue());
                }
            }

            if (mouse.leftButton.isPressed && _mode != MobileGestureMode.None)
            {
                UpdateSinglePointer(mouse.position.ReadValue(), 1f);
            }

            if (mouse.rightButton.wasPressedThisFrame)
            {
                _mode = MobileGestureMode.Orbit;
                _previousPosition = mouse.position.ReadValue();
                _previousSampleTime = Time.unscaledTimeAsDouble;
            }

            if (mouse.rightButton.isPressed && _mode == MobileGestureMode.Orbit)
            {
                UpdateSinglePointer(mouse.position.ReadValue(), 1f);
            }

            if (mouse.leftButton.wasReleasedThisFrame
                || mouse.rightButton.wasReleasedThisFrame)
            {
                CompleteActiveGesture();
            }
        }

        private void BeginSinglePointer(Vector2 position)
        {
            ResolveReferences();
            _mode = ClassifyScreenPoint(position);
            _previousPosition = position;
            _previousSampleTime = Time.unscaledTimeAsDouble;
            _filteredSpinSpeed = 0f;
            _hasSpinSample = false;
            _oppositeDirectionTravel = 0f;
            _gestureStartTime = _previousSampleTime;
            _gestureSignedTravel = 0f;
            _gestureTotalTravel = 0f;
            _filteredReleasePixelVelocity = 0f;
            _hasWorldPoint = _mode == MobileGestureMode.Spin
                && TryProjectToRotorPlane(position, out _previousWorldPoint);
            if (_mode == MobileGestureMode.Spin)
            {
                rotor?.BeginFingerControl();
                FidgetHapticRouter.Emit(FidgetSemanticEvent.Selection, 0.4f);
            }
        }

        private void UpdateSinglePointer(Vector2 position, float pressure)
        {
            double now = Time.unscaledTimeAsDouble;
            float deltaTime = (float)(now - _previousSampleTime);
            if (deltaTime <= 0.0001f)
            {
                return;
            }

            Vector2 screenDelta = position - _previousPosition;
            if (_mode == MobileGestureMode.Orbit)
            {
                orbitCamera?.OrbitByPixels(screenDelta);
            }
            else if (_mode == MobileGestureMode.Spin && rotor != null)
            {
                Vector3 currentWorldPoint;
                bool hasCurrentWorldPoint = TryProjectToRotorPlane(
                    position,
                    out currentWorldPoint);
                float fallbackAngle = CalculateScreenFallbackAngle(
                    _previousPosition,
                    position);
                float angleDegrees = fallbackAngle;
                if (_hasWorldPoint && hasCurrentWorldPoint)
                {
                    Vector3 previousRadius = Vector3.ProjectOnPlane(
                        _previousWorldPoint - rotor.PivotWorld,
                        rotor.SpinAxisWorld);
                    Vector3 currentRadius = Vector3.ProjectOnPlane(
                        currentWorldPoint - rotor.PivotWorld,
                        rotor.SpinAxisWorld);
                    float minimumRadiusSquared = minimumWorldRadius * minimumWorldRadius;
                    if (previousRadius.sqrMagnitude >= minimumRadiusSquared
                        && currentRadius.sqrMagnitude >= minimumRadiusSquared)
                    {
                        float worldAngle = Vector3.SignedAngle(
                            previousRadius,
                            currentRadius,
                            rotor.SpinAxisWorld);
                        angleDegrees = Mathf.Abs(worldAngle) >= Mathf.Abs(fallbackAngle) * 0.4f
                            ? worldAngle
                            : fallbackAngle;
                    }
                }

                if (screenDelta.sqrMagnitude < minimumScreenDelta * minimumScreenDelta)
                {
                    angleDegrees = 0f;
                }
                angleDegrees = Mathf.Clamp(
                    angleDegrees,
                    -maximumSampleAngleDegrees,
                    maximumSampleAngleDegrees);

                float rawSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion
                    .MapGestureToAngularSpeed(
                        angleDegrees,
                        screenDelta.magnitude,
                        deltaTime,
                        spinSensitivity,
                        maxSpinSpeed,
                        screenSpeedForFullSpin,
                        pressure);

                if (Mathf.Abs(angleDegrees) > Mathf.Epsilon)
                {
                    float signedTravel = Mathf.Sign(angleDegrees)
                        * screenDelta.magnitude;
                    _gestureSignedTravel += signedTravel;
                    _gestureTotalTravel += screenDelta.magnitude;
                    float releaseSampleVelocity = signedTravel / deltaTime;
                    float releaseBlend = 1f - Mathf.Exp(-18f * deltaTime);
                    _filteredReleasePixelVelocity = Mathf.Lerp(
                        _filteredReleasePixelVelocity,
                        releaseSampleVelocity,
                        releaseBlend);
                }

                float currentSpeed = rotor.AngularSpeedRadians;
                bool requestsOppositeDirection = Mathf.Abs(currentSpeed) >= reversalMinimumSpeed
                    && Mathf.Abs(rawSpeed) >= reversalMinimumSpeed
                    && Mathf.Sign(currentSpeed) != Mathf.Sign(rawSpeed);
                _oppositeDirectionTravel = requestsOppositeDirection
                    ? _oppositeDirectionTravel + screenDelta.magnitude
                    : 0f;
                if (global::ThreeBladeEDC.FidgetSpinnerMotion.ConfirmsDirectionReversal(
                        currentSpeed,
                        rawSpeed,
                        _oppositeDirectionTravel,
                        reversalMinimumSpeed,
                        reversalConfirmationPixels))
                {
                    rotor.EndFingerControl();
                    rotor.SmoothStop(reversalStopDuration);
                    FidgetHapticRouter.Emit(FidgetSemanticEvent.DirectionReversed);
                    _mode = MobileGestureMode.None;
                    _hasSpinSample = false;
                    _waitForAllTouchesToLift = true;
                    return;
                }

                if (requestsOppositeDirection)
                {
                    StorePointerSample(position, now, currentWorldPoint, hasCurrentWorldPoint);
                    return;
                }

                float sourceSpeed = _hasSpinSample
                    ? _filteredSpinSpeed
                    : currentSpeed;
                _filteredSpinSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion
                    .FollowDragSpeed(
                        sourceSpeed,
                        rawSpeed,
                        deltaTime,
                        spinSmoothing,
                        spinBrakeResponse,
                        maxSpinSpeed);
                _hasSpinSample = true;
                rotor.DriveFromFinger(_filteredSpinSpeed);
                _previousWorldPoint = currentWorldPoint;
                _hasWorldPoint = hasCurrentWorldPoint;
            }

            _previousPosition = position;
            _previousSampleTime = now;
        }

        private float CalculateScreenFallbackAngle(Vector2 previous, Vector2 current)
        {
            Vector2 center = GetInteractionCenter();
            Vector2 delta = current - previous;
            Vector2 radial = ((previous + current) * 0.5f) - center;
            float signedPixels;
            if (radial.sqrMagnitude > 24f * 24f)
            {
                Vector2 tangent = new Vector2(-radial.y, radial.x).normalized;
                Camera camera = ResolveCamera();
                signedPixels = global::ThreeBladeEDC.FidgetSpinnerMotion
                    .AlignScreenTangentToSpinAxis(
                        Vector2.Dot(delta, tangent),
                        camera != null
                            ? camera.transform.forward
                            : Vector3.zero,
                        rotor != null ? rotor.SpinAxisWorld : Vector3.zero);
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

            return signedPixels * fallbackDegreesPerPixel;
        }

        private Vector2 GetInteractionCenter()
        {
            Camera camera = ResolveCamera();
            if (camera == null || rotor == null)
            {
                return new Vector2(Screen.width * 0.5f, Screen.height * 0.5f);
            }

            Vector3 center = camera.WorldToScreenPoint(rotor.PivotWorld);
            return new Vector2(center.x, center.y);
        }

        private void StorePointerSample(
            Vector2 position,
            double sampleTime,
            Vector3 worldPoint,
            bool hasWorldPoint)
        {
            _previousPosition = position;
            _previousSampleTime = sampleTime;
            _previousWorldPoint = worldPoint;
            _hasWorldPoint = hasWorldPoint;
        }

        private void CompleteActiveGesture()
        {
            bool completedSpin = _mode == MobileGestureMode.Spin
                && _hasSpinSample
                && rotor != null;
            bool qualifiedFling = false;
            float releaseSpeed = 0f;
            if (completedSpin)
            {
                float duration = (float)(Time.unscaledTimeAsDouble - _gestureStartTime);
                qualifiedFling = global::ThreeBladeEDC.FidgetSpinnerMotion
                    .QualifiesReleaseFling(
                        _filteredReleasePixelVelocity,
                        _gestureSignedTravel,
                        _gestureTotalTravel,
                        duration);
                releaseSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion
                    .ResolveReleaseAngularSpeed(
                        _filteredSpinSpeed,
                        _filteredReleasePixelVelocity,
                        _gestureSignedTravel,
                        _gestureTotalTravel,
                        duration,
                        spinSensitivity,
                        maxSpinSpeed,
                        screenSpeedForFullSpin);
                rotor.DriveFromFinger(releaseSpeed);
                if (qualifiedFling)
                {
                    rotor.RecordInitialFlickForce(
                        Mathf.Abs(releaseSpeed) / Mathf.Max(0.1f, maxSpinSpeed));
                }
            }

            rotor?.EndFingerControl();
            if (completedSpin)
            {
                float normalizedForce = Mathf.Clamp01(Mathf.Max(
                    Mathf.Abs(releaseSpeed) / Mathf.Max(0.1f, maxSpinSpeed),
                    _gestureTotalTravel / Mathf.Max(1f, Screen.width * 0.6f)));
                SpinGestureCompleted?.Invoke(normalizedForce);
            }
            if (completedSpin && qualifiedFling)
            {
                if (flipOnRelease && Mathf.Abs(_filteredSpinSpeed) > 0.05f)
                {
                    rotor.TriggerFlip(Mathf.Sign(_filteredSpinSpeed));
                }
                FidgetHapticRouter.Emit(FidgetSemanticEvent.Released);
            }

            CancelAll();
        }

        private bool TryProjectToRotorPlane(Vector2 screenPosition, out Vector3 point)
        {
            point = default;
            Camera camera = ResolveCamera();
            if (camera == null || rotor == null)
            {
                return false;
            }

            Plane plane = new Plane(rotor.SpinAxisWorld, rotor.PivotWorld);
            Ray ray = camera.ScreenPointToRay(screenPosition);
            if (!plane.Raycast(ray, out float enter) || enter < 0f)
            {
                return false;
            }

            point = ray.GetPoint(enter);
            return true;
        }

        private static bool IsPointerOverUi(int pointerId)
        {
            return EventSystem.current != null
                && EventSystem.current.IsPointerOverGameObject(pointerId);
        }

        private void ResolveReferences()
        {
            if (rotor == null)
            {
                rotor = FindAnyObjectByType<RotorRigidbodyController>();
            }
            if (interactionCamera == null)
            {
                interactionCamera = Camera.main;
            }
            if (orbitCamera == null && interactionCamera != null)
            {
                orbitCamera = interactionCamera.GetComponent<OrbitPresentationCamera>();
            }
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
