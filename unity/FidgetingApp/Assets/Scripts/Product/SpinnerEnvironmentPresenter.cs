using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Product
{
    public readonly struct SpinnerEnvironmentLightPreset
    {
        public SpinnerEnvironmentLightPreset(string objectName, Color color, float intensity)
        {
            ObjectName = objectName;
            Color = color;
            Intensity = intensity;
        }

        public string ObjectName { get; }
        public Color Color { get; }
        public float Intensity { get; }
    }

    public readonly struct SpinnerEnvironmentProfile
    {
        public SpinnerEnvironmentProfile(
            string modelId,
            string scenePath,
            string backgroundResourcePath,
            int sourceWidth,
            int sourceHeight,
            int importMaxTextureSize,
            float coverOverscan,
            float saturation,
            bool layeredParallax,
            Color ambientSky,
            Color ambientEquator,
            Color ambientGround,
            float reflectionIntensity,
            float libraryLightScale,
            float libraryReflectionScale,
            SpinnerGroundingStageShape stageShape,
            float stageScale,
            float stageThicknessRatio,
            bool usesBakedSupportSurface,
            string legacyBackdropObjectName,
            params SpinnerEnvironmentLightPreset[] lights)
        {
            ModelId = modelId;
            ScenePath = scenePath;
            BackgroundResourcePath = backgroundResourcePath;
            SourceWidth = sourceWidth;
            SourceHeight = sourceHeight;
            ImportMaxTextureSize = importMaxTextureSize;
            CoverOverscan = coverOverscan;
            Saturation = saturation;
            LayeredParallax = layeredParallax;
            AmbientSky = ambientSky;
            AmbientEquator = ambientEquator;
            AmbientGround = ambientGround;
            ReflectionIntensity = reflectionIntensity;
            LibraryLightScale = libraryLightScale;
            LibraryReflectionScale = libraryReflectionScale;
            StageShape = stageShape;
            StageScale = stageScale;
            StageThicknessRatio = stageThicknessRatio;
            UsesBakedSupportSurface = usesBakedSupportSurface;
            LegacyBackdropObjectName = legacyBackdropObjectName;
            Lights = lights ?? Array.Empty<SpinnerEnvironmentLightPreset>();
        }

        public string ModelId { get; }
        public string ScenePath { get; }
        public string BackgroundResourcePath { get; }
        public string TextureAssetPath =>
            $"Assets/Resources/{BackgroundResourcePath}.png";
        public int SourceWidth { get; }
        public int SourceHeight { get; }
        public int ImportMaxTextureSize { get; }
        public float CoverOverscan { get; }
        public float Saturation { get; }
        public bool LayeredParallax { get; }
        public Color AmbientSky { get; }
        public Color AmbientEquator { get; }
        public Color AmbientGround { get; }
        public float ReflectionIntensity { get; }
        public float LibraryLightScale { get; }
        public float LibraryReflectionScale { get; }
        public SpinnerGroundingStageShape StageShape { get; }
        public float StageScale { get; }
        public float StageThicknessRatio { get; }
        public bool UsesBakedSupportSurface { get; }
        public string LegacyBackdropObjectName { get; }
        public IReadOnlyList<SpinnerEnvironmentLightPreset> Lights { get; }
    }

    /// <summary>
    /// Single source of truth for the product-scene environment plates and
    /// presentation-only lighting. These values never write rotor motion,
    /// interaction, detent, or Haptic state.
    /// </summary>
    public static class SpinnerEnvironmentCatalog
    {
        public const string PointedScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        public const string BlueScenePath = "Assets/Scenes/FidgetSpinnerDemo.unity";
        public const string MetalScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity";
        public const string ImportedScenePath =
            "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity";
        public const string TwoLobeScenePath =
            "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity";
        public const string EdcScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        public const string FanCardScenePath =
            "Assets/_FanCard/Scenes/MagneticFanCard.unity";
        public const string MaterialResourcePath =
            "EnvironmentBackgrounds/EnvironmentBackgroundMaterial";
        public const string ParallaxMaterialResourcePath =
            "EnvironmentBackgrounds/EnvironmentParallaxMaterial";
        public const string StarfieldMaterialResourcePath =
            "EnvironmentBackgrounds/EnvironmentStarfieldMaterial";
        public const string UnifiedBackgroundResourcePath =
            "EnvironmentBackgrounds/canyon-unified-ledgestone-v1-2x";

        private static readonly SpinnerEnvironmentProfile[] profiles =
        {
            new SpinnerEnvironmentProfile(
                "pointed-three-blade",
                PointedScenePath,
                UnifiedBackgroundResourcePath,
                1882,
                3344,
                4096,
                1.08f,
                0.68f,
                false,
                new Color(0.135f, 0.130f, 0.125f),
                new Color(0.058f, 0.055f, 0.052f),
                new Color(0.018f, 0.017f, 0.016f),
                0.66f,
                0.48f,
                0.42f,
                SpinnerGroundingStageShape.SoftSquare,
                1.32f,
                0.10f,
                true,
                string.Empty,
                new SpinnerEnvironmentLightPreset(
                    "Key_5000K",
                    new Color(0.91f, 0.90f, 1.00f),
                    0.50f),
                new SpinnerEnvironmentLightPreset(
                    "WarmRim_3200K",
                    new Color(1.00f, 0.56f, 0.40f),
                    0.42f),
                new SpinnerEnvironmentLightPreset(
                    "CoolFill_6500K",
                    new Color(0.40f, 0.60f, 1.00f),
                    0.18f)),
            new SpinnerEnvironmentProfile(
                "metal-three-blade",
                MetalScenePath,
                UnifiedBackgroundResourcePath,
                1882,
                3344,
                4096,
                1.08f,
                0.68f,
                false,
                new Color(0.135f, 0.130f, 0.125f),
                new Color(0.058f, 0.055f, 0.052f),
                new Color(0.018f, 0.017f, 0.016f),
                0.66f,
                0.48f,
                0.42f,
                SpinnerGroundingStageShape.SoftSquare,
                1.32f,
                0.10f,
                true,
                string.Empty,
                new SpinnerEnvironmentLightPreset(
                    "Key_5000K",
                    new Color(0.91f, 0.90f, 1.00f),
                    0.50f),
                new SpinnerEnvironmentLightPreset(
                    "WarmRim_3200K",
                    new Color(1.00f, 0.56f, 0.40f),
                    0.42f),
                new SpinnerEnvironmentLightPreset(
                    "CoolFill_6500K",
                    new Color(0.40f, 0.60f, 1.00f),
                    0.18f)),
            new SpinnerEnvironmentProfile(
                "gold-four-wing",
                ImportedScenePath,
                UnifiedBackgroundResourcePath,
                1882,
                3344,
                4096,
                1.08f,
                0.68f,
                false,
                new Color(0.150f, 0.155f, 0.158f),
                new Color(0.062f, 0.064f, 0.066f),
                new Color(0.017f, 0.018f, 0.019f),
                0.92f,
                0.48f,
                0.45f,
                SpinnerGroundingStageShape.Round,
                1.35f,
                0.085f,
                true,
                string.Empty,
                new SpinnerEnvironmentLightPreset(
                    "Key_5000K",
                    new Color(0.84f, 0.91f, 1.00f),
                    0.64f),
                new SpinnerEnvironmentLightPreset(
                    "WarmRim_3200K",
                    new Color(1.00f, 0.66f, 0.48f),
                    0.22f),
                new SpinnerEnvironmentLightPreset(
                    "CoolFill_6500K",
                    new Color(0.44f, 0.68f, 1.00f),
                    0.48f)),
            new SpinnerEnvironmentProfile(
                "graphite-two-lobe",
                TwoLobeScenePath,
                UnifiedBackgroundResourcePath,
                1882,
                3344,
                4096,
                1.08f,
                0.68f,
                false,
                new Color(0.125f, 0.128f, 0.120f),
                new Color(0.052f, 0.054f, 0.050f),
                new Color(0.014f, 0.015f, 0.014f),
                0.70f,
                0.70f,
                0.90f,
                SpinnerGroundingStageShape.Oblong,
                1.34f,
                0.12f,
                true,
                "WarmDefocusedBackdrop",
                new SpinnerEnvironmentLightPreset(
                    "LargeSoftAreaKey_UpperLeft",
                    new Color(0.76f, 0.84f, 0.82f),
                    0.86f)),
            new SpinnerEnvironmentProfile(
                "magnetic-slide-tile",
                EdcScenePath,
                UnifiedBackgroundResourcePath,
                1882,
                3344,
                4096,
                1.08f,
                0.68f,
                false,
                new Color(0.122f, 0.126f, 0.120f),
                new Color(0.050f, 0.052f, 0.049f),
                new Color(0.013f, 0.014f, 0.013f),
                0.66f,
                0.20f,
                0.30f,
                SpinnerGroundingStageShape.SoftSquare,
                1.42f,
                0.065f,
                true,
                string.Empty,
                new SpinnerEnvironmentLightPreset(
                    "Key_UpperLeft",
                    new Color(0.78f, 0.84f, 0.82f),
                    0.88f),
                new SpinnerEnvironmentLightPreset(
                    "CoolFill",
                    new Color(0.50f, 0.62f, 0.70f),
                    0.32f)),
            new SpinnerEnvironmentProfile(
                "magnetic-fan-card",
                FanCardScenePath,
                UnifiedBackgroundResourcePath,
                1882,
                3344,
                4096,
                1.08f,
                0.68f,
                false,
                new Color(0.30f, 0.275f, 0.24f),
                new Color(0.14f, 0.125f, 0.105f),
                new Color(0.035f, 0.031f, 0.026f),
                0.82f,
                0.52f,
                0.58f,
                SpinnerGroundingStageShape.SoftSquare,
                1.40f,
                0.075f,
                true,
                string.Empty,
                new SpinnerEnvironmentLightPreset(
                    "LargeSoftKey_UpperLeft",
                    new Color(1.00f, 0.88f, 0.76f),
                    0.96f),
                new SpinnerEnvironmentLightPreset(
                    "CoolBroadFill",
                    new Color(0.58f, 0.68f, 0.78f),
                    0.34f))
        };

        public static IReadOnlyList<SpinnerEnvironmentProfile> Profiles => profiles;

        public static bool TryGetProfile(
            string scenePath,
            out SpinnerEnvironmentProfile profile)
        {
            for (int index = 0; index < profiles.Length; index++)
            {
                if (string.Equals(
                        profiles[index].ScenePath,
                        scenePath,
                        StringComparison.Ordinal))
                {
                    profile = profiles[index];
                    return true;
                }
            }

            profile = default;
            return false;
        }
    }

    /// <summary>
    /// Places the selected, already depth-blurred environment plate behind the
    /// active model and harmonizes the scene's authored lights with that plate.
    /// The background is unlit so scene lighting remains exclusive to the 3D
    /// spinner and its physical presentation materials.
    /// </summary>
    [DefaultExecutionOrder(1100)]
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class SpinnerEnvironmentPresenter : MonoBehaviour
    {
        public const string BackgroundObjectName = "SpinnerEnvironmentBackground";
        public const string MidgroundObjectName = "SpinnerEnvironmentMidground";
        public const string DeepStarfieldObjectName = "SpinnerEnvironmentStarsDeep";
        public const string NearStarfieldObjectName = "SpinnerEnvironmentStarsNear";
        public const string RightForegroundObjectName = "SpinnerEnvironmentRightForeground";
        public const string LeftForegroundObjectName = "SpinnerEnvironmentLeftForeground";
        public const string LeftForegroundResourcePath =
            "EnvironmentForegrounds/canyon-left-foreground-v1";
        public const string RightForegroundResourcePath =
            "EnvironmentForegrounds/canyon-right-foreground-v1";

        private const float MaximumBackgroundDistance = 50f;
        private const float FarClipFraction = 0.90f;
        private Camera targetCamera;
        private GameObject backgroundObject;
        private GameObject midgroundObject;
        private Mesh backgroundMesh;
        private MeshRenderer backgroundRenderer;
        private MeshRenderer midgroundRenderer;
        private GameObject deepStarfieldObject;
        private GameObject nearStarfieldObject;
        private GameObject rightForegroundObject;
        private GameObject leftForegroundObject;
        private MeshRenderer deepStarfieldRenderer;
        private MeshRenderer nearStarfieldRenderer;
        private MeshRenderer rightForegroundRenderer;
        private MeshRenderer leftForegroundRenderer;
        private Material midgroundMaterial;
        private Material deepStarfieldMaterial;
        private Material nearStarfieldMaterial;
        private Material rightForegroundMaterial;
        private Material leftForegroundMaterial;
        private Texture2D backgroundTexture;
        private Texture2D rightForegroundTexture;
        private Texture2D leftForegroundTexture;
        private SpinnerEnvironmentProfile currentProfile;
        private readonly Vector3[] frustumCorners = new Vector3[4];
        private Matrix4x4 previousProjectionMatrix;
        private bool hasPreviousProjection;
        private float previousFarClip = -1f;
        private float currentViewportWidth;
        private float currentViewportHeight;
        private Vector3 backgroundBasePosition;
        private Vector3 midgroundBasePosition;
        private Vector3 deepStarfieldBasePosition;
        private Vector3 nearStarfieldBasePosition;
        private Vector3 rightForegroundBasePosition;
        private Vector3 leftForegroundBasePosition;
        private Vector2 parallaxTilt;
        private float farParallaxPixels;
        private float midParallaxPixels;
        private float anchorParallaxPixels;
        private float modelHoverPixels;
        private float modelHoverNormalized;
        private MaterialPropertyBlock leftGlowProperties;
        private MaterialPropertyBlock rightGlowProperties;
        private MaterialPropertyBlock backgroundGlowProperties;
        private float framingVisibility = 1f;
        private float targetFramingVisibility = 1f;

        public Texture2D BackgroundTexture => backgroundTexture;
        public MeshRenderer BackgroundRenderer => backgroundRenderer;
        public MeshRenderer MidgroundRenderer => midgroundRenderer;
        public MeshRenderer DeepStarfieldRenderer => deepStarfieldRenderer;
        public MeshRenderer NearStarfieldRenderer => nearStarfieldRenderer;
        public MeshRenderer RightForegroundRenderer => rightForegroundRenderer;
        public MeshRenderer LeftForegroundRenderer => leftForegroundRenderer;
        public SpinnerSceneParallaxController ParallaxController { get; private set; }
        public SpinnerGroundingStage GroundingStage { get; private set; }
        public SpinnerImageBasedLightingController ImageBasedLighting { get; private set; }

        public static SpinnerEnvironmentPresenter Install(string scenePath)
        {
            if (!SpinnerEnvironmentCatalog.TryGetProfile(scenePath, out var profile))
            {
                Debug.LogWarning(
                    $"[FidgetingApp] No environment profile registered for {scenePath}.");
                return null;
            }

            Camera camera = Camera.main ?? FindAnyObjectByType<Camera>();
            if (camera == null)
            {
                Debug.LogError(
                    $"[FidgetingApp] Cannot install environment for {scenePath}: no camera.");
                return null;
            }

            SpinnerEnvironmentPresenter presenter =
                camera.GetComponent<SpinnerEnvironmentPresenter>();
            if (presenter == null)
            {
                presenter = camera.gameObject.AddComponent<SpinnerEnvironmentPresenter>();
            }

            presenter.Apply(profile);
            return presenter;
        }

        public void Apply(SpinnerEnvironmentProfile profile)
        {
            targetCamera = GetComponent<Camera>();
            currentProfile = profile;
            backgroundTexture = Resources.Load<Texture2D>(profile.BackgroundResourcePath);
            rightForegroundTexture = Resources.Load<Texture2D>(RightForegroundResourcePath);
            leftForegroundTexture = Resources.Load<Texture2D>(LeftForegroundResourcePath);
            Material backgroundMaterial = Resources.Load<Material>(
                SpinnerEnvironmentCatalog.ParallaxMaterialResourcePath);
            Material starfieldMaterial = Resources.Load<Material>(
                SpinnerEnvironmentCatalog.StarfieldMaterialResourcePath);

            if (backgroundTexture == null
                || backgroundMaterial == null
                || rightForegroundTexture == null
                || leftForegroundTexture == null)
            {
                Debug.LogError(
                    "[FidgetingApp] Environment assets are incomplete: "
                    + $"texture={profile.BackgroundResourcePath}, "
                    + $"leftForeground={LeftForegroundResourcePath}, "
                    + $"rightForeground={RightForegroundResourcePath}, "
                    + "material="
                    + SpinnerEnvironmentCatalog.ParallaxMaterialResourcePath
                    + ".");
                SetBackgroundActive(false);
                return;
            }

            EnsureBackgroundObject();
            backgroundRenderer.sharedMaterial = backgroundMaterial;
            ConfigureRendererProperties(
                backgroundRenderer,
                ResolveExperienceTint(targetCamera.backgroundColor),
                profile.Saturation,
                false);
            backgroundObject.SetActive(true);

            ConfigureMidground(profile, backgroundMaterial);
            ConfigureDepthLayers(profile, backgroundMaterial, starfieldMaterial);

            DisableLegacyBackdrop(profile);
            GroundingStage = SpinnerGroundingStage.Install(profile);
            ImageBasedLighting = GetComponent<SpinnerImageBasedLightingController>();
            if (ImageBasedLighting == null)
            {
                ImageBasedLighting = gameObject.AddComponent<
                    SpinnerImageBasedLightingController>();
            }
            ImageBasedLighting.Configure(backgroundTexture, profile, GroundingStage);

            ParallaxController = GetComponent<SpinnerSceneParallaxController>();
            if (ParallaxController == null)
            {
                ParallaxController = gameObject.AddComponent<SpinnerSceneParallaxController>();
            }
            ParallaxController.Configure(this, ImageBasedLighting);
            ResizeBackground(true);
        }

        public void SetExperienceTint(Color backgroundAccent)
        {
            Color tint = ResolveExperienceTint(backgroundAccent);
            if (backgroundRenderer != null)
            {
                SetRendererTint(backgroundRenderer, tint);
            }

            if (midgroundRenderer != null && midgroundRenderer.gameObject.activeSelf)
            {
                SetRendererTint(midgroundRenderer, tint);
            }

            Color foregroundHue = Color.Lerp(Color.white, tint, 0.18f);
            if (rightForegroundRenderer != null)
            {
                SetRendererTint(
                    rightForegroundRenderer,
                    new Color(
                        foregroundHue.r * 0.62f,
                        foregroundHue.g * 0.64f,
                        foregroundHue.b * 0.63f,
                        1f));
            }
            if (leftForegroundRenderer != null)
            {
                SetRendererTint(
                    leftForegroundRenderer,
                    new Color(
                        foregroundHue.r * 0.54f,
                        foregroundHue.g * 0.56f,
                        foregroundHue.b * 0.55f,
                        1f));
            }
        }

        public void SetParallaxTilt(
            Vector2 normalizedTilt,
            float farLayerPixels,
            float midLayerPixels)
        {
            parallaxTilt = Vector2.ClampMagnitude(normalizedTilt, 1f);
            farParallaxPixels = Mathf.Max(0f, farLayerPixels);
            midParallaxPixels = Mathf.Max(0f, midLayerPixels);
            anchorParallaxPixels = SpinnerSceneParallaxController.AnchorLayerPixels;
            modelHoverPixels = 0f;
            modelHoverNormalized = 0f;
            ApplyParallaxOffsets();
        }

        public void SetLayeredParallaxTilt(
            Vector2 normalizedTilt,
            float anchorLayerPixels)
        {
            SetLayeredParallaxTilt(
                normalizedTilt,
                anchorLayerPixels,
                0f,
                0f);
        }

        public void SetLayeredParallaxTilt(
            Vector2 normalizedTilt,
            float anchorLayerPixels,
            float hoverPixels,
            float hoverNormalized)
        {
            parallaxTilt = Vector2.ClampMagnitude(normalizedTilt, 1f);
            farParallaxPixels = SpinnerSceneParallaxController.FarLayerPixels;
            midParallaxPixels = SpinnerSceneParallaxController.MidLayerPixels;
            anchorParallaxPixels = Mathf.Max(0f, anchorLayerPixels);
            modelHoverPixels = Mathf.Max(0f, hoverPixels);
            modelHoverNormalized = Mathf.Clamp01(hoverNormalized);
            ApplyParallaxOffsets();
        }

        public void SetEnvironmentGlow(
            Color leftGlow,
            Color rightGlow,
            Vector2 normalizedTilt)
        {
            leftGlowProperties ??= new MaterialPropertyBlock();
            rightGlowProperties ??= new MaterialPropertyBlock();
            backgroundGlowProperties ??= new MaterialPropertyBlock();
            ConfigureBackgroundSubjectGlow(
                backgroundRenderer,
                backgroundGlowProperties,
                leftGlow,
                rightGlow,
                normalizedTilt,
                modelHoverNormalized);
            ConfigureForegroundGlow(
                leftForegroundRenderer,
                leftGlowProperties,
                leftGlow,
                rightGlow,
                new Vector2(
                    0.22f + normalizedTilt.x * 0.035f,
                    0.50f + normalizedTilt.y * 0.030f));
            ConfigureForegroundGlow(
                rightForegroundRenderer,
                rightGlowProperties,
                rightGlow,
                leftGlow,
                new Vector2(
                    0.78f + normalizedTilt.x * 0.035f,
                    0.46f + normalizedTilt.y * 0.030f));
        }

        public void SetLibraryPreviewActive(bool active, bool immediate = false)
        {
            targetFramingVisibility = active ? 1f : 0f;
            GroundingStage?.SetLibraryPreviewActive(active, immediate);
            ImageBasedLighting?.SetLibraryPreviewActive(active);
            ParallaxController?.SetLibraryPreviewActive(active, immediate);
            if (immediate)
            {
                framingVisibility = targetFramingVisibility;
                ApplyParallaxOffsets();
            }
        }

        public void BeginLibraryPageExit(float direction)
        {
            ParallaxController?.BeginLibraryPageExit(direction);
        }

        public void BeginLibraryPageEntrance(float direction)
        {
            ParallaxController?.BeginLibraryPageEntrance(direction);
        }

        public void RefreshLayout()
        {
            ResizeBackground(true);
        }

        public static Color ResolveExperienceTint(Color backgroundAccent)
        {
            float magnitude = Mathf.Max(
                backgroundAccent.r,
                backgroundAccent.g,
                backgroundAccent.b);
            if (magnitude <= 0.0001f)
            {
                return Color.white;
            }

            Color hue = new Color(
                backgroundAccent.r / magnitude,
                backgroundAccent.g / magnitude,
                backgroundAccent.b / magnitude,
                1f);
            float activation = Mathf.InverseLerp(0f, 0.14f, magnitude);
            return Color.Lerp(Color.white, hue, activation * 0.18f);
        }

        private void LateUpdate()
        {
            float transitionBlend = 1f - Mathf.Exp(-Time.unscaledDeltaTime * 7.2f);
            framingVisibility = Mathf.Lerp(
                framingVisibility,
                targetFramingVisibility,
                transitionBlend);
            if (Mathf.Abs(framingVisibility - targetFramingVisibility) < 0.001f)
            {
                framingVisibility = targetFramingVisibility;
            }
            ResizeBackground(false);
            ApplyParallaxOffsets();
        }

        private void OnDestroy()
        {
            DestroyRuntimeMaterial(ref midgroundMaterial);
            DestroyRuntimeMaterial(ref deepStarfieldMaterial);
            DestroyRuntimeMaterial(ref nearStarfieldMaterial);
            DestroyRuntimeMaterial(ref rightForegroundMaterial);
            DestroyRuntimeMaterial(ref leftForegroundMaterial);

            if (backgroundMesh == null)
            {
                return;
            }

            if (Application.isPlaying)
            {
                Destroy(backgroundMesh);
            }
            else
            {
                DestroyImmediate(backgroundMesh);
            }

            backgroundMesh = null;
        }

        private void EnsureBackgroundObject()
        {
            if (backgroundObject != null)
            {
                return;
            }

            backgroundObject = new GameObject(BackgroundObjectName);
            backgroundObject.transform.SetParent(transform, false);

            var filter = backgroundObject.AddComponent<MeshFilter>();
            backgroundRenderer = backgroundObject.AddComponent<MeshRenderer>();
            backgroundMesh = CreateQuadMesh();
            filter.sharedMesh = backgroundMesh;

            backgroundRenderer.shadowCastingMode = ShadowCastingMode.Off;
            backgroundRenderer.receiveShadows = false;
            backgroundRenderer.lightProbeUsage = LightProbeUsage.Off;
            backgroundRenderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            backgroundRenderer.motionVectorGenerationMode =
                MotionVectorGenerationMode.ForceNoMotion;
            backgroundRenderer.allowOcclusionWhenDynamic = false;
            backgroundRenderer.sortingOrder = -1000;
        }

        private void EnsureMidgroundObject()
        {
            if (midgroundObject != null)
            {
                return;
            }

            midgroundObject = new GameObject(MidgroundObjectName);
            midgroundObject.transform.SetParent(transform, false);

            var filter = midgroundObject.AddComponent<MeshFilter>();
            filter.sharedMesh = backgroundMesh;
            midgroundRenderer = midgroundObject.AddComponent<MeshRenderer>();
            midgroundRenderer.shadowCastingMode = ShadowCastingMode.Off;
            midgroundRenderer.receiveShadows = false;
            midgroundRenderer.lightProbeUsage = LightProbeUsage.Off;
            midgroundRenderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            midgroundRenderer.motionVectorGenerationMode =
                MotionVectorGenerationMode.ForceNoMotion;
            midgroundRenderer.allowOcclusionWhenDynamic = false;
            midgroundRenderer.sortingOrder = -999;
        }

        private void ConfigureMidground(
            SpinnerEnvironmentProfile profile,
            Material backgroundMaterial)
        {
            if (!profile.LayeredParallax)
            {
                if (midgroundObject != null)
                {
                    midgroundObject.SetActive(false);
                }
                return;
            }

            EnsureMidgroundObject();
            if (midgroundMaterial != null)
            {
                if (Application.isPlaying)
                {
                    Destroy(midgroundMaterial);
                }
                else
                {
                    DestroyImmediate(midgroundMaterial);
                }
            }

            midgroundMaterial = new Material(backgroundMaterial)
            {
                name = $"{profile.ModelId}_EnvironmentMidground_Runtime",
                renderQueue = (int)RenderQueue.Transparent
            };
            midgroundMaterial.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            midgroundMaterial.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            midgroundMaterial.SetFloat("_ZWrite", 0f);
            midgroundRenderer.sharedMaterial = midgroundMaterial;
            ConfigureRendererProperties(
                midgroundRenderer,
                ResolveExperienceTint(targetCamera.backgroundColor),
                profile.Saturation,
                true);
            midgroundObject.SetActive(true);
        }

        private void ConfigureDepthLayers(
            SpinnerEnvironmentProfile profile,
            Material backgroundMaterial,
            Material starfieldSourceMaterial)
        {
            EnsureDepthLayerObjects();

            bool hasStarfield = starfieldSourceMaterial != null
                && starfieldSourceMaterial.shader != null;
            if (!hasStarfield)
            {
                Debug.LogError(
                    "[FidgetingApp] Environment starfield material is unavailable: "
                    + SpinnerEnvironmentCatalog.StarfieldMaterialResourcePath
                    + ". Continuing with canyon foregrounds and no stars.");
                DestroyRuntimeMaterial(ref deepStarfieldMaterial);
                DestroyRuntimeMaterial(ref nearStarfieldMaterial);
                deepStarfieldObject.SetActive(false);
                nearStarfieldObject.SetActive(false);
            }
            else
            {
                DestroyRuntimeMaterial(ref deepStarfieldMaterial);
                deepStarfieldMaterial = CreateStarfieldMaterial(
                    starfieldSourceMaterial,
                    $"{profile.ModelId}_StarsDeep_Runtime",
                    new Color(0.58f, 0.66f, 0.62f, 0.62f),
                    0.028f,
                    58f,
                    3.17f,
                    0.46f,
                    0.105f);
                deepStarfieldRenderer.sharedMaterial = deepStarfieldMaterial;

                DestroyRuntimeMaterial(ref nearStarfieldMaterial);
                nearStarfieldMaterial = CreateStarfieldMaterial(
                    starfieldSourceMaterial,
                    $"{profile.ModelId}_StarsNear_Runtime",
                    new Color(0.74f, 0.82f, 0.77f, 0.78f),
                    0.020f,
                    82f,
                    8.63f,
                    0.68f,
                    0.14f);
                nearStarfieldRenderer.sharedMaterial = nearStarfieldMaterial;
                deepStarfieldObject.SetActive(true);
                nearStarfieldObject.SetActive(true);
            }

            DestroyRuntimeMaterial(ref rightForegroundMaterial);
            rightForegroundMaterial = CreateForegroundMaterial(
                backgroundMaterial,
                $"{profile.ModelId}_RightForeground_Runtime",
                (int)RenderQueue.Transparent + 1);
            rightForegroundRenderer.sharedMaterial = rightForegroundMaterial;
            ConfigureLayerRendererProperties(
                rightForegroundRenderer,
                rightForegroundTexture,
                new Color(0.62f, 0.64f, 0.63f, 1f),
                Mathf.Min(profile.Saturation, 0.52f),
                0.90f,
                true);

            DestroyRuntimeMaterial(ref leftForegroundMaterial);
            leftForegroundMaterial = CreateForegroundMaterial(
                backgroundMaterial,
                $"{profile.ModelId}_LeftForeground_Runtime",
                (int)RenderQueue.Transparent + 2);
            leftForegroundRenderer.sharedMaterial = leftForegroundMaterial;
            ConfigureLayerRendererProperties(
                leftForegroundRenderer,
                leftForegroundTexture,
                new Color(0.54f, 0.56f, 0.55f, 1f),
                Mathf.Min(profile.Saturation, 0.46f),
                0.94f,
                true);

            rightForegroundObject.SetActive(true);
            leftForegroundObject.SetActive(true);
        }

        private void EnsureDepthLayerObjects()
        {
            EnsureLayerObject(
                ref deepStarfieldObject,
                ref deepStarfieldRenderer,
                DeepStarfieldObjectName,
                -900);
            EnsureLayerObject(
                ref nearStarfieldObject,
                ref nearStarfieldRenderer,
                NearStarfieldObjectName,
                -899);
            EnsureLayerObject(
                ref rightForegroundObject,
                ref rightForegroundRenderer,
                RightForegroundObjectName,
                1000);
            EnsureLayerObject(
                ref leftForegroundObject,
                ref leftForegroundRenderer,
                LeftForegroundObjectName,
                1001);
        }

        private void EnsureLayerObject(
            ref GameObject layerObject,
            ref MeshRenderer layerRenderer,
            string objectName,
            int sortingOrder)
        {
            if (layerObject == null)
            {
                layerObject = new GameObject(objectName);
                layerObject.transform.SetParent(transform, false);
                var filter = layerObject.AddComponent<MeshFilter>();
                filter.sharedMesh = backgroundMesh;
                layerRenderer = layerObject.AddComponent<MeshRenderer>();
            }

            layerRenderer.shadowCastingMode = ShadowCastingMode.Off;
            layerRenderer.receiveShadows = false;
            layerRenderer.lightProbeUsage = LightProbeUsage.Off;
            layerRenderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            layerRenderer.motionVectorGenerationMode =
                MotionVectorGenerationMode.ForceNoMotion;
            layerRenderer.allowOcclusionWhenDynamic = false;
            layerRenderer.sortingOrder = sortingOrder;
        }

        private static Material CreateStarfieldMaterial(
            Material source,
            string name,
            Color color,
            float density,
            float grid,
            float seed,
            float intensity,
            float pointRadius)
        {
            var material = new Material(source)
            {
                name = name,
                renderQueue = (int)RenderQueue.Transparent
            };
            material.SetColor("_StarColor", color);
            material.SetFloat("_Density", density);
            material.SetFloat("_Grid", grid);
            material.SetFloat("_Seed", seed);
            material.SetFloat("_Intensity", intensity);
            material.SetFloat("_PointRadius", pointRadius);
            return material;
        }

        private static Material CreateForegroundMaterial(
            Material source,
            string name,
            int renderQueue)
        {
            var material = new Material(source)
            {
                name = name,
                renderQueue = renderQueue
            };
            material.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            material.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            material.SetFloat("_ZWrite", 0f);
            material.SetFloat("_ZTest", (float)CompareFunction.Always);
            return material;
        }

        private static void ConfigureLayerRendererProperties(
            MeshRenderer renderer,
            Texture texture,
            Color tint,
            float saturation,
            float opacity,
            bool glowEnabled)
        {
            var properties = new MaterialPropertyBlock();
            properties.SetTexture("_BaseMap", texture);
            properties.SetTexture("_MainTex", texture);
            properties.SetColor("_BaseColor", tint);
            properties.SetFloat("_Saturation", saturation);
            properties.SetFloat("_LayerMask", 0f);
            properties.SetFloat("_Opacity", opacity);
            properties.SetFloat("_GlowEnabled", glowEnabled ? 1f : 0f);
            properties.SetFloat("_GlowRadius", 0.29f);
            properties.SetFloat("_GlowIntensity", glowEnabled ? 0.16f : 0f);
            renderer.SetPropertyBlock(properties);
        }

        private static void ConfigureForegroundGlow(
            MeshRenderer renderer,
            MaterialPropertyBlock properties,
            Color primary,
            Color secondary,
            Vector2 center)
        {
            if (renderer == null)
            {
                return;
            }

            renderer.GetPropertyBlock(properties);
            properties.SetColor("_GlowColorA", primary.linear * 0.58f);
            properties.SetColor("_GlowColorB", secondary.linear * 0.38f);
            properties.SetVector(
                "_GlowCenterA",
                new Vector4(center.x, center.y, 0f, 0f));
            properties.SetVector(
                "_GlowCenterB",
                new Vector4(1f - center.x, center.y - 0.10f, 0f, 0f));
            properties.SetFloat("_GlowIntensity", 0.32f);
            properties.SetVector("_GlowScaleA", new Vector4(0.5625f, 1f, 0f, 0f));
            properties.SetVector("_GlowScaleB", new Vector4(0.5625f, 1f, 0f, 0f));
            renderer.SetPropertyBlock(properties);
        }

        private static void ConfigureBackgroundSubjectGlow(
            MeshRenderer renderer,
            MaterialPropertyBlock properties,
            Color leftColor,
            Color rightColor,
            Vector2 normalizedTilt,
            float hoverNormalized)
        {
            if (renderer == null)
            {
                return;
            }

            renderer.GetPropertyBlock(properties);
            Color subjectColor = Color.Lerp(leftColor, rightColor, 0.5f);
            Color contactColor = Color.Lerp(rightColor, leftColor, 0.32f);
            properties.SetFloat("_GlowEnabled", 1f);
            properties.SetColor("_GlowColorA", subjectColor.linear * 0.84f);
            properties.SetColor("_GlowColorB", contactColor.linear * 0.62f);
            properties.SetVector(
                "_GlowCenterA",
                new Vector4(
                    0.50f + normalizedTilt.x * 0.028f,
                    0.43f + normalizedTilt.y * 0.020f,
                    0f,
                    0f));
            properties.SetVector(
                "_GlowCenterB",
                new Vector4(
                    0.50f - normalizedTilt.x * 0.012f,
                    0.315f + normalizedTilt.y * 0.006f,
                    0f,
                    0f));
            properties.SetVector("_GlowScaleA", new Vector4(0.5625f, 1f, 0f, 0f));
            properties.SetVector("_GlowScaleB", new Vector4(0.42f, 2.8f, 0f, 0f));
            properties.SetFloat("_GlowRadius", 0.24f);
            properties.SetFloat("_GlowIntensity", 0.42f);
            properties.SetFloat("_ShadowEnabled", 1f);
            properties.SetVector(
                "_ShadowCenter",
                new Vector4(
                    0.50f + normalizedTilt.x * 0.030f,
                    0.325f + normalizedTilt.y * 0.008f,
                    0f,
                    0f));
            properties.SetVector(
                "_ShadowScale",
                new Vector4(
                    Mathf.Lerp(0.82f, 0.70f, hoverNormalized),
                    Mathf.Lerp(11.0f, 8.2f, hoverNormalized),
                    0f,
                    0f));
            properties.SetFloat(
                "_ShadowRadius",
                Mathf.Lerp(0.175f, 0.225f, hoverNormalized));
            properties.SetFloat(
                "_ShadowStrength",
                Mathf.Lerp(0.88f, 0.50f, hoverNormalized));
            renderer.SetPropertyBlock(properties);
        }

        private void ConfigureRendererProperties(
            MeshRenderer renderer,
            Color tint,
            float saturation,
            bool midgroundMask)
        {
            var properties = new MaterialPropertyBlock();
            properties.SetTexture("_BaseMap", backgroundTexture);
            properties.SetTexture("_MainTex", backgroundTexture);
            properties.SetColor("_BaseColor", tint);
            properties.SetFloat("_Saturation", saturation);
            properties.SetFloat("_LayerMask", midgroundMask ? 1f : 0f);
            properties.SetFloat("_LayerMaskStart", 0.38f);
            properties.SetFloat("_LayerMaskFeather", 0.10f);
            properties.SetFloat("_GlowEnabled", midgroundMask ? 0f : 1f);
            properties.SetFloat("_GlowRadius", 0.24f);
            properties.SetFloat("_GlowIntensity", 0f);
            properties.SetFloat("_ShadowEnabled", 0f);
            properties.SetVector("_ShadowScale", new Vector4(0.82f, 11f, 0f, 0f));
            properties.SetFloat("_ShadowRadius", 0.20f);
            properties.SetFloat("_ShadowStrength", 0f);
            properties.SetVector("_GlowScaleA", new Vector4(0.5625f, 1f, 0f, 0f));
            properties.SetVector("_GlowScaleB", new Vector4(0.42f, 2.8f, 0f, 0f));
            renderer.SetPropertyBlock(properties);
        }

        private static void SetRendererTint(MeshRenderer renderer, Color tint)
        {
            var properties = new MaterialPropertyBlock();
            renderer.GetPropertyBlock(properties);
            properties.SetColor("_BaseColor", tint);
            renderer.SetPropertyBlock(properties);
        }

        private static Mesh CreateQuadMesh()
        {
            var mesh = new Mesh
            {
                name = "SpinnerEnvironmentBackground_Runtime"
            };
            mesh.SetVertices(new[]
            {
                new Vector3(-0.5f, -0.5f, 0f),
                new Vector3(0.5f, -0.5f, 0f),
                new Vector3(-0.5f, 0.5f, 0f),
                new Vector3(0.5f, 0.5f, 0f)
            });
            mesh.SetUVs(0, new[]
            {
                new Vector2(0f, 0f),
                new Vector2(1f, 0f),
                new Vector2(0f, 1f),
                new Vector2(1f, 1f)
            });
            mesh.SetTriangles(new[] { 0, 2, 1, 2, 3, 1 }, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        private void ResizeBackground(bool force)
        {
            if (targetCamera == null || backgroundObject == null || backgroundTexture == null)
            {
                return;
            }

            Matrix4x4 projectionMatrix = targetCamera.projectionMatrix;
            if (!force
                && hasPreviousProjection
                && previousProjectionMatrix == projectionMatrix
                && Mathf.Approximately(previousFarClip, targetCamera.farClipPlane))
            {
                return;
            }

            float distance = Mathf.Min(
                MaximumBackgroundDistance,
                targetCamera.farClipPlane * FarClipFraction);
            distance = Mathf.Max(distance, targetCamera.nearClipPlane + 0.05f);

            targetCamera.CalculateFrustumCorners(
                new Rect(0f, 0f, 1f, 1f),
                distance,
                Camera.MonoOrStereoscopicEye.Mono,
                frustumCorners);
            float minimumX = frustumCorners.Min(corner => corner.x);
            float maximumX = frustumCorners.Max(corner => corner.x);
            float minimumY = frustumCorners.Min(corner => corner.y);
            float maximumY = frustumCorners.Max(corner => corner.y);
            float viewportWidth = Mathf.Max(0.01f, maximumX - minimumX);
            float viewportHeight = Mathf.Max(0.01f, maximumY - minimumY);
            float textureAspect =
                (float)backgroundTexture.width / Mathf.Max(1, backgroundTexture.height);

            float backgroundWidth = viewportWidth;
            float backgroundHeight = backgroundWidth / textureAspect;
            if (backgroundHeight < viewportHeight)
            {
                backgroundHeight = viewportHeight;
                backgroundWidth = backgroundHeight * textureAspect;
            }

            float overscan = Mathf.Max(1f, currentProfile.CoverOverscan);
            backgroundWidth *= overscan;
            backgroundHeight *= overscan;

            Transform backgroundTransform = backgroundObject.transform;
            backgroundBasePosition = new Vector3(
                (minimumX + maximumX) * 0.5f,
                (minimumY + maximumY) * 0.5f,
                distance);
            backgroundTransform.localPosition = backgroundBasePosition;
            backgroundTransform.localRotation = Quaternion.identity;
            backgroundTransform.localScale =
                new Vector3(backgroundWidth, backgroundHeight, 1f);

            if (midgroundObject != null && midgroundObject.activeSelf)
            {
                Transform midgroundTransform = midgroundObject.transform;
                midgroundBasePosition = new Vector3(
                    backgroundBasePosition.x,
                    backgroundBasePosition.y,
                    Mathf.Max(targetCamera.nearClipPlane + 0.04f, distance - 0.02f));
                midgroundTransform.localPosition = midgroundBasePosition;
                midgroundTransform.localRotation = Quaternion.identity;
                midgroundTransform.localScale =
                    new Vector3(backgroundWidth, backgroundHeight, 1f);
            }

            if (deepStarfieldObject != null)
            {
                deepStarfieldBasePosition = new Vector3(
                    backgroundBasePosition.x,
                    backgroundBasePosition.y,
                    Mathf.Max(targetCamera.nearClipPlane + 0.04f, distance - 0.030f));
                SetLayerTransform(
                    deepStarfieldObject.transform,
                    deepStarfieldBasePosition,
                    backgroundWidth,
                    backgroundHeight,
                    1.015f);
            }

            if (nearStarfieldObject != null)
            {
                nearStarfieldBasePosition = new Vector3(
                    backgroundBasePosition.x,
                    backgroundBasePosition.y,
                    Mathf.Max(targetCamera.nearClipPlane + 0.035f, distance - 0.040f));
                SetLayerTransform(
                    nearStarfieldObject.transform,
                    nearStarfieldBasePosition,
                    backgroundWidth,
                    backgroundHeight,
                    1.020f);
            }

            if (rightForegroundObject != null)
            {
                rightForegroundBasePosition = new Vector3(
                    backgroundBasePosition.x,
                    backgroundBasePosition.y,
                    Mathf.Max(targetCamera.nearClipPlane + 0.030f, distance - 0.050f));
                SetLayerTransform(
                    rightForegroundObject.transform,
                    rightForegroundBasePosition,
                    backgroundWidth,
                    backgroundHeight,
                    1.13f);
            }

            if (leftForegroundObject != null)
            {
                leftForegroundBasePosition = new Vector3(
                    backgroundBasePosition.x,
                    backgroundBasePosition.y,
                    Mathf.Max(targetCamera.nearClipPlane + 0.025f, distance - 0.060f));
                SetLayerTransform(
                    leftForegroundObject.transform,
                    leftForegroundBasePosition,
                    backgroundWidth,
                    backgroundHeight,
                    1.16f);
            }

            currentViewportWidth = viewportWidth;
            currentViewportHeight = viewportHeight;
            ApplyParallaxOffsets();

            previousProjectionMatrix = projectionMatrix;
            hasPreviousProjection = true;
            previousFarClip = targetCamera.farClipPlane;
        }

        private void ApplyParallaxOffsets()
        {
            if (targetCamera == null
                || backgroundObject == null
                || currentViewportWidth <= 0f
                || currentViewportHeight <= 0f)
            {
                return;
            }

            Vector2 viewportPixels =
                SpinnerSceneParallaxController.ResolveViewportPixels(targetCamera);
            float hoverCompensationDirection = targetCamera.orthographic ? -1f : 1f;
            Vector3 hoverCompensation = PixelOffsetToLocal(
                new Vector2(0f, modelHoverPixels * hoverCompensationDirection),
                viewportPixels);
            float farLocalPixels = ResolveLocalLayerPixels(
                targetCamera.orthographic,
                anchorParallaxPixels,
                farParallaxPixels,
                true);
            Vector3 farOffset = PixelOffsetToLocal(
                parallaxTilt * farLocalPixels,
                viewportPixels);
            backgroundObject.transform.localPosition = backgroundBasePosition
                + farOffset
                + hoverCompensation;

            if (midgroundObject != null && midgroundObject.activeSelf)
            {
                float midLocalPixels = ResolveLocalLayerPixels(
                    targetCamera.orthographic,
                    anchorParallaxPixels,
                    midParallaxPixels,
                    true);
                Vector3 midOffset = PixelOffsetToLocal(
                    parallaxTilt * midLocalPixels,
                    viewportPixels);
                midgroundObject.transform.localPosition = midgroundBasePosition
                    + midOffset
                    + hoverCompensation;
            }

            ApplyLayerOffset(
                deepStarfieldObject,
                deepStarfieldBasePosition,
                SpinnerSceneParallaxController.DeepStarLayerPixels,
                true,
                viewportPixels);
            ApplyLayerOffset(
                nearStarfieldObject,
                nearStarfieldBasePosition,
                SpinnerSceneParallaxController.StarLayerPixels,
                true,
                viewportPixels);
            ApplyLayerOffset(
                rightForegroundObject,
                rightForegroundBasePosition,
                SpinnerSceneParallaxController.RightForegroundPixels,
                false,
                viewportPixels);
            ApplyLayerOffset(
                leftForegroundObject,
                leftForegroundBasePosition,
                SpinnerSceneParallaxController.LeftForegroundPixels,
                false,
                viewportPixels);

            float retreat = 1f - framingVisibility;
            float easedRetreat = retreat * retreat * (3f - 2f * retreat);
            if (rightForegroundObject != null)
            {
                rightForegroundObject.transform.localPosition += new Vector3(
                    currentViewportWidth * 0.64f * easedRetreat,
                    -currentViewportHeight * 0.08f * easedRetreat,
                    0f);
            }
            if (leftForegroundObject != null)
            {
                leftForegroundObject.transform.localPosition += new Vector3(
                    -currentViewportWidth * 0.68f * easedRetreat,
                    -currentViewportHeight * 0.10f * easedRetreat,
                    0f);
            }
        }

        private static void SetLayerTransform(
            Transform layer,
            Vector3 basePosition,
            float width,
            float height,
            float overscan)
        {
            layer.localPosition = basePosition;
            layer.localRotation = Quaternion.identity;
            layer.localScale = new Vector3(
                width * Mathf.Max(1f, overscan),
                height * Mathf.Max(1f, overscan),
                1f);
        }

        private void ApplyLayerOffset(
            GameObject layer,
            Vector3 basePosition,
            float layerPixels,
            bool inverse,
            Vector2 viewportPixels)
        {
            if (layer == null || !layer.activeSelf)
            {
                return;
            }

            float localPixels = ResolveLocalLayerPixels(
                targetCamera.orthographic,
                anchorParallaxPixels,
                layerPixels,
                inverse);
            layer.transform.localPosition = basePosition + PixelOffsetToLocal(
                parallaxTilt * localPixels,
                viewportPixels)
                + PixelOffsetToLocal(
                    new Vector2(
                        0f,
                        modelHoverPixels * (targetCamera.orthographic ? -1f : 1f)),
                    viewportPixels);
        }

        public static float ResolveLocalLayerPixels(
            bool orthographic,
            float anchorLayerPixels,
            float desiredLayerPixels,
            bool inverse)
        {
            float projectionDirection = orthographic ? 1f : -1f;
            float projectedScreenPixels = projectionDirection
                * Mathf.Max(0f, anchorLayerPixels);
            float desiredScreenPixels = projectionDirection
                * Mathf.Max(0f, desiredLayerPixels)
                * (inverse ? -1f : 1f);
            return desiredScreenPixels - projectedScreenPixels;
        }

        private Vector3 PixelOffsetToLocal(Vector2 pixelOffset, Vector2 viewportPixels)
        {
            return new Vector3(
                pixelOffset.x * currentViewportWidth / Mathf.Max(1f, viewportPixels.x),
                pixelOffset.y * currentViewportHeight / Mathf.Max(1f, viewportPixels.y),
                0f);
        }

        private static void DisableLegacyBackdrop(SpinnerEnvironmentProfile profile)
        {
            if (string.IsNullOrEmpty(profile.LegacyBackdropObjectName))
            {
                return;
            }

            Transform[] sceneTransforms = FindObjectsByType<Transform>(
                FindObjectsInactive.Include,
                FindObjectsSortMode.None);
            for (int index = 0; index < sceneTransforms.Length; index++)
            {
                GameObject candidate = sceneTransforms[index].gameObject;
                if (candidate.scene.IsValid()
                    && string.Equals(
                        candidate.name,
                        profile.LegacyBackdropObjectName,
                        StringComparison.Ordinal))
                {
                    candidate.SetActive(false);
                }
            }
        }

        private void SetBackgroundActive(bool active)
        {
            if (backgroundObject != null)
            {
                backgroundObject.SetActive(active);
            }

            if (midgroundObject != null)
            {
                midgroundObject.SetActive(active && currentProfile.LayeredParallax);
            }

            deepStarfieldObject?.SetActive(active);
            nearStarfieldObject?.SetActive(active);
            rightForegroundObject?.SetActive(active);
            leftForegroundObject?.SetActive(active);
        }

        private static void DestroyRuntimeMaterial(ref Material material)
        {
            if (material == null)
            {
                return;
            }

            if (Application.isPlaying)
            {
                Destroy(material);
            }
            else
            {
                DestroyImmediate(material);
            }
            material = null;
        }
    }
}
