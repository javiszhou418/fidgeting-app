using System;
using System.IO;
using System.Linq;
using System.Text;
using FidgetingApp.EDC;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.EditorTools
{
    public static class EdcSceneBuilder
    {
        public const string ScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        public const string PrefabPath = "Assets/_EDC/Prefabs/EDC_Root.prefab";
        public const string MagneticProfilePath =
            "Assets/_EDC/Generated/LinearMagneticDetentProfile.asset";
        public const string MagneticSlideEffectPath =
            "Assets/_EDC/Audio/MagneticSlide_AlloyClick_766Hz.wav";

        private const string ManifestPath =
            "Assets/_EDC/Generated/Meshes/layer-manifest.json";
        private const string DarkMaterialPath =
            "Assets/_EDC/Generated/Materials/M_EDC_DarkPolymer.mat";
        private const string MagnetMaterialPath =
            "Assets/_EDC/Generated/Materials/M_EDC_Magnet.mat";
        private const string ScrewMaterialPath =
            "Assets/_EDC/Generated/Materials/M_EDC_Screw.mat";
        private const string RailMeshPath =
            "Assets/_EDC/Generated/Meshes/M_EDC_SlideRail.asset";
        private const string MagnetMeshPath =
            "Assets/_EDC/Generated/Meshes/M_EDC_Magnet.asset";
        private const string ScrewMeshPath =
            "Assets/_EDC/Generated/Meshes/M_EDC_Screw.asset";

        private const float RailLength = 0.066f;
        private const float RailHeight = 0.0011f;
        private const float RailWidth = 0.0026f;
        private const float MagnetRadius = 0.00365f;
        private const float MagnetHeight = 0.0012f;
        private const float ScrewRadius = 0.00145f;
        private const float ScrewHeight = 0.0007f;
        private const int CaptureWidth = 1200;
        private const int CaptureHeight = 800;
        private const int PortraitCaptureWidth = 1290;
        private const int PortraitCaptureHeight = 2796;

        [MenuItem("Tools/Codex/EDC/4 Build Layered Slider Scene")]
        public static void BuildLayeredSliderScene()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            LayerManifest manifest = LoadManifest();
            ConfigureLayerImporters(manifest);
            LinearMagneticDetentProfile magneticProfile =
                CreateOrUpdateMagneticProfile();

            Material textured = AssetDatabase.LoadAssetAtPath<Material>(
                EdcImportPipeline.MaterialPath);
            if (textured == null)
            {
                throw new FileNotFoundException(
                    "The prepared URP Meshy material is missing.",
                    EdcImportPipeline.MaterialPath);
            }

            Material dark = CreateOrUpdateMaterial(
                DarkMaterialPath,
                new Color(0.018f, 0.022f, 0.027f, 1f),
                0.28f,
                0.38f);
            Material magnet = CreateOrUpdateMaterial(
                MagnetMaterialPath,
                new Color(0.12f, 0.14f, 0.16f, 1f),
                0.95f,
                0.72f);
            Material screw = CreateOrUpdateMaterial(
                ScrewMaterialPath,
                new Color(0.58f, 0.61f, 0.65f, 1f),
                1f,
                0.80f);

            Mesh railMesh = CreateOrUpdateBoxMesh(
                RailMeshPath,
                "M_EDC_SlideRail",
                new Vector3(RailLength, RailHeight, RailWidth));
            Mesh magnetMesh = CreateOrUpdateCylinderMesh(
                MagnetMeshPath,
                "M_EDC_Magnet",
                MagnetRadius,
                MagnetHeight,
                32);
            Mesh screwMesh = CreateOrUpdateCylinderMesh(
                ScrewMeshPath,
                "M_EDC_Screw",
                ScrewRadius,
                ScrewHeight,
                24);

            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            var root = new GameObject("EDC_Root");
            var sliderGroup = CreateGroup("SliderGroup", root.transform);
            var baseGroup = CreateGroup("Base", root.transform);
            var screwsGroup = CreateGroup("Screws", root.transform);

            LayerEntry l1 = RequireLayer(manifest, "L1_TopFrame");
            LayerEntry l2 = RequireLayer(manifest, "L2_UpperShell");
            LayerEntry l3 = RequireLayer(manifest, "L3_Gasket");
            LayerEntry l6 = RequireLayer(manifest, "L6_InnerFrame");
            LayerEntry l7 = RequireLayer(manifest, "L7_BottomShell");
            CreateImportedLayer(l1, sliderGroup.transform, textured);
            CreateImportedLayer(l2, sliderGroup.transform, textured);
            CreateImportedLayer(l3, baseGroup.transform, dark);

            GameObject railsGroup = CreateGroup("L4_SlideRails", baseGroup.transform);
            CreateMeshObject(
                "Rail_Left",
                railsGroup.transform,
                railMesh,
                dark,
                new Vector3(0f, -0.00065f, -0.0180f));
            CreateMeshObject(
                "Rail_Right",
                railsGroup.transform,
                railMesh,
                dark,
                new Vector3(0f, -0.00065f, 0.0180f));

            GameObject magnetsGroup = CreateGroup("L5_Magnets", baseGroup.transform);
            float magnetCenterOffset = magneticProfile.TravelMeters * 0.5f;
            for (int index = 0; index < magneticProfile.DetentCount; index++)
            {
                CreateMeshObject(
                    $"Magnet_{index + 1:D2}",
                    magnetsGroup.transform,
                    magnetMesh,
                    magnet,
                    new Vector3(
                        magneticProfile.GetDetentPositionMeters(index)
                            - magnetCenterOffset,
                        -0.00115f,
                        0f));
            }

            CreateImportedLayer(l6, baseGroup.transform, textured);
            CreateImportedLayer(l7, baseGroup.transform, textured);

            Vector3[] screwPositions =
            {
                // The screws remain logically separate from Base, but sit on its
                // locating posts so they do not float when SliderGroup opens.
                new Vector3(-0.0323f, -0.00090f, -0.0184f),
                new Vector3(0.0323f, -0.00090f, -0.0184f),
                new Vector3(-0.0323f, -0.00090f, 0.0184f),
                new Vector3(0.0323f, -0.00090f, 0.0184f)
            };
            for (int index = 0; index < screwPositions.Length; index++)
            {
                CreateMeshObject(
                    $"Screw_{index + 1:D2}",
                    screwsGroup.transform,
                    screwMesh,
                    screw,
                    screwPositions[index]);
            }

            GameObject interactionObject = CreateGroup(
                "InteractionSurface",
                sliderGroup.transform);
            BoxCollider surface = interactionObject.AddComponent<BoxCollider>();
            surface.center = Vector3.zero;
            surface.size = EdcSliderController.DefaultInteractionSurfaceSize;

            Camera camera = CreateStudio(scene);
            EdcPortraitCameraFramer cameraFramer =
                camera.gameObject.AddComponent<EdcPortraitCameraFramer>();
            cameraFramer.Configure(root.transform);
            EdcSliderController controller = root.AddComponent<EdcSliderController>();
            controller.Configure(
                sliderGroup.transform,
                null,
                surface,
                magneticProfile);
            controller.ResetToDefaultDetent();
            ConfigureMagneticSlideAudio(root, controller);

            PrefabUtility.SaveAsPrefabAssetAndConnect(
                root,
                PrefabPath,
                InteractionMode.AutomatedAction);
            controller.Configure(
                sliderGroup.transform,
                camera,
                surface,
                magneticProfile);
            SharedPresentationGestureController presentationGestures =
                camera.gameObject.AddComponent<SharedPresentationGestureController>();
            presentationGestures.Configure(cameraFramer, camera, surface);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath, true);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log(
                $"[EDCScene] built={ScenePath} prefab={PrefabPath} "
                + $"runtimeTriangles={manifest.totalRuntimeTriangles} "
                + $"detents={magneticProfile.DetentCount} "
                + $"travel={controller.TravelDistance:F6}");
        }

        [MenuItem("Tools/Codex/EDC/6 Install Magnetic Slide Audio")]
        public static void InstallMagneticSlideAudio()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            GameObject prefabRoot = PrefabUtility.LoadPrefabContents(PrefabPath);
            try
            {
                EdcSliderController controller =
                    prefabRoot.GetComponent<EdcSliderController>();
                if (controller == null)
                {
                    throw new InvalidDataException(
                        "EDC prefab has no EdcSliderController.");
                }
                ConfigureMagneticSlideAudio(prefabRoot, controller);
                PrefabUtility.SaveAsPrefabAsset(prefabRoot, PrefabPath);
            }
            finally
            {
                PrefabUtility.UnloadPrefabContents(prefabRoot);
            }

            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject sceneRoot = scene.GetRootGameObjects()
                .Single(candidate => candidate.name == "EDC_Root");
            if (sceneRoot.GetComponentInChildren<MagneticSlideDetentAudio>(true) == null)
            {
                throw new InvalidDataException(
                    "EDC scene did not inherit MagneticSlideDetentAudio from its prefab.");
            }
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log(
                $"[EDCAudio] installed={MagneticSlideEffectPath} "
                + $"prefab={PrefabPath} scene={ScenePath}");
        }

        [MenuItem("Tools/Codex/EDC/5 Capture Verification Views")]
        public static void CaptureVerificationViews()
        {
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            GameObject root = scene.GetRootGameObjects()
                .Single(candidate => candidate.name == "EDC_Root");
            Camera camera = scene.GetRootGameObjects()
                .SelectMany(candidate => candidate.GetComponentsInChildren<Camera>(true))
                .Single(candidate => candidate.name == "MainCamera");
            EdcSliderController controller = root.GetComponent<EdcSliderController>();
            if (controller == null)
            {
                throw new InvalidDataException("EDC scene has no slider controller.");
            }

            string outputFolder = Path.GetFullPath(
                Path.Combine(Application.dataPath, "../../../Artifacts/EDC"));
            Directory.CreateDirectory(outputFolder);

            bool previousOrthographic = camera.orthographic;
            float previousOrthographicSize = camera.orthographicSize;
            Vector3 previousPosition = camera.transform.position;
            Quaternion previousRotation = camera.transform.rotation;
            controller.ResetToDefaultDetent();

            camera.orthographic = true;
            camera.orthographicSize = 0.030f;
            camera.transform.position = new Vector3(0f, 0.15f, 0f);
            camera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
            CaptureCamera(camera, Path.Combine(outputFolder, "Final_Top.png"));

            camera.orthographicSize = 0.030f;
            camera.transform.position = new Vector3(0f, 0f, -0.15f);
            camera.transform.rotation = Quaternion.identity;
            CaptureCamera(camera, Path.Combine(outputFolder, "Final_Side.png"));

            controller.SetSlideProgress(1f);
            camera.orthographic = previousOrthographic;
            camera.orthographicSize = previousOrthographicSize;
            camera.transform.position = previousPosition;
            camera.transform.rotation = previousRotation;
            CaptureCamera(camera, Path.Combine(outputFolder, "Final_Open.png"));

            controller.ResetToDefaultDetent();
            camera.orthographic = previousOrthographic;
            camera.orthographicSize = previousOrthographicSize;
            camera.transform.position = previousPosition;
            camera.transform.rotation = previousRotation;

            EdcPortraitCameraFramer cameraFramer =
                camera.GetComponent<EdcPortraitCameraFramer>();
            if (cameraFramer == null)
            {
                throw new InvalidDataException("EDC scene has no portrait camera framer.");
            }
            float previousAspect = camera.aspect;
            camera.aspect = (float)PortraitCaptureWidth / PortraitCaptureHeight;
            cameraFramer.FrameNow();
            CaptureCamera(
                camera,
                Path.Combine(outputFolder, "Final_iPhone_Portrait.png"),
                PortraitCaptureWidth,
                PortraitCaptureHeight);
            camera.aspect = previousAspect;

            var hierarchy = new StringBuilder(2048);
            AppendHierarchy(hierarchy, root.transform, 0);
            const string hierarchyPath = "Assets/_EDC/Reports/final-hierarchy.txt";
            File.WriteAllText(hierarchyPath, hierarchy.ToString(), new UTF8Encoding(false));
            AssetDatabase.ImportAsset(hierarchyPath, ImportAssetOptions.ForceSynchronousImport);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log(
                $"[EDCVerification] folder={outputFolder} hierarchy={hierarchyPath}\n"
                + hierarchy);
        }

        private static void CaptureCamera(Camera camera, string outputPath)
        {
            CaptureCamera(camera, outputPath, CaptureWidth, CaptureHeight);
        }

        private static void CaptureCamera(
            Camera camera,
            string outputPath,
            int width,
            int height)
        {
            var renderTexture = new RenderTexture(
                width,
                height,
                24,
                RenderTextureFormat.ARGB32)
            {
                antiAliasing = 4
            };
            var texture = new Texture2D(
                width,
                height,
                TextureFormat.RGBA32,
                false,
                false);
            RenderTexture previous = RenderTexture.active;
            try
            {
                camera.targetTexture = renderTexture;
                camera.Render();
                RenderTexture.active = renderTexture;
                texture.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                texture.Apply(false, false);
                File.WriteAllBytes(outputPath, texture.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = null;
                RenderTexture.active = previous;
                UnityEngine.Object.DestroyImmediate(texture);
                UnityEngine.Object.DestroyImmediate(renderTexture);
            }
        }

        private static void AppendHierarchy(
            StringBuilder output,
            Transform transform,
            int depth)
        {
            output.Append(' ', depth * 2).AppendLine(transform.name);
            for (int index = 0; index < transform.childCount; index++)
            {
                AppendHierarchy(output, transform.GetChild(index), depth + 1);
            }
        }

        private static LayerManifest LoadManifest()
        {
            if (!File.Exists(ManifestPath))
            {
                throw new FileNotFoundException(
                    "Generate the simplified EDC layer manifest first.",
                    ManifestPath);
            }
            LayerManifest manifest = JsonUtility.FromJson<LayerManifest>(
                File.ReadAllText(ManifestPath));
            if (manifest == null || manifest.layers == null || manifest.layers.Length != 5)
            {
                throw new InvalidDataException("EDC layer manifest must contain five cut layers.");
            }
            return manifest;
        }

        private static void ConfigureLayerImporters(LayerManifest manifest)
        {
            foreach (LayerEntry layer in manifest.layers)
            {
                AssetDatabase.ImportAsset(
                    layer.assetPath,
                    ImportAssetOptions.ForceSynchronousImport);
                ModelImporter importer = AssetImporter.GetAtPath(layer.assetPath) as ModelImporter;
                if (importer == null)
                {
                    throw new FileNotFoundException(
                        "Generated EDC OBJ importer is missing.",
                        layer.assetPath);
                }
                importer.globalScale = 1f;
                importer.useFileScale = false;
                importer.importAnimation = false;
                importer.importBlendShapes = false;
                importer.importCameras = false;
                importer.importLights = false;
                importer.materialImportMode = ModelImporterMaterialImportMode.None;
                importer.meshCompression = ModelImporterMeshCompression.Off;
                importer.optimizeMeshPolygons = true;
                importer.optimizeMeshVertices = true;
                importer.weldVertices = false;
                importer.isReadable = false;
                importer.importNormals = ModelImporterNormals.Import;
                importer.importTangents = ModelImporterTangents.CalculateMikk;
                importer.SaveAndReimport();
            }
        }

        private static GameObject CreateImportedLayer(
            LayerEntry entry,
            Transform parent,
            Material material)
        {
            Mesh mesh = AssetDatabase.LoadAllAssetsAtPath(entry.assetPath)
                .OfType<Mesh>()
                .OrderByDescending(candidate => candidate.vertexCount)
                .FirstOrDefault();
            if (mesh == null)
            {
                throw new InvalidDataException($"No mesh found in {entry.assetPath}.");
            }
            return CreateMeshObject(
                entry.name,
                parent,
                mesh,
                material,
                ToVector3(entry.pivotPosition));
        }

        private static LayerEntry RequireLayer(LayerManifest manifest, string name)
        {
            LayerEntry entry = manifest.layers.SingleOrDefault(layer => layer.name == name);
            if (entry == null)
            {
                throw new InvalidDataException($"Layer manifest is missing {name}.");
            }
            return entry;
        }

        private static GameObject CreateGroup(string name, Transform parent)
        {
            var group = new GameObject(name);
            group.transform.SetParent(parent, false);
            return group;
        }

        private static void ConfigureMagneticSlideAudio(
            GameObject root,
            EdcSliderController controller)
        {
            Transform existing = root.transform.Find("MagneticSlideAudio");
            if (existing != null)
            {
                UnityEngine.Object.DestroyImmediate(existing.gameObject);
            }

            AudioClip effect = AssetDatabase.LoadAssetAtPath<AudioClip>(
                MagneticSlideEffectPath);
            if (effect == null)
            {
                throw new FileNotFoundException(
                    "The selected magnetic slide audio effect is missing.",
                    MagneticSlideEffectPath);
            }

            GameObject audioObject = CreateGroup(
                "MagneticSlideAudio",
                root.transform);
            var voices = new AudioSource[MagneticSlideAudioModel.VoiceCount];
            for (int index = 0; index < voices.Length; index++)
            {
                voices[index] = audioObject.AddComponent<AudioSource>();
            }

            MagneticSlideDetentAudio renderer =
                audioObject.AddComponent<MagneticSlideDetentAudio>();
            renderer.Configure(
                controller,
                effect,
                voices,
                MagneticSlideAudioModel.DefaultMasterVolume);
        }

        private static GameObject CreateMeshObject(
            string name,
            Transform parent,
            Mesh mesh,
            Material material,
            Vector3 localPosition)
        {
            var gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            gameObject.transform.localPosition = localPosition;
            MeshFilter filter = gameObject.AddComponent<MeshFilter>();
            filter.sharedMesh = mesh;
            MeshRenderer renderer = gameObject.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.On;
            renderer.receiveShadows = true;
            return gameObject;
        }

        private static Camera CreateStudio(Scene scene)
        {
            GameObject studio = CreateGroup("Studio", null);
            SceneManager.MoveGameObjectToScene(studio, scene);

            GameObject cameraObject = CreateGroup("MainCamera", studio.transform);
            cameraObject.tag = "MainCamera";
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.012f, 0.016f, 0.023f, 1f);
            camera.usePhysicalProperties = true;
            camera.sensorSize = EdcPortraitCameraFramer.DefaultSensorSizeMillimeters;
            camera.focalLength = EdcPortraitCameraFramer.DefaultFocalLengthMillimeters;
            camera.gateFit = Camera.GateFitMode.Horizontal;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 5f;
            camera.allowHDR = false;
            camera.allowMSAA = true;
            cameraObject.AddComponent<AudioListener>();
            camera.transform.position = new Vector3(0.105f, 0.075f, -0.120f);
            camera.transform.LookAt(new Vector3(0f, -0.0005f, 0f));

            CreateStudioLight(
                "Key_UpperLeft",
                studio.transform,
                Quaternion.Euler(42f, -32f, 0f),
                new Color(1f, 0.93f, 0.82f),
                1.8f);
            CreateStudioLight(
                "CoolFill",
                studio.transform,
                Quaternion.Euler(125f, 150f, 0f),
                new Color(0.52f, 0.68f, 1f),
                1.0f);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.13f, 0.16f, 0.21f, 1f);
            RenderSettings.reflectionIntensity = 0.35f;
            return camera;
        }

        private static void CreateStudioLight(
            string name,
            Transform parent,
            Quaternion rotation,
            Color color,
            float intensity)
        {
            GameObject lightObject = CreateGroup(name, parent);
            lightObject.transform.rotation = rotation;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
        }

        private static Material CreateOrUpdateMaterial(
            string path,
            Color color,
            float metallic,
            float smoothness)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                throw new InvalidDataException("URP/Lit shader is unavailable.");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader) { name = Path.GetFileNameWithoutExtension(path) };
                AssetDatabase.CreateAsset(material, path);
            }
            material.shader = shader;
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.DisableKeyword("_NORMALMAP");
            material.DisableKeyword("_METALLICSPECGLOSSMAP");
            EditorUtility.SetDirty(material);
            return material;
        }

        private static LinearMagneticDetentProfile CreateOrUpdateMagneticProfile()
        {
            LinearMagneticDetentProfile profile =
                AssetDatabase.LoadAssetAtPath<LinearMagneticDetentProfile>(
                    MagneticProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<LinearMagneticDetentProfile>();
                profile.name = "LinearMagneticDetentProfile_HeavySixStep";
                AssetDatabase.CreateAsset(profile, MagneticProfilePath);
            }
            profile.ApplyHeavyDefaults();
            EditorUtility.SetDirty(profile);
            return profile;
        }

        private static Mesh CreateOrUpdateBoxMesh(
            string path,
            string name,
            Vector3 size)
        {
            Vector3 half = size * 0.5f;
            Vector3[] vertices =
            {
                new(-half.x, -half.y, -half.z), new(-half.x, half.y, -half.z),
                new(half.x, half.y, -half.z), new(half.x, -half.y, -half.z),
                new(half.x, -half.y, half.z), new(half.x, half.y, half.z),
                new(-half.x, half.y, half.z), new(-half.x, -half.y, half.z),
                new(-half.x, -half.y, half.z), new(-half.x, half.y, half.z),
                new(-half.x, half.y, -half.z), new(-half.x, -half.y, -half.z),
                new(half.x, -half.y, -half.z), new(half.x, half.y, -half.z),
                new(half.x, half.y, half.z), new(half.x, -half.y, half.z),
                new(-half.x, half.y, -half.z), new(-half.x, half.y, half.z),
                new(half.x, half.y, half.z), new(half.x, half.y, -half.z),
                new(-half.x, -half.y, half.z), new(-half.x, -half.y, -half.z),
                new(half.x, -half.y, -half.z), new(half.x, -half.y, half.z)
            };
            int[] triangles =
            {
                0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7,
                8, 9, 10, 8, 10, 11, 12, 13, 14, 12, 14, 15,
                16, 17, 18, 16, 18, 19, 20, 21, 22, 20, 22, 23
            };
            Mesh mesh = LoadOrCreateMesh(path, name);
            mesh.Clear();
            mesh.vertices = vertices;
            mesh.triangles = triangles;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            EditorUtility.SetDirty(mesh);
            return mesh;
        }

        private static Mesh CreateOrUpdateCylinderMesh(
            string path,
            string name,
            float radius,
            float height,
            int segments)
        {
            var vertices = new Vector3[segments * 4 + 2];
            var uvs = new Vector2[vertices.Length];
            var triangles = new int[segments * 12];
            float halfHeight = height * 0.5f;
            for (int index = 0; index < segments; index++)
            {
                float angle = Mathf.PI * 2f * index / segments;
                float x = Mathf.Cos(angle) * radius;
                float z = Mathf.Sin(angle) * radius;
                int side = index * 2;
                vertices[side] = new Vector3(x, -halfHeight, z);
                vertices[side + 1] = new Vector3(x, halfHeight, z);
                uvs[side] = new Vector2((float)index / segments, 0f);
                uvs[side + 1] = new Vector2((float)index / segments, 1f);

                int cap = segments * 2 + index * 2;
                vertices[cap] = new Vector3(x, -halfHeight, z);
                vertices[cap + 1] = new Vector3(x, halfHeight, z);
                uvs[cap] = uvs[cap + 1] = new Vector2(
                    x / (radius * 2f) + 0.5f,
                    z / (radius * 2f) + 0.5f);
            }
            int bottomCenter = vertices.Length - 2;
            int topCenter = vertices.Length - 1;
            vertices[bottomCenter] = new Vector3(0f, -halfHeight, 0f);
            vertices[topCenter] = new Vector3(0f, halfHeight, 0f);
            uvs[bottomCenter] = uvs[topCenter] = new Vector2(0.5f, 0.5f);

            int triangle = 0;
            for (int index = 0; index < segments; index++)
            {
                int next = (index + 1) % segments;
                int side = index * 2;
                int nextSide = next * 2;
                triangles[triangle++] = side;
                triangles[triangle++] = side + 1;
                triangles[triangle++] = nextSide + 1;
                triangles[triangle++] = side;
                triangles[triangle++] = nextSide + 1;
                triangles[triangle++] = nextSide;

                int cap = segments * 2 + index * 2;
                int nextCap = segments * 2 + next * 2;
                triangles[triangle++] = bottomCenter;
                triangles[triangle++] = nextCap;
                triangles[triangle++] = cap;
                triangles[triangle++] = topCenter;
                triangles[triangle++] = cap + 1;
                triangles[triangle++] = nextCap + 1;
            }

            Mesh mesh = LoadOrCreateMesh(path, name);
            mesh.Clear();
            mesh.vertices = vertices;
            mesh.uv = uvs;
            mesh.triangles = triangles;
            mesh.RecalculateNormals();
            mesh.RecalculateTangents();
            mesh.RecalculateBounds();
            EditorUtility.SetDirty(mesh);
            return mesh;
        }

        private static Mesh LoadOrCreateMesh(string path, string name)
        {
            Mesh mesh = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (mesh == null)
            {
                mesh = new Mesh { name = name };
                AssetDatabase.CreateAsset(mesh, path);
            }
            mesh.name = name;
            return mesh;
        }

        private static Vector3 ToVector3(float[] values)
        {
            if (values == null || values.Length != 3)
            {
                throw new InvalidDataException("Layer pivot must contain three values.");
            }
            return new Vector3(values[0], values[1], values[2]);
        }

        [Serializable]
        private sealed class LayerManifest
        {
            public float targetLongestDimensionMeters;
            public int totalRuntimeTriangles;
            public LayerEntry[] layers;
        }

        [Serializable]
        private sealed class LayerEntry
        {
            public string name;
            public string assetPath;
            public float[] pivotPosition;
            public float[] sourceBoundsSize;
            public int sourceVertices;
            public int sourceTriangles;
            public int runtimeVertices;
            public int runtimeTriangles;
        }
    }
}
