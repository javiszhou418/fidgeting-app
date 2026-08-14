using System.IO;
using System.Linq;
using NUnit.Framework;
using ThreeBladeEDC.Interaction;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ThreeBladeEDC.Tests.Editor
{
    public sealed class RotorWindAudioTests
    {
        private SceneSetup[] _previousSceneSetup;

        [SetUp]
        public void CaptureSceneSetup()
        {
            _previousSceneSetup = EditorSceneManager.GetSceneManagerSetup();
        }

        [TearDown]
        public void RestoreSceneSetup()
        {
            if (_previousSceneSetup != null
                && _previousSceneSetup.Any(setup => setup.isLoaded))
            {
                EditorSceneManager.RestoreSceneManagerSetup(_previousSceneSetup);
            }
            else
            {
                EditorSceneManager.NewScene(
                    NewSceneSetup.EmptyScene,
                    NewSceneMode.Single);
            }
        }

        [Test]
        public void WindModel_IsSilentAtRestAndBelowAudibleThreshold()
        {
            RotorWindAudioFrame stopped = RotorWindAudioModel.Evaluate(0f, 3);
            RotorWindAudioFrame barelyMoving = RotorWindAudioModel.Evaluate(
                RotorWindAudioModel.AudibleThresholdRadians * 0.9f,
                3);

            Assert.That(stopped.IsAudible, Is.False);
            Assert.That(stopped.Gain, Is.Zero);
            Assert.That(barelyMoving.IsAudible, Is.False);
            Assert.That(barelyMoving.Gain, Is.Zero);
        }

        [Test]
        public void WindModel_GrowsWithMeasuredSpeedAndUsesRaisedMasterVolume()
        {
            RotorWindAudioFrame slow = RotorWindAudioModel.Evaluate(3f, 3);
            RotorWindAudioFrame medium = RotorWindAudioModel.Evaluate(12f, 3);
            RotorWindAudioFrame fast = RotorWindAudioModel.Evaluate(
                RotorWindAudioModel.FullScaleAngularSpeed,
                3);

            Assert.That(slow.Gain, Is.GreaterThan(0f));
            Assert.That(medium.Gain, Is.GreaterThan(slow.Gain));
            Assert.That(fast.Gain, Is.GreaterThan(medium.Gain));
            Assert.That(
                fast.Gain,
                Is.EqualTo(RotorWindAudioModel.DefaultMasterVolume).Within(0.0001f));
            Assert.That(RotorWindAudioModel.DefaultMasterVolume, Is.EqualTo(0.50f));
        }

        [Test]
        public void WindModel_IsClearlyAudibleAcrossRealisticSubFourHundredRpmPlay()
        {
            float RadiansPerSecond(float rpm) => rpm * Mathf.PI * 2f / 60f;
            RotorWindAudioFrame sixty = RotorWindAudioModel.Evaluate(
                RadiansPerSecond(60f),
                3);
            RotorWindAudioFrame oneTwenty = RotorWindAudioModel.Evaluate(
                RadiansPerSecond(120f),
                3);
            RotorWindAudioFrame twoFifty = RotorWindAudioModel.Evaluate(
                RadiansPerSecond(250f),
                3);
            RotorWindAudioFrame fourHundred = RotorWindAudioModel.Evaluate(
                RadiansPerSecond(400f),
                3);

            Assert.That(RotorWindAudioModel.GainCurveExponent, Is.EqualTo(0.62f));
            Assert.That(sixty.Gain, Is.GreaterThan(0.15f));
            Assert.That(oneTwenty.Gain, Is.GreaterThan(sixty.Gain));
            Assert.That(twoFifty.Gain, Is.GreaterThan(oneTwenty.Gain));
            Assert.That(
                fourHundred.Gain,
                Is.EqualTo(RotorWindAudioModel.DefaultMasterVolume)
                    .Within(0.0001f));
        }

        [Test]
        public void WindModel_MetalCadenceAndPitchBothFollowMeasuredSpeed()
        {
            float RadiansPerSecond(float rpm) => rpm * Mathf.PI * 2f / 60f;
            RotorWindAudioFrame oneTwenty = RotorWindAudioModel.Evaluate(
                RadiansPerSecond(120f),
                3);
            RotorWindAudioFrame twoFifty = RotorWindAudioModel.Evaluate(
                RadiansPerSecond(250f),
                3);
            RotorWindAudioFrame fourHundred = RotorWindAudioModel.Evaluate(
                RadiansPerSecond(400f),
                3);

            Assert.That(oneTwenty.BladePassFrequency, Is.EqualTo(6f).Within(0.0001f));
            Assert.That(fourHundred.BladePassFrequency, Is.EqualTo(20f).Within(0.0001f));
            Assert.That(twoFifty.BladePassFrequency, Is.EqualTo(12.5f).Within(0.0001f));
            Assert.That(twoFifty.PrimaryResonance, Is.EqualTo(1588f).Within(2f));
            Assert.That(twoFifty.SecondaryResonance, Is.EqualTo(3651f).Within(2f));
            Assert.That(twoFifty.UpperAlloyResonance, Is.EqualTo(6588f).Within(2f));
            Assert.That(fourHundred.PrimaryResonance, Is.EqualTo(1810f).Within(2f));
            Assert.That(fourHundred.SecondaryResonance, Is.EqualTo(4161f).Within(2f));
            Assert.That(fourHundred.UpperAlloyResonance, Is.EqualTo(7508f).Within(2f));
            Assert.That(
                fourHundred.PrimaryResonance / oneTwenty.PrimaryResonance,
                Is.GreaterThan(1.20f),
                "Metal pitch must rise audibly with RPM, not only repeat more often.");
            Assert.That(fourHundred.SecondaryResonance, Is.GreaterThan(oneTwenty.SecondaryResonance));
            Assert.That(fourHundred.UpperAlloyResonance, Is.GreaterThan(oneTwenty.UpperAlloyResonance));
            Assert.That(RotorWindAudioModel.ResonancePitchTrackingExponent, Is.EqualTo(0.78f));
            Assert.That(RotorWindAudioModel.FinalMetalPitchSemitones, Is.EqualTo(9f));
        }

        [Test]
        public void WindModel_UsesLowNoiseBladeFocusedSpectrumAndFastResponse()
        {
            RotorWindAudioFrame fast = RotorWindAudioModel.Evaluate(
                RotorWindAudioModel.FullScaleAngularSpeed,
                3);

            Assert.That(RotorWindAudioModel.BodyNoiseMix, Is.GreaterThan(0.8f));
            Assert.That(RotorWindAudioModel.MidNoiseMix, Is.LessThanOrEqualTo(0.14f));
            Assert.That(RotorWindAudioModel.EdgeNoiseMix, Is.LessThanOrEqualTo(0.02f));
            Assert.That(
                RotorWindAudioModel.PrimaryResonanceMix
                    + RotorWindAudioModel.SecondaryResonanceMix,
                Is.GreaterThanOrEqualTo(0.18f),
                "The alloy resonance must remain audible under the low-noise wind bed.");
            Assert.That(
                RotorWindAudioModel.MetalStrikeNoiseMix,
                Is.GreaterThanOrEqualTo(0.20f),
                "A short upper-band strike supplies the crisp collision attack.");
            Assert.That(
                RotorWindAudioModel.UpperAlloyResonanceMix,
                Is.InRange(0.15f, 0.17f),
                "The selected bright-alloy profile needs an audible upper mode.");
            Assert.That(RotorWindAudioModel.PrimaryResonanceMix, Is.EqualTo(0.105f));
            Assert.That(RotorWindAudioModel.SecondaryResonanceMix, Is.EqualTo(0.215f));
            Assert.That(RotorWindAudioModel.MetalStrikeNoiseMix, Is.EqualTo(0.34f));
            Assert.That(
                RotorWindAudioModel.ResolveBrightAlloyTriangle(
                    Mathf.PI * 0.5f,
                    1800f,
                    48000f),
                Is.EqualTo(1f).Within(0.0001f));
            Assert.That(
                RotorWindAudioModel.ResolveBrightAlloyTriangle(
                    Mathf.PI * 0.25f,
                    8000f,
                    44100f),
                Is.EqualTo(Mathf.Sin(Mathf.PI * 0.25f)).Within(0.0001f),
                "The +9-semitone upper mode must drop its third harmonic near Nyquist.");
            Assert.That(RotorWindAudioModel.ParameterSmoothingSeconds, Is.LessThanOrEqualTo(0.004f));
            Assert.That(fast.BodyCutoff, Is.LessThanOrEqualTo(800f));
            Assert.That(fast.MidBandCenter, Is.LessThanOrEqualTo(1500f));
            Assert.That(fast.EdgeCutoff, Is.GreaterThanOrEqualTo(5000f));
        }

        [Test]
        public void MetalResonance_IsShortBladePulseInsteadOfContinuousHum()
        {
            string windSource = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_Fidgeting/Runtime/Interaction/RotorWindAudio.cs"));
            Assert.That(RotorWindAudioModel.ResolveMetalPulse(0f), Is.EqualTo(1f));
            Assert.That(
                RotorWindAudioModel.ResolveMetalPulse(
                    Mathf.PI * 2f * RotorWindAudioModel.MetalPulseDutyCycle * 0.5f),
                Is.EqualTo(0.125f).Within(0.0001f));
            Assert.That(RotorWindAudioModel.ResolveMetalPulse(Mathf.PI), Is.Zero);

            const int sampleCount = 360;
            int activeSamples = Enumerable.Range(0, sampleCount)
                .Count(index => RotorWindAudioModel.ResolveMetalPulse(
                    index * Mathf.PI * 2f / sampleCount) > 0f);

            Assert.That(RotorWindAudioModel.MetalPulseDutyCycle, Is.EqualTo(0.14f));
            Assert.That(
                RotorWindAudioModel.SecondaryResonanceMix,
                Is.GreaterThan(RotorWindAudioModel.PrimaryResonanceMix),
                "The short upper alloy mode must lead the crisp collision identity.");
            Assert.That(
                activeSamples / (float)sampleCount,
                Is.LessThan(0.16f),
                "The alloy layer must ring briefly per blade, not hum continuously.");
            const float lowSpeedBladePassHz = 6f;
            const float highSpeedBladePassHz = 20f;
            Assert.That(RotorWindAudioModel.ResolveMetalRing(0f, lowSpeedBladePassHz), Is.Zero);
            Assert.That(
                RotorWindAudioModel.ResolveMetalRing(
                    Mathf.PI * 2f * lowSpeedBladePassHz
                        * RotorWindAudioModel.MetalRingAttackSeconds,
                    lowSpeedBladePassHz),
                Is.EqualTo(1f).Within(0.0001f));
            Assert.That(
                RotorWindAudioModel.ResolveMetalRing(
                    Mathf.PI * 2f * lowSpeedBladePassHz
                        * (RotorWindAudioModel.MetalRingMaximumSeconds + 0.001f),
                    lowSpeedBladePassHz),
                Is.Zero);
            int lowSpeedRingingSamples = Enumerable.Range(0, sampleCount)
                .Count(index => RotorWindAudioModel.ResolveMetalRing(
                    index * Mathf.PI * 2f / sampleCount,
                    lowSpeedBladePassHz) > 0f);
            Assert.That(
                lowSpeedRingingSamples / (float)sampleCount,
                Is.InRange(0.37f, 0.40f),
                "At 120 RPM the three-blade material body should last about 65 ms, not imply a large cavity.");
            int highSpeedRingingSamples = Enumerable.Range(0, sampleCount)
                .Count(index => RotorWindAudioModel.ResolveMetalRing(
                    index * Mathf.PI * 2f / sampleCount,
                    highSpeedBladePassHz) > 0f);
            Assert.That(
                highSpeedRingingSamples / (float)sampleCount,
                Is.InRange(0.65f, 0.73f),
                "At 400 RPM the ring must still finish before the next blade pass.");
            Assert.That(RotorWindAudioModel.MetalRingMaximumSeconds, Is.EqualTo(0.065f));
            StringAssert.Contains(
                "* (ringEnvelope * ringing + strikePulse * strike);",
                windSource,
                "One resonance amount must control every modal and strike component together.");
            StringAssert.DoesNotContain("brightAlloy", windSource);
        }

        [Test]
        public void WindRenderer_UsesMixerCallbackAndProjectUsesLowLatencyBuffer()
        {
            string windSource = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_Fidgeting/Runtime/Interaction/RotorWindAudio.cs"));
            string audioSettings = File.ReadAllText(Path.Combine(
                Directory.GetParent(Application.dataPath).FullName,
                "ProjectSettings/AudioManager.asset"));

            StringAssert.Contains("OnAudioFilterRead(float[] data, int channels)", windSource);
            StringAssert.Contains("_sampleRate,\n                    false);", windSource);
            StringAssert.DoesNotContain("FillAudioBuffer", windSource);
            StringAssert.Contains(
                $"m_DSPBufferSize: {RotorWindAudioModel.DspBufferSamples}",
                audioSettings);
        }

        [TestCase(2, 2f)]
        [TestCase(3, 3f)]
        [TestCase(4, 4f)]
        public void WindModel_BladePassRateMatchesPhysicalBladeCount(
            int bladeCount,
            float expectedFrequency)
        {
            RotorWindAudioFrame frame = RotorWindAudioModel.Evaluate(
                Mathf.PI * 2f,
                bladeCount);

            Assert.That(
                frame.BladePassFrequency,
                Is.EqualTo(expectedFrequency).Within(0.0001f));
            Assert.That(frame.PrimaryResonance, Is.InRange(1125f, 1810f));
            Assert.That(frame.SecondaryResonance, Is.InRange(2588f, 4161f));
            Assert.That(frame.UpperAlloyResonance, Is.InRange(4669f, 7508f));
            Assert.That(
                frame.SecondaryResonance / frame.PrimaryResonance,
                Is.GreaterThan(2.0f),
                "The upper alloy mode stays inharmonic without becoming shrill.");
        }

        [Test]
        public void SmoothModeHasWindOnlyAndRatchetModeLayersDetentClicks()
        {
            string windSource = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_Fidgeting/Runtime/Interaction/RotorWindAudio.cs"));
            string rotorSource = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_Fidgeting/Runtime/Interaction/RotorRigidbodyController.cs"));

            StringAssert.Contains("rotor.AngularSpeedRadians", windSource);
            StringAssert.Contains("rotor.ResetPerformed", windSource);
            StringAssert.DoesNotContain("SetSpinVelocity(", windSource);
            StringAssert.DoesNotContain("angularVelocity =", windSource);
            StringAssert.DoesNotContain("IosHaptics", windSource);
            StringAssert.Contains(
                "resistanceMode != global::ThreeBladeEDC.SpinnerResistanceMode.MagneticDetent",
                rotorSource);
            StringAssert.Contains("RatchetDetentCrossed?.Invoke", rotorSource);
        }

        [TestCase("Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity", 3)]
        [TestCase("Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity", 3)]
        [TestCase("Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity", 4)]
        [TestCase("Assets/_TwoLobeBar/Scenes/TwoLobeBar.unity", 2)]
        public void ShippingRotorScene_HasWindAndLayeredRatchetAudio(
            string scenePath,
            int expectedBladeCount)
        {
            Assert.That(
                AssetDatabase.LoadAssetAtPath<SceneAsset>(scenePath),
                Is.Not.Null,
                $"Missing shipping rotor scene: {scenePath}");
            Scene scene = EditorSceneManager.OpenScene(
                scenePath,
                OpenSceneMode.Single);
            RotorRigidbodyController rotor = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<RotorRigidbodyController>(true))
                .Single();
            RotorWindAudio[] winds = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<RotorWindAudio>(true))
                .ToArray();
            MetalRatchetDetentAudio[] ratchets = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<MetalRatchetDetentAudio>(true))
                .ToArray();

            Assert.That(winds, Has.Length.EqualTo(1));
            Assert.That(winds[0].Rotor, Is.SameAs(rotor));
            Assert.That(winds[0].BladeCount, Is.EqualTo(expectedBladeCount));
            Assert.That(
                winds[0].AlloyResonance,
                Is.EqualTo(RotorWindAudioModel.DefaultAlloyResonance).Within(0.0001f));
            Assert.That(
                winds[0].MasterVolume,
                Is.EqualTo(RotorWindAudioModel.DefaultMasterVolume).Within(0.0001f));
            AudioSource windSource = winds[0].GetComponent<AudioSource>();
            Assert.That(windSource, Is.Not.Null);
            Assert.That(windSource.playOnAwake, Is.False);
            Assert.That(windSource.loop, Is.True);

            Assert.That(ratchets, Has.Length.EqualTo(1));
            Assert.That(ratchets[0].Rotor, Is.SameAs(rotor));
            Assert.That(ratchets[0].ClickVariants, Has.Length.EqualTo(5));
            Assert.That(ratchets[0].Voices, Has.Length.EqualTo(12));
            Assert.That(ratchets[0].ClickVariants, Has.None.Null);
            Assert.That(ratchets[0].Voices, Has.None.Null);
        }
    }
}
