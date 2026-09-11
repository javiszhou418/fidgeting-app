using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using TouchPhase = UnityEngine.InputSystem.TouchPhase;

namespace FidgetingApp.MagneticSlide.PlayModeTests
{
    public sealed class MagneticSlideTileInputPlayModeTests
    {
        private const string SceneName = "MeshyEDC";
        private Touchscreen touchscreen;
        private bool previousRunInBackground;
        private InputSettings.BackgroundBehavior previousBackgroundBehavior;
#if UNITY_EDITOR
        private InputSettings.EditorInputBehaviorInPlayMode
            previousEditorInputBehavior;
#endif

        [UnitySetUp]
        public IEnumerator LoadShippingScene()
        {
            previousRunInBackground = Application.runInBackground;
            previousBackgroundBehavior =
                InputSystem.settings.backgroundBehavior;
            Application.runInBackground = true;
            InputSystem.settings.backgroundBehavior =
                InputSettings.BackgroundBehavior.IgnoreFocus;
#if UNITY_EDITOR
            previousEditorInputBehavior =
                InputSystem.settings.editorInputBehaviorInPlayMode;
            InputSystem.settings.editorInputBehaviorInPlayMode =
                InputSettings.EditorInputBehaviorInPlayMode
                    .AllDeviceInputAlwaysGoesToGameView;
#endif
            AsyncOperation load = SceneManager.LoadSceneAsync(SceneName);
            Assert.That(load, Is.Not.Null);
            while (!load.isDone)
                yield return null;
            yield return null;
            yield return null;
            touchscreen = InputSystem.AddDevice<Touchscreen>(
                "MagneticSlideIntegrationTouchscreen");
            InputSystem.EnableDevice(touchscreen);
            Assert.That(Touchscreen.current, Is.SameAs(touchscreen));
            Assert.That(touchscreen.enabled, Is.True);
        }

        [UnityTearDown]
        public IEnumerator RemoveSyntheticTouchscreen()
        {
            if (touchscreen != null && touchscreen.added)
                InputSystem.RemoveDevice(touchscreen);
            InputSystem.settings.backgroundBehavior =
                previousBackgroundBehavior;
#if UNITY_EDITOR
            InputSystem.settings.editorInputBehaviorInPlayMode =
                previousEditorInputBehavior;
#endif
            Application.runInBackground = previousRunInBackground;
            yield return null;
        }

        [UnityTest]
        public IEnumerator ShippingSceneUsesTrueLayerCapAssemblies()
        {
            RuntimeContext context = RuntimeContext.Resolve();
            MeshRenderer[] bodyRenderers = context.Candidate
                .GetComponentsInChildren<MeshRenderer>(true)
                .Where(renderer => renderer.enabled
                    && (renderer.name == "MovingTopBody"
                        || renderer.name == "BottomExterior"))
                .ToArray();
            Assert.That(bodyRenderers, Has.Length.EqualTo(2));
            foreach (MeshRenderer renderer in bodyRenderers)
            {
                Assert.That(renderer.sharedMaterials, Has.Length.EqualTo(4));
                int substrateIndex = Array.FindIndex(
                    renderer.sharedMaterials,
                    material => material != null
                        && material.name.Contains(
                            "Rev12DetailSubstrate",
                            StringComparison.Ordinal));
                Assert.That(substrateIndex, Is.GreaterThanOrEqualTo(0));
                Assert.That(
                    renderer.GetComponent<MeshFilter>().sharedMesh
                        .GetIndexCount(substrateIndex),
                    Is.Zero);
                Assert.That(renderer.sharedMaterials[0].name,
                    Does.Contain("SolidDarkSide"));
            }
            Transform[] assemblies = context.Candidate
                .GetComponentsInChildren<Transform>(true)
                .Where(item => item.name.EndsWith(
                    "_TrueLayerAssembly_R013",
                    StringComparison.Ordinal))
                .ToArray();
            Assert.That(assemblies, Has.Length.EqualTo(2));
            foreach (Transform assembly in assemblies)
            {
                MeshRenderer substrate = assembly
                    .GetComponentsInChildren<MeshRenderer>(true)
                    .Single(renderer => renderer.name.Contains(
                        "_SubstrateInlay_R013",
                        StringComparison.Ordinal));
                MeshRenderer motif = assembly
                    .GetComponentsInChildren<MeshRenderer>(true)
                    .Single(renderer => renderer.name.Contains(
                        "_EtchedMotif_R013",
                        StringComparison.Ordinal));
                MeshRenderer crystal = assembly
                    .GetComponentsInChildren<MeshRenderer>(true)
                    .Single(renderer => renderer.name.Contains(
                        "_CrystalCap_R013",
                        StringComparison.Ordinal));
                Assert.That(substrate.enabled, Is.True);
                Assert.That(motif.enabled, Is.True);
                Assert.That(crystal.enabled, Is.True);
                Assert.That(
                    substrate.sharedMaterial.shader.name,
                    Is.EqualTo(
                        "FidgetingApp/MagneticSlideTile/HybridSubstrateR014"));
                Assert.That(
                    motif.sharedMaterial.shader.name,
                    Is.EqualTo(
                        "FidgetingApp/MagneticSlideTile/HybridMotifR014"));
                Assert.That(
                    crystal.sharedMaterial.shader.name,
                    Is.EqualTo(
                        "FidgetingApp/MagneticSlideTile/HybridCrystalR014"));
                Assert.That(
                    crystal.sharedMaterial.GetFloat("_Ior"),
                    Is.EqualTo(1.52f));
                Assert.That(
                    crystal.sharedMaterial.GetFloat("_ThicknessMeters"),
                    Is.EqualTo(0.00028f));
                Assert.That(
                    substrate.sharedMaterial.GetFloat("_MicaScale"),
                    Is.EqualTo(28f));
                Assert.That(
                    substrate.sharedMaterial.GetFloat("_MicroflakeScale"),
                    Is.EqualTo(85f));
                Assert.That(
                    crystal.sharedMaterial.GetFloat("_Transmission"),
                    Is.EqualTo(0.985f));
                Assert.That(
                    substrate.sharedMaterial.HasProperty("_EmissionColor"),
                    Is.False);
            }
            yield return null;
            Assert.That(context.IsPoseLegal, Is.True);
        }

