using System;
using System.Collections.Generic;

namespace FidgetingApp.GachaBox
{
    public enum GachaBoxPhase
    {
        Sealed = 0,
        Primed = 1,
        Opened = 2
    }

    public enum GachaBoxEventKind
    {
        RattleImpulse = 0,
        Warmed = 1,
        LidBreakaway = 2,
        LidOpened = 3
    }

    public readonly struct GachaBoxEvent
    {
        public GachaBoxEvent(GachaBoxEventKind kind, float weight)
        {
            Kind = kind;
            Weight = Math.Max(0f, weight);
        }

        public GachaBoxEventKind Kind { get; }
        public float Weight { get; }
    }

    /// <summary>
    /// Deterministic blind-box interaction state machine: shake to hear the
    /// rarity rattle, rub to warm the seal, then drag the lid through a
    /// preload to breakaway and pop. Pure C# — no UnityEngine, no physics
    /// writes, no direct haptic calls. Time only advances through Tick, and
    /// with zero input the machine emits nothing forever.
    /// </summary>
    public sealed class GachaBoxInteractionMachine
    {
        private readonly GachaBoxRattleSignature rattle;
        private readonly Queue<GachaBoxEvent> pendingEvents = new Queue<GachaBoxEvent>();

        private GachaBoxPhase phase = GachaBoxPhase.Sealed;
        private float warmth;
        private bool warmedEmitted;
        private bool shakeLatched;
        private float shakeCooldownRemaining;
        private int burstImpulsesRemaining;
        private float burstNextImpulseIn;
        private bool breakawayEmitted;
        private float lidPopRemaining = -1f;

        public GachaBoxInteractionMachine(int rarityIndex)
        {
            rattle = GachaBoxProfile.RattleSignature(rarityIndex);
        }

        public GachaBoxPhase Phase => phase;
        public float Warmth => warmth;

        /// <summary>
        /// Advances the machine. userAccelerationG is the current user
        /// acceleration magnitude in g; rubArcRadians is the tangential arc
        /// the finger travelled this tick; lidDragNormalized is the current
        /// lid drag position (only honored while primed and held).
        /// </summary>
        public void Tick(
            float deltaSeconds,
            float userAccelerationG,
            float rubArcRadians,
            float lidDragNormalized,
            bool lidHeld)
        {
            float dt = Math.Max(0f, deltaSeconds);
            UpdateShake(dt, Math.Max(0f, userAccelerationG));
            UpdateWarmth(dt, Math.Max(0f, rubArcRadians));
            UpdateLid(dt, lidDragNormalized, lidHeld);
        }

        /// <summary>Drains every event produced since the last call.</summary>
        public IReadOnlyList<GachaBoxEvent> DrainEvents()
        {
            if (pendingEvents.Count == 0)
            {
                return Array.Empty<GachaBoxEvent>();
            }

            var drained = new List<GachaBoxEvent>(pendingEvents.Count);
            while (pendingEvents.Count > 0)
            {
                drained.Add(pendingEvents.Dequeue());
            }

            return drained;
        }

        /// <summary>
        /// Skip button: opens immediately. The LidOpened weight of zero tells
        /// the routing layer to stay silent, matching the product rule that
        /// programmatic staging never plays feedback.
        /// </summary>
        public void SkipToOpened()
        {
            if (phase == GachaBoxPhase.Opened)
            {
                return;
            }

            phase = GachaBoxPhase.Opened;
            lidPopRemaining = -1f;
            burstImpulsesRemaining = 0;
            pendingEvents.Enqueue(new GachaBoxEvent(GachaBoxEventKind.LidOpened, 0f));
        }

        private void UpdateShake(float dt, float accelerationG)
        {
            shakeCooldownRemaining = Math.Max(0f, shakeCooldownRemaining - dt);

            // Emit any impulses still scheduled from the active burst.
            if (burstImpulsesRemaining > 0)
            {
                burstNextImpulseIn -= dt;
                while (burstImpulsesRemaining > 0 && burstNextImpulseIn <= 0f)
                {
                    int index = rattle.ImpulseWeights.Length - burstImpulsesRemaining;
                    pendingEvents.Enqueue(new GachaBoxEvent(
                        GachaBoxEventKind.RattleImpulse,
                        rattle.ImpulseWeights[index]));
                    burstImpulsesRemaining -= 1;
                    burstNextImpulseIn += rattle.ImpulseSpacingSeconds;
                }
            }

            if (phase == GachaBoxPhase.Opened)
            {
                return;
            }

            if (shakeLatched)
            {
                if (accelerationG <= GachaBoxProfile.ShakeExitG)
                {
                    shakeLatched = false;
                }

                return;
            }

            if (accelerationG >= GachaBoxProfile.ShakeEnterG
                && shakeCooldownRemaining <= 0f
                && burstImpulsesRemaining == 0)
            {
                shakeLatched = true;
                shakeCooldownRemaining = GachaBoxProfile.ShakeCooldownSeconds;
                burstImpulsesRemaining = rattle.ImpulseWeights.Length;
                burstNextImpulseIn = 0f;
                if (burstImpulsesRemaining > 0)
                {
                    pendingEvents.Enqueue(new GachaBoxEvent(
                        GachaBoxEventKind.RattleImpulse,
                        rattle.ImpulseWeights[0]));
                    burstImpulsesRemaining -= 1;
                    burstNextImpulseIn = rattle.ImpulseSpacingSeconds;
                }
            }
        }

        private void UpdateWarmth(float dt, float rubArcRadians)
        {
            if (phase != GachaBoxPhase.Sealed)
            {
                return;
            }

            if (rubArcRadians > 0.0001f)
            {
                warmth += rubArcRadians / GachaBoxProfile.WarmthFullArcRadians;
            }
            else if (warmth > 0f && dt > 0f)
            {
                warmth *= (float)Math.Pow(
                    0.5,
                    dt / GachaBoxProfile.WarmthDecayHalfLifeSeconds);
            }

            if (warmth >= 1f)
            {
                warmth = 1f;
                phase = GachaBoxPhase.Primed;
                if (!warmedEmitted)
                {
                    warmedEmitted = true;
                    pendingEvents.Enqueue(new GachaBoxEvent(GachaBoxEventKind.Warmed, 0.45f));
                }
            }
        }

        private void UpdateLid(float dt, float lidDragNormalized, bool lidHeld)
        {
            if (lidPopRemaining >= 0f)
            {
                lidPopRemaining -= dt;
                if (lidPopRemaining <= 0f && phase != GachaBoxPhase.Opened)
                {
                    phase = GachaBoxPhase.Opened;
                    lidPopRemaining = -1f;
                    pendingEvents.Enqueue(new GachaBoxEvent(GachaBoxEventKind.LidOpened, 0.7f));
                }

                return;
            }

            if (phase != GachaBoxPhase.Primed || breakawayEmitted)
            {
                return;
            }

            // Below breakaway the lid is preload only: releasing snaps it
            // shut silently. Crossing the threshold while held breaks the
            // seal exactly once and schedules the pop.
            if (lidHeld && lidDragNormalized >= GachaBoxProfile.LidBreakawayThreshold)
            {
                breakawayEmitted = true;
                pendingEvents.Enqueue(new GachaBoxEvent(GachaBoxEventKind.LidBreakaway, 0.8f));
                lidPopRemaining = GachaBoxProfile.LidPopDelaySeconds;
            }
        }
    }
}
