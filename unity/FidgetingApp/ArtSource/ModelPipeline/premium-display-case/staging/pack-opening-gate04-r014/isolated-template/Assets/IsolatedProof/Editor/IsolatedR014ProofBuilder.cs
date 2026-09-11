using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.Candidates;
using FidgetingApp.DisplayCase.IsolatedCandidate;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.Editor
{
    public static class IsolatedR014ProofBuilder
    {
        private const string Root = "Assets/IsolatedProof";
        private const string Generated = Root + "/Generated";
        private const string ScenePath = Generated + "/PackOpeningGate04R014Isolated.unity";
        private const string ProfilePath = Generated + "/PackOpeningGate04R014Profile.asset";
        private const string RigPath = "Assets/Source/R014/PackOpeningGate04R014PackOnlyRig.fbx";
        private const string CasePrefabPath =
            "Assets/Source/PremiumDisplayCase/Prefabs/PresentationRoot.prefab";
        private const string PackArtPath = "Assets/Source/Pack/gacha-pack-standard-body.png";
        private const string FlapArtPath = "Assets/Source/Pack/gacha-pack-standard-flap.png";
        private const string EnvironmentPath =
            "Assets/Source/Environment/canyon-unified-ledgestone-v1-2x.png";
        private const int Width = 1206;
        private const int Height = 2622;
        private const int FrameRate = 60;
        private const int FrameCount = 96;
        private static readonly int[] PrimaryFrames = { 0, 16, 29, 43, 59, 74 };

        [MenuItem("Fidgeting/Isolated Candidate/R014 Build Scene")]
        public static void BuildSceneOnly()
        {
            BuildScene();
            Debug.Log("R014_ISOLATED_SCENE_BUILT");
        }

        [MenuItem("Fidgeting/Isolated Candidate/R014 Build And Capture")]
        public static void BuildAndCapture()
        {
            SceneState state = BuildScene();
            string captureRoot = Path.Combine(
                Directory.GetParent(Application.dataPath).FullName, "Captures");
            Directory.CreateDirectory(captureRoot);
            Capture(state, captureRoot, effectsEnabled: true, closeup: false, "normal");
            Capture(state, captureRoot, effectsEnabled: true, closeup: true, "slow-closeup");
            Capture(state, captureRoot, effectsEnabled: false, closeup: false, "effects-off");
            Debug.Log("R014_ISOLATED_CAPTURE_COMPLETE");
        }

        internal static IsolatedR014ProofSequence BuildSequenceForTests()
        {
            return BuildScene().Sequence;
        }

        private static SceneState BuildScene()
        {
            EnsurePipeline();
            AssetDatabase.CreateFolder("Assets", "IsolatedProof");
            if (!AssetDatabase.IsValidFolder(Generated))
            {
                AssetDatabase.CreateFolder(Root, "Generated");
            }

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            PackOpeningGate04R014Profile profile = LoadOrCreateProfile();
            Camera camera = BuildCamera();
            BuildEnvironment();
            BuildLighting();
            Transform caseRoot = BuildActualCase();
            (Transform packRoot, SkinnedMeshRenderer[] renderers) = BuildPack();
            var sequence = new IsolatedR014ProofSequence(
                profile, camera, packRoot, renderers, caseRoot);
            sequence.SetTime(0f, false);
            EditorSceneManager.SaveScene(scene, ScenePath);
            return new SceneState(camera, sequence);
        }

        private static void EnsurePipeline()
        {
            const string path = Generated + "/IsolatedR014URP.asset";
            if (!AssetDatabase.IsValidFolder(Root))
            {
                AssetDatabase.CreateFolder("Assets", "IsolatedProof");
            }
            if (!AssetDatabase.IsValidFolder(Generated))
            {
                AssetDatabase.CreateFolder(Root, "Generated");
            }

            UniversalRenderPipelineAsset pipeline =
                AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(path);
            if (pipeline == null)
            {
                pipeline = UniversalRenderPipelineAsset.Create();
                AssetDatabase.CreateAsset(pipeline, path);
                AssetDatabase.SaveAssets();
            }
            GraphicsSettings.defaultRenderPipeline = pipeline;
            QualitySettings.renderPipeline = pipeline;
        }

        private static PackOpeningGate04R014Profile LoadOrCreateProfile()
        {
            PackOpeningGate04R014Profile profile =
                AssetDatabase.LoadAssetAtPath<PackOpeningGate04R014Profile>(ProfilePath);
            if (profile != null) return profile;
            profile = ScriptableObject.CreateInstance<PackOpeningGate04R014Profile>();
            AssetDatabase.CreateAsset(profile, ProfilePath);
            AssetDatabase.SaveAssets();
            return profile;
        }

        private static Camera BuildCamera()
        {
            var item = new GameObject("IsolatedR014PortraitCamera") { tag = "MainCamera" };
            Camera camera = item.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.003f, 0.004f, 0.005f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.fieldOfView = 27f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.transform.position = new Vector3(0f, -0.006f, -1.10f);
            camera.transform.LookAt(new Vector3(0f, -0.018f, 0.020f));
            return camera;
        }

        private static void BuildEnvironment()
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
            if (shader == null) throw new InvalidOperationException("URP Unlit shader is unavailable.");
            var material = new Material(shader) { name = "StaticDarkMineralEnvironment" };
            material.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(EnvironmentPath));
            material.SetColor("_BaseColor", new Color(0.26f, 0.28f, 0.27f, 1f));
            GameObject item = GameObject.CreatePrimitive(PrimitiveType.Quad);
            item.name = "StaticDarkMineralEnvironment";
            item.transform.position = new Vector3(0f, -0.020f, 1.45f);
            item.transform.localScale = new Vector3(0.90f, 1.52f, 1f);
            UnityEngine.Object.DestroyImmediate(item.GetComponent<Collider>());
            MeshRenderer renderer = item.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
        }

        private static void BuildLighting()
        {
            CreateLight("NeutralKey", Quaternion.Euler(34f, -32f, 0f),
                new Color(1f, 0.90f, 0.78f), 1.32f);
            CreateLight("MineralFill", Quaternion.Euler(54f, 148f, 0f),
                new Color(0.68f, 0.72f, 0.76f), 0.42f);
            CreateLight("FoilEdge", Quaternion.Euler(18f, 210f, 0f),
                new Color(0.94f, 0.82f, 0.66f), 0.46f);
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.135f, 0.140f, 0.145f);
            RenderSettings.ambientEquatorColor = new Color(0.062f, 0.066f, 0.070f);
            RenderSettings.ambientGroundColor = new Color(0.016f, 0.016f, 0.015f);
            RenderSettings.reflectionIntensity = 0.48f;
        }

        private static void CreateLight(
            string name,
            Quaternion rotation,
            Color color,
            float intensity)
        {
            var item = new GameObject(name);
            var light = item.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
            item.transform.rotation = rotation;
        }

        private static Transform BuildActualCase()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(CasePrefabPath);
            if (prefab == null) throw new MissingReferenceException(CasePrefabPath);
            var motion = new GameObject("SingleLivePremiumDisplayCase");
            motion.transform.position = new Vector3(0f, -0.072f, 0.055f);
            motion.transform.localScale = Vector3.one * 0.80f;
            GameObject caseObject = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (caseObject == null) throw new InvalidOperationException("Could not instantiate case.");
            caseObject.name = "ActualUnchangedPremiumDisplayCaseGate11";
            caseObject.transform.SetParent(motion.transform, false);
            Transform contentSlot = FindByName(caseObject.transform, "ContentSlot");
            if (contentSlot == null) throw new InvalidOperationException("Actual case lacks ContentSlot.");
            contentSlot.name = "ContentSlot_CallerOwned_UnchangedEmpty";
            return motion.transform;
        }

        private static (Transform, SkinnedMeshRenderer[]) BuildPack()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(RigPath);
            if (prefab == null) throw new MissingReferenceException(RigPath);
            GameObject rig = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (rig == null) throw new InvalidOperationException("Could not instantiate R014 Pack rig.");
            rig.name = "ActualAuthoredStandardPackOnlyRigR014";
            SkinnedMeshRenderer[] renderers = rig.GetComponentsInChildren<SkinnedMeshRenderer>(true)
                .OrderBy(item => item.name, StringComparer.Ordinal)
                .ToArray();
            if (renderers.Length != 10) throw new InvalidOperationException("R014 rig must contain 10 renderers.");

            Shader packShader = Shader.Find("FidgetingApp/Candidates/MakeItShineCc0PackR014");
            Shader sweepShader = Shader.Find("FidgetingApp/Candidates/MakeItShineCc0ContourSweepR014");
            Shader litShader = Shader.Find("Universal Render Pipeline/Lit");
            if (packShader == null || sweepShader == null || litShader == null)
            {
                throw new InvalidOperationException("R014 or URP shaders are unavailable.");
            }
            Material pack = new(packShader) { name = "Actual384x512PackArtwork" };
            pack.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(PackArtPath));
            pack.SetTexture("_FlapMap", AssetDatabase.LoadAssetAtPath<Texture2D>(FlapArtPath));
            Material inner = new(litShader) { name = "DarkInnerFoilSidewalls" };
            inner.SetColor("_BaseColor", new Color(0.025f, 0.032f, 0.038f, 1f));
            inner.SetFloat("_Metallic", 0.82f);
            inner.SetFloat("_Smoothness", 0.44f);
            Material lip = new(litShader) { name = "FiniteCrimpedFoilLip" };
            lip.SetColor("_BaseColor", new Color(0.72f, 0.66f, 0.55f, 1f));
            lip.SetFloat("_Metallic", 0.92f);
            lip.SetFloat("_Smoothness", 0.67f);
            Material sweep = new(sweepShader) { name = "LocalizedCc0ContourSweep" };
            sweep.SetColor("_RimColor", new Color(1f, 0.82f, 0.60f, 0.34f));

            foreach (SkinnedMeshRenderer renderer in renderers)
            {
                renderer.updateWhenOffscreen = true;
                renderer.sharedMaterial = renderer.name switch
                {
                    "Pack_InnerFoilMouth" or "Pack_InnerBackFoilRim"
                        or "Pack_TearLeadingSidewall" or "Pack_TearTrailingSidewall" => inner,
                    "Pack_RolledCrimpLip" or "Pack_TopRightPullTab" => lip,
                    "Pack_TornContourRim" => sweep,
                    _ => pack
                };
            }
            return (rig.transform, renderers);
        }

        private static Transform FindByName(Transform root, string name)
        {
            if (root.name == name) return root;
            foreach (Transform child in root)
            {
                Transform found = FindByName(child, name);
                if (found != null) return found;
            }
            return null;
        }

        private static void Capture(
            SceneState state,
            string captureRoot,
            bool effectsEnabled,
            bool closeup,
            string pass)
        {
            string root = Path.Combine(captureRoot, pass);
            string frames = Path.Combine(root, "frames");
            string primary = Path.Combine(root, "primary");
            Directory.CreateDirectory(frames);
            Directory.CreateDirectory(primary);
            Vector3 basePosition = state.Camera.transform.position;
            float baseFov = state.Camera.fieldOfView;
            if (closeup)
            {
                state.Camera.fieldOfView = 18f;
                state.Camera.transform.position = new Vector3(0.035f, 0.105f, -0.88f);
                state.Camera.transform.LookAt(new Vector3(0.02f, 0.105f, 0.025f));
            }

            var records = new List<string>();
            RenderTexture target = RenderTexture.GetTemporary(Width, Height, 24, RenderTextureFormat.ARGB32);
            Texture2D pixels = new(Width, Height, TextureFormat.RGB24, false);
            for (int frame = 0; frame < FrameCount; frame++)
            {
                float seconds = frame / (float)FrameRate;
                state.Sequence.SetTime(seconds, effectsEnabled);
                var request = new RenderPipeline.StandardRequest
                {
                    destination = target
                };
                RenderPipeline.SubmitRenderRequest(state.Camera, request);
                RenderTexture.active = target;
                pixels.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                pixels.Apply(false, false);
                byte[] png = pixels.EncodeToPNG();
                string path = Path.Combine(frames, $"frame-{frame:D3}.png");
                File.WriteAllBytes(path, png);
                if (PrimaryFrames.Contains(frame))
                {
                    File.WriteAllBytes(Path.Combine(primary, $"pose-{frame:D3}.png"), png);
                }

                Rect bounds = state.Sequence.GetCaseViewportBounds();
                PackOpeningGate04R014Sample sample = state.Sequence.CurrentSample;
                records.Add(
                    $"{{\"frame\":{frame},\"seconds\":{seconds:F6},\"caseEntityId\":\"{state.Sequence.CaseEntityId}\","
                    + $"\"occlusion\":\"{sample.Occlusion}\",\"tear\":{sample.TearProgress:F6},"
                    + $"\"caseBounds\":[{bounds.xMin:F6},{bounds.yMin:F6},{bounds.width:F6},{bounds.height:F6}],"
                    + $"\"effectsEnabled\":{effectsEnabled.ToString().ToLowerInvariant()}}}");
            }
            RenderTexture.active = null;
            RenderTexture.ReleaseTemporary(target);
            UnityEngine.Object.DestroyImmediate(pixels);
            state.Camera.transform.position = basePosition;
            state.Camera.fieldOfView = baseFov;
            state.Camera.transform.LookAt(new Vector3(0f, -0.018f, 0.020f));
            File.WriteAllText(
                Path.Combine(root, "technical-continuity.json"),
                "{\n"
                + $"\"isolatedUnityCandidate\":true,\n\"width\":{Width},\n\"height\":{Height},\n"
                + $"\"frameRate\":{FrameRate},\n\"frameCount\":{FrameCount},\n"
                + $"\"durationSeconds\":{FrameCount / (float)FrameRate:F2},\n"
                + $"\"caseEntityId\":\"{state.Sequence.CaseEntityId}\",\n"
                + $"\"effectsEnabled\":{effectsEnabled.ToString().ToLowerInvariant()},\n"
                + "\"frames\":[\n" + string.Join(",\n", records) + "\n]}\n");
        }

        private readonly struct SceneState
        {
            public SceneState(Camera camera, IsolatedR014ProofSequence sequence)
            {
                Camera = camera;
                Sequence = sequence;
            }
            public Camera Camera { get; }
            public IsolatedR014ProofSequence Sequence { get; }
        }
    }
}
