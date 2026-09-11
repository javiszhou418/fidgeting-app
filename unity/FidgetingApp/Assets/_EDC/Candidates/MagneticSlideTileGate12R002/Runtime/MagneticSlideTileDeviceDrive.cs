using UnityEngine;

namespace FidgetingApp.EDC.Gate12R002
{
    /// <summary>Mechanism pose the drive reads each step.</summary>
    public readonly struct MagneticSlideTileDeviceState
    {
        public MagneticSlideTileDeviceState(
            float travelMeters,
            float maximumTravelMeters,
            bool atMaximumTravel,
            bool angleAligned,
            bool rotationBrokenAway,
            float unwrappedAngleDegrees,
            float detentStepDegrees,
            float breakawayDegrees,
            float captureRadiusDegrees)
        {
            TravelMeters = travelMeters;
            MaximumTravelMeters = maximumTravelMeters;
            AtMaximumTravel = atMaximumTravel;
            AngleAligned = angleAligned;
            RotationBrokenAway = rotationBrokenAway;
            UnwrappedAngleDegrees = unwrappedAngleDegrees;
            DetentStepDegrees = detentStepDegrees;
            BreakawayDegrees = breakawayDegrees;
            CaptureRadiusDegrees = captureRadiusDegrees;
        }

        public float TravelMeters { get; }
        public float MaximumTravelMeters { get; }
        public bool AtMaximumTravel { get; }
        public bool AngleAligned { get; }
        public bool RotationBrokenAway { get; }
        public float UnwrappedAngleDegrees { get; }
        public float DetentStepDegrees { get; }
        public float BreakawayDegrees { get; }
        public float CaptureRadiusDegrees { get; }
    }

    /// <summary>Calibrated device inputs, already mapped into the mechanism frame.</summary>
    public readonly struct MagneticSlideTileDeviceSample
    {
        public MagneticSlideTileDeviceSample(
            float gravityTorqueNormalized,
            float phoneRateAboutAxisDegrees,
            float slideAccelerationG)
        {
            GravityTorqueNormalized = gravityTorqueNormalized;
            PhoneRateAboutAxisDegrees = phoneRateAboutAxisDegrees;
            SlideAccelerationG = slideAccelerationG;
        }

        /// <summary>Gravity torque on the moving top about the axis; +1 = one g at right angles, positive increases the angle.</summary>
        public float GravityTorqueNormalized { get; }
        /// <summary>Phone rotation about the axis in the mechanism's angle sign, deg/s, dead-zoned.</summary>
        public float PhoneRateAboutAxisDegrees { get; }
        /// <summary>User acceleration along increasing travel, in g.</summary>
        public float SlideAccelerationG { get; }
    }

    public enum MagneticSlideTileDeviceCommandKind
    {
        None = 0,
        BeginRotation = 1,
        SetAngle = 2,
        CaptureAngle = 3,
        SetTravel = 4
    }

    public readonly struct MagneticSlideTileDeviceCommand
    {
        public MagneticSlideTileDeviceCommand(
            MagneticSlideTileDeviceCommandKind kind,
            float value,
            float breakawaySignDegrees = 0f)
        {
            Kind = kind;
            Value = value;
            BreakawaySignDegrees = breakawaySignDegrees;
        }

        public static MagneticSlideTileDeviceCommand None =>
            new(MagneticSlideTileDeviceCommandKind.None, 0f);

        public MagneticSlideTileDeviceCommandKind Kind { get; }
        /// <summary>Angle in unwrapped degrees or travel in meters, by kind.</summary>
        public float Value { get; }
        /// <summary>Signed breakaway drag passed to TryBeginRotation before SetAngle.</summary>
        public float BreakawaySignDegrees { get; }
    }

    /// <summary>
    /// Signed one-axis flick detector on user acceleration along the slide.
    /// Hysteresis plus cooldown keep one flick from firing twice; a jerk gate
    /// rejects slow carries. The inertial top lags the body, so the resulting
    /// slide direction is opposite to the acceleration.
    /// </summary>
    public sealed class MagneticSlideFlickDetector
    {
        public const float ThresholdOnG = 1.10f;
        public const float ThresholdOffG = 0.45f;
        public const float JerkThresholdGPerSecond = 9f;
        public const float CooldownSeconds = 0.25f;
        public const float MaximumAccelerationForMappingG = 2.6f;

        private float previousMagnitude;
        private float cooldownRemaining;
        private bool armed = true;

        public bool Armed => armed;

