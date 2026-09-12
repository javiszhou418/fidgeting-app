using System;
using System.IO;
using System.Linq;
using FidgetingApp.EDC.Candidates.ModelHhax;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    /// <summary>
    /// Adds a fail-closed model-hhax candidate to the real MeshyEDC shipping
    /// scene. Every pre-existing root keeps its saved state and the new
    /// candidate remains inactive outside explicit evidence capture.
    /// </summary>
    public static class ModelHhaxGate12Builder
    {
        public const string ShippingScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        public const string SwitchName = "ModelHhax_Gate12R001_CandidateSwitch";
        public const string CandidateName = "ModelHhax_Gate12R001_Candidate";
        public const string PresentationName = "ModelHhax_Gate12R001_Presentation";
        public const string EvidenceRelative =
            "ArtSource/ModelPipeline/model-hhax/evidence/12-shipping/rev-001";
        public const string RuntimeEvidenceRelative =
            "ArtSource/ModelPipeline/model-hhax/evidence/12-shipping/rev-002/runtime-frames";
        private const string PendingRuntimeCaptureKey =
            "Fidgeting.ModelHhax.Gate12.PendingRuntimeCapture";

        [MenuItem("Fidgeting/Model Pipeline/model-hhax/Gate 12 Build")]
        public static void BuildGate12()
        {
            if (AssetDatabase.LoadAssetAtPath<GameObject>(ModelHhaxGate11Builder.PrefabPath) == null)
                throw new InvalidDataException("Approved Gate 11 candidate prefab is missing.");
            if (ModelHhaxGate11Builder.Sha256(AssetAbsolute(ModelHhaxGate11Builder.ModelPath))
                != ModelHhaxGate11Builder.ApprovedFbxSha256)
                throw new InvalidDataException("Gate 11 candidate no longer matches the approved Gate 10 FBX.");
            string gate11Report = ProjectPath(ModelHhaxGate11Builder.EvidenceRelative
                + "/unity-parity-report.json");
            if (!File.Exists(gate11Report)
                || !File.ReadAllText(gate11Report).Contains("\"status\": \"pass\"", StringComparison.Ordinal))
                throw new InvalidDataException("A passing Gate 11 parity report is required.");
            Directory.CreateDirectory(EvidenceRoot);
            Directory.CreateDirectory(ProjectPath(RuntimeEvidenceRelative));
            string sceneHashBefore = ModelHhaxGate11Builder.Sha256(AssetAbsolute(ShippingScenePath));

            Scene scene = EditorSceneManager.OpenScene(ShippingScenePath, OpenSceneMode.Single);
            GameObject prior = scene.GetRootGameObjects().FirstOrDefault(item => item.name == SwitchName);
            GameObject[] existingRoots = scene.GetRootGameObjects()
                .Where(item => item.name != SwitchName).ToArray();
            bool[] existingRootStates = existingRoots.Select(item => item.activeSelf).ToArray();
            string existingRootStateBefore = RootStateSignature(existingRoots, existingRootStates);
            if (prior != null) UnityEngine.Object.DestroyImmediate(prior);
            if (existingRoots.Length == 0)
                throw new InvalidDataException("MeshyEDC shipping scene has no existing roots to preserve.");
            GameObject[] environmentRoots = existingRoots.Where(item => item.name == "Studio").ToArray();
            if (environmentRoots.Length != 1)
                throw new InvalidDataException("Expected the real shipping Studio root exactly once.");
            GameObject[] existingProductRoots = existingRoots
                .Where(item => !environmentRoots.Contains(item)).ToArray();
            bool[] existingProductRootStates = existingProductRoots
                .Select(item => item.activeSelf).ToArray();

            GameObject switchRoot = new GameObject(SwitchName);
            SceneManager.MoveGameObjectToScene(switchRoot, scene);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(ModelHhaxGate11Builder.PrefabPath)
                ?? throw new InvalidDataException("Approved Gate 11 candidate prefab is missing.");
            GameObject candidate = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
            candidate.name = CandidateName;
            candidate.transform.SetParent(switchRoot.transform, false);
            candidate.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
            candidate.transform.localScale = Vector3.one;

            GameObject presentation = new GameObject(PresentationName);
            presentation.transform.SetParent(switchRoot.transform, false);
            Light[] lights = environmentRoots
                .SelectMany(item => item.GetComponentsInChildren<Light>(true)).ToArray();
            if (lights.Length == 0)
                throw new InvalidDataException("Real shipping Studio has no lights.");
            Camera camera = CreateCamera(presentation.transform);

            ModelHhaxDirectPoseController controller = candidate.GetComponent<ModelHhaxDirectPoseController>()
                ?? throw new InvalidDataException("Gate 11 direct-pose controller is missing.");

            CaptureStaticEvidence(existingProductRoots, existingProductRootStates, candidate,
                presentation, controller, camera, lights);

            controller.ResetPose();
            RestoreRootStates(existingRoots, existingRootStates);
            switchRoot.SetActive(true);
            candidate.SetActive(false);
            presentation.SetActive(false);
            EditorSceneManager.SaveScene(scene, ShippingScenePath, false);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            string sceneHashAfter = ModelHhaxGate11Builder.Sha256(AssetAbsolute(ShippingScenePath));
            string existingRootStateAfter = RootStateSignature(existingRoots,
                existingRoots.Select(item => item.activeSelf).ToArray());
            WriteReports(sceneHashBefore, sceneHashAfter, existingRootStateBefore,
                existingRootStateAfter, existingRoots, candidate, presentation);
            Debug.Log("model-hhax Gate 12 real shipping-scene candidate and views complete; fallback remains default.");
        }

        [MenuItem("Fidgeting/Model Pipeline/model-hhax/Gate 12 Build And Run PlayMode Capture")]
        public static void BuildAndRunGate12()
        {
            SessionState.SetBool(PendingRuntimeCaptureKey, true);
            BuildGate12();
            QueuePendingRuntimeCapture();
        }

        [InitializeOnLoadMethod]
        private static void ResumePendingRuntimeCaptureAfterReload()
        {
            if (SessionState.GetBool(PendingRuntimeCaptureKey, false))
                QueuePendingRuntimeCapture();
        }

        private static void QueuePendingRuntimeCapture()
        {
            EditorApplication.delayCall -= TryStartPendingRuntimeCapture;
            EditorApplication.delayCall += TryStartPendingRuntimeCapture;
        }

        private static void TryStartPendingRuntimeCapture()
        {
            if (!SessionState.GetBool(PendingRuntimeCaptureKey, false)) return;
            if (EditorApplication.isCompiling || EditorApplication.isUpdating)
            {
                QueuePendingRuntimeCapture();
                return;
            }

            Scene scene = EditorSceneManager.OpenScene(ShippingScenePath, OpenSceneMode.Single);
            GameObject switchRoot = scene.GetRootGameObjects().FirstOrDefault(item => item.name == SwitchName)
                ?? throw new InvalidDataException("model-hhax Gate 12 switch is missing.");
            GameObject candidate = switchRoot.transform.Find(CandidateName)?.gameObject
                ?? throw new InvalidDataException("model-hhax Gate 12 candidate is missing.");
            GameObject presentation = switchRoot.transform.Find(PresentationName)?.gameObject
                ?? throw new InvalidDataException("model-hhax Gate 12 presentation is missing.");
            ModelHhaxDirectPoseController controller = candidate.GetComponent<ModelHhaxDirectPoseController>()
                ?? throw new InvalidDataException("model-hhax direct-pose controller is missing.");
            Camera camera = presentation.GetComponentInChildren<Camera>(true)
                ?? throw new InvalidDataException("model-hhax review camera is missing.");
            GameObject[] environmentRoots = scene.GetRootGameObjects()
                .Where(item => item.name == "Studio").ToArray();
            GameObject[] existingProductRoots = scene.GetRootGameObjects()
                .Where(item => item != switchRoot && !environmentRoots.Contains(item)).ToArray();
            bool[] existingProductRootStates = existingProductRoots
                .Select(item => item.activeSelf).ToArray();
            Light[] lights = environmentRoots
                .SelectMany(item => item.GetComponentsInChildren<Light>(true)).ToArray();
            ModelHhaxShippingRuntimeEvidenceCapture capture =
                switchRoot.AddComponent<ModelHhaxShippingRuntimeEvidenceCapture>();
            if (capture == null)
            {
                SessionState.SetBool(PendingRuntimeCaptureKey, false);
                throw new InvalidOperationException(
                    "Gate 12 runtime evidence component could not be attached.");
            }
            capture.Configure(existingProductRoots, existingProductRootStates, candidate,
                presentation, controller, camera, lights, null, ProjectPath(RuntimeEvidenceRelative));
            SessionState.SetBool(PendingRuntimeCaptureKey, false);
            // Evidence harness and absolute output path remain unsaved/editor-only.
            EditorApplication.delayCall += () => EditorApplication.isPlaying = true;
        }

        public static string ProjectRoot => Directory.GetParent(Application.dataPath)!.FullName;
        public static string EvidenceRoot => ProjectPath(EvidenceRelative);

        private static string ProjectPath(string relative) =>
            Path.GetFullPath(Path.Combine(ProjectRoot, relative));

        private static string AssetAbsolute(string assetPath) =>
            Path.GetFullPath(Path.Combine(ProjectRoot, assetPath));

        private static void CaptureStaticEvidence(
            GameObject[] existingProductRoots,
            bool[] existingProductRootStates,
            GameObject candidate,
            GameObject presentation,
            ModelHhaxDirectPoseController controller,
            Camera camera,
            Light[] lights)
        {
            bool[] lightStates = lights.Select(item => item.enabled).ToArray();
            Color ambientBefore = RenderSettings.ambientLight;
            SetRootStates(existingProductRoots, false);
            try
            {
                candidate.SetActive(true);
                presentation.SetActive(true);
                controller.ResetPose();

                CaptureView(camera, "shipping-library.png", new Vector3(0.000f, 0.075f, -0.180f),
                    new Vector3(0f, 0.006f, 0f), 34f, 1600, 1000);
                CaptureView(camera, "shipping-hero.png", new Vector3(0.092f, 0.094f, -0.119f),
                    new Vector3(0f, 0.006f, 0f), 32.378413f, 1600, 1000);
                CaptureView(camera, "shipping-top.png", new Vector3(0.001f, 0.190f, -0.010f),
                    new Vector3(0f, 0.006f, 0f), 25f, 1600, 1000);
                CaptureView(camera, "shipping-left-oblique.png", new Vector3(-0.105f, 0.080f, -0.105f),
                    new Vector3(0f, 0.006f, 0f), 34f, 1600, 1000);
                CaptureView(camera, "shipping-right-oblique.png", new Vector3(0.105f, 0.080f, -0.105f),
                    new Vector3(0f, 0.006f, 0f), 34f, 1600, 1000);
                CaptureView(camera, "shipping-low.png", new Vector3(0.090f, 0.033f, -0.125f),
                    new Vector3(0f, 0.006f, 0f), 34f, 1600, 1000);
                CaptureView(camera, "shipping-phone.png", new Vector3(0.070f, 0.090f, -0.150f),
                    new Vector3(0f, 0.006f, 0f), 30f, 1290, 2796);

                controller.SetTravelMm(ModelHhaxDirectPoseController.MaximumTravelMm);
                CaptureView(camera, "shipping-open.png", new Vector3(0.095f, 0.100f, -0.145f),
                    new Vector3(0f, 0.006f, 0.008f), 34f, 1600, 1000);
                CaptureView(camera, "shipping-track-closeup.png", new Vector3(0.055f, 0.065f, -0.080f),
                    new Vector3(0f, 0.006f, 0.010f), 31f, 1600, 1000);

                controller.ResetPose();
                CaptureView(camera, "shipping-back.png", new Vector3(0.070f, -0.060f, 0.105f),
                    new Vector3(0f, 0.006f, 0f), 34f, 1600, 1000);

                foreach (Light light in lights) light.enabled = false;
                RenderSettings.ambientLight = Color.black;
                ModelHhaxArtworkEmission.Set(candidate, 3.6f);
                CaptureView(camera, "shipping-dark.png", new Vector3(0.092f, 0.094f, -0.119f),
                    new Vector3(0f, 0.006f, 0f), 32.378413f, 1600, 1000);
                ModelHhaxArtworkEmission.Clear(candidate);
            }
            finally
            {
                for (int index = 0; index < lights.Length; index++)
                    lights[index].enabled = lightStates[index];
                RenderSettings.ambientLight = ambientBefore;
                controller.ResetPose();
                candidate.SetActive(false);
                presentation.SetActive(false);
                RestoreRootStates(existingProductRoots, existingProductRootStates);
            }
        }

        private static void CaptureView(
            Camera camera, string file, Vector3 position, Vector3 target,
            float fov, int width, int height)
        {
            camera.transform.position = position;
            camera.transform.rotation = Quaternion.LookRotation(target - position, Vector3.up);
            camera.fieldOfView = fov;
            ModelHhaxGate11Builder.Capture(camera, Path.Combine(EvidenceRoot, file), width, height);
        }

        private static Camera CreateCamera(Transform parent)
        {
            GameObject item = new GameObject("CAM_HHAX_Gate12_ShippingReview");
            item.transform.SetParent(parent, false);
            Camera camera = item.AddComponent<Camera>();
            camera.enabled = false;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Hex("171326");
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 10f;
            camera.allowHDR = true;
            camera.allowMSAA = true;
            return camera;
        }

        private static Color Hex(string value)
        {
            if (!ColorUtility.TryParseHtmlString("#" + value, out Color color))
                throw new InvalidDataException("Bad colour: " + value);
            return color;
        }

        private static void WriteReports(
            string sceneHashBefore,
            string sceneHashAfter,
            string existingRootStateBefore,
            string existingRootStateAfter,
            GameObject[] existingRoots,
            GameObject candidate,
            GameObject presentation)
        {
            bool rootStatesUnchanged = existingRootStateBefore == existingRootStateAfter;
            bool pass = rootStatesUnchanged && !candidate.activeSelf && !presentation.activeSelf
                && candidate.GetComponent<ModelHhaxDirectPoseController>() != null
                && candidate.transform.root.GetComponent<ModelHhaxShippingRuntimeEvidenceCapture>() == null;
            string activeRoots = string.Join(", ", existingRoots
                .Where(item => item.activeSelf).Select(item => item.name));
            string report = "{\n"
                + "  \"schemaVersion\": 1,\n"
                + "  \"modelId\": \"model-hhax\",\n"
                + "  \"engine\": \"Unity 6000.5.6f1 / URP\",\n"
                + $"  \"status\": \"{(pass ? "pass" : "fail")}\",\n"
                + $"  \"shippingScenePath\": \"{ShippingScenePath}\",\n"
                + $"  \"shippingSceneSha256Before\": \"{sceneHashBefore}\",\n"
                + $"  \"shippingSceneSha256After\": \"{sceneHashAfter}\",\n"
                + $"  \"existingRootStatesUnchanged\": {rootStatesUnchanged.ToString().ToLowerInvariant()},\n"
                + $"  \"existingActiveRoots\": \"{JsonEscape(activeRoots)}\",\n"
                + $"  \"candidateDefaultActive\": {candidate.activeSelf.ToString().ToLowerInvariant()},\n"
                + $"  \"presentationDefaultActive\": {presentation.activeSelf.ToString().ToLowerInvariant()},\n"
                + "  \"serializedEvidenceHarness\": false,\n"
                + "  \"shippingEnvironment\": \"existing Studio root and its saved lighting\",\n"
                + "  \"shippingSceneMutation\": \"added or replaced only the model-hhax fail-closed switch; preserved every pre-existing root and active state\",\n"
                + "  \"requiredViews\": [\"shipping-library.png\", \"shipping-hero.png\", \"shipping-top.png\", \"shipping-left-oblique.png\", \"shipping-right-oblique.png\", \"shipping-low.png\", \"shipping-phone.png\"],\n"
                + "  \"supplementalViews\": [\"shipping-dark.png\", \"shipping-back.png\", \"shipping-open.png\", \"shipping-track-closeup.png\"],\n"
                + "  \"materialPolicy\": \"7 model-specific HHAX bindings + bevel-polished + groove-dark; three MOP texture sets remain model-local\",\n"
                + "  \"motionPolicy\": \"explicit direct pose only; no Update loop, auto motion, easing, inertia, detent, haptic, timing or coupling\",\n"
                + "  \"deviceBoundary\": \"no build, archive, install, launch or phone push\",\n"
                + "  \"physicalOrManufacturingClaim\": false\n"
                + "}\n";
            File.WriteAllText(Path.Combine(EvidenceRoot, "shipping-report.json"), report);
            string snapshot = "{\n"
                + "  \"schemaVersion\": 1,\n"
                + "  \"sourceGate11Prefab\": \"ModelHhaxGate11R001.prefab\",\n"
                + "  \"shippingEnvironment\": \"existing MeshyEDC Studio root\",\n"
                + "  \"expectedClosedBoundsMm\": [30.9, 50.5, 13.6],\n"
                + "  \"slideTravelMm\": [0, 18.7],\n"
                + "  \"automaticMotion\": false,\n"
                + "  \"existingRootStatesPreserved\": true,\n"
                + "  \"savedCandidateDefaultActive\": false,\n"
                + "  \"phoneBuildInstallPush\": \"not-authorized\"\n"
                + "}\n";
            File.WriteAllText(Path.Combine(EvidenceRoot, "shipping-parameters.json"), snapshot);
            if (!pass)
                throw new InvalidOperationException("model-hhax shipping scene did not save fail-closed defaults.");
        }

        private static void SetRootStates(GameObject[] roots, bool active)
        {
            foreach (GameObject root in roots)
                if (root != null) root.SetActive(active);
        }

        private static void RestoreRootStates(GameObject[] roots, bool[] states)
        {
            if (roots.Length != states.Length)
                throw new ArgumentException("Shipping root/state arrays must have the same length.");
            for (int index = 0; index < roots.Length; index++)
                if (roots[index] != null) roots[index].SetActive(states[index]);
        }

        private static string RootStateSignature(GameObject[] roots, bool[] states)
        {
            if (roots.Length != states.Length)
                throw new ArgumentException("Shipping root/state arrays must have the same length.");
            return string.Join("\n", roots.Select((root, index) =>
                (root == null ? "<missing>" : root.name) + "|" + states[index]));
        }

        private static string JsonEscape(string value) => value
            .Replace("\\", "\\\\", StringComparison.Ordinal)
            .Replace("\"", "\\\"", StringComparison.Ordinal)
            .Replace("\r", "\\r", StringComparison.Ordinal)
            .Replace("\n", "\\n", StringComparison.Ordinal);
    }
}
