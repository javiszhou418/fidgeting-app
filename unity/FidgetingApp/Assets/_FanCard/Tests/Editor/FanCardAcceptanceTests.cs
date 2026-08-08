using System.Collections.Generic;
using System.IO;
using System.Linq;
using CodexUnityLab;
using FidgetingApp.EDC;
using FidgetingApp.EditorTools;
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
        public void ShippingGeometryPassesTheFrozenStructuralGate()
        {
            Assert.That(
                CardGeometryValidator.ValidateShippingScene(),
                Is.True,
                "The shipping scene must contain three watertight rigid slabs, "
                + "valid flat face projections, real spindle holes, and the "
                + "authored 3.75 mm spindle-axis air gaps.");
        }

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
        public void ReferenceGeometryKeepsFullCardSizeThickSidewallsAndExpandedFraming()
        {
            Assert.That(FanCardSpecifications.CardWidth, Is.EqualTo(0.0635f));
            Assert.That(FanCardSpecifications.CardHeight, Is.EqualTo(0.0889f));
            Assert.That(FanCardSpecifications.CardThickness, Is.EqualTo(0.0025f));
            Assert.That(
                FanCardSpecifications.CardWidth / FanCardSpecifications.CardHeight,
                Is.EqualTo(63.5f / 88.9f).Within(0.00001f));
            Assert.That(
                FanCardSpecifications.CardCornerRadius,
                Is.EqualTo(FanCardSpecifications.CardWidth * 0.06f));
            Assert.That(
                FanCardSpecifications.EdgeBevel,
                Is.EqualTo(FanCardSpecifications.CardThickness * 0.15f));
            Assert.That(FanCardSpecifications.LayerPitch, Is.EqualTo(0.00625f));
            Assert.That(FanCardSpecifications.AxisHoleRadius, Is.EqualTo(0.00215f));
            Assert.That(
                FanCardSpecifications.LayerPitch
                    - FanCardSpecifications.CardThickness,
                Is.GreaterThanOrEqualTo(
                    FanCardSpecifications.CardThickness * 1.5f),
                "The face-to-face air gap must be at least 1.5 slab thicknesses.");
            Assert.That(
                FanCardSpecifications.LayerPitch
                    - FanCardSpecifications.CardThickness
                    - FanCardSpecifications.FollowerBallProtrusion,
                Is.GreaterThanOrEqualTo(0.0005f),
                "The visible follower cap must clear the adjacent plate.");
            Assert.That(
                FanCardSpecifications.AxisHoleRadius
                    - FanCardSpecifications.AxisInnerRadius * 0.76f,
                Is.InRange(0.00015f, 0.00025f),
                "The spindle hole should add only a small radial clearance.");

            ProductFramingProfile framing = ProductFramingCatalog.Resolve(
                FanCardSpecifications.ScenePath);
            Assert.That(framing.DetailWidthFraction, Is.EqualTo(0.84f));
            Assert.That(framing.DetailHeightFraction, Is.EqualTo(0.78f));
            Assert.That(framing.LibraryWidthFraction, Is.EqualTo(0.79f));
            Assert.That(framing.LibraryHeightFraction, Is.EqualTo(0.73f));
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
                Quaternion.Angle(Quaternion.identity, bottom.localRotation),
                Is.EqualTo(90f).Within(0.01f));
            Assert.That(
                Quaternion.Angle(Quaternion.identity, top.localRotation),
                Is.EqualTo(0f).Within(0.01f),
                "The front/top card stays at 0 degrees while the lower cards fan beneath it.");
            Assert.That(
                Mathf.DeltaAngle(0f, middle.localEulerAngles.y),
                Is.EqualTo(45f).Within(0.01f));
            Assert.That(
                Mathf.DeltaAngle(0f, bottom.localEulerAngles.y),
                Is.EqualTo(90f).Within(0.01f));
            Vector3 openDirection = bottom.TransformPoint(
                    FanCardSpecifications.CardCenterFromPivot)
                - root.position;
            float openPlanAngle = Mathf.Atan2(
                openDirection.z,
                openDirection.x) * Mathf.Rad2Deg;
            controller.SetFanProgress(0f);
            Vector3 closedDirection = bottom.TransformPoint(
                    FanCardSpecifications.CardCenterFromPivot)
                - root.position;
            float closedPlanAngle = Mathf.Atan2(
                closedDirection.z,
                closedDirection.x) * Mathf.Rad2Deg;
            Assert.That(
                Mathf.DeltaAngle(openPlanAngle, closedPlanAngle),
                Is.EqualTo(90f).Within(0.01f),
                "The visible closing path must travel counterclockwise from 90 degrees to 0 degrees.");
            controller.SetFanProgress(1f);
            Assert.That(controller.CapturedDetentIndex, Is.EqualTo(3));
            Renderer authoredTopFace = top.Find("WarmSilverFace")
                .GetComponent<Renderer>();
            Vector3 authoredPivot = root.position;
            Assert.That(authoredPivot.x, Is.GreaterThan(authoredTopFace.bounds.center.x));
            Assert.That(authoredPivot.z, Is.LessThan(authoredTopFace.bounds.center.z),
                "In the authored top view, the common axis must sit at the top card's lower-right corner.");

            Transform[] hierarchy = root.GetComponentsInChildren<Transform>(true);
            Assert.That(
                controller.GetComponentsInChildren<Cloth>(true),
                Is.Empty,
                "Rigid cards must not contain cloth or soft-body components.");
            Assert.That(
                controller.GetComponentsInChildren<SkinnedMeshRenderer>(true),
                Is.Empty,
                "Rigid cards must not be driven by a deforming skinned mesh.");
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
                hierarchy.Count(item => item.name == "FollowerSeat_Undercut"),
                Is.EqualTo(2));
            Assert.That(
                hierarchy.Count(item => item.name == "CommonAxis_ChromeBall"),
                Is.EqualTo(1));
            Assert.That(
                hierarchy.Count(item => item.name == "CommonAxis_BallSeat"),
                Is.EqualTo(1));

            Renderer[] bodies = hierarchy
                .Where(item => item.name == "GunmetalFrame")
                .Select(item => item.GetComponent<Renderer>())
                .OrderBy(item => item.bounds.center.y)
                .ToArray();
            Assert.That(bodies, Has.Length.EqualTo(3));
            Assert.That(
                bodies.All(item => Mathf.Abs(item.bounds.size.y
                    - FanCardSpecifications.CardThickness) < 0.00001f),
                Is.True,
                "Every shipping card body must retain the authored 2.5 mm section.");
            for (int index = 1; index < bodies.Length; index++)
            {
                Assert.That(
                    bodies[index].bounds.min.y - bodies[index - 1].bounds.max.y,
                    Is.GreaterThanOrEqualTo(
                        FanCardSpecifications.CardThickness * 1.5f - 0.00001f),
                    "Adjacent card bodies must keep a physical air gap.");
            }
            Assert.That(
                hierarchy.Count(item => item.name == "WarmSilverBackFace"),
                Is.EqualTo(3),
                "All three rigid slabs need a rendered underside face.");
            Mesh projectedFaceMesh = top.Find("WarmSilverFace")
                .GetComponent<MeshFilter>().sharedMesh;
            Assert.That(
                projectedFaceMesh.vertices.All(vertex => Mathf.Abs(vertex.y) < 0.000001f),
                Is.True,
                "Face art must be a perfectly flat surface projection, not a second bent slab.");

            Mesh bodyMesh = top.Find("GunmetalFrame")
                .GetComponent<MeshFilter>().sharedMesh;
            Vector2 holeCenter = new(
                FanCardSpecifications.PivotX,
                FanCardSpecifications.PivotZ);
            Assert.That(
                CapContainsPoint(
                    bodyMesh,
                    holeCenter,
                    FanCardSpecifications.CardThickness * 0.5f),
                Is.False,
                "The common axis must pass through a real opening, not a solid cap.");
            Assert.That(
                hierarchy.Where(item => item.name == "CurvedTrack_GoldWoven")
                    .All(item => item.GetComponent<MeshFilter>().sharedMesh.bounds.center.x < 0f
                        && item.GetComponent<MeshFilter>().sharedMesh.bounds.center.z < 0f),
                Is.True,
                "Both curved tracks must stay inset toward the lower-left, not touch an edge.");
            Assert.That(
                hierarchy.Where(item => item.name.StartsWith("CurvedTrack_"))
                    .All(item => item.GetComponent<MeshFilter>().sharedMesh.vertices
                        .All(vertex => IsInsideCardOutline(vertex, 0.0005f))),
                Is.True,
                "The entire back-track projection must remain inside the card outline.");
            Assert.That(
                hierarchy.Where(item => item.name.StartsWith("CurvedTrack_"))
                    .All(item => item.localPosition.y
                        < -FanCardSpecifications.CardThickness * 0.5f
                        && item.localRotation == Quaternion.identity
                        && item.GetComponent<MeshFilter>().sharedMesh.normals
                            .All(normal => normal.y < -0.999f)),
                Is.True,
                "Both track layers must face outward from the back of their rigid slab.");
            Assert.That(
                hierarchy.Where(item => item.name.StartsWith("Magnet_"))
                    .All(item => item.localPosition.y
                        < -FanCardSpecifications.CardThickness * 0.5f),
                Is.True,
                "All magnetic detent inserts belong on the back, never the visible front face.");
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
            Assert.That(gunmetal.GetFloat("_Metallic"), Is.EqualTo(0.90f));
            Assert.That(gunmetal.GetFloat("_Smoothness"), Is.EqualTo(0.34f));
            Assert.That(silver.GetFloat("_Metallic"), Is.EqualTo(1f));
            Assert.That(silver.GetFloat("_Smoothness"), Is.EqualTo(0.36f));
            Assert.That(chrome.GetFloat("_Smoothness"), Is.EqualTo(0.92f));
            Assert.That(
                chrome.shader.name,
                Is.EqualTo("FidgetingApp/FanCardChrome"));
            Assert.That(gunmetal.GetTexture("_BumpMap"), Is.Not.Null);
            Assert.That(gunmetal.GetTexture("_BaseMap"), Is.Not.Null);
            Assert.That(
                gunmetal.shader.name,
                Is.EqualTo("FidgetingApp/FanCardGunmetal"));
            Assert.That(silver.GetTexture("_BumpMap"), Is.Not.Null);
            Assert.That(
                silver.shader.name,
                Is.EqualTo("FidgetingApp/FanCardSatinSilver"));
            Assert.That(gold.GetTexture("_BaseMap"), Is.Not.Null);

            EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            FanCardController controller =
                Object.FindAnyObjectByType<FanCardController>();
            TextMesh[] labels = controller.GetComponentsInChildren<TextMesh>(true);
            Assert.That(labels, Has.Length.EqualTo(12));
            Assert.That(
                labels.All(label => label.text == "A"
                    && label.font != null
                    && label.font.name.Contains("Oxanium")),
                Is.True,
                "Both card corners must use the bundled app typeface without clipped glyphs.");
            Assert.That(
                controller.GetComponentsInChildren<Transform>(true)
                    .Count(item => item.name.StartsWith("Spade_Etched")),
                Is.EqualTo(6));
            Assert.That(
                controller.GetComponentsInChildren<Transform>(true)
                    .Count(item => item.name.StartsWith("Spade_VerticalSlots")),
                Is.EqualTo(6));

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

        private static bool CapContainsPoint(Mesh mesh, Vector2 point, float y)
        {
            Vector3[] vertices = mesh.vertices;
            int[] triangles = mesh.triangles;
            for (int index = 0; index < triangles.Length; index += 3)
            {
                Vector3 a = vertices[triangles[index]];
                Vector3 b = vertices[triangles[index + 1]];
                Vector3 c = vertices[triangles[index + 2]];
                if (Mathf.Abs(a.y - y) > 0.00001f
                    || Mathf.Abs(b.y - y) > 0.00001f
                    || Mathf.Abs(c.y - y) > 0.00001f)
                {
                    continue;
                }
                if (PointInTriangle(
                    point,
                    new Vector2(a.x, a.z),
                    new Vector2(b.x, b.z),
                    new Vector2(c.x, c.z)))
                {
                    return true;
                }
            }
            return false;
        }

        private static bool IsInsideCardOutline(Vector3 vertex, float margin)
        {
            Vector2 center = new(
                FanCardSpecifications.CardCenterFromPivot.x,
                FanCardSpecifications.CardCenterFromPivot.z);
            Vector2 local = new(vertex.x - center.x, vertex.z - center.y);
            float halfWidth = FanCardSpecifications.CardWidth * 0.5f - margin;
            float halfHeight = FanCardSpecifications.CardHeight * 0.5f - margin;
            float radius = Mathf.Max(
                0.0001f,
                FanCardSpecifications.CardCornerRadius - margin);
            Vector2 cornerDistance = new(
                Mathf.Abs(local.x) - (halfWidth - radius),
                Mathf.Abs(local.y) - (halfHeight - radius));
            Vector2 outside = new(
                Mathf.Max(cornerDistance.x, 0f),
                Mathf.Max(cornerDistance.y, 0f));
            float signedDistance = outside.magnitude
                + Mathf.Min(Mathf.Max(cornerDistance.x, cornerDistance.y), 0f)
                - radius;
            return signedDistance <= 0.000001f;
        }

        private static bool PointInTriangle(
            Vector2 point,
            Vector2 a,
            Vector2 b,
            Vector2 c)
        {
            float d1 = Cross(point, a, b);
            float d2 = Cross(point, b, c);
            float d3 = Cross(point, c, a);
            bool hasNegative = d1 < -0.0000001f
                || d2 < -0.0000001f
                || d3 < -0.0000001f;
            bool hasPositive = d1 > 0.0000001f
                || d2 > 0.0000001f
                || d3 > 0.0000001f;
            return !(hasNegative && hasPositive);
        }

        private static float Cross(Vector2 p, Vector2 a, Vector2 b)
        {
            return (p.x - b.x) * (a.y - b.y)
                - (a.x - b.x) * (p.y - b.y);
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
