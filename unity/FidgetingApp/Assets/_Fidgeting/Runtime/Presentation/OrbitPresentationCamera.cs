using FidgetingApp.Product;
using FidgetingApp.DisplayCase;
using UnityEngine;
using UnityEngine.InputSystem;

namespace ThreeBladeEDC.Presentation
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class OrbitPresentationCamera : MonoBehaviour,
        IPremiumDisplayCaseCameraStateAuthor
    {
        public const float LibraryMotionOrbitMultiplier = 1.25f;
        public const float MinimumUserZoomScale = 0.72f;
        public const float MaximumUserZoomScale = 1.55f;
        [SerializeField] private Transform target;
        [SerializeField] private Transform focusTarget;
        [SerializeField] private float orbitSensitivity = 0.18f;
        [SerializeField] private float zoomSensitivity = 0.008f;
        [SerializeField] private Vector2 pitchLimits = new Vector2(3f, 89f);
        [SerializeField] private bool readDesktopInput = true;

        private float distance;
        private float heroDistance;
        private float libraryPreviewDistance;
        private float userZoomScale = 1f;
        private float appearanceActivationScale = 1f;
        private ProductFramingProfile framingProfile;
        private float _yaw = 32f;
        private float _pitch = 42f;
        private int _preset;
        private Vector2 _motionTilt;
        private float _maximumMotionOrbitDegrees = 6.5f;
        private bool _libraryPreviewActive;
        private bool _presentationTransitionActive;
        private float _presentationTransitionElapsed;
        private float _transitionStartYaw;
        private float _transitionStartPitch;
        private float _transitionStartDistance;
        private float _transitionTargetYaw;
        private float _transitionTargetPitch;
        private float _transitionTargetDistance;
        private float _presentationMotionOrbitMultiplier = 1f;
        private float _transitionStartMotionMultiplier;
        private float _transitionTargetMotionMultiplier;
        private bool displayCaseCameraControlSuppressed;

        public Transform Target
        {
            get => target;
            set
            {
                target = value;
                RefreshFramedDistances();
            }
        }

        /// <summary>
        /// Stable visible point on the mechanical axis. ThreeBladeEDC wires
        /// this to the upper finger-cap face so the point viewers perceive as
        /// the center, rather than the rotor's hidden mid-plane, occupies the
        /// center of the screen at oblique camera angles.
        /// </summary>
        public Transform FocusTarget
        {
            get => focusTarget;
            set
            {
                focusTarget = value;
                RefreshFramedDistances();
            }
        }

        public Vector3 FocusPoint => ResolveFocusPoint();

        public float Distance => distance;
        public float AppearanceActivationScale => appearanceActivationScale;

        private void Awake()
        {
            Camera cameraComponent = GetComponent<Camera>();
            cameraComponent.usePhysicalProperties = true;
            cameraComponent.focalLength = 85f;
            cameraComponent.sensorSize = new Vector2(36f, 24f);
            cameraComponent.gateFit = Camera.GateFitMode.Horizontal;
            cameraComponent.nearClipPlane = 0.01f;
            cameraComponent.farClipPlane = 10f;
            ConfigureFraming(ProductFramingCatalog.Resolve(gameObject.scene.path));
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
                float scrollDelta = mouse.scroll.ReadValue().y;
                if (!Mathf.Approximately(scrollDelta, 0f))
                {
                    SetDistance(distance - scrollDelta * zoomSensitivity * 0.01f);
                }
            }

            Keyboard keyboard = Keyboard.current;
            if (keyboard != null && keyboard.vKey.wasPressedThisFrame)
            {
                CyclePreset();
            }

            if (_presentationTransitionActive)
            {
                AdvancePresentationTransition(Time.unscaledDeltaTime);
            }
            ApplyOrbitPose();
        }

        private void ApplyOrbitPose()
        {
            if (displayCaseCameraControlSuppressed || target == null)
            {
                return;
            }

            Vector2 motionOrbit = DeviceMotionOrbitMapping.ResolveOrbitDegrees(
                _motionTilt,
                _maximumMotionOrbitDegrees * _presentationMotionOrbitMultiplier);
            Quaternion orbit = Quaternion.Euler(
                _pitch - motionOrbit.y,
                _yaw + motionOrbit.x,
                0f);
            // Never focus a rotating renderer's AABB: its center moves as an
            // asymmetric rotor turns. The optional focus target is a static,
            // visible point on the same mechanical axis (the upper cap face in
            // ThreeBladeEDC). Other products retain the mechanical root fallback.
            Vector3 focus = ResolveFocusPoint();
            Vector3 authoredBackward = Vector3.back;
            Vector3 position = focus + orbit * (
                authoredBackward * distance / appearanceActivationScale);
            transform.SetPositionAndRotation(
                position,
                DeviceMotionOrbitMapping.ResolveStableLookRotation(
                    authoredBackward,
                    orbit));
        }

        public void SetDisplayCaseCameraControlSuppressed(bool suppressed)
        {
            displayCaseCameraControlSuppressed = suppressed;
        }

        public void SetAppearanceActivationScale(float apparentScale)
        {
            appearanceActivationScale = Mathf.Clamp(apparentScale, 0.95f, 1.1f);
            ApplyOrbitPose();
        }

        public void ConfigureFraming(ProductFramingProfile profile)
        {
            framingProfile = profile;
            userZoomScale = 1f;
            RefreshFramedDistances();
            distance = _libraryPreviewActive
                ? libraryPreviewDistance
                : heroDistance;
            ApplyOrbitPose();
        }

        public void CyclePreset()
        {
            CancelPresentationTransition();
            _preset = (_preset + 1) % 3;
            userZoomScale = 1f;
            switch (_preset)
            {
                case 0:
                    _yaw = 32f;
                    _pitch = 42f;
                    distance = heroDistance;
                    break;
                case 1:
                    _yaw = 0f;
                    _pitch = 89f;
                    distance = FramedDistanceFor(
                        _yaw,
                        _pitch,
                        framingProfile.DetailWidthFraction,
                        framingProfile.DetailHeightFraction);
                    break;
                default:
                    _yaw = 0f;
                    _pitch = 3f;
                    distance = FramedDistanceFor(
                        _yaw,
                        _pitch,
                        framingProfile.DetailWidthFraction,
                        framingProfile.DetailHeightFraction);
                    break;
            }
        }

        public void ResetHero()
        {
            CancelPresentationTransition();
            _preset = 0;
            _yaw = 32f;
            _pitch = 42f;
            userZoomScale = 1f;
            RefreshFramedDistances();
            distance = heroDistance;
            ApplyOrbitPose();
        }

        /// <summary>
        /// Reapplies the current authored orbit without recalculating zoom.
        /// Editor previews and deterministic tests use the same path as
        /// LateUpdate while a rotor changes orientation.
        /// </summary>
        public void FrameNow()
        {
            ApplyOrbitPose();
        }

        public void SetLibraryPreviewActive(bool active, bool immediate = false)
        {
            if (!immediate && _libraryPreviewActive == active)
            {
                return;
            }

            _libraryPreviewActive = active;
            RefreshFramedDistances();
            float targetYaw = active ? 0f : 32f;
            float targetPitch = active ? 89f : 42f;
            float targetDistance = active ? libraryPreviewDistance : heroDistance;
            userZoomScale = 1f;

            _preset = 0;
            if (immediate)
            {
                CancelPresentationTransition();
                _yaw = targetYaw;
                _pitch = targetPitch;
                distance = targetDistance;
                ApplyOrbitPose();
                return;
            }

            // Present the rotor face nearly square to camera so it reads as a
            // vertical object hovering over the ledge. Detail mode restores
            // the authored orbit. A reversal starts from the current pose, so
            // rapid enter/back navigation cannot visibly jump.
            _transitionStartYaw = _yaw;
            _transitionStartPitch = _pitch;
            _transitionStartDistance = distance;
            _transitionTargetYaw = targetYaw;
            _transitionTargetPitch = targetPitch;
            _transitionTargetDistance = targetDistance;
            _transitionStartMotionMultiplier = _presentationMotionOrbitMultiplier;
            _transitionTargetMotionMultiplier = active
                ? LibraryMotionOrbitMultiplier
                : 1f;
            _presentationTransitionElapsed = 0f;
            _presentationTransitionActive = true;
        }

        public void SetDetailEntranceProgressForPreview(float progress)
        {
            SetLibraryPreviewActive(true, true);
            SetLibraryPreviewActive(false, false);
            _presentationTransitionElapsed =
                SpinnerPresentationTransition.DurationSeconds
                * Mathf.Clamp01(progress);
            AdvancePresentationTransition(0f);
            _presentationTransitionActive = false;
            ApplyOrbitPose();
        }

        public void ConfigureHeroDistance(float value)
        {
            CancelPresentationTransition();
            float clamped = Mathf.Max(ProductCameraFraming.MinimumDistance, value);
            heroDistance = clamped;
            libraryPreviewDistance = clamped;
            userZoomScale = 1f;
            distance = clamped;
            ApplyOrbitPose();
        }

        public void SetMotionTilt(Vector2 normalizedTilt, float maximumOrbitDegrees)
        {
            _motionTilt = normalizedTilt;
            _maximumMotionOrbitDegrees = Mathf.Clamp(maximumOrbitDegrees, 0f, 24f);
        }

        public void ResetMotionTilt()
        {
            _motionTilt = Vector2.zero;
        }

        public void OrbitByPixels(Vector2 screenDelta)
        {
            if (screenDelta.sqrMagnitude <= Mathf.Epsilon)
            {
                return;
            }

            CancelPresentationTransition();
            _yaw += screenDelta.x * orbitSensitivity;
            _pitch = Mathf.Clamp(
                _pitch - screenDelta.y * orbitSensitivity,
                pitchLimits.x,
                pitchLimits.y);
            // A single pointer owns orbit only. Reframing for every new angle
            // changes camera distance and reads as one-finger zoom. Preserve
            // the current distance here; only the two-finger pinch path may
            // call ZoomByScale and change the user's zoom level.
        }

        public void ZoomByScale(float scale)
        {
            if (scale <= Mathf.Epsilon)
            {
                return;
            }

            CancelPresentationTransition();
            userZoomScale = Mathf.Clamp(
                userZoomScale / scale,
                MinimumUserZoomScale,
                MaximumUserZoomScale);
            distance = FramedDistanceForCurrentPose() * userZoomScale;
        }

        public void SetDistance(float value)
        {
            CancelPresentationTransition();
            float baseDistance = FramedDistanceForCurrentPose();
            userZoomScale = Mathf.Clamp(
                value / Mathf.Max(ProductCameraFraming.MinimumDistance, baseDistance),
                MinimumUserZoomScale,
                MaximumUserZoomScale);
            distance = baseDistance * userZoomScale;
        }

        private void RefreshFramedDistances()
        {
            heroDistance = FramedDistanceFor(
                32f,
                42f,
                framingProfile.DetailWidthFraction,
                framingProfile.DetailHeightFraction);
            libraryPreviewDistance = FramedDistanceFor(
                0f,
                89f,
                framingProfile.LibraryWidthFraction,
                framingProfile.LibraryHeightFraction);
        }

        private float FramedDistanceForCurrentPose()
        {
            return FramedDistanceFor(
                _yaw,
                _pitch,
                _libraryPreviewActive
                    ? framingProfile.LibraryWidthFraction
                    : framingProfile.DetailWidthFraction,
                _libraryPreviewActive
                    ? framingProfile.LibraryHeightFraction
                    : framingProfile.DetailHeightFraction);
        }

        private float FramedDistanceFor(
            float yaw,
            float pitch,
            float widthFraction,
            float heightFraction)
        {
            if (target == null
                || !ProductCameraFraming.TryGetProductBounds(target, out Bounds bounds))
            {
                return Mathf.Max(ProductCameraFraming.MinimumDistance, distance);
            }

            Quaternion orbit = Quaternion.Euler(pitch, yaw, 0f);
            Vector3 framingBackward = orbit * Vector3.back;
            return ProductCameraFraming.RequiredDistance(
                GetComponent<Camera>(),
                bounds,
                framingBackward,
                widthFraction,
                heightFraction,
                focusPoint: ResolveFocusPoint());
        }

        private Vector3 ResolveFocusPoint()
        {
            if (focusTarget != null)
            {
                Renderer focusRenderer = focusTarget.GetComponent<Renderer>();
                return focusRenderer != null
                    ? focusRenderer.bounds.center
                    : focusTarget.position;
            }

            return target != null ? target.position : transform.position;
        }

        private void AdvancePresentationTransition(float deltaTime)
        {
            _presentationTransitionElapsed += Mathf.Max(0f, deltaTime);
            float progress = SpinnerPresentationTransition.ResolveProgress(
                _presentationTransitionElapsed);
            _yaw = Mathf.LerpAngle(
                _transitionStartYaw,
                _transitionTargetYaw,
                progress);
            _pitch = Mathf.LerpAngle(
                _transitionStartPitch,
                _transitionTargetPitch,
                progress);
            distance = Mathf.Lerp(
                _transitionStartDistance,
                _transitionTargetDistance,
                progress);
            _presentationMotionOrbitMultiplier = Mathf.Lerp(
                _transitionStartMotionMultiplier,
                _transitionTargetMotionMultiplier,
                progress);

            if (progress >= 1f)
            {
                _yaw = _transitionTargetYaw;
                _pitch = _transitionTargetPitch;
                distance = _transitionTargetDistance;
                _presentationMotionOrbitMultiplier = _transitionTargetMotionMultiplier;
                _presentationTransitionActive = false;
            }
        }

        private void CancelPresentationTransition()
        {
            _presentationTransitionActive = false;
            _presentationMotionOrbitMultiplier = _libraryPreviewActive
                ? LibraryMotionOrbitMultiplier
                : 1f;
        }

        public void SetDesktopInputEnabled(bool enabled)
        {
            readDesktopInput = enabled;
        }
    }
}
