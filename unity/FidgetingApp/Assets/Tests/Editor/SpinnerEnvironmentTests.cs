using System.Collections.Generic;
using System.IO;
using System.Linq;
using CodexUnityLab;
using FidgetingApp.EDC;
using FidgetingApp.Editor;
using FidgetingApp.Product;
using NUnit.Framework;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace FidgetingApp.Tests.Editor
{
    public sealed class SpinnerEnvironmentTests
    {
        [SetUp]
        public void ResetEnvironmentThemePreference()
        {
            PlayerPrefs.DeleteKey(SpinnerEnvironmentThemeCatalog.PreferenceKey);
        }

        [TearDown]
        public void ClearEnvironmentThemePreference()
        {
            PlayerPrefs.DeleteKey(SpinnerEnvironmentThemeCatalog.PreferenceKey);
        }

        [Test]
        public void LibrarySwipeSessionGateCommitsCancelsAndRejectsStaleEnds()
        {
            var gate = new LibrarySwipeSessionGate();

            Assert.That(gate.Begin(1001), Is.True);
            Assert.That(gate.Accepts(1001), Is.True);
            Assert.That(gate.Commit(1001), Is.True);
            Assert.That(
                gate.End(1001),
                Is.EqualTo(LibrarySwipeEndDisposition.Committed),
                "A committed page must not spring back before its scene exit.");

            Assert.That(gate.Begin(1002), Is.True);
            Assert.That(
                gate.End(1001),
                Is.EqualTo(LibrarySwipeEndDisposition.Ignored),
                "A stale End must not disturb the active swipe session.");
            Assert.That(gate.Accepts(1002), Is.True);
            Assert.That(
                gate.End(1002),
                Is.EqualTo(LibrarySwipeEndDisposition.Rebound),
                "Only a current uncommitted edge or cancelled drag rebounds.");

            Assert.That(gate.Begin(1001), Is.False);
            Assert.That(gate.Accepts(1001), Is.False);
        }

        [Test]
        public void EnvironmentThemeCatalogDefinesCanyonAndCyberpunkWithoutResampling()
        {
            IReadOnlyList<SpinnerEnvironmentThemeProfile> themes =
                SpinnerEnvironmentThemeCatalog.Profiles;

            Assert.That(themes.Count, Is.EqualTo(4));
            Assert.That(themes[0].Id, Is.EqualTo(SpinnerEnvironmentThemeCatalog.AdaptiveId));
            Assert.That(themes[0].DisplayName, Is.EqualTo("随形微光"));
            Assert.That(themes[0].ModelReactiveBackdrop, Is.True);
            Assert.That(themes[1].Id, Is.EqualTo(SpinnerEnvironmentThemeCatalog.CanyonId));
            Assert.That(themes[1].DisplayName, Is.EqualTo("星岩峡谷"));
            Assert.That(themes[1].HasForegroundLayers, Is.True);
            Assert.That(themes[2].Id, Is.EqualTo(SpinnerEnvironmentThemeCatalog.CyberpunkId));
            Assert.That(themes[2].DisplayName, Is.EqualTo("霓虹都市"));
            Assert.That(themes[2].LayeredMidground, Is.True);
            Assert.That(themes[2].DynamicStarfield, Is.True);
            Assert.That(themes[2].HasForegroundLayers, Is.False);
            Assert.That(themes[3].Id, Is.EqualTo(SpinnerEnvironmentThemeCatalog.MineralRidgeId));
            Assert.That(
                SpinnerEnvironmentThemeCatalog.NormalizeId("CYBERPUNK"),
                Is.EqualTo(SpinnerEnvironmentThemeCatalog.CyberpunkId));
            Assert.That(
                SpinnerEnvironmentThemeCatalog.NormalizeId("unknown"),
                Is.EqualTo(SpinnerEnvironmentThemeCatalog.AdaptiveId));

            const string cyberAssetPath =
                "Assets/Resources/EnvironmentBackgrounds/"
                + "cyber-neon-parallax-depth-v13.png";
            Assert.That(File.Exists(cyberAssetPath), Is.True);
            Texture2D texture = Resources.Load<Texture2D>(
                SpinnerEnvironmentThemeCatalog.CyberpunkBackgroundResourcePath);
            Assert.That(texture, Is.Not.Null);
            Assert.That(texture.width, Is.EqualTo(941));
            Assert.That(texture.height, Is.EqualTo(1672));

            TextureImporter importer = AssetImporter.GetAtPath(cyberAssetPath)
                as TextureImporter;
            Assert.That(importer, Is.Not.Null);
            Assert.That(importer.sRGBTexture, Is.True);
            Assert.That(importer.isReadable, Is.False);
            Assert.That(importer.mipmapEnabled, Is.False);
            Assert.That(importer.npotScale, Is.EqualTo(TextureImporterNPOTScale.None));
            Assert.That(importer.wrapMode, Is.EqualTo(TextureWrapMode.Clamp));
            TextureImporterPlatformSettings ios =
                importer.GetPlatformTextureSettings("iPhone");
            Assert.That(ios.overridden, Is.True);
            Assert.That(ios.maxTextureSize, Is.EqualTo(4096));
            Assert.That(ios.format, Is.EqualTo(TextureImporterFormat.ASTC_8x8));
        }

        [Test]
        public void PresenterSwitchesThemesWithoutTouchingTheModelMechanism()
        {
            SpinnerEnvironmentProfile profile = SpinnerEnvironmentCatalog.Profiles[1];
            EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
            Rigidbody[] bodies = Object.FindObjectsByType<Rigidbody>();
            Vector3[] angularVelocities = bodies
                .Select(body => body.angularVelocity)
                .ToArray();
            SpinnerEnvironmentPresenter presenter =
                SpinnerEnvironmentPresenter.Install(profile.ScenePath);

            Assert.That(
                presenter.ApplyTheme(SpinnerEnvironmentThemeCatalog.CyberpunkId),
                Is.True);
            Assert.That(
                presenter.CurrentThemeId,
                Is.EqualTo(SpinnerEnvironmentThemeCatalog.CyberpunkId));
            Assert.That(
                presenter.BackgroundTexture.name,
                Is.EqualTo("cyber-neon-parallax-depth-v13"));
            Assert.That(presenter.MidgroundRenderer.gameObject.activeSelf, Is.True);
            Assert.That(presenter.DeepStarfieldRenderer.gameObject.activeSelf, Is.True);
            Assert.That(presenter.NearStarfieldRenderer.gameObject.activeSelf, Is.True);
            Assert.That(presenter.RightForegroundRenderer.gameObject.activeSelf, Is.False);
            Assert.That(presenter.LeftForegroundRenderer.gameObject.activeSelf, Is.False);
            Assert.That(presenter.ImageBasedLighting.GeneratedReflection, Is.Not.Null);

            Assert.That(
                presenter.ApplyTheme(SpinnerEnvironmentThemeCatalog.CanyonId),
                Is.True);
            Assert.That(
                presenter.CurrentThemeId,
                Is.EqualTo(SpinnerEnvironmentThemeCatalog.CanyonId));
            Assert.That(presenter.MidgroundRenderer.gameObject.activeSelf, Is.False);
            Assert.That(presenter.RightForegroundRenderer.gameObject.activeSelf, Is.True);
            Assert.That(presenter.LeftForegroundRenderer.gameObject.activeSelf, Is.True);

            for (int index = 0; index < bodies.Length; index++)
            {
                Assert.That(
                    bodies[index].angularVelocity,
                    Is.EqualTo(angularVelocities[index]),
                    $"Theme switching must not inject motion into {bodies[index].name}.");
            }
        }

        [Test]
        public void CatalogMapsTheApprovedUnifiedCanyonBackgroundToAllProductScenes()
        {
            IReadOnlyList<SpinnerEnvironmentProfile> profiles =
                SpinnerEnvironmentCatalog.Profiles;

            Assert.That(profiles.Count, Is.EqualTo(6));
            string[] enabledScenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray();
            CollectionAssert.AreEqual(
                ProductCatalog.ShippingScenePaths(),
                enabledScenes,
                "Release build settings must exactly match the approved product catalog.");
            CollectionAssert.IsSubsetOf(
                enabledScenes,
                profiles.Select(profile => profile.ScenePath).ToArray(),
                "Every shipping product must retain an authored environment profile.");
            Assert.That(
                profiles.Select(profile => profile.ModelId).Distinct().Count(),
                Is.EqualTo(6));
            Assert.That(
                profiles.Select(profile => profile.BackgroundResourcePath).Distinct().Count(),
                Is.EqualTo(1));
            Assert.That(
                Directory.GetFiles(
                        "Assets/Resources/EnvironmentBackgrounds",
                        "*-v3-*.png")
                    .Concat(Directory.GetFiles(
                        "Assets/Resources/EnvironmentBackgrounds",
                        "*-v4-*.png")),
                Is.Empty,
                "Superseded plates must stay outside Resources and the iOS bundle.");

            foreach (SpinnerEnvironmentProfile profile in profiles)
            {
                Assert.That(File.Exists(profile.TextureAssetPath), Is.True, profile.ModelId);
                Assert.That(
                    profile.BackgroundResourcePath,
                    Is.EqualTo(SpinnerEnvironmentCatalog.UnifiedBackgroundResourcePath));
                StringAssert.EndsWith(
                    "canyon-unified-ledgestone-v1-2x.png",
                    profile.TextureAssetPath);
                Assert.That(profile.SourceWidth, Is.EqualTo(1882));
                Assert.That(profile.SourceHeight, Is.EqualTo(3344));
                Assert.That(profile.ImportMaxTextureSize, Is.EqualTo(4096));
                Assert.That(profile.CoverOverscan, Is.EqualTo(1.08f));
                Assert.That(profile.Saturation, Is.EqualTo(0.68f));
                Assert.That(profile.LayeredParallax, Is.False);
                Assert.That(profile.UsesBakedSupportSurface, Is.True);
                Assert.That(profile.LibraryLightScale, Is.InRange(0.20f, 1.00f));
                Assert.That(profile.LibraryReflectionScale, Is.InRange(0.25f, 1.00f));
                Assert.That(profile.StageScale, Is.InRange(1.30f, 1.45f));
                Assert.That(profile.StageThicknessRatio, Is.InRange(0.06f, 0.13f));

                Texture2D texture = Resources.Load<Texture2D>(
                    profile.BackgroundResourcePath);
                Assert.That(texture, Is.Not.Null, profile.ModelId);
                Assert.That(texture.width, Is.EqualTo(profile.SourceWidth));
                Assert.That(texture.height, Is.EqualTo(profile.SourceHeight));

                TextureImporter importer =
                    AssetImporter.GetAtPath(profile.TextureAssetPath) as TextureImporter;
                Assert.That(importer, Is.Not.Null);
                Assert.That(importer.sRGBTexture, Is.True);
                Assert.That(importer.isReadable, Is.False);
                Assert.That(importer.mipmapEnabled, Is.False);
                Assert.That(importer.wrapMode, Is.EqualTo(TextureWrapMode.Clamp));
                Assert.That(importer.npotScale, Is.EqualTo(TextureImporterNPOTScale.None));
                Assert.That(importer.maxTextureSize, Is.EqualTo(profile.ImportMaxTextureSize));

                TextureImporterPlatformSettings ios =
                    importer.GetPlatformTextureSettings("iPhone");
                Assert.That(ios.overridden, Is.True);
                Assert.That(ios.maxTextureSize, Is.EqualTo(profile.ImportMaxTextureSize));
                Assert.That(ios.format, Is.EqualTo(TextureImporterFormat.ASTC_8x8));
                Assert.That(profile.Lights.Count, Is.GreaterThanOrEqualTo(1));
                Assert.That(
                    profile.Lights.All(light =>
                        !string.IsNullOrEmpty(light.ObjectName) && light.Intensity > 0f),
                    Is.True);
            }

            Material material = Resources.Load<Material>(
                SpinnerEnvironmentCatalog.MaterialResourcePath);
            Assert.That(material, Is.Not.Null);
            Assert.That(material.shader.name, Is.EqualTo("Universal Render Pipeline/Unlit"));
            Assert.That(material.renderQueue, Is.EqualTo(2000));
            Assert.That(material.GetFloat("_ZWrite"), Is.EqualTo(1f));
            Assert.That(material.GetFloat("_Cull"), Is.EqualTo(0f));
            Assert.That(File.Exists(SpinnerEnvironmentAssetBuilder.MaterialAssetPath), Is.True);

            Material parallaxMaterial = Resources.Load<Material>(
                SpinnerEnvironmentCatalog.ParallaxMaterialResourcePath);
            Assert.That(parallaxMaterial, Is.Not.Null);
            Assert.That(
                parallaxMaterial.shader.name,
                Is.EqualTo(SpinnerEnvironmentAssetBuilder.ParallaxShaderName));
            Assert.That(parallaxMaterial.renderQueue, Is.EqualTo(2000));
            Assert.That(parallaxMaterial.GetFloat("_ZWrite"), Is.EqualTo(1f));
            Assert.That(
                File.Exists(SpinnerEnvironmentAssetBuilder.ParallaxMaterialAssetPath),
                Is.True);

            Material starfieldMaterial = Resources.Load<Material>(
                SpinnerEnvironmentCatalog.StarfieldMaterialResourcePath);
            Assert.That(starfieldMaterial, Is.Not.Null,
                "The Resources material must retain the procedural star shader in iOS builds.");
            Assert.That(
                starfieldMaterial.shader.name,
                Is.EqualTo(SpinnerEnvironmentAssetBuilder.StarfieldShaderName));
            Assert.That(
                File.Exists(SpinnerEnvironmentAssetBuilder.StarfieldMaterialAssetPath),
                Is.True);
            string starfieldShader = File.ReadAllText(
                "Assets/Shaders/EnvironmentStarfield.shader");
            StringAssert.Contains("_Time.y * twinkleRate", starfieldShader);
            StringAssert.Contains("twinklePhase", starfieldShader);

            foreach (string foregroundPath in new[]
                     {
                         SpinnerEnvironmentAssetBuilder.LeftForegroundAssetPath,
                         SpinnerEnvironmentAssetBuilder.RightForegroundAssetPath
                     })
            {
                Assert.That(File.Exists(foregroundPath), Is.True, foregroundPath);
                Texture2D foreground = AssetDatabase.LoadAssetAtPath<Texture2D>(foregroundPath);
                Assert.That(foreground, Is.Not.Null, foregroundPath);
                Assert.That(foreground.width, Is.EqualTo(1882), foregroundPath);
                Assert.That(foreground.height, Is.EqualTo(3344), foregroundPath);

                TextureImporter foregroundImporter =
                    AssetImporter.GetAtPath(foregroundPath) as TextureImporter;
                Assert.That(foregroundImporter, Is.Not.Null);
                Assert.That(foregroundImporter.alphaSource,
                    Is.EqualTo(TextureImporterAlphaSource.FromInput));
                Assert.That(foregroundImporter.alphaIsTransparency, Is.True);
                Assert.That(foregroundImporter.isReadable, Is.False);
                Assert.That(foregroundImporter.mipmapEnabled, Is.False);
                Assert.That(foregroundImporter.wrapMode, Is.EqualTo(TextureWrapMode.Clamp));
                TextureImporterPlatformSettings foregroundIos =
                    foregroundImporter.GetPlatformTextureSettings("iPhone");
                Assert.That(foregroundIos.overridden, Is.True);
                Assert.That(foregroundIos.maxTextureSize, Is.EqualTo(4096));
                Assert.That(foregroundIos.format, Is.EqualTo(TextureImporterFormat.ASTC_6x6));
            }
        }

        [Test]
        public void EveryProductSceneInstallsItsBackgroundAndHarmonizedModelLights()
        {
            foreach (SpinnerEnvironmentProfile profile in SpinnerEnvironmentCatalog.Profiles)
            {
                EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
                Rigidbody[] bodies = Object.FindObjectsByType<Rigidbody>();
                Vector3[] previousAngularVelocities =
                    bodies.Select(body => body.angularVelocity).ToArray();
                Camera sceneCamera = Camera.main ?? Object.FindAnyObjectByType<Camera>();
                Matrix4x4 projectionBeforeInstall = sceneCamera.projectionMatrix;

                SpinnerEnvironmentPresenter presenter =
                    SpinnerEnvironmentPresenter.Install(profile.ScenePath);
                bool softSpinnerLighting = SpinnerImageBasedLightingController
                    .UsesSoftSpinnerLighting(profile.ModelId);
                float softSpinnerLightTrim = SpinnerImageBasedLightingController
                    .ResolveSoftSpinnerLightTrim(profile.ModelId);
                float ambientScale = softSpinnerLighting
                    ? SpinnerImageBasedLightingController.SoftAmbientScale
                        * softSpinnerLightTrim
                    : 1f;
                float directScale = softSpinnerLighting
                    ? SpinnerImageBasedLightingController.SoftDirectLightScale
                        * softSpinnerLightTrim
                    : 1f;
                float reflectionScale = softSpinnerLighting
                    ? SpinnerImageBasedLightingController
                        .SoftReflectionIntensityScale * softSpinnerLightTrim
                    : 1f;

                Assert.That(presenter, Is.Not.Null, profile.ModelId);
                Assert.That(presenter.BackgroundTexture, Is.Not.Null);
                Assert.That(
                    presenter.BackgroundTexture.name,
                    Is.EqualTo(Path.GetFileNameWithoutExtension(profile.TextureAssetPath))
                        .Or.EqualTo("adaptive-dark-neutral-runtime"),
                    profile.ModelId);
                Assert.That(presenter.BackgroundRenderer, Is.Not.Null);
                Assert.That(presenter.ParallaxController, Is.Not.Null);
                Assert.That(
                    sceneCamera.projectionMatrix,
                    Is.EqualTo(projectionBeforeInstall),
                    "Installing parallax must preserve the authored static projection.");
                Assert.That(
                    presenter.BackgroundRenderer.name,
                    Is.EqualTo(SpinnerEnvironmentPresenter.BackgroundObjectName));
                Assert.That(
                    presenter.BackgroundRenderer.transform.parent,
                    Is.EqualTo(presenter.transform));
                Assert.That(
                    presenter.BackgroundRenderer.GetComponent<Collider>(),
                    Is.Null);
                Assert.That(
                    presenter.BackgroundRenderer.GetComponent<Rigidbody>(),
                    Is.Null);
                Assert.That(presenter.BackgroundRenderer.receiveShadows, Is.False);
                Assert.That(
                    presenter.BackgroundRenderer.shadowCastingMode,
                    Is.EqualTo(UnityEngine.Rendering.ShadowCastingMode.Off));
                Assert.That(
                    presenter.BackgroundRenderer.transform.localPosition.z,
                    Is.GreaterThan(presenter.GetComponent<Camera>().nearClipPlane));
                Assert.That(
                    presenter.BackgroundRenderer.transform.localScale.x,
                    Is.GreaterThan(0f));
                Assert.That(
                    presenter.BackgroundRenderer.transform.localScale.y,
                    Is.GreaterThan(0f));
                AssertBackgroundCoversViewport(
                    presenter.GetComponent<Camera>(),
                    presenter.BackgroundRenderer.transform,
                    profile.ModelId);

                var backgroundProperties = new MaterialPropertyBlock();
                presenter.BackgroundRenderer.GetPropertyBlock(backgroundProperties);
                float expectedSaturation =
                    SpinnerEnvironmentThemeCatalog.Default.ModelReactiveBackdrop
                        ? 0f
                        : profile.Saturation;
                Assert.That(
                    backgroundProperties.GetFloat("_Saturation"),
                    Is.EqualTo(expectedSaturation).Within(0.0001f),
                    profile.ModelId);
                Assert.That(
                    backgroundProperties.GetFloat("_GlowEnabled"),
                    Is.EqualTo(1f));
                Assert.That(
                    backgroundProperties.GetFloat("_GlowIntensity"),
                    Is.EqualTo(0.42f).Within(0.0001f)
                        .Or.EqualTo(0.26f).Within(0.0001f),
                    profile.ModelId);
                Assert.That(
                    backgroundProperties.GetFloat("_ShadowEnabled"),
                    Is.EqualTo(1f));
                Assert.That(
                    backgroundProperties.GetFloat("_ShadowStrength"),
                    Is.EqualTo(0.88f).Within(0.0001f)
                        .Or.EqualTo(
                            SpinnerImageBasedLightingController
                                .FanCardContactShadowStrength)
                            .Within(0.0001f),
                    "The baked ledge must visibly receive the model contact shadow.");
                Assert.That(
                    backgroundProperties.GetVector("_GlowScaleB").y,
                    Is.EqualTo(2.8f).Within(0.0001f),
                    "The lower response must be a compressed contact-light pool on the baked ledge.");

                Assert.That(
                    presenter.MidgroundRenderer == null
                    || !presenter.MidgroundRenderer.gameObject.activeSelf,
                    Is.True,
                    "The baked platform copy must not remain as a fake midground layer.");

                MeshRenderer[] depthRenderers =
                {
                    presenter.DeepStarfieldRenderer,
                    presenter.NearStarfieldRenderer,
                    presenter.RightForegroundRenderer,
                    presenter.LeftForegroundRenderer
                };
                Assert.That(depthRenderers.All(renderer => renderer != null), Is.True);
                Assert.That(depthRenderers.All(renderer => renderer.gameObject.activeSelf), Is.True);
                Assert.That(depthRenderers.All(renderer =>
                    renderer.GetComponent<Collider>() == null
                    && renderer.GetComponent<Rigidbody>() == null), Is.True);
                Assert.That(
                    presenter.DeepStarfieldRenderer.sharedMaterial.shader.name,
                    Is.EqualTo("FidgetingApp/EnvironmentStarfield"));
                Assert.That(
                    presenter.NearStarfieldRenderer.sharedMaterial.shader.name,
                    Is.EqualTo("FidgetingApp/EnvironmentStarfield"));
                Assert.That(
                    presenter.RightForegroundRenderer.sharedMaterial.renderQueue,
                    Is.GreaterThanOrEqualTo(3000));
                Assert.That(
                    presenter.LeftForegroundRenderer.sharedMaterial.renderQueue,
                    Is.GreaterThanOrEqualTo(3000));
                Assert.That(
                    presenter.RightForegroundRenderer.sharedMaterial.GetFloat("_ZWrite"),
                    Is.EqualTo(0f));
                Assert.That(
                    presenter.LeftForegroundRenderer.sharedMaterial.GetFloat("_ZWrite"),
                    Is.EqualTo(0f));

                var rightForegroundProperties = new MaterialPropertyBlock();
                presenter.RightForegroundRenderer.GetPropertyBlock(
                    rightForegroundProperties);
                Assert.That(
                    rightForegroundProperties.GetTexture("_BaseMap"),
                    Is.Not.Null);
                Assert.That(
                    rightForegroundProperties.GetFloat("_GlowEnabled"),
                    Is.EqualTo(1f));
                Assert.That(
                    rightForegroundProperties.GetFloat("_GlowIntensity"),
                    Is.EqualTo(0.32f).Within(0.0001f));

                Camera camera = presenter.GetComponent<Camera>();
                float previousAspect = camera.aspect;
                foreach (float aspect in new[] { 9f / 21f, 9f / 16f, 3f / 4f, 1f })
                {
                    camera.aspect = aspect;
                    presenter.RefreshLayout();
                    AssertBackgroundCoversViewport(
                        camera,
                        presenter.BackgroundRenderer.transform,
                        $"{profile.ModelId}/{aspect:0.000}",
                        0.03f);
                    Assert.That(
                        presenter.BackgroundRenderer.transform.localScale.x
                        / presenter.BackgroundRenderer.transform.localScale.y,
                        Is.EqualTo((float)profile.SourceWidth / profile.SourceHeight)
                            .Within(0.0001f));
                }
                camera.aspect = previousAspect;
                presenter.RefreshLayout();

                Matrix4x4 neutralProjection = camera.projectionMatrix;
                camera.projectionMatrix = SpinnerSceneParallaxController.OffsetProjection(
                    neutralProjection,
                    camera.orthographic,
                    new Vector2(
                        SpinnerSceneParallaxController.ForegroundPixels,
                        -SpinnerSceneParallaxController.ForegroundPixels),
                    new Vector2(900f, 1600f));
                presenter.RefreshLayout();
                presenter.SetParallaxTilt(
                    new Vector2(1f, -1f).normalized,
                    SpinnerSceneParallaxController.FarLayerPixels,
                    SpinnerSceneParallaxController.MidLayerPixels);
                AssertBackgroundCoversViewport(
                    camera,
                    presenter.BackgroundRenderer.transform,
                    $"{profile.ModelId}/maximum-parallax");
                camera.projectionMatrix = neutralProjection;
                presenter.RefreshLayout();

                Vector3 farStart = presenter.BackgroundRenderer.transform.localPosition;
                presenter.SetParallaxTilt(
                    Vector2.right,
                    SpinnerSceneParallaxController.FarLayerPixels,
                    SpinnerSceneParallaxController.MidLayerPixels);
                float farTravel = Mathf.Abs(
                    presenter.BackgroundRenderer.transform.localPosition.x - farStart.x);
                Assert.That(farTravel, Is.GreaterThan(0f));
                presenter.SetParallaxTilt(Vector2.zero, 0f, 0f);

                Assert.That(presenter.GroundingStage, Is.Not.Null, profile.ModelId);
                Assert.That(presenter.GroundingStage.StageRenderer, Is.Not.Null);
                Assert.That(
                    presenter.GroundingStage.StageRenderer.enabled,
                    Is.False,
                    "The approved plate already owns the ledge; a second procedural slab must never render.");
                Assert.That(presenter.GroundingStage.SupportRenderer.enabled, Is.False);
                Assert.That(
                    presenter.GroundingStage.name,
                    Is.EqualTo(SpinnerGroundingStage.ObjectName));
                Assert.That(
                    presenter.GroundingStage.GetComponent<Collider>(),
                    Is.Null,
                    "The visual stage must not enter model physics.");
                Assert.That(presenter.GroundingStage.GetComponent<Rigidbody>(), Is.Null);
                Assert.That(presenter.GroundingStage.StageRenderer.receiveShadows, Is.True);
                Assert.That(presenter.GroundingStage.SupportRenderer, Is.Not.Null);
                Assert.That(
                    presenter.GroundingStage.SupportRenderer.receiveShadows,
                    Is.True);
                Assert.That(
                    presenter.GroundingStage.StageRenderer.sharedMaterial.GetFloat("_Metallic"),
                    Is.EqualTo(0f));
                Assert.That(
                    presenter.GroundingStage.StageRenderer.sharedMaterial.GetFloat("_Smoothness"),
                    Is.LessThanOrEqualTo(0.03f));
                Assert.That(
                    presenter.GroundingStage.StageRenderer.sharedMaterial.GetTexture("_BaseMap"),
                    Is.EqualTo(presenter.GroundingStage.SupportRenderer.sharedMaterial
                        .GetTexture("_BaseMap")),
                    "The shelf and center support must read as one continuous canyon material.");
                Assert.That(
                    presenter.GroundingStage.SupportRenderer.GetComponent<Collider>(),
                    Is.Null,
                    "The center support is visual-only and must not alter rotor physics.");
                Assert.That(
                    presenter.GroundingStage.SupportRenderer.GetComponent<Rigidbody>(),
                    Is.Null);
                Assert.That(
                    presenter.GroundingStage.TopY,
                    Is.LessThan(presenter.GroundingStage.ModelBounds.min.y));
                Assert.That(
                    presenter.GroundingStage.SupportTopY,
                    Is.GreaterThan(presenter.GroundingStage.TopY));
                Assert.That(
                    presenter.GroundingStage.SupportTopY,
                    Is.LessThan(presenter.GroundingStage.ModelBounds.min.y));
                Assert.That(
                    presenter.GroundingStage.ModelBounds.min.y
                    - presenter.GroundingStage.SupportTopY,
                    Is.LessThan(Mathf.Max(
                        presenter.GroundingStage.ModelBounds.size.x,
                        presenter.GroundingStage.ModelBounds.size.z) * 0.02f));
                Assert.That(
                    presenter.GroundingStage.SupportRenderer.transform.position.x,
                    Is.EqualTo(presenter.GroundingStage.ModelBounds.center.x)
                        .Within(0.001f));
                Assert.That(
                    presenter.GroundingStage.SupportRenderer.transform.position.z,
                    Is.EqualTo(presenter.GroundingStage.ModelBounds.center.z)
                        .Within(0.001f));
                Assert.That(
                    Vector2.Distance(
                        new Vector2(
                            presenter.GroundingStage.StageRenderer.bounds.center.x,
                            presenter.GroundingStage.StageRenderer.bounds.center.z),
                        new Vector2(
                            presenter.GroundingStage.ModelBounds.center.x,
                            presenter.GroundingStage.ModelBounds.center.z)),
                    Is.GreaterThan(0f),
                    "The slab must extend toward the viewer instead of reading as a centered midground pad.");

                Assert.That(presenter.ImageBasedLighting, Is.Not.Null);
                Assert.That(presenter.ImageBasedLighting.SoftSpinnerLightingActive,
                    Is.EqualTo(softSpinnerLighting));
                Assert.That(presenter.ImageBasedLighting.GeneratedReflection, Is.Not.Null);
                Assert.That(
                    RenderSettings.customReflectionTexture,
                    Is.EqualTo(presenter.ImageBasedLighting.GeneratedReflection));
                Assert.That(presenter.ImageBasedLighting.ModelBounceLight, Is.Not.Null);
                Assert.That(
                    presenter.ImageBasedLighting.ModelBounceLight.name,
                    Is.EqualTo(SpinnerImageBasedLightingController.BounceLightName));
                Assert.That(presenter.ImageBasedLighting.VisibilityFillLight, Is.Not.Null);
                Assert.That(
                    presenter.ImageBasedLighting.VisibilityFillLight.name,
                    Is.EqualTo(SpinnerImageBasedLightingController.VisibilityFillName));
                Assert.That(
                    presenter.ImageBasedLighting.VisibilityFillLight.type,
                    Is.EqualTo(LightType.Directional));
                Assert.That(
                    presenter.ImageBasedLighting.VisibilityFillLight.shadows,
                    Is.EqualTo(LightShadows.None));
                Assert.That(presenter.ImageBasedLighting.ViewHighlightLight, Is.Not.Null);
                Assert.That(
                    presenter.ImageBasedLighting.ViewHighlightLight.name,
                    Is.EqualTo(SpinnerImageBasedLightingController.ViewHighlightName));
                Assert.That(
                    presenter.ImageBasedLighting.ViewHighlightLight.shadows,
                    Is.EqualTo(LightShadows.None));
                Assert.That(
                    presenter.GroundingStage.ModelRenderers.All(renderer =>
                        renderer.reflectionProbeUsage
                        == UnityEngine.Rendering.ReflectionProbeUsage.BlendProbes),
                    Is.True);

                if (!string.IsNullOrEmpty(profile.LegacyBackdropObjectName))
                {
                    Transform legacyBackdrop = Object
                        .FindObjectsByType<Transform>(
                            FindObjectsInactive.Include,
                            FindObjectsSortMode.None)
                        .Single(transform =>
                            transform.gameObject.scene.IsValid()
                            && transform.name == profile.LegacyBackdropObjectName);
                    Assert.That(legacyBackdrop.gameObject.activeSelf, Is.False);
                }

                presenter.SetExperienceTint(new Color(0.12f, 0.03f, 0.08f, 1f));
                var properties = new MaterialPropertyBlock();
                presenter.BackgroundRenderer.GetPropertyBlock(properties);
                Color experienceTint = properties.GetColor("_BaseColor");
                Assert.That(experienceTint.r, Is.EqualTo(1f).Within(0.0001f));
                Assert.That(experienceTint.g, Is.LessThan(experienceTint.r));
                Assert.That(experienceTint.b, Is.LessThan(experienceTint.r));
                Assert.That(
                    properties.GetTexture("_BaseMap"),
                    Is.EqualTo(presenter.BackgroundTexture));

                bool geeoneRecipe = SpinnerImageBasedLightingController
                    .UsesGeeonePresentationRecipe(profile.ModelId);
                SpinnerEnvironmentPalette palette =
                    presenter.ImageBasedLighting.CurrentPalette;
                AssertColor(
                    RenderSettings.ambientSkyColor,
                    ExpectedAmbient(
                        palette.Sky * ambientScale,
                        geeoneRecipe,
                        SpinnerImageBasedLightingController.GeeoneAmbientFloorSky));
                AssertColor(
                    RenderSettings.ambientEquatorColor,
                    ExpectedAmbient(
                        palette.Equator * ambientScale,
                        geeoneRecipe,
                        SpinnerImageBasedLightingController.GeeoneAmbientFloorEquator));
                AssertColor(
                    RenderSettings.ambientGroundColor,
                    ExpectedAmbient(
                        palette.Ground * ambientScale,
                        geeoneRecipe,
                        SpinnerImageBasedLightingController.GeeoneAmbientFloorGround));
                float geeoneReflectionBoost = geeoneRecipe
                    ? SpinnerImageBasedLightingController.GeeoneReflectionBoost
                    : 1f;
                float geeoneLightBoost = geeoneRecipe
                    ? SpinnerImageBasedLightingController.GeeoneDirectLightBoost
                    : 1f;
                if (geeoneRecipe)
                {
                    // 2026-09-08 "内外一定要一致": GEEONE must not dim in the library.
                    Assert.That(profile.LibraryLightScale, Is.EqualTo(1f));
                    Assert.That(profile.LibraryReflectionScale, Is.EqualTo(1f));
                }
                Assert.That(
                    RenderSettings.reflectionIntensity,
                    Is.EqualTo(profile.ReflectionIntensity
                        * reflectionScale
                        * profile.LibraryReflectionScale
                        * geeoneReflectionBoost)
                        .Within(0.0001f));

                Light[] lights = Object.FindObjectsByType<Light>();
                foreach (SpinnerEnvironmentLightPreset expected in profile.Lights)
                {
                    Light actual = lights.SingleOrDefault(light =>
                        light.name == expected.ObjectName);
                    Assert.That(actual, Is.Not.Null, $"{profile.ModelId}/{expected.ObjectName}");
                    Assert.That(
                        actual.intensity,
                        Is.EqualTo(SpinnerImageBasedLightingController
                            .ResolveAuthoredLightIntensity(
                                profile.ModelId,
                                expected.ObjectName,
                                expected.Intensity * directScale,
                                profile.LibraryLightScale * geeoneLightBoost))
                            .Within(0.0001f));
                    Assert.That(actual.useColorTemperature, Is.False);
                    Color.RGBToHSV(actual.color, out _, out float saturation, out _);
                    Assert.That(saturation, Is.LessThanOrEqualTo(0.43f));
                }

                for (int index = 0; index < bodies.Length; index++)
                {
                    Assert.That(
                        bodies[index].angularVelocity,
                        Is.EqualTo(previousAngularVelocities[index]),
                        $"Environment setup must not inject spin into {bodies[index].name}.");
                }

                Color librarySky = RenderSettings.ambientSkyColor;
                presenter.SetLibraryPreviewActive(false, true);
                Assert.That(presenter.GroundingStage.StageRenderer.enabled, Is.False);
                Assert.That(presenter.GroundingStage.SupportRenderer.enabled, Is.False);
                Assert.That(
                    RenderSettings.reflectionIntensity,
                    Is.EqualTo(profile.ReflectionIntensity
                        * reflectionScale
                        * geeoneReflectionBoost)
                        .Within(0.0001f));
                foreach (SpinnerEnvironmentLightPreset expected in profile.Lights)
                {
                    Light restored = Object.FindObjectsByType<Light>()
                        .Single(light => light.name == expected.ObjectName);
                    Assert.That(
                        restored.intensity,
                        Is.EqualTo(SpinnerImageBasedLightingController
                            .ResolveAuthoredLightIntensity(
                                profile.ModelId,
                                expected.ObjectName,
                                expected.Intensity * directScale,
                                geeoneLightBoost))
                            .Within(0.0001f));
                }
                if (geeoneRecipe)
                {
                    AssertColor(RenderSettings.ambientSkyColor, librarySky);
                    Assert.That(
                        presenter.ImageBasedLighting.ResolvePresentationState(true).LightScale,
                        Is.EqualTo(presenter.ImageBasedLighting
                            .ResolvePresentationState(false).LightScale)
                            .Within(0.0001f),
                        "GEEONE library and detail must light identically.");
                }
                presenter.SetLibraryPreviewActive(true, true);
                Assert.That(presenter.GroundingStage.StageRenderer.enabled, Is.False);
                Assert.That(presenter.GroundingStage.SupportRenderer.enabled, Is.False);
                Assert.That(
                    RenderSettings.reflectionIntensity,
                    Is.EqualTo(profile.ReflectionIntensity
                        * reflectionScale
                        * profile.LibraryReflectionScale
                        * geeoneReflectionBoost)
                        .Within(0.0001f));
            }
        }

        private static Color ExpectedAmbient(Color scaled, bool geeoneRecipe, Color floor)
        {
            if (!geeoneRecipe)
            {
                return scaled;
            }

            Color boosted = scaled * SpinnerImageBasedLightingController.GeeoneAmbientBoost;
            floor = GeeoneLightingPresetCatalog.ScaleFloor(
                floor,
                SpinnerImageBasedLightingController.GeeoneAmbientFloorScale);
            return new Color(
                Mathf.Max(boosted.r, floor.r),
                Mathf.Max(boosted.g, floor.g),
                Mathf.Max(boosted.b, floor.b),
                1f);
        }

        [Test]
        public void GeeoneLightingPresets_ShipSoftStudioAndKeepStudioBrightOnlyForReview()
        {
            GeeoneLightingPresetCatalog.ResetActive();
            GeeoneLightingPreset shipping = GeeoneLightingPresetCatalog.Active;

            // User 2026-09-09 "我感觉柔光棚好看一点" after the mobile HDR switch.
            Assert.That(shipping.Id, Is.EqualTo(GeeoneLightingPresetCatalog.ShippingId));
            Assert.That(shipping.Id, Is.EqualTo(GeeoneLightingPresetCatalog.SoftStudioId));
            Assert.That(
                shipping.StudioSoftboxIntensity,
                Is.EqualTo(SpinnerImageBasedLightingController.GeeoneStudioSoftboxIntensity));
            Assert.That(
                shipping.AmbientFloorScale,
                Is.EqualTo(SpinnerImageBasedLightingController.GeeoneAmbientFloorScale));
            Assert.That(
                shipping.DirectLightBoost,
                Is.EqualTo(SpinnerImageBasedLightingController.GeeoneDirectLightBoost));
            Assert.That(
                shipping.ReflectionBoost,
                Is.EqualTo(SpinnerImageBasedLightingController.GeeoneReflectionBoost));
            Assert.That(
                shipping.AmbientBoost,
                Is.EqualTo(SpinnerImageBasedLightingController.GeeoneAmbientBoost));
            Assert.That(
                shipping.VisibilityFillIntensity,
                Is.EqualTo(SpinnerImageBasedLightingController.GeeoneVisibilityFillIntensity));
            Assert.That(
                shipping.KeyLightFloor,
                Is.EqualTo(SpinnerImageBasedLightingController.GeeoneKeyLightFloor));
            Assert.That(
                SpinnerImageBasedLightingController.ResolveGeeoneLightFloor("Key_5000K"),
                Is.EqualTo(SpinnerImageBasedLightingController.GeeoneKeyLightFloor));

            Assert.That(GeeoneLightingPresetCatalog.All.Count, Is.EqualTo(4));
            Assert.That(
                GeeoneLightingPresetCatalog.All.Select(preset => preset.Id).Distinct().Count(),
                Is.EqualTo(4));
            // The superseded Build 47 recipe stays only as the A/B reference:
            // brighter on every direct lever, no softbox. It must not ship.
            GeeoneLightingPreset old = GeeoneLightingPresetCatalog.StudioBright;
            Assert.That(old.Id, Is.Not.EqualTo(GeeoneLightingPresetCatalog.ShippingId));
            Assert.That(old.StudioSoftboxIntensity, Is.EqualTo(0f));
            Assert.That(shipping.DirectLightBoost, Is.LessThan(old.DirectLightBoost));
            Assert.That(shipping.ReflectionBoost, Is.LessThan(old.ReflectionBoost));
            Assert.That(shipping.KeyLightFloor, Is.LessThan(old.KeyLightFloor));
            // The camera-aligned fill is what flattens the facets into one
            // white plane on metallic steel; Soft Studio cuts it to ~30%.
            Assert.That(
                shipping.VisibilityFillIntensity,
                Is.LessThan(old.VisibilityFillIntensity * 0.35f));
            Assert.That(shipping.TotalDirectEnergy, Is.LessThan(old.TotalDirectEnergy * 0.40f));
            // The steel's only large soft source; shipping now carries it.
            Assert.That(shipping.StudioSoftboxIntensity, Is.GreaterThan(0f));

            foreach (GeeoneLightingPreset preset in GeeoneLightingPresetCatalog.All)
            {
                Assert.That(preset.DirectLightBoost, Is.GreaterThan(0f), preset.Id);
                Assert.That(preset.TotalDirectEnergy, Is.GreaterThan(0f), preset.Id);
            }
            Assert.That(
                GeeoneLightingPresetCatalog.Overcast.StudioSoftboxIntensity,
                Is.GreaterThan(shipping.StudioSoftboxIntensity));
            Assert.That(
                GeeoneLightingPresetCatalog.Overcast.TotalDirectEnergy,
                Is.LessThan(shipping.TotalDirectEnergy));
            Assert.That(
                GeeoneLightingPresetCatalog.LowKey.TotalDirectEnergy,
                Is.LessThan(shipping.TotalDirectEnergy));

            try
            {
                GeeoneLightingPresetCatalog.SetActiveForPreview(GeeoneLightingPresetCatalog.Overcast);
                Assert.That(
                    SpinnerImageBasedLightingController.ResolveGeeoneLightFloor("Key_5000K"),
                    Is.EqualTo(GeeoneLightingPresetCatalog.Overcast.KeyLightFloor));
                // Preset values are the spots' final GEEONE intensities, not a
                // floor under the authored value; otherwise softer presets
                // could not lower the key below authored*boost.
                Assert.That(
                    SpinnerImageBasedLightingController.ResolveAuthoredLightIntensity(
                        "metal-three-blade",
                        "Key_5000K",
                        1.4f,
                        1f),
                    Is.EqualTo(GeeoneLightingPresetCatalog.Overcast.KeyLightFloor).Within(1e-5f));
            }
            finally
            {
                GeeoneLightingPresetCatalog.ResetActive();
            }

            Assert.That(
                GeeoneLightingPresetCatalog.Active.Id,
                Is.EqualTo(GeeoneLightingPresetCatalog.ShippingId),
                "A preview capture must never leave a review preset active.");
        }

        [Test]
        public void GeeoneLightingPreset_LaunchArgumentsSelectPresetAndScaleOnlyDirectLights()
        {
            GeeoneLightingPreset none = GeeoneLightingPresetCatalog.ResolveLaunchPreset(
                new[] { "--unrelated" });
            Assert.That(none.Id, Is.EqualTo(GeeoneLightingPresetCatalog.ShippingId));

            GeeoneLightingPreset scaled = GeeoneLightingPresetCatalog.ResolveLaunchPreset(
                new[]
                {
                    GeeoneLightingPresetCatalog.PresetLaunchArgumentPrefix
                        + GeeoneLightingPresetCatalog.SoftStudioId,
                    GeeoneLightingPresetCatalog.DirectScaleLaunchArgumentPrefix + "0.5",
                });
            GeeoneLightingPreset soft = GeeoneLightingPresetCatalog.SoftStudio;
            Assert.That(scaled.Id, Is.EqualTo(soft.Id));
            Assert.That(scaled.KeyLightFloor, Is.EqualTo(soft.KeyLightFloor * 0.5f).Within(0.0001f));
            Assert.That(scaled.VisibilityFillIntensity, Is.EqualTo(soft.VisibilityFillIntensity * 0.5f).Within(0.0001f));
            Assert.That(scaled.StudioSoftboxIntensity, Is.EqualTo(soft.StudioSoftboxIntensity));
            Assert.That(scaled.AmbientBoost, Is.EqualTo(soft.AmbientBoost));

            GeeoneLightingPreset bad = GeeoneLightingPresetCatalog.ResolveLaunchPreset(
                new[] { GeeoneLightingPresetCatalog.DirectScaleLaunchArgumentPrefix + "-1" });
            Assert.That(bad.KeyLightFloor, Is.EqualTo(GeeoneLightingPresetCatalog.Shipping.KeyLightFloor));
        }

        [Test]
        public void EveryProductSceneSharesOneSubtleCameraGrading()
        {
            // Post exposure lifts the shared canyon backdrop as well as the toy,
            // so the four scenes may only differ in model lights, never in EV.
            Assert.That(SpinnerSharedPresentationGrading.PostExposureEv, Is.EqualTo(0.15f));
            Assert.That(
                SpinnerSharedPresentationGrading.PostExposureLinearGain,
                Is.EqualTo(1.11f).Within(0.01f));
            Assert.That(
                MagneticSlideShippingLighting.BalancedPostExposureEv,
                Is.EqualTo(SpinnerSharedPresentationGrading.PostExposureEv));

            // Backdrop glow energy must be the same behind every canyon toy.
            Assert.That(
                SpinnerImageBasedLightingController.ResolveEnvironmentGlowScale(
                    ProductCatalog.MagneticSlideTileModelId),
                Is.EqualTo(SpinnerImageBasedLightingController.ResolveEnvironmentGlowScale(
                    ProductCatalog.MetalThreeBladeModelId)));
            Assert.That(
                SpinnerImageBasedLightingController.ResolveEnvironmentGlowScale(
                    ProductCatalog.MagneticSlideTileModelId),
                Is.EqualTo(SpinnerImageBasedLightingController.SoftEnvironmentGlowScale));
            // Backdrop glow energy must not depend on accent hue.
            float[] glowLuminance = ProductCatalog.ShippingModelIds()
                .Select(SpinnerEnvironmentAccentCatalog.Resolve)
                .Select(SpinnerAdaptiveBackdropRules.Luminance)
                .ToArray();
            Assert.That(glowLuminance.Max(), Is.LessThanOrEqualTo(SpinnerAdaptiveBackdropRules.MaximumLuminance + 0.001f));
            Assert.That(glowLuminance.Max() - glowLuminance.Min(), Is.LessThan(0.01f));

            foreach (string scenePath in ProductCatalog.ShippingScenePaths())
            {
                EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
                SpinnerEnvironmentPresenter presenter =
                    SpinnerEnvironmentPresenter.Install(scenePath);
                Assert.That(presenter, Is.Not.Null, scenePath);
                Camera camera = presenter.GetComponent<Camera>();
                Assert.That(camera.allowHDR, Is.True, scenePath);
                Assert.That(
                    camera.GetUniversalAdditionalCameraData().renderPostProcessing,
                    Is.True,
                    scenePath);
                Assert.That(
                    SpinnerSharedPresentationGrading.TryReadExposure(
                        camera,
                        out float exposure,
                        out UnityEngine.Rendering.Universal.TonemappingMode mode),
                    Is.True,
                    scenePath);
                Assert.That(
                    exposure,
                    Is.EqualTo(SpinnerSharedPresentationGrading.PostExposureEv),
                    scenePath);
                Assert.That(
                    mode,
                    Is.EqualTo(SpinnerSharedPresentationGrading.Tonemapping),
                    scenePath);
                // Exactly one camera volume: the slide's controller must reuse
                // the shared one instead of stacking a second exposure.
                Assert.That(
                    camera.GetComponents<UnityEngine.Rendering.Volume>().Length,
                    Is.EqualTo(1),
                    scenePath);
            }
        }

        [Test]
        public void GeeoneLightsIdenticallyInLibraryAndDetail()
        {
            SpinnerEnvironmentProfile profile = SpinnerEnvironmentCatalog.Profiles
                .Single(candidate => candidate.ModelId == ProductCatalog.MetalThreeBladeModelId);
            Assert.That(profile.LibraryLightScale, Is.EqualTo(1f));
            Assert.That(profile.LibraryReflectionScale, Is.EqualTo(1f));

            EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
            SpinnerEnvironmentPresenter presenter =
                SpinnerEnvironmentPresenter.Install(profile.ScenePath);
            SpinnerImageBasedLightingController ibl = presenter.ImageBasedLighting;
            Assert.That(ibl, Is.Not.Null);

            presenter.SetLibraryPreviewActive(true, true);
            float[] libraryIntensities = ReadAuthoredIntensities(profile);
            float libraryReflection = RenderSettings.reflectionIntensity;
            Color librarySky = RenderSettings.ambientSkyColor;
            float libraryFill = ibl.VisibilityFillLight.intensity;

            presenter.SetLibraryPreviewActive(false, true);
            float[] detailIntensities = ReadAuthoredIntensities(profile);
            Assert.That(detailIntensities, Is.EqualTo(libraryIntensities).Within(0.0001f));
            Assert.That(RenderSettings.reflectionIntensity, Is.EqualTo(libraryReflection).Within(0.0001f));
            AssertColor(RenderSettings.ambientSkyColor, librarySky);
            Assert.That(ibl.VisibilityFillLight.intensity, Is.EqualTo(libraryFill).Within(0.0001f));

            // The recipe itself: boosted soft-metal with per-light floors.
            Assert.That(
                ibl.VisibilityFillLight.intensity,
                Is.EqualTo(SpinnerImageBasedLightingController.GeeoneVisibilityFillIntensity)
                    .Within(0.0001f));
            Assert.That(
                detailIntensities[0],
                Is.GreaterThanOrEqualTo(SpinnerImageBasedLightingController.GeeoneKeyLightFloor));
            Assert.That(
                RenderSettings.ambientSkyColor.r,
                Is.GreaterThanOrEqualTo(
                    SpinnerImageBasedLightingController.GeeoneAmbientFloorSky.r
                        * SpinnerImageBasedLightingController.GeeoneAmbientFloorScale
                        - 0.0001f));
            Assert.That(ibl.PresentationTransitionActive, Is.False);
        }

        private static float[] ReadAuthoredIntensities(SpinnerEnvironmentProfile profile)
        {
            Light[] lights = Object.FindObjectsByType<Light>();
            return profile.Lights
                .Select(preset => lights.Single(light => light.name == preset.ObjectName).intensity)
                .ToArray();
        }

        [Test]
        public void LibraryDetailLightingSwitchTweensOnTheSharedPresentationCurve()
        {
            var from = new SpinnerImageBasedLightingController.PresentationLightingState(
                0.48f, 0.42f, 0.10f, 0.6f, Color.black, Color.black, Color.black);
            var to = new SpinnerImageBasedLightingController.PresentationLightingState(
                1f, 1f, 0.30f, 1f, Color.white, Color.gray, Color.red);
            var mid = SpinnerImageBasedLightingController.PresentationLightingState.Lerp(
                from, to, 0.5f);
            Assert.That(mid.LightScale, Is.EqualTo(0.74f).Within(0.0001f));
            Assert.That(mid.ReflectionScale, Is.EqualTo(0.71f).Within(0.0001f));
            Assert.That(mid.VisibilityFillIntensity, Is.EqualTo(0.20f).Within(0.0001f));
            Assert.That(mid.AmbientSky.r, Is.EqualTo(0.5f).Within(0.0001f));

            string ibl = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerImageBasedLightingController.cs");
            StringAssert.Contains("SpinnerPresentationTransition.ResolveProgress(", ibl);
            StringAssert.Contains("AdvancePresentationTransition(Time.unscaledDeltaTime)", ibl);
            StringAssert.DoesNotContain("libraryPreviewActive ? 1.28f : 1f", ibl);
            string presenter = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerEnvironmentPresenter.cs");
            StringAssert.Contains(
                "ImageBasedLighting?.SetLibraryPreviewActive(active, immediate)",
                presenter);
            string capture = File.ReadAllText(
                "Assets/Editor/GeeoneShippingPreviewCapture.cs");
            StringAssert.DoesNotContain("SetLightIntensity(\"Key_5000K\"", capture);
            StringAssert.DoesNotContain("RenderSettings.reflectionIntensity = 0.62f", capture);
        }

        [Test]
        public void ProductCoordinatorWiresEnvironmentWithoutEnteringInteractionOrHaptics()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string presenter = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerEnvironmentPresenter.cs");
            string parallax = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerSceneParallaxController.cs");
            string imageBasedLighting = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerImageBasedLightingController.cs");
            string groundingStage = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerGroundingStage.cs");
            string parallaxShader = File.ReadAllText(
                "Assets/Shaders/EnvironmentParallaxUnlit.shader");
            string portraitCamera = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/PortraitCameraFramer.cs");
            string orbitCamera = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Presentation/OrbitPresentationCamera.cs");
            string edcCamera = File.ReadAllText(
                "Assets/_EDC/Runtime/EdcPortraitCameraFramer.cs");
            string presentationTransition = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerPresentationTransition.cs");
            string blueMotionSource = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/DeviceMotionController.cs");
            string metalMotionSource = File.ReadAllText(
                "Assets/Scripts/Product/MetalDeviceMotionController.cs");
            string edcMotionSource = File.ReadAllText(
                "Assets/Scripts/Product/EdcDeviceMotionController.cs");
            string nativeMotionSource = File.ReadAllText(
                "Assets/Plugins/iOS/CodexIosDeviceMotion.mm");
            string nativeOverlaySource = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");

            StringAssert.Contains(
                "environmentPresenter = SpinnerEnvironmentPresenter.Install(scenePath)",
                coordinator);
            StringAssert.Contains("SetLibraryPreviewActive", coordinator);
            StringAssert.Contains("targetPresentationVisibility", groundingStage);
            StringAssert.Contains("usesBakedSupportSurface", groundingStage);
            StringAssert.Contains("SetExperienceTint", presenter);
            StringAssert.Contains("ConfigureBackgroundSubjectGlow", presenter);
            StringAssert.Contains("fanCardPedestalVolume", presenter);
            StringAssert.Contains("FanCardForegroundGlowIntensity", presenter);
            StringAssert.DoesNotContain("angularVelocity", presenter);
            StringAssert.DoesNotContain("IosHaptics", presenter);
            StringAssert.DoesNotContain("FidgetHapticRouter", presenter);
            StringAssert.DoesNotContain("DetentFeelRuntime", presenter);
            StringAssert.Contains(
                "SceneParallaxInput.Publish(filteredTilt, maximumInputAngle);",
                blueMotionSource);
            StringAssert.Contains(
                "SceneParallaxInput.Publish(filteredTilt, maximumInputAngle);",
                metalMotionSource);
            StringAssert.Contains(
                "SceneParallaxInput.Publish(filteredTilt, maximumInputAngle);",
                edcMotionSource);
            StringAssert.DoesNotContain(
                "targetTilt = Vector2.ClampMagnitude(targetTilt, 1f);",
                blueMotionSource);
            StringAssert.DoesNotContain(
                "targetTilt = Vector2.ClampMagnitude(targetTilt, 1f);",
                metalMotionSource);
            StringAssert.DoesNotContain(
                "targetTilt = Vector2.ClampMagnitude(targetTilt, 1f);",
                edcMotionSource);
            StringAssert.Contains(
                "DeviceMotionOrbitMapping.ResolveOrbitDegrees",
                portraitCamera);
            StringAssert.Contains(
                "DeviceMotionOrbitMapping.ResolveOrbitDegrees",
                orbitCamera);
            StringAssert.Contains(
                "DeviceMotionOrbitMapping.ResolveOrbitDegrees",
                edcCamera);
            StringAssert.Contains("EdcDeviceMotionController", coordinator);
            StringAssert.Contains("SceneManager.LoadSceneAsync", coordinator);
            StringAssert.DoesNotContain("SceneManager.LoadScene(buildIndex", coordinator);
            StringAssert.Contains(
                ".BeginLibraryPageExit(-pageDirection)",
                coordinator,
                "A left swipe to the next page must move the old model left.");
            StringAssert.Contains(
                ".BeginLibraryPageEntrance(\n"
                + "                        pendingLibraryPageEntranceDirection)",
                coordinator,
                "The next model must enter from the right for a left swipe.");
            StringAssert.Contains("SetLibrarySwipeProgressFromNativeUi", coordinator);
            StringAssert.Contains("SetLibraryPageDragProgress(progress)", coordinator);
            StringAssert.Contains("BeginLibrarySwipeFromNativeUi", coordinator);
            StringAssert.Contains("CommitLibrarySwipeFromNativeUi", coordinator);
            StringAssert.Contains("EndLibrarySwipeFromNativeUi", coordinator);
            StringAssert.Contains("LibrarySwipeSessionGate", coordinator);
            StringAssert.Contains("EndLibraryPageDrag()", coordinator);
            StringAssert.Contains("SetLibraryPageDragProgress", parallax);
            StringAssert.Contains(
                "value.translation.width / width",
                nativeOverlaySource,
                "A leftward finger translation must drive the old model left.");
            StringAssert.Contains(".highPriorityGesture(", nativeOverlaySource);
            StringAssert.Contains("BeginLibrarySwipeFromNativeUi", nativeOverlaySource);
            StringAssert.Contains("CommitLibrarySwipeFromNativeUi", nativeOverlaySource);
            StringAssert.DoesNotContain(
                "Give that bridge one frame to start the page transition",
                nativeOverlaySource,
                "The swipe must use an explicit commit/cancel handshake, not a timer.");
            StringAssert.Contains(
                ".accessibilityIdentifier(\"library-model-carousel\")",
                nativeOverlaySource);
            StringAssert.Contains("load.allowSceneActivation = false", coordinator);
            StringAssert.Contains("LibraryPageExitLeadSeconds", coordinator);
            StringAssert.Contains("queuedModelId", coordinator);
            StringAssert.Contains("DeepStarLayerPixels = 2f", parallax);
            StringAssert.Contains("FarLayerPixels = 8f", parallax);
            StringAssert.Contains("AnchorLayerPixels = 14f", parallax);
            StringAssert.Contains("LibraryAnchorLayerPixels = 20f", parallax);
            StringAssert.Contains("LibraryHoverAmplitudePixels = 2.5f", parallax);
            StringAssert.Contains("LibraryPageTravelViewport = 1.08f", parallax);
            StringAssert.Contains("LeftForegroundPixels = 30f", parallax);
            StringAssert.Contains("IsReduceMotionEnabled", parallax);
            StringAssert.Contains("SetViewResponse", parallax);
            StringAssert.Contains("ParallaxFullScaleAngle = 15f", parallax);
            StringAssert.Contains("VerticalMotionScale = 0.60f", parallax);
            StringAssert.DoesNotContain("IosDeviceMotion.Start", parallax);
            StringAssert.DoesNotContain("angularVelocity", parallax);
            StringAssert.DoesNotContain("FidgetHapticRouter", parallax);
            StringAssert.DoesNotContain("DeviceOrientationEvent", parallax);
            StringAssert.Contains("BuildReflectionCubemap", imageBasedLighting);
            StringAssert.Contains("CachedBackgroundPalettes", imageBasedLighting);
            StringAssert.Contains(
                "profile.BackgroundResourcePath",
                imageBasedLighting);
            StringAssert.Contains("TryResolvePalette", imageBasedLighting);
            StringAssert.Contains("weightChroma", imageBasedLighting);
            StringAssert.Contains("|chroma-key", imageBasedLighting);
            StringAssert.Contains("ResolveModelAccent", imageBasedLighting);
            StringAssert.Contains("ResolveCoupledGlowColors", imageBasedLighting);
            StringAssert.Contains("EnvironmentColorCoupling", imageBasedLighting);
            StringAssert.Contains("FanCardEnvironmentColorCoupling", imageBasedLighting);
            StringAssert.Contains("CoupleFanCardPalette", imageBasedLighting);
            StringAssert.Contains("ResolveFanCardSampleMix", imageBasedLighting);
            StringAssert.Contains("FanCardVisibleKeyViewportX", imageBasedLighting);
            StringAssert.Contains("FanCardKeyPitchMin", imageBasedLighting);
            StringAssert.Contains("FanCardForegroundGlowIntensity", imageBasedLighting);
            StringAssert.Contains("FanCardPedestalGlowRadius", imageBasedLighting);
            StringAssert.Contains("ResolveFanCardKeyRotation", imageBasedLighting);
            StringAssert.Contains("ResolveFanCardContactShadowCenterX", imageBasedLighting);
            StringAssert.Contains("FanCardAmbientChromaRetention", imageBasedLighting);
            StringAssert.Contains("RetainAmbientLuminance", imageBasedLighting);
            StringAssert.Contains("_GlowScaleB", parallaxShader);
            StringAssert.Contains("_ShadowStrength", parallaxShader);
            StringAssert.Contains("color *= 1.0h - shadow", parallaxShader);
            StringAssert.Contains("new Vector3(0f, 1f, -0.02f)", portraitCamera);
            StringAssert.Contains("_pitch = 89f", orbitCamera);
            StringAssert.Contains("new Vector3(0f, 1f, -0.02f)", edcCamera);
            StringAssert.Contains(
                "SetLibraryPreviewActive(bool active, bool immediate = false)",
                portraitCamera);
            StringAssert.Contains(
                "SetLibraryPreviewActive(bool active, bool immediate = false)",
                orbitCamera);
            StringAssert.Contains(
                "SetLibraryPreviewActive(bool active, bool immediate = false)",
                edcCamera);
            StringAssert.Contains("Vector3.Slerp", portraitCamera);
            StringAssert.Contains("Mathf.LerpAngle", orbitCamera);
            StringAssert.Contains("Vector3.Slerp", edcCamera);
            StringAssert.Contains("DurationSeconds = 0.68f", presentationTransition);
            StringAssert.Contains("ResolveDetailDepthScale", presentationTransition);
            StringAssert.Contains("DetailBackgroundScale = 1.16f", presenter);
            StringAssert.Contains("DetailMidgroundScale = 1.20f", presenter);
            StringAssert.Contains("ApplyDetailDepthScale", presenter);
            StringAssert.Contains("framingTransitionElapsed", presenter);
            StringAssert.Contains(
                "SetDetailEntranceProgressForPreview",
                portraitCamera);
            StringAssert.Contains(
                "SetDetailEntranceProgressForPreview",
                orbitCamera);
            StringAssert.Contains(
                "SetDetailEntranceProgressForPreview",
                edcCamera);
            StringAssert.Contains(
                "detailEntranceDuration: TimeInterval = 0.68",
                nativeOverlaySource);
            StringAssert.Contains(
                "detailControlsRevealDelay: TimeInterval = 0.48",
                nativeOverlaySource);
            StringAssert.Contains(
                "hidePanel(forDetailEntrance: true)",
                nativeOverlaySource);
            StringAssert.DoesNotContain(
                "angularVelocity",
                portraitCamera + orbitCamera + edcCamera + presentationTransition);
            StringAssert.Contains("libraryLightScale", imageBasedLighting);
            StringAssert.Contains("UIAccessibilityIsReduceMotionEnabled", nativeMotionSource);
            StringAssert.Contains("receiveShadows = true", groundingStage);
            StringAssert.DoesNotContain("Rigidbody =", groundingStage);
            StringAssert.DoesNotContain("IosHaptics", imageBasedLighting);
            StringAssert.DoesNotContain("FidgetHapticRouter", imageBasedLighting);
            StringAssert.DoesNotContain("Rigidbody", edcMotionSource);
            StringAssert.DoesNotContain("IosHaptics", edcMotionSource);
            StringAssert.DoesNotContain("FidgetHapticRouter", edcMotionSource);

            AssertColor(
                SpinnerEnvironmentPresenter.ResolveExperienceTint(Color.black),
                Color.white);
        }

        [Test]
        public void AllSixProductsUseLiveBoundsAndViewportOccupancyBoundaries()
        {
            foreach (SpinnerEnvironmentProfile environment in
                     SpinnerEnvironmentCatalog.Profiles)
            {
                EditorSceneManager.OpenScene(
                    environment.ScenePath,
                    OpenSceneMode.Single);
                ProductFramingProfile framing = ProductFramingCatalog.Resolve(
                    environment.ScenePath);

                Camera camera;
                Transform target;
                System.Action<bool> setLibraryPreview;
                PortraitCameraFramer portrait =
                    Object.FindAnyObjectByType<PortraitCameraFramer>();
                OrbitPresentationCamera orbit =
                    Object.FindAnyObjectByType<OrbitPresentationCamera>();
                EdcPortraitCameraFramer edc =
                    Object.FindAnyObjectByType<EdcPortraitCameraFramer>();

                if (portrait != null)
                {
                    camera = portrait.GetComponent<Camera>();
                    target = portrait.Target;
                    portrait.ConfigureFraming(framing);
                    portrait.ResetInteractiveView();
                    setLibraryPreview = active =>
                        portrait.SetLibraryPreviewActive(active, true);
                }
                else if (orbit != null)
                {
                    camera = orbit.GetComponent<Camera>();
                    target = orbit.Target;
                    orbit.ConfigureFraming(framing);
                    orbit.ResetHero();
                    setLibraryPreview = active =>
                        orbit.SetLibraryPreviewActive(active, true);
                }
                else
                {
                    Assert.That(edc, Is.Not.Null, environment.ModelId);
                    camera = edc.GetComponent<Camera>();
                    target = edc.Target;
                    edc.ConfigureFraming(framing);
                    edc.ResetInteractiveView();
                    setLibraryPreview = active =>
                        edc.SetLibraryPreviewActive(active, true);
                }

                camera.aspect = 1290f / 2796f;
                setLibraryPreview(false);
                if (edc != null && edc.PreservesAuthoredDefaultPose)
                {
                    // The slide tile detail camera is an authored fixed pose, so
                    // the library must keep that magnification instead of
                    // refilling a boundary that scales with the phone aspect.
                    float authored = edc.AuthoredDefaultDistance;
                    Assert.That(
                        edc.FramedDistance,
                        Is.EqualTo(authored).Within(0.0005f),
                        environment.ModelId + " detail must sit at the authored distance.");
                    setLibraryPreview(true);
                    Assert.That(
                        edc.FramedDistance,
                        Is.GreaterThanOrEqualTo(
                            authored * EdcPortraitCameraFramer.LibraryDistanceScale - 0.0005f),
                        environment.ModelId + " library must not be closer than detail.");
                    Assert.That(
                        edc.FramedDistance,
                        Is.LessThanOrEqualTo(authored * 1.35f),
                        environment.ModelId + " library must stay near the detail magnification.");
                    Assert.That(
                        ProductCameraFraming.TryGetProductBounds(target, out Bounds libraryBounds),
                        Is.True);
                    Vector2 projected = ProductCameraFraming.ProjectedViewportSize(
                        camera,
                        libraryBounds);
                    Assert.That(projected.x, Is.LessThanOrEqualTo(
                        EdcPortraitCameraFramer.LibrarySafetyFraction + 0.03f));
                    Assert.That(projected.y, Is.LessThanOrEqualTo(
                        EdcPortraitCameraFramer.LibrarySafetyFraction + 0.03f));
                    continue;
                }

                AssertViewportBoundary(
                    environment.ModelId + " detail",
                    camera,
                    target,
                    framing.DetailWidthFraction,
                    framing.DetailHeightFraction,
                    environment.ModelId == ProductCatalog.MagneticFanCardModelId
                        ? 0.60f
                        : 0.88f);

                setLibraryPreview(true);
                AssertViewportBoundary(
                    environment.ModelId + " library",
                    camera,
                    target,
                    framing.LibraryWidthFraction,
                    framing.LibraryHeightFraction,
                    environment.ModelId == ProductCatalog.MagneticFanCardModelId
                        ? 0.60f
                        : 0.88f);
            }
        }

        [Test]
        public void BackgroundPaletteAndGroundingMesh_AreDeterministicAndMaterialDriven()
        {
            const int width = 6;
            const int height = 8;
            var pixels = Enumerable.Repeat(
                new Color(0.018f, 0.020f, 0.022f, 1f),
                width * height).ToArray();
            for (int y = 5; y < height; y++)
            {
                for (int x = 0; x < 2; x++)
                {
                    pixels[y * width + x] = new Color(0.42f, 0.30f, 0.20f, 1f);
                }
            }

            SpinnerEnvironmentPalette palette =
                SpinnerImageBasedLightingController.AnalyzePixels(
                    pixels,
                    width,
                    height);
            SpinnerEnvironmentPalette chromaWeighted =
                SpinnerImageBasedLightingController.AnalyzePixels(
                    pixels,
                    width,
                    height,
                    true);
            Assert.That(chromaWeighted.Key.r, Is.GreaterThan(chromaWeighted.Key.b));
            Assert.That(palette.KeyViewport.x, Is.LessThan(0.5f));
            Assert.That(palette.KeyViewport.y, Is.GreaterThan(0.5f));
            Assert.That(palette.Sky.maxColorComponent, Is.GreaterThan(
                palette.Ground.maxColorComponent));

            Mesh round = SpinnerGroundingStage.CreateStageMesh(
                SpinnerGroundingStageShape.Round,
                2f,
                2f,
                0.25f);
            Mesh oblong = SpinnerGroundingStage.CreateStageMesh(
                SpinnerGroundingStageShape.Oblong,
                3f,
                1.5f,
                0.25f);
            try
            {
                Assert.That(round.vertexCount, Is.GreaterThan(128));
                Assert.That(round.triangles.Length / 3, Is.GreaterThan(200));
                Assert.That(round.bounds.size.x, Is.EqualTo(round.bounds.size.z).Within(0.03f));
                Assert.That(oblong.bounds.size.x, Is.GreaterThan(oblong.bounds.size.z));
                Assert.That(oblong.bounds.size.y, Is.EqualTo(0.25f).Within(0.01f));
            }
            finally
            {
                Object.DestroyImmediate(round);
                Object.DestroyImmediate(oblong);
            }
        }

        [Test]
        public void SoftLightingPolicy_ReducesEnergyAndCapsReflectionWithoutHueShift()
        {
            Assert.That(SpinnerImageBasedLightingController.UsesSoftSpinnerLighting(
                ProductCatalog.PointedThreeBladeModelId), Is.True);
            Assert.That(SpinnerImageBasedLightingController.UsesSoftSpinnerLighting(
                ProductCatalog.MetalThreeBladeModelId), Is.True);
            Assert.That(SpinnerImageBasedLightingController.UsesSoftSpinnerLighting(
                ProductCatalog.GoldFourWingModelId), Is.True);
            Assert.That(SpinnerImageBasedLightingController.UsesSoftSpinnerLighting(
                ProductCatalog.GraphiteTwoLobeModelId), Is.True);
            Assert.That(SpinnerImageBasedLightingController.UsesSoftSpinnerLighting(
                ProductCatalog.MagneticSlideTileModelId), Is.False);
            Assert.That(SpinnerImageBasedLightingController.UsesSoftSpinnerLighting(
                ProductCatalog.MagneticFanCardModelId), Is.False);
            Assert.That(SpinnerImageBasedLightingController.SoftAmbientScale,
                Is.InRange(0.35f, 0.5f));
            Assert.That(SpinnerImageBasedLightingController.SoftDirectLightScale,
                Is.InRange(0.3f, 0.45f));
            Assert.That(
                SpinnerImageBasedLightingController.SoftReflectionIntensityScale,
                Is.InRange(0.3f, 0.45f));
            Assert.That(
                SpinnerImageBasedLightingController.SoftViewHighlightScale,
                Is.LessThan(SpinnerImageBasedLightingController
                    .SoftDirectLightScale));
            Assert.That(
                SpinnerImageBasedLightingController.SoftEnvironmentGlowScale,
                Is.InRange(0.25f, 0.45f));
            Assert.That(
                SpinnerImageBasedLightingController.ResolveSoftSpinnerLightTrim(
                    ProductCatalog.PointedThreeBladeModelId),
                Is.LessThan(SpinnerImageBasedLightingController
                    .ResolveSoftSpinnerLightTrim(
                        ProductCatalog.MetalThreeBladeModelId)));
            // GEEONE keeps the full soft trim and layers its own boosted recipe
            // on top in both library and detail (rev-007, device accepted).
            Assert.That(
                SpinnerImageBasedLightingController.ResolveSoftSpinnerLightTrim(
                    ProductCatalog.MetalThreeBladeModelId),
                Is.EqualTo(1f));
            Assert.That(
                SpinnerImageBasedLightingController.ResolveSoftSpinnerLightTrim(
                    ProductCatalog.GraphiteTwoLobeModelId),
                Is.EqualTo(1f));
            Assert.That(
                SpinnerImageBasedLightingController.ResolveSoftSpinnerLightTrim(
                    ProductCatalog.MagneticFanCardModelId),
                Is.EqualTo(1f));
            Assert.That(
                SpinnerImageBasedLightingController.SoftBrightMetalAlbedoScale,
                Is.InRange(0.85f, 0.95f));
            Assert.That(
                SpinnerImageBasedLightingController.SoftBrightMetalSmoothnessCap,
                Is.InRange(0.6f, 0.75f));
            Assert.That(
                SpinnerImageBasedLightingController.EnvironmentColorCoupling,
                Is.InRange(0.10f, 0.18f));
            Assert.That(
                SpinnerImageBasedLightingController.FanCardEnvironmentColorCoupling,
                Is.InRange(0.20f, 0.34f));
            Assert.That(
                SpinnerImageBasedLightingController.FanCardEnvironmentColorCoupling,
                Is.GreaterThan(
                    SpinnerImageBasedLightingController.EnvironmentColorCoupling));
            Assert.That(
                SpinnerImageBasedLightingController.AmbientChromaRetention,
                Is.InRange(0.24f, 0.40f));
            Assert.That(
                SpinnerImageBasedLightingController.FanCardAmbientChromaRetention,
                Is.GreaterThan(
                    SpinnerImageBasedLightingController.AmbientChromaRetention));

            Color brightMetal = new Color(0.80f, 0.40f, 0.20f, 0.65f);
            Color softenedMetal = SpinnerImageBasedLightingController
                .ResolveSoftMaterialColor(brightMetal);
            Assert.That(softenedMetal.r, Is.LessThan(brightMetal.r));
            Assert.That(softenedMetal.g / softenedMetal.r,
                Is.EqualTo(brightMetal.g / brightMetal.r).Within(0.0001f));
            Assert.That(softenedMetal.b / softenedMetal.r,
                Is.EqualTo(brightMetal.b / brightMetal.r).Within(0.0001f));
            Assert.That(softenedMetal.a, Is.EqualTo(brightMetal.a));

            Color saturatedAmbient = new Color(0.20f, 0.55f, 0.90f, 1f);
            Color restrainedAmbient = SpinnerImageBasedLightingController
                .RetainAmbientLuminance(saturatedAmbient);
            Color fanAmbient = SpinnerImageBasedLightingController
                .RetainAmbientLuminance(
                    saturatedAmbient,
                    SpinnerImageBasedLightingController.FanCardAmbientChromaRetention);
            float sourceChroma = Mathf.Max(saturatedAmbient.r, saturatedAmbient.g, saturatedAmbient.b)
                - Mathf.Min(saturatedAmbient.r, saturatedAmbient.g, saturatedAmbient.b);
            float restrainedChroma = Mathf.Max(restrainedAmbient.r, restrainedAmbient.g, restrainedAmbient.b)
                - Mathf.Min(restrainedAmbient.r, restrainedAmbient.g, restrainedAmbient.b);
            float fanChroma = Mathf.Max(fanAmbient.r, fanAmbient.g, fanAmbient.b)
                - Mathf.Min(fanAmbient.r, fanAmbient.g, fanAmbient.b);
            Assert.That(restrainedChroma, Is.LessThan(sourceChroma));
            Assert.That(fanChroma, Is.GreaterThan(restrainedChroma));

            var warmPalette = new SpinnerEnvironmentPalette(
                new Color(0.22f, 0.18f, 0.14f),
                new Color(0.16f, 0.12f, 0.10f),
                new Color(0.06f, 0.04f, 0.03f),
                new Color(1.00f, 0.52f, 0.22f),
                new Color(0.42f, 0.58f, 0.78f),
                new Vector2(0.78f, 0.84f));
            Color model = new Color(0.40f, 0.385f, 0.36f, 1f);
            SpinnerImageBasedLightingController.ResolveCoupledGlowColors(
                warmPalette,
                model,
                Vector2.zero,
                out Color rotorLeft,
                out _);
            SpinnerImageBasedLightingController.ResolveCoupledGlowColors(
                warmPalette,
                model,
                Vector2.zero,
                SpinnerImageBasedLightingController.FanCardEnvironmentColorCoupling,
                out Color fanLeft,
                out _);
            Assert.That(fanLeft.r - fanLeft.b, Is.GreaterThan(rotorLeft.r - rotorLeft.b));

            var greyCanyonSample = new SpinnerEnvironmentPalette(
                new Color(0.12f, 0.13f, 0.12f),
                new Color(0.08f, 0.09f, 0.08f),
                new Color(0.02f, 0.02f, 0.02f),
                new Color(0.26f, 0.28f, 0.25f),
                new Color(0.22f, 0.24f, 0.23f),
                new Vector2(0.50f, 0.38f));
            var authoredFanLights = new SpinnerEnvironmentPalette(
                new Color(0.22f, 0.205f, 0.185f),
                new Color(0.10f, 0.092f, 0.082f),
                new Color(0.028f, 0.025f, 0.022f),
                new Color(1.00f, 0.88f, 0.76f),
                new Color(0.58f, 0.68f, 0.78f),
                new Vector2(0.50f, 0.94f));
            SpinnerEnvironmentPalette coupledGrey =
                SpinnerImageBasedLightingController.CoupleFanCardPalette(
                    greyCanyonSample,
                    authoredFanLights);
            Assert.That(coupledGrey.Key.r - coupledGrey.Key.b,
                Is.GreaterThan(0.18f));
            Assert.That(
                coupledGrey.KeyViewport.x,
                Is.EqualTo(
                    SpinnerImageBasedLightingController.FanCardVisibleKeyViewportX)
                    .Within(0.001f));

            Color source = new Color(3f, 1.5f, 0.75f, 0.2f);
            Color limited = SpinnerImageBasedLightingController
                .LimitReflectionPeak(
                    source,
                    SpinnerImageBasedLightingController.SoftReflectionPeak);
            Assert.That(limited.maxColorComponent,
                Is.EqualTo(SpinnerImageBasedLightingController
                    .SoftReflectionPeak).Within(0.0001f));
            Assert.That(limited.g / limited.r,
                Is.EqualTo(source.g / source.r).Within(0.0001f));
            Assert.That(limited.b / limited.r,
                Is.EqualTo(source.b / source.r).Within(0.0001f));
            Assert.That(limited.a, Is.EqualTo(1f));
        }

        [Test]
        public void ParallaxMathUsesDeadZoneExponentialSmoothingAndPixelAccurateProjection()
        {
            Assert.That(
                SpinnerPresentationTransition.ResolveProgress(0f),
                Is.EqualTo(0f));
            Assert.That(
                SpinnerPresentationTransition.ResolveProgress(
                    SpinnerPresentationTransition.DurationSeconds * 0.5f),
                Is.EqualTo(0.5f).Within(0.0001f));
            Assert.That(
                SpinnerPresentationTransition.ResolveProgress(
                    SpinnerPresentationTransition.DurationSeconds),
                Is.EqualTo(1f));
            Assert.That(
                SpinnerPresentationTransition.ResolveDetailDepthScale(1f, 1.10f),
                Is.EqualTo(1f).Within(0.0001f));
            Assert.That(
                SpinnerPresentationTransition.ResolveDetailDepthScale(0.5f, 1.10f),
                Is.EqualTo(1.05f).Within(0.0001f));
            Assert.That(
                SpinnerPresentationTransition.ResolveDetailDepthScale(0f, 1.10f),
                Is.EqualTo(1.10f).Within(0.0001f));

            Assert.That(
                SceneParallaxInput.NormalizePointer(
                    new Vector2(500f, 250f),
                    new Vector2(1000f, 500f)),
                Is.EqualTo(Vector2.zero));
            Assert.That(
                SceneParallaxInput.ApplyRadialDeadZone(
                    new Vector2(0.02f, 0.02f),
                    SpinnerSceneParallaxController.DefaultDeadZone),
                Is.EqualTo(Vector2.zero));

            Vector2 smoothed = SceneParallaxInput.Smooth(
                Vector2.zero,
                Vector2.one,
                SpinnerSceneParallaxController.DefaultResponse,
                1f / 60f);
            Assert.That(smoothed.x, Is.GreaterThan(0f).And.LessThan(1f));
            Assert.That(smoothed.y, Is.EqualTo(smoothed.x).Within(0.0001f));
            Assert.That(smoothed.x, Is.EqualTo(0.10f).Within(0.006f));

            Vector2 mapped = SceneParallaxInput.MapToParallax(
                new Vector2(15f / 18f, 15f / 18f),
                18f,
                SpinnerSceneParallaxController.ParallaxFullScaleAngle,
                SpinnerSceneParallaxController.VerticalMotionScale);
            Assert.That(mapped.x, Is.EqualTo(1f).Within(0.0001f));
            Assert.That(mapped.y, Is.EqualTo(0.60f).Within(0.0001f));
            Assert.That(SceneParallaxInput.SoftClampAxis(2f), Is.EqualTo(1f));
            Assert.That(SceneParallaxInput.SoftClampAxis(-2f), Is.EqualTo(-1f));

            Vector2 halfScaleOrbit = DeviceMotionOrbitMapping.ResolveOrbitDegrees(
                new Vector2(0.5f, 0f),
                16f);
            Vector2 fullScaleOrbit = DeviceMotionOrbitMapping.ResolveOrbitDegrees(
                Vector2.right,
                16f);
            Vector2 continuedOrbit = DeviceMotionOrbitMapping.ResolveOrbitDegrees(
                Vector2.right * 2f,
                16f);
            Vector2 fartherOrbit = DeviceMotionOrbitMapping.ResolveOrbitDegrees(
                Vector2.right * 4f,
                16f);
            Assert.That(halfScaleOrbit.x, Is.EqualTo(8f).Within(0.0001f));
            Assert.That(fullScaleOrbit.x, Is.EqualTo(16f).Within(0.0001f));
            Assert.That(continuedOrbit.x, Is.GreaterThan(fullScaleOrbit.x));
            Assert.That(fartherOrbit.x, Is.GreaterThan(continuedOrbit.x));
            Assert.That(
                fartherOrbit.x,
                Is.LessThan(DeviceMotionOrbitMapping.MaximumContinuedOrbitDegrees));
            Assert.That(
                DeviceMotionOrbitMapping.ResolveOrbitDegrees(
                    Vector2.left * 4f,
                    16f).x,
                Is.EqualTo(-fartherOrbit.x).Within(0.0001f));

            Quaternion justBeforePole =
                DeviceMotionOrbitMapping.ResolveStableLookRotation(
                    Vector3.back,
                    Quaternion.Euler(89.9f, 0f, 0f));
            Quaternion justAfterPole =
                DeviceMotionOrbitMapping.ResolveStableLookRotation(
                    Vector3.back,
                    Quaternion.Euler(90.1f, 0f, 0f));
            Assert.That(
                Quaternion.Angle(justBeforePole, justAfterPole),
                Is.LessThan(0.25f),
                "Crossing the top-down camera pole must remain continuous.");
            Assert.That(
                Vector3.Dot(
                    justBeforePole * Vector3.up,
                    justAfterPole * Vector3.up),
                Is.GreaterThan(0.999f),
                "Camera up must not switch hemispheres at the motion threshold.");

            float hoverPeakTime = 1f
                / (SpinnerSceneParallaxController.LibraryHoverCyclesPerSecond * 4f);
            Assert.That(
                SpinnerSceneParallaxController.ResolveLibraryHoverPixels(
                    0f,
                    false,
                    false),
                Is.EqualTo(0f));
            Assert.That(
                SpinnerSceneParallaxController.ResolveLibraryHoverPixels(
                    0f,
                    true,
                    true),
                Is.EqualTo(SpinnerSceneParallaxController.LibraryHoverBasePixels));
            Assert.That(
                SpinnerSceneParallaxController.ResolveLibraryHoverPixels(
                    hoverPeakTime,
                    true,
                    false),
                Is.EqualTo(
                    SpinnerSceneParallaxController.LibraryHoverBasePixels
                    + SpinnerSceneParallaxController.LibraryHoverAmplitudePixels)
                    .Within(0.0001f));
            Assert.That(
                SpinnerSceneParallaxController.ResolveLibraryHoverNormalized(
                    hoverPeakTime,
                    true,
                    false),
                Is.EqualTo(1f).Within(0.0001f));
            Assert.That(
                SpinnerSceneParallaxController.ResolveLibraryPageProjectionPixels(
                    -1f,
                    900f),
                Is.EqualTo(972f).Within(0.0001f),
                "A logical left exit needs positive perspective projection pixels.");
            Assert.That(
                SpinnerSceneParallaxController.ResolveLibraryPageProjectionPixels(
                    1f,
                    900f),
                Is.EqualTo(-972f).Within(0.0001f),
                "A logical right entrance needs negative perspective projection pixels.");
            Assert.That(
                FidgetAppCoordinator.ResolveLibraryPageDirection(
                    ProductCatalog.PointedThreeBladeModelId,
                    ProductCatalog.MetalThreeBladeModelId),
                Is.EqualTo(1f));
            Assert.That(
                FidgetAppCoordinator.ResolveLibraryPageDirection(
                    ProductCatalog.GraphiteTwoLobeModelId,
                    ProductCatalog.GoldFourWingModelId),
                Is.EqualTo(-1f));
            Assert.That(
                FidgetAppCoordinator.ResolveLibraryPageDirection(
                    ProductCatalog.MagneticSlideTileModelId,
                    ProductCatalog.MagneticSlideTileModelId),
                Is.EqualTo(0f));

            Assert.That(
                SpinnerEnvironmentPresenter.ResolveLocalLayerPixels(
                    false,
                    SpinnerSceneParallaxController.AnchorLayerPixels,
                    SpinnerSceneParallaxController.FarLayerPixels,
                    true),
                Is.EqualTo(22f));
            Assert.That(
                SpinnerEnvironmentPresenter.ResolveLocalLayerPixels(
                    false,
                    SpinnerSceneParallaxController.AnchorLayerPixels,
                    SpinnerSceneParallaxController.RightForegroundPixels,
                    false),
                Is.EqualTo(-8f));
            Assert.That(
                SpinnerEnvironmentPresenter.ResolveLocalLayerPixels(
                    false,
                    SpinnerSceneParallaxController.AnchorLayerPixels,
                    SpinnerSceneParallaxController.LeftForegroundPixels,
                    false),
                Is.EqualTo(-16f));

            Matrix4x4 perspective = Matrix4x4.identity;
            Matrix4x4 shifted = SpinnerSceneParallaxController.OffsetProjection(
                perspective,
                false,
                new Vector2(20f, -20f),
                new Vector2(1000f, 2000f));
            Assert.That(shifted.m02, Is.EqualTo(0.04f).Within(0.0001f));
            Assert.That(shifted.m12, Is.EqualTo(-0.02f).Within(0.0001f));
            Assert.That(shifted.m03, Is.EqualTo(0f));
            Assert.That(shifted.m13, Is.EqualTo(0f));
        }

        private static void AssertColor(Color actual, Color expected)
        {
            Assert.That(actual.r, Is.EqualTo(expected.r).Within(0.0001f));
            Assert.That(actual.g, Is.EqualTo(expected.g).Within(0.0001f));
            Assert.That(actual.b, Is.EqualTo(expected.b).Within(0.0001f));
            Assert.That(actual.a, Is.EqualTo(expected.a).Within(0.0001f));
        }

        private static void AssertViewportBoundary(
            string label,
            Camera camera,
            Transform target,
            float widthFraction,
            float heightFraction,
            float minimumFillRatio)
        {
            Assert.That(camera, Is.Not.Null, label);
            Assert.That(target, Is.Not.Null, label);
            Assert.That(
                ProductCameraFraming.TryGetProductBounds(target, out Bounds bounds),
                Is.True,
                label);
            Vector2 projected = ProductCameraFraming.ProjectedViewportSize(
                camera,
                bounds);
            Assert.That(
                projected.x,
                Is.LessThanOrEqualTo(widthFraction + 0.03f),
                label + " must stay inside its horizontal boundary.");
            Assert.That(
                projected.y,
                Is.LessThanOrEqualTo(heightFraction + 0.03f),
                label + " must stay inside its vertical boundary.");
            Assert.That(
                Mathf.Max(
                    projected.x / widthFraction,
                    projected.y / heightFraction),
                Is.InRange(minimumFillRatio, 1.03f),
                label + " should fill its authored live or full-sweep framing boundary.");
        }

        private static void AssertBackgroundCoversViewport(
            Camera camera,
            Transform background,
            string modelId,
            float minimumMargin = 0f)
        {
            Vector3[] localCorners =
            {
                new Vector3(-0.5f, -0.5f, 0f),
                new Vector3(0.5f, -0.5f, 0f),
                new Vector3(-0.5f, 0.5f, 0f),
                new Vector3(0.5f, 0.5f, 0f)
            };
            Vector3[] viewportCorners = localCorners
                .Select(corner => camera.WorldToViewportPoint(
                    background.TransformPoint(corner)))
                .ToArray();

            Assert.That(viewportCorners.Min(corner => corner.x),
                Is.LessThanOrEqualTo(0.001f - minimumMargin), modelId);
            Assert.That(viewportCorners.Max(corner => corner.x),
                Is.GreaterThanOrEqualTo(0.999f + minimumMargin), modelId);
            Assert.That(viewportCorners.Min(corner => corner.y),
                Is.LessThanOrEqualTo(0.001f - minimumMargin), modelId);
            Assert.That(viewportCorners.Max(corner => corner.y),
                Is.GreaterThanOrEqualTo(0.999f + minimumMargin), modelId);
            Assert.That(viewportCorners.All(corner => corner.z > 0f), Is.True, modelId);
        }
    }
}
