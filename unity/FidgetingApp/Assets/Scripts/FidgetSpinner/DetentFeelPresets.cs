using System.Runtime.InteropServices;
using UnityEngine;

namespace CodexUnityLab
{
    /// <summary>
    /// The complete runtime detent tuning surface. Detent count belongs to the
    /// shared mechanism setting; intensity and sharpness are final Core Haptics
    /// event values and are never multiplied by another product control.
    /// </summary>
    public readonly struct DetentFeelConfig
    {
        public DetentFeelConfig(
            int detentsPerRevolution,
            float intensity,
            float sharpness)
        {
            DetentsPerRevolution = Mathf.Clamp(detentsPerRevolution, 1, 120);
            Intensity = Mathf.Clamp01(intensity);
            Sharpness = Mathf.Clamp01(sharpness);
        }

        public int DetentsPerRevolution { get; }
        public float Intensity { get; }
        public float Sharpness { get; }
        public float SpacingDegrees => 360f / DetentsPerRevolution;

        public DetentFeelConfig WithTuning(float intensity, float sharpness)
        {
            return new DetentFeelConfig(
                DetentsPerRevolution,
                intensity,
                sharpness);
        }
    }

    public readonly struct DetentFeelPreset
    {
        public DetentFeelPreset(string name, DetentFeelConfig config)
        {
            Name = name;
            Config = config;
        }

        public string Name { get; }
        public DetentFeelConfig Config { get; }
    }

    /// <summary>
    /// Add a future preset by adding one entry to this array. Native debug UI
    /// receives the count/name/current values from this catalog at runtime.
    /// </summary>
    public static class DetentFeelPresetCatalog
    {
        public const int DefaultPresetIndex = 1;

        private static readonly DetentFeelPreset[] Presets =
        {
            new DetentFeelPreset("Vault", new DetentFeelConfig(8, 1.00f, 0.55f)),
            new DetentFeelPreset("Camera Dial", new DetentFeelConfig(12, 1.00f, 0.72f)),
            new DetentFeelPreset("Watch Bezel", new DetentFeelConfig(24, 0.85f, 0.90f)),
            new DetentFeelPreset("Silk Ratchet", new DetentFeelConfig(36, 0.60f, 1.00f))
        };

        public static int Count => Presets.Length;
        public static DetentFeelPreset Default => Presets[DefaultPresetIndex];

        public static DetentFeelPreset Get(int index)
        {
            return Presets[Mathf.Clamp(index, 0, Presets.Length - 1)];
        }

        public static int FindClosestIndexByDetentCount(int detentsPerRevolution)
        {
            int bestIndex = 0;
            int bestDistance = int.MaxValue;
            for (int index = 0; index < Presets.Length; index++)
            {
                int distance = Mathf.Abs(
                    Presets[index].Config.DetentsPerRevolution
                    - detentsPerRevolution);
                if (distance < bestDistance)
                {
                    bestDistance = distance;
                    bestIndex = index;
                }
            }
            return bestIndex;
        }
    }

    public static class DetentFeelRuntime
    {
        private static int activePresetIndex = DetentFeelPresetCatalog.DefaultPresetIndex;
        private static DetentFeelConfig activeConfig =
            DetentFeelPresetCatalog.Default.Config;

        public static int ActivePresetIndex => activePresetIndex;
        public static DetentFeelPreset ActivePreset =>
            DetentFeelPresetCatalog.Get(activePresetIndex);
        public static DetentFeelConfig ActiveConfig => activeConfig;

        public static DetentFeelConfig SelectPreset(int index)
        {
            activePresetIndex = Mathf.Clamp(
                index,
                0,
                DetentFeelPresetCatalog.Count - 1);
            activeConfig = ActivePreset.Config;
            return activeConfig;
        }

        public static DetentFeelConfig OverrideIntensity(float intensity)
        {
            activeConfig = activeConfig.WithTuning(
                intensity,
                activeConfig.Sharpness);
            return activeConfig;
        }

        public static DetentFeelConfig OverrideSharpness(float sharpness)
        {
            activeConfig = activeConfig.WithTuning(
                activeConfig.Intensity,
                sharpness);
            return activeConfig;
        }

        public static void ResetToDefault()
        {
            SelectPreset(DetentFeelPresetCatalog.DefaultPresetIndex);
        }
    }

    public static class DetentFeelDebugBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexDetentTuningReceiveState(
            int presetIndex,
            int presetCount,
            string presetName,
            int detentsPerRevolution,
            float intensity,
            float sharpness);
#endif

        public static void Publish()
        {
#if UNITY_IOS && !UNITY_EDITOR
            DetentFeelPreset preset = DetentFeelRuntime.ActivePreset;
            DetentFeelConfig config = DetentFeelRuntime.ActiveConfig;
            CodexDetentTuningReceiveState(
                DetentFeelRuntime.ActivePresetIndex,
                DetentFeelPresetCatalog.Count,
                preset.Name,
                config.DetentsPerRevolution,
                config.Intensity,
                config.Sharpness);
#endif
        }
    }
}
