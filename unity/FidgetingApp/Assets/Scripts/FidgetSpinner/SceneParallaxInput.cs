using UnityEngine;

namespace CodexUnityLab
{
    /// <summary>
    /// Shared, presentation-only handoff for the already filtered device tilt.
    /// Motion controllers remain the single owners of Core Motion/Input System
    /// sampling; visual consumers never start a second sensor pipeline.
    /// </summary>
    public static class SceneParallaxInput
    {
        private static Vector2 latestTilt;
        private static float latestFullScaleAngle = 15f;
        private static int latestFrame = int.MinValue;

        public static void Publish(Vector2 normalizedTilt)
        {
            Publish(normalizedTilt, 15f);
        }

        public static void Publish(
            Vector2 normalizedTilt,
            float fullScaleAngleDegrees)
        {
            latestTilt = Vector2.ClampMagnitude(normalizedTilt, 1f);
            latestFullScaleAngle = Mathf.Max(1f, fullScaleAngleDegrees);
            latestFrame = Time.frameCount;
        }

        public static bool TryGetRecent(out Vector2 normalizedTilt, int maximumFrameAge = 2)
        {
            normalizedTilt = latestTilt;
            if (latestFrame == int.MinValue)
            {
                return false;
            }

            return Time.frameCount - latestFrame <= Mathf.Max(0, maximumFrameAge);
        }

        public static bool TryGetRecent(
            out Vector2 normalizedTilt,
            out float fullScaleAngleDegrees,
            int maximumFrameAge = 2)
        {
            fullScaleAngleDegrees = latestFullScaleAngle;
            return TryGetRecent(out normalizedTilt, maximumFrameAge);
        }

        public static void Reset()
        {
            latestTilt = Vector2.zero;
            latestFullScaleAngle = 15f;
            latestFrame = int.MinValue;
        }

        public static Vector2 MapToParallax(
            Vector2 normalizedTilt,
            float sourceFullScaleAngleDegrees,
            float parallaxFullScaleAngleDegrees,
            float verticalScale)
        {
            float sourceAngle = Mathf.Max(1f, sourceFullScaleAngleDegrees);
            float targetAngle = Mathf.Max(1f, parallaxFullScaleAngleDegrees);
            Vector2 angleRatio = normalizedTilt * sourceAngle / targetAngle;
            return new Vector2(
                SoftClampAxis(angleRatio.x),
                SoftClampAxis(angleRatio.y) * Mathf.Clamp01(verticalScale));
        }

        public static float SoftClampAxis(float normalizedAngle)
        {
            float sign = Mathf.Sign(normalizedAngle);
            float magnitude = Mathf.Abs(normalizedAngle);
            if (magnitude <= 0.80f)
            {
                return normalizedAngle;
            }
            if (magnitude >= 1f)
            {
                return sign;
            }

            float t = (magnitude - 0.80f) / 0.20f;
            float shoulder = t + t * t - t * t * t;
            return sign * Mathf.Lerp(0.80f, 1f, shoulder);
        }

        public static Vector2 NormalizePointer(Vector2 pointerPixels, Vector2 viewportPixels)
        {
            float width = Mathf.Max(1f, viewportPixels.x);
            float height = Mathf.Max(1f, viewportPixels.y);
            return new Vector2(
                Mathf.Clamp(pointerPixels.x / width * 2f - 1f, -1f, 1f),
                Mathf.Clamp(pointerPixels.y / height * 2f - 1f, -1f, 1f));
        }

        public static Vector2 ApplyRadialDeadZone(Vector2 value, float deadZone)
        {
            float clampedDeadZone = Mathf.Clamp(deadZone, 0f, 0.95f);
            float magnitude = value.magnitude;
            if (magnitude <= clampedDeadZone)
            {
                return Vector2.zero;
            }

            float remappedMagnitude = Mathf.InverseLerp(clampedDeadZone, 1f, magnitude);
            return value.normalized * Mathf.Clamp01(remappedMagnitude);
        }

        public static Vector2 Smooth(
            Vector2 current,
            Vector2 target,
            float response,
            float unscaledDeltaTime)
        {
            float blend = response <= 0f
                ? 1f
                : 1f - Mathf.Exp(-response * Mathf.Max(0f, unscaledDeltaTime));
            return Vector2.Lerp(current, target, blend);
        }
    }
}
