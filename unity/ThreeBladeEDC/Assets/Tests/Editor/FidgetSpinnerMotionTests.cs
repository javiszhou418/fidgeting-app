using NUnit.Framework;
using ThreeBladeEDC;

public sealed class FidgetSpinnerMotionTests
{
    [Test]
    public void SwipeVelocity_UsesPointThreeScale()
    {
        float angularVelocity = FidgetSpinnerMotion.ScaleSwipeVelocity(
            1000f,
            0.3f,
            2000f);

        Assert.That(angularVelocity, Is.EqualTo(300f).Within(0.001f));
    }

    [Test]
    public void FlipCurve_HasTenPercentPeakOvershoot()
    {
        float coefficient =
            FidgetSpinnerMotion.BackCoefficientForOvershoot(0.1f);
        float peak = 0f;

        for (int i = 0; i <= 10000; i++)
        {
            float value = FidgetSpinnerMotion.EaseOutBack(
                i / 10000f,
                coefficient);
            peak = UnityEngine.Mathf.Max(peak, value);
        }

        Assert.That(peak, Is.EqualTo(1.1f).Within(0.0002f));
        Assert.That(
            FidgetSpinnerMotion.EaseOutBack(1f, coefficient),
            Is.EqualTo(1f).Within(0.0001f));
    }

    [Test]
    public void ReversalBrake_ReachesZeroAtThreeHundredMilliseconds()
    {
        const float initialVelocity = 600f;

        float halfway = FidgetSpinnerMotion.DecelerateToStop(
            initialVelocity,
            0.15f,
            0.3f);
        float finished = FidgetSpinnerMotion.DecelerateToStop(
            initialVelocity,
            0.3f,
            0.3f);

        Assert.That(halfway, Is.GreaterThan(0f));
        Assert.That(halfway, Is.LessThan(initialVelocity));
        Assert.That(finished, Is.EqualTo(0f).Within(0.0001f));
    }
}
