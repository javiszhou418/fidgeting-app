using CodexUnityLab;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class HapticSpeedTextureTests
    {
        [Test]
        public void DetentRateUsesActualAngularSpeedAndSharedDetentCount()
        {
            float angularSpeed = 2f * Mathf.PI;

            Assert.That(
                HapticSpeedTextureStateMachine.DetentsPerSecond(angularSpeed, 24),
                Is.EqualTo(24f).Within(0.0001f));
            Assert.That(
                HapticSpeedTextureStateMachine.DetentsPerSecond(-angularSpeed, 24),
                Is.EqualTo(24f).Within(0.0001f));
        }

        [Test]
        public void RestCanNeverStartContinuousOutput()
        {
            var machine = new HapticSpeedTextureStateMachine();

            HapticSpeedTextureSample sample = machine.Step(
                0f,
                24,
                0,
                true,
                HapticSpeedTextureProfile.Recommended);

            Assert.That(sample.Band, Is.EqualTo(HapticSpeedTextureBand.Rest));
            Assert.That(sample.Action, Is.EqualTo(HapticSpeedTextureAction.None));
            Assert.That(machine.ContinuousActive, Is.False);
        }

        [Test]
        public void ContinuousCrossoverUsesHysteresisWithoutBoundaryChatter()
        {
            var machine = new HapticSpeedTextureStateMachine();
            HapticSpeedTextureProfile profile = HapticSpeedTextureProfile.Recommended;

            HapticSpeedTextureSample entered = machine.Step(8f, 24, 0, true, profile);
            HapticSpeedTextureSample stayed = machine.Step(7.5f, 24, 0.04, true, profile);
            HapticSpeedTextureSample exited = machine.Step(7f, 24, 0.08, true, profile);

            Assert.That(entered.DetentsPerSecond, Is.GreaterThan(30f));
            Assert.That(entered.Action, Is.EqualTo(HapticSpeedTextureAction.StartContinuous));
            Assert.That(stayed.DetentsPerSecond, Is.InRange(27f, 30f));
            Assert.That(stayed.Band, Is.EqualTo(HapticSpeedTextureBand.BearingContinuous));
            Assert.That(stayed.SuppressDetentTransients, Is.False);
            Assert.That(stayed.ContinuousIntensity, Is.LessThanOrEqualTo(0.05f));
            Assert.That(exited.DetentsPerSecond, Is.LessThan(27f));
            Assert.That(exited.Action, Is.EqualTo(HapticSpeedTextureAction.StopContinuous));
            Assert.That(machine.ContinuousActive, Is.False);
        }

        [Test]
        public void ContinuousUpdatesAreThrottledToConfiguredRate()
        {
            var machine = new HapticSpeedTextureStateMachine();
            HapticSpeedTextureProfile profile = HapticSpeedTextureProfile.Recommended;

            Assert.That(
                machine.Step(8f, 24, 0, true, profile).Action,
                Is.EqualTo(HapticSpeedTextureAction.StartContinuous));
            Assert.That(
                machine.Step(8f, 24, 0.02, true, profile).Action,
                Is.EqualTo(HapticSpeedTextureAction.None));
            Assert.That(
                machine.Step(8f, 24, 0.034, true, profile).Action,
                Is.EqualTo(HapticSpeedTextureAction.UpdateContinuous));
        }

        [Test]
        public void DiscreteDetentsKeepExactPresetStrengthUntilBlurThreshold()
        {
            var lowMachine = new HapticSpeedTextureStateMachine();
            var highMachine = new HapticSpeedTextureStateMachine();
            HapticSpeedTextureProfile profile = HapticSpeedTextureProfile.Recommended;

            HapticSpeedTextureSample low = lowMachine.Step(1f, 24, 0, true, profile);
            HapticSpeedTextureSample high = highMachine.Step(7f, 24, 0, true, profile);

            Assert.That(low.DetentIntensityGain, Is.EqualTo(1f));
            Assert.That(high.DetentIntensityGain, Is.EqualTo(1f));
            Assert.That(low.SuppressDetentTransients, Is.False);
            Assert.That(high.SuppressDetentTransients, Is.False);
        }

        [Test]
        public void DisallowedOutputStopsAnActiveContinuousTexture()
        {
            var machine = new HapticSpeedTextureStateMachine();
            HapticSpeedTextureProfile profile = HapticSpeedTextureProfile.Recommended;
            machine.Step(8f, 24, 0, true, profile);

            HapticSpeedTextureSample stopped = machine.Step(8f, 24, 0.1, false, profile);

            Assert.That(stopped.Action, Is.EqualTo(HapticSpeedTextureAction.StopContinuous));
            Assert.That(stopped.SuppressDetentTransients, Is.False);
        }

        [Test]
        public void ProfileRejectsNonFiniteAndInvalidRanges()
        {
            var profile = new HapticSpeedTextureProfile(
                true,
                float.NaN,
                float.PositiveInfinity,
                float.NaN,
                -1f,
                2f,
                0.4f,
                0.1f,
                0.8f,
                0.2f,
                float.NaN,
                100f,
                -2f,
                4f);

            Assert.That(profile.EnterContinuousDetentsPerSecond, Is.EqualTo(30f));
            Assert.That(profile.ExitContinuousDetentsPerSecond, Is.EqualTo(27f));
            Assert.That(
                profile.FullScaleAngularSpeed,
                Is.EqualTo(
                    global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed));
            Assert.That(profile.SlowDetentIntensityGain, Is.EqualTo(0f));
            Assert.That(profile.FastDetentIntensityGain, Is.EqualTo(1f));
            Assert.That(profile.MinimumContinuousIntensity, Is.EqualTo(0.1f));
            Assert.That(profile.MaximumContinuousIntensity, Is.EqualTo(0.4f));
            Assert.That(profile.MinimumContinuousSharpness, Is.EqualTo(0.2f));
            Assert.That(profile.MaximumContinuousSharpness, Is.EqualTo(0.8f));
            Assert.That(profile.UpdateRateHz, Is.EqualTo(60f));
            Assert.That(profile.Attack, Is.EqualTo(0f));
            Assert.That(profile.ReleaseSeconds, Is.EqualTo(1f));
        }

        [Test]
        public void FourDetentPresetsMatchProductTableExactly()
        {
            Assert.That(DetentFeelPresetCatalog.Count, Is.EqualTo(4));
            AssertPreset(0, "Vault", 8, 1f, 0.55f, 45f);
            AssertPreset(1, "Camera Dial", 12, 1f, 0.72f, 30f);
            AssertPreset(2, "Watch Bezel", 24, 0.85f, 0.90f, 15f);
            AssertPreset(3, "Silk Ratchet", 36, 0.60f, 1f, 10f);
        }

        [Test]
        public void PresetOverrideChangesOnlyIntensityAndSharpnessAndClamps()
        {
            try
            {
                DetentFeelRuntime.SelectPreset(0);
                DetentFeelRuntime.OverrideIntensity(2f);
                DetentFeelRuntime.OverrideSharpness(-1f);

                Assert.That(
                    DetentFeelRuntime.ActiveConfig.DetentsPerRevolution,
                    Is.EqualTo(8));
                Assert.That(DetentFeelRuntime.ActiveConfig.Intensity, Is.EqualTo(1f));
                Assert.That(DetentFeelRuntime.ActiveConfig.Sharpness, Is.EqualTo(0f));
            }
            finally
            {
                DetentFeelRuntime.ResetToDefault();
            }
        }

        [Test]
        public void ContinuousBlurUsesPresetValuesAndDenserPresetEntersEarlier()
        {
            HapticSpeedTextureProfile profile = HapticSpeedTextureProfile.Recommended;
            DetentFeelConfig vault = DetentFeelPresetCatalog.Get(0).Config;
            DetentFeelConfig silk = DetentFeelPresetCatalog.Get(3).Config;
            float vaultThresholdSpeed = 30f * 2f * Mathf.PI / vault.DetentsPerRevolution;
            float silkThresholdSpeed = 30f * 2f * Mathf.PI / silk.DetentsPerRevolution;

            Assert.That(silkThresholdSpeed, Is.LessThan(vaultThresholdSpeed));

            var machine = new HapticSpeedTextureStateMachine();
            float speed = silkThresholdSpeed + 0.1f;
            HapticSpeedTextureSample sample = machine.Step(
                speed,
                silk.DetentsPerRevolution,
                0,
                true,
                profile,
                silk);

            Assert.That(sample.Action, Is.EqualTo(HapticSpeedTextureAction.StartContinuous));
            Assert.That(sample.SuppressDetentTransients, Is.True);
            Assert.That(sample.ContinuousSharpness, Is.EqualTo(silk.Sharpness));
            Assert.That(
                sample.ContinuousIntensity,
                Is.EqualTo(
                    Mathf.Clamp01(speed / profile.FullScaleAngularSpeed)
                    * silk.Intensity).Within(0.0001f));
        }

        private static void AssertPreset(
            int index,
            string name,
            int detents,
            float intensity,
            float sharpness,
            float spacing)
        {
            DetentFeelPreset preset = DetentFeelPresetCatalog.Get(index);
            Assert.That(preset.Name, Is.EqualTo(name));
            Assert.That(preset.Config.DetentsPerRevolution, Is.EqualTo(detents));
            Assert.That(preset.Config.Intensity, Is.EqualTo(intensity));
            Assert.That(preset.Config.Sharpness, Is.EqualTo(sharpness));
            Assert.That(preset.Config.SpacingDegrees, Is.EqualTo(spacing));
        }
    }
}
