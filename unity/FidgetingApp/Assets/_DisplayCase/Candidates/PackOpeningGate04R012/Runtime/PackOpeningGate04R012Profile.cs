using System;
using System.Collections.Generic;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    public enum PackOpeningGate04R012Phase
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

    public enum PackOpeningGate04R012Occlusion
    {
        Sealed,
        MouthOpening,
        CaseCrossingMouth,
        PackDiscarded
    }

    public enum PackOpeningGate04R012SemanticEvent
    {
        TearResistance,
        TearSnap,
        Impact,
        CaseSettled
    }

    public readonly struct PackOpeningGate04R012Sample
    {
        public PackOpeningGate04R012Sample(
            PackOpeningGate04R012Phase phase,
            PackOpeningGate04R012Occlusion occlusion,
            float sourceTimeSeconds,
            float tearProgress,
            float apertureProgress,
            float tabLift,
            float packDissolve,
            float packRetreat,
            float caseTravel,
            float caseLift,
            float caseRotationDegrees,
            float sourceSweep,
            float sourceImpact,
            float caseSheen,
            float cameraPush,
            Vector2 cameraKick,
            bool sourceEffectsEnabled)
        {
            Phase = phase;
            Occlusion = occlusion;
            SourceTimeSeconds = sourceTimeSeconds;
            TearProgress = tearProgress;
            ApertureProgress = apertureProgress;
            TabLift = tabLift;
            PackDissolve = packDissolve;
            PackRetreat = packRetreat;
            CaseTravel = caseTravel;
            CaseLift = caseLift;
            CaseRotationDegrees = caseRotationDegrees;
            SourceSweep = sourceSweep;
            SourceImpact = sourceImpact;
            CaseSheen = caseSheen;
            CameraPush = cameraPush;
            CameraKick = cameraKick;
            SourceEffectsEnabled = sourceEffectsEnabled;
        }

        public PackOpeningGate04R012Phase Phase { get; }
        public PackOpeningGate04R012Occlusion Occlusion { get; }
        public float SourceTimeSeconds { get; }
        public float TearProgress { get; }
        public float ApertureProgress { get; }
        public float TabLift { get; }
        public float PackDissolve { get; }
        public float PackRetreat { get; }
        public float CaseTravel { get; }
        public float CaseLift { get; }
        public float CaseRotationDegrees { get; }
        public float SourceSweep { get; }
        public float SourceImpact { get; }
        public float CaseSheen { get; }
        public float CameraPush { get; }
        public Vector2 CameraKick { get; }
        public bool SourceEffectsEnabled { get; }
    }

    [CreateAssetMenu(
        fileName = "PackOpeningGate04R012Profile",
        menuName = "Fidgeting/Display Case/Candidates/Pack Opening Gate 04 R012")]
    public sealed class PackOpeningGate04R012Profile : ScriptableObject
    {
        public const float TotalSeconds = 3.60f;
        public const float HandoffEnd = 0.28f;
        public const float PullTabStart = 0.36f;
        public const float ResistanceEnd = 0.70f;
        public const float SnapEnd = 0.75f;
        public const float TearEnd = 1.62f;
        public const float ImpactStart = TearEnd;
        public const float ImpactEnd = 1.82f;
        public const float CaseTravelStart = 1.22f;
        public const float CaseTravelEnd = 2.512371f;
        public const float CaseSettleEnd = 2.90f;
        public const float SheenStart = 2.74f;
        public const float SheenEnd = 3.08f;
        public const float SettledStart = 3.14f;

        public const float SourceExplosionStart = 5.8194770813f;
        public const float SourceProxyResultStart = 5.9179303646f;
        public const float SourceSolidPackOff = 5.9333767891f;
        public const float SourceRealResultStart = 6.711848f;
        public const float SourceProxyResultOff = 6.742770f;
        public const float SourceTimeOffset = SourceExplosionStart - ImpactStart;
        public const float TargetProxyResultStart =
            SourceProxyResultStart - SourceTimeOffset;
        public const float TargetSolidPackOff =
            SourceSolidPackOff - SourceTimeOffset;
        public const float TargetRealResultStart =
            SourceRealResultStart - SourceTimeOffset;
        public const float TargetProxyResultOff =
            SourceProxyResultOff - SourceTimeOffset;

        public const float StandardStartRotationDegrees = -22f;
        public const float ReducedStartRotationDegrees = -8f;

        public PackOpeningGate04R012Sample Evaluate(
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

            float tear;
            if (elapsed < PullTabStart)
            {
                tear = 0f;
            }
            else if (elapsed < ResistanceEnd)
            {
                tear = Mathf.Lerp(0f, 0.055f, resistance);
            }
            else if (elapsed < SnapEnd)
            {
                tear = Mathf.Lerp(0.055f, 0.17f, snap);
            }
            else
            {
                tear = Mathf.Lerp(0.17f, 1f, progressive);
            }

            float aperture = Smooth01(Mathf.InverseLerp(0.025f, 0.90f, tear));
            float tabLift = Smooth01(
                Mathf.InverseLerp(PullTabStart, ResistanceEnd, elapsed));
            float discardTime = Mathf.InverseLerp(
                TargetSolidPackOff,
                TargetProxyResultOff,
                elapsed);
            float packDissolve = elapsed < TargetSolidPackOff
                ? 0f
                : MakeItShineCc0EffectCurves
                    .CreateDiscardDissolveCurve()
                    .Evaluate(discardTime);
            float packRetreat = Smooth01(
                Mathf.InverseLerp(2.04f, TargetProxyResultOff, elapsed));
            float caseTravel = Smooth01(
                Mathf.InverseLerp(CaseTravelStart, CaseTravelEnd, elapsed));
            float caseLift = Smooth01(
                Mathf.InverseLerp(1.36f, CaseSettleEnd, elapsed));
            float startRotation = reduceMotion
                ? ReducedStartRotationDegrees
                : StandardStartRotationDegrees;
            float caseRotation = Mathf.Lerp(
                startRotation,
                0f,
                Smooth01(Mathf.InverseLerp(1.55f, CaseSettleEnd, elapsed)));

            float sourceSweep = Mathf.Sin(
                Mathf.Clamp01(Mathf.InverseLerp(0.94f, 1.98f, elapsed))
                * Mathf.PI);
            float sourceImpact = Mathf.Sin(
                Mathf.Clamp01(Mathf.InverseLerp(ImpactStart, ImpactEnd, elapsed))
                * Mathf.PI);
            float sheen = Mathf.InverseLerp(SheenStart, SheenEnd, elapsed);
            if (elapsed < SheenStart || elapsed > SheenEnd)
            {
                sheen = 0f;
            }

            float pushIn = Smooth01(
                Mathf.InverseLerp(HandoffEnd, ResistanceEnd, elapsed));
            float pushOut = EaseOutCubic(
                Mathf.InverseLerp(ImpactStart, ImpactEnd, elapsed));
            float cameraPush = reduceMotion
                ? 0f
                : 0.016f * pushIn * (1f - pushOut);
            Vector2 cameraKick = Vector2.zero;
            if (!reduceMotion && elapsed >= ImpactStart && elapsed < 1.69f)
            {
                float kick = Mathf.InverseLerp(ImpactStart, 1.69f, elapsed);
                float envelope = 1f - EaseOutCubic(kick);
                cameraKick = new Vector2(
                    Mathf.Sin(kick * Mathf.PI) * 0.0015f,
                    Mathf.Sin(kick * Mathf.PI * 2f) * 0.00065f) * envelope;
            }

            PackOpeningGate04R012Occlusion occlusion;
            if (tear <= 0.001f)
            {
                occlusion = PackOpeningGate04R012Occlusion.Sealed;
            }
            else if (caseTravel <= 0.02f)
            {
                occlusion = PackOpeningGate04R012Occlusion.MouthOpening;
            }
            else if (packDissolve < 0.999f)
            {
                occlusion = PackOpeningGate04R012Occlusion.CaseCrossingMouth;
            }
            else
            {
                occlusion = PackOpeningGate04R012Occlusion.PackDiscarded;
            }

            return new PackOpeningGate04R012Sample(
                ResolvePhase(elapsed),
                occlusion,
                elapsed + SourceTimeOffset,
                Mathf.Clamp01(tear),
                aperture,
                tabLift,
                Mathf.Clamp01(packDissolve),
                packRetreat,
                caseTravel,
                caseLift,
                caseRotation,
                reduceMotion ? 0f : sourceSweep,
                reduceMotion ? 0f : sourceImpact,
                sheen,
                cameraPush,
                cameraKick,
                !reduceMotion && elapsed >= 0.94f && elapsed <= 2.16f);
        }

        public PackOpeningGate04R012SemanticEvent[] ResolveSemanticEvents(
            float previousSeconds,
            float elapsedSeconds)
        {
            float previous = Mathf.Clamp(previousSeconds, 0f, TotalSeconds);
            float current = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            if (current <= previous)
            {
                return Array.Empty<PackOpeningGate04R012SemanticEvent>();
            }

            var events = new List<PackOpeningGate04R012SemanticEvent>(4);
            AddCrossing(
                events,
                previous,
                current,
                PullTabStart,
                PackOpeningGate04R012SemanticEvent.TearResistance);
            AddCrossing(
                events,
                previous,
                current,
                ResistanceEnd,
                PackOpeningGate04R012SemanticEvent.TearSnap);
            AddCrossing(
                events,
                previous,
                current,
                ImpactStart,
                PackOpeningGate04R012SemanticEvent.Impact);
            AddCrossing(
                events,
                previous,
                current,
                CaseSettleEnd,
                PackOpeningGate04R012SemanticEvent.CaseSettled);
            return events.ToArray();
        }

        private static PackOpeningGate04R012Phase ResolvePhase(float elapsed)
        {
            if (elapsed < HandoffEnd) return PackOpeningGate04R012Phase.Handoff;
            if (elapsed < PullTabStart) return PackOpeningGate04R012Phase.PullTab;
            if (elapsed < ResistanceEnd) return PackOpeningGate04R012Phase.Resistance;
            if (elapsed < SnapEnd) return PackOpeningGate04R012Phase.Snap;
            if (elapsed < TearEnd) return PackOpeningGate04R012Phase.ProgressiveTear;
            if (elapsed < ImpactEnd) return PackOpeningGate04R012Phase.SourceImpact;
            if (elapsed < SettledStart) return PackOpeningGate04R012Phase.ContinuousReveal;
            return PackOpeningGate04R012Phase.Settled;
        }

        private static void AddCrossing(
            ICollection<PackOpeningGate04R012SemanticEvent> events,
            float previous,
            float current,
            float threshold,
            PackOpeningGate04R012SemanticEvent semanticEvent)
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
