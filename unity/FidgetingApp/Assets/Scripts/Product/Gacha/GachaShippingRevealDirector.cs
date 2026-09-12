using System;
using System.Collections.Generic;
using System.Globalization;
using FidgetingApp.DisplayCase;
using UnityEngine;

namespace FidgetingApp.Product.Gacha
{
    public static class GachaNativeHybridCandidateMotion
    {
        public const float DurationSeconds = 0.64f;
        public const float PackLipCrossingProgress = 0.58f;
        public const float MouthViewportYFraction = 0.592f;
        public const float ContainedCaseViewportWidthFraction = 0.42f;
        public const float PackInnerViewportMinX = 0.24f;
        public const float PackInnerViewportMaxX = 0.76f;
        public const float PackViewportMinY = 0.30f;
        public const float PackMouthViewportMaxY = 0.62f;
        public const float MaximumInitialYOffsetMeters = 0.20f;
        public const float MinimumInitialYOffsetMeters = -0.04f;
        public const float FallbackInitialYOffsetMeters = -0.05f;
        /// <summary>
        /// R033 case rise starts slightly underscaled and eases to the
        /// contained viewport scale during the upward motion.
        /// </summary>
        public const float CaseRiseScaleStartFraction = 0.94f;
    }

    public static class GachaShippingLabelAuthority
    {
        public static PremiumDisplayCaseLabelData Create(
            GachaPrizeDefinition prize,
            GachaDrawReceiptRow receiptRow,
            int productLevel)
        {
            if (!string.Equals(
                    prize.Id,
                    receiptRow.Outcome.PrizeId,
                    StringComparison.Ordinal))
            {
                throw new ArgumentException(
                    "Receipt and catalog prize ids must match.",
                    nameof(receiptRow));
            }
            if (!DateTime.TryParse(
                    receiptRow.FirstObtainedAtUtc,
                    CultureInfo.InvariantCulture,
                    DateTimeStyles.RoundtripKind,
                    out DateTime acquiredAt))
            {
                throw new ArgumentException(
                    "Receipt requires an authoritative acquisition timestamp.",
                    nameof(receiptRow));
            }
            if (string.IsNullOrWhiteSpace(receiptRow.CollectibleId))
            {
                throw new ArgumentException(
                    "Receipt requires a durable collectible id.",
                    nameof(receiptRow));
            }
            // R053 (user 2026-09-09): English plate in one typeface; the
            // LEVEL n suffix is dropped for now. productLevel stays in the
            // signature so the receipt path is unchanged.
            _ = productLevel;
            string rarity = receiptRow.Outcome.Rarity.ToString().ToUpperInvariant();
            return new PremiumDisplayCaseLabelData(
                prize.PlateName,
                prize.PlateEdition,
                acquiredAt.ToUniversalTime().ToString(
                    "yyyy-MM-dd",
                    CultureInfo.InvariantCulture),
                rarity,
                receiptRow.CollectibleId);
        }
    }

    [DisallowMultipleComponent]
    public sealed class GachaShippingRevealDirector : MonoBehaviour
    {
        private PremiumDisplayCaseShippingPresentation activeCase;
        private Transform prize;
        private bool completionForwarded;
        private bool nativeHybridCandidate;
        private bool nativeHybridPlaying;
        private bool nativeHybridCrossedPackLip;
        private float nativeHybridElapsedSeconds;
        private Vector3 nativeHybridInitialPosition;
        private Vector3 nativeHybridFinalPosition;
        private Vector3 nativeHybridCaseScale = Vector3.one;
        private Vector3 nativeHybridInitialScale = Vector3.one;

        // R037 shipping choreography (emerge → hold → anticipate → flip →
        // reveal). Offsets are relative to the authored case pose.
        private bool shippingPlaying;
        private float shippingElapsedSeconds;
        private bool shippingCrossedPackLip;
        private bool shippingFrontRevealed;
        private Vector3 shippingInsidePackOffset;
        private Vector3 shippingApexOffset;
        private Vector3 shippingRestOffset;
        private float shippingRestScaleMultiplier = 1f;
        private float shippingCaseWidthMeters = 0.2f;
        private bool shippingBurstEmitted;
        private GachaRevealRarityStyle shippingRarityStyle =
            GachaRevealRarityStyle.For(GachaRarity.Standard);
        private GachaRevealStageFX stageFX;
        private readonly List<Renderer> bladeRenderers = new List<Renderer>();
        private MaterialPropertyBlock bladeProperties;
        private static readonly int EmissionColorId =
            Shader.PropertyToID("_EmissionColor");

