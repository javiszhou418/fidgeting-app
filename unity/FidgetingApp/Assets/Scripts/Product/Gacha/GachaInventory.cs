using System;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;

namespace FidgetingApp.Product.Gacha
{
    public enum GachaPaymentMethod
    {
        Ticket = 0,
        Coin = 1
    }

    public readonly struct GachaDrawReceiptRow
    {
        public GachaDrawReceiptRow(
            GachaDrawOutcome outcome,
            bool isNew,
            int shardsGained)
        {
            Outcome = outcome;
            IsNew = isNew;
            ShardsGained = Math.Max(0, shardsGained);
        }

        public GachaDrawOutcome Outcome { get; }
        public bool IsNew { get; }
        public int ShardsGained { get; }
    }

    public readonly struct GachaDrawReceipt
    {
        public GachaDrawReceipt(
            bool success,
            string failureReason,
            IReadOnlyList<GachaDrawReceiptRow> rows)
        {
            Success = success;
            FailureReason = failureReason ?? string.Empty;
            Rows = rows ?? Array.Empty<GachaDrawReceiptRow>();
        }

        public bool Success { get; }
        public string FailureReason { get; }
        public IReadOnlyList<GachaDrawReceiptRow> Rows { get; }

        public static GachaDrawReceipt Failure(string reason)
        {
            return new GachaDrawReceipt(false, reason, Array.Empty<GachaDrawReceiptRow>());
        }
    }

    /// <summary>
    /// Owns balances, owned prizes, shards, and per-series pity. Persistence
    /// mirrors CollectorProgressionRuntime: namespaced PlayerPrefs keys with a
    /// version stamp so later schema changes migrate explicitly.
    /// </summary>
    public sealed class GachaInventoryRuntime
    {
        public const string DefaultPrefix = "fidgeting.gacha.v1.";
        public const string InternalUnlimitedPrefix = "fidgeting.gacha.internal.v2.";
        public const int SchemaVersion = 1;
        private const int TransactionSchemaVersion = 2;

        private readonly string prefix;
        private readonly IGachaRandom random;
        private readonly HashSet<string> ownedPrizes = new HashSet<string>(StringComparer.Ordinal);
        private readonly Dictionary<string, GachaPityState> pityBySeries =
            new Dictionary<string, GachaPityState>(StringComparer.Ordinal);
        private readonly Dictionary<string, int> shardsBySeries =
            new Dictionary<string, int>(StringComparer.Ordinal);
        private readonly Dictionary<string, int> drawsBySeries =
            new Dictionary<string, int>(StringComparer.Ordinal);
        private readonly Dictionary<string, GachaPendingTransaction> completedTransactions =
            new Dictionary<string, GachaPendingTransaction>(StringComparer.Ordinal);
        private readonly HashSet<string> completedRequestIds =
            new HashSet<string>(StringComparer.Ordinal);

        private int tickets;
        private int coins;
        private GachaPendingTransaction pendingTransaction;
        private GachaPendingTransaction lastCompletedTransaction;

        public GachaInventoryRuntime(
            string storagePrefix = DefaultPrefix,
            IGachaRandom randomSource = null)
            : this(GachaRuntimeMode.Production, storagePrefix, randomSource)
        {
        }

        public GachaInventoryRuntime(
            GachaRuntimeMode runtimeMode,
            string storagePrefix = null,
            IGachaRandom randomSource = null)
        {
            RuntimeMode = runtimeMode;
            prefix = string.IsNullOrEmpty(storagePrefix)
                ? runtimeMode == GachaRuntimeMode.InternalUnlimited
                    ? InternalUnlimitedPrefix
                    : DefaultPrefix
                : storagePrefix;
            random = randomSource ?? new GachaSplitMix64(
                (ulong)Environment.TickCount * 0x9E3779B97F4A7C15UL + 0xD1B54A32D192ED03UL);
            Load();
        }

