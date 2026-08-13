using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Runtime.InteropServices;
using UnityEngine;

namespace FidgetingApp.Product
{
    public enum CollectorAchievementMetric
    {
        CompletedRhythmWeeks = 0,
        DiscoveredModels = 1,
        ToyLevel20Count = 2,
        ToyLevel100Count = 3,
        CollectedCosmetics = 4
    }

    public readonly struct CollectorAchievementDefinition
    {
        public CollectorAchievementDefinition(
            string id,
            CollectorAchievementMetric metric,
            int threshold,
            string title,
            double rewardExperience)
        {
            Id = id;
            Metric = metric;
            Threshold = Math.Max(0, threshold);
            Title = title;
            RewardExperience = Math.Max(0d, rewardExperience);
        }

        public string Id { get; }
        public CollectorAchievementMetric Metric { get; }
        public int Threshold { get; }
        public string Title { get; }
        public double RewardExperience { get; }
    }

    public readonly struct CollectorProgressionSnapshot
    {
        public CollectorProgressionSnapshot(
            int rank,
            double totalExperience,
            double rankStartExperience,
            double nextRankExperience,
            float rankProgress,
            string focusModelId,
            bool canChangeFocus,
            float globalActiveBonus,
            float focusActiveBonus,
            int validDaysInWindow,
            int completedRhythmWeeks,
            int discoveredModelCount,
            int collectedCosmeticCount,
            int unlockedAchievementCount,
            string discoveredModelPayload,
            string achievementCatalogPayload,
            int toyLevel20Count = 0,
            int toyLevel100Count = 0)
        {
            Rank = rank;
            TotalExperience = Math.Max(0d, totalExperience);
            RankStartExperience = Math.Max(0d, rankStartExperience);
            NextRankExperience = Math.Max(RankStartExperience, nextRankExperience);
            RankProgress = Mathf.Clamp01(rankProgress);
            FocusModelId = focusModelId ?? string.Empty;
            CanChangeFocus = canChangeFocus;
            GlobalActiveBonus = Mathf.Max(0f, globalActiveBonus);
            FocusActiveBonus = Mathf.Max(GlobalActiveBonus, focusActiveBonus);
            ValidDaysInWindow = Math.Max(0, validDaysInWindow);
            CompletedRhythmWeeks = Math.Max(0, completedRhythmWeeks);
            DiscoveredModelCount = Math.Max(0, discoveredModelCount);
            CollectedCosmeticCount = Math.Max(0, collectedCosmeticCount);
            UnlockedAchievementCount = Math.Max(0, unlockedAchievementCount);
            DiscoveredModelPayload = discoveredModelPayload ?? string.Empty;
            AchievementCatalogPayload = achievementCatalogPayload ?? string.Empty;
            ToyLevel20Count = Math.Max(0, toyLevel20Count);
            ToyLevel100Count = Math.Max(0, toyLevel100Count);
        }

        public int Rank { get; }
        public double TotalExperience { get; }
        public double RankStartExperience { get; }
        public double NextRankExperience { get; }
        public float RankProgress { get; }
        public string FocusModelId { get; }
        public bool CanChangeFocus { get; }
        public float GlobalActiveBonus { get; }
        public float FocusActiveBonus { get; }
        public int ValidDaysInWindow { get; }
        public int CompletedRhythmWeeks { get; }
        public int DiscoveredModelCount { get; }
        public int CollectedCosmeticCount { get; }
        public int UnlockedAchievementCount { get; }
        public string DiscoveredModelPayload { get; }
        public string AchievementCatalogPayload { get; }
        public int ToyLevel20Count { get; }
        public int ToyLevel100Count { get; }
    }

