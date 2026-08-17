using System;
using FidgetingApp.DisplayCase;
using UnityEngine;

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Scene-facing wrapper around GachaRevealSession. Setup and Start are
    /// deliberately separate so native can make its transparent presentation
    /// visible before Unity advances the authoritative six-phase clock.
    /// </summary>
    public sealed class GachaRevealDirector : MonoBehaviour
    {
        public event Action<GachaRevealPhase> phaseChanged;
        public event Action revealCompleted;

        private GachaRevealSession session;

        public GachaRevealPhase Phase => session?.Phase ?? GachaRevealPhase.Idle;
        public string PhaseToken => GachaPresentationNativeBridge.PhaseToken(Phase);
        public float PhaseProgress => session?.PhaseProgress ?? 0f;
        public PremiumDisplayCase ActiveCase => session?.DisplayCase;
        public Transform ActivePrize => session?.Prize;
        public Light AccentLight => session?.SheenLight;
        public string FailureReason { get; private set; } = string.Empty;
        public bool IsPrepared => session != null;

        public bool Prepare(GachaDrawOutcome outcome)
        {
            Dismiss();
            if (!GachaRevealSession.TryCreate(
                    transform,
                    outcome,
                    out session,
                    out string failureReason))
            {
                FailureReason = failureReason;
                session = null;
                return false;
            }

            FailureReason = string.Empty;
            Subscribe();
            return true;
        }

        public bool Prepare(GachaPrizeDefinition prize)
        {
            Dismiss();
            if (!GachaRevealSession.TryCreate(
                    transform,
                    prize,
                    out session,
                    out string failureReason))
            {
                FailureReason = failureReason;
                session = null;
                return false;
            }

            FailureReason = string.Empty;
            Subscribe();
            return true;
        }

        public bool StartReveal()
        {
            if (session == null)
            {
                FailureReason = "reveal-not-prepared";
                return false;
            }

            session.Start();
            return true;
        }

        public void Begin(GachaDrawOutcome outcome)
        {
            if (!Prepare(outcome))
            {
                throw new InvalidOperationException(FailureReason);
            }
            StartReveal();
        }

        /// <summary>
        /// Compatibility overload for callers that already own an imported
        /// renderer-only prize. New gacha code should use Prepare(outcome),
        /// which resolves the stable ContentReference itself.
        /// </summary>
        public void Begin(GachaDrawOutcome outcome, Transform prizeNode)
        {
            GachaPrizeDefinition? prize = GachaCatalog.ResolvePrize(outcome.PrizeId);
            GachaPrizeKind kind = prize.HasValue
                ? prize.Value.Kind
                : GachaPrizeKind.ToySkin;
            Begin(
                outcome.Rarity,
                kind,
                prize.HasValue ? prize.Value.DisplayName : "COLLECTOR EDITION",
                prizeNode);
        }

        public void Begin(
            GachaRarity rarity,
            GachaPrizeKind kind,
            Transform prizeNode)
        {
            Begin(rarity, kind, kind.ToString(), prizeNode);
        }

        public void Begin(
            GachaRarity rarity,
            GachaPrizeKind kind,
            string displayName,
            Transform prizeNode)
        {
            _ = kind;
            Dismiss();
            session = GachaRevealSession.CreateExternal(
                transform,
                rarity,
                displayName,
                prizeNode);
            FailureReason = string.Empty;
            Subscribe();
            session.Start();
        }

        /// <summary>Deterministic step, called from Update and tests.</summary>
        public void Tick(float unscaledDeltaTime)
        {
            session?.Advance(unscaledDeltaTime);
        }

        public void Dismiss()
        {
            if (session != null)
            {
                Unsubscribe();
                session.Dispose();
                session = null;
            }
            FailureReason = string.Empty;
        }

        private void Update()
        {
            Tick(Time.unscaledDeltaTime);
        }

        private void OnDisable()
        {
            Dismiss();
        }

        private void Subscribe()
        {
            session.phaseChanged += HandlePhaseChanged;
            session.revealCompleted += HandleRevealComplete;
        }

        private void Unsubscribe()
        {
            session.phaseChanged -= HandlePhaseChanged;
            session.revealCompleted -= HandleRevealComplete;
        }

        private void HandlePhaseChanged(GachaRevealPhase phase)
        {
            phaseChanged?.Invoke(phase);
        }

        private void HandleRevealComplete()
        {
            revealCompleted?.Invoke();
        }
    }
}
