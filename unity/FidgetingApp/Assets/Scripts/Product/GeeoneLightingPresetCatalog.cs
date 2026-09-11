using System;
using System.Collections.Generic;
using UnityEngine;

namespace FidgetingApp.Product
{
    /// <summary>
    /// One GEEONE (metal-three-blade) lighting recipe. The controller applies
    /// the same preset in library and detail, so a preset changes the whole
    /// product look, never one pose.
    ///
    /// What each lever does on this product (metallic 1.0 satin/polished steel,
    /// verified by ablation renders of the shipping scene, 2026-09-09):
    /// - <see cref="VisibilityFillIntensity"/>: camera-aligned directional fill.
    ///   Largest single contributor; every facet facing the phone gets it, so a
    ///   high value flattens the blades into one white plateau.
    /// - Key/WarmRim/CoolFill floors: the three authored spots. They carve the
    ///   facets and give the relief its shadow side.
    /// - <see cref="AmbientBoost"/> / <see cref="AmbientFloorScale"/>: only the
    ///   non-metal parts (dark rings, insets, ledge) respond; steel ignores it.
    /// - <see cref="DirectLightBoost"/> / <see cref="ReflectionBoost"/>: kept for
    ///   the softened authored intensities, but the floors above win on GEEONE.
    /// - <see cref="StudioSoftboxIntensity"/>: the only "large soft source";
    ///   adding it while cutting the spots is what reads as softbox metal.
    /// - Key/WarmRim/CoolFill values are the spots' final intensities on GEEONE.
    /// </summary>
    public readonly struct GeeoneLightingPreset
    {
        public GeeoneLightingPreset(
            string id,
            string displayName,
            float directLightBoost,
            float reflectionBoost,
            float ambientBoost,
            float visibilityFillIntensity,
            float ambientFloorScale,
            float keyLightFloor,
            float warmRimLightFloor,
            float coolFillLightFloor,
            float studioSoftboxIntensity)
        {
            Id = id;
            DisplayName = displayName;
            DirectLightBoost = directLightBoost;
            ReflectionBoost = reflectionBoost;
            AmbientBoost = ambientBoost;
            VisibilityFillIntensity = visibilityFillIntensity;
            AmbientFloorScale = ambientFloorScale;
            KeyLightFloor = keyLightFloor;
            WarmRimLightFloor = warmRimLightFloor;
            CoolFillLightFloor = coolFillLightFloor;
            StudioSoftboxIntensity = studioSoftboxIntensity;
        }

        public string Id { get; }
        public string DisplayName { get; }
        public float DirectLightBoost { get; }
        public float ReflectionBoost { get; }
        public float AmbientBoost { get; }
        public float VisibilityFillIntensity { get; }
        public float AmbientFloorScale { get; }
        public float KeyLightFloor { get; }
        public float WarmRimLightFloor { get; }
        public float CoolFillLightFloor { get; }
        /// <summary>
        /// Intensity of a broad studio softbox added to the reflection cubemap
        /// (0 = today's near-black canyon only). This is the only large soft
        /// source available to metallic 1.0 steel; it replaces hot spot lobes
        /// with a wide even sheen. Rebuilt on Configure.
        /// </summary>
        public float StudioSoftboxIntensity { get; }

        /// <summary>Sum of the four lights that reach the steel; a quick "how bright" number.</summary>
        public float TotalDirectEnergy =>
            VisibilityFillIntensity + KeyLightFloor + WarmRimLightFloor + CoolFillLightFloor;
    }

    /// <summary>
    /// GEEONE lighting presets. <see cref="Shipping"/> is the recipe that ships;
    /// the others exist for side-by-side user review and are only activated by
    /// editor preview captures. The active preset is restored after a capture.
    /// </summary>
    public static class GeeoneLightingPresetCatalog
    {
        public const string SoftStudioId = "soft-studio";
        public const string StudioBrightId = "studio-bright";
        public const string OvercastId = "overcast-diffuse";
        public const string LowKeyId = "low-key-metal";
        /// <summary>
        /// User 2026-09-09 18:07 "我感觉柔光棚好看一点" on the mobile-HDR
        /// simulator sheet (r004): Soft Studio ships.
        /// </summary>
        public const string ShippingId = SoftStudioId;