        [UnityTest]
        public IEnumerator TouchEventsDriveInterlockFullTurnAudioAndHaptics()
        {
            RuntimeContext context = RuntimeContext.Resolve();
            Matrix4x4 bottomBaseline =
                FindTransform(context.Candidate.transform, "BottomExterior")
                    .localToWorldMatrix;
            Matrix4x4 axisBaseline =
                context.FixedAxis.localToWorldMatrix;

            yield return RotateTouch(
                1,
                SurfaceScreenPoint(context),
                AxisScreenPoint(context),
                24f,
                2);
            Assert.That(context.AngleDegrees, Is.Zero);
            yield return CloseTouch(2, context);

            int slideAudioBefore = context.AudioPlaybackCount;
            yield return OpenTouch(3, context);
            Assert.That(context.AtMaximumTravel, Is.True);
            Assert.That(context.AngleDegrees, Is.Zero);
            Assert.That(
                context.AudioCount("MagneticEdgeProbe"),
                Is.GreaterThanOrEqualTo(context.SlideStepCount));
            Assert.That(
                context.AudioCount("Breakaway"),
                Is.GreaterThanOrEqualTo(1));

            yield return RotateTouch(
                4,
                SurfaceScreenPoint(context),
                AxisScreenPoint(context),
                context.DetentStepDegrees,
                1);
            Assert.That(context.CurrentDetentIndex, Is.EqualTo(1));
            float openTravel = context.TravelMeters;
            yield return CloseTouch(5, context);
            Assert.That(
                context.TravelMeters,
                Is.EqualTo(openTravel).Within(0.000001f));

            int alignmentSteps = Mathf.Abs(context.UnwrappedDetentIndex);
            float alignmentStep = -Mathf.Sign(context.UnwrappedDetentIndex)
                * context.DetentStepDegrees;
            yield return RotateTouch(
                6,
                SurfaceScreenPoint(context),
                AxisScreenPoint(context),
                alignmentStep,
                alignmentSteps);
            Assert.That(context.AngleDegrees, Is.Zero.Within(0.001f));
            yield return CloseTouch(7, context);
            Assert.That(
                context.TravelMeters,
                Is.LessThanOrEqualTo(context.EndpointToleranceMeters));

            yield return OpenTouch(8, context);
            int detentAudioBefore = context.AudioCount("DetentCrossed");
            int semanticBefore = context.SemanticEventCount;
            HapticSnapshot hapticBefore = HapticSnapshot.Read();
            yield return RotateTouch(
                9,
                SurfaceScreenPoint(context),
                AxisScreenPoint(context),
                context.DetentStepDegrees,
                context.DetentCount);

            Assert.That(
                context.UnwrappedAngleDegrees,
                Is.EqualTo(360f).Within(0.001f));
            Assert.That(context.AngleDegrees, Is.Zero.Within(0.001f));
            Assert.That(context.CurrentDetentIndex, Is.Zero);
            Assert.That(
                context.AudioCount("DetentCrossed") - detentAudioBefore,
                Is.EqualTo(context.DetentCount));
            Assert.That(
                context.SemanticEventCount - semanticBefore,
                Is.GreaterThanOrEqualTo(context.DetentCount + 1));

            yield return CloseTouch(10, context);
            HapticSnapshot hapticAfter = HapticSnapshot.Read();
            Assert.That(
                hapticAfter.RenderedEventCount,
                Is.GreaterThan(hapticBefore.RenderedEventCount));
            Assert.That(
                hapticAfter.SuppressedEventCount,
                Is.GreaterThan(hapticBefore.SuppressedEventCount));
            Assert.That(
                context.AudioPlaybackCount,
                Is.GreaterThan(slideAudioBefore));
            Assert.That(context.AudioReady, Is.True);
            Assert.That(context.AudioInitializationCount, Is.GreaterThanOrEqualTo(1));
            Assert.That(context.AudioVoices, Has.Length.EqualTo(6));
            Assert.That(
                context.AudioVoices.All(source =>
                    source != null
                    && source.enabled
                    && !source.playOnAwake
                    && !source.loop),
                Is.True);
            Assert.That(context.TouchReceiptCount, Is.GreaterThan(0));
            Assert.That(context.SlideInputCount, Is.GreaterThan(0));
            Assert.That(context.RotationInputCount, Is.GreaterThan(0));
            Assert.That(context.IsPoseLegal, Is.True);
            Assert.That(context.OutOfPlaneSlideResidualMeters, Is.Zero);
            Assert.That(context.TopStackHeightResidualMeters, Is.LessThan(0.000001f));
            Assert.That(
                MatrixDifference(
                    FindTransform(context.Candidate.transform, "BottomExterior")
                        .localToWorldMatrix,
                    bottomBaseline),
                Is.Zero);
            Assert.That(
                MatrixDifference(
                    context.FixedAxis.localToWorldMatrix,
                    axisBaseline),
                Is.Zero);
        }

