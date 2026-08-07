using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;

namespace FidgetingApp.EDC
{
    /// <summary>
    /// Gives the fifth product the same presentation gestures as the rotor
    /// products while reserving touches that begin on the sliding lid.
    /// </summary>
    [DisallowMultipleComponent]
    [DefaultExecutionOrder(-45)]
    public sealed class SharedPresentationGestureController : MonoBehaviour
    {
        private enum GestureMode
        {
            None,
            ReservedForProduct,
            Orbit,
            Pinch
        }

        [SerializeField] private EdcPortraitCameraFramer presentationCamera;
        [SerializeField] private Camera interactionCamera;
        [SerializeField] private Collider productInteractionSurface;
        [SerializeField, Min(0.1f)] private float maximumRayDistance = 5f;

        private GestureMode mode;
        private Vector2 previousPosition;
        private float previousPinchDistance;
        private bool waitForTouchesToClear;

        public bool IsInteracting => mode == GestureMode.Orbit || mode == GestureMode.Pinch;

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
                if (mode != GestureMode.Pinch)
                {
                    mode = GestureMode.Pinch;
                    previousPinchDistance = distance;
                    return true;
                }
                if (previousPinchDistance > 1f && distance > 1f)
                {
                    presentationCamera?.ZoomByScale(distance / previousPinchDistance);
                }
                previousPinchDistance = distance;
                return true;
            }

            if (mode == GestureMode.Pinch)
            {
                waitForTouchesToClear = true;
                CancelGesture();
                return true;
            }

            Vector2 position = first.position.ReadValue();
            if (mode == GestureMode.None)
            {
                int touchId = first.touchId.ReadValue();
                if (IsPointerOverUi(touchId) || HitsProductSurface(position))
                {
                    mode = GestureMode.ReservedForProduct;
                    return true;
                }
                mode = GestureMode.Orbit;
                previousPosition = position;
                return true;
            }

            if (mode == GestureMode.Orbit)
            {
                presentationCamera?.OrbitByPixels(position - previousPosition);
                previousPosition = position;
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
                mode = GestureMode.Orbit;
                previousPosition = mouse.position.ReadValue();
            }
            if (mouse.rightButton.isPressed && mode == GestureMode.Orbit)
            {
                Vector2 position = mouse.position.ReadValue();
                presentationCamera?.OrbitByPixels(position - previousPosition);
                previousPosition = position;
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
            mode = GestureMode.None;
            previousPinchDistance = 0f;
        }

        private void OnDisable()
        {
            waitForTouchesToClear = false;
            CancelGesture();
        }
    }
}
