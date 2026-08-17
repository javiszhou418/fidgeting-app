using UnityEngine;
using FidgetingApp.DisplayCase;

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Per-rarity visual signature. Rarity may color and scale the final sheen
    /// but never changes the strict six-phase clock or the neutral case.
    /// </summary>
    public readonly struct GachaRevealSignature
    {
        public GachaRevealSignature(
            Color liningColor,
            float accentIntensity)
        {
            LiningColor = liningColor;
            AccentIntensity = Mathf.Clamp01(accentIntensity);
        }

        public Color LiningColor { get; }
        public float AccentIntensity { get; }
    }

    public static class GachaRevealRules
    {
        public const PremiumDisplayCaseCapsulePreset SharedCapsulePreset =
            PremiumDisplayCaseCapsulePreset.RoundedSquareDeep;

        /// <summary>Peak lumen budget for the director-owned accent light.</summary>
        public const float AccentLightMaxIntensity = 1.6f;

        public static GachaRevealSignature Signature(GachaRarity rarity)
        {
            return rarity switch
            {
                GachaRarity.Heirloom => new GachaRevealSignature(
                    new Color(0.42f, 0.58f, 0.62f),
                    1.0f),
                GachaRarity.Signature => new GachaRevealSignature(
                    new Color(0.36f, 0.22f, 0.12f),
                    0.8f),
                GachaRarity.Refined => new GachaRevealSignature(
                    new Color(0.16f, 0.22f, 0.30f),
                    0.55f),
                _ => new GachaRevealSignature(
                    new Color(0.13f, 0.13f, 0.14f),
                    0.35f)
            };
        }

        public static PremiumDisplayCaseCapsulePreset CapsulePresetFor(GachaPrizeKind kind)
        {
            _ = kind;
            return SharedCapsulePreset;
        }

        public static float TotalRevealSeconds(GachaRarity rarity)
        {
            _ = rarity;
            return GachaRevealTimeline.TotalSeconds;
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