        public GachaRuntimeMode RuntimeMode { get; }
        public string StoragePrefix => prefix;
        public bool HasUnlimitedDraws => RuntimeMode == GachaRuntimeMode.InternalUnlimited;
        public int Tickets => tickets;
        public int Coins => coins;
        public GachaPendingTransaction PendingTransaction => pendingTransaction;

        public int Shards(string seriesId)
        {
            return shardsBySeries.TryGetValue(seriesId ?? string.Empty, out int value) ? value : 0;
        }

        public int TotalDraws(string seriesId)
        {
            return drawsBySeries.TryGetValue(seriesId ?? string.Empty, out int value) ? value : 0;
        }

        public bool Owns(string prizeId)
        {
            return ownedPrizes.Contains(prizeId ?? string.Empty);
        }

        public int OwnedCount => ownedPrizes.Count;

        public GachaPityState Pity(string seriesId)
        {
            return pityBySeries.TryGetValue(seriesId ?? string.Empty, out GachaPityState value)
                ? value
                : default;
        }

        public void CreditTickets(int amount)
        {
            if (amount <= 0)
            {
                return;
            }

            tickets += amount;
            Persist();
        }

        public void CreditCoins(int amount)
        {
            if (amount <= 0)
            {
                return;
            }

            coins += amount;
            Persist();
        }

        public int RhythmWeeksCredited { get; private set; }

        /// <summary>
        /// Free-ticket loop: every completed 7-day rhythm week grants exactly
        /// one draw ticket, keyed to a persisted credited counter so repeated
        /// publishes and reloads never double-grant. Returns tickets granted.
        /// </summary>
        public int SyncRhythmTickets(int completedRhythmWeeks)
        {
            int completed = Math.Max(0, completedRhythmWeeks);
            if (completed <= RhythmWeeksCredited)
            {
                return 0;
            }

            int granted = completed - RhythmWeeksCredited;
            RhythmWeeksCredited = completed;
            tickets += granted;
            Persist();
            return granted;
        }

        /// <summary>
        /// Fixes one authoritative outcome and persists it before presentation.
        /// No wallet, pity, ownership, shard, or draw-count mutation occurs
        /// until AcknowledgePending succeeds.
        /// </summary>
        public GachaTransactionResult PrepareDraw(
            string seriesId,
            int count,
            GachaPaymentMethod method,
            string requestId)
        {
            if (!GachaTransactionCodec.IsRequestIdValid(requestId))
            {
                return TransactionFailure(requestId, "invalid-request-id");
            }

            if (pendingTransaction != null)
            {
                if (string.Equals(
                    pendingTransaction.RequestId,
                    requestId,
                    StringComparison.Ordinal))
                {
                    return pendingTransaction.Matches(seriesId, count, method)
                        ? GachaTransactionResult.Succeeded(RuntimeMode, pendingTransaction)
                        : TransactionFailure(requestId, "request-id-conflict");
                }
            }

            if (completedTransactions.TryGetValue(
                    requestId,
                    out GachaPendingTransaction completedTransaction))
            {
                return completedTransaction.Matches(seriesId, count, method)
                    ? GachaTransactionResult.Succeeded(RuntimeMode, completedTransaction)
                    : TransactionFailure(requestId, "request-id-conflict");
            }

            if (completedRequestIds.Contains(requestId))
            {
                return TransactionFailure(requestId, "completed-receipt-unavailable");
            }

            if (pendingTransaction != null)
            {
                return TransactionFailure(requestId, "transaction-in-flight");
            }

            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(seriesId);
            if (series == null)
            {
                return TransactionFailure(requestId, "unknown-series");
            }

            if (count != 1 && count != GachaEconomyRules.TenDrawCount)
            {
                return TransactionFailure(requestId, "unsupported-count");
            }

            if (RuntimeMode == GachaRuntimeMode.InternalUnlimited && count != 1)
            {
                return TransactionFailure(requestId, "unsupported-count");
            }

            if (method != GachaPaymentMethod.Ticket && method != GachaPaymentMethod.Coin)
            {
                return TransactionFailure(requestId, "unsupported-payment-method");
            }

            if (RuntimeMode == GachaRuntimeMode.InternalUnlimited
                && method != GachaPaymentMethod.Ticket)
            {
                return TransactionFailure(requestId, "unsupported-payment-method");
            }

            int ticketCost = count * GachaEconomyRules.SingleDrawTicketCost;
            int coinCost = count == GachaEconomyRules.TenDrawCount
                ? GachaEconomyRules.TenDrawCoinCost
                : GachaEconomyRules.SingleDrawCoinCost;
            if (RuntimeMode == GachaRuntimeMode.Production)
            {
                if (method == GachaPaymentMethod.Ticket && tickets < ticketCost)
                {
                    return TransactionFailure(requestId, "insufficient-tickets");
                }

                if (method == GachaPaymentMethod.Coin && coins < coinCost)
                {
                    return TransactionFailure(requestId, "insufficient-coins");
                }
            }

            GachaPityState pityAfter = Pity(seriesId);
            IReadOnlyList<GachaDrawOutcome> outcomes = GachaDrawEngine.DrawBatch(
                series,
                count,
                ref pityAfter,
                random);
            var projectedOwned = new HashSet<string>(ownedPrizes, StringComparer.Ordinal);
            var rows = new List<GachaDrawReceiptRow>(outcomes.Count);
            for (int index = 0; index < outcomes.Count; index++)
            {
                GachaDrawOutcome outcome = outcomes[index];
                bool isNew = projectedOwned.Add(outcome.PrizeId);
                int shardsGained = isNew
                    ? 0
                    : GachaEconomyRules.DuplicateShardValue(outcome.Rarity);
                rows.Add(new GachaDrawReceiptRow(outcome, isNew, shardsGained));
            }

            pendingTransaction = new GachaPendingTransaction(
                requestId,
                seriesId,
                count,
                method,
                RuntimeMode,
                GachaTransactionPhase.Prepared,
                pityAfter,
                ticketCost,
                coinCost,
                rows);
            Persist();
            return GachaTransactionResult.Succeeded(RuntimeMode, pendingTransaction);
        }

