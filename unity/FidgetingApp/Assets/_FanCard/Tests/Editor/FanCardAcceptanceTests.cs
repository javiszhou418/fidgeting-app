using System.Collections.Generic;
using System.IO;
using System.Linq;
using CodexUnityLab;
using FidgetingApp.EDC;
using FidgetingApp.FanCard;
using FidgetingApp.Product;
using NUnit.Framework;
using ThreeBladeEDC.Interaction;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class FanCardAcceptanceTests
    {
        [Test]
        public void ReferenceProfilePreservesApprovedFourDetentFanFeel()
        {
            FanCardDetentProfile profile = CreateProfile();
            try
            {
                Assert.That(profile.DetentCount, Is.EqualTo(4));
                Assert.That(profile.MaximumRelativeAngleDegrees, Is.EqualTo(45f));
                Assert.That(profile.MaximumTotalAngleDegrees, Is.EqualTo(90f));
                Assert.That(profile.BreakawayLoad, Is.EqualTo(0.067f));
                Assert.That(profile.HandSpring, Is.EqualTo(52f));
                Assert.That(profile.HandDamping, Is.EqualTo(8.7f));
                Assert.That(profile.MagneticForcePeak, Is.EqualTo(7.8f));
                Assert.That(profile.RailFriction, Is.EqualTo(0.72f));
                Assert.That(profile.CaptureSpring, Is.EqualTo(92f));
                Assert.That(profile.CaptureDamping, Is.EqualTo(13.6f));
                Assert.That(profile.BreakawayImpulse, Is.EqualTo(0.72f));
                Assert.That(profile.CapturePredictionSeconds, Is.EqualTo(0.055f));
                Assert.That(profile.VisiblePreloadScale, Is.EqualTo(0.28f));
                Assert.That(profile.MaximumSubstepSeconds, Is.EqualTo(1f / 240f));
            }
            finally
            {
                Object.DestroyImmediate(profile);
            }
        }

        [Test]
        public void TrackRequiresBreakawayOnceAndIsDirectionallySymmetric()
        {
            FanCardDetentProfile profile = CreateProfile();
            try
            {
                var track = new FanCardMagneticTrack(profile);
                track.ResetToDetent(1);
                float center = 1f / 3f;

                FanCardStepResult preload = track.Step(
                    1f / 60f,
                    center + profile.BreakawayLoad - 0.001f,
                    true);
                Assert.That(preload.BrokeAway, Is.False);
                Assert.That(track.State, Is.EqualTo(MagneticDetentState.Loading));
                Assert.That(track.Position, Is.EqualTo(center).Within(0.000001f));

                FanCardStepResult forward = track.Step(
                    1f / 60f,
                    center + profile.BreakawayLoad + 0.002f,
                    true);
                Assert.That(forward.BrokeAway, Is.True);
                Assert.That(
                    track.Step(1f / 60f, center + 0.20f, true).BrokeAway,
                    Is.False,
                    "One threshold crossing must produce one breakaway event.");

                track.ResetToDetent(1);
                Assert.That(
                    track.Step(
                        1f / 60f,
                        center - profile.BreakawayLoad - 0.002f,
                        true).BrokeAway,
                    Is.True,
                    "Breakaway must be symmetric in the closing direction.");
                Assert.That(track.Velocity, Is.LessThan(0f));
            }
            finally
            {
                Object.DestroyImmediate(profile);
            }
        }

        [TestCase(30)]
        [TestCase(60)]
        [TestCase(120)]
        public void ReleasedMotionSettlesExactlyAtTheSameDetentAcrossFrameRates(
            int frameRate)
        {
            FanCardDetentProfile profile = CreateProfile();
            try
            {
                FanCardMagneticTrack track = RunOpenAndRelease(profile, frameRate);
                Assert.That(track.CapturedDetentIndex, Is.EqualTo(3));
                Assert.That(track.Position, Is.EqualTo(1f).Within(0.000001f));
                Assert.That(track.Velocity, Is.EqualTo(0f));
                Assert.That(track.State, Is.EqualTo(MagneticDetentState.Captured));
            }
            finally
            {
                Object.DestroyImmediate(profile);
            }
        }

        [Test]
        public void ShippingSceneHasThreePortraitLayersSharedPivotAndInsetTrackHardware()
        {
            EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            FanCardController controller =
                Object.FindAnyObjectByType<FanCardController>();
            Assert.That(controller, Is.Not.Null);

            Transform root = controller.transform;
            Transform bottom = root.Find("BottomCard");
            Transform middle = root.Find("MiddleCard");
            Transform top = root.Find("TopCard");
            Assert.That(bottom, Is.Not.Null);
            Assert.That(middle, Is.Not.Null);
            Assert.That(top, Is.Not.Null);
            Assert.That(
                Mathf.Abs(Mathf.DeltaAngle(
                    root.localEulerAngles.y,
                    FanCardSpecifications.PresentationRotationDegrees)),
                Is.LessThan(0.01f));
            Assert.That(bottom.localPosition.x, Is.EqualTo(0f));
            Assert.That(middle.localPosition.x, Is.EqualTo(0f));
            Assert.That(top.localPosition.x, Is.EqualTo(0f));
            Assert.That(bottom.localPosition.z, Is.EqualTo(0f));
            Assert.That(middle.localPosition.z, Is.EqualTo(0f));
            Assert.That(top.localPosition.z, Is.EqualTo(0f));
            Assert.That(
                middle.localPosition.y - bottom.localPosition.y,
                Is.EqualTo(FanCardSpecifications.LayerPitch).Within(0.000001f));
            Assert.That(
                top.localPosition.y - middle.localPosition.y,
                Is.EqualTo(FanCardSpecifications.LayerPitch).Within(0.000001f));

            controller.SetFanProgress(1f);
            Assert.That(
                Quaternion.Angle(Quaternion.identity, middle.localRotation),
                Is.EqualTo(45f).Within(0.01f));
            Assert.That(
                Quaternion.Angle(Quaternion.identity, top.localRotation),
                Is.EqualTo(90f).Within(0.01f));
            Assert.That(controller.CapturedDetentIndex, Is.EqualTo(3));

            Transform[] hierarchy = root.GetComponentsInChildren<Transform>(true);
            Assert.That(
                hierarchy.Count(item => item.name == "CurvedTrack_GoldWoven"),
                Is.EqualTo(2));
            Assert.That(
                hierarchy.Count(item => item.name.StartsWith("Magnet_")),
                Is.EqualTo(6));
            Assert.That(
                hierarchy.Count(item => item.name == "FollowerBearing_Chrome"),
                Is.EqualTo(2));
            Assert.That(
                hierarchy.Count(item => item.name == "CommonAxis_ChromeBall"),
                Is.EqualTo(1));
            Assert.That(
                hierarchy.Count(item => item.name == "CommonAxis_BallSeat"),
                Is.EqualTo(1));
            Assert.That(
                hierarchy.Where(item => item.name == "CurvedTrack_GoldWoven")
                    .All(item => item.GetComponent<MeshFilter>().sharedMesh.bounds.center.x < 0f
                        && item.GetComponent<MeshFilter>().sharedMesh.bounds.center.z < 0f),
                Is.True,
                "Both curved tracks must stay inset toward the lower-left, not touch an edge.");
            Assert.That(root.GetComponentsInChildren<Rigidbody>(true), Is.Empty);
            Assert.That(root.GetComponentsInChildren<Collider>(true), Has.Length.EqualTo(1));
            Assert.That(controller.InteractionSurface, Is.SameAs(top.GetComponent<BoxCollider>()));
            Assert.That(Object.FindAnyObjectByType<EdcPortraitCameraFramer>(), Is.Not.Null);
            Assert.That(
                Object.FindAnyObjectByType<FanCardCameraProjectionGuard>(),
                Is.Not.Null);
            Assert.That(
                Object.FindAnyObjectByType<SharedPresentationGestureController>(),
                Is.Not.Null);
        }

        [Test]
        public void PortraitProjectionPreservesTheAuthoredCardWidthToHeightRatio()
        {
            EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            FanCardController controller =
                Object.FindAnyObjectByType<FanCardController>();
            Camera camera = Object.FindAnyObjectByType<Camera>();
            FanCardCameraProjectionGuard projection =
                camera.GetComponent<FanCardCameraProjectionGuard>();
            Assert.That(controller, Is.Not.Null);
            Assert.That(projection, Is.Not.Null);

            controller.SetFanProgress(0f);
            float previousAspect = camera.aspect;
            Vector3 previousPosition = camera.transform.position;
            Quaternion previousRotation = camera.transform.rotation;
            camera.aspect = 1290f / 2796f;
            projection.ApplyNow();

            Vector3 center = controller.transform.TransformPoint(
                FanCardSpecifications.CardCenterFromPivot);
            camera.transform.position = center + Vector3.up * 0.25f;
            camera.transform.rotation = Quaternion.LookRotation(
                Vector3.down,
                Vector3.forward);
            Vector3 left = camera.WorldToViewportPoint(
                center - Vector3.right * (FanCardSpecifications.CardWidth * 0.5f));
            Vector3 right = camera.WorldToViewportPoint(
                center + Vector3.right * (FanCardSpecifications.CardWidth * 0.5f));
            Vector3 bottom = camera.WorldToViewportPoint(
                center - Vector3.forward * (FanCardSpecifications.CardHeight * 0.5f));
            Vector3 top = camera.WorldToViewportPoint(
                center + Vector3.forward * (FanCardSpecifications.CardHeight * 0.5f));
            float projectedRatio = Mathf.Abs(right.x - left.x) * 1290f
                / (Mathf.Abs(top.y - bottom.y) * 2796f);

            Assert.That(camera.usePhysicalProperties, Is.False);
            Assert.That(
                projectedRatio,
                Is.EqualTo(FanCardSpecifications.CardWidth
                    / FanCardSpecifications.CardHeight).Within(0.01f),
                "The phone projection must not stretch or squeeze the 52 x 74 mm card.");

            camera.aspect = previousAspect;
            camera.transform.SetPositionAndRotation(previousPosition, previousRotation);
            camera.ResetProjectionMatrix();
        }

        [Test]
        public void ShippingMaterialsUseIndependentBeadBlastedMetalAndReadableFaceMarks()
        {
            Material gunmetal = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_FanCard/Generated/Materials/M_FanCardGunmetal.mat");
            Material silver = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_FanCard/Generated/Materials/M_FanCardWarmSilver.mat");
            Material chrome = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_FanCard/Generated/Materials/M_FanCardChrome.mat");
            Material gold = AssetDatabase.LoadAssetAtPath<Material>(
                "Assets/_FanCard/Generated/Materials/M_FanCardGoldMesh.mat");
            Assert.That(gunmetal, Is.Not.Null);
            Assert.That(silver, Is.Not.Null);
            Assert.That(chrome, Is.Not.Null);
            Assert.That(gold, Is.Not.Null);
            Assert.That(gunmetal.GetFloat("_Metallic"), Is.EqualTo(0.96f));
            Assert.That(gunmetal.GetFloat("_Smoothness"), Is.EqualTo(0.18f));
            Assert.That(silver.GetFloat("_Metallic"), Is.EqualTo(1f));
            Assert.That(silver.GetFloat("_Smoothness"), Is.EqualTo(0.22f));
            Assert.That(chrome.GetFloat("_Smoothness"), Is.EqualTo(0.97f));
            Assert.That(gunmetal.GetTexture("_BumpMap"), Is.Not.Null);
            Assert.That(silver.GetTexture("_BumpMap"), Is.Not.Null);
            Assert.That(gold.GetTexture("_BaseMap"), Is.Not.Null);

            EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            FanCardController controller =
                Object.FindAnyObjectByType<FanCardController>();
            TextMesh[] labels = controller.GetComponentsInChildren<TextMesh>(true);
            Assert.That(labels, Has.Length.EqualTo(6));
            Assert.That(
                labels.All(label => label.text == "A"
                    && label.font != null
                    && label.font.name.Contains("Oxanium")),
                Is.True,
                "Both card corners must use the bundled app typeface without clipped glyphs.");
            Assert.That(
                controller.GetComponentsInChildren<Transform>(true)
                    .Count(item => item.name == "Spade_Etched"),
                Is.EqualTo(3));
            Assert.That(
                controller.GetComponentsInChildren<Transform>(true)
                    .Count(item => item.name == "Spade_VerticalSlots"),
                Is.EqualTo(3));

            Mesh spade = AssetDatabase.LoadAssetAtPath<Mesh>(
                "Assets/_FanCard/Generated/Meshes/M_FanCardSpade.asset");
            Assert.That(spade, Is.Not.Null);
            Assert.That(spade.bounds.min.z, Is.LessThan(-0.012f));
            Assert.That(spade.bounds.max.z, Is.GreaterThan(0.012f));
            Assert.That(spade.normals.Average(normal => normal.y), Is.GreaterThan(0.9f));

            HashSet<Mesh> meshes = controller.GetComponentsInChildren<MeshFilter>(true)
                .Select(filter => filter.sharedMesh)
                .Where(mesh => mesh != null)
                .ToHashSet();
            int triangleCount = meshes.Sum(mesh => mesh.triangles.Length / 3);
            Assert.That(triangleCount, Is.LessThan(30000));
        }

        [Test]
        public void FanCardDoesNotMutateExistingRotaryOrLinearTuningAndHasNoRawHapticCall()
        {
            string controller = File.ReadAllText(
                "Assets/_FanCard/Runtime/FanCardController.cs");
            string profile = File.ReadAllText(
                "Assets/_FanCard/Runtime/FanCardDetentProfile.cs");
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");

            StringAssert.DoesNotContain("IosHaptics", controller);
            StringAssert.DoesNotContain("LinearMagneticDetentProfile", profile);
            StringAssert.DoesNotContain("RotorDetentProfile", profile);
            StringAssert.Contains("SemanticEventRaised", controller);
            StringAssert.Contains("HandleFanCardSemanticEvent", coordinator);
            StringAssert.Contains("FanCardScenePath", coordinator);
        }

        private static FanCardDetentProfile CreateProfile()
        {
            FanCardDetentProfile profile =
                ScriptableObject.CreateInstance<FanCardDetentProfile>();
            profile.ApplyReferenceDefaults();
            return profile;
        }

        private static FanCardMagneticTrack RunOpenAndRelease(
            FanCardDetentProfile profile,
            int frameRate)
        {
            var track = new FanCardMagneticTrack(profile);
            float deltaTime = 1f / frameRate;
            for (int frame = 0; frame < Mathf.CeilToInt(1.2f * frameRate); frame++)
            {
                track.Step(deltaTime, 1f, true);
            }
            track.Release();
            for (int frame = 0; frame < 8 * frameRate && !track.IsAtRest; frame++)
            {
                track.Step(deltaTime, track.Position, false);
            }
            return track;
        }
    }
}