        public event Action revealCompleted;
        public event Action caseCrossedPackLip;
        /// <summary>The front face has landed; reveal effects start here.</summary>
        public event Action frontRevealed;

        public PremiumDisplayCaseShippingPresentation ActiveCase => activeCase;
        public Transform Prize => prize;
        public float HandoffDurationSeconds =>
            nativeHybridCandidate
                ? GachaNativeHybridCandidateMotion.DurationSeconds
                : GachaShippingRevealChoreography.PullSeconds;
        public bool IsNativeHybridCandidate => nativeHybridCandidate;
        public bool IsShippingChoreography =>
            activeCase != null && !nativeHybridCandidate;
        public float ShippingElapsedSeconds => shippingElapsedSeconds;
        public bool ShippingFrontRevealed => shippingFrontRevealed;
        public bool ShippingStageFXWired => stageFX != null && stageFX.IsWired;
        public float NativeHybridProgress { get; private set; }
        public Vector3 NativeHybridInitialPosition => nativeHybridInitialPosition;
        public Vector3 NativeHybridFinalPosition => nativeHybridFinalPosition;
        public Vector3 NativeHybridCaseScale => nativeHybridCaseScale;
        public Vector3 NativeHybridInitialScale => nativeHybridInitialScale;
        public EntityId NativeHybridCaseEntityId =>
            activeCase != null ? activeCase.GetEntityId() : default;
        public string NativeHybridCaseRootName =>
            activeCase != null ? activeCase.gameObject.name : string.Empty;
        public string NativeHybridCaseTypeName =>
            activeCase != null
                ? activeCase.GetType().FullName
                : string.Empty;
        public int NativeHybridCaseRendererCount =>
            activeCase != null
                ? activeCase.GetComponentsInChildren<Renderer>(true).Length
                : 0;
        public bool HasCanonicalNativeHybridCase =>
            nativeHybridCandidate
            && activeCase != null
            && activeCase.gameObject.name
                == PremiumDisplayCaseShippingFactory
                    .NativeHybridPresentationInstanceName
            && activeCase.CaseAssembly != null
            && prize != null
            && prize.IsChildOf(activeCase.ContentSlot)
            && !NativeHybridCaseEntityId.Equals(default(EntityId));
        public bool IsComplete { get; private set; }

        public void Begin(
            GachaPrizeDefinition prizeDefinition,
            GachaDrawReceiptRow receiptRow,
            int productLevel,
            Transform prizeNode,
            bool reduceMotion)
        {
            Begin(
                prizeDefinition,
                receiptRow,
                productLevel,
                prizeNode,
                reduceMotion,
                false);
        }

        public void BeginNativeHybridCandidate(
            GachaPrizeDefinition prizeDefinition,
            GachaDrawReceiptRow receiptRow,
            int productLevel,
            Transform prizeNode,
            bool reduceMotion)
        {
            Begin(
                prizeDefinition,
                receiptRow,
                productLevel,
                prizeNode,
                reduceMotion,
                true);
        }

