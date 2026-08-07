using System.Globalization;
using FidgetingApp.Product;
using UnityEngine;

namespace CodexUnityLab
{
    [ExecuteAlways]
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class PortraitCameraFramer : MonoBehaviour
    {
        public const float LibraryMotionOrbitMultiplier = 1.25f;
        [SerializeField] private Transform target;

        [Header("Interactive Zoom")]
        [SerializeField, Min(0.1f)] private float minimumZoomScale = 0.58f;
        [SerializeField, Min(0.1f)] private float maximumZoomScale = 2f;
        [SerializeField, Min(0.0001f)] private float pinchZoomSensitivity = 0.004f;
        [SerializeField, Min(0f)] private float zoomSmoothingTime = 0.06f;

        [Header("Device Motion")]
        [SerializeField, Range(0f, 24f)] private float maximumMotionOrbitDegrees = 6.5f;

        private Camera targetCamera;
        private int previousScreenWidth;
        private int previousScreenHeight;
        private Vector3 framedFocus;
        private Vector3 framingBackward;
        private Vector3 defaultFramingBackward;
        private float framedDistance;
        private float zoomScale = 1f;
        private float targetZoomScale = 1f;
        private float appearanceActivationScale = 1f;
        private Vector2 motionTilt;
        private bool hasFrame;
        private bool hasFramingDirection;
        private bool hasDefaultFramingDirection;
        private bool libraryPreviewActive;
        private bool presentationTransitionActive;
        private float presentationTransitionElapsed;
        private Vector3 transitionStartBackward;
        private Vector3 transitionTargetBackward;
        private float transitionStartZoom;
        private float transitionTargetZoom;
        private float presentationMotionOrbitMultiplier = 1f;
        private float transitionStartMotionMultiplier;
        private float transitionTargetMotionMultiplier;
        private ProductFramingProfile framingProfile;
        private float presentationWidthFraction;
        private float presentationHeightFraction;
        private float transitionStartWidthFraction;
        private float transitionTargetWidthFraction;
        private float transitionStartHeightFraction;
        private float transitionTargetHeightFraction;

        public float ZoomScale => zoomScale;
        public float AppearanceActivationScale => appearanceActivationScale;
        public float MaximumMotionOrbitDegrees => maximumMotionOrbitDegrees;
        public Transform Target => target;

        private void OnEnable()
        {
            targetCamera = GetComponent<Camera>();
            ConfigureFraming(ProductFramingCatalog.Resolve(gameObject.scene.path));
            FrameNow();
        }

        private void Start()
        {
            FrameNow();
        }

        private void LateUpdate()
        {
            if (Screen.width != previousScreenWidth || Screen.height != previousScreenHeight)
            {
                FrameNow();
            }

            if (presentationTransitionActive)
            {
                AdvancePresentationTransition(Time.unscaledDeltaTime);
            }
            else if (!Mathf.Approximately(zoomScale, targetZoomScale))
            {
                float blend = zoomSmoothingTime <= 0f
                    ? 1f
                    : 1f - Mathf.Exp(-Time.unscaledDeltaTime / zoomSmoothingTime);
                zoomScale = Mathf.Lerp(zoomScale, targetZoomScale, blend);

                if (Mathf.Abs(zoomScale - targetZoomScale) < 0.0001f)
                {
                    zoomScale = targetZoomScale;
                }

                ApplyViewPose();
            }
        }

        public void SetTarget(Transform newTarget)
        {
            CancelPresentationTransition();
            target = newTarget;
            hasFramingDirection = false;
            FrameNow();
        }

        public void ConfigureFraming(ProductFramingProfile profile)
        {
            framingProfile = profile;
            presentationWidthFraction = libraryPreviewActive
                ? profile.LibraryWidthFraction
                : profile.DetailWidthFraction;
            presentationHeightFraction = libraryPreviewActive
                ? profile.LibraryHeightFraction
                : profile.DetailHeightFraction;
            FrameNow();
        }

        public void ApplyPinchDelta(float pinchDeltaPixels)
        {
            if (Mathf.Approximately(pinchDeltaPixels, 0f))
            {
                return;
            }

            CancelPresentationTransition();
            float multiplier = Mathf.Exp(-pinchDeltaPixels * pinchZoomSensitivity);
            targetZoomScale = ClampZoomScale(targetZoomScale * multiplier);
        }

        public void SetZoomScale(float newZoomScale)
        {
            CancelPresentationTransition();
            zoomScale = ClampZoomScale(newZoomScale);
            targetZoomScale = zoomScale;
            ApplyViewPose();
        }

        public void SetMotionTilt(Vector2 normalizedTilt)
        {
            motionTilt = normalizedTilt;
            ApplyViewPose();
        }

        public void SetAppearanceActivationScale(float apparentScale)
        {
            appearanceActivationScale = Mathf.Clamp(apparentScale, 0.95f, 1.1f);
            ApplyViewPose();
        }

        public void SetMaximumMotionOrbitDegreesFromNativeUi(string value)
        {
            if (!float.TryParse(
                    value,
                    NumberStyles.Float,
                    CultureInfo.InvariantCulture,
                    out float parsedValue))
            {
                return;
            }

            maximumMotionOrbitDegrees = Mathf.Clamp(parsedValue, 0f, 24f);
            ApplyViewPose();
        }

        public void ResetInteractiveView()
        {
            CancelPresentationTransition();
            zoomScale = 1f;
            targetZoomScale = 1f;
            motionTilt = Vector2.zero;
            ApplyViewPose();
        }

        private float ClampZoomScale(float value)
        {
            float lower = Mathf.Min(minimumZoomScale, maximumZoomScale);
            float upper = Mathf.Max(minimumZoomScale, maximumZoomScale);
            return Mathf.Clamp(value, lower, upper);
        }

        public void FrameNow()
        {
            if (target == null)
            {
                return;
            }

            if (targetCamera == null)
            {
                targetCamera = GetComponent<Camera>();
            }

            if (!ProductCameraFraming.TryGetProductBounds(target, out Bounds bounds))
            {
                return;
            }

            framedFocus = bounds.center;
            if (!hasFramingDirection)
            {
                framingBackward = transform.position - framedFocus;
                if (framingBackward.sqrMagnitude < 0.0001f)
                {
                    framingBackward = new Vector3(0f, 1f, -1f);
                }

                framingBackward.Normalize();
                hasFramingDirection = true;
            }

            if (!hasDefaultFramingDirection)
            {
                defaultFramingBackward = framingBackward;
                hasDefaultFramingDirection = true;
            }

            framedDistance = ProductCameraFraming.RequiredDistance(
                targetCamera,
                bounds,
                framingBackward,
                presentationWidthFraction,
                presentationHeightFraction);
            hasFrame = true;
            previousScreenWidth = Screen.width;
            previousScreenHeight = Screen.height;
            ApplyViewPose();
        }

        public void SetLibraryPreviewActive(bool active, bool immediate = false)
        {
            if (!hasDefaultFramingDirection)
            {
                FrameNow();
                if (!hasDefaultFramingDirection)
                {
                    return;
                }
            }

            if (!immediate && libraryPreviewActive == active)
            {
                return;
            }

            libraryPreviewActive = active;
            Vector3 targetBackward = active
                // A near-axis presentation makes the spinner read as a
                // vertical 90-degree hero above the photographed ledge. This
                // is camera-only: the rotor's physics transform stays intact.
                ? new Vector3(0f, 1f, -0.02f).normalized
                : defaultFramingBackward;
            float targetZoom = 1f;
            float targetWidthFraction = active
                ? framingProfile.LibraryWidthFraction
                : framingProfile.DetailWidthFraction;
            float targetHeightFraction = active
                ? framingProfile.LibraryHeightFraction
                : framingProfile.DetailHeightFraction;

            if (immediate)
            {
                CancelPresentationTransition();
                framingBackward = targetBackward;
                zoomScale = targetZoom;
                targetZoomScale = targetZoom;
                presentationWidthFraction = targetWidthFraction;
                presentationHeightFraction = targetHeightFraction;
                hasFramingDirection = true;
                FrameNow();
                return;
            }

            transitionStartBackward = framingBackward;
            transitionTargetBackward = targetBackward;
            transitionStartZoom = zoomScale;
            transitionTargetZoom = targetZoom;
            transitionStartWidthFraction = presentationWidthFraction;
            transitionTargetWidthFraction = targetWidthFraction;
            transitionStartHeightFraction = presentationHeightFraction;
            transitionTargetHeightFraction = targetHeightFraction;
            transitionStartMotionMultiplier = presentationMotionOrbitMultiplier;
            transitionTargetMotionMultiplier = active
                ? LibraryMotionOrbitMultiplier
                : 1f;
            presentationTransitionElapsed = 0f;
            presentationTransitionActive = true;
            hasFramingDirection = true;
        }

        private void AdvancePresentationTransition(float deltaTime)
        {
            presentationTransitionElapsed += Mathf.Max(0f, deltaTime);
            float progress = SpinnerPresentationTransition.ResolveProgress(
                presentationTransitionElapsed);
            framingBackward = Vector3.Slerp(
                transitionStartBackward,
                transitionTargetBackward,
                progress).normalized;
            zoomScale = Mathf.Lerp(
                transitionStartZoom,
                transitionTargetZoom,
                progress);
            targetZoomScale = zoomScale;
            presentationWidthFraction = Mathf.Lerp(
                transitionStartWidthFraction,
                transitionTargetWidthFraction,
                progress);
            presentationHeightFraction = Mathf.Lerp(
                transitionStartHeightFraction,
                transitionTargetHeightFraction,
                progress);
            presentationMotionOrbitMultiplier = Mathf.Lerp(
                transitionStartMotionMultiplier,
                transitionTargetMotionMultiplier,
                progress);

            if (progress >= 1f)
            {
                framingBackward = transitionTargetBackward;
                zoomScale = transitionTargetZoom;
                targetZoomScale = transitionTargetZoom;
                presentationWidthFraction = transitionTargetWidthFraction;
                presentationHeightFraction = transitionTargetHeightFraction;
                presentationMotionOrbitMultiplier = transitionTargetMotionMultiplier;
                presentationTransitionActive = false;
            }

            FrameNow();
        }

        private void CancelPresentationTransition()
        {
            presentationTransitionActive = false;
            presentationMotionOrbitMultiplier = libraryPreviewActive
                ? LibraryMotionOrbitMultiplier
                : 1f;
        }

        private void ApplyViewPose()
        {
            if (!hasFrame)
            {
                return;
            }

            Vector2 motionOrbit = DeviceMotionOrbitMapping.ResolveOrbitDegrees(
                motionTilt,
                maximumMotionOrbitDegrees * presentationMotionOrbitMultiplier);
            Quaternion orbit = Quaternion.Euler(
                -motionOrbit.y,
                motionOrbit.x,
                0f);
            Vector3 cameraOffset = orbit * (
                framingBackward
                * framedDistance
                * zoomScale
                / appearanceActivationScale);
            Vector3 cameraPosition = framedFocus + cameraOffset;
            Vector3 lookDirection = framedFocus - cameraPosition;
            Quaternion cameraRotation = Quaternion.LookRotation(lookDirection.normalized, Vector3.up);
            transform.SetPositionAndRotation(cameraPosition, cameraRotation);
        }
    }
}
