using System.Linq;
using FidgetingApp.DisplayCase;
using FidgetingApp.DisplayCase.Editor;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    /// <summary>
    /// Gate 12 R005 candidate: holo graphite plate with left column + right
    /// rarity block, rarity foil tiers, chamber bezel, bottom-rim brand
    /// mark. R004 stays the shipping prefab until the user approves.
    /// </summary>
    public sealed class PremiumDisplayCaseGate12R005Tests
    {
        private static readonly string[] ForbiddenExplodeNames =
        {
            "Explode", "Reassembl", "LayerSeparation", "Scrub"
        };

        [TestCase("HEIRLOOM", PremiumDisplayCaseFoilTier.Gold)]
        [TestCase("heirloom", PremiumDisplayCaseFoilTier.Gold)]
        [TestCase("SIGNATURE", PremiumDisplayCaseFoilTier.Silver)]
        [TestCase("REFINED", PremiumDisplayCaseFoilTier.Copper)]
        [TestCase("STANDARD", PremiumDisplayCaseFoilTier.Steel)]
        [TestCase("", PremiumDisplayCaseFoilTier.Steel)]
        [TestCase(null, PremiumDisplayCaseFoilTier.Steel)]
        [TestCase("MYTHIC", PremiumDisplayCaseFoilTier.Steel)]
        public void RarityWordsMapToFixedFoilTiers(
            string rarity,
            PremiumDisplayCaseFoilTier expected)
        {
            Assert.That(PremiumDisplayCaseLabelPlate.ResolveTier(rarity), Is.EqualTo(expected));
        }

        [Test]
        public void ShippingFactoryStillPointsAtApprovedR004()
        {
            Assert.That(
                PremiumDisplayCaseGate12R005Builder.ShippingPrefabPath,
                Is.Not.EqualTo(PremiumDisplayCaseGate12Builder.ShippingPrefabPath));
            GameObject r004 = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12Builder.ShippingPrefabPath);
            Assert.That(r004, Is.Not.Null);
            Assert.That(
                r004.GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true),
                Is.Null,
                "R005 plate must not leak into the approved R004 prefab");
        }

        [Test]
        public void R005PrefabWiresPlateBezelAndBrandMarkWithoutExplodeControls()
        {
            GameObject prefab = LoadR005();
            PremiumDisplayCaseLabelPlate plate =
                prefab.GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true);
            Assert.That(plate, Is.Not.Null);
            Assert.That(plate.IsWired, Is.True);
            Assert.That(plate.LeftColumnMaxWidth,
                Is.EqualTo(PremiumDisplayCaseGate12R005Builder.LeftColumnMaxWidth).Within(1e-9f));
            Assert.That(plate.TierMaxWidth,
                Is.EqualTo(PremiumDisplayCaseGate12R005Builder.TierMaxWidth).Within(1e-9f));

            Transform[] transforms = prefab.GetComponentsInChildren<Transform>(true);
            string[] names = transforms.Select(item => item.name).ToArray();
            foreach (string required in new[]
                     {
                         "PhysicalLabel", "RarityEmblem", "PlateDivider",
                         "PlateFrameTop", "PlateFrameBottom", "PlateFrameLeft", "PlateFrameRight",
                         "ChamberBezel", "BrandMarkFace", "BrandMarkShadow"
                     })
            {
                Assert.That(names, Does.Contain(required));
            }
            foreach (string forbidden in ForbiddenExplodeNames)
            {
                Assert.That(names.Any(name => name.Contains(forbidden)), Is.False, forbidden);
            }

            Renderer label = prefab.GetComponentsInChildren<Renderer>(true)
                .Single(item => item.name == "PhysicalLabel");
            Assert.That(label.sharedMaterial.shader.name,
                Is.EqualTo("FidgetingApp/Gate12R005FoilLabel"));
            Assert.That(label.sharedMaterial.HasProperty(PremiumDisplayCaseLabelFoil.SheenPhaseId),
                Is.True, "R053 tilt driver must still reach the R005 plate");
            Renderer emblem = prefab.GetComponentsInChildren<Renderer>(true)
                .Single(item => item.name == "RarityEmblem");
            Assert.That(emblem.sharedMaterial.GetFloat("_AlphaClip"), Is.EqualTo(1f));

            TextMesh brand = prefab.GetComponentsInChildren<TextMesh>(true)
                .Single(item => item.name == "BrandMarkFace");
            Assert.That(brand.text, Is.EqualTo(PremiumDisplayCaseGate12R005Builder.BrandMark));
            // Bottom rim: tube spans y −0.152…−0.142 and its front face is z −0.0295.
            Assert.That(brand.transform.localPosition.y, Is.InRange(-0.152f, -0.142f));
            Assert.That(brand.transform.localPosition.z, Is.LessThan(-0.0295f));

            Renderer[] shells = prefab.GetComponentsInChildren<Renderer>(true)
                .Where(item => item.name.EndsWith("PolycarbonateShell")
                    || item.name == "ContinuousTubePerimeter")
                .ToArray();
            Assert.That(shells.Length, Is.EqualTo(3));
            foreach (Renderer shell in shells)
            {
                Assert.That(shell.sharedMaterial.shader.name,
                    Is.EqualTo("FidgetingApp/Gate12R005MeshClippedFrosted"), shell.name);
                Assert.That(shell.sharedMaterial.GetFloat("_Frost"), Is.GreaterThan(0f), shell.name);
            }
        }

        [Test]
        public void PlateKeepsEveryLineInsideAndTintsHeirloomGold()
        {
            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(LoadR005());
            try
            {
                var presentation = instance.GetComponent<PremiumDisplayCaseShippingPresentation>();
                PremiumDisplayCaseLabelPlate plate =
                    instance.GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true);
                TextMesh name = Text(instance, "AuthoritativeProductName");
                TextMesh tier = Text(instance, "AuthoritativeRarityLevel");
                float authoredName = name.characterSize;

                presentation.SetLabel(new PremiumDisplayCaseLabelData(
                    "GEEONE TRI-SPINNER",
                    "SATIN STEEL · DRAGON SCALE",
                    "2026-09-09",
                    "HEIRLOOM",
                    "FDT-82C77C1831AF"));
                Assert.That(plate.Tier, Is.EqualTo(PremiumDisplayCaseFoilTier.Gold));
                Assert.That(tier.color.r, Is.GreaterThan(tier.color.b + 0.3f), "gold ink");
                Assert.That(plate.MeasureWidth(name), Is.LessThanOrEqualTo(plate.LeftColumnMaxWidth));
                Assert.That(name.characterSize, Is.LessThanOrEqualTo(authoredName));

                var block = new MaterialPropertyBlock();
                Renderer emblem = instance.GetComponentsInChildren<Renderer>(true)
                    .Single(item => item.name == "RarityEmblem");
                emblem.GetPropertyBlock(block);
                Assert.That(block.GetTexture("_MainTex"), Is.SameAs(plate.Emblem));

                presentation.SetLabel(new PremiumDisplayCaseLabelData(
                    "AN UNREASONABLY LONG COLLECTIBLE PRODUCT NAME THAT MUST SHRINK",
                    "SATIN STEEL · DRAGON SCALE",
                    "2026-09-09",
                    "REFINED",
                    "FDT-82C77C1831AF"));
                Assert.That(plate.Tier, Is.EqualTo(PremiumDisplayCaseFoilTier.Copper));
                Assert.That(name.characterSize, Is.LessThan(authoredName));
                Assert.That(plate.MeasureWidth(name),
                    Is.LessThanOrEqualTo(plate.LeftColumnMaxWidth * 1.001f));

                // Shrinking is not sticky: the next short name restores size.
                presentation.SetLabel(new PremiumDisplayCaseLabelData(
                    "SHORT", "X", "2026-09-09", "STANDARD", "FDT-1"));
                Assert.That(name.characterSize, Is.EqualTo(authoredName).Within(1e-9f));
                Assert.That(plate.Tier, Is.EqualTo(PremiumDisplayCaseFoilTier.Steel));
            }
            finally
            {
                Object.DestroyImmediate(instance);
            }
        }

        private static GameObject LoadR005()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R005Builder.ShippingPrefabPath);
            Assert.That(prefab, Is.Not.Null, "run Fidgeting/Display Case/Gate 12/R005 Build Candidate");
            return prefab;
        }

        private static TextMesh Text(GameObject root, string name)
        {
            return root.GetComponentsInChildren<TextMesh>(true).Single(item => item.name == name);
        }
    }
}
