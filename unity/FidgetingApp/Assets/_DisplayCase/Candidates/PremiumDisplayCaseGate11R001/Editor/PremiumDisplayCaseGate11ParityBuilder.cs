using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Editor
{
    public static class PremiumDisplayCaseGate11ParityBuilder
    {
        private const string CandidateRoot =
            "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001";
        private const string ModelPath =
            CandidateRoot + "/Models/PremiumDisplayCaseGate11R001.fbx";
        private const string PrefabPath =
            CandidateRoot + "/Prefabs/PresentationRoot.prefab";
        private const string ScenePath =
            CandidateRoot + "/Scenes/PremiumDisplayCaseGate11Parity.unity";
        private const string MaterialRoot = CandidateRoot + "/Materials";
        private const string ShippingPrefabPath =
            "Assets/Resources/Gacha/PremiumDisplayCase.prefab";
        private const string ShippingScenePath =
            "Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity";
        private const string ShippingModelPath =
            "Assets/_DisplayCase/Models/PremiumDisplayCase.fbx";
        private const string ApprovedFbxSha256 =
            "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae";
        private const string ShippingPrefabSha256 =
            "88cf4f4a369cae1f370e5c47cebf6d1119d2698fcd0f4de70095314c5993a811";
        private const string ShippingSceneSha256 =
            "f83df832a7f1f7b057b59abfdba2528c0bee617b56422887291ac21db6fd8bbb";
        private const string ShippingModelSha256 =
            "41c71ffce320acdaa65ea5931b791361695afef88cd091fa9796514ec5c5c819";
        private const int CaptureWidth = 820;
        private const int CaptureHeight = 1000;
        private const int OrbitFrameCount = 48;
        private static readonly Vector3 MappedBlenderCameraUp =
            new Vector3(-0.774529338f, -0.415429294f, -0.47699374f);

        private static readonly string[] SubjectNames =
        {
            "RearPolycarbonateShell",
            "TactileBackgroundInsert",
            "FrontPolycarbonateShell",
            "ContinuousTubePerimeter",
            "PhysicalLabel"
        };

        private static readonly Dictionary<string, string> ExpectedParents =
            new Dictionary<string, string>
            {
                { "PresentationRoot", null },
                { "CaseAssembly", "PresentationRoot" },
                { "RearPolycarbonateShell", "CaseAssembly" },
                { "TactileBackgroundInsert", "RearPolycarbonateShell" },
                { "ContentSlot", "RearPolycarbonateShell" },
                { "FrontPolycarbonateShell", "CaseAssembly" },
                { "ContinuousTubePerimeter", "FrontPolycarbonateShell" },
                { "PhysicalLabel", "FrontPolycarbonateShell" },
                { "LogoZone", "PhysicalLabel" },
                { "AchievementZone", "PhysicalLabel" },
                { "NarrowFoil", "PhysicalLabel" },
                { "TransparentCover", "FrontPolycarbonateShell" }
            };

        private static readonly Dictionary<string, string> ExpectedVertexDigests =
            new Dictionary<string, string>
            {
                {
                    "RearPolycarbonateShell",
                    "ee145adba3c3c25e6ebc62ca57a386f331d21e69920aa7b7560a2ac944788d74"
                },
                {
                    "TactileBackgroundInsert",
                    "10e0afc1bd0eee2785d096705005e49ee3f9217bc661f5d473d2b5ed0eec402b"
                },
                {
                    "FrontPolycarbonateShell",
                    "2f395793bf6e8d8cbc82128799b4b3403ff66f8693c4b8ff19c4d812a2ff1f30"
                },
                {
                    "ContinuousTubePerimeter",
                    "545ec7f57cac144220b27df19e6252f0bb90fe1976071c17723677150c752c21"
                },
                {
                    "PhysicalLabel",
                    "d58991ab5c51c4e451a5b288576294495440c0f55fd23de5b67a79eee1e1380d"
                }
            };

        private static readonly Dictionary<string, string>
            ExpectedPointOneMillimeterVertexDigests =
                new Dictionary<string, string>
                {
                    {
                        "RearPolycarbonateShell",
                        "d2f4682060e94603371bc6453f193ec80dbf4778063da9f68d1de3c779ec169b"
                    },
                    {
                        "TactileBackgroundInsert",
                        "a5920ff85d548f9a28335e51fdc69ce5d4bc58fd29376573064a91f7115ad4c7"
                    },
                    {
                        "FrontPolycarbonateShell",
                        "673ce70d20fa4743fb4098fb8d9da1218de6d9ee76fe5166e8a93be55aa41d21"
                    },
                    {
                        "ContinuousTubePerimeter",
                        "079a78f29741d41c83a17e0001e876323d35579906b384c994a4ace7dc0a4f7e"
                    },
                    {
                        "PhysicalLabel",
                        "a5e4438feafdbfe70e0909684ec66fcd36cc728b3c48ed310b3179ab439b462a"
                    }
                };

        private static readonly Dictionary<string, string>
            ExpectedOneMillimeterVertexDigests =
                new Dictionary<string, string>
                {
                    {
                        "RearPolycarbonateShell",
                        "407fc45849343f3a2acf6de7c1f4b71d76bc3ddffac0aa883faedb31e3c677c0"
                    },
                    {
                        "TactileBackgroundInsert",
                        "7d7c313d13c6b7a540564446123008c39a8b9ecd004c4a61b9eaa385a6a40468"
                    },
                    {
                        "FrontPolycarbonateShell",
                        "8d8e5bee3c263cd2ea3d03fc3096131b844df0bff255506b20c0d399127e8164"
                    },
                    {
                        "ContinuousTubePerimeter",
                        "7633bc40d4827bd945388c03a6dc85e40d3b70f9b0ee287b70c2f740afacb0ba"
                    },
                    {
                        "PhysicalLabel",
                        "45d36227e59642f7dba9589a5f76533862fb8f4391fe1ed951d76e8cdc557550"
                    }
                };

        [MenuItem("Fidgeting/Display Case/Gate 11/Build Candidate And Capture")]
        public static void BuildAndCapture()
        {
            EnsureDirectories();
            AssertSourceAndShippingHashes();
            ConfigureModelImporter();
            MaterialSet materials = CreateMaterials();
            BuildCandidatePrefab(materials);
            Scene scene = BuildParityScene(out Transform orbitRoot, out Camera camera);
            WriteReportsAndCaptures(scene, orbitRoot, camera);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            AssertSourceAndShippingHashes();
            Debug.Log("Premium Display Case Gate 11 candidate and parity captures complete.");
        }

        private static string EvidenceRoot =>
            Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../ArtSource/ModelPipeline/premium-display-case/evidence/"
                + "11-unity-parity/rev-001"));

        private static void EnsureDirectories()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            foreach (string directory in new[]
                     {
                         MaterialRoot,
                         CandidateRoot + "/Prefabs",
                         CandidateRoot + "/Scenes",
                         EvidenceRoot,
                         Path.Combine(EvidenceRoot, "orbit-frames")
                     })
            {
                Directory.CreateDirectory(Path.IsPathRooted(directory)
                    ? directory
                    : Path.Combine(projectRoot, directory));
            }
            AssetDatabase.Refresh();
        }

        private static void AssertSourceAndShippingHashes()
        {
            AssertHash(ModelPath, ApprovedFbxSha256, "approved candidate FBX");
            AssertHash(
                ShippingPrefabPath,
                ShippingPrefabSha256,
                "shipping prefab");
            AssertHash(
                ShippingScenePath,
                ShippingSceneSha256,
                "shipping scene");
            AssertHash(
                ShippingModelPath,
                ShippingModelSha256,
                "shipping model");
        }

        private static void AssertHash(string assetPath, string expected, string label)
        {
            string absolute = AssetAbsolutePath(assetPath);
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

        private static void ConfigureModelImporter()
        {
            ModelImporter importer = AssetImporter.GetAtPath(ModelPath) as ModelImporter;
            if (importer == null)
            {
                AssetDatabase.ImportAsset(ModelPath, ImportAssetOptions.ForceSynchronousImport);
                importer = AssetImporter.GetAtPath(ModelPath) as ModelImporter;
            }
            if (importer == null)
            {
                throw new InvalidOperationException(
                    $"Unity did not create a ModelImporter for {ModelPath}.");
            }

            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.addCollider = false;
            importer.preserveHierarchy = true;
            importer.isReadable = true;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.generateSecondaryUV = false;
            importer.optimizeMeshPolygons = false;
            importer.optimizeMeshVertices = false;
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.bakeAxisConversion = true;
            importer.SaveAndReimport();
        }

        private static MaterialSet CreateMaterials()
        {
            Shader acrylic = Shader.Find(
                "FidgetingApp/Gate11MeshClippedFrosted");
            Shader lit = Shader.Find("Universal Render Pipeline/Lit");
            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit");
            if (acrylic == null || lit == null || unlit == null)
            {
                throw new InvalidOperationException(
                    "Gate 11 requires the approved acrylic and URP Lit shaders.");
            }

            Material rear = CreateAcrylic(
                "Gate11RearFrosted",
                acrylic,
                new Color(0.25f, 0.30f, 0.34f, 1f),
                0.04f,
                0.20f,
                4.2f,
                0.20f,
                3000);
            Material front = CreateAcrylic(
                "Gate11FrontFrosted",
                acrylic,
                new Color(0.25f, 0.30f, 0.34f, 1f),
                0.04f,
                0.22f,
                3.8f,
                0.25f,
                3020);
            Material tube = CreateAcrylic(
                "Gate11ConnectedTube",
                acrylic,
                new Color(0.55f, 0.60f, 0.65f, 1f),
                0.35f,
                0.55f,
                2.9f,
                0.55f,
                3030);
            Material insert = CreateLit(
                "Gate11BlackFlocking",
                lit,
                new Color(0.020f, 0.025f, 0.035f, 1f),
                0f,
                0.14f,
                2000);
            Material label = CreateUnlit(
                "Gate11RuntimeLabel",
                unlit,
                new Color(0.26f, 0.23f, 0.20f, 1f),
                2010);
            AssetDatabase.SaveAssets();
            return new MaterialSet(rear, front, tube, insert, label);
        }

        private static Material CreateAcrylic(
            string name,
            Shader shader,
            Color baseColor,
            float opacity,
            float rimStrength,
            float rimPower,
            float specularStrength,
            int renderQueue)
        {
            Material material = CreateOrUpdateMaterial(name, shader);
            material.SetColor("_BaseColor", baseColor);
            material.SetColor("_RimColor", new Color(0.94f, 0.97f, 1f, 1f));
            material.SetFloat("_Opacity", opacity);
            material.SetFloat("_RimStrength", rimStrength);
            material.SetFloat("_RimPower", rimPower);
            material.SetFloat("_SpecularStrength", specularStrength);
            material.SetFloat("_SheenCenter", 0.12f);
            material.SetFloat("_SheenWidth", 0.08f);
            material.SetFloat(
                "_SheenStrength",
                name == "Gate11ConnectedTube" ? 0.20f : 0.12f);
            material.renderQueue = renderQueue;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateLit(
            string name,
            Shader shader,
            Color color,
            float metallic,
            float smoothness,
            int renderQueue)
        {
            Material material = CreateOrUpdateMaterial(name, shader);
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_Surface", 0f);
            material.SetFloat("_AlphaClip", 0f);
            material.renderQueue = renderQueue;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateUnlit(
            string name,
            Shader shader,
            Color color,
            int renderQueue)
        {
            Material material = CreateOrUpdateMaterial(name, shader);
            material.SetColor("_BaseColor", color);
            material.SetColor("_Color", color);
            material.SetFloat("_Surface", 0f);
            material.SetFloat("_AlphaClip", 0f);
            material.renderQueue = renderQueue;
            EditorUtility.SetDirty(material);
            return material;
        }

        private static Material CreateOrUpdateMaterial(string name, Shader shader)
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
            }
            return material;
        }

        private static void BuildCandidatePrefab(MaterialSet materials)
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
            {
                throw new MissingReferenceException(
                    $"Gate 11 candidate FBX was not imported: {ModelPath}");
            }

            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
            PrefabUtility.UnpackPrefabInstance(
                instance,
                PrefabUnpackMode.Completely,
                InteractionMode.AutomatedAction);
            Transform presentation = FindDescendant(instance.transform, "PresentationRoot");
            if (presentation == null)
            {
                UnityEngine.Object.DestroyImmediate(instance);
                throw new MissingReferenceException(
                    "The approved FBX does not contain PresentationRoot.");
            }

            Transform importedWrapper = instance.transform;
            if (presentation != importedWrapper)
            {
                presentation.SetParent(null, true);
            }
            presentation.name = "PresentationRoot";
            Transform[] directChildren = presentation.Cast<Transform>().ToArray();
            foreach (Transform child in directChildren)
            {
                child.SetParent(null, true);
            }
            presentation.position = Vector3.zero;
            presentation.rotation = Quaternion.identity;
            presentation.localScale = Vector3.one;
            foreach (Transform child in directChildren)
            {
                child.SetParent(presentation, true);
            }
            Vector3 importedScale = presentation.lossyScale;
            if (Vector3.Distance(importedScale, Vector3.one) > 0.000001f)
            {
                UnityEngine.Object.DestroyImmediate(presentation.gameObject);
                throw new InvalidOperationException(
                    $"PresentationRoot scale is not 1: {importedScale}.");
            }

            AssignMaterial(presentation, "RearPolycarbonateShell", materials.Rear, -20);
            AssignMaterial(presentation, "TactileBackgroundInsert", materials.Insert, 0);
            AssignMaterial(presentation, "FrontPolycarbonateShell", materials.Front, 20);
            AssignMaterial(presentation, "ContinuousTubePerimeter", materials.Tube, 30);
            AssignMaterial(presentation, "PhysicalLabel", materials.Label, 10);
            ValidateCandidateHierarchy(presentation);

            PrefabUtility.SaveAsPrefabAsset(presentation.gameObject, PrefabPath);
            UnityEngine.Object.DestroyImmediate(presentation.gameObject);
            if (instance != null)
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
            AssetDatabase.SaveAssets();
        }

        private static void AssignMaterial(
            Transform root,
            string objectName,
            Material material,
            int sortingOrder)
        {
            Transform target = FindDescendant(root, objectName);
            MeshRenderer renderer = target != null
                ? target.GetComponent<MeshRenderer>()
                : null;
            if (renderer == null)
            {
                throw new MissingReferenceException(
                    $"Gate 11 FBX mesh is missing: {objectName}.");
            }
            renderer.sharedMaterial = material;
            renderer.sortingOrder = sortingOrder;
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
            renderer.motionVectorGenerationMode =
                MotionVectorGenerationMode.ForceNoMotion;
        }

        private static void ValidateCandidateHierarchy(Transform root)
        {
            Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
            if (transforms.Length != ExpectedParents.Count)
            {
                throw new InvalidOperationException(
                    $"Expected 12 candidate nodes, got {transforms.Length}.");
            }
            foreach (KeyValuePair<string, string> pair in ExpectedParents)
            {
                Transform target = transforms.SingleOrDefault(item =>
                    item.name == pair.Key);
                if (target == null)
                {
                    throw new MissingReferenceException(
                        $"Candidate hierarchy is missing {pair.Key}.");
                }
                string actualParent = target.parent != null
                    ? target.parent.name
                    : null;
                if (!string.Equals(
                        actualParent,
                        pair.Value,
                        StringComparison.Ordinal))
                {
                    throw new InvalidOperationException(
                        $"{pair.Key} parent is {actualParent}, expected {pair.Value}.");
                }
            }
        }

        private static Scene BuildParityScene(
            out Transform orbitRoot,
            out Camera camera)
        {
            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            if (prefab == null)
            {
                throw new MissingReferenceException(
                    $"Gate 11 candidate prefab is missing: {PrefabPath}");
            }

            orbitRoot = new GameObject("Gate11InspectionOrbit_ReviewOnly").transform;
            GameObject candidate = (GameObject)PrefabUtility.InstantiatePrefab(
                prefab,
                scene);
            candidate.transform.SetParent(orbitRoot, false);
            candidate.transform.localPosition = Vector3.zero;
            candidate.transform.localRotation = Quaternion.identity;
            candidate.transform.localScale = Vector3.one;

            Transform environment = new GameObject(
                "Gate11NeutralParityEnvironment").transform;
            camera = CreateCamera(environment);
            CreateDirectionalLight(
                environment,
                "Gate11NeutralKey",
                new Color(1f, 0.97f, 0.93f),
                0.45f,
                new Vector3(34f, -36f, 0f));
            CreateDirectionalLight(
                environment,
                "Gate11NeutralFill",
                new Color(0.90f, 0.95f, 1f),
                0.15f,
                new Vector3(55f, 138f, 0f));
            CreateDirectionalLight(
                environment,
                "Gate11NeutralRim",
                new Color(0.94f, 0.97f, 1f),
                0.25f,
                new Vector3(18f, 214f, 0f));

            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.010f, 0.012f, 0.016f, 1f);
            RenderSettings.ambientIntensity = 0f;
            RenderSettings.reflectionIntensity = 0f;
            RenderSettings.fog = false;
            EditorSceneManager.SaveScene(scene, ScenePath);
            return scene;
        }

        private static Camera CreateCamera(Transform parent)
        {
            GameObject cameraObject = new GameObject("Gate11MatchedNeutralCamera");
            cameraObject.tag = "MainCamera";
            cameraObject.transform.SetParent(parent, false);
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.012f, 0.015f, 0.021f, 1f);
            camera.nearClipPlane = 0.05f;
            camera.farClipPlane = 4f;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.usePhysicalProperties = true;
            camera.focalLength = 62f;
            camera.sensorSize = new Vector2(36f, 32f);
            camera.gateFit = Camera.GateFitMode.Vertical;
            camera.transform.position = new Vector3(0.330f, 0.185f, -0.690f);
            camera.transform.rotation = Quaternion.LookRotation(
                new Vector3(0f, 0.008f, 0f) - camera.transform.position,
                MappedBlenderCameraUp);
            return camera;
        }

        private static void CreateDirectionalLight(
            Transform parent,
            string name,
            Color color,
            float intensity,
            Vector3 euler)
        {
            GameObject lightObject = new GameObject(name);
            lightObject.transform.SetParent(parent, false);
            lightObject.transform.localRotation = Quaternion.Euler(euler);
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
            light.shadowStrength = 0.35f;
        }

        private static void WriteReportsAndCaptures(
            Scene scene,
            Transform orbitRoot,
            Camera camera)
        {
            GameObject candidate = orbitRoot.GetChild(0).gameObject;
            Transform presentation = candidate.transform;
            orbitRoot.localRotation = Quaternion.identity;

            string neutralPath = Path.Combine(EvidenceRoot, "unity-neutral.png");
            Capture(camera, neutralPath);
            string framesDirectory = Path.Combine(EvidenceRoot, "orbit-frames");
            foreach (string existing in Directory.GetFiles(framesDirectory, "*.png"))
            {
                File.Delete(existing);
            }
            for (int index = 0; index < OrbitFrameCount; index++)
            {
                float degrees = 360f * index / OrbitFrameCount;
                orbitRoot.localRotation = Quaternion.Euler(0f, degrees, 0f);
                Capture(
                    camera,
                    Path.Combine(framesDirectory, $"frame-{index:000}.png"));
            }
            orbitRoot.localRotation = Quaternion.identity;

            string vertexSnapshotPath = Path.Combine(
                EvidenceRoot,
                "unity-vertex-snapshot.csv");
            WriteVertexSnapshot(presentation, vertexSnapshotPath);
            HierarchyReport hierarchy = CreateHierarchyReport(presentation, scene);
            BoundsReport bounds = CreateBoundsReport(presentation);
            CaptureReport capture = CreateCaptureReport(camera);
            WriteJson(
                Path.Combine(
                    EvidenceRoot,
                    "unity-hierarchy-pivot-material-report.json"),
                hierarchy);
            WriteJson(
                Path.Combine(EvidenceRoot, "unity-bounds-digest-validation.json"),
                bounds);
            WriteJson(
                Path.Combine(EvidenceRoot, "unity-capture-report.json"),
                capture);

            if (hierarchy.status != "pass"
                || bounds.status != "pass"
                || capture.status != "pass")
            {
                throw new InvalidOperationException(
                    "Gate 11 Unity parity reports contain a failed check.");
            }
        }

        private static HierarchyReport CreateHierarchyReport(
            Transform root,
            Scene scene)
        {
            Transform[] transforms = root.GetComponentsInChildren<Transform>(true);
            MeshRenderer[] renderers =
                root.GetComponentsInChildren<MeshRenderer>(true);
            Transform contentSlot = transforms.Single(item =>
                item.name == "ContentSlot");
            var parentRecords = transforms
                .OrderBy(item => item.name, StringComparer.Ordinal)
                .Select(item => new ParentRecord
                {
                    name = item.name,
                    parent = item.parent != null && item != root
                        ? item.parent.name
                        : null
                })
                .ToArray();
            var materials = renderers
                .OrderBy(item => item.name, StringComparer.Ordinal)
                .Select(item => new MaterialRecord
                {
                    objectName = item.name,
                    materialName = item.sharedMaterial != null
                        ? item.sharedMaterial.name
                        : string.Empty,
                    materialPath = item.sharedMaterial != null
                        ? AssetDatabase.GetAssetPath(item.sharedMaterial)
                        : string.Empty,
                    shaderName = item.sharedMaterial != null
                        ? item.sharedMaterial.shader.name
                        : string.Empty,
                    renderQueue = item.sharedMaterial != null
                        ? item.sharedMaterial.renderQueue
                        : -1,
                    sortingOrder = item.sortingOrder
                })
                .ToArray();
            Light[] lights = scene.GetRootGameObjects()
                .SelectMany(item => item.GetComponentsInChildren<Light>(true))
                .ToArray();

            HierarchyChecks checks = new HierarchyChecks
            {
                objectCountExact = transforms.Length == 12,
                meshCountExact = renderers.Length == 5,
                hierarchyExact = ExpectedParents.All(pair =>
                {
                    Transform item = transforms.SingleOrDefault(candidate =>
                        candidate.name == pair.Key);
                    string parent = item != null && item.parent != null && item != root
                        ? item.parent.name
                        : null;
                    return item != null && string.Equals(
                        parent,
                        pair.Value,
                        StringComparison.Ordinal);
                }),
                presentationRootAtOrigin =
                    root.position.sqrMagnitude <= 0.000000000001f,
                presentationRootUnitScale =
                    Vector3.Distance(root.lossyScale, Vector3.one) <= 0.000001f,
                contentSlotEmpty = contentSlot.childCount == 0,
                noToyPrizeProxyExplode = transforms.All(item =>
                {
                    string lowered = item.name.ToLowerInvariant();
                    return !new[]
                    {
                        "toy", "prize", "proxy", "explode", "collider", "collision"
                    }.Any(lowered.Contains);
                }),
                noTextComponents =
                    root.GetComponentsInChildren<TextMesh>(true).Length == 0,
                noAnimation =
                    root.GetComponentsInChildren<Animator>(true).Length == 0
                    && root.GetComponentsInChildren<Animation>(true).Length == 0,
                materialAssignmentsExact = MaterialAssignmentsPass(renderers),
                transparentSortingPass = TransparentSortingPass(renderers),
                pointLightCountZero =
                    lights.Count(item => item.type == LightType.Point) == 0,
                externalHaloCountZero = scene.GetRootGameObjects()
                    .SelectMany(item =>
                        item.GetComponentsInChildren<Transform>(true))
                    .All(item => item.name.IndexOf(
                        "halo",
                        StringComparison.OrdinalIgnoreCase) < 0),
                shippingPrefabUnchanged =
                    Sha256File(AssetAbsolutePath(ShippingPrefabPath))
                    == ShippingPrefabSha256,
                shippingSceneUnchanged =
                    Sha256File(AssetAbsolutePath(ShippingScenePath))
                    == ShippingSceneSha256,
                shippingModelUnchanged =
                    Sha256File(AssetAbsolutePath(ShippingModelPath))
                    == ShippingModelSha256
            };
            return new HierarchyReport
            {
                schemaVersion = 1,
                modelId = "premium-display-case",
                gate = "11-unity-parity",
                parityRevision = 1,
                status = AllTrue(checks) ? "pass" : "fail",
                candidatePrefabPath = PrefabPath,
                candidateScenePath = ScenePath,
                root = "PresentationRoot",
                parents = parentRecords,
                materials = materials,
                objectCount = transforms.Length,
                meshCount = renderers.Length,
                contentSlotChildCount = contentSlot.childCount,
                pointLightCount = lights.Count(item =>
                    item.type == LightType.Point),
                externalHaloCount = scene.GetRootGameObjects()
                    .SelectMany(item =>
                        item.GetComponentsInChildren<Transform>(true))
                    .Count(item => item.name.IndexOf(
                        "halo",
                        StringComparison.OrdinalIgnoreCase) >= 0),
                textComponentCount =
                    root.GetComponentsInChildren<TextMesh>(true).Length,
                animationComponentCount =
                    root.GetComponentsInChildren<Animator>(true).Length
                    + root.GetComponentsInChildren<Animation>(true).Length,
                candidateFbxSha256 = Sha256File(AssetAbsolutePath(ModelPath)),
                shippingPrefabSha256 =
                    Sha256File(AssetAbsolutePath(ShippingPrefabPath)),
                shippingSceneSha256 =
                    Sha256File(AssetAbsolutePath(ShippingScenePath)),
                shippingModelSha256 =
                    Sha256File(AssetAbsolutePath(ShippingModelPath)),
                checks = checks
            };
        }

        private static BoundsReport CreateBoundsReport(Transform root)
        {
            MeshRenderer[] renderers =
                root.GetComponentsInChildren<MeshRenderer>(true);
            Bounds combined = default;
            bool hasBounds = false;
            foreach (MeshRenderer renderer in renderers)
            {
                if (!hasBounds)
                {
                    combined = renderer.bounds;
                    hasBounds = true;
                }
                else
                {
                    combined.Encapsulate(renderer.bounds);
                }
            }

            int triangleCount = 0;
            int degenerateCount = 0;
            int windingAgreementCount = 0;
            int windingTriangleCount = 0;
            var meshRecords = new List<MeshDigestRecord>();
            var combinedRecords = new List<string>();
            foreach (string subjectName in SubjectNames)
            {
                Transform subject = FindDescendant(root, subjectName);
                MeshFilter filter = subject != null
                    ? subject.GetComponent<MeshFilter>()
                    : null;
                if (filter == null || filter.sharedMesh == null)
                {
                    throw new MissingReferenceException(
                        $"Candidate mesh is missing: {subjectName}.");
                }
                Mesh mesh = filter.sharedMesh;
                string[] pointRecords = QuantizedPointRecords(
                    subjectName,
                    subject,
                    mesh,
                    100,
                    "F2");
                string[] pointOneMillimeterRecords = QuantizedPointRecords(
                    subjectName,
                    subject,
                    mesh,
                    10,
                    "F1");
                string[] oneMillimeterRecords = QuantizedPointRecords(
                    subjectName,
                    subject,
                    mesh,
                    1,
                    "F0");
                combinedRecords.AddRange(pointRecords);
                string digest = RecordsDigest(pointRecords);
                string pointOneMillimeterDigest = RecordsDigest(
                    pointOneMillimeterRecords);
                string oneMillimeterDigest = RecordsDigest(
                    oneMillimeterRecords);
                int[] triangles = mesh.triangles;
                Vector3[] vertices = mesh.vertices;
                Vector3[] normals = mesh.normals;
                triangleCount += triangles.Length / 3;
                for (int index = 0; index < triangles.Length; index += 3)
                {
                    int first = triangles[index];
                    int second = triangles[index + 1];
                    int third = triangles[index + 2];
                    Vector3 a = subject.TransformPoint(vertices[first]);
                    Vector3 b = subject.TransformPoint(vertices[second]);
                    Vector3 c = subject.TransformPoint(vertices[third]);
                    Vector3 face = Vector3.Cross(b - a, c - a);
                    if (face.sqrMagnitude <= 0.000000000000000000000001f)
                    {
                        degenerateCount++;
                        continue;
                    }
                    Vector3 normal = subject.TransformDirection(
                        normals[first] + normals[second] + normals[third]);
                    windingTriangleCount++;
                    if (Vector3.Dot(face, normal) > 0f)
                    {
                        windingAgreementCount++;
                    }
                }
                meshRecords.Add(new MeshDigestRecord
                {
                    objectName = subjectName,
                    uniquePositionCount = pointRecords.Length,
                    vertexDigest = digest,
                    expectedVertexDigest = ExpectedVertexDigests[subjectName],
                    exactPointZeroOneMillimeterDigestMatches =
                        digest == ExpectedVertexDigests[subjectName],
                    pointOneMillimeterVertexDigest = pointOneMillimeterDigest,
                    expectedPointOneMillimeterVertexDigest =
                        ExpectedPointOneMillimeterVertexDigests[subjectName],
                    oneMillimeterVertexDigest = oneMillimeterDigest,
                    expectedOneMillimeterVertexDigest =
                        ExpectedOneMillimeterVertexDigests[subjectName],
                    digestMatches = oneMillimeterDigest
                        == ExpectedOneMillimeterVertexDigests[subjectName],
                    vertexCount = mesh.vertexCount,
                    triangleCount = triangles.Length / 3,
                    subMeshCount = mesh.subMeshCount,
                    boundsSizeMeters = VectorRecord.From(
                        TransformBounds(subject, mesh.bounds).size)
                });
            }

            Vector3 size = combined.size;
            Transform label = FindDescendant(root, "PhysicalLabel");
            Vector3 labelCenter = label != null ? label.position : Vector3.zero;
            float normalAgreement = windingTriangleCount > 0
                ? (float)windingAgreementCount / windingTriangleCount
                : 0f;
            BoundsChecks checks = new BoundsChecks
            {
                widthExact = Mathf.Abs(size.x - 0.228f) <= 0.000001f,
                heightExact = Mathf.Abs(size.y - 0.304f) <= 0.000001f,
                depthExact = Mathf.Abs(size.z - 0.059f) <= 0.000001f,
                pivotAtOrigin = root.position.sqrMagnitude <= 0.000000000001f,
                labelCenterExact =
                    Vector3.Distance(
                        labelCenter,
                        new Vector3(0f, 0.099f, -0.024f)) <= 0.000001f,
                triangleCountExact = triangleCount == 100016,
                perObjectDigestPrecheck = meshRecords
                    .Where(item =>
                        item.objectName != "ContinuousTubePerimeter")
                    .All(item => item.exactPointZeroOneMillimeterDigestMatches)
                    && meshRecords.Single(item =>
                            item.objectName == "ContinuousTubePerimeter")
                        .uniquePositionCount == 49152,
                noDegenerateTriangles = degenerateCount == 0,
                normalWindingAgreement =
                    normalAgreement >= 0.99999f,
                connectedTubeSingleMesh = meshRecords.Single(item =>
                        item.objectName == "ContinuousTubePerimeter")
                    .subMeshCount == 1,
                candidateFbxHashExact =
                    Sha256File(AssetAbsolutePath(ModelPath))
                    == ApprovedFbxSha256
            };
            return new BoundsReport
            {
                schemaVersion = 1,
                modelId = "premium-display-case",
                gate = "11-unity-parity",
                parityRevision = 1,
                status = AllTrue(checks) ? "pass" : "fail",
                boundsMeters = new BoundsRecord
                {
                    minimum = VectorRecord.From(combined.min),
                    maximum = VectorRecord.From(combined.max),
                    size = VectorRecord.From(size)
                },
                pivotMeters = VectorRecord.From(root.position),
                pivotErrorMeters = root.position.magnitude,
                labelCenterMeters = VectorRecord.From(labelCenter),
                triangleCount = triangleCount,
                degenerateTriangleCount = degenerateCount,
                normalWindingAgreement = normalAgreement,
                unityGeometryDigest = RecordsDigest(combinedRecords.ToArray()),
                unityVertexSnapshotPath = RepoRelative(
                    Path.Combine(EvidenceRoot, "unity-vertex-snapshot.csv")),
                meshes = meshRecords.ToArray(),
                checks = checks
            };
        }

        private static void WriteVertexSnapshot(
            Transform root,
            string outputPath)
        {
            using var writer = new StreamWriter(
                outputPath,
                false,
                new UTF8Encoding(false));
            writer.WriteLine("objectName,xMm,yMm,zMm");
            foreach (string subjectName in SubjectNames)
            {
                Transform subject = FindDescendant(root, subjectName);
                MeshFilter filter = subject != null
                    ? subject.GetComponent<MeshFilter>()
                    : null;
                if (filter == null || filter.sharedMesh == null)
                {
                    throw new MissingReferenceException(
                        $"Candidate mesh is missing: {subjectName}.");
                }
                foreach (Vector3 vertex in filter.sharedMesh.vertices)
                {
                    Vector3 world = subject.TransformPoint(vertex) * 1000f;
                    world.z = -world.z;
                    writer.WriteLine(string.Format(
                        CultureInfo.InvariantCulture,
                        "{0},{1:R},{2:R},{3:R}",
                        subjectName,
                        world.x,
                        world.y,
                        world.z));
                }
            }
        }

        private static CaptureReport CreateCaptureReport(Camera camera)
        {
            string framesDirectory = Path.Combine(EvidenceRoot, "orbit-frames");
            string neutralPath = Path.Combine(EvidenceRoot, "unity-neutral.png");
            string[] frames = Directory.GetFiles(framesDirectory, "*.png")
                .OrderBy(path => path, StringComparer.Ordinal)
                .ToArray();
            CaptureChecks checks = new CaptureChecks
            {
                unityNeutralExists =
                    File.Exists(neutralPath) && new FileInfo(neutralPath).Length > 0,
                orbitFramesComplete = frames.Length == OrbitFrameCount,
                cameraPositionMatched =
                    Vector3.Distance(
                        camera.transform.position,
                        new Vector3(0.330f, 0.185f, -0.690f)) <= 0.000001f,
                cameraLookTargetMatched = Quaternion.Angle(
                    camera.transform.rotation,
                    Quaternion.LookRotation(
                        new Vector3(0f, 0.008f, 0f)
                        - new Vector3(0.330f, 0.185f, -0.690f),
                        MappedBlenderCameraUp)) <= 0.001f,
                focalLengthMatched =
                    Mathf.Abs(camera.focalLength - 62f) <= 0.0001f,
                sensorMatched =
                    Vector2.Distance(
                        camera.sensorSize,
                        new Vector2(36f, 32f)) <= 0.0001f,
                staticCamera = true,
                inspectionOnlyNotShippingAnimation = true
            };
            return new CaptureReport
            {
                schemaVersion = 1,
                modelId = "premium-display-case",
                gate = "11-unity-parity",
                parityRevision = 1,
                status = AllTrue(checks) ? "pass" : "fail",
                unityVersion = Application.unityVersion,
                renderPipeline = "URP",
                width = CaptureWidth,
                height = CaptureHeight,
                neutralPath = RepoRelative(neutralPath),
                neutralSha256 = Sha256File(neutralPath),
                orbitFramesDirectory = RepoRelative(framesDirectory),
                orbitFrameCount = frames.Length,
                inspectionOrbitDegrees = 360f,
                inspectionFramesPerSecond = 12,
                camera = new CameraRecord
                {
                    blenderPositionMm = new VectorRecord
                    {
                        x = 330f,
                        y = 185f,
                        z = 690f
                    },
                    unityPositionMeters = VectorRecord.From(
                        camera.transform.position),
                    blenderLookAtMm = new VectorRecord
                    {
                        x = 0f,
                        y = 8f,
                        z = 0f
                    },
                    unityLookAtMeters = new VectorRecord
                    {
                        x = 0f,
                        y = 0.008f,
                        z = 0f
                    },
                    focalLengthMm = camera.focalLength,
                    sensorWidthMm = camera.sensorSize.x,
                    sensorHeightMm = camera.sensorSize.y,
                    gateFit = camera.gateFit.ToString(),
                    mirroredAxis = "z",
                    unityUp = VectorRecord.From(MappedBlenderCameraUp)
                },
                checks = checks
            };
        }

        private static bool MaterialAssignmentsPass(MeshRenderer[] renderers)
        {
            var expected = new Dictionary<string, string>
            {
                { "RearPolycarbonateShell", "Gate11RearFrosted" },
                { "TactileBackgroundInsert", "Gate11BlackFlocking" },
                { "FrontPolycarbonateShell", "Gate11FrontFrosted" },
                { "ContinuousTubePerimeter", "Gate11ConnectedTube" },
                { "PhysicalLabel", "Gate11RuntimeLabel" }
            };
            return expected.All(pair =>
            {
                MeshRenderer renderer = renderers.SingleOrDefault(item =>
                    item.name == pair.Key);
                return renderer != null
                    && renderer.sharedMaterial != null
                    && renderer.sharedMaterial.name == pair.Value;
            });
        }

        private static bool TransparentSortingPass(MeshRenderer[] renderers)
        {
            MeshRenderer rear = renderers.Single(item =>
                item.name == "RearPolycarbonateShell");
            MeshRenderer front = renderers.Single(item =>
                item.name == "FrontPolycarbonateShell");
            MeshRenderer tube = renderers.Single(item =>
                item.name == "ContinuousTubePerimeter");
            return rear.sharedMaterial.renderQueue < front.sharedMaterial.renderQueue
                && front.sharedMaterial.renderQueue < tube.sharedMaterial.renderQueue
                && rear.sortingOrder < front.sortingOrder
                && front.sortingOrder < tube.sortingOrder;
        }

        private static string[] QuantizedPointRecords(
            string objectName,
            Transform transform,
            Mesh mesh,
            int unitsPerMillimeter,
            string format)
        {
            var points = new SortedSet<QuantizedPoint>();
            foreach (Vector3 vertex in mesh.vertices)
            {
                Vector3 world = transform.TransformPoint(vertex) * 1000f;
                world.z = -world.z;
                points.Add(QuantizedPoint.From(world, unitsPerMillimeter));
            }
            return points.Select(point => string.Format(
                CultureInfo.InvariantCulture,
                "{0}:{1},{2},{3}",
                objectName,
                Quantized(point.X, unitsPerMillimeter, format),
                Quantized(point.Y, unitsPerMillimeter, format),
                Quantized(point.Z, unitsPerMillimeter, format))).ToArray();
        }

        private static string Quantized(
            float value,
            int unitsPerMillimeter,
            string format)
        {
            if (Mathf.Abs(value) < 0.5f)
            {
                value = 0f;
            }
            return (value / unitsPerMillimeter).ToString(
                format,
                CultureInfo.InvariantCulture);
        }

        private static Bounds TransformBounds(Transform transform, Bounds local)
        {
            Vector3 center = transform.TransformPoint(local.center);
            Vector3 extents = local.extents;
            Vector3 axisX = transform.TransformVector(
                new Vector3(extents.x, 0f, 0f));
            Vector3 axisY = transform.TransformVector(
                new Vector3(0f, extents.y, 0f));
            Vector3 axisZ = transform.TransformVector(
                new Vector3(0f, 0f, extents.z));
            extents = new Vector3(
                Mathf.Abs(axisX.x) + Mathf.Abs(axisY.x) + Mathf.Abs(axisZ.x),
                Mathf.Abs(axisX.y) + Mathf.Abs(axisY.y) + Mathf.Abs(axisZ.y),
                Mathf.Abs(axisX.z) + Mathf.Abs(axisY.z) + Mathf.Abs(axisZ.z));
            return new Bounds(center, extents * 2f);
        }

        private static void Capture(Camera camera, string outputPath)
        {
            RenderTexture target = new RenderTexture(
                CaptureWidth,
                CaptureHeight,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 1,
                name = "PremiumDisplayCaseGate11ParityRT"
            };
            target.Create();
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            camera.targetTexture = target;
            RenderTexture.active = target;
            camera.Render();
            Texture2D texture = new Texture2D(
                CaptureWidth,
                CaptureHeight,
                TextureFormat.RGBA32,
                false,
                false);
            texture.ReadPixels(
                new Rect(0, 0, CaptureWidth, CaptureHeight),
                0,
                0);
            texture.Apply(false, false);
            File.WriteAllBytes(outputPath, texture.EncodeToPNG());
            camera.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            target.Release();
            UnityEngine.Object.DestroyImmediate(texture);
            UnityEngine.Object.DestroyImmediate(target);
        }

        private static Transform FindDescendant(Transform root, string name)
        {
            if (root.name == name)
            {
                return root;
            }
            foreach (Transform child in root)
            {
                Transform match = FindDescendant(child, name);
                if (match != null)
                {
                    return match;
                }
            }
            return null;
        }

        private static string RecordsDigest(IEnumerable<string> records)
        {
            using SHA256 sha = SHA256.Create();
            foreach (string record in records)
            {
                byte[] bytes = Encoding.UTF8.GetBytes(record + "\n");
                sha.TransformBlock(bytes, 0, bytes.Length, null, 0);
            }
            sha.TransformFinalBlock(Array.Empty<byte>(), 0, 0);
            return ToHex(sha.Hash);
        }

        private static string Sha256File(string path)
        {
            using SHA256 sha = SHA256.Create();
            using FileStream stream = File.OpenRead(path);
            return ToHex(sha.ComputeHash(stream));
        }

        private static string ToHex(byte[] bytes)
        {
            var builder = new StringBuilder(bytes.Length * 2);
            foreach (byte value in bytes)
            {
                builder.Append(value.ToString("x2", CultureInfo.InvariantCulture));
            }
            return builder.ToString();
        }

        private static string AssetAbsolutePath(string assetPath)
        {
            return Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                assetPath));
        }

        private static string RepoRelative(string absolutePath)
        {
            string repoRoot = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "../../.."));
            return Path.GetRelativePath(repoRoot, absolutePath)
                .Replace('\\', '/');
        }

        private static void WriteJson<T>(string path, T value)
        {
            File.WriteAllText(
                path,
                JsonUtility.ToJson(value, true) + "\n",
                new UTF8Encoding(false));
        }

        private static bool AllTrue(object checks)
        {
            return checks.GetType()
                .GetFields()
                .Where(field => field.FieldType == typeof(bool))
                .All(field => (bool)field.GetValue(checks));
        }

        private readonly struct MaterialSet
        {
            public MaterialSet(
                Material rear,
                Material front,
                Material tube,
                Material insert,
                Material label)
            {
                Rear = rear;
                Front = front;
                Tube = tube;
                Insert = insert;
                Label = label;
            }

            public Material Rear { get; }
            public Material Front { get; }
            public Material Tube { get; }
            public Material Insert { get; }
            public Material Label { get; }
        }

        private readonly struct QuantizedPoint : IComparable<QuantizedPoint>
        {
            private QuantizedPoint(int x, int y, int z)
            {
                X = x;
                Y = y;
                Z = z;
            }

            public int X { get; }
            public int Y { get; }
            public int Z { get; }

            public static QuantizedPoint From(
                Vector3 millimeters,
                int unitsPerMillimeter)
            {
                return new QuantizedPoint(
                    Mathf.RoundToInt(millimeters.x * unitsPerMillimeter),
                    Mathf.RoundToInt(millimeters.y * unitsPerMillimeter),
                    Mathf.RoundToInt(millimeters.z * unitsPerMillimeter));
            }

            public int CompareTo(QuantizedPoint other)
            {
                int x = X.CompareTo(other.X);
                if (x != 0)
                {
                    return x;
                }
                int y = Y.CompareTo(other.Y);
                return y != 0 ? y : Z.CompareTo(other.Z);
            }
        }

        [Serializable]
        private sealed class ParentRecord
        {
            public string name;
            public string parent;
        }

        [Serializable]
        private sealed class MaterialRecord
        {
            public string objectName;
            public string materialName;
            public string materialPath;
            public string shaderName;
            public int renderQueue;
            public int sortingOrder;
        }

        [Serializable]
        private sealed class VectorRecord
        {
            public float x;
            public float y;
            public float z;

            public static VectorRecord From(Vector3 value)
            {
                return new VectorRecord
                {
                    x = Round(value.x),
                    y = Round(value.y),
                    z = Round(value.z)
                };
            }

            private static float Round(float value)
            {
                return (float)Math.Round(value, 9, MidpointRounding.AwayFromZero);
            }
        }

        [Serializable]
        private sealed class BoundsRecord
        {
            public VectorRecord minimum;
            public VectorRecord maximum;
            public VectorRecord size;
        }

        [Serializable]
        private sealed class MeshDigestRecord
        {
            public string objectName;
            public int uniquePositionCount;
            public int vertexCount;
            public int triangleCount;
            public int subMeshCount;
            public string vertexDigest;
            public string expectedVertexDigest;
            public bool exactPointZeroOneMillimeterDigestMatches;
            public string pointOneMillimeterVertexDigest;
            public string expectedPointOneMillimeterVertexDigest;
            public string oneMillimeterVertexDigest;
            public string expectedOneMillimeterVertexDigest;
            public bool digestMatches;
            public VectorRecord boundsSizeMeters;
        }

        [Serializable]
        private sealed class HierarchyChecks
        {
            public bool objectCountExact;
            public bool meshCountExact;
            public bool hierarchyExact;
            public bool presentationRootAtOrigin;
            public bool presentationRootUnitScale;
            public bool contentSlotEmpty;
            public bool noToyPrizeProxyExplode;
            public bool noTextComponents;
            public bool noAnimation;
            public bool materialAssignmentsExact;
            public bool transparentSortingPass;
            public bool pointLightCountZero;
            public bool externalHaloCountZero;
            public bool shippingPrefabUnchanged;
            public bool shippingSceneUnchanged;
            public bool shippingModelUnchanged;
        }

        [Serializable]
        private sealed class HierarchyReport
        {
            public int schemaVersion;
            public string modelId;
            public string gate;
            public int parityRevision;
            public string status;
            public string candidatePrefabPath;
            public string candidateScenePath;
            public string root;
            public ParentRecord[] parents;
            public MaterialRecord[] materials;
            public int objectCount;
            public int meshCount;
            public int contentSlotChildCount;
            public int pointLightCount;
            public int externalHaloCount;
            public int textComponentCount;
            public int animationComponentCount;
            public string candidateFbxSha256;
            public string shippingPrefabSha256;
            public string shippingSceneSha256;
            public string shippingModelSha256;
            public HierarchyChecks checks;
        }

        [Serializable]
        private sealed class BoundsChecks
        {
            public bool widthExact;
            public bool heightExact;
            public bool depthExact;
            public bool pivotAtOrigin;
            public bool labelCenterExact;
            public bool triangleCountExact;
            public bool perObjectDigestPrecheck;
            public bool noDegenerateTriangles;
            public bool normalWindingAgreement;
            public bool connectedTubeSingleMesh;
            public bool candidateFbxHashExact;
        }

        [Serializable]
        private sealed class BoundsReport
        {
            public int schemaVersion;
            public string modelId;
            public string gate;
            public int parityRevision;
            public string status;
            public BoundsRecord boundsMeters;
            public VectorRecord pivotMeters;
            public float pivotErrorMeters;
            public VectorRecord labelCenterMeters;
            public int triangleCount;
            public int degenerateTriangleCount;
            public float normalWindingAgreement;
            public string unityGeometryDigest;
            public string unityVertexSnapshotPath;
            public MeshDigestRecord[] meshes;
            public BoundsChecks checks;
        }

        [Serializable]
        private sealed class CameraRecord
        {
            public VectorRecord blenderPositionMm;
            public VectorRecord unityPositionMeters;
            public VectorRecord blenderLookAtMm;
            public VectorRecord unityLookAtMeters;
            public float focalLengthMm;
            public float sensorWidthMm;
            public float sensorHeightMm;
            public string gateFit;
            public string mirroredAxis;
            public VectorRecord unityUp;
        }

        [Serializable]
        private sealed class CaptureChecks
        {
            public bool unityNeutralExists;
            public bool orbitFramesComplete;
            public bool cameraPositionMatched;
            public bool cameraLookTargetMatched;
            public bool focalLengthMatched;
            public bool sensorMatched;
            public bool staticCamera;
            public bool inspectionOnlyNotShippingAnimation;
        }

        [Serializable]
        private sealed class CaptureReport
        {
            public int schemaVersion;
            public string modelId;
            public string gate;
            public int parityRevision;
            public string status;
            public string unityVersion;
            public string renderPipeline;
            public int width;
            public int height;
            public string neutralPath;
            public string neutralSha256;
            public string orbitFramesDirectory;
            public int orbitFrameCount;
            public float inspectionOrbitDegrees;
            public int inspectionFramesPerSecond;
            public CameraRecord camera;
            public CaptureChecks checks;
        }
    }
}
