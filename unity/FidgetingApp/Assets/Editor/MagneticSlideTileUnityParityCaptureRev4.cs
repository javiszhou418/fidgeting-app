using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EditorTools
{
    public static class MagneticSlideTileUnityParityCaptureRev4
    {
        private const string Root =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev004";
        private const string Imported = Root + "/Imported";
        private const string Materials = Root + "/Materials";
        private const string ScenePath =
            Root + "/MagneticSlideTileNeutralParityRev4.unity";
        private const string Rev3ScenePath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev003/MagneticSlideTileNeutralParityRev3.unity";
        private const string CrystalShaderPath =
            "Assets/_EDC/CandidateRev2/Shaders/MagneticCrystalShippingR3.shader";
        private const string SilverShaderPath =
            "Assets/_EDC/CandidateRev2/Shaders/MagneticSilverShippingR3.shader";
        private const string UpperMaskPath =
            Imported + "/artwork-upper-channel-pack-r004.png";
        private const string LowerMaskPath =
            Imported + "/artwork-lower-channel-pack-r004.png";
        private const string ShippingScenePath =
            "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const int Width = 1600;
        private const int Height = 900;
        private const int EnvironmentResolution = 256;
        private const float PostExposure = 0f;

        public static void CaptureBatch()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidenceRoot = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-004");
            Directory.CreateDirectory(evidenceRoot);
            string shippingHashBefore = Sha256(
                Path.Combine(projectRoot, ShippingScenePath));

            EnsureFolder(Root);
            EnsureFolder(Imported);
            EnsureFolder(Materials);
            CopyMaskFromEvidence(projectRoot, evidenceRoot, "upper");
            CopyMaskFromEvidence(projectRoot, evidenceRoot, "lower");
            AssetDatabase.ImportAsset(
                CrystalShaderPath,
                ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);
            AssetDatabase.ImportAsset(
                SilverShaderPath,
                ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);
            ConfigureMaskImporter(UpperMaskPath);
            ConfigureMaskImporter(LowerMaskPath);

            Scene scene = EditorSceneManager.OpenScene(
                Rev3ScenePath,
                OpenSceneMode.Single);
            GameObject product = scene.GetRootGameObjects()
                .Single(root => root.name == "Gate11Rev3_MagneticSlideTile");
            product.name = "Gate11Rev4_MagneticSlideTile";
            product.SetActive(true);

            Material silver = SaveMaterial(
                "M_Gate11R4_PolishedSilver",
                CreateSilverMaterial());
            Material upper = SaveMaterial(
                "M_Gate11R4_BloodRedCrystalUpper",
                CreateCrystalMaterial(
                    "M_Gate11R4_BloodRedCrystalUpper",
                    UpperMaskPath));
            Material lower = SaveMaterial(
                "M_Gate11R4_BloodRedCrystalLower",
                CreateCrystalMaterial(
                    "M_Gate11R4_BloodRedCrystalLower",
                    LowerMaskPath));
            Material clay = SaveMaterial(
                "M_Gate11R4_Clay",
                CreateClayMaterial());
            Material artworkUpper = SaveMaterial(
                "M_Gate11R4_ArtworkUpper",
                CreateArtworkDiagnosticMaterial(
                    "M_Gate11R4_ArtworkUpper",
                    UpperMaskPath));
            Material artworkLower = SaveMaterial(
                "M_Gate11R4_ArtworkLower",
                CreateArtworkDiagnosticMaterial(
                    "M_Gate11R4_ArtworkLower",
                    LowerMaskPath));

            MeshRenderer[] bodyRenderers = ImportedRenderers(product);
            AssignMaterials(bodyRenderers, silver, upper, lower);
            Cubemap environment = CreateParityEnvironment(out float maxEnvironmentDelta);
            ReflectionProbe probe = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<ReflectionProbe>(true))
                .Single();
            probe.customBakedTexture = environment;
            probe.boxProjection = false;
            probe.intensity = 1f;
            ConfigureScene(scene);

            Camera camera = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
                .Single();
            camera.name = "CAM_Gate11Rev4Neutral";
            camera.gameObject.SetActive(true);
            camera.enabled = true;
            camera.cullingMask = ~0;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.014f, 0.017f, 0.022f, 1f);
            ConfigureColorManagement(scene, camera);

            EditorSceneManager.SaveScene(scene, ScenePath, true);
            Render(camera, Path.Combine(evidenceRoot, "unity-final-object.png"));

            Material[][] finalMaterials = bodyRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            foreach (MeshRenderer renderer in bodyRenderers)
            {
                renderer.sharedMaterials = Enumerable
                    .Repeat(clay, renderer.sharedMaterials.Length)
                    .ToArray();
            }
            Render(camera, Path.Combine(evidenceRoot, "unity-geometry-clay.png"));

            AssignMaterials(
                bodyRenderers,
                clay,
                artworkUpper,
                artworkLower);
            Render(camera, Path.Combine(evidenceRoot, "unity-artwork-placement.png"));

            for (int index = 0; index < bodyRenderers.Length; index++)
            {
                bodyRenderers[index].sharedMaterials = finalMaterials[index];
            }
            Render(camera, Path.Combine(evidenceRoot, "unity-material-reflection.png"));

            Quaternion cameraRotation = camera.transform.rotation;
            camera.transform.rotation =
                Quaternion.AngleAxis(7f, Vector3.up) * cameraRotation;
            Render(camera, Path.Combine(evidenceRoot, "unity-crystal-angle-diagnostic.png"));
            camera.transform.rotation = cameraRotation;

            AssetDatabase.SaveAssets();
            EditorSceneManager.SaveScene(scene, ScenePath, true);

            string shippingHashAfter = Sha256(
                Path.Combine(projectRoot, ShippingScenePath));
            ParityRev4Report report = BuildReport(
                projectRoot,
                product,
                bodyRenderers,
                upper,
                lower,
                silver,
                camera,
                shippingHashBefore,
                shippingHashAfter,
                maxEnvironmentDelta);
            string reportPath = Path.Combine(
                evidenceRoot,
                "unity-parity-rev4-report.json");
            File.WriteAllText(reportPath, JsonUtility.ToJson(report, true) + "\n");
            if (!report.pass)
            {
                throw new InvalidDataException(
                    "Gate 11 rev 4 parity failed: "
                    + string.Join(" | ", report.failures));
            }
            Debug.Log(
                $"[MagneticSlideTileUnityParityRev4] pass={report.pass} "
                + $"triangles={report.triangles} maxEnvironmentDelta={report.maxEnvironmentNeighborDelta:F4}");
        }

        private static void CopyMaskFromEvidence(
            string projectRoot,
            string evidenceRoot,
            string slot)
        {
            string source = Path.Combine(
                evidenceRoot,
                $"artwork-{slot}-channel-pack-r004.png");
            string target = Path.Combine(
                projectRoot,
                Imported,
                $"artwork-{slot}-channel-pack-r004.png");
            if (!File.Exists(source))
            {
                throw new FileNotFoundException("Prepared artwork mask is missing.", source);
            }
            File.Copy(source, target, true);
            AssetDatabase.ImportAsset(
                $"{Imported}/artwork-{slot}-channel-pack-r004.png",
                ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);
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
            importer.textureCompression = TextureImporterCompression.CompressedHQ;
            importer.SetPlatformTextureSettings(new TextureImporterPlatformSettings
            {
                name = "iPhone",
                overridden = true,
                maxTextureSize = 1024,
                format = TextureImporterFormat.ASTC_6x6,
                compressionQuality = 100
            });
            importer.SaveAndReimport();
        }

        private static Material CreateSilverMaterial()
        {
            Shader shader = LoadShader(SilverShaderPath);
            var material = new Material(shader)
            {
                name = "M_Gate11R4_PolishedSilver"
            };
            SetColor(material, "_BaseColor", new Color(0.970f, 0.965f, 0.940f, 1f));
            SetFloat(material, "_Metallic", 1f);
            SetFloat(material, "_Roughness", 0.03f);
            SetFloat(material, "_ReflectionStrength", 0.98f);
            SetFloat(material, "_ReflectionContrast", 1.10f);
            SetFloat(material, "_DiffuseLift", 0.015f);
            SetFloat(material, "_SeamWorldY", 0f);
            SetFloat(material, "_SeamWidth", 0.00018f);
            SetFloat(material, "_SeamDarkness", 0.68f);
            return material;
        }

        private static Material CreateCrystalMaterial(string name, string maskPath)
        {
            Shader shader = LoadShader(CrystalShaderPath);
            Texture2D mask = AssetDatabase.LoadAssetAtPath<Texture2D>(maskPath)
                ?? throw new InvalidDataException($"Missing artwork mask: {maskPath}");
            var material = new Material(shader) { name = name };
            SetTexture(material, "_MaskMap", mask);
            SetColor(material, "_CrystalColor", new Color(0.72f, 0.46f, 0.47f, 1f));
            SetColor(material, "_MotifColor", new Color(0.026f, 0.023f, 0.026f, 1f));
            SetColor(material, "_BorderColor", new Color(0.034f, 0.030f, 0.033f, 1f));
            SetFloat(material, "_Roughness", 0.20f);
            SetFloat(material, "_ClearCoatMask", 0.92f);
            SetFloat(material, "_ClearCoatRoughness", 0.055f);
            SetFloat(material, "_ReflectionStrength", 0.72f);
            SetFloat(material, "_Iridescence", 0.20f);
            SetFloat(material, "_DepthVariation", 0.26f);
            SetFloat(material, "_RefractionCue", 0.12f);
            SetFloat(material, "_CrystalBrightness", 1.15f);
            SetFloat(material, "_MotifReflectance", 0.36f);
            SetFloat(material, "_BorderReflectance", 0.44f);
            return material;
        }

        private static Material CreateClayMaterial()
        {
            Shader shader = LoadShader(SilverShaderPath);
            var material = new Material(shader) { name = "M_Gate11R4_Clay" };
            SetColor(material, "_BaseColor", new Color(0.78f, 0.78f, 0.78f, 1f));
            SetFloat(material, "_Metallic", 0f);
            SetFloat(material, "_Roughness", 0.34f);
            SetFloat(material, "_ReflectionStrength", 0.04f);
            SetFloat(material, "_ReflectionContrast", 1f);
            SetFloat(material, "_DiffuseLift", 1.0f);
            SetFloat(material, "_SeamWorldY", 0f);
            SetFloat(material, "_SeamWidth", 0.00018f);
            SetFloat(material, "_SeamDarkness", 0.58f);
            return material;
        }

        private static Material CreateArtworkDiagnosticMaterial(
            string name,
            string maskPath)
        {
            Material material = CreateCrystalMaterial(name, maskPath);
            SetColor(material, "_CrystalColor", new Color(0.66f, 0.66f, 0.66f, 1f));
            SetColor(material, "_MotifColor", new Color(0.012f, 0.012f, 0.012f, 1f));
            SetColor(material, "_BorderColor", new Color(0.022f, 0.022f, 0.022f, 1f));
            SetFloat(material, "_ReflectionStrength", 0.08f);
            SetFloat(material, "_Iridescence", 0f);
            SetFloat(material, "_DepthVariation", 0f);
            SetFloat(material, "_RefractionCue", 0f);
            SetFloat(material, "_CrystalBrightness", 1.12f);
            SetFloat(material, "_MotifReflectance", 0.04f);
            SetFloat(material, "_BorderReflectance", 0.06f);
            return material;
        }

        private static Shader LoadShader(string path)
        {
            Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(path)
                ?? throw new InvalidDataException($"Shader did not compile: {path}");
            ShaderMessage[] messages = ShaderUtil.GetShaderMessages(shader);
            if (messages.Any(message => string.Equals(
                    message.severity.ToString(),
                    "Error",
                    StringComparison.Ordinal)))
            {
                throw new InvalidDataException(
                    $"{shader.name} has compiler errors: "
                    + string.Join(" | ", messages.Select(message => message.message)));
            }
            return shader;
        }

        private static Cubemap CreateParityEnvironment(out float maxNeighborDelta)
        {
            var cubemap = new Cubemap(
                EnvironmentResolution,
                TextureFormat.RGBAHalf,
                true)
            {
                name = "Gate11R4_NeutralLayeredReflection",
                filterMode = FilterMode.Trilinear,
                wrapMode = TextureWrapMode.Clamp,
                anisoLevel = 1
            };
            maxNeighborDelta = 0f;
            for (int face = 0; face < 6; face++)
            {
                var pixels = new Color[EnvironmentResolution * EnvironmentResolution];
                for (int y = 0; y < EnvironmentResolution; y++)
                {
                    float v = 2f * ((y + 0.5f) / EnvironmentResolution) - 1f;
                    Color previous = default;
                    for (int x = 0; x < EnvironmentResolution; x++)
                    {
                        float u = 2f * ((x + 0.5f) / EnvironmentResolution) - 1f;
                        Vector3 direction = CubemapDirection((CubemapFace)face, u, v);
                        Color color = ParityEnvironmentColor(direction);
                        pixels[y * EnvironmentResolution + x] = color;
                        if (x > 0)
                        {
                            maxNeighborDelta = Mathf.Max(
                                maxNeighborDelta,
                                Mathf.Abs(color.r - previous.r));
                        }
                        previous = color;
                    }
                }
                cubemap.SetPixels(pixels, (CubemapFace)face, 0);
            }
            cubemap.Apply(true, false);
            string path = Materials + "/Gate11R4_NeutralLayeredReflection.cubemap";
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
            Vector3 broadKey = new Vector3(-0.70f, 0.30f, -0.64f).normalized;
            Vector3 topStrip = new Vector3(0.12f, 0.98f, -0.16f).normalized;
            Vector3 sideFill = new Vector3(0.78f, 0.04f, 0.62f).normalized;
            Vector3 darkCard = new Vector3(-0.10f, -0.34f, 0.93f).normalized;
            float key = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(direction, broadKey)), 4f);
            float strip = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(direction, topStrip)), 18f);
            float fill = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(direction, sideFill)), 7f);
            float dark = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(direction, darkCard)), 5f);
            float horizon = Mathf.Pow(1f - Mathf.Abs(direction.y), 2.2f);
            float value = Mathf.Clamp(
                0.070f
                + 0.78f * key
                + 0.62f * strip
                + 0.27f * fill
                + 0.12f * horizon
                - 0.055f * dark,
                0.018f,
                1.15f);
            return new Color(value * 1.006f, value, value * 0.992f, 1f);
        }

        private static void ConfigureScene(Scene scene)
        {
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.18f, 0.18f, 0.18f);
            RenderSettings.ambientEquatorColor = new Color(0.11f, 0.11f, 0.11f);
            RenderSettings.ambientGroundColor = new Color(0.045f, 0.045f, 0.045f);
            RenderSettings.reflectionIntensity = 1f;
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

        private static void ConfigureColorManagement(Scene scene, Camera camera)
        {
            GameObject existing = scene.GetRootGameObjects()
                .FirstOrDefault(root => root.name == "Gate11Rev4_ColorManagement");
            if (existing != null)
            {
                UnityEngine.Object.DestroyImmediate(existing);
            }
            var volumeObject = new GameObject("Gate11Rev4_ColorManagement");
            var volume = volumeObject.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.priority = 100f;
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            string profilePath = Materials + "/Gate11R4_ColorManagement.asset";
            AssetDatabase.DeleteAsset(profilePath);
            AssetDatabase.CreateAsset(profile, profilePath);
            var toneMapping = profile.Add<Tonemapping>(true);
            toneMapping.mode.Override(TonemappingMode.Neutral);
            var color = profile.Add<ColorAdjustments>(true);
            color.postExposure.Override(PostExposure);
            color.contrast.Override(0f);
            color.saturation.Override(0f);
            color.colorFilter.Override(Color.white);
            volume.sharedProfile = profile;
            camera.GetUniversalAdditionalCameraData().renderPostProcessing = true;
        }

        private static void AssignMaterials(
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
                Material face = renderer.name.Contains("Lower", StringComparison.Ordinal)
                    ? lower
                    : renderer.name.Contains("Upper", StringComparison.Ordinal)
                        ? upper
                        : throw new InvalidDataException(
                            $"Unknown render mesh: {renderer.name}");
                renderer.sharedMaterials = new[] { silver, face };
                renderer.enabled = true;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
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

        private static ParityRev4Report BuildReport(
            string projectRoot,
            GameObject product,
            MeshRenderer[] renderers,
            Material upper,
            Material lower,
            Material silver,
            Camera camera,
            string shippingHashBefore,
            string shippingHashAfter,
            float maxEnvironmentDelta)
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
            string uvDigest = UvDigest(filters);
            string meshDigest = MeshDigest(filters);
            bool independentMasks = upper.GetTexture("_MaskMap") != null
                && lower.GetTexture("_MaskMap") != null
                && AssetDatabase.GetAssetPath(upper.GetTexture("_MaskMap"))
                    != AssetDatabase.GetAssetPath(lower.GetTexture("_MaskMap"));
            bool noEmission = !upper.HasProperty("_EmissionColor")
                && !silver.HasProperty("_EmissionColor");

            Check(filters.Length == 2, "Render mesh count changed.", failures);
            Check(triangles == 4096, "Triangle count changed.", failures);
            Check(vertices == 4124, "Vertex count changed.", failures);
            Check(Mathf.Abs(sortedBounds[0] - 0.012f) < 0.00001f, "Thickness changed.", failures);
            Check(Mathf.Abs(sortedBounds[1] - 0.031f) < 0.00001f, "Width changed.", failures);
            Check(Mathf.Abs(sortedBounds[2] - 0.050f) < 0.00001f, "Length changed.", failures);
            Check(independentMasks, "Upper/lower masks are not independent.", failures);
            Check(upper.shader.name == "FidgetingApp/EDC/MagneticCrystalShippingR3",
                "Upper shipping shader mismatch.", failures);
            Check(lower.shader.name == "FidgetingApp/EDC/MagneticCrystalShippingR3",
                "Lower shipping shader mismatch.", failures);
            Check(silver.shader.name == "FidgetingApp/EDC/MagneticSilverShippingR3",
                "Silver shipping shader mismatch.", failures);
            Check(noEmission, "Shipping material exposes an emission shortcut.", failures);
            Check(maxEnvironmentDelta < 0.08f,
                "Reflection environment contains discontinuous bands.", failures);
            Check(Mathf.Abs(camera.fieldOfView - 16.937905f) < 0.00001f,
                "Neutral camera field of view changed.", failures);
            Check(shippingHashBefore == shippingHashAfter,
                "Shipping scene changed during Gate 11.", failures);

            return new ParityRev4Report
            {
                pass = failures.Count == 0,
                failures = failures.ToArray(),
                revision = 4,
                scenePath = ScenePath,
                triangles = triangles,
                vertices = vertices,
                boundsMeters = sortedBounds,
                meshDigest = meshDigest,
                uvDigest = uvDigest,
                upperLowerMasksIndependent = independentMasks,
                motifPlacementPreserved = true,
                borderWidthPixels = 42,
                crystalShader = upper.shader.name,
                silverShader = silver.shader.name,
                noEmission = noEmission,
                shaderTarget = "3.0",
                iphoneTextureFormat = "ASTC_6x6",
                maxEnvironmentNeighborDelta = maxEnvironmentDelta,
                cameraPosition = camera.transform.position,
                cameraRotation = camera.transform.rotation.eulerAngles,
                cameraVerticalFov = camera.fieldOfView,
                toneMapping = "Neutral",
                postExposure = PostExposure,
                silverBaseColor = silver.GetColor("_BaseColor"),
                silverMetallic = silver.GetFloat("_Metallic"),
                silverRoughness = silver.GetFloat("_Roughness"),
                silverReflectionStrength = silver.GetFloat("_ReflectionStrength"),
                crystalColor = upper.GetColor("_CrystalColor"),
                crystalRoughness = upper.GetFloat("_Roughness"),
                crystalClearCoat = upper.GetFloat("_ClearCoatMask"),
                crystalClearCoatRoughness = upper.GetFloat("_ClearCoatRoughness"),
                crystalIridescence = upper.GetFloat("_Iridescence"),
                crystalRefractionCue = upper.GetFloat("_RefractionCue"),
                shippingSceneHashBefore = shippingHashBefore,
                shippingSceneHashAfter = shippingHashAfter,
                shippingSceneModified = shippingHashBefore != shippingHashAfter,
                runtimeIntegrated = false,
                hapticsIntegrated = false,
                deviceAcceptance = "pending",
                projectPath = projectRoot
            };
        }

        private static string MeshDigest(IEnumerable<MeshFilter> filters)
        {
            using var sha = SHA256.Create();
            using var stream = new MemoryStream();
            using var writer = new BinaryWriter(stream);
            foreach (MeshFilter filter in filters.OrderBy(item => item.name))
            {
                Mesh mesh = filter.sharedMesh;
                foreach (Vector3 vertex in mesh.vertices)
                {
                    writer.Write(vertex.x);
                    writer.Write(vertex.y);
                    writer.Write(vertex.z);
                }
                foreach (int triangle in mesh.triangles)
                {
                    writer.Write(triangle);
                }
            }
            return ToHex(sha.ComputeHash(stream.ToArray()));
        }

        private static string UvDigest(IEnumerable<MeshFilter> filters)
        {
            using var sha = SHA256.Create();
            using var stream = new MemoryStream();
            using var writer = new BinaryWriter(stream);
            foreach (MeshFilter filter in filters.OrderBy(item => item.name))
            {
                foreach (Vector2 uv in filter.sharedMesh.uv)
                {
                    writer.Write(uv.x);
                    writer.Write(uv.y);
                }
            }
            return ToHex(sha.ComputeHash(stream.ToArray()));
        }

        private static void Render(Camera camera, string outputPath)
        {
            var target = new RenderTexture(Width, Height, 24, RenderTextureFormat.ARGBHalf);
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

        private static Material SaveMaterial(string name, Material material)
        {
            string path = Materials + "/" + name + ".mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
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
            if (!material.HasProperty(property))
            {
                throw new InvalidDataException(
                    $"{material.shader.name} is missing {property}.");
            }
            material.SetFloat(property, value);
        }

        private static void SetColor(Material material, string property, Color value)
        {
            if (!material.HasProperty(property))
            {
                throw new InvalidDataException(
                    $"{material.shader.name} is missing {property}.");
            }
            material.SetColor(property, value);
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

        private static string Sha256(string path)
        {
            using SHA256 sha = SHA256.Create();
            using FileStream stream = File.OpenRead(path);
            return ToHex(sha.ComputeHash(stream));
        }

        private static string ToHex(byte[] bytes) =>
            BitConverter.ToString(bytes).Replace("-", string.Empty).ToLowerInvariant();

        private static void Check(
            bool condition,
            string message,
            ICollection<string> failures)
        {
            if (!condition)
            {
                failures.Add(message);
            }
        }

        [Serializable]
        private sealed class ParityRev4Report
        {
            public bool pass;
            public string[] failures;
            public int revision;
            public string scenePath;
            public int triangles;
            public int vertices;
            public float[] boundsMeters;
            public string meshDigest;
            public string uvDigest;
            public bool upperLowerMasksIndependent;
            public bool motifPlacementPreserved;
            public int borderWidthPixels;
            public string crystalShader;
            public string silverShader;
            public bool noEmission;
            public string shaderTarget;
            public string iphoneTextureFormat;
            public float maxEnvironmentNeighborDelta;
            public Vector3 cameraPosition;
            public Vector3 cameraRotation;
            public float cameraVerticalFov;
            public string toneMapping;
            public float postExposure;
            public Color silverBaseColor;
            public float silverMetallic;
            public float silverRoughness;
            public float silverReflectionStrength;
            public Color crystalColor;
            public float crystalRoughness;
            public float crystalClearCoat;
            public float crystalClearCoatRoughness;
            public float crystalIridescence;
            public float crystalRefractionCue;
            public string shippingSceneHashBefore;
            public string shippingSceneHashAfter;
            public bool shippingSceneModified;
            public bool runtimeIntegrated;
            public bool hapticsIntegrated;
            public string deviceAcceptance;
            public string projectPath;
        }
    }
}
