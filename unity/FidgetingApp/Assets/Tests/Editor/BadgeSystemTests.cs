using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using FidgetingApp.Product;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class BadgeSystemTests
    {
        private const string ArtworkRoot = "Assets/Plugins/iOS/BadgeArtwork";

        [Test]
        public void CatalogDefinesThirtyFourPermanentAndSixSpecialBadges()
        {
            Assert.That(BadgeCatalogV2.ToyDefinitions.Count, Is.EqualTo(21));
            Assert.That(BadgeCatalogV2.CollectorDefinitions.Count, Is.EqualTo(13));
            Assert.That(BadgeCatalogV2.SpecialDefinitions.Count, Is.EqualTo(6));

            BadgeDefinition[] all = BadgeCatalogV2.ToyDefinitions
                .Concat(BadgeCatalogV2.CollectorDefinitions)
                .Concat(BadgeCatalogV2.SpecialDefinitions)
                .ToArray();
            Assert.That(all.Length, Is.EqualTo(40));
            Assert.That(all.Select(item => item.Id).Distinct().Count(), Is.EqualTo(40));
            Assert.That(all.Select(item => item.AssetName).Distinct().Count(), Is.EqualTo(40));
            Assert.That(
                BadgeCatalogV2.ToyDefinitions.Count(
                    item => item.Visibility == BadgeVisibility.Hidden),
                Is.EqualTo(3));
            Assert.That(
                BadgeCatalogV2.SpecialDefinitions.Count(
                    item => item.Scope == BadgeScope.Challenge),
                Is.EqualTo(5));
            Assert.That(
                BadgeCatalogV2.SpecialDefinitions.Count(
                    item => item.Scope == BadgeScope.Legacy),
                Is.EqualTo(1));
        }

        [Test]
        public void CatalogUsesExactThresholdsGradesAndRewards()
        {
            AssertThresholds(
                BadgeCategory.Power,
                new[] { 1d, 2d, 3.5d, 4.5d });
            AssertThresholds(
                BadgeCategory.Pulse,
                new[] { 100d, 1000d, 10000d, 100000d });
            AssertThresholds(
                BadgeCategory.Combo,
                new[] { 5d, 10d, 20d, 50d });
            AssertThresholds(
                BadgeCategory.Focus,
                new[] { 300d, 1800d, 7200d, 36000d });

            BadgeGrade[] expectedGrades =
            {
                BadgeGrade.Ignition,
                BadgeGrade.Overdrive,
                BadgeGrade.Apex,
                BadgeGrade.Singularity
            };
            Assert.That(
                BadgeCatalogV2.ToyDefinitions
                    .Where(item => item.Category == BadgeCategory.Combo)
                    .Select(item => item.Grade),
                Is.EqualTo(expectedGrades));
            Assert.That(expectedGrades.Select(BadgeRewardRules.ExperienceForGrade),
                Is.EqualTo(new[] { 5, 10, 20, 40 }));
            Assert.That(expectedGrades.Select(BadgeRewardRules.ShardsForGrade),
                Is.EqualTo(new[] { 1, 2, 3, 5 }));
        }

        [Test]
        public void RotorSliderAndFanReceiveMechanismSpecificReachablePowerPaths()
        {
            string rotor = BadgeCatalogV2.ToyCatalogJson(Snapshot(
                ProductCatalog.MetalThreeBladeModelId,
                peakRimSpeedKmh: 3.5d,
                peakNormalizedForce: 0d));
            StringAssert.Contains("\"mechanism\":\"Rotor\"", rotor);
            StringAssert.Contains("\"displayToken\":\"3.5\"", rotor);
            StringAssert.Contains("\"displayUnit\":\"KM/H\"", rotor);

            foreach (string modelId in new[]
                     {
                         ProductCatalog.MagneticSlideTileModelId,
                         ProductCatalog.MagneticFanCardModelId
                     })
            {
                string payload = BadgeCatalogV2.ToyCatalogJson(Snapshot(
                    modelId,
                    peakRimSpeedKmh: 0d,
                    peakNormalizedForce: 0.75d));
                StringAssert.Contains("\"targetValue\":0.75", payload);
                StringAssert.Contains("\"displayToken\":\"0.75\"", payload);
                StringAssert.Contains("\"displayUnit\":\"\"", payload);
                StringAssert.Contains(
                    "\"mechanism\":\"" +
                    ProductCatalog.MechanismForModel(modelId) + "\"",
                    payload);
            }
        }

        [Test]
        public void JsonV2ExposesHiddenProgressAndTwoLineRuntimeTypography()
        {
            string payload = BadgeCatalogV2.ToyCatalogJson(Snapshot(
                ProductCatalog.MetalThreeBladeModelId,
                peakRimSpeedKmh: 1.4d,
                peakNormalizedForce: 0d));
            StringAssert.Contains("\"version\":2", payload);
            StringAssert.Contains("\"id\":\"toy_technique_speed\"", payload);
            StringAssert.Contains("\"visibility\":\"Hidden\"", payload);
            StringAssert.Contains("\"state\":\"Hidden\"", payload);
            StringAssert.Contains("\"assetName\":\"badge-b10-toy-technique-speed\"", payload);
            StringAssert.Contains("\"displayToken\":\"1.0\"", payload);
            StringAssert.Contains("\"shortName\":\"POWER\"", payload);
            StringAssert.DoesNotContain("LifetimeOfflineExperience", payload);
        }

        [Test]
        public void FeaturedToyBadge_PrefersGradeThenHighestResolvedNumber()
        {
            SpinnerProgressionSnapshot empty = Snapshot(
                ProductCatalog.MetalThreeBladeModelId,
                peakRimSpeedKmh: 0d,
                peakNormalizedForce: 0d);
            Assert.That(
                BadgeCatalogV2.TryResolveFeaturedToyBadge(empty, out _),
                Is.False);

            SpinnerProgressionSnapshot higherGrade = Snapshot(
                ProductCatalog.MetalThreeBladeModelId,
                peakRimSpeedKmh: 3.5d,
                peakNormalizedForce: 0d,
                lifetimeGestureCount: 1000L,
                perfectTechniqueCount: 1);
            Assert.That(
                BadgeCatalogV2.TryResolveFeaturedToyBadge(
                    higherGrade,
                    out BadgeDefinition perfect),
                Is.True);
            Assert.That(perfect.Id, Is.EqualTo("toy_technique_perfect"));

            SpinnerProgressionSnapshot sameGrade = Snapshot(
                ProductCatalog.MetalThreeBladeModelId,
                peakRimSpeedKmh: 4.5d,
                peakNormalizedForce: 0d,
                lifetimeGestureCount: 100000L,
                activeInteractionSeconds: 36000d,
                highestCombo: 50,
                perfectTechniqueCount: 1);
            Assert.That(
                BadgeCatalogV2.TryResolveFeaturedToyBadge(
                    sameGrade,
                    out BadgeDefinition highestNumber),
                Is.True);
            Assert.That(highestNumber.Id, Is.EqualTo("toy_pulse_100k"));
            Assert.That(
                BadgeCatalogV2.ToyDisplayToken(sameGrade, highestNumber),
                Is.EqualTo("100K"));
        }

        [Test]
        public void UtcCycleIndexCannotReturnBeforeEpoch()
        {
            Assert.That(
                BadgeCatalogV2.UtcWeekIndex(
                    new DateTime(1969, 12, 31, 23, 59, 59, DateTimeKind.Utc)),
                Is.EqualTo(0));
            Assert.That(
                BadgeCatalogV2.UtcWeekIndex(
                    new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)),
                Is.EqualTo(0));
            Assert.That(
                BadgeCatalogV2.UtcWeekIndex(
                    new DateTime(1970, 1, 8, 0, 0, 0, DateTimeKind.Utc)),
                Is.EqualTo(1));
        }

        [Test]
        public void RewardLedgerClaimsEachBadgeOnceAndPublishesClaimState()
        {
            string prefix = "badge-ledger-test-" + Guid.NewGuid() + ".";
            string modelId = "badge-reward-model-" + Guid.NewGuid();
            var ledger = new BadgeRewardLedger(prefix);
            BadgeDefinition definition = BadgeCatalogV2.ToyDefinitions
                .Single(item => item.Id == "toy_power_ignition");
            string claimKey = BadgeRewardLedger.ToyClaimKey(modelId, definition.Id);
            int experience = 0;

            Assert.That(
                ledger.TryClaim(claimKey, definition, DateTime.UtcNow,
                    reward => experience += reward),
                Is.True);
            Assert.That(
                ledger.TryClaim(claimKey, definition, DateTime.UtcNow,
                    reward => experience += reward),
                Is.False);
            Assert.That(experience, Is.EqualTo(definition.ExperienceReward));
            Assert.That(ledger.ShardBalance, Is.EqualTo(definition.ShardReward));
            ledger.SaveIfDirty(true);

            var restored = new BadgeRewardLedger(prefix);
            Assert.That(restored.IsClaimed(claimKey), Is.True);
            Assert.That(restored.ShardBalance, Is.EqualTo(definition.ShardReward));
            string payload = BadgeCatalogV2.ToyCatalogJson(
                Snapshot(modelId, peakRimSpeedKmh: 1d, peakNormalizedForce: 0d),
                restored);
            StringAssert.Contains("\"rewardClaimed\":true", payload);
            StringAssert.Contains("\"shardBalance\":1", payload);
            StringAssert.Contains("\"unlockedAtUtc\":\"", payload);
        }

        [Test]
        public void SpinnerRuntimeAwardsBadgeXpAndShardsOnlyOnce()
        {
            string modelId = "badge-runtime-" + Guid.NewGuid();
            var ledger = new BadgeRewardLedger(
                "badge-runtime-ledger-" + Guid.NewGuid() + ".");
            var runtime = new SpinnerProgressionRuntime(modelId, ledger);
            double before = runtime.Snapshot.TotalExperience;

            runtime.RecordGesture(
                normalizedForce: 0.8f,
                angularSpeedRadians: 7f);
            double afterFirst = runtime.Snapshot.TotalExperience;
            int shardsAfterFirst = ledger.ShardBalance;
            runtime.RecordGesture(
                normalizedForce: 0.8f,
                angularSpeedRadians: 7f,
                countGesture: false);

            Assert.That(afterFirst - before, Is.GreaterThan(5d));
            Assert.That(shardsAfterFirst, Is.EqualTo(1));
            Assert.That(ledger.ShardBalance, Is.EqualTo(shardsAfterFirst));
            Assert.That(runtime.ConsumePendingBadgeUnlockCount(), Is.EqualTo(1));
            Assert.That(runtime.ConsumePendingBadgeUnlockCount(), Is.Zero);
        }

        [Test]
        public void CollectorRuntimeUsesTheSharedBadgeLedgerAndCannotPayTwice()
        {
            string prefix = "badge-collector-runtime-" + Guid.NewGuid() + ".";
            var ledger = new BadgeRewardLedger(prefix + "ledger.");
            var runtime = new CollectorProgressionRuntime(
                "seed-model",
                prefix,
                ledger);
            runtime.ConsumePendingBadgeUnlockCount();

            runtime.BackfillModel("collector-model-a", 1, true);
            double afterFirstModel = runtime.Snapshot.TotalExperience;
            runtime.BackfillModel("collector-model-b", 1, true);
            double afterSecondModel = runtime.Snapshot.TotalExperience;

            Assert.That(
                afterSecondModel - afterFirstModel,
                Is.EqualTo(
                    CollectorProgressionRules.FirstModelExperience
                    + BadgeRewardRules.ExperienceForGrade(BadgeGrade.Ignition))
                    .Within(0.001d));
            Assert.That(ledger.ShardBalance, Is.EqualTo(1));
            Assert.That(runtime.ConsumePendingBadgeUnlockCount(), Is.EqualTo(1));
            StringAssert.Contains(
                "\"id\":\"collector_explore_2\"",
                runtime.Snapshot.AchievementCatalogPayload);
            StringAssert.Contains(
                "\"rewardClaimed\":true",
                runtime.Snapshot.AchievementCatalogPayload);
            StringAssert.Contains(
                "\"shardBalance\":1",
                runtime.Snapshot.AchievementCatalogPayload);

            runtime.BackfillModel("collector-model-b", 1, true);
            Assert.That(runtime.Snapshot.TotalExperience, Is.EqualTo(afterSecondModel));
            Assert.That(ledger.ShardBalance, Is.EqualTo(1));
            Assert.That(runtime.ConsumePendingBadgeUnlockCount(), Is.Zero);
            runtime.SaveIfDirty(true);

            var restoredLedger = new BadgeRewardLedger(prefix + "ledger.");
            var restoredRuntime = new CollectorProgressionRuntime(
                "seed-model",
                prefix,
                restoredLedger);
            Assert.That(restoredLedger.ShardBalance, Is.EqualTo(1));
            Assert.That(restoredRuntime.ConsumePendingBadgeUnlockCount(), Is.Zero);
        }

        [Test]
        public void ShippingArtworkIsCompleteSquareTransparentSrgbAndTextFree()
        {
            var definitions = BadgeCatalogV2.ToyDefinitions
                .Concat(BadgeCatalogV2.CollectorDefinitions)
                .Concat(BadgeCatalogV2.SpecialDefinitions)
                .ToArray();

            foreach (BadgeDefinition definition in definitions)
            {
                string pngPath = Path.Combine(
                    ArtworkRoot,
                    definition.AssetName + ".png");
                Assert.That(File.Exists(pngPath), Is.True, pngPath);

                byte[] png = File.ReadAllBytes(pngPath);
                Assert.That(ReadPngInt32(png, 16), Is.EqualTo(1024), pngPath);
                Assert.That(ReadPngInt32(png, 20), Is.EqualTo(1024), pngPath);
                Assert.That(
                    png[25],
                    Is.EqualTo((byte)4).Or.EqualTo((byte)6),
                    pngPath);
                Assert.That(
                    HasSrgbColorSpaceTag(png),
                    Is.True,
                    $"{pngPath} must declare sRGB via an 'sRGB' chunk or an " +
                    "embedded 'iCCP' sRGB profile.");

                var texture = new UnityEngine.Texture2D(
                    2,
                    2,
                    UnityEngine.TextureFormat.RGBA32,
                    false,
                    false);
                try
                {
                    Assert.That(
                        UnityEngine.ImageConversion.LoadImage(texture, png, false),
                        Is.True,
                        pngPath);
                    UnityEngine.Color32[] pixels = texture.GetPixels32();
                    int minX = texture.width;
                    int minY = texture.height;
                    int maxX = -1;
                    int maxY = -1;
                    for (int y = 0; y < texture.height; y++)
                    {
                        for (int x = 0; x < texture.width; x++)
                        {
                            if (pixels[y * texture.width + x].a < 16)
                            {
                                continue;
                            }

                            minX = Math.Min(minX, x);
                            minY = Math.Min(minY, y);
                            maxX = Math.Max(maxX, x);
                            maxY = Math.Max(maxY, y);
                        }
                    }

                    Assert.That(maxX, Is.GreaterThanOrEqualTo(0), pngPath);
                    int visibleWidth = maxX - minX + 1;
                    int visibleHeight = maxY - minY + 1;
                    // The 2026-08-21 Challenge+Legacy master (b10) normalizes
                    // to a ~76-77% visible-fraction safe area (measured 780-791
                    // px across all 40 approved assets), wider than the prior
                    // b8/b9.2 generation's 74% (754-762 px) target.
                    Assert.That(
                        Math.Max(visibleWidth, visibleHeight),
                        Is.InRange(770, 795),
                        $"{pngPath} must aspect-fit its longest side into the shared b10 safe area.");
                    Assert.That(
                        (minX + maxX + 1) * 0.5,
                        Is.EqualTo(512d).Within(3d),
                        $"{pngPath} must be horizontally centered by visible bounds.");
                    Assert.That(
                        (minY + maxY + 1) * 0.5,
                        Is.EqualTo(512d).Within(3d),
                        $"{pngPath} must be vertically centered by visible bounds.");
                }
                finally
                {
                    UnityEngine.Object.DestroyImmediate(texture);
                }
            }
        }

        private static void AssertThresholds(
            BadgeCategory category,
            IReadOnlyCollection<double> expected)
        {
            Assert.That(
                BadgeCatalogV2.ToyDefinitions
                    .Where(item => item.Category == category)
                    .Select(item => item.Threshold),
                Is.EqualTo(expected));
        }

        private static SpinnerProgressionSnapshot Snapshot(
            string modelId,
            double peakRimSpeedKmh,
            double peakNormalizedForce,
            long lifetimeGestureCount = 0L,
            double activeInteractionSeconds = 0d,
            int highestCombo = 0,
            int perfectTechniqueCount = 0)
        {
            return new SpinnerProgressionSnapshot(
                modelId,
                1,
                0d,
                0d,
                SpinnerProgressionRules.ExperienceForLevel(2),
                0f,
                SpinnerProgressionRules.StageForLevel(1),
                SpinnerProgressionRules.NextUnlockForLevel(1),
                false,
                peakRimSpeedKmh,
                lifetimeGestureCount,
                0,
                activeInteractionSeconds,
                0d,
                peakNormalizedForce,
                highestCombo,
                perfectTechniqueCount: perfectTechniqueCount);
        }

        private static int ReadPngInt32(byte[] bytes, int offset)
        {
            return (bytes[offset] << 24)
                   | (bytes[offset + 1] << 16)
                   | (bytes[offset + 2] << 8)
                   | bytes[offset + 3];
        }

        /// A PNG may declare sRGB either with a dedicated 'sRGB' chunk or by
        /// embedding an actual sRGB ICC profile in an 'iCCP' chunk (what
        /// Pillow/ImageCms write); both are spec-compliant, so this walks the
        /// chunk table instead of grepping the whole file for ASCII "sRGB".
        private static bool HasSrgbColorSpaceTag(byte[] png)
        {
            int offset = 8;
            while (offset + 8 <= png.Length)
            {
                int length = ReadPngInt32(png, offset);
                string type = Encoding.ASCII.GetString(png, offset + 4, 4);
                int dataStart = offset + 8;
                if (dataStart + length > png.Length)
                {
                    break;
                }

                if (type == "sRGB")
                {
                    return true;
                }

                if (type == "iCCP")
                {
                    int nameEnd = Array.IndexOf(
                        png, (byte)0, dataStart, length);
                    if (nameEnd >= 0)
                    {
                        int compressedStart = nameEnd + 2;
                        int compressedLength = dataStart + length - compressedStart;
                        if (compressedLength > 2)
                        {
                            byte[] profile = InflateZlib(
                                png, compressedStart, compressedLength);
                            // ICC "mluc" description tags store text as
                            // UTF-16BE (e.g. lcms writes "sRGB built-in"),
                            // so an ASCII scan alone would miss it.
                            if (profile != null
                                && (Encoding.ASCII.GetString(profile)
                                        .Contains("sRGB")
                                    || Encoding.BigEndianUnicode
                                        .GetString(profile)
                                        .Contains("sRGB")))
                            {
                                return true;
                            }
                        }
                    }
                }

                offset = dataStart + length + 4;
            }
            return false;
        }

        private static byte[] InflateZlib(byte[] bytes, int start, int length)
        {
            try
            {
                // Skip the 2-byte zlib header; DeflateStream expects raw
                // deflate data, not the zlib wrapper.
                using var compressed = new MemoryStream(
                    bytes, start + 2, length - 2);
                using var inflate = new System.IO.Compression.DeflateStream(
                    compressed, System.IO.Compression.CompressionMode.Decompress);
                using var result = new MemoryStream();
                inflate.CopyTo(result);
                return result.ToArray();
            }
            catch (Exception)
            {
                return null;
            }
        }
    }
}