    /// <summary>
    /// Long-lived, cross-toy progression. Collector rank rewards real use and
    /// breadth without changing rotor physics, haptics, offline XP or AUTO.
    /// </summary>
    public static class CollectorProgressionRules
    {
        public const int MaximumRank = 30;
        public const double FinalExperience = 6000d;
        public const double EffectiveDayExperience = 20d;
        public const double RhythmWeekExperience = 80d;
        public const double FirstModelExperience = 40d;
        public const double CosmeticExperience = 5d;
        public const double MaximumCollectionExperience = 900d;
        public const double EffectiveDayInteractionSeconds = 60d;
        public const int EffectiveDayInteractionCount = 3;
        public const int RhythmWindowDays = 7;
        public const int RhythmRequiredDays = 5;
        public const double MaximumManualExperienceMultiplier = 1.50d;

        private const double RankCurveExponent = 1.4d;

        private static readonly int[] toyMilestoneLevels = { 5, 20, 50, 100 };
        private static readonly double[] toyMilestoneExperience = { 20d, 60d, 120d, 240d };

        private static readonly CollectorAchievementDefinition[] achievements =
        {
            new CollectorAchievementDefinition(
                "rhythm-1", CollectorAchievementMetric.CompletedRhythmWeeks,
                1, "初次成行", 5d),
            new CollectorAchievementDefinition(
                "rhythm-4", CollectorAchievementMetric.CompletedRhythmWeeks,
                4, "稳定节奏", 10d),
            new CollectorAchievementDefinition(
                "rhythm-12", CollectorAchievementMetric.CompletedRhythmWeeks,
                12, "日常相伴", 20d),
            new CollectorAchievementDefinition(
                "explore-2", CollectorAchievementMetric.DiscoveredModels,
                2, "双件轮换", 5d),
            new CollectorAchievementDefinition(
                "explore-3", CollectorAchievementMetric.DiscoveredModels,
                3, "三件轮换", 10d),
            new CollectorAchievementDefinition(
                "explore-5", CollectorAchievementMetric.DiscoveredModels,
                5, "完整轮换", 20d),
            new CollectorAchievementDefinition(
                "master-20-1", CollectorAchievementMetric.ToyLevel20Count,
                1, "首件入门", 5d),
            new CollectorAchievementDefinition(
                "master-20-3", CollectorAchievementMetric.ToyLevel20Count,
                3, "三件入门", 10d),
            new CollectorAchievementDefinition(
                "master-100-1", CollectorAchievementMetric.ToyLevel100Count,
                1, "首件完成体", 20d),
            new CollectorAchievementDefinition(
                "master-100-3", CollectorAchievementMetric.ToyLevel100Count,
                3, "多件精通", 40d),
            new CollectorAchievementDefinition(
                "collection-cosmetic-5", CollectorAchievementMetric.CollectedCosmetics,
                5, "五种外观", 5d),
            new CollectorAchievementDefinition(
                "collection-cosmetic-10", CollectorAchievementMetric.CollectedCosmetics,
                10, "十种外观", 10d),
            new CollectorAchievementDefinition(
                "collection-cosmetic-25", CollectorAchievementMetric.CollectedCosmetics,
                25, "外观藏册", 40d)
        };

        public static IReadOnlyList<int> ToyMilestoneLevels => toyMilestoneLevels;
        public static IReadOnlyList<CollectorAchievementDefinition> Achievements => achievements;

        public static double ExperienceForRank(int rank)
        {
            int clamped = Mathf.Clamp(rank, 1, MaximumRank);
            if (clamped <= 1)
            {
                return 0d;
            }

            if (clamped >= MaximumRank)
            {
                return FinalExperience;
            }

            double normalized = (clamped - 1d) / (MaximumRank - 1d);
            return FinalExperience * Math.Pow(normalized, RankCurveExponent);
        }

        public static int RankForExperience(double experience)
        {
            double clamped = Math.Max(0d, experience);
            if (clamped >= FinalExperience)
            {
                return MaximumRank;
            }

            int low = 1;
            int high = MaximumRank;
            while (low < high)
            {
                int middle = (low + high + 1) / 2;
                if (ExperienceForRank(middle) <= clamped)
                {
                    low = middle;
                }
                else
                {
                    high = middle - 1;
                }
            }

            return low;
        }

