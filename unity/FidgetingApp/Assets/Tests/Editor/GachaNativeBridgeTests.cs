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
                        40)
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
                "0")));
        }

        [Test]
        public void TransactionReceiptsAppendEnglishPlateCopyAfterCollectibleId()
        {
            GachaPrizeDefinition prize = GachaCatalog.ResolvePrize(
                "canyon-heir-metal-three-blade").Value;
            var receipt = new GachaDrawReceipt(
                true,
                string.Empty,
                new List<GachaDrawReceiptRow>
                {
                    new GachaDrawReceiptRow(
                        new GachaDrawOutcome(prize.Id, GachaRarity.Heirloom,
                            false, false, false),
                        true,
                        0,
                        "2026-09-09T10:58:00.0000000Z",
                        "FDT-R053")
                });

            string[] cells = GachaNativeBridge.ReceiptPayload(receipt, "req-r053")
                .Split('\n')[1].Split('\t');
            // Swift parses cells[12]/[13] only when 14 cells are present.
            Assert.That(cells.Length, Is.EqualTo(14));
            Assert.That(cells[10], Is.EqualTo("2026-09-09T10:58:00.0000000Z"));
            Assert.That(cells[11], Is.EqualTo("FDT-R053"));
            Assert.That(cells[12], Is.EqualTo("GEEONE TRI-SPINNER"));
            Assert.That(cells[13], Is.EqualTo("SATIN STEEL · DRAGON SCALE"));
            Assert.That(
                GachaNativeBridge.ReceiptPayload(receipt).Split('\n')[1].Split('\t').Length,
                Is.EqualTo(10),
                "non-transaction receipts keep the legacy 10-cell row");
        }
    }
}
