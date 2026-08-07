namespace FidgetingApp.EDC
{
    public readonly struct MagneticEdgeProbeResult
    {
        public MagneticEdgeProbeResult(bool shouldEmit, int milestoneIndex, float signal)
        {
            ShouldEmit = shouldEmit;
            MilestoneIndex = milestoneIndex;
            NormalizedSignal = UnityEngine.Mathf.Clamp01(signal);
        }

        public bool ShouldEmit { get; }
        public int MilestoneIndex { get; }
        public float NormalizedSignal { get; }
        public static MagneticEdgeProbeResult None => new(false, -1, 0f);
    }

    /// <summary>
    /// Converts spatial load milestones into at-most-once edge cues. Time and
    /// touch duration are deliberately absent, so holding still can never
    /// retrigger or extend a haptic.
    /// </summary>
    public sealed class MagneticEdgeProbeSequence
    {
        private int direction;
        private int nextMilestoneIndex;

        public MagneticEdgeProbeResult Step(
            float normalizedLoad,
            int loadDirection,
            bool active,
            LinearMagneticDetentProfile profile)
        {
            if (profile == null)
            {
                Reset();
                return MagneticEdgeProbeResult.None;
            }

            float load = UnityEngine.Mathf.Clamp01(normalizedLoad);
            if (load <= profile.EdgeProbeRearmLoad)
            {
                nextMilestoneIndex = 0;
            }
            int resolvedDirection = System.Math.Sign(loadDirection);
            if (!active || resolvedDirection == 0)
            {
                return MagneticEdgeProbeResult.None;
            }

            if (resolvedDirection != direction)
            {
                direction = resolvedDirection;
                nextMilestoneIndex = 0;
            }

            int crossedIndex = -1;
            while (nextMilestoneIndex < profile.EdgeProbeLoads.Count
                && load >= profile.EdgeProbeLoads[nextMilestoneIndex])
            {
                crossedIndex = nextMilestoneIndex;
                nextMilestoneIndex++;
            }
            if (crossedIndex < 0)
            {
                return MagneticEdgeProbeResult.None;
            }

            float signal = profile.EdgeProbeLoads.Count <= 1
                ? 1f
                : crossedIndex / (float)(profile.EdgeProbeLoads.Count - 1);
            return new MagneticEdgeProbeResult(true, crossedIndex, signal);
        }

        public void Reset()
        {
            direction = 0;
            nextMilestoneIndex = 0;
        }
    }

    public static class EdcSliderMotion
    {
        // Only used if the active camera cannot project the physical 68 mm
        // track. Travel and capture are owned by LinearMagneticDetentProfile.
        public const float ScreenTravelFallbackFactor = 0.60f;
    }
}
