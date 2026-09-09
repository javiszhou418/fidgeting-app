using System;
using System.IO;
using System.Linq;
using System.Reflection;
using FidgetingApp.Product;
using NUnit.Framework;
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
        public void DefaultContentOptions_EnableFourSecondIdleRotation()
        {
            PremiumDisplayCaseContentOptions options =
                PremiumDisplayCaseContentOptions.Default;

            Assert.That(options.IdleRotationEnabled, Is.True);
            Assert.That(options.IdleRotationPeriodSeconds,
                Is.EqualTo(4f).Within(0.0001f));
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
        public void ProductProfiles_CoverAllFourShippingModelsAndPreserveBaseline()
        {
            PremiumDisplayCaseProductProfile[] profiles =
                PremiumDisplayCaseProductProfiles.Profiles.ToArray();

            Assert.That(profiles.Length, Is.EqualTo(4));
            Assert.That(profiles.Select(profile => profile.ModelId),
                Is.EquivalentTo(ProductCatalog.ShippingModelIds()));
            Assert.That(profiles.Select(profile => profile.ModelId).Distinct().Count(),
                Is.EqualTo(4));
            Assert.That(profiles.Select(profile => profile.EnglishDisplayName),
                Has.All.Not.Empty);
            Assert.That(profiles.Select(profile => profile.EnglishDisplayName)
                    .Distinct().Count(),
                Is.EqualTo(4));
            Assert.That(profiles.All(profile =>
                    profile.EnglishDisplayName
                        == profile.EnglishDisplayName.ToUpperInvariant()),
                Is.True);

            PremiumDisplayCaseProductProfile magneticBaseline =
                PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MagneticSlideTileModelId);
            Assert.That(magneticBaseline.CapsulePreset,
                Is.EqualTo(PremiumDisplayCaseCapsulePreset.RoundedSquareDeep));
            Assert.That(magneticBaseline.ContentOptions.InitialEulerAngles,
                Is.EqualTo(new Vector3(90f, -8f, 0f)));
            Assert.That(magneticBaseline.ContentOptions.IdleRotationPeriodSeconds,
                Is.EqualTo(6f).Within(0.0001f));
            Assert.That(magneticBaseline.SceneRootName,
                Is.EqualTo("EDC_Root"));
            Assert.That(magneticBaseline.EnglishDisplayName,
                Is.EqualTo("MAGNETIC SLIDE"));

            foreach (PremiumDisplayCaseProductProfile profile in profiles)
            {
                Assert.That(profile.CapsulePreset,
                    Is.EqualTo(magneticBaseline.CapsulePreset),
                    profile.ModelId);
                Assert.That(profile.ContentOptions.IdleRotationEnabled,
                    Is.EqualTo(magneticBaseline.ContentOptions.IdleRotationEnabled),
                    profile.ModelId);
                Assert.That(profile.ContentOptions.IdleRotationPeriodSeconds,
                    Is.EqualTo(magneticBaseline.ContentOptions
                        .IdleRotationPeriodSeconds).Within(0.0001f),
                    profile.ModelId);
                Assert.That(profile.SceneRootName, Is.Not.Empty, profile.ModelId);
            }
            Assert.That(profiles
                    .Where(profile => profile.ModelId
                        != ProductCatalog.MagneticFanCardModelId)
                    .Select(profile => profile.ContentOptions.InitialEulerAngles),
                Has.All.EqualTo(magneticBaseline.ContentOptions.InitialEulerAngles));

            Assert.That(PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MetalThreeBladeModelId).SceneRootName,
                Is.EqualTo("ThreeBladeEDC_Root"));
            Assert.That(PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.GraphiteTwoLobeModelId).SceneRootName,
                Is.EqualTo("TwoLobeBar_Root"));
            Assert.That(PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MagneticFanCardModelId).SceneRootName,
                Is.EqualTo("MagneticFanCard_Root"));
            Assert.That(PremiumDisplayCaseProductProfiles.Resolve(
                    ProductCatalog.MagneticFanCardModelId)
                    .ContentOptions.InitialEulerAngles,
                Is.EqualTo(new Vector3(-90f, -8f, 0f)));
        }

        [Test]
        public void LaserIdentification_IsCenteredAndUsesCurrentClampedLevel()
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
                    Is.EqualTo("LEVEL 24"));

                TextMesh[] marks = instance.GetComponentsInChildren<TextMesh>(true)
                    .Where(mark => mark.name.StartsWith("Laser"))
                    .ToArray();
                Assert.That(marks.Length, Is.EqualTo(2));
                Assert.That(marks.Select(mark => mark.anchor),
                    Has.All.EqualTo(TextAnchor.MiddleCenter));
                Assert.That(marks.Select(mark => mark.alignment),
                    Has.All.EqualTo(TextAlignment.Center));
                foreach (TextMesh mark in marks)
                {
                    Assert.That(mark.font.name, Does.Contain("Oxanium"));
                    Assert.That(mark.transform.localPosition.x,
                        Is.EqualTo(0f).Within(0.0001f));
                }

                instance.SetIdentification("EDGE TRIAD", -10);
                Assert.That(instance.IdentificationLevelText, Is.EqualTo("LEVEL 1"));
                instance.SetIdentification("EDGE TRIAD", 500);
                Assert.That(instance.IdentificationLevelText, Is.EqualTo("LEVEL 100"));
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
                    Is.EqualTo(0.081f).Within(0.0001f));
                Assert.That(badgeRenderer.transform.localPosition.x,
                    Is.EqualTo(-0.014f).Within(0.0001f));
                Assert.That(badgeRenderer.transform.localScale.x,
                    Is.EqualTo(0.031f).Within(0.0001f));
                Assert.That(tokenMark.transform.localPosition.x,
                    Is.EqualTo(0.014f).Within(0.0001f));
                TextMesh shortNameMark = instance.GetComponentsInChildren<TextMesh>(
                        true)
                    .Single(mark => mark.name == "FeaturedBadgeShortName");
                Assert.That(shortNameMark.transform.localPosition.x,
                    Is.EqualTo(0.014f).Within(0.0001f));
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
        public void ProductSnapshot_RemovesShippingPresentationTransform()
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
                Assert.That(Vector3.Distance(
                        captured.localPosition,
                        visual.transform.localPosition),
                    Is.LessThan(0.00001f));
                Assert.That(Quaternion.Angle(
                        captured.localRotation,
                        visual.transform.localRotation),
                    Is.LessThan(0.001f));
                Assert.That(Vector3.Distance(
                        captured.localScale,
                        visual.transform.localScale),
                    Is.LessThan(0.00001f));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(snapshot);
                UnityEngine.Object.DestroyImmediate(sourceRoot);
            }
        }

        [Test]
        public void RoundedCapsule_UsesOpaqueNeutralMaterialsInsteadOfFloatingAcrylic()
        {
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<
                PremiumDisplayCase>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the display-case builder first.");
            Transform[] transforms = prefab.GetComponentsInChildren<Transform>(true);

            Renderer wall = transforms.Single(item =>
                item.name == "RoundedRecessWall").GetComponent<Renderer>();
            Renderer back = transforms.Single(item =>
                item.name == "RoundedRecessBack").GetComponent<Renderer>();
            Renderer edge = transforms.Single(item =>
                item.name == "RoundedEdgeLight").GetComponent<Renderer>();

            Assert.That(wall.sharedMaterial.name, Is.EqualTo("NeutralGraphite"));
            Assert.That(back.sharedMaterial.name, Is.EqualTo("BlackVelvet"));
            Assert.That(edge.sharedMaterial.name, Is.EqualTo("BrushedMetal"));
            Assert.That(new[] { wall, back }.Select(renderer =>
                    renderer.sharedMaterial.shader.name),
                Has.None.EqualTo("FidgetingApp/PremiumAcrylicLiquidGlass"));
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

            Assert.That(transforms.Count(item => item.name.StartsWith("Fastener_")),
                Is.EqualTo(4));
            Assert.That(transforms.Count(item => item.name.StartsWith("ChromeCollar_")),
                Is.EqualTo(4));
            Assert.That(transforms.Any(item => item.name == "MatteBlack_OuterTray"),
                Is.False);
            Assert.That(transforms.Any(item => item.name == "MatteBlack_BoxLid"),
                Is.False);
            Assert.That(transforms.Any(item => item.name == "Graphite_InnerTray"),
                Is.True);
            Assert.That(transforms.Count(item => item.name.StartsWith("Acrylic_BackFrame")),
                Is.EqualTo(4));

            foreach (Transform fastener in transforms.Where(item =>
                         item.name.StartsWith("Fastener_")))
            {
                Assert.That(fastener.GetComponent<Renderer>().sharedMaterial.name,
                    Is.EqualTo("MatteBlackBox"));
            }
            foreach (Transform collar in transforms.Where(item =>
                         item.name.StartsWith("ChromeCollar_")))
            {
                Assert.That(collar.GetComponent<Renderer>().sharedMaterial.name,
                    Is.EqualTo("BrushedMetal"));
            }

            Renderer front = transforms.Single(item =>
                item.name == "Acrylic_FrontPlate").GetComponent<Renderer>();
            Renderer rear = transforms.Single(item =>
                item.name == "Acrylic_RearPlate").GetComponent<Renderer>();
            Assert.That(front.bounds.center.z, Is.LessThan(rear.bounds.center.z),
                "FBX depth must face the shipping camera; rear plate cannot occlude content.");
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
            StringAssert.Contains(
                "receipt-prize-not-canonical-toy",
                coordinator);
            StringAssert.Contains(
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
        public void ThreeBladePrize_MapsSpinnerPlaneToDisplayCaseFace()
        {
            PremiumDisplayCaseContentOptions options =
                ThreeBladeDisplayPrizeFactory.ContentOptions;

            Assert.That(options.InitialEulerAngles.x,
                Is.EqualTo(90f).Within(0.0001f));
            Assert.That(options.InitialEulerAngles.y,
                Is.EqualTo(-18f).Within(0.0001f));
            Assert.That(options.IdleRotationEnabled, Is.True);
            Assert.That(options.IdleRotationPeriodSeconds,
                Is.EqualTo(4f).Within(0.0001f));
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

    }
}
