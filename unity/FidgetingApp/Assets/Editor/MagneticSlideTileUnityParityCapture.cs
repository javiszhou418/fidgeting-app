using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Profiling;
using UnityEngine.Rendering;

namespace FidgetingApp.EditorTools
{
    public static class MagneticSlideTileUnityParityCapture
    {
        private const string Root = "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001";
        private const string Imported = Root + "/Imported";
        private const string Materials = Root + "/Materials";
        private const string ProductPath = Imported + "/magnetic-slide-tile-r002.fbx";
        private const string CollisionPath = Imported + "/magnetic-slide-tile-collision-r002.fbx";
        private const string ScenePath = Root + "/MagneticSlideTileNeutralParity.unity";
        private const string ShippingScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const int Width = 1600;
        private const int Height = 900;

        public static void CaptureBatch()
        {
            Capture();
        }

        private static void Capture()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string exportRoot = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-002");
            string evidenceRoot = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-001");
            Directory.CreateDirectory(evidenceRoot);
            string shippingHashBefore = Sha256(Path.Combine(projectRoot, ShippingScenePath));

            EnsureFolder(Root);
            EnsureFolder(Imported);
            EnsureFolder(Materials);
            CopyAndImportModel(
                Path.Combine(exportRoot, "magnetic-slide-tile-r002.fbx"),
                ProductPath,
                true);
            CopyAndImportModel(
                Path.Combine(exportRoot, "magnetic-slide-tile-collision-r002.fbx"),
                CollisionPath,
                false);

            string[] textureNames =
            {
                "artwork-lower-channel-pack.png",
                "artwork-lower-mask.png",
                "artwork-top-perimeter-border-mask.png",
                "artwork-upper-channel-pack.png",
                "artwork-upper-mask.png",
                "face-lower-transport-basecolor.png",
                "face-upper-transport-basecolor.png"
            };
            foreach (string file in textureNames)
            {
                CopyAndImportTexture(
                    Path.Combine(exportRoot, "textures", file),
                    Imported + "/" + file,
                    file);
            }

            var recipe = JsonUtility.FromJson<CameraRecipeFile>(
                File.ReadAllText(Path.Combine(evidenceRoot, "neutral-camera-recipe.json")));
            if (recipe?.camera == null)
            {
                throw new InvalidDataException("Gate 11 camera recipe is invalid.");
            }

            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject productPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(ProductPath);
            GameObject collisionPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(CollisionPath);
            if (productPrefab == null || collisionPrefab == null)
            {
                throw new InvalidDataException("Unity did not import the isolated Gate 11 assets.");
            }

            GameObject product = UnityEngine.Object.Instantiate(productPrefab);
            product.name = "Gate11_MagneticSlideTile";
            GameObject collision = UnityEngine.Object.Instantiate(collisionPrefab);
            collision.name = "Gate11_Collision_Proxies";
            ConfigureCollision(collision);

            Material silver = SaveMaterial(
                "M_Gate11_PolishedSilver",
                CreateSilverMaterial());
            Material lower = SaveMaterial(
                "M_Gate11_BloodRedLower",
                CreateFaceMaterial(
                    "M_Gate11_BloodRedLower",
                    Imported + "/face-lower-transport-basecolor.png"));
            Material upper = SaveMaterial(
                "M_Gate11_BloodRedUpper",
                CreateFaceMaterial(
                    "M_Gate11_BloodRedUpper",
                    Imported + "/face-upper-transport-basecolor.png"));
            AssignMaterials(product, silver);
            int artworkPreviewMeshes = CreateArtworkOverlays(product, lower, upper);

            Cubemap reflection = CreateReflectionCubemap();
            ReflectionProbe probe = CreateReflectionProbe(reflection);
            ConfigureEnvironment(reflection);
            CreateLighting();
            Camera camera = CreateCamera(recipe);

            var metadataObject = new GameObject("Gate11_SpecifiedOnly_Metadata");
            metadataObject.AddComponent<FidgetingApp.ModelPipeline.MagneticSlideTileParityMetadata>();
            EditorSceneManager.SaveScene(
                UnityEngine.SceneManagement.SceneManager.GetActiveScene(),
                ScenePath);

