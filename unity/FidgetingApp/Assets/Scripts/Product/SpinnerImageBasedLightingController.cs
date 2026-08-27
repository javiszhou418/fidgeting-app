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
        public const float MagneticSlideSoftboxIntensity = 0.26f;
        public const float MagneticSlideReflectionBaseScale = 1.00f;
        public const float MagneticSlideOpposingStripIntensity = 0.18f;
        public const float MagneticSlideSoftboxHorizontalCore = 0.22f;
        public const float MagneticSlideSoftboxHorizontalEdge = 0.88f;
        public const float MagneticSlideSoftboxVerticalCore = 0.18f;
        public const float MagneticSlideSoftboxVerticalEdge = 0.78f;
        public const float FanCardSoftboxIntensity = 0.22f;
        public const float FanCardReflectionBaseScale = 0.92f;
        public const float FanCardOpposingStripIntensity = 0.10f;
        public const float FanCardSoftboxHorizontalCore = 0.22f;
        public const float FanCardSoftboxHorizontalEdge = 0.88f;
        public const float FanCardSoftboxVerticalCore = 0.18f;
        public const float FanCardSoftboxVerticalEdge = 0.78f;
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
        public const float SoftBrightMetalThreshold = 0.55f;
        public const float SoftBrightMetalAlbedoScale = 0.68f;
        public const float SoftBrightMetalSmoothnessCap = 0.70f;

        // Every product scene currently uses the same approved canyon plate.
        // A GPU ReadPixels during each page selection forces a render-thread
        // synchronization and presents as a visible swipe hitch on iPhone.
        // Cache by the catalog resource path so the plate is sampled once per
        // app session while each model still applies its own authored fallback
        // and lighting scales.
        private static readonly Dictionary<string, SpinnerEnvironmentPalette>
            CachedBackgroundPalettes = new();

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
        private bool softSpinnerLightingActive;
        private float softSpinnerLightTrim = 1f;
        private readonly List<Light> authoredLights = new();
        private readonly List<float> authoredLightIntensities = new();

        public SpinnerEnvironmentPalette CurrentPalette { get; private set; }
        public Cubemap GeneratedReflection => generatedReflection;
        public Light ModelBounceLight => modelBounceLight;
        public Light VisibilityFillLight => visibilityFillLight;
        public Light ViewHighlightLight => viewHighlightLight;
        public bool SoftSpinnerLightingActive => softSpinnerLightingActive;

        public void Configure(
            Texture background,
            SpinnerEnvironmentProfile profile,
            SpinnerGroundingStage groundingStage,
            string backgroundCacheKey = null)
        {
            softSpinnerLightingActive = UsesSoftSpinnerLighting(profile.ModelId);
            softSpinnerLightTrim = ResolveSoftSpinnerLightTrim(profile.ModelId);
            SpinnerEnvironmentPalette fallback = new SpinnerEnvironmentPalette(
                profile.AmbientSky,
                profile.AmbientEquator,
                profile.AmbientGround,
                profile.Lights.Count > 0 ? profile.Lights[0].Color : Color.white,
                profile.Lights.Count > 1 ? profile.Lights[1].Color : profile.AmbientEquator,
                new Vector2(0.36f, 0.76f));
            libraryLightScale = Mathf.Clamp01(profile.LibraryLightScale);
            libraryReflectionScale = Mathf.Clamp01(profile.LibraryReflectionScale);

            CurrentPalette = TryResolvePalette(
                    background,
                    string.IsNullOrEmpty(backgroundCacheKey)
                        ? profile.BackgroundResourcePath
                        : backgroundCacheKey,
                    out SpinnerEnvironmentPalette sampled)
                ? StabilizePalette(sampled, fallback)
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
                out smoothedLeftGlow,
                out smoothedRightGlow);
            SetLibraryPreviewActive(true);
            SetViewResponse(Vector2.zero, false, 0f, 0f, 0f);
        }

        public void SetLibraryPreviewActive(bool active)
        {
            libraryPreviewActive = active;
            presentationLightScale = active ? libraryLightScale : 1f;
            for (int index = 0; index < authoredLights.Count; index++)
            {
                Light light = authoredLights[index];
                if (light != null)
                {
                    light.intensity = authoredLightIntensities[index]
                        * presentationLightScale;
                }
            }

            if (visibilityFillLight != null)
            {
                float visibilityScale = Mathf.Lerp(
                    0.28f,
                    1f,
                    libraryLightScale);
                visibilityFillLight.intensity = visibilityFillBaseIntensity
                    * (active ? visibilityScale : 1f);
            }
            if (modelBounceLight != null)
            {
                modelBounceLight.intensity = baseBounceIntensity
                    * presentationLightScale;
            }
            RenderSettings.reflectionIntensity = baseReflectionIntensity
                * (active ? libraryReflectionScale : 1f);
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
            float environmentGlowScale = softSpinnerLightingActive
                ? SoftEnvironmentGlowScale * softSpinnerLightTrim
                : 1f;
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
                * presentationLightScale
                * breathing
                * (libraryPreviewActive ? 1.28f : 1f);

            EnsureViewHighlight();
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
                smoothedLeftGlow,
                smoothedRightGlow,
                Mathf.Clamp01(0.5f + opticalTilt.x * 0.5f)));
            float highlightIntensity = Mathf.Lerp(
                0.045f,
                0.16f,
                modelColorfulness) * (softSpinnerLightingActive
                    ? SoftViewHighlightScale * softSpinnerLightTrim
                    : 1f);
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
            float horizontal = Mathf.Clamp01(0.5f + normalizedTilt.x * 0.5f);
            Color leftEnvironment = Color.Lerp(palette.Key, palette.Fill, horizontal);
            Color rightEnvironment = Color.Lerp(palette.Fill, palette.Key, horizontal);
            left = NormalizeLightColor(Color.Lerp(modelColor, leftEnvironment, 0.34f));
            right = NormalizeLightColor(Color.Lerp(modelColor, rightEnvironment, 0.34f));
        }

        public static SpinnerEnvironmentPalette AnalyzePixels(
            Color[] pixels,
            int width,
            int height)
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
                    float score = Luminance(tile);
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
                    SampleHeight);
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
            out SpinnerEnvironmentPalette palette)
        {
            string cacheKey = string.IsNullOrEmpty(resourcePath)
                ? background != null ? background.name : string.Empty
                : resourcePath;
            if (!string.IsNullOrEmpty(cacheKey)
                && CachedBackgroundPalettes.TryGetValue(cacheKey, out palette))
            {
                return true;
            }

            if (!TryReadPalette(background, out palette))
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
            RenderSettings.ambientSkyColor = palette.Sky * ambientScale;
            RenderSettings.ambientEquatorColor = palette.Equator * ambientScale;
            RenderSettings.ambientGroundColor = palette.Ground * ambientScale;
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
            bool useBroadMetalSoftboxes = isFanCard || isMagneticSlide;
            float reflectionBaseScale = isMagneticSlide
                ? MagneticSlideReflectionBaseScale
                : isFanCard
                    ? FanCardReflectionBaseScale
                    : 1.28f;
            float broadPanelIntensity = isMagneticSlide
                ? MagneticSlideSoftboxIntensity
                : isFanCard
                    ? FanCardSoftboxIntensity
                    : 0.86f;
            float opposingStripIntensity = isMagneticSlide
                ? MagneticSlideOpposingStripIntensity
                : isFanCard
                    ? FanCardOpposingStripIntensity
                    : 0.24f;
            float panelHorizontalCore = isMagneticSlide
                ? MagneticSlideSoftboxHorizontalCore
                : isFanCard
                    ? FanCardSoftboxHorizontalCore
                    : 0.28f;
            float panelHorizontalEdge = isMagneticSlide
                ? MagneticSlideSoftboxHorizontalEdge
                : isFanCard
                    ? FanCardSoftboxHorizontalEdge
                    : 0.56f;
            float panelVerticalCore = isMagneticSlide
                ? MagneticSlideSoftboxVerticalCore
                : isFanCard
                    ? FanCardSoftboxVerticalCore
                    : 0.20f;
            float panelVerticalEdge = isMagneticSlide
                ? MagneticSlideSoftboxVerticalEdge
                : isFanCard
                    ? FanCardSoftboxVerticalEdge
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
                                reflectionBaseScale,
                                broadPanelIntensity,
                                opposingStripIntensity,
                                panelHorizontalCore,
                                panelHorizontalEdge,
                                panelVerticalCore,
                                panelVerticalEdge);
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
            float reflectionBaseScale,
            float broadPanelIntensity,
            float opposingStripIntensity,
            float panelHorizontalCore,
            float panelHorizontalEdge,
            float panelVerticalCore,
            float panelVerticalEdge)
        {
            float vertical = direction.y;
            Color baseColor = vertical >= 0f
                ? Color.Lerp(palette.Equator, palette.Sky, vertical)
                : Color.Lerp(palette.Equator, palette.Ground, -vertical);
            Vector3 keyDirection = new Vector3(
                palette.KeyViewport.x * 2f - 1f,
                palette.KeyViewport.y * 2f - 1f,
                -0.65f).normalized;
            float keyHighlight = Mathf.Pow(
                Mathf.Max(0f, Vector3.Dot(direction, keyDirection)),
                12f);
            float fillHighlight = Mathf.Pow(
                Mathf.Max(0f, Vector3.Dot(direction, -keyDirection)),
                5f) * 0.18f;
            Color result;
            if (useBroadMetalSoftboxes)
            {
                // Chrome only reads as chrome when it reflects shapes, not
                // point-like lamps. Magnetic slide keeps a readable panel.
                // The bead-blasted fan card uses the same shape at much
                // lower energy so faces do not read as digital studio metal.
                // This remains environment lighting: no geometry, mechanics,
                // or product interaction state is touched.
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
                result = baseColor * reflectionBaseScale
                    + NormalizeLightColor(palette.Key) * keyHighlight * 0.12f
                    + NormalizeLightColor(palette.Fill) * fillHighlight * 0.10f
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
                return 0.64f;
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
                    light.color = NormalizeLightColor(Color.Lerp(
                        preset.Color,
                        NormalizeLightColor(sampledColor),
                        0.82f));
                    float softenedIntensity = preset.Intensity
                        * (softSpinnerLightingActive
                            ? SoftDirectLightScale * softSpinnerLightTrim
                            : 1f);
                    light.intensity = softenedIntensity;
                    authoredLights.Add(light);
                    authoredLightIntensities.Add(softenedIntensity);
                    break;
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
                    : 1f);
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
            SpinnerEnvironmentPalette fallback)
        {
            return new SpinnerEnvironmentPalette(
                StabilizeAmbient(sampled.Sky, fallback.Sky, 0.075f, 0.24f),
                StabilizeAmbient(sampled.Equator, fallback.Equator, 0.035f, 0.14f),
                StabilizeAmbient(sampled.Ground, fallback.Ground, 0.012f, 0.07f),
                NormalizeLightColor(sampled.Key),
                NormalizeLightColor(sampled.Fill),
                sampled.KeyViewport);
        }

        private static Color StabilizeAmbient(
            Color sampled,
            Color fallback,
            float minimumValue,
            float maximumValue)
        {
            Color blended = Color.Lerp(fallback.linear, sampled, 0.72f);
            Color.RGBToHSV(blended, out float hue, out float saturation, out float value);
            saturation = Mathf.Min(saturation, 0.30f);
            value = Mathf.Clamp(value, minimumValue, maximumValue);
            Color result = Color.HSVToRGB(hue, saturation, value);
            result.a = 1f;
            return result;
        }

        private static Color NormalizeLightColor(Color source)
        {
            Color.RGBToHSV(source, out float hue, out float saturation, out float value);
            if (value <= 0.0001f)
            {
                return Color.white;
            }
            saturation = Mathf.Min(saturation, 0.42f);
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
