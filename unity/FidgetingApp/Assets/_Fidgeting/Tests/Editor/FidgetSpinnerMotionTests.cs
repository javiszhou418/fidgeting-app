using CodexUnityLab;
using FidgetingApp.Product;
using NUnit.Framework;
using ThreeBladeEDC.Interaction;
using UnityEngine;

namespace ThreeBladeEDC.Tests.Editor
{
    public sealed class FidgetSpinnerMotionTests
    {
        [SetUp]
        public void SetUp()
        {
            FidgetHapticRecipeLibrary.ClearOverrides();
        }

        [TearDown]
        public void TearDown()
        {
            FidgetHapticRecipeLibrary.ClearOverrides();
        }

        [Test]
        public void CoastHalfLife_HalvesSpeedIndependentOfModel()
        {
            Assert.That(
                FidgetSpinnerMotion.ApplyCoastHalfLife(20f, 2f, 2f),
                Is.EqualTo(10f).Within(0.0001f));
        }

        [Test]
        public void CoastHalfLife_NeverCreatesMotionFromRest()
        {
            Assert.That(
                FidgetSpinnerMotion.ApplyCoastHalfLife(0f, 0.02f, 5f),
                Is.EqualTo(0f));
        }

        [Test]
        public void GestureSpeedMapping_IsDirectionalResponsiveAndClamped()
        {
            float slow = FidgetSpinnerMotion.MapGestureToAngularSpeed(
                1f,
                2f,
                1f / 60f,
                0.65f,
                24f,
                1100f,
                0.5f);
            float fast = FidgetSpinnerMotion.MapGestureToAngularSpeed(
                10f,
                20f,
                1f / 60f,
                0.65f,
                24f,
                1100f,
                0.5f);
            float opposite = FidgetSpinnerMotion.MapGestureToAngularSpeed(
                -10f,
                20f,
                1f / 60f,
                0.65f,
                24f,
                1100f,
                0.5f);

            Assert.That(slow, Is.GreaterThan(0.5f));
            Assert.That(fast, Is.GreaterThan(slow * 2f));
            Assert.That(fast, Is.LessThanOrEqualTo(24f));
            Assert.That(opposite, Is.EqualTo(-fast).Within(0.0001f));
        }

        [Test]
        public void GestureSpeedMapping_RejectsSubpixelSpikeAndHasWideTouchResponseRange()
        {
            float spike = FidgetSpinnerMotion.MapGestureToAngularSpeed(
                12f,
                0.5f,
                0.001f,
                1f,
                42f,
                720f);

            Assert.That(spike, Is.Zero, "A tiny sample must not become a max-speed spin.");
            Assert.That(
                FidgetSpinnerMotion.TouchResponseToSensitivityGain(1f),
                Is.GreaterThan(
                    FidgetSpinnerMotion.TouchResponseToSensitivityGain(0f) * 8f));
        }

        [Test]
        public void TouchResponse_ResolvesOneMonotonicServoProfile()
        {
            FidgetSpinnerMotion.TouchResponseProfile low =
                FidgetSpinnerMotion.ResolveTouchResponse(0f);
            FidgetSpinnerMotion.TouchResponseProfile middle =
                FidgetSpinnerMotion.ResolveTouchResponse(0.5f);
            FidgetSpinnerMotion.TouchResponseProfile high =
                FidgetSpinnerMotion.ResolveTouchResponse(1f);

            Assert.That(low.MaximumAngularSpeed, Is.LessThan(middle.MaximumAngularSpeed));
            Assert.That(middle.MaximumAngularSpeed, Is.LessThan(high.MaximumAngularSpeed));
            Assert.That(low.ScreenSpeedForFullSpin, Is.GreaterThan(middle.ScreenSpeedForFullSpin));
            Assert.That(middle.ScreenSpeedForFullSpin, Is.GreaterThan(high.ScreenSpeedForFullSpin));
            Assert.That(low.DragBrakeResponse, Is.GreaterThan(low.DragFollowResponse));
            Assert.That(high.DragBrakeResponse, Is.GreaterThan(high.DragFollowResponse));
        }

