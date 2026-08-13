using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using UnityEngine;

namespace FidgetingApp.Product
{
    public enum BadgeScope
    {
        Toy = 0,
        Collector = 1,
        Challenge = 2,
        Legacy = 3
    }

    public enum BadgeCategory
    {
        Power = 0,
        Pulse = 1,
        Technique = 2,
        Combo = 3,
        Focus = 4,
        Rhythm = 5,
        Explore = 6,
        Mastery = 7,
        Collection = 8,
        Challenge = 9,
        Legacy = 10
    }

    public enum BadgeMetric
    {
        PeakPower = 0,
        LifetimeGestures = 1,
        TechniqueClean = 2,
        TechniquePower = 3,
        TechniqueSpeed = 4,
        TechniqueEndurance = 5,
        TechniquePerfect = 6,
        HighestCombo = 7,
        ActiveInteractionSeconds = 8,
        CompletedRhythmWeeks = 9,
        DiscoveredModels = 10,
        ToyLevel20Count = 11,
        ToyLevel100Count = 12,
        CollectedCosmetics = 13,
        ChallengeRedline = 14,
        ChallengeChain = 15,
        ChallengePerfect = 16,
        ChallengeRaid = 17,
        ChallengeCycle = 18,
        LegacyFounder = 19
    }

    public enum BadgeGrade
    {
        Ignition = 0,
        Overdrive = 1,
        Apex = 2,
        Singularity = 3
    }

    public enum BadgeVisibility
    {
        Standard = 0,
        Hidden = 1
    }

    public enum BadgeProgressState
    {
        Locked = 0,
        InProgress = 1,
        Hidden = 2,
        Unlocked = 3
    }

    public readonly struct BadgeDefinition
    {
        public BadgeDefinition(
            string id,
            BadgeScope scope,
            BadgeCategory category,
            ProductMechanismKind? mechanism,
            BadgeMetric metric,
            double threshold,
            BadgeGrade grade,
            BadgeVisibility visibility,
            string title,
            string description,
            string assetName,
            string displayToken,
            string displayUnit,
            string shortName,
            int displayOrder)
        {
            Id = id;
            Scope = scope;
            Category = category;
            Mechanism = mechanism;
            Metric = metric;
            Threshold = Math.Max(0d, threshold);
            Grade = grade;
            Visibility = visibility;
            Title = title ?? string.Empty;
            Description = description ?? string.Empty;
            AssetName = assetName ?? string.Empty;
            DisplayToken = displayToken ?? string.Empty;
            DisplayUnit = displayUnit ?? string.Empty;
            ShortName = shortName ?? string.Empty;
            DisplayOrder = Math.Max(0, displayOrder);
            ExperienceReward = BadgeRewardRules.ExperienceForGrade(grade);
            ShardReward = BadgeRewardRules.ShardsForGrade(grade);
        }

        public string Id { get; }
        public BadgeScope Scope { get; }
        public BadgeCategory Category { get; }
        public ProductMechanismKind? Mechanism { get; }
        public BadgeMetric Metric { get; }
        public double Threshold { get; }
        public BadgeGrade Grade { get; }
        public BadgeVisibility Visibility { get; }
        public string Title { get; }
        public string Description { get; }
        public string AssetName { get; }
        public string DisplayToken { get; }
        public string DisplayUnit { get; }
        public string ShortName { get; }
        public int ExperienceReward { get; }
        public int ShardReward { get; }
        public int DisplayOrder { get; }
    }

    public readonly struct BadgeProgressSnapshot
    {
        public BadgeProgressSnapshot(
            string id,
            double currentValue,
            double targetValue,
            BadgeProgressState state,
            string unlockedAtUtc,
            bool rewardClaimed)
        {
            Id = id ?? string.Empty;
            CurrentValue = Math.Max(0d, currentValue);
            TargetValue = Math.Max(0d, targetValue);
            State = state;
            Progress = TargetValue <= 0d
                ? (state == BadgeProgressState.Unlocked ? 1f : 0f)
                : Mathf.Clamp01((float)(CurrentValue / TargetValue));
            UnlockedAtUtc = unlockedAtUtc ?? string.Empty;
            RewardClaimed = rewardClaimed;
        }

        public string Id { get; }
        public double CurrentValue { get; }
        public double TargetValue { get; }
        public BadgeProgressState State { get; }
        public float Progress { get; }
        public string UnlockedAtUtc { get; }
        public bool RewardClaimed { get; }
    }

