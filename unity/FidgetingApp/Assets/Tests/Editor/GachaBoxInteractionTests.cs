using System.Collections.Generic;
using FidgetingApp.GachaBox;
using NUnit.Framework;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaBoxInteractionTests
    {
        private const int HeirloomRarity = 3;

        private static List<GachaBoxEvent> TickAndDrain(
            GachaBoxInteractionMachine machine,
            float deltaSeconds,
            float accelerationG = 0f,
            float rubArc = 0f,
            float lidDrag = 0f,
            bool lidHeld = false)
        {
            machine.Tick(deltaSeconds, accelerationG, rubArc, lidDrag, lidHeld);
            return new List<GachaBoxEvent>(machine.DrainEvents());
        }

        [Test]
        public void ZeroInputProducesNoEventsAndNoPhaseChangeEver()
        {
            var machine = new GachaBoxInteractionMachine(HeirloomRarity);
            for (int step = 0; step < 600; step++)
            {
                Assert.That(TickAndDrain(machine, 1f / 60f), Is.Empty);
            }

            Assert.That(machine.Phase, Is.EqualTo(GachaBoxPhase.Sealed));
            Assert.That(machine.Warmth, Is.Zero);
        }

        [Test]
        public void ShakeBelowEnterThresholdNeverRattles()
        {
            var machine = new GachaBoxInteractionMachine(HeirloomRarity);
            for (int step = 0; step < 120; step++)
            {
                Assert.That(TickAndDrain(machine, 1f / 60f, 0.29f), Is.Empty);
            }
        }

        [Test]
        public void ShakeEmitsTheRarityImpulseTrainWithSpacing()
        {
            var machine = new GachaBoxInteractionMachine(HeirloomRarity);
            GachaBoxRattleSignature signature =
                GachaBoxProfile.RattleSignature(HeirloomRarity);

            var received = new List<GachaBoxEvent>();
            var timestamps = new List<float>();
            float clock = 0f;
            const float dt = 0.01f;

            // One strong shake sample, then stillness while the burst drains.
            machine.Tick(dt, 0.35f, 0f, 0f, false);
            clock += dt;
            foreach (GachaBoxEvent boxEvent in machine.DrainEvents())
            {
                received.Add(boxEvent);
                timestamps.Add(clock);
            }

            for (int step = 0; step < 60; step++)
            {
                machine.Tick(dt, 0f, 0f, 0f, false);
                clock += dt;
                foreach (GachaBoxEvent boxEvent in machine.DrainEvents())
                {
                    received.Add(boxEvent);
                    timestamps.Add(clock);
                }
            }

            Assert.That(received.Count, Is.EqualTo(signature.ImpulseWeights.Length));
            for (int index = 0; index < received.Count; index++)
            {
                Assert.That(received[index].Kind,
                    Is.EqualTo(GachaBoxEventKind.RattleImpulse));
                Assert.That(received[index].Weight,
                    Is.EqualTo(signature.ImpulseWeights[index]).Within(1e-6));
            }

            for (int index = 1; index < timestamps.Count; index++)
            {
                Assert.That(timestamps[index] - timestamps[index - 1],
                    Is.EqualTo(signature.ImpulseSpacingSeconds).Within(dt + 1e-4),
                    "Impulses must follow the signature spacing.");
            }
        }

        [Test]
        public void SustainedAccelerationLatchesToASingleBurst()
        {
            var machine = new GachaBoxInteractionMachine(0);
            int impulses = 0;
            for (int step = 0; step < 300; step++)
            {
                foreach (GachaBoxEvent boxEvent in TickAndDrain(machine, 1f / 60f, 0.9f))
                {
                    if (boxEvent.Kind == GachaBoxEventKind.RattleImpulse)
                    {
                        impulses += 1;
                    }
                }
            }

            Assert.That(impulses,
                Is.EqualTo(GachaBoxProfile.RattleSignature(0).ImpulseWeights.Length),
                "Holding the box above the enter threshold must not machine-gun bursts.");
        }

        [Test]
        public void HysteresisAndCooldownGateTheNextBurst()
        {
            var machine = new GachaBoxInteractionMachine(0);
            Assert.That(TickAndDrain(machine, 0.01f, 0.5f), Has.Count.EqualTo(1));

            // Dropping below exit re-arms the latch, but the cooldown still
            // blocks an immediate second burst.
            Assert.That(TickAndDrain(machine, 0.01f, 0.05f), Is.Empty);
            Assert.That(TickAndDrain(machine, 0.01f, 0.5f), Is.Empty,
                "Cooldown must gate the burst even after the latch re-arms.");

            // After the cooldown a fresh swing rattles again.
            Assert.That(TickAndDrain(machine, GachaBoxProfile.ShakeCooldownSeconds, 0.05f),
                Is.Empty);
            Assert.That(TickAndDrain(machine, 0.01f, 0.5f), Has.Count.EqualTo(1));
        }

        [Test]
        public void RubbingWarmsToPrimedAndEmitsWarmedExactlyOnce()
        {
            var machine = new GachaBoxInteractionMachine(0);
            int warmedCount = 0;
            for (int step = 0; step < 80; step++)
            {
                foreach (GachaBoxEvent boxEvent in TickAndDrain(
                    machine, 1f / 60f, 0f, GachaBoxProfile.WarmthFullArcRadians / 60f))
                {
                    if (boxEvent.Kind == GachaBoxEventKind.Warmed)
                    {
                        warmedCount += 1;
                    }
                }
            }

            Assert.That(machine.Phase, Is.EqualTo(GachaBoxPhase.Primed));
            Assert.That(machine.Warmth, Is.EqualTo(1f));
            Assert.That(warmedCount, Is.EqualTo(1));
        }

        [Test]
        public void IdleWarmthDecaysWithTheConfiguredHalfLife()
        {
            var machine = new GachaBoxInteractionMachine(0);
            machine.Tick(0.01f, 0f, GachaBoxProfile.WarmthFullArcRadians * 0.5f, 0f, false);
            machine.DrainEvents();
            float warmed = machine.Warmth;
            Assert.That(warmed, Is.EqualTo(0.5f).Within(1e-4));

            machine.Tick(GachaBoxProfile.WarmthDecayHalfLifeSeconds, 0f, 0f, 0f, false);
            Assert.That(machine.Warmth, Is.EqualTo(warmed * 0.5f).Within(1e-4));
            Assert.That(machine.Phase, Is.EqualTo(GachaBoxPhase.Sealed));
        }

        [Test]
        public void LidIsInertUntilPrimedAndBelowBreakaway()
        {
            var machine = new GachaBoxInteractionMachine(0);
            Assert.That(TickAndDrain(machine, 0.01f, 0f, 0f, 0.9f, true), Is.Empty,
                "A sealed box must ignore lid drags entirely.");

            Prime(machine);
            Assert.That(TickAndDrain(
                machine, 0.01f, 0f, 0f,
                GachaBoxProfile.LidBreakawayThreshold - 0.01f, true),
                Is.Empty);
            Assert.That(TickAndDrain(machine, 0.01f, 0f, 0f, 0f, false), Is.Empty,
                "Releasing inside the preload zone snaps shut silently.");
        }

        [Test]
        public void BreakawayFiresOnceThenTheLidPopsOpen()
        {
            var machine = new GachaBoxInteractionMachine(0);
            Prime(machine);

            List<GachaBoxEvent> events = TickAndDrain(
                machine, 0.01f, 0f, 0f,
                GachaBoxProfile.LidBreakawayThreshold + 0.02f, true);
            Assert.That(events, Has.Count.EqualTo(1));
            Assert.That(events[0].Kind, Is.EqualTo(GachaBoxEventKind.LidBreakaway));

            // Dragging further before the pop must not re-fire breakaway.
            Assert.That(TickAndDrain(machine, 0.02f, 0f, 0f, 0.9f, true), Is.Empty);

            List<GachaBoxEvent> popped = TickAndDrain(
                machine, GachaBoxProfile.LidPopDelaySeconds, 0f, 0f, 0.9f, true);
            Assert.That(popped, Has.Count.EqualTo(1));
            Assert.That(popped[0].Kind, Is.EqualTo(GachaBoxEventKind.LidOpened));
            Assert.That(popped[0].Weight, Is.GreaterThan(0f));
            Assert.That(machine.Phase, Is.EqualTo(GachaBoxPhase.Opened));
        }

        [Test]
        public void SkipOpensSilentlyAndDeadensEverything()
        {
            var machine = new GachaBoxInteractionMachine(HeirloomRarity);
            machine.SkipToOpened();
            List<GachaBoxEvent> events = new List<GachaBoxEvent>(machine.DrainEvents());
            Assert.That(events, Has.Count.EqualTo(1));
            Assert.That(events[0].Kind, Is.EqualTo(GachaBoxEventKind.LidOpened));
            Assert.That(events[0].Weight, Is.Zero,
                "Skip is programmatic staging and must route silently.");

            machine.SkipToOpened();
            Assert.That(machine.DrainEvents(), Is.Empty, "Skip must be idempotent.");

            Assert.That(TickAndDrain(machine, 0.01f, 0.9f), Is.Empty,
                "An opened box no longer rattles.");
        }

        private static void Prime(GachaBoxInteractionMachine machine)
        {
            machine.Tick(0.01f, 0f, GachaBoxProfile.WarmthFullArcRadians, 0f, false);
            machine.DrainEvents();
            Assert.That(machine.Phase, Is.EqualTo(GachaBoxPhase.Primed));
        }
    }
}
