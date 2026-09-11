using System.Linq;
using FidgetingApp.DisplayCase;
using FidgetingApp.DisplayCase.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.Tests.Editor
{
    /// <summary>
    /// Gate 12 R008 lookdev: PSA-style clear acrylic + glitter backing.
    /// Candidate only; the shipping factory still points at R004.
    /// </summary>
    public sealed class PremiumDisplayCaseGate12R008Tests
    {
        [Test]
        public void PrefabUsesClearAcrylicAndGlitterWithoutExplodeControls()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R008Builder.PrefabPath);
            Assert.That(prefab, Is.Not.Null, "run Fidgeting/Display Case/Gate 12/R008 Build Reference-Match Lookdev");
            string[] names = prefab.GetComponentsInChildren<Transform>(true).Select(t => t.name).ToArray();
            foreach (string forbidden in new[] { "Explode", "Reassembl", "LayerSeparation", "Scrub" })
            {
                Assert.That(names.Any(n => n.Contains(forbidden)), Is.False, forbidden);
            }
            Assert.That(names, Does.Contain("SideWallSkirt"));
            foreach (string inherited in new[] { "LabelWellFloor", "BridgeBar", "TactileBackgroundInsert" })
            {
                Assert.That(names, Does.Contain(inherited));
            }

            MeshRenderer[] renderers = prefab.GetComponentsInChildren<MeshRenderer>(true);
            Assert.That(Renderer(renderers, "FrontPolycarbonateShell").sharedMaterial.shader.name,
                Is.EqualTo(PremiumDisplayCaseGate12R008Builder.AcrylicShaderName));
            Assert.That(Renderer(renderers, "RearPolycarbonateShell").sharedMaterial.shader.name,
                Is.EqualTo(PremiumDisplayCaseGate12R008Builder.AcrylicShaderName));
            Assert.That(Renderer(renderers, "SideWallSkirt").sharedMaterial.shader.name,
                Is.EqualTo(PremiumDisplayCaseGate12R008Builder.AcrylicShaderName));
            Assert.That(Renderer(renderers, "TactileBackgroundInsert").sharedMaterial.shader.name,
                Is.EqualTo(PremiumDisplayCaseGate12R008Builder.GlitterShaderName));
            Assert.That(Renderer(renderers, "LabelWellFloor").sharedMaterial.shader.name,
                Is.EqualTo(PremiumDisplayCaseGate12R008Builder.GlitterShaderName));
            Assert.That(Renderer(renderers, "ChamberBezel").enabled, Is.False);
            Assert.That(Renderer(renderers, "SideWallSkirt").sharedMaterial.GetFloat("_Cull"),
                Is.EqualTo((float)CullMode.Back));
            Assert.That(Renderer(renderers, "FrontPolycarbonateShell").sharedMaterial.GetFloat("_HotspotStrength"),
                Is.GreaterThan(4f));
        }

        [Test]
        public void LookdevCameraStaysPulledBackAndFactoryStaysOnR004()
        {
            Assert.That(PremiumDisplayCaseGate12R008Builder.PrefabPath,
                Is.Not.EqualTo(PremiumDisplayCaseGate12Builder.ShippingPrefabPath));
            Assert.That(PremiumDisplayCaseShippingFactory.ResourcesPath,
                Is.EqualTo("Gacha/PremiumDisplayCaseGate12R004/PresentationRoot"));

            string scene = System.IO.File.ReadAllText(PremiumDisplayCaseGate12R008Builder.ScenePath);
            Assert.That(scene, Does.Contain("z: -1.22"));
            Assert.That(scene, Does.Contain("m_HDR: 1"));

            GameObject r004 = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12Builder.ShippingPrefabPath);
            string[] names = r004.GetComponentsInChildren<Transform>(true).Select(t => t.name).ToArray();
            Assert.That(names, Does.Not.Contain("SideWallSkirt"));
        }

        private static MeshRenderer Renderer(MeshRenderer[] renderers, string name)
        {
            return renderers.Single(r => r.name == name);
        }
    }
}
