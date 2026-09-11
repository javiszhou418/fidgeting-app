using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.Rendering;
using UnityEngine;

namespace FidgetingApp.EDC.Tests.Editor
{
    public sealed class MagneticSlideLayeredMaterialRevisionTests
    {
        private const string ShaderName =
            "FidgetingApp/MagneticSlideTile/LayeredOpticsR012";

        [Test]
        public void Rev12HistoricalMaterialsRemainIndependent()
        {
            const string root =
                "Assets/_EDC/Candidates/MagneticSlideTileGate11R012/Materials/";
            Material[] tops =
            {
                AssetDatabase.LoadAssetAtPath<Material>(
                    root + "M_G11R012_UpperLayeredTop.mat"),
                AssetDatabase.LoadAssetAtPath<Material>(
                    root + "M_G11R012_LowerLayeredTop.mat"),
            };
            Assert.That(tops, Has.All.Not.Null);
            Assert.That(tops.Select(material => material.name).Distinct().Count(),
                Is.EqualTo(2));
            Assert.That(tops.All(material => material.shader.name == ShaderName),
                Is.True);
            Assert.That(
                tops.Select(material => AssetDatabase.GetAssetPath(
                        material.GetTexture("_MotifMask")))
                    .Distinct()
                    .Count(),
                Is.EqualTo(2));
            foreach (Material material in tops)
            {
                Assert.That(material.GetTag("RenderType", false), Is.EqualTo("Opaque"));
                Assert.That(material.renderQueue, Is.EqualTo(2000));
                Assert.That(material.passCount, Is.EqualTo(3));
                Assert.That(material.GetFloat("_CoatIor"), Is.EqualTo(1.52f));
                Assert.That(material.GetFloat("_CoatRoughness"), Is.EqualTo(0.035f));
                Assert.That(material.GetFloat("_CoatStrength"), Is.EqualTo(0.78f));
                Assert.That(material.GetFloat("_MicaScale"), Is.EqualTo(28f));
                Assert.That(material.GetFloat("_MicroflakeScale"), Is.EqualTo(85f));
                Assert.That(material.GetFloat("_MicroflakeStrength"), Is.EqualTo(0.16f));
                Assert.That(material.GetFloat("_IridescenceStrength"), Is.EqualTo(0.12f));
                Assert.That(material.GetFloat("_MotifRoughness"), Is.EqualTo(0.18f));
                Assert.That(material.GetFloat("_MotifMetallic"), Is.EqualTo(0.24f));
                Assert.That(material.HasProperty("_EmissionColor"), Is.False);
            }
        }

        [Test]
        public void LayeredShaderCompilesWithoutMobileTransportFallback()
        {
            Shader shader = Shader.Find(ShaderName);
            Assert.That(shader, Is.Not.Null);
            Assert.That(shader.isSupported, Is.True);
            Assert.That(
                ShaderUtil.GetShaderMessages(shader)
                    .Count(message =>
                        message.severity == ShaderCompilerMessageSeverity.Error),
                Is.Zero);
        }

        [Test]
        public void MaterialReviewPreservesRuntimeGeometryAndBuildGate()
        {
            string root = Directory.GetParent(Application.dataPath)!.FullName;
            string evidence = Path.Combine(
                root,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
                + "11-unity-parity/rev-012-layered-material");
            string report = File.ReadAllText(
                Path.Combine(evidence, "unity-layered-material-report.json"));
            string metrics = File.ReadAllText(
                Path.Combine(evidence, "layered-material-image-metrics.json"));

            StringAssert.Contains("\"protectedRuntimeUnchanged\": true", report);
            StringAssert.Contains("\"geometryMeshInstancesUnchanged\": true", report);
            StringAssert.Contains("\"boundsCenterDeltaMeters\": 0.0", report);
            StringAssert.Contains("\"boundsSizeDeltaMeters\": 0.0", report);
            StringAssert.Contains("\"addedRenderers\": 0", report);
            StringAssert.Contains("\"addedDrawCalls\": 0", report);
            StringAssert.Contains("\"build44Installed\": false", report);
            StringAssert.Contains("\"visualApproval\": \"pending\"", report);
            StringAssert.Contains("\"pass\": true", metrics);
        }
    }
}