        [Test]
        public void SerializedDefaults_AreDerivedFromTheProductResponseAndResistance()
        {
            FidgetSpinnerMotion.TouchResponseProfile profile =
                FidgetSpinnerMotion.ResolveTouchResponse(
                    FidgetSpinnerMotion.DefaultTouchResponse);

            Assert.That(
                profile.MaximumAngularSpeed,
                Is.EqualTo(FidgetSpinnerMotion.DefaultMaximumAngularSpeed).Within(0.0001f));
            Assert.That(
                profile.ScreenSpeedForFullSpin,
                Is.EqualTo(FidgetSpinnerMotion.DefaultScreenSpeedForFullSpin).Within(0.001f));
            Assert.That(
                profile.DragFollowResponse,
                Is.EqualTo(FidgetSpinnerMotion.DefaultDragFollowResponse).Within(0.0001f));
            Assert.That(
                profile.DragBrakeResponse,
                Is.EqualTo(FidgetSpinnerMotion.DefaultDragBrakeResponse).Within(0.0001f));
            Assert.That(
                FidgetSpinnerMotion.ResistanceToCoastHalfLife(
                    FidgetSpinnerMotion.DefaultSpinResistance),
                Is.EqualTo(FidgetSpinnerMotion.DefaultCoastHalfLife).Within(0.0001f));
        }

        [Test]
        public void DragServo_SlowsFasterThanItAccelerates()
        {
            float accelerated = FidgetSpinnerMotion.FollowDragSpeed(
                0f,
                20f,
                1f / 60f,
                24f,
                60f,
                42f);
            float remainingAfterBrake = FidgetSpinnerMotion.FollowDragSpeed(
                20f,
                0f,
                1f / 60f,
                24f,
                60f,
                42f);

            Assert.That(20f - remainingAfterBrake, Is.GreaterThan(accelerated));
            Assert.That(
                FidgetSpinnerMotion.FollowDragSpeed(0f, 0f, 1f / 60f, 24f, 60f, 42f),
                Is.Zero,
                "The drag servo must never create motion from rest.");
        }

        [Test]
        public void ReleaseFling_RequiresDistanceTimeAndConsistentDirection()
        {
            Assert.That(
                FidgetSpinnerMotion.QualifiesReleaseFling(1400f, 18f, 18f, 0.04f),
                Is.False,
                "A tiny fast swipe must not become a persistent fling.");
            Assert.That(
                FidgetSpinnerMotion.QualifiesReleaseFling(900f, 20f, 90f, 0.2f),
                Is.False,
                "Back-and-forth travel must not qualify as a directional fling.");
            Assert.That(
                FidgetSpinnerMotion.QualifiesReleaseFling(900f, 82f, 90f, 0.2f),
                Is.True);
        }

        [Test]
        public void ReleaseFling_ReplacesRatherThanAddsToDragVelocity()
        {
            float fromSlowRotor = FidgetSpinnerMotion.ResolveReleaseAngularSpeed(
                3f, 900f, 82f, 90f, 0.2f, 0.65f, 30f, 1100f);
            float fromFastRotor = FidgetSpinnerMotion.ResolveReleaseAngularSpeed(
                25f, 900f, 82f, 90f, 0.2f, 0.65f, 30f, 1100f);
            float tinyGesture = FidgetSpinnerMotion.ResolveReleaseAngularSpeed(
                20f, 1400f, 18f, 18f, 0.04f, 1f, 42f, 720f);

            Assert.That(fromSlowRotor, Is.EqualTo(fromFastRotor).Within(0.0001f));
            Assert.That(fromSlowRotor, Is.LessThanOrEqualTo(30f));
            Assert.That(tinyGesture, Is.LessThan(2f));
        }

        [Test]
        public void DirectionReversal_RequiresIntentionalOppositeTravel()
        {
            Assert.That(
                FidgetSpinnerMotion.ConfirmsDirectionReversal(8f, -10f, 17.9f, 1.5f, 18f),
                Is.False);
            Assert.That(
                FidgetSpinnerMotion.ConfirmsDirectionReversal(8f, -10f, 18f, 1.5f, 18f),
                Is.True);
            Assert.That(
                FidgetSpinnerMotion.ConfirmsDirectionReversal(0.8f, -10f, 30f, 1.5f, 18f),
                Is.False);
        }