        /// <summary>
        /// Restores/query a known transaction without consuming random state.
        /// The active pending transaction and every completed request remain
        /// queryable so an old retry can never reroll after later draws.
        /// </summary>
        public GachaTransactionResult QueryTransaction(string requestId)
        {
            if (!GachaTransactionCodec.IsRequestIdValid(requestId))
            {
                return TransactionFailure(requestId, "invalid-request-id");
            }

            if (pendingTransaction != null
                && string.Equals(
                    pendingTransaction.RequestId,
                    requestId,
                    StringComparison.Ordinal))
            {
                return GachaTransactionResult.Succeeded(RuntimeMode, pendingTransaction);
            }

            if (completedTransactions.TryGetValue(
                    requestId,
                    out GachaPendingTransaction completedTransaction))
            {
                return GachaTransactionResult.Succeeded(RuntimeMode, completedTransaction);
            }

            if (completedRequestIds.Contains(requestId))
            {
                return TransactionFailure(requestId, "completed-receipt-unavailable");
            }

            return TransactionFailure(requestId, "transaction-not-found");
        }

        /// <summary>
        /// Records that the shipping 3D animation reached its acceptance gate.
        /// Repeating the call is idempotent and never commits inventory state.
        /// </summary>
        public GachaTransactionResult MarkRevealAwaitingAcceptance(string requestId)
        {
            GachaTransactionResult found = QueryTransaction(requestId);
            if (!found.Success)
            {
                return found;
            }

            if (found.Transaction.Phase == GachaTransactionPhase.Completed
                || found.Transaction.Phase == GachaTransactionPhase.AwaitingAcceptance)
            {
                return found;
            }

            pendingTransaction = pendingTransaction.WithPhase(
                GachaTransactionPhase.AwaitingAcceptance);
            Persist();
            return GachaTransactionResult.Succeeded(RuntimeMode, pendingTransaction);
        }