        [UnityTest]
        public IEnumerator TouchEventsArbitrateToyOrbitAndPinch()
        {
            RuntimeContext context = RuntimeContext.Resolve();
            float travelAtStart = context.TravelMeters;
            float yawAtStart = context.YawOffset;

            yield return DragTouch(
                21,
                new Vector2(8f, Screen.height * 0.52f),
                new Vector2(
                    Mathf.Min(Screen.width * 0.25f, 120f),
                    Screen.height * 0.62f),
                4);
            Assert.That(context.YawOffset, Is.Not.EqualTo(yawAtStart));
            Assert.That(context.OrbitUpdateCount, Is.GreaterThan(0));
            Assert.That(
                context.TravelMeters,
                Is.EqualTo(travelAtStart).Within(0.000001f));

            float zoomBefore = context.TargetZoomScale;
            Vector2 pinchLeft = new(
                Screen.width * 0.20f,
                Screen.height * 0.28f);
            Vector2 pinchRight = new(
                Screen.width * 0.80f,
                Screen.height * 0.28f);
            QueueTouchEvent(22, TouchPhase.Began, pinchLeft, Vector2.zero);
            QueueTouchEvent(23, TouchPhase.Began, pinchRight, Vector2.zero);
            yield return null;
            Vector2 widerLeft = pinchLeft + Vector2.left * 40f;
            Vector2 widerRight = pinchRight + Vector2.right * 40f;
            QueueTouchEvent(
                22,
                TouchPhase.Moved,
                widerLeft,
                widerLeft - pinchLeft);
            QueueTouchEvent(
                23,
                TouchPhase.Moved,
                widerRight,
                widerRight - pinchRight);
            yield return null;
            Assert.That(context.PinchUpdateCount, Is.GreaterThan(0));
            Assert.That(context.TargetZoomScale, Is.LessThan(zoomBefore));
            Assert.That(context.IsDragging, Is.False);
            Assert.That(
                context.TravelMeters,
                Is.EqualTo(travelAtStart).Within(0.000001f));

            QueueTouchEvent(23, TouchPhase.Ended, widerRight, Vector2.zero);
            yield return null;
            float travelWithOnePinchTouch = context.TravelMeters;
            QueueTouchEvent(
                22,
                TouchPhase.Moved,
                widerLeft + Vector2.down * 100f,
                Vector2.down * 100f);
            yield return null;
            Assert.That(
                context.TravelMeters,
                Is.EqualTo(travelWithOnePinchTouch).Within(0.000001f));
            QueueTouchEvent(
                22,
                TouchPhase.Ended,
                widerLeft + Vector2.down * 100f,
                Vector2.zero);
            yield return null;
            yield return null;

            int orbitBeforeToy = context.OrbitUpdateCount;
            yield return OpenTouch(24, context, 0.45f);
            Assert.That(context.TravelMeters, Is.GreaterThan(0f));
            Assert.That(context.OrbitUpdateCount, Is.EqualTo(orbitBeforeToy));
            Assert.That(context.SlideInputCount, Is.GreaterThan(0));
        }

