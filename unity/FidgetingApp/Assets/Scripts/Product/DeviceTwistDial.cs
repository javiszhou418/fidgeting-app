using UnityEngine;

namespace FidgetingApp.Product
{
    public readonly struct DeviceTwistDialStep
    {
        public DeviceTwistDialStep(
            bool emitTick,
            int crossedDetents,
            int direction,
            float normalizedIntensity)
        {
            EmitTick = emitTick;
            CrossedDetents = crossedDetents;
            Direction = direction;
            NormalizedIntensity = normalizedIntensity;
        }

        /// <summary>True when a rate-limited tick may be rendered this step.</summary>
        public bool EmitTick { get; }
        /// <summary>Detents actually crossed this step. Never delayed by the rate limit.</summary>
        public int CrossedDetents { get; }
        public int Direction { get; }
        public float NormalizedIntensity { get; }
    }

    /// <summary>
    /// The phone body as an endless dial about the screen normal. Integrates
    /// the dead-zoned gyroscope rate (never wrapped-Euler subtraction), so the
    /// accumulated angle stays continuous across ±180°. The one detent count
    /// drives both the physical index and the haptic ticks. Ticks are rate
    /// limited without ever delaying or queuing the index.
    /// </summary>
    public sealed class DeviceTwistDial
    {
        public const int DefaultDetentsPerTurn = 24;
        public const float BoundaryHysteresisDegrees = 1.0f;
        public const float RateDeadZoneRadians =
            DeviceMotionMechanismCoupling.RotationRateDeadZoneRadians;
        public const float MaximumRateRadians =
            DeviceMotionMechanismCoupling.MaximumRotationRateRadians;
        public const float RateForFullIntensity = 5f;
        public const float MinimumTickInterval = 0.030f;
        private const double NormalizationLimitDegrees = 1.0e7;

        private double accumulatedDegrees;
        private int detentIndex;
        private float tickCooldown;

        public DeviceTwistDial(int detentsPerTurn = DefaultDetentsPerTurn)
        {
            DetentsPerTurn = Mathf.Clamp(detentsPerTurn, 1, 360);
        }

        public int DetentsPerTurn { get; }
        public float DetentStepDegrees => 360f / DetentsPerTurn;
        public double AccumulatedDegrees => accumulatedDegrees;
        public int DetentIndex => detentIndex;

        public void Recenter()
        {
            accumulatedDegrees = 0d;
            detentIndex = 0;
            tickCooldown = 0f;
        }

        public DeviceTwistDialStep Update(float rateRadiansPerSecond, float deltaTime)
        {
            float dt = Mathf.Max(0f, deltaTime);
            tickCooldown = Mathf.Max(0f, tickCooldown - dt);
            float rate = Mathf.Clamp(
                DeviceMotionMechanismCoupling.ApplyDeadZone(
                    rateRadiansPerSecond,
                    RateDeadZoneRadians),
                -MaximumRateRadians,
                MaximumRateRadians);
            if (dt <= 0f || Mathf.Approximately(rate, 0f))
            {
                return default;
            }

            accumulatedDegrees += rate * Mathf.Rad2Deg * dt;

            double step = DetentStepDegrees;
            int crossed = 0;
            int direction = 0;
            while (true)
            {
                double upperBoundary =
                    (detentIndex + 0.5) * step + BoundaryHysteresisDegrees;
                double lowerBoundary =
                    (detentIndex - 0.5) * step - BoundaryHysteresisDegrees;
                if (accumulatedDegrees >= upperBoundary)
                {
                    detentIndex++;
                    crossed++;
                    direction = 1;
                }
                else if (accumulatedDegrees <= lowerBoundary)
                {
                    detentIndex--;
                    crossed++;
                    direction = -1;
                }
                else
                {
                    break;
                }
            }

            NormalizeAccumulation();
            if (crossed == 0)
            {
                return default;
            }

            float intensity = Mathf.Clamp01(Mathf.Abs(rate) / RateForFullIntensity);
            bool emit = tickCooldown <= 0f;
            if (emit)
            {
                tickCooldown = MinimumTickInterval;
            }
            return new DeviceTwistDialStep(emit, crossed, direction, intensity);
        }

        private void NormalizeAccumulation()
        {
            if (System.Math.Abs(accumulatedDegrees) < NormalizationLimitDegrees)
            {
                return;
            }
            // The dial is relative; rebasing onto the current detent keeps the
            // double bounded without changing the residual inside the detent.
            accumulatedDegrees -= detentIndex * (double)DetentStepDegrees;
            detentIndex = 0;
        }
    }
}
