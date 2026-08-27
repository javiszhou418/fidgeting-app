using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MagneticSlideTileParityRev2Tests
    {
        private const string ProductPath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/magnetic-slide-tile-r002.fbx";
        private const string EnvironmentPath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev002/Materials/Gate11R2_DirectionContinuousEnvironment.cubemap";

        [Test]
        public void Rev2ReusesUnchangedImportedGeometry()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(ProductPath);
            Assert.That(prefab, Is.Not.Null);
            MeshFilter[] filters = prefab.GetComponentsInChildren<MeshFilter>(true);
            Assert.That(filters, Has.Length.EqualTo(2));
            Assert.That(
                filters.Sum(filter => filter.sharedMesh.triangles.Length / 3),
                Is.EqualTo(4096));
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
        public void Rev2EnvironmentUsesContinuousFilteredMipChain()
        {
            Cubemap environment = AssetDatabase.LoadAssetAtPath<Cubemap>(EnvironmentPath);
            Assert.That(environment, Is.Not.Null);
            Assert.That(environment.width, Is.EqualTo(256));
            Assert.That(environment.mipmapCount, Is.GreaterThanOrEqualTo(9));
            Assert.That(environment.filterMode, Is.EqualTo(FilterMode.Trilinear));
            Assert.That(environment.wrapMode, Is.EqualTo(TextureWrapMode.Clamp));
        }

        [Test]
        public void Rev2NormalProgressionMatchesDenseArc()
        {
            string json = ReadEvidence("unity-import-parity-report.json");
            StringAssert.Contains("\"gradualProgressionPass\": true", json);
            StringAssert.Contains("\"expectedSegmentsPerSemicircle\": 256", json);
            StringAssert.Contains("\"hardBoundaryPass\": true", json);
            StringAssert.Contains("\"importerNormalsChanged\": false", json);
            StringAssert.Contains("\"geometryChanged\": false", json);
            StringAssert.Contains("\"renderGeometryInflated\": false", json);
        }

        [Test]
        public void Rev2KeepsPatternDecisionSeparate()
        {
            string json = ReadEvidence("unity-import-parity-report.json");
            StringAssert.Contains(
                "\"patternPlacementDecision\": \"accepted-provisionally-not-under-review\"",
                json);
            StringAssert.Contains(
                "\"roundEdgeDecision\": \"rev1-rejected-rev2-pending\"",
                json);
            StringAssert.Contains("\"shippingSceneModified\": false", json);
            StringAssert.Contains("\"gate12Started\": false", json);
        }

        [Test]
        public void Rev2ProducesRealUnityReviewFrames()
        {
            foreach (string file in new[]
            {
                "unity-neutral.png",
                "unity-neutral-all-silver.png",
                "unity-wireframe.png"
            })
            {
                string path = EvidencePath(file);
                Assert.That(File.Exists(path), Is.True, file);
                Assert.That(new FileInfo(path).Length, Is.GreaterThan(4096), file);
            }
        }

        private static string ReadEvidence(string file) =>
            File.ReadAllText(EvidencePath(file));

        private static string EvidencePath(string file)
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            return Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-002",
                file);
        }
    }
}