        [UnityTest]
        public IEnumerator TouchArcsPreserveVisualDirectionAcrossOrbitAndZoom()
        {
            RuntimeContext context = RuntimeContext.Resolve();
            yield return OpenTouch(31, context);

            int clockwiseDirection =
                LocalDirectionForScreenArc(context, true);
            Vector2 start = SurfaceScreenPoint(context);
            AssertScreenArcDirection(
                context,
                start,
                clockwiseDirection * context.DetentStepDegrees,
                true);
            var clockwiseDetents = new List<int>();
            yield return RotateTouch(
                32,
                start,
                AxisScreenPoint(context),
                clockwiseDirection * context.DetentStepDegrees,
                1,
                context,
                clockwiseDetents);
            Assert.That(
                context.UnwrappedAngleDegrees,
                Is.EqualTo(clockwiseDirection * 12f).Within(0.001f));
            Assert.That(clockwiseDetents, Is.EqualTo(
                new[] { clockwiseDirection }));
            AssertDirectionMetadata(context, clockwiseDirection);

            yield return RotateTouch(
                33,
                SurfaceScreenPoint(context),
                AxisScreenPoint(context),
                -clockwiseDirection * context.DetentStepDegrees,
                1,
                context);
            Assert.That(context.AngleDegrees, Is.Zero.Within(0.001f));
            yield return CloseTouch(34, context);
            Assert.That(
                context.TravelMeters,
                Is.LessThanOrEqualTo(context.EndpointToleranceMeters));

            context.ResetPose();
            yield return OpenTouch(35, context);
            float yawBefore = context.YawOffset;
            yield return DragTouch(
                36,
                new Vector2(8f, Screen.height * 0.52f),
                new Vector2(120f, Screen.height * 0.52f),
                4);
            Assert.That(context.YawOffset, Is.GreaterThan(yawBefore));
            int counterclockwiseDirection =
                LocalDirectionForScreenArc(context, false);
            start = SurfaceScreenPoint(context);
            AssertScreenArcDirection(
                context,
                start,
                counterclockwiseDirection * 36f,
                false);
            var counterclockwiseDetents = new List<int>();
            yield return RotateTouch(
                37,
                start,
                AxisScreenPoint(context),
                counterclockwiseDirection * context.DetentStepDegrees,
                3,
                context,
                counterclockwiseDetents);
            Assert.That(
                context.UnwrappedAngleDegrees,
                Is.EqualTo(counterclockwiseDirection * 36f).Within(0.001f));
            Assert.That(
                counterclockwiseDetents,
                Is.EqualTo(Enumerable.Range(1, 3)
                    .Select(index => counterclockwiseDirection * index)));
            AssertDirectionMetadata(context, counterclockwiseDirection);

            context.ResetPose();
            float zoomBefore = context.TargetZoomScale;
            yield return PinchOut(38, 39);
            Assert.That(context.TargetZoomScale, Is.LessThan(zoomBefore));
            yield return OpenTouch(40, context);
            clockwiseDirection = LocalDirectionForScreenArc(context, true);
            start = SurfaceScreenPoint(context);
            AssertScreenArcDirection(
                context,
                start,
                clockwiseDirection * 24f,
                true);
            int audioBefore = context.AudioCount("DetentCrossed");
            var fullTurnDetents = new List<int>();
            yield return RotateTouch(
                41,
                start,
                AxisScreenPoint(context),
                clockwiseDirection * context.DetentStepDegrees,
                context.DetentCount,
                context,
                fullTurnDetents);
            Assert.That(
                context.UnwrappedAngleDegrees,
                Is.EqualTo(clockwiseDirection * 360f).Within(0.001f));
            Assert.That(context.AngleDegrees, Is.Zero.Within(0.001f));
            Assert.That(fullTurnDetents.Count, Is.EqualTo(context.DetentCount));
            Assert.That(
                fullTurnDetents,
                Is.EqualTo(Enumerable.Range(1, context.DetentCount)
                    .Select(index => clockwiseDirection * index)));
            Assert.That(
                context.AudioCount("DetentCrossed") - audioBefore,
                Is.EqualTo(context.DetentCount));
            AssertDirectionMetadata(context, clockwiseDirection);
            yield return CloseTouch(42, context);
            for (int frame = 0; frame < 20; frame++)
                yield return null;
            Assert.That(
                context.TravelMeters,
                Is.LessThanOrEqualTo(context.EndpointToleranceMeters));
            Assert.That(context.AngleDegrees, Is.Zero.Within(0.001f));
            Assert.That(context.LinearVelocity, Is.Zero);
            Assert.That(context.AngularVelocity, Is.Zero);
            Assert.That(context.IsDragging, Is.False);
            Assert.That(context.IsPoseLegal, Is.True);
            context.ResetPose();
            AssertRest(context);
        }

        [UnityTest]
        public IEnumerator ReloadAndIdleFramesPreserveZeroMotion()
        {
            RuntimeContext before = RuntimeContext.Resolve();
            Matrix4x4 bottomBaseline =
                FindTransform(before.Candidate.transform, "BottomExterior")
                    .localToWorldMatrix;
            Matrix4x4 axisBaseline = before.FixedAxis.localToWorldMatrix;
            for (int frame = 0; frame < 30; frame++)
                yield return null;
            AssertRest(before);
            Assert.That(
                MatrixDifference(
                    FindTransform(before.Candidate.transform, "BottomExterior")
                        .localToWorldMatrix,
                    bottomBaseline),
                Is.Zero);
            Assert.That(
                MatrixDifference(
                    before.FixedAxis.localToWorldMatrix,
                    axisBaseline),
                Is.Zero);

            AsyncOperation reload = SceneManager.LoadSceneAsync(SceneName);
            Assert.That(reload, Is.Not.Null);
            while (!reload.isDone)
                yield return null;
            yield return null;
            yield return null;
            RuntimeContext after = RuntimeContext.Resolve();
            AssertRest(after);
            Assert.That(after.CandidateActive, Is.True);
            Assert.That(after.FallbackActive, Is.False);
            Assert.That(after.CameraTarget, Is.SameAs(after.Candidate.transform));
            Assert.That(after.UsesStableCameraBounds, Is.True);
            Assert.That(after.PreservesAuthoredCameraPose, Is.True);
            Assert.That(after.AudioReady, Is.True);
        }

