using System;
using System.Collections.Generic;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    public enum PackOpeningGate04R013Phase
    {
        Handoff,
        PullTab,
        Resistance,
        Snap,
        ProgressiveTear,
        SourceImpact,
        ContinuousReveal,
        Settled
    }

    public enum PackOpeningGate04R013Occlusion
    {
        Sealed,
        MouthOpening,
        CaseContained,
        CaseCrossingMouth,
        PackDiscarded
    }

    public enum PackOpeningGate04R013SemanticEvent
    {
        TearResistance,
        TearSnap,
        Impact,
        CaseSettled
    }

    public readonly struct PackOpeningGate04R013Sample
    {
        public PackOpeningGate04R013Sample(
            PackOpeningGate04R013Phase phase,
            PackOpeningGate04R013Occlusion occlusion,
            float tearProgress,
            float packDissolve,
            float caseTravel,
            float caseLift,
            float caseRotationDegrees,
            float rimSweep,
            float sourceImpact,
            float cameraPush,
            Vector2 cameraKick,
            bool sourceEffectsEnabled)
        {
            Phase = phase;
            Occlusion = occlusion;
            TearProgress = tearProgress;
            PackDissolve = packDissolve;
            CaseTravel = caseTravel;
            CaseLift = caseLift;
            CaseRotationDegrees = caseRotationDegrees;
            RimSweep = rimSweep;
            SourceImpact = sourceImpact;
            CameraPush = cameraPush;
            CameraKick = cameraKick;
            SourceEffectsEnabled = sourceEffectsEnabled;
        }

        public PackOpeningGate04R013Phase Phase { get; }
        public PackOpeningGate04R013Occlusion Occlusion { get; }
        public float TearProgress { get; }
        public float PackDissolve { get; }
        public float CaseTravel { get; }
        public float CaseLift { get; }
        public float CaseRotationDegrees { get; }
        public float RimSweep { get; }
        public float SourceImpact { get; }
        public float CameraPush { get; }
        public Vector2 CameraKick { get; }
        public bool SourceEffectsEnabled { get; }
    }

    [CreateAssetMenu(
        fileName = "PackOpeningGate04R013Profile",
        menuName = "Fidgeting/Display Case/Candidates/Pack Opening Gate 04 R013")]
    public sealed class PackOpeningGate04R013Profile : ScriptableObject
    {
        public const float TotalSeconds = 3.50f;
        public const float PullTabStart = 0.32f;
        public const float ResistanceEnd = 0.60f;
        public const float SnapEnd = 0.65f;
        public const float TearEnd = 1.62f;
        public const float ImpactStart = 1.62f;
        public const float ImpactEnd = 1.80f;
        public const float CaseTravelStart = 0.80f;
        public const float CaseTravelEnd = 2.30f;
        public const float PackDiscardStart = 1.84f;
        public const float PackDiscardEnd = 2.48f;
        public const float CaseSettleEnd = 2.92f;
        public const float SettledStart = 3.08f;

        public PackOpeningGate04R013Sample Evaluate(
            float elapsedSeconds,
            bool reduceMotion = false)
        {
            float elapsed = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            float resistance = Smooth01(
                Mathf.InverseLerp(PullTabStart, ResistanceEnd, elapsed));
            float snap = EaseOutQuart(
                Mathf.InverseLerp(ResistanceEnd, SnapEnd, elapsed));
            float progressive = EaseOutCubic(
                Mathf.InverseLerp(SnapEnd, TearEnd, elapsed));
            float tear = elapsed < PullTabStart
                ? 0f
                : elapsed < ResistanceEnd
                    ? Mathf.Lerp(0f, 0.045f, resistance)
                    : elapsed < SnapEnd
                        ? Mathf.Lerp(0.045f, 0.15f, snap)
                        : Mathf.Lerp(0.15f, 1f, progressive);

            float discardTime = Mathf.InverseLerp(
                PackDiscardStart,
                PackDiscardEnd,
                elapsed);
            float packDissolve = elapsed < PackDiscardStart
                ? 0f
                : MakeItShineCc0EffectCurves
                    .CreateDiscardDissolveCurve()
                    .Evaluate(discardTime);
            float caseTravel = Smooth01(
                Mathf.InverseLerp(CaseTravelStart, CaseTravelEnd, elapsed));
            float caseLift = Smooth01(
                Mathf.InverseLerp(1.04f, CaseSettleEnd, elapsed));
            float caseRotation = Mathf.Lerp(
                reduceMotion ? -7f : -19f,
                0f,
                Smooth01(Mathf.InverseLerp(1.50f, CaseSettleEnd, elapsed)));
            float rimSweep = reduceMotion
                ? 0f
                : Mathf.Sin(
                    Mathf.Clamp01(Mathf.InverseLerp(0.70f, 1.72f, elapsed))
                    * Mathf.PI);
            float impact = reduceMotion
                ? 0f
                : Mathf.Sin(
                    Mathf.Clamp01(Mathf.InverseLerp(ImpactStart, ImpactEnd, elapsed))
                    * Mathf.PI);
            float pushIn = Smooth01(Mathf.InverseLerp(0.22f, 0.60f, elapsed));
            float pushOut = EaseOutCubic(
                Mathf.InverseLerp(ImpactStart, ImpactEnd, elapsed));
            float cameraPush = reduceMotion ? 0f : 0.011f * pushIn * (1f - pushOut);
            Vector2 cameraKick = Vector2.zero;
            if (!reduceMotion && elapsed >= ImpactStart && elapsed < 1.70f)
            {
                float phase = Mathf.InverseLerp(ImpactStart, 1.70f, elapsed);
                float decay = 1f - EaseOutCubic(phase);
                cameraKick = new Vector2(
                    Mathf.Sin(phase * Mathf.PI) * 0.0010f,
                    Mathf.Sin(phase * Mathf.PI * 2f) * 0.00045f) * decay;
            }

            PackOpeningGate04R013Occlusion occlusion;
            if (tear <= 0.001f)
            {
                occlusion = PackOpeningGate04R013Occlusion.Sealed;
            }
            else if (caseTravel <= 0.02f)
            {
                occlusion = PackOpeningGate04R013Occlusion.MouthOpening;
            }
            else if (tear < 0.97f)
            {
                occlusion = PackOpeningGate04R013Occlusion.CaseContained;
            }
            else if (packDissolve < 0.999f)
            {
                occlusion = PackOpeningGate04R013Occlusion.CaseCrossingMouth;
            }
            else
            {
                occlusion = PackOpeningGate04R013Occlusion.PackDiscarded;
            }

            return new PackOpeningGate04R013Sample(
                ResolvePhase(elapsed),
                occlusion,
                Mathf.Clamp01(tear),
                Mathf.Clamp01(packDissolve),
                caseTravel,
                caseLift,
                caseRotation,
                rimSweep,
                impact,
                cameraPush,
                cameraKick,
                !reduceMotion && elapsed >= 0.70f && elapsed <= 2.08f);
        }

        public PackOpeningGate04R013SemanticEvent[] ResolveSemanticEvents(
            float previousSeconds,
            float elapsedSeconds)
        {
            float previous = Mathf.Clamp(previousSeconds, 0f, TotalSeconds);
            float current = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            if (current <= previous)
            {
                return Array.Empty<PackOpeningGate04R013SemanticEvent>();
            }

            var events = new List<PackOpeningGate04R013SemanticEvent>(4);
            AddCrossing(events, previous, current, PullTabStart,
                PackOpeningGate04R013SemanticEvent.TearResistance);
            AddCrossing(events, previous, current, ResistanceEnd,
                PackOpeningGate04R013SemanticEvent.TearSnap);
            AddCrossing(events, previous, current, ImpactStart,
                PackOpeningGate04R013SemanticEvent.Impact);
            AddCrossing(events, previous, current, CaseSettleEnd,
                PackOpeningGate04R013SemanticEvent.CaseSettled);
            return events.ToArray();
        }

        private static PackOpeningGate04R013Phase ResolvePhase(float elapsed)
        {
            if (elapsed < 0.22f) return PackOpeningGate04R013Phase.Handoff;
            if (elapsed < PullTabStart) return PackOpeningGate04R013Phase.PullTab;
            if (elapsed < ResistanceEnd) return PackOpeningGate04R013Phase.Resistance;
            if (elapsed < SnapEnd) return PackOpeningGate04R013Phase.Snap;
            if (elapsed < TearEnd) return PackOpeningGate04R013Phase.ProgressiveTear;
            if (elapsed < ImpactEnd) return PackOpeningGate04R013Phase.SourceImpact;
            if (elapsed < SettledStart) return PackOpeningGate04R013Phase.ContinuousReveal;
            return PackOpeningGate04R013Phase.Settled;
        }

        private static void AddCrossing(
            ICollection<PackOpeningGate04R013SemanticEvent> events,
            float previous,
            float current,
            float threshold,
            PackOpeningGate04R013SemanticEvent semanticEvent)
        {
            if (previous < threshold && current >= threshold)
            {
                events.Add(semanticEvent);
            }
        }

        private static float Smooth01(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return clamped * clamped * (3f - 2f * clamped);
        }

        private static float EaseOutCubic(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return 1f - Mathf.Pow(1f - clamped, 3f);
        }

        private static float EaseOutQuart(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return 1f - Mathf.Pow(1f - clamped, 4f);
        }
    }
}
