using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using CodexUnityLab;
using FidgetingApp.EDC.Gate12R002;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.TestTools;

namespace FidgetingApp.EDC.Tests
{
    public sealed class MagneticSlideTileGate12R002Tests
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002";
        private const string ScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";

        [Test]
        public void SharedSettingsOwnAllEndpointAndDetentValues()
        {
            MagneticSlideTileMechanismSettings settings =
                AssetDatabase.LoadAssetAtPath<MagneticSlideTileMechanismSettings>(
                    Root + "/Settings/MagneticSlideTileMechanismSettingsR002.asset");
            Assert.That(settings, Is.Not.Null);
            Assert.That(settings.MaximumTravelMeters, Is.EqualTo(0.018076433f)
                .Within(0.000000001f));
            Assert.That(settings.EndpointToleranceMeters, Is.EqualTo(0.000001f));
            Assert.That(settings.SlideStepCount, Is.EqualTo(4));
            Assert.That(
                settings.SlideStepMeters * settings.SlideStepCount,
                Is.EqualTo(settings.MaximumTravelMeters).Within(0.000000001f));
            Assert.That(settings.DetentCount, Is.EqualTo(30));
            Assert.That(settings.DetentStepDegrees, Is.EqualTo(12f));
            Assert.That(
                settings.DetentCount * settings.DetentStepDegrees,
                Is.EqualTo(360f));
        }

