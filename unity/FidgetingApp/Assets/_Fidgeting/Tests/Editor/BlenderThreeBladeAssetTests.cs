using System;
using System.Linq;
using NUnit.Framework;
using ThreeBladeEDC.EditorTools;
using Unity.Collections;
using UnityEditor;
using UnityEngine;

namespace ThreeBladeEDC.Tests.Editor
{
    public sealed class BlenderThreeBladeAssetTests
    {
        private const string VisualModelPath =
            "Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner.fbx";
        private const string CollisionModelPath =
            "Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner_Collision.fbx";

        [Test]
        public void BlenderVisualAsset_PreservesMechanicalHierarchyAtMeterScale()
        {
            GameObject asset = AssetDatabase.LoadAssetAtPath<GameObject>(VisualModelPath);
            Assert.That(asset, Is.Not.Null, $"Missing model: {VisualModelPath}");

            GameObject instance = UnityEngine.Object.Instantiate(asset);
            try
            {
                Transform[] transforms = instance.GetComponentsInChildren<Transform>(true);
                AssertNamedTransform(transforms, "ThreeBladeSpinner_Root");
                AssertNamedTransform(transforms, "Rotor_Root");
                AssertNamedTransform(transforms, "Fixed_Root");
                AssertNamedTransform(transforms, "BearingCage_Root");

                Transform[] blades = transforms
                    .Where(transform => transform.name.StartsWith(
                        "BladeShell_",
                        StringComparison.Ordinal))
                    .OrderBy(transform => transform.name, StringComparer.Ordinal)
                    .ToArray();
                Assert.That(
                    blades.Select(blade => blade.name),
                    Is.EqualTo(new[] { "BladeShell_01", "BladeShell_02", "BladeShell_03" }));
                Assert.That(
                    transforms.Count(transform => transform.name.StartsWith(
                        "BearingBall_",
                        StringComparison.Ordinal)),
                    Is.EqualTo(10));

                Bounds bounds = CalculateExactVertexBounds(instance);

                float planarDiameter = Mathf.Max(bounds.size.x, bounds.size.z);
                Assert.That(
                    planarDiameter,
                    Is.InRange(0.086f, 0.089f),
                    "The FBX must remain a real-size 87 mm-class EDC model.");
                Assert.That(
                    bounds.size.y,
                    Is.InRange(0.015f, 0.017f),
                    "The exported Blender Z axis must become Unity's Y spin axis.");

                Assert.That(instance.GetComponentInChildren<Rigidbody>(true), Is.Null);
                Assert.That(instance.GetComponentInChildren<Animator>(true), Is.Null);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }

        [Test]
        public void BlenderCollisionAsset_ContainsThreeBladesAndHub()
        {
            GameObject asset = AssetDatabase.LoadAssetAtPath<GameObject>(CollisionModelPath);
            Assert.That(asset, Is.Not.Null, $"Missing model: {CollisionModelPath}");
            Transform[] transforms = asset.GetComponentsInChildren<Transform>(true);
            AssertNamedTransform(transforms, "Collision_Root");
            AssertNamedTransform(transforms, "COL_Hub");
            Assert.That(
                transforms
                    .Where(transform => transform.name.StartsWith(
                        "COL_Blade_",
                        StringComparison.Ordinal))
                    .Select(transform => transform.name)
                    .OrderBy(name => name, StringComparer.Ordinal),
                Is.EqualTo(new[] { "COL_Blade_01", "COL_Blade_02", "COL_Blade_03" }));
        }

        [Test]
        public void BlenderFbxImporters_UseCanonicalScaleAndNoDccRuntimeData()
        {
            foreach (string path in new[] { VisualModelPath, CollisionModelPath })
            {
                var importer = AssetImporter.GetAtPath(path) as ModelImporter;
                Assert.That(importer, Is.Not.Null, $"{path} is not handled by FBXImporter.");
                Assert.That(importer.globalScale, Is.EqualTo(1f));
                Assert.That(importer.useFileScale, Is.True);
                Assert.That(importer.preserveHierarchy, Is.True);
                Assert.That(importer.importAnimation, Is.False);
                Assert.That(importer.importCameras, Is.False);
                Assert.That(importer.importLights, Is.False);
                Assert.That(importer.isReadable, Is.False);
            }
        }

        private static void AssertNamedTransform(Transform[] transforms, string name)
        {
            Assert.That(
                transforms.Any(transform => transform.name == name),
                Is.True,
                $"Imported hierarchy is missing {name}.");
        }

        private static Bounds CalculateExactVertexBounds(GameObject instance)
        {
            bool hasVertex = false;
            Vector3 minimum = Vector3.positiveInfinity;
            Vector3 maximum = Vector3.negativeInfinity;
            MeshFilter[] filters = instance.GetComponentsInChildren<MeshFilter>(true);
            Assert.That(filters, Is.Not.Empty, "Imported FBX contains no meshes.");

            foreach (MeshFilter filter in filters)
            {
                Mesh mesh = filter.sharedMesh;
                Assert.That(mesh, Is.Not.Null, $"{filter.name} has no shared mesh.");
                using (Mesh.MeshDataArray data = Mesh.AcquireReadOnlyMeshData(mesh))
                using (var vertices = new NativeArray<Vector3>(
                           mesh.vertexCount,
                           Allocator.Temp,
                           NativeArrayOptions.UninitializedMemory))
                {
                    data[0].GetVertices(vertices);
                    foreach (Vector3 vertex in vertices)
                    {
                        Vector3 world = filter.transform.TransformPoint(vertex);
                        minimum = Vector3.Min(minimum, world);
                        maximum = Vector3.Max(maximum, world);
                        hasVertex = true;
                    }
                }
            }

            Assert.That(hasVertex, Is.True, "Imported FBX meshes contain no vertices.");
            return new Bounds((minimum + maximum) * 0.5f, maximum - minimum);
        }
    }
}
