using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    [Serializable]
    public struct PremiumDisplayCaseBadgeArtworkBinding
    {
        public PremiumDisplayCaseBadgeArtworkBinding(
            string assetName,
            Texture2D artwork)
        {
            this.assetName = assetName ?? string.Empty;
            this.artwork = artwork;
        }

        [SerializeField] private string assetName;
        [SerializeField] private Texture2D artwork;

        public string AssetName => assetName ?? string.Empty;
        public Texture2D Artwork => artwork;
    }

    /// <summary>
    /// Reusable gacha presentation component. The case owns presentation,
    /// lighting, parallax and reveal motion; callers own the prize node and
    /// pass an already instantiated glTF root through setContent().
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class PremiumDisplayCase : MonoBehaviour
    {
        private const float AuthoredCapsuleWidth = 0.180f;
        private const float AuthoredCapsuleHeight = 0.198f;
        private const float AuthoredCapsuleDepth = 0.048f;

        [Header("Reveal hierarchy")]
        [SerializeField] private Transform caseRevealRoot;
        [SerializeField] private Transform boxParallaxRoot;
        [SerializeField] private Transform boxLidRoot;
        [SerializeField] private Transform acrylicParallaxRoot;
        [SerializeField] private Transform interiorParallaxRoot;
        [SerializeField] private Transform contentParallaxRoot;

        [Header("Neutral capsule")]
        [SerializeField] private Transform circularCapsuleGeometry;
        [SerializeField] private Transform roundedSquareCapsuleGeometry;
        [SerializeField] private Transform contentSlot;
        [SerializeField] private Transform contentRevealRoot;
        [SerializeField] private Transform contentOrbitRoot;
        [SerializeField] private Transform contentFitRoot;
        [SerializeField] private Transform developmentPlaceholder;
        [SerializeField] private PremiumDisplayCaseCapsulePreset capsulePreset =
            PremiumDisplayCaseCapsulePreset.CircularStandard;

        [Header("Physical collector label")]
        [SerializeField] private TextMesh levelLaserMark;
        [SerializeField] private TextMesh productNameLaserMark;
        [SerializeField] private TextMesh editionLabelMark;
        [SerializeField] private TextMesh acquiredDateLabelMark;
        [SerializeField] private TextMesh collectibleIdLabelMark;
        [SerializeField] private Renderer rarityFoilRenderer;

        [Header("Featured earned Badge")]
        [SerializeField] private Transform featuredBadgeRoot;
        [SerializeField] private Renderer featuredBadgeArtworkRenderer;
        [SerializeField] private TextMesh featuredBadgeTokenMark;
        [SerializeField] private TextMesh featuredBadgeShortNameMark;
        [SerializeField] private PremiumDisplayCaseBadgeArtworkBinding[]
            featuredBadgeArtwork = Array.Empty<
                PremiumDisplayCaseBadgeArtworkBinding>();

        [Header("Case-owned rendering")]
        [SerializeField] private Renderer[] acrylicRenderers = Array.Empty<Renderer>();
        [SerializeField] private Light[] revealLights = Array.Empty<Light>();
        [SerializeField] private bool playOnEnable;
        [SerializeField, Min(0.1f)] private float parallaxResponse = 10f;

        private MaterialPropertyBlock materialProperties;
        private MaterialPropertyBlock badgeMaterialProperties;
        private MaterialPropertyBlock labelMaterialProperties;
        private readonly List<Renderer> measuredRenderers = new List<Renderer>();
        private readonly List<Collider> measuredColliders = new List<Collider>();
        private PremiumDisplayCaseContentOptions contentOptions =
            PremiumDisplayCaseContentOptions.Default;
        private PremiumDisplayCaseCapsuleDimensions capsuleDimensions;
        private ContentAttachment externalContent;
        private Vector2 targetParallax;
        private Vector2 filteredParallax;
        private float revealElapsed;
        private bool revealPlaying;
        private bool revealCallbackFired;
        private Vector3 revealedCasePosition;
        private Vector3 lidClosedPosition;
        private Quaternion lidClosedRotation;
        private Vector3 boxParallaxBase;
        private Vector3 acrylicParallaxBase;
        private Vector3 interiorParallaxBase;
        private Vector3 contentParallaxBase;
        private Quaternion caseBaseRotation;
        private float[] baseLightIntensities = Array.Empty<float>();
        private Color[] baseLightColors = Array.Empty<Color>();
        private PremiumDisplayCaseLightingPreset selectedLightingPreset =
            PremiumDisplayCaseLightingCatalog.Resolve(
                PremiumDisplayCaseLightingCatalog.DefaultId);
        private float currentRevealLightBoost = 1f;
        private bool hierarchyCaptured;

        private static readonly int RevealVisibilityId =
            Shader.PropertyToID("_RevealVisibility");
        private static readonly int RevealSweepId =
            Shader.PropertyToID("_RevealSweep");
        private static readonly int ParallaxTiltId =
            Shader.PropertyToID("_ParallaxTilt");
        private static readonly int BadgeBaseMapId =
            Shader.PropertyToID("_BaseMap");
        private static readonly int BaseColorId =
            Shader.PropertyToID("_BaseColor");

        /// <summary>
        /// Exact API contract consumed by the future gacha coordinator.
        /// </summary>
        public event Action onRevealComplete;

        public Transform ContentSlot => contentSlot;
        public Transform contentSlotAnchor => contentSlot;
        public PremiumDisplayCaseCapsulePreset CapsulePreset => capsulePreset;
        public PremiumDisplayCaseCapsuleDimensions CapsuleDimensions =>
            capsuleDimensions;
        public bool IsRevealPlaying => revealPlaying;
        public string IdentificationLevelText => levelLaserMark != null
            ? levelLaserMark.text
            : string.Empty;
        public string IdentificationProductName => productNameLaserMark != null
            ? productNameLaserMark.text
            : string.Empty;
        public string IdentificationEditionText => editionLabelMark != null
            ? editionLabelMark.text
            : string.Empty;
        public string IdentificationAcquiredText => acquiredDateLabelMark != null
            ? acquiredDateLabelMark.text
            : string.Empty;
        public string IdentificationCollectibleText => collectibleIdLabelMark != null
            ? collectibleIdLabelMark.text
            : string.Empty;
        public bool HasFeaturedBadge => featuredBadgeRoot != null
            && featuredBadgeRoot.gameObject.activeSelf;
        public string FeaturedBadgeAssetName { get; private set; } = string.Empty;
        public string FeaturedBadgeToken => featuredBadgeTokenMark != null
            ? featuredBadgeTokenMark.text
            : string.Empty;
        public string FeaturedBadgeShortName => featuredBadgeShortNameMark != null
            ? featuredBadgeShortNameMark.text
            : string.Empty;
        public float RevealProgress => Mathf.Clamp01(
            revealElapsed / PremiumDisplayCaseRevealMotion.DurationSeconds);
        public string CurrentLightingPresetId => selectedLightingPreset.Id;

        private void Awake()
        {
            CaptureAuthoredHierarchy();
            setCapsulePreset(capsulePreset);
            UseDevelopmentPlaceholder();
            ApplyRevealSample(PremiumDisplayCaseRevealMotion.Evaluate(
                playOnEnable ? 0f : PremiumDisplayCaseRevealMotion.DurationSeconds));
        }

        private void OnEnable()
        {
            if (playOnEnable)
            {
                play();
            }
        }

        private void OnDisable()
        {
            RestoreExternalContent();
        }

        private void OnDestroy()
        {
            RestoreExternalContent();
        }

        private void Update()
        {
            float deltaTime = Time.unscaledDeltaTime;
            UpdateParallax(deltaTime);
            UpdateIdleRotation(deltaTime);
            if (!revealPlaying)
            {
                return;
            }

            revealElapsed += Mathf.Max(0f, deltaTime);
            PremiumDisplayCaseRevealSample sample =
                PremiumDisplayCaseRevealMotion.Evaluate(revealElapsed);
            ApplyRevealSample(sample);
            if (!sample.Complete)
            {
                return;
            }

            revealPlaying = false;
            if (!revealCallbackFired)
            {
                revealCallbackFired = true;
                onRevealComplete?.Invoke();
            }
        }

        public void setContent(Transform gltfNode)
        {
            setContent(gltfNode, PremiumDisplayCaseContentOptions.Default);
        }

        public void setContent(
            GameObject gltfNode,
            PremiumDisplayCaseContentOptions options)
        {
            setContent(gltfNode != null ? gltfNode.transform : null, options);
        }

        public void setContent(
            Transform gltfNode,
            PremiumDisplayCaseContentOptions options)
        {
            CaptureAuthoredHierarchy();
            if (gltfNode == null)
            {
                RestoreExternalContent();
                UseDevelopmentPlaceholder();
                return;
            }
            if (contentFitRoot == null)
            {
                throw new InvalidOperationException(
                    "PremiumDisplayCase requires a contentFitRoot.");
            }
            if (gltfNode == transform || gltfNode.IsChildOf(transform))
            {
                throw new ArgumentException(
                    "The prize must be an external glTF root, not part of the case hierarchy.",
                    nameof(gltfNode));
            }

            RestoreExternalContent();
            if (developmentPlaceholder != null)
            {
                developmentPlaceholder.gameObject.SetActive(false);
            }

            externalContent = new ContentAttachment(gltfNode);
            contentOptions = options;
            gltfNode.SetParent(contentFitRoot, false);
            gltfNode.localPosition = Vector3.zero;
            gltfNode.localRotation = Quaternion.Euler(options.InitialEulerAngles);
            gltfNode.localScale = Vector3.one;
            gltfNode.gameObject.SetActive(true);
            FitAttachedContent(gltfNode);
            ResetIdleRotation();
        }

        public void setCapsulePreset(PremiumDisplayCaseCapsulePreset preset)
        {
            capsulePreset = preset;
            ApplyCapsuleDimensions(PremiumDisplayCaseCapsulePresets.Resolve(preset));
        }

        public void SetIdentification(string englishProductName, int currentLevel)
        {
            SetCollectorLabel(new PremiumDisplayCaseCollectorLabel(
                englishProductName,
                "ORIGINAL FINISH",
                currentLevel,
                string.Empty));
        }

        public void SetCollectorLabel(PremiumDisplayCaseCollectorLabel label)
        {
            if (levelLaserMark != null)
            {
                levelLaserMark.text = label.TierAndLevelDisplay;
            }
            if (productNameLaserMark != null)
            {
                productNameLaserMark.text = label.ProductName;
                const float baseCharacterSize = 0.00225f;
                float estimatedWidth = Mathf.Max(
                    0.001f,
                    label.ProductName.Length * baseCharacterSize * 2.8f);
                productNameLaserMark.characterSize = baseCharacterSize
                    * Mathf.Min(1f, 0.142f / estimatedWidth);
            }
            if (editionLabelMark != null)
            {
                editionLabelMark.text = label.Edition;
            }
            if (acquiredDateLabelMark != null)
            {
                acquiredDateLabelMark.text = label.AcquiredDisplay;
            }
            if (collectibleIdLabelMark != null)
            {
                collectibleIdLabelMark.text = label.CollectibleDisplay;
                collectibleIdLabelMark.gameObject.SetActive(
                    !string.IsNullOrEmpty(label.CollectibleDisplay));
            }
            if (rarityFoilRenderer != null)
            {
                labelMaterialProperties ??= new MaterialPropertyBlock();
                rarityFoilRenderer.GetPropertyBlock(labelMaterialProperties);
                labelMaterialProperties.SetColor(
                    BaseColorId,
                    PremiumDisplayCaseCollectorTierRules.FoilColor(label.Tier));
                rarityFoilRenderer.SetPropertyBlock(labelMaterialProperties);
            }
        }

        public void SetFeaturedBadge(
            string assetName,
            string displayToken,
            string shortName,
            string grade)
        {
            Texture2D artwork = ResolveBadgeArtwork(assetName);
            if (artwork == null
                || featuredBadgeRoot == null
                || featuredBadgeArtworkRenderer == null)
            {
                ClearFeaturedBadge();
                return;
            }

            FeaturedBadgeAssetName = assetName.Trim();
            featuredBadgeRoot.gameObject.SetActive(true);
            featuredBadgeArtworkRenderer.enabled = true;
            badgeMaterialProperties ??= new MaterialPropertyBlock();
            featuredBadgeArtworkRenderer.GetPropertyBlock(
                badgeMaterialProperties);
            badgeMaterialProperties.SetTexture(BadgeBaseMapId, artwork);
            featuredBadgeArtworkRenderer.SetPropertyBlock(
                badgeMaterialProperties);

            Color typographyColor = BadgeTypographyColor(grade);
            if (featuredBadgeTokenMark != null)
            {
                string normalizedToken = (displayToken ?? string.Empty)
                    .Trim()
                    .ToUpperInvariant();
                featuredBadgeTokenMark.text = normalizedToken;
                const float baseCharacterSize = 0.0015f;
                float estimatedWidth = Mathf.Max(
                    0.001f,
                    normalizedToken.Length * baseCharacterSize * 2.8f);
                featuredBadgeTokenMark.characterSize = baseCharacterSize
                    * Mathf.Min(1f, 0.037f / estimatedWidth);
                featuredBadgeTokenMark.color = typographyColor;
            }
            if (featuredBadgeShortNameMark != null)
            {
                featuredBadgeShortNameMark.text = (shortName ?? string.Empty)
                    .Trim()
                    .ToUpperInvariant();
                featuredBadgeShortNameMark.color = new Color(
                    typographyColor.r,
                    typographyColor.g,
                    typographyColor.b,
                    0.82f);
            }
        }

        public void ClearFeaturedBadge()
        {
            FeaturedBadgeAssetName = string.Empty;
            if (featuredBadgeRoot != null)
            {
                featuredBadgeRoot.gameObject.SetActive(false);
            }
            if (featuredBadgeTokenMark != null)
            {
                featuredBadgeTokenMark.text = string.Empty;
            }
            if (featuredBadgeShortNameMark != null)
            {
                featuredBadgeShortNameMark.text = string.Empty;
            }
        }

        public void setCapsuleDimensions(
            PremiumDisplayCaseCapsuleShape shape,
            float diameter,
            float depth,
            float cornerRadius = 0.018f)
        {
            ApplyCapsuleDimensions(new PremiumDisplayCaseCapsuleDimensions(
                shape,
                diameter,
                depth,
                cornerRadius));
        }

        public void play()
        {
            CaptureAuthoredHierarchy();
            revealElapsed = 0f;
            revealPlaying = true;
            revealCallbackFired = false;
            ResetIdleRotation();
            ApplyRevealSample(PremiumDisplayCaseRevealMotion.Evaluate(0f));
        }

        public void SetParallaxInput(Vector2 normalizedTilt)
        {
            targetParallax = Vector2.ClampMagnitude(normalizedTilt, 1f);
        }

        public void SetParallaxForPreview(Vector2 normalizedTilt)
        {
            CaptureAuthoredHierarchy();
            targetParallax = Vector2.ClampMagnitude(normalizedTilt, 1f);
            filteredParallax = targetParallax;
            UpdateParallax(0f);
        }

        public void SetLightingPreset(string presetId)
        {
            CaptureAuthoredHierarchy();
            selectedLightingPreset = PremiumDisplayCaseLightingCatalog.Resolve(
                presetId);
            ApplyLighting(currentRevealLightBoost);
        }

        public void SetRevealProgressForPreview(float normalizedProgress)
        {
            CaptureAuthoredHierarchy();
            revealPlaying = false;
            revealElapsed = Mathf.Clamp01(normalizedProgress)
                * PremiumDisplayCaseRevealMotion.DurationSeconds;
            ApplyRevealSample(PremiumDisplayCaseRevealMotion.Evaluate(revealElapsed));
        }

        public void ConfigureAuthoring(
            Transform authoredCaseRevealRoot,
            Transform authoredBoxParallaxRoot,
            Transform authoredBoxLidRoot,
            Transform authoredAcrylicParallaxRoot,
            Transform authoredInteriorParallaxRoot,
            Transform authoredContentParallaxRoot,
            Transform authoredCircularCapsuleGeometry,
            Transform authoredRoundedSquareCapsuleGeometry,
            Transform authoredContentSlot,
            Transform authoredContentRevealRoot,
            Transform authoredContentOrbitRoot,
            Transform authoredContentFitRoot,
            Transform authoredDevelopmentPlaceholder,
            TextMesh authoredLevelLaserMark,
            TextMesh authoredProductNameLaserMark,
            TextMesh authoredEditionLabelMark,
            TextMesh authoredAcquiredDateLabelMark,
            TextMesh authoredCollectibleIdLabelMark,
            Renderer authoredRarityFoilRenderer,
            Transform authoredFeaturedBadgeRoot,
            Renderer authoredFeaturedBadgeArtworkRenderer,
            TextMesh authoredFeaturedBadgeTokenMark,
            TextMesh authoredFeaturedBadgeShortNameMark,
            PremiumDisplayCaseBadgeArtworkBinding[] authoredFeaturedBadgeArtwork,
            Renderer[] authoredAcrylicRenderers,
            Light[] authoredRevealLights)
        {
            caseRevealRoot = authoredCaseRevealRoot;
            boxParallaxRoot = authoredBoxParallaxRoot;
            boxLidRoot = authoredBoxLidRoot;
            acrylicParallaxRoot = authoredAcrylicParallaxRoot;
            interiorParallaxRoot = authoredInteriorParallaxRoot;
            contentParallaxRoot = authoredContentParallaxRoot;
            circularCapsuleGeometry = authoredCircularCapsuleGeometry;
            roundedSquareCapsuleGeometry = authoredRoundedSquareCapsuleGeometry;
            contentSlot = authoredContentSlot;
            contentRevealRoot = authoredContentRevealRoot;
            contentOrbitRoot = authoredContentOrbitRoot;
            contentFitRoot = authoredContentFitRoot;
            developmentPlaceholder = authoredDevelopmentPlaceholder;
            levelLaserMark = authoredLevelLaserMark;
            productNameLaserMark = authoredProductNameLaserMark;
            editionLabelMark = authoredEditionLabelMark;
            acquiredDateLabelMark = authoredAcquiredDateLabelMark;
            collectibleIdLabelMark = authoredCollectibleIdLabelMark;
            rarityFoilRenderer = authoredRarityFoilRenderer;
            featuredBadgeRoot = authoredFeaturedBadgeRoot;
            featuredBadgeArtworkRenderer = authoredFeaturedBadgeArtworkRenderer;
            featuredBadgeTokenMark = authoredFeaturedBadgeTokenMark;
            featuredBadgeShortNameMark = authoredFeaturedBadgeShortNameMark;
            featuredBadgeArtwork = authoredFeaturedBadgeArtwork ?? Array.Empty<
                PremiumDisplayCaseBadgeArtworkBinding>();
            acrylicRenderers = authoredAcrylicRenderers ?? Array.Empty<Renderer>();
            revealLights = authoredRevealLights ?? Array.Empty<Light>();
            hierarchyCaptured = false;
            CaptureAuthoredHierarchy();
            setCapsulePreset(capsulePreset);
            UseDevelopmentPlaceholder();
            SetIdentification("COLLECTOR EDITION", 1);
            ClearFeaturedBadge();
        }

        private Texture2D ResolveBadgeArtwork(string assetName)
        {
            if (string.IsNullOrWhiteSpace(assetName))
            {
                return null;
            }
            string normalized = assetName.Trim();
            for (int index = 0; index < featuredBadgeArtwork.Length; index++)
            {
                PremiumDisplayCaseBadgeArtworkBinding binding =
                    featuredBadgeArtwork[index];
                if (string.Equals(
                        binding.AssetName,
                        normalized,
                        StringComparison.Ordinal))
                {
                    return binding.Artwork;
                }
            }
            return null;
        }

        private static Color BadgeTypographyColor(string grade)
        {
            _ = grade;
            return new Color(0.66f, 0.69f, 0.71f, 0.90f);
        }

        private void CaptureAuthoredHierarchy()
        {
            if (hierarchyCaptured)
            {
                return;
            }
            if (caseRevealRoot == null
                || boxLidRoot == null
                || contentSlot == null
                || contentRevealRoot == null
                || contentOrbitRoot == null
                || contentFitRoot == null)
            {
                return;
            }

            revealedCasePosition = caseRevealRoot.localPosition;
            caseBaseRotation = caseRevealRoot.localRotation;
            lidClosedPosition = boxLidRoot.localPosition;
            lidClosedRotation = boxLidRoot.localRotation;
            boxParallaxBase = boxParallaxRoot != null
                ? boxParallaxRoot.localPosition
                : Vector3.zero;
            acrylicParallaxBase = acrylicParallaxRoot != null
                ? acrylicParallaxRoot.localPosition
                : Vector3.zero;
            interiorParallaxBase = interiorParallaxRoot != null
                ? interiorParallaxRoot.localPosition
                : Vector3.zero;
            contentParallaxBase = contentParallaxRoot != null
                ? contentParallaxRoot.localPosition
                : Vector3.zero;
            baseLightIntensities = new float[revealLights.Length];
            baseLightColors = new Color[revealLights.Length];
            for (int index = 0; index < revealLights.Length; index++)
            {
                baseLightIntensities[index] = revealLights[index] != null
                    ? revealLights[index].intensity
                    : 0f;
                baseLightColors[index] = revealLights[index] != null
                    ? revealLights[index].color
                    : Color.white;
            }
            hierarchyCaptured = true;
        }

        private void ApplyCapsuleDimensions(
            PremiumDisplayCaseCapsuleDimensions dimensions)
        {
            capsuleDimensions = dimensions;
            bool circular = dimensions.Shape == PremiumDisplayCaseCapsuleShape.Circular;
            if (circularCapsuleGeometry != null)
            {
                circularCapsuleGeometry.gameObject.SetActive(circular);
                circularCapsuleGeometry.localScale = new Vector3(
                    dimensions.Width / AuthoredCapsuleWidth,
                    dimensions.Height / AuthoredCapsuleHeight,
                    dimensions.Depth / AuthoredCapsuleDepth);
            }
            if (roundedSquareCapsuleGeometry != null)
            {
                roundedSquareCapsuleGeometry.gameObject.SetActive(!circular);
                roundedSquareCapsuleGeometry.localScale = new Vector3(
                    dimensions.Width / AuthoredCapsuleWidth,
                    dimensions.Height / AuthoredCapsuleHeight,
                    dimensions.Depth / AuthoredCapsuleDepth);
            }

            Transform content = externalContent.Node != null
                ? externalContent.Node
                : developmentPlaceholder;
            if (content != null && content.gameObject.activeInHierarchy)
            {
                FitAttachedContent(content);
            }
        }

        private void UseDevelopmentPlaceholder()
        {
            if (developmentPlaceholder == null || contentFitRoot == null)
            {
                return;
            }
            developmentPlaceholder.SetParent(contentFitRoot, false);
            developmentPlaceholder.localPosition = Vector3.zero;
            developmentPlaceholder.localRotation = Quaternion.Euler(
                PremiumDisplayCaseContentOptions.Default.InitialEulerAngles);
            developmentPlaceholder.localScale = Vector3.one;
            developmentPlaceholder.gameObject.SetActive(true);
            contentOptions = PremiumDisplayCaseContentOptions.Default;
            FitAttachedContent(developmentPlaceholder);
            ResetIdleRotation();
        }

        private void FitAttachedContent(Transform content)
        {
            if (content == null || contentFitRoot == null)
            {
                return;
            }

            contentFitRoot.localPosition = Vector3.zero;
            contentFitRoot.localScale = Vector3.one;
            if (!TryMeasureContent(content, out Bounds bounds))
            {
                contentFitRoot.localScale = Vector3.one;
                return;
            }

            PremiumDisplayCaseFitResult fit = PremiumDisplayCaseLayout.Fit(
                bounds,
                capsuleDimensions);
            contentFitRoot.localScale = Vector3.one * fit.UniformScale;
            contentFitRoot.localPosition = fit.CenterOffset;
        }

        private bool TryMeasureContent(Transform content, out Bounds bounds)
        {
            measuredRenderers.Clear();
            content.GetComponentsInChildren(true, measuredRenderers);
            bool hasBounds = false;
            bounds = default;
            foreach (Renderer renderer in measuredRenderers)
            {
                if (renderer == null || !renderer.enabled)
                {
                    continue;
                }
                EncapsulateWorldBounds(renderer.bounds, ref bounds, ref hasBounds);
            }
            if (hasBounds)
            {
                return true;
            }

            measuredColliders.Clear();
            content.GetComponentsInChildren(true, measuredColliders);
            foreach (Collider collider in measuredColliders)
            {
                if (collider == null || !collider.enabled)
                {
                    continue;
                }
                EncapsulateWorldBounds(collider.bounds, ref bounds, ref hasBounds);
            }
            return hasBounds;
        }

        private void EncapsulateWorldBounds(
            Bounds worldBounds,
            ref Bounds localBounds,
            ref bool hasBounds)
        {
            Vector3 center = worldBounds.center;
            Vector3 extents = worldBounds.extents;
            for (int x = -1; x <= 1; x += 2)
            {
                for (int y = -1; y <= 1; y += 2)
                {
                    for (int z = -1; z <= 1; z += 2)
                    {
                        Vector3 worldCorner = center + Vector3.Scale(
                            extents,
                            new Vector3(x, y, z));
                        Vector3 localCorner = contentFitRoot.InverseTransformPoint(
                            worldCorner);
                        if (!hasBounds)
                        {
                            localBounds = new Bounds(localCorner, Vector3.zero);
                            hasBounds = true;
                        }
                        else
                        {
                            localBounds.Encapsulate(localCorner);
                        }
                    }
                }
            }
        }

        private void UpdateIdleRotation(float deltaTime)
        {
            if (contentOrbitRoot == null || !contentOptions.IdleRotationEnabled)
            {
                return;
            }
            float period = Mathf.Max(0.1f, contentOptions.IdleRotationPeriodSeconds);
            contentOrbitRoot.Rotate(
                Vector3.up,
                360f / period * Mathf.Max(0f, deltaTime),
                Space.Self);
        }

        private void ResetIdleRotation()
        {
            if (contentOrbitRoot != null)
            {
                contentOrbitRoot.localRotation = Quaternion.identity;
            }
        }

        private void UpdateParallax(float deltaTime)
        {
            float blend = parallaxResponse <= 0f
                ? 1f
                : 1f - Mathf.Exp(-parallaxResponse * Mathf.Max(0f, deltaTime));
            filteredParallax = Vector2.Lerp(filteredParallax, targetParallax, blend);
            PremiumDisplayCaseParallaxSample sample =
                PremiumDisplayCaseParallaxRules.Evaluate(filteredParallax);
            if (boxParallaxRoot != null)
            {
                boxParallaxRoot.localPosition = boxParallaxBase + sample.BoxOffset;
            }
            if (acrylicParallaxRoot != null)
            {
                acrylicParallaxRoot.localPosition =
                    acrylicParallaxBase + sample.AcrylicOffset;
            }
            if (interiorParallaxRoot != null)
            {
                interiorParallaxRoot.localPosition =
                    interiorParallaxBase + sample.InteriorOffset;
            }
            if (contentParallaxRoot != null)
            {
                contentParallaxRoot.localPosition =
                    contentParallaxBase + sample.ContentOffset;
            }
            if (caseRevealRoot != null)
            {
                caseRevealRoot.localRotation = caseBaseRotation
                    * Quaternion.Euler(sample.EulerAngles);
            }
            SetAcrylicProperty(ParallaxTiltId, new Vector4(
                filteredParallax.x,
                filteredParallax.y,
                0f,
                0f));
        }

        private void ApplyRevealSample(PremiumDisplayCaseRevealSample sample)
        {
            if (!hierarchyCaptured)
            {
                return;
            }
            if (caseRevealRoot != null)
            {
                caseRevealRoot.localPosition = revealedCasePosition
                    + Vector3.down * (0.045f * (1f - sample.CaseRise));
                caseRevealRoot.localScale = Vector3.one * sample.CaseScale;
            }
            if (boxLidRoot != null)
            {
                PremiumDisplayCaseLidPose lidPose =
                    PremiumDisplayCaseLidMotion.Evaluate(sample);
                boxLidRoot.localPosition = lidClosedPosition
                    + lidPose.PositionOffset;
                boxLidRoot.localRotation = lidClosedRotation
                    * Quaternion.Euler(lidPose.EulerOffset);
            }
            if (contentRevealRoot != null)
            {
                float visibleScale = Mathf.Clamp(sample.ContentVisibility, 0f, 1.08f);
                contentRevealRoot.localScale = Vector3.one * visibleScale;
            }
            SetAcrylicProperty(RevealVisibilityId, sample.AcrylicVisibility);
            SetAcrylicProperty(RevealSweepId, sample.Sweep);
            currentRevealLightBoost = sample.LightBoost;
            ApplyLighting(currentRevealLightBoost);
        }

        private void ApplyLighting(float revealLightBoost)
        {
            for (int index = 0; index < revealLights.Length; index++)
            {
                Light light = revealLights[index];
                if (light != null)
                {
                    Color authoredColor = index < baseLightColors.Length
                        ? baseLightColors[index]
                        : light.color;
                    float authoredIntensity = index < baseLightIntensities.Length
                        ? baseLightIntensities[index]
                        : light.intensity;
                    light.useColorTemperature = false;
                    light.color = selectedLightingPreset.ColorFor(
                        light.name,
                        authoredColor);
                    light.intensity = authoredIntensity
                        * selectedLightingPreset.IntensityScaleFor(light.name)
                        * Mathf.Lerp(0.55f, 1.32f, revealLightBoost);
                }
            }
        }

        private void SetAcrylicProperty(int propertyId, float value)
        {
            materialProperties ??= new MaterialPropertyBlock();
            foreach (Renderer renderer in acrylicRenderers)
            {
                if (renderer == null)
                {
                    continue;
                }
                renderer.GetPropertyBlock(materialProperties);
                materialProperties.SetFloat(propertyId, value);
                renderer.SetPropertyBlock(materialProperties);
            }
        }

        private void SetAcrylicProperty(int propertyId, Vector4 value)
        {
            materialProperties ??= new MaterialPropertyBlock();
            foreach (Renderer renderer in acrylicRenderers)
            {
                if (renderer == null)
                {
                    continue;
                }
                renderer.GetPropertyBlock(materialProperties);
                materialProperties.SetVector(propertyId, value);
                renderer.SetPropertyBlock(materialProperties);
            }
        }

        private void RestoreExternalContent()
        {
            if (externalContent.Node != null)
            {
                externalContent.Restore();
            }
            externalContent = default;
        }

        private readonly struct ContentAttachment
        {
            public ContentAttachment(Transform node)
            {
                Node = node;
                Parent = node.parent;
                LocalPosition = node.localPosition;
                LocalRotation = node.localRotation;
                LocalScale = node.localScale;
                WasActive = node.gameObject.activeSelf;
            }

            public Transform Node { get; }
            private Transform Parent { get; }
            private Vector3 LocalPosition { get; }
            private Quaternion LocalRotation { get; }
            private Vector3 LocalScale { get; }
            private bool WasActive { get; }

            public void Restore()
            {
                if (Node == null)
                {
                    return;
                }
                Node.SetParent(Parent, false);
                Node.localPosition = LocalPosition;
                Node.localRotation = LocalRotation;
                Node.localScale = LocalScale;
                Node.gameObject.SetActive(WasActive);
            }
        }
    }
}
