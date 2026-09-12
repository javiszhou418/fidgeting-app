using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FidgetingApp.DisplayCase;
using FidgetingApp.DisplayCase.Editor;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class PremiumDisplayCaseGate12Tests
    {
        private const string TransactionPrefix =
            "fidgeting.gacha.tests.premium-display-case-gate12.";

        [TearDown]
        public void TearDown()
        {
            new GachaInventoryRuntime(TransactionPrefix).DeleteAllForTests();
            PlayerPrefs.Save();
        }

        [Test]
        public void ProfileOrdersEntryTwoSpinsSheenAndStaticHold()
        {
            PremiumDisplayCaseRevealProfile profile = LoadProfile();
            Assert.That(
                profile.EntryRotationOverlapSeconds,
                Is.LessThanOrEqualTo(profile.EntryDurationSeconds));
            Assert.That(
                profile.EntryRotationOverlapSeconds,
                Is.LessThanOrEqualTo(profile.RotationDurationSeconds));

            Assert.That(
                profile.Evaluate(0f).Phase,
                Is.EqualTo(PremiumDisplayCaseShippingPhase.Entry));
            Assert.That(
                profile.Evaluate(profile.RotationStartSeconds + 0.01f).Phase,
                Is.EqualTo(
                    PremiumDisplayCaseShippingPhase.EntryFirstSpinOverlap));
            Assert.That(
                profile.Evaluate(profile.EntryDurationSeconds + 0.01f).Phase,
                Is.EqualTo(PremiumDisplayCaseShippingPhase.FirstSpin));
            Assert.That(
                profile.Evaluate(profile.FirstSpinEndSeconds + 0.01f).Phase,
                Is.EqualTo(PremiumDisplayCaseShippingPhase.SecondSpin));
            Assert.That(
                profile.Evaluate(profile.RotationEndSeconds + 0.01f).Phase,
                Is.EqualTo(PremiumDisplayCaseShippingPhase.Sheen));
            Assert.That(
                profile.Evaluate(profile.SheenEndSeconds + 0.01f).Phase,
                Is.EqualTo(PremiumDisplayCaseShippingPhase.Hold));
            Assert.That(
                profile.FinalSample().Phase,
                Is.EqualTo(PremiumDisplayCaseShippingPhase.Complete));
        }

        [Test]
        public void ProfileHasNoXRollPitchScaleOrBackgroundMotion()
        {
            PremiumDisplayCaseRevealProfile profile = LoadProfile();
            for (int index = 0; index <= 120; index++)
            {
                PremiumDisplayCaseShippingSample sample = profile.Evaluate(
                    profile.TotalDurationSeconds * index / 120f);
                Assert.That(sample.PositionOffset.x, Is.Zero.Within(0.0000001f));
                Assert.That(sample.LocalYawDegrees, Is.InRange(0f, 720f));
            }
            Assert.That(
                profile.FinalSample().LocalYawDegrees,
                Is.EqualTo(720f).Within(0.0001f));
        }

        [Test]
        public void CandidateIsShorterWithFastFirstAndSlowerSecondSpin()
        {
            PremiumDisplayCaseRevealProfile profile = LoadProfile();
            Assert.That(profile.HandoffDurationSeconds,
                Is.EqualTo(0.14f).Within(0.0001f));
            Assert.That(profile.EntryDurationSeconds,
                Is.EqualTo(0.56f).Within(0.0001f));
            Assert.That(profile.FirstSpinDurationSeconds,
                Is.EqualTo(0.50f).Within(0.0001f));
            Assert.That(profile.SecondSpinDurationSeconds,
                Is.EqualTo(1.10f).Within(0.0001f));
            Assert.That(profile.EntryRotationOverlapSeconds,
                Is.EqualTo(0.18f).Within(0.0001f));
            Assert.That(profile.ArrivalRimDurationSeconds,
                Is.EqualTo(0.28f).Within(0.0001f));
            Assert.That(profile.TotalDurationSeconds,
                Is.EqualTo(2.94f).Within(0.0001f));
            Assert.That(
                profile.TotalDurationSeconds,
                Is.LessThan(
                    PremiumDisplayCaseRevealProfile
                        .PreviousApprovedTotalDurationSeconds));
            Assert.That(
                profile.HandoffDurationSeconds,
                Is.LessThan(
                    PremiumDisplayCaseRevealProfile
                        .PreviousApprovedHandoffDurationSeconds));
            Assert.That(
                profile.AverageFirstSpinDegreesPerSecond,
                Is.GreaterThan(
                    profile.AverageSecondSpinDegreesPerSecond * 2f));
            Assert.That(profile.FirstSpinDegrees, Is.EqualTo(360f));
            Assert.That(profile.SecondSpinDegrees, Is.EqualTo(360f));
            Assert.That(profile.LightRevealIntensity,
                Is.EqualTo(1f).Within(0.0001f));
            Assert.That(profile.FirstRotationRimIntensity,
                Is.EqualTo(0.92f).Within(0.0001f));
            Assert.That(profile.SecondRotationRimIntensity,
                Is.EqualTo(0.74f).Within(0.0001f));
            Assert.That(profile.SheenIntensity,
                Is.EqualTo(1f).Within(0.0001f));
            Assert.That(profile.UsesCc0LightRevealCurve, Is.True);
        }

        [Test]
        public void SpinBoundaryPreservesPositiveAngularVelocity()
        {
            PremiumDisplayCaseRevealProfile profile = LoadProfile();
            const float sampleStep = 0.001f;
            float boundary = profile.FirstSpinEndSeconds;
            float yawBefore = profile.Evaluate(boundary - sampleStep)
                .LocalYawDegrees;
            float yawAtBoundary = profile.Evaluate(boundary)
                .LocalYawDegrees;
            float yawAfter = profile.Evaluate(boundary + sampleStep)
                .LocalYawDegrees;
            float velocityBefore =
                (yawAtBoundary - yawBefore) / sampleStep;
            float velocityAfter =
                (yawAfter - yawAtBoundary) / sampleStep;

            Assert.That(velocityBefore, Is.GreaterThan(200f));
            Assert.That(velocityAfter, Is.GreaterThan(200f));
            Assert.That(
                Mathf.Abs(velocityBefore - velocityAfter),
                Is.LessThan(5f));
        }

        [Test]
        public void Cc0ExtractionContainsOnlyCurvesMasksAndProvenance()
        {
            string module = Path.Combine(
                Application.dataPath,
                "_DisplayCase/Runtime/MakeItShineCc0Effects");
            string contract = File.ReadAllText(
                Path.Combine(module, "SOURCE_CONTRACT.json"));
            StringAssert.Contains(
                "88842be0063b5b0b75e82ed6572752a37a13c82b",
                contract);
            StringAssert.Contains(
                "be661fe81b095f7f1ad08fb2a1c003b15f8690ee08d43f9f705dc849924fb2c6",
                contract);
            StringAssert.Contains(
                "6a7718d6ae1eba360c03a1ea16b207ada5ae80f1a4dc2df0d004453bf94e2067",
                contract);
            StringAssert.Contains(
                "a4eb3922e72a3dadb436902d2c4a57c3fbd6768e4b137104abeed6167e1f4f7d",
                contract);
            StringAssert.Contains("\"externalModelsImported\": false", contract);
            StringAssert.Contains("\"externalPrefabsImported\": false", contract);
            StringAssert.Contains("\"particlesEnabled\": false", contract);
            StringAssert.Contains("\"vfxGraphDependency\": false", contract);
            StringAssert.Contains("BoosterFractured_B.fbx", contract);
            StringAssert.Contains("Spawn Cards Timeline.playable", contract);

            string[] forbiddenExtensions =
            {
                ".fbx",
                ".prefab",
                ".anim",
                ".playable",
                ".vfx",
                ".shadergraph",
                ".mat",
                ".png",
                ".jpg"
            };
            string[] files = Directory.GetFiles(
                module,
                "*",
                SearchOption.AllDirectories);
            Assert.That(
                files.Any(file => forbiddenExtensions.Contains(
                    Path.GetExtension(file).ToLowerInvariant())),
                Is.False);
        }

        [Test]
        public void RevealAndSheenAreFiniteMeshLocalCues()
        {
            PremiumDisplayCaseRevealProfile profile = LoadProfile();
            Assert.That(
                profile.Evaluate(profile.ArrivalRimDurationSeconds * 0.5f)
                    .LightRevealStrength,
                Is.GreaterThan(0f));
            Assert.That(
                profile.Evaluate(profile.EntryDurationSeconds + 0.01f)
                    .LightRevealStrength,
                Is.Zero.Within(0.0001f));
            Assert.That(
                profile.Evaluate(
                    profile.SecondSpinEndSeconds
                    + profile.SheenDurationSeconds * 0.5f)
                    .SheenStrength,
                Is.GreaterThan(0f));
            Assert.That(
                profile.FinalSample().SheenStrength,
                Is.Zero.Within(0.0001f));

            float lightPeak = 0f;
            float firstRotationRimPeak = 0f;
            float secondRotationRimPeak = 0f;
            float sheenPeak = 0f;
            for (int index = 0; index <= 720; index++)
            {
                PremiumDisplayCaseShippingSample sample = profile.Evaluate(
                    profile.TotalDurationSeconds * index / 720f);
                lightPeak = Mathf.Max(lightPeak, sample.LightRevealStrength);
                if (sample.RotationRimPass == 1)
                {
                    firstRotationRimPeak = Mathf.Max(
                        firstRotationRimPeak,
                        sample.RotationRimStrength);
                }
                else if (sample.RotationRimPass == 2)
                {
                    secondRotationRimPeak = Mathf.Max(
                        secondRotationRimPeak,
                        sample.RotationRimStrength);
                }
                sheenPeak = Mathf.Max(sheenPeak, sample.SheenStrength);
            }
            Assert.That(lightPeak, Is.GreaterThan(0.85f));
            Assert.That(firstRotationRimPeak, Is.GreaterThan(0.85f));
            Assert.That(secondRotationRimPeak, Is.GreaterThan(0.68f));
            Assert.That(sheenPeak, Is.GreaterThan(0.92f));
            Assert.That(
                profile.Evaluate(profile.FirstSpinEndSeconds)
                    .RotationRimStrength,
                Is.Zero.Within(0.0001f));
            Assert.That(
                profile.Evaluate(profile.FirstSpinEndSeconds)
                    .RotationRimPass,
                Is.EqualTo(2));
            Assert.That(
                profile.FinalSample().RotationRimStrength,
                Is.Zero.Within(0.0001f));
        }

        [Test]
        public void ShippingPrefabUsesApprovedGeometryAndOneMeshClippedSheen()
        {
            PremiumDisplayCaseShippingPresentation prefab =
                AssetDatabase.LoadAssetAtPath<
                    PremiumDisplayCaseShippingPresentation>(
                    PremiumDisplayCaseGate12Builder.ShippingPrefabPath);
            Assert.That(prefab, Is.Not.Null);
            Assert.That(
                prefab.GetComponentsInChildren<MeshFilter>(true).Length,
                Is.EqualTo(5));
            Assert.That(
                prefab.GetComponentsInChildren<MeshFilter>(true)
                    .Sum(filter => filter.sharedMesh.triangles.Length / 3),
                Is.EqualTo(100016));
            Assert.That(
                prefab.GetComponentsInChildren<Transform>(true)
                    .Count(item => item.name == "PresentationRoot"),
                Is.EqualTo(1));
            Assert.That(prefab.name, Is.EqualTo("PresentationRoot"));
            Assert.That(
                prefab.ContentSlot.Find("ContentFit"),
                Is.Not.Null);
            Assert.That(
                prefab.ContentSlot.GetComponentsInChildren<Renderer>(true)
                    .Where(renderer => renderer.transform.IsChildOf(
                        prefab.ContentSlot))
                    .Count(),
                Is.Zero);

            Assert.That(prefab.EffectsAreWired, Is.True);
            Assert.That(prefab.EffectRenderers.Count, Is.EqualTo(3));
            Assert.That(prefab.RevealProfile.UsesCc0LightRevealCurve, Is.True);
            foreach (Renderer effectRenderer in prefab.EffectRenderers)
            {
                Assert.That(effectRenderer, Is.Not.Null);
                Assert.That(
                    effectRenderer.sharedMaterial.shader.name,
                    Is.EqualTo(
                        "FidgetingApp/Gate12R004MeshClippedFrosted"));
                Assert.That(
                    effectRenderer.sharedMaterial.HasProperty(
                        "_LightRevealStrength"),
                    Is.True);
                Assert.That(
                    effectRenderer.sharedMaterial.HasProperty(
                        "_RotationRimProgress"),
                    Is.True);
                Assert.That(
                    effectRenderer.sharedMaterial.HasProperty(
                        "_RotationRimStrength"),
                    Is.True);
                Assert.That(
                    effectRenderer.sharedMaterial.HasProperty(
                        "_SheenStrength"),
                    Is.True);
            }

            string shader = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_DisplayCase/Shaders/PremiumDisplayCaseGate12R004Frosted.shader"));
            StringAssert.Contains("input.positionOS", shader);
            StringAssert.Contains("MakeItShineCc0Masks.hlsl", shader);
            StringAssert.Contains("_LightRevealProgress", shader);
            StringAssert.Contains("_LightRevealStrength", shader);
            StringAssert.Contains("_RotationRimProgress", shader);
            StringAssert.Contains("_RotationRimStrength", shader);
            StringAssert.Contains("_SheenStrength", shader);
            StringAssert.Contains("_SheenFalloff", shader);
            StringAssert.Contains("_SheenObjectCenter", shader);
            StringAssert.Contains("_SheenObjectInvSize", shader);
            StringAssert.DoesNotContain("LightType.Point", shader);
            StringAssert.DoesNotContain("SAMPLE_TEXTURE2D", shader);
        }

        [Test]
        public void RuntimeWritesVisibleEffectPeaksToEveryMaterial()
        {
            PremiumDisplayCaseShippingPresentation prefab =
                AssetDatabase.LoadAssetAtPath<
                    PremiumDisplayCaseShippingPresentation>(
                    PremiumDisplayCaseGate12Builder.ShippingPrefabPath);
            PremiumDisplayCaseShippingPresentation instance =
                UnityEngine.Object.Instantiate(prefab);
            var block = new MaterialPropertyBlock();
            try
            {
                float lightPeakTime = FindPeakTime(
                    instance.RevealProfile,
                    sample => sample.LightRevealStrength);
                instance.SetTimeForPreview(lightPeakTime);
                foreach (Renderer renderer in instance.EffectRenderers)
                {
                    renderer.GetPropertyBlock(block);
                    Assert.That(
                        block.GetFloat("_LightRevealStrength"),
                        Is.GreaterThan(0.85f));
                }

                float firstRimPeakTime = FindPeakTime(
                    instance.RevealProfile,
                    sample => sample.RotationRimPass == 1
                        ? sample.RotationRimStrength
                        : 0f);
                instance.SetTimeForPreview(firstRimPeakTime);
                foreach (Renderer renderer in instance.EffectRenderers)
                {
                    renderer.GetPropertyBlock(block);
                    Assert.That(
                        block.GetFloat("_RotationRimStrength"),
                        Is.GreaterThan(0.85f));
                }

                float secondRimPeakTime = FindPeakTime(
                    instance.RevealProfile,
                    sample => sample.RotationRimPass == 2
                        ? sample.RotationRimStrength
                        : 0f);
                instance.SetTimeForPreview(secondRimPeakTime);
                foreach (Renderer renderer in instance.EffectRenderers)
                {
                    renderer.GetPropertyBlock(block);
                    Assert.That(
                        block.GetFloat("_RotationRimStrength"),
                        Is.GreaterThan(0.68f));
                }

                float sheenPeakTime = FindPeakTime(
                    instance.RevealProfile,
                    sample => sample.SheenStrength);
                instance.SetTimeForPreview(sheenPeakTime);
                foreach (Renderer renderer in instance.EffectRenderers)
                {
                    renderer.GetPropertyBlock(block);
                    Assert.That(
                        block.GetFloat("_SheenStrength"),
                        Is.GreaterThan(0.92f));
                }
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(instance.gameObject);
            }
        }

        [Test]
        public void GpuLightCuesAreVisibleAndStayInsideCaseFragments()
        {
            PremiumDisplayCaseShippingPresentation prefab =
                AssetDatabase.LoadAssetAtPath<
                    PremiumDisplayCaseShippingPresentation>(
                    PremiumDisplayCaseGate12Builder.ShippingPrefabPath);
            PremiumDisplayCaseShippingPresentation instance =
                UnityEngine.Object.Instantiate(prefab);
            var cameraObject = new GameObject("Gate12EffectPixelTestCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.clear;
            camera.nearClipPlane = 0.02f;
            camera.farClipPlane = 3f;
            camera.fieldOfView = 27f;
            camera.aspect = 0.82f;
            camera.transform.position = new Vector3(0f, 0.008f, -0.78f);
            camera.transform.LookAt(new Vector3(0f, 0.008f, 0f));
            try
            {
                var cues = new[]
                {
                    (
                        "arrival",
                        FindPeakTime(
                            instance.RevealProfile,
                            sample => sample.LightRevealStrength)),
                    (
                        "first-rotation-rim",
                        FindPeakTime(
                            instance.RevealProfile,
                            sample => sample.RotationRimPass == 1
                                ? sample.RotationRimStrength
                                : 0f)),
                    (
                        "second-rotation-rim",
                        FindPeakTime(
                            instance.RevealProfile,
                            sample => sample.RotationRimPass == 2
                                ? sample.RotationRimStrength
                                : 0f)),
                    (
                        "final-sheen",
                        FindPeakTime(
                            instance.RevealProfile,
                            sample => sample.SheenStrength))
                };
                foreach ((string cue, float time) in cues)
                {
                    EffectPixelMetrics metrics = MeasureEffectPixels(
                        instance,
                        camera,
                        time);
                    TestContext.WriteLine(
                        $"{cue}: changed={metrics.ChangedPixels}, "
                        + $"fraction={metrics.ChangedFraction:F4}, "
                        + $"meanLuma={metrics.MeanLumaDelta:F4}, "
                        + $"p95Luma={metrics.P95LumaDelta:F4}, "
                        + $"maxLuma={metrics.MaximumLumaDelta:F4}, "
                        + $"external={metrics.ExternalPixels}");
                    Assert.That(
                        metrics.ChangedPixels,
                        Is.GreaterThan(160),
                        $"{cue} must change real GPU pixels.");
                    Assert.That(
                        metrics.ChangedFraction,
                        Is.GreaterThan(0.04f),
                        $"{cue} must cover a readable part of the case.");
                    Assert.That(
                        metrics.MeanLumaDelta,
                        Is.GreaterThan(0.012f),
                        $"{cue} must change average case luminance.");
                    Assert.That(
                        metrics.P95LumaDelta,
                        Is.GreaterThan(0.05f),
                        $"{cue} must have a readable high-contrast area.");
                    Assert.That(
                        metrics.MaximumLumaDelta,
                        Is.GreaterThan(0.10f),
                        $"{cue} must reach a readable GPU peak.");
                    Assert.That(
                        metrics.ExternalPixels,
                        Is.Zero,
                        $"{cue} must stay inside the base case fragments.");
                }
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(cameraObject);
                UnityEngine.Object.DestroyImmediate(instance.gameObject);
            }
        }

        [Test]
        public void PresentationKeepsOneCaseAndToyStaticThroughCompletion()
        {
            PremiumDisplayCaseShippingPresentation prefab =
                AssetDatabase.LoadAssetAtPath<
                    PremiumDisplayCaseShippingPresentation>(
                    PremiumDisplayCaseGate12Builder.ShippingPrefabPath);
            PremiumDisplayCaseShippingPresentation instance =
                UnityEngine.Object.Instantiate(prefab);
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            try
            {
                PremiumDisplayCaseShippingPresentation identity = instance;
                instance.SetLabel(AuthoritativeLabel());
                instance.AttachContent(
                    prize.transform,
                    PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
                instance.Play(false);
                int guard = 0;
                while (instance.IsPlaying && guard++ < 500)
                {
                    instance.Tick(1f / 60f);
                }
                Assert.That(instance, Is.SameAs(identity));
                Assert.That(instance.Phase,
                    Is.EqualTo(PremiumDisplayCaseShippingPhase.Complete));
                Assert.That(instance.LightRevealActivationCount, Is.EqualTo(1));
                Assert.That(instance.RotationRimPassCount, Is.EqualTo(2));
                Assert.That(instance.SheenActivationCount, Is.EqualTo(1));
                Assert.That(instance.HasFixedScale, Is.True);
                Assert.That(instance.ToyAngularVelocityIsZero, Is.True);
                Assert.That(prize.transform.IsChildOf(instance.ContentSlot), Is.True);
                Assert.That(instance.HasAuthoritativeLabel, Is.True);
                // Only the attached prize may be active under ContentFit; any
                // authored placeholder would read as a second object.
                Assert.That(instance.ContentFitHoldsOnlyAttachedContent, Is.True);
            }
            finally
            {
                if (instance != null)
                {
                    instance.DetachContent();
                    UnityEngine.Object.DestroyImmediate(instance.gameObject);
                }
                if (prize != null)
                {
                    UnityEngine.Object.DestroyImmediate(prize);
                }
            }
        }

        [Test]
        public void ReduceMotionKeepsCausalityAndCompletesAtStaticPose()
        {
            PremiumDisplayCaseShippingPresentation prefab =
                AssetDatabase.LoadAssetAtPath<
                    PremiumDisplayCaseShippingPresentation>(
                    PremiumDisplayCaseGate12Builder.ShippingPrefabPath);
            PremiumDisplayCaseShippingPresentation instance =
                UnityEngine.Object.Instantiate(prefab);
            GameObject prize = ThreeBladeDisplayPrizeFactory.Instantiate();
            try
            {
                instance.SetLabel(AuthoritativeLabel());
                instance.AttachContent(
                    prize.transform,
                    PremiumDisplayCaseShippingFactory.ThreeBladeContentEuler);
                instance.Play(true);

                Assert.That(instance.Phase,
                    Is.EqualTo(PremiumDisplayCaseShippingPhase.Complete));
                Assert.That(instance.LightRevealActivationCount, Is.Zero);
                Assert.That(instance.RotationRimPassCount, Is.Zero);
                Assert.That(instance.SheenActivationCount, Is.Zero);
                Assert.That(instance.ToyAngularVelocityIsZero, Is.True);
                Assert.That(instance.HasFixedScale, Is.True);

                instance.Tick(0f);
                Assert.That(instance.IsPlaying, Is.False);
            }
            finally
            {
                if (instance != null)
                {
                    instance.DetachContent();
                    UnityEngine.Object.DestroyImmediate(instance.gameObject);
                }
                if (prize != null)
                {
                    UnityEngine.Object.DestroyImmediate(prize);
                }
            }
        }

        [Test]
        public void DurableReceiptRejectsStaleRequestsAndAcknowledgesOnce()
        {
            GachaInventoryRuntime inventory = NewPreviewInventory();
            GachaTransactionResult first = inventory.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "gate12-request-a");
            Assert.That(first.Success, Is.True);
            Assert.That(first.Receipt.Rows[0].Outcome.PrizeId,
                Is.EqualTo("canyon-heir-metal-three-blade"));
            Assert.That(first.Receipt.Rows[0].CollectibleId, Is.Not.Empty);
            Assert.That(first.Receipt.Rows[0].FirstObtainedAtUtc, Is.Not.Empty);

            GachaTransactionResult duplicate = inventory.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "gate12-request-a");
            Assert.That(duplicate.Success, Is.True);
            Assert.That(
                duplicate.Receipt.Rows[0].CollectibleId,
                Is.EqualTo(first.Receipt.Rows[0].CollectibleId));
            Assert.That(
                inventory.PrepareDraw(
                    GachaCatalog.LaunchSeriesId,
                    1,
                    GachaPaymentMethod.Ticket,
                    "gate12-request-b").FailureReason,
                Is.EqualTo("transaction-in-flight"));
            Assert.That(
                inventory.MarkRevealReady("stale-request").FailureReason,
                Is.EqualTo("stale-request"));
            Assert.That(
                inventory.AcknowledgePending("gate12-request-a").FailureReason,
                Is.EqualTo("reveal-not-ready"));

            inventory.MarkRevealReady("gate12-request-a");
            GachaTransactionResult accepted =
                inventory.AcknowledgePending("gate12-request-a");
            int draws = inventory.TotalDraws(GachaCatalog.LaunchSeriesId);
            Assert.That(accepted.Success, Is.True);
            Assert.That(
                inventory.AcknowledgePending("gate12-request-a").Success,
                Is.True);
            Assert.That(
                inventory.TotalDraws(GachaCatalog.LaunchSeriesId),
                Is.EqualTo(draws));
        }

        [Test]
        public void PendingReceiptRestoresAfterInterruptionWithoutReroll()
        {
            GachaInventoryRuntime inventory = NewPreviewInventory();
            GachaTransactionResult prepared = inventory.PrepareDraw(
                GachaCatalog.LaunchSeriesId,
                1,
                GachaPaymentMethod.Ticket,
                "gate12-interrupted");
            string collectibleId = prepared.Receipt.Rows[0].CollectibleId;

            var restored = new GachaInventoryRuntime(TransactionPrefix);
            GachaTransactionResult query =
                restored.QueryTransaction("gate12-interrupted");
            Assert.That(query.Success, Is.True);
            Assert.That(
                query.Receipt.Rows[0].CollectibleId,
                Is.EqualTo(collectibleId));
            Assert.That(
                query.Transaction.Phase,
                Is.EqualTo(GachaTransactionPhase.Prepared));
            Assert.That(restored.OwnedCount, Is.Zero);
        }

        [Test]
        public void LabelAuthorityPrintsEnglishPlateCopyWithoutLevel()
        {
            GachaPrizeDefinition prize = GachaCatalog.ResolvePrize(
                "canyon-heir-metal-three-blade").Value;
            PremiumDisplayCaseLabelData label = GachaShippingLabelAuthority.Create(
                prize,
                new GachaDrawReceiptRow(
                    new GachaDrawOutcome(
                        prize.Id, GachaRarity.Heirloom, false, true, false),
                    true,
                    0,
                    "2026-09-09T10:58:00.0000000Z",
                    "FDT-R053"),
                17);
            Assert.That(label.ProductName, Is.EqualTo("GEEONE TRI-SPINNER"));
            Assert.That(label.EditionFinish, Is.EqualTo("SATIN STEEL · DRAGON SCALE"));
            Assert.That(label.RarityLevel, Is.EqualTo("HEIRLOOM"));
            Assert.That(label.RarityLevel, Does.Not.Contain("LEVEL"));
            Assert.That(label.AcquiredDate, Is.EqualTo("2026-09-09"));
            Assert.That(label.IsAuthoritative, Is.True);
            Assert.That(
                PremiumDisplayCaseShippingPresentation.ShowsCollectibleIdOnPlate,
                Is.False,
                "the FDT id stays in the receipt, off the plate (user 09-09 18:58)");
        }

        [Test]
        public void Gate12PrefabLabelIsOxaniumOnHoloFoilWithTiltDriver()
        {
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                PremiumDisplayCaseGate12LabelRestyle.PrefabPath);
            Assert.That(prefab, Is.Not.Null);

            Renderer plate = prefab.GetComponentsInChildren<Renderer>(true)
                .Single(item => item.name == "PhysicalLabel");
            Assert.That(
                plate.sharedMaterial.shader.name,
                Is.EqualTo(PremiumDisplayCaseGate12LabelRestyle.FoilShaderName));
            Assert.That(plate.sharedMaterial.HasProperty(
                PremiumDisplayCaseLabelFoil.SheenPhaseId), Is.True);

            var driver = prefab.GetComponent<PremiumDisplayCaseLabelFoil>();
            Assert.That(driver, Is.Not.Null);
            Assert.That(driver.Plate, Is.SameAs(plate));

            TextMesh[] rows = prefab.GetComponentsInChildren<TextMesh>(true)
                .Where(item => item.name.StartsWith("Authoritative"))
                .ToArray();
            Assert.That(rows.Length, Is.EqualTo(5));
            foreach (TextMesh row in rows)
            {
                Assert.That(row.font, Is.Not.Null, row.name);
                Assert.That(row.font.name, Does.Contain("Oxanium"), row.name);
                Assert.That(
                    row.GetComponent<MeshRenderer>().sharedMaterial,
                    Is.SameAs(row.font.material),
                    row.name);
                Assert.That(row.richText, Is.False, row.name);
                Assert.That(row.transform.localPosition.x,
                    Is.EqualTo(PremiumDisplayCaseGate12LabelRestyle.LeftMarginX)
                        .Within(0.000001f),
                    row.name);
                Assert.That(row.color.grayscale, Is.LessThan(0.35f),
                    row.name + " prints dark ink on the bright foil");
            }
            TextMesh name = rows.Single(item => item.name == "AuthoritativeProductName");
            TextMesh edition = rows.Single(item => item.name == "AuthoritativeEditionFinish");
            Assert.That(name.fontStyle, Is.EqualTo(FontStyle.Bold));
            Assert.That(name.characterSize, Is.GreaterThan(edition.characterSize * 1.8f));
            Assert.That(edition.transform.localPosition.z,
                Is.LessThan(name.transform.localPosition.z),
                "edition kicker sits above the name");
        }

        [Test]
        public void LabelFoilFollowsTiltAndDriftsWhenStill()
        {
            var host = new GameObject("foil-host");
            var stillHost = new GameObject("foil-still-host");
            try
            {
                var driver = host.AddComponent<PremiumDisplayCaseLabelFoil>();
                for (int i = 0; i < 120; i++)
                {
                    driver.Step(1f / 60f, true, new Vector3(0.6f, 0f, -0.8f));
                }
                float tilted = driver.Phase;
                Assert.That(tilted, Is.GreaterThan(
                    0.6f * PremiumDisplayCaseLabelFoil.TiltPhaseGain * 0.9f));

                var still = stillHost.AddComponent<PremiumDisplayCaseLabelFoil>();
                still.Step(1f, false, Vector3.zero);
                Assert.That(
                    still.Phase,
                    Is.EqualTo(PremiumDisplayCaseLabelFoil.IdleDriftCyclesPerSecond)
                        .Within(0.0001f),
                    "no motion: only the slow idle drift moves the band");
                Assert.That(
                    PremiumDisplayCaseLabelFoil.IdleDriftCyclesPerSecond,
                    Is.LessThan(0.1f),
                    "idle drift must read as a passive surface, not self-motion");
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(host);
                UnityEngine.Object.DestroyImmediate(stillHost);
            }
        }

        [Test]
        public void LabelRejectsPlaceholderOrMismatchedReceiptData()
        {
            PremiumDisplayCaseLabelData valid = AuthoritativeLabel();
            Assert.That(valid.IsAuthoritative, Is.True);
            Assert.That(
                new PremiumDisplayCaseLabelData(
                    "PLACEHOLDER",
                    valid.EditionFinish,
                    valid.AcquiredDate,
                    valid.RarityLevel,
                    valid.CollectibleId).IsAuthoritative,
                Is.False);

            GachaPrizeDefinition prize = GachaCatalog.ResolvePrize(
                "canyon-heir-metal-three-blade").Value;
            Assert.Throws<ArgumentException>(() =>
                GachaShippingLabelAuthority.Create(
                    prize,
                    new GachaDrawReceiptRow(
                        new GachaDrawOutcome(
                            "wrong-prize",
                            GachaRarity.Heirloom,
                            false,
                            true,
                            false),
                        true,
                        0,
                        DateTime.UtcNow.ToString("O"),
                        "FDT-REAL"),
                    1));
        }

        [Test]
        public void CoordinatorRequiresTwoStableEndOfFrameChecks()
        {
            string coordinator = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "Scripts/Product/FidgetAppCoordinator.cs"));
            StringAssert.Contains(
                "ConfirmGachaRevealReadyAfterTwoFrames",
                coordinator);
            Assert.That(
                Count(coordinator, "yield return new WaitForEndOfFrame();"),
                Is.GreaterThanOrEqualTo(2));
            StringAssert.Contains(
                "activeGachaRevealDirector.ActiveCase != caseReference",
                coordinator);
            StringAssert.Contains(
                "activeGachaPrize != prizeReference",
                coordinator);
            StringAssert.Contains(
                "displayCaseCamera != cameraReference",
                coordinator);
            StringAssert.Contains(
                "PremiumDisplayCaseGachaLightingInstaller.Install",
                coordinator);
            StringAssert.DoesNotContain("LightType.Point", coordinator);

            string storefront = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "Plugins/iOS/FidgetGachaShippingStorefront.swift"));
            StringAssert.Contains(
                "private var showsPack",
                storefront);
            StringAssert.Contains(
                "gate.allowsLiveCaseAperture",
                storefront);
            // R037: departure is driven by `case-crossing-pack-lip`; the
            // backdrop fades into the live stage instead of a black cut.
            StringAssert.DoesNotContain(
                "model.revealHandoffDurationSeconds",
                storefront);
            StringAssert.Contains("stageBackdropOpacity", storefront);
            StringAssert.DoesNotContain(
                "Color.black\n                    .ignoresSafeArea()",
                storefront);
            StringAssert.Contains("showsCompletedOverlay", storefront);
            StringAssert.Contains(
                "GachaPackHandoffRules.resultPanelDelayNanoseconds",
                storefront);
            StringAssert.Contains(
                "GachaPackHandoffRules.selectedPackGeometryID",
                storefront);
            StringAssert.DoesNotContain(
                "GachaSingleDrawGateState.packToCaseTransitionSeconds",
                storefront);
            StringAssert.Contains(
                "activeGachaRevealDirector.HandoffDurationSeconds",
                coordinator);
            StringAssert.Contains(
                "StartGachaRevealFromNativeUi",
                coordinator);
            StringAssert.Contains("activeGachaRevealStarted", coordinator);
            StringAssert.Contains("model.startReveal(requestID:", storefront);
        }

        [Test]
        public void NativePackTearUsesRealLayersMaskAndReadyGatedCoverage()
        {
            string storefront = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "Plugins/iOS/FidgetGachaShippingStorefront.swift"));
            string components = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "Plugins/iOS/FidgetProductUIComponents.swift"));
            string rules = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "Plugins/iOS/FidgetGachaPackPresentation.swift"));

            StringAssert.Contains("ProductPackTearRevealLayer(", storefront);
            StringAssert.Contains("gestureActive: phase == .tearPack", storefront);
            StringAssert.Contains("handoffActive: phase == .handoff", storefront);
            // Gate12 preview plays one confident slice at the shipping
            // tear duration; the old hesitate-and-retry rehearsal is gone.
            StringAssert.DoesNotContain("tearProgress = 0.48", storefront);
            StringAssert.DoesNotContain("tearProgress = 0.68", storefront);
            StringAssert.Contains("tearProgress = 0", storefront);
            StringAssert.Contains(
                "tearProgress = GachaPackOpeningRules.tearCommitProgress",
                storefront);
            StringAssert.Contains(
                ".nativeHybridTearDurationSeconds)) {",
                storefront);
            // The Pack must stay mounted while it slides away.
            StringAssert.Contains("packDeparted ? 1.0 : 0.0", storefront);
            StringAssert.Contains("private func retreatPack(", storefront);
            StringAssert.Contains(
                "packReleasePulseStrength = 1",
                storefront);
            StringAssert.Contains(
                "translationPoints: value.translation.width",
                storefront);
            StringAssert.DoesNotContain(
                "translationPoints: -value.translation.height",
                storefront);
            StringAssert.DoesNotContain(
                ".frame(width: 238, height: 82)",
                storefront);

            StringAssert.Contains("struct ProductTearablePackArtwork", components);
            StringAssert.Contains("struct ProductPackTearRevealLayer",
                components);
            // R035: the sealed Pack is body + seal fin (flap raster). The fin
            // is the lid; the body raster is never cut. The attached-fin mask
            // is an explicit complement (even-odd left it invisible).
            StringAssert.Contains(
                "struct ProductPackSlitBodyMask",
                components);
            StringAssert.DoesNotContain(
                "struct ProductPackOuterFoilMask",
                components);
            StringAssert.Contains(
                "FillStyle(eoFill: false)",
                components);
            StringAssert.Contains(
                "ProductPackSlitCavity",
                components);
            // No lip line or outline above the body edge.
            StringAssert.DoesNotContain("ProductPackMouthLip", components);
            StringAssert.DoesNotContain("ProductPackTornEdge", components);
            StringAssert.DoesNotContain(
                "ProductPackApertureOccluder",
                components);
            StringAssert.DoesNotContain("openingOpacity", components);
            StringAssert.Contains(
                "struct ProductPackSealedArtwork",
                components);
            StringAssert.Contains(
                "ProductRasterAssetImage(name: flapAssetName)",
                components);
            StringAssert.Contains(
                "ProductPackLid(\n                assetName: flapAssetName",
                components);
            StringAssert.DoesNotContain(
                "ProductPackLid(\n                assetName: bodyAssetName",
                components);
            // Carousel and tear stage start from the same sealed pixels.
            StringAssert.Contains("ProductPackSealedArtwork(", storefront);
            StringAssert.Contains(
                "authoredSeamYFraction: Double = 92.0 / 512.0",
                rules);
            StringAssert.Contains(
                "authoredPackTopYFraction: Double = 45.0 / 512.0",
                rules);
            StringAssert.Contains("GachaPackLidRules.pose(", components);
            StringAssert.Contains(
                ".rotationEffect(.degrees(pose.rotationDegrees), anchor: hinge)",
                components);
            StringAssert.DoesNotContain("attachedFlapMask", components);
            StringAssert.DoesNotContain("movingFlapMask", components);
            StringAssert.DoesNotContain(".mask(packMask)", components);
            StringAssert.DoesNotContain(".mask(openingMask)", components);
            // The lid pose comes from GachaPackLidRules; the old per-flap
            // offset helpers must not come back as a second motion source.
            StringAssert.DoesNotContain("flapHorizontalOffsetPoints", components);
            StringAssert.DoesNotContain("flapVerticalOffsetPoints", components);
            StringAssert.Contains("openingHeightPoints", components);
            StringAssert.Contains("releasePulseStrength", components);

            StringAssert.Contains("tearCommitProgress: Double = 0.62", rules);
            StringAssert.Contains(
                "flapHorizontalTravelPoints: Double = 16",
                rules);
            StringAssert.Contains(
                "authoredCanvasWidth: Double = 384",
                rules);
            StringAssert.Contains(
                "authoredCanvasHeight: Double = 512",
                rules);
            StringAssert.Contains(
                "releasePulseDurationSeconds: Double = 0.60",
                rules);
            StringAssert.Contains(
                "openingMaskAreaSquarePoints",
                rules);
            StringAssert.Contains(
                "canRevealLiveCase",
                rules);
            StringAssert.Contains("GachaPackHandoffRules.showsPack", storefront);
            StringAssert.Contains("packVisible || realCaseReady", rules);
        }

        private static PremiumDisplayCaseRevealProfile LoadProfile()
        {
            PremiumDisplayCaseRevealProfile profile =
                AssetDatabase.LoadAssetAtPath<
                    PremiumDisplayCaseRevealProfile>(
                    PremiumDisplayCaseGate12Builder.ProfilePath);
            Assert.That(profile, Is.Not.Null,
                "Run the Gate 12 builder before tests.");
            return profile;
        }

        private static GachaInventoryRuntime NewPreviewInventory()
        {
            var inventory = new GachaInventoryRuntime(
                TransactionPrefix,
                new GachaSplitMix64(0x120011UL));
            inventory.DeleteAllForTests();
            inventory = new GachaInventoryRuntime(
                TransactionPrefix,
                new GachaSplitMix64(0x120011UL));
            inventory.PrimeGate12SimulatorPreview();
            return inventory;
        }

        private static PremiumDisplayCaseLabelData AuthoritativeLabel()
        {
            return new PremiumDisplayCaseLabelData(
                "三叶金属陀螺",
                "峡谷矿脉 · 抛光钢",
                "2026-08-27",
                "HEIRLOOM · LEVEL 1",
                "FDT-82C77C1831AF");
        }

        private static float FindPeakTime(
            PremiumDisplayCaseRevealProfile profile,
            Func<PremiumDisplayCaseShippingSample, float> value)
        {
            float peakTime = 0f;
            float peakValue = float.MinValue;
            for (int index = 0; index <= 720; index++)
            {
                float time = profile.TotalDurationSeconds * index / 720f;
                float candidate = value(profile.Evaluate(time));
                if (candidate > peakValue)
                {
                    peakValue = candidate;
                    peakTime = time;
                }
            }
            return peakTime;
        }

        private static EffectPixelMetrics MeasureEffectPixels(
            PremiumDisplayCaseShippingPresentation presentation,
            Camera camera,
            float time)
        {
            presentation.SetTimeForPreview(time);
            Color32[] fragmentMask = CaptureEffectFragmentMask(
                presentation,
                camera);
            Color32[] effect = CapturePixels(camera);
            var block = new MaterialPropertyBlock();
            foreach (Renderer renderer in presentation.EffectRenderers)
            {
                renderer.GetPropertyBlock(block);
                block.SetFloat("_LightRevealStrength", 0f);
                block.SetFloat("_RotationRimStrength", 0f);
                block.SetFloat("_SheenStrength", 0f);
                renderer.SetPropertyBlock(block);
            }
            Color32[] baseline = CapturePixels(camera);
            presentation.SetTimeForPreview(time);

            int changed = 0;
            int external = 0;
            int fragmentPixels = 0;
            float maximumLumaDelta = 0f;
            float lumaDeltaSum = 0f;
            var fragmentLumaDeltas = new List<float>();
            for (int index = 0; index < effect.Length; index++)
            {
                Color32 before = baseline[index];
                Color32 after = effect[index];
                float beforeLuma =
                    (before.r * 0.2126f
                        + before.g * 0.7152f
                        + before.b * 0.0722f) / 255f;
                float afterLuma =
                    (after.r * 0.2126f
                        + after.g * 0.7152f
                        + after.b * 0.0722f) / 255f;
                float lumaDelta = Mathf.Abs(afterLuma - beforeLuma);
                if (fragmentMask[index].a > 0)
                {
                    fragmentPixels += 1;
                    lumaDeltaSum += lumaDelta;
                    fragmentLumaDeltas.Add(lumaDelta);
                }
                int maximumChannelDelta = Mathf.Max(
                    Mathf.Abs(after.r - before.r),
                    Mathf.Max(
                        Mathf.Abs(after.g - before.g),
                        Mathf.Abs(after.b - before.b)));
                if (maximumChannelDelta <= 3
                    && Mathf.Abs(after.a - before.a) <= 3)
                {
                    continue;
                }
                changed += 1;
                if (fragmentMask[index].a == 0)
                {
                    external += 1;
                }
                maximumLumaDelta = Mathf.Max(
                    maximumLumaDelta,
                    lumaDelta);
            }
            fragmentLumaDeltas.Sort();
            float p95LumaDelta = fragmentLumaDeltas.Count == 0
                ? 0f
                : fragmentLumaDeltas[Mathf.Clamp(
                    Mathf.CeilToInt(fragmentLumaDeltas.Count * 0.95f) - 1,
                    0,
                    fragmentLumaDeltas.Count - 1)];
            return new EffectPixelMetrics(
                changed,
                external,
                fragmentPixels,
                fragmentPixels > 0
                    ? lumaDeltaSum / fragmentPixels
                    : 0f,
                p95LumaDelta,
                maximumLumaDelta);
        }

        private static Color32[] CaptureEffectFragmentMask(
            PremiumDisplayCaseShippingPresentation presentation,
            Camera camera)
        {
            Renderer[] allRenderers =
                presentation.GetComponentsInChildren<Renderer>(true);
            var effectRenderers = new HashSet<Renderer>(
                presentation.EffectRenderers);
            bool[] enabledStates = allRenderers
                .Select(renderer => renderer.enabled)
                .ToArray();
            Material[][] materialStates = allRenderers
                .Select(renderer => renderer.sharedMaterials)
                .ToArray();
            Shader shader = Shader.Find(
                "FidgetingApp/Gate12R004MeshClippedFrosted");
            var maskMaterial = new Material(shader);
            maskMaterial.SetColor("_BaseColor", Color.white);
            maskMaterial.SetColor("_RimColor", Color.white);
            maskMaterial.SetFloat("_Opacity", 1f);
            maskMaterial.SetFloat("_RimStrength", 0f);
            maskMaterial.SetFloat("_SpecularStrength", 0f);
            maskMaterial.SetFloat("_LightRevealStrength", 0f);
            maskMaterial.SetFloat("_RotationRimProgress", 0f);
            maskMaterial.SetFloat("_RotationRimStrength", 0f);
            maskMaterial.SetFloat("_SheenStrength", 0f);
            try
            {
                for (int index = 0; index < allRenderers.Length; index++)
                {
                    Renderer renderer = allRenderers[index];
                    bool isEffectRenderer = effectRenderers.Contains(renderer);
                    renderer.enabled = isEffectRenderer;
                    if (isEffectRenderer)
                    {
                        renderer.sharedMaterials = renderer.sharedMaterials
                            .Select(_ => maskMaterial)
                            .ToArray();
                        renderer.SetPropertyBlock(null);
                    }
                }
                return CapturePixels(camera);
            }
            finally
            {
                for (int index = 0; index < allRenderers.Length; index++)
                {
                    allRenderers[index].sharedMaterials = materialStates[index];
                    allRenderers[index].enabled = enabledStates[index];
                }
                UnityEngine.Object.DestroyImmediate(maskMaterial);
                presentation.SetTimeForPreview(presentation.ElapsedSeconds);
            }
        }

        private static Color32[] CapturePixels(Camera camera)
        {
            const int width = 256;
            const int height = 320;
            var target = new RenderTexture(
                width,
                height,
                24,
                RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.Linear);
            var texture = new Texture2D(
                width,
                height,
                TextureFormat.RGBA32,
                false,
                true);
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            try
            {
                target.Create();
                camera.targetTexture = target;
                RenderTexture.active = target;
                camera.Render();
                texture.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                texture.Apply(false, false);
                return texture.GetPixels32();
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                UnityEngine.Object.DestroyImmediate(texture);
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
            }
        }

        private readonly struct EffectPixelMetrics
        {
            public EffectPixelMetrics(
                int changedPixels,
                int externalPixels,
                int fragmentPixels,
                float meanLumaDelta,
                float p95LumaDelta,
                float maximumLumaDelta)
            {
                ChangedPixels = changedPixels;
                ExternalPixels = externalPixels;
                FragmentPixels = fragmentPixels;
                MeanLumaDelta = meanLumaDelta;
                P95LumaDelta = p95LumaDelta;
                MaximumLumaDelta = maximumLumaDelta;
            }

            public int ChangedPixels { get; }
            public int ExternalPixels { get; }
            public int FragmentPixels { get; }
            public float ChangedFraction => FragmentPixels > 0
                ? (float)ChangedPixels / FragmentPixels
                : 0f;
            public float MeanLumaDelta { get; }
            public float P95LumaDelta { get; }
            public float MaximumLumaDelta { get; }
        }

        private static int Count(string source, string value)
        {
            int count = 0;
            int index = 0;
            while ((index = source.IndexOf(
                       value,
                       index,
                       StringComparison.Ordinal)) >= 0)
            {
                count += 1;
                index += value.Length;
            }
            return count;
        }
    }
}
