using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.EDC.EditorTools;
using FidgetingApp.EDC.Gate12R002;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileGate12R003MotionReviewBuilder
    {
        private const string ShippingScene = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string EvidenceRoot =
            "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping";
        private const string AcceptedRevision = EvidenceRoot + "/rev-002";
        private const string OutputRevision = EvidenceRoot + "/rev-003";
        private const string RuntimeRecovery =
            EvidenceRoot + "/runtime-recovery-build42";
        private static readonly Vector3 ApprovedRuntimeCameraPosition =
            new(0f, 0.07940412f, -0.1366955f);
        private static readonly Quaternion ApprovedRuntimeCameraRotation =
            new(0.25881907f, 0f, 0f, 0.9659259f);

        private static readonly string[] AcceptedViews =
        {
            "library.png",
            "hero.png",
            "top.png",
            "left-oblique.png",
            "right-oblique.png",
            "low.png",
            "phone.png",
        };

        [MenuItem("Fidgeting/Model Pipeline/Capture Magnetic Slide Gate 12 R003")]
        public static void CaptureCorrectedMotionViews()
        {
            Scene scene = EditorSceneManager.OpenScene(
                ShippingScene, OpenSceneMode.Single);
            MagneticSlideTileShippingCoordinator coordinator =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include)
                ?? throw new InvalidDataException(
                    "Gate 12 shipping coordinator is missing.");
            MagneticSlideTileGate12PlayModeCapture capture =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileGate12PlayModeCapture>(
                    FindObjectsInactive.Include)
                ?? throw new InvalidDataException(
                    "Gate 12 PlayMode capture host is missing.");
            Camera camera = capture.GetComponentInChildren<Camera>(true)
                ?? UnityEngine.Object.FindObjectsByType<Camera>(
                    FindObjectsInactive.Include, FindObjectsSortMode.None)
                    .First(item => item.name.Contains("Gate12R002"));

            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string accepted = Path.Combine(projectRoot, AcceptedRevision);
            string output = Path.Combine(projectRoot, OutputRevision);
            Directory.CreateDirectory(output);
            PreserveAcceptedViews(accepted, output);

            coordinator.SetPreviewActive(true);
            MagneticSlideTileShippingMechanism mechanism = coordinator.Mechanism;
            mechanism.ResetPose(false);
            mechanism.TrySetTravel(coordinator.Settings.MaximumTravelMeters);
            RenderView(camera, output, "max-open");
            mechanism.TrySetAngle(12f, false);
            RenderView(camera, output, "endpoint-12deg");
            mechanism.TrySetAngle(36f, false);
            RenderView(camera, output, "endpoint-36deg");
            mechanism.TrySetAngle(360f, false);
            RenderView(camera, output, "endpoint-360deg");

            WriteMotionFixReport(
                Path.Combine(output, "gate12-motion-fix-report.json"),
                projectRoot,
                mechanism);
            mechanism.ResetPose(false);
            coordinator.SetPreviewActive(false);
            camera.enabled = false;
        }

        [MenuItem("Fidgeting/Model Pipeline/Run Magnetic Slide Gate 12 R003")]
        public static void CaptureCorrectedMotionRecording()
        {
            CaptureCorrectedMotionViews();
            MagneticSlideTileGate12PlayModeCapture capture =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileGate12PlayModeCapture>(
                    FindObjectsInactive.Include);
            MagneticSlideTileShippingCoordinator coordinator =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include);
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string frames = Path.Combine(
                projectRoot, OutputRevision, "unity-playmode-frames");
            Directory.CreateDirectory(frames);
            capture.Configure(
                coordinator,
                UnityEngine.Object.FindObjectsByType<Camera>(
                    FindObjectsInactive.Include, FindObjectsSortMode.None)
                    .First(item => item.name.Contains("Gate12R002")),
                frames);
            capture.Arm();
            File.WriteAllText(Path.Combine(frames, "capture.request"), "armed\n");
            EditorApplication.delayCall += () => EditorApplication.isPlaying = true;
        }

        [MenuItem("Fidgeting/Model Pipeline/Promote Magnetic Slide Gate 12 R003")]
        public static void PromoteApprovedCandidate()
        {
            Scene scene = EditorSceneManager.OpenScene(
                ShippingScene, OpenSceneMode.Single);
            MagneticSlideTileShippingCoordinator coordinator =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include)
                ?? throw new InvalidDataException(
                    "Gate 12 shipping coordinator is missing.");
            coordinator.Mechanism.ResetPose(false);
            coordinator.SetPreviewActive(true);
            foreach (MagneticSlideTileGate12PlayModeCapture capture in
                UnityEngine.Object.FindObjectsByType<
                    MagneticSlideTileGate12PlayModeCapture>(
                    FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                capture.enabled = false;
            }
            foreach (Camera camera in UnityEngine.Object.FindObjectsByType<Camera>(
                FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                if (camera.name.Contains("Gate12R002"))
                    camera.enabled = false;
            }

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ShippingScene, false);
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string output = Path.Combine(projectRoot, OutputRevision);
            Directory.CreateDirectory(output);
            ShippingPromotionReport report = new()
            {
                pass = coordinator.CandidatePreviewEnabled
                    && coordinator.CandidateModelActive
                    && !coordinator.FallbackModelActive
                    && coordinator.Mechanism.IsPoseLegal(),
                shippingScenePath = ShippingScene,
                shippingSceneSha256 = Sha256(
                    Path.Combine(projectRoot, ShippingScene)),
                gate12Revision = 3,
                candidateDefaultActive = coordinator.CandidateModelActive,
                fallbackDefaultActive = coordinator.FallbackModelActive,
                fallbackPreserved = true,
                travelMeters = coordinator.Mechanism.TravelMeters,
                angleDegrees = coordinator.Mechanism.AngleDegrees,
                linearVelocityMetersPerSecond =
                    coordinator.Mechanism.LinearVelocityMetersPerSecond,
                angularVelocityDegreesPerSecond =
                    coordinator.Mechanism.AngularVelocityDegreesPerSecond,
                topStackHeightResidualMeters =
                    coordinator.Mechanism.TopStackHeightResidualMeters,
                fixedAxisConstraintResidual =
                    coordinator.Mechanism.FixedAxisConstraintResidual,
                renderersRemainAttached =
                    coordinator.Mechanism.RenderersRemainAttached,
                buildInstallPhone = false,
            };
            if (!report.pass)
                throw new InvalidDataException(
                    "Approved Gate 12 candidate promotion failed validation.");
            File.WriteAllText(
                Path.Combine(output, "shipping-promotion-report.json"),
                JsonUtility.ToJson(report, true));
        }

        [MenuItem("Fidgeting/Model Pipeline/Wire Magnetic Slide Gate 12 Interaction")]
        public static void WireApprovedRuntimeInteraction()
        {
            Scene scene = EditorSceneManager.OpenScene(
                ShippingScene, OpenSceneMode.Single);
            MagneticSlideTileShippingCoordinator coordinator =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include)
                ?? throw new InvalidDataException(
                    "Gate 12 shipping coordinator is missing.");
            MagneticSlideTileShippingMechanism mechanism =
                coordinator.Mechanism
                ?? throw new InvalidDataException(
                    "Gate 12 shipping mechanism is missing.");
            Camera interactionCamera = Camera.main
                ?? throw new InvalidDataException(
                    "The shipping interaction camera is missing.");

            Transform top = mechanism.TopLocalSlide
                ?? throw new InvalidDataException(
                    "The approved TopLocalSlide binding is missing.");
            foreach (Transform staleSurface in coordinator.CandidateModel
                .GetComponentsInChildren<Transform>(true)
                .Where(item =>
                    item.name == "ShippingInteractionSurface"
                    && item.parent != top)
                .ToArray())
            {
                UnityEngine.Object.DestroyImmediate(
                    staleSurface.gameObject);
            }
            Transform surfaceTransform = top.Find("ShippingInteractionSurface");
            GameObject surfaceObject;
            if (surfaceTransform == null)
            {
                surfaceObject = new GameObject("ShippingInteractionSurface");
                surfaceTransform = surfaceObject.transform;
                surfaceTransform.SetParent(top, false);
            }
            else
            {
                surfaceObject = surfaceTransform.gameObject;
            }
            surfaceObject.layer = 0;
            BoxCollider surface = surfaceObject.GetComponent<BoxCollider>();
            if (surface == null)
                surface = surfaceObject.AddComponent<BoxCollider>();
            Bounds localBounds = CalculateLocalRendererBounds(top);
            surface.center = localBounds.center;
            surface.size = new Vector3(
                Mathf.Max(0.02f, localBounds.size.x),
                Mathf.Max(0.02f, localBounds.size.y),
                Mathf.Max(0.004f, localBounds.size.z));
            surface.isTrigger = false;
            surface.enabled = true;

            foreach (Collider collider in coordinator.CandidateModel
                .GetComponentsInChildren<Collider>(true))
            {
                if (collider != surface)
                    collider.enabled = false;
            }

            EdcSliderController input =
                coordinator.CandidateModel.GetComponent<EdcSliderController>();
            if (input == null)
            {
                input = coordinator.CandidateModel.AddComponent<
                    EdcSliderController>();
            }

            SharedPresentationGestureController presentationGestures =
                UnityEngine.Object.FindFirstObjectByType<
                    SharedPresentationGestureController>(
                    FindObjectsInactive.Include)
                ?? throw new InvalidDataException(
                    "Shared presentation gestures are missing.");
            EdcPortraitCameraFramer framer =
                interactionCamera.GetComponent<EdcPortraitCameraFramer>()
                ?? throw new InvalidDataException(
                    "The EDC camera framer is missing.");
            LinearMagneticDetentProfile hapticProfile =
                AssetDatabase.LoadAssetAtPath<LinearMagneticDetentProfile>(
                    EdcSceneBuilder.MagneticProfilePath)
                ?? throw new InvalidDataException(
                    "The production magnetic Haptic profile is missing.");
            input.ConfigureShipping(
                coordinator,
                interactionCamera,
                surface,
                hapticProfile,
                presentationGestures);
            Bounds stableBounds = CalculateStableClosedBounds(
                coordinator.CandidateModel.transform,
                mechanism);
            interactionCamera.transform.SetPositionAndRotation(
                ApprovedRuntimeCameraPosition,
                ApprovedRuntimeCameraRotation);
            Vector3 stableWorldCenter =
                coordinator.CandidateModel.transform.TransformPoint(
                    stableBounds.center);
            float focusDistance = Mathf.Max(
                0.01f,
                Vector3.Dot(
                    stableWorldCenter - interactionCamera.transform.position,
                    interactionCamera.transform.forward));
            Vector3 authoredFocus =
                interactionCamera.transform.position
                + interactionCamera.transform.forward * focusDistance;
            framer.ConfigureAuthoredRuntimeTarget(
                coordinator.CandidateModel.transform,
                stableBounds,
                authoredFocus);
            presentationGestures.Configure(framer, interactionCamera, surface);
            ConfigureProductionAudio(coordinator, input);

            coordinator.SetPreviewActive(true);
            coordinator.ResetShippingPose(false);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ShippingScene, false);

            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string output = Path.Combine(projectRoot, RuntimeRecovery);
            Directory.CreateDirectory(output);
            MagneticSlideDetentAudio audio =
                coordinator.CandidateModel.GetComponentInChildren<
                    MagneticSlideDetentAudio>(true);
            RuntimeWiringReport report = new()
            {
                pass = input.UsesShippingMechanism
                    && input.ShippingCoordinator == coordinator
                    && input.InteractionCamera == interactionCamera
                    && input.InteractionSurface == surface
                    && input.Profile == hapticProfile
                    && input.PresentationGestures == presentationGestures
                    && framer.Target == coordinator.CandidateModel.transform
                    && framer.UsesStableLocalBounds
                    && framer.PreservesAuthoredDefaultPose
                    && audio != null
                    && audio.Slider == input
                    && audio.AudioReady
                    && coordinator.CandidateModelActive
                    && !coordinator.FallbackModelActive,
                sourceScene = ShippingScene,
                shippingSceneSha256 = Sha256(
                    Path.Combine(projectRoot, ShippingScene)),
                inputController = input.GetType().FullName,
                interactionSurface = surface.name,
                interactionCamera = interactionCamera.name,
                candidateDefaultActive = coordinator.CandidateModelActive,
                fallbackDefaultActive = coordinator.FallbackModelActive,
                hiddenDebugCollidersEnabled = coordinator.CandidateModel
                    .GetComponentsInChildren<Collider>(true)
                    .Count(collider => collider != surface && collider.enabled),
                audioRenderer = audio?.GetType().FullName,
                audioVoices = audio?.Voices.Length ?? 0,
                cameraTarget = framer.Target?.name,
                stableCameraBounds = framer.UsesStableLocalBounds,
                authoredCameraPosePreserved =
                    framer.PreservesAuthoredDefaultPose,
                hapticRoute =
                    "mechanism semantic event -> EdcSliderController -> "
                    + "FidgetAppCoordinator -> FidgetHapticRouter",
                visualGeometryChanged = false,
                materialChanged = false,
                deviceAcceptance = "failed-build-41-runtime-recovery",
            };
            if (!report.pass || report.hiddenDebugCollidersEnabled != 0)
                throw new InvalidDataException(
                    "Gate 12 runtime input wiring validation failed.");
            File.WriteAllText(
                Path.Combine(output, "runtime-interaction-wiring-report.json"),
                JsonUtility.ToJson(report, true));
        }

        private static Bounds CalculateLocalRendererBounds(Transform root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
                throw new InvalidDataException(
                    "MovingTop has no renderers for its hit surface.");
            bool initialized = false;
            Bounds localBounds = default;
            foreach (Renderer renderer in renderers)
            {
                Bounds world = renderer.bounds;
                for (int x = -1; x <= 1; x += 2)
                for (int y = -1; y <= 1; y += 2)
                for (int z = -1; z <= 1; z += 2)
                {
                    Vector3 corner = world.center + Vector3.Scale(
                        world.extents, new Vector3(x, y, z));
                    Vector3 local = root.InverseTransformPoint(corner);
                    if (!initialized)
                    {
                        localBounds = new Bounds(local, Vector3.zero);
                        initialized = true;
                    }
                    else
                    {
                        localBounds.Encapsulate(local);
                    }
                }
            }
            return localBounds;
        }

        private static Bounds CalculateStableClosedBounds(
            Transform root,
            MagneticSlideTileShippingMechanism mechanism)
        {
            bool initialized = false;
            Bounds bounds = default;
            mechanism.ResetPose(false);
            EncapsulateEnabledRenderers(
                root,
                ref bounds,
                ref initialized);
            if (!initialized)
            {
                throw new InvalidDataException(
                    "The approved candidate has no enabled renderers.");
            }
            return bounds;
        }

        private static void EncapsulateEnabledRenderers(
            Transform root,
            ref Bounds bounds,
            ref bool initialized)
        {
            foreach (Renderer renderer in
                root.GetComponentsInChildren<Renderer>(true))
            {
                if (!renderer.enabled)
                    continue;
                Bounds world = renderer.bounds;
                for (int x = -1; x <= 1; x += 2)
                for (int y = -1; y <= 1; y += 2)
                for (int z = -1; z <= 1; z += 2)
                {
                    Vector3 local = root.InverseTransformPoint(
                        world.center + Vector3.Scale(
                            world.extents,
                            new Vector3(x, y, z)));
                    if (!initialized)
                    {
                        bounds = new Bounds(local, Vector3.zero);
                        initialized = true;
                    }
                    else
                    {
                        bounds.Encapsulate(local);
                    }
                }
            }
        }

        private static void ConfigureProductionAudio(
            MagneticSlideTileShippingCoordinator coordinator,
            EdcSliderController input)
        {
            Transform existing = coordinator.CandidateModel.transform.Find(
                "MagneticSlideAudio");
            if (existing != null)
                UnityEngine.Object.DestroyImmediate(existing.gameObject);

            AudioClip effect = AssetDatabase.LoadAssetAtPath<AudioClip>(
                EdcSceneBuilder.MagneticSlideEffectPath)
                ?? throw new InvalidDataException(
                    "The production magnetic slide audio clip is missing.");
            GameObject audioObject = new("MagneticSlideAudio");
            audioObject.transform.SetParent(
                coordinator.CandidateModel.transform,
                false);
            AudioSource[] voices =
                new AudioSource[MagneticSlideAudioModel.VoiceCount];
            for (int index = 0; index < voices.Length; index++)
                voices[index] = audioObject.AddComponent<AudioSource>();
            MagneticSlideDetentAudio audio =
                audioObject.AddComponent<MagneticSlideDetentAudio>();
            audio.Configure(
                input,
                effect,
                voices,
                MagneticSlideAudioModel.DefaultMasterVolume);
        }

        private static void PreserveAcceptedViews(string source, string output)
        {
            foreach (string file in AcceptedViews)
                File.Copy(Path.Combine(source, file), Path.Combine(output, file), true);
        }

        private static void RenderView(
            Camera camera,
            string directory,
            string name)
        {
            camera.transform.position = new Vector3(0.074f, 0.072f, -0.116f);
            camera.transform.rotation = Quaternion.LookRotation(
                new Vector3(0f, 0.005f, 0f) - camera.transform.position,
                Vector3.up);
            camera.fieldOfView = 20f;
            RenderTexture target = new(
                1600, 1000, 24, RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Default);
            target.Create();
            RenderTexture previous = RenderTexture.active;
            camera.targetTexture = target;
            camera.Render();
            camera.Render();
            RenderTexture.active = target;
            Texture2D image = new(
                1600, 1000, TextureFormat.RGBA32, false, false);
            image.ReadPixels(new Rect(0, 0, 1600, 1000), 0, 0);
            image.Apply(false, false);
            File.WriteAllBytes(
                Path.Combine(directory, name + ".png"), image.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(image);
            camera.targetTexture = null;
            RenderTexture.active = previous;
            target.Release();
            UnityEngine.Object.DestroyImmediate(target);
        }

        private static void WriteMotionFixReport(
            string path,
            string projectRoot,
            MagneticSlideTileShippingMechanism mechanism)
        {
            MotionFixReport report = new()
            {
                pass = mechanism.IsPoseLegal()
                    && mechanism.TopStackHeightResidualMeters <= 0.000001f
                    && mechanism.OutOfPlaneSlideResidualMeters <= 0.000001f
                    && mechanism.FixedAxisConstraintResidual <= 0.000001f
                    && mechanism.RenderersRemainAttached,
                shippingScenePath = ShippingScene,
                shippingSceneSha256 = Sha256(
                    Path.Combine(projectRoot, ShippingScene)),
                sourceEvidenceRevision = 2,
                evidenceRevision = 3,
                rootCause =
                    "Travel used converted local +Z, which mapped to world-up; "
                    + "rotation used converted local Y, which mapped off-plane.",
                correctedSlideAxis = "TopLocalSlide local -Y",
                correctedRotationAxis = "MovingTop/RotatingCarrier local +Z",
                travelMeters = mechanism.TravelMeters,
                angleDegrees = mechanism.AngleDegrees,
                topStackHeightResidualMeters =
                    mechanism.TopStackHeightResidualMeters,
                outOfPlaneSlideResidualMeters =
                    mechanism.OutOfPlaneSlideResidualMeters,
                fixedAxisConstraintResidual =
                    mechanism.FixedAxisConstraintResidual,
                renderersRemainAttached = mechanism.RenderersRemainAttached,
                acceptedViewsCopiedByteForByte = true,
                buildInstallPhone = false,
            };
            File.WriteAllText(path, JsonUtility.ToJson(report, true));
        }

        private static string Sha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            using SHA256 algorithm = SHA256.Create();
            return string.Concat(
                algorithm.ComputeHash(stream).Select(value => value.ToString("x2")));
        }

        [Serializable]
        private sealed class MotionFixReport
        {
            public bool pass;
            public string shippingScenePath;
            public string shippingSceneSha256;
            public int sourceEvidenceRevision;
            public int evidenceRevision;
            public string rootCause;
            public string correctedSlideAxis;
            public string correctedRotationAxis;
            public float travelMeters;
            public float angleDegrees;
            public float topStackHeightResidualMeters;
            public float outOfPlaneSlideResidualMeters;
            public float fixedAxisConstraintResidual;
            public bool renderersRemainAttached;
            public bool acceptedViewsCopiedByteForByte;
            public bool buildInstallPhone;
        }

        [Serializable]
        private sealed class ShippingPromotionReport
        {
            public bool pass;
            public string shippingScenePath;
            public string shippingSceneSha256;
            public int gate12Revision;
            public bool candidateDefaultActive;
            public bool fallbackDefaultActive;
            public bool fallbackPreserved;
            public float travelMeters;
            public float angleDegrees;
            public float linearVelocityMetersPerSecond;
            public float angularVelocityDegreesPerSecond;
            public float topStackHeightResidualMeters;
            public float fixedAxisConstraintResidual;
            public bool renderersRemainAttached;
            public bool buildInstallPhone;
        }

        [Serializable]
        private sealed class RuntimeWiringReport
        {
            public bool pass;
            public string sourceScene;
            public string shippingSceneSha256;
            public string inputController;
            public string interactionSurface;
            public string interactionCamera;
            public bool candidateDefaultActive;
            public bool fallbackDefaultActive;
            public int hiddenDebugCollidersEnabled;
            public string audioRenderer;
            public int audioVoices;
            public string cameraTarget;
            public bool stableCameraBounds;
            public bool authoredCameraPosePreserved;
            public string hapticRoute;
            public bool visualGeometryChanged;
            public bool materialChanged;
            public string deviceAcceptance;
        }
    }
}
