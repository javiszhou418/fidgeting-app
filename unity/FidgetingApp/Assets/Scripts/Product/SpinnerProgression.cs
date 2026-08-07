using System;
using System.Collections.Generic;
using System.Globalization;
using System.Runtime.InteropServices;
using UnityEngine;

namespace FidgetingApp.Product
{
    public readonly struct SpinnerUpgradeStage
    {
        public SpinnerUpgradeStage(
            int levelThreshold,
            string name,
            string componentName,
            string materialName)
        {
            LevelThreshold = levelThreshold;
            Name = name;
            ComponentName = componentName;
            MaterialName = materialName;
        }

        public int LevelThreshold { get; }
        public string Name { get; }
        public string ComponentName { get; }
        public string MaterialName { get; }
    }

    public readonly struct SpinnerProgressionMilestone
    {
        public SpinnerProgressionMilestone(int level, string rewardName)
        {
            Level = level;
            RewardName = rewardName;
        }

        public int Level { get; }
        public string RewardName { get; }
    }

    public readonly struct SpinnerLevelBand
    {
        public SpinnerLevelBand(int levelThreshold, string title, string unlockName)
        {
            LevelThreshold = levelThreshold;
            Title = title;
            UnlockName = unlockName;
        }

        public int LevelThreshold { get; }
        public string Title { get; }
        public string UnlockName { get; }
    }

    public readonly struct SpinnerProgressionSnapshot
    {
        public SpinnerProgressionSnapshot(
            string modelId,
            int level,
            double totalExperience,
            double levelStartExperience,
            double nextLevelExperience,
            float levelProgress,
            SpinnerUpgradeStage stage,
            SpinnerUpgradeStage? nextUnlock,
            bool assistantEnabled,
            double peakRimSpeedKmh,
            long lifetimeGestureCount,
            int todayGestureCount,
            double activeInteractionSeconds,
            double lifetimeOfflineExperience)
        {
            ModelId = modelId;
            Level = level;
            TotalExperience = totalExperience;
            LevelStartExperience = levelStartExperience;
            NextLevelExperience = nextLevelExperience;
            LevelProgress = levelProgress;
            Stage = stage;
            NextUnlock = nextUnlock;
            AssistantEnabled = assistantEnabled;
            PeakRimSpeedKmh = Math.Max(0d, peakRimSpeedKmh);
            LifetimeGestureCount = Math.Max(0L, lifetimeGestureCount);
            TodayGestureCount = Math.Max(0, todayGestureCount);
            ActiveInteractionSeconds = Math.Max(0d, activeInteractionSeconds);
            LifetimeOfflineExperience = Math.Max(0d, lifetimeOfflineExperience);
        }

        public string ModelId { get; }
        public int Level { get; }
        public double TotalExperience { get; }
        public double LevelStartExperience { get; }
        public double NextLevelExperience { get; }
        public float LevelProgress { get; }
        public SpinnerUpgradeStage Stage { get; }
        public SpinnerUpgradeStage? NextUnlock { get; }
        public bool AssistantEnabled { get; }
        public double PeakRimSpeedKmh { get; }
        public long LifetimeGestureCount { get; }
        public int TodayGestureCount { get; }
        public double ActiveInteractionSeconds { get; }
        public double LifetimeOfflineExperience { get; }
    }

    public enum SpinnerAchievementMetric
    {
        PeakRimSpeedKmh = 0,
        LifetimeGestures = 1,
        ActiveInteractionSeconds = 2,
        LifetimeOfflineExperience = 3
    }

    public readonly struct SpinnerAchievementDefinition
    {
        public SpinnerAchievementDefinition(
            string id,
            SpinnerAchievementMetric metric,
            double threshold,
            string title)
        {
            Id = id;
            Metric = metric;
            Threshold = Math.Max(0d, threshold);
            Title = title;
        }

        public string Id { get; }
        public SpinnerAchievementMetric Metric { get; }
        public double Threshold { get; }
        public string Title { get; }
    }

    public readonly struct SpinnerOfflineReward
    {
        public SpinnerOfflineReward(
            string modelId,
            double experience,
            double elapsedHours,
            bool assistantEnabled,
            int previousLevel,
            int newLevel)
        {
            ModelId = modelId;
            Experience = experience;
            ElapsedHours = elapsedHours;
            AssistantEnabled = assistantEnabled;
            PreviousLevel = previousLevel;
            NewLevel = newLevel;
        }

        public string ModelId { get; }
        public double Experience { get; }
        public double ElapsedHours { get; }
        public bool AssistantEnabled { get; }
        public int PreviousLevel { get; }
        public int NewLevel { get; }
        public bool HasReward => Experience >= 1d;

        public static SpinnerOfflineReward None(string modelId)
        {
            return new SpinnerOfflineReward(modelId, 0d, 0d, false, 1, 1);
        }
    }

