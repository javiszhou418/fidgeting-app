using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.EDC.Tests.Editor
{
    public sealed class MagneticDetentTrack1DTests
    {
        private LinearMagneticDetentProfile profile;

        [SetUp]
        public void CreateProfile()
        {
            profile = ScriptableObject.CreateInstance<LinearMagneticDetentProfile>();
            profile.ApplyHeavyDefaults();
        }

        [TearDown]
        public void DestroyProfile()
        {
            Object.DestroyImmediate(profile);
        }

        [Test]
        public void HeavyProfile_IsTheSingleSixDetent68MillimeterSource()
        {
            Assert.That(profile.DetentCount, Is.EqualTo(6));
            Assert.That(profile.TravelMeters, Is.EqualTo(0.068f).Within(0.000001f));
            for (int index = 0; index < profile.DetentCount; index++)
            {
                Assert.That(
                    profile.GetDetentPositionMeters(index),
                    Is.EqualTo(index * 0.0136f).Within(0.000001f));
            }
            Assert.That(profile.MovingMassKilograms, Is.EqualTo(0.055f));
            Assert.That(profile.HandSpringNewtonsPerMeter, Is.EqualTo(100f));
            Assert.That(profile.HandDampingNewtonSecondsPerMeter, Is.EqualTo(5.0f));
            Assert.That(profile.BreakawayForceNewtons, Is.EqualTo(0.44f));
            Assert.That(profile.MagneticPeakForceNewtons, Is.EqualTo(0.42f));
            Assert.That(profile.RailFrictionNewtons, Is.EqualTo(0.085f));
            Assert.That(profile.RailDampingNewtonSecondsPerMeter, Is.EqualTo(0.30f));
            Assert.That(profile.DefaultDetentIndex, Is.EqualTo(2));
            Assert.That(profile.DefaultPositionMeters, Is.EqualTo(0.0272f));
            Assert.That(profile.MaximumVisiblePreloadMeters, Is.EqualTo(0.0009f));
            Assert.That(profile.CaptureSpringNewtonsPerMeter, Is.EqualTo(150f));
            Assert.That(profile.CaptureDampingNewtonSecondsPerMeter, Is.EqualTo(5.8f));
            Assert.That(profile.EdgeProbeLoads, Is.EqualTo(new[] { 0.72f, 0.84f, 0.94f }));
            Assert.That(profile.EdgeProbeRearmLoad, Is.EqualTo(0.55f));
            Assert.That(profile.EdgeProbeMinimumIntensity, Is.EqualTo(0.20f));
            Assert.That(profile.EdgeProbeMaximumIntensity, Is.EqualTo(0.38f));
            Assert.That(profile.EdgeProbeMinimumSharpness, Is.EqualTo(0.18f));
            Assert.That(profile.EdgeProbeMaximumSharpness, Is.EqualTo(0.32f));
            Assert.That(profile.EdgeProbePulseDurationSeconds, Is.EqualTo(0.016f));
            Assert.That(profile.DetentHapticIntensity, Is.EqualTo(0.98f));
            Assert.That(profile.DetentHapticSharpness, Is.EqualTo(0.78f));
            Assert.That(profile.DetentHapticBodyIntensity, Is.EqualTo(0.58f));
            Assert.That(profile.DetentHapticBodySharpness, Is.EqualTo(0.22f));
            Assert.That(profile.DetentHapticBodyDurationSeconds, Is.EqualTo(0.030f));
            Assert.That(profile.DetentHapticSecondaryIntensity, Is.EqualTo(0.52f));
            Assert.That(profile.DetentHapticSecondarySharpness, Is.EqualTo(0.44f));
            Assert.That(profile.DetentHapticPulseIntervalSeconds, Is.EqualTo(0.022f));
            Assert.That(profile.EdgeGovernorStartSpeedMetersPerSecond, Is.EqualTo(0.022f));
            Assert.That(profile.EdgeGovernorEndSpeedMetersPerSecond, Is.EqualTo(0.0055f));
            Assert.That(profile.MaximumSubstepsPerFrame, Is.EqualTo(8));
        }

        [Test]
        public void InteriorDefaultDetent_CanBreakAwayImmediatelyInBothDirections()
        {
            var left = new MagneticDetentTrack1D(profile);
            var right = new MagneticDetentTrack1D(profile);
            left.ResetToDetent(profile.DefaultDetentIndex);
            right.ResetToDetent(profile.DefaultDetentIndex);

            MagneticDetentStepResult leftResult = left.Step(1f / 120f, 0f, true);
            MagneticDetentStepResult rightResult = right.Step(
                1f / 120f,
                profile.TravelMeters,
                true);

            Assert.That(leftResult.BrokeAway, Is.True);
            Assert.That(rightResult.BrokeAway, Is.True);
            Assert.That(left.VelocityMetersPerSecond, Is.LessThan(0f));
            Assert.That(right.VelocityMetersPerSecond, Is.GreaterThan(0f));
        }

        [Test]
        public void BelowBreakaway_LoadsVisuallyButCannotLeaveCapturedDetent()
        {
            var track = new MagneticDetentTrack1D(profile);
            float subThresholdTarget = 0.99f
                * profile.BreakawayForceNewtons
                / profile.HandSpringNewtonsPerMeter;
            for (int frame = 0; frame < 30; frame++)
            {
                MagneticDetentStepResult result = track.Step(
                    1f / 60f,
                    subThresholdTarget,
                    true);
                Assert.That(result.BrokeAway, Is.False);
            }

            Assert.That(track.State, Is.EqualTo(MagneticDetentState.Loading));
            Assert.That(track.PositionMeters, Is.Zero.Within(0.000001f));
            Assert.That(track.VelocityMetersPerSecond, Is.Zero);
            Assert.That(track.LoadNormalized, Is.EqualTo(0.99f).Within(0.002f));
            Assert.That(
                track.VisiblePreloadMeters,
                Is.EqualTo(profile.MaximumVisiblePreloadMeters * 0.99f)
                    .Within(0.00001f));
        }

        [Test]
        public void BreakawayThreshold_FiresExactlyOnceUntilAnotherCapture()
        {
            var track = new MagneticDetentTrack1D(profile);
            float target = 1.01f
                * profile.BreakawayForceNewtons
                / profile.HandSpringNewtonsPerMeter;
            int breakaways = 0;
            float breakawayVelocity = 0f;
            for (int frame = 0; frame < 20; frame++)
            {
                if (track.Step(1f / 120f, target, true).BrokeAway)
                {
                    breakaways++;
                    breakawayVelocity = Mathf.Abs(track.VelocityMetersPerSecond);
                }
            }

            Assert.That(breakaways, Is.EqualTo(1));
            Assert.That(track.PositionMeters, Is.GreaterThan(0f));
            Assert.That(
                breakawayVelocity,
                Is.LessThan(0.045f),
                "Stored preload may release controllably but must not launch the tile.");
        }

        [Test]
        public void SlowManualSearch_DeceleratesNearBarrierAndStillCrossesIt()
        {
            var track = new MagneticDetentTrack1D(profile);
            const float deltaTime = 1f / 120f;
            const float handSpeed = 0.010f;
            float handTarget = 0f;
            float middleMaximumSpeed = 0f;
            float edgeMaximumSpeed = 0f;
            bool crossed = false;

            for (int frame = 0; frame < 1200 && !crossed; frame++)
            {
                handTarget = Mathf.Min(
                    profile.GetDetentPositionMeters(1),
                    handTarget + handSpeed * deltaTime);
                MagneticDetentStepResult result = track.Step(
                    deltaTime,
                    handTarget,
                    true,
                    true);
                float progress = track.BarrierProgress;
                float speed = Mathf.Abs(track.VelocityMetersPerSecond);
                if (progress >= 0.56f && progress <= 0.70f)
                {
                    middleMaximumSpeed = Mathf.Max(middleMaximumSpeed, speed);
                }
                if (progress >= 0.86f && progress <= 0.98f)
                {
                    edgeMaximumSpeed = Mathf.Max(edgeMaximumSpeed, speed);
                }
                crossed = result.CrossedDetentCount > 0;
            }

            Assert.That(crossed, Is.True, "The edge governor must never deadlock crossing.");
            Assert.That(middleMaximumSpeed, Is.GreaterThan(0.007f));
            Assert.That(edgeMaximumSpeed, Is.GreaterThan(0f));
            Assert.That(edgeMaximumSpeed, Is.LessThan(middleMaximumSpeed * 0.70f));
            Assert.That(
                edgeMaximumSpeed,
                Is.LessThanOrEqualTo(0.009f),
                "The last edge-search segment should be visibly slower than approach.");
        }

        [Test]
        public void ManualPullPastCapturingDetent_ImmediatelyReturnsControlToFinger()
        {
            var track = new MagneticDetentTrack1D(profile);
            const float deltaTime = 1f / 120f;
            float handTarget = 0f;
            bool enteredCapture = false;

            for (int frame = 0; frame < 1200; frame++)
            {
                handTarget = Mathf.Min(
                    profile.GetDetentPositionMeters(1),
                    handTarget + 0.010f * deltaTime);
                track.Step(deltaTime, handTarget, true, true);
                if (track.State == MagneticDetentState.Capturing)
                {
                    enteredCapture = true;
                    break;
                }
            }

            Assert.That(enteredCapture, Is.True, "The setup must enter magnetic capture.");
            float positionBeforePull = track.PositionMeters;
            track.Step(deltaTime, profile.TravelMeters, true, false);

            Assert.That(
                track.State,
                Is.Not.EqualTo(MagneticDetentState.Capturing),
                "An active finger pulling beyond the next threshold must not be trapped "
                + "inside a stale capture animation.");
            Assert.That(track.PositionMeters, Is.GreaterThan(positionBeforePull));
        }

        [Test]
        public void SpatialEdgeCues_DoNotRepeatWhileFingerHoldsStill()
        {
            var sequence = new MagneticEdgeProbeSequence();

            MagneticEdgeProbeResult first = sequence.Step(0.72f, 1, true, profile);
            Assert.That(first.ShouldEmit, Is.True);
            Assert.That(first.MilestoneIndex, Is.Zero);
            Assert.That(first.NormalizedSignal, Is.Zero);

            for (int frame = 0; frame < 240; frame++)
            {
                Assert.That(
                    sequence.Step(0.72f, 1, true, profile).ShouldEmit,
                    Is.False,
                    "Two seconds of stationary touch must remain silent after the cue.");
            }

            MagneticEdgeProbeResult second = sequence.Step(0.84f, 1, true, profile);
            MagneticEdgeProbeResult third = sequence.Step(0.94f, 1, true, profile);
            Assert.That(second.MilestoneIndex, Is.EqualTo(1));
            Assert.That(second.NormalizedSignal, Is.EqualTo(0.5f));
            Assert.That(third.MilestoneIndex, Is.EqualTo(2));
            Assert.That(third.NormalizedSignal, Is.EqualTo(1f));
            Assert.That(sequence.Step(1f, 1, true, profile).ShouldEmit, Is.False);

            Assert.That(
                sequence.Step(0.54f, 1, true, profile).ShouldEmit,
                Is.False);
            Assert.That(
                sequence.Step(0.72f, 1, true, profile).ShouldEmit,
                Is.True,
                "Only spatial retreat below the re-arm load may enable a new cue.");
        }

        [Test]
        public void PoweredTraversal_ReportsEveryBarrierAndEndsExactlyAtRest()
        {
            var track = new MagneticDetentTrack1D(profile);
            int crossings = 0;
            int captures = 0;
            for (int frame = 0; frame < 600 && !IsCapturedAt(track, 5); frame++)
            {
                MagneticDetentStepResult result = track.Step(
                    1f / 120f,
                    profile.TravelMeters,
                    true);
                crossings += result.CrossedDetentCount;
                captures += result.Captured ? 1 : 0;
            }

            Assert.That(crossings, Is.EqualTo(5));
            Assert.That(captures, Is.GreaterThanOrEqualTo(1));
            Assert.That(track.CapturedDetentIndex, Is.EqualTo(5));
            Assert.That(track.PositionMeters, Is.EqualTo(0.068f).Within(0.000001f));
            Assert.That(track.VelocityMetersPerSecond, Is.Zero);
        }

        [Test]
        public void FastTraversal_CanReportMultipleBarrierCrossingsInOneFrame()
        {
            var track = new MagneticDetentTrack1D(profile);
            int maximumCrossingsInFrame = 0;
            int totalCrossings = 0;
            for (int frame = 0; frame < 120 && !IsCapturedAt(track, 5); frame++)
            {
                MagneticDetentStepResult result = track.Step(
                    1f / 30f,
                    profile.TravelMeters,
                    true);
                maximumCrossingsInFrame = Mathf.Max(
                    maximumCrossingsInFrame,
                    result.CrossedDetentCount);
                totalCrossings += result.CrossedDetentCount;
            }

            Assert.That(totalCrossings, Is.EqualTo(5));
            Assert.That(maximumCrossingsInFrame, Is.GreaterThanOrEqualTo(2));
        }

        [Test]
        public void BreakawayTiming_RemainsWithinOneThirtyHertzFrameAcrossFrameRates()
        {
            float at30 = SimulateBreakawayTime(30);
            float at60 = SimulateBreakawayTime(60);
            float at120 = SimulateBreakawayTime(120);
            Assert.That(Mathf.Abs(at30 - at120), Is.LessThanOrEqualTo(1f / 30f));
            Assert.That(Mathf.Abs(at60 - at120), Is.LessThanOrEqualTo(1f / 30f));
        }

        [Test]
        public void ForwardAndReverseTracks_AreSymmetric()
        {
            var forward = new MagneticDetentTrack1D(profile);
            var reverse = new MagneticDetentTrack1D(profile);
            reverse.ResetToDetent(5);
            int forwardCrossings = 0;
            int reverseCrossings = 0;

            for (int frame = 0; frame < 600; frame++)
            {
                forwardCrossings += forward.Step(
                    1f / 120f,
                    profile.TravelMeters,
                    true).CrossedDetentCount;
                reverseCrossings += reverse.Step(
                    1f / 120f,
                    0f,
                    true).CrossedDetentCount;
                if (IsCapturedAt(forward, 5) && IsCapturedAt(reverse, 0))
                {
                    break;
                }
            }

            Assert.That(forwardCrossings, Is.EqualTo(5));
            Assert.That(reverseCrossings, Is.EqualTo(5));
            Assert.That(
                forward.PositionMeters,
                Is.EqualTo(profile.TravelMeters - reverse.PositionMeters)
                    .Within(0.0002f));
            Assert.That(forward.VelocityMetersPerSecond, Is.Zero);
            Assert.That(reverse.VelocityMetersPerSecond, Is.Zero);
        }

        [Test]
        public void Release_UsesPositionAndVelocityPredictionThenCapturesNearestDetent()
        {
            var track = new MagneticDetentTrack1D(profile);
            float target = profile.GetDetentPositionMeters(2);
            float minimumTravel = profile.GetDetentPositionMeters(1) * 0.95f;
            for (int frame = 0; frame < 80 && track.PositionMeters < minimumTravel; frame++)
            {
                track.Step(1f / 120f, target, true);
            }
            track.Release();
            for (int frame = 0; frame < 600 && !track.IsAtRest; frame++)
            {
                track.Step(1f / 120f, 0f, false);
            }

            Assert.That(track.IsAtRest, Is.True);
            Assert.That(track.CapturedDetentIndex, Is.InRange(1, 3));
            Assert.That(
                track.PositionMeters,
                Is.EqualTo(profile.GetDetentPositionMeters(track.CapturedDetentIndex))
                    .Within(0.000001f));
            Assert.That(track.VelocityMetersPerSecond, Is.Zero);
        }

        [TestCase(30)]
        [TestCase(60)]
        [TestCase(120)]
        public void FrameRateVariants_ReachSameFinalDetentWithinPointTwoMillimeters(int hz)
        {
            MagneticDetentTrack1D reference = SimulatePoweredTraversal(120);
            MagneticDetentTrack1D candidate = SimulatePoweredTraversal(hz);
            Assert.That(candidate.CapturedDetentIndex, Is.EqualTo(reference.CapturedDetentIndex));
            Assert.That(
                candidate.PositionMeters,
                Is.EqualTo(reference.PositionMeters).Within(0.0002f));
            Assert.That(candidate.VelocityMetersPerSecond, Is.Zero);
        }

        [Test]
        public void EndpointPressure_DoesNotChatterOrCreateBoundaryCrossings()
        {
            var track = new MagneticDetentTrack1D(profile);
            int crossings = 0;
            for (int frame = 0; frame < 240; frame++)
            {
                MagneticDetentStepResult result = track.Step(1f / 120f, -0.020f, true);
                crossings += result.CrossedDetentCount;
                Assert.That(result.BrokeAway, Is.False);
            }
            Assert.That(crossings, Is.Zero);
            Assert.That(track.CapturedDetentIndex, Is.Zero);
            Assert.That(track.VelocityMetersPerSecond, Is.Zero);
        }

        private MagneticDetentTrack1D SimulatePoweredTraversal(int hz)
        {
            var track = new MagneticDetentTrack1D(profile);
            for (int frame = 0; frame < hz * 5 && !IsCapturedAt(track, 5); frame++)
            {
                track.Step(1f / hz, profile.TravelMeters, true);
            }
            return track;
        }

        private float SimulateBreakawayTime(int hz)
        {
            var track = new MagneticDetentTrack1D(profile);
            float elapsed = 0f;
            float deltaTime = 1f / hz;
            const float handTargetSpeed = 0.010f;
            for (int frame = 0; frame < hz * 2; frame++)
            {
                elapsed += deltaTime;
                float handTarget = handTargetSpeed * elapsed;
                if (track.Step(deltaTime, handTarget, true).BrokeAway)
                {
                    return elapsed;
                }
            }
            Assert.Fail("The ramped hand target never reached breakaway.");
            return float.PositiveInfinity;
        }

        private static bool IsCapturedAt(MagneticDetentTrack1D track, int index)
        {
            return track.IsAtRest && track.CapturedDetentIndex == index;
        }
    }
}
