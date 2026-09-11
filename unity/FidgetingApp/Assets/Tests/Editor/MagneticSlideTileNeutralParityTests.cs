using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MagneticSlideTileNeutralParityTests
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate08R004NeutralParity";
        private const string ScenePath =
            Root + "/Scenes/MagneticSlideTileNeutralParityR004.unity";

        [Test]
        public void NeutralSceneHasOneReflectionSourceAndNoGroundOrLights()
        {
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject[] roots = scene.GetRootGameObjects();
            Assert.That(
                roots.SelectMany(root => root.GetComponentsInChildren<Light>(true)),
                Is.Empty);
            Assert.That(
                roots.SelectMany(root => root.GetComponentsInChildren<ReflectionProbe>(true)),
                Is.Empty);
            Assert.That(roots.Any(root => root.name.Contains("Ground")), Is.False);
            Assert.That(RenderSettings.skybox, Is.Null);
            Assert.That(
                RenderSettings.defaultReflectionMode,
                Is.EqualTo(DefaultReflectionMode.Skybox));
            Assert.That(RenderSettings.reflectionIntensity, Is.Zero);

            Material[] materials = roots
                .SelectMany(root => root.GetComponentsInChildren<Renderer>(true))
                .SelectMany(renderer => renderer.sharedMaterials)
                .Where(material => material != null)
                .Distinct()
                .ToArray();
            Assert.That(materials, Is.Not.Empty);
            Assert.That(
                materials.Where(material => material.HasProperty("_EnvironmentCube"))
                    .Select(material => material.GetTexture("_EnvironmentCube"))
                    .Distinct(),
                Has.Exactly(1).Not.Null);
        }

        [Test]
        public void EnvironmentImportPreservesHdrValues()
        {
            const string path = Root + "/Environment/neutral-parity-studio-r004.exr";
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            Assert.That(importer, Is.Not.Null);
            Assert.That(importer!.sRGBTexture, Is.False);
            Assert.That(importer.isReadable, Is.True);
            Assert.That(importer.mipmapEnabled, Is.False);
            Assert.That(
                importer.GetDefaultPlatformTextureSettings().format,
                Is.EqualTo(TextureImporterFormat.RGBAHalf));
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            Assert.That(texture.graphicsFormat, Is.EqualTo(GraphicsFormat.R16G16B16A16_SFloat));
            Assert.That(
                texture.GetPixels().Max(pixel => Mathf.Max(pixel.r, pixel.g, pixel.b)),
                Is.GreaterThan(5.6f));
        }

        [Test]
        public void NeutralShadersContainNoSecondLightingPath()
        {
            string project = Directory.GetParent(Application.dataPath)!.FullName;
            foreach (string name in new[]
            {
                "MagneticSlideTileNeutralSurfaceR004.shader",
                "MagneticSlideTileNeutralCrystalR004.shader"
            })
            {
                string source = File.ReadAllText(
                    Path.Combine(project, Root, "Shaders", name));
                Assert.That(source, Does.Contain("SAMPLE_TEXTURECUBE_LOD"));
                Assert.That(source, Does.Contain("_EnvironmentCube"));
                Assert.That(source, Does.Not.Contain("GetMainLight"));
                Assert.That(source, Does.Not.Contain("SampleSH"));
                Assert.That(source, Does.Not.Contain("GlossyEnvironmentReflection"));
                Assert.That(source, Does.Not.Contain("softbox"));
                Assert.That(source, Does.Not.Contain("Emission"));
            }
        }

        [Test]
        public void ReportsKeepDownstreamGatesBlocked()
        {
            string project = Directory.GetParent(Application.dataPath)!.FullName;
            string evidence = Path.Combine(
                project,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-004");
            string unity = File.ReadAllText(
                Path.Combine(evidence, "neutral-parity-unity-report.json"));
            string audit = File.ReadAllText(
                Path.Combine(evidence, "neutral-parity-audit.json"));
            Assert.That(unity, Does.Contain("\"reflectionSourceCount\": 1"));
            Assert.That(unity, Does.Contain("\"sourceTextureFormat\": \"R16G16B16A16_SFloat\""));
            Assert.That(unity, Does.Contain("\"shippingSceneModified\": false"));
            Assert.That(audit, Does.Contain("\"status\": \"ready-for-interactive-review-not-approved\""));
            Assert.That(audit, Does.Contain("\"approved\": false"));
            Assert.That(audit, Does.Contain("\"gate09Advanced\": false"));
            Assert.That(audit, Does.Contain("\"gate11Advanced\": false"));
            Assert.That(audit, Does.Contain("\"gate12Advanced\": false"));
        }
    }
}
