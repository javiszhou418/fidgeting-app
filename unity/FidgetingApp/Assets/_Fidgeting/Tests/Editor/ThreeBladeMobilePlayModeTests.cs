using System.Collections;
using NUnit.Framework;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.TestTools;

namespace ThreeBladeEDC.Tests.Editor
{
    public sealed class ThreeBladeMobilePlayModeTests
    {
        private const string ScenePath =
            "Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity";

        [UnityTearDown]
        public IEnumerator EnsureEditMode()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                yield return new ExitPlayMode();
            }
        }

        [UnityTest]
        public IEnumerator MobileViewer_EntersPlayModeAndRestoresExplodedPhysics()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            yield return new EnterPlayMode();
            yield return null;

            RotorRigidbodyController rotor =
                Object.FindAnyObjectByType<RotorRigidbodyController>();
            ExplodedViewController exploded =
                Object.FindAnyObjectByType<ExplodedViewController>();
            Assert.That(rotor, Is.Not.Null);
            Assert.That(exploded, Is.Not.Null);
            Assert.That(Application.targetFrameRate, Is.EqualTo(60));

            exploded.SetExploded(true);
            yield return new WaitForSecondsRealtime(0.55f);
            Assert.That(exploded.IsExploded, Is.True);
            Assert.That(rotor.Body.isKinematic, Is.True);

            exploded.SetExploded(false);
            rotor.ResetRotor();
            yield return new WaitForSecondsRealtime(0.55f);
            Assert.That(exploded.IsExploded, Is.False);
            Assert.That(rotor.Body.isKinematic, Is.False);
            Assert.That(rotor.AngularSpeedRadians, Is.EqualTo(0f).Within(0.001f));
        }

        [UnityTest]
        public IEnumerator MobileGestures_OrbitKeepsScaleAndPinchZoomClamps()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            yield return new EnterPlayMode();
            yield return null;

            MobileGestureController gestures =
                Object.FindAnyObjectByType<MobileGestureController>();
            OrbitPresentationCamera orbit =
                Object.FindAnyObjectByType<OrbitPresentationCamera>();
            Assert.That(gestures, Is.Not.Null);
            Assert.That(orbit, Is.Not.Null);

            Physics.SyncTransforms();
            Assert.That(
                gestures.ClassifyScreenPoint(
                    new Vector2(Screen.width * 0.5f, Screen.height * 0.5f)),
                Is.EqualTo(MobileGestureMode.Spin));
            Assert.That(
                gestures.ClassifyScreenPoint(new Vector2(4f, 4f)),
                Is.EqualTo(MobileGestureMode.Orbit));

            Camera camera = Camera.main;
            Assert.That(camera, Is.Not.Null);
            Vector3 projectedPivot = camera.WorldToScreenPoint(
                gestures.Rotor.PivotWorld);
            float shortSide = Mathf.Min(Screen.width, Screen.height);
            Vector2 formerOversizedSpinPoint = new Vector2(
                projectedPivot.x + shortSide * 0.42f,
                projectedPivot.y);
            Assert.That(
                gestures.ClassifyScreenPoint(formerOversizedSpinPoint),
                Is.EqualTo(MobileGestureMode.Orbit),
                "The old 48% fallback consumed this outer camera-orbit band.");

            orbit.ResetHero();
            float boundsFramedDistance = orbit.Distance;
            orbit.OrbitByPixels(new Vector2(96f, -48f));
            Assert.That(
                orbit.Distance,
                Is.EqualTo(boundsFramedDistance).Within(0.0001f),
                "A single-finger orbit must not change camera distance.");

            orbit.ResetHero();
            boundsFramedDistance = orbit.Distance;
            orbit.ZoomByScale(100f);
            Assert.That(
                orbit.Distance,
                Is.EqualTo(
                    boundsFramedDistance
                    * OrbitPresentationCamera.MinimumUserZoomScale)
                    .Within(0.001f));
            orbit.ZoomByScale(0.001f);
            Assert.That(
                orbit.Distance,
                Is.EqualTo(
                    boundsFramedDistance
                    * OrbitPresentationCamera.MaximumUserZoomScale)
                    .Within(0.001f));
        }

        [UnityTest]
        public IEnumerator MobilePause_CancelsMotorAndGestureState()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            yield return new EnterPlayMode();
            yield return null;

            RotorRigidbodyController rotor =
                Object.FindAnyObjectByType<RotorRigidbodyController>();
            MobileGestureController gestures =
                Object.FindAnyObjectByType<MobileGestureController>();
            MobileRuntimeBootstrap bootstrap =
                Object.FindAnyObjectByType<MobileRuntimeBootstrap>();
            Assert.That(rotor, Is.Not.Null);
            Assert.That(gestures, Is.Not.Null);
            Assert.That(bootstrap, Is.Not.Null);

            rotor.SetMotorActive(true);
            Assert.That(
                rotor.MotorActive,
                Is.False,
                "Product rotor must never acquire speed from the historical demo motor.");
            bootstrap.SendMessage("OnApplicationPause", true);
            Assert.That(rotor.MotorActive, Is.False);
            Assert.That(gestures.CurrentMode, Is.EqualTo(MobileGestureMode.None));
        }

        [UnityTest]
        public IEnumerator MagneticDetent_RequiresBreakawayAndCapturesAtRest()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            yield return new EnterPlayMode();
            yield return null;

            RotorRigidbodyController rotor =
                Object.FindAnyObjectByType<RotorRigidbodyController>();
            Assert.That(rotor, Is.Not.Null);
            rotor.SetResistanceMode(SpinnerResistanceMode.MagneticDetent);
            rotor.SetMagneticBreakawaySpeed(2f);
            rotor.ResetRotor();

            rotor.BeginFingerControl();
            Assert.That(rotor.DriveFromFinger(1.9f), Is.False);
            Assert.That(rotor.DriveFromFinger(2.1f), Is.True);
            rotor.EndFingerControl();
        }

        [UnityTest]
        public IEnumerator MetalGlint_UsesRealSpeedAndResetReturnsToDark()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            yield return new EnterPlayMode();
            yield return null;

            RotorRigidbodyController rotor =
                Object.FindAnyObjectByType<RotorRigidbodyController>();
            MetalGlintController glint =
                Object.FindAnyObjectByType<MetalGlintController>();
            Assert.That(rotor, Is.Not.Null);
            Assert.That(glint, Is.Not.Null);
            Assert.That(glint.Rotor, Is.SameAs(rotor));
            Assert.That(glint.CurrentIntensity, Is.Zero.Within(0.001f));

            rotor.Body.angularVelocity = rotor.SpinAxisWorld * 24f;
            yield return new WaitForSecondsRealtime(0.05f);
            Assert.That(
                rotor.AngularSpeedRadians,
                Is.GreaterThan(0f),
                "The test Rigidbody must hold real axial speed before evaluating visuals.");
            Assert.That(
                glint.CurrentIntensity,
                Is.GreaterThan(0f),
                "A local glint may appear only after real rotor speed exists.");

            rotor.ResetRotor();
            yield return null;
            Assert.That(rotor.AngularSpeedRadians, Is.Zero.Within(0.001f));
            Assert.That(
                glint.CurrentIntensity,
                Is.Zero.Within(0.001f),
                "Reset must clear both physical motion and the visual glint.");
        }
    }
}