        private IEnumerator OpenTouch(
            int touchId,
            RuntimeContext context,
            float fraction = 1.2f)
        {
            Physics.SyncTransforms();
            Vector2 start = SurfaceScreenPoint(context);
            yield return DragTouch(
                touchId,
                start,
                start + SlideScreenDelta(context) * fraction,
                6);
        }

        private IEnumerator CloseTouch(
            int touchId,
            RuntimeContext context)
        {
            Physics.SyncTransforms();
            Vector2 start = SurfaceScreenPoint(context);
            yield return DragTouch(
                touchId,
                start,
                start - SlideScreenDelta(context) * 1.25f,
                6);
        }

        private IEnumerator DragTouch(
            int touchId,
            Vector2 start,
            Vector2 end,
            int segments)
        {
            QueueTouchEvent(
                touchId,
                TouchPhase.Began,
                start,
                Vector2.zero);
            yield return null;
            Vector2 previous = start;
            for (int segment = 1; segment <= segments; segment++)
            {
                Vector2 current = Vector2.Lerp(
                    start,
                    end,
                    (float)segment / segments);
                QueueTouchEvent(
                    touchId,
                    TouchPhase.Moved,
                    current,
                    current - previous);
                previous = current;
                yield return null;
            }
            QueueTouchEvent(
                touchId,
                TouchPhase.Ended,
                end,
                Vector2.zero);
            yield return null;
            yield return null;
        }

        private IEnumerator PinchOut(int leftTouchId, int rightTouchId)
        {
            Vector2 left = new(Screen.width * 0.28f, Screen.height * 0.24f);
            Vector2 right = new(Screen.width * 0.72f, Screen.height * 0.24f);
            QueueTouchEvent(leftTouchId, TouchPhase.Began, left, Vector2.zero);
            QueueTouchEvent(rightTouchId, TouchPhase.Began, right, Vector2.zero);
            yield return null;
            Vector2 widerLeft = left + Vector2.left * 36f;
            Vector2 widerRight = right + Vector2.right * 36f;
            QueueTouchEvent(
                leftTouchId,
                TouchPhase.Moved,
                widerLeft,
                widerLeft - left);
            QueueTouchEvent(
                rightTouchId,
                TouchPhase.Moved,
                widerRight,
                widerRight - right);
            yield return null;
            QueueTouchEvent(
                leftTouchId,
                TouchPhase.Ended,
                widerLeft,
                Vector2.zero);
            QueueTouchEvent(
                rightTouchId,
                TouchPhase.Ended,
                widerRight,
                Vector2.zero);
            yield return null;
            yield return null;
        }

        private IEnumerator RotateTouch(
            int touchId,
            Vector2 start,
            Vector2 pivot,
            float stepDegrees,
            int stepCount,
            RuntimeContext context = null,
            IList<int> observedDetents = null)
        {
            if (stepCount <= 0)
                yield break;
            context ??= RuntimeContext.Resolve();
            Camera camera = context.InteractionCamera;
            Vector3 pivotWorld = context.FixedAxis.position;
            Vector3 axisWorld = context.RotatingCarrier
                .TransformDirection(Vector3.forward)
                .normalized;
            Plane plane = new(axisWorld, pivotWorld);
            Ray startRay = camera.ScreenPointToRay(start);
            Assert.That(plane.Raycast(startRay, out float distance), Is.True);
            Vector3 radial = Vector3.ProjectOnPlane(
                startRay.GetPoint(distance) - pivotWorld,
                axisWorld);
            Assert.That(radial.magnitude, Is.GreaterThan(0.0005f));
            QueueTouchEvent(
                touchId,
                TouchPhase.Began,
                start,
                Vector2.zero);
            yield return null;
            Vector2 previous = start;
            for (int step = 1; step <= stepCount; step++)
            {
                Vector3 world = pivotWorld
                    + Quaternion.AngleAxis(
                        stepDegrees * step,
                        axisWorld) * radial;
                Vector2 current = camera.WorldToScreenPoint(world);
                QueueTouchEvent(
                    touchId,
                    TouchPhase.Moved,
                    current,
                    current - previous);
                previous = current;
                yield return null;
                if (observedDetents != null
                    && context.LastSemanticDetentIndex != 0
                    && (observedDetents.Count == 0
                        || observedDetents[^1]
                            != context.LastSemanticDetentIndex))
                {
                    observedDetents.Add(context.LastSemanticDetentIndex);
                }
            }
            QueueTouchEvent(
                touchId,
                TouchPhase.Ended,
                previous,
                Vector2.zero);
            yield return null;
            yield return null;
        }

        private void QueueTouchEvent(
            int touchId,
            TouchPhase phase,
            Vector2 position,
            Vector2 delta)
        {
            InputSystem.QueueStateEvent(
                touchscreen,
                new TouchState
                {
                    touchId = touchId,
                    phase = phase,
                    position = position,
                    delta = delta,
                    pressure = 1f,
                },
                InputState.currentTime);
        }