        private void Begin(
            GachaPrizeDefinition prizeDefinition,
            GachaDrawReceiptRow receiptRow,
            int productLevel,
            Transform prizeNode,
            bool reduceMotion,
            bool useNativeHybridCandidate)
        {
            if (prizeDefinition.Kind != GachaPrizeKind.Toy
                || !string.Equals(
                    prizeDefinition.ContentReference,
                    "toy/metal-three-blade",
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    "Shipping display-case reveal accepts only the canonical Toy content.");
            }
            if (prizeNode == null)
            {
                throw new ArgumentNullException(nameof(prizeNode));
            }

            // Dismiss() disposes stage effects, but effects adopted from the
            // storefront's stage entry (Pack-hue dim) must survive into this
            // reveal, otherwise the tint drops out on the first case frame.
            GachaRevealStageFX adoptedStageFX = stageFX;
            stageFX = null;
            Dismiss();
            stageFX = adoptedStageFX;
            nativeHybridCandidate = useNativeHybridCandidate;
            activeCase = nativeHybridCandidate
                ? PremiumDisplayCaseShippingFactory
                    .InstantiateNativeHybridBaseline(transform)
                : PremiumDisplayCaseShippingFactory.Instantiate(transform);
            activeCase.name = nativeHybridCandidate
                ? PremiumDisplayCaseShippingFactory
                    .NativeHybridPresentationInstanceName
                : PremiumDisplayCaseShippingFactory.PresentationInstanceName;
            activeCase.SetLabel(GachaShippingLabelAuthority.Create(
                prizeDefinition,
                receiptRow,
                productLevel));
            if (nativeHybridCandidate)
            {
                activeCase.AttachContent(
                    prizeNode,
                    PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
            }
            else
            {
                activeCase.AttachContentToCircularPocket(
                    prizeNode,
                    PremiumDisplayCaseV3PocketProfiles.Resolve(
                        ProductCatalog.MetalThreeBladeModelId));
            }
            Debug.Log(
                "PDC_GACHA_BEGIN "
                + $"case={activeCase.name} "
                + $"renderers={activeCase.GetComponentsInChildren<Renderer>(true).Length} "
                + $"screen={Screen.width}x{Screen.height}");
            activeCase.revealCompleted += HandleRevealComplete;
            prize = prizeNode;
            IsComplete = false;
            completionForwarded = false;
            PendingReduceMotion = reduceMotion;
            if (nativeHybridCandidate)
            {
                PrepareNativeHybridCandidate();
            }
            else
            {
                shippingRarityStyle = GachaRevealRarityStyle.For(
                    receiptRow.Outcome.Rarity);
                PrepareShippingChoreography();
            }
        }

        public bool PendingReduceMotion { get; private set; }

        public void Play()
        {
            if (activeCase == null)
            {
                throw new InvalidOperationException(
                    "Reveal must be prepared before play.");
            }
            if (nativeHybridCandidate)
            {
                if (PendingReduceMotion)
                {
                    ApplyNativeHybridProgress(1f);
                    CompleteReveal();
                    return;
                }
                nativeHybridPlaying = true;
                nativeHybridElapsedSeconds = 0f;
                ApplyNativeHybridProgress(0f);
                return;
            }
            if (PendingReduceMotion)
            {
                shippingPlaying = true;
                shippingElapsedSeconds =
                    GachaShippingRevealChoreography.CompleteSeconds;
                ApplyShippingChoreography(shippingElapsedSeconds);
                CompleteReveal();
                return;
            }
            shippingPlaying = true;
            shippingElapsedSeconds = 0f;
            ApplyShippingChoreography(0f);
        }

        public void Skip()
        {
            if (activeCase == null)
            {
                throw new InvalidOperationException(
                    "Reveal must be prepared before skip.");
            }
            if (nativeHybridCandidate)
            {
                nativeHybridPlaying = false;
                ApplyNativeHybridProgress(1f);
                CompleteReveal();
                return;
            }
            shippingPlaying = true;
            shippingElapsedSeconds = GachaShippingRevealChoreography.CompleteSeconds;
            ApplyShippingChoreography(shippingElapsedSeconds);
            CompleteReveal();
        }

        public void SetNativeHybridPreviewProgress(float progress)
        {
            if (!nativeHybridCandidate || activeCase == null)
            {
                throw new InvalidOperationException(
                    "Native hybrid preview must be prepared first.");
            }
            nativeHybridPlaying = false;
            ApplyNativeHybridProgress(progress);
        }

        public void Tick(float unscaledDeltaTime)
        {
            if (nativeHybridCandidate)
            {
                if (!nativeHybridPlaying)
                {
                    return;
                }
                nativeHybridElapsedSeconds = Mathf.Min(
                    GachaNativeHybridCandidateMotion.DurationSeconds,
                    nativeHybridElapsedSeconds
                        + Mathf.Max(0f, unscaledDeltaTime));
                ApplyNativeHybridProgress(
                    nativeHybridElapsedSeconds
                        / GachaNativeHybridCandidateMotion.DurationSeconds);
                if (NativeHybridProgress >= 1f)
                {
                    nativeHybridPlaying = false;
                    CompleteReveal();
                }
                return;
            }
            if (!shippingPlaying || activeCase == null)
            {
                return;
            }
            shippingElapsedSeconds += Mathf.Max(0f, unscaledDeltaTime);
            ApplyShippingChoreography(shippingElapsedSeconds);
            if (GachaShippingRevealChoreography.IsComplete(shippingElapsedSeconds))
            {
                // Keep ticking: the case idles (±3° yaw) under the result panel.
                CompleteReveal();
            }
        }

        public void Dismiss()
        {
            if (activeCase != null)
            {
                activeCase.revealCompleted -= HandleRevealComplete;
                activeCase.DetachContent();
                DestroyOwned(activeCase.gameObject);
            }
            stageFX?.Dispose();
            stageFX = null;
            activeCase = null;
            prize = null;
            IsComplete = false;
            completionForwarded = false;
            PendingReduceMotion = false;
            nativeHybridCandidate = false;
            nativeHybridPlaying = false;
            nativeHybridCrossedPackLip = false;
            nativeHybridElapsedSeconds = 0f;
            NativeHybridProgress = 0f;
            nativeHybridInitialPosition = Vector3.zero;
            nativeHybridFinalPosition = Vector3.zero;
            nativeHybridCaseScale = Vector3.one;
            nativeHybridInitialScale = Vector3.one;
            shippingPlaying = false;
            shippingElapsedSeconds = 0f;
            shippingCrossedPackLip = false;
            shippingFrontRevealed = false;
            shippingInsidePackOffset = Vector3.zero;
            shippingApexOffset = Vector3.zero;
            shippingRestOffset = Vector3.zero;
            shippingRestScaleMultiplier = 1f;
            shippingBurstEmitted = false;
            bladeRenderers.Clear();
        }

        private void Update()
        {
            Tick(Time.unscaledDeltaTime);
        }

        private void OnDisable()
        {
            Dismiss();
        }

        private void HandleRevealComplete()
        {
            CompleteReveal();
        }

        private void CompleteReveal()
        {
            IsComplete = true;
            if (completionForwarded)
            {
                return;
            }
            completionForwarded = true;
            Debug.Log(
                "PDC_GACHA_COMPLETE "
                + $"t={shippingElapsedSeconds:F3} "
                + $"scale={(activeCase != null ? activeCase.transform.localScale : Vector3.zero):F4} "
                + $"position={(activeCase != null ? activeCase.transform.localPosition : Vector3.zero):F4}");
            revealCompleted?.Invoke();
        }

        /// <summary>
        /// Stage effects created when the native storefront entered the gacha
        /// stage (dim cave behind the sealed Pack). The director takes
        /// ownership and drives them through the reveal.
        /// </summary>
        public void AdoptStageFX(GachaRevealStageFX fx)
        {
            if (fx == null || fx == stageFX)
            {
                return;
            }
            stageFX?.Dispose();
            stageFX = fx;
        }

        /// <summary>
        /// Measures rest and inside-Pack offsets on screen so the pull reads
        /// the same on every device: the case top starts 20 pt above the
        /// Pack mouth line and the case centre rests at 44% from the top.
        /// </summary>
        private void PrepareShippingChoreography()
        {
            activeCase.ApplyDirectedPose(
                PremiumDisplayCaseDirectedPose.Rest(
                    GachaShippingRevealChoreography.BackYawDegrees,
                    0f,
                    false));
            shippingRestScaleMultiplier = ResolveScaleMultiplierForViewportWidth(
                GachaShippingRevealChoreography.RestCaseViewportWidthFraction);
            MeasureShippingOffsets();
            shippingElapsedSeconds = 0f;
            shippingPlaying = false;
            shippingCrossedPackLip = false;
            shippingFrontRevealed = false;
            shippingBurstEmitted = false;
            PrepareBladeEmissive();
            ApplyShippingChoreography(0f);
            ShrinkStartUntilInsidePack();
            Debug.Log(
                "PDC_GACHA_PREP "
                + $"scale={activeCase.transform.localScale:F4} "
                + $"position={activeCase.transform.localPosition:F4} "
                + $"inside={shippingInsidePackOffset:F4} "
                + $"rest={shippingRestOffset:F4}");

            Camera camera = Camera.main;
            if (stageFX == null)
            {
                stageFX = new GachaRevealStageFX(transform, camera);
            }
            if (camera != null)
            {
                stageFX.PlaceForCaseDistance(Vector3.Distance(
                    camera.transform.position,
                    activeCase.transform.position));
            }
            // Case (and prize) renderers sort above the stage backdrop so the
            // frosted shells still blend over it; sortingOrder outranks render
            // queue in Unity's transparent sort.
            Renderer[] caseRenderers = activeCase.GetComponentsInChildren<Renderer>(true);
            for (int index = 0; index < caseRenderers.Length; index++)
            {
                if (caseRenderers[index] != null)
                {
                    caseRenderers[index].sortingOrder = GachaRevealStageFX.CaseSortingOrder;
                }
            }
        }

        private void ApplyShippingChoreography(float seconds)
        {
            float pull = GachaShippingRevealChoreography.PullProgress(seconds);
            float glow = GachaShippingRevealChoreography.GlowFraction(seconds)
                * shippingRarityStyle.GlowIntensity;
            PremiumDisplayCaseDirectedPose pose =
                PremiumDisplayCaseDirectedPose.Rest(
                    GachaShippingRevealChoreography.YawDegrees(seconds),
                    GachaShippingRevealChoreography.LabelAlpha(seconds),
                    GachaShippingRevealChoreography.IsComplete(seconds));
            pose.PositionOffset = Vector3.Lerp(
                Vector3.Lerp(shippingInsidePackOffset, shippingApexOffset, pull),
                shippingRestOffset,
                GachaShippingRevealChoreography.SettleProgress(seconds));
            pose.TiltDegrees = GachaShippingRevealChoreography.TiltDegrees(seconds);
            pose.ScaleMultiplier = shippingRestScaleMultiplier
                * GachaShippingRevealChoreography.ScaleMultiplier(seconds);
            pose.RimColor = shippingRarityStyle.Glow;
            pose.RimGlow = glow;
            activeCase.ApplyDirectedPose(pose);
            ApplyBladeEmissive(
                GachaShippingRevealChoreography.BladeEmissive(seconds));

            if (stageFX != null)
            {
                stageFX.SetStageStrength(
                    GachaShippingRevealChoreography.StageDim(seconds));
                stageFX.SetFlash(
                    GachaShippingRevealChoreography.FlashOpacity(
                        seconds,
                        shippingRarityStyle),
                    Color.white);
                stageFX.SetHalo(
                    GachaShippingRevealChoreography.HaloOpacityAt(seconds),
                    shippingRarityStyle.Glow,
                    shippingCaseWidthMeters
                        * GachaShippingRevealChoreography.HaloRadiusCaseWidths
                        * 0.5f,
                    activeCase.transform.position);
            }

            // Pack release is a played beat: Prepare samples t = 0 too, but
            // the native Pack may only drop once the reveal is playing.
            if (shippingPlaying
                && !shippingCrossedPackLip
                && GachaShippingRevealChoreography.HasCrossedPackLip(seconds))
            {
                shippingCrossedPackLip = true;
                Debug.Log(
                    "PDC_GACHA_PACK_LIP "
                    + $"t={seconds:F3} "
                    + $"scale={activeCase.transform.localScale:F4} "
                    + $"position={activeCase.transform.localPosition:F4}");
                caseCrossedPackLip?.Invoke();
            }
            if (!shippingFrontRevealed
                && seconds >= GachaShippingRevealChoreography.RevealSeconds)
            {
                shippingFrontRevealed = true;
                Debug.Log(
                    "PDC_GACHA_FRONT "
                    + $"t={seconds:F3} "
                    + $"scale={activeCase.transform.localScale:F4} "
                    + $"position={activeCase.transform.localPosition:F4}");
                EmitRevealBurst();
                frontRevealed?.Invoke();
            }
        }

        private void EmitRevealBurst()
        {
            if (shippingBurstEmitted || stageFX == null)
            {
                return;
            }
            shippingBurstEmitted = true;
            Camera camera = Camera.main;
            if (camera == null
                || !TryMeasureBounds(activeCase.CaseAssembly, out Bounds bounds))
            {
                return;
            }
            float pixelsPerMeter = PixelsPerMeterAt(camera, bounds.center);
            stageFX.EmitBurst(
                bounds.center,
                new Vector2(bounds.extents.x, bounds.extents.y),
                shippingRarityStyle.ParticleCount,
                shippingRarityStyle.Glow,
                pixelsPerMeter);
        }

        /// <summary>
        /// Rarity colour on the prize at reveal. The retired procedural frame
        /// lit its dark insets fully; the GEEONE satin body (R053) only takes
        /// a faint tint so it never reads as a white blob.
        /// The prize is caller-owned content; only its emission is driven,
        /// on a per-reveal material instance.
        /// </summary>
        public const float GeeoneBodyEmissiveScale = 0.12f;

        private static float EmissiveScaleFor(string rendererName)
        {
            switch (rendererName)
            {
                case "ThreeBladeInsets":
                    return 1f;
                case "Rotor_Body":
                    return GeeoneBodyEmissiveScale;
                default:
                    return 0f;
            }
        }

        private void PrepareBladeEmissive()
        {
            bladeRenderers.Clear();
            if (prize == null)
            {
                return;
            }
            Renderer[] renderers = prize.GetComponentsInChildren<Renderer>(true);
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null
                    || EmissiveScaleFor(renderer.gameObject.name) <= 0f)
                {
                    continue;
                }
                Material instance = renderer.material;
                if (instance != null && instance.HasProperty(EmissionColorId))
                {
                    instance.EnableKeyword("_EMISSION");
                    instance.globalIlluminationFlags =
                        MaterialGlobalIlluminationFlags.RealtimeEmissive;
                    bladeRenderers.Add(renderer);
                }
            }
        }

