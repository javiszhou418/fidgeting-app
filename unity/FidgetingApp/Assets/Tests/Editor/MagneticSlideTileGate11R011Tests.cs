using System.Collections;
using System.IO;
using System.Linq;
using FidgetingApp.EDC.Candidates;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.TestTools;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MagneticSlideTileGate11R011Tests
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R011";
        private const string ProductPath =
            Root + "/Imported/magnetic-slide-tile-render-r011.fbx";
        private const string ScenePath =
            Root + "/Scenes/MagneticSlideTileGate11R011Parity.unity";

        [Test]
        public void ImportPreservesApprovedHierarchyAndVertexData()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(ProductPath);
            Assert.That(prefab, Is.Not.Null);
            MeshFilter[] filters = prefab.GetComponentsInChildren<MeshFilter>(true);
            Assert.That(filters.Select(filter => filter.name), Is.EquivalentTo(new[]
            {
                "BallCandidateLeft",
                "BallCandidateRight",
                "BottomExterior",
                "CarrierFollowerLeft",
                "CarrierFollowerRight",
                "InternalAxisBoss",
                "MovingTopBody",
                "RotatingCarrierBody"
            }));
            Assert.That(filters.All(filter =>
                filter.sharedMesh.normals.Length == filter.sharedMesh.vertexCount), Is.True);
            Assert.That(filters.All(filter =>
                filter.sharedMesh.tangents.Length == filter.sharedMesh.vertexCount), Is.True);
            Assert.That(filters.All(filter =>
                filter.sharedMesh.uv.Length == filter.sharedMesh.vertexCount), Is.True);
        }

        [Test]
        public void ImportSettingsRemainDeterministic()
        {
            ModelImporter importer = AssetImporter.GetAtPath(ProductPath) as ModelImporter;
            Assert.That(importer, Is.Not.Null);
            Assert.That(importer.meshCompression, Is.EqualTo(ModelImporterMeshCompression.Off));
            Assert.That(importer.importNormals, Is.EqualTo(ModelImporterNormals.Import));
            Assert.That(importer.importTangents, Is.EqualTo(ModelImporterTangents.Import));
            Assert.That(importer.importAnimation, Is.False);

            foreach (string path in AssetDatabase.FindAssets(
                "t:Texture2D", new[] { Root + "/Imported/Textures" })
                .Select(AssetDatabase.GUIDToAssetPath))
            {
                TextureImporter texture = AssetImporter.GetAtPath(path) as TextureImporter;
                Assert.That(texture, Is.Not.Null);
                Assert.That(texture.npotScale, Is.EqualTo(TextureImporterNPOTScale.None));
            }
        }

        [Test]
        public void ReportsPassWithoutShippingPromotion()
        {
            string import = ReadEvidence("unity-import-parity-report.json");
            string parity = ReadEvidence("parity-validation.json");
            StringAssert.Contains("\"pass\": true", import);
            StringAssert.Contains("\"shippingSceneModified\": false", import);
            StringAssert.Contains("\"oldShippingModelDefault\": true", import);
            StringAssert.Contains("\"buildInstallPhone\": false", import);
            StringAssert.Contains("\"pass\": true", parity);
            StringAssert.Contains("\"status\": \"complete\"", parity);
            StringAssert.Contains("\"topArtworkOnly\": true", parity);
            StringAssert.Contains("\"sideArtworkTriangles\": 0", parity);
        }

        [Test]
        public void HdrAndMaterialPathRemainLinearAndPhysical()
        {
            const string cubemapPath =
                Root + "/Imported/Environment/unity-specular-strip-r011.exr";
            TextureImporter importer =
                AssetImporter.GetAtPath(cubemapPath) as TextureImporter;
            Cubemap cubemap = AssetDatabase.LoadAssetAtPath<Cubemap>(cubemapPath);
            Assert.That(importer, Is.Not.Null);
            Assert.That(importer.textureShape, Is.EqualTo(TextureImporterShape.TextureCube));
            Assert.That(importer.sRGBTexture, Is.False);
            Assert.That(cubemap, Is.Not.Null);
            Assert.That(cubemap.format, Is.EqualTo(TextureFormat.RGBAHalf));

            foreach (Material material in AssetDatabase.FindAssets(
                "t:Material", new[] { Root + "/Materials" })
                .Select(AssetDatabase.GUIDToAssetPath)
                .Select(AssetDatabase.LoadAssetAtPath<Material>)
                .Where(material => material.name.StartsWith("M_G11R011_")
                    && material.name != "M_G11R011_SharedEnvironmentSky"))
            {
                Assert.That(material.shader.name,
                    Is.EqualTo("FidgetingApp/MagneticSlideTile/PortablePBRR011"));
                Assert.That(material.GetFloat("_EnvironmentIntensity"), Is.EqualTo(0.85f));
                Assert.That(material.IsKeywordEnabled("_EMISSION"), Is.False);
            }
        }

        [UnityTest]
        public IEnumerator EndpointInterlockEnforcesAllLegalTransitions()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            MagneticSlideTileEndpointInterlockController controller =
                Object.FindAnyObjectByType<MagneticSlideTileEndpointInterlockController>();
            Assert.That(controller, Is.Not.Null);
            Assert.That(controller.TravelMeters, Is.Zero);
            Assert.That(controller.AngleDegrees, Is.Zero);
            Assert.That(controller.LinearVelocityMetersPerSecond, Is.Zero);
            Assert.That(controller.AngularVelocityDegreesPerSecond, Is.Zero);

            Assert.That(controller.TrySetTravel(controller.MaximumTravelMeters * 0.5f), Is.True);
            Assert.That(controller.TrySetAngle(12f), Is.False);
            Assert.That(controller.TrySetTravel(controller.MaximumTravelMeters), Is.True);
            for (int detent = 0; detent < 30; detent++)
                Assert.That(controller.TrySetEndpointDetent(detent), Is.True);
            Assert.That(controller.TrySetEndpointDetent(7), Is.True);
            Assert.That(controller.TrySetTravel(0f), Is.False);
            Assert.That(controller.TrySetAngle(0f), Is.True);
            Assert.That(controller.TrySetTravel(0f), Is.True);
            Assert.That(controller.TravelMeters, Is.Zero);
            Assert.That(controller.AngleDegrees, Is.Zero);
            yield return null;
        }

        private static string ReadEvidence(string filename)
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string path = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-011",
                filename);
            Assert.That(File.Exists(path), Is.True);
            return File.ReadAllText(path);
        }
    }
}
