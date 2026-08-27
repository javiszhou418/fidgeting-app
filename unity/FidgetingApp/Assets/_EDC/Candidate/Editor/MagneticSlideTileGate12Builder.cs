using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using FidgetingApp.EDC.Candidate;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.EditorTools
{
    public static class MagneticSlideTileGate12Builder
    {
        public const string ShippingScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        public const string CandidateRoot = "Assets/_EDC/Candidate";
        public const string CandidatePrefabPath =
            CandidateRoot + "/Prefabs/MagneticSlideTileCandidate.prefab";
        public const string SettingsPath =
            CandidateRoot + "/Settings/MagneticSlideTileCandidateSettings.asset";
        public const string SilverMaterialPath =
            CandidateRoot + "/Materials/M_Gate12_PolishedSilver.mat";
        public const string UpperMaterialPath =
            CandidateRoot + "/Materials/M_Gate12_CrystalUpper.mat";
        public const string LowerMaterialPath =
            CandidateRoot + "/Materials/M_Gate12_CrystalLower.mat";
        public const string ReflectionPath =
            CandidateRoot + "/Materials/Gate12_ShippingReflection.cubemap";
        public const string ImportedModelPath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/magnetic-slide-tile-r002.fbx";
        public const string UpperTexturePath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/face-upper-transport-basecolor.png";
        public const string LowerTexturePath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/face-lower-transport-basecolor.png";
        public const string Gate11ReflectionPath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev002/Materials/Gate11R2_DirectionContinuousEnvironment.cubemap";

        private const string SwitchName = "MagneticSlideTile_CandidateSwitch";
        private const string CandidateName = "Gate12Candidate_MagneticSlideTile";
        private const int LandscapeWidth = 1600;
        private const int LandscapeHeight = 1000;

        public static void BuildAndCaptureBatch()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidence = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-001");
            Directory.CreateDirectory(evidence);
            BuildCandidateAssets();
            IntegrateCandidateSwitch();
            CaptureShippingViews(evidence, projectRoot);
        }

        private static void BuildCandidateAssets()
        {
            EnsureFolder(CandidateRoot + "/Prefabs");
            EnsureFolder(CandidateRoot + "/Settings");
            EnsureFolder(CandidateRoot + "/Materials");

            MagneticSlideTileCandidateSettings settings =
                AssetDatabase.LoadAssetAtPath<MagneticSlideTileCandidateSettings>(SettingsPath);
            if (settings == null)
            {
                settings = ScriptableObject.CreateInstance<MagneticSlideTileCandidateSettings>();
                AssetDatabase.CreateAsset(settings, SettingsPath);
            }
            if (!settings.IsLockedContractValid)
            {
                throw new InvalidDataException("Candidate shared settings drifted.");
            }

            Material silver = SaveMaterial(SilverMaterialPath, CreateSilverMaterial());
            Material upper = SaveMaterial(
                UpperMaterialPath,
                CreateCrystalMaterial("M_Gate12_CrystalUpper", UpperTexturePath));
            Material lower = SaveMaterial(
                LowerMaterialPath,
                CreateCrystalMaterial("M_Gate12_CrystalLower", LowerTexturePath));
            Cubemap reflection = SaveReflection();

            GameObject source = AssetDatabase.LoadAssetAtPath<GameObject>(ImportedModelPath);
            if (source == null)
            {
                throw new FileNotFoundException("Approved imported candidate model is missing.");
            }
            GameObject candidate = UnityEngine.Object.Instantiate(source);
            candidate.name = CandidateName;
            candidate.transform.SetPositionAndRotation(Vector3.zero, Quaternion.Euler(0f, 90f, 0f));
            candidate.transform.localScale = Vector3.one;

            MeshRenderer[] renderers = candidate.GetComponentsInChildren<MeshRenderer>(true);
            if (renderers.Length != 2)
            {
                throw new InvalidDataException($"Expected two candidate renderers, found {renderers.Length}.");
            }
            foreach (MeshRenderer renderer in renderers)
            {
                bool lowerMesh = renderer.name.Contains("Lower", StringComparison.Ordinal);
                renderer.sharedMaterials = new[] { silver, lowerMesh ? lower : upper };
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
            }

            Transform upperPivot = Find(candidate.transform, "CentralAxisPivot_Point");
            MagneticSlideTileCandidateController controller =
                candidate.AddComponent<MagneticSlideTileCandidateController>();
            controller.Configure(upperPivot, settings);

            var probeObject = new GameObject("Gate12_LocalReflectionProbe");
            probeObject.transform.SetParent(candidate.transform, false);
            probeObject.transform.localPosition = new Vector3(0f, 0.018f, 0f);
            ReflectionProbe probe = probeObject.AddComponent<ReflectionProbe>();
            probe.mode = ReflectionProbeMode.Custom;
            probe.customBakedTexture = reflection;
            probe.boxProjection = false;
            probe.size = new Vector3(0.12f, 0.10f, 0.12f);
            probe.intensity = 1f;
            probe.importance = 100;

            PrefabUtility.SaveAsPrefabAsset(candidate, CandidatePrefabPath);
            UnityEngine.Object.DestroyImmediate(candidate);
            AssetDatabase.SaveAssets();
        }

        private static void IntegrateCandidateSwitch()
        {
            Scene scene = EditorSceneManager.OpenScene(ShippingScenePath, OpenSceneMode.Single);
            GameObject shipping = scene.GetRootGameObjects()
                .Single(root => root.name == "EDC_Root");
            GameObject previous = scene.GetRootGameObjects()
                .FirstOrDefault(root => root.name == SwitchName);
            if (previous != null)
            {
                UnityEngine.Object.DestroyImmediate(previous);
            }

            var switchObject = new GameObject(SwitchName);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(CandidatePrefabPath);
            GameObject candidate = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
            candidate.name = CandidateName;
            candidate.transform.SetParent(switchObject.transform, true);
            candidate.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            MagneticSlideTileCandidateActivation activation =
                switchObject.AddComponent<MagneticSlideTileCandidateActivation>();
            activation.Configure(shipping, candidate);
            activation.SetCandidatePreview(false);
            RestoreShippingDefaults(scene);

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ShippingScenePath, true);
            AssetDatabase.SaveAssets();
        }

        private static void RestoreShippingDefaults(Scene scene)
        {
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Skybox;
            RenderSettings.customReflectionTexture = null;
            RenderSettings.reflectionIntensity = 0.35f;
            RenderSettings.reflectionBounces = 1;

            Camera camera = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single();
            camera.transform.localPosition = new Vector3(0f, 0.1016102f, -0.17515755f);
            camera.transform.localRotation = new Quaternion(
                0.25881907f,
                0f,
                0f,
                0.9659258f);
            camera.backgroundColor = new Color(0.012f, 0.016f, 0.023f, 1f);
            camera.focalLength = 50f;
            camera.fieldOfView = 26.991467f;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 5f;

            Component framer = camera.GetComponent("EdcPortraitCameraFramer");
            if (framer != null)
            {
                var serialized = new SerializedObject(framer);
                serialized.FindProperty("screenWidthFraction").floatValue = 0.64f;
                serialized.FindProperty("screenHeightFraction").floatValue = 0.64f;
                serialized.ApplyModifiedPropertiesWithoutUndo();
            }
        }

        private static void CaptureShippingViews(string evidence, string projectRoot)
        {
            Scene scene = EditorSceneManager.OpenScene(ShippingScenePath, OpenSceneMode.Single);
            MagneticSlideTileCandidateActivation activation = scene.GetRootGameObjects()
                .Select(root => root.GetComponent<MagneticSlideTileCandidateActivation>())
                .Single(component => component != null);
            if (activation.CandidatePreviewEnabled
                || !activation.ShippingModel.activeSelf
                || activation.CandidateModel.activeSelf)
            {
                throw new InvalidDataException("Shipping scene did not open with the current model active.");
            }
            string defaultSceneHash = Sha256(Path.Combine(projectRoot, ShippingScenePath));

            Camera camera = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single();
            activation.SetCandidatePreview(true);
            GameObject candidate = activation.CandidateModel;
            MagneticSlideTileCandidateController controller =
                candidate.GetComponent<MagneticSlideTileCandidateController>();
            ReflectionProbe probe = candidate.GetComponentInChildren<ReflectionProbe>(true);
            ConfigureShippingReflection(probe);
            foreach (Light light in scene.GetRootGameObjects()
                         .SelectMany(root => root.GetComponentsInChildren<Light>(true)))
            {
                light.enabled = true;
            }

            var views = new List<ViewRecord>();
            CaptureView(camera, candidate, evidence, views, "library",
                new Vector3(0f, 0.070f, -0.135f), new Vector3(0f, 0f, 0f), 42f,
                LandscapeWidth, LandscapeHeight);
            CaptureView(camera, candidate, evidence, views, "hero",
                new Vector3(0.044f, 0.040f, -0.064f), new Vector3(0f, 0f, 0f), 36f,
                LandscapeWidth, LandscapeHeight);
            CaptureView(camera, candidate, evidence, views, "top",
                new Vector3(0f, 0.115f, -0.006f), Vector3.zero, 38f,
                LandscapeWidth, LandscapeHeight);
            CaptureView(camera, candidate, evidence, views, "left-oblique",
                new Vector3(-0.055f, 0.040f, -0.055f), Vector3.zero, 36f,
                LandscapeWidth, LandscapeHeight);
            CaptureView(camera, candidate, evidence, views, "right-oblique",
                new Vector3(0.055f, 0.040f, -0.055f), Vector3.zero, 36f,
                LandscapeWidth, LandscapeHeight);
            CaptureView(camera, candidate, evidence, views, "low",
                new Vector3(0.045f, 0.018f, -0.070f), new Vector3(0f, 0.002f, 0f), 36f,
                LandscapeWidth, LandscapeHeight);
            CaptureView(camera, candidate, evidence, views, "phone",
                new Vector3(0.030f, 0.030f, -0.050f), Vector3.zero, 38f,
                1290, 2796);

            controller.SetSlideProgress(1f);
            CaptureView(camera, candidate, evidence, views, "slide-open",
                new Vector3(0.055f, 0.055f, -0.078f), new Vector3(-0.005f, 0f, 0f), 40f,
                LandscapeWidth, LandscapeHeight);
            controller.ResetPose();
            controller.SetDetentIndex(5);
            CaptureView(camera, candidate, evidence, views, "ratchet-60deg",
                new Vector3(0.044f, 0.040f, -0.064f), Vector3.zero, 36f,
                LandscapeWidth, LandscapeHeight);
            controller.ResetPose();

            ShippingReport report = BuildReport(
                candidate,
                controller,
                probe,
                views,
                defaultSceneHash,
                projectRoot);
            File.WriteAllText(
                Path.Combine(evidence, "gate12-shipping-report.json"),
                JsonUtility.ToJson(report, true) + "\n");

            activation.SetCandidatePreview(false);
            if (!activation.ShippingModel.activeSelf || activation.CandidateModel.activeSelf)
            {
                throw new InvalidDataException("Candidate preview did not return to safe default.");
            }
            EditorSceneManager.OpenScene(ShippingScenePath, OpenSceneMode.Single);
            string finalSceneHash = Sha256(Path.Combine(projectRoot, ShippingScenePath));
            if (finalSceneHash != defaultSceneHash)
            {
                throw new InvalidDataException("Preview capture changed the saved shipping scene.");
            }
            Debug.Log(
                $"[Gate12] views={views.Count} scene={ShippingScenePath} "
                + $"defaultCandidate={activation.CandidatePreviewEnabled} pass={report.pass}");
            if (!report.pass)
            {
                throw new InvalidDataException(
                    "Gate 12 shipping preview failed: " + string.Join(" | ", report.failures));
            }
        }

        private static void ConfigureShippingReflection(ReflectionProbe probe)
        {
            Cubemap reflection = AssetDatabase.LoadAssetAtPath<Cubemap>(ReflectionPath);
            probe.mode = ReflectionProbeMode.Custom;
            probe.customBakedTexture = reflection;
            probe.boxProjection = false;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = reflection;
            RenderSettings.reflectionIntensity = 1f;
            RenderSettings.reflectionBounces = 1;
        }

        private static void CaptureView(
            Camera camera,
            GameObject candidate,
            string evidence,
            List<ViewRecord> views,
            string id,
            Vector3 position,
            Vector3 lookAt,
            float verticalFov,
            int width,
            int height)
        {
            camera.transform.position = position;
            camera.transform.rotation = Quaternion.LookRotation(lookAt - position, Vector3.up);
            camera.fieldOfView = verticalFov;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 3f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.008f, 0.011f, 0.016f, 1f);
            camera.allowHDR = false;
            Render(camera, Path.Combine(evidence, id + ".png"), width, height);
            views.Add(new ViewRecord
            {
                id = id,
                output = id + ".png",
                cameraPosition = position,
                lookAt = lookAt,
                verticalFovDegrees = verticalFov,
                resolution = new Vector2Int(width, height),
                candidateActive = candidate.activeSelf
            });
        }

        private static void Render(Camera camera, string path, int width, int height)
        {
            var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            var image = new Texture2D(width, height, TextureFormat.RGBA32, false, false);
            RenderTexture previous = RenderTexture.active;
            float aspect = camera.aspect;
            try
            {
                target.Create();
                camera.aspect = (float)width / height;
                camera.targetTexture = target;
                var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(path, image.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = null;
                camera.aspect = aspect;
                RenderTexture.active = previous;
                UnityEngine.Object.DestroyImmediate(image);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static ShippingReport BuildReport(
            GameObject candidate,
            MagneticSlideTileCandidateController controller,
            ReflectionProbe probe,
            List<ViewRecord> views,
            string sceneHash,
            string projectRoot)
        {
            MeshFilter[] filters = candidate.GetComponentsInChildren<MeshFilter>(true);
            MeshRenderer[] renderers = candidate.GetComponentsInChildren<MeshRenderer>(true);
            int triangles = filters.Sum(filter => filter.sharedMesh.triangles.Length / 3);
            Bounds bounds = renderers[0].bounds;
            foreach (MeshRenderer renderer in renderers.Skip(1)) bounds.Encapsulate(renderer.bounds);
            float[] dimensions = { bounds.size.x, bounds.size.y, bounds.size.z };
            Array.Sort(dimensions);
            Material[] materials = renderers.SelectMany(renderer => renderer.sharedMaterials)
                .Distinct().ToArray();
            var failures = new List<string>();
            Check(filters.Length == 2, "render mesh count", failures);
            Check(triangles == 4096, "triangle count", failures);
            Check(Mathf.Abs(dimensions[0] - 0.012f) < 0.00001f, "thickness", failures);
            Check(Mathf.Abs(dimensions[1] - 0.031f) < 0.00001f, "width", failures);
            Check(Mathf.Abs(dimensions[2] - 0.050f) < 0.00001f, "length", failures);
            Check(controller.Settings.IsLockedContractValid, "shared settings", failures);
            Check(controller.AngularVelocityDegreesPerSecond == 0f, "angular velocity", failures);
            Check(controller.LinearVelocityMetersPerSecond == 0f, "linear velocity", failures);
            Check(!controller.RuntimeInputIntegrated && !controller.HapticsIntegrated, "delivery state", failures);
            Check(!probe.boxProjection, "reflection probe", failures);
            Check(materials.All(material => !material.IsKeywordEnabled("_EMISSION")), "emission", failures);
            Check(views.Count == 9 && views.All(view => view.candidateActive), "view capture", failures);

            return new ShippingReport
            {
                pass = failures.Count == 0,
                failures = failures.ToArray(),
                unityVersion = Application.unityVersion,
                urpVersion = "17.5.0",
                shippingScenePath = ShippingScenePath,
                shippingSceneHash = sceneHash,
                candidatePrefabPath = CandidatePrefabPath,
                candidateDefaultActive = false,
                currentShippingModelDefaultActive = true,
                candidateActivationControl = SwitchName,
                sourceModelPath = ImportedModelPath,
                sourceModelSha256 = Sha256(Path.Combine(projectRoot, ImportedModelPath)),
                upperArtworkPath = UpperTexturePath,
                upperArtworkSha256 = Sha256(Path.Combine(projectRoot, UpperTexturePath)),
                lowerArtworkPath = LowerTexturePath,
                lowerArtworkSha256 = Sha256(Path.Combine(projectRoot, LowerTexturePath)),
                upperLowerArtworkIndependent = UpperTexturePath != LowerTexturePath,
                renderMeshes = filters.Length,
                vertices = filters.Sum(filter => filter.sharedMesh.vertexCount),
                triangles = triangles,
                sortedBoundsMeters = dimensions,
                slideTravelMeters = controller.Settings.SlideTravelMeters,
                detentCount = controller.Settings.DetentCount,
                detentStepDegrees = controller.Settings.DetentStepDegrees,
                zeroInitialAndResetVelocity = true,
                runtimeInputIntegrated = controller.RuntimeInputIntegrated,
                hapticsIntegrated = controller.HapticsIntegrated,
                reflectionProbe = new ReflectionRecord
                {
                    mode = probe.mode.ToString(),
                    boxProjection = probe.boxProjection,
                    mipCount = ((Cubemap)probe.customBakedTexture).mipmapCount,
                    filterMode = probe.customBakedTexture.filterMode.ToString()
                },
                materials = materials.Select(material => new MaterialRecord
                {
                    name = material.name,
                    shader = material.shader.name,
                    emissionEnabled = material.IsKeywordEnabled("_EMISSION")
                }).ToArray(),
                materialGaps = new[]
                {
                    "Mobile custom crystal shader approximates clearcoat, back-light transmission and Fresnel iridescence in one opaque pass.",
                    "It does not provide ray-traced refraction, physical volume absorption or Blender thin-film spectral transport.",
                    "No device HDR, thermal, memory or Haptic acceptance has been measured."
                },
                views = views.ToArray(),
                deliveryState = "real-shipping-scene-candidate-preview-only",
                gate12Approval = "pending",
                deviceAcceptance = "pending",
                buildInstallPhonePush = "not-started"
            };
        }

        private static Material CreateSilverMaterial()
        {
            Material material = NewMaterial("Universal Render Pipeline/Lit");
            material.name = "M_Gate12_PolishedSilver";
            SetColor(material, "_BaseColor", new Color(0.97f, 0.965f, 0.94f, 1f));
            SetFloat(material, "_Metallic", 1f);
            SetFloat(material, "_Smoothness", 0.97f);
            SetFloat(material, "_ClearCoatMask", 0.06f);
            SetFloat(material, "_ClearCoatSmoothness", 0.98f);
            return material;
        }

        private static Material CreateCrystalMaterial(string name, string texturePath)
        {
            Material material = NewMaterial("FidgetingApp/EDC/MagneticCrystalMobile");
            material.name = name;
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
            if (texture == null) throw new FileNotFoundException(texturePath);
            material.SetTexture("_BaseMap", texture);
            material.SetColor("_BaseColor", new Color(0.74f, 0.065f, 0.075f, 1f));
            material.SetFloat("_ClearCoat", 0.92f);
            material.SetFloat("_Iridescence", 0.16f);
            material.SetFloat("_TransmissionApprox", 0.18f);
            return material;
        }

        private static Material NewMaterial(string shaderName)
        {
            Shader shader = Shader.Find(shaderName);
            if (shader == null) throw new InvalidDataException($"Missing shader {shaderName}.");
            return new Material(shader);
        }

        private static Material SaveMaterial(string path, Material material)
        {
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static Cubemap SaveReflection()
        {
            Cubemap source = AssetDatabase.LoadAssetAtPath<Cubemap>(Gate11ReflectionPath);
            if (source == null) throw new FileNotFoundException(Gate11ReflectionPath);
            Cubemap clone = UnityEngine.Object.Instantiate(source);
            clone.name = "Gate12_ShippingReflection";
            clone.filterMode = FilterMode.Trilinear;
            clone.wrapMode = TextureWrapMode.Clamp;
            AssetDatabase.DeleteAsset(ReflectionPath);
            AssetDatabase.CreateAsset(clone, ReflectionPath);
            return AssetDatabase.LoadAssetAtPath<Cubemap>(ReflectionPath);
        }

        private static Transform Find(Transform parent, string name)
        {
            foreach (Transform child in parent.GetComponentsInChildren<Transform>(true))
            {
                if (child.name == name) return child;
            }
            throw new InvalidDataException($"Missing transform {name}.");
        }

        private static void EnsureFolder(string path)
        {
            string[] segments = path.Split('/');
            string current = segments[0];
            for (int index = 1; index < segments.Length; index++)
            {
                string next = current + "/" + segments[index];
                if (!AssetDatabase.IsValidFolder(next))
                    AssetDatabase.CreateFolder(current, segments[index]);
                current = next;
            }
        }

        private static void SetFloat(Material material, string property, float value)
        {
            if (material.HasProperty(property)) material.SetFloat(property, value);
        }

        private static void SetColor(Material material, string property, Color value)
        {
            if (material.HasProperty(property)) material.SetColor(property, value);
        }

        private static void Check(bool condition, string failure, List<string> failures)
        {
            if (!condition) failures.Add(failure);
        }

        private static string Sha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            using SHA256 sha = SHA256.Create();
            byte[] hash = sha.ComputeHash(stream);
            var builder = new StringBuilder(hash.Length * 2);
            foreach (byte value in hash) builder.Append(value.ToString("x2"));
            return builder.ToString();
        }

        [Serializable]
        private sealed class ShippingReport
        {
            public bool pass;
            public string[] failures;
            public string unityVersion;
            public string urpVersion;
            public string shippingScenePath;
            public string shippingSceneHash;
            public string candidatePrefabPath;
            public bool candidateDefaultActive;
            public bool currentShippingModelDefaultActive;
            public string candidateActivationControl;
            public string sourceModelPath;
            public string sourceModelSha256;
            public string upperArtworkPath;
            public string upperArtworkSha256;
            public string lowerArtworkPath;
            public string lowerArtworkSha256;
            public bool upperLowerArtworkIndependent;
            public int renderMeshes;
            public int vertices;
            public int triangles;
            public float[] sortedBoundsMeters;
            public float slideTravelMeters;
            public int detentCount;
            public float detentStepDegrees;
            public bool zeroInitialAndResetVelocity;
            public bool runtimeInputIntegrated;
            public bool hapticsIntegrated;
            public ReflectionRecord reflectionProbe;
            public MaterialRecord[] materials;
            public string[] materialGaps;
            public ViewRecord[] views;
            public string deliveryState;
            public string gate12Approval;
            public string deviceAcceptance;
            public string buildInstallPhonePush;
        }

        [Serializable]
        private sealed class ReflectionRecord
        {
            public string mode;
            public bool boxProjection;
            public int mipCount;
            public string filterMode;
        }

        [Serializable]
        private sealed class MaterialRecord
        {
            public string name;
            public string shader;
            public bool emissionEnabled;
        }

        [Serializable]
        private sealed class ViewRecord
        {
            public string id;
            public string output;
            public Vector3 cameraPosition;
            public Vector3 lookAt;
            public float verticalFovDegrees;
            public Vector2Int resolution;
            public bool candidateActive;
        }
    }
}
