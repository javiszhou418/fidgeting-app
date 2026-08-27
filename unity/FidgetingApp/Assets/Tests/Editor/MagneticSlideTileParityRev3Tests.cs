using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MagneticSlideTileParityRev3Tests
    {
        private const string Root =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev003";
        private const string UpperMaterialPath =
            Root + "/Materials/M_Gate11R3_BloodRedCrystalUpper.mat";
        private const string LowerMaterialPath =
            Root + "/Materials/M_Gate11R3_BloodRedCrystalLower.mat";
        private const string SilverMaterialPath =
            Root + "/Materials/M_Gate11R3_PolishedSilver.mat";
        private const string ScenePath =
            Root + "/MagneticSlideTileNeutralParityRev3.unity";

        [Test]
        public void Rev3UsesShippingCapableCrystalShaderAndIndependentMasks()
        {
            Material upper = AssetDatabase.LoadAssetAtPath<Material>(UpperMaterialPath);
            Material lower = AssetDatabase.LoadAssetAtPath<Material>(LowerMaterialPath);
            Material silver = AssetDatabase.LoadAssetAtPath<Material>(SilverMaterialPath);
            Assert.That(upper, Is.Not.Null);
            Assert.That(lower, Is.Not.Null);
            Assert.That(silver, Is.Not.Null);
            Assert.That(
                upper.shader.name,
                Is.EqualTo("FidgetingApp/EDC/MagneticCrystalShippingR2"));
            Assert.That(lower.shader.name, Is.EqualTo(upper.shader.name));
            Assert.That(
                silver.shader.name,
                Is.EqualTo("FidgetingApp/EDC/MagneticSilverShippingR2"));
            Assert.That(upper.GetTexture("_MaskMap"), Is.Not.Null);
            Assert.That(lower.GetTexture("_MaskMap"), Is.Not.Null);
            Assert.That(
                AssetDatabase.GetAssetPath(upper.GetTexture("_MaskMap")),
                Is.Not.EqualTo(
                    AssetDatabase.GetAssetPath(lower.GetTexture("_MaskMap"))));
        }

        [Test]
        public void Rev3SceneAndEvidenceExist()
        {
            Assert.That(AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath), Is.Not.Null);
            foreach (string file in new[]
            {
                "unity-material-final.png",
                "unity-geometry-clay.png",
                "unity-artwork-material.png",
                "unity-parity-rev3-report.json"
            })
            {
                FileInfo info = new(EvidencePath(file));
                Assert.That(info.Exists, Is.True, file);
                Assert.That(info.Length, Is.GreaterThan(1024), file);
            }
        }

        [Test]
        public void Rev3ReportRejectsUnlitOverlayShortcutAndPreservesGeometry()
        {
            string json = File.ReadAllText(EvidencePath("unity-parity-rev3-report.json"));
            StringAssert.Contains("\"pass\": true", json);
            StringAssert.Contains("\"triangles\": 4096", json);
            StringAssert.Contains("\"unlitOverlayCount\": 0", json);
            StringAssert.Contains("\"upperLowerMasksIndependent\": true", json);
            StringAssert.Contains("\"shippingSceneModified\": false", json);
            StringAssert.Contains("\"runtimeIntegrated\": false", json);
            StringAssert.Contains("\"hapticsIntegrated\": false", json);
        }

        private static string EvidencePath(string file)
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            return Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-003",
                file);
        }
    }
}
