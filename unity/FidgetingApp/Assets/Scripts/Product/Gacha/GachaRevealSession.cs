using System;
using System.Collections.Generic;
using System.Globalization;
using FidgetingApp.DisplayCase;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Six visible shipping phases plus an idle setup state and terminal
    /// complete state. Native code consumes the lower-camel tokens published
    /// by GachaPresentationNativeBridge; it never owns this clock.
    /// </summary>
    public enum GachaRevealPhase
    {
        Idle = 0,
        Back = 1,
        Front = 2,
        Readable = 3,
        Exploded = 4,
        PrizeOnly = 5,
        Sheen = 6,
        Complete = 7
    }

    public static class GachaRevealTimeline
    {
        public const float BackSeconds = 0.50f;
        public const float FrontSeconds = 0.70f;
        public const float ReadableSeconds =
            PremiumDisplayCaseRevealMotion.DurationSeconds
            - BackSeconds
            - FrontSeconds;
        public const float ExplodedSeconds =
            PremiumDisplayCaseExplodedLayout.AssemblyDurationSeconds;
        public const float PrizeOnlySeconds = 0.55f;
        public const float SheenSeconds = 0.45f;

        public const float BackEnd = BackSeconds;
        public const float FrontEnd = BackEnd + FrontSeconds;
        public const float ReadableEnd = FrontEnd + ReadableSeconds;
        public const float ExplodedEnd = ReadableEnd + ExplodedSeconds;
        public const float PrizeOnlyEnd = ExplodedEnd + PrizeOnlySeconds;
        public const float TotalSeconds = PrizeOnlyEnd + SheenSeconds;

        public static GachaRevealPhase PhaseAt(float elapsedSeconds)
        {
            float elapsed = Mathf.Max(0f, elapsedSeconds);
            if (elapsed < BackEnd)
            {
                return GachaRevealPhase.Back;
            }
            if (elapsed < FrontEnd)
            {
                return GachaRevealPhase.Front;
            }
            if (elapsed < ReadableEnd)
            {
                return GachaRevealPhase.Readable;
            }
            if (elapsed < ExplodedEnd)
            {
                return GachaRevealPhase.Exploded;
            }
            if (elapsed < PrizeOnlyEnd)
            {
                return GachaRevealPhase.PrizeOnly;
            }
            if (elapsed < TotalSeconds)
            {
                return GachaRevealPhase.Sheen;
            }
            return GachaRevealPhase.Complete;
        }

        public static float PhaseProgress(
            GachaRevealPhase phase,
            float elapsedSeconds)
        {
            return phase switch
            {
                GachaRevealPhase.Back => Range(elapsedSeconds, 0f, BackEnd),
                GachaRevealPhase.Front => Range(
                    elapsedSeconds,
                    BackEnd,
                    FrontEnd),
                GachaRevealPhase.Readable => Range(
                    elapsedSeconds,
                    FrontEnd,
                    ReadableEnd),
                GachaRevealPhase.Exploded => Range(
                    elapsedSeconds,
                    ReadableEnd,
                    ExplodedEnd),
                GachaRevealPhase.PrizeOnly => Range(
                    elapsedSeconds,
                    ExplodedEnd,
                    PrizeOnlyEnd),
                GachaRevealPhase.Sheen => Range(
                    elapsedSeconds,
                    PrizeOnlyEnd,
                    TotalSeconds),
                GachaRevealPhase.Complete => 1f,
                _ => 0f
            };
        }

        private static float Range(float value, float start, float end)
        {
            return Mathf.Clamp01(Mathf.InverseLerp(start, end, value));
        }
    }

    /// <summary>
    /// Gacha-only exploded-motion envelope for the shared magnetic-slide case.
    /// The approved reveal, box, content pose and camera remain untouched;
    /// only the interactive viewer's broad authored layer offsets are reduced
    /// to a compact, readable fan for the locked portrait viewport. No prize
    /// is allowed to select a different profile.
    /// </summary>
    public static class GachaRevealPresentationMotion
    {
        public const float ExplodedOffsetScale = 0.10f;

        public static float OffsetScale(
            GachaRevealPhase phase,
            float phaseProgress)
        {
            return phase switch
            {
                GachaRevealPhase.Exploded => ExplodedOffsetScale,
                GachaRevealPhase.PrizeOnly => Mathf.Lerp(
                    ExplodedOffsetScale,
                    0f,
                    Smooth(phaseProgress)),
                _ => 0f
            };
        }

        private static float Smooth(float value)
        {
            float t = Mathf.Clamp01(value);
            return t * t * (3f - 2f * t);
        }
    }

    /// <summary>
    /// One shared, prize-independent finishing treatment. The case profile,
    /// capsule and camera never vary; only the already fitted content grows
    /// into a readable centered hero while the shell dissolves away.
    /// </summary>
    public static class GachaRevealPrizePresentation
    {
        public const float FinalPrizeScale = 1.45f;

        public static float PrizeScale(
            GachaRevealPhase phase,
            float phaseProgress)
        {
            return phase switch
            {
                GachaRevealPhase.PrizeOnly => Mathf.Lerp(
                    1f,
                    FinalPrizeScale,
                    Smooth(phaseProgress)),
                GachaRevealPhase.Sheen => FinalPrizeScale,
                GachaRevealPhase.Complete => FinalPrizeScale,
                _ => 1f
            };
        }

        public static float ShellOpacity(
            GachaRevealPhase phase,
            float phaseProgress)
        {
            return phase switch
            {
                // The shell finishes dissolving during the tail of the
                // exploded phase. PrizeOnly therefore means exactly what its
                // native phase token says: only the prize remains. Starting
                // after the midpoint preserves a clearly readable exploded
                // keyframe while avoiding a hard cut at the phase boundary.
                GachaRevealPhase.Exploded => 1f - Smooth(
                    Mathf.InverseLerp(0.55f, 1f, phaseProgress)),
                GachaRevealPhase.PrizeOnly => 0f,
                GachaRevealPhase.Sheen => 0f,
                GachaRevealPhase.Complete => 0f,
                _ => 1f
            };
        }

        public static bool ShowsFrontIdentification(GachaRevealPhase phase)
        {
            return phase != GachaRevealPhase.Back;
        }

        private static float Smooth(float value)
        {
            float t = Mathf.Clamp01(value);
            return t * t * (3f - 2f * t);
        }
    }

    /// <summary>
    /// Converts authoritative gacha metadata into the physical Collector Slab
    /// label. The pending receipt supplies acquisition time; no collectible id
    /// is invented when the product has no durable numbering source.
    /// </summary>
    public static class GachaCollectorLabelRules
    {
        public static PremiumDisplayCaseCollectorLabel Create(
            GachaPrizeDefinition prize,
            string firstObtainedAtUtc)
        {
            return new PremiumDisplayCaseCollectorLabel(
                ProductName(prize),
                EditionName(prize.SeriesId),
                1,
                AcquiredDate(firstObtainedAtUtc),
                string.Empty,
                CollectorTier(prize.Rarity));
        }

        public static PremiumDisplayCaseCollectorTier CollectorTier(
            GachaRarity rarity)
        {
            return rarity switch
            {
                GachaRarity.Refined => PremiumDisplayCaseCollectorTier.Refined,
                GachaRarity.Signature => PremiumDisplayCaseCollectorTier.Signature,
                GachaRarity.Heirloom => PremiumDisplayCaseCollectorTier.Heirloom,
                _ => PremiumDisplayCaseCollectorTier.Standard
            };
        }

        private static string ProductName(GachaPrizeDefinition prize)
        {
            if (string.Equals(
                    prize.Id,
                    "canyon-std-slate-lining",
                    StringComparison.Ordinal))
            {
                return "SLATE LINING";
            }

            return string.IsNullOrWhiteSpace(prize.DisplayName)
                ? "COLLECTOR EDITION"
                : prize.DisplayName;
        }

        private static string EditionName(string seriesId)
        {
            return string.IsNullOrWhiteSpace(seriesId)
                ? "GACHA EDITION"
                : seriesId.Replace('-', ' ').ToUpperInvariant();
        }

        private static string AcquiredDate(string firstObtainedAtUtc)
        {
            if (!DateTime.TryParse(
                    firstObtainedAtUtc,
                    CultureInfo.InvariantCulture,
                    DateTimeStyles.RoundtripKind,
                    out DateTime parsed))
            {
                return string.Empty;
            }

            return parsed.ToUniversalTime().ToString(
                "yyyy-MM-dd",
                CultureInfo.InvariantCulture);
        }
    }

    /// <summary>
    /// Owns one neutral case, one prize presentation and the deterministic
    /// reveal timeline. Camera ownership, live-product hiding, transaction
    /// persistence and native callbacks remain coordinator responsibilities.
    /// </summary>
    public sealed class GachaRevealSession : IDisposable
    {
        private readonly Transform host;
        private readonly GachaRevealSignature signature;
        private readonly bool ownsPrize;
        private readonly Renderer[] caseRenderers;
        private readonly Renderer[] identificationRenderers;
        private readonly Quaternion caseBaseRotation;
        private readonly Vector3 caseBasePosition;
        private readonly Transform prizeFitRoot;
        private readonly Vector3 prizeFitBasePosition;
        private readonly Vector3 prizeFitBaseScale;
        private readonly List<ShellFadeMaterial> shellFadeMaterials =
            new List<ShellFadeMaterial>();
        private GachaResolvedPrizePresentation resolvedPrize;
        private bool shellFadePrepared;
        private bool disposed;
        private bool started;
        private bool completionForwarded;
        private float elapsed;

        private GachaRevealSession(
            Transform host,
            GachaRarity rarity,
            PremiumDisplayCaseCollectorLabel collectorLabel,
            Transform prize,
            bool ownsPrize,
            GachaResolvedPrizePresentation resolvedPrize)
        {
            this.host = host;
            this.ownsPrize = ownsPrize;
            this.resolvedPrize = resolvedPrize;
            signature = GachaRevealRules.Signature(rarity);

            DisplayCase = PremiumDisplayCaseFactory.Instantiate(host);
            DisplayCase.name = "GachaPremiumDisplayCase";
            caseBasePosition = DisplayCase.transform.localPosition;
            caseBaseRotation = DisplayCase.transform.localRotation;
            caseRenderers = DisplayCase.GetComponentsInChildren<Renderer>(true);
            identificationRenderers = Array.FindAll(
                caseRenderers,
                IsFrontIdentificationRenderer);
            Interaction = DisplayCase.GetComponent<
                PremiumDisplayCaseInteractionController>();
            if (Interaction == null)
            {
                throw new MissingReferenceException(
                    "PremiumDisplayCase requires its interaction controller.");
            }

            // Deactivate before attachment. PremiumDisplayCase intentionally
            // restores external content from OnDisable, so deactivating after
            // setContent would silently pull the prize back out of contentSlot.
            DisplayCase.gameObject.SetActive(false);

            DisplayCase.setCapsulePreset(
                GachaRevealRules.SharedCapsulePreset);
            DisplayCase.SetProductPresentationOffset(Vector3.zero);
            DisplayCase.SetCollectorLabel(collectorLabel);
            DisplayCase.setContent(
                prize,
                GachaPrizePresentationResolver.SharedContentOptions);
            prizeFitRoot = prize.parent;
            if (prizeFitRoot == null
                || !prizeFitRoot.IsChildOf(DisplayCase.transform))
            {
                throw new MissingReferenceException(
                    "PremiumDisplayCase did not attach the prize to contentFitRoot.");
            }
            prizeFitBasePosition = prizeFitRoot.localPosition;
            prizeFitBaseScale = prizeFitRoot.localScale;
            DisplayCase.SetRevealProgressForPreview(0f);
            Interaction.SetExplodedProgress(0f);

            Prize = prize;
            SheenLight = CreateSheenLight(host, signature.LiningColor);
            SetCaseRenderersVisible(true);
            SheenLight.gameObject.SetActive(false);
        }

        public event Action<GachaRevealPhase> phaseChanged;
        public event Action revealCompleted;

        public PremiumDisplayCase DisplayCase { get; private set; }
        public PremiumDisplayCaseInteractionController Interaction { get; private set; }
        public Transform Prize { get; private set; }
        public Light SheenLight { get; private set; }
        public GachaRevealPhase Phase { get; private set; } = GachaRevealPhase.Idle;
        public float PhaseProgress => GachaRevealTimeline.PhaseProgress(Phase, elapsed);
        public float ElapsedSeconds => elapsed;
        public bool IsStarted => started;
        public bool IsComplete => Phase == GachaRevealPhase.Complete;
        public float ShellOpacity { get; private set; } = 1f;
        public float PrizePresentationScale { get; private set; } = 1f;
        public bool FrontIdentificationVisible { get; private set; } = true;

        public static bool TryCreate(
            Transform host,
            GachaDrawOutcome outcome,
            out GachaRevealSession session,
            out string failureReason)
        {
            return TryCreate(
                host,
                outcome,
                string.Empty,
                out session,
                out failureReason);
        }

        /// <summary>
        /// firstObtainedAtUtc is the authoritative receipt row's acquisition
        /// timestamp; pass string.Empty only when no durable receipt exists.
        /// </summary>
        public static bool TryCreate(
            Transform host,
            GachaDrawOutcome outcome,
            string firstObtainedAtUtc,
            out GachaRevealSession session,
            out string failureReason)
        {
            GachaPrizeDefinition? prize = GachaCatalog.ResolvePrize(outcome.PrizeId);
            if (!prize.HasValue)
            {
                session = null;
                failureReason = "unknown-prize:" + (outcome.PrizeId ?? string.Empty);
                return false;
            }

            return TryCreate(
                host,
                prize.Value,
                firstObtainedAtUtc,
                out session,
                out failureReason);
        }

        public static bool TryCreate(
            Transform host,
            GachaPrizeDefinition prize,
            out GachaRevealSession session,
            out string failureReason)
        {
            return TryCreate(
                host,
                prize,
                string.Empty,
                out session,
                out failureReason);
        }

        public static bool TryCreate(
            Transform host,
            GachaPrizeDefinition prize,
            string firstObtainedAtUtc,
            out GachaRevealSession session,
            out string failureReason)
        {
            if (!GachaPrizePresentationResolver.TryResolve(
                    prize,
                    host,
                    out GachaResolvedPrizePresentation presentation,
                    out failureReason))
            {
                session = null;
                return false;
            }

            try
            {
                session = new GachaRevealSession(
                    host,
                    prize.Rarity,
                    GachaCollectorLabelRules.Create(prize, firstObtainedAtUtc),
                    presentation.Transform,
                    true,
                    presentation);
                failureReason = string.Empty;
                return true;
            }
            catch (Exception exception)
            {
                presentation.Dispose();
                session = null;
                failureReason = "reveal-session-setup-failed:" + exception.Message;
                return false;
            }
        }

        public static GachaRevealSession Create(
            Transform host,
            GachaDrawOutcome outcome)
        {
            if (!TryCreate(host, outcome, out var session, out string reason))
            {
                throw new InvalidOperationException(reason);
            }
            return session;
        }

        public static GachaRevealSession Create(
            Transform host,
            GachaPrizeDefinition prize)
        {
            if (!TryCreate(host, prize, out var session, out string reason))
            {
                throw new InvalidOperationException(reason);
            }
            return session;
        }

        public static GachaRevealSession CreateExternal(
            Transform host,
            GachaRarity rarity,
            string displayName,
            Transform prize)
        {
            if (prize == null)
            {
                throw new ArgumentNullException(nameof(prize));
            }

            return new GachaRevealSession(
                host,
                rarity,
                new PremiumDisplayCaseCollectorLabel(
                    displayName,
                    "GACHA EDITION",
                    1,
                    string.Empty,
                    string.Empty,
                    GachaCollectorLabelRules.CollectorTier(rarity)),
                prize,
                false,
                null);
        }

        public void Start()
        {
            ThrowIfDisposed();
            if (started)
            {
                return;
            }

            started = true;
            completionForwarded = false;
            elapsed = 0f;
            DisplayCase.gameObject.SetActive(true);
            SheenLight.gameObject.SetActive(true);
            SetCaseRenderersVisible(true);
            ApplyVisualState();
            SetPhase(GachaRevealPhase.Back);
        }

        /// <summary>
        /// Deterministic clock. A large step still publishes every crossed
        /// phase in order so native state cannot silently skip a contract
        /// boundary after a frame hitch or resume.
        /// </summary>
        public void Advance(float unscaledDeltaTime)
        {
            ThrowIfDisposed();
            if (!started || IsComplete)
            {
                return;
            }

            elapsed = Mathf.Min(
                GachaRevealTimeline.TotalSeconds,
                elapsed + Mathf.Max(0f, unscaledDeltaTime));
            GachaRevealPhase target = GachaRevealTimeline.PhaseAt(elapsed);
            while (Phase < target)
            {
                SetPhase((GachaRevealPhase)((int)Phase + 1));
            }
            ApplyVisualState();

            if (target == GachaRevealPhase.Complete && !completionForwarded)
            {
                completionForwarded = true;
                revealCompleted?.Invoke();
            }
        }

        public void Dismiss()
        {
            if (disposed)
            {
                return;
            }

            if (DisplayCase != null)
            {
                SetCaseRenderersVisible(false);
                DisplayCase.setContent((Transform)null);
                // Destroy is intentionally deferred in a player. Deactivate
                // synchronously so a dismissed presentation cannot render or
                // run another component update while Unity reclaims it.
                DisplayCase.gameObject.SetActive(false);
                GachaPrizePresentationResolver.DestroyOwned(
                    DisplayCase.gameObject);
                DisplayCase = null;
                Interaction = null;
            }
            DisposeShellFadeMaterials();

            if (SheenLight != null)
            {
                SheenLight.gameObject.SetActive(false);
                GachaPrizePresentationResolver.DestroyOwned(
                    SheenLight.gameObject);
                SheenLight = null;
            }

            if (ownsPrize && resolvedPrize != null)
            {
                if (resolvedPrize.Root != null)
                {
                    resolvedPrize.Root.SetActive(false);
                }
                resolvedPrize.Dispose();
                resolvedPrize = null;
            }

            Prize = null;
            Phase = GachaRevealPhase.Idle;
            started = false;
            disposed = true;
        }

        public void Dispose()
        {
            Dismiss();
        }

        private void ApplyVisualState()
        {
            if (DisplayCase == null)
            {
                return;
            }

            float progress = GachaRevealTimeline.PhaseProgress(
                GachaRevealTimeline.PhaseAt(elapsed),
                elapsed);
            GachaRevealPhase visualPhase = GachaRevealTimeline.PhaseAt(elapsed);
            float caseRevealProgress;
            float yaw;
            float entryOffset;
            float explodedProgress;
            float explodedOffsetScale;
            float shellOpacity;
            float prizeScale;
            float sheen;

            switch (visualPhase)
            {
                case GachaRevealPhase.Back:
                    caseRevealProgress = Mathf.Lerp(0.04f, 0.18f, Smooth(progress));
                    yaw = 180f;
                    entryOffset = Mathf.Lerp(0.030f, 0.012f, Smooth(progress));
                    explodedProgress = 0f;
                    explodedOffsetScale = 0f;
                    shellOpacity = 1f;
                    prizeScale = 1f;
                    sheen = 0f;
                    break;
                case GachaRevealPhase.Front:
                    caseRevealProgress = Mathf.Lerp(0.18f, 0.46f, Smooth(progress));
                    yaw = Mathf.Lerp(180f, 0f, EaseOutCubic(progress));
                    entryOffset = Mathf.Lerp(0.012f, 0f, Smooth(progress));
                    explodedProgress = 0f;
                    explodedOffsetScale = 0f;
                    shellOpacity = 1f;
                    prizeScale = 1f;
                    sheen = 0f;
                    break;
                case GachaRevealPhase.Readable:
                    caseRevealProgress = Mathf.Lerp(0.46f, 1f, Smooth(progress));
                    yaw = 0f;
                    entryOffset = 0f;
                    explodedProgress = 0f;
                    explodedOffsetScale = 0f;
                    shellOpacity = 1f;
                    prizeScale = 1f;
                    sheen = 0f;
                    break;
                case GachaRevealPhase.Exploded:
                    caseRevealProgress = 1f;
                    yaw = 0f;
                    entryOffset = 0f;
                    explodedProgress = PremiumDisplayCaseExplodedLayout
                        .EaseAssembly(progress);
                    explodedOffsetScale = GachaRevealPresentationMotion
                        .OffsetScale(visualPhase, progress);
                    shellOpacity = GachaRevealPrizePresentation.ShellOpacity(
                        visualPhase,
                        progress);
                    prizeScale = 1f;
                    sheen = 0f;
                    break;
                case GachaRevealPhase.PrizeOnly:
                    caseRevealProgress = 1f;
                    yaw = 0f;
                    entryOffset = 0f;
                    explodedProgress = 1f;
                    explodedOffsetScale = GachaRevealPresentationMotion
                        .OffsetScale(visualPhase, progress);
                    shellOpacity = GachaRevealPrizePresentation.ShellOpacity(
                        visualPhase,
                        progress);
                    prizeScale = GachaRevealPrizePresentation.PrizeScale(
                        visualPhase,
                        progress);
                    sheen = 0f;
                    break;
                case GachaRevealPhase.Sheen:
                    caseRevealProgress = 1f;
                    yaw = 0f;
                    entryOffset = 0f;
                    explodedProgress = 1f;
                    explodedOffsetScale = 0f;
                    shellOpacity = 0f;
                    prizeScale = GachaRevealPrizePresentation.FinalPrizeScale;
                    sheen = Mathf.Sin(progress * Mathf.PI);
                    break;
                default:
                    caseRevealProgress = 1f;
                    yaw = 0f;
                    entryOffset = 0f;
                    explodedProgress = 1f;
                    explodedOffsetScale = 0f;
                    shellOpacity = 0f;
                    prizeScale = GachaRevealPrizePresentation.FinalPrizeScale;
                    sheen = 0f;
                    break;
            }

            DisplayCase.transform.localPosition = caseBasePosition
                + Vector3.forward * entryOffset;
            DisplayCase.transform.localRotation = caseBaseRotation
                * Quaternion.Euler(0f, yaw, 0f);
            DisplayCase.SetRevealProgressForPreview(caseRevealProgress);
            Interaction.SetExplodedProgress(
                explodedProgress,
                explodedOffsetScale);
            ApplyPrizeScale(prizeScale);
            SetShellOpacity(shellOpacity);
            SetFrontIdentificationVisible(
                GachaRevealPrizePresentation.ShowsFrontIdentification(
                    visualPhase));
            ApplySheen(progress, sheen);
        }

        private void ApplyPrizeScale(float scale)
        {
            PrizePresentationScale = Mathf.Max(0.01f, scale);
            if (prizeFitRoot == null)
            {
                return;
            }

            // PremiumDisplayCase fit position is -bounds.center * fitScale.
            // Scaling both values by the same factor keeps the fitted bounds
            // at the exact shared capsule/camera center instead of drifting.
            prizeFitRoot.localScale = prizeFitBaseScale
                * PrizePresentationScale;
            prizeFitRoot.localPosition = prizeFitBasePosition
                * PrizePresentationScale;
        }

        private void ApplySheen(float progress, float envelope)
        {
            if (SheenLight == null)
            {
                return;
            }
            SheenLight.transform.localPosition = new Vector3(
                Mathf.Lerp(-0.12f, 0.12f, progress),
                0.08f,
                -0.16f);
            SheenLight.intensity = envelope
                * signature.AccentIntensity
                * GachaRevealRules.AccentLightMaxIntensity;
        }

        private void SetCaseRenderersVisible(bool visible)
        {
            if (caseRenderers == null)
            {
                return;
            }
            for (int index = 0; index < caseRenderers.Length; index++)
            {
                if (caseRenderers[index] != null)
                {
                    caseRenderers[index].enabled = visible;
                }
            }
        }

        private void SetShellOpacity(float opacity)
        {
            ShellOpacity = Mathf.Clamp01(opacity);
            if (ShellOpacity < 0.999f)
            {
                EnsureShellFadeMaterials();
            }

            for (int index = 0; index < shellFadeMaterials.Count; index++)
            {
                shellFadeMaterials[index].SetOpacity(ShellOpacity);
            }
            SetCaseRenderersVisible(ShellOpacity > 0.001f);
        }

        private void SetFrontIdentificationVisible(bool visible)
        {
            FrontIdentificationVisible = visible && ShellOpacity > 0.001f;
            for (int index = 0; index < identificationRenderers.Length; index++)
            {
                if (identificationRenderers[index] != null)
                {
                    identificationRenderers[index].enabled =
                        FrontIdentificationVisible;
                }
            }
        }

        private void EnsureShellFadeMaterials()
        {
            if (shellFadePrepared)
            {
                return;
            }
            shellFadePrepared = true;

            for (int rendererIndex = 0;
                 rendererIndex < caseRenderers.Length;
                 rendererIndex++)
            {
                Renderer renderer = caseRenderers[rendererIndex];
                if (renderer == null)
                {
                    continue;
                }

                Material[] originals = renderer.sharedMaterials;
                var clones = new Material[originals.Length];
                for (int materialIndex = 0;
                     materialIndex < originals.Length;
                     materialIndex++)
                {
                    Material original = originals[materialIndex];
                    if (original == null)
                    {
                        continue;
                    }

                    var clone = new Material(original)
                    {
                        name = original.name + "_GachaShellFade"
                    };
                    clones[materialIndex] = clone;
                    shellFadeMaterials.Add(new ShellFadeMaterial(clone));
                }
                renderer.sharedMaterials = clones;
            }
        }

        private void DisposeShellFadeMaterials()
        {
            for (int index = shellFadeMaterials.Count - 1;
                 index >= 0;
                 index--)
            {
                shellFadeMaterials[index].Dispose();
            }
            shellFadeMaterials.Clear();
        }

        private static bool IsFrontIdentificationRenderer(Renderer renderer)
        {
            if (renderer == null)
            {
                return false;
            }
            string name = renderer.name ?? string.Empty;
            return name == "LaserLevelMark"
                || name == "LaserProductName"
                || name == "FeaturedBadgeArtwork"
                || name == "FeaturedBadgeToken"
                || name == "FeaturedBadgeShortName"
                || name == "CollectorTierAndLevel"
                || name == "CollectorProductName"
                || name == "CollectorEdition"
                || name == "CollectorAcquiredDate"
                || name == "CollectorStableId"
                || name == "Collector_LabelPaper"
                || name == "Collector_RarityFoilBand"
                || name.StartsWith(
                    "Collector_LabelFoil_",
                    StringComparison.Ordinal);
        }

        private sealed class ShellFadeMaterial : IDisposable
        {
            private static readonly int BaseColorId =
                Shader.PropertyToID("_BaseColor");
            private static readonly int ColorId = Shader.PropertyToID("_Color");
            private static readonly int OpacityId =
                Shader.PropertyToID("_Opacity");
            private static readonly int EtchOpacityId =
                Shader.PropertyToID("_EtchOpacity");

            private Material material;
            private readonly bool hasBaseColor;
            private readonly bool hasColor;
            private readonly bool hasOpacity;
            private readonly bool hasEtchOpacity;
            private readonly Color baseColor;
            private readonly Color color;
            private readonly float opacity;
            private readonly float etchOpacity;

            public ShellFadeMaterial(Material material)
            {
                this.material = material;
                hasBaseColor = material.HasProperty(BaseColorId);
                hasColor = material.HasProperty(ColorId);
                hasOpacity = material.HasProperty(OpacityId);
                hasEtchOpacity = material.HasProperty(EtchOpacityId);
                baseColor = hasBaseColor
                    ? material.GetColor(BaseColorId)
                    : Color.white;
                color = hasColor
                    ? material.GetColor(ColorId)
                    : Color.white;
                opacity = hasOpacity ? material.GetFloat(OpacityId) : 1f;
                etchOpacity = hasEtchOpacity
                    ? material.GetFloat(EtchOpacityId)
                    : 1f;
                ConfigureTransparent(material);
            }

            public void SetOpacity(float value)
            {
                if (material == null)
                {
                    return;
                }
                float alpha = Mathf.Clamp01(value);
                if (hasBaseColor)
                {
                    material.SetColor(BaseColorId, WithAlpha(baseColor, alpha));
                }
                if (hasColor)
                {
                    material.SetColor(ColorId, WithAlpha(color, alpha));
                }
                if (hasOpacity)
                {
                    material.SetFloat(OpacityId, opacity * alpha);
                }
                if (hasEtchOpacity)
                {
                    material.SetFloat(EtchOpacityId, etchOpacity * alpha);
                }
            }

            public void Dispose()
            {
                if (material == null)
                {
                    return;
                }
                GachaPrizePresentationResolver.DestroyOwned(material);
                material = null;
            }

            private static void ConfigureTransparent(Material target)
            {
                if (target.HasProperty("_Surface"))
                {
                    target.SetFloat("_Surface", 1f);
                    target.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
                }
                if (target.HasProperty("_Mode"))
                {
                    target.SetFloat("_Mode", 3f);
                    target.EnableKeyword("_ALPHABLEND_ON");
                }
                if (target.HasProperty("_SrcBlend"))
                {
                    target.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
                }
                if (target.HasProperty("_DstBlend"))
                {
                    target.SetFloat(
                        "_DstBlend",
                        (float)BlendMode.OneMinusSrcAlpha);
                }
                if (target.HasProperty("_ZWrite"))
                {
                    target.SetFloat("_ZWrite", 0f);
                }
                target.SetOverrideTag("RenderType", "Transparent");
                target.renderQueue = (int)RenderQueue.Transparent;
            }

            private static Color WithAlpha(Color source, float opacity)
            {
                return new Color(
                    source.r,
                    source.g,
                    source.b,
                    source.a * opacity);
            }
        }

        private void SetPhase(GachaRevealPhase value)
        {
            if (Phase == value)
            {
                return;
            }
            Phase = value;
            phaseChanged?.Invoke(value);
        }

        private static Light CreateSheenLight(Transform parent, Color color)
        {
            var lightObject = new GameObject("GachaPrizeSheenLight");
            lightObject.transform.SetParent(parent, false);
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = color;
            light.range = 0.60f;
            light.intensity = 0f;
            light.shadows = LightShadows.None;
            return light;
        }

        private static float Smooth(float value)
        {
            float t = Mathf.Clamp01(value);
            return t * t * (3f - 2f * t);
        }

        private static float EaseOutCubic(float value)
        {
            float inverse = 1f - Mathf.Clamp01(value);
            return 1f - inverse * inverse * inverse;
        }

        private void ThrowIfDisposed()
        {
            if (disposed)
            {
                throw new ObjectDisposedException(nameof(GachaRevealSession));
            }
        }
    }
}
