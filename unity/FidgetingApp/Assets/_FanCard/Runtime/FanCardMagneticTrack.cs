using FidgetingApp.EDC;
using UnityEngine;

namespace FidgetingApp.FanCard
{
    public readonly struct FanCardStepResult
    {
        public FanCardStepResult(
            bool brokeAway,
            int crossedDetentCount,
            int crossingDirection,
            bool captured)
        {
            BrokeAway = brokeAway;
            CrossedDetentCount = crossedDetentCount;
            CrossingDirection = crossingDirection;
            Captured = captured;
        }

        public bool BrokeAway { get; }
        public int CrossedDetentCount { get; }
        public int CrossingDirection { get; }
        public bool Captured { get; }
    }

    /// <summary>
    /// Deterministic normalized 1D magnetic track used by the fan-card angle.
    /// Its equations and thresholds intentionally match the approved browser
    /// prototype rather than inheriting any rotary or linear-slider tuning.
    /// </summary>
    public sealed class FanCardMagneticTrack
    {
        private readonly FanCardDetentProfile profile;
        private float captureTarget;
        private float load;
        private bool captured = true;
        private int lastCrossedIndex;

        public FanCardMagneticTrack(FanCardDetentProfile profile)
        {
            this.profile = profile;
            ResetToDetent(0);
        }

        public float Position { get; private set; }
        public float Velocity { get; private set; }
        public MagneticDetentState State { get; private set; } =
            MagneticDetentState.Captured;
        public int CapturedDetentIndex { get; private set; }
        public float Load => load;
        public float LoadNormalized => Mathf.Clamp01(
            Mathf.Abs(load) / profile.BreakawayLoad);
        public bool IsAtRest => captured
            && State == MagneticDetentState.Captured
            && Mathf.Abs(Velocity) <= Mathf.Epsilon;

        public float VisualPosition
        {
            get
            {
                float preload = captured
                    ? Mathf.Clamp(
                        load,
                        -profile.BreakawayLoad,
                        profile.BreakawayLoad)
                        * profile.VisiblePreloadScale
                    : 0f;
                return Mathf.Clamp01(Position + preload);
            }
        }

        public void ResetToDetent(int index)
        {
            int clamped = Mathf.Clamp(index, 0, profile.DetentCount - 1);
            Position = clamped / (float)profile.DetentIntervals;
            Velocity = 0f;
            captureTarget = Position;
            load = 0f;
            captured = true;
            CapturedDetentIndex = clamped;
            lastCrossedIndex = clamped;
            State = MagneticDetentState.Captured;
        }

        public void ResetToPosition(float normalizedPosition)
        {
            int nearest = Mathf.RoundToInt(
                Mathf.Clamp01(normalizedPosition) * profile.DetentIntervals);
            ResetToDetent(nearest);
        }

        public void Release()
        {
            captureTarget = NearestDetent(
                Mathf.Clamp01(
                    Position + Velocity * profile.CapturePredictionSeconds));
            load = 0f;
            captured = false;
            State = MagneticDetentState.Capturing;
        }

