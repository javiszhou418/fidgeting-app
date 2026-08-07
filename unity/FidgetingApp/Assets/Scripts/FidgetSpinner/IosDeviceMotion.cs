using System.Runtime.InteropServices;
using UnityEngine;

namespace CodexUnityLab
{
    public static class IosDeviceMotion
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern int CodexIosDeviceMotionStart();

        [DllImport("__Internal")]
        private static extern void CodexIosDeviceMotionStop();

        [DllImport("__Internal")]
        private static extern int CodexIosReduceMotionEnabled();

        [DllImport("__Internal")]
        private static extern int CodexIosDeviceMotionRead(
            out double roll,
            out double pitch,
            out double yaw,
            out double rotationRateX,
            out double rotationRateY,
            out double rotationRateZ,
            out double gravityX,
            out double gravityY,
            out double gravityZ,
            out double userAccelerationX,
            out double userAccelerationY,
            out double userAccelerationZ);
#endif

        public static bool Start()
        {
#if UNITY_IOS && !UNITY_EDITOR
            return CodexIosDeviceMotionStart() != 0;
#else
            return false;
#endif
        }

        public static void Stop()
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexIosDeviceMotionStop();
#endif
        }

        public static bool IsReduceMotionEnabled()
        {
#if UNITY_IOS && !UNITY_EDITOR
            return CodexIosReduceMotionEnabled() != 0;
#else
            return false;
#endif
        }

        public static bool TryRead(out Vector3 attitudeRadians, out Vector3 rotationRateRadians)
        {
            return TryRead(
                out attitudeRadians,
                out rotationRateRadians,
                out _,
                out _);
        }

        public static bool TryRead(
            out Vector3 attitudeRadians,
            out Vector3 rotationRateRadians,
            out Vector3 gravity,
            out Vector3 userAcceleration)
        {
            attitudeRadians = Vector3.zero;
            rotationRateRadians = Vector3.zero;
            gravity = Vector3.zero;
            userAcceleration = Vector3.zero;

#if UNITY_IOS && !UNITY_EDITOR
            if (CodexIosDeviceMotionRead(
                    out double roll,
                    out double pitch,
                    out double yaw,
                    out double rotationRateX,
                    out double rotationRateY,
                    out double rotationRateZ,
                    out double gravityX,
                    out double gravityY,
                    out double gravityZ,
                    out double userAccelerationX,
                    out double userAccelerationY,
                    out double userAccelerationZ) == 0)
            {
                return false;
            }

            attitudeRadians = new Vector3((float)roll, (float)pitch, (float)yaw);
            rotationRateRadians = new Vector3(
                (float)rotationRateX,
                (float)rotationRateY,
                (float)rotationRateZ);
            gravity = new Vector3((float)gravityX, (float)gravityY, (float)gravityZ);
            userAcceleration = new Vector3(
                (float)userAccelerationX,
                (float)userAccelerationY,
                (float)userAccelerationZ);
            return true;
#else
            return false;
#endif
        }
    }

    /// <summary>
    /// Stateful threshold/hysteresis detector. Core Motion userAcceleration is
    /// measured in g. A jerk gate rejects slow device movement, while cooldown
    /// and a lower re-arm threshold prevent repeated bursts from one shake.
    /// </summary>
    public sealed class FidgetShakeDetector
    {
        public const float ThresholdOn = 1.55f;
        public const float ThresholdOff = 0.65f;
        public const float JerkThreshold = 8f;
        public const float MinimumPeakDuration = 0.025f;
        public const float Cooldown = 0.14f;
        public const float MaximumAccelerationForMapping = 3f;

        private float previousMagnitude;
        private float candidateDuration;
        private float cooldownRemaining;
        private bool candidate;
        private bool armed = true;

        public bool Armed => armed;

        public bool Update(Vector3 userAcceleration, float deltaTime, out float strength)
        {
            strength = 0f;
            float dt = Mathf.Max(0.0001f, deltaTime);
            float magnitude = userAcceleration.magnitude;
            float jerk = Mathf.Abs(magnitude - previousMagnitude) / dt;
            previousMagnitude = magnitude;
            cooldownRemaining = Mathf.Max(0f, cooldownRemaining - dt);

            if (!armed)
            {
                if (cooldownRemaining <= 0f && magnitude <= ThresholdOff)
                {
                    armed = true;
                }
                return false;
            }

            if (!candidate)
            {
                if (magnitude >= ThresholdOn && jerk >= JerkThreshold)
                {
                    candidate = true;
                    candidateDuration = dt;
                }
                return false;
            }

            if (magnitude < ThresholdOn * 0.80f)
            {
                candidate = false;
                candidateDuration = 0f;
                return false;
            }

            candidateDuration += dt;
            if (candidateDuration < MinimumPeakDuration)
            {
                return false;
            }

            strength = Mathf.Clamp01(
                (magnitude - ThresholdOn)
                / Mathf.Max(0.01f, MaximumAccelerationForMapping - ThresholdOn));
            candidate = false;
            candidateDuration = 0f;
            cooldownRemaining = Cooldown;
            armed = false;
            return true;
        }

        public void Reset()
        {
            previousMagnitude = 0f;
            candidateDuration = 0f;
            cooldownRemaining = 0f;
            candidate = false;
            armed = true;
        }
    }

    /// <summary>
    /// Low-threshold device-mass channel. It uses Core Motion userAcceleration
    /// in g, a 0.30/0.22 hysteresis pair, and a 125 ms gate so sustained motion
    /// can read as weight shifting without exceeding eight taps per second.
    /// </summary>
    public sealed class FidgetInertiaHapticDetector
    {
        public const float ThresholdOn = 0.30f;
        public const float ThresholdOff = 0.22f;
        public const float MaximumAccelerationForMapping = 1.50f;
        public const float MinimumInterval = 0.125f;

        private bool active;
        private float intervalRemaining;

        public bool Active => active;

        public bool Update(
            Vector3 userAcceleration,
            float deltaTime,
            out float normalizedStrength)
        {
            normalizedStrength = 0f;
            float magnitude = userAcceleration.magnitude;
            intervalRemaining = Mathf.Max(
                0f,
                intervalRemaining - Mathf.Max(0f, deltaTime));

            if (active)
            {
                if (magnitude <= ThresholdOff)
                {
                    active = false;
                    return false;
                }
            }
            else
            {
                if (magnitude < ThresholdOn)
                {
                    return false;
                }
                active = true;
            }

            if (intervalRemaining > 0f)
            {
                return false;
            }

            normalizedStrength = Mathf.Clamp01(
                (magnitude - ThresholdOn)
                / (MaximumAccelerationForMapping - ThresholdOn));
            intervalRemaining = MinimumInterval;
            return true;
        }

        public void Reset()
        {
            active = false;
            intervalRemaining = 0f;
        }
    }
}