        [Test]
        public void ScreenTangentDirection_MatchesTheViewedPhysicalSpinAxis()
        {
            Assert.That(
                FidgetSpinnerMotion.AlignScreenTangentToSpinAxis(
                    12f,
                    Vector3.down,
                    Vector3.up),
                Is.EqualTo(-12f));
            Assert.That(
                FidgetSpinnerMotion.AlignScreenTangentToSpinAxis(
                    12f,
                    Vector3.up,
                    Vector3.up),
                Is.EqualTo(12f));
        }

        [Test]
        public void ResistanceMapping_IsInvertedClampedAndRoundTrips()
        {
            Assert.That(
                FidgetSpinnerMotion.ResistanceToCoastHalfLife(0f),
                Is.EqualTo(FidgetSpinnerMotion.MaximumCoastHalfLife));
            Assert.That(
                FidgetSpinnerMotion.ResistanceToCoastHalfLife(1f),
                Is.EqualTo(FidgetSpinnerMotion.MinimumCoastHalfLife).Within(0.0001f));
            Assert.That(FidgetSpinnerMotion.MinimumCoastHalfLife, Is.LessThan(0.3f));
            Assert.That(
                FidgetSpinnerMotion.ResistanceToCoastHalfLife(0.75f),
                Is.LessThan(FidgetSpinnerMotion.ResistanceToCoastHalfLife(0.25f)));

            float resistance = FidgetSpinnerMotion.CoastHalfLifeToResistance(5f);
            Assert.That(
                FidgetSpinnerMotion.ResistanceToCoastHalfLife(resistance),
                Is.EqualTo(5f).Within(0.0001f));
        }

        [TestCase(1.9f, 2f, false)]
        [TestCase(2f, 2f, true)]
        [TestCase(-2.5f, 2f, true)]
        public void MagneticBreakaway_UsesAbsoluteFingerVelocity(
            float requested,
            float threshold,
            bool expected)
        {
            Assert.That(
                FidgetSpinnerMotion.BreaksMagneticDetent(requested, threshold),
                Is.EqualTo(expected));
        }

        [Test]
        public void NearestDetent_SnapsToConfiguredSegment()
        {
            Assert.That(
                FidgetSpinnerMotion.NearestDetentDegrees(22f, 24),
                Is.EqualTo(15f).Within(0.0001f));
        }

        [TestCase(7.4f, 24, 0)]
        [TestCase(7.6f, 24, 1)]
        [TestCase(-7.6f, 24, -1)]
        [TestCase(367.6f, 24, 25)]
        public void DetentIndex_UsesUnwrappedMechanicalAngle(
            float angle,
            int detents,
            int expected)
        {
            Assert.That(
                FidgetSpinnerMotion.DetentIndex(angle, detents),
                Is.EqualTo(expected));
        }

        [Test]
        public void RatchetAudioVolume_IsFullAtSlowSpeedAndFallsAtHighSpeed()
        {
            float slow = RatchetAudioPhysicsModel.ResolveVolume(0f, 0f, -1);
            float medium = RatchetAudioPhysicsModel.ResolveVolume(0.5f, 0f, -1);
            float fast = RatchetAudioPhysicsModel.ResolveVolume(1f, 0f, -1);
            float forceEmphasized = RatchetAudioPhysicsModel.ResolveVolume(1f, 1f, 0);

            Assert.That(slow, Is.EqualTo(1f));
            Assert.That(medium, Is.LessThan(slow));
            Assert.That(fast, Is.EqualTo(RatchetAudioPhysicsModel.HighSpeedVolumeGain));
            Assert.That(forceEmphasized, Is.GreaterThan(fast));
            Assert.That(
                RatchetAudioPhysicsModel.ResolveVolume(1f, 1f, 4),
                Is.LessThan(forceEmphasized));
            Assert.That(
                RatchetAudioPhysicsModel.ResolveVolume(1f, 1f, 5),
                Is.EqualTo(fast));
        }

