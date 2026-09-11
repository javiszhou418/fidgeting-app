using System.Linq;
using FidgetingApp.DisplayCase;
using FidgetingApp.DisplayCase.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    /// <summary>
    /// Gate 12 R007 A/B: the rarity block as die-struck sandblasted foil.
    /// A puts the relief on its own plaque, B cuts it into the plate. Both
    /// stay candidates; the shipping factory still points at R004.
    /// </summary>
    public sealed class PremiumDisplayCaseGate12R007Tests
    {
        private const float Mm = 0.00001f;

        [TestCase(PremiumDisplayCaseGate12R007Builder.PlaquePrefabPath, true)]
        [TestCase(PremiumDisplayCaseGate12R007Builder.ReliefPrefabPath, false)]
        public void ReliefUsesSandblastFoilAndOnlyAHasThePlaque(string prefabPath, bool plaqueVariant)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            Assert.That(prefab, Is.Not.Null, "run Fidgeting/Display Case/Gate 12/R007 Build Candidates");
            string[] names = prefab.GetComponentsInChildren<Transform>(true).Select(t => t.name).ToArray();
            foreach (string forbidden in new[] { "Explode", "Reassembl", "LayerSeparation", "Scrub" })
            {
                Assert.That(names.Any(n => n.Contains(forbidden)), Is.False, forbidden);
            }
            // R006 slab details survive underneath.
            foreach (string inherited in new[] { "LabelWellFloor", "BridgeBar", "PlateTierKeyline", "CornerMark" })
            {
                Assert.That(names, Does.Contain(inherited));
            }

            MeshRenderer[] renderers = prefab.GetComponentsInChildren<MeshRenderer>(true);
            MeshRenderer emblem = renderers.Single(r => r.name == "RarityEmblem");
            MeshRenderer tier = renderers.Single(r => r.name == "AuthoritativeRarityLevel");
            Assert.That(emblem.sharedMaterial.shader.name, Is.EqualTo(PremiumDisplayCaseGate12R007Builder.ShaderName));
            Assert.That(tier.sharedMaterial.shader.name, Is.EqualTo(PremiumDisplayCaseGate12R007Builder.ShaderName));
            Assert.That(emblem.sharedMaterial.GetTexture("_GrainTex"), Is.Not.Null, "bead-blast grain");
            // Relief needs a visible bevel: authored in metres, sub-millimetre.
            Assert.That(emblem.sharedMaterial.GetFloat("_BevelWidth"), Is.InRange(0.0001f, 0.0006f));
            Assert.That(tier.sharedMaterial.GetFloat("_BevelHeight"), Is.GreaterThan(1f));
            // Emblem above, tier word below, both on the block axis.
            Assert.That(emblem.transform.localPosition.x, Is.EqualTo(tier.transform.localPosition.x).Within(1e-7f));
            Assert.That(emblem.transform.localPosition.z, Is.LessThan(tier.transform.localPosition.z));
            Assert.That(emblem.transform.localScale.x, Is.EqualTo(PremiumDisplayCaseGate12R007Builder.EmblemSizeMm * Mm).Within(1e-8f));

            PremiumDisplayCaseLabelPlate plate = prefab.GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true);
            Assert.That(plate.IsWired, Is.True);
            Assert.That(plate.TierWordUsesFoil, Is.True, "tier word joins the foil set so it takes the tier tint");

            bool hasPlaque = names.Contains(PremiumDisplayCaseGate12R007Builder.PlaqueName);
            Assert.That(hasPlaque, Is.EqualTo(plaqueVariant));
            // 4 frame lines + divider + keyline + tier word (+ plaque).
            Assert.That(plate.FoilRendererCount, Is.EqualTo(plaqueVariant ? 8 : 7));
            if (plaqueVariant)
            {
                MeshRenderer plaque = renderers.Single(r => r.name == PremiumDisplayCaseGate12R007Builder.PlaqueName);
                Assert.That(plaque.sharedMaterial.shader.name, Is.EqualTo(PremiumDisplayCaseGate12R007Builder.ShaderName));
                Assert.That(plaque.sharedMaterial.GetTexture("_MainTex"), Is.Not.Null, "rounded-square relief mask");
                float expected = (PremiumDisplayCaseGate12R007Builder.PlaqueSizeMm + 1f) * Mm;
                Assert.That(plaque.transform.localScale.x, Is.EqualTo(expected).Within(1e-8f));
                Assert.That(plaque.transform.localScale.y, Is.EqualTo(expected).Within(1e-8f));
                // Emblem and word sit inside the plaque footprint.
                float half = PremiumDisplayCaseGate12R007Builder.PlaqueSizeMm * 0.5f * Mm;
                float emblemHalf = PremiumDisplayCaseGate12R007Builder.EmblemSizeMm * 0.5f * Mm;
                Assert.That(emblem.transform.localPosition.z - emblemHalf, Is.GreaterThan(-half));
                Assert.That(emblem.transform.localPosition.z + emblemHalf, Is.LessThan(half));
                Assert.That(tier.transform.localPosition.z, Is.LessThan(half - 4f * Mm));
                // Plaque renders first, relief on top.
                Assert.That(plaque.sharedMaterial.renderQueue, Is.LessThan(emblem.sharedMaterial.renderQueue));
                Assert.That(emblem.sharedMaterial.renderQueue, Is.LessThan(tier.sharedMaterial.renderQueue));
            }
        }

        [Test]
        public void HeirloomBindsGoldFoilAndFontAtlasToTheTierWord()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R007Builder.PlaquePrefabPath);
            Assert.That(prefab, Is.Not.Null, "run Fidgeting/Display Case/Gate 12/R007 Build Candidates");
            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            try
            {
                var presentation = instance.GetComponent<PremiumDisplayCaseShippingPresentation>();
                PremiumDisplayCaseLabelPlate plate = instance.GetComponentInChildren<PremiumDisplayCaseLabelPlate>(true);
                presentation.SetLabel(new PremiumDisplayCaseLabelData(
                    "GEEONE TRI-SPINNER", "SATIN STEEL · DRAGON SCALE", "2026-09-09", "HEIRLOOM", "FDT-82C77C1831AF"));
                Assert.That(plate.Tier, Is.EqualTo(PremiumDisplayCaseFoilTier.Gold));

                TextMesh tier = instance.GetComponentsInChildren<TextMesh>(true)
                    .Single(t => t.name == "AuthoritativeRarityLevel");
                Assert.That(plate.TierWordAtlas, Is.SameAs(tier.font.material.mainTexture),
                    "foil-shaded word must sample the live dynamic font atlas");

                var block = new MaterialPropertyBlock();
                foreach (string name in new[] { PremiumDisplayCaseGate12R007Builder.PlaqueName, "RarityEmblem", "AuthoritativeRarityLevel" })
                {
                    Renderer renderer = instance.GetComponentsInChildren<Renderer>(true).Single(r => r.name == name);
                    renderer.GetPropertyBlock(block);
                    Color foil = block.GetColor("_FoilColor");
                    AssertColor(foil, plate.FoilColor, name);
                    Assert.That(foil.r, Is.GreaterThan(foil.b + 0.3f), name + " gold");
                }

                presentation.SetLabel(new PremiumDisplayCaseLabelData(
                    "GEEONE TRI-SPINNER", "SATIN STEEL", "2026-09-09", "SIGNATURE", "FDT-1"));
                Assert.That(plate.Tier, Is.EqualTo(PremiumDisplayCaseFoilTier.Silver));
                Renderer plaque = instance.GetComponentsInChildren<Renderer>(true)
                    .Single(r => r.name == PremiumDisplayCaseGate12R007Builder.PlaqueName);
                plaque.GetPropertyBlock(block);
                AssertColor(block.GetColor("_FoilColor"), plate.FoilColor, "plaque follows tier");
            }
            finally
            {
                Object.DestroyImmediate(instance);
            }
        }

        // Property blocks round-trip through the GPU constant layout; compare
        // per channel with a tolerance instead of Color.Equals.
        private static void AssertColor(Color actual, Color expected, string context)
        {
            Assert.That(actual.r, Is.EqualTo(expected.r).Within(1e-3f), context + " r");
            Assert.That(actual.g, Is.EqualTo(expected.g).Within(1e-3f), context + " g");
            Assert.That(actual.b, Is.EqualTo(expected.b).Within(1e-3f), context + " b");
        }

        [Test]
        public void EarlierRoundsAndShippingFactoryAreUntouched()
        {
            Assert.That(PremiumDisplayCaseGate12R007Builder.PlaquePrefabPath,
                Is.Not.EqualTo(PremiumDisplayCaseGate12Builder.ShippingPrefabPath));
            Assert.That(PremiumDisplayCaseGate12R007Builder.ReliefPrefabPath,
                Is.Not.EqualTo(PremiumDisplayCaseGate12Builder.ShippingPrefabPath));
            foreach (string path in new[]
                     {
                         PremiumDisplayCaseGate12Builder.ShippingPrefabPath,
                         PremiumDisplayCaseGate12R005Builder.ShippingPrefabPath,
                         PremiumDisplayCaseGate12R006Builder.FlockingPrefabPath
                     })
            {
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                Assert.That(prefab, Is.Not.Null, path);
                string[] names = prefab.GetComponentsInChildren<Transform>(true).Select(t => t.name).ToArray();
                Assert.That(names, Does.Not.Contain(PremiumDisplayCaseGate12R007Builder.PlaqueName), path);
                MeshRenderer emblem = prefab.GetComponentsInChildren<MeshRenderer>(true)
                    .FirstOrDefault(r => r.name == "RarityEmblem");
                if (emblem != null)
                {
                    Assert.That(emblem.sharedMaterial.shader.name,
                        Is.Not.EqualTo(PremiumDisplayCaseGate12R007Builder.ShaderName), path);
                }
            }
        }
    }
}
