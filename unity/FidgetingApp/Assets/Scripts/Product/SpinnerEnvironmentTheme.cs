using System;
using System.Collections.Generic;

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
            bool dynamicStarfield)
        {
            Id = id;
            DisplayName = displayName;
            BackgroundResourcePath = backgroundResourcePath;
            LeftForegroundResourcePath = leftForegroundResourcePath;
            RightForegroundResourcePath = rightForegroundResourcePath;
            Saturation = saturation;
            LayeredMidground = layeredMidground;
            DynamicStarfield = dynamicStarfield;
        }

        public string Id { get; }
        public string DisplayName { get; }
        public string BackgroundResourcePath { get; }
        public string LeftForegroundResourcePath { get; }
        public string RightForegroundResourcePath { get; }
        public float Saturation { get; }
        public bool LayeredMidground { get; }
        public bool DynamicStarfield { get; }
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
        public const string CanyonId = "canyon";
        public const string CyberpunkId = "cyberpunk";
        public const string PreferenceKey = "fidgeting.environment.theme.v1";
        public const string CyberpunkBackgroundResourcePath =
            "EnvironmentBackgrounds/cyber-neon-parallax-depth-v13";

        private static readonly SpinnerEnvironmentThemeProfile[] profiles =
        {
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
            if (string.Equals(id, CyberpunkId, StringComparison.OrdinalIgnoreCase))
            {
                return CyberpunkId;
            }
            return CanyonId;
        }
    }
}
