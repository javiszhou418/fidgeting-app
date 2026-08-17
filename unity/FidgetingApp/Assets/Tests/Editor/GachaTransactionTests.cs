using System;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaTransactionTests
    {
        private const string ProductionPrefix = "fidgeting.gacha.transaction-tests.production.";
        private const string InternalPrefix = "fidgeting.gacha.transaction-tests.internal.v2.";

        private sealed class CountingRandom : IGachaRandom
        {
            private readonly double value;

            public CountingRandom(double value = 0.9999d)
            {
                this.value = value;
            }

            public int Calls { get; private set; }

            public double NextDouble()
            {
                Calls += 1;
                return value;
            }
        }

        [TearDown]
        public void TearDown()
        {
            new GachaInventoryRuntime(ProductionPrefix).DeleteAllForTests();
            new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                InternalPrefix).DeleteAllForTests();
            PlayerPrefs.Save();
        }

        [Test]
        public void InternalUnlimitedUsesIsolatedV2NamespaceAndNeverConsumesTickets()
        {
            GachaInventoryRuntime formal = CleanProduction();
            formal.CreditTickets(3);

            var random = new CountingRandom();
            GachaInventoryRuntime internalRuntime = CleanInternal(random);
            Assert.That(
                GachaInventoryRuntime.InternalUnlimitedPrefix,
                Is.EqualTo("fidgeting.gacha.internal.v2."));
            Assert.That(internalRuntime.StoragePrefix, Is.EqualTo(InternalPrefix));
            Assert.That(internalRuntime.HasUnlimitedDraws, Is.True);
            Assert.That(internalRuntime.Tickets, Is.Zero);

            GachaTransactionResult prepared = internalRuntime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "internal-001");
            Assert.That(prepared.Success, Is.True);
            Assert.That(internalRuntime.Tickets, Is.Zero);
            Assert.That(internalRuntime.OwnedCount, Is.Zero,
                "Preparing must not write Gallery ownership.");
            Assert.That(internalRuntime.TotalDraws(GachaCatalog.LaunchSeriesId), Is.Zero);

            Assert.That(internalRuntime.MarkRevealAwaitingAcceptance("internal-001").Success);
            GachaTransactionResult accepted =
                internalRuntime.AcknowledgePending("internal-001");
            Assert.That(accepted.Success, Is.True);
            Assert.That(accepted.Transaction.Phase, Is.EqualTo(GachaTransactionPhase.Completed));
            Assert.That(internalRuntime.Tickets, Is.Zero,
                "Unlimited draws must never synthesize or deduct ticket balance.");
            Assert.That(internalRuntime.OwnedCount, Is.EqualTo(1));
            Assert.That(internalRuntime.TotalDraws(GachaCatalog.LaunchSeriesId), Is.EqualTo(1));

            var formalReload = new GachaInventoryRuntime(ProductionPrefix);
            Assert.That(formalReload.Tickets, Is.EqualTo(3));
            Assert.That(formalReload.OwnedCount, Is.Zero,
                "Internal v2 ownership must not contaminate production v1 data.");
        }

        [Test]
        public void ProductionZeroTicketPrepareFailsWithoutCreatingPendingState()
        {
            GachaInventoryRuntime runtime = CleanProduction();
            GachaTransactionResult result = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "production-empty");

            Assert.That(result.Success, Is.False);
            Assert.That(result.FailureReason, Is.EqualTo("insufficient-tickets"));
            Assert.That(runtime.PendingTransaction, Is.Null);
            Assert.That(runtime.OwnedCount, Is.Zero);
            Assert.That(runtime.TotalDraws(GachaCatalog.LaunchSeriesId), Is.Zero);
            StringAssert.Contains("runtime-mode\tproduction", runtime.SnapshotPayload());
            StringAssert.Contains("transaction\t\tidle", runtime.SnapshotPayload());
            StringAssert.Contains("result\tnone", runtime.SnapshotPayload());
        }

        [Test]
        public void SameRequestIsIdempotentAndDifferentRequestIsRejectedWhilePending()
        {
            var random = new CountingRandom();
            GachaInventoryRuntime runtime = CleanInternal(random);
            GachaTransactionResult first = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "repeatable-request");
            int callsAfterFirst = random.Calls;

            GachaTransactionResult retry = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "repeatable-request");
            Assert.That(retry.Success, Is.True);
            Assert.That(retry.Transaction.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(first.Transaction.Receipt.Rows[0].Outcome.PrizeId));
            Assert.That(random.Calls, Is.EqualTo(callsAfterFirst),
                "Idempotent retry must not consume random state or reroll.");

            GachaTransactionResult conflict = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "second-request");
            Assert.That(conflict.Success, Is.False);
            Assert.That(conflict.FailureReason, Is.EqualTo("transaction-in-flight"));
            Assert.That(runtime.PendingTransaction.RequestId,
                Is.EqualTo("repeatable-request"));

            GachaTransactionResult reusedWithDifferentArguments = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                10,
                GachaPaymentMethod.Ticket,
                "repeatable-request");
            Assert.That(reusedWithDifferentArguments.FailureReason,
                Is.EqualTo("request-id-conflict"));
        }

        [Test]
        public void PreparedTransactionAndAcceptancePhaseSurviveReloadWithoutEarlyCommit()
        {
            GachaInventoryRuntime first = CleanProduction(new CountingRandom());
            first.CreditTickets(1);
            GachaTransactionResult prepared = first.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "reload-pending");
            Assert.That(prepared.Success);
            Assert.That(first.Tickets, Is.EqualTo(1));
            Assert.That(first.OwnedCount, Is.Zero);
            Assert.That(first.Pity(GachaCatalog.LaunchSeriesId).SignatureMisses, Is.Zero);

            var restoredPrepared = new GachaInventoryRuntime(ProductionPrefix);
            Assert.That(restoredPrepared.PendingTransaction, Is.Not.Null);
            Assert.That(restoredPrepared.PendingTransaction.RequestId,
                Is.EqualTo("reload-pending"));
            Assert.That(restoredPrepared.PendingTransaction.Phase,
                Is.EqualTo(GachaTransactionPhase.Prepared));
            Assert.That(restoredPrepared.Tickets, Is.EqualTo(1));
            Assert.That(restoredPrepared.OwnedCount, Is.Zero);

            GachaTransactionResult awaiting =
                restoredPrepared.MarkRevealAwaitingAcceptance("reload-pending");
            Assert.That(awaiting.Transaction.Phase,
                Is.EqualTo(GachaTransactionPhase.AwaitingAcceptance));
            var restoredAwaiting = new GachaInventoryRuntime(ProductionPrefix);
            Assert.That(restoredAwaiting.PendingTransaction.Phase,
                Is.EqualTo(GachaTransactionPhase.AwaitingAcceptance));
            Assert.That(restoredAwaiting.AcknowledgePending("reload-pending").Success);
            Assert.That(restoredAwaiting.Tickets, Is.Zero);
            Assert.That(restoredAwaiting.OwnedCount, Is.EqualTo(1));
            Assert.That(restoredAwaiting.TotalDraws(GachaCatalog.LaunchSeriesId), Is.EqualTo(1));
        }

        [Test]
        public void AcknowledgeRequiresRevealAndRepeatedAckNeverDoubleCommits()
        {
            GachaInventoryRuntime runtime = CleanInternal(new CountingRandom());
            GachaTransactionResult prepared = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "ack-once");
            string prizeId = prepared.Transaction.Receipt.Rows[0].Outcome.PrizeId;

            GachaTransactionResult tooSoon = runtime.AcknowledgePending("ack-once");
            Assert.That(tooSoon.Success, Is.False);
            Assert.That(tooSoon.FailureReason, Is.EqualTo("reveal-not-ready"));
            Assert.That(runtime.Owns(prizeId), Is.False);

            runtime.MarkRevealAwaitingAcceptance("ack-once");
            GachaTransactionResult firstAck = runtime.AcknowledgePending("ack-once");
            Assert.That(firstAck.Success);
            int draws = runtime.TotalDraws(GachaCatalog.LaunchSeriesId);
            int shards = runtime.Shards(GachaCatalog.LaunchSeriesId);

            GachaTransactionResult repeatedAck = runtime.AcknowledgePending("ack-once");
            Assert.That(repeatedAck.Success, Is.True);
            Assert.That(repeatedAck.Transaction.Phase,
                Is.EqualTo(GachaTransactionPhase.Completed));
            Assert.That(runtime.TotalDraws(GachaCatalog.LaunchSeriesId), Is.EqualTo(draws));
            Assert.That(runtime.Shards(GachaCatalog.LaunchSeriesId), Is.EqualTo(shards));

            var reloaded = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                InternalPrefix);
            GachaTransactionResult retryAfterRestart =
                reloaded.AcknowledgePending("ack-once");
            Assert.That(retryAfterRestart.Success, Is.True);
            Assert.That(reloaded.TotalDraws(GachaCatalog.LaunchSeriesId), Is.EqualTo(draws));
            Assert.That(reloaded.Shards(GachaCatalog.LaunchSeriesId), Is.EqualTo(shards));
        }

        [Test]
        public void SnapshotAndTransactionReceiptExposeModeRequestPhaseAndPendingPrize()
        {
            GachaInventoryRuntime runtime = CleanInternal(new CountingRandom());
            GachaTransactionResult prepared = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "snapshot-request");
            string prizeId = prepared.Transaction.Receipt.Rows[0].Outcome.PrizeId;

            string snapshot = runtime.SnapshotPayload();
            StringAssert.Contains("runtime-mode\tinternalUnlimited", snapshot);
            StringAssert.Contains(
                "transaction\tsnapshot-request\tprepared\tcanyon-lode\t1\tticket",
                snapshot);
            StringAssert.Contains("result\tok", snapshot);
            StringAssert.Contains("row\t" + prizeId + "\t", snapshot);

            string receipt = GachaNativeBridge.ReceiptPayload(prepared);
            StringAssert.StartsWith("runtime-mode\tinternalUnlimited\n", receipt);
            StringAssert.Contains(
                "transaction\tsnapshot-request\tprepared\tcanyon-lode\t1\tticket",
                receipt);
            StringAssert.Contains("result\tok", receipt);
            StringAssert.Contains("row\t" + prizeId + "\t", receipt);
        }

        [Test]
        public void CompletedRequestReplayReturnsOriginalReceiptWithoutRerolling()
        {
            var random = new CountingRandom();
            GachaInventoryRuntime runtime = CleanInternal(random);
            GachaTransactionResult original = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "completed-replay");
            runtime.MarkRevealAwaitingAcceptance("completed-replay");
            runtime.AcknowledgePending("completed-replay");
            int callsAfterCommit = random.Calls;

            GachaTransactionResult replay = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "completed-replay");
            Assert.That(replay.Success, Is.True);
            Assert.That(replay.Transaction.Phase, Is.EqualTo(GachaTransactionPhase.Completed));
            Assert.That(replay.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo(original.Receipt.Rows[0].Outcome.PrizeId));
            Assert.That(random.Calls, Is.EqualTo(callsAfterCommit));
            Assert.That(runtime.TotalDraws(GachaCatalog.LaunchSeriesId), Is.EqualTo(1));
        }

        [Test]
        public void DuplicateShardAndPityChangesWaitForAckAndCommitExactlyOnce()
        {
            GachaInventoryRuntime runtime = CleanInternal(new CountingRandom());
            runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "first-copy");
            runtime.MarkRevealAwaitingAcceptance("first-copy");
            runtime.AcknowledgePending("first-copy");

            GachaTransactionResult duplicate = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "duplicate-copy");
            Assert.That(duplicate.Receipt.Rows[0].IsNew, Is.False);
            int plannedShards = duplicate.Receipt.Rows[0].ShardsGained;
            Assert.That(plannedShards, Is.GreaterThan(0));
            Assert.That(runtime.Shards(GachaCatalog.LaunchSeriesId), Is.Zero,
                "Projected duplicate shards must not land during prepare.");
            Assert.That(runtime.TotalDraws(GachaCatalog.LaunchSeriesId), Is.EqualTo(1));

            runtime.MarkRevealAwaitingAcceptance("duplicate-copy");
            runtime.AcknowledgePending("duplicate-copy");
            Assert.That(runtime.Shards(GachaCatalog.LaunchSeriesId),
                Is.EqualTo(plannedShards));
            Assert.That(runtime.TotalDraws(GachaCatalog.LaunchSeriesId), Is.EqualTo(2));
            Assert.That(runtime.Pity(GachaCatalog.LaunchSeriesId).SignatureMisses,
                Is.EqualTo(2));

            runtime.AcknowledgePending("duplicate-copy");
            Assert.That(runtime.Shards(GachaCatalog.LaunchSeriesId),
                Is.EqualTo(plannedShards));
            Assert.That(runtime.TotalDraws(GachaCatalog.LaunchSeriesId), Is.EqualTo(2));
        }

        [Test]
        public void CompletedLedgerReplaysAAfterBAndReloadWithoutRerollOrDoubleCommit()
        {
            var originalRandom = new CountingRandom();
            GachaInventoryRuntime runtime = CleanInternal(originalRandom);
            GachaTransactionResult preparedA = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "ledger-request-a");
            runtime.MarkRevealAwaitingAcceptance("ledger-request-a");
            GachaTransactionResult completedA =
                runtime.AcknowledgePending("ledger-request-a");

            runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "ledger-request-b");
            runtime.MarkRevealAwaitingAcceptance("ledger-request-b");
            runtime.AcknowledgePending("ledger-request-b");
            int callsAfterB = originalRandom.Calls;
            int drawsAfterB = runtime.TotalDraws(GachaCatalog.LaunchSeriesId);
            int shardsAfterB = runtime.Shards(GachaCatalog.LaunchSeriesId);

            GachaTransactionResult retryABeforeReload = runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "ledger-request-a");
            AssertSameReceipt(completedA.Receipt, retryABeforeReload.Receipt);
            Assert.That(retryABeforeReload.Transaction.Phase,
                Is.EqualTo(GachaTransactionPhase.Completed));
            Assert.That(originalRandom.Calls, Is.EqualTo(callsAfterB));
            Assert.That(runtime.TotalDraws(GachaCatalog.LaunchSeriesId),
                Is.EqualTo(drawsAfterB));
            Assert.That(runtime.Shards(GachaCatalog.LaunchSeriesId),
                Is.EqualTo(shardsAfterB));

            var restartRandom = new CountingRandom(0.005d);
            var reloaded = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                InternalPrefix,
                restartRandom);
            GachaTransactionResult queriedA =
                reloaded.QueryTransaction("ledger-request-a");
            Assert.That(queriedA.Success, Is.True);
            AssertSameReceipt(preparedA.Receipt, queriedA.Receipt);

            GachaTransactionResult retryAAfterReload = reloaded.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "ledger-request-a");
            AssertSameReceipt(completedA.Receipt, retryAAfterReload.Receipt);
            Assert.That(restartRandom.Calls, Is.Zero,
                "Historical request retries after restart must not reroll.");
            Assert.That(reloaded.AcknowledgePending("ledger-request-a").Success, Is.True);
            Assert.That(reloaded.TotalDraws(GachaCatalog.LaunchSeriesId),
                Is.EqualTo(drawsAfterB));
            Assert.That(reloaded.Shards(GachaCatalog.LaunchSeriesId),
                Is.EqualTo(shardsAfterB));
        }

        [Test]
        public void LegacyLatestCompletedKeyMigratesIntoDurableLedger()
        {
            GachaInventoryRuntime runtime = CleanInternal(new CountingRandom());
            runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "legacy-latest");
            runtime.MarkRevealAwaitingAcceptance("legacy-latest");
            GachaTransactionResult completed =
                runtime.AcknowledgePending("legacy-latest");

            PlayerPrefs.DeleteKey(InternalPrefix + "transaction.completedLedger");
            PlayerPrefs.Save();
            var migrated = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                InternalPrefix);
            GachaTransactionResult restored = migrated.QueryTransaction("legacy-latest");
            Assert.That(restored.Success, Is.True);
            AssertSameReceipt(completed.Receipt, restored.Receipt);
            Assert.That(
                PlayerPrefs.GetString(
                    InternalPrefix + "transaction.completedLedger",
                    string.Empty),
                Is.Not.Empty,
                "Loading the legacy latest key must durably write the ledger migration.");
        }

        [Test]
        public void MixedGoodAndCorruptLedgerEntriesSalvageGoodAndTombstoneBadId()
        {
            GachaInventoryRuntime runtime = CleanInternal(new CountingRandom());
            GachaTransactionResult completedA = Complete(runtime, "salvage-a");
            GachaTransactionResult completedB = Complete(runtime, "salvage-b");
            int drawsBeforeCorruption = runtime.TotalDraws(GachaCatalog.LaunchSeriesId);
            string ledgerKey = InternalPrefix + "transaction.completedLedger";
            string ledger = PlayerPrefs.GetString(ledgerKey, string.Empty);
            string corrupted = CorruptLedgerEntryPayload(ledger, "salvage-a");
            Assert.That(corrupted, Is.Not.EqualTo(ledger));
            PlayerPrefs.SetString(ledgerKey, corrupted);
            PlayerPrefs.Save();

            var restored = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                InternalPrefix,
                new CountingRandom(0.005d));
            GachaTransactionResult good = restored.QueryTransaction("salvage-b");
            Assert.That(good.Success, Is.True);
            AssertSameReceipt(completedB.Receipt, good.Receipt);

            GachaTransactionResult bad = restored.QueryTransaction("salvage-a");
            Assert.That(bad.Success, Is.False);
            Assert.That(bad.FailureReason,
                Is.EqualTo("completed-receipt-unavailable"));
            GachaTransactionResult noReroll = restored.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "salvage-a");
            Assert.That(noReroll.Success, Is.False);
            Assert.That(noReroll.FailureReason,
                Is.EqualTo("completed-receipt-unavailable"));
            Assert.That(restored.TotalDraws(GachaCatalog.LaunchSeriesId),
                Is.EqualTo(drawsBeforeCorruption));

            var secondReload = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                InternalPrefix);
            AssertSameReceipt(
                completedB.Receipt,
                secondReload.QueryTransaction("salvage-b").Receipt);
            Assert.That(secondReload.QueryTransaction("salvage-a").FailureReason,
                Is.EqualTo("completed-receipt-unavailable"),
                "Independent request-id tombstone must survive ledger rewrite/reload.");
            Assert.That(completedA.Success, Is.True);
        }

        [Test]
        public void CompletedReceiptSurvivesOldSchemaAndHistoricalCostValues()
        {
            GachaInventoryRuntime runtime = CleanInternal(new CountingRandom());
            GachaTransactionResult completed = Complete(runtime, "old-schema-cost");
            string ledgerKey = InternalPrefix + "transaction.completedLedger";
            string ledger = PlayerPrefs.GetString(ledgerKey, string.Empty);
            string historical = ledger
                .Replace("\\\"schemaVersion\\\":2", "\\\"schemaVersion\\\":0")
                .Replace("\\\"ticketCost\\\":1", "\\\"ticketCost\\\":77");
            Assert.That(historical, Is.Not.EqualTo(ledger));
            PlayerPrefs.SetString(ledgerKey, historical);
            PlayerPrefs.Save();

            var restored = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                InternalPrefix);
            GachaTransactionResult replay =
                restored.QueryTransaction("old-schema-cost");
            Assert.That(replay.Success, Is.True);
            AssertSameReceipt(completed.Receipt, replay.Receipt);
            Assert.That(restored.TotalDraws(GachaCatalog.LaunchSeriesId), Is.EqualTo(1));
        }

        private static GachaTransactionResult Complete(
            GachaInventoryRuntime runtime,
            string requestId)
        {
            runtime.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                requestId);
            runtime.MarkRevealAwaitingAcceptance(requestId);
            return runtime.AcknowledgePending(requestId);
        }

        private static string CorruptLedgerEntryPayload(
            string ledger,
            string requestId)
        {
            string marker = "\"requestId\":\"" + requestId
                + "\",\"transaction\":\"";
            int markerIndex = ledger.IndexOf(marker, StringComparison.Ordinal);
            Assert.That(markerIndex, Is.GreaterThanOrEqualTo(0));
            int payloadIndex = markerIndex + marker.Length;
            Assert.That(payloadIndex, Is.LessThan(ledger.Length));
            return ledger.Substring(0, payloadIndex)
                + "!"
                + ledger.Substring(payloadIndex + 1);
        }

        private static void AssertSameReceipt(
            GachaDrawReceipt expected,
            GachaDrawReceipt actual)
        {
            Assert.That(actual.Success, Is.EqualTo(expected.Success));
            Assert.That(actual.FailureReason, Is.EqualTo(expected.FailureReason));
            Assert.That(actual.Rows.Count, Is.EqualTo(expected.Rows.Count));
            for (int index = 0; index < expected.Rows.Count; index++)
            {
                GachaDrawReceiptRow expectedRow = expected.Rows[index];
                GachaDrawReceiptRow actualRow = actual.Rows[index];
                Assert.That(actualRow.Outcome.PrizeId,
                    Is.EqualTo(expectedRow.Outcome.PrizeId));
                Assert.That(actualRow.Outcome.Rarity,
                    Is.EqualTo(expectedRow.Outcome.Rarity));
                Assert.That(actualRow.IsNew, Is.EqualTo(expectedRow.IsNew));
                Assert.That(actualRow.ShardsGained,
                    Is.EqualTo(expectedRow.ShardsGained));
                Assert.That(actualRow.Outcome.ForcedBySignaturePity,
                    Is.EqualTo(expectedRow.Outcome.ForcedBySignaturePity));
                Assert.That(actualRow.Outcome.ForcedByHeirloomPity,
                    Is.EqualTo(expectedRow.Outcome.ForcedByHeirloomPity));
                Assert.That(actualRow.Outcome.ForcedByTenDraw,
                    Is.EqualTo(expectedRow.Outcome.ForcedByTenDraw));
            }
        }

        private static GachaInventoryRuntime CleanProduction(IGachaRandom random = null)
        {
            var runtime = new GachaInventoryRuntime(ProductionPrefix, random);
            runtime.DeleteAllForTests();
            return new GachaInventoryRuntime(ProductionPrefix, random);
        }

        private static GachaInventoryRuntime CleanInternal(IGachaRandom random = null)
        {
            var runtime = new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                InternalPrefix,
                random);
            runtime.DeleteAllForTests();
            return new GachaInventoryRuntime(
                GachaRuntimeMode.InternalUnlimited,
                InternalPrefix,
                random);
        }
    }
}
