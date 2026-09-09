using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FidgetingApp.EDC.EditorTools
{
    public static class EdcImportPipeline
    {
        public const string SourceFolder = "Assets/_EDC/Source";
        public const string ModelPath =
            SourceFolder + "/Meshy_AI_Futuristic_Top_View_C_0804153834_texture.fbx";
        public const string BaseMapPath =
            SourceFolder + "/Meshy_AI_Futuristic_Top_View_C_0804153834_texture.png";
        public const string EmissionMapPath =
            SourceFolder + "/Meshy_AI_Futuristic_Top_View_C_0804153834_texture_emission.png";
        public const string MetallicMapPath =
            SourceFolder + "/Meshy_AI_Futuristic_Top_View_C_0804153834_texture_metallic.png";
        public const string NormalMapPath =
            SourceFolder + "/Meshy_AI_Futuristic_Top_View_C_0804153834_texture_normal.png";
        public const string RoughnessMapPath =
            SourceFolder + "/Meshy_AI_Futuristic_Top_View_C_0804153834_texture_roughness.png";

        public const string GeneratedFolder = "Assets/_EDC/Generated";
        public const string PackedMaskPath =
            GeneratedFolder + "/Textures/T_EDC_MetallicSmoothness.png";
        public const string MaterialPath =
            GeneratedFolder + "/Materials/M_EDC_Meshy_URP_Lit.mat";
        public const string ImportReportPath =
            "Assets/_EDC/Reports/import-audit.txt";
        public const string ComponentReportPath =
            "Assets/_EDC/Reports/connected-components.txt";
        public const string HeightProfilePath =
            "Assets/_EDC/Reports/height-profile.csv";

        public const float TargetLongestDimensionMeters = 0.08f;
        public const float SilverRoughnessInfluence = 0.58f;
        public const float SilverNormalScale = 0.28f;
        public const float SilverGlossMapScale = 0.68f;
        public const float SilverRealtimeSpecular = 1f;
        public const float SilverTintRed = 0.66f;
        public const float SilverTintGreen = 0.70f;
        public const float SilverTintBlue = 0.72f;
        public const int PolishedTextureCompressionQuality = 100;
        private const float PositionWeldToleranceMeters = 0.000001f;
        private const int PreviewWidth = 1200;
        private const int PreviewHeight = 800;
        private const int HeightProfileBins = 256;
        private const string ManualLayerSourceFolder = "/tmp/fidgeting_edc_manual_layers";
        private const float TopFrameMinimumY = 0.0064f;
        private const float UpperShellMinimumY = 0.0010f;
        private const float GasketMinimumY = 0.0000f;
        private const float InnerFrameMinimumY = -0.0030f;

        [MenuItem("Tools/Codex/EDC/1 Prepare And Audit Meshy Source")]
        public static void PrepareAndAuditSource()
        {
            RequireAsset(ModelPath);
            RequireAsset(BaseMapPath);
            RequireAsset(EmissionMapPath);
            RequireAsset(MetallicMapPath);
            RequireAsset(NormalMapPath);
            RequireAsset(RoughnessMapPath);

            AssetDatabase.ImportAsset(ModelPath, ImportAssetOptions.ForceSynchronousImport);
            ConfigureSourceModelImporter();
            ConfigureSourceTextures();
            CreatePackedMetallicSmoothnessMap();
            Material material = CreateOrUpdateUrpMaterial();

            Bounds before = GetModelBounds();
            float longestBefore = MaxDimension(before.size);
            if (longestBefore <= 0f || !float.IsFinite(longestBefore))
            {
                throw new InvalidDataException(
                    $"Imported FBX has invalid bounds: {before.size}.");
            }

            ModelImporter importer = GetModelImporter();
            float correction = TargetLongestDimensionMeters / longestBefore;
            importer.globalScale *= correction;
            importer.SaveAndReimport();

            Bounds after = GetModelBounds();
            float longestAfter = MaxDimension(after.size);
            if (Mathf.Abs(longestAfter - TargetLongestDimensionMeters) > 0.0001f)
            {
                throw new InvalidDataException(
                    $"Scale normalization failed. Expected {TargetLongestDimensionMeters:F5} m, "
                    + $"got {longestAfter:F5} m.");
            }

            string report = BuildImportReport(before, after, correction, importer, material);
            File.WriteAllText(ImportReportPath, report, new UTF8Encoding(false));
            AssetDatabase.ImportAsset(ImportReportPath, ImportAssetOptions.ForceSynchronousImport);
            AssetDatabase.SaveAssets();
            Debug.Log(report);
        }

        [MenuItem("Tools/Codex/EDC/Apply Silver Metal Material")]
        public static void ApplySilverMetalMaterial()
        {
            RequireAsset(BaseMapPath);
            RequireAsset(EmissionMapPath);
            RequireAsset(MetallicMapPath);
            RequireAsset(NormalMapPath);
            RequireAsset(RoughnessMapPath);
            ConfigureSourceTextures();
            CreatePackedMetallicSmoothnessMap();
            Material material = CreateOrUpdateUrpMaterial();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log(
                $"[EDCSilverMetal] material={material.name} "
                + $"roughnessInfluence={SilverRoughnessInfluence:F2} "
                + $"normalScale={SilverNormalScale:F2} "
                + $"glossScale={SilverGlossMapScale:F2} "
                + $"textureQuality={PolishedTextureCompressionQuality}");
        }

        [MenuItem("Tools/Codex/EDC/2 Analyze Connected Components")]
        public static void AnalyzeConnectedComponents()
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
            {
                throw new FileNotFoundException("Unity could not load the Meshy FBX.", ModelPath);
            }

            GameObject instance = UnityEngine.Object.Instantiate(model);
            instance.name = "EDC_ComponentAnalysis";
            try
            {
                MeshFilter[] filters = instance.GetComponentsInChildren<MeshFilter>(true);
                if (filters.Length != 1 || filters[0].sharedMesh == null)
                {
                    throw new InvalidDataException(
                        $"Expected exactly one source mesh, found {filters.Length}.");
                }

                string report = AnalyzeMesh(filters[0]);
                File.WriteAllText(ComponentReportPath, report, new UTF8Encoding(false));
                AssetDatabase.ImportAsset(
                    ComponentReportPath,
                    ImportAssetOptions.ForceSynchronousImport);
                Debug.Log(report);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }

        [MenuItem("Tools/Codex/EDC/Capture Source Orthographic Views")]
        public static void CaptureSourceOrthographicViews()
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            Material material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath);
            if (model == null || material == null)
            {
                throw new InvalidDataException(
                    "Prepare the Meshy source and URP material before capturing previews.");
            }

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("EDC_SourcePreview");
            GameObject instance = (GameObject)PrefabUtility.InstantiatePrefab(model, scene);
            instance.name = "Meshy_Source";
            instance.transform.SetParent(root.transform, false);
            instance.transform.localRotation = Quaternion.identity;
            foreach (Renderer renderer in instance.GetComponentsInChildren<Renderer>(true))
            {
                var materials = new Material[renderer.sharedMaterials.Length];
                for (int index = 0; index < materials.Length; index++)
                {
                    materials[index] = material;
                }
                renderer.sharedMaterials = materials;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                renderer.receiveShadows = true;
            }

            Bounds bounds = CombinedRendererBounds(instance);
            instance.transform.position -= bounds.center;
            bounds = CombinedRendererBounds(instance);

            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.18f, 0.20f, 0.24f, 1f);
            RenderSettings.reflectionIntensity = 0.35f;

            CreateDirectionalLight(
                "Key",
                Quaternion.Euler(42f, -28f, 0f),
                new Color(1f, 0.94f, 0.86f),
                2.2f);
            CreateDirectionalLight(
                "Fill",
                Quaternion.Euler(125f, 145f, 0f),
                new Color(0.58f, 0.72f, 1f),
                1.1f);

            var cameraObject = new GameObject("PreviewCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.018f, 0.021f, 0.028f, 1f);
            camera.orthographic = true;
            camera.nearClipPlane = 0.01f;
            camera.farClipPlane = 1f;
            camera.allowHDR = false;
            camera.allowMSAA = true;

            string outputFolder = Path.GetFullPath(
                Path.Combine(Application.dataPath, "../../../Artifacts/EDC"));
            Directory.CreateDirectory(outputFolder);

            camera.orthographicSize = Mathf.Max(
                bounds.size.z * 1.8f,
                bounds.size.x / ((float)PreviewWidth / PreviewHeight) * 0.60f);
            camera.transform.position = new Vector3(0f, 0.15f, 0f);
            camera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
            CaptureCamera(camera, Path.Combine(outputFolder, "Source_Edge_PosY.png"));

            camera.transform.position = new Vector3(0f, -0.15f, 0f);
            camera.transform.rotation = Quaternion.Euler(-90f, 0f, 0f);
            CaptureCamera(camera, Path.Combine(outputFolder, "Source_Face_NegY.png"));

            camera.orthographicSize = Mathf.Max(
                bounds.size.y * 0.60f,
                bounds.size.x / ((float)PreviewWidth / PreviewHeight) * 0.60f);
            camera.transform.position = new Vector3(0f, 0f, -0.15f);
            camera.transform.rotation = Quaternion.identity;
            CaptureCamera(camera, Path.Combine(outputFolder, "Source_Face_NegZ.png"));

            camera.transform.position = new Vector3(0f, 0f, 0.15f);
            camera.transform.rotation = Quaternion.Euler(0f, 180f, 0f);
            CaptureCamera(camera, Path.Combine(outputFolder, "Source_Face_PosZ.png"));

            camera.orthographicSize = Mathf.Max(bounds.size.y, bounds.size.z) * 0.65f;
            camera.transform.position = new Vector3(0.15f, 0f, 0f);
            camera.transform.rotation = Quaternion.Euler(0f, -90f, 0f);
            CaptureCamera(camera, Path.Combine(outputFolder, "Source_End_PosX.png"));

            Debug.Log(
                $"[EDCSourcePreview] folder={outputFolder} "
                + $"bounds={bounds.size.ToString("F6")}");
        }

        [MenuItem("Tools/Codex/EDC/Analyze Source Height Profile")]
        public static void AnalyzeSourceHeightProfile()
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
            {
                throw new FileNotFoundException("Unity could not load the Meshy FBX.", ModelPath);
            }

            GameObject instance = UnityEngine.Object.Instantiate(model);
            try
            {
                MeshFilter[] filters = instance.GetComponentsInChildren<MeshFilter>(true);
                if (filters.Length != 1 || filters[0].sharedMesh == null)
                {
                    throw new InvalidDataException(
                        $"Expected one source mesh for height analysis, found {filters.Length}.");
                }

                MeshFilter filter = filters[0];
                Mesh mesh = filter.sharedMesh;
                Vector3[] sourceVertices = mesh.vertices;
                var vertices = new Vector3[sourceVertices.Length];
                Matrix4x4 localToWorld = filter.transform.localToWorldMatrix;
                float minimumY = float.PositiveInfinity;
                float maximumY = float.NegativeInfinity;
                for (int index = 0; index < sourceVertices.Length; index++)
                {
                    Vector3 world = localToWorld.MultiplyPoint3x4(sourceVertices[index]);
                    vertices[index] = ToUnityYUp(world);
                    minimumY = Mathf.Min(minimumY, vertices[index].y);
                    maximumY = Mathf.Max(maximumY, vertices[index].y);
                }

                var triangleCounts = new long[HeightProfileBins];
                var surfaceAreas = new double[HeightProfileBins];
                var horizontalAreas = new double[HeightProfileBins];
                var verticalAreas = new double[HeightProfileBins];
                float heightRange = maximumY - minimumY;
                for (int submesh = 0; submesh < mesh.subMeshCount; submesh++)
                {
                    int[] triangles = mesh.GetTriangles(submesh);
                    for (int index = 0; index < triangles.Length; index += 3)
                    {
                        Vector3 first = vertices[triangles[index]];
                        Vector3 second = vertices[triangles[index + 1]];
                        Vector3 third = vertices[triangles[index + 2]];
                        Vector3 cross = Vector3.Cross(second - first, third - first);
                        double area = cross.magnitude * 0.5;
                        float centroidY = (first.y + second.y + third.y) / 3f;
                        int bin = Mathf.Clamp(
                            Mathf.FloorToInt((centroidY - minimumY) / heightRange * HeightProfileBins),
                            0,
                            HeightProfileBins - 1);
                        triangleCounts[bin]++;
                        surfaceAreas[bin] += area;
                        float verticalNormal = cross.sqrMagnitude > 0f
                            ? Mathf.Abs(cross.normalized.y)
                            : 0f;
                        if (verticalNormal >= 0.70f)
                        {
                            horizontalAreas[bin] += area;
                        }
                        else
                        {
                            verticalAreas[bin] += area;
                        }
                    }
                }

                var invariant = CultureInfo.InvariantCulture;
                var csv = new StringBuilder(HeightProfileBins * 96);
                csv.AppendLine(
                    "bin,center_y_m,center_y_mm,triangle_count,surface_area_m2,horizontal_area_m2,vertical_area_m2");
                float binHeight = heightRange / HeightProfileBins;
                for (int bin = 0; bin < HeightProfileBins; bin++)
                {
                    float center = minimumY + (bin + 0.5f) * binHeight;
                    csv.Append(bin.ToString(invariant)).Append(',')
                        .Append(center.ToString("R", invariant)).Append(',')
                        .Append((center * 1000f).ToString("F6", invariant)).Append(',')
                        .Append(triangleCounts[bin].ToString(invariant)).Append(',')
                        .Append(surfaceAreas[bin].ToString("R", invariant)).Append(',')
                        .Append(horizontalAreas[bin].ToString("R", invariant)).Append(',')
                        .Append(verticalAreas[bin].ToString("R", invariant)).AppendLine();
                }

                File.WriteAllText(HeightProfilePath, csv.ToString(), new UTF8Encoding(false));
                AssetDatabase.ImportAsset(HeightProfilePath, ImportAssetOptions.ForceSynchronousImport);
                Debug.Log(
                    $"[EDCHeightProfile] minY={minimumY:F6} maxY={maximumY:F6} "
                    + $"range={heightRange:F6} bins={HeightProfileBins} path={HeightProfilePath}");
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }

        [MenuItem("Tools/Codex/EDC/3 Export Manual Layer Sources")]
        public static void ExportManualLayerSources()
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
            {
                throw new FileNotFoundException("Unity could not load the Meshy FBX.", ModelPath);
            }

            GameObject instance = UnityEngine.Object.Instantiate(model);
            try
            {
                MeshFilter[] filters = instance.GetComponentsInChildren<MeshFilter>(true);
                if (filters.Length != 1 || filters[0].sharedMesh == null)
                {
                    throw new InvalidDataException(
                        $"Expected one source mesh for manual cutting, found {filters.Length}.");
                }

                MeshFilter filter = filters[0];
                Mesh mesh = filter.sharedMesh;
                Vector3[] sourceVertices = mesh.vertices;
                Vector2[] sourceUvs = mesh.uv;
                Vector3[] sourceNormals = mesh.normals;
                if (sourceUvs.Length != sourceVertices.Length)
                {
                    throw new InvalidDataException(
                        $"Manual cutting requires one UV per vertex; got "
                        + $"{sourceVertices.Length} vertices and {sourceUvs.Length} UVs.");
                }
                if (sourceNormals.Length != sourceVertices.Length)
                {
                    throw new InvalidDataException(
                        $"Manual cutting requires one normal per vertex; got "
                        + $"{sourceVertices.Length} vertices and {sourceNormals.Length} normals.");
                }

                Matrix4x4 localToWorld = filter.transform.localToWorldMatrix;
                var vertices = new Vector3[sourceVertices.Length];
                var normals = new Vector3[sourceVertices.Length];
                Bounds productBounds = default;
                bool hasBounds = false;
                for (int index = 0; index < sourceVertices.Length; index++)
                {
                    Vector3 world = localToWorld.MultiplyPoint3x4(sourceVertices[index]);
                    Vector3 product = ToProductYUp(world);
                    vertices[index] = product;
                    normals[index] = ToProductYUp(
                        localToWorld.MultiplyVector(sourceNormals[index])).normalized;
                    if (!hasBounds)
                    {
                        productBounds = new Bounds(product, Vector3.zero);
                        hasBounds = true;
                    }
                    else
                    {
                        productBounds.Encapsulate(product);
                    }
                }

                Vector3 planarCenter = new Vector3(
                    productBounds.center.x,
                    0f,
                    productBounds.center.z);
                for (int index = 0; index < vertices.Length; index++)
                {
                    vertices[index] -= planarCenter;
                }

                ManualLayerCut[] layers = CreateManualLayerCuts();
                for (int submesh = 0; submesh < mesh.subMeshCount; submesh++)
                {
                    int[] triangles = mesh.GetTriangles(submesh);
                    for (int index = 0; index < triangles.Length; index += 3)
                    {
                        int first = triangles[index];
                        int second = triangles[index + 1];
                        int third = triangles[index + 2];
                        float centroidY = (
                            vertices[first].y + vertices[second].y + vertices[third].y) / 3f;
                        ManualLayerCut layer = ResolveManualLayer(layers, centroidY);
                        layer.Triangles.Add(first);
                        layer.Triangles.Add(second);
                        layer.Triangles.Add(third);
                    }
                }

                Directory.CreateDirectory(ManualLayerSourceFolder);
                var report = new StringBuilder(2048);
                report.AppendLine("[EDCManualLayerExport] PASS");
                report.Append("productBoundsCenter=").AppendLine(productBounds.center.ToString("F6"));
                report.Append("productBoundsSize=").AppendLine(productBounds.size.ToString("F6"));
                report.Append("planarCenterRemoved=").AppendLine(planarCenter.ToString("F6"));
                foreach (ManualLayerCut layer in layers)
                {
                    string outputPath = Path.Combine(
                        ManualLayerSourceFolder,
                        layer.Name + "_Source.obj");
                    int exportedVertices = WriteLayerObj(
                        outputPath,
                        layer.Name,
                        vertices,
                        sourceUvs,
                        normals,
                        layer.Triangles);
                    report.Append("layer=").Append(layer.Name)
                        .Append(" minY=").Append(layer.MinimumY.ToString("F6", CultureInfo.InvariantCulture))
                        .Append(" vertices=").Append(exportedVertices)
                        .Append(" triangles=").Append(layer.Triangles.Count / 3)
                        .Append(" path=").AppendLine(outputPath);
                }

                var allTriangles = new List<int>(
                    layers.Sum(layer => layer.Triangles.Count));
                foreach (ManualLayerCut layer in layers)
                {
                    allTriangles.AddRange(layer.Triangles);
                }
                string fullSourcePath = Path.Combine(
                    ManualLayerSourceFolder,
                    "EDC_Full_Source.obj");
                int fullVertexCount = WriteLayerObj(
                    fullSourcePath,
                    "EDC_Full_Source",
                    vertices,
                    sourceUvs,
                    normals,
                    allTriangles);
                report.Append("full vertices=").Append(fullVertexCount)
                    .Append(" triangles=").Append(allTriangles.Count / 3)
                    .Append(" path=").AppendLine(fullSourcePath);

                string reportPath = Path.Combine(ManualLayerSourceFolder, "export-report.txt");
                File.WriteAllText(reportPath, report.ToString(), new UTF8Encoding(false));
                Debug.Log(report.ToString());
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }

        private static ManualLayerCut[] CreateManualLayerCuts()
        {
            return new[]
            {
                new ManualLayerCut("L1_TopFrame", TopFrameMinimumY),
                new ManualLayerCut("L2_UpperShell", UpperShellMinimumY),
                new ManualLayerCut("L3_Gasket", GasketMinimumY),
                new ManualLayerCut("L6_InnerFrame", InnerFrameMinimumY),
                new ManualLayerCut("L7_BottomShell", float.NegativeInfinity)
            };
        }

        private static ManualLayerCut ResolveManualLayer(
            ManualLayerCut[] layers,
            float centroidY)
        {
            foreach (ManualLayerCut layer in layers)
            {
                if (centroidY >= layer.MinimumY)
                {
                    return layer;
                }
            }
            throw new InvalidDataException($"No manual layer accepts y={centroidY}.");
        }

        private static int WriteLayerObj(
            string path,
            string objectName,
            Vector3[] vertices,
            Vector2[] uvs,
            Vector3[] normals,
            List<int> triangles)
        {
            var sourceToLayer = new int[vertices.Length];
            Array.Fill(sourceToLayer, -1);
            var referenced = new List<int>(Mathf.Min(vertices.Length, triangles.Count));
            foreach (int sourceIndex in triangles)
            {
                if (sourceToLayer[sourceIndex] >= 0)
                {
                    continue;
                }
                sourceToLayer[sourceIndex] = referenced.Count;
                referenced.Add(sourceIndex);
            }

            var invariant = CultureInfo.InvariantCulture;
            using var writer = new StreamWriter(
                path,
                false,
                new UTF8Encoding(false),
                1 << 20);
            writer.Write("# Height-band manual cut from Meshy source\no ");
            writer.WriteLine(objectName);
            foreach (int sourceIndex in referenced)
            {
                Vector3 vertex = vertices[sourceIndex];
                writer.Write("v ");
                writer.Write(vertex.x.ToString("R", invariant));
                writer.Write(' ');
                writer.Write(vertex.y.ToString("R", invariant));
                writer.Write(' ');
                writer.Write(vertex.z.ToString("R", invariant));
                writer.WriteLine();
            }
            foreach (int sourceIndex in referenced)
            {
                Vector2 uv = uvs[sourceIndex];
                writer.Write("vt ");
                writer.Write(uv.x.ToString("R", invariant));
                writer.Write(' ');
                writer.Write(uv.y.ToString("R", invariant));
                writer.WriteLine();
            }
            foreach (int sourceIndex in referenced)
            {
                Vector3 normal = normals[sourceIndex];
                writer.Write("vn ");
                writer.Write(normal.x.ToString("R", invariant));
                writer.Write(' ');
                writer.Write(normal.y.ToString("R", invariant));
                writer.Write(' ');
                writer.Write(normal.z.ToString("R", invariant));
                writer.WriteLine();
            }
            for (int index = 0; index < triangles.Count; index += 3)
            {
                int first = sourceToLayer[triangles[index]] + 1;
                int second = sourceToLayer[triangles[index + 1]] + 1;
                int third = sourceToLayer[triangles[index + 2]] + 1;
                writer.Write("f ");
                WriteObjIndex(writer, first);
                writer.Write(' ');
                WriteObjIndex(writer, second);
                writer.Write(' ');
                WriteObjIndex(writer, third);
                writer.WriteLine();
            }
            return referenced.Count;
        }

        private static void WriteObjIndex(StreamWriter writer, int index)
        {
            writer.Write(index);
            writer.Write('/');
            writer.Write(index);
            writer.Write('/');
            writer.Write(index);
        }

        private static Vector3 ToProductYUp(Vector3 source)
        {
            // Rotate the imported source -90 degrees around X so the X-frame
            // faces upward. This preserves handedness and triangle winding.
            return new Vector3(source.x, source.z, -source.y);
        }

        private static void CaptureCamera(Camera camera, string outputPath)
        {
            var renderTexture = new RenderTexture(
                PreviewWidth,
                PreviewHeight,
                24,
                RenderTextureFormat.ARGB32)
            {
                antiAliasing = 4
            };
            var texture = new Texture2D(
                PreviewWidth,
                PreviewHeight,
                TextureFormat.RGBA32,
                false,
                false);
            RenderTexture previous = RenderTexture.active;
            try
            {
                camera.targetTexture = renderTexture;
                camera.Render();
                RenderTexture.active = renderTexture;
                texture.ReadPixels(new Rect(0, 0, PreviewWidth, PreviewHeight), 0, 0);
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

        private static Bounds CombinedRendererBounds(GameObject root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
            {
                throw new InvalidDataException("Preview model contains no renderers.");
            }

            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Length; index++)
            {
                bounds.Encapsulate(renderers[index].bounds);
            }
            return bounds;
        }

        private static void CreateDirectionalLight(
            string name,
            Quaternion rotation,
            Color color,
            float intensity)
        {
            var lightObject = new GameObject(name);
            lightObject.transform.rotation = rotation;
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
        }

        private static string AnalyzeMesh(MeshFilter filter)
        {
            Mesh mesh = filter.sharedMesh;
            Vector3[] vertices = mesh.vertices;
            int vertexCount = vertices.Length;
            var unionFind = new UnionFind(vertexCount);
            var referenced = new bool[vertexCount];
            var submeshTriangles = new int[mesh.subMeshCount][];
            long triangleCount = 0;

            for (int submesh = 0; submesh < mesh.subMeshCount; submesh++)
            {
                int[] triangles = mesh.GetTriangles(submesh);
                submeshTriangles[submesh] = triangles;
                triangleCount += triangles.LongLength / 3;
                for (int index = 0; index < triangles.Length; index += 3)
                {
                    int first = triangles[index];
                    int second = triangles[index + 1];
                    int third = triangles[index + 2];
                    referenced[first] = true;
                    referenced[second] = true;
                    referenced[third] = true;
                    unionFind.Union(first, second);
                    unionFind.Union(first, third);
                }
            }

            Matrix4x4 localToWorld = filter.transform.localToWorldMatrix;
            var canonicalByPosition = new Dictionary<QuantizedPosition, int>(vertexCount);
            for (int index = 0; index < vertexCount; index++)
            {
                if (!referenced[index])
                {
                    continue;
                }

                Vector3 world = localToWorld.MultiplyPoint3x4(vertices[index]);
                var key = new QuantizedPosition(world, PositionWeldToleranceMeters);
                if (canonicalByPosition.TryGetValue(key, out int canonical))
                {
                    unionFind.Union(index, canonical);
                }
                else
                {
                    canonicalByPosition.Add(key, index);
                }
            }

            var statsByRoot = new Dictionary<int, ComponentStats>();
            for (int index = 0; index < vertexCount; index++)
            {
                if (!referenced[index])
                {
                    continue;
                }

                int root = unionFind.Find(index);
                if (!statsByRoot.TryGetValue(root, out ComponentStats stats))
                {
                    stats = new ComponentStats(root);
                    statsByRoot.Add(root, stats);
                }

                Vector3 world = localToWorld.MultiplyPoint3x4(vertices[index]);
                stats.AddVertex(ToUnityYUp(world));
            }

            foreach (int[] triangles in submeshTriangles)
            {
                for (int index = 0; index < triangles.Length; index += 3)
                {
                    int root = unionFind.Find(triangles[index]);
                    ComponentStats stats = statsByRoot[root];
                    stats.TriangleCount++;
                }
            }

            ComponentStats[] components = statsByRoot.Values
                .OrderByDescending(component => component.BoundsVolume)
                .ThenByDescending(component => component.Bounds.center.y)
                .ToArray();

            var invariant = CultureInfo.InvariantCulture;
            var report = new StringBuilder(Math.Max(4096, components.Length * 180));
            report.AppendLine("[EDCConnectedComponents]");
            report.Append("model=").AppendLine(ModelPath);
            report.Append("mesh=").AppendLine(mesh.name);
            report.Append("sourceVertices=").AppendLine(vertexCount.ToString(invariant));
            report.Append("sourceTriangles=").AppendLine(triangleCount.ToString(invariant));
            report.Append("positionWeldToleranceMeters=")
                .AppendLine(PositionWeldToleranceMeters.ToString("R", invariant));
            report.AppendLine("axisConversion=source(X,Y,Z) -> UnityYUp(X,Z,-Y)");
            report.Append("componentCount=").AppendLine(components.Length.ToString(invariant));
            report.Append("mappingGate=")
                .AppendLine(IsPlausibleComponentCount(components.Length) ? "COUNT_PLAUSIBLE" : "STOP_COUNT_MISMATCH");
            report.AppendLine(
                "columns=id centerMeters sizeMeters boundsVolume vertices triangles minAxis/maxAxis");

            for (int index = 0; index < components.Length; index++)
            {
                ComponentStats stats = components[index];
                Vector3 size = stats.Bounds.size;
                float minAxis = Mathf.Min(size.x, Mathf.Min(size.y, size.z));
                float maxAxis = Mathf.Max(size.x, Mathf.Max(size.y, size.z));
                float axisRatio = maxAxis / Mathf.Max(minAxis, 0.000000001f);
                report.Append("C").Append((index + 1).ToString("D4", invariant))
                    .Append(" center=").Append(stats.Bounds.center.ToString("F6"))
                    .Append(" size=").Append(size.ToString("F6"))
                    .Append(" volume=").Append(stats.BoundsVolume.ToString("E6", invariant))
                    .Append(" vertices=").Append(stats.VertexCount.ToString(invariant))
                    .Append(" triangles=").Append(stats.TriangleCount.ToString(invariant))
                    .Append(" axisRatio=").Append(axisRatio.ToString("F3", invariant))
                    .AppendLine();
            }

            return report.ToString();
        }

        private static bool IsPlausibleComponentCount(int count)
        {
            // The brief expects roughly 10-16 pieces, while the fully explicit
            // hierarchy would contain 17 loose pieces (two rails, six magnets,
            // four screws, and five other structural bodies). Accept only this
            // narrow range for the next, shape-aware mapping gate.
            return count >= 10 && count <= 17;
        }

        private static Vector3 ToUnityYUp(Vector3 source)
        {
            return new Vector3(source.x, source.z, -source.y);
        }

        private static void ConfigureSourceModelImporter()
        {
            ModelImporter importer = GetModelImporter();
            importer.useFileScale = true;
            importer.importAnimation = false;
            importer.importBlendShapes = false;
            importer.importCameras = false;
            importer.importLights = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.meshCompression = ModelImporterMeshCompression.Off;
            importer.optimizeMeshPolygons = false;
            importer.optimizeMeshVertices = false;
            importer.weldVertices = false;
            importer.isReadable = true;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.SaveAndReimport();
        }

        private static void ConfigureSourceTextures()
        {
            ConfigureTexture(BaseMapPath, true, TextureImporterType.Default, false);
            ConfigureTexture(EmissionMapPath, true, TextureImporterType.Default, false);
            ConfigureTexture(MetallicMapPath, false, TextureImporterType.Default, true);
            ConfigureTexture(NormalMapPath, false, TextureImporterType.NormalMap, false);
            ConfigureTexture(RoughnessMapPath, false, TextureImporterType.Default, true);
        }

        private static void ConfigureTexture(
            string path,
            bool sRgb,
            TextureImporterType type,
            bool readable)
        {
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null)
            {
                throw new InvalidDataException($"Texture importer missing for {path}.");
            }

            importer.textureType = type;
            importer.sRGBTexture = sRgb;
            importer.isReadable = readable;
            importer.mipmapEnabled = true;
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.filterMode = FilterMode.Trilinear;
            importer.anisoLevel = 4;
            importer.mipMapBias = -0.25f;
            importer.textureCompression = TextureImporterCompression.CompressedHQ;
            importer.compressionQuality = PolishedTextureCompressionQuality;
            importer.SaveAndReimport();
        }

        private static void CreatePackedMetallicSmoothnessMap()
        {
            Texture2D metallic = AssetDatabase.LoadAssetAtPath<Texture2D>(MetallicMapPath);
            Texture2D roughness = AssetDatabase.LoadAssetAtPath<Texture2D>(RoughnessMapPath);
            if (metallic == null || roughness == null)
            {
                throw new InvalidDataException("Metallic or roughness texture failed to import.");
            }
            if (metallic.width != roughness.width || metallic.height != roughness.height)
            {
                throw new InvalidDataException(
                    "Metallic and roughness maps must have identical dimensions.");
            }

            Color32[] metallicPixels = metallic.GetPixels32();
            Color32[] roughnessPixels = roughness.GetPixels32();
            var packedPixels = new Color32[metallicPixels.Length];
            for (int index = 0; index < packedPixels.Length; index++)
            {
                byte metallicValue = metallicPixels[index].r;
                byte smoothnessValue = (byte)Mathf.Clamp(
                    Mathf.RoundToInt(
                        255f
                        - roughnessPixels[index].r * SilverRoughnessInfluence),
                    0,
                    255);
                packedPixels[index] = new Color32(
                    metallicValue,
                    metallicValue,
                    metallicValue,
                    smoothnessValue);
            }

            var packed = new Texture2D(
                metallic.width,
                metallic.height,
                TextureFormat.RGBA32,
                false,
                true);
            packed.name = "T_EDC_MetallicSmoothness";
            packed.SetPixels32(packedPixels);
            packed.Apply(false, false);
            File.WriteAllBytes(PackedMaskPath, packed.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(packed);

            AssetDatabase.ImportAsset(PackedMaskPath, ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = AssetImporter.GetAtPath(PackedMaskPath) as TextureImporter;
            if (importer == null)
            {
                throw new InvalidDataException("Packed mask texture importer is missing.");
            }
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = false;
            importer.alphaSource = TextureImporterAlphaSource.FromInput;
            importer.isReadable = false;
            importer.mipmapEnabled = true;
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.filterMode = FilterMode.Trilinear;
            importer.anisoLevel = 4;
            importer.mipMapBias = -0.25f;
            importer.textureCompression = TextureImporterCompression.CompressedHQ;
            importer.compressionQuality = PolishedTextureCompressionQuality;
            importer.SaveAndReimport();

            SetTextureReadability(MetallicMapPath, false);
            SetTextureReadability(RoughnessMapPath, false);
        }

        private static Material CreateOrUpdateUrpMaterial()
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                throw new InvalidDataException("URP/Lit shader is unavailable in this project.");
            }

            Material material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath);
            if (material == null)
            {
                material = new Material(shader) { name = "M_EDC_Meshy_URP_Lit" };
                AssetDatabase.CreateAsset(material, MaterialPath);
            }
            else
            {
                material.shader = shader;
            }

            material.SetColor(
                "_BaseColor",
                new Color(SilverTintRed, SilverTintGreen, SilverTintBlue, 1f));
            material.SetTexture("_BaseMap", LoadTexture(BaseMapPath));
            material.SetFloat("_Metallic", 1f);
            material.SetFloat("_Smoothness", 1f);
            material.SetFloat("_GlossMapScale", SilverGlossMapScale);
            material.SetFloat("_SmoothnessTextureChannel", 0f);
            material.SetTexture("_MetallicGlossMap", LoadTexture(PackedMaskPath));
            material.EnableKeyword("_METALLICSPECGLOSSMAP");
            material.SetFloat("_BumpScale", SilverNormalScale);
            material.SetTexture("_BumpMap", LoadTexture(NormalMapPath));
            material.EnableKeyword("_NORMALMAP");
            material.SetFloat("_EnvironmentReflections", 1f);
            material.SetFloat("_SpecularHighlights", SilverRealtimeSpecular);
            material.DisableKeyword("_SPECULARHIGHLIGHTS_OFF");
            // Realtime specular is the gyro-tracked environment highlight.
            // Emission still stays off so silver never self-glows or clips
            // independently of the scene lights.
            material.SetColor("_EmissionColor", Color.black);
            material.SetTexture("_EmissionMap", null);
            material.DisableKeyword("_EMISSION");
            material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.None;
            EditorUtility.SetDirty(material);
            AssetDatabase.SaveAssetIfDirty(material);
            return material;
        }

        private static string BuildImportReport(
            Bounds before,
            Bounds after,
            float correction,
            ModelImporter importer,
            Material material)
        {
            var invariant = CultureInfo.InvariantCulture;
            var report = new StringBuilder(4096);
            report.AppendLine("[EDCImportAudit] PASS");
            report.Append("model=").AppendLine(ModelPath);
            report.Append("boundsBeforeCenter=").AppendLine(before.center.ToString("F6"));
            report.Append("boundsBeforeSize=").AppendLine(before.size.ToString("F6"));
            report.Append("scaleCorrection=")
                .AppendLine(correction.ToString("R", invariant));
            report.Append("importerGlobalScale=")
                .AppendLine(importer.globalScale.ToString("R", invariant));
            report.Append("boundsAfterCenter=").AppendLine(after.center.ToString("F6"));
            report.Append("boundsAfterSize=").AppendLine(after.size.ToString("F6"));
            report.Append("targetLongestDimensionMeters=")
                .AppendLine(TargetLongestDimensionMeters.ToString("R", invariant));
            report.Append("material=").Append(material.name)
                .Append(" shader=").AppendLine(material.shader.name);
            AppendTextureBinding(report, material, "_BaseMap");
            AppendTextureBinding(report, material, "_MetallicGlossMap");
            AppendTextureBinding(report, material, "_BumpMap");
            AppendTextureBinding(report, material, "_EmissionMap");
            report.Append("roughnessSource=").AppendLine(RoughnessMapPath);

            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            GameObject instance = UnityEngine.Object.Instantiate(model);
            try
            {
                MeshFilter[] filters = instance.GetComponentsInChildren<MeshFilter>(true);
                report.Append("meshFilterCount=").AppendLine(filters.Length.ToString(invariant));
                foreach (MeshFilter filter in filters)
                {
                    Mesh mesh = filter.sharedMesh;
                    report.Append("mesh=").Append(mesh != null ? mesh.name : "none")
                        .Append(" vertices=").Append(mesh != null ? mesh.vertexCount : 0)
                        .Append(" subMeshes=").Append(mesh != null ? mesh.subMeshCount : 0)
                        .Append(" uv0=").Append(mesh != null ? mesh.uv.Length : 0)
                        .AppendLine();
                }
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
            return report.ToString();
        }

        private static void AppendTextureBinding(
            StringBuilder report,
            Material material,
            string property)
        {
            Texture texture = material.GetTexture(property);
            report.Append(property).Append('=')
                .Append(texture != null ? AssetDatabase.GetAssetPath(texture) : "none")
                .AppendLine();
        }

        private static Bounds GetModelBounds()
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
            {
                throw new FileNotFoundException("Unity could not import the Meshy FBX.", ModelPath);
            }

            GameObject instance = UnityEngine.Object.Instantiate(model);
            try
            {
                Renderer[] renderers = instance.GetComponentsInChildren<Renderer>(true);
                if (renderers.Length == 0)
                {
                    throw new InvalidDataException("Imported FBX contains no renderers.");
                }

                Bounds bounds = renderers[0].bounds;
                for (int index = 1; index < renderers.Length; index++)
                {
                    bounds.Encapsulate(renderers[index].bounds);
                }
                return bounds;
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }

        private static float MaxDimension(Vector3 size)
        {
            return Mathf.Max(size.x, Mathf.Max(size.y, size.z));
        }

        private static ModelImporter GetModelImporter()
        {
            ModelImporter importer = AssetImporter.GetAtPath(ModelPath) as ModelImporter;
            if (importer == null)
            {
                throw new FileNotFoundException("ModelImporter is missing.", ModelPath);
            }
            return importer;
        }

        private static Texture2D LoadTexture(string path)
        {
            Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (texture == null)
            {
                throw new FileNotFoundException("Texture asset is missing.", path);
            }
            return texture;
        }

        private static void RequireAsset(string path)
        {
            if (!File.Exists(path))
            {
                throw new FileNotFoundException("Required Meshy source asset is missing.", path);
            }
        }

        private static void SetTextureReadability(string path, bool readable)
        {
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer != null && importer.isReadable != readable)
            {
                importer.isReadable = readable;
                importer.SaveAndReimport();
            }
        }

        private readonly struct QuantizedPosition : IEquatable<QuantizedPosition>
        {
            private readonly int x;
            private readonly int y;
            private readonly int z;

            public QuantizedPosition(Vector3 position, float tolerance)
            {
                x = Mathf.RoundToInt(position.x / tolerance);
                y = Mathf.RoundToInt(position.y / tolerance);
                z = Mathf.RoundToInt(position.z / tolerance);
            }

            public bool Equals(QuantizedPosition other)
            {
                return x == other.x && y == other.y && z == other.z;
            }

            public override bool Equals(object obj)
            {
                return obj is QuantizedPosition other && Equals(other);
            }

            public override int GetHashCode()
            {
                unchecked
                {
                    int hash = x;
                    hash = (hash * 397) ^ y;
                    hash = (hash * 397) ^ z;
                    return hash;
                }
            }
        }

        private sealed class UnionFind
        {
            private readonly int[] parent;
            private readonly byte[] rank;

            public UnionFind(int count)
            {
                parent = new int[count];
                rank = new byte[count];
                for (int index = 0; index < count; index++)
                {
                    parent[index] = index;
                }
            }

            public int Find(int value)
            {
                int root = value;
                while (parent[root] != root)
                {
                    root = parent[root];
                }
                while (parent[value] != value)
                {
                    int next = parent[value];
                    parent[value] = root;
                    value = next;
                }
                return root;
            }

            public void Union(int first, int second)
            {
                int firstRoot = Find(first);
                int secondRoot = Find(second);
                if (firstRoot == secondRoot)
                {
                    return;
                }

                if (rank[firstRoot] < rank[secondRoot])
                {
                    parent[firstRoot] = secondRoot;
                }
                else if (rank[firstRoot] > rank[secondRoot])
                {
                    parent[secondRoot] = firstRoot;
                }
                else
                {
                    parent[secondRoot] = firstRoot;
                    rank[firstRoot]++;
                }
            }
        }

        private sealed class ComponentStats
        {
            private bool hasBounds;

            public ComponentStats(int root)
            {
                Root = root;
            }

            public int Root { get; }
            public Bounds Bounds { get; private set; }
            public int VertexCount { get; private set; }
            public long TriangleCount { get; set; }
            public float BoundsVolume => Bounds.size.x * Bounds.size.y * Bounds.size.z;

            public void AddVertex(Vector3 position)
            {
                if (!hasBounds)
                {
                    Bounds = new Bounds(position, Vector3.zero);
                    hasBounds = true;
                }
                else
                {
                    Bounds bounds = Bounds;
                    bounds.Encapsulate(position);
                    Bounds = bounds;
                }
                VertexCount++;
            }
        }

        private sealed class ManualLayerCut
        {
            public ManualLayerCut(string name, float minimumY)
            {
                Name = name;
                MinimumY = minimumY;
                Triangles = new List<int>();
            }

            public string Name { get; }
            public float MinimumY { get; }
            public List<int> Triangles { get; }
        }
    }
}
