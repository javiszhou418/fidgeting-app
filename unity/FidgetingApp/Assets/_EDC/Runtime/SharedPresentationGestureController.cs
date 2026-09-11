using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;

namespace FidgetingApp.EDC
{
    public enum SharedPresentationGestureMode
    {
        None,
        ReservedForProduct,
        Orbit,
        Pinch
    }

    /// <summary>
    /// Gives the fifth product the same presentation gestures as the rotor
    /// products while reserving touches that begin on the sliding lid.
    /// </summary>
    [DisallowMultipleComponent]
    [DefaultExecutionOrder(-45)]
    public sealed class SharedPresentationGestureController : MonoBehaviour
    {
        [SerializeField] private EdcPortraitCameraFramer presentationCamera;
        [SerializeField] private Camera interactionCamera;
        [SerializeField] private Collider productInteractionSurface;
        [SerializeField, Min(0.1f)] private float maximumRayDistance = 5f;

        private SharedPresentationGestureMode mode;
        private Vector2 previousPosition;
        private float previousPinchDistance;
        private bool waitForTouchesToClear;

        public bool IsInteracting =>
            mode == SharedPresentationGestureMode.Orbit
            || mode == SharedPresentationGestureMode.Pinch;
        public bool IsPinching => mode == SharedPresentationGestureMode.Pinch;
        public bool IsOrbiting => mode == SharedPresentationGestureMode.Orbit;
        public bool IsProductReserved =>
            mode == SharedPresentationGestureMode.ReservedForProduct;
        public SharedPresentationGestureMode CurrentMode => mode;
        public Collider ProductInteractionSurface => productInteractionSurface;
        public int TouchReceiptCount { get; private set; }
        public int InputUpdateCount { get; private set; }
        public int PinchUpdateCount { get; private set; }
        public int OrbitUpdateCount { get; private set; }

        public void Configure(
            EdcPortraitCameraFramer cameraFramer,
            Camera camera,
            Collider interactionSurface)
        {
            presentationCamera = cameraFramer;
            interactionCamera = camera;
            productInteractionSurface = interactionSurface;
            CancelGesture();
        }

        private void Awake()
        {
            if (interactionCamera == null)
            {
                interactionCamera = GetComponent<Camera>();
            }
            if (presentationCamera == null)
            {
                presentationCamera = GetComponent<EdcPortraitCameraFramer>();
            }
        }

        private void Update()
        {
            InputUpdateCount++;
            Touchscreen touchscreen = Touchscreen.current;
            if (touchscreen != null && ReadTouches(touchscreen))
            {
                return;
            }
            ReadMouse();
        }

        private bool ReadTouches(Touchscreen touchscreen)
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
                waitForTouchesToClear = false;
                CancelGesture();
                return false;
            }

            if (waitForTouchesToClear)
            {
                return true;
            }

            if (second != null)
            {
                float distance = Vector2.Distance(
                    first.position.ReadValue(),
                    second.position.ReadValue());
                if (mode != SharedPresentationGestureMode.Pinch)
                {
                    mode = SharedPresentationGestureMode.Pinch;
                    previousPinchDistance = distance;
                    TouchReceiptCount += 2;
                    Debug.Log(
                        "[MagneticSlideRuntime] pinch-begin "
                        + $"distance={distance:F1}");
                    return true;
                }
                if (previousPinchDistance > 1f && distance > 1f)
                {
                    presentationCamera?.ZoomByScale(distance / previousPinchDistance);
                    PinchUpdateCount++;
                }
                previousPinchDistance = distance;
                return true;
            }

            if (mode == SharedPresentationGestureMode.Pinch)
            {
                waitForTouchesToClear = true;
                CancelGesture();
                return true;
            }

            Vector2 position = first.position.ReadValue();
            if (mode == SharedPresentationGestureMode.None)
            {
                TouchReceiptCount++;
                int touchId = first.touchId.ReadValue();
                if (IsPointerOverUi(touchId) || HitsProductSurface(position))
                {
                    mode = SharedPresentationGestureMode.ReservedForProduct;
                    Debug.Log(
                        "[MagneticSlideRuntime] presentation-reserved-for-product "
                        + $"touch={touchId}");
                    return true;
                }
                mode = SharedPresentationGestureMode.Orbit;
                previousPosition = position;
                Debug.Log(
                    "[MagneticSlideRuntime] orbit-begin "
                    + $"touch={touchId} x={position.x:F1} y={position.y:F1}");
                return true;
            }

            if (mode == SharedPresentationGestureMode.Orbit)
            {
                presentationCamera?.OrbitByPixels(position - previousPosition);
                previousPosition = position;
                OrbitUpdateCount++;
            }
            return true;
        }

        private void ReadMouse()
        {
            Mouse mouse = Mouse.current;
            if (mouse == null)
            {
                return;
            }
            float scroll = mouse.scroll.ReadValue().y;
            if (Mathf.Abs(scroll) > Mathf.Epsilon)
            {
                presentationCamera?.ZoomByScale(Mathf.Exp(scroll * 0.0012f));
            }
            if (mouse.rightButton.wasPressedThisFrame)
            {
                mode = SharedPresentationGestureMode.Orbit;
                previousPosition = mouse.position.ReadValue();
            }
            if (mouse.rightButton.isPressed
                && mode == SharedPresentationGestureMode.Orbit)
            {
                Vector2 position = mouse.position.ReadValue();
                presentationCamera?.OrbitByPixels(position - previousPosition);
                previousPosition = position;
                OrbitUpdateCount++;
            }
            if (mouse.rightButton.wasReleasedThisFrame)
            {
                CancelGesture();
            }
        }

        private bool HitsProductSurface(Vector2 screenPosition)
        {
            Camera camera = interactionCamera != null ? interactionCamera : Camera.main;
            if (camera == null || productInteractionSurface == null)
            {
                return false;
            }
            Ray ray = camera.ScreenPointToRay(screenPosition);
            return productInteractionSurface.Raycast(ray, out _, maximumRayDistance);
        }

        private static bool IsPointerOverUi(int pointerId)
        {
            EventSystem eventSystem = EventSystem.current;
            return eventSystem != null
                && (pointerId >= 0
                    ? eventSystem.IsPointerOverGameObject(pointerId)
                    : eventSystem.IsPointerOverGameObject());
        }

        private void CancelGesture()
        {
            mode = SharedPresentationGestureMode.None;
            previousPinchDistance = 0f;
        }

        private void OnDisable()
        {
            waitForTouchesToClear = false;
            CancelGesture();
        }
    }
}
