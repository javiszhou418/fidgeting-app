using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using FidgetingApp.EDC.Candidates;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.Editor
{
    public static class MagneticSlideTileGate11Builder
    {
        private const string Root =
            "Assets/_EDC/Candidates/MagneticSlideTileGate11R009";
        private const string Imported = Root + "/Imported";
        private const string Textures = Imported + "/Textures";
        private const string Environment = Imported + "/Environment";
        private const string Materials = Root + "/Materials";
        private const string ScenePath =
            Root + "/Scenes/MagneticSlideTileGate11R009Parity.unity";
        private const string ProductPath =
            Imported + "/magnetic-slide-tile-render-r009.fbx";
        private const string CollisionPath =
            Imported + "/magnetic-slide-tile-collision-r009.fbx";
        private const string EnvironmentPath =
            Environment + "/magnetic-slide-tile-shipping-studio-r008.exr";
        private const string ShippingScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const int Width = 1400;
        private const int Height = 1100;

        private static readonly string[] ExpectedRenderMeshes =
        {
            "BottomExterior",
            "FixedAxisBoss",
            "RotatingCarrierBody",
            "CarrierFollowerLeft",
            "CarrierFollowerRight",
            "BallCandidateLeft",
            "BallCandidateRight",
            "MovingTopBody"
        };

        [MenuItem("Fidgeting/Model Pipeline/Build Magnetic Slide Gate 11 R009")]
        public static void BuildAndCapture()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidenceRoot = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-009");
            Directory.CreateDirectory(evidenceRoot);
            string shippingHashBefore = Sha256(
                Path.Combine(projectRoot, ShippingScenePath));

            ConfigureImporters();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);

            Scene scene = EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            GameObject productPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(ProductPath);
            GameObject collisionPrefab =
                AssetDatabase.LoadAssetAtPath<GameObject>(CollisionPath);
            if (productPrefab == null || collisionPrefab == null)
            {
                throw new InvalidDataException(
                    "Gate 10 render or collision FBX did not import.");
            }

            GameObject product = (GameObject)PrefabUtility.InstantiatePrefab(productPrefab);
            product.name = "MagneticSlideTile_Gate11R009_Candidate";
            product.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);

            GameObject collision =
                (GameObject)PrefabUtility.InstantiatePrefab(collisionPrefab);
            collision.name = "MagneticSlideTile_Gate11R009_Collision";
            collision.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            ConfigureCollision(collision);

            Dictionary<string, Material> materials = CreateMaterials();
            AssignMaterials(product, materials);
            SetReflectionProbeUsage(product);

            Bounds bounds = CalculateBounds(product);
            product.transform.position -= new Vector3(
                bounds.center.x,
                bounds.min.y,
                bounds.center.z);
            collision.transform.position = product.transform.position;
            bounds = CalculateBounds(product);

            Cubemap environmentCubemap = CreateEnvironmentCubemap();
            ConfigureEnvironment(environmentCubemap);
            ReflectionProbe probe = CreateReflectionProbe(environmentCubemap, bounds);
            CreateGround(bounds);
            CreateLights(bounds);
            Camera camera = CreateCamera(bounds);
            CreatePostProcessing();

            GameObject controllerObject = product;
            MagneticSlideTileGate11Metadata metadata =
                controllerObject.AddComponent<MagneticSlideTileGate11Metadata>();
            MagneticSlideTileGate11PreviewController controller =
                controllerObject.AddComponent<MagneticSlideTileGate11PreviewController>();
            Transform carrier = FindTransform(product.transform, "RotatingCarrier");
            Transform movingTop = FindTransform(product.transform, "MovingTop");
            Transform topLocalSlide = FindTransform(product.transform, "TopLocalSlide");
            GameObject orbitTargetObject = new("Gate11OrbitTarget");
            orbitTargetObject.transform.position = bounds.center;
            controller.Configure(
                carrier,
                movingTop,
                topLocalSlide,
                camera,
                orbitTargetObject.transform,
                Vector3.up,
                Vector3.forward);

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();

            CopyReferenceImages(projectRoot, evidenceRoot);
            Render(camera, Path.Combine(evidenceRoot, "unity-shipping-closed.png"));
            RenderExr(camera, Path.Combine(evidenceRoot, "unity-shipping-closed-linear.exr"));

            Material clay = CreateTransientClayMaterial();
            Dictionary<Renderer, Material[]> originalMaterials = SwapToClay(product, clay);
            Render(camera, Path.Combine(evidenceRoot, "unity-clay.png"));
            RestoreMaterials(originalMaterials);
            UnityEngine.Object.DestroyImmediate(clay);

            Material silhouette = CreateTransientSilhouetteMaterial();
            Dictionary<Renderer, Material[]> silhouetteMaterials =
                SwapToClay(product, silhouette);
            GameObject ground = GameObject.Find("Gate11R009Ground");
            bool groundWasActive = ground != null && ground.activeSelf;
            if (ground != null)
            {
                ground.SetActive(false);
            }
            Color previousBackground = camera.backgroundColor;
            camera.backgroundColor = Color.black;
            Render(camera, Path.Combine(evidenceRoot, "unity-silhouette.png"));
            camera.backgroundColor = previousBackground;
            if (ground != null)
            {
                ground.SetActive(groundWasActive);
            }
            RestoreMaterials(silhouetteMaterials);
            UnityEngine.Object.DestroyImmediate(silhouette);

            controller.SetPose(0f, metadata.MaximumTravelMeters);
            Render(camera, Path.Combine(evidenceRoot, "unity-max-open.png"));
            controller.SetPose(12f, metadata.MaximumTravelMeters * 0.5f);
            Render(camera, Path.Combine(evidenceRoot, "unity-detent-12.png"));
            controller.SetPose(36f, 0f);
            Render(camera, Path.Combine(evidenceRoot, "unity-detent-36.png"));
            controller.ResetPose();
            CaptureTurntable(camera, bounds.center, controller, evidenceRoot);
            EditorSceneManager.SaveScene(scene, ScenePath);

            string shippingHashAfter = Sha256(
                Path.Combine(projectRoot, ShippingScenePath));
            Gate11Report report = BuildReport(
                product,
                collision,
                metadata,
                probe,
                camera,
                bounds,
                shippingHashBefore,
                shippingHashAfter);
            File.WriteAllText(
                Path.Combine(evidenceRoot, "unity-import-parity-report.json"),
                JsonUtility.ToJson(report, true));
            File.WriteAllText(
                Path.Combine(evidenceRoot, "unity-scene-path.txt"),
                ScenePath + System.Environment.NewLine);
            AssetDatabase.Refresh();

            if (!report.pass)
            {
                throw new InvalidDataException(
                    "Gate 11 parity report failed: "
                    + string.Join(", ", report.failures));
            }

            Debug.Log(
                $"[MagneticSlideTile] Gate 11 R009 built. Scene={ScenePath}; "
                + $"bounds={report.boundsMeters}; meshes={report.renderMeshCount}; "
                + $"triangles={report.renderTriangleCount}.");
        }

        private static void ConfigureImporters()
        {
            ConfigureModelImporter(ProductPath, true);
            ConfigureModelImporter(CollisionPath, false);

            string[] baseColors =
            {
                Textures + "/upperBaseColor.png",
                Textures + "/lowerBaseColor.png"
            };
            string[] linearTextures =
            {
                Textures + "/upperArtworkMask.png",
                Textures + "/lowerArtworkMask.png",
                Textures + "/perimeterMask.png",
                Textures + "/upper-maskmap-r009.png",
                Textures + "/lower-maskmap-r009.png",
                Textures + "/upperRoughness.png",
                Textures + "/lowerRoughness.png"
            };
            string[] normalTextures =
            {
                Textures + "/upper-normal-r009.png",
                Textures + "/lower-normal-r009.png"
            };

            foreach (string path in baseColors)
            {
                ConfigureTextureImporter(path, true, false);
            }
            foreach (string path in linearTextures)
            {
                ConfigureTextureImporter(path, false, false);
            }
            foreach (string path in normalTextures)
            {
                ConfigureTextureImporter(path, false, true);
            }

            AssetDatabase.ImportAsset(
                EnvironmentPath,
                ImportAssetOptions.ForceSynchronousImport
                | ImportAssetOptions.ForceUpdate);
            if (AssetImporter.GetAtPath(EnvironmentPath) is not TextureImporter environment)
            {
                throw new InvalidDataException("Portable EXR importer missing.");
            }
            environment.textureType = TextureImporterType.Default;
            environment.textureShape = TextureImporterShape.Texture2D;
            environment.sRGBTexture = false;
            environment.isReadable = true;
            environment.mipmapEnabled = false;
            environment.npotScale = TextureImporterNPOTScale.None;
            environment.textureCompression = TextureImporterCompression.Uncompressed;
            environment.wrapModeU = TextureWrapMode.Repeat;
            environment.wrapModeV = TextureWrapMode.Clamp;
            environment.filterMode = FilterMode.Bilinear;
            environment.SaveAndReimport();
        }

        private static void ConfigureModelImporter(string path, bool renderModel)
        {
            AssetDatabase.ImportAsset(
                path,
                ImportAssetOptions.ForceSynchronousImport
                | ImportAssetOptions.ForceUpdate);
            if (AssetImporter.GetAtPath(path) is not ModelImporter importer)
            {
                throw new InvalidDataException($"No ModelImporter for {path}.");
            }
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.preserveHierarchy = true;
            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importVisibility = false;
            importer.materialImportMode = renderModel
                ? ModelImporterMaterialImportMode.ImportStandard
                : ModelImporterMaterialImportMode.None;
            if (renderModel)
            {
                importer.materialLocation = ModelImporterMaterialLocation.InPrefab;
                importer.materialName = ModelImporterMaterialName.BasedOnMaterialName;
                importer.materialSearch = ModelImporterMaterialSearch.Local;
            }
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.optimizeMeshPolygons = false;
            importer.optimizeMeshVertices = false;
            importer.weldVertices = false;
            importer.isReadable = true;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = renderModel
                ? ModelImporterTangents.Import
                : ModelImporterTangents.None;
            importer.SaveAndReimport();
        }

        private static void ConfigureTextureImporter(
            string path,
            bool sRgb,
            bool normalMap)
        {
            AssetDatabase.ImportAsset(
                path,
                ImportAssetOptions.ForceSynchronousImport
                | ImportAssetOptions.ForceUpdate);
            if (AssetImporter.GetAtPath(path) is not TextureImporter importer)
            {
                throw new InvalidDataException($"No TextureImporter for {path}.");
            }
            importer.textureType = normalMap
                ? TextureImporterType.NormalMap
                : TextureImporterType.Default;
            importer.sRGBTexture = sRgb;
            importer.mipmapEnabled = true;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.alphaIsTransparency = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = FilterMode.Trilinear;
            importer.anisoLevel = 4;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.maxTextureSize = 2048;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            TextureImporterPlatformSettings ios =
                importer.GetPlatformTextureSettings("iPhone");
            ios.overridden = false;
            importer.SetPlatformTextureSettings(ios);
            importer.SaveAndReimport();
        }

        private static Dictionary<string, Material> CreateMaterials()
        {
            Shader silverShader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/Silver")
                ?? throw new InvalidDataException("Silver shader missing.");
            Shader crystalShader = Shader.Find(
                "FidgetingApp/MagneticSlideTile/BloodRedCrystal")
                ?? throw new InvalidDataException("Crystal shader missing.");
            Shader lit = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidDataException("URP Lit shader missing.");

            Material silver = new(silverShader) { name = "M_G11R009_PolishedSilver" };
            silver.SetColor("_BaseColor", new Color(0.78f, 0.77f, 0.74f, 1f));
            silver.SetFloat("_Smoothness", 0.925f);
            silver.SetFloat("_ReflectionStrength", 1f);
            silver.SetFloat("_DirectSpecularStrength", 0.35f);

            Material internalSilver = new(silverShader)
            {
                name = "M_G11R009_InternalSilver"
            };
            internalSilver.SetColor("_BaseColor", new Color(0.72f, 0.71f, 0.69f, 1f));
            internalSilver.SetFloat("_Smoothness", 0.84f);
            internalSilver.SetFloat("_ReflectionStrength", 0.82f);
            internalSilver.SetFloat("_DirectSpecularStrength", 0.32f);

            Material crystalUpper = CreateCrystalMaterial(
                crystalShader,
                "M_G11R009_CrystalUpper",
                Textures + "/upperBaseColor.png",
                Textures + "/upper-maskmap-r009.png",
                Textures + "/upper-normal-r009.png",
                Textures + "/upperArtworkMask.png");
            Material crystalLower = CreateCrystalMaterial(
                crystalShader,
                "M_G11R009_CrystalLower",
                Textures + "/lowerBaseColor.png",
                Textures + "/lower-maskmap-r009.png",
                Textures + "/lower-normal-r009.png",
                Textures + "/lowerArtworkMask.png");

            Material dark = new(lit) { name = "M_G11R009_DarkExterior" };
            dark.SetColor("_BaseColor", new Color(0.018f, 0.020f, 0.024f, 1f));
            dark.SetFloat("_Metallic", 0.24f);
            dark.SetFloat("_Smoothness", 0.82f);
            dark.SetFloat("_ClearCoatMask", 0.55f);
            dark.SetFloat("_ClearCoatSmoothness", 0.88f);
            dark.SetFloat("_Cull", 0f);

            Material technical = new(lit) { name = "M_G11R009_Technical" };
            technical.SetColor("_BaseColor", new Color(0.16f, 0.17f, 0.18f, 1f));
            technical.SetFloat("_Metallic", 0.6f);
            technical.SetFloat("_Smoothness", 0.58f);
            technical.SetFloat("_Cull", 0f);

            Material ball = new(lit) { name = "M_G11R009_BallUnknown" };
            ball.SetColor("_BaseColor", new Color(0.78f, 0.80f, 0.82f, 1f));
            ball.SetFloat("_Metallic", 0.5f);
            ball.SetFloat("_Smoothness", 0.86f);
            ball.SetFloat("_Cull", 0f);

            Dictionary<string, Material> result = new()
            {
                ["silver"] = SaveMaterial(silver),
                ["internal"] = SaveMaterial(internalSilver),
                ["upper"] = SaveMaterial(crystalUpper),
                ["lower"] = SaveMaterial(crystalLower),
                ["dark"] = SaveMaterial(dark),
                ["technical"] = SaveMaterial(technical),
                ["ball"] = SaveMaterial(ball)
            };
            return result;
        }

        private static Material CreateCrystalMaterial(
            Shader shader,
            string name,
            string basePath,
            string maskPath,
            string normalPath,
            string artworkPath)
        {
            Material material = new(shader) { name = name };
            material.SetTexture("_BaseMap", LoadTexture(basePath));
            material.SetTexture("_MaskMap", LoadTexture(maskPath));
            material.SetTexture("_BumpMap", LoadTexture(normalPath));
            material.SetTexture("_ArtworkMask", LoadTexture(artworkPath));
            material.SetTexture(
                "_PerimeterMask",
                LoadTexture(Textures + "/perimeterMask.png"));
            material.SetColor("_DeepBloodRed", new Color(0.18f, 0.003f, 0.008f, 1f));
            material.SetColor("_BlackColor", new Color(0.004f, 0.0015f, 0.0018f, 1f));
            material.SetFloat("_Smoothness", 0.965f);
            material.SetFloat("_BlackSmoothness", 0.84f);
            material.SetFloat("_NormalScale", 0.75f);
            material.SetFloat("_ReflectionStrength", 0.85f);
            material.SetFloat("_CoatStrength", 0.34f);
            material.SetFloat("_Iridescence", 0.08f);
            material.SetFloat("_CrystalDepth", 0.22f);
            return material;
        }

        private static Texture2D LoadTexture(string path)
        {
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path)
                ?? throw new InvalidDataException($"Texture missing: {path}");
        }

        private static Material SaveMaterial(Material material)
        {
            string path = Materials + "/" + material.name + ".mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static void AssignMaterials(
            GameObject product,
            IReadOnlyDictionary<string, Material> materials)
        {
            foreach (MeshRenderer renderer in
                     product.GetComponentsInChildren<MeshRenderer>(true))
            {
                Material[] imported = renderer.sharedMaterials;
                Material[] fallback = renderer.name switch
                {
                    "BottomExterior" => new[]
                    {
                        materials["lower"],
                        materials["dark"],
                        materials["silver"],
                        materials["technical"]
                    },
                    "MovingTopBody" => new[]
                    {
                        materials["upper"],
                        materials["dark"],
                        materials["silver"],
                        materials["technical"]
                    },
                    "FixedAxisBoss" => new[] { materials["silver"] },
                    "RotatingCarrierBody" => new[] { materials["internal"] },
                    "CarrierFollowerLeft" or "CarrierFollowerRight"
                        => new[] { materials["technical"] },
                    "BallCandidateLeft" or "BallCandidateRight"
                        => new[] { materials["ball"] },
                    _ => throw new InvalidDataException(
                        $"Unexpected render mesh {renderer.name}.")
                };
                if (imported.Length != fallback.Length)
                {
                    throw new InvalidDataException(
                        $"{renderer.name} expected {fallback.Length} material slots, "
                        + $"imported {imported.Length}.");
                }
                Material[] assigned = imported
                    .Select((material, index) => ResolveImportedMaterial(
                        material != null ? material.name : string.Empty,
                        materials,
                        fallback[index]))
                    .ToArray();
                renderer.sharedMaterials = assigned;
                renderer.enabled = true;
                renderer.forceRenderingOff = false;
                renderer.renderingLayerMask = uint.MaxValue;
                renderer.gameObject.SetActive(true);
                renderer.gameObject.layer = 0;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
            }
        }

        private static Material ResolveImportedMaterial(
            string importedName,
            IReadOnlyDictionary<string, Material> materials,
            Material fallback)
        {
            if (importedName.Contains("Crystal_Upper", StringComparison.OrdinalIgnoreCase))
                return materials["upper"];
            if (importedName.Contains("Crystal_Lower", StringComparison.OrdinalIgnoreCase))
                return materials["lower"];
            if (importedName.Contains("DarkExteriorSide", StringComparison.OrdinalIgnoreCase))
                return materials["dark"];
            if (importedName.Contains("PolishedSilver", StringComparison.OrdinalIgnoreCase))
                return materials["silver"];
            if (importedName.Contains("InternalSilver", StringComparison.OrdinalIgnoreCase))
                return materials["internal"];
            if (importedName.Contains("NeutralTechnical", StringComparison.OrdinalIgnoreCase))
                return materials["technical"];
            if (importedName.Contains("BallCandidate", StringComparison.OrdinalIgnoreCase))
                return materials["ball"];
            return fallback;
        }

        private static void SetReflectionProbeUsage(GameObject product)
        {
            foreach (MeshRenderer renderer in
                     product.GetComponentsInChildren<MeshRenderer>(true))
            {
                renderer.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
                renderer.lightProbeUsage = LightProbeUsage.BlendProbes;
            }
        }

        private static void ConfigureCollision(GameObject collision)
        {
            foreach (MeshRenderer renderer in
                     collision.GetComponentsInChildren<MeshRenderer>(true))
            {
                renderer.enabled = false;
            }
            foreach (MeshFilter filter in
                     collision.GetComponentsInChildren<MeshFilter>(true))
            {
                MeshCollider collider =
                    filter.gameObject.GetComponent<MeshCollider>();
                if (collider == null)
                {
                    collider = filter.gameObject.AddComponent<MeshCollider>();
                }
                collider.sharedMesh = filter.sharedMesh;
                collider.convex = true;
            }
            collision.SetActive(false);
        }

        private static Cubemap CreateEnvironmentCubemap()
        {
            Texture2D source = LoadTexture(EnvironmentPath);
            const int size = 256;
            Cubemap cubemap = new(size, TextureFormat.RGBAHalf, true)
            {
                name = "MagneticSlideTileGate11R009Environment",
                filterMode = FilterMode.Trilinear,
                wrapMode = TextureWrapMode.Clamp,
                anisoLevel = 4
            };
            for (int face = 0; face < 6; face++)
            {
                Color[] pixels = new Color[size * size];
                for (int y = 0; y < size; y++)
                {
                    for (int x = 0; x < size; x++)
                    {
                        Vector3 direction = CubemapDirection(
                            (CubemapFace)face,
                            x,
                            y,
                            size);
                        float u = Mathf.Atan2(direction.x, direction.z)
                            / (2f * Mathf.PI) + 0.5f;
                        float v = Mathf.Asin(direction.y) / Mathf.PI + 0.5f;
                        pixels[y * size + x] = source.GetPixelBilinear(
                            Mathf.Repeat(u, 1f),
                            Mathf.Clamp01(v));
                    }
                }
                cubemap.SetPixels(pixels, (CubemapFace)face, 0);
            }
            cubemap.Apply(true, false);
            string path = Environment + "/MagneticSlideTileGate11R009Environment.cubemap";
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
            Shader skyboxShader = Shader.Find("Skybox/Cubemap")
                ?? throw new InvalidDataException("Skybox/Cubemap missing.");
            Material skybox = new(skyboxShader)
            {
                name = "M_G11R009_Skybox"
            };
            skybox.SetTexture("_Tex", cubemap);
            skybox.SetFloat("_Exposure", -5.50f);
            skybox.SetFloat("_Rotation", 0f);
            string path = Materials + "/M_G11R009_Skybox.mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(skybox, path);
            RenderSettings.skybox = AssetDatabase.LoadAssetAtPath<Material>(path);
            RenderSettings.ambientMode = AmbientMode.Skybox;
            RenderSettings.ambientIntensity = 0.65f;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflection = cubemap;
            RenderSettings.reflectionIntensity = 1f;
            RenderSettings.reflectionBounces = 1;
            QualitySettings.realtimeReflectionProbes = false;
        }

        private static ReflectionProbe CreateReflectionProbe(
            Cubemap cubemap,
            Bounds bounds)
        {
            GameObject probeObject = new("Gate11R009LocalReflectionProbe");
            probeObject.transform.position = bounds.center
                + new Vector3(0f, 0.006f, 0f);
            ReflectionProbe probe = probeObject.AddComponent<ReflectionProbe>();
            probe.mode = ReflectionProbeMode.Custom;
            probe.customBakedTexture = cubemap;
            probe.boxProjection = false;
            probe.size = new Vector3(0.14f, 0.09f, 0.14f);
            probe.center = Vector3.zero;
            probe.intensity = 1f;
            probe.importance = 100;
            probe.blendDistance = 0.02f;
            return probe;
        }

        private static void CreateGround(Bounds bounds)
        {
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Gate11R009Ground";
            ground.transform.position = new Vector3(
                bounds.center.x,
                bounds.min.y - 0.00025f,
                bounds.center.z);
            ground.transform.localScale = new Vector3(0.035f, 1f, 0.035f);
            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit")
                ?? throw new InvalidDataException("URP Unlit missing.");
            Material material = new(unlit) { name = "M_G11R009_Ground" };
            material.SetColor("_BaseColor", new Color(0.035f, 0.031f, 0.033f, 1f));
            material.SetFloat("_Cull", 0f);
            string materialPath = Materials + "/M_G11R009_Ground.mat";
            AssetDatabase.DeleteAsset(materialPath);
            AssetDatabase.CreateAsset(material, materialPath);
            MeshRenderer renderer = ground.GetComponent<MeshRenderer>();
            renderer.sharedMaterial =
                AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
        }

        private static void CreateLights(Bounds bounds)
        {
            Vector3 target = bounds.center;
            CreateDirectional(
                "Gate11R009Key",
                new Color(1f, 0.98f, 0.94f),
                1.70f,
                new Vector3(-58f, -120f, 70f),
                target);
            CreateDirectional(
                "Gate11R009Fill",
                new Color(0.90f, 0.95f, 1f),
                0.48f,
                new Vector3(-54f, -12f, 58f),
                target);
            CreateDirectional(
                "Gate11R009Rim",
                Color.white,
                0.72f,
                new Vector3(44f, 70f, 62f),
                target);
            CreatePoint(
                "Gate11R009MechanismReveal",
                new Color(1f, 0.90f, 0.80f),
                2.2f,
                new Vector3(-0.026f, 0.028f, -0.020f),
                0.18f);
        }

        private static void CreateDirectional(
            string name,
            Color color,
            float intensity,
            Vector3 sourceMillimeters,
            Vector3 target)
        {
            GameObject lightObject = new(name);
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.None;
            Vector3 source = new(
                sourceMillimeters.x * 0.001f,
                sourceMillimeters.z * 0.001f,
                -sourceMillimeters.y * 0.001f);
            lightObject.transform.rotation = Quaternion.LookRotation(
                target - source,
                Vector3.up);
        }

        private static void CreatePoint(
            string name,
            Color color,
            float intensity,
            Vector3 position,
            float range)
        {
            GameObject lightObject = new(name);
            lightObject.transform.position = position;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Point;
            light.color = color;
            light.intensity = intensity;
            light.range = range;
            light.shadows = LightShadows.None;
        }

        private static Camera CreateCamera(Bounds bounds)
        {
            GameObject cameraObject = new("CAM_Gate11R009Parity");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.Skybox;
            camera.backgroundColor = new Color(0.008f, 0.009f, 0.011f, 1f);
            camera.allowHDR = true;
            camera.allowMSAA = true;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 10f;
            camera.sensorSize = new Vector2(36f, 36f / ((float)Width / Height));
            camera.focalLength = 76f;
            camera.fieldOfView = Camera.FocalLengthToFieldOfView(
                camera.focalLength,
                camera.sensorSize.y);
            UniversalAdditionalCameraData additional =
                cameraObject.AddComponent<UniversalAdditionalCameraData>();
            additional.renderPostProcessing = true;
            additional.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            additional.antialiasingQuality = AntialiasingQuality.High;

            Vector3 target = new(0f, 0.005f, -0.002f);
            camera.transform.position = new Vector3(0.074f, 0.072f, -0.116f);
            camera.transform.LookAt(target);
            camera.tag = "MainCamera";
            return camera;
        }

        private static void CreatePostProcessing()
        {
            VolumeProfile profile = ScriptableObject.CreateInstance<VolumeProfile>();
            profile.name = "Gate11R009ParityVolume";
            Tonemapping tone = profile.Add<Tonemapping>(true);
            tone.mode.Override(TonemappingMode.ACES);
            WhiteBalance whiteBalance = profile.Add<WhiteBalance>(true);
            whiteBalance.temperature.Override(0f);
            whiteBalance.tint.Override(10f);
            ColorAdjustments color = profile.Add<ColorAdjustments>(true);
            color.postExposure.Override(0.70f);
            string path = Root + "/Materials/Gate11R009ParityVolume.asset";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(profile, path);
            GameObject volumeObject = new("Gate11R009GlobalVolume");
            Volume volume = volumeObject.AddComponent<Volume>();
            volume.isGlobal = true;
            volume.priority = 100;
            volume.sharedProfile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(path);
        }

        private static Bounds CalculateBounds(GameObject root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => renderer.enabled)
                .ToArray();
            if (renderers.Length == 0)
            {
                throw new InvalidDataException("No renderers in imported product.");
            }
            Bounds bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers.Skip(1))
            {
                bounds.Encapsulate(renderer.bounds);
            }
            return bounds;
        }

        private static Transform FindTransform(Transform root, string name)
        {
            foreach (Transform transform in root.GetComponentsInChildren<Transform>(true))
            {
                if (string.Equals(transform.name, name, StringComparison.Ordinal))
                {
                    return transform;
                }
            }
            throw new InvalidDataException($"Transform missing: {name}");
        }

        private static Material CreateTransientClayMaterial()
        {
            Shader lit = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidDataException("URP Lit missing.");
            Material clay = new(lit);
            clay.SetColor("_BaseColor", new Color(0.62f, 0.63f, 0.64f, 1f));
            clay.SetFloat("_Metallic", 0f);
            clay.SetFloat("_Smoothness", 0.42f);
            clay.SetFloat("_Cull", 0f);
            return clay;
        }

        private static Material CreateTransientSilhouetteMaterial()
        {
            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit")
                ?? throw new InvalidDataException("URP Unlit missing.");
            Material silhouette = new(unlit);
            silhouette.SetColor("_BaseColor", Color.white);
            silhouette.SetFloat("_Cull", 0f);
            return silhouette;
        }

        private static Dictionary<Renderer, Material[]> SwapToClay(
            GameObject product,
            Material clay)
        {
            Dictionary<Renderer, Material[]> originals = new();
            foreach (Renderer renderer in product.GetComponentsInChildren<Renderer>(true))
            {
                originals[renderer] = renderer.sharedMaterials;
                renderer.sharedMaterials = Enumerable
                    .Repeat(clay, renderer.sharedMaterials.Length)
                    .ToArray();
            }
            return originals;
        }

        private static void RestoreMaterials(
            IReadOnlyDictionary<Renderer, Material[]> originals)
        {
            foreach ((Renderer renderer, Material[] materials) in originals)
            {
                renderer.sharedMaterials = materials;
            }
        }

        private static void CopyReferenceImages(
            string projectRoot,
            string evidenceRoot)
        {
            string blender = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-008/shipping-closed-hero.png");
            string clay = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-002/pass-clay.png");
            File.Copy(blender, Path.Combine(evidenceRoot, "blender-shipping-closed.png"), true);
            File.Copy(clay, Path.Combine(evidenceRoot, "blender-clay.png"), true);
        }

        private static void Render(Camera camera, string path)
        {
            Render(camera, path, Width, Height);
        }

        private static void Render(
            Camera camera,
            string path,
            int width,
            int height)
        {
            RenderTexture target = new(
                width,
                height,
                24,
                RenderTextureFormat.ARGB32);
            target.antiAliasing = 4;
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            try
            {
                target.Create();
                camera.targetTexture = target;
                UnityEngine.Rendering.RenderPipeline.StandardRequest request = new()
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
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

        private static void CaptureTurntable(
            Camera camera,
            Vector3 target,
            MagneticSlideTileGate11PreviewController controller,
            string evidenceRoot)
        {
            string folder = Path.Combine(evidenceRoot, "turntable-frames");
            Directory.CreateDirectory(folder);
            const int frameCount = 72;
            const float radius = 0.165f;
            const float height = 0.078f;
            Vector3 originalPosition = camera.transform.position;
            Quaternion originalRotation = camera.transform.rotation;
            for (int frame = 0; frame < frameCount; frame++)
            {
                if (frame < 18)
                {
                    controller.SetPose(0f, 0f);
                }
                else if (frame < 36)
                {
                    controller.SetPose(0f, 0.018076433f);
                }
                else if (frame < 54)
                {
                    controller.SetPose(12f, 0.009038216f);
                }
                else
                {
                    controller.SetPose(36f, 0f);
                }

                float radians = frame * Mathf.PI * 2f / frameCount;
                camera.transform.position = target + new Vector3(
                    Mathf.Sin(radians) * radius,
                    height,
                    Mathf.Cos(radians) * radius);
                camera.transform.LookAt(target + new Vector3(0f, 0.004f, 0f));
                Render(
                    camera,
                    Path.Combine(folder, $"frame-{frame:D3}.png"),
                    960,
                    720);
            }
            controller.ResetPose();
            camera.transform.SetPositionAndRotation(
                originalPosition,
                originalRotation);
        }

        private static void RenderExr(Camera camera, string path)
        {
            RenderTexture target = new(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGBFloat,
                RenderTextureReadWrite.Linear);
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            try
            {
                target.Create();
                camera.targetTexture = target;
                UnityEngine.Rendering.RenderPipeline.StandardRequest request = new()
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
                RenderTexture.active = target;
                Texture2D image = new(Width, Height, TextureFormat.RGBAFloat, false, true);
                image.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(
                    path,
                    image.EncodeToEXR(Texture2D.EXRFlags.CompressZIP));
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

        private static Gate11Report BuildReport(
            GameObject product,
            GameObject collision,
            MagneticSlideTileGate11Metadata metadata,
            ReflectionProbe probe,
            Camera camera,
            Bounds bounds,
            string shippingHashBefore,
            string shippingHashAfter)
        {
            MeshFilter[] renderFilters = product
                .GetComponentsInChildren<MeshFilter>(true);
            MeshFilter[] collisionFilters = collision
                .GetComponentsInChildren<MeshFilter>(true);
            string[] renderNames = renderFilters.Select(filter => filter.name)
                .OrderBy(name => name)
                .ToArray();
            int triangles = renderFilters.Sum(
                filter => filter.sharedMesh.triangles.Length / 3);
            int vertices = renderFilters.Sum(
                filter => filter.sharedMesh.vertexCount);
            Vector3 size = bounds.size;
            float[] sortedBounds = { size.x, size.y, size.z };
            Array.Sort(sortedBounds);

            List<string> failures = new();
            if (!ExpectedRenderMeshes.OrderBy(name => name).SequenceEqual(renderNames))
                failures.Add("render mesh names");
            if (Mathf.Abs(sortedBounds[0] - 0.012f) > 0.00001f
                || Mathf.Abs(sortedBounds[1] - 0.031f) > 0.00001f
                || Mathf.Abs(sortedBounds[2] - 0.050f) > 0.00001f)
                failures.Add("bounds");
            if (renderFilters.Any(filter =>
                    filter.sharedMesh.normals.Length != filter.sharedMesh.vertexCount))
                failures.Add("normals");
            if (renderFilters.Any(filter =>
                    filter.sharedMesh.tangents.Length != filter.sharedMesh.vertexCount))
                failures.Add("tangents");
            if (renderFilters.Any(filter =>
                    filter.sharedMesh.uv.Length != filter.sharedMesh.vertexCount))
                failures.Add("uvs");
            if (collisionFilters.Length != 2)
                failures.Add("collision meshes");
            if (shippingHashBefore != shippingHashAfter)
                failures.Add("shipping scene changed");
            if (product.GetComponentsInChildren<Animator>(true).Length > 0)
                failures.Add("animator");
            if (product.GetComponentsInChildren<Animation>(true).Length > 0)
                failures.Add("animation");
            Vector3 viewportCenter = camera.WorldToViewportPoint(bounds.center);
            if (viewportCenter.z <= 0f
                || viewportCenter.x <= 0f
                || viewportCenter.x >= 1f
                || viewportCenter.y <= 0f
                || viewportCenter.y >= 1f)
                failures.Add("camera does not frame model");
            if (product.GetComponentsInChildren<Renderer>(true)
                .Any(renderer => !renderer.enabled || !renderer.gameObject.activeInHierarchy))
                failures.Add("renderers disabled");

            return new Gate11Report
            {
                schemaVersion = 1,
                gate = "11-unity-parity",
                revision = 9,
                unityVersion = Application.unityVersion,
                scenePath = ScenePath,
                boundsMeters = $"{size.x:F9}×{size.y:F9}×{size.z:F9}",
                sortedBoundsMeters = sortedBounds,
                renderMeshCount = renderFilters.Length,
                renderVertexCount = vertices,
                renderTriangleCount = triangles,
                renderMeshNames = renderNames,
                collisionMeshCount = collisionFilters.Length,
                collisionTriangleCounts = collisionFilters
                    .Select(filter => filter.sharedMesh.triangles.Length / 3)
                    .ToArray(),
                fixedAxisFound = FindTransform(product.transform, "FixedAxis") != null,
                fourGroovesFound = new[]
                {
                    "TopOuterGrooveLeft",
                    "TopInnerGrooveLeft",
                    "TopInnerGrooveRight",
                    "TopOuterGrooveRight"
                }.All(name => FindTransform(product.transform, name) != null),
                materialCount = AssetDatabase.FindAssets(
                        "t:Material",
                        new[] { Materials })
                    .Length,
                shaderCount = 2,
                reflectionProbeMode = probe.mode.ToString(),
                reflectionProbeBoxProjection = probe.boxProjection,
                cameraFocalLengthMm = camera.focalLength,
                cameraVerticalFovDegrees = camera.fieldOfView,
                cameraViewportCenter = viewportCenter,
                gate10GlbSha256 = metadata.Gate10GlbSha256,
                geometryDigest = metadata.GeometryDigest,
                portabilityContractSha256 = metadata.PortabilityContractSha256,
                maximumTravelMeters = metadata.MaximumTravelMeters,
                detentCount = metadata.DetentCount,
                detentStepDegrees = metadata.DetentStepDegrees,
                provisionalDimensions = metadata.ProvisionalDimensions,
                shippingSceneHashBefore = shippingHashBefore,
                shippingSceneHashAfter = shippingHashAfter,
                shippingSceneModified = shippingHashBefore != shippingHashAfter,
                oldShippingModelDefault = true,
                buildInstallDevice = false,
                failures = failures.ToArray(),
                pass = failures.Count == 0
            };
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
            public string gate = "";
            public int revision;
            public string unityVersion = "";
            public string scenePath = "";
            public string boundsMeters = "";
            public float[] sortedBoundsMeters = Array.Empty<float>();
            public int renderMeshCount;
            public int renderVertexCount;
            public int renderTriangleCount;
            public string[] renderMeshNames = Array.Empty<string>();
            public int collisionMeshCount;
            public int[] collisionTriangleCounts = Array.Empty<int>();
            public bool fixedAxisFound;
            public bool fourGroovesFound;
            public int materialCount;
            public int shaderCount;
            public string reflectionProbeMode = "";
            public bool reflectionProbeBoxProjection;
            public float cameraFocalLengthMm;
            public float cameraVerticalFovDegrees;
            public Vector3 cameraViewportCenter;
            public string gate10GlbSha256 = "";
            public string geometryDigest = "";
            public string portabilityContractSha256 = "";
            public float maximumTravelMeters;
            public int detentCount;
            public float detentStepDegrees;
            public bool provisionalDimensions;
            public string shippingSceneHashBefore = "";
            public string shippingSceneHashAfter = "";
            public bool shippingSceneModified;
            public bool oldShippingModelDefault;
            public bool buildInstallDevice;
            public string[] failures = Array.Empty<string>();
            public bool pass;
        }
    }
}
