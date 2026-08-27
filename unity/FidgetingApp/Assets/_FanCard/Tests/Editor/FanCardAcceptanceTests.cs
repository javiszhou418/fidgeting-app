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
                + "authored 1.0 mm spindle-axis air gaps.");
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
                Assert.That(profile.BreakawayLoad, Is.EqualTo(0.050f));
                Assert.That(profile.HandSpring, Is.EqualTo(96f));
                Assert.That(profile.HandDamping, Is.EqualTo(6.0f));
                Assert.That(profile.MagneticForcePeak, Is.EqualTo(6.4f));
                Assert.That(profile.RailFriction, Is.EqualTo(0.38f));
                Assert.That(profile.CaptureSpring, Is.EqualTo(118f));
                Assert.That(profile.CaptureDamping, Is.EqualTo(14.2f));
                Assert.That(profile.BreakawayImpulse, Is.EqualTo(0.95f));
                Assert.That(profile.CapturePredictionSeconds, Is.EqualTo(0.070f));
                Assert.That(profile.VisiblePreloadScale, Is.EqualTo(0.24f));
                Assert.That(profile.MaximumHeldSpeed, Is.EqualTo(2.4f));
                Assert.That(profile.FastBreakawayLoad, Is.EqualTo(0.024f));
                Assert.That(profile.FastHandSpring, Is.EqualTo(220f));
                Assert.That(profile.FastHandDamping, Is.EqualTo(5.2f));
                Assert.That(profile.FastMagneticForceScale, Is.EqualTo(0.50f));
                Assert.That(profile.FastRailFriction, Is.EqualTo(0.16f));
                Assert.That(profile.FastBreakawayImpulse, Is.EqualTo(1.8f));
                Assert.That(profile.FastMaximumHeldSpeed, Is.EqualTo(5.0f));
                Assert.That(profile.FastTraversalHoldAuthority, Is.EqualTo(0.72f));
                Assert.That(profile.DetentHapticMinimumIntensity, Is.EqualTo(0.92f));
                Assert.That(profile.DetentHapticMaximumIntensity, Is.EqualTo(1.0f));
                Assert.That(profile.DetentHapticMinimumSharpness, Is.EqualTo(0.76f));
                Assert.That(profile.DetentHapticMaximumSharpness, Is.EqualTo(0.90f));
                Assert.That(profile.DetentHapticBodyIntensity, Is.EqualTo(0.64f));
                Assert.That(profile.DetentHapticBodySharpness, Is.EqualTo(0.24f));
                Assert.That(profile.DetentHapticBodyDurationSeconds, Is.EqualTo(0.032f));
                Assert.That(profile.DetentHapticTailIntensity, Is.EqualTo(0.56f));
                Assert.That(profile.DetentHapticTailSharpness, Is.EqualTo(0.42f));
                Assert.That(profile.DetentHapticTailDelaySeconds, Is.EqualTo(0.022f));
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
            Assert.That(FanCardSpecifications.CardThickness, Is.EqualTo(0.0035f));
            Assert.That(
                FanCardSpecifications.CardWidth / FanCardSpecifications.CardHeight,
                Is.EqualTo(63.5f / 88.9f).Within(0.00001f));
            Assert.That(
                FanCardSpecifications.CardCornerRadius,
                Is.EqualTo(0.0095f));
            Assert.That(
                FanCardSpecifications.VisualCornerSegmentsPerQuadrant,
                Is.EqualTo(72));
            Assert.That(
                FanCardSpecifications.EdgeBevel,
                Is.EqualTo(FanCardSpecifications.CardThickness * 0.15f)
                    .Within(0.000000001f));
            Assert.That(FanCardSpecifications.LayerAirGap, Is.EqualTo(0.0010f));
            Assert.That(
                FanCardSpecifications.LayerPitch,
                Is.EqualTo(0.0045f).Within(0.000000001f));
            Assert.That(FanCardSpecifications.BlackBorderWidth, Is.EqualTo(0.0010f));
            Assert.That(FanCardSpecifications.GoldTrimWidth, Is.EqualTo(0.0008f));
            Assert.That(FanCardSpecifications.GoldTrimBevel, Is.EqualTo(0.00038f));
            Assert.That(
                FanCardSpecifications.FaceInset,
                Is.EqualTo(
                    FanCardSpecifications.BlackBorderWidth
                    + FanCardSpecifications.GoldTrimWidth));
            Assert.That(FanCardSpecifications.DecorativeDotCountPerFront, Is.Zero);
            Assert.That(FanCardSpecifications.LibraryPreviewDetentIndex, Is.EqualTo(2));
            Assert.That(FanCardSpecifications.LibraryPreviewProgress, Is.EqualTo(2f / 3f));
            Assert.That(FanCardSpecifications.LibraryPreviewRollDegrees, Is.EqualTo(45f));
            Assert.That(FanCardSpecifications.AxisHoleRadius, Is.EqualTo(0.00215f));
            Assert.That(FanCardSpecifications.RecessedSpindleRadius, Is.EqualTo(0.00200f));
            Assert.That(FanCardSpecifications.RecessedSpindleTopInset, Is.EqualTo(0.00012f));
            Assert.That(FanCardSpecifications.BearingCapRadius, Is.EqualTo(0.00207f));
            Assert.That(FanCardSpecifications.BearingCapHeight, Is.EqualTo(0.00065f));
            Assert.That(
                FanCardSpecifications.AxisHoleRadius
                    - FanCardSpecifications.RecessedSpindleRadius,
                Is.GreaterThanOrEqualTo(0.0001f),
                "The near-flush matte shaft still keeps mechanical clearance.");
            Assert.That(
                FanCardSpecifications.LayerPitch
                    - FanCardSpecifications.CardThickness,
                Is.EqualTo(FanCardSpecifications.LayerAirGap)
                    .Within(0.000001f),
                "The tight stack keeps one millimetre of physical air.");
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
            Assert.That(framing.DetailWidthFraction, Is.EqualTo(0.80f));
            Assert.That(framing.DetailHeightFraction, Is.EqualTo(0.80f));
            Assert.That(framing.LibraryWidthFraction, Is.EqualTo(0.72f));
            Assert.That(framing.LibraryHeightFraction, Is.EqualTo(0.72f));
            Assert.That(
                FanCardSpecifications.VisualSweepBounds.size.x,
                Is.GreaterThan(FanCardSpecifications.CardWidth * 1.6f));
            Assert.That(
                FanCardSpecifications.VisualSweepBounds.size.z
                    / FanCardSpecifications.CardHeight,
                Is.InRange(1.51f, 1.53f),
                "The approved 9.5 mm corners keep the portrait sweep "
                + "inside the locked framing range.");
            Assert.That(
                FanCardSpecifications.InteractionSweepBounds.size.x,
                Is.GreaterThan(FanCardSpecifications.VisualSweepBounds.size.x));
            Assert.That(
                FanCardSpecifications.CameraSweepBounds.size.x
                    / FanCardSpecifications.VisualSweepBounds.size.x,
                Is.EqualTo(FanCardSpecifications.CameraSweepBoundsScale)
                    .Within(0.000001f));
            Assert.That(
                FanCardSpecifications.CameraSweepBoundsScale,
                Is.InRange(0.99f, 1f),
                "Camera framing may ignore only sub-percent tangent extrema.");
        }

        [Test]
        public void ShippingVisualMeshesAndShaderUseTheAuthoritativeBlenderSource()
        {
            ModelImporter importer = AssetImporter.GetAtPath(
                FidgetingApp.FanCard.EditorTools.FanCardVisualModelIntegrator
                    .VisualModelPath)
                as ModelImporter;
            Assert.That(importer, Is.Not.Null);
            Assert.That(importer.preserveHierarchy, Is.True);
            Assert.That(importer.bakeAxisConversion, Is.True);
            Assert.That(importer.importNormals, Is.EqualTo(ModelImporterNormals.Import));

            Mesh[] meshes = AssetDatabase.LoadAllAssetsAtPath(
                    FidgetingApp.FanCard.EditorTools.FanCardVisualModelIntegrator
                        .VisualModelPath)
                .OfType<Mesh>()
                .ToArray();
            foreach (string name in new[]
            {
                "BottomCard_GunmetalFrame",
                "BottomCard_GoldTrim",
                "BottomCard_WarmSilverFace"
            })
            {
                Assert.That(
                    meshes.Any(mesh =>
                        mesh.name == name || mesh.name == name + "_Mesh"),
                    Is.True,
                    name);
            }

            string builder = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_FanCard/Editor/FanCardSceneBuilder.cs"));
            int buildStart = builder.IndexOf(
                "public static void BuildScene()",
                System.StringComparison.Ordinal);
            int buildEnd = builder.IndexOf(
                "[MenuItem(\"Tools/Codex/Fan Card/2",
                buildStart,
                System.StringComparison.Ordinal);
            Assert.That(buildStart, Is.GreaterThanOrEqualTo(0));
            Assert.That(buildEnd, Is.GreaterThan(buildStart));
            string buildMethod = builder.Substring(
                buildStart,
                buildEnd - buildStart);
            StringAssert.Contains("LoadVisualModelPart(", buildMethod);
            StringAssert.Contains("ConvertAuthoritativeVisualMesh(", buildMethod);
            StringAssert.DoesNotContain("CreateRoundedBoxMesh(", buildMethod);
            StringAssert.DoesNotContain("CreateRoundedSurfaceMesh(", buildMethod);

            string shader = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_FanCard/Shaders/FanCardSatinSilver.shader"));
            StringAssert.DoesNotContain("softPanel", shader);
            StringAssert.DoesNotContain("reflectedBand", shader);
            StringAssert.DoesNotContain("0.30, 0.30, 0.30", shader);
            StringAssert.DoesNotContain("0.34 + ambientIrradiance", shader);
            StringAssert.Contains("GetMainLight", shader);
            StringAssert.Contains("SampleSH", shader);

            string gunmetalShader = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_FanCard/Shaders/FanCardGunmetal.shader"));
            StringAssert.DoesNotContain("studioForward", gunmetalShader);
            StringAssert.DoesNotContain("studioSheen", gunmetalShader);
            StringAssert.Contains("GetMainLight", gunmetalShader);
            StringAssert.Contains("SampleSH", gunmetalShader);
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

        [Test]
        public void PointerArcUsesResponsiveGainWithoutChangingMagneticTuning()
        {
            Assert.That(
                FanCardController.ResolveHandTargetForPointerArc(0f, 72f, 90f),
                Is.EqualTo(1f).Within(0.000001f));
            Assert.That(
                FanCardController.ResolveHandTargetForPointerArc(1f, -72f, 90f),
                Is.EqualTo(0f).Within(0.000001f));
            Assert.That(
                FanCardController.ResolveHandTargetForPointerArc(0.5f, 18f, 90f),
                Is.EqualTo(0.75f).Within(0.000001f));
        }

        [Test]
        public void CentroidProjectedGestureTracksDistanceWithoutUsingCornerPivotAngle()
        {
            Vector3 closed = FanCardController.ResolveFanCentroidLocal(0f);
            Vector3 half = FanCardController.ResolveFanCentroidLocal(0.5f);
            Vector3 open = FanCardController.ResolveFanCentroidLocal(1f);
            Assert.That(Vector3.Distance(closed, half), Is.GreaterThan(0.005f));
            Assert.That(Vector3.Distance(half, open), Is.GreaterThan(0.005f));
            Assert.That(
                FanCardController.ResolveHandTargetForProjectedTravel(0.25f, 0.20f),
                Is.EqualTo(0.45f).Within(0.000001f));
            Assert.That(
                FanCardController.ResolveHandTargetForProjectedTravel(0.25f, -0.50f),
                Is.EqualTo(0f).Within(0.000001f));
            Assert.That(
                FanCardController.ResolveGestureIntensity(1f, 1f, 1f, 1f),
                Is.EqualTo(1f).Within(0.000001f));
            Assert.That(
                FanCardController.ResolveTraversalAuthority(
                    300f,
                    1000f,
                    0f,
                    0.55f,
                    1.30f,
                    0.10f,
                    0.45f,
                    1f,
                    0f),
                Is.EqualTo(0.78f).Within(0.000001f),
                "A long controlled stroke increases traversal response without becoming a binary toggle.");
        }

        [Test]
        public void GestureClassifierSeparatesControlledPushFromFastOrFirmTraversal()
        {
            const float referenceWidth = 1000f;
            Assert.That(
                FanCardController.ResolveTraversalAuthority(
                    300f,
                    referenceWidth,
                    0f,
                    0.55f,
                    1.30f,
                    0.10f,
                    0.45f),
                Is.Zero,
                "A deliberate slow push must retain full magnetic detent feel.");
            Assert.That(
                FanCardController.ResolveTraversalAuthority(
                    1300f,
                    referenceWidth,
                    0f,
                    0.55f,
                    1.30f,
                    0.10f,
                    0.45f),
                Is.EqualTo(1f).Within(0.000001f),
                "A fast screen-width flick must select ballistic traversal.");
            Assert.That(
                FanCardController.ResolveTraversalAuthority(
                    0f,
                    referenceWidth,
                    0.45f,
                    0.55f,
                    1.30f,
                    0.10f,
                    0.45f),
                Is.EqualTo(1f).Within(0.000001f),
                "A supported pressure increase can independently authorize the fast path.");
        }

        [Test]
        public void FanCardCrossingsUseAnUnthrottledProductSpecificHapticPath()
        {
            var tuning = new FanCardHapticTuning(
                0.92f,
                1f,
                0.76f,
                0.90f,
                0.64f,
                0.24f,
                0.032f,
                0.56f,
                0.42f,
                0.022f);
            Assert.That(tuning.BodyIntensity, Is.EqualTo(0.64f));
            Assert.That(tuning.BodyDurationSeconds, Is.EqualTo(0.032f));
            Assert.That(tuning.TailDelaySeconds, Is.EqualTo(0.022f));
            FidgetHapticTelemetry before = FidgetHapticRouter.GetTelemetry();

            FidgetHapticRouter.EmitFanCard(
                FidgetSemanticEvent.DetentCrossed,
                0.15f,
                tuning);
            FidgetHapticRouter.EmitFanCard(
                FidgetSemanticEvent.DetentCrossed,
                0.55f,
                tuning);
            FidgetHapticRouter.EmitFanCard(
                FidgetSemanticEvent.DetentCrossed,
                1f,
                tuning);

            FidgetHapticTelemetry afterCrossings = FidgetHapticRouter.GetTelemetry();
            Assert.That(
                afterCrossings.RenderedEventCount - before.RenderedEventCount,
                Is.EqualTo(3),
                "A fast three-boundary traversal must not inherit the rotary detent rate limiter.");
            Assert.That(
                afterCrossings.SuppressedEventCount - before.SuppressedEventCount,
                Is.Zero);
            Assert.That(
                afterCrossings.LastSemanticEvent,
                Is.EqualTo(FidgetSemanticEvent.DetentCrossed));

            FidgetHapticRouter.EmitFanCard(
                FidgetSemanticEvent.Breakaway,
                1f,
                tuning);
            FidgetHapticRouter.EmitFanCard(
                FidgetSemanticEvent.DetentCaptured,
                1f,
                tuning);

            FidgetHapticTelemetry after = FidgetHapticRouter.GetTelemetry();
            Assert.That(
                after.RenderedEventCount - before.RenderedEventCount,
                Is.EqualTo(3),
                "Only the three real crossings render weighted packets.");
            Assert.That(
                after.SuppressedEventCount - before.SuppressedEventCount,
                Is.EqualTo(2),
                "Breakaway and capture stay semantic-only for the fan card.");
        }

        [TestCase(30)]
        [TestCase(60)]
        [TestCase(120)]
        public void FastTraversalCrossesEveryDetentAndCapturesAtTheEndpoint(
            int frameRate)
        {
            FanCardDetentProfile profile = CreateProfile();
            try
            {
                var track = new FanCardMagneticTrack(profile);
                float deltaTime = 1f / frameRate;
                int breakaways = 0;
                int crossings = 0;
                for (int frame = 0; frame < frameRate * 2; frame++)
                {
                    FanCardStepResult result = track.Step(
                        deltaTime,
                        1f,
                        true,
                        profile.FastTraversalHoldAuthority);
                    breakaways += result.BrokeAway ? 1 : 0;
                    crossings += result.CrossedDetentCount;
                    if (track.IsAtRest && track.CapturedDetentIndex == 3)
                    {
                        break;
                    }
                }

                Assert.That(breakaways, Is.EqualTo(1));
                Assert.That(crossings, Is.EqualTo(3));
                Assert.That(track.CapturedDetentIndex, Is.EqualTo(3));
                Assert.That(track.Position, Is.EqualTo(1f).Within(0.000001f));
                Assert.That(track.Velocity, Is.Zero);
            }
            finally
            {
                Object.DestroyImmediate(profile);
            }
        }

        [Test]
        public void DeviceMotionYieldsToEitherDirectProductGesture()
        {
            Assert.That(
                EdcDeviceMotionController.ShouldSuppressForProductInteraction(
                    false,
                    false),
                Is.False);
            Assert.That(
                EdcDeviceMotionController.ShouldSuppressForProductInteraction(
                    true,
                    false),
                Is.True);
            Assert.That(
                EdcDeviceMotionController.ShouldSuppressForProductInteraction(
                    false,
                    true),
                Is.True);
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
            Assert.That(
                Quaternion.Angle(Quaternion.identity, bottom.localRotation),
                Is.EqualTo(0f).Within(0.01f),
                "The physical bottom card is the stationary reference layer.");
            Assert.That(
                Mathf.DeltaAngle(0f, middle.localEulerAngles.y),
                Is.EqualTo(45f).Within(0.01f));
            Assert.That(
                Mathf.DeltaAngle(0f, top.localEulerAngles.y),
                Is.EqualTo(90f).Within(0.01f));
            Vector3 openDirection = top.TransformPoint(
                    FanCardSpecifications.CardCenterFromPivot)
                - root.position;
            float openPlanAngle = Mathf.Atan2(
                openDirection.z,
                openDirection.x) * Mathf.Rad2Deg;
            controller.SetFanProgress(0f);
            Vector3 closedDirection = top.TransformPoint(
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
            controller.SetFanProgress(0f);
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
                hierarchy.Count(item => item.name == "CurvedTrack_GoldGrille"),
                Is.EqualTo(2));
            Assert.That(
                hierarchy.Where(item => item.name == "CurvedTrack_GoldGrille")
                    .Select(item => item.parent.name),
                Is.EquivalentTo(new[] { "TopCard", "MiddleCard" }),
                "Only the top and middle cards own rear tracks.");
            Assert.That(
                bottom.Find("CurvedTrack_GoldGrille"),
                Is.Null,
                "The final/bottom blade must never render a rear track.");
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
                hierarchy.Where(item => item.name == "FollowerBearing_Chrome")
                    .Select(item => item.parent.name),
                Is.EquivalentTo(new[] { "MiddleCard", "BottomCard" }));
            Assert.That(
                hierarchy.Count(item => item.name == "CommonAxis_ChromeBall"),
                Is.EqualTo(0),
                "The pivot must not regress to a free-floating primitive ball.");
            Assert.That(
                hierarchy.Count(item => item.name == "CommonAxis_BallSeat"),
                Is.EqualTo(0));
            Assert.That(
                hierarchy.Count(item => item.name.StartsWith("AxisSeat_")),
                Is.EqualTo(0),
                "No surface disk may cover the authored spindle hole.");
            Transform spindleMarker = root.Find("CommonAxis_ShadowSleeve");
            Assert.That(spindleMarker, Is.Not.Null);
            Renderer spindleRenderer = spindleMarker.GetComponent<Renderer>();
            Assert.That(
                spindleRenderer == null || !spindleRenderer.enabled,
                Is.True,
                "The structural spindle marker must not render as an unexplained front-face ring.");
            Transform recessedSpindle = root.Find(
                "CommonAxis_RecessedMatteSpindle");
            Assert.That(recessedSpindle, Is.Not.Null);
            Assert.That(recessedSpindle.GetComponent<Renderer>(), Is.Not.Null);
            Assert.That(
                recessedSpindle.localScale.x,
                Is.LessThan(FanCardSpecifications.AxisHoleRadius),
                "The intentional matte shaft must not form a ring over the beveled hole.");
            Transform bearingCap = root.Find("CommonAxis_BearingCap_Chrome");
            Assert.That(bearingCap, Is.Not.Null);
            MeshFilter bearingCapFilter = bearingCap.GetComponent<MeshFilter>();
            MeshRenderer bearingCapRenderer = bearingCap.GetComponent<MeshRenderer>();
            Assert.That(bearingCapFilter, Is.Not.Null);
            Assert.That(bearingCapRenderer, Is.Not.Null);
            Assert.That(
                bearingCapFilter.sharedMesh.bounds.extents.x,
                Is.EqualTo(FanCardSpecifications.BearingCapRadius)
                    .Within(0.00001f));
            Assert.That(
                bearingCapFilter.sharedMesh.bounds.extents.y,
                Is.EqualTo(FanCardSpecifications.BearingCapHeight)
                    .Within(0.00001f));
            StringAssert.Contains("Chrome", bearingCapRenderer.sharedMaterial.name);

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
                "Every shipping card body must retain the authored 3.5 mm section.");
            for (int index = 1; index < bodies.Length; index++)
            {
                Assert.That(
                    bodies[index].bounds.min.y - bodies[index - 1].bounds.max.y,
                    Is.GreaterThanOrEqualTo(
                        FanCardSpecifications.LayerAirGap - 0.00001f),
                    "Adjacent card bodies must keep a physical air gap.");
            }
            Assert.That(
                hierarchy.Count(item => item.name == "WarmSilverBackFace"),
                Is.EqualTo(3),
                "All three rigid slabs need a rendered underside face.");
            Transform[] frontGoldTrims = hierarchy
                .Where(item => item.name == "WarmGoldTrim")
                .ToArray();
            Transform[] backGoldTrims = hierarchy
                .Where(item => item.name == "WarmGoldBackTrim")
                .ToArray();
            Assert.That(frontGoldTrims, Has.Length.EqualTo(3));
            Assert.That(backGoldTrims, Has.Length.EqualTo(3));
            Assert.That(
                frontGoldTrims.Concat(backGoldTrims)
                    .All(item => item.GetComponent<Renderer>()
                        .sharedMaterial.name.Contains("Gold")),
                Is.True,
                "The black frame must transition through the approved warm-gold inlay.");
            Assert.That(
                hierarchy.Count(item => item.name.StartsWith("EtchedDot_")),
                Is.Zero,
                "The approved face has no semantically unexplained three-dot motif.");
            Mesh projectedFaceMesh = top.Find("WarmSilverFace")
                .GetComponent<MeshFilter>().sharedMesh;
            Assert.That(
                projectedFaceMesh.vertexCount,
                Is.EqualTo(1579),
                "The visible silver face must come from the authoritative FBX cap.");
            Assert.That(
                projectedFaceMesh.vertices.All(vertex => Mathf.Abs(vertex.y) < 0.000001f),
                Is.True,
                "Face art must be a perfectly flat surface projection, not a second bent slab.");
            Assert.That(
                projectedFaceMesh.bounds.size.x,
                Is.EqualTo(FanCardSpecifications.FaceWidth).Within(0.00002f));
            Assert.That(
                projectedFaceMesh.bounds.size.z,
                Is.EqualTo(FanCardSpecifications.FaceHeight).Within(0.00002f));
            Assert.That(
                CapContainsPoint(projectedFaceMesh, new Vector2(
                    FanCardSpecifications.PivotX,
                    FanCardSpecifications.PivotZ), 0f),
                Is.False,
                "The full silver corner must contain one enclosed spindle opening, never an edge notch.");

            Mesh bodyMesh = top.Find("GunmetalFrame")
                .GetComponent<MeshFilter>().sharedMesh;
            Assert.That(
                bodyMesh.vertexCount,
                Is.EqualTo(3969),
                "The visible body must preserve the authoritative FBX split normals.");
            Mesh goldTrimMesh = top.Find("WarmGoldTrim")
                .GetComponent<MeshFilter>().sharedMesh;
            Assert.That(
                goldTrimMesh.vertexCount,
                Is.EqualTo(3981),
                "The warm-gold trim must preserve the authoritative FBX split normals.");
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
                hierarchy.Where(item => item.name == "CurvedTrack_GoldGrille")
                    .All(item => item.GetComponent<MeshFilter>().sharedMesh.bounds.center.x < 0f
                        && item.GetComponent<MeshFilter>().sharedMesh.bounds.center.z < 0f),
                Is.True,
                "Both curved tracks must stay inset toward the lower-left, not touch an edge.");
            Transform[] grilles = hierarchy
                .Where(item => item.name == "CurvedTrack_GoldGrille")
                .ToArray();
            Assert.That(
                grilles.All(item => item.GetComponent<MeshFilter>()
                    .sharedMesh.triangles.Length / 3
                    == FanCardSpecifications.TrackGridExpectedTriangleCount
                    && item.GetComponent<MeshFilter>().sharedMesh.vertexCount
                    == FanCardSpecifications.TrackGridExpectedVertexCount),
                Is.True,
                "The shipping track must use the validated Blender wire grille, not a solid textured ribbon. "
                + string.Join(", ", grilles.Select(item =>
                {
                    Mesh mesh = item.GetComponent<MeshFilter>().sharedMesh;
                    return $"{mesh.name}: {mesh.vertexCount} verts / "
                        + $"{mesh.triangles.Length / 3} tris";
                })));
            Assert.That(
                grilles.All(item => item.GetComponent<Renderer>()
                    .sharedMaterial.GetTexture("_BaseMap") == null),
                Is.True,
                "Grille openings must come from geometry so magnets remain visible through them.");
            Assert.That(
                hierarchy.Where(item => item.name.StartsWith("CurvedTrack_"))
                    .All(item => item.GetComponent<MeshFilter>().sharedMesh.vertices
                        .All(vertex => IsInsideCardOutline(vertex, 0.0005f))),
                Is.True,
                "The entire back-track projection must remain inside the card outline.");
            Assert.That(
                hierarchy.Where(item => item.name.StartsWith("CurvedTrack_"))
                    .All(item =>
                    {
                        Transform backFace = item.parent.Find("WarmSilverBackFace");
                        return backFace != null
                            && item.localPosition.y < backFace.localPosition.y
                            && item.localRotation == Quaternion.identity;
                    }),
                Is.True,
                "Both Blender-authored track layers must remain visibly outside "
                + "the back face of their rigid slab.");
            Assert.That(
                grilles.All(item =>
                {
                    Mesh mesh = item.GetComponent<MeshFilter>().sharedMesh;
                    return mesh.bounds.size.y >= 0.00010f
                        && mesh.normals.Any(normal => normal.y > 0.5f)
                        && mesh.normals.Any(normal => normal.y < -0.5f);
                }),
                Is.True,
                "The grille wires need real round thickness and two-sided surface normals from Blender.");
            Assert.That(
                hierarchy.Where(item => item.name.StartsWith("Magnet_"))
                    .All(item => item.localPosition.y
                        < -FanCardSpecifications.CardThickness * 0.5f),
                Is.True,
                "All magnetic detent inserts belong on the back, never the visible front face.");
            foreach (Transform grille in grilles)
            {
                Transform[] layerMagnets = grille.parent
                    .Cast<Transform>()
                    .Where(item => item.name.StartsWith("Magnet_"))
                    .ToArray();
                Assert.That(layerMagnets, Has.Length.EqualTo(3));
                Assert.That(
                    layerMagnets.All(magnet => grille.localPosition.y
                        < magnet.localPosition.y - 0.00016f * 0.5f),
                    Is.True,
                    "The real grille must sit outward of the magnet caps so its wires visibly cross over them.");
            }
            Assert.That(root.GetComponentsInChildren<Rigidbody>(true), Is.Empty);
            Assert.That(root.GetComponentsInChildren<Collider>(true), Has.Length.EqualTo(1));
            BoxCollider interaction = root.GetComponent<BoxCollider>();
            Assert.That(interaction, Is.Not.Null);
            Assert.That(controller.InteractionSurface, Is.SameAs(interaction));
            Bounds expectedInteraction =
                FanCardSpecifications.InteractionSweepBounds;
            Assert.That(
                Vector3.Distance(interaction.center, expectedInteraction.center),
                Is.LessThan(0.000001f));
            Assert.That(
                Vector3.Distance(interaction.size, expectedInteraction.size),
                Is.LessThan(0.000001f));
            EdcPortraitCameraFramer framer =
                Object.FindAnyObjectByType<EdcPortraitCameraFramer>();
            Assert.That(framer, Is.Not.Null);
            Assert.That(framer.UsesStableLocalBounds, Is.True);
            Assert.That(framer.FocusTarget, Is.Not.Null);
            Assert.That(framer.FocusTarget.name, Is.EqualTo("FanCardPresentationCenter"));
            Assert.That(
                Vector3.Distance(
                    framer.StableLocalBounds.center,
                    FanCardSpecifications.CameraSweepBounds.center),
                Is.LessThan(0.000001f));
            Assert.That(
                Vector3.Distance(
                    framer.StableLocalBounds.size,
                    FanCardSpecifications.CameraSweepBounds.size),
                Is.LessThan(0.000001f));
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
        public void LibraryPreviewCentersASecondDetentFortyFiveDegreeFanWithoutMutatingMechanics()
        {
            EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            FanCardController controller =
                Object.FindAnyObjectByType<FanCardController>();
            EdcPortraitCameraFramer framer =
                Object.FindAnyObjectByType<EdcPortraitCameraFramer>();
            Camera camera = Object.FindAnyObjectByType<Camera>();
            Assert.That(controller, Is.Not.Null);
            Assert.That(framer, Is.Not.Null);
            Assert.That(camera, Is.Not.Null);

            Transform middle = controller.transform.Find("MiddleCard");
            Transform outer = controller.transform.Find("TopCard");
            Assert.That(middle, Is.Not.Null);
            Assert.That(outer, Is.Not.Null);

            controller.SetFanProgress(0f);
            Quaternion middleClosed = middle.localRotation;
            Quaternion outerClosed = outer.localRotation;
            controller.SetFanProgress(1f / 3f);
            int semanticCount = 0;
            controller.SemanticEventRaised += (_, _) => semanticCount++;
            controller.SetLibraryPreviewActive(true);
            framer.SetLibraryPreviewActive(true, true);

            Assert.That(controller.Progress, Is.EqualTo(1f / 3f).Within(0.000001f));
            Assert.That(controller.CapturedDetentIndex, Is.EqualTo(1));
            Assert.That(semanticCount, Is.Zero);
            Assert.That(
                Quaternion.Angle(middleClosed, middle.localRotation),
                Is.EqualTo(30f).Within(0.05f));
            Assert.That(
                Quaternion.Angle(outerClosed, outer.localRotation),
                Is.EqualTo(60f).Within(0.05f));
            Assert.That(framer.LibraryRollDegrees, Is.EqualTo(45f));
            Assert.That(framer.FramingRollDegrees, Is.EqualTo(45f));
            Assert.That(
                ProductCameraFraming.TryGetProductBounds(
                    controller.transform,
                    out Bounds previewBounds),
                Is.True);
            Vector3 viewport = camera.WorldToViewportPoint(previewBounds.center);
            Assert.That(viewport.z, Is.GreaterThan(0f));
            Assert.That(viewport.x, Is.EqualTo(0.5f).Within(0.04f));
            Assert.That(viewport.y, Is.EqualTo(0.5f).Within(0.04f));

            framer.SetLibraryPreviewActive(false, true);
            controller.SetLibraryPreviewActive(false);
            Assert.That(controller.Progress, Is.EqualTo(1f / 3f).Within(0.000001f));
            Assert.That(
                Quaternion.Angle(middleClosed, middle.localRotation),
                Is.EqualTo(15f).Within(0.05f));
            Assert.That(
                Quaternion.Angle(outerClosed, outer.localRotation),
                Is.EqualTo(30f).Within(0.05f));
            Assert.That(framer.FramingRollDegrees, Is.Zero.Within(0.001f));
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
            Assert.That(
                gunmetal.GetFloat("_Smoothness"),
                Is.EqualTo(FanCardSpecifications.GunmetalSmoothness));
            Assert.That(silver.GetFloat("_Metallic"), Is.EqualTo(1f));
            Assert.That(
                silver.GetFloat("_Smoothness"),
                Is.EqualTo(FanCardSpecifications.SilverSmoothness));
            Assert.That(
                silver.GetFloat("_BumpScale"),
                Is.EqualTo(FanCardSpecifications.SilverBumpScale));
            Assert.That(
                chrome.GetFloat("_Smoothness"),
                Is.EqualTo(FanCardSpecifications.ChromeSmoothness));
            Assert.That(
                gold.GetFloat("_Metallic"),
                Is.EqualTo(FanCardSpecifications.GoldMetallic));
            Assert.That(
                gold.GetFloat("_Smoothness"),
                Is.EqualTo(FanCardSpecifications.GoldSmoothness));
            Assert.That(
                SpinnerImageBasedLightingController.FanCardSoftboxIntensity,
                Is.EqualTo(0.22f));
            Assert.That(
                SpinnerImageBasedLightingController.FanCardReflectionBaseScale,
                Is.EqualTo(0.92f));
            Assert.That(
                SpinnerImageBasedLightingController.FanCardOpposingStripIntensity,
                Is.EqualTo(0.10f));
            Assert.That(
                SpinnerEnvironmentCatalog.TryGetProfile(
                    FanCardSpecifications.ScenePath,
                    out SpinnerEnvironmentProfile environment),
                Is.True);
            Assert.That(environment.ReflectionIntensity, Is.EqualTo(0.28f));
            Assert.That(
                environment.Lights[0].Intensity,
                Is.EqualTo(0.92f));
            Assert.That(
                environment.Lights[1].Intensity,
                Is.EqualTo(0.28f));
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
            Assert.That(
                gold.GetTexture("_BaseMap"),
                Is.Null,
                "The track is a real open mesh; an opaque woven texture would hide its magnets.");

            EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            FanCardController controller =
                Object.FindAnyObjectByType<FanCardController>();
            TextMesh[] labels = controller.GetComponentsInChildren<TextMesh>(true);
            Assert.That(
                labels,
                Is.Empty,
                "Face marks must be manufactured mesh, not camera-dependent TextMesh quads.");
            Transform[] rankMarks = controller.GetComponentsInChildren<Transform>(true)
                .Where(item => item.name.StartsWith("RankGlyph_"))
                .ToArray();
            Assert.That(
                rankMarks,
                Has.Length.EqualTo(6),
                "Each rigid front face needs upper-left and lower-right rank marks.");
            Assert.That(
                rankMarks.GroupBy(mark => mark.parent.name)
                    .ToDictionary(group => group.Key, group => group.Count()),
                Is.EquivalentTo(new Dictionary<string, int>
                {
                    { "BottomCard", 2 },
                    { "MiddleCard", 2 },
                    { "TopCard", 2 }
                }),
                "Both rank marks must be parented directly to their own rigid slab.");
            Assert.That(
                controller.GetComponentsInChildren<Transform>(true)
                    .Any(item => item.name == "BackFaceArtwork"
                        || item.name.Contains("RankGlyph_Back")
                        || item.name.Contains("CornerSpade_Back")),
                Is.False,
                "Corner indices belong only on the front; the track side stays mechanical.");
            Transform[] cornerSpades = controller
                .GetComponentsInChildren<Transform>(true)
                .Where(item => item.name.StartsWith("CornerSpade_"))
                .ToArray();
            Assert.That(cornerSpades, Has.Length.EqualTo(6));
            foreach (string layerName in new[] { "BottomCard", "MiddleCard", "TopCard" })
            {
                Transform layer = controller.transform.Find(layerName);
                Transform topLeftRank = layer.Find("RankGlyph_TopLeft");
                Transform topLeftSpade = layer.Find("CornerSpade_TopLeft");
                Transform bottomRightRank = layer.Find("RankGlyph_BottomRight");
                Transform bottomRightSpade = layer.Find("CornerSpade_BottomRight");
                Assert.That(topLeftRank, Is.Not.Null);
                Assert.That(topLeftSpade, Is.Not.Null);
                Assert.That(bottomRightRank, Is.Not.Null);
                Assert.That(bottomRightSpade, Is.Not.Null);

                Vector3 center = FanCardSpecifications.CardCenterFromPivot;
                Assert.That(
                    Vector2.Distance(
                        new Vector2(
                            topLeftRank.localPosition.x - center.x,
                            topLeftRank.localPosition.z - center.z),
                        FanCardSpecifications.CornerTopLeftRankOffset),
                    Is.LessThan(0.000001f));
                Assert.That(
                    Vector2.Distance(
                        new Vector2(
                            topLeftSpade.localPosition.x - center.x,
                            topLeftSpade.localPosition.z - center.z),
                        FanCardSpecifications.CornerTopLeftSpadeOffset),
                    Is.LessThan(0.000001f));
                Assert.That(
                    Vector2.Distance(
                        new Vector2(
                            bottomRightRank.localPosition.x - center.x,
                            bottomRightRank.localPosition.z - center.z),
                        FanCardSpecifications.CornerBottomRightRankOffset),
                    Is.LessThan(0.000001f));
                Assert.That(
                    Vector2.Distance(
                        new Vector2(
                            bottomRightSpade.localPosition.x - center.x,
                            bottomRightSpade.localPosition.z - center.z),
                        FanCardSpecifications.CornerBottomRightSpadeOffset),
                    Is.LessThan(0.000001f));

                Assert.That(
                    Quaternion.Angle(
                        topLeftRank.localRotation,
                        Quaternion.Euler(
                            0f,
                            FanCardSpecifications.CornerTopLeftRotationDegrees,
                            0f)),
                    Is.LessThan(0.001f));
                Assert.That(
                    Quaternion.Angle(topLeftRank.localRotation, topLeftSpade.localRotation),
                    Is.LessThan(0.001f),
                    "The upper-left rank and spade must read in the same direction.");
                Assert.That(
                    Quaternion.Angle(
                        bottomRightRank.localRotation,
                        Quaternion.Euler(
                            0f,
                            FanCardSpecifications.CornerBottomRightRotationDegrees,
                            0f)),
                    Is.LessThan(0.001f));
                Assert.That(
                    Quaternion.Angle(
                        bottomRightRank.localRotation,
                        bottomRightSpade.localRotation),
                    Is.LessThan(0.001f),
                    "The lower-right rank and spade must both rotate 180 degrees.");
            }
            Assert.That(
                controller.GetComponentsInChildren<Transform>(true)
                    .Count(item => item.name.StartsWith("Spade_Etched")),
                Is.EqualTo(3));
            Assert.That(
                controller.GetComponentsInChildren<Transform>(true)
                    .Count(item => item.name.StartsWith("Spade_VerticalSlots")),
                Is.EqualTo(3));

            Dictionary<string, Mesh> rankMeshes = AssetDatabase
                .LoadAllAssetsAtPath(FanCardSpecifications.BackMechanismModelPath)
                .OfType<Mesh>()
                .Where(mesh => new[]
                {
                    "Ace_A_Oxanium",
                    "Queen_Q_Oxanium",
                    "King_K_Oxanium"
                }.Contains(mesh.name))
                .ToDictionary(mesh => mesh.name);
            Assert.That(rankMeshes.Keys, Is.EquivalentTo(new[]
            {
                "Ace_A_Oxanium",
                "Queen_Q_Oxanium",
                "King_K_Oxanium"
            }));
            foreach (Mesh rankMesh in rankMeshes.Values)
            {
                Assert.That(
                    rankMesh.bounds.size.z,
                    Is.EqualTo(0.0064f).Within(0.00015f));
                Assert.That(rankMesh.bounds.size.y, Is.GreaterThan(0.00005f));
                Assert.That(rankMesh.triangles.Length / 3, Is.GreaterThan(10));
            }

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
            Assert.That(triangleCount, Is.LessThan(100000));
        }

        [Test]
        public void FaceRankPatternsSwitchAsWholeSetsWithoutMovingRigidLayers()
        {
            EditorSceneManager.OpenScene(
                FanCardSpecifications.ScenePath,
                OpenSceneMode.Single);
            FanCardController controller =
                Object.FindAnyObjectByType<FanCardController>();
            FanCardFaceRankPresenter presenter =
                controller.GetComponent<FanCardFaceRankPresenter>();
            Assert.That(presenter, Is.Not.Null);
            Assert.That(presenter.LayerCount, Is.EqualTo(3));
            Assert.That(
                FanCardFaceRankPresenter.ResolvePattern(0.0f),
                Is.EqualTo(FanCardRankPattern.TripleAce));
            Assert.That(
                FanCardFaceRankPresenter.ResolvePattern(0.4999f),
                Is.EqualTo(FanCardRankPattern.TripleAce));
            Assert.That(
                FanCardFaceRankPresenter.ResolvePattern(0.5f),
                Is.EqualTo(FanCardRankPattern.QueenKingAce));
            Assert.That(
                FanCardFaceRankPresenter.ResolvePattern(1.0f),
                Is.EqualTo(FanCardRankPattern.QueenKingAce));

            Transform[] layers = new[] { "BottomCard", "MiddleCard", "TopCard" }
                .Select(name => controller.transform.Find(name))
                .ToArray();
            Vector3[] positions = layers.Select(layer => layer.localPosition).ToArray();
            Quaternion[] rotations = layers.Select(layer => layer.localRotation).ToArray();
            float progress = controller.Progress;
            int semanticEvents = 0;
            controller.SemanticEventRaised += (_, _) => semanticEvents++;

            presenter.ApplyPattern(FanCardRankPattern.QueenKingAce);
            Assert.That(presenter.CurrentPattern, Is.EqualTo(FanCardRankPattern.QueenKingAce));
            string[] expectedQka =
            {
                "Queen_Q_Oxanium",
                "King_K_Oxanium",
                "Ace_A_Oxanium"
            };
            for (int index = 0; index < layers.Length; index++)
            {
                MeshFilter left = layers[index]
                    .Find("RankGlyph_TopLeft")
                    .GetComponent<MeshFilter>();
                MeshFilter right = layers[index]
                    .Find("RankGlyph_BottomRight")
                    .GetComponent<MeshFilter>();
                Assert.That(left.sharedMesh.name, Is.EqualTo(expectedQka[index]));
                Assert.That(right.sharedMesh, Is.SameAs(left.sharedMesh));
                Assert.That(presenter.RankForLayer(index), Is.EqualTo(new[]
                {
                    FanCardRank.Queen,
                    FanCardRank.King,
                    FanCardRank.Ace
                }[index]));
            }

            presenter.ApplyPattern(FanCardRankPattern.TripleAce);
            Assert.That(presenter.CurrentPattern, Is.EqualTo(FanCardRankPattern.TripleAce));
            foreach (Transform layer in layers)
            {
                Assert.That(
                    layer.Find("RankGlyph_TopLeft")
                        .GetComponent<MeshFilter>().sharedMesh.name,
                    Is.EqualTo("Ace_A_Oxanium"));
                Assert.That(
                    layer.Find("RankGlyph_BottomRight")
                        .GetComponent<MeshFilter>().sharedMesh.name,
                    Is.EqualTo("Ace_A_Oxanium"));
            }

            Assert.That(controller.Progress, Is.EqualTo(progress));
            Assert.That(semanticEvents, Is.Zero);
            for (int index = 0; index < layers.Length; index++)
            {
                Assert.That(layers[index].localPosition, Is.EqualTo(positions[index]));
                Assert.That(layers[index].localRotation, Is.EqualTo(rotations[index]));
            }
        }

        [Test]
        public void BackTrackKeepsTheLockedSixMillimeterOuterEdgeClearance()
        {
            Vector2 follower = FanCardSpecifications.FollowerFromPivot;
            float radius = follower.magnitude;
            float startAngle = Mathf.Atan2(follower.y, follower.x);
            float minimumClearance = float.PositiveInfinity;
            float halfTrackWidth = FanCardSpecifications.TrackShellWidth * 0.5f;
            for (int step = 0; step <= 720; step++)
            {
                float angle = startAngle + Mathf.Deg2Rad
                    * (45f * step / 720f);
                Vector2 radial = new(Mathf.Cos(angle), Mathf.Sin(angle));
                minimumClearance = Mathf.Min(
                    minimumClearance,
                    CardOutlineClearance(radial * (radius - halfTrackWidth)),
                    CardOutlineClearance(radial * (radius + halfTrackWidth)));
            }
            foreach (float endpointDegrees in new[] { 0f, 45f })
            {
                float endpointAngle = startAngle
                    + endpointDegrees * Mathf.Deg2Rad;
                Vector2 endpoint = new(
                    Mathf.Cos(endpointAngle) * radius,
                    Mathf.Sin(endpointAngle) * radius);
                for (int step = 0; step <= 180; step++)
                {
                    float capAngle = Mathf.PI * 2f * step / 180f;
                    Vector2 point = endpoint + new Vector2(
                        Mathf.Cos(capAngle),
                        Mathf.Sin(capAngle)) * halfTrackWidth;
                    minimumClearance = Mathf.Min(
                        minimumClearance,
                        CardOutlineClearance(point));
                }
            }

            Assert.That(
                minimumClearance,
                Is.GreaterThanOrEqualTo(
                    FanCardSpecifications.MinimumTrackOuterEdgeClearance),
                $"The complete undercut contour is only "
                + $"{minimumClearance * 1000f:F3} mm from the card edge. "
                + "This previously repeated regression must block the build.");
            Assert.That(
                minimumClearance * 1000f,
                Is.EqualTo(7.590f).Within(0.015f));
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
            string motion = File.ReadAllText(
                "Assets/Scripts/Product/EdcDeviceMotionController.cs");

            StringAssert.DoesNotContain("IosHaptics", controller);
            StringAssert.DoesNotContain("LinearMagneticDetentProfile", profile);
            StringAssert.DoesNotContain("RotorDetentProfile", profile);
            StringAssert.Contains("SemanticEventRaised", controller);
            StringAssert.Contains("HandleFanCardSemanticEvent", coordinator);
            StringAssert.Contains("FidgetHapticRouter.EmitFanCard", coordinator);
            StringAssert.Contains("fanCardController.IsDirectInteractionActive", motion);
            StringAssert.Contains("motionSuspendedForInteraction", motion);
            StringAssert.Contains(
                "SceneParallaxInput.Publish(filteredTilt, maximumInputAngle)",
                motion,
                "The parallax sample must remain frozen while direct manipulation owns the model.");
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
            const float planeTolerance = 0.000002f;
            Vector3[] vertices = mesh.vertices;
            int[] triangles = mesh.triangles;
            for (int index = 0; index < triangles.Length; index += 3)
            {
                Vector3 a = vertices[triangles[index]];
                Vector3 b = vertices[triangles[index + 1]];
                Vector3 c = vertices[triangles[index + 2]];
                if (Mathf.Abs(a.y - y) > planeTolerance
                    || Mathf.Abs(b.y - y) > planeTolerance
                    || Mathf.Abs(c.y - y) > planeTolerance)
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

        private static float CardOutlineClearance(Vector2 point)
        {
            Vector2 center = new(
                FanCardSpecifications.CardCenterFromPivot.x,
                FanCardSpecifications.CardCenterFromPivot.z);
            Vector2 local = new(
                Mathf.Abs(point.x - center.x),
                Mathf.Abs(point.y - center.y));
            float halfWidth = FanCardSpecifications.CardWidth * 0.5f;
            float halfHeight = FanCardSpecifications.CardHeight * 0.5f;
            float radius = FanCardSpecifications.CardCornerRadius;
            Vector2 cornerDistance = new(
                local.x - (halfWidth - radius),
                local.y - (halfHeight - radius));
            Vector2 outside = new(
                Mathf.Max(cornerDistance.x, 0f),
                Mathf.Max(cornerDistance.y, 0f));
            float signedDistance = outside.magnitude
                + Mathf.Min(Mathf.Max(cornerDistance.x, cornerDistance.y), 0f)
                - radius;
            return -signedDistance;
        }

        private static bool PointInTriangle(
            Vector2 point,
            Vector2 a,
            Vector2 b,
            Vector2 c)
        {
            const float signedAreaTolerance = 0.000000000001f;
            float d1 = Cross(point - a, b - a);
            float d2 = Cross(point - b, c - b);
            float d3 = Cross(point - c, a - c);
            bool negative = d1 < -signedAreaTolerance
                || d2 < -signedAreaTolerance
                || d3 < -signedAreaTolerance;
            bool positive = d1 > signedAreaTolerance
                || d2 > signedAreaTolerance
                || d3 > signedAreaTolerance;
            return !(negative && positive);
        }

        private static float Cross(Vector2 a, Vector2 b)
        {
            return a.x * b.y - a.y * b.x;
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
