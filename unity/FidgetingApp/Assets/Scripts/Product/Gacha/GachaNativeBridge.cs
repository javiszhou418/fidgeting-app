using System;
using System.Collections.Generic;
using System.Globalization;
#if UNITY_IOS && !UNITY_EDITOR
using System.Runtime.InteropServices;
#endif

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Publishes gacha state to the SwiftUI shell, mirroring the other
    /// Codex*ReceiveState bridges: Unity is the single source of truth and
    /// pushes TSV payloads after every state change.
    /// </summary>
    public static class GachaNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexGachaReceiveState(
            string catalogPayload,
            string snapshotPayload,
            string receiptPayload);
#endif

        public static void Publish(
            string catalogPayload,
            string snapshotPayload,
            string receiptPayload)
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexGachaReceiveState(
                catalogPayload ?? string.Empty,
                snapshotPayload ?? string.Empty,
                receiptPayload ?? string.Empty);
#endif
        }

        /// <summary>
        /// TSV receipt rows for the native results panel. First row is
        /// "result\tok" or "result\t&lt;failure-reason&gt;"; each prize row
        /// carries rarity, kind, newness, shard conversion, and every
        /// guarantee flag so the UI can label pity wins honestly.
        /// </summary>
        public static string ReceiptPayload(GachaDrawReceipt receipt)
        {
            var rows = new List<string>();
            AppendReceiptRows(rows, receipt);
            return string.Join("\n", rows);
        }

        /// <summary>
        /// Transaction-aware receipt. Metadata precedes the legacy result/row
        /// block so native retry, resume, and acceptance handling never need to
        /// infer mode or lifecycle phase from UI state.
        /// </summary>
        public static string ReceiptPayload(GachaTransactionResult result)
        {
            var rows = new List<string>
            {
                "runtime-mode\t" + RuntimeModeToken(result.RuntimeMode)
            };
            if (result.Success && result.Transaction != null)
            {
                rows.Add(string.Join(
                    "\t",
                    "transaction",
                    result.Transaction.RequestId,
                    PhaseToken(result.Transaction.Phase),
                    result.Transaction.SeriesId,
                    result.Transaction.Count.ToString(CultureInfo.InvariantCulture),
                    PaymentToken(result.Transaction.PaymentMethod)));
                AppendReceiptRows(rows, result.Transaction.Receipt);
            }
            else
            {
                rows.Add(string.Join(
                    "\t",
                    "transaction",
                    result.RequestId,
                    "failed",
                    string.Empty,
                    "0",
                    "ticket"));
                AppendReceiptRows(rows, GachaDrawReceipt.Failure(result.FailureReason));
            }

            return string.Join("\n", rows);
        }

        internal static void AppendReceiptRows(
            List<string> rows,
            GachaDrawReceipt receipt)
        {
            rows.Add("result\t" + (receipt.Success ? "ok" : receipt.FailureReason));
            IReadOnlyList<GachaDrawReceiptRow> receiptRows =
                receipt.Rows ?? Array.Empty<GachaDrawReceiptRow>();
            for (int index = 0; index < receiptRows.Count; index++)
            {
                GachaDrawReceiptRow row = receiptRows[index];
                GachaPrizeDefinition? prize = GachaCatalog.ResolvePrize(row.Outcome.PrizeId);
                rows.Add(string.Join(
                    "\t",
                    "row",
                    row.Outcome.PrizeId,
                    prize.HasValue ? prize.Value.DisplayName : row.Outcome.PrizeId,
                    ((int)row.Outcome.Rarity).ToString(CultureInfo.InvariantCulture),
                    prize.HasValue
                        ? ((int)prize.Value.Kind).ToString(CultureInfo.InvariantCulture)
                        : "0",
                    row.IsNew ? "1" : "0",
                    row.ShardsGained.ToString(CultureInfo.InvariantCulture),
                    row.Outcome.ForcedBySignaturePity ? "1" : "0",
                    row.Outcome.ForcedByHeirloomPity ? "1" : "0",
                    row.Outcome.ForcedByTenDraw ? "1" : "0"));
            }
        }

        public static string RuntimeModeToken(GachaRuntimeMode mode)
        {
            return mode == GachaRuntimeMode.InternalUnlimited
                ? "internalUnlimited"
                : "production";
        }

        public static string PhaseToken(GachaTransactionPhase phase)
        {
            return phase switch
            {
                GachaTransactionPhase.AwaitingAcceptance => "awaitingAcceptance",
                GachaTransactionPhase.Completed => "completed",
                _ => "prepared"
            };
        }

        public static string PaymentToken(GachaPaymentMethod method)
        {
            return method == GachaPaymentMethod.Coin ? "coin" : "ticket";
        }
    }
}