        private void ApplyBladeEmissive(float emissive)
        {
            if (bladeRenderers.Count == 0)
            {
                return;
            }
            bladeProperties ??= new MaterialPropertyBlock();
            Color emission = shippingRarityStyle.Glow
                * (emissive * shippingRarityStyle.GlowIntensity * 1.6f);
            for (int index = 0; index < bladeRenderers.Count; index++)
            {
                Renderer renderer = bladeRenderers[index];
                if (renderer == null)
                {
                    continue;
                }
                Color scaled = emission
                    * EmissiveScaleFor(renderer.gameObject.name);
                scaled.a = 1f;
                renderer.GetPropertyBlock(bladeProperties);
                bladeProperties.SetColor(EmissionColorId, scaled);
                renderer.SetPropertyBlock(bladeProperties);
            }
        }

        /// <summary>
        /// The case must start hidden behind the native Pack. Unlike the R030
        /// candidate this never throws: on a narrow aspect it lowers the rest
        /// scale a step at a time until the start pose fits the Pack region.
        /// </summary>
        private void ShrinkStartUntilInsidePack()
        {
            for (int attempt = 0; attempt < 6; attempt++)
            {
                if (StartPoseIsInsidePack())
                {
                    return;
                }
                shippingRestScaleMultiplier *= 0.92f;
                MeasureShippingOffsets();
                ApplyShippingChoreography(0f);
            }
        }

