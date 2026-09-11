using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using FidgetingApp.Product.Gacha;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Candidates.Editor
{
    public static class PackOpeningGate04R012Builder
    {
        public const string CandidateRoot =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R012";
        public const string ScenePath =
            CandidateRoot + "/Scenes/PackOpeningGate04R012.unity";
        public const string ProfilePath =
            CandidateRoot + "/Profiles/PackOpeningGate04R012Profile.asset";
        public const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-012";
        public const string PackBodyPath =
            "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png";
        public const string PackFlapPath =
            "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png";
        public const string ActualCasePrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab";
        public const string ActualPrizePrefabPath =
            "Assets/Resources/Gacha/ThreeBladeDisplayPrize.prefab";
        public const string EnvironmentTexturePath =
            "Assets/Resources/EnvironmentBackgrounds/canyon-unified-ledgestone-v1-2x.png";
        public const string EnvironmentMaterialPath =
            "Assets/Resources/EnvironmentBackgrounds/EnvironmentParallaxMaterial.mat";

        public const string SourceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-011/source-raw";
        public const string SourceImportedRoot =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R011/ImportedSource";
        public const string ImportedSourceRoot = CandidateRoot + "/ImportedSource";

        private const string MaterialRoot = CandidateRoot + "/Generated/Materials";
        private const string SourceTimelineHash =
            "baec0abcf084db64a2b353947a9e67408e6b41ec27d5c645621d8f93aec9b086";
        private const string SourceDiscardHash =
            "be661fe81b095f7f1ad08fb2a1c003b15f8690ee08d43f9f705dc849924fb2c6";
        private const string SourceBoosterHash =
            "e1de0669f3f7c8ade21f656ab17c5e14e6d45cd5e689c79ddb983f27e61f6c34";
        private const string SourceTitleHash =
            "6a7718d6ae1eba360c03a1ea16b207ada5ae80f1a4dc2df0d004453bf94e2067";
        private const string SourceLightingHash =
            "a4eb3922e72a3dadb436902d2c4a57c3fbd6768e4b137104abeed6167e1f4f7d";
        private const string SourceFlareHash =
            "bbf7c86f5435ec3097717ef092e531214916e9cbb7db2b71f059e3d12f90ffa3";
        private const string SourceNoiseHash =
            "2303e1fb3c86af9e9b6a4ccd4ecb615b9cdd172253eea8988c7a6ac4a165e886";
        private const string SourceActivationHash =
            "c56ed7a46cc1276b16e5e6e47879e4c7a665425df9d8e2e6693ac8ef1924ff67";
        private const string SourceStrikeVfxHash =
            "4f4da1d0038cee4e4599467b754a429263286073233bb8ac0f259e908635d7b5";
        private const string SourceExplosionHash =
            "d6af66e7b91e7097d50fbef376bf7b33b63dd9e6738a4c99084cb46460aaac2f";
        private const string PackBodyHash =
            "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6";
        private const string PackFlapHash =
            "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49";
        private const string CasePrefabHash =
            "7a96aae6245b5a1d5463dabc3cb4518af8693ba8f8328ad9f2fe4ee6c6a67e2c";
        private const string PrizePrefabHash =
            "d68f51b0034199987fa9e0cd44a8e3ba351b70b4289ff4773edc296e9395a8e1";

        [MenuItem("Fidgeting/Display Case/Gate 04 R012/Build And Capture")]
        public static void BuildAndRunCapture()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                throw new InvalidOperationException(
                    "Unity is already entering or running PlayMode.");
            }
            BuildSceneInternal();
            Debug.Log(
                "GATE04_R012_PHYSICAL_TEAR_CAPTURE_READY "
                + $"scene={ScenePath} evidence={EvidenceRoot}");
            EditorApplication.isPlaying = true;
        }

        [MenuItem("Fidgeting/Display Case/Gate 04 R012/Build Scene Only")]
        public static void BuildSceneOnly()
        {
            BuildSceneInternal();
            Debug.Log($"Gate 04 rev 12 candidate scene built at {ScenePath}.");
        }

        private static void BuildSceneInternal()
        {
            AssertEngineContract();
            EnsureDirectories();
            CopyDirectSources();
            CopySourceReferenceFrames();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            AssertSourceAssets();
            PackOpeningGate04R012Profile profile = CreateProfile();
            MaterialSet materials = CreateMaterials();
            Scene scene = BuildScene(profile, materials);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            AssertSourceAssets();
            WriteSourceMapping();
            WriteSourceManifest();
        }

        private static void AssertEngineContract()
        {
            if (!string.Equals(
                    Application.unityVersion,
                    "6000.5.6f1",
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"Gate 04 rev 12 requires Unity 6000.5.6f1, got {Application.unityVersion}.");
            }
            UnityEditor.PackageManager.PackageInfo urp =
                UnityEditor.PackageManager.PackageInfo.FindForAssetPath(
                    "Packages/com.unity.render-pipelines.universal");
            if (urp == null || urp.version != "17.5.0")
            {
                throw new InvalidOperationException(
                    $"Gate 04 rev 12 requires URP 17.5.0, got {urp?.version ?? "missing"}.");
            }
        }

        private static void EnsureDirectories()
        {
            foreach (string directory in new[]
                     {
                         CandidateRoot + "/Scenes",
                         CandidateRoot + "/Profiles",
                         CandidateRoot + "/Generated/Materials",
                         CandidateRoot + "/ImportedSource/Animation",
                         CandidateRoot + "/ImportedSource/Textures",
                         EvidenceRoot,
                         EvidenceRoot + "/source-raw",
                         EvidenceRoot + "/source-reference",
                         EvidenceRoot + "/frames",
                         EvidenceRoot + "/frames-tear-quarter",
                         EvidenceRoot + "/frames-impact-quarter"
                     })
            {
                Directory.CreateDirectory(Path.Combine(ProjectRoot, directory));
            }
        }

        private static void CopyDirectSources()
        {
            CopyExact(
                SourceImportedRoot + "/Animation/Booster_Discarded.anim",
                ImportedSourceRoot + "/Animation/Booster_Discarded.anim",
                SourceDiscardHash);
            CopyExact(
                SourceImportedRoot + "/Textures/TX_Flare_2x2_M.png",
                ImportedSourceRoot + "/Textures/TX_Flare_2x2_M.png",
                SourceFlareHash);
            CopyExact(
                SourceImportedRoot + "/Textures/TX_Noise_M.tga",
                ImportedSourceRoot + "/Textures/TX_Noise_M.tga",
                SourceNoiseHash);
            CopyExact(
                SourceRoot + "/Booster to Card Timeline.playable",
                EvidenceRoot + "/source-raw/Booster to Card Timeline.playable",
                SourceTimelineHash);
            CopyExact(
                SourceRoot + "/SG_BoosterPack.shadergraph",
                EvidenceRoot + "/source-raw/SG_BoosterPack.shadergraph",
                SourceBoosterHash);
            CopyExact(
                SourceRoot + "/SG_Title_Kyle.shadergraph",
                EvidenceRoot + "/source-raw/SG_Title_Kyle.shadergraph",
                SourceTitleHash);
            CopyExact(
                SourceRoot + "/SG_LightingStrike.shadergraph",
                EvidenceRoot + "/source-raw/SG_LightingStrike.shadergraph",
                SourceLightingHash);
            CopyExact(
                SourceRoot + "/VFX_BoosterActivation.vfx",
                EvidenceRoot + "/source-raw/VFX_BoosterActivation.vfx",
                SourceActivationHash);
            CopyExact(
                SourceRoot + "/VFXG_LightingStrike.vfx",
                EvidenceRoot + "/source-raw/VFXG_LightingStrike.vfx",
                SourceStrikeVfxHash);
            CopyExact(
                SourceRoot + "/VFX_BoosterExplosion.vfx",
                EvidenceRoot + "/source-raw/VFX_BoosterExplosion.vfx",
                SourceExplosionHash);
        }

        private static void CopySourceReferenceFrames()
        {
            string sourceRoot = Path.Combine(
                ProjectRoot,
                "..",
                "..",
                "..",
                "Fidgeting app External Research",
                "Unite2025-MakeItShine-Unity65-Study",
                "FidgetingStudyCaptures",
                "MatchedEffect");
            string destinationRoot = Path.Combine(
                ProjectRoot,
                EvidenceRoot,
                "source-reference");
            foreach (string name in new[]
                     {
                         "source-05.800s.png",
                         "source-05.950s.png",
                         "source-06.150s.png",
                         "source-06.450s.png",
                         "source-06.740s.png",
                         "source-07.000s.png",
                         "source-capture-report.json"
                     })
            {
                string source = Path.Combine(sourceRoot, name);
                if (!File.Exists(source))
                {
                    throw new FileNotFoundException(
                        $"Missing real CC0 source capture: {source}");
                }
                File.Copy(source, Path.Combine(destinationRoot, name), true);
            }
        }

        private static void AssertSourceAssets()
        {
            AssertHash(PackBodyPath, PackBodyHash);
            AssertHash(PackFlapPath, PackFlapHash);
            AssertHash(ActualCasePrefabPath, CasePrefabHash);
            AssertHash(ActualPrizePrefabPath, PrizePrefabHash);
            AssertHash(
                ImportedSourceRoot + "/Animation/Booster_Discarded.anim",
                SourceDiscardHash);
            AssertHash(
                ImportedSourceRoot + "/Textures/TX_Flare_2x2_M.png",
                SourceFlareHash);
            AssertHash(
                ImportedSourceRoot + "/Textures/TX_Noise_M.tga",
                SourceNoiseHash);
            AssertHash(
                EvidenceRoot + "/source-raw/Booster to Card Timeline.playable",
                SourceTimelineHash);
            AssertHash(
                EvidenceRoot + "/source-raw/SG_BoosterPack.shadergraph",
                SourceBoosterHash);
            AssertHash(
                EvidenceRoot + "/source-raw/SG_Title_Kyle.shadergraph",
                SourceTitleHash);
            AssertHash(
                EvidenceRoot + "/source-raw/SG_LightingStrike.shadergraph",
                SourceLightingHash);
            AssertHash(
                EvidenceRoot + "/source-raw/VFX_BoosterActivation.vfx",
                SourceActivationHash);
            AssertHash(
                EvidenceRoot + "/source-raw/VFXG_LightingStrike.vfx",
                SourceStrikeVfxHash);
            AssertHash(
                EvidenceRoot + "/source-raw/VFX_BoosterExplosion.vfx",
                SourceExplosionHash);
            AssertPngDimensions(PackBodyPath, 384, 512);
            AssertPngDimensions(PackFlapPath, 384, 512);
        }

        private static PackOpeningGate04R012Profile CreateProfile()
        {
            PackOpeningGate04R012Profile profile =
                AssetDatabase.LoadAssetAtPath<PackOpeningGate04R012Profile>(
                    ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<
                    PackOpeningGate04R012Profile>();
                AssetDatabase.CreateAsset(profile, ProfilePath);
            }
            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static MaterialSet CreateMaterials()
        {
            Shader lit = RequireShader("Universal Render Pipeline/Lit");
            Shader packShader = RequireShader(
                "FidgetingApp/Candidates/MakeItShineCc0PackR012");
            Shader sourceShader = RequireShader(
                "FidgetingApp/Candidates/MakeItShineCc0PortR012");
            Texture2D body = RequireTexture(PackBodyPath);
            Texture2D flap = RequireTexture(PackFlapPath);
            Texture2D flare = RequireTexture(
                ImportedSourceRoot + "/Textures/TX_Flare_2x2_M.png");
            Texture2D noise = RequireTexture(
                ImportedSourceRoot + "/Textures/TX_Noise_M.tga");

            Material pack = CreateMaterial(
                "Gate04R012RealPackContourDiscard",
                packShader,
                material =>
                {
                    material.SetTexture("_BaseMap", body);
                    material.SetTexture("_NoiseMap", noise);
                    material.SetColor("_BaseColor", Color.white);
                    material.SetFloat("_Dissolve", 0f);
                    material.SetFloat("_EdgeWidth", 0.012f);
                    material.SetColor(
                        "_EdgeColor",
                        new Color(1f, 0.94f, 0.82f, 1f));
                    material.SetFloat("_EdgeStrength", 0.50f);
                    material.SetFloat("_TearSweep", 0f);
                    material.SetFloat("_TearEdgeWidth", 0.048f);
                    material.SetColor(
                        "_TearEdgeColor",
                        new Color(0.94f, 0.82f, 0.62f, 1f));
                    material.SetFloat("_TearEdgeStrength", 0.34f);
                    material.renderQueue = 2460;
                });
            Material rearRim = CreateMaterial(
                "Gate04R012RearFoilRim",
                lit,
                material => ConfigureLitTexture(
                    material,
                    flap,
                    new Color(0.48f, 0.45f, 0.41f, 1f),
                    0.25f,
                    0.28f,
                    2470));
            Material stripFront = CreateMaterial(
                "Gate04R012TornSealFront",
                lit,
                material => ConfigureLitTexture(
                    material,
                    flap,
                    new Color(0.72f, 0.67f, 0.59f, 1f),
                    0.30f,
                    0.31f,
                    2475));
            Material stripUnder = CreateLitMaterial(
                "Gate04R012TornSealDarkUnderside",
                lit,
                new Color(0.022f, 0.020f, 0.018f, 1f),
                0.12f,
                0.18f,
                2475);
            Material stripEdge = CreateLitMaterial(
                "Gate04R012TornSealCutEdge",
                lit,
                new Color(0.13f, 0.112f, 0.090f, 1f),
                0.18f,
                0.22f,
                2475);
            Material cavity = CreateLitMaterial(
                "Gate04R012InnerFoilWalls",
                lit,
                new Color(0.026f, 0.024f, 0.022f, 1f),
                0.18f,
                0.22f,
                2000);
            Material contact = CreateLitMaterial(
                "Gate04R012InnerFoilContact",
                lit,
                new Color(0.004f, 0.004f, 0.003f, 1f),
                0.08f,
                0.10f,
                2000);
            Material sweep = CreateMaterial(
                "Gate04R012Cc0FlareSweep",
                sourceShader,
                material =>
                {
                    material.SetTexture("_BaseMap", flare);
                    material.SetTextureScale("_BaseMap", new Vector2(0.5f, 0.5f));
                    material.SetTextureOffset("_BaseMap", new Vector2(0.5f, 0f));
                    material.SetColor(
                        "_BaseColor",
                        new Color(1f, 0.79f, 0.58f, 0.43f));
                    material.SetFloat("_Reveal", 1f);
                    material.SetFloat("_Erode", 0.018f);
                    material.SetFloat("_Intensity", 1.15f);
                    material.renderQueue = 3020;
                });
            Material strike = CreateMaterial(
                "Gate04R012Cc0LightingStrike",
                sourceShader,
                material =>
                {
                    material.SetTexture("_BaseMap", flare);
                    material.SetTextureScale("_BaseMap", new Vector2(0.5f, 0.5f));
                    material.SetTextureOffset("_BaseMap", new Vector2(0.5f, 0f));
                    material.SetColor(
                        "_BaseColor",
                        new Color(0.72f, 0.84f, 1f, 0.24f));
                    material.SetFloat("_Reveal", 1f);
                    material.SetFloat("_Erode", 0.024f);
                    material.SetFloat("_Intensity", 0.92f);
                    material.renderQueue = 3020;
                });
            Material environment = CreateEnvironmentMaterial();
            return new MaterialSet(
                pack,
                rearRim,
                stripFront,
                stripUnder,
                stripEdge,
                cavity,
                contact,
                sweep,
                strike,
                environment);
        }

        private static Material CreateEnvironmentMaterial()
        {
            string path = MaterialRoot + "/Gate04R012DarkMineralEnvironment.mat";
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
                name = "Gate04R012DarkMineralEnvironment"
            };
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        private static Scene BuildScene(
            PackOpeningGate04R012Profile profile,
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
                out MeshFilter frontFilter,
                out Renderer frontRenderer,
                out MeshFilter sealedBackFilter,
                out Renderer sealedBackRenderer,
                out MeshFilter rearRimFilter,
                out Renderer rearRimRenderer,
                out MeshFilter stripFilter,
                out Renderer stripRenderer,
                out MeshFilter cavityFilter,
                out Renderer cavityRenderer,
                out Transform pullTab,
                out Renderer pullTabRenderer);
            SourceEffects sourceEffects = BuildSourceEffects(
                packRoot,
                materials.Sweep,
                materials.Strike);

            var controllerObject = new GameObject(
                "PackOpeningGate04R012PhysicalTearController");
            var controller =
                controllerObject.AddComponent<PackOpeningGate04R012Sequence>();
            controller.Configure(
                profile,
                camera,
                packRoot,
                frontFilter,
                frontRenderer,
                sealedBackFilter,
                sealedBackRenderer,
                rearRimFilter,
                rearRimRenderer,
                stripFilter,
                stripRenderer,
                cavityFilter,
                cavityRenderer,
                pullTab,
                pullTabRenderer,
                caseMotionRoot,
                presentation,
                sourceEffects.Root,
                sourceEffects.Systems);

            var captureObject = new GameObject("RealUnityPlayModeCaptureR012");
            var capture =
                captureObject.AddComponent<PackOpeningGate04R012Capture>();
            capture.Configure(
                camera,
                controller,
                Path.Combine(ProjectRoot, EvidenceRoot),
                ScenePath);
            Selection.activeGameObject = controllerObject;
            return scene;
        }

        private static Camera BuildCamera()
        {
            var item = new GameObject("Gate04R012ShippingPortraitCamera");
            item.tag = "MainCamera";
            Camera camera = item.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.003f, 0.004f, 0.005f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.fieldOfView = 30.5f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.transform.position = new Vector3(0f, 0.004f, -1.35f);
            camera.transform.LookAt(new Vector3(0f, -0.006f, -0.04f));
            return camera;
        }

        private static void BuildEnvironment(Material material)
        {
            GameObject item = GameObject.CreatePrimitive(PrimitiveType.Quad);
            item.name = "ActualShippingDarkMineralEnvironment";
            item.transform.position = new Vector3(0f, -0.025f, 1.45f);
            item.transform.localScale = new Vector3(1.04f, 1.84f, 1f);
            UnityEngine.Object.DestroyImmediate(item.GetComponent<Collider>());
            MeshRenderer renderer = item.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            material.SetTexture(
                "_BaseMap",
                RequireTexture(EnvironmentTexturePath));
            material.SetColor(
                "_BaseColor",
                new Color(0.72f, 0.74f, 0.72f, 1f));
            material.SetFloat("_Saturation", 0.44f);
            material.SetFloat("_Opacity", 1f);
            material.SetFloat("_GlowEnabled", 0f);
            EditorUtility.SetDirty(material);
        }

        private static void BuildLighting()
        {
            CreateDirectionalLight(
                "PremiumNeutralKey",
                Quaternion.Euler(32f, -28f, 0f),
                new Color(1f, 0.93f, 0.84f),
                2.45f,
                0.42f);
            CreateDirectionalLight(
                "CoolMineralFill",
                Quaternion.Euler(56f, 145f, 0f),
                new Color(0.64f, 0.71f, 0.78f),
                0.88f,
                0.24f);
            CreateDirectionalLight(
                "ControlledMetalRim",
                Quaternion.Euler(18f, 212f, 0f),
                new Color(0.94f, 0.90f, 0.82f),
                1.18f,
                0.30f);
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.290f, 0.305f, 0.320f);
            RenderSettings.ambientEquatorColor =
                new Color(0.175f, 0.182f, 0.188f);
            RenderSettings.ambientGroundColor =
                new Color(0.062f, 0.062f, 0.058f);
            RenderSettings.reflectionIntensity = 0.74f;
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
            var motion = new GameObject("SingleConstantScalePremiumDisplayCase");
            caseMotionRoot = motion.transform;
            caseMotionRoot.position = new Vector3(0f, 0.002f, 0.060f);
            caseMotionRoot.localScale = Vector3.one
                * PackOpeningGate04R012Sequence.CaseScale;
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
            presentation.SetLabel(BuildAuthoritativeReviewLabel());
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
            out MeshFilter frontFilter,
            out Renderer frontRenderer,
            out MeshFilter sealedBackFilter,
            out Renderer sealedBackRenderer,
            out MeshFilter rearRimFilter,
            out Renderer rearRimRenderer,
            out MeshFilter stripFilter,
            out Renderer stripRenderer,
            out MeshFilter cavityFilter,
            out Renderer cavityRenderer,
            out Transform pullTab,
            out Renderer pullTabRenderer)
        {
            var root = new GameObject("ActualAuthoredStandardPackPhysicalLayers");
            packRoot = root.transform;
            packRoot.position = new Vector3(0f, 0.015f, -0.180f);
            GameObject front = CreateDynamicMeshObject(
                packRoot,
                "FineSegmentFrontPackLayer",
                materials.Pack);
            frontFilter = front.GetComponent<MeshFilter>();
            frontRenderer = front.GetComponent<MeshRenderer>();
            GameObject back = CreateDynamicMeshObject(
                packRoot,
                "CoincidentSealedBackPackLayer",
                materials.Pack);
            sealedBackFilter = back.GetComponent<MeshFilter>();
            sealedBackRenderer = back.GetComponent<MeshRenderer>();
            GameObject rear = CreateDynamicMeshObject(
                packRoot,
                "SeparatedRearFoilRim",
                materials.RearRim);
            rearRimFilter = rear.GetComponent<MeshFilter>();
            rearRimRenderer = rear.GetComponent<MeshRenderer>();
            GameObject strip = CreateDynamicMeshObject(
                packRoot,
                "CurledNarrowTornSealStrip",
                materials.StripFront);
            stripFilter = strip.GetComponent<MeshFilter>();
            stripRenderer = strip.GetComponent<MeshRenderer>();
            stripRenderer.sharedMaterials = new[]
            {
                materials.StripFront,
                materials.StripUnder,
                materials.StripEdge
            };
            GameObject cavity = CreateDynamicMeshObject(
                packRoot,
                "DeepInnerFoilMouth",
                materials.Cavity);
            cavityFilter = cavity.GetComponent<MeshFilter>();
            cavityRenderer = cavity.GetComponent<MeshRenderer>();
            cavityRenderer.sharedMaterials = new[]
            {
                materials.Cavity,
                materials.Contact
            };
            GameObject tab = CreatePullTab(
                packRoot,
                materials.StripFront,
                materials.StripUnder,
                materials.StripEdge);
            pullTab = tab.transform;
            pullTabRenderer = tab.GetComponent<MeshRenderer>();
        }

        private static GameObject CreatePullTab(
            Transform parent,
            Material front,
            Material underside,
            Material edge)
        {
            var item = new GameObject("LocalizedTopRightPullTab");
            item.transform.SetParent(parent, false);
            var filter = item.AddComponent<MeshFilter>();
            MeshRenderer renderer = item.AddComponent<MeshRenderer>();
            renderer.sharedMaterials = new[] { front, underside, edge };
            var mesh = new Mesh
            {
                name = "Gate04R012PhysicalFoldedPullTab",
                subMeshCount = 3
            };
            Vector3[] vertices =
            {
                new Vector3(-0.008f, -0.001f, -0.0004f),
                new Vector3(0.008f, -0.001f, -0.0004f),
                new Vector3(0.007f, 0.014f, -0.0004f),
                new Vector3(0.002f, 0.021f, -0.0004f),
                new Vector3(-0.006f, 0.017f, -0.0004f),
                new Vector3(-0.008f, -0.001f, 0.0004f),
                new Vector3(0.008f, -0.001f, 0.0004f),
                new Vector3(0.007f, 0.014f, 0.0004f),
                new Vector3(0.002f, 0.021f, 0.0004f),
                new Vector3(-0.006f, 0.017f, 0.0004f)
            };
            mesh.vertices = vertices;
            mesh.uv = new[]
            {
                new Vector2(0f, 0f), new Vector2(1f, 0f),
                new Vector2(1f, 1f), new Vector2(0.5f, 1f),
                new Vector2(0f, 1f), new Vector2(0f, 0f),
                new Vector2(1f, 0f), new Vector2(1f, 1f),
                new Vector2(0.5f, 1f), new Vector2(0f, 1f)
            };
            mesh.SetTriangles(
                new[] { 0, 1, 2, 0, 2, 4, 4, 2, 3 },
                0);
            mesh.SetTriangles(
                new[] { 5, 7, 6, 5, 9, 7, 9, 8, 7 },
                1);
            mesh.SetTriangles(
                new[]
                {
                    0, 5, 1, 1, 5, 6,
                    1, 6, 2, 2, 6, 7,
                    2, 7, 3, 3, 7, 8,
                    3, 8, 4, 4, 8, 9,
                    4, 9, 0, 0, 9, 5
                },
                2);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            filter.sharedMesh = mesh;
            return item;
        }

        private static SourceEffects BuildSourceEffects(
            Transform parent,
            Material sweepMaterial,
            Material strikeMaterial)
        {
            var root = new GameObject("AuditedMakeItShineCc0ShurikenAdapter");
            root.transform.SetParent(parent, false);
            ParticleSystem sweep = CreateSourceSystem(
                root.transform,
                "SG_TitleKyleSphereMaskSweep_ShuriKen",
                sweepMaterial,
                6,
                0.92f,
                new Vector2(0.070f, 0.136f),
                new Vector2(0.004f, 0.012f),
                1229u,
                true);
            ParticleSystem strike = CreateSourceSystem(
                root.transform,
                "SG_LightingStrikeContourAccent_ShuriKen",
                strikeMaterial,
                14,
                0.52f,
                new Vector2(0.028f, 0.075f),
                new Vector2(0.012f, 0.046f),
                2237u,
                false);
            return new SourceEffects(root.transform, new[] { sweep, strike });
        }

        private static ParticleSystem CreateSourceSystem(
            Transform parent,
            string name,
            Material material,
            short particles,
            float lifetime,
            Vector2 width,
            Vector2 speed,
            uint seed,
            bool primarySweep)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            ParticleSystem system = item.AddComponent<ParticleSystem>();
            ParticleSystem.MainModule main = system.main;
            main.loop = false;
            main.playOnAwake = false;
            main.duration = 0.08f;
            main.startLifetime = new ParticleSystem.MinMaxCurve(
                lifetime * 0.72f,
                lifetime);
            main.startSize3D = true;
            main.startSizeX = new ParticleSystem.MinMaxCurve(width.x, width.y);
            main.startSizeY = new ParticleSystem.MinMaxCurve(
                primarySweep ? 0.0035f : 0.0018f,
                primarySweep ? 0.0075f : 0.004f);
            main.startSizeZ = new ParticleSystem.MinMaxCurve(1f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(speed.x, speed.y);
            main.startColor = primarySweep
                ? new ParticleSystem.MinMaxGradient(
                    new Color(1f, 0.82f, 0.62f, 0.52f),
                    new Color(0.76f, 0.87f, 1f, 0.30f))
                : new ParticleSystem.MinMaxGradient(
                    new Color(0.84f, 0.91f, 1f, 0.26f),
                    new Color(1f, 0.76f, 0.53f, 0.22f));
            main.simulationSpace = ParticleSystemSimulationSpace.Local;
            main.maxParticles = particles;
            ParticleSystem.EmissionModule emission = system.emission;
            emission.rateOverTime = 0f;
            emission.SetBursts(new[]
            {
                new ParticleSystem.Burst(0f, particles)
            });
            ParticleSystem.ShapeModule shape = system.shape;
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Sphere;
            shape.radius = primarySweep ? 0.033f : 0.020f;
            shape.radiusThickness = 1f;
            ParticleSystem.VelocityOverLifetimeModule velocity =
                system.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.Local;
            velocity.x = new ParticleSystem.MinMaxCurve(
                primarySweep ? -0.040f : -0.068f,
                primarySweep ? 0.040f : 0.068f);
            velocity.y = new ParticleSystem.MinMaxCurve(
                primarySweep ? 0.010f : 0.018f,
                primarySweep ? 0.042f : 0.070f);
            velocity.z = new ParticleSystem.MinMaxCurve(-0.004f, 0.004f);
            ParticleSystem.ColorOverLifetimeModule color = system.colorOverLifetime;
            color.enabled = true;
            var gradient = new Gradient();
            gradient.SetKeys(
                primarySweep
                    ? new[]
                    {
                        new GradientColorKey(
                            new Color(1f, 0.82f, 0.61f), 0f),
                        new GradientColorKey(
                            new Color(1f, 0.97f, 0.92f), 0.54f),
                        new GradientColorKey(
                            new Color(0.79f, 0.88f, 1f), 1f)
                    }
                    : new[]
                    {
                        new GradientColorKey(
                            new Color(0.72f, 0.84f, 1f), 0f),
                        new GradientColorKey(
                            new Color(1f, 0.82f, 0.59f), 1f)
                    },
                new[]
                {
                    new GradientAlphaKey(0f, 0f),
                    new GradientAlphaKey(primarySweep ? 0.75f : 0.48f, 0.13f),
                    new GradientAlphaKey(primarySweep ? 0.44f : 0.22f, 0.68f),
                    new GradientAlphaKey(0f, 1f)
                });
            color.color = new ParticleSystem.MinMaxGradient(gradient);
            ParticleSystem.SizeOverLifetimeModule size = system.sizeOverLifetime;
            size.enabled = true;
            size.size = new ParticleSystem.MinMaxCurve(
                1f,
                AnimationCurve.EaseInOut(0f, 0.32f, 1f, 0.78f));
            ParticleSystemRenderer renderer =
                item.GetComponent<ParticleSystemRenderer>();
            renderer.sharedMaterial = material;
            renderer.renderMode = ParticleSystemRenderMode.Billboard;
            renderer.alignment = ParticleSystemRenderSpace.View;
            renderer.sortingOrder = 6;
            system.useAutoRandomSeed = false;
            system.randomSeed = seed;
            system.Stop(
                true,
                ParticleSystemStopBehavior.StopEmittingAndClear);
            return system;
        }

        private static GameObject CreateDynamicMeshObject(
            Transform parent,
            string name,
            Material material)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            item.AddComponent<MeshFilter>();
            MeshRenderer renderer = item.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
            return item;
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

        private static void ConfigureLitTexture(
            Material material,
            Texture texture,
            Color color,
            float metallic,
            float smoothness,
            int renderQueue)
        {
            material.SetTexture("_BaseMap", texture);
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_AlphaClip", 1f);
            material.SetFloat("_Cutoff", 0.018f);
            material.EnableKeyword("_ALPHATEST_ON");
            material.renderQueue = renderQueue;
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
                    material.renderQueue = renderQueue;
                });
        }

        private static Material CreateMaterial(
            string name,
            Shader shader,
            Action<Material> configure)
        {
            string path = $"{MaterialRoot}/{name}.mat";
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

        private static PremiumDisplayCaseLabelData BuildAuthoritativeReviewLabel()
        {
            const string prefix =
                "fidgeting.gacha.preview.gate04-r012-physical-tear.";
            var inventory = new GachaInventoryRuntime(
                prefix,
                new GachaSplitMix64(0x410012UL));
            const string request = "gate04-r012-physical-tear";
            GachaTransactionResult transaction = inventory.QueryTransaction(request);
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
                    "Could not create the authoritative rev 12 review receipt.");
            }
            GachaDrawReceiptRow row = transaction.Receipt.Rows[0];
            GachaPrizeDefinition prize =
                GachaCatalog.ResolvePrize(row.Outcome.PrizeId).Value;
            return GachaShippingLabelAuthority.Create(prize, row, 1);
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

        private static void WriteSourceMapping()
        {
            string path = Path.Combine(
                ProjectRoot,
                EvidenceRoot,
                "source-to-canonical-mapping.json");
            var json = new StringBuilder(16384);
            json.AppendLine("{");
            json.AppendLine("  \"schema\": \"make-it-shine-cc0-source-mapping.v2\",");
            json.AppendLine("  \"sourceCommit\": \"88842be0063b5b0b75e82ed6572752a37a13c82b\",");
            json.AppendLine("  \"license\": \"CC0-1.0\",");
            json.AppendLine("  \"entries\": [");
            AppendMapping(json,
                "Assets/Animation/Timelines/Booster to Card Timeline.playable",
                SourceTimelineHash,
                EvidenceRoot + "/source-raw/Booster to Card Timeline.playable",
                "direct-copy",
                "The exact source Timeline remains an immutable audit source. Its proxy and VFX Graph bindings are not a runtime dependency.");
            AppendMapping(json,
                "Assets/Animation/Clips/Booster/Booster_Discarded.anim",
                SourceDiscardHash,
                ImportedSourceRoot + "/Animation/Booster_Discarded.anim",
                "direct-copy",
                "Exact source discard curve copied before the R012 profile evaluates its normalized keys.");
            AppendMapping(json,
                "Assets/Art/Environment/Shaders/SG_BoosterPack.shadergraph",
                SourceBoosterHash,
                EvidenceRoot + "/source-raw/SG_BoosterPack.shadergraph",
                "direct-copy",
                "Exact source shader graph retained before the torn-contour discard adapter.");
            AppendMapping(json,
                "Assets/Art/Kyle/Materials/SG_Title_Kyle.shadergraph",
                SourceTitleHash,
                EvidenceRoot + "/source-raw/SG_Title_Kyle.shadergraph",
                "direct-copy",
                "Exact source Sphere Mask graph retained before the Shuriken flare sweep adapter.");
            AppendMapping(json,
                "Assets/Art/Booster/SG_LightingStrike.shadergraph",
                SourceLightingHash,
                EvidenceRoot + "/source-raw/SG_LightingStrike.shadergraph",
                "direct-copy",
                "Exact source Reveal/Erode graph retained before the Shuriken-compatible port.");
            AppendMapping(json,
                "Assets/Art/Booster/TX_Flare_2x2_M.png",
                SourceFlareHash,
                ImportedSourceRoot + "/Textures/TX_Flare_2x2_M.png",
                "direct-copy",
                "Exact flare atlas drives the visible source sweep and contour accent.");
            AppendMapping(json,
                "Assets/Art/Common/Textures/TX_Noise_M.tga",
                SourceNoiseHash,
                ImportedSourceRoot + "/Textures/TX_Noise_M.tga",
                "direct-copy",
                "Exact source noise is retained for audit only. It does not create pixel-noise dissolve.");
            AppendMapping(json,
                "Assets/Animation/Clips/Booster/Booster_Discarded.anim",
                SourceDiscardHash,
                CandidateRoot + "/Runtime/PackOpeningGate04R012Profile.cs",
                "adapted",
                "The normalized source curve drives a physical Pack discard after the same case begins its continuous exit.");
            AppendMapping(json,
                "Assets/Art/Environment/Shaders/SG_BoosterPack.shadergraph",
                SourceBoosterHash,
                CandidateRoot + "/Shaders/MakeItShineCc0PackR012.shader",
                "adapted",
                "The source dissolve/emissive edge is evaluated from the fine per-column torn contour, not a screen-wide rectangle.");
            AppendMapping(json,
                "Assets/Art/Kyle/Materials/SG_Title_Kyle.shadergraph",
                SourceTitleHash,
                CandidateRoot + "/Shaders/MakeItShineCc0PortR012.shader",
                "adapted",
                "The source Sphere Mask sweep gates a portrait Shuriken flare sweep after the aperture appears.");
            AppendMapping(json,
                "Assets/Art/Booster/SG_LightingStrike.shadergraph",
                SourceLightingHash,
                CandidateRoot + "/Shaders/MakeItShineCc0PortR012.shader",
                "adapted",
                "The source Reveal/Erode structure ports to an additive URP Shuriken material with the source flare atlas.");
            AppendMapping(json,
                "Assets/Art/Booster/VFX_BoosterActivation.vfx",
                SourceActivationHash,
                CandidateRoot + "/Editor/PackOpeningGate04R012Builder.cs",
                "adapted",
                "VFX Graph is forbidden. The source timing language is retargeted as a bounded Shuriken sphere-mask sweep.");
            AppendMapping(json,
                "Assets/Art/Booster/VFXG_LightingStrike.vfx",
                SourceStrikeVfxHash,
                CandidateRoot + "/Editor/PackOpeningGate04R012Builder.cs",
                "adapted",
                "VFX Graph is forbidden. The source strike is reduced to a Shuriken contour accent with no magenta or cyan sparkle atlas cells.");
            AppendRejected(json,
                "Assets/Prefabs/Cinematic/Opening_Booster.prefab",
                "b155b76ffe54ac737651adbbfa177e284b22175733096e279e056316bf5aa978",
                "The sample uses a surrogate Pack and object swaps.");
            AppendRejected(json,
                "Assets/Art/Booster/BoosterFractured_B.fbx",
                "fd78b007802a1966a1dfb1a1c6b8c7c36cec2f3622dcbaf480fe039967ded602",
                "The sample has no physical tear mesh and its fractured Pack is forbidden.");
            AppendRejected(json,
                "Assets/Art/Booster/VFX_BoosterExplosion.vfx",
                SourceExplosionHash,
                "Source explosion and generic particulate burst are not a permitted product effect.");
            json.AppendLine("  ],");
            json.AppendLine("  \"vfxGraphDependency\": false,");
            json.AppendLine("  \"shurikenAdapter\": true,");
            json.AppendLine("  \"sampleModelsImported\": false,");
            json.AppendLine("  \"sampleArtworkImported\": false,");
            json.AppendLine("  \"shippingReady\": false");
            json.AppendLine("}");
            File.WriteAllText(
                path,
                json.ToString().Replace("    },\n  ],", "    }\n  ],"));
        }

        private static void WriteSourceManifest()
        {
            string path = Path.Combine(
                ProjectRoot,
                EvidenceRoot,
                "unity-source-manifest.json");
            string json =
                "{\n"
                + "  \"schema\": \"premium-display-case-gate04-r012-unity-source.v1\",\n"
                + "  \"unity\": \"6000.5.6f1\",\n"
                + "  \"urp\": \"17.5.0\",\n"
                + $"  \"scene\": \"{ScenePath}\",\n"
                + "  \"realPackCanvas\": [384, 512],\n"
                + "  \"longitudinalTearSegments\": 128,\n"
                + "  \"assembledCaseInstances\": 1,\n"
                + "  \"packFrontAndBackCoincidentAhead\": true,\n"
                + "  \"physicalMouth\": \"front lip, rear rim, side walls, rear wall behind case\",\n"
                + "  \"vfxGraph\": false,\n"
                + "  \"shuriken\": true,\n"
                + "  \"sampleModelsImported\": false,\n"
                + "  \"sampleArtworkImported\": false,\n"
                + "  \"shippingRuntimeWired\": false,\n"
                + "  \"nativeUiWired\": false,\n"
                + "  \"shippingReady\": false,\n"
                + "  \"physicalPhoneInstalled\": false\n"
                + "}\n";
            File.WriteAllText(path, json);
        }

        private static void AppendMapping(
            StringBuilder json,
            string source,
            string sourceHash,
            string destination,
            string decision,
            string reason)
        {
            string destinationAbsolute = Path.Combine(ProjectRoot, destination);
            string destinationHash = File.Exists(destinationAbsolute)
                ? Sha256File(destinationAbsolute)
                : "generated-after-import";
            json.AppendLine("    {");
            json.AppendLine($"      \"source\": \"{source}\",");
            json.AppendLine($"      \"sourceSha256\": \"{sourceHash}\",");
            json.AppendLine($"      \"destination\": \"{destination}\",");
            json.AppendLine($"      \"destinationSha256\": \"{destinationHash}\",");
            json.AppendLine($"      \"decision\": \"{decision}\",");
            json.AppendLine($"      \"reason\": \"{Escape(reason)}\"");
            json.AppendLine("    },");
        }

        private static void AppendRejected(
            StringBuilder json,
            string source,
            string sourceHash,
            string reason)
        {
            json.AppendLine("    {");
            json.AppendLine($"      \"source\": \"{source}\",");
            json.AppendLine($"      \"sourceSha256\": \"{sourceHash}\",");
            json.AppendLine("      \"destination\": null,");
            json.AppendLine("      \"destinationSha256\": null,");
            json.AppendLine("      \"decision\": \"rejected\",");
            json.AppendLine($"      \"reason\": \"{Escape(reason)}\"");
            json.AppendLine("    },");
        }

        private static void CopyExact(
            string sourceRelative,
            string destinationRelative,
            string expectedHash)
        {
            string source = Path.Combine(ProjectRoot, sourceRelative);
            string destination = Path.Combine(ProjectRoot, destinationRelative);
            if (!File.Exists(source))
            {
                throw new FileNotFoundException(
                    $"Missing direct CC0 source: {sourceRelative}");
            }
            string sourceHash = Sha256File(source);
            if (sourceHash != expectedHash)
            {
                throw new InvalidOperationException(
                    $"Source hash mismatch for {sourceRelative}: "
                    + $"expected {expectedHash}, got {sourceHash}.");
            }
            Directory.CreateDirectory(Path.GetDirectoryName(destination) ?? ProjectRoot);
            if (!File.Exists(destination)
                || !string.Equals(
                    Sha256File(destination),
                    expectedHash,
                    StringComparison.OrdinalIgnoreCase))
            {
                File.Copy(source, destination, true);
            }
            if (Sha256File(destination) != expectedHash)
            {
                throw new InvalidOperationException(
                    $"Copy hash mismatch for {destinationRelative}.");
            }
        }

        private static void AssertHash(string assetPath, string expected)
        {
            string absolute = Path.Combine(ProjectRoot, assetPath);
            if (!File.Exists(absolute))
            {
                throw new FileNotFoundException($"Missing source: {assetPath}");
            }
            string actual = Sha256File(absolute);
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

        private static string Sha256File(string path)
        {
            using SHA256 sha = SHA256.Create();
            using FileStream stream = File.OpenRead(path);
            return string.Concat(
                sha.ComputeHash(stream).Select(
                    value => value.ToString("x2", CultureInfo.InvariantCulture)));
        }

        private static string Escape(string value)
        {
            return value.Replace("\\", "\\\\").Replace("\"", "\\\"");
        }

        private static string ProjectRoot =>
            Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

        private readonly struct MaterialSet
        {
            public MaterialSet(
                Material pack,
                Material rearRim,
                Material stripFront,
                Material stripUnder,
                Material stripEdge,
                Material cavity,
                Material contact,
                Material sweep,
                Material strike,
                Material environment)
            {
                Pack = pack;
                RearRim = rearRim;
                StripFront = stripFront;
                StripUnder = stripUnder;
                StripEdge = stripEdge;
                Cavity = cavity;
                Contact = contact;
                Sweep = sweep;
                Strike = strike;
                Environment = environment;
            }

            public Material Pack { get; }
            public Material RearRim { get; }
            public Material StripFront { get; }
            public Material StripUnder { get; }
            public Material StripEdge { get; }
            public Material Cavity { get; }
            public Material Contact { get; }
            public Material Sweep { get; }
            public Material Strike { get; }
            public Material Environment { get; }
        }

        private readonly struct SourceEffects
        {
            public SourceEffects(Transform root, ParticleSystem[] systems)
            {
                Root = root;
                Systems = systems;
            }

            public Transform Root { get; }
            public ParticleSystem[] Systems { get; }
        }
    }
}
