using System.IO;
using System.Linq;
using CodexUnityLab;
using FidgetingApp.EDC;
using FidgetingApp.FanCard;
using FidgetingApp.Product;
using NUnit.Framework;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class ProductArchitectureTests
    {
        private const string CanonicalBundleIdentifier =
            "com.jiaweizhou.fidgetspinner.codex";

        [Test]
        public void BuildContainsAllSixFidgetModelsInOneProduct()
        {
            string[] scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray();

            CollectionAssert.AreEqual(
                new[]
                {
                    "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity",
                    "Assets/Scenes/FidgetSpinnerDemo.unity",
                    "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity",
                    "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity",
                    "Assets/_EDC/Scenes/MeshyEDC.unity",
                    "Assets/_FanCard/Scenes/MagneticFanCard.unity"
                },
                scenes);
        }

        [Test]
        public void DragonScaleThreeBladeOwnsThePrimaryCatalogSlotAcrossUnityAndNativeUi()
        {
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string buildPipeline = File.ReadAllText(
                "Assets/Editor/IosBuildPipeline.cs");

            Assert.That(
                swift.IndexOf("case metalThreeBlade = \"metal-three-blade\""),
                Is.LessThan(swift.IndexOf("case blueClassic = \"blue-classic\"")),
                "The Dragon Scale model must be the first native library page.");
            StringAssert.Contains(
                "static let primaryModelCatalogVersion = \"fidgeting.primaryModelCatalogVersion\"",
                swift,
                "Existing installs need a one-time migration away from the retired first slot.");
            StringAssert.Contains("? .metalThreeBlade", swift);
            StringAssert.Contains(
                "new SpinnerProgressionRuntime(MetalModelId)",
                coordinator);
            StringAssert.Contains(
                "new CollectorProgressionRuntime(MetalModelId)",
                coordinator);

            int productOrder = coordinator.IndexOf(
                "MetalModelId,\n            BlueModelId,");
            Assert.That(productOrder, Is.GreaterThanOrEqualTo(0));
            int sceneOrder = buildPipeline.IndexOf(
                "MetalScenePath,\n            BlueScenePath,");
            Assert.That(sceneOrder, Is.GreaterThanOrEqualTo(0));

            string[] scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray();
            Assert.That(
                scenes.First(),
                Is.EqualTo("Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity"),
                "The shipping app must boot directly into the replacement first spinner.");
        }

        [Test]
        public void NativeOverlayInstallIsApplicationBootstrappedAndDoesNotDependOnTheBlueScene()
        {
            string controller = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/IosSwiftUiOverlayController.cs");
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string buildPipeline = File.ReadAllText(
                "Assets/Editor/IosBuildPipeline.cs");
            string[] scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray();

            Assert.That(
                scenes.First(),
                Is.Not.EqualTo("Assets/Scenes/FidgetSpinnerDemo.unity"),
                "This regression only stays covered while the app boots outside the legacy scene.");
            StringAssert.Contains(
                "[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]",
                controller);
            StringAssert.Contains("InstallAtApplicationStartup", controller);
            StringAssert.Contains("CodexSwiftUiOverlayInstall();", controller);
            StringAssert.Contains("func install(retryCount: Int = 0)", swift);
            StringAssert.Contains("guard retryCount < 12 else { return }", swift);
            StringAssert.Contains("self?.install(retryCount: retryCount + 1)", swift);
            StringAssert.Contains(
                "PlayerSettings.iOS.simulatorSdkArchitecture =\n" +
                "                    AppleMobileArchitectureSimulator.ARM64;",
                buildPipeline);
            StringAssert.Contains("PlayerSettings.iOS.buildNumber = \"21\";", buildPipeline);
        }

        [Test]
        public void BuildContainsAllFourSpinnerModelsInOneProduct()
        {
            string[] scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray();

            CollectionAssert.IsSubsetOf(
                new[]
                {
                    "Assets/Scenes/FidgetSpinnerDemo.unity",
                    "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity",
                    "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity",
                    "Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity"
                },
                scenes,
                "Adding the EDC must not remove any of the four existing spinners.");
        }

        [Test]
        public void RotarySpeedDashboardAndComboPipelineUseCanonicalSources()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = File.ReadAllText(
                "Assets/Plugins/iOS/FidgetProductUIComponents.swift");

            StringAssert.Contains(
                "DontDestroyOnLoad(bridge)",
                coordinator,
                "The combo coordinator must survive all product-scene changes.");
            StringAssert.Contains(
                "blueSpinner.SpinGestureCompleted += HandleSpinGestureCompleted",
                coordinator);
            StringAssert.Contains(
                "metalGestures.SpinGestureCompleted += HandleSpinGestureCompleted",
                coordinator);
            StringAssert.Contains(
                "edcSlider.InteractionGestureCompleted += HandleSpinGestureCompleted",
                coordinator);
            StringAssert.Contains(
                "SpinnerComboNativeBridge.Publish(combo.Snapshot, angularSpeed)",
                coordinator);
            StringAssert.Contains(
                "rootView: SpinnerExperienceFeedbackLayer(state: state)",
                swift,
                "The speed dashboard must belong to the shared product shell.");
            StringAssert.Contains("SpinnerMetricCluster", swift);
            StringAssert.Contains("ProductSpeedDashboard(", swift);
            StringAssert.Contains("struct ProductSpeedDashboard", components);
            StringAssert.Contains("ProductSideMetricDashboard(", swift);
            StringAssert.Contains("struct ProductSideMetricDashboard", components);
            StringAssert.Contains("ProductDashboardSweepField", components);
            StringAssert.DoesNotContain("ProductDashboardNeedle", components);
            StringAssert.DoesNotContain("ProductDashboardFlames", components);
            StringAssert.Contains("private struct ProductDashboardCaption", components);
            StringAssert.Contains(".frame(height: 20)", components);
            StringAssert.Contains("isPeak: telemetry.speedBand == .peak", swift);
            StringAssert.Contains("ProductOverlayLayout.feedbackBottomClearance", swift);
            StringAssert.Contains("ProductMotionTelemetryNativeBridge.Publish", coordinator);
            StringAssert.Contains("HasRotarySpeedTelemetry()", coordinator);
            StringAssert.DoesNotContain("AutomotiveMetricGauge", swift);

            Assert.That(SpinnerEnvironmentCatalog.Profiles.Count, Is.EqualTo(6));
            foreach (SpinnerEnvironmentProfile profile in SpinnerEnvironmentCatalog.Profiles)
            {
                EditorSceneManager.OpenScene(profile.ScenePath, OpenSceneMode.Single);
                if (profile.ScenePath == SpinnerEnvironmentCatalog.BlueScenePath)
                {
                    Assert.That(
                        Object.FindAnyObjectByType<FidgetSpinnerController>(),
                        Is.Not.Null,
                        $"{profile.ModelId} must publish completed gestures to the gauges.");
                    continue;
                }

                if (profile.ScenePath == SpinnerEnvironmentCatalog.EdcScenePath)
                {
                    Assert.That(
                        Object.FindAnyObjectByType<EdcSliderController>(),
                        Is.Not.Null,
                        "The fifth product keeps its slide mechanism without mislabeling activity as RPM.");
                    Assert.That(
                        Object.FindAnyObjectByType<SharedPresentationGestureController>(),
                        Is.Not.Null,
                        "The fifth product must share pinch, zoom and orbit presentation gestures.");
                    continue;
                }

                if (profile.ScenePath == SpinnerEnvironmentCatalog.FanCardScenePath)
                {
                    Assert.That(
                        Object.FindAnyObjectByType<FanCardController>(),
                        Is.Not.Null,
                        "The sixth product keeps its fan-card mechanism without mislabeling activity as RPM.");
                    Assert.That(
                        Object.FindAnyObjectByType<SharedPresentationGestureController>(),
                        Is.Not.Null,
                        "The sixth product must share pinch, zoom and orbit presentation gestures.");
                    continue;
                }

                Assert.That(
                    Object.FindAnyObjectByType<MobileGestureController>(),
                    Is.Not.Null,
                    $"{profile.ModelId} must publish completed gestures to the gauges.");
                Assert.That(
                    Object.FindAnyObjectByType<RotorRigidbodyController>(),
                    Is.Not.Null,
                    $"{profile.ModelId} must provide real angular speed to the Speed gauge.");
            }
        }

        [Test]
        public void ImportedThirdSpinnerUsesOptimizedRuntimeMeshAndCanonicalInteraction()
        {
            const string sourceModel =
                "Assets/_ImportedSpinner/Models/ImportedSpinner.fbx";
            const string runtimeModel =
                "Assets/_ImportedSpinner/Models/ImportedSpinner_Runtime.obj";
            const string scenePath =
                "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity";
            const string mirrorStudio =
                "Assets/_ImportedSpinner/Materials/C_ImportedSpinnerMirrorStudio.asset";
            const string baseColor =
                "Assets/_ImportedSpinner/Textures/texture_pbr_20250901.png";
            const string normal =
                "Assets/_ImportedSpinner/Textures/texture_pbr_20250901_normal.png";
            const string metallicSmoothness =
                "Assets/_ImportedSpinner/Textures/texture_pbr_20250901_metallic_smoothness.png";

            Assert.That(File.Exists(sourceModel), Is.True);
            Assert.That(File.Exists(runtimeModel), Is.True);
            Assert.That(File.Exists(scenePath), Is.True);
            Assert.That(File.Exists(mirrorStudio), Is.True);
            Assert.That(File.Exists(baseColor), Is.True);
            Assert.That(File.Exists(normal), Is.True);
            Assert.That(File.Exists(metallicSmoothness), Is.True);

            string[] dependencies = AssetDatabase.GetDependencies(scenePath, true);
            CollectionAssert.Contains(dependencies, runtimeModel);
            CollectionAssert.Contains(dependencies, mirrorStudio);
            CollectionAssert.DoesNotContain(
                dependencies,
                baseColor,
                "Mirror steel must not reintroduce baked color, grain or surface noise.");
            CollectionAssert.DoesNotContain(dependencies, normal);
            CollectionAssert.DoesNotContain(dependencies, metallicSmoothness);
            CollectionAssert.DoesNotContain(
                dependencies,
                sourceModel,
                "The 1.5M-triangle source FBX must never enter the shipping scene.");

            Mesh[] runtimeMeshes = AssetDatabase.LoadAllAssetsAtPath(runtimeModel)
                .OfType<Mesh>()
                .ToArray();
            Assert.That(runtimeMeshes, Is.Not.Empty);
            ModelImporter runtimeImporter = AssetImporter.GetAtPath(runtimeModel) as ModelImporter;
            Assert.That(runtimeImporter, Is.Not.Null);
            Assert.That(
                runtimeImporter.meshCompression,
                Is.EqualTo(ModelImporterMeshCompression.Off),
                "Mirror steel must keep full vertex precision so reflections stay smooth.");
            Assert.That(
                runtimeImporter.normalCalculationMode,
                Is.EqualTo(ModelImporterNormalCalculationMode.AreaAndAngleWeighted));
            Assert.That(
                runtimeImporter.normalSmoothingSource,
                Is.EqualTo(ModelImporterNormalSmoothingSource.FromAngle));
            Assert.That(
                runtimeMeshes.All(mesh => mesh.normals.Length == mesh.vertexCount),
                Is.True,
                "The welded mirror mesh must retain smooth per-vertex normals.");
            int triangleCount = runtimeMeshes.Sum(mesh =>
                Enumerable.Range(0, mesh.subMeshCount)
                    .Sum(submesh => (int)(mesh.GetIndexCount(submesh) / 3)));
            Assert.That(triangleCount, Is.InRange(150000, 200000));

            EditorSceneManager.OpenScene(scenePath);
            GameObject root = GameObject.Find("ImportedSpinner_Root");
            Assert.That(root, Is.Not.Null);
            Transform rotor = root.transform.Find("RotorDynamic");
            Assert.That(rotor, Is.Not.Null);
            Assert.That(rotor.GetComponent<RotorRigidbodyController>(), Is.Not.Null);
            Assert.That(rotor.GetComponent<SpinnerTouchSurface>(), Is.Not.Null);
            Assert.That(rotor.GetComponent<BoxCollider>(), Is.Not.Null);
            Assert.That(root.GetComponent<MobileGestureController>(), Is.Not.Null);
            OrbitPresentationCamera camera =
                Object.FindAnyObjectByType<OrbitPresentationCamera>();
            Assert.That(camera, Is.Not.Null);
            Camera cameraComponent = camera.GetComponent<Camera>();
            cameraComponent.aspect = 1290f / 2796f;
            ProductFramingProfile framing = ProductFramingCatalog.Resolve(scenePath);
            camera.ConfigureFraming(framing);
            camera.ResetHero();
            Assert.That(
                ProductCameraFraming.TryGetProductBounds(camera.Target, out Bounds bounds),
                Is.True);
            Vector2 projectedSize = ProductCameraFraming.ProjectedViewportSize(
                cameraComponent,
                bounds);
            Assert.That(projectedSize.x, Is.LessThanOrEqualTo(framing.DetailWidthFraction + 0.03f));
            Assert.That(projectedSize.y, Is.LessThanOrEqualTo(framing.DetailHeightFraction + 0.03f));
            Assert.That(
                Mathf.Max(
                    projectedSize.x / framing.DetailWidthFraction,
                    projectedSize.y / framing.DetailHeightFraction),
                Is.InRange(0.90f, 1.03f),
                "The live renderer bounds should fill one detail boundary, not a fixed authored distance.");
            Assert.That(Object.FindAnyObjectByType<MetalRatchetDetentAudio>(), Is.Null);
            Transform visual = rotor.Find("ImportedSpinnerVisual");
            Assert.That(visual, Is.Not.Null);
            Renderer mirrorRenderer = visual.GetComponentInChildren<Renderer>();
            Assert.That(mirrorRenderer, Is.Not.Null);
            Material mirrorMaterial = mirrorRenderer.sharedMaterial;
            Assert.That(mirrorMaterial, Is.Not.Null);
            Assert.That(mirrorMaterial.name, Is.EqualTo("M_ImportedSpinnerMirrorSteel"));
            Assert.That(mirrorMaterial.GetTexture("_BaseMap"), Is.Null);
            Assert.That(mirrorMaterial.GetTexture("_BumpMap"), Is.Null);
            Assert.That(mirrorMaterial.GetTexture("_MetallicGlossMap"), Is.Null);
            Assert.That(mirrorMaterial.GetFloat("_Metallic"), Is.EqualTo(1f));
            Assert.That(mirrorMaterial.GetFloat("_Smoothness"), Is.EqualTo(0.95f));
            Color steel = mirrorMaterial.GetColor("_BaseColor");
            Assert.That(Mathf.Abs(steel.r - steel.g), Is.LessThan(0.03f));
            Assert.That(Mathf.Abs(steel.g - steel.b), Is.LessThan(0.04f));
            Assert.That(mirrorMaterial.IsKeywordEnabled("_NORMALMAP"), Is.False);
            Assert.That(mirrorMaterial.IsKeywordEnabled("_METALLICSPECGLOSSMAP"), Is.False);
            Assert.That(
                mirrorRenderer.reflectionProbeUsage,
                Is.EqualTo(UnityEngine.Rendering.ReflectionProbeUsage.BlendProbes));
            Assert.That(RenderSettings.customReflectionTexture, Is.Not.Null);
            Assert.That(
                RenderSettings.customReflectionTexture.name,
                Is.EqualTo("C_ImportedSpinnerMirrorStudio"));
            Assert.That(RenderSettings.reflectionIntensity, Is.EqualTo(0.9f).Within(0.001f));
            Assert.That(rotor.GetComponent<Rigidbody>().angularVelocity, Is.EqualTo(Vector3.zero));
        }

        [Test]
        public void ProductIdentityCannotDriftToStandaloneMetalApp()
        {
            Assert.That(
                PlayerSettings.GetApplicationIdentifier(NamedBuildTarget.iOS),
                Is.EqualTo(CanonicalBundleIdentifier));
            Assert.That(
                File.Exists("Assets/_Fidgeting/Editor/IOSBuildPipeline.cs"),
                Is.False,
                "The standalone metal model build pipeline must not enter the product project.");

            string optimizationBuild = File.ReadAllText(
                "Assets/_EDC/Tests/OptimizationValidation/Editor/EdcOptimizationIosBuild.cs");
            StringAssert.Contains(
                "com.jiaweizhou.fidgetspinner.codex.edcopt",
                optimizationBuild);
            StringAssert.DoesNotContain(
                "CanonicalSigningBundleIdentifier",
                optimizationBuild,
                "An isolated EDC validation build must never sign as the shipping app.");
        }

        [Test]
        public void NativeBridgeHasOneStableProductObjectName()
        {
            Assert.That(FidgetAppCoordinator.BridgeObjectName, Is.EqualTo("FidgetApp"));
        }

        [Test]
        public void SettingsPanelSeparatesProductControlsFromSemanticCoreHapticsEditor()
        {
            string source = File.ReadAllText("Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string[] productControls =
            {
                "title: \"其他事件力度\"",
                "title: \"其他事件锐度\"",
                "title: \"拖动响应\"",
                "title: \"惯性阻力\"",
                "Label(\"棘轮咬合\""
            };

            foreach (string control in productControls)
            {
                StringAssert.Contains(control, source);
            }

            StringAssert.Contains("触觉映射 · 高级", source);
            StringAssert.Contains("Label(\"脉冲节奏\"", source);
            StringAssert.Contains("title: \"速度调制\"", source);
            StringAssert.Contains("if state.interactionMode == .ratchet", source);
            StringAssert.DoesNotContain("title: \"跟手灵敏度\"", source);
            StringAssert.DoesNotContain("title: \"旋转阻力\"", source);
            StringAssert.DoesNotContain("title: \"速度跟随\"", source);

            string[] advancedControls =
            {
                "Core Haptics · 事件配方",
                "事件力度 Intensity",
                "事件锐度 Sharpness",
                "持续时间 Duration",
                "起振 Attack",
                "衰落 Decay",
                "释振 Release",
                "保持 Sustained",
                "动态力度",
                "动态锐度",
                "动态 Attack",
                "动态 Decay",
                "动态 Release"
            };

            foreach (string control in advancedControls)
            {
                StringAssert.Contains(control, source);
            }

            StringAssert.DoesNotContain("title: \"段落密度\"", source);
            StringAssert.Contains("private struct DetentTuningPanel: View", source);
            StringAssert.Contains("SetDetentFeelPresetFromNativeUi", source);
            StringAssert.Contains("SetDetentIntensityOverrideFromNativeUi", source);
            StringAssert.Contains("SetDetentSharpnessOverrideFromNativeUi", source);
            StringAssert.Contains("EditableHapticSemantic.generalTuningCases", source);
            StringAssert.Contains("DETENT LAB 独占", source);
            StringAssert.Contains("SetRatchetFeelFromNativeUi", source);
            StringAssert.Contains("SetSpinResponseFromNativeUi", source);
            StringAssert.Contains("SetSpinResistanceFromNativeUi", source);
            StringAssert.Contains("SetHapticRecipeOverrideFromNativeUi", source);
            StringAssert.Contains("PreviewHapticRecipeFromNativeUi", source);
        }

        [Test]
        public void MotionSensitivityPresetsAreMonotonicSharedAndVisibleInSettings()
        {
            FidgetMotionSensitivityProfile low =
                FidgetMotionSensitivityPresetCatalog.Resolve(
                    FidgetMotionSensitivityPreset.Low);
            FidgetMotionSensitivityProfile medium =
                FidgetMotionSensitivityPresetCatalog.Resolve(
                    FidgetMotionSensitivityPreset.Medium);
            FidgetMotionSensitivityProfile high =
                FidgetMotionSensitivityPresetCatalog.Resolve(
                    FidgetMotionSensitivityPreset.High);

            Assert.That(low.MaximumInputAngle, Is.EqualTo(18f).Within(0.0001f));
            Assert.That(low.MotionResponse, Is.EqualTo(8f).Within(0.0001f));
            Assert.That(low.GyroscopeLead, Is.EqualTo(0.035f).Within(0.0001f));
            Assert.That(low.MaximumMotionOrbit, Is.EqualTo(6.5f).Within(0.0001f));
            Assert.That(medium.MaximumInputAngle, Is.EqualTo(10f).Within(0.0001f));
            Assert.That(medium.MotionResponse, Is.EqualTo(15f).Within(0.0001f));
            Assert.That(medium.GyroscopeLead, Is.EqualTo(0.06f).Within(0.0001f));
            Assert.That(medium.MaximumMotionOrbit, Is.EqualTo(11f).Within(0.0001f));
            Assert.That(high.MaximumInputAngle, Is.EqualTo(7f).Within(0.0001f));
            Assert.That(high.MotionResponse, Is.EqualTo(22f).Within(0.0001f));
            Assert.That(high.GyroscopeLead, Is.EqualTo(0.10f).Within(0.0001f));
            Assert.That(high.MaximumMotionOrbit, Is.EqualTo(16f).Within(0.0001f));

            Assert.That(low.MaximumInputAngle, Is.GreaterThan(medium.MaximumInputAngle));
            Assert.That(medium.MaximumInputAngle, Is.GreaterThan(high.MaximumInputAngle));
            Assert.That(low.MotionResponse, Is.LessThan(medium.MotionResponse));
            Assert.That(medium.MotionResponse, Is.LessThan(high.MotionResponse));
            Assert.That(low.GyroscopeLead, Is.LessThan(medium.GyroscopeLead));
            Assert.That(medium.GyroscopeLead, Is.LessThan(high.GyroscopeLead));
            Assert.That(low.MaximumMotionOrbit, Is.LessThan(medium.MaximumMotionOrbit));
            Assert.That(medium.MaximumMotionOrbit, Is.LessThan(high.MaximumMotionOrbit));

            string nativeUi = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            StringAssert.Contains("Label(\"陀螺仪灵敏度\"", nativeUi);
            StringAssert.Contains("MotionSensitivityPreset.allCases", nativeUi);
            StringAssert.Contains("Input Angle 是反向参数", nativeUi);
            StringAssert.Contains(
                "SetMotionSensitivityPresetFromNativeUi",
                nativeUi);
            StringAssert.Contains(
                "public void SetMotionSensitivityPresetFromNativeUi",
                coordinator);
            StringAssert.Contains("edcMotion?.ResetReference();", coordinator);
            StringAssert.DoesNotContain("Rigidbody", nativeUi.Substring(
                nativeUi.IndexOf("private enum MotionSensitivityPreset"),
                nativeUi.IndexOf("private enum SpinnerModel")
                    - nativeUi.IndexOf("private enum MotionSensitivityPreset")));
        }

        [Test]
        public void InteractionControllersRouteSemanticEventsInsteadOfCallingIosRenderer()
        {
            string metalGestures = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Interaction/MobileGestureController.cs");
            string classicSpinner = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/FidgetSpinnerController.cs");

            StringAssert.DoesNotContain("IosHaptics.", metalGestures);
            StringAssert.DoesNotContain("IosHaptics.", classicSpinner);
            StringAssert.Contains("FidgetHapticRouter.Emit", metalGestures);
            StringAssert.Contains("FidgetHapticRouter.Emit", classicSpinner);
        }

        [Test]
        public void InteractionTabsResolveToSmoothAndMechanicalPresets()
        {
            FidgetInteractionPreset smooth = FidgetAppCoordinator.ResolveInteractionPreset(
                FidgetInteractionMode.Smooth);
            FidgetInteractionPreset ratchet = FidgetAppCoordinator.ResolveInteractionPreset(
                FidgetInteractionMode.Ratchet);

            {
                Assert.That(smooth.RatchetFeel, Is.EqualTo(FidgetRatchetFeel.Freewheel));
                Assert.That(smooth.SpinResistance, Is.EqualTo(0.58f).Within(0.0001f));
                Assert.That(smooth.SpinResponse, Is.EqualTo(0.55f).Within(0.0001f));
                Assert.That(smooth.ClassicDetentHapticsEnabled, Is.False);
                Assert.That(smooth.HapticIntensity, Is.EqualTo(0.62f).Within(0.0001f));
                Assert.That(smooth.HapticFrequencyFeel, Is.EqualTo(0.62f).Within(0.0001f));

                Assert.That(ratchet.RatchetFeel, Is.EqualTo(FidgetRatchetFeel.Mechanical));
                Assert.That(
                    ratchet.DetentsPerTurn,
                    Is.EqualTo(DetentFeelPresetCatalog.Default.Config.DetentsPerRevolution));
                Assert.That(ratchet.SpinResponse, Is.EqualTo(0.48f).Within(0.0001f));
                Assert.That(ratchet.SpinResistance, Is.EqualTo(0.58f).Within(0.0001f));
                Assert.That(ratchet.ClassicDetentHapticsEnabled, Is.True);
                Assert.That(ratchet.HapticIntensity, Is.EqualTo(0.95f).Within(0.0001f));
                Assert.That(ratchet.HapticFrequencyFeel, Is.EqualTo(0.88f).Within(0.0001f));
            }

            FidgetAppCoordinator.ResolveRatchetFeel(
                ratchet.RatchetFeel,
                out ThreeBladeEDC.SpinnerResistanceMode resistance,
                out float breakaway,
                out float capture,
                out float snap);
            {
                Assert.That(
                    resistance,
                    Is.EqualTo(ThreeBladeEDC.SpinnerResistanceMode.MagneticDetent));
                Assert.That(breakaway, Is.EqualTo(2.2f).Within(0.0001f));
                Assert.That(capture, Is.EqualTo(1.2f).Within(0.0001f));
                Assert.That(snap, Is.EqualTo(16f).Within(0.0001f));
            }
        }

        [Test]
        public void NativeUiUsesLivePagedModelsLiquidGlassAndModeTabs()
        {
            string source = File.ReadAllText("Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = File.ReadAllText(
                "Assets/Plugins/iOS/FidgetProductUIComponents.swift");

            StringAssert.Contains("TabView(selection: Binding(", source);
            StringAssert.Contains("双指捏合控制放大缩小", source);
            StringAssert.Contains("ProductPageIndicator(", source);
            StringAssert.Contains("items.firstIndex(of: selection)", components);
            StringAssert.Contains("case goldFourWing = \"gold-four-wing\"", source);
            StringAssert.Contains("case .goldFourWing: return \"镜钢四翼\"", source);
            StringAssert.Contains("case graphiteTwoLobe = \"graphite-two-lobe\"", source);
            StringAssert.Contains("case .graphiteTwoLobe: return \"石墨双叶\"", source);
            StringAssert.Contains("case magneticSlideTile = \"magnetic-slide-tile\"", source);
            StringAssert.Contains("case .magneticSlideTile: return \"磁吸推牌\"", source);
            StringAssert.Contains("case magneticFanCard = \"magnetic-fan-card\"", source);
            StringAssert.Contains("case .magneticFanCard: return \"磁吸扇牌\"", source);
            StringAssert.Contains("setModeBarVisible(true)", source);
            StringAssert.DoesNotContain(
                "state.selectedModel != .magneticSlideTile",
                source);
            StringAssert.Contains("SetLibraryPreviewActiveFromNativeUi", source);
            StringAssert.Contains("private struct ProductModeBar: View", source);
            StringAssert.Contains("case smooth", source);
            StringAssert.Contains("case ratchet", source);
            StringAssert.Contains(
                "self == .smooth ? \"arrow.triangle.2.circlepath\" : \"gearshape.fill\"",
                source);
            StringAssert.Contains("symbol: { $0.symbol }", source);
            StringAssert.Contains("Image(systemName: symbol(option))", components);
            StringAssert.DoesNotContain("Label(mode.title, systemImage: mode.symbol)", source);
            StringAssert.Contains(".fixedSize()", components);
            StringAssert.Contains("Text(\"LV \\(state.displayedProgressionLevel)\")", source);
            StringAssert.Contains("Text(state.currentAppearanceName)", source);
            StringAssert.Contains(
                ".foregroundStyle(state.currentAppearanceAccent.opacity(0.78))",
                source);
            StringAssert.Contains("topDestinationButton(", source);
            StringAssert.DoesNotContain("info.circle", source);
            StringAssert.Contains("return \"Fidgeting\"", source);
            StringAssert.Contains("title: state.selectedModel.title", source);
            StringAssert.Contains(
                "subtitle: \"\\(state.currentAppearanceName) · LV.\\(state.displayedProgressionLevel)\"",
                source);
            int topBarStart = source.IndexOf("private struct ProductTopBar");
            int topBarEnd = source.IndexOf("private struct SpinnerOnboardingView");
            string topBar = source.Substring(topBarStart, topBarEnd - topBarStart);
            StringAssert.DoesNotContain("label: \"玩具\"", topBar);
            StringAssert.DoesNotContain("symbol: \"square.grid.2x2\"", topBar);
            StringAssert.Contains("symbol: \"gearshape\"", topBar);
            StringAssert.Contains("showMySpinners()", topBar);
            StringAssert.Contains("struct ProductSheetDragHandle", components);
            StringAssert.DoesNotContain("ProductSheetDragHandle(closeTitle: \"关闭面板\")", source);
            StringAssert.Contains("dismissPanelToSelectedModel", source);
            StringAssert.DoesNotContain("private struct ProductBottomBar: View", source);
            StringAssert.DoesNotContain("bottomController", source);
            StringAssert.Contains("safeAreaLayoutGuide.bottomAnchor", source);
            StringAssert.Contains("SetInteractionModeFromNativeUi", source);
            StringAssert.Contains(".glassEffect(", components);
            StringAssert.DoesNotContain("所有 3D 模型都在同一个 App 中，通过这里切换。", source);
        }

        [Test]
        public void NativeUiUsesBundledSquareArtworkForModelsSkinsAndStickers()
        {
            const string thumbnailRoot = "Assets/Plugins/iOS/Thumbnails";
            const string stickerRoot =
                "Assets/Resources/ProductStickers/BackdropWhite";
            string source = File.ReadAllText("Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string pipeline = File.ReadAllText("Assets/Editor/IosBuildPipeline.cs");

            string[] thumbnails = Directory.GetFiles(
                thumbnailRoot,
                "*.png",
                SearchOption.AllDirectories);
            Assert.That(thumbnails, Has.Length.EqualTo(16));

            string[] expectedNames =
            {
                "product-thumbnail-blue-classic.png",
                "product-thumbnail-metal-three-blade.png",
                "product-thumbnail-gold-four-wing.png",
                "product-thumbnail-graphite-two-lobe.png",
                "product-thumbnail-magnetic-slide-tile.png",
                "product-thumbnail-magnetic-fan-card.png",
                "skin-thumbnail-factory-silver.png",
                "skin-thumbnail-gunmetal-brush.png",
                "skin-thumbnail-night-cyan-index.png",
                "skin-thumbnail-tungsten-honeycomb.png",
                "skin-thumbnail-ice-guilloche.png",
                "skin-thumbnail-blue-damascus.png",
                "skin-thumbnail-copper-circuit.png",
                "skin-thumbnail-titanium-heat.png",
                "skin-thumbnail-meteor-obsidian.png",
                "skin-thumbnail-mirror-aurora.png"
            };
            CollectionAssert.AreEquivalent(
                expectedNames,
                thumbnails.Select(Path.GetFileName).ToArray());

            foreach (string thumbnailPath in thumbnails)
            {
                byte[] png = File.ReadAllBytes(thumbnailPath);
                Assert.That(png.Length, Is.GreaterThan(24), thumbnailPath);
                Assert.That(png[0], Is.EqualTo(0x89), thumbnailPath);
                Assert.That(png[1], Is.EqualTo(0x50), thumbnailPath);
                int width = (png[16] << 24) | (png[17] << 16) | (png[18] << 8) | png[19];
                int height = (png[20] << 24) | (png[21] << 16) | (png[22] << 8) | png[23];
                Assert.That(width, Is.EqualTo(512), thumbnailPath);
                Assert.That(height, Is.EqualTo(512), thumbnailPath);
            }

            string[] stickerThumbnails = Directory.GetFiles(
                stickerRoot,
                "*.png",
                SearchOption.TopDirectoryOnly);
            Assert.That(stickerThumbnails, Has.Length.EqualTo(24));
            CollectionAssert.AreEquivalent(
                ProductStickerCatalog.Stickers
                    .Skip(1)
                    .Select(sticker => sticker.ArtworkAssetName + ".png")
                    .ToArray(),
                stickerThumbnails.Select(Path.GetFileName).ToArray());
            foreach (string thumbnailPath in stickerThumbnails)
            {
                byte[] png = File.ReadAllBytes(thumbnailPath);
                Assert.That(png.Length, Is.GreaterThan(24), thumbnailPath);
                Assert.That(png[0], Is.EqualTo(0x89), thumbnailPath);
                Assert.That(png[1], Is.EqualTo(0x50), thumbnailPath);
                int width = (png[16] << 24) | (png[17] << 16) | (png[18] << 8) | png[19];
                int height = (png[20] << 24) | (png[21] << 16) | (png[22] << 8) | png[23];
                Assert.That(width, Is.EqualTo(1024), thumbnailPath);
                Assert.That(height, Is.EqualTo(1024), thumbnailPath);
            }

            StringAssert.Contains("var thumbnailAssetName: String", source);
            StringAssert.Contains("private struct NativeSquareArtwork: View", source);
            StringAssert.Contains("UIImage(named: assetName)", source);
            StringAssert.DoesNotContain("private struct SpinnerLibraryThumbnailTabBar: View", source);
            StringAssert.Contains(".tabViewStyle(.page(indexDisplayMode: .always))", source);
            StringAssert.Contains(".indexViewStyle(.page(backgroundDisplayMode: .never))", source);
            StringAssert.Contains("skin.thumbnailAssetName", source);
            StringAssert.Contains("sticker.thumbnailAssetName", source);
            StringAssert.Contains(".scaledToFit()", source);
            StringAssert.Contains(
                "ConfigureProductThumbnails(projectRoot, outputPath)",
                pipeline);
            StringAssert.Contains("ProductThumbnailAssetRootPath", pipeline);
            StringAssert.Contains("ProductStickerArtworkAssetRootPath", pipeline);
            StringAssert.Contains("project.AddFileToBuild(mainTarget, fileGuid)", pipeline);
        }

        [Test]
        public void CollectorRankIsCrossToyManualOnlyAndUsesARealBackButton()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string collector = File.ReadAllText(
                "Assets/Scripts/Product/CollectorProgression.cs");
            string progression = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerProgression.cs");
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");

            StringAssert.Contains("CollectorProgressionRuntime", coordinator);
            StringAssert.Contains("collectorProgression?.RecordGesture", coordinator);
            StringAssert.Contains("collectorProgression.RecordActivity", coordinator);
            StringAssert.Contains("SetCollectorFocusFromNativeUi", coordinator);
            StringAssert.Contains("CollectorProgressionNativeBridge.Publish", coordinator);
            StringAssert.Contains("ActiveBonusForModel", coordinator);
            StringAssert.Contains("collectorBonus", progression);
            StringAssert.Contains("MaximumManualExperienceMultiplier = 1.50d", collector);
            StringAssert.Contains("EffectiveDayInteractionSeconds = 60d", collector);
            StringAssert.Contains("RhythmRequiredDays = 5", collector);
            StringAssert.Contains("MaximumCollectionExperience = 900d", collector);
            StringAssert.DoesNotContain("OfflineExperience(", collector);

            StringAssert.Contains("case collector", swift);
            StringAssert.Contains("private struct CollectorProfile: View", swift);
            StringAssert.Contains("Text(\"藏家 · \\(state.collectorRank)\")", swift);
            StringAssert.Contains("Text(\"等级\").tag(0)", swift);
            StringAssert.Contains("Text(\"成就\").tag(1)", swift);
            StringAssert.Contains("Text(\"收藏\").tag(2)", swift);
            StringAssert.Contains("symbol: \"chevron.left\"", swift);
            StringAssert.Contains("accessibilityLabel: \"返回\"", swift);
            StringAssert.Contains("if showsBackButton", swift);
            StringAssert.Contains("label: \"藏家档案\"", swift);
            StringAssert.Contains("CodexSwiftUIOverlayManager.shared.showMySpinners()", swift);
            StringAssert.Contains("CodexCollectorReceiveState", swift);
            StringAssert.Contains("CollectorUnlockOverlay", swift);
        }

        [Test]
        public void NativeUiUsesReusableProductComponentLibrary()
        {
            string source = File.ReadAllText("Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = File.ReadAllText(
                "Assets/Plugins/iOS/FidgetProductUIComponents.swift");
            string guideline = File.ReadAllText("Docs/LiquidGlassDesignGuideline.md");

            StringAssert.Contains("enum FidgetUITokens", components);
            StringAssert.Contains("static let minimumHitTarget: CGFloat = 44", components);
            StringAssert.Contains("static let compactIconButton: CGFloat = 38", components);
            StringAssert.Contains("static let primaryActionHeight: CGFloat = 52", components);
            StringAssert.Contains("static let selectionDuration = 0.18", components);
            StringAssert.Contains("struct ProductGlassModifier", components);
            StringAssert.Contains(".background(.ultraThinMaterial, in: shape)", components);
            StringAssert.DoesNotContain("fallbackStroke", components);
            StringAssert.DoesNotContain("shape.stroke(", components);
            StringAssert.Contains("struct ProductIconButton", components);
            StringAssert.Contains("struct ProductIconSegmentedControl", components);
            StringAssert.Contains("struct ProductPageIndicator", components);
            StringAssert.Contains("struct ProductPrimaryActionLabel", components);
            StringAssert.Contains("struct ProductActionLabel", components);
            StringAssert.Contains("struct ProductSectionCard", components);
            StringAssert.Contains("struct ProductBottomSheetShell", components);
            StringAssert.Contains("struct ProductStatusPill", components);
            StringAssert.Contains("struct ProductProgressGauge", components);
            StringAssert.Contains("struct ProductSpeedDashboard", components);
            StringAssert.Contains("struct ProductSideMetricDashboard", components);
            StringAssert.Contains("struct ProductMetricCard", components);
            StringAssert.Contains("struct ProductScreenHeading", components);
            StringAssert.Contains("struct ProductInlineTag", components);
            StringAssert.Contains("struct ProductNoticeBanner", components);
            StringAssert.Contains("struct ProductSelectionCard", components);
            StringAssert.Contains("struct ProductBadgeTile", components);
            StringAssert.Contains("struct ProductCompactMetric", components);
            StringAssert.Contains("struct ProductSliderRow", components);
            StringAssert.Contains("struct ProductToggleRow", components);
            StringAssert.Contains("struct ProductEmptyState", components);

            StringAssert.Contains("ProductIconButton(", source);
            StringAssert.Contains("ProductIconSegmentedControl(", source);
            StringAssert.Contains("ProductPageIndicator(", source);
            StringAssert.Contains("ProductPrimaryActionLabel(", source);
            StringAssert.Contains("ProductActionLabel(", source);
            StringAssert.Contains("ProductSectionCard(", source);
            StringAssert.Contains("ProductBottomSheetShell(", source);
            StringAssert.Contains("ProductStatusPill(", source);
            StringAssert.Contains("ProductProgressGauge(", source);
            StringAssert.Contains("ProductSpeedDashboard(", source);
            StringAssert.Contains("ProductSideMetricDashboard(", source);
            StringAssert.Contains("ProductMetricCard(", source);
            StringAssert.Contains("ProductScreenHeading(", source);
            StringAssert.Contains("ProductInlineTag(", source);
            StringAssert.Contains("ProductNoticeBanner(", source);
            StringAssert.Contains("symbol: \"star.fill\"", source);
            StringAssert.Contains("ProductSelectionCard(", source);
            StringAssert.Contains("ProductBadgeTile(", source);
            StringAssert.Contains("ProductCompactMetric(", source);
            StringAssert.Contains("ProductSliderRow(", source);
            StringAssert.Contains("ProductToggleRow(", source);
            StringAssert.Contains("ProductEmptyState(", source);

            StringAssert.DoesNotContain("private struct ProductGlassModifier", source);
            StringAssert.DoesNotContain("private struct GlassActionLabel", source);
            StringAssert.DoesNotContain("private func settingsCard", source);
            StringAssert.DoesNotContain("UnityBridge", components);
            StringAssert.DoesNotContain("IosHaptics", components);
            StringAssert.DoesNotContain(".tracking(", source);
            StringAssert.DoesNotContain(".tracking(", components);
            StringAssert.DoesNotContain(".kerning(", source);
            StringAssert.DoesNotContain(".kerning(", components);
            StringAssert.Contains(".symbolVariant(.fill)", components);
            StringAssert.Contains(
                "Image(systemName: \"checkmark.circle.fill\")",
                components);
            StringAssert.Contains("禁止用 SwiftUI `tracking` / `kerning`", guideline);
            StringAssert.Contains(
                ".font(.product(.title3, weight: .bold).monospacedDigit())",
                components);
            StringAssert.Contains(
                "Metric 中的数字本身是视觉 headline",
                guideline);
            StringAssert.Contains(
                "跨两个以上业务界面重复的 heading、notice、tag、selection card、badge tile、metric、slider、toggle、empty state",
                guideline);
            StringAssert.Contains(
                "Liquid Glass 表面不使用周圈描边或 outline",
                guideline);
            StringAssert.Contains(
                "选中状态通过玻璃 tint / 亮度、tag 和 checkmark 表达",
                guideline);
            StringAssert.Contains(
                "Badge / 成就解锁通知固定使用实心 SF Symbol",
                guideline);
        }

        [Test]
        public void EntireProductUiUsesOxaniumAndTheSharedDesignSystem()
        {
            const string fontPath =
                "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf";
            const string fontLicensePath = "Assets/Plugins/iOS/Fonts/OFL.txt";
            const string fontGuid = "4acabaa33f32e44ff8de56b38dbcae31";
            string source = File.ReadAllText("Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = File.ReadAllText(
                "Assets/Plugins/iOS/FidgetProductUIComponents.swift");
            string pipeline = File.ReadAllText("Assets/Editor/IosBuildPipeline.cs");
            string builder = File.ReadAllText(
                "Assets/_Fidgeting/Editor/ThreeBladeSceneBuilder.cs");
            string metalScene = File.ReadAllText(
                "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity");
            string importedScene = File.ReadAllText(
                "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity");
            string guideline = File.ReadAllText("Docs/LiquidGlassDesignGuideline.md");

            Assert.That(File.Exists(fontPath), Is.True);
            Assert.That(new FileInfo(fontPath).Length, Is.GreaterThan(40000));
            Assert.That(File.Exists(fontLicensePath), Is.True);
            StringAssert.Contains("SIL OPEN FONT LICENSE", File.ReadAllText(fontLicensePath));

            StringAssert.Contains("static let familyName = \"Oxanium\"", components);
            StringAssert.Contains("CTFontManagerRegisterFontsForURL", components);
            StringAssert.Contains("static func product(", components);
            StringAssert.Contains("func productDesignSystem()", components);
            StringAssert.Contains("ProductTypography.configureUIKitAppearance()", source);
            Assert.That(
                source.Split(
                    new[] { "productDesignSystem()" },
                    System.StringSplitOptions.None).Length - 1,
                Is.GreaterThanOrEqualTo(7));

            string combinedSwiftUi = components + source;
            foreach (string forbiddenFont in new[]
                     {
                         ".font(.system",
                         ".font(.largeTitle",
                         ".font(.title",
                         ".font(.headline",
                         ".font(.body",
                         ".font(.callout",
                         ".font(.subheadline",
                         ".font(.footnote",
                         ".font(.caption"
                     })
            {
                StringAssert.DoesNotContain(forbiddenFont, combinedSwiftUi);
            }
            StringAssert.DoesNotContain("Color.cyan", combinedSwiftUi);
            StringAssert.DoesNotContain(".tint(.cyan)", combinedSwiftUi);

            StringAssert.Contains("ConfigureProductFont(projectRoot, outputPath)", pipeline);
            StringAssert.Contains("Oxanium-VariableFont_wght.ttf", pipeline);
            StringAssert.Contains("project.AddFileToBuild(mainTarget, fontGuid)", pipeline);
            StringAssert.Contains("CreateArray(\"UIAppFonts\")", pipeline);
            StringAssert.Contains(
                "AssetDatabase.LoadAssetAtPath<Font>(ProductFontPath)",
                builder);
            StringAssert.DoesNotContain("LegacyRuntime.ttf", builder);

            string fontReference =
                $"m_Font: {{fileID: 12800000, guid: {fontGuid}, type: 3}}";
            StringAssert.Contains(fontReference, metalScene);
            StringAssert.Contains(fontReference, importedScene);
            StringAssert.DoesNotContain(
                "m_Font: {fileID: 10102, guid: 0000000000000000e000000000000000, type: 0}",
                metalScene + importedScene);

            foreach (string scenePath in new[]
                     {
                         "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity",
                         "Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity"
                     })
            {
                EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
                UnityEngine.UI.Text[] labels = Object.FindObjectsByType<UnityEngine.UI.Text>(
                    FindObjectsInactive.Include,
                    FindObjectsSortMode.None);
                Assert.That(labels, Is.Not.Empty, $"{scenePath} must contain its legacy HUD labels.");
                Assert.That(
                    labels.All(label => label.font != null && label.font.name.Contains("Oxanium")),
                    Is.True,
                    $"Every legacy label in {scenePath} must use the canonical Oxanium asset.");
            }

            StringAssert.Contains("全 App 的拉丁字母与数字统一使用 Oxanium", guideline);
            StringAssert.Contains("业务层禁止固定 `Color.cyan`", guideline);
        }

        [Test]
        public void EntireProductUiDefaultsToDarkAppearance()
        {
            string source = File.ReadAllText("Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = File.ReadAllText(
                "Assets/Plugins/iOS/FidgetProductUIComponents.swift");
            string pipeline = File.ReadAllText("Assets/Editor/IosBuildPipeline.cs");
            string guideline = File.ReadAllText("Docs/LiquidGlassDesignGuideline.md");

            StringAssert.Contains("Color.black", components);
            StringAssert.Contains(".environment(\\.colorScheme, .dark)", components);
            StringAssert.Contains("UINavigationBar.appearance().barStyle = .black", components);
            StringAssert.Contains(".foregroundColor: UIColor.white", components);
            StringAssert.Contains("controller.overrideUserInterfaceStyle = .dark", source);
            StringAssert.DoesNotContain("rootController.overrideUserInterfaceStyle", source);
            StringAssert.DoesNotContain("window.overrideUserInterfaceStyle", source);
            StringAssert.Contains("private var showsLiveModelStage: Bool", source);
            StringAssert.Contains("if showsLiveModelStage", source);
            StringAssert.Contains("The library previews the live Unity renderer", source);
            StringAssert.Contains("plist.root.SetString(\"UIUserInterfaceStyle\", \"Dark\")", pipeline);
            StringAssert.Contains("全 App 固定使用 Dark Mode", guideline);
            StringAssert.Contains("模型库的 Unity 实时模型舞台必须保持透明", guideline);
        }

        [Test]
        public void MagneticSlideTileIsRoutedByTheCanonicalCoordinator()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");

            StringAssert.Contains(
                "private const string EdcModelId = \"magnetic-slide-tile\"",
                coordinator);
            StringAssert.Contains(
                "private const string EdcScenePath = SpinnerEnvironmentCatalog.EdcScenePath",
                coordinator);
            StringAssert.Contains("case EdcModelId:", coordinator);
            StringAssert.Contains("scenePath = EdcScenePath", coordinator);
            StringAssert.Contains("edcSlider.ResetToDefaultDetent()", coordinator);
            StringAssert.Contains(
                "environmentPresenter = SpinnerEnvironmentPresenter.Install(scenePath)",
                coordinator);
            StringAssert.Contains("edcSlider.ActivitySpeedRadians", coordinator);
            StringAssert.Contains("edcCamera?.SetLibraryPreviewActive", coordinator);
        }

        [Test]
        public void MagneticSlideUsesSpatialEdgeCuesAndFiniteCrossingTremor()
        {
            string controller = File.ReadAllText(
                "Assets/_EDC/Runtime/EdcSliderController.cs");
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string managed = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/IosHaptics.cs");
            string native = File.ReadAllText(
                "Assets/Plugins/iOS/CodexIosHaptics.mm");
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");

            StringAssert.Contains("SemanticEventRaised", controller);
            StringAssert.Contains("FidgetSemanticEvent.Breakaway", controller);
            StringAssert.Contains("FidgetSemanticEvent.DetentCrossed", controller);
            StringAssert.Contains("FidgetSemanticEvent.DetentCaptured", controller);
            StringAssert.Contains("FidgetSemanticEvent.MagneticEdgeProbe", controller);
            StringAssert.Contains("UpdateEdgeProbeMilestones", controller);
            StringAssert.Contains("BeginCrossingTremor(result.CrossingDirection)", controller);
            StringAssert.Contains("crossingTremorElapsed", controller);
            StringAssert.Contains("CrossingFrequencyHertz", controller);
            StringAssert.DoesNotContain("MagneticPreloadChanged", controller);
            StringAssert.DoesNotContain("IosHaptics", controller);

            StringAssert.Contains(
                "edcSlider.SemanticEventRaised += HandleEdcSemanticEvent",
                coordinator);
            StringAssert.Contains("FidgetHapticRouter.EmitMagneticSlider", coordinator);
            StringAssert.Contains("new MagneticSliderHapticTuning", coordinator);
            StringAssert.DoesNotContain("HandleEdcMagneticPreload", coordinator);
            StringAssert.DoesNotContain("UpdateMagneticPreload", coordinator);

            StringAssert.Contains("PlayMagneticEdgeProbeResolved", managed);
            StringAssert.Contains("PlayMagneticCrossingTremorResolved", managed);
            int magneticRendererStart = managed.IndexOf(
                "internal static void PlayMagneticEdgeProbeResolved");
            int magneticRendererEnd = managed.IndexOf(
                "internal static void PlayInertiaTransientResolved",
                magneticRendererStart);
            Assert.That(magneticRendererStart, Is.GreaterThanOrEqualTo(0));
            Assert.That(magneticRendererEnd, Is.GreaterThan(magneticRendererStart));
            string magneticRenderer = managed.Substring(
                magneticRendererStart,
                magneticRendererEnd - magneticRendererStart);
            StringAssert.Contains("CodexIosHapticsPlayMagneticEdgeProbe", magneticRenderer);
            StringAssert.Contains("CodexIosHapticsPlayMagneticCrossingTremor", magneticRenderer);
            StringAssert.DoesNotContain("StartMagneticPreloadContinuous", managed);
            StringAssert.DoesNotContain("UpdateMagneticPreloadContinuous", managed);
            StringAssert.DoesNotContain("MinimumMagneticSliderDetentInterval", managed);
            StringAssert.Contains("StopAllContinuous", managed);
            StringAssert.DoesNotContain("gMagneticPreloadPlayer", native);
            StringAssert.Contains(
                "CodexIosHapticsPlayMagneticEdgeProbe",
                native);
            StringAssert.Contains(
                "CodexIosHapticsPlayMagneticCrossingTremor",
                native);
            StringAssert.Contains("PlayMagneticCrossingTremorPattern", native);
            StringAssert.Contains("false,", native);
            StringAssert.Contains("view.isHidden = !visible", swift);
            StringAssert.Contains(
                "state.selectedModel == .magneticSlideTile",
                swift);
            StringAssert.Contains(
                "state.selectedModel == .magneticFanCard",
                swift);
        }

        [Test]
        public void AssistantDriveIsExplicitSharedAndStopsAtLifecycleBoundaries()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string classic = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/FidgetSpinnerController.cs");
            string rotor = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Interaction/RotorRigidbodyController.cs");
            string edc = File.ReadAllText(
                "Assets/_EDC/Runtime/EdcSliderController.cs");
            string progressionBridge = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerProgression.cs");
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");

            StringAssert.Contains("SetProgressionAssistantFromNativeUi", coordinator);
            StringAssert.Contains(
                "blueSpinner?.SetAssistantDrive(enabled, angularSpeed)",
                coordinator);
            StringAssert.Contains(
                "metalSpinner?.SetAssistantDrive(enabled, angularSpeed)",
                coordinator);
            StringAssert.Contains(
                "edcSlider?.SetAssistantDrive(enabled, sliderSpeed)",
                coordinator);
            StringAssert.Contains(
                "float assistantSpeedMultiplier",
                progressionBridge);
            StringAssert.Contains(
                "_ assistantSpeedMultiplier: Float",
                swift);
            StringAssert.Contains(
                "assistantMultiplier: Double(assistantSpeedMultiplier)",
                swift);
            StringAssert.Contains("StopAssistantDrive(true)", coordinator);
            StringAssert.Contains("private bool assistantDriveActive", classic);
            StringAssert.Contains("private bool _assistantDriveActive", rotor);
            StringAssert.Contains("private bool assistantDriveActive", edc);
            StringAssert.Contains("assistantDriveActive = false", classic);
            StringAssert.Contains("_assistantDriveActive = false", rotor);
            StringAssert.Contains("assistantDriveActive = false", edc);
            StringAssert.DoesNotContain("Mathf.Min(6f, maximumAngularSpeed)", classic);
            StringAssert.DoesNotContain("maxAngularSpeed * 0.5f", rotor);
            StringAssert.Contains("assistantTargetSpeedMetersPerSecond", edc);
            StringAssert.DoesNotContain(
                "const float targetSpeedMetersPerSecond = 0.030f",
                edc);
            StringAssert.Contains("pressedTouchCount >= 2", edc);
            StringAssert.Contains("shared pinch", edc);
        }

        [TestCase(1f, 2.2f, 0.030f)]
        [TestCase(1.5f, 3.3f, 0.045f)]
        [TestCase(2f, 4.4f, 0.060f)]
        [TestCase(3f, 6.6f, 0.090f)]
        public void AssistantDriveMultipliersScaleTheOneXBaseline(
            float requested,
            float expectedAngularSpeed,
            float expectedSliderSpeed)
        {
            Assert.That(
                AssistantDriveSpeedRules.TryResolveMultiplier(
                    requested,
                    out float resolved),
                Is.True);
            Assert.That(resolved, Is.EqualTo(requested).Within(0.0001f));
            Assert.That(
                AssistantDriveSpeedRules.AngularSpeedFor(resolved),
                Is.EqualTo(expectedAngularSpeed).Within(0.0001f));
            Assert.That(
                AssistantDriveSpeedRules.SliderSpeedFor(resolved),
                Is.EqualTo(expectedSliderSpeed).Within(0.0001f));
        }

        [Test]
        public void AssistantDriveRejectsUndefinedMultiplier()
        {
            Assert.That(
                AssistantDriveSpeedRules.TryResolveMultiplier(2.5f, out float resolved),
                Is.False);
            Assert.That(
                resolved,
                Is.EqualTo(AssistantDriveSpeedRules.DefaultMultiplier));
        }

        [Test]
        public void NativeDetentDebugUiRequestsRuntimeCatalogInsteadOfDuplicatingPresets()
        {
            string source = File.ReadAllText("Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");

            StringAssert.Contains("RequestDetentFeelStateFromNativeUi", source);
            StringAssert.Contains("CodexDetentTuningReceiveState", source);
            StringAssert.Contains("ForEach(Array(0..<state.detentPresetCount)", source);
            StringAssert.Contains("state.detentPresetName", source);
            StringAssert.Contains("String(format: \"%.2f\", value)", source);
            StringAssert.DoesNotContain("Camera Dial\"", source);
            StringAssert.DoesNotContain("Silk Ratchet\"", source);
        }

        [Test]
        public void NativeRendererUsesWaveformEnvelopeAndAllHapticDynamicControls()
        {
            string managed = File.ReadAllText("Assets/Scripts/FidgetSpinner/IosHaptics.cs");
            string native = File.ReadAllText("Assets/Plugins/iOS/CodexIosHaptics.mm");

            StringAssert.Contains("(int)recipe.Waveform", managed);
            StringAssert.Contains("CHHapticEventTypeHapticTransient", native);
            StringAssert.Contains("CHHapticEventTypeHapticContinuous", native);
            StringAssert.Contains("CodexIosHapticsPlayIsolatedTransient", managed);
            StringAssert.Contains("PlayIsolatedTransient", native);
            StringAssert.Contains("CHHapticEventParameterIDAttackTime", native);
            StringAssert.Contains("CHHapticEventParameterIDDecayTime", native);
            StringAssert.Contains("CHHapticEventParameterIDReleaseTime", native);
            StringAssert.Contains("CHHapticEventParameterIDSustained", native);
            StringAssert.Contains("CHHapticDynamicParameterIDHapticIntensityControl", native);
            StringAssert.Contains("CHHapticDynamicParameterIDHapticSharpnessControl", native);
            StringAssert.Contains("CHHapticDynamicParameterIDHapticAttackTimeControl", native);
            StringAssert.Contains("CHHapticDynamicParameterIDHapticDecayTimeControl", native);
            StringAssert.Contains("CHHapticDynamicParameterIDHapticReleaseTimeControl", native);
        }

        [Test]
        public void SpeedTextureLabIsWiredFromActualRotorStateThroughSemanticRouter()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string router = File.ReadAllText("Assets/Scripts/FidgetSpinner/IosHaptics.cs");
            string classic = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/FidgetSpinnerController.cs");
            string swift = File.ReadAllText("Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");

            StringAssert.Contains("metalSpinner.AngularSpeedRadians", coordinator);
            StringAssert.Contains("blueSpinner.AngularSpeedRadians", coordinator);
            StringAssert.Contains("FidgetHapticRouter.UpdateSpeedTexture", coordinator);
            StringAssert.Contains("blueSpinner?.SetDetentsPerTurn(detentsPerTurn)", coordinator);
            StringAssert.Contains("metalSpinner?.SetMagneticDetentsPerTurn(detentsPerTurn)", coordinator);
            StringAssert.DoesNotContain("IosHaptics.StartContinuous", coordinator);
            StringAssert.DoesNotContain("IosHaptics.UpdateContinuous", coordinator);

            StringAssert.Contains("HapticSpeedTextureStateMachine", router);
            StringAssert.Contains("SuppressDetentTransients", router);
            StringAssert.Contains("StartDetentContinuousResolved", router);
            StringAssert.Contains("TrackDetentCrossing", classic);
            StringAssert.DoesNotContain("dragHapticSpacing", classic);

            StringAssert.Contains("触觉实验室 · 转速质感", swift);
            StringAssert.Contains("SetHapticSpeedTextureProfileFromNativeUi", swift);
            StringAssert.Contains("CodexHapticLabReceiveTelemetry", swift);
            StringAssert.Contains("触点/s", swift);
            StringAssert.Contains("这里不是马达 Hz 或 G 值", swift);
            StringAssert.Contains("EditableHapticSemantic.generalTuningCases", swift);
            StringAssert.Contains("DETENT LAB 独占", swift);
        }

        [Test]
        public void NativeHapticLifecyclePreparesReportsAndStopsContinuousPlayer()
        {
            string managed = File.ReadAllText("Assets/Scripts/FidgetSpinner/IosHaptics.cs");
            string native = File.ReadAllText("Assets/Plugins/iOS/CodexIosHaptics.mm");

            StringAssert.Contains("CodexIosHapticsPrepare", managed);
            StringAssert.Contains("CodexIosHapticsGetStatus", managed);
            StringAssert.Contains("extern \"C\" void CodexIosHapticsPrepare", native);
            StringAssert.Contains("extern \"C\" int CodexIosHapticsGetStatus", native);
            StringAssert.Contains("gHapticEngine.resetHandler", native);
            StringAssert.Contains("gHapticEngine.stoppedHandler", native);
            StringAssert.Contains("RestartEngineAndRestorePlayers", native);
            StringAssert.Contains("gHapticEngine.autoShutdownEnabled = false", native);
            StringAssert.Contains("UIApplicationStateActive", native);
            StringAssert.Contains("StopContinuousPattern", native);
        }

        [Test]
        public void DetentAndInertiaUseIndependentIsolatedTransientChannels()
        {
            string managed = File.ReadAllText("Assets/Scripts/FidgetSpinner/IosHaptics.cs");
            string native = File.ReadAllText("Assets/Plugins/iOS/CodexIosHaptics.mm");
            string classicMotion = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/DeviceMotionController.cs");
            string metalMotion = File.ReadAllText(
                "Assets/Scripts/Product/MetalDeviceMotionController.cs");

            StringAssert.Contains("PlayDetentTransientResolved", managed);
            StringAssert.Contains("PlayInertiaTransientResolved", managed);
            StringAssert.Contains("FidgetSemanticEvent.InertiaShift", classicMotion);
            StringAssert.Contains("FidgetSemanticEvent.InertiaShift", metalMotion);
            StringAssert.DoesNotContain(
                "FidgetHapticRouter.Emit(FidgetSemanticEvent.ShakeBurst",
                classicMotion);
            StringAssert.DoesNotContain(
                "FidgetHapticRouter.Emit(FidgetSemanticEvent.ShakeBurst",
                metalMotion);
            StringAssert.Contains("CHHapticEventTypeHapticTransient", native);
            StringAssert.DoesNotContain("CHHapticAudioResourceID", native);
            StringAssert.DoesNotContain("initWithAudioResourceID", native);
        }

        [Test]
        public void RatchetAudioIsPhysicsDrivenAtomicPolyphonicAndNeverScheduled()
        {
            const string audioFolder = "Assets/_Fidgeting/Audio/RatchetClicks";
            string renderer = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Interaction/MetalRatchetDetentAudio.cs");
            string rotor = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Interaction/RotorRigidbodyController.cs");
            string builder = File.ReadAllText(
                "Assets/_Fidgeting/Editor/ThreeBladeSceneBuilder.cs");
            string native = File.ReadAllText("Assets/Plugins/iOS/CodexIosHaptics.mm");

            string[] variants = Directory.GetFiles(audioFolder, "*.wav");
            Assert.That(variants, Has.Length.EqualTo(5));
            Assert.That(
                File.Exists("Assets/_Fidgeting/Audio/MetalThreeBlade_RatchetDetent.wav"),
                Is.False);
            Assert.That(Directory.Exists("Assets/StreamingAssets"), Is.False);

            StringAssert.Contains("rotor.RatchetDetentCrossed +=", renderer);
            StringAssert.Contains("voice.PlayOneShot(clip, volume)", renderer);
            StringAssert.Contains("AudioSource[] voices", renderer);
            StringAssert.Contains("ResolveVolume", renderer);
            StringAssert.Contains("NextVariantIndex", renderer);
            StringAssert.Contains("ResolvePitchSemitones", renderer);
            StringAssert.DoesNotContain("void Update(", renderer);
            StringAssert.DoesNotContain("PlayScheduled", renderer);
            StringAssert.DoesNotContain("SetScheduled", renderer);
            StringAssert.DoesNotContain("StartCoroutine", renderer);
            StringAssert.DoesNotContain("Invoke(", renderer);

            StringAssert.Contains("for (int crossing = 0; crossing < crossingCount", rotor);
            StringAssert.Contains("RatchetDetentCrossed?.Invoke", rotor);
            StringAssert.Contains("RatchetAudioVoiceCount = 12", builder);
            StringAssert.DoesNotContain("ConfigureDetentAudio", native);
            StringAssert.DoesNotContain("CHHapticAudioResourceID", native);
            StringAssert.DoesNotContain("registerAudioResource", native);
            StringAssert.DoesNotContain("initWithAudioResourceID", native);
        }

        [Test]
        public void BothModelsUseWideTwoDimensionalVelocityResponsiveGestures()
        {
            string classic = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/FidgetSpinnerController.cs");
            string metal = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Interaction/MobileGestureController.cs");

            StringAssert.Contains("ApplyScreenDrag", classic);
            StringAssert.Contains("CalculateSignedDragPixels", classic);
            StringAssert.DoesNotContain("ApplyHorizontalDrag", classic);
            StringAssert.Contains("MapGestureToAngularSpeed", classic);
            StringAssert.Contains("FollowDragSpeed", classic);
            StringAssert.Contains("ResolveReleaseAngularSpeed", classic);
            StringAssert.DoesNotContain("flingImpulsePerPixelPerSecond", classic);
            StringAssert.DoesNotContain("tapImpulse", classic);
            StringAssert.Contains("fallbackTouchRadius = 0.48f", classic);
            StringAssert.Contains("AlignScreenTangentToSpinAxis", classic);
            StringAssert.DoesNotContain("-signedPixels * fallbackDegreesPerPixel", classic);
            StringAssert.DoesNotContain("-filteredHorizontalVelocity", classic);
            StringAssert.Contains("MapGestureToAngularSpeed", metal);
            StringAssert.Contains("FollowDragSpeed", metal);
            StringAssert.Contains("ResolveReleaseAngularSpeed", metal);
            StringAssert.Contains("SetTouchResponse", metal);
            StringAssert.Contains("CalculateScreenFallbackAngle", metal);
            StringAssert.Contains("AlignScreenTangentToSpinAxis", metal);
            StringAssert.Contains("fallbackTouchRadius = 0.48f", metal);
            StringAssert.Contains("reversalConfirmationPixels = 18f", metal);
        }
    }
}
