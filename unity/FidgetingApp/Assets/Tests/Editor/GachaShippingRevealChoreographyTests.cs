using System.IO;
using FidgetingApp.Product.Gacha;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    /// <summary>
    /// Gacha reveal v2 timeline for the live case: pull → hold back →
    /// anticipate → flip → reveal → labels → complete → idle. Deterministic
    /// rules only; the Simulator recording is the visual gate.
    /// </summary>
    public sealed class GachaShippingRevealChoreographyTests
    {
        private const float Epsilon = 0.0001f;

        [Test]
        public void SpecCurvesAreUsedAsWritten()
        {
            // cubic-bezier(0.83, 0, 0.17, 1): slow start, fast middle.
            Assert.Less(GachaCubicBezier.EaseInOut.Evaluate(0.25f), 0.1f);
            Assert.AreEqual(0.5f, GachaCubicBezier.EaseInOut.Evaluate(0.5f), 0.02f);
            Assert.Greater(GachaCubicBezier.EaseInOut.Evaluate(0.75f), 0.9f);
            // cubic-bezier(0.16, 1, 0.3, 1): most of the travel early.
            Assert.Greater(GachaCubicBezier.EaseOut.Evaluate(0.3f), 0.75f);
            // Anticipate dips below zero before rising.
            Assert.Less(GachaCubicBezier.Anticipate.Evaluate(0.35f), 0f);
            Assert.AreEqual(1f, GachaCubicBezier.Anticipate.Evaluate(1f), Epsilon);
            // Overshoot passes 1 before settling.
            Assert.Greater(GachaCubicBezier.Overshoot.Evaluate(0.5f), 1f);
        }

        [Test]
        public void TimelineMatchesTheSpecBeats()
        {
            // T0-relative spec values minus the 0.70 s case play offset, plus
            // the Pack-release lead (rev-005 review; 0.35 → 0.24 in the
            // rev-009 gacha-reveal-timeline canvas review).
            Assert.AreEqual(0.24f, GachaShippingRevealChoreography.PullStartSeconds, Epsilon);
            Assert.AreEqual(1.02f, GachaShippingRevealChoreography.PullEndSeconds, Epsilon);
            Assert.AreEqual(1.26f, GachaShippingRevealChoreography.SettleEndSeconds, Epsilon);
            Assert.AreEqual(1.66f, GachaShippingRevealChoreography.HoldBackEndSeconds, Epsilon);
            Assert.AreEqual(1.86f, GachaShippingRevealChoreography.AnticipateEndSeconds, Epsilon);
            Assert.AreEqual(2.28f, GachaShippingRevealChoreography.FlipEndSeconds, Epsilon);
            Assert.AreEqual(3.26f, GachaShippingRevealChoreography.CompleteSeconds, Epsilon);
            // Face passes 90° near the middle of the flip.
            Assert.AreEqual(2.07f, GachaShippingRevealChoreography.RevealSeconds, 0.02f);
            // Labels land 0.80 s after the overshoot, unchanged since rev-005.
            Assert.AreEqual(
                0.80f,
                GachaShippingRevealChoreography.LabelSeconds
                - GachaShippingRevealChoreography.OvershootEndSeconds,
                Epsilon);
            Assert.GreaterOrEqual(
                GachaShippingRevealChoreography.HoldBackSeconds,
                0.4f,
                "the back must rest ≥ 400 ms before the flip");
        }

        [Test]
        public void CaseStaysBackFacingUntilTheFlipAndSettlesToTheFront()
        {
            Assert.AreEqual(180f, GachaShippingRevealChoreography.YawDegrees(0f), Epsilon);
            Assert.AreEqual(
                180f,
                GachaShippingRevealChoreography.YawDegrees(
                    GachaShippingRevealChoreography.HoldBackEndSeconds - 0.01f),
                Epsilon);
            float anticipated = GachaShippingRevealChoreography.YawDegrees(
                GachaShippingRevealChoreography.AnticipateEndSeconds - 0.001f);
            Assert.Greater(anticipated, 180f, "anticipation leans away first");
            Assert.AreEqual(
                0f,
                GachaShippingRevealChoreography.YawDegrees(
                    GachaShippingRevealChoreography.FlipEndSeconds),
                0.01f);
            float overshoot = GachaShippingRevealChoreography.YawDegrees(
                GachaShippingRevealChoreography.FlipEndSeconds
                + GachaShippingRevealChoreography.FlipOvershootSeconds * 0.5f);
            Assert.AreEqual(
                -GachaShippingRevealChoreography.FlipOvershootDegrees,
                overshoot,
                0.01f);
            Assert.AreEqual(
                0f,
                GachaShippingRevealChoreography.YawDegrees(
                    GachaShippingRevealChoreography.OvershootEndSeconds),
                Epsilon);
            // Idle under the result panel: ±3°.
            Assert.LessOrEqual(
                Mathf.Abs(GachaShippingRevealChoreography.YawDegrees(
                    GachaShippingRevealChoreography.CompleteSeconds + 1f)),
                GachaShippingRevealChoreography.IdleYawDegrees + Epsilon);
        }

        [Test]
        public void FlipAcceleratesThroughTheMiddleAndEasesOut()
        {
            float start = GachaShippingRevealChoreography.AnticipateEndSeconds;
            float duration = GachaShippingRevealChoreography.FlipSeconds;
            float early = Mathf.Abs(
                GachaShippingRevealChoreography.YawDegrees(start + duration * 0.1f)
                - GachaShippingRevealChoreography.YawDegrees(start));
            float middle = Mathf.Abs(
                GachaShippingRevealChoreography.YawDegrees(start + duration * 0.55f)
                - GachaShippingRevealChoreography.YawDegrees(start + duration * 0.45f));
            float late = Mathf.Abs(
                GachaShippingRevealChoreography.YawDegrees(start + duration)
                - GachaShippingRevealChoreography.YawDegrees(start + duration * 0.9f));
            Assert.Greater(middle, early);
            Assert.Greater(middle, late);
        }

        [Test]
        public void PackReleasesBeforeTheCaseStartsMoving()
        {
            Assert.IsFalse(GachaShippingRevealChoreography.HasCrossedPackLip(-0.01f));
            Assert.IsTrue(GachaShippingRevealChoreography.HasCrossedPackLip(0f));
            // The case holds its inside-Pack pose while the Pack starts to drop.
            Assert.AreEqual(0f, GachaShippingRevealChoreography.PullProgress(0f));
            Assert.AreEqual(
                0f,
                GachaShippingRevealChoreography.PullProgress(
                    GachaShippingRevealChoreography.PullStartSeconds));
            Assert.Greater(
                GachaShippingRevealChoreography.PullProgress(
                    GachaShippingRevealChoreography.PullStartSeconds + 0.3f),
                0f);
            Assert.AreEqual(
                1f,
                GachaShippingRevealChoreography.PullProgress(
                    GachaShippingRevealChoreography.PullEndSeconds),
                Epsilon);
            Assert.AreEqual(
                GachaShippingRevealChoreography.PullLeanDegrees,
                GachaShippingRevealChoreography.TiltDegrees(0.4f),
                Epsilon);
            Assert.AreEqual(
                0f,
                GachaShippingRevealChoreography.TiltDegrees(
                    GachaShippingRevealChoreography.SettleEndSeconds),
                Epsilon);
        }

        [Test]
        public void RevealEffectsKeyOffTheNinetyDegreeFrameAndScaleWithRarity()
        {
            float reveal = GachaShippingRevealChoreography.RevealSeconds;
            GachaRevealRarityStyle heirloom = GachaRevealRarityStyle.For(GachaRarity.Heirloom);
            GachaRevealRarityStyle rare = GachaRevealRarityStyle.For(GachaRarity.Signature);
            GachaRevealRarityStyle standard = GachaRevealRarityStyle.For(GachaRarity.Standard);

            Assert.AreEqual(0.85f, heirloom.FlashAlpha, Epsilon);
            Assert.AreEqual(240, heirloom.ParticleCount);
            Assert.AreEqual(0.4f, rare.FlashAlpha, Epsilon);
            Assert.AreEqual(96, rare.ParticleCount);
            Assert.AreEqual(0f, standard.FlashAlpha, Epsilon);
            Assert.AreEqual(0, standard.ParticleCount);
            Assert.Greater(heirloom.GlowIntensity, rare.GlowIntensity);
            Assert.Greater(rare.GlowIntensity, standard.GlowIntensity);

            Assert.AreEqual(0f, GachaShippingRevealChoreography.FlashOpacity(reveal - 0.01f, heirloom));
            Assert.AreEqual(
                heirloom.FlashAlpha,
                GachaShippingRevealChoreography.FlashOpacity(
                    reveal + GachaShippingRevealChoreography.FlashRiseSeconds,
                    heirloom),
                Epsilon);
            Assert.AreEqual(
                0f,
                GachaShippingRevealChoreography.FlashOpacity(
                    reveal + GachaShippingRevealChoreography.FlashSeconds,
                    heirloom),
                Epsilon);
            // Glow: half intensity before the flip, peak at reveal + 120 ms,
            // then settles to 0.6.
            Assert.AreEqual(
                GachaShippingRevealChoreography.GlowHoldBeforeFlipFraction,
                GachaShippingRevealChoreography.GlowFraction(
                    GachaShippingRevealChoreography.HoldBackEndSeconds),
                Epsilon);
            Assert.AreEqual(
                1f,
                GachaShippingRevealChoreography.GlowFraction(
                    reveal + GachaShippingRevealChoreography.GlowPeakSeconds),
                Epsilon);
            Assert.AreEqual(
                GachaShippingRevealChoreography.GlowHoldFraction,
                GachaShippingRevealChoreography.GlowFraction(reveal + 5f),
                Epsilon);
            // Stage: 25% until the reveal, lit 800 ms later.
            Assert.AreEqual(1f, GachaShippingRevealChoreography.StageDim(reveal));
            Assert.AreEqual(
                0f,
                GachaShippingRevealChoreography.StageDim(
                    reveal + GachaShippingRevealChoreography.StageLightUpSeconds),
                Epsilon);
            Assert.AreEqual(0.75f, GachaRevealStageFX.IdleStageDim, Epsilon);
            Assert.AreEqual(0.35f, GachaShippingRevealChoreography.StageLightUpSeconds, Epsilon,
                "the backdrop → environment cut hides behind the 260 ms flash");
            // Labels after 3.2 s; complete then.
            Assert.AreEqual(0f, GachaShippingRevealChoreography.LabelAlpha(
                GachaShippingRevealChoreography.LabelSeconds));
            Assert.AreEqual(
                1f,
                GachaShippingRevealChoreography.LabelAlpha(
                    GachaShippingRevealChoreography.LabelSeconds
                    + GachaShippingRevealChoreography.LabelFadeSeconds),
                Epsilon);
            Assert.IsTrue(GachaShippingRevealChoreography.IsComplete(
                GachaShippingRevealChoreography.CompleteSeconds));
        }

        [Test]
        public void DirectorAndCoordinatorWireTheShippingChoreography()
        {
            string director = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "Scripts/Product/Gacha/GachaShippingRevealDirector.cs"));
            string coordinator = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "Scripts/Product/FidgetAppCoordinator.cs"));
            string presentation = File.ReadAllText(Path.Combine(
                Application.dataPath,
                "_DisplayCase/Runtime/PremiumDisplayCaseShippingPresentation.cs"));

            StringAssert.Contains("PrepareShippingChoreography()", director);
            StringAssert.Contains("ApplyShippingChoreography(", director);
            StringAssert.Contains("frontRevealed?.Invoke()", director);
            StringAssert.Contains("caseCrossedPackLip?.Invoke()", director);
            StringAssert.Contains("EmitRevealBurst()", director);
            StringAssert.Contains("PrepareBladeEmissive()", director);
            StringAssert.Contains("AdoptStageFX(", director);
            StringAssert.Contains("ShrinkStartUntilInsidePack()", director);
            StringAssert.DoesNotContain("activeCase.SetTimeForPreview(0f);", director);

            StringAssert.Contains("EnterGachaStageFromNativeUi", coordinator);
            // The Pack-hue gradient backdrop stays in front of the environment
            // until the flip (user: 卡片啪转过来那一刻再切场景).
            StringAssert.Contains("gachaStageFX.TrySetBackdropImage(snapshotPath)", coordinator);
            StringAssert.Contains("gachaStageFX.SetBackdrop(tint, strength)", coordinator);
            StringAssert.Contains("stageFX.SetStageStrength(", director);
            StringAssert.Contains("LeaveGachaStageFromNativeUi", coordinator);
            StringAssert.Contains("EmitGachaTearSnapFromNativeUi", coordinator);
            // Carousel tier ladder: the snap detent is weighted by tier and
            // goes through the semantic pipeline, not a raw IosHaptics call.
            StringAssert.Contains("EmitGachaCarouselSnapFromNativeUi", coordinator);

            // Device hang 2026-09-07: the storefront must read Unity's draw
            // failure at once and pay with what the player has. Its cost
            // constants mirror GachaEconomyRules; a drift here reintroduces
            // the silent 20 s wait.
            string rules = File.ReadAllText(Path.Combine(
                Application.dataPath, "Plugins/iOS/FidgetGachaPackPresentation.swift"));
            StringAssert.Contains(
                $"singleDrawCoinCost = {GachaEconomyRules.SingleDrawCoinCost}", rules);
            StringAssert.Contains(
                $"singleDrawTicketCost = {GachaEconomyRules.SingleDrawTicketCost}", rules);
            string storefront = File.ReadAllText(Path.Combine(
                Application.dataPath, "Plugins/iOS/FidgetGachaShippingStorefront.swift"));
            StringAssert.Contains(".onChange(of: model.lastFailureReason)", storefront);
            StringAssert.Contains("useCoins: drawPaymentMethod == .coins", storefront);
            StringAssert.Contains(
                "FidgetHapticRouter.Emit(FidgetSemanticEvent.DetentCaptured, signal)",
                coordinator);
            StringAssert.Contains("HandleGachaShippingFrontRevealed", coordinator);
            StringAssert.Contains(
                "FidgetHapticRouter.Emit(FidgetSemanticEvent.BadgeUnlocked",
                coordinator);
            StringAssert.Contains("\"front-revealed\"", coordinator);
            StringAssert.Contains("IsShippingChoreography", coordinator);
            // The library toy at the origin showed through the clear case as
            // a second, edge-on spinner (rev-005 review); it is hidden for
            // the whole gacha stage and restored with the camera.
            StringAssert.Contains("HideLibraryProductForGacha();", coordinator);
            StringAssert.Contains("RestoreLibraryProductAfterGacha();", coordinator);
            StringAssert.Contains("HideLibraryProductForGacha();", coordinator);
            StringAssert.Contains("RestoreLibraryProductAfterGacha();", coordinator);

            StringAssert.Contains("public void ApplyDirectedPose(", presentation);
            StringAssert.Contains("ApplyRimGlow(pose.RimColor, pose.RimGlow)", presentation);
            StringAssert.Contains("SetLabelAlpha(pose.LabelAlpha)", presentation);
        }
    }
}
