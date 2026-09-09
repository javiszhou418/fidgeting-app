using System;
using System.Collections.Generic;
using System.IO;
using FidgetingApp.Product;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    public static class PremiumDisplayCaseSceneBuilder
    {
        private const string GeneratedRoot = "Assets/_DisplayCase/Generated";
        private const string MeshRoot = GeneratedRoot + "/Meshes";
        private const string MaterialRoot = GeneratedRoot + "/Materials";
        private const string BlenderModelPath =
            "Assets/_DisplayCase/Models/PremiumDisplayCase.fbx";
        private const string PrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCase.prefab";
        private const string ThreeBladePrizePrefabPath =
            "Assets/Resources/Gacha/ThreeBladeDisplayPrize.prefab";
        private const string ThreeBladeMeshRoot =
            "Assets/_Fidgeting/Generated/Meshes";
        private const string ThreeBladeMaterialRoot =
            "Assets/_Fidgeting/Generated/Materials";
        private const string ScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity";
        private const string ProductFontPath =
            "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf";
        private const string BadgeArtworkRoot =
            "Assets/Plugins/iOS/BadgeArtwork";

        [MenuItem("Fidgeting/Display Case/Build Prefab And Scene")]
        public static void BuildPrefabAndScene()
        {
            EnsureDirectories();
            BuildThreeBladeDisplayPrizePrefab();
            MaterialLibrary materials = CreateMaterials();
            GameObject authoredRoot = BuildCase(materials);
            PrefabUtility.SaveAsPrefabAsset(authoredRoot, PrefabPath);
            UnityEngine.Object.DestroyImmediate(authoredRoot);

            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            PremiumDisplayCase prefab = AssetDatabase.LoadAssetAtPath<PremiumDisplayCase>(
                PrefabPath);
            PremiumDisplayCase instance = (PremiumDisplayCase)PrefabUtility
                .InstantiatePrefab(prefab, scene);
            instance.name = "PremiumDisplayCase";
            CreatePreviewEnvironment();
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"Premium display case generated: {PrefabPath}");
        }

        [MenuItem("Fidgeting/Display Case/Rebuild Three-Blade Prize")]
        public static void BuildThreeBladeDisplayPrizePrefab()
        {
            EnsureDirectories();
            GameObject prize = BuildThreeBladeDisplayPrize();
            PrefabUtility.SaveAsPrefabAsset(prize, ThreeBladePrizePrefabPath);
            UnityEngine.Object.DestroyImmediate(prize);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"Three-blade display prize generated: {ThreeBladePrizePrefabPath}");
        }

        [MenuItem("Fidgeting/Display Case/Build Three-Blade App Previews")]
        public static void BuildThreeBladeAppSceneAndPreviews()
        {
            BuildPrefabAndScene();
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            PremiumDisplayCase displayCase = UnityEngine.Object.FindAnyObjectByType<
                PremiumDisplayCase>();
            Camera camera = UnityEngine.Object.FindAnyObjectByType<Camera>();
            if (displayCase == null || camera == null)
            {
                throw new InvalidOperationException(
                    "Generated display-case preview scene is incomplete.");
            }

            GameObject prize = AttachThreeBladePrizeForPreview(displayCase);
            string outputDirectory = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/PremiumDisplayCaseThreeBladePreview"));
            Directory.CreateDirectory(outputDirectory);
            displayCase.setCapsulePreset(
                PremiumDisplayCaseCapsulePreset.CircularStandard);
            displayCase.SetRevealProgressForPreview(1f);

            displayCase.SetParallaxForPreview(Vector2.zero);
            Capture(camera, displayCase, outputDirectory, "01_hero.png",
                PremiumDisplayCaseCameraRules.FrontCameraPosition,
                PremiumDisplayCaseCameraRules.FrontLookAt,
                PremiumDisplayCaseCameraRules.ReferenceVerticalFieldOfView);
            displayCase.SetParallaxForPreview(new Vector2(0.22f, -0.12f));
            Capture(camera, displayCase, outputDirectory, "02_top.png",
                new Vector3(0.02f, 0.50f, -0.46f),
                new Vector3(0f, 0.012f, 0.016f), 29f);
            Capture(camera, displayCase, outputDirectory, "03_left_oblique.png",
                new Vector3(-0.30f, 0.085f, -0.72f),
                new Vector3(0f, 0.012f, 0.014f), 29f);
            Capture(camera, displayCase, outputDirectory, "04_right_oblique.png",
                new Vector3(0.30f, 0.085f, -0.72f),
                new Vector3(0f, 0.012f, 0.014f), 29f);
            Capture(camera, displayCase, outputDirectory, "05_low_angle.png",
                new Vector3(0.18f, -0.23f, -0.72f),
                new Vector3(0f, 0.012f, 0.016f), 29f);
            displayCase.SetParallaxForPreview(Vector2.zero);
            Capture(camera, displayCase, outputDirectory, "06_phone_hero.png",
                PremiumDisplayCaseCameraRules.FrontCameraPosition,
                PremiumDisplayCaseCameraRules.FrontLookAt,
                PremiumDisplayCaseCameraRules.ResolveVerticalFieldOfView(
                    942f / 2048f),
                942,
                2048);

            PremiumDisplayCaseInteractionController interaction =
                displayCase.GetComponent<PremiumDisplayCaseInteractionController>();
            if (interaction == null)
            {
                throw new InvalidOperationException(
                    "Display-case interaction controller is incomplete.");
            }
            interaction.SetExplodedProgressForPreview(1f);
            interaction.SetOrbitDegrees(15f, -6f);
            Capture(camera, displayCase, outputDirectory, "07_exploded.png",
                new Vector3(0.28f, 0.22f, -1.02f),
                new Vector3(0f, 0.008f, 0.020f),
                28f,
                1600,
                1600);
            interaction.SetExplodedProgressForPreview(0f);
            interaction.ResetInteraction();

            displayCase.setContent((Transform)null);
            UnityEngine.Object.DestroyImmediate(prize);
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log($"Three-blade app previews: {outputDirectory}");
        }

        [MenuItem("Fidgeting/Display Case/Capture All Shipping Products")]
        public static void CaptureAllShippingProducts()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing shipping display-case prefab: {PrefabPath}");
            }

            string outputRoot = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview"));
            Directory.CreateDirectory(outputRoot);

            foreach (ProductCatalogEntry product in ProductCatalog.ShippingEntries)
            {
                Scene scene = EditorSceneManager.OpenScene(
                    product.ScenePath,
                    OpenSceneMode.Single);
                Transform sourceRoot = FindShippingProductRoot(scene, product.ModelId);
                GameObject snapshot = PremiumDisplayCaseProductSnapshot.Capture(
                    product.ModelId,
                    sourceRoot);

                foreach (GameObject sceneRoot in scene.GetRootGameObjects())
                {
                    if (sceneRoot != snapshot)
                    {
                        sceneRoot.SetActive(false);
                    }
                }

                GameObject caseInstance = (GameObject)PrefabUtility
                    .InstantiatePrefab(prefab, scene);
                PremiumDisplayCase displayCase = caseInstance != null
                    ? caseInstance.GetComponent<PremiumDisplayCase>()
                    : null;
                if (displayCase == null)
                {
                    throw new MissingReferenceException(
                        $"Shipping display-case component is missing for {product.ModelId}.");
                }
                displayCase.name = $"PremiumDisplayCase_{product.ModelId}";
                PremiumDisplayCaseProductProfile profile =
                    PremiumDisplayCaseProductProfiles.Resolve(product.ModelId);
                displayCase.SetIdentification(
                    profile.EnglishDisplayName,
                    PreviewLevel(product.ModelId));
                ApplyPreviewFeaturedBadge(displayCase, product.ModelId);
                displayCase.setCapsulePreset(profile.CapsulePreset);
                displayCase.setContent(snapshot.transform, profile.ContentOptions);
                displayCase.SetRevealProgressForPreview(1f);
                displayCase.SetParallaxForPreview(Vector2.zero);

                CreatePreviewEnvironment();
                Camera camera = UnityEngine.Object.FindAnyObjectByType<Camera>();
                if (camera == null)
                {
                    throw new InvalidOperationException(
                        $"Preview camera was not created for {product.ModelId}.");
                }

                string productOutput = Path.Combine(outputRoot, product.ModelId);
                Directory.CreateDirectory(productOutput);
                CaptureProductApprovalViews(
                    camera,
                    displayCase,
                    productOutput);

                displayCase.setContent((Transform)null);
                UnityEngine.Object.DestroyImmediate(snapshot);
                UnityEngine.Object.DestroyImmediate(displayCase.gameObject);
                Debug.Log(
                    $"Display-case product preview complete: {product.ModelId}");
            }

            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Debug.Log($"All shipping display-case previews: {outputRoot}");
        }

        [MenuItem("Fidgeting/Display Case/Capture Lighting Palette Previews")]
        public static void CaptureLightingPalettePreviews()
        {
            const string modelId = "magnetic-slide-tile";
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing shipping display-case prefab: {PrefabPath}");
            }

            PremiumDisplayCaseProductProfile profile =
                PremiumDisplayCaseProductProfiles.Resolve(modelId);
            Scene scene = EditorSceneManager.OpenScene(
                SpinnerEnvironmentCatalog.EdcScenePath,
                OpenSceneMode.Single);
            Transform sourceRoot = FindShippingProductRoot(scene, modelId);
            GameObject snapshot = PremiumDisplayCaseProductSnapshot.Capture(
                modelId,
                sourceRoot);
            foreach (GameObject sceneRoot in scene.GetRootGameObjects())
            {
                if (sceneRoot != snapshot)
                {
                    sceneRoot.SetActive(false);
                }
            }

            GameObject caseInstance = (GameObject)PrefabUtility.InstantiatePrefab(
                prefab,
                scene);
            PremiumDisplayCase displayCase = caseInstance != null
                ? caseInstance.GetComponent<PremiumDisplayCase>()
                : null;
            if (displayCase == null)
            {
                throw new MissingReferenceException(
                    "Shipping display-case component is missing.");
            }

            displayCase.SetIdentification(
                profile.EnglishDisplayName,
                PreviewLevel(modelId));
            ApplyPreviewFeaturedBadge(displayCase, modelId);
            displayCase.setCapsulePreset(profile.CapsulePreset);
            displayCase.setContent(snapshot.transform, profile.ContentOptions);
            displayCase.SetRevealProgressForPreview(1f);
            displayCase.SetParallaxForPreview(Vector2.zero);
            CreatePreviewEnvironment();
            Camera camera = UnityEngine.Object.FindAnyObjectByType<Camera>();
            if (camera == null)
            {
                throw new InvalidOperationException(
                    "Display-case lighting preview camera is missing.");
            }

            string outputRoot = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/PremiumDisplayCaseLightingPalettePreview"));
            Directory.CreateDirectory(outputRoot);
            int index = 1;
            foreach (PremiumDisplayCaseLightingPreset preset in
                     PremiumDisplayCaseLightingCatalog.Presets)
            {
                displayCase.SetLightingPreset(preset.Id);
                string prefix = $"{index:00}_{preset.Id}";
                Capture(camera, displayCase, outputRoot, $"{prefix}_phone.png",
                    PremiumDisplayCaseCameraRules.FrontCameraPosition,
                    PremiumDisplayCaseCameraRules.FrontLookAt,
                    PremiumDisplayCaseCameraRules.ResolveVerticalFieldOfView(
                        942f / 2048f),
                    942,
                    2048);
                Capture(camera, displayCase, outputRoot, $"{prefix}_left.png",
                    new Vector3(-0.30f, 0.085f, -0.72f),
                    new Vector3(0f, 0.012f, 0.014f),
                    29f);
                Capture(camera, displayCase, outputRoot, $"{prefix}_right.png",
                    new Vector3(0.30f, 0.085f, -0.72f),
                    new Vector3(0f, 0.012f, 0.014f),
                    29f);
                index++;
            }

            displayCase.setContent((Transform)null);
            UnityEngine.Object.DestroyImmediate(snapshot);
            UnityEngine.Object.DestroyImmediate(displayCase.gameObject);
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Debug.Log(
                $"Display-case lighting palette previews: {outputRoot}");
        }

        private static void CaptureProductApprovalViews(
            Camera camera,
            PremiumDisplayCase displayCase,
            string outputDirectory)
        {
            Capture(camera, displayCase, outputDirectory, "01_hero.png",
                PremiumDisplayCaseCameraRules.FrontCameraPosition,
                PremiumDisplayCaseCameraRules.FrontLookAt,
                PremiumDisplayCaseCameraRules.ReferenceVerticalFieldOfView);
            Capture(camera, displayCase, outputDirectory, "02_top.png",
                new Vector3(0.02f, 0.50f, -0.46f),
                new Vector3(0f, 0.012f, 0.016f), 29f);
            Capture(camera, displayCase, outputDirectory, "03_left_oblique.png",
                new Vector3(-0.30f, 0.085f, -0.72f),
                new Vector3(0f, 0.012f, 0.014f), 29f);
            Capture(camera, displayCase, outputDirectory, "04_right_oblique.png",
                new Vector3(0.30f, 0.085f, -0.72f),
                new Vector3(0f, 0.012f, 0.014f), 29f);
            Capture(camera, displayCase, outputDirectory, "05_low_angle.png",
                new Vector3(0.18f, -0.23f, -0.72f),
                new Vector3(0f, 0.012f, 0.016f), 29f);
            Capture(camera, displayCase, outputDirectory, "06_phone_hero.png",
                PremiumDisplayCaseCameraRules.FrontCameraPosition,
                PremiumDisplayCaseCameraRules.FrontLookAt,
                PremiumDisplayCaseCameraRules.ResolveVerticalFieldOfView(
                    942f / 2048f),
                942,
                2048);
        }

        private static Transform FindShippingProductRoot(
            Scene scene,
            string modelId)
        {
            string expectedName = PremiumDisplayCaseProductProfiles.Resolve(modelId)
                .SceneRootName;

            foreach (GameObject root in scene.GetRootGameObjects())
            {
                if (string.Equals(
                        root.name,
                        expectedName,
                        StringComparison.Ordinal))
                {
                    return root.transform;
                }
            }

            throw new MissingReferenceException(
                $"Shipping product root {expectedName} is missing for {modelId}.");
        }

        [MenuItem("Fidgeting/Display Case/Build And Capture Previews")]
        public static void BuildPrefabSceneAndPreviews()
        {
            BuildPrefabAndScene();
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            PremiumDisplayCase displayCase = UnityEngine.Object.FindAnyObjectByType<
                PremiumDisplayCase>();
            Camera camera = UnityEngine.Object.FindAnyObjectByType<Camera>();
            if (displayCase == null || camera == null)
            {
                throw new InvalidOperationException(
                    "Generated display-case preview scene is incomplete.");
            }

            string outputDirectory = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/PremiumDisplayCasePreview"));
            Directory.CreateDirectory(outputDirectory);
            displayCase.setCapsulePreset(
                PremiumDisplayCaseCapsulePreset.CircularStandard);
            displayCase.SetRevealProgressForPreview(1f);
            displayCase.SetParallaxForPreview(Vector2.zero);

            Capture(camera, displayCase, outputDirectory, "01_hero.png",
                PremiumDisplayCaseCameraRules.FrontCameraPosition,
                PremiumDisplayCaseCameraRules.FrontLookAt,
                PremiumDisplayCaseCameraRules.ReferenceVerticalFieldOfView);
            displayCase.SetParallaxForPreview(new Vector2(0.22f, -0.12f));
            Capture(camera, displayCase, outputDirectory, "02_top.png",
                new Vector3(0.02f, 0.50f, -0.46f),
                new Vector3(0f, 0.012f, 0.016f), 29f);
            Capture(camera, displayCase, outputDirectory, "03_left_oblique.png",
                new Vector3(-0.30f, 0.085f, -0.72f),
                new Vector3(0f, 0.012f, 0.014f), 29f);
            Capture(camera, displayCase, outputDirectory, "04_right_oblique.png",
                new Vector3(0.30f, 0.085f, -0.72f),
                new Vector3(0f, 0.012f, 0.014f), 29f);
            Capture(camera, displayCase, outputDirectory, "05_low_angle.png",
                new Vector3(0.18f, -0.23f, -0.72f),
                new Vector3(0f, 0.012f, 0.016f), 29f);

            displayCase.SetRevealProgressForPreview(0f);
            displayCase.SetParallaxForPreview(Vector2.zero);
            Capture(camera, displayCase, outputDirectory, "06_closed_box.png",
                new Vector3(0.23f, 0.10f, -0.57f),
                new Vector3(0f, 0.008f, 0f), 31f);

            displayCase.SetRevealProgressForPreview(0.58f);
            Capture(camera, displayCase, outputDirectory, "07_mid_reveal.png",
                new Vector3(0.25f, 0.14f, -0.57f),
                new Vector3(0f, 0.012f, 0.002f), 31f);

            displayCase.setCapsulePreset(
                PremiumDisplayCaseCapsulePreset.RoundedSquareStandard);
            displayCase.SetRevealProgressForPreview(1f);
            displayCase.SetParallaxForPreview(new Vector2(-0.18f, 0.10f));
            Capture(camera, displayCase, outputDirectory,
                "08_rounded_square_preset.png",
                new Vector3(-0.245f, 0.13f, -0.56f),
                new Vector3(0f, 0.014f, 0.004f), 31f);

            displayCase.setCapsulePreset(
                PremiumDisplayCaseCapsulePreset.CircularStandard);
            displayCase.SetParallaxForPreview(Vector2.zero);

            PremiumDisplayCaseInteractionController interaction =
                displayCase.GetComponent<PremiumDisplayCaseInteractionController>();
            if (interaction != null)
            {
                interaction.SetExplodedProgressForPreview(0.52f);
                interaction.SetOrbitDegrees(18f, -7f);
            }
            Capture(camera, displayCase, outputDirectory,
                "09_interactive_half_exploded.png",
                new Vector3(0.22f, 0.16f, -0.92f),
                new Vector3(0f, 0.012f, 0.020f), 29f);
            if (interaction != null)
            {
                interaction.SetExplodedProgressForPreview(1f);
                interaction.SetOrbitDegrees(-14f, 8f);
            }
            Capture(camera, displayCase, outputDirectory,
                "10_interactive_exploded.png",
                new Vector3(0.28f, 0.22f, -1.02f),
                new Vector3(0f, 0.008f, 0.020f), 28f);
            if (interaction != null)
            {
                interaction.SetExplodedProgressForPreview(0f);
                interaction.ResetInteraction();
            }
            Capture(camera, displayCase, outputDirectory,
                "11_phone_hero.png",
                PremiumDisplayCaseCameraRules.FrontCameraPosition,
                PremiumDisplayCaseCameraRules.FrontLookAt,
                PremiumDisplayCaseCameraRules.ResolveVerticalFieldOfView(
                    942f / 2048f),
                942,
                2048);
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log($"Premium display-case previews: {outputDirectory}");
        }

        [MenuItem("Fidgeting/Display Case/Capture Transparent Exploded View")]
        public static void BuildAndCaptureTransparentExplodedView()
        {
            BuildPrefabAndScene();
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            PremiumDisplayCase displayCase = UnityEngine.Object.FindAnyObjectByType<
                PremiumDisplayCase>();
            Camera camera = UnityEngine.Object.FindAnyObjectByType<Camera>();
            if (displayCase == null || camera == null)
            {
                throw new InvalidOperationException(
                    "Generated display-case scene is incomplete.");
            }

            displayCase.setCapsulePreset(
                PremiumDisplayCaseCapsulePreset.CircularStandard);
            displayCase.SetRevealProgressForPreview(1f);
            displayCase.SetParallaxForPreview(Vector2.zero);

            PremiumDisplayCaseInteractionController interaction =
                displayCase.GetComponent<PremiumDisplayCaseInteractionController>();
            if (interaction == null)
            {
                throw new InvalidOperationException(
                    "Display-case interaction controller is incomplete.");
            }
            interaction.SetExplodedProgressForPreview(1f);
            interaction.SetOrbitDegrees(15f, -6f);
            GameObject backdrop = GameObject.Find("BlackBackdrop");
            if (backdrop != null)
            {
                backdrop.SetActive(false);
            }

            camera.orthographic = false;
            camera.backgroundColor = new Color(0f, 0f, 0f, 0f);
            string outputDirectory = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../Artifacts/PremiumDisplayCaseExploded"));
            Directory.CreateDirectory(outputDirectory);
            Capture(camera, displayCase, outputDirectory,
                "acrylic-case-exploded-transparent.png",
                new Vector3(0.28f, 0.22f, -1.08f),
                new Vector3(0f, 0.008f, 0.020f),
                28f,
                1800,
                1800,
                true);
            Debug.Log($"Transparent exploded view: {outputDirectory}");
        }

        /// <summary>
        /// R053 (user 2026-09-09): the reveal shows the shipping GEEONE
        /// dragon-scale tri-spinner (ModelPipeline metal-three-blade Gate 10
        /// export) with its approved Gate 07 materials, not the retired
        /// procedural three-blade frame. Same two kinematic groups as the
        /// product scene: Rotor_Root under RotorVisual, caps + hub core under
        /// HubVisual. No bearing is visible on the GEEONE design.
        /// </summary>
        private static GameObject BuildThreeBladeDisplayPrize()
        {
            GameObject modelAsset = AssetDatabase.LoadAssetAtPath<GameObject>(
                ThreeBladeEDC.EditorTools.ThreeBladeSceneBuilder.GeeoneModelPath);
            if (modelAsset == null)
            {
                throw new FileNotFoundException(
                    "The GEEONE tri-spinner FBX is missing.",
                    ThreeBladeEDC.EditorTools.ThreeBladeSceneBuilder.GeeoneModelPath);
            }

            GameObject root = new GameObject("ThreeBladeDisplayPrize");
            Transform rotor = Child(root.transform, "RotorVisual");
            Transform hub = Child(root.transform, "HubVisual");

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(modelAsset);
            instance.name = "GeeoneTriSpinner_Source";
            // The case slot rotates content +90° about X, so local -Y faces
            // the viewer and local -Z points to the top of the screen. The
            // GEEONE bottom is a recessed cup that shows the dark hub core
            // (diag 2026-09-09), so flip the spinner: Cap_Top toward the
            // viewer, the Blender twelve-o'clock blade (Unity -Z) screen-up.
            instance.transform.localRotation = Quaternion.Euler(0f, 0f, 180f);
            PrefabUtility.UnpackPrefabInstance(
                instance,
                PrefabUnpackMode.Completely,
                InteractionMode.AutomatedAction);

            Material satin = RequireThreeBladeMaterial("M_GeeoneSatin");
            Material disc = RequireThreeBladeMaterial("M_GeeoneDiscTurned");
            Material hubDark = RequireThreeBladeMaterial("M_GeeoneHubDark");

            ReparentGeeonePart(instance.transform, "Rotor_Root", rotor);
            ReparentGeeonePart(instance.transform, "Cap_Top", hub);
            ReparentGeeonePart(instance.transform, "Cap_Bottom", hub);
            ReparentGeeonePart(instance.transform, "Hub_Core", hub);
            UnityEngine.Object.DestroyImmediate(instance);

            foreach (Renderer renderer in root.GetComponentsInChildren<Renderer>(true))
            {
                renderer.enabled = true;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                Material[] assigned = renderer.sharedMaterials;
                for (int index = 0; index < assigned.Length; index++)
                {
                    string name = assigned[index] != null ? assigned[index].name : string.Empty;
                    assigned[index] = name.Contains("DiscTurned")
                        ? disc
                        : name.Contains("HubDark") ? hubDark : satin;
                }
                renderer.sharedMaterials = assigned;
            }
            foreach (Collider collider in root.GetComponentsInChildren<Collider>(true))
            {
                UnityEngine.Object.DestroyImmediate(collider);
            }
            return root;
        }

        private static void ReparentGeeonePart(Transform source, string name, Transform parent)
        {
            Transform part = null;
            foreach (Transform candidate in source.GetComponentsInChildren<Transform>(true))
            {
                if (candidate.name == name)
                {
                    part = candidate;
                    break;
                }
            }
            if (part == null)
            {
                throw new MissingReferenceException(
                    $"GEEONE FBX has no '{name}' node.");
            }
            part.SetParent(parent, true);
        }

        private static GameObject BuildLegacyProceduralThreeBladeDisplayPrize()
        {
            GameObject root = new GameObject("ThreeBladeDisplayPrize");
            Transform rotor = Child(root.transform, "RotorVisual");
            Transform hub = Child(root.transform, "HubVisual");
            Transform bearing = Child(root.transform, "BearingVisual");

            Material blade = RequireThreeBladeMaterial("M_BladeSandblast");
            Material bevel = RequireThreeBladeMaterial("M_BevelPolished");
            Material inset = RequireThreeBladeMaterial("M_BladeInset");
            Material darkRing = RequireThreeBladeMaterial("M_DarkRing");
            Material bearingSteel = RequireThreeBladeMaterial("M_BearingSteel");
            Material cap = RequireThreeBladeMaterial("M_CapRadialBrushed");

            AddThreeBladeMesh("RotorCore", rotor, "M_RotorCore",
                new[] { darkRing });
            AddThreeBladeMesh("BearingOuterRace", rotor, "M_BearingOuterRace",
                new[] { bearingSteel });
            AddThreeBladeMesh("ThreeBladeFrame", rotor, "M_ThreeBladeFrame",
                new[] { blade, bevel });
            GameObject insets = AddThreeBladeMesh(
                "ThreeBladeInsets",
                rotor,
                "M_ThreeBladeInsets",
                new[] { inset });
            insets.transform.localPosition = new Vector3(0f, 0.00316f, 0f);
            GameObject topTrim = AddThreeBladeMesh(
                "RotorCoreTopTrim",
                rotor,
                "M_RotorCoreTopTrim",
                new[] { darkRing });
            topTrim.transform.localPosition = new Vector3(0f, 0.00312f, 0f);

            GameObject axle = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            axle.name = "Axle";
            axle.transform.SetParent(hub, false);
            axle.transform.localScale = new Vector3(0.0078f, 0.0035f, 0.0078f);
            axle.GetComponent<MeshRenderer>().sharedMaterial = bearingSteel;
            Collider axleCollider = axle.GetComponent<Collider>();
            if (axleCollider != null)
            {
                UnityEngine.Object.DestroyImmediate(axleCollider);
            }

            AddThreeBladeMesh("BearingInnerRace", hub, "M_BearingInnerRace",
                new[] { bearingSteel });
            GameObject topWasher = AddThreeBladeMesh(
                "TopWasher",
                hub,
                "M_BearingWasher",
                new[] { darkRing });
            topWasher.transform.localPosition = new Vector3(0f, 0.00355f, 0f);
            GameObject bottomWasher = AddThreeBladeMesh(
                "BottomWasher",
                hub,
                "M_BearingWasher",
                new[] { darkRing });
            bottomWasher.transform.localPosition = new Vector3(0f, -0.00355f, 0f);
            GameObject topCap = AddThreeBladeMesh(
                "TopCap",
                hub,
                "M_FacetedTopCap",
                new[] { cap, bevel });
            topCap.transform.localPosition = new Vector3(0f, 0.0056f, 0f);
            GameObject bottomCap = AddThreeBladeMesh(
                "BottomCap",
                hub,
                "M_FacetedBottomCap",
                new[] { darkRing, bevel });
            bottomCap.transform.localPosition = new Vector3(0f, -0.0054f, 0f);

            GameObject cage = new GameObject("BallCage");
            cage.transform.SetParent(bearing, false);
            cage.transform.localPosition = new Vector3(0f, -0.0004f, 0f);
            AddThreeBladeMesh("BearingBalls", cage.transform, "M_BearingBallCage",
                new[] { bearingSteel });
            return root;
        }

        private static GameObject AddThreeBladeMesh(
            string name,
            Transform parent,
            string meshName,
            Material[] materials)
        {
            GameObject child = new GameObject(name);
            child.transform.SetParent(parent, false);
            child.AddComponent<MeshFilter>().sharedMesh = RequireThreeBladeMesh(meshName);
            child.AddComponent<MeshRenderer>().sharedMaterials = materials;
            return child;
        }

        private static Mesh RequireThreeBladeMesh(string name)
        {
            Mesh mesh = AssetDatabase.LoadAssetAtPath<Mesh>(
                $"{ThreeBladeMeshRoot}/{name}.asset");
            if (mesh == null)
            {
                throw new MissingReferenceException(
                    $"Missing authored three-blade mesh {name}.asset.");
            }
            return mesh;
        }

        private static Material RequireThreeBladeMaterial(string name)
        {
            Material material = AssetDatabase.LoadAssetAtPath<Material>(
                $"{ThreeBladeMaterialRoot}/{name}.mat");
            if (material == null)
            {
                throw new MissingReferenceException(
                    $"Missing authored three-blade material {name}.mat.");
            }
            return material;
        }

        private static GameObject AttachThreeBladePrizeForPreview(
            PremiumDisplayCase displayCase)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                ThreeBladePrizePrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing generated prize prefab {ThreeBladePrizePrefabPath}.");
            }

            GameObject prize = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            prize.name = "ThreeBladeDisplayPrize_Preview";
            displayCase.setContent(
                prize.transform,
                ThreeBladeDisplayPrizeFactory.ContentOptions);
            return prize;
        }

        private static GameObject BuildCase(MaterialLibrary materials)
        {
            GameObject root = new GameObject("PremiumDisplayCase");
            PremiumDisplayCase displayCase = root.AddComponent<PremiumDisplayCase>();
            root.AddComponent<PremiumDisplayCaseGyroAdapter>();
            PremiumDisplayCaseInteractionController interaction =
                root.AddComponent<PremiumDisplayCaseInteractionController>();

            Transform interactionRoot = Child(root.transform, "InteractionRoot");

            Transform boxParallax = Child(interactionRoot, "BoxParallaxRoot");
            Transform lid = Child(boxParallax, "BoxLidRoot");
            lid.localPosition = Vector3.zero;

            Transform caseReveal = Child(interactionRoot, "CaseRevealRoot");
            Transform interior = Child(caseReveal, "InteriorParallaxRoot");
            List<Renderer> acrylicRenderers = new List<Renderer>();
            Transform[] blenderLayers = AttachBlenderModelLayers(
                interactionRoot,
                boxParallax,
                lid,
                interior,
                caseReveal,
                materials,
                acrylicRenderers);
            Transform circularCapsule = Child(interior, "CircularCapsuleGeometry");
            blenderLayers[3].SetParent(circularCapsule, true);
            Transform roundedCapsule = Child(interior, "RoundedSquareCapsuleGeometry");
            BuildRoundedCapsule(roundedCapsule, materials);

            Transform contentParallax = Child(caseReveal, "ContentParallaxRoot");
            contentParallax.localPosition = new Vector3(0f, 0f, -0.014f);
            Transform contentSlot = Child(contentParallax, "contentSlot");
            Transform contentReveal = Child(contentSlot, "ContentRevealRoot");
            Transform contentOrbit = Child(contentReveal, "ContentOrbitRoot");
            Transform contentFit = Child(contentOrbit, "ContentFitRoot");
            Transform placeholder = BuildPlaceholderCoin(contentFit, materials);
            Font productFont = AssetDatabase.LoadAssetAtPath<Font>(ProductFontPath);
            if (productFont == null)
            {
                throw new MissingReferenceException(
                    $"Display-case laser font is missing: {ProductFontPath}");
            }
            TextMesh levelLaserMark = BuildLaserMark(
                interior,
                "LaserLevelMark",
                productFont,
                "LEVEL 1",
                new Vector3(0f, -0.073f, -0.012f),
                0.0014f,
                new Color(0.54f, 0.60f, 0.65f, 0.86f));
            TextMesh productNameLaserMark = BuildLaserMark(
                interior,
                "LaserProductName",
                productFont,
                "COLLECTOR EDITION",
                new Vector3(0f, -0.087f, -0.012f),
                0.0019f,
                new Color(0.72f, 0.76f, 0.79f, 0.94f));
            BuildFeaturedBadge(
                interior,
                materials,
                productFont,
                out Transform featuredBadgeRoot,
                out Renderer featuredBadgeArtworkRenderer,
                out TextMesh featuredBadgeTokenMark,
                out TextMesh featuredBadgeShortNameMark);
            PremiumDisplayCaseBadgeArtworkBinding[] badgeArtwork =
                LoadToyBadgeArtwork();

            Transform acrylic = Child(caseReveal, "AcrylicParallaxRoot");
            for (int index = 0; index < 3; index++)
            {
                blenderLayers[index].SetParent(acrylic, true);
            }
            foreach (Transform blenderLayer in blenderLayers)
            {
                // The selected FBX children carry Blender's X/Z face plane
                // after their import wrapper is unpacked. Reapply a proper
                // handedness conversion: Blender +Z becomes Unity +Y and
                // Blender -Y becomes Unity -Z (the authored front direction).
                // Keeping the two rotations explicit prevents a sign error
                // that would vertically mirror the capsule anchor.
                Quaternion axisConversion = Quaternion.Euler(0f, 180f, 0f)
                    * Quaternion.Euler(-90f, 0f, 0f);
                blenderLayer.localRotation = axisConversion
                    * blenderLayer.localRotation;
            }
            Light[] lights = BuildCaseLights(root.transform);

            displayCase.ConfigureAuthoring(
                caseReveal,
                boxParallax,
                lid,
                acrylic,
                interior,
                contentParallax,
                circularCapsule,
                roundedCapsule,
                contentSlot,
                contentReveal,
                contentOrbit,
                contentFit,
                placeholder,
                levelLaserMark,
                productNameLaserMark,
                featuredBadgeRoot,
                featuredBadgeArtworkRenderer,
                featuredBadgeTokenMark,
                featuredBadgeShortNameMark,
                badgeArtwork,
                acrylicRenderers.ToArray(),
                lights);
            interaction.ConfigureAuthoring(
                interactionRoot,
                blenderLayers,
                new[]
                {
                    new Vector3(-0.130f, 0.100f, -0.090f),
                    new Vector3(-0.101f, 0.076f, -0.070f),
                    new Vector3(-0.071f, 0.052f, -0.051f),
                    new Vector3(-0.037f, 0.027f, -0.027f),
                    new Vector3(0.030f, -0.021f, 0.021f),
                    new Vector3(0.064f, -0.047f, 0.043f),
                    new Vector3(0.102f, -0.076f, 0.069f),
                    new Vector3(0.142f, 0.105f, 0.105f)
                },
                contentParallax,
                3);
            return root;
        }

        private static TextMesh BuildLaserMark(
            Transform parent,
            string name,
            Font font,
            string text,
            Vector3 localPosition,
            float characterSize,
            Color color)
        {
            GameObject label = new GameObject(name);
            label.transform.SetParent(parent, false);
            label.transform.localPosition = localPosition;
            label.transform.localRotation = Quaternion.identity;
            label.transform.localScale = Vector3.one;

            TextMesh mark = label.AddComponent<TextMesh>();
            mark.font = font;
            mark.fontSize = 64;
            mark.fontStyle = FontStyle.Normal;
            mark.text = text;
            mark.characterSize = characterSize;
            mark.anchor = TextAnchor.MiddleCenter;
            mark.alignment = TextAlignment.Center;
            mark.color = color;
            mark.richText = false;

            MeshRenderer renderer = label.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = font.material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            renderer.lightProbeUsage = LightProbeUsage.Off;
            renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            renderer.motionVectorGenerationMode = MotionVectorGenerationMode.ForceNoMotion;
            renderer.sortingOrder = 1;
            return mark;
        }

        private static void BuildFeaturedBadge(
            Transform interior,
            MaterialLibrary materials,
            Font font,
            out Transform badgeRoot,
            out Renderer artworkRenderer,
            out TextMesh tokenMark,
            out TextMesh shortNameMark)
        {
            badgeRoot = Child(interior, "FeaturedBadgeRoot");
            badgeRoot.localPosition = new Vector3(0f, 0.081f, -0.013f);

            GameObject artwork = GameObject.CreatePrimitive(PrimitiveType.Quad);
            artwork.name = "FeaturedBadgeArtwork";
            artwork.transform.SetParent(badgeRoot, false);
            artwork.transform.localPosition = new Vector3(-0.014f, 0f, 0f);
            artwork.transform.localRotation = Quaternion.identity;
            artwork.transform.localScale = Vector3.one * 0.031f;
            Collider artworkCollider = artwork.GetComponent<Collider>();
            if (artworkCollider != null)
            {
                UnityEngine.Object.DestroyImmediate(artworkCollider);
            }
            artworkRenderer = artwork.GetComponent<Renderer>();
            artworkRenderer.sharedMaterial = materials.BadgeArtwork;
            artworkRenderer.shadowCastingMode = ShadowCastingMode.Off;
            artworkRenderer.receiveShadows = false;
            artworkRenderer.lightProbeUsage = LightProbeUsage.Off;
            artworkRenderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
            artworkRenderer.motionVectorGenerationMode =
                MotionVectorGenerationMode.ForceNoMotion;
            artworkRenderer.sortingOrder = 2;

            tokenMark = BuildLaserMark(
                badgeRoot,
                "FeaturedBadgeToken",
                font,
                "100K",
                new Vector3(0.014f, 0.0032f, -0.0012f),
                0.0015f,
                new Color(0.66f, 0.69f, 0.71f, 0.90f));
            tokenMark.GetComponent<MeshRenderer>().sortingOrder = 3;
            shortNameMark = BuildLaserMark(
                badgeRoot,
                "FeaturedBadgeShortName",
                font,
                "PULSE",
                new Vector3(0.014f, -0.0040f, -0.0013f),
                0.00068f,
                new Color(0.66f, 0.69f, 0.71f, 0.74f));
            shortNameMark.GetComponent<MeshRenderer>().sortingOrder = 3;
        }

        private static PremiumDisplayCaseBadgeArtworkBinding[] LoadToyBadgeArtwork()
        {
            IReadOnlyList<BadgeDefinition> definitions =
                BadgeCatalogV2.ToyDefinitions;
            var bindings = new PremiumDisplayCaseBadgeArtworkBinding[
                definitions.Count];
            for (int index = 0; index < definitions.Count; index++)
            {
                BadgeDefinition definition = definitions[index];
                string path = $"{BadgeArtworkRoot}/{definition.AssetName}.png";
                Texture2D artwork = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                if (artwork == null)
                {
                    throw new MissingReferenceException(
                        $"Display-case Badge artwork is missing: {path}");
                }
                bindings[index] = new PremiumDisplayCaseBadgeArtworkBinding(
                    definition.AssetName,
                    artwork);
            }
            return bindings;
        }

        private static void ApplyPreviewFeaturedBadge(
            PremiumDisplayCase displayCase,
            string modelId)
        {
            string definitionId = modelId switch
            {
                ProductCatalog.PointedThreeBladeModelId => "toy_combo_20",
                ProductCatalog.MetalThreeBladeModelId => "toy_power_singularity",
                ProductCatalog.GoldFourWingModelId => "toy_pulse_100k",
                ProductCatalog.GraphiteTwoLobeModelId => "toy_technique_perfect",
                ProductCatalog.MagneticSlideTileModelId => "toy_focus_10h",
                ProductCatalog.MagneticFanCardModelId => "toy_combo_50",
                _ => "toy_power_ignition"
            };
            BadgeDefinition selected = default;
            bool found = false;
            foreach (BadgeDefinition definition in BadgeCatalogV2.ToyDefinitions)
            {
                if (!string.Equals(
                        definition.Id,
                        definitionId,
                        StringComparison.Ordinal))
                {
                    continue;
                }
                selected = definition;
                found = true;
                break;
            }
            if (!found)
            {
                throw new InvalidOperationException(
                    $"Preview Badge definition is missing: {definitionId}");
            }
            displayCase.SetFeaturedBadge(
                selected.AssetName,
                selected.DisplayToken,
                selected.ShortName,
                selected.Grade.ToString());
        }

        private static int PreviewLevel(string modelId)
        {
            return modelId switch
            {
                ProductCatalog.PointedThreeBladeModelId => 7,
                ProductCatalog.MetalThreeBladeModelId => 24,
                ProductCatalog.GoldFourWingModelId => 42,
                ProductCatalog.GraphiteTwoLobeModelId => 58,
                ProductCatalog.MagneticSlideTileModelId => 73,
                ProductCatalog.MagneticFanCardModelId => 91,
                _ => 1
            };
        }

        private static Transform[] AttachBlenderModelLayers(
            Transform interactionRoot,
            Transform boxParallax,
            Transform lidRoot,
            Transform interior,
            Transform caseReveal,
            MaterialLibrary materials,
            List<Renderer> acrylicRenderers)
        {
            GameObject modelAsset = AssetDatabase.LoadAssetAtPath<GameObject>(
                BlenderModelPath);
            if (modelAsset == null)
            {
                throw new InvalidOperationException(
                    $"Blender display-case model is missing: {BlenderModelPath}");
            }

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(modelAsset);
            instance.name = "BlenderDisplayCaseAuthoring";
            PrefabUtility.UnpackPrefabInstance(
                instance,
                PrefabUnpackMode.Completely,
                InteractionMode.AutomatedAction);
            instance.transform.SetParent(interactionRoot, false);
            instance.transform.localPosition = Vector3.zero;
            instance.transform.localRotation = Quaternion.identity;
            instance.transform.localScale = Vector3.one;

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
            Transform[] layers = new Transform[names.Length];
            for (int index = 0; index < names.Length; index++)
            {
                layers[index] = FindDescendant(instance.transform, names[index]);
                if (layers[index] == null)
                {
                    UnityEngine.Object.DestroyImmediate(instance);
                    throw new InvalidOperationException(
                        $"Blender display-case layer is missing: {names[index]}");
                }
                AssignImportedMaterials(layers[index], materials, acrylicRenderers);
            }

            layers[3].SetParent(interior, true);
            layers[4].SetParent(interior, true);
            layers[5].SetParent(interior, true);
            layers[6].SetParent(boxParallax, true);
            layers[7].SetParent(lidRoot, true);

            // The first three layers are moved under AcrylicParallaxRoot after
            // that runtime root is created. Keep them alive while discarding
            // the FBX wrapper and DCC-only ContentSlot locator.
            for (int index = 0; index < 3; index++)
            {
                layers[index].SetParent(caseReveal, true);
            }
            UnityEngine.Object.DestroyImmediate(instance);
            return layers;
        }

        private static Transform FindDescendant(Transform root, string name)
        {
            if (root.name == name)
            {
                return root;
            }
            foreach (Transform child in root)
            {
                Transform match = FindDescendant(child, name);
                if (match != null)
                {
                    return match;
                }
            }
            return null;
        }

        private static void AssignImportedMaterials(
            Transform layer,
            MaterialLibrary materials,
            List<Renderer> acrylicRenderers)
        {
            Renderer[] renderers = layer.GetComponentsInChildren<Renderer>(true);
            foreach (Renderer renderer in renderers)
            {
                string name = renderer.gameObject.name;
                Material resolved;
                if (name.StartsWith("Acrylic_FrontPlate", StringComparison.Ordinal)
                    || name.StartsWith("Acrylic_RearPlate", StringComparison.Ordinal)
                    || name.StartsWith("Acrylic_BackFrame", StringComparison.Ordinal)
                    || name == "Capsule_ClearBack")
                {
                    resolved = materials.Acrylic;
                    acrylicRenderers.Add(renderer);
                }
                else if (name.StartsWith("Acrylic_SpacerFrame", StringComparison.Ordinal)
                    || name == "Capsule_CircularRing")
                {
                    resolved = materials.AcrylicEdge;
                    acrylicRenderers.Add(renderer);
                }
                else if (name.StartsWith("ChromeCollar_", StringComparison.Ordinal)
                    || name == "Capsule_EdgeHighlight")
                {
                    resolved = materials.BrushedMetal;
                }
                else if (name.StartsWith("Fastener_", StringComparison.Ordinal))
                {
                    resolved = materials.MatteBox;
                }
                else if (name.Contains("Velvet", StringComparison.Ordinal))
                {
                    resolved = materials.Velvet;
                }
                else if (name.StartsWith("Graphite_", StringComparison.Ordinal))
                {
                    resolved = materials.Graphite;
                }
                else
                {
                    resolved = materials.Graphite;
                }
                renderer.sharedMaterial = resolved;
            }
        }

        private static void BuildOuterBox(Transform parent, MaterialLibrary materials)
        {
            AddRoundedBox(parent, "MatteBlackOuterBox", 0.222f, 0.286f,
                0.036f, 0.017f, new Vector3(0f, 0f, 0.048f), materials.MatteBox);
            AddRoundedBox(parent, "VelvetWell", 0.198f, 0.260f,
                0.010f, 0.013f, new Vector3(0f, 0f, 0.025f), materials.Velvet);
            AddRoundedBox(parent, "BoxLeftRail", 0.013f, 0.264f,
                0.030f, 0.005f, new Vector3(-0.104f, 0f, 0.018f), materials.MatteBox);
            AddRoundedBox(parent, "BoxRightRail", 0.013f, 0.264f,
                0.030f, 0.005f, new Vector3(0.104f, 0f, 0.018f), materials.MatteBox);
            AddRoundedBox(parent, "BoxBottomRail", 0.214f, 0.014f,
                0.030f, 0.005f, new Vector3(0f, -0.136f, 0.018f), materials.MatteBox);
        }

        private static void BuildBoxLid(Transform lid, MaterialLibrary materials)
        {
            AddRoundedBox(lid, "MatteBlackLid", 0.218f, 0.282f,
                0.018f, 0.017f, new Vector3(0f, -0.141f, 0f), materials.MatteBox);
            AddCube(lid, "LidOcclusionCore", new Vector3(0.194f, 0.252f, 0.012f),
                new Vector3(0f, -0.141f, -0.012f), materials.MatteBox);
            AddRoundedBox(lid, "LidInset", 0.184f, 0.218f,
                0.004f, 0.012f, new Vector3(0f, -0.135f, -0.020f), materials.Velvet);
            AddRoundedBox(lid, "LidRevealLine", 0.082f, 0.003f,
                0.002f, 0.0015f, new Vector3(0f, -0.212f, -0.023f), materials.Graphite);
        }

        private static void BuildInterior(Transform parent, MaterialLibrary materials)
        {
            AddRoundedBox(parent, "VelvetBacking", 0.170f, 0.220f,
                0.008f, 0.013f, new Vector3(0f, 0f, 0.020f), materials.Velvet);
            AddRoundedBox(parent, "LowerPlaque", 0.106f, 0.036f,
                0.006f, 0.009f, new Vector3(0f, -0.081f, 0.010f), materials.Graphite);
            AddRoundedBox(parent, "PlaqueHighlight", 0.055f, 0.002f,
                0.002f, 0.001f, new Vector3(0f, -0.081f, 0.006f), materials.BrushedMetal);
        }

        private static void BuildCircularCapsule(Transform parent, MaterialLibrary materials)
        {
            AddCircularRing(parent, "CircularRecessWall", 0.126f, 0.112f,
                0.040f, new Vector3(0f, 0.018f, 0.010f), materials.Graphite, 64);
            AddCylinder(parent, "CircularRecessBack", 0.112f, 0.004f,
                new Vector3(0f, 0.018f, 0.028f), materials.Velvet, 64);
            AddCircularRing(parent, "CircularEdgeLight", 0.119f, 0.112f,
                0.002f, new Vector3(0f, 0.018f, -0.011f),
                materials.BrushedMetal, 64);
        }

        private static void BuildRoundedCapsule(Transform parent, MaterialLibrary materials)
        {
            AddRoundedRing(parent, "RoundedRecessWall", 0.096f, 0.084f,
                0.026f, 0.017f, 0.014f, new Vector3(0f, 0f, -0.007f),
                materials.Graphite);
            AddRoundedBox(parent, "RoundedRecessBack", 0.084f, 0.084f,
                0.003f, 0.014f, new Vector3(0f, 0f, -0.001f), materials.Velvet);
            AddRoundedRing(parent, "RoundedEdgeLight", 0.090f, 0.086f,
                0.002f, 0.015f, 0.014f, new Vector3(0f, 0f, -0.012f),
                materials.BrushedMetal);
        }

        private static Transform BuildPlaceholderCoin(
            Transform parent,
            MaterialLibrary materials)
        {
            Transform coin = Child(parent, "DevelopmentPlaceholder_Coin");
            AddCylinder(coin, "PlaceholderCoinBody", 0.064f, 0.012f,
                Vector3.zero, materials.PlaceholderGem, 64);
            AddCylinder(coin, "PlaceholderCoinInset", 0.050f, 0.003f,
                new Vector3(0f, 0f, -0.0075f), materials.BrushedMetal, 64);
            AddCylinder(coin, "PlaceholderCoinCenter", 0.020f, 0.004f,
                new Vector3(0f, 0f, -0.0095f), materials.PlaceholderGem, 48);
            return coin;
        }

        private static void BuildAcrylicCase(
            Transform parent,
            MaterialLibrary materials,
            List<Renderer> acrylicRenderers)
        {
            GameObject front = AddRoundedBox(parent, "LiquidGlassFront",
                0.188f, 0.240f, 0.006f, 0.015f,
                new Vector3(0f, 0f, -0.037f), materials.Acrylic);
            acrylicRenderers.Add(front.GetComponent<Renderer>());

            AddAcrylicPiece(parent, acrylicRenderers, materials, "AcrylicTopEdge",
                0.190f, 0.012f, 0.014f, 0.005f, new Vector3(0f, 0.116f, -0.029f));
            AddAcrylicPiece(parent, acrylicRenderers, materials, "AcrylicBottomEdge",
                0.190f, 0.012f, 0.014f, 0.005f, new Vector3(0f, -0.116f, -0.029f));
            AddAcrylicPiece(parent, acrylicRenderers, materials, "AcrylicLeftEdge",
                0.012f, 0.228f, 0.014f, 0.005f, new Vector3(-0.089f, 0f, -0.029f));
            AddAcrylicPiece(parent, acrylicRenderers, materials, "AcrylicRightEdge",
                0.012f, 0.228f, 0.014f, 0.005f, new Vector3(0.089f, 0f, -0.029f));

            Vector2[] fasteners =
            {
                new Vector2(-0.078f, 0.105f),
                new Vector2(0.078f, 0.105f),
                new Vector2(-0.078f, -0.105f),
                new Vector2(0.078f, -0.105f)
            };
            foreach (Vector2 point in fasteners)
            {
                AddCylinder(parent, "BrushedMetalFastener", 0.012f, 0.008f,
                    new Vector3(point.x, point.y, -0.043f),
                    materials.BrushedMetal, 32);
            }
        }

        private static void AddAcrylicPiece(
            Transform parent,
            List<Renderer> renderers,
            MaterialLibrary materials,
            string name,
            float width,
            float height,
            float depth,
            float radius,
            Vector3 position)
        {
            GameObject piece = AddRoundedBox(parent, name, width, height, depth,
                radius, position, materials.AcrylicEdge);
            renderers.Add(piece.GetComponent<Renderer>());
        }

        private static Light[] BuildCaseLights(Transform parent)
        {
            Light key = AddLight(parent, "CaseLight_Key", LightType.Directional,
                new Color(1f, 0.72f, 0.90f), 0.42f,
                new Vector3(-0.26f, 0.31f, -0.34f));
            key.transform.LookAt(Vector3.zero);

            Light fill = AddLight(parent, "CaseLight_Fill", LightType.Point,
                new Color(0.76f, 0.90f, 1f), 0.13f,
                new Vector3(0.22f, 0.035f, -0.24f));
            fill.range = 0.75f;

            Light rim = AddLight(parent, "CaseLight_Rim", LightType.Point,
                new Color(1f, 0.30f, 0.70f), 0.24f,
                new Vector3(-0.18f, 0.13f, 0.17f));
            rim.range = 0.65f;
            return new[] { key, fill, rim };
        }

        private static Light AddLight(
            Transform parent,
            string name,
            LightType type,
            Color color,
            float intensity,
            Vector3 position)
        {
            GameObject lightObject = new GameObject(name);
            lightObject.transform.SetParent(parent, false);
            lightObject.transform.localPosition = position;
            Light light = lightObject.AddComponent<Light>();
            light.type = type;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
            light.shadowStrength = 0.42f;
            return light;
        }

        private static void CreatePreviewEnvironment()
        {
            GameObject environment = new GameObject("PreviewEnvironment");

            GameObject cameraObject = new GameObject("PremiumDisplayCaseCamera");
            cameraObject.tag = "MainCamera";
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.34f, 0.045f, 0.17f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.allowHDR = true;
            camera.fieldOfView =
                PremiumDisplayCaseCameraRules.ReferenceVerticalFieldOfView;
            camera.transform.position =
                PremiumDisplayCaseCameraRules.FrontCameraPosition;
            camera.transform.LookAt(PremiumDisplayCaseCameraRules.FrontLookAt);

            GameObject ambient = new GameObject("PreviewAmbientLight");
            Light ambientLight = ambient.AddComponent<Light>();
            ambientLight.type = LightType.Directional;
            ambientLight.color = new Color(0.88f, 0.48f, 0.70f);
            ambientLight.intensity = 0.10f;
            ambient.transform.rotation = Quaternion.Euler(42f, -28f, 0f);

            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.055f, 0.020f, 0.045f);
            RenderSettings.fog = false;
        }

        private static void Capture(
            Camera camera,
            PremiumDisplayCase displayCase,
            string outputDirectory,
            string filename,
            Vector3 cameraPosition,
            Vector3 lookAt,
            float fieldOfView,
            int width = 1200,
            int height = 1600,
            bool transparentBackground = false)
        {
            camera.transform.position = cameraPosition;
            camera.transform.LookAt(lookAt);
            camera.fieldOfView = fieldOfView;
            Color previousBackground = camera.backgroundColor;
            CameraClearFlags previousClearFlags = camera.clearFlags;
            bool previousAllowMsaa = camera.allowMSAA;
            camera.allowMSAA = false;
            if (transparentBackground)
            {
                camera.clearFlags = CameraClearFlags.SolidColor;
                camera.backgroundColor = new Color(0f, 0f, 0f, 0f);
            }
            RenderTexture renderTexture = new RenderTexture(width, height, 24,
                RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 1,
                name = "PremiumDisplayCasePreviewRT"
            };
            renderTexture.Create();
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            camera.targetTexture = renderTexture;
            RenderTexture.active = renderTexture;
            camera.Render();
            Texture2D texture = new Texture2D(width, height, TextureFormat.RGBA32,
                false, false);
            texture.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            texture.Apply(false, false);
            File.WriteAllBytes(Path.Combine(outputDirectory, filename),
                texture.EncodeToPNG());
            camera.targetTexture = previousTarget;
            camera.backgroundColor = previousBackground;
            camera.clearFlags = previousClearFlags;
            camera.allowMSAA = previousAllowMsaa;
            RenderTexture.active = previousActive;
            renderTexture.Release();
            UnityEngine.Object.DestroyImmediate(texture);
            UnityEngine.Object.DestroyImmediate(renderTexture);
        }

        private static MaterialLibrary CreateMaterials()
        {
            Shader lit = Shader.Find("Universal Render Pipeline/Lit");
            Shader acrylicShader = Shader.Find(
                "FidgetingApp/PremiumAcrylicLiquidGlass");
            Shader badgeShader = Shader.Find("FidgetingApp/PremiumBadgeArtwork");
            if (lit == null || acrylicShader == null || badgeShader == null)
            {
                throw new InvalidOperationException(
                    "Required display-case shaders are unavailable.");
            }

            Material matteBox = CreateLitMaterial("MatteBlackBox", lit,
                new Color(0.003f, 0.004f, 0.006f, 1f), 0.10f, 0.78f);
            Material velvet = CreateLitMaterial("BlackVelvet", lit,
                new Color(0.012f, 0.016f, 0.022f, 1f), 0f, 0.16f);
            Material graphite = CreateLitMaterial("NeutralGraphite", lit,
                new Color(0.055f, 0.067f, 0.082f, 1f), 0.46f, 0.66f);
            Material metal = CreateLitMaterial("BrushedMetal", lit,
                new Color(0.58f, 0.62f, 0.68f, 1f), 0.98f, 0.82f);
            Material gem = CreateLitMaterial("DevelopmentGem", lit,
                new Color(0.20f, 0.27f, 0.30f, 1f), 0.74f, 0.74f);
            gem.SetColor("_EmissionColor", new Color(0.006f, 0.014f, 0.018f));
            gem.EnableKeyword("_EMISSION");
            Material background = CreateLitMaterial("PreviewBackground", lit,
                new Color(0.34f, 0.045f, 0.17f, 1f), 0f, 0.08f);

            Material acrylic = CreateOrUpdateMaterial(
                MaterialRoot + "/LiquidGlass.mat", acrylicShader);
            acrylic.SetColor("_BaseColor", new Color(0.70f, 0.82f, 0.90f, 1f));
            acrylic.SetColor("_RimColor", new Color(1f, 0.72f, 0.94f, 1f));
            acrylic.SetFloat("_Opacity", 0.035f);
            acrylic.SetFloat("_RimStrength", 0.72f);
            acrylic.SetFloat("_RimPower", 3.8f);
            acrylic.SetFloat("_SpecularStrength", 0.94f);
            acrylic.renderQueue = (int)RenderQueue.Transparent + 20;

            Material acrylicEdge = CreateOrUpdateMaterial(
                MaterialRoot + "/LiquidGlassEdge.mat", acrylicShader);
            acrylicEdge.SetColor("_BaseColor", new Color(0.72f, 0.86f, 0.94f, 1f));
            acrylicEdge.SetColor("_RimColor", new Color(1f, 0.66f, 0.92f, 1f));
            acrylicEdge.SetFloat("_Opacity", 0.075f);
            acrylicEdge.SetFloat("_RimStrength", 1.02f);
            acrylicEdge.SetFloat("_RimPower", 2.8f);
            acrylicEdge.SetFloat("_SpecularStrength", 1.08f);
            acrylicEdge.renderQueue = (int)RenderQueue.Transparent + 21;

            Material badgeArtwork = CreateOrUpdateMaterial(
                MaterialRoot + "/PremiumBadgeArtwork.mat", badgeShader);
            badgeArtwork.SetColor(
                "_EtchColor",
                new Color(0.66f, 0.69f, 0.71f, 1f));
            badgeArtwork.SetFloat("_EtchOpacity", 0.88f);
            badgeArtwork.SetFloat("_GrainStrength", 0.065f);
            badgeArtwork.renderQueue = (int)RenderQueue.Transparent + 10;

            EditorUtility.SetDirty(acrylic);
            EditorUtility.SetDirty(acrylicEdge);
            EditorUtility.SetDirty(badgeArtwork);
            return new MaterialLibrary(matteBox, velvet, graphite, metal, gem,
                acrylic, acrylicEdge, badgeArtwork, background);
        }

        private static Material CreateLitMaterial(
            string name,
            Shader shader,
            Color color,
            float metallic,
            float smoothness)
        {
            Material material = CreateOrUpdateMaterial(
                $"{MaterialRoot}/{name}.mat", shader);
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_Surface", 0f);
            material.renderQueue = (int)RenderQueue.Geometry;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateOrUpdateMaterial(string path, Shader shader)
        {
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader)
                {
                    name = Path.GetFileNameWithoutExtension(path)
                };
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.shader = shader;
            }
            return material;
        }

        private static GameObject AddRoundedBox(
            Transform parent,
            string name,
            float width,
            float height,
            float depth,
            float radius,
            Vector3 position,
            Material material)
        {
            string meshName = string.Concat(
                name, "_", Millimeters(width), "x", Millimeters(height), "x",
                Millimeters(depth), "_r", Millimeters(radius));
            return AddMesh(parent, name,
                GetOrCreateMesh(meshName,
                    () => CreateRoundedBoxMesh(width, height, depth, radius, 7)),
                material,
                position);
        }

        private static GameObject AddCylinder(
            Transform parent,
            string name,
            float diameter,
            float depth,
            Vector3 position,
            Material material,
            int segments)
        {
            string meshName = string.Concat(name, "_d", Millimeters(diameter),
                "x", Millimeters(depth), "_s", segments);
            return AddMesh(parent, name,
                GetOrCreateMesh(meshName,
                    () => CreateCylinderMesh(diameter, depth, segments)),
                material,
                position);
        }

        private static GameObject AddCircularRing(
            Transform parent,
            string name,
            float outerDiameter,
            float innerDiameter,
            float depth,
            Vector3 position,
            Material material,
            int segments)
        {
            string meshName = string.Concat(name, "_d", Millimeters(outerDiameter),
                "_i", Millimeters(innerDiameter), "x", Millimeters(depth),
                "_s", segments);
            return AddMesh(parent, name,
                GetOrCreateMesh(meshName, () => CreateRingMesh(
                    CreateCircularPerimeter(outerDiameter, segments),
                    CreateCircularPerimeter(innerDiameter, segments),
                    depth)),
                material,
                position);
        }

        private static GameObject AddRoundedRing(
            Transform parent,
            string name,
            float outerSize,
            float innerSize,
            float depth,
            float outerRadius,
            float innerRadius,
            Vector3 position,
            Material material)
        {
            const int segmentsPerCorner = 7;
            string meshName = string.Concat(name, "_", Millimeters(outerSize),
                "_i", Millimeters(innerSize), "x", Millimeters(depth));
            return AddMesh(parent, name,
                GetOrCreateMesh(meshName, () => CreateRingMesh(
                    CreateRoundedPerimeter(outerSize, outerSize, outerRadius,
                        segmentsPerCorner),
                    CreateRoundedPerimeter(innerSize, innerSize, innerRadius,
                        segmentsPerCorner),
                    depth)),
                material,
                position);
        }

        private static GameObject AddCube(
            Transform parent,
            string name,
            Vector3 size,
            Vector3 position,
            Material material)
        {
            GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cube.name = name;
            cube.transform.SetParent(parent, false);
            cube.transform.localPosition = position;
            cube.transform.localScale = size;
            Collider collider = cube.GetComponent<Collider>();
            if (collider != null)
            {
                UnityEngine.Object.DestroyImmediate(collider);
            }
            cube.GetComponent<MeshRenderer>().sharedMaterial = material;
            return cube;
        }

        private static GameObject AddMesh(
            Transform parent,
            string name,
            Mesh mesh,
            Material material,
            Vector3 position)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            gameObject.transform.localPosition = position;
            MeshFilter filter = gameObject.AddComponent<MeshFilter>();
            filter.sharedMesh = mesh;
            MeshRenderer renderer = gameObject.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
            return gameObject;
        }

        private static Mesh GetOrCreateMesh(string name, Func<Mesh> factory)
        {
            string safeName = name.Replace(" ", string.Empty);
            string path = $"{MeshRoot}/{safeName}.asset";
            Mesh generated = factory();
            generated.name = safeName;
            Mesh existing = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (existing == null)
            {
                AssetDatabase.CreateAsset(generated, path);
                return generated;
            }

            EditorUtility.CopySerialized(generated, existing);
            UnityEngine.Object.DestroyImmediate(generated);
            EditorUtility.SetDirty(existing);
            return existing;
        }

        private static Mesh CreateRoundedBoxMesh(
            float width,
            float height,
            float depth,
            float radius,
            int segmentsPerCorner)
        {
            return ExtrudePolygon(CreateRoundedPerimeter(
                width,
                height,
                radius,
                segmentsPerCorner), depth);
        }

        private static List<Vector2> CreateRoundedPerimeter(
            float width,
            float height,
            float radius,
            int segmentsPerCorner)
        {
            radius = Mathf.Min(radius, Mathf.Min(width, height) * 0.5f);
            List<Vector2> perimeter = new List<Vector2>();
            Vector2[] centers =
            {
                new Vector2(width * 0.5f - radius, -height * 0.5f + radius),
                new Vector2(width * 0.5f - radius, height * 0.5f - radius),
                new Vector2(-width * 0.5f + radius, height * 0.5f - radius),
                new Vector2(-width * 0.5f + radius, -height * 0.5f + radius)
            };
            for (int corner = 0; corner < 4; corner++)
            {
                float start = -90f + corner * 90f;
                for (int step = 0; step <= segmentsPerCorner; step++)
                {
                    if (corner > 0 && step == 0)
                    {
                        continue;
                    }
                    float angle = (start + 90f * step / segmentsPerCorner)
                        * Mathf.Deg2Rad;
                    perimeter.Add(centers[corner] + new Vector2(
                        Mathf.Cos(angle), Mathf.Sin(angle)) * radius);
                }
            }
            return perimeter;
        }

        private static Mesh CreateCylinderMesh(
            float diameter,
            float depth,
            int segments)
        {
            return ExtrudePolygon(CreateCircularPerimeter(diameter, segments), depth);
        }

        private static List<Vector2> CreateCircularPerimeter(
            float diameter,
            int segments)
        {
            List<Vector2> perimeter = new List<Vector2>(segments);
            float radius = diameter * 0.5f;
            for (int index = 0; index < segments; index++)
            {
                float angle = Mathf.PI * 2f * index / segments;
                perimeter.Add(new Vector2(Mathf.Cos(angle), Mathf.Sin(angle))
                    * radius);
            }
            return perimeter;
        }

        private static Mesh CreateRingMesh(
            IReadOnlyList<Vector2> outer,
            IReadOnlyList<Vector2> inner,
            float depth)
        {
            if (outer.Count != inner.Count)
            {
                throw new ArgumentException("Ring perimeters must have matching topology.");
            }
            int count = outer.Count;
            float front = -depth * 0.5f;
            float back = depth * 0.5f;
            List<Vector3> vertices = new List<Vector3>(count * 4);
            for (int index = 0; index < count; index++)
            {
                vertices.Add(new Vector3(outer[index].x, outer[index].y, front));
                vertices.Add(new Vector3(outer[index].x, outer[index].y, back));
                vertices.Add(new Vector3(inner[index].x, inner[index].y, front));
                vertices.Add(new Vector3(inner[index].x, inner[index].y, back));
            }
            List<int> triangles = new List<int>(count * 24);
            for (int index = 0; index < count; index++)
            {
                int next = (index + 1) % count;
                int outerFront = index * 4;
                int outerBack = outerFront + 1;
                int innerFront = outerFront + 2;
                int innerBack = outerFront + 3;
                int nextOuterFront = next * 4;
                int nextOuterBack = nextOuterFront + 1;
                int nextInnerFront = nextOuterFront + 2;
                int nextInnerBack = nextOuterFront + 3;

                AddQuad(triangles, outerFront, nextOuterFront,
                    nextInnerFront, innerFront);
                AddQuad(triangles, outerBack, innerBack,
                    nextInnerBack, nextOuterBack);
                AddQuad(triangles, outerFront, outerBack,
                    nextOuterBack, nextOuterFront);
                AddQuad(triangles, innerFront, nextInnerFront,
                    nextInnerBack, innerBack);
            }
            Mesh mesh = new Mesh();
            mesh.SetVertices(vertices);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static void AddQuad(
            List<int> triangles,
            int first,
            int second,
            int third,
            int fourth)
        {
            triangles.Add(first);
            triangles.Add(second);
            triangles.Add(third);
            triangles.Add(first);
            triangles.Add(third);
            triangles.Add(fourth);
        }

        private static Mesh ExtrudePolygon(IReadOnlyList<Vector2> perimeter, float depth)
        {
            int count = perimeter.Count;
            List<Vector3> vertices = new List<Vector3>(count * 2 + 2);
            float front = -depth * 0.5f;
            float back = depth * 0.5f;
            for (int index = 0; index < count; index++)
            {
                vertices.Add(new Vector3(perimeter[index].x, perimeter[index].y, front));
                vertices.Add(new Vector3(perimeter[index].x, perimeter[index].y, back));
            }
            int frontCenter = vertices.Count;
            vertices.Add(new Vector3(0f, 0f, front));
            int backCenter = vertices.Count;
            vertices.Add(new Vector3(0f, 0f, back));

            List<int> triangles = new List<int>(count * 12);
            for (int index = 0; index < count; index++)
            {
                int next = (index + 1) % count;
                int currentFront = index * 2;
                int currentBack = currentFront + 1;
                int nextFront = next * 2;
                int nextBack = nextFront + 1;
                triangles.Add(frontCenter);
                triangles.Add(nextFront);
                triangles.Add(currentFront);
                triangles.Add(backCenter);
                triangles.Add(currentBack);
                triangles.Add(nextBack);
                triangles.Add(currentFront);
                triangles.Add(nextFront);
                triangles.Add(nextBack);
                triangles.Add(currentFront);
                triangles.Add(nextBack);
                triangles.Add(currentBack);
            }

            Mesh mesh = new Mesh();
            mesh.SetVertices(vertices);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static Mesh CreateGemMesh()
        {
            const int segments = 10;
            List<Vector3> vertices = new List<Vector3>
            {
                new Vector3(0f, 0.039f, 0f),
                new Vector3(0f, -0.042f, 0f)
            };
            for (int index = 0; index < segments; index++)
            {
                float angle = Mathf.PI * 2f * index / segments;
                float cosine = Mathf.Cos(angle);
                float sine = Mathf.Sin(angle);
                vertices.Add(new Vector3(cosine * 0.032f, 0.010f,
                    sine * 0.032f));
                vertices.Add(new Vector3(cosine * 0.025f, -0.017f,
                    sine * 0.025f));
            }
            List<int> triangles = new List<int>();
            for (int index = 0; index < segments; index++)
            {
                int next = (index + 1) % segments;
                int upper = 2 + index * 2;
                int lower = upper + 1;
                int nextUpper = 2 + next * 2;
                int nextLower = nextUpper + 1;
                triangles.Add(0);
                triangles.Add(upper);
                triangles.Add(nextUpper);
                triangles.Add(upper);
                triangles.Add(lower);
                triangles.Add(nextLower);
                triangles.Add(upper);
                triangles.Add(nextLower);
                triangles.Add(nextUpper);
                triangles.Add(1);
                triangles.Add(nextLower);
                triangles.Add(lower);
            }
            Mesh mesh = new Mesh();
            mesh.SetVertices(vertices);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static Transform Child(Transform parent, string name)
        {
            GameObject child = new GameObject(name);
            child.transform.SetParent(parent, false);
            return child.transform;
        }

        private static string Millimeters(float meters)
        {
            return Mathf.RoundToInt(meters * 1000f).ToString();
        }

        private static void EnsureDirectories()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string[] directories =
            {
                MeshRoot,
                MaterialRoot,
                "Assets/Resources/Gacha",
                "Assets/_DisplayCase/Scenes"
            };
            foreach (string directory in directories)
            {
                Directory.CreateDirectory(Path.Combine(projectRoot, directory));
            }
            AssetDatabase.Refresh();
        }

        private readonly struct MaterialLibrary
        {
            public MaterialLibrary(
                Material matteBox,
                Material velvet,
                Material graphite,
                Material brushedMetal,
                Material placeholderGem,
                Material acrylic,
                Material acrylicEdge,
                Material badgeArtwork,
                Material previewBackground)
            {
                MatteBox = matteBox;
                Velvet = velvet;
                Graphite = graphite;
                BrushedMetal = brushedMetal;
                PlaceholderGem = placeholderGem;
                Acrylic = acrylic;
                AcrylicEdge = acrylicEdge;
                BadgeArtwork = badgeArtwork;
                PreviewBackground = previewBackground;
            }

            public Material MatteBox { get; }
            public Material Velvet { get; }
            public Material Graphite { get; }
            public Material BrushedMetal { get; }
            public Material PlaceholderGem { get; }
            public Material Acrylic { get; }
            public Material AcrylicEdge { get; }
            public Material BadgeArtwork { get; }
            public Material PreviewBackground { get; }
        }
    }
}