    public readonly struct BadgeChallengeSnapshot
    {
        public BadgeChallengeSnapshot(
            string templateId,
            long cycleIndex,
            string startsAtUtc,
            string endsAtUtc,
            double currentValue,
            double targetValue,
            bool completed,
            bool rewardClaimed)
        {
            TemplateId = templateId ?? string.Empty;
            CycleIndex = Math.Max(0L, cycleIndex);
            StartsAtUtc = startsAtUtc ?? string.Empty;
            EndsAtUtc = endsAtUtc ?? string.Empty;
            CurrentValue = Math.Max(0d, currentValue);
            TargetValue = Math.Max(0d, targetValue);
            Completed = completed;
            RewardClaimed = rewardClaimed;
        }

        public string TemplateId { get; }
        public long CycleIndex { get; }
        public string StartsAtUtc { get; }
        public string EndsAtUtc { get; }
        public double CurrentValue { get; }
        public double TargetValue { get; }
        public bool Completed { get; }
        public bool RewardClaimed { get; }
    }

    public static class BadgeRewardRules
    {
        public static int ExperienceForGrade(BadgeGrade grade)
        {
            switch (grade)
            {
                case BadgeGrade.Ignition: return 5;
                case BadgeGrade.Overdrive: return 10;
                case BadgeGrade.Apex: return 20;
                case BadgeGrade.Singularity: return 40;
                default: return 0;
            }
        }

        public static int ShardsForGrade(BadgeGrade grade)
        {
            switch (grade)
            {
                case BadgeGrade.Ignition: return 1;
                case BadgeGrade.Overdrive: return 2;
                case BadgeGrade.Apex: return 3;
                case BadgeGrade.Singularity: return 5;
                default: return 0;
            }
        }
    }

    /// <summary>
    /// One app-wide, idempotent reward ledger shared by toy, collector and
    /// challenge Badge runtimes. Claim keys include their scope (and the model
    /// for toy Badges), so repeated publishes, relaunches and migrations cannot
    /// award XP or shards twice.
    /// </summary>
    public sealed class BadgeRewardLedger
    {
        public const string DefaultPrefix = "fidgeting.badges.v2.";

        private readonly string prefix;
        private readonly HashSet<string> claimedRewardKeys;
        private readonly Dictionary<string, string> unlockedAtUtcByKey =
            new Dictionary<string, string>(StringComparer.Ordinal);
        private int shardBalance;
        private bool dirty;

        public BadgeRewardLedger(string storagePrefix = DefaultPrefix)
        {
            prefix = string.IsNullOrEmpty(storagePrefix)
                ? DefaultPrefix
                : storagePrefix;
            claimedRewardKeys = new HashSet<string>(
                PlayerPrefs.GetString(Key("claimedRewards"), string.Empty)
                    .Split(new[] { '|' }, StringSplitOptions.RemoveEmptyEntries),
                StringComparer.Ordinal);
            shardBalance = Math.Max(0, PlayerPrefs.GetInt(Key("shards"), 0));
        }

        public int ShardBalance => shardBalance;

        public static string ToyClaimKey(string modelId, string badgeId)
        {
            return "toy:" + (modelId ?? string.Empty) + ":" + (badgeId ?? string.Empty);
        }

        public static string CollectorClaimKey(string badgeId)
        {
            return "collector:" + (badgeId ?? string.Empty);
        }

        public static string SpecialClaimKey(
            BadgeScope scope,
            string badgeId,
            long cycleIndex = 0L)
        {
            return scope.ToString().ToLowerInvariant()
                + ":" + (badgeId ?? string.Empty)
                + (scope == BadgeScope.Challenge
                    ? ":" + Math.Max(0L, cycleIndex).ToString(CultureInfo.InvariantCulture)
                    : string.Empty);
        }

        public bool IsClaimed(string claimKey)
        {
            return !string.IsNullOrEmpty(claimKey)
                && claimedRewardKeys.Contains(claimKey);
        }

        public string UnlockedAtUtc(string claimKey)
        {
            if (string.IsNullOrEmpty(claimKey))
            {
                return string.Empty;
            }
            if (unlockedAtUtcByKey.TryGetValue(claimKey, out string cached))
            {
                return cached;
            }

            string value = PlayerPrefs.GetString(
                Key("unlockedAt." + claimKey),
                string.Empty);
            unlockedAtUtcByKey[claimKey] = value;
            return value;
        }