        /// <summary>
        /// Offsets depend on scale, so each is measured at the scale it plays
        /// at: the rest offset at rest scale, the inside-Pack offset at the
        /// pull start scale.
        /// </summary>
        private void MeasureShippingOffsets()
        {
            PremiumDisplayCaseDirectedPose measure =
                PremiumDisplayCaseDirectedPose.Rest(
                    GachaShippingRevealChoreography.BackYawDegrees,
                    0f,
                    false);
            measure.ScaleMultiplier = shippingRestScaleMultiplier;
            activeCase.ApplyDirectedPose(measure);
            shippingRestOffset = Vector3.up * ResolveOffsetForViewportY(
                GachaShippingRevealChoreography.RestCenterViewportYFraction,
                useTopEdge: false);
            shippingApexOffset = Vector3.up * ResolveOffsetForViewportY(
                GachaShippingRevealChoreography.PullApexCenterViewportYFraction,
                useTopEdge: false);
            if (TryMeasureBounds(activeCase.CaseAssembly, out Bounds restBounds))
            {
                shippingCaseWidthMeters = restBounds.size.x;
            }
            measure.ScaleMultiplier = shippingRestScaleMultiplier
                * GachaShippingRevealChoreography.PullStartScaleFraction;
            activeCase.ApplyDirectedPose(measure);
            float peekFraction = ResolvePointsAsViewportFraction(
                GachaShippingRevealChoreography.PullStartPeekPoints);
            shippingInsidePackOffset = Vector3.up * ResolveOffsetForViewportY(
                GachaShippingRevealChoreography.MouthViewportYFraction + peekFraction,
                useTopEdge: true);
        }

