using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.Tests.Editor
{
    public sealed class MagneticSlideTilePortableLightingTests
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate08R003PortableValidation";
        private const string ScenePath =
            Root + "/Scenes/MagneticSlideTilePortableLightingR003.unity";

        [Test]
        public void PortableSceneUsesOneDirectionalAndNoSyntheticProbe()
        {
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Light[] lights = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Light>(true))
                .ToArray();
            Assert.That(lights, Has.Length.EqualTo(1));
            Assert.That(lights[0].type, Is.EqualTo(LightType.Directional));
            Assert.That(lights[0].color, Is.EqualTo(Color.white));
            Assert.That(lights[0].intensity, Is.EqualTo(0.75f).Within(0.0001f));
            Assert.That(
                scene.GetRootGameObjects()
                    .SelectMany(root => root.GetComponentsInChildren<ReflectionProbe>(true)),
                Is.Empty);
            Assert.That(
                scene.GetRootGameObjects()
                    .SelectMany(root => root.GetComponentsInChildren<Volume>(true)),
                Is.Empty);
        }

        [Test]
        public void PortableShaderContainsNoSyntheticSoftbox()
        {
            string project = Directory.GetParent(Application.dataPath)!.FullName;
            string source = File.ReadAllText(Path.Combine(
                project,
                Root,
                "Shaders/MagneticSlideTilePortableCrystal.shader"));
            Assert.That(source, Does.Not.Contain("broadSoftbox"));
            Assert.That(source, Does.Not.Contain("panelForward"));
            Assert.That(source, Does.Not.Contain("softboxFootprint"));
            Assert.That(source, Does.Contain("GlossyEnvironmentReflection"));
            Assert.That(source, Does.Contain("GetMainLight"));
        }

        [Test]
        public void PortableEnvironmentIsLinearAndReadable()
        {
            const string path = Root + "/Environment/portable-studio-r003.exr";
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            Assert.That(importer, Is.Not.Null);
            Assert.That(importer!.sRGBTexture, Is.False);
            Assert.That(importer.isReadable, Is.True);
            Assert.That(importer.textureCompression,
                Is.EqualTo(TextureImporterCompression.Uncompressed));
        }

        [Test]
        public void ShippingSceneWasNotUsedAsPortableCandidate()
        {
            Assert.That(
                AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath),
                Is.Not.Null);
            Assert.That(
                ScenePath,
                Is.Not.EqualTo("Assets/_EDC/Scenes/MeshyEDC.unity"));
        }
    }
}