        public bool TryClaim(
            string claimKey,
            BadgeDefinition definition,
            DateTime utcNow,
            Action<int> awardExperience)
        {
            if (string.IsNullOrEmpty(claimKey)
                || claimedRewardKeys.Contains(claimKey))
            {
                return false;
            }

            claimedRewardKeys.Add(claimKey);
            string unlockedAt = NormalizeUtc(utcNow)
                .ToString("O", CultureInfo.InvariantCulture);
            unlockedAtUtcByKey[claimKey] = unlockedAt;
            PlayerPrefs.SetString(Key("unlockedAt." + claimKey), unlockedAt);
            awardExperience?.Invoke(definition.ExperienceReward);
            shardBalance = checked(shardBalance + definition.ShardReward);
            dirty = true;
            return true;
        }

        /// <summary>
        /// Migration-only claim. It preserves a reward already paid by the old
        /// achievement economy without granting duplicate XP or shards.
        /// </summary>
        public bool MarkClaimed(string claimKey, DateTime utcNow)
        {
            if (string.IsNullOrEmpty(claimKey)
                || !claimedRewardKeys.Add(claimKey))
            {
                return false;
            }

            string unlockedAt = NormalizeUtc(utcNow)
                .ToString("O", CultureInfo.InvariantCulture);
            unlockedAtUtcByKey[claimKey] = unlockedAt;
            PlayerPrefs.SetString(Key("unlockedAt." + claimKey), unlockedAt);
            dirty = true;
            return true;
        }

        public void SaveIfDirty(bool flush)
        {
            if (dirty)
            {
                PlayerPrefs.SetString(
                    Key("claimedRewards"),
                    string.Join(
                        "|",
                        claimedRewardKeys.OrderBy(value => value, StringComparer.Ordinal)));
                PlayerPrefs.SetInt(Key("shards"), shardBalance);
                dirty = false;
            }
            if (flush)
            {
                PlayerPrefs.Save();
            }
        }

        private string Key(string suffix)
        {
            return prefix + suffix;
        }

        private static DateTime NormalizeUtc(DateTime value)
        {
            return value.Kind == DateTimeKind.Utc ? value : value.ToUniversalTime();
        }
    }

