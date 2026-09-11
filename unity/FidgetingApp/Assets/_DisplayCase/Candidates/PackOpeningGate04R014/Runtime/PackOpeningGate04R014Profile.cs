using System;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    public enum PackOpeningGate04R014Phase
    {
        Sealed,
        TabCatch,
        NarrowPeel,
        FormedMouth,
        CaseContained,
        ContinuousRise,
        Complete
    }

    public enum PackOpeningGate04R014Occlusion
    {
        Sealed,
        MouthOpening,
        CaseContained,
        CaseCrossingMouth,
        PackRetreating,
        PackGone
    }

    public readonly struct PackOpeningGate04R014Sample
    {
        public PackOpeningGate04R014Sample(
            PackOpeningGate04R014Phase phase,
            PackOpeningGate04R014Occlusion occlusion,
            float tearProgress,
            float packDissolve,
            float caseTravel,
            float opticalSweep)
        {
            Phase = phase;
            Occlusion = occlusion;
            TearProgress = tearProgress;
            PackDissolve = packDissolve;
            CaseTravel = caseTravel;
            OpticalSweep = opticalSweep;
        }

        public PackOpeningGate04R014Phase Phase { get; }
        public PackOpeningGate04R014Occlusion Occlusion { get; }
        public float TearProgress { get; }
        public float PackDissolve { get; }
        public float CaseTravel { get; }
        public float OpticalSweep { get; }
    }

    [CreateAssetMenu(
        fileName = "PackOpeningGate04R014Profile",
        menuName = "Fidgeting/Display Case/Candidates/Pack Opening Gate 04 R014")]
    public sealed class PackOpeningGate04R014Profile : ScriptableObject
    {
        public const float TotalSeconds = 1.60f;
        public const float TabCatchEnd = 0.30f;
        public const float NarrowPeelEnd = 0.48f;
        public const float FormedMouthEnd = 0.72f;
        public const float CaseContainedEnd = 0.98f;
        public const float ContinuousRiseEnd = 1.24f;
        public const float PackDiscardStart = 1.24f;
        public const float PackDiscardEnd = 1.54f;

        public static readonly float[] AuthoredPoseProgresses =
        {
            0f, 0.12f, 0.28f, 0.48f, 0.68f, 0.84f, 1f
        };

        public PackOpeningGate04R014Sample Evaluate(
            float elapsedSeconds,
            bool reduceMotion = false)
        {
            float elapsed = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            float tear = ResolveTearProgress(elapsed);
            float discardTime = Mathf.InverseLerp(
                PackDiscardStart,
                PackDiscardEnd,
                elapsed);
            float dissolve = elapsed < PackDiscardStart
                ? 0f
                : MakeItShineCc0EffectCurves
                    .CreateDiscardDissolveCurve()
                    .Evaluate(discardTime);
            float caseTravel = Smooth01(Mathf.InverseLerp(
                CaseContainedEnd,
                TotalSeconds,
                elapsed));
            float opticalSweep = reduceMotion
                ? 0f
                : Mathf.Sin(Mathf.Clamp01(Mathf.InverseLerp(
                    0.62f,
                    1.36f,
                    elapsed)) * Mathf.PI);

            return new PackOpeningGate04R014Sample(
                ResolvePhase(elapsed),
                ResolveOcclusion(tear, dissolve, caseTravel),
                tear,
                Mathf.Clamp01(dissolve),
                caseTravel,
                opticalSweep);
        }

        private static float ResolveTearProgress(float elapsed)
        {
            if (elapsed < 0.16f)
            {
                return 0f;
            }
            if (elapsed < TabCatchEnd)
            {
                return Mathf.Lerp(
                    0f,
                    0.12f,
                    Smooth01(Mathf.InverseLerp(0.16f, TabCatchEnd, elapsed)));
            }
            if (elapsed < NarrowPeelEnd)
            {
                return Mathf.Lerp(
                    0.12f,
                    0.28f,
                    Smooth01(Mathf.InverseLerp(
                        TabCatchEnd,
                        NarrowPeelEnd,
                        elapsed)));
            }
            if (elapsed < FormedMouthEnd)
            {
                return Mathf.Lerp(
                    0.28f,
                    0.68f,
                    Smooth01(Mathf.InverseLerp(
                        NarrowPeelEnd,
                        FormedMouthEnd,
                        elapsed)));
            }
            if (elapsed < CaseContainedEnd)
            {
                return Mathf.Lerp(
                    0.68f,
                    0.84f,
                    Smooth01(Mathf.InverseLerp(
                        FormedMouthEnd,
                        CaseContainedEnd,
                        elapsed)));
            }
            return Mathf.Lerp(
                0.84f,
                1f,
                Smooth01(Mathf.InverseLerp(
                    CaseContainedEnd,
                    ContinuousRiseEnd,
                    elapsed)));
        }

        private static PackOpeningGate04R014Phase ResolvePhase(float elapsed)
        {
            if (elapsed < 0.16f) return PackOpeningGate04R014Phase.Sealed;
            if (elapsed < TabCatchEnd) return PackOpeningGate04R014Phase.TabCatch;
            if (elapsed < NarrowPeelEnd) return PackOpeningGate04R014Phase.NarrowPeel;
            if (elapsed < FormedMouthEnd) return PackOpeningGate04R014Phase.FormedMouth;
            if (elapsed < CaseContainedEnd)
            {
                return PackOpeningGate04R014Phase.CaseContained;
            }
            if (elapsed < PackDiscardEnd)
            {
                return PackOpeningGate04R014Phase.ContinuousRise;
            }
            return PackOpeningGate04R014Phase.Complete;
        }

        private static PackOpeningGate04R014Occlusion ResolveOcclusion(
            float tear,
            float dissolve,
            float caseTravel)
        {
            if (tear <= 0.001f)
            {
                return PackOpeningGate04R014Occlusion.Sealed;
            }
            if (tear < 0.68f)
            {
                return PackOpeningGate04R014Occlusion.MouthOpening;
            }
            if (caseTravel <= 0.01f)
            {
                return PackOpeningGate04R014Occlusion.CaseContained;
            }
            if (dissolve < 0.02f)
            {
                return PackOpeningGate04R014Occlusion.CaseCrossingMouth;
            }
            if (dissolve < 0.999f)
            {
                return PackOpeningGate04R014Occlusion.PackRetreating;
            }
            return PackOpeningGate04R014Occlusion.PackGone;
        }

        private static float Smooth01(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return clamped * clamped * (3f - 2f * clamped);
        }
    }
}
