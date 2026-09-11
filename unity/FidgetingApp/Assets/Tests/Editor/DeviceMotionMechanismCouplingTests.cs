using System.IO;
using FidgetingApp.EDC;
using FidgetingApp.EDC.Gate12R002;
using FidgetingApp.FanCard;
using FidgetingApp.Product;
using NUnit.Framework;
using ThreeBladeEDC;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    /// <summary>
    /// Device motion → mechanism state → semantic event coverage for the
    /// phone-frame rotor coupling, Device Twist dial, shake impulse, and the
    /// gravity / flick drives of the slide tile and fan card.
    /// </summary>
    public sealed class DeviceMotionMechanismCouplingTests
    {
        private static readonly Vector3 CameraRight = Vector3.right;
        private static readonly Vector3 CameraUp = Vector3.up;
        private static readonly Vector3 CameraForward = Vector3.forward;

        // ----- Core Motion → Unity mapping -----

        [Test]
        public void PhoneTwistCounterclockwiseMakesFreeRotorAppearClockwise()
        {
            // Core Motion +z is toward the user; +rz is counterclockwise on screen.
            Vector3 rotationRate = new(0f, 0f, 1f);
            Vector3 rotorAxisTowardViewer = -CameraForward;

            float rateAboutAxis = DeviceMotionMechanismCoupling.ResolvePhoneRateAboutAxis(
                rotationRate,
                CameraRight,
                CameraUp,
                CameraForward,
                rotorAxisTowardViewer);

            // Unity: positive about an axis pointing at the viewer is clockwise,
            // so the phone's counterclockwise twist is negative here...
            Assert.That(rateAboutAxis, Is.LessThan(0f));
            // ...and the free rotor, which changes by minus this value, appears clockwise.
            Assert.That(-rateAboutAxis, Is.GreaterThan(0f));
            Assert.That(
                Mathf.Abs(rateAboutAxis),
                Is.EqualTo(1f - DeviceMotionMechanismCoupling.RotationRateDeadZoneRadians)
                    .Within(0.0001f));
        }

        [Test]
        public void PitchAndRollRatesFlipSignWhileGravityDoesNot()
        {
            Vector3 angular = DeviceMotionMechanismCoupling.ResolvePhoneAngularVelocityWorld(
                new Vector3(1f, 2f, 3f),
                CameraRight,
                CameraUp,
                CameraForward);
            Vector3 gravity = DeviceMotionMechanismCoupling.ResolveDeviceVectorWorld(
                new Vector3(0f, -1f, 0f),
                CameraRight,
                CameraUp,
                CameraForward);
            Vector3 flat = DeviceMotionMechanismCoupling.ResolveDeviceVectorWorld(
                new Vector3(0f, 0f, -1f),
                CameraRight,
                CameraUp,
                CameraForward);

            Assert.That(angular, Is.EqualTo(new Vector3(-1f, -2f, 3f)));
            Assert.That(gravity, Is.EqualTo(-CameraUp));
            Assert.That(flat, Is.EqualTo(CameraForward));
        }

        [Test]
        public void RestingGyroNoiseNeverProducesRate()
        {
            float rate = DeviceMotionMechanismCoupling.ResolvePhoneRateAboutAxis(
                new Vector3(0.01f, -0.02f, 0.05f),
                CameraRight,
                CameraUp,
                CameraForward,
                CameraForward);

            Assert.That(rate, Is.EqualTo(0f));
            Assert.That(DeviceMotionMechanismCoupling.ApplyDeadZone(0.5f, 0.1f), Is.EqualTo(0.4f).Within(1e-5f));
            Assert.That(DeviceMotionMechanismCoupling.ApplyDeadZone(-0.5f, 0.1f), Is.EqualTo(-0.4f).Within(1e-5f));
            Assert.That(
                DeviceMotionMechanismCoupling.ResolvePhoneRateAboutAxis(
                    new Vector3(0f, 0f, 40f),
                    CameraRight,
                    CameraUp,
                    CameraForward,
                    CameraForward),
                Is.EqualTo(DeviceMotionMechanismCoupling.MaximumRotationRateRadians));
        }

        [Test]
        public void GravityTorqueIsZeroWhenHangingAndFollowsUnityRotationSign()
        {
            Vector3 axis = Vector3.up;
            Vector3 hangingLever = Vector3.back;
            Vector3 gravityDown = Vector3.back;

            Assert.That(
                DeviceMotionMechanismCoupling.ResolveGravityTorqueNormalized(
                    hangingLever,
                    gravityDown,
                    axis),
                Is.EqualTo(0f).Within(1e-6f));
            // Lever along +Z, gravity along +X: a positive Unity rotation about +Y.
            Assert.That(
                DeviceMotionMechanismCoupling.ResolveGravityTorqueNormalized(
                    Vector3.forward,
                    Vector3.right,
                    axis),
                Is.EqualTo(1f).Within(1e-6f));
            Assert.That(
                DeviceMotionMechanismCoupling.ResolveGravityTorqueNormalized(
                    Vector3.forward,
                    Vector3.left * 0.5f,
                    axis),
                Is.EqualTo(-0.5f).Within(1e-6f));
            // Gravity along the axis produces no in-plane torque.
            Assert.That(
                DeviceMotionMechanismCoupling.ResolveGravityTorqueNormalized(
                    Vector3.forward,
                    Vector3.up,
                    axis),
                Is.EqualTo(0f).Within(1e-6f));
        }

        // ----- Device Twist dial -----

        [Test]
        public void TwistDialRestNeverTicksOverSixtySeconds()
        {
            var dial = new DeviceTwistDial();
            int ticks = 0;
            for (int frame = 0; frame < 3600; frame++)
            {
                float noise = (frame % 2 == 0 ? 1f : -1f) * 0.05f;
                if (dial.Update(noise, 1f / 60f).EmitTick)
                {
                    ticks++;
                }
            }

            Assert.That(ticks, Is.EqualTo(0));
            Assert.That(dial.DetentIndex, Is.EqualTo(0));
            Assert.That(dial.AccumulatedDegrees, Is.EqualTo(0d));
        }

        [Test]
        public void TwistDialFullTurnCrossesConfiguredDetentCountWithoutWrapArtifacts()
        {
            var dial = new DeviceTwistDial();
            // 1 rad/s dead-zoned to 0.94 rad/s; run until 360° plus margin.
            float rate = 1f + DeviceTwistDial.RateDeadZoneRadians;
            float dt = 1f / 60f;
            float elapsed = 0f;
            int crossed = 0;
            while (elapsed < 2f * Mathf.PI + 0.05f)
            {
                crossed += dial.Update(rate, dt).CrossedDetents;
                elapsed += dt;
            }

            Assert.That(dial.DetentIndex, Is.EqualTo(DeviceTwistDial.DefaultDetentsPerTurn));
            Assert.That(crossed, Is.EqualTo(DeviceTwistDial.DefaultDetentsPerTurn));
            Assert.That(dial.AccumulatedDegrees, Is.GreaterThan(359d));

            // Turning back the same way returns to zero: continuous across the
            // ±180° seam because nothing ever wraps.
            elapsed = 0f;
            while (elapsed < 2f * Mathf.PI + 0.05f)
            {
                dial.Update(-rate, dt);
                elapsed += dt;
            }
            Assert.That(dial.DetentIndex, Is.EqualTo(0));
        }

        [Test]
        public void TwistDialBoundaryHysteresisPreventsChatter()
        {
            var dial = new DeviceTwistDial();
            float dt = 1f / 60f;
            // Move just past the first boundary (7.5° + 1° hysteresis).
            float degreesNeeded = dial.DetentStepDegrees * 0.5f
                + DeviceTwistDial.BoundaryHysteresisDegrees + 0.2f;
            float rate = degreesNeeded * Mathf.Deg2Rad / dt + DeviceTwistDial.RateDeadZoneRadians;
            DeviceTwistDialStep first = dial.Update(rate, dt);
            Assert.That(first.CrossedDetents, Is.EqualTo(1));
            Assert.That(dial.DetentIndex, Is.EqualTo(1));

            // Wobble ±0.8° around the boundary: inside the ±1° band, no ticks.
            float wobbleRate = 0.8f * Mathf.Deg2Rad / dt + DeviceTwistDial.RateDeadZoneRadians;
            int ticks = 0;
            for (int i = 0; i < 40; i++)
            {
                float signed = i % 2 == 0 ? -wobbleRate : wobbleRate;
                ticks += dial.Update(signed, dt).CrossedDetents;
            }
            Assert.That(ticks, Is.EqualTo(0));
            Assert.That(dial.DetentIndex, Is.EqualTo(1));
        }

        [Test]
        public void TwistDialRateLimitsTicksButNeverDelaysIndex()
        {
            var dial = new DeviceTwistDial();
            // 12 rad/s clamp = 687°/s → 45.8 detents/s at 24 per turn.
            float dt = 1f / 120f;
            int emitted = 0;
            int crossed = 0;
            for (int frame = 0; frame < 120; frame++)
            {
                DeviceTwistDialStep step = dial.Update(20f, dt);
                emitted += step.EmitTick ? 1 : 0;
                crossed += step.CrossedDetents;
                if (step.CrossedDetents > 0)
                {
                    Assert.That(step.NormalizedIntensity, Is.EqualTo(1f));
                }
            }

            float turned = DeviceTwistDial.MaximumRateRadians * Mathf.Rad2Deg;
            int expectedIndex = Mathf.FloorToInt(
                (turned - dial.DetentStepDegrees * 0.5f - DeviceTwistDial.BoundaryHysteresisDegrees)
                / dial.DetentStepDegrees) + 1;
            Assert.That(dial.DetentIndex, Is.EqualTo(expectedIndex));
            Assert.That(crossed, Is.EqualTo(expectedIndex));
            Assert.That(emitted, Is.LessThan(crossed));
            Assert.That(emitted, Is.LessThanOrEqualTo(Mathf.CeilToInt(1f / DeviceTwistDial.MinimumTickInterval) + 1));
        }

        [Test]
        public void TwistDialRecenterZeroesEverything()
        {
            var dial = new DeviceTwistDial();
            dial.Update(6f, 0.5f);
            Assert.That(dial.DetentIndex, Is.GreaterThan(0));

            dial.Recenter();

            Assert.That(dial.DetentIndex, Is.EqualTo(0));
            Assert.That(dial.AccumulatedDegrees, Is.EqualTo(0d));
        }

        // ----- Rotor phone-frame coupling -----

        [Test]
        public void FreeRotorLagsPhoneAndReturnsToRestAfterTwistStops()
        {
            const float maximum = 29f;
            float axialSpeed = 0f;
            float previousRate = 0f;
            float[] phoneRates = { 0f, 1f, 2f, 3f, 3f, 2f, 1f, 0f };
            float minimumDuringTwist = 0f;

            foreach (float rate in phoneRates)
            {
                FidgetSpinnerMotion.DeviceFrameCouplingResult result =
                    FidgetSpinnerMotion.ApplyDeviceFrameCoupling(
                        axialSpeed,
                        rate,
                        previousRate,
                        false,
                        false,
                        2.2f,
                        maximum);
                axialSpeed = result.AxialSpeed;
                previousRate = rate;
                minimumDuringTwist = Mathf.Min(minimumDuringTwist, axialSpeed);
                Assert.That(result.BrokeAway, Is.False);
                Assert.That(result.InhibitsCapture, Is.False);
            }

            Assert.That(minimumDuringTwist, Is.EqualTo(-3f).Within(1e-5f));
            Assert.That(axialSpeed, Is.EqualTo(0f).Within(1e-5f));
        }

        [Test]
        public void CapturedRatchetCoRotatesBelowBreakawayAndReleasesAtBreakawayRate()
        {
            FidgetSpinnerMotion.DeviceFrameCouplingResult held =
                FidgetSpinnerMotion.ApplyDeviceFrameCoupling(0f, 1.5f, 0f, true, true, 2.2f, 29f);
            Assert.That(held.AxialSpeed, Is.EqualTo(0f));
            Assert.That(held.BrokeAway, Is.False);
            Assert.That(held.InhibitsCapture, Is.False);

            FidgetSpinnerMotion.DeviceFrameCouplingResult released =
                FidgetSpinnerMotion.ApplyDeviceFrameCoupling(0f, 2.2f, 1.5f, true, true, 2.2f, 29f);
            Assert.That(released.BrokeAway, Is.True);
            Assert.That(released.InhibitsCapture, Is.True);
            // Lag starts at zero: the rotor co-rotated until this frame.
            Assert.That(released.AxialSpeed, Is.EqualTo(0f));

            FidgetSpinnerMotion.DeviceFrameCouplingResult accelerating =
                FidgetSpinnerMotion.ApplyDeviceFrameCoupling(0f, 3.2f, 2.2f, true, false, 2.2f, 29f);
            Assert.That(accelerating.AxialSpeed, Is.EqualTo(-1f).Within(1e-5f));
            Assert.That(accelerating.InhibitsCapture, Is.True);

            FidgetSpinnerMotion.DeviceFrameCouplingResult slowing =
                FidgetSpinnerMotion.ApplyDeviceFrameCoupling(-1f, 1f, 3.2f, true, false, 2.2f, 29f);
            Assert.That(slowing.InhibitsCapture, Is.False);
        }

        [Test]
        public void ZeroBreakawaySpeedCannotReleaseARestingPhone()
        {
            FidgetSpinnerMotion.DeviceFrameCouplingResult result =
                FidgetSpinnerMotion.ApplyDeviceFrameCoupling(0f, 0f, 0f, true, true, 0f, 29f);

            Assert.That(result.BrokeAway, Is.False);
        }

        // ----- Fan card gravity drive -----

        private static FanCardDetentProfile CreateFanProfile()
        {
            FanCardDetentProfile profile = ScriptableObject.CreateInstance<FanCardDetentProfile>();
            profile.ApplyReferenceDefaults();
            return profile;
        }

        [Test]
        public void FanCardZeroDeviceLoadKeepsTheApprovedEquationsAndRest()
        {
            FanCardDetentProfile profile = CreateFanProfile();
            try
            {
                var reference = new FanCardMagneticTrack(profile);
                var withParameter = new FanCardMagneticTrack(profile);
                for (int frame = 0; frame < 120; frame++)
                {
                    float target = frame < 60 ? 0.20f : 0.34f;
                    FanCardStepResult a = reference.Step(1f / 60f, target, true);
                    FanCardStepResult b = withParameter.Step(1f / 60f, target, true, 0f, 0f);
                    Assert.That(b.CrossedDetentCount, Is.EqualTo(a.CrossedDetentCount));
                    Assert.That(withParameter.Position, Is.EqualTo(reference.Position));
                }

                var resting = new FanCardMagneticTrack(profile);
                for (int frame = 0; frame < 600; frame++)
                {
                    resting.Step(1f / 60f, 0f, false, 0f, 0f);
                }
                Assert.That(resting.IsAtRest, Is.True);
                Assert.That(resting.CapturedDetentIndex, Is.EqualTo(0));
            }
            finally
            {
                Object.DestroyImmediate(profile);
            }
        }

        [Test]
        public void FanCardSubBreakawayGravityOnlyLeansAndNeverCrosses()
        {
            FanCardDetentProfile profile = CreateFanProfile();
            try
            {
                var track = new FanCardMagneticTrack(profile);
                float load = profile.BreakawayLoad * 0.8f;
                int crossings = 0;
                for (int frame = 0; frame < 300; frame++)
                {
                    crossings += track.Step(1f / 60f, 0f, false, 0f, load).CrossedDetentCount;
                }

                Assert.That(crossings, Is.EqualTo(0));
                Assert.That(track.CapturedDetentIndex, Is.EqualTo(0));
                Assert.That(track.State, Is.EqualTo(MagneticDetentState.Loading));
                Assert.That(track.LoadNormalized, Is.EqualTo(0.8f).Within(0.01f));
                Assert.That(track.VisualPosition, Is.GreaterThan(0f));
                Assert.That(track.Velocity, Is.EqualTo(0f));
            }
            finally
            {
                Object.DestroyImmediate(profile);
            }
        }

        [Test]
        public void FanCardSustainedGravityStepsOneDetentAtATimeAndStopsAtTheEnd()
        {
            FanCardDetentProfile profile = CreateFanProfile();
            try
            {
                var track = new FanCardMagneticTrack(profile);
                float load = profile.BreakawayLoad * 1.5f;
                int breakaways = 0;
                int crossings = 0;
                int captures = 0;
                int firstCaptureFrame = -1;
                for (int frame = 0; frame < 600; frame++)
                {
                    FanCardStepResult result = track.Step(1f / 60f, 0f, false, 0f, load);
                    breakaways += result.BrokeAway ? 1 : 0;
                    crossings += result.CrossedDetentCount;
                    captures += result.Captured ? 1 : 0;
                    if (result.Captured && firstCaptureFrame < 0)
                    {
                        firstCaptureFrame = frame;
                        Assert.That(track.CapturedDetentIndex, Is.EqualTo(1));
                        Assert.That(crossings, Is.EqualTo(1));
                    }
                }

                Assert.That(track.CapturedDetentIndex, Is.EqualTo(profile.DetentIntervals));
                Assert.That(breakaways, Is.EqualTo(profile.DetentIntervals));
                Assert.That(crossings, Is.EqualTo(profile.DetentIntervals));
                Assert.That(captures, Is.EqualTo(profile.DetentIntervals));
                Assert.That(track.Velocity, Is.EqualTo(0f));
                Assert.That(track.Position, Is.EqualTo(1f));
                Assert.That(firstCaptureFrame, Is.GreaterThan(0));

                // Fully open against the end stop: no further breakaway or motion.
                for (int frame = 0; frame < 120; frame++)
                {
                    FanCardStepResult result = track.Step(1f / 60f, 0f, false, 0f, load);
                    Assert.That(result.BrokeAway, Is.False);
                    Assert.That(result.CrossedDetentCount, Is.EqualTo(0));
                }
                Assert.That(track.Position, Is.EqualTo(1f));
                Assert.That(track.Velocity, Is.EqualTo(0f));
            }
            finally
            {
                Object.DestroyImmediate(profile);
            }
        }

        [Test]
        public void FanCardGravityStepLandsOnTheSameDetentAtThirtySixtyAndOneTwentyHertz()
        {
            FanCardDetentProfile profile = CreateFanProfile();
            try
            {
                float load = -profile.BreakawayLoad * 1.2f;
                int[] finalIndices = new int[3];
                float[] rates = { 30f, 60f, 120f };
                for (int i = 0; i < rates.Length; i++)
                {
                    var track = new FanCardMagneticTrack(profile);
                    track.ResetToDetent(profile.DetentIntervals);
                    float dt = 1f / rates[i];
                    float elapsed = 0f;
                    while (elapsed < 1.5f)
                    {
                        track.Step(dt, 0f, false, 0f, elapsed < 0.05f ? load : 0f);
                        elapsed += dt;
                    }
                    finalIndices[i] = track.CapturedDetentIndex;
                    Assert.That(track.IsAtRest, Is.True, $"rate {rates[i]}");
                    Assert.That(track.Velocity, Is.EqualTo(0f));
                }

                Assert.That(finalIndices[0], Is.EqualTo(profile.DetentIntervals - 1));
                Assert.That(finalIndices[1], Is.EqualTo(finalIndices[0]));
                Assert.That(finalIndices[2], Is.EqualTo(finalIndices[0]));
            }
            finally
            {
                Object.DestroyImmediate(profile);
            }
        }

        [Test]
        public void FanCardHandAlwaysOverridesDeviceGravity()
        {
            FanCardDetentProfile profile = CreateFanProfile();
            try
            {
                var track = new FanCardMagneticTrack(profile);
                for (int frame = 0; frame < 120; frame++)
                {
                    track.Step(1f / 60f, 0f, true, 0f, profile.BreakawayLoad * 3f);
                }

                Assert.That(track.CapturedDetentIndex, Is.EqualTo(0));
                Assert.That(track.State, Is.EqualTo(MagneticDetentState.Captured));
            }
            finally
            {
                Object.DestroyImmediate(profile);
            }
        }

        [Test]
        public void FanCardGravityLoadOpensWhenGravityPullsTheMovingPlatesOpenAndIsDeadZoned()
        {
            Vector3 pivotUp = Vector3.up;
            Vector3 lever = FanCardController.ResolveMovingCentroidLocal(0f);
            Vector3 openingDirection = Vector3.Cross(pivotUp, lever).normalized;
            // Positive Unity rotation about +Y moves the lever toward Cross(up, lever).

            float opening = FanCardController.ResolveDeviceGravityLoad(
                openingDirection,
                pivotUp,
                lever);
            float closing = FanCardController.ResolveDeviceGravityLoad(
                -openingDirection,
                pivotUp,
                lever);
            float hanging = FanCardController.ResolveDeviceGravityLoad(
                lever.normalized,
                pivotUp,
                lever);
            float alongAxis = FanCardController.ResolveDeviceGravityLoad(
                pivotUp,
                pivotUp,
                lever);

            Assert.That(opening, Is.GreaterThan(0f));
            Assert.That(closing, Is.LessThan(0f));
            Assert.That(
                opening,
                Is.EqualTo((1f - FanCardSpecifications.DeviceGravityTorqueDeadZone)
                    * FanCardSpecifications.DeviceGravityLoadScale).Within(1e-4f));
            Assert.That(hanging, Is.EqualTo(0f).Within(1e-5f));
            Assert.That(alongAxis, Is.EqualTo(0f).Within(1e-5f));
            Assert.That(
                FanCardController.ResolveDeviceGravityLoad(
                    openingDirection * 0.05f,
                    pivotUp,
                    lever),
                Is.EqualTo(0f));
        }

        // ----- Slide tile device drive -----

        private static MagneticSlideTileDeviceState SlideState(
            float travel,
            bool atMax,
            bool aligned,
            bool brokenAway,
            float angle)
        {
            return new MagneticSlideTileDeviceState(
                travel,
                0.018076433f,
                atMax,
                aligned,
                brokenAway,
                angle,
                12f,
                2.4f,
                5.4f);
        }

        [Test]
        public void SlideFlickDetectorUsesHysteresisCooldownAndOpposesAcceleration()
        {
            var detector = new MagneticSlideFlickDetector();
            float dt = 1f / 60f;

            Assert.That(detector.Update(0f, dt, out _, out _), Is.False);
            // Slow carry above threshold without jerk does not fire.
            Assert.That(detector.Update(0.05f, dt, out _, out _), Is.False);
            Assert.That(detector.Update(1.2f, 1f, out _, out _), Is.False);
            detector.Reset();

            Assert.That(detector.Update(0f, dt, out _, out _), Is.False);
            Assert.That(detector.Update(1.6f, dt, out int direction, out float strength), Is.True);
            Assert.That(direction, Is.EqualTo(-1));
            Assert.That(strength, Is.GreaterThan(0f).And.LessThan(1f));

            // Still high and inside cooldown: no second flick.
            Assert.That(detector.Update(1.8f, dt, out _, out _), Is.False);
            for (int i = 0; i < 20; i++)
            {
                detector.Update(0.1f, dt, out _, out _);
            }
            Assert.That(detector.Armed, Is.True);
            Assert.That(detector.Update(-1.5f, dt, out direction, out _), Is.True);
            Assert.That(direction, Is.EqualTo(1));
        }

        [Test]
        public void SlideDriveFlickTravelsToTheFarEndpointAndStops()
        {
            var drive = new MagneticSlideTileDeviceDrive();
            float dt = 1f / 60f;
            float travel = 0f;
            MagneticSlideTileDeviceState state = SlideState(travel, false, true, false, 0f);

            drive.Step(dt, new MagneticSlideTileDeviceSample(0f, 0f, 0f), state);
            MagneticSlideTileDeviceCommand first = drive.Step(
                dt,
                new MagneticSlideTileDeviceSample(0f, 0f, -1.6f),
                state);
            Assert.That(first.Kind, Is.EqualTo(MagneticSlideTileDeviceCommandKind.SetTravel));
            Assert.That(first.Value, Is.GreaterThan(0f));
            Assert.That(drive.IsSliding, Is.True);

            float last = first.Value;
            int frames = 0;
            while (drive.IsSliding && frames < 120)
            {
                MagneticSlideTileDeviceCommand next = drive.Step(
                    dt,
                    new MagneticSlideTileDeviceSample(0f, 0f, 0f),
                    SlideState(last, false, true, false, 0f));
                Assert.That(next.Kind, Is.EqualTo(MagneticSlideTileDeviceCommandKind.SetTravel));
                Assert.That(next.Value, Is.GreaterThanOrEqualTo(last));
                last = next.Value;
                frames++;
            }

            Assert.That(drive.IsSliding, Is.False);
            Assert.That(last, Is.EqualTo(0.018076433f).Within(1e-6f));
            Assert.That(frames, Is.LessThan(20));

            // Calm at the end: nothing more happens.
            MagneticSlideTileDeviceCommand idle = drive.Step(
                dt,
                new MagneticSlideTileDeviceSample(0f, 0f, 0f),
                SlideState(last, true, true, false, 0f));
            Assert.That(idle.Kind, Is.EqualTo(MagneticSlideTileDeviceCommandKind.None));
        }

        [Test]
        public void SlideDriveIgnoresFlicksWhileRotationIsMisaligned()
        {
            var drive = new MagneticSlideTileDeviceDrive();
            float dt = 1f / 60f;
            MagneticSlideTileDeviceState misaligned = SlideState(0.018076433f, true, false, false, 24f);

            drive.Step(dt, new MagneticSlideTileDeviceSample(0f, 0f, 0f), misaligned);
            MagneticSlideTileDeviceCommand command = drive.Step(
                dt,
                new MagneticSlideTileDeviceSample(0f, 0f, 1.9f),
                misaligned);

            Assert.That(command.Kind, Is.EqualTo(MagneticSlideTileDeviceCommandKind.None));
            Assert.That(drive.IsActive, Is.False);
        }

        [Test]
        public void SlideDriveGravityPendulumBreaksAwaySwingsAndCapturesAtZeroVelocity()
        {
            var drive = new MagneticSlideTileDeviceDrive();
            float dt = 1f / 60f;
            float angle = 0f;
            bool brokenAway = false;
            MagneticSlideTileDeviceCommand begin = drive.Step(
                dt,
                new MagneticSlideTileDeviceSample(0.9f, 0f, 0f),
                SlideState(0.018076433f, true, true, false, angle));

            Assert.That(begin.Kind, Is.EqualTo(MagneticSlideTileDeviceCommandKind.BeginRotation));
            Assert.That(begin.BreakawaySignDegrees, Is.EqualTo(2.4f));
            Assert.That(drive.IsRotating, Is.True);
            brokenAway = true;

            // Torque falls toward zero as the top approaches hanging (mock a pendulum
            // whose torque is sin of the remaining angle to 90°).
            int setAngleCommands = 0;
            bool captured = false;
            for (int frame = 0; frame < 600 && !captured; frame++)
            {
                float torque = Mathf.Sin((90f - angle) * Mathf.Deg2Rad);
                MagneticSlideTileDeviceCommand command = drive.Step(
                    dt,
                    new MagneticSlideTileDeviceSample(torque, 0f, 0f),
                    SlideState(0.018076433f, true, false, brokenAway, Mathf.Round(angle / 12f) * 12f));
                switch (command.Kind)
                {
                    case MagneticSlideTileDeviceCommandKind.SetAngle:
                        setAngleCommands++;
                        angle = command.Value;
                        break;
                    case MagneticSlideTileDeviceCommandKind.CaptureAngle:
                        captured = true;
                        angle = command.Value;
                        break;
                }
            }

            Assert.That(captured, Is.True);
            Assert.That(setAngleCommands, Is.GreaterThan(3));
            Assert.That(drive.IsRotating, Is.False);
            Assert.That(drive.AngularVelocityDegrees, Is.EqualTo(0f));
            Assert.That(Mathf.Abs(Mathf.DeltaAngle(angle, 84f)) <= 12.01f
                || Mathf.Abs(Mathf.DeltaAngle(angle, 96f)) <= 12.01f,
                $"captured near hanging, got {angle}");
            Assert.That(angle % 12f, Is.EqualTo(0f).Within(1e-4f));
        }

        [Test]
        public void SlideDriveSubThresholdGravityHoldsTheEndpointDetent()
        {
            var drive = new MagneticSlideTileDeviceDrive();
            for (int frame = 0; frame < 120; frame++)
            {
                MagneticSlideTileDeviceCommand command = drive.Step(
                    1f / 60f,
                    new MagneticSlideTileDeviceSample(0.25f, 0f, 0f),
                    SlideState(0.018076433f, true, true, false, 0f));
                Assert.That(command.Kind, Is.EqualTo(MagneticSlideTileDeviceCommandKind.None));
            }
            Assert.That(drive.IsActive, Is.False);
        }

        [Test]
        public void SlideDrivePhoneTwistAboveBreakawayReleasesTheTopAgainstTheTwist()
        {
            var drive = new MagneticSlideTileDeviceDrive();
            float dt = 1f / 60f;
            drive.Step(dt, new MagneticSlideTileDeviceSample(0f, 0f, 0f), SlideState(0.018076433f, true, true, false, 0f));
            MagneticSlideTileDeviceCommand begin = drive.Step(
                dt,
                new MagneticSlideTileDeviceSample(0f, 150f, 0f),
                SlideState(0.018076433f, true, true, false, 0f));

            Assert.That(begin.Kind, Is.EqualTo(MagneticSlideTileDeviceCommandKind.BeginRotation));
            Assert.That(begin.BreakawaySignDegrees, Is.EqualTo(-2.4f));

            // Body keeps turning faster: the top lags (negative relative rate).
            MagneticSlideTileDeviceCommand lag = drive.Step(
                dt,
                new MagneticSlideTileDeviceSample(0f, 210f, 0f),
                SlideState(0.018076433f, true, false, true, 0f));
            Assert.That(lag.Kind, Is.EqualTo(MagneticSlideTileDeviceCommandKind.SetAngle));
            Assert.That(drive.AngularVelocityDegrees, Is.LessThan(0f));
        }

        [Test]
        public void SlideDeviceSampleMapsTorqueTwistAndSlideAccelerationIntoTheMechanismFrame()
        {
            Vector3 axis = Vector3.forward;
            Vector3 lever = Vector3.down;
            Vector3 slideDirection = Vector3.down;

            MagneticSlideTileDeviceSample hanging = EdcSliderController.ResolveDeviceSample(
                Vector3.down,
                Vector3.zero,
                Vector3.zero,
                axis,
                lever,
                slideDirection);
            MagneticSlideTileDeviceSample tilted = EdcSliderController.ResolveDeviceSample(
                Vector3.right,
                Vector3.down * 1.5f,
                axis * 1f,
                axis,
                lever,
                slideDirection);

            Assert.That(hanging.GravityTorqueNormalized, Is.EqualTo(0f).Within(1e-5f));
            Assert.That(hanging.SlideAccelerationG, Is.EqualTo(0f));
            Assert.That(
                Mathf.Abs(tilted.GravityTorqueNormalized),
                Is.EqualTo(1f - DeviceMotionMechanismCoupling.GravityTorqueDeadZone).Within(1e-4f));
            Assert.That(tilted.SlideAccelerationG, Is.EqualTo(1.5f).Within(1e-5f));
            Assert.That(
                tilted.PhoneRateAboutAxisDegrees,
                Is.EqualTo((1f - DeviceMotionMechanismCoupling.RotationRateDeadZoneRadians) * Mathf.Rad2Deg)
                    .Within(1e-3f));
        }

        // ----- Architecture: motion input never talks to the renderer directly -----

        [Test]
        public void DeviceMotionHapticsOriginateFromMechanismsNotFromMotionInput()
        {
            string metalMotion = File.ReadAllText(
                "Assets/Scripts/Product/MetalDeviceMotionController.cs");
            string classicMotion = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/DeviceMotionController.cs");
            string edcMotion = File.ReadAllText(
                "Assets/Scripts/Product/EdcDeviceMotionController.cs");
            string rotor = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Interaction/RotorRigidbodyController.cs");
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string router = File.ReadAllText("Assets/Scripts/FidgetSpinner/IosHaptics.cs");
            string fanCard = File.ReadAllText("Assets/_FanCard/Runtime/FanCardController.cs");
            string slider = File.ReadAllText("Assets/_EDC/Runtime/EdcSliderController.cs");
            string slideDrive = File.ReadAllText(
                "Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/MagneticSlideTileDeviceDrive.cs");

            string classicSpinner = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/FidgetSpinnerController.cs");

            // Shake: motion input applies an impulse; the rotor raises ShakeBurst.
            StringAssert.Contains("rotor?.ApplyDeviceShakeImpulse(", metalMotion);
            StringAssert.DoesNotContain("AddFlickVelocity", metalMotion);
            StringAssert.DoesNotContain("FidgetSemanticEvent.ShakeBurst", metalMotion);
            StringAssert.Contains("EmitSemantic(FidgetSemanticEvent.ShakeBurst", rotor);
            StringAssert.Contains("spinner.ApplyDeviceShakeImpulse(", classicMotion);
            StringAssert.DoesNotContain("FidgetSemanticEvent.ShakeBurst", classicMotion);
            StringAssert.Contains("FidgetSemanticEvent.ShakeBurst", classicSpinner);
            StringAssert.DoesNotContain("IosHaptics.", classicSpinner);

            // Phone-frame coupling reaches every rotor as state, not as a haptic.
            StringAssert.Contains("rotor.SetDeviceFrameRotationRate(", metalMotion);
            StringAssert.Contains("ApplyDeviceFrameCoupling(", rotor);
            StringAssert.Contains("_deviceFrameInhibitsCapture", rotor);
            StringAssert.Contains("ClearDeviceFrameRotation();", rotor);
            StringAssert.Contains("spinner.SetDeviceFrameRotationRate(", classicMotion);
            StringAssert.Contains(".ApplyDeviceFrameCoupling(", classicSpinner);
            StringAssert.Contains("ClearDeviceFrameRotation();", classicSpinner);

            // Twist dial ticks travel as mechanism events through the coordinator.
            StringAssert.Contains("FidgetSemanticEvent.TwistDetentCrossed", metalMotion);
            StringAssert.Contains("FidgetSemanticEvent.TwistDetentCrossed", classicMotion);
            StringAssert.Contains("SemanticEventRaised?.Invoke(", metalMotion);
            StringAssert.Contains("SemanticEventRaised?.Invoke(", classicMotion);
            StringAssert.DoesNotContain("FidgetHapticRouter.Emit(FidgetSemanticEvent.TwistDetentCrossed", metalMotion);
            StringAssert.DoesNotContain("FidgetHapticRouter.Emit(FidgetSemanticEvent.TwistDetentCrossed", classicMotion);
            StringAssert.Contains("metalMotion.SemanticEventRaised += HandleRotorSemanticEvent;", coordinator);
            StringAssert.Contains("blueMotion.SemanticEventRaised += HandleRotorSemanticEvent;", coordinator);
            StringAssert.Contains("rotor.IsDetentTravelActive", metalMotion);
            StringAssert.Contains("TwistDetentCrossed = 16", router);
            StringAssert.Contains("semanticEvent == FidgetSemanticEvent.TwistDetentCrossed", router);
            StringAssert.Contains("BadgeUnlocked = 15", router);

            // EDC motion only supplies samples; mechanisms own the events.
            StringAssert.DoesNotContain("FidgetHapticRouter", edcMotion);
            StringAssert.DoesNotContain("IosHaptics", edcMotion);
            StringAssert.DoesNotContain("SemanticEventRaised", edcMotion);
            StringAssert.Contains("sliderController?.SetDeviceMotionSample(", edcMotion);
            StringAssert.Contains("fanCardController?.SetDeviceGravity(", edcMotion);
            StringAssert.Contains("out Vector3 gravity,", edcMotion);
            StringAssert.Contains("out Vector3 userAcceleration)", edcMotion);
            StringAssert.DoesNotContain("IosHaptics", fanCard);
            StringAssert.DoesNotContain("FidgetHapticRouter", fanCard);
            StringAssert.DoesNotContain("IosHaptics", slider);
            StringAssert.DoesNotContain("FidgetHapticRouter", slider);
            StringAssert.DoesNotContain("IosHaptics", slideDrive);
            StringAssert.DoesNotContain("SemanticEvent", slideDrive);
            StringAssert.Contains("deviceDrive.Cancel();", slider);

            // Library browsing disables every device→mechanism drive.
            StringAssert.Contains("blueMotion?.SetMechanismDriveEnabled(mechanismDrive);", coordinator);
            StringAssert.Contains("metalMotion?.SetMechanismDriveEnabled(mechanismDrive);", coordinator);
            StringAssert.Contains("edcMotion?.SetMechanismDriveEnabled(mechanismDrive);", coordinator);
        }
    }
}