    public static class BadgeCatalogV2
    {
        private static readonly BadgeDefinition[] toyDefinitions =
        {
            Toy("toy_power_ignition", BadgeCategory.Power, BadgeMetric.PeakPower, 1d, BadgeGrade.Ignition, "动力点火", "达到第一档动力门槛", "1.0", "KM/H", "POWER", 0),
            Toy("toy_power_overdrive", BadgeCategory.Power, BadgeMetric.PeakPower, 2d, BadgeGrade.Overdrive, "动力增压", "达到第二档动力门槛", "2.0", "KM/H", "POWER", 1),
            Toy("toy_power_apex", BadgeCategory.Power, BadgeMetric.PeakPower, 3.5d, BadgeGrade.Apex, "动力红线", "达到 Apex 动力门槛", "3.5", "KM/H", "REDLINE", 2),
            Toy("toy_power_singularity", BadgeCategory.Power, BadgeMetric.PeakPower, 4.5d, BadgeGrade.Singularity, "动力奇点", "达到最高动力门槛", "4.5", "KM/H", "REDLINE", 3),
            Toy("toy_pulse_100", BadgeCategory.Pulse, BadgeMetric.LifetimeGestures, 100d, BadgeGrade.Ignition, "百次脉冲", "完成 100 次真实手势", "100", "", "PULSE", 4),
            Toy("toy_pulse_1k", BadgeCategory.Pulse, BadgeMetric.LifetimeGestures, 1000d, BadgeGrade.Overdrive, "千次脉冲", "完成 1,000 次真实手势", "1K", "", "PULSE", 5),
            Toy("toy_pulse_10k", BadgeCategory.Pulse, BadgeMetric.LifetimeGestures, 10000d, BadgeGrade.Apex, "万次脉冲", "完成 10,000 次真实手势", "10K", "", "PULSE", 6),
            Toy("toy_pulse_100k", BadgeCategory.Pulse, BadgeMetric.LifetimeGestures, 100000d, BadgeGrade.Singularity, "十万脉冲", "完成 100,000 次真实手势", "100K", "", "PULSE", 7),
            Toy("toy_technique_clean", BadgeCategory.Technique, BadgeMetric.TechniqueClean, 1d, BadgeGrade.Ignition, "Clean", "完成一次干净技巧", "CLEAN", "", "CONTROL", 8),
            Toy("toy_technique_power", BadgeCategory.Technique, BadgeMetric.TechniquePower, 1d, BadgeGrade.Overdrive, "Power", "完成一次高动力技巧", "POWER", "", "CONTROL", 9),
            Toy("toy_technique_speed", BadgeCategory.Technique, BadgeMetric.TechniqueSpeed, 1d, BadgeGrade.Apex, "Speed", "完成一次高速技巧", "SPEED", "", "CONTROL", 10, BadgeVisibility.Hidden),
            Toy("toy_technique_endurance", BadgeCategory.Technique, BadgeMetric.TechniqueEndurance, 1d, BadgeGrade.Apex, "Endurance", "完成一次耐久技巧", "ENDURE", "", "CONTROL", 11, BadgeVisibility.Hidden),
            Toy("toy_technique_perfect", BadgeCategory.Technique, BadgeMetric.TechniquePerfect, 1d, BadgeGrade.Singularity, "Perfect", "完成一次完美技巧", "PERFECT", "", "CONTROL", 12, BadgeVisibility.Hidden),
            Toy("toy_combo_5", BadgeCategory.Combo, BadgeMetric.HighestCombo, 5d, BadgeGrade.Ignition, "Chain 5", "单次达到 5 Combo", "×5", "", "CHAIN", 13),
            Toy("toy_combo_10", BadgeCategory.Combo, BadgeMetric.HighestCombo, 10d, BadgeGrade.Overdrive, "Chain 10", "单次达到 10 Combo", "×10", "", "CHAIN", 14),
            Toy("toy_combo_20", BadgeCategory.Combo, BadgeMetric.HighestCombo, 20d, BadgeGrade.Apex, "Chain 20", "单次达到 20 Combo", "×20", "", "CHAIN", 15),
            Toy("toy_combo_50", BadgeCategory.Combo, BadgeMetric.HighestCombo, 50d, BadgeGrade.Singularity, "Chain 50", "单次达到 50 Combo", "×50", "", "CHAIN", 16),
            Toy("toy_focus_5m", BadgeCategory.Focus, BadgeMetric.ActiveInteractionSeconds, 300d, BadgeGrade.Ignition, "专注 5 分钟", "真实触摸累计 5 分钟", "5M", "", "FOCUS", 17),
            Toy("toy_focus_30m", BadgeCategory.Focus, BadgeMetric.ActiveInteractionSeconds, 1800d, BadgeGrade.Overdrive, "专注 30 分钟", "真实触摸累计 30 分钟", "30M", "", "FOCUS", 18),
            Toy("toy_focus_2h", BadgeCategory.Focus, BadgeMetric.ActiveInteractionSeconds, 7200d, BadgeGrade.Apex, "专注 2 小时", "真实触摸累计 2 小时", "2H", "", "FOCUS", 19),
            Toy("toy_focus_10h", BadgeCategory.Focus, BadgeMetric.ActiveInteractionSeconds, 36000d, BadgeGrade.Singularity, "专注 10 小时", "真实触摸累计 10 小时", "10H", "", "FOCUS", 20)
        };

