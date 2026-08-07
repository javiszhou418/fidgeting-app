using System;
using UnityEngine;

namespace FidgetingApp.EDC
{
    public enum MagneticDetentState
    {
        Captured = 0,
        Loading = 1,
        Breakaway = 2,
        Traveling = 3,
        Capturing = 4
    }

    public readonly struct MagneticDetentStepResult
    {
        public MagneticDetentStepResult(
            bool brokeAway,
            int crossedDetentCount,
            int crossingDirection,
            bool captured,
            int capturedDetentIndex,
            int captureDirection)
        {
            BrokeAway = brokeAway;
            CrossedDetentCount = Mathf.Max(0, crossedDetentCount);
            CrossingDirection = Math.Sign(crossingDirection);
            Captured = captured;
            CapturedDetentIndex = capturedDetentIndex;
            CaptureDirection = Math.Sign(captureDirection);
        }

        public bool BrokeAway { get; }
        public int CrossedDetentCount { get; }
        public int CrossingDirection { get; }
        public bool Captured { get; }
        public int CapturedDetentIndex { get; }
        public int CaptureDirection { get; }
        public static MagneticDetentStepResult None => new(
            false,
            0,
            0,
            false,
            -1,
            0);
    }

    /// <summary>
    /// Allocation-free, deterministic one-dimensional magnetic detent solver.
    /// The scalar coordinate can later be adapted to radians for rotary products.
    /// </summary>
    public sealed class MagneticDetentTrack1D
    {
        private readonly LinearMagneticDetentProfile profile;
        private int capturedDetentIndex;
        private int basinDetentIndex;
        private int captureTargetIndex;
        private int breakawayDirection;
        private bool escapedCapturedWell;

        public MagneticDetentTrack1D(LinearMagneticDetentProfile profile)
        {
            this.profile = profile != null
                ? profile
                : throw new ArgumentNullException(nameof(profile));
            if (!profile.IsValid(out string reason))
            {
                throw new ArgumentException(reason, nameof(profile));
            }
            ResetToDetent(0);
        }

        public MagneticDetentState State { get; private set; }
        public float PositionMeters { get; private set; }
        public float VelocityMetersPerSecond { get; private set; }
        public float LoadNormalized { get; private set; }
        public float VisiblePreloadMeters { get; private set; }
        public int CapturedDetentIndex => capturedDetentIndex;
        public int BasinDetentIndex => basinDetentIndex;
        public float BarrierProgress => ResolveBarrierProgress();
        public bool IsAtRest => State == MagneticDetentState.Captured
            && Mathf.Approximately(VelocityMetersPerSecond, 0f);

        public void ResetToDetent(int detentIndex)
        {
            int resolvedIndex = Mathf.Clamp(detentIndex, 0, profile.DetentCount - 1);
            capturedDetentIndex = resolvedIndex;
            basinDetentIndex = resolvedIndex;
            captureTargetIndex = resolvedIndex;
            PositionMeters = profile.GetDetentPositionMeters(resolvedIndex);
            VelocityMetersPerSecond = 0f;
            LoadNormalized = 0f;
            VisiblePreloadMeters = 0f;
            State = MagneticDetentState.Captured;
            breakawayDirection = 0;
            escapedCapturedWell = false;
        }

        public void ResetToPosition(float positionMeters)
        {
            ResetToDetent(FindNearestDetentIndex(positionMeters));
        }

        public void Release()
        {
            LoadNormalized = 0f;
            VisiblePreloadMeters = 0f;
            if (State == MagneticDetentState.Captured)
            {
                VelocityMetersPerSecond = 0f;
                return;
            }

            float predicted = PositionMeters
                + VelocityMetersPerSecond * profile.ReleasePredictionSeconds;
            BeginCapture(FindNearestDetentIndex(predicted));
        }

