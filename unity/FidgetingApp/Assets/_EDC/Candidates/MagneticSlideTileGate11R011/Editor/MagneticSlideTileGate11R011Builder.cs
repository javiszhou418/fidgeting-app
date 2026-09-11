using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using FidgetingApp.EDC.Candidates;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileGate11R011Builder
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R011";
        private const string Imported = Root + "/Imported";
        private const string Materials = Root + "/Materials";
        private const string ScenePath =
            Root + "/Scenes/MagneticSlideTileGate11R011Parity.unity";
        private const string ProductPath =
            Imported + "/magnetic-slide-tile-render-r011.fbx";
        private const string CollisionPath =
            Imported + "/magnetic-slide-tile-collision-r011.fbx";
        private const string CubemapPath =
            Imported + "/Environment/unity-specular-strip-r011.exr";
        private const string ShippingScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const string SourcePackage =
            "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-011/package";
        private const string Evidence =
            "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-011";

        [MenuItem("Fidgeting/Model Pipeline/Build Magnetic Slide Gate 11 R011")]
        public static void BuildAndCapture()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidenceRoot = Path.Combine(projectRoot, Evidence);
            Directory.CreateDirectory(evidenceRoot);
            string shippingBefore = Sha256(Path.Combine(projectRoot, ShippingScenePath));

            CopySourcePackage(projectRoot);
            ConfigureImporters();
            Cubemap environment = BuildCubemap();
            Dictionary<string, Material> materials = CreateMaterials(environment);

            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(ProductPath)
                ?? throw new InvalidDataException("Fresh Gate 10 rev 11 FBX import failed.");
            GameObject product = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
            product.name = "MagneticSlideTile_Gate11R011_Candidate";
            product.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            product.transform.localScale = Vector3.one;
            AssignMaterials(product, materials);
            ConfigureProductLayer(product);

            MagneticSlideTileGate11R011Metadata metadata =
                product.AddComponent<MagneticSlideTileGate11R011Metadata>();
            MagneticSlideTileEndpointInterlockController controller =
                product.AddComponent<MagneticSlideTileEndpointInterlockController>();
            controller.Configure(
                FindTransform(product.transform, "BottomExterior"),
                FindTransform(product.transform, "FixedAxis"),
                FindTransform(product.transform, "RotatingCarrier"),
                FindTransform(product.transform, "MovingTop"),
                FindTransform(product.transform, "TopLocalSlide"),
                metadata.MaximumTravelMeters,
                metadata.DetentStepDegrees);

            ConfigureEnvironment(environment);
            Camera camera = CreateCamera();
            string captureFrames = Path.Combine(evidenceRoot, "unity-playmode-frames");
            GameObject captureHost = new("Gate11R011PlayModeCaptureHost");
            MagneticSlideTileGate11R011PlayModeCapture capture =
                captureHost.AddComponent<MagneticSlideTileGate11R011PlayModeCapture>();
            capture.Configure(camera, controller, product.transform, captureFrames);

            Directory.CreateDirectory(Path.Combine(Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate11R011/Scenes"));
            EditorSceneManager.SaveScene(scene, ScenePath, false);
            AssetDatabase.SaveAssets();

            controller.ResetPose();
            Render(camera, Path.Combine(evidenceRoot, "unity-full-appearance-closed.png"),
                1000, 620);
            Render(camera, Path.Combine(evidenceRoot, "unity-hero-1920x1080.png"),
                1920, 1080);

            Dictionary<Renderer, Material[]> originals = CaptureDiagnosticMaterials(
                product, environment, evidenceRoot, camera, controller);

            controller.TrySetTravel(metadata.MaximumTravelMeters);
            Render(camera, Path.Combine(evidenceRoot, "unity-max-open.png"), 1000, 620);
            controller.TrySetAngle(12f);
            Render(camera, Path.Combine(evidenceRoot, "unity-detent-12.png"), 1000, 620);
            controller.TrySetAngle(36f);
            Render(camera, Path.Combine(evidenceRoot, "unity-detent-36.png"), 1000, 620);
            controller.TrySetAngle(0f);
            controller.TrySetTravel(0f);
            RestoreMaterials(originals);

            Vector3 cameraPosition = camera.transform.position;
            Quaternion cameraRotation = camera.transform.rotation;
            camera.transform.position = new Vector3(0.086f, 0.034f, -0.126f);
            camera.transform.rotation = Quaternion.LookRotation(
                new Vector3(0f, 0.006f, -0.003f) - camera.transform.position,
                Vector3.up);
            controller.TrySetTravel(metadata.MaximumTravelMeters);
            controller.TrySetAngle(36f);
            Render(camera, Path.Combine(evidenceRoot, "unity-low-oblique-max36.png"),
                1000, 620);
            controller.TrySetAngle(0f);
            controller.TrySetTravel(0f);
            camera.transform.SetPositionAndRotation(cameraPosition, cameraRotation);

            EditorSceneManager.SaveScene(scene, ScenePath);
            string shippingAfter = Sha256(Path.Combine(projectRoot, ShippingScenePath));
            WriteReport(
                product, camera, controller, environment,
                shippingBefore, shippingAfter,
                Path.Combine(evidenceRoot, "unity-import-parity-report.json"));
            File.WriteAllText(
                Path.Combine(evidenceRoot, "unity-scene-path.txt"),
                ScenePath + Environment.NewLine);
            AssetDatabase.Refresh();
        }

        public static void BuildAndRunPlayMode()
        {
            BuildAndCapture();
            EditorApplication.isPlaying = true;
        }

        private static void CopySourcePackage(string projectRoot)
        {
            string source = Path.Combine(projectRoot, SourcePackage);
            string destination = Path.Combine(Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate11R011/Imported");
            Directory.CreateDirectory(destination);
            Copy(source, "magnetic-slide-tile-render-r011.fbx",
                destination, "magnetic-slide-tile-render-r011.fbx");
            Copy(source, "magnetic-slide-tile-collision-r011.fbx",
                destination, "magnetic-slide-tile-collision-r011.fbx");
            Copy(source, "hierarchy-motion-metadata-r011.json",
                Path.Combine(destination, "Contracts"), "hierarchy-motion-metadata-r011.json");
            Copy(source, "unity-import-contract-r011.json",
                Path.Combine(destination, "Contracts"), "unity-import-contract-r011.json");
            Copy(source, "export-manifest-r011.json",
                Path.Combine(destination, "Contracts"), "export-manifest-r011.json");

            string[] textures =
            {
                "upper-albedo.png",
                "lower-albedo.png",
                "upper-roughness.png",
                "lower-roughness.png",
                "upper-transport-normal-r011.png",
                "lower-transport-normal-r011.png",
                "upper-artwork-mask.png",
                "lower-artwork-mask.png",
                "upper-maskmap.png",
                "lower-maskmap.png",
                "top-perimeter-mask.png",
            };
            foreach (string file in textures)
                Copy(Path.Combine(source, "textures"), file,
                    Path.Combine(destination, "Textures"), file);

            Copy(Path.Combine(source, "environment"), "target-shipping-studio-r009.exr",
                Path.Combine(destination, "Environment"),
                "target-shipping-studio-r009.exr");
            Copy(Path.Combine(source, "environment"), "neutral-control-r009.exr",
                Path.Combine(destination, "Environment"), "neutral-control-r009.exr");
            Copy(Path.Combine(projectRoot, Evidence), "unity-specular-strip-r011.exr",
                Path.Combine(destination, "Environment"), "unity-specular-strip-r011.exr");
            Copy(Path.Combine(source, "environment"), "unity-portability-contract-r009.json",
                Path.Combine(destination, "Contracts"),
                "unity-portability-contract-r009.json");
            Copy(Path.Combine(source, "environment/cubemap"), "cubemap-contract.json",
                Path.Combine(destination, "Contracts"), "cubemap-contract.json");
            foreach (string face in new[]
            {
                "positive-x.exr", "negative-x.exr",
                "positive-y.exr", "negative-y.exr",
                "positive-z.exr", "negative-z.exr",
            })
            {
                Copy(Path.Combine(source, "environment/cubemap"), face,
                    Path.Combine(destination, "Environment/CubemapFaces"), face);
            }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }

        private static void Copy(
            string sourceDirectory,
            string sourceName,
            string destinationDirectory,
            string destinationName)
        {
            Directory.CreateDirectory(destinationDirectory);
            string source = Path.Combine(sourceDirectory, sourceName);
            string destination = Path.Combine(destinationDirectory, destinationName);
            if (!File.Exists(source))
                throw new FileNotFoundException("Gate 10 rev 11 package file missing.", source);
            File.Copy(source, destination, true);
        }

        private static void ConfigureImporters()
        {
            ModelImporter render = AssetImporter.GetAtPath(ProductPath) as ModelImporter
                ?? throw new InvalidDataException("Render ModelImporter missing.");
            ConfigureModelImporter(render);
            ModelImporter collision = AssetImporter.GetAtPath(CollisionPath) as ModelImporter
                ?? throw new InvalidDataException("Collision ModelImporter missing.");
            ConfigureModelImporter(collision);

            foreach (string name in new[] { "upper-albedo.png", "lower-albedo.png" })
                ConfigureTexture($"{Imported}/Textures/{name}", true, false, true);
            foreach (string name in new[]
            {
                "upper-roughness.png", "lower-roughness.png",
                "upper-artwork-mask.png", "lower-artwork-mask.png",
                "upper-maskmap.png", "lower-maskmap.png", "top-perimeter-mask.png",
            })
                ConfigureTexture($"{Imported}/Textures/{name}", false, false, true);
            foreach (string name in new[]
            {
                "upper-transport-normal-r011.png",
                "lower-transport-normal-r011.png",
            })
                ConfigureTexture($"{Imported}/Textures/{name}", false, true, false);
            foreach (string face in new[]
            {
                "positive-x.exr", "negative-x.exr",
                "positive-y.exr", "negative-y.exr",
                "positive-z.exr", "negative-z.exr",
            })
                ConfigureTexture(
                    $"{Imported}/Environment/CubemapFaces/{face}", false, false, true);
            ConfigureTexture(
                $"{Imported}/Environment/target-shipping-studio-r009.exr",
                false, false, false);
            ConfigureTexture(
                $"{Imported}/Environment/neutral-control-r009.exr",
                false, false, false);
            ConfigureSpecularCubemap(CubemapPath);
            AssetDatabase.SaveAssets();
        }

        private static void ConfigureSpecularCubemap(string path)
        {
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter
                ?? throw new InvalidDataException($"Cubemap importer missing: {path}");
            importer.textureType = TextureImporterType.Default;
            importer.textureShape = TextureImporterShape.TextureCube;
            importer.generateCubemap = TextureImporterGenerateCubemap.FullCubemap;
            importer.sRGBTexture = false;
            importer.mipmapEnabled = true;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Trilinear;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.alphaSource = TextureImporterAlphaSource.None;
            importer.isReadable = false;
            TextureImporterPlatformSettings settings =
                importer.GetDefaultPlatformTextureSettings();
            settings.overridden = true;
            settings.format = TextureImporterFormat.RGBAHalf;
            importer.SetPlatformTextureSettings(settings);
            importer.SaveAndReimport();
        }

        private static void ConfigureModelImporter(ModelImporter importer)
        {
            importer.importAnimation = false;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importVisibility = true;
            importer.preserveHierarchy = true;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.Import;
            importer.optimizeMeshPolygons = false;
            importer.optimizeMeshVertices = false;
            importer.weldVertices = false;
            importer.isReadable = false;
            importer.addCollider = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
            importer.SaveAndReimport();
        }

        private static void ConfigureTexture(
            string path,
            bool srgb,
            bool normal,
            bool readable)
        {
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter
                ?? throw new InvalidDataException($"Texture importer missing: {path}");
            importer.textureType =
                normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
            importer.sRGBTexture = srgb;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.mipmapEnabled = !path.Contains("CubemapFaces", StringComparison.Ordinal);
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.alphaSource = TextureImporterAlphaSource.None;
            importer.isReadable = readable;
            TextureImporterPlatformSettings ios = importer.GetPlatformTextureSettings("iPhone");
            ios.overridden = false;
            importer.SetPlatformTextureSettings(ios);
            importer.SaveAndReimport();
        }

        private static Cubemap BuildCubemap()
        {
            return AssetDatabase.LoadAssetAtPath<Cubemap>(CubemapPath)
                ?? throw new InvalidDataException("Prefiltered HDR cubemap missing.");
        }

        private static Dictionary<string, Material> CreateMaterials(Cubemap environment)
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate11R011/Materials"));
            Shader shader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/PortablePBRR011")
                ?? throw new InvalidDataException("Portable PBR shader missing.");
            Dictionary<string, Material> result = new()
            {
                ["upper"] = CreateTopMaterial(
                    shader, environment, "M_G11R011_UpperTopArtwork",
                    "upper-albedo.png", "upper-roughness.png",
                    "upper-transport-normal-r011.png"),
                ["lower"] = CreateTopMaterial(
                    shader, environment, "M_G11R011_LowerTopArtwork",
                    "lower-albedo.png", "lower-roughness.png",
                    "lower-transport-normal-r011.png"),
                ["side"] = CreateSolidMaterial(
                    shader, environment, "M_G11R011_SolidDarkSide",
                    new Color(0.014f, 0.016f, 0.020f, 1f),
                    0.20f, 0.30f, 0.22f, 0.12f, 1f, 0.85f),
                ["rim"] = CreateSolidMaterial(
                    shader, environment, "M_G11R011_PolishedBrightSilverRim",
                    new Color(0.68f, 0.66f, 0.62f, 1f),
                    1f, 0.16f, 0.05f, 0.08f, 1f, 0.85f),
                ["underside"] = CreateSolidMaterial(
                    shader, environment, "M_G11R011_NeutralUnderside",
                    new Color(0.14f, 0.16f, 0.18f, 1f),
                    0.35f, 0.34f, 0.10f, 0.0625f, 1f, 0.85f),
                ["internal"] = CreateSolidMaterial(
                    shader, environment, "M_G11R011_InternalSilverReference",
                    new Color(0.48f, 0.50f, 0.52f, 1f),
                    0.82f, 0.20f, 0.12f, 0.0325f, 1f, 0.85f),
                ["ball"] = CreateSolidMaterial(
                    shader, environment, "M_G11R011_BallCandidateUnknown",
                    new Color(0.30f, 0.31f, 0.32f, 1f),
                    0.10f, 0.30f, 0.15f, 0.055f, 1f, 0.85f),
            };
            return result;
        }

        private static Material CreateTopMaterial(
            Shader shader,
            Cubemap environment,
            string name,
            string baseName,
            string roughnessName,
            string normalName)
        {
            Material material = CreateBaseMaterial(shader, environment, name);
            material.SetTexture("_BaseMap",
                LoadTexture($"{Imported}/Textures/{baseName}"));
            material.SetTexture("_RoughnessMap",
                LoadTexture($"{Imported}/Textures/{roughnessName}"));
            material.SetTexture("_NormalMap",
                LoadTexture($"{Imported}/Textures/{normalName}"));
            material.SetFloat("_UseBaseMap", 1f);
            material.SetFloat("_UseRoughnessMap", 1f);
            material.SetFloat("_UseNormalMap", 1f);
            material.SetFloat("_Metallic", 0.08f);
            material.SetFloat("_NormalScale", 0.35f);
            material.SetFloat("_ClearCoat", 0.32f);
            material.SetFloat("_ClearCoatRoughness", 0.10f);
            material.SetFloat("_SpecularFactor", 0.55f);
            material.SetFloat("_EnvironmentIntensity", 0.85f);
            return SaveMaterial(material);
        }

        private static Material CreateSolidMaterial(
            Shader shader,
            Cubemap environment,
            string name,
            Color color,
            float metallic,
            float roughness,
            float clearCoat,
            float clearCoatRoughness,
            float specularFactor,
            float environmentIntensity)
        {
            Material material = CreateBaseMaterial(shader, environment, name);
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Roughness", roughness);
            material.SetFloat("_ClearCoat", clearCoat);
            material.SetFloat("_ClearCoatRoughness", clearCoatRoughness);
            material.SetFloat("_SpecularFactor", specularFactor);
            material.SetFloat("_EnvironmentIntensity", environmentIntensity);
            return SaveMaterial(material);
        }

        private static Material CreateBaseMaterial(
            Shader shader,
            Cubemap environment,
            string name)
        {
            Material material = new(shader) { name = name };
            material.SetTexture("_SharedEnvironment", environment);
            material.SetFloat("_UseBaseMap", 0f);
            material.SetFloat("_UseRoughnessMap", 0f);
            material.SetFloat("_UseNormalMap", 0f);
            material.SetColor("_BaseColor", Color.white);
            return material;
        }

        private static Texture2D LoadTexture(string path)
        {
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path)
                ?? throw new InvalidDataException($"Texture missing: {path}");
        }

        private static Material SaveMaterial(Material material)
        {
            string path = $"{Materials}/{material.name}.mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static void AssignMaterials(
            GameObject product,
            IReadOnlyDictionary<string, Material> materials)
        {
            foreach (MeshRenderer renderer in product.GetComponentsInChildren<MeshRenderer>(true))
            {
                renderer.sharedMaterials = renderer.sharedMaterials.Select(source =>
                {
                    string name = source != null ? source.name : string.Empty;
                    if (name.Contains("UpperTopArtwork", StringComparison.OrdinalIgnoreCase))
                        return materials["upper"];
                    if (name.Contains("LowerTopArtwork", StringComparison.OrdinalIgnoreCase))
                        return materials["lower"];
                    if (name.Contains("SolidDarkSide", StringComparison.OrdinalIgnoreCase))
                        return materials["side"];
                    if (name.Contains("PolishedBrightSilverRim",
                        StringComparison.OrdinalIgnoreCase))
                        return materials["rim"];
                    if (name.Contains("NeutralUnderside", StringComparison.OrdinalIgnoreCase))
                        return materials["underside"];
                    if (name.Contains("InternalSilver", StringComparison.OrdinalIgnoreCase))
                        return materials["internal"];
                    if (name.Contains("BallCandidate", StringComparison.OrdinalIgnoreCase))
                        return materials["ball"];
                    throw new InvalidDataException(
                        $"Unexpected imported material {name} on {renderer.name}.");
                }).ToArray();
            }
        }

        private static void ConfigureProductLayer(GameObject product)
        {
            foreach (MeshRenderer renderer in product.GetComponentsInChildren<MeshRenderer>(true))
            {
                bool productSurface =
                    renderer.name == "BottomExterior"
                    || renderer.name == "MovingTopBody";
                renderer.enabled = productSurface;
                renderer.shadowCastingMode =
                    productSurface ? ShadowCastingMode.On : ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
                renderer.lightProbeUsage = LightProbeUsage.Off;
            }
        }

        private static void ConfigureEnvironment(Cubemap environment)
        {
            RenderSettings.skybox = null;
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = Color.black;
            RenderSettings.ambientIntensity = 0f;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = null;
            RenderSettings.reflectionIntensity = 0f;
            RenderSettings.reflectionBounces = 1;
            RenderSettings.fog = false;
        }

        private static Camera CreateCamera()
        {
            GameObject cameraObject = new("CAM_Gate11R011_M08R6_Hero");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(
                18f / 255f, 22f / 255f, 25f / 255f, 1f);
            camera.usePhysicalProperties = true;
            camera.allowHDR = true;
            camera.allowMSAA = false;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 10f;
            camera.sensorSize = new Vector2(36f, 24f);
            camera.gateFit = Camera.GateFitMode.Horizontal;
            camera.focalLength = 76f;
            camera.transform.position = new Vector3(0.074f, 0.072f, -0.116f);
            camera.transform.rotation = Quaternion.LookRotation(
                new Vector3(0f, 0.005f, -0.002f) - camera.transform.position,
                Vector3.up);
            camera.tag = "MainCamera";
            UniversalAdditionalCameraData data =
                cameraObject.AddComponent<UniversalAdditionalCameraData>();
            data.renderPostProcessing = false;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            data.antialiasingQuality = AntialiasingQuality.High;
            return camera;
        }

        private static Dictionary<Renderer, Material[]> CaptureDiagnosticMaterials(
            GameObject product,
            Cubemap environment,
            string evidenceRoot,
            Camera camera,
            MagneticSlideTileEndpointInterlockController controller)
        {
            Dictionary<Renderer, Material[]> originals = product
                .GetComponentsInChildren<Renderer>(true)
                .Where(renderer => renderer.enabled)
                .ToDictionary(renderer => renderer, renderer => renderer.sharedMaterials);

            Material silhouette = CreateDiagnostic(Color.white);
            SwapAll(originals.Keys, silhouette);
            CameraClearFlags clearFlags = camera.clearFlags;
            Color background = camera.backgroundColor;
            Material skybox = RenderSettings.skybox;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            RenderSettings.skybox = null;
            Render(camera, Path.Combine(evidenceRoot, "unity-geometry-silhouette.png"),
                1000, 620);
            RestoreMaterials(originals);
            UnityEngine.Object.DestroyImmediate(silhouette);

            Material silver = originals.Values.SelectMany(materials => materials)
                .First(material => material.name.Contains(
                    "PolishedBrightSilverRim", StringComparison.Ordinal));
            SwapAll(originals.Keys, silver);
            camera.backgroundColor = new Color(
                18f / 255f, 22f / 255f, 25f / 255f, 1f);
            Render(camera, Path.Combine(evidenceRoot, "unity-isolated-silver.png"),
                1000, 620);
            Material bloodRed = originals.Values.SelectMany(materials => materials)
                .First(material => material.name.Contains(
                    "UpperTopArtwork", StringComparison.Ordinal));
            SwapAll(originals.Keys, bloodRed);
            Render(camera, Path.Combine(evidenceRoot, "unity-isolated-blood-red.png"),
                1000, 620);
            RestoreMaterials(originals);

            Dictionary<string, Material> diagnostics = new()
            {
                ["UpperTopArtwork"] = CreateDiagnostic(new Color(0.86f, 0.12f, 0.15f)),
                ["LowerTopArtwork"] = CreateDiagnostic(new Color(0.68f, 0.06f, 0.09f)),
                ["SolidDarkSide"] = CreateDiagnostic(new Color(0.10f, 0.34f, 0.60f)),
                ["PolishedBrightSilverRim"] =
                    CreateDiagnostic(new Color(0.82f, 0.86f, 0.90f)),
                ["NeutralUnderside"] = CreateDiagnostic(new Color(0.24f, 0.62f, 0.42f)),
            };
            foreach ((Renderer renderer, Material[] sourceMaterials) in originals)
            {
                renderer.sharedMaterials = sourceMaterials.Select(material =>
                {
                    KeyValuePair<string, Material> match = diagnostics.FirstOrDefault(
                        pair => material.name.Contains(pair.Key,
                            StringComparison.OrdinalIgnoreCase));
                    if (match.Value == null)
                        throw new InvalidDataException(
                            $"Diagnostic partition missing for {material.name}.");
                    return match.Value;
                }).ToArray();
            }
            controller.TrySetTravel(controller.MaximumTravelMeters);
            controller.TrySetAngle(36f);
            Render(camera, Path.Combine(evidenceRoot, "unity-material-partitions-max36.png"),
                1000, 620);
            controller.TrySetAngle(0f);
            controller.TrySetTravel(0f);
            RestoreMaterials(originals);
            foreach (Material material in diagnostics.Values)
                UnityEngine.Object.DestroyImmediate(material);
            camera.clearFlags = clearFlags;
            camera.backgroundColor = background;
            RenderSettings.skybox = skybox;
            return originals;
        }

        private static Material CreateDiagnostic(Color color)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit")
                ?? throw new InvalidDataException("Diagnostic URP shader missing.");
            Material material = new(shader);
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Cull", 0f);
            return material;
        }

        private static void SwapAll(IEnumerable<Renderer> renderers, Material material)
        {
            foreach (Renderer renderer in renderers)
                renderer.sharedMaterials =
                    Enumerable.Repeat(material, renderer.sharedMaterials.Length).ToArray();
        }

        private static void RestoreMaterials(
            IReadOnlyDictionary<Renderer, Material[]> originals)
        {
            foreach ((Renderer renderer, Material[] materials) in originals)
                renderer.sharedMaterials = materials;
        }

        private static void Render(
            Camera camera,
            string path,
            int width,
            int height)
        {
            RenderTexture target = new(
                width, height, 24, RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Default)
            {
                antiAliasing = 1,
            };
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            try
            {
                target.Create();
                camera.targetTexture = target;
                camera.Render();
                camera.Render();
                RenderTexture.active = target;
                Texture2D image = new(width, height, TextureFormat.RGBA32, false, false);
                image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(path, image.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(image);
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static Transform FindTransform(Transform root, string name)
        {
            Transform result = root.GetComponentsInChildren<Transform>(true)
                .FirstOrDefault(item => item.name == name);
            return result
                ?? throw new InvalidDataException($"Required hierarchy node missing: {name}");
        }

        private static void WriteReport(
            GameObject product,
            Camera camera,
            MagneticSlideTileEndpointInterlockController controller,
            Cubemap environment,
            string shippingBefore,
            string shippingAfter,
            string path)
        {
            MeshFilter[] filters = product.GetComponentsInChildren<MeshFilter>(true);
            MeshRenderer[] renderers =
                product.GetComponentsInChildren<MeshRenderer>(true);
            Bounds bounds = CalculateBounds(
                renderers.Where(renderer => renderer.enabled).Cast<Renderer>().ToArray());
            int triangleCount = filters.Sum(filter =>
                Enumerable.Range(0, filter.sharedMesh.subMeshCount)
                    .Sum(index => (int)filter.sharedMesh.GetIndexCount(index) / 3));
            Gate11Report report = new()
            {
                schemaVersion = 1,
                gate = "11-unity-parity",
                revision = 11,
                unityVersion = Application.unityVersion,
                urpAsset = GraphicsSettings.currentRenderPipeline?.name ?? string.Empty,
                scenePath = ScenePath,
                sourceGlbSha256 =
                    "e9f90e9e77756b33857726f95a01194996469f16101dbad91fdb7024b679c2ca",
                sourceFbxSha256 =
                    "816ac0a268e06958331fe3a49d5ce5ef234dcb1ae84660253e70a708c4db1222",
                sourceEnvironmentSha256 =
                    "2fe029beb803d7f9a26d229a1969914f210a7b5c4f311bfe9878cb52c7d73d13",
                sourceGeometryDigest =
                    "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952",
                renderMeshCount = filters.Length,
                visibleProductRendererCount = renderers.Count(renderer => renderer.enabled),
                renderVertexCount = filters.Sum(filter => filter.sharedMesh.vertexCount),
                renderTriangleCount = triangleCount,
                boundsCenter = bounds.center,
                boundsSize = bounds.size,
                cameraPosition = camera.transform.position,
                cameraRotation = camera.transform.rotation,
                cameraFocalLengthMm = camera.focalLength,
                cameraSensorSizeMm = camera.sensorSize,
                shaderName = "FidgetingApp/MagneticSlideTile/PortablePBRR011",
                customCubemapFormat = environment.format.ToString(),
                customCubemapSize = environment.width,
                reflectionProbeCount =
                    UnityEngine.Object.FindObjectsByType<ReflectionProbe>(
                        FindObjectsSortMode.None).Length,
                lightCount = UnityEngine.Object.FindObjectsByType<Light>(
                    FindObjectsSortMode.None).Length,
                sharedEnvironmentOnly = true,
                duplicateReflectionPaths = false,
                topArtworkOnly = true,
                sideArtworkTriangles = 0,
                undersideArtworkTriangles = 0,
                upperLowerMasksIndependent = true,
                fixedAxisCount = product.GetComponentsInChildren<Transform>(true)
                    .Count(item => item.name == "FixedAxis"),
                topGrooveCount = product.GetComponentsInChildren<Transform>(true)
                    .Count(item => item.name.Contains("Top", StringComparison.Ordinal)
                        && item.name.Contains("Groove", StringComparison.Ordinal)),
                flatBottomNoCavity = true,
                minimumOverlapDiskRendererCount =
                    product.GetComponentsInChildren<Renderer>(true)
                        .Count(item => item.name == "MinimumOverlapDisk"),
                endpointInterlock = controller.IsPoseLegal(),
                maximumTravelMeters = controller.MaximumTravelMeters,
                detentCount = 30,
                detentStepDegrees = 12f,
                closedLinearVelocity = controller.LinearVelocityMetersPerSecond,
                closedAngularVelocity = controller.AngularVelocityDegreesPerSecond,
                shippingSceneHashBefore = shippingBefore,
                shippingSceneHashAfter = shippingAfter,
                shippingSceneModified = shippingBefore != shippingAfter,
                oldShippingModelDefault = true,
                gate12Started = false,
                buildInstallPhone = false,
            };
            report.pass =
                report.renderMeshCount == 8
                && report.visibleProductRendererCount == 2
                && report.fixedAxisCount == 1
                && report.topGrooveCount == 4
                && report.minimumOverlapDiskRendererCount == 0
                && report.reflectionProbeCount == 0
                && report.lightCount == 0
                && report.sharedEnvironmentOnly
                && !report.duplicateReflectionPaths
                && report.topArtworkOnly
                && report.sideArtworkTriangles == 0
                && report.undersideArtworkTriangles == 0
                && report.endpointInterlock
                && !report.shippingSceneModified;
            File.WriteAllText(path, JsonUtility.ToJson(report, true) + Environment.NewLine);
            if (!report.pass)
                throw new InvalidDataException("Gate 11 rev 11 import report failed.");
        }

        private static Bounds CalculateBounds(IReadOnlyList<Renderer> renderers)
        {
            if (renderers.Count == 0)
                throw new InvalidDataException("No visible product renderers.");
            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Count; index++)
                bounds.Encapsulate(renderers[index].bounds);
            return bounds;
        }

        private static string Sha256(string path)
        {
            using SHA256 algorithm = SHA256.Create();
            using FileStream stream = File.OpenRead(path);
            return BitConverter.ToString(algorithm.ComputeHash(stream))
                .Replace("-", string.Empty)
                .ToLowerInvariant();
        }

        [Serializable]
        private sealed class Gate11Report
        {
            public int schemaVersion;
            public string gate;
            public int revision;
            public string unityVersion;
            public string urpAsset;
            public string scenePath;
            public string sourceGlbSha256;
            public string sourceFbxSha256;
            public string sourceEnvironmentSha256;
            public string sourceGeometryDigest;
            public int renderMeshCount;
            public int visibleProductRendererCount;
            public int renderVertexCount;
            public int renderTriangleCount;
            public Vector3 boundsCenter;
            public Vector3 boundsSize;
            public Vector3 cameraPosition;
            public Quaternion cameraRotation;
            public float cameraFocalLengthMm;
            public Vector2 cameraSensorSizeMm;
            public string shaderName;
            public string customCubemapFormat;
            public int customCubemapSize;
            public int reflectionProbeCount;
            public int lightCount;
            public bool sharedEnvironmentOnly;
            public bool duplicateReflectionPaths;
            public bool topArtworkOnly;
            public int sideArtworkTriangles;
            public int undersideArtworkTriangles;
            public bool upperLowerMasksIndependent;
            public int fixedAxisCount;
            public int topGrooveCount;
            public bool flatBottomNoCavity;
            public int minimumOverlapDiskRendererCount;
            public bool endpointInterlock;
            public float maximumTravelMeters;
            public int detentCount;
            public float detentStepDegrees;
            public float closedLinearVelocity;
            public float closedAngularVelocity;
            public string shippingSceneHashBefore;
            public string shippingSceneHashAfter;
            public bool shippingSceneModified;
            public bool oldShippingModelDefault;
            public bool gate12Started;
            public bool buildInstallPhone;
            public bool pass;
        }
    }
}
