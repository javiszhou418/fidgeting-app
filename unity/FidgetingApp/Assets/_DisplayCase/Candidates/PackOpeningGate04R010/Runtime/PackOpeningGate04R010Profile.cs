using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    public enum PackOpeningGate04R010Phase
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

    public enum PackOpeningGate04R010Occlusion
    {
        Sealed,
        AperturePartial,
        CrossingOccluder,
        PackGone
    }

    public enum PackOpeningGate04R010SemanticEvent
    {
        TearResistance,
        TearSnap,
        Impact,
        CaseSettled
    }

    public readonly struct PackOpeningGate04R010Sample
    {
        public PackOpeningGate04R010Sample(
            PackOpeningGate04R010Phase phase,
            PackOpeningGate04R010Occlusion occlusion,
            float tearProgress,
            float apertureProgress,
            float packRetreat,
            float caseTravel,
            float caseRotationDegrees,
            float caseSettleOffset,
            float localizedFlash,
            float energyRingProgress,
            float impactParticleAge,
            float caseSheen,
            float cameraPush,
            Vector2 cameraKick,
            float packCompression,
            bool impactParticlesEnabled,
            bool directionalStreaksEnabled,
            bool heroSilhouetteRequired)
        {
            Phase = phase;
            Occlusion = occlusion;
            TearProgress = tearProgress;
            ApertureProgress = apertureProgress;
            PackRetreat = packRetreat;
            CaseTravel = caseTravel;
            CaseRotationDegrees = caseRotationDegrees;
            CaseSettleOffset = caseSettleOffset;
            LocalizedFlash = localizedFlash;
            EnergyRingProgress = energyRingProgress;
            ImpactParticleAge = impactParticleAge;
            CaseSheen = caseSheen;
            CameraPush = cameraPush;
            CameraKick = cameraKick;
            PackCompression = packCompression;
            ImpactParticlesEnabled = impactParticlesEnabled;
            DirectionalStreaksEnabled = directionalStreaksEnabled;
            HeroSilhouetteRequired = heroSilhouetteRequired;
        }

        public PackOpeningGate04R010Phase Phase { get; }
        public PackOpeningGate04R010Occlusion Occlusion { get; }
        public float TearProgress { get; }
        public float ApertureProgress { get; }
        public float PackRetreat { get; }
        public float CaseTravel { get; }
        public float CaseRotationDegrees { get; }
        public float CaseSettleOffset { get; }
        public float LocalizedFlash { get; }
        public float EnergyRingProgress { get; }
        public float ImpactParticleAge { get; }
        public float CaseSheen { get; }
        public float CameraPush { get; }
        public Vector2 CameraKick { get; }
        public float PackCompression { get; }
        public bool ImpactParticlesEnabled { get; }
        public bool DirectionalStreaksEnabled { get; }
        public bool HeroSilhouetteRequired { get; }
    }

    [CreateAssetMenu(
        fileName = "PackOpeningGate04R010Profile",
        menuName = "Fidgeting/Display Case/Candidates/Pack Opening Gate 04 R010")]
    public sealed class PackOpeningGate04R010Profile : ScriptableObject
    {
        public const float TotalSeconds = 3.10f;
        public const float HandoffEnd = 0.28f;
        public const float AnticipationEnd = 0.55f;
        public const float ResistanceEnd = 0.85f;
        public const float SnapEnd = 0.90f;
        public const float TearEnd = 1.60f;
        public const float ImpactStart = TearEnd;
        public const float ImpactEnd = 1.78f;
        public const float CaseSettleStart = 1.64f;
        public const float CaseSettleEnd = 2.36f;
        public const float SheenStart = ImpactEnd;
        public const float SheenEnd = 2.12f;
        public const float SettledStart = 2.45f;
        public const float ImpactDuration = ImpactEnd - ImpactStart;
        public const float SnapDuration = SnapEnd - ResistanceEnd;
        public const float FlashFrameDuration = 1f / 60f;
        public const float StandardStartRotationDegrees = -25f;
        public const float ReducedStartRotationDegrees = -10f;

        public PackOpeningGate04R010Sample Evaluate(
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

            float aperture = Smooth01(Mathf.InverseLerp(0.025f, 0.92f, tear));
            float impact = Smooth01(
                Mathf.InverseLerp(ImpactStart, ImpactEnd, elapsed));
            float packRetreat = impact;
            float caseTravel = Smooth01(
                Mathf.InverseLerp(ImpactStart, ImpactEnd, elapsed));
            float settle = Smooth01(
                Mathf.InverseLerp(CaseSettleStart, CaseSettleEnd, elapsed));
            float startRotation = reduceMotion
                ? ReducedStartRotationDegrees
                : StandardStartRotationDegrees;
            float caseRotation = Mathf.Lerp(startRotation, 0f, settle);
            float settleOffset = elapsed >= ImpactEnd
                && elapsed <= CaseSettleEnd
                ? Mathf.Sin(
                    Mathf.InverseLerp(
                        ImpactEnd,
                        CaseSettleEnd,
                        elapsed) * Mathf.PI)
                    * (1f - Mathf.InverseLerp(
                        ImpactEnd,
                        CaseSettleEnd,
                        elapsed))
                    * (reduceMotion ? 0.0025f : 0.010f)
                : 0f;

            bool flashFrame =
                elapsed >= ImpactStart
                && elapsed < ImpactStart + FlashFrameDuration;
            float flash = flashFrame ? (reduceMotion ? 0.18f : 1f) : 0f;
            float ring = reduceMotion
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
                ring = 0f;
            }

            float impactAge = elapsed >= ImpactStart
                && elapsed <= ImpactEnd + 0.24f
                ? elapsed - ImpactStart
                : -1f;
            float sheen = Mathf.InverseLerp(SheenStart, SheenEnd, elapsed);
            if (elapsed < SheenStart || elapsed > SheenEnd)
            {
                sheen = 0f;
            }

            float pushIn = Smooth01(
                Mathf.InverseLerp(HandoffEnd, ResistanceEnd, elapsed));
            float pushRecovery = EaseOutCubic(
                Mathf.InverseLerp(ImpactStart, ImpactEnd, elapsed));
            float cameraPush = reduceMotion
                ? 0f
                : 0.032f * pushIn * (1f - pushRecovery);
            Vector2 cameraKick = Vector2.zero;
            if (
                !reduceMotion
                && elapsed >= ImpactStart
                && elapsed < ImpactStart + 0.10f
            )
            {
                float kickTime = (elapsed - ImpactStart) / 0.10f;
                float envelope = 1f - EaseOutCubic(kickTime);
                cameraKick = new Vector2(
                    Mathf.Sin(kickTime * Mathf.PI) * 0.0045f,
                    Mathf.Sin(kickTime * Mathf.PI * 2f) * 0.0022f)
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

            return new PackOpeningGate04R010Sample(
                ResolvePhase(elapsed),
                ResolveOcclusion(elapsed, tear, packRetreat),
                tear,
                aperture,
                packRetreat,
                caseTravel,
                caseRotation,
                settleOffset,
                flash,
                ring,
                impactAge,
                sheen,
                cameraPush,
                cameraKick,
                compression,
                !reduceMotion && impactAge >= 0f,
                !reduceMotion && impactAge >= 0f,
                elapsed >= ImpactStart);
        }

        public PackOpeningGate04R010SemanticEvent[] ResolveSemanticEvents(
            float previousSeconds,
            float elapsedSeconds)
        {
            float previous = Mathf.Clamp(previousSeconds, 0f, TotalSeconds);
            float current = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            if (current <= previous)
            {
                return Array.Empty<PackOpeningGate04R010SemanticEvent>();
            }

            var events = new List<PackOpeningGate04R010SemanticEvent>(4);
            AddCrossing(
                events,
                previous,
                current,
                AnticipationEnd,
                PackOpeningGate04R010SemanticEvent.TearResistance);
            AddCrossing(
                events,
                previous,
                current,
                ResistanceEnd,
                PackOpeningGate04R010SemanticEvent.TearSnap);
            AddCrossing(
                events,
                previous,
                current,
                ImpactStart,
                PackOpeningGate04R010SemanticEvent.Impact);
            AddCrossing(
                events,
                previous,
                current,
                CaseSettleEnd,
                PackOpeningGate04R010SemanticEvent.CaseSettled);
            return events.ToArray();
        }

        private static PackOpeningGate04R010Phase ResolvePhase(float elapsed)
        {
            if (elapsed < HandoffEnd) return PackOpeningGate04R010Phase.Handoff;
            if (elapsed < AnticipationEnd) return PackOpeningGate04R010Phase.Anticipation;
            if (elapsed < ResistanceEnd) return PackOpeningGate04R010Phase.Resistance;
            if (elapsed < SnapEnd) return PackOpeningGate04R010Phase.Snap;
            if (elapsed < TearEnd) return PackOpeningGate04R010Phase.Tear;
            if (elapsed < ImpactEnd) return PackOpeningGate04R010Phase.Impact;
            if (elapsed < SettledStart) return PackOpeningGate04R010Phase.Reveal;
            return PackOpeningGate04R010Phase.Settled;
        }

        private static PackOpeningGate04R010Occlusion ResolveOcclusion(
            float elapsed,
            float tear,
            float packRetreat)
        {
            if (tear <= 0.001f)
            {
                return PackOpeningGate04R010Occlusion.Sealed;
            }
            if (elapsed < ImpactStart)
            {
                return PackOpeningGate04R010Occlusion.AperturePartial;
            }
            return packRetreat < 0.999f
                ? PackOpeningGate04R010Occlusion.CrossingOccluder
                : PackOpeningGate04R010Occlusion.PackGone;
        }

        private static void AddCrossing(
            ICollection<PackOpeningGate04R010SemanticEvent> events,
            float previous,
            float current,
            float threshold,
            PackOpeningGate04R010SemanticEvent semanticEvent)
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