        [Test]
        public void ShippingScenePromotesApprovedCandidateByDefault()
        {
            EditorSceneManager.OpenScene(ScenePath);
            GameObject oldModel = GameObject.Find("EDC_Root");
            MagneticSlideTileShippingCoordinator coordinator =
                Object.FindFirstObjectByType<MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include);
            Assert.That(coordinator, Is.Not.Null);
            Assert.That(oldModel, Is.Null);
            Assert.That(coordinator.CandidatePreviewEnabled, Is.True);
            Assert.That(coordinator.CandidateModelActive, Is.True);
            Assert.That(coordinator.FallbackModelActive, Is.False);
            Assert.That(coordinator.Mechanism.gameObject.activeSelf, Is.True);
            Assert.That(coordinator.Settings, Is.SameAs(
                coordinator.Mechanism.Settings));
            Assert.That(coordinator.DeviceHapticAcceptancePending, Is.True);
        }

        [Test]
        public void ShippingSceneWiresPointerInputToApprovedCandidate()
        {
            EditorSceneManager.OpenScene(ScenePath);
            MagneticSlideTileShippingCoordinator coordinator =
                Object.FindFirstObjectByType<MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include);
            EdcSliderController input = coordinator.CandidateModel
                .GetComponent<EdcSliderController>();
            Assert.That(input, Is.Not.Null);
            Assert.That(input.enabled, Is.True);
            Assert.That(input.UsesShippingMechanism, Is.True);
            Assert.That(input.ShippingCoordinator, Is.SameAs(coordinator));
            Assert.That(input.InteractionCamera, Is.SameAs(Camera.main));
            Assert.That(input.InteractionSurface, Is.Not.Null);
            Assert.That(
                input.InteractionSurface.transform.parent,
                Is.SameAs(coordinator.Mechanism.TopLocalSlide));
            Assert.That(input.InteractionSurface.enabled, Is.True);
            Assert.That(input.Profile, Is.Not.Null);
            Assert.That(input.PresentationGestures, Is.Not.Null);
            Assert.That(
                input.PresentationGestures.ProductInteractionSurface,
                Is.SameAs(input.InteractionSurface));
            EdcPortraitCameraFramer framer =
                Camera.main.GetComponent<EdcPortraitCameraFramer>();
            Assert.That(
                framer.Target,
                Is.SameAs(coordinator.CandidateModel.transform));
            Assert.That(framer.UsesStableLocalBounds, Is.True);
            Assert.That(framer.PreservesAuthoredDefaultPose, Is.True);
            MagneticSlideDetentAudio audio =
                coordinator.CandidateModel.GetComponentInChildren<
                    MagneticSlideDetentAudio>(true);
            Assert.That(audio, Is.Not.Null);
            Assert.That(audio.Slider, Is.SameAs(input));
            Assert.That(
                audio.Voices,
                Has.Length.EqualTo(MagneticSlideAudioModel.VoiceCount));
            Assert.That(
                Object.FindFirstObjectByType<EventSystem>(
                    FindObjectsInactive.Include),
                Is.Null);
            Assert.That(
                coordinator.CandidateModel.GetComponent<PlayerInput>(),
                Is.Null);
            InputActionAsset inputActions =
                AssetDatabase.LoadAssetAtPath<InputActionAsset>(
                    "Assets/InputSystem_Actions.inputactions");
            Assert.That(inputActions, Is.Not.Null);
            Assert.That(
                inputActions.FindActionMap("UI", true)
                    .FindAction("Point", true).bindings
                    .Any(binding =>
                        binding.path == "<Touchscreen>/touch*/position"),
                Is.True);
            Assert.That(
                coordinator.CandidateModel.GetComponentsInChildren<Collider>(true)
                    .Count(collider =>
                        collider != input.InteractionSurface && collider.enabled),
                Is.Zero);

            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            EditorSceneManager.OpenScene(ScenePath);
            coordinator =
                Object.FindFirstObjectByType<MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include);
            input = coordinator.CandidateModel.GetComponent<EdcSliderController>();
            Assert.That(input.ShippingCoordinator, Is.SameAs(coordinator));
            Assert.That(input.InteractionSurface, Is.Not.Null);
        }

        [UnityTest]
        public IEnumerator ShippingScenePlayModeUsesApprovedAttachedMotion()
        {
            EditorSceneManager.OpenScene(ScenePath);
            yield return new EnterPlayMode();
            yield return null;

            MagneticSlideTileShippingCoordinator coordinator =
                Object.FindFirstObjectByType<MagneticSlideTileShippingCoordinator>();
            Assert.That(coordinator, Is.Not.Null);
            Assert.That(coordinator.CandidatePreviewEnabled, Is.True);
            Assert.That(coordinator.CandidateModelActive, Is.True);
            Assert.That(coordinator.FallbackModelActive, Is.False);

            MagneticSlideTileShippingMechanism mechanism = coordinator.Mechanism;
            mechanism.ResetPose(false);
            Assert.That(mechanism.LinearVelocityMetersPerSecond, Is.Zero);
            Assert.That(mechanism.AngularVelocityDegreesPerSecond, Is.Zero);
            Assert.That(coordinator.TryApplyRotationInput(12f, false), Is.False);
            Assert.That(coordinator.TryApplySlideInput(
                coordinator.Settings.MaximumTravelMeters, false), Is.True);
            Assert.That(coordinator.TryApplyRotationInput(12f, false), Is.True);
            Assert.That(mechanism.TopStackHeightResidualMeters,
                Is.LessThanOrEqualTo(0.000000005f));
            Assert.That(mechanism.OutOfPlaneSlideResidualMeters, Is.Zero);
            Assert.That(mechanism.FixedAxisConstraintResidual, Is.Zero);
            Assert.That(mechanism.RenderersRemainAttached, Is.True);
            Assert.That(mechanism.IsPoseLegal(), Is.True);

            yield return new ExitPlayMode();
        }

        [Test]
        public void ApprovedGeometryAndMaterialsRemainExact()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                Root + "/Prefabs/MagneticSlideTileGate12R002Candidate.prefab");
            Assert.That(prefab, Is.Not.Null);
            Transform[] transforms = prefab.GetComponentsInChildren<Transform>(true);
            Assert.That(transforms.Count(item => item.name == "FixedAxis"), Is.EqualTo(1));
            Assert.That(transforms.Count(item =>
                    item.name.Contains("Top") && item.name.Contains("Groove")),
                Is.EqualTo(4));
            Assert.That(transforms.Any(item => item.name == "BottomExterior"), Is.True);
            Assert.That(transforms.Any(item => item.name == "RotatingCarrier"), Is.True);
            Assert.That(transforms.Any(item => item.name == "TopLocalSlide"), Is.True);
            Assert.That(transforms.Any(item => item.name.Contains("Cavity")), Is.False);
            Assert.That(transforms.Any(item => item.name.Contains("Proxy")), Is.False);

            Renderer[] renderers = prefab.GetComponentsInChildren<Renderer>(true);
            Assert.That(renderers.Count(renderer => renderer.enabled), Is.EqualTo(2));
            int triangles = prefab.GetComponentsInChildren<MeshFilter>(true)
                .Sum(filter => filter.sharedMesh.triangles.Length / 3);
            Assert.That(triangles, Is.EqualTo(99280));
            foreach (Material material in renderers
                .SelectMany(renderer => renderer.sharedMaterials)
                .Where(material => material != null)
                .Distinct())
            {
                Assert.That(material.shader.name,
                    Is.EqualTo("FidgetingApp/MagneticSlideTile/PortablePBRR011"));
                Assert.That(material.IsKeywordEnabled("_EMISSION"), Is.False);
            }
        }

        [Test]
        public void EndpointInterlockStopsAllUnauthorizedMotion()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                Root + "/Prefabs/MagneticSlideTileGate12R002Candidate.prefab");
            GameObject instance = Object.Instantiate(prefab);
            MagneticSlideTileShippingMechanism mechanism =
                instance.GetComponent<MagneticSlideTileShippingMechanism>();
            List<FidgetSemanticEvent> semanticEvents = new();
            mechanism.SemanticEventRaised +=
                (semanticEvent, _) => semanticEvents.Add(semanticEvent);
            mechanism.ResetPose(false);
            Assert.That(mechanism.TrySetAngle(12f), Is.False);
            Assert.That(mechanism.TrySetTravel(
                mechanism.Settings.MaximumTravelMeters * 0.5f), Is.True);
            Assert.That(mechanism.TrySetAngle(12f), Is.False);
            Assert.That(mechanism.TrySetTravel(
                mechanism.Settings.MaximumTravelMeters, true), Is.True);
            Assert.That(mechanism.TryBeginRotation(1f), Is.False);
            Assert.That(mechanism.TryBeginRotation(12f, true), Is.True);
            Assert.That(mechanism.TrySetAngle(36f, true), Is.True);
            Assert.That(mechanism.TrySetTravel(0f), Is.False);
            Assert.That(mechanism.TrySetAngle(360f), Is.True);
            Assert.That(mechanism.TrySetTravel(0f), Is.True);
            Assert.That(semanticEvents,
                Does.Contain(FidgetSemanticEvent.Breakaway));
            Assert.That(semanticEvents,
                Does.Contain(FidgetSemanticEvent.DetentCrossed));
            Assert.That(mechanism.IsPoseLegal(), Is.True);
            Assert.That(mechanism.LinearVelocityMetersPerSecond, Is.Zero);
            Assert.That(mechanism.AngularVelocityDegreesPerSecond, Is.Zero);
            Object.DestroyImmediate(instance);
        }

        [Test]
        public void FullMotionKeepsOneConnectedInPlaneStack()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                Root + "/Prefabs/MagneticSlideTileGate12R002Candidate.prefab");
            GameObject instance = Object.Instantiate(prefab);
            MagneticSlideTileShippingMechanism mechanism =
                instance.GetComponent<MagneticSlideTileShippingMechanism>();
            mechanism.ResetPose(false);

            Assert.That(mechanism.TrySetTravel(
                mechanism.Settings.MaximumTravelMeters), Is.True);
            Assert.That(mechanism.AngleDegrees, Is.Zero);
            Assert.That(mechanism.TopStackHeightResidualMeters,
                Is.LessThanOrEqualTo(0.000001f));
            Assert.That(mechanism.OutOfPlaneSlideResidualMeters,
                Is.LessThanOrEqualTo(0.000001f));

            for (int index = 1; index <= mechanism.Settings.DetentCount; index++)
            {
                Assert.That(mechanism.TrySetEndpointDetent(index, false), Is.True);
                Assert.That(mechanism.AtMaximumTravel, Is.True);
                Assert.That(mechanism.TopStackHeightResidualMeters,
                    Is.LessThanOrEqualTo(0.000001f));
                Assert.That(mechanism.OutOfPlaneSlideResidualMeters,
                    Is.LessThanOrEqualTo(0.000001f));
                Assert.That(mechanism.FixedAxisConstraintResidual,
                    Is.LessThanOrEqualTo(0.000001f));
                Assert.That(mechanism.RenderersRemainAttached, Is.True);
                Assert.That(mechanism.IsPoseLegal(), Is.True);
            }

            Assert.That(mechanism.TrySetTravel(0f), Is.True);
            Assert.That(mechanism.TopStackHeightResidualMeters,
                Is.LessThanOrEqualTo(0.000001f));
            Object.DestroyImmediate(instance);
        }

        [Test]
        public void HapticsOnlyConsumeSemanticMechanismEvents()
        {
            string mechanism = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/"
                + "MagneticSlideTileShippingMechanism.cs"));
            string coordinator = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/"
                + "MagneticSlideTileShippingCoordinator.cs"));
            string slider = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_EDC/Runtime/EdcSliderController.cs"));
            string appCoordinator = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "Scripts/Product/FidgetAppCoordinator.cs"));
            Assert.That(mechanism, Does.Contain("SemanticEventRaised"));
            Assert.That(mechanism, Does.Not.Contain("IosHaptics."));
            Assert.That(coordinator, Does.Not.Contain("FidgetHapticRouter"));
            Assert.That(coordinator, Does.Not.Contain("IosHaptics."));
            Assert.That(
                slider,
                Does.Contain(
                    "subscribedShippingMechanism.SemanticEventRaised +="));
            Assert.That(
                appCoordinator,
                Does.Contain("FidgetHapticRouter.EmitMagneticSlider"));
        }
    }
}