    /// <summary>
    /// Deterministic progression economy. The target pacing is approximately
    /// 10-15 active minutes per day plus ordinary overnight collection for
    /// a complete level-100 build in about two weeks.
    /// </summary>
    public static class SpinnerProgressionRules
    {
        public const int MaximumLevel = 100;
        public const double FinalExperience = 84000d;
        public const double OfflineCapHours = 16d;
        public const double OfflineExperiencePerHour = 90d;
        public const double AssistantOfflineMultiplier = 1.75d;
        public const double NightOfflineBonus = 0.25d;
        public const double MinimumOfflineClaimMinutes = 5d;
        public const double VirtualRimRadiusMeters = 0.04d;

        private const double LevelCurveExponent = 1.32d;

        private static readonly SpinnerUpgradeStage[] stages =
        {
            new SpinnerUpgradeStage(1, "初始装配", "标准单列轴承", "基础合金"),
            new SpinnerUpgradeStage(20, "静态配重", "精钢配重环", "强化不锈钢"),
            new SpinnerUpgradeStage(50, "双轴承结构", "双列辅助轴承", "精密轴承钢"),
            new SpinnerUpgradeStage(75, "轻量竞速", "低阻保持架", "航空钛合金"),
            new SpinnerUpgradeStage(100, "最终完成体", "陶瓷主轴承 + 双列辅助轴承", "镜面精钢")
        };

        private static readonly SpinnerProgressionMilestone[] milestones =
        {
            new SpinnerProgressionMilestone(5, "磨合完成贴纸"),
            new SpinnerProgressionMilestone(10, "夜光刻度"),
            new SpinnerProgressionMilestone(20, "精钢配重环"),
            new SpinnerProgressionMilestone(35, "静音缓冲垫圈"),
            new SpinnerProgressionMilestone(50, "双列辅助轴承"),
            new SpinnerProgressionMilestone(65, "蓝钢锁环"),
            new SpinnerProgressionMilestone(75, "航空钛合金框架"),
            new SpinnerProgressionMilestone(90, "收藏铭牌"),
            new SpinnerProgressionMilestone(100, "终极镜钢完成体")
        };

        private static readonly SpinnerLevelBand[] levelBands =
        {
            new SpinnerLevelBand(1, "初转学徒", "标准单列轴承与基础成长罐"),
            new SpinnerLevelBand(5, "磨合新手", "磨合完成贴纸"),
            new SpinnerLevelBand(10, "夜光巡航者", "夜光刻度"),
            new SpinnerLevelBand(20, "稳态工匠", "精钢配重环与强化不锈钢"),
            new SpinnerLevelBand(35, "静音调校师", "静音缓冲垫圈"),
            new SpinnerLevelBand(50, "双轴领航员", "双列辅助轴承与精密轴承钢"),
            new SpinnerLevelBand(65, "蓝钢技师", "蓝钢锁环"),
            new SpinnerLevelBand(75, "轻量竞速者", "低阻保持架与航空钛合金"),
            new SpinnerLevelBand(90, "典藏大师", "收藏铭牌"),
            new SpinnerLevelBand(100, "镜钢宗师", "陶瓷主轴承与终极镜钢完成体")
        };