        /// <summary>
        /// Commits the prepared outcome exactly once. Acknowledgement is only
        /// legal after the reveal session explicitly reaches its acceptance
        /// phase; duplicate acknowledgements return the completed receipt.
        /// </summary>
        public GachaTransactionResult AcknowledgePending(string requestId)
        {
            if (!GachaTransactionCodec.IsRequestIdValid(requestId))
            {
                return TransactionFailure(requestId, "invalid-request-id");
            }

            if (completedTransactions.TryGetValue(
                    requestId,
                    out GachaPendingTransaction completedTransaction))
            {
                return GachaTransactionResult.Succeeded(RuntimeMode, completedTransaction);
            }

            if (completedRequestIds.Contains(requestId))
            {
                return TransactionFailure(requestId, "completed-receipt-unavailable");
            }

            if (pendingTransaction == null
                || !string.Equals(
                    pendingTransaction.RequestId,
                    requestId,
                    StringComparison.Ordinal))
            {
                return TransactionFailure(requestId, "transaction-not-found");
            }

            if (pendingTransaction.Phase != GachaTransactionPhase.AwaitingAcceptance)
            {
                return TransactionFailure(requestId, "reveal-not-ready");
            }

            if (RuntimeMode == GachaRuntimeMode.Production)
            {
                if (pendingTransaction.PaymentMethod == GachaPaymentMethod.Ticket
                    && tickets < pendingTransaction.TicketCost)
                {
                    return TransactionFailure(requestId, "reserved-funds-unavailable");
                }

                if (pendingTransaction.PaymentMethod == GachaPaymentMethod.Coin
                    && coins < pendingTransaction.CoinCost)
                {
                    return TransactionFailure(requestId, "reserved-funds-unavailable");
                }
            }

            int shardsGained = 0;
            for (int index = 0; index < pendingTransaction.Receipt.Rows.Count; index++)
            {
                GachaDrawReceiptRow row = pendingTransaction.Receipt.Rows[index];
                ownedPrizes.Add(row.Outcome.PrizeId);
                shardsGained += row.ShardsGained;
            }

            if (RuntimeMode == GachaRuntimeMode.Production)
            {
                if (pendingTransaction.PaymentMethod == GachaPaymentMethod.Ticket)
                {
                    tickets -= pendingTransaction.TicketCost;
                }
                else
                {
                    coins -= pendingTransaction.CoinCost;
                }
            }

            pityBySeries[pendingTransaction.SeriesId] = pendingTransaction.PityAfter;
            shardsBySeries[pendingTransaction.SeriesId] =
                Shards(pendingTransaction.SeriesId) + shardsGained;
            drawsBySeries[pendingTransaction.SeriesId] =
                TotalDraws(pendingTransaction.SeriesId) + pendingTransaction.Count;

            lastCompletedTransaction = pendingTransaction.WithPhase(
                GachaTransactionPhase.Completed);
            completedTransactions[lastCompletedTransaction.RequestId] =
                lastCompletedTransaction;
            completedRequestIds.Add(lastCompletedTransaction.RequestId);
            pendingTransaction = null;
            Persist();
            return GachaTransactionResult.Succeeded(RuntimeMode, lastCompletedTransaction);
        }

        private GachaTransactionResult TransactionFailure(string requestId, string reason)
        {
            return GachaTransactionResult.Failed(RuntimeMode, requestId, reason);
        }