        /// <summary>
        /// Spots and camera fill at ~35% of Studio Bright plus a 0.42 studio
        /// softbox. Facets stop merging into one white plane; the key side
        /// still reads brightest. Total direct energy 0.96.
        /// </summary>
        public static readonly GeeoneLightingPreset SoftStudio = new(
            SoftStudioId,
            "柔光棚（Soft Studio）",
            directLightBoost: 2.40f,
            reflectionBoost: 1.80f,
            ambientBoost: 3.20f,
            visibilityFillIntensity: 0.26f,
            ambientFloorScale: 0.95f,
            keyLightFloor: 0.30f,
            warmRimLightFloor: 0.22f,
            coolFillLightFloor: 0.18f,
            studioSoftboxIntensity: 0.42f);

        /// <summary>The recipe the runtime reads. Alias of the user-chosen preset.</summary>
        public static readonly GeeoneLightingPreset Shipping = SoftStudio;

        /// <summary>
        /// Gate 12 rev-007 recipe as accepted on device (Build 47) under the
        /// LDR mobile pipeline. Superseded 2026-09-09: under mobile HDR its
        /// highlights overexpose. Kept for A/B review only. Total direct energy 2.65.
        /// </summary>
        public static readonly GeeoneLightingPreset StudioBright = new(
            StudioBrightId,
            "旧基线（Studio Bright）",
            directLightBoost: 3.10f,
            reflectionBoost: 2.55f,
            ambientBoost: 3.40f,
            visibilityFillIntensity: 0.85f,
            ambientFloorScale: 1.00f,
            keyLightFloor: 0.72f,
            warmRimLightFloor: 0.58f,
            coolFillLightFloor: 0.50f,
            studioSoftboxIntensity: 0.00f);

        /// <summary>
        /// Softbox-led (0.62). Spots at ~20%, so the
        /// steel shades by broad gradients with no hot spot; lowest contrast,
        /// satin mid-grey, relief visible but shadows shallow.
        /// Total direct energy 0.46.
        /// </summary>
        public static readonly GeeoneLightingPreset Overcast = new(
            OvercastId,
            "阴天漫射（Overcast Diffuse）",
            directLightBoost: 1.80f,
            reflectionBoost: 1.40f,
            ambientBoost: 3.60f,
            visibilityFillIntensity: 0.14f,
            ambientFloorScale: 1.05f,
            keyLightFloor: 0.12f,
            warmRimLightFloor: 0.10f,
            coolFillLightFloor: 0.10f,
            studioSoftboxIntensity: 0.62f);

        /// <summary>
        /// Darkest and most contrasty. Camera fill nearly off, key spot at
        /// ~40%, a faint 0.15 softbox; the shadow side of each scale goes
        /// deep and the steel reads gunmetal. Total direct energy 0.50.
        /// </summary>
        public static readonly GeeoneLightingPreset LowKey = new(
            LowKeyId,
            "低调金属（Low-key Metal）",
            directLightBoost: 2.20f,
            reflectionBoost: 1.20f,
            ambientBoost: 2.40f,
            visibilityFillIntensity: 0.05f,
            ambientFloorScale: 0.75f,
            keyLightFloor: 0.30f,
            warmRimLightFloor: 0.10f,
            coolFillLightFloor: 0.05f,
            studioSoftboxIntensity: 0.15f);

        private static readonly GeeoneLightingPreset[] all =
        {
            SoftStudio,
            StudioBright,
            Overcast,
            LowKey
        };

        public static IReadOnlyList<GeeoneLightingPreset> All => all;

        /// <summary>
        /// Simulator/device review hooks (same family as the Swift
        /// `--fidgeting-preview-enter-detail-after=`): pick a preset by id and
        /// optionally scale its four direct intensities. Editor renders cannot
        /// reproduce the mobile HDR grading, so A/B must run in the real app.
        /// </summary>
        public const string PresetLaunchArgumentPrefix = "--fidgeting-preview-geeone-lighting=";
        public const string DirectScaleLaunchArgumentPrefix = "--fidgeting-preview-geeone-direct-scale=";

