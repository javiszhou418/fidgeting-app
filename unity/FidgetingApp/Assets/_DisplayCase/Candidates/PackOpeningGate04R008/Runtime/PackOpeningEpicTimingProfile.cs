using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates
{
    public enum PackOpeningEpicPhase
    {
        Handoff,
        Anticipation,
        Resistance,
        Snap,
        Tear,
        Impact,
        Reveal,
        NativeSettle,
        Complete
    }

    public readonly struct PackOpeningEpicSample
    {
        public PackOpeningEpicSample(
            PackOpeningEpicPhase phase,
            float tearProgress,
            float packDissolve,
            float impact,
            float caseRotationDegrees,
            float title,
            float chip,
            float info,
            float cta,
            bool fakeOut,
            bool hitstop,
            bool cameraEffectsEnabled)
        {
            Phase = phase;
            TearProgress = tearProgress;
            PackDissolve = packDissolve;
            Impact = impact;
            CaseRotationDegrees = caseRotationDegrees;
            Title = title;
            Chip = chip;
            Info = info;
            Cta = cta;
            FakeOut = fakeOut;
            Hitstop = hitstop;
            CameraEffectsEnabled = cameraEffectsEnabled;
        }

        public PackOpeningEpicPhase Phase { get; }
        public float TearProgress { get; }
        public float PackDissolve { get; }
        public float Impact { get; }
        public float CaseRotationDegrees { get; }
        public float Title { get; }
        public float Chip { get; }
        public float Info { get; }
        public float Cta { get; }
        public bool FakeOut { get; }
        public bool Hitstop { get; }
        public bool CameraEffectsEnabled { get; }
    }

    [CreateAssetMenu(
        fileName = "PackOpeningEpicTimingProfile",
        menuName = "Fidgeting/Display Case/Candidates/Pack Opening Epic Timing")]
    public sealed class PackOpeningEpicTimingProfile : ScriptableObject
    {
        public const float TotalSeconds = 3.10f;
        public const float HandoffEnd = 0.35f;
        public const float AnticipationEnd = 0.65f;
        public const float ResistanceEnd = 0.95f;
        public const float SnapEnd = 1.00f;
        public const float TearEnd = 1.75f;
        public const float FakeOutStart = 1.55f;
        public const float FakeOutEnd = 1.61f;
        public const float ImpactEnd = 1.93f;
        public const float RevealEnd = 2.53f;
        public const float TitleStart = 2.53f;
        public const float ChipStart = 2.64f;
        public const float InfoStart = 2.76f;
        public const float CtaStart = 2.90f;
        public const float HitstopStart = 1.78f;
        public const float HitstopEnd = 1.84f;
        public const float SkipLandingSeconds = 0.20f;
        public const float StartCaseRotationDegrees = -25f;

        [SerializeField] private AnimationCurve tearCurve =
            AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
        [SerializeField] private AnimationCurve revealCurve =
            AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
        [SerializeField] private AnimationCurve settleCurve =
            AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);

        public PackOpeningEpicSample Evaluate(
            float elapsedSeconds,
            bool reduceMotion = false)
        {
            float elapsed = Mathf.Clamp(elapsedSeconds, 0f, TotalSeconds);
            PackOpeningEpicPhase phase = ResolvePhase(elapsed);
            float tear = Evaluate01(
                tearCurve,
                Mathf.InverseLerp(SnapEnd, TearEnd, elapsed));
            float dissolve = Evaluate01(
                tearCurve,
                Mathf.InverseLerp(FakeOutEnd, TearEnd, elapsed));
            float impact = reduceMotion
                ? 0f
                : Mathf.Sin(
                    Mathf.InverseLerp(TearEnd, ImpactEnd, elapsed) * Mathf.PI);
            if (elapsed < TearEnd || elapsed > ImpactEnd)
            {
                impact = 0f;
            }

            float reveal = Evaluate01(
                revealCurve,
                Mathf.InverseLerp(ImpactEnd, RevealEnd, elapsed));
            float rotation = Mathf.Lerp(
                StartCaseRotationDegrees,
                0f,
                Evaluate01(settleCurve, reveal));
            float title = StepProgress(elapsed, TitleStart, 0.14f);
            float chip = StepProgress(elapsed, ChipStart, 0.14f);
            float info = StepProgress(elapsed, InfoStart, 0.14f);
            float cta = StepProgress(elapsed, CtaStart, 0.20f);

            return new PackOpeningEpicSample(
                phase,
                tear,
                dissolve,
                impact,
                elapsed < ImpactEnd ? StartCaseRotationDegrees : rotation,
                title,
                chip,
                info,
                cta,
                !reduceMotion && elapsed >= FakeOutStart && elapsed < FakeOutEnd,
                !reduceMotion && elapsed >= HitstopStart && elapsed < HitstopEnd,
                !reduceMotion);
        }

        public PackOpeningEpicSample SkipLandingSample(bool reduceMotion = false)
        {
            return Evaluate(TotalSeconds, reduceMotion);
        }

        private static PackOpeningEpicPhase ResolvePhase(float elapsed)
        {
            if (elapsed < HandoffEnd) return PackOpeningEpicPhase.Handoff;
            if (elapsed < AnticipationEnd) return PackOpeningEpicPhase.Anticipation;
            if (elapsed < ResistanceEnd) return PackOpeningEpicPhase.Resistance;
            if (elapsed < SnapEnd) return PackOpeningEpicPhase.Snap;
            if (elapsed < TearEnd) return PackOpeningEpicPhase.Tear;
            if (elapsed < ImpactEnd) return PackOpeningEpicPhase.Impact;
            if (elapsed < RevealEnd) return PackOpeningEpicPhase.Reveal;
            if (elapsed < TotalSeconds) return PackOpeningEpicPhase.NativeSettle;
            return PackOpeningEpicPhase.Complete;
        }

        private static float Evaluate01(AnimationCurve curve, float progress)
        {
            float clamped = Mathf.Clamp01(progress);
            return Mathf.Clamp01(curve != null ? curve.Evaluate(clamped) : clamped);
        }

        private static float StepProgress(
            float elapsed,
            float start,
            float duration)
        {
            return Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(
                start,
                start + duration,
                elapsed));
        }
    }
}