        public GachaDrawReceipt Draw(string seriesId, int count, GachaPaymentMethod method)
        {
            if (RuntimeMode != GachaRuntimeMode.Production)
            {
                return GachaDrawReceipt.Failure("transaction-api-required");
            }

            if (pendingTransaction != null)
            {
                return GachaDrawReceipt.Failure("transaction-in-flight");
            }

            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(seriesId);
            if (series == null)
            {
                return GachaDrawReceipt.Failure("unknown-series");
            }

            if (count != 1 && count != GachaEconomyRules.TenDrawCount)
            {
                return GachaDrawReceipt.Failure("unsupported-count");
            }

            int ticketCost = count * GachaEconomyRules.SingleDrawTicketCost;
            int coinCost = count == GachaEconomyRules.TenDrawCount
                ? GachaEconomyRules.TenDrawCoinCost
                : GachaEconomyRules.SingleDrawCoinCost;
            if (method == GachaPaymentMethod.Ticket && tickets < ticketCost)
            {
                return GachaDrawReceipt.Failure("insufficient-tickets");
            }

            if (method == GachaPaymentMethod.Coin && coins < coinCost)
            {
                return GachaDrawReceipt.Failure("insufficient-coins");
            }

            GachaPityState pity = Pity(seriesId);
            IReadOnlyList<GachaDrawOutcome> outcomes =
                GachaDrawEngine.DrawBatch(series, count, ref pity, random);
            pityBySeries[seriesId] = pity;

            var rows = new List<GachaDrawReceiptRow>(outcomes.Count);
            int shardsGainedTotal = 0;
            for (int index = 0; index < outcomes.Count; index++)
            {
                GachaDrawOutcome outcome = outcomes[index];
                bool isNew = ownedPrizes.Add(outcome.PrizeId);
                int shardsGained = 0;
                if (!isNew)
                {
                    shardsGained = GachaEconomyRules.DuplicateShardValue(outcome.Rarity);
                    shardsGainedTotal += shardsGained;
                }

                rows.Add(new GachaDrawReceiptRow(outcome, isNew, shardsGained));
            }

            if (method == GachaPaymentMethod.Ticket)
            {
                tickets -= ticketCost;
            }
            else
            {
                coins -= coinCost;
            }

            shardsBySeries[seriesId] = Shards(seriesId) + shardsGainedTotal;
            drawsBySeries[seriesId] = TotalDraws(seriesId) + count;
            Persist();
            return new GachaDrawReceipt(true, string.Empty, rows);
        }

        public bool TryRedeemShards(string prizeId, out string failureReason)
        {
            if (pendingTransaction != null)
            {
                failureReason = "transaction-in-flight";
                return false;
            }

            GachaPrizeDefinition? resolved = GachaCatalog.ResolvePrize(prizeId);
            if (!resolved.HasValue)
            {
                failureReason = "unknown-prize";
                return false;
            }

            GachaPrizeDefinition prize = resolved.Value;
            if (!GachaEconomyRules.CanRedeem(prize.Rarity))
            {
                failureReason = "not-redeemable";
                return false;
            }

            if (Owns(prize.Id))
            {
                failureReason = "already-owned";
                return false;
            }

            int cost = GachaEconomyRules.RedeemShardCost(prize.Rarity);
            int balance = Shards(prize.SeriesId);
            if (balance < cost)
            {
                failureReason = "insufficient-shards";
                return false;
            }

            shardsBySeries[prize.SeriesId] = balance - cost;
            ownedPrizes.Add(prize.Id);
            Persist();
            failureReason = string.Empty;
            return true;
        }

        /// <summary>
        /// TSV snapshot for the native UI: balances, then one row per series
        /// with pity progress and shards, then owned prize ids.
        /// </summary>
        public string SnapshotPayload()
        {
            var rows = new List<string>
            {
                string.Join(
                    "\t",
                    "wallet",
                    tickets.ToString(CultureInfo.InvariantCulture),
                    coins.ToString(CultureInfo.InvariantCulture))
            };
            IReadOnlyList<GachaSeriesDefinition> series = GachaCatalog.Series;
            for (int index = 0; index < series.Count; index++)
            {
                GachaSeriesDefinition definition = series[index];
                GachaPityState pity = Pity(definition.Id);
                rows.Add(string.Join(
                    "\t",
                    "series-state",
                    definition.Id,
                    pity.SignatureMisses.ToString(CultureInfo.InvariantCulture),
                    pity.HeirloomMisses.ToString(CultureInfo.InvariantCulture),
                    Shards(definition.Id).ToString(CultureInfo.InvariantCulture),
                    TotalDraws(definition.Id).ToString(CultureInfo.InvariantCulture)));
            }

            rows.Add("runtime-mode\t" + GachaNativeBridge.RuntimeModeToken(RuntimeMode));
            if (pendingTransaction != null)
            {
                rows.Add(string.Join(
                    "\t",
                    "transaction",
                    pendingTransaction.RequestId,
                    GachaNativeBridge.PhaseToken(pendingTransaction.Phase),
                    pendingTransaction.SeriesId,
                    pendingTransaction.Count.ToString(CultureInfo.InvariantCulture),
                    GachaNativeBridge.PaymentToken(pendingTransaction.PaymentMethod)));
                GachaNativeBridge.AppendReceiptRows(rows, pendingTransaction.Receipt);
            }
            else
            {
                rows.Add("transaction\t\tidle\t\t0\tticket");
                rows.Add("result\tnone");
            }

            var owned = new List<string>(ownedPrizes);
            owned.Sort(StringComparer.Ordinal);
            rows.Add("owned\t" + string.Join("|", owned));
            return string.Join("\n", rows);
        }