        public static float ProgressWithinRank(double experience)
        {
            int rank = RankForExperience(experience);
            if (rank >= MaximumRank)
            {
                return 1f;
            }

            double start = ExperienceForRank(rank);
            double end = ExperienceForRank(rank + 1);
            return Mathf.Clamp01((float)((Math.Max(0d, experience) - start) / (end - start)));
        }

        public static float GlobalActiveBonusForRank(int rank)
        {
            if (rank >= 30) return 0.10f;
            if (rank >= 25) return 0.09f;
            if (rank >= 20) return 0.08f;
            if (rank >= 15) return 0.06f;
            if (rank >= 10) return 0.04f;
            if (rank >= 5) return 0.02f;
            return 0f;
        }

        public static float FocusActiveBonusForRank(int rank)
        {
            if (rank >= 30) return 0.20f;
            if (rank >= 25) return 0.18f;
            if (rank >= 20) return 0.16f;
            if (rank >= 15) return 0.13f;
            if (rank >= 10) return 0.10f;
            if (rank >= 5) return 0.07f;
            return 0.05f;
        }

        public static double ResolveManualExperienceMultiplier(
            double comboMultiplier,
            double collectorBonus)
        {
            double combo = Math.Min(1.30d, Math.Max(1d, comboMultiplier));
            double bonus = Math.Min(0.20d, Math.Max(0d, collectorBonus));
            return Math.Min(MaximumManualExperienceMultiplier, combo + bonus);
        }

        public static double ToyMilestoneReward(int level)
        {
            for (int index = 0; index < toyMilestoneLevels.Length; index++)
            {
                if (toyMilestoneLevels[index] == level)
                {
                    return toyMilestoneExperience[index];
                }
            }

            return 0d;
        }
    }

    public sealed class CollectorProgressionRuntime
    {
        public const string DefaultPrefix = "fidgeting.collector.v1.";

        private readonly string prefix;
        private readonly HashSet<string> discoveredModels;
        private readonly HashSet<string> collectedCosmetics;
        private readonly HashSet<string> awardedToyMilestones;
        private readonly HashSet<string> unlockedAchievements;
        private readonly HashSet<string> validDayStamps;
        private readonly Dictionary<string, int> highestToyLevels;
        private readonly BadgeRewardLedger badgeRewards;

        private double experience;
        private double collectionExperience;
        private string focusModelId;
        private string lastFocusChangeStamp;
        private string todayStamp;
        private double todayInteractionSeconds;
        private int todayInteractionCount;
        private bool todayCredited;
        private string lastRhythmRewardStamp;
        private int completedRhythmWeeks;
        private int pendingPreviousRank;
        private int pendingBadgeUnlockCount;
        private bool initialized;
        private bool dirty;

        public CollectorProgressionRuntime(
            string fallbackFocusModelId,
            string storagePrefix = DefaultPrefix,
            BadgeRewardLedger rewardLedger = null)
        {
            prefix = string.IsNullOrEmpty(storagePrefix) ? DefaultPrefix : storagePrefix;
            badgeRewards = rewardLedger ?? new BadgeRewardLedger(
                prefix == DefaultPrefix
                    ? BadgeRewardLedger.DefaultPrefix
                    : prefix + "badges.v2.");
            experience = ReadDouble("experience");
            collectionExperience = ReadDouble("collectionExperience");
            focusModelId = PlayerPrefs.GetString(
                Key("focusModel"),
                fallbackFocusModelId ?? string.Empty);
            lastFocusChangeStamp = PlayerPrefs.GetString(Key("lastFocusChange"), string.Empty);
            todayStamp = PlayerPrefs.GetString(Key("todayStamp"), string.Empty);
            todayInteractionSeconds = ReadDouble("todayInteractionSeconds");
            todayInteractionCount = PlayerPrefs.GetInt(Key("todayInteractionCount"), 0);
            todayCredited = PlayerPrefs.GetInt(Key("todayCredited"), 0) != 0;
            lastRhythmRewardStamp = PlayerPrefs.GetString(
                Key("lastRhythmReward"),
                string.Empty);
            completedRhythmWeeks = PlayerPrefs.GetInt(Key("completedRhythmWeeks"), 0);
            initialized = PlayerPrefs.GetInt(Key("initialized"), 0) != 0;
            discoveredModels = ReadSet("discoveredModels");
            collectedCosmetics = ReadSet("collectedCosmetics");
            awardedToyMilestones = ReadSet("awardedToyMilestones");
            unlockedAchievements = ReadSet("unlockedAchievements");
            validDayStamps = ReadSet("validDays");
            highestToyLevels = ReadLevelMap("highestToyLevels");
            RefreshDay(DateTime.Now);
            MigrateLegacyAchievementClaims(DateTime.UtcNow);
            EvaluateAchievements();
        }