        private static GeeoneLightingPreset active = ResolveLaunchPreset();

        /// <summary>
        /// Preset the runtime recipe reads. Defaults to <see cref="Shipping"/>
        /// unless a preview launch argument selects another; editor captures
        /// may swap it temporarily for review renders.
        /// </summary>
        public static GeeoneLightingPreset Active => active;

        /// <summary>
        /// iOS drops process argv before Mono sees it, but `-key value` launch
        /// arguments land in NSUserDefaults, which PlayerPrefs reads. Both
        /// spellings are accepted; the `--` form serves editor/macOS runs.
        /// </summary>
        public const string PresetPlayerPrefKey = "fidgeting.preview.geeoneLighting";
        public const string DirectScalePlayerPrefKey = "fidgeting.preview.geeoneDirectScale";

        public static GeeoneLightingPreset ResolveLaunchPreset()
        {
            List<string> arguments = new(Environment.GetCommandLineArgs() ?? Array.Empty<string>());
            string presetId = PlayerPrefs.GetString(PresetPlayerPrefKey, string.Empty);
            if (!string.IsNullOrEmpty(presetId))
            {
                arguments.Add(PresetLaunchArgumentPrefix + presetId);
            }
            string directScale = PlayerPrefs.GetString(DirectScalePlayerPrefKey, string.Empty);
            if (!string.IsNullOrEmpty(directScale))
            {
                arguments.Add(DirectScaleLaunchArgumentPrefix + directScale);
            }
            return ResolveLaunchPreset(arguments.ToArray());
        }

        public static GeeoneLightingPreset ResolveLaunchPreset(string[] arguments)
        {
            GeeoneLightingPreset preset = Shipping;
            float directScale = 1f;
            if (arguments == null)
            {
                return preset;
            }
            foreach (string argument in arguments)
            {
                if (argument == null)
                {
                    continue;
                }
                if (argument.StartsWith(PresetLaunchArgumentPrefix, StringComparison.Ordinal))
                {
                    TryResolve(argument.Substring(PresetLaunchArgumentPrefix.Length), out preset);
                }
                else if (argument.StartsWith(DirectScaleLaunchArgumentPrefix, StringComparison.Ordinal)
                    && float.TryParse(
                        argument.Substring(DirectScaleLaunchArgumentPrefix.Length),
                        System.Globalization.NumberStyles.Float,
                        System.Globalization.CultureInfo.InvariantCulture,
                        out float parsed)
                    && parsed > 0f)
                {
                    directScale = parsed;
                }
            }
            return Mathf.Approximately(directScale, 1f) ? preset : ScaleDirect(preset, directScale);
        }

        public static GeeoneLightingPreset ScaleDirect(GeeoneLightingPreset preset, float scale)
        {
            return new GeeoneLightingPreset(
                preset.Id,
                preset.DisplayName,
                preset.DirectLightBoost,
                preset.ReflectionBoost,
                preset.AmbientBoost,
                preset.VisibilityFillIntensity * scale,
                preset.AmbientFloorScale,
                preset.KeyLightFloor * scale,
                preset.WarmRimLightFloor * scale,
                preset.CoolFillLightFloor * scale,
                preset.StudioSoftboxIntensity);
        }

        public static void SetActiveForPreview(GeeoneLightingPreset preset)
        {
            active = preset;
        }

        public static void ResetActive()
        {
            active = ResolveLaunchPreset();
        }

        public static bool TryResolve(string id, out GeeoneLightingPreset preset)
        {
            for (int index = 0; index < all.Length; index++)
            {
                if (string.Equals(all[index].Id, id, StringComparison.Ordinal))
                {
                    preset = all[index];
                    return true;
                }
            }

            preset = Shipping;
            return false;
        }

        public static Color ScaleFloor(Color floor, float scale)
        {
            return new Color(floor.r * scale, floor.g * scale, floor.b * scale, 1f);
        }
    }
}
