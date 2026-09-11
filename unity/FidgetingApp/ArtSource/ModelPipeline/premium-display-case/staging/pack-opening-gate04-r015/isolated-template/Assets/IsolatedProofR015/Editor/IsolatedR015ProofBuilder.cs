using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase.IsolatedCandidate.R015;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.IsolatedCandidate.R015.Editor
{
    public static class IsolatedR015ProofBuilder
    {
        private const string Root = "Assets/IsolatedProofR015";
        private const string Generated = Root + "/Generated";
        private const string ScenePath =
            Generated + "/PackOpeningGate04R015Isolated.unity";
        private const string ProfilePath =
            Generated + "/IsolatedR015Profile.asset";
        private const string FixedPipelinePath =
            "Assets/IsolatedProof/Generated/IsolatedR014URPFixed.asset";
        private const string FixedRendererPath =
            "Assets/IsolatedProof/Generated/IsolatedR014Renderer.asset";
        private const string RigPath =
            "Assets/Source/R015/PackOpeningGate04R015PackOnlyRig.fbx";
        private const string CasePrefabPath =
            "Assets/Source/PremiumDisplayCase/Prefabs/PresentationRoot.prefab";
        private const string PackBodyPath =
            "Assets/Source/Pack/gacha-pack-standard-body.png";
        private const string PackFlapPath =
            "Assets/Source/Pack/gacha-pack-standard-flap.png";
        private const string EnvironmentPath =
            "Assets/Source/Environment/canyon-unified-ledgestone-v1-2x.png";

        [MenuItem("Fidgeting/Isolated Candidate/R015 Build And Capture")]
        public static void BuildAndCapture()
        {
            SceneState state = BuildScene();
            string captureRoot = Path.Combine(
                Directory.GetParent(Application.dataPath).FullName,
                "Captures",
                "r015-orientation-polish");
            Directory.CreateDirectory(captureRoot);
            IsolatedR015ProofCapture.Run(
                state.Camera,
                state.Sequence,
                captureRoot,
                ScenePath);
            Debug.Log("R015_ISOLATED_CAPTURE_COMPLETE");
        }

        [MenuItem("Fidgeting/Isolated Candidate/R015 Build Scene")]
        public static void BuildSceneOnly()
        {
            BuildScene();
            Debug.Log("R015_ISOLATED_SCENE_BUILT");
        }

        internal static IsolatedR015ProofSequence BuildSequenceForTests()
        {
            return BuildScene().Sequence;
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
            IsolatedR015Profile profile = LoadOrCreateProfile();
            var sequence = new IsolatedR015ProofSequence(
                profile,
                camera,
                packRoot,
                renderers,
                caseRoot);
            sequence.InitializeSealedState();
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            return new SceneState(camera, sequence);
        }

        private static void AssertEngineAndSourceBoundary()
        {
            if (Application.unityVersion != "6000.5.6f1")
            {
                throw new InvalidOperationException(
                    $"R015 requires Unity 6000.5.6f1, got {Application.unityVersion}.");
            }
            UnityEditor.PackageManager.PackageInfo package =
                UnityEditor.PackageManager.PackageInfo.FindForAssetPath(
                "Packages/com.unity.render-pipelines.universal");
            if (package == null || package.version != "17.5.0")
            {
                throw new InvalidOperationException(
                    $"R015 requires URP 17.5.0, got {package?.version ?? "missing"}.");
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
                    "R015 requires the recovered R014 URP default renderer.");
            }
            GraphicsSettings.defaultRenderPipeline = pipeline;
            QualitySettings.renderPipeline = pipeline;

            foreach (string path in new[]
                     {
                         RigPath,
                         CasePrefabPath,
                         PackBodyPath,
                         PackFlapPath,
                         EnvironmentPath
                     })
            {
                if (!File.Exists(Path.Combine(ProjectRoot, path)))
                {
                    throw new FileNotFoundException(
                        "Missing isolated R015 source.",
                        path);
                }
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

        private static IsolatedR015Profile LoadOrCreateProfile()
        {
            IsolatedR015Profile profile =
                AssetDatabase.LoadAssetAtPath<IsolatedR015Profile>(ProfilePath);
            if (profile != null)
            {
                return profile;
            }
            profile = ScriptableObject.CreateInstance<IsolatedR015Profile>();
            AssetDatabase.CreateAsset(profile, ProfilePath);
            return profile;
        }

        private static Camera BuildCamera()
        {
            var item = new GameObject("IsolatedR015PortraitCamera")
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
                name = "R015StaticDarkMineralEnvironment"
            };
            material.SetTexture(
                "_BaseMap",
                AssetDatabase.LoadAssetAtPath<Texture2D>(EnvironmentPath));
            material.SetColor(
                "_BaseColor",
                new Color(0.31f, 0.33f, 0.32f, 1f));
            GameObject item = GameObject.CreatePrimitive(PrimitiveType.Quad);
            item.name = "R015StaticDarkMineralEnvironment";
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
                "R015NeutralKey",
                Quaternion.Euler(34f, -32f, 0f),
                new Color(1f, 0.90f, 0.78f),
                1.50f,
                0.35f);
            CreateLight(
                "R015MineralFill",
                Quaternion.Euler(54f, 148f, 0f),
                new Color(0.68f, 0.72f, 0.76f),
                0.52f,
                0.16f);
            CreateLight(
                "R015FoilEdge",
                Quaternion.Euler(18f, 210f, 0f),
                new Color(0.94f, 0.82f, 0.66f),
                0.50f,
                0.20f);
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

        private static Transform BuildActualCase()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                CasePrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(CasePrefabPath);
            }

            var motion = new GameObject("SingleLivePremiumDisplayCaseR015");
            motion.transform.position = new Vector3(0f, -0.030f, 0.070f);
            motion.transform.localScale = Vector3.one * 0.80f;
            GameObject caseObject =
                PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (caseObject == null)
            {
                throw new InvalidOperationException(
                    "Could not instantiate the actual assembled case.");
            }
            caseObject.name = "ActualUnchangedPremiumDisplayCaseR015";
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
                    "Could not instantiate the R015 Pack-only FBX.");
            }
            rig.name = "Actual384x512FoilPouchR015";
            Transform root = rig.transform;
            root.position = Vector3.zero;
            root.localRotation = Quaternion.identity;
            root.localScale = Vector3.one;
            SkinnedMeshRenderer[] renderers = rig.GetComponentsInChildren<
                SkinnedMeshRenderer>(true)
                .OrderBy(item => item.name, StringComparer.Ordinal)
                .ToArray();
            if (renderers.Length != IsolatedR015ProofSequence.ExpectedRendererCount)
            {
                throw new InvalidOperationException(
                    $"R015 expects {IsolatedR015ProofSequence.ExpectedRendererCount} Pack renderers, got {renderers.Length}.");
            }

            Shader packShader = RequireShader(
                "FidgetingApp/Isolated/R015/MakeItShineCc0Pack");
            Shader contourShader = RequireShader(
                "FidgetingApp/Isolated/R015/MakeItShineCc0ContourSweep");
            Shader litShader = RequireShader("Universal Render Pipeline/Lit");
            Texture2D body = RequireTexture(PackBodyPath);
            Texture2D flap = RequireTexture(PackFlapPath);
            Material printed = CreatePackMaterial(
                "R015Actual384x512PrintedFoil",
                packShader,
                body,
                new Color(0.78f, 0.78f, 0.75f, 1f));
            Material crimp = CreateLitMaterial(
                "R015AttachedPrintedCrimp",
                litShader,
                flap,
                new Color(0.50f, 0.49f, 0.46f, 1f),
                0.34f,
                0.46f,
                2460);
            Material inner = CreateLitMaterial(
                "R015ReflectiveInnerFoil",
                litShader,
                null,
                new Color(0.036f, 0.040f, 0.043f, 1f),
                0.64f,
                0.44f,
                2470);
            Material rear = CreateLitMaterial(
                "R015RearInnerFoil",
                litShader,
                null,
                new Color(0.070f, 0.073f, 0.075f, 1f),
                0.58f,
                0.48f,
                2470);
            Material lip = CreateLitMaterial(
                "R015FineRolledCrimpLip",
                litShader,
                null,
                new Color(0.14f, 0.11f, 0.080f, 1f),
                0.26f,
                0.50f,
                2480);
            Material releasedFront = CreateLitMaterial(
                "R015ReleasedSealFront",
                litShader,
                flap,
                new Color(0.42f, 0.38f, 0.30f, 1f),
                0.18f,
                0.56f,
                2490);
            Material releasedUnder = CreateLitMaterial(
                "R015ReleasedSealDarkUnderside",
                litShader,
                null,
                new Color(0.013f, 0.011f, 0.009f, 1f),
                0.08f,
                0.70f,
                2491);
            Material cutEdge = CreateLitMaterial(
                "R015FineFibrousTornEdge",
                litShader,
                null,
                new Color(0.24f, 0.17f, 0.11f, 1f),
                0.10f,
                0.76f,
                2492);
            var contour = new Material(contourShader)
            {
                name = "R015LocalizedWarmNeutralContourSweep",
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
                    $"Missing R015 shader: {name}");
            }
            return shader;
        }

        private static Texture2D RequireTexture(string path)
        {
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (texture == null)
            {
                throw new MissingReferenceException(
                    $"Missing R015 texture: {path}");
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
                    != IsolatedR015ProofSequence.ExpectedBlendShapeCount)
            {
                throw new MissingReferenceException(
                    $"Invalid R015 Pack renderer: {name}");
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
                Camera camera,
                IsolatedR015ProofSequence sequence)
            {
                Camera = camera;
                Sequence = sequence;
            }

            public Camera Camera { get; }
            public IsolatedR015ProofSequence Sequence { get; }
        }
    }
}
