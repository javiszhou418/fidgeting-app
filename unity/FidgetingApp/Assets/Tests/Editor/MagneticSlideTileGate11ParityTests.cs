using System.Collections;
using System.IO;
using System.Linq;
using FidgetingApp.EDC.Candidates;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.TestTools;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MagneticSlideTileGate11ParityTests
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R010";
        private const string SourceRoot =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R009";
        private const string ProductPath =
            SourceRoot + "/Imported/magnetic-slide-tile-render-r009.fbx";
        private const string CollisionPath =
            SourceRoot + "/Imported/magnetic-slide-tile-collision-r009.fbx";
        private const string ScenePath =
            Root + "/Scenes/MagneticSlideTileGate11R010Parity.unity";

        [Test]
        public void ImportedRenderModelPreservesEightMeshHierarchy()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(ProductPath);
            Assert.That(prefab, Is.Not.Null);
            MeshFilter[] filters = prefab.GetComponentsInChildren<MeshFilter>(true);
            Assert.That(filters, Has.Length.EqualTo(8));
            string[] names = filters.Select(filter => filter.name)
                .OrderBy(name => name)
                .ToArray();
            Assert.That(names, Is.EqualTo(new[]
            {
                "BallCandidateLeft",
                "BallCandidateRight",
                "BottomExterior",
                "CarrierFollowerLeft",
                "CarrierFollowerRight",
                "FixedAxisBoss",
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
        public void ImportSettingsPreserveNpotAndLosslessParitySources()
        {
            ModelImporter model = AssetImporter.GetAtPath(ProductPath) as ModelImporter;
            Assert.That(model, Is.Not.Null);
            Assert.That(model.meshCompression, Is.EqualTo(ModelImporterMeshCompression.Off));
            Assert.That(model.importNormals, Is.EqualTo(ModelImporterNormals.Import));
            Assert.That(model.importTangents, Is.EqualTo(ModelImporterTangents.Import));
            Assert.That(model.importAnimation, Is.False);

            string[] baseTextures =
            {
                SourceRoot + "/Imported/Textures/upperBaseColor.png",
                SourceRoot + "/Imported/Textures/lowerBaseColor.png"
            };
            foreach (string path in baseTextures)
            {
                TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
                Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                Assert.That(importer, Is.Not.Null);
                Assert.That(texture, Is.Not.Null);
                Assert.That(texture.width, Is.EqualTo(620));
                Assert.That(texture.height, Is.EqualTo(1000));
                Assert.That(importer.npotScale, Is.EqualTo(TextureImporterNPOTScale.None));
                Assert.That(importer.sRGBTexture, Is.True);
                Assert.That(importer.textureCompression,
                    Is.EqualTo(TextureImporterCompression.Uncompressed));
            }
        }

        [Test]
        public void ParitySceneKeepsShippingSceneUntouchedAndCandidateIsolated()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            MagneticSlideTileGate11Metadata metadata =
                Object.FindAnyObjectByType<MagneticSlideTileGate11Metadata>();
            MagneticSlideTileGate11PreviewController controller =
                Object.FindAnyObjectByType<MagneticSlideTileGate11PreviewController>();
            Assert.That(metadata, Is.Not.Null);
            Assert.That(controller, Is.Not.Null);
            Assert.That(metadata.Gate10GlbSha256,
                Is.EqualTo("f95b1b2ebed5859aa185aa4e3ba81dcb7a8de266ac9244f4b3270b35c877cba6"));
            Assert.That(metadata.DetentCount, Is.EqualTo(30));
            Assert.That(metadata.DetentStepDegrees, Is.EqualTo(12f));
            Assert.That(metadata.DeliveryState,
                Is.EqualTo("isolated-gate11-parity-only"));
            Assert.That(controller.RotatingCarrier, Is.Not.Null);
            Assert.That(controller.MovingTop, Is.Not.Null);
            Assert.That(controller.TopLocalSlide, Is.Not.Null);
            ReflectionProbe probe = Object.FindAnyObjectByType<ReflectionProbe>();
            Assert.That(probe, Is.Not.Null);
            Assert.That(probe.boxProjection, Is.True);
            GameObject ground = GameObject.Find("Gate11R010Ground");
            Assert.That(ground, Is.Not.Null);
            Assert.That(ground.GetComponent<Renderer>().receiveShadows, Is.True);
            Assert.That(Object.FindAnyObjectByType<Camera>().focalLength,
                Is.EqualTo(76f).Within(0.001f));
        }

        [Test]
        public void CollisionStaysSeparateAndNonRendering()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(CollisionPath);
            Assert.That(prefab, Is.Not.Null);
            MeshFilter[] filters = prefab.GetComponentsInChildren<MeshFilter>(true);
            Assert.That(filters, Has.Length.EqualTo(2));
        }

        [Test]
        public void UnityTransportPassesWithoutShippingIntegration()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string path = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-010/unity-import-parity-report.json");
            Assert.That(File.Exists(path), Is.True);
            string json = File.ReadAllText(path);
            StringAssert.Contains("\"pass\": true", json);
            StringAssert.Contains("\"shippingSceneModified\": false", json);
            StringAssert.Contains("\"oldShippingModelDefault\": true", json);
            StringAssert.Contains("\"gate12Started\": false", json);
            StringAssert.Contains("\"buildInstallDevice\": false", json);
        }

        [Test]
        public void FullFrameValidatorBlocksReviewWhenVisualMetricsFail()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string path = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-010/full-frame-parity-report.json");
            Assert.That(File.Exists(path), Is.True);
            string json = File.ReadAllText(path);
            StringAssert.Contains("\"sameFullFrame\": true", json);
            StringAssert.Contains("\"independentCropping\": false", json);
            StringAssert.Contains("\"cameraAndBbox\": true", json);
            StringAssert.Contains("\"hotspot\": false", json);
            StringAssert.Contains("\"clayGradient\": false", json);
            StringAssert.Contains("\"pass\": false", json);
        }

        [UnityTest]
        public IEnumerator PreviewControllerUsesSeparateCompoundPosesAndResets()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            MagneticSlideTileGate11PreviewController controller =
                Object.FindAnyObjectByType<MagneticSlideTileGate11PreviewController>();
            Assert.That(controller, Is.Not.Null);
            Vector3 closedPosition = controller.TopLocalSlide.localPosition;

            controller.SetPose(36f, 0.009f);
            yield return null;

            Assert.That(controller.AngleDegrees, Is.EqualTo(36f).Within(0.001f));
            Assert.That(controller.TravelMeters, Is.EqualTo(0.009f).Within(0.000001f));
            Assert.That(
                Quaternion.Angle(
                    controller.RotatingCarrier.localRotation,
                    controller.MovingTop.localRotation),
                Is.LessThan(0.001f));
            Assert.That(
                Vector3.Distance(
                    controller.TopLocalSlide.localPosition,
                    closedPosition),
                Is.EqualTo(0.009f).Within(0.00001f));

            controller.ResetPose();
            yield return null;
            Assert.That(controller.AngleDegrees, Is.EqualTo(0f));
            Assert.That(controller.TravelMeters, Is.EqualTo(0f));
            Assert.That(controller.TopLocalSlide.localPosition, Is.EqualTo(closedPosition));
        }
    }
}
