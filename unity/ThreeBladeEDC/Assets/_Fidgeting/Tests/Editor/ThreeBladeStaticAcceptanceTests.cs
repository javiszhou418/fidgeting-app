using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using ThreeBladeEDC.EditorTools;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace ThreeBladeEDC.Tests.Editor
{
    /// <summary>
    /// Static delivery checks for the authored concept scene. These tests do
    /// not enter Play Mode and intentionally treat object names and ownership
    /// as a hand-off contract between geometry, interaction and presentation.
    /// </summary>
    public sealed class ThreeBladeStaticAcceptanceTests
    {
        private const string DeliveryScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";
        private const string RootName = "ThreeBladeEDC_Root";
        private const float AngularToleranceDegrees = 0.5f;
        private const float RadialToleranceFraction = 0.005f;

        private SceneSetup[] _previousSceneSetup;
        private Scene _deliveryScene;
        private Transform _root;

        [SetUp]
        public void OpenDeliveryScene()
        {
            _previousSceneSetup = EditorSceneManager.GetSceneManagerSetup();

            SceneAsset sceneAsset =
                AssetDatabase.LoadAssetAtPath<SceneAsset>(DeliveryScenePath);
            Assert.That(
                sceneAsset,
                Is.Not.Null,
                $"Delivery scene is missing at {DeliveryScenePath}.");

            _deliveryScene = EditorSceneManager.OpenScene(
                DeliveryScenePath,
                OpenSceneMode.Single);
            Assert.That(_deliveryScene.IsValid(), Is.True);
            Assert.That(_deliveryScene.isLoaded, Is.True);

            GameObject rootObject = _deliveryScene
                .GetRootGameObjects()
                .SingleOrDefault(candidate => candidate.name == RootName);
            Assert.That(
                rootObject,
                Is.Not.Null,
                $"Scene must contain one root named {RootName}.");
            _root = rootObject.transform;
        }

        [TearDown]
        public void RestorePreviousScenes()
        {
            if (_previousSceneSetup != null
                && _previousSceneSetup.Any(setup => setup.isLoaded))
            {
                EditorSceneManager.RestoreSceneManagerSetup(_previousSceneSetup);
                return;
            }

            // Batch-mode Test Runner may start without any loaded scene. Unity
            // requires one active scene, so restore a clean empty scene rather
            // than passing an invalid, empty SceneManagerSetup array.
            EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,
                NewSceneMode.Single);
        }

        [Test]
        public void Rotor_HasExactlyThreeEqualBladesAtOneHundredTwentyDegrees()
        {
            Transform rotor = Require("RotorDynamic");
            Transform[] blades = rotor
                .Cast<Transform>()
                .Where(child => child.name.StartsWith(
                    "Blade_",
                    StringComparison.Ordinal))
                .OrderBy(child => child.name, StringComparer.Ordinal)
                .ToArray();

            Assert.That(
                blades.Select(blade => blade.name),
                Is.EqualTo(new[] { "Blade_00", "Blade_01", "Blade_02" }));

            var radialSamples = new List<Vector2>(blades.Length);
            foreach (Transform blade in blades)
            {
                Vector3 centroid = CalculateMeshCentroidInRotorSpace(
                    blade,
                    rotor);
                Vector2 radial = new Vector2(centroid.x, centroid.z);
                Assert.That(
                    radial.magnitude,
                    Is.GreaterThan(0.0001f),
                    $"{blade.name} must extend away from the local Y spin axis.");
                radialSamples.Add(radial);
            }

            float[] radii = radialSamples
                .Select(sample => sample.magnitude)
                .ToArray();
            float averageRadius = radii.Average();
            float radiusSpread = radii.Max() - radii.Min();
            Assert.That(
                radiusSpread,
                Is.LessThanOrEqualTo(
                    averageRadius * RadialToleranceFraction + 0.00001f),
                "Blade radial centroids must match within 0.5%.");

            float[] angles = radialSamples
                .Select(sample => Mathf.Repeat(
                    Mathf.Atan2(sample.y, sample.x) * Mathf.Rad2Deg,
                    360f))
                .OrderBy(angle => angle)
                .ToArray();

            float[] angularGaps =
            {
                angles[1] - angles[0],
                angles[2] - angles[1],
                angles[0] + 360f - angles[2]
            };
            foreach (float gap in angularGaps)
            {
                Assert.That(
                    gap,
                    Is.EqualTo(120f).Within(AngularToleranceDegrees),
                    "Consecutive blade sectors must be separated by 120° ±0.5°.");
            }
        }

        [Test]
        public void RenderMeshes_HaveFiniteGeometryAndValidTriangleIndices()
        {
            MeshFilter[] meshFilters = _root.GetComponentsInChildren<MeshFilter>(true);
            Assert.That(meshFilters, Is.Not.Empty, "The delivery model has no meshes.");

            var validatedMeshes = new HashSet<Mesh>();
            foreach (MeshFilter filter in meshFilters)
            {
                Mesh mesh = filter.sharedMesh;
                Assert.That(
                    mesh,
                    Is.Not.Null,
                    $"{HierarchyPath(filter.transform)} has no shared mesh.");

                if (!validatedMeshes.Add(mesh))
                {
                    continue;
                }

                ValidateMesh(mesh, HierarchyPath(filter.transform));
            }
        }

        [Test]
        public void BearingAndRotor_HaveIndependentPhysicalOwnership()
        {
            Transform hubStatic = Require("HubStatic");
            Transform rotor = Require("RotorDynamic");
            Transform bearingVisual = Require("BearingVisual");

            Transform axle = Require(hubStatic, "Axle");
            Transform innerRace = Require(hubStatic, "BearingInnerRace");
            Transform topCap = Require(hubStatic, "TopCap");
            Transform bottomCap = Require(hubStatic, "BottomCap");
            Transform rotorCore = Require(rotor, "RotorCore");
            Transform outerRace = Require(rotor, "BearingOuterRace");
            Transform cage = Require(bearingVisual, "BallCage");

            Assert.That(hubStatic.parent, Is.EqualTo(_root));
            Assert.That(rotor.parent, Is.EqualTo(_root));
            Assert.That(bearingVisual.parent, Is.EqualTo(_root));
            Assert.That(rotor.IsChildOf(hubStatic), Is.False);
            Assert.That(hubStatic.IsChildOf(rotor), Is.False);

            foreach (Transform fixedPart in new[]
                     {
                         axle,
                         innerRace,
                         topCap,
                         bottomCap
                     })
            {
                Assert.That(
                    fixedPart.IsChildOf(rotor),
                    Is.False,
                    $"{fixedPart.name} must remain independent of RotorDynamic.");
            }

            Assert.That(rotorCore.IsChildOf(rotor), Is.True);
            Assert.That(outerRace.IsChildOf(rotor), Is.True);
            Assert.That(cage.IsChildOf(rotor), Is.False);

            Rigidbody body = rotor.GetComponent<Rigidbody>();
            RotorRigidbodyController controller =
                rotor.GetComponent<RotorRigidbodyController>();
            MobileGestureController input =
                _root.GetComponent<MobileGestureController>();
            Assert.That(body, Is.Not.Null, "RotorDynamic needs a Rigidbody.");
            Assert.That(
                controller,
                Is.Not.Null,
                "RotorDynamic needs RotorRigidbodyController.");
            Assert.That(input, Is.Not.Null, "Root needs MobileGestureController.");
            Assert.That(input.Rotor, Is.SameAs(controller));

            BearingCageVisualSync cageSync =
                bearingVisual.GetComponentInChildren<BearingCageVisualSync>(true);
            Assert.That(
                cageSync,
                Is.Not.Null,
                "BearingVisual needs BearingCageVisualSync for accumulated real rotation.");
            Assert.That(cageSync.Rotor, Is.SameAs(controller));
            Assert.That(cageSync.CageVisual, Is.SameAs(cage));

            Transform[] balls = cage
                .Cast<Transform>()
                .Where(child => child.name.StartsWith(
                    "Ball_",
                    StringComparison.Ordinal))
                .OrderBy(child => child.name, StringComparer.Ordinal)
                .ToArray();
            Assert.That(
                balls.Select(ball => ball.name),
                Is.EqualTo(new[]
                {
                    "Ball_00",
                    "Ball_01",
                    "Ball_02",
                    "Ball_03",
                    "Ball_04",
                    "Ball_05",
                    "Ball_06",
                    "Ball_07"
                }));

            Vector3 radialOffset = Vector3.ProjectOnPlane(
                rotor.position - hubStatic.position,
                Vector3.up);
            Assert.That(
                radialOffset.magnitude,
                Is.LessThanOrEqualTo(0.0001f),
                "Rotor and static holder must share one Y-axis pivot.");
        }

        [Test]
        public void MobileDelivery_UsesOneGestureOwnerSafeAreaAndStudioStage()
        {
            RotorRigidbodyController[] controllers =
                _root.GetComponentsInChildren<RotorRigidbodyController>(true);
            MobileGestureController[] gestures =
                _root.GetComponentsInChildren<MobileGestureController>(true);
            RotorFlickInput[] legacyInputs =
                _root.GetComponentsInChildren<RotorFlickInput>(true);
            MobileViewerUI[] mobileUi =
                _root.GetComponentsInChildren<MobileViewerUI>(true);
            SafeAreaFitter[] safeAreas =
                _root.GetComponentsInChildren<SafeAreaFitter>(true);

            Assert.That(controllers, Has.Length.EqualTo(1));
            Assert.That(gestures, Has.Length.EqualTo(1));
            Assert.That(legacyInputs, Is.Empty);
            Assert.That(mobileUi, Has.Length.EqualTo(1));
            Assert.That(safeAreas, Has.Length.EqualTo(1));
            Assert.That(gestures[0].Rotor, Is.SameAs(controllers[0]));

            Rigidbody body = controllers[0].GetComponent<Rigidbody>();
            Assert.That(body.angularDamping, Is.EqualTo(0.55f).Within(0.001f));

            SerializedObject gestureSettings = new SerializedObject(gestures[0]);
            AssertSerializedFloat(gestureSettings, "spinSensitivity", 0.34f);
            AssertSerializedFloat(gestureSettings, "maxSpinSpeed", 24f);
            AssertSerializedFloat(gestureSettings, "spinSmoothing", 15f);

            SerializedObject controllerSettings =
                new SerializedObject(controllers[0]);
            SerializedProperty configureOnAwake =
                controllerSettings.FindProperty("configureBodyOnAwake");
            Assert.That(configureOnAwake, Is.Not.Null);
            Assert.That(configureOnAwake.boolValue, Is.True);
            AssertSerializedFloat(controllerSettings, "maxAngularSpeed", 24f);
            AssertSerializedFloat(controllerSettings, "flipDuration", 0.4f);
            AssertSerializedFloat(controllerSettings, "flipOvershoot", 0.1f);
            AssertSerializedFloat(
                controllerSettings,
                "reversalStopDuration",
                0.3f);

            Camera camera = _root.GetComponentInChildren<Camera>(true);
            Assert.That(camera, Is.Not.Null);
            Assert.That(camera.clearFlags, Is.EqualTo(CameraClearFlags.SolidColor));
            Assert.That(camera.allowHDR, Is.True);

            Transform floor = Require("Studio/StudioFloor");
            Assert.That(floor.gameObject.activeSelf, Is.True);
        }

        [Test]
        public void MobileMeshes_StayInsideTriangleBudgetAndProvidePbrChannels()
        {
            MeshFilter[] filters = _root.GetComponentsInChildren<MeshFilter>(true);
            long visibleTriangleCount = 0;
            foreach (MeshFilter filter in filters)
            {
                Mesh mesh = filter.sharedMesh;
                Assert.That(mesh.uv.Length, Is.EqualTo(mesh.vertexCount), filter.name);
                Assert.That(mesh.tangents.Length, Is.EqualTo(mesh.vertexCount), filter.name);
                for (int subMesh = 0; subMesh < mesh.subMeshCount; subMesh++)
                {
                    visibleTriangleCount += (long)mesh.GetIndexCount(subMesh) / 3L;
                }
            }

            Assert.That(
                visibleTriangleCount,
                Is.LessThanOrEqualTo(60000),
                "The iPhone delivery must remain under the 60k visible-triangle budget.");
        }

        [Test]
        public void IOSDeliverySettings_AreDeviceReady()
        {
            NamedBuildTarget ios = NamedBuildTarget.iOS;
            Assert.That(
                PlayerSettings.GetApplicationIdentifier(ios),
                Is.EqualTo(IOSBuildPipeline.BundleIdentifier));
            Assert.That(PlayerSettings.bundleVersion, Is.EqualTo("0.1.0"));
            Assert.That(PlayerSettings.iOS.targetOSVersionString, Is.EqualTo("15.0"));
            Assert.That(PlayerSettings.iOS.appleEnableAutomaticSigning, Is.True);
            Assert.That(PlayerSettings.iOS.appleDeveloperTeamID, Is.Not.Empty);
            Assert.That(PlayerSettings.allowedAutorotateToPortrait, Is.False);
            Assert.That(PlayerSettings.allowedAutorotateToLandscapeLeft, Is.True);
            Assert.That(PlayerSettings.allowedAutorotateToLandscapeRight, Is.True);

            UniversalRenderPipelineAsset mobilePipeline =
                AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(
                    "Assets/Settings/Mobile_RPAsset.asset");
            Assert.That(mobilePipeline, Is.Not.Null);
            Assert.That(mobilePipeline.msaaSampleCount, Is.EqualTo(4));
            Assert.That(mobilePipeline.renderScale, Is.EqualTo(1f).Within(0.001f));
        }

        private static void AssertSerializedFloat(
            SerializedObject serializedObject,
            string propertyName,
            float expected)
        {
            SerializedProperty property =
                serializedObject.FindProperty(propertyName);
            Assert.That(property, Is.Not.Null, $"Missing setting: {propertyName}");
            Assert.That(
                property.floatValue,
                Is.EqualTo(expected).Within(0.001f),
                propertyName);
        }

        private Transform Require(string relativePath)
        {
            return Require(_root, relativePath);
        }

        private static Transform Require(Transform parent, string relativePath)
        {
            Transform result = parent.Find(relativePath);
            Assert.That(
                result,
                Is.Not.Null,
                $"Missing required hierarchy path: {HierarchyPath(parent)}/{relativePath}");
            return result;
        }

        private static Vector3 CalculateMeshCentroidInRotorSpace(
            Transform blade,
            Transform rotor)
        {
            MeshFilter[] filters = blade.GetComponentsInChildren<MeshFilter>(true);
            Assert.That(
                filters,
                Is.Not.Empty,
                $"{HierarchyPath(blade)} must contain renderable mesh geometry.");

            Vector3 sum = Vector3.zero;
            int sampleCount = 0;
            foreach (MeshFilter filter in filters)
            {
                Mesh mesh = filter.sharedMesh;
                Assert.That(mesh, Is.Not.Null);
                foreach (Vector3 vertex in mesh.vertices)
                {
                    Vector3 world = filter.transform.TransformPoint(vertex);
                    sum += rotor.InverseTransformPoint(world);
                    sampleCount++;
                }
            }

            Assert.That(sampleCount, Is.GreaterThan(0));
            return sum / sampleCount;
        }

        private static void ValidateMesh(Mesh mesh, string ownerPath)
        {
            Vector3[] vertices = mesh.vertices;
            Assert.That(vertices, Is.Not.Empty, $"{ownerPath} has no vertices.");
            for (int i = 0; i < vertices.Length; i++)
            {
                Assert.That(
                    IsFinite(vertices[i]),
                    Is.True,
                    $"{ownerPath} vertex {i} is not finite.");
            }

            Vector3[] normals = mesh.normals;
            Assert.That(
                normals.Length,
                Is.EqualTo(vertices.Length),
                $"{ownerPath} must provide one normal per vertex for PBR rendering.");
            for (int i = 0; i < normals.Length; i++)
            {
                Assert.That(
                    IsFinite(normals[i]),
                    Is.True,
                    $"{ownerPath} normal {i} is not finite.");
            }

            Bounds bounds = mesh.bounds;
            Assert.That(IsFinite(bounds.center), Is.True, $"{ownerPath} bounds center is invalid.");
            Assert.That(IsFinite(bounds.extents), Is.True, $"{ownerPath} bounds extents are invalid.");
            Assert.That(
                bounds.extents.sqrMagnitude,
                Is.GreaterThan(0f),
                $"{ownerPath} bounds are empty.");

            Assert.That(mesh.subMeshCount, Is.GreaterThan(0));
            for (int subMesh = 0; subMesh < mesh.subMeshCount; subMesh++)
            {
                Assert.That(
                    mesh.GetTopology(subMesh),
                    Is.EqualTo(MeshTopology.Triangles),
                    $"{ownerPath} submesh {subMesh} must use triangles.");

                int[] indices = mesh.GetIndices(subMesh);
                Assert.That(indices, Is.Not.Empty);
                Assert.That(
                    indices.Length % 3,
                    Is.EqualTo(0),
                    $"{ownerPath} submesh {subMesh} has an incomplete triangle.");

                for (int i = 0; i < indices.Length; i++)
                {
                    Assert.That(
                        indices[i],
                        Is.InRange(0, vertices.Length - 1),
                        $"{ownerPath} submesh {subMesh} index {i} is out of range.");
                }

                for (int i = 0; i < indices.Length; i += 3)
                {
                    Vector3 a = vertices[indices[i]];
                    Vector3 b = vertices[indices[i + 1]];
                    Vector3 c = vertices[indices[i + 2]];
                    float doubledAreaSquared =
                        Vector3.Cross(b - a, c - a).sqrMagnitude;
                    Assert.That(
                        doubledAreaSquared,
                        Is.GreaterThan(1e-16f),
                        $"{ownerPath} submesh {subMesh} triangle {i / 3} is degenerate.");
                }
            }
        }

        private static bool IsFinite(Vector3 value)
        {
            return IsFinite(value.x) && IsFinite(value.y) && IsFinite(value.z);
        }

        private static bool IsFinite(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value);
        }

        private static string HierarchyPath(Transform transform)
        {
            var parts = new Stack<string>();
            Transform current = transform;
            while (current != null)
            {
                parts.Push(current.name);
                current = current.parent;
            }

            return string.Join("/", parts);
        }
    }
}
