using ThreeBladeEDC.Presentation;
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
        [SerializeField, Min(0.01f)] private float spinSensitivity = 0.34f;
        [SerializeField, Min(0.1f)] private float maxSpinSpeed = 24f;
        [SerializeField, Min(0f)] private float spinSmoothing = 15f;
        [SerializeField, Min(0.01f)] private float maxRayDistance = 5f;

        private MobileGestureMode _mode;
        private Vector2 _previousPosition;
        private Vector3 _previousWorldPoint;
        private double _previousSampleTime;
        private float _filteredSpinSpeed;
        private float _previousPinchDistance;
        private bool _hasWorldPoint;
        private bool _hasSpinSample;
        private bool _waitForAllTouchesToLift;

        public MobileGestureMode CurrentMode => _mode;
        public bool IsInteracting => _mode != MobileGestureMode.None;
        public RotorRigidbodyController Rotor => rotor;
        public OrbitPresentationCamera OrbitCamera => orbitCamera;

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
                && hit.collider.GetComponentInParent<SpinnerTouchSurface>() != null)
            {
                return MobileGestureMode.Spin;
            }

            return MobileGestureMode.Orbit;
        }

        public void CancelAll()
        {
            _mode = MobileGestureMode.None;
            _hasWorldPoint = false;
            _hasSpinSample = false;
            _filteredSpinSpeed = 0f;
            _previousPinchDistance = 0f;
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
                CancelAll();
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

            UpdateSinglePointer(position);
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
                UpdateSinglePointer(mouse.position.ReadValue());
            }

            if (mouse.rightButton.wasPressedThisFrame)
            {
                _mode = MobileGestureMode.Orbit;
                _previousPosition = mouse.position.ReadValue();
                _previousSampleTime = Time.unscaledTimeAsDouble;
            }

            if (mouse.rightButton.isPressed && _mode == MobileGestureMode.Orbit)
            {
                UpdateSinglePointer(mouse.position.ReadValue());
            }

            if (mouse.leftButton.wasReleasedThisFrame
                || mouse.rightButton.wasReleasedThisFrame)
            {
                CancelAll();
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
            _hasWorldPoint = _mode == MobileGestureMode.Spin
                && TryProjectToRotorPlane(position, out _previousWorldPoint);
        }

        private void UpdateSinglePointer(Vector2 position)
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
                float angleDegrees;
                if (_hasWorldPoint && hasCurrentWorldPoint)
                {
                    Vector3 previousRadius = Vector3.ProjectOnPlane(
                        _previousWorldPoint - rotor.PivotWorld,
                        rotor.SpinAxisWorld);
                    Vector3 currentRadius = Vector3.ProjectOnPlane(
                        currentWorldPoint - rotor.PivotWorld,
                        rotor.SpinAxisWorld);
                    angleDegrees = Vector3.SignedAngle(
                        previousRadius,
                        currentRadius,
                        rotor.SpinAxisWorld);
                }
                else
                {
                    angleDegrees = screenDelta.x * 0.32f;
                }

                float rawSpeed = Mathf.Clamp(
                    angleDegrees * Mathf.Deg2Rad / deltaTime * spinSensitivity,
                    -maxSpinSpeed,
                    maxSpinSpeed);
                float blend = spinSmoothing <= Mathf.Epsilon
                    ? 1f
                    : 1f - Mathf.Exp(-spinSmoothing * deltaTime);
                _filteredSpinSpeed = _hasSpinSample
                    ? Mathf.Lerp(_filteredSpinSpeed, rawSpeed, blend)
                    : rawSpeed;
                _hasSpinSample = true;
                rotor.SetSpinVelocity(_filteredSpinSpeed);
                _previousWorldPoint = currentWorldPoint;
                _hasWorldPoint = hasCurrentWorldPoint;
            }

            _previousPosition = position;
            _previousSampleTime = now;
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
