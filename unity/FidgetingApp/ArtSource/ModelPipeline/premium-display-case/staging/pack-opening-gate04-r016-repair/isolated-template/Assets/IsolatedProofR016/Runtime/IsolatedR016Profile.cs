using FidgetingApp.DisplayCase.MakeItShineCc0;
using UnityEngine;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R016
{
    public enum IsolatedR016Phase
    {
        Sealed,
        TabCatch,
        Resistance,
        TearPropagation,
        FormedMouth,
        CaseContained,
        ContinuousRise,
        Complete
    }

    public enum IsolatedR016Occlusion
    {
        Sealed,
        MouthOpening,
        CaseContained,
        CaseCrossingMouth,
        PackRetreating,
        PackGone
    }

    public readonly struct IsolatedR016Sample
    {
        public IsolatedR016Sample(
            IsolatedR016Phase phase,
            IsolatedR016Occlusion occlusion,
            float tearProgress,
            float packDissolve,
            float caseTravel,
            float contourSweep)
        {
            Phase = phase;
            Occlusion = occlusion;
            TearProgress = tearProgress;
            PackDissolve = packDissolve;
            CaseTravel = caseTravel;
            ContourSweep = contourSweep;
        }

        public IsolatedR016Phase Phase { get; }
        public IsolatedR016Occlusion Occlusion { get; }
        public float TearProgress { get; }
        public float PackDissolve { get; }
        public float CaseTravel { get; }
        public float ContourSweep { get; }
    }

    [CreateAssetMenu(
        fileName = "IsolatedR016Profile",
        menuName = "Fidgeting/Display Case/Isolated R016 Profile")]
    public sealed class IsolatedR016Profile : ScriptableObject
    {
        public const float TotalSeconds = 1.60f;
        public const float TabCatchStart = 0.14f;
        public const float TabCatchEnd = 0.32f;
        public const float ResistanceEnd = 0.50f;
        public const float TearPropagationEnd = 0.76f;
        public const float CaseContainedEnd = 1.03f;
        public const float ContinuousRiseEnd = 1.28f;
        public const float PackDiscardStart = 1.30f;
        public const float PackDiscardEnd = 1.58f;

        public static readonly float[] AuthoredPoseProgresses =
        {
            0f, 0.11f, 0.28f, 0.50f, 0.70f, 0.86f, 1f
        };

        public IsolatedR016Sample Evaluate(
            float elapsedSeconds,
            bool effectsEnabled)
        {
            float elapsed = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            float tear = ResolveTearProgress(elapsed);
            float caseTravel = Smooth01(Mathf.InverseLerp(
                CaseContainedEnd,
                TotalSeconds,
                elapsed));
            float discardTime = Mathf.InverseLerp(
                PackDiscardStart,
                PackDiscardEnd,
                elapsed);
            float discard = elapsed < PackDiscardStart
                ? 0f
                : MakeItShineCc0EffectCurves
                    .CreateDiscardDissolveCurve()
                    .Evaluate(discardTime);
            float contourSweep = effectsEnabled
                ? SingleContourSweep(elapsed)
                : 0f;
            return new IsolatedR016Sample(
                ResolvePhase(elapsed),
                ResolveOcclusion(tear, caseTravel, discard),
                tear,
                Mathf.Clamp01(discard),
                caseTravel,
                contourSweep);
        }

        private static float ResolveTearProgress(float elapsed)
        {
            if (elapsed < TabCatchStart)
            {
                return 0f;
            }
            if (elapsed < TabCatchEnd)
            {
                return Mathf.Lerp(
                    0f,
                    0.11f,
                    Smooth01(Mathf.InverseLerp(
                        TabCatchStart,
                        TabCatchEnd,
                        elapsed)));
            }
            if (elapsed < ResistanceEnd)
            {
                return Mathf.Lerp(
                    0.11f,
                    0.28f,
                    Smooth01(Mathf.InverseLerp(
                        TabCatchEnd,
                        ResistanceEnd,
                        elapsed)));
            }
            if (elapsed < TearPropagationEnd)
            {
                return Mathf.Lerp(
                    0.28f,
                    0.70f,
                    Smooth01(Mathf.InverseLerp(
                        ResistanceEnd,
                        TearPropagationEnd,
                        elapsed)));
            }
            if (elapsed < CaseContainedEnd)
            {
                return Mathf.Lerp(
                    0.70f,
                    0.86f,
                    Smooth01(Mathf.InverseLerp(
                        TearPropagationEnd,
                        CaseContainedEnd,
                        elapsed)));
            }
            return Mathf.Lerp(
                0.86f,
                1f,
                Smooth01(Mathf.InverseLerp(
                    CaseContainedEnd,
                    ContinuousRiseEnd,
                    elapsed)));
        }

        private static IsolatedR016Phase ResolvePhase(float elapsed)
        {
            if (elapsed < TabCatchStart) return IsolatedR016Phase.Sealed;
            if (elapsed < TabCatchEnd) return IsolatedR016Phase.TabCatch;
            if (elapsed < ResistanceEnd) return IsolatedR016Phase.Resistance;
            if (elapsed < TearPropagationEnd)
            {
                return IsolatedR016Phase.TearPropagation;
            }
            if (elapsed < 0.90f) return IsolatedR016Phase.FormedMouth;
            if (elapsed < CaseContainedEnd)
            {
                return IsolatedR016Phase.CaseContained;
            }
            if (elapsed < PackDiscardEnd)
            {
                return IsolatedR016Phase.ContinuousRise;
            }
            return IsolatedR016Phase.Complete;
        }

        private static IsolatedR016Occlusion ResolveOcclusion(
            float tear,
            float caseTravel,
            float discard)
        {
            if (tear <= 0.001f) return IsolatedR016Occlusion.Sealed;
            if (tear < 0.70f) return IsolatedR016Occlusion.MouthOpening;
            if (caseTravel <= 0.01f)
            {
                return IsolatedR016Occlusion.CaseContained;
            }
            if (discard <= 0.01f)
            {
                return IsolatedR016Occlusion.CaseCrossingMouth;
            }
            if (discard < 0.999f)
            {
                return IsolatedR016Occlusion.PackRetreating;
            }
            return IsolatedR016Occlusion.PackGone;
        }

        private static float SingleContourSweep(float elapsed)
        {
            if (elapsed <= 0.42f || elapsed >= 0.98f)
            {
                return 0f;
            }
            float progress = Mathf.InverseLerp(0.42f, 0.98f, elapsed);
            return Mathf.Sin(progress * Mathf.PI) * 0.24f;
        }

        private static float Smooth01(float value)
        {
            float clamped = Mathf.Clamp01(value);
            return clamped * clamped * (3f - 2f * clamped);
        }
    }
}
