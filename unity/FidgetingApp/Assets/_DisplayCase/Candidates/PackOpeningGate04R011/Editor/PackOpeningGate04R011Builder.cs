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
using UnityEngine.Playables;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using UnityEngine.Timeline;

namespace FidgetingApp.DisplayCase.Candidates.Editor
{
    public static class PackOpeningGate04R011Builder
    {
        public const string CandidateRoot =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R011";
        public const string ScenePath =
            CandidateRoot + "/Scenes/PackOpeningGate04R011.unity";
        public const string ProfilePath =
            CandidateRoot + "/Profiles/PackOpeningGate04R011Profile.asset";
        public const string TimelinePath =
            CandidateRoot + "/Timelines/MakeItShineRetargetedR011.playable";
        public const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-011";
        public const string EvidenceIterationRoot =
            EvidenceRoot + "/iterations/iteration-12";
        public const string PackBodyPath =
            "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png";
        public const string PackFlapPath =
            "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png";
        public const string ActualCasePrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab";
        public const string ActualPrizePrefabPath =
            "Assets/Resources/Gacha/ThreeBladeDisplayPrize.prefab";
        public const string ShippingEnvironmentTexturePath =
            "Assets/Resources/EnvironmentBackgrounds/canyon-unified-ledgestone-v1-2x.png";
        public const string ShippingEnvironmentMaterialPath =
            "Assets/Resources/EnvironmentBackgrounds/EnvironmentParallaxMaterial.mat";
        public const string SourceDiscardClipPath =
            CandidateRoot + "/ImportedSource/Animation/Booster_Discarded.anim";
        public const string SourceFlareTexturePath =
            CandidateRoot + "/ImportedSource/Textures/TX_Flare_2x2_M.png";
        public const string SourceNoiseTexturePath =
            CandidateRoot + "/ImportedSource/Textures/TX_Noise_M.tga";
        public const string SourceSelectedGraphPath =
            CandidateRoot + "/ImportedSource/ShaderGraphs/SG_SelectedBooster.shadergraph";
        public const string SourceLightingImportedGraphPath =
            CandidateRoot + "/ImportedSource/ShaderGraphs/SG_LightingStrike.shadergraph";
        public const string SourceCardMaskGraphPath =
            CandidateRoot + "/ImportedSource/ShaderGraphs/CardMask.shadergraph";

        private const string MaterialRoot = CandidateRoot + "/Generated/Materials";
        private const string ExpectedPackBodySha256 =
            "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6";
        private const string ExpectedPackFlapSha256 =
            "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49";
        private const string ExpectedCasePrefabSha256 =
            "7a96aae6245b5a1d5463dabc3cb4518af8693ba8f8328ad9f2fe4ee6c6a67e2c";
        private const string ExpectedPrizePrefabSha256 =
            "d68f51b0034199987fa9e0cd44a8e3ba351b70b4289ff4773edc296e9395a8e1";
        private const string ExpectedEnvironmentTextureSha256 =
            "ed1fc13c9419f350fd772e31f505cabe016995e17c06c576c873b19a2a526d5d";
        private const string ExpectedEnvironmentMaterialSha256 =
            "0ead2d5373447be0c5b7d3e12c96962146bf4128741f2070d7348132401a738a";
        private const string SourceTimelineSha256 =
            "baec0abcf084db64a2b353947a9e67408e6b41ec27d5c645621d8f93aec9b086";
        private const string SourceDiscardSha256 =
            "be661fe81b095f7f1ad08fb2a1c003b15f8690ee08d43f9f705dc849924fb2c6";
        private const string SourceBoosterGraphSha256 =
            "e1de0669f3f7c8ade21f656ab17c5e14e6d45cd5e689c79ddb983f27e61f6c34";
        private const string SourceSelectedGraphSha256 =
            "75eb59c320c80b693d24d61df3c9238a8670cef64f73247727558e6db512308b";
        private const string SourceLightingGraphSha256 =
            "a4eb3922e72a3dadb436902d2c4a57c3fbd6768e4b137104abeed6167e1f4f7d";
        private const string SourceTitleGraphSha256 =
            "6a7718d6ae1eba360c03a1ea16b207ada5ae80f1a4dc2df0d004453bf94e2067";
        private const string SourceCardMaskSha256 =
            "20bf26a2efe854ee561cbdca77697c63651124ca3c095185837885984f19234c";
        private const string SourceExplosionVfxSha256 =
            "d6af66e7b91e7097d50fbef376bf7b33b63dd9e6738a4c99084cb46460aaac2f";
        private const string SourceLightingVfxSha256 =
            "4f4da1d0038cee4e4599467b754a429263286073233bb8ac0f259e908635d7b5";
        private const string SourceActivationVfxSha256 =
            "c56ed7a46cc1276b16e5e6e47879e4c7a665425df9d8e2e6693ac8ef1924ff67";
        private const string SourceFlareSha256 =
            "bbf7c86f5435ec3097717ef092e531214916e9cbb7db2b71f059e3d12f90ffa3";
        private const string SourceNoiseSha256 =
            "2303e1fb3c86af9e9b6a4ccd4ecb615b9cdd172253eea8988c7a6ac4a165e886";
        private const string SourceBaseMaterialSha256 =
            "bfa2402ca04c1234a46b5eae70106765e8463af0aa7660a826c1c64487efe385";
        private const string SourceVariantMaterialSha256 =
            "509561d9751a7cf69db654129b3994c0d9da58a3a8d1ebb7cfdb8a3fdd87bf96";

