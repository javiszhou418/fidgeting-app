using System.IO;
using System.Linq;
using FidgetingApp.EDC.Candidate;
using FidgetingApp.EDC.EditorTools;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Tests.Editor
{
    public sealed class MagneticSlideTileGate12Tests
    {
        private SceneSetup[] previousSceneSetup;

        [TearDown]
        public void RestoreScenes()
        {
            if (previousSceneSetup != null && previousSceneSetup.Any(item => item.isLoaded))
            {
                EditorSceneManager.RestoreSceneManagerSetup(previousSceneSetup);
            }
        }

        [Test]
        public void ShippingSceneKeepsCurrentModelActiveByDefault()
        {
            previousSceneSetup = EditorSceneManager.GetSceneManagerSetup();
            Scene scene = EditorSceneManager.OpenScene(
                MagneticSlideTileGate12Builder.ShippingScenePath,
                OpenSceneMode.Single);
            MagneticSlideTileCandidateActivation activation = scene.GetRootGameObjects()
                .Select(root => root.GetComponent<MagneticSlideTileCandidateActivation>())
                .Single(component => component != null);

            Assert.That(activation.CandidatePreviewEnabled, Is.False);
            Assert.That(activation.ShippingModel.activeSelf, Is.True);
            Assert.That(activation.CandidateModel.activeSelf, Is.False);
            Assert.That(activation.ShippingModel.name, Is.EqualTo("EDC_Root"));
        }

        [Test]
        public void CandidatePrefabPreservesApprovedGeometryAndMaterials()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                MagneticSlideTileGate12Builder.CandidatePrefabPath);
            Assert.That(prefab, Is.Not.Null);
            MeshFilter[] filters = prefab.GetComponentsInChildren<MeshFilter>(true);
            Assert.That(filters, Has.Length.EqualTo(2));
            Assert.That(filters.Sum(filter => filter.sharedMesh.triangles.Length / 3),
                Is.EqualTo(4096));
            Renderer[] renderers = prefab.GetComponentsInChildren<Renderer>(true);
            Bounds bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1)) bounds.Encapsulate(renderer.bounds);
            float[] dimensions = { bounds.size.x, bounds.size.y, bounds.size.z };
            System.Array.Sort(dimensions);
            Assert.That(dimensions[0], Is.EqualTo(0.012f).Within(0.00001f));
            Assert.That(dimensions[1], Is.EqualTo(0.031f).Within(0.00001f));
            Assert.That(dimensions[2], Is.EqualTo(0.050f).Within(0.00001f));

            Material[] materials = renderers.SelectMany(renderer => renderer.sharedMaterials)
                .Distinct().ToArray();
            Assert.That(materials.Any(material =>
                material.shader.name == "Universal Render Pipeline/Lit"), Is.True);
            Assert.That(materials.Count(material =>
                material.shader.name == "FidgetingApp/EDC/MagneticCrystalMobile"), Is.EqualTo(2));
            Assert.That(materials.All(material => !material.IsKeywordEnabled("_EMISSION")), Is.True);
        }

        [Test]
        public void CandidateUsesOneLockedMechanismSettingsAsset()
        {
            MagneticSlideTileCandidateSettings settings =
                AssetDatabase.LoadAssetAtPath<MagneticSlideTileCandidateSettings>(
                    MagneticSlideTileGate12Builder.SettingsPath);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                MagneticSlideTileGate12Builder.CandidatePrefabPath);
            MagneticSlideTileCandidateController controller =
                prefab.GetComponent<MagneticSlideTileCandidateController>();

            Assert.That(settings, Is.Not.Null);
            Assert.That(settings.IsLockedContractValid, Is.True);
            Assert.That(settings.SlideTravelMeters, Is.EqualTo(0.021f));
            Assert.That(settings.DetentCount, Is.EqualTo(30));
            Assert.That(settings.DetentStepDegrees, Is.EqualTo(12f));
            Assert.That(controller.Settings, Is.SameAs(settings));
            Assert.That(controller.RuntimeInputIntegrated, Is.False);
            Assert.That(controller.HapticsIntegrated, Is.False);
        }

        [Test]
        public void ArtworkLayersRemainIndependentAndReplaceable()
        {
            Material upper = AssetDatabase.LoadAssetAtPath<Material>(
                MagneticSlideTileGate12Builder.UpperMaterialPath);
            Material lower = AssetDatabase.LoadAssetAtPath<Material>(
                MagneticSlideTileGate12Builder.LowerMaterialPath);
            Assert.That(upper, Is.Not.Null);
            Assert.That(lower, Is.Not.Null);
            Assert.That(upper, Is.Not.SameAs(lower));
            Assert.That(
                AssetDatabase.GetAssetPath(upper.GetTexture("_BaseMap")),
                Is.EqualTo(MagneticSlideTileGate12Builder.UpperTexturePath));
            Assert.That(
                AssetDatabase.GetAssetPath(lower.GetTexture("_BaseMap")),
                Is.EqualTo(MagneticSlideTileGate12Builder.LowerTexturePath));
        }

        [Test]
        public void ReflectionProbeUsesFilteredContinuousEnvironment()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                MagneticSlideTileGate12Builder.CandidatePrefabPath);
            ReflectionProbe probe = prefab.GetComponentInChildren<ReflectionProbe>(true);
            Cubemap cubemap = probe.customBakedTexture as Cubemap;
            Assert.That(probe.mode, Is.EqualTo(ReflectionProbeMode.Custom));
            Assert.That(probe.boxProjection, Is.False);
            Assert.That(cubemap, Is.Not.Null);
            Assert.That(cubemap.mipmapCount, Is.GreaterThanOrEqualTo(9));
            Assert.That(cubemap.filterMode, Is.EqualTo(FilterMode.Trilinear));
        }

        [Test]
        public void RealShippingPreviewReportPassesAllRequiredViews()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string reportPath = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-001/gate12-shipping-report.json");
            string report = File.ReadAllText(reportPath);
            StringAssert.Contains("\"pass\": true", report);
            foreach (string view in new[]
            {
                "library", "hero", "top", "left-oblique", "right-oblique",
                "low", "phone", "slide-open", "ratchet-60deg"
            })
            {
                StringAssert.Contains($"\"id\": \"{view}\"", report);
                Assert.That(File.Exists(Path.Combine(Path.GetDirectoryName(reportPath)!, view + ".png")),
                    Is.True, view);
            }
            StringAssert.Contains("\"candidateDefaultActive\": false", report);
            StringAssert.Contains("\"currentShippingModelDefaultActive\": true", report);
            StringAssert.Contains("\"runtimeInputIntegrated\": false", report);
            StringAssert.Contains("\"hapticsIntegrated\": false", report);
        }

        [Test]
        public void CandidateCodeAddsNoDirectIosHapticsCalls()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string runtimeRoot = Path.Combine(projectRoot, "Assets/_EDC/Candidate/Runtime");
            foreach (string file in Directory.GetFiles(runtimeRoot, "*.cs"))
            {
                StringAssert.DoesNotContain("IosHaptics", File.ReadAllText(file), file);
            }
        }
    }
}
