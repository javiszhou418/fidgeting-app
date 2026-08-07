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
        private readonly List<Light> authoredLights = new();
        private readonly List<float> authoredLightIntensities = new();

        public SpinnerEnvironmentPalette CurrentPalette { get; private set; }
        public Cubemap GeneratedReflection => generatedReflection;
        public Light ModelBounceLight => modelBounceLight;
        public Light VisibilityFillLight => visibilityFillLight;
        public Light ViewHighlightLight => viewHighlightLight;

        public void Configure(
            Texture background,
            SpinnerEnvironmentProfile profile,
            SpinnerGroundingStage groundingStage)
        {
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
                    profile.BackgroundResourcePath,
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
            environmentPresenter?.SetEnvironmentGlow(
                smoothedLeftGlow * breathing,
                smoothedRightGlow * breathing,
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
                modelColorfulness);
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
            RenderSettings.ambientSkyColor = palette.Sky;
            RenderSettings.ambientEquatorColor = palette.Equator;
            RenderSettings.ambientGroundColor = palette.Ground;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            baseReflectionIntensity = profile.ReflectionIntensity;
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
                            SynthesizeReflection(direction, palette);
                    }
                }
                cubemap.SetPixels(colors, face);
            }
            cubemap.Apply(true, true);
            return cubemap;
        }

        private static Color SynthesizeReflection(
            Vector3 direction,
            SpinnerEnvironmentPalette palette)
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
            Color result = baseColor * 2.2f
                + NormalizeLightColor(palette.Key) * keyHighlight * 0.72f
                + NormalizeLightColor(palette.Fill) * fillHighlight;
            result.a = 1f;
            return result;
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
                    light.intensity = preset.Intensity;
                    authoredLights.Add(light);
                    authoredLightIntensities.Add(preset.Intensity);
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
                Mathf.InverseLerp(0.035f, 0.14f, ambientValue));
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
            modelBounceLight.intensity = Mathf.Lerp(0.065f, 0.26f, bounceStrength);
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
