using UnityEngine;

namespace FidgetingApp.EDC.Candidates
{
    public sealed class MagneticSlideTileGate11PreviewController : MonoBehaviour
    {
        [Header("Mechanism")]
        [SerializeField] private Transform rotatingCarrier;
        [SerializeField] private Transform movingTop;
        [SerializeField] private Transform topLocalSlide;
        [SerializeField] private Vector3 rotationAxisLocal = Vector3.up;
        [SerializeField] private Vector3 slideAxisLocal = Vector3.forward;
        [SerializeField] private float maximumTravelMeters = 0.018076433f;
        [SerializeField] private float angleDegrees;
        [SerializeField] private float travelMeters;

        [Header("Camera orbit")]
        [SerializeField] private Camera previewCamera;
        [SerializeField] private Transform orbitTarget;
        [SerializeField] private float orbitSensitivity = 0.22f;
        [SerializeField] private float zoomSensitivity = 0.018f;

        private Vector3 topSlideClosedPosition;
        private Vector3 cameraTarget;
        private float cameraDistance;
        private float cameraYaw;
        private float cameraPitch = 24f;

        public float AngleDegrees => angleDegrees;
        public float TravelMeters => travelMeters;
        public Transform RotatingCarrier => rotatingCarrier;
        public Transform MovingTop => movingTop;
        public Transform TopLocalSlide => topLocalSlide;

        private void Awake()
        {
            if (topLocalSlide != null)
            {
                topSlideClosedPosition = topLocalSlide.localPosition;
            }

            if (previewCamera != null)
            {
                cameraTarget = orbitTarget != null
                    ? orbitTarget.position
                    : transform.position;
                cameraDistance = Vector3.Distance(
                    previewCamera.transform.position,
                    cameraTarget);
                Vector3 direction = previewCamera.transform.position - cameraTarget;
                cameraYaw = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;
                cameraPitch = Mathf.Asin(
                    Mathf.Clamp(direction.y / Mathf.Max(cameraDistance, 0.0001f), -1f, 1f))
                    * Mathf.Rad2Deg;
            }

            ResetPose();
        }

        private void Update()
        {
            bool shift = Input.GetKey(KeyCode.LeftShift)
                || Input.GetKey(KeyCode.RightShift);
            if (Input.GetMouseButton(0) && !shift)
            {
                angleDegrees += Input.GetAxis("Mouse X") * 0.9f;
                travelMeters = Mathf.Clamp(
                    travelMeters - Input.GetAxis("Mouse Y") * 0.00012f,
                    0f,
                    maximumTravelMeters);
                ApplyPose();
            }

            if ((Input.GetMouseButton(1) || shift && Input.GetMouseButton(0))
                && previewCamera != null)
            {
                cameraYaw += Input.GetAxis("Mouse X") * orbitSensitivity * 12f;
                cameraPitch = Mathf.Clamp(
                    cameraPitch - Input.GetAxis("Mouse Y") * orbitSensitivity * 12f,
                    -8f,
                    82f);
                ApplyCamera();
            }

            float scroll = Input.mouseScrollDelta.y;
            if (Mathf.Abs(scroll) > 0.001f && previewCamera != null)
            {
                cameraDistance = Mathf.Clamp(
                    cameraDistance - scroll * zoomSensitivity,
                    0.055f,
                    0.45f);
                ApplyCamera();
            }

            if (Input.GetKeyDown(KeyCode.R))
            {
                ResetPose();
            }
            if (Input.GetKeyDown(KeyCode.Alpha1))
            {
                SetPose(0f, 0f);
            }
            if (Input.GetKeyDown(KeyCode.Alpha2))
            {
                SetPose(12f, maximumTravelMeters * 0.5f);
            }
            if (Input.GetKeyDown(KeyCode.Alpha3))
            {
                SetPose(36f, maximumTravelMeters);
            }
        }

        public void Configure(
            Transform carrier,
            Transform top,
            Transform slide,
            Camera camera,
            Transform target,
            Vector3 rotationAxis,
            Vector3 slideAxis)
        {
            rotatingCarrier = carrier;
            movingTop = top;
            topLocalSlide = slide;
            previewCamera = camera;
            orbitTarget = target;
            rotationAxisLocal = rotationAxis.normalized;
            slideAxisLocal = slideAxis.normalized;
            topSlideClosedPosition = slide != null ? slide.localPosition : Vector3.zero;
        }

        public void SetPose(float angle, float travel)
        {
            angleDegrees = angle;
            travelMeters = Mathf.Clamp(travel, 0f, maximumTravelMeters);
            ApplyPose();
        }

        public void ResetPose()
        {
            angleDegrees = 0f;
            travelMeters = 0f;
            ApplyPose();
        }

        private void ApplyPose()
        {
            Quaternion rotation = Quaternion.AngleAxis(
                angleDegrees,
                rotationAxisLocal);
            if (rotatingCarrier != null)
            {
                rotatingCarrier.localRotation = rotation;
            }
            if (movingTop != null)
            {
                movingTop.localRotation = rotation;
            }
            if (topLocalSlide != null)
            {
                topLocalSlide.localPosition = topSlideClosedPosition
                    + slideAxisLocal * travelMeters;
            }
        }

        private void ApplyCamera()
        {
            if (previewCamera == null)
            {
                return;
            }

            float pitchRadians = cameraPitch * Mathf.Deg2Rad;
            float yawRadians = cameraYaw * Mathf.Deg2Rad;
            Vector3 offset = new(
                Mathf.Sin(yawRadians) * Mathf.Cos(pitchRadians),
                Mathf.Sin(pitchRadians),
                Mathf.Cos(yawRadians) * Mathf.Cos(pitchRadians));
            previewCamera.transform.position = cameraTarget + offset * cameraDistance;
            previewCamera.transform.LookAt(cameraTarget);
        }
    }
}
