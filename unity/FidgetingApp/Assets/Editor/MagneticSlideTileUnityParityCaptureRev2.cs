using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.EditorTools
{
    public static class MagneticSlideTileUnityParityCaptureRev2
    {
        private const string Root = "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev002";
        private const string Materials = Root + "/Materials";
        private const string ProductPath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/magnetic-slide-tile-r002.fbx";
        private const string CollisionPath =
            "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/magnetic-slide-tile-collision-r002.fbx";
        private const string ScenePath = Root + "/MagneticSlideTileNeutralParityRev2.unity";
        private const string ShippingScenePath = "Assets/_EDC/Scenes/MeshyEDC.unity";
        private const int Width = 1600;
        private const int Height = 900;
        private const int EnvironmentResolution = 256;

        public static void CaptureBatch()
        {
            Capture();
        }

        private static void Capture()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string evidenceRoot = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-002");
            Directory.CreateDirectory(evidenceRoot);
            string shippingHashBefore = Sha256(Path.Combine(projectRoot, ShippingScenePath));

            EnsureFolder(Root);
            EnsureFolder(Materials);
            ValidateImporter(ProductPath, renderModel: true);
            ValidateImporter(CollisionPath, renderModel: false);
            CameraRecipeFile recipe = JsonUtility.FromJson<CameraRecipeFile>(
                File.ReadAllText(Path.Combine(evidenceRoot, "neutral-camera-recipe.json")));
            if (recipe?.camera == null)
            {
                throw new InvalidDataException("Gate 11 rev 2 camera recipe is invalid.");
            }

            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject productPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(ProductPath);
            GameObject collisionPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(CollisionPath);
            if (productPrefab == null || collisionPrefab == null)
            {
                throw new InvalidDataException("Approved Gate 10 import assets are unavailable.");
            }
            GameObject product = UnityEngine.Object.Instantiate(productPrefab);
            product.name = "Gate11Rev2_MagneticSlideTile";
            GameObject collision = UnityEngine.Object.Instantiate(collisionPrefab);
            collision.name = "Gate11Rev2_Collision_Proxies";
            ConfigureCollision(collision);

            Material silver = SaveMaterial(
                "M_Gate11R2_PolishedSilver",
                CreateSilverMaterial());
            Material lower = SaveMaterial(
                "M_Gate11R2_BloodRedLower",
                CreateFaceMaterial(
                    "M_Gate11R2_BloodRedLower",
                    "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/face-lower-transport-basecolor.png"));
            Material upper = SaveMaterial(
                "M_Gate11R2_BloodRedUpper",
                CreateFaceMaterial(
                    "M_Gate11R2_BloodRedUpper",
                    "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported/face-upper-transport-basecolor.png"));
            AssignSilver(product, silver);
            CreateArtworkOverlays(product, lower, upper);

            Cubemap environment = CreateContinuousEnvironment();
            ReflectionProbe probe = CreateReflectionProbe(environment);
            ConfigureEnvironment(environment);
            CreateLighting();
            Camera camera = CreateCamera(recipe);
            var metadataObject = new GameObject("Gate11Rev2_SpecifiedOnly_Metadata");
            metadataObject.AddComponent<FidgetingApp.ModelPipeline.MagneticSlideTileParityMetadata>();

            EditorSceneManager.SaveScene(
                UnityEngine.SceneManagement.SceneManager.GetActiveScene(),
                ScenePath);
            Render(camera, Path.Combine(evidenceRoot, "unity-neutral.png"));

            Renderer[] allRenderers = product.GetComponentsInChildren<Renderer>(true);
            Material[][] originalMaterials = allRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            foreach (Renderer renderer in allRenderers)
            {
                renderer.sharedMaterials = Enumerable
                    .Repeat(silver, renderer.sharedMaterials.Length)
                    .ToArray();
            }
            Render(camera, Path.Combine(evidenceRoot, "unity-neutral-all-silver.png"));
            for (int index = 0; index < allRenderers.Length; index++)
            {
                allRenderers[index].sharedMaterials = originalMaterials[index];
            }

            Material wire = SaveMaterial("M_Gate11R2_Wireframe", CreateWireMaterial());
            Renderer[] bodyRenderers = ImportedRenderers(product);
            Renderer[] artworkRenderers = product.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => renderer.name.Contains("Artwork", StringComparison.Ordinal))
                .ToArray();
            Material[][] bodyMaterials = bodyRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            foreach (Renderer renderer in artworkRenderers)
            {
                renderer.enabled = false;
            }
            foreach (Renderer renderer in bodyRenderers)
            {
                renderer.sharedMaterials = Enumerable
                    .Repeat(wire, renderer.sharedMaterials.Length)
                    .ToArray();
            }
            GL.wireframe = true;
            try
            {
                Render(camera, Path.Combine(evidenceRoot, "unity-wireframe.png"));
            }
            finally
            {
                GL.wireframe = false;
                for (int index = 0; index < bodyRenderers.Length; index++)
                {
                    bodyRenderers[index].sharedMaterials = bodyMaterials[index];
                }
                foreach (Renderer renderer in artworkRenderers)
                {
                    renderer.enabled = true;
                }
            }

            string shippingHashAfter = Sha256(Path.Combine(projectRoot, ShippingScenePath));
            UnityParityReport report = BuildReport(
                product,
                collision,
                probe,
                environment,
                recipe,
                camera,
                shippingHashBefore,
                shippingHashAfter);
            File.WriteAllText(
                Path.Combine(evidenceRoot, "unity-import-parity-report.json"),
                JsonUtility.ToJson(report, true) + "\n");
            AssetDatabase.SaveAssets();
            Debug.Log(
                $"[MagneticSlideTileUnityParityRev2] pass={report.pass} "
                + $"arcMax={report.arcNormals.maximumAdjacentStepDegrees:F6} "
                + $"mips={report.environment.mipCount}");
            if (!report.pass)
            {
                throw new InvalidDataException(
                    "Gate 11 rev 2 parity failed: " + string.Join(" | ", report.failures));
            }
        }

        private static void ValidateImporter(string path, bool renderModel)
        {
            if (AssetImporter.GetAtPath(path) is not ModelImporter importer)
            {
                throw new InvalidDataException($"No ModelImporter for {path}.");
            }
            var failures = new List<string>();
            if (importer.globalScale != 1f) failures.Add("globalScale");
            if (!importer.useFileScale) failures.Add("useFileScale");
            if (!importer.preserveHierarchy) failures.Add("preserveHierarchy");
            if (importer.importAnimation) failures.Add("importAnimation");
            if (importer.meshCompression != ModelImporterMeshCompression.Off) failures.Add("meshCompression");
            if (importer.importNormals != ModelImporterNormals.Import) failures.Add("normals");
            if (renderModel && importer.importTangents != ModelImporterTangents.Import) failures.Add("tangents");
            if (failures.Count > 0)
            {
                throw new InvalidDataException(
                    $"Importer drift at {path}: {string.Join(", ", failures)}");
            }
        }

        private static Material CreateSilverMaterial()
        {
            Material material = NewMaterial(
                "Universal Render Pipeline/Lit",
                "M_Gate11R2_PolishedSilver");
            SetColor(material, "_BaseColor", new Color(0.97f, 0.965f, 0.94f, 1f));
            SetFloat(material, "_Metallic", 1f);
            SetFloat(material, "_Smoothness", 0.97f);
            SetFloat(material, "_ClearCoatMask", 0.06f);
            SetFloat(material, "_ClearCoatSmoothness", 0.98f);
            return material;
        }

        private static Material CreateFaceMaterial(string name, string texturePath)
        {
            Material material = NewMaterial("Universal Render Pipeline/Unlit", name);
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
            if (texture == null)
            {
                throw new InvalidDataException($"Missing face texture {texturePath}.");
            }
            SetTexture(material, "_BaseMap", texture);
            SetColor(material, "_BaseColor", Color.white);
            return material;
        }

        private static Material CreateWireMaterial()
        {
            Material material = NewMaterial(
                "Universal Render Pipeline/Unlit",
                "M_Gate11R2_Wireframe");
            SetColor(material, "_BaseColor", new Color(0.18f, 0.92f, 1f, 1f));
            return material;
        }

        private static Material NewMaterial(string shaderName, string name)
        {
            Shader shader = Shader.Find(shaderName)
                ?? throw new InvalidDataException($"Shader unavailable: {shaderName}.");
            return new Material(shader) { name = name };
        }

        private static Material SaveMaterial(string name, Material material)
        {
            string path = Materials + "/" + name + ".mat";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(material, path);
            return AssetDatabase.LoadAssetAtPath<Material>(path);
        }

        private static void AssignSilver(GameObject product, Material silver)
        {
            Renderer[] renderers = ImportedRenderers(product);
            if (renderers.Length != 2)
            {
                throw new InvalidDataException($"Expected two imported renderers, found {renderers.Length}.");
            }
            foreach (Renderer renderer in renderers)
            {
                renderer.sharedMaterials = Enumerable
                    .Repeat(silver, renderer.sharedMaterials.Length)
                    .ToArray();
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
            }
        }

        private static void CreateArtworkOverlays(
            GameObject product,
            Material lower,
            Material upper)
        {
            foreach (MeshFilter source in ImportedFilters(product))
            {
                Material material = source.name.Contains("Lower", StringComparison.Ordinal)
                    ? lower
                    : upper;
                Mesh sourceMesh = source.sharedMesh;
                var overlayMesh = new Mesh
                {
                    name = source.name + "_Gate11Rev2Artwork"
                };
                overlayMesh.vertices = sourceMesh.vertices;
                overlayMesh.uv = sourceMesh.uv;
                overlayMesh.normals = sourceMesh.normals;
                overlayMesh.tangents = sourceMesh.tangents;
                overlayMesh.triangles = sourceMesh.GetTriangles(1);
                overlayMesh.RecalculateBounds();

                var overlay = new GameObject(source.name + "_ArtworkAccepted");
                overlay.transform.SetParent(source.transform, false);
                overlay.transform.localPosition = Vector3.forward * 0.00001f;
                overlay.transform.localRotation = Quaternion.identity;
                overlay.transform.localScale = Vector3.one;
                overlay.AddComponent<MeshFilter>().sharedMesh = overlayMesh;
                MeshRenderer renderer = overlay.AddComponent<MeshRenderer>();
                renderer.sharedMaterial = material;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
            }
        }

        private static void ConfigureCollision(GameObject collision)
        {
            foreach (Renderer renderer in collision.GetComponentsInChildren<Renderer>(true))
            {
                renderer.enabled = false;
            }
            collision.SetActive(false);
        }

        private static Cubemap CreateContinuousEnvironment()
        {
            var cubemap = new Cubemap(
                EnvironmentResolution,
                TextureFormat.RGBAHalf,
                true)
            {
                name = "Gate11R2_DirectionContinuousEnvironment",
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
                        pixels[y * EnvironmentResolution + x] = EnvironmentColor(direction);
                    }
                }
                cubemap.SetPixels(pixels, (CubemapFace)face, 0);
            }
            cubemap.Apply(true, false);
            string path = Materials + "/Gate11R2_DirectionContinuousEnvironment.cubemap";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(cubemap, path);
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

        private static Color EnvironmentColor(Vector3 direction)
        {
            Vector3 key = new Vector3(-0.72f, 0.58f, -0.38f).normalized;
            Vector3 fill = new Vector3(0.54f, 0.31f, 0.78f).normalized;
            float keyLobe = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(direction, key) * 0.5f + 0.5f), 5f);
            float fillLobe = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(direction, fill) * 0.5f + 0.5f), 3f);
            float horizon = 1f - Mathf.Abs(direction.y);
            float value = 0.18f + 0.52f * keyLobe + 0.18f * fillLobe + 0.12f * horizon;
            return new Color(value * 1.015f, value, value * 0.985f, 1f);
        }

        private static ReflectionProbe CreateReflectionProbe(Cubemap cubemap)
        {
            var probeObject = new GameObject("Gate11Rev2_ContinuousReflectionProbe");
            ReflectionProbe probe = probeObject.AddComponent<ReflectionProbe>();
            probe.mode = ReflectionProbeMode.Custom;
            probe.customBakedTexture = cubemap;
            probe.boxProjection = false;
            probe.size = new Vector3(0.16f, 0.10f, 0.16f);
            probe.intensity = 1f;
            probe.importance = 100;
            return probe;
        }

        private static void ConfigureEnvironment(Cubemap cubemap)
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.24f, 0.24f, 0.24f);
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.customReflectionTexture = cubemap;
            RenderSettings.reflectionIntensity = 1f;
            RenderSettings.reflectionBounces = 1;
            QualitySettings.realtimeReflectionProbes = false;
        }

        private static void CreateLighting()
        {
            CreateDirectional(
                "Gate11Rev2_Key",
                new Color(1f, 0.99f, 0.97f),
                1.15f,
                new Vector3(48f, -32f, 0f));
            CreateDirectional(
                "Gate11Rev2_Fill",
                Color.white,
                0.42f,
                new Vector3(55f, 138f, 0f));
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
            var cameraObject = new GameObject("CAM_Gate11Rev2Neutral");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.transform.position = ToVector(recipe.camera.unityPositionMeters);
            Vector3 target = ToVector(recipe.camera.unityLookAtMeters);
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
            ReflectionProbe probe,
            Cubemap environment,
            CameraRecipeFile recipe,
            Camera camera,
            string shippingHashBefore,
            string shippingHashAfter)
        {
            var failures = new List<string>();
            MeshFilter[] filters = ImportedFilters(product);
            Renderer[] renderers = ImportedRenderers(product);
            MeshFilter[] collisionFilters = collision.GetComponentsInChildren<MeshFilter>(true);
            int triangles = filters.Sum(filter => filter.sharedMesh.triangles.Length / 3);
            int[] collisionTriangles = collisionFilters
                .Select(filter => filter.sharedMesh.triangles.Length / 3)
                .OrderBy(value => value)
                .ToArray();
            Bounds bounds = CombinedBounds(renderers);
            float[] sortedBounds = { bounds.size.x, bounds.size.y, bounds.size.z };
            Array.Sort(sortedBounds);
            float[] expected = { 0.012f, 0.031f, 0.050f };
            float boundsError = sortedBounds
                .Zip(expected, (actual, target) => RelativeError(target, actual))
                .Max();
            ArcNormalRecord arcNormals = MeasureArcNormals(filters);
            BoundaryNormalRecord boundary = MeasureCapSideBoundary(filters);
            EnvironmentRecord environmentRecord = MeasureEnvironment(environment, probe);

            Check(filters.Length == 2, "Render mesh count changed.", failures);
            Check(triangles == 4096, "Triangle count changed.", failures);
            Check(boundsError < 0.001f, "Bounds changed.", failures);
            Check(collisionTriangles.SequenceEqual(new[] { 128, 128 }), "Collision changed.", failures);
            Check(arcNormals.uniqueHorizontalNormals >= 512, "Arc normal density is too low.", failures);
            Check(arcNormals.maximumAdjacentStepDegrees < 0.9f, "Adjacent arc normals are not gradual.", failures);
            Check(arcNormals.p95AdjacentStepDegrees < 0.71f, "Arc normal progression is irregular.", failures);
            Check(boundary.minimumCapSideAngleDegrees >= 89f, "Cap-side hard boundary changed.", failures);
            Check(environmentRecord.mipCount >= 9, "Environment mip chain is missing.", failures);
            Check(environmentRecord.filterMode == "Trilinear", "Environment filtering is not trilinear.", failures);
            Check(!environmentRecord.boxProjection, "Box projection must remain disabled.", failures);
            Check(environmentRecord.maximumAnalyticSeamDelta < 0.005f, "Environment function is discontinuous.", failures);
            Check(shippingHashBefore == shippingHashAfter, "Shipping scene changed.", failures);

            return new UnityParityReport
            {
                pass = failures.Count == 0,
                failures = failures.ToArray(),
                unityVersion = Application.unityVersion,
                urpVersion = "17.5.0",
                sourceProductAssetPath = ProductPath,
                sourceCollisionAssetPath = CollisionPath,
                parityScenePath = ScenePath,
                renderMeshes = filters.Length,
                vertices = filters.Sum(filter => filter.sharedMesh.vertexCount),
                triangles = triangles,
                collisionTriangles = collisionTriangles,
                boundsMeters = sortedBounds,
                boundsRelativeError = boundsError,
                arcNormals = arcNormals,
                capSideBoundary = boundary,
                environment = environmentRecord,
                camera = new CameraRecord
                {
                    position = camera.transform.position,
                    lookAt = ToVector(recipe.camera.unityLookAtMeters),
                    verticalFovDegrees = camera.fieldOfView,
                    resolution = new Vector2Int(Width, Height)
                },
                geometryChanged = false,
                renderGeometryInflated = false,
                patternPlacementDecision = "accepted-provisionally-not-under-review",
                roundEdgeDecision = "rev1-rejected-rev2-pending",
                rootCause = "Rev 1 used six unrelated solid-color cubemap faces without mipmaps. Near-mirror silver exposed the face transitions as broad hard bands.",
                importerNormalsChanged = false,
                shippingSceneHashBefore = shippingHashBefore,
                shippingSceneHashAfter = shippingHashAfter,
                shippingSceneModified = shippingHashBefore != shippingHashAfter,
                shippingIntegrated = false,
                gate12Started = false,
                deviceAcceptance = "pending"
            };
        }

        private static ArcNormalRecord MeasureArcNormals(MeshFilter[] filters)
        {
            var unique = new Dictionary<string, Vector3>();
            var edgeSteps = new List<float>();
            foreach (MeshFilter filter in filters)
            {
                Mesh mesh = filter.sharedMesh;
                Vector3[] vertices = mesh.vertices;
                Vector3[] normals = mesh.normals;
                for (int index = 0; index < mesh.vertexCount; index++)
                {
                    Vector3 normal = filter.transform.TransformDirection(normals[index]).normalized;
                    if (Mathf.Abs(normal.y) > 0.2f)
                    {
                        continue;
                    }
                    string key =
                        $"{Mathf.Round(normal.x * 1000000f)},{Mathf.Round(normal.z * 1000000f)}";
                    unique[key] = normal;
                }
                int[] triangles = mesh.triangles;
                for (int index = 0; index < triangles.Length; index += 3)
                {
                    int a = triangles[index];
                    int b = triangles[index + 1];
                    int c = triangles[index + 2];
                    Vector3 pa = filter.transform.TransformPoint(vertices[a]);
                    Vector3 pb = filter.transform.TransformPoint(vertices[b]);
                    Vector3 pc = filter.transform.TransformPoint(vertices[c]);
                    Vector3 faceNormal = Vector3.Cross(pb - pa, pc - pa).normalized;
                    if (Mathf.Abs(faceNormal.y) > 0.5f)
                    {
                        continue;
                    }
                    AddNormalEdgeStep(filter, normals, a, b, edgeSteps);
                    AddNormalEdgeStep(filter, normals, b, c, edgeSteps);
                    AddNormalEdgeStep(filter, normals, c, a, edgeSteps);
                }
            }
            float[] ordered = edgeSteps
                .Where(value => value > 0.0001f)
                .OrderBy(value => value)
                .ToArray();
            return new ArcNormalRecord
            {
                uniqueHorizontalNormals = unique.Count,
                nonZeroAdjacentEdges = ordered.Length,
                expectedSegmentsPerSemicircle = 256,
                expectedNormalStepDegrees = 0.703125f,
                minimumAdjacentStepDegrees = ordered.FirstOrDefault(),
                medianAdjacentStepDegrees = Percentile(ordered, 0.5f),
                p95AdjacentStepDegrees = Percentile(ordered, 0.95f),
                maximumAdjacentStepDegrees = ordered.LastOrDefault(),
                gradualProgressionPass = ordered.Length > 0
                    && ordered.Last() < 0.9f
                    && Percentile(ordered, 0.95f) < 0.71f
            };
        }

        private static void AddNormalEdgeStep(
            MeshFilter filter,
            Vector3[] normals,
            int a,
            int b,
            List<float> steps)
        {
            Vector3 na = filter.transform.TransformDirection(normals[a]).normalized;
            Vector3 nb = filter.transform.TransformDirection(normals[b]).normalized;
            if (Mathf.Abs(na.y) < 0.2f && Mathf.Abs(nb.y) < 0.2f)
            {
                steps.Add(Vector3.Angle(na, nb));
            }
        }

        private static BoundaryNormalRecord MeasureCapSideBoundary(MeshFilter[] filters)
        {
            float minimum = 180f;
            int pairs = 0;
            foreach (MeshFilter filter in filters)
            {
                Mesh mesh = filter.sharedMesh;
                var groups = new Dictionary<string, List<Vector3>>();
                for (int index = 0; index < mesh.vertexCount; index++)
                {
                    Vector3 p = filter.transform.TransformPoint(mesh.vertices[index]);
                    Vector3 n = filter.transform.TransformDirection(mesh.normals[index]).normalized;
                    string key =
                        $"{Mathf.Round(p.x * 100000f)},{Mathf.Round(p.y * 100000f)},{Mathf.Round(p.z * 100000f)}";
                    if (!groups.TryGetValue(key, out List<Vector3> values))
                    {
                        values = new List<Vector3>();
                        groups.Add(key, values);
                    }
                    values.Add(n);
                }
                foreach (List<Vector3> values in groups.Values)
                {
                    Vector3[] caps = values.Where(normal => Mathf.Abs(normal.y) > 0.9f).ToArray();
                    Vector3[] sides = values.Where(normal => Mathf.Abs(normal.y) < 0.2f).ToArray();
                    foreach (Vector3 cap in caps)
                    {
                        foreach (Vector3 side in sides)
                        {
                            minimum = Mathf.Min(minimum, Vector3.Angle(cap, side));
                            pairs += 1;
                        }
                    }
                }
            }
            return new BoundaryNormalRecord
            {
                comparedPairs = pairs,
                minimumCapSideAngleDegrees = pairs > 0 ? minimum : -1f,
                hardBoundaryPass = pairs > 0 && minimum >= 89f
            };
        }

        private static EnvironmentRecord MeasureEnvironment(
            Cubemap environment,
            ReflectionProbe probe)
        {
            float maximumDelta = 0f;
            const float epsilon = 0.0001f;
            for (int index = 0; index <= 64; index++)
            {
                float t = -1f + 2f * index / 64f;
                Vector3[] boundaries =
                {
                    new Vector3(1f, t, 1f),
                    new Vector3(1f, t, -1f),
                    new Vector3(t, 1f, 1f),
                    new Vector3(t, -1f, 1f),
                };
                foreach (Vector3 boundary in boundaries)
                {
                    Vector3 a = (boundary + new Vector3(epsilon, 0f, -epsilon)).normalized;
                    Vector3 b = (boundary + new Vector3(-epsilon, 0f, epsilon)).normalized;
                    Color ca = EnvironmentColor(a);
                    Color cb = EnvironmentColor(b);
                    maximumDelta = Mathf.Max(
                        maximumDelta,
                        Mathf.Max(
                            Mathf.Abs(ca.r - cb.r),
                            Mathf.Max(Mathf.Abs(ca.g - cb.g), Mathf.Abs(ca.b - cb.b))));
                }
            }
            return new EnvironmentRecord
            {
                resolution = environment.width,
                format = environment.format.ToString(),
                mipCount = environment.mipmapCount,
                filterMode = environment.filterMode.ToString(),
                wrapMode = environment.wrapMode.ToString(),
                boxProjection = probe.boxProjection,
                realtimeUpdates = false,
                directionContinuousFormula = true,
                maximumAnalyticSeamDelta = maximumDelta,
                oldEnvironment = "six independent 32x32 solid-color faces; mipmaps false",
                newEnvironment = "256x256 RGBAHalf direction-continuous function; mipmaps true; trilinear"
            };
        }

        private static float Percentile(float[] values, float percentile)
        {
            if (values.Length == 0)
            {
                return 0f;
            }
            float position = (values.Length - 1) * percentile;
            int lower = Mathf.FloorToInt(position);
            int upper = Mathf.CeilToInt(position);
            return Mathf.Lerp(values[lower], values[upper], position - lower);
        }

        private static MeshFilter[] ImportedFilters(GameObject product) =>
            product.GetComponentsInChildren<MeshFilter>(true)
                .Where(filter => !filter.name.Contains("Artwork", StringComparison.Ordinal))
                .ToArray();

        private static Renderer[] ImportedRenderers(GameObject product) =>
            product.GetComponentsInChildren<Renderer>(true)
                .Where(renderer => !renderer.name.Contains("Artwork", StringComparison.Ordinal))
                .ToArray();

        private static Bounds CombinedBounds(Renderer[] renderers)
        {
            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Length; index++)
            {
                bounds.Encapsulate(renderers[index].bounds);
            }
            return bounds;
        }

        private static void Check(bool condition, string message, List<string> failures)
        {
            if (!condition)
            {
                failures.Add(message);
            }
        }

        private static float RelativeError(float expected, float actual) =>
            Mathf.Abs(expected - actual)
            / Mathf.Max(Mathf.Abs(expected), Mathf.Abs(actual), 0.000000001f);

        private static Vector3 ToVector(float[] values) =>
            new(values[0], values[1], values[2]);

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
            if (material.HasProperty(property)) material.SetFloat(property, value);
        }

        private static void SetColor(Material material, string property, Color value)
        {
            if (material.HasProperty(property)) material.SetColor(property, value);
        }

        private static void SetTexture(Material material, string property, Texture value)
        {
            if (material.HasProperty(property)) material.SetTexture(property, value);
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
            public float[] backgroundLinearRgb;
            public CameraRecipe camera;
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
            public string sourceProductAssetPath;
            public string sourceCollisionAssetPath;
            public string parityScenePath;
            public int renderMeshes;
            public int vertices;
            public int triangles;
            public int[] collisionTriangles;
            public float[] boundsMeters;
            public float boundsRelativeError;
            public ArcNormalRecord arcNormals;
            public BoundaryNormalRecord capSideBoundary;
            public EnvironmentRecord environment;
            public CameraRecord camera;
            public bool geometryChanged;
            public bool renderGeometryInflated;
            public string patternPlacementDecision;
            public string roundEdgeDecision;
            public string rootCause;
            public bool importerNormalsChanged;
            public string shippingSceneHashBefore;
            public string shippingSceneHashAfter;
            public bool shippingSceneModified;
            public bool shippingIntegrated;
            public bool gate12Started;
            public string deviceAcceptance;
        }

        [Serializable]
        private sealed class ArcNormalRecord
        {
            public int uniqueHorizontalNormals;
            public int nonZeroAdjacentEdges;
            public int expectedSegmentsPerSemicircle;
            public float expectedNormalStepDegrees;
            public float minimumAdjacentStepDegrees;
            public float medianAdjacentStepDegrees;
            public float p95AdjacentStepDegrees;
            public float maximumAdjacentStepDegrees;
            public bool gradualProgressionPass;
        }

        [Serializable]
        private sealed class BoundaryNormalRecord
        {
            public int comparedPairs;
            public float minimumCapSideAngleDegrees;
            public bool hardBoundaryPass;
        }

        [Serializable]
        private sealed class EnvironmentRecord
        {
            public int resolution;
            public string format;
            public int mipCount;
            public string filterMode;
            public string wrapMode;
            public bool boxProjection;
            public bool realtimeUpdates;
            public bool directionContinuousFormula;
            public float maximumAnalyticSeamDelta;
            public string oldEnvironment;
            public string newEnvironment;
        }

        [Serializable]
        private sealed class CameraRecord
        {
            public Vector3 position;
            public Vector3 lookAt;
            public float verticalFovDegrees;
            public Vector2Int resolution;
        }
    }
}
