using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.DisplayCase.Candidates.Tests
{
    public sealed class PackOpeningEpicTimingProfileTests
    {
        private PackOpeningEpicTimingProfile profile;

        [SetUp]
        public void SetUp()
        {
            profile = ScriptableObject.CreateInstance<PackOpeningEpicTimingProfile>();
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(profile);
        }

        [TestCase(0.00f, PackOpeningEpicPhase.Handoff)]
        [TestCase(0.35f, PackOpeningEpicPhase.Anticipation)]
        [TestCase(0.65f, PackOpeningEpicPhase.Resistance)]
        [TestCase(0.95f, PackOpeningEpicPhase.Snap)]
        [TestCase(1.00f, PackOpeningEpicPhase.Tear)]
        [TestCase(1.75f, PackOpeningEpicPhase.Impact)]
        [TestCase(1.93f, PackOpeningEpicPhase.Reveal)]
        [TestCase(2.53f, PackOpeningEpicPhase.NativeSettle)]
        [TestCase(3.10f, PackOpeningEpicPhase.Complete)]
        public void Evaluate_UsesAcceptanceTimeline(
            float elapsed,
            PackOpeningEpicPhase expected)
        {
            Assert.That(profile.Evaluate(elapsed).Phase, Is.EqualTo(expected));
        }

        [Test]
        public void Evaluate_UsesOneSettlingCaseRotation()
        {
            Assert.That(
                profile.Evaluate(PackOpeningEpicTimingProfile.ImpactEnd)
                    .CaseRotationDegrees,
                Is.EqualTo(PackOpeningEpicTimingProfile.StartCaseRotationDegrees)
                    .Within(0.001f));
            Assert.That(
                profile.Evaluate(PackOpeningEpicTimingProfile.RevealEnd)
                    .CaseRotationDegrees,
                Is.EqualTo(0f).Within(0.001f));
        }

        [Test]
        public void Evaluate_StagesNativeInformationBeforeCta()
        {
            PackOpeningEpicSample sample = profile.Evaluate(2.83f);

            Assert.That(sample.Title, Is.EqualTo(1f).Within(0.001f));
            Assert.That(sample.Chip, Is.GreaterThan(0f));
            Assert.That(sample.Info, Is.GreaterThan(0f));
            Assert.That(sample.Cta, Is.EqualTo(0f));
        }

        [Test]
        public void Evaluate_ReduceMotionKeepsCausalityWithoutSensoryEffects()
        {
            PackOpeningEpicSample standard = profile.Evaluate(1.80f);
            PackOpeningEpicSample reduced = profile.Evaluate(1.80f, true);

            Assert.That(reduced.Phase, Is.EqualTo(standard.Phase));
            Assert.That(reduced.TearProgress, Is.EqualTo(standard.TearProgress));
            Assert.That(reduced.Hitstop, Is.False);
            Assert.That(reduced.CameraEffectsEnabled, Is.False);
            Assert.That(reduced.Impact, Is.Zero);
        }

        [Test]
        public void SkipLandingSample_EndsSettledWithoutRepeatingMotion()
        {
            PackOpeningEpicSample sample = profile.SkipLandingSample();

            Assert.That(
                PackOpeningEpicTimingProfile.SkipLandingSeconds,
                Is.EqualTo(0.20f));
            Assert.That(sample.Phase, Is.EqualTo(PackOpeningEpicPhase.Complete));
            Assert.That(sample.CaseRotationDegrees, Is.EqualTo(0f).Within(0.001f));
            Assert.That(sample.Cta, Is.EqualTo(1f).Within(0.001f));
        }
    }
}