        private bool StartPoseIsInsidePack()
        {
            Camera camera = Camera.main;
            if (camera == null
                || Screen.width <= 0
                || Screen.height <= 0
                || activeCase.CaseAssembly == null
                || !TryMeasureBounds(activeCase.CaseAssembly, out Bounds bounds)
                || !TryProjectBounds(camera, bounds, out Rect screenBounds))
            {
                return true;
            }
            // The 20 pt peek above the mouth is intended; only the sides and
            // the bottom must stay behind the Pack.
            return screenBounds.xMin >= Screen.width
                    * GachaNativeHybridCandidateMotion.PackInnerViewportMinX
                && screenBounds.xMax <= Screen.width
                    * GachaNativeHybridCandidateMotion.PackInnerViewportMaxX
                && screenBounds.yMin >= Screen.height
                    * GachaNativeHybridCandidateMotion.PackViewportMinY;
        }

        private float ResolveScaleMultiplierForViewportWidth(float widthFraction)
        {
            Camera camera = Camera.main;
            if (camera == null
                || Screen.width <= 0
                || activeCase.CaseAssembly == null
                || !TryMeasureBounds(activeCase.CaseAssembly, out Bounds bounds)
                || !TryProjectBounds(camera, bounds, out Rect screenBounds)
                || screenBounds.width <= 0.0001f)
            {
                return 1f;
            }
            return Mathf.Clamp(
                Screen.width * widthFraction / screenBounds.width,
                0.3f,
                1.6f);
        }

