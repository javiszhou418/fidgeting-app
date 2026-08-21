using System;
using System.Globalization;
using FidgetingApp.DisplayCase;
using UnityEngine;

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Three visible shipping phases plus an idle setup state and terminal
    /// complete state. Native code consumes the lower-camel tokens published
    /// by GachaPresentationNativeBridge; it never owns this clock.
    /// </summary>
    public enum GachaRevealPhase
    {
        Idle = 0,
        Back = 1,
        Front = 2,
        Readable = 3,
        Complete = 4
    }

    public static class GachaRevealTimeline
    {
        public const float BackSeconds = 0.50f;
        public const float FrontSeconds = 0.70f;
        public const float ReadableSeconds =
            PremiumDisplayCaseRevealMotion.DurationSeconds
            - BackSeconds
            - FrontSeconds;

        public const float BackEnd = BackSeconds;
        public const float FrontEnd = BackEnd + FrontSeconds;
        public const float ReadableEnd = FrontEnd + ReadableSeconds;
        public const float TotalSeconds = ReadableEnd;

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
    /// One shared, prize-independent finishing treatment. The case, its
    /// shell and the fitted content never leave 1x scale/full opacity --
    /// the reveal ends with the case itself settled and fully visible, not
    /// a bare zoomed prize.
    /// </summary>
    public static class GachaRevealPrizePresentation
    {
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
        private readonly bool ownsPrize;
        private readonly Renderer[] caseRenderers;
        private readonly Renderer[] identificationRenderers;
        private readonly Renderer[] lidRenderers;
        private readonly Quaternion caseBaseRotation;
        private readonly Vector3 caseBasePosition;
        private readonly Transform prizeFitRoot;
        private readonly Vector3 prizeFitBasePosition;
        private readonly Vector3 prizeFitBaseScale;
        private GachaResolvedPrizePresentation resolvedPrize;
        private bool disposed;
        private bool started;
        private bool completionForwarded;
        private float elapsed;

        private GachaRevealSession(
            Transform host,
            PremiumDisplayCaseCollectorLabel collectorLabel,
            Transform prize,
            bool ownsPrize,
            GachaResolvedPrizePresentation resolvedPrize)
        {
            this.host = host;
            this.ownsPrize = ownsPrize;
            this.resolvedPrize = resolvedPrize;

            DisplayCase = PremiumDisplayCaseFactory.Instantiate(host);
            DisplayCase.name = "GachaPremiumDisplayCase";
            DisplayCase.transform.localScale =
                Vector3.one * GachaRevealRules.CaseViewportScale;
            caseBasePosition = DisplayCase.transform.localPosition;
            caseBaseRotation = DisplayCase.transform.localRotation;
            caseRenderers = DisplayCase.GetComponentsInChildren<Renderer>(true);
            identificationRenderers = Array.FindAll(
                caseRenderers,
                IsFrontIdentificationRenderer);
            lidRenderers = Array.FindAll(caseRenderers, IsLidRenderer);
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

            Prize = prize;
            SetCaseRenderersVisible(true);
        }

        public event Action<GachaRevealPhase> phaseChanged;
        public event Action revealCompleted;

        public PremiumDisplayCase DisplayCase { get; private set; }
        public PremiumDisplayCaseInteractionController Interaction { get; private set; }
        public Transform Prize { get; private set; }
        public GachaRevealPhase Phase { get; private set; } = GachaRevealPhase.Idle;
        public float PhaseProgress => GachaRevealTimeline.PhaseProgress(Phase, elapsed);
        public float ElapsedSeconds => elapsed;
        public bool IsStarted => started;
        public bool IsComplete => Phase == GachaRevealPhase.Complete;
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

            switch (visualPhase)
            {
                case GachaRevealPhase.Back:
                    caseRevealProgress = Mathf.Lerp(0.04f, 0.18f, Smooth(progress));
                    yaw = 180f;
                    entryOffset = Mathf.Lerp(0.030f, 0.012f, Smooth(progress));
                    break;
                case GachaRevealPhase.Front:
                    caseRevealProgress = Mathf.Lerp(0.18f, 0.46f, Smooth(progress));
                    yaw = Mathf.Lerp(180f, 0f, EaseOutCubic(progress));
                    entryOffset = Mathf.Lerp(0.012f, 0f, Smooth(progress));
                    break;
                case GachaRevealPhase.Readable:
                default:
                    caseRevealProgress = Mathf.Lerp(0.46f, 1f, Smooth(progress));
                    yaw = 0f;
                    entryOffset = 0f;
                    break;
            }

            DisplayCase.transform.localPosition = caseBasePosition
                + Vector3.forward * entryOffset;
            DisplayCase.transform.localRotation = caseBaseRotation
                * Quaternion.Euler(0f, yaw, 0f);
            DisplayCase.SetRevealProgressForPreview(caseRevealProgress);
            SetFrontIdentificationVisible(
                GachaRevealPrizePresentation.ShowsFrontIdentification(
                    visualPhase));
            // The shared reveal envelope slides the lid fully open by this
            // fraction of caseRevealProgress (PremiumDisplayCaseRevealMotion's
            // lidOpen curve). Gacha's compact viewport scale shortens the
            // lid's resting slide-away distance enough that it can graze back
            // into frame, so it is disabled once retracted instead of relying
            // on distance alone to hide it.
            const float lidFullyOpenProgress = 0.38f;
            SetLidRenderersVisible(caseRevealProgress < lidFullyOpenProgress);
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

        private void SetFrontIdentificationVisible(bool visible)
        {
            FrontIdentificationVisible = visible;
            for (int index = 0; index < identificationRenderers.Length; index++)
            {
                if (identificationRenderers[index] != null)
                {
                    identificationRenderers[index].enabled =
                        FrontIdentificationVisible;
                }
            }
        }

        private void SetLidRenderersVisible(bool visible)
        {
            for (int index = 0; index < lidRenderers.Length; index++)
            {
                if (lidRenderers[index] != null)
                {
                    lidRenderers[index].enabled = visible;
                }
            }
        }

        /// <summary>
        /// The shared case hides its lid by sliding Layer_08_BoxLid outside
        /// the shot once opened (see GachaBuild42ShippingCapture's
        /// IsTransientBoxLid) rather than disabling it. That escape distance
        /// is expressed in the case's own local space, so gacha's compact
        /// viewport scale shrinks it along with everything else and the lid
        /// can graze back into frame. Disabling it explicitly here is scoped
        /// to gacha only; the shared component's default behavior is
        /// unchanged for the Library case.
        /// </summary>
        private static bool IsLidRenderer(Renderer renderer)
        {
            if (renderer == null)
            {
                return false;
            }
            for (Transform cursor = renderer.transform;
                 cursor != null;
                 cursor = cursor.parent)
            {
                if (cursor.name == "BoxLidRoot")
                {
                    return true;
                }
            }
            return false;
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

        private void SetPhase(GachaRevealPhase value)
        {
            if (Phase == value)
            {
                return;
            }
            Phase = value;
            phaseChanged?.Invoke(value);
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
