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
            int shardsGained,
            string firstObtainedAtUtc = "",
            string collectibleId = "")
        {
            Outcome = outcome;
            IsNew = isNew;
            ShardsGained = Math.Max(0, shardsGained);
            FirstObtainedAtUtc = firstObtainedAtUtc ?? string.Empty;
            CollectibleId = collectibleId ?? string.Empty;
        }

        public GachaDrawOutcome Outcome { get; }
        public bool IsNew { get; }
        public int ShardsGained { get; }
        public string FirstObtainedAtUtc { get; }
        public string CollectibleId { get; }
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
        public const int SchemaVersion = 2;

        private readonly string prefix;
        private readonly IGachaRandom random;
        private readonly HashSet<string> ownedPrizes = new HashSet<string>(StringComparer.Ordinal);
        private readonly Dictionary<string, string> firstObtainedAtUtcByPrize =
            new Dictionary<string, string>(StringComparer.Ordinal);
        private readonly Dictionary<string, string> collectibleIdByPrize =
            new Dictionary<string, string>(StringComparer.Ordinal);
        private readonly Dictionary<string, GachaPityState> pityBySeries =
            new Dictionary<string, GachaPityState>(StringComparer.Ordinal);
        private readonly Dictionary<string, int> shardsBySeries =
            new Dictionary<string, int>(StringComparer.Ordinal);
        private readonly Dictionary<string, int> drawsBySeries =
            new Dictionary<string, int>(StringComparer.Ordinal);

        private int tickets;
        private int coins;
        private GachaPendingTransaction pendingTransaction;
        private GachaPendingTransaction completedTransaction;

        public GachaInventoryRuntime(
            string storagePrefix = DefaultPrefix,
            IGachaRandom randomSource = null)
        {
            prefix = string.IsNullOrEmpty(storagePrefix) ? DefaultPrefix : storagePrefix;
            random = randomSource ?? new GachaSplitMix64(
                (ulong)Environment.TickCount * 0x9E3779B97F4A7C15UL + 0xD1B54A32D192ED03UL);
            Load();
        }

        public int Tickets => tickets;
        public int Coins => coins;
        public string StoragePrefix => prefix;
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

#if UNITY_EDITOR || DEVELOPMENT_BUILD || FIDGET_GATE12_SIMULATOR_PREVIEW
        public void PrimeGate12SimulatorPreview()
        {
            tickets = Math.Max(tickets, 1);
            pityBySeries[GachaCatalog.LaunchSeriesId] = new GachaPityState
            {
                SignatureMisses = GachaEconomyRules.SignatureHardPity,
                HeirloomMisses = GachaEconomyRules.HeirloomHardPity
            };
            Persist();
        }
