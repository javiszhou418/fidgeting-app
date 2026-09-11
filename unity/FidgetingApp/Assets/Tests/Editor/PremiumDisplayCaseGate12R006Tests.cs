using System;
using System.Linq;
using FidgetingApp.DisplayCase;
using FidgetingApp.DisplayCase.Editor;
using FidgetingApp.Product;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    /// <summary>
    /// Gate 12 R006 A/B: slab details on top of R005. A keeps the black
    /// flocking; B lays a printed certificate card on it. Both stay
    /// candidates; the shipping factory still points at R004.
    /// </summary>
    public sealed class PremiumDisplayCaseGate12R006Tests
    {
        private static readonly string[] SharedDetails =
        {
            "LabelWellFloor", "BridgeBar", "RimEdgeHighlight", "WeldSeam",
            "ChamberGap", "ChamberWellShadow", "CornerMark", "PlateTierKeyline",
            "ChamberBezel", "BrandMarkFace", "RarityEmblem"
        };

        [TestCase(PremiumDisplayCaseGate12R006Builder.FlockingPrefabPath, false)]
        [TestCase(PremiumDisplayCaseGate12R006Builder.PaperPrefabPath, true)]
        public void VariantCarriesSlabDetailsAndOnlyPaperHasTheCard(string prefabPath, bool paper)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            Assert.That(prefab, Is.Not.Null, "run Fidgeting/Display Case/Gate 12/R006 Build Candidates");
            string[] names = prefab.GetComponentsInChildren<Transform>(true)
                .Select(t => t.name).ToArray();
            foreach (string required in SharedDetails)
            {
                Assert.That(names, Does.Contain(required));
            }
            Assert.That(names.Contains("CertificateCard"), Is.EqualTo(paper));
            foreach (string forbidden in new[] { "Explode", "Reassembl", "LayerSeparation", "Scrub" })
            {
                Assert.That(names.Any(n => n.Contains(forbidden)), Is.False, forbidden);
            }

            // Tier keyline joins the foil set so it follows rarity, and on the
            // paper variant so do the three trait bar fills.
            PremiumDisplayCaseLabelPlate plate =
                prefab.GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true);
            Assert.That(plate.IsWired, Is.True);
            Assert.That(plate.FoilRendererCount, Is.EqualTo(paper ? 9 : 6),
                "4 frame lines + divider + keyline, plus 3 trait fills on paper");

            TextMesh corner = prefab.GetComponentsInChildren<TextMesh>(true)
                .Single(t => t.name == "CornerMark");
            Assert.That(corner.text, Is.EqualTo(PremiumDisplayCaseGate12R006Builder.CornerMark));
            Assert.That(corner.color.a, Is.LessThan(0.5f), "etched, not printed");
            // Lower-right of the front shell, in front of its face (z −0.023).
            Assert.That(corner.transform.localPosition.x, Is.GreaterThan(0.06f));
            Assert.That(corner.transform.localPosition.y, Is.LessThan(-0.12f));
            Assert.That(corner.transform.localPosition.z, Is.LessThan(-0.023f));

            if (paper)
            {
                Transform card = prefab.GetComponentsInChildren<Transform>(true)
                    .Single(t => t.name == "CertificateCard");
                Transform sheet = card.Find("Paper");
                Assert.That(sheet.lossyScale.x, Is.EqualTo(0.184f).Within(1e-4f));
                Assert.That(sheet.lossyScale.y, Is.EqualTo(0.204f).Within(1e-4f));
                // 3 mm smaller than the 190x210 insert so the flocking shows as a gap.
                Assert.That(sheet.position.z, Is.LessThan(-0.0005f), "card lies on the insert face");
                TextMesh band = card.GetComponentsInChildren<TextMesh>(true)
                    .Single(t => t.name == "BandText");
                Assert.That(band.text, Is.EqualTo(PremiumDisplayCaseGate12R006Builder.CertificateBand));
                string[] printed = card.GetComponentsInChildren<TextMesh>(true)
                    .Select(t => t.text).ToArray();
                Assert.That(printed.Any(t => t.Contains("FDT-")), Is.False,
                    "certificate copy is static series print; no collectible id (R053)");
                Assert.That(names, Does.Contain("ToyContactShadow"));
            }
        }

        [Test]
        public void PaperCardPrintsTheSealedToysThreeTraits()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R006Builder.PaperPrefabPath);
            Assert.That(prefab, Is.Not.Null, "run Fidgeting/Display Case/Gate 12/R006 Build Candidates");
            PremiumDisplayCaseTraitBlock block =
                prefab.GetComponentInChildren<PremiumDisplayCaseTraitBlock>(true);
            Assert.That(block, Is.Not.Null);
            Assert.That(block.IsWired, Is.True);

            // Traits belong to the toy the preview seals, not to the draw.
            GachaPrizeDefinition prize = GachaCatalog
                .ResolvePrize(PremiumDisplayCaseGate12R006Builder.PreviewPrizeId).Value;
            ToyTalentProfile expected =
                ToyTalentCatalog.ResolveFromContentReference(prize.ContentReference);
            Assert.That(block.AppliedToyId, Is.EqualTo(expected.ToyId));

            TextMesh[] texts = prefab.GetComponentsInChildren<TextMesh>(true);
            foreach (ToyTalentAxis axis in Enum.GetValues(typeof(ToyTalentAxis)))
            {
                string label = ToyTalentCatalog.Label(axis);
                int value = expected.Value(axis);
                Assert.That(block.AppliedValue(axis), Is.EqualTo(value));
                Assert.That(
                    block.FilledFraction(axis),
                    Is.EqualTo(value / (float)ToyTalentCatalog.AxisMaximum).Within(1e-4f),
                    label + " bar length must match its printed number");
                Assert.That(
                    texts.Single(t => t.name == "Trait" + label + "Value").text,
                    Is.EqualTo(value.ToString("00")));
            }

            Assert.That(
                texts.Single(t => t.name == "TraitBudget").text,
                Is.EqualTo("210 / 300"),
                "every toy spends the same budget, so the trade-off is visible");
        }

        [Test]
        public void TraitRowsFitBetweenTheBandAndTheBottomKeyline()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R006Builder.PaperPrefabPath);
            Transform card = prefab.GetComponentsInChildren<Transform>(true)
                .Single(t => t.name == "CertificateCard");
            float bandBottom = card.Find("Band").position.y
                - card.Find("Band").lossyScale.y * 0.5f;
            float keylineTop = card.Find("KeylineBottom").position.y;

            foreach (Transform row in card.GetComponentsInChildren<Transform>(true)
                         .Where(t => t.name.StartsWith("Trait")))
            {
                Renderer renderer = row.GetComponent<Renderer>();
                if (renderer == null)
                {
                    continue;
                }
                Bounds bounds = renderer.bounds;
                Assert.That(bounds.max.y, Is.LessThan(bandBottom), row.name + " overlaps the band");
                Assert.That(bounds.min.y, Is.GreaterThan(keylineTop), row.name + " runs off the card");
                Assert.That(Mathf.Abs(bounds.center.x), Is.LessThan(0.088f),
                    row.name + " runs past the side keylines");
            }
        }

        [Test]
        public void ShippingFactoryStillPointsAtApprovedR004()
        {
            Assert.That(PremiumDisplayCaseGate12R006Builder.FlockingPrefabPath,
                Is.Not.EqualTo(PremiumDisplayCaseGate12Builder.ShippingPrefabPath));
            Assert.That(PremiumDisplayCaseGate12R006Builder.PaperPrefabPath,
                Is.Not.EqualTo(PremiumDisplayCaseGate12Builder.ShippingPrefabPath));
            GameObject r004 = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12Builder.ShippingPrefabPath);
            string[] names = r004.GetComponentsInChildren<Transform>(true).Select(t => t.name).ToArray();
            foreach (string detail in new[] { "BridgeBar", "CertificateCard", "CornerMark", "WeldSeam" })
            {
                Assert.That(names, Does.Not.Contain(detail));
            }
        }
    }
}