            string output = Path.Combine(evidenceRoot, "unity-neutral.png");
            Render(camera, output);
            Renderer[] parityRenderers = product.GetComponentsInChildren<Renderer>(true);
            Material[][] parityMaterials = parityRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            foreach (Renderer renderer in parityRenderers)
            {
                renderer.sharedMaterials = Enumerable
                    .Repeat(silver, renderer.sharedMaterials.Length)
                    .ToArray();
            }
            Render(
                camera,
                Path.Combine(evidenceRoot, "unity-neutral-all-silver-diagnostic.png"));
            for (int index = 0; index < parityRenderers.Length; index++)
            {
                parityRenderers[index].sharedMaterials = parityMaterials[index];
            }
            string shippingHashAfter = Sha256(Path.Combine(projectRoot, ShippingScenePath));
            UnityParityReport report = BuildReport(
                product,
                collision,
                artworkPreviewMeshes,
                probe,
                recipe,
                camera,
                output,
                shippingHashBefore,
                shippingHashAfter);
            File.WriteAllText(
                Path.Combine(evidenceRoot, "unity-import-parity-report.json"),
                JsonUtility.ToJson(report, true) + "\n");
            AssetDatabase.SaveAssets();
            Debug.Log(
                $"[MagneticSlideTileUnityParity] pass={report.pass} "
                + $"tris={report.triangles} bounds={report.bounds.extent} "
                + $"output={output}");
            if (!report.pass)
            {
                throw new InvalidDataException(
                    "Magnetic slide Unity parity failed: "
                    + string.Join(" | ", report.failures));
            }
        }

        private static void CopyAndImportModel(
            string source,
            string assetPath,
            bool renderModel)
        {
            CopySource(source, assetPath);
            AssetDatabase.ImportAsset(
                assetPath,
                ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
            if (AssetImporter.GetAtPath(assetPath) is not ModelImporter importer)
            {
                throw new InvalidDataException($"No ModelImporter for {assetPath}.");
            }
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importVisibility = false;
            importer.preserveHierarchy = true;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
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

        private static void CopyAndImportTexture(
            string source,
            string assetPath,
            string file)
        {
            CopySource(source, assetPath);
            AssetDatabase.ImportAsset(
                assetPath,
                ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
            if (AssetImporter.GetAtPath(assetPath) is not TextureImporter importer)
            {
                throw new InvalidDataException($"No TextureImporter for {assetPath}.");
            }
            bool channelPack = file.Contains("channel-pack", StringComparison.Ordinal);
            bool baseColor = file.Contains("basecolor", StringComparison.Ordinal);
            importer.textureType = TextureImporterType.Default;
            importer.maxTextureSize = 1024;
            importer.mipmapEnabled = channelPack;
            importer.sRGBTexture = baseColor;
            importer.alphaSource = channelPack
                ? TextureImporterAlphaSource.FromInput
                : TextureImporterAlphaSource.None;
            importer.alphaIsTransparency = false;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.filterMode = channelPack
                ? FilterMode.Trilinear
                : FilterMode.Bilinear;
            importer.isReadable = true;
            if (channelPack || baseColor)
            {
                var ios = importer.GetPlatformTextureSettings("iPhone");
                ios.name = "iPhone";
                ios.overridden = true;
                ios.maxTextureSize = 1024;
                ios.resizeAlgorithm = TextureResizeAlgorithm.Mitchell;
                ios.format = channelPack
                    ? TextureImporterFormat.ASTC_4x4
                    : TextureImporterFormat.ASTC_6x6;
                ios.compressionQuality = 100;
                importer.SetPlatformTextureSettings(ios);
            }
            importer.SaveAndReimport();
        }

        private static void CopySource(string source, string assetPath)
        {
            if (!File.Exists(source))
            {
                throw new FileNotFoundException("Gate 10 source is missing.", source);
            }
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string destination = Path.Combine(projectRoot, assetPath);
            Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
            File.Copy(source, destination, true);
        }

        private static Material CreateSilverMaterial()
        {
            Material material = NewUrpMaterial("M_Gate11_PolishedSilver");
            SetColor(material, "_BaseColor", new Color(0.97f, 0.965f, 0.94f, 1f));
            SetFloat(material, "_Metallic", 1f);
            SetFloat(material, "_Smoothness", 0.97f);
            SetFloat(material, "_ClearCoatMask", 0.06f);
            SetFloat(material, "_ClearCoatSmoothness", 0.98f);
            SetFloat(material, "_EmissionColor", 0f);
            return material;
        }

        private static Material CreateFaceMaterial(string name, string texturePath)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Unlit")
                ?? throw new InvalidDataException("URP Unlit shader is unavailable.");
            var material = new Material(shader) { name = name };
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
            if (texture == null)
            {
                throw new InvalidDataException($"Missing face texture {texturePath}.");
            }
            SetTexture(material, "_BaseMap", texture);
            SetColor(material, "_BaseColor", Color.white);
            SetFloat(material, "_EmissionColor", 0f);
            return material;
        }

        private static Material NewUrpMaterial(string name)
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit")
                ?? throw new InvalidDataException("URP Lit shader is unavailable.");
            return new Material(shader) { name = name };
        }

        private static Material SaveMaterial(string name, Material material)
        {
            string path = Materials + "/" + name + ".mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static void AssignMaterials(
            GameObject product,
            Material silver)
        {
            Renderer[] renderers = product.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length != 2)
            {
                throw new InvalidDataException(
                    $"Expected two renderers, found {renderers.Length}.");
            }
            foreach (Renderer renderer in renderers)
            {
                if (!renderer.name.Contains("Lower", StringComparison.Ordinal)
                    && !renderer.name.Contains("Upper", StringComparison.Ordinal))
                {
                    throw new InvalidDataException($"Unknown render object {renderer.name}.");
                }
                renderer.sharedMaterials = new[] { silver, silver };
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
            }
        }

