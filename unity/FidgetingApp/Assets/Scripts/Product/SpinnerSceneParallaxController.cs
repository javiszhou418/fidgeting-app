using CodexUnityLab;
using UnityEngine;
using UnityEngine.InputSystem;

namespace FidgetingApp.Product
{
    /// <summary>
    /// Applies one coherent visual parallax response across six depth layers.
    /// The camera projection moves the real model and grounding stage together,
    /// while camera-attached image layers compensate to their requested screen
    /// travel. It consumes the existing motion-controller output and never
    /// changes rotor physics or Haptics.
    /// </summary>
    [DefaultExecutionOrder(1000)]
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class SpinnerSceneParallaxController : MonoBehaviour
    {
        public const float DeepStarLayerPixels = 2f;
        public const float StarLayerPixels = 4f;
        public const float FarLayerPixels = 8f;
        public const float MidLayerPixels = 14f;
        public const float AnchorLayerPixels = 14f;
        public const float LibraryAnchorLayerPixels = 20f;
        public const float ForegroundPixels = AnchorLayerPixels;
        public const float RightForegroundPixels = 22f;
        public const float LeftForegroundPixels = 30f;
        public const float ParallaxFullScaleAngle = 15f;
        public const float VerticalMotionScale = 0.60f;
        public const float DefaultResponse = 6.32f;
        public const float DefaultDeadZone = 0.045f;
        public const float LibraryHoverBasePixels = 3.5f;
        public const float LibraryHoverAmplitudePixels = 2.5f;
        public const float LibraryHoverCyclesPerSecond = 0.42f;
        public const float LibraryPageTravelViewport = 1.08f;
        public const float LibraryPageTransitionResponse = 13.5f;
        private const float AccessibilityRefreshInterval = 1f;

        private Camera targetCamera;
        private SpinnerEnvironmentPresenter environmentPresenter;
        private SpinnerImageBasedLightingController imageBasedLighting;
        private Vector2 filteredTilt;
        private bool configured;
        private bool reduceMotionEnabled;
        private float nextAccessibilityRefresh;
        private Matrix4x4 baselineProjection;
        private float baselineAspect;
        private bool hasBaselineProjection;
        private bool libraryPreviewActive;
        private float libraryPageOffset;
        private float targetLibraryPageOffset;

        public Vector2 FilteredTilt => filteredTilt;
        public float LibraryPageOffset => libraryPageOffset;

        public void Configure(SpinnerEnvironmentPresenter presenter)
        {
            Configure(presenter, null);
        }

        public void Configure(
            SpinnerEnvironmentPresenter presenter,
            SpinnerImageBasedLightingController lighting)
        {
            targetCamera = GetComponent<Camera>();
            environmentPresenter = presenter;
            imageBasedLighting = lighting;
            filteredTilt = Vector2.zero;
            configured = presenter != null;
            baselineProjection = targetCamera.projectionMatrix;
            baselineAspect = targetCamera.aspect;
            hasBaselineProjection = true;
            RefreshAccessibilitySetting(true);
            SceneParallaxInput.Reset();
            ResetPresentation();
        }

        private void LateUpdate()
        {
            if (!configured || targetCamera == null || environmentPresenter == null)
            {
                return;
            }

            RefreshAccessibilitySetting(false);
            Vector2 targetTilt = reduceMotionEnabled
                ? Vector2.zero
                : ResolveTargetTilt();
            targetTilt = SceneParallaxInput.ApplyRadialDeadZone(
                targetTilt,
                DefaultDeadZone);
            filteredTilt = SceneParallaxInput.Smooth(
                filteredTilt,
                targetTilt,
                DefaultResponse,
                Time.unscaledDeltaTime);

            float pageBlend = 1f - Mathf.Exp(
                -LibraryPageTransitionResponse * Time.unscaledDeltaTime);
            libraryPageOffset = Mathf.Lerp(
                libraryPageOffset,
                targetLibraryPageOffset,
                pageBlend);
            if (Mathf.Abs(libraryPageOffset - targetLibraryPageOffset) < 0.001f)
            {
                libraryPageOffset = targetLibraryPageOffset;
            }

            float hoverPixels = ResolveLibraryHoverPixels(
                Time.unscaledTime,
                libraryPreviewActive,
                reduceMotionEnabled);
            float hoverNormalized = ResolveLibraryHoverNormalized(
                Time.unscaledTime,
                libraryPreviewActive,
                reduceMotionEnabled);
            float anchorPixels = libraryPreviewActive
                ? LibraryAnchorLayerPixels
                : AnchorLayerPixels;
            ApplyProjectionOffset(filteredTilt, anchorPixels, hoverPixels);
            environmentPresenter.SetLayeredParallaxTilt(
                filteredTilt,
                anchorPixels,
                hoverPixels,
                hoverNormalized);
            imageBasedLighting?.SetViewResponse(
                filteredTilt,
                reduceMotionEnabled,
                Time.unscaledTime,
                Time.unscaledDeltaTime,
                hoverNormalized);
        }

        private Vector2 ResolveTargetTilt()
        {
            if (SceneParallaxInput.TryGetRecent(
                    out Vector2 deviceTilt,
                    out float sourceFullScaleAngle))
            {
                return SceneParallaxInput.MapToParallax(
                    deviceTilt,
                    sourceFullScaleAngle,
                    ParallaxFullScaleAngle,
                    VerticalMotionScale);
            }

#if UNITY_EDITOR || UNITY_STANDALONE
            if (!Application.isBatchMode && Mouse.current != null)
            {
                Vector2 viewport = ResolveViewportPixels(targetCamera);
                Vector2 pointer = SceneParallaxInput.NormalizePointer(
                    Mouse.current.position.ReadValue(),
                    viewport);
                return new Vector2(pointer.x, pointer.y * VerticalMotionScale);
            }
#endif

            return Vector2.zero;
        }

        private void ApplyProjectionOffset(
            Vector2 normalizedTilt,
            float anchorPixels,
            float hoverPixels)
        {
            if (!Mathf.Approximately(baselineAspect, targetCamera.aspect))
            {
                float previousAspect = Mathf.Max(0.01f, baselineAspect);
                float currentAspect = Mathf.Max(0.01f, targetCamera.aspect);
                baselineProjection.m00 *= previousAspect / currentAspect;
                baselineAspect = targetCamera.aspect;
            }

            Vector2 viewport = ResolveViewportPixels(targetCamera);
            Vector2 pixelOffset = normalizedTilt * anchorPixels;
            // Perspective projection uses the opposite sign from screen-space
            // travel because visible camera-space Z is negative. Resolve the
            // sign explicitly so the canyon follows the user's swipe instead
            // of appearing to move against their finger.
            pixelOffset.x += ResolveLibraryPageProjectionPixels(
                libraryPageOffset,
                viewport.x);
            pixelOffset.y += hoverPixels;
            targetCamera.projectionMatrix = OffsetProjection(
                baselineProjection,
                targetCamera.orthographic,
                pixelOffset,
                viewport);
        }

        private void OnDisable()
        {
            ResetPresentation();
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                filteredTilt = Vector2.zero;
                ResetPresentation();
            }
        }

