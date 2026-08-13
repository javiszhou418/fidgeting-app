using System;
using System.Collections.Generic;

namespace FidgetingApp.Product.Gacha
{
    public interface IGachaRandom
    {
        /// <summary>Uniform value in [0, 1).</summary>
        double NextDouble();
    }

    /// <summary>
    /// Deterministic seedable generator (SplitMix64). The engine never touches
    /// UnityEngine.Random so draws replay exactly under a fixed seed in tests.
    /// </summary>
    public sealed class GachaSplitMix64 : IGachaRandom
    {
        private ulong state;

        public GachaSplitMix64(ulong seed)
        {
            state = seed;
        }

        public double NextDouble()
        {
            state += 0x9E3779B97F4A7C15UL;
            ulong z = state;
            z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
            z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
            z ^= z >> 31;
            return (z >> 11) * (1.0 / 9007199254740992.0);
        }
    }

    /// <summary>
    /// Per-series pity counters. Signature misses also reset on Heirloom
    /// because the guarantee is "Signature or better".
    /// </summary>
    public struct GachaPityState
    {
        public int SignatureMisses;
        public int HeirloomMisses;
    }

    public readonly struct GachaDrawOutcome
    {
        public GachaDrawOutcome(
            string prizeId,
            GachaRarity rarity,
            bool forcedBySignaturePity,
            bool forcedByHeirloomPity,
            bool forcedByTenDraw)
        {
            PrizeId = prizeId ?? string.Empty;
            Rarity = rarity;
            ForcedBySignaturePity = forcedBySignaturePity;
            ForcedByHeirloomPity = forcedByHeirloomPity;
            ForcedByTenDraw = forcedByTenDraw;
        }

        public string PrizeId { get; }
        public GachaRarity Rarity { get; }
        public bool ForcedBySignaturePity { get; }
        public bool ForcedByHeirloomPity { get; }
        public bool ForcedByTenDraw { get; }
    }

    /// <summary>
    /// Pure draw logic: rarity roll with pity ramp, hard guarantees, ten-draw
    /// floor, and uniform prize selection inside a rarity pool. Stateless
    /// beyond the caller-owned pity struct; no UnityEngine dependency.
    /// </summary>
    public static class GachaDrawEngine
    {
        public static GachaDrawOutcome Draw(
            GachaSeriesDefinition series,
            ref GachaPityState pity,
            IGachaRandom random)
        {
            return DrawInternal(series, ref pity, random, false);
        }

        /// <summary>
        /// A ten-draw batch: if the first nine stayed Standard the tenth is
        /// floored at Refined. Guarantee flags survive into the outcomes so
        /// the UI can label them honestly.
        /// </summary>
        public static IReadOnlyList<GachaDrawOutcome> DrawBatch(
            GachaSeriesDefinition series,
            int count,
            ref GachaPityState pity,
            IGachaRandom random)
        {
            var outcomes = new List<GachaDrawOutcome>(count);
            bool sawRefinedOrBetter = false;
            for (int index = 0; index < count; index++)
            {
                bool floorApplies = count >= GachaEconomyRules.TenDrawCount
                    && index == count - 1
                    && !sawRefinedOrBetter;
                GachaDrawOutcome outcome = DrawInternal(series, ref pity, random, floorApplies);
                if (outcome.Rarity >= GachaEconomyRules.TenDrawMinimumRarity)
                {
                    sawRefinedOrBetter = true;
                }

                outcomes.Add(outcome);
            }

            return outcomes;
        }

        private static GachaDrawOutcome DrawInternal(
            GachaSeriesDefinition series,
            ref GachaPityState pity,
            IGachaRandom random,
            bool applyTenDrawFloor)
        {
            if (series == null)
            {
                throw new ArgumentNullException(nameof(series));
            }

            bool heirloomForced = pity.HeirloomMisses >= GachaEconomyRules.HeirloomHardPity;
            bool signatureForced = pity.SignatureMisses >= GachaEconomyRules.SignatureHardPity;

            GachaRarity rarity;
            if (heirloomForced)
            {
                rarity = GachaRarity.Heirloom;
            }
            else
            {
                double roll = random.NextDouble();
                double heirloomRate = series.Rates.Heirloom;
                double signatureRate = GachaEconomyRules.EffectiveSignatureRate(
                    series.Rates,
                    pity.SignatureMisses);

                // The pity ramp inflates Signature, so the lower tiers must
                // share the remaining mass at their base ratio or the bands
                // overflow past 1 and worst-luck rolls stop landing Standard.
                double lowerBase = series.Rates.Refined + series.Rates.Standard;
                double remaining = Math.Max(0d, 1d - heirloomRate - signatureRate);
                double refinedRate = lowerBase > 0d
                    ? remaining * (series.Rates.Refined / lowerBase)
                    : 0d;
                if (roll < heirloomRate)
                {
                    rarity = GachaRarity.Heirloom;
                }
                else if (signatureForced || roll < heirloomRate + signatureRate)
                {
                    rarity = GachaRarity.Signature;
                }
                else if (roll < heirloomRate + signatureRate + refinedRate)
                {
                    rarity = GachaRarity.Refined;
                }
                else
                {
                    rarity = GachaRarity.Standard;
                }
            }

            bool tenDrawForced = false;
            if (applyTenDrawFloor && rarity < GachaEconomyRules.TenDrawMinimumRarity)
            {
                rarity = GachaEconomyRules.TenDrawMinimumRarity;
                tenDrawForced = true;
            }

            if (rarity >= GachaRarity.Signature)
            {
                pity.SignatureMisses = 0;
            }
            else
            {
                pity.SignatureMisses += 1;
            }

            if (rarity == GachaRarity.Heirloom)
            {
                pity.HeirloomMisses = 0;
            }
            else
            {
                pity.HeirloomMisses += 1;
            }

            IReadOnlyList<GachaPrizeDefinition> pool = series.PrizesOfRarity(rarity);
            if (pool.Count == 0)
            {
                throw new InvalidOperationException(
                    $"Series '{series.Id}' has no prizes of rarity {rarity}.");
            }

            int prizeIndex = (int)(random.NextDouble() * pool.Count);
            if (prizeIndex >= pool.Count)
            {
                prizeIndex = pool.Count - 1;
            }

            return new GachaDrawOutcome(
                pool[prizeIndex].Id,
                rarity,
                signatureForced && rarity == GachaRarity.Signature,
                heirloomForced,
                tenDrawForced);
        }
    }
}