        private string Key(string suffix)
        {
            return prefix + suffix;
        }

        private void WriteCompletedRequestIds()
        {
            if (completedRequestIds.Count == 0)
            {
                PlayerPrefs.DeleteKey(Key("transaction.completedRequestIds"));
                return;
            }

            var requestIds = new List<string>(completedRequestIds);
            requestIds.Sort(StringComparer.Ordinal);
            PlayerPrefs.SetString(
                Key("transaction.completedRequestIds"),
                string.Join("|", requestIds));
        }

        private void Load()
        {
            int version = PlayerPrefs.GetInt(Key("version"), 0);
            if (version == 0)
            {
                PlayerPrefs.SetInt(Key("version"), SchemaVersion);
            }

            tickets = PlayerPrefs.GetInt(Key("tickets"), 0);
            coins = PlayerPrefs.GetInt(Key("coins"), 0);
            RhythmWeeksCredited = PlayerPrefs.GetInt(Key("rhythmWeeksCredited"), 0);
            string owned = PlayerPrefs.GetString(Key("owned"), string.Empty);
            if (!string.IsNullOrEmpty(owned))
            {
                foreach (string prizeId in owned.Split('|'))
                {
                    if (!string.IsNullOrEmpty(prizeId))
                    {
                        ownedPrizes.Add(prizeId);
                    }
                }
            }

            IReadOnlyList<GachaSeriesDefinition> series = GachaCatalog.Series;
            for (int index = 0; index < series.Count; index++)
            {
                string seriesId = series[index].Id;
                var pity = new GachaPityState
                {
                    SignatureMisses = PlayerPrefs.GetInt(
                        Key(seriesId + ".signatureMisses"), 0),
                    HeirloomMisses = PlayerPrefs.GetInt(
                        Key(seriesId + ".heirloomMisses"), 0)
                };
                pityBySeries[seriesId] = pity;
                shardsBySeries[seriesId] = PlayerPrefs.GetInt(Key(seriesId + ".shards"), 0);
                drawsBySeries[seriesId] = PlayerPrefs.GetInt(Key(seriesId + ".draws"), 0);
            }

            bool discardedCorruptTransaction = false;
            string pendingPayload = PlayerPrefs.GetString(
                Key("transaction.pending"),
                string.Empty);
            if (!string.IsNullOrEmpty(pendingPayload))
            {
                if (GachaTransactionCodec.TryDeserialize(
                        pendingPayload,
                        RuntimeMode,
                        out GachaPendingTransaction restoredPending)
                    && restoredPending.Phase != GachaTransactionPhase.Completed)
                {
                    pendingTransaction = restoredPending;
                }
                else
                {
                    PlayerPrefs.DeleteKey(Key("transaction.pending"));
                    discardedCorruptTransaction = true;
                }
            }

            bool completedLedgerNeedsWrite = false;
            string completedRequestIdsPayload = PlayerPrefs.GetString(
                Key("transaction.completedRequestIds"),
                string.Empty);
            if (!string.IsNullOrEmpty(completedRequestIdsPayload))
            {
                string[] persistedRequestIds = completedRequestIdsPayload.Split('|');
                for (int index = 0; index < persistedRequestIds.Length; index++)
                {
                    if (GachaTransactionCodec.IsRequestIdValid(
                            persistedRequestIds[index]))
                    {
                        completedRequestIds.Add(persistedRequestIds[index]);
                    }
                    else
                    {
                        completedLedgerNeedsWrite = true;
                    }
                }
            }

            string completedLedgerPayload = PlayerPrefs.GetString(
                Key("transaction.completedLedger"),
                string.Empty);
            if (!string.IsNullOrEmpty(completedLedgerPayload))
            {
                if (GachaTransactionCodec.TryDeserializeCompletedLedger(
                        completedLedgerPayload,
                        RuntimeMode,
                        out List<GachaPendingTransaction> restoredLedger,
                        out HashSet<string> ledgerRequestIds,
                        out bool ledgerRequiresRewrite))
                {
                    completedLedgerNeedsWrite |= ledgerRequiresRewrite;
                    foreach (string requestId in ledgerRequestIds)
                    {
                        if (completedRequestIds.Add(requestId))
                        {
                            completedLedgerNeedsWrite = true;
                        }
                    }

                    for (int index = 0; index < restoredLedger.Count; index++)
                    {
                        GachaPendingTransaction completed = restoredLedger[index];
                        completedTransactions[completed.RequestId] = completed;
                        completedRequestIds.Add(completed.RequestId);
                    }
                }
                else
                {
                    // The independent request-id index remains authoritative:
                    // every known id becomes a no-reroll tombstone.
                    PlayerPrefs.DeleteKey(Key("transaction.completedLedger"));
                    discardedCorruptTransaction = true;
                    completedLedgerNeedsWrite = true;
                }
            }

            // Compatibility migration for Build 42 candidates that persisted
            // only the most recent completed request.
            string completedPayload = PlayerPrefs.GetString(
                Key("transaction.completed"),
                string.Empty);
            if (!string.IsNullOrEmpty(completedPayload))
            {
                if (GachaTransactionCodec.TryReadRequestId(
                        completedPayload,
                        out string legacyRequestId)
                    && completedRequestIds.Add(legacyRequestId))
                {
                    completedLedgerNeedsWrite = true;
                }

                if (GachaTransactionCodec.TryDeserialize(
                        completedPayload,
                        RuntimeMode,
                        out GachaPendingTransaction restoredCompleted)
                    && restoredCompleted.Phase == GachaTransactionPhase.Completed)
                {
                    if (completedRequestIds.Add(restoredCompleted.RequestId))
                    {
                        completedLedgerNeedsWrite = true;
                    }

                    if (completedTransactions.TryGetValue(
                            restoredCompleted.RequestId,
                            out GachaPendingTransaction ledgerCompleted))
                    {
                        if (string.Equals(
                                GachaTransactionCodec.Serialize(ledgerCompleted),
                                GachaTransactionCodec.Serialize(restoredCompleted),
                                StringComparison.Ordinal))
                        {
                            lastCompletedTransaction = ledgerCompleted;
                        }
                        else
                        {
                            PlayerPrefs.DeleteKey(Key("transaction.completed"));
                            discardedCorruptTransaction = true;
                        }
                    }
                    else
                    {
                        completedTransactions[restoredCompleted.RequestId] =
                            restoredCompleted;
                        lastCompletedTransaction = restoredCompleted;
                        completedLedgerNeedsWrite = true;
                    }
                }
                else
                {
                    PlayerPrefs.DeleteKey(Key("transaction.completed"));
                    discardedCorruptTransaction = true;
                }
            }

            if (completedLedgerNeedsWrite)
            {
                PlayerPrefs.SetInt(Key("transaction.version"), TransactionSchemaVersion);
                PlayerPrefs.SetString(
                    Key("transaction.completedLedger"),
                    GachaTransactionCodec.SerializeCompletedLedger(
                        completedTransactions.Values));
                WriteCompletedRequestIds();
            }

            if (discardedCorruptTransaction || completedLedgerNeedsWrite)
            {
                PlayerPrefs.Save();
            }
        }

