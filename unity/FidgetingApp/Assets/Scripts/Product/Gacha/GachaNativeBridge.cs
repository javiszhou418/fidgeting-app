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
            var rows = new List<string>
            {
                "result\t" + (receipt.Success ? "ok" : receipt.FailureReason)
            };
            for (int index = 0; index < receipt.Rows.Count; index++)
            {
                GachaDrawReceiptRow row = receipt.Rows[index];
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

            return string.Join("\n", rows);
        }
    }
}
