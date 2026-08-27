using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.Product
{
    public readonly struct SpinnerEnvironmentThemeProfile
    {
        public SpinnerEnvironmentThemeProfile(
            string id,
            string displayName,
            string backgroundResourcePath,
            string leftForegroundResourcePath,
            string rightForegroundResourcePath,
            float saturation,
            bool layeredMidground,
            bool dynamicStarfield,
            bool modelReactiveBackdrop = false,
            bool collageMineralPlate = false)
        {
            Id = id;
            DisplayName = displayName;
            BackgroundResourcePath = backgroundResourcePath;
            LeftForegroundResourcePath = leftForegroundResourcePath;
            RightForegroundResourcePath = rightForegroundResourcePath;
            Saturation = saturation;
            LayeredMidground = layeredMidground;
            DynamicStarfield = dynamicStarfield;
            ModelReactiveBackdrop = modelReactiveBackdrop;
            CollageMineralPlate = collageMineralPlate;
        }

        public string Id { get; }
        public string DisplayName { get; }
        public string BackgroundResourcePath { get; }
        public string LeftForegroundResourcePath { get; }
        public string RightForegroundResourcePath { get; }
        public float Saturation { get; }
        public bool LayeredMidground { get; }
        public bool DynamicStarfield { get; }
        public bool ModelReactiveBackdrop { get; }
        public bool CollageMineralPlate { get; }
        public bool HasForegroundLayers =>
            !string.IsNullOrEmpty(LeftForegroundResourcePath)
            && !string.IsNullOrEmpty(RightForegroundResourcePath);
    }

    /// <summary>
    /// Global visual theme catalog. Theme selection changes presentation-only
    /// environment resources and never writes product physics or Haptics.
    /// </summary>
    public static class SpinnerEnvironmentThemeCatalog
    {
        public const string AdaptiveId = "adaptive";
        public const string CanyonId = "canyon";
        public const string CyberpunkId = "cyberpunk";
        public const string MineralRidgeId = "mineral-ridge";
        public const string PreferenceKey = "fidgeting.environment.theme.v1";
        public const string CyberpunkBackgroundResourcePath =
            "EnvironmentBackgrounds/cyber-neon-parallax-depth-v13";
        public const string MineralRidgeBackgroundResourcePath =
            "EnvironmentBackgrounds/mineral-ridge-digital-collage-v3";

        private static readonly SpinnerEnvironmentThemeProfile[] profiles =
        {
            new SpinnerEnvironmentThemeProfile(
                AdaptiveId,
                "随形微光",
                string.Empty,
                string.Empty,
                string.Empty,
                0f,
                false,
                false,
                true),
            new SpinnerEnvironmentThemeProfile(
                CanyonId,
                "星岩峡谷",
                SpinnerEnvironmentCatalog.UnifiedBackgroundResourcePath,
                SpinnerEnvironmentPresenter.LeftForegroundResourcePath,
                SpinnerEnvironmentPresenter.RightForegroundResourcePath,
                -1f,
                false,
                true),
            new SpinnerEnvironmentThemeProfile(
                CyberpunkId,
                "霓虹都市",
                CyberpunkBackgroundResourcePath,
                string.Empty,
                string.Empty,
                0.74f,
                true,
                true),
            new SpinnerEnvironmentThemeProfile(
                MineralRidgeId,
                "矿脊台座",
                MineralRidgeBackgroundResourcePath,
                string.Empty,
                string.Empty,
                0f,
                false,
                false,
                false,
                true)
        };

        public static IReadOnlyList<SpinnerEnvironmentThemeProfile> Profiles => profiles;

        public static SpinnerEnvironmentThemeProfile Default => profiles[0];

        public static bool TryGet(
            string id,
            out SpinnerEnvironmentThemeProfile profile)
        {
            string normalized = NormalizeId(id);
            for (int index = 0; index < profiles.Length; index++)
            {
                if (string.Equals(
                        profiles[index].Id,
                        normalized,
                        StringComparison.Ordinal))
                {
                    profile = profiles[index];
                    return true;
                }
            }

            profile = Default;
            return false;
        }

        public static string NormalizeId(string id)
        {
            if (string.Equals(id, AdaptiveId, StringComparison.OrdinalIgnoreCase))
            {
                return AdaptiveId;
            }
            if (string.Equals(id, CyberpunkId, StringComparison.OrdinalIgnoreCase))
            {
                return CyberpunkId;
            }
            if (string.Equals(id, CanyonId, StringComparison.OrdinalIgnoreCase))
            {
                return CanyonId;
            }
            if (string.Equals(id, MineralRidgeId, StringComparison.OrdinalIgnoreCase))
            {
                return MineralRidgeId;
            }
            return AdaptiveId;
        }
    }

    public readonly struct SpinnerAdaptiveBackdropTransition
    {
        public SpinnerAdaptiveBackdropTransition(
            Color outgoingColor,
            Color incomingColor,
            float outgoingWeight,
            float incomingWeight,
            float outgoingCenterX,
            float incomingCenterX,
            string incomingModelId)
        {
            OutgoingColor = outgoingColor;
            IncomingColor = incomingColor;
            OutgoingWeight = outgoingWeight;
            IncomingWeight = incomingWeight;
            OutgoingCenterX = outgoingCenterX;
            IncomingCenterX = incomingCenterX;
            IncomingModelId = incomingModelId;
        }

        public Color OutgoingColor { get; }
        public Color IncomingColor { get; }
        public float OutgoingWeight { get; }
        public float IncomingWeight { get; }
        public float OutgoingCenterX { get; }
        public float IncomingCenterX { get; }
        public string IncomingModelId { get; }
    }

    /// <summary>
    /// Low-saturation identity colors used before the adjacent Unity scene is
    /// available. Once a scene is active, the lighting controller still reads
    /// the real renderer materials and blends that measured accent into the
    /// stable halo. These presets only make the in-flight page transition
    /// deterministic and never affect product materials or mechanics.
    /// </summary>
    public static class SpinnerEnvironmentAccentCatalog
    {
        public static Color Resolve(string modelId)
        {
            Color color;
            switch (modelId)
            {
                case ProductCatalog.MetalThreeBladeModelId:
                    color = new Color(0.66f, 0.54f, 0.56f, 1f);
                    break;
                case ProductCatalog.GoldFourWingModelId:
                    color = new Color(0.74f, 0.65f, 0.48f, 1f);
                    break;
                case ProductCatalog.GraphiteTwoLobeModelId:
                    color = new Color(0.45f, 0.53f, 0.49f, 1f);
                    break;
                case ProductCatalog.MagneticSlideTileModelId:
                    color = new Color(0.34f, 0.67f, 0.71f, 1f);
                    break;
                case ProductCatalog.MagneticFanCardModelId:
                    color = new Color(0.72f, 0.56f, 0.38f, 1f);
                    break;
                default:
                    color = new Color(0.56f, 0.61f, 0.68f, 1f);
                    break;
            }
            return SpinnerAdaptiveBackdropRules.Restrain(color);
        }
    }

    /// <summary>
    /// Matches the reference pager: a near-black surface stays fixed while
    /// the old and new low-frequency color fields travel with their pages.
    /// Page offset is normalized to one viewport and is signed exactly like
    /// the native drag (negative means the next product enters from the right).
    /// </summary>
    public static class SpinnerAdaptiveBackdropRules
    {
        public const float GlowCenterY = 0.57f;
        public const float GlowRadius = 0.62f;
        public const float GlowIntensity = 0.26f;
        public const float StableSecondaryWeight = 0.16f;
        public const float MaximumSaturation = 0.20f;
        public const float MaximumValue = 0.58f;
        public const float GrainIntensity = 0.012f;
        public const float TopLightBottomBrightness = 0.08f;
        public const float TopLightBottomSaturation = 0.18f;
        public const float TopLightFalloff = 1.25f;

        public static Color Restrain(Color color)
        {
            Color.RGBToHSV(color, out float hue, out float saturation, out float value);
            Color restrained = Color.HSVToRGB(
                hue,
                Mathf.Min(saturation, MaximumSaturation),
                Mathf.Min(value, MaximumValue));
            restrained.a = color.a;
            return restrained;
        }

        public static SpinnerAdaptiveBackdropTransition Resolve(
            string currentModelId,
            float signedPageOffset)
        {
            float offset = Mathf.Clamp(signedPageOffset, -1f, 1f);
            float progress = Mathf.Abs(offset);
            Color current = SpinnerEnvironmentAccentCatalog.Resolve(currentModelId);
            if (progress <= 0.0001f
                || !TryResolveAdjacentModel(
                    currentModelId,
                    offset < 0f ? 1 : -1,
                    out string adjacentModelId))
            {
                return new SpinnerAdaptiveBackdropTransition(
                    current,
                    Restrain(Color.Lerp(current, Color.white, 0.18f)),
                    1f,
                    StableSecondaryWeight,
                    0.50f,
                    0.72f,
                    currentModelId);
            }

            float direction = Mathf.Sign(offset);
            return new SpinnerAdaptiveBackdropTransition(
                current,
                SpinnerEnvironmentAccentCatalog.Resolve(adjacentModelId),
                1f - progress,
                progress,
                0.50f + offset,
                0.50f + offset - direction,
                adjacentModelId);
        }

        private static bool TryResolveAdjacentModel(
            string currentModelId,
            int indexOffset,
            out string adjacentModelId)
        {
            IReadOnlyList<ProductCatalogEntry> entries = ProductCatalog.ShippingEntries;
            for (int index = 0; index < entries.Count; index++)
            {
                if (!string.Equals(
                        entries[index].ModelId,
                        currentModelId,
                        StringComparison.Ordinal))
                {
                    continue;
                }

                int adjacentIndex = index + indexOffset;
                if (adjacentIndex >= 0 && adjacentIndex < entries.Count)
                {
                    adjacentModelId = entries[adjacentIndex].ModelId;
                    return true;
                }
                break;
            }

            adjacentModelId = currentModelId;
            return false;
        }
    }
}
