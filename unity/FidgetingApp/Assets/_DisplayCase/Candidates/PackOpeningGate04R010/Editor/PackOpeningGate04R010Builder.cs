using System;
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
    public static class PackOpeningGate04R010Builder
    {
        public const string CandidateRoot =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R010";
        public const string ScenePath =
            CandidateRoot + "/Scenes/PackOpeningGate04R010.unity";
        public const string ProfilePath =
            CandidateRoot + "/Profiles/PackOpeningGate04R010Profile.asset";
        public const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-010";
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

        private const string MaterialRoot = CandidateRoot + "/Generated/Materials";
        private const string MeshRoot = CandidateRoot + "/Generated/Meshes";
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

        [MenuItem("Fidgeting/Display Case/Gate 04 R010/Build And Capture")]
        public static void BuildAndRunCapture()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                throw new InvalidOperationException(
                    "Unity is already entering or running PlayMode.");
            }
            BuildSceneInternal();
            Debug.Log(
                "GATE04_R010_REAL_UNITY_CAPTURE_READY "
                + $"scene={ScenePath} output={EvidenceRoot}");
            EditorApplication.isPlaying = true;
        }

        [MenuItem("Fidgeting/Display Case/Gate 04 R010/Build Scene Only")]
        public static void BuildSceneOnly()
        {
            BuildSceneInternal();
            Debug.Log($"Gate 04 rev 10 candidate scene built at {ScenePath}.");
        }

        private static void BuildSceneInternal()
        {
            AssertEngineContract();
            EnsureDirectories();
            AssertSourceAssets();
            PackOpeningGate04R010Profile profile = CreateProfile();
            MaterialSet materials = CreateMaterials();
            MeshSet meshes = CreateEffectMeshes();
            Scene scene = BuildScene(profile, materials, meshes);
            EditorSceneManager.SaveScene(scene, ScenePath);
            WriteSourceManifest();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
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
                    $"Gate 04 rev 10 requires Unity 6000.5.6f1, got {Application.unityVersion}.");
            }
            UnityEditor.PackageManager.PackageInfo urp =
                UnityEditor.PackageManager.PackageInfo.FindForAssetPath(
                    "Packages/com.unity.render-pipelines.universal");
            if (
                urp == null
                || !string.Equals(urp.version, "17.5.0", StringComparison.Ordinal)
            )
            {
                throw new InvalidOperationException(
                    $"Gate 04 rev 10 requires URP 17.5.0, got {urp?.version ?? "missing"}.");
            }
        }

        private static void EnsureDirectories()
        {
            foreach (string directory in new[]
                     {
                         CandidateRoot + "/Scenes",
                         CandidateRoot + "/Profiles",
                         MaterialRoot,
                         MeshRoot,
                         EvidenceRoot,
                         EvidenceRoot + "/frames"
                     })
            {
                Directory.CreateDirectory(Path.Combine(ProjectRoot, directory));
            }
            AssetDatabase.Refresh();
        }

        private static void AssertSourceAssets()
        {
            AssertHash(
                PackBodyPath,
                ExpectedPackBodySha256,
                "authored Standard Pack body");
            AssertHash(
                PackFlapPath,
                ExpectedPackFlapSha256,
                "authored Standard Pack flap");
            AssertHash(
                ActualCasePrefabPath,
                ExpectedCasePrefabSha256,
                "real assembled Premium Display Case prefab");
            AssertHash(
                ActualPrizePrefabPath,
                ExpectedPrizePrefabSha256,
                "caller-owned prize prefab");
            AssertHash(
                ShippingEnvironmentTexturePath,
                ExpectedEnvironmentTextureSha256,
                "shipping dark mineral environment texture");
            AssertHash(
                ShippingEnvironmentMaterialPath,
                ExpectedEnvironmentMaterialSha256,
                "shipping environment material");
            AssertPngDimensions(PackBodyPath, 384, 512);
            AssertPngDimensions(PackFlapPath, 384, 512);
            AssertPngDimensions(
                ShippingEnvironmentTexturePath,
                1882,
                3344);
        }

        private static PackOpeningGate04R010Profile CreateProfile()
        {
            PackOpeningGate04R010Profile profile =
                AssetDatabase.LoadAssetAtPath<PackOpeningGate04R010Profile>(
                    ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<
                    PackOpeningGate04R010Profile>();
                AssetDatabase.CreateAsset(profile, ProfilePath);
            }
            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static MaterialSet CreateMaterials()
        {
            Shader lit = RequireShader("Universal Render Pipeline/Lit");
            Shader accent = RequireShader(
                "FidgetingApp/Candidates/OpeningAccentR010");
            Texture2D bodyTexture = RequireTexture(PackBodyPath);
            Texture2D flapTexture = RequireTexture(PackFlapPath);

            Material body = CreateMaterial(
                "Gate04R010ActualPackBodyOccluder",
                lit,
                material =>
                {
                    ConfigureLitTexture(
                        material,
                        bodyTexture,
                        new Color(0.96f, 0.96f, 0.95f, 1f),
                        0.58f,
                        0.46f);
                    material.renderQueue = 2460;
                });
            Material stripFront = CreateMaterial(
                "Gate04R010FoilStripFront",
                lit,
                material =>
                {
                    ConfigureLitTexture(
                        material,
                        flapTexture,
                        Color.white,
                        0.72f,
                        0.58f);
                    material.renderQueue = 2470;
                });
            Material stripUnderside = CreateLitMaterial(
                "Gate04R010FoilStripDarkUnderside",
                lit,
                new Color(0.105f, 0.108f, 0.116f, 1f),
                0.78f,
                0.32f);
            Material stripEdge = CreateLitMaterial(
                "Gate04R010FoilStripThinEdge",
                lit,
                new Color(0.48f, 0.46f, 0.43f, 1f),
                0.86f,
                0.52f);
            Material cavity = CreateLitMaterial(
                "Gate04R010ShapedInnerFoil",
                lit,
                new Color(0.135f, 0.126f, 0.112f, 1f),
                0.66f,
                0.31f);
            Material contactShadow = CreateAccentMaterial(
                "Gate04R010RestrainedContactShadow",
                accent,
                new Color(0.005f, 0.006f, 0.007f, 0.24f),
                3005);
            Material stripSpecular = CreateAccentMaterial(
                "Gate04R010MovingNarrowSpecular",
                accent,
                new Color(1f, 0.93f, 0.78f, 0.12f),
                3025);
            Material flash = CreateAccentMaterial(
                "Gate04R010ApertureFlash",
                accent,
                new Color(1f, 0.985f, 0.93f, 0.92f),
                2980);
            Material ring = CreateAccentMaterial(
                "Gate04R010SingleEnergyRing",
                accent,
                new Color(0.50f, 0.38f, 0.72f, 0.18f),
                2970);
            Material shard = CreateLitMaterial(
                "Gate04R010AuthoredFoilShard",
                lit,
                new Color(0.71f, 0.69f, 0.64f, 1f),
                0.82f,
                0.48f);
            Material glint = CreateAccentMaterial(
                "Gate04R010RestrainedGlint",
                accent,
                new Color(1f, 0.92f, 0.72f, 0.84f),
                3020);
            Material streak = CreateAccentMaterial(
                "Gate04R010NarrowVioletStreak",
                accent,
                new Color(0.49f, 0.36f, 0.70f, 0.48f),
                2960);

            Material shippingEnvironment =
                AssetDatabase.LoadAssetAtPath<Material>(
                    ShippingEnvironmentMaterialPath);
            if (shippingEnvironment == null)
            {
                throw new MissingReferenceException(
                    $"Missing shipping environment material: {ShippingEnvironmentMaterialPath}");
            }

            return new MaterialSet(
                body,
                stripFront,
                stripUnderside,
                stripEdge,
                cavity,
                contactShadow,
                stripSpecular,
                flash,
                ring,
                shard,
                glint,
                streak,
                shippingEnvironment);
        }

        private static MeshSet CreateEffectMeshes()
        {
            return new MeshSet(
                CreateOrReplaceMesh(
                    "Gate04R010ApertureBurst",
                    CreateApertureBurstMesh),
                CreateOrReplaceMesh(
                    "Gate04R010ThinEnergyRing",
                    CreateRingMesh),
                CreateOrReplaceMesh(
                    "Gate04R010FoldedFoilShard",
                    CreateShardMesh),
                CreateOrReplaceMesh(
                    "Gate04R010Glint",
                    CreateGlintMesh),
                CreateOrReplaceMesh(
                    "Gate04R010DirectionalStreak",
                    CreateStreakMesh));
        }

        private static Scene BuildScene(
            PackOpeningGate04R010Profile profile,
            MaterialSet materials,
            MeshSet meshes)
        {
            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            Camera camera = BuildCamera();
            Texture2D environmentTexture = RequireTexture(
                ShippingEnvironmentTexturePath);
            Renderer environmentRenderer = BuildEnvironment(
                materials.ShippingEnvironment);
            BuildLighting(out Light openingLight);
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
            BuildImpact(
                materials,
                meshes,
                out Transform flash,
                out Renderer flashRenderer,
                out Transform ring,
                out Renderer ringRenderer,
                out ParticleSystem shards,
                out ParticleSystem glints,
                out ParticleSystem streaks);

            var controllerObject = new GameObject(
                "PackOpeningGate04R010Controller");
            var controller =
                controllerObject.AddComponent<PackOpeningGate04R010Controller>();
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
                flash,
                flashRenderer,
                ring,
                ringRenderer,
                shards,
                glints,
                streaks,
                openingLight);

            string evidenceAbsolute = Path.Combine(ProjectRoot, EvidenceRoot);
            var captureObject = new GameObject("RealUnityPlayModeCaptureR010");
            var capture =
                captureObject.AddComponent<PackOpeningGate04R010Capture>();
            capture.Configure(camera, controller, evidenceAbsolute, ScenePath);
            Selection.activeGameObject = controllerObject;
            return scene;
        }

        private static Camera BuildCamera()
        {
            var cameraObject = new GameObject(
                "Gate04R010ShippingPortraitCamera");
            cameraObject.tag = "MainCamera";
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.003f, 0.004f, 0.005f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.fieldOfView = 30.5f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.transform.position = new Vector3(0f, 0.004f, -1.35f);
            camera.transform.LookAt(new Vector3(0f, -0.006f, -0.04f), Vector3.up);
            return camera;
        }

        private static Renderer BuildEnvironment(Material shippingMaterial)
        {
            GameObject environment = GameObject.CreatePrimitive(
                PrimitiveType.Quad);
            environment.name = "ActualShippingDarkMineralEnvironment";
            environment.transform.position = new Vector3(0f, -0.025f, 1.45f);
            environment.transform.localScale = new Vector3(1.04f, 1.84f, 1f);
            UnityEngine.Object.DestroyImmediate(
                environment.GetComponent<Collider>());
            MeshRenderer renderer = environment.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = shippingMaterial;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            return renderer;
        }

        private static void BuildLighting(out Light openingLight)
        {
            CreateDirectionalLight(
                "PremiumNeutralKey",
                Quaternion.Euler(32f, -28f, 0f),
                new Color(1f, 0.91f, 0.80f),
                1.72f,
                0.42f);
            CreateDirectionalLight(
                "CoolMineralFill",
                Quaternion.Euler(56f, 145f, 0f),
                new Color(0.60f, 0.68f, 0.76f),
                0.54f,
                0.24f);
            CreateDirectionalLight(
                "ControlledMetalRim",
                Quaternion.Euler(18f, 212f, 0f),
                new Color(0.92f, 0.88f, 0.78f),
                0.92f,
                0.30f);
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(
                0.095f,
                0.105f,
                0.110f);
            RenderSettings.ambientEquatorColor = new Color(
                0.042f,
                0.046f,
                0.047f);
            RenderSettings.ambientGroundColor = new Color(
                0.012f,
                0.012f,
                0.011f);
            RenderSettings.reflectionIntensity = 0.52f;

            var lightObject = new GameObject("ApertureReleaseLight");
            openingLight = lightObject.AddComponent<Light>();
            openingLight.type = LightType.Point;
            openingLight.range = 0.50f;
            openingLight.intensity = 0f;
            openingLight.color = new Color(1f, 0.84f, 0.62f);
            openingLight.shadows = LightShadows.Soft;
            openingLight.shadowStrength = 0.18f;
            openingLight.transform.position = new Vector3(
                0f,
                0.082f,
                -0.075f);
        }

        private static PremiumDisplayCaseShippingPresentation BuildActualCase(
            out Transform caseMotionRoot)
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                ActualCasePrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Missing actual case prefab: {ActualCasePrefabPath}");
            }
            var motionObject = new GameObject(
                "SingleConstantScalePremiumDisplayCase");
            caseMotionRoot = motionObject.transform;
            caseMotionRoot.position = new Vector3(0f, 0.002f, 0.060f);
            caseMotionRoot.rotation = Quaternion.identity;
            caseMotionRoot.localScale = Vector3.one
                * PackOpeningGate04R010Controller.CaseScale;

            GameObject caseObject =
                PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (caseObject == null)
            {
                throw new InvalidOperationException(
                    "Could not instantiate the real assembled case.");
            }
            caseObject.name = "ActualAssembledPremiumDisplayCase";
            caseObject.transform.SetParent(caseMotionRoot, false);
            caseObject.transform.localPosition = Vector3.zero;
            caseObject.transform.localRotation = Quaternion.identity;
            caseObject.transform.localScale = Vector3.one;
            PremiumDisplayCaseShippingPresentation presentation =
                caseObject.GetComponent<PremiumDisplayCaseShippingPresentation>();
            if (presentation == null || presentation.ContentSlot == null)
            {
                throw new MissingReferenceException(
                    "The real case must expose its configured ContentSlot.");
            }
            presentation.SetLabel(BuildAuthoritativeReviewLabel());
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            prize.name = "CallerOwnedThreeBladeContent";
            presentation.AttachContent(
                prize.transform,
                PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
            presentation.SetTimeForPreview(
                presentation.RevealProfile.TotalDurationSeconds);
            caseMotionRoot.gameObject.SetActive(true);
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
            bodyRenderer.shadowCastingMode = ShadowCastingMode.On;
            bodyRenderer.receiveShadows = true;

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
            stripRenderer.shadowCastingMode = ShadowCastingMode.On;
            stripRenderer.receiveShadows = true;

            GameObject cavity = CreateDynamicMeshObject(
                packRoot,
                "ShapedInnerFoilCavity",
                materials.Cavity);
            cavityFilter = cavity.GetComponent<MeshFilter>();
            cavityRenderer = cavity.GetComponent<MeshRenderer>();
            cavityRenderer.shadowCastingMode = ShadowCastingMode.On;
            cavityRenderer.receiveShadows = true;

            GameObject contactShadow = CreateDynamicMeshObject(
                packRoot,
                "RestrainedStripContactShadow",
                materials.ContactShadow);
            contactShadowFilter = contactShadow.GetComponent<MeshFilter>();
            contactShadowRenderer = contactShadow.GetComponent<MeshRenderer>();
            contactShadowRenderer.shadowCastingMode = ShadowCastingMode.Off;
            contactShadowRenderer.receiveShadows = false;
            contactShadowRenderer.sortingOrder = 12;

            GameObject specular = CreateDynamicMeshObject(
                packRoot,
                "MovingNarrowFoilSpecular",
                materials.StripSpecular);
            specularFilter = specular.GetComponent<MeshFilter>();
            specularRenderer = specular.GetComponent<MeshRenderer>();
            specularRenderer.shadowCastingMode = ShadowCastingMode.Off;
            specularRenderer.receiveShadows = false;
            specularRenderer.sortingOrder = 14;
        }

        private static void BuildImpact(
            MaterialSet materials,
            MeshSet meshes,
            out Transform localizedFlash,
            out Renderer localizedFlashRenderer,
            out Transform energyRing,
            out Renderer energyRingRenderer,
            out ParticleSystem foilShards,
            out ParticleSystem glints,
            out ParticleSystem directionalStreaks)
        {
            var root = new GameObject("ApertureLedPremiumImpact");

            GameObject flashObject = CreateMeshObject(
                root.transform,
                "OneFrameApertureFlashBehindCase",
                meshes.ApertureBurst,
                materials.Flash);
            flashObject.transform.position = new Vector3(0f, 0.065f, 0.115f);
            flashObject.SetActive(false);
            localizedFlash = flashObject.transform;
            localizedFlashRenderer = flashObject.GetComponent<Renderer>();

            GameObject ringObject = CreateMeshObject(
                root.transform,
                "OneThinEnergyRingBehindProduct",
                meshes.Ring,
                materials.Ring);
            ringObject.transform.position = new Vector3(0f, -0.006f, 0.150f);
            ringObject.SetActive(false);
            energyRing = ringObject.transform;
            energyRingRenderer = ringObject.GetComponent<Renderer>();

            foilShards = CreateParticleSystem(
                root.transform,
                "ThreeAuthoredFoilShards",
                meshes.Shard,
                materials.Shard,
                3,
                0.010f,
                0.28f,
                0.22f,
                new Vector2(-0.24f, 0.24f),
                new Vector2(0.16f, 0.42f),
                9137u);
            glints = CreateParticleSystem(
                root.transform,
                "ThreeRestrainedGlints",
                meshes.Glint,
                materials.Glint,
                3,
                0.007f,
                0.18f,
                0.16f,
                new Vector2(-0.18f, 0.18f),
                new Vector2(0.08f, 0.30f),
                4201u);
            directionalStreaks = CreateParticleSystem(
                root.transform,
                "TwoNarrowDirectionalVioletStreaks",
                meshes.Streak,
                materials.Streak,
                2,
                0.010f,
                0.23f,
                0.14f,
                new Vector2(-0.36f, 0.36f),
                new Vector2(0.05f, 0.20f),
                7129u);
        }

        private static ParticleSystem CreateParticleSystem(
            Transform parent,
            string name,
            Mesh mesh,
            Material material,
            short count,
            float size,
            float duration,
            float lifetime,
            Vector2 velocityX,
            Vector2 velocityY,
            uint randomSeed)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            item.transform.position = new Vector3(0f, 0.070f, 0.120f);
            ParticleSystem system = item.AddComponent<ParticleSystem>();
            ParticleSystem.MainModule main = system.main;
            main.loop = false;
            main.playOnAwake = false;
            main.duration = duration;
            main.startLifetime = lifetime;
            main.startSpeed = 0f;
            main.startSize = size;
            main.startColor = Color.white;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.gravityModifier = 0.08f;
            main.maxParticles = count;

            ParticleSystem.EmissionModule emission = system.emission;
            emission.rateOverTime = 0f;
            emission.SetBursts(new[]
            {
                new ParticleSystem.Burst(0f, count)
            });
            ParticleSystem.ShapeModule shape = system.shape;
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(0.050f, 0.010f, 0.006f);

            ParticleSystem.VelocityOverLifetimeModule velocity =
                system.velocityOverLifetime;
            velocity.enabled = true;
            velocity.space = ParticleSystemSimulationSpace.World;
            velocity.x = new ParticleSystem.MinMaxCurve(
                velocityX.x,
                velocityX.y);
            velocity.y = new ParticleSystem.MinMaxCurve(
                velocityY.x,
                velocityY.y);
            velocity.z = new ParticleSystem.MinMaxCurve(-0.10f, 0.02f);

            ParticleSystem.RotationOverLifetimeModule rotation =
                system.rotationOverLifetime;
            rotation.enabled = true;
            rotation.z = new ParticleSystem.MinMaxCurve(-3.2f, 3.2f);
            ParticleSystem.ColorOverLifetimeModule colorOverLifetime =
                system.colorOverLifetime;
            colorOverLifetime.enabled = true;
            colorOverLifetime.color = new ParticleSystem.MinMaxGradient(
                new Gradient
                {
                    alphaKeys = new[]
                    {
                        new GradientAlphaKey(0f, 0f),
                        new GradientAlphaKey(1f, 0.08f),
                        new GradientAlphaKey(0f, 1f)
                    },
                    colorKeys = new[]
                    {
                        new GradientColorKey(Color.white, 0f),
                        new GradientColorKey(Color.white, 1f)
                    }
                });

            ParticleSystemRenderer renderer =
                item.GetComponent<ParticleSystemRenderer>();
            renderer.renderMode = ParticleSystemRenderMode.Mesh;
            renderer.mesh = mesh;
            renderer.sharedMaterial = material;
            renderer.alignment = ParticleSystemRenderSpace.View;
            renderer.sortingOrder = 8;
            system.useAutoRandomSeed = false;
            system.randomSeed = randomSeed;
            system.Stop(
                true,
                ParticleSystemStopBehavior.StopEmittingAndClear);
            return system;
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
            material.SetOverrideTag("RenderType", "TransparentCutout");
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
                    material.DisableKeyword("_ALPHATEST_ON");
                    material.SetFloat("_AlphaClip", 0f);
                    material.renderQueue = 2000;
                });
        }

        private static Material CreateAccentMaterial(
            string name,
            Shader shader,
            Color color,
            int renderQueue)
        {
            return CreateMaterial(
                name,
                shader,
                material =>
                {
                    material.SetColor("_BaseColor", color);
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
            else
            {
                material.shader = shader;
                material.name = name;
            }
            configure(material);
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Mesh CreateOrReplaceMesh(
            string name,
            Func<Mesh> create)
        {
            string path = $"{MeshRoot}/{name}.asset";
            if (AssetDatabase.LoadAssetAtPath<Mesh>(path) != null)
            {
                AssetDatabase.DeleteAsset(path);
            }
            Mesh mesh = create();
            mesh.name = name;
            AssetDatabase.CreateAsset(mesh, path);
            return mesh;
        }

        private static Mesh CreateApertureBurstMesh()
        {
            const int points = 64;
            var vertices = new Vector3[points + 1];
            var uvs = new Vector2[points + 1];
            var colors = new Color[points + 1];
            var triangles = new int[points * 3];
            vertices[0] = Vector3.zero;
            uvs[0] = new Vector2(0.5f, 0.5f);
            colors[0] = Color.white;
            for (int index = 0; index < points; index++)
            {
                float angle = index / (float)points * Mathf.PI * 2f;
                float radius = 1f + 0.018f * Mathf.Sin(angle * 3f + 0.4f);
                vertices[index + 1] = new Vector3(
                    Mathf.Cos(angle) * radius,
                    Mathf.Sin(angle) * radius,
                    0f);
                uvs[index + 1] = new Vector2(
                    0.5f + Mathf.Cos(angle) * 0.5f,
                    0.5f + Mathf.Sin(angle) * 0.5f);
                colors[index + 1] = new Color(1f, 1f, 1f, 0.035f);
                triangles[index * 3] = 0;
                triangles[index * 3 + 1] = index + 1;
                triangles[index * 3 + 2] = (index + 1) % points + 1;
            }
            Mesh mesh = BuildMesh(vertices, uvs, triangles);
            mesh.colors = colors;
            return mesh;
        }

        private static Mesh CreateRingMesh()
        {
            const int segments = 96;
            var vertices = new Vector3[segments * 2];
            var uvs = new Vector2[vertices.Length];
            var triangles = new int[segments * 6];
            for (int index = 0; index < segments; index++)
            {
                float angle = index / (float)segments * Mathf.PI * 2f;
                Vector3 direction = new Vector3(
                    Mathf.Cos(angle),
                    Mathf.Sin(angle),
                    0f);
                vertices[index * 2] = direction;
                vertices[index * 2 + 1] = direction * 0.976f;
                uvs[index * 2] = new Vector2(1f, index / (float)segments);
                uvs[index * 2 + 1] = new Vector2(0f, index / (float)segments);
                int next = (index + 1) % segments;
                int offset = index * 6;
                triangles[offset] = index * 2;
                triangles[offset + 1] = next * 2;
                triangles[offset + 2] = index * 2 + 1;
                triangles[offset + 3] = index * 2 + 1;
                triangles[offset + 4] = next * 2;
                triangles[offset + 5] = next * 2 + 1;
            }
            return BuildMesh(vertices, uvs, triangles);
        }

        private static Mesh CreateShardMesh()
        {
            Vector3[] vertices =
            {
                new Vector3(-0.52f, -0.30f, -0.05f),
                new Vector3(0.48f, -0.22f, 0.08f),
                new Vector3(0.18f, 0.42f, -0.10f),
                new Vector3(-0.24f, 0.30f, 0.06f)
            };
            Vector2[] uvs =
            {
                Vector2.zero,
                Vector2.right,
                Vector2.one,
                Vector2.up
            };
            return BuildMesh(
                vertices,
                uvs,
                new[] { 0, 1, 2, 0, 2, 3, 2, 1, 0, 3, 2, 0 });
        }

        private static Mesh CreateGlintMesh()
        {
            Vector3[] vertices =
            {
                new Vector3(-0.08f, 0f, 0f),
                new Vector3(0f, -1f, 0f),
                new Vector3(0.08f, 0f, 0f),
                new Vector3(0f, 1f, 0f),
                new Vector3(-1f, 0f, 0f),
                new Vector3(0f, -0.08f, 0f),
                new Vector3(1f, 0f, 0f),
                new Vector3(0f, 0.08f, 0f)
            };
            Vector2[] uvs = Enumerable
                .Repeat(new Vector2(0.5f, 0.5f), 8)
                .ToArray();
            return BuildMesh(
                vertices,
                uvs,
                new[] { 0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7 });
        }

        private static Mesh CreateStreakMesh()
        {
            Vector3[] vertices =
            {
                new Vector3(-1f, -0.05f, 0f),
                new Vector3(0.55f, -0.10f, 0f),
                new Vector3(1f, 0.05f, 0f),
                new Vector3(0.55f, 0.10f, 0f)
            };
            Vector2[] uvs =
            {
                Vector2.zero,
                Vector2.right,
                Vector2.one,
                Vector2.up
            };
            return BuildMesh(vertices, uvs, new[] { 0, 1, 2, 0, 2, 3 });
        }

        private static Mesh BuildMesh(
            Vector3[] vertices,
            Vector2[] uvs,
            int[] triangles)
        {
            var mesh = new Mesh();
            mesh.vertices = vertices;
            mesh.uv = uvs;
            mesh.triangles = triangles;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static GameObject CreateDynamicMeshObject(
            Transform parent,
            string name,
            Material material)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            item.transform.localPosition = Vector3.zero;
            item.AddComponent<MeshFilter>();
            MeshRenderer renderer = item.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            return item;
        }

        private static GameObject CreateMeshObject(
            Transform parent,
            string name,
            Mesh mesh,
            Material material)
        {
            GameObject item = CreateDynamicMeshObject(parent, name, material);
            item.GetComponent<MeshFilter>().sharedMesh = mesh;
            MeshRenderer renderer = item.GetComponent<MeshRenderer>();
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
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

        private static PremiumDisplayCaseLabelData BuildAuthoritativeReviewLabel()
        {
            const string prefix =
                "fidgeting.gacha.preview.gate04-r010-unity.";
            var inventory = new GachaInventoryRuntime(
                prefix,
                new GachaSplitMix64(0x410010UL));
            GachaTransactionResult transaction =
                inventory.QueryTransaction("gate04-r010-real-unity");
            if (!transaction.Success)
            {
                inventory.PrimeGate12SimulatorPreview();
                transaction = inventory.PrepareDraw(
                    GachaCatalog.LaunchSeriesId,
                    1,
                    GachaPaymentMethod.Ticket,
                    "gate04-r010-real-unity");
            }
            if (!transaction.Success || transaction.Receipt.Rows.Count != 1)
            {
                throw new InvalidOperationException(
                    "Could not create the authoritative rev 10 review receipt.");
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

        private static void AssertPngDimensions(
            string assetPath,
            int expectedWidth,
            int expectedHeight)
        {
            Vector2Int size = ReadPngDimensions(
                Path.Combine(ProjectRoot, assetPath));
            if (size.x != expectedWidth || size.y != expectedHeight)
            {
                throw new InvalidOperationException(
                    $"{assetPath} expected {expectedWidth}x{expectedHeight}, got {size.x}x{size.y}.");
            }
        }

        private static Vector2Int ReadPngDimensions(string absolutePath)
        {
            byte[] header = new byte[24];
            using FileStream stream = File.OpenRead(absolutePath);
            if (
                stream.Read(header, 0, header.Length) != header.Length
                || header[0] != 0x89
                || header[1] != 0x50
                || header[2] != 0x4E
                || header[3] != 0x47
            )
            {
                throw new InvalidDataException(
                    $"Invalid PNG header: {absolutePath}");
            }
            int width =
                header[16] << 24
                | header[17] << 16
                | header[18] << 8
                | header[19];
            int height =
                header[20] << 24
                | header[21] << 16
                | header[22] << 8
                | header[23];
            return new Vector2Int(width, height);
        }

        private static void AssertHash(
            string assetPath,
            string expected,
            string label)
        {
            string absolute = Path.Combine(ProjectRoot, assetPath);
            if (!File.Exists(absolute))
            {
                throw new FileNotFoundException($"Missing {label}: {assetPath}");
            }
            string actual = Sha256File(absolute);
            if (!string.Equals(actual, expected, StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"{label} hash changed. Expected {expected}, got {actual}.");
            }
        }

        private static void WriteSourceManifest()
        {
            string path = Path.Combine(
                ProjectRoot,
                EvidenceRoot,
                "unity-source-manifest.json");
            string controllerPath =
                CandidateRoot + "/Runtime/PackOpeningGate04R010Controller.cs";
            string profilePath =
                CandidateRoot + "/Runtime/PackOpeningGate04R010Profile.cs";
            string capturePath =
                CandidateRoot + "/Runtime/PackOpeningGate04R010Capture.cs";
            string builderPath =
                CandidateRoot + "/Editor/PackOpeningGate04R010Builder.cs";
            string testsPath =
                CandidateRoot + "/Tests/Editor/PackOpeningGate04R010Tests.cs";
            string shaderPath =
                CandidateRoot + "/Shaders/OpeningAccentR010.shader";
            string json =
                "{\n"
                + "  \"schema\": \"premium-display-case-gate04-r010-unity-source.v1\",\n"
                + "  \"source\": \"canonical unity/FidgetingApp\",\n"
                + $"  \"unity\": \"{Application.unityVersion}\",\n"
                + "  \"urp\": \"17.5.0\",\n"
                + $"  \"scene\": \"{ScenePath}\",\n"
                + $"  \"profile\": \"{ProfilePath}\",\n"
                + "  \"actualPack\": {\n"
                + $"    \"body\": \"{PackBodyPath}\",\n"
                + $"    \"bodySha256\": \"{ExpectedPackBodySha256}\",\n"
                + $"    \"flap\": \"{PackFlapPath}\",\n"
                + $"    \"flapSha256\": \"{ExpectedPackFlapSha256}\",\n"
                + "    \"authoredCanvas\": [384, 512]\n"
                + "  },\n"
                + "  \"actualAssembledCase\": {\n"
                + $"    \"prefab\": \"{ActualCasePrefabPath}\",\n"
                + $"    \"sha256\": \"{ExpectedCasePrefabSha256}\",\n"
                + $"    \"callerOwnedContent\": \"{ActualPrizePrefabPath}\",\n"
                + $"    \"callerOwnedContentSha256\": \"{ExpectedPrizePrefabSha256}\",\n"
                + "    \"instanceCount\": 1,\n"
                + "    \"constantRootScale\": 1.02,\n"
                + "    \"wholeCaseOnly\": true,\n"
                + "    \"toyEdited\": false\n"
                + "  },\n"
                + "  \"actualShippingEnvironment\": {\n"
                + $"    \"texture\": \"{ShippingEnvironmentTexturePath}\",\n"
                + $"    \"textureSha256\": \"{ExpectedEnvironmentTextureSha256}\",\n"
                + $"    \"material\": \"{ShippingEnvironmentMaterialPath}\",\n"
                + $"    \"materialSha256\": \"{ExpectedEnvironmentMaterialSha256}\",\n"
                + "    \"flatDebugBlocks\": false\n"
                + "  },\n"
                + "  \"foilConstruction\": {\n"
                + "    \"longitudinalSegments\": 48,\n"
                + "    \"crossRows\": 4,\n"
                + "    \"frontMaterial\": true,\n"
                + "    \"darkUndersideMaterial\": true,\n"
                + "    \"edgeThicknessMeters\": 0.00075,\n"
                + "    \"movingSpecularGeometry\": true,\n"
                + "    \"contactShadowGeometry\": true,\n"
                + "    \"sharedSeededTearEdge\": true,\n"
                + "    \"maximumTearAmplitudeMeters\": 0.00115,\n"
                + "    \"shapedCavityGeometry\": true\n"
                + "  },\n"
                + "  \"sources\": {\n"
                + $"    \"controller\": \"{Sha256File(Path.Combine(ProjectRoot, controllerPath))}\",\n"
                + $"    \"profile\": \"{Sha256File(Path.Combine(ProjectRoot, profilePath))}\",\n"
                + $"    \"capture\": \"{Sha256File(Path.Combine(ProjectRoot, capturePath))}\",\n"
                + $"    \"builder\": \"{Sha256File(Path.Combine(ProjectRoot, builderPath))}\",\n"
                + $"    \"tests\": \"{Sha256File(Path.Combine(ProjectRoot, testsPath))}\",\n"
                + $"    \"accentShader\": \"{Sha256File(Path.Combine(ProjectRoot, shaderPath))}\"\n"
                + "  },\n"
                + "  \"rendering\": {\n"
                + "    \"vfxGraph\": false,\n"
                + "    \"shuriken\": true,\n"
                + "    \"postProcessingBloom\": false,\n"
                + "    \"chromaticAberration\": false,\n"
                + "    \"lensDistortion\": false,\n"
                + "    \"noiseParticles\": false,\n"
                + "    \"fullScreenEffect\": false\n"
                + "  },\n"
                + "  \"shippingRuntimeWired\": false,\n"
                + "  \"nativeUiWired\": false,\n"
                + "  \"shippingReady\": false,\n"
                + "  \"physicalPhoneInstalled\": false\n"
                + "}\n";
            File.WriteAllText(path, json);
        }

        private static string Sha256File(string absolute)
        {
            using SHA256 sha = SHA256.Create();
            using FileStream stream = File.OpenRead(absolute);
            return string.Concat(
                sha.ComputeHash(stream).Select(
                    value => value.ToString("x2", CultureInfo.InvariantCulture)));
        }

        private static string ProjectRoot =>
            Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

        private readonly struct MaterialSet
        {
            public MaterialSet(
                Material packBody,
                Material stripFront,
                Material stripUnderside,
                Material stripEdge,
                Material cavity,
                Material contactShadow,
                Material stripSpecular,
                Material flash,
                Material ring,
                Material shard,
                Material glint,
                Material streak,
                Material shippingEnvironment)
            {
                PackBody = packBody;
                StripFront = stripFront;
                StripUnderside = stripUnderside;
                StripEdge = stripEdge;
                Cavity = cavity;
                ContactShadow = contactShadow;
                StripSpecular = stripSpecular;
                Flash = flash;
                Ring = ring;
                Shard = shard;
                Glint = glint;
                Streak = streak;
                ShippingEnvironment = shippingEnvironment;
            }

            public Material PackBody { get; }
            public Material StripFront { get; }
            public Material StripUnderside { get; }
            public Material StripEdge { get; }
            public Material Cavity { get; }
            public Material ContactShadow { get; }
            public Material StripSpecular { get; }
            public Material Flash { get; }
            public Material Ring { get; }
            public Material Shard { get; }
            public Material Glint { get; }
            public Material Streak { get; }
            public Material ShippingEnvironment { get; }
        }

        private readonly struct MeshSet
        {
            public MeshSet(
                Mesh apertureBurst,
                Mesh ring,
                Mesh shard,
                Mesh glint,
                Mesh streak)
            {
                ApertureBurst = apertureBurst;
                Ring = ring;
                Shard = shard;
                Glint = glint;
                Streak = streak;
            }

            public Mesh ApertureBurst { get; }
            public Mesh Ring { get; }
            public Mesh Shard { get; }
            public Mesh Glint { get; }
            public Mesh Streak { get; }
        }
    }
}
