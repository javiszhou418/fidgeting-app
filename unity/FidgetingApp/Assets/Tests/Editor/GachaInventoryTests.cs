using System.Collections.Generic;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaInventoryTests
    {
        private const string TestPrefix = "fidgeting.gacha.tests.";

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

        private static GachaInventoryRuntime CreateClean(IGachaRandom random = null)
        {
            var runtime = new GachaInventoryRuntime(TestPrefix, random);
            runtime.DeleteAllForTests();
            return new GachaInventoryRuntime(TestPrefix, random);
        }

        private static void Cleanup()
        {
            new GachaInventoryRuntime(TestPrefix).DeleteAllForTests();
        }

        [Test]
        public void DrawRejectsInsufficientFundsAndUnknownSeries()
        {
            try
            {
                GachaInventoryRuntime inventory = CreateClean();
                GachaDrawReceipt broke = inventory.Draw(
                    GachaCatalog.LaunchSeriesId, 1, GachaPaymentMethod.Ticket);
                Assert.That(broke.Success, Is.False);
                Assert.That(broke.FailureReason, Is.EqualTo("insufficient-tickets"));

                inventory.CreditTickets(5);
                GachaDrawReceipt unknown = inventory.Draw(
                    "missing-series", 1, GachaPaymentMethod.Ticket);
                Assert.That(unknown.FailureReason, Is.EqualTo("unknown-series"));
                Assert.That(inventory.Tickets, Is.EqualTo(5),
                    "A failed draw must not consume funds.");

                GachaDrawReceipt oddCount = inventory.Draw(
                    GachaCatalog.LaunchSeriesId, 3, GachaPaymentMethod.Ticket);
                Assert.That(oddCount.FailureReason, Is.EqualTo("unsupported-count"));
            }
            finally
            {
                Cleanup();
            }
        }

        [Test]
        public void TicketAndCoinCostsFollowTheEconomyRules()
        {
            try
            {
                GachaInventoryRuntime inventory = CreateClean(new GachaSplitMix64(7UL));
                inventory.CreditTickets(11);
                inventory.CreditCoins(GachaEconomyRules.TenDrawCoinCost
                    + GachaEconomyRules.SingleDrawCoinCost);

                Assert.That(inventory.Draw(
                    GachaCatalog.LaunchSeriesId, 1, GachaPaymentMethod.Ticket).Success);
                Assert.That(inventory.Tickets, Is.EqualTo(10));

                Assert.That(inventory.Draw(
                    GachaCatalog.LaunchSeriesId, 10, GachaPaymentMethod.Ticket).Success);
                Assert.That(inventory.Tickets, Is.Zero);

                Assert.That(inventory.Draw(
                    GachaCatalog.LaunchSeriesId, 10, GachaPaymentMethod.Coin).Success);
                Assert.That(inventory.Coins,
                    Is.EqualTo(GachaEconomyRules.SingleDrawCoinCost));

                Assert.That(inventory.TotalDraws(GachaCatalog.LaunchSeriesId),
                    Is.EqualTo(21));
            }
            finally
            {
                Cleanup();
            }
        }

        [Test]
        public void DuplicatesConvertToShardsExactlyOnceEach()
        {
            try
            {
                // Worst-luck constant rolls always land the same Standard
                // prize, so draw 1 is new and every later draw is a duplicate.
                GachaInventoryRuntime inventory = CreateClean(new ConstantRandom(0.9999d));
                inventory.CreditTickets(40);
                int expectedShards = 0;
                int newCount = 0;
                for (int index = 0; index < 40; index++)
                {
                    GachaDrawReceipt receipt = inventory.Draw(
                        GachaCatalog.LaunchSeriesId, 1, GachaPaymentMethod.Ticket);
                    Assert.That(receipt.Success, Is.True);
                    GachaDrawReceiptRow row = receipt.Rows[0];
                    if (row.IsNew)
                    {
                        newCount += 1;
                        Assert.That(row.ShardsGained, Is.Zero);
                    }
                    else
                    {
                        expectedShards += GachaEconomyRules.DuplicateShardValue(
                            row.Outcome.Rarity);
                        Assert.That(row.ShardsGained, Is.GreaterThan(0));
                    }
                }

                Assert.That(newCount, Is.EqualTo(1));
                Assert.That(inventory.OwnedCount, Is.EqualTo(1));
                Assert.That(inventory.Shards(GachaCatalog.LaunchSeriesId),
                    Is.EqualTo(expectedShards),
                    "Shard balance must equal the sum of every duplicate's value.");
            }
            finally
            {
                Cleanup();
            }
        }

        [Test]
        public void RedeemEnforcesCatalogOwnershipAndBalanceRules()
        {
            try
            {
                GachaInventoryRuntime inventory = CreateClean(new ConstantRandom(0.9999d));
                inventory.CreditTickets(40);
                for (int index = 0; index < 40; index++)
                {
                    inventory.Draw(GachaCatalog.LaunchSeriesId, 1, GachaPaymentMethod.Ticket);
                }

                int shards = inventory.Shards(GachaCatalog.LaunchSeriesId);
                Assert.That(shards,
                    Is.GreaterThanOrEqualTo(GachaEconomyRules.RedeemShardCost(
                        GachaRarity.Standard)));

                Assert.That(inventory.TryRedeemShards("missing-prize", out string reason),
                    Is.False);
                Assert.That(reason, Is.EqualTo("unknown-prize"));

                Assert.That(inventory.TryRedeemShards(
                    "canyon-heir-metal-three-blade",
                    out reason),
                    Is.False);
                Assert.That(reason, Is.EqualTo("not-redeemable"),
                    "Heirloom prizes must never be purchasable with shards.");

                string ownedId = null;
                string unownedStandardId = null;
                foreach (GachaPrizeDefinition prize in GachaCatalog
                    .ResolveSeries(GachaCatalog.LaunchSeriesId)
                    .PrizesOfRarity(GachaRarity.Standard))
                {
                    if (inventory.Owns(prize.Id))
                    {
                        ownedId = prize.Id;
                    }
                    else
                    {
                        unownedStandardId = prize.Id;
                    }
                }

                Assert.That(ownedId, Is.Not.Null);
                Assert.That(unownedStandardId, Is.Not.Null);

                Assert.That(inventory.TryRedeemShards(ownedId, out reason), Is.False);
                Assert.That(reason, Is.EqualTo("already-owned"));

                Assert.That(inventory.TryRedeemShards(unownedStandardId, out reason), Is.True);
                Assert.That(inventory.Owns(unownedStandardId), Is.True);
                Assert.That(inventory.Shards(GachaCatalog.LaunchSeriesId),
                    Is.EqualTo(shards - GachaEconomyRules.RedeemShardCost(
                        GachaRarity.Standard)));

                GachaInventoryRuntime drained = CreateClean();
                Assert.That(drained.TryRedeemShards(unownedStandardId, out reason), Is.False);
                Assert.That(reason, Is.EqualTo("insufficient-shards"));
            }
            finally
            {
                Cleanup();
            }
        }

        [Test]
        public void StateSurvivesAReloadUnderTheSamePrefix()
        {
            try
            {
                GachaInventoryRuntime first = CreateClean(new GachaSplitMix64(99UL));
                first.CreditTickets(12);
                first.CreditCoins(500);
                GachaDrawReceipt receipt = first.Draw(
                    GachaCatalog.LaunchSeriesId, 10, GachaPaymentMethod.Ticket);
                Assert.That(receipt.Success, Is.True);

                var reloaded = new GachaInventoryRuntime(TestPrefix);
                Assert.That(reloaded.Tickets, Is.EqualTo(first.Tickets));
                Assert.That(reloaded.Coins, Is.EqualTo(first.Coins));
                Assert.That(reloaded.OwnedCount, Is.EqualTo(first.OwnedCount));
                Assert.That(reloaded.Shards(GachaCatalog.LaunchSeriesId),
                    Is.EqualTo(first.Shards(GachaCatalog.LaunchSeriesId)));
                Assert.That(reloaded.TotalDraws(GachaCatalog.LaunchSeriesId),
                    Is.EqualTo(10));
                GachaPityState expectedPity = first.Pity(GachaCatalog.LaunchSeriesId);
                GachaPityState actualPity = reloaded.Pity(GachaCatalog.LaunchSeriesId);
                Assert.That(actualPity.SignatureMisses,
                    Is.EqualTo(expectedPity.SignatureMisses));
                Assert.That(actualPity.HeirloomMisses,
                    Is.EqualTo(expectedPity.HeirloomMisses));
                Assert.That(reloaded.SnapshotPayload(),
                    Is.EqualTo(first.SnapshotPayload()));
            }
            finally
            {
                Cleanup();
            }
        }

        [Test]
        public void RhythmTicketsGrantOncePerCompletedWeekAndSurviveReload()
        {
            try
            {
                GachaInventoryRuntime inventory = CreateClean();
                Assert.That(inventory.SyncRhythmTickets(0), Is.Zero);
                Assert.That(inventory.SyncRhythmTickets(2), Is.EqualTo(2));
                Assert.That(inventory.Tickets, Is.EqualTo(2));
                Assert.That(inventory.SyncRhythmTickets(2), Is.Zero,
                    "Republishing the same week count must not double-grant.");
                Assert.That(inventory.SyncRhythmTickets(1), Is.Zero,
                    "A lower count must never rewind the credited counter.");
                Assert.That(inventory.SyncRhythmTickets(3), Is.EqualTo(1));

                var reloaded = new GachaInventoryRuntime(TestPrefix);
                Assert.That(reloaded.RhythmWeeksCredited, Is.EqualTo(3));
                Assert.That(reloaded.Tickets, Is.EqualTo(3));
                Assert.That(reloaded.SyncRhythmTickets(3), Is.Zero);
            }
            finally
            {
                Cleanup();
            }
        }

        [Test]
        public void SnapshotPayloadListsWalletSeriesStateAndOwnedPrizes()
        {
            try
            {
                GachaInventoryRuntime inventory = CreateClean(new ConstantRandom(0.9999d));
                inventory.CreditTickets(2);
                inventory.CreditCoins(300);
                inventory.Draw(GachaCatalog.LaunchSeriesId, 1, GachaPaymentMethod.Ticket);

                string payload = inventory.SnapshotPayload();
                var lines = new List<string>(payload.Split('\n'));
                Assert.That(lines[0], Is.EqualTo("wallet\t1\t300"));
                StringAssert.StartsWith("series-state\tcanyon-lode\t1\t1\t0\t1", lines[1]);
                StringAssert.StartsWith("owned\t", lines[lines.Count - 1]);
                StringAssert.Contains("canyon-std-", lines[lines.Count - 1]);
            }
            finally
            {
                Cleanup();
            }
        }
    }
}
