using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using UnityEngine;

namespace FidgetingApp.Product
{
    /// <summary>
    /// One-time, idempotent migrations for stable product identities. Visual
    /// replacements must not silently discard progression or collector state.
    /// </summary>
    public static class ProductCatalogMigration
    {
        public const string LegacyBlueModelId = "blue-classic";
        public const string PointedThreeBladeModelId = "pointed-three-blade";
        public const string GoldFourWingModelId = ProductCatalog.GoldFourWingModelId;
        public const string ConsolidatedRotorModelId = ProductCatalog.MetalThreeBladeModelId;

        public const string MigrationVersionKey =
            "fidgeting.catalog.migration.version";
        // v1: blue-classic -> pointed-three-blade.
        // v2: FDB-PREF-032 consolidation, pointed-three-blade and
        //     gold-four-wing -> metal-three-blade (max-merge, never discard).
        public const int CurrentMigrationVersion = 2;
        private const string ProgressionPrefix = "fidgeting.progression.v1.";
        private const string CollectorPrefix = "fidgeting.collector.v1.";
        private const string StickerPrefix = "fidgeting.appearance.sticker.v1.";

        private static readonly string[] ProgressionStringFields =
        {
            "experience",
            "peakRimSpeedKmh",
            "lifetimeGestures",
            "dailyGestureStamp",
            "activeInteractionSeconds",
            "lifetimeOfflineExperience"
        };

        private static readonly string[] ProgressionIntegerFields =
        {
            "assistant",
            "todayGestures"
        };

        public static void Apply()
        {
            int version = PlayerPrefs.GetInt(MigrationVersionKey, 0);
            if (version >= CurrentMigrationVersion)
            {
                return;
            }

            if (version < 1)
            {
                MigrateProgression(LegacyBlueModelId, PointedThreeBladeModelId, false);
                MigrateCollector(LegacyBlueModelId, PointedThreeBladeModelId);
                CopyStringIfDestinationMissing(
                    StickerPrefix + LegacyBlueModelId,
                    StickerPrefix + PointedThreeBladeModelId);
            }

            if (version < 2)
            {
                foreach (string retired in ProductCatalog.RetiredModelIds)
                {
                    MigrateProgression(retired, ConsolidatedRotorModelId, true);
                    MigrateCollector(retired, ConsolidatedRotorModelId);
                    CopyStringIfDestinationMissing(
                        StickerPrefix + retired,
                        StickerPrefix + ConsolidatedRotorModelId);
                }
            }

            PlayerPrefs.SetInt(MigrationVersionKey, CurrentMigrationVersion);
            PlayerPrefs.Save();
        }

        private static void MigrateProgression(
            string sourceModelId,
            string targetModelId,
            bool mergeMaximum)
        {
            foreach (string field in ProgressionStringFields)
            {
                string sourceKey = ProgressionPrefix + sourceModelId + "." + field;
                string targetKey = ProgressionPrefix + targetModelId + "." + field;
                if (mergeMaximum)
                {
                    MergeMaximumNumericString(sourceKey, targetKey);
                }
                else
                {
                    CopyStringIfDestinationMissing(sourceKey, targetKey);
                }
            }

            foreach (string field in ProgressionIntegerFields)
            {
                string sourceKey = ProgressionPrefix + sourceModelId + "." + field;
                string targetKey = ProgressionPrefix + targetModelId + "." + field;
                if (mergeMaximum)
                {
                    MergeMaximumInteger(sourceKey, targetKey);
                }
                else
                {
                    CopyIntegerIfDestinationMissing(sourceKey, targetKey);
                }
            }

            ReplaceExactValue(
                ProgressionPrefix + "activeModel",
                sourceModelId,
                targetModelId);
            ReplaceExactValue(
                ProgressionPrefix + "suspendedModel",
                sourceModelId,
                targetModelId);
        }

        private static void MigrateCollector(string sourceModelId, string targetModelId)
        {
            ReplaceExactValue(
                CollectorPrefix + "focusModel",
                sourceModelId,
                targetModelId);
            ReplaceSetValue(
                CollectorPrefix + "discoveredModels",
                value => value == sourceModelId ? targetModelId : value);
            ReplaceSetValue(
                CollectorPrefix + "awardedToyMilestones",
                value => ReplaceModelPrefix(value, sourceModelId, targetModelId));
            ReplaceSetValue(
                CollectorPrefix + "collectedCosmetics",
                value => ReplaceModelPrefix(value, sourceModelId, targetModelId));
            ReplaceLevelMap(
                CollectorPrefix + "highestToyLevels",
                sourceModelId,
                targetModelId);
        }

