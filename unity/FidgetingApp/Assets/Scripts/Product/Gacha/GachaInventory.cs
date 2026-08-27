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
            : this(outcome, isNew, shardsGained, string.Empty)
        {
        }

        public GachaDrawReceiptRow(
            GachaDrawOutcome outcome,
            bool isNew,
            int shardsGained,
            string firstObtainedAtUtc)
        {
            Outcome = outcome;
            IsNew = isNew;
            ShardsGained = Math.Max(0, shardsGained);
            FirstObtainedAtUtc = firstObtainedAtUtc ?? string.Empty;
        }

        public GachaDrawOutcome Outcome { get; }
        public bool IsNew { get; }
        public int ShardsGained { get; }
        public string FirstObtainedAtUtc { get; }
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
        public const string DevelopmentPreviewFundingToken =
            "metal-three-blade-v1";
        private const string DevelopmentPreviewFundingKey =
            "developmentPreviewFunding.metalThreeBladeV1";

        private readonly string prefix;
        private readonly IGachaRandom random;
        private readonly Func<DateTime> utcNow;
        private readonly HashSet<string> ownedPrizes = new HashSet<string>(StringComparer.Ordinal);
        private readonly Dictionary<string, string> firstObtainedAtUtcByPrize =
            new Dictionary<string, string>(StringComparer.Ordinal);
        private readonly Dictionary<string, GachaPityState> pityBySeries =
            new Dictionary<string, GachaPityState>(StringComparer.Ordinal);
        private readonly Dictionary<string, int> shardsBySeries =
            new Dictionary<string, int>(StringComparer.Ordinal);
        private readonly Dictionary<string, int> drawsBySeries =
            new Dictionary<string, int>(StringComparer.Ordinal);

        private int tickets;
        private int coins;
        private string pendingRequestId = string.Empty;
        private string pendingSeriesId = string.Empty;
        private int pendingCount;
        private GachaPaymentMethod pendingPaymentMethod;
        private GachaDrawReceipt pendingReceipt;
        private bool hasPendingReceipt;

        public GachaInventoryRuntime(
            string storagePrefix = DefaultPrefix,
            IGachaRandom randomSource = null,
            Func<DateTime> utcNowProvider = null)
        {
            prefix = string.IsNullOrEmpty(storagePrefix) ? DefaultPrefix : storagePrefix;
            random = randomSource ?? new GachaSplitMix64(
                (ulong)Environment.TickCount * 0x9E3779B97F4A7C15UL + 0xD1B54A32D192ED03UL);
            utcNow = utcNowProvider ?? (() => DateTime.UtcNow);
            Load();
        }

        public int Tickets => tickets;
        public int Coins => coins;

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
        public string PendingRequestId => hasPendingReceipt
            ? pendingRequestId
            : string.Empty;

        /// <summary>
        /// Returns the authoritative first-obtained timestamp captured when a
        /// prize was actually awarded. Migrated v1 ownership intentionally has
        /// no timestamp: the UI must render an unknown marker instead of
        /// inventing today's date.
        /// </summary>
        public string FirstObtainedAtUtc(string prizeId)
        {
            return firstObtainedAtUtcByPrize.TryGetValue(
                prizeId ?? string.Empty,
                out string value)
                ? value
                : string.Empty;
        }

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

        /// <summary>
        /// Credits one real ticket for deterministic Development evidence.
        /// Both the runtime build flag and the exact launch token are required;
        /// a persisted marker makes the grant one-shot across app restarts.
        /// The subsequent draw still uses the normal payment, pity, ownership
        /// and durable receipt transaction.
        /// </summary>
        public bool CreditDevelopmentPreviewTicketOnce(
            string token,
            bool isDebugBuild)
        {
            if (!isDebugBuild
                || !string.Equals(
                    token,
                    DevelopmentPreviewFundingToken,
                    StringComparison.Ordinal)
                || PlayerPrefs.GetInt(
                    Key(DevelopmentPreviewFundingKey),
                    0) == 1)
            {
                return false;
            }

            tickets += GachaEconomyRules.SingleDrawTicketCost;
            PlayerPrefs.SetInt(Key(DevelopmentPreviewFundingKey), 1);
            Persist();
            return true;
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

        public GachaDrawReceipt Draw(string seriesId, int count, GachaPaymentMethod method)
        {
            return DrawInternal(seriesId, count, method, true);
        }

        private GachaDrawReceipt DrawInternal(
            string seriesId,
            int count,
            GachaPaymentMethod method,
            bool saveImmediately)
        {
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
                string firstObtainedAtUtc = FirstObtainedAtUtc(outcome.PrizeId);
                int shardsGained = 0;
                if (isNew)
                {
                    firstObtainedAtUtc = RecordFirstObtainedAtUtc(outcome.PrizeId);
                }
                else
                {
                    shardsGained = GachaEconomyRules.DuplicateShardValue(outcome.Rarity);
                    shardsGainedTotal += shardsGained;
                }

                rows.Add(new GachaDrawReceiptRow(
                    outcome,
                    isNew,
                    shardsGained,
                    firstObtainedAtUtc));
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
            Persist(saveImmediately);
            return new GachaDrawReceipt(true, string.Empty, rows);
        }

        /// <summary>
        /// Idempotent native draw entry. A request id is charged and rolled at
        /// most once; duplicate delivery returns the persisted receipt. Only one
        /// unacknowledged native request may exist because the shipping UI only
        /// exposes single draw and blocks a second flow until reveal handoff.
        /// </summary>
        public GachaDrawReceipt DrawOnce(
            string requestId,
            string seriesId,
            int count,
            GachaPaymentMethod method)
        {
            string normalizedRequestId = (requestId ?? string.Empty).ToLowerInvariant();
            if (!Guid.TryParseExact(normalizedRequestId, "D", out _))
            {
                return GachaDrawReceipt.Failure("invalid-request-id");
            }

            if (hasPendingReceipt)
            {
                if (!string.Equals(
                        pendingRequestId,
                        normalizedRequestId,
                        StringComparison.Ordinal))
                {
                    return GachaDrawReceipt.Failure("draw-already-pending");
                }
                if (!string.Equals(pendingSeriesId, seriesId, StringComparison.Ordinal)
                    || pendingCount != count
                    || pendingPaymentMethod != method)
                {
                    return GachaDrawReceipt.Failure("request-id-conflict");
                }
                return pendingReceipt;
            }

            // Inventory and its durable receipt are staged into PlayerPrefs and
            // committed with one Save. A process interruption therefore sees
            // either neither side or both sides of the authoritative draw.
            GachaDrawReceipt receipt = DrawInternal(
                seriesId,
                count,
                method,
                false);
            pendingRequestId = normalizedRequestId;
            pendingSeriesId = seriesId ?? string.Empty;
            pendingCount = count;
            pendingPaymentMethod = method;
            pendingReceipt = receipt;
            hasPendingReceipt = true;
            PersistPendingReceipt(false);
            PlayerPrefs.Save();
            return receipt;
        }

        /// <summary>
        /// Deterministic authoritative preview path. The coordinator exposes
        /// it only when Debug.isDebugBuild is true. It performs the same funds,
        /// ownership, pity, persistence and exactly-once receipt transaction as
        /// shipping DrawOnce; only the prize roll is controlled for evidence.
        /// </summary>
        public GachaDrawReceipt DrawOnceForDevelopmentPreview(
            string requestId,
            string seriesId,
            GachaPaymentMethod method,
            string forcedPrizeId)
        {
            string normalizedRequestId = (requestId ?? string.Empty).ToLowerInvariant();
            if (!Guid.TryParseExact(normalizedRequestId, "D", out _))
            {
                return GachaDrawReceipt.Failure("invalid-request-id");
            }
            if (hasPendingReceipt)
            {
                return DrawOnce(normalizedRequestId, seriesId, 1, method);
            }

            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(seriesId);
            GachaPrizeDefinition? resolved = GachaCatalog.ResolvePrize(forcedPrizeId);
            if (series == null
                || !resolved.HasValue
                || !string.Equals(
                    resolved.Value.SeriesId,
                    seriesId,
                    StringComparison.Ordinal))
            {
                return GachaDrawReceipt.Failure("unknown-preview-prize");
            }

            int cost = method == GachaPaymentMethod.Ticket
                ? GachaEconomyRules.SingleDrawTicketCost
                : GachaEconomyRules.SingleDrawCoinCost;
            int balance = method == GachaPaymentMethod.Ticket ? tickets : coins;
            if (balance < cost)
            {
                return GachaDrawReceipt.Failure(method == GachaPaymentMethod.Ticket
                    ? "insufficient-tickets"
                    : "insufficient-coins");
            }

            GachaPrizeDefinition prize = resolved.Value;
            GachaPityState pity = Pity(seriesId);
            pity.SignatureMisses = prize.Rarity >= GachaRarity.Signature
                ? 0
                : pity.SignatureMisses + 1;
            pity.HeirloomMisses = prize.Rarity == GachaRarity.Heirloom
                ? 0
                : pity.HeirloomMisses + 1;
            pityBySeries[seriesId] = pity;

            bool isNew = ownedPrizes.Add(prize.Id);
            string obtainedAt = isNew
                ? RecordFirstObtainedAtUtc(prize.Id)
                : FirstObtainedAtUtc(prize.Id);
            int shardsGained = isNew
                ? 0
                : GachaEconomyRules.DuplicateShardValue(prize.Rarity);
            if (method == GachaPaymentMethod.Ticket)
            {
                tickets -= cost;
            }
            else
            {
                coins -= cost;
            }
            shardsBySeries[seriesId] = Shards(seriesId) + shardsGained;
            drawsBySeries[seriesId] = TotalDraws(seriesId) + 1;

            var outcome = new GachaDrawOutcome(
                prize.Id,
                prize.Rarity,
                false,
                false,
                false);
            var row = new GachaDrawReceiptRow(
                outcome,
                isNew,
                shardsGained,
                obtainedAt);
            var receipt = new GachaDrawReceipt(
                true,
                string.Empty,
                new[] { row });

            pendingRequestId = normalizedRequestId;
            pendingSeriesId = seriesId;
            pendingCount = 1;
            pendingPaymentMethod = method;
            pendingReceipt = receipt;
            hasPendingReceipt = true;
            Persist(false);
            PersistPendingReceipt(false);
            PlayerPrefs.Save();
            return receipt;
        }

        public bool TryGetPendingReceipt(
            string requestId,
            out GachaDrawReceipt receipt)
        {
            string normalizedRequestId = (requestId ?? string.Empty).ToLowerInvariant();
            if (hasPendingReceipt
                && string.Equals(
                    pendingRequestId,
                    normalizedRequestId,
                    StringComparison.Ordinal))
            {
                receipt = pendingReceipt;
                return true;
            }
            receipt = default;
            return false;
        }

        public bool AcknowledgePendingReceipt(string requestId)
        {
            if (!hasPendingReceipt
                || !string.Equals(
                    pendingRequestId,
                    (requestId ?? string.Empty).ToLowerInvariant(),
                    StringComparison.Ordinal))
            {
                return false;
            }
            ClearPendingReceipt();
            PlayerPrefs.Save();
            return true;
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
            RecordFirstObtainedAtUtc(prize.Id);
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
            for (int index = 0; index < owned.Count; index++)
            {
                string prizeId = owned[index];
                string firstObtainedAtUtc = FirstObtainedAtUtc(prizeId);
                if (!string.IsNullOrEmpty(firstObtainedAtUtc))
                {
                    rows.Add(string.Join(
                        "\t",
                        "owned-meta",
                        prizeId,
                        firstObtainedAtUtc));
                }
            }
            rows.Add("owned\t" + string.Join("|", owned));
            return string.Join("\n", rows);
        }

        private string RecordFirstObtainedAtUtc(string prizeId)
        {
            string normalizedPrizeId = prizeId ?? string.Empty;
            if (string.IsNullOrEmpty(normalizedPrizeId))
            {
                return string.Empty;
            }
            if (firstObtainedAtUtcByPrize.TryGetValue(
                    normalizedPrizeId,
                    out string existing))
            {
                return existing;
            }

            DateTime now = utcNow();
            DateTime normalized = now.Kind == DateTimeKind.Utc
                ? now
                : now.ToUniversalTime();
            string value = normalized.ToString("O", CultureInfo.InvariantCulture);
            firstObtainedAtUtcByPrize[normalizedPrizeId] = value;
            return value;
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

            string firstObtained = PlayerPrefs.GetString(
                Key("firstObtainedAtUtc"),
                string.Empty);
            if (!string.IsNullOrEmpty(firstObtained))
            {
                foreach (string row in firstObtained.Split('|'))
                {
                    int separator = row.IndexOf('=');
                    if (separator <= 0 || separator >= row.Length - 1)
                    {
                        continue;
                    }
                    string prizeId = row.Substring(0, separator);
                    string timestamp = row.Substring(separator + 1);
                    if (!ownedPrizes.Contains(prizeId)
                        || !DateTime.TryParseExact(
                            timestamp,
                            "O",
                            CultureInfo.InvariantCulture,
                            DateTimeStyles.RoundtripKind,
                            out DateTime parsed))
                    {
                        continue;
                    }
                    DateTime normalized = parsed.Kind == DateTimeKind.Utc
                        ? parsed
                        : parsed.ToUniversalTime();
                    firstObtainedAtUtcByPrize[prizeId] = normalized.ToString(
                        "O",
                        CultureInfo.InvariantCulture);
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

            LoadPendingReceipt();

            if (version < SchemaVersion)
            {
                // v1 carried ownership without acquisition timestamps. Do not
                // backfill with migration time because that would create a
                // false physical-label date.
                PlayerPrefs.SetInt(Key("version"), SchemaVersion);
                PlayerPrefs.Save();
            }
        }

        private void LoadPendingReceipt()
        {
            if (PlayerPrefs.GetInt(Key("pending.exists"), 0) != 1)
            {
                return;
            }

            string requestId = PlayerPrefs.GetString(
                Key("pending.requestId"), string.Empty).ToLowerInvariant();
            string seriesId = PlayerPrefs.GetString(
                Key("pending.seriesId"), string.Empty);
            int count = PlayerPrefs.GetInt(Key("pending.count"), 0);
            int methodRaw = PlayerPrefs.GetInt(Key("pending.method"), -1);
            if (!Guid.TryParseExact(requestId, "D", out _)
                || string.IsNullOrEmpty(seriesId)
                || count <= 0
                || !Enum.IsDefined(typeof(GachaPaymentMethod), methodRaw))
            {
                ClearPendingReceipt();
                return;
            }

            bool success = PlayerPrefs.GetInt(Key("pending.success"), 0) == 1;
            string failure = PlayerPrefs.GetString(
                Key("pending.failure"), string.Empty);
            var rows = new List<GachaDrawReceiptRow>();
            string rowsPayload = PlayerPrefs.GetString(
                Key("pending.rows"), string.Empty);
            if (!string.IsNullOrEmpty(rowsPayload))
            {
                foreach (string line in rowsPayload.Split('\n'))
                {
                    string[] cells = line.Split('\t');
                    if (cells.Length < 8
                        || !int.TryParse(cells[1], NumberStyles.Integer,
                            CultureInfo.InvariantCulture, out int rarityRaw)
                        || !Enum.IsDefined(typeof(GachaRarity), rarityRaw)
                        || !int.TryParse(cells[3], NumberStyles.Integer,
                            CultureInfo.InvariantCulture, out int shards))
                    {
                        ClearPendingReceipt();
                        return;
                    }
                    rows.Add(new GachaDrawReceiptRow(
                        new GachaDrawOutcome(
                            cells[0],
                            (GachaRarity)rarityRaw,
                            cells[4] == "1",
                            cells[5] == "1",
                            cells[6] == "1"),
                        cells[2] == "1",
                        shards,
                        cells[7]));
                }
            }

            pendingRequestId = requestId;
            pendingSeriesId = seriesId;
            pendingCount = count;
            pendingPaymentMethod = (GachaPaymentMethod)methodRaw;
            pendingReceipt = new GachaDrawReceipt(success, failure, rows);
            hasPendingReceipt = true;
        }

        private void PersistPendingReceipt(bool saveImmediately = true)
        {
            PlayerPrefs.SetInt(Key("pending.exists"), hasPendingReceipt ? 1 : 0);
            PlayerPrefs.SetString(Key("pending.requestId"), pendingRequestId);
            PlayerPrefs.SetString(Key("pending.seriesId"), pendingSeriesId);
            PlayerPrefs.SetInt(Key("pending.count"), pendingCount);
            PlayerPrefs.SetInt(Key("pending.method"), (int)pendingPaymentMethod);
            PlayerPrefs.SetInt(Key("pending.success"), pendingReceipt.Success ? 1 : 0);
            PlayerPrefs.SetString(
                Key("pending.failure"),
                pendingReceipt.FailureReason ?? string.Empty);
            var rowPayloads = new List<string>();
            for (int index = 0; index < pendingReceipt.Rows.Count; index++)
            {
                GachaDrawReceiptRow row = pendingReceipt.Rows[index];
                rowPayloads.Add(string.Join(
                    "\t",
                    row.Outcome.PrizeId,
                    ((int)row.Outcome.Rarity).ToString(CultureInfo.InvariantCulture),
                    row.IsNew ? "1" : "0",
                    row.ShardsGained.ToString(CultureInfo.InvariantCulture),
                    row.Outcome.ForcedBySignaturePity ? "1" : "0",
                    row.Outcome.ForcedByHeirloomPity ? "1" : "0",
                    row.Outcome.ForcedByTenDraw ? "1" : "0",
                    row.FirstObtainedAtUtc));
            }
            PlayerPrefs.SetString(Key("pending.rows"), string.Join("\n", rowPayloads));
            if (saveImmediately)
            {
                PlayerPrefs.Save();
            }
        }

        private void ClearPendingReceipt()
        {
            pendingRequestId = string.Empty;
            pendingSeriesId = string.Empty;
            pendingCount = 0;
            pendingPaymentMethod = default;
            pendingReceipt = default;
            hasPendingReceipt = false;
            PlayerPrefs.DeleteKey(Key("pending.exists"));
            PlayerPrefs.DeleteKey(Key("pending.requestId"));
            PlayerPrefs.DeleteKey(Key("pending.seriesId"));
            PlayerPrefs.DeleteKey(Key("pending.count"));
            PlayerPrefs.DeleteKey(Key("pending.method"));
            PlayerPrefs.DeleteKey(Key("pending.success"));
            PlayerPrefs.DeleteKey(Key("pending.failure"));
            PlayerPrefs.DeleteKey(Key("pending.rows"));
        }

        private void Persist(bool saveImmediately = true)
        {
            PlayerPrefs.SetInt(Key("version"), SchemaVersion);
            PlayerPrefs.SetInt(Key("tickets"), tickets);
            PlayerPrefs.SetInt(Key("coins"), coins);
            PlayerPrefs.SetInt(Key("rhythmWeeksCredited"), RhythmWeeksCredited);
            var owned = new List<string>(ownedPrizes);
            owned.Sort(StringComparer.Ordinal);
            PlayerPrefs.SetString(Key("owned"), string.Join("|", owned));
            var firstObtainedRows = new List<string>();
            for (int index = 0; index < owned.Count; index++)
            {
                string prizeId = owned[index];
                if (firstObtainedAtUtcByPrize.TryGetValue(
                        prizeId,
                        out string timestamp)
                    && !string.IsNullOrEmpty(timestamp))
                {
                    firstObtainedRows.Add(prizeId + "=" + timestamp);
                }
            }
            PlayerPrefs.SetString(
                Key("firstObtainedAtUtc"),
                string.Join("|", firstObtainedRows));
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

            if (saveImmediately)
            {
                PlayerPrefs.Save();
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
            PlayerPrefs.DeleteKey(Key("firstObtainedAtUtc"));
            PlayerPrefs.DeleteKey(Key(DevelopmentPreviewFundingKey));
            ClearPendingReceipt();
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
