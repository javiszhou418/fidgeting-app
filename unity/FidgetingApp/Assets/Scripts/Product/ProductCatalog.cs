using System;
using System.Collections.Generic;

namespace FidgetingApp.Product
{
    public enum ProductMechanismKind
    {
        Rotor = 0,
        Slider = 1,
        Fan = 2
    }

    public readonly struct ProductCatalogEntry
    {
        public ProductCatalogEntry(
            string modelId,
            string scenePath,
            ProductMechanismKind mechanism)
        {
            ModelId = modelId;
            ScenePath = scenePath;
            Mechanism = mechanism;
        }

        public string ModelId { get; }
        public string ScenePath { get; }
        public ProductMechanismKind Mechanism { get; }
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
                SpinnerEnvironmentCatalog.PointedScenePath,
                ProductMechanismKind.Rotor),
            new ProductCatalogEntry(
                MetalThreeBladeModelId,
                SpinnerEnvironmentCatalog.MetalScenePath,
                ProductMechanismKind.Rotor),
            new ProductCatalogEntry(
                GoldFourWingModelId,
                SpinnerEnvironmentCatalog.ImportedScenePath,
                ProductMechanismKind.Rotor),
            new ProductCatalogEntry(
                GraphiteTwoLobeModelId,
                SpinnerEnvironmentCatalog.TwoLobeScenePath,
                ProductMechanismKind.Rotor),
            new ProductCatalogEntry(
                MagneticSlideTileModelId,
                SpinnerEnvironmentCatalog.EdcScenePath,
                ProductMechanismKind.Slider),
            new ProductCatalogEntry(
                MagneticFanCardModelId,
                SpinnerEnvironmentCatalog.FanCardScenePath,
                ProductMechanismKind.Fan)
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

        public static ProductMechanismKind MechanismForModel(string modelId)
        {
            for (int index = 0; index < shippingEntries.Length; index++)
            {
                if (string.Equals(
                        shippingEntries[index].ModelId,
                        modelId,
                        StringComparison.Ordinal))
                {
                    return shippingEntries[index].Mechanism;
                }
            }

            return ProductMechanismKind.Rotor;
        }
    }
}
