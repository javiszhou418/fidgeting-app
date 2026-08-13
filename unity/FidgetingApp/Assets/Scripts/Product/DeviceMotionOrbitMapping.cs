using UnityEngine;

namespace FidgetingApp.Product
{
    /// <summary>
    /// Maps device tilt to presentation orbit without a hard stop at the
    /// configured full-scale input angle. The first segment preserves the
    /// selected sensitivity preset exactly. Beyond full scale, the view keeps
    /// following through a compressed, asymptotic shoulder so it remains
    /// responsive without exposing the back of the staged environment.
    /// </summary>
    public static class DeviceMotionOrbitMapping
    {
        public const float MaximumContinuedOrbitDegrees = 42f;
        public const float BeyondFullScaleResponse = 0.45f;

        /// <summary>
        /// Builds a camera orientation from the same orbit that moves its
        /// position. Rotating both forward and up avoids Quaternion.LookRotation
        /// changing hemispheres when a near-top-down Library camera crosses the
        /// world-up pole; that discontinuity was perceived as the model suddenly
        /// flipping one blade from up to down.
        /// </summary>
        public static Quaternion ResolveStableLookRotation(
            Vector3 authoredBackward,
            Quaternion orbit)
        {
            if (authoredBackward.sqrMagnitude <= Mathf.Epsilon)
            {
                return orbit;
            }

            Vector3 baseForward = -authoredBackward.normalized;
            Vector3 referenceUp = Mathf.Abs(Vector3.Dot(baseForward, Vector3.up))
                > 0.98f
                ? Vector3.forward
                : Vector3.up;
            Quaternion authoredLook = Quaternion.LookRotation(
                baseForward,
                referenceUp);
            Vector3 rotatedForward = orbit * baseForward;
            Vector3 rotatedUp = orbit * (authoredLook * Vector3.up);
            return Quaternion.LookRotation(rotatedForward, rotatedUp);
        }

        public static Vector2 ResolveOrbitDegrees(
            Vector2 normalizedTilt,
            float fullScaleOrbitDegrees)
        {
            float baseOrbit = Mathf.Clamp(fullScaleOrbitDegrees, 0f, 24f);
            if (baseOrbit <= 0f
                || float.IsNaN(normalizedTilt.x)
                || float.IsNaN(normalizedTilt.y)
                || float.IsInfinity(normalizedTilt.x)
                || float.IsInfinity(normalizedTilt.y))
            {
                return Vector2.zero;
            }

            float magnitude = normalizedTilt.magnitude;
            if (magnitude <= Mathf.Epsilon)
            {
                return Vector2.zero;
            }

            float orbitMagnitude;
            if (magnitude <= 1f)
            {
                orbitMagnitude = magnitude * baseOrbit;
            }
            else
            {
                float continuation = 1f - Mathf.Exp(
                    -(magnitude - 1f) * BeyondFullScaleResponse);
                orbitMagnitude = Mathf.Lerp(
                    baseOrbit,
                    MaximumContinuedOrbitDegrees,
                    continuation);
            }

            return normalizedTilt / magnitude * orbitMagnitude;
        }
    }
}
