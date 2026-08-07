using UnityEngine;

namespace ThreeBladeEDC
{
    /// <summary>
    /// Pure motion helpers kept separate from input and Transform state so the
    /// interaction curves can be verified with Edit Mode tests.
    /// </summary>
    public static class FidgetSpinnerMotion
    {
        public static float ScaleSwipeVelocity(
            float pixelsPerSecond,
            float speedScale,
            float maxAngularSpeed)
        {
            return Mathf.Clamp(
                pixelsPerSecond * Mathf.Max(0f, speedScale),
                -Mathf.Abs(maxAngularSpeed),
                Mathf.Abs(maxAngularSpeed));
        }

        public static float EaseOutCubic(float t)
        {
            t = Mathf.Clamp01(t);
            float inverse = 1f - t;
            return 1f - inverse * inverse * inverse;
        }

        /// <summary>
        /// Converts a requested peak overshoot fraction into the coefficient
        /// used by the standard ease-out-back equation.
        /// </summary>
        public static float BackCoefficientForOvershoot(float overshootFraction)
        {
            float target = Mathf.Max(0f, overshootFraction);
            if (target <= Mathf.Epsilon)
            {
                return 0f;
            }

            // For coefficient c, the curve's exact peak overshoot is:
            // 4c^3 / (27(c + 1)^2). Binary search keeps the Inspector value
            // meaningful (0.1 means a 10% peak overshoot).
            float low = 0f;
            float high = 32f;
            for (int i = 0; i < 20; i++)
            {
                float coefficient = (low + high) * 0.5f;
                float numerator = 4f * coefficient * coefficient * coefficient;
                float denominator = 27f * (coefficient + 1f) * (coefficient + 1f);
                float peakOvershoot = numerator / denominator;

                if (peakOvershoot < target)
                {
                    low = coefficient;
                }
                else
                {
                    high = coefficient;
                }
            }

            return (low + high) * 0.5f;
        }

        public static float EaseOutBack(float t, float backCoefficient)
        {
            t = Mathf.Clamp01(t);
            float shifted = t - 1f;
            return 1f
                + (backCoefficient + 1f) * shifted * shifted * shifted
                + backCoefficient * shifted * shifted;
        }

        public static float DecelerateToStop(
            float initialVelocity,
            float elapsed,
            float duration)
        {
            if (duration <= Mathf.Epsilon)
            {
                return 0f;
            }

            float progress = EaseOutCubic(elapsed / duration);
            return Mathf.LerpUnclamped(initialVelocity, 0f, progress);
        }
    }
}