        public bool Update(
            float accelerationAlongTravelG,
            float deltaTime,
            out int slideDirection,
            out float strength)
        {
            slideDirection = 0;
            strength = 0f;
            float dt = Mathf.Max(0.0001f, deltaTime);
            float magnitude = Mathf.Abs(accelerationAlongTravelG);
            float jerk = Mathf.Abs(magnitude - previousMagnitude) / dt;
            previousMagnitude = magnitude;
            cooldownRemaining = Mathf.Max(0f, cooldownRemaining - dt);

            if (!armed)
            {
                if (cooldownRemaining <= 0f && magnitude <= ThresholdOffG)
                {
                    armed = true;
                }
                return false;
            }

            if (magnitude < ThresholdOnG || jerk < JerkThresholdGPerSecond)
            {
                return false;
            }

            slideDirection = accelerationAlongTravelG > 0f ? -1 : 1;
            strength = Mathf.Clamp01(
                (magnitude - ThresholdOnG)
                / Mathf.Max(0.01f, MaximumAccelerationForMappingG - ThresholdOnG));
            armed = false;
            cooldownRemaining = CooldownSeconds;
            return true;
        }

        public void Reset()
        {
            previousMagnitude = 0f;
            cooldownRemaining = 0f;
            armed = true;
        }
    }

    /// <summary>
    /// Device-motion dynamics for the kinematic slide tile. The mechanism
    /// stays the single authority for pose, interlocks, and semantic events;
    /// this class only decides, per frame, which pose request to make:
    /// a gravity pendulum plus phone-frame coupling for the unlocked rotation
    /// at maximum travel, and an inertial flick along the slide while the
    /// angle is aligned. Pure and deterministic for a given sample stream.
    /// </summary>
    public sealed class MagneticSlideTileDeviceDrive
    {
        /// <summary>Normalized gravity torque needed to pull the top out of an endpoint detent.</summary>
        public const float GravityBreakawayTorque = 0.30f;
        /// <summary>Angular acceleration per unit normalized torque, deg/s².</summary>
        public const float GravityAngularAcceleration = 720f;
        /// <summary>Viscous bearing loss, 1/s.</summary>
        public const float RotationDamping = 2.2f;
        /// <summary>Below this speed, inside the capture radius, the magnets win.</summary>
        public const float CaptureSpeedDegreesPerSecond = 90f;
        /// <summary>Phone twist rate that releases a captured endpoint detent (2.2 rad/s, same as the rotor).</summary>
        public const float PhoneBreakawayRateDegreesPerSecond = 2.2f * Mathf.Rad2Deg;
        public const float MaximumAngularSpeedDegreesPerSecond = 1080f;
        public const float MinimumSlideSpeedMetersPerSecond = 0.16f;
        public const float MaximumSlideSpeedMetersPerSecond = 0.32f;

        private readonly MagneticSlideFlickDetector flickDetector = new();
        private bool rotating;
        private float angleDegrees;
        private float angularVelocityDegrees;
        private bool hasPhoneRate;
        private float previousPhoneRateDegrees;
        private bool sliding;
        private int slideDirection;
        private float slideSpeed;
        private float slideTravelMeters;

        public bool IsRotating => rotating;
        public bool IsSliding => sliding;
        public bool IsActive => rotating || sliding;
        public float AngleDegrees => angleDegrees;
        public float AngularVelocityDegrees => angularVelocityDegrees;

        /// <summary>Drops all motion. Called when a finger takes over or motion suspends.</summary>
        public void Cancel()
        {
            rotating = false;
            angularVelocityDegrees = 0f;
            sliding = false;
            slideDirection = 0;
            slideSpeed = 0f;
            hasPhoneRate = false;
            previousPhoneRateDegrees = 0f;
            flickDetector.Reset();
        }

        public MagneticSlideTileDeviceCommand Step(
            float deltaTime,
            in MagneticSlideTileDeviceSample sample,
            in MagneticSlideTileDeviceState state)
        {
            float dt = Mathf.Clamp(deltaTime, 0f, 1f / 20f);
            if (dt <= 0f)
            {
                return MagneticSlideTileDeviceCommand.None;
            }

            float phoneRate = sample.PhoneRateAboutAxisDegrees;
            float phoneRateDelta = hasPhoneRate ? phoneRate - previousPhoneRateDegrees : 0f;
            previousPhoneRateDegrees = phoneRate;
            hasPhoneRate = true;

            if (sliding)
            {
                return StepSlide(dt, state);
            }

            if (state.AtMaximumTravel)
            {
                return StepRotation(dt, sample, state, phoneRateDelta);
            }

            rotating = false;
            angularVelocityDegrees = 0f;
            return TryBeginSlide(dt, sample, state);
        }

