using System;
using System.IO;
using System.Linq;
using System.Reflection;
using CodexUnityLab;
using FidgetingApp.EDC;
using FidgetingApp.FanCard;
using FidgetingApp.Product;
using NUnit.Framework;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Tests.Editor
{
    public sealed class PremiumDisplayCaseTests
    {
        private const string PrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCase.prefab";
        private const string ThreeBladePrizePrefabPath =
            "Assets/Resources/Gacha/ThreeBladeDisplayPrize.prefab";

        [Test]
        public void ContentFit_UsesEightPercentPaddingAndCentersAllAxes()
        {
            Bounds bounds = new Bounds(
                new Vector3(1f, 2f, -0.5f),
                new Vector3(2f, 4f, 1f));
            PremiumDisplayCaseCapsuleDimensions capsule =
                PremiumDisplayCaseCapsulePresets.Resolve(
                    PremiumDisplayCaseCapsulePreset.CircularStandard);

            PremiumDisplayCaseFitResult result = PremiumDisplayCaseLayout.Fit(
                bounds,
                capsule);

            float expectedScale = capsule.Diameter * 0.92f / 4f;
            Assert.That(result.UniformScale, Is.EqualTo(expectedScale).Within(0.000001f));
            Assert.That(Vector3.SqrMagnitude(
                result.CenterOffset - (-bounds.center * expectedScale)),
                Is.LessThan(0.00000001f));
        }

        [Test]
        public void CapsulePresets_AreNeutralAndExposeDifferentDepths()
        {
            PremiumDisplayCaseCapsuleDimensions circular =
                PremiumDisplayCaseCapsulePresets.Resolve(
                    PremiumDisplayCaseCapsulePreset.CircularStandard);
            PremiumDisplayCaseCapsuleDimensions circularDeep =
                PremiumDisplayCaseCapsulePresets.Resolve(
                    PremiumDisplayCaseCapsulePreset.CircularDeep);
            PremiumDisplayCaseCapsuleDimensions rounded =
                PremiumDisplayCaseCapsulePresets.Resolve(
                    PremiumDisplayCaseCapsulePreset.RoundedSquareStandard);

            Assert.That(circular.Shape,
                Is.EqualTo(PremiumDisplayCaseCapsuleShape.Circular));
            Assert.That(rounded.Shape,
                Is.EqualTo(PremiumDisplayCaseCapsuleShape.RoundedSquare));
            Assert.That(circularDeep.Depth, Is.GreaterThan(circular.Depth));
            Assert.That(circular.Diameter, Is.EqualTo(0.084f).Within(0.0001f));
        }

        [Test]
        public void DefaultContentOptions_MatchMagneticSlidePresentation()
        {
            PremiumDisplayCaseContentOptions options =
                PremiumDisplayCaseContentOptions.Default;

            Assert.That(options.IdleRotationEnabled, Is.True);
            Assert.That(options.IdleRotationPeriodSeconds,
                Is.EqualTo(6f).Within(0.0001f));
            Assert.That(options.InitialEulerAngles,
                Is.EqualTo(new Vector3(90f, -8f, 0f)));
        }

        [Test]
        public void LightingCatalog_OffersFourDistinctPersistentStudioPalettes()
        {
            PremiumDisplayCaseLightingPreset[] presets =
                PremiumDisplayCaseLightingCatalog.Presets.ToArray();

            Assert.That(presets.Length, Is.EqualTo(4));
            Assert.That(presets.Select(preset => preset.Id).Distinct().Count(),
                Is.EqualTo(4));
            Assert.That(presets.Select(preset => preset.DisplayName),
                Has.All.Not.Empty);
            Assert.That(PremiumDisplayCaseLightingCatalog.PreferenceKey,
                Is.EqualTo("FidgetingApp.DisplayCaseLightingPreset"));
            Assert.That(PremiumDisplayCaseLightingCatalog.Resolve("missing").Id,
                Is.EqualTo(PremiumDisplayCaseLightingCatalog.DefaultId));
            Assert.That(presets.Select(preset => preset.Key),
                Is.Unique);
        }

        [Test]
        public void LightingPreset_SwitchesImmediatelyWithoutIntensityDrift()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            PremiumDisplayCase instance = UnityEngine.Object.Instantiate(prefab);
            try
            {
                instance.SetRevealProgressForPreview(1f);
                instance.SetLightingPreset("soft-neutral");
                Light key = instance.GetComponentsInChildren<Light>(true)
                    .Single(light => light.name == "CaseLight_Key");
                Color neutralColor = key.color;
                float neutralIntensity = key.intensity;

                instance.SetLightingPreset("rose-studio");
                Assert.That(instance.CurrentLightingPresetId,
                    Is.EqualTo("rose-studio"));
                Assert.That(Vector4.Distance(key.color, neutralColor),
                    Is.GreaterThan(0.05f));

                instance.SetLightingPreset("soft-neutral");
                Assert.That(key.color, Is.EqualTo(neutralColor));
                Assert.That(key.intensity,
                    Is.EqualTo(neutralIntensity).Within(0.000001f));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance.gameObject);
            }
        }

        [Test]
        public void ProductProfiles_ReuseMagneticSlidePackagingForAllSixModels()
        {
            PremiumDisplayCaseProductProfile[] profiles =
                PremiumDisplayCaseProductProfiles.Profiles.ToArray();
            Type[] profileConstructorParameters = typeof(
                    PremiumDisplayCaseProductProfile)
                .GetConstructors()
                .Single()
                .GetParameters()
                .Select(parameter => parameter.ParameterType)
                .ToArray();

            Assert.That(profiles.Length, Is.EqualTo(6));
            Assert.That(profileConstructorParameters, Is.EqualTo(new[]
            {
                typeof(string),
                typeof(string),
                typeof(string),
                typeof(PremiumDisplayCasePrizeNormalization)
            }),
                "A product profile may only identify its prize and normalize "
                + "its authored front; the shared case contract and the "
                + "one-sided readability policy are resolved centrally.");
            Assert.That(profiles.Select(profile => profile.ModelId),
                Is.EquivalentTo(ProductCatalog.ShippingModelIds()));
            Assert.That(profiles.Select(profile => profile.ModelId).Distinct().Count(),
                Is.EqualTo(6));
            Assert.That(profiles.Select(profile => profile.EnglishDisplayName),
                Has.All.Not.Empty);
            Assert.That(profiles.Select(profile => profile.EnglishDisplayName)
                    .Distinct().Count(),
                Is.EqualTo(6));
            Assert.That(profiles.All(profile =>
                    profile.EnglishDisplayName
                        == profile.EnglishDisplayName.ToUpperInvariant()),
                Is.True);

            PremiumDisplayCaseProductProfile magneticBaseline =
                PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MagneticSlideTileModelId);
            Assert.That(magneticBaseline.CapsulePreset,
                Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabLarge));
            Assert.That(magneticBaseline.ContentOptions.InitialEulerAngles,
                Is.EqualTo(new Vector3(90f, -8f, 0f)));
            Assert.That(magneticBaseline.ContentOptions.IdleRotationPeriodSeconds,
                Is.EqualTo(6f).Within(0.0001f));
            Assert.That(magneticBaseline.SceneRootName,
                Is.EqualTo("EDC_Root"));
            Assert.That(magneticBaseline.EnglishDisplayName,
                Is.EqualTo("MAGNETIC SLIDE"));
            Assert.That(magneticBaseline.PresentationOffset,
                Is.EqualTo(Vector3.zero));
            Assert.That(magneticBaseline.ContentOptions.IdleRotationEnabled,
                Is.True);

            Assert.That(profiles.Select(profile => profile.SceneRootName),
                Has.All.Not.Empty);
            foreach (PremiumDisplayCaseProductProfile profile in profiles)
            {
                AssertSharedPresentation(profile, magneticBaseline);
            }

            AssertPrizeNormalization(ProductCatalog.PointedThreeBladeModelId,
                "ThreeBladeEDC_Root", new Vector3(90f, -18f, 0f));
            AssertPrizeNormalization(ProductCatalog.MetalThreeBladeModelId,
                "ThreeBladeEDC_Root", new Vector3(-90f, -8f, 0f));
            AssertPrizeNormalization(ProductCatalog.GoldFourWingModelId,
                "ImportedSpinner_Root", new Vector3(90f, -12f, 0f));
            AssertPrizeNormalization(ProductCatalog.GraphiteTwoLobeModelId,
                "TwoLobeBar_Root", new Vector3(90f, -10f, 0f));
            AssertPrizeNormalization(ProductCatalog.MagneticSlideTileModelId,
                "EDC_Root", new Vector3(90f, -8f, 0f));
            AssertPrizeNormalization(ProductCatalog.MagneticFanCardModelId,
                "MagneticFanCard_Root", new Vector3(-90f, 0f, 0f));
        }

        [Test]
        public void AllProfiles_ExposeOnlyTheSharedCasePresentationContract()
        {
            PremiumDisplayCaseProductProfile baseline =
                PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MagneticSlideTileModelId);

            foreach (PremiumDisplayCaseProductProfile profile in
                     PremiumDisplayCaseProductProfiles.Profiles)
            {
                AssertSharedPresentation(profile, baseline);
            }
            Assert.That(PremiumDisplayCaseRevealMotion.DurationSeconds,
                Is.EqualTo(2.20f).Within(0.0001f));
            Assert.That(PremiumDisplayCaseExplodedLayout.AssemblyDurationSeconds,
                Is.EqualTo(1.35f).Within(0.0001f));
        }

        private static void AssertSharedPresentation(
            PremiumDisplayCaseProductProfile profile,
            PremiumDisplayCaseProductProfile baseline)
        {
            Assert.That(profile.CapsulePreset,
                Is.EqualTo(baseline.CapsulePreset), profile.ModelId);
            Assert.That(profile.CapsuleDimensions.Shape,
                Is.EqualTo(baseline.CapsuleDimensions.Shape), profile.ModelId);
            Assert.That(profile.CapsuleDimensions.Width,
                Is.EqualTo(baseline.CapsuleDimensions.Width).Within(0.000001f),
                profile.ModelId);
            Assert.That(profile.CapsuleDimensions.Height,
                Is.EqualTo(baseline.CapsuleDimensions.Height).Within(0.000001f),
                profile.ModelId);
            Assert.That(profile.CapsuleDimensions.Depth,
                Is.EqualTo(baseline.CapsuleDimensions.Depth).Within(0.000001f),
                profile.ModelId);
            Assert.That(profile.CapsuleDimensions.CornerRadius,
                Is.EqualTo(baseline.CapsuleDimensions.CornerRadius)
                    .Within(0.000001f), profile.ModelId);
            Assert.That(profile.PresentationOffset,
                Is.EqualTo(baseline.PresentationOffset), profile.ModelId);
            Assert.That(profile.ContentOptions.InitialEulerAngles,
                Is.EqualTo(baseline.ContentOptions.InitialEulerAngles),
                profile.ModelId);
            bool requiresReadableFront = string.Equals(
                profile.ModelId,
                ProductCatalog.MagneticFanCardModelId,
                StringComparison.Ordinal);
            Assert.That(profile.ContentOptions.IdleRotationEnabled,
                Is.EqualTo(!requiresReadableFront),
                requiresReadableFront
                    ? "The one-sided fan-card snapshot must not settle on its intentionally blank back."
                    : profile.ModelId);
            Assert.That(profile.ContentOptions.IdleRotationPeriodSeconds,
                Is.EqualTo(baseline.ContentOptions.IdleRotationPeriodSeconds)
                    .Within(0.0001f), profile.ModelId);
        }

        private static void AssertPrizeNormalization(
            string modelId,
            string sceneRootName,
            Vector3 expectedCanonicalFront)
        {
            PremiumDisplayCaseProductProfile profile =
                PremiumDisplayCaseProductProfiles.Resolve(modelId);
            Assert.That(profile.SceneRootName, Is.EqualTo(sceneRootName), modelId);
            Quaternion composed = Quaternion.Euler(
                    PremiumDisplayCaseProductProfiles.SharedContentOptions
                        .InitialEulerAngles)
                * profile.PrizeNormalization.SnapshotLocalRotation;
            Assert.That(Quaternion.Angle(
                    composed,
                    Quaternion.Euler(expectedCanonicalFront)),
                Is.LessThan(0.001f), modelId);
        }

        [Test]
        public void FanPrize_UsesTheSharedSlideCapsuleWithUniformScale()
        {
            PremiumDisplayCaseCapsuleDimensions capsule =
                PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MagneticFanCardModelId).CapsuleDimensions;
            PremiumDisplayCaseCapsuleDimensions baseline =
                PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MagneticSlideTileModelId).CapsuleDimensions;
            Bounds expandedFan = new Bounds(
                Vector3.zero,
                new Vector3(0.109327f, 0.144984f, 0.0095f));

            PremiumDisplayCaseFitResult fit = PremiumDisplayCaseLayout.Fit(
                expandedFan,
                capsule);

            Assert.That(capsule.Shape, Is.EqualTo(baseline.Shape));
            Assert.That(capsule.InnerSize, Is.EqualTo(baseline.InnerSize));
            Assert.That(fit.UniformScale, Is.GreaterThan(0.955f));
            Assert.That(fit.UniformScale, Is.LessThan(0.957f));
            Assert.That(fit.CenterOffset,
                Is.EqualTo(-expandedFan.center * fit.UniformScale));
        }

        [Test]
        public void FanSnapshot_UsesTheReadableNinetyDegreeCollectorFanWithoutMutatingLiveLayers()
        {
            var root = new GameObject("MagneticFanCard_Root");
            GameObject middle = new GameObject("MiddleCard");
            GameObject top = new GameObject("TopCard");
            middle.transform.SetParent(root.transform, false);
            top.transform.SetParent(root.transform, false);
            GameObject middleVisual = GameObject.CreatePrimitive(PrimitiveType.Cube);
            GameObject topVisual = GameObject.CreatePrimitive(PrimitiveType.Cube);
            middleVisual.name = "MiddleReadableFace";
            topVisual.name = "TopReadableFace";
            middleVisual.transform.SetParent(middle.transform, false);
            topVisual.transform.SetParent(top.transform, false);
            middleVisual.transform.localPosition = Vector3.right * 0.01f;
            topVisual.transform.localPosition = Vector3.right * 0.01f;

            GameObject snapshot = null;
            try
            {
                snapshot = PremiumDisplayCaseProductSnapshot.Capture(
                    ProductCatalog.MagneticFanCardModelId,
                    root.transform);
                Transform capturedMiddle = snapshot.transform.Cast<Transform>()
                    .Single(item => item.name.Contains("MiddleReadableFace"));
                Transform capturedTop = snapshot.transform.Cast<Transform>()
                    .Single(item => item.name.Contains("TopReadableFace"));
                Quaternion sharedCaseRotation = Quaternion.Euler(
                    PremiumDisplayCaseProductProfiles.SharedContentOptions
                        .InitialEulerAngles);
                Quaternion canonicalFanFront = Quaternion.Euler(
                    PremiumDisplayCaseProductProfiles.Resolve(
                            ProductCatalog.MagneticFanCardModelId)
                        .PrizeNormalization.CanonicalFrontEulerAngles);

                Assert.That(Quaternion.Angle(
                        sharedCaseRotation * capturedMiddle.localRotation,
                        canonicalFanFront * Quaternion.Euler(0f, 45f, 0f)),
                    Is.LessThan(0.01f));
                Assert.That(Quaternion.Angle(
                        sharedCaseRotation * capturedTop.localRotation,
                        canonicalFanFront * Quaternion.Euler(0f, 90f, 0f)),
                    Is.LessThan(0.01f));
                Assert.That(snapshot.GetComponents<MonoBehaviour>()
                        .Select(component => component.GetType().Name),
                    Does.Not.Contain("PremiumDisplayCaseFanSnapshotReveal"));
                Assert.That(middle.transform.localRotation,
                    Is.EqualTo(Quaternion.identity));
                Assert.That(top.transform.localRotation,
                    Is.EqualTo(Quaternion.identity));
            }
            finally
            {
                if (snapshot != null)
                {
                    UnityEngine.Object.DestroyImmediate(snapshot);
                }
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        [Test]
        public void FanSnapshot_DoesNotAddAProductSpecificRevealTimeline()
        {
            Assert.That(typeof(PremiumDisplayCaseProductSnapshot).Assembly.GetType(
                    "FidgetingApp.DisplayCase.PremiumDisplayCaseFanSnapshotReveal"),
                Is.Null);
            Assert.That(PremiumDisplayCaseRevealMotion.DurationSeconds,
                Is.EqualTo(2.20f).Within(0.0001f));
            Assert.That(PremiumDisplayCaseExplodedLayout.AssemblyDurationSeconds,
                Is.EqualTo(1.35f).Within(0.0001f));
        }

        [Test]
        public void FanPrize_ComposesTheSharedInitialPoseAndHoldsItsReadableFrontAfterSettling()
        {
            PremiumDisplayCaseProductProfile fan =
                PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MagneticFanCardModelId);
            PremiumDisplayCaseProductProfile slide =
                PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MagneticSlideTileModelId);

            Quaternion composedFront = Quaternion.Euler(
                    fan.ContentOptions.InitialEulerAngles)
                * fan.PrizeNormalization.SnapshotLocalRotation;

            Assert.That(Quaternion.Angle(
                    composedFront,
                    Quaternion.Euler(-90f, 0f, 0f)),
                Is.LessThan(0.001f),
                "The shared case Euler and fan snapshot normalization must compose to the approved A/Q/K front.");
            Assert.That(fan.ContentOptions.InitialEulerAngles,
                Is.EqualTo(slide.ContentOptions.InitialEulerAngles));
            Assert.That(fan.ContentOptions.IdleRotationPeriodSeconds,
                Is.EqualTo(slide.ContentOptions.IdleRotationPeriodSeconds)
                    .Within(0.0001f));
            Assert.That(fan.ContentOptions.IdleRotationEnabled, Is.False,
                "Settled fan-card content must remain on its readable front.");
            Assert.That(slide.ContentOptions.IdleRotationEnabled, Is.True,
                "The magnetic-slide baseline keeps its approved idle turn.");
        }

        [Test]
        public void CollectorIdentification_IsLeftAlignedOnTheLabelAndUsesCurrentClampedLevel()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            PremiumDisplayCase instance = UnityEngine.Object.Instantiate(prefab);
            try
            {
                instance.SetIdentification(" magnetic trinity ", 24);
                Assert.That(instance.IdentificationProductName,
                    Is.EqualTo("MAGNETIC TRINITY"));
                Assert.That(instance.IdentificationLevelText,
                    Is.EqualTo("REFINED · LEVEL 24"));

                TextMesh[] marks = instance.GetComponentsInChildren<TextMesh>(true)
                    .Where(mark => mark.name == "CollectorTierAndLevel"
                        || mark.name == "CollectorProductName")
                    .ToArray();
                Assert.That(marks.Length, Is.EqualTo(2));
                Assert.That(marks.Select(mark => mark.anchor),
                    Has.All.EqualTo(TextAnchor.MiddleLeft));
                Assert.That(marks.Select(mark => mark.alignment),
                    Has.All.EqualTo(TextAlignment.Left));
                float sharedLabelX = marks[0].transform.localPosition.x;
                foreach (TextMesh mark in marks)
                {
                    Assert.That(mark.font.name, Does.Contain("Oxanium"));
                    Assert.That(mark.transform.localPosition.x,
                        Is.EqualTo(sharedLabelX).Within(0.0001f),
                        "Both lines must sit flush on the same label margin.");
                }

                instance.SetIdentification("EDGE TRIAD", -10);
                Assert.That(instance.IdentificationLevelText,
                    Is.EqualTo("STANDARD · LEVEL 1"));
                instance.SetIdentification("EDGE TRIAD", 500);
                Assert.That(instance.IdentificationLevelText,
                    Is.EqualTo("HEIRLOOM · LEVEL 100"));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance.gameObject);
            }
        }

        [Test]
        public void FeaturedBadge_UsesCanonicalArtworkAndHidesUnknownOrEmptyState()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            PremiumDisplayCase instance = UnityEngine.Object.Instantiate(prefab);
            try
            {
                FieldInfo bindingField = typeof(PremiumDisplayCase).GetField(
                    "featuredBadgeArtwork",
                    BindingFlags.Instance | BindingFlags.NonPublic);
                Assert.That(bindingField, Is.Not.Null);
                var bindings = (PremiumDisplayCaseBadgeArtworkBinding[])
                    bindingField.GetValue(instance);
                Assert.That(bindings.Length,
                    Is.EqualTo(BadgeCatalogV2.ToyDefinitions.Count));
                Assert.That(bindings.Select(binding => binding.AssetName).Distinct()
                    .Count(), Is.EqualTo(bindings.Length));
                Assert.That(bindings.Select(binding => binding.Artwork),
                    Has.All.Not.Null);

                instance.SetFeaturedBadge(
                    "badge-b8-toy-pulse-100k",
                    "100k",
                    "pulse",
                    BadgeGrade.Singularity.ToString());
                Assert.That(instance.HasFeaturedBadge, Is.True);
                Assert.That(instance.FeaturedBadgeAssetName,
                    Is.EqualTo("badge-b8-toy-pulse-100k"));
                Assert.That(instance.FeaturedBadgeToken, Is.EqualTo("100K"));
                Assert.That(instance.FeaturedBadgeShortName, Is.EqualTo("PULSE"));
                TextMesh tokenMark = instance.GetComponentsInChildren<TextMesh>(true)
                    .Single(mark => mark.name == "FeaturedBadgeToken");
                Color singularityColor = tokenMark.color;
                instance.SetFeaturedBadge(
                    "badge-b8-toy-power-ignition",
                    "1.0",
                    "power",
                    BadgeGrade.Ignition.ToString());
                Assert.That(tokenMark.color.r,
                    Is.EqualTo(singularityColor.r).Within(0.0001f));
                Assert.That(tokenMark.color.g,
                    Is.EqualTo(singularityColor.g).Within(0.0001f));
                Assert.That(tokenMark.color.b,
                    Is.EqualTo(singularityColor.b).Within(0.0001f));

                Renderer badgeRenderer = instance.GetComponentsInChildren<Renderer>(
                        true)
                    .Single(renderer => renderer.name == "FeaturedBadgeArtwork");
                Transform badgeRoot = instance.GetComponentsInChildren<Transform>(
                        true)
                    .Single(child => child.name == "FeaturedBadgeRoot");
                Assert.That(badgeRoot.localPosition.y,
                    Is.EqualTo(0.108f).Within(0.0001f));
                Assert.That(badgeRenderer.transform.localPosition.x,
                    Is.EqualTo(-0.013f).Within(0.0001f));
                Assert.That(badgeRenderer.transform.localScale.x,
                    Is.EqualTo(0.022f).Within(0.0001f));
                Assert.That(tokenMark.transform.localPosition.x,
                    Is.EqualTo(0.012f).Within(0.0001f));
                TextMesh shortNameMark = instance.GetComponentsInChildren<TextMesh>(
                        true)
                    .Single(mark => mark.name == "FeaturedBadgeShortName");
                Assert.That(shortNameMark.transform.localPosition.x,
                    Is.EqualTo(0.012f).Within(0.0001f));
                Assert.That(badgeRenderer.sharedMaterial.shader.name,
                    Is.EqualTo("FidgetingApp/PremiumBadgeArtwork"));
                Assert.That(badgeRenderer.sharedMaterial.HasProperty("_EtchColor"),
                    Is.True);
                Assert.That(badgeRenderer.sharedMaterial.HasProperty("_Tint"),
                    Is.False);

                instance.SetFeaturedBadge(
                    "missing-artwork",
                    "999",
                    "invalid",
                    BadgeGrade.Singularity.ToString());
                Assert.That(instance.HasFeaturedBadge, Is.False);
                Assert.That(instance.FeaturedBadgeAssetName, Is.Empty);
                Assert.That(instance.FeaturedBadgeToken, Is.Empty);
                Assert.That(instance.FeaturedBadgeShortName, Is.Empty);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance.gameObject);
            }
        }

        [Test]
        public void ProductSnapshot_CopiesCurrentVisualsWithoutPhysicsOrInput()
        {
            GameObject source = GameObject.CreatePrimitive(PrimitiveType.Cube);
            source.name = "CurrentSelectedProduct";
            source.transform.position = new Vector3(0.12f, 0.08f, -0.04f);
            source.transform.rotation = Quaternion.Euler(11f, 23f, 7f);
            source.AddComponent<Rigidbody>();
            MeshRenderer sourceRenderer = source.GetComponent<MeshRenderer>();
            var sourceProperties = new MaterialPropertyBlock();
            int propertyId = Shader.PropertyToID("_DisplayCaseSnapshotTest");
            sourceProperties.SetFloat(propertyId, 0.63f);
            sourceRenderer.SetPropertyBlock(sourceProperties);

            GameObject snapshot = PremiumDisplayCaseProductSnapshot.Capture(
                ProductCatalog.GoldFourWingModelId,
                source.transform);

            try
            {
                Assert.That(snapshot.activeSelf, Is.False);
                Assert.That(snapshot.name, Does.Contain("gold_four_wing"));
                Assert.That(snapshot.GetComponentsInChildren<MeshFilter>(true).Length,
                    Is.EqualTo(1));
                Assert.That(snapshot.GetComponentsInChildren<MeshRenderer>(true).Length,
                    Is.EqualTo(1));
                Assert.That(snapshot.GetComponentsInChildren<Collider>(true), Is.Empty);
                Assert.That(snapshot.GetComponentsInChildren<Rigidbody>(true), Is.Empty);
                Assert.That(snapshot.GetComponentsInChildren<Camera>(true), Is.Empty);
                Assert.That(snapshot.GetComponentsInChildren<AudioSource>(true), Is.Empty);
                Assert.That(snapshot.GetComponentsInChildren<MonoBehaviour>(true)
                        .Select(component => component.GetType()),
                    Is.EquivalentTo(new[]
                    {
                        typeof(PremiumDisplayCaseRuntimeMeshOwner)
                    }));

                MeshRenderer captured = snapshot.GetComponentInChildren<MeshRenderer>(true);
                Assert.That(captured.sharedMaterials,
                    Is.EqualTo(sourceRenderer.sharedMaterials));
                var capturedProperties = new MaterialPropertyBlock();
                captured.GetPropertyBlock(capturedProperties);
                Assert.That(capturedProperties.GetFloat(propertyId),
                    Is.EqualTo(0.63f).Within(0.0001f));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(snapshot);
                UnityEngine.Object.DestroyImmediate(source);
            }
        }

        [Test]
        public void ProductSnapshot_RemovesShippingTransformThenNormalizesPrizeFront()
        {
            var sourceRoot = new GameObject("ShippingProductRoot");
            sourceRoot.transform.position = new Vector3(4f, -3f, 7f);
            sourceRoot.transform.rotation = Quaternion.Euler(23f, -41f, 12f);
            sourceRoot.transform.localScale = Vector3.one * 2.75f;

            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
            visual.name = "AuthoredProductVisual";
            visual.transform.SetParent(sourceRoot.transform, false);
            visual.transform.localPosition = new Vector3(0.12f, -0.04f, 0.03f);
            visual.transform.localRotation = Quaternion.Euler(7f, 18f, -5f);
            visual.transform.localScale = new Vector3(0.08f, 0.06f, 0.02f);

            GameObject snapshot = PremiumDisplayCaseProductSnapshot.Capture(
                ProductCatalog.GraphiteTwoLobeModelId,
                sourceRoot.transform);
            try
            {
                Transform captured = snapshot.transform.GetChild(0);
                PremiumDisplayCasePrizeNormalization normalization =
                    PremiumDisplayCaseProductProfiles.Resolve(
                        ProductCatalog.GraphiteTwoLobeModelId)
                    .PrizeNormalization;
                Matrix4x4 authoredLocal = Matrix4x4.TRS(
                    visual.transform.localPosition,
                    visual.transform.localRotation,
                    visual.transform.localScale);
                Matrix4x4 expectedLocal = normalization.SnapshotLocalMatrix
                    * authoredLocal;
                Assert.That(Vector3.Distance(
                        captured.localPosition,
                        expectedLocal.GetPosition()),
                    Is.LessThan(0.00001f));
                Assert.That(Quaternion.Angle(
                        captured.localRotation,
                        expectedLocal.rotation),
                    Is.LessThan(0.001f));
                Assert.That(Vector3.Distance(
                        captured.localScale,
                        expectedLocal.lossyScale),
                    Is.LessThan(0.00001f));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(snapshot);
                UnityEngine.Object.DestroyImmediate(sourceRoot);
            }
        }

        [Test]
        public void CollectorSlab_BackingIsOpaqueVelvetAndRarityBandIsBrushedMetal()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            Transform[] transforms = prefab.GetComponentsInChildren<Transform>(true);

            Renderer back = transforms.Single(item =>
                item.name == "Collector_BlackFlocking").GetComponent<Renderer>();
            Renderer rarityBand = transforms.Single(item =>
                item.name == "Collector_RarityFoilBand").GetComponent<Renderer>();

            Assert.That(back.sharedMaterial.name, Is.EqualTo("BlackVelvet"));
            Assert.That(rarityBand.sharedMaterial.name, Is.EqualTo("BrushedMetal"));
            Assert.That(back.sharedMaterial.shader.name,
                Is.Not.EqualTo("FidgetingApp/PremiumAcrylicLiquidGlass"),
                "The label backing must stay opaque velvet, not floating acrylic.");
        }

        [Test]
        public void CameraRules_PreserveHorizontalCompositionOnTallPhones()
        {
            float reference =
                PremiumDisplayCaseCameraRules.ResolveVerticalFieldOfView(
                    PremiumDisplayCaseCameraRules.ReferenceAspect);
            float phone = PremiumDisplayCaseCameraRules.ResolveVerticalFieldOfView(
                942f / 2048f);

            Assert.That(reference, Is.EqualTo(29f).Within(0.0001f));
            Assert.That(phone, Is.GreaterThan(45f));
            float referenceHorizontal = Camera.VerticalToHorizontalFieldOfView(
                reference,
                PremiumDisplayCaseCameraRules.ReferenceAspect);
            float phoneHorizontal = Camera.VerticalToHorizontalFieldOfView(
                phone,
                942f / 2048f);
            Assert.That(phoneHorizontal,
                Is.EqualTo(referenceHorizontal).Within(0.0001f));
        }

        [Test]
        public void CameraRules_DefaultPoseIsAnExactCenteredFrontView()
        {
            Vector3 camera = PremiumDisplayCaseCameraRules.FrontCameraPosition;
            Vector3 target = PremiumDisplayCaseCameraRules.FrontLookAt;
            Vector3 direction = (target - camera).normalized;

            Assert.That(camera.x, Is.EqualTo(0f).Within(0.0001f));
            Assert.That(target.x, Is.EqualTo(0f).Within(0.0001f));
            Assert.That(camera.y, Is.EqualTo(target.y).Within(0.0001f));
            Assert.That(direction.x, Is.EqualTo(0f).Within(0.0001f));
            Assert.That(direction.y, Is.EqualTo(0f).Within(0.0001f));
            Assert.That(direction.z, Is.EqualTo(1f).Within(0.0001f));
        }

        [Test]
        public void CameraLease_SuppressesDirectAuthorsAndRestoresFullState()
        {
            var cameraObject = new GameObject("ShippingCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            DisplayCaseCameraStateAuthorProbe author = cameraObject.AddComponent<
                DisplayCaseCameraStateAuthorProbe>();

            try
            {
                camera.transform.SetPositionAndRotation(
                    new Vector3(0.31f, -0.22f, 0.44f),
                    Quaternion.Euler(17f, 31f, -9f));
                camera.orthographic = false;
                camera.aspect = 0.71f;
                camera.nearClipPlane = 0.023f;
                camera.farClipPlane = 77f;
                camera.sensorSize = new Vector2(32f, 18f);
                camera.lensShift = new Vector2(0.07f, -0.04f);
                camera.gateFit = Camera.GateFitMode.Overscan;
                camera.usePhysicalProperties = true;
                camera.focalLength = 61f;
                camera.iso = 320;
                camera.shutterSpeed = 0.0125f;
                camera.aperture = 3.2f;
                camera.focusDistance = 1.7f;
                camera.bladeCount = 7;
                camera.curvature = new Vector2(1.7f, 8.2f);
                camera.barrelClipping = 0.21f;
                camera.anamorphism = 0.33f;
                Matrix4x4 customProjection = Matrix4x4.Perspective(
                    37f,
                    camera.aspect,
                    camera.nearClipPlane,
                    camera.farClipPlane);
                customProjection.m02 = 0.08f;
                customProjection.m12 = -0.05f;
                camera.projectionMatrix = customProjection;
                camera.nonJitteredProjectionMatrix = customProjection;
                camera.useJitteredProjectionMatrixForTransparentRendering = false;
                PremiumDisplayCaseCameraState expected =
                    PremiumDisplayCaseCameraState.Capture(camera);

                PremiumDisplayCaseCameraLease lease =
                    PremiumDisplayCaseCameraLease.Acquire(camera);
                Assert.That(lease, Is.Not.Null);
                Assert.That(lease.CameraStateAuthorCount, Is.EqualTo(1));
                Assert.That(author.enabled, Is.False);
                Assert.That(author.Suppressed, Is.True);
                Assert.That(camera.orthographic, Is.False);
                Assert.That(camera.usePhysicalProperties, Is.False);
                Assert.That(camera.lensShift, Is.EqualTo(Vector2.zero));
                Assert.That(Vector3.Distance(
                        camera.transform.position,
                        PremiumDisplayCaseCameraRules.FrontCameraPosition),
                    Is.LessThan(0.000001f));

                Vector3 ownedPosition = camera.transform.position;
                Matrix4x4 ownedProjection = camera.projectionMatrix;
                author.AttemptCameraWrite();
                Assert.That(camera.transform.position, Is.EqualTo(ownedPosition),
                    "Direct callbacks must not bypass display-case ownership.");
                AssertMatrixEquals(ownedProjection, camera.projectionMatrix);

                lease.Restore();
                Assert.That(author.enabled, Is.True);
                Assert.That(author.Suppressed, Is.False);
                Assert.That(camera.transform.position,
                    Is.EqualTo(expected.Position));
                Assert.That(camera.transform.rotation,
                    Is.EqualTo(expected.Rotation));
                Assert.That(camera.orthographic,
                    Is.EqualTo(expected.Orthographic));
                Assert.That(camera.usePhysicalProperties,
                    Is.EqualTo(expected.UsePhysicalProperties));
                Assert.That(camera.focalLength,
                    Is.EqualTo(expected.FocalLength).Within(0.0001f));
                Assert.That(camera.sensorSize, Is.EqualTo(expected.SensorSize));
                Assert.That(camera.lensShift, Is.EqualTo(expected.LensShift));
                Assert.That(camera.gateFit, Is.EqualTo(expected.GateFit));
                Assert.That(camera.nearClipPlane,
                    Is.EqualTo(expected.NearClipPlane).Within(0.000001f));
                Assert.That(camera.farClipPlane,
                    Is.EqualTo(expected.FarClipPlane).Within(0.0001f));
                AssertMatrixEquals(expected.ProjectionMatrix,
                    camera.projectionMatrix);
                AssertMatrixEquals(expected.NonJitteredProjectionMatrix,
                    camera.nonJitteredProjectionMatrix);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(cameraObject);
            }
        }

        [Test]
        public void CameraRules_ValidateRealCaseViewportAndRejectPoseOverwrite()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null);
            PremiumDisplayCase displayCase = UnityEngine.Object.Instantiate(prefab);
            var cameraObject = new GameObject("DisplayCaseValidationCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.aspect = 942f / 2048f;

            try
            {
                // Shipping acknowledges the presentation at the first
                // EndOfFrame while the shared case is still closed.  Validate
                // that exact phase; fully revealed authored layers may
                // intentionally slide beyond the closed-shell viewport.
                displayCase.SetRevealProgressForPreview(0f);
                PremiumDisplayCaseCameraRules.ApplyFrontPresentation(camera);
                Assert.That(PremiumDisplayCaseCameraRules.TryValidateFrontPresentation(
                        camera,
                        displayCase.transform,
                        out string validReason),
                    Is.True,
                    validReason);

                camera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
                Assert.That(PremiumDisplayCaseCameraRules.TryValidateFrontPresentation(
                        camera,
                        displayCase.transform,
                        out string overwrittenReason),
                    Is.False);
                Assert.That(overwrittenReason,
                    Is.EqualTo("display-camera-pose-overwritten"));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(cameraObject);
                UnityEngine.Object.DestroyImmediate(displayCase.gameObject);
            }
        }

        [Test]
        public void AllShippingCameraAuthors_ImplementExplicitSuppressionContract()
        {
            Type contract = typeof(IPremiumDisplayCaseCameraStateAuthor);
            Type[] cameraAuthors =
            {
                typeof(OrbitPresentationCamera),
                typeof(EdcPortraitCameraFramer),
                typeof(PortraitCameraFramer),
                typeof(SpinnerSceneParallaxController),
                typeof(FanCardCameraProjectionGuard)
            };

            Assert.That(cameraAuthors, Has.All.Matches<Type>(
                author => contract.IsAssignableFrom(author)));
            string[] sources =
            {
                "Assets/_Fidgeting/Runtime/Presentation/OrbitPresentationCamera.cs",
                "Assets/_EDC/Runtime/EdcPortraitCameraFramer.cs",
                "Assets/Scripts/FidgetSpinner/PortraitCameraFramer.cs",
                "Assets/Scripts/Product/SpinnerSceneParallaxController.cs",
                "Assets/_FanCard/Runtime/FanCardCameraProjectionGuard.cs"
            };
            foreach (string path in sources)
            {
                string source = File.ReadAllText(path);
                StringAssert.Contains(
                    "displayCaseCameraControlSuppressed",
                    source,
                    path);
                StringAssert.Contains(
                    "SetDisplayCaseCameraControlSuppressed",
                    source,
                    path);
            }
        }

        [Test]
        public void RevealMotion_HasClosedMidAndSettledStates()
        {
            PremiumDisplayCaseRevealSample closed =
                PremiumDisplayCaseRevealMotion.Evaluate(0f);
            PremiumDisplayCaseRevealSample middle =
                PremiumDisplayCaseRevealMotion.Evaluate(
                    PremiumDisplayCaseRevealMotion.DurationSeconds * 0.58f);
            PremiumDisplayCaseRevealSample open =
                PremiumDisplayCaseRevealMotion.Evaluate(
                    PremiumDisplayCaseRevealMotion.DurationSeconds);

            Assert.That(closed.LidOpen, Is.EqualTo(0f));
            Assert.That(closed.ContentVisibility, Is.EqualTo(0f));
            Assert.That(middle.LidOpen, Is.GreaterThan(0.9f));
            Assert.That(middle.ContentVisibility, Is.GreaterThan(0f));
            Assert.That(open.CaseRise, Is.EqualTo(1f).Within(0.0001f));
            Assert.That(open.ContentVisibility, Is.EqualTo(1f).Within(0.0001f));
            Assert.That(open.Complete, Is.True);
        }

        [Test]
        public void LidMotion_ClosedIsFlushAndOpenClearsCaseToUpperRight()
        {
            PremiumDisplayCaseLidPose closed = PremiumDisplayCaseLidMotion.Evaluate(
                PremiumDisplayCaseRevealMotion.Evaluate(0f));
            PremiumDisplayCaseLidPose open = PremiumDisplayCaseLidMotion.Evaluate(
                PremiumDisplayCaseRevealMotion.Evaluate(
                    PremiumDisplayCaseRevealMotion.DurationSeconds));

            Assert.That(closed.PositionOffset, Is.EqualTo(Vector3.zero));
            Assert.That(closed.EulerOffset, Is.EqualTo(Vector3.zero));
            Assert.That(open.PositionOffset.x, Is.EqualTo(0.310f).Within(0.0001f));
            Assert.That(open.PositionOffset.y, Is.EqualTo(0.185f).Within(0.0001f));
            Assert.That(open.EulerOffset.x, Is.EqualTo(-15f).Within(0.0001f));
        }

        [Test]
        public void Parallax_ContentTravelsMoreThanAcrylicAndBoxCounters()
        {
            PremiumDisplayCaseParallaxSample sample =
                PremiumDisplayCaseParallaxRules.Evaluate(new Vector2(0.8f, -0.4f));

            Assert.That(sample.ContentOffset.magnitude,
                Is.GreaterThan(sample.InteriorOffset.magnitude));
            Assert.That(sample.InteriorOffset.magnitude,
                Is.GreaterThan(sample.AcrylicOffset.magnitude));
            Assert.That(Mathf.Sign(sample.BoxOffset.x),
                Is.Not.EqualTo(Mathf.Sign(sample.ContentOffset.x)));
            Assert.That(Mathf.Abs(sample.EulerAngles.y),
                Is.LessThanOrEqualTo(PremiumDisplayCaseParallaxRules.MaximumTiltDegrees));
        }

        [Test]
        public void PublicApi_MatchesGachaContract()
        {
            Type type = typeof(PremiumDisplayCase);
            Assert.That(type.GetMethod("setContent", new[] { typeof(Transform) }),
                Is.Not.Null);
            Assert.That(type.GetMethod("setContent", new[]
            {
                typeof(Transform),
                typeof(PremiumDisplayCaseContentOptions)
            }), Is.Not.Null);
            Assert.That(type.GetMethod("play", Type.EmptyTypes), Is.Not.Null);
            Assert.That(type.GetEvent("onRevealComplete"), Is.Not.Null);
            Assert.That(type.GetMethod("setCapsulePreset", new[]
            {
                typeof(PremiumDisplayCaseCapsulePreset)
            }), Is.Not.Null);
        }

        [Test]
        public void RevealComplete_FiresOncePerPlayAndCanReplay()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            PremiumDisplayCase instance = UnityEngine.Object.Instantiate(prefab);
            FieldInfo elapsedField = typeof(PremiumDisplayCase).GetField(
                "revealElapsed",
                BindingFlags.Instance | BindingFlags.NonPublic);
            MethodInfo updateMethod = typeof(PremiumDisplayCase).GetMethod(
                "Update",
                BindingFlags.Instance | BindingFlags.NonPublic);
            Assert.That(elapsedField, Is.Not.Null);
            Assert.That(updateMethod, Is.Not.Null);
            int callbackCount = 0;
            instance.onRevealComplete += () => callbackCount++;

            instance.play();
            elapsedField.SetValue(instance,
                PremiumDisplayCaseRevealMotion.DurationSeconds);
            updateMethod.Invoke(instance, null);
            updateMethod.Invoke(instance, null);
            Assert.That(callbackCount, Is.EqualTo(1));
            Assert.That(instance.IsRevealPlaying, Is.False);

            instance.play();
            elapsedField.SetValue(instance,
                PremiumDisplayCaseRevealMotion.DurationSeconds);
            updateMethod.Invoke(instance, null);
            Assert.That(callbackCount, Is.EqualTo(2));
            UnityEngine.Object.DestroyImmediate(instance.gameObject);
        }

        [Test]
        public void ShippingPrefab_HasContentSlotPlaceholderAndBothCapsules()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);

            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            Transform[] transforms = prefab.GetComponentsInChildren<Transform>(true);
            Assert.That(transforms.Count(item => item.name == "contentSlot"),
                Is.EqualTo(1));
            Assert.That(transforms.Any(item =>
                item.name == "DevelopmentPlaceholder_Coin"), Is.True);
            Assert.That(transforms.Any(item =>
                item.name == "CircularCapsuleGeometry"), Is.True);
            Assert.That(transforms.Any(item =>
                item.name == "RoundedSquareCapsuleGeometry"), Is.True);
            Assert.That(prefab.GetComponent<PremiumDisplayCaseGyroAdapter>(), Is.Not.Null);
            Assert.That(prefab.GetComponent<PremiumDisplayCaseInteractionController>(),
                Is.Not.Null);
            Assert.That(prefab.GetComponentsInChildren<Light>(true).Length,
                Is.GreaterThanOrEqualTo(3));
        }

        [Test]
        public void ExplodedLayout_IsDeterministicStaggeredAndReassemblesExactly()
        {
            Vector3 offset = new Vector3(0.12f, -0.05f, 0.18f);
            PremiumDisplayCaseExplodedSample assembled =
                PremiumDisplayCaseExplodedLayout.Evaluate(4, 8, 0f, offset);
            PremiumDisplayCaseExplodedSample earlyFront =
                PremiumDisplayCaseExplodedLayout.Evaluate(0, 8, 0.24f, offset);
            PremiumDisplayCaseExplodedSample earlyBack =
                PremiumDisplayCaseExplodedLayout.Evaluate(7, 8, 0.24f, offset);
            PremiumDisplayCaseExplodedSample exploded =
                PremiumDisplayCaseExplodedLayout.Evaluate(4, 8, 1f, offset);

            Assert.That(assembled.Offset, Is.EqualTo(Vector3.zero));
            Assert.That(earlyFront.Visibility, Is.GreaterThan(earlyBack.Visibility));
            Assert.That(Vector3.Distance(exploded.Offset, offset),
                Is.LessThan(0.000001f));
            Assert.That(PremiumDisplayCaseExplodedLayout.AssemblyDurationSeconds,
                Is.EqualTo(1.35f).Within(0.0001f));
        }

        [Test]
        public void ExplodedLayout_ContentSlotFollowsNeutralCapsuleLayerExactly()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            PremiumDisplayCase instance = UnityEngine.Object.Instantiate(prefab);
            PremiumDisplayCaseInteractionController interaction =
                instance.GetComponent<PremiumDisplayCaseInteractionController>();
            Transform[] transforms = instance.GetComponentsInChildren<Transform>(true);
            Transform capsule = transforms.Single(item =>
                item.name == "Layer_04_Capsule");
            Transform content = transforms.Single(item =>
                item.name == "ContentParallaxRoot");
            Vector3 capsuleAssembled = capsule.localPosition;
            Vector3 contentAssembled = content.localPosition;

            interaction.SetExplodedProgressForPreview(1f);

            Vector3 capsuleDisplacement = capsule.localPosition - capsuleAssembled;
            Vector3 contentDisplacement = content.localPosition - contentAssembled;
            Assert.That(Vector3.Distance(
                capsuleDisplacement,
                contentDisplacement), Is.LessThan(0.000001f));
            UnityEngine.Object.DestroyImmediate(instance.gameObject);
        }

        [Test]
        public void ShippingPrefab_UsesBlenderFbxForAllApprovedCaseLayers()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            string[] layerNames =
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
            Transform[] transforms = prefab.GetComponentsInChildren<Transform>(true);
            foreach (string layerName in layerNames)
            {
                Transform layer = transforms.SingleOrDefault(item => item.name == layerName);
                Assert.That(layer, Is.Not.Null, $"Missing Blender layer {layerName}.");
                MeshFilter[] filters = layer.GetComponentsInChildren<MeshFilter>(true);
                Assert.That(filters.Length, Is.GreaterThan(0), layerName);
                Assert.That(filters.All(filter =>
                    AssetDatabase.GetAssetPath(filter.sharedMesh)
                        == "Assets/_DisplayCase/Models/PremiumDisplayCase.fbx"),
                    Is.True,
                    $"{layerName} contains non-FBX shipping geometry.");
            }

            Assert.That(transforms.Count(item =>
                item.name.StartsWith("Polycarbonate_FrontStep_")), Is.EqualTo(4));
            Assert.That(transforms.Count(item =>
                item.name.StartsWith("Polycarbonate_RearStep_")), Is.EqualTo(4));
            Assert.That(transforms.Count(item =>
                item.name.StartsWith("Polycarbonate_SpacerFrame_")), Is.EqualTo(4));

            foreach (Transform edge in transforms.Where(item =>
                         item.name.StartsWith("Polycarbonate_FrontStep_")
                         || item.name.StartsWith("Polycarbonate_RearStep_")
                         || item.name.StartsWith("Polycarbonate_SpacerFrame_")))
            {
                Assert.That(edge.GetComponent<Renderer>().sharedMaterial.name,
                    Is.EqualTo("LiquidGlassEdge"), edge.name);
            }

            Renderer front = transforms.Single(item =>
                item.name == "Polycarbonate_FrontShell").GetComponent<Renderer>();
            Renderer rear = transforms.Single(item =>
                item.name == "Polycarbonate_RearShell").GetComponent<Renderer>();
            Assert.That(front.sharedMaterial.name, Is.EqualTo("LiquidGlass"));
            Assert.That(rear.sharedMaterial.name, Is.EqualTo("LiquidGlass"));
            Assert.That(front.bounds.center.z, Is.LessThan(rear.bounds.center.z),
                "FBX depth must face the shipping camera; rear shell cannot occlude content.");
        }

        [Test]
        public void BlenderManifest_IsReferenceClearAcrylicAndContainsNoPrizeGeometry()
        {
            string manifest = File.ReadAllText(
                "ArtSource/DisplayCase/premium_display_case_manifest.json");
            StringAssert.Contains("\"containsPrizeGeometry\": false", manifest);
            StringAssert.Contains("\"contentSlot\": \"ContentSlot_Anchor\"", manifest);
            StringAssert.Contains("\"diameterMm\": 84", manifest);
            StringAssert.Contains(
                "\"style\": \"clear-acrylic-four-fastener\"", manifest);
            StringAssert.Contains("\"hasOpaqueOuterBox\": false", manifest);
            StringAssert.Contains(
                "\"fastenerStyle\": \"black-cap-with-chrome-collar\"", manifest);
            StringAssert.DoesNotContain("TRINITY", manifest.ToUpperInvariant());
            StringAssert.DoesNotContain("TRI-BLADE", manifest.ToUpperInvariant());
        }

        [Test]
        public void NativeBridge_ExposesDragPinchScrubReplayAndCloseLifecycle()
        {
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");

            StringAssert.Contains("PremiumDisplayCaseExperienceView", swift);
            StringAssert.Contains("Text(\"装配并重播\")", swift);
            StringAssert.DoesNotContain(
                "Label(\"装配并重播\", systemImage: \"play.fill\")",
                swift,
                "The primary display-case CTA must remain text-only under the "
                + "shipping Liquid Glass guideline.");
            StringAssert.Contains("DragGesture(minimumDistance: 0)", swift);
            StringAssert.Contains(
                "orbitStart.width - value.translation.width * 0.16",
                swift,
                "Horizontal case orbit must move the visible surface with the finger.");
            StringAssert.Contains(
                "orbitStart.height - value.translation.height * 0.16",
                swift,
                "Vertical case orbit must move the visible surface with the finger.");
            StringAssert.DoesNotContain(
                "orbitStart.width + value.translation.width * 0.16",
                swift);
            StringAssert.Contains("MagnificationGesture()", swift);
            StringAssert.Contains("SetDisplayCaseExplodedProgressFromNativeUi", swift);
            StringAssert.Contains("PlayDisplayCaseAssemblyFromNativeUi", swift);
            StringAssert.Contains("SetDisplayCasePresentedFromNativeUi", swift);
            StringAssert.Contains(
                "@AppStorage(\"FidgetingApp.DisplayCaseLightingPreset\")",
                swift);
            StringAssert.Contains("DisplayCaseLightingPreset.allCases", swift);
            StringAssert.Contains("SetDisplayCaseLightingFromNativeUi", swift);
            StringAssert.Contains("public void SetDisplayCasePresentedFromNativeUi", coordinator);
            StringAssert.Contains(
                "public void SetDisplayCaseLightingFromNativeUi",
                coordinator);
            StringAssert.Contains(
                "PremiumDisplayCaseLightingCatalog.PreferenceKey",
                coordinator);
            StringAssert.Contains("activeDisplayCase?.SetLightingPreset", coordinator);
            StringAssert.Contains("DismissDisplayCaseExperience();", coordinator);
            StringAssert.Contains("PremiumDisplayCaseFactory.ResourcesPath", coordinator);
            StringAssert.Contains("DisplayCaseProductRoot(modelId)", coordinator);
            StringAssert.Contains("profile.SceneRootName", coordinator);
            StringAssert.Contains("PremiumDisplayCaseProductSnapshot.Capture", coordinator);
            StringAssert.Contains(
                "PremiumDisplayCaseProductProfiles.Resolve(modelId)",
                coordinator);
            StringAssert.Contains("activeDisplayCase.SetIdentification", coordinator);
            StringAssert.Contains(
                "BadgeCatalogV2.TryResolveFeaturedToyBadge",
                coordinator);
            StringAssert.Contains("activeDisplayCase.SetFeaturedBadge", coordinator);
            StringAssert.Contains("activeDisplayCase.ClearFeaturedBadge", coordinator);
            StringAssert.DoesNotContain(
                "ThreeBladeDisplayPrizeFactory.Instantiate()",
                coordinator);
            StringAssert.Contains("activeDisplayCase.setContent", coordinator);
        }

        [Test]
        public void ThreeBladePrize_UsesAuthoredMeshesAndMaterials()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                ThreeBladePrizePrefabPath);
            Assert.That(prefab, Is.Not.Null,
                "Run the three-blade display-prize builder first.");

            MeshFilter frame = prefab.GetComponentsInChildren<MeshFilter>(true)
                .Single(item => item.name == "ThreeBladeFrame");
            MeshFilter insets = prefab.GetComponentsInChildren<MeshFilter>(true)
                .Single(item => item.name == "ThreeBladeInsets");
            MeshFilter cap = prefab.GetComponentsInChildren<MeshFilter>(true)
                .Single(item => item.name == "TopCap");
            Assert.That(frame.sharedMesh.name, Is.EqualTo("M_ThreeBladeFrame"));
            Assert.That(insets.sharedMesh.name, Is.EqualTo("M_ThreeBladeInsets"));
            Assert.That(cap.sharedMesh.name, Is.EqualTo("M_ScallopedTopCap"));
            Assert.That(frame.GetComponent<MeshRenderer>().sharedMaterials
                .Select(material => material.name),
                Is.EquivalentTo(new[] { "M_BladeSandblast", "M_BevelPolished" }));
            Assert.That(cap.GetComponent<MeshRenderer>().sharedMaterials
                .Select(material => material.name),
                Is.EquivalentTo(new[] { "M_CapRadialBrushed", "M_BevelPolished" }));
        }

        [Test]
        public void ThreeBladePrizeFactory_UsesTheSharedSlidePresentation()
        {
            PremiumDisplayCaseContentOptions options =
                ThreeBladeDisplayPrizeFactory.ContentOptions;

            Assert.That(options.InitialEulerAngles.x,
                Is.EqualTo(90f).Within(0.0001f));
            Assert.That(options.InitialEulerAngles.y,
                Is.EqualTo(-8f).Within(0.0001f));
            Assert.That(options.IdleRotationEnabled, Is.True);
            Assert.That(options.IdleRotationPeriodSeconds,
                Is.EqualTo(6f).Within(0.0001f));
        }

        [Test]
        public void SetContent_ParentsArbitraryNodeAndRestoresCallerOwnership()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            PremiumDisplayCase instance = UnityEngine.Object.Instantiate(prefab);
            GameObject callerRoot = new GameObject("CallerOwnedPrizeRoot");
            GameObject prize = GameObject.CreatePrimitive(PrimitiveType.Cube);
            prize.name = "ArbitraryImportedGltfRoot";
            prize.transform.SetParent(callerRoot.transform, false);
            prize.transform.localPosition = new Vector3(1f, 2f, 3f);
            prize.transform.localScale = new Vector3(2f, 0.5f, 1.2f);
            prize.SetActive(false);

            instance.setContent(prize.transform,
                new PremiumDisplayCaseContentOptions(false, 7f, Vector3.zero));

            Assert.That(prize.transform.IsChildOf(instance.ContentSlot), Is.True);
            Assert.That(prize.activeSelf, Is.True);
            typeof(PremiumDisplayCase).GetMethod(
                "OnDisable",
                BindingFlags.Instance | BindingFlags.NonPublic)?.Invoke(
                    instance,
                    null);
            UnityEngine.Object.DestroyImmediate(instance.gameObject);
            Assert.That(prize.transform.parent, Is.EqualTo(callerRoot.transform));
            Assert.That(Vector3.SqrMagnitude(
                prize.transform.localPosition - new Vector3(1f, 2f, 3f)),
                Is.LessThan(0.00000001f));
            Assert.That(Vector3.SqrMagnitude(
                prize.transform.localScale - new Vector3(2f, 0.5f, 1.2f)),
                Is.LessThan(0.00000001f));
            Assert.That(prize.activeSelf, Is.False);

            UnityEngine.Object.DestroyImmediate(callerRoot);
        }

        [Test]
        public void CaseRendering_DoesNotDependOnPrizeTexturesOrSensorOwnership()
        {
            string shader = File.ReadAllText(
                "Assets/_DisplayCase/Shaders/PremiumAcrylicLiquidGlass.shader");
            string gyro = File.ReadAllText(
                "Assets/_DisplayCase/Runtime/PremiumDisplayCaseGyroAdapter.cs");
            string runtime = File.ReadAllText(
                "Assets/_DisplayCase/Runtime/PremiumDisplayCase.cs");

            StringAssert.DoesNotContain("sampler2D", shader);
            StringAssert.DoesNotContain("TEXTURE2D", shader);
            StringAssert.Contains("SceneParallaxInput.TryGetRecent", gyro);
            StringAssert.DoesNotContain("IosDeviceMotion.Start", gyro);
            StringAssert.DoesNotContain("IosDeviceMotion.Stop", gyro);
            StringAssert.DoesNotContain("TRINITY", runtime.ToUpperInvariant());
            StringAssert.DoesNotContain("TRI-BLADE", runtime.ToUpperInvariant());
        }

        [Test]
        public void ResourcesFactory_ResolvesShippingPrefab()
        {
            PremiumDisplayCase resource = Resources.Load<PremiumDisplayCase>(
                PremiumDisplayCaseFactory.ResourcesPath);
            Assert.That(resource, Is.Not.Null);
            Assert.That(Resources.Load<GameObject>(
                ThreeBladeDisplayPrizeFactory.ResourcesPath), Is.Not.Null);
        }

        private static void AssertMatrixEquals(
            Matrix4x4 expected,
            Matrix4x4 actual)
        {
            for (int index = 0; index < 16; index++)
            {
                Assert.That(actual[index],
                    Is.EqualTo(expected[index]).Within(0.000001f),
                    $"Matrix element {index}");
            }
        }

    }

    internal sealed class DisplayCaseCameraStateAuthorProbe : MonoBehaviour,
        IPremiumDisplayCaseCameraStateAuthor
    {
        public bool Suppressed { get; private set; }

        public void SetDisplayCaseCameraControlSuppressed(bool suppressed)
        {
            Suppressed = suppressed;
        }

        public void AttemptCameraWrite()
        {
            if (Suppressed)
            {
                return;
            }

            Camera camera = GetComponent<Camera>();
            camera.transform.SetPositionAndRotation(
                new Vector3(9f, 8f, 7f),
                Quaternion.Euler(40f, 50f, 60f));
            Matrix4x4 projection = camera.projectionMatrix;
            projection.m02 += 0.25f;
            camera.projectionMatrix = projection;
        }

        private void OnEnable()
        {
            AttemptCameraWrite();
        }

        private void OnDisable()
        {
            AttemptCameraWrite();
        }
    }
}