        private static Vector2 SurfaceScreenPoint(RuntimeContext context)
        {
            Physics.SyncTransforms();
            Collider surface = context.InteractionSurface;
            Camera camera = context.InteractionCamera;
            Vector3 projected = camera.WorldToScreenPoint(
                surface.bounds.center);
            Assert.That(projected.z, Is.GreaterThan(0f));
            Ray ray = camera.ScreenPointToRay(projected);
            Assert.That(surface.Raycast(ray, out _, 5f), Is.True);
            return projected;
        }

        private static Vector2 AxisScreenPoint(RuntimeContext context)
        {
            return context.InteractionCamera.WorldToScreenPoint(
                context.FixedAxis.position);
        }

        private static int LocalDirectionForScreenArc(
            RuntimeContext context,
            bool clockwise)
        {
            Camera camera = context.InteractionCamera;
            Vector3 pivotWorld = context.FixedAxis.position;
            Vector3 axisWorld = context.RotatingCarrier
                .TransformDirection(Vector3.forward)
                .normalized;
            Vector3 toCamera =
                (camera.transform.position - pivotWorld).normalized;
            float facing = Vector3.Dot(axisWorld, toCamera);
            Assert.That(Mathf.Abs(facing), Is.GreaterThan(0.1f));
            Vector2 start = SurfaceScreenPoint(context);
            Plane plane = new(axisWorld, pivotWorld);
            Ray ray = camera.ScreenPointToRay(start);
            Assert.That(plane.Raycast(ray, out float distance), Is.True);
            Vector3 radial = Vector3.ProjectOnPlane(
                ray.GetPoint(distance) - pivotWorld,
                axisWorld);
            Vector2 pivot = camera.WorldToScreenPoint(pivotWorld);
            Vector2 positiveEnd = camera.WorldToScreenPoint(
                pivotWorld + Quaternion.AngleAxis(5f, axisWorld) * radial);
            Vector2 startRadial = start - pivot;
            Vector2 endRadial = positiveEnd - pivot;
            float positiveCross = startRadial.x * endRadial.y
                - startRadial.y * endRadial.x;
            int clockwiseLocalDirection = positiveCross < 0f ? 1 : -1;
            return clockwise ? clockwiseLocalDirection : -clockwiseLocalDirection;
        }

        private static void AssertScreenArcDirection(
            RuntimeContext context,
            Vector2 start,
            float localDegrees,
            bool clockwise)
        {
            Camera camera = context.InteractionCamera;
            Vector3 pivotWorld = context.FixedAxis.position;
            Vector3 axisWorld = context.RotatingCarrier
                .TransformDirection(Vector3.forward)
                .normalized;
            Plane plane = new(axisWorld, pivotWorld);
            Ray ray = camera.ScreenPointToRay(start);
            Assert.That(plane.Raycast(ray, out float distance), Is.True);
            Vector3 radial = Vector3.ProjectOnPlane(
                ray.GetPoint(distance) - pivotWorld,
                axisWorld);
            Vector2 pivot = camera.WorldToScreenPoint(pivotWorld);
            Vector2 end = camera.WorldToScreenPoint(
                pivotWorld
                + Quaternion.AngleAxis(localDegrees, axisWorld) * radial);
            Vector2 startRadial = start - pivot;
            Vector2 endRadial = end - pivot;
            float cross = startRadial.x * endRadial.y
                - startRadial.y * endRadial.x;
            Assert.That(
                clockwise ? cross : -cross,
                Is.LessThan(-0.01f));
        }

        private static void AssertDirectionMetadata(
            RuntimeContext context,
            int expectedDirection)
        {
            Assert.That(
                context.LastSemanticDetentDirection,
                Is.EqualTo(expectedDirection));
            Assert.That(
                context.LastAudioDetentDirection,
                Is.EqualTo(expectedDirection));
            Assert.That(
                context.LastAudioDetentIndex,
                Is.EqualTo(context.LastSemanticDetentIndex));
            HapticSnapshot haptic = HapticSnapshot.Read();
            Assert.That(
                haptic.MagneticSliderDirection,
                Is.EqualTo(expectedDirection));
            Assert.That(
                haptic.MagneticSliderDetentIndex,
                Is.EqualTo(context.LastSemanticDetentIndex));
        }

        private static Vector2 SlideScreenDelta(RuntimeContext context)
        {
            Vector3 center = context.InteractionSurface.bounds.center;
            Vector3 worldSlide = context.TopLocalSlide.parent.TransformVector(
                Vector3.down * context.MaximumTravelMeters);
            return (Vector2)context.InteractionCamera.WorldToScreenPoint(
                    center + worldSlide)
                - (Vector2)context.InteractionCamera.WorldToScreenPoint(center);
        }

        private static void AssertRest(RuntimeContext context)
        {
            Assert.That(context.TravelMeters, Is.Zero);
            Assert.That(context.AngleDegrees, Is.Zero);
            Assert.That(context.UnwrappedAngleDegrees, Is.Zero);
            Assert.That(context.LinearVelocity, Is.Zero);
            Assert.That(context.AngularVelocity, Is.Zero);
            Assert.That(context.IsDragging, Is.False);
            Assert.That(context.IsPoseLegal, Is.True);
        }