        public bool HasInitializedProfile => initialized;

        public CollectorProgressionSnapshot Snapshot => CreateSnapshot(DateTime.Now);

        public CollectorProgressionSnapshot SnapshotAt(DateTime localNow) =>
            CreateSnapshot(localNow);

        public void BackfillModel(string modelId, int level, bool meaningfullyUsed)
        {
            if (string.IsNullOrEmpty(modelId))
            {
                return;
            }

            if (meaningfullyUsed && discoveredModels.Add(modelId))
            {
                AddExperience(CollectorProgressionRules.FirstModelExperience);
            }

            RecordToyLevelInternal(modelId, level);
            EvaluateAchievements();
            dirty = true;
        }

        public void BackfillCosmetic(string cosmeticId)
        {
            RecordCosmeticInternal(cosmeticId);
        }

        public void CompleteBackfill()
        {
            initialized = true;
            pendingPreviousRank = 0;
            dirty = true;
            SaveIfDirty(true);
        }

        public bool RecordGesture(string modelId, DateTime? localNow = null)
        {
            DateTime now = localNow ?? DateTime.Now;
            RefreshDay(now);
            todayInteractionCount++;
            if (!string.IsNullOrEmpty(modelId) && discoveredModels.Add(modelId))
            {
                AddExperience(CollectorProgressionRules.FirstModelExperience);
            }
            TryCreditEffectiveDay(now);
            EvaluateAchievements();
            dirty = true;
            return true;
        }

        public bool RecordActivity(double interactionSeconds, DateTime? localNow = null)
        {
            double added = Math.Max(0d, interactionSeconds);
            if (added <= 0d)
            {
                return false;
            }

            DateTime now = localNow ?? DateTime.Now;
            RefreshDay(now);
            bool wasCredited = todayCredited;
            todayInteractionSeconds += added;
            TryCreditEffectiveDay(now);
            dirty = true;
            return !wasCredited && todayCredited;
        }

        public bool RecordToyLevel(string modelId, int level)
        {
            bool changed = RecordToyLevelInternal(modelId, level);
            if (changed)
            {
                EvaluateAchievements();
                dirty = true;
            }
            return changed;
        }

        public bool RecordCosmeticUnlock(string cosmeticId)
        {
            bool changed = RecordCosmeticInternal(cosmeticId);
            if (changed)
            {
                EvaluateAchievements();
            }
            return changed;
        }

        public bool SetFocusModel(string modelId, DateTime? localNow = null)
        {
            if (string.IsNullOrEmpty(modelId))
            {
                return false;
            }

            if (string.Equals(focusModelId, modelId, StringComparison.Ordinal))
            {
                return true;
            }

            DateTime now = localNow ?? DateTime.Now;
            if (!CanChangeFocus(now))
            {
                return false;
            }

            focusModelId = modelId;
            lastFocusChangeStamp = DateStamp(now);
            dirty = true;
            return true;
        }

