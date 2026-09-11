using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.DisplayCase.Tests.Editor
{
    public sealed class PremiumDisplayCaseGate11ParityTests
    {
        private const string CandidateRoot =
            "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001";
        private const string FbxPath =
            CandidateRoot + "/Models/PremiumDisplayCaseGate11R001.fbx";
        private const string PrefabPath =
            CandidateRoot + "/Prefabs/PresentationRoot.prefab";
        private const string ScenePath =
            CandidateRoot + "/Scenes/PremiumDisplayCaseGate11Parity.unity";
        private const string ApprovedFbxSha256 =
            "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae";

        [Test]
        public void CandidateFbx_IsByteIdenticalToApprovedGate10Authority()
        {
            Assert.That(Sha256File(FbxPath), Is.EqualTo(ApprovedFbxSha256));
            Assert.That(
                AssetDatabase.GetAssetPath(
                    AssetDatabase.LoadAssetAtPath<GameObject>(FbxPath)),
                Is.EqualTo(FbxPath));
        }

        [Test]
        public void CandidatePrefab_PreservesApprovedHierarchyAndEmptyContentSlot()
        {
            GameObject prefab = LoadPrefab();
            Transform[] transforms = prefab.GetComponentsInChildren<Transform>(true);
            Assert.That(prefab.name, Is.EqualTo("PresentationRoot"));
            Assert.That(transforms.Length, Is.EqualTo(12));
            AssertParent(transforms, "CaseAssembly", "PresentationRoot");
            AssertParent(transforms, "RearPolycarbonateShell", "CaseAssembly");
            AssertParent(
                transforms,
                "TactileBackgroundInsert",
                "RearPolycarbonateShell");
            AssertParent(transforms, "ContentSlot", "RearPolycarbonateShell");
            AssertParent(transforms, "FrontPolycarbonateShell", "CaseAssembly");
            AssertParent(
                transforms,
                "ContinuousTubePerimeter",
                "FrontPolycarbonateShell");
            AssertParent(transforms, "PhysicalLabel", "FrontPolycarbonateShell");
            AssertParent(transforms, "LogoZone", "PhysicalLabel");
            AssertParent(transforms, "AchievementZone", "PhysicalLabel");
            AssertParent(transforms, "NarrowFoil", "PhysicalLabel");
            AssertParent(
                transforms,
                "TransparentCover",
                "FrontPolycarbonateShell");
            Assert.That(
                transforms.Single(item => item.name == "ContentSlot").childCount,
                Is.Zero);
        }

        [Test]
        public void CandidateGeometry_PreservesBoundsPivotAndTriangleCount()
        {
            GameObject instance = UnityEngine.Object.Instantiate(LoadPrefab());
            try
            {
                instance.transform.position = Vector3.zero;
                Bounds bounds = CombinedBounds(
                    instance.GetComponentsInChildren<MeshRenderer>(true));
                Assert.That(bounds.size.x, Is.EqualTo(0.228f).Within(0.000001f));
                Assert.That(bounds.size.y, Is.EqualTo(0.304f).Within(0.000001f));
                Assert.That(bounds.size.z, Is.EqualTo(0.059f).Within(0.000001f));
                Assert.That(instance.transform.position, Is.EqualTo(Vector3.zero));
                Assert.That(instance.transform.lossyScale, Is.EqualTo(Vector3.one));
                int triangles = instance.GetComponentsInChildren<MeshFilter>(true)
                    .Sum(filter => filter.sharedMesh.triangles.Length / 3);
                Assert.That(triangles, Is.EqualTo(100016));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }

        [Test]
        public void CandidateGeometry_PreservesImportedNormalsAndWinding()
        {
            GameObject instance = UnityEngine.Object.Instantiate(LoadPrefab());
            try
            {
                int tested = 0;
                int agreeing = 0;
                foreach (MeshFilter filter in
                         instance.GetComponentsInChildren<MeshFilter>(true))
                {
                    Mesh mesh = filter.sharedMesh;
                    Vector3[] vertices = mesh.vertices;
                    Vector3[] normals = mesh.normals;
                    int[] triangles = mesh.triangles;
                    for (int index = 0; index < triangles.Length; index += 3)
                    {
                        int first = triangles[index];
                        int second = triangles[index + 1];
                        int third = triangles[index + 2];
                        Vector3 face = Vector3.Cross(
                            vertices[second] - vertices[first],
                            vertices[third] - vertices[first]);
                        Assert.That(
                            face.sqrMagnitude,
                            Is.GreaterThan(0.000000000000000000000001f));
                        Vector3 normal =
                            normals[first] + normals[second] + normals[third];
                        tested++;
                        if (Vector3.Dot(face, normal) > 0f)
                        {
                            agreeing++;
                        }
                    }
                }
                Assert.That((float)agreeing / tested, Is.GreaterThanOrEqualTo(0.99999f));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance);
            }
        }

        [Test]
        public void CandidateMaterials_PreserveZonesAndTransparentSortOrder()
        {
            MeshRenderer[] renderers =
                LoadPrefab().GetComponentsInChildren<MeshRenderer>(true);
            AssertMaterial(renderers, "RearPolycarbonateShell", "Gate11RearFrosted");
            AssertMaterial(
                renderers,
                "TactileBackgroundInsert",
                "Gate11BlackFlocking");
            AssertMaterial(
                renderers,
                "FrontPolycarbonateShell",
                "Gate11FrontFrosted");
            AssertMaterial(
                renderers,
                "ContinuousTubePerimeter",
                "Gate11ConnectedTube");
            AssertMaterial(renderers, "PhysicalLabel", "Gate11RuntimeLabel");

            MeshRenderer rear = renderers.Single(item =>
                item.name == "RearPolycarbonateShell");
            MeshRenderer front = renderers.Single(item =>
                item.name == "FrontPolycarbonateShell");
            MeshRenderer tube = renderers.Single(item =>
                item.name == "ContinuousTubePerimeter");
            Assert.That(
                rear.sharedMaterial.shader.name,
                Is.EqualTo("FidgetingApp/Gate11MeshClippedFrosted"));
            Assert.That(
                rear.sharedMaterial.renderQueue,
                Is.LessThan(front.sharedMaterial.renderQueue));
            Assert.That(
                front.sharedMaterial.renderQueue,
                Is.LessThan(tube.sharedMaterial.renderQueue));
            Assert.That(rear.sortingOrder, Is.LessThan(front.sortingOrder));
            Assert.That(front.sortingOrder, Is.LessThan(tube.sortingOrder));
        }

        [Test]
        public void CandidatePrefab_ContainsNoTextToyProxyExplodeOrAnimation()
        {
            GameObject prefab = LoadPrefab();
            Transform[] transforms = prefab.GetComponentsInChildren<Transform>(true);
            Assert.That(prefab.GetComponentsInChildren<TextMesh>(true), Is.Empty);
            Assert.That(prefab.GetComponentsInChildren<Animator>(true), Is.Empty);
            Assert.That(prefab.GetComponentsInChildren<Animation>(true), Is.Empty);
            Assert.That(prefab.GetComponentsInChildren<Light>(true), Is.Empty);
            Assert.That(prefab.GetComponentsInChildren<Collider>(true), Is.Empty);
            foreach (Transform transform in transforms)
            {
                string lowered = transform.name.ToLowerInvariant();
                Assert.That(lowered, Does.Not.Contain("toy"));
                Assert.That(lowered, Does.Not.Contain("prize"));
                Assert.That(lowered, Does.Not.Contain("proxy"));
                Assert.That(lowered, Does.Not.Contain("explode"));
                Assert.That(lowered, Does.Not.Contain("placeholder"));
            }
        }

        [Test]
        public void ParityScene_UsesNoPointLightOrExternalHalo()
        {
            Scene previous = SceneManager.GetActiveScene();
            Scene scene = EditorSceneManager.OpenScene(
                ScenePath,
                OpenSceneMode.Single);
            Light[] lights = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Light>(true))
                .ToArray();
            Transform[] transforms = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Transform>(true))
                .ToArray();
            Assert.That(lights, Has.Length.EqualTo(3));
            Assert.That(lights.Select(light => light.type),
                Has.All.EqualTo(LightType.Directional));
            Assert.That(
                transforms.Any(transform => transform.name.IndexOf(
                    "halo",
                    StringComparison.OrdinalIgnoreCase) >= 0),
                Is.False);
            Assert.That(
                transforms.Count(transform =>
                    transform.name == "PresentationRoot"),
                Is.EqualTo(1));
            _ = previous;
        }

        [Test]
        public void ShippingPrefabSceneAndModel_RemainUnchanged()
        {
            Assert.That(
                Sha256File("Assets/Resources/Gacha/PremiumDisplayCase.prefab"),
                Is.EqualTo(
                    "88cf4f4a369cae1f370e5c47cebf6d1119d2698fcd0f4de70095314c5993a811"));
            Assert.That(
                Sha256File("Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity"),
                Is.EqualTo(
                    "f83df832a7f1f7b057b59abfdba2528c0bee617b56422887291ac21db6fd8bbb"));
            Assert.That(
                Sha256File("Assets/_DisplayCase/Models/PremiumDisplayCase.fbx"),
                Is.EqualTo(
                    "41c71ffce320acdaa65ea5931b791361695afef88cd091fa9796514ec5c5c819"));
        }

        private static GameObject LoadPrefab()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            Assert.That(prefab, Is.Not.Null, "Run the Gate 11 parity builder first.");
            return prefab;
        }

        private static void AssertParent(
            Transform[] transforms,
            string childName,
            string parentName)
        {
            Transform child = transforms.Single(item => item.name == childName);
            Assert.That(child.parent, Is.Not.Null);
            Assert.That(child.parent.name, Is.EqualTo(parentName));
        }

        private static void AssertMaterial(
            MeshRenderer[] renderers,
            string objectName,
            string materialName)
        {
            MeshRenderer renderer = renderers.Single(item =>
                item.name == objectName);
            Assert.That(renderer.sharedMaterial, Is.Not.Null);
            Assert.That(renderer.sharedMaterial.name, Is.EqualTo(materialName));
        }

        private static Bounds CombinedBounds(MeshRenderer[] renderers)
        {
            Assert.That(renderers, Is.Not.Empty);
            Bounds bounds = renderers[0].bounds;
            for (int index = 1; index < renderers.Length; index++)
            {
                bounds.Encapsulate(renderers[index].bounds);
            }
            return bounds;
        }

        private static string Sha256File(string assetPath)
        {
            string absolute = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                assetPath));
            using SHA256 sha = SHA256.Create();
            using FileStream stream = File.OpenRead(absolute);
            byte[] digest = sha.ComputeHash(stream);
            var builder = new StringBuilder(digest.Length * 2);
            foreach (byte value in digest)
            {
                builder.Append(value.ToString("x2"));
            }
            return builder.ToString();
        }
    }
}
