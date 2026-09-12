using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    public readonly struct PremiumDisplayCaseLabelData
    {
        public PremiumDisplayCaseLabelData(
            string productName,
            string editionFinish,
            string acquiredDate,
            string rarityLevel,
            string collectibleId)
        {
            ProductName = Normalize(productName);
            EditionFinish = Normalize(editionFinish);
            AcquiredDate = Normalize(acquiredDate);
            RarityLevel = Normalize(rarityLevel);
            CollectibleId = Normalize(collectibleId);
        }

        public string ProductName { get; }
        public string EditionFinish { get; }
        public string AcquiredDate { get; }
        public string RarityLevel { get; }
        public string CollectibleId { get; }

        public bool IsAuthoritative =>
            !string.IsNullOrEmpty(ProductName)
            && !string.IsNullOrEmpty(EditionFinish)
            && !string.IsNullOrEmpty(AcquiredDate)
            && !string.IsNullOrEmpty(RarityLevel)
            && !string.IsNullOrEmpty(CollectibleId)
            && !ContainsPlaceholder(ProductName)
            && !ContainsPlaceholder(EditionFinish)
            && !ContainsPlaceholder(AcquiredDate)
            && !ContainsPlaceholder(RarityLevel)
            && !ContainsPlaceholder(CollectibleId);

        private static string Normalize(string value)
        {
            return (value ?? string.Empty).Trim();
        }

        private static bool ContainsPlaceholder(string value)
        {
            return value.IndexOf("placeholder", StringComparison.OrdinalIgnoreCase) >= 0
                || value.IndexOf("lorem", StringComparison.OrdinalIgnoreCase) >= 0
                || value.IndexOf("sample", StringComparison.OrdinalIgnoreCase) >= 0;
        }
    }

    [DisallowMultipleComponent]
    public sealed class PremiumDisplayCaseShippingPresentation : MonoBehaviour
    {
        private static readonly int LightRevealProgressId =
            Shader.PropertyToID("_LightRevealProgress");
        private static readonly int LightRevealWidthId =
            Shader.PropertyToID("_LightRevealWidth");
        private static readonly int LightRevealStrengthId =
            Shader.PropertyToID("_LightRevealStrength");
        private static readonly int RotationRimProgressId =
            Shader.PropertyToID("_RotationRimProgress");
        private static readonly int RotationRimStrengthId =
            Shader.PropertyToID("_RotationRimStrength");
        private static readonly int SheenCenterId =
            Shader.PropertyToID("_SheenCenter");
        private static readonly int SheenWidthId =
            Shader.PropertyToID("_SheenWidth");
        private static readonly int SheenStrengthId =
            Shader.PropertyToID("_SheenStrength");
        private static readonly int SheenFalloffId =
            Shader.PropertyToID("_SheenFalloff");
        private static readonly int SheenObjectCenterId =
            Shader.PropertyToID("_SheenObjectCenter");
        private static readonly int SheenObjectInvSizeId =
            Shader.PropertyToID("_SheenObjectInvSize");
        private static readonly int RimColorId = Shader.PropertyToID("_RimColor");
        private static readonly int RimStrengthId = Shader.PropertyToID("_RimStrength");
        /// <summary>Authored frosted-shell rim (shader defaults).</summary>
        private static readonly Color NeutralRimColor = new Color(0.96f, 0.94f, 0.90f, 1f);
        private const float RestingRimStrength = 0.18f;

        [SerializeField] private Transform caseAssembly;
        [SerializeField] private Transform contentSlot;
        [SerializeField] private Transform contentFitRoot;
        [SerializeField] private Renderer[] sheenRenderers = Array.Empty<Renderer>();
        [SerializeField] private PremiumDisplayCaseRevealProfile revealProfile;
        [SerializeField] private TextMesh productNameLabel;
        [SerializeField] private TextMesh editionFinishLabel;
        [SerializeField] private TextMesh acquiredDateLabel;
        [SerializeField] private TextMesh rarityLevelLabel;
        [SerializeField] private TextMesh collectibleIdLabel;
        // Defaults are the R004 case's chamber; the V3 slab overrides them
        // with its pocket well (ConfigureContentFit). Older prefabs carry no
        // value for these fields and keep the R004 fit.
        [SerializeField] private Vector3 contentFitAvailableSize =
            new Vector3(0.165f, 0.182f, 0.040f);
        [SerializeField] private float contentFitDepthOffsetMeters = 0.015f;

        private readonly List<RigidbodyState> rigidbodyStates =
            new List<RigidbodyState>();
        private MaterialPropertyBlock materialProperties;
        private ContentAttachment contentAttachment;
        private Vector3 authoredPosition;
        private Quaternion authoredRotation;
        private Vector3 authoredScale;
        private float elapsedSeconds;
        private bool playing;
        private bool completionForwarded;
        private bool lightRevealActive;
        private bool sheenActive;
        private bool authoredPoseCaptured;
        private int activeRotationRimPass;

        public event Action revealCompleted;

        public PremiumDisplayCaseRevealProfile RevealProfile => revealProfile;
        public Transform CaseAssembly => caseAssembly;
        public Transform ContentSlot => contentSlot;
        public Transform AttachedContent => contentAttachment.Node;
        public float ElapsedSeconds => elapsedSeconds;
        public bool IsPlaying => playing;
        public int LightRevealActivationCount { get; private set; }
        public int RotationRimPassCount { get; private set; }
        public int SheenActivationCount { get; private set; }
        public PremiumDisplayCaseShippingPhase Phase { get; private set; } =
            PremiumDisplayCaseShippingPhase.Complete;
        public PremiumDisplayCaseLabelData LabelData { get; private set; }
        public bool HasAuthoritativeLabel => LabelData.IsAuthoritative;
        public IReadOnlyList<Renderer> EffectRenderers => sheenRenderers;
        public bool EffectsAreWired
        {
            get
            {
                if (revealProfile == null
                    || !revealProfile.UsesCc0LightRevealCurve
                    || sheenRenderers == null
                    || sheenRenderers.Length == 0)
                {
                    return false;
                }
                for (int index = 0; index < sheenRenderers.Length; index++)
                {
                    Renderer renderer = sheenRenderers[index];
                    if (renderer == null || renderer.sharedMaterials.Length == 0)
                    {
                        return false;
                    }
                    for (int materialIndex = 0;
                         materialIndex < renderer.sharedMaterials.Length;
                         materialIndex++)
                    {
                        Material material =
                            renderer.sharedMaterials[materialIndex];
                        if (material == null
                            || !material.HasProperty(LightRevealProgressId)
                            || !material.HasProperty(LightRevealStrengthId)
                            || !material.HasProperty(RotationRimProgressId)
                            || !material.HasProperty(RotationRimStrengthId)
                            || !material.HasProperty(SheenCenterId)
                            || !material.HasProperty(SheenStrengthId))
                        {
                            return false;
                        }
                    }
                }
                return true;
            }
        }
        public bool HasFixedScale => transform.localScale == authoredScale;
        public bool ToyAngularVelocityIsZero
        {
            get
            {
                if (AttachedContent == null)
                {
                    return true;
                }
                Rigidbody[] bodies = AttachedContent.GetComponentsInChildren<
                    Rigidbody>(true);
                for (int index = 0; index < bodies.Length; index++)
                {
                    if (bodies[index] != null
                        && bodies[index].angularVelocity.sqrMagnitude > 0.00000001f)
                    {
                        return false;
                    }
                }
                return true;
            }
        }

        private void Awake()
        {
            CaptureAuthoredPose();
            ApplySample(revealProfile != null
                ? revealProfile.FinalSample()
                : default);
        }

        private void OnDisable()
        {
            RestoreContent();
        }

        private void OnDestroy()
        {
            RestoreContent();
        }

        public void ConfigureAuthoring(
            Transform authoredCaseAssembly,
            Transform authoredContentSlot,
            Transform authoredContentFitRoot,
            Renderer[] authoredSheenRenderers,
            PremiumDisplayCaseRevealProfile authoredRevealProfile,
            TextMesh authoredProductNameLabel,
            TextMesh authoredEditionFinishLabel,
            TextMesh authoredAcquiredDateLabel,
            TextMesh authoredRarityLevelLabel,
            TextMesh authoredCollectibleIdLabel)
        {
            caseAssembly = authoredCaseAssembly;
            contentSlot = authoredContentSlot;
            contentFitRoot = authoredContentFitRoot;
            sheenRenderers = authoredSheenRenderers ?? Array.Empty<Renderer>();
            revealProfile = authoredRevealProfile;
            productNameLabel = authoredProductNameLabel;
            editionFinishLabel = authoredEditionFinishLabel;
            acquiredDateLabel = authoredAcquiredDateLabel;
            rarityLevelLabel = authoredRarityLevelLabel;
            collectibleIdLabel = authoredCollectibleIdLabel;
            CaptureAuthoredPose(true);
            ClearLabel();
            ApplySample(revealProfile != null
                ? revealProfile.FinalSample()
                : default);
        }

        /// <summary>
        /// Box (metres, slot-local axes) the attached content must fit, and
        /// how far the content centre sits in front of the slot pivot.
        /// </summary>
        public void ConfigureContentFit(Vector3 availableSize, float depthOffsetMeters)
        {
            if (availableSize.x <= 0f || availableSize.y <= 0f || availableSize.z <= 0f)
            {
                throw new ArgumentOutOfRangeException(nameof(availableSize));
            }
            contentFitAvailableSize = availableSize;
            contentFitDepthOffsetMeters = depthOffsetMeters;
        }

        public Vector3 ContentFitAvailableSize => contentFitAvailableSize;
        public float ContentFitDepthOffsetMeters => contentFitDepthOffsetMeters;

        public void SetLabel(PremiumDisplayCaseLabelData data)
        {
            if (!data.IsAuthoritative)
            {
                throw new ArgumentException(
                    "Display-case labels require authoritative product, edition, date, rarity/level and collectible id data.",
                    nameof(data));
            }
            LabelData = data;
            SetText(productNameLabel, data.ProductName);
            SetText(editionFinishLabel, data.EditionFinish);
            SetText(acquiredDateLabel, "ACQUIRED " + data.AcquiredDate);
            SetText(rarityLevelLabel, data.RarityLevel);
            // The id stays authoritative in the receipt; it is not printed
            // on the plate for now (R053, user 2026-09-09).
            SetText(
                collectibleIdLabel,
                ShowsCollectibleIdOnPlate ? data.CollectibleId : string.Empty);
            // R005 plate (optional): fits every line inside the plate and
            // tints the rarity block. R004 prefabs carry no plate component.
            PremiumDisplayCaseLabelPlate plate =
                GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true);
            if (plate != null)
            {
                plate.Apply(data);
            }
            PremiumDisplayCaseV3RarityCmf rarityCmf =
                GetComponentInChildren<PremiumDisplayCaseV3RarityCmf>(true);
            if (rarityCmf != null)
            {
                rarityCmf.Apply(data.RarityLevel);
            }
        }

        public const bool ShowsCollectibleIdOnPlate = false;

        public void AttachContent(Transform content, Vector3 initialEulerAngles)
        {
            PrepareContent(content, initialEulerAngles);
            FitContent(content);
        }

        public PremiumDisplayCasePocketFitResult AttachContentToCircularPocket(
            Transform content,
            PremiumDisplayCasePocketContentProfile profile)
        {
            PrepareContent(content, profile.InitialEulerAngles);
            return FitContentToCircularPocket(content, profile);
        }

        private void PrepareContent(Transform content, Vector3 initialEulerAngles)
        {
            if (content == null)
            {
                throw new ArgumentNullException(nameof(content));
            }
            if (contentSlot == null || contentFitRoot == null)
            {
                throw new MissingReferenceException(
                    "Shipping display case requires ContentSlot and ContentFit.");
            }
            if (content == transform || content.IsChildOf(transform))
            {
                throw new ArgumentException(
                    "Content must be caller-owned before attachment.",
                    nameof(content));
            }

            RestoreContent();
            HideAuthoredPlaceholders(content);
            contentAttachment = new ContentAttachment(content);
            FreezeRigidbodies(content);
            content.SetParent(contentFitRoot, false);
            content.localPosition = Vector3.zero;
            content.localRotation = Quaternion.Euler(initialEulerAngles);
            content.localScale = Vector3.one;
            content.gameObject.SetActive(true);
        }

        /// <summary>
        /// The authored prefab ships a development coin inside ContentFit.
        /// Real content replaces it; anything else already under ContentFit
        /// would otherwise read as a second object in the case.
        /// </summary>
        private void HideAuthoredPlaceholders(Transform incoming)
        {
            for (int index = 0; index < contentFitRoot.childCount; index++)
            {
                Transform child = contentFitRoot.GetChild(index);
                if (child == incoming)
                {
                    continue;
                }
                child.gameObject.SetActive(false);
            }
        }

        /// <summary>True when only the attached content is active under ContentFit.</summary>
        public bool ContentFitHoldsOnlyAttachedContent
        {
            get
            {
                if (contentFitRoot == null || contentAttachment.Node == null)
                {
                    return false;
                }
                for (int index = 0; index < contentFitRoot.childCount; index++)
                {
                    Transform child = contentFitRoot.GetChild(index);
                    if (child != contentAttachment.Node && child.gameObject.activeSelf)
                    {
                        return false;
                    }
                }
                return true;
            }
        }

        public void DetachContent()
        {
            RestoreContent();
        }

        public void Play(bool reduceMotion)
        {
            if (revealProfile == null)
            {
                throw new MissingReferenceException(
                    "Shipping display case requires a reveal profile.");
            }
            CaptureAuthoredPose();
            elapsedSeconds = reduceMotion
                ? revealProfile.TotalDurationSeconds
                : 0f;
            completionForwarded = false;
            playing = true;
            lightRevealActive = false;
            sheenActive = false;
            activeRotationRimPass = 0;
            LightRevealActivationCount = 0;
            RotationRimPassCount = 0;
            SheenActivationCount = 0;
            ApplySample(reduceMotion
                ? revealProfile.FinalSample()
                : revealProfile.Evaluate(0f));
        }

        public void Tick(float unscaledDeltaTime)
        {
            if (!playing || revealProfile == null)
            {
                return;
            }
            elapsedSeconds = Mathf.Min(
                revealProfile.TotalDurationSeconds,
                elapsedSeconds + Mathf.Max(0f, unscaledDeltaTime));
            PremiumDisplayCaseShippingSample sample =
                revealProfile.Evaluate(elapsedSeconds);
            ApplySample(sample);
            if (!sample.Complete)
            {
                return;
            }

            playing = false;
            if (!completionForwarded)
            {
                completionForwarded = true;
                revealCompleted?.Invoke();
            }
        }

        public void SetTimeForPreview(float elapsed)
        {
            if (revealProfile == null)
            {
                return;
            }
            CaptureAuthoredPose();
            playing = false;
            elapsedSeconds = Mathf.Clamp(
                elapsed,
                0f,
                revealProfile.TotalDurationSeconds);
            ApplySample(revealProfile.Evaluate(elapsedSeconds));
        }

        /// <summary>
        /// Pose and effects driven frame by frame by a director instead of
        /// the profile timeline (R037 emerge → flip choreography). The
        /// profile timeline is stopped; the authored pose stays the anchor.
        /// </summary>
        public void ApplyDirectedPose(PremiumDisplayCaseDirectedPose pose)
        {
            CaptureAuthoredPose();
            playing = false;
            transform.localPosition = authoredPosition + pose.PositionOffset;
            transform.localRotation = authoredRotation
                * Quaternion.Euler(pose.TiltDegrees, pose.YawDegrees, 0f);
            transform.localScale = authoredScale * pose.ScaleMultiplier;
            Phase = pose.Complete
                ? PremiumDisplayCaseShippingPhase.Complete
                : PremiumDisplayCaseShippingPhase.Hold;
            ApplyEffects(new PremiumDisplayCaseShippingSample(
                Phase,
                pose.PositionOffset,
                pose.YawDegrees,
                pose.LightRevealProgress,
                pose.LightRevealWidth,
                pose.LightRevealStrength,
                pose.RotationRimProgress,
                pose.RotationRimStrength,
                0,
                pose.SheenCenter,
                pose.SheenWidth,
                pose.SheenStrength,
                pose.SheenFalloff,
                pose.Complete));
            ApplyRimGlow(pose.RimColor, pose.RimGlow);
            SetLabelAlpha(pose.LabelAlpha);
        }

        /// <summary>
        /// Rarity edge glow on the frosted shell: the material's neutral rim
        /// is the floor; glow adds colour and strength above it.
        /// </summary>
        private void ApplyRimGlow(Color? rimColor, float rimGlow)
        {
            materialProperties ??= new MaterialPropertyBlock();
            float glow = Mathf.Clamp01(rimGlow);
            for (int index = 0; index < sheenRenderers.Length; index++)
            {
                Renderer renderer = sheenRenderers[index];
                if (renderer == null)
                {
                    continue;
                }
                renderer.GetPropertyBlock(materialProperties);
                if (rimColor.HasValue)
                {
                    materialProperties.SetColor(
                        RimColorId,
                        Color.Lerp(NeutralRimColor, rimColor.Value, glow));
                }
                materialProperties.SetFloat(
                    RimStrengthId,
                    Mathf.Lerp(RestingRimStrength, 1f, glow));
                renderer.SetPropertyBlock(materialProperties);
            }
        }

        private void SetLabelAlpha(float alpha)
        {
            float clamped = Mathf.Clamp01(alpha);
            ApplyLabelAlpha(productNameLabel, clamped);
            ApplyLabelAlpha(editionFinishLabel, clamped);
            ApplyLabelAlpha(acquiredDateLabel, clamped);
            ApplyLabelAlpha(rarityLevelLabel, clamped);
            ApplyLabelAlpha(collectibleIdLabel, clamped);
        }

        private static void ApplyLabelAlpha(TextMesh label, float alpha)
        {
            if (label == null)
            {
                return;
            }
            Color color = label.color;
            color.a = alpha;
            label.color = color;
        }

        private void CaptureAuthoredPose(bool force = false)
        {
            if (authoredPoseCaptured && !force)
            {
                return;
            }
            authoredPosition = transform.localPosition;
            authoredRotation = transform.localRotation;
            authoredScale = transform.localScale;
            authoredPoseCaptured = true;
        }

        private void ApplySample(PremiumDisplayCaseShippingSample sample)
        {
            transform.localPosition = authoredPosition + sample.PositionOffset;
            transform.localRotation = authoredRotation
                * Quaternion.Euler(0f, sample.LocalYawDegrees, 0f);
            transform.localScale = authoredScale;
            Phase = sample.Phase;

            bool nextLightRevealActive =
                sample.LightRevealStrength > 0.0001f;
            if (nextLightRevealActive && !lightRevealActive)
            {
                LightRevealActivationCount += 1;
            }
            lightRevealActive = nextLightRevealActive;
            if (sample.RotationRimPass > 0
                && sample.RotationRimPass != activeRotationRimPass)
            {
                RotationRimPassCount += 1;
            }
            activeRotationRimPass = sample.RotationRimPass;
            bool nextSheenActive = sample.SheenStrength > 0.0001f;
            if (nextSheenActive && !sheenActive)
            {
                SheenActivationCount += 1;
            }
            sheenActive = nextSheenActive;
            ApplyEffects(sample);
        }

        private void ApplyEffects(PremiumDisplayCaseShippingSample sample)
        {
            materialProperties ??= new MaterialPropertyBlock();
            for (int index = 0; index < sheenRenderers.Length; index++)
            {
                Renderer renderer = sheenRenderers[index];
                if (renderer == null)
                {
                    continue;
                }
                renderer.GetPropertyBlock(materialProperties);
                materialProperties.SetFloat(
                    LightRevealProgressId,
                    sample.LightRevealProgress);
                materialProperties.SetFloat(
                    LightRevealWidthId,
                    sample.LightRevealWidth);
                materialProperties.SetFloat(
                    LightRevealStrengthId,
                    sample.LightRevealStrength);
                materialProperties.SetFloat(
                    RotationRimProgressId,
                    sample.RotationRimProgress);
                materialProperties.SetFloat(
                    RotationRimStrengthId,
                    sample.RotationRimStrength);
                materialProperties.SetFloat(SheenCenterId, sample.SheenCenter);
                materialProperties.SetFloat(SheenWidthId, sample.SheenWidth);
                materialProperties.SetFloat(SheenStrengthId, sample.SheenStrength);
                materialProperties.SetFloat(SheenFalloffId, sample.SheenFalloff);
                MeshFilter filter = renderer.GetComponent<MeshFilter>();
                if (filter != null && filter.sharedMesh != null)
                {
                    Bounds bounds = filter.sharedMesh.bounds;
                    materialProperties.SetVector(
                        SheenObjectCenterId,
                        bounds.center);
                    materialProperties.SetVector(
                        SheenObjectInvSizeId,
                        new Vector4(
                            1f / Mathf.Max(bounds.size.x, 0.000001f),
                            1f / Mathf.Max(bounds.size.y, 0.000001f),
                            1f / Mathf.Max(bounds.size.z, 0.000001f),
                            0f));
                }
                renderer.SetPropertyBlock(materialProperties);
            }
        }

        private void ClearLabel()
        {
            LabelData = default;
            SetText(productNameLabel, string.Empty);
            SetText(editionFinishLabel, string.Empty);
            SetText(acquiredDateLabel, string.Empty);
            SetText(rarityLevelLabel, string.Empty);
            SetText(collectibleIdLabel, string.Empty);
        }

        private static void SetText(TextMesh label, string value)
        {
            if (label != null)
            {
                label.text = value ?? string.Empty;
            }
        }

        private void FitContent(Transform content)
        {
            if (!TryMeasureWorldBounds(content, out Bounds bounds))
            {
                return;
            }
            Vector3 available = contentFitAvailableSize;
            float scale = Mathf.Min(
                available.x / Mathf.Max(bounds.size.x, 0.0001f),
                Mathf.Min(
                    available.y / Mathf.Max(bounds.size.y, 0.0001f),
                    available.z / Mathf.Max(bounds.size.z, 0.0001f)));
            scale = Mathf.Min(1f, scale);
            contentFitRoot.localScale = Vector3.one * scale;
            if (TryMeasureWorldBounds(content, out Bounds scaledBounds))
            {
                contentFitRoot.position +=
                    contentSlot.position
                    + Vector3.back * contentFitDepthOffsetMeters
                    - scaledBounds.center;
            }
        }

        private PremiumDisplayCasePocketFitResult FitContentToCircularPocket(
            Transform content,
            PremiumDisplayCasePocketContentProfile profile)
        {
            if (!TryMeasureSlotLocalGeometry(content, out List<Vector3> points))
            {
                throw new MissingReferenceException(
                    $"No visible mesh geometry was available for {profile.ModelId}.");
            }

            MeasureSlotLocal(points, out Vector3 minimum, out Vector3 maximum);
            Vector3 boundsCenter = (minimum + maximum) * 0.5f;
            Vector3 planarCenter = profile.Anchor == PremiumDisplayCasePocketAnchor.MechanicalPivot
                ? contentSlot.InverseTransformPoint(content.position)
                : boundsCenter;
            float radialExtent = MeasureRadialExtent(points, planarCenter);
            float depth = maximum.z - minimum.z;
            float radialScale =
                profile.FitDiameterMeters * 0.5f
                / Mathf.Max(radialExtent, 0.0001f);
            float depthScale = profile.ConstrainScaleByDepth
                ? profile.ReferenceDepthMeters / Mathf.Max(depth, 0.0001f)
                : 1f;
            float uniformScale = Mathf.Min(1f, Mathf.Min(radialScale, depthScale));
            contentFitRoot.localScale = Vector3.one * uniformScale;

            if (!TryMeasureSlotLocalGeometry(content, out points))
            {
                throw new MissingReferenceException(
                    $"Scaled geometry disappeared for {profile.ModelId}.");
            }

            MeasureSlotLocal(points, out minimum, out maximum);
            boundsCenter = (minimum + maximum) * 0.5f;
            Vector3 anchorCenter = profile.Anchor == PremiumDisplayCasePocketAnchor.MechanicalPivot
                ? new Vector3(
                    contentSlot.InverseTransformPoint(content.position).x,
                    contentSlot.InverseTransformPoint(content.position).y,
                    boundsCenter.z)
                : boundsCenter;
            depth = maximum.z - minimum.z;
            float frontShift = Mathf.Max(
                0f,
                depth - profile.ReferenceDepthMeters) * 0.5f;
            Vector3 targetCenter = new Vector3(
                0f,
                0f,
                -contentFitDepthOffsetMeters - frontShift);
            contentFitRoot.position +=
                contentSlot.TransformPoint(targetCenter)
                - contentSlot.TransformPoint(anchorCenter);

            if (!TryMeasureSlotLocalGeometry(content, out points))
            {
                throw new MissingReferenceException(
                    $"Fitted geometry disappeared for {profile.ModelId}.");
            }

            MeasureSlotLocal(points, out minimum, out maximum);
            boundsCenter = (minimum + maximum) * 0.5f;
            Vector3 finalCenter = profile.Anchor == PremiumDisplayCasePocketAnchor.MechanicalPivot
                ? new Vector3(
                    contentSlot.InverseTransformPoint(content.position).x,
                    contentSlot.InverseTransformPoint(content.position).y,
                    boundsCenter.z)
                : boundsCenter;
            return new PremiumDisplayCasePocketFitResult(
                uniformScale,
                MeasureRadialExtent(points, finalCenter),
                maximum.z - minimum.z,
                finalCenter - targetCenter);
        }

        private bool TryMeasureSlotLocalGeometry(
            Transform content,
            out List<Vector3> points)
        {
            points = new List<Vector3>();
            MeshFilter[] filters = content.GetComponentsInChildren<MeshFilter>(true);
            for (int filterIndex = 0; filterIndex < filters.Length; filterIndex++)
            {
                MeshFilter filter = filters[filterIndex];
                Renderer renderer = filter.GetComponent<Renderer>();
                if (filter.sharedMesh == null
                    || renderer == null
                    || !renderer.enabled
                    || !renderer.gameObject.activeInHierarchy)
                {
                    continue;
                }

                Vector3[] vertices = filter.sharedMesh.vertices;
                for (int vertexIndex = 0; vertexIndex < vertices.Length; vertexIndex++)
                {
                    Vector3 world = filter.transform.TransformPoint(vertices[vertexIndex]);
                    points.Add(contentSlot.InverseTransformPoint(world));
                }
            }

            return points.Count > 0;
        }

        private static void MeasureSlotLocal(
            List<Vector3> points,
            out Vector3 minimum,
            out Vector3 maximum)
        {
            minimum = points[0];
            maximum = points[0];
            for (int index = 1; index < points.Count; index++)
            {
                minimum = Vector3.Min(minimum, points[index]);
                maximum = Vector3.Max(maximum, points[index]);
            }
        }

        private static float MeasureRadialExtent(
            List<Vector3> points,
            Vector3 planarCenter)
        {
            float maximum = 0f;
            for (int index = 0; index < points.Count; index++)
            {
                Vector2 delta = new Vector2(
                    points[index].x - planarCenter.x,
                    points[index].y - planarCenter.y);
                maximum = Mathf.Max(maximum, delta.magnitude);
            }
            return maximum;
        }

        private static bool TryMeasureWorldBounds(
            Transform content,
            out Bounds bounds)
        {
            Renderer[] renderers = content.GetComponentsInChildren<Renderer>(true);
            bool hasBounds = false;
            bounds = default;
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null || !renderer.enabled)
                {
                    continue;
                }
                if (!hasBounds)
                {
                    bounds = renderer.bounds;
                    hasBounds = true;
                }
                else
                {
                    bounds.Encapsulate(renderer.bounds);
                }
            }
            return hasBounds;
        }

        private void FreezeRigidbodies(Transform content)
        {
            rigidbodyStates.Clear();
            Rigidbody[] bodies = content.GetComponentsInChildren<Rigidbody>(true);
            for (int index = 0; index < bodies.Length; index++)
            {
                Rigidbody body = bodies[index];
                if (body == null)
                {
                    continue;
                }
                rigidbodyStates.Add(new RigidbodyState(body));
                body.linearVelocity = Vector3.zero;
                body.angularVelocity = Vector3.zero;
                body.isKinematic = true;
            }
        }

        private void RestoreContent()
        {
            if (contentAttachment.Node != null)
            {
                contentAttachment.Restore();
            }
            for (int index = 0; index < rigidbodyStates.Count; index++)
            {
                rigidbodyStates[index].Restore();
            }
            rigidbodyStates.Clear();
            contentAttachment = default;
            if (contentFitRoot != null)
            {
                contentFitRoot.localPosition = Vector3.zero;
                contentFitRoot.localRotation = Quaternion.identity;
                contentFitRoot.localScale = Vector3.one;
            }
        }

        private readonly struct RigidbodyState
        {
            public RigidbodyState(Rigidbody body)
            {
                Body = body;
                IsKinematic = body.isKinematic;
                LinearVelocity = body.linearVelocity;
                AngularVelocity = body.angularVelocity;
            }

            private Rigidbody Body { get; }
            private bool IsKinematic { get; }
            private Vector3 LinearVelocity { get; }
            private Vector3 AngularVelocity { get; }

            public void Restore()
            {
                if (Body == null)
                {
                    return;
                }
                Body.isKinematic = IsKinematic;
                Body.linearVelocity = LinearVelocity;
                Body.angularVelocity = AngularVelocity;
            }
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
                Active = node.gameObject.activeSelf;
            }

            public Transform Node { get; }
            private Transform Parent { get; }
            private Vector3 LocalPosition { get; }
            private Quaternion LocalRotation { get; }
            private Vector3 LocalScale { get; }
            private bool Active { get; }

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
                Node.gameObject.SetActive(Active);
            }
        }
    }
}
