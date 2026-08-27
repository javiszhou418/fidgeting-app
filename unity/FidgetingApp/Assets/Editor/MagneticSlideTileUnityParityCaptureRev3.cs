using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EditorTools
{
    public static class MagneticSlideTileUnityParityCaptureRev3
    {
        private const string Root =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev003";
        private const string Materials = Root + "/Materials";
        private const string ScenePath =
            Root + "/MagneticSlideTileNeutralParityRev3.unity";
        private const string Rev2ScenePath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev002/MagneticSlideTileNeutralParityRev2.unity";
        private const string ShaderPath =
            "Assets/_EDC/CandidateRev2/Shaders/MagneticCrystalShippingR2.shader";
        private const string SilverShaderPath =
            "Assets/_EDC/CandidateRev2/Shaders/MagneticSilverShippingR2.shader";
        private const string UpperMaskPath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/artwork-upper-channel-pack.png";
        private const string LowerMaskPath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/artwork-lower-channel-pack.png";
        private const string ShippingScenePath =
            "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const int Width = 1600;
        private const int Height = 900;
        private const int EnvironmentResolution = 256;

        public static void CaptureBatch()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidenceRoot = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-003");
            Directory.CreateDirectory(evidenceRoot);
            string shippingHashBefore = Sha256(
                Path.Combine(projectRoot, ShippingScenePath));

            EnsureFolder(Root);
            EnsureFolder(Materials);
            AssetDatabase.ImportAsset(
                ShaderPath,
                ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);
            AssetDatabase.ImportAsset(
                SilverShaderPath,
                ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);
            ConfigureMaskImporter(UpperMaskPath);
            ConfigureMaskImporter(LowerMaskPath);

            Scene scene = EditorSceneManager.OpenScene(
                Rev2ScenePath,
                OpenSceneMode.Single);
            GameObject product = scene.GetRootGameObjects()
                .Single(root => root.name == "Gate11Rev2_MagneticSlideTile");
            product.name = "Gate11Rev3_MagneticSlideTile";
            product.SetActive(true);
            RemoveRev2ArtworkOverlays(product);

            Material silver = SaveMaterial(
                "M_Gate11R3_PolishedSilver",
                CreateSilverMaterial());
            Material upper = SaveMaterial(
                "M_Gate11R3_BloodRedCrystalUpper",
                CreateCrystalMaterial(
                    "M_Gate11R3_BloodRedCrystalUpper",
                    UpperMaskPath));
            Material lower = SaveMaterial(
                "M_Gate11R3_BloodRedCrystalLower",
                CreateCrystalMaterial(
                    "M_Gate11R3_BloodRedCrystalLower",
                    LowerMaskPath));
            Material clay = SaveMaterial(
                "M_Gate11R3_Clay",
                CreateClayMaterial());

            MeshRenderer[] bodyRenderers = ImportedRenderers(product);
            AssignShippingMaterials(bodyRenderers, silver, upper, lower);
            Cubemap environment = CreateParityEnvironment();
            ReflectionProbe probe = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<ReflectionProbe>(true))
                .Single();
            probe.customBakedTexture = environment;
            probe.boxProjection = false;
            probe.intensity = 1f;
            ConfigureSceneForMaterialParity(scene);
            Camera camera = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single();
            camera.name = "CAM_Gate11Rev3Neutral";
            camera.gameObject.SetActive(true);
            camera.enabled = true;
            camera.cullingMask = ~0;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.014f, 0.017f, 0.022f, 1f);

            EditorSceneManager.SaveScene(scene, ScenePath, true);
            Render(camera, Path.Combine(evidenceRoot, "unity-material-final.png"));

            Material[][] originalMaterials = bodyRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            foreach (MeshRenderer renderer in bodyRenderers)
            {
                renderer.sharedMaterials = Enumerable
                    .Repeat(clay, renderer.sharedMaterials.Length)
                    .ToArray();
            }
            Render(camera, Path.Combine(evidenceRoot, "unity-geometry-clay.png"));
            for (int index = 0; index < bodyRenderers.Length; index++)
            {
                bodyRenderers[index].sharedMaterials = originalMaterials[index];
            }

            Render(camera, Path.Combine(evidenceRoot, "unity-artwork-material.png"));
            AssetDatabase.SaveAssets();
            EditorSceneManager.SaveScene(scene, ScenePath, true);

            string shippingHashAfter = Sha256(
                Path.Combine(projectRoot, ShippingScenePath));
            ParityRev3Report report = BuildReport(
                product,
                bodyRenderers,
                upper,
                lower,
                camera,
                shippingHashBefore,
                shippingHashAfter);
            string reportPath = Path.Combine(
                evidenceRoot,
                "unity-parity-rev3-report.json");
            File.WriteAllText(
                reportPath,
                JsonUtility.ToJson(report, true) + "\n");
            if (!report.pass)
            {
                throw new InvalidDataException(
                    "Gate 11 rev 3 material parity failed: "
                    + string.Join(" | ", report.failures));
            }
            Debug.Log(
                $"[MagneticSlideTileUnityParityRev3] pass={report.pass} "
                + $"triangles={report.triangles} unlitOverlays={report.unlitOverlayCount}");
        }

        private static void ConfigureMaskImporter(string path)
        {
            if (AssetImporter.GetAtPath(path) is not TextureImporter importer)
            {
                throw new InvalidDataException($"Missing artwork mask importer: {path}");
            }
            importer.sRGBTexture = false;
            importer.mipmapEnabled = true;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Bilinear;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = false;
            importer.SaveAndReimport();
        }

        private static void RemoveRev2ArtworkOverlays(GameObject product)
        {
            GameObject[] overlays = product
                .GetComponentsInChildren<Transform>(true)
                .Where(transform => transform.name.Contains(
                    "Artwork",
                    StringComparison.Ordinal))
                .Select(transform => transform.gameObject)
                .ToArray();
            foreach (GameObject overlay in overlays)
            {
                UnityEngine.Object.DestroyImmediate(overlay);
            }
        }

        private static Material CreateSilverMaterial()
        {
            Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(SilverShaderPath)
                ?? throw new InvalidDataException(
                    "Shipping-capable magnetic silver shader did not compile.");
            var material = new Material(shader)
            {
                name = "M_Gate11R3_PolishedSilver"
            };
            SetColor(material, "_BaseColor", new Color(0.90f, 0.89f, 0.86f, 1f));
            SetFloat(material, "_Roughness", 0.06f);
            SetFloat(material, "_ReflectionStrength", 1.22f);
            SetFloat(material, "_DiffuseLift", 0.16f);
            SetFloat(material, "_SeamWorldY", 0f);
            SetFloat(material, "_SeamWidth", 0.00018f);
            SetFloat(material, "_SeamDarkness", 0.72f);
            return material;
        }

        private static Material CreateCrystalMaterial(string name, string maskPath)
        {
            Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath)
                ?? throw new InvalidDataException(
                    "Shipping-capable magnetic crystal shader did not compile.");
            Texture2D mask = AssetDatabase.LoadAssetAtPath<Texture2D>(maskPath)
                ?? throw new InvalidDataException($"Missing artwork mask: {maskPath}");
            var material = new Material(shader) { name = name };
            SetTexture(material, "_MaskMap", mask);
            SetColor(material, "_CrystalColor", new Color(0.54f, 0.22f, 0.23f, 1f));
            SetColor(material, "_MotifColor", new Color(0.003f, 0.002f, 0.003f, 1f));
            SetFloat(material, "_Roughness", 0.035f);
            SetFloat(material, "_ClearCoat", 1f);
            SetFloat(material, "_ReflectionStrength", 0.24f);
            SetFloat(material, "_Iridescence", 0.025f);
            SetFloat(material, "_CrystalBrightness", 1.0f);
            return material;
        }

        private static Material CreateClayMaterial()
        {
            Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(SilverShaderPath)
                ?? throw new InvalidDataException(
                    "Shipping-capable magnetic silver shader did not compile.");
            var material = new Material(shader) { name = "M_Gate11R3_Clay" };
            SetColor(material, "_BaseColor", new Color(0.88f, 0.88f, 0.88f, 1f));
            SetFloat(material, "_Roughness", 0.28f);
            SetFloat(material, "_ReflectionStrength", 0.05f);
            SetFloat(material, "_DiffuseLift", 0.82f);
            SetFloat(material, "_SeamWorldY", 0f);
            SetFloat(material, "_SeamWidth", 0.00018f);
            SetFloat(material, "_SeamDarkness", 0.58f);
            return material;
        }

        private static Cubemap CreateParityEnvironment()
        {
            var cubemap = new Cubemap(
                EnvironmentResolution,
                TextureFormat.RGBAHalf,
                true)
            {
                name = "Gate11R3_ApprovedReflection",
                filterMode = FilterMode.Trilinear,
                wrapMode = TextureWrapMode.Clamp,
                anisoLevel = 1
            };
            for (int face = 0; face < 6; face++)
            {
                var pixels = new Color[EnvironmentResolution * EnvironmentResolution];
                for (int y = 0; y < EnvironmentResolution; y++)
                {
                    float v = 2f * ((y + 0.5f) / EnvironmentResolution) - 1f;
                    for (int x = 0; x < EnvironmentResolution; x++)
                    {
                        float u = 2f * ((x + 0.5f) / EnvironmentResolution) - 1f;
                        Vector3 direction = CubemapDirection((CubemapFace)face, u, v);
                        pixels[y * EnvironmentResolution + x] =
                            ParityEnvironmentColor(direction);
                    }
                }
                cubemap.SetPixels(pixels, (CubemapFace)face, 0);
            }
            cubemap.Apply(true, false);
            string path = Materials + "/Gate11R3_ApprovedReflection.cubemap";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(cubemap, path);
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = cubemap;
            return AssetDatabase.LoadAssetAtPath<Cubemap>(path);
        }

        private static Vector3 CubemapDirection(CubemapFace face, float u, float v)
        {
            Vector3 direction = face switch
            {
                CubemapFace.PositiveX => new Vector3(1f, -v, -u),
                CubemapFace.NegativeX => new Vector3(-1f, -v, u),
                CubemapFace.PositiveY => new Vector3(u, 1f, v),
                CubemapFace.NegativeY => new Vector3(u, -1f, -v),
                CubemapFace.PositiveZ => new Vector3(u, -v, 1f),
                CubemapFace.NegativeZ => new Vector3(-u, -v, -1f),
                _ => Vector3.forward
            };
            return direction.normalized;
        }

        private static Color ParityEnvironmentColor(Vector3 direction)
        {
            Vector3 key = new Vector3(-0.74f, 0.38f, -0.56f).normalized;
            Vector3 fill = new Vector3(0.58f, 0.16f, 0.80f).normalized;
            Vector3 rim = new Vector3(0.18f, 0.92f, 0.34f).normalized;
            float keyLobe = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(direction, key)), 8f);
            float fillLobe = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(direction, fill)), 5f);
            float rimLobe = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(direction, rim)), 14f);
            float horizon = Mathf.Pow(1f - Mathf.Abs(direction.y), 2f);
            float value = Mathf.Clamp01(
                0.15f
                + 0.52f * keyLobe
                + 0.20f * fillLobe
                + 0.28f * rimLobe
                + 0.14f * horizon);
            return new Color(value * 1.01f, value, value * 0.985f, 1f);
        }

        private static Material SaveMaterial(string name, Material material)
        {
            string path = Materials + "/" + name + ".mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static void AssignShippingMaterials(
            IEnumerable<MeshRenderer> renderers,
            Material silver,
            Material upper,
            Material lower)
        {
            foreach (MeshRenderer renderer in renderers)
            {
                if (renderer.sharedMaterials.Length != 2)
                {
                    throw new InvalidDataException(
                        $"{renderer.name} must keep two approved material slots.");
                }
                Material crystal = renderer.name.Contains("Lower", StringComparison.Ordinal)
                    ? lower
                    : renderer.name.Contains("Upper", StringComparison.Ordinal)
                        ? upper
                        : throw new InvalidDataException(
                            $"Unknown render mesh: {renderer.name}");
                renderer.sharedMaterials = new[] { silver, crystal };
                renderer.enabled = true;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
            }
        }

        private static void ConfigureSceneForMaterialParity(Scene scene)
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.18f, 0.18f, 0.18f);
            RenderSettings.reflectionIntensity = 0.82f;
            RenderSettings.reflectionBounces = 1;
            foreach (Light light in scene.GetRootGameObjects()
                         .SelectMany(root => root.GetComponentsInChildren<Light>(true)))
            {
                light.enabled = true;
                if (light.name.Contains("Key", StringComparison.Ordinal))
                {
                    light.intensity = 1.0f;
                    light.color = new Color(1f, 0.99f, 0.97f);
                }
                else
                {
                    light.intensity = 0.35f;
                    light.color = Color.white;
                }
                light.shadows = LightShadows.Soft;
                light.shadowBias = 0.02f;
                light.shadowNormalBias = 0.2f;
            }
        }

        private static MeshRenderer[] ImportedRenderers(GameObject product) =>
            product.GetComponentsInChildren<MeshRenderer>(true)
                .Where(renderer => renderer.name.Contains(
                    "LowerBody",
                    StringComparison.Ordinal)
                    || renderer.name.Contains("UpperCapsule", StringComparison.Ordinal))
                .Where(renderer => renderer.GetComponent<MeshFilter>()?.sharedMesh?.subMeshCount == 2)
                .ToArray();

        private static ParityRev3Report BuildReport(
            GameObject product,
            MeshRenderer[] renderers,
            Material upper,
            Material lower,
            Camera camera,
            string shippingHashBefore,
            string shippingHashAfter)
        {
            var failures = new List<string>();
            MeshFilter[] filters = product.GetComponentsInChildren<MeshFilter>(true);
            int triangles = filters.Sum(filter => filter.sharedMesh.triangles.Length / 3);
            int vertices = filters.Sum(filter => filter.sharedMesh.vertexCount);
            Bounds bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1))
            {
                bounds.Encapsulate(renderer.bounds);
            }
            float[] sortedBounds = { bounds.size.x, bounds.size.y, bounds.size.z };
            Array.Sort(sortedBounds);
            int unlitOverlays = product.GetComponentsInChildren<Renderer>(true)
                .Count(renderer => renderer.name.Contains(
                    "ArtworkPreview",
                    StringComparison.Ordinal));
            bool independentMasks = upper.GetTexture("_MaskMap") != null
                && lower.GetTexture("_MaskMap") != null
                && AssetDatabase.GetAssetPath(upper.GetTexture("_MaskMap"))
                    != AssetDatabase.GetAssetPath(lower.GetTexture("_MaskMap"));

            Check(filters.Length == 2, "Render mesh count changed.", failures);
            Check(triangles == 4096, "Triangle count changed.", failures);
            Check(Mathf.Abs(sortedBounds[0] - 0.012f) < 0.00001f, "Thickness changed.", failures);
            Check(Mathf.Abs(sortedBounds[1] - 0.031f) < 0.00001f, "Width changed.", failures);
            Check(Mathf.Abs(sortedBounds[2] - 0.050f) < 0.00001f, "Length changed.", failures);
            Check(unlitOverlays == 0, "Unlit artwork shortcut remains.", failures);
            Check(independentMasks, "Upper/lower masks are not independent.", failures);
            Check(upper.shader.name == "FidgetingApp/EDC/MagneticCrystalShippingR2",
                "Upper shipping shader mismatch.", failures);
            Check(lower.shader.name == "FidgetingApp/EDC/MagneticCrystalShippingR2",
                "Lower shipping shader mismatch.", failures);
            Check(shippingHashBefore == shippingHashAfter,
                "Shipping scene changed during Gate 11.", failures);

            return new ParityRev3Report
            {
                pass = failures.Count == 0,
                failures = failures.ToArray(),
                revision = 3,
                scenePath = ScenePath,
                shaderPath = ShaderPath,
                triangles = triangles,
                vertices = vertices,
                boundsMeters = sortedBounds,
                unlitOverlayCount = unlitOverlays,
                upperLowerMasksIndependent = independentMasks,
                crystalShader = upper.shader.name,
                silverShader = renderers[0].sharedMaterials[0].shader.name,
                cameraPosition = camera.transform.position,
                cameraVerticalFov = camera.fieldOfView,
                shippingSceneHashBefore = shippingHashBefore,
                shippingSceneHashAfter = shippingHashAfter,
                shippingSceneModified = shippingHashBefore != shippingHashAfter,
                runtimeIntegrated = false,
                hapticsIntegrated = false,
                deviceAcceptance = "pending"
            };
        }

        private static void Render(Camera camera, string outputPath)
        {
            var target = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGB32);
            var image = new Texture2D(Width, Height, TextureFormat.RGBA32, false, false);
            RenderTexture previous = RenderTexture.active;
            float previousAspect = camera.aspect;
            try
            {
                target.Create();
                camera.aspect = (float)Width / Height;
                camera.targetTexture = target;
                var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0f, 0f, Width, Height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(outputPath, image.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = null;
                camera.aspect = previousAspect;
                RenderTexture.active = previous;
                UnityEngine.Object.DestroyImmediate(image);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static void EnsureFolder(string path)
        {
            string[] parts = path.Split('/');
            string current = parts[0];
            for (int index = 1; index < parts.Length; index++)
            {
                string next = current + "/" + parts[index];
                if (!AssetDatabase.IsValidFolder(next))
                {
                    AssetDatabase.CreateFolder(current, parts[index]);
                }
                current = next;
            }
        }

        private static void SetFloat(Material material, string property, float value)
        {
            if (material.HasProperty(property))
            {
                material.SetFloat(property, value);
            }
        }

        private static void SetColor(Material material, string property, Color value)
        {
            if (material.HasProperty(property))
            {
                material.SetColor(property, value);
            }
        }

        private static void SetTexture(
            Material material,
            string property,
            Texture value)
        {
            if (!material.HasProperty(property))
            {
                throw new InvalidDataException(
                    $"{material.shader.name} is missing {property}.");
            }
            material.SetTexture(property, value);
        }

        private static void Check(
            bool condition,
            string failure,
            ICollection<string> failures)
        {
            if (!condition)
            {
                failures.Add(failure);
            }
        }

        private static string Sha256(string path)
        {
            using SHA256 sha = SHA256.Create();
            using FileStream stream = File.OpenRead(path);
            return BitConverter.ToString(sha.ComputeHash(stream))
                .Replace("-", string.Empty)
                .ToLowerInvariant();
        }

        [Serializable]
        private sealed class ParityRev3Report
        {
            public bool pass;
            public string[] failures;
            public int revision;
            public string scenePath;
            public string shaderPath;
            public int triangles;
            public int vertices;
            public float[] boundsMeters;
            public int unlitOverlayCount;
            public bool upperLowerMasksIndependent;
            public string crystalShader;
            public string silverShader;
            public Vector3 cameraPosition;
            public float cameraVerticalFov;
            public string shippingSceneHashBefore;
            public string shippingSceneHashAfter;
            public bool shippingSceneModified;
            public bool runtimeIntegrated;
            public bool hapticsIntegrated;
            public string deviceAcceptance;
        }
    }
}