        private MagneticSlideTileDeviceCommand StepRotation(
            float dt,
            in MagneticSlideTileDeviceSample sample,
            in MagneticSlideTileDeviceState state,
            float phoneRateDelta)
        {
            float torque = sample.GravityTorqueNormalized;
            bool phoneDrives = Mathf.Abs(sample.PhoneRateAboutAxisDegrees)
                >= PhoneBreakawayRateDegreesPerSecond;

            if (!rotating)
            {
                angleDegrees = state.UnwrappedAngleDegrees;
                angularVelocityDegrees = 0f;
                bool gravityDrives = Mathf.Abs(torque) >= GravityBreakawayTorque;
                if (state.AngleAligned && !gravityDrives && !phoneDrives)
                {
                    // Aligned and calm: the slide may still respond to a flick.
                    return TryBeginSlide(dt, sample, state);
                }
                if (!gravityDrives && !phoneDrives)
                {
                    return MagneticSlideTileDeviceCommand.None;
                }

                rotating = true;
                float sign = gravityDrives
                    ? Mathf.Sign(torque)
                    : -Mathf.Sign(sample.PhoneRateAboutAxisDegrees);
                // The top co-rotated with the body until now; lag starts at zero.
                return new MagneticSlideTileDeviceCommand(
                    MagneticSlideTileDeviceCommandKind.BeginRotation,
                    angleDegrees,
                    sign * state.BreakawayDegrees);
            }

            float acceleration = torque * GravityAngularAcceleration
                - RotationDamping * angularVelocityDegrees;
            angularVelocityDegrees += acceleration * dt;
            // The free top keeps its world rate: relative rate loses the body's change.
            angularVelocityDegrees -= phoneRateDelta;
            angularVelocityDegrees = Mathf.Clamp(
                angularVelocityDegrees,
                -MaximumAngularSpeedDegreesPerSecond,
                MaximumAngularSpeedDegreesPerSecond);
            angleDegrees += angularVelocityDegrees * dt;

            float nearest = Mathf.Round(angleDegrees / state.DetentStepDegrees)
                * state.DetentStepDegrees;
            bool nearWell = Mathf.Abs(angleDegrees - nearest) <= state.CaptureRadiusDegrees;
            bool slow = Mathf.Abs(angularVelocityDegrees) < CaptureSpeedDegreesPerSecond;
            bool torqueHolds = Mathf.Abs(torque) < GravityBreakawayTorque;
            if (nearWell && slow && torqueHolds && !phoneDrives)
            {
                rotating = false;
                angularVelocityDegrees = 0f;
                angleDegrees = nearest;
                return new MagneticSlideTileDeviceCommand(
                    MagneticSlideTileDeviceCommandKind.CaptureAngle,
                    nearest);
            }

            return new MagneticSlideTileDeviceCommand(
                MagneticSlideTileDeviceCommandKind.SetAngle,
                angleDegrees);
        }

        private MagneticSlideTileDeviceCommand TryBeginSlide(
            float dt,
            in MagneticSlideTileDeviceSample sample,
            in MagneticSlideTileDeviceState state)
        {
            bool flicked = flickDetector.Update(
                sample.SlideAccelerationG,
                dt,
                out int direction,
                out float strength);
            if (!flicked || !state.AngleAligned)
            {
                return MagneticSlideTileDeviceCommand.None;
            }

            bool alreadyThere = direction > 0
                ? state.AtMaximumTravel
                : state.TravelMeters <= 0f;
            if (alreadyThere)
            {
                return MagneticSlideTileDeviceCommand.None;
            }

            sliding = true;
            slideDirection = direction;
            slideSpeed = Mathf.Lerp(
                MinimumSlideSpeedMetersPerSecond,
                MaximumSlideSpeedMetersPerSecond,
                strength);
            slideTravelMeters = state.TravelMeters;
            return StepSlide(dt, state);
        }

        private MagneticSlideTileDeviceCommand StepSlide(
            float dt,
            in MagneticSlideTileDeviceState state)
        {
            slideTravelMeters += slideDirection * slideSpeed * dt;
            float target = slideDirection > 0 ? state.MaximumTravelMeters : 0f;
            bool reached = slideDirection > 0
                ? slideTravelMeters >= target
                : slideTravelMeters <= target;
            if (reached)
            {
                slideTravelMeters = target;
                sliding = false;
                slideDirection = 0;
                slideSpeed = 0f;
            }
            return new MagneticSlideTileDeviceCommand(
                MagneticSlideTileDeviceCommandKind.SetTravel,
                slideTravelMeters);
        }
    }
}