        private static readonly BadgeDefinition[] collectorDefinitions =
        {
            Collector("collector_rhythm_1w", BadgeCategory.Rhythm, BadgeMetric.CompletedRhythmWeeks, 1, BadgeGrade.Ignition, "初次节奏", "完成 1 个有效节奏周", "1W", "RHYTHM", 0),
            Collector("collector_rhythm_4w", BadgeCategory.Rhythm, BadgeMetric.CompletedRhythmWeeks, 4, BadgeGrade.Overdrive, "稳定节奏", "完成 4 个有效节奏周", "4W", "RHYTHM", 1),
            Collector("collector_rhythm_12w", BadgeCategory.Rhythm, BadgeMetric.CompletedRhythmWeeks, 12, BadgeGrade.Apex, "长程节奏", "完成 12 个有效节奏周", "12W", "RHYTHM", 2),
            Collector("collector_explore_2", BadgeCategory.Explore, BadgeMetric.DiscoveredModels, 2, BadgeGrade.Ignition, "双核探索", "有效使用 2 个模型", "2", "EXPLORE", 3),
            Collector("collector_explore_3", BadgeCategory.Explore, BadgeMetric.DiscoveredModels, 3, BadgeGrade.Overdrive, "三核探索", "有效使用 3 个模型", "3", "EXPLORE", 4),
            Collector("collector_explore_5", BadgeCategory.Explore, BadgeMetric.DiscoveredModels, 5, BadgeGrade.Apex, "完整探索", "有效使用 5 个模型", "5", "EXPLORE", 5),
            Collector("collector_mastery_1_lv20", BadgeCategory.Mastery, BadgeMetric.ToyLevel20Count, 1, BadgeGrade.Ignition, "首次精通", "1 个模型达到 LV.20", "LV 20", "MASTERY", 6),
            Collector("collector_mastery_3_lv20", BadgeCategory.Mastery, BadgeMetric.ToyLevel20Count, 3, BadgeGrade.Overdrive, "多核精通", "3 个模型达到 LV.20", "3×20", "MASTERY", 7),
            Collector("collector_mastery_1_lv100", BadgeCategory.Mastery, BadgeMetric.ToyLevel100Count, 1, BadgeGrade.Apex, "完成体", "1 个模型达到 LV.100", "LV 100", "MASTERY", 8),
            Collector("collector_mastery_3_lv100", BadgeCategory.Mastery, BadgeMetric.ToyLevel100Count, 3, BadgeGrade.Singularity, "三重完成体", "3 个模型达到 LV.100", "3×100", "MASTERY", 9),
            Collector("collector_collection_5", BadgeCategory.Collection, BadgeMetric.CollectedCosmetics, 5, BadgeGrade.Ignition, "外观匣", "收集 5 个外观", "5", "VAULT", 10),
            Collector("collector_collection_10", BadgeCategory.Collection, BadgeMetric.CollectedCosmetics, 10, BadgeGrade.Overdrive, "外观库", "收集 10 个外观", "10", "VAULT", 11),
            Collector("collector_collection_25", BadgeCategory.Collection, BadgeMetric.CollectedCosmetics, 25, BadgeGrade.Singularity, "外观藏册", "收集 25 个外观", "25", "VAULT", 12)
        };

        private static readonly BadgeDefinition[] specialDefinitions =
        {
            Special("challenge_redline", BadgeScope.Challenge, BadgeMetric.ChallengeRedline, 3, BadgeGrade.Apex, "Redline", "在两个 UTC 日累计三次达到 Apex 动力", "3×", "REDLINE", 0),
            Special("challenge_chain_reactor", BadgeScope.Challenge, BadgeMetric.ChallengeChain, 2, BadgeGrade.Apex, "Chain Reactor", "本周两次达到 20 Combo", "2×20", "CHAIN", 1),
            Special("challenge_perfect_protocol", BadgeScope.Challenge, BadgeMetric.ChallengePerfect, 3, BadgeGrade.Singularity, "Perfect Protocol", "本周完成三次 Perfect", "3×", "PERFECT", 2),
            Special("challenge_three_core_raid", BadgeScope.Challenge, BadgeMetric.ChallengeRaid, 3, BadgeGrade.Singularity, "Three-Core Raid", "三个模型分别达到有效使用", "3 CORE", "RAID", 3),
            Special("challenge_cycle_total", BadgeScope.Challenge, BadgeMetric.ChallengeCycle, 4, BadgeGrade.Singularity, "Cycle Complete", "完成四周循环", "4/4", "CYCLE", 4),
            Special("legacy_founder", BadgeScope.Legacy, BadgeMetric.LegacyFounder, 1, BadgeGrade.Singularity, "创始收藏", "由旧离线成就迁移获得", "LEGACY", "FOUNDER", 5)
        };

        public static IReadOnlyList<BadgeDefinition> ToyDefinitions => toyDefinitions;
        public static IReadOnlyList<BadgeDefinition> CollectorDefinitions => collectorDefinitions;
        public static IReadOnlyList<BadgeDefinition> SpecialDefinitions => specialDefinitions;

        public static int UnlockedToyCount(SpinnerProgressionSnapshot snapshot)
        {
            int count = 0;
            ProductMechanismKind mechanism = ProductCatalog.MechanismForModel(snapshot.ModelId);
            for (int index = 0; index < toyDefinitions.Length; index++)
            {
                BadgeDefinition definition = toyDefinitions[index];
                double target = ResolveToyThreshold(definition, mechanism);
                if (ToyMetricValue(snapshot, definition.Metric, mechanism) >= target)
                {
                    count++;
                }
            }
            return count;
        }

        public static bool IsToyUnlocked(
            SpinnerProgressionSnapshot snapshot,
            BadgeDefinition definition)
        {
            ProductMechanismKind mechanism = ProductCatalog.MechanismForModel(
                snapshot.ModelId);
            return ToyMetricValue(snapshot, definition.Metric, mechanism)
                >= ResolveToyThreshold(definition, mechanism);
        }

