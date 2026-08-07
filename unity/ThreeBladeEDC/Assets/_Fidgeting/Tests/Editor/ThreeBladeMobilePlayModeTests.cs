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
            MobileViewerUI ui = Object.FindAnyObjectByType<MobileViewerUI>();
            ExplodedViewController exploded =
                Object.FindAnyObjectByType<ExplodedViewController>();
            Assert.That(rotor, Is.Not.Null);
            Assert.That(ui, Is.Not.Null);
            Assert.That(exploded, Is.Not.Null);
            Assert.That(Application.targetFrameRate, Is.EqualTo(60));

            ui.ToggleExploded();
            yield return new WaitForSecondsRealtime(0.55f);
            Assert.That(exploded.IsExploded, Is.True);
            Assert.That(rotor.Body.isKinematic, Is.True);

            ui.ResetPresentation();
            yield return new WaitForSecondsRealtime(0.55f);
            Assert.That(exploded.IsExploded, Is.False);
            Assert.That(rotor.Body.isKinematic, Is.False);
            Assert.That(rotor.AngularSpeedRadians, Is.EqualTo(0f).Within(0.001f));
        }

        [UnityTest]
        public IEnumerator MobileGestures_ClassifyModelAndBackgroundAndClampZoom()
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

            orbit.SetDistance(0.24f);
            orbit.ZoomByScale(100f);
            Assert.That(orbit.Distance, Is.EqualTo(0.16f).Within(0.001f));
            orbit.ZoomByScale(0.001f);
            Assert.That(orbit.Distance, Is.EqualTo(0.40f).Within(0.001f));
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
            Assert.That(rotor.MotorActive, Is.True);
            bootstrap.SendMessage("OnApplicationPause", true);
            Assert.That(rotor.MotorActive, Is.False);
            Assert.That(gestures.CurrentMode, Is.EqualTo(MobileGestureMode.None));
        }
    }
}
