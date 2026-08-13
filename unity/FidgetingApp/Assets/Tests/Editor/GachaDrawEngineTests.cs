using System.Collections.Generic;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaDrawEngineTests
    {
        private sealed class ConstantRandom : IGachaRandom
        {
            private readonly double value;

            public ConstantRandom(double value)
            {
                this.value = value;
            }

            public double NextDouble()
            {
                return value;
            }
        }

        private sealed class QueueRandom : IGachaRandom
        {
            private readonly Queue<double> values;
            private readonly double fallback;

            public QueueRandom(IEnumerable<double> values, double fallback)
            {
                this.values = new Queue<double>(values);
                this.fallback = fallback;
            }

            public double NextDouble()
            {
                return values.Count > 0 ? values.Dequeue() : fallback;
            }
        }

        [Test]
        public void EverySeriesPublishesNormalizedRatesAndFullPools()
        {
            var seenPrizeIds = new HashSet<string>();
            foreach (GachaSeriesDefinition series in GachaCatalog.Series)
            {
                Assert.That(series.Rates.Total, Is.EqualTo(1d).Within(1e-9),
                    $"Rates of '{series.Id}' must sum to 1 for honest odds disclosure.");
                foreach (GachaRarity rarity in new[]
                {
                    GachaRarity.Standard,
                    GachaRarity.Refined,
                    GachaRarity.Signature,
                    GachaRarity.Heirloom
                })
                {
                    Assert.That(series.PrizesOfRarity(rarity), Is.Not.Empty,
                        $"Series '{series.Id}' must stock rarity {rarity}.");
                }

                foreach (GachaPrizeDefinition prize in series.Prizes)
                {
                    Assert.That(seenPrizeIds.Add(prize.Id), Is.True,
                        $"Prize id '{prize.Id}' must be globally unique.");
                    Assert.That(prize.SeriesId, Is.EqualTo(series.Id));
                }
            }
        }

        [Test]
        public void CatalogPayloadPublishesExactOddsPerSeries()
        {
            string payload = GachaCatalog.CatalogPayload();
            StringAssert.Contains(
                "series\tcanyon-lode\t峡谷矿脉\t0.7\t0.24\t0.05\t0.01",
                payload);
            foreach (GachaPrizeDefinition prize in
                GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId).Prizes)
            {
                StringAssert.Contains("prize\t" + prize.Id + "\t", payload);
            }
        }

        [Test]
        public void BaseRarityDistributionConvergesToPublishedRates()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            var random = new GachaSplitMix64(0xF1D6E7UL);
            var counts = new int[4];
            const int draws = 200000;
            for (int index = 0; index < draws; index++)
            {
                var pity = new GachaPityState();
                GachaDrawOutcome outcome = GachaDrawEngine.Draw(series, ref pity, random);
                counts[(int)outcome.Rarity] += 1;
            }

            Assert.That(counts[0] / (double)draws, Is.EqualTo(0.70d).Within(0.01d));
            Assert.That(counts[1] / (double)draws, Is.EqualTo(0.24d).Within(0.01d));
            Assert.That(counts[2] / (double)draws, Is.EqualTo(0.05d).Within(0.005d));
            Assert.That(counts[3] / (double)draws, Is.EqualTo(0.01d).Within(0.003d));
        }

        [Test]
        public void SignatureHardPityForcesTheFiftyFirstDraw()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            var pity = new GachaPityState();
            var worstLuck = new ConstantRandom(0.9999d);
            for (int draw = 1; draw <= 50; draw++)
            {
                GachaDrawOutcome outcome = GachaDrawEngine.Draw(series, ref pity, worstLuck);
                Assert.That(outcome.Rarity, Is.EqualTo(GachaRarity.Standard),
                    $"Draw {draw} should stay Standard under worst luck.");
            }

            GachaDrawOutcome forced = GachaDrawEngine.Draw(series, ref pity, worstLuck);
            Assert.That(forced.Rarity, Is.EqualTo(GachaRarity.Signature));
            Assert.That(forced.ForcedBySignaturePity, Is.True);
            Assert.That(pity.SignatureMisses, Is.Zero);
        }

        [Test]
        public void SoftPityRampRaisesSignatureOddsBeforeTheGuarantee()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);

            double baseRate = GachaEconomyRules.EffectiveSignatureRate(series.Rates, 0);
            double preRamp = GachaEconomyRules.EffectiveSignatureRate(
                series.Rates, GachaEconomyRules.SignatureSoftPityStart - 1);
            Assert.That(preRamp, Is.EqualTo(baseRate).Within(1e-12),
                "No boost before the soft-pity start.");

            double previous = baseRate;
            for (int misses = GachaEconomyRules.SignatureSoftPityStart;
                misses < GachaEconomyRules.SignatureHardPity;
                misses++)
            {
                double effective = GachaEconomyRules.EffectiveSignatureRate(series.Rates, misses);
                Assert.That(effective, Is.GreaterThan(previous),
                    $"Ramp must be strictly monotonic at {misses} misses.");
                Assert.That(effective, Is.LessThan(1d));
                previous = effective;
            }

            Assert.That(
                GachaEconomyRules.EffectiveSignatureRate(
                    series.Rates, GachaEconomyRules.SignatureHardPity),
                Is.EqualTo(1d));

            // A mid roll that misses at base rates lands Signature mid-ramp.
            var pity = new GachaPityState { SignatureMisses = 45 };
            var midLuck = new ConstantRandom(0.5d);
            GachaDrawOutcome outcome = GachaDrawEngine.Draw(series, ref pity, midLuck);
            Assert.That(outcome.Rarity, Is.EqualTo(GachaRarity.Signature));
            Assert.That(outcome.ForcedBySignaturePity, Is.False,
                "Ramp wins are organic, not the hard guarantee.");
        }

        [Test]
        public void HeirloomHardPityForcesTheNinetiethDraw()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            var pity = new GachaPityState();
            var worstLuck = new ConstantRandom(0.9999d);
            GachaDrawOutcome outcome = default;
            for (int draw = 1; draw <= 90; draw++)
            {
                outcome = GachaDrawEngine.Draw(series, ref pity, worstLuck);
                if (draw < 90)
                {
                    Assert.That(outcome.Rarity, Is.Not.EqualTo(GachaRarity.Heirloom),
                        $"Draw {draw} must not reach Heirloom under worst luck.");
                }
            }

            Assert.That(outcome.Rarity, Is.EqualTo(GachaRarity.Heirloom));
            Assert.That(outcome.ForcedByHeirloomPity, Is.True);
            Assert.That(pity.HeirloomMisses, Is.Zero);
        }

        [Test]
        public void SignatureMissesAlsoResetOnHeirloom()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            var pity = new GachaPityState { SignatureMisses = 20, HeirloomMisses = 89 };
            GachaDrawOutcome outcome = GachaDrawEngine.Draw(
                series, ref pity, new ConstantRandom(0.9999d));
            Assert.That(outcome.Rarity, Is.EqualTo(GachaRarity.Heirloom));
            Assert.That(pity.SignatureMisses, Is.Zero,
                "The guarantee is Signature-or-better, so Heirloom clears it.");
        }

        [Test]
        public void TenDrawFloorsTheLastDrawAtRefinedWhenNineStayStandard()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            var pity = new GachaPityState();
            IReadOnlyList<GachaDrawOutcome> outcomes = GachaDrawEngine.DrawBatch(
                series, 10, ref pity, new ConstantRandom(0.9999d));
            for (int index = 0; index < 9; index++)
            {
                Assert.That(outcomes[index].Rarity, Is.EqualTo(GachaRarity.Standard));
            }

            Assert.That(outcomes[9].Rarity, Is.EqualTo(GachaRarity.Refined));
            Assert.That(outcomes[9].ForcedByTenDraw, Is.True);
        }

        [Test]
        public void TenDrawFloorStaysInactiveOnceAnyDrawReachesRefined()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            var pity = new GachaPityState();
            // First draw: rarity roll 0.2 lands Refined, prize roll 0.0;
            // every later roll is worst-luck Standard.
            var random = new QueueRandom(new[] { 0.2d, 0d }, 0.9999d);
            IReadOnlyList<GachaDrawOutcome> outcomes = GachaDrawEngine.DrawBatch(
                series, 10, ref pity, random);
            Assert.That(outcomes[0].Rarity, Is.EqualTo(GachaRarity.Refined));
            Assert.That(outcomes[9].Rarity, Is.EqualTo(GachaRarity.Standard));
            Assert.That(outcomes[9].ForcedByTenDraw, Is.False);
        }

        [Test]
        public void FixedSeedReplaysIdenticalOutcomeSequences()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            var first = new List<GachaDrawOutcome>();
            var second = new List<GachaDrawOutcome>();
            var pityA = new GachaPityState();
            var pityB = new GachaPityState();
            var randomA = new GachaSplitMix64(42UL);
            var randomB = new GachaSplitMix64(42UL);
            for (int index = 0; index < 200; index++)
            {
                first.Add(GachaDrawEngine.Draw(series, ref pityA, randomA));
                second.Add(GachaDrawEngine.Draw(series, ref pityB, randomB));
            }

            for (int index = 0; index < first.Count; index++)
            {
                Assert.That(second[index].PrizeId, Is.EqualTo(first[index].PrizeId));
                Assert.That(second[index].Rarity, Is.EqualTo(first[index].Rarity));
            }
        }
    }
}
