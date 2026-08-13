using System;

namespace FidgetingApp.GachaBox
{
    /// <summary>
    /// Rattle signature heard/felt when shaking the sealed box: an impulse
    /// weight train with fixed spacing. Rarity is identifiable by pattern
    /// ("listen for the heirloom"), never by any physics change.
    /// </summary>
    public readonly struct GachaBoxRattleSignature
    {
        public GachaBoxRattleSignature(float[] impulseWeights, float impulseSpacingSeconds)
        {
            ImpulseWeights = impulseWeights ?? Array.Empty<float>();
            ImpulseSpacingSeconds = Math.Max(0f, impulseSpacingSeconds);
        }

        public float[] ImpulseWeights { get; }
        public float ImpulseSpacingSeconds { get; }
    }

    /// <summary>
    /// Single source of truth for the blind-box interaction feel. All values
    /// are deterministic rules consumed by the state machine; nothing here
    /// writes physics or renders haptics directly.
    /// </summary>
    public static class GachaBoxProfile
    {
        /// <summary>Shake enter threshold, in g of user acceleration.</summary>
        public const float ShakeEnterG = 0.30f;

        /// <summary>Hysteresis exit threshold; re-arms the shake latch.</summary>
        public const float ShakeExitG = 0.18f;

        /// <summary>Minimum seconds between rattle bursts.</summary>
        public const float ShakeCooldownSeconds = 0.35f;

        /// <summary>
        /// Radians of finger rub arc that fully warm the box (about three
        /// full circles).
        /// </summary>
        public const float WarmthFullArcRadians = (float)(6.0 * Math.PI);

        /// <summary>Warmth half-life once the finger goes idle.</summary>
        public const float WarmthDecayHalfLifeSeconds = 1.2f;

        /// <summary>Normalized lid drag where the magnetic seal breaks.</summary>
        public const float LidBreakawayThreshold = 0.44f;

        /// <summary>Seconds between breakaway and the lid popping open.</summary>
        public const float LidPopDelaySeconds = 0.18f;

        private static readonly GachaBoxRattleSignature[] rattleByRarity =
        {
            // Standard: one light knock.
            new GachaBoxRattleSignature(new[] { 0.35f }, 0f),
            // Refined: a dense double tap.
            new GachaBoxRattleSignature(new[] { 0.55f, 0.50f }, 0.070f),
            // Signature: one heavy landing with an inertia tail.
            new GachaBoxRattleSignature(new[] { 0.85f, 0.30f }, 0.110f),
            // Heirloom: the unmistakable weighted triple.
            new GachaBoxRattleSignature(new[] { 0.95f, 0.80f, 0.90f }, 0.090f)
        };

        public static GachaBoxRattleSignature RattleSignature(int rarityIndex)
        {
            if (rarityIndex < 0)
            {
                rarityIndex = 0;
            }

            if (rarityIndex >= rattleByRarity.Length)
            {
                rarityIndex = rattleByRarity.Length - 1;
            }

            return rattleByRarity[rarityIndex];
        }
    }
}
