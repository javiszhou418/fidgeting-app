using System.IO;
using System.Linq;
using FidgetingApp.EDC.Gate11R013;
using FidgetingApp.EDC.Gate12R002;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.Rendering;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools.Utils;

namespace FidgetingApp.EDC.Tests.Editor
{
    public sealed class MagneticSlideTrueLayerRevisionTests
    {
        private const string ScenePath =
            "Assets/_EDC/Scenes/MeshyEDC.unity";

        [Test]
        public void ShippingSceneUsesTwoPhysicalThreeLayerCaps()
        {
            EditorSceneManager.OpenScene(
                ScenePath, OpenSceneMode.Single);
            MagneticSlideTileShippingCoordinator coordinator =
                Object.FindFirstObjectByType<
                    MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include);
            MagneticSlideTrueLayerAssembly[] assemblies =
                coordinator.CandidateModel.GetComponentsInChildren<
                    MagneticSlideTrueLayerAssembly>(true);
            Assert.That(assemblies, Has.Length.EqualTo(2));
            Assert.That(
                assemblies.Select(item => item.FaceId),
                Is.EquivalentTo(new[] { "upper", "lower" }));
            foreach (MagneticSlideTrueLayerAssembly assembly in assemblies)
            {
                Assert.That(
                    assembly.Substrate.transform.localPosition,
                    Is.EqualTo(
                        -assembly.LocalOutwardNormal * 0.00028f)
                        .Using(Vector3ComparerWithEqualsOperator.Instance));
                Assert.That(
                    assembly.Motif.transform.localPosition,
                    Is.EqualTo(
                        -assembly.LocalOutwardNormal * 0.00014f)
                        .Using(Vector3ComparerWithEqualsOperator.Instance));
                Assert.That(
                    assembly.CrystalCap.transform.localPosition,
                    Is.EqualTo(Vector3.zero)
                        .Using(Vector3ComparerWithEqualsOperator.Instance));
                Assert.That(
                    assembly.Substrate.GetComponent<MeshFilter>()
                        .sharedMesh.subMeshCount,
                    Is.EqualTo(1));
                Assert.That(
                    assembly.Motif.GetComponent<MeshFilter>()
                        .sharedMesh.subMeshCount,
                    Is.EqualTo(1));
                Assert.That(
                    assembly.CrystalCap.GetComponent<MeshFilter>()
                        .sharedMesh.subMeshCount,
                    Is.EqualTo(1));
            }
        }

        [Test]
        public void HybridShadersCompileAndRestoreRev12DetailTuning()
        {
            EditorSceneManager.OpenScene(
                ScenePath, OpenSceneMode.Single);
            string[] names =
            {
                "FidgetingApp/MagneticSlideTile/HybridSubstrateR014",
                "FidgetingApp/MagneticSlideTile/HybridMotifR014",
                "FidgetingApp/MagneticSlideTile/HybridCrystalR014",
            };
            Shader[] shaders = names.Select(Shader.Find).ToArray();
            Assert.That(shaders.All(shader => shader != null), Is.True);
            Assert.That(shaders.All(shader => shader.isSupported), Is.True);
            Assert.That(
                shaders.Sum(shader => ShaderUtil.GetShaderMessages(shader)
                    .Count(message =>
                        message.severity
                        == ShaderCompilerMessageSeverity.Error)),
                Is.Zero);

            MagneticSlideTrueLayerAssembly assembly =
                Object.FindFirstObjectByType<
                    MagneticSlideTrueLayerAssembly>(
                    FindObjectsInactive.Include);
            Assert.That(
                assembly.Substrate.sharedMaterial.renderQueue,
                Is.LessThan(assembly.Motif.sharedMaterial.renderQueue));
            Assert.That(
                assembly.Motif.sharedMaterial.renderQueue,
                Is.LessThan(
                    assembly.CrystalCap.sharedMaterial.renderQueue));
            Assert.That(
                assembly.CrystalCap.sharedMaterial.GetFloat("_Ior"),
                Is.EqualTo(1.52f));
            Assert.That(
                assembly.CrystalCap.sharedMaterial
                    .GetFloat("_ThicknessMeters"),
                Is.EqualTo(0.00028f));
            Assert.That(
                assembly.CrystalCap.sharedMaterial
                    .GetFloat("_Transmission"),
                Is.EqualTo(0.985f));
            Assert.That(
                assembly.CrystalCap.sharedMaterial
                    .GetFloat("_RefractionPixels"),
                Is.EqualTo(0.35f));
            Assert.That(
                assembly.Substrate.sharedMaterial
                    .GetFloat("_MicaScale"),
                Is.EqualTo(28f));
            Assert.That(
                assembly.Substrate.sharedMaterial
                    .GetFloat("_MicroflakeScale"),
                Is.EqualTo(85f));
            Assert.That(
                assembly.Substrate.sharedMaterial
                    .GetFloat("_NormalScale"),
                Is.EqualTo(0.32f));
            Assert.That(
                assembly.Substrate.sharedMaterial
                    .HasProperty("_EmissionColor"),
                Is.False);
        }

        [Test]
        public void HybridEvidenceProvesDetailParallaxAndBuildGate()
        {
            string root =
                Directory.GetParent(Application.dataPath)!.FullName;
            string evidence = Path.Combine(
                root,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
                + "11-unity-parity/rev-014-detail-depth-hybrid");
            string report = File.ReadAllText(
                Path.Combine(
                    evidence, "unity-hybrid-report.json"));
            string metrics = File.ReadAllText(
                Path.Combine(
                    evidence, "hybrid-detail-metrics.json"));
            StringAssert.Contains(
                "\"measuredParallaxPixelsAt15Degrees\":",
                report);
            StringAssert.DoesNotContain(
                "\"measuredParallaxPixelsAt15Degrees\": 0.0",
                report);
            StringAssert.Contains(
                "\"boundsCenterDeltaMeters\": 0.0",
                report);
            StringAssert.Contains(
                "\"boundsSizeDeltaMeters\": 0.0",
                report);
            StringAssert.Contains(
                "\"collidersUnchanged\": true",
                report);
            StringAssert.Contains(
                "\"protectedRuntimeUnchanged\": true",
                report);
            StringAssert.Contains(
                "\"endpointInterlockLegal\": true",
                report);
            StringAssert.Contains(
                "\"build44InstallAuthorized\": false",
                report);
            StringAssert.Contains(
                "\"visualApproval\": \"pending\"",
                report);
            StringAssert.Contains("\"pass\": true", report);
            StringAssert.Contains(
                "\"laplacianAtLeastRev12\": true",
                metrics);
            StringAssert.Contains(
                "\"localVarianceAtLeastRev12\": true",
                metrics);
            StringAssert.Contains(
                "\"edgeDensityAtLeastRev12\": true",
                metrics);
            StringAssert.Contains("\"pass\": true", metrics);
        }
    }
}
