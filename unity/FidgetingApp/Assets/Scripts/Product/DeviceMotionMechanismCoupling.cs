using UnityEngine;

namespace FidgetingApp.Product
{
    /// <summary>
    /// Pure conversions from Core Motion device-frame samples into Unity
    /// world-space mechanism quantities. Core Motion is right-handed with +z
    /// toward the user; Unity is left-handed with camera forward into the
    /// screen. Rotation rates are pseudo-vectors and flip sign under that
    /// mapping; gravity and user acceleration are true vectors and do not.
    /// </summary>
    public static class DeviceMotionMechanismCoupling
    {
        /// <summary>Gyro noise floor. A phone at rest must never drive a mechanism.</summary>
        public const float RotationRateDeadZoneRadians = 0.06f;
        public const float MaximumRotationRateRadians = 12f;
        /// <summary>Normalized gravity torque below this reads as level.</summary>
        public const float GravityTorqueDeadZone = 0.06f;

        /// <summary>
        /// Soft dead zone: values inside the band read as zero, values outside
        /// keep their sign and lose the band width so the output stays continuous.
        /// </summary>
        public static float ApplyDeadZone(float value, float deadZone)
        {
            float band = Mathf.Max(0f, deadZone);
            float magnitude = Mathf.Abs(value);
            if (magnitude <= band)
            {
                return 0f;
            }
            return Mathf.Sign(value) * (magnitude - band);
        }

        /// <summary>
        /// Phone angular velocity in Unity world space using Unity's
        /// left-handed rotation sign, from a Core Motion rotationRate sample.
        /// </summary>
        public static Vector3 ResolvePhoneAngularVelocityWorld(
            Vector3 rotationRateDevice,
            Vector3 cameraRight,
            Vector3 cameraUp,
            Vector3 cameraForward)
        {
            return -rotationRateDevice.x * cameraRight
                - rotationRateDevice.y * cameraUp
                + rotationRateDevice.z * cameraForward;
        }

        /// <summary>
        /// Signed phone rotation rate about a mechanism axis (Unity sign,
        /// rad/s) after the dead zone and clamp. A free rotor keeps its world
        /// angular velocity, so its velocity relative to the phone changes by
        /// minus this value.
        /// </summary>
        public static float ResolvePhoneRateAboutAxis(
            Vector3 rotationRateDevice,
            Vector3 cameraRight,
            Vector3 cameraUp,
            Vector3 cameraForward,
            Vector3 axisWorld)
        {
            if (axisWorld.sqrMagnitude <= Mathf.Epsilon)
            {
                return 0f;
            }

            float raw = Vector3.Dot(
                ResolvePhoneAngularVelocityWorld(
                    rotationRateDevice,
                    cameraRight,
                    cameraUp,
                    cameraForward),
                axisWorld.normalized);
            return Mathf.Clamp(
                ApplyDeadZone(raw, RotationRateDeadZoneRadians),
                -MaximumRotationRateRadians,
                MaximumRotationRateRadians);
        }

        /// <summary>
        /// Maps a device-frame true vector (gravity or userAcceleration, in g)
        /// into Unity world space through the viewing camera basis.
        /// </summary>
        public static Vector3 ResolveDeviceVectorWorld(
            Vector3 deviceVector,
            Vector3 cameraRight,
            Vector3 cameraUp,
            Vector3 cameraForward)
        {
            return deviceVector.x * cameraRight
                + deviceVector.y * cameraUp
                - deviceVector.z * cameraForward;
        }

        /// <summary>
        /// Normalized gravity torque about <paramref name="axisWorld"/> acting
        /// on a mass whose centroid sits at <paramref name="leverWorld"/> from
        /// the pivot. 1.0 means one g at right angles to the lever. Positive
        /// follows Unity's positive rotation about the axis.
        /// </summary>
        public static float ResolveGravityTorqueNormalized(
            Vector3 leverWorld,
            Vector3 gravityWorld,
            Vector3 axisWorld)
        {
            if (axisWorld.sqrMagnitude <= Mathf.Epsilon)
            {
                return 0f;
            }

            Vector3 axis = axisWorld.normalized;
            Vector3 lever = Vector3.ProjectOnPlane(leverWorld, axis);
            if (lever.sqrMagnitude <= 1e-12f)
            {
                return 0f;
            }

            Vector3 gravityInPlane = Vector3.ProjectOnPlane(gravityWorld, axis);
            float torque = Vector3.Dot(
                Vector3.Cross(lever.normalized, gravityInPlane),
                axis);
            return Mathf.Clamp(torque, -1f, 1f);
        }
    }
}