        [Test]
        public void RatchetAudioVariants_RoundRobinWithoutImmediateRepeat()
        {
            int previous = -1;
            for (int click = 0; click < 15; click++)
            {
                int next = RatchetAudioPhysicsModel.NextVariantIndex(5, previous);
                Assert.That(next, Is.Not.EqualTo(previous));
                Assert.That(next, Is.EqualTo(click % 5));
                previous = next;
            }
        }

        [Test]
        public void RatchetAudioPitch_UsesRandomOneToTwoSemitonesPlusSpeedRise()
        {
            uint slowState = 0x12345678u;
            uint fastState = slowState;
            for (int click = 0; click < 32; click++)
            {
                float slow = RatchetAudioPhysicsModel.ResolvePitchSemitones(
                    0f,
                    ref slowState);
                float fast = RatchetAudioPhysicsModel.ResolvePitchSemitones(
                    1f,
                    ref fastState);

                Assert.That(Mathf.Abs(slow), Is.InRange(1f, 2f));
                Assert.That(fast - slow, Is.InRange(0f, 1f));
                Assert.That(
                    RatchetAudioPhysicsModel.SemitonesToPitch(fast),
                    Is.GreaterThan(0f));
            }
        }

        [TestCase(0, 0, 0)]
        [TestCase(2, 5, 3)]
        [TestCase(5, 2, 3)]
        [TestCase(-3, 2, 5)]
        public void RatchetAudioCrossings_CountEveryDetentInEitherDirection(
            int previousIndex,
            int currentIndex,
            int expected)
        {
            Assert.That(
                RatchetAudioPhysicsModel.CrossedDetentCount(
                    previousIndex,
                    currentIndex),
                Is.EqualTo(expected));
        }

