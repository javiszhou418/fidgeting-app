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
    public static class PackOpeningGate04R009Builder
    {
        public const string CandidateRoot =
            "Assets/_DisplayCase/Candidates/PackOpeningGate04R009";
        public const string ScenePath =
            CandidateRoot + "/Scenes/PackOpeningGate04R009.unity";
        public const string ProfilePath =
            CandidateRoot + "/Profiles/PackOpeningGate04R009Profile.asset";
        public const string EvidenceRoot =
            "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-009";
        public const string PackBodyPath =
            "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png";
        public const string PackFlapPath =
            "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png";
        public const string ActualCasePrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab";
        public const string ActualPrizePrefabPath =
            "Assets/Resources/Gacha/ThreeBladeDisplayPrize.prefab";

        private const string MaterialRoot = CandidateRoot + "/Generated/Materials";
        private const string MeshRoot = CandidateRoot + "/Generated/Meshes";
        private const string ExpectedPackBodySha256 =
            "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6";
        private const string ExpectedPackFlapSha256 =
            "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49";
        private const string ExpectedCasePrefabSha256 =
            "7a96aae6245b5a1d5463dabc3cb4518af8693ba8f8328ad9f2fe4ee6c6a67e2c";

        [MenuItem("Fidgeting/Display Case/Gate 04 R009/Build And Capture Real Unity")]
        public static void BuildAndRunCapture()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                throw new InvalidOperationException(
                    "Unity is already entering or running PlayMode.");
            }

            AssertEngineContract();
            EnsureDirectories();
            AssertSourceAssets();
            PackOpeningGate04R009Profile profile = CreateProfile();
            MaterialSet materials = CreateMaterials();
            MeshSet meshes = CreateEffectMeshes();
            Scene scene = BuildScene(profile, materials, meshes);
            EditorSceneManager.SaveScene(scene, ScenePath);
            WriteSourceManifest();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            AssertSourceAssets();
            Debug.Log(
                "GATE04_R009_REAL_UNITY_CAPTURE_READY "
                + $"scene={ScenePath} output={EvidenceRoot}");
            EditorApplication.isPlaying = true;
        }

        [MenuItem("Fidgeting/Display Case/Gate 04 R009/Build Scene Only")]
        public static void BuildSceneOnly()
        {
            AssertEngineContract();
            EnsureDirectories();
            AssertSourceAssets();
            PackOpeningGate04R009Profile profile = CreateProfile();
            MaterialSet materials = CreateMaterials();
            MeshSet meshes = CreateEffectMeshes();
            Scene scene = BuildScene(profile, materials, meshes);
            EditorSceneManager.SaveScene(scene, ScenePath);
            WriteSourceManifest();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            AssertSourceAssets();
            Debug.Log($"Gate 04 rev 9 candidate scene built at {ScenePath}.");
        }

        private static void AssertEngineContract()
        {
            if (!string.Equals(
                    Application.unityVersion,
                    "6000.5.6f1",
                    StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"Gate 04 rev 9 requires Unity 6000.5.6f1, got {Application.unityVersion}.");
            }
            UnityEditor.PackageManager.PackageInfo urp =
                UnityEditor.PackageManager.PackageInfo.FindForAssetPath(
                    "Packages/com.unity.render-pipelines.universal");
            if (urp == null || !string.Equals(urp.version, "17.5.0", StringComparison.Ordinal))
            {
                throw new InvalidOperationException(
                    $"Gate 04 rev 9 requires URP 17.5.0, got {urp?.version ?? "missing"}.");
            }
        }

        private static void EnsureDirectories()
        {
            string project = ProjectRoot;
            foreach (string directory in new[]
                     {
                         CandidateRoot + "/Scenes",
                         CandidateRoot + "/Profiles",
                         MaterialRoot,
                         MeshRoot,
                         EvidenceRoot,
                         EvidenceRoot + "/frames",
                         EvidenceRoot + "/tear-closeup-frames",
                         EvidenceRoot + "/impact-closeup-frames"
                     })
            {
                Directory.CreateDirectory(Path.Combine(project, directory));
            }
            AssetDatabase.Refresh();
        }

        private static void AssertSourceAssets()
        {
            AssertHash(PackBodyPath, ExpectedPackBodySha256, "authored Standard Pack body");
            AssertHash(PackFlapPath, ExpectedPackFlapSha256, "authored Standard Pack flap");
            AssertHash(
                ActualCasePrefabPath,
                ExpectedCasePrefabSha256,
                "real assembled Premium Display Case prefab");
            if (AssetDatabase.LoadAssetAtPath<GameObject>(ActualPrizePrefabPath) == null)
            {
                throw new MissingReferenceException(
                    $"Missing caller-owned prize prefab: {ActualPrizePrefabPath}");
            }
        }

        private static PackOpeningGate04R009Profile CreateProfile()
        {
            PackOpeningGate04R009Profile profile =
                AssetDatabase.LoadAssetAtPath<PackOpeningGate04R009Profile>(
                    ProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<
                    PackOpeningGate04R009Profile>();
                AssetDatabase.CreateAsset(profile, ProfilePath);
            }
            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static MaterialSet CreateMaterials()
        {
            Shader bodyShader = RequireShader(
                "FidgetingApp/Candidates/PackFoilBodyTearR009");
            Shader foilShader = RequireShader(
                "FidgetingApp/Candidates/PackFoilSurfaceR009");
            Shader accentShader = RequireShader(
                "FidgetingApp/Candidates/OpeningAccentR009");
            Shader litShader = RequireShader("Universal Render Pipeline/Lit");

            Texture2D bodyTexture = RequireTexture(PackBodyPath);
            Texture2D flapTexture = RequireTexture(PackFlapPath);
            Material body = CreateMaterial(
                "Gate04R009ActualPackBody",
                bodyShader,
                material =>
                {
                    material.SetTexture("_BaseMap", bodyTexture);
                    material.SetColor("_BaseColor", Color.white);
                    material.SetColor(
                        "_EdgeColor",
                        new Color(0.66f, 0.60f, 0.60f, 1f));
                    material.renderQueue = 2470;
                });
            Material flap = CreateMaterial(
                "Gate04R009ActualPackFlap",
                foilShader,
                material =>
                {
                    material.SetTexture("_BaseMap", flapTexture);
                    material.SetColor("_BaseColor", Color.white);
                    material.SetColor(
                        "_HighlightColor",
                        new Color(1f, 0.95f, 0.84f, 1f));
                    material.SetColor(
                        "_VioletEdge",
                        new Color(0.42f, 0.28f, 0.60f, 1f));
                    material.renderQueue = 3030;
                });
            Material tornEdge = CreateMaterial(
                "Gate04R009TornFoilThickness",
                accentShader,
                material =>
                {
                    material.SetColor(
                        "_BaseColor",
                        new Color(0.76f, 0.72f, 0.64f, 0.86f));
                    material.renderQueue = 3010;
                });
            Material flash = CreateMaterial(
                "Gate04R009LocalizedOpeningFlash",
                accentShader,
                material =>
                {
                    material.SetColor(
                        "_BaseColor",
                        new Color(1f, 0.985f, 0.94f, 0.96f));
                    material.renderQueue = 2990;
                });
            Material shockwave = CreateMaterial(
                "Gate04R009ThinOpeningShockwave",
                accentShader,
                material =>
                {
                    material.SetColor(
                        "_BaseColor",
                        new Color(0.46f, 0.32f, 0.68f, 0.42f));
                    material.renderQueue = 2980;
                });
            Material shard = CreateMaterial(
                "Gate04R009FoilShard",
                accentShader,
                material =>
                {
                    material.SetColor(
                        "_BaseColor",
                        new Color(0.86f, 0.82f, 0.73f, 0.92f));
                    material.renderQueue = 3020;
                });
            Material glint = CreateMaterial(
                "Gate04R009WarmGlint",
                accentShader,
                material =>
                {
                    material.SetColor(
                        "_BaseColor",
                        new Color(1f, 0.94f, 0.78f, 0.94f));
                    material.renderQueue = 3022;
                });
            Material streak = CreateMaterial(
                "Gate04R009VioletDirectionalStreak",
                accentShader,
                material =>
                {
                    material.SetColor(
                        "_BaseColor",
                        new Color(0.48f, 0.33f, 0.68f, 0.54f));
                    material.renderQueue = 2985;
                });

            Material mineral = CreateLitMaterial(
                "Gate04R009DarkMineral",
                litShader,
                new Color(0.032f, 0.034f, 0.038f, 1f),
                0.12f,
                0.22f);
            Material mineralRaised = CreateLitMaterial(
                "Gate04R009RaisedMineral",
                litShader,
                new Color(0.060f, 0.058f, 0.055f, 1f),
                0.18f,
                0.31f);
            Material plinth = CreateLitMaterial(
                "Gate04R009WarmNeutralPlinth",
                litShader,
                new Color(0.105f, 0.098f, 0.087f, 1f),
                0.62f,
                0.46f);
            return new MaterialSet(
                body,
                flap,
                tornEdge,
                flash,
                shockwave,
                shard,
                glint,
                streak,
                mineral,
                mineralRaised,
                plinth);
        }

        private static MeshSet CreateEffectMeshes()
        {
            return new MeshSet(
                CreateOrReplaceMesh("Gate04R009OpeningStar", CreateStarMesh),
                CreateOrReplaceMesh("Gate04R009ThinRing", CreateRingMesh),
                CreateOrReplaceMesh("Gate04R009FoldedFoilShard", CreateShardMesh),
                CreateOrReplaceMesh("Gate04R009Glint", CreateGlintMesh),
                CreateOrReplaceMesh("Gate04R009DirectionalStreak", CreateStreakMesh));
        }

        private static Scene BuildScene(
            PackOpeningGate04R009Profile profile,
            MaterialSet materials,
            MeshSet meshes)
        {
            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            BuildEnvironment(materials);
            Camera camera = BuildCamera();
            BuildLighting(out Light openingLight);
            PremiumDisplayCaseShippingPresentation presentation =
                BuildActualCase(out Transform caseMotionRoot);
            BuildPack(
                materials,
                out Renderer packBodyRenderer,
                out MeshFilter flapFilter,
                out Renderer flapRenderer,
                out MeshFilter rimFilter,
                out Renderer rimRenderer);
            BuildImpact(
                materials,
                meshes,
                out Transform flash,
                out Renderer flashRenderer,
                out Transform shockwave,
                out Renderer shockwaveRenderer,
                out ParticleSystem shards,
                out ParticleSystem glints,
                out ParticleSystem streaks);

            var controllerObject = new GameObject("PackOpeningGate04R009Controller");
            var controller =
                controllerObject.AddComponent<PackOpeningGate04R009Controller>();
            controller.Configure(
                profile,
                camera,
                packBodyRenderer,
                flapFilter,
                flapRenderer,
                rimFilter,
                rimRenderer,
                caseMotionRoot,
                presentation,
                flash,
                flashRenderer,
                shockwave,
                shockwaveRenderer,
                shards,
                glints,
                streaks,
                openingLight);

            string evidenceAbsolute = Path.Combine(ProjectRoot, EvidenceRoot);
            var captureObject = new GameObject("RealUnityPlayModeCapture");
            var capture =
                captureObject.AddComponent<PackOpeningGate04R009Capture>();
            capture.Configure(camera, controller, evidenceAbsolute, ScenePath);
            Selection.activeGameObject = controllerObject;
            return scene;
        }

        private static void BuildEnvironment(MaterialSet materials)
        {
            GameObject root = new GameObject("PreloadedDarkMineralEnvironment");
            CreateCube(
                root.transform,
                "MineralBackdrop",
                new Vector3(0f, 0.04f, 0.39f),
                new Vector3(0.72f, 0.92f, 0.055f),
                materials.Mineral);
            CreateCube(
                root.transform,
                "LeftMineralRelief",
                new Vector3(-0.265f, 0.03f, 0.22f),
                new Vector3(0.075f, 0.62f, 0.075f),
                materials.MineralRaised);
            CreateCube(
                root.transform,
                "RightMineralRelief",
                new Vector3(0.265f, 0.03f, 0.22f),
                new Vector3(0.075f, 0.62f, 0.075f),
                materials.MineralRaised);
        }

        private static Camera BuildCamera()
        {
            var cameraObject = new GameObject("Gate04R009ShippingPortraitCamera");
            cameraObject.tag = "MainCamera";
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.007f, 0.008f, 0.010f, 1f);
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 8f;
            camera.fieldOfView = 28.5f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.transform.position = new Vector3(0f, 0.006f, -1.30f);
            camera.transform.LookAt(new Vector3(0f, -0.006f, 0f), Vector3.up);
            return camera;
        }

        private static void BuildLighting(out Light openingLight)
        {
            CreateDirectionalLight(
                "WarmNeutralKey",
                Quaternion.Euler(37f, -31f, 0f),
                new Color(1f, 0.91f, 0.78f),
                1.34f);
            CreateDirectionalLight(
                "NeutralFill",
                Quaternion.Euler(59f, 136f, 0f),
                new Color(0.64f, 0.70f, 0.76f),
                0.42f);
            CreateDirectionalLight(
                "ControlledMetalRim",
                Quaternion.Euler(17f, 208f, 0f),
                new Color(0.92f, 0.89f, 0.82f),
                0.68f);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.080f, 0.080f, 0.084f);
            RenderSettings.reflectionIntensity = 0.45f;

            var lightObject = new GameObject("OpeningOriginEnergyLight");
            openingLight = lightObject.AddComponent<Light>();
            openingLight.type = LightType.Point;
            openingLight.range = 0.42f;
            openingLight.intensity = 0f;
            openingLight.color = new Color(0.58f, 0.42f, 0.72f);
            openingLight.shadows = LightShadows.None;
            openingLight.transform.position = new Vector3(0f, 0.045f, -0.08f);
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
            var motionObject = new GameObject("OneSettlingCaseReveal");
            caseMotionRoot = motionObject.transform;
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
            caseMotionRoot.gameObject.SetActive(false);
            return presentation;
        }

        private static void BuildPack(
            MaterialSet materials,
            out Renderer bodyRenderer,
            out MeshFilter flapFilter,
            out Renderer flapRenderer,
            out MeshFilter rimFilter,
            out Renderer rimRenderer)
        {
            var root = new GameObject("ActualAuthoredStandardPack");
            root.transform.position = new Vector3(0f, 0.016f, -0.42f);

            GameObject body = GameObject.CreatePrimitive(PrimitiveType.Quad);
            body.name = "Actual384x512PackBody";
            body.transform.SetParent(root.transform, false);
            body.transform.localPosition = Vector3.zero;
            body.transform.localScale = new Vector3(0.145f, 0.145f * 4f / 3f, 1f);
            UnityEngine.Object.DestroyImmediate(body.GetComponent<Collider>());
            bodyRenderer = body.GetComponent<MeshRenderer>();
            bodyRenderer.sharedMaterial = materials.PackBody;
            bodyRenderer.shadowCastingMode = ShadowCastingMode.Off;
            bodyRenderer.receiveShadows = false;

            var flap = new GameObject("ProgressiveDeformingActualPackFlap");
            flap.transform.SetParent(root.transform, false);
            flap.transform.localPosition = Vector3.zero;
            flapFilter = flap.AddComponent<MeshFilter>();
            flapRenderer = flap.AddComponent<MeshRenderer>();
            flapRenderer.sharedMaterial = materials.PackFlap;
            flapRenderer.shadowCastingMode = ShadowCastingMode.Off;
            flapRenderer.receiveShadows = false;
            flapRenderer.sortingOrder = 30;

            var rim = new GameObject("IrregularTornFoilThickness");
            rim.transform.SetParent(root.transform, false);
            rim.transform.localPosition = new Vector3(0f, 0f, 0.003f);
            rimFilter = rim.AddComponent<MeshFilter>();
            rimRenderer = rim.AddComponent<MeshRenderer>();
            rimRenderer.sharedMaterial = materials.TornEdge;
            rimRenderer.shadowCastingMode = ShadowCastingMode.Off;
            rimRenderer.receiveShadows = false;
            rimRenderer.sortingOrder = 20;
        }

        private static void BuildImpact(
            MaterialSet materials,
            MeshSet meshes,
            out Transform localizedFlash,
            out Renderer localizedFlashRenderer,
            out Transform shockwave,
            out Renderer shockwaveRenderer,
            out ParticleSystem foilShards,
            out ParticleSystem glints,
            out ParticleSystem directionalStreaks)
        {
            var root = new GameObject("OpeningOriginImpact");

            GameObject flashObject = CreateMeshObject(
                root.transform,
                "OneFrameLocalizedNearWhiteFlash",
                meshes.Star,
                materials.Flash);
            flashObject.transform.position = new Vector3(0f, 0.045f, -0.15f);
            flashObject.SetActive(false);
            localizedFlash = flashObject.transform;
            localizedFlashRenderer = flashObject.GetComponent<Renderer>();

            GameObject shockwaveObject = CreateMeshObject(
                root.transform,
                "OneThinFastShockwaveBehindProduct",
                meshes.Ring,
                materials.Shockwave);
            shockwaveObject.transform.position = new Vector3(0f, 0.045f, 0.12f);
            shockwaveObject.SetActive(false);
            shockwave = shockwaveObject.transform;
            shockwaveRenderer = shockwaveObject.GetComponent<Renderer>();

            foilShards = CreateParticleSystem(
                root.transform,
                "AuthoredFoilShards",
                meshes.Shard,
                materials.Shard,
                5,
                0.008f,
                0.24f,
                0.15f,
                new Color(0.92f, 0.88f, 0.78f, 0.96f),
                9137u);
            glints = CreateParticleSystem(
                root.transform,
                "RestrainedWarmGlints",
                meshes.Glint,
                materials.Glint,
                4,
                0.008f,
                0.17f,
                0.13f,
                new Color(1f, 0.94f, 0.78f, 0.94f),
                4201u);
            directionalStreaks = CreateParticleSystem(
                root.transform,
                "DirectionalOpeningStreaks",
                meshes.Streak,
                materials.Streak,
                4,
                0.012f,
                0.26f,
                0.15f,
                new Color(0.52f, 0.38f, 0.70f, 0.62f),
                7129u);
        }

        private static ParticleSystem CreateParticleSystem(
            Transform parent,
            string name,
            Mesh mesh,
            Material material,
            short count,
            float size,
            float speed,
            float lifetime,
            Color color,
            uint randomSeed)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            item.transform.position = new Vector3(0f, 0.045f, -0.12f);
            ParticleSystem system = item.AddComponent<ParticleSystem>();
            ParticleSystem.MainModule main = system.main;
            main.loop = false;
            main.playOnAwake = false;
            main.duration = 0.5f;
            main.startLifetime = lifetime;
            main.startSpeed = speed;
            main.startSize = size;
            main.startColor = color;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.gravityModifier = 0.12f;
            main.maxParticles = count;

            ParticleSystem.EmissionModule emission = system.emission;
            emission.rateOverTime = 0f;
            emission.SetBursts(new[]
            {
                new ParticleSystem.Burst(0f, count)
            });
            ParticleSystem.ShapeModule shape = system.shape;
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = 0.018f;
            shape.radiusThickness = 1f;
            shape.rotation = Vector3.zero;

            ParticleSystem.RotationOverLifetimeModule rotation =
                system.rotationOverLifetime;
            rotation.enabled = true;
            rotation.z = new ParticleSystem.MinMaxCurve(
                -4.2f,
                4.2f);
            ParticleSystem.ColorOverLifetimeModule colorOverLifetime =
                system.colorOverLifetime;
            colorOverLifetime.enabled = true;
            colorOverLifetime.color = new ParticleSystem.MinMaxGradient(
                new Gradient
                {
                    alphaKeys = new[]
                    {
                        new GradientAlphaKey(0f, 0f),
                        new GradientAlphaKey(1f, 0.10f),
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

        private static Mesh CreateStarMesh()
        {
            const int points = 16;
            var vertices = new Vector3[points + 1];
            var uvs = new Vector2[points + 1];
            var triangles = new int[points * 3];
            vertices[0] = Vector3.zero;
            uvs[0] = new Vector2(0.5f, 0.5f);
            for (int index = 0; index < points; index++)
            {
                float angle = index / (float)points * Mathf.PI * 2f;
                float radius =
                    0.84f
                    + 0.09f * Mathf.Sin(index * 2.31f + 0.4f)
                    + 0.04f * Mathf.Sin(index * 4.17f + 1.1f);
                vertices[index + 1] = new Vector3(
                    Mathf.Cos(angle) * radius,
                    Mathf.Sin(angle) * radius * 0.42f,
                    0f);
                uvs[index + 1] = new Vector2(
                    0.5f + Mathf.Cos(angle) * 0.5f,
                    0.5f + Mathf.Sin(angle) * 0.5f);
                triangles[index * 3] = 0;
                triangles[index * 3 + 1] = index + 1;
                triangles[index * 3 + 2] = (index + 1) % points + 1;
            }
            return BuildMesh(vertices, uvs, triangles);
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
                vertices[index * 2 + 1] = direction * 0.989f;
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
                new Vector3(-0.55f, -0.35f, 0f),
                new Vector3(0.58f, -0.24f, 0.14f),
                new Vector3(-0.08f, 0.52f, -0.08f)
            };
            Vector2[] uvs =
            {
                Vector2.zero,
                Vector2.right,
                Vector2.up
            };
            return BuildMesh(vertices, uvs, new[] { 0, 1, 2 });
        }

        private static Mesh CreateGlintMesh()
        {
            Vector3[] vertices =
            {
                new Vector3(-0.12f, 0f, 0f),
                new Vector3(0f, -1f, 0f),
                new Vector3(0.12f, 0f, 0f),
                new Vector3(0f, 1f, 0f),
                new Vector3(-1f, 0f, 0f),
                new Vector3(0f, -0.12f, 0f),
                new Vector3(1f, 0f, 0f),
                new Vector3(0f, 0.12f, 0f)
            };
            Vector2[] uvs = Enumerable.Repeat(new Vector2(0.5f, 0.5f), 8).ToArray();
            return BuildMesh(
                vertices,
                uvs,
                new[] { 0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7 });
        }

        private static Mesh CreateStreakMesh()
        {
            Vector3[] vertices =
            {
                new Vector3(-1f, 0f, 0f),
                new Vector3(0.55f, -0.12f, 0f),
                new Vector3(1f, 0f, 0f),
                new Vector3(0.55f, 0.12f, 0f)
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

        private static GameObject CreateMeshObject(
            Transform parent,
            string name,
            Mesh mesh,
            Material material)
        {
            var item = new GameObject(name);
            item.transform.SetParent(parent, false);
            MeshFilter filter = item.AddComponent<MeshFilter>();
            filter.sharedMesh = mesh;
            MeshRenderer renderer = item.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            return item;
        }

        private static GameObject CreateCube(
            Transform parent,
            string name,
            Vector3 position,
            Vector3 scale,
            Material material)
        {
            GameObject item = GameObject.CreatePrimitive(PrimitiveType.Cube);
            item.name = name;
            item.transform.SetParent(parent, false);
            item.transform.position = position;
            item.transform.localScale = scale;
            UnityEngine.Object.DestroyImmediate(item.GetComponent<Collider>());
            item.GetComponent<MeshRenderer>().sharedMaterial = material;
            return item;
        }

        private static void CreateDirectionalLight(
            string name,
            Quaternion rotation,
            Color color,
            float intensity)
        {
            var item = new GameObject(name);
            item.transform.rotation = rotation;
            Light light = item.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
            light.shadowStrength = 0.34f;
        }

        private static PremiumDisplayCaseLabelData BuildAuthoritativeReviewLabel()
        {
            const string prefix =
                "fidgeting.gacha.preview.gate04-r009-unity.";
            var inventory = new GachaInventoryRuntime(
                prefix,
                new GachaSplitMix64(0x409009UL));
            GachaTransactionResult transaction =
                inventory.QueryTransaction("gate04-r009-real-unity");
            if (!transaction.Success)
            {
                inventory.PrimeGate12SimulatorPreview();
                transaction = inventory.PrepareDraw(
                    GachaCatalog.LaunchSeriesId,
                    1,
                    GachaPaymentMethod.Ticket,
                    "gate04-r009-real-unity");
            }
            if (!transaction.Success || transaction.Receipt.Rows.Count != 1)
            {
                throw new InvalidOperationException(
                    "Could not create the authoritative rev 9 review receipt.");
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
            Vector2Int sourceSize = ReadPngDimensions(
                Path.Combine(ProjectRoot, path));
            if (sourceSize.x != 384 || sourceSize.y != 512)
            {
                throw new InvalidOperationException(
                    $"{path} must preserve its authored 384x512 canvas, got {sourceSize.x}x{sourceSize.y}.");
            }
            return texture;
        }

        private static Vector2Int ReadPngDimensions(string absolutePath)
        {
            byte[] header = new byte[24];
            using FileStream stream = File.OpenRead(absolutePath);
            int read = stream.Read(header, 0, header.Length);
            if (
                read != header.Length
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
            string path = Path.Combine(ProjectRoot, EvidenceRoot, "unity-source-manifest.json");
            string controllerPath =
                CandidateRoot + "/Runtime/PackOpeningGate04R009Controller.cs";
            string profileSourcePath =
                CandidateRoot + "/Runtime/PackOpeningGate04R009Profile.cs";
            string capturePath =
                CandidateRoot + "/Runtime/PackOpeningGate04R009Capture.cs";
            string builderPath =
                CandidateRoot + "/Editor/PackOpeningGate04R009Builder.cs";
            string json =
                "{\n"
                + "  \"schema\": \"premium-display-case-gate04-r009-unity-source.v1\",\n"
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
                + $"    \"callerOwnedContentSha256\": \"{Sha256File(Path.Combine(ProjectRoot, ActualPrizePrefabPath))}\",\n"
                + "    \"wholeCaseOnly\": true,\n"
                + "    \"toyEdited\": false\n"
                + "  },\n"
                + "  \"sources\": {\n"
                + $"    \"controller\": \"{Sha256File(Path.Combine(ProjectRoot, controllerPath))}\",\n"
                + $"    \"profile\": \"{Sha256File(Path.Combine(ProjectRoot, profileSourcePath))}\",\n"
                + $"    \"capture\": \"{Sha256File(Path.Combine(ProjectRoot, capturePath))}\",\n"
                + $"    \"builder\": \"{Sha256File(Path.Combine(ProjectRoot, builderPath))}\"\n"
                + "  },\n"
                + "  \"rendering\": {\n"
                + "    \"vfxGraph\": false,\n"
                + "    \"shuriken\": true,\n"
                + "    \"postProcessingBloom\": false,\n"
                + "    \"chromaticAberration\": false,\n"
                + "    \"lensDistortion\": false,\n"
                + "    \"noiseParticles\": false\n"
                + "  },\n"
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
                sha.ComputeHash(stream).Select(value => value.ToString("x2", CultureInfo.InvariantCulture)));
        }

        private static string ProjectRoot =>
            Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

        private readonly struct MaterialSet
        {
            public MaterialSet(
                Material packBody,
                Material packFlap,
                Material tornEdge,
                Material flash,
                Material shockwave,
                Material shard,
                Material glint,
                Material streak,
                Material mineral,
                Material mineralRaised,
                Material plinth)
            {
                PackBody = packBody;
                PackFlap = packFlap;
                TornEdge = tornEdge;
                Flash = flash;
                Shockwave = shockwave;
                Shard = shard;
                Glint = glint;
                Streak = streak;
                Mineral = mineral;
                MineralRaised = mineralRaised;
                Plinth = plinth;
            }

            public Material PackBody { get; }
            public Material PackFlap { get; }
            public Material TornEdge { get; }
            public Material Flash { get; }
            public Material Shockwave { get; }
            public Material Shard { get; }
            public Material Glint { get; }
            public Material Streak { get; }
            public Material Mineral { get; }
            public Material MineralRaised { get; }
            public Material Plinth { get; }
        }

        private readonly struct MeshSet
        {
            public MeshSet(
                Mesh star,
                Mesh ring,
                Mesh shard,
                Mesh glint,
                Mesh streak)
            {
                Star = star;
                Ring = ring;
                Shard = shard;
                Glint = glint;
                Streak = streak;
            }

            public Mesh Star { get; }
            public Mesh Ring { get; }
            public Mesh Shard { get; }
            public Mesh Glint { get; }
            public Mesh Streak { get; }
        }
    }
}