        public float ActiveBonusForModel(string modelId)
        {
            int rank = CollectorProgressionRules.RankForExperience(experience);
            return string.Equals(modelId, focusModelId, StringComparison.Ordinal)
                ? CollectorProgressionRules.FocusActiveBonusForRank(rank)
                : CollectorProgressionRules.GlobalActiveBonusForRank(rank);
        }

        public int ConsumePendingPreviousRank()
        {
            int previous = pendingPreviousRank;
            pendingPreviousRank = 0;
            return previous;
        }

        public int ConsumePendingBadgeUnlockCount()
        {
            int count = pendingBadgeUnlockCount;
            pendingBadgeUnlockCount = 0;
            return count;
        }

        public void SaveIfDirty(bool flush)
        {
            if (dirty)
            {
                PlayerPrefs.SetString(
                    Key("experience"),
                    experience.ToString("R", CultureInfo.InvariantCulture));
                PlayerPrefs.SetString(
                    Key("collectionExperience"),
                    collectionExperience.ToString("R", CultureInfo.InvariantCulture));
                PlayerPrefs.SetString(Key("focusModel"), focusModelId ?? string.Empty);
                PlayerPrefs.SetString(Key("lastFocusChange"), lastFocusChangeStamp ?? string.Empty);
                PlayerPrefs.SetString(Key("todayStamp"), todayStamp ?? string.Empty);
                PlayerPrefs.SetString(
                    Key("todayInteractionSeconds"),
                    todayInteractionSeconds.ToString("R", CultureInfo.InvariantCulture));
                PlayerPrefs.SetInt(Key("todayInteractionCount"), todayInteractionCount);
                PlayerPrefs.SetInt(Key("todayCredited"), todayCredited ? 1 : 0);
                PlayerPrefs.SetString(
                    Key("lastRhythmReward"),
                    lastRhythmRewardStamp ?? string.Empty);
                PlayerPrefs.SetInt(Key("completedRhythmWeeks"), completedRhythmWeeks);
                PlayerPrefs.SetInt(Key("initialized"), initialized ? 1 : 0);
                WriteSet("discoveredModels", discoveredModels);
                WriteSet("collectedCosmetics", collectedCosmetics);
                WriteSet("awardedToyMilestones", awardedToyMilestones);
                WriteSet("unlockedAchievements", unlockedAchievements);
                WriteSet("validDays", validDayStamps);
                WriteLevelMap("highestToyLevels", highestToyLevels);
                badgeRewards.SaveIfDirty(false);
                dirty = false;
            }
            else
            {
                badgeRewards.SaveIfDirty(false);
            }

            if (flush)
            {
                PlayerPrefs.Save();
            }
        }

        private CollectorProgressionSnapshot CreateSnapshot(DateTime localNow)
        {
            RefreshDay(localNow);
            PruneValidDays(localNow);
            int rank = CollectorProgressionRules.RankForExperience(experience);
            double rankStart = CollectorProgressionRules.ExperienceForRank(rank);
            double nextRank = rank >= CollectorProgressionRules.MaximumRank
                ? CollectorProgressionRules.FinalExperience
                : CollectorProgressionRules.ExperienceForRank(rank + 1);
            int toyLevel20Count = highestToyLevels.Values.Count(level => level >= 20);
            int toyLevel100Count = highestToyLevels.Values.Count(level => level >= 100);
            string discoveredPayload = string.Join(
                "|",
                discoveredModels.OrderBy(value => value, StringComparer.Ordinal));
            var preliminary = new CollectorProgressionSnapshot(
                rank,
                experience,
                rankStart,
                nextRank,
                CollectorProgressionRules.ProgressWithinRank(experience),
                focusModelId,
                CanChangeFocus(localNow),
                CollectorProgressionRules.GlobalActiveBonusForRank(rank),
                CollectorProgressionRules.FocusActiveBonusForRank(rank),
                validDayStamps.Count,
                completedRhythmWeeks,
                discoveredModels.Count,
                collectedCosmetics.Count,
                0,
                discoveredPayload,
                string.Empty,
                toyLevel20Count,
                toyLevel100Count);
            int unlockedBadgeCount = BadgeCatalogV2.UnlockedCollectorCount(preliminary);
            string achievementPayload = BadgeCatalogV2.CollectorCatalogJson(
                preliminary,
                badgeRewards);
            return new CollectorProgressionSnapshot(
                rank,
                experience,
                rankStart,
                nextRank,
                CollectorProgressionRules.ProgressWithinRank(experience),
                focusModelId,
                CanChangeFocus(localNow),
                CollectorProgressionRules.GlobalActiveBonusForRank(rank),
                CollectorProgressionRules.FocusActiveBonusForRank(rank),
                validDayStamps.Count,
                completedRhythmWeeks,
                discoveredModels.Count,
                collectedCosmetics.Count,
                unlockedBadgeCount,
                discoveredPayload,
                achievementPayload,
                toyLevel20Count,
                toyLevel100Count);
        }

