using FidgetingApp.Product;
using UnityEngine;

namespace FidgetingApp.EDC
{
    [ExecuteAlways]
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class EdcPortraitCameraFramer : MonoBehaviour
    {
        public const float LibraryMotionOrbitMultiplier = 1.25f;
        public const float DefaultScreenWidthFraction =
            ProductFramingCatalog.ElongatedDetailWidthFraction;
        public const float DefaultScreenHeightFraction =
            ProductFramingCatalog.ElongatedDetailHeightFraction;
        public const float DefaultFocalLengthMillimeters = 50f;
        public static readonly Vector2 DefaultSensorSizeMillimeters = new(36f, 24f);
        public static readonly Vector3 DefaultDetailFramingBackward =
            new(0f, 0.5f, -0.8660254f);
        // The detail pose is an authored fixed camera, so a boundary-fraction
        // library pose scaled with the phone aspect while detail did not; on a
        // 19.5:9 phone the closed tile read ~1.7x larger in the library
        // (user 2026-09-08: "在列表场景的时候，它的尺寸过大了"). Library now keeps
        // the authored magnification and only steps back by the catalog's
        // library/detail ratio, like the circular rotors.
        public const float LibraryDistanceScale =
            ProductFramingCatalog.CircularDetailFraction
            / ProductFramingCatalog.CircularLibraryFraction;
        public const float LibrarySafetyFraction = 0.90f;

        [SerializeField] private Transform target;
        [SerializeField] private Transform focusTarget;
        [SerializeField] private bool useStableLocalBounds;
        [SerializeField] private Bounds stableLocalBounds;
        [SerializeField, Range(0.30f, 0.90f)]
        private float screenWidthFraction = DefaultScreenWidthFraction;
        [SerializeField, Range(0.30f, 0.90f)]
        private float screenHeightFraction = DefaultScreenHeightFraction;
        [SerializeField, Min(0.01f)]
        private float minimumDistance = 0.08f;
        [SerializeField, Min(0f)]
        private float distancePadding = 0.004f;
        [SerializeField, Min(0.01f)] private float orbitSensitivity = 0.16f;
        [SerializeField] private Vector2 yawLimits = new(-55f, 55f);
        [SerializeField] private Vector2 pitchLimits = new(-28f, 34f);
        [SerializeField] private Vector2 zoomLimits = new(0.62f, 1.85f);
        [SerializeField, Min(0.1f)] private float viewResponse = 10f;
        [SerializeField] private bool usePhysicalProjection = true;
        [SerializeField, Range(5f, 120f)]
        private float standardFieldOfView = 26.991f;
        [SerializeField, Range(-60f, 60f)] private float libraryRollDegrees;
        [SerializeField] private bool preserveAuthoredDefaultPose;
        [SerializeField] private Vector3 authoredDefaultCameraPosition;
        [SerializeField] private Quaternion authoredDefaultCameraRotation =
            Quaternion.identity;
        [SerializeField] private Vector3 authoredDefaultFocusPoint;

        private Camera targetCamera;
        private Vector3 framingBackward;
        private Vector3 defaultFramingBackward;
        private bool hasFramingDirection;
        private bool hasDefaultFramingDirection;
        private int previousScreenWidth;
        private int previousScreenHeight;
        private float yawOffset;
        private float pitchOffset;
        private float zoomScale = 1f;
        private float targetZoomScale = 1f;
        private float appearanceActivationScale = 1f;
        private Vector2 motionTilt;
        private float maximumMotionOrbitDegrees = 6.5f;
        private bool libraryPreviewActive;
        private bool presentationTransitionActive;
        private float presentationTransitionElapsed;
        private Vector3 transitionStartBackward;
        private Vector3 transitionTargetBackward;
        private float transitionStartYaw;
        private float transitionTargetYaw;
        private float transitionStartPitch;
        private float transitionTargetPitch;
        private float framingRollDegrees;
        private float transitionStartRoll;
        private float transitionTargetRoll;
        private float transitionStartZoom;
        private float transitionTargetZoom;
        private float presentationMotionOrbitMultiplier = 1f;
        private float transitionStartMotionMultiplier;
        private float transitionTargetMotionMultiplier;
        private ProductFramingProfile framingProfile;
        private float transitionStartWidthFraction;
        private float transitionTargetWidthFraction;
        private float transitionStartHeightFraction;
        private float transitionTargetHeightFraction;
        private float transitionStartDistance;
        private float transitionTargetDistance;
        private float transitionProgress;

        public Transform Target => target;
        public float AuthoredDefaultDistance => Vector3.Distance(
            authoredDefaultCameraPosition,
            authoredDefaultFocusPoint);
        public Transform FocusTarget => focusTarget;
        public float ScreenWidthFraction => screenWidthFraction;
        public float ScreenHeightFraction => screenHeightFraction;
        public float FramedDistance { get; private set; }
        public float ZoomScale => zoomScale;
        public float TargetZoomScale => targetZoomScale;
        public float YawOffset => yawOffset;
        public float PitchOffset => pitchOffset;
        public int ZoomUpdateCount { get; private set; }
        public int OrbitUpdateCount { get; private set; }
        public float AppearanceActivationScale => appearanceActivationScale;
        public bool UsesPhysicalProjection => usePhysicalProjection;
        public bool UsesStableLocalBounds => useStableLocalBounds;
        public bool PreservesAuthoredDefaultPose =>
            preserveAuthoredDefaultPose;
        public Bounds StableLocalBounds => stableLocalBounds;
        public float LibraryRollDegrees => libraryRollDegrees;
        public float FramingRollDegrees => framingRollDegrees;

        private void OnEnable()
        {
            targetCamera = GetComponent<Camera>();
            ConfigureCameraProjection(targetCamera);
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
            else
            {
                float blend = 1f - Mathf.Exp(-Time.unscaledDeltaTime * viewResponse);
                zoomScale = Mathf.Lerp(zoomScale, targetZoomScale, blend);
            }
            ApplyViewPose();
        }

        public void Configure(Transform newTarget)
        {
            CancelPresentationTransition();
            target = newTarget;
            preserveAuthoredDefaultPose = false;
            hasFramingDirection = false;
            FrameNow();
        }

        public void ConfigureAuthoredRuntimeTarget(
            Transform newTarget,
            Bounds localBounds,
            Vector3 focusPoint)
        {
            CancelPresentationTransition();
            target = newTarget;
            focusTarget = null;
            useStableLocalBounds =
                localBounds.size.sqrMagnitude > 0.000001f;
            stableLocalBounds = localBounds;
            preserveAuthoredDefaultPose = true;
            authoredDefaultCameraPosition = transform.position;
            authoredDefaultCameraRotation = transform.rotation;
            authoredDefaultFocusPoint = focusPoint;
            ApplyAuthoredDefaultPose();
        }

        public void ConfigureFocusTarget(Transform newFocusTarget)
        {
            focusTarget = newFocusTarget;
            FrameNow();
        }

        public void ConfigureStableLocalBounds(Bounds localBounds)
        {
            useStableLocalBounds = localBounds.size.sqrMagnitude > 0.000001f;
            stableLocalBounds = localBounds;
            FrameNow();
        }

        public void ConfigureProjection(
            bool usePhysical,
            float fieldOfViewDegrees = 26.991f)
        {
            usePhysicalProjection = usePhysical;
            standardFieldOfView = Mathf.Clamp(fieldOfViewDegrees, 5f, 120f);
            if (targetCamera == null)
            {
                targetCamera = GetComponent<Camera>();
            }
            ConfigureCameraProjection(targetCamera);
            FrameNow();
        }

        public void ConfigureFraming(ProductFramingProfile profile)
        {
            framingProfile = profile;
            screenWidthFraction = libraryPreviewActive
                ? profile.LibraryWidthFraction
                : profile.DetailWidthFraction;
            screenHeightFraction = libraryPreviewActive
                ? profile.LibraryHeightFraction
                : profile.DetailHeightFraction;
            if (preserveAuthoredDefaultPose && !libraryPreviewActive)
            {
                ApplyAuthoredDefaultPose();
                return;
            }
            FrameNow();
        }

        public void ConfigureLibraryPresentation(float rollDegrees)
        {
            libraryRollDegrees = Mathf.Clamp(rollDegrees, -60f, 60f);
            if (libraryPreviewActive)
            {
                framingRollDegrees = libraryRollDegrees;
            }
            FrameNow();
        }

        public void OrbitByPixels(Vector2 screenDelta)
        {
            if (screenDelta.sqrMagnitude <= Mathf.Epsilon)
            {
                return;
            }

            CancelPresentationTransition();
            yawOffset = Mathf.Clamp(
                yawOffset + screenDelta.x * orbitSensitivity,
                yawLimits.x,
                yawLimits.y);
            pitchOffset = Mathf.Clamp(
                pitchOffset - screenDelta.y * orbitSensitivity,
                pitchLimits.x,
                pitchLimits.y);
            OrbitUpdateCount++;
            Debug.Log(
                "[MagneticSlideRuntime] orbit-update "
                + $"yaw={yawOffset:F2} pitch={pitchOffset:F2}");
            ApplyViewPose();
        }

        public void ZoomByScale(float scale)
        {
            if (scale <= Mathf.Epsilon)
            {
                return;
            }
            CancelPresentationTransition();
            targetZoomScale = Mathf.Clamp(
                targetZoomScale / scale,
                zoomLimits.x,
                zoomLimits.y);
            ZoomUpdateCount++;
            Debug.Log(
                "[MagneticSlideRuntime] zoom-update "
                + $"scale={scale:F4} target={targetZoomScale:F3}");
        }

        public void ResetInteractiveView()
        {
            CancelPresentationTransition();
            yawOffset = 0f;
            pitchOffset = 0f;
            zoomScale = 1f;
            targetZoomScale = 1f;
            if (preserveAuthoredDefaultPose && !libraryPreviewActive)
            {
                ApplyAuthoredDefaultPose();
                return;
            }
            ApplyViewPose();
        }

        public void SetMotionTilt(
            Vector2 normalizedTilt,
            float maximumOrbitDegrees)
        {
            motionTilt = normalizedTilt;
            maximumMotionOrbitDegrees = Mathf.Clamp(maximumOrbitDegrees, 0f, 24f);
            ApplyViewPose();
        }

        public void ResetMotionTilt()
        {
            motionTilt = Vector2.zero;
            ApplyViewPose();
        }

        public void SetAppearanceActivationScale(float apparentScale)
        {
            appearanceActivationScale = Mathf.Clamp(apparentScale, 0.95f, 1.1f);
            ApplyViewPose();
        }

        public void SetLibraryPreviewActive(bool active, bool immediate = false)
        {
            if (!hasDefaultFramingDirection)
            {
                FrameNow();
            }

            if (!hasDefaultFramingDirection
                || (!immediate && libraryPreviewActive == active))
            {
                return;
            }

            libraryPreviewActive = active;
            Vector3 targetBackward = active
                ? new Vector3(0f, 1f, -0.02f).normalized
                : defaultFramingBackward;
            float targetZoom = 1f;
            float targetWidthFraction = active
                ? framingProfile.LibraryWidthFraction
                : framingProfile.DetailWidthFraction;
            float targetHeightFraction = active
                ? framingProfile.LibraryHeightFraction
                : framingProfile.DetailHeightFraction;
            float targetRoll = active ? libraryRollDegrees : 0f;

            if (immediate)
            {
                CancelPresentationTransition();
                framingBackward = targetBackward;
                yawOffset = 0f;
                pitchOffset = 0f;
                zoomScale = targetZoom;
                targetZoomScale = targetZoom;
                screenWidthFraction = targetWidthFraction;
                screenHeightFraction = targetHeightFraction;
                framingRollDegrees = targetRoll;
                hasFramingDirection = true;
                FrameNow();
                return;
            }

            transitionStartBackward = framingBackward;
            transitionTargetBackward = targetBackward;
            transitionStartYaw = yawOffset;
            transitionTargetYaw = 0f;
            transitionStartPitch = pitchOffset;
            transitionTargetPitch = 0f;
            transitionStartRoll = framingRollDegrees;
            transitionTargetRoll = targetRoll;
            transitionStartZoom = zoomScale;
            transitionTargetZoom = targetZoom;
            transitionStartWidthFraction = screenWidthFraction;
            transitionTargetWidthFraction = targetWidthFraction;
            transitionStartHeightFraction = screenHeightFraction;
            transitionTargetHeightFraction = targetHeightFraction;
            transitionStartMotionMultiplier = presentationMotionOrbitMultiplier;
            transitionTargetMotionMultiplier = active
                ? LibraryMotionOrbitMultiplier
                : 1f;
            transitionStartDistance = FramedDistance;
            transitionTargetDistance = ResolveAuthoredPoseDistance(
                active,
                targetBackward,
                targetRoll);
            transitionProgress = 0f;
            presentationTransitionElapsed = 0f;
            presentationTransitionActive = true;
            hasFramingDirection = true;
        }

        /// <summary>
        /// Distance for a pose when the detail camera is authored. Library keeps
        /// the authored magnification (stepped back by
        /// <see cref="LibraryDistanceScale"/>) and never lets the closed tile
        /// exceed <see cref="LibrarySafetyFraction"/> of the viewport.
        /// </summary>
        public float ResolveAuthoredPoseDistance(
            bool libraryPose,
            Vector3 poseBackward,
            float rollDegrees)
        {
            float authored = AuthoredDefaultDistance;
            if (!libraryPose)
            {
                return authored;
            }

            float matched = authored * LibraryDistanceScale;
            if (targetCamera == null)
            {
                targetCamera = GetComponent<Camera>();
            }
            if (targetCamera == null || !TryGetFramingBounds(out Bounds bounds))
            {
                return matched;
            }

            float safety = ProductCameraFraming.RequiredDistance(
                targetCamera,
                bounds,
                poseBackward,
                LibrarySafetyFraction,
                LibrarySafetyFraction,
                minimumDistance,
                distancePadding,
                null,
                rollDegrees);
            return Mathf.Max(matched, safety);
        }

        public void SetDetailEntranceProgressForPreview(float progress)
        {
            SetLibraryPreviewActive(true, true);
            SetLibraryPreviewActive(false, false);
            presentationTransitionElapsed =
                SpinnerPresentationTransition.DurationSeconds
                * Mathf.Clamp01(progress);
            AdvancePresentationTransition(0f);
            presentationTransitionActive = false;
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
            yawOffset = Mathf.LerpAngle(
                transitionStartYaw,
                transitionTargetYaw,
                progress);
            pitchOffset = Mathf.LerpAngle(
                transitionStartPitch,
                transitionTargetPitch,
                progress);
            framingRollDegrees = Mathf.LerpAngle(
                transitionStartRoll,
                transitionTargetRoll,
                progress);
            zoomScale = Mathf.Lerp(
                transitionStartZoom,
                transitionTargetZoom,
                progress);
            targetZoomScale = zoomScale;
            screenWidthFraction = Mathf.Lerp(
                transitionStartWidthFraction,
                transitionTargetWidthFraction,
                progress);
            screenHeightFraction = Mathf.Lerp(
                transitionStartHeightFraction,
                transitionTargetHeightFraction,
                progress);
            presentationMotionOrbitMultiplier = Mathf.Lerp(
                transitionStartMotionMultiplier,
                transitionTargetMotionMultiplier,
                progress);
            transitionProgress = progress;

            if (progress >= 1f)
            {
                framingBackward = transitionTargetBackward;
                yawOffset = transitionTargetYaw;
                pitchOffset = transitionTargetPitch;
                zoomScale = transitionTargetZoom;
                targetZoomScale = transitionTargetZoom;
                framingRollDegrees = transitionTargetRoll;
                screenWidthFraction = transitionTargetWidthFraction;
                screenHeightFraction = transitionTargetHeightFraction;
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

        public void FrameNow()
        {
            if (target == null || !TryGetFramingBounds(out Bounds bounds))
            {
                return;
            }

            if (preserveAuthoredDefaultPose
                && !libraryPreviewActive
                && !presentationTransitionActive
                && Mathf.Abs(yawOffset) <= 0.0001f
                && Mathf.Abs(pitchOffset) <= 0.0001f
                && Mathf.Abs(targetZoomScale - 1f) <= 0.0001f)
            {
                ApplyAuthoredDefaultPose();
                return;
            }

            if (targetCamera == null)
            {
                targetCamera = GetComponent<Camera>();
            }
            ConfigureCameraProjection(targetCamera);

            if (!hasFramingDirection)
            {
                // Detail view is deliberately front-aligned so the slide axis
                // maps to screen X without diagonal perspective compression.
                // The 30-degree elevation keeps the top controls visible.
                framingBackward = DefaultDetailFramingBackward.normalized;
                hasFramingDirection = true;
            }

            if (!hasDefaultFramingDirection)
            {
                defaultFramingBackward = framingBackward;
                hasDefaultFramingDirection = true;
            }

            FramedDistance = ProductCameraFraming.RequiredDistance(
                targetCamera,
                bounds,
                framingBackward,
                screenWidthFraction,
                screenHeightFraction,
                minimumDistance,
                distancePadding,
                null,
                framingRollDegrees);
            if (preserveAuthoredDefaultPose)
            {
                if (presentationTransitionActive)
                {
                    FramedDistance = Mathf.Lerp(
                        transitionStartDistance,
                        transitionTargetDistance,
                        transitionProgress);
                }
                else if (libraryPreviewActive)
                {
                    FramedDistance = ResolveAuthoredPoseDistance(
                        true,
                        framingBackward,
                        framingRollDegrees);
                }
            }
            previousScreenWidth = Screen.width;
            previousScreenHeight = Screen.height;
            ApplyViewPose();
        }

        private void ApplyViewPose()
        {
            if (target == null || FramedDistance <= 0f)
            {
                return;
            }

            if (!TryGetFramingBounds(out Bounds bounds))
            {
                return;
            }

            Vector2 motionOrbit = DeviceMotionOrbitMapping.ResolveOrbitDegrees(
                motionTilt,
                maximumMotionOrbitDegrees * presentationMotionOrbitMultiplier);
            Quaternion orbit = Quaternion.Euler(
                pitchOffset - motionOrbit.y,
                yawOffset + motionOrbit.x,
                0f);
            Vector3 backward = orbit * framingBackward;
            Vector3 focus = preserveAuthoredDefaultPose
                    && !libraryPreviewActive
                ? authoredDefaultFocusPoint
                : bounds.center;
            Vector3 position = focus
                + backward * (
                    FramedDistance
                    * Mathf.Max(0.01f, zoomScale)
                    / appearanceActivationScale);
            Quaternion look =
                DeviceMotionOrbitMapping.ResolveStableLookRotation(
                    framingBackward,
                    orbit);
            transform.SetPositionAndRotation(
                position,
                look * Quaternion.AngleAxis(
                    framingRollDegrees,
                    Vector3.forward));
        }

        private void ApplyAuthoredDefaultPose()
        {
            if (!preserveAuthoredDefaultPose)
                return;
            if (targetCamera == null)
                targetCamera = GetComponent<Camera>();
            framingBackward =
                authoredDefaultCameraRotation * Vector3.back;
            defaultFramingBackward = framingBackward;
            hasFramingDirection = true;
            hasDefaultFramingDirection = true;
            FramedDistance = Vector3.Distance(
                authoredDefaultCameraPosition,
                authoredDefaultFocusPoint);
            zoomScale = 1f;
            targetZoomScale = 1f;
            previousScreenWidth = Screen.width;
            previousScreenHeight = Screen.height;
            transform.SetPositionAndRotation(
                authoredDefaultCameraPosition,
                authoredDefaultCameraRotation);
        }

        private void ConfigureCameraProjection(Camera camera)
        {
            if (camera == null)
            {
                return;
            }

            camera.usePhysicalProperties = usePhysicalProjection;
            if (usePhysicalProjection)
            {
                camera.sensorSize = DefaultSensorSizeMillimeters;
                camera.focalLength = DefaultFocalLengthMillimeters;
                camera.gateFit = Camera.GateFitMode.Horizontal;
            }
            else
            {
                camera.fieldOfView = standardFieldOfView;
                camera.ResetProjectionMatrix();
            }
        }

        private bool TryGetFramingBounds(out Bounds bounds)
        {
            // Detail interaction uses the complete mechanism sweep so the
            // camera never chases moving layers. Library preview is static;
            // there the visible closed product itself must define the center,
            // rather than the corner pivot or an asymmetric sweep envelope.
            if (useStableLocalBounds && !libraryPreviewActive && target != null)
            {
                Vector3 localExtents = stableLocalBounds.extents;
                Vector3 worldCenter = focusTarget != null
                    ? focusTarget.position
                    : target.TransformPoint(stableLocalBounds.center);
                Vector3 worldX = target.TransformVector(
                    new Vector3(localExtents.x, 0f, 0f));
                Vector3 worldY = target.TransformVector(
                    new Vector3(0f, localExtents.y, 0f));
                Vector3 worldZ = target.TransformVector(
                    new Vector3(0f, 0f, localExtents.z));
                Vector3 worldExtents = new(
                    Mathf.Abs(worldX.x) + Mathf.Abs(worldY.x) + Mathf.Abs(worldZ.x),
                    Mathf.Abs(worldX.y) + Mathf.Abs(worldY.y) + Mathf.Abs(worldZ.y),
                    Mathf.Abs(worldX.z) + Mathf.Abs(worldY.z) + Mathf.Abs(worldZ.z));
                bounds = new Bounds(worldCenter, worldExtents * 2f);
                return true;
            }
            return ProductCameraFraming.TryGetProductBounds(target, out bounds);
        }
    }
}
