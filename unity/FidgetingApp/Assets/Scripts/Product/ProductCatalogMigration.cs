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

        private const string MigrationVersionKey =
            "fidgeting.catalog.migration.version";
        private const int CurrentMigrationVersion = 1;
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
            if (PlayerPrefs.GetInt(MigrationVersionKey, 0) >= CurrentMigrationVersion)
            {
                return;
            }

            MigrateProgression(LegacyBlueModelId, PointedThreeBladeModelId);
            MigrateCollector(LegacyBlueModelId, PointedThreeBladeModelId);
            CopyStringIfDestinationMissing(
                StickerPrefix + LegacyBlueModelId,
                StickerPrefix + PointedThreeBladeModelId);
            PlayerPrefs.SetInt(MigrationVersionKey, CurrentMigrationVersion);
            PlayerPrefs.Save();
        }

        private static void MigrateProgression(string sourceModelId, string targetModelId)
        {
            foreach (string field in ProgressionStringFields)
            {
                CopyStringIfDestinationMissing(
                    ProgressionPrefix + sourceModelId + "." + field,
                    ProgressionPrefix + targetModelId + "." + field);
            }

            foreach (string field in ProgressionIntegerFields)
            {
                CopyIntegerIfDestinationMissing(
                    ProgressionPrefix + sourceModelId + "." + field,
                    ProgressionPrefix + targetModelId + "." + field);
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
            ReplaceStringMapKey(
                CollectorPrefix + "firstDiscoveredDates",
                sourceModelId,
                targetModelId);
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

        private static void ReplaceStringMapKey(
            string key,
            string sourceModelId,
            string targetModelId)
        {
            if (!PlayerPrefs.HasKey(key))
            {
                return;
            }

            var values = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (string row in PlayerPrefs.GetString(key, string.Empty).Split(
                         new[] { '|' },
                         StringSplitOptions.RemoveEmptyEntries))
            {
                int separator = row.IndexOf('=');
                if (separator <= 0 || separator >= row.Length - 1)
                {
                    continue;
                }
                string modelId = row.Substring(0, separator);
                string value = row.Substring(separator + 1);
                if (modelId == sourceModelId)
                {
                    modelId = targetModelId;
                }
                if (!values.ContainsKey(modelId))
                {
                    values[modelId] = value;
                }
            }

            PlayerPrefs.SetString(
                key,
                string.Join(
                    "|",
                    values.OrderBy(pair => pair.Key, StringComparer.Ordinal)
                        .Select(pair => pair.Key + "=" + pair.Value)));
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