        private bool RecordToyLevelInternal(string modelId, int level)
        {
            if (string.IsNullOrEmpty(modelId))
            {
                return false;
            }

            int clamped = Mathf.Clamp(level, 1, SpinnerProgressionRules.MaximumLevel);
            highestToyLevels.TryGetValue(modelId, out int previous);
            if (clamped <= previous)
            {
                return false;
            }

            highestToyLevels[modelId] = clamped;
            foreach (int milestone in CollectorProgressionRules.ToyMilestoneLevels)
            {
                string key = modelId + "@" + milestone.ToString(CultureInfo.InvariantCulture);
                if (clamped >= milestone && awardedToyMilestones.Add(key))
                {
                    AddExperience(CollectorProgressionRules.ToyMilestoneReward(milestone));
                }
            }

            return true;
        }

        private bool RecordCosmeticInternal(string cosmeticId)
        {
            if (string.IsNullOrEmpty(cosmeticId) || !collectedCosmetics.Add(cosmeticId))
            {
                return false;
            }

            double remaining = Math.Max(
                0d,
                CollectorProgressionRules.MaximumCollectionExperience - collectionExperience);
            double reward = Math.Min(CollectorProgressionRules.CosmeticExperience, remaining);
            collectionExperience += reward;
            AddExperience(reward);
            dirty = true;
            return true;
        }

        private void TryCreditEffectiveDay(DateTime localNow)
        {
            if (todayCredited
                || todayInteractionSeconds
                    < CollectorProgressionRules.EffectiveDayInteractionSeconds
                || todayInteractionCount
                    < CollectorProgressionRules.EffectiveDayInteractionCount)
            {
                return;
            }

            todayCredited = true;
            validDayStamps.Add(DateStamp(localNow));
            AddExperience(CollectorProgressionRules.EffectiveDayExperience);
            PruneValidDays(localNow);
            TryAwardRhythmWeek(localNow);
            EvaluateAchievements();
        }

        private void TryAwardRhythmWeek(DateTime localNow)
        {
            if (validDayStamps.Count < CollectorProgressionRules.RhythmRequiredDays)
            {
                return;
            }

            DateTime lastReward;
            bool hasLastReward = TryParseDate(lastRhythmRewardStamp, out lastReward);
            if (hasLastReward && (localNow.Date - lastReward.Date).TotalDays < 7d)
            {
                return;
            }

            completedRhythmWeeks++;
            lastRhythmRewardStamp = DateStamp(localNow);
            AddExperience(CollectorProgressionRules.RhythmWeekExperience);
        }

        private void EvaluateAchievements()
        {
            CollectorProgressionSnapshot snapshot = CreateMetricSnapshot();
            foreach (BadgeDefinition definition in BadgeCatalogV2.CollectorDefinitions)
            {
                if (!BadgeCatalogV2.IsCollectorUnlocked(snapshot, definition))
                {
                    continue;
                }

                string claimKey = BadgeRewardLedger.CollectorClaimKey(definition.Id);
                if (badgeRewards.TryClaim(
                        claimKey,
                        definition,
                        DateTime.UtcNow,
                        reward => AddExperience(reward)))
                {
                    pendingBadgeUnlockCount++;
                    dirty = true;
                }
            }
        }