        [Test]
        public void ProductRhythm_ChangesCadenceWithoutReplacingRecipeIdentity()
        {
            FidgetHapticSettings single = new FidgetHapticSettings(
                true,
                0.72f,
                0.68f,
                FidgetHapticRhythm.Single,
                0.65f,
                24);
            FidgetHapticSettings burst = new FidgetHapticSettings(
                true,
                0.72f,
                0.68f,
                FidgetHapticRhythm.Burst,
                0.65f,
                24);

            HapticRecipe singleTick = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.DetentCrossed,
                0.5f,
                single);
            HapticRecipe burstTick = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.DetentCrossed,
                0.5f,
                burst);
            HapticRecipe pop = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.Pop,
                0.5f,
                burst);

            Assert.That(singleTick.SemanticEvent, Is.EqualTo(FidgetSemanticEvent.DetentCrossed));
            Assert.That(burstTick.SemanticEvent, Is.EqualTo(FidgetSemanticEvent.DetentCrossed));
            Assert.That(singleTick.PulseCount, Is.EqualTo(1));
            Assert.That(
                burstTick.PulseCount,
                Is.EqualTo(1),
                "Detents stay one isolated transient regardless of product rhythm.");
            Assert.That(pop.PulseCount, Is.EqualTo(2), "Pop keeps its dedicated two-stage membrane recipe.");
        }

        [Test]
        public void SpeedFollow_OnlyModulatesMappedMechanicalEvents()
        {
            FidgetHapticSettings settings = new FidgetHapticSettings(
                true,
                1f,
                0.5f,
                FidgetHapticRhythm.Single,
                1f,
                24);

            HapticRecipe slow = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.DetentCrossed,
                0f,
                settings);
            HapticRecipe fast = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.DetentCrossed,
                1f,
                settings);
            HapticRecipe resetSlow = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.Reset,
                0f,
                settings);
            HapticRecipe resetFast = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.Reset,
                1f,
                settings);

            Assert.That(
                fast.Intensity,
                Is.EqualTo(slow.Intensity),
                "Discrete preset intensity stays exact below the blur transition.");
            Assert.That(resetFast.Intensity, Is.EqualTo(resetSlow.Intensity).Within(0.0001f));

            FidgetHapticSettings noFollow = new FidgetHapticSettings(
                true,
                1f,
                0.5f,
                FidgetHapticRhythm.Single,
                0f,
                24);
            HapticRecipe noFollowSlow = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.DetentCrossed,
                0f,
                noFollow);
            HapticRecipe noFollowFast = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.DetentCrossed,
                1f,
                noFollow);
            Assert.That(
                noFollowFast.Intensity,
                Is.EqualTo(noFollowSlow.Intensity).Within(0.0001f));
        }

        [Test]
        public void RecommendedMechanicalRecipesAreStrongAndKeepSemanticIdentity()
        {
            HapticRecipe tick = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.DetentCrossed,
                1f,
                FidgetHapticSettings.Recommended);
            HapticRecipe capture = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.DetentCaptured,
                1f,
                FidgetHapticSettings.Recommended);

            Assert.That(tick.SemanticEvent, Is.EqualTo(FidgetSemanticEvent.DetentCrossed));
            Assert.That(tick.Waveform, Is.EqualTo(FidgetHapticWaveform.Transient));
            Assert.That(tick.Intensity, Is.EqualTo(1f));
            Assert.That(tick.Sharpness, Is.EqualTo(0.72f));
            Assert.That(tick.ImpactLayers, Is.EqualTo(1f));
            Assert.That(capture.SemanticEvent, Is.EqualTo(FidgetSemanticEvent.DetentCaptured));
            Assert.That(capture.Waveform, Is.EqualTo(FidgetHapticWaveform.Hybrid));
            Assert.That(capture.PulseCount, Is.EqualTo(2));
            Assert.That(capture.Intensity, Is.GreaterThan(0.85f));
        }

        [Test]
        public void RecipeOverrideExposesCompleteHapticParameterSurface()
        {
            FidgetHapticRecipeLibrary.SetOverride(
                FidgetSemanticEvent.Selection,
                new HapticRecipeOverride(
                    FidgetHapticWaveform.Continuous,
                    0.81f,
                    0.73f,
                    0.22f,
                    0.11f,
                    0.31f,
                    0.19f,
                    true,
                    0.42f,
                    0.37f,
                    4,
                    0.052f,
                    2.25f,
                    0.91f,
                    -0.21f,
                    0.17f,
                    -0.33f,
                    0.44f));

            HapticRecipe recipe = FidgetHapticRecipeLibrary.Resolve(
                FidgetSemanticEvent.Selection,
                0f,
                new FidgetHapticSettings(
                    true,
                    1f,
                    0.5f,
                    FidgetHapticRhythm.Single,
                    0f,
                    24));

            Assert.That(recipe.SemanticEvent, Is.EqualTo(FidgetSemanticEvent.Selection));
            Assert.That(recipe.Waveform, Is.EqualTo(FidgetHapticWaveform.Continuous));
            Assert.That(recipe.Intensity, Is.EqualTo(0.81f).Within(0.0001f));
            Assert.That(recipe.Sharpness, Is.EqualTo(0.73f).Within(0.0001f));
            Assert.That(recipe.Duration, Is.EqualTo(0.22f).Within(0.0001f));
            Assert.That(recipe.Attack, Is.EqualTo(0.11f).Within(0.0001f));
            Assert.That(recipe.Decay, Is.EqualTo(0.31f).Within(0.0001f));
            Assert.That(recipe.Release, Is.EqualTo(0.19f).Within(0.0001f));
            Assert.That(recipe.Sustained, Is.True);
            Assert.That(recipe.EndIntensity, Is.EqualTo(0.42f).Within(0.0001f));
            Assert.That(recipe.EndSharpness, Is.EqualTo(0.37f).Within(0.0001f));
            Assert.That(recipe.PulseCount, Is.EqualTo(4));
            Assert.That(recipe.PulseInterval, Is.EqualTo(0.052f).Within(0.0001f));
            Assert.That(recipe.ImpactLayers, Is.EqualTo(2.25f).Within(0.0001f));
            Assert.That(recipe.DynamicIntensity, Is.EqualTo(0.91f).Within(0.0001f));
            Assert.That(recipe.DynamicSharpness, Is.EqualTo(-0.21f).Within(0.0001f));
            Assert.That(recipe.DynamicAttack, Is.EqualTo(0.17f).Within(0.0001f));
            Assert.That(recipe.DynamicDecay, Is.EqualTo(-0.33f).Within(0.0001f));
            Assert.That(recipe.DynamicRelease, Is.EqualTo(0.44f).Within(0.0001f));
        }

        [TestCase(FidgetRatchetFeel.Freewheel, SpinnerResistanceMode.Freewheel, 2.2f, 1.2f, 16f)]
        [TestCase(FidgetRatchetFeel.Light, SpinnerResistanceMode.MagneticDetent, 1.4f, 0.8f, 10f)]
        [TestCase(FidgetRatchetFeel.Mechanical, SpinnerResistanceMode.MagneticDetent, 2.2f, 1.2f, 16f)]
        [TestCase(FidgetRatchetFeel.Heavy, SpinnerResistanceMode.MagneticDetent, 3.4f, 1.6f, 24f)]
        public void RatchetFeel_MapsOneProductChoiceToCoherentMechanics(
            FidgetRatchetFeel feel,
            SpinnerResistanceMode expectedMode,
            float expectedBreakaway,
            float expectedCapture,
            float expectedSnap)
        {
            FidgetAppCoordinator.ResolveRatchetFeel(
                feel,
                out SpinnerResistanceMode mode,
                out float breakaway,
                out float capture,
                out float snap);

            Assert.That(mode, Is.EqualTo(expectedMode));
            Assert.That(breakaway, Is.EqualTo(expectedBreakaway).Within(0.0001f));
            Assert.That(capture, Is.EqualTo(expectedCapture).Within(0.0001f));
            Assert.That(snap, Is.EqualTo(expectedSnap).Within(0.0001f));
        }

        [Test]
        public void ShakeDetector_RequiresJerkAndRearmsAfterCooldownAndHysteresis()
        {
            FidgetShakeDetector detector = new FidgetShakeDetector();

            for (int i = 1; i <= 12; i++)
            {
                Assert.That(
                    detector.Update(new Vector3(i * 0.1f, 0f, 0f), 0.1f, out _),
                    Is.False,
                    "Slow movement must not trigger a shake.");
            }

            Assert.That(detector.Update(new Vector3(2.2f, 0f, 0f), 1f / 60f, out _), Is.False);
            Assert.That(
                detector.Update(new Vector3(2.2f, 0f, 0f), 1f / 60f, out float strength),
                Is.True);
            Assert.That(strength, Is.InRange(0f, 1f));
            Assert.That(detector.Update(new Vector3(2.2f, 0f, 0f), 1f / 60f, out _), Is.False);

            for (int i = 0; i < 10; i++)
            {
                detector.Update(Vector3.zero, 1f / 60f, out _);
            }
            Assert.That(detector.Armed, Is.True);
        }

        [Test]
        public void InertiaHaptic_UsesPointThreeGThresholdHysteresisAndEightHertzLimit()
        {
            var detector = new FidgetInertiaHapticDetector();

            Assert.That(
                detector.Update(new Vector3(0.29f, 0f, 0f), 1f / 60f, out _),
                Is.False);
            Assert.That(
                detector.Update(new Vector3(0.30f, 0f, 0f), 1f / 60f, out float low),
                Is.True);
            Assert.That(low, Is.EqualTo(0f).Within(0.0001f));

            for (int index = 0; index < 7; index++)
            {
                Assert.That(
                    detector.Update(new Vector3(1.5f, 0f, 0f), 1f / 60f, out _),
                    Is.False);
            }
            Assert.That(
                detector.Update(new Vector3(1.5f, 0f, 0f), 1f / 60f, out float high),
                Is.True);
            Assert.That(high, Is.EqualTo(1f).Within(0.0001f));

            detector.Update(new Vector3(0.24f, 0f, 0f), 0.2f, out _);
            Assert.That(detector.Active, Is.True);
            detector.Update(new Vector3(0.21f, 0f, 0f), 1f / 60f, out _);
            Assert.That(detector.Active, Is.False);
        }
    }
}
