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
    public static class MagneticSlideTilePortableLightingBuilder
    {
        private const string SourceRoot =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R010";
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate08R003PortableValidation";
        private const string ScenePath =
            Root + "/Scenes/MagneticSlideTilePortableLightingR003.unity";
        private const string SourceScene =
            SourceRoot + "/Scenes/MagneticSlideTileGate11R010Parity.unity";
        private const string Materials = Root + "/Materials";
        private const string Environment = Root + "/Environment";
        private const string Textures =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R009/Imported/Textures";
        private const string ShippingScene = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const int Width = 1400;
        private const int Height = 1100;

        [MenuItem("Fidgeting/Model Pipeline/Build Portable Gate 08 R003 Validation")]
        public static void BuildAndCapture()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidence = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-003");
            string sourceExr = Path.Combine(evidence, "portable-studio-r003.exr");
            string shippingBefore = Sha256(Path.Combine(projectRoot, ShippingScene));
            PrepareEnvironmentAsset(sourceExr);

            Scene scene = EditorSceneManager.OpenScene(SourceScene, OpenSceneMode.Single);
            GameObject product = scene.GetRootGameObjects().First(
                root => root.GetComponent<MagneticSlideTileGate11Metadata>() != null);
            product.name = "MagneticSlideTile_Gate08R003_PortableValidation";
            Bounds bounds = CalculateBounds(product);
            RemovePresentation(scene, product);
            AssignPortableMaterials(product);
            ConfigureRenderers(product);
            Cubemap cubemap = CreateEnvironmentCubemap();
            ConfigureEnvironment(cubemap);
            CreateGround(bounds);
            CreateDirectionalLight();
            Camera camera = CreateCamera();

            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath)!);
            EditorSceneManager.SaveScene(scene, ScenePath, true);
            AssetDatabase.SaveAssets();
            DynamicGI.UpdateEnvironment();

            Render(camera, Path.Combine(evidence, "unity-portable-beauty.png"));
            Material clay = CreateClay();
            Dictionary<Renderer, Material[]> original = SwapMaterials(product, clay);
            Render(camera, Path.Combine(evidence, "unity-portable-clay.png"));
            RestoreMaterials(original);
            UnityEngine.Object.DestroyImmediate(clay);
            CaptureOrbit(camera, bounds.center, evidence);
            EditorSceneManager.SaveScene(scene, ScenePath);

            string shippingAfter = Sha256(Path.Combine(projectRoot, ShippingScene));
            var report = new
            {
                schemaVersion = 1,
                gate = "08-lighting",
                revision = 3,
                purpose = "cross-engine-portability-validation-not-gate11-approval",
                scenePath = ScenePath,
                imageWidth = Width,
                imageHeight = Height,
                camera = new
                {
                    position = camera.transform.position,
                    rotation = camera.transform.rotation,
                    focalLengthMm = camera.focalLength,
                    sensorSizeMm = camera.sensorSize,
                    viewMatrix = MatrixValues(camera.worldToCameraMatrix),
                    projectionMatrix = MatrixValues(camera.projectionMatrix)
                },
                objectBounds = bounds,
                environment = new
                {
                    sourceExrSha256 = Sha256(sourceExr),
                    cubemapAsset = $"{Environment}/PortableStudioR003.cubemap",
                    rotationDegrees = 0f,
                    intensity = 1f,
                    contributionCount = 1,
                    reflectionProbeCount = 0,
                    syntheticHighlightCount = 0
                },
                directLight = new
                {
                    type = "Directional",
                    color = "D65",
                    intensity = 0.75f,
                    direction = new Vector3(-0.452821f, -0.710461f, -0.538701f),
                    shadows = "Soft"
                },
                colorManagement = new
                {
                    workingSpace = "Linear Rec.709 D65",
                    tonemapping = "None",
                    postExposureEv = 0f,
                    note = "No ACES stacking; Blender candidate uses Standard/Medium High Contrast at -0.35 EV."
                },
                material = new
                {
                    geometryChanged = false,
                    artworkChanged = false,
                    emission = 0f,
                    areaLightApproximation = false,
                    syntheticSoftbox = false
                },
                shippingSceneHashBefore = shippingBefore,
                shippingSceneHashAfter = shippingAfter,
                shippingSceneModified = shippingBefore != shippingAfter,
                gate09Advanced = false,
                gate11Advanced = false,
                gate12Started = false,
                buildInstallPhone = false,
                pass = shippingBefore == shippingAfter
            };
            File.WriteAllText(
                Path.Combine(evidence, "unity-portable-lighting-report.json"),
                JsonUtility.ToJson(report, true) + System.Environment.NewLine);
            AssetDatabase.Refresh();
        }

        private static void PrepareEnvironmentAsset(string sourceExr)
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate08R003PortableValidation/Environment"));
            string destination = Path.Combine(
                Directory.GetParent(Application.dataPath)!.FullName,
                Environment,
                "portable-studio-r003.exr");
            File.Copy(sourceExr, destination, true);
            AssetDatabase.ImportAsset(
                $"{Environment}/portable-studio-r003.exr",
                ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = AssetImporter.GetAtPath(
                $"{Environment}/portable-studio-r003.exr") as TextureImporter
                ?? throw new InvalidDataException("Portable EXR importer missing.");
            importer.textureType = TextureImporterType.Default;
            importer.textureShape = TextureImporterShape.Texture2D;
            importer.sRGBTexture = false;
            importer.isReadable = true;
            importer.mipmapEnabled = false;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SaveAndReimport();
        }

        private static void RemovePresentation(Scene scene, GameObject product)
        {
            foreach (GameObject root in scene.GetRootGameObjects())
            {
                if (root == product || root.name.Contains("Collision", StringComparison.Ordinal))
                    continue;
                UnityEngine.Object.DestroyImmediate(root);
            }
        }

        private static void AssignPortableMaterials(GameObject product)
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate08R003PortableValidation/Materials"));
            Shader shader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/PortableCrystalR003")
                ?? throw new InvalidDataException("Portable crystal shader missing.");
            Material upper = CreateCrystal(
                shader,
                "M_G08R003_PortableCrystalUpper",
                "upperBaseColor.png",
                "upper-maskmap-r009.png",
                "upper-normal-r009.png",
                "upperArtworkMask.png");
            Material lower = CreateCrystal(
                shader,
                "M_G08R003_PortableCrystalLower",
                "lowerBaseColor.png",
                "lower-maskmap-r009.png",
                "lower-normal-r009.png",
                "lowerArtworkMask.png");
            foreach (MeshRenderer renderer in product.GetComponentsInChildren<MeshRenderer>(true))
            {
                renderer.sharedMaterials = renderer.sharedMaterials.Select(material =>
                {
                    string name = material != null ? material.name : "";
                    if (name.Contains("CrystalUpper", StringComparison.OrdinalIgnoreCase))
                        return upper;
                    if (name.Contains("CrystalLower", StringComparison.OrdinalIgnoreCase))
                        return lower;
                    return material;
                }).ToArray();
            }
        }

        private static Material CreateCrystal(
            Shader shader,
            string name,
            string baseMap,
            string maskMap,
            string normalMap,
            string artwork)
        {
            Material material = new(shader) { name = name };
            material.SetTexture("_BaseMap", LoadTexture(baseMap));
            material.SetTexture("_MaskMap", LoadTexture(maskMap));
            material.SetTexture("_BumpMap", LoadTexture(normalMap));
            material.SetTexture("_ArtworkMask", LoadTexture(artwork));
            material.SetTexture("_PerimeterMask", LoadTexture("perimeterMask.png"));
            material.SetColor("_DeepBloodRed", new Color(0.18f, 0.003f, 0.008f, 1f));
            material.SetColor("_BlackColor", new Color(0.004f, 0.0015f, 0.0018f, 1f));
            material.SetFloat("_Smoothness", 0.94f);
            material.SetFloat("_BlackSmoothness", 0.84f);
            material.SetFloat("_NormalScale", 0.75f);
            material.SetFloat("_ReflectionStrength", 1f);
            material.SetFloat("_CoatStrength", 0.30f);
            material.SetFloat("_CrystalDepth", 0.26f);
            return SaveMaterial(material);
        }

        private static Texture2D LoadTexture(string name) =>
            AssetDatabase.LoadAssetAtPath<Texture2D>($"{Textures}/{name}")
            ?? throw new InvalidDataException($"Texture missing: {name}");

        private static Material SaveMaterial(Material material)
        {
            string path = $"{Materials}/{material.name}.mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static void ConfigureRenderers(GameObject product)
        {
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
                renderer.lightProbeUsage = LightProbeUsage.Off;
            }
        }

        private static Cubemap CreateEnvironmentCubemap()
        {
            Texture2D source = AssetDatabase.LoadAssetAtPath<Texture2D>(
                $"{Environment}/portable-studio-r003.exr")
                ?? throw new InvalidDataException("Portable EXR missing.");
            const int size = 256;
            Cubemap cubemap = new(size, TextureFormat.RGBAHalf, true)
            {
                name = "PortableStudioR003",
                filterMode = FilterMode.Trilinear,
                wrapMode = TextureWrapMode.Clamp
            };
            for (int face = 0; face < 6; face++)
            {
                Color[] pixels = new Color[size * size];
                for (int y = 0; y < size; y++)
                {
                    for (int x = 0; x < size; x++)
                    {
                        Vector3 direction = CubemapDirection((CubemapFace)face, x, y, size);
                        float u = Mathf.Atan2(direction.x, direction.z) / (2f * Mathf.PI) + 0.5f;
                        float v = Mathf.Asin(direction.y) / Mathf.PI + 0.5f;
                        pixels[y * size + x] = source.GetPixelBilinear(
                            Mathf.Repeat(u, 1f), Mathf.Clamp01(v));
                    }
                }
                cubemap.SetPixels(pixels, (CubemapFace)face, 0);
            }
            cubemap.Apply(true, false);
            string path = $"{Environment}/PortableStudioR003.cubemap";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(cubemap, path);
            return AssetDatabase.LoadAssetAtPath<Cubemap>(path);
        }

        private static Vector3 CubemapDirection(
            CubemapFace face,
            int x,
            int y,
            int size)
        {
            float a = 2f * (x + 0.5f) / size - 1f;
            float b = 2f * (y + 0.5f) / size - 1f;
            Vector3 direction = face switch
            {
                CubemapFace.PositiveX => new Vector3(1f, -b, -a),
                CubemapFace.NegativeX => new Vector3(-1f, -b, a),
                CubemapFace.PositiveY => new Vector3(a, 1f, b),
                CubemapFace.NegativeY => new Vector3(a, -1f, -b),
                CubemapFace.PositiveZ => new Vector3(a, -b, 1f),
                CubemapFace.NegativeZ => new Vector3(-a, -b, -1f),
                _ => Vector3.forward
            };
            return direction.normalized;
        }

        private static void ConfigureEnvironment(Cubemap cubemap)
        {
            Shader shader = Shader.Find("Skybox/Cubemap")
                ?? throw new InvalidDataException("Skybox/Cubemap missing.");
            Material skybox = new(shader) { name = "M_G08R003_PortableSkybox" };
            skybox.SetTexture("_Tex", cubemap);
            skybox.SetFloat("_Exposure", 0.125f);
            skybox.SetFloat("_Rotation", 0f);
            RenderSettings.skybox = SaveMaterial(skybox);
            RenderSettings.ambientMode = AmbientMode.Skybox;
            RenderSettings.ambientIntensity = 0.125f;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflection = cubemap;
            RenderSettings.reflectionIntensity = 0.125f;
            RenderSettings.reflectionBounces = 1;
        }

        private static void CreateGround(Bounds bounds)
        {
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Gate08R003PortableGround";
            ground.transform.position = new Vector3(
                bounds.center.x, bounds.min.y - 0.0006f, bounds.center.z);
            ground.transform.localScale = new Vector3(0.022f, 1f, 0.022f);
            Shader lit = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidDataException("URP Lit missing.");
            Material material = new(lit) { name = "M_G08R003_PortableGround" };
            material.SetColor("_BaseColor", new Color(0.003f, 0.003f, 0.0035f, 1f));
            material.SetFloat("_Metallic", 0f);
            material.SetFloat("_Smoothness", 0.54f);
            ground.GetComponent<Renderer>().sharedMaterial = SaveMaterial(material);
            ground.GetComponent<Renderer>().shadowCastingMode = ShadowCastingMode.Off;
            ground.GetComponent<Renderer>().receiveShadows = true;
        }

        private static void CreateDirectionalLight()
        {
            GameObject lightObject = new("Gate08R003D65Directional");
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = Color.white;
            light.intensity = 0.75f;
            light.shadows = LightShadows.Soft;
            light.shadowStrength = 1f;
            light.shadowBias = 0.015f;
            light.shadowNormalBias = 0.18f;
            lightObject.transform.rotation = Quaternion.LookRotation(
                new Vector3(-0.452821f, -0.710461f, -0.538701f),
                Vector3.up);
        }

        private static Camera CreateCamera()
        {
            GameObject cameraObject = new("CAM_Gate08R003Portable");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.Skybox;
            camera.allowHDR = true;
            camera.allowMSAA = true;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 10f;
            camera.sensorSize = new Vector2(36f, 36f / ((float)Width / Height));
            camera.focalLength = 76f;
            camera.fieldOfView = Camera.FocalLengthToFieldOfView(
                camera.focalLength, camera.sensorSize.y);
            camera.transform.position = new Vector3(0.074f, 0.072f, -0.116f);
            camera.transform.LookAt(new Vector3(0f, 0.005f, -0.002f));
            camera.tag = "MainCamera";
            UniversalAdditionalCameraData data =
                cameraObject.AddComponent<UniversalAdditionalCameraData>();
            data.renderPostProcessing = false;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            data.antialiasingQuality = AntialiasingQuality.High;
            return camera;
        }

        private static Material CreateClay()
        {
            Shader lit = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidDataException("URP Lit missing.");
            Material clay = new(lit);
            clay.SetColor("_BaseColor", new Color(0.42f, 0.42f, 0.42f, 1f));
            clay.SetFloat("_Metallic", 0f);
            clay.SetFloat("_Smoothness", 0.58f);
            return clay;
        }

        private static Dictionary<Renderer, Material[]> SwapMaterials(
            GameObject product,
            Material material)
        {
            Dictionary<Renderer, Material[]> original = new();
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                original[renderer] = renderer.sharedMaterials;
                renderer.sharedMaterials = renderer.sharedMaterials
                    .Select(_ => material).ToArray();
            }
            return original;
        }

        private static void RestoreMaterials(
            IReadOnlyDictionary<Renderer, Material[]> original)
        {
            foreach ((Renderer renderer, Material[] materials) in original)
                renderer.sharedMaterials = materials;
        }

        private static void CaptureOrbit(Camera camera, Vector3 target, string evidence)
        {
            string folder = Path.Combine(evidence, "unity-portable-orbit-frames");
            Directory.CreateDirectory(folder);
            const int frames = 72;
            const float radius = 0.145f;
            for (int frame = 0; frame < frames; frame++)
            {
                float angle = frame / (float)frames * Mathf.PI * 2f;
                camera.transform.position = target + new Vector3(
                    Mathf.Sin(angle) * radius,
                    0.068f + Mathf.Sin(angle * 2f) * 0.012f,
                    -Mathf.Cos(angle) * radius);
                camera.transform.LookAt(target);
                Render(camera, Path.Combine(folder, $"frame-{frame:000}.png"), 960, 720);
            }
            camera.transform.position = new Vector3(0.074f, 0.072f, -0.116f);
            camera.transform.LookAt(new Vector3(0f, 0.005f, -0.002f));
        }

        private static void Render(
            Camera camera,
            string path,
            int width = Width,
            int height = Height)
        {
            RenderTexture texture = new(
                width, height, 24, RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB);
            texture.Create();
            RenderTexture previous = camera.targetTexture;
            camera.targetTexture = texture;
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(
                camera,
                new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = texture
                });
            RenderTexture.active = texture;
            Texture2D image = new(width, height, TextureFormat.RGBA32, false, false);
            image.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            image.Apply(false, false);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllBytes(path, image.EncodeToPNG());
            camera.targetTexture = previous;
            RenderTexture.active = null;
            UnityEngine.Object.DestroyImmediate(image);
            texture.Release();
            UnityEngine.Object.DestroyImmediate(texture);
        }

        private static Bounds CalculateBounds(GameObject root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            Bounds bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1))
                bounds.Encapsulate(renderer.bounds);
            return bounds;
        }

        private static float[] MatrixValues(Matrix4x4 matrix)
        {
            float[] values = new float[16];
            for (int row = 0; row < 4; row++)
            {
                for (int column = 0; column < 4; column++)
                    values[row * 4 + column] = matrix[row, column];
            }
            return values;
        }

        private static string Sha256(string path)
        {
            using SHA256 hash = SHA256.Create();
            return BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes(path)))
                .Replace("-", "")
                .ToLowerInvariant();
        }
    }
}
