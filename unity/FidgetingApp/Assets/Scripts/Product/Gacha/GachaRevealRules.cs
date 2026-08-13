using UnityEngine;
using FidgetingApp.DisplayCase;

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Per-rarity reveal signature. The premium display case timeline is a
    /// frozen 2.20 s contract, so rarity never stretches it; higher tiers add
    /// a suspense hold before play() plus a director-owned accent light. The
    /// case prefab itself stays neutral (PRODUCT_PLAN: prize lighting must not
    /// be baked into any specific model).
    /// </summary>
    public readonly struct GachaRevealSignature
    {
        public GachaRevealSignature(
            float suspenseHoldSeconds,
            Color liningColor,
            float accentIntensity)
        {
            SuspenseHoldSeconds = Mathf.Max(0f, suspenseHoldSeconds);
            LiningColor = liningColor;
            AccentIntensity = Mathf.Clamp01(accentIntensity);
        }

        public float SuspenseHoldSeconds { get; }
        public Color LiningColor { get; }
        public float AccentIntensity { get; }
    }

    public static class GachaRevealRules
    {
        public const float SignatureSuspenseSeconds = 0.6f;
        public const float HeirloomSuspenseSeconds = 1.2f;

        /// <summary>Peak lumen budget for the director-owned accent light.</summary>
        public const float AccentLightMaxIntensity = 1.6f;

        public static GachaRevealSignature Signature(GachaRarity rarity)
        {
            return rarity switch
            {
                GachaRarity.Heirloom => new GachaRevealSignature(
                    HeirloomSuspenseSeconds,
                    new Color(0.42f, 0.58f, 0.62f),
                    1.0f),
                GachaRarity.Signature => new GachaRevealSignature(
                    SignatureSuspenseSeconds,
                    new Color(0.36f, 0.22f, 0.12f),
                    0.8f),
                GachaRarity.Refined => new GachaRevealSignature(
                    0f,
                    new Color(0.16f, 0.22f, 0.30f),
                    0.55f),
                _ => new GachaRevealSignature(
                    0f,
                    new Color(0.13f, 0.13f, 0.14f),
                    0.35f)
            };
        }

        public static PremiumDisplayCaseCapsulePreset CapsulePresetFor(GachaPrizeKind kind)
        {
            return kind switch
            {
                GachaPrizeKind.Toy => PremiumDisplayCaseCapsulePreset.CircularDeep,
                GachaPrizeKind.DisplayBase =>
                    PremiumDisplayCaseCapsulePreset.RoundedSquareDeep,
                GachaPrizeKind.Sticker =>
                    PremiumDisplayCaseCapsulePreset.RoundedSquareStandard,
                GachaPrizeKind.EnvironmentTint =>
                    PremiumDisplayCaseCapsulePreset.RoundedSquareStandard,
                _ => PremiumDisplayCaseCapsulePreset.CircularStandard
            };
        }

        public static float TotalRevealSeconds(GachaRarity rarity)
        {
            return Signature(rarity).SuspenseHoldSeconds
                + PremiumDisplayCaseRevealMotion.DurationSeconds;
        }

        /// <summary>
        /// Accent light envelope over the case's reveal progress: silent
        /// through the lid phase, a sine swell across the content reveal, and
        /// a small sustained floor once complete so the lining tint reads
        /// while the prize orbits.
        /// </summary>
        public static float AccentEnvelope(float revealProgress)
        {
            float t = Mathf.Clamp01(revealProgress);
            const float sustain = 0.22f;
            if (t <= 0.34f)
            {
                return 0f;
            }

            float swell = Mathf.Sin(Mathf.InverseLerp(0.34f, 1f, t) * Mathf.PI);
            return Mathf.Max(swell, t >= 0.96f ? sustain : 0f);
        }
    }
}
