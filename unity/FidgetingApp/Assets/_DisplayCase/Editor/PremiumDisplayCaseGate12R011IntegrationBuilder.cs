using System;
using System.IO;
using FidgetingApp.Product.Gacha;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    public static class PremiumDisplayCaseGate12R011IntegrationBuilder
    {
        public const string LightingProfilePath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R011Lighting.asset";
        public const string EvidenceRelativeRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/v3-rev-011";
        public const string AppScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity";
        public const int CaptureWidth = 589;
        public const int CaptureHeight = 1278;
        public const int CaptureFps = 30;
        public const int CaptureFrames = 180;

        public static string EvidenceRoot =>
            Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                EvidenceRelativeRoot));

        [MenuItem(
            "Fidgeting/Display Case/Gate 12/R011 Build Runtime Lighting And Capture")]
        public static void BuildAndCapture()
        {
            AssertFreshOutputs();
            EnsureDirectories();
            BuildLightingProfile();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            CaptureRuntimeFrames(EvidenceRoot);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log("Gate 12 R011 runtime lighting and frame capture complete.");
        }

        private static void AssertFreshOutputs()
        {
            if (AssetDatabase.LoadAssetAtPath<
                    PremiumDisplayCaseGachaLightingProfile>(
                    LightingProfilePath) != null
                || Directory.Exists(EvidenceRoot))
            {
                throw new IOException(
                    "R011 already exists. Preserve it and use a new revision.");
            }
        }

        private static void EnsureDirectories()
        {
            Directory.CreateDirectory(EvidenceRoot);
            Directory.CreateDirectory(Path.Combine(EvidenceRoot, "runtime-frames"));
            AssetDatabase.Refresh();
        }

        private static void BuildLightingProfile()
        {
            Cubemap cubemap = AssetDatabase.LoadAssetAtPath<Cubemap>(
                TriSpinnerSlabGate11ParityBuilder.ShippingCubemapPath);
            VolumeProfile volume = AssetDatabase.LoadAssetAtPath<VolumeProfile>(
                PremiumDisplayCaseGate12R009Builder.VolumeProfilePath);
            if (cubemap == null || volume == null)
            {
                throw new MissingReferenceException(
                    "R011 requires the approved Gate 09 cubemap and R009 beauty Volume.");
            }

            var profile =
                ScriptableObject.CreateInstance<
                    PremiumDisplayCaseGachaLightingProfile>();
            profile.name = "PremiumDisplayCaseGate12R011Lighting";
            profile.Configure(
                PremiumDisplayCaseGachaLightingContract.AmbientLinear,
                1f,
                cubemap,
                volume,
                PremiumDisplayCaseGachaLightingContract.CreateLightSpecs());
            AssetDatabase.CreateAsset(profile, LightingProfilePath);
        }

        public static void CaptureRuntimeFrames(string evidenceRoot)
        {
            Scene scene = EditorSceneManager.OpenScene(
                AppScenePath,
                OpenSceneMode.Single);
            Camera camera = FindMainCamera();
            PrepareAppCamera(camera);
            HideSceneProductRenderers(camera);

            var host = new GameObject("GachaShippingRevealHost");
            PremiumDisplayCaseGachaLightingScope lighting =
                PremiumDisplayCaseGachaLightingInstaller.Install(host.transform);
            if (!lighting.IsWired)
            {
                throw new InvalidOperationException(
                    "R011 runtime lighting scope is incomplete.");
            }

            var director =
                host.AddComponent<GachaShippingRevealDirector>();
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            (GachaPrizeDefinition definition, GachaDrawReceiptRow row) =
                BuildReviewReceipt();
            director.Begin(
                definition,
                row,
                1,
                prize.transform,
                false);
            director.Play();

            string frames = Path.Combine(evidenceRoot, "runtime-frames");
            for (int frame = 0; frame < CaptureFrames; frame++)
            {
                if (frame > 0)
                {
                    director.Tick(1f / CaptureFps);
                }
                TriSpinnerSlabGate11ParityBuilder.Capture(
                    camera,
                    Path.Combine(frames, $"frame-{frame:D3}.png"),
                    CaptureWidth,
                    CaptureHeight);
            }

            var report = new RuntimeCaptureReport
            {
                status = director.ActiveCase != null
                    && lighting.IsWired
                    && PremiumDisplayCaseShippingFactory.ResourcesPath
                        == PremiumDisplayCaseGate12R010ReviewBuilder.ResourcesPath
                        ? "pass"
                        : "fail",
                factoryResourcesPath =
                    PremiumDisplayCaseShippingFactory.ResourcesPath,
                activeCaseName = director.ActiveCase != null
                    ? director.ActiveCase.name
                    : string.Empty,
                lightingProfileResourcesPath =
                    PremiumDisplayCaseGachaLightingContract.ResourcesPath,
                lightingRealtimeCount = lighting.RealtimeLightCount,
                mainDirectionalLights =
                    PremiumDisplayCaseGachaLightingContract
                        .MainDirectionalLightCount,
                additionalRealtimeLights =
                    PremiumDisplayCaseGachaLightingContract
                        .AdditionalRealtimeLightCount,
                beautyVolume = lighting.Profile.BeautyVolume.name,
                reflectionCubemap = lighting.Profile.ReflectionCubemap.name,
                frameCount = CaptureFrames,
                fps = CaptureFps,
                durationSeconds = (float)CaptureFrames / CaptureFps,
                shippingElapsedSeconds = director.ShippingElapsedSeconds,
                complete = director.IsComplete,
                toyAngularVelocityZero =
                    director.ActiveCase != null
                    && director.ActiveCase.ToyAngularVelocityIsZero,
                factoryChangedAfterUserApproval = true,
                physicalPhoneInstalled = false
            };
            TriSpinnerSlabGate11ParityBuilder.WriteJson(
                Path.Combine(evidenceRoot, "runtime-capture-report.json"),
                report);
            if (report.status != "pass")
            {
                throw new InvalidOperationException(
                    "R011 runtime capture report failed.");
            }

            EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
        }

        private static Camera FindMainCamera()
        {
            Camera[] cameras = UnityEngine.Object.FindObjectsByType<Camera>(
                FindObjectsInactive.Include,
                FindObjectsSortMode.None);
            foreach (Camera camera in cameras)
            {
                if (camera.CompareTag("MainCamera"))
                {
                    return camera;
                }
            }
            throw new MissingReferenceException(
                "The shipping app scene has no MainCamera.");
        }

        private static void PrepareAppCamera(Camera camera)
        {
            foreach (Camera other in UnityEngine.Object.FindObjectsByType<Camera>(
                         FindObjectsInactive.Include,
                         FindObjectsSortMode.None))
            {
                other.enabled = other == camera;
            }
            camera.gameObject.SetActive(true);
            camera.transform.position = new Vector3(0f, 0.008f, -0.78f);
            camera.transform.rotation = Quaternion.LookRotation(
                new Vector3(0f, 0.008f, 0f) - camera.transform.position,
                Vector3.up);
            camera.orthographic = false;
            camera.usePhysicalProperties = false;
            camera.fieldOfView = 27f;
            camera.allowHDR = true;
            camera.allowMSAA = true;
            camera.aspect = (float)CaptureWidth / CaptureHeight;
            camera.GetUniversalAdditionalCameraData().renderPostProcessing = true;
        }

        private static void HideSceneProductRenderers(Camera camera)
        {
            foreach (Renderer renderer
                     in UnityEngine.Object.FindObjectsByType<Renderer>(
                         FindObjectsInactive.Exclude,
                         FindObjectsSortMode.None))
            {
                if (renderer.GetComponentInParent<Camera>() == camera)
                {
                    continue;
                }
                renderer.enabled = false;
            }
            foreach (Light light
                     in UnityEngine.Object.FindObjectsByType<Light>(
                         FindObjectsInactive.Exclude,
                         FindObjectsSortMode.None))
            {
                light.enabled = false;
            }
        }

        private static (
            GachaPrizeDefinition,
            GachaDrawReceiptRow) BuildReviewReceipt()
        {
            const string prefix =
                "fidgeting.gacha.preview.gate12-r011-runtime.";
            const string request =
                "gate12-r011-runtime-20260912";
            var inventory = new GachaInventoryRuntime(
                prefix,
                new GachaSplitMix64(0x120111UL));
            GachaTransactionResult transaction =
                inventory.QueryTransaction(request);
            if (!transaction.Success)
            {
                inventory.PrimeGate12SimulatorPreview();
                transaction = inventory.PrepareDraw(
                    GachaCatalog.LaunchSeriesId,
                    1,
                    GachaPaymentMethod.Ticket,
                    request);
            }
            if (!transaction.Success || transaction.Receipt.Rows.Count != 1)
            {
                throw new InvalidOperationException(
                    "Could not create the R011 review receipt.");
            }
            GachaDrawReceiptRow row = transaction.Receipt.Rows[0];
            return (GachaCatalog.ResolvePrize(row.Outcome.PrizeId).Value, row);
        }

        [Serializable]
        public sealed class RuntimeCaptureReport
        {
            public string status;
            public string factoryResourcesPath;
            public string activeCaseName;
            public string lightingProfileResourcesPath;
            public int lightingRealtimeCount;
            public int mainDirectionalLights;
            public int additionalRealtimeLights;
            public string beautyVolume;
            public string reflectionCubemap;
            public int frameCount;
            public int fps;
            public float durationSeconds;
            public float shippingElapsedSeconds;
            public bool complete;
            public bool toyAngularVelocityZero;
            public bool factoryChangedAfterUserApproval;
            public bool physicalPhoneInstalled;
        }
    }
}
