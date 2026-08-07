using System;
using System.Linq;
using CodexUnityLab;
using FidgetingApp.EDC.EditorTools;
using FidgetingApp.EDC;
using FidgetingApp.Product;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Tests.Editor
{
    public sealed class EdcSliderAcceptanceTests
    {
        private const string ScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private SceneSetup[] previousSceneSetup;
        private Scene scene;
        private Transform root;

        [SetUp]
        public void OpenScene()
        {
            previousSceneSetup = EditorSceneManager.GetSceneManagerSetup();
            Assert.That(AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath), Is.Not.Null);
            scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            root = scene.GetRootGameObjects()
                .Single(candidate => candidate.name == "EDC_Root")
                .transform;
        }

        [TearDown]
        public void RestoreScene()
        {
            if (previousSceneSetup != null
                && previousSceneSetup.Any(setup => setup.isLoaded))
            {
                EditorSceneManager.RestoreSceneManagerSetup(previousSceneSetup);
                return;
            }
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        }

        [Test]
        public void MagneticProfile_DefinesSixHeavyDetentsAnd68MillimeterTravel()
        {
            EdcSliderController controller = root.GetComponent<EdcSliderController>();
            LinearMagneticDetentProfile profile = controller.Profile;
            Assert.That(profile, Is.Not.Null);
            Assert.That(profile.DetentCount, Is.EqualTo(6));
            Assert.That(profile.TravelMeters, Is.EqualTo(0.068f).Within(0.000001f));
            Assert.That(profile.DefaultDetentIndex, Is.EqualTo(2));
            Assert.That(profile.DefaultPositionMeters, Is.EqualTo(0.0272f).Within(0.000001f));
            Assert.That(profile.BreakawayForceNewtons, Is.EqualTo(0.44f));
            Assert.That(profile.MagneticPeakForceNewtons, Is.EqualTo(0.42f));
            Assert.That(profile.MaximumIntegrationStepSeconds, Is.EqualTo(1f / 240f));
            Assert.That(profile.EdgeProbeLoads, Is.EqualTo(new[] { 0.72f, 0.84f, 0.94f }));
            Assert.That(profile.EdgeProbeMinimumIntensity, Is.EqualTo(0.08f));
            Assert.That(profile.EdgeProbeMaximumIntensity, Is.EqualTo(0.14f));
            Assert.That(profile.EdgeProbeMinimumSharpness, Is.EqualTo(0.14f));
            Assert.That(profile.EdgeProbeMaximumSharpness, Is.EqualTo(0.22f));
            Assert.That(profile.DetentHapticIntensity, Is.EqualTo(0.28f));
            Assert.That(profile.DetentHapticSharpness, Is.EqualTo(0.46f));
            Assert.That(profile.DetentHapticSecondaryIntensity, Is.EqualTo(0.14f));
            Assert.That(profile.DetentHapticSecondarySharpness, Is.EqualTo(0.28f));
            Assert.That(profile.CrossingMaximumDurationSeconds, Is.EqualTo(0.080f));
        }

        [Test]
        public void AlloyClick766HzAudio_IsWiredToAuthorizedDetentCrossingsOnly()
        {
            EdcSliderController controller = root.GetComponent<EdcSliderController>();
            MagneticSlideDetentAudio[] renderers =
                root.GetComponentsInChildren<MagneticSlideDetentAudio>(true);
            AudioSource[] audioSources = root.GetComponentsInChildren<AudioSource>(true);

            Assert.That(renderers, Has.Length.EqualTo(1));
            MagneticSlideDetentAudio renderer = renderers[0];
            Assert.That(renderer.Slider, Is.SameAs(controller));
            Assert.That(renderer.EffectClip, Is.Not.Null);
            Assert.That(
                AssetDatabase.GetAssetPath(renderer.EffectClip),
                Is.EqualTo(EdcSceneBuilder.MagneticSlideEffectPath));
            Assert.That(renderer.EffectClip.channels, Is.EqualTo(1));
            Assert.That(renderer.EffectClip.frequency, Is.EqualTo(48000));
            Assert.That(renderer.EffectClip.length, Is.EqualTo(0.93f).Within(0.01f));
            Assert.That(
                renderer.MasterVolume,
                Is.EqualTo(MagneticSlideAudioModel.DefaultMasterVolume));
            Assert.That(
                renderer.Voices,
                Has.Length.EqualTo(MagneticSlideAudioModel.VoiceCount));
            Assert.That(audioSources, Has.Length.EqualTo(renderer.Voices.Length));
            foreach (AudioSource voice in renderer.Voices)
            {
                Assert.That(voice, Is.Not.Null);
                Assert.That(voice.clip, Is.Null);
                Assert.That(voice.playOnAwake, Is.False);
                Assert.That(voice.loop, Is.False);
                Assert.That(voice.spatialBlend, Is.Zero);
                Assert.That(voice.reverbZoneMix, Is.Zero);
                Assert.That(voice.bypassReverbZones, Is.True);
            }

            Assert.That(
                MagneticSlideAudioModel.ShouldRender(FidgetSemanticEvent.DetentCrossed),
                Is.True);
            Assert.That(
                MagneticSlideAudioModel.ShouldRender(FidgetSemanticEvent.Breakaway),
                Is.False);
            Assert.That(
                MagneticSlideAudioModel.ShouldRender(FidgetSemanticEvent.DetentCaptured),
                Is.False,
                "Capture must not create a second click after the crossing sound.");
        }

        [Test]
        public void AlloyClick766HzAudio_HasOneTransientAndNoSecondClick()
        {
            AudioClip clip = root
                .GetComponentInChildren<MagneticSlideDetentAudio>(true)
                .EffectClip;
            var samples = new float[clip.samples * clip.channels];
            Assert.That(clip.GetData(samples, 0), Is.True);

            int headEnd = Mathf.RoundToInt(0.08f * clip.frequency);
            float headPeak = 0f;
            float postHeadPeak = 0f;
            for (int index = 0; index < samples.Length; index++)
            {
                float magnitude = Mathf.Abs(samples[index]);
                if (index < headEnd)
                {
                    headPeak = Mathf.Max(headPeak, magnitude);
                }
                else
                {
                    postHeadPeak = Mathf.Max(postHeadPeak, magnitude);
                }
            }

            Assert.That(headPeak, Is.GreaterThan(0.10f));
            Assert.That(
                postHeadPeak,
                Is.LessThan(headPeak * 0.10f),
                "The effect must not contain a second click transient.");
        }

        [Test]
        public void SceneHierarchy_ContainsSevenLayersSixMagnetsAndFourScrews()
        {
            Transform slider = Require(root, "SliderGroup");
            Transform baseGroup = Require(root, "Base");
            Transform screws = Require(root, "Screws");

            Assert.That(Require(slider, "L1_TopFrame"), Is.Not.Null);
            Assert.That(Require(slider, "L2_UpperShell"), Is.Not.Null);
            Assert.That(Require(baseGroup, "L3_Gasket"), Is.Not.Null);
            Transform rails = Require(baseGroup, "L4_SlideRails");
            Transform magnets = Require(baseGroup, "L5_Magnets");
            Assert.That(Require(baseGroup, "L6_InnerFrame"), Is.Not.Null);
            Assert.That(Require(baseGroup, "L7_BottomShell"), Is.Not.Null);

            Assert.That(rails.childCount, Is.EqualTo(2));
            Assert.That(rails.Cast<Transform>().Select(child => child.name), Is.EquivalentTo(
                new[] { "Rail_Left", "Rail_Right" }));
            Assert.That(magnets.childCount, Is.EqualTo(6));
            Assert.That(
                magnets.Cast<Transform>().Select(child => child.name),
                Is.EquivalentTo(Enumerable.Range(1, 6).Select(index => $"Magnet_{index:D2}")));
            LinearMagneticDetentProfile profile =
                root.GetComponent<EdcSliderController>().Profile;
            float centerOffset = profile.TravelMeters * 0.5f;
            for (int index = 0; index < profile.DetentCount; index++)
            {
                Transform magnet = Require(magnets, $"Magnet_{index + 1:D2}");
                Assert.That(
                    magnet.localPosition.x,
                    Is.EqualTo(profile.GetDetentPositionMeters(index) - centerOffset)
                        .Within(0.000001f));
            }
            Assert.That(screws.childCount, Is.EqualTo(4));
            Assert.That(
                screws.Cast<Transform>().Select(child => child.name),
                Is.EquivalentTo(Enumerable.Range(1, 4).Select(index => $"Screw_{index:D2}")));
        }

        [Test]
        public void CutLayers_PreserveCenteredPivotsUvsAndExplicitUrpMaterials()
        {
            string[] cutLayerPaths =
            {
                "SliderGroup/L1_TopFrame",
                "SliderGroup/L2_UpperShell",
                "Base/L3_Gasket",
                "Base/L6_InnerFrame",
                "Base/L7_BottomShell"
            };
            foreach (string path in cutLayerPaths)
            {
                Transform layer = Require(root, path);
                MeshFilter filter = layer.GetComponent<MeshFilter>();
                MeshRenderer renderer = layer.GetComponent<MeshRenderer>();
                Assert.That(filter, Is.Not.Null, path);
                Assert.That(renderer, Is.Not.Null, path);
                Assert.That(filter.sharedMesh, Is.Not.Null, path);
                Assert.That(
                    filter.sharedMesh.bounds.center.magnitude,
                    Is.LessThan(0.00001f),
                    $"{path} pivot must be its own bounds center.");
                Assert.That(
                    filter.sharedMesh.uv.Length,
                    Is.EqualTo(filter.sharedMesh.vertexCount),
                    $"{path} must preserve one UV per vertex.");
                Assert.That(renderer.sharedMaterial, Is.Not.Null, path);
                Assert.That(
                    renderer.sharedMaterial.shader.name,
                    Is.EqualTo("Universal Render Pipeline/Lit"),
                    path);
                Assert.That(renderer.sharedMaterial.name, Does.Not.Contain("Default"));
            }

            Material textured = Require(root, "SliderGroup/L1_TopFrame")
                .GetComponent<MeshRenderer>().sharedMaterial;
            Assert.That(textured.GetTexture("_BaseMap"), Is.Not.Null);
            Assert.That(textured.GetTexture("_MetallicGlossMap"), Is.Not.Null);
            Assert.That(textured.GetTexture("_BumpMap"), Is.Not.Null);
            Assert.That(textured.GetTexture("_EmissionMap"), Is.Not.Null);
            Assert.That(
                Require(root, "Base/L3_Gasket").GetComponent<MeshRenderer>()
                    .sharedMaterial.name,
                Is.EqualTo("M_EDC_DarkPolymer"));
        }

        [Test]
        public void Controller_MovesOnlySliderGroupAlongLocalXAndExposesToggleContract()
        {
            EdcSliderController controller = root.GetComponent<EdcSliderController>();
            Transform slider = Require(root, "SliderGroup");
            Transform baseGroup = Require(root, "Base");
            Vector3 basePosition = baseGroup.localPosition;
            float expectedTravel = controller.Profile.TravelMeters;

            Assert.That(controller, Is.Not.Null);
            Assert.That(controller.TravelDistance, Is.EqualTo(expectedTravel).Within(0.0001f));
            controller.ResetToDefaultDetent();
            Assert.That(controller.CapturedDetentIndex, Is.EqualTo(2));
            Assert.That(slider.localPosition, Is.EqualTo(Vector3.zero));
            controller.SetSlideProgress(0f);
            Assert.That(
                slider.localPosition.x,
                Is.EqualTo(-controller.Profile.DefaultPositionMeters).Within(0.0001f));
            controller.SetSlideProgress(1f);
            Assert.That(
                slider.localPosition.x,
                Is.EqualTo(expectedTravel - controller.Profile.DefaultPositionMeters)
                    .Within(0.0001f));
            Assert.That(slider.localPosition.y, Is.EqualTo(0f).Within(0.0001f));
            Assert.That(slider.localPosition.z, Is.EqualTo(0f).Within(0.0001f));
            Assert.That(baseGroup.localPosition, Is.EqualTo(basePosition));

            controller.Toggle();
            Assert.That(controller.IsSettling, Is.True);
            Assert.That(typeof(EdcSliderController).GetMethod("Toggle"), Is.Not.Null);
        }

        [Test]
        public void DetailCamera_UsesFrontTopProductScaleAndExpandedTouchSurface()
        {
            Camera camera = scene.GetRootGameObjects()
                .SelectMany(sceneRoot => sceneRoot.GetComponentsInChildren<Camera>(true))
                .Single();
            Assert.That(camera, Is.Not.Null);
            EdcPortraitCameraFramer framer = camera.GetComponent<EdcPortraitCameraFramer>();
            Assert.That(framer, Is.Not.Null);
            Assert.That(framer.Target, Is.EqualTo(root));
            Assert.That(
                framer.ScreenWidthFraction,
                Is.EqualTo(EdcPortraitCameraFramer.DefaultScreenWidthFraction));
            Assert.That(
                framer.ScreenHeightFraction,
                Is.EqualTo(EdcPortraitCameraFramer.DefaultScreenHeightFraction));
            Assert.That(camera.usePhysicalProperties, Is.True);
            Assert.That(camera.gateFit, Is.EqualTo(Camera.GateFitMode.Horizontal));
            Assert.That(
                camera.focalLength,
                Is.EqualTo(EdcPortraitCameraFramer.DefaultFocalLengthMillimeters));

            camera.aspect = 1290f / 2796f;
            Require(root, "SliderGroup").localPosition = Vector3.zero;
            framer.FrameNow();
            Assert.That(
                ProductCameraFraming.TryGetProductBounds(root, out Bounds bounds),
                Is.True);
            Vector2 viewportSize = ProductCameraFraming.ProjectedViewportSize(
                camera,
                bounds);
            Assert.That(
                viewportSize.x,
                Is.LessThanOrEqualTo(framer.ScreenWidthFraction + 0.03f));
            Assert.That(
                viewportSize.y,
                Is.LessThanOrEqualTo(framer.ScreenHeightFraction + 0.03f));
            Assert.That(
                Mathf.Max(
                    viewportSize.x / framer.ScreenWidthFraction,
                    viewportSize.y / framer.ScreenHeightFraction),
                Is.InRange(0.90f, 1.03f));

            Vector3 detailBackward = (camera.transform.position - bounds.center).normalized;
            Assert.That(
                detailBackward.x,
                Is.EqualTo(0f).Within(0.001f),
                "The detail camera must not foreshorten the horizontal slide axis.");
            Assert.That(
                Vector3.Dot(
                    detailBackward,
                    EdcPortraitCameraFramer.DefaultDetailFramingBackward.normalized),
                Is.GreaterThan(0.999f));

            Vector3 leftScreen = camera.WorldToViewportPoint(
                bounds.center - Vector3.right * bounds.extents.x);
            Vector3 rightScreen = camera.WorldToViewportPoint(
                bounds.center + Vector3.right * bounds.extents.x);
            Assert.That(
                Mathf.Abs(rightScreen.y - leftScreen.y),
                Is.LessThan(0.001f),
                "The rail must read as a horizontal gesture in the detail view.");

            Transform interactionSurface = Require(
                root,
                "SliderGroup/InteractionSurface");
            BoxCollider surface = interactionSurface.GetComponent<BoxCollider>();
            Assert.That(surface, Is.Not.Null);
            Assert.That(
                surface.size,
                Is.EqualTo(EdcSliderController.DefaultInteractionSurfaceSize));
            Assert.That(surface.size.x, Is.GreaterThan(0.08f));
            Assert.That(surface.size.z, Is.GreaterThan(0.047f));
        }

        [Test]
        public void SceneTriangleCount_IsSourceFaithfulAndExplicitlyNotMobileOptimized()
        {
            int triangles = root.GetComponentsInChildren<MeshFilter>(true)
                .Where(filter => filter.sharedMesh != null)
                .Sum(filter => filter.sharedMesh.triangles.Length / 3);
            Assert.That(triangles, Is.GreaterThanOrEqualTo(1_994_857));
            Assert.That(triangles, Is.LessThan(2_000_000));
        }

        private static Transform Require(Transform parent, string path)
        {
            Transform result = parent.Find(path);
            Assert.That(result, Is.Not.Null, $"Missing hierarchy path: {path}");
            return result;
        }
    }
}
