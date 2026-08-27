using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MagneticSlideTileParityTests
    {
        private const string Root =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001";
        private const string ProductPath =
            Root + "/Imported/magnetic-slide-tile-r002.fbx";
        private const string CollisionPath =
            Root + "/Imported/magnetic-slide-tile-collision-r002.fbx";
        private const string ScenePath =
            Root + "/MagneticSlideTileNeutralParity.unity";

        [Test]
        public void IsolatedRenderModelPreservesGate10Geometry()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(ProductPath);
            Assert.That(prefab, Is.Not.Null);
            MeshFilter[] filters = prefab.GetComponentsInChildren<MeshFilter>(true);
            Assert.That(filters, Has.Length.EqualTo(2));
            Assert.That(
                filters.Sum(filter => filter.sharedMesh.triangles.Length / 3),
                Is.EqualTo(4096));
            Assert.That(filters.All(filter =>
                filter.sharedMesh.normals.Length == filter.sharedMesh.vertexCount), Is.True);
            Assert.That(filters.All(filter =>
                filter.sharedMesh.tangents.Length == filter.sharedMesh.vertexCount), Is.True);
            Assert.That(filters.All(filter =>
                filter.sharedMesh.uv.Length == filter.sharedMesh.vertexCount), Is.True);

            Renderer[] renderers = prefab.GetComponentsInChildren<Renderer>(true);
            Bounds bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1))
            {
                bounds.Encapsulate(renderer.bounds);
            }
            float[] dimensions = { bounds.size.x, bounds.size.y, bounds.size.z };
            System.Array.Sort(dimensions);
            Assert.That(dimensions[0], Is.EqualTo(0.012f).Within(0.00001f));
            Assert.That(dimensions[1], Is.EqualTo(0.031f).Within(0.00001f));
            Assert.That(dimensions[2], Is.EqualTo(0.050f).Within(0.00001f));
        }

        [Test]
        public void ImportersPreserveClosedStaticAsset()
        {
            var importer = AssetImporter.GetAtPath(ProductPath) as ModelImporter;
            Assert.That(importer, Is.Not.Null);
            Assert.That(importer.globalScale, Is.EqualTo(1f));
            Assert.That(importer.useFileScale, Is.True);
            Assert.That(importer.preserveHierarchy, Is.True);
            Assert.That(importer.importAnimation, Is.False);
            Assert.That(importer.importNormals, Is.EqualTo(ModelImporterNormals.Import));
            Assert.That(importer.importTangents, Is.EqualTo(ModelImporterTangents.Import));
            Assert.That(importer.meshCompression, Is.EqualTo(ModelImporterMeshCompression.Off));

            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(ProductPath);
            Assert.That(prefab.GetComponentsInChildren<Animation>(true), Is.Empty);
            Assert.That(prefab.GetComponentsInChildren<Animator>(true), Is.Empty);
        }

        [Test]
        public void CollisionRemainsTwoNonRenderingProxies()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(CollisionPath);
            Assert.That(prefab, Is.Not.Null);
            int[] triangles = prefab.GetComponentsInChildren<MeshFilter>(true)
                .Select(filter => filter.sharedMesh.triangles.Length / 3)
                .OrderBy(value => value)
                .ToArray();
            Assert.That(triangles, Is.EqualTo(new[] { 128, 128 }));
        }

        [Test]
        public void ArtworkPacksUseIndependentAstc4x4Imports()
        {
            string[] paths =
            {
                Root + "/Imported/artwork-upper-channel-pack.png",
                Root + "/Imported/artwork-lower-channel-pack.png"
            };
            Assert.That(paths.Distinct().Count(), Is.EqualTo(2));
            foreach (string path in paths)
            {
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                Assert.That(importer, Is.Not.Null);
                Assert.That(importer.sRGBTexture, Is.False);
                Assert.That(importer.mipmapEnabled, Is.True);
                TextureImporterPlatformSettings ios =
                    importer.GetPlatformTextureSettings("iPhone");
                Assert.That(ios.overridden, Is.True);
                Assert.That(ios.maxTextureSize, Is.EqualTo(1024));
                Assert.That(ios.format, Is.EqualTo(TextureImporterFormat.ASTC_4x4));
            }
        }

        [Test]
        public void ParitySceneCarriesSpecifiedOnlyMetadata()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var metadata = Object.FindFirstObjectByType<
                FidgetingApp.ModelPipeline.MagneticSlideTileParityMetadata>();
            Assert.That(metadata, Is.Not.Null);
            Assert.That(metadata.PointAxisMeters, Is.EqualTo(new Vector3(0f, 0f, 0.0095f)));
            Assert.That(metadata.SlideDirection, Is.EqualTo(Vector3.back));
            Assert.That(metadata.SlideTravelMeters, Is.EqualTo(0.021f).Within(0.000001f));
            Assert.That(metadata.DetentCount, Is.EqualTo(30));
            Assert.That(metadata.DetentStepDegrees, Is.EqualTo(12f));
            Assert.That(metadata.DetentDeliveryState, Is.EqualTo("specified-only"));
            Assert.That(metadata.UnityIntegrationState, Is.EqualTo("isolated-gate11-parity-only"));
        }

        [Test]
        public void UnityParityReportPassedWithoutShippingIntegration()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string reportPath = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-001/unity-import-parity-report.json");
            string json = File.ReadAllText(reportPath);
            StringAssert.Contains("\"pass\": true", json);
            StringAssert.Contains("\"shippingSceneModified\": false", json);
            StringAssert.Contains("\"shippingIntegrated\": false", json);
            StringAssert.Contains("\"deviceMemoryMeasured\": false", json);
        }
    }
}