#endif

        public GachaTransactionResult PrepareDraw(
            string seriesId,
            int count,
            GachaPaymentMethod method,
            string requestId)
        {
            if (!GachaTransactionCodec.IsRequestIdValid(requestId))
            {
                return GachaTransactionResult.Failed(
                    requestId,
                    "invalid-request-id");
            }
            if (pendingTransaction != null)
            {
                if (string.Equals(
                        pendingTransaction.RequestId,
                        requestId,
                        StringComparison.Ordinal))
                {
                    return pendingTransaction.Matches(seriesId, count, method)
                        ? GachaTransactionResult.Succeeded(pendingTransaction)
                        : GachaTransactionResult.Failed(
                            requestId,
                            "request-id-conflict");
                }
                return GachaTransactionResult.Failed(
                    requestId,
                    "transaction-in-flight");
            }
            if (completedTransaction != null
                && string.Equals(
                    completedTransaction.RequestId,
                    requestId,
                    StringComparison.Ordinal))
            {
                return completedTransaction.Matches(seriesId, count, method)
                    ? GachaTransactionResult.Succeeded(completedTransaction)
                    : GachaTransactionResult.Failed(
                        requestId,
                        "request-id-conflict");
            }

            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(seriesId);
            if (series == null)
            {
                return GachaTransactionResult.Failed(requestId, "unknown-series");
            }
            if (count != 1 && count != GachaEconomyRules.TenDrawCount)
            {
                return GachaTransactionResult.Failed(
                    requestId,
                    "unsupported-count");
            }
            if (method != GachaPaymentMethod.Ticket
                && method != GachaPaymentMethod.Coin)
            {
                return GachaTransactionResult.Failed(
                    requestId,
                    "unsupported-payment-method");
            }
            int ticketCost = count * GachaEconomyRules.SingleDrawTicketCost;
            int coinCost = count == GachaEconomyRules.TenDrawCount
                ? GachaEconomyRules.TenDrawCoinCost
                : GachaEconomyRules.SingleDrawCoinCost;
            if (method == GachaPaymentMethod.Ticket && tickets < ticketCost)
            {
                return GachaTransactionResult.Failed(
                    requestId,
                    "insufficient-tickets");
            }
            if (method == GachaPaymentMethod.Coin && coins < coinCost)
            {
                return GachaTransactionResult.Failed(
                    requestId,
                    "insufficient-coins");
            }

            GachaPityState pityAfter = Pity(seriesId);
            IReadOnlyList<GachaDrawOutcome> outcomes =
                GachaDrawEngine.DrawBatch(series, count, ref pityAfter, random);
            var stagedOwned = new HashSet<string>(
                ownedPrizes,
                StringComparer.Ordinal);
            var rows = new List<GachaDrawReceiptRow>(outcomes.Count);
            string preparedAt = DateTime.UtcNow.ToString(
                "O",
                CultureInfo.InvariantCulture);
            for (int index = 0; index < outcomes.Count; index++)
            {
                GachaDrawOutcome outcome = outcomes[index];
                bool isNew = stagedOwned.Add(outcome.PrizeId);
                int shards = isNew
                    ? 0
                    : GachaEconomyRules.DuplicateShardValue(outcome.Rarity);
                string firstObtained = firstObtainedAtUtcByPrize.TryGetValue(
                    outcome.PrizeId,
                    out string knownDate)
                    ? knownDate
                    : preparedAt;
                string collectibleId = collectibleIdByPrize.TryGetValue(
                    outcome.PrizeId,
                    out string knownId)
                    ? knownId
                    : GachaCollectibleId.Create(
                        requestId,
                        outcome.PrizeId,
                        index);
                rows.Add(new GachaDrawReceiptRow(
                    outcome,
                    isNew,
                    shards,
                    firstObtained,
                    collectibleId));
            }

            pendingTransaction = new GachaPendingTransaction(
                requestId,
                seriesId,
                count,
                method,
                GachaTransactionPhase.Prepared,
                pityAfter,
                ticketCost,
                coinCost,
                rows);
            Persist();
            return GachaTransactionResult.Succeeded(pendingTransaction);
        }

        public GachaTransactionResult QueryTransaction(string requestId)
        {
            if (pendingTransaction != null
                && string.Equals(
                    pendingTransaction.RequestId,
                    requestId,
                    StringComparison.Ordinal))
            {
                return GachaTransactionResult.Succeeded(pendingTransaction);
            }
            if (completedTransaction != null
                && string.Equals(
                    completedTransaction.RequestId,
                    requestId,
                    StringComparison.Ordinal))
            {
                return GachaTransactionResult.Succeeded(completedTransaction);
            }
            return GachaTransactionResult.Failed(
                requestId,
                "stale-request");
        }

        public GachaTransactionResult MarkRevealReady(string requestId)
        {
            if (pendingTransaction == null
                || !string.Equals(
                    pendingTransaction.RequestId,
                    requestId,
                    StringComparison.Ordinal))
            {
                return QueryTransaction(requestId);
            }
            if (pendingTransaction.Phase == GachaTransactionPhase.Prepared)
            {
                pendingTransaction = pendingTransaction.WithPhase(
                    GachaTransactionPhase.RevealReady);
                Persist();
            }
            return GachaTransactionResult.Succeeded(pendingTransaction);
        }

        public GachaTransactionResult AcknowledgePending(string requestId)
        {
            if (completedTransaction != null
                && string.Equals(
                    completedTransaction.RequestId,
                    requestId,
                    StringComparison.Ordinal))
            {
                return GachaTransactionResult.Succeeded(completedTransaction);
            }
            if (pendingTransaction == null
                || !string.Equals(
                    pendingTransaction.RequestId,
                    requestId,
                    StringComparison.Ordinal))
            {
                return GachaTransactionResult.Failed(
                    requestId,
                    "stale-request");
            }
            if (pendingTransaction.Phase != GachaTransactionPhase.RevealReady)
            {
                return GachaTransactionResult.Failed(
                    requestId,
                    "reveal-not-ready");
            }
            if (pendingTransaction.PaymentMethod == GachaPaymentMethod.Ticket
                && tickets < pendingTransaction.TicketCost)
            {
                return GachaTransactionResult.Failed(
                    requestId,
                    "reserved-funds-missing");
            }
            if (pendingTransaction.PaymentMethod == GachaPaymentMethod.Coin
                && coins < pendingTransaction.CoinCost)
            {
                return GachaTransactionResult.Failed(
                    requestId,
                    "reserved-funds-missing");
            }

            if (pendingTransaction.PaymentMethod == GachaPaymentMethod.Ticket)
            {
                tickets -= pendingTransaction.TicketCost;
            }
            else
            {
                coins -= pendingTransaction.CoinCost;
            }
            pityBySeries[pendingTransaction.SeriesId] =
                pendingTransaction.PityAfter;
            int shards = 0;
            for (int index = 0;
                 index < pendingTransaction.Receipt.Rows.Count;
                 index++)
            {
                GachaDrawReceiptRow row =
                    pendingTransaction.Receipt.Rows[index];
                ownedPrizes.Add(row.Outcome.PrizeId);
                firstObtainedAtUtcByPrize[row.Outcome.PrizeId] =
                    row.FirstObtainedAtUtc;
                collectibleIdByPrize[row.Outcome.PrizeId] =
                    row.CollectibleId;
                shards += row.ShardsGained;
            }
            shardsBySeries[pendingTransaction.SeriesId] =
                Shards(pendingTransaction.SeriesId) + shards;
            drawsBySeries[pendingTransaction.SeriesId] =
                TotalDraws(pendingTransaction.SeriesId)
                + pendingTransaction.Count;
            completedTransaction = pendingTransaction.WithPhase(
                GachaTransactionPhase.Completed);
            pendingTransaction = null;
            Persist();
            return GachaTransactionResult.Succeeded(completedTransaction);
        }

        public GachaDrawReceipt Draw(string seriesId, int count, GachaPaymentMethod method)
        {
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

            var owned = new List<string>(ownedPrizes);
            owned.Sort(StringComparer.Ordinal);
            GachaPendingTransaction active =
                pendingTransaction ?? completedTransaction;
            rows.Add(active == null
                ? "transaction\t\tidle"
                : string.Join(
                    "\t",
                    "transaction",
                    active.RequestId,
                    active.Phase.ToString().ToLowerInvariant()));
            rows.Add("owned\t" + string.Join("|", owned));
            return string.Join("\n", rows);
        }

        private string Key(string suffix)
        {
            return prefix + suffix;
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
            ReadMap(
                PlayerPrefs.GetString(Key("obtainedDates"), string.Empty),
                firstObtainedAtUtcByPrize);
            ReadMap(
                PlayerPrefs.GetString(Key("collectibleIds"), string.Empty),
                collectibleIdByPrize);

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

            if (!GachaTransactionCodec.TryDeserialize(
                    PlayerPrefs.GetString(
                        Key("transaction.pending"),
                        string.Empty),
                    out pendingTransaction))
            {
                pendingTransaction = null;
            }
            if (!GachaTransactionCodec.TryDeserialize(
                    PlayerPrefs.GetString(
                        Key("transaction.completed"),
                        string.Empty),
                    out completedTransaction)
                || completedTransaction.Phase
                    != GachaTransactionPhase.Completed)
            {
                completedTransaction = null;
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
            WriteMap(Key("obtainedDates"), firstObtainedAtUtcByPrize);
            WriteMap(Key("collectibleIds"), collectibleIdByPrize);
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

            WriteTransaction(Key("transaction.pending"), pendingTransaction);
            WriteTransaction(Key("transaction.completed"), completedTransaction);

            PlayerPrefs.Save();
        }

        private static void ReadMap(
            string payload,
            Dictionary<string, string> destination)
        {
            if (string.IsNullOrEmpty(payload))
            {
                return;
            }
            string[] rows = payload.Split('|');
            for (int index = 0; index < rows.Length; index++)
            {
                int separator = rows[index].IndexOf('=');
                if (separator <= 0 || separator >= rows[index].Length - 1)
                {
                    continue;
                }
                destination[rows[index].Substring(0, separator)] =
                    rows[index].Substring(separator + 1);
            }
        }

        private static void WriteMap(
            string key,
            Dictionary<string, string> source)
        {
            if (source.Count == 0)
            {
                PlayerPrefs.DeleteKey(key);
                return;
            }
            var rows = new List<string>(source.Count);
            foreach (KeyValuePair<string, string> entry in source)
            {
                rows.Add(entry.Key + "=" + entry.Value);
            }
            rows.Sort(StringComparer.Ordinal);
            PlayerPrefs.SetString(key, string.Join("|", rows));
        }

        private static void WriteTransaction(
            string key,
            GachaPendingTransaction transaction)
        {
            if (transaction == null)
            {
                PlayerPrefs.DeleteKey(key);
            }
            else
            {
                PlayerPrefs.SetString(
                    key,
                    GachaTransactionCodec.Serialize(transaction));
            }
        }

        /// <summary>Test hook: removes every key under this runtime's prefix.</summary>
        public void DeleteAllForTests()
        {
            PlayerPrefs.DeleteKey(Key("version"));
            PlayerPrefs.DeleteKey(Key("tickets"));
            PlayerPrefs.DeleteKey(Key("coins"));
            PlayerPrefs.DeleteKey(Key("rhythmWeeksCredited"));
            PlayerPrefs.DeleteKey(Key("owned"));
            PlayerPrefs.DeleteKey(Key("obtainedDates"));
            PlayerPrefs.DeleteKey(Key("collectibleIds"));
            PlayerPrefs.DeleteKey(Key("transaction.pending"));
            PlayerPrefs.DeleteKey(Key("transaction.completed"));
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
