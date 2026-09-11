using System;
using FidgetingApp.DisplayCase.MakeItShineCc0;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    public enum PremiumDisplayCaseShippingPhase
    {
        Entry = 0,
        EntryFirstSpinOverlap = 1,
        FirstSpin = 2,
        SecondSpin = 3,
        Sheen = 4,
        Hold = 5,
        Complete = 6
    }

    public readonly struct PremiumDisplayCaseShippingSample
    {
        public PremiumDisplayCaseShippingSample(
            PremiumDisplayCaseShippingPhase phase,
            Vector3 positionOffset,
            float localYawDegrees,
            float lightRevealProgress,
            float lightRevealWidth,
            float lightRevealStrength,
            float rotationRimProgress,
            float rotationRimStrength,
            int rotationRimPass,
            float sheenCenter,
            float sheenWidth,
            float sheenStrength,
            float sheenFalloff,
            bool complete)
        {
            Phase = phase;
            PositionOffset = positionOffset;
            LocalYawDegrees = localYawDegrees;
            LightRevealProgress = lightRevealProgress;
            LightRevealWidth = lightRevealWidth;
            LightRevealStrength = lightRevealStrength;
            RotationRimProgress = rotationRimProgress;
            RotationRimStrength = rotationRimStrength;
            RotationRimPass = rotationRimPass;
            SheenCenter = sheenCenter;
            SheenWidth = sheenWidth;
            SheenStrength = sheenStrength;
            SheenFalloff = sheenFalloff;
            Complete = complete;
        }

        public PremiumDisplayCaseShippingPhase Phase { get; }
        public Vector3 PositionOffset { get; }
        public float LocalYawDegrees { get; }
        public float LightRevealProgress { get; }
        public float LightRevealWidth { get; }
        public float LightRevealStrength { get; }
        public float RotationRimProgress { get; }
        public float RotationRimStrength { get; }
        public int RotationRimPass { get; }
        public float SheenCenter { get; }
        public float SheenWidth { get; }
        public float SheenStrength { get; }
        public float SheenFalloff { get; }
        public bool Complete { get; }
    }

    /// <summary>
    /// One frame of director-driven pose for
    /// <see cref="PremiumDisplayCaseShippingPresentation.ApplyDirectedPose"/>.
    /// Offsets and yaw are relative to the authored pose; scale multiplies
    /// the authored scale.
    /// </summary>
    public struct PremiumDisplayCaseDirectedPose
    {
        public Vector3 PositionOffset;
        public float YawDegrees;
        public float TiltDegrees;
        public float ScaleMultiplier;
        public float LightRevealProgress;
        public float LightRevealWidth;
        public float LightRevealStrength;
        public float RotationRimProgress;
        public float RotationRimStrength;
        public float SheenCenter;
        public float SheenWidth;
        public float SheenStrength;
        public float SheenFalloff;
        /// <summary>Edge glow colour; null keeps the material's neutral rim.</summary>
        public Color? RimColor;
        /// <summary>Edge glow 0–1 above the material's resting rim strength.</summary>
        public float RimGlow;
        public float LabelAlpha;
        public bool Complete;

        public static PremiumDisplayCaseDirectedPose Rest(
            float yawDegrees,
            float labelAlpha,
            bool complete)
        {
            return new PremiumDisplayCaseDirectedPose
            {
                PositionOffset = Vector3.zero,
                YawDegrees = yawDegrees,
                TiltDegrees = 0f,
                ScaleMultiplier = 1f,
                LightRevealWidth = 0.18f,
                SheenWidth = 0.16f,
                SheenFalloff = 0.30f,
                RimColor = null,
                RimGlow = 0f,
                LabelAlpha = labelAlpha,
                Complete = complete
            };
        }
    }

    [CreateAssetMenu(
        fileName = "PremiumDisplayCaseRevealProfile",
        menuName = "Fidgeting/Display Case/Reveal Profile")]
    public sealed class PremiumDisplayCaseRevealProfile : ScriptableObject
    {
        public const float PreviousApprovedTotalDurationSeconds = 4.60f;
        public const float PreviousApprovedHandoffDurationSeconds = 0.28f;
        public const float CandidateHandoffDurationSeconds = 0.14f;
        public const float CandidateEntryDurationSeconds = 0.56f;
        public const float CandidateFirstSpinDurationSeconds = 0.50f;
        public const float CandidateSecondSpinDurationSeconds = 1.10f;
        public const float CandidateEntryRotationOverlapSeconds = 0.18f;
        public const float CandidateArrivalRimDurationSeconds = 0.28f;
        public const float CandidateSheenDurationSeconds = 0.34f;
        public const float CandidateHoldDurationSeconds = 0.62f;
        public const float CandidateLightRevealWidth = 0.18f;
        public const float CandidateArrivalRimIntensity = 1.00f;
        public const float CandidateFirstRotationRimIntensity = 0.92f;
        public const float CandidateSecondRotationRimIntensity = 0.74f;
        public const float CandidateSheenWidth = 0.16f;
        public const float CandidateSheenIntensity = 1.00f;
        public const float CandidateSheenFalloff = 0.30f;

        [Header("Candidate timing")]
        [SerializeField, Min(0.05f)] private float handoffDurationSeconds =
            CandidateHandoffDurationSeconds;
        [SerializeField, Min(0.05f)] private float entryDurationSeconds =
            CandidateEntryDurationSeconds;
        [SerializeField, Min(0.05f)] private float firstSpinDurationSeconds =
            CandidateFirstSpinDurationSeconds;
        [SerializeField, Min(0.05f)] private float secondSpinDurationSeconds =
            CandidateSecondSpinDurationSeconds;
        [SerializeField, Min(0f)] private float entryRotationOverlapSeconds =
            CandidateEntryRotationOverlapSeconds;
        [SerializeField, Min(0.05f)] private float arrivalRimDurationSeconds =
            CandidateArrivalRimDurationSeconds;
        [SerializeField, Min(0.05f)] private float sheenDurationSeconds =
            CandidateSheenDurationSeconds;
        [SerializeField, Min(0f)] private float holdDurationSeconds =
            CandidateHoldDurationSeconds;

        [Header("Candidate motion")]
        [SerializeField] private float entryYOffsetMeters = -0.18f;
        [SerializeField, Min(0f)] private float entryCameraDepthZMeters = 0.11f;
        [SerializeField] private float firstSpinDegrees = 360f;
        [SerializeField] private float secondSpinDegrees = 360f;
        [SerializeField] private AnimationCurve entryEase =
            AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
        [SerializeField] private AnimationCurve firstSpinEase =
            AnimationCurve.Linear(0f, 0f, 1f, 1f);
        [SerializeField] private AnimationCurve secondSpinEase =
            AnimationCurve.Linear(0f, 0f, 1f, 1f);

        [Header("Candidate mesh reveal")]
        [SerializeField] private AnimationCurve lightRevealEase =
            AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
        [SerializeField, Range(0.01f, 0.5f)] private float lightRevealWidth =
            CandidateLightRevealWidth;
        [SerializeField, Range(0f, 1f)] private float lightRevealIntensity =
            CandidateArrivalRimIntensity;

        [Header("Candidate object-bound rotation rim")]
        [SerializeField, Range(0f, 1f)] private float firstRotationRimIntensity =
            CandidateFirstRotationRimIntensity;
        [SerializeField, Range(0f, 1f)] private float secondRotationRimIntensity =
            CandidateSecondRotationRimIntensity;

        [Header("Candidate mesh sheen")]
        [SerializeField] private AnimationCurve sheenEase =
            AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
        [SerializeField] private float sheenStart = -0.62f;
        [SerializeField] private float sheenEnd = 0.62f;
        [SerializeField, Range(0.01f, 0.5f)] private float sheenWidth =
            CandidateSheenWidth;
        [SerializeField, Range(0f, 1f)] private float sheenIntensity =
            CandidateSheenIntensity;
        [SerializeField, Range(0.05f, 0.95f)] private float sheenFalloff =
            CandidateSheenFalloff;

        public float HandoffDurationSeconds => handoffDurationSeconds;
        public float EntryDurationSeconds => entryDurationSeconds;
        public float FirstSpinDurationSeconds => firstSpinDurationSeconds;
        public float SecondSpinDurationSeconds => secondSpinDurationSeconds;
        public float RotationDurationSeconds =>
            FirstSpinDurationSeconds + SecondSpinDurationSeconds;
        public float EntryRotationOverlapSeconds => Mathf.Min(
            entryRotationOverlapSeconds,
            Mathf.Min(entryDurationSeconds, firstSpinDurationSeconds));
        public float ArrivalRimDurationSeconds => Mathf.Min(
            arrivalRimDurationSeconds,
            EntryDurationSeconds);
        public float SheenDurationSeconds => sheenDurationSeconds;
        public float HoldDurationSeconds => holdDurationSeconds;
        public float FirstSpinStartSeconds =>
            EntryDurationSeconds - EntryRotationOverlapSeconds;
        public float RotationStartSeconds => FirstSpinStartSeconds;
        public float FirstSpinEndSeconds =>
            FirstSpinStartSeconds + FirstSpinDurationSeconds;
        public float SecondSpinEndSeconds =>
            FirstSpinEndSeconds + SecondSpinDurationSeconds;
        public float RotationEndSeconds => SecondSpinEndSeconds;
        public float SheenEndSeconds =>
            SecondSpinEndSeconds + SheenDurationSeconds;
        public float TotalDurationSeconds => SheenEndSeconds + HoldDurationSeconds;
        public float FirstSpinDegrees => firstSpinDegrees;
        public float SecondSpinDegrees => secondSpinDegrees;
        public float LocalYawDegrees => FirstSpinDegrees + SecondSpinDegrees;
        public float AverageFirstSpinDegreesPerSecond =>
            FirstSpinDegrees / FirstSpinDurationSeconds;
        public float AverageSecondSpinDegreesPerSecond =>
            SecondSpinDegrees / SecondSpinDurationSeconds;
        public float LightRevealIntensity => lightRevealIntensity;
        public float FirstRotationRimIntensity => firstRotationRimIntensity;
        public float SecondRotationRimIntensity => secondRotationRimIntensity;
        public float SheenIntensity => sheenIntensity;
        public bool UsesCc0LightRevealCurve =>
            MakeItShineCc0EffectCurves.MatchesDiscardDissolveCurve(
                lightRevealEase);

        public PremiumDisplayCaseShippingSample Evaluate(float elapsedSeconds)
        {
            float elapsed = Mathf.Max(0f, elapsedSeconds);
            float entryProgress = EvaluateCurve(
                entryEase,
                Mathf.InverseLerp(0f, EntryDurationSeconds, elapsed));
            Vector3 position = new Vector3(
                0f,
                Mathf.Lerp(entryYOffsetMeters, 0f, entryProgress),
                Mathf.Lerp(entryCameraDepthZMeters, 0f, entryProgress));

            float firstSpinTime = Mathf.InverseLerp(
                FirstSpinStartSeconds,
                FirstSpinEndSeconds,
                elapsed);
            float firstSpinProgress = EvaluateCurve(
                firstSpinEase,
                firstSpinTime);
            float secondSpinTime = Mathf.InverseLerp(
                FirstSpinEndSeconds,
                SecondSpinEndSeconds,
                elapsed);
            float secondSpinProgress = EvaluateCurve(
                secondSpinEase,
                secondSpinTime);
            float yaw = FirstSpinDegrees * firstSpinProgress
                + SecondSpinDegrees * secondSpinProgress;

            float rotationRimProgress = 0f;
            float rotationRimStrength = 0f;
            int rotationRimPass = 0;
            if (elapsed >= FirstSpinStartSeconds
                && elapsed < FirstSpinEndSeconds)
            {
                rotationRimPass = 1;
                rotationRimProgress = firstSpinProgress;
                rotationRimStrength = firstRotationRimIntensity
                    * Mathf.Sin(Mathf.Clamp01(firstSpinTime) * Mathf.PI);
            }
            else if (elapsed >= FirstSpinEndSeconds
                     && elapsed < SecondSpinEndSeconds)
            {
                rotationRimPass = 2;
                rotationRimProgress = secondSpinProgress;
                rotationRimStrength = secondRotationRimIntensity
                    * Mathf.Sin(Mathf.Clamp01(secondSpinTime) * Mathf.PI);
            }

            float lightRevealTime = Mathf.InverseLerp(
                0f,
                ArrivalRimDurationSeconds,
                elapsed);
            float lightRevealProgress = EvaluateCurve(
                lightRevealEase,
                lightRevealTime);
            bool inLightReveal = elapsed > 0f
                && elapsed < ArrivalRimDurationSeconds;
            float lightRevealEnvelope = inLightReveal
                ? Mathf.Sin(Mathf.Clamp01(lightRevealProgress) * Mathf.PI)
                : 0f;

            float sheenProgress = EvaluateCurve(
                sheenEase,
                Mathf.InverseLerp(
                    SecondSpinEndSeconds,
                    SheenEndSeconds,
                    elapsed));
            bool inSheen = elapsed >= SecondSpinEndSeconds
                && elapsed < SheenEndSeconds;
            float sheenEnvelope = inSheen
                ? Mathf.Sin(Mathf.Clamp01(sheenProgress) * Mathf.PI)
                : 0f;

            PremiumDisplayCaseShippingPhase phase;
            if (elapsed < FirstSpinStartSeconds)
            {
                phase = PremiumDisplayCaseShippingPhase.Entry;
            }
            else if (elapsed < EntryDurationSeconds)
            {
                phase =
                    PremiumDisplayCaseShippingPhase.EntryFirstSpinOverlap;
            }
            else if (elapsed < FirstSpinEndSeconds)
            {
                phase = PremiumDisplayCaseShippingPhase.FirstSpin;
            }
            else if (elapsed < SecondSpinEndSeconds)
            {
                phase = PremiumDisplayCaseShippingPhase.SecondSpin;
            }
            else if (elapsed < SheenEndSeconds)
            {
                phase = PremiumDisplayCaseShippingPhase.Sheen;
            }
            else if (elapsed < TotalDurationSeconds)
            {
                phase = PremiumDisplayCaseShippingPhase.Hold;
            }
            else
            {
                phase = PremiumDisplayCaseShippingPhase.Complete;
            }

            return new PremiumDisplayCaseShippingSample(
                phase,
                phase == PremiumDisplayCaseShippingPhase.Complete
                    ? Vector3.zero
                    : position,
                phase == PremiumDisplayCaseShippingPhase.Complete
                    ? LocalYawDegrees
                    : yaw,
                lightRevealProgress,
                lightRevealWidth,
                lightRevealIntensity * lightRevealEnvelope,
                rotationRimProgress,
                rotationRimStrength,
                rotationRimPass,
                Mathf.Lerp(sheenStart, sheenEnd, sheenProgress),
                sheenWidth,
                sheenIntensity * sheenEnvelope,
                sheenFalloff,
                phase == PremiumDisplayCaseShippingPhase.Complete);
        }

        public PremiumDisplayCaseShippingSample FinalSample()
        {
            return Evaluate(TotalDurationSeconds);
        }

        public void ConfigureCandidate(
            float handoffSeconds,
            float entrySeconds,
            float firstSpinSeconds,
            float secondSpinSeconds,
            float overlapSeconds,
            float arrivalRimSeconds,
            float sheenSeconds,
            float holdSeconds,
            float yOffsetMeters,
            float zOffsetMeters,
            float firstDegrees,
            float secondDegrees,
            float revealWidth,
            float revealIntensity,
            float authoredFirstRotationRimIntensity,
            float authoredSecondRotationRimIntensity,
            float authoredSheenWidth,
            float authoredSheenIntensity,
            float authoredSheenFalloff,
            AnimationCurve authoredEntryEase,
            AnimationCurve authoredFirstSpinEase,
            AnimationCurve authoredSecondSpinEase,
            AnimationCurve authoredLightRevealEase,
            AnimationCurve authoredSheenEase)
        {
            handoffDurationSeconds = Mathf.Max(0.05f, handoffSeconds);
            entryDurationSeconds = Mathf.Max(0.05f, entrySeconds);
            firstSpinDurationSeconds = Mathf.Max(0.05f, firstSpinSeconds);
            secondSpinDurationSeconds = Mathf.Max(0.05f, secondSpinSeconds);
            entryRotationOverlapSeconds = Mathf.Clamp(
                overlapSeconds,
                0f,
                Mathf.Min(entryDurationSeconds, firstSpinDurationSeconds));
            arrivalRimDurationSeconds = Mathf.Clamp(
                arrivalRimSeconds,
                0.05f,
                entryDurationSeconds);
            sheenDurationSeconds = Mathf.Max(0.05f, sheenSeconds);
            holdDurationSeconds = Mathf.Max(0f, holdSeconds);
            entryYOffsetMeters = yOffsetMeters;
            entryCameraDepthZMeters = Mathf.Max(0f, zOffsetMeters);
            firstSpinDegrees = firstDegrees;
            secondSpinDegrees = secondDegrees;
            lightRevealWidth = Mathf.Clamp(revealWidth, 0.01f, 0.5f);
            lightRevealIntensity = Mathf.Clamp01(revealIntensity);
            firstRotationRimIntensity = Mathf.Clamp01(
                authoredFirstRotationRimIntensity);
            secondRotationRimIntensity = Mathf.Clamp01(
                authoredSecondRotationRimIntensity);
            sheenWidth = Mathf.Clamp(authoredSheenWidth, 0.01f, 0.5f);
            sheenIntensity = Mathf.Clamp01(authoredSheenIntensity);
            sheenFalloff = Mathf.Clamp(
                authoredSheenFalloff,
                0.05f,
                0.95f);
            entryEase = authoredEntryEase ?? AnimationCurve.Linear(0f, 0f, 1f, 1f);
            firstSpinEase = authoredFirstSpinEase
                ?? AnimationCurve.Linear(0f, 0f, 1f, 1f);
            secondSpinEase = authoredSecondSpinEase
                ?? AnimationCurve.Linear(0f, 0f, 1f, 1f);
            lightRevealEase = authoredLightRevealEase
                ?? AnimationCurve.Linear(0f, 0f, 1f, 1f);
            sheenEase = authoredSheenEase
                ?? AnimationCurve.Linear(0f, 0f, 1f, 1f);
        }

        private static float EvaluateCurve(AnimationCurve curve, float value)
        {
            return Mathf.Clamp01(
                curve != null ? curve.Evaluate(Mathf.Clamp01(value)) : value);
        }
    }
}