        private static int CreateArtworkOverlays(
            GameObject product,
            Material lower,
            Material upper)
        {
            int count = 0;
            foreach (MeshFilter source in product.GetComponentsInChildren<MeshFilter>(true))
            {
                Material material = source.name.Contains("Lower", StringComparison.Ordinal)
                    ? lower
                    : source.name.Contains("Upper", StringComparison.Ordinal)
                        ? upper
                        : null;
                if (material == null || source.sharedMesh.subMeshCount < 2)
                {
                    continue;
                }
                Mesh sourceMesh = source.sharedMesh;
                var overlayMesh = new Mesh
                {
                    name = source.name + "_Gate11ArtworkPreview"
                };
                overlayMesh.vertices = sourceMesh.vertices;
                overlayMesh.uv = sourceMesh.uv;
                overlayMesh.normals = sourceMesh.normals;
                overlayMesh.tangents = sourceMesh.tangents;
                overlayMesh.triangles = sourceMesh.GetTriangles(1);
                overlayMesh.RecalculateBounds();

                var overlay = new GameObject(source.name + "_ArtworkPreview");
                overlay.transform.SetParent(source.transform, false);
                overlay.transform.localPosition = Vector3.forward * 0.00001f;
                overlay.transform.localRotation = Quaternion.identity;
                overlay.transform.localScale = Vector3.one;
                overlay.AddComponent<MeshFilter>().sharedMesh = overlayMesh;
                MeshRenderer renderer = overlay.AddComponent<MeshRenderer>();
                renderer.sharedMaterial = material;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
                count += 1;
            }
            return count;
        }

        private static void ConfigureCollision(GameObject collision)
        {
            foreach (Renderer renderer in collision.GetComponentsInChildren<Renderer>(true))
            {
                renderer.enabled = false;
            }
            foreach (MeshFilter filter in collision.GetComponentsInChildren<MeshFilter>(true))
            {
                MeshCollider collider = filter.gameObject.GetComponent<MeshCollider>();
                if (collider == null)
                {
                    collider = filter.gameObject.AddComponent<MeshCollider>();
                }
                collider.sharedMesh = filter.sharedMesh;
                collider.convex = true;
            }
            collision.SetActive(false);
        }

        private static Cubemap CreateReflectionCubemap()
        {
            var cubemap = new Cubemap(32, TextureFormat.RGBA32, false)
            {
                name = "Gate11_NeutralReflection"
            };
            Color[] colors =
            {
                new(0.86f, 0.85f, 0.82f), new(0.10f, 0.11f, 0.12f),
                new(0.48f, 0.49f, 0.48f), new(0.04f, 0.05f, 0.06f),
                new(0.72f, 0.71f, 0.68f), new(0.16f, 0.17f, 0.18f)
            };
            for (int face = 0; face < 6; face++)
            {
                cubemap.SetPixels(
                    Enumerable.Repeat(colors[face], 32 * 32).ToArray(),
                    (CubemapFace)face);
            }
            cubemap.Apply(false, true);
            string path = Materials + "/Gate11_NeutralReflection.cubemap";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(cubemap, path);
            return AssetDatabase.LoadAssetAtPath<Cubemap>(path);
        }

