using System;
using System.Collections.Generic;

namespace FidgetingApp.Product
{
    public readonly struct ProductCatalogEntry
    {
        public ProductCatalogEntry(string modelId, string scenePath)
        {
            ModelId = modelId;
            ScenePath = scenePath;
        }

        public string ModelId { get; }
        public string ScenePath { get; }
    }

    /// <summary>
    /// Shipping model order and scene ownership. Experimental scenes can stay
    /// in source control without silently entering the Release catalog.
    /// </summary>
    public static class ProductCatalog
    {
        public const string PointedThreeBladeModelId = "pointed-three-blade";
        public const string MetalThreeBladeModelId = "metal-three-blade";
        public const string GoldFourWingModelId = "gold-four-wing";
        public const string GraphiteTwoLobeModelId = "graphite-two-lobe";
        public const string MagneticSlideTileModelId = "magnetic-slide-tile";
        public const string MagneticFanCardModelId = "magnetic-fan-card";

        private static readonly ProductCatalogEntry[] shippingEntries =
        {
            new ProductCatalogEntry(
                PointedThreeBladeModelId,
                SpinnerEnvironmentCatalog.PointedScenePath),
            new ProductCatalogEntry(
                MetalThreeBladeModelId,
                SpinnerEnvironmentCatalog.MetalScenePath),
            new ProductCatalogEntry(
                GoldFourWingModelId,
                SpinnerEnvironmentCatalog.ImportedScenePath),
            new ProductCatalogEntry(
                GraphiteTwoLobeModelId,
                SpinnerEnvironmentCatalog.TwoLobeScenePath),
            new ProductCatalogEntry(
                MagneticSlideTileModelId,
                SpinnerEnvironmentCatalog.EdcScenePath),
            new ProductCatalogEntry(
                MagneticFanCardModelId,
                SpinnerEnvironmentCatalog.FanCardScenePath)
        };

        public static IReadOnlyList<ProductCatalogEntry> ShippingEntries =>
            shippingEntries;

        public static string[] ShippingScenePaths()
        {
            var result = new string[shippingEntries.Length];
            for (int index = 0; index < shippingEntries.Length; index++)
            {
                result[index] = shippingEntries[index].ScenePath;
            }
            return result;
        }

        public static string[] ShippingModelIds()
        {
            var result = new string[shippingEntries.Length];
            for (int index = 0; index < shippingEntries.Length; index++)
            {
                result[index] = shippingEntries[index].ModelId;
            }
            return result;
        }

        public static bool TryGetScenePath(string modelId, out string scenePath)
        {
            for (int index = 0; index < shippingEntries.Length; index++)
            {
                if (string.Equals(
                        shippingEntries[index].ModelId,
                        modelId,
                        StringComparison.Ordinal))
                {
                    scenePath = shippingEntries[index].ScenePath;
                    return true;
                }
            }

            scenePath = string.Empty;
            return false;
        }

        public static bool TryGetModelId(string scenePath, out string modelId)
        {
            for (int index = 0; index < shippingEntries.Length; index++)
            {
                if (string.Equals(
                        shippingEntries[index].ScenePath,
                        scenePath,
                        StringComparison.Ordinal))
                {
                    modelId = shippingEntries[index].ModelId;
                    return true;
                }
            }

            modelId = string.Empty;
            return false;
        }
    }
}
