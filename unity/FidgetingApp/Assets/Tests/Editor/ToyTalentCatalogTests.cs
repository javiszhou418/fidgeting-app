using System;
using System.Linq;
using FidgetingApp.Product;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;

namespace FidgetingApp.Tests.Editor
{
    /// <summary>
    /// The three innate traits are the only stat surface a player reads on a
    /// slab, so the invariants that keep them honest live here: one fixed
    /// budget, no duplicate builds, and no link to draw rarity.
    /// </summary>
    public sealed class ToyTalentCatalogTests
    {
        [Test]
        public void EveryToySpendsTheSameTalentBudget()
        {
            Assert.That(ToyTalentCatalog.Profiles, Is.Not.Empty);
            foreach (ToyTalentProfile profile in ToyTalentCatalog.Profiles)
            {
                Assert.That(profile.Total, Is.EqualTo(ToyTalentCatalog.TalentBudget), profile.ToyId);
                Assert.That(profile.IsAuthoritative, Is.True, profile.ToyId);
                foreach (ToyTalentAxis axis in Enum.GetValues(typeof(ToyTalentAxis)))
                {
                    Assert.That(
                        profile.Value(axis),
                        Is.InRange(ToyTalentCatalog.AxisMinimum, ToyTalentCatalog.AxisMaximum),
                        profile.ToyId + " " + ToyTalentCatalog.Label(axis));
                }
            }
        }

        [Test]
        public void NoTwoToysShareTheSameBuild()
        {
            string[] builds = ToyTalentCatalog.Profiles
                .Select(p => p.Spin + "/" + p.Feel + "/" + p.Craft)
                .ToArray();
            Assert.That(builds, Is.Unique);
            Assert.That(ToyTalentCatalog.Profiles.Select(p => p.ToyId).ToArray(), Is.Unique);
        }

        [Test]
        public void EveryShippingToyAndRetiredSaveResolves()
        {
            foreach (string toyId in new[]
                     {
                         "metal-three-blade", "graphite-two-lobe",
                         "magnetic-slide-tile", "magnetic-fan-card",
                         "pointed-three-blade", "gold-four-wing"
                     })
            {
                Assert.That(ToyTalentCatalog.TryResolve(toyId, out _), Is.True, toyId);
            }

            Assert.That(ToyTalentCatalog.TryResolve("no-such-toy", out _), Is.False);
            Assert.Throws<ArgumentOutOfRangeException>(() => ToyTalentCatalog.Resolve("no-such-toy"));
        }

        [Test]
        public void TraitsResolveFromTheDrawnPrizeContentReference()
        {
            GachaPrizeDefinition prize = GachaCatalog
                .ResolvePrize("canyon-heir-metal-three-blade").Value;
            Assert.That(prize.Kind, Is.EqualTo(GachaPrizeKind.Toy));
            ToyTalentProfile profile =
                ToyTalentCatalog.ResolveFromContentReference(prize.ContentReference);
            Assert.That(profile.ToyId, Is.EqualTo("metal-three-blade"));
            Assert.Throws<ArgumentException>(
                () => ToyTalentCatalog.ResolveFromContentReference("skin/anything"));
        }

        /// <summary>
        /// A fixed budget is what stops the draw from selling stats. If a
        /// rarity could raise a trait, the highest-rarity toy would win every
        /// axis; the budget makes that arithmetically impossible.
        /// </summary>
        [Test]
        public void RarityCannotBuyATraitAdvantage()
        {
            foreach (ToyTalentAxis axis in Enum.GetValues(typeof(ToyTalentAxis)))
            {
                ToyTalentProfile best = ToyTalentCatalog.Profiles
                    .OrderByDescending(p => p.Value(axis))
                    .First();
                Assert.That(
                    ToyTalentCatalog.Profiles.Any(p => p.Value(axis) < best.Value(axis)),
                    Is.True,
                    ToyTalentCatalog.Label(axis) + " must separate the toys");
                Assert.That(
                    ToyTalentCatalog.Profiles.All(p => p.Total == best.Total),
                    Is.True,
                    "leading one axis has to cost another");
            }
        }
    }
}
