using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    public readonly struct PremiumDisplayCaseLightingPreset
    {
        public PremiumDisplayCaseLightingPreset(
            string id,
            string displayName,
            Color key,
            Color fill,
            Color rim,
            float keyIntensityScale,
            float fillIntensityScale,
            float rimIntensityScale)
        {
            Id = id ?? string.Empty;
            DisplayName = displayName ?? string.Empty;
            Key = key;
            Fill = fill;
            Rim = rim;
            KeyIntensityScale = keyIntensityScale;
            FillIntensityScale = fillIntensityScale;
            RimIntensityScale = rimIntensityScale;
        }

        public string Id { get; }
        public string DisplayName { get; }
        public Color Key { get; }
        public Color Fill { get; }
        public Color Rim { get; }
        public float KeyIntensityScale { get; }
        public float FillIntensityScale { get; }
        public float RimIntensityScale { get; }

        public Color ColorFor(string lightName, Color fallback)
        {
            if (ContainsRole(lightName, "Key"))
            {
                return Key;
            }
            if (ContainsRole(lightName, "Fill"))
            {
                return Fill;
            }
            if (ContainsRole(lightName, "Rim"))
            {
                return Rim;
            }
            return fallback;
        }

        public float IntensityScaleFor(string lightName)
        {
            if (ContainsRole(lightName, "Key"))
            {
                return KeyIntensityScale;
            }
            if (ContainsRole(lightName, "Fill"))
            {
                return FillIntensityScale;
            }
            if (ContainsRole(lightName, "Rim"))
            {
                return RimIntensityScale;
            }
            return 1f;
        }

        private static bool ContainsRole(string value, string role)
        {
            return !string.IsNullOrEmpty(value)
                && value.IndexOf(role, StringComparison.OrdinalIgnoreCase) >= 0;
        }
    }

    public static class PremiumDisplayCaseLightingCatalog
    {
        public const string PreferenceKey =
            "FidgetingApp.DisplayCaseLightingPreset";
        public const string DefaultId = "soft-neutral";

        private static readonly PremiumDisplayCaseLightingPreset[] presets =
        {
            new PremiumDisplayCaseLightingPreset(
                DefaultId,
                "柔白",
                new Color(1.00f, 0.94f, 0.86f),
                new Color(0.74f, 0.84f, 0.94f),
                new Color(0.58f, 0.34f, 0.40f),
                0.92f,
                0.72f,
                0.46f),
            new PremiumDisplayCaseLightingPreset(
                "rose-studio",
                "玫瑰",
                new Color(1.00f, 0.70f, 0.87f),
                new Color(0.66f, 0.80f, 1.00f),
                new Color(1.00f, 0.30f, 0.62f),
                0.78f,
                0.86f,
                0.72f),
            new PremiumDisplayCaseLightingPreset(
                "amber-gallery",
                "琥珀",
                new Color(1.00f, 0.78f, 0.54f),
                new Color(0.84f, 0.68f, 0.50f),
                new Color(1.00f, 0.45f, 0.22f),
                0.78f,
                0.82f,
                0.68f),
            new PremiumDisplayCaseLightingPreset(
                "cool-mist",
                "冷雾",
                new Color(0.70f, 0.88f, 1.00f),
                new Color(0.50f, 0.68f, 0.92f),
                new Color(0.40f, 0.54f, 1.00f),
                0.76f,
                0.88f,
                0.70f)
        };

        public static IReadOnlyList<PremiumDisplayCaseLightingPreset> Presets =>
            presets;

        public static PremiumDisplayCaseLightingPreset Resolve(string id)
        {
            for (int index = 0; index < presets.Length; index++)
            {
                if (string.Equals(
                        presets[index].Id,
                        id,
                        StringComparison.Ordinal))
                {
                    return presets[index];
                }
            }
            return presets[0];
        }
    }
}