        private void ResetPresentation()
        {
            if (targetCamera != null && hasBaselineProjection)
            {
                targetCamera.projectionMatrix = baselineProjection;
            }

            environmentPresenter?.SetLayeredParallaxTilt(
                Vector2.zero,
                0f,
                0f,
                0f);
            imageBasedLighting?.SetViewResponse(
                Vector2.zero,
                reduceMotionEnabled,
                Time.unscaledTime,
                0f,
                0f);
        }

        public void SetLibraryPreviewActive(bool active, bool immediate = false)
        {
            libraryPreviewActive = active;
            if (!active)
            {
                targetLibraryPageOffset = 0f;
            }
            if (immediate)
            {
                libraryPageOffset = targetLibraryPageOffset;
            }
        }

        public void BeginLibraryPageExit(float direction)
        {
            if (!libraryPreviewActive)
            {
                return;
            }

            targetLibraryPageOffset = Mathf.Sign(direction);
        }

        public void BeginLibraryPageEntrance(float direction)
        {
            libraryPreviewActive = true;
            libraryPageOffset = Mathf.Sign(direction);
            targetLibraryPageOffset = 0f;
        }

        public static float ResolveLibraryHoverPixels(
            float unscaledTime,
            bool libraryActive,
            bool reduceMotion)
        {
            if (!libraryActive)
            {
                return 0f;
            }

            if (reduceMotion)
            {
                return LibraryHoverBasePixels;
            }

            return LibraryHoverBasePixels
                + Mathf.Sin(
                    unscaledTime
                    * LibraryHoverCyclesPerSecond
                    * Mathf.PI
                    * 2f)
                * LibraryHoverAmplitudePixels;
        }

        public static float ResolveLibraryHoverNormalized(
            float unscaledTime,
            bool libraryActive,
            bool reduceMotion)
        {
            if (!libraryActive || reduceMotion)
            {
                return 0f;
            }

            return Mathf.Sin(
                    unscaledTime
                    * LibraryHoverCyclesPerSecond
                    * Mathf.PI
                    * 2f)
                * 0.5f
                + 0.5f;
        }

        public static float ResolveLibraryPageProjectionPixels(
            float normalizedPageOffset,
            float viewportWidthPixels)
        {
            return -Mathf.Clamp(normalizedPageOffset, -1f, 1f)
                * Mathf.Max(1f, viewportWidthPixels)
                * LibraryPageTravelViewport;
        }

        private void RefreshAccessibilitySetting(bool force)
        {
            if (!force && Time.unscaledTime < nextAccessibilityRefresh)
            {
                return;
            }

            reduceMotionEnabled = IosDeviceMotion.IsReduceMotionEnabled();
            nextAccessibilityRefresh = Time.unscaledTime
                + AccessibilityRefreshInterval;
        }

        public static Matrix4x4 OffsetProjection(
            Matrix4x4 projection,
            bool orthographic,
            Vector2 pixelOffset,
            Vector2 viewportPixels)
        {
            float normalizedX = pixelOffset.x * 2f / Mathf.Max(1f, viewportPixels.x);
            float normalizedY = pixelOffset.y * 2f / Mathf.Max(1f, viewportPixels.y);
            if (orthographic)
            {
                projection.m03 += normalizedX;
                projection.m13 += normalizedY;
            }
            else
            {
                projection.m02 += normalizedX;
                projection.m12 += normalizedY;
            }

            return projection;
        }

        public static Vector2 ResolveViewportPixels(Camera camera)
        {
            if (camera != null && camera.targetTexture != null)
            {
                return new Vector2(
                    camera.targetTexture.width,
                    camera.targetTexture.height);
            }

            return new Vector2(
                Mathf.Max(1, camera != null ? camera.pixelWidth : Screen.width),
                Mathf.Max(1, camera != null ? camera.pixelHeight : Screen.height));
        }
    }
}