        public FanCardStepResult Step(
            float deltaTime,
            float handTarget,
            bool handActive,
            float traversalAuthority = 0f)
        {
            bool brokeAway = false;
            int crossedCount = 0;
            int crossingDirection = 0;
            bool capturedThisStep = false;
            float remaining = Mathf.Min(
                Mathf.Max(0f, deltaTime),
                profile.MaximumFrameStepSeconds);
            float clampedTarget = Mathf.Clamp01(handTarget);
            float authority = Mathf.Clamp01(traversalAuthority);
            float breakawayLoad = Mathf.Lerp(
                profile.BreakawayLoad,
                profile.FastBreakawayLoad,
                authority);
            float breakawayImpulse = Mathf.Lerp(
                profile.BreakawayImpulse,
                profile.FastBreakawayImpulse,
                authority);
            float handSpring = Mathf.Lerp(
                profile.HandSpring,
                profile.FastHandSpring,
                authority);
            float handDamping = Mathf.Lerp(
                profile.HandDamping,
                profile.FastHandDamping,
                authority);
            float magneticScale = Mathf.Lerp(
                1f,
                profile.FastMagneticForceScale,
                authority);
            float railFriction = Mathf.Lerp(
                profile.RailFriction,
                profile.FastRailFriction,
                authority);
            float maximumHeldSpeed = Mathf.Lerp(
                profile.MaximumHeldSpeed,
                profile.FastMaximumHeldSpeed,
                authority);

            while (remaining > 0f)
            {
                float step = Mathf.Min(profile.MaximumSubstepSeconds, remaining);
                remaining -= step;

                if (captured && handActive)
                {
                    load = clampedTarget - Position;
                    Velocity = 0f;
                    if (Mathf.Abs(load) >= breakawayLoad)
                    {
                        captured = false;
                        State = MagneticDetentState.Breakaway;
                        Velocity = Mathf.Sign(load) * breakawayImpulse;
                        brokeAway = true;
                    }
                    else
                    {
                        State = Mathf.Abs(load) > 0.006f
                            ? MagneticDetentState.Loading
                            : MagneticDetentState.Captured;
                    }
                    continue;
                }

                if (captured)
                {
                    load = 0f;
                    continue;
                }

                float force;
                if (handActive)
                {
                    load = clampedTarget - Position;
                    force = handSpring * load
                        - handDamping * Velocity
                        + MagneticForce(Position) * magneticScale;
                    State = MagneticDetentState.Traveling;
                }
                else
                {
                    load = 0f;
                    force = profile.CaptureSpring * (captureTarget - Position)
                        - profile.CaptureDamping * Velocity
                        + MagneticForce(Position) * 0.30f;
                    State = MagneticDetentState.Capturing;
                }

                if (Mathf.Abs(Velocity) > 0.008f)
                {
                    force -= railFriction * Mathf.Sign(Velocity);
                }

                Velocity += force * step;
                if (handActive)
                {
                    Velocity = Mathf.Clamp(
                        Velocity,
                        -maximumHeldSpeed,
                        maximumHeldSpeed);
                }
                float previous = Position;
                Position = Mathf.Clamp01(Position + Velocity * step);
                if ((Position <= 0f && Velocity < 0f)
                    || (Position >= 1f && Velocity > 0f))
                {
                    Velocity = 0f;
                }

                int crossed = Mathf.Clamp(
                    Mathf.FloorToInt(Position * profile.DetentIntervals + 0.5f),
                    0,
                    profile.DetentIntervals);
                if (crossed != lastCrossedIndex
                    && Mathf.Abs(Position - previous) > 0.0001f)
                {
                    crossingDirection = crossed > lastCrossedIndex ? 1 : -1;
                    crossedCount += Mathf.Abs(crossed - lastCrossedIndex);
                    lastCrossedIndex = crossed;
                }

                float nearest = NearestDetent(Position);
                if (handActive)
                {
                    bool handNearWell = Mathf.Abs(clampedTarget - nearest)
                        < profile.HeldTargetError;
                    if (Mathf.Abs(Position - nearest)
                            < profile.HeldCapturePositionError
                        && Mathf.Abs(Velocity) < profile.HeldCaptureSpeed
                        && handNearWell)
                    {
                        Capture(nearest);
                        capturedThisStep = true;
                    }
                }
                else if (Mathf.Abs(Position - captureTarget)
                             < profile.ReleaseCapturePositionError
                    && Mathf.Abs(Velocity) < profile.ReleaseCaptureSpeed)
                {
                    Capture(captureTarget);
                    capturedThisStep = true;
                }
            }

            return new FanCardStepResult(
                brokeAway,
                crossedCount,
                crossingDirection,
                capturedThisStep);
        }

        private float MagneticForce(float position)
        {
            return -profile.MagneticForcePeak
                * Mathf.Sin(Mathf.PI * 2f * profile.DetentIntervals * position);
        }

        private float NearestDetent(float position)
        {
            return Mathf.Clamp(
                    Mathf.RoundToInt(position * profile.DetentIntervals),
                    0,
                    profile.DetentIntervals)
                / (float)profile.DetentIntervals;
        }

        private void Capture(float detentPosition)
        {
            Position = Mathf.Clamp01(detentPosition);
            Velocity = 0f;
            load = 0f;
            captured = true;
            CapturedDetentIndex = Mathf.RoundToInt(
                Position * profile.DetentIntervals);
            lastCrossedIndex = CapturedDetentIndex;
            State = MagneticDetentState.Captured;
        }
    }
}
