using NUnit.Framework;

namespace FidgetingApp.Editor.Prototypes.Tests
{
    public sealed class DisplayCaseRarityRevealPrototypeTests
    {
        [Test]
        public void Palette_ContainsExactlyBlueGreenPurpleGoldInRarityOrder()
        {
            CollectionAssert.AreEqual(
                new[]
                {
                    "standard-blue",
                    "refined-green",
                    "signature-purple",
                    "heirloom-gold"
                },
                DisplayCaseRarityRevealPrototype.PaletteIds);
        }

        [Test]
        public void Timeline_OrdersEveryRequestedRevealBeat()
        {
            Assert.That(
                DisplayCaseRarityRevealPrototype.SamplePhase(0.3f),
                Is.EqualTo(PrototypePhase.BackFacing));
            Assert.That(
                DisplayCaseRarityRevealPrototype.SamplePhase(1.2f),
                Is.EqualTo(PrototypePhase.FlipToFront));
            Assert.That(
                DisplayCaseRarityRevealPrototype.SamplePhase(2.2f),
                Is.EqualTo(PrototypePhase.PrizeReadable));
            Assert.That(
                DisplayCaseRarityRevealPrototype.SamplePhase(3.3f),
                Is.EqualTo(PrototypePhase.PartsExplode));
            Assert.That(
                DisplayCaseRarityRevealPrototype.SamplePhase(4.2f),
                Is.EqualTo(PrototypePhase.ExplodedHold));
            Assert.That(
                DisplayCaseRarityRevealPrototype.SamplePhase(5.2f),
                Is.EqualTo(PrototypePhase.PrizeOnlyLightPass));
            Assert.That(
                DisplayCaseRarityRevealPrototype.SamplePhase(6f),
                Is.EqualTo(PrototypePhase.Complete));
        }
    }
}