        private void Persist()
        {
            PlayerPrefs.SetInt(Key("version"), SchemaVersion);
            PlayerPrefs.SetInt(Key("tickets"), tickets);
            PlayerPrefs.SetInt(Key("coins"), coins);
            PlayerPrefs.SetInt(Key("rhythmWeeksCredited"), RhythmWeeksCredited);
            var owned = new List<string>(ownedPrizes);
            owned.Sort(StringComparer.Ordinal);
            PlayerPrefs.SetString(Key("owned"), string.Join("|", owned));
            foreach (KeyValuePair<string, GachaPityState> entry in pityBySeries)
            {
                PlayerPrefs.SetInt(
                    Key(entry.Key + ".signatureMisses"), entry.Value.SignatureMisses);
                PlayerPrefs.SetInt(
                    Key(entry.Key + ".heirloomMisses"), entry.Value.HeirloomMisses);
            }

            foreach (KeyValuePair<string, int> entry in shardsBySeries)
            {
                PlayerPrefs.SetInt(Key(entry.Key + ".shards"), entry.Value);
            }

            foreach (KeyValuePair<string, int> entry in drawsBySeries)
            {
                PlayerPrefs.SetInt(Key(entry.Key + ".draws"), entry.Value);
            }

            PlayerPrefs.SetInt(Key("transaction.version"), TransactionSchemaVersion);
            if (pendingTransaction == null)
            {
                PlayerPrefs.DeleteKey(Key("transaction.pending"));
            }
            else
            {
                PlayerPrefs.SetString(
                    Key("transaction.pending"),
                    GachaTransactionCodec.Serialize(pendingTransaction));
            }

            if (lastCompletedTransaction == null)
            {
                PlayerPrefs.DeleteKey(Key("transaction.completed"));
            }
            else
            {
                PlayerPrefs.SetString(
                    Key("transaction.completed"),
                    GachaTransactionCodec.Serialize(lastCompletedTransaction));
            }

            if (completedTransactions.Count == 0)
            {
                PlayerPrefs.DeleteKey(Key("transaction.completedLedger"));
            }
            else
            {
                PlayerPrefs.SetString(
                    Key("transaction.completedLedger"),
                    GachaTransactionCodec.SerializeCompletedLedger(
                        completedTransactions.Values));
            }

            WriteCompletedRequestIds();

            PlayerPrefs.Save();
        }