        private static readonly SpinnerAchievementDefinition[] achievements =
        {
            new SpinnerAchievementDefinition("speed-050", SpinnerAchievementMetric.PeakRimSpeedKmh, 0.5d, "初次加速"),
            new SpinnerAchievementDefinition("speed-100", SpinnerAchievementMetric.PeakRimSpeedKmh, 1d, "疾行"),
            new SpinnerAchievementDefinition("speed-200", SpinnerAchievementMetric.PeakRimSpeedKmh, 2d, "破风"),
            new SpinnerAchievementDefinition("speed-350", SpinnerAchievementMetric.PeakRimSpeedKmh, 3.5d, "3.5 KM/H"),
            new SpinnerAchievementDefinition("speed-450", SpinnerAchievementMetric.PeakRimSpeedKmh, 4.5d, "极速外缘"),
            new SpinnerAchievementDefinition("swipe-100", SpinnerAchievementMetric.LifetimeGestures, 100d, "百次触发"),
            new SpinnerAchievementDefinition("swipe-500", SpinnerAchievementMetric.LifetimeGestures, 500d, "500 SWIPES"),
            new SpinnerAchievementDefinition("swipe-1k", SpinnerAchievementMetric.LifetimeGestures, 1000d, "1K SWIPES"),
            new SpinnerAchievementDefinition("swipe-5k", SpinnerAchievementMetric.LifetimeGestures, 5000d, "5K SWIPES"),
            new SpinnerAchievementDefinition("swipe-10k", SpinnerAchievementMetric.LifetimeGestures, 10000d, "10K SWIPES"),
            new SpinnerAchievementDefinition("swipe-100k", SpinnerAchievementMetric.LifetimeGestures, 100000d, "100K SWIPES"),
            new SpinnerAchievementDefinition("focus-1m", SpinnerAchievementMetric.ActiveInteractionSeconds, 60d, "专注 1 分钟"),
            new SpinnerAchievementDefinition("focus-5m", SpinnerAchievementMetric.ActiveInteractionSeconds, 300d, "专注 5 分钟"),
            new SpinnerAchievementDefinition("focus-30m", SpinnerAchievementMetric.ActiveInteractionSeconds, 1800d, "专注 30 分钟"),
            new SpinnerAchievementDefinition("focus-1h", SpinnerAchievementMetric.ActiveInteractionSeconds, 3600d, "触摸 1 小时"),
            new SpinnerAchievementDefinition("focus-5h", SpinnerAchievementMetric.ActiveInteractionSeconds, 18000d, "触摸 5 小时"),
            new SpinnerAchievementDefinition("offline-500", SpinnerAchievementMetric.LifetimeOfflineExperience, 500d, "离线 500 XP"),
            new SpinnerAchievementDefinition("offline-1k", SpinnerAchievementMetric.LifetimeOfflineExperience, 1000d, "离线 1K XP"),
            new SpinnerAchievementDefinition("offline-5k", SpinnerAchievementMetric.LifetimeOfflineExperience, 5000d, "离线 5K XP"),
            new SpinnerAchievementDefinition("offline-10k", SpinnerAchievementMetric.LifetimeOfflineExperience, 10000d, "离线 10K XP"),
            new SpinnerAchievementDefinition("offline-100k", SpinnerAchievementMetric.LifetimeOfflineExperience, 100000d, "离线 100K XP")
        };

        public static IReadOnlyList<SpinnerUpgradeStage> Stages => stages;
        public static IReadOnlyList<SpinnerProgressionMilestone> Milestones => milestones;
        public static IReadOnlyList<SpinnerLevelBand> LevelBands => levelBands;
        public static IReadOnlyList<SpinnerAchievementDefinition> Achievements => achievements;

        public static double RimSpeedKmh(float angularSpeedRadians)
        {
            return Math.Abs(angularSpeedRadians)
                * VirtualRimRadiusMeters
                * 3.6d;
        }

        public static double AchievementValue(
            SpinnerProgressionSnapshot snapshot,
            SpinnerAchievementMetric metric)
        {
            switch (metric)
            {
                case SpinnerAchievementMetric.PeakRimSpeedKmh:
                    return snapshot.PeakRimSpeedKmh;
                case SpinnerAchievementMetric.LifetimeGestures:
                    return snapshot.LifetimeGestureCount;
                case SpinnerAchievementMetric.ActiveInteractionSeconds:
                    return snapshot.ActiveInteractionSeconds;
                case SpinnerAchievementMetric.LifetimeOfflineExperience:
                    return snapshot.LifetimeOfflineExperience;
                default:
                    return 0d;
            }
        }

        public static int UnlockedAchievementCount(SpinnerProgressionSnapshot snapshot)
        {
            int unlocked = 0;
            for (int index = 0; index < achievements.Length; index++)
            {
                SpinnerAchievementDefinition achievement = achievements[index];
                if (AchievementValue(snapshot, achievement.Metric) >= achievement.Threshold)
                {
                    unlocked++;
                }
            }

            return unlocked;
        }

        public static string AchievementCatalogPayload()
        {
            var rows = new string[achievements.Length];
            for (int index = 0; index < achievements.Length; index++)
            {
                SpinnerAchievementDefinition achievement = achievements[index];
                rows[index] = string.Join(
                    "\t",
                    achievement.Id,
                    achievement.Metric.ToString(),
                    achievement.Threshold.ToString("R", CultureInfo.InvariantCulture),
                    achievement.Title);
            }

            return string.Join("\n", rows);
        }

        public static string AchievementCatalogPayload(SpinnerProgressionSnapshot snapshot)
        {
            var rows = new string[achievements.Length];
            for (int index = 0; index < achievements.Length; index++)
            {
                SpinnerAchievementDefinition achievement = achievements[index];
                rows[index] = string.Join(
                    "\t",
                    achievement.Id,
                    achievement.Metric.ToString(),
                    achievement.Threshold.ToString("R", CultureInfo.InvariantCulture),
                    achievement.Title,
                    AchievementValue(snapshot, achievement.Metric) >= achievement.Threshold
                        ? "1"
                        : "0");
            }

            return string.Join("\n", rows);
        }

