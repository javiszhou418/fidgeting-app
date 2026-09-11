using System;
using System.Collections.Generic;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    public enum PackOpeningGate04R011Phase
    {
        Handoff,
        Anticipation,
        Resistance,
        Snap,
        Tear,
        SourceImpact,
        SourceReveal,
        Settled
    }

    public enum PackOpeningGate04R011Occlusion
    {
        Sealed,
        AperturePartial,
        CrossingOccluder,
        PackGone
    }

    public enum PackOpeningGate04R011SemanticEvent
    {
        TearResistance,
        TearSnap,
        Impact,
        CaseSettled
    }

    public readonly struct PackOpeningGate04R011Sample
    {
        public PackOpeningGate04R011Sample(
            PackOpeningGate04R011Phase phase,
            PackOpeningGate04R011Occlusion occlusion,
            float sourceTimeSeconds,
            float tearProgress,
            float apertureProgress,
            float packRetreat,
            float packDissolve,
            float caseTravel,
            float caseRotationDegrees,
            float caseSettleOffset,
            float activationAge,
            float lightningAge,
            float explosionAge,
            float caseSheen,
            float rarityReveal,
            float cameraPush,
            Vector2 cameraKick,
            float packCompression,
            bool activationEnabled,
            bool lightningEnabled,
            bool explosionEnabled,
            bool heroSilhouetteRequired)
        {
            Phase = phase;
            Occlusion = occlusion;
            SourceTimeSeconds = sourceTimeSeconds;
            TearProgress = tearProgress;
            ApertureProgress = apertureProgress;
            PackRetreat = packRetreat;
            PackDissolve = packDissolve;
            CaseTravel = caseTravel;
            CaseRotationDegrees = caseRotationDegrees;
            CaseSettleOffset = caseSettleOffset;
            ActivationAge = activationAge;
            LightningAge = lightningAge;
            ExplosionAge = explosionAge;
            CaseSheen = caseSheen;
            RarityReveal = rarityReveal;
            CameraPush = cameraPush;
            CameraKick = cameraKick;
            PackCompression = packCompression;
            ActivationEnabled = activationEnabled;
            LightningEnabled = lightningEnabled;
            ExplosionEnabled = explosionEnabled;
            HeroSilhouetteRequired = heroSilhouetteRequired;
        }

        public PackOpeningGate04R011Phase Phase { get; }
        public PackOpeningGate04R011Occlusion Occlusion { get; }
        public float SourceTimeSeconds { get; }
        public float TearProgress { get; }
        public float ApertureProgress { get; }
        public float PackRetreat { get; }
        public float PackDissolve { get; }
        public float CaseTravel { get; }
        public float CaseRotationDegrees { get; }
        public float CaseSettleOffset { get; }
        public float ActivationAge { get; }
        public float LightningAge { get; }
        public float ExplosionAge { get; }
        public float CaseSheen { get; }
        public float RarityReveal { get; }
        public float CameraPush { get; }
        public Vector2 CameraKick { get; }
        public float PackCompression { get; }
        public bool ActivationEnabled { get; }
        public bool LightningEnabled { get; }
        public bool ExplosionEnabled { get; }
        public bool HeroSilhouetteRequired { get; }
    }

    [CreateAssetMenu(
        fileName = "PackOpeningGate04R011Profile",
        menuName = "Fidgeting/Display Case/Candidates/Pack Opening Gate 04 R011")]
    public sealed class PackOpeningGate04R011Profile : ScriptableObject
    {
        public const float TotalSeconds = 3.45f;
        public const float HandoffEnd = 0.28f;
        public const float AnticipationEnd = 0.55f;
        public const float ResistanceEnd = 0.85f;
        public const float SnapEnd = 0.90f;
        public const float TearEnd = 1.60f;
        public const float ImpactStart = TearEnd;
        public const float ImpactEnd = 1.78f;
        public const float ActivationStart = AnticipationEnd;
        public const float LightningStart = 1.48f;
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
        public const float CaseSettleEnd = 2.82f;
        public const float SheenStart = 2.72f;
        public const float SheenEnd = 3.08f;
        public const float SettledStart = 3.10f;
        public const float ImpactDuration = ImpactEnd - ImpactStart;
        public const float SnapDuration = SnapEnd - ResistanceEnd;
        public const float StandardStartRotationDegrees = -25f;
        public const float ReducedStartRotationDegrees = -10f;

        public PackOpeningGate04R011Sample Evaluate(
            float elapsedSeconds,
            bool reduceMotion = false)
        {
            float elapsed = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            float resistance = Smooth01(
                Mathf.InverseLerp(AnticipationEnd, ResistanceEnd, elapsed));
            float snap = EaseOutQuart(
                Mathf.InverseLerp(ResistanceEnd, SnapEnd, elapsed));
            float progressive = EaseOutCubic(
                Mathf.InverseLerp(SnapEnd, TearEnd, elapsed));

            float tear;
            if (elapsed < AnticipationEnd)
            {
                tear = 0f;
            }
            else if (elapsed < ResistanceEnd)
            {
                tear = Mathf.Lerp(0f, 0.06f, resistance);
            }
            else if (elapsed < SnapEnd)
            {
                tear = Mathf.Lerp(0.06f, 0.20f, snap);
            }
            else
            {
                tear = Mathf.Lerp(0.20f, 1f, progressive);
            }
            tear = Mathf.Clamp01(tear);

            float sourceTime = elapsed + SourceTimeOffset;
            float discardTime = Mathf.InverseLerp(
                TargetSolidPackOff,
                TargetProxyResultOff,
                elapsed);
            float packDissolve = elapsed < TargetSolidPackOff
                ? 0f
                : MakeItShineCc0EffectCurves
                    .CreateDiscardDissolveCurve()
                    .Evaluate(discardTime);
            float packRetreat = Smooth01(discardTime);
            float aperture = Smooth01(Mathf.InverseLerp(0.025f, 0.92f, tear));
            float caseTravel = Smooth01(Mathf.InverseLerp(
                TargetProxyResultStart,
                TargetRealResultStart,
                elapsed));
            float settle = Smooth01(Mathf.InverseLerp(
                TargetProxyResultStart,
                CaseSettleEnd,
                elapsed));
            float startRotation = reduceMotion
                ? ReducedStartRotationDegrees
                : StandardStartRotationDegrees;
            float caseRotation = Mathf.Lerp(startRotation, 0f, settle);
            float settleOffset = elapsed >= TargetRealResultStart
                && elapsed <= CaseSettleEnd
                ? Mathf.Sin(
                    Mathf.InverseLerp(
                        TargetRealResultStart,
                        CaseSettleEnd,
                        elapsed) * Mathf.PI)
                    * (1f - Mathf.InverseLerp(
                        TargetRealResultStart,
                        CaseSettleEnd,
                        elapsed))
                    * (reduceMotion ? 0.0015f : 0.006f)
                : 0f;

            float activationAge = elapsed - ActivationStart;
            float lightningAge = elapsed - LightningStart;
            float explosionAge = elapsed - ImpactStart;
            float sheen = Mathf.InverseLerp(SheenStart, SheenEnd, elapsed);
            if (elapsed < SheenStart || elapsed > SheenEnd)
            {
                sheen = 0f;
            }
            float rarityReveal = Smooth01(Mathf.InverseLerp(
                TargetRealResultStart,
                CaseSettleEnd,
                elapsed));

            float pushIn = Smooth01(
                Mathf.InverseLerp(HandoffEnd, ResistanceEnd, elapsed));
            float pushRecovery = EaseOutCubic(
                Mathf.InverseLerp(ImpactStart, ImpactEnd, elapsed));
            float cameraPush = reduceMotion
                ? 0f
                : 0.022f * pushIn * (1f - pushRecovery);
            Vector2 cameraKick = Vector2.zero;
            if (
                !reduceMotion
                && elapsed >= ImpactStart
                && elapsed < ImpactStart + 0.08f
            )
            {
                float kickTime = (elapsed - ImpactStart) / 0.08f;
                float envelope = 1f - EaseOutCubic(kickTime);
                cameraKick = new Vector2(
                    Mathf.Sin(kickTime * Mathf.PI) * 0.0024f,
                    Mathf.Sin(kickTime * Mathf.PI * 2f) * 0.0012f)
                    * envelope;
            }

            float compression = elapsed >= HandoffEnd
                && elapsed <= SnapEnd
                ? Mathf.Sin(
                    Mathf.InverseLerp(
                        HandoffEnd,
                        SnapEnd,
                        elapsed) * Mathf.PI)
                    * (reduceMotion ? 0.004f : 0.018f)
                : 0f;

            return new PackOpeningGate04R011Sample(
                ResolvePhase(elapsed),
                ResolveOcclusion(tear, packRetreat),
                sourceTime,
                tear,
                aperture,
                packRetreat,
                packDissolve,
                caseTravel,
                caseRotation,
                settleOffset,
                activationAge,
                lightningAge,
                explosionAge,
                sheen,
                rarityReveal,
                cameraPush,
                cameraKick,
                compression,
                !reduceMotion && activationAge >= 0f && elapsed <= 2.48f,
                !reduceMotion && lightningAge >= 0f && elapsed <= 2.08f,
                !reduceMotion && explosionAge >= 0f && elapsed <= 2.72f,
                elapsed >= ImpactStart);
        }

        public PackOpeningGate04R011SemanticEvent[] ResolveSemanticEvents(
            float previousSeconds,
            float elapsedSeconds)
        {
            float previous = Mathf.Clamp(previousSeconds, 0f, TotalSeconds);
            float current = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            if (current <= previous)
            {
                return Array.Empty<PackOpeningGate04R011SemanticEvent>();
            }

            var events = new List<PackOpeningGate04R011SemanticEvent>(4);
            AddCrossing(
                events,
                previous,
                current,
                AnticipationEnd,
                PackOpeningGate04R011SemanticEvent.TearResistance);
            AddCrossing(
                events,
                previous,
                current,
                ResistanceEnd,
                PackOpeningGate04R011SemanticEvent.TearSnap);
            AddCrossing(
                events,
                previous,
                current,
                ImpactStart,
                PackOpeningGate04R011SemanticEvent.Impact);
            AddCrossing(
                events,
                previous,
                current,
                CaseSettleEnd,
                PackOpeningGate04R011SemanticEvent.CaseSettled);
            return events.ToArray();
        }

        private static PackOpeningGate04R011Phase ResolvePhase(float elapsed)
        {
            if (elapsed < HandoffEnd) return PackOpeningGate04R011Phase.Handoff;
            if (elapsed < AnticipationEnd) return PackOpeningGate04R011Phase.Anticipation;
            if (elapsed < ResistanceEnd) return PackOpeningGate04R011Phase.Resistance;
            if (elapsed < SnapEnd) return PackOpeningGate04R011Phase.Snap;
            if (elapsed < TearEnd) return PackOpeningGate04R011Phase.Tear;
            if (elapsed < ImpactEnd) return PackOpeningGate04R011Phase.SourceImpact;
            if (elapsed < SettledStart) return PackOpeningGate04R011Phase.SourceReveal;
            return PackOpeningGate04R011Phase.Settled;
        }

        private static PackOpeningGate04R011Occlusion ResolveOcclusion(
            float tear,
            float packRetreat)
        {
            if (tear <= 0.001f)
            {
                return PackOpeningGate04R011Occlusion.Sealed;
            }
            if (packRetreat <= 0.001f)
            {
                return PackOpeningGate04R011Occlusion.AperturePartial;
            }
            return packRetreat < 0.999f
                ? PackOpeningGate04R011Occlusion.CrossingOccluder
                : PackOpeningGate04R011Occlusion.PackGone;
        }

        private static void AddCrossing(
            ICollection<PackOpeningGate04R011SemanticEvent> events,
            float previous,
            float current,
            float threshold,
            PackOpeningGate04R011SemanticEvent semanticEvent)
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
