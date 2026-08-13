using System;
using System.Collections.Generic;
using System.Linq;
using FidgetingApp.Product;
using NUnit.Framework;
using ThreeBladeEDC.EditorTools;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using Unity.Collections;
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
            Transform frame = Require(rotor, "ThreeBladeFrame");
            Transform insets = Require(rotor, "ThreeBladeInsets");
            Transform cage = Require(bearingVisual, "BallCage");

            Assert.That(
                rotor.Find("RotorCoreTopTrim"),
                Is.Null,
                "The removed decorative axis ring must not return as a physical requirement.");

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
            Assert.That(frame.IsChildOf(rotor), Is.True);
            Assert.That(insets.IsChildOf(rotor), Is.True);
            Assert.That(cage.IsChildOf(rotor), Is.False);

            Assert.That(
                rotorCore.GetComponent<MeshFilter>()?.sharedMesh,
                Is.Not.Null,
                "RotorCore must remain the real rotating carrier after decorative trim removal.");
            Assert.That(
                rotorCore.GetComponent<MeshRenderer>()?.enabled,
                Is.True,
                "The real RotorCore carrier must remain visible and owned by RotorDynamic.");
            Assert.That(
                outerRace.GetComponent<MeshFilter>()?.sharedMesh,
                Is.Not.Null,
                "BearingOuterRace must remain real rotating bearing geometry.");
            Assert.That(
                outerRace.GetComponent<MeshRenderer>()?.enabled,
                Is.True,
                "BearingOuterRace must remain visible and owned by RotorDynamic.");

            Rigidbody body = rotor.GetComponent<Rigidbody>();
            RotorRigidbodyController controller =
                rotor.GetComponent<RotorRigidbodyController>();
            MobileGestureController input =
                _root.GetComponent<MobileGestureController>();
            Assert.That(body, Is.Not.Null, "RotorDynamic needs a Rigidbody.");
            Rigidbody hubBody = hubStatic.GetComponent<Rigidbody>();
            Assert.That(
                hubBody,
                Is.Not.Null,
                "HubStatic needs its own kinematic anchor Rigidbody.");
            Assert.That(
                hubBody,
                Is.Not.SameAs(body),
                "HubStatic and RotorDynamic must retain distinct Rigidbody ownership.");
            Assert.That(
                hubBody.isKinematic,
                Is.True,
                "The fixed hub body must remain kinematic.");
            Assert.That(
                body.isKinematic,
                Is.False,
                "The real rotating carrier must remain the non-kinematic body.");
            Assert.That(
                bearingVisual.GetComponent<Rigidbody>(),
                Is.Null,
                "BearingVisual must remain a driven visual, not an independent physics body.");
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

            Transform bearingBalls = Require(cage, "BearingBalls");
            Mesh ballMesh = bearingBalls.GetComponent<MeshFilter>().sharedMesh;
            Assert.That(ballMesh.name, Is.EqualTo("M_BearingBallCage"));
            Assert.That(
                cage.GetComponentsInChildren<MeshRenderer>(true),
                Has.Length.EqualTo(1),
                "All eight visible balls must share one renderer and draw call.");

            Vector3 radialOffset = Vector3.ProjectOnPlane(
                rotor.position - hubStatic.position,
                Vector3.up);
            Assert.That(
                radialOffset.magnitude,
                Is.LessThanOrEqualTo(0.0001f),
                "Rotor and static holder must share one Y-axis pivot.");
        }

        [Test]
        public void VisibleRotorAxisPoint_RemainsAtViewportCenterAcrossRepresentativeAngles()
        {
            Transform rotor = Require("RotorDynamic");
            Transform visibleTopCap = Require("HubStatic/TopCap");
            Renderer visibleTopCapRenderer = visibleTopCap.GetComponent<Renderer>();
            Assert.That(visibleTopCapRenderer, Is.Not.Null);
            OrbitPresentationCamera orbit =
                _root.GetComponentInChildren<OrbitPresentationCamera>(true);
            Assert.That(orbit, Is.Not.Null, "The delivery camera needs orbit framing.");
            Assert.That(
                orbit.FocusTarget,
                Is.SameAs(visibleTopCap),
                "The delivery camera must target the visible center of the upper cap.");

            Vector3 axisOffset = Vector3.ProjectOnPlane(
                visibleTopCapRenderer.bounds.center - rotor.position,
                Vector3.up);
            Assert.That(
                axisOffset.magnitude,
                Is.LessThanOrEqualTo(0.0001f),
                "The visible focus must remain on the physical spin axis.");

            Camera camera = orbit.GetComponent<Camera>();
            camera.aspect = 1290f / 2796f;
            ProductFramingProfile framing = ProductFramingCatalog.Resolve(
                DeliveryScenePath);
            Quaternion initialRotation = rotor.localRotation;

            try
            {
                orbit.ConfigureFraming(framing);
                orbit.ResetHero();
                float fixedDistance = orbit.Distance;
                foreach (float angle in new[] { 0f, 30f, 60f, 90f, 120f })
                {
                    rotor.localRotation = Quaternion.Euler(0f, angle, 0f);
                    orbit.FrameNow();

                    Assert.That(
                        orbit.Distance,
                        Is.EqualTo(fixedDistance).Within(0.000001f),
                        $"The camera zoom breathed while the rotor turned to {angle} degrees.");

                    Vector3 pivotViewport = camera.WorldToViewportPoint(
                        visibleTopCapRenderer.bounds.center);
                    Assert.That(pivotViewport.z, Is.GreaterThan(0f), $"angle={angle}");
                    Assert.That(
                        pivotViewport.x,
                        Is.EqualTo(0.5f).Within(0.0001f),
                        $"The visible axis point drifted horizontally at {angle} degrees.");
                    Assert.That(
                        pivotViewport.y,
                        Is.EqualTo(0.5f).Within(0.0001f),
                        $"The visible axis point drifted vertically at {angle} degrees.");

                    AssertVisibleGeometryStaysInsideFraming(
                        camera,
                        _root,
                        framing.DetailWidthFraction,
                        framing.DetailHeightFraction,
                        angle);
                }
            }
            finally
            {
                rotor.localRotation = initialRotation;
            }
        }

        [Test]
        public void MobileDelivery_UsesOneGestureOwnerNoLegacyCanvasAndStudioStage()
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
            Canvas[] canvases = _root.GetComponentsInChildren<Canvas>(true);

            Assert.That(controllers, Has.Length.EqualTo(1));
            Assert.That(gestures, Has.Length.EqualTo(1));
            Assert.That(legacyInputs, Is.Empty);
            Assert.That(_root.GetComponentsInChildren<HingeJoint>(true), Is.Empty);
            Assert.That(mobileUi, Is.Empty);
            Assert.That(safeAreas, Is.Empty);
            Assert.That(canvases, Is.Empty);
            Assert.That(gestures[0].Rotor, Is.SameAs(controllers[0]));

            Rigidbody body = controllers[0].GetComponent<Rigidbody>();
            Assert.That(body.angularDamping, Is.EqualTo(0f).Within(0.001f));

            SerializedObject gestureSettings = new SerializedObject(gestures[0]);
            AssertSerializedFloat(
                gestureSettings,
                "spinSensitivity",
                global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultTouchResponse);
            AssertSerializedFloat(
                gestureSettings,
                "maxSpinSpeed",
                global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed);
            AssertSerializedFloat(
                gestureSettings,
                "spinSmoothing",
                global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultDragFollowResponse);
            AssertSerializedFloat(
                gestureSettings,
                "spinBrakeResponse",
                global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultDragBrakeResponse);
            AssertSerializedFloat(
                gestureSettings,
                "screenSpeedForFullSpin",
                global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultScreenSpeedForFullSpin);
            AssertSerializedFloat(
                gestureSettings,
                "fallbackTouchRadius",
                global::ThreeBladeEDC.FidgetSpinnerMotion
                    .DefaultFallbackTouchRadiusFraction);
            AssertSerializedFloat(gestureSettings, "reversalConfirmationPixels", 18f);
            SerializedProperty flipOnRelease =
                gestureSettings.FindProperty("flipOnRelease");
            Assert.That(flipOnRelease, Is.Not.Null);
            Assert.That(flipOnRelease.boolValue, Is.False);

            SerializedObject controllerSettings =
                new SerializedObject(controllers[0]);
            SerializedProperty configureOnAwake =
                controllerSettings.FindProperty("configureBodyOnAwake");
            Assert.That(configureOnAwake, Is.Not.Null);
            Assert.That(configureOnAwake.boolValue, Is.True);
            AssertSerializedFloat(
                controllerSettings,
                "maxAngularSpeed",
                global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed);
            AssertSerializedFloat(
                controllerSettings,
                "coastHalfLife",
                global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultCoastHalfLife);
            AssertSerializedFloat(controllerSettings, "magneticBreakawaySpeed", 2.2f);
            AssertSerializedFloat(controllerSettings, "magneticCaptureSpeed", 1.2f);
            AssertSerializedFloat(controllerSettings, "flipDuration", 0.4f);
            AssertSerializedFloat(controllerSettings, "flipOvershoot", 0.1f);
            AssertSerializedFloat(
                controllerSettings,
                "reversalStopDuration",
                0.3f);

            Camera camera = _root.GetComponentInChildren<Camera>(true);
            Assert.That(camera, Is.Not.Null);
            Assert.That(camera.clearFlags, Is.EqualTo(CameraClearFlags.SolidColor));
            Assert.That(camera.allowHDR, Is.False);
            UniversalAdditionalCameraData cameraData =
                camera.GetUniversalAdditionalCameraData();
            Assert.That(cameraData.renderPostProcessing, Is.False);

            MetalGlintController glint =
                _root.GetComponentInChildren<MetalGlintController>(true);
            Assert.That(glint, Is.Not.Null);
            Assert.That(glint.Rotor, Is.SameAs(controllers[0]));

            Transform floor = Require("Studio/StudioFloor");
            Assert.That(
                floor.gameObject.activeSelf,
                Is.False,
                "The shipping Unity stage must remain pure black and avoid floor fill-rate.");
        }

        [Test]
        public void RatchetAudio_UsesFiveAtomicVariantsTwelveVoicesAndOneListener()
        {
            MetalRatchetDetentAudio[] renderers =
                _root.GetComponentsInChildren<MetalRatchetDetentAudio>(true);
            AudioListener[] listeners =
                _root.GetComponentsInChildren<AudioListener>(true);

            Assert.That(renderers, Has.Length.EqualTo(1));
            MetalRatchetDetentAudio renderer = renderers[0];
            AudioSource[] ratchetSources =
                renderer.GetComponentsInChildren<AudioSource>(true);
            Assert.That(renderer.Rotor, Is.SameAs(
                _root.GetComponentInChildren<RotorRigidbodyController>(true)));
            Assert.That(renderer.ClickVariants, Has.Length.EqualTo(5));
            Assert.That(
                renderer.ClickVariants.Select(clip => clip.name).Distinct().Count(),
                Is.EqualTo(5));
            foreach (AudioClip clip in renderer.ClickVariants)
            {
                Assert.That(clip, Is.Not.Null);
                Assert.That(clip.channels, Is.EqualTo(1), clip.name);
                Assert.That(clip.length, Is.InRange(0.03f, 0.08f), clip.name);
                float[] samples = new float[clip.samples];
                Assert.That(clip.GetData(samples, 0), Is.True, clip.name);
                float peak = samples.Max(sample => Mathf.Abs(sample));
                float threshold = peak * 0.01f;
                int firstActive = Array.FindIndex(
                    samples,
                    sample => Mathf.Abs(sample) >= threshold);
                int lastActive = Array.FindLastIndex(
                    samples,
                    sample => Mathf.Abs(sample) >= threshold);
                Assert.That(
                    firstActive / (float)clip.frequency,
                    Is.LessThan(0.003f),
                    $"{clip.name} has leading silence padding.");
                Assert.That(
                    (samples.Length - 1 - lastActive) / (float)clip.frequency,
                    Is.LessThan(0.005f),
                    $"{clip.name} has trailing silence padding.");
            }

            Assert.That(
                renderer.Voices.Length,
                Is.GreaterThanOrEqualTo(RatchetAudioPhysicsModel.MinimumVoiceCount));
            Assert.That(
                ratchetSources,
                Has.Length.EqualTo(renderer.Voices.Length),
                "The independent looping wind source must not be counted as a ratchet voice.");
            Assert.That(listeners, Has.Length.EqualTo(1));
            foreach (AudioSource source in renderer.Voices)
            {
                Assert.That(source, Is.Not.Null);
                Assert.That(source.clip, Is.Null);
                Assert.That(source.playOnAwake, Is.False);
                Assert.That(source.loop, Is.False);
                Assert.That(source.spatialBlend, Is.Zero);
                Assert.That(source.reverbZoneMix, Is.Zero);
                Assert.That(source.bypassReverbZones, Is.True);
            }
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
                Is.LessThanOrEqualTo(45000),
                "The assembled iPhone delivery must remain under the 45k triangle budget.");
        }

        [Test]
        public void MobileRenderers_StayInsideDrawCallAndMaterialBudgets()
        {
            MeshRenderer[] renderers = _root
                .GetComponentsInChildren<MeshRenderer>(true)
                .Where(renderer => renderer.enabled)
                .ToArray();
            int estimatedDrawCalls = renderers.Sum(
                renderer => renderer.sharedMaterials.Length);
            Assert.That(
                estimatedDrawCalls,
                Is.LessThanOrEqualTo(20),
                "The complete presentation must remain within the exploded-view 20 draw-call budget.");

            Transform studio = Require("Studio");
            Material[] modelMaterials = renderers
                .Where(renderer => !renderer.transform.IsChildOf(studio))
                .SelectMany(renderer => renderer.sharedMaterials)
                .Where(material => material != null)
                .Distinct()
                .ToArray();
            Assert.That(
                modelMaterials,
                Has.Length.LessThanOrEqualTo(6),
                "The three-blade model must use at most six shared materials.");
        }

        [Test]
        public void BladeGroove_ReusesTheExistingPolishedSubmesh()
        {
            Transform frameObject = Require("RotorDynamic/ThreeBladeFrame");
            Mesh mesh = frameObject.GetComponent<MeshFilter>().sharedMesh;
            MeshRenderer renderer = frameObject.GetComponent<MeshRenderer>();

            Assert.That(mesh.subMeshCount, Is.EqualTo(2));
            Assert.That(renderer.sharedMaterials, Has.Length.EqualTo(2));

            Vector3[] vertices = mesh.vertices;
            int polishedGrooveVertices = mesh.GetTriangles(1)
                .Distinct()
                .Count(index => vertices[index].y > 0.0032f);
            Assert.That(
                polishedGrooveVertices,
                Is.EqualTo(60),
                "Three five-sided groove borders must live in the existing polished submesh.");
        }

        [Test]
        public void ReferenceProportions_CenterCapIsAboutHalfTheFrameWidth()
        {
            Mesh frame = Require("RotorDynamic/ThreeBladeFrame")
                .GetComponent<MeshFilter>().sharedMesh;
            Mesh topCap = Require("HubStatic/TopCap")
                .GetComponent<MeshFilter>().sharedMesh;
            float ratio = topCap.bounds.size.x / frame.bounds.size.x;
            Assert.That(
                ratio,
                Is.InRange(0.50f, 0.54f),
                "Reference sheet specifies a center diameter close to 0.52 of total width.");
        }

        [Test]
        public void TopCap_HasTwentyFourWaveTeethAndUsesSimplifiedCollision()
        {
            Transform topCap = Require("HubStatic/TopCap");
            Mesh visualMesh = topCap.GetComponent<MeshFilter>().sharedMesh;
            MeshCollider collider = topCap.GetComponent<MeshCollider>();

            Assert.That(visualMesh.name, Is.EqualTo("M_ScallopedTopCap"));
            Assert.That(collider, Is.Not.Null);
            Assert.That(collider.convex, Is.True);
            Assert.That(collider.sharedMesh, Is.Not.SameAs(visualMesh));
            Assert.That(collider.sharedMesh.name, Is.EqualTo("M_TopCapCollision"));
            Assert.That(
                TriangleCount(collider.sharedMesh),
                Is.LessThan(TriangleCount(visualMesh)),
                "Detailed grip teeth must not inflate the convex touch collider.");

            Vector3[] vertices = visualMesh.vertices;
            float sideHeight = visualMesh.bounds.extents.y - 0.00072f;
            var perimeterByAngle = vertices
                .Where(vertex => Mathf.Abs(Mathf.Abs(vertex.y) - sideHeight) < 0.00001f)
                .Select(vertex => new
                {
                    Angle = Mathf.Repeat(
                        Mathf.Atan2(vertex.z, vertex.x) * Mathf.Rad2Deg,
                        360f),
                    Radius = new Vector2(vertex.x, vertex.z).magnitude
                })
                .GroupBy(sample => Mathf.RoundToInt(sample.Angle * 1000f))
                .Select(group => group.Max(sample => sample.Radius))
                .ToArray();

            Assert.That(perimeterByAngle, Has.Length.EqualTo(24 * 6));
            Assert.That(
                perimeterByAngle.Max() - perimeterByAngle.Min(),
                Is.EqualTo(0.00012f).Within(0.00002f),
                "The grip valleys must be visibly recessed from each tooth crest.");

            int crestCount = 0;
            for (int i = 0; i < perimeterByAngle.Length; i++)
            {
                float previous = perimeterByAngle[
                    (i - 1 + perimeterByAngle.Length) % perimeterByAngle.Length];
                float current = perimeterByAngle[i];
                float next = perimeterByAngle[(i + 1) % perimeterByAngle.Length];
                if (current > previous + 0.000001f
                    && current > next + 0.000001f)
                {
                    crestCount++;
                }
            }

            Assert.That(
                crestCount,
                Is.EqualTo(24),
                "The central metal cap must expose 24 continuous dog-tooth waves.");
        }

        [Test]
        public void RoundMetalParts_UseDenseButMobileSafePerimeters()
        {
            Assert.That(
                Require("RotorDynamic/RotorCore")
                    .GetComponent<MeshFilter>().sharedMesh.vertexCount,
                Is.EqualTo(128 * 16));
            Assert.That(
                Require("RotorDynamic/BearingOuterRace")
                    .GetComponent<MeshFilter>().sharedMesh.vertexCount,
                Is.EqualTo(128 * 16));
            Assert.That(
                Require("HubStatic/BearingInnerRace")
                    .GetComponent<MeshFilter>().sharedMesh.vertexCount,
                Is.EqualTo(128 * 16));
            Assert.That(
                Require("HubStatic/BottomCap")
                    .GetComponent<MeshFilter>().sharedMesh.vertexCount,
                Is.EqualTo(96 * 18));
        }

        [Test]
        public void IOSDeliverySettings_AreDeviceReady()
        {
            NamedBuildTarget ios = NamedBuildTarget.iOS;
            Assert.That(
                PlayerSettings.GetApplicationIdentifier(ios),
                Is.EqualTo("com.jiaweizhou.fidgetspinner.codex"));
            Assert.That(PlayerSettings.bundleVersion, Is.EqualTo("0.1.0"));
            Assert.That(PlayerSettings.iOS.targetOSVersionString, Is.EqualTo("15.0"));
            Assert.That(PlayerSettings.allowedAutorotateToPortrait, Is.True);
            Assert.That(PlayerSettings.allowedAutorotateToLandscapeLeft, Is.False);
            Assert.That(PlayerSettings.allowedAutorotateToLandscapeRight, Is.False);

            UniversalRenderPipelineAsset mobilePipeline =
                AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(
                    "Assets/Settings/Mobile_RPAsset.asset");
            Assert.That(mobilePipeline, Is.Not.Null);
            Assert.That(mobilePipeline.msaaSampleCount, Is.EqualTo(2));
            Assert.That(mobilePipeline.renderScale, Is.EqualTo(0.9f).Within(0.001f));
            Assert.That(mobilePipeline.supportsHDR, Is.False);
        }

        private static void AssertVisibleGeometryStaysInsideFraming(
            Camera camera,
            Transform root,
            float widthFraction,
            float heightFraction,
            float angle)
        {
            float minimumX = float.PositiveInfinity;
            float maximumX = float.NegativeInfinity;
            float minimumY = float.PositiveInfinity;
            float maximumY = float.NegativeInfinity;
            bool foundVertex = false;

            foreach (MeshRenderer renderer in
                     root.GetComponentsInChildren<MeshRenderer>(true))
            {
                if (renderer == null
                    || !renderer.enabled
                    || !renderer.gameObject.activeInHierarchy
                    || renderer.GetComponentInParent<Camera>() != null)
                {
                    continue;
                }

                MeshFilter filter = renderer.GetComponent<MeshFilter>();
                Mesh mesh = filter != null ? filter.sharedMesh : null;
                Assert.That(
                    mesh,
                    Is.Not.Null,
                    $"Visible renderer {HierarchyPath(renderer.transform)} needs a mesh.");

                using (Mesh.MeshDataArray data = Mesh.AcquireReadOnlyMeshData(mesh))
                using (var vertices = new NativeArray<Vector3>(
                           mesh.vertexCount,
                           Allocator.Temp,
                           NativeArrayOptions.UninitializedMemory))
                {
                    data[0].GetVertices(vertices);
                    foreach (Vector3 vertex in vertices)
                    {
                        Vector3 viewport = camera.WorldToViewportPoint(
                            filter.transform.TransformPoint(vertex));
                        Assert.That(viewport.z, Is.GreaterThan(0f), $"angle={angle}");
                        minimumX = Mathf.Min(minimumX, viewport.x);
                        maximumX = Mathf.Max(maximumX, viewport.x);
                        minimumY = Mathf.Min(minimumY, viewport.y);
                        maximumY = Mathf.Max(maximumY, viewport.y);
                        foundVertex = true;
                    }
                }
            }

            Assert.That(foundVertex, Is.True, $"angle={angle}");
            Assert.That(
                minimumX,
                Is.GreaterThanOrEqualTo(0.5f - widthFraction * 0.5f - 0.001f),
                $"Visible rotor geometry exceeded the left boundary at {angle} degrees.");
            Assert.That(
                maximumX,
                Is.LessThanOrEqualTo(0.5f + widthFraction * 0.5f + 0.001f),
                $"Visible rotor geometry exceeded the right boundary at {angle} degrees.");
            Assert.That(
                minimumY,
                Is.GreaterThanOrEqualTo(0.5f - heightFraction * 0.5f - 0.001f),
                $"Visible rotor geometry exceeded the bottom boundary at {angle} degrees.");
            Assert.That(
                maximumY,
                Is.LessThanOrEqualTo(0.5f + heightFraction * 0.5f + 0.001f),
                $"Visible rotor geometry exceeded the top boundary at {angle} degrees.");
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

            if (sampleCount == 0)
            {
                MeshCollider collider = blade.GetComponent<MeshCollider>();
                Assert.That(
                    collider,
                    Is.Not.Null,
                    $"{HierarchyPath(blade)} must provide visual or collision geometry.");
                Assert.That(collider.sharedMesh, Is.Not.Null);
                foreach (Vector3 vertex in collider.sharedMesh.vertices)
                {
                    Vector3 world = blade.TransformPoint(vertex);
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
            float meshScaleSquared = bounds.size.sqrMagnitude;
            float minimumDoubledAreaSquared = Mathf.Max(
                1e-24f,
                meshScaleSquared * meshScaleSquared * 1e-17f);
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
                        Is.GreaterThan(minimumDoubledAreaSquared),
                        $"{ownerPath} submesh {subMesh} triangle {i / 3} is " +
                        "numerically degenerate for its mesh scale.");
                }
            }
        }

        private static long TriangleCount(Mesh mesh)
        {
            long triangleCount = 0;
            for (int subMesh = 0; subMesh < mesh.subMeshCount; subMesh++)
            {
                triangleCount += (long)mesh.GetIndexCount(subMesh) / 3L;
            }
            return triangleCount;
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
