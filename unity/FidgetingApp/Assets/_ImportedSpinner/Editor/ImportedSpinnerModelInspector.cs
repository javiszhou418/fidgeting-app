using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.ImportedSpinner.EditorTools
{
    public static class ImportedSpinnerModelInspector
    {
        private const string ModelPath =
            "Assets/_ImportedSpinner/Models/ImportedSpinner.fbx";
        private const string SimplificationSourcePath =
            "/tmp/fidgeting_imported_spinner_source.obj";
        private const string TextureFolder =
            "Assets/_ImportedSpinner/Textures";

        [MenuItem("Tools/Codex/Prepare Imported Spinner Textured Runtime Source")]
        public static void PrepareTexturedRuntimeSource()
        {
            ExtractPbrTextures();
            ExportSimplificationSource();
            Report();
        }

        [MenuItem("Tools/Codex/Extract Imported Spinner PBR Textures")]
        public static void ExtractPbrTextures()
        {
            EnsureAssetFolder(TextureFolder);
            ModelImporter importer = AssetImporter.GetAtPath(ModelPath) as ModelImporter;
            if (importer == null)
            {
                throw new FileNotFoundException("The supplied FBX importer is missing.", ModelPath);
            }

            bool extracted = importer.ExtractTextures(TextureFolder);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            string[] texturePaths = AssetDatabase.FindAssets("t:Texture2D", new[] { TextureFolder })
                .Select(AssetDatabase.GUIDToAssetPath)
                .OrderBy(path => path)
                .ToArray();
            if (texturePaths.Length < 4)
            {
                throw new InvalidDataException(
                    $"Expected four embedded PBR textures, found {texturePaths.Length}. "
                    + $"ExtractTextures returned {extracted}.");
            }

            Debug.Log(
                $"[ImportedSpinnerTextures] extracted={extracted} count={texturePaths.Length}\n"
                + string.Join("\n", texturePaths));
        }

        [MenuItem("Tools/Codex/Export Imported Spinner Simplification Source")]
        public static void ExportSimplificationSource()
        {
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
            {
                throw new FileNotFoundException(
                    "Unity could not load the supplied spinner FBX.",
                    ModelPath);
            }

            GameObject instance = Object.Instantiate(model);
            instance.name = "ImportedSpinnerExport";

            try
            {
                MeshFilter[] filters = instance.GetComponentsInChildren<MeshFilter>(true);
                if (filters.Length == 0)
                {
                    throw new InvalidDataException("The supplied FBX contains no mesh filters.");
                }

                var invariant = CultureInfo.InvariantCulture;
                using var writer = new StreamWriter(
                    SimplificationSourcePath,
                    false,
                    new UTF8Encoding(false),
                    1 << 20);
                writer.WriteLine(
                    "# Unity-exported simplification source with original UVs for the third spinner");

                int vertexOffset = 0;
                int triangleCount = 0;
                foreach (MeshFilter filter in filters)
                {
                    Mesh mesh = filter.sharedMesh;
                    if (mesh == null)
                    {
                        continue;
                    }

                    Matrix4x4 localToWorld = filter.transform.localToWorldMatrix;
                    Vector3[] vertices = mesh.vertices;
                    Vector2[] uvs = mesh.uv;
                    if (uvs.Length != vertices.Length)
                    {
                        throw new InvalidDataException(
                            $"Mesh {mesh.name} has {vertices.Length} vertices but {uvs.Length} UVs.");
                    }
                    foreach (Vector3 vertex in vertices)
                    {
                        Vector3 transformed = localToWorld.MultiplyPoint3x4(vertex);
                        writer.Write("v ");
                        writer.Write(transformed.x.ToString("R", invariant));
                        writer.Write(' ');
                        writer.Write(transformed.y.ToString("R", invariant));
                        writer.Write(' ');
                        writer.Write(transformed.z.ToString("R", invariant));
                        writer.WriteLine();
                    }

                    foreach (Vector2 uv in uvs)
                    {
                        writer.Write("vt ");
                        writer.Write(uv.x.ToString("R", invariant));
                        writer.Write(' ');
                        writer.Write(uv.y.ToString("R", invariant));
                        writer.WriteLine();
                    }

                    for (int submesh = 0; submesh < mesh.subMeshCount; submesh++)
                    {
                        int[] indices = mesh.GetTriangles(submesh);
                        for (int index = 0; index < indices.Length; index += 3)
                        {
                            writer.Write("f ");
                            int first = vertexOffset + indices[index] + 1;
                            int second = vertexOffset + indices[index + 2] + 1;
                            int third = vertexOffset + indices[index + 1] + 1;
                            writer.Write(first);
                            writer.Write('/');
                            writer.Write(first);
                            writer.Write(' ');
                            writer.Write(second);
                            writer.Write('/');
                            writer.Write(second);
                            writer.Write(' ');
                            writer.Write(third);
                            writer.Write('/');
                            writer.Write(third);
                            writer.WriteLine();
                            triangleCount++;
                        }
                    }

                    vertexOffset += vertices.Length;
                }

                Debug.Log(
                    $"[ImportedSpinnerExport] path={SimplificationSourcePath} "
                    + $"vertices={vertexOffset} triangles={triangleCount}");
            }
            finally
            {
                Object.DestroyImmediate(instance);
            }
        }

        [MenuItem("Tools/Codex/Inspect Imported Spinner")]
        public static void Report()
        {
            AssetDatabase.ImportAsset(ModelPath, ImportAssetOptions.ForceUpdate);
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
            if (model == null)
            {
                throw new System.IO.FileNotFoundException(
                    "Unity could not import the supplied spinner FBX.",
                    ModelPath);
            }

            GameObject instance = Object.Instantiate(model);
            instance.name = "ImportedSpinnerInspection";

            try
            {
                var report = new StringBuilder(4096);
                report.AppendLine("[ImportedSpinnerInspection] BEGIN");
                AppendTransform(report, instance.transform, 0);

                Renderer[] renderers = instance.GetComponentsInChildren<Renderer>(true);
                Bounds combined = default;
                bool hasBounds = false;
                int vertexCount = 0;
                int triangleCount = 0;

                foreach (Renderer renderer in renderers)
                {
                    if (!hasBounds)
                    {
                        combined = renderer.bounds;
                        hasBounds = true;
                    }
                    else
                    {
                        combined.Encapsulate(renderer.bounds);
                    }

                    Mesh mesh = null;
                    if (renderer.TryGetComponent(out MeshFilter filter))
                    {
                        mesh = filter.sharedMesh;
                    }
                    else if (renderer is SkinnedMeshRenderer skinned)
                    {
                        mesh = skinned.sharedMesh;
                    }

                    if (mesh != null)
                    {
                        vertexCount += mesh.vertexCount;
                        for (int submesh = 0; submesh < mesh.subMeshCount; submesh++)
                        {
                            triangleCount += (int)(mesh.GetIndexCount(submesh) / 3);
                        }
                    }

                    report.Append("RENDERER path=")
                        .Append(GetPath(renderer.transform, instance.transform))
                        .Append(" mesh=").Append(mesh != null ? mesh.name : "none")
                        .Append(" vertices=").Append(mesh != null ? mesh.vertexCount : 0)
                        .Append(" submeshes=").Append(mesh != null ? mesh.subMeshCount : 0)
                        .Append(" uv0=").Append(mesh != null ? mesh.uv.Length : 0)
                        .Append(" materials=").Append(renderer.sharedMaterials.Length)
                        .Append(" boundsCenter=").Append(renderer.bounds.center.ToString("F5"))
                        .Append(" boundsSize=").Append(renderer.bounds.size.ToString("F5"))
                        .AppendLine();

                    foreach (Material material in renderer.sharedMaterials)
                    {
                        report.Append("MATERIAL name=")
                            .Append(material != null ? material.name : "none")
                            .Append(" shader=")
                            .Append(material != null && material.shader != null
                                ? material.shader.name
                                : "none")
                            .AppendLine();
                        if (material == null)
                        {
                            continue;
                        }

                        foreach (string propertyName in material.GetTexturePropertyNames())
                        {
                            Texture texture = material.GetTexture(propertyName);
                            if (texture != null)
                            {
                                report.Append("TEXTURE property=").Append(propertyName)
                                    .Append(" name=").Append(texture.name)
                                    .Append(" path=").Append(AssetDatabase.GetAssetPath(texture))
                                    .AppendLine();
                            }
                        }
                    }
                }

                ModelImporter importer = AssetImporter.GetAtPath(ModelPath) as ModelImporter;
                report.Append("SUMMARY renderers=").Append(renderers.Length)
                    .Append(" vertices=").Append(vertexCount)
                    .Append(" triangles=").Append(triangleCount)
                    .Append(" boundsCenter=").Append(combined.center.ToString("F5"))
                    .Append(" boundsSize=").Append(combined.size.ToString("F5"))
                    .Append(" globalScale=").Append(importer != null ? importer.globalScale : 0f)
                    .Append(" useFileScale=").Append(importer != null && importer.useFileScale)
                    .AppendLine();
                report.AppendLine("[ImportedSpinnerInspection] END");
                Debug.Log(report.ToString());
            }
            finally
            {
                Object.DestroyImmediate(instance);
            }
        }

        private static void AppendTransform(StringBuilder report, Transform transform, int depth)
        {
            report.Append(' ', depth * 2)
                .Append("NODE ").Append(transform.name)
                .Append(" position=").Append(transform.localPosition.ToString("F5"))
                .Append(" rotation=").Append(transform.localEulerAngles.ToString("F3"))
                .Append(" scale=").Append(transform.localScale.ToString("F5"))
                .AppendLine();

            for (int index = 0; index < transform.childCount; index++)
            {
                AppendTransform(report, transform.GetChild(index), depth + 1);
            }
        }

        private static string GetPath(Transform transform, Transform root)
        {
            var path = new StringBuilder(transform.name);
            Transform current = transform.parent;
            while (current != null && current != root)
            {
                path.Insert(0, current.name + "/");
                current = current.parent;
            }

            return path.ToString();
        }

        private static void EnsureAssetFolder(string folderPath)
        {
            string[] segments = folderPath.Split('/');
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
    }
}
