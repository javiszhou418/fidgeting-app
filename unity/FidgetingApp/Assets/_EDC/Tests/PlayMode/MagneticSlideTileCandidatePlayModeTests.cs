using FidgetingApp.EDC.Candidate;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.EDC.Tests.PlayMode
{
    public sealed class MagneticSlideTileCandidatePlayModeTests
    {
        [Test]
        public void CandidateResetLeavesNoSelfMotion()
        {
            var root = new GameObject("CandidatePlayModeTest");
            var pivot = new GameObject("UpperPivot").transform;
            pivot.SetParent(root.transform, false);
            MagneticSlideTileCandidateSettings settings =
                ScriptableObject.CreateInstance<MagneticSlideTileCandidateSettings>();
            MagneticSlideTileCandidateController controller =
                root.AddComponent<MagneticSlideTileCandidateController>();
            controller.Configure(pivot, settings);

            Vector3 initialPosition = pivot.localPosition;
            Quaternion initialRotation = pivot.localRotation;
            Assert.That(pivot.localPosition, Is.EqualTo(initialPosition));
            Assert.That(pivot.localRotation, Is.EqualTo(initialRotation));
            Assert.That(controller.AngularVelocityDegreesPerSecond, Is.Zero);
            Assert.That(controller.LinearVelocityMetersPerSecond, Is.Zero);

            controller.SetSlideProgress(1f);
            controller.SetDetentIndex(5);
            controller.ResetPose();
            Assert.That(controller.SlideProgress, Is.Zero);
            Assert.That(controller.CapturedDetentIndex, Is.Zero);
            Assert.That(controller.AngularVelocityDegreesPerSecond, Is.Zero);
            Assert.That(controller.LinearVelocityMetersPerSecond, Is.Zero);
            Assert.That(pivot.localPosition, Is.EqualTo(initialPosition));
            Assert.That(pivot.localRotation, Is.EqualTo(initialRotation));

            Object.Destroy(root);
            Object.Destroy(settings);
        }
    }
}