        /// <summary>
        /// Selects the strongest Badge earned by this toy only. Grade is the
        /// primary achievement tier; the resolved numeric target breaks ties,
        /// followed by catalog order so the result is deterministic.
        /// </summary>
        public static bool TryResolveFeaturedToyBadge(
            SpinnerProgressionSnapshot snapshot,
            out BadgeDefinition featured)
        {
            ProductMechanismKind mechanism = ProductCatalog.MechanismForModel(
                snapshot.ModelId);
            featured = default;
            bool found = false;
            double featuredTarget = 0d;

            for (int index = 0; index < toyDefinitions.Length; index++)
            {
                BadgeDefinition candidate = toyDefinitions[index];
                if (!IsToyUnlocked(snapshot, candidate))
                {
                    continue;
                }

                double candidateTarget = ResolveToyThreshold(candidate, mechanism);
                if (!found
                    || candidate.Grade > featured.Grade
                    || (candidate.Grade == featured.Grade
                        && candidateTarget > featuredTarget)
                    || (candidate.Grade == featured.Grade
                        && Math.Abs(candidateTarget - featuredTarget) < 0.000001d
                        && candidate.DisplayOrder < featured.DisplayOrder))
                {
                    featured = candidate;
                    featuredTarget = candidateTarget;
                    found = true;
                }
            }

            return found;
        }

        public static string ToyDisplayToken(
            SpinnerProgressionSnapshot snapshot,
            BadgeDefinition definition)
        {
            return DisplayToken(
                definition,
                ProductCatalog.MechanismForModel(snapshot.ModelId));
        }

        public static string ToyDisplayUnit(
            SpinnerProgressionSnapshot snapshot,
            BadgeDefinition definition)
        {
            return DisplayUnit(
                definition,
                ProductCatalog.MechanismForModel(snapshot.ModelId));
        }

        public static string ToyCatalogJson(
            SpinnerProgressionSnapshot snapshot,
            BadgeRewardLedger rewardLedger = null)
        {
            ProductMechanismKind mechanism = ProductCatalog.MechanismForModel(snapshot.ModelId);
            var items = new BadgePayloadItem[toyDefinitions.Length];
            for (int index = 0; index < toyDefinitions.Length; index++)
            {
                BadgeDefinition definition = toyDefinitions[index];
                double target = ResolveToyThreshold(definition, mechanism);
                double current = ToyMetricValue(snapshot, definition.Metric, mechanism);
                string claimKey = BadgeRewardLedger.ToyClaimKey(
                    snapshot.ModelId,
                    definition.Id);
                items[index] = Payload(
                    definition,
                    mechanism,
                    current,
                    target,
                    rewardLedger?.IsClaimed(claimKey) == true,
                    rewardLedger?.UnlockedAtUtc(claimKey) ?? string.Empty);
            }
            return JsonUtility.ToJson(new BadgeCatalogEnvelope
            {
                version = 2,
                modelId = snapshot.ModelId,
                shardBalance = rewardLedger?.ShardBalance ?? 0,
                badges = items
            });
        }

        public static int UnlockedCollectorCount(CollectorProgressionSnapshot snapshot)
        {
            int count = 0;
            for (int index = 0; index < collectorDefinitions.Length; index++)
            {
                if (IsCollectorUnlocked(snapshot, collectorDefinitions[index]))
                {
                    count++;
                }
            }
            return count;
        }

        public static bool IsCollectorUnlocked(
            CollectorProgressionSnapshot snapshot,
            BadgeDefinition definition)
        {
            return CollectorMetricValue(snapshot, definition.Metric)
                >= definition.Threshold;
        }

        public static string CollectorCatalogJson(
            CollectorProgressionSnapshot snapshot,
            BadgeRewardLedger rewardLedger = null)
        {
            var items = new BadgePayloadItem[
                collectorDefinitions.Length + specialDefinitions.Length];
            int output = 0;
            for (int index = 0; index < collectorDefinitions.Length; index++)
            {
                BadgeDefinition definition = collectorDefinitions[index];
                double current = CollectorMetricValue(snapshot, definition.Metric);
                string claimKey = BadgeRewardLedger.CollectorClaimKey(definition.Id);
                items[output++] = Payload(
                    definition,
                    null,
                    current,
                    definition.Threshold,
                    rewardLedger?.IsClaimed(claimKey) == true,
                    rewardLedger?.UnlockedAtUtc(claimKey) ?? string.Empty);
            }

            long cycle = UtcWeekIndex(DateTime.UtcNow);
            for (int index = 0; index < specialDefinitions.Length; index++)
            {
                BadgeDefinition definition = specialDefinitions[index];
                string claimKey = BadgeRewardLedger.SpecialClaimKey(
                    definition.Scope,
                    definition.Id,
                    cycle);
                items[output++] = Payload(
                    definition,
                    null,
                    0d,
                    definition.Threshold,
                    rewardLedger?.IsClaimed(claimKey) == true,
                    rewardLedger?.UnlockedAtUtc(claimKey) ?? string.Empty,
                    cycle);
            }
            return JsonUtility.ToJson(new BadgeCatalogEnvelope
            {
                version = 2,
                modelId = string.Empty,
                shardBalance = rewardLedger?.ShardBalance ?? 0,
                badges = items
            });
        }