        private static Transform FindTransform(
            Transform root,
            string name)
        {
            Transform result = root.GetComponentsInChildren<Transform>(true)
                .SingleOrDefault(item => item.name == name);
            Assert.That(result, Is.Not.Null, name);
            return result;
        }

        private static float MatrixDifference(Matrix4x4 a, Matrix4x4 b)
        {
            float maximum = 0f;
            for (int row = 0; row < 4; row++)
            for (int column = 0; column < 4; column++)
                maximum = Mathf.Max(
                    maximum,
                    Mathf.Abs(a[row, column] - b[row, column]));
            return maximum;
        }

        private sealed class RuntimeContext
        {
            private readonly Component coordinator;
            private readonly Component mechanism;
            private readonly Component input;
            private readonly Component gestures;
            private readonly Component framer;
            private readonly Component audio;
            private readonly object settings;

            private RuntimeContext(
                Component coordinator,
                Component mechanism,
                Component input,
                Component gestures,
                Component framer,
                Component audio,
                object settings,
                GameObject candidate)
            {
                this.coordinator = coordinator;
                this.mechanism = mechanism;
                this.input = input;
                this.gestures = gestures;
                this.framer = framer;
                this.audio = audio;
                this.settings = settings;
                Candidate = candidate;
            }

            public static RuntimeContext Resolve()
            {
                Component coordinator = FindActiveComponent(
                    "FidgetingApp.EDC.Gate12R002."
                    + "MagneticSlideTileShippingCoordinator");
                GameObject candidate = Get<GameObject>(
                    coordinator,
                    "CandidateModel");
                Component mechanism = Get<Component>(
                    coordinator,
                    "Mechanism");
                Type inputType = RequireType(
                    "FidgetingApp.EDC.EdcSliderController");
                Type gesturesType = RequireType(
                    "FidgetingApp.EDC.SharedPresentationGestureController");
                Type framerType = RequireType(
                    "FidgetingApp.EDC.EdcPortraitCameraFramer");
                Type audioType = RequireType(
                    "FidgetingApp.EDC.MagneticSlideDetentAudio");
                Component input = candidate.GetComponent(inputType);
                Component gestures = Camera.main.GetComponent(gesturesType);
                Component framer = Camera.main.GetComponent(framerType);
                Component audio = candidate
                    .GetComponentsInChildren(audioType, true)
                    .Single();
                Assert.That(input, Is.Not.Null);
                Assert.That(gestures, Is.Not.Null);
                Assert.That(framer, Is.Not.Null);
                Assert.That(audio, Is.Not.Null);
                return new RuntimeContext(
                    coordinator,
                    mechanism,
                    input,
                    gestures,
                    framer,
                    audio,
                    Get<object>(coordinator, "Settings"),
                    candidate);
            }

            public GameObject Candidate { get; }
            public bool CandidateActive =>
                Get<bool>(coordinator, "CandidateModelActive");
            public bool FallbackActive =>
                Get<bool>(coordinator, "FallbackModelActive");
            public float TravelMeters => Get<float>(mechanism, "TravelMeters");
            public float AngleDegrees => Get<float>(mechanism, "AngleDegrees");
            public float UnwrappedAngleDegrees =>
                Get<float>(mechanism, "UnwrappedAngleDegrees");
            public float LinearVelocity =>
                Get<float>(mechanism, "LinearVelocityMetersPerSecond");
            public float AngularVelocity =>
                Get<float>(mechanism, "AngularVelocityDegreesPerSecond");
            public int CurrentDetentIndex =>
                Get<int>(mechanism, "CurrentDetentIndex");
            public int UnwrappedDetentIndex =>
                Get<int>(mechanism, "UnwrappedDetentIndex");
            public bool AtMaximumTravel =>
                Get<bool>(mechanism, "AtMaximumTravel");
            public float OutOfPlaneSlideResidualMeters =>
                Get<float>(mechanism, "OutOfPlaneSlideResidualMeters");
            public float TopStackHeightResidualMeters =>
                Get<float>(mechanism, "TopStackHeightResidualMeters");
            public bool IsPoseLegal =>
                Invoke<bool>(mechanism, "IsPoseLegal");
            public Transform FixedAxis =>
                Get<Transform>(mechanism, "FixedAxis");
            public Transform RotatingCarrier =>
                Get<Transform>(mechanism, "RotatingCarrier");
            public Transform TopLocalSlide =>
                Get<Transform>(mechanism, "TopLocalSlide");
            public Collider InteractionSurface =>
                Get<Collider>(input, "InteractionSurface");
            public Camera InteractionCamera =>
                Get<Camera>(input, "InteractionCamera");
            public bool IsDragging => Get<bool>(input, "IsDragging");
            public int TouchReceiptCount =>
                Get<int>(input, "TouchReceiptCount");
            public int SlideInputCount =>
                Get<int>(input, "SlideInputCount");
            public int RotationInputCount =>
                Get<int>(input, "RotationInputCount");
            public int SemanticEventCount =>
                Get<int>(input, "SemanticEventCount");
            public int LastSemanticDetentDirection =>
                Get<int>(input, "LastSemanticDetentDirection");
            public int LastSemanticDetentIndex =>
                Get<int>(input, "LastSemanticDetentIndex");
            public float YawOffset => Get<float>(framer, "YawOffset");
            public float TargetZoomScale =>
                Get<float>(framer, "TargetZoomScale");
            public int OrbitUpdateCount =>
                Get<int>(gestures, "OrbitUpdateCount");
            public int PinchUpdateCount =>
                Get<int>(gestures, "PinchUpdateCount");
            public Transform CameraTarget => Get<Transform>(framer, "Target");
            public bool UsesStableCameraBounds =>
                Get<bool>(framer, "UsesStableLocalBounds");
            public bool PreservesAuthoredCameraPose =>
                Get<bool>(framer, "PreservesAuthoredDefaultPose");
            public bool AudioReady => Get<bool>(audio, "AudioReady");
            public int AudioPlaybackCount =>
                Get<int>(audio, "PlaybackCount");
            public int AudioInitializationCount =>
                Get<int>(audio, "InitializationCount");
            public int LastAudioDetentDirection =>
                Get<int>(audio, "LastDetentDirection");
            public int LastAudioDetentIndex =>
                Get<int>(audio, "LastDetentIndex");
            public AudioSource[] AudioVoices =>
                Get<AudioSource[]>(audio, "Voices");
            public float MaximumTravelMeters =>
                Get<float>(settings, "MaximumTravelMeters");
            public float EndpointToleranceMeters =>
                Get<float>(settings, "EndpointToleranceMeters");
            public int SlideStepCount =>
                Get<int>(settings, "SlideStepCount");
            public int DetentCount => Get<int>(settings, "DetentCount");
            public float DetentStepDegrees =>
                Get<float>(settings, "DetentStepDegrees");

