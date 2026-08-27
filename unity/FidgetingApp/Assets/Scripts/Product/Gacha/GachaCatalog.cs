using System;
using System.Collections.Generic;
using System.Globalization;

namespace FidgetingApp.Product.Gacha
{
    public enum GachaRarity
    {
        Standard = 0,
        Refined = 1,
        Signature = 2,
        Heirloom = 3
    }

    public enum GachaPrizeKind
    {
        ToySkin = 0,
        Sticker = 1,
        DisplayBase = 2,
        EnvironmentTint = 3,
        Toy = 4
    }

    public readonly struct GachaPrizeDefinition
    {
        public GachaPrizeDefinition(
            string id,
            string seriesId,
            GachaRarity rarity,
            GachaPrizeKind kind,
            string displayName,
            string contentReference)
        {
            Id = id ?? string.Empty;
            SeriesId = seriesId ?? string.Empty;
            Rarity = rarity;
            Kind = kind;
            DisplayName = displayName ?? string.Empty;
            ContentReference = contentReference ?? string.Empty;
        }

        public string Id { get; }
        public string SeriesId { get; }
        public GachaRarity Rarity { get; }
        public GachaPrizeKind Kind { get; }
        public string DisplayName { get; }

        /// <summary>
        /// Stable reference consumed by the reveal director: a skin id, a
        /// sticker id, or a Resources prefab path depending on Kind. The
        /// economy layer never dereferences it.
        /// </summary>
        public string ContentReference { get; }
    }

    public readonly struct GachaRates
    {
        public GachaRates(double standard, double refined, double signature, double heirloom)
        {
            Standard = Math.Max(0d, standard);
            Refined = Math.Max(0d, refined);
            Signature = Math.Max(0d, signature);
            Heirloom = Math.Max(0d, heirloom);
        }

        public double Standard { get; }
        public double Refined { get; }
        public double Signature { get; }
        public double Heirloom { get; }

        public double Total => Standard + Refined + Signature + Heirloom;

        public double For(GachaRarity rarity)
        {
            return rarity switch
            {
                GachaRarity.Heirloom => Heirloom,
                GachaRarity.Signature => Signature,
                GachaRarity.Refined => Refined,
                _ => Standard
            };
        }
    }

    public sealed class GachaSeriesDefinition
    {
        public GachaSeriesDefinition(
            string id,
            string displayName,
            GachaRates rates,
            IReadOnlyList<GachaPrizeDefinition> prizes)
        {
            Id = id ?? string.Empty;
            DisplayName = displayName ?? string.Empty;
            Rates = rates;
            Prizes = prizes ?? Array.Empty<GachaPrizeDefinition>();
        }

        public string Id { get; }
        public string DisplayName { get; }
        public GachaRates Rates { get; }
        public IReadOnlyList<GachaPrizeDefinition> Prizes { get; }

        public IReadOnlyList<GachaPrizeDefinition> PrizesOfRarity(GachaRarity rarity)
        {
            var matches = new List<GachaPrizeDefinition>();
            for (int index = 0; index < Prizes.Count; index++)
            {
                if (Prizes[index].Rarity == rarity)
                {
                    matches.Add(Prizes[index]);
                }
            }

            return matches;
        }
    }

    /// <summary>
    /// Draw economy constants. Prizes are cosmetics/collection only; nothing
    /// here may grant XP, physics, or growth multipliers (PRODUCT_PLAN rule:
    /// purchases never replace real fidgeting).
    /// </summary>
    public static class GachaEconomyRules
    {
        public const int SingleDrawTicketCost = 1;
        public const int SingleDrawCoinCost = 160;
        public const int TenDrawCount = 10;
        public const int TenDrawCoinCost = 1440;

        /// <summary>Draws without Signature-or-better before the ramp begins.</summary>
        public const int SignatureSoftPityStart = 40;

        /// <summary>Misses at or above this force Signature (the 51st draw).</summary>
        public const int SignatureHardPity = 50;

        /// <summary>Misses at or above this force Heirloom (the 90th draw).</summary>
        public const int HeirloomHardPity = 89;

        public const GachaRarity TenDrawMinimumRarity = GachaRarity.Refined;

        private static readonly int[] duplicateShardValue = { 1, 3, 12, 40 };
        private static readonly int[] redeemShardCost = { 4, 12, 60, -1 };

        public static int DuplicateShardValue(GachaRarity rarity)
        {
            return duplicateShardValue[(int)rarity];
        }

        public static bool CanRedeem(GachaRarity rarity)
        {
            return redeemShardCost[(int)rarity] > 0;
        }

        public static int RedeemShardCost(GachaRarity rarity)
        {
            int cost = redeemShardCost[(int)rarity];
            return cost > 0 ? cost : int.MaxValue;
        }

        /// <summary>
        /// Effective Signature probability for the next draw given the current
        /// miss counter. Linear ramp from the base rate at the soft-pity start
        /// to 1.0 at hard pity; deterministic and monotonic.
        /// </summary>
        public static double EffectiveSignatureRate(GachaRates rates, int signatureMisses)
        {
            double baseRate = rates.Signature;
            if (signatureMisses >= SignatureHardPity)
            {
                return 1d;
            }

            if (signatureMisses < SignatureSoftPityStart)
            {
                return baseRate;
            }

            // Denominator keeps the ramp strictly below 1 so the guarantee
            // itself only fires at SignatureHardPity (the 51st draw).
            int rampSteps = SignatureHardPity - SignatureSoftPityStart + 1;
            double progress = (signatureMisses - SignatureSoftPityStart + 1d) / rampSteps;
            return baseRate + (1d - baseRate) * Math.Min(1d, progress);
        }
    }

