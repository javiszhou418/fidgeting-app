using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.EDC.Gate12R002;
using UnityEditor;
using UnityEditor.Rendering;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileGate11R012MaterialReviewBuilder
    {
        private const string ShippingScene = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R012";
        private const string Materials = Root + "/Materials";
        private const string ShaderName =
            "FidgetingApp/MagneticSlideTile/LayeredOpticsR012";
        private const string Source =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported";
        private const string OutputRelative =
            "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
            + "11-unity-parity/rev-012-layered-material";

        private static readonly string[] ProtectedSources =
        {
            "Assets/_EDC/Runtime/EdcSliderController.cs",
            "Assets/_EDC/Runtime/MagneticSlideDetentAudio.cs",
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/"
                + "MagneticSlideTileShippingCoordinator.cs",
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/"
                + "MagneticSlideTileShippingMechanism.cs",
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Settings/"
                + "MagneticSlideTileMechanismSettingsR002.asset",
            "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Prefabs/"
                + "MagneticSlideTileGate12R002Candidate.prefab",
            "Assets/Scripts/FidgetSpinner/IosHaptics.cs",
        };

        private static readonly ViewRecipe[] Views =
        {
            new("front", new Vector3(0f, 0.082f, -0.110f),
                new Vector3(0f, 0.004f, 0f), 30f, 1280, 960, Pose.Closed),
            new("hero", new Vector3(0.074f, 0.072f, -0.116f),
                new Vector3(0f, 0.005f, -0.002f), 17.945253f,
                1600, 1000, Pose.Closed),
            new("left-oblique", new Vector3(-0.055f, 0.040f, -0.055f),
                Vector3.zero, 36f, 1280, 960, Pose.Closed),
            new("right-oblique", new Vector3(0.055f, 0.040f, -0.055f),
                Vector3.zero, 36f, 1280, 960, Pose.Closed),
            new("grazing", new Vector3(0.066f, 0.012f, -0.060f),
                new Vector3(0f, 0.004f, 0f), 34f, 1280, 960, Pose.Closed),
            new("low", new Vector3(0.045f, 0.018f, -0.070f),
                new Vector3(0f, 0.002f, 0f), 36f, 1280, 960, Pose.Closed),
            new("phone", new Vector3(0.030f, 0.030f, -0.050f),
                Vector3.zero, 38f, 1290, 2796, Pose.Closed),
            new("max-open", new Vector3(0.074f, 0.072f, -0.116f),
                new Vector3(0f, 0.005f, 0.006f), 20f,
                1600, 1000, Pose.MaximumOpen),
        };

        [MenuItem("Fidgeting/Model Pipeline/Capture Magnetic Slide Layered Material R012")]
        public static void Capture()
        {
            Scene scene = EditorSceneManager.OpenScene(
                ShippingScene, OpenSceneMode.Single);
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string output = Path.Combine(projectRoot, OutputRelative);
            Directory.CreateDirectory(output);
            string flatDirectory = Path.Combine(output, "A-current-flat-unity");
            string layeredDirectory = Path.Combine(output, "B-layered-unity");
            string frameDirectory = Path.Combine(output, "reflection-motion-frames");
            Directory.CreateDirectory(flatDirectory);
            Directory.CreateDirectory(layeredDirectory);
            Directory.CreateDirectory(frameDirectory);

            Dictionary<string, string> protectedBefore =
                HashProtectedSources(projectRoot);
            string sceneBefore = Sha256(Path.Combine(projectRoot, ShippingScene));

            MagneticSlideTileShippingCoordinator coordinator =
                UnityEngine.Object.FindFirstObjectByType<
                    MagneticSlideTileShippingCoordinator>(
                    FindObjectsInactive.Include)
                ?? throw new InvalidDataException("Shipping coordinator missing.");
            Camera camera = Camera.main
                ?? throw new InvalidDataException("Shipping camera missing.");
            MagneticSlideShippingLightingController lighting =
                camera.GetComponent<MagneticSlideShippingLightingController>()
                ?? throw new InvalidDataException("Approved lighting controller missing.");
            lighting.ApplyVariant(MagneticSlideLightingVariant.BalancedBrighter);
            coordinator.SetPreviewActive(true);
            coordinator.ResetShippingPose(false);

            MeshRenderer[] renderers = coordinator.CandidateModel
                .GetComponentsInChildren<MeshRenderer>(true)
                .Where(renderer => renderer.enabled)
                .ToArray();
            AssignFlatTopMaterials(renderers);
            Dictionary<MeshRenderer, Material[]> originalMaterials =
                renderers.ToDictionary(
                    renderer => renderer,
                    renderer => renderer.sharedMaterials.ToArray());
            Bounds beforeBounds = CalculateBounds(renderers);
            string[] beforeMeshIds = renderers
                .Select(renderer => MeshIdentity(
                    renderer.GetComponent<MeshFilter>().sharedMesh))
                .ToArray();

            CameraState cameraState = new(camera);
            foreach (ViewRecipe view in Views)
            {
                ApplyPose(coordinator, view.Pose);
                Render(camera, flatDirectory, view);
            }

            Dictionary<string, Material> layered = CreateLayeredMaterials();
            AssignTopMaterials(renderers, layered);
            foreach (MeshRenderer renderer in renderers)
                PrefabUtility.RecordPrefabInstancePropertyModifications(renderer);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ShippingScene, false);

            foreach (ViewRecipe view in Views)
            {
                ApplyPose(coordinator, view.Pose);
                Render(camera, layeredDirectory, view);
            }
            CaptureReflectionMotion(camera, coordinator, frameDirectory);

            coordinator.ResetShippingPose(false);
            cameraState.Restore(camera);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ShippingScene, false);
            AssetDatabase.SaveAssets();

            Bounds afterBounds = CalculateBounds(renderers);
            string[] afterMeshIds = renderers
                .Select(renderer => MeshIdentity(
                    renderer.GetComponent<MeshFilter>().sharedMesh))
                .ToArray();
            Dictionary<string, string> protectedAfter =
                HashProtectedSources(projectRoot);
            bool protectedUnchanged = protectedBefore.All(
                pair => protectedAfter.TryGetValue(pair.Key, out string value)
                    && value == pair.Value);
            Shader shader = Shader.Find(ShaderName)
                ?? throw new InvalidDataException("Layered shader missing.");
            ShaderMessage[] shaderMessages = ShaderUtil.GetShaderMessages(shader);
            bool shaderErrors = shaderMessages.Any(
                message => message.severity == ShaderCompilerMessageSeverity.Error);

            MaterialReviewReport report = new()
            {
                schemaVersion = 1,
                gate = "11-unity-parity",
                evidenceRevision = 12,
                sourceScene = ShippingScene,
                sceneSha256Before = sceneBefore,
                sceneSha256After = Sha256(Path.Combine(projectRoot, ShippingScene)),
                userFeedback =
                    "red face flattened; material depth, color variation and "
                    + "distinct reflection characteristics are missing",
                rootCause =
                    "Gate 10/11 PortablePBRR011 uses one opaque BRDF with one "
                    + "base color, roughness, normal and weak clearcoat. "
                    + "Transmission was removed and all optical layers collapsed.",
                architecture =
                    "one-pass opaque URP layered optics; no shell, no transparent "
                    + "sorting, no bounds expansion",
                shaderName = ShaderName,
                shaderSupported = shader.isSupported,
                shaderTarget = "3.5",
                shaderErrorCount = shaderMessages.Count(
                    message => message.severity
                        == ShaderCompilerMessageSeverity.Error),
                shaderWarningCount = shaderMessages.Count(
                    message => message.severity
                        == ShaderCompilerMessageSeverity.Warning),
                srpBatcherLayout = "single UnityPerMaterial CBUFFER",
                topPasses = 1,
                addedRenderers = 0,
                addedDrawCalls = 0,
                textureSamplesPerTopPixel = 5,
                cubemapSamplesPerTopPixel = 4,
                estimatedMobileCost =
                    "two top submeshes, one pass, about 5 texture + 4 cubemap "
                    + "samples per covered pixel; no transparency overdraw",
                coatIor = 1.52f,
                coatRoughness = 0.035f,
                coatStrength = 0.78f,
                layerDepthUv = 0.0016f,
                micaScale = 28f,
                microflakeScale = 85f,
                microflakeStrength = 0.16f,
                iridescenceStrength = 0.12f,
                motifRoughness = 0.18f,
                motifMetallic = 0.24f,
                motifReliefUv = 0.0012f,
                emission = 0f,
                protectedRuntimeUnchanged = protectedUnchanged,
                geometryMeshInstancesUnchanged =
                    beforeMeshIds.SequenceEqual(afterMeshIds),
                boundsCenterDeltaMeters =
                    Vector3.Distance(beforeBounds.center, afterBounds.center),
                boundsSizeDeltaMeters =
                    Vector3.Distance(beforeBounds.size, afterBounds.size),
                rendererCountBefore = renderers.Length,
                rendererCountAfter = renderers.Length,
                materialSlotsBefore = originalMaterials.Values.Sum(items => items.Length),
                materialSlotsAfter = renderers.Sum(
                    renderer => renderer.sharedMaterials.Length),
                candidateActive = coordinator.CandidateModelActive,
                fallbackActive = coordinator.FallbackModelActive,
                mechanismPoseLegal = coordinator.Mechanism.IsPoseLegal(),
                build44Installed = false,
                deviceAcceptance = "failed-material-flatness",
                visualApproval = "pending",
                pass = shader.isSupported
                    && !shaderErrors
                    && protectedUnchanged
                    && beforeMeshIds.SequenceEqual(afterMeshIds)
                    && Vector3.Distance(beforeBounds.center, afterBounds.center) < 1e-7f
                    && Vector3.Distance(beforeBounds.size, afterBounds.size) < 1e-7f
                    && coordinator.CandidateModelActive
                    && !coordinator.FallbackModelActive
                    && coordinator.Mechanism.IsPoseLegal(),
            };
            File.WriteAllText(
                Path.Combine(output, "unity-layered-material-report.json"),
                JsonUtility.ToJson(report, true) + Environment.NewLine);
            if (!report.pass)
                throw new InvalidDataException("Layered material review failed.");
        }

        private static Dictionary<string, Material> CreateLayeredMaterials()
        {
            Directory.CreateDirectory(
                Path.Combine(Application.dataPath,
                    "_EDC/Candidates/MagneticSlideTileGate11R012/Materials"));
            Shader shader = Shader.Find(ShaderName)
                ?? throw new InvalidDataException("Layered optics shader missing.");
            Cubemap environment = AssetDatabase.LoadAssetAtPath<Cubemap>(
                Source + "/Environment/MagneticSlideTileGate11R011Environment.cubemap")
                ?? throw new InvalidDataException("Approved cubemap missing.");
            Texture2D perimeter = LoadTexture("top-perimeter-mask.png");
            return new Dictionary<string, Material>
            {
                ["upper"] = CreateTop(
                    shader, environment, perimeter,
                    "M_G11R012_UpperLayeredTop",
                    "upper-albedo.png", "upper-roughness.png",
                    "upper-transport-normal-r011.png",
                    "upper-artwork-mask.png"),
                ["lower"] = CreateTop(
                    shader, environment, perimeter,
                    "M_G11R012_LowerLayeredTop",
                    "lower-albedo.png", "lower-roughness.png",
                    "lower-transport-normal-r011.png",
                    "lower-artwork-mask.png"),
            };
        }

        private static Material CreateTop(
            Shader shader,
            Cubemap environment,
            Texture2D perimeter,
            string name,
            string baseName,
            string roughnessName,
            string normalName,
            string maskName)
        {
            string path = $"{Materials}/{name}.mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            else
            {
                material.shader = shader;
                material.name = name;
            }
            material.SetTexture("_BaseMap", LoadTexture(baseName));
            material.SetTexture("_RoughnessMap", LoadTexture(roughnessName));
            material.SetTexture("_NormalMap", LoadTexture(normalName));
            material.SetTexture("_MotifMask", LoadTexture(maskName));
            material.SetTexture("_PerimeterMask", perimeter);
            material.SetTexture("_SharedEnvironment", environment);
            material.SetColor(
                "_SubstrateTint", new Color(1f, 0.62f, 0.70f, 1f));
            material.SetColor(
                "_MotifColor", new Color(0.018f, 0.020f, 0.024f, 1f));
            EditorUtility.SetDirty(material);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static Texture2D LoadTexture(string name)
        {
            return AssetDatabase.LoadAssetAtPath<Texture2D>(
                Source + "/Textures/" + name)
                ?? throw new InvalidDataException($"Texture missing: {name}");
        }

        private static void AssignTopMaterials(
            IEnumerable<MeshRenderer> renderers,
            IReadOnlyDictionary<string, Material> materials)
        {
            foreach (MeshRenderer renderer in renderers)
            {
                Material[] assigned = renderer.sharedMaterials.ToArray();
                if (assigned.Length < 4)
                    throw new InvalidDataException(
                        $"Expected four material slots on {renderer.name}.");
                if (renderer.name == "MovingTopBody")
                    assigned[3] = materials["upper"];
                else if (renderer.name == "BottomExterior")
                    assigned[3] = materials["lower"];
                renderer.sharedMaterials = assigned;
            }
        }

        private static void AssignFlatTopMaterials(
            IEnumerable<MeshRenderer> renderers)
        {
            Material upper = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_EDC/Candidates/MagneticSlideTileGate11R011/"
                + "Materials/M_G11R011_UpperTopArtwork.mat");
            Material lower = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_EDC/Candidates/MagneticSlideTileGate11R011/"
                + "Materials/M_G11R011_LowerTopArtwork.mat");
            Material side = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_EDC/Candidates/MagneticSlideTileGate11R011/"
                + "Materials/M_G11R011_SolidDarkSide.mat");
            Material rim = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_EDC/Candidates/MagneticSlideTileGate11R011/"
                + "Materials/M_G11R011_PolishedBrightSilverRim.mat");
            Material underside = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_EDC/Candidates/MagneticSlideTileGate11R011/"
                + "Materials/M_G11R011_NeutralUnderside.mat");
            if (upper == null || lower == null || side == null
                || rim == null || underside == null)
                throw new InvalidDataException("Flat comparison materials missing.");
            foreach (MeshRenderer renderer in renderers)
            {
                Material[] assigned = renderer.sharedMaterials.ToArray();
                if (assigned.Length < 4)
                    throw new InvalidDataException(
                        $"Expected four material slots on {renderer.name}.");
                assigned[0] = side;
                assigned[1] = rim;
                assigned[2] = underside;
                if (renderer.name == "MovingTopBody")
                    assigned[3] = upper;
                else if (renderer.name == "BottomExterior")
                    assigned[3] = lower;
                renderer.sharedMaterials = assigned;
            }
        }

        private static void CaptureReflectionMotion(
            Camera camera,
            MagneticSlideTileShippingCoordinator coordinator,
            string directory)
        {
            coordinator.ResetShippingPose(false);
            Vector3 target = new(0f, 0.004f, 0f);
            const int frameCount = 180;
            for (int frame = 0; frame < frameCount; frame++)
            {
                float phase = frame / (float)(frameCount - 1);
                float angle = Mathf.Lerp(-42f, 42f, phase) * Mathf.Deg2Rad;
                Vector3 position = new(
                    Mathf.Sin(angle) * 0.105f,
                    0.055f + Mathf.Sin(phase * Mathf.PI) * 0.012f,
                    -Mathf.Cos(angle) * 0.105f);
                camera.transform.SetPositionAndRotation(
                    position,
                    Quaternion.LookRotation(target - position, Vector3.up));
                camera.usePhysicalProperties = false;
                camera.fieldOfView = 28f;
                RenderCurrent(
                    camera,
                    Path.Combine(directory, $"frame-{frame:D4}.png"),
                    1280,
                    720);
            }
        }

        private static void ApplyPose(
            MagneticSlideTileShippingCoordinator coordinator,
            Pose pose)
        {
            coordinator.ResetShippingPose(false);
            if (pose == Pose.MaximumOpen)
            {
                coordinator.TryApplySlideInput(
                    coordinator.Settings.MaximumTravelMeters, false);
            }
        }

        private static void Render(
            Camera camera,
            string directory,
            ViewRecipe view)
        {
            camera.transform.SetPositionAndRotation(
                view.Position,
                Quaternion.LookRotation(view.LookAt - view.Position, Vector3.up));
            camera.usePhysicalProperties = false;
            camera.fieldOfView = view.FieldOfView;
            camera.aspect = (float)view.Width / view.Height;
            RenderCurrent(
                camera,
                Path.Combine(directory, view.Id + ".png"),
                view.Width,
                view.Height);
        }

        private static void RenderCurrent(
            Camera camera,
            string path,
            int width,
            int height)
        {
            RenderTexture target = new(
                width, height, 24, RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Default);
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            try
            {
                target.Create();
                camera.targetTexture = target;
                camera.Render();
                camera.Render();
                RenderTexture.active = target;
                Texture2D image = new(
                    width, height, TextureFormat.RGBA32, false, false);
                image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(path, image.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(image);
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static Bounds CalculateBounds(IReadOnlyList<MeshRenderer> renderers)
        {
            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Count; index++)
                bounds.Encapsulate(renderers[index].bounds);
            return bounds;
        }

        private static string MeshIdentity(Mesh mesh)
        {
            return $"{AssetDatabase.GetAssetPath(mesh)}|{mesh.name}|"
                + $"{mesh.vertexCount}|{mesh.subMeshCount}|{mesh.bounds}";
        }

        private static Dictionary<string, string> HashProtectedSources(
            string projectRoot)
        {
            return ProtectedSources.ToDictionary(
                path => path,
                path => Sha256(Path.Combine(projectRoot, path)));
        }

        private static string Sha256(string path)
        {
            using SHA256 algorithm = SHA256.Create();
            using FileStream stream = File.OpenRead(path);
            return BitConverter.ToString(algorithm.ComputeHash(stream))
                .Replace("-", string.Empty)
                .ToLowerInvariant();
        }

        private enum Pose
        {
            Closed,
            MaximumOpen,
        }

        private readonly struct ViewRecipe
        {
            public ViewRecipe(
                string id,
                Vector3 position,
                Vector3 lookAt,
                float fieldOfView,
                int width,
                int height,
                Pose pose)
            {
                Id = id;
                Position = position;
                LookAt = lookAt;
                FieldOfView = fieldOfView;
                Width = width;
                Height = height;
                Pose = pose;
            }

            public string Id { get; }
            public Vector3 Position { get; }
            public Vector3 LookAt { get; }
            public float FieldOfView { get; }
            public int Width { get; }
            public int Height { get; }
            public Pose Pose { get; }
        }

        private readonly struct CameraState
        {
            private readonly Vector3 position;
            private readonly Quaternion rotation;
            private readonly bool physical;
            private readonly float fieldOfView;
            private readonly float aspect;

            public CameraState(Camera camera)
            {
                position = camera.transform.position;
                rotation = camera.transform.rotation;
                physical = camera.usePhysicalProperties;
                fieldOfView = camera.fieldOfView;
                aspect = camera.aspect;
            }

            public void Restore(Camera camera)
            {
                camera.transform.SetPositionAndRotation(position, rotation);
                camera.usePhysicalProperties = physical;
                camera.fieldOfView = fieldOfView;
                camera.aspect = aspect;
            }
        }

        [Serializable]
        private sealed class MaterialReviewReport
        {
            public int schemaVersion;
            public string gate;
            public int evidenceRevision;
            public string sourceScene;
            public string sceneSha256Before;
            public string sceneSha256After;
            public string userFeedback;
            public string rootCause;
            public string architecture;
            public string shaderName;
            public bool shaderSupported;
            public string shaderTarget;
            public int shaderErrorCount;
            public int shaderWarningCount;
            public string srpBatcherLayout;
            public int topPasses;
            public int addedRenderers;
            public int addedDrawCalls;
            public int textureSamplesPerTopPixel;
            public int cubemapSamplesPerTopPixel;
            public string estimatedMobileCost;
            public float coatIor;
            public float coatRoughness;
            public float coatStrength;
            public float layerDepthUv;
            public float micaScale;
            public float microflakeScale;
            public float microflakeStrength;
            public float iridescenceStrength;
            public float motifRoughness;
            public float motifMetallic;
            public float motifReliefUv;
            public float emission;
            public bool protectedRuntimeUnchanged;
            public bool geometryMeshInstancesUnchanged;
            public float boundsCenterDeltaMeters;
            public float boundsSizeDeltaMeters;
            public int rendererCountBefore;
            public int rendererCountAfter;
            public int materialSlotsBefore;
            public int materialSlotsAfter;
            public bool candidateActive;
            public bool fallbackActive;
            public bool mechanismPoseLegal;
            public bool build44Installed;
            public string deviceAcceptance;
            public string visualApproval;
            public bool pass;
        }
    }
}
