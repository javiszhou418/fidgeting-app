using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EditorTools
{
    public static class FanCardUnityParityCapture
    {
        private const string GeneratedFolder =
            "Assets/Editor/GeneratedModelParity/MagneticFanCard";
        private const string ProductAssetPath =
            GeneratedFolder + "/magnetic-fan-card.fbx";
        private const string CollisionAssetPath =
            GeneratedFolder + "/magnetic-fan-card-collision.fbx";
        private const int Width = 1179;
        private const int Height = 654;
        private static readonly string[] CardNames =
        {
            "BottomCard",
            "MiddleCard",
            "TopCard"
        };

        [MenuItem("Tools/Codex/Fan Card/Capture Unity Import Parity")]
        public static void CaptureMenu()
        {
            Capture();
        }

        public static void CaptureBatch()
        {
            Capture();
        }

        private static void Capture()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)!.FullName;
            string exportFolder = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-fan-card/evidence/10-export/rev-003");
            string evidenceFolder = Path.Combine(
                projectRoot,
                "ArtSource/ModelPipeline/magnetic-fan-card/evidence/11-unity-parity/rev-003");
            Directory.CreateDirectory(evidenceFolder);
            ImportModel(
                Path.Combine(exportFolder, "magnetic-fan-card.fbx"),
                ProductAssetPath);
            ImportModel(
                Path.Combine(exportFolder, "magnetic-fan-card-collision.fbx"),
                CollisionAssetPath);

            NeutralCameraRecipe recipe = JsonUtility.FromJson<NeutralCameraRecipe>(
                File.ReadAllText(
                    Path.Combine(evidenceFolder, "neutral-camera-recipe.json")));
            if (recipe == null || recipe.camera == null)
            {
                throw new InvalidDataException("Neutral camera recipe is invalid.");
            }

            EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
            GameObject productPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                ProductAssetPath);
            GameObject collisionPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                CollisionAssetPath);
            if (productPrefab == null || collisionPrefab == null)
            {
                throw new InvalidDataException("Unity did not import the parity FBX assets.");
            }

            GameObject product = UnityEngine.Object.Instantiate(productPrefab);
            product.name = "Parity_Product";
            GameObject collision = UnityEngine.Object.Instantiate(collisionPrefab);
            collision.name = "Parity_Collision";
            collision.SetActive(false);

            Material neutral = CreateNeutralMaterial();
            Renderer[] renderers = product.GetComponentsInChildren<Renderer>(true);
            foreach (Renderer renderer in renderers)
            {
                renderer.sharedMaterial = neutral;
                renderer.shadowCastingMode = ShadowCastingMode.Off;
                renderer.receiveShadows = false;
            }

            Camera camera = CreateCamera(recipe);
            CreateLighting();
            string outputPath = Path.Combine(evidenceFolder, "unity-neutral.png");
            Render(camera, outputPath);

            ParityReport report = BuildReport(
                product,
                collision,
                renderers,
                recipe,
                camera,
                outputPath);
            string reportPath = Path.Combine(
                evidenceFolder,
                "unity-neutral-report.json");
            File.WriteAllText(reportPath, JsonUtility.ToJson(report, true) + "\n");
            Debug.Log(
                $"[FanCardUnityParity] pass={report.pass} "
                + $"tris={report.triangles} boundsError={report.boundsRelativeError:F8} "
                + $"output={outputPath}");
            if (!report.pass)
            {
                throw new InvalidDataException(
                    "Fan-card Unity import parity failed. See unity-neutral-report.json.");
            }

            UnityEngine.Object.DestroyImmediate(neutral);
        }

        private static void ImportModel(string sourcePath, string assetPath)
        {
            if (!File.Exists(sourcePath))
            {
                throw new FileNotFoundException("Parity source is missing.", sourcePath);
            }
            string absoluteAssetPath = Path.Combine(
                Directory.GetParent(Application.dataPath)!.FullName,
                assetPath);
            Directory.CreateDirectory(Path.GetDirectoryName(absoluteAssetPath)!);
            File.Copy(sourcePath, absoluteAssetPath, true);
            AssetDatabase.ImportAsset(
                assetPath,
                ImportAssetOptions.ForceSynchronousImport
                    | ImportAssetOptions.ForceUpdate);
            ModelImporter importer = AssetImporter.GetAtPath(assetPath) as ModelImporter;
            if (importer == null)
            {
                throw new InvalidDataException($"No ModelImporter for {assetPath}.");
            }
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.importBlendShapes = false;
            importer.preserveHierarchy = true;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.isReadable = true;
            importer.optimizeMeshPolygons = false;
            importer.optimizeMeshVertices = false;
            importer.SaveAndReimport();
        }

        private static Material CreateNeutralMaterial()
        {
            Shader shader =
                Shader.Find("Universal Render Pipeline/Lit")
                ?? Shader.Find("Standard");
            if (shader == null)
            {
                throw new InvalidDataException("No neutral lit shader is available.");
            }
            var material = new Material(shader)
            {
                name = "M_UnityParityNeutral",
                color = new Color(0.60f, 0.57f, 0.51f, 1f)
            };
            if (material.HasProperty("_BaseColor"))
            {
                material.SetColor("_BaseColor", material.color);
            }
            if (material.HasProperty("_Metallic"))
            {
                material.SetFloat("_Metallic", 0.05f);
            }
            if (material.HasProperty("_Smoothness"))
            {
                material.SetFloat("_Smoothness", 0.34f);
            }
            return material;
        }

        private static Camera CreateCamera(NeutralCameraRecipe recipe)
        {
            var cameraObject = new GameObject("CAM_UnityParity");
            Camera camera = cameraObject.AddComponent<Camera>();
            Vector3 position = FromBlender(recipe.camera.position);
            Vector3 target = FromBlender(recipe.camera.lookAt);
            camera.transform.position = position;
            camera.transform.rotation = Quaternion.LookRotation(
                target - position,
                Vector3.up);
            camera.fieldOfView = recipe.camera.verticalFovDegrees;
            camera.nearClipPlane = recipe.camera.nearClip;
            camera.farClipPlane = recipe.camera.farClip;
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

        private static void CreateLighting()
        {
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.24f, 0.23f, 0.22f);
            var keyObject = new GameObject("LGT_UnityParityKey");
            Light key = keyObject.AddComponent<Light>();
            key.type = LightType.Directional;
            key.color = new Color(1f, 0.93f, 0.84f);
            key.intensity = 1.35f;
            key.shadows = LightShadows.None;
            keyObject.transform.rotation = Quaternion.Euler(48f, -32f, 0f);
        }

        private static void Render(Camera camera, string outputPath)
        {
            RenderTexture previousTarget = camera.targetTexture;
            RenderTexture previousActive = RenderTexture.active;
            float previousAspect = camera.aspect;
            var target = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32);
            var image = new Texture2D(
                Width,
                Height,
                TextureFormat.RGBA32,
                false,
                false);
            try
            {
                if (!target.Create())
                {
                    throw new InvalidDataException(
                        "Unity could not create the parity render target.");
                }
                camera.aspect = (float)Width / Height;
                camera.targetTexture = target;
                var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
                {
                    destination = target
                };
                UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(
                    camera,
                    request);
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0f, 0f, Width, Height), 0, 0);
                image.Apply(false, false);
                File.WriteAllBytes(outputPath, image.EncodeToPNG());
            }
            finally
            {
                camera.aspect = previousAspect;
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                UnityEngine.Object.DestroyImmediate(image);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private static ParityReport BuildReport(
            GameObject product,
            GameObject collision,
            Renderer[] renderers,
            NeutralCameraRecipe recipe,
            Camera camera,
            string outputPath)
        {
            Transform modelRoot = FindDeep(product.transform, "MagneticFanCard_Root");
            var failures = new List<string>();
            if (modelRoot == null)
            {
                failures.Add("MagneticFanCard_Root is missing.");
            }

            var hierarchy = new List<HierarchyRecord>();
            foreach (string cardName in CardNames)
            {
                Transform card = modelRoot == null
                    ? null
                    : FindDeep(modelRoot, cardName);
                hierarchy.Add(new HierarchyRecord
                {
                    name = cardName,
                    parent = card?.parent?.name
                });
                if (card == null || card.parent != modelRoot)
                {
                    failures.Add($"{cardName} is not parented to MagneticFanCard_Root.");
                }
            }

            MeshFilter[] filters = product.GetComponentsInChildren<MeshFilter>(true);
            int triangles = filters
                .Where(filter => filter.sharedMesh != null)
                .Sum(filter => filter.sharedMesh.triangles.Length / 3);
            int vertices = filters
                .Where(filter => filter.sharedMesh != null)
                .Sum(filter => filter.sharedMesh.vertexCount);
            if (triangles != 70530)
            {
                failures.Add($"Triangle count changed to {triangles}.");
            }

            int rankMeshes = filters.Count(filter =>
                filter.name.Contains("_Rank_")
                && filter.sharedMesh != null);
            if (rankMeshes != 6)
            {
                failures.Add($"Expected 6 rank meshes, found {rankMeshes}.");
            }
            int bottomTracks = filters.Count(filter =>
                filter.name.StartsWith("BottomCard_Track_", StringComparison.Ordinal));
            int middleTopTracks = filters.Count(filter =>
                filter.name.StartsWith("MiddleCard_Track_", StringComparison.Ordinal)
                || filter.name.StartsWith("TopCard_Track_", StringComparison.Ordinal));
            if (bottomTracks != 0 || middleTopTracks != 4)
            {
                failures.Add(
                    $"Track distribution changed: bottom={bottomTracks}, "
                    + $"middle/top={middleTopTracks}.");
            }

            Bounds productBounds = CombinedBounds(renderers);
            float[] expected = recipe.sourceBounds.extent
                .OrderBy(value => value)
                .ToArray();
            float[] actual =
            {
                productBounds.size.x,
                productBounds.size.y,
                productBounds.size.z
            };
            Array.Sort(actual);
            float boundsError = expected.Zip(
                    actual,
                    (reference, imported) => RelativeError(reference, imported))
                .Max();
            if (boundsError > 0.01f)
            {
                failures.Add($"Imported bounds differ by {boundsError:P4}.");
            }

            MeshFilter[] collisionFilters =
                collision.GetComponentsInChildren<MeshFilter>(true);
            if (collisionFilters.Length != 3)
            {
                failures.Add(
                    $"Expected 3 collision meshes, found {collisionFilters.Length}.");
            }
            foreach (string cardName in CardNames)
            {
                Transform collider = FindDeep(
                    collision.transform,
                    $"COLLIDER_{cardName}");
                if (collider == null || collider.parent?.name != cardName)
                {
                    failures.Add(
                        $"COLLIDER_{cardName} is missing or has the wrong parent.");
                }
            }

            return new ParityReport
            {
                pass = failures.Count == 0,
                failures = failures.ToArray(),
                productAssetPath = ProductAssetPath,
                collisionAssetPath = CollisionAssetPath,
                unityVersion = Application.unityVersion,
                output = outputPath,
                meshObjects = filters.Length,
                vertices = vertices,
                triangles = triangles,
                rankMeshes = rankMeshes,
                bottomTrackObjects = bottomTracks,
                middleTopTrackObjects = middleTopTracks,
                collisionMeshes = collisionFilters.Length,
                bounds = new BoundsRecord
                {
                    center = productBounds.center,
                    extent = productBounds.size
                },
                sourceBoundsExtent = new Vector3(
                    recipe.sourceBounds.extent[0],
                    recipe.sourceBounds.extent[2],
                    recipe.sourceBounds.extent[1]),
                boundsRelativeError = boundsError,
                hierarchy = hierarchy.ToArray(),
                camera = new CameraRecord
                {
                    position = camera.transform.position,
                    lookAt = FromBlender(recipe.camera.lookAt),
                    verticalFovDegrees = camera.fieldOfView,
                    resolution = new Vector2Int(Width, Height)
                },
                importer = new ImporterRecord
                {
                    globalScale = 1f,
                    useFileScale = true,
                    normals = "Import",
                    tangents = "CalculateMikk",
                    materials = "None",
                    optimizeMesh = false
                },
                shippingIntegrated = false
            };
        }

        private static Bounds CombinedBounds(Renderer[] renderers)
        {
            if (renderers.Length == 0)
            {
                throw new InvalidDataException("Imported model has no renderers.");
            }
            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Length; index++)
            {
                bounds.Encapsulate(renderers[index].bounds);
            }
            return bounds;
        }

        private static Transform FindDeep(Transform root, string name)
        {
            return root.GetComponentsInChildren<Transform>(true)
                .FirstOrDefault(candidate => candidate.name == name);
        }

        private static Vector3 FromBlender(float[] value)
        {
            return new Vector3(-value[0], value[2], -value[1]);
        }

        private static float RelativeError(float expected, float actual)
        {
            return Mathf.Abs(expected - actual)
                / Mathf.Max(Mathf.Abs(expected), Mathf.Abs(actual), 0.000000001f);
        }

        [Serializable]
        private sealed class NeutralCameraRecipe
        {
            public int[] resolution;
            public CameraRecipe camera;
            public float[] backgroundLinearRgb;
            public BoundsRecipe sourceBounds;
        }

        [Serializable]
        private sealed class CameraRecipe
        {
            public float[] position;
            public float[] lookAt;
            public float verticalFovDegrees;
            public float nearClip;
            public float farClip;
        }

        [Serializable]
        private sealed class BoundsRecipe
        {
            public float[] extent;
        }

        [Serializable]
        private sealed class ParityReport
        {
            public bool pass;
            public string[] failures;
            public string productAssetPath;
            public string collisionAssetPath;
            public string unityVersion;
            public string output;
            public int meshObjects;
            public int vertices;
            public int triangles;
            public int rankMeshes;
            public int bottomTrackObjects;
            public int middleTopTrackObjects;
            public int collisionMeshes;
            public BoundsRecord bounds;
            public Vector3 sourceBoundsExtent;
            public float boundsRelativeError;
            public HierarchyRecord[] hierarchy;
            public CameraRecord camera;
            public ImporterRecord importer;
            public bool shippingIntegrated;
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
        private sealed class CameraRecord
        {
            public Vector3 position;
            public Vector3 lookAt;
            public float verticalFovDegrees;
            public Vector2Int resolution;
        }

        [Serializable]
        private sealed class ImporterRecord
        {
            public float globalScale;
            public bool useFileScale;
            public string normals;
            public string tangents;
            public string materials;
            public bool optimizeMesh;
        }
    }
}
