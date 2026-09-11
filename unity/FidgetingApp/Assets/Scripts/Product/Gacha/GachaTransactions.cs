using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.Product.Gacha
{
    public enum GachaTransactionPhase
    {
        Prepared = 0,
        RevealReady = 1,
        Completed = 2
    }

    public sealed class GachaPendingTransaction
    {
        internal GachaPendingTransaction(
            string requestId,
            string seriesId,
            int count,
            GachaPaymentMethod paymentMethod,
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
                phase,
                PityAfter,
                TicketCost,
                CoinCost,
                Receipt.Rows);
        }
    }

    public readonly struct GachaTransactionResult
    {
        private GachaTransactionResult(
            string requestId,
            bool success,
            string failureReason,
            GachaPendingTransaction transaction)
        {
            RequestId = requestId ?? string.Empty;
            Success = success;
            FailureReason = failureReason ?? string.Empty;
            Transaction = transaction;
        }

        public string RequestId { get; }
        public bool Success { get; }
        public string FailureReason { get; }
        public GachaPendingTransaction Transaction { get; }
        public GachaDrawReceipt Receipt => Success && Transaction != null
            ? Transaction.Receipt
            : GachaDrawReceipt.Failure(FailureReason);

        internal static GachaTransactionResult Succeeded(
            GachaPendingTransaction transaction)
        {
            return new GachaTransactionResult(
                transaction.RequestId,
                true,
                string.Empty,
                transaction);
        }

        internal static GachaTransactionResult Failed(
            string requestId,
            string failureReason)
        {
            return new GachaTransactionResult(
                requestId,
                false,
                failureReason,
                null);
        }
    }

    internal static class GachaTransactionCodec
    {
        private const int SchemaVersion = 1;

        [Serializable]
        private sealed class StoredTransaction
        {
            public int schemaVersion;
            public string requestId;
            public string seriesId;
            public int count;
            public int paymentMethod;
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
            public string firstObtainedAtUtc;
            public string collectibleId;
        }

        public static string Serialize(GachaPendingTransaction transaction)
        {
            if (transaction == null)
            {
                return string.Empty;
            }
            var stored = new StoredTransaction
            {
                schemaVersion = SchemaVersion,
                requestId = transaction.RequestId,
                seriesId = transaction.SeriesId,
                count = transaction.Count,
                paymentMethod = (int)transaction.PaymentMethod,
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
                    firstObtainedAtUtc = row.FirstObtainedAtUtc,
                    collectibleId = row.CollectibleId
                });
            }
            return JsonUtility.ToJson(stored);
        }

        public static bool TryDeserialize(
            string payload,
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
                || stored.schemaVersion != SchemaVersion
                || !IsRequestIdValid(stored.requestId)
                || string.IsNullOrEmpty(stored.seriesId)
                || stored.count < 1
                || stored.rows == null
                || stored.rows.Count != stored.count
                || stored.paymentMethod < (int)GachaPaymentMethod.Ticket
                || stored.paymentMethod > (int)GachaPaymentMethod.Coin
                || stored.phase < (int)GachaTransactionPhase.Prepared
                || stored.phase > (int)GachaTransactionPhase.Completed)
            {
                return false;
            }

            var rows = new List<GachaDrawReceiptRow>(stored.rows.Count);
            for (int index = 0; index < stored.rows.Count; index++)
            {
                StoredRow row = stored.rows[index];
                if (row == null
                    || string.IsNullOrEmpty(row.prizeId)
                    || row.rarity < (int)GachaRarity.Standard
                    || row.rarity > (int)GachaRarity.Heirloom
                    || string.IsNullOrEmpty(row.firstObtainedAtUtc)
                    || string.IsNullOrEmpty(row.collectibleId))
                {
                    return false;
                }
                rows.Add(new GachaDrawReceiptRow(
                    new GachaDrawOutcome(
                        row.prizeId,
                        (GachaRarity)row.rarity,
                        row.forcedBySignaturePity,
                        row.forcedByHeirloomPity,
                        row.forcedByTenDraw),
                    row.isNew,
                    row.shardsGained,
                    row.firstObtainedAtUtc,
                    row.collectibleId));
            }

            transaction = new GachaPendingTransaction(
                stored.requestId,
                stored.seriesId,
                stored.count,
                (GachaPaymentMethod)stored.paymentMethod,
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
            if (string.IsNullOrWhiteSpace(requestId) || requestId.Length > 128)
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

    public static class GachaCollectibleId
    {
        public static string Create(
            string requestId,
            string prizeId,
            int rowIndex)
        {
            string source = (requestId ?? string.Empty)
                + "|"
                + (prizeId ?? string.Empty)
                + "|"
                + rowIndex;
            const ulong offset = 14695981039346656037UL;
            const ulong prime = 1099511628211UL;
            ulong hash = offset;
            for (int index = 0; index < source.Length; index++)
            {
                hash ^= source[index];
                hash *= prime;
            }
            return "FDT-" + hash.ToString("X12");
        }
    }
}
