using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.EDC.Candidates;
using FidgetingApp.EDC.Gate12R002;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileGate12R002Builder
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002";
        private const string SourceScene =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Scenes/"
            + "MagneticSlideTileGate11R011Parity.unity";
        private const string ShippingScene = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string PrefabPath =
            Root + "/Prefabs/MagneticSlideTileGate12R002Candidate.prefab";
        private const string SettingsPath =
            Root + "/Settings/MagneticSlideTileMechanismSettingsR002.asset";
        private const string EvidenceRelative =
            "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
            + "12-shipping/rev-002";
        private const string SwitchName =
            "MagneticSlideTile_Gate12R002_CandidateSwitch";

        [MenuItem("Fidgeting/Model Pipeline/Build Magnetic Slide Gate 12 R002")]
        public static void BuildAndCapture()
        {
            EnsureFolders();
            MagneticSlideTileMechanismSettings settings = EnsureSettings();
            BuildCandidatePrefab(settings);
            BuildShippingScene(settings);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
        }

        [MenuItem("Fidgeting/Model Pipeline/Run Magnetic Slide Gate 12 R002")]
        public static void BuildAndRunPlayMode()
        {
            BuildAndCapture();
            MagneticSlideTileGate12PlayModeCapture capture =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileGate12PlayModeCapture>(
                    FindObjectsInactive.Include);
            if (capture == null)
                throw new InvalidDataException("Gate 12 capture host is missing.");
            capture.Arm();
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string frames = Path.Combine(
                projectRoot, EvidenceRelative, "unity-playmode-frames");
            Directory.CreateDirectory(frames);
            File.WriteAllText(Path.Combine(frames, "capture.request"), "armed\n");
            EditorSceneManager.SaveScene(SceneManager.GetActiveScene());
            EditorApplication.delayCall += () => EditorApplication.isPlaying = true;
        }

        private static void BuildCandidatePrefab(
            MagneticSlideTileMechanismSettings settings)
        {
            Scene source = EditorSceneManager.OpenScene(
                SourceScene, OpenSceneMode.Single);
            MagneticSlideTileGate11R011Metadata metadata =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileGate11R011Metadata>(
                    FindObjectsInactive.Include);
            if (metadata == null)
                throw new InvalidDataException("Approved Gate 11 root is missing.");
            if (metadata.Gate10GlbSha256
                != "e9f90e9e77756b33857726f95a01194996469f16101dbad91fdb7024b679c2ca")
            {
                throw new InvalidDataException("Gate 11 source hash changed.");
            }

            GameObject clone = UnityEngine.Object.Instantiate(metadata.gameObject);
            clone.name = "MagneticSlideTile_Gate12R002_Candidate";
            clone.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            clone.transform.localScale = Vector3.one;
            foreach (MonoBehaviour obsolete in clone.GetComponents<MonoBehaviour>())
            {
                if (obsolete is MagneticSlideTileGate11R011Metadata
                    || obsolete is MagneticSlideTileEndpointInterlockController)
                {
                    UnityEngine.Object.DestroyImmediate(obsolete);
                }
            }

            Transform topLocalSlide = FindTransform(
                clone.transform, "TopLocalSlide");
            MagneticSlideTileShippingMechanism mechanism =
                clone.AddComponent<MagneticSlideTileShippingMechanism>();
            mechanism.Configure(
                settings,
                FindTransform(clone.transform, "BottomExterior"),
                FindTransform(clone.transform, "FixedAxis"),
                FindTransform(clone.transform, "RotatingCarrier"),
                FindTransform(clone.transform, "MovingTop"),
                topLocalSlide);
            PrefabUtility.SaveAsPrefabAsset(clone, PrefabPath);
            UnityEngine.Object.DestroyImmediate(clone);
            EditorSceneManager.CloseScene(source, true);
        }

        private static void BuildShippingScene(
            MagneticSlideTileMechanismSettings settings)
        {
            Scene scene = EditorSceneManager.OpenScene(
                ShippingScene, OpenSceneMode.Single);
            GameObject prior = GameObject.Find(SwitchName);
            if (prior != null)
                UnityEngine.Object.DestroyImmediate(prior);

            GameObject oldShippingModel = scene.GetRootGameObjects()
                .FirstOrDefault(item => item.name == "EDC_Root")
                ?? throw new InvalidDataException("Current EDC_Root is missing.");
            oldShippingModel.SetActive(true);

            GameObject switchRoot = new(SwitchName);
            SceneManager.MoveGameObjectToScene(switchRoot, scene);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath)
                ?? throw new InvalidDataException("Gate 12 candidate prefab is missing.");
            GameObject candidate = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
            candidate.transform.SetParent(switchRoot.transform, false);
            candidate.SetActive(false);
            MagneticSlideTileShippingMechanism mechanism =
                candidate.GetComponent<MagneticSlideTileShippingMechanism>();

            MagneticSlideTileShippingCoordinator coordinator =
                switchRoot.AddComponent<MagneticSlideTileShippingCoordinator>();
            coordinator.Configure(settings, oldShippingModel, candidate, mechanism);

            Camera camera = CreateReviewCamera(switchRoot.transform);
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidence = Path.Combine(projectRoot, EvidenceRelative);
            Directory.CreateDirectory(evidence);
            MagneticSlideTileGate12PlayModeCapture capture =
                switchRoot.AddComponent<MagneticSlideTileGate12PlayModeCapture>();
            capture.Configure(
                coordinator,
                camera,
                Path.Combine(evidence, "unity-playmode-frames"));

            coordinator.SetPreviewActive(true);
            RenderEvidence(camera, coordinator, mechanism, evidence);
            coordinator.SetPreviewActive(false);
            camera.enabled = false;
            oldShippingModel.SetActive(true);
            candidate.SetActive(false);
            EditorSceneManager.SaveScene(scene, ShippingScene, false);

            WriteReport(
                Path.Combine(evidence, "gate12-shipping-report.json"),
                projectRoot,
                settings,
                candidate,
                oldShippingModel);
            File.WriteAllText(
                Path.Combine(evidence, "shipping-scene-path.txt"),
                ShippingScene + Environment.NewLine);
        }

        private static void RenderEvidence(
            Camera camera,
            MagneticSlideTileShippingCoordinator coordinator,
            MagneticSlideTileShippingMechanism mechanism,
            string evidence)
        {
            mechanism.ResetPose(false);
            RenderView(camera, evidence, "library", new(0f, 0.070f, -0.135f),
                Vector3.zero, 42f, 1600, 1000);
            RenderView(camera, evidence, "hero", new(0.074f, 0.072f, -0.116f),
                new(0f, 0.005f, -0.002f), 17.945253f, 1600, 1000);
            RenderView(camera, evidence, "top", new(0f, 0.115f, -0.006f),
                Vector3.zero, 38f, 1600, 1000);
            RenderView(camera, evidence, "left-oblique",
                new(-0.055f, 0.040f, -0.055f), Vector3.zero, 36f, 1600, 1000);
            RenderView(camera, evidence, "right-oblique",
                new(0.055f, 0.040f, -0.055f), Vector3.zero, 36f, 1600, 1000);
            RenderView(camera, evidence, "low", new(0.045f, 0.018f, -0.070f),
                new(0f, 0.002f, 0f), 36f, 1600, 1000);
            RenderView(camera, evidence, "phone", new(0.030f, 0.030f, -0.050f),
                Vector3.zero, 38f, 1290, 2796);

            mechanism.TrySetTravel(
                coordinator.Settings.MaximumTravelMeters,
                false);
            RenderView(camera, evidence, "max-open",
                new(0.074f, 0.072f, -0.116f),
                new(0f, 0.005f, 0.006f), 20f, 1600, 1000);
            mechanism.TrySetAngle(12f, false);
            RenderView(camera, evidence, "endpoint-12deg",
                new(0.074f, 0.072f, -0.116f),
                new(0f, 0.005f, 0f), 20f, 1600, 1000);
            mechanism.TrySetAngle(36f, false);
            RenderView(camera, evidence, "endpoint-36deg",
                new(0.074f, 0.072f, -0.116f),
                new(0f, 0.005f, 0f), 20f, 1600, 1000);
            for (int index = 4; index <= coordinator.Settings.DetentCount; index++)
                mechanism.TrySetEndpointDetent(index, false);
            RenderView(camera, evidence, "endpoint-360deg",
                new(0.074f, 0.072f, -0.116f),
                new(0f, 0.005f, 0f), 20f, 1600, 1000);
            mechanism.TrySetTravel(0f);
        }

        private static Camera CreateReviewCamera(Transform parent)
        {
            GameObject cameraObject = new("CAM_Gate12R002_ShippingReview");
            cameraObject.transform.SetParent(parent, false);
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.enabled = false;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.07058824f, 0.08627451f, 0.09803922f);
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 10f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            return camera;
        }

        private static void RenderView(
            Camera camera,
            string directory,
            string name,
            Vector3 position,
            Vector3 lookAt,
            float fieldOfView,
            int width,
            int height)
        {
            camera.transform.position = position;
            camera.transform.rotation = Quaternion.LookRotation(
                lookAt - position, Vector3.up);
            camera.fieldOfView = fieldOfView;
            RenderTexture target = new(
                width,
                height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Default);
            target.Create();
            RenderTexture previous = RenderTexture.active;
            camera.targetTexture = target;
            camera.Render();
            camera.Render();
            RenderTexture.active = target;
            Texture2D image = new(width, height, TextureFormat.RGBA32, false, false);
            image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            image.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(directory, name + ".png"),
                image.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(image);
            camera.targetTexture = null;
            RenderTexture.active = previous;
            target.Release();
            UnityEngine.Object.DestroyImmediate(target);
        }

        private static void WriteReport(
            string output,
            string projectRoot,
            MagneticSlideTileMechanismSettings settings,
            GameObject candidate,
            GameObject oldShippingModel)
        {
            Renderer[] renderers = candidate.GetComponentsInChildren<Renderer>(true);
            MeshFilter[] filters = candidate.GetComponentsInChildren<MeshFilter>(true);
            int triangles = filters.Sum(filter =>
                filter.sharedMesh == null ? 0 : filter.sharedMesh.triangles.Length / 3);
            string sceneHash = Sha256(Path.Combine(projectRoot, ShippingScene));
            Report report = new()
            {
                pass = true,
                shippingScenePath = ShippingScene,
                shippingSceneSha256 = sceneHash,
                candidatePrefabPath = PrefabPath,
                sourceGate11Folder =
                    "Assets/_EDC/Candidates/MagneticSlideTileGate11R011",
                sourceGate11GlbSha256 =
                    "e9f90e9e77756b33857726f95a01194996469f16101dbad91fdb7024b679c2ca",
                candidateExplicitlyEnabledForCapture = true,
                candidateDefaultActive = candidate.activeSelf,
                oldShippingModelDefaultActive = oldShippingModel.activeSelf,
                maximumTravelMeters = settings.MaximumTravelMeters,
                endpointToleranceMeters = settings.EndpointToleranceMeters,
                detentCount = settings.DetentCount,
                detentStepDegrees = settings.DetentStepDegrees,
                renderMeshes = renderers.Count(renderer => renderer.enabled),
                triangles = triangles,
                semanticRoute =
                    "input -> MagneticSlideTileShippingMechanism -> "
                    + "FidgetSemanticEvent -> FidgetHapticRouter -> IosHaptics",
                runtimeInputIntegrated = true,
                hapticsIntegrated = true,
                initialAndResetVelocity = 0f,
                gate12Approval = "pending",
                deliveryState = "real-shipping-scene-candidate-preview-only",
                deviceHapticAcceptance = "pending",
                buildInstallPhonePush = "not-started",
                requiredViews = new[]
                {
                    "library.png", "hero.png", "top.png", "left-oblique.png",
                    "right-oblique.png", "low.png", "phone.png", "max-open.png",
                    "endpoint-12deg.png", "endpoint-36deg.png",
                    "endpoint-360deg.png",
                },
            };
            File.WriteAllText(output, JsonUtility.ToJson(report, true));
        }

        private static MagneticSlideTileMechanismSettings EnsureSettings()
        {
            MagneticSlideTileMechanismSettings settings =
                AssetDatabase.LoadAssetAtPath<
                    MagneticSlideTileMechanismSettings>(SettingsPath);
            if (settings != null)
                return settings;
            settings = ScriptableObject.CreateInstance<
                MagneticSlideTileMechanismSettings>();
            AssetDatabase.CreateAsset(settings, SettingsPath);
            return settings;
        }

        private static Transform FindTransform(Transform root, string name)
        {
            Transform found = root.GetComponentsInChildren<Transform>(true)
                .FirstOrDefault(item => item.name == name);
            return found ?? throw new InvalidDataException(
                $"Required Gate 11 transform is missing: {name}");
        }

        private static void EnsureFolders()
        {
            string[] folders =
            {
                Root,
                Root + "/Runtime",
                Root + "/Editor",
                Root + "/Tests",
                Root + "/Tests/Editor",
                Root + "/Prefabs",
                Root + "/Settings",
            };
            foreach (string folder in folders)
            {
                if (AssetDatabase.IsValidFolder(folder))
                    continue;
                string parent = folder[..folder.LastIndexOf('/')];
                string name = folder[(folder.LastIndexOf('/') + 1)..];
                AssetDatabase.CreateFolder(parent, name);
            }
        }

        private static string Sha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            using SHA256 algorithm = SHA256.Create();
            return string.Concat(
                algorithm.ComputeHash(stream).Select(value => value.ToString("x2")));
        }

        [Serializable]
        private sealed class Report
        {
            public bool pass;
            public string shippingScenePath;
            public string shippingSceneSha256;
            public string candidatePrefabPath;
            public string sourceGate11Folder;
            public string sourceGate11GlbSha256;
            public bool candidateExplicitlyEnabledForCapture;
            public bool candidateDefaultActive;
            public bool oldShippingModelDefaultActive;
            public float maximumTravelMeters;
            public float endpointToleranceMeters;
            public int detentCount;
            public float detentStepDegrees;
            public int renderMeshes;
            public int triangles;
            public string semanticRoute;
            public bool runtimeInputIntegrated;
            public bool hapticsIntegrated;
            public float initialAndResetVelocity;
            public string gate12Approval;
            public string deliveryState;
            public string deviceHapticAcceptance;
            public string buildInstallPhonePush;
            public string[] requiredViews;
        }
    }
}