        public static long UtcWeekIndex(DateTime utcNow)
        {
            DateTime normalized = utcNow.Kind == DateTimeKind.Utc
                ? utcNow
                : utcNow.ToUniversalTime();
            var unixEpoch = new DateTime(
                1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
            long seconds = (long)(normalized - unixEpoch).TotalSeconds;
            return Math.Max(0L, seconds / 604800L);
        }

        private static BadgeDefinition Toy(
            string id,
            BadgeCategory category,
            BadgeMetric metric,
            double threshold,
            BadgeGrade grade,
            string title,
            string description,
            string token,
            string unit,
            string shortName,
            int order,
            BadgeVisibility visibility = BadgeVisibility.Standard)
        {
            return new BadgeDefinition(
                id, BadgeScope.Toy, category, null, metric, threshold, grade,
                visibility, title, description, AssetName(id), token, unit,
                shortName, order);
        }

        private static BadgeDefinition Collector(
            string id,
            BadgeCategory category,
            BadgeMetric metric,
            double threshold,
            BadgeGrade grade,
            string title,
            string description,
            string token,
            string shortName,
            int order)
        {
            return new BadgeDefinition(
                id, BadgeScope.Collector, category, null, metric, threshold,
                grade, BadgeVisibility.Standard, title, description,
                AssetName(id), token, string.Empty, shortName, order);
        }

        private static BadgeDefinition Special(
            string id,
            BadgeScope scope,
            BadgeMetric metric,
            double threshold,
            BadgeGrade grade,
            string title,
            string description,
            string token,
            string shortName,
            int order)
        {
            return new BadgeDefinition(
                id, scope, scope == BadgeScope.Legacy
                    ? BadgeCategory.Legacy
                    : BadgeCategory.Challenge,
                null, metric, threshold, grade, BadgeVisibility.Standard,
                title, description, AssetName(id), token, string.Empty,
                shortName, order);
        }

        private static string AssetName(string id)
        {
            return "badge-b8-" + id.Replace('_', '-');
        }

        private static double ResolveToyThreshold(
            BadgeDefinition definition,
            ProductMechanismKind mechanism)
        {
            if (definition.Metric != BadgeMetric.PeakPower
                || mechanism == ProductMechanismKind.Rotor)
            {
                return definition.Threshold;
            }

            switch (definition.Grade)
            {
                case BadgeGrade.Ignition: return 0.35d;
                case BadgeGrade.Overdrive: return 0.55d;
                case BadgeGrade.Apex: return 0.75d;
                case BadgeGrade.Singularity: return 0.90d;
                default: return 1d;
            }
        }

        private static double ToyMetricValue(
            SpinnerProgressionSnapshot snapshot,
            BadgeMetric metric,
            ProductMechanismKind mechanism)
        {
            switch (metric)
            {
                case BadgeMetric.PeakPower:
                    return mechanism == ProductMechanismKind.Rotor
                        ? snapshot.PeakRimSpeedKmh
                        : snapshot.PeakNormalizedForce;
                case BadgeMetric.LifetimeGestures:
                    return snapshot.LifetimeGestureCount;
                case BadgeMetric.TechniqueClean:
                    return snapshot.CleanTechniqueCount;
                case BadgeMetric.TechniquePower:
                    return snapshot.PowerTechniqueCount;
                case BadgeMetric.TechniqueSpeed:
                    return snapshot.SpeedTechniqueCount;
                case BadgeMetric.TechniqueEndurance:
                    return snapshot.EnduranceTechniqueCount;
                case BadgeMetric.TechniquePerfect:
                    return snapshot.PerfectTechniqueCount;
                case BadgeMetric.HighestCombo:
                    return snapshot.HighestCombo;
                case BadgeMetric.ActiveInteractionSeconds:
                    return snapshot.ActiveInteractionSeconds;
                default:
                    return 0d;
            }
        }

        private static double CollectorMetricValue(
            CollectorProgressionSnapshot snapshot,
            BadgeMetric metric)
        {
            switch (metric)
            {
                case BadgeMetric.CompletedRhythmWeeks:
                    return snapshot.CompletedRhythmWeeks;
                case BadgeMetric.DiscoveredModels:
                    return snapshot.DiscoveredModelCount;
                case BadgeMetric.ToyLevel20Count:
                    return snapshot.ToyLevel20Count;
                case BadgeMetric.ToyLevel100Count:
                    return snapshot.ToyLevel100Count;
                case BadgeMetric.CollectedCosmetics:
                    return snapshot.CollectedCosmeticCount;
                default:
                    return 0d;
            }
        }

        private static BadgePayloadItem Payload(
            BadgeDefinition definition,
            ProductMechanismKind? mechanism,
            double current,
            double target,
            bool rewardClaimed,
            string unlockedAtUtc,
            long cycleIndex = 0L)
        {
            BadgeProgressState state = ResolveState(
                definition.Visibility,
                current,
                target);
            return new BadgePayloadItem
            {
                id = definition.Id,
                scope = definition.Scope.ToString(),
                category = definition.Category.ToString(),
                mechanism = mechanism?.ToString() ?? "Any",
                metric = definition.Metric.ToString(),
                currentValue = current,
                targetValue = target,
                progress = target <= 0d ? 0f : Mathf.Clamp01((float)(current / target)),
                state = state.ToString(),
                unlockedAtUtc = state == BadgeProgressState.Unlocked
                    ? unlockedAtUtc ?? string.Empty
                    : string.Empty,
                rewardClaimed = rewardClaimed,
                grade = definition.Grade.ToString(),
                visibility = definition.Visibility.ToString(),
                title = definition.Title,
                description = definition.Description,
                assetName = definition.AssetName,
                displayToken = DisplayToken(definition, mechanism),
                displayUnit = DisplayUnit(definition, mechanism),
                shortName = definition.ShortName,
                experienceReward = definition.ExperienceReward,
                shardReward = definition.ShardReward,
                displayOrder = definition.DisplayOrder,
                cycleIndex = cycleIndex
            };
        }

        private static string DisplayToken(
            BadgeDefinition definition,
            ProductMechanismKind? mechanism)
        {
            if (definition.Metric != BadgeMetric.PeakPower
                || !mechanism.HasValue
                || mechanism.Value == ProductMechanismKind.Rotor)
            {
                return definition.DisplayToken;
            }

            switch (definition.Grade)
            {
                case BadgeGrade.Ignition: return "0.35";
                case BadgeGrade.Overdrive: return "0.55";
                case BadgeGrade.Apex: return "0.75";
                case BadgeGrade.Singularity: return "0.90";
                default: return definition.DisplayToken;
            }
        }

        private static string DisplayUnit(
            BadgeDefinition definition,
            ProductMechanismKind? mechanism)
        {
            if (definition.Metric == BadgeMetric.PeakPower
                && mechanism.HasValue
                && mechanism.Value != ProductMechanismKind.Rotor)
            {
                return string.Empty;
            }
            return definition.DisplayUnit;
        }

        private static BadgeProgressState ResolveState(
            BadgeVisibility visibility,
            double current,
            double target)
        {
            if (target > 0d && current >= target)
            {
                return BadgeProgressState.Unlocked;
            }
            if (visibility == BadgeVisibility.Hidden)
            {
                return BadgeProgressState.Hidden;
            }
            return current > 0d
                ? BadgeProgressState.InProgress
                : BadgeProgressState.Locked;
        }

        [Serializable]
        private sealed class BadgeCatalogEnvelope
        {
            public int version;
            public string modelId;
            public int shardBalance;
            public BadgePayloadItem[] badges;
        }

        [Serializable]
        private sealed class BadgePayloadItem
        {
            public string id;
            public string scope;
            public string category;
            public string mechanism;
            public string metric;
            public double currentValue;
            public double targetValue;
            public float progress;
            public string state;
            public string unlockedAtUtc;
            public bool rewardClaimed;
            public string grade;
            public string visibility;
            public string title;
            public string description;
            public string assetName;
            public string displayToken;
            public string displayUnit;
            public string shortName;
            public int experienceReward;
            public int shardReward;
            public int displayOrder;
            public long cycleIndex;
        }
    }
}
