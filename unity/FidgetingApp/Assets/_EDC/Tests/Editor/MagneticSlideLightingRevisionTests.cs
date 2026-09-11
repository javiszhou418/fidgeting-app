using System.IO;
using System.Linq;
using FidgetingApp.EDC.Gate12R002;
using FidgetingApp.Product;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Tests
{
    public sealed class MagneticSlideLightingRevisionTests
    {
        private const string ScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";

        [Test]
        public void ShippingScene_DefaultsToBalancedLightingOnly()
        {
            Scene scene = EditorSceneManager.OpenScene(
                ScenePath, OpenSceneMode.Single);
            Camera camera = Camera.main;
            MagneticSlideShippingLightingController lighting =
                camera.GetComponent<MagneticSlideShippingLightingController>();
            MagneticSlideTileShippingCoordinator coordinator =
                Object.FindFirstObjectByType<
                    MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include);

            Assert.That(lighting, Is.Not.Null);
            Assert.That(
                lighting.Variant,
                Is.EqualTo(MagneticSlideLightingVariant.BalancedBrighter));
            Assert.That(camera.allowHDR, Is.True);
            Assert.That(coordinator.CandidateModelActive, Is.True);
            Assert.That(coordinator.FallbackModelActive, Is.False);
            coordinator.ResetShippingPose(false);
            Assert.That(coordinator.Mechanism.IsPoseLegal(), Is.True);
        }

        [Test]
        public void BalancedLighting_HasNeutralToneMapAndMeasuredLift()
        {
            MagneticSlideLightingValues baseline =
                MagneticSlideShippingLighting.Resolve(
                    MagneticSlideLightingVariant.Build42Baseline);
            MagneticSlideLightingValues balanced =
                MagneticSlideShippingLighting.Resolve(
                    MagneticSlideLightingVariant.BalancedBrighter);
            MagneticSlideLightingValues everyday =
                MagneticSlideShippingLighting.Resolve(
                    MagneticSlideLightingVariant.EverydayD65);

            Assert.That(baseline.Hdr, Is.False);
            Assert.That(baseline.PostProcessing, Is.False);
            Assert.That(balanced.Hdr, Is.True);
            // rev 5: exposure is the shared four-scene value; the 0.40 EV the
            // slide lost comes back on its model lights (x1.32), not the frame.
            Assert.That(
                balanced.PostExposureEv,
                Is.EqualTo(SpinnerSharedPresentationGrading.PostExposureEv));
            Assert.That(balanced.PostExposureEv, Is.EqualTo(0.15f));
            Assert.That(balanced.AmbientMultiplier, Is.EqualTo(1.25f));
            float restoredGain = Mathf.Pow(
                2f,
                MagneticSlideShippingLighting.Rev4PostExposureEv - balanced.PostExposureEv);
            Assert.That(balanced.KeyIntensity, Is.EqualTo(0.90f));
            Assert.That(balanced.FillIntensity, Is.EqualTo(0.71f));
            Assert.That(
                balanced.KeyIntensity,
                Is.EqualTo(MagneticSlideShippingLighting.Rev4KeyIntensity * restoredGain).Within(0.01f));
            Assert.That(
                balanced.FillIntensity,
                Is.EqualTo(MagneticSlideShippingLighting.Rev4FillIntensity * restoredGain).Within(0.01f));
            Assert.That(balanced.ReflectionIntensity, Is.EqualTo(0.70f));
            Assert.That(
                balanced.Tonemapping,
                Is.EqualTo(
                    UnityEngine.Rendering.Universal.TonemappingMode.Neutral));
            Assert.That(
                balanced.KeyColor,
                Is.EqualTo(new Color(0.96f, 0.98f, 1f, 1f)));
            Assert.That(
                balanced.FillColor,
                Is.EqualTo(new Color(0.90f, 0.95f, 1f, 1f)));
            Assert.That(everyday.PostExposureEv, Is.EqualTo(2.35f));
            Assert.That(everyday.AmbientMultiplier, Is.EqualTo(1.80f));
        }

        [Test]
        public void LightingRevision_DoesNotAddEmissionOrChangeMechanism()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            MagneticSlideTileShippingCoordinator coordinator =
                Object.FindFirstObjectByType<
                    MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include);
            Material[] materials = coordinator.CandidateModel
                .GetComponentsInChildren<Renderer>(true)
                .SelectMany(renderer => renderer.sharedMaterials)
                .Where(material => material != null)
                .Distinct()
                .ToArray();

            Assert.That(coordinator.Settings.DetentCount, Is.EqualTo(30));
            Assert.That(coordinator.Settings.DetentStepDegrees, Is.EqualTo(12f));
            Assert.That(
                coordinator.Mechanism.LinearVelocityMetersPerSecond,
                Is.EqualTo(0f));
            Assert.That(
                coordinator.Mechanism.AngularVelocityDegreesPerSecond,
                Is.EqualTo(0f));
            foreach (Material material in materials)
            {
                if (material.HasProperty("_EmissionColor"))
                {
                    Assert.That(
                        material.GetColor("_EmissionColor").maxColorComponent,
                        Is.EqualTo(0f),
                        material.name);
                }
            }
        }

        [Test]
        public void LightingReview_ProvesProtectedRuntimeHashesUnchanged()
        {
            string reportPath = Path.Combine(
                Directory.GetParent(Application.dataPath)!.FullName,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
                + "12-shipping/rev-004-lighting/lighting-review-report.json");
            string report = File.ReadAllText(reportPath);

            StringAssert.Contains(
                "\"protectedRuntimeUnchanged\": true", report);
            StringAssert.Contains("\"geometryChanged\": false", report);
            StringAssert.Contains("\"materialsChanged\": false", report);
            StringAssert.Contains("\"interactionChanged\": false", report);
            StringAssert.Contains("\"audioChanged\": false", report);
            StringAssert.Contains("\"hapticsChanged\": false", report);
            StringAssert.Contains("\"buildInstallPhone\": false", report);
        }
    }
}
