using System;
using System.Collections.Generic;
using System.Linq;
using FidgetingApp.Product;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Tests.Editor
{
    public sealed class PremiumDisplayCaseDynamicRuntimeTests
    {
        private const string PrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCase.prefab";

        private static IEnumerable<TestCaseData> ShippingProducts()
        {
            foreach (ProductCatalogEntry entry in ProductCatalog.ShippingEntries)
            {
                yield return new TestCaseData(entry.ModelId, entry.ScenePath)
                    .SetName($"DynamicSession_{entry.ModelId}");
            }
        }

        [TestCaseSource(nameof(ShippingProducts))]
        public void ShippingRuntimePath_CompletesReplayOrbitExplodeAndRestore(
            string modelId,
            string scenePath)
        {
            Scene scene = EditorSceneManager.OpenScene(
                scenePath,
                OpenSceneMode.Single);
            PremiumDisplayCaseProductProfile profile =
                PremiumDisplayCaseProductProfiles.Resolve(modelId);
            Transform source = scene.GetRootGameObjects()
                .Select(root => root.transform)
                .Single(root => root.name == profile.SceneRootName);
            GameObject canonical = PremiumDisplayCaseProductSnapshot.Capture(
                modelId,
                source);
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null);
            PremiumDisplayCase displayCase = UnityEngine.Object.Instantiate(prefab);
            PremiumDisplayCaseInteractionController interaction = displayCase
                .GetComponent<PremiumDisplayCaseInteractionController>();
            Assert.That(interaction, Is.Not.Null);

            try
            {
                displayCase.setCapsuleDimensions(profile.CapsuleDimensions);
                displayCase.SetProductPresentationOffset(profile.PresentationOffset);
                displayCase.setContent(canonical.transform, profile.ContentOptions);
                Assert.That(displayCase.ContentFitScale.x,
                    Is.GreaterThan(0f), modelId);
                Assert.That(float.IsFinite(displayCase.ContentFitScale.x),
                    Is.True, modelId);
                if (modelId == ProductCatalog.MetalThreeBladeModelId)
                {
                    Assert.That(displayCase.ContentFitScale.x,
                        Is.EqualTo(1.494417f).Within(0.003f),
                        "Metal must use one uniform fit inside the shared Collector Slab capsule.");
                }
                if (modelId == ProductCatalog.GoldFourWingModelId)
                {
                    Assert.That(displayCase.ContentFitScale.x,
                        Is.EqualTo(0.895743f).Within(0.003f),
                        "Mirror Quad must preserve the verified full four-wing fit in the shared case.");
                }
                if (modelId == ProductCatalog.MagneticFanCardModelId)
                {
                    Assert.That(displayCase.ContentFitScale.x,
                        Is.EqualTo(0.957329f).Within(0.003f),
                        "The readable Q/K/A fan must fit uniformly inside the same Collector Slab capsule without a portrait exception.");
                }

                interaction.SetExplodedProgress(1f);
                displayCase.play();
                interaction.PlayAssembly();
                Advance(displayCase, interaction, 2.4f);
                Assert.That(displayCase.RevealProgress,
                    Is.EqualTo(1f).Within(0.0001f), modelId);
                Assert.That(interaction.ExplodedProgress,
                    Is.EqualTo(0f).Within(0.0001f), modelId);
                Assert.That(Quaternion.Angle(
                        Quaternion.identity,
                        displayCase.ContentOrbitRotation),
                    Is.LessThan(0.001f),
                    $"{modelId} must finish its entrance on the readable front.");

                Transform[] layers = DisplayLayers(displayCase);
                Vector3[] assembled = layers.Select(layer => layer.localPosition)
                    .ToArray();

                interaction.SetOrbitDegrees(24f, 0f);
                Assert.That(interaction.OrbitDegrees.x,
                    Is.EqualTo(24f).Within(0.0001f), modelId);
                interaction.SetOrbitDegrees(0f, -16f);
                Assert.That(interaction.OrbitDegrees.y,
                    Is.EqualTo(-16f).Within(0.0001f), modelId);
                interaction.ResetInteraction();

                interaction.PlayExplode();
                Advance(displayCase, interaction, 1.5f);
                Assert.That(interaction.ExplodedProgress,
                    Is.EqualTo(1f).Within(0.0001f), modelId);
                Assert.That(layers.Where((layer, index) =>
                        Vector3.Distance(layer.localPosition, assembled[index])
                            > 0.001f).Count(),
                    Is.GreaterThanOrEqualTo(6), modelId);

                displayCase.play();
                interaction.PlayAssembly();
                Advance(displayCase, interaction, 2.4f);
                Assert.That(interaction.ExplodedProgress,
                    Is.EqualTo(0f).Within(0.0001f), modelId);
                for (int index = 0; index < layers.Length; index++)
                {
                    Assert.That(Vector3.Distance(
                            layers[index].localPosition,
                            assembled[index]),
                        Is.LessThan(0.00001f),
                        $"{modelId} layer {layers[index].name} did not restore.");
                }

                displayCase.AdvanceAnimation(
                    PremiumDisplayCase.FrontReadableHoldSeconds + 0.01f);
                Quaternion beforeTurn = displayCase.ContentOrbitRotation;
                displayCase.AdvanceAnimation(
                    profile.ContentOptions.IdleRotationPeriodSeconds * 0.5f);
                float turnAngle = Quaternion.Angle(
                    beforeTurn,
                    displayCase.ContentOrbitRotation);
                if (profile.ContentOptions.IdleRotationEnabled)
                {
                    Assert.That(turnAngle, Is.GreaterThan(175f), modelId);
                }
                else
                {
                    Assert.That(turnAngle, Is.LessThan(0.001f),
                        $"{modelId} must hold the readable front instead of exposing its mechanical rear.");
                    Assert.That(modelId,
                        Is.EqualTo(ProductCatalog.MagneticFanCardModelId),
                        "Only the intentionally one-sided fan-card prize may suppress the shared idle turn.");
                    displayCase.AdvanceAnimation(
                        profile.ContentOptions.IdleRotationPeriodSeconds * 2f);
                    Assert.That(Quaternion.Angle(
                            Quaternion.identity,
                            displayCase.ContentOrbitRotation),
                        Is.LessThan(0.001f),
                        "The settled A/Q/K front must remain stable beyond two complete baseline idle periods.");
                }

                displayCase.setContent((Transform)null);
                Assert.That(canonical.transform.parent, Is.Null, modelId);
                Assert.That(canonical.activeSelf, Is.False, modelId);
            }
            finally
            {
                if (displayCase != null)
                {
                    UnityEngine.Object.DestroyImmediate(displayCase.gameObject);
                }
                if (canonical != null)
                {
                    UnityEngine.Object.DestroyImmediate(canonical);
                }
            }
        }

        [Test]
        public void CanonicalSnapshot_PreservesRestPoseWhileAppearanceRefreshes()
        {
            var source = new GameObject("ShippingRoot");
            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
            visual.transform.SetParent(source.transform, false);
            visual.transform.localPosition = new Vector3(0.01f, 0.02f, 0.03f);
            Material initial = visual.GetComponent<Renderer>().sharedMaterial;
            GameObject snapshot = PremiumDisplayCaseProductSnapshot.Capture(
                ProductCatalog.PointedThreeBladeModelId,
                source.transform);
            Transform cachedVisual = snapshot.transform.GetChild(0);
            Vector3 cachedPosition = cachedVisual.localPosition;

            try
            {
                visual.transform.localPosition = new Vector3(8f, 9f, 10f);
                var replacement = new Material(initial)
                {
                    name = "ReplacementAppearance"
                };
                visual.GetComponent<Renderer>().sharedMaterial = replacement;

                Assert.That(PremiumDisplayCaseProductSnapshot.RefreshAppearance(
                    snapshot,
                    source.transform), Is.True);
                Assert.That(cachedVisual.localPosition,
                    Is.EqualTo(cachedPosition));
                Assert.That(cachedVisual.GetComponent<Renderer>().sharedMaterial,
                    Is.EqualTo(replacement));
                UnityEngine.Object.DestroyImmediate(replacement);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(snapshot);
                UnityEngine.Object.DestroyImmediate(source);
            }
        }

        [Test]
        public void Coordinator_CachesAfterAppearanceAndNeverCapturesLiveOnPresent()
        {
            string source = System.IO.File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            int visuals = source.IndexOf("ConfigureExperienceVisuals();",
                StringComparison.Ordinal);
            int cache = source.IndexOf("CacheDisplayCaseCanonicalPrize(",
                visuals,
                StringComparison.Ordinal);
            int libraryPose = source.IndexOf("ApplyLibraryPreviewPose();",
                cache,
                StringComparison.Ordinal);
            Assert.That(visuals, Is.GreaterThanOrEqualTo(0));
            Assert.That(cache, Is.GreaterThan(visuals));
            Assert.That(libraryPose, Is.GreaterThan(cache));
            StringAssert.Contains(
                "InstantiateDisplayCaseCanonicalPrize(modelId)",
                source);
            StringAssert.Contains(
                "Refusing to snapshot live physical state",
                source);
            StringAssert.DoesNotContain(
                "activeDisplayCasePrize = PremiumDisplayCaseProductSnapshot.Capture",
                source);
        }

        private static void Advance(
            PremiumDisplayCase displayCase,
            PremiumDisplayCaseInteractionController interaction,
            float seconds)
        {
            const float step = 1f / 60f;
            int count = Mathf.CeilToInt(seconds / step);
            for (int index = 0; index < count; index++)
            {
                displayCase.AdvanceAnimation(step);
                interaction.AdvanceAnimation(step);
            }
        }

        private static Transform[] DisplayLayers(PremiumDisplayCase displayCase)
        {
            string[] names =
            {
                "Layer_01_FrontPlate",
                "Layer_02_Fasteners",
                "Layer_03_SpacerFrame",
                "Layer_04_Capsule",
                "Layer_05_VelvetInsert",
                "Layer_06_RearPlate",
                "Layer_07_OuterTray",
                "Layer_08_BoxLid"
            };
            Transform[] transforms = displayCase.GetComponentsInChildren<Transform>(
                true);
            return names.Select(name => transforms.Single(item => item.name == name))
                .ToArray();
        }
    }
}
