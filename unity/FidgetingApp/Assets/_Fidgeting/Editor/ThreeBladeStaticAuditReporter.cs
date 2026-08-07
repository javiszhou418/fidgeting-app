using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Profiling;

namespace ThreeBladeEDC.EditorTools
{
    /// <summary>
    /// Read-only source for the static part of the iPhone rendering checklist.
    /// Dynamic frame time, phys_footprint, available memory and thermal state
    /// still require a Development Build running on an actual iPhone.
    /// </summary>
    public static class ThreeBladeStaticAuditReporter
    {
        private const string ScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        private const string TextureFolder =
            "Assets/_Fidgeting/Generated/Textures";

        [Serializable]
        private sealed class StaticAudit
        {
            public string scene;
            public int visibleRenderers;
            public long visibleVertices;
            public long visibleTriangles;
            public int estimatedDrawCalls;
            public int distinctMaterials;
            public int meshColliders;
            public int convexMeshColliders;
            public int generatedTextures;
            public long generatedTextureBytes;
        }

        [MenuItem("Fidgeting/Three-Blade/Log Static iPhone Audit")]
        public static void LogStaticAudit()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

            MeshRenderer[] renderers = UnityEngine.Object
                .FindObjectsByType<MeshRenderer>(
                    FindObjectsInactive.Exclude,
                    FindObjectsSortMode.None)
                .Where(renderer => renderer.enabled)
                .ToArray();

            long vertices = 0;
            long triangles = 0;
            int drawCalls = 0;
            var materials = new HashSet<Material>();

            foreach (MeshRenderer renderer in renderers)
            {
                MeshFilter filter = renderer.GetComponent<MeshFilter>();
                Mesh mesh = filter != null ? filter.sharedMesh : null;
                if (mesh == null)
                {
                    continue;
                }

                vertices += mesh.vertexCount;
                for (int subMesh = 0; subMesh < mesh.subMeshCount; subMesh++)
                {
                    triangles += (long)mesh.GetIndexCount(subMesh) / 3L;
                }

                drawCalls += mesh.subMeshCount;
                foreach (Material material in renderer.sharedMaterials)
                {
                    if (material != null)
                    {
                        materials.Add(material);
                    }
                }
            }

            MeshCollider[] colliders = UnityEngine.Object.FindObjectsByType<MeshCollider>(
                FindObjectsInactive.Exclude,
                FindObjectsSortMode.None);

            string[] textureGuids = AssetDatabase.FindAssets(
                "t:Texture",
                new[] { TextureFolder });
            long textureBytes = 0;
            foreach (string guid in textureGuids)
            {
                Texture texture = AssetDatabase.LoadAssetAtPath<Texture>(
                    AssetDatabase.GUIDToAssetPath(guid));
                if (texture != null)
                {
                    textureBytes += Profiler.GetRuntimeMemorySizeLong(texture);
                }
            }

            var audit = new StaticAudit
            {
                scene = ScenePath,
                visibleRenderers = renderers.Length,
                visibleVertices = vertices,
                visibleTriangles = triangles,
                estimatedDrawCalls = drawCalls,
                distinctMaterials = materials.Count,
                meshColliders = colliders.Length,
                convexMeshColliders = colliders.Count(collider => collider.convex),
                generatedTextures = textureGuids.Length,
                generatedTextureBytes = textureBytes
            };

            Debug.Log("THREE_BLADE_STATIC_AUDIT " + JsonUtility.ToJson(audit));
        }
    }
}