        public static SpinnerLevelBand LevelBandForLevel(int level)
        {
            SpinnerLevelBand active = levelBands[0];
            for (int index = 1; index < levelBands.Length; index++)
            {
                if (level < levelBands[index].LevelThreshold)
                {
                    break;
                }

                active = levelBands[index];
            }

            return active;
        }

        public static string LevelCatalogPayload()
        {
            var rows = new string[levelBands.Length];
            for (int index = 0; index < levelBands.Length; index++)
            {
                SpinnerLevelBand band = levelBands[index];
                rows[index] = string.Join(
                    "\t",
                    band.LevelThreshold.ToString(CultureInfo.InvariantCulture),
                    band.Title,
                    band.UnlockName);
            }

            return string.Join("\n", rows);
        }

        public static double ExperienceForLevel(int level)
        {
            int clampedLevel = Mathf.Clamp(level, 1, MaximumLevel);
            if (clampedLevel <= 1)
            {
                return 0d;
            }

            if (clampedLevel >= MaximumLevel)
            {
                return FinalExperience;
            }

            double normalized = (clampedLevel - 1d) / (MaximumLevel - 1d);
            return FinalExperience * Math.Pow(normalized, LevelCurveExponent);
        }

        public static int LevelForExperience(double experience)
        {
            double clamped = Math.Max(0d, experience);
            if (clamped >= FinalExperience)
            {
                return MaximumLevel;
            }

            int low = 1;
            int high = MaximumLevel;
            while (low < high)
            {
                int middle = (low + high + 1) / 2;
                if (ExperienceForLevel(middle) <= clamped)
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

        public static float ProgressWithinLevel(double experience)
        {
            int level = LevelForExperience(experience);
            if (level >= MaximumLevel)
            {
                return 1f;
            }

            double start = ExperienceForLevel(level);
            double end = ExperienceForLevel(level + 1);
            return Mathf.Clamp01((float)((Math.Max(0d, experience) - start) / (end - start)));
        }

        public static double GestureExperience(float normalizedForce)
        {
            float force = Mathf.Clamp01(normalizedForce);
            return 4d + 8d * Math.Pow(force, 0.8d);
        }

        public static double ExperienceForRevolutions(
            double absoluteRevolutions,
            float normalizedForce)
        {
            double revolutions = Math.Max(0d, absoluteRevolutions);
            float force = Mathf.Clamp01(normalizedForce);
            double forceMultiplier = 0.72d + 0.78d * Math.Sqrt(force);
            return revolutions * forceMultiplier;
        }

        public static double OfflineExperience(
            double elapsedHours,
            bool assistantEnabled,
            double nightFraction)
        {
            double hours = Math.Min(OfflineCapHours, Math.Max(0d, elapsedHours));
            if (hours * 60d < MinimumOfflineClaimMinutes)
            {
                return 0d;
            }

            double assistantMultiplier = assistantEnabled
                ? AssistantOfflineMultiplier
                : 1d;
            double nightMultiplier = 1d
                + NightOfflineBonus * Math.Min(1d, Math.Max(0d, nightFraction));
            return hours
                * OfflineExperiencePerHour
                * assistantMultiplier
                * nightMultiplier;
        }

        public static SpinnerUpgradeStage StageForLevel(int level)
        {
            SpinnerUpgradeStage active = stages[0];
            for (int index = 1; index < stages.Length; index++)
            {
                if (level < stages[index].LevelThreshold)
                {
                    break;
                }

                active = stages[index];
            }

            return active;
        }

        public static SpinnerUpgradeStage? NextUnlockForLevel(int level)
        {
            for (int index = 0; index < stages.Length; index++)
            {
                if (stages[index].LevelThreshold > level)
                {
                    return stages[index];
                }
            }

            return null;
        }

        public static SpinnerProgressionMilestone? MilestoneCrossed(
            int previousLevel,
            int newLevel)
        {
            SpinnerProgressionMilestone? crossed = null;
            for (int index = 0; index < milestones.Length; index++)
            {
                SpinnerProgressionMilestone milestone = milestones[index];
                if (milestone.Level > previousLevel && milestone.Level <= newLevel)
                {
                    crossed = milestone;
                }
            }

            return crossed;
        }

        public static double EstimateTwoWeekExperience(
            double activeMinutesPerDay,
            double averageRevolutionsPerSecond,
            float averageForce,
            double offlineHoursPerDay,
            double nightFraction,
            bool assistantEnabled)
        {
            double dailyRevolutions = Math.Max(0d, activeMinutesPerDay)
                * 60d
                * Math.Max(0d, averageRevolutionsPerSecond);
            double daily = ExperienceForRevolutions(dailyRevolutions, averageForce)
                + OfflineExperience(
                    offlineHoursPerDay,
                    assistantEnabled,
                    nightFraction);
            return daily * 14d;
        }
    }

    /// <summary>
    /// Small persistent session owned by FidgetAppCoordinator. PlayerPrefs is
    /// written lazily and flushed only on lifecycle boundaries or a slow timer.
    /// </summary>
    public sealed class SpinnerProgressionRuntime
    {
        private const string Prefix = "fidgeting.progression.v1.";
        private const string SuspendedAtKey = Prefix + "suspendedAtUtcTicks";
        private const string SuspendedModelKey = Prefix + "suspendedModel";
        private const string ActiveModelKey = Prefix + "activeModel";

        private readonly Dictionary<string, ProgressionRecord> records =
            new Dictionary<string, ProgressionRecord>(StringComparer.Ordinal);

        private string activeModelId;
        private bool spinCreditArmed;
        private float activeGestureForce;
        private bool dirty;

        public SpinnerProgressionRuntime(string fallbackModelId)
        {
            activeModelId = PlayerPrefs.GetString(ActiveModelKey, fallbackModelId);
            if (string.IsNullOrEmpty(activeModelId))
            {
                activeModelId = fallbackModelId;
            }
            EnsureRecord(activeModelId);
        }

        public string ActiveModelId => activeModelId;
        public bool HasSpinCredit => spinCreditArmed;

        public SpinnerProgressionSnapshot Snapshot => SnapshotWithFreshDay(activeModelId);

        public void SetActiveModel(string modelId)
        {
            if (string.IsNullOrEmpty(modelId) || modelId == activeModelId)
            {
                return;
            }

            PersistRecord(activeModelId, EnsureRecord(activeModelId));
            activeModelId = modelId;
            PlayerPrefs.SetString(ActiveModelKey, activeModelId);
            EnsureRecord(activeModelId);
            EndSpinCredit();
            dirty = true;
        }

        public double RecordGesture(
            float normalizedForce,
            double experienceMultiplier = 1d,
            float angularSpeedRadians = 0f,
            bool countGesture = true,
            DateTime? localNow = null,
            double collectorBonus = 0d)
        {
            ProgressionRecord record = EnsureRecord(activeModelId);
            if (countGesture)
            {
                RefreshDailyGestureWindow(ref record, localNow ?? DateTime.Now);
                record.LifetimeGestureCount++;
                record.TodayGestureCount++;
            }
            record.PeakRimSpeedKmh = Math.Max(
                record.PeakRimSpeedKmh,
                SpinnerProgressionRules.RimSpeedKmh(angularSpeedRadians));
            records[activeModelId] = record;
            dirty = true;
            activeGestureForce = Mathf.Clamp01(normalizedForce);
            spinCreditArmed = true;
            double multiplier = CollectorProgressionRules.ResolveManualExperienceMultiplier(
                experienceMultiplier,
                collectorBonus);
            double gained = SpinnerProgressionRules.GestureExperience(activeGestureForce)
                * multiplier;
            AddExperience(activeModelId, gained);
            return gained;
        }

        public bool RecordActivity(
            float angularSpeedRadians,
            float interactionSeconds,
            bool authorizedMotion)
        {
            if (!authorizedMotion)
            {
                return false;
            }

            ProgressionRecord record = EnsureRecord(activeModelId);
            double nextPeak = Math.Max(
                record.PeakRimSpeedKmh,
                SpinnerProgressionRules.RimSpeedKmh(angularSpeedRadians));
            double addedInteraction = Math.Max(0d, interactionSeconds);
            if (nextPeak <= record.PeakRimSpeedKmh && addedInteraction <= 0d)
            {
                return false;
            }

            record.PeakRimSpeedKmh = nextPeak;
            record.ActiveInteractionSeconds += addedInteraction;
            records[activeModelId] = record;
            dirty = true;
            return true;
        }

        public double RecordRotationDegrees(
            double absoluteDegrees,
            double experienceMultiplier = 1d,
            double collectorBonus = 0d)
        {
            if (!spinCreditArmed || absoluteDegrees <= 0d)
            {
                return 0d;
            }

            double multiplier = CollectorProgressionRules.ResolveManualExperienceMultiplier(
                experienceMultiplier,
                collectorBonus);
            double gained = SpinnerProgressionRules.ExperienceForRevolutions(
                absoluteDegrees / 360d,
                activeGestureForce)
                * multiplier;
            AddExperience(activeModelId, gained);
            return gained;
        }

        public void EndSpinCredit()
        {
            spinCreditArmed = false;
            activeGestureForce = 0f;
        }

        public void SetAssistantEnabled(bool enabled)
        {
            ProgressionRecord record = EnsureRecord(activeModelId);
            if (record.AssistantEnabled == enabled)
            {
                return;
            }

            record.AssistantEnabled = enabled;
            records[activeModelId] = record;
            dirty = true;
        }

        public void Suspend(DateTime utcNow)
        {
            DateTime normalized = utcNow.Kind == DateTimeKind.Utc
                ? utcNow
                : utcNow.ToUniversalTime();
            PlayerPrefs.SetString(
                SuspendedAtKey,
                normalized.Ticks.ToString(CultureInfo.InvariantCulture));
            PlayerPrefs.SetString(SuspendedModelKey, activeModelId);
            SaveIfDirty(true);
        }

        public SpinnerOfflineReward Resume(DateTime utcNow)
        {
            string ticksText = PlayerPrefs.GetString(SuspendedAtKey, string.Empty);
            string suspendedModel = PlayerPrefs.GetString(
                SuspendedModelKey,
                activeModelId);
            PlayerPrefs.DeleteKey(SuspendedAtKey);
            PlayerPrefs.DeleteKey(SuspendedModelKey);

            if (!long.TryParse(
                    ticksText,
                    NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out long ticks)
                || ticks <= 0L)
            {
                PlayerPrefs.Save();
                return SpinnerOfflineReward.None(suspendedModel);
            }

            DateTime startUtc;
            try
            {
                startUtc = new DateTime(ticks, DateTimeKind.Utc);
            }
            catch (ArgumentOutOfRangeException)
            {
                PlayerPrefs.Save();
                return SpinnerOfflineReward.None(suspendedModel);
            }

            DateTime endUtc = utcNow.Kind == DateTimeKind.Utc
                ? utcNow
                : utcNow.ToUniversalTime();
            double elapsedHours = Math.Max(0d, (endUtc - startUtc).TotalHours);
            double creditedHours = Math.Min(
                SpinnerProgressionRules.OfflineCapHours,
                elapsedHours);
            DateTime creditedStart = endUtc.AddHours(-creditedHours);
            double nightFraction = CalculateNightFraction(creditedStart, endUtc);

            ProgressionRecord record = EnsureRecord(suspendedModel);
            int previousLevel = SpinnerProgressionRules.LevelForExperience(record.Experience);
            double reward = SpinnerProgressionRules.OfflineExperience(
                elapsedHours,
                record.AssistantEnabled,
                nightFraction);
            if (reward > 0d)
            {
                AddExperience(suspendedModel, reward);
                record = EnsureRecord(suspendedModel);
                record.LifetimeOfflineExperience += reward;
                records[suspendedModel] = record;
                dirty = true;
            }

            int newLevel = SpinnerProgressionRules.LevelForExperience(record.Experience);
            SaveIfDirty(true);
            return new SpinnerOfflineReward(
                suspendedModel,
                reward,
                creditedHours,
                record.AssistantEnabled,
                previousLevel,
                newLevel);
        }

        public SpinnerProgressionSnapshot SnapshotFor(string modelId)
        {
            return SnapshotWithFreshDay(modelId);
        }

        private SpinnerProgressionSnapshot SnapshotWithFreshDay(string modelId)
        {
            ProgressionRecord record = EnsureRecord(modelId);
            string previousStamp = record.DailyGestureStamp;
            RefreshDailyGestureWindow(ref record, DateTime.Now);
            if (record.DailyGestureStamp != previousStamp)
            {
                records[modelId] = record;
                dirty = true;
            }

            return CreateSnapshot(modelId, record);
        }

        public void SaveIfDirty(bool flush)
        {
            if (dirty)
            {
                foreach (KeyValuePair<string, ProgressionRecord> pair in records)
                {
                    PersistRecord(pair.Key, pair.Value);
                }
                dirty = false;
            }

            if (flush)
            {
                PlayerPrefs.Save();
            }
        }

        private void AddExperience(string modelId, double amount)
        {
            if (amount <= 0d)
            {
                return;
            }

            ProgressionRecord record = EnsureRecord(modelId);
            record.Experience = Math.Min(
                SpinnerProgressionRules.FinalExperience,
                Math.Max(0d, record.Experience + amount));
            records[modelId] = record;
            dirty = true;
        }

        private ProgressionRecord EnsureRecord(string modelId)
        {
            if (records.TryGetValue(modelId, out ProgressionRecord record))
            {
                return record;
            }

            string experienceText = PlayerPrefs.GetString(
                Prefix + modelId + ".experience",
                "0");
            double.TryParse(
                experienceText,
                NumberStyles.Float,
                CultureInfo.InvariantCulture,
                out double experience);
            record = new ProgressionRecord
            {
                Experience = Math.Min(
                    SpinnerProgressionRules.FinalExperience,
                    Math.Max(0d, experience)),
                AssistantEnabled = PlayerPrefs.GetInt(
                    Prefix + modelId + ".assistant",
                    0) != 0,
                PeakRimSpeedKmh = ReadDouble(modelId, "peakRimSpeedKmh"),
                LifetimeGestureCount = ReadLong(modelId, "lifetimeGestures"),
                TodayGestureCount = PlayerPrefs.GetInt(
                    Prefix + modelId + ".todayGestures",
                    0),
                DailyGestureStamp = PlayerPrefs.GetString(
                    Prefix + modelId + ".dailyGestureStamp",
                    string.Empty),
                ActiveInteractionSeconds = ReadDouble(modelId, "activeInteractionSeconds"),
                LifetimeOfflineExperience = ReadDouble(modelId, "lifetimeOfflineExperience")
            };
            RefreshDailyGestureWindow(ref record, DateTime.Now);
            records[modelId] = record;
            return record;
        }

        private static SpinnerProgressionSnapshot CreateSnapshot(
            string modelId,
            ProgressionRecord record)
        {
            int level = SpinnerProgressionRules.LevelForExperience(record.Experience);
            double levelStart = SpinnerProgressionRules.ExperienceForLevel(level);
            double nextLevel = level >= SpinnerProgressionRules.MaximumLevel
                ? SpinnerProgressionRules.FinalExperience
                : SpinnerProgressionRules.ExperienceForLevel(level + 1);
            return new SpinnerProgressionSnapshot(
                modelId,
                level,
                record.Experience,
                levelStart,
                nextLevel,
                SpinnerProgressionRules.ProgressWithinLevel(record.Experience),
                SpinnerProgressionRules.StageForLevel(level),
                SpinnerProgressionRules.NextUnlockForLevel(level),
                record.AssistantEnabled,
                record.PeakRimSpeedKmh,
                record.LifetimeGestureCount,
                record.TodayGestureCount,
                record.ActiveInteractionSeconds,
                record.LifetimeOfflineExperience);
        }

        private static double CalculateNightFraction(DateTime startUtc, DateTime endUtc)
        {
            if (endUtc <= startUtc)
            {
                return 0d;
            }

            TimeSpan step = TimeSpan.FromMinutes(15d);
            double totalMinutes = 0d;
            double nightMinutes = 0d;
            for (DateTime cursor = startUtc; cursor < endUtc; cursor += step)
            {
                DateTime next = cursor + step < endUtc ? cursor + step : endUtc;
                double minutes = (next - cursor).TotalMinutes;
                DateTime localMidpoint = cursor.AddMinutes(minutes * 0.5d).ToLocalTime();
                bool isNight = localMidpoint.Hour >= 22 || localMidpoint.Hour < 8;
                totalMinutes += minutes;
                if (isNight)
                {
                    nightMinutes += minutes;
                }
            }

            return totalMinutes > 0d ? nightMinutes / totalMinutes : 0d;
        }

        private static void PersistRecord(string modelId, ProgressionRecord record)
        {
            PlayerPrefs.SetString(
                Prefix + modelId + ".experience",
                record.Experience.ToString("R", CultureInfo.InvariantCulture));
            PlayerPrefs.SetInt(
                Prefix + modelId + ".assistant",
                record.AssistantEnabled ? 1 : 0);
            PlayerPrefs.SetString(
                Prefix + modelId + ".peakRimSpeedKmh",
                record.PeakRimSpeedKmh.ToString("R", CultureInfo.InvariantCulture));
            PlayerPrefs.SetString(
                Prefix + modelId + ".lifetimeGestures",
                record.LifetimeGestureCount.ToString(CultureInfo.InvariantCulture));
            PlayerPrefs.SetInt(
                Prefix + modelId + ".todayGestures",
                record.TodayGestureCount);
            PlayerPrefs.SetString(
                Prefix + modelId + ".dailyGestureStamp",
                record.DailyGestureStamp ?? string.Empty);
            PlayerPrefs.SetString(
                Prefix + modelId + ".activeInteractionSeconds",
                record.ActiveInteractionSeconds.ToString("R", CultureInfo.InvariantCulture));
            PlayerPrefs.SetString(
                Prefix + modelId + ".lifetimeOfflineExperience",
                record.LifetimeOfflineExperience.ToString("R", CultureInfo.InvariantCulture));
        }

        private static double ReadDouble(string modelId, string suffix)
        {
            double.TryParse(
                PlayerPrefs.GetString(Prefix + modelId + "." + suffix, "0"),
                NumberStyles.Float,
                CultureInfo.InvariantCulture,
                out double value);
            return Math.Max(0d, value);
        }

        private static long ReadLong(string modelId, string suffix)
        {
            long.TryParse(
                PlayerPrefs.GetString(Prefix + modelId + "." + suffix, "0"),
                NumberStyles.Integer,
                CultureInfo.InvariantCulture,
                out long value);
            return Math.Max(0L, value);
        }

        private static void RefreshDailyGestureWindow(
            ref ProgressionRecord record,
            DateTime localNow)
        {
            string stamp = localNow.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
            if (record.DailyGestureStamp == stamp)
            {
                return;
            }

            record.DailyGestureStamp = stamp;
            record.TodayGestureCount = 0;
        }

        private struct ProgressionRecord
        {
            public double Experience;
            public bool AssistantEnabled;
            public double PeakRimSpeedKmh;
            public long LifetimeGestureCount;
            public int TodayGestureCount;
            public string DailyGestureStamp;
            public double ActiveInteractionSeconds;
            public double LifetimeOfflineExperience;
        }
    }

    public static class SpinnerProgressionNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexProgressionReceiveState(
            string modelId,
            int level,
            float totalExperience,
            float levelStartExperience,
            float nextLevelExperience,
            float levelProgress,
            string stageName,
            string stageComponent,
            string stageMaterial,
            string levelTitle,
            string levelCatalog,
            int nextUnlockLevel,
            string nextUnlockName,
            int assistantEnabled,
            float assistantSpeedMultiplier,
            string offlineModelId,
            int offlineAssistantEnabled,
            float offlineExperience,
            float offlineHours,
            int previousLevel,
            int offlineNewLevel,
            int livePreviousLevel,
            string liveRewardName,
            float peakRimSpeedKmh,
            long lifetimeGestureCount,
            int todayGestureCount,
            float activeInteractionSeconds,
            float lifetimeOfflineExperience,
            int unlockedAchievementCount,
            int totalAchievementCount,
            string achievementCatalog,
            string threeBladeMetalSkinCatalog,
            string equippedThreeBladeMetalSkinId,
            string productStickerCatalog,
            string equippedProductStickerId);
#endif

        public static void Publish(
            SpinnerProgressionSnapshot snapshot,
            SpinnerOfflineReward offlineReward,
            int livePreviousLevel,
            string liveRewardName,
            float assistantSpeedMultiplier,
            string appliedThreeBladeMetalSkinId,
            string appliedProductStickerId)
        {
#if UNITY_IOS && !UNITY_EDITOR
            SpinnerUpgradeStage? next = snapshot.NextUnlock;
            CodexProgressionReceiveState(
                snapshot.ModelId,
                snapshot.Level,
                (float)snapshot.TotalExperience,
                (float)snapshot.LevelStartExperience,
                (float)snapshot.NextLevelExperience,
                snapshot.LevelProgress,
                snapshot.Stage.Name,
                snapshot.Stage.ComponentName,
                snapshot.Stage.MaterialName,
                SpinnerProgressionRules.LevelBandForLevel(snapshot.Level).Title,
                SpinnerProgressionRules.LevelCatalogPayload(),
                next?.LevelThreshold ?? SpinnerProgressionRules.MaximumLevel,
                next?.Name ?? "已完成全部升级",
                snapshot.AssistantEnabled ? 1 : 0,
                assistantSpeedMultiplier,
                string.IsNullOrEmpty(offlineReward.ModelId)
                    ? snapshot.ModelId
                    : offlineReward.ModelId,
                offlineReward.AssistantEnabled ? 1 : 0,
                (float)offlineReward.Experience,
                (float)offlineReward.ElapsedHours,
                offlineReward.PreviousLevel,
                offlineReward.NewLevel,
                livePreviousLevel,
                liveRewardName ?? string.Empty,
                (float)snapshot.PeakRimSpeedKmh,
                snapshot.LifetimeGestureCount,
                snapshot.TodayGestureCount,
                (float)snapshot.ActiveInteractionSeconds,
                (float)snapshot.LifetimeOfflineExperience,
                SpinnerProgressionRules.UnlockedAchievementCount(snapshot),
                SpinnerProgressionRules.Achievements.Count,
                SpinnerProgressionRules.AchievementCatalogPayload(snapshot),
                ThreeBladeMetalSkinCatalog.CatalogPayload(),
                appliedThreeBladeMetalSkinId ?? string.Empty,
                ProductStickerCatalog.CatalogPayload(),
                appliedProductStickerId ?? string.Empty);
#endif
        }
    }
}