        /// <summary>Points on a 3x display as a fraction of screen height.</summary>
        private static float ResolvePointsAsViewportFraction(float points)
        {
            if (Screen.height <= 0)
            {
                return 0f;
            }
            float scale = Screen.dpi > 0f ? Screen.dpi / 163f : 3f;
            return points * scale / Screen.height;
        }

        /// <summary>
        /// Vertical offset (metres) from the authored pose that puts the case
        /// top edge (or centre) at <paramref name="viewportYFraction"/> of the
        /// screen height, measured from the bottom in Unity screen space.
        /// </summary>
        private float ResolveOffsetForViewportY(
            float viewportYFraction,
            bool useTopEdge)
        {
            Camera camera = Camera.main;
            if (camera == null
                || Screen.height <= 0
                || activeCase.CaseAssembly == null
                || !TryMeasureBounds(activeCase.CaseAssembly, out Bounds bounds))
            {
                return 0f;
            }
            Vector3 anchor = useTopEdge
                ? new Vector3(bounds.center.x, bounds.max.y, bounds.center.z)
                : bounds.center;
            float currentY = camera.WorldToScreenPoint(anchor).y;
            float pixelsPerMeter = PixelsPerMeterAt(camera, anchor);
            if (Mathf.Abs(pixelsPerMeter) <= 0.0001f)
            {
                return 0f;
            }
            float desiredY = Screen.height * viewportYFraction;
            return Mathf.Clamp(
                (desiredY - currentY) / pixelsPerMeter,
                -GachaShippingRevealChoreography.MaximumRestOffsetMeters,
                GachaShippingRevealChoreography.MaximumRestOffsetMeters);
        }

        private static float PixelsPerMeterAt(Camera camera, Vector3 worldPoint)
        {
            const float sampleMeters = 0.01f;
            float baseY = camera.WorldToScreenPoint(worldPoint).y;
            float sampledY = camera.WorldToScreenPoint(
                worldPoint + Vector3.up * sampleMeters).y;
            return (sampledY - baseY) / sampleMeters;
        }

        private void PrepareNativeHybridCandidate()
        {
            activeCase.SetTimeForPreview(
                activeCase.RevealProfile.TotalDurationSeconds);
            nativeHybridCaseScale = ResolveNativeHybridCaseScale();
            nativeHybridInitialScale = nativeHybridCaseScale
                * GachaNativeHybridCandidateMotion.CaseRiseScaleStartFraction;
            activeCase.transform.localScale = nativeHybridInitialScale;
            nativeHybridFinalPosition = activeCase.transform.localPosition;
            nativeHybridInitialPosition = nativeHybridFinalPosition
                + Vector3.up * ResolveNativeHybridInitialYOffset();
            nativeHybridElapsedSeconds = 0f;
            NativeHybridProgress = 0f;
            nativeHybridPlaying = false;
            nativeHybridCrossedPackLip = false;
            activeCase.transform.localPosition = nativeHybridInitialPosition;
            EnsureNativeHybridCaseStartsInsidePack();
        }

        private Vector3 ResolveNativeHybridCaseScale()
        {
            Camera camera = Camera.main;
            if (camera == null
                || Screen.width <= 0
                || activeCase.CaseAssembly == null
                || !TryMeasureBounds(
                    activeCase.CaseAssembly,
                    out Bounds bounds)
                || !TryProjectBounds(camera, bounds, out Rect screenBounds)
                || screenBounds.width <= 0.0001f)
            {
                return Vector3.one;
            }

            float scale = Mathf.Clamp(
                Screen.width
                    * GachaNativeHybridCandidateMotion
                        .ContainedCaseViewportWidthFraction
                    / screenBounds.width,
                0.35f,
                1f);
            return Vector3.one * scale;
        }

        private float ResolveNativeHybridInitialYOffset()
        {
            Camera camera = Camera.main;
            if (camera == null
                || Screen.height <= 0
                || activeCase.CaseAssembly == null
                || !TryMeasureBounds(
                    activeCase.CaseAssembly,
                    out Bounds bounds))
            {
                return GachaNativeHybridCandidateMotion
                    .FallbackInitialYOffsetMeters;
            }

            Vector3 top = new Vector3(
                bounds.center.x,
                bounds.max.y,
                bounds.center.z);
            float currentY = camera.WorldToScreenPoint(top).y;
            float offsetSampleMeters = 0.01f;
            float sampledY = camera.WorldToScreenPoint(
                top + Vector3.up * offsetSampleMeters).y;
            float pixelsPerMeter = (sampledY - currentY)
                / offsetSampleMeters;
            if (Mathf.Abs(pixelsPerMeter) <= 0.0001f)
            {
                return GachaNativeHybridCandidateMotion
                    .FallbackInitialYOffsetMeters;
            }

            float desiredY = Screen.height
                * GachaNativeHybridCandidateMotion.MouthViewportYFraction;
            return Mathf.Clamp(
                (desiredY - currentY) / pixelsPerMeter,
                -GachaNativeHybridCandidateMotion.MaximumInitialYOffsetMeters,
                GachaNativeHybridCandidateMotion.MinimumInitialYOffsetMeters);
        }

