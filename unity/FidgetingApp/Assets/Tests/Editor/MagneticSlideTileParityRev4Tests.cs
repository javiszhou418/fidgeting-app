using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MagneticSlideTileParityRev4Tests
    {
        private const string Root =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev004";
        private const string UpperMaterialPath =
            Root + "/Materials/M_Gate11R4_BloodRedCrystalUpper.mat";
        private const string LowerMaterialPath =
            Root + "/Materials/M_Gate11R4_BloodRedCrystalLower.mat";
        private const string SilverMaterialPath =
            Root + "/Materials/M_Gate11R4_PolishedSilver.mat";
        private const string ScenePath =
            Root + "/MagneticSlideTileNeutralParityRev4.unity";

        [Test]
        public void Rev4UsesMobileShippingShadersWithoutEmission()
        {
            Material upper = AssetDatabase.LoadAssetAtPath<Material>(UpperMaterialPath);
            Material lower = AssetDatabase.LoadAssetAtPath<Material>(LowerMaterialPath);
            Material silver = AssetDatabase.LoadAssetAtPath<Material>(SilverMaterialPath);
            Assert.That(upper, Is.Not.Null);
            Assert.That(lower, Is.Not.Null);
            Assert.That(silver, Is.Not.Null);
            Assert.That(
                upper.shader.name,
                Is.EqualTo("FidgetingApp/EDC/MagneticCrystalShippingR3"));
            Assert.That(lower.shader.name, Is.EqualTo(upper.shader.name));
            Assert.That(
                silver.shader.name,
                Is.EqualTo("FidgetingApp/EDC/MagneticSilverShippingR3"));
            Assert.That(upper.shader.isSupported, Is.True);
            Assert.That(silver.shader.isSupported, Is.True);
            Assert.That(upper.HasProperty("_EmissionColor"), Is.False);
            Assert.That(silver.HasProperty("_EmissionColor"), Is.False);
        }

        [Test]
        public void Rev4PreservesIndependentArtworkAndUsesAstcOnIphone()
        {
            Material upper = AssetDatabase.LoadAssetAtPath<Material>(UpperMaterialPath);
            Material lower = AssetDatabase.LoadAssetAtPath<Material>(LowerMaterialPath);
            string upperPath = AssetDatabase.GetAssetPath(upper.GetTexture("_MaskMap"));
            string lowerPath = AssetDatabase.GetAssetPath(lower.GetTexture("_MaskMap"));
            Assert.That(upperPath, Is.Not.EqualTo(lowerPath));
            foreach (string path in new[] { upperPath, lowerPath })
            {
                TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
                Assert.That(importer, Is.Not.Null);
                TextureImporterPlatformSettings iphone =
                    importer.GetPlatformTextureSettings("iPhone");
                Assert.That(iphone.overridden, Is.True);
                Assert.That(iphone.format, Is.EqualTo(TextureImporterFormat.ASTC_6x6));
                Assert.That(importer.sRGBTexture, Is.False);
            }
        }

        [Test]
        public void Rev4ReportsUnchangedGeometryAndBlockedShipping()
        {
            Assert.That(AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath), Is.Not.Null);
            string unityReport = File.ReadAllText(
                EvidencePath("unity-parity-rev4-report.json"));
            StringAssert.Contains("\"pass\": true", unityReport);
            StringAssert.Contains("\"triangles\": 4096", unityReport);
            StringAssert.Contains("\"vertices\": 4124", unityReport);
            StringAssert.Contains("\"motifPlacementPreserved\": true", unityReport);
            StringAssert.Contains("\"borderWidthPixels\": 42", unityReport);
            StringAssert.Contains("\"shippingSceneModified\": false", unityReport);
            StringAssert.Contains("\"runtimeIntegrated\": false", unityReport);
            StringAssert.Contains("\"deviceAcceptance\": \"pending\"", unityReport);

            string perceptual = File.ReadAllText(
                EvidencePath("parity-review-validation-rev4.json"));
            StringAssert.Contains("\"pass\": true", perceptual);
            StringAssert.Contains("\"cameraRecipeIdentical\": true", perceptual);
            StringAssert.Contains("\"emission\": false", perceptual);
            StringAssert.Contains("\"shippingSceneDefault\": \"unchanged\"", perceptual);
            StringAssert.Contains("\"buildInstallPhone\": \"not_started\"", perceptual);
        }

        [Test]
        public void Rev4EvidenceIncludesLargeBoardsAndHeatmap()
        {
            foreach (string file in new[]
            {
                "gate11-rev4-geometry-board.png",
                "gate11-rev4-artwork-board.png",
                "gate11-rev4-material-board.png",
                "gate11-rev4-final-board.png",
                "gate11-rev4-difference-heatmap.png",
                "gate11-rev4-review.png"
            })
            {
                FileInfo info = new(EvidencePath(file));
                Assert.That(info.Exists, Is.True, file);
                Assert.That(info.Length, Is.GreaterThan(16 * 1024), file);
            }
        }

        private static string EvidencePath(string file)
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            return Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-004",
                file);
        }
    }
}
