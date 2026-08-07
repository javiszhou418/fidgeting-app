using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using FidgetingApp.EDC;
using FidgetingApp.EDC.EditorTools;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace FidgetingApp.EDC.Tests.Editor
{
    /// <summary>
    /// Non-destructive visual validation harness for temporary EDC reduction candidates.
    /// Candidate meshes are read directly from /tmp and never imported over production assets.
    /// </summary>
    public static class EdcOptimizationVisualValidator
    {
        private const int Width = 1200;
        private const int Height = 800;

        public static void CaptureAll()
        {
            string candidateRoot = Environment.GetEnvironmentVariable("EDC_OPT_CANDIDATES");
            if (string.IsNullOrWhiteSpace(candidateRoot))
            {
                candidateRoot = "/tmp/fidgeting_edc_optimization_candidates";
            }

            string outputRoot = Environment.GetEnvironmentVariable("EDC_OPT_OUTPUT");
            if (string.IsNullOrWhiteSpace(outputRoot))
            {
                outputRoot = Path.GetFullPath(Path.Combine(
                    Application.dataPath,
                    "../../../Artifacts/EDC/OptimizationValidation/UnityMetal"));
            }

            Directory.CreateDirectory(outputRoot);
            EditorSceneManager.OpenScene(EdcSceneBuilder.ScenePath, OpenSceneMode.Single);
            GameObject root = GameObject.Find("EDC_Root");
            Camera camera = Camera.main;
            EdcSliderController controller = root != null
                ? root.GetComponent<EdcSliderController>()
                : null;
            if (root == null || camera == null || controller == null)
            {
                throw new InvalidDataException("MeshyEDC validation scene is incomplete.");
            }

            var layerFilters = new Dictionary<string, MeshFilter>
            {
                { "L1_TopFrame", RequireFilter(root.transform, "SliderGroup/L1_TopFrame") },
                { "L2_UpperShell", RequireFilter(root.transform, "SliderGroup/L2_UpperShell") },
                { "L3_Gasket", RequireFilter(root.transform, "Base/L3_Gasket") },
                { "L6_InnerFrame", RequireFilter(root.transform, "Base/L6_InnerFrame") },
                { "L7_BottomShell", RequireFilter(root.transform, "Base/L7_BottomShell") }
            };
            var originalMeshes = layerFilters.ToDictionary(pair => pair.Key, pair => pair.Value.sharedMesh);
            var originalPositions = layerFilters.ToDictionary(
                pair => pair.Key,
                pair => pair.Value.transform.localPosition);

            Debug.Log(
                $"EDC_OPT_RENDERER graphics={SystemInfo.graphicsDeviceType} "
                + $"device={SystemInfo.graphicsDeviceName} output={outputRoot}");
            CaptureSet(camera, controller, Path.Combine(outputRoot, "baseline_1994857"));

            string[] candidateFolders = Directory.GetDirectories(candidateRoot, "qem_a1_t*")
                .OrderByDescending(ParseTarget)
                .ToArray();
            if (candidateFolders.Length == 0)
            {
                throw new DirectoryNotFoundException(
                    $"No qem_a1_t* candidates found in {candidateRoot}");
            }

            foreach (string candidateFolder in candidateFolders)
            {
                string manifestPath = Path.Combine(candidateFolder, "layer-manifest.json");
                LayerManifest manifest = JsonUtility.FromJson<LayerManifest>(
                    File.ReadAllText(manifestPath));
                var transientMeshes = new List<Mesh>();
                try
                {
                    foreach (LayerEntry layer in manifest.layers)
                    {
                        Mesh mesh = ReadObj(Path.Combine(
                            candidateFolder,
                            layer.name + "_Runtime.obj"));
                        transientMeshes.Add(mesh);
                        MeshFilter filter = layerFilters[layer.name];
                        filter.sharedMesh = mesh;
                        filter.transform.localPosition = ToVector3(layer.pivotPosition);
                    }

                    string folderName = new DirectoryInfo(candidateFolder).Name;
                    CaptureSet(camera, controller, Path.Combine(outputRoot, folderName));
                    Debug.Log(
                        $"EDC_OPT_CAPTURE tier={folderName} "
                        + $"triangles={manifest.totalRuntimeTriangles}");
                }
                finally
                {
                    foreach (KeyValuePair<string, MeshFilter> pair in layerFilters)
                    {
                        pair.Value.sharedMesh = originalMeshes[pair.Key];
                        pair.Value.transform.localPosition = originalPositions[pair.Key];
                    }
                    foreach (Mesh mesh in transientMeshes)
                    {
                        UnityEngine.Object.DestroyImmediate(mesh);
                    }
                }
            }

            controller.SetSlideProgress(0f);
            Debug.Log("EDC_OPT_CAPTURE_COMPLETE");
        }

        private static int ParseTarget(string path)
        {
            string name = new DirectoryInfo(path).Name;
            int marker = name.LastIndexOf('t');
            return marker >= 0 && int.TryParse(name.Substring(marker + 1), out int target)
                ? target
                : 0;
        }

        private static MeshFilter RequireFilter(Transform root, string path)
        {
            Transform found = root.Find(path);
            MeshFilter filter = found != null ? found.GetComponent<MeshFilter>() : null;
            if (filter == null)
            {
                throw new InvalidDataException($"Missing EDC mesh at {path}");
            }
            return filter;
        }

        private static void CaptureSet(
            Camera camera,
            EdcSliderController controller,
            string folder)
        {
            Directory.CreateDirectory(folder);
            bool orthographic = camera.orthographic;
            float orthographicSize = camera.orthographicSize;
            Vector3 position = camera.transform.position;
            Quaternion rotation = camera.transform.rotation;

            controller.SetSlideProgress(0f);
            camera.orthographic = true;
            camera.orthographicSize = 0.030f;
            camera.transform.position = new Vector3(0f, 0.15f, 0f);
            camera.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
            Capture(camera, Path.Combine(folder, "Top.png"));

            camera.transform.position = new Vector3(0f, 0f, -0.15f);
            camera.transform.rotation = Quaternion.identity;
            Capture(camera, Path.Combine(folder, "Side.png"));

            camera.orthographic = orthographic;
            camera.orthographicSize = orthographicSize;
            camera.transform.position = position;
            camera.transform.rotation = rotation;
            Capture(camera, Path.Combine(folder, "Hero.png"));

            controller.SetSlideProgress(1f);
            Capture(camera, Path.Combine(folder, "Open.png"));

            controller.SetSlideProgress(0f);
            camera.orthographic = orthographic;
            camera.orthographicSize = orthographicSize;
            camera.transform.position = position;
            camera.transform.rotation = rotation;
        }

        private static void Capture(Camera camera, string outputPath)
        {
            var renderTexture = new RenderTexture(
                Width,
                Height,
                24,
                RenderTextureFormat.ARGB32)
            {
                antiAliasing = 4
            };
            var texture = new Texture2D(
                Width,
                Height,
                TextureFormat.RGBA32,
                false,
                false);
            RenderTexture previous = RenderTexture.active;
            try
            {
                camera.targetTexture = renderTexture;
                camera.Render();
                RenderTexture.active = renderTexture;
                texture.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
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

        private static Mesh ReadObj(string path)
        {
            var vertices = new List<Vector3>();
            var uvs = new List<Vector2>();
            var normals = new List<Vector3>();
            var triangles = new List<int>();
            using (var input = new StreamReader(path))
            {
                string line;
                while ((line = input.ReadLine()) != null)
                {
                    if (line.StartsWith("v ", StringComparison.Ordinal))
                    {
                        string[] parts = line.Split(' ');
                        vertices.Add(new Vector3(
                            ParseFloat(parts[1]),
                            ParseFloat(parts[2]),
                            ParseFloat(parts[3])));
                    }
                    else if (line.StartsWith("vt ", StringComparison.Ordinal))
                    {
                        string[] parts = line.Split(' ');
                        uvs.Add(new Vector2(ParseFloat(parts[1]), ParseFloat(parts[2])));
                    }
                    else if (line.StartsWith("vn ", StringComparison.Ordinal))
                    {
                        string[] parts = line.Split(' ');
                        normals.Add(new Vector3(
                            ParseFloat(parts[1]),
                            ParseFloat(parts[2]),
                            ParseFloat(parts[3])));
                    }
                    else if (line.StartsWith("f ", StringComparison.Ordinal))
                    {
                        string[] parts = line.Split(' ');
                        triangles.Add(ParseFaceIndex(parts[1]));
                        triangles.Add(ParseFaceIndex(parts[2]));
                        triangles.Add(ParseFaceIndex(parts[3]));
                    }
                }
            }

            if (vertices.Count != uvs.Count || vertices.Count != normals.Count)
            {
                throw new InvalidDataException(
                    $"OBJ attribute count mismatch in {path}: "
                    + $"v={vertices.Count} vt={uvs.Count} vn={normals.Count}");
            }

            var mesh = new Mesh
            {
                name = "EDC_Optimization_" + Path.GetFileNameWithoutExtension(path),
                indexFormat = IndexFormat.UInt32
            };
            mesh.SetVertices(vertices);
            mesh.SetUVs(0, uvs);
            mesh.SetNormals(normals);
            mesh.SetTriangles(triangles, 0, true);
            if (string.Equals(
                Environment.GetEnvironmentVariable("EDC_OPT_RECALCULATE_NORMALS"),
                "1",
                StringComparison.Ordinal))
            {
                mesh.RecalculateNormals();
            }
            mesh.RecalculateTangents();
            return mesh;
        }

        private static float ParseFloat(string text)
        {
            return float.Parse(text, NumberStyles.Float, CultureInfo.InvariantCulture);
        }

        private static int ParseFaceIndex(string text)
        {
            int slash = text.IndexOf('/');
            string index = slash >= 0 ? text.Substring(0, slash) : text;
            return int.Parse(index, NumberStyles.Integer, CultureInfo.InvariantCulture) - 1;
        }

        private static Vector3 ToVector3(float[] values)
        {
            return new Vector3(values[0], values[1], values[2]);
        }

        [Serializable]
        private sealed class LayerManifest
        {
            public int totalRuntimeTriangles;
            public LayerEntry[] layers;
        }

        [Serializable]
        private sealed class LayerEntry
        {
            public string name;
            public float[] pivotPosition;
        }
    }
}