        private static ReflectionProbe CreateReflectionProbe(Cubemap cubemap)
        {
            var probeObject = new GameObject("Gate11_LocalReflectionProbe");
            ReflectionProbe probe = probeObject.AddComponent<ReflectionProbe>();
            probe.mode = ReflectionProbeMode.Custom;
            probe.customBakedTexture = cubemap;
            probe.boxProjection = true;
            probe.size = new Vector3(0.16f, 0.10f, 0.16f);
            probe.center = Vector3.zero;
            probe.intensity = 1f;
            probe.importance = 100;
            return probe;
        }

        private static void ConfigureEnvironment(Cubemap cubemap)
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.24f, 0.24f, 0.24f);
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflection = cubemap;
            RenderSettings.reflectionIntensity = 1f;
            RenderSettings.reflectionBounces = 1;
            QualitySettings.realtimeReflectionProbes = false;
        }

        private static void CreateLighting()
        {
            CreateDirectional("Gate11_Key", new Color(1f, 0.99f, 0.97f), 1.15f, new Vector3(48f, -32f, 0f));
            CreateDirectional("Gate11_Fill", Color.white, 0.42f, new Vector3(55f, 138f, 0f));
        }

        private static void CreateDirectional(
            string name,
            Color color,
            float intensity,
            Vector3 rotation)
        {
            var lightObject = new GameObject(name);
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.None;
            lightObject.transform.rotation = Quaternion.Euler(rotation);
        }

        private static Camera CreateCamera(CameraRecipeFile recipe)
        {
            var cameraObject = new GameObject("CAM_Gate11Neutral");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.transform.position = ArrayToVector(recipe.camera.unityPositionMeters);
            Vector3 target = ArrayToVector(recipe.camera.unityLookAtMeters);
            camera.transform.rotation = Quaternion.LookRotation(
                target - camera.transform.position,
                Vector3.up);
            camera.fieldOfView = recipe.camera.verticalFovDegrees;
            camera.nearClipPlane = recipe.camera.nearMeters;
            camera.farClipPlane = recipe.camera.farMeters;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(
                recipe.backgroundLinearRgb[0],
                recipe.backgroundLinearRgb[1],
                recipe.backgroundLinearRgb[2],
                1f);
            camera.allowHDR = false;
            camera.allowMSAA = true;
            return camera;
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

        private static UnityParityReport BuildReport(
            GameObject product,
            GameObject collision,
            int artworkPreviewMeshes,
            ReflectionProbe probe,
            CameraRecipeFile recipe,
            Camera camera,
            string output,
            string shippingHashBefore,
            string shippingHashAfter)
        {
            var failures = new List<string>();
            MeshFilter[] filters = product.GetComponentsInChildren<MeshFilter>(true)
                .Where(filter => !filter.name.EndsWith("_ArtworkPreview", StringComparison.Ordinal))
                .ToArray();
            Renderer[] renderers = product.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => !renderer.name.EndsWith("_ArtworkPreview", StringComparison.Ordinal))
                .ToArray();
            MeshFilter[] collisionFilters = collision.GetComponentsInChildren<MeshFilter>(true);
            int triangles = filters.Sum(filter => filter.sharedMesh.triangles.Length / 3);
            int vertices = filters.Sum(filter => filter.sharedMesh.vertexCount);
            int[] collisionTriangles = collisionFilters
                .Select(filter => filter.sharedMesh.triangles.Length / 3)
                .OrderBy(value => value)
                .ToArray();
            Bounds bounds = CombinedBounds(renderers);
            float[] sortedBounds = { bounds.size.x, bounds.size.y, bounds.size.z };
            Array.Sort(sortedBounds);
            float[] expectedBounds = { 0.012f, 0.031f, 0.050f };
            float boundsError = sortedBounds.Zip(
                expectedBounds,
                (actual, expected) => RelativeError(expected, actual)).Max();

            bool uvValid = filters.All(filter =>
                filter.sharedMesh.uv.Length == filter.sharedMesh.vertexCount);
            bool normalsValid = filters.All(filter =>
                filter.sharedMesh.normals.Length == filter.sharedMesh.vertexCount);
            bool tangentsValid = filters.All(filter =>
                filter.sharedMesh.tangents.Length == filter.sharedMesh.vertexCount);
            bool materialSlotsValid = renderers.All(renderer =>
                renderer.sharedMaterials.Length == 2);
            bool noAnimation = product.GetComponentsInChildren<Animation>(true).Length == 0
                && product.GetComponentsInChildren<Animator>(true).Length == 0;
            NormalRecord normals = MeasureNormals(filters);
            ModelImporter importer = AssetImporter.GetAtPath(ProductPath) as ModelImporter;
            TextureRecord[] textures = BuildTextureRecords();

            Check(filters.Length == 2, "Expected exactly two render meshes.", failures);
            Check(triangles == 4096, $"Triangle count changed to {triangles}.", failures);
            Check(boundsError <= 0.001f, $"Bounds error is {boundsError}.", failures);
            Check(collisionFilters.Length == 2, "Expected two collision meshes.", failures);
            Check(collisionTriangles.SequenceEqual(new[] { 128, 128 }), "Collision triangles changed.", failures);
            Check(uvValid, "UV0 is incomplete.", failures);
            Check(normalsValid, "Imported normals are incomplete.", failures);
            Check(tangentsValid, "Imported tangents are incomplete.", failures);
            Check(materialSlotsValid, "Expected silver + face slots on both meshes.", failures);
            Check(noAnimation, "Unexpected animation component exists.", failures);
            Check(normals.maxSideDuplicateAngleDegrees <= 1f, "Curved side normals split.", failures);
            Check(normals.minimumCapSideAngleDegrees >= 80f, "Cap-side hard boundary was lost.", failures);
            Check(shippingHashBefore == shippingHashAfter, "Shipping scene changed.", failures);
            Check(probe.mode == ReflectionProbeMode.Custom, "Probe is not custom/static.", failures);
            Check(textures.Count(record => record.iosFormat == "ASTC_4x4") == 2, "ASTC 4x4 packs missing.", failures);

            return new UnityParityReport
            {
                pass = failures.Count == 0,
                failures = failures.ToArray(),
                unityVersion = Application.unityVersion,
                urpVersion = "17.5.0",
                productAssetPath = ProductPath,
                collisionAssetPath = CollisionPath,
                parityScenePath = ScenePath,
                output = output,
                renderMeshes = filters.Length,
                vertices = vertices,
                triangles = triangles,
                collisionMeshes = collisionFilters.Length,
                collisionTriangles = collisionTriangles,
                bounds = new BoundsRecord { center = bounds.center, extent = bounds.size },
                sortedBoundsMeters = sortedBounds,
                boundsRelativeError = boundsError,
                hierarchy = filters.Select(filter => new HierarchyRecord
                {
                    name = filter.name,
                    parent = filter.transform.parent?.name
                }).ToArray(),
                uv0Valid = uvValid,
                normalsValid = normalsValid,
                tangentsValid = tangentsValid,
                materialSlotsValid = materialSlotsValid,
                submeshes = BuildSubmeshRecords(filters),
                previewArtworkOverlayMeshes = artworkPreviewMeshes,
                previewArtworkOverlayState = "isolated-parity-scene-only-not-shipping-geometry",
                noAnimationOrSelfMotion = noAnimation,
                closedDefaultPosition = product.transform.position,
                closedDefaultRotation = product.transform.eulerAngles,
                pointAxisMeters = new Vector3(0f, 0f, 0.0095f),
                pointAxisDirection = Vector3.up,
                slideDirection = Vector3.back,
                slideTravelMeters = 0.021f,
                detentCount = 30,
                detentStepDegrees = 12f,
                detentDeliveryState = "specified-only-not-runtime-integrated",
                normalMetrics = normals,
                importer = new ImporterRecord
                {
                    globalScale = importer?.globalScale ?? -1f,
                    useFileScale = importer?.useFileScale ?? false,
                    preserveHierarchy = importer?.preserveHierarchy ?? false,
                    importAnimation = importer?.importAnimation ?? true,
                    normals = importer?.importNormals.ToString(),
                    tangents = importer?.importTangents.ToString(),
                    meshCompression = importer?.meshCompression.ToString()
                },
                textures = textures,
                upperLowerArtworkIndependent = textures
                    .Where(record => record.file.Contains("channel-pack"))
                    .Select(record => record.assetPath)
                    .Distinct().Count() == 2,
                camera = new CameraRecord
                {
                    position = camera.transform.position,
                    lookAt = ArrayToVector(recipe.camera.unityLookAtMeters),
                    verticalFovDegrees = camera.fieldOfView,
                    resolution = new Vector2Int(Width, Height)
                },
                reflection = new ReflectionRecord
                {
                    strategy = "static custom local reflection probe + custom neutral cubemap",
                    mode = probe.mode.ToString(),
                    boxProjection = probe.boxProjection,
                    realtimeUpdates = false,
                    approximation = "cubemap approximation; not ray-traced or per-pixel true mirror"
                },
                materialGaps = new[]
                {
                    "URP Lit has no direct parity for Blender thin-film interference.",
                    "Crystal transmission is approximated with an opaque blood-red artwork layer.",
                    "The isolated artwork overlay uses URP Unlit to prevent the face texture from contaminating polished-side parity; crystal response remains a known Gate 11 approximation.",
                    "Silver reflections use a static cubemap/local probe approximation.",
                    "Artwork uses cap-only preview overlays so imported FBX geometry stays immutable; these overlays are not shipping integration.",
                    "AgX and Unity URP tone mapping are not identical."
                },
                shippingScenePath = ShippingScenePath,
                shippingSceneHashBefore = shippingHashBefore,
                shippingSceneHashAfter = shippingHashAfter,
                shippingSceneModified = shippingHashBefore != shippingHashAfter,
                shippingIntegrated = false,
                deviceMemoryMeasured = false,
                deviceAcceptance = "pending"
            };
        }

        private static TextureRecord[] BuildTextureRecords()
        {
            string[] names =
            {
                "artwork-lower-channel-pack.png",
                "artwork-lower-mask.png",
                "artwork-top-perimeter-border-mask.png",
                "artwork-upper-channel-pack.png",
                "artwork-upper-mask.png",
                "face-lower-transport-basecolor.png",
                "face-upper-transport-basecolor.png"
            };
            return names.Select(file =>
            {
                string path = Imported + "/" + file;
                Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
                TextureImporterPlatformSettings ios = importer!.GetPlatformTextureSettings("iPhone");
                int block = ios.format == TextureImporterFormat.ASTC_4x4 ? 4
                    : ios.format == TextureImporterFormat.ASTC_6x6 ? 6 : 0;
                return new TextureRecord
                {
                    file = file,
                    assetPath = path,
                    width = texture.width,
                    height = texture.height,
                    mipmaps = importer.mipmapEnabled,
                    sRgb = importer.sRGBTexture,
                    alphaSource = importer.alphaSource.ToString(),
                    iosOverridden = ios.overridden,
                    iosFormat = ios.overridden ? ios.format.ToString() : "EditorSource",
                    iosMaxSize = ios.overridden ? ios.maxTextureSize : importer.maxTextureSize,
                    editorRuntimeMemoryBytes = Profiler.GetRuntimeMemorySizeLong(texture),
                    iosEstimatedTextureBytes = block > 0
                        ? EstimateAstcBytes(texture.width, texture.height, block, importer.mipmapEnabled)
                        : 0,
                    deviceMemoryMeasured = false
                };
            }).ToArray();
        }

        private static SubmeshRecord[] BuildSubmeshRecords(MeshFilter[] filters)
        {
            var records = new List<SubmeshRecord>();
            foreach (MeshFilter filter in filters)
            {
                Mesh mesh = filter.sharedMesh;
                Renderer renderer = filter.GetComponent<Renderer>();
                for (int submesh = 0; submesh < mesh.subMeshCount; submesh++)
                {
                    int[] indices = mesh.GetTriangles(submesh);
                    int capTriangles = 0;
                    int sideTriangles = 0;
                    Bounds submeshBounds = new(
                        filter.transform.TransformPoint(mesh.vertices[indices[0]]),
                        Vector3.zero);
                    for (int index = 0; index < indices.Length; index += 3)
                    {
                        Vector3 a = filter.transform.TransformPoint(mesh.vertices[indices[index]]);
                        Vector3 b = filter.transform.TransformPoint(mesh.vertices[indices[index + 1]]);
                        Vector3 c = filter.transform.TransformPoint(mesh.vertices[indices[index + 2]]);
                        submeshBounds.Encapsulate(a);
                        submeshBounds.Encapsulate(b);
                        submeshBounds.Encapsulate(c);
                        Vector3 normal = Vector3.Cross(b - a, c - a).normalized;
                        if (Mathf.Abs(normal.y) > 0.8f)
                        {
                            capTriangles += 1;
                        }
                        else
                        {
                            sideTriangles += 1;
                        }
                    }
                    records.Add(new SubmeshRecord
                    {
                        mesh = filter.name,
                        submesh = submesh,
                        material = renderer.sharedMaterials[submesh]?.name,
                        triangles = indices.Length / 3,
                        capTriangles = capTriangles,
                        sideTriangles = sideTriangles,
                        bounds = new BoundsRecord
                        {
                            center = submeshBounds.center,
                            extent = submeshBounds.size
                        }
                    });
                }
            }
            return records.ToArray();
        }

        private static long EstimateAstcBytes(int width, int height, int block, bool mipmaps)
        {
            long total = 0;
            do
            {
                total += (long)Mathf.CeilToInt((float)width / block)
                    * Mathf.CeilToInt((float)height / block) * 16;
                width = Mathf.Max(1, width / 2);
                height = Mathf.Max(1, height / 2);
            }
            while (mipmaps && (width > 1 || height > 1));
            return total;
        }

        private static NormalRecord MeasureNormals(MeshFilter[] filters)
        {
            float maxSideAngle = 0f;
            float minCapSideAngle = 180f;
            bool foundBoundary = false;
            foreach (MeshFilter filter in filters)
            {
                Mesh mesh = filter.sharedMesh;
                var groups = new Dictionary<string, List<Vector3>>();
                for (int index = 0; index < mesh.vertexCount; index++)
                {
                    Vector3 p = filter.transform.TransformPoint(mesh.vertices[index]);
                    string key = $"{Mathf.Round(p.x * 100000f)},{Mathf.Round(p.y * 100000f)},{Mathf.Round(p.z * 100000f)}";
                    if (!groups.TryGetValue(key, out List<Vector3> list))
                    {
                        list = new List<Vector3>();
                        groups.Add(key, list);
                    }
                    list.Add(filter.transform.TransformDirection(mesh.normals[index]).normalized);
                }
                foreach (List<Vector3> normals in groups.Values)
                {
                    Vector3[] side = normals.Where(normal => Mathf.Abs(normal.y) < 0.75f).ToArray();
                    Vector3[] cap = normals.Where(normal => Mathf.Abs(normal.y) > 0.9f).ToArray();
                    for (int i = 0; i < side.Length; i++)
                    {
                        for (int j = i + 1; j < side.Length; j++)
                        {
                            maxSideAngle = Mathf.Max(maxSideAngle, Vector3.Angle(side[i], side[j]));
                        }
                    }
                    foreach (Vector3 capNormal in cap)
                    {
                        foreach (Vector3 sideNormal in side)
                        {
                            foundBoundary = true;
                            minCapSideAngle = Mathf.Min(
                                minCapSideAngle,
                                Vector3.Angle(capNormal, sideNormal));
                        }
                    }
                }
            }
            return new NormalRecord
            {
                maxSideDuplicateAngleDegrees = maxSideAngle,
                minimumCapSideAngleDegrees = foundBoundary ? minCapSideAngle : -1f,
                smoothSidePass = maxSideAngle <= 1f,
                hardCapSidePass = foundBoundary && minCapSideAngle >= 80f
            };
        }

        private static Bounds CombinedBounds(Renderer[] renderers)
        {
            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Length; index++)
            {
                bounds.Encapsulate(renderers[index].bounds);
            }
            return bounds;
        }

        private static Vector3 ArrayToVector(float[] values) =>
            new(values[0], values[1], values[2]);

        private static float RelativeError(float expected, float actual) =>
            Mathf.Abs(expected - actual)
            / Mathf.Max(Mathf.Abs(expected), Mathf.Abs(actual), 0.000000001f);

        private static void Check(bool condition, string message, List<string> failures)
        {
            if (!condition)
            {
                failures.Add(message);
            }
        }

        private static void EnsureFolder(string path)
        {
            string[] segments = path.Split('/');
            string current = segments[0];
            for (int index = 1; index < segments.Length; index++)
            {
                string next = current + "/" + segments[index];
                if (!AssetDatabase.IsValidFolder(next))
                {
                    AssetDatabase.CreateFolder(current, segments[index]);
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

        private static void SetTexture(Material material, string property, Texture value)
        {
            if (material.HasProperty(property))
            {
                material.SetTexture(property, value);
            }
        }

        private static string Sha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            using SHA256 sha = SHA256.Create();
            byte[] hash = sha.ComputeHash(stream);
            var builder = new StringBuilder(hash.Length * 2);
            foreach (byte value in hash)
            {
                builder.Append(value.ToString("x2"));
            }
            return builder.ToString();
        }

        [Serializable]
        private sealed class CameraRecipeFile
        {
            public int[] resolution;
            public CameraRecipe camera;
            public float[] backgroundLinearRgb;
        }

        [Serializable]
        private sealed class CameraRecipe
        {
            public float[] unityPositionMeters;
            public float[] unityLookAtMeters;
            public float verticalFovDegrees;
            public float nearMeters;
            public float farMeters;
        }

        [Serializable]
        private sealed class UnityParityReport
        {
            public bool pass;
            public string[] failures;
            public string unityVersion;
            public string urpVersion;
            public string productAssetPath;
            public string collisionAssetPath;
            public string parityScenePath;
            public string output;
            public int renderMeshes;
            public int vertices;
            public int triangles;
            public int collisionMeshes;
            public int[] collisionTriangles;
            public BoundsRecord bounds;
            public float[] sortedBoundsMeters;
            public float boundsRelativeError;
            public HierarchyRecord[] hierarchy;
            public bool uv0Valid;
            public bool normalsValid;
            public bool tangentsValid;
            public bool materialSlotsValid;
            public SubmeshRecord[] submeshes;
            public int previewArtworkOverlayMeshes;
            public string previewArtworkOverlayState;
            public bool noAnimationOrSelfMotion;
            public Vector3 closedDefaultPosition;
            public Vector3 closedDefaultRotation;
            public Vector3 pointAxisMeters;
            public Vector3 pointAxisDirection;
            public Vector3 slideDirection;
            public float slideTravelMeters;
            public int detentCount;
            public float detentStepDegrees;
            public string detentDeliveryState;
            public NormalRecord normalMetrics;
            public ImporterRecord importer;
            public TextureRecord[] textures;
            public bool upperLowerArtworkIndependent;
            public CameraRecord camera;
            public ReflectionRecord reflection;
            public string[] materialGaps;
            public string shippingScenePath;
            public string shippingSceneHashBefore;
            public string shippingSceneHashAfter;
            public bool shippingSceneModified;
            public bool shippingIntegrated;
            public bool deviceMemoryMeasured;
            public string deviceAcceptance;
        }

        [Serializable]
        private sealed class BoundsRecord
        {
            public Vector3 center;
            public Vector3 extent;
        }

        [Serializable]
        private sealed class HierarchyRecord
        {
            public string name;
            public string parent;
        }

        [Serializable]
        private sealed class NormalRecord
        {
            public float maxSideDuplicateAngleDegrees;
            public float minimumCapSideAngleDegrees;
            public bool smoothSidePass;
            public bool hardCapSidePass;
        }

        [Serializable]
        private sealed class ImporterRecord
        {
            public float globalScale;
            public bool useFileScale;
            public bool preserveHierarchy;
            public bool importAnimation;
            public string normals;
            public string tangents;
            public string meshCompression;
        }

        [Serializable]
        private sealed class TextureRecord
        {
            public string file;
            public string assetPath;
            public int width;
            public int height;
            public bool mipmaps;
            public bool sRgb;
            public string alphaSource;
            public bool iosOverridden;
            public string iosFormat;
            public int iosMaxSize;
            public long editorRuntimeMemoryBytes;
            public long iosEstimatedTextureBytes;
            public bool deviceMemoryMeasured;
        }

        [Serializable]
        private sealed class SubmeshRecord
        {
            public string mesh;
            public int submesh;
            public string material;
            public int triangles;
            public int capTriangles;
            public int sideTriangles;
            public BoundsRecord bounds;
        }

        [Serializable]
        private sealed class CameraRecord
        {
            public Vector3 position;
            public Vector3 lookAt;
            public float verticalFovDegrees;
            public Vector2Int resolution;
        }

        [Serializable]
        private sealed class ReflectionRecord
        {
            public string strategy;
            public string mode;
            public bool boxProjection;
            public bool realtimeUpdates;
            public string approximation;
        }
    }
}
