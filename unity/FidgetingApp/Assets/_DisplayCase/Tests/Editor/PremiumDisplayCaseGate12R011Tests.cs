using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.DisplayCase.Tests
{
    public sealed class PremiumDisplayCaseGate12R011Tests
    {
        [Test]
        public void FactoryUsesTheUserApprovedR010Candidate()
        {
            Assert.That(
                PremiumDisplayCaseShippingFactory.ResourcesPath,
                Is.EqualTo(
                    PremiumDisplayCaseGate12R010ReviewBuilder.ResourcesPath));
            Assert.That(
                PremiumDisplayCaseShippingFactory.PresentationInstanceName,
                Is.EqualTo("PremiumDisplayCaseGate12R010"));
            Assert.That(
                Resources.Load<PremiumDisplayCaseShippingPresentation>(
                    PremiumDisplayCaseShippingFactory.ResourcesPath),
                Is.Not.Null);
            Assert.That(
                Resources.Load<PremiumDisplayCaseShippingPresentation>(
                    PremiumDisplayCaseShippingFactory
                        .NativeHybridResourcesPath),
                Is.Not.Null);
        }

        [Test]
        public void RuntimeLightingProfileMatchesTheGate09ShippingRig()
        {
            var profile = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCaseGachaLightingProfile>(
                PremiumDisplayCaseGate12R011IntegrationBuilder
                    .LightingProfilePath);
            Assert.That(profile, Is.Not.Null);
            Assert.That(profile.ReflectionCubemap, Is.Not.Null);
            Assert.That(profile.BeautyVolume, Is.Not.Null);
            Assert.That(profile.Lights.Length,
                Is.EqualTo(
                    PremiumDisplayCaseGachaLightingContract
                        .RealtimeLightCount));
            Assert.That(
                profile.Lights.Count(light =>
                    light.type == LightType.Directional),
                Is.EqualTo(2));
            Assert.That(
                profile.Lights.Count(light =>
                    light.type == LightType.Spot),
                Is.EqualTo(2));
            Assert.That(profile.Lights[0].name,
                Is.EqualTo("LGT_PDC_SOFT_KEY"));
            Assert.That(profile.Lights[0].intensity,
                Is.EqualTo(1.86804699f).Within(0.00001f));
        }

        [Test]
        public void LightingScopeRestoresTheAppRenderSettings()
        {
            AmbientMode ambientMode = RenderSettings.ambientMode;
            Color ambientLight = RenderSettings.ambientLight;
            float ambientIntensity = RenderSettings.ambientIntensity;
            DefaultReflectionMode reflectionMode =
                RenderSettings.defaultReflectionMode;
            Texture reflectionTexture =
                RenderSettings.customReflectionTexture;
            float reflectionIntensity =
                RenderSettings.reflectionIntensity;
            int reflectionBounces =
                RenderSettings.reflectionBounces;
            bool fog = RenderSettings.fog;
            GameObject host = new GameObject("LightingScopeTest");
            PremiumDisplayCaseGachaLightingScope scope = null;
            try
            {
                scope = PremiumDisplayCaseGachaLightingInstaller.Install(
                    host.transform);
                Assert.That(scope.IsWired, Is.True);
                Assert.That(scope.RealtimeLightCount, Is.EqualTo(4));
                Assert.That(RenderSettings.defaultReflectionMode,
                    Is.EqualTo(DefaultReflectionMode.Custom));
                Assert.That(RenderSettings.customReflectionTexture,
                    Is.EqualTo(scope.Profile.ReflectionCubemap));
                Assert.That(
                    scope.GetComponentsInChildren<Volume>(true).Length,
                    Is.EqualTo(1));
            }
            finally
            {
                scope?.Restore();
                Object.DestroyImmediate(host);
            }

            Assert.That(RenderSettings.ambientMode, Is.EqualTo(ambientMode));
            Assert.That(RenderSettings.ambientLight, Is.EqualTo(ambientLight));
            Assert.That(RenderSettings.ambientIntensity,
                Is.EqualTo(ambientIntensity));
            Assert.That(RenderSettings.defaultReflectionMode,
                Is.EqualTo(reflectionMode));
            Assert.That(RenderSettings.customReflectionTexture,
                Is.EqualTo(reflectionTexture));
            Assert.That(RenderSettings.reflectionIntensity,
                Is.EqualTo(reflectionIntensity));
            Assert.That(RenderSettings.reflectionBounces,
                Is.EqualTo(reflectionBounces));
            Assert.That(RenderSettings.fog, Is.EqualTo(fog));
        }

        [Test]
        public void CorrectedR012RuntimeCaptureUsesR010AndKeepsTheToyStopped()
        {
            string reportPath = Path.Combine(
                PremiumDisplayCaseGate12R012RuntimeCapture.EvidenceRoot,
                "runtime-capture-report.json");
            Assert.That(File.Exists(reportPath), Is.True);
            var report = JsonUtility.FromJson<
                PremiumDisplayCaseGate12R011IntegrationBuilder
                    .RuntimeCaptureReport>(File.ReadAllText(reportPath));
            Assert.That(report.status, Is.EqualTo("pass"));
            Assert.That(report.factoryResourcesPath,
                Is.EqualTo(
                    PremiumDisplayCaseGate12R010ReviewBuilder.ResourcesPath));
            Assert.That(report.activeCaseName,
                Is.EqualTo(
                    PremiumDisplayCaseShippingFactory
                        .PresentationInstanceName));
            Assert.That(report.lightingRealtimeCount, Is.EqualTo(4));
            Assert.That(report.mainDirectionalLights, Is.EqualTo(1));
            Assert.That(report.additionalRealtimeLights, Is.EqualTo(3));
            Assert.That(report.frameCount, Is.EqualTo(180));
            Assert.That(report.toyAngularVelocityZero, Is.True);
            Assert.That(report.physicalPhoneInstalled, Is.False);
        }

        [Test]
        public void IosBuildProvenanceNamesR010AndUniqueR011Simulator()
        {
            string source = File.ReadAllText(
                "Assets/Editor/IosBuildPipeline.cs");
            StringAssert.Contains(
                "PremiumDisplayCaseGate12R010/PresentationRoot.prefab",
                source);
            StringAssert.Contains(
                "PremiumDisplayCaseGate12R011Lighting.asset",
                source);
            StringAssert.Contains(
                "BuildPremiumDisplayCaseGate12R011SimulatorProject",
                source);
            StringAssert.Contains(
                "Builds/iOS/SimulatorJobs/",
                source);
        }
    }
}