        public MagneticDetentStepResult Step(
            float deltaTime,
            float handTargetMeters,
            bool handActive,
            bool slowIntent = false)
        {
            float availableTime = Mathf.Min(
                Mathf.Max(0f, deltaTime),
                profile.MaximumIntegrationStepSeconds * profile.MaximumSubstepsPerFrame);
            if (availableTime <= 0f)
            {
                return MagneticDetentStepResult.None;
            }

            bool brokeAway = false;
            int crossed = 0;
            int crossingDirection = 0;
            bool captured = false;
            int resultCapturedIndex = -1;
            int captureDirection = 0;
            int substeps = Mathf.Clamp(
                Mathf.CeilToInt(availableTime / profile.MaximumIntegrationStepSeconds),
                1,
                profile.MaximumSubstepsPerFrame);
            float stepSeconds = availableTime / substeps;

            for (int step = 0; step < substeps; step++)
            {
                MagneticDetentStepResult partial = StepSubstep(
                    stepSeconds,
                    handTargetMeters,
                    handActive,
                    slowIntent);
                brokeAway |= partial.BrokeAway;
                if (partial.CrossedDetentCount > 0)
                {
                    crossed += partial.CrossedDetentCount;
                    crossingDirection = partial.CrossingDirection;
                }
                if (partial.Captured)
                {
                    captured = true;
                    resultCapturedIndex = partial.CapturedDetentIndex;
                    captureDirection = partial.CaptureDirection;
                }
            }

            return new MagneticDetentStepResult(
                brokeAway,
                crossed,
                crossingDirection,
                captured,
                resultCapturedIndex,
                captureDirection);
        }

        public int FindNearestDetentIndex(float positionMeters)
        {
            int nearest = 0;
            float nearestDistance = Mathf.Abs(
                positionMeters - profile.GetDetentPositionMeters(0));
            for (int index = 1; index < profile.DetentCount; index++)
            {
                float distance = Mathf.Abs(
                    positionMeters - profile.GetDetentPositionMeters(index));
                if (distance < nearestDistance)
                {
                    nearest = index;
                    nearestDistance = distance;
                }
            }
            return nearest;
        }

        private MagneticDetentStepResult StepSubstep(
            float deltaTime,
            float handTargetMeters,
            bool handActive,
            bool slowIntent)
        {
            switch (State)
            {
                case MagneticDetentState.Captured:
                case MagneticDetentState.Loading:
                    return StepCaptured(handTargetMeters, handActive);
                case MagneticDetentState.Breakaway:
                    State = MagneticDetentState.Traveling;
                    return StepTraveling(
                        deltaTime,
                        handTargetMeters,
                        handActive,
                        slowIntent);
                case MagneticDetentState.Traveling:
                    if (!handActive)
                    {
                        Release();
                        return StepCapturing(deltaTime);
                    }
                    return StepTraveling(deltaTime, handTargetMeters, true, slowIntent);
                case MagneticDetentState.Capturing:
                    return StepCapturing(deltaTime);
                default:
                    return MagneticDetentStepResult.None;
            }
        }

        private MagneticDetentStepResult StepCaptured(
            float handTargetMeters,
            bool handActive)
        {
            PositionMeters = profile.GetDetentPositionMeters(capturedDetentIndex);
            VelocityMetersPerSecond = 0f;
            if (!handActive)
            {
                State = MagneticDetentState.Captured;
                LoadNormalized = 0f;
                VisiblePreloadMeters = 0f;
                return MagneticDetentStepResult.None;
            }

            float handForce = profile.HandSpringNewtonsPerMeter
                * (handTargetMeters - PositionMeters);
            LoadNormalized = profile.BreakawayForceNewtons > 0f
                ? Mathf.Clamp01(Mathf.Abs(handForce) / profile.BreakawayForceNewtons)
                : 1f;
            int direction = Math.Sign(handForce);
            VisiblePreloadMeters = direction
                * profile.MaximumVisiblePreloadMeters
                * LoadNormalized;

            if (Mathf.Abs(handForce) + 0.000001f < profile.BreakawayForceNewtons
                || direction == 0
                || (direction < 0 && capturedDetentIndex == 0)
                || (direction > 0 && capturedDetentIndex == profile.DetentCount - 1))
            {
                State = LoadNormalized > 0f
                    ? MagneticDetentState.Loading
                    : MagneticDetentState.Captured;
                return MagneticDetentStepResult.None;
            }

            breakawayDirection = direction;
            escapedCapturedWell = false;
            PositionMeters += VisiblePreloadMeters;
            float storedEnergy = 0.5f
                * profile.HandSpringNewtonsPerMeter
                * VisiblePreloadMeters
                * VisiblePreloadMeters;
            VelocityMetersPerSecond = direction * Mathf.Sqrt(
                Mathf.Max(0f, 2f * storedEnergy / profile.MovingMassKilograms));
            LoadNormalized = 0f;
            VisiblePreloadMeters = 0f;
            State = MagneticDetentState.Breakaway;
            return new MagneticDetentStepResult(true, 0, 0, false, -1, 0);
        }

