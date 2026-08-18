using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Production keeps the shipped v1 economy. InternalUnlimited is an
    /// isolated, ticket-free validation economy used only by internal builds.
    /// </summary>
    public enum GachaRuntimeMode
    {
        Production = 0,
        InternalUnlimited = 1
    }

    public enum GachaTransactionPhase
    {
        Prepared = 0,
        AwaitingAcceptance = 1,
        Completed = 2
    }

    /// <summary>
    /// Durable draw intent. Preparing a transaction fixes its outcome without
    /// touching wallet, pity, Gallery, shards, or draw counts. Acknowledging it
    /// commits all of those changes together.
    /// </summary>
    public sealed class GachaPendingTransaction
    {
        internal GachaPendingTransaction(
            string requestId,
            string seriesId,
            int count,
            GachaPaymentMethod paymentMethod,
            GachaRuntimeMode runtimeMode,
            GachaTransactionPhase phase,
            GachaPityState pityAfter,
            int ticketCost,
            int coinCost,
            IReadOnlyList<GachaDrawReceiptRow> rows)
        {
            RequestId = requestId ?? string.Empty;
            SeriesId = seriesId ?? string.Empty;
            Count = count;
            PaymentMethod = paymentMethod;
            RuntimeMode = runtimeMode;
            Phase = phase;
            PityAfter = pityAfter;
            TicketCost = Math.Max(0, ticketCost);
            CoinCost = Math.Max(0, coinCost);
            Receipt = new GachaDrawReceipt(true, string.Empty, rows);
        }

        public string RequestId { get; }
        public string SeriesId { get; }
        public int Count { get; }
        public GachaPaymentMethod PaymentMethod { get; }
        public GachaRuntimeMode RuntimeMode { get; }
        public GachaTransactionPhase Phase { get; }
        public GachaDrawReceipt Receipt { get; }

        internal GachaPityState PityAfter { get; }
        internal int TicketCost { get; }
        internal int CoinCost { get; }

        internal bool Matches(
            string seriesId,
            int count,
            GachaPaymentMethod paymentMethod)
        {
            return string.Equals(SeriesId, seriesId, StringComparison.Ordinal)
                && Count == count
                && PaymentMethod == paymentMethod;
        }

        internal GachaPendingTransaction WithPhase(GachaTransactionPhase phase)
        {
            return new GachaPendingTransaction(
                RequestId,
                SeriesId,
                Count,
                PaymentMethod,
                RuntimeMode,
                phase,
                PityAfter,
                TicketCost,
                CoinCost,
                Receipt.Rows);
        }
    }

    /// <summary>
    /// Result returned for prepare, query, reveal-ready, and acknowledgement.
    /// Successful retries return the original durable transaction and receipt.
    /// </summary>
    public readonly struct GachaTransactionResult
    {
        private GachaTransactionResult(
            GachaRuntimeMode runtimeMode,
            string requestId,
            bool success,
            string failureReason,
            GachaPendingTransaction transaction)
        {
            RuntimeMode = runtimeMode;
            RequestId = requestId ?? string.Empty;
            Success = success;
            FailureReason = failureReason ?? string.Empty;
            Transaction = transaction;
        }

        public GachaRuntimeMode RuntimeMode { get; }
        public string RequestId { get; }
        public bool Success { get; }
        public string FailureReason { get; }
        public GachaPendingTransaction Transaction { get; }
        public GachaDrawReceipt Receipt => Success && Transaction != null
            ? Transaction.Receipt
            : GachaDrawReceipt.Failure(FailureReason);

        internal static GachaTransactionResult Succeeded(
            GachaRuntimeMode runtimeMode,
            GachaPendingTransaction transaction)
        {
            if (transaction == null)
            {
                throw new ArgumentNullException(nameof(transaction));
            }

            return new GachaTransactionResult(
                runtimeMode,
                transaction.RequestId,
                true,
                string.Empty,
                transaction);
        }

        internal static GachaTransactionResult Failed(
            GachaRuntimeMode runtimeMode,
            string requestId,
            string reason)
        {
            return new GachaTransactionResult(
                runtimeMode,
                requestId,
                false,
                reason,
                null);
        }
    }

    /// <summary>
    /// JsonUtility DTO codec kept separate from the public immutable contract.
    /// Only stable primitive fields are persisted, so a pending reveal can be
    /// restored after process termination without rerolling random state.
    /// </summary>
    internal static class GachaTransactionCodec
    {
        private const int CurrentTransactionSchemaVersion = 3;
        private const int CurrentLedgerSchemaVersion = 2;

        [Serializable]
        private sealed class StoredTransaction
        {
            public int schemaVersion;
            public string requestId;
            public string seriesId;
            public int count;
            public int paymentMethod;
            public int runtimeMode;
            public int phase;
            public int signatureMissesAfter;
            public int heirloomMissesAfter;
            public int ticketCost;
            public int coinCost;
            public List<StoredRow> rows = new List<StoredRow>();
        }

        [Serializable]
        private sealed class StoredRow
        {
            public string prizeId;
            public int rarity;
            public bool forcedBySignaturePity;
            public bool forcedByHeirloomPity;
            public bool forcedByTenDraw;
            public bool isNew;
            public int shardsGained;

            // Absent on schema 2 rows; deserializes to null and is treated
            // as an unknown acquisition date.
            public string firstObtainedAtUtc;
        }

        [Serializable]
        private sealed class StoredCompletedLedgerEntry
        {
            public int schemaVersion;
            public string requestId;
            public string transaction;
        }

        [Serializable]
        private sealed class StoredCompletedLedger
        {
            public int schemaVersion;
            public List<StoredCompletedLedgerEntry> entries =
                new List<StoredCompletedLedgerEntry>();

            // Build 42 pre-ledger-hardening compatibility.
            public List<string> transactions = new List<string>();
        }

        public static string Serialize(GachaPendingTransaction transaction)
        {
            if (transaction == null)
            {
                return string.Empty;
            }

            var stored = new StoredTransaction
            {
                schemaVersion = CurrentTransactionSchemaVersion,
                requestId = transaction.RequestId,
                seriesId = transaction.SeriesId,
                count = transaction.Count,
                paymentMethod = (int)transaction.PaymentMethod,
                runtimeMode = (int)transaction.RuntimeMode,
                phase = (int)transaction.Phase,
                signatureMissesAfter = transaction.PityAfter.SignatureMisses,
                heirloomMissesAfter = transaction.PityAfter.HeirloomMisses,
                ticketCost = transaction.TicketCost,
                coinCost = transaction.CoinCost
            };
            for (int index = 0; index < transaction.Receipt.Rows.Count; index++)
            {
                GachaDrawReceiptRow row = transaction.Receipt.Rows[index];
                stored.rows.Add(new StoredRow
                {
                    prizeId = row.Outcome.PrizeId,
                    rarity = (int)row.Outcome.Rarity,
                    forcedBySignaturePity = row.Outcome.ForcedBySignaturePity,
                    forcedByHeirloomPity = row.Outcome.ForcedByHeirloomPity,
                    forcedByTenDraw = row.Outcome.ForcedByTenDraw,
                    isNew = row.IsNew,
                    shardsGained = row.ShardsGained,
                    firstObtainedAtUtc = row.FirstObtainedAtUtc
                });
            }

            return JsonUtility.ToJson(stored);
        }

        public static string SerializeCompletedLedger(
            IEnumerable<GachaPendingTransaction> transactions)
        {
            var ordered = new List<GachaPendingTransaction>();
            if (transactions != null)
            {
                foreach (GachaPendingTransaction transaction in transactions)
                {
                    if (transaction != null
                        && transaction.Phase == GachaTransactionPhase.Completed)
                    {
                        ordered.Add(transaction);
                    }
                }
            }

            ordered.Sort((left, right) => string.Compare(
                left.RequestId,
                right.RequestId,
                StringComparison.Ordinal));
            var ledger = new StoredCompletedLedger
            {
                schemaVersion = CurrentLedgerSchemaVersion
            };
            for (int index = 0; index < ordered.Count; index++)
            {
                ledger.entries.Add(new StoredCompletedLedgerEntry
                {
                    schemaVersion = CurrentLedgerSchemaVersion,
                    requestId = ordered[index].RequestId,
                    transaction = Serialize(ordered[index])
                });
            }

            return JsonUtility.ToJson(ledger);
        }

        public static bool TryDeserializeCompletedLedger(
            string payload,
            GachaRuntimeMode expectedMode,
            out List<GachaPendingTransaction> transactions,
            out HashSet<string> knownRequestIds,
            out bool requiresRewrite)
        {
            transactions = new List<GachaPendingTransaction>();
            knownRequestIds = new HashSet<string>(StringComparer.Ordinal);
            requiresRewrite = false;
            if (string.IsNullOrEmpty(payload))
            {
                return false;
            }

            StoredCompletedLedger ledger;
            try
            {
                ledger = JsonUtility.FromJson<StoredCompletedLedger>(payload);
            }
            catch (Exception)
            {
                return false;
            }

            if (ledger == null)
            {
                return false;
            }

            if (ledger.transactions == null)
            {
                ledger.transactions = new List<string>();
            }

            var restoredByRequestId =
                new Dictionary<string, GachaPendingTransaction>(StringComparer.Ordinal);
            if (ledger.entries != null)
            {
                for (int index = 0; index < ledger.entries.Count; index++)
                {
                    StoredCompletedLedgerEntry entry = ledger.entries[index];
                    if (entry == null || !IsRequestIdValid(entry.requestId))
                    {
                        requiresRewrite = true;
                        continue;
                    }

                    knownRequestIds.Add(entry.requestId);
                    if (entry.schemaVersion > CurrentLedgerSchemaVersion
                        || !TryDeserialize(
                            entry.transaction,
                            expectedMode,
                            out GachaPendingTransaction transaction)
                        || transaction.Phase != GachaTransactionPhase.Completed
                        || !string.Equals(
                            transaction.RequestId,
                            entry.requestId,
                            StringComparison.Ordinal))
                    {
                        // Preserve the independently stored request id as a
                        // tombstone; only this receipt is unavailable.
                        requiresRewrite = true;
                        continue;
                    }

                    requiresRewrite |=
                        entry.schemaVersion != CurrentLedgerSchemaVersion;

                    if (restoredByRequestId.ContainsKey(entry.requestId))
                    {
                        requiresRewrite = true;
                        continue;
                    }

                    restoredByRequestId.Add(entry.requestId, transaction);
                }
            }

            // Salvage the v1 list entry-by-entry. A malformed transaction can
            // never invalidate a valid sibling, and any readable request id is
            // retained as a no-reroll tombstone.
            for (int index = 0; index < ledger.transactions.Count; index++)
            {
                string legacyPayload = ledger.transactions[index];
                if (TryReadRequestId(legacyPayload, out string legacyRequestId))
                {
                    knownRequestIds.Add(legacyRequestId);
                }

                if (TryDeserialize(
                        legacyPayload,
                        expectedMode,
                        out GachaPendingTransaction transaction)
                    && transaction.Phase == GachaTransactionPhase.Completed
                    && !restoredByRequestId.ContainsKey(transaction.RequestId))
                {
                    restoredByRequestId.Add(transaction.RequestId, transaction);
                    knownRequestIds.Add(transaction.RequestId);
                }

                requiresRewrite = true;
            }

            var requestIds = new List<string>(restoredByRequestId.Keys);
            requestIds.Sort(StringComparer.Ordinal);
            for (int index = 0; index < requestIds.Count; index++)
            {
                transactions.Add(restoredByRequestId[requestIds[index]]);
            }

            requiresRewrite |= ledger.schemaVersion != CurrentLedgerSchemaVersion;

            return true;
        }

        public static bool TryReadRequestId(string payload, out string requestId)
        {
            requestId = string.Empty;
            if (string.IsNullOrEmpty(payload))
            {
                return false;
            }

            try
            {
                StoredTransaction stored = JsonUtility.FromJson<StoredTransaction>(payload);
                if (stored != null && IsRequestIdValid(stored.requestId))
                {
                    requestId = stored.requestId;
                    return true;
                }
            }
            catch (Exception)
            {
                // Callers retain any independent ledger-entry id as tombstone.
            }

            return false;
        }

        public static bool TryDeserialize(
            string payload,
            GachaRuntimeMode expectedMode,
            out GachaPendingTransaction transaction)
        {
            transaction = null;
            if (string.IsNullOrEmpty(payload))
            {
                return false;
            }

            StoredTransaction stored;
            try
            {
                stored = JsonUtility.FromJson<StoredTransaction>(payload);
            }
            catch (Exception)
            {
                return false;
            }

            if (stored == null
                || !IsRequestIdValid(stored.requestId)
                || string.IsNullOrEmpty(stored.seriesId)
                || stored.schemaVersion > CurrentTransactionSchemaVersion
                || (stored.count != 1 && stored.count != GachaEconomyRules.TenDrawCount)
                || (expectedMode == GachaRuntimeMode.InternalUnlimited && stored.count != 1)
                || stored.runtimeMode != (int)expectedMode
                || stored.paymentMethod < (int)GachaPaymentMethod.Ticket
                || stored.paymentMethod > (int)GachaPaymentMethod.Coin
                || (expectedMode == GachaRuntimeMode.InternalUnlimited
                    && stored.paymentMethod != (int)GachaPaymentMethod.Ticket)
                || stored.phase < (int)GachaTransactionPhase.Prepared
                || stored.phase > (int)GachaTransactionPhase.Completed
                || stored.signatureMissesAfter < 0
                || stored.heirloomMissesAfter < 0
                || stored.ticketCost < 0
                || stored.coinCost < 0
                || stored.rows == null
                || stored.rows.Count != stored.count)
            {
                return false;
            }

            bool isCompleted = stored.phase == (int)GachaTransactionPhase.Completed;
            if (!isCompleted
                && (GachaCatalog.ResolveSeries(stored.seriesId) == null
                    || stored.ticketCost
                        != stored.count * GachaEconomyRules.SingleDrawTicketCost
                    || stored.coinCost
                        != (stored.count == GachaEconomyRules.TenDrawCount
                            ? GachaEconomyRules.TenDrawCoinCost
                            : GachaEconomyRules.SingleDrawCoinCost)))
            {
                return false;
            }

            var rows = new List<GachaDrawReceiptRow>(stored.rows.Count);
            for (int index = 0; index < stored.rows.Count; index++)
            {
                StoredRow storedRow = stored.rows[index];
                GachaPrizeDefinition? prize = GachaCatalog.ResolvePrize(storedRow.prizeId);
                if (string.IsNullOrEmpty(storedRow.prizeId)
                    || storedRow.rarity < (int)GachaRarity.Standard
                    || storedRow.rarity > (int)GachaRarity.Heirloom
                    || storedRow.shardsGained < 0
                    || (storedRow.isNew && storedRow.shardsGained != 0))
                {
                    return false;
                }

                if (!isCompleted
                    && (!prize.HasValue
                        || !string.Equals(
                            prize.Value.SeriesId,
                            stored.seriesId,
                            StringComparison.Ordinal)
                        || storedRow.rarity != (int)prize.Value.Rarity
                        || (!storedRow.isNew
                            && storedRow.shardsGained
                                != GachaEconomyRules.DuplicateShardValue(
                                    prize.Value.Rarity))))
                {
                    return false;
                }

                rows.Add(new GachaDrawReceiptRow(
                    new GachaDrawOutcome(
                        storedRow.prizeId,
                        (GachaRarity)storedRow.rarity,
                        storedRow.forcedBySignaturePity,
                        storedRow.forcedByHeirloomPity,
                        storedRow.forcedByTenDraw),
                    storedRow.isNew,
                    storedRow.shardsGained,
                    storedRow.firstObtainedAtUtc ?? string.Empty));
            }

            transaction = new GachaPendingTransaction(
                stored.requestId,
                stored.seriesId,
                stored.count,
                (GachaPaymentMethod)stored.paymentMethod,
                expectedMode,
                (GachaTransactionPhase)stored.phase,
                new GachaPityState
                {
                    SignatureMisses = stored.signatureMissesAfter,
                    HeirloomMisses = stored.heirloomMissesAfter
                },
                stored.ticketCost,
                stored.coinCost,
                rows);
            return true;
        }

        public static bool IsRequestIdValid(string requestId)
        {
            if (string.IsNullOrEmpty(requestId) || requestId.Length > 128)
            {
                return false;
            }

            for (int index = 0; index < requestId.Length; index++)
            {
                char character = requestId[index];
                if (char.IsWhiteSpace(character)
                    || char.IsControl(character)
                    || character == '|'
                    || character == '\t'
                    || character == '\n'
                    || character == '\r')
                {
                    return false;
                }
            }

            return true;
        }
    }
}
