using System;
using System.IO;
using System.Linq;
using FidgetingApp.TwoLobeBar.Geometry;
using NUnit.Framework;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FidgetingApp.TwoLobeBar.Tests.Editor
{
    public sealed class TwoLobeBarStaticAcceptanceTests
    {
        private SceneSetup[] previousSceneSetup;
        private Transform root;

        [SetUp]
        public void OpenDeliveryScene()
        {
            previousSceneSetup = EditorSceneManager.GetSceneManagerSetup();
            SceneAsset sceneAsset = AssetDatabase.LoadAssetAtPath<SceneAsset>(
                TwoLobeBarSpecifications.ScenePath);
            Assert.That(sceneAsset, Is.Not.Null);

            Scene scene = EditorSceneManager.OpenScene(
                TwoLobeBarSpecifications.ScenePath,
                OpenSceneMode.Single);
            root = scene.GetRootGameObjects()
                .Single(candidate => candidate.name == "TwoLobeBar_Root")
                .transform;
        }

        [TearDown]
        public void RestoreScenes()
        {
            if (previousSceneSetup != null
                && previousSceneSetup.Any(setup => setup.isLoaded))
            {
                EditorSceneManager.RestoreSceneManagerSetup(previousSceneSetup);
                return;
            }

            EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
        }

        [Test]
        public void DimensionsAndPbrValues_MatchTheAuthoredSpecification()
        {
            Assert.That(TwoLobeBarSpecifications.BodyLength, Is.EqualTo(0.050f));
            Assert.That(TwoLobeBarSpecifications.BodyWidth, Is.EqualTo(0.018f));
            Assert.That(TwoLobeBarSpecifications.BodyThickness, Is.EqualTo(0.013f));
            Assert.That(TwoLobeBarSpecifications.EdgeFilletRadius, Is.EqualTo(0.0035f));
            Assert.That(TwoLobeBarSpecifications.EndTransitionLength, Is.EqualTo(0.0035f));
            Assert.That(TwoLobeBarSpecifications.EndFaceInset, Is.EqualTo(0.0023f));
            Assert.That(TwoLobeBarSpecifications.ButtonDiameter, Is.EqualTo(0.024f));
            Assert.That(TwoLobeBarSpecifications.ButtonProudHeight, Is.EqualTo(0.003f));
            Assert.That(TwoLobeBarSpecifications.ButtonDishDepth, Is.EqualTo(0.0015f));
            Assert.That(TwoLobeBarSpecifications.Metallic, Is.EqualTo(1f));
            Assert.That(TwoLobeBarSpecifications.OffsetFromCollinearDegrees, Is.Zero);
            Assert.That(TwoLobeBarSpecifications.Roughness, Is.EqualTo(0.76f));
            Assert.That(
                TwoLobeBarSpecifications.Smoothness,
                Is.EqualTo(0.24f).Within(0.0001f));
        }

        [Test]
        public void ProceduralMeshes_PreserveContinuousBarAndConcaveDishBounds()
        {
            Mesh body = TwoLobeBarMeshFactory.CreateBody("AcceptanceBody");
            Mesh button = TwoLobeBarMeshFactory.CreateConcaveButton("AcceptanceButton");
            try
            {
                Assert.That(
                    body.bounds.size.x,
                    Is.EqualTo(TwoLobeBarSpecifications.BodyWidth).Within(0.00005f));
                Assert.That(
                    body.bounds.size.y,
                    Is.EqualTo(TwoLobeBarSpecifications.BodyThickness).Within(0.00005f));
                Assert.That(
                    body.bounds.size.z,
                    Is.EqualTo(TwoLobeBarSpecifications.BodyLength).Within(0.00005f));
                Assert.That(
                    body.vertices.Select(vertex => vertex.y).Distinct().Count(),
                    Is.GreaterThan(8),
                    "The crowned body must roll continuously into the side wall.");

                Assert.That(
                    button.bounds.size.x,
                    Is.EqualTo(TwoLobeBarSpecifications.ButtonDiameter).Within(0.00005f));
                Assert.That(
                    button.bounds.size.z,
                    Is.EqualTo(TwoLobeBarSpecifications.ButtonDiameter).Within(0.00005f));
                Assert.That(
                    button.bounds.size.y,
                    Is.EqualTo(TwoLobeBarSpecifications.ButtonProudHeight).Within(0.00005f));

                float dishCenterHeight = button.vertices
                    .Where(vertex => new Vector2(vertex.x, vertex.z).sqrMagnitude < 1e-12f)
                    .Max(vertex => vertex.y);
                Assert.That(
                    button.bounds.max.y - dishCenterHeight,
                    Is.EqualTo(TwoLobeBarSpecifications.ButtonDishDepth).Within(0.00005f));

                AssertFinite(body);
                AssertFinite(button);
                int totalTriangles = body.triangles.Length / 3
                    + button.triangles.Length / 3;
                Assert.That(totalTriangles, Is.LessThan(10000));
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(body);
                UnityEngine.Object.DestroyImmediate(button);
            }
        }

        [Test]
        public void Scene_HasOneContinuousBarStationaryButtonAndCanonicalInteraction()
        {
            Transform rotor = Require("RotorDynamic");
            Transform hub = Require("HubStatic");
            Transform bodyVisual = Require(rotor, "Body");
            Transform topButton = Require(hub, "TopButton");
            Transform bottomButton = Require(hub, "BottomButton");

            Assert.That(bodyVisual.GetComponent<BoxCollider>(), Is.Not.Null);
            Assert.That(rotor.Find("Lobe_A"), Is.Null);
            Assert.That(rotor.Find("Lobe_B"), Is.Null);
            Assert.That(topButton.GetComponent<SpinnerTouchSurface>(), Is.Not.Null);
            Assert.That(topButton.GetComponent<BoxCollider>(), Is.Not.Null);
            Assert.That(
                Quaternion.Angle(
                    bottomButton.localRotation,
                    Quaternion.Euler(180f, 0f, 0f)),
                Is.LessThan(0.05f));

            RotorRigidbodyController controller =
                rotor.GetComponent<RotorRigidbodyController>();
            Rigidbody body = rotor.GetComponent<Rigidbody>();
            Assert.That(controller, Is.Not.Null);
            Assert.That(root.GetComponent<MobileGestureController>(), Is.Not.Null);
            Assert.That(body, Is.Not.Null);
            Assert.That(body.angularVelocity, Is.EqualTo(Vector3.zero));
            Assert.That(body.linearVelocity, Is.EqualTo(Vector3.zero));
            Assert.That(topButton.IsChildOf(rotor), Is.False);
            Assert.That(bottomButton.IsChildOf(rotor), Is.False);
        }

        [Test]
        public void MaterialAndStudio_UseGraphiteBeadBlastAndOneSoftKey()
        {
            Transform bodyVisual = Require(Require("RotorDynamic"), "Body");
            Transform topButton = Require(Require("HubStatic"), "TopButton");
            Material material = bodyVisual.GetComponent<MeshRenderer>().sharedMaterial;
            Assert.That(material, Is.Not.Null);
            Assert.That(material.name, Is.EqualTo("M_TwoLobeGraphite"));
            Assert.That(material.GetFloat("_Metallic"), Is.EqualTo(1f).Within(0.0001f));
            Assert.That(
                material.GetFloat("_Smoothness"),
                Is.EqualTo(TwoLobeBarSpecifications.Smoothness).Within(0.0001f));
            Color color = material.GetColor("_BaseColor");
            Color expected = TwoLobeBarSpecifications.BodyBaseColor;
            Assert.That(color.r, Is.EqualTo(expected.r).Within(0.002f));
            Assert.That(color.g, Is.EqualTo(expected.g).Within(0.002f));
            Assert.That(color.b, Is.EqualTo(expected.b).Within(0.002f));
            Texture normal = material.GetTexture("_BumpMap");
            Assert.That(normal, Is.Not.Null);
            TextureImporter importer = AssetImporter.GetAtPath(
                AssetDatabase.GetAssetPath(normal)) as TextureImporter;
            Assert.That(importer, Is.Not.Null);
            Assert.That(importer.textureType, Is.EqualTo(TextureImporterType.NormalMap));
            Assert.That(importer.wrapMode, Is.EqualTo(TextureWrapMode.Repeat));

            Material buttonMaterial =
                topButton.GetComponent<MeshRenderer>().sharedMaterial;
            Assert.That(buttonMaterial.name, Is.EqualTo("M_TwoLobeButton"));
            Assert.That(buttonMaterial.GetColor("_BaseColor"), Is.EqualTo(color));
            Assert.That(buttonMaterial.GetFloat("_Metallic"), Is.EqualTo(1f));
            Assert.That(
                buttonMaterial.GetFloat("_Smoothness"),
                Is.EqualTo(TwoLobeBarSpecifications.Smoothness).Within(0.0001f));
            Assert.That(buttonMaterial.GetTexture("_OcclusionMap"), Is.Not.Null);

            Light[] lights = root.GetComponentsInChildren<Light>(true);
            Assert.That(lights, Has.Length.EqualTo(1));
            Assert.That(lights[0].name, Is.EqualTo("LargeSoftAreaKey_UpperLeft"));
            Assert.That(lights[0].type, Is.EqualTo(LightType.Spot));
            Assert.That(lights[0].shadows, Is.EqualTo(LightShadows.Soft));

            Camera camera = root.GetComponentInChildren<Camera>(true);
            Assert.That(camera, Is.Not.Null);
            Transform backdrop = camera.transform.Find("WarmDefocusedBackdrop");
            Assert.That(backdrop, Is.Not.Null);
            Assert.That(backdrop.GetComponent<MeshRenderer>().sharedMaterial, Is.Not.Null);
        }

        [Test]
        public void ProductRegistrationSources_ContainTheGraphiteModel()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string environmentCatalog = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerEnvironmentPresenter.cs");
            string nativeUi = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            StringAssert.Contains(TwoLobeBarSpecifications.ModelId, coordinator);
            StringAssert.Contains("SpinnerEnvironmentCatalog.TwoLobeScenePath", coordinator);
            StringAssert.Contains(TwoLobeBarSpecifications.ScenePath, environmentCatalog);
            StringAssert.Contains(
                "case graphiteTwoLobe = \"graphite-two-lobe\"",
                nativeUi);
        }

        private Transform Require(string path)
        {
            Transform transform = root.Find(path);
            Assert.That(transform, Is.Not.Null, $"Missing {path}.");
            return transform;
        }

        private static Transform Require(Transform parent, string childName)
        {
            Transform child = parent.Find(childName);
            Assert.That(child, Is.Not.Null, $"Missing {parent.name}/{childName}.");
            return child;
        }

        private static void AssertFinite(Mesh mesh)
        {
            Assert.That(mesh.vertices, Is.Not.Empty);
            Assert.That(mesh.normals, Has.Length.EqualTo(mesh.vertexCount));
            Assert.That(mesh.tangents, Has.Length.EqualTo(mesh.vertexCount));
            foreach (Vector3 vertex in mesh.vertices)
            {
                Assert.That(float.IsNaN(vertex.x) || float.IsInfinity(vertex.x), Is.False);
                Assert.That(float.IsNaN(vertex.y) || float.IsInfinity(vertex.y), Is.False);
                Assert.That(float.IsNaN(vertex.z) || float.IsInfinity(vertex.z), Is.False);
            }
        }
    }
}
