using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Product
{
    public readonly struct SpinnerEnvironmentPalette
    {
        public SpinnerEnvironmentPalette(
            Color sky,
            Color equator,
            Color ground,
            Color key,
            Color fill,
            Vector2 keyViewport)
        {
            Sky = sky;
            Equator = equator;
            Ground = ground;
            Key = key;
            Fill = fill;
            KeyViewport = keyViewport;
        }

        public Color Sky { get; }
        public Color Equator { get; }
        public Color Ground { get; }
        public Color Key { get; }
        public Color Fill { get; }
        public Vector2 KeyViewport { get; }
    }

    /// <summary>
    /// Adapts the product lighting to the selected environment image. It reads
    /// a tiny GPU thumbnail once when a scene is selected, derives a stable
    /// palette, synthesizes a low-frequency reflection cubemap, updates the
    /// authored lights, and adds a restrained product-color bounce aligned to
    /// the baked grounding ledge. Replacing the background therefore does not
    /// require manually authoring another reflection texture.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class SpinnerImageBasedLightingController : MonoBehaviour
    {
        public const string BounceLightName = "SpinnerModelColorBounce";
        public const string VisibilityFillName = "SpinnerEnvironmentVisibilityFill";
        public const string ViewHighlightName = "SpinnerViewResponsiveHighlight";
        public const int SampleWidth = 24;
        public const int SampleHeight = 32;
        public const int ReflectionSize = 16;
        public const float MagneticSlideSoftboxIntensity = 0.40f;
        public const float MagneticSlideReflectionBaseScale = 1.00f;
        public const float MagneticSlideOpposingStripIntensity = 0.26f;
        public const float MagneticSlideSoftboxHorizontalCore = 0.22f;
        public const float MagneticSlideSoftboxHorizontalEdge = 0.88f;
        public const float MagneticSlideSoftboxVerticalCore = 0.18f;
        public const float MagneticSlideSoftboxVerticalEdge = 0.78f;
        public const float FanCardReflectionBaseScale = 0.78f;
        public const float FanCardReflectionPeak = 0.66f;
        public const float FanCardReflectionYawRadians = 0.10f;
        public const float FanCardReflectionPitchRadians = 0.07f;
        public const float SoftAmbientScale = 0.42f;
        public const float SoftDirectLightScale = 0.36f;
        public const float SoftReflectionIntensityScale = 0.35f;
        public const float SoftVisibilityFillScale = 0.35f;
        public const float SoftModelBounceScale = 0.28f;
        public const float SoftViewHighlightScale = 0.25f;
        public const float SoftReflectionBaseScale = 0.75f;
        public const float SoftReflectionKeyScale = 0.12f;
        public const float SoftReflectionFillScale = 0.04f;
        public const float SoftReflectionPeak = 0.65f;
        public const float SoftEnvironmentGlowScale = 0.38f;
        // GEEONE ships on a near-black plate. The shared soft-metal policy was tuned for
        // bright canyon library cards and leaves the satin steel too dim. One recipe is
        // applied in library and detail (user 2026-09-08: "内外一定要一致"); the profile
        // library scales for this model are 1.0 so both poses light identically.
        // The numbers live in GeeoneLightingPresetCatalog.Shipping; these
        // constants mirror them for tests and older call sites.
        public const float GeeoneDirectLightBoost = 3.10f;
        public const float GeeoneReflectionBoost = 2.55f;
        public const float GeeoneAmbientBoost = 3.40f;
        public const float GeeoneVisibilityFillIntensity = 0.85f;
        public static readonly Color GeeoneAmbientFloorSky =
            new(0.42f, 0.44f, 0.48f, 1f);
        public static readonly Color GeeoneAmbientFloorEquator =
            new(0.30f, 0.32f, 0.36f, 1f);
        public static readonly Color GeeoneAmbientFloorGround =
            new(0.12f, 0.13f, 0.15f, 1f);
        public const float GeeoneKeyLightFloor = 0.72f;
        public const float GeeoneWarmRimLightFloor = 0.58f;
        public const float GeeoneCoolFillLightFloor = 0.50f;
        // Library thumbnails carry a slightly stronger product-color bounce so the
        // ledge pool reads on the small card. Tweened with the rest of the state.
        public const float LibraryBounceScale = 1.28f;
        public const float SoftBrightMetalThreshold = 0.55f;
        public const float SoftBrightMetalAlbedoScale = 0.90f;
        public const float SoftBrightMetalSmoothnessCap = 0.70f;
        public const float EnvironmentColorCoupling = 0.14f;
        public const float AmbientChromaRetention = 0.32f;
        public const float FanCardEnvironmentColorCoupling = 0.26f;
        public const float FanCardAmbientChromaRetention = 0.44f;
        public const float FanCardCubemapKeyScale = 0.34f;
        public const float FanCardCubemapFillScale = 0.12f;
        public const float FanCardKeyHighlightPower = 8.0f;
        public const float FanCardVisibilityFillScale = 0f;
        public const float FanCardSoftFrontLiftScale = 0f;
        // The key must sit far enough off the view axis that its specular band
        // and its cast shadow both read as coming from one visible direction.
        public const float FanCardKeyYawSpan = 60f;
        public const float FanCardKeyPitchMin = 52f;
        public const float FanCardKeyPitchMax = 58f;
        public const float FanCardSkyFillPitch = 72f;
        public const float FanCardSkyFillYaw = -60f;
        public const float FanCardLightSaturationCap = 0.30f;
        public const float FanCardAmbientSaturationCap = 0.40f;
        public const float FanCardAmbientKeyMix = 0.14f;
        public const float FanCardAuthoredLightMix = 0.18f;
        public const float FanCardSampledLightMix = 0.30f;
        public const float FanCardSourceColorSampleMix = 0.28f;
        public const float FanCardSampledChromaFloor = 0.05f;
        public const float FanCardSampledChromaFull = 0.20f;
        public const float FanCardVisibleKeyViewportX = 0.34f;
        public const float FanCardVisibleKeyViewportY = 0.94f;
        public const float FanCardPedestalGlowCenterY = 0.34f;
        public const float FanCardPedestalGlowRadius = 0.13f;
        public const float FanCardPedestalGlowIntensity = 0f;
        public const float FanCardForegroundGlowIntensity = 0f;
        public const float FanCardContactShadowScaleX = 0.76f;
        public const float FanCardContactShadowScaleY = 9.2f;
        public const float FanCardContactShadowRadius = 0.145f;
        public const float FanCardContactShadowStrength = 0.46f;
        public const float FanCardKeyIntensityScale = 1f;
        public const float FanCardFillIntensityScale = 1f;

        // Every product scene currently uses the same approved canyon plate.
        // A GPU ReadPixels during each page selection forces a render-thread
        // synchronization and presents as a visible swipe hitch on iPhone.
        // Cache by the catalog resource path so the plate is sampled once per
        // app session while each model still applies its own authored fallback
        // and lighting scales.
        private static readonly Dictionary<string, SpinnerEnvironmentPalette>
            CachedBackgroundPalettes = new();
        private static readonly int FanCardReflectionTiltShaderId =
            Shader.PropertyToID("_FanCardViewReflectionTilt");

        private Cubemap generatedReflection;
        private Light modelBounceLight;
        private Light visibilityFillLight;
        private Light viewHighlightLight;
        private SpinnerGroundingStage groundingStage;
        private SpinnerEnvironmentPresenter environmentPresenter;
        private Color modelAccent = Color.white;
        private Color smoothedLeftGlow = Color.black;
        private Color smoothedRightGlow = Color.black;
        private Vector3 baseBouncePosition;
        private float baseBounceIntensity;
        private float planarModelSize;
        private float modelColorfulness;
        private float visibilityFillBaseIntensity;
        private float presentationLightScale = 1f;
        private float baseReflectionIntensity;
        private float libraryLightScale = 1f;
        private float libraryReflectionScale = 1f;
        private bool libraryPreviewActive;
        private PresentationLightingState presentationState =
            PresentationLightingState.Neutral;
        private PresentationLightingState transitionStartState;
        private PresentationLightingState transitionTargetState;
        private float transitionElapsedSeconds;
        private bool transitionActive;
        private bool softSpinnerLightingActive;
        private bool fanCardLightingActive;
        private float softSpinnerLightTrim = 1f;
        private string currentModelId = string.Empty;
        private Color baseAmbientSky = Color.black;
        private Color baseAmbientEquator = Color.black;
        private Color baseAmbientGround = Color.black;
        private readonly List<Light> authoredLights = new();
        private readonly List<float> authoredLightIntensities = new();

        public SpinnerEnvironmentPalette CurrentPalette { get; private set; }
        public Cubemap GeneratedReflection => generatedReflection;
        public Light ModelBounceLight => modelBounceLight;
        public Light VisibilityFillLight => visibilityFillLight;
        public Light ViewHighlightLight => viewHighlightLight;
        public bool SoftSpinnerLightingActive => softSpinnerLightingActive;
        public bool PresentationTransitionActive => transitionActive;
        public PresentationLightingState CurrentPresentationState => presentationState;

        /// <summary>
        /// Everything the library/detail pose changes about the lighting, as one
        /// value so the switch can be tweened instead of jumped.
        /// </summary>
        public readonly struct PresentationLightingState
        {
            public PresentationLightingState(
                float lightScale,
                float reflectionScale,
                float visibilityFillIntensity,
                float bounceScale,
                Color ambientSky,
                Color ambientEquator,
                Color ambientGround)
            {
                LightScale = lightScale;
                ReflectionScale = reflectionScale;
                VisibilityFillIntensity = visibilityFillIntensity;
                BounceScale = bounceScale;
                AmbientSky = ambientSky;
                AmbientEquator = ambientEquator;
                AmbientGround = ambientGround;
            }

            public float LightScale { get; }
            public float ReflectionScale { get; }
            public float VisibilityFillIntensity { get; }
            public float BounceScale { get; }
            public Color AmbientSky { get; }
            public Color AmbientEquator { get; }
            public Color AmbientGround { get; }

            public static PresentationLightingState Neutral =>
                new(1f, 1f, 0f, 1f, Color.black, Color.black, Color.black);

            public static PresentationLightingState Lerp(
                PresentationLightingState from,
                PresentationLightingState to,
                float progress)
            {
                float t = Mathf.Clamp01(progress);
                return new PresentationLightingState(
                    Mathf.Lerp(from.LightScale, to.LightScale, t),
                    Mathf.Lerp(from.ReflectionScale, to.ReflectionScale, t),
                    Mathf.Lerp(from.VisibilityFillIntensity, to.VisibilityFillIntensity, t),
                    Mathf.Lerp(from.BounceScale, to.BounceScale, t),
                    Color.Lerp(from.AmbientSky, to.AmbientSky, t),
                    Color.Lerp(from.AmbientEquator, to.AmbientEquator, t),
                    Color.Lerp(from.AmbientGround, to.AmbientGround, t));
            }
        }

        public void Configure(
            Texture background,
            SpinnerEnvironmentProfile profile,
            SpinnerGroundingStage groundingStage,
            string backgroundCacheKey = null)
        {
            currentModelId = profile.ModelId;
            softSpinnerLightingActive = UsesSoftSpinnerLighting(profile.ModelId);
            fanCardLightingActive = string.Equals(
                profile.ModelId,
                "magnetic-fan-card",
                StringComparison.Ordinal);
            softSpinnerLightTrim = ResolveSoftSpinnerLightTrim(profile.ModelId);
            SpinnerEnvironmentPalette fallback = new SpinnerEnvironmentPalette(
                profile.AmbientSky,
                profile.AmbientEquator,
                profile.AmbientGround,
                profile.Lights.Count > 0 ? profile.Lights[0].Color : Color.white,
                profile.Lights.Count > 1 ? profile.Lights[1].Color : profile.AmbientEquator,
                fanCardLightingActive
                    ? new Vector2(FanCardVisibleKeyViewportX, FanCardVisibleKeyViewportY)
                    : new Vector2(0.36f, 0.76f));
            libraryLightScale = Mathf.Clamp01(profile.LibraryLightScale);
            libraryReflectionScale = Mathf.Clamp01(profile.LibraryReflectionScale);

            bool sampledPalette = TryResolvePalette(
                    background,
                    string.IsNullOrEmpty(backgroundCacheKey)
                        ? profile.BackgroundResourcePath
                        : backgroundCacheKey,
                    fanCardLightingActive,
                    out SpinnerEnvironmentPalette sampled);
            SpinnerEnvironmentPalette coupled = sampled;
            if (fanCardLightingActive && sampledPalette)
            {
                coupled = CoupleFanCardPalette(sampled, fallback);
            }
            CurrentPalette = sampledPalette
                ? StabilizePalette(coupled, fallback, fanCardLightingActive)
                : fallback;

            ApplyAmbientAndReflection(profile, CurrentPalette);
            ApplyAuthoredLights(profile, CurrentPalette);
            ApplyVisibilityFill(CurrentPalette);
            ApplyModelAndStageResponse(groundingStage, CurrentPalette);
            environmentPresenter = GetComponent<SpinnerEnvironmentPresenter>();
            ResolveCoupledGlowColors(
                CurrentPalette,
                modelAccent,
                Vector2.zero,
                ResolveEnvironmentColorCoupling(),
                out smoothedLeftGlow,
                out smoothedRightGlow);
            SetLibraryPreviewActive(true, true);
            SetViewResponse(Vector2.zero, false, 0f, 0f, 0f);
        }

        public void SetLibraryPreviewActive(bool active, bool immediate = false)
        {
            libraryPreviewActive = active;
            PresentationLightingState target = ResolvePresentationState(active);
            // Editor captures and tests have no LateUpdate; batch previews must
            // land on the final state in the same call.
            if (immediate || !Application.isPlaying)
            {
                transitionActive = false;
                ApplyPresentationState(target);
                return;
            }

            transitionStartState = presentationState;
            transitionTargetState = target;
            transitionElapsedSeconds = 0f;
            transitionActive = true;
        }

        private void LateUpdate()
        {
            if (!transitionActive)
            {
                return;
            }

            AdvancePresentationTransition(Time.unscaledDeltaTime);
        }

        /// <summary>
        /// Advances the library/detail lighting tween on the shared
        /// <see cref="SpinnerPresentationTransition"/> curve so lights, ambient,
        /// and reflections arrive together with the camera and stage.
        /// </summary>
        public void AdvancePresentationTransition(float unscaledDeltaTime)
        {
            if (!transitionActive)
            {
                return;
            }

            transitionElapsedSeconds += Mathf.Max(0f, unscaledDeltaTime);
            float progress = SpinnerPresentationTransition.ResolveProgress(
                transitionElapsedSeconds);
            ApplyPresentationState(PresentationLightingState.Lerp(
                transitionStartState,
                transitionTargetState,
                progress));
            if (progress >= 1f)
            {
                transitionActive = false;
                ApplyPresentationState(transitionTargetState);
            }
        }

        /// <summary>
        /// Editor previews: place the lighting at a point on the library→detail
        /// timeline (0 = library, 1 = detail) using the same eased curve.
        /// </summary>
        public void SetDetailEntranceProgressForPreview(float progress)
        {
            transitionActive = false;
            libraryPreviewActive = progress < 1f;
            float eased = SpinnerPresentationTransition.ResolveProgress(
                SpinnerPresentationTransition.DurationSeconds * Mathf.Clamp01(progress));
            ApplyPresentationState(PresentationLightingState.Lerp(
                ResolvePresentationState(true),
                ResolvePresentationState(false),
                eased));
        }

        public PresentationLightingState ResolvePresentationState(bool libraryPose)
        {
            float lightScale = libraryPose ? libraryLightScale : 1f;
            float reflectionScale = libraryPose ? libraryReflectionScale : 1f;
            float visibilityFill = visibilityFillBaseIntensity
                * (libraryPose ? Mathf.Lerp(0.28f, 1f, libraryLightScale) : 1f);
            float bounceScale = lightScale * (libraryPose ? LibraryBounceScale : 1f);
            Color sky = baseAmbientSky;
            Color equator = baseAmbientEquator;
            Color ground = baseAmbientGround;
            if (UsesGeeonePresentationRecipe(currentModelId))
            {
                GeeoneLightingPreset preset = GeeoneLightingPresetCatalog.Active;
                lightScale *= preset.DirectLightBoost;
                reflectionScale *= preset.ReflectionBoost;
                visibilityFill = preset.VisibilityFillIntensity;
                bounceScale = lightScale;
                sky = ColorMax(
                    baseAmbientSky * preset.AmbientBoost,
                    GeeoneLightingPresetCatalog.ScaleFloor(
                        GeeoneAmbientFloorSky,
                        preset.AmbientFloorScale));
                equator = ColorMax(
                    baseAmbientEquator * preset.AmbientBoost,
                    GeeoneLightingPresetCatalog.ScaleFloor(
                        GeeoneAmbientFloorEquator,
                        preset.AmbientFloorScale));
                ground = ColorMax(
                    baseAmbientGround * preset.AmbientBoost,
                    GeeoneLightingPresetCatalog.ScaleFloor(
                        GeeoneAmbientFloorGround,
                        preset.AmbientFloorScale));
            }

            return new PresentationLightingState(
                lightScale,
                reflectionScale,
                visibilityFill,
                bounceScale,
                sky,
                equator,
                ground);
        }

        private void ApplyPresentationState(PresentationLightingState state)
        {
            presentationState = state;
            presentationLightScale = state.LightScale;
            for (int index = 0; index < authoredLights.Count; index++)
            {
                Light light = authoredLights[index];
                if (light != null)
                {
                    light.intensity = ResolveAuthoredLightIntensity(
                        currentModelId,
                        light.name,
                        authoredLightIntensities[index],
                        state.LightScale);
                }
            }

            if (visibilityFillLight != null)
            {
                visibilityFillLight.intensity = state.VisibilityFillIntensity;
            }
            if (modelBounceLight != null)
            {
                modelBounceLight.intensity = baseBounceIntensity * state.BounceScale;
            }

            RenderSettings.reflectionIntensity = baseReflectionIntensity * state.ReflectionScale;
            RenderSettings.ambientSkyColor = state.AmbientSky;
            RenderSettings.ambientEquatorColor = state.AmbientEquator;
            RenderSettings.ambientGroundColor = state.AmbientGround;
        }

        /// <summary>
        /// Single source for an authored light's runtime intensity. Editor
        /// captures and tests must call this instead of hard-coding values.
        /// </summary>
        public static float ResolveAuthoredLightIntensity(
            string modelId,
            string lightName,
            float softenedBaseIntensity,
            float lightScale)
        {
            float intensity = softenedBaseIntensity * lightScale;
            if (UsesGeeonePresentationRecipe(modelId))
            {
                // GEEONE's three authored spots take their intensity straight
                // from the preset so a softer preset can really lower them; the
                // shipping values equal the old floors, so nothing shifts.
                float presetIntensity = ResolveGeeoneLightFloor(lightName);
                if (presetIntensity > 0f)
                {
                    return presetIntensity;
                }
            }
            return intensity;
        }

        public static float ResolveGeeoneLightFloor(string lightName)
        {
            GeeoneLightingPreset preset = GeeoneLightingPresetCatalog.Active;
            if (string.Equals(lightName, "Key_5000K", StringComparison.Ordinal))
            {
                return preset.KeyLightFloor;
            }
            if (string.Equals(lightName, "WarmRim_3200K", StringComparison.Ordinal))
            {
                return preset.WarmRimLightFloor;
            }
            if (string.Equals(lightName, "CoolFill_6500K", StringComparison.Ordinal))
            {
                return preset.CoolFillLightFloor;
            }
            return 0f;
        }

        public static bool UsesGeeonePresentationRecipe(string modelId)
        {
            return string.Equals(
                modelId,
                ProductCatalog.MetalThreeBladeModelId,
                StringComparison.Ordinal);
        }

        private static Color ColorMax(Color value, Color floor)
        {
            return new Color(
                Mathf.Max(value.r, floor.r),
                Mathf.Max(value.g, floor.g),
                Mathf.Max(value.b, floor.b),
                1f);
        }

        public void SetViewResponse(
            Vector2 normalizedTilt,
            bool reduceMotion,
            float unscaledTime,
            float unscaledDeltaTime,
            float hoverNormalized)
        {
            if (groundingStage == null || modelBounceLight == null)
            {
                return;
            }

            Vector2 opticalTilt = reduceMotion
                ? Vector2.zero
                : Vector2.ClampMagnitude(normalizedTilt, 1f);
            Shader.SetGlobalVector(
                FanCardReflectionTiltShaderId,
                fanCardLightingActive
                    ? ResolveFanCardReflectionTilt(opticalTilt)
                    : Vector4.zero);
            if (visibilityFillLight != null)
            {
                // Keep the restrained fill camera-facing after the library
                // camera moves into its 90-degree display pose.
                visibilityFillLight.transform.SetPositionAndRotation(
                    transform.position,
                    transform.rotation);
            }
            ResolveCoupledGlowColors(
                CurrentPalette,
                modelAccent,
                opticalTilt,
                ResolveEnvironmentColorCoupling(),
                out Color targetLeft,
                out Color targetRight);
            float blend = unscaledDeltaTime <= 0f
                ? 1f
                : 1f - Mathf.Exp(-4.2f * unscaledDeltaTime);
            smoothedLeftGlow = Color.Lerp(smoothedLeftGlow, targetLeft, blend);
            smoothedRightGlow = Color.Lerp(smoothedRightGlow, targetRight, blend);

            float breathing = reduceMotion
                ? 0.94f + Mathf.Sin(unscaledTime * 1.15f) * 0.06f
                : 1f;
            float environmentGlowScale = ResolveEnvironmentGlowScale(currentModelId);
            environmentPresenter?.SetEnvironmentGlow(
                smoothedLeftGlow * breathing * environmentGlowScale,
                smoothedRightGlow * breathing * environmentGlowScale,
                opticalTilt);

            Transform cameraTransform = transform;
            Vector3 lateral = cameraTransform.right * opticalTilt.x;
            Vector3 vertical = cameraTransform.up * opticalTilt.y;
            modelBounceLight.transform.position = baseBouncePosition
                + lateral * planarModelSize * 0.20f
                + vertical * planarModelSize * 0.08f;
            modelBounceLight.color = NormalizeLightColor(Color.Lerp(
                smoothedLeftGlow,
                smoothedRightGlow,
                Mathf.Clamp01(0.5f + opticalTilt.x * 0.5f)));
            modelBounceLight.intensity = baseBounceIntensity
                * presentationState.BounceScale
                * breathing;

            EnsureViewHighlight();
            if (fanCardLightingActive)
            {
                // A camera-side point source made a hard, triangular glint on
                // the front bevel. The shipping canyon has no such practical.
                viewHighlightLight.gameObject.SetActive(false);
                return;
            }
            viewHighlightLight.gameObject.SetActive(true);
            Bounds bounds = groundingStage.ModelBounds;
            Vector3 towardCamera = transform.position - bounds.center;
            if (towardCamera.sqrMagnitude < 0.000001f)
            {
                towardCamera = -transform.forward;
            }
            towardCamera.Normalize();
            viewHighlightLight.transform.position = bounds.center
                + towardCamera * planarModelSize * 0.64f
                + lateral * planarModelSize * 0.48f
                + vertical * planarModelSize * 0.34f
                + Vector3.up * bounds.size.y * 0.34f;
            viewHighlightLight.color = NormalizeLightColor(Color.Lerp(
                new Color(0.94f, 0.93f, 0.90f, 1f),
                Color.Lerp(
                    smoothedLeftGlow,
                    smoothedRightGlow,
                    Mathf.Clamp01(0.5f + opticalTilt.x * 0.5f)),
                ResolveEnvironmentColorCoupling()));
            float highlightIntensity = Mathf.Lerp(
                0.045f,
                0.16f,
                modelColorfulness) * (softSpinnerLightingActive
                    ? SoftViewHighlightScale * softSpinnerLightTrim
                    : 1f);
            if (fanCardLightingActive)
            {
                highlightIntensity = Mathf.Max(highlightIntensity, 0.22f);
            }
            viewHighlightLight.intensity = (reduceMotion
                ? highlightIntensity * 0.55f
                : highlightIntensity)
                * presentationLightScale
                * breathing
                * Mathf.Lerp(1.08f, 0.90f, hoverNormalized);
        }

        public static void ResolveCoupledGlowColors(
            SpinnerEnvironmentPalette palette,
            Color modelColor,
            Vector2 normalizedTilt,
            out Color left,
            out Color right)
        {
            ResolveCoupledGlowColors(
                palette,
                modelColor,
                normalizedTilt,
                EnvironmentColorCoupling,
                out left,
                out right);
        }

        public static void ResolveCoupledGlowColors(
            SpinnerEnvironmentPalette palette,
            Color modelColor,
            Vector2 normalizedTilt,
            float coupling,
            out Color left,
            out Color right)
        {
            float horizontal = Mathf.Clamp01(0.5f + normalizedTilt.x * 0.5f);
            Color leftEnvironment = Color.Lerp(palette.Key, palette.Fill, horizontal);
            Color rightEnvironment = Color.Lerp(palette.Fill, palette.Key, horizontal);
            float amount = Mathf.Clamp01(coupling);
            left = NormalizeLightColor(Color.Lerp(modelColor, leftEnvironment, amount));
            right = NormalizeLightColor(Color.Lerp(modelColor, rightEnvironment, amount));
        }

        public static Quaternion ResolveFanCardKeyRotation(Vector2 keyViewport)
        {
            // The top key travels down toward the central stone support. The
            // reflection source is resolved separately from the rear opening.
            float yaw = (0.5f - Mathf.Clamp01(keyViewport.x)) * 2f * FanCardKeyYawSpan;
            float pitch = Mathf.Lerp(
                FanCardKeyPitchMin,
                FanCardKeyPitchMax,
                Mathf.Clamp01(keyViewport.y));
            return Quaternion.Euler(pitch, yaw, 0f);
        }

        public static Vector4 ResolveFanCardReflectionTilt(Vector2 normalizedTilt)
        {
            Vector2 tilt = Vector2.ClampMagnitude(normalizedTilt, 1f);
            return new Vector4(
                tilt.x * FanCardReflectionYawRadians,
                tilt.y * FanCardReflectionPitchRadians,
                0f,
                0f);
        }

        public static Quaternion ResolveFanCardSkyFillRotation()
        {
            return Quaternion.Euler(
                FanCardSkyFillPitch,
                FanCardSkyFillYaw,
                0f);
        }

        public static float ResolveFanCardContactShadowCenterX(Vector2 keyViewport)
        {
            return Mathf.Clamp(
                0.50f - (Mathf.Clamp01(keyViewport.x) - 0.5f) * 0.40f,
                0.36f,
                0.64f);
        }

        public static float ColorChroma(Color color)
        {
            return Mathf.Max(color.r, Mathf.Max(color.g, color.b))
                - Mathf.Min(color.r, Mathf.Min(color.g, color.b));
        }

        public static float ResolveFanCardSampleMix(Color sampledKey)
        {
            return Mathf.Lerp(
                FanCardAuthoredLightMix,
                FanCardSampledLightMix,
                Mathf.InverseLerp(
                    FanCardSampledChromaFloor,
                    FanCardSampledChromaFull,
                    ColorChroma(sampledKey)));
        }

        public static SpinnerEnvironmentPalette CoupleFanCardPalette(
            SpinnerEnvironmentPalette sampled,
            SpinnerEnvironmentPalette authored)
        {
            float mix = ResolveFanCardSampleMix(sampled.Key);
            return new SpinnerEnvironmentPalette(
                sampled.Sky,
                sampled.Equator,
                sampled.Ground,
                Color.Lerp(authored.Key, sampled.Key, mix),
                Color.Lerp(authored.Fill, sampled.Fill, mix),
                new Vector2(
                    FanCardVisibleKeyViewportX,
                    FanCardVisibleKeyViewportY));
        }

        public static SpinnerEnvironmentPalette AnalyzePixels(
            Color[] pixels,
            int width,
            int height)
        {
            return AnalyzePixels(pixels, width, height, false);
        }

        public static SpinnerEnvironmentPalette AnalyzePixels(
            Color[] pixels,
            int width,
            int height,
            bool weightChroma)
        {
            if (pixels == null || pixels.Length != width * height || width < 2 || height < 3)
            {
                throw new ArgumentException("A complete image sample is required.", nameof(pixels));
            }

            Color sky = AverageBand(pixels, width, height, 0.66f, 1f);
            Color equator = AverageBand(pixels, width, height, 0.32f, 0.68f);
            Color ground = AverageBand(pixels, width, height, 0f, 0.34f);

            Color key = Color.black;
            float brightestScore = -1f;
            Vector2 keyViewport = new Vector2(0.5f, 0.75f);
            const int columns = 3;
            const int rows = 4;
            for (int tileY = 0; tileY < rows; tileY++)
            {
                for (int tileX = 0; tileX < columns; tileX++)
                {
                    Color tile = AverageRect(
                        pixels,
                        width,
                        height,
                        (float)tileX / columns,
                        (float)(tileX + 1) / columns,
                        (float)tileY / rows,
                        (float)(tileY + 1) / rows);
                    float chroma = ColorChroma(tile);
                    float score = Luminance(tile)
                        * (weightChroma ? 1f + chroma * 3.2f : 1f);
                    if (score > brightestScore)
                    {
                        brightestScore = score;
                        key = tile;
                        keyViewport = new Vector2(
                            (tileX + 0.5f) / columns,
                            (tileY + 0.5f) / rows);
                    }
                }
            }

            bool keyOnLeft = keyViewport.x < 0.5f;
            Color fill = AverageRect(
                pixels,
                width,
                height,
                keyOnLeft ? 0.55f : 0f,
                keyOnLeft ? 1f : 0.45f,
                0.18f,
                0.82f);

            return new SpinnerEnvironmentPalette(
                sky,
                equator,
                ground,
                key,
                fill,
                keyViewport);
        }

        public static Color ResolveModelAccent(IReadOnlyList<Renderer> renderers)
        {
            if (renderers == null || renderers.Count == 0)
            {
                return new Color(0.35f, 0.36f, 0.37f, 1f);
            }

            Color accumulated = Color.black;
            float totalWeight = 0f;
            for (int rendererIndex = 0; rendererIndex < renderers.Count; rendererIndex++)
            {
                Renderer renderer = renderers[rendererIndex];
                if (renderer == null)
                {
                    continue;
                }

                float rendererWeight = Mathf.Max(0.001f, renderer.bounds.size.sqrMagnitude);
                Material[] materials = renderer.sharedMaterials;
                for (int materialIndex = 0; materialIndex < materials.Length; materialIndex++)
                {
                    Material material = materials[materialIndex];
                    if (material == null)
                    {
                        continue;
                    }

                    Color color = material.HasProperty("_BaseColor")
                        ? material.GetColor("_BaseColor")
                        : material.HasProperty("_Color")
                            ? material.GetColor("_Color")
                            : Color.gray;
                    accumulated += color.linear * rendererWeight;
                    totalWeight += rendererWeight;
                }
            }

            if (totalWeight <= 0f)
            {
                return new Color(0.35f, 0.36f, 0.37f, 1f);
            }

            Color average = accumulated / totalWeight;
            average.a = 1f;
            return NormalizeLightColor(average);
        }

        private bool TryReadPalette(
            Texture background,
            bool weightChroma,
            out SpinnerEnvironmentPalette palette)
        {
            palette = default;
            if (background == null
                || SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
            {
                return false;
            }

            RenderTexture target = RenderTexture.GetTemporary(
                SampleWidth,
                SampleHeight,
                0,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Linear);
            RenderTexture previous = RenderTexture.active;
            Texture2D thumbnail = null;
            try
            {
                Graphics.Blit(background, target);
                RenderTexture.active = target;
                thumbnail = new Texture2D(
                    SampleWidth,
                    SampleHeight,
                    TextureFormat.RGBA32,
                    false,
                    true);
                thumbnail.ReadPixels(
                    new Rect(0f, 0f, SampleWidth, SampleHeight),
                    0,
                    0,
                    false);
                thumbnail.Apply(false, false);
                palette = AnalyzePixels(
                    thumbnail.GetPixels(),
                    SampleWidth,
                    SampleHeight,
                    weightChroma);
                return true;
            }
            catch (Exception exception)
            {
                Debug.LogWarning(
                    "[FidgetingApp] Background palette sampling fell back to the "
                    + $"catalog values: {exception.Message}");
                return false;
            }
            finally
            {
                RenderTexture.active = previous;
                RenderTexture.ReleaseTemporary(target);
                DestroyRuntimeObject(thumbnail);
            }
        }

        private bool TryResolvePalette(
            Texture background,
            string resourcePath,
            bool weightChroma,
            out SpinnerEnvironmentPalette palette)
        {
            string cacheKey = string.IsNullOrEmpty(resourcePath)
                ? background != null ? background.name : string.Empty
                : resourcePath;
            if (weightChroma && !string.IsNullOrEmpty(cacheKey))
            {
                cacheKey += "|chroma-key";
            }
            if (!string.IsNullOrEmpty(cacheKey)
                && CachedBackgroundPalettes.TryGetValue(cacheKey, out palette))
            {
                return true;
            }

            if (!TryReadPalette(background, weightChroma, out palette))
            {
                return false;
            }

            if (!string.IsNullOrEmpty(cacheKey))
            {
                CachedBackgroundPalettes[cacheKey] = palette;
            }
            return true;
        }

        private void ApplyAmbientAndReflection(
            SpinnerEnvironmentProfile profile,
            SpinnerEnvironmentPalette palette)
        {
            RenderSettings.ambientMode = AmbientMode.Trilight;
            float ambientScale = softSpinnerLightingActive
                ? SoftAmbientScale * softSpinnerLightTrim
                : 1f;
            float chromaRetention = fanCardLightingActive
                ? FanCardAmbientChromaRetention
                : AmbientChromaRetention;
            Color sky = RetainAmbientLuminance(palette.Sky, chromaRetention);
            Color equator = RetainAmbientLuminance(palette.Equator, chromaRetention);
            Color ground = RetainAmbientLuminance(palette.Ground, chromaRetention);
            if (fanCardLightingActive)
            {
                Color key = palette.Key;
                Color fill = palette.Fill;
                sky = Color.Lerp(sky, key, FanCardAmbientKeyMix);
                equator = Color.Lerp(equator, fill, FanCardAmbientKeyMix * 0.85f);
                ground = Color.Lerp(ground, fill, FanCardAmbientKeyMix * 1.15f);
            }
            baseAmbientSky = sky * ambientScale;
            baseAmbientEquator = equator * ambientScale;
            baseAmbientGround = ground * ambientScale;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            baseReflectionIntensity = profile.ReflectionIntensity
                * (softSpinnerLightingActive
                    ? SoftReflectionIntensityScale * softSpinnerLightTrim
                    : 1f);
            RenderSettings.reflectionIntensity = baseReflectionIntensity;

            DestroyRuntimeObject(generatedReflection);
            generatedReflection = BuildReflectionCubemap(palette, profile.ModelId);
            RenderSettings.customReflectionTexture = generatedReflection;

            ReflectionProbe[] probes = FindObjectsByType<ReflectionProbe>(
                FindObjectsInactive.Include,
                FindObjectsSortMode.None);
            for (int index = 0; index < probes.Length; index++)
            {
                ReflectionProbe probe = probes[index];
                probe.mode = ReflectionProbeMode.Custom;
                probe.customBakedTexture = generatedReflection;
                probe.intensity = 1f;
            }
        }

        private static Cubemap BuildReflectionCubemap(
            SpinnerEnvironmentPalette palette,
            string modelId)
        {
            bool isFanCard = string.Equals(
                modelId,
                "magnetic-fan-card",
                StringComparison.Ordinal);
            bool isMagneticSlide = string.Equals(
                modelId,
                "magnetic-slide-tile",
                StringComparison.Ordinal);
            // GEEONE's canyon palette is near black, so its steel sees almost no
            // environment and shades only by spot lobes. A preset may add the
            // slide's broad studio softbox so the metal gets a large soft source.
            float geeoneSoftbox = UsesGeeonePresentationRecipe(modelId)
                ? GeeoneLightingPresetCatalog.Active.StudioSoftboxIntensity
                : 0f;
            bool useBroadMetalSoftboxes = isMagneticSlide || geeoneSoftbox > 0f;
            float reflectionBaseScale = isMagneticSlide
                ? MagneticSlideReflectionBaseScale
                : isFanCard
                    ? FanCardReflectionBaseScale
                    : 1.28f;
            float broadPanelIntensity = isMagneticSlide
                ? MagneticSlideSoftboxIntensity
                : geeoneSoftbox;
            float opposingStripIntensity = isMagneticSlide
                ? MagneticSlideOpposingStripIntensity
                : geeoneSoftbox * 0.65f;
            float panelHorizontalCore = useBroadMetalSoftboxes
                ? MagneticSlideSoftboxHorizontalCore
                : 0.28f;
            float panelHorizontalEdge = useBroadMetalSoftboxes
                ? MagneticSlideSoftboxHorizontalEdge
                : 0.56f;
            float panelVerticalCore = useBroadMetalSoftboxes
                ? MagneticSlideSoftboxVerticalCore
                : 0.20f;
            float panelVerticalEdge = useBroadMetalSoftboxes
                ? MagneticSlideSoftboxVerticalEdge
                : 0.48f;
            TextureFormat format = SystemInfo.SupportsTextureFormat(TextureFormat.RGBAHalf)
                ? TextureFormat.RGBAHalf
                : TextureFormat.RGBA32;
            var cubemap = new Cubemap(ReflectionSize, format, true)
            {
                name = $"{modelId}_BackgroundReflection_Runtime",
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Trilinear
            };

            Array faces = Enum.GetValues(typeof(CubemapFace));
            for (int faceIndex = 0; faceIndex < faces.Length; faceIndex++)
            {
                CubemapFace face = (CubemapFace)faces.GetValue(faceIndex);
                if (face == CubemapFace.Unknown)
                {
                    continue;
                }

                var colors = new Color[ReflectionSize * ReflectionSize];
                for (int y = 0; y < ReflectionSize; y++)
                {
                    for (int x = 0; x < ReflectionSize; x++)
                    {
                        Vector3 direction = CubeDirection(face, x, y, ReflectionSize);
                        colors[y * ReflectionSize + x] =
                            SynthesizeReflection(
                                direction,
                                palette,
                                useBroadMetalSoftboxes,
                                isFanCard,
                                reflectionBaseScale,
                                broadPanelIntensity,
                                opposingStripIntensity,
                                panelHorizontalCore,
                                panelHorizontalEdge,
                                panelVerticalCore,
                                panelVerticalEdge,
                                geeoneSoftbox > 0f ? geeoneSoftbox * 0.55f : 0f);
                    }
                }
                cubemap.SetPixels(colors, face);
            }
            cubemap.Apply(true, true);
            return cubemap;
        }

        private static Color SynthesizeReflection(
            Vector3 direction,
            SpinnerEnvironmentPalette palette,
            bool useBroadMetalSoftboxes,
            bool isFanCard,
            float reflectionBaseScale,
            float broadPanelIntensity,
            float opposingStripIntensity,
            float panelHorizontalCore,
            float panelHorizontalEdge,
            float panelVerticalCore,
            float panelVerticalEdge,
            float neutralFloor = 0f)
        {
            float vertical = direction.y;
            Color baseColor = vertical >= 0f
                ? Color.Lerp(palette.Equator, palette.Sky, vertical)
                : Color.Lerp(palette.Equator, palette.Ground, -vertical);
            float reflectionDepth = isFanCard ? 0.65f : -0.65f;
            Vector3 keyDirection = new Vector3(
                palette.KeyViewport.x * 2f - 1f,
                palette.KeyViewport.y * 2f - 1f,
                reflectionDepth).normalized;
            float keyPower = isFanCard ? FanCardKeyHighlightPower : 12f;
            float keyHighlight = Mathf.Pow(
                Mathf.Max(0f, Vector3.Dot(direction, keyDirection)),
                keyPower);
            float fillHighlight = Mathf.Pow(
                Mathf.Max(0f, Vector3.Dot(direction, -keyDirection)),
                5f) * 0.18f;
            Color keyColor = NormalizeLightColor(palette.Key);
            Color fillColor = NormalizeLightColor(palette.Fill);
            if (isFanCard)
            {
                // The card carries only a low-frequency version of the real
                // environment. Its direct top key supplies the readable satin
                // sheen; synthetic panel and strip shapes remain slide-only.
                Color fanCardReflection = baseColor * reflectionBaseScale
                    + keyColor * keyHighlight * FanCardCubemapKeyScale
                    + fillColor * fillHighlight * FanCardCubemapFillScale;
                return LimitReflectionPeak(
                    fanCardReflection,
                    FanCardReflectionPeak);
            }
            Color result;
            if (useBroadMetalSoftboxes)
            {
                Vector3 panelForward = keyDirection;
                Vector3 panelRight = Vector3.Cross(Vector3.up, panelForward).normalized;
                if (panelRight.sqrMagnitude < 0.001f)
                {
                    panelRight = Vector3.right;
                }
                Vector3 panelUp = Vector3.Cross(panelForward, panelRight).normalized;
                float facing = Mathf.Clamp01(Vector3.Dot(direction, panelForward));
                float panelX = 1f - Mathf.SmoothStep(
                    panelHorizontalCore,
                    panelHorizontalEdge,
                    Mathf.Abs(Vector3.Dot(direction, panelRight)));
                float panelY = 1f - Mathf.SmoothStep(
                    panelVerticalCore,
                    panelVerticalEdge,
                    Mathf.Abs(Vector3.Dot(direction, panelUp)));
                float broadPanel = Mathf.SmoothStep(0.42f, 0.82f, facing)
                    * panelX
                    * panelY;

                Vector3 stripForward = -panelRight * 0.86f
                    + panelUp * 0.28f
                    - panelForward * 0.10f;
                stripForward.Normalize();
                float stripFacing = Mathf.Clamp01(
                    Vector3.Dot(direction, stripForward));
                float opposingStrip = Mathf.SmoothStep(
                    0.64f,
                    0.90f,
                    stripFacing);
                // neutralFloor lifts the whole sphere (sky brighter than ground)
                // so a near-black plate still gives the metal a readable sheen.
                float floorGradient = Mathf.Lerp(0.55f, 1f, Mathf.Clamp01(vertical * 0.5f + 0.5f));
                result = baseColor * reflectionBaseScale
                    + new Color(0.92f, 0.94f, 0.98f) * neutralFloor * floorGradient
                    + keyColor * keyHighlight * 0.12f
                    + fillColor * fillHighlight * 0.10f
                    + new Color(1.0f, 0.96f, 0.90f)
                        * broadPanel * broadPanelIntensity
                    + new Color(0.55f, 0.66f, 0.78f)
                        * opposingStrip * opposingStripIntensity;
            }
            else
            {
                result = baseColor * SoftReflectionBaseScale
                    + NormalizeLightColor(palette.Key)
                        * keyHighlight * SoftReflectionKeyScale
                    + NormalizeLightColor(palette.Fill)
                        * fillHighlight * SoftReflectionFillScale;
            }
            if (useBroadMetalSoftboxes)
            {
                result.a = 1f;
                return result;
            }
            return LimitReflectionPeak(result, SoftReflectionPeak);
        }

        public static bool UsesSoftSpinnerLighting(string modelId)
        {
            return string.Equals(
                    modelId,
                    ProductCatalog.PointedThreeBladeModelId,
                    StringComparison.Ordinal)
                || string.Equals(
                    modelId,
                    ProductCatalog.MetalThreeBladeModelId,
                    StringComparison.Ordinal)
                || string.Equals(
                    modelId,
                    ProductCatalog.GoldFourWingModelId,
                    StringComparison.Ordinal)
                || string.Equals(
                    modelId,
                    ProductCatalog.GraphiteTwoLobeModelId,
                    StringComparison.Ordinal);
        }

        /// <summary>
        /// Backdrop glow energy behind the toy. The slide tile is not a soft
        /// spinner but shares the canyon, so it must not run the glow at 1.0
        /// while the spinners run 0.38: that 2.6x was the bright haze under the
        /// slide (user 2026-09-09). The fan card keeps its own pedestal glow.
        /// </summary>
        public static float ResolveEnvironmentGlowScale(string modelId)
        {
            if (UsesSoftSpinnerLighting(modelId))
            {
                return SoftEnvironmentGlowScale * ResolveSoftSpinnerLightTrim(modelId);
            }
            if (string.Equals(
                    modelId,
                    ProductCatalog.MagneticSlideTileModelId,
                    StringComparison.Ordinal))
            {
                return SoftEnvironmentGlowScale;
            }
            return 1f;
        }

        public static float ResolveSoftSpinnerLightTrim(string modelId)
        {
            if (string.Equals(
                    modelId,
                    ProductCatalog.PointedThreeBladeModelId,
                    StringComparison.Ordinal))
            {
                return 0.58f;
            }
            if (string.Equals(
                    modelId,
                    ProductCatalog.MetalThreeBladeModelId,
                    StringComparison.Ordinal))
            {
                return 1.00f;
            }
            if (string.Equals(
                    modelId,
                    ProductCatalog.GoldFourWingModelId,
                    StringComparison.Ordinal))
            {
                return 0.70f;
            }
            return 1f;
        }

        public static Color LimitReflectionPeak(Color source, float peakLimit)
        {
            float limit = Mathf.Max(0.001f, peakLimit);
            float peak = Mathf.Max(source.r, Mathf.Max(source.g, source.b));
            if (peak > limit)
            {
                float scale = limit / peak;
                source.r *= scale;
                source.g *= scale;
                source.b *= scale;
            }
            source.a = 1f;
            return source;
        }

        private static Vector3 CubeDirection(
            CubemapFace face,
            int x,
            int y,
            int size)
        {
            float u = (x + 0.5f) / size * 2f - 1f;
            float v = (y + 0.5f) / size * 2f - 1f;
            switch (face)
            {
                case CubemapFace.PositiveX: return new Vector3(1f, -v, -u).normalized;
                case CubemapFace.NegativeX: return new Vector3(-1f, -v, u).normalized;
                case CubemapFace.PositiveY: return new Vector3(u, 1f, v).normalized;
                case CubemapFace.NegativeY: return new Vector3(u, -1f, -v).normalized;
                case CubemapFace.PositiveZ: return new Vector3(u, -v, 1f).normalized;
                default: return new Vector3(-u, -v, -1f).normalized;
            }
        }

        private void ApplyAuthoredLights(
            SpinnerEnvironmentProfile profile,
            SpinnerEnvironmentPalette palette)
        {
            authoredLights.Clear();
            authoredLightIntensities.Clear();
            Light[] lights = FindObjectsByType<Light>(
                FindObjectsInactive.Exclude,
                FindObjectsSortMode.None);
            for (int presetIndex = 0; presetIndex < profile.Lights.Count; presetIndex++)
            {
                SpinnerEnvironmentLightPreset preset = profile.Lights[presetIndex];
                for (int lightIndex = 0; lightIndex < lights.Length; lightIndex++)
                {
                    Light light = lights[lightIndex];
                    if (light == null
                        || !string.Equals(
                            light.name,
                            preset.ObjectName,
                            StringComparison.Ordinal))
                    {
                        continue;
                    }

                    Color sampledColor = presetIndex == 0
                        ? palette.Key
                        : presetIndex == 1
                            ? palette.Fill
                            : palette.Sky;
                    light.useColorTemperature = false;
                    float sampledLightMix = fanCardLightingActive
                        ? FanCardSourceColorSampleMix
                        : 0.82f;
                    light.color = NormalizeLightColor(Color.Lerp(
                        preset.Color,
                        NormalizeLightColor(sampledColor),
                        sampledLightMix));
                    if (fanCardLightingActive)
                    {
                        Quaternion keyRotation = ResolveFanCardKeyRotation(
                            palette.KeyViewport);
                        if (presetIndex == 0)
                        {
                            light.transform.rotation = keyRotation;
                        }
                        else if (presetIndex == 1)
                        {
                            Vector3 keyEuler = keyRotation.eulerAngles;
                            light.transform.rotation = Quaternion.Euler(
                                Mathf.Clamp(keyEuler.x - 12f, 40f, 52f),
                                keyEuler.y + 168f,
                                0f);
                        }
                    }
                    float softenedIntensity = preset.Intensity
                        * (softSpinnerLightingActive
                            ? SoftDirectLightScale * softSpinnerLightTrim
                            : 1f);
                    if (fanCardLightingActive)
                    {
                        softenedIntensity *= presetIndex == 0
                            ? FanCardKeyIntensityScale
                            : presetIndex == 1
                                ? FanCardFillIntensityScale
                                : 1f;
                    }
                    light.intensity = softenedIntensity;
                    authoredLights.Add(light);
                    authoredLightIntensities.Add(softenedIntensity);
                    break;
                }
            }

            if (fanCardLightingActive)
            {
                for (int lightIndex = 0; lightIndex < lights.Length; lightIndex++)
                {
                    Light lift = lights[lightIndex];
                    if (lift != null
                        && string.Equals(
                            lift.name,
                            "SoftFrontLift",
                            StringComparison.Ordinal))
                    {
                        lift.intensity = 0.10f * FanCardSoftFrontLiftScale;
                        break;
                    }
                }
            }
        }

        private void ApplyVisibilityFill(SpinnerEnvironmentPalette palette)
        {
            if (visibilityFillLight == null)
            {
                GameObject lightObject = new GameObject(VisibilityFillName);
                lightObject.transform.SetParent(transform, false);
                visibilityFillLight = lightObject.AddComponent<Light>();
            }

            // A restrained camera-side fill keeps the product readable even
            // when a dark replacement plate places its brightest area behind
            // the authored key. Its color and strength still come from the
            // selected image rather than a product-specific hard-coded hue.
            float ambientValue = Luminance(palette.Equator);
            visibilityFillLight.gameObject.SetActive(true);
            visibilityFillLight.transform.SetPositionAndRotation(
                transform.position,
                transform.rotation);
            visibilityFillLight.type = LightType.Directional;
            visibilityFillLight.color = NormalizeLightColor(Color.Lerp(
                palette.Equator,
                palette.Key,
                0.24f));
            visibilityFillLight.intensity = Mathf.Lerp(
                0.30f,
                0.18f,
                Mathf.InverseLerp(0.035f, 0.14f, ambientValue))
                * (softSpinnerLightingActive
                    ? SoftVisibilityFillScale * softSpinnerLightTrim
                    : 1f)
                * (fanCardLightingActive ? FanCardVisibilityFillScale : 1f);
            visibilityFillBaseIntensity = visibilityFillLight.intensity;
            visibilityFillLight.shadows = LightShadows.None;
            visibilityFillLight.renderMode = LightRenderMode.Auto;
        }

        private void ApplyModelAndStageResponse(
            SpinnerGroundingStage groundingStage,
            SpinnerEnvironmentPalette palette)
        {
            this.groundingStage = groundingStage;
            if (groundingStage == null)
            {
                if (modelBounceLight != null)
                {
                    modelBounceLight.gameObject.SetActive(false);
                }
                return;
            }

            modelAccent = ResolveModelAccent(groundingStage.ModelRenderers);
            Color.RGBToHSV(modelAccent, out _, out float saturation, out _);
            float bounceStrength = Mathf.InverseLerp(0.04f, 0.58f, saturation);
            modelColorfulness = bounceStrength;
            groundingStage.SetLightingColors(
                palette.Ground * 1.8f + palette.Equator * 0.45f,
                modelAccent,
                bounceStrength);

            if (modelBounceLight == null)
            {
                GameObject lightObject = new GameObject(BounceLightName);
                lightObject.transform.SetParent(transform, false);
                modelBounceLight = lightObject.AddComponent<Light>();
            }
            Bounds bounds = groundingStage.ModelBounds;
            float planarSize = Mathf.Max(bounds.size.x, bounds.size.z);
            planarModelSize = planarSize;
            if (fanCardLightingActive)
            {
                // The baked canyon has no visible practical at the support
                // plane. This point light made an unexplained triangle on the
                // front bevel, so the fan uses only its top key and ambient
                // environment response.
                modelBounceLight.gameObject.SetActive(false);
                baseBounceIntensity = 0f;
            }
            else
            {
                modelBounceLight.gameObject.SetActive(true);
                modelBounceLight.transform.position = new Vector3(
                    bounds.center.x,
                    groundingStage.SupportTopY
                        + Mathf.Max(bounds.size.y * 0.04f, planarSize * 0.005f),
                    bounds.center.z);
                baseBouncePosition = modelBounceLight.transform.position;
                modelBounceLight.type = LightType.Point;
                modelBounceLight.color = modelAccent;
                modelBounceLight.intensity = Mathf.Lerp(
                    0.065f,
                    0.26f,
                    bounceStrength) * (softSpinnerLightingActive
                        ? SoftModelBounceScale * softSpinnerLightTrim
                        : 1f);
                baseBounceIntensity = modelBounceLight.intensity;
                modelBounceLight.range = Mathf.Max(0.01f, planarSize * 0.72f);
                modelBounceLight.shadows = LightShadows.None;
                modelBounceLight.renderMode = LightRenderMode.Auto;
            }

            for (int index = 0; index < groundingStage.ModelRenderers.Count; index++)
            {
                Renderer renderer = groundingStage.ModelRenderers[index];
                if (renderer != null)
                {
                    renderer.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
                }
            }
            if (softSpinnerLightingActive)
            {
                ApplySoftMaterialResponse(groundingStage.ModelRenderers);
            }
        }

        private static void ApplySoftMaterialResponse(
            IReadOnlyList<Renderer> renderers)
        {
            for (int rendererIndex = 0; rendererIndex < renderers.Count; rendererIndex++)
            {
                Renderer renderer = renderers[rendererIndex];
                if (renderer == null)
                {
                    continue;
                }

                Material[] materials = renderer.sharedMaterials;
                for (int materialIndex = 0; materialIndex < materials.Length; materialIndex++)
                {
                    Material material = materials[materialIndex];
                    if (!UsesSoftMaterialResponse(material))
                    {
                        continue;
                    }

                    var properties = new MaterialPropertyBlock();
                    renderer.GetPropertyBlock(properties, materialIndex);
                    Color source = material.HasProperty("_BaseColor")
                        ? material.GetColor("_BaseColor")
                        : material.GetColor("_Color");
                    Color softened = ResolveSoftMaterialColor(source);
                    if (material.HasProperty("_BaseColor"))
                    {
                        properties.SetColor("_BaseColor", softened);
                    }
                    if (material.HasProperty("_Color"))
                    {
                        properties.SetColor("_Color", softened);
                    }
                    if (material.HasProperty("_Smoothness"))
                    {
                        properties.SetFloat(
                            "_Smoothness",
                            Mathf.Min(
                                material.GetFloat("_Smoothness"),
                                SoftBrightMetalSmoothnessCap));
                    }
                    renderer.SetPropertyBlock(properties, materialIndex);
                }
            }
        }

        public static bool UsesSoftMaterialResponse(Material material)
        {
            if (material == null
                || !material.HasProperty("_Metallic")
                || material.GetFloat("_Metallic") < 0.5f
                || (!material.HasProperty("_BaseColor")
                    && !material.HasProperty("_Color")))
            {
                return false;
            }

            Color color = material.HasProperty("_BaseColor")
                ? material.GetColor("_BaseColor")
                : material.GetColor("_Color");
            return color.maxColorComponent >= SoftBrightMetalThreshold;
        }

        public static Color ResolveSoftMaterialColor(Color source)
        {
            float alpha = source.a;
            source *= SoftBrightMetalAlbedoScale;
            source.a = alpha;
            return source;
        }

        private void EnsureViewHighlight()
        {
            if (viewHighlightLight != null)
            {
                return;
            }

            GameObject lightObject = new GameObject(ViewHighlightName);
            lightObject.transform.SetParent(transform, false);
            viewHighlightLight = lightObject.AddComponent<Light>();
            viewHighlightLight.type = LightType.Point;
            viewHighlightLight.range = Mathf.Max(0.01f, planarModelSize * 1.20f);
            viewHighlightLight.shadows = LightShadows.None;
            viewHighlightLight.renderMode = LightRenderMode.Auto;
        }

        private static SpinnerEnvironmentPalette StabilizePalette(
            SpinnerEnvironmentPalette sampled,
            SpinnerEnvironmentPalette fallback,
            bool retainFanChroma = false)
        {
            float ambientSat = retainFanChroma ? FanCardAmbientSaturationCap : 0.30f;
            float lightSat = retainFanChroma ? FanCardLightSaturationCap : 0.42f;
            return new SpinnerEnvironmentPalette(
                StabilizeAmbient(sampled.Sky, fallback.Sky, 0.075f, 0.24f, ambientSat),
                StabilizeAmbient(sampled.Equator, fallback.Equator, 0.035f, 0.14f, ambientSat),
                StabilizeAmbient(sampled.Ground, fallback.Ground, 0.012f, 0.07f, ambientSat),
                NormalizeLightColor(sampled.Key, lightSat),
                NormalizeLightColor(sampled.Fill, lightSat),
                sampled.KeyViewport);
        }

        private static Color StabilizeAmbient(
            Color sampled,
            Color fallback,
            float minimumValue,
            float maximumValue,
            float saturationCap = 0.30f)
        {
            Color blended = Color.Lerp(fallback.linear, sampled, 0.72f);
            Color.RGBToHSV(blended, out float hue, out float saturation, out float value);
            saturation = Mathf.Min(saturation, saturationCap);
            value = Mathf.Clamp(value, minimumValue, maximumValue);
            Color result = Color.HSVToRGB(hue, saturation, value);
            result.a = 1f;
            return result;
        }

        public static Color RetainAmbientLuminance(Color source)
        {
            return RetainAmbientLuminance(source, AmbientChromaRetention);
        }

        public static Color RetainAmbientLuminance(Color source, float chromaRetention)
        {
            float luma = Luminance(source);
            Color grey = new Color(luma, luma, luma, 1f);
            Color result = Color.Lerp(grey, source, Mathf.Clamp01(chromaRetention));
            result.a = 1f;
            return result;
        }

        private float ResolveEnvironmentColorCoupling()
        {
            return fanCardLightingActive
                ? FanCardEnvironmentColorCoupling
                : EnvironmentColorCoupling;
        }

        private static Color NormalizeLightColor(Color source)
        {
            return NormalizeLightColor(source, 0.42f);
        }

        private static Color NormalizeLightColor(Color source, float saturationCap)
        {
            Color.RGBToHSV(source, out float hue, out float saturation, out float value);
            if (value <= 0.0001f)
            {
                return Color.white;
            }
            saturation = Mathf.Min(saturation, saturationCap);
            Color result = Color.HSVToRGB(hue, saturation, 1f);
            result.a = 1f;
            return result;
        }

        private static Color AverageBand(
            Color[] pixels,
            int width,
            int height,
            float minimumY,
            float maximumY)
        {
            return AverageRect(pixels, width, height, 0f, 1f, minimumY, maximumY);
        }

        private static Color AverageRect(
            Color[] pixels,
            int width,
            int height,
            float minimumX,
            float maximumX,
            float minimumY,
            float maximumY)
        {
            int startX = Mathf.Clamp(Mathf.FloorToInt(minimumX * width), 0, width - 1);
            int endX = Mathf.Clamp(Mathf.CeilToInt(maximumX * width), startX + 1, width);
            int startY = Mathf.Clamp(Mathf.FloorToInt(minimumY * height), 0, height - 1);
            int endY = Mathf.Clamp(Mathf.CeilToInt(maximumY * height), startY + 1, height);
            Color sum = Color.black;
            float weightSum = 0f;
            for (int y = startY; y < endY; y++)
            {
                for (int x = startX; x < endX; x++)
                {
                    Color color = pixels[y * width + x];
                    float weight = 0.08f + Mathf.Sqrt(Mathf.Max(0f, Luminance(color)));
                    sum += color * weight;
                    weightSum += weight;
                }
            }
            Color average = weightSum > 0f ? sum / weightSum : Color.black;
            average.a = 1f;
            return average;
        }

        private static float Luminance(Color color)
        {
            return color.r * 0.2126f + color.g * 0.7152f + color.b * 0.0722f;
        }

        private void OnDestroy()
        {
            Shader.SetGlobalVector(FanCardReflectionTiltShaderId, Vector4.zero);
            DestroyRuntimeObject(generatedReflection);
            if (modelBounceLight != null)
            {
                DestroyRuntimeObject(modelBounceLight.gameObject);
            }
            if (visibilityFillLight != null)
            {
                DestroyRuntimeObject(visibilityFillLight.gameObject);
            }
            if (viewHighlightLight != null)
            {
                DestroyRuntimeObject(viewHighlightLight.gameObject);
            }
        }

        private static void DestroyRuntimeObject(UnityEngine.Object value)
        {
            if (value == null)
            {
                return;
            }

            if (Application.isPlaying)
            {
                Destroy(value);
            }
            else
            {
                DestroyImmediate(value);
            }
        }
    }
}