        private CollectorProgressionSnapshot CreateMetricSnapshot()
        {
            int rank = CollectorProgressionRules.RankForExperience(experience);
            return new CollectorProgressionSnapshot(
                rank,
                experience,
                CollectorProgressionRules.ExperienceForRank(rank),
                rank >= CollectorProgressionRules.MaximumRank
                    ? CollectorProgressionRules.FinalExperience
                    : CollectorProgressionRules.ExperienceForRank(rank + 1),
                CollectorProgressionRules.ProgressWithinRank(experience),
                focusModelId,
                true,
                CollectorProgressionRules.GlobalActiveBonusForRank(rank),
                CollectorProgressionRules.FocusActiveBonusForRank(rank),
                validDayStamps.Count,
                completedRhythmWeeks,
                discoveredModels.Count,
                collectedCosmetics.Count,
                0,
                string.Empty,
                string.Empty,
                highestToyLevels.Values.Count(level => level >= 20),
                highestToyLevels.Values.Count(level => level >= 100));
        }

        private void MigrateLegacyAchievementClaims(DateTime utcNow)
        {
            foreach (CollectorAchievementDefinition legacy
                     in CollectorProgressionRules.Achievements)
            {
                if (!unlockedAchievements.Contains(legacy.Id))
                {
                    continue;
                }

                BadgeMetric metric = MapLegacyMetric(legacy.Metric);
                BadgeDefinition replacement = BadgeCatalogV2.CollectorDefinitions
                    .FirstOrDefault(candidate => candidate.Metric == metric
                        && Math.Abs(candidate.Threshold - legacy.Threshold) < 0.001d);
                if (string.IsNullOrEmpty(replacement.Id))
                {
                    continue;
                }

                badgeRewards.MarkClaimed(
                    BadgeRewardLedger.CollectorClaimKey(replacement.Id),
                    utcNow);
            }
        }

        private static BadgeMetric MapLegacyMetric(CollectorAchievementMetric metric)
        {
            switch (metric)
            {
                case CollectorAchievementMetric.CompletedRhythmWeeks:
                    return BadgeMetric.CompletedRhythmWeeks;
                case CollectorAchievementMetric.DiscoveredModels:
                    return BadgeMetric.DiscoveredModels;
                case CollectorAchievementMetric.ToyLevel20Count:
                    return BadgeMetric.ToyLevel20Count;
                case CollectorAchievementMetric.ToyLevel100Count:
                    return BadgeMetric.ToyLevel100Count;
                case CollectorAchievementMetric.CollectedCosmetics:
                    return BadgeMetric.CollectedCosmetics;
                default:
                    return BadgeMetric.CompletedRhythmWeeks;
            }
        }

        private void AddExperience(double amount)
        {
            if (amount <= 0d)
            {
                return;
            }

            int previousRank = CollectorProgressionRules.RankForExperience(experience);
            experience = Math.Min(
                CollectorProgressionRules.FinalExperience,
                Math.Max(0d, experience + amount));
            int newRank = CollectorProgressionRules.RankForExperience(experience);
            if (newRank > previousRank && pendingPreviousRank == 0)
            {
                pendingPreviousRank = previousRank;
            }
            dirty = true;
        }

        private void RefreshDay(DateTime localNow)
        {
            string stamp = DateStamp(localNow);
            if (todayStamp == stamp)
            {
                return;
            }

            todayStamp = stamp;
            todayInteractionSeconds = 0d;
            todayInteractionCount = 0;
            todayCredited = false;
            PruneValidDays(localNow);
            dirty = true;
        }