        [MenuItem("Fidgeting/Display Case/Gate 04 R011/Build And Capture")]
        public static void BuildAndRunCapture()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                throw new InvalidOperationException(
                    "Unity is already entering or running PlayMode.");
            }
            BuildSceneInternal();
            Debug.Log(
                "GATE04_R011_CC0_REUSE_CAPTURE_READY "
                + $"scene={ScenePath} output={EvidenceRoot}");
            EditorApplication.isPlaying = true;
        }

        [MenuItem("Fidgeting/Display Case/Gate 04 R011/Build Scene Only")]
        public static void BuildSceneOnly()
        {
            BuildSceneInternal();
            Debug.Log($"Gate 04 rev 11 candidate scene built at {ScenePath}.");
        }

        private static void BuildSceneInternal()
        {
            AssertEngineContract();
            EnsureDirectories();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            AssertSourceAssets();
            PackOpeningGate04R011Profile profile = CreateProfile();
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
                    $"Gate 04 rev 11 requires Unity 6000.5.6f1, got {Application.unityVersion}.");
            }
            UnityEditor.PackageManager.PackageInfo urp =
                UnityEditor.PackageManager.PackageInfo.FindForAssetPath(
                    "Packages/com.unity.render-pipelines.universal");
            if (urp == null || urp.version != "17.5.0")
            {
                throw new InvalidOperationException(
                    $"Gate 04 rev 11 requires URP 17.5.0, got {urp?.version ?? "missing"}.");
            }
        }

        private static void EnsureDirectories()
        {
            foreach (string directory in new[]
                     {
                         CandidateRoot + "/Scenes",
                         CandidateRoot + "/Profiles",
                         CandidateRoot + "/Timelines",
                         MaterialRoot,
                         EvidenceRoot,
                         EvidenceIterationRoot,
                         EvidenceIterationRoot + "/frames"
                     })
            {
                Directory.CreateDirectory(Path.Combine(ProjectRoot, directory));
            }
        }

        private static void AssertSourceAssets()
        {
            AssertHash(PackBodyPath, ExpectedPackBodySha256);
            AssertHash(PackFlapPath, ExpectedPackFlapSha256);
            AssertHash(ActualCasePrefabPath, ExpectedCasePrefabSha256);
            AssertHash(ActualPrizePrefabPath, ExpectedPrizePrefabSha256);
            AssertHash(
                ShippingEnvironmentTexturePath,
                ExpectedEnvironmentTextureSha256);
            AssertHash(
                ShippingEnvironmentMaterialPath,
                ExpectedEnvironmentMaterialSha256);
            AssertHash(SourceDiscardClipPath, SourceDiscardSha256);
            AssertHash(SourceFlareTexturePath, SourceFlareSha256);
            AssertHash(SourceNoiseTexturePath, SourceNoiseSha256);
            AssertHash(SourceSelectedGraphPath, SourceSelectedGraphSha256);
            AssertHash(
                SourceLightingImportedGraphPath,
                SourceLightingGraphSha256);
            AssertHash(SourceCardMaskGraphPath, SourceCardMaskSha256);
            AssertHash(
                EvidenceRoot + "/source-raw/Booster to Card Timeline.playable",
                SourceTimelineSha256);
            AssertHash(
                EvidenceRoot + "/source-raw/SG_BoosterPack.shadergraph",
                SourceBoosterGraphSha256);
            AssertHash(
                EvidenceRoot + "/source-raw/SG_LightingStrike.shadergraph",
                SourceLightingGraphSha256);
            AssertHash(
                EvidenceRoot + "/source-raw/SG_Title_Kyle.shadergraph",
                SourceTitleGraphSha256);
            AssertHash(
                EvidenceRoot + "/source-raw/VFX_BoosterExplosion.vfx",
                SourceExplosionVfxSha256);
            AssertHash(
                EvidenceRoot + "/source-raw/VFXG_LightingStrike.vfx",
                SourceLightingVfxSha256);
            AssertHash(
                EvidenceRoot + "/source-raw/VFX_BoosterActivation.vfx",
                SourceActivationVfxSha256);
            AssertPngDimensions(PackBodyPath, 384, 512);
            AssertPngDimensions(PackFlapPath, 384, 512);
        }

        private static PackOpeningGate04R011Profile CreateProfile()
        {
            PackOpeningGate04R011Profile profile =
                AssetDatabase.LoadAssetAtPath<PackOpeningGate04R011Profile>(
                    ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<
                    PackOpeningGate04R011Profile>();
                AssetDatabase.CreateAsset(profile, ProfilePath);
            }
            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static MaterialSet CreateMaterials()
        {
            Shader lit = RequireShader("Universal Render Pipeline/Lit");
            Shader alpha = RequireShader(
                "FidgetingApp/Candidates/OpeningAccentR011");
            Shader packShader = RequireShader(
                "FidgetingApp/Candidates/MakeItShineCc0PackR011");
            Shader sourceEffectShader = RequireShader(
                "FidgetingApp/Candidates/MakeItShineCc0PortR011");
            Shader sourceLightingShader = RequireShader(
                "Shader Graphs/SG_LightingStrike");
            Texture2D packBody = RequireTexture(PackBodyPath);
            Texture2D packFlap = RequireTexture(PackFlapPath);
            Texture2D sourceNoise = RequireTexture(SourceNoiseTexturePath);
            Texture2D sourceFlare = RequireTexture(SourceFlareTexturePath);

            Material body = CreateMaterial(
                "Gate04R011RealPackSourceDissolve",
                packShader,
                material =>
                {
                    material.SetTexture("_BaseMap", packBody);
                    material.SetTexture("_NoiseMap", sourceNoise);
                    material.SetColor("_BaseColor", Color.white);
                    material.SetFloat("_Dissolve", 0f);
                    material.SetFloat("_DissolveScale", 0.05f);
                    // The audited SG_BoosterPack discard edge is the approved
                    // identity carrier, so it has to out-read the particle port.
                    // A wide band here degenerated into flat horizontal
                    // rectangles at mid dissolve, so the width is back to a thin
                    // line and the contour-space sweep below carries the read.
                    material.SetFloat("_EdgeWidth", 0.022f);
                    material.SetFloat("_EdgeStrength", 0.54f);
                    material.SetColor(
                        "_EdgeColor",
                        new Color(1f, 0.94f, 0.82f, 1f));
                    material.SetFloat("_DissolveJitter", 0.052f);
                    material.SetFloat("_TearSweep", 0f);
                    material.SetFloat("_TearEdgeWidth", 0.105f);
                    material.SetColor(
                        "_TearEdgeColor",
                        new Color(0.96f, 0.86f, 0.70f, 1f));
                    material.SetFloat("_TearEdgeStrength", 0.38f);
                    material.SetFloat("_TearFrontBoost", 0.80f);
                    material.renderQueue = 2460;
                });
            // Metallic 0.72 / smoothness 0.58 resolved the freed band as one
            // hard chrome sheet. Foil is a rougher, less mirror-like surface, so
            // the highlight breaks up across the curl instead of forming a
            // single blade-shaped specular.
            Material stripFront = CreateMaterial(
                "Gate04R011RealPackFoilFront",
                lit,
                material => ConfigureLitTexture(
                    material,
                    packFlap,
                    Color.white,
                    0.10f,
                    0.12f));
            Material stripUnderside = CreateLitMaterial(
                "Gate04R011FoilDarkUnderside",
                lit,
                new Color(0.065f, 0.061f, 0.056f, 1f),
                0.10f,
                0.10f);
            Material stripEdge = CreateLitMaterial(
                "Gate04R011FoilThinEdge",
                lit,
                new Color(0.18f, 0.170f, 0.155f, 1f),
                0.12f,
                0.16f);
            // Iteration 08 brightened this because a near-black interior read as
            // a void behind a paper cutout. The cause was a missing volume, not
            // the value: there was no back wall, no side wall and no lip. With a
            // real mouth the interior must go back to reading as a recess, or the
            // opening looks like a lit panel instead of a cavity.
            Material cavity = CreateLitMaterial(
                "Gate04R011ShapedInnerFoil",
                lit,
                new Color(0.048f, 0.046f, 0.043f, 1f),
                0.18f,
                0.16f);
            // The band directly behind the torn lip is occluded by the front
            // face. Painting it separately is what turns a flat interior into a
            // readable recess and silhouettes the concealed case against the
            // deeper wall.
            Material cavityContact = CreateLitMaterial(
                "Gate04R011InnerFoilContactOcclusion",
                lit,
                new Color(0.008f, 0.008f, 0.007f, 1f),
                0.05f,
                0.08f);
            Material contactShadow = CreateAlphaMaterial(
                "Gate04R011RestrainedContactShadow",
                alpha,
                new Color(0.005f, 0.006f, 0.007f, 0.24f));
            Material stripSpecular = CreateAlphaMaterial(
                "Gate04R011MovingNarrowSpecular",
                alpha,
                new Color(1f, 0.93f, 0.78f, 0.07f));
            Material activation = CreateSourceEffectMaterial(
                "Gate04R011SourceActivationGlow",
                sourceEffectShader,
                sourceFlare,
                new Color(0.70f, 0.84f, 1f, 0.22f),
                0.72f);
            activation.SetTextureScale("_BaseMap", new Vector2(0.5f, 0.5f));
            // The bottom-left cell is a symmetric cross, which also reads as a
            // sparkle glyph. Use the horizontal streak cell instead.
            activation.SetTextureOffset("_BaseMap", new Vector2(0.5f, 0f));
            Material lightning = CreateMaterial(
                "Gate04R011SourceLightning",
                sourceLightingShader,
                material =>
                {
                    material.SetTexture(
                        "_SampleTexture2D_721830d4e32b499f825cd95f292dd123_Texture_1_Texture2D",
                        sourceFlare);
                    // This material was the only one still addressing the atlas
                    // cell that holds the four-point star, via a _BaseMap tiling
                    // left over from an earlier iteration. Point it at the
                    // horizontal streak cell like every other port.
                    material.SetTexture("_BaseMap", sourceFlare);
                    material.SetTextureScale(
                        "_BaseMap",
                        new Vector2(0.5f, 0.5f));
                    material.SetTextureOffset(
                        "_BaseMap",
                        new Vector2(0.5f, 0f));
                    // At 0.56 the 25 trails read as a decorative star cluster
                    // and out-competed the Pack and case.
                    material.SetColor(
                        "_Color",
                        new Color(0.86f, 0.92f, 1f, 0.26f));
                    material.SetFloat("_Reveal", 1f);
                    material.SetFloat("_Erode", 0.02f);
                    material.SetFloat("_Speed", 0f);
                    material.SetFloat("_Size", 0.12f);
                    material.SetFloat("_ErosionScale", 1f);
                    material.renderQueue = 3020;
                });
            Material lightningSparks = CreateSourceEffectMaterial(
                "Gate04R011SourceLightningSparks",
                sourceEffectShader,
                sourceFlare,
                new Color(0.55f, 0.75f, 1f, 0.012f),
                0.35f);
            lightningSparks.SetTextureScale(
                "_BaseMap",
                new Vector2(0.5f, 0.5f));
            lightningSparks.SetTextureOffset(
                "_BaseMap",
                new Vector2(0.5f, 0f));
            Material explosionDust = CreateSourceEffectMaterial(
                "Gate04R011SourceExplosionDust",
                sourceEffectShader,
                sourceFlare,
                new Color(0.62f, 0.55f, 0.48f, 0.24f),
                0.46f);
            explosionDust.SetTextureScale("_BaseMap", new Vector2(0.5f, 0.5f));
            explosionDust.SetTextureOffset("_BaseMap", new Vector2(0f, 0.5f));
            // The other ports select one quadrant of the source 2x2 atlas via
            // tiling. This one had no tiling, so every flare billboard sampled
            // all four quadrants at once and drew the four-point star in the
            // top-right cell. Quadrant (0.5, 0) is the horizontal streak.
            Material explosionFlares = CreateSourceEffectMaterial(
                "Gate04R011SourceExplosionFlares",
                sourceEffectShader,
                sourceFlare,
                new Color(1f, 0.98f, 0.94f, 0.44f),
                1.18f);
            explosionFlares.SetTextureScale("_BaseMap", new Vector2(0.5f, 0.5f));
            explosionFlares.SetTextureOffset(
                "_BaseMap",
                new Vector2(0.5f, 0f));
            Material environment =
                AssetDatabase.LoadAssetAtPath<Material>(
                    ShippingEnvironmentMaterialPath);
            if (environment == null)
            {
                throw new MissingReferenceException(
                    $"Missing {ShippingEnvironmentMaterialPath}");
            }
            return new MaterialSet(
                body,
                stripFront,
                stripUnderside,
                stripEdge,
                cavity,
                cavityContact,
                contactShadow,
                stripSpecular,
                activation,
                lightning,
                lightningSparks,
                explosionDust,
                explosionFlares,
                environment);
        }

        private static Scene BuildScene(
            PackOpeningGate04R011Profile profile,
            MaterialSet materials)
        {
            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            Camera camera = BuildCamera();
            Texture2D environmentTexture = RequireTexture(
                ShippingEnvironmentTexturePath);
            Renderer environmentRenderer = BuildEnvironment(
                materials.Environment);
            BuildLighting();
            PremiumDisplayCaseShippingPresentation presentation =
                BuildActualCase(out Transform caseMotionRoot);
            BuildPack(
                materials,
                out Transform packRoot,
                out MeshFilter bodyFilter,
                out Renderer bodyRenderer,
                out MeshFilter stripFilter,
                out Renderer stripRenderer,
                out MeshFilter cavityFilter,
                out Renderer cavityRenderer,
                out MeshFilter contactShadowFilter,
                out Renderer contactShadowRenderer,
                out MeshFilter specularFilter,
                out Renderer specularRenderer);
            SourceEffects effects = BuildSourceEffects(materials);

            var controllerObject = new GameObject(
                "PackOpeningGate04R011Controller");
            var controller =
                controllerObject.AddComponent<PackOpeningGate04R011Controller>();
            controller.Configure(
                profile,
                camera,
                environmentRenderer,
                environmentTexture,
                packRoot,
                bodyFilter,
                bodyRenderer,
                stripFilter,
                stripRenderer,
                cavityFilter,
                cavityRenderer,
                contactShadowFilter,
                contactShadowRenderer,
                specularFilter,
                specularRenderer,
                caseMotionRoot,
                presentation,
                effects.Activation,
                effects.LightningStrips,
                effects.LightningSparks,
                effects.ExplosionDust,
                effects.ExplosionFlares);
            PlayableDirector director = controllerObject.AddComponent<
                PlayableDirector>();
            director.playableAsset = CreateAdaptedTimeline(
                director,
                packRoot.gameObject,
                caseMotionRoot.gameObject,
                effects);
            director.timeUpdateMode = DirectorUpdateMode.Manual;
            director.extrapolationMode = DirectorWrapMode.Hold;
            director.time = 0d;
            director.Evaluate();

            string evidenceAbsolute = Path.Combine(
                ProjectRoot,
                EvidenceIterationRoot);
            string sourceCaptureAbsolute = Path.Combine(
                ProjectRoot,
                EvidenceRoot,
                "source-captures");
            var captureObject = new GameObject("RealUnityPlayModeCaptureR011");
            var capture =
                captureObject.AddComponent<PackOpeningGate04R011Capture>();
            capture.Configure(
                camera,
                controller,
                director,
                evidenceAbsolute,
                ScenePath,
                sourceCaptureAbsolute);
            Selection.activeGameObject = controllerObject;
            return scene;
        }

        private static Camera BuildCamera()
        {
            var item = new GameObject("Gate04R011ShippingPortraitCamera");
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

        private static Renderer BuildEnvironment(Material material)
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
            return renderer;
        }

        private static void BuildLighting()
        {
            // The Pack body renders unlit, so the URP Lit case needs enough key
            // and ambient to read as the same product through the aperture.
            CreateDirectionalLight(
                "PremiumNeutralKey",
                Quaternion.Euler(32f, -28f, 0f),
                new Color(1f, 0.93f, 0.84f),
                2.55f,
                0.42f);
            CreateDirectionalLight(
                "CoolMineralFill",
                Quaternion.Euler(56f, 145f, 0f),
                new Color(0.64f, 0.71f, 0.78f),
                0.96f,
                0.24f);
            CreateDirectionalLight(
                "ControlledMetalRim",
                Quaternion.Euler(18f, 212f, 0f),
                new Color(0.94f, 0.90f, 0.82f),
                1.34f,
                0.30f);
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.290f, 0.305f, 0.320f);
            RenderSettings.ambientEquatorColor = new Color(0.175f, 0.182f, 0.188f);
            RenderSettings.ambientGroundColor = new Color(0.062f, 0.062f, 0.058f);
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
                * PackOpeningGate04R011Controller.CaseScale;
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
            out MeshFilter bodyFilter,
            out Renderer bodyRenderer,
            out MeshFilter stripFilter,
            out Renderer stripRenderer,
            out MeshFilter cavityFilter,
            out Renderer cavityRenderer,
            out MeshFilter contactShadowFilter,
            out Renderer contactShadowRenderer,
            out MeshFilter specularFilter,
            out Renderer specularRenderer)
        {
            var root = new GameObject("ActualAuthoredStandardPackOccluder");
            packRoot = root.transform;
            packRoot.position = new Vector3(0f, 0.015f, -0.180f);
            GameObject body = CreateDynamicMeshObject(
                packRoot,
                "PhysicalPackBodyOccluder",
                materials.PackBody);
            bodyFilter = body.GetComponent<MeshFilter>();
            bodyRenderer = body.GetComponent<MeshRenderer>();
            GameObject strip = CreateDynamicMeshObject(
                packRoot,
                "SubdividedDeformableFoilStrip",
                materials.StripFront);
            stripFilter = strip.GetComponent<MeshFilter>();
            stripRenderer = strip.GetComponent<MeshRenderer>();
            stripRenderer.sharedMaterials = new[]
            {
                materials.StripFront,
                materials.StripUnderside,
                materials.StripEdge
            };
            GameObject cavity = CreateDynamicMeshObject(
                packRoot,
                "ShapedInnerFoilCavity",
                materials.Cavity);
            cavityFilter = cavity.GetComponent<MeshFilter>();
            cavityRenderer = cavity.GetComponent<MeshRenderer>();
            cavityRenderer.sharedMaterials = new[]
            {
                materials.Cavity,
                materials.CavityContact
            };
            GameObject shadow = CreateDynamicMeshObject(
                packRoot,
                "RestrainedStripContactShadow",
                materials.ContactShadow);
            contactShadowFilter = shadow.GetComponent<MeshFilter>();
            contactShadowRenderer = shadow.GetComponent<MeshRenderer>();
            contactShadowRenderer.shadowCastingMode = ShadowCastingMode.Off;
            GameObject specular = CreateDynamicMeshObject(
                packRoot,
                "MovingNarrowFoilSpecular",
                materials.StripSpecular);
            specularFilter = specular.GetComponent<MeshFilter>();
            specularRenderer = specular.GetComponent<MeshRenderer>();
            specularRenderer.shadowCastingMode = ShadowCastingMode.Off;
        }

        private static SourceEffects BuildSourceEffects(MaterialSet materials)
        {
            var root = new GameObject("AuditedMakeItShineCc0ShurikenPort");
            root.transform.position = new Vector3(0f, 0.070f, -0.105f);
            ParticleSystem activation = CreateSourceSystem(
                root.transform,
                "VFX_BoosterActivation_ShuriKenPort",
                materials.Activation,
                3,
                2.20f,
                new Vector2(0.018f, 0.035f),
                new Vector2(0f, 0.015f),
                1907u,
                SourceParticleKind.Activation);
            ParticleSystem lightningStrips = CreateSourceSystem(
                root.transform,
                "VFXG_LightingStrike_25Strips_ShuriKenPort",
                materials.Lightning,
                25,
                0.42f,
                new Vector2(0.0015f, 0.0030f),
                new Vector2(0.08f, 0.16f),
                772u,
                SourceParticleKind.LightningTrail);
            ParticleSystem lightningSparks = CreateSourceSystem(
                root.transform,
                "VFXG_LightingStrike_512Sparks_ShuriKenPort",
                materials.LightningSparks,
                512,
                0.38f,
                new Vector2(0.0005f, 0.0015f),
                new Vector2(0.06f, 0.16f),
                2371u,
                SourceParticleKind.Spark);
            ParticleSystem explosionDust = CreateSourceSystem(
                root.transform,
                "VFX_BoosterExplosion_512Quads_ShuriKenPort",
                materials.ExplosionDust,
                512,
                0.82f,
                new Vector2(0.0004f, 0.0018f),
                new Vector2(0.22f, 0.75f),
                3190u,
                SourceParticleKind.Dust);
            ParticleSystem explosionFlares = CreateSourceSystem(
                root.transform,
                "VFX_BoosterExplosion_16Flares_ShuriKenPort",
                materials.ExplosionFlares,
                16,
                0.58f,
                new Vector2(0.022f, 0.068f),
                new Vector2(0.02f, 0.11f),
                4193u,
                SourceParticleKind.Flare);
            return new SourceEffects(
                activation,
                lightningStrips,
                lightningSparks,
                explosionDust,
                explosionFlares);
        }

        private static ParticleSystem CreateSourceSystem(
            Transform parent,
            string name,
            Material material,
            short count,
            float lifetime,
            Vector2 size,
            Vector2 speed,
            uint seed,
            SourceParticleKind kind)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            ParticleSystem system = item.AddComponent<ParticleSystem>();
            ParticleSystem.MainModule main = system.main;
            main.loop = false;
            main.playOnAwake = false;
            // Flares carry the audited crimson-purple-cyan colour-over-lifetime
            // sequence. A narrow lifetime spread put all 16 at the same gradient
            // position every frame, which read as one uniform-hue orb rather
            // than the source's mixed warm and cool flare field.
            main.duration = kind == SourceParticleKind.Flare ? 0.12f : 0.05f;
            main.startLifetime = new ParticleSystem.MinMaxCurve(
                lifetime * (kind == SourceParticleKind.Flare ? 0.26f : 0.58f),
                lifetime);
            main.startSpeed = new ParticleSystem.MinMaxCurve(speed.x, speed.y);
            main.startSize = new ParticleSystem.MinMaxCurve(size.x, size.y);
            if (kind == SourceParticleKind.Activation)
            {
                main.startSize3D = true;
                main.startSizeX = new ParticleSystem.MinMaxCurve(0.28f, 0.42f);
                main.startSizeY = new ParticleSystem.MinMaxCurve(
                    size.x,
                    size.y);
                main.startSizeZ = new ParticleSystem.MinMaxCurve(1f);
            }
            if (kind == SourceParticleKind.Spark)
            {
                main.startSize3D = true;
                main.startSizeX = new ParticleSystem.MinMaxCurve(0.006f, 0.012f);
                main.startSizeY = new ParticleSystem.MinMaxCurve(
                    0.00035f,
                    0.0008f);
                main.startSizeZ = new ParticleSystem.MinMaxCurve(1f);
            }
            if (kind == SourceParticleKind.Flare)
            {
                // Every cell of the source atlas is a four-armed glyph; none is
                // a pure horizontal streak. Flattening the billboard compresses
                // the vertical arm and stretches the horizontal one, so the
                // unmodified source texture reads as a streak instead of a
                // sparkle. This is a port aspect change, not a texture edit.
                main.startSize3D = true;
                main.startSizeX = new ParticleSystem.MinMaxCurve(
                    size.x * 1.55f,
                    size.y * 1.55f);
                main.startSizeY = new ParticleSystem.MinMaxCurve(
                    size.x * 0.16f,
                    size.y * 0.16f);
                main.startSizeZ = new ParticleSystem.MinMaxCurve(1f);
            }
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.maxParticles = count;
            main.gravityModifier = kind == SourceParticleKind.Spark
                ? 0.06f
                : 0f;
            main.startColor = SourceColor(kind);
            ParticleSystem.EmissionModule emission = system.emission;
            emission.rateOverTime = 0f;
            emission.SetBursts(
                kind == SourceParticleKind.Flare
                    ? new[]
                    {
                        new ParticleSystem.Burst(0f, (short)(count / 2)),
                        new ParticleSystem.Burst(
                            0.045f,
                            (short)(count - count / 2 - count / 4)),
                        new ParticleSystem.Burst(0.090f, (short)(count / 4))
                    }
                    : new[] { new ParticleSystem.Burst(0f, count) });
            ParticleSystem.ShapeModule shape = system.shape;
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Sphere;
            shape.radius = kind == SourceParticleKind.Activation
                ? 0.085f
                : kind == SourceParticleKind.Flare
                    ? 0.034f
                    : kind == SourceParticleKind.LightningTrail
                        ? 0.012f
                        : kind == SourceParticleKind.Spark
                            ? 0.010f
                            : 0.025f;
            shape.radiusThickness =
                kind == SourceParticleKind.Activation
                || kind == SourceParticleKind.Flare
                    ? 1f
                    : 0f;
            ParticleSystem.VelocityOverLifetimeModule velocity =
                system.velocityOverLifetime;
            velocity.enabled = kind != SourceParticleKind.Activation;
            velocity.space = ParticleSystemSimulationSpace.World;
            velocity.z = new ParticleSystem.MinMaxCurve(-0.025f, 0.035f);
            ParticleSystem.NoiseModule noise = system.noise;
            noise.enabled = kind == SourceParticleKind.LightningTrail;
            noise.strength = new ParticleSystem.MinMaxCurve(0.06f, 0.14f);
            noise.frequency = 3f;
            noise.scrollSpeed = 0.5f;
            ParticleSystem.ColorOverLifetimeModule color = system.colorOverLifetime;
            color.enabled = true;
            color.color = new ParticleSystem.MinMaxGradient(
                SourceLifetimeGradient(kind));
            ParticleSystem.SizeOverLifetimeModule sizeOverLifetime =
                system.sizeOverLifetime;
            sizeOverLifetime.enabled = true;
            sizeOverLifetime.size = new ParticleSystem.MinMaxCurve(
                1f,
                SourceSizeCurve(kind));
            ParticleSystem.RotationOverLifetimeModule rotation =
                system.rotationOverLifetime;
            // The streak cell of the source atlas is a horizontally dominant
            // cross. Spinning it made every particle sweep through the angles
            // that read as a four-point star, which is why changing the atlas
            // cell alone did not remove the sparkle glyphs. Only the radial glow
            // cell is safe to rotate.
            rotation.enabled = kind == SourceParticleKind.Dust;
            rotation.z = new ParticleSystem.MinMaxCurve(-2.4f, 2.4f);
            if (kind != SourceParticleKind.Dust)
            {
                // A narrow spread keeps the streaks from looking stamped without
                // ever reaching a symmetric star angle.
                main.startRotation = new ParticleSystem.MinMaxCurve(
                    -0.21f,
                    0.21f);
            }
            ParticleSystemRenderer renderer =
                item.GetComponent<ParticleSystemRenderer>();
            renderer.sharedMaterial = material;
            renderer.renderMode = ParticleSystemRenderMode.Billboard;
            renderer.alignment = ParticleSystemRenderSpace.View;
            renderer.sortingOrder = 6;
            if (kind == SourceParticleKind.LightningTrail)
            {
                ParticleSystem.TrailModule trails = system.trails;
                trails.enabled = true;
                trails.mode = ParticleSystemTrailMode.PerParticle;
                trails.ratio = 1f;
                trails.lifetime = 0.12f;
                trails.dieWithParticles = true;
                trails.sizeAffectsWidth = true;
                trails.widthOverTrail = new ParticleSystem.MinMaxCurve(
                    1f,
                    AnimationCurve.EaseInOut(0f, 0f, 0.18f, 1f));
                renderer.trailMaterial = material;
                renderer.renderMode = ParticleSystemRenderMode.None;
            }
            if (kind == SourceParticleKind.Spark)
            {
                // A short stretch on the soft source flare tile produced hard
                // arrowhead glyphs at close-up framing. A long thin streak keeps
                // the source texture family without reading as a UI marker.
                renderer.renderMode = ParticleSystemRenderMode.Stretch;
                renderer.cameraVelocityScale = 0f;
                renderer.velocityScale = 0.055f;
                renderer.lengthScale = 4.2f;
            }
            if (kind == SourceParticleKind.Flare)
            {
                // Quadrant selection is done by the material's tiling, the same
                // way every other source port does it. Leaving sheet animation
                // on as well fought that tiling and let the four-point star cell
                // reappear.
                ParticleSystem.TextureSheetAnimationModule sheet =
                    system.textureSheetAnimation;
                sheet.enabled = false;
            }
            system.useAutoRandomSeed = false;
            system.randomSeed = seed;
            system.Stop(
                true,
                ParticleSystemStopBehavior.StopEmittingAndClear);
            return system;
        }

        private static ParticleSystem.MinMaxGradient SourceColor(
            SourceParticleKind kind)
        {
            switch (kind)
            {
                case SourceParticleKind.Activation:
                    return new ParticleSystem.MinMaxGradient(
                        new Color(0.70f, 0.84f, 1f, 0.16f),
                        new Color(0.94f, 0.98f, 1f, 0.30f));
                case SourceParticleKind.Flare:
                    // The audited crimson-purple-cyan sequence is carried by
                    // SourceLifetimeGradient. Randomising it here instead made
                    // all 16 deterministic flares average to one magenta orb.
                    return new ParticleSystem.MinMaxGradient(
                        new Color(1f, 0.97f, 0.92f, 0.62f),
                        new Color(1f, 1f, 1f, 0.74f));
                default:
                    return new ParticleSystem.MinMaxGradient(
                        new Color(0.20f, 0.18f, 0.16f, 0.20f),
                        new Color(0.46f, 0.40f, 0.34f, 0.34f));
            }
        }

        private static Gradient SourceLifetimeGradient(SourceParticleKind kind)
        {
            var gradient = new Gradient();
            gradient.SetKeys(
                kind == SourceParticleKind.Flare
                    // The source sequence is crimson -> purple -> saturated cyan
                    // -> pale cyan. The purple key and the saturated cyan key are
                    // what produced the magenta smudge and the cyan sparkles, and
                    // desynchronising emission only spread them thinner. Both
                    // hues are excluded here. The source's warm-to-cool travel
                    // and its key positions are kept, so the flare still reads as
                    // the audited effect rather than a new one.
                    ? new[]
                    {
                        new GradientColorKey(
                            new Color(0.988f, 0.320f, 0.242f),
                            0f),
                        new GradientColorKey(
                            new Color(1f, 0.760f, 0.560f),
                            0.333333f),
                        new GradientColorKey(
                            new Color(1f, 0.968f, 0.920f),
                            0.666667f),
                        new GradientColorKey(
                            new Color(0.880f, 0.930f, 1f),
                            0.990311f)
                    }
                    : new[]
                    {
                        new GradientColorKey(Color.white, 0f),
                        new GradientColorKey(Color.white, 1f)
                    },
                kind == SourceParticleKind.Activation
                    ? new[]
                    {
                        new GradientAlphaKey(0f, 0f),
                        new GradientAlphaKey(1f, 0.08903639f),
                        new GradientAlphaKey(1f, 0.8749981f),
                        new GradientAlphaKey(0f, 0.8887007f)
                    }
                    : new[]
                    {
                        new GradientAlphaKey(0f, 0f),
                        new GradientAlphaKey(1f, 0.09523737f),
                        new GradientAlphaKey(0.80f, 0.80f),
                        new GradientAlphaKey(0f, 1f)
                    });
            return gradient;
        }

        private static AnimationCurve SourceSizeCurve(SourceParticleKind kind)
        {
            if (kind == SourceParticleKind.Dust)
            {
                return new AnimationCurve(
                    new Keyframe(0f, 0f, 0f, 0f),
                    new Keyframe(
                        0.13285856f,
                        1.0027729f,
                        0.13623545f,
                        0.13623545f),
                    new Keyframe(1f, 0f, 0f, 0f));
            }
            return AnimationCurve.EaseInOut(0f, 0f, 0.12f, 1f);
        }

        private static TimelineAsset CreateAdaptedTimeline(
            PlayableDirector director,
            GameObject pack,
            GameObject sameCase,
            SourceEffects effects)
        {
            if (AssetDatabase.LoadAssetAtPath<TimelineAsset>(TimelinePath) != null)
            {
                AssetDatabase.DeleteAsset(TimelinePath);
            }
            TimelineAsset timeline = ScriptableObject.CreateInstance<TimelineAsset>();
            timeline.name = "Make It Shine CC0 → Real Pack And Same Case";
            AssetDatabase.CreateAsset(timeline, TimelinePath);
            GroupTrack booster = timeline.CreateTrack<GroupTrack>(null, "Booster");
            ActivationTrack packTrack = timeline.CreateTrack<ActivationTrack>(
                booster,
                "Pack Foreground Occluder");
            TimelineClip packClip = packTrack.CreateDefaultClip();
            packClip.start = 0d;
            packClip.duration = PackOpeningGate04R011Profile.TargetProxyResultOff;
            director.SetGenericBinding(packTrack, pack);
            AddControlTrack(
                timeline,
                director,
                booster,
                "VFX_BoosterActivation → Shuriken",
                effects.Activation.gameObject,
                PackOpeningGate04R011Profile.ActivationStart,
                1.93d);
            AddControlTrack(
                timeline,
                director,
                booster,
                "VFXG_LightingStrike → Shuriken",
                effects.LightningStrips.transform.parent.gameObject,
                PackOpeningGate04R011Profile.LightningStart,
                0.60d);
            AddControlTrack(
                timeline,
                director,
                null,
                "VFX_BoosterExplosion → Shuriken",
                effects.ExplosionDust.transform.parent.gameObject,
                PackOpeningGate04R011Profile.ImpactStart,
                1.20d);
            GroupTrack result = timeline.CreateTrack<GroupTrack>(
                null,
                "Card Spawn → Existing Assembled Case");
            ActivationTrack sameCaseTrack = timeline.CreateTrack<ActivationTrack>(
                result,
                "Same Case Active From First Frame");
            TimelineClip caseClip = sameCaseTrack.CreateDefaultClip();
            caseClip.start = 0d;
            caseClip.duration = PackOpeningGate04R011Profile.TotalSeconds;
            director.SetGenericBinding(sameCaseTrack, sameCase);
            EditorUtility.SetDirty(timeline);
            return timeline;
        }

        private static void AddControlTrack(
            TimelineAsset timeline,
            PlayableDirector director,
            TrackAsset parent,
            string name,
            GameObject target,
            double start,
            double duration)
        {
            ControlTrack track = timeline.CreateTrack<ControlTrack>(parent, name);
            TimelineClip clip = track.CreateDefaultClip();
            clip.start = start;
            clip.duration = duration;
            var asset = (ControlPlayableAsset)clip.asset;
            ExposedReference<GameObject> reference = asset.sourceGameObject;
            reference.exposedName = new PropertyName(Guid.NewGuid().ToString("N"));
            asset.sourceGameObject = reference;
            asset.active = true;
            asset.updateParticle = false;
            asset.postPlayback = ActivationControlPlayable.PostPlaybackState.Revert;
            director.SetReferenceValue(reference.exposedName, target);
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
            float smoothness)
        {
            material.SetTexture("_BaseMap", texture);
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_AlphaClip", 1f);
            material.SetFloat("_Cutoff", 0.018f);
            material.EnableKeyword("_ALPHATEST_ON");
            material.renderQueue = 2470;
        }

        private static Material CreateLitMaterial(
            string name,
            Shader shader,
            Color color,
            float metallic,
            float smoothness)
        {
            return CreateMaterial(
                name,
                shader,
                material =>
                {
                    material.SetColor("_BaseColor", color);
                    material.SetFloat("_Metallic", metallic);
                    material.SetFloat("_Smoothness", smoothness);
                    material.renderQueue = 2000;
                });
        }

        private static Material CreateAlphaMaterial(
            string name,
            Shader shader,
            Color color)
        {
            return CreateMaterial(
                name,
                shader,
                material =>
                {
                    material.SetColor("_BaseColor", color);
                    material.renderQueue = 3010;
                });
        }

        private static Material CreateSourceEffectMaterial(
            string name,
            Shader shader,
            Texture texture,
            Color color,
            float intensity)
        {
            return CreateMaterial(
                name,
                shader,
                material =>
                {
                    material.SetTexture("_BaseMap", texture);
                    material.SetColor("_BaseColor", color);
                    material.SetFloat("_Reveal", 1f);
                    material.SetFloat("_Erode", 0.02f);
                    material.SetFloat("_Speed", 0.08f);
                    material.SetFloat("_Intensity", intensity);
                    material.renderQueue = 3020;
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
                "fidgeting.gacha.preview.gate04-r011-cc0-reuse.";
            var inventory = new GachaInventoryRuntime(
                prefix,
                new GachaSplitMix64(0x410011UL));
            const string request = "gate04-r011-cc0-direct-reuse";
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
                    "Could not create the authoritative rev 11 review receipt.");
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
                EvidenceIterationRoot,
                "source-to-canonical-mapping.json");
            string portShader =
                CandidateRoot + "/Shaders/MakeItShineCc0PortR011.shader";
            string packShader =
                CandidateRoot + "/Shaders/MakeItShineCc0PackR011.shader";
            var json = new StringBuilder(32768);
            json.AppendLine("{");
            json.AppendLine("  \"schema\": \"make-it-shine-cc0-source-mapping.v1\",");
            json.AppendLine("  \"sourceCommit\": \"88842be0063b5b0b75e82ed6572752a37a13c82b\",");
            json.AppendLine("  \"license\": \"CC0-1.0\",");
            json.AppendLine("  \"entries\": [");
            AppendMapping(json, "Assets/Animation/Timelines/Booster to Card Timeline.playable",
                SourceTimelineSha256, EvidenceRoot + "/source-raw/Booster to Card Timeline.playable",
                "direct-copy", "Exact source structure retained outside Assets because its VFX Control tracks require the banned VFX Graph package.", false);
            AppendMapping(json, "Assets/Art/Environment/Shaders/SG_BoosterPack.shadergraph",
                SourceBoosterGraphSha256, EvidenceRoot + "/source-raw/SG_BoosterPack.shadergraph",
                "direct-copy", "Exact authored graph retained for audit; source mesh vertex-color and UV bindings prevent direct runtime use.", false);
            AppendMapping(json, "Assets/Art/Booster/SG_LightingStrike.shadergraph",
                SourceLightingGraphSha256, EvidenceRoot + "/source-raw/SG_LightingStrike.shadergraph",
                "direct-copy", "Exact VFX-targeted authored graph retained before the Shuriken compatibility port.", false);
            AppendMapping(json, "Assets/Art/Booster/SG_LightingStrike.shadergraph",
                SourceLightingGraphSha256, SourceLightingImportedGraphPath,
                "direct-copy", "Exact authored graph imported and bound directly as the Shuriken lightning trail material.", false);
            AppendMapping(json, "Assets/Art/Kyle/Materials/SG_Title_Kyle.shadergraph",
                SourceTitleGraphSha256, EvidenceRoot + "/source-raw/SG_Title_Kyle.shadergraph",
                "direct-copy", "Exact Sphere Mask graph retained; sample title texture remains rejected.", false);
            AppendMapping(json, "Assets/Art/Booster/VFX_BoosterActivation.vfx",
                SourceActivationVfxSha256, EvidenceRoot + "/source-raw/VFX_BoosterActivation.vfx",
                "direct-copy", "Exact VFX Graph retained outside Assets because the product bans the package.", false);
            AppendMapping(json, "Assets/Art/Booster/VFXG_LightingStrike.vfx",
                SourceLightingVfxSha256, EvidenceRoot + "/source-raw/VFXG_LightingStrike.vfx",
                "direct-copy", "Exact 25-strip and 512-spark source graph retained outside Assets.", false);
            AppendMapping(json, "Assets/Art/Booster/VFX_BoosterExplosion.vfx",
                SourceExplosionVfxSha256, EvidenceRoot + "/source-raw/VFX_BoosterExplosion.vfx",
                "direct-copy", "Exact 512-quad and 16-flare source graph retained outside Assets.", false);
            AppendMapping(json, "Assets/Animation/Timelines/Booster to Card Timeline.playable",
                SourceTimelineSha256, TimelinePath, "adapted",
                "Retargeted bindings keep source effect ordering and matched timestamps while the Pack and one pre-instantiated case remain the only product objects.", false);
            AppendMapping(json, "Assets/Animation/Clips/Booster/Booster_Discarded.anim",
                SourceDiscardSha256, SourceDiscardClipPath, "direct-copy",
                "Exact normalized dissolve curve and tangents imported.", false);
            AppendMapping(json, "Assets/Art/Environment/Shaders/SG_SelectedBooster.shadergraph",
                SourceSelectedGraphSha256, SourceSelectedGraphPath, "direct-copy",
                "Compatible authored selected-emission graph imported unchanged.", false);
            AppendMapping(json, "Assets/Art/Common/Graphs/CardMask.shadergraph",
                SourceCardMaskSha256, SourceCardMaskGraphPath, "direct-copy",
                "Compatible mask graph imported unchanged for audit; runtime rejects it as a Pack-mouth mask.", false);
            AppendMapping(json, "Assets/Art/Booster/TX_Flare_2x2_M.png",
                SourceFlareSha256, SourceFlareTexturePath, "direct-copy",
                "Exact source 2x2 flare texture drives the Shuriken port.", false);
            AppendMapping(json, "Assets/Art/Common/Textures/TX_Noise_M.tga",
                SourceNoiseSha256, SourceNoiseTexturePath, "direct-copy",
                "Exact source mask is imported for provenance but rejected at runtime after it produced forbidden pixel-noise holes.", false);
            AppendMapping(json, "Assets/Art/Booster/SG_LightingStrike.shadergraph",
                SourceLightingGraphSha256, portShader, "adapted",
                "VFX-targeted Shader Graph cannot bind to Shuriken directly; preserve its Reveal/Erode/Speed contract and source flare texture in a URP additive port.", false);
            AppendMapping(json, "Assets/Art/Environment/Shaders/SG_BoosterPack.shadergraph",
                SourceBoosterGraphSha256, packShader, "adapted",
                "Source graph depends on source mesh vertex colors and UVs; preserve its discard curve and emissive edge as a coherent torn-edge sweep on the real 384x512 Pack.", false);
            AppendMapping(json, "Assets/Art/Booster/VFX_BoosterActivation.vfx",
                SourceActivationVfxSha256, CandidateRoot + "/Runtime/PackOpeningGate04R011Controller.cs",
                "adapted", "VFX Graph is banned; port the source 3-particle activation envelope to deterministic Shuriken.", false);
            AppendMapping(json, "Assets/Art/Booster/VFXG_LightingStrike.vfx",
                SourceLightingVfxSha256, CandidateRoot + "/Editor/PackOpeningGate04R011Builder.cs",
                "adapted", "VFX Graph is banned; port 25 strips and 512 sparks to Shuriken trails and sparks.", false);
            AppendMapping(json, "Assets/Art/Booster/VFX_BoosterExplosion.vfx",
                SourceExplosionVfxSha256, CandidateRoot + "/Editor/PackOpeningGate04R011Builder.cs",
                "adapted", "VFX Graph is banned; port the 512-quad and 16-flare systems with source curves, gradient family, and texture.", false);
            AppendRejected(json, "Assets/Prefabs/Cinematic/Opening_Booster.prefab",
                "b155b76ffe54ac737651adbbfa177e284b22175733096e279e056316bf5aa978",
                "Contains sample Booster, fracture model, and object-swap ownership.");
            AppendRejected(json, "Assets/Art/Booster/BoosterFractured_B.fbx",
                "fd78b007802a1966a1dfb1a1c6b8c7c36cec2f3622dcbaf480fe039967ded602",
                "Sample geometry and fracture swap are forbidden.");
            AppendRejected(json, "Assets/Animation/Timelines/Spawn Cards Timeline.playable",
                "8d1cf67b8fdd982cd0cb6827afbdba96270f95cd5e24f99a30e53b30b60b6e28",
                "Three-card proxy handoff is replaced by the same real assembled case.");
            AppendRejected(json, "Assets/Art/Environment/Shaders/M_BoosterPack.mat",
                SourceBaseMaterialSha256,
                "Source material binds sample textures and source mesh data; the adapted material binds real Pack artwork.");
            AppendRejected(json, "Assets/Art/Environment/Shaders/MV_Pack_A.mat",
                SourceVariantMaterialSha256,
                "Source material variant carries sample art and is not imported or displayed.");
            AppendRejected(json, "Assets/Art/Kyle/TXT/TX_Title_Kyle.png",
                "6bc151e0aa4163961f2b95a54fac7c89208af5d7bdc60d0b0e297f4f668594c1",
                "Sample title artwork is not imported or displayed.", true);
            json.AppendLine("  ],");
            json.AppendLine("  \"vfxGraphDependency\": false,");
            json.AppendLine("  \"sampleModelsImported\": false,");
            json.AppendLine("  \"sampleArtworkImported\": false,");
            json.AppendLine("  \"shippingReady\": false");
            json.AppendLine("}");
            File.WriteAllText(path, json.ToString());
        }

        private static void AppendMapping(
            StringBuilder json,
            string source,
            string sourceHash,
            string destination,
            string decision,
            string reason,
            bool last)
        {
            string destinationHash = File.Exists(Path.Combine(ProjectRoot, destination))
                ? Sha256File(Path.Combine(ProjectRoot, destination))
                : "generated-after-import";
            json.AppendLine("    {");
            json.AppendLine($"      \"source\": \"{source}\",");
            json.AppendLine($"      \"sourceSha256\": \"{sourceHash}\",");
            json.AppendLine($"      \"destination\": \"{destination}\",");
            json.AppendLine($"      \"destinationSha256\": \"{destinationHash}\",");
            json.AppendLine($"      \"decision\": \"{decision}\",");
            json.AppendLine($"      \"reason\": \"{Escape(reason)}\"");
            json.AppendLine(last ? "    }" : "    },");
        }

        private static void AppendRejected(
            StringBuilder json,
            string source,
            string sourceHash,
            string reason,
            bool last = false)
        {
            json.AppendLine("    {");
            json.AppendLine($"      \"source\": \"{source}\",");
            json.AppendLine($"      \"sourceSha256\": \"{sourceHash}\",");
            json.AppendLine("      \"destination\": null,");
            json.AppendLine("      \"destinationSha256\": null,");
            json.AppendLine("      \"decision\": \"rejected\",");
            json.AppendLine($"      \"reason\": \"{Escape(reason)}\"");
            json.AppendLine(last ? "    }" : "    },");
        }

        private static void WriteSourceManifest()
        {
            string path = Path.Combine(
                ProjectRoot,
                EvidenceIterationRoot,
                "unity-source-manifest.json");
            string json =
                "{\n"
                + "  \"schema\": \"premium-display-case-gate04-r011-unity-source.v1\",\n"
                + "  \"unity\": \"6000.5.6f1\",\n"
                + "  \"urp\": \"17.5.0\",\n"
                + $"  \"scene\": \"{ScenePath}\",\n"
                + $"  \"timeline\": \"{TimelinePath}\",\n"
                + "  \"sourceTimelineSha256\": \"" + SourceTimelineSha256 + "\",\n"
                + "  \"sourceEffectSystems\": {\n"
                + "    \"activationParticles\": 3,\n"
                + "    \"lightningStrips\": 25,\n"
                + "    \"lightningSparks\": 512,\n"
                + "    \"explosionQuads\": 512,\n"
                + "    \"explosionFlares\": 16\n"
                + "  },\n"
                + "  \"realPackCanvas\": [384, 512],\n"
                + "  \"assembledCaseInstances\": 1,\n"
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

        private static void AssertHash(string assetPath, string expected)
        {
            string absolute = Path.Combine(ProjectRoot, assetPath);
            if (!File.Exists(absolute))
            {
                throw new FileNotFoundException($"Missing source: {assetPath}");
            }
            string actual = Sha256File(absolute);
            if (actual != expected)
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

        private enum SourceParticleKind
        {
            Activation,
            LightningTrail,
            Spark,
            Dust,
            Flare
        }

        private readonly struct MaterialSet
        {
            public MaterialSet(
                Material packBody,
                Material stripFront,
                Material stripUnderside,
                Material stripEdge,
                Material cavity,
                Material cavityContact,
                Material contactShadow,
                Material stripSpecular,
                Material activation,
                Material lightning,
                Material lightningSparks,
                Material explosionDust,
                Material explosionFlares,
                Material environment)
            {
                PackBody = packBody;
                StripFront = stripFront;
                StripUnderside = stripUnderside;
                StripEdge = stripEdge;
                Cavity = cavity;
                CavityContact = cavityContact;
                ContactShadow = contactShadow;
                StripSpecular = stripSpecular;
                Activation = activation;
                Lightning = lightning;
                LightningSparks = lightningSparks;
                ExplosionDust = explosionDust;
                ExplosionFlares = explosionFlares;
                Environment = environment;
            }

            public Material PackBody { get; }
            public Material StripFront { get; }
            public Material StripUnderside { get; }
            public Material StripEdge { get; }
            public Material Cavity { get; }
            public Material CavityContact { get; }
            public Material ContactShadow { get; }
            public Material StripSpecular { get; }
            public Material Activation { get; }
            public Material Lightning { get; }
            public Material LightningSparks { get; }
            public Material ExplosionDust { get; }
            public Material ExplosionFlares { get; }
            public Material Environment { get; }
        }

        private readonly struct SourceEffects
        {
            public SourceEffects(
                ParticleSystem activation,
                ParticleSystem lightningStrips,
                ParticleSystem lightningSparks,
                ParticleSystem explosionDust,
                ParticleSystem explosionFlares)
            {
                Activation = activation;
                LightningStrips = lightningStrips;
                LightningSparks = lightningSparks;
                ExplosionDust = explosionDust;
                ExplosionFlares = explosionFlares;
            }

            public ParticleSystem Activation { get; }
            public ParticleSystem LightningStrips { get; }
            public ParticleSystem LightningSparks { get; }
            public ParticleSystem ExplosionDust { get; }
            public ParticleSystem ExplosionFlares { get; }
        }
    }
}