        private static void CopyStringIfDestinationMissing(string sourceKey, string targetKey)
        {
            if (!PlayerPrefs.HasKey(targetKey) && PlayerPrefs.HasKey(sourceKey))
            {
                PlayerPrefs.SetString(targetKey, PlayerPrefs.GetString(sourceKey));
            }
        }

        private static void CopyIntegerIfDestinationMissing(string sourceKey, string targetKey)
        {
            if (!PlayerPrefs.HasKey(targetKey) && PlayerPrefs.HasKey(sourceKey))
            {
                PlayerPrefs.SetInt(targetKey, PlayerPrefs.GetInt(sourceKey));
            }
        }

        /// <summary>
        /// Consolidating several toys into one must not lose the best run on
        /// any of them. Numeric strings keep the larger value; non-numeric
        /// strings (date stamps) only fill a missing destination.
        /// </summary>
        private static void MergeMaximumNumericString(string sourceKey, string targetKey)
        {
            if (!PlayerPrefs.HasKey(sourceKey))
            {
                return;
            }

            string source = PlayerPrefs.GetString(sourceKey);
            if (!PlayerPrefs.HasKey(targetKey))
            {
                PlayerPrefs.SetString(targetKey, source);
                return;
            }

            string target = PlayerPrefs.GetString(targetKey);
            if (double.TryParse(
                    source,
                    NumberStyles.Float,
                    CultureInfo.InvariantCulture,
                    out double sourceValue)
                && double.TryParse(
                    target,
                    NumberStyles.Float,
                    CultureInfo.InvariantCulture,
                    out double targetValue)
                && sourceValue > targetValue)
            {
                PlayerPrefs.SetString(targetKey, source);
            }
        }

        private static void MergeMaximumInteger(string sourceKey, string targetKey)
        {
            if (!PlayerPrefs.HasKey(sourceKey))
            {
                return;
            }

            int source = PlayerPrefs.GetInt(sourceKey);
            if (!PlayerPrefs.HasKey(targetKey) || source > PlayerPrefs.GetInt(targetKey))
            {
                PlayerPrefs.SetInt(targetKey, source);
            }
        }

        private static void ReplaceExactValue(
            string key,
            string sourceModelId,
            string targetModelId)
        {
            if (PlayerPrefs.GetString(key, string.Empty) == sourceModelId)
            {
                PlayerPrefs.SetString(key, targetModelId);
            }
        }

        private static void ReplaceSetValue(string key, Func<string, string> replace)
        {
            if (!PlayerPrefs.HasKey(key))
            {
                return;
            }

            IEnumerable<string> values = PlayerPrefs.GetString(key, string.Empty)
                .Split(new[] { '|' }, StringSplitOptions.RemoveEmptyEntries)
                .Select(replace)
                .Distinct(StringComparer.Ordinal)
                .OrderBy(value => value, StringComparer.Ordinal);
            PlayerPrefs.SetString(key, string.Join("|", values));
        }

        private static void ReplaceLevelMap(
            string key,
            string sourceModelId,
            string targetModelId)
        {
            if (!PlayerPrefs.HasKey(key))
            {
                return;
            }

            var levels = new Dictionary<string, int>(StringComparer.Ordinal);
            foreach (string row in PlayerPrefs.GetString(key, string.Empty).Split(
                         new[] { '|' },
                         StringSplitOptions.RemoveEmptyEntries))
            {
                int separator = row.LastIndexOf('@');
                if (separator <= 0
                    || !int.TryParse(
                        row.Substring(separator + 1),
                        NumberStyles.Integer,
                        CultureInfo.InvariantCulture,
                        out int level))
                {
                    continue;
                }

                string modelId = row.Substring(0, separator);
                if (modelId == sourceModelId)
                {
                    modelId = targetModelId;
                }
                levels.TryGetValue(modelId, out int current);
                levels[modelId] = Math.Max(current, level);
            }

            PlayerPrefs.SetString(
                key,
                string.Join(
                    "|",
                    levels.OrderBy(pair => pair.Key, StringComparer.Ordinal)
                        .Select(pair => pair.Key + "@"
                            + pair.Value.ToString(CultureInfo.InvariantCulture))));
        }

        private static string ReplaceModelPrefix(
            string value,
            string sourceModelId,
            string targetModelId)
        {
            if (value == sourceModelId)
            {
                return targetModelId;
            }

            string prefix = sourceModelId + "@";
            if (value.StartsWith(prefix, StringComparison.Ordinal))
            {
                return targetModelId + value.Substring(sourceModelId.Length);
            }

            prefix = sourceModelId + ":";
            return value.StartsWith(prefix, StringComparison.Ordinal)
                ? targetModelId + value.Substring(sourceModelId.Length)
                : value;
        }
    }
}
