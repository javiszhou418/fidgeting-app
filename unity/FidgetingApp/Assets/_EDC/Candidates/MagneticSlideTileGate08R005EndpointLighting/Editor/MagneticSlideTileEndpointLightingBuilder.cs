using System;
using System.Collections.Generic;
using System.Globalization;
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
    public static class MagneticSlideTileEndpointLightingBuilder
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate08R005EndpointLighting";
        private const string ModelPath = Root + "/Models/magnetic-slide-tile-lighting-r005-unity-preview.fbx";
        private const string ScenePath =
            Root + "/Scenes/MagneticSlideTileNeutralParityR005.unity";
        private const string Environment = Root + "/Environment";
        private const string Materials = Root + "/Materials";
        private const string Textures = Root + "/Textures";
        private const string ShippingScene = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const int Width = 1400;
        private const int Height = 1100;
        private const int CubemapSize = 512;
        private const float EnvironmentStrength = 0.85f;
        private static Cubemap sharedEnvironment;
        private static float sourceEnvironmentMaximum;
        private static float cubemapEnvironmentMaximum;
        private static string sourceEnvironmentFormat;

        [MenuItem("Fidgeting/Model Pipeline/Build Gate 08 R005 Neutral Parity")]
        public static void BuildAndCapture()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidence = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-005");
            string sourceExr = Path.Combine(evidence, "neutral-parity-studio-r005.exr");
            string shippingBefore = Sha256(Path.Combine(projectRoot, ShippingScene));
            PrepareEnvironment(sourceExr);

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject sourceModel = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath)
                ?? throw new InvalidDataException("Gate 08 rev 5 FBX missing.");
            GameObject product = PrefabUtility.InstantiatePrefab(sourceModel) as GameObject
                ?? throw new InvalidDataException("Gate 08 rev 5 FBX could not be instantiated.");
            product.name = "MagneticSlideTile_Gate08R005_NeutralParity";
            NormalizeImportedModel(product);
            RemovePresentation(scene, product);
            AssignNeutralMaterials(product);
            Cubemap cubemap = CreateEnvironmentCubemap();
            sharedEnvironment = cubemap;
            Debug.Log(
                $"G08R5_ENV_STATS sourceFormat={sourceEnvironmentFormat} "
                + $"sourceMax={sourceEnvironmentMaximum:F6} "
                + $"cubemapMax={cubemapEnvironmentMaximum:F6}");
            AssignEnvironment(product, cubemap);
            ConfigureEnvironment(cubemap);
            Camera camera = CreateCamera();
            ConfigureRenderers(product);

            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath)!);
            EditorSceneManager.SaveScene(scene, ScenePath, true);
            AssetDatabase.SaveAssets();
            DynamicGI.UpdateEnvironment();

            RenderDiagnostics(product, camera, evidence);
            EditorSceneManager.SaveScene(scene, ScenePath);
            string shippingAfter = Sha256(Path.Combine(projectRoot, ShippingScene));
            string report = BuildReport(
                camera,
                sourceExr,
                shippingBefore,
                shippingAfter,
                DirectionMarkerDelta(cubemap));
            File.WriteAllText(
                Path.Combine(evidence, "neutral-parity-unity-report.json"),
                report + System.Environment.NewLine);
            AssetDatabase.Refresh();
        }

        private static void NormalizeImportedModel(GameObject product)
        {
            Renderer[] renderers = product.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
                throw new InvalidDataException("Gate 08 rev 5 FBX has no renderers.");
            Bounds bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1))
                bounds.Encapsulate(renderer.bounds);
            float maximumDimension = Mathf.Max(bounds.size.x, bounds.size.y, bounds.size.z);
            if (maximumDimension <= 0f)
                throw new InvalidDataException("Gate 08 rev 5 FBX bounds are empty.");
            product.transform.localScale *= 0.05f / maximumDimension;
            bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1))
                bounds.Encapsulate(renderer.bounds);
            product.transform.position += new Vector3(0f, 0.005f, -0.002f) - bounds.center;
            Debug.Log(
                $"G08R5_MODEL_BOUNDS size={bounds.size} center={bounds.center} "
                + $"normalizedScale={product.transform.localScale.x:F6}");
        }

        private static void PrepareEnvironment(string sourceExr)
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate08R005EndpointLighting/Environment"));
            string destination = Path.Combine(
                Directory.GetParent(Application.dataPath)!.FullName,
                Environment,
                "neutral-parity-studio-r005.exr");
            File.Copy(sourceExr, destination, true);
            string assetPath = $"{Environment}/neutral-parity-studio-r005.exr";
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = AssetImporter.GetAtPath(assetPath) as TextureImporter
                ?? throw new InvalidDataException("Neutral parity EXR importer missing.");
            importer.textureType = TextureImporterType.Default;
            importer.textureShape = TextureImporterShape.Texture2D;
            importer.sRGBTexture = false;
            importer.isReadable = true;
            importer.mipmapEnabled = false;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            TextureImporterPlatformSettings settings =
                importer.GetDefaultPlatformTextureSettings();
            settings.overridden = true;
            settings.format = TextureImporterFormat.RGBAHalf;
            settings.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SetPlatformTextureSettings(settings);
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

        private static void AssignNeutralMaterials(GameObject product)
        {
            Directory.CreateDirectory(Path.Combine(Application.dataPath,
                "_EDC/Candidates/MagneticSlideTileGate08R005EndpointLighting/Materials"));
            Shader crystal = Shader.Find(
                "FidgetingApp/MagneticSlideTile/NeutralCrystalR005")
                ?? throw new InvalidDataException("Neutral crystal shader missing.");
            Shader surface = Shader.Find(
                "FidgetingApp/MagneticSlideTile/NeutralSurfaceR005")
                ?? throw new InvalidDataException("Neutral surface shader missing.");
            Dictionary<Material, Material> replacements = new();
            foreach (MeshRenderer renderer in product.GetComponentsInChildren<MeshRenderer>(true))
            {
                renderer.sharedMaterials = renderer.sharedMaterials.Select(original =>
                {
                    if (original == null) return original;
                    if (!replacements.TryGetValue(original, out Material replacement))
                    {
                        replacement = original.name.Contains(
                            "Crystal", StringComparison.OrdinalIgnoreCase)
                            ? CreateCrystal(crystal, original)
                            : CreateSurface(surface, original);
                        replacements.Add(original, replacement);
                    }
                    return replacement;
                }).ToArray();
            }
        }

        private static Material CreateCrystal(Shader shader, Material original)
        {
            Material material = new(shader) { name = original.name.Replace("R003", "R005") };
            foreach (string property in new[]
            {
                "_BaseMap", "_MaskMap", "_BumpMap", "_ArtworkMask", "_PerimeterMask"
            })
            {
                if (original.HasProperty(property))
                    material.SetTexture(property, original.GetTexture(property));
            }
            bool lower = original.name.Contains("Lower", StringComparison.OrdinalIgnoreCase);
            material.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(
                $"{Textures}/{(lower ? "lower" : "upper")}-albedo.png"));
            material.SetTexture("_ArtworkMask", AssetDatabase.LoadAssetAtPath<Texture2D>(
                $"{Textures}/{(lower ? "artwork-lower-mask-r010" : "artwork-upper-mask")}.png"));
            material.SetTexture("_PerimeterMask", AssetDatabase.LoadAssetAtPath<Texture2D>(
                $"{Textures}/artwork-top-perimeter-border-mask.png"));
            material.SetColor("_DeepBloodRed", new Color(0.18f, 0.003f, 0.008f, 1f));
            material.SetColor("_BlackColor", new Color(0.004f, 0.0015f, 0.0018f, 1f));
            material.SetFloat("_Smoothness", 0.50f);
            material.SetFloat("_BlackSmoothness", 0.82f);
            material.SetFloat("_NormalScale", 0.75f);
            material.SetFloat("_ReflectionStrength", 0.70f);
            material.SetFloat("_DiffuseStrength", 1.50f);
            material.SetFloat("_CoatStrength", 0.48f);
            material.SetFloat("_CrystalDepth", 0.26f);
            material.SetColor(
                "_ResponseBalance", new Color(1f, 1.07f, 1.08f, 1f));
            return SaveMaterial(material);
        }

        private static Material CreateSurface(Shader shader, Material original)
        {
            string name = original.name.Replace("R010", "R005");
            Material material = new(shader) { name = name };
            bool silver = original.name.Contains("Silver", StringComparison.OrdinalIgnoreCase);
            bool dark = original.name.Contains("DarkExterior", StringComparison.OrdinalIgnoreCase);
            Color baseColor = silver
                ? new Color(0.78f, 0.77f, 0.74f, 1f)
                : dark
                    ? new Color(0.018f, 0.020f, 0.024f, 1f)
                    : ReadColor(original, "_BaseColor", new Color(0.42f, 0.42f, 0.42f, 1f));
            float metallic = silver ? 1f : dark ? 0.24f : ReadFloat(original, "_Metallic", 0f);
            float smoothness = silver
                ? 0.925f
                : dark ? 0.82f : ReadFloat(original, "_Smoothness", 0.50f);
            material.SetColor("_BaseColor", baseColor);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_ReflectionStrength", silver ? 1.37f : 0.82f);
            material.SetFloat("_DiffuseStrength", silver ? 0.08f : 2.50f);
            material.SetFloat("_CoatStrength", silver ? 0.08f : dark ? 0.55f : 0f);
            material.SetColor("_ResponseBalance", Color.white);
            return SaveMaterial(material);
        }

        private static Color ReadColor(Material material, string property, Color fallback) =>
            material.HasProperty(property) ? material.GetColor(property) : fallback;

        private static float ReadFloat(Material material, string property, float fallback) =>
            material.HasProperty(property) ? material.GetFloat(property) : fallback;

        private static Material SaveMaterial(Material material)
        {
            string path = $"{Materials}/{material.name}.mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static Cubemap CreateEnvironmentCubemap()
        {
            Texture2D source = AssetDatabase.LoadAssetAtPath<Texture2D>(
                $"{Environment}/neutral-parity-studio-r005.exr")
                ?? throw new InvalidDataException("Neutral parity EXR missing.");
            sourceEnvironmentFormat = source.graphicsFormat.ToString();
            sourceEnvironmentMaximum = source.GetPixels()
                .Max(pixel => Mathf.Max(pixel.r, pixel.g, pixel.b));
            Cubemap cubemap = new(CubemapSize, TextureFormat.RGBAHalf, true)
            {
                name = "NeutralParityStudioR005",
                filterMode = FilterMode.Trilinear,
                wrapMode = TextureWrapMode.Clamp
            };
            for (int face = 0; face < 6; face++)
            {
                Color[] pixels = new Color[CubemapSize * CubemapSize];
                for (int y = 0; y < CubemapSize; y++)
                {
                    for (int x = 0; x < CubemapSize; x++)
                    {
                        Vector3 direction = CubemapDirection(
                            (CubemapFace)face, x, y, CubemapSize);
                        float u = Mathf.Atan2(-direction.z, direction.x)
                            / (2f * Mathf.PI) + 0.5f;
                        float v = 0.5f + Mathf.Asin(direction.y) / Mathf.PI;
                        pixels[y * CubemapSize + x] = source.GetPixelBilinear(
                            Mathf.Repeat(u, 1f), Mathf.Clamp01(v))
                            * EnvironmentStrength;
                    }
                }
                cubemap.SetPixels(pixels, (CubemapFace)face, 0);
            }
            cubemap.Apply(true, false);
            cubemapEnvironmentMaximum = Enumerable.Range(0, 6)
                .SelectMany(face => cubemap.GetPixels((CubemapFace)face, 0))
                .Max(pixel => Mathf.Max(pixel.r, pixel.g, pixel.b));
            string path = $"{Environment}/NeutralParityStudioR005.cubemap";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(cubemap, path);
            return AssetDatabase.LoadAssetAtPath<Cubemap>(path);
        }

        private static Vector3 CubemapDirection(
            CubemapFace face, int x, int y, int size)
        {
            float a = 2f * (x + 0.5f) / size - 1f;
            float b = 2f * (y + 0.5f) / size - 1f;
            return face switch
            {
                CubemapFace.PositiveX => new Vector3(1f, -b, -a).normalized,
                CubemapFace.NegativeX => new Vector3(-1f, -b, a).normalized,
                CubemapFace.PositiveY => new Vector3(a, 1f, b).normalized,
                CubemapFace.NegativeY => new Vector3(a, -1f, -b).normalized,
                CubemapFace.PositiveZ => new Vector3(a, -b, 1f).normalized,
                CubemapFace.NegativeZ => new Vector3(-a, -b, -1f).normalized,
                _ => Vector3.forward
            };
        }

        private static void ConfigureEnvironment(Cubemap cubemap)
        {
            RenderSettings.skybox = null;
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = Color.black;
            RenderSettings.ambientIntensity = 0f;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Skybox;
            RenderSettings.customReflection = null;
            RenderSettings.reflectionIntensity = 0f;
            RenderSettings.reflectionBounces = 1;
        }

        private static void AssignEnvironment(GameObject product, Cubemap cubemap)
        {
            foreach (Material material in product
                .GetComponentsInChildren<Renderer>(true)
                .SelectMany(renderer => renderer.sharedMaterials)
                .Where(material => material != null)
                .Distinct())
            {
                if (material.HasProperty("_EnvironmentCube"))
                    material.SetTexture("_EnvironmentCube", cubemap);
            }
        }

        private static void ConfigureRenderers(GameObject product)
        {
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                renderer.reflectionProbeUsage = ReflectionProbeUsage.Off;
                renderer.lightProbeUsage = LightProbeUsage.Off;
            }
        }

        private static Camera CreateCamera()
        {
            GameObject cameraObject = new("CAM_Gate08R005NeutralParity");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.035f, 0.035f, 0.035f, 0f);
            camera.allowHDR = true;
            camera.allowMSAA = false;
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
            data.antialiasing = AntialiasingMode.None;
            return camera;
        }

        private static void RenderDiagnostics(
            GameObject product, Camera camera, string evidence)
        {
            Material mirror = CreateDiagnosticSurface(
                "M_G08R005_ReflectionDiagnostic",
                new Color(0.74f, 0.74f, 0.74f, 1f), 1f, 0.925f);
            SetProductActive(product, false);
            GameObject[] diagnostics = CreateSphereStrip(mirror);
            RenderLinear(camera, Path.Combine(evidence, "unity-reflection-only-linear.exr"));
            Destroy(diagnostics);

            Material silver = CreateDiagnosticSurface(
                "M_G08R005_SilverDiagnostic",
                new Color(0.78f, 0.77f, 0.74f, 1f), 1f, 0.925f);
            diagnostics = CreateSphereStrip(silver);
            RenderLinear(camera, Path.Combine(evidence, "unity-silver-linear.exr"));
            Destroy(diagnostics);

            SetProductActive(product, true);
            Dictionary<Renderer, Material[]> originals = SwapAll(
                product,
                CreateDiagnosticSurface(
                    "M_G08R005_Clay", new Color(0.42f, 0.42f, 0.42f, 1f),
                    0f, 0.50f));
            RenderLinear(camera, Path.Combine(evidence, "unity-clay-linear.exr"));
            Restore(originals);

            Renderer[] renderers = product.GetComponentsInChildren<Renderer>(true);
            Dictionary<Renderer, bool> states = renderers.ToDictionary(
                renderer => renderer, renderer => renderer.enabled);
            foreach (Renderer renderer in renderers)
            {
                renderer.enabled = renderer.sharedMaterials.Any(material =>
                    material != null
                    && material.name.Contains("CrystalUpper", StringComparison.OrdinalIgnoreCase));
            }
            RenderLinear(camera, Path.Combine(evidence, "unity-crystal-linear.exr"));
            foreach ((Renderer renderer, bool enabled) in states)
                renderer.enabled = enabled;
            RenderLinear(camera, Path.Combine(evidence, "unity-full-model-linear.exr"));
        }

        private static Material CreateDiagnosticSurface(
            string name, Color color, float metallic, float smoothness)
        {
            Shader shader = Shader.Find("FidgetingApp/MagneticSlideTile/NeutralSurfaceR005")
                ?? throw new InvalidDataException("Neutral surface shader missing.");
            Material material = new(shader) { name = name };
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Metallic", metallic);
            material.SetFloat("_Smoothness", smoothness);
            material.SetFloat("_ReflectionStrength",
                metallic > 0.5f && color.r > 0.75f ? 1.37f : 1f);
            material.SetFloat("_DiffuseStrength", metallic > 0.5f ? 0.08f : 2.50f);
            material.SetFloat("_CoatStrength", metallic > 0.5f ? 0.08f : 0f);
            material.SetColor("_ResponseBalance", Color.white);
            material.SetTexture("_EnvironmentCube", sharedEnvironment);
            return material;
        }

        private static GameObject[] CreateSphereStrip(Material material)
        {
            GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sphere.name = "M08R4_DiagnosticSphere";
            sphere.transform.position = new Vector3(-0.017f, 0.005f, 0f);
            sphere.transform.localScale = Vector3.one * 0.026f;
            sphere.GetComponent<Renderer>().sharedMaterial = material;
            GameObject strip = GameObject.CreatePrimitive(PrimitiveType.Cube);
            strip.name = "M08R4_DiagnosticStrip";
            strip.transform.position = new Vector3(0.014f, 0.005f, 0f);
            strip.transform.localScale = new Vector3(0.026f, 0.006f, 0.010f);
            strip.GetComponent<Renderer>().sharedMaterial = material;
            return new[] { sphere, strip };
        }

        private static void Destroy(IEnumerable<GameObject> objects)
        {
            foreach (GameObject item in objects)
                UnityEngine.Object.DestroyImmediate(item);
        }

        private static void SetProductActive(GameObject product, bool active) =>
            product.SetActive(active);

        private static Dictionary<Renderer, Material[]> SwapAll(
            GameObject product, Material material)
        {
            Dictionary<Renderer, Material[]> originals = new();
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                originals[renderer] = renderer.sharedMaterials;
                renderer.sharedMaterials = renderer.sharedMaterials.Select(_ => material).ToArray();
            }
            return originals;
        }

        private static void Restore(IReadOnlyDictionary<Renderer, Material[]> originals)
        {
            foreach ((Renderer renderer, Material[] materials) in originals)
                renderer.sharedMaterials = materials;
        }

        private static void RenderLinear(Camera camera, string path)
        {
            RenderTexture texture = new(
                Width, Height, 24, RenderTextureFormat.ARGBFloat,
                RenderTextureReadWrite.Linear);
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
            Texture2D image = new(Width, Height, TextureFormat.RGBAFloat, false, true);
            image.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
            image.Apply(false, false);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllBytes(path, image.EncodeToEXR(
                Texture2D.EXRFlags.OutputAsFloat | Texture2D.EXRFlags.CompressZIP));
            camera.targetTexture = previous;
            RenderTexture.active = null;
            UnityEngine.Object.DestroyImmediate(image);
            texture.Release();
            UnityEngine.Object.DestroyImmediate(texture);
        }

        private static float DirectionMarkerDelta(Cubemap cubemap)
        {
            Texture2D source = AssetDatabase.LoadAssetAtPath<Texture2D>(
                $"{Environment}/neutral-parity-studio-r005.exr");
            CubemapFace[] markers =
            {
                CubemapFace.PositiveX,
                CubemapFace.NegativeX,
                CubemapFace.PositiveZ,
                CubemapFace.NegativeZ,
                CubemapFace.PositiveY,
                CubemapFace.NegativeY
            };
            float maximum = 0f;
            foreach (CubemapFace face in markers)
            {
                Vector3 direction = CubemapDirection(
                    face, CubemapSize / 2, CubemapSize / 2, CubemapSize);
                float u = Mathf.Atan2(-direction.z, direction.x)
                    / (2f * Mathf.PI) + 0.5f;
                float v = 0.5f + Mathf.Asin(direction.y) / Mathf.PI;
                Color expected = source.GetPixelBilinear(u, v) * EnvironmentStrength;
                Color[] pixels = cubemap.GetPixels(face, 0);
                Color actual = pixels[(CubemapSize / 2) * CubemapSize + CubemapSize / 2];
                maximum = Mathf.Max(maximum,
                    Mathf.Abs(expected.r - actual.r),
                    Mathf.Abs(expected.g - actual.g),
                    Mathf.Abs(expected.b - actual.b));
            }
            return maximum;
        }

        private static string BuildReport(
            Camera camera,
            string sourceExr,
            string shippingBefore,
            string shippingAfter,
            float directionDelta)
        {
            string Float(float value) =>
                value.ToString("R", CultureInfo.InvariantCulture);
            string Array(float[] values) =>
                string.Join(",", values.Select(Float));
            Vector3 position = camera.transform.position;
            Quaternion rotation = camera.transform.rotation;
            return "{\n"
                + "  \"schemaVersion\": 1,\n"
                + "  \"gate\": \"08-lighting\",\n"
                + "  \"revision\": 4,\n"
                + "  \"status\": \"diagnostic-not-reviewable\",\n"
                + $"  \"scenePath\": \"{ScenePath}\",\n"
                + $"  \"imageSize\": [{Width},{Height}],\n"
                + "  \"camera\": {\n"
                + $"    \"position\": [{Float(position.x)},{Float(position.y)},{Float(position.z)}],\n"
                + $"    \"rotation\": [{Float(rotation.x)},{Float(rotation.y)},{Float(rotation.z)},{Float(rotation.w)}],\n"
                + $"    \"focalLengthMm\": {Float(camera.focalLength)},\n"
                + $"    \"sensorSizeMm\": [{Float(camera.sensorSize.x)},{Float(camera.sensorSize.y)}],\n"
                + $"    \"viewMatrix\": [{Array(MatrixValues(camera.worldToCameraMatrix))}],\n"
                + $"    \"projectionMatrix\": [{Array(MatrixValues(camera.projectionMatrix))}]\n"
                + "  },\n"
                + "  \"environment\": {\n"
                + $"    \"sourceExrSha256\": \"{Sha256(sourceExr)}\",\n"
                + $"    \"cubemapAsset\": \"{Environment}/NeutralParityStudioR005.cubemap\",\n"
                + $"    \"intensity\": {Float(EnvironmentStrength)},\n"
                + "    \"reflectionSourceCount\": 1,\n"
                + "    \"reflectionProbeCount\": 0,\n"
                + "    \"directLightCount\": 0,\n"
                + "    \"groundCount\": 0,\n"
                + "    \"syntheticHighlightCount\": 0,\n"
                + $"    \"directionMarkerMaxAbsoluteDelta\": {Float(directionDelta)},\n"
                + $"    \"sourceTextureFormat\": \"{sourceEnvironmentFormat}\",\n"
                + $"    \"sourceMaximum\": {Float(sourceEnvironmentMaximum)},\n"
                + $"    \"cubemapMaximum\": {Float(cubemapEnvironmentMaximum)}\n"
                + "  },\n"
                + "  \"colorManagement\": {\n"
                + "    \"renderOutput\": \"scene-linear Rec.709 D65 RGBAFloat EXR\",\n"
                + "    \"displayTransform\": \"shared post-render neutral-display-v1\",\n"
                + "    \"unityTonemapping\": \"None\"\n"
                + "  },\n"
                + "  \"material\": {\n"
                + "    \"geometryChanged\": false,\n"
                + "    \"artworkChanged\": false,\n"
                + "    \"emission\": 0,\n"
                + "    \"silverSmoothness\": 0.925,\n"
                + "    \"crystalSmoothness\": 0.5\n"
                + "  },\n"
                + $"  \"shippingSceneHashBefore\": \"{shippingBefore}\",\n"
                + $"  \"shippingSceneHashAfter\": \"{shippingAfter}\",\n"
                + $"  \"shippingSceneModified\": {(shippingBefore != shippingAfter ? "true" : "false")},\n"
                + "  \"gate09Advanced\": false,\n"
                + "  \"gate11Advanced\": false,\n"
                + "  \"gate12Started\": false,\n"
                + "  \"buildInstallPhone\": false,\n"
                + $"  \"pass\": {(shippingBefore == shippingAfter ? "true" : "false")}\n"
                + "}";
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
