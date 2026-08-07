using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using ThreeBladeEDC.EditorTools;
using ThreeBladeEDC.Presentation;
using Unity.Collections;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ThreeBladeEDC.Tests.Editor
{
    public sealed class BlenderDragonScaleAssetTests
    {
        private const string VisualModelPath =
            "Assets/_Fidgeting/Models/BlenderDragonScale/DragonScaleEDC.fbx";
        private const string CollisionModelPath =
            "Assets/_Fidgeting/Models/BlenderDragonScale/DragonScaleEDC_Collision.fbx";
        private const string DeliveryScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";

        [Test]
        public void DeliveryScene_UsesSelectedOnePieceDragonScaleVisualAndExplodedOrder()
        {
            SceneSetup[] previousSetup = EditorSceneManager.GetSceneManagerSetup();
            try
            {
                Scene scene = EditorSceneManager.OpenScene(
                    DeliveryScenePath,
                    OpenSceneMode.Single);
                Transform root = scene.GetRootGameObjects()
                    .Single(candidate => candidate.name == "ThreeBladeEDC_Root")
                    .transform;

                Transform rotor = RequirePath(root, "RotorDynamic");
                Transform onePieceRotor = RequirePath(
                    rotor,
                    "Rotor_Root/RotorBody_OnePiece");
                var selectedRenderer = onePieceRotor.GetComponent<MeshRenderer>();
                Assert.That(selectedRenderer, Is.Not.Null);
                Assert.That(selectedRenderer.enabled, Is.True);
                Assert.That(
                    AssetDatabase.GetAssetPath(onePieceRotor.GetComponent<MeshFilter>().sharedMesh),
                    Is.EqualTo(VisualModelPath));

                Assert.That(
                    RequirePath(rotor, "ThreeBladeFrame")
                        .GetComponent<MeshRenderer>().enabled,
                    Is.False,
                    "The superseded procedural visual must stay hidden.");
                Assert.That(
                    RequirePath(root, "HubStatic/TopCap/TopCap_Root/FingerCap_Top")
                        .GetComponent<MeshRenderer>().enabled,
                    Is.True);
                Assert.That(
                    RequirePath(root, "BearingVisual/BearingAssembly_Root"),
                    Is.Not.Null);

                Transform cage = RequirePath(root, "BearingVisual/BallCage");
                Assert.That(
                    RequirePath(cage, "BearingBalls").GetComponent<MeshRenderer>().enabled,
                    Is.True,
                    "The batched bearing balls are the only visible cage renderer.");
                Assert.That(
                    cage.Find("BearingCage_Root"),
                    Is.Null,
                    "The ten per-ball import renderers must not remain in the runtime scene.");

                ExplodedViewController exploded =
                    root.GetComponent<ExplodedViewController>();
                Assert.That(exploded, Is.Not.Null);
                SerializedProperty parts = new SerializedObject(exploded)
                    .FindProperty("parts");
                Assert.That(parts.arraySize, Is.EqualTo(6));

                string[] expectedNames =
                {
                    "TopCap",
                    "TopWasher",
                    "BearingVisual",
                    "RotorDynamic",
                    "BottomWasher",
                    "BottomCap",
                };
                float[] expectedOffsets = { 0.043f, 0.024f, 0.010f, 0f, -0.016f, -0.036f };
                for (int index = 0; index < expectedNames.Length; index++)
                {
                    SerializedProperty part = parts.GetArrayElementAtIndex(index);
                    Transform partTransform = part.FindPropertyRelative("transform")
                        .objectReferenceValue as Transform;
                    Vector3 offset = part.FindPropertyRelative("localOffset").vector3Value;
                    Assert.That(partTransform, Is.Not.Null);
                    Assert.That(partTransform.name, Is.EqualTo(expectedNames[index]));
                    Assert.That(offset, Is.EqualTo(Vector3.up * expectedOffsets[index]));
                }

                Rigidbody body = rotor.GetComponent<Rigidbody>();
                Assert.That(body, Is.Not.Null);
                Assert.That(body.angularVelocity, Is.EqualTo(Vector3.zero));
            }
            finally
            {
                if (previousSetup != null && previousSetup.Any(setup => setup.isLoaded))
                {
                    EditorSceneManager.RestoreSceneManagerSetup(previousSetup);
                }
                else
                {
                    EditorSceneManager.NewScene(
                        NewSceneSetup.EmptyScene,
                        NewSceneMode.Single);
                }
            }
        }

        [Test]
        public void VisualAsset_PreservesReferenceHierarchyAndRealScale()
        {
            GameObject asset = AssetDatabase.LoadAssetAtPath<GameObject>(VisualModelPath);
            Assert.That(asset, Is.Not.Null, $"Missing model: {VisualModelPath}");

            GameObject instance = UnityEngine.Object.Instantiate(asset);
            try
            {
                Transform[] transforms = instance.GetComponentsInChildren<Transform>(true);
                AssertNamedTransform(transforms, "DragonScaleEDC_Root");
                AssertNamedTransform(transforms, "Rotor_Root");
                AssertNamedTransform(transforms, "Fixed_Root");
                AssertNamedTransform(transforms, "BearingAssembly_Root");
                AssertNamedTransform(transforms, "BearingCage_Root");
                AssertNamedTransform(transforms, "RotorBody_OnePiece");
                AssertNamedTransform(transforms, "TopCap_Root");
                AssertNamedTransform(transforms, "TopWasher_Root");
                AssertNamedTransform(transforms, "BottomWasher_Root");
                AssertNamedTransform(transforms, "BottomCap_Root");
                AssertNamedTransform(transforms, "FingerCap_Top");
                AssertNamedTransform(transforms, "FingerCap_Bottom");

                Assert.That(
                    transforms.Count(transform => transform.name.StartsWith(
                        "DragonBlade_",
                        StringComparison.Ordinal)),
                    Is.Zero,
                    "The reference rotor is one carrier, not three detached shield meshes.");
                Assert.That(
                    transforms.Count(transform => transform.name.StartsWith(
                        "BladePocketFloor_",
                        StringComparison.Ordinal)),
                    Is.EqualTo(3));
                Assert.That(
                    transforms.Count(transform => transform.name.StartsWith(
                        "BladePocketInlay_",
                        StringComparison.Ordinal)),
                    Is.EqualTo(3));
                Assert.That(
                    transforms.Count(transform => transform.name.StartsWith(
                        "BearingBall_",
                        StringComparison.Ordinal)),
                    Is.EqualTo(10));

                Bounds bounds = CalculateExactVertexBounds(instance);
                float planarDiameter = Mathf.Max(bounds.size.x, bounds.size.z);
                Assert.That(
                    planarDiameter,
                    Is.InRange(0.083f, 0.0855f),
                    "Dragon Scale FBX must keep the reference-matched compact 84 mm-class blade proportions.");
                Assert.That(
                    bounds.size.y,
                    Is.InRange(0.016f, 0.018f),
                    "Blender Z must export as Unity Y with the reference side profile intact.");

                Assert.That(instance.GetComponentInChildren<Rigidbody>(true), Is.Null);
                Assert.That(instance.GetComponentInChildren<Animator>(true), Is.Null);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }

        [Test]
        public void VisibleCircularParts_UseRetinaReadySilhouettesAndCalmCapNormals()
        {
            GameObject asset = AssetDatabase.LoadAssetAtPath<GameObject>(VisualModelPath);
            Assert.That(asset, Is.Not.Null, $"Missing model: {VisualModelPath}");

            GameObject instance = UnityEngine.Object.Instantiate(asset);
            try
            {
                Transform[] transforms = instance.GetComponentsInChildren<Transform>(true);
                AssertSilhouetteSamples(transforms, "FingerCap_Top", 120);
                AssertSilhouetteSamples(transforms, "FingerCapTop_BrushedFace", 120);
                AssertSilhouetteSamples(transforms, "RotorCrownTrim", 120);
                AssertSilhouetteSamples(transforms, "BearingOuterRace", 66);
                AssertSilhouetteSamples(transforms, "TopWasher", 66);
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }

            Material cap = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_Fidgeting/Generated/Materials/M_CapRadialBrushed.mat");
            Assert.That(cap, Is.Not.Null);
            Assert.That(cap.HasProperty("_BumpScale"), Is.True);
            Assert.That(
                cap.GetFloat("_BumpScale"),
                Is.EqualTo(0.10f).Within(0.0001f),
                "The close-up cap normal must stay below the old sparkling 0.18 setting.");
        }

        [Test]
        public void CollisionAsset_ContainsThreeDragonBladesAndHub()
        {
            GameObject asset = AssetDatabase.LoadAssetAtPath<GameObject>(CollisionModelPath);
            Assert.That(asset, Is.Not.Null, $"Missing model: {CollisionModelPath}");
            Transform[] transforms = asset.GetComponentsInChildren<Transform>(true);
            AssertNamedTransform(transforms, "Collision_Root");
            AssertNamedTransform(transforms, "COL_Hub");
            Assert.That(
                transforms
                    .Where(transform => transform.name.StartsWith(
                        "COL_DragonBlade_",
                        StringComparison.Ordinal))
                    .Select(transform => transform.name)
                    .OrderBy(name => name, StringComparer.Ordinal),
                Is.EqualTo(new[]
                {
                    "COL_DragonBlade_01",
                    "COL_DragonBlade_02",
                    "COL_DragonBlade_03",
                }));
        }

        [Test]
        public void FbxImporters_UseCanonicalScaleAndNoDccRuntimeData()
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

        private static void AssertSilhouetteSamples(
            Transform[] transforms,
            string name,
            int minimumSamples)
        {
            Transform target = transforms.Single(transform => transform.name == name);
            Mesh mesh = target.GetComponent<MeshFilter>()?.sharedMesh;
            Assert.That(mesh, Is.Not.Null, $"{name} has no imported MeshFilter mesh.");

            using (Mesh.MeshDataArray data = Mesh.AcquireReadOnlyMeshData(mesh))
            using (var vertices = new NativeArray<Vector3>(
                       mesh.vertexCount,
                       Allocator.Temp,
                       NativeArrayOptions.UninitializedMemory))
            {
                data[0].GetVertices(vertices);
                float maximumRadius = 0f;
                for (int index = 0; index < vertices.Length; index++)
                {
                    Vector3 point = target.TransformPoint(vertices[index]);
                    Vector2 planar = new Vector2(
                        point.x - target.position.x,
                        point.z - target.position.z);
                    maximumRadius = Mathf.Max(maximumRadius, planar.magnitude);
                }

                var angles = new HashSet<int>();
                for (int index = 0; index < vertices.Length; index++)
                {
                    Vector3 point = target.TransformPoint(vertices[index]);
                    Vector2 planar = new Vector2(
                        point.x - target.position.x,
                        point.z - target.position.z);
                    if (planar.magnitude < maximumRadius * 0.985f)
                    {
                        continue;
                    }

                    angles.Add(Mathf.RoundToInt(
                        Mathf.Atan2(planar.y, planar.x) * Mathf.Rad2Deg * 10f));
                }

                Assert.That(
                    angles.Count,
                    Is.GreaterThanOrEqualTo(minimumSamples),
                    $"{name} regressed to a visibly faceted {angles.Count}-sample silhouette.");
            }
        }

        private static Transform RequirePath(Transform root, string path)
        {
            Transform result = root.Find(path);
            Assert.That(result, Is.Not.Null, $"Missing scene object: {root.name}/{path}");
            return result;
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
