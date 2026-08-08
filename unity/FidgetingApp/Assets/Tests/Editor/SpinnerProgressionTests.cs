using System.IO;
using System.Linq;
using FidgetingApp.Product;
using NUnit.Framework;
using ThreeBladeEDC.Interaction;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class SpinnerProgressionTests
    {
        [Test]
        public void CatalogMigrationMovesLegacyBlueProgressionAndCollectorIdentityOnce()
        {
            string[] keys =
            {
                "fidgeting.catalog.migration.version",
                "fidgeting.progression.v1.blue-classic.experience",
                "fidgeting.progression.v1.pointed-three-blade.experience",
                "fidgeting.progression.v1.activeModel",
                "fidgeting.collector.v1.focusModel",
                "fidgeting.collector.v1.discoveredModels",
                "fidgeting.collector.v1.awardedToyMilestones",
                "fidgeting.collector.v1.highestToyLevels",
                "fidgeting.appearance.sticker.v1.blue-classic",
                "fidgeting.appearance.sticker.v1.pointed-three-blade"
            };
            foreach (string key in keys)
            {
                PlayerPrefs.DeleteKey(key);
            }

            try
            {
                PlayerPrefs.SetString(
                    "fidgeting.progression.v1.blue-classic.experience",
                    "1234.5");
                PlayerPrefs.SetString(
                    "fidgeting.progression.v1.activeModel",
                    "blue-classic");
                PlayerPrefs.SetString(
                    "fidgeting.collector.v1.focusModel",
                    "blue-classic");
                PlayerPrefs.SetString(
                    "fidgeting.collector.v1.discoveredModels",
                    "blue-classic|gold-four-wing");
                PlayerPrefs.SetString(
                    "fidgeting.collector.v1.awardedToyMilestones",
                    "blue-classic@20");
                PlayerPrefs.SetString(
                    "fidgeting.collector.v1.highestToyLevels",
                    "blue-classic@35");
                PlayerPrefs.SetString(
                    "fidgeting.appearance.sticker.v1.blue-classic",
                    "orbit-mark");

                ProductCatalogMigration.Apply();

                Assert.That(
                    PlayerPrefs.GetString(
                        "fidgeting.progression.v1.pointed-three-blade.experience"),
                    Is.EqualTo("1234.5"));
                Assert.That(
                    PlayerPrefs.GetString("fidgeting.progression.v1.activeModel"),
                    Is.EqualTo("pointed-three-blade"));
                Assert.That(
                    PlayerPrefs.GetString("fidgeting.collector.v1.focusModel"),
                    Is.EqualTo("pointed-three-blade"));
                StringAssert.Contains(
                    "pointed-three-blade",
                    PlayerPrefs.GetString("fidgeting.collector.v1.discoveredModels"));
                Assert.That(
                    PlayerPrefs.GetString("fidgeting.collector.v1.awardedToyMilestones"),
                    Is.EqualTo("pointed-three-blade@20"));
                Assert.That(
                    PlayerPrefs.GetString("fidgeting.collector.v1.highestToyLevels"),
                    Is.EqualTo("pointed-three-blade@35"));
                Assert.That(
                    PlayerPrefs.GetString(
                        "fidgeting.appearance.sticker.v1.pointed-three-blade"),
                    Is.EqualTo("orbit-mark"));

                PlayerPrefs.SetString(
                    "fidgeting.progression.v1.blue-classic.experience",
                    "9999");
                ProductCatalogMigration.Apply();
                Assert.That(
                    PlayerPrefs.GetString(
                        "fidgeting.progression.v1.pointed-three-blade.experience"),
                    Is.EqualTo("1234.5"),
                    "The migration must be idempotent and never overwrite new data.");
            }
            finally
            {
                foreach (string key in keys)
                {
                    PlayerPrefs.DeleteKey(key);
                }
                PlayerPrefs.Save();
            }
        }

        [Test]
        public void LevelCurve_IsMonotonicAndEndsAtLevelOneHundred()
        {
            double previous = -1d;
            for (int level = 1; level <= SpinnerProgressionRules.MaximumLevel; level++)
            {
                double threshold = SpinnerProgressionRules.ExperienceForLevel(level);
                Assert.That(threshold, Is.GreaterThan(previous));
                Assert.That(
                    SpinnerProgressionRules.LevelForExperience(threshold),
                    Is.EqualTo(level));
                previous = threshold;
            }

            Assert.That(
                SpinnerProgressionRules.ExperienceForLevel(100),
                Is.EqualTo(SpinnerProgressionRules.FinalExperience));
            Assert.That(
                SpinnerProgressionRules.ProgressWithinLevel(
                    SpinnerProgressionRules.FinalExperience),
                Is.EqualTo(1f));
        }

        [Test]
        public void CollectorRankCurveAndManualBonusesStayBounded()
        {
            double previous = -1d;
            for (int rank = 1; rank <= CollectorProgressionRules.MaximumRank; rank++)
            {
                double threshold = CollectorProgressionRules.ExperienceForRank(rank);
                Assert.That(threshold, Is.GreaterThan(previous));
                Assert.That(
                    CollectorProgressionRules.RankForExperience(threshold),
                    Is.EqualTo(rank));
                previous = threshold;
            }

            Assert.That(
                CollectorProgressionRules.ExperienceForRank(30),
                Is.EqualTo(CollectorProgressionRules.FinalExperience));
            Assert.That(CollectorProgressionRules.GlobalActiveBonusForRank(30), Is.EqualTo(0.10f));
            Assert.That(CollectorProgressionRules.FocusActiveBonusForRank(30), Is.EqualTo(0.20f));
            Assert.That(
                CollectorProgressionRules.ResolveManualExperienceMultiplier(1.30d, 0.20d),
                Is.EqualTo(1.50d));
            Assert.That(
                CollectorProgressionRules.ResolveManualExperienceMultiplier(99d, 99d),
                Is.EqualTo(1.50d));
        }

        [Test]
        public void CollectorEffectiveDaysUseThreeInteractionsSixtySecondsAndFlexibleFiveOfSeven()
        {
            string prefix = "collector-days-" + System.Guid.NewGuid() + ".";
            var runtime = new CollectorProgressionRuntime("blue-classic", prefix);
            runtime.CompleteBackfill();
            System.DateTime firstDay = System.DateTime.Now.Date.AddDays(-4d).AddHours(12d);

            for (int day = 0; day < 5; day++)
            {
                System.DateTime now = firstDay.AddDays(day);
                runtime.RecordGesture("blue-classic", now);
                runtime.RecordGesture("blue-classic", now);
                runtime.RecordGesture("blue-classic", now);
                runtime.RecordActivity(59.9d, now);
                Assert.That(runtime.SnapshotAt(now).ValidDaysInWindow, Is.EqualTo(day));
                runtime.RecordActivity(0.1d, now);
                Assert.That(runtime.SnapshotAt(now).ValidDaysInWindow, Is.EqualTo(day + 1));
            }

            CollectorProgressionSnapshot snapshot =
                runtime.SnapshotAt(firstDay.AddDays(4d));
            Assert.That(snapshot.ValidDaysInWindow, Is.EqualTo(5));
            Assert.That(snapshot.CompletedRhythmWeeks, Is.EqualTo(1));
            Assert.That(snapshot.DiscoveredModelCount, Is.EqualTo(1));
            StringAssert.Contains("rhythm-1", snapshot.AchievementCatalogPayload);
        }

        [Test]
        public void CollectorFocusChangesOncePerLocalDayAndDoesNotBoostOfflineRules()
        {
            string prefix = "collector-focus-" + System.Guid.NewGuid() + ".";
            var runtime = new CollectorProgressionRuntime("blue-classic", prefix);
            runtime.CompleteBackfill();
            System.DateTime today = System.DateTime.Now.Date.AddHours(10d);

            Assert.That(runtime.SetFocusModel("metal-three-blade", today), Is.True);
            Assert.That(runtime.SetFocusModel("gold-four-wing", today), Is.False);
            Assert.That(runtime.SetFocusModel("gold-four-wing", today.AddDays(1d)), Is.True);

            double ordinaryOffline = SpinnerProgressionRules.OfflineExperience(8d, false, 0.5d);
            Assert.That(
                SpinnerProgressionRules.OfflineExperience(8d, false, 0.5d),
                Is.EqualTo(ordinaryOffline),
                "Collector progression must not enter the offline XP formula.");
        }

        [Test]
        public void CollectorMilestonesAreCrossToyPersistentAndNeverDoubleAwarded()
        {
            string prefix = "collector-milestones-" + System.Guid.NewGuid() + ".";
            var runtime = new CollectorProgressionRuntime("blue-classic", prefix);
            runtime.BackfillModel("blue-classic", 100, true);
            double firstExperience = runtime.Snapshot.TotalExperience;
            runtime.BackfillModel("blue-classic", 100, true);
            Assert.That(runtime.Snapshot.TotalExperience, Is.EqualTo(firstExperience));

            runtime.BackfillModel("metal-three-blade", 20, true);
            runtime.BackfillModel("gold-four-wing", 20, true);
            runtime.CompleteBackfill();
            CollectorProgressionSnapshot snapshot = runtime.Snapshot;
            Assert.That(snapshot.DiscoveredModelCount, Is.EqualTo(3));
            StringAssert.Contains("master-20-3", snapshot.AchievementCatalogPayload);
            StringAssert.Contains("master-100-1", snapshot.AchievementCatalogPayload);
        }

        [Test]
        public void SpinnerExperienceAddsCollectorBonusAfterComboAndCapsAtOnePointFive()
        {
            string baselineModel = "collector-base-" + System.Guid.NewGuid();
            string boostedModel = "collector-boost-" + System.Guid.NewGuid();
            var baseline = new SpinnerProgressionRuntime(baselineModel);
            var boosted = new SpinnerProgressionRuntime(boostedModel);
            baseline.RecordGesture(0.7f, 1.30d);
            boosted.RecordGesture(
                0.7f,
                1.30d,
                collectorBonus: 0.20d);

            Assert.That(
                boosted.Snapshot.TotalExperience,
                Is.EqualTo(baseline.Snapshot.TotalExperience * (1.50d / 1.30d))
                    .Within(0.001d));
        }

        [Test]
        public void UpgradeStages_UnlockComponentsAndMaterialsAtMilestones()
        {
            Assert.That(SpinnerProgressionRules.Stages.Count, Is.EqualTo(5));
            Assert.That(SpinnerProgressionRules.StageForLevel(1).Name, Is.EqualTo("初始装配"));
            Assert.That(SpinnerProgressionRules.StageForLevel(20).ComponentName, Does.Contain("配重"));
            Assert.That(SpinnerProgressionRules.StageForLevel(50).ComponentName, Does.Contain("辅助轴承"));
            Assert.That(SpinnerProgressionRules.StageForLevel(75).MaterialName, Does.Contain("钛合金"));
            Assert.That(SpinnerProgressionRules.StageForLevel(100).MaterialName, Does.Contain("镜面精钢"));
            Assert.That(
                SpinnerProgressionRules.NextUnlockForLevel(19)?.LevelThreshold,
                Is.EqualTo(20));
            Assert.That(
                SpinnerProgressionRules.NextUnlockForLevel(19)?.Name,
                Is.EqualTo("静态配重"));
            Assert.That(SpinnerProgressionRules.NextUnlockForLevel(100), Is.Null);
            Assert.That(SpinnerProgressionRules.Milestones.Count, Is.EqualTo(9));
            Assert.That(
                SpinnerProgressionRules.MilestoneCrossed(9, 10)?.RewardName,
                Is.EqualTo("夜光刻度"));
            Assert.That(
                SpinnerProgressionRules.MilestoneCrossed(49, 50)?.RewardName,
                Does.Contain("辅助轴承"));

            Assert.That(SpinnerProgressionRules.LevelBands.Count, Is.EqualTo(10));
            Assert.That(
                SpinnerProgressionRules.LevelBandForLevel(27).Title,
                Is.EqualTo("稳态工匠"));
            Assert.That(
                SpinnerProgressionRules.LevelBandForLevel(100).UnlockName,
                Does.Contain("陶瓷主轴承"));
            StringAssert.Contains("20\t稳态工匠", SpinnerProgressionRules.LevelCatalogPayload());
        }

        [Test]
        public void BadgeCatalog_UsesIndependentSpeedSwipeTimeAndOfflineMilestones()
        {
            Assert.That(SpinnerProgressionRules.Achievements.Count, Is.EqualTo(21));
            Assert.That(
                SpinnerProgressionRules.RimSpeedKmh(25f),
                Is.EqualTo(3.6d).Within(0.001d));
            StringAssert.Contains(
                "speed-350\tPeakRimSpeedKmh\t3.5\t3.5 KM/H",
                SpinnerProgressionRules.AchievementCatalogPayload());
            StringAssert.Contains(
                "swipe-100k\tLifetimeGestures\t100000\t100K SWIPES",
                SpinnerProgressionRules.AchievementCatalogPayload());

            var snapshot = new SpinnerProgressionSnapshot(
                "badge-test",
                1,
                0d,
                0d,
                SpinnerProgressionRules.ExperienceForLevel(2),
                0f,
                SpinnerProgressionRules.StageForLevel(1),
                SpinnerProgressionRules.NextUnlockForLevel(1),
                false,
                3.5d,
                500L,
                12,
                300d,
                1000d);

            Assert.That(
                SpinnerProgressionRules.UnlockedAchievementCount(snapshot),
                Is.EqualTo(10));
            string statePayload = SpinnerProgressionRules.AchievementCatalogPayload(snapshot);
            StringAssert.Contains(
                "speed-350\tPeakRimSpeedKmh\t3.5\t3.5 KM/H\t1",
                statePayload);
            StringAssert.Contains(
                "speed-450\tPeakRimSpeedKmh\t4.5\t极速外缘\t0",
                statePayload);
        }

        [Test]
        public void ProgressionRuntime_TracksRealActivityAndDailyGesturesPerModel()
        {
            string model = "activity-" + System.Guid.NewGuid();
            var runtime = new SpinnerProgressionRuntime(model);
            runtime.SetActiveModel(model);
            System.DateTime now = System.DateTime.Now;

            runtime.RecordGesture(0.7f, 1d, 25f, true, now.AddDays(-1d));
            runtime.RecordGesture(0.7f, 1d, 25f, true, now);
            runtime.RecordActivity(25f, 12.5f, true);
            runtime.RecordActivity(100f, 99f, false);

            SpinnerProgressionSnapshot snapshot = runtime.Snapshot;
            Assert.That(snapshot.LifetimeGestureCount, Is.EqualTo(2L));
            Assert.That(snapshot.TodayGestureCount, Is.EqualTo(1));
            Assert.That(snapshot.PeakRimSpeedKmh, Is.EqualTo(3.6d).Within(0.001d));
            Assert.That(snapshot.ActiveInteractionSeconds, Is.EqualTo(12.5d).Within(0.001d));
        }

        [Test]
        public void Combo_RequiresSpeedIntensityAndSwipeFrequencyThenExpires()
        {
            var combo = new SpinnerComboRuntime();

            combo.RecordGesture(0f, 24f, 0.82f);
            Assert.That(combo.Snapshot.IsActive, Is.False,
                "One strong swipe has no cadence yet and must not create a combo.");

            combo.RecordGesture(0.8f, 24f, 0.82f);
            Assert.That(combo.Snapshot.Tier, Is.EqualTo(SpinnerComboTier.Overdrive));
            Assert.That(combo.Snapshot.Count, Is.EqualTo(2));
            Assert.That(combo.Snapshot.ExperienceMultiplier, Is.EqualTo(1.30f));

            combo.RecordGesture(1.5f, 16f, 0.58f);
            Assert.That(combo.Snapshot.Tier, Is.EqualTo(SpinnerComboTier.Drive));
            Assert.That(combo.Snapshot.Count, Is.EqualTo(3));

            Assert.That(combo.Tick(4f), Is.True);
            Assert.That(combo.Snapshot, Is.EqualTo(SpinnerComboSnapshot.Rest));

            combo.RecordGesture(5f, 28f, 0.10f);
            combo.RecordGesture(5.5f, 28f, 0.90f);
            Assert.That(combo.Snapshot.IsActive, Is.False,
                "A weak first swipe must not seed cadence for a later strong swipe.");
        }

        [Test]
        public void Combo_FlowTierAndExperienceBonusStayBounded()
        {
            var combo = new SpinnerComboRuntime();
            combo.RecordGesture(0f, 8f, 0.32f);
            combo.RecordGesture(1.8f, 8f, 0.32f);

            Assert.That(combo.Snapshot.Tier, Is.EqualTo(SpinnerComboTier.Flow));
            Assert.That(combo.Snapshot.NormalizedSpeed, Is.InRange(0.26f, 0.27f));
            Assert.That(combo.Snapshot.NormalizedIntensity, Is.EqualTo(0.32f));
            Assert.That(combo.Snapshot.NormalizedFrequency, Is.GreaterThan(0.20f));

            string baseModel = "combo-base-" + System.Guid.NewGuid();
            string bonusModel = "combo-bonus-" + System.Guid.NewGuid();
            var ordinary = new SpinnerProgressionRuntime(baseModel);
            var boosted = new SpinnerProgressionRuntime(bonusModel);
            ordinary.SetActiveModel(baseModel);
            boosted.SetActiveModel(bonusModel);
            ordinary.RecordGesture(0.7f);
            boosted.RecordGesture(0.7f, 99d);

            Assert.That(
                boosted.Snapshot.TotalExperience,
                Is.EqualTo(ordinary.Snapshot.TotalExperience * 1.30d).Within(0.001d),
                "Combo XP must use the hard 1.30x economy cap.");
        }

        [Test]
        public void Combo_RealMechanicalTravelAddsFastLegibleCountPulses()
        {
            Assert.That(SpinnerComboRules.CountPulseDegrees, Is.EqualTo(120f));
            Assert.That(
                SpinnerComboRules.MinimumCountPulseIntervalSeconds,
                Is.EqualTo(0.16f));
            Assert.That(
                SpinnerComboRules.MinimumCountPulseAngularSpeed,
                Is.EqualTo(4f));

            var combo = new SpinnerComboRuntime();
            Assert.That(
                combo.RecordMechanicalActivity(0.1f, 360f, 24f),
                Is.False,
                "Mechanical travel cannot invent a combo before qualified gestures.");

            combo.RecordGesture(0f, 24f, 0.82f);
            combo.RecordGesture(0.8f, 24f, 0.82f);
            Assert.That(combo.Snapshot.Count, Is.EqualTo(2));
            float multiplier = combo.Snapshot.ExperienceMultiplier;

            Assert.That(
                combo.RecordMechanicalActivity(0.90f, 119f, 24f),
                Is.False);
            Assert.That(
                combo.RecordMechanicalActivity(0.92f, 1f, 24f),
                Is.True);
            Assert.That(combo.Snapshot.Count, Is.EqualTo(3));
            Assert.That(combo.Snapshot.ExperienceMultiplier, Is.EqualTo(multiplier),
                "Display pulses must not award or amplify XP.");

            Assert.That(
                combo.RecordMechanicalActivity(0.95f, 120f, 24f),
                Is.False,
                "The pulse rate cap keeps fast rotors legible.");
            Assert.That(
                combo.RecordMechanicalActivity(1.09f, 0f, 24f),
                Is.True,
                "Accumulated real travel should publish as soon as the cadence gate opens.");
            Assert.That(combo.Snapshot.Count, Is.EqualTo(4));

            Assert.That(combo.Tick(3.40f), Is.False,
                "A real activity pulse extends the visible combo window.");
            Assert.That(combo.Tick(3.50f), Is.True);
            Assert.That(combo.Snapshot, Is.EqualTo(SpinnerComboSnapshot.Rest));

            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            StringAssert.Contains("combo.RecordMechanicalActivity(", coordinator);
            StringAssert.Contains("!IsAssistantDriveActive()", coordinator,
                "AUTO must never farm the visual Combo counter.");
        }

        [Test]
        public void SpinRewards_EvaluateForceSpeedAndRealRevolutionsWithoutChangingPhysics()
        {
            Assert.That(
                SpinnerSpinRewardRules.Resolve(0.90f, 24f, 5.9d),
                Is.Not.EqualTo(SpinnerSpinRewardKind.PerfectSpin));
            Assert.That(
                SpinnerSpinRewardRules.Resolve(0.90f, 21.6f, 6d),
                Is.EqualTo(SpinnerSpinRewardKind.PerfectSpin));
            Assert.That(
                SpinnerSpinRewardRules.Resolve(0.90f, 12f, 12d),
                Is.EqualTo(SpinnerSpinRewardKind.Endurance));
            Assert.That(
                SpinnerSpinRewardRules.Resolve(0.55f, 26f, 4d),
                Is.EqualTo(SpinnerSpinRewardKind.SpeedRun));

            var runtime = new SpinnerSpinRewardRuntime();
            runtime.RecordGesture(0.9f, 20f);
            runtime.RecordRotation(3d * 360d, 20f);
            Assert.That(runtime.EndSpin(10f), Is.True);
            Assert.That(
                runtime.TryReveal(11.99f, out _),
                Is.False,
                "The final rating must not appear before two seconds at rest.");
            Assert.That(
                runtime.TryReveal(12f, out SpinnerSpinRewardSnapshot first),
                Is.True);
            Assert.That(first.Kind, Is.EqualTo(SpinnerSpinRewardKind.PowerSpin));
            Assert.That(first.Revolutions, Is.EqualTo(3d).Within(0.0001d));

            runtime.RecordGesture(0.9f, 24f);
            runtime.RecordRotation(6d * 360d, 24f);
            Assert.That(runtime.EndSpin(20f), Is.True);
            Assert.That(
                runtime.TryReveal(22f, out SpinnerSpinRewardSnapshot perfect),
                Is.True);
            Assert.That(perfect.Kind, Is.EqualTo(SpinnerSpinRewardKind.PerfectSpin));
            Assert.That(perfect.NormalizedForce, Is.EqualTo(0.9f));
            Assert.That(perfect.PeakAngularSpeedRadians, Is.EqualTo(24f));
            Assert.That(runtime.TryReveal(30f, out _), Is.False,
                "One stopped spin must publish exactly one final rating.");

            runtime.Reset();
            runtime.RecordRotation(20d * 360d, 30f);
            Assert.That(runtime.EndSpin(40f), Is.False,
                "Movement without a new explicit gesture must never earn a reward.");
        }

        [Test]
        public void ExperienceVisuals_KeepBackgroundDarkAndGateFireSparksByRealSpeed()
        {
            Color overdrive = SpinnerExperienceVisualRules.ResolveDarkBackground(
                SpinnerComboTier.Overdrive,
                SpinnerSpinRewardKind.None);
            Assert.That(Mathf.Max(overdrive.r, overdrive.g, overdrive.b), Is.LessThan(0.15f));
            Assert.That(overdrive.maxColorComponent, Is.GreaterThan(0f));
            Assert.That(
                SpinnerExperienceVisualRules.ResolveSparkRate(21.5f),
                Is.Zero);
            Assert.That(
                SpinnerExperienceVisualRules.ResolveSparkRate(30f),
                Is.EqualTo(SpinnerExperienceVisualRules.MaximumSparkRate).Within(0.001f));
        }

        [Test]
        public void VisualAssembly_AppliesFiveRealMaterialAndComponentStagesWithoutPhysics()
        {
            var rotor = new GameObject("ProgressionVisualTestRotor");
            GameObject sourceVisual = GameObject.CreatePrimitive(PrimitiveType.Cube);
            sourceVisual.name = "SourceSpinnerVisual";
            sourceVisual.transform.SetParent(rotor.transform, false);
            sourceVisual.transform.localScale = new Vector3(0.12f, 0.012f, 0.12f);

            try
            {
                SpinnerProgressionVisuals visuals =
                    rotor.AddComponent<SpinnerProgressionVisuals>();

                visuals.Apply("test-model", 1);
                Assert.That(visuals.ActiveStageIndex, Is.EqualTo(0));
                Assert.That(visuals.ActiveMaterialName, Does.Contain("001"));
                Assert.That(visuals.WeightRingVisible, Is.False);

                visuals.Apply("test-model", 20);
                Assert.That(visuals.ActiveStageIndex, Is.EqualTo(1));
                Assert.That(visuals.WeightRingVisible, Is.True);
                Assert.That(visuals.AuxiliaryBearingsVisible, Is.False);

                visuals.Apply("test-model", 50);
                Assert.That(visuals.ActiveStageIndex, Is.EqualTo(2));
                Assert.That(visuals.AuxiliaryBearingsVisible, Is.True);
                Assert.That(visuals.LowResistanceCageVisible, Is.False);

                visuals.Apply("test-model", 75);
                Assert.That(visuals.ActiveStageIndex, Is.EqualTo(3));
                Assert.That(visuals.LowResistanceCageVisible, Is.True);
                Assert.That(visuals.FinalCrownVisible, Is.False);

                visuals.Apply("test-model", 100);
                Assert.That(visuals.ActiveStageIndex, Is.EqualTo(4));
                Assert.That(visuals.ActiveMaterialName, Does.Contain("100"));
                Assert.That(visuals.FinalCrownVisible, Is.True);
                Assert.That(visuals.GeneratedColliderCount, Is.Zero);
                Assert.That(rotor.GetComponent<Rigidbody>(), Is.Null);

                Transform generatedRoot = rotor.transform.Find(
                    SpinnerProgressionVisuals.VisualRootName);
                Assert.That(generatedRoot, Is.Not.Null);
                Assert.That(
                    generatedRoot.GetComponentsInChildren<Renderer>(true)
                        .Any(renderer => renderer.sharedMaterial != null
                            && renderer.sharedMaterial.name ==
                            "Progression_100_CeramicBearing"),
                    Is.True,
                    "The final stage must visibly replace steel bearing balls with ceramic ones.");
            }
            finally
            {
                Object.DestroyImmediate(rotor);
            }
        }

        [Test]
        public void ActiveExperience_UsesBothActualRevolutionsAndGestureForce()
        {
            double lowForce = SpinnerProgressionRules.ExperienceForRevolutions(10d, 0.1f);
            double highForce = SpinnerProgressionRules.ExperienceForRevolutions(10d, 0.9f);
            double twiceTheTurns = SpinnerProgressionRules.ExperienceForRevolutions(20d, 0.1f);

            Assert.That(highForce, Is.GreaterThan(lowForce * 1.25d));
            Assert.That(twiceTheTurns, Is.EqualTo(lowForce * 2d).Within(0.0001d));
            Assert.That(
                SpinnerProgressionRules.GestureExperience(1f),
                Is.GreaterThan(SpinnerProgressionRules.GestureExperience(0f)));
        }

        [Test]
        public void OfflineExperience_IsCappedNightBoostedAndAssistantAccelerated()
        {
            double ordinary = SpinnerProgressionRules.OfflineExperience(8d, false, 0d);
            double night = SpinnerProgressionRules.OfflineExperience(8d, false, 1d);
            double assisted = SpinnerProgressionRules.OfflineExperience(8d, true, 0d);
            double capped = SpinnerProgressionRules.OfflineExperience(100d, false, 0d);
            double sixteenHours = SpinnerProgressionRules.OfflineExperience(16d, false, 0d);

            Assert.That(night, Is.EqualTo(ordinary * 1.25d).Within(0.001d));
            Assert.That(assisted, Is.EqualTo(ordinary * 1.75d).Within(0.001d));
            Assert.That(capped, Is.EqualTo(sixteenHours).Within(0.001d));
            Assert.That(
                SpinnerProgressionRules.OfflineExperience(4d / 60d, true, 1d),
                Is.Zero);
        }

        [Test]
        public void TwoWeekPacing_ReachesFinalBuildAroundDayFourteen()
        {
            double experience = SpinnerProgressionRules.EstimateTwoWeekExperience(
                activeMinutesPerDay: 12d,
                averageRevolutionsPerSecond: 5d,
                averageForce: 0.6f,
                offlineHoursPerDay: 12d,
                nightFraction: 8d / 12d,
                assistantEnabled: false);

            Assert.That(
                experience,
                Is.InRange(
                    SpinnerProgressionRules.FinalExperience * 0.95d,
                    SpinnerProgressionRules.FinalExperience * 1.08d));
        }

        [Test]
        public void ThreeBladeMetalSkinCatalog_MapsAllTenLevelBandsToRealRewards()
        {
            int[] expectedLevels = { 1, 5, 10, 20, 35, 50, 65, 75, 90, 100 };
            CollectionAssert.AreEqual(
                expectedLevels,
                ThreeBladeMetalSkinCatalog.Skins.Select(skin => skin.Level).ToArray());
            Assert.That(ThreeBladeMetalSkinCatalog.Skins.Count, Is.EqualTo(10));
            Assert.That(
                ThreeBladeMetalSkinCatalog.HighestUnlocked(49).Id,
                Is.EqualTo("ice-guilloche"));
            Assert.That(
                ThreeBladeMetalSkinCatalog.Resolve("mirror-aurora", 20).Id,
                Is.EqualTo("tungsten-honeycomb"),
                "A locked selection must fall back to the newest unlocked skin.");
            Assert.That(
                ThreeBladeMetalSkinCatalog.Resolve("blue-damascus", 100).Id,
                Is.EqualTo("blue-damascus"),
                "Older unlocked skins remain equipable.");

            string payload = ThreeBladeMetalSkinCatalog.CatalogPayload();
            Assert.That(payload.Split('\n').Length, Is.EqualTo(10));
            StringAssert.Contains("夜航刻度", payload);
            StringAssert.Contains("大马士革水波纹", payload);
            StringAssert.Contains("陶瓷主轴承 + 镜钢完成体", payload);
            StringAssert.Contains("齐平青蓝蚀刻", payload);
            StringAssert.DoesNotContain("配重钉", payload,
                "Skin metadata must not promise floating hardware that the physical shell cannot support.");
        }

        [Test]
        public void AppearanceLongPress_RequiresAStationaryProductHold()
        {
            var gesture = new ProductAppearanceLongPressGesture();

            gesture.Begin(true, Vector2.zero, 10f);
            Assert.That(
                gesture.Update(true, new Vector2(5f, 0f), 10.54f),
                Is.False);
            Assert.That(
                gesture.Update(true, new Vector2(5f, 0f), 10.56f),
                Is.True,
                "A valid hold should trigger once after the frame-rate-independent threshold.");
            Assert.That(
                gesture.Update(true, new Vector2(5f, 0f), 11f),
                Is.False,
                "One hold must not present the editor twice.");

            gesture.Begin(true, Vector2.zero, 20f);
            Assert.That(
                gesture.Update(
                    true,
                    new Vector2(
                        ProductAppearanceLongPressGesture.MaximumMovementPoints + 0.1f,
                        0f),
                    20.56f),
                Is.False,
                "A drag is not a model long press.");
            Assert.That(gesture.IsTracking, Is.False);

            gesture.Begin(false, Vector2.zero, 30f);
            Assert.That(gesture.Update(true, Vector2.zero, 31f), Is.False,
                "A hold that starts away from the model must be ignored.");

            gesture.Begin(true, Vector2.zero, 40f);
            Assert.That(gesture.Update(false, Vector2.zero, 40.2f), Is.False);
            Assert.That(gesture.IsTracking, Is.False);
        }

        [Test]
        public void AppearanceActivation_PopsThenPresentsHalfSheetExactlyOnce()
        {
            var sequence = new ProductAppearanceActivationSequence();
            const float startTime = 10f;

            Assert.That(sequence.Begin(startTime), Is.True);
            Assert.That(sequence.Begin(startTime + 0.01f), Is.False,
                "A second hold cannot restart an active entrance response.");

            ProductAppearanceActivationSample initial = sequence.Update(startTime);
            Assert.That(initial.ApparentScale, Is.EqualTo(1f).Within(0.0001f));
            Assert.That(initial.ShouldPresentHalfSheet, Is.False);

            ProductAppearanceActivationSample peak = sequence.Update(
                startTime + ProductAppearanceActivationSequence.PeakTimeSeconds);
            Assert.That(
                peak.ApparentScale,
                Is.EqualTo(ProductAppearanceActivationSequence.PeakScale)
                    .Within(0.0001f));

            ProductAppearanceActivationSample settle = sequence.Update(
                startTime + ProductAppearanceActivationSequence.SettleTimeSeconds);
            Assert.That(
                settle.ApparentScale,
                Is.EqualTo(ProductAppearanceActivationSequence.SettleScale)
                    .Within(0.0001f));
            Assert.That(settle.ShouldPresentHalfSheet, Is.False);

            ProductAppearanceActivationSample complete = sequence.Update(
                startTime + ProductAppearanceActivationSequence.DurationSeconds + 0.001f);
            Assert.That(complete.ApparentScale, Is.EqualTo(1f).Within(0.0001f));
            Assert.That(complete.ShouldPresentHalfSheet, Is.True,
                "The half sheet opens only after the visual settles to rest.");
            Assert.That(sequence.IsActive, Is.False);
            Assert.That(
                sequence.Update(startTime + 1f).ShouldPresentHalfSheet,
                Is.False,
                "Completion is a one-shot signal.");
        }

        [Test]
        public void AppearanceHitTesting_AcceptsMetalCenterCapSiblingSurface()
        {
            var cameraObject = new GameObject("AppearanceHitCamera");
            var productRoot = new GameObject("AppearanceHitProduct");
            try
            {
                Camera camera = cameraObject.AddComponent<Camera>();
                camera.transform.position = new Vector3(0f, 0f, -3f);
                camera.transform.LookAt(Vector3.zero);

                var rotorObject = new GameObject("RotorDynamic");
                rotorObject.transform.SetParent(productRoot.transform, false);
                Rigidbody rotorBody = rotorObject.AddComponent<Rigidbody>();
                rotorBody.useGravity = false;
                RotorRigidbodyController rotor =
                    rotorObject.AddComponent<RotorRigidbodyController>();

                GameObject centerCap = GameObject.CreatePrimitive(PrimitiveType.Cube);
                centerCap.name = "TopCap";
                centerCap.transform.SetParent(productRoot.transform, false);
                centerCap.transform.localScale = new Vector3(0.8f, 0.8f, 0.1f);
                centerCap.AddComponent<SpinnerTouchSurface>();

                MobileGestureController gestures =
                    productRoot.AddComponent<MobileGestureController>();
                gestures.Configure(rotor, camera, null);
                Physics.SyncTransforms();

                Vector2 center = camera.WorldToScreenPoint(centerCap.transform.position);
                Assert.That(
                    ProductAppearanceHitTester.ContainsScreenPoint(
                        center,
                        null,
                        gestures,
                        null,
                        rotor.transform,
                        camera),
                    Is.True,
                    "The fixed center cap is a sibling of RotorDynamic but is still "
                    + "the model's authoritative SpinnerTouchSurface.");
                Assert.That(
                    ProductAppearanceHitTester.ContainsScreenPoint(
                        new Vector2(-10000f, -10000f),
                        null,
                        gestures,
                        null,
                        rotor.transform,
                        camera),
                    Is.False,
                    "A hold far away from the product must remain ignored.");
            }
            finally
            {
                Object.DestroyImmediate(productRoot);
                Object.DestroyImmediate(cameraObject);
            }
        }

        [Test]
        public void DefaultStickerCatalogAndPresenter_ArePersistentVisualOnlyAssets()
        {
            Assert.That(ProductStickerCatalog.Stickers.Count, Is.EqualTo(25));
            Assert.That(ProductStickerCatalog.Stickers[0].Id, Is.EqualTo("none"));
            Assert.That(
                ProductStickerCatalog.Resolve("charge-bolt").Id,
                Is.EqualTo("20-warning-triangle"),
                "Previously persisted placeholder IDs must migrate to designer art.");
            Assert.That(ProductStickerCatalog.Resolve("unknown").Id, Is.EqualTo("none"));
            Assert.That(ProductStickerCatalog.CatalogPayload().Split('\n').Length, Is.EqualTo(25));
            Shader engravingShader = Resources.Load<Shader>(
                ProductStickerPresenter.LaserEngravingShaderResourcePath);
            Assert.That(engravingShader, Is.Not.Null,
                "The laser engraving shader must be bundled through Resources.");
            Assert.That(
                engravingShader.name,
                Is.EqualTo(ProductStickerPresenter.LaserEngravingShaderName));
            string appearanceSource = File.ReadAllText(
                "Assets/Scripts/Product/ProductAppearanceCustomization.cs");
            StringAssert.DoesNotContain(
                "CreatePrimitive(PrimitiveType.Quad)",
                appearanceSource,
                "A laser engraving may not regress to a floating plane.");
            StringAssert.Contains(
                "Quaternion.LookRotation(\n                -projectionNormalWorld",
                appearanceSource,
                "The engraving projector's X axis must not mirror text artwork.");
            string engravingShaderSource = File.ReadAllText(
                "Assets/Resources/ProductStickers/ProductLaserEngraving.shader");
            StringAssert.Contains("_ReceiverToProjector", engravingShaderSource);
            StringAssert.Contains("_ProjectionNormalOS", engravingShaderSource);
            StringAssert.Contains("_SurfaceLift", engravingShaderSource);
            StringAssert.Contains("ZWrite On", engravingShaderSource);
            StringAssert.Contains("AlphaToMask On", engravingShaderSource);
            StringAssert.Contains("Cull Back", engravingShaderSource);
            StringAssert.Contains("fwidth(input.uv)", engravingShaderSource);
            StringAssert.Contains("inwardEdge", engravingShaderSource);
            StringAssert.Contains(
                "normalize(input.normalOS) * _SurfaceLift",
                engravingShaderSource,
                "The depth separation must follow the real curved surface normal.");
            StringAssert.Contains(
                "clip(surfaceAlignment - _SurfaceAlignment)",
                engravingShaderSource,
                "Only the physical top-facing receiver triangles may be marked.");

            for (int index = 1; index < ProductStickerCatalog.Stickers.Count; index++)
            {
                ProductStickerDefinition definition =
                    ProductStickerCatalog.Stickers[index];
                Texture2D artwork = Resources.Load<Texture2D>(
                    ProductStickerCatalog.ArtworkResourceRoot
                    + "/"
                    + definition.ArtworkAssetName);
                Assert.That(artwork, Is.Not.Null, definition.Id);
                Assert.That(artwork.width, Is.EqualTo(1024), definition.Id);
                Assert.That(artwork.height, Is.EqualTo(1024), definition.Id);

                string artworkPath = Path.Combine(
                    "Assets/Resources/ProductStickers/BackdropWhite",
                    definition.ArtworkAssetName + ".png");
                AssertStickerArtworkCentered(artworkPath, definition.Id);
                TextureImporter importer =
                    AssetImporter.GetAtPath(artworkPath) as TextureImporter;
                Assert.That(importer, Is.Not.Null, definition.Id);
                Assert.That(importer.mipmapEnabled, Is.True, definition.Id);
                Assert.That(
                    importer.mipMapsPreserveCoverage,
                    Is.True,
                    definition.Id);
                Assert.That(importer.anisoLevel, Is.EqualTo(8), definition.Id);
                Assert.That(
                    importer.GetPlatformTextureSettings("iPhone").format,
                    Is.EqualTo(TextureImporterFormat.ASTC_4x4),
                    definition.Id);

                string vectorPath = Path.Combine(
                    "Assets/Art/ProductStickers/Vector",
                    definition.ArtworkAssetName + ".svg");
                Assert.That(File.Exists(vectorPath), Is.True, definition.Id);
                string vectorSource = File.ReadAllText(vectorPath);
                StringAssert.Contains(
                    "viewBox=\"0 0 256.000000 256.000000\"",
                    vectorSource,
                    definition.Id);
                StringAssert.Contains("fill=\"#ffffff\"", vectorSource, definition.Id);
            }

            var product = new GameObject("StickerProduct");
            var cameraObject = new GameObject("StickerCamera");
            try
            {
                GameObject body = GameObject.CreatePrimitive(PrimitiveType.Cube);
                body.name = "VisualBody";
                body.transform.SetParent(product.transform, false);
                body.transform.localScale = new Vector3(1.2f, 0.8f, 0.15f);

                Camera camera = cameraObject.AddComponent<Camera>();
                camera.transform.position = new Vector3(0f, 0f, -3f);
                camera.transform.LookAt(Vector3.zero);

                ProductStickerPresenter presenter =
                    product.AddComponent<ProductStickerPresenter>();
                Texture2D appliedArtwork = Resources.Load<Texture2D>(
                    ProductStickerCatalog.ArtworkResourceRoot + "/10-meteor");
                presenter.Apply("10-meteor", camera);

                Assert.That(presenter.AppliedStickerId, Is.EqualTo("10-meteor"));
                Assert.That(presenter.HasAppliedSticker, Is.True);
                Assert.That(presenter.GeneratedColliderCount, Is.Zero,
                    "The engraving must never alter touch or physics geometry.");
                Assert.That(presenter.UsesConformalReceiverMeshes, Is.True);
                Assert.That(presenter.GeneratedSurfaceCount, Is.EqualTo(1));
                Assert.That(product.GetComponents<Rigidbody>().Length, Is.Zero);
                Transform sticker = product.transform.Find(
                    ProductStickerPresenter.StickerRootName);
                Assert.That(sticker, Is.Not.Null);
                Assert.That(sticker.gameObject.activeSelf, Is.True);
                Assert.That(sticker.GetComponent<MeshRenderer>(), Is.Null,
                    "The engraving root must not be a floating Quad renderer.");
                Transform conformalSurface = body.transform.Find(
                    ProductStickerPresenter.EngravingSurfaceNamePrefix + body.name);
                Assert.That(conformalSurface, Is.Not.Null);
                Assert.That(conformalSurface.localPosition, Is.EqualTo(Vector3.zero));
                Assert.That(conformalSurface.localRotation, Is.EqualTo(Quaternion.identity));
                Assert.That(conformalSurface.localScale, Is.EqualTo(Vector3.one));
                Assert.That(
                    conformalSurface.GetComponent<MeshFilter>().sharedMesh,
                    Is.SameAs(body.GetComponent<MeshFilter>().sharedMesh),
                    "Laser marks must reuse the receiver mesh instead of a plane.");
                MeshRenderer engraving = conformalSurface.GetComponent<MeshRenderer>();
                Assert.That(engraving, Is.Not.Null);
                Assert.That(
                    engraving.sharedMaterial.shader.name,
                    Is.EqualTo(ProductStickerPresenter.LaserEngravingShaderName));
                Assert.That(
                    engraving.sharedMaterial.GetTexture("_BaseMap"),
                    Is.SameAs(appliedArtwork));
                Assert.That(
                    engraving.sharedMaterial.GetColor("_EngraveColor").grayscale,
                    Is.LessThan(0.10f),
                    "Model artwork must render as a dark laser cut, not a white sticker.");
                Assert.That(
                    engraving.sharedMaterial.GetFloat("_Strength"),
                    Is.EqualTo(0.94f).Within(0.001f));
                Assert.That(
                    engraving.sharedMaterial.GetFloat("_BevelStrength"),
                    Is.EqualTo(0.88f).Within(0.001f),
                    "A screen-aware machined edge keeps the etch legible on dark metal.");
                Assert.That(
                    engraving.sharedMaterial.GetFloat("_SurfaceAlignment"),
                    Is.InRange(0.08f, 0.20f),
                    "A curved top cap must not lose the mark on its oblique slopes.");
                Assert.That(
                    engraving.sharedMaterial.GetFloat("_SurfaceLift"),
                    Is.EqualTo(0.00018f).Within(0.000001f),
                    "The mark needs a restrained but stable curved-surface separation.");
                Assert.That(engraving.sharedMaterial.renderQueue, Is.EqualTo(2475));
                var properties = new MaterialPropertyBlock();
                engraving.GetPropertyBlock(properties);
                Vector4 projectionNormal = properties
                    .GetVector("_ProjectionNormalOS")
                    .normalized;
                Assert.That(projectionNormal.x, Is.EqualTo(0f).Within(0.001f));
                Assert.That(projectionNormal.y, Is.EqualTo(1f).Within(0.001f));
                Assert.That(projectionNormal.z, Is.EqualTo(0f).Within(0.001f));
                Assert.That(
                    projectionNormal.w,
                    Is.EqualTo(0f).Within(0.001f),
                    "The mark must be projected onto the product's physical top face.");

                presenter.Apply("none", camera);
                Assert.That(presenter.AppliedStickerId, Is.EqualTo("none"));
                Assert.That(presenter.HasAppliedSticker, Is.True);
                Assert.That(sticker.gameObject.activeSelf, Is.False);
                Assert.That(conformalSurface.gameObject.activeSelf, Is.False);
            }
            finally
            {
                Object.DestroyImmediate(product);
                Object.DestroyImmediate(cameraObject);
            }
        }

        [Test]
        public void ConformalEngraving_UsesActualMetalTopCapAndStaysVisible()
        {
            UnityEngine.SceneManagement.Scene scene =
                UnityEditor.SceneManagement.EditorSceneManager.OpenScene(
                    "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity",
                    UnityEditor.SceneManagement.OpenSceneMode.Single);
            GameObject productRoot = scene.GetRootGameObjects()
                .First(root => root.name == "ThreeBladeEDC_Root");
            Transform rotor = productRoot.transform.Find("RotorDynamic");
            Transform legacyTopCap = productRoot.transform.Find("HubStatic/TopCap");
            Transform visibleTopCap = productRoot.transform.Find(
                "HubStatic/TopCap/TopCap_Root/FingerCapTop_BrushedFace");
            Transform structuralTopCap = productRoot.transform.Find(
                "HubStatic/TopCap/TopCap_Root/FingerCap_Top");
            Assert.That(rotor, Is.Not.Null);
            Assert.That(legacyTopCap, Is.Not.Null);
            Assert.That(visibleTopCap, Is.Not.Null);
            Assert.That(structuralTopCap, Is.Not.Null);
            Assert.That(
                legacyTopCap.GetComponent<MeshRenderer>().enabled,
                Is.False,
                "The superseded procedural cap is intentionally hidden.");
            Assert.That(
                visibleTopCap.GetComponent<MeshRenderer>().enabled,
                Is.True,
                "The imported brushed face is the physical top surface the user sees.");
            Assert.That(
                visibleTopCap.localPosition.z,
                Is.GreaterThan(structuralTopCap.localPosition.z),
                "The engraving receiver must be above the structural cap shell.");

            ProductStickerPresenter presenter =
                productRoot.AddComponent<ProductStickerPresenter>();
            try
            {
                presenter.Apply("10-meteor", Camera.main);
                Assert.That(presenter.AppliedStickerId, Is.EqualTo("10-meteor"));
                Assert.That(presenter.UsesTopCapReceiver, Is.True);
                Assert.That(presenter.GeneratedSurfaceCount, Is.EqualTo(1));
                Assert.That(presenter.GeneratedColliderCount, Is.Zero);

                MeshRenderer[] engravingRenderers = productRoot
                    .GetComponentsInChildren<MeshRenderer>(true)
                    .Where(renderer => renderer.gameObject.name.StartsWith(
                        ProductStickerPresenter.EngravingSurfaceNamePrefix))
                    .ToArray();
                Assert.That(engravingRenderers.Length, Is.EqualTo(1));
                foreach (MeshRenderer engraving in engravingRenderers)
                {
                    Transform surface = engraving.transform;
                    MeshRenderer receiver = surface.parent.GetComponent<MeshRenderer>();
                    Assert.That(receiver, Is.Not.Null);
                    Assert.That(receiver.transform, Is.SameAs(visibleTopCap));
                    Assert.That(surface.localPosition, Is.EqualTo(Vector3.zero));
                    Assert.That(surface.localRotation, Is.EqualTo(Quaternion.identity));
                    Assert.That(surface.localScale, Is.EqualTo(Vector3.one));
                    Assert.That(
                        surface.GetComponent<MeshFilter>().sharedMesh,
                        Is.SameAs(receiver.GetComponent<MeshFilter>().sharedMesh),
                        receiver.name);
                    Assert.That(surface.GetComponent<Collider>(), Is.Null);
                    Assert.That(
                        surface.IsChildOf(visibleTopCap),
                        Is.True,
                        "The mark must sit on the topmost imported metal face, not the occluded shell.");
                }
            }
            finally
            {
                Object.DestroyImmediate(presenter);
            }
        }

        [Test]
        public void LongPressAppearanceEditor_UsesSharedUiAndConfirmedUnitySelections()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string appearance = File.ReadAllText(
                "Assets/Scripts/Product/ProductAppearanceCustomization.cs");
            string progression = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerProgression.cs");
            string blueCamera = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/PortraitCameraFramer.cs");
            string metalCamera = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Presentation/OrbitPresentationCamera.cs");
            string edcCamera = File.ReadAllText(
                "Assets/_EDC/Runtime/EdcPortraitCameraFramer.cs");
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");

            StringAssert.Contains("UpdateAppearanceLongPressInput", coordinator);
            StringAssert.Contains("TryHitActiveProduct", coordinator);
            StringAssert.Contains("ProductAppearanceHitTester.ContainsScreenPoint", coordinator);
            StringAssert.Contains("SetProductInteractionEnabled(false)", coordinator);
            StringAssert.Contains("ProductAppearanceActivationSequence", coordinator);
            StringAssert.Contains(
                "FidgetHapticRouter.Emit(FidgetSemanticEvent.Pop)",
                coordinator);
            StringAssert.Contains("sample.ShouldPresentHalfSheet", coordinator);
            StringAssert.Contains(
                "ProductAppearanceNativeBridge.SetPresented(true)",
                coordinator);
            StringAssert.Contains("SetAppearanceActivationScale", blueCamera);
            StringAssert.Contains("SetAppearanceActivationScale", metalCamera);
            StringAssert.Contains("SetAppearanceActivationScale", edcCamera);
            StringAssert.Contains("SetAppearanceEditorPresentedFromNativeUi", coordinator);
            StringAssert.Contains("SetProductStickerFromNativeUi", coordinator);
            StringAssert.Contains("ProductStickerSelectionKeyPrefix", coordinator);
            StringAssert.Contains("ProductStickerReceiverRoot", coordinator);
            StringAssert.Contains("productRoot.Find(\"HubStatic\")", coordinator);
            StringAssert.Contains("hub.Find(\"TopCap\")", coordinator);
            StringAssert.Contains("ProductStickerCatalog.CatalogPayload()", progression);
            StringAssert.Contains("ProductAppearanceEditor", swift);
            StringAssert.Contains("LazyVGrid(columns: columns", swift);
            StringAssert.Contains("ProductIconSegmentedControl(", swift);
            StringAssert.Contains("ProductSelectionCard(", swift);
            StringAssert.Contains("sticker.thumbnailAssetName", swift);
            StringAssert.Contains("fitsInside: sticker.id != \"none\"", swift);
            StringAssert.Contains("setModeBarVisible(false)", swift);
            StringAssert.Contains("equippedProductStickerId", swift);
            StringAssert.DoesNotContain(
                "equippedProductStickerId = sticker.id",
                swift,
                "The UI must wait for Unity's applied sticker confirmation.");
            StringAssert.DoesNotContain("IosHaptics", appearance);
            StringAssert.DoesNotContain("Rigidbody", appearance);
        }

        [Test]
        public void ThreeBladeMetalSkins_ApplyEveryAuthoredSurfaceWithoutExtraGeometry()
        {
            Shader shader = Shader.Find("Universal Render Pipeline/Lit")
                ?? Shader.Find("Standard");
            Assert.That(shader, Is.Not.Null);
            var original = new Material(shader) { name = "OriginalMetal" };
            GameObject productRoot = new GameObject("ThreeBladeProduct");
            try
            {
                GameObject hub = new GameObject("HubStatic");
                hub.transform.SetParent(productRoot.transform, false);
                AddTestRenderer(hub.transform, "TopCap", original, 2);
                AddTestRenderer(hub.transform, "TopWasher", original, 1);
                AddTestRenderer(hub.transform, "BottomWasher", original, 1);

                GameObject rotor = new GameObject("RotorDynamic");
                rotor.transform.SetParent(productRoot.transform, false);
                AddTestRenderer(rotor.transform, "ThreeBladeFrame", original, 2);
                AddTestRenderer(rotor.transform, "ThreeBladeInsets", original, 1);
                AddTestRenderer(rotor.transform, "RotorCore", original, 1);
                AddTestRenderer(rotor.transform, "RotorCoreTopTrim", original, 1);
                Rigidbody body = rotor.AddComponent<Rigidbody>();
                body.angularVelocity = Vector3.zero;

                ThreeBladeMetalSkinProgression skins =
                    rotor.AddComponent<ThreeBladeMetalSkinProgression>();
                skins.Apply(1, ThreeBladeMetalSkinCatalog.AutomaticSelectionId);
                Assert.That(skins.ActiveSkinId, Is.EqualTo("factory-silver"));
                Assert.That(skins.AppliedRendererCount, Is.EqualTo(7));
                Assert.That(skins.HasAppliedSkin, Is.True,
                    "Native UI must only report a skin after every visible product renderer uses it.");
                Assert.That(skins.IndexMarkersVisible, Is.False);
                Assert.That(skins.WeightPlugsVisible, Is.False);
                Assert.That(
                    rotor.transform.Find(ThreeBladeMetalSkinProgression.DecorationRootName),
                    Is.Null,
                    "A skin must not add floating bars or weights above the authored shell.");

                skins.Apply(20, "mirror-aurora");
                Assert.That(skins.ActiveSkinId, Is.EqualTo("tungsten-honeycomb"));
                Assert.That(skins.IndexMarkersVisible, Is.False);
                StringAssert.Contains("tungsten-honeycomb", skins.FrameBodyMaterialName);
                Assert.That(skins.HasAppliedSkin, Is.True);

                skins.Apply(65, "copper-circuit");
                Assert.That(skins.WeightPlugsVisible, Is.False);
                Assert.That(skins.GeneratedColliderCount, Is.Zero);
                Assert.That(rotor.GetComponents<Rigidbody>().Length, Is.EqualTo(1));
                Assert.That(body.angularVelocity, Is.EqualTo(Vector3.zero));
            }
            finally
            {
                Object.DestroyImmediate(productRoot);
                Object.DestroyImmediate(original);
            }
        }

        [Test]
        public void ThreeBladeMetalSkins_TargetEnabledDragonScaleModelInMetalScene()
        {
            UnityEngine.SceneManagement.Scene scene =
                UnityEditor.SceneManagement.EditorSceneManager.OpenScene(
                    "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity",
                    UnityEditor.SceneManagement.OpenSceneMode.Single);
            GameObject productRoot = scene.GetRootGameObjects()
                .First(root => root.name == "ThreeBladeEDC_Root");
            Transform rotor = productRoot.transform.Find("RotorDynamic");
            MeshRenderer hiddenLegacyFrame = rotor
                .Find("ThreeBladeFrame")
                .GetComponent<MeshRenderer>();
            MeshRenderer visibleBody = rotor
                .Find("Rotor_Root/RotorBody_OnePiece")
                .GetComponent<MeshRenderer>();
            MeshRenderer visibleTopCap = productRoot.transform
                .Find("HubStatic/TopCap/TopCap_Root/FingerCap_Top")
                .GetComponent<MeshRenderer>();
            Assert.That(hiddenLegacyFrame.enabled, Is.False);
            Assert.That(visibleBody.enabled, Is.True);
            Assert.That(visibleTopCap.enabled, Is.True);
            Material originalVisibleBody = visibleBody.sharedMaterial;

            ThreeBladeMetalSkinProgression skins =
                rotor.gameObject.AddComponent<ThreeBladeMetalSkinProgression>();
            try
            {
                skins.Apply(10, "night-cyan-index");

                Assert.That(skins.ActiveSkinId, Is.EqualTo("night-cyan-index"));
                Assert.That(skins.AppliedRendererCount, Is.GreaterThan(8));
                Assert.That(skins.HasAppliedSkin, Is.True);
                Assert.That(visibleBody.sharedMaterial, Is.Not.SameAs(originalVisibleBody));
                StringAssert.Contains("night-cyan-index", visibleBody.sharedMaterial.name);
                StringAssert.Contains("night-cyan-index", visibleTopCap.sharedMaterial.name);
                Assert.That(
                    visibleBody.sharedMaterial.GetTexture("_BaseMap"),
                    Is.Not.Null,
                    "The dark-blue skin texture must land on the visible authored body.");
                Assert.That(
                    rotor.Find(ThreeBladeMetalSkinProgression.DecorationRootName),
                    Is.Null);
                Assert.That(
                    rotor.Find(SpinnerProgressionVisuals.VisualRootName),
                    Is.Null);
                Assert.That(hiddenLegacyFrame.sharedMaterial, Is.Not.SameAs(visibleBody.sharedMaterial));
            }
            finally
            {
                Object.DestroyImmediate(skins);
            }
        }

        [Test]
        public void ThreeBladeMetalSkinSelection_IsPersistedAndBridgedWithoutRawHaptics()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string progression = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerProgression.cs");
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");

            StringAssert.Contains("SetThreeBladeMetalSkinFromNativeUi", coordinator);
            StringAssert.Contains("ThreeBladeMetalSkinSelectionKey", coordinator);
            StringAssert.Contains("usesIntegratedThreeBladeSkins", coordinator);
            StringAssert.Contains("if (!usesIntegratedThreeBladeSkins)", coordinator,
                "The three-blade model must not receive generic floating progression geometry.");
            StringAssert.Contains("FidgetHapticRouter.Emit(FidgetSemanticEvent.Selection)", coordinator);
            StringAssert.DoesNotContain("IosHaptics", File.ReadAllText(
                "Assets/Scripts/Product/ThreeBladeMetalSkinProgression.cs"));
            StringAssert.Contains("ThreeBladeMetalSkinCatalog.CatalogPayload()", progression);
            StringAssert.Contains("ThreeBladeMetalSkinRow", swift);
            StringAssert.Contains("贴纸 / 纹饰：", swift);
            StringAssert.Contains("配件：", swift);
            StringAssert.Contains("equippedThreeBladeMetalSkinId", swift);
            StringAssert.DoesNotContain(
                "equippedThreeBladeMetalSkinId = skin.id",
                swift,
                "Native UI must wait for Unity renderer confirmation before showing equipped.");
            StringAssert.Contains("HasAppliedSkin", coordinator);
        }

        [Test]
        public void RuntimeAndLiquidGlassUi_AreWiredForGrowthAndOfflineReturn()
        {
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string classic = File.ReadAllText(
                "Assets/Scripts/FidgetSpinner/FidgetSpinnerController.cs");
            string metal = File.ReadAllText(
                "Assets/_Fidgeting/Runtime/Interaction/MobileGestureController.cs");
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = File.ReadAllText(
                "Assets/Plugins/iOS/FidgetProductUIComponents.swift");
            string designGuideline = File.ReadAllText(
                "Docs/LiquidGlassDesignGuideline.md");
            string experienceVisuals = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerExperienceVisuals.cs");

            StringAssert.Contains("RecordRotationDegrees", coordinator);
            StringAssert.Contains("SpinGestureCompleted +=", coordinator);
            StringAssert.Contains("libraryPreviewActive", coordinator);
            StringAssert.Contains("MaximumCreditableRotationPerFrame", coordinator);
            StringAssert.Contains("ConfigureProgressionVisuals", coordinator);
            StringAssert.Contains("ApplyProgressionVisualStage", coordinator);
            StringAssert.Contains("SpinGestureCompleted?.Invoke", classic);
            StringAssert.Contains("SpinGestureCompleted?.Invoke", metal);
            StringAssert.Contains("SpinnerProgressionHUD", swift);
            StringAssert.Contains("ProgressionUnlockThumbnail", swift);
            StringAssert.Contains("model: state.selectedModel", swift);
            StringAssert.Contains("skin: unlockSkin(for: detail.level)", swift);
            StringAssert.Contains("assetName: model.thumbnailAssetName", swift);
            StringAssert.Contains("ProductProgressGauge(", swift);
            StringAssert.Contains("struct ProductProgressGauge", components);
            StringAssert.Contains("min(1, max(0, value))", components);
            StringAssert.Contains("Text(\"AUTO\")", swift);
            StringAssert.Contains("[1.0, 1.5, 2.0, 3.0]", swift);
            StringAssert.Contains("setProgressionAssistantMultiplier", swift);
            StringAssert.Contains("stopProgressionAssistant", swift);
            int hudStart = swift.IndexOf("private struct SpinnerProgressionHUD");
            int hudEnd = swift.IndexOf("private struct ProgressionLevelDetailsSheet");
            string progressionHud = swift.Substring(hudStart, hudEnd - hudStart);
            int autoMenuStart = progressionHud.IndexOf("            Menu {");
            int autoMenuEnd = progressionHud.IndexOf(
                "            } label: {\n                VStack(spacing: 10)",
                autoMenuStart);
            string autoMenu = progressionHud.Substring(
                autoMenuStart,
                autoMenuEnd - autoMenuStart);
            StringAssert.DoesNotContain("lock.fill", autoMenu);
            StringAssert.DoesNotContain("PRO", progressionHud);
            StringAssert.DoesNotContain("presentAutoGate", progressionHud);
            StringAssert.DoesNotContain("ExperienceJar(", progressionHud);
            StringAssert.Contains("ZStack(alignment: .leading)", progressionHud);
            StringAssert.Contains("ProgressionMilestoneGauge(", progressionHud);
            StringAssert.Contains("previousLevel: previousMilestoneLevel", progressionHud);
            StringAssert.Contains("currentLevel: state.progressionLevel", progressionHud);
            StringAssert.Contains("nextLevel: nextMilestoneLevel", progressionHud);
            StringAssert.Contains("AutoSpeedRotorBadge(", progressionHud);
            StringAssert.Contains("VStack(spacing: 10)", progressionHud);
            StringAssert.Contains(".padding(.horizontal, 14)", progressionHud);
            StringAssert.Contains(".padding(.vertical, 10)", progressionHud);
            StringAssert.Contains(".frame(width: 80, height: 80)", progressionHud);
            StringAssert.Contains(".frame(width: 84, height: 84)", progressionHud);
            StringAssert.Contains(".product(size: 11, weight: .black)", progressionHud);
            StringAssert.Contains("Color(red: 0.30, green: 0.92, blue: 0.80)", progressionHud);
            StringAssert.Contains("? autoEnabledColor.opacity(0.96)", progressionHud);
            StringAssert.Contains("accent: autoEnabledColor", progressionHud);
            StringAssert.Contains("AutoControlGlassSurface(", progressionHud);
            StringAssert.Contains(".fill(.ultraThinMaterial)", progressionHud);
            StringAssert.Contains("LinearGradient(", progressionHud);
            StringAssert.Contains("RadialGradient(", progressionHud);
            StringAssert.Contains("coolReflection.opacity", progressionHud);
            StringAssert.Contains("accessibilityReduceTransparency", progressionHud);
            StringAssert.Contains("active ? accent.opacity(0.98)", progressionHud);
            StringAssert.Contains("active ? accent.opacity(0.24)", progressionHud);
            StringAssert.Contains("active ? accent.opacity(0.98) : Color.white.opacity(0.58)", progressionHud);
            StringAssert.Contains("value: state.progressionAssistantEnabled", progressionHud);
            StringAssert.Contains("case hudOff = \"hud-off\"", swift);
            StringAssert.Contains("state.progressionAssistantEnabled = mode == .hud", swift);
            StringAssert.Contains(
                "angularSpeedRadians: state.motionTelemetry.angularSpeedRadians",
                progressionHud);
            StringAssert.Contains("Text(multiplierText)", progressionHud);
            StringAssert.Contains("CADisplayLink(target:", progressionHud);
            StringAssert.Contains("displayLink?.invalidate()", progressionHud);
            StringAssert.Contains(
                "angularSpeedRadians * delta * 180 / .pi",
                progressionHud);
            StringAssert.DoesNotContain(
                "state.progressionNextUnlockName",
                progressionHud,
                "The bearing unlock copy should not consume a second HUD line.");
            StringAssert.Contains(
                "图标、图标容器与相邻文字之间的留白是硬性约束",
                designGuideline);
            StringAssert.Contains(
                "图标容器与 label 视觉间距不得小于 `4 pt`",
                designGuideline);
            StringAssert.Contains(
                "容器内部的 glyph、倍率数字或状态标记",
                designGuideline);
            StringAssert.DoesNotContain("progressionStageComponent", progressionHud,
                "The one-line bearing/material copy was removed from the bottom HUD.");
            StringAssert.DoesNotContain(
                "当前装配：\\(state.progressionStageComponent)",
                swift,
                "The visible standard-bearing line was removed from every progression view.");
            StringAssert.Contains("离线收获", swift);
            StringAssert.Contains("LEVEL UP", swift);
            StringAssert.Contains("CodexProgressionReceiveState", swift);
            StringAssert.Contains("ProgressionLevelDetailsSheet", swift);
            StringAssert.Contains("ProgressionLevelTimeline", swift);
            StringAssert.Contains("ProgressionVerticalRail", swift);
            StringAssert.Contains("ProgressionBadgeAchievements", swift);
            StringAssert.Contains("ProgressionCosmeticsCatalog", swift);
            StringAssert.Contains("BadgeUnlockOverlay", swift);
            StringAssert.Contains("BADGE UNLOCKED", swift);
            StringAssert.Contains("Text(\"成就\").tag(0)", swift);
            StringAssert.Contains("Text(\"Badge\").tag(1)", swift);
            StringAssert.Contains("Text(\"外观\").tag(2)", swift);
            StringAssert.Contains("SpinnerOnboardingView", swift);
            StringAssert.Contains("双指捏合控制放大缩小", swift);
            StringAssert.Contains("停止交互并停稳约 2 秒后", swift);
            StringAssert.Contains("RecordActivity", coordinator);
            StringAssert.Contains("AchievementCatalogPayload", File.ReadAllText(
                "Assets/Scripts/Product/SpinnerProgression.cs"));
            StringAssert.Contains("progressionLevelCatalog", swift);
            StringAssert.Contains("CodexComboReceiveState", swift);
            StringAssert.Contains("COMBO", swift);
            StringAssert.Contains("SpinnerExperienceFeedbackLayer", swift);
            StringAssert.Contains("CodexSpinRewardReceiveState", swift);
            StringAssert.Contains("PERFECT SPIN", swift);
            StringAssert.Contains("accessibilityHint(\"打开成长详情\")", swift);
            int feedbackStart = swift.IndexOf("private struct SpinnerExperienceFeedbackLayer");
            int feedbackEnd = swift.IndexOf("private struct SpinnerProgressionHUD");
            string feedbackLayer = swift.Substring(
                feedbackStart,
                feedbackEnd - feedbackStart);
            StringAssert.DoesNotContain("LinearGradient", feedbackLayer,
                "The native text overlay must not tint the foreground spinner.");
            StringAssert.Contains("if state.motionTelemetry.available", feedbackLayer);
            StringAssert.Contains(
                "reward: state.showingSpinReward ? state.spinReward : nil",
                feedbackLayer);
            StringAssert.Contains("Text(combo.title.uppercased())", swift);
            StringAssert.Contains(
                "ProductOverlayLayout.comboTopMinimum",
                feedbackLayer);
            StringAssert.Contains("RewardingComboLockup(", feedbackLayer);
            int metricStart = swift.IndexOf("private struct SpinnerMetricCluster");
            int metricEnd = swift.IndexOf("private enum ComboPresentationLevel");
            string metricCluster = swift.Substring(
                metricStart,
                metricEnd - metricStart);
            StringAssert.DoesNotContain("combo.title.uppercased()", metricCluster,
                "Combo tier text belongs above the 3D model, not in the bottom metrics cluster.");
            StringAssert.Contains("camera.backgroundColor", experienceVisuals);
            StringAssert.Contains("ComboLightMotes", experienceVisuals);
            StringAssert.Contains("HighSpeedFireSparks", experienceVisuals);
            StringAssert.Contains("DetentTuningPanel(state: state)", swift);
            StringAssert.DoesNotContain("detentController", swift);
            StringAssert.Contains("SpinnerComboRuntime", coordinator);
            StringAssert.Contains("SpinnerSpinRewardRuntime", coordinator);
            StringAssert.Contains(".productGlass(", swift);
        }

        [Test]
        public void SpeedDashboard_UsesVisibleCaptionsWithoutDecorativeFlames()
        {
            string combo = File.ReadAllText(
                "Assets/Scripts/Product/SpinnerCombo.cs");
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = File.ReadAllText(
                "Assets/Plugins/iOS/FidgetProductUIComponents.swift");

            Assert.That(
                SpinnerComboRules.HudUpdateIntervalSeconds,
                Is.EqualTo(0.05f));
            StringAssert.Contains("SpinnerMetricCluster", swift);
            StringAssert.Contains("ProductSpeedDashboard(", swift);
            StringAssert.Contains("struct ProductSpeedDashboard", components);
            StringAssert.Contains("struct ProductSideMetricDashboard", components);
            StringAssert.Contains("ProductDashboardSweepField", components);
            StringAssert.Contains("productDashboardGradientStops", components);
            StringAssert.DoesNotContain("ProductDashboardNeedle", components);
            StringAssert.DoesNotContain(
                ".trim(from: 0, to: clampedFraction)",
                components,
                "The sweep field itself must be the pointer; do not stack a separate active arc.");
            StringAssert.Contains(
                ".init(color: accent.opacity(0.00), location: 0.00)",
                components);
            StringAssert.Contains(
                ".init(color: accent.opacity(outerOpacity), location: 1.00)",
                components);
            StringAssert.DoesNotContain("ProductDashboardFlames", components);
            StringAssert.Contains("private struct ProductDashboardCaption", components);
            StringAssert.Contains(".frame(height: 20)", components);
            StringAssert.Contains(
                "Color.black.opacity(reduceTransparency ? 0.98 : 0.90)",
                components);
            StringAssert.Contains(".layoutPriority(2)", components);
            StringAssert.Contains(".zIndex(5)", components);
            StringAssert.Contains(
                "let gaugeHeight = min(84, max(68",
                components);
            StringAssert.Contains(
                "let gaugeHeight = min(54, max(48",
                components);
            StringAssert.Contains(
                "HStack(alignment: .firstTextBaseline, spacing: 3)",
                components);
            StringAssert.Contains(
                "HStack(alignment: .firstTextBaseline, spacing: 1)",
                components);
            StringAssert.Contains(
                "y: gaugeProxy.size.height * 0.62",
                components);
            StringAssert.Contains(
                "y: gaugeProxy.size.height * 0.64",
                components);
            StringAssert.Contains(
                "@ScaledMetric(relativeTo: .title2) private var valueSize: CGFloat = 25",
                components);
            StringAssert.Contains(
                "@ScaledMetric(relativeTo: .headline) private var valueSize: CGFloat = 17",
                components);
            StringAssert.Contains(
                ".frame(height: isAccessibilityCategory ? 148 : 118)",
                components);
            StringAssert.Contains(
                ".frame(height: sizeCategory.isAccessibilityCategory ? 98 : 78)",
                components);
            StringAssert.Contains(
                ".frame(height: sizeCategory.isAccessibilityCategory ? 148 : 118)",
                swift);
            StringAssert.Contains("title: \"SPEED\"", swift);
            StringAssert.Contains("unit: \"RPM\"", swift);
            StringAssert.Contains("telemetry.rpm", swift);
            StringAssert.DoesNotContain("AutomotiveMetricGauge", swift);
            StringAssert.Contains("title: \"INTENSITY\"", swift);
            StringAssert.Contains("title: \"FREQUENCY\"", swift);
            StringAssert.Contains("fraction: combo.intensity", swift);
            StringAssert.Contains("fraction: combo.frequency", swift);
            StringAssert.Contains(
                "HStack(alignment: .bottom, spacing: 10)",
                swift);
            StringAssert.Contains("let sideWidth = min(74", swift);
            StringAssert.Contains("max(124, proxy.size.width", swift);
            StringAssert.Contains(
                "isPeak: telemetry.speedBand == .peak",
                swift);
            StringAssert.Contains(
                "case .peak: return Color(red: 1.00, green: 0.18, blue: 0.08)",
                swift);
            StringAssert.Contains("private enum ProductOverlayLayout", swift);
            StringAssert.Contains("static let progressionHeight: CGFloat = 96", swift);
            StringAssert.Contains("static let progressionBottomInset: CGFloat = 12", swift);
            StringAssert.Contains("static let feedbackGap: CGFloat = 14", swift);
            StringAssert.Contains("static let comboTopMinimum: CGFloat = 190", swift);
            StringAssert.Contains("static let comboTopSafeAreaOffset: CGFloat = 132", swift);
            StringAssert.Contains("Spacer(minLength: 0)", swift);
            StringAssert.Contains(
                "ProductOverlayLayout.feedbackBottomClearance",
                swift);
            Assert.That(
                swift.Split(new[] { "ProductSideMetricDashboard(" },
                    System.StringSplitOptions.None).Length - 1,
                Is.EqualTo(2));
            StringAssert.Contains("angularSpeedRadians", combo);
            StringAssert.Contains("CodexMotionTelemetryReceiveState", swift);
            StringAssert.Contains("ProductMotionTelemetryNativeBridge", combo);
            StringAssert.Contains(
                "SpinnerComboRules.HudUpdateIntervalSeconds",
                coordinator);
            StringAssert.Contains(
                "PublishMotionTelemetryIfDue(angularSpeed)",
                coordinator);
            StringAssert.Contains("HasRotarySpeedTelemetry()", coordinator);
        }

        [Test]
        public void ComboPresentation_UsesNumberFirstBorderlessRewardLevelsAndIos15Fallback()
        {
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            int comboStart = swift.IndexOf("private enum ComboPresentationLevel");
            int comboEnd = swift.IndexOf("private struct SpinnerExperienceFeedbackLayer");
            string comboPresentation = swift.Substring(comboStart, comboEnd - comboStart);
            int feedbackStart = swift.IndexOf("private struct SpinnerExperienceFeedbackLayer");
            int feedbackEnd = swift.IndexOf("private struct SpinnerProgressionHUD");
            string feedbackLayer = swift.Substring(feedbackStart, feedbackEnd - feedbackStart);

            StringAssert.Contains("case 2...4: return .ignition", comboPresentation);
            StringAssert.Contains("case 5...9: return .boost", comboPresentation);
            StringAssert.Contains("case 10...19: return .burst", comboPresentation);
            StringAssert.Contains("count >= 20 ? .peak", comboPresentation);
            StringAssert.Contains("if count == 5 { return .sweep }", comboPresentation);
            StringAssert.Contains("if count == 10 { return .echo }", comboPresentation);
            StringAssert.Contains(
                "count >= 20 && count % 10 == 0",
                comboPresentation);
            StringAssert.Contains("case .ignition: return 1.14", comboPresentation);
            StringAssert.Contains("case .boost: return 1.20", comboPresentation);
            StringAssert.Contains("case .burst: return 1.27", comboPresentation);
            StringAssert.Contains("case .peak: return 1.32", comboPresentation);
            StringAssert.Contains("activeEffect == .peakBurst ? 1.40", comboPresentation);
            StringAssert.Contains("case .ignition: return 42", comboPresentation);
            StringAssert.Contains("case .boost: return 47", comboPresentation);
            StringAssert.Contains("case .burst: return 52", comboPresentation);
            StringAssert.Contains("case .peak: return 58", comboPresentation);
            StringAssert.Contains(".combo(", comboPresentation);
            StringAssert.Contains(".monospacedDigit()", comboPresentation);
            StringAssert.Contains(
                ".frame(width: 112, height: 62, alignment: .center)",
                comboPresentation);
            StringAssert.Contains("outgoingOffset = -12", comboPresentation);
            StringAssert.Contains("incomingOffset = 14", comboPresentation);
            StringAssert.Contains("numberWidthScale = 1.08", comboPresentation);
            StringAssert.Contains("numberHeightScale = 0.82", comboPresentation);
            StringAssert.Contains("numberGlowPulse = 1", comboPresentation);
            StringAssert.Contains("Text(\"×\")", comboPresentation);
            StringAssert.Contains(".mask(", comboPresentation);
            StringAssert.Contains("RadialGradient(", comboPresentation);
            StringAssert.Contains("private struct RewardingComboLockup", comboPresentation);
            StringAssert.DoesNotContain("RewardingComboPill", comboPresentation);
            StringAssert.DoesNotContain(".stroke(", comboPresentation,
                "The Combo treatment must not regress to a ticket or pill outline.");
            StringAssert.DoesNotContain(".productGlass(", comboPresentation,
                "The number-first Combo lockup must float over the model without a pill container.");
            StringAssert.DoesNotContain("combo.accent", comboPresentation,
                "Combo typography and number feedback must stay neutral white.");
            StringAssert.Contains("static let windUpSeconds = 0.045", comboPresentation);
            StringAssert.Contains("static let handoffSeconds = 0.085", comboPresentation);
            StringAssert.Contains("static let reducedMotionCrossfadeSeconds = 0.11", comboPresentation);
            StringAssert.Contains("if !reduceMotion", comboPresentation);
            StringAssert.Contains("playReducedMotionChange", comboPresentation);
            StringAssert.Contains("private struct ComboPresentationKey: Equatable", comboPresentation);
            StringAssert.Contains(".onChange(of: presentationKey)", comboPresentation);
            StringAssert.DoesNotContain(".onChange(of: combo)", comboPresentation,
                "20 Hz telemetry-only snapshots must not restart the combo animation.");
            StringAssert.Contains("if newCombo.count == oldCount", comboPresentation);
            StringAssert.Contains("playTierChange", comboPresentation);
            StringAssert.Contains("animationGeneration == token", comboPresentation);
            StringAssert.Contains(".frame(width: 124, height: 82)", comboPresentation);
            StringAssert.Contains("count: activeEffect == .echo ? 4 : 8", comboPresentation);
            StringAssert.Contains("accessibilityLabel(\"\\(combo.count) 连击，\\(combo.title)\")", comboPresentation);
            StringAssert.DoesNotContain("UnityBridge.feedback", comboPresentation);
            StringAssert.DoesNotContain("UIImpactFeedbackGenerator", comboPresentation);
            StringAssert.DoesNotContain("AudioServices", comboPresentation);
            StringAssert.DoesNotContain("numericText", comboPresentation,
                "iOS 15 must receive the complete old/new digit transition.");
            StringAssert.DoesNotContain("KeyframeAnimator", comboPresentation,
                "iOS 15 must not depend on an iOS 17-only animation path.");
            StringAssert.Contains("ProductOverlayLayout.comboTopMinimum", feedbackLayer);
            StringAssert.Contains("ProductOverlayLayout.comboTopSafeAreaOffset", feedbackLayer);
            StringAssert.Contains(".allowsHitTesting(false)", feedbackLayer);
            StringAssert.Contains("if reduceMotion", feedbackLayer);
            StringAssert.Contains(".transition(comboTransition)", feedbackLayer);
            StringAssert.Contains("static let breakFadeSeconds = 0.22", comboPresentation);
        }

        [Test]
        public void ComboMilestoneHalo_UsesSharedNativeCurveAndModelCenterStage()
        {
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string halo = File.ReadAllText(
                "Assets/Plugins/iOS/FidgetComboHalo.swift");
            string importer = File.ReadAllText(
                "Assets/Plugins/iOS/FidgetComboHalo.swift.meta");

            StringAssert.Contains("firstMilestone: 10", halo);
            StringAssert.Contains("repeatInterval: 10", halo);
            StringAssert.Contains("durationSeconds: 0.92", halo);
            StringAssert.Contains("endRadiusScale: 1.04", halo);
            StringAssert.Contains("peakOpacity: 0.34", halo);
            StringAssert.Contains(
                "func milestoneCrossed(previousCount: Int, newCount: Int)",
                halo);
            StringAssert.Contains("func coreFlashOpacity(at progress: Double)", halo);
            StringAssert.Contains("func primaryRingOpacity(at progress: Double)", halo);
            StringAssert.Contains("func echoRingOpacity(at progress: Double)", halo);
            StringAssert.Contains("func trailingRingOpacity(at progress: Double)", halo);
            StringAssert.Contains("func mistOpacity(at progress: Double)", halo);
            StringAssert.Contains("enum ComboHaloMilestoneStyle: Equatable", halo);
            StringAssert.Contains("if count >= 50 { return .apex }", halo);
            StringAssert.Contains("if count >= 30 { return .overdrive }", halo);
            StringAssert.Contains("case .overdrive: return 10", halo);
            StringAssert.Contains("case .apex: return 14", halo);
            StringAssert.Contains("func speedTunnelOpacity(", halo);
            StringAssert.Contains("func edgeBloomOpacity(", halo);
            StringAssert.Contains("peakScale: 0.72", halo);
            StringAssert.Contains("peakScale: 1.00", halo);
            StringAssert.Contains("peakScale: 0.65", halo);
            StringAssert.Contains("peakScale: 0.38", halo);
            StringAssert.Contains("peakScale: 0.78", halo);
            StringAssert.Contains("return nextStep <= newCount", halo);
            StringAssert.Contains("struct ComboCenterHalo: View, Animatable", halo);
            StringAssert.Contains("struct ComboHaloMistCloud: Shape", halo);
            StringAssert.Contains("struct ComboHaloBrokenRing: View", halo);
            StringAssert.Contains("struct ComboHaloMistWisps: View", halo);
            StringAssert.Contains("struct ComboHaloSpeedTunnel: View", halo);
            StringAssert.Contains(".trim(from: start, to: end)", halo);
            StringAssert.Contains("ForEach(0..<7", halo);
            StringAssert.Contains("AngularGradient(", halo);
            StringAssert.Contains("echoExpansion", halo);
            StringAssert.Contains("trailingExpansion", halo);
            StringAssert.Contains("mistExpansion", halo);
            StringAssert.Contains("speedExpansion", halo);
            StringAssert.Contains("milestoneCount: Int = 10", halo);
            StringAssert.Contains("milestoneStyle != .standard && !reduceMotion", halo);
            StringAssert.Contains(
                "var animatableData: AnimatablePair<CGFloat, CGFloat>",
                halo);
            StringAssert.Contains("opacityProgress = newValue.second", halo);
            StringAssert.Contains("struct ComboHaloProjectionState", halo);
            StringAssert.Contains("minorAxisRatio: 0.67", halo);
            StringAssert.Contains("primaryExpansion * axisRatio", halo);
            StringAssert.Contains("echoExpansion * axisRatio", halo);
            StringAssert.Contains("trailingExpansion * axisRatio", halo);
            StringAssert.Contains("mistExpansion * axisRatio", halo);
            StringAssert.Contains(".rotationEffect(.degrees(rotation))", halo);
            StringAssert.Contains("proxy.size.width * centerX", halo);
            StringAssert.Contains("proxy.size.height * centerY", halo);
            StringAssert.Contains(".blendMode(.screen)", halo);
            StringAssert.Contains("struct ComboBezierCurveEditor: View", halo);
            StringAssert.Contains("path.addCurve(", halo);
            StringAssert.Contains("DragGesture(minimumDistance: 0)", halo);
            StringAssert.DoesNotContain("combo.accent", halo);

            StringAssert.Contains("progress: haloProgress", swift);
            StringAssert.Contains(
                "opacityProgress: haloOpacityProgress",
                swift);
            StringAssert.Contains(
                "withAnimation(.linear(duration: duration))",
                swift);
            StringAssert.Contains("projection: state.comboHaloProjection", swift);
            StringAssert.Contains("milestoneCount: haloMilestoneCount", swift);
            StringAssert.Contains("haloMilestoneCount = newCount", swift);
            StringAssert.Contains("CodexComboHaloReceiveProjection", swift);
            StringAssert.Contains(
                "state.comboHaloTuning.milestoneCrossed(",
                swift);
            StringAssert.Contains("private struct ComboHaloTuningPanel", swift);
            StringAssert.Contains("ComboBezierCurveEditor(", swift);
            StringAssert.Contains("打开 Combo 光晕工具", swift);
            int settingsStart = swift.IndexOf("private struct SettingsPanel");
            int settingsEnd = swift.IndexOf("private struct ProductPanel");
            string settings = swift.Substring(settingsStart, settingsEnd - settingsStart);
            Assert.That(
                settings.IndexOf("#if DEBUG"),
                Is.LessThan(settings.IndexOf("打开 Combo 光晕工具")),
                "The Combo curve tool must not appear in Release settings UI.");
            StringAssert.Contains("restoreRecommendedComboHaloTuning", swift);
            StringAssert.Contains("accessibilityReduceMotion", swift);
            StringAssert.Contains("iPhone: iOS", importer);
            StringAssert.Contains("enabled: 1", importer);
        }

        [Test]
        public void ComboHaloProjection_UsesModelPlaneEllipseAndTopOriginCenter()
        {
            bool resolved = ComboHaloProjectionRules.TryResolveProjectedEllipse(
                new Vector3(0.42f, 0.64f, 1f),
                new Vector3(0.52f, 0.64f, 1f),
                new Vector3(0.42f, 0.69f, 1f),
                new Vector2(1000f, 1000f),
                out ComboHaloProjection projection);

            Assert.That(resolved, Is.True);
            Assert.That(projection.CenterX, Is.EqualTo(0.42f).Within(0.0001f));
            Assert.That(projection.CenterY, Is.EqualTo(0.36f).Within(0.0001f));
            Assert.That(projection.RotationDegrees, Is.EqualTo(0f).Within(0.001f));
            Assert.That(projection.MinorAxisRatio, Is.EqualTo(0.5f).Within(0.001f));

            resolved = ComboHaloProjectionRules.TryResolveProjectedEllipse(
                new Vector3(0.5f, 0.5f, 1f),
                new Vector3(0.6f, 0.6f, 1f),
                new Vector3(0.475f, 0.525f, 1f),
                new Vector2(1000f, 1000f),
                out projection);

            Assert.That(resolved, Is.True);
            Assert.That(projection.RotationDegrees, Is.EqualTo(-45f).Within(0.001f));
            Assert.That(projection.MinorAxisRatio, Is.EqualTo(0.25f).Within(0.001f));
        }

        [Test]
        public void SpeedDashboardBands_UseDeterministicFourPercentHysteresis()
        {
            Assert.That(
                SpinnerSpeedDashboardRules.ResolveBand(0.24f, SpinnerSpeedBand.Calm),
                Is.EqualTo(SpinnerSpeedBand.Calm));
            Assert.That(
                SpinnerSpeedDashboardRules.ResolveBand(0.25f, SpinnerSpeedBand.Calm),
                Is.EqualTo(SpinnerSpeedBand.Engaged));
            Assert.That(
                SpinnerSpeedDashboardRules.ResolveBand(0.22f, SpinnerSpeedBand.Engaged),
                Is.EqualTo(SpinnerSpeedBand.Engaged));
            Assert.That(
                SpinnerSpeedDashboardRules.ResolveBand(0.20f, SpinnerSpeedBand.Engaged),
                Is.EqualTo(SpinnerSpeedBand.Calm));
            Assert.That(
                SpinnerSpeedDashboardRules.ResolveBand(0.55f, SpinnerSpeedBand.Engaged),
                Is.EqualTo(SpinnerSpeedBand.Fast));
            Assert.That(
                SpinnerSpeedDashboardRules.ResolveBand(0.52f, SpinnerSpeedBand.Fast),
                Is.EqualTo(SpinnerSpeedBand.Fast));
            Assert.That(
                SpinnerSpeedDashboardRules.ResolveBand(0.80f, SpinnerSpeedBand.Fast),
                Is.EqualTo(SpinnerSpeedBand.Peak));
            Assert.That(
                SpinnerSpeedDashboardRules.ResolveBand(0.77f, SpinnerSpeedBand.Peak),
                Is.EqualTo(SpinnerSpeedBand.Peak));
            Assert.That(
                SpinnerSpeedDashboardRules.ResolveBand(0.75f, SpinnerSpeedBand.Peak),
                Is.EqualTo(SpinnerSpeedBand.Fast));
        }

        private static Renderer AddTestRenderer(
            Transform parent,
            string objectName,
            Material material,
            int materialCount)
        {
            GameObject child = new GameObject(objectName);
            child.transform.SetParent(parent, false);
            MeshRenderer renderer = child.AddComponent<MeshRenderer>();
            renderer.sharedMaterials = Enumerable.Repeat(material, materialCount).ToArray();
            return renderer;
        }

        private static void AssertStickerArtworkCentered(
            string artworkPath,
            string stickerId)
        {
            var readable = new Texture2D(
                2,
                2,
                TextureFormat.RGBA32,
                false,
                false);
            try
            {
                Assert.That(
                    readable.LoadImage(File.ReadAllBytes(artworkPath), false),
                    Is.True,
                    stickerId);
                Color32[] pixels = readable.GetPixels32();
                int minX = readable.width;
                int minY = readable.height;
                int maxX = -1;
                int maxY = -1;
                for (int y = 0; y < readable.height; y++)
                {
                    int row = y * readable.width;
                    for (int x = 0; x < readable.width; x++)
                    {
                        if (pixels[row + x].a <= 15)
                        {
                            continue;
                        }

                        minX = Mathf.Min(minX, x);
                        minY = Mathf.Min(minY, y);
                        maxX = Mathf.Max(maxX, x);
                        maxY = Mathf.Max(maxY, y);
                    }
                }

                Assert.That(maxX, Is.GreaterThanOrEqualTo(minX), stickerId);
                Assert.That(maxY, Is.GreaterThanOrEqualTo(minY), stickerId);
                float canvasCenter = (readable.width - 1f) * 0.5f;
                Assert.That(
                    (minX + maxX) * 0.5f,
                    Is.EqualTo(canvasCenter).Within(1f),
                    $"{stickerId} artwork is not horizontally centered.");
                Assert.That(
                    (minY + maxY) * 0.5f,
                    Is.EqualTo(canvasCenter).Within(1f),
                    $"{stickerId} artwork is not vertically centered.");
                int maximumSpan = Mathf.Max(maxX - minX + 1, maxY - minY + 1);
                Assert.That(
                    maximumSpan,
                    Is.InRange(800, 850),
                    $"{stickerId} must use the canonical centered artwork scale.");
            }
            finally
            {
                Object.DestroyImmediate(readable);
            }
        }
    }
}