            public int AudioCount(string semanticName)
            {
                Type semanticType = RequireType(
                    "CodexUnityLab.FidgetSemanticEvent");
                object semantic = Enum.Parse(semanticType, semanticName);
                return (int)audio.GetType()
                    .GetMethod(
                        "PlaybackCountFor",
                        BindingFlags.Instance | BindingFlags.Public)
                    .Invoke(audio, new[] { semantic });
            }

            public void ResetPose()
            {
                coordinator.GetType()
                    .GetMethod(
                        "ResetShippingPose",
                        BindingFlags.Instance | BindingFlags.Public)
                    .Invoke(coordinator, new object[] { false });
            }
        }

        private readonly struct HapticSnapshot
        {
            private HapticSnapshot(
                int renderedEventCount,
                int suppressedEventCount,
                int magneticSliderDirection,
                int magneticSliderDetentIndex)
            {
                RenderedEventCount = renderedEventCount;
                SuppressedEventCount = suppressedEventCount;
                MagneticSliderDirection = magneticSliderDirection;
                MagneticSliderDetentIndex = magneticSliderDetentIndex;
            }

            public int RenderedEventCount { get; }
            public int SuppressedEventCount { get; }
            public int MagneticSliderDirection { get; }
            public int MagneticSliderDetentIndex { get; }

            public static HapticSnapshot Read()
            {
                Type router = RequireType(
                    "CodexUnityLab.FidgetHapticRouter");
                object telemetry = router.GetMethod(
                        "GetTelemetry",
                        BindingFlags.Static | BindingFlags.Public)
                    .Invoke(null, null);
                return new HapticSnapshot(
                    Get<int>(telemetry, "RenderedEventCount"),
                    Get<int>(telemetry, "SuppressedEventCount"),
                    (int)router.GetProperty(
                            "LastMagneticSliderDirection",
                            BindingFlags.Static | BindingFlags.Public)
                        .GetValue(null),
                    (int)router.GetProperty(
                            "LastMagneticSliderDetentIndex",
                            BindingFlags.Static | BindingFlags.Public)
                        .GetValue(null));
            }
        }

        private static Component FindActiveComponent(string fullName)
        {
            Component result = UnityEngine.Object
                .FindObjectsByType<MonoBehaviour>(
                    FindObjectsInactive.Exclude,
                    FindObjectsSortMode.None)
                .FirstOrDefault(item =>
                    item.GetType().FullName == fullName);
            Assert.That(result, Is.Not.Null, fullName);
            return result;
        }

        private static Type RequireType(string fullName)
        {
            Type result = AppDomain.CurrentDomain.GetAssemblies()
                .Select(assembly => assembly.GetType(fullName, false))
                .FirstOrDefault(type => type != null);
            Assert.That(result, Is.Not.Null, fullName);
            return result;
        }

        private static T Get<T>(object instance, string propertyName)
        {
            PropertyInfo property = instance.GetType().GetProperty(
                propertyName,
                BindingFlags.Instance | BindingFlags.Public);
            Assert.That(property, Is.Not.Null, propertyName);
            return (T)property.GetValue(instance);
        }

        private static T Invoke<T>(object instance, string methodName)
        {
            MethodInfo method = instance.GetType().GetMethod(
                methodName,
                BindingFlags.Instance | BindingFlags.Public);
            Assert.That(method, Is.Not.Null, methodName);
            return (T)method.Invoke(instance, null);
        }
    }
}