        private void PruneValidDays(DateTime localNow)
        {
            DateTime firstAllowed = localNow.Date.AddDays(
                -(CollectorProgressionRules.RhythmWindowDays - 1));
            validDayStamps.RemoveWhere(stamp =>
            {
                if (!TryParseDate(stamp, out DateTime date))
                {
                    return true;
                }
                return date.Date < firstAllowed || date.Date > localNow.Date;
            });
        }

        private bool CanChangeFocus(DateTime localNow)
        {
            return !string.Equals(
                lastFocusChangeStamp,
                DateStamp(localNow),
                StringComparison.Ordinal);
        }

        private string Key(string suffix)
        {
            return prefix + suffix;
        }

        private double ReadDouble(string suffix)
        {
            double.TryParse(
                PlayerPrefs.GetString(Key(suffix), "0"),
                NumberStyles.Float,
                CultureInfo.InvariantCulture,
                out double value);
            return Math.Max(0d, value);
        }

        private HashSet<string> ReadSet(string suffix)
        {
            string payload = PlayerPrefs.GetString(Key(suffix), string.Empty);
            return new HashSet<string>(
                payload.Split(
                    new[] { '|' },
                    StringSplitOptions.RemoveEmptyEntries),
                StringComparer.Ordinal);
        }

        private Dictionary<string, int> ReadLevelMap(string suffix)
        {
            var result = new Dictionary<string, int>(StringComparer.Ordinal);
            string payload = PlayerPrefs.GetString(Key(suffix), string.Empty);
            foreach (string row in payload.Split(
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
                result[row.Substring(0, separator)] = level;
            }
            return result;
        }

        private void WriteSet(string suffix, IEnumerable<string> values)
        {
            PlayerPrefs.SetString(
                Key(suffix),
                string.Join("|", values.OrderBy(value => value, StringComparer.Ordinal)));
        }

        private void WriteLevelMap(string suffix, Dictionary<string, int> values)
        {
            PlayerPrefs.SetString(
                Key(suffix),
                string.Join(
                    "|",
                    values.OrderBy(pair => pair.Key, StringComparer.Ordinal)
                        .Select(pair => pair.Key + "@"
                            + pair.Value.ToString(CultureInfo.InvariantCulture))));
        }

        private static string DateStamp(DateTime localNow)
        {
            return localNow.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
        }

        private static bool TryParseDate(string stamp, out DateTime date)
        {
            return DateTime.TryParseExact(
                stamp,
                "yyyy-MM-dd",
                CultureInfo.InvariantCulture,
                DateTimeStyles.None,
                out date);
        }
    }

    public static class CollectorProgressionNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexCollectorReceiveState(
            int rank,
            float totalExperience,
            float rankStartExperience,
            float nextRankExperience,
            float rankProgress,
            string focusModelId,
            int canChangeFocus,
            float globalActiveBonus,
            float focusActiveBonus,
            int validDaysInWindow,
            int completedRhythmWeeks,
            int discoveredModelCount,
            int collectedCosmeticCount,
            int unlockedAchievementCount,
            int totalAchievementCount,
            string discoveredModelPayload,
            string achievementCatalogPayload,
            int previousRank);
#endif

        public static void Publish(CollectorProgressionSnapshot snapshot, int previousRank)
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexCollectorReceiveState(
                snapshot.Rank,
                (float)snapshot.TotalExperience,
                (float)snapshot.RankStartExperience,
                (float)snapshot.NextRankExperience,
                snapshot.RankProgress,
                snapshot.FocusModelId,
                snapshot.CanChangeFocus ? 1 : 0,
                snapshot.GlobalActiveBonus,
                snapshot.FocusActiveBonus,
                snapshot.ValidDaysInWindow,
                snapshot.CompletedRhythmWeeks,
                snapshot.DiscoveredModelCount,
                snapshot.CollectedCosmeticCount,
                snapshot.UnlockedAchievementCount,
                BadgeCatalogV2.CollectorDefinitions.Count,
                snapshot.DiscoveredModelPayload,
                snapshot.AchievementCatalogPayload,
                previousRank);
#endif
        }
    }
}