        private void EnsureNativeHybridCaseStartsInsidePack()
        {
            Camera camera = Camera.main;
            if (camera == null
                || Screen.width <= 0
                || Screen.height <= 0
                || activeCase.CaseAssembly == null
                || !TryMeasureBounds(
                    activeCase.CaseAssembly,
                    out Bounds bounds)
                || !TryProjectBounds(camera, bounds, out Rect screenBounds))
            {
                return;
            }

            float minX = Screen.width
                * GachaNativeHybridCandidateMotion.PackInnerViewportMinX;
            float maxX = Screen.width
                * GachaNativeHybridCandidateMotion.PackInnerViewportMaxX;
            float minY = Screen.height
                * GachaNativeHybridCandidateMotion.PackViewportMinY;
            float maxY = Screen.height
                * GachaNativeHybridCandidateMotion.PackMouthViewportMaxY;
            if (screenBounds.xMin < minX
                || screenBounds.xMax > maxX
                || screenBounds.yMin < minY
                || screenBounds.yMax > maxY)
            {
                throw new InvalidOperationException(
                    "native-hybrid-case-not-contained-by-pack");
            }
        }

        private void ApplyNativeHybridProgress(float progress)
        {
            NativeHybridProgress = Mathf.Clamp01(progress);
            float eased = NativeHybridProgress * NativeHybridProgress
                * (3f - 2f * NativeHybridProgress);
            activeCase.transform.localPosition = Vector3.Lerp(
                nativeHybridInitialPosition,
                nativeHybridFinalPosition,
                eased);
            activeCase.transform.localScale = Vector3.Lerp(
                nativeHybridInitialScale,
                nativeHybridCaseScale,
                eased);
            if (!nativeHybridCrossedPackLip
                && NativeHybridProgress
                    >= GachaNativeHybridCandidateMotion
                        .PackLipCrossingProgress)
            {
                nativeHybridCrossedPackLip = true;
                caseCrossedPackLip?.Invoke();
            }
        }

        private static bool TryMeasureBounds(
            Transform root,
            out Bounds bounds)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            bounds = default;
            bool found = false;
            for (int index = 0; index < renderers.Length; index++)
            {
                Renderer renderer = renderers[index];
                if (renderer == null || !renderer.enabled)
                {
                    continue;
                }
                if (!found)
                {
                    bounds = renderer.bounds;
                    found = true;
                }
                else
                {
                    bounds.Encapsulate(renderer.bounds);
                }
            }
            return found;
        }

        private static bool TryProjectBounds(
            Camera camera,
            Bounds bounds,
            out Rect screenBounds)
        {
            screenBounds = default;
            if (camera == null)
            {
                return false;
            }

            Vector3 min = bounds.min;
            Vector3 max = bounds.max;
            Vector3[] corners =
            {
                new Vector3(min.x, min.y, min.z),
                new Vector3(min.x, min.y, max.z),
                new Vector3(min.x, max.y, min.z),
                new Vector3(min.x, max.y, max.z),
                new Vector3(max.x, min.y, min.z),
                new Vector3(max.x, min.y, max.z),
                new Vector3(max.x, max.y, min.z),
                new Vector3(max.x, max.y, max.z)
            };

            float minX = float.MaxValue;
            float maxX = float.MinValue;
            float minY = float.MaxValue;
            float maxY = float.MinValue;
            for (int index = 0; index < corners.Length; index++)
            {
                Vector3 point = camera.WorldToScreenPoint(corners[index]);
                if (point.z <= 0f)
                {
                    return false;
                }
                minX = Mathf.Min(minX, point.x);
                maxX = Mathf.Max(maxX, point.x);
                minY = Mathf.Min(minY, point.y);
                maxY = Mathf.Max(maxY, point.y);
            }
            screenBounds = Rect.MinMaxRect(minX, minY, maxX, maxY);
            return true;
        }

        private static void DestroyOwned(GameObject target)
        {
            if (target == null)
            {
                return;
            }
            if (Application.isPlaying)
            {
                Destroy(target);
            }
            else
            {
                DestroyImmediate(target);
            }
        }
    }
}
