using System;
using System.Collections.Generic;

namespace FidgetingApp.Product
{
    /// <summary>Innate trait axes printed on a Collector Slab certificate.</summary>
    public enum ToyTalentAxis
    {
        /// <summary>Peak angular velocity and how long the toy coasts.</summary>
        Spin = 0,

        /// <summary>Detent density and breakaway strength: how mechanical it feels.</summary>
        Feel = 1,

        /// <summary>How much authored appearance the toy can wear.</summary>
        Craft = 2
    }

    public readonly struct ToyTalentProfile
    {
        public ToyTalentProfile(string toyId, int spin, int feel, int craft)
        {
            ToyId = (toyId ?? string.Empty).Trim();
            Spin = spin;
            Feel = feel;
            Craft = craft;
        }

        public string ToyId { get; }
        public int Spin { get; }
        public int Feel { get; }
        public int Craft { get; }
        public int Total => Spin + Feel + Craft;

        public int Value(ToyTalentAxis axis)
        {
            return axis switch
            {
                ToyTalentAxis.Spin => Spin,
                ToyTalentAxis.Feel => Feel,
                _ => Craft
            };
        }

        public bool IsAuthoritative =>
            !string.IsNullOrEmpty(ToyId)
            && Spin >= ToyTalentCatalog.AxisMinimum
            && Feel >= ToyTalentCatalog.AxisMinimum
            && Craft >= ToyTalentCatalog.AxisMinimum
            && Spin <= ToyTalentCatalog.AxisMaximum
            && Feel <= ToyTalentCatalog.AxisMaximum
            && Craft <= ToyTalentCatalog.AxisMaximum
            && Total == ToyTalentCatalog.TalentBudget;
    }

    /// <summary>
    /// Single source of truth for the three innate trait values printed on a
    /// Collector Slab. These describe what a toy *is*, so they are fixed per
    /// model and independent of the three earned systems already shipping:
    /// per-toy Lv.1–100 XP, Collector Rank 1–30, and draw rarity. Rarity must
    /// never raise a trait, or the draw becomes a stat purchase.
    ///
    /// Every toy spends the same <see cref="TalentBudget"/>, so there is no
    /// strictly best model — picking one is a trade-off.
    /// </summary>
    public static class ToyTalentCatalog
    {
        public const int AxisMinimum = 0;
        public const int AxisMaximum = 100;

        /// <summary>Fixed talent budget: 210 of a possible 300.</summary>
        public const int TalentBudget = 210;

        public const int AxisCount = 3;

        private const string ToyReferencePrefix = "toy/";

        private static readonly string[] axisLabels = { "SPIN", "FEEL", "CRAFT" };

        private static readonly ToyTalentProfile[] profiles =
        {
            // Long satin-steel freewheel, few detents, ten authored skins.
            new ToyTalentProfile("metal-three-blade", 88, 36, 86),
            // Lighter two-lobe: quick to start, shorter coast, fewer finishes.
            new ToyTalentProfile("graphite-two-lobe", 84, 60, 66),
            // Magnetic push tile: no rotor, the strongest detent ladder we ship.
            new ToyTalentProfile("magnetic-slide-tile", 24, 96, 90),
            // Fan card: mid-speed fan-out with a hard clack at each stop.
            new ToyTalentProfile("magnetic-fan-card", 46, 88, 76),
            // Retired from the library; kept so migrated saves still resolve.
            new ToyTalentProfile("pointed-three-blade", 90, 34, 86),
            new ToyTalentProfile("gold-four-wing", 78, 52, 80)
        };

        public static IReadOnlyList<ToyTalentProfile> Profiles => profiles;

        public static string Label(ToyTalentAxis axis)
        {
            return axisLabels[(int)axis];
        }

        public static bool TryResolve(string toyId, out ToyTalentProfile profile)
        {
            string key = (toyId ?? string.Empty).Trim();
            for (int index = 0; index < profiles.Length; index++)
            {
                if (string.Equals(profiles[index].ToyId, key, StringComparison.Ordinal))
                {
                    profile = profiles[index];
                    return true;
                }
            }

            profile = default;
            return false;
        }

        public static ToyTalentProfile Resolve(string toyId)
        {
            if (!TryResolve(toyId, out ToyTalentProfile profile))
            {
                throw new ArgumentOutOfRangeException(
                    nameof(toyId),
                    toyId,
                    "No trait profile for this toy. Add one to ToyTalentCatalog.");
            }

            return profile;
        }

        /// <summary>
        /// Resolves from a <c>GachaPrizeDefinition.ContentReference</c> such as
        /// <c>toy/metal-three-blade</c>, so the printed traits and the drawn
        /// prize cannot drift apart.
        /// </summary>
        public static ToyTalentProfile ResolveFromContentReference(string contentReference)
        {
            string value = (contentReference ?? string.Empty).Trim();
            if (!value.StartsWith(ToyReferencePrefix, StringComparison.Ordinal))
            {
                throw new ArgumentException(
                    "Trait profiles resolve from a toy content reference.",
                    nameof(contentReference));
            }

            return Resolve(value.Substring(ToyReferencePrefix.Length));
        }
    }
}
