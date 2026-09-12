using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.Product;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    /// <summary>
    /// Replaces the rejected R009 content matrix. R010 closes source scenes
    /// before rendering, uses V3-specific rotations, fits exact mesh vertices
    /// to the circular pocket and captures a straight-on centering proof.
    /// </summary>
    public static class PremiumDisplayCaseGate12R010ReviewBuilder
    {
        public const string ResourcesFolder =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R010";
        public const string PrefabPath = ResourcesFolder + "/PresentationRoot.prefab";
        public const string ResourcesPath =
            "Gacha/PremiumDisplayCaseGate12R010/PresentationRoot";
        public const string ScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R010.unity";
        public const string EvidenceRelativeRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/v3-rev-010";
        public const string ReportFile = "gate12-r010-review-report.json";
        public const int PocketCaptureSize = 1600;
        public const float MaximumCenterErrorMm = 0.05f;
        public const float MaximumScreenCenterErrorPixels = 1f;
        public const float MaximumRadialOverflowMm = 0.05f;
        public const float MaximumDepthOverflowMm = 0.05f;

        private static readonly string[] RarityWords =
        {
            "STANDARD",
            "REFINED",
            "SIGNATURE",
            "HEIRLOOM"
        };

        public static string EvidenceRoot =>
            Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                EvidenceRelativeRoot));

        [MenuItem(
            "Fidgeting/Display Case/Gate 12/Tri-Spinner Slab R010 Build Reviewed Matrix")]
        public static void BuildAndCapture()
        {
            TriSpinnerSlabGate11ParityBuilder.AssertSourceAndShippingHashes();
            AssertFreshOutputs();
            EnsureDirectories();
            BuildPrefab();

            var report = new ReviewReport
            {
                candidatePrefab = PrefabPath,
                shippingFactoryResourcesPath =
                    PremiumDisplayCaseShippingFactory.ResourcesPath,
                sourcePrefab = PremiumDisplayCaseGate12R009Builder.PrefabPath,
                governingContractSha256 =
                    "e9a6f14a61e823274c716f3b3c26ee63e0bbc8e5879145e7b98c65aa9ea88294"
            };
            CaptureContentMatrix(report);
            CaptureRarityMatrix(report);
            SaveReviewScene();
            report.status = report.failures.Count == 0 ? "pass" : "fail";
            TriSpinnerSlabGate11ParityBuilder.WriteJson(
                Path.Combine(EvidenceRoot, ReportFile),
                report);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            TriSpinnerSlabGate11ParityBuilder.AssertSourceAndShippingHashes();
            if (report.status != "pass")
            {
                throw new InvalidOperationException(
                    "Gate 12 R010 review failed: "
                    + string.Join("; ", report.failures));
            }

            Debug.Log("Gate 12 R010 reviewed content and rarity matrices complete.");
        }

        private static void AssertFreshOutputs()
        {
            if (AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath) != null
                || AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) != null
                || Directory.Exists(EvidenceRoot))
            {
                throw new IOException(
                    "R010 already exists. Preserve it and use a new revision.");
            }
        }

        private static void EnsureDirectories()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            foreach (string relative in new[]
                     {
                         ResourcesFolder,
                         "Assets/_DisplayCase/Scenes",
                         EvidenceRelativeRoot,
                         EvidenceRelativeRoot + "/content",
                         EvidenceRelativeRoot + "/rarity"
                     })
            {
                Directory.CreateDirectory(Path.Combine(project, relative));
            }
            AssetDatabase.Refresh();
        }

        private static void BuildPrefab()
        {
            GameObject source = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12R009Builder.PrefabPath);
            if (source == null)
            {
                throw new MissingReferenceException("R009 candidate prefab is missing.");
            }

            GameObject root = (GameObject)PrefabUtility.InstantiatePrefab(source);
            try
            {
                PrefabUtility.UnpackPrefabInstance(
                    root,
                    PrefabUnpackMode.OutermostRoot,
                    InteractionMode.AutomatedAction);
                root.name = PremiumDisplayCaseGate12R009Builder.RootName;
                Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
                Renderer header = renderers.Single(
                    item => item.name
                        == PremiumDisplayCaseGate12R009Builder.HeaderPlaneName);
                Renderer[] liner = ByMaterial(renderers, "M_PDC_SmokeLiner");
                Renderer[] frame = ByMaterial(renderers, "M_PDC_BrushedSteel");
                Renderer[] polished = ByMaterial(renderers, "M_PDC_Mirror");
                Renderer[] accent = ByMaterial(renderers, "M_PDC_AccentMetal");
                Transform labels = root.transform.Find(
                    PremiumDisplayCaseGate12R009Builder.HeaderLabelRootName);
                Renderer rarity = labels.Find("LABEL_RARITY").GetComponent<Renderer>();
                Renderer rule = labels.Find("LABEL_RULE").GetComponent<Renderer>();
                var cmf = root.AddComponent<PremiumDisplayCaseV3RarityCmf>();
                cmf.Configure(
                    header,
                    liner,
                    frame,
                    polished,
                    accent,
                    rarity,
                    rule);
                if (!cmf.IsWired)
                {
                    throw new InvalidOperationException(
                        "R010 rarity CMF did not bind every material zone.");
                }

                PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static Renderer[] ByMaterial(
            Renderer[] renderers,
            string materialName)
        {
            return renderers.Where(renderer =>
                    renderer.sharedMaterials.Any(material =>
                        material != null
                        && material.name.StartsWith(
                            materialName,
                            StringComparison.Ordinal)))
                .ToArray();
        }

        private static void CaptureContentMatrix(ReviewReport report)
        {
            Scene reviewScene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            ReviewRig rig = CreateReviewRig(reviewScene);

            foreach (ProductCatalogEntry entry in ProductCatalog.ShippingEntries)
            {
                ProductReview record = CaptureProduct(
                    reviewScene,
                    rig,
                    entry,
                    report);
                report.products.Add(record);
            }

            EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
        }

        private static ProductReview CaptureProduct(
            Scene reviewScene,
            ReviewRig rig,
            ProductCatalogEntry entry,
            ReviewReport report)
        {
            PremiumDisplayCaseProductProfile productProfile =
                PremiumDisplayCaseProductProfiles.Resolve(entry.ModelId);
            PremiumDisplayCasePocketContentProfile pocketProfile =
                PremiumDisplayCaseV3PocketProfiles.Resolve(entry.ModelId);
            var record = new ProductReview
            {
                modelId = entry.ModelId,
                scenePath = entry.ScenePath,
                sourceRoot = productProfile.SceneRootName,
                initialEuler = ToArray(pocketProfile.InitialEulerAngles),
                anchor = pocketProfile.Anchor.ToString()
            };

            PremiumDisplayCaseShippingPresentation presentation = null;
            GameObject content = null;
            try
            {
                presentation = SpawnPresentation(reviewScene);
                presentation.SetLabel(ProductLabel(entry.ModelId, productProfile));
                presentation.SetTimeForPreview(
                    presentation.RevealProfile.TotalDurationSeconds);
                content = CreateContentSnapshot(reviewScene, entry, productProfile);
                PremiumDisplayCasePocketFitResult fit =
                    presentation.AttachContentToCircularPocket(
                        content.transform,
                        pocketProfile);
                record.uniformScale = fit.UniformScale;
                record.radialExtentMm = fit.RadialExtentMeters * 1000f;
                record.depthMm = fit.DepthMeters * 1000f;
                record.centerOffsetMm = ToMillimetres(
                    fit.CenterOffsetSlotLocal);
                record.occupancy = fit.RadialExtentMeters
                    / (pocketProfile.FitDiameterMeters * 0.5f);
                record.rendererCount = content
                    .GetComponentsInChildren<Renderer>(true)
                    .Count(renderer => renderer.enabled);

                SetPocketFrontCamera(rig.Camera, presentation.ContentSlot);
                record.screenCenterErrorPixels = MeasureScreenCenterError(
                    rig.Camera,
                    presentation.ContentSlot,
                    fit.CenterOffsetSlotLocal,
                    PocketCaptureSize);
                record.pocketFrontFile =
                    $"content/{entry.ModelId}-pocket-front.png";
                TriSpinnerSlabGate11ParityBuilder.Capture(
                    rig.Camera,
                    Path.Combine(EvidenceRoot, record.pocketFrontFile),
                    PocketCaptureSize,
                    PocketCaptureSize);

                record.phoneFrontFile =
                    $"content/{entry.ModelId}-phone-front.png";
                SetPhoneCamera(rig.Camera, presentation.transform, 0f);
                TriSpinnerSlabGate11ParityBuilder.Capture(
                    rig.Camera,
                    Path.Combine(EvidenceRoot, record.phoneFrontFile),
                    PremiumDisplayCaseGate12R009Builder.PhoneWidth,
                    PremiumDisplayCaseGate12R009Builder.PhoneHeight);

                record.phoneQuarterFile =
                    $"content/{entry.ModelId}-phone-quarter.png";
                SetPhoneCamera(rig.Camera, presentation.transform, 28f);
                TriSpinnerSlabGate11ParityBuilder.Capture(
                    rig.Camera,
                    Path.Combine(EvidenceRoot, record.phoneQuarterFile),
                    PremiumDisplayCaseGate12R009Builder.PhoneWidth,
                    PremiumDisplayCaseGate12R009Builder.PhoneHeight);
                ValidateProduct(record, pocketProfile, report);
            }
            catch (Exception exception)
            {
                record.error = exception.Message;
                report.failures.Add(entry.ModelId + ": " + exception.Message);
            }
            finally
            {
                if (presentation != null)
                {
                    presentation.DetachContent();
                }
                if (content != null)
                {
                    UnityEngine.Object.DestroyImmediate(content);
                }
                if (presentation != null)
                {
                    UnityEngine.Object.DestroyImmediate(presentation.gameObject);
                }
            }

            return record;
        }

        private static GameObject CreateContentSnapshot(
            Scene reviewScene,
            ProductCatalogEntry entry,
            PremiumDisplayCaseProductProfile profile)
        {
            if (entry.ModelId == ProductCatalog.MetalThreeBladeModelId)
            {
                GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
                SceneManager.MoveGameObjectToScene(prize, reviewScene);
                return prize;
            }

            Scene productScene = EditorSceneManager.OpenScene(
                entry.ScenePath,
                OpenSceneMode.Additive);
            GameObject fallback = null;
            try
            {
                Transform root = FindRoot(productScene, profile.SceneRootName);
                GameObject snapshot;
                try
                {
                    snapshot = PremiumDisplayCaseProductSnapshot.Capture(
                        entry.ModelId,
                        root);
                }
                catch (MissingReferenceException) when (
                    entry.ModelId == ProductCatalog.MagneticSlideTileModelId)
                {
                    const string edcPrefab = "Assets/_EDC/Prefabs/EDC_Root.prefab";
                    GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                        edcPrefab);
                    if (prefab == null)
                    {
                        throw new MissingReferenceException(
                            "The magnetic-slide shipping prefab is missing.");
                    }
                    fallback = (GameObject)PrefabUtility.InstantiatePrefab(
                        prefab,
                        productScene);
                    fallback.SetActive(true);
                    snapshot = PremiumDisplayCaseProductSnapshot.Capture(
                        entry.ModelId,
                        fallback.transform);
                }

                SceneManager.MoveGameObjectToScene(snapshot, reviewScene);
                snapshot.SetActive(true);
                return snapshot;
            }
            finally
            {
                if (fallback != null)
                {
                    UnityEngine.Object.DestroyImmediate(fallback);
                }
                EditorSceneManager.CloseScene(productScene, true);
                EditorSceneManager.SetActiveScene(reviewScene);
            }
        }

        private static Transform FindRoot(Scene scene, string name)
        {
            foreach (GameObject root in scene.GetRootGameObjects())
            {
                if (root.name == name)
                {
                    return root.transform;
                }
                Transform nested = root.GetComponentsInChildren<Transform>(true)
                    .FirstOrDefault(item => item.name == name);
                if (nested != null)
                {
                    return nested;
                }
            }
            throw new MissingReferenceException(
                $"Scene {scene.path} has no {name} root.");
        }

        private static void ValidateProduct(
            ProductReview record,
            PremiumDisplayCasePocketContentProfile profile,
            ReviewReport report)
        {
            float centerError = Mathf.Max(
                Mathf.Abs(record.centerOffsetMm[0]),
                Mathf.Abs(record.centerOffsetMm[1]));
            if (centerError > MaximumCenterErrorMm)
            {
                report.failures.Add(
                    $"{record.modelId} center error {centerError:F3} mm");
            }
            float fitRadiusMm =
                PremiumDisplayCaseV3PocketProfiles.FitDiameterMeters * 500f;
            if (record.radialExtentMm > fitRadiusMm + MaximumRadialOverflowMm)
            {
                report.failures.Add(
                    $"{record.modelId} radial extent "
                    + $"{record.radialExtentMm:F2} mm > {fitRadiusMm:F2} mm");
            }
            float fitDepthMm = profile.ReferenceDepthMeters * 1000f;
            if (profile.ConstrainScaleByDepth
                && record.depthMm > fitDepthMm + MaximumDepthOverflowMm)
            {
                report.failures.Add(
                    $"{record.modelId} depth "
                    + $"{record.depthMm:F2} mm > {fitDepthMm:F2} mm");
            }
            if (record.screenCenterErrorPixels > MaximumScreenCenterErrorPixels)
            {
                report.failures.Add(
                    $"{record.modelId} screen center error "
                    + $"{record.screenCenterErrorPixels:F2} px");
            }
            if (record.rendererCount == 0)
            {
                report.failures.Add(record.modelId + " has no visible renderers");
            }

            float minimumOccupancy;
            switch (record.modelId)
            {
                case ProductCatalog.GraphiteTwoLobeModelId:
                    minimumOccupancy = 0.75f;
                    break;
                case ProductCatalog.MagneticSlideTileModelId:
                    minimumOccupancy = 0.72f;
                    break;
                default:
                    minimumOccupancy = 0.90f;
                    break;
            }
            if (record.occupancy < minimumOccupancy || record.occupancy > 1.002f)
            {
                report.failures.Add(
                    $"{record.modelId} occupancy {record.occupancy:F3} "
                    + $"outside {minimumOccupancy:F2}-1.002");
            }
        }

        private static void CaptureRarityMatrix(ReviewReport report)
        {
            Scene reviewScene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            ReviewRig rig = CreateReviewRig(reviewScene);
            PremiumDisplayCaseShippingPresentation presentation =
                SpawnPresentation(reviewScene);
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            SceneManager.MoveGameObjectToScene(prize, reviewScene);
            presentation.AttachContentToCircularPocket(
                prize.transform,
                PremiumDisplayCaseV3PocketProfiles.Resolve(
                    ProductCatalog.MetalThreeBladeModelId));
            presentation.SetTimeForPreview(
                presentation.RevealProfile.TotalDurationSeconds);

            for (int index = 0; index < RarityWords.Length; index++)
            {
                string rarity = RarityWords[index];
                presentation.SetLabel(new PremiumDisplayCaseLabelData(
                    "GEEONE TRI-SPINNER",
                    "SATIN STEEL · DRAGON SCALE",
                    "2026-09-11",
                    rarity,
                    $"R010-{index + 1:D2}"));
                PremiumDisplayCaseV3RarityCmf cmf =
                    presentation.GetComponent<PremiumDisplayCaseV3RarityCmf>();
                string tier = cmf.Tier.ToString().ToLowerInvariant();
                var record = new RarityReview
                {
                    rarityWord = rarity,
                    tier = cmf.Tier.ToString(),
                    accentSrgb = ToArray(
                        PremiumDisplayCaseV3RarityCmf.AccentSrgb(cmf.Tier)),
                    linerSrgb = ToArray(
                        PremiumDisplayCaseV3RarityCmf.LinerSrgb(cmf.Tier)),
                    headerSrgb = ToArray(
                        PremiumDisplayCaseV3RarityCmf.HeaderSrgb(cmf.Tier)),
                    phoneFrontFile = $"rarity/{tier}-phone-front.png",
                    headerFrontFile = $"rarity/{tier}-header-front.png"
                };

                SetPhoneCamera(rig.Camera, presentation.transform, 0f);
                TriSpinnerSlabGate11ParityBuilder.Capture(
                    rig.Camera,
                    Path.Combine(EvidenceRoot, record.phoneFrontFile),
                    PremiumDisplayCaseGate12R009Builder.PhoneWidth,
                    PremiumDisplayCaseGate12R009Builder.PhoneHeight);
                SetHeaderFrontCamera(rig.Camera);
                TriSpinnerSlabGate11ParityBuilder.Capture(
                    rig.Camera,
                    Path.Combine(EvidenceRoot, record.headerFrontFile),
                    1600,
                    900);
                report.rarities.Add(record);
            }

            presentation.DetachContent();
            UnityEngine.Object.DestroyImmediate(prize);
            UnityEngine.Object.DestroyImmediate(presentation.gameObject);
            EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
        }

        private static void SaveReviewScene()
        {
            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            CreateReviewRig(scene);
            PremiumDisplayCaseShippingPresentation presentation =
                SpawnPresentation(scene);
            presentation.SetLabel(new PremiumDisplayCaseLabelData(
                "GEEONE TRI-SPINNER",
                "SATIN STEEL · DRAGON SCALE",
                "2026-09-11",
                "HEIRLOOM",
                "R010-SCENE"));
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            SceneManager.MoveGameObjectToScene(prize, scene);
            presentation.AttachContentToCircularPocket(
                prize.transform,
                PremiumDisplayCaseV3PocketProfiles.Resolve(
                    ProductCatalog.MetalThreeBladeModelId));
            presentation.SetTimeForPreview(
                presentation.RevealProfile.TotalDurationSeconds);
            EditorSceneManager.SaveScene(scene, ScenePath);
        }

        private static PremiumDisplayCaseShippingPresentation SpawnPresentation(
            Scene scene)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException("R010 candidate prefab is missing.");
            }
            var presentation = ((GameObject)PrefabUtility.InstantiatePrefab(
                prefab,
                scene)).GetComponent<PremiumDisplayCaseShippingPresentation>();
            presentation.transform.SetPositionAndRotation(
                Vector3.zero,
                Quaternion.identity);
            return presentation;
        }

        private static PremiumDisplayCaseLabelData ProductLabel(
            string modelId,
            PremiumDisplayCaseProductProfile profile)
        {
            string finish;
            switch (modelId)
            {
                case ProductCatalog.GraphiteTwoLobeModelId:
                    finish = "GRAPHITE · SATIN";
                    break;
                case ProductCatalog.MagneticSlideTileModelId:
                    finish = "MAGNETIC SLIDE · DUAL PLATE";
                    break;
                case ProductCatalog.MagneticFanCardModelId:
                    finish = "A/Q/K FAN · SATIN SILVER";
                    break;
                default:
                    finish = "SATIN STEEL · DRAGON SCALE";
                    break;
            }
            return new PremiumDisplayCaseLabelData(
                profile.EnglishDisplayName,
                finish,
                "2026-09-11",
                "STANDARD",
                "R010-" + modelId);
        }

        private static ReviewRig CreateReviewRig(Scene scene)
        {
            TriSpinnerSlabGate11ParityBuilder.ParityReference reference =
                TriSpinnerSlabGate11ParityBuilder.LoadReference();
            var cubemap = AssetDatabase.LoadAssetAtPath<Cubemap>(
                TriSpinnerSlabGate11ParityBuilder.ShippingCubemapPath);
            if (cubemap == null)
            {
                throw new MissingReferenceException(
                    "Gate 11 shipping cubemap is missing.");
            }

            Transform environment =
                new GameObject("Gate12R010ReviewEnvironment").transform;
            SceneManager.MoveGameObjectToScene(environment.gameObject, scene);
            Camera camera =
                TriSpinnerSlabGate11ParityBuilder.CreateCamera(environment);
            TriSpinnerSlabGate11ParityBuilder.ApplyRig(
                environment,
                camera,
                reference.shippingLights,
                reference.shippingWorld,
                cubemap,
                "Gate12R010");
            UniversalAdditionalCameraData additional =
                camera.GetUniversalAdditionalCameraData();
            additional.renderPostProcessing = true;
            var volumeObject = new GameObject("Gate12R010BeautyVolume");
            SceneManager.MoveGameObjectToScene(volumeObject, scene);
            Volume volume = volumeObject.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(
                PremiumDisplayCaseGate12R009Builder.VolumeProfilePath);
            return new ReviewRig(environment, camera);
        }

        private static void SetPocketFrontCamera(Camera camera, Transform slot)
        {
            const float focalLength = 85f;
            const float fitFraction = 0.82f;
            float halfHorizontalFov = Mathf.Atan(18f / focalLength);
            float pocketDiameter = 0.0739f;
            float distance = pocketDiameter
                / (2f * fitFraction * Mathf.Tan(halfHorizontalFov));
            camera.orthographic = false;
            camera.usePhysicalProperties = true;
            camera.focalLength = focalLength;
            camera.sensorSize = new Vector2(36f, 36f);
            camera.gateFit = Camera.GateFitMode.Horizontal;
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.transform.position = new Vector3(
                slot.position.x,
                slot.position.y,
                slot.position.z - distance);
            camera.transform.rotation = Quaternion.identity;
        }

        private static void SetHeaderFrontCamera(Camera camera)
        {
            const float focalLength = 85f;
            const float headerWidth = 0.08148f;
            const float fitFraction = 0.82f;
            float halfHorizontalFov = Mathf.Atan(18f / focalLength);
            float distance = headerWidth
                / (2f * fitFraction * Mathf.Tan(halfHorizontalFov));
            camera.orthographic = false;
            camera.usePhysicalProperties = true;
            camera.focalLength = focalLength;
            camera.sensorSize = new Vector2(36f, 20.25f);
            camera.gateFit = Camera.GateFitMode.Horizontal;
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.transform.position = new Vector3(0f, 0.0558f, -distance);
            camera.transform.rotation = Quaternion.identity;
        }

        private static void SetPhoneCamera(
            Camera camera,
            Transform presentation,
            float yaw)
        {
            presentation.rotation = Quaternion.Euler(0f, yaw, 0f);
            camera.orthographic = false;
            camera.usePhysicalProperties = true;
            camera.focalLength =
                PremiumDisplayCaseGate12R009Builder.PhoneFocalLengthMm;
            camera.sensorSize = new Vector2(36f, 24f);
            camera.gateFit = Camera.GateFitMode.Horizontal;
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            float halfHorizontalFov = Mathf.Atan(
                18f
                / PremiumDisplayCaseGate12R009Builder.PhoneFocalLengthMm);
            float distance = 0.10128f
                / (2f
                    * PremiumDisplayCaseGate12R009Builder.PhoneCaseWidthFraction
                    * Mathf.Tan(halfHorizontalFov));
            camera.transform.position = new Vector3(0f, 0f, -distance);
            camera.transform.rotation = Quaternion.identity;
        }

        private static float MeasureScreenCenterError(
            Camera camera,
            Transform slot,
            Vector3 centerOffsetSlotLocal,
            int pixelSize)
        {
            Vector3 slotViewport = camera.WorldToViewportPoint(slot.position);
            Vector3 centerViewport = camera.WorldToViewportPoint(
                slot.TransformPoint(centerOffsetSlotLocal));
            return Vector2.Distance(
                new Vector2(slotViewport.x, slotViewport.y),
                new Vector2(centerViewport.x, centerViewport.y))
                * pixelSize;
        }

        private static float[] ToArray(Vector3 value)
        {
            return new[] { value.x, value.y, value.z };
        }

        private static float[] ToArray(Color value)
        {
            return new[] { value.r, value.g, value.b, value.a };
        }

        private static float[] ToMillimetres(Vector3 value)
        {
            return new[]
            {
                value.x * 1000f,
                value.y * 1000f,
                value.z * 1000f
            };
        }

        private readonly struct ReviewRig
        {
            public ReviewRig(Transform environment, Camera camera)
            {
                Environment = environment;
                Camera = camera;
            }

            public Transform Environment { get; }
            public Camera Camera { get; }
        }

        [Serializable]
        public sealed class ReviewReport
        {
            public string status;
            public string candidatePrefab;
            public string sourcePrefab;
            public string shippingFactoryResourcesPath;
            public string governingContractSha256;
            public List<ProductReview> products = new List<ProductReview>();
            public List<RarityReview> rarities = new List<RarityReview>();
            public List<string> failures = new List<string>();
        }

        [Serializable]
        public sealed class ProductReview
        {
            public string modelId;
            public string scenePath;
            public string sourceRoot;
            public float[] initialEuler;
            public string anchor;
            public float uniformScale;
            public float radialExtentMm;
            public float depthMm;
            public float[] centerOffsetMm;
            public float occupancy;
            public float screenCenterErrorPixels;
            public int rendererCount;
            public string pocketFrontFile;
            public string phoneFrontFile;
            public string phoneQuarterFile;
            public string error;
        }

        [Serializable]
        public sealed class RarityReview
        {
            public string rarityWord;
            public string tier;
            public float[] accentSrgb;
            public float[] linerSrgb;
            public float[] headerSrgb;
            public string phoneFrontFile;
            public string headerFrontFile;
        }
    }
}
