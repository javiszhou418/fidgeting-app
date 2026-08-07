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
        [SerializeField] private bool showTouchFeedback = true;

        [Header("Flick")]
        [SerializeField, Range(0f, 1f)] private float sensitivity = 0.3f;
        [SerializeField, Min(0.1f)] private float maxFlickSpeed = 24f;
        [SerializeField, Min(0f)] private float minimumAngleDegrees = 0.01f;
        [SerializeField, Min(0f)] private float minimumSwipeDistancePixels = 2f;
        [SerializeField, Min(0f)] private float smoothing = 12f;
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
        private bool _flipTriggeredForGesture;
        private bool _gestureLockedByReversal;
        private Texture2D _touchRingTexture;

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

        private void OnDestroy()
        {
            if (_touchRingTexture != null)
            {
                Destroy(_touchRingTexture);
            }
        }

        private void OnGUI()
        {
            if (!showTouchFeedback || !IsPointerActive)
            {
                return;
            }

            EnsureTouchRingTexture();
            float size = Mathf.Clamp(Screen.width * 0.055f, 56f, 84f);
            Rect touchRect = new Rect(
                _currentScreenPosition.x - size * 0.5f,
                Screen.height - _currentScreenPosition.y - size * 0.5f,
                size,
                size);
            GUI.DrawTexture(touchRect, _touchRingTexture, ScaleMode.StretchToFill, true);
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
            _flipTriggeredForGesture = false;
            _gestureLockedByReversal = false;
            _hasWorldPoint = TryProjectToRotorPlane(
                screenPosition,
                out _previousWorldPoint);
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
                float rawSpeed = Mathf.Clamp(
                    angleDegrees * Mathf.Deg2Rad / deltaTime * sensitivity,
                    -maxFlickSpeed,
                    maxFlickSpeed);
                float currentSpeed = rotor.AngularSpeedRadians;

                if (!_flipTriggeredForGesture)
                {
                    rotor.TriggerFlip(Mathf.Sign(rawSpeed));
                    _flipTriggeredForGesture = true;
                }

                bool reversed = Mathf.Abs(currentSpeed) >= reversalSpeedThreshold
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

                float blend = smoothing <= Mathf.Epsilon
                    ? 1f
                    : 1f - Mathf.Exp(-smoothing * deltaTime);
                _filteredFlickSpeed = _hasFlickSample
                    ? Mathf.Lerp(_filteredFlickSpeed, rawSpeed, blend)
                    : rawSpeed;
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
                rotor.SmoothStop(reversalStopDuration);
            }
            else if (_hasFlickSample && !driveRotorWhileDragging)
            {
                rotor.SetSpinVelocity(_filteredFlickSpeed);
            }

            CancelPointer();
        }

        private void CancelPointer()
        {
            _pointerSource = PointerSource.None;
            _hasWorldPoint = false;
            _hasFlickSample = false;
            _flipTriggeredForGesture = false;
            _gestureLockedByReversal = false;
            _filteredFlickSpeed = 0f;
            _totalPointerTravel = 0f;
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

        private void EnsureTouchRingTexture()
        {
            if (_touchRingTexture != null)
            {
                return;
            }

            const int size = 64;
            _touchRingTexture = new Texture2D(
                size,
                size,
                TextureFormat.RGBA32,
                false)
            {
                name = "Touch Feedback Ring",
                filterMode = FilterMode.Bilinear,
                wrapMode = TextureWrapMode.Clamp,
                hideFlags = HideFlags.HideAndDontSave
            };

            Color32[] pixels = new Color32[size * size];
            Vector2 center = Vector2.one * ((size - 1) * 0.5f);
            float outer = size * 0.46f;
            float inner = size * 0.35f;
            for (int y = 0; y < size; y++)
            {
                for (int x = 0; x < size; x++)
                {
                    float radius = Vector2.Distance(new Vector2(x, y), center);
                    float alpha = radius >= inner && radius <= outer
                        ? 0.72f
                        : 0f;
                    pixels[y * size + x] = new Color(0.12f, 0.72f, 0.9f, alpha);
                }
            }

            _touchRingTexture.SetPixels32(pixels);
            _touchRingTexture.Apply(false, true);
        }
    }
}
