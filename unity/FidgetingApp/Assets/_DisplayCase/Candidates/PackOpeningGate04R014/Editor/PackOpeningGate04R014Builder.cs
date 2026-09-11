using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.Product.Gacha;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Candidates.Editor
{
    public static class PackOpeningGate04R014Builder
    {
        public const string CandidateRoot =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R014";
        public const string ScenePath =
            CandidateRoot + "/Scenes/PackOpeningGate04R014.unity";
        public const string ProfilePath =
            CandidateRoot + "/Profiles/PackOpeningGate04R014Profile.asset";
        public const string RigPath =
            CandidateRoot + "/Imported/PackOpeningGate04R014PackOnlyRig.fbx";
        public const string StagingRoot =
            "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r014";
        public const string ProofRoot = StagingRoot + "/proof-initial";
        public const string PackBodyPath =
            "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png";
        public const string PackFlapPath =
            "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png";
        public const string ActualCasePrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab";
        public const string EnvironmentTexturePath =
            "Assets/Resources/EnvironmentBackgrounds/canyon-unified-ledgestone-v1-2x.png";
        public const string EnvironmentMaterialPath =
            "Assets/Resources/EnvironmentBackgrounds/EnvironmentParallaxMaterial.mat";

        private const string PackBodyHash =
            "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6";
        private const string PackFlapHash =
            "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49";
        private const string CasePrefabHash =
            "7a96aae6245b5a1d5463dabc3cb4518af8693ba8f8328ad9f2fe4ee6c6a67e2c";

        [MenuItem("Fidgeting/Display Case/Gate 04 R014/Build And Capture")]
        public static void BuildAndRunCapture()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                throw new InvalidOperationException(
                    "Unity is already entering or running PlayMode.");
            }

            BuildSceneInternal();
            Debug.Log(
                "GATE04_R014_PACK_ONLY_CAPTURE_READY "
                + $"scene={ScenePath} proof={ProofRoot}");
            EditorApplication.isPlaying = true;
        }

        [MenuItem("Fidgeting/Display Case/Gate 04 R014/Build Scene Only")]
        public static void BuildSceneOnly()
        {
            BuildSceneInternal();
            Debug.Log($"Gate 04 R014 Pack-only scene built at {ScenePath}.");
        }

        private static void BuildSceneInternal()
        {
            AssertEngineContract();
            EnsureDirectories();
            ConfigureRigImporter();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            AssertSourceAssets();
            PackOpeningGate04R014Profile profile = CreateProfile();
            MaterialSet materials = CreateMaterials();
            Scene scene = BuildScene(profile, materials);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            AssertSourceAssets();
        }

        private static void AssertEngineContract()
        {
            if (!string.Equals(
                    Application.unityVersion,
                    "6000.5.6f1",
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"R014 requires Unity 6000.5.6f1, got {Application.unityVersion}.");
            }

            UnityEditor.PackageManager.PackageInfo urp =
                UnityEditor.PackageManager.PackageInfo.FindForAssetPath(
                    "Packages/com.unity.render-pipelines.universal");
            if (urp == null || urp.version != "17.5.0")
            {
                throw new InvalidOperationException(
                    $"R014 requires URP 17.5.0, got {urp?.version ?? "missing"}.");
            }
        }

        private static void EnsureDirectories()
        {
            foreach (string directory in new[]
                     {
                         CandidateRoot + "/Scenes",
                         CandidateRoot + "/Profiles",
                         CandidateRoot + "/Generated/Materials",
                         ProofRoot,
                         ProofRoot + "/frames",
                         ProofRoot + "/frames-tear-quarter",
                         ProofRoot + "/frames-physical"
                     })
            {
                Directory.CreateDirectory(Path.Combine(ProjectRoot, directory));
            }
        }

        private static void ConfigureRigImporter()
        {
            string absolute = Path.Combine(ProjectRoot, RigPath);
            if (!File.Exists(absolute))
            {
                throw new FileNotFoundException(
                    "Build the R014 Pack-only Blender rig before Unity import.",
                    RigPath);
            }

            AssetDatabase.ImportAsset(
                RigPath,
                ImportAssetOptions.ForceSynchronousImport);
            ModelImporter importer = AssetImporter.GetAtPath(RigPath)
                as ModelImporter;
            if (importer == null)
            {
                throw new InvalidOperationException(
                    "The Pack-only FBX has no Unity ModelImporter.");
            }

            importer.importBlendShapes = true;
            importer.animationType = ModelImporterAnimationType.Generic;
            importer.importAnimation = false;
            AssetDatabase.WriteImportSettingsIfDirty(RigPath);
            AssetDatabase.ImportAsset(
                RigPath,
                ImportAssetOptions.ForceSynchronousImport);
        }

        private static void AssertSourceAssets()
        {
            AssertHash(PackBodyPath, PackBodyHash);
            AssertHash(PackFlapPath, PackFlapHash);
            AssertHash(ActualCasePrefabPath, CasePrefabHash);
            AssertPngDimensions(PackBodyPath, 384, 512);
            AssertPngDimensions(PackFlapPath, 384, 512);
            if (!File.Exists(Path.Combine(ProjectRoot, RigPath)))
            {
                throw new FileNotFoundException("Missing Pack-only rig.", RigPath);
            }
        }

        private static PackOpeningGate04R014Profile CreateProfile()
        {
            PackOpeningGate04R014Profile profile =
                AssetDatabase.LoadAssetAtPath<PackOpeningGate04R014Profile>(
                    ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<
                    PackOpeningGate04R014Profile>();
                AssetDatabase.CreateAsset(profile, ProfilePath);
            }
            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static MaterialSet CreateMaterials()
        {
            Shader lit = RequireShader("Universal Render Pipeline/Lit");
            Shader packShader = RequireShader(
                "FidgetingApp/Candidates/MakeItShineCc0PackR014");
            Shader sweepShader = RequireShader(
                "FidgetingApp/Candidates/MakeItShineCc0ContourSweepR014");
            Texture2D body = RequireTexture(PackBodyPath);
            Texture2D flap = RequireTexture(PackFlapPath);

            Material pack = CreateMaterial(
                "Gate04R014ActualPack",
                packShader,
                material =>
                {
                    material.SetTexture("_BaseMap", body);
                    material.SetColor(
                        "_BaseColor",
                        new Color(0.76f, 0.77f, 0.75f, 1f));
                    material.SetFloat("_Dissolve", 0f);
                    material.SetFloat("_EdgeWidth", 0.014f);
                    material.SetColor(
                        "_EdgeColor",
                        new Color(1f, 0.80f, 0.56f, 1f));
                    material.SetFloat("_EdgeStrength", 0.10f);
                    material.renderQueue = 2460;
                });
            Material topSeal = CreateMaterial(
                "Gate04R014ActualTopSeal",
                packShader,
                material =>
                {
                    material.SetTexture("_BaseMap", flap);
                    material.SetColor(
                        "_BaseColor",
                        new Color(0.58f, 0.57f, 0.54f, 1f));
                    material.SetFloat("_Dissolve", 0f);
                    material.SetFloat("_EdgeWidth", 0.014f);
                    material.SetColor(
                        "_EdgeColor",
                        new Color(0.92f, 0.74f, 0.50f, 1f));
                    material.SetFloat("_EdgeStrength", 0.06f);
                    material.renderQueue = 2461;
                });
            Material inner = CreateLitMaterial(
                "Gate04R014DarkInnerFoil",
                lit,
                new Color(0.012f, 0.010f, 0.009f, 1f),
                0.10f,
                0.62f,
                2470);
            Material backRim = CreateLitMaterial(
                "Gate04R014InnerBackFoilRim",
                lit,
                new Color(0.055f, 0.040f, 0.028f, 1f),
                0.14f,
                0.52f,
                2471);
            Material lip = CreateLitMaterial(
                "Gate04R014CrimpedContactLip",
                lit,
                new Color(0.12f, 0.082f, 0.050f, 1f),
                0.16f,
                0.54f,
                2480);
            Material stripFront = CreateLitTextureMaterial(
                "Gate04R014TornSealFront",
                lit,
                flap,
                new Color(0.36f, 0.32f, 0.26f, 1f),
                0.10f,
                0.62f,
                2490);
            Material stripUnder = CreateLitMaterial(
                "Gate04R014TornSealDarkUnderside",
                lit,
                new Color(0.010f, 0.008f, 0.006f, 1f),
                0.06f,
                0.70f,
                2490);
            Material cutEdge = CreateLitMaterial(
                "Gate04R014FibrousCutEdge",
                lit,
                new Color(0.16f, 0.105f, 0.060f, 1f),
                0.08f,
                0.78f,
                2490);
            Material contour = CreateMaterial(
                "Gate04R014Cc0TornContourSweep",
                sweepShader,
                material =>
                {
                    material.SetColor(
                        "_RimColor",
                        new Color(1f, 0.78f, 0.54f, 0.78f));
                    material.SetFloat("_SweepProgress", 0f);
                    material.SetFloat("_Intensity", 0f);
                    material.renderQueue = 3000;
                });
            return new MaterialSet(
                pack,
                topSeal,
                inner,
                backRim,
                lip,
                stripFront,
                stripUnder,
                cutEdge,
                contour,
                CreateEnvironmentMaterial());
        }

        private static Material CreateEnvironmentMaterial()
        {
            string path = CandidateRoot
                + "/Generated/Materials/Gate04R014DarkMineralEnvironment.mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material != null)
            {
                return material;
            }

            Material source = AssetDatabase.LoadAssetAtPath<Material>(
                EnvironmentMaterialPath);
            if (source == null)
            {
                throw new MissingReferenceException(
                    $"Missing {EnvironmentMaterialPath}");
            }
            material = new Material(source)
            {
                name = "Gate04R014DarkMineralEnvironment"
            };
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        private static Scene BuildScene(
            PackOpeningGate04R014Profile profile,
            MaterialSet materials)
        {
            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            Camera camera = BuildCamera();
            BuildEnvironment(materials.Environment);
            BuildLighting();
            PremiumDisplayCaseShippingPresentation presentation =
                BuildActualCase(out Transform caseMotionRoot);
            BuildPack(
                materials,
                out Transform packRoot,
                out SkinnedMeshRenderer[] packRenderers,
                out SkinnedMeshRenderer frontFoil,
                out SkinnedMeshRenderer topSeal,
                out SkinnedMeshRenderer innerMouth,
                out SkinnedMeshRenderer innerBackRim,
                out SkinnedMeshRenderer rolledCrimpLip,
                out SkinnedMeshRenderer tornContourRim,
                out SkinnedMeshRenderer tornSealStrip,
                out SkinnedMeshRenderer pullTab);

            var controllerObject = new GameObject(
                "PackOpeningGate04R014PackOnlyController");
            var controller =
                controllerObject.AddComponent<PackOpeningGate04R014Sequence>();
            controller.Configure(
                profile,
                camera,
                packRoot,
                packRenderers,
                frontFoil,
                topSeal,
                innerMouth,
                innerBackRim,
                rolledCrimpLip,
                tornContourRim,
                tornSealStrip,
                pullTab,
                caseMotionRoot,
                presentation);

            var captureObject = new GameObject("ActualUnityGameViewCaptureR014");
            var capture =
                captureObject.AddComponent<PackOpeningGate04R014Capture>();
            capture.Configure(
                camera,
                controller,
                Path.Combine(ProjectRoot, ProofRoot),
                ScenePath);
            Selection.activeGameObject = controllerObject;
            return scene;
        }

        private static Camera BuildCamera()
        {
            var item = new GameObject("Gate04R014ShippingPortraitCamera");
            item.tag = "MainCamera";
            Camera camera = item.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.003f, 0.004f, 0.005f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.fieldOfView = 27.0f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.transform.position = new Vector3(0f, -0.006f, -1.10f);
            camera.transform.LookAt(new Vector3(0f, -0.018f, 0.020f));
            return camera;
        }

        private static void BuildEnvironment(Material material)
        {
            GameObject item = GameObject.CreatePrimitive(PrimitiveType.Quad);
            item.name = "ActualShippingDarkMineralEnvironment";
            item.transform.position = new Vector3(0f, -0.020f, 1.45f);
            item.transform.localScale = new Vector3(0.90f, 1.52f, 1f);
            UnityEngine.Object.DestroyImmediate(item.GetComponent<Collider>());
            MeshRenderer renderer = item.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            material.SetTexture("_BaseMap", RequireTexture(EnvironmentTexturePath));
            material.SetColor(
                "_BaseColor",
                new Color(0.58f, 0.60f, 0.59f, 1f));
            material.SetFloat("_Saturation", 0.28f);
            material.SetFloat("_Opacity", 1f);
            material.SetFloat("_GlowEnabled", 0f);
            EditorUtility.SetDirty(material);
        }

        private static void BuildLighting()
        {
            CreateDirectionalLight(
                "PremiumNeutralKey",
                Quaternion.Euler(34f, -32f, 0f),
                new Color(1f, 0.90f, 0.78f),
                1.32f,
                0.36f);
            CreateDirectionalLight(
                "MineralSoftFill",
                Quaternion.Euler(54f, 148f, 0f),
                new Color(0.68f, 0.72f, 0.76f),
                0.42f,
                0.18f);
            CreateDirectionalLight(
                "FoilEdgeLight",
                Quaternion.Euler(18f, 210f, 0f),
                new Color(0.94f, 0.82f, 0.66f),
                0.46f,
                0.24f);
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.135f, 0.140f, 0.145f);
            RenderSettings.ambientEquatorColor =
                new Color(0.062f, 0.066f, 0.070f);
            RenderSettings.ambientGroundColor =
                new Color(0.016f, 0.016f, 0.015f);
            RenderSettings.reflectionIntensity = 0.48f;
        }

        private static PremiumDisplayCaseShippingPresentation BuildActualCase(
            out Transform caseMotionRoot)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                ActualCasePrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing {ActualCasePrefabPath}");
            }

            var motion = new GameObject("SingleLivePremiumDisplayCase");
            caseMotionRoot = motion.transform;
            caseMotionRoot.position = new Vector3(0f, -0.072f, 0.055f);
            caseMotionRoot.localScale = Vector3.one * 0.80f;
            GameObject caseObject =
                PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (caseObject == null)
            {
                throw new InvalidOperationException(
                    "Could not instantiate the real assembled case.");
            }
            caseObject.name = "ActualAssembledPremiumDisplayCase";
            caseObject.transform.SetParent(caseMotionRoot, false);
            PremiumDisplayCaseShippingPresentation presentation =
                caseObject.GetComponent<PremiumDisplayCaseShippingPresentation>();
            if (presentation == null || presentation.ContentSlot == null)
            {
                throw new MissingReferenceException(
                    "The real case must expose ContentSlot.");
            }

            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            prize.name = "CallerOwnedThreeBladeContent";
            presentation.AttachContent(
                prize.transform,
                PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
            presentation.SetTimeForPreview(
                presentation.RevealProfile.TotalDurationSeconds);
            return presentation;
        }

        private static void BuildPack(
            MaterialSet materials,
            out Transform packRoot,
            out SkinnedMeshRenderer[] renderers,
            out SkinnedMeshRenderer frontFoil,
            out SkinnedMeshRenderer topSeal,
            out SkinnedMeshRenderer innerMouth,
            out SkinnedMeshRenderer innerBackRim,
            out SkinnedMeshRenderer rolledCrimpLip,
            out SkinnedMeshRenderer tornContourRim,
            out SkinnedMeshRenderer tornSealStrip,
            out SkinnedMeshRenderer pullTab)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(RigPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing imported Pack-only rig {RigPath}");
            }
            GameObject rig = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (rig == null)
            {
                throw new InvalidOperationException("Could not instantiate the Pack-only rig.");
            }

            rig.name = "ActualAuthoredStandardPackOnlyRig";
            packRoot = rig.transform;
            packRoot.position = Vector3.zero;
            packRoot.localRotation = Quaternion.identity;
            packRoot.localScale = Vector3.one;
            renderers = rig.GetComponentsInChildren<SkinnedMeshRenderer>(true)
                .OrderBy(item => item.name, StringComparer.Ordinal)
                .ToArray();
            if (renderers.Length != 10)
            {
                throw new InvalidOperationException(
                    $"Expected 10 Pack-only rig renderers, got {renderers.Length}.");
            }

            frontFoil = RequireRenderer(renderers, "Pack_FrontFoil");
            topSeal = RequireRenderer(renderers, "Pack_TopSealRemaining");
            innerMouth = RequireRenderer(renderers, "Pack_InnerFoilMouth");
            innerBackRim = RequireRenderer(renderers, "Pack_InnerBackFoilRim");
            rolledCrimpLip = RequireRenderer(renderers, "Pack_RolledCrimpLip");
            tornContourRim = RequireRenderer(renderers, "Pack_TornContourRim");
            tornSealStrip = RequireRenderer(renderers, "Pack_TornSealStrip");
            pullTab = RequireRenderer(renderers, "Pack_TopRightPullTab");
            SkinnedMeshRenderer leading = RequireRenderer(
                renderers,
                "Pack_TearLeadingSidewall");
            SkinnedMeshRenderer tabWall = RequireRenderer(
                renderers,
                "Pack_TabSidewall");

            frontFoil.sharedMaterial = materials.Pack;
            topSeal.sharedMaterial = materials.TopSeal;
            innerMouth.sharedMaterial = materials.Inner;
            innerBackRim.sharedMaterial = materials.InnerBackRim;
            rolledCrimpLip.sharedMaterial = materials.Lip;
            tornContourRim.sharedMaterial = materials.Contour;
            leading.sharedMaterial = materials.Inner;
            tabWall.sharedMaterial = materials.Inner;
            tornSealStrip.sharedMaterials = new[]
            {
                materials.StripFront,
                materials.StripUnderside,
                materials.CutEdge
            };
            pullTab.sharedMaterials = new[]
            {
                materials.StripFront,
                materials.StripUnderside,
                materials.CutEdge
            };
            foreach (SkinnedMeshRenderer renderer in renderers)
            {
                renderer.updateWhenOffscreen = true;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
            }
        }

        private static SkinnedMeshRenderer RequireRenderer(
            IEnumerable<SkinnedMeshRenderer> renderers,
            string name)
        {
            SkinnedMeshRenderer renderer = renderers.SingleOrDefault(
                item => string.Equals(item.name, name, StringComparison.Ordinal));
            if (renderer == null || renderer.sharedMesh == null
                || renderer.sharedMesh.blendShapeCount != 6)
            {
                throw new MissingReferenceException(
                    $"Invalid R014 Pack-only rig renderer: {name}");
            }
            return renderer;
        }

        private static Shader RequireShader(string name)
        {
            Shader shader = Shader.Find(name);
            if (shader == null)
            {
                throw new MissingReferenceException($"Missing shader: {name}");
            }
            return shader;
        }

        private static Texture2D RequireTexture(string path)
        {
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (texture == null)
            {
                AssetDatabase.ImportAsset(
                    path,
                    ImportAssetOptions.ForceSynchronousImport);
                texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            }
            if (texture == null)
            {
                throw new MissingReferenceException($"Missing texture: {path}");
            }
            return texture;
        }

        private static Material CreateMaterial(
            string name,
            Shader shader,
            Action<Material> configure)
        {
            string path = CandidateRoot + "/Generated/Materials/" + name + ".mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = name };
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            configure(material);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateLitMaterial(
            string name,
            Shader shader,
            Color color,
            float metallic,
            float smoothness,
            int renderQueue)
        {
            return CreateMaterial(
                name,
                shader,
                material =>
                {
                    material.SetColor("_BaseColor", color);
                    material.SetFloat("_Metallic", metallic);
                    material.SetFloat("_Smoothness", smoothness);
                    material.SetFloat("_Cull", 0f);
                    material.renderQueue = renderQueue;
                });
        }

        private static Material CreateLitTextureMaterial(
            string name,
            Shader shader,
            Texture texture,
            Color color,
            float metallic,
            float smoothness,
            int renderQueue)
        {
            return CreateMaterial(
                name,
                shader,
                material =>
                {
                    material.SetTexture("_BaseMap", texture);
                    material.SetColor("_BaseColor", color);
                    material.SetFloat("_Metallic", metallic);
                    material.SetFloat("_Smoothness", smoothness);
                    material.SetFloat("_Cull", 0f);
                    material.renderQueue = renderQueue;
                });
        }

        private static void CreateDirectionalLight(
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

        private static void AssertHash(string assetPath, string expected)
        {
            string absolute = Path.Combine(ProjectRoot, assetPath);
            if (!File.Exists(absolute))
            {
                throw new FileNotFoundException($"Missing source: {assetPath}");
            }
            using SHA256 hash = SHA256.Create();
            using FileStream stream = File.OpenRead(absolute);
            string actual = string.Concat(hash.ComputeHash(stream).Select(
                value => value.ToString("x2", CultureInfo.InvariantCulture)));
            if (!string.Equals(actual, expected, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(
                    $"{assetPath} expected {expected}, got {actual}.");
            }
        }

        private static void AssertPngDimensions(
            string assetPath,
            int expectedWidth,
            int expectedHeight)
        {
            byte[] header = new byte[24];
            using FileStream stream = File.OpenRead(
                Path.Combine(ProjectRoot, assetPath));
            if (stream.Read(header, 0, header.Length) != header.Length)
            {
                throw new InvalidDataException($"Invalid PNG: {assetPath}");
            }
            int width = header[16] << 24
                | header[17] << 16
                | header[18] << 8
                | header[19];
            int height = header[20] << 24
                | header[21] << 16
                | header[22] << 8
                | header[23];
            if (width != expectedWidth || height != expectedHeight)
            {
                throw new InvalidOperationException(
                    $"{assetPath} expected {expectedWidth}x{expectedHeight}, got {width}x{height}.");
            }
        }

        private static string ProjectRoot =>
            Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

        private readonly struct MaterialSet
        {
            public MaterialSet(
                Material pack,
                Material topSeal,
                Material inner,
                Material innerBackRim,
                Material lip,
                Material stripFront,
                Material stripUnderside,
                Material cutEdge,
                Material contour,
                Material environment)
            {
                Pack = pack;
                TopSeal = topSeal;
                Inner = inner;
                InnerBackRim = innerBackRim;
                Lip = lip;
                StripFront = stripFront;
                StripUnderside = stripUnderside;
                CutEdge = cutEdge;
                Contour = contour;
                Environment = environment;
            }

            public Material Pack { get; }
            public Material TopSeal { get; }
            public Material Inner { get; }
            public Material InnerBackRim { get; }
            public Material Lip { get; }
            public Material StripFront { get; }
            public Material StripUnderside { get; }
            public Material CutEdge { get; }
            public Material Contour { get; }
            public Material Environment { get; }
        }
    }
}
