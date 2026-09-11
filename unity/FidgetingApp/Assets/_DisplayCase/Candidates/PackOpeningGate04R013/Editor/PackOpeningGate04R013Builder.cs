using System;
using System.Collections.Generic;
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
    public static class PackOpeningGate04R013Builder
    {
        public const string CandidateRoot =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R013";
        public const string ScenePath =
            CandidateRoot + "/Scenes/PackOpeningGate04R013.unity";
        public const string ProfilePath =
            CandidateRoot + "/Profiles/PackOpeningGate04R013Profile.asset";
        public const string RigPath =
            CandidateRoot + "/Imported/PackOpeningGate04R013PackOnlyRig.fbx";
        public const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-013";
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

        private const string PreviousCandidateRoot =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R012";
        private const string PreviousEvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-012";
        private const string PackBodyHash =
            "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6";
        private const string PackFlapHash =
            "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49";
        private const string CasePrefabHash =
            "7a96aae6245b5a1d5463dabc3cb4518af8693ba8f8328ad9f2fe4ee6c6a67e2c";
        private const string PrizePrefabHash =
            "d68f51b0034199987fa9e0cd44a8e3ba351b70b4289ff4773edc296e9395a8e1";
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

        [MenuItem("Fidgeting/Display Case/Gate 04 R013/Build And Capture")]
        public static void BuildAndRunCapture()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                throw new InvalidOperationException(
                    "Unity is already entering or running PlayMode.");
            }

            BuildSceneInternal();
            Debug.Log(
                "GATE04_R013_PACK_ONLY_BLENDER_CAPTURE_READY "
                + $"scene={ScenePath} evidence={EvidenceRoot}");
            EditorApplication.isPlaying = true;
        }

        [MenuItem("Fidgeting/Display Case/Gate 04 R013/Build Scene Only")]
        public static void BuildSceneOnly()
        {
            BuildSceneInternal();
            Debug.Log($"Gate 04 R013 Pack-only scene built at {ScenePath}.");
        }

        private static void BuildSceneInternal()
        {
            AssertEngineContract();
            EnsureDirectories();
            CopyDirectSources();
            CopySourceReferenceFrames();
            ConfigureRigImporter();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            AssertSourceAssets();
            PackOpeningGate04R013Profile profile = CreateProfile();
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
                    $"R013 requires Unity 6000.5.6f1, got {Application.unityVersion}.");
            }

            UnityEditor.PackageManager.PackageInfo urp =
                UnityEditor.PackageManager.PackageInfo.FindForAssetPath(
                    "Packages/com.unity.render-pipelines.universal");
            if (urp == null || urp.version != "17.5.0")
            {
                throw new InvalidOperationException(
                    $"R013 requires URP 17.5.0, got {urp?.version ?? "missing"}.");
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

        private static void ConfigureRigImporter()
        {
            string absolute = Path.Combine(ProjectRoot, RigPath);
            if (!File.Exists(absolute))
            {
                throw new FileNotFoundException(
                    "Build the Pack-only Blender rig before Unity import.",
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
            importer.optimizeMeshPolygons = true;
            importer.optimizeMeshVertices = true;
            AssetDatabase.WriteImportSettingsIfDirty(RigPath);
            AssetDatabase.ImportAsset(
                RigPath,
                ImportAssetOptions.ForceSynchronousImport);
        }

        private static void CopyDirectSources()
        {
            CopyExact(
                PreviousCandidateRoot + "/ImportedSource/Animation/Booster_Discarded.anim",
                CandidateRoot + "/ImportedSource/Animation/Booster_Discarded.anim",
                SourceDiscardHash);
            CopyExact(
                PreviousCandidateRoot + "/ImportedSource/Textures/TX_Flare_2x2_M.png",
                CandidateRoot + "/ImportedSource/Textures/TX_Flare_2x2_M.png",
                SourceFlareHash);
            CopyExact(
                PreviousCandidateRoot + "/ImportedSource/Textures/TX_Noise_M.tga",
                CandidateRoot + "/ImportedSource/Textures/TX_Noise_M.tga",
                SourceNoiseHash);
            CopyExact(
                PreviousEvidenceRoot + "/source-raw/Booster to Card Timeline.playable",
                EvidenceRoot + "/source-raw/Booster to Card Timeline.playable",
                SourceTimelineHash);
            CopyExact(
                PreviousEvidenceRoot + "/source-raw/SG_BoosterPack.shadergraph",
                EvidenceRoot + "/source-raw/SG_BoosterPack.shadergraph",
                SourceBoosterHash);
            CopyExact(
                PreviousEvidenceRoot + "/source-raw/SG_Title_Kyle.shadergraph",
                EvidenceRoot + "/source-raw/SG_Title_Kyle.shadergraph",
                SourceTitleHash);
            CopyExact(
                PreviousEvidenceRoot + "/source-raw/SG_LightingStrike.shadergraph",
                EvidenceRoot + "/source-raw/SG_LightingStrike.shadergraph",
                SourceLightingHash);
            CopyExact(
                PreviousEvidenceRoot + "/source-raw/VFX_BoosterActivation.vfx",
                EvidenceRoot + "/source-raw/VFX_BoosterActivation.vfx",
                SourceActivationHash);
            CopyExact(
                PreviousEvidenceRoot + "/source-raw/VFXG_LightingStrike.vfx",
                EvidenceRoot + "/source-raw/VFXG_LightingStrike.vfx",
                SourceStrikeVfxHash);
            CopyExact(
                PreviousEvidenceRoot + "/source-raw/VFX_BoosterExplosion.vfx",
                EvidenceRoot + "/source-raw/VFX_BoosterExplosion.vfx",
                SourceExplosionHash);
        }

        private static void CopySourceReferenceFrames()
        {
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
                string source = Path.Combine(
                    ProjectRoot,
                    PreviousEvidenceRoot,
                    "source-reference",
                    name);
                if (!File.Exists(source))
                {
                    throw new FileNotFoundException(
                        "The audited source capture is missing.",
                        source);
                }

                File.Copy(
                    source,
                    Path.Combine(
                        ProjectRoot,
                        EvidenceRoot,
                        "source-reference",
                        name),
                    true);
            }
        }

        private static void AssertSourceAssets()
        {
            AssertHash(PackBodyPath, PackBodyHash);
            AssertHash(PackFlapPath, PackFlapHash);
            AssertHash(ActualCasePrefabPath, CasePrefabHash);
            AssertHash(ActualPrizePrefabPath, PrizePrefabHash);
            AssertHash(
                CandidateRoot + "/ImportedSource/Animation/Booster_Discarded.anim",
                SourceDiscardHash);
            AssertHash(
                CandidateRoot + "/ImportedSource/Textures/TX_Flare_2x2_M.png",
                SourceFlareHash);
            AssertHash(
                CandidateRoot + "/ImportedSource/Textures/TX_Noise_M.tga",
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
            AssertHash(RigPath, Sha256File(Path.Combine(ProjectRoot, RigPath)));
            AssertPngDimensions(PackBodyPath, 384, 512);
            AssertPngDimensions(PackFlapPath, 384, 512);
        }

        private static PackOpeningGate04R013Profile CreateProfile()
        {
            PackOpeningGate04R013Profile profile =
                AssetDatabase.LoadAssetAtPath<PackOpeningGate04R013Profile>(
                    ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<
                    PackOpeningGate04R013Profile>();
                AssetDatabase.CreateAsset(profile, ProfilePath);
            }

            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static MaterialSet CreateMaterials()
        {
            Shader lit = RequireShader("Universal Render Pipeline/Lit");
            Shader packShader = RequireShader(
                "FidgetingApp/Candidates/MakeItShineCc0PackR013");
            Shader rimShader = RequireShader(
                "FidgetingApp/Candidates/MakeItShineCc0ContourRimR013");
            Shader portShader = RequireShader(
                "FidgetingApp/Candidates/MakeItShineCc0PortR013");
            Texture2D body = RequireTexture(PackBodyPath);
            Texture2D flap = RequireTexture(PackFlapPath);
            Texture2D flare = RequireTexture(
                CandidateRoot + "/ImportedSource/Textures/TX_Flare_2x2_M.png");

            Material pack = CreateMaterial(
                "Gate04R013RealPackCc0Discard",
                packShader,
                material =>
                {
                    material.SetTexture("_BaseMap", body);
                    material.SetColor("_BaseColor", new Color(0.96f, 0.96f, 0.94f, 1f));
                    material.SetFloat("_Dissolve", 0f);
                    material.SetFloat("_EdgeWidth", 0.018f);
                    material.SetColor("_EdgeColor", new Color(0.95f, 0.70f, 0.40f, 1f));
                    material.SetFloat("_EdgeStrength", 0.44f);
                    material.renderQueue = 2460;
                });
            Material back = CreateMaterial(
                "Gate04R013BackFoil",
                packShader,
                material =>
                {
                    material.SetTexture("_BaseMap", body);
                    material.SetColor(
                        "_BaseColor",
                        new Color(0.12f, 0.11f, 0.10f, 1f));
                    material.SetFloat("_Dissolve", 0f);
                    material.SetFloat("_EdgeWidth", 0.018f);
                    material.SetColor(
                        "_EdgeColor",
                        new Color(0.55f, 0.38f, 0.23f, 1f));
                    material.SetFloat("_EdgeStrength", 0.24f);
                    material.renderQueue = 2450;
                });
            Material inner = CreateLitMaterial(
                "Gate04R013InnerFoil",
                lit,
                new Color(0.026f, 0.018f, 0.012f, 1f),
                0f,
                0.42f,
                2470);
            Material contact = CreateLitMaterial(
                "Gate04R013FrontLipContact",
                lit,
                new Color(0.006f, 0.004f, 0.002f, 1f),
                0f,
                0.48f,
                2480);
            Material stripFront = CreateMaterial(
                "Gate04R013TornSealFront",
                lit,
                material => ConfigureLitTexture(
                    material,
                    flap,
                    new Color(0.34f, 0.31f, 0.27f, 1f),
                    0.25f,
                    0.62f,
                    2490));
            Material stripUnder = CreateLitMaterial(
                "Gate04R013TornSealDarkUnderside",
                lit,
                new Color(0.012f, 0.011f, 0.010f, 1f),
                0.12f,
                0.72f,
                2490);
            Material cutEdge = CreateLitMaterial(
                "Gate04R013TornSealCutEdge",
                lit,
                new Color(0.12f, 0.092f, 0.060f, 1f),
                0.18f,
                0.58f,
                2490);
            Material rim = CreateMaterial(
                "Gate04R013Cc0TornContourRim",
                rimShader,
                material =>
                {
                    material.SetColor(
                        "_RimColor",
                        new Color(0.98f, 0.38f, 0.08f, 0.88f));
                    material.SetFloat("_Progress", 0f);
                    material.SetFloat("_Intensity", 1.20f);
                    material.renderQueue = 3000;
                });
            Material flareSweep = CreateMaterial(
                "Gate04R013Cc0FlareSweep",
                portShader,
                material =>
                {
                    material.SetTexture("_BaseMap", flare);
                    material.SetTextureScale("_BaseMap", new Vector2(0.5f, 0.5f));
                    material.SetTextureOffset("_BaseMap", new Vector2(0.5f, 0f));
                    material.SetColor(
                        "_BaseColor",
                        new Color(1f, 0.58f, 0.26f, 0.84f));
                    material.SetFloat("_Reveal", 1f);
                    material.SetFloat("_Erode", 0.012f);
                    material.SetFloat("_Intensity", 1.40f);
                    material.renderQueue = 3020;
                });
            Material flareAccent = CreateMaterial(
                "Gate04R013Cc0FlareAccent",
                portShader,
                material =>
                {
                    material.SetTexture("_BaseMap", flare);
                    material.SetTextureScale("_BaseMap", new Vector2(0.5f, 0.5f));
                    material.SetTextureOffset("_BaseMap", new Vector2(0.5f, 0f));
                    material.SetColor(
                        "_BaseColor",
                        new Color(0.84f, 0.40f, 0.16f, 0.72f));
                    material.SetFloat("_Reveal", 1f);
                    material.SetFloat("_Erode", 0.018f);
                    material.SetFloat("_Intensity", 1.05f);
                    material.renderQueue = 3020;
                });
            Material environment = CreateEnvironmentMaterial();
            return new MaterialSet(
                pack,
                back,
                inner,
                contact,
                stripFront,
                stripUnder,
                cutEdge,
                rim,
                flareSweep,
                flareAccent,
                environment);
        }

        private static Material CreateEnvironmentMaterial()
        {
            string path = CandidateRoot
                + "/Generated/Materials/Gate04R013DarkMineralEnvironment.mat";
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
                name = "Gate04R013DarkMineralEnvironment"
            };
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        private static Scene BuildScene(
            PackOpeningGate04R013Profile profile,
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
                out SkinnedMeshRenderer backFoil,
                out SkinnedMeshRenderer topCrimp,
                out SkinnedMeshRenderer tornContourRim,
                out SkinnedMeshRenderer tornSealStrip,
                out SkinnedMeshRenderer rolledFrontLip);
            SourceEffects sourceEffects = BuildSourceEffects(
                packRoot,
                materials.FlareSweep,
                materials.FlareAccent);

            var controllerObject = new GameObject(
                "PackOpeningGate04R013PackOnlyBlenderController");
            var controller =
                controllerObject.AddComponent<PackOpeningGate04R013Sequence>();
            controller.Configure(
                profile,
                camera,
                packRoot,
                packRenderers,
                frontFoil,
                backFoil,
                topCrimp,
                tornContourRim,
                tornSealStrip,
                rolledFrontLip,
                caseMotionRoot,
                presentation,
                sourceEffects.Root,
                sourceEffects.Systems);

            var captureObject = new GameObject(
                "RealUnityPlayModeCaptureR013");
            var capture =
                captureObject.AddComponent<PackOpeningGate04R013Capture>();
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
            var item = new GameObject("Gate04R013ShippingPortraitCamera");
            item.tag = "MainCamera";
            Camera camera = item.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.003f, 0.004f, 0.005f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.fieldOfView = 31.0f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.transform.position = new Vector3(0f, 0.004f, -1.40f);
            camera.transform.LookAt(new Vector3(0f, -0.006f, -0.035f));
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
                new Color(0.66f, 0.68f, 0.67f, 1f));
            material.SetFloat("_Saturation", 0.34f);
            material.SetFloat("_Opacity", 1f);
            material.SetFloat("_GlowEnabled", 0f);
            EditorUtility.SetDirty(material);
        }

        private static void BuildLighting()
        {
            CreateDirectionalLight(
                "PremiumNeutralKey",
                Quaternion.Euler(33f, -31f, 0f),
                new Color(1f, 0.92f, 0.82f),
                2.25f,
                0.36f);
            CreateDirectionalLight(
                "MineralSoftFill",
                Quaternion.Euler(54f, 148f, 0f),
                new Color(0.70f, 0.73f, 0.76f),
                0.70f,
                0.20f);
            CreateDirectionalLight(
                "FoilRim",
                Quaternion.Euler(24f, 210f, 0f),
                new Color(0.96f, 0.84f, 0.68f),
                0.90f,
                0.24f);
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.220f, 0.225f, 0.230f);
            RenderSettings.ambientEquatorColor =
                new Color(0.100f, 0.105f, 0.110f);
            RenderSettings.ambientGroundColor =
                new Color(0.026f, 0.026f, 0.024f);
            RenderSettings.reflectionIntensity = 0.62f;
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
            caseMotionRoot.position = new Vector3(0f, -0.010f, 0.180f);
            caseMotionRoot.localScale = Vector3.one * 1.02f;
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
            out SkinnedMeshRenderer[] renderers,
            out SkinnedMeshRenderer frontFoil,
            out SkinnedMeshRenderer backFoil,
            out SkinnedMeshRenderer topCrimp,
            out SkinnedMeshRenderer tornContourRim,
            out SkinnedMeshRenderer tornSealStrip,
            out SkinnedMeshRenderer rolledFrontLip)
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

            rig.name = "ActualAuthoredStandardPackOnlyBlenderRig";
            packRoot = rig.transform;
            packRoot.position = new Vector3(0f, 0.015f, -0.180f);
            packRoot.localRotation = Quaternion.identity;
            packRoot.localScale = new Vector3(-1f, 1f, 1f);
            renderers = rig.GetComponentsInChildren<SkinnedMeshRenderer>(true)
                .OrderBy(item => item.name, StringComparer.Ordinal)
                .ToArray();
            if (renderers.Length != 10)
            {
                throw new InvalidOperationException(
                    $"Expected 10 Pack-only rig renderers, got {renderers.Length}.");
            }

            frontFoil = RequireRenderer(renderers, "Pack_FrontFoil");
            backFoil = RequireRenderer(renderers, "Pack_BackFoil");
            topCrimp = RequireRenderer(renderers, "Pack_TopCrimpRemaining");
            SkinnedMeshRenderer mouth = RequireRenderer(
                renderers,
                "Pack_InnerFoilMouth");
            SkinnedMeshRenderer leadingGusset = RequireRenderer(
                renderers,
                "Pack_MouthLeadingGusset");
            SkinnedMeshRenderer tabGusset = RequireRenderer(
                renderers,
                "Pack_MouthTabGusset");
            rolledFrontLip = RequireRenderer(renderers, "Pack_RolledFrontLip");
            tornContourRim = RequireRenderer(
                renderers,
                "Pack_TornContourRim");
            tornSealStrip = RequireRenderer(renderers, "Pack_TornSealStrip");
            SkinnedMeshRenderer pullTab = RequireRenderer(
                renderers,
                "Pack_TopRightPullTab");

            frontFoil.sharedMaterial = materials.Pack;
            topCrimp.sharedMaterial = materials.Pack;
            backFoil.sharedMaterial = materials.Back;
            mouth.sharedMaterial = materials.Inner;
            leadingGusset.sharedMaterial = materials.Inner;
            tabGusset.sharedMaterial = materials.Inner;
            rolledFrontLip.sharedMaterial = materials.Contact;
            tornContourRim.sharedMaterial = materials.Rim;
            tornSealStrip.sharedMaterials = new[]
            {
                materials.StripFront,
                materials.StripUnder,
                materials.CutEdge
            };
            pullTab.sharedMaterials = new[]
            {
                materials.StripFront,
                materials.StripUnder,
                materials.CutEdge
            };
            foreach (SkinnedMeshRenderer renderer in renderers)
            {
                renderer.updateWhenOffscreen = true;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
            }
        }

        private static SourceEffects BuildSourceEffects(
            Transform parent,
            Material sweepMaterial,
            Material accentMaterial)
        {
            var root = new GameObject("AuditedMakeItShineCc0ShurikenAdapter");
            root.transform.SetParent(parent, false);
            ParticleSystem sweep = CreateSourceSystem(
                root.transform,
                "SG_TitleKyleSphereMaskSweep_ShuriKen",
                sweepMaterial,
                3,
                0.88f,
                new Vector2(0.040f, 0.072f),
                new Vector2(0.006f, 0.012f),
                13013u);
            ParticleSystem accent = CreateSourceSystem(
                root.transform,
                "SG_LightingStrikeWarmContourAccent_ShuriKen",
                accentMaterial,
                4,
                0.46f,
                new Vector2(0.020f, 0.040f),
                new Vector2(0.012f, 0.030f),
                13014u);
            return new SourceEffects(root.transform, new[] { sweep, accent });
        }

        private static ParticleSystem CreateSourceSystem(
            Transform parent,
            string name,
            Material material,
            short particles,
            float lifetime,
            Vector2 width,
            Vector2 speed,
            uint seed)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            ParticleSystem system = item.AddComponent<ParticleSystem>();
            ParticleSystem.MainModule main = system.main;
            main.loop = false;
            main.playOnAwake = false;
            main.duration = 0.06f;
            main.startLifetime = new ParticleSystem.MinMaxCurve(
                lifetime * 0.72f,
                lifetime);
            main.startSize3D = true;
            main.startSizeX = new ParticleSystem.MinMaxCurve(width.x, width.y);
            main.startSizeY = new ParticleSystem.MinMaxCurve(0.006f, 0.012f);
            main.startSizeZ = new ParticleSystem.MinMaxCurve(1f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(speed.x, speed.y);
            main.startColor = new ParticleSystem.MinMaxGradient(
                new Color(1f, 0.62f, 0.28f, 0.82f),
                new Color(0.74f, 0.38f, 0.16f, 0.64f));
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
            shape.radius = 0.012f;
            shape.radiusThickness = 1f;
            ParticleSystem.VelocityOverLifetimeModule velocity =
                system.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.Local;
            velocity.x = new ParticleSystem.MinMaxCurve(-0.028f, 0.028f);
            velocity.y = new ParticleSystem.MinMaxCurve(0.006f, 0.028f);
            velocity.z = new ParticleSystem.MinMaxCurve(-0.002f, 0.002f);
            ParticleSystem.ColorOverLifetimeModule color = system.colorOverLifetime;
            color.enabled = true;
            var gradient = new Gradient();
            gradient.SetKeys(
                new[]
                {
                    new GradientColorKey(new Color(1f, 0.72f, 0.42f), 0f),
                    new GradientColorKey(new Color(0.78f, 0.52f, 0.32f), 1f)
                },
                new[]
                {
                    new GradientAlphaKey(0f, 0f),
                    new GradientAlphaKey(0.82f, 0.14f),
                    new GradientAlphaKey(0.48f, 0.66f),
                    new GradientAlphaKey(0f, 1f)
                });
            color.color = new ParticleSystem.MinMaxGradient(gradient);
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

        private static PremiumDisplayCaseLabelData BuildAuthoritativeReviewLabel()
        {
            const string prefix =
                "fidgeting.gacha.preview.gate04-r013-pack-only-blender.";
            var inventory = new GachaInventoryRuntime(
                prefix,
                new GachaSplitMix64(0x410013UL));
            const string request = "gate04-r013-pack-only-blender";
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
                    "Could not create the authoritative R013 review receipt.");
            }

            GachaDrawReceiptRow row = transaction.Receipt.Rows[0];
            GachaPrizeDefinition prize =
                GachaCatalog.ResolvePrize(row.Outcome.PrizeId).Value;
            return GachaShippingLabelAuthority.Create(prize, row, 1);
        }

        private static SkinnedMeshRenderer RequireRenderer(
            IEnumerable<SkinnedMeshRenderer> renderers,
            string name)
        {
            SkinnedMeshRenderer renderer = renderers.SingleOrDefault(
                item => string.Equals(item.name, name, StringComparison.Ordinal));
            if (renderer == null || renderer.sharedMesh == null
                || renderer.sharedMesh.blendShapeCount != 5)
            {
                throw new MissingReferenceException(
                    $"Invalid Pack-only rig renderer: {name}");
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
            material.SetFloat("_Cull", 0f);
            material.SetFloat("_AlphaClip", 1f);
            material.SetFloat("_Cutoff", 0.018f);
            material.EnableKeyword("_ALPHATEST_ON");
            material.renderQueue = renderQueue;
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

        private static void WriteSourceMapping()
        {
            string fbxHash = Sha256File(Path.Combine(ProjectRoot, RigPath));
            string blendHash = Sha256File(Path.Combine(
                ProjectRoot,
                EvidenceRoot,
                "pack-opening-gate04-r013.blend"));
            string path = Path.Combine(
                ProjectRoot,
                EvidenceRoot,
                "source-to-canonical-mapping.json");
            var json = new StringBuilder(16384);
            json.AppendLine("{");
            json.AppendLine("  \"schema\": \"make-it-shine-cc0-source-mapping.v3\",");
            json.AppendLine("  \"sourceCommit\": \"88842be0063b5b0b75e82ed6572752a37a13c82b\",");
            json.AppendLine("  \"license\": \"CC0-1.0\",");
            json.AppendLine("  \"entries\": [");
            AppendMapping(json,
                "Assets/Animation/Timelines/Booster to Card Timeline.playable",
                SourceTimelineHash,
                EvidenceRoot + "/source-raw/Booster to Card Timeline.playable",
                "direct-copy",
                "Immutable CC0 Timeline audit source; its proxies are not a runtime dependency.");
            AppendMapping(json,
                "Assets/Animation/Clips/Booster/Booster_Discarded.anim",
                SourceDiscardHash,
                CandidateRoot + "/ImportedSource/Animation/Booster_Discarded.anim",
                "direct-copy",
                "Exact source discard curve copied before R013 evaluates its normalized keys.");
            AppendMapping(json,
                "Assets/Art/Environment/Shaders/SG_BoosterPack.shadergraph",
                SourceBoosterHash,
                EvidenceRoot + "/source-raw/SG_BoosterPack.shadergraph",
                "direct-copy",
                "Exact source dissolve graph retained before the Pack-only adapter.");
            AppendMapping(json,
                "Assets/Art/Kyle/Materials/SG_Title_Kyle.shadergraph",
                SourceTitleHash,
                EvidenceRoot + "/source-raw/SG_Title_Kyle.shadergraph",
                "direct-copy",
                "Exact source sphere-mask graph retained before the contour sweep adapter.");
            AppendMapping(json,
                "Assets/Art/Booster/SG_LightingStrike.shadergraph",
                SourceLightingHash,
                EvidenceRoot + "/source-raw/SG_LightingStrike.shadergraph",
                "direct-copy",
                "Exact source reveal and erode graph retained before the Shuriken adapter.");
            AppendMapping(json,
                "Assets/Art/Booster/TX_Flare_2x2_M.png",
                SourceFlareHash,
                CandidateRoot + "/ImportedSource/Textures/TX_Flare_2x2_M.png",
                "direct-copy",
                "Exact atlas is sampled as luminance only, so source RGB fringes cannot leak.");
            AppendMapping(json,
                "Assets/Art/Common/Textures/TX_Noise_M.tga",
                SourceNoiseHash,
                CandidateRoot + "/ImportedSource/Textures/TX_Noise_M.tga",
                "direct-copy",
                "Exact source noise remains audit-only; it cannot create a pixel-noise dissolve.");
            AppendMapping(json,
                "Assets/Animation/Clips/Booster/Booster_Discarded.anim",
                SourceDiscardHash,
                CandidateRoot + "/Runtime/PackOpeningGate04R013Profile.cs",
                "adapted",
                "The exact normalized curve drives late Pack discard after the case has entered the mouth.");
            AppendMapping(json,
                "Assets/Art/Environment/Shaders/SG_BoosterPack.shadergraph",
                SourceBoosterHash,
                CandidateRoot + "/Shaders/MakeItShineCc0PackR013.shader",
                "adapted",
                "Source discard and emissive edge are constrained to the physical Pack after the tear.");
            AppendMapping(json,
                "Assets/Art/Kyle/Materials/SG_Title_Kyle.shadergraph",
                SourceTitleHash,
                CandidateRoot + "/Shaders/MakeItShineCc0ContourRimR013.shader",
                "adapted",
                "Source sphere-mask timing sweeps a narrow Blender-authored torn contour.");
            AppendMapping(json,
                "Assets/Art/Booster/SG_LightingStrike.shadergraph",
                SourceLightingHash,
                CandidateRoot + "/Shaders/MakeItShineCc0PortR013.shader",
                "adapted",
                "Source reveal and erode math drives a small warm-neutral Shuriken accent.");
            AppendMapping(json,
                "Assets/Art/Booster/VFX_BoosterActivation.vfx",
                SourceActivationHash,
                CandidateRoot + "/Editor/PackOpeningGate04R013Builder.cs",
                "adapted",
                "Only bounded timing and source-material presentation are ported to Shuriken.");
            AppendMapping(json,
                "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png",
                PackBodyHash,
                RigPath,
                "adapted",
                $"Blender Pack-only blend-shape rig preserves the actual 384x512 artwork; FBX SHA-256 {fbxHash}.");
            AppendMapping(json,
                "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png",
                PackFlapHash,
                EvidenceRoot + "/pack-opening-gate04-r013.blend",
                "adapted",
                $"Blender top crimp and pull tab use the actual flap artwork; Blend SHA-256 {blendHash}.");
            AppendRejected(json,
                "Assets/Prefabs/Cinematic/Opening_Booster.prefab",
                "b155b76ffe54ac737651adbbfa177e284b22175733096e279e056316bf5aa978",
                "Sample surrogate Pack and object swaps are forbidden.");
            AppendRejected(json,
                "Assets/Art/Booster/BoosterFractured_B.fbx",
                "fd78b007802a1966a1dfb1a1c6b8c7c36cec2f3622dcbaf480fe039967ded602",
                "The sample has no continuous Pack mouth and cannot replace the physical Blender rig.");
            AppendRejected(json,
                "Assets/Art/Booster/VFXG_LightingStrike.vfx",
                SourceStrikeVfxHash,
                "512-spark source behavior is forbidden; no VFX Graph is imported or executed.");
            AppendRejected(json,
                "Assets/Art/Booster/VFX_BoosterExplosion.vfx",
                SourceExplosionHash,
                "Explosion burst is forbidden; no generic particulate effect is ported.");
            json.AppendLine("  ],");
            json.AppendLine("  \"vfxGraphDependency\": false,");
            json.AppendLine("  \"shurikenAdapter\": true,");
            json.AppendLine("  \"sampleModelsImported\": false,");
            json.AppendLine("  \"sampleArtworkImported\": false,");
            json.AppendLine("  \"packOnlyBlenderRig\": true,");
            json.AppendLine("  \"shippingReady\": false");
            json.AppendLine("}");
            File.WriteAllText(
                path,
                json.ToString().Replace("    },\n  ],", "    }\n  ],"));
        }

        private static void WriteSourceManifest()
        {
            string rigAbsolute = Path.Combine(ProjectRoot, RigPath);
            string blendAbsolute = Path.Combine(
                ProjectRoot,
                EvidenceRoot,
                "pack-opening-gate04-r013.blend");
            string json =
                "{\n"
                + "  \"schema\": \"premium-display-case-gate04-r013-unity-source.v1\",\n"
                + "  \"unity\": \"6000.5.6f1\",\n"
                + "  \"urp\": \"17.5.0\",\n"
                + $"  \"scene\": \"{ScenePath}\",\n"
                + $"  \"packOnlyRig\": \"{RigPath}\",\n"
                + $"  \"packOnlyRigSha256\": \"{Sha256File(rigAbsolute)}\",\n"
                + $"  \"blendSha256\": \"{Sha256File(blendAbsolute)}\",\n"
                + "  \"runtimeRepresentation\": \"FBX relative blend shapes driven by normalized drag progress\",\n"
                + "  \"realPackCanvas\": [384, 512],\n"
                + "  \"longitudinalTearColumns\": 96,\n"
                + "  \"shapeSamples\": [0, 0.15, 0.35, 0.55, 0.75, 1.0],\n"
                + "  \"assembledCaseInstances\": 1,\n"
                + "  \"caseGeometryIncludedInRig\": false,\n"
                + "  \"caseRenderedOrBaked\": false,\n"
                + "  \"physicalMouth\": \"front foil, rear rim, narrow liner, moving and tab side gussets, rolled front contact lip\",\n"
                + "  \"vfxGraph\": false,\n"
                + "  \"shuriken\": true,\n"
                + "  \"sampleModelsImported\": false,\n"
                + "  \"sampleArtworkImported\": false,\n"
                + "  \"shippingRuntimeWired\": false,\n"
                + "  \"nativeUiWired\": false,\n"
                + "  \"shippingReady\": false,\n"
                + "  \"physicalPhoneInstalled\": false\n"
                + "}\n";
            File.WriteAllText(
                Path.Combine(ProjectRoot, EvidenceRoot, "unity-source-manifest.json"),
                json);
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

            if (!string.Equals(
                    Sha256File(source),
                    expectedHash,
                    StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(
                    $"Source hash mismatch for {sourceRelative}.");
            }

            if (!File.Exists(destination)
                || !string.Equals(
                    Sha256File(destination),
                    expectedHash,
                    StringComparison.OrdinalIgnoreCase))
            {
                File.Copy(source, destination, true);
            }

            AssertHash(destinationRelative, expectedHash);
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
            return string.Concat(sha.ComputeHash(stream).Select(
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
                Material back,
                Material inner,
                Material contact,
                Material stripFront,
                Material stripUnder,
                Material cutEdge,
                Material rim,
                Material flareSweep,
                Material flareAccent,
                Material environment)
            {
                Pack = pack;
                Back = back;
                Inner = inner;
                Contact = contact;
                StripFront = stripFront;
                StripUnder = stripUnder;
                CutEdge = cutEdge;
                Rim = rim;
                FlareSweep = flareSweep;
                FlareAccent = flareAccent;
                Environment = environment;
            }

            public Material Pack { get; }
            public Material Back { get; }
            public Material Inner { get; }
            public Material Contact { get; }
            public Material StripFront { get; }
            public Material StripUnder { get; }
            public Material CutEdge { get; }
            public Material Rim { get; }
            public Material FlareSweep { get; }
            public Material FlareAccent { get; }
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
