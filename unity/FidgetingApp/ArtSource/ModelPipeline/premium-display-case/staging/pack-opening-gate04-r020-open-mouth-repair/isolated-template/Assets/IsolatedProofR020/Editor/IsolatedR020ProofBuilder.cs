using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.IsolatedCandidate.R020;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R020.Editor
{
    public static class IsolatedR020ProofBuilder
    {
        private const string Root = "Assets/IsolatedProofR020";
        private const string Generated = Root + "/Generated";
        private const string ScenePath =
            Generated + "/PackOpeningGate04R020Isolated.unity";
        private const string ProfilePath =
            Generated + "/IsolatedR020Profile.asset";
        private const string FixedPipelinePath =
            "Assets/IsolatedProof/Generated/IsolatedR014URPFixed.asset";
        private const string FixedRendererPath =
            "Assets/IsolatedProof/Generated/IsolatedR014Renderer.asset";
        private const string RigPath =
            "Assets/Source/R020/PackOpeningGate04R020PackOnlyRig.fbx";
        private const string R017MirrorControlRigPath =
            "Assets/Source/R017Control/PackOpeningGate04R017MirrorControl.fbx";
        private const string CasePrefabPath =
            "Assets/Source/PremiumDisplayCase/Prefabs/PresentationRoot.prefab";
        private const string PackBodyPath =
            "Assets/Source/Pack/gacha-pack-standard-body.png";
        private const string PackFlapPath =
            "Assets/Source/Pack/gacha-pack-standard-flap.png";
        private const string EnvironmentPath =
            "Assets/Source/Environment/canyon-unified-ledgestone-v1-2x.png";

        [MenuItem("Fidgeting/Isolated Candidate/R020 Run Preflight")]
        public static void RunPreCaptureStaticTest()
        {
            RunInPlayMode(
                IsolatedR020RunMode.PreCaptureStatic,
                "r020-preflight");
        }

        [MenuItem("Fidgeting/Isolated Candidate/R020 Run Scrub")]
        public static void RunScrub()
        {
            RunInPlayMode(IsolatedR020RunMode.Scrub, "r020-scrub");
        }

        [MenuItem("Fidgeting/Isolated Candidate/R020 Run Full Proof")]
        public static void RunFullProof()
        {
            RunInPlayMode(IsolatedR020RunMode.FullProof, "r020-full-proof");
        }

        [MenuItem("Fidgeting/Isolated Candidate/R020 Build Scene")]
        public static void BuildSceneOnly()
        {
            BuildScene();
            Debug.Log("R020_ISOLATED_SCENE_BUILT");
        }

        internal static IsolatedR020ProofSequence BuildSequenceForTests()
        {
            SceneState state = BuildScene();
            var sequence = new IsolatedR020ProofSequence(
                state.Profile,
                state.Camera,
                state.PackRoot,
                state.PackRenderers,
                state.CaseRoot);
            sequence.InitializeSealedState();
            return sequence;
        }

        private static void RunInPlayMode(
            IsolatedR020RunMode mode,
            string captureDirectory)
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                throw new InvalidOperationException(
                    "R020 capture must start from isolated Edit Mode.");
            }
            string captureRoot = Path.Combine(
                ProjectRoot,
                "Captures",
                captureDirectory);
            if (Directory.Exists(captureRoot))
            {
                throw new InvalidOperationException(
                    $"R020 capture already exists: {captureRoot}");
            }
            SceneState state = BuildScene();
            var item = new GameObject("IsolatedR020RuntimeCaptureDriver");
            var driver = item.AddComponent<IsolatedR020ProofRuntimeDriver>();
            driver.Configure(
                mode,
                state.Profile,
                state.Camera,
                state.PackRoot,
                state.PackRenderers,
                state.CaseRoot,
                state.R017MirrorControlFront,
                captureRoot,
                ScenePath);
            EditorSceneManager.SaveScene(SceneManager.GetActiveScene(), ScenePath);
            AssetDatabase.SaveAssets();
            EditorApplication.delayCall += EnterPlayMode;
        }

        private static void EnterPlayMode()
        {
            if (!EditorApplication.isPlayingOrWillChangePlaymode)
            {
                EditorApplication.isPlaying = true;
            }
        }

        private static SceneState BuildScene()
        {
            AssertEngineAndSourceBoundary();
            EnsureFolder(Root);
            EnsureFolder(Generated);
            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            Camera camera = BuildCamera();
            BuildEnvironment();
            BuildLighting();
            Transform caseRoot = BuildActualCase();
            (Transform packRoot, SkinnedMeshRenderer[] renderers) = BuildPack();
            SkinnedMeshRenderer r017MirrorControlFront =
                BuildR017MirrorControl();
            IsolatedR020Profile profile = LoadOrCreateProfile();
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            return new SceneState(
                profile,
                camera,
                packRoot,
                renderers,
                caseRoot,
                r017MirrorControlFront);
        }

        private static void AssertEngineAndSourceBoundary()
        {
            if (Application.unityVersion != "6000.5.6f1")
            {
                throw new InvalidOperationException(
                    $"R020 requires Unity 6000.5.6f1, got {Application.unityVersion}.");
            }
            UnityEditor.PackageManager.PackageInfo package =
                UnityEditor.PackageManager.PackageInfo.FindForAssetPath(
                "Packages/com.unity.render-pipelines.universal");
            if (package == null || package.version != "17.5.0")
            {
                throw new InvalidOperationException(
                    $"R020 requires URP 17.5.0, got {package?.version ?? "missing"}.");
            }

            UniversalRenderPipelineAsset pipeline =
                AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(
                    FixedPipelinePath);
            UniversalRendererData renderer =
                AssetDatabase.LoadAssetAtPath<UniversalRendererData>(
                    FixedRendererPath);
            if (pipeline == null || renderer == null)
            {
                throw new InvalidOperationException(
                    "R020 requires the recovered R014 URP default renderer.");
            }
            GraphicsSettings.defaultRenderPipeline = pipeline;
            QualitySettings.renderPipeline = pipeline;

            foreach (string path in new[]
                     {
                         RigPath,
                         R017MirrorControlRigPath,
                         CasePrefabPath,
                         PackBodyPath,
                         PackFlapPath,
                         EnvironmentPath
                     })
            {
                if (!File.Exists(Path.Combine(ProjectRoot, path)))
                {
                    throw new FileNotFoundException(
                        "Missing isolated R020 source.",
                        path);
                }
            }
            AssertReadableUnbakedBlendShapeImporter(RigPath);
            AssertReadableUnbakedBlendShapeImporter(R017MirrorControlRigPath);
        }

        private static void AssertReadableUnbakedBlendShapeImporter(string path)
        {
            ModelImporter importer = AssetImporter.GetAtPath(path) as ModelImporter;
            if (importer == null
                || !importer.importBlendShapes
                || importer.bakeAxisConversion)
            {
                throw new InvalidOperationException(
                    "R020 requires unbaked-axis Pack-only blend-shape imports.");
            }
            if (!importer.isReadable)
            {
                importer.isReadable = true;
                importer.SaveAndReimport();
            }
        }

        private static void EnsureFolder(string path)
        {
            string[] segments = path.Split('/');
            string current = segments[0];
            for (int index = 1; index < segments.Length; index++)
            {
                string next = current + "/" + segments[index];
                if (!AssetDatabase.IsValidFolder(next))
                {
                    AssetDatabase.CreateFolder(current, segments[index]);
                }
                current = next;
            }
        }

        private static IsolatedR020Profile LoadOrCreateProfile()
        {
            IsolatedR020Profile profile =
                AssetDatabase.LoadAssetAtPath<IsolatedR020Profile>(ProfilePath);
            if (profile != null)
            {
                return profile;
            }
            profile = ScriptableObject.CreateInstance<IsolatedR020Profile>();
            AssetDatabase.CreateAsset(profile, ProfilePath);
            return profile;
        }

        private static Camera BuildCamera()
        {
            var item = new GameObject("IsolatedR020PortraitCamera")
            {
                tag = "MainCamera"
            };
            Camera camera = item.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.003f, 0.004f, 0.005f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.fieldOfView = 27f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.transform.position = new Vector3(0f, -0.010f, -1.08f);
            camera.transform.LookAt(new Vector3(0f, -0.010f, 0.035f));
            return camera;
        }

        private static void BuildEnvironment()
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
            if (shader == null)
            {
                throw new MissingReferenceException(
                    "URP Unlit shader is unavailable.");
            }
            var material = new Material(shader)
            {
                name = "R020StaticDarkMineralEnvironment"
            };
            material.SetTexture(
                "_BaseMap",
                AssetDatabase.LoadAssetAtPath<Texture2D>(EnvironmentPath));
            material.SetColor(
                "_BaseColor",
                new Color(0.31f, 0.33f, 0.32f, 1f));
            GameObject item = GameObject.CreatePrimitive(PrimitiveType.Quad);
            item.name = "R020StaticDarkMineralEnvironment";
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
            CreateLight(
                "R020NeutralKey",
                Quaternion.Euler(34f, -32f, 0f),
                new Color(1f, 0.90f, 0.78f),
                1.50f,
                0.35f);
            CreateLight(
                "R020MineralFill",
                Quaternion.Euler(54f, 148f, 0f),
                new Color(0.68f, 0.72f, 0.76f),
                0.52f,
                0.16f);
            CreateLight(
                "R020FoilEdge",
                Quaternion.Euler(18f, 210f, 0f),
                new Color(0.94f, 0.82f, 0.66f),
                0.50f,
                0.20f);
            CreateMouthBounce();
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.155f, 0.160f, 0.165f);
            RenderSettings.ambientEquatorColor =
                new Color(0.072f, 0.076f, 0.080f);
            RenderSettings.ambientGroundColor =
                new Color(0.018f, 0.018f, 0.017f);
            RenderSettings.reflectionIntensity = 0.54f;
        }

        private static void CreateLight(
            string name,
            Quaternion rotation,
            Color color,
            float intensity,
            float shadowStrength)
        {
            var item = new GameObject(name);
            item.transform.rotation = rotation;
            Light light = item.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
            light.shadowStrength = shadowStrength;
        }

        private static void CreateMouthBounce()
        {
            var item = new GameObject("R020MouthWarmNeutralBounce");
            item.transform.position = new Vector3(-0.018f, 0.090f, 0.092f);
            item.transform.LookAt(new Vector3(-0.012f, 0.052f, 0.036f));
            Light light = item.AddComponent<Light>();
            light.type = LightType.Spot;
            light.color = new Color(1f, 0.88f, 0.76f);
            light.intensity = 0.95f;
            light.range = 0.20f;
            light.spotAngle = 24f;
            light.shadows = LightShadows.None;
        }

        private static Transform BuildActualCase()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                CasePrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(CasePrefabPath);
            }

            var motion = new GameObject("SingleLivePremiumDisplayCaseR020");
            motion.transform.position = new Vector3(0f, 0.028f, 0.070f);
            motion.transform.localScale = Vector3.one * 0.80f;
            GameObject caseObject =
                PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (caseObject == null)
            {
                throw new InvalidOperationException(
                    "Could not instantiate the actual assembled case.");
            }
            caseObject.name = "ActualUnchangedPremiumDisplayCaseR020";
            caseObject.transform.SetParent(motion.transform, false);
            if (FindByName(caseObject.transform, "ContentSlot") == null)
            {
                throw new InvalidOperationException(
                    "The actual case has no caller-owned ContentSlot.");
            }
            return motion.transform;
        }

        private static (Transform, SkinnedMeshRenderer[]) BuildPack()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(RigPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(RigPath);
            }
            GameObject rig = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (rig == null)
            {
                throw new InvalidOperationException(
                    "Could not instantiate the R020 Pack-only FBX.");
            }
            rig.name = "Actual384x512FoilPouchR020";
            Transform root = rig.transform;
            root.position = Vector3.zero;
            root.localRotation = Quaternion.identity;
            root.localScale = Vector3.one;
            SkinnedMeshRenderer[] renderers = rig.GetComponentsInChildren<
                SkinnedMeshRenderer>(true)
                .OrderBy(item => item.name, StringComparer.Ordinal)
                .ToArray();
            if (renderers.Length != IsolatedR020ProofSequence.ExpectedRendererCount)
            {
                throw new InvalidOperationException(
                    $"R020 expects {IsolatedR020ProofSequence.ExpectedRendererCount} Pack renderers, got {renderers.Length}.");
            }

            Shader packShader = RequireShader(
                "FidgetingApp/Isolated/R020/MakeItShineCc0Pack");
            Shader contourShader = RequireShader(
                "FidgetingApp/Isolated/R020/MakeItShineCc0ContourSweep");
            Shader topSealShader = RequireShader(
                "FidgetingApp/Isolated/R020/TopSealTearClip");
            Shader litShader = RequireShader("Universal Render Pipeline/Lit");
            Texture2D body = RequireTexture(PackBodyPath);
            Texture2D flap = RequireTexture(PackFlapPath);
            Material printed = CreatePackMaterial(
                "R020Actual384x512PrintedFoil",
                packShader,
                body,
                new Color(0.78f, 0.78f, 0.75f, 1f));
            Material crimp = CreateTopSealMaterial(
                "R020AttachedPrintedCrimp",
                topSealShader,
                flap,
                new Color(0.50f, 0.49f, 0.46f, 1f));
            Material inner = CreateLitMaterial(
                "R020ReflectiveInnerFoil",
                litShader,
                null,
                new Color(0.38f, 0.40f, 0.42f, 1f),
                0.76f,
                0.38f,
                2470);
            Material rear = CreateLitMaterial(
                "R020RecessedCavity",
                litShader,
                null,
                new Color(0.023f, 0.027f, 0.032f, 1f),
                0.05f,
                0.78f,
                2470);
            Material lip = CreateLitMaterial(
                "R020FineRolledCrimpLip",
                litShader,
                null,
                new Color(0.16f, 0.13f, 0.095f, 1f),
                0.34f,
                0.44f,
                2480);
            Material releasedFront = CreateLitMaterial(
                "R020ReleasedSealFront",
                litShader,
                flap,
                new Color(0.42f, 0.38f, 0.30f, 1f),
                0.18f,
                0.56f,
                2490);
            Material releasedUnder = CreateLitMaterial(
                "R020ReleasedSealDarkUnderside",
                litShader,
                null,
                new Color(0.013f, 0.011f, 0.009f, 1f),
                0.08f,
                0.70f,
                2491);
            Material cutEdge = CreateLitMaterial(
                "R020FineFibrousTornEdge",
                litShader,
                null,
                new Color(0.24f, 0.17f, 0.11f, 1f),
                0.10f,
                0.76f,
                2492);
            var contour = new Material(contourShader)
            {
                name = "R020LocalizedWarmNeutralContourSweep",
                renderQueue = 3000
            };
            contour.SetColor(
                "_RimColor",
                new Color(1f, 0.78f, 0.54f, 0.65f));

            RequireRenderer(renderers, "Pack_FrontPrintedFoil").sharedMaterial =
                printed;
            RequireRenderer(renderers, "Pack_RearInnerFoil").sharedMaterial = rear;
            RequireRenderer(renderers, "Pack_TopSealRemaining").sharedMaterial =
                crimp;
            RequireRenderer(renderers, "Pack_InnerFoilMouth").sharedMaterial = inner;
            RequireRenderer(renderers, "Pack_InnerBackFoilRim").sharedMaterial =
                inner;
            RequireRenderer(renderers, "Pack_RolledCrimpLip").sharedMaterial = lip;
            RequireRenderer(
                renderers,
                "Pack_TornContourSweepCarrier").sharedMaterial = contour;
            RequireRenderer(renderers, "Pack_TearFrontSidewall").sharedMaterial =
                inner;
            RequireRenderer(renderers, "Pack_TabSidewall").sharedMaterial = inner;
            RequireRenderer(
                renderers,
                "Pack_ReleasedSealStrip").sharedMaterials = new[]
            {
                releasedFront,
                releasedUnder,
                cutEdge
            };
            RequireRenderer(renderers, "Pack_TopRightPullTab").sharedMaterials =
                new[]
                {
                    releasedFront,
                    releasedUnder,
                    cutEdge
                };
            foreach (SkinnedMeshRenderer renderer in renderers)
            {
                renderer.updateWhenOffscreen = true;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
            }
            return (root, renderers);
        }

        private static SkinnedMeshRenderer BuildR017MirrorControl()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                R017MirrorControlRigPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(R017MirrorControlRigPath);
            }
            GameObject control = PrefabUtility.InstantiatePrefab(prefab)
                as GameObject;
            if (control == null)
            {
                throw new InvalidOperationException(
                    "Could not instantiate the R017 mirror control.");
            }
            control.name = "R017MirrorOrientationControl";
            control.transform.SetPositionAndRotation(
                Vector3.zero,
                Quaternion.identity);
            control.transform.localScale = Vector3.one;
            SkinnedMeshRenderer front = control.GetComponentsInChildren<
                SkinnedMeshRenderer>(true).SingleOrDefault(
                    item => item.name == "Pack_FrontPrintedFoil");
            if (front == null)
            {
                throw new MissingReferenceException(
                    "R017 mirror control front foil is missing.");
            }
            control.SetActive(false);
            return front;
        }

        private static Material CreatePackMaterial(
            string name,
            Shader shader,
            Texture texture,
            Color color)
        {
            var material = new Material(shader)
            {
                name = name,
                renderQueue = 2460
            };
            material.SetTexture("_BaseMap", texture);
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Dissolve", 0f);
            material.SetFloat("_EdgeWidth", 0.018f);
            material.SetColor("_EdgeColor", new Color(1f, 0.78f, 0.54f, 1f));
            material.SetFloat("_EdgeStrength", 0.075f);
            return material;
        }

        private static Material CreateTopSealMaterial(
            string name,
            Shader shader,
            Texture texture,
            Color color)
        {
            var material = new Material(shader)
            {
                name = name,
                renderQueue = 2460
            };
            material.SetTexture("_BaseMap", texture);
            material.SetColor("_BaseColor", color);
            material.SetFloat("_TearFront", 0f);
            material.SetFloat("_Cutoff", 0.018f);
            return material;
        }

        private static Material CreateLitMaterial(
            string name,
            Shader shader,
            Texture texture,
            Color color,
            float metallic,
            float smoothness,
            int renderQueue)
        {
            var material = new Material(shader)
            {
                name = name,
                renderQueue = renderQueue
            };
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_Cull", 0f);
            if (texture != null)
            {
                material.SetTexture("_BaseMap", texture);
            }
            return material;
        }

        private static Shader RequireShader(string name)
        {
            Shader shader = Shader.Find(name);
            if (shader == null)
            {
                throw new MissingReferenceException(
                    $"Missing R020 shader: {name}");
            }
            return shader;
        }

        private static Texture2D RequireTexture(string path)
        {
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (texture == null)
            {
                throw new MissingReferenceException(
                    $"Missing R020 texture: {path}");
            }
            return texture;
        }

        private static SkinnedMeshRenderer RequireRenderer(
            IEnumerable<SkinnedMeshRenderer> renderers,
            string name)
        {
            SkinnedMeshRenderer renderer = renderers.SingleOrDefault(
                item => string.Equals(item.name, name, StringComparison.Ordinal));
            if (renderer == null
                || renderer.sharedMesh == null
                || renderer.sharedMesh.blendShapeCount
                    != IsolatedR020ProofSequence.ExpectedBlendShapeCount)
            {
                throw new MissingReferenceException(
                    $"Invalid R020 Pack renderer: {name}");
            }
            return renderer;
        }

        private static Transform FindByName(Transform root, string name)
        {
            if (root.name == name)
            {
                return root;
            }
            foreach (Transform child in root)
            {
                Transform found = FindByName(child, name);
                if (found != null)
                {
                    return found;
                }
            }
            return null;
        }

        private static string ProjectRoot =>
            Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

        private readonly struct SceneState
        {
            public SceneState(
                IsolatedR020Profile profile,
                Camera camera,
                Transform packRoot,
                SkinnedMeshRenderer[] packRenderers,
                Transform caseRoot,
                SkinnedMeshRenderer r017MirrorControlFront)
            {
                Profile = profile;
                Camera = camera;
                PackRoot = packRoot;
                PackRenderers = packRenderers;
                CaseRoot = caseRoot;
                R017MirrorControlFront = r017MirrorControlFront;
            }

            public IsolatedR020Profile Profile { get; }
            public Camera Camera { get; }
            public Transform PackRoot { get; }
            public SkinnedMeshRenderer[] PackRenderers { get; }
            public Transform CaseRoot { get; }
            public SkinnedMeshRenderer R017MirrorControlFront { get; }
        }
    }
}
