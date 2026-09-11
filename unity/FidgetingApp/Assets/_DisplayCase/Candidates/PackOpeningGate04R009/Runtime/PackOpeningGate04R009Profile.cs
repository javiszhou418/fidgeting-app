using System;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    public enum PackOpeningGate04R009Phase
    {
        Handoff,
        Anticipation,
        Resistance,
        Snap,
        Tear,
        Impact,
        Reveal,
        Settled
    }

    public enum PackOpeningGate04R009SemanticEvent
    {
        TearResistance,
        TearSnap,
        Impact,
        CaseSettled
    }

    public readonly struct PackOpeningGate04R009Sample
    {
        public PackOpeningGate04R009Sample(
            PackOpeningGate04R009Phase phase,
            float tearProgress,
            float openingProgress,
            float packRetreat,
            float caseEntry,
            float caseRotationDegrees,
            float localizedFlash,
            float shockwaveProgress,
            float impactParticleAge,
            float caseSweep,
            float cameraPush,
            Vector2 cameraKick,
            bool impactParticlesEnabled,
            bool directionalStreaksEnabled,
            bool heroSilhouetteRequired)
        {
            Phase = phase;
            TearProgress = tearProgress;
            OpeningProgress = openingProgress;
            PackRetreat = packRetreat;
            CaseEntry = caseEntry;
            CaseRotationDegrees = caseRotationDegrees;
            LocalizedFlash = localizedFlash;
            ShockwaveProgress = shockwaveProgress;
            ImpactParticleAge = impactParticleAge;
            CaseSweep = caseSweep;
            CameraPush = cameraPush;
            CameraKick = cameraKick;
            ImpactParticlesEnabled = impactParticlesEnabled;
            DirectionalStreaksEnabled = directionalStreaksEnabled;
            HeroSilhouetteRequired = heroSilhouetteRequired;
        }

        public PackOpeningGate04R009Phase Phase { get; }
        public float TearProgress { get; }
        public float OpeningProgress { get; }
        public float PackRetreat { get; }
        public float CaseEntry { get; }
        public float CaseRotationDegrees { get; }
        public float LocalizedFlash { get; }
        public float ShockwaveProgress { get; }
        public float ImpactParticleAge { get; }
        public float CaseSweep { get; }
        public float CameraPush { get; }
        public Vector2 CameraKick { get; }
        public bool ImpactParticlesEnabled { get; }
        public bool DirectionalStreaksEnabled { get; }
        public bool HeroSilhouetteRequired { get; }
    }

    [CreateAssetMenu(
        fileName = "PackOpeningGate04R009Profile",
        menuName = "Fidgeting/Display Case/Candidates/Pack Opening Gate 04 R009")]
    public sealed class PackOpeningGate04R009Profile : ScriptableObject
    {
        public const float TotalSeconds = 3.10f;
        public const float HandoffEnd = 0.35f;
        public const float AnticipationEnd = 0.65f;
        public const float ResistanceEnd = 0.95f;
        public const float SnapEnd = 1.00f;
        public const float TearEnd = 1.75f;
        public const float ImpactEnd = 1.93f;
        public const float RevealEnd = 2.53f;
        public const float CaseEntryStart = 1.48f;
        public const float PackRetreatStart = 1.60f;
        public const float PackRetreatEnd = 2.18f;
        public const float CaseEntryEnd = 2.36f;
        public const float CaseSettleStart = 1.78f;
        public const float CaseSettleEnd = 2.42f;
        public const float CaseSweepStart = 1.93f;
        public const float CaseSweepEnd = 2.14f;
        public const float ImpactStart = TearEnd;
        public const float ImpactDuration = ImpactEnd - ImpactStart;
        public const float SnapDuration = SnapEnd - ResistanceEnd;
        public const float FlashFrameDuration = 1f / 60f;
        public const float StartCaseRotationDegrees = -25f;

        [SerializeField] private AnimationCurve anticipationCurve =
            new AnimationCurve(
                new Keyframe(0f, 0f, 0f, 0f),
                new Keyframe(1f, 1f, 0f, 0f));
        [SerializeField] private AnimationCurve tearCurve =
            new AnimationCurve(
                new Keyframe(0f, 0f, 0f, 2.4f),
                new Keyframe(0.62f, 0.83f, 0.75f, 0.75f),
                new Keyframe(1f, 1f, 0f, 0f));
        [SerializeField] private AnimationCurve revealCurve =
            new AnimationCurve(
                new Keyframe(0f, 0f, 0f, 4.2f),
                new Keyframe(0.58f, 0.88f, 0.55f, 0.55f),
                new Keyframe(1f, 1f, 0f, 0f));
        [SerializeField] private AnimationCurve settleCurve =
            new AnimationCurve(
                new Keyframe(0f, 0f, 0f, 4.6f),
                new Keyframe(0.64f, 0.93f, 0.45f, 0.45f),
                new Keyframe(1f, 1f, 0f, 0f));

        public PackOpeningGate04R009Sample Evaluate(
            float elapsedSeconds,
            bool reduceMotion = false)
        {
            float elapsed = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            float resistance = Evaluate01(
                anticipationCurve,
                Mathf.InverseLerp(AnticipationEnd, ResistanceEnd, elapsed));
            float snap = Mathf.InverseLerp(ResistanceEnd, SnapEnd, elapsed);
            float postSnapTear = Evaluate01(
                tearCurve,
                Mathf.InverseLerp(SnapEnd, TearEnd, elapsed));
            float tear = elapsed < ResistanceEnd
                ? 0.055f * resistance
                : elapsed < SnapEnd
                    ? Mathf.Lerp(0.055f, 0.24f, EaseOutQuart(snap))
                    : Mathf.Lerp(0.24f, 1f, postSnapTear);
            if (elapsed < AnticipationEnd)
            {
                tear = 0f;
            }

            float opening = Mathf.SmoothStep(
                0f,
                1f,
                Mathf.InverseLerp(ResistanceEnd, TearEnd, elapsed));
            float retreat = EaseInOutCubic(
                Mathf.InverseLerp(PackRetreatStart, PackRetreatEnd, elapsed));
            float caseEntry = Evaluate01(
                revealCurve,
                Mathf.InverseLerp(CaseEntryStart, CaseEntryEnd, elapsed));
            float settle = Evaluate01(
                settleCurve,
                Mathf.InverseLerp(CaseSettleStart, CaseSettleEnd, elapsed));
            float caseRotation = Mathf.Lerp(
                StartCaseRotationDegrees,
                0f,
                reduceMotion ? Mathf.Clamp01(settle * 1.45f) : settle);

            bool flashFrame =
                elapsed >= ImpactStart
                && elapsed < ImpactStart + FlashFrameDuration;
            float localizedFlash = flashFrame ? (reduceMotion ? 0.28f : 1f) : 0f;
            float shockwave = reduceMotion
                ? 0f
                : Mathf.InverseLerp(
                    ImpactStart + FlashFrameDuration,
                    ImpactEnd,
                    elapsed);
            if (
                elapsed < ImpactStart + FlashFrameDuration
                || elapsed > ImpactEnd
            )
            {
                shockwave = 0f;
            }

            float impactAge = Mathf.Max(0f, elapsed - ImpactStart);
            if (elapsed < ImpactStart || elapsed > ImpactEnd + 0.28f)
            {
                impactAge = -1f;
            }
            float sweep = Mathf.InverseLerp(
                CaseSweepStart,
                CaseSweepEnd,
                elapsed);
            if (elapsed < CaseSweepStart || elapsed > CaseSweepEnd)
            {
                sweep = 0f;
            }

            float pushIn = Evaluate01(
                anticipationCurve,
                Mathf.InverseLerp(HandoffEnd, ResistanceEnd, elapsed));
            float pushOut = EaseOutQuart(
                Mathf.InverseLerp(ImpactStart, ImpactStart + 0.16f, elapsed));
            float cameraPush = reduceMotion ? 0f : 0.052f * pushIn * (1f - pushOut);
            Vector2 cameraKick = Vector2.zero;
            if (!reduceMotion && elapsed >= ImpactStart && elapsed < ImpactStart + 0.12f)
            {
                float kickTime = (elapsed - ImpactStart) / 0.12f;
                float envelope = 1f - EaseOutQuart(kickTime);
                cameraKick = new Vector2(
                    Mathf.Sin(kickTime * Mathf.PI * 2f) * 0.010f,
                    Mathf.Sin(kickTime * Mathf.PI) * 0.006f) * envelope;
            }

            return new PackOpeningGate04R009Sample(
                ResolvePhase(elapsed),
                Mathf.Clamp01(tear),
                opening,
                retreat,
                caseEntry,
                caseRotation,
                localizedFlash,
                shockwave,
                impactAge,
                sweep,
                cameraPush,
                cameraKick,
                !reduceMotion && impactAge >= 0f,
                !reduceMotion && impactAge >= 0f,
                elapsed >= ImpactStart + FlashFrameDuration);
        }

        public PackOpeningGate04R009SemanticEvent[] ResolveSemanticEvents(
            float previousSeconds,
            float elapsedSeconds)
        {
            float previous = Mathf.Clamp(previousSeconds, 0f, TotalSeconds);
            float current = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            if (current <= previous)
            {
                return Array.Empty<PackOpeningGate04R009SemanticEvent>();
            }

            var events = new System.Collections.Generic.List<
                PackOpeningGate04R009SemanticEvent>(4);
            AddCrossing(
                events,
                previous,
                current,
                AnticipationEnd,
                PackOpeningGate04R009SemanticEvent.TearResistance);
            AddCrossing(
                events,
                previous,
                current,
                ResistanceEnd,
                PackOpeningGate04R009SemanticEvent.TearSnap);
            AddCrossing(
                events,
                previous,
                current,
                ImpactStart,
                PackOpeningGate04R009SemanticEvent.Impact);
            AddCrossing(
                events,
                previous,
                current,
                RevealEnd,
                PackOpeningGate04R009SemanticEvent.CaseSettled);
            return events.ToArray();
        }

        private static PackOpeningGate04R009Phase ResolvePhase(float elapsed)
        {
            if (elapsed < HandoffEnd) return PackOpeningGate04R009Phase.Handoff;
            if (elapsed < AnticipationEnd) return PackOpeningGate04R009Phase.Anticipation;
            if (elapsed < ResistanceEnd) return PackOpeningGate04R009Phase.Resistance;
            if (elapsed < SnapEnd) return PackOpeningGate04R009Phase.Snap;
            if (elapsed < TearEnd) return PackOpeningGate04R009Phase.Tear;
            if (elapsed < ImpactEnd) return PackOpeningGate04R009Phase.Impact;
            if (elapsed < RevealEnd) return PackOpeningGate04R009Phase.Reveal;
            return PackOpeningGate04R009Phase.Settled;
        }

        private static void AddCrossing(
            System.Collections.Generic.ICollection<
                PackOpeningGate04R009SemanticEvent> events,
            float previous,
            float current,
            float threshold,
            PackOpeningGate04R009SemanticEvent semanticEvent)
        {
            if (previous < threshold && current >= threshold)
            {
                events.Add(semanticEvent);
            }
        }

        private static float Evaluate01(AnimationCurve curve, float progress)
        {
            float clamped = Mathf.Clamp01(progress);
            return Mathf.Clamp01(curve != null ? curve.Evaluate(clamped) : clamped);
        }

        private static float EaseOutQuart(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return 1f - Mathf.Pow(1f - clamped, 4f);
        }

        private static float EaseInOutCubic(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return clamped < 0.5f
                ? 4f * clamped * clamped * clamped
                : 1f - Mathf.Pow(-2f * clamped + 2f, 3f) * 0.5f;
        }
    }
}
