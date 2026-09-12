using System;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.Editor;
using FidgetingApp.Product;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Tests
{
    public sealed class PremiumDisplayCaseGate12R010Tests
    {
        [Test]
        public void V3ProfilesCoverTheShippingCatalogWithoutLegacyPitch()
        {
            foreach (string modelId in ProductCatalog.ShippingModelIds())
            {
                PremiumDisplayCasePocketContentProfile profile =
                    PremiumDisplayCaseV3PocketProfiles.Resolve(modelId);
                Assert.That(profile.ModelId, Is.EqualTo(modelId));
                Assert.That(profile.InitialEulerAngles.x, Is.EqualTo(0f));
                Assert.That(profile.FitDiameterMeters,
                    Is.EqualTo(PremiumDisplayCaseV3PocketProfiles.FitDiameterMeters));
                Assert.That(profile.ReferenceDepthMeters,
                    Is.EqualTo(PremiumDisplayCaseV3PocketProfiles.FitDepthMeters));
            }
        }

        [Test]
        public void R010WiresRarityCmfAndIsTheApprovedFactoryResource()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R010ReviewBuilder.PrefabPath);
            Assert.That(prefab, Is.Not.Null);
            var cmf = prefab.GetComponent<PremiumDisplayCaseV3RarityCmf>();
            Assert.That(cmf, Is.Not.Null);
            Assert.That(cmf.IsWired, Is.True);
            Assert.That(PremiumDisplayCaseShippingFactory.ResourcesPath,
                Is.EqualTo(PremiumDisplayCaseGate12R010ReviewBuilder.ResourcesPath));
        }

        [Test]
        public void RarityCmfUsesTheLockedMutedPalette()
        {
            AssertColor(
                PremiumDisplayCaseV3RarityCmf.AccentSrgb(
                    PremiumDisplayCaseFoilTier.Steel),
                0.62f, 0.65f, 0.69f);
            AssertColor(
                PremiumDisplayCaseV3RarityCmf.AccentSrgb(
                    PremiumDisplayCaseFoilTier.Copper),
                0.70f, 0.58f, 0.52f);
            AssertColor(
                PremiumDisplayCaseV3RarityCmf.AccentSrgb(
                    PremiumDisplayCaseFoilTier.Silver),
                0.58f, 0.63f, 0.70f);
            AssertColor(
                PremiumDisplayCaseV3RarityCmf.AccentSrgb(
                    PremiumDisplayCaseFoilTier.Gold),
                0.80f, 0.73f, 0.60f);
        }

        [Test]
        public void DynamicLabelAppliesTheRarityCmf()
        {
            GameObject instance = null;
            try
            {
                instance = (GameObject)PrefabUtility.InstantiatePrefab(
                    AssetDatabase.LoadAssetAtPath<GameObject>(
                        PremiumDisplayCaseGate12R010ReviewBuilder.PrefabPath));
                var presentation =
                    instance.GetComponent<PremiumDisplayCaseShippingPresentation>();
                presentation.SetLabel(new PremiumDisplayCaseLabelData(
                    "GRAPHITE DUO",
                    "GRAPHITE · SATIN",
                    "2026-09-11",
                    "REFINED",
                    "R010-TEST"));
                Assert.That(
                    instance.GetComponent<PremiumDisplayCaseV3RarityCmf>().Tier,
                    Is.EqualTo(PremiumDisplayCaseFoilTier.Copper));
                TextMesh title = instance
                    .GetComponentsInChildren<TextMesh>(true)
                    .Single(text => text.name == "LABEL_PRODUCT_NAME");
                Assert.That(title.text, Is.EqualTo("GRAPHITE DUO"));
            }
            finally
            {
                if (instance != null)
                {
                    UnityEngine.Object.DestroyImmediate(instance);
                }
            }
        }

        [Test]
        public void CircularFitCentersAnAsymmetricMesh()
        {
            GameObject instance = null;
            GameObject content = null;
            try
            {
                instance = (GameObject)PrefabUtility.InstantiatePrefab(
                    AssetDatabase.LoadAssetAtPath<GameObject>(
                        PremiumDisplayCaseGate12R010ReviewBuilder.PrefabPath));
                var presentation =
                    instance.GetComponent<PremiumDisplayCaseShippingPresentation>();
                content = new GameObject("AsymmetricContent");
                GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
                visual.transform.SetParent(content.transform, false);
                visual.transform.localPosition = new Vector3(0.2f, -0.1f, 0.03f);
                visual.transform.localScale = new Vector3(0.08f, 0.04f, 0.01f);
                PremiumDisplayCasePocketFitResult fit =
                    presentation.AttachContentToCircularPocket(
                        content.transform,
                        PremiumDisplayCaseV3PocketProfiles.Resolve(
                            ProductCatalog.GraphiteTwoLobeModelId));
                Assert.That(Mathf.Abs(fit.CenterOffsetSlotLocal.x),
                    Is.LessThan(0.00005f));
                Assert.That(Mathf.Abs(fit.CenterOffsetSlotLocal.y),
                    Is.LessThan(0.00005f));
                Assert.That(fit.RadialExtentMeters,
                    Is.LessThanOrEqualTo(
                        PremiumDisplayCaseV3PocketProfiles.FitDiameterMeters
                        * 0.5f
                        + 0.00005f));
            }
            finally
            {
                if (content != null)
                {
                    UnityEngine.Object.DestroyImmediate(content);
                }
                if (instance != null)
                {
                    UnityEngine.Object.DestroyImmediate(instance);
                }
            }
        }

        [Test]
        public void ReportPassesCenterScaleAndCompleteFrameGate()
        {
            string reportPath = Path.Combine(
                PremiumDisplayCaseGate12R010ReviewBuilder.EvidenceRoot,
                PremiumDisplayCaseGate12R010ReviewBuilder.ReportFile);
            var report =
                JsonUtility.FromJson<PremiumDisplayCaseGate12R010ReviewBuilder.ReviewReport>(
                    File.ReadAllText(reportPath));
            Assert.That(report.status, Is.EqualTo("pass"));
            Assert.That(report.failures, Is.Empty);
            Assert.That(report.products.Count, Is.EqualTo(4));
            foreach (PremiumDisplayCaseGate12R010ReviewBuilder.ProductReview product
                     in report.products)
            {
                Assert.That(product.error, Is.Empty, product.modelId);
                Assert.That(product.rendererCount, Is.GreaterThan(0), product.modelId);
                Assert.That(Mathf.Abs(product.centerOffsetMm[0]),
                    Is.LessThanOrEqualTo(0.05f), product.modelId);
                Assert.That(Mathf.Abs(product.centerOffsetMm[1]),
                    Is.LessThanOrEqualTo(0.05f), product.modelId);
                Assert.That(product.screenCenterErrorPixels,
                    Is.LessThanOrEqualTo(1f), product.modelId);
                Assert.That(product.occupancy,
                    Is.InRange(0.75f, 1.002f), product.modelId);
                Assert.That(File.Exists(Path.Combine(
                    PremiumDisplayCaseGate12R010ReviewBuilder.EvidenceRoot,
                    product.pocketFrontFile)), Is.True, product.modelId);
                Assert.That(File.Exists(Path.Combine(
                    PremiumDisplayCaseGate12R010ReviewBuilder.EvidenceRoot,
                    product.phoneFrontFile)), Is.True, product.modelId);
                Assert.That(File.Exists(Path.Combine(
                    PremiumDisplayCaseGate12R010ReviewBuilder.EvidenceRoot,
                    product.phoneQuarterFile)), Is.True, product.modelId);
            }
        }

        private static void AssertColor(
            Color actual,
            float red,
            float green,
            float blue)
        {
            Assert.That(actual.r, Is.EqualTo(red).Within(0.0001f));
            Assert.That(actual.g, Is.EqualTo(green).Within(0.0001f));
            Assert.That(actual.b, Is.EqualTo(blue).Within(0.0001f));
        }
    }
}
