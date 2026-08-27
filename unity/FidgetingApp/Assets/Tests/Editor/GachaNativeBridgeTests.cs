using System.Collections.Generic;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaNativeBridgeTests
    {
        [Test]
        public void FailureReceiptsSerializeTheReasonAndNoRows()
        {
            string payload = GachaNativeBridge.ReceiptPayload(
                GachaDrawReceipt.Failure("insufficient-tickets"));
            Assert.That(payload, Is.EqualTo("result\tinsufficient-tickets"));
        }

        [Test]
        public void SuccessReceiptsCarryRarityKindNewnessShardsAndGuaranteeFlags()
        {
            GachaSeriesDefinition series =
                GachaCatalog.ResolveSeries(GachaCatalog.LaunchSeriesId);
            GachaPrizeDefinition heirloom = series.PrizesOfRarity(GachaRarity.Heirloom)[0];
            var receipt = new GachaDrawReceipt(
                true,
                string.Empty,
                new List<GachaDrawReceiptRow>
                {
                    new GachaDrawReceiptRow(
                        new GachaDrawOutcome(heirloom.Id, GachaRarity.Heirloom,
                            false, true, false),
                        false,
                        40,
                        "2026-08-17T07:12:30.0000000Z")
                });

            string payload = GachaNativeBridge.ReceiptPayload(receipt);
            string[] lines = payload.Split('\n');
            Assert.That(lines[0], Is.EqualTo("result\tok"));
            Assert.That(lines[1], Is.EqualTo(string.Join(
                "\t",
                "row",
                heirloom.Id,
                heirloom.DisplayName,
                "3",
                ((int)heirloom.Kind).ToString(),
                "0",
                "40",
                "0",
                "1",
                "0",
                "2026-08-17T07:12:30.0000000Z")));
        }

        [Test]
        public void RequestScopedReceiptCarriesStableExactlyOnceRequestId()
        {
            const string requestId = "2fd82871-0797-4a11-a910-a6573ffe7227";
            string payload = GachaNativeBridge.ReceiptPayload(
                requestId,
                GachaDrawReceipt.Failure("draw-already-pending"));
            Assert.That(payload,
                Is.EqualTo("result\t" + requestId + "\tdraw-already-pending"));
        }
    }
}