    /// <summary>
    /// Single source of truth for series, pools, and published odds. Adding a
    /// season means adding entries here plus content assets; no code changes.
    /// </summary>
    public static class GachaCatalog
    {
        public const string LaunchSeriesId = "canyon-lode";
        public const string MetalThreeBladePrizeId =
            "canyon-heir-metal-three-blade";
        public const string MetalThreeBladeContentReference =
            "toy/metal-three-blade";

        private static readonly GachaSeriesDefinition[] series =
        {
            new GachaSeriesDefinition(
                LaunchSeriesId,
                "峡谷矿脉",
                new GachaRates(0.70d, 0.24d, 0.05d, 0.01d),
                new[]
                {
                    new GachaPrizeDefinition(
                        "canyon-std-slate-lining", LaunchSeriesId,
                        GachaRarity.Standard, GachaPrizeKind.DisplayBase,
                        "板岩内衬", "display-lining/slate"),
                    new GachaPrizeDefinition(
                        "canyon-std-strata-sticker", LaunchSeriesId,
                        GachaRarity.Standard, GachaPrizeKind.Sticker,
                        "岩层纹贴纸", "sticker/canyon-strata"),
                    new GachaPrizeDefinition(
                        "canyon-std-dust-sticker", LaunchSeriesId,
                        GachaRarity.Standard, GachaPrizeKind.Sticker,
                        "矿尘贴纸", "sticker/canyon-dust"),
                    new GachaPrizeDefinition(
                        "canyon-std-basalt-base", LaunchSeriesId,
                        GachaRarity.Standard, GachaPrizeKind.DisplayBase,
                        "玄武岩底座", "display-base/basalt"),
                    new GachaPrizeDefinition(
                        "canyon-ref-bluesteel-wash", LaunchSeriesId,
                        GachaRarity.Refined, GachaPrizeKind.ToySkin,
                        "蓝钢冲刷", "skin/pointed-three-blade/gacha-bluesteel-wash"),
                    new GachaPrizeDefinition(
                        "canyon-ref-ridge-tint", LaunchSeriesId,
                        GachaRarity.Refined, GachaPrizeKind.EnvironmentTint,
                        "岭线暮色", "environment-tint/canyon-ridge-dusk"),
                    new GachaPrizeDefinition(
                        "canyon-sig-copper-strata", LaunchSeriesId,
                        GachaRarity.Signature, GachaPrizeKind.ToySkin,
                        "铜层岩理", "skin/pointed-three-blade/gacha-copper-strata"),
                    new GachaPrizeDefinition(
                        "canyon-heir-aurora-vein", LaunchSeriesId,
                        GachaRarity.Heirloom, GachaPrizeKind.ToySkin,
                        "极光矿脉", "skin/pointed-three-blade/gacha-aurora-vein"),
                    new GachaPrizeDefinition(
                        MetalThreeBladePrizeId, LaunchSeriesId,
                        GachaRarity.Heirloom, GachaPrizeKind.Toy,
                        "三叶金属陀螺", MetalThreeBladeContentReference)
                })
        };

        public static IReadOnlyList<GachaSeriesDefinition> Series => series;

        public static GachaSeriesDefinition ResolveSeries(string seriesId)
        {
            for (int index = 0; index < series.Length; index++)
            {
                if (series[index].Id == seriesId)
                {
                    return series[index];
                }
            }

            return null;
        }

        public static GachaPrizeDefinition? ResolvePrize(string prizeId)
        {
            for (int seriesIndex = 0; seriesIndex < series.Length; seriesIndex++)
            {
                IReadOnlyList<GachaPrizeDefinition> prizes = series[seriesIndex].Prizes;
                for (int prizeIndex = 0; prizeIndex < prizes.Count; prizeIndex++)
                {
                    if (prizes[prizeIndex].Id == prizeId)
                    {
                        return prizes[prizeIndex];
                    }
                }
            }

            return null;
        }

        /// <summary>
        /// TSV rows for the native store UI. Series rows publish the exact
        /// odds (App Store loot-box disclosure); prize rows list the pool.
        /// </summary>
        public static string CatalogPayload()
        {
            var rows = new List<string>();
            for (int seriesIndex = 0; seriesIndex < series.Length; seriesIndex++)
            {
                GachaSeriesDefinition definition = series[seriesIndex];
                rows.Add(string.Join(
                    "\t",
                    "series",
                    definition.Id,
                    definition.DisplayName,
                    Rate(definition.Rates.Standard),
                    Rate(definition.Rates.Refined),
                    Rate(definition.Rates.Signature),
                    Rate(definition.Rates.Heirloom)));
                for (int prizeIndex = 0; prizeIndex < definition.Prizes.Count; prizeIndex++)
                {
                    GachaPrizeDefinition prize = definition.Prizes[prizeIndex];
                    rows.Add(string.Join(
                        "\t",
                        "prize",
                        prize.Id,
                        prize.SeriesId,
                        ((int)prize.Rarity).ToString(CultureInfo.InvariantCulture),
                        ((int)prize.Kind).ToString(CultureInfo.InvariantCulture),
                        prize.DisplayName));
                }
            }

            return string.Join("\n", rows);
        }

        private static string Rate(double value)
        {
            return value.ToString("0.####", CultureInfo.InvariantCulture);
        }
    }
}