        private MagneticDetentStepResult StepTraveling(
            float deltaTime,
            float handTargetMeters,
            bool handActive,
            bool slowIntent)
        {
            float previousPosition = PositionMeters;
            float force = MagneticForce(PositionMeters)
                - profile.RailDampingNewtonSecondsPerMeter * VelocityMetersPerSecond;
            if (handActive)
            {
                force += profile.HandSpringNewtonsPerMeter
                    * (handTargetMeters - PositionMeters);
                force -= profile.HandDampingNewtonSecondsPerMeter
                    * VelocityMetersPerSecond;
            }
            force = ApplyDryFriction(force, VelocityMetersPerSecond);

            VelocityMetersPerSecond += force
                / profile.MovingMassKilograms
                * deltaTime;
            if (handActive && slowIntent)
            {
                ApplySlowEdgeGovernor();
            }
            PositionMeters += VelocityMetersPerSecond * deltaTime;
            ConstrainToTrack();

            int previousBasin = basinDetentIndex;
            UpdateBasinWithHysteresis();
            int basinDelta = basinDetentIndex - previousBasin;
            if (basinDelta != 0)
            {
                escapedCapturedWell = true;
            }

            if (handActive && escapedCapturedWell)
            {
                int nearest = FindNearestDetentIndex(PositionMeters);
                float distance = Mathf.Abs(
                    PositionMeters - profile.GetDetentPositionMeters(nearest));
                if (distance <= profile.CaptureRadiusMeters
                    && Mathf.Abs(VelocityMetersPerSecond)
                        <= profile.CaptureEntrySpeedMetersPerSecond)
                {
                    BeginCapture(nearest);
                }
            }

            int direction = basinDelta != 0
                ? Math.Sign(basinDelta)
                : Math.Sign(PositionMeters - previousPosition);
            return new MagneticDetentStepResult(
                false,
                Mathf.Abs(basinDelta),
                direction,
                false,
                -1,
                0);
        }

        private MagneticDetentStepResult StepCapturing(float deltaTime)
        {
            float target = profile.GetDetentPositionMeters(captureTargetIndex);
            float previousPosition = PositionMeters;
            float force = profile.CaptureSpringNewtonsPerMeter
                    * (target - PositionMeters)
                - profile.CaptureDampingNewtonSecondsPerMeter
                    * VelocityMetersPerSecond
                + MagneticForce(PositionMeters)
                - profile.RailDampingNewtonSecondsPerMeter
                    * VelocityMetersPerSecond;
            force = ApplyDryFriction(force, VelocityMetersPerSecond);
            VelocityMetersPerSecond += force
                / profile.MovingMassKilograms
                * deltaTime;
            PositionMeters += VelocityMetersPerSecond * deltaTime;
            ConstrainToTrack();

            int previousBasin = basinDetentIndex;
            UpdateBasinWithHysteresis();
            int basinDelta = basinDetentIndex - previousBasin;

            float error = target - PositionMeters;
            if (Mathf.Abs(error) > profile.LockPositionErrorMeters
                || Mathf.Abs(VelocityMetersPerSecond) > profile.LockSpeedMetersPerSecond)
            {
                return new MagneticDetentStepResult(
                    false,
                    Mathf.Abs(basinDelta),
                    Math.Sign(basinDelta),
                    false,
                    -1,
                    0);
            }

            int direction = Math.Sign(target - previousPosition);
            PositionMeters = target;
            VelocityMetersPerSecond = 0f;
            capturedDetentIndex = captureTargetIndex;
            basinDetentIndex = captureTargetIndex;
            LoadNormalized = 0f;
            VisiblePreloadMeters = 0f;
            State = MagneticDetentState.Captured;
            escapedCapturedWell = false;
            breakawayDirection = 0;
            return new MagneticDetentStepResult(
                false,
                Mathf.Abs(basinDelta),
                Math.Sign(basinDelta),
                true,
                capturedDetentIndex,
                direction);
        }

