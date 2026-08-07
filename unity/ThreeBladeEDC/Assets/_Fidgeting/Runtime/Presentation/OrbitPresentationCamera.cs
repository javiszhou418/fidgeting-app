using UnityEngine;
using UnityEngine.InputSystem;

namespace ThreeBladeEDC.Presentation
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class OrbitPresentationCamera : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private float distance = 0.24f;
        [SerializeField] private float orbitSensitivity = 0.18f;
        [SerializeField] private float zoomSensitivity = 0.008f;
        [SerializeField] private Vector2 pitchLimits = new Vector2(3f, 89f);
        [SerializeField] private Vector2 distanceLimits = new Vector2(0.16f, 0.40f);
        [SerializeField] private bool readDesktopInput = true;

        private float _yaw = 32f;
        private float _pitch = 42f;
        private int _preset;

        public Transform Target
        {
            get => target;
            set => target = value;
        }

        public float Distance => distance;

        private void Awake()
        {
            Camera cameraComponent = GetComponent<Camera>();
            cameraComponent.usePhysicalProperties = true;
            cameraComponent.focalLength = 85f;
            cameraComponent.sensorSize = new Vector2(36f, 24f);
            cameraComponent.nearClipPlane = 0.01f;
            cameraComponent.farClipPlane = 10f;
        }

        private void LateUpdate()
        {
            if (target == null)
            {
                return;
            }

            Mouse mouse = readDesktopInput ? Mouse.current : null;
            if (mouse != null && mouse.rightButton.isPressed)
            {
                OrbitByPixels(mouse.delta.ReadValue());
            }

            if (mouse != null)
            {
                distance = Mathf.Clamp(
                    distance - mouse.scroll.ReadValue().y * zoomSensitivity * 0.01f,
                    distanceLimits.x,
                    distanceLimits.y);
            }

            Keyboard keyboard = Keyboard.current;
            if (keyboard != null && keyboard.vKey.wasPressedThisFrame)
            {
                CyclePreset();
            }

            Quaternion orbit = Quaternion.Euler(_pitch, _yaw, 0f);
            transform.position = target.position + orbit * (Vector3.back * distance);
            transform.LookAt(target.position, Vector3.up);
        }

        public void CyclePreset()
        {
            _preset = (_preset + 1) % 3;
            switch (_preset)
            {
                case 0:
                    _yaw = 32f;
                    _pitch = 42f;
                    distance = 0.24f;
                    break;
                case 1:
                    _yaw = 0f;
                    _pitch = 89f;
                    distance = 0.22f;
                    break;
                default:
                    _yaw = 0f;
                    _pitch = 3f;
                    distance = 0.25f;
                    break;
            }
        }

        public void ResetHero()
        {
            _preset = 0;
            _yaw = 32f;
            _pitch = 42f;
            distance = 0.24f;
        }

        public void OrbitByPixels(Vector2 screenDelta)
        {
            _yaw += screenDelta.x * orbitSensitivity;
            _pitch = Mathf.Clamp(
                _pitch - screenDelta.y * orbitSensitivity,
                pitchLimits.x,
                pitchLimits.y);
        }

        public void ZoomByScale(float scale)
        {
            if (scale <= Mathf.Epsilon)
            {
                return;
            }

            SetDistance(distance / scale);
        }

        public void SetDistance(float value)
        {
            distance = Mathf.Clamp(value, distanceLimits.x, distanceLimits.y);
        }

        public void SetDesktopInputEnabled(bool enabled)
        {
            readDesktopInput = enabled;
        }
    }
}