        /// <summary>Test hook: removes every key under this runtime's prefix.</summary>
        public void DeleteAllForTests()
        {
            PlayerPrefs.DeleteKey(Key("version"));
            PlayerPrefs.DeleteKey(Key("tickets"));
            PlayerPrefs.DeleteKey(Key("coins"));
            PlayerPrefs.DeleteKey(Key("rhythmWeeksCredited"));
            PlayerPrefs.DeleteKey(Key("owned"));
            PlayerPrefs.DeleteKey(Key("transaction.version"));
            PlayerPrefs.DeleteKey(Key("transaction.pending"));
            PlayerPrefs.DeleteKey(Key("transaction.completed"));
            PlayerPrefs.DeleteKey(Key("transaction.completedLedger"));
            PlayerPrefs.DeleteKey(Key("transaction.completedRequestIds"));
            IReadOnlyList<GachaSeriesDefinition> series = GachaCatalog.Series;
            for (int index = 0; index < series.Count; index++)
            {
                string seriesId = series[index].Id;
                PlayerPrefs.DeleteKey(Key(seriesId + ".signatureMisses"));
                PlayerPrefs.DeleteKey(Key(seriesId + ".heirloomMisses"));
                PlayerPrefs.DeleteKey(Key(seriesId + ".shards"));
                PlayerPrefs.DeleteKey(Key(seriesId + ".draws"));
            }
        }
    }
}