        private void BeginCapture(int targetIndex)
        {
            captureTargetIndex = Mathf.Clamp(targetIndex, 0, profile.DetentCount - 1);
            State = MagneticDetentState.Capturing;
            LoadNormalized = 0f;
            VisiblePreloadMeters = 0f;
        }

        private void ApplySlowEdgeGovernor()
        {
            float progress = ResolveBarrierProgress();
            if (progress < profile.EdgeGovernorStartProgress || progress >= 1f)
            {
                return;
            }

            float weight = Mathf.SmoothStep(
                0f,
                1f,
                Mathf.InverseLerp(
                    profile.EdgeGovernorStartProgress,
                    profile.EdgeGovernorEndProgress,
                    progress));
            float speedCap = Mathf.Lerp(
                profile.EdgeGovernorStartSpeedMetersPerSecond,
                profile.EdgeGovernorEndSpeedMetersPerSecond,
                weight);
            float towardBarrierSpeed = breakawayDirection * VelocityMetersPerSecond;
            if (towardBarrierSpeed > speedCap)
            {
                VelocityMetersPerSecond = breakawayDirection * speedCap;
            }
        }

        private float ResolveBarrierProgress()
        {
            if (breakawayDirection == 0)
            {
                return 0f;
            }

            int adjacentIndex = capturedDetentIndex + breakawayDirection;
            if (adjacentIndex < 0 || adjacentIndex >= profile.DetentCount)
            {
                return 0f;
            }

            float center = profile.GetDetentPositionMeters(capturedDetentIndex);
            float adjacent = profile.GetDetentPositionMeters(adjacentIndex);
            float barrierDistance = Mathf.Abs(adjacent - center) * 0.5f;
            if (barrierDistance <= 0.000001f)
            {
                return 0f;
            }
            return Mathf.Max(
                0f,
                breakawayDirection * (PositionMeters - center) / barrierDistance);
        }

        private float MagneticForce(float positionMeters)
        {
            int leftIndex = 0;
            while (leftIndex < profile.DetentCount - 2
                && positionMeters > profile.GetDetentPositionMeters(leftIndex + 1))
            {
                leftIndex++;
            }
            float left = profile.GetDetentPositionMeters(leftIndex);
            float right = profile.GetDetentPositionMeters(leftIndex + 1);
            float q = Mathf.InverseLerp(left, right, positionMeters);
            return -profile.MagneticPeakForceNewtons
                * Mathf.Sin(2f * Mathf.PI * q);
        }

        private float ApplyDryFriction(float force, float velocity)
        {
            float friction = profile.RailFrictionNewtons;
            if (Mathf.Abs(velocity) > 0.00001f)
            {
                return force - Mathf.Sign(velocity) * friction;
            }
            if (Mathf.Abs(force) <= friction)
            {
                return 0f;
            }
            return force - Mathf.Sign(force) * friction;
        }

        private void UpdateBasinWithHysteresis()
        {
            float hysteresis = profile.BarrierHysteresisMeters;
            while (basinDetentIndex < profile.DetentCount - 1)
            {
                float barrier = 0.5f * (
                    profile.GetDetentPositionMeters(basinDetentIndex)
                    + profile.GetDetentPositionMeters(basinDetentIndex + 1));
                if (PositionMeters <= barrier + hysteresis)
                {
                    break;
                }
                basinDetentIndex++;
            }
            while (basinDetentIndex > 0)
            {
                float barrier = 0.5f * (
                    profile.GetDetentPositionMeters(basinDetentIndex - 1)
                    + profile.GetDetentPositionMeters(basinDetentIndex));
                if (PositionMeters >= barrier - hysteresis)
                {
                    break;
                }
                basinDetentIndex--;
            }
        }

        private void ConstrainToTrack()
        {
            float minimum = profile.GetDetentPositionMeters(0);
            float maximum = profile.GetDetentPositionMeters(profile.DetentCount - 1);
            if (PositionMeters <= minimum)
            {
                PositionMeters = minimum;
                if (VelocityMetersPerSecond < 0f)
                {
                    VelocityMetersPerSecond = 0f;
                }
            }
            else if (PositionMeters >= maximum)
            {
                PositionMeters = maximum;
                if (VelocityMetersPerSecond > 0f)
                {
                    VelocityMetersPerSecond = 0f;
                }
            }
        }
    }
}
