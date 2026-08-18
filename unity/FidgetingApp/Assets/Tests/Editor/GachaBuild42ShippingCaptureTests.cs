using System;
using System.Linq;
using FidgetingApp.DisplayCase;
using FidgetingApp.Product.Gacha;
using FidgetingApp.Product.Gacha.Editor;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaBuild42ShippingCaptureTests
    {
        [Test]
        public void CaptureContractCoversAllEightMappedShippingPrizes()
        {
            GachaSeriesDefinition series = GachaCatalog.ResolveSeries(
                GachaCatalog.LaunchSeriesId);

            Assert.That(series, Is.Not.Null);
            Assert.That(series.Prizes.Count, Is.EqualTo(8));
            Assert.That(GachaPrizePresentationResolver.Descriptors.Count,
                Is.EqualTo(8));
            Assert.That(series.Prizes.Select(prize => prize.ContentReference),
                Is.Unique);
            foreach (GachaPrizeDefinition prize in series.Prizes)
            {
                Assert.That(GachaPrizePresentationResolver.TryResolveDescriptor(
                    prize.ContentReference,
                    out GachaPrizePresentationDescriptor descriptor),
                    Is.True,
                    prize.Id);
                Assert.That(descriptor.CapsulePreset,
                    Is.EqualTo(PremiumDisplayCaseCapsulePreset.CollectorSlabLarge));
                Assert.That(descriptor.ContentOptions.IdleRotationEnabled,
                    Is.False,
                    prize.Id + " must never self-spin in the reveal.");
            }
        }

        [Test]
        public void CaptureSamplesStrictSixPhaseMidpointsFromRuntimeTimeline()
        {
            Assert.That(GachaBuild42ShippingCapture.VisiblePhaseOrder,
                Is.EqualTo(new[]
                {
                    GachaRevealPhase.Back,
                    GachaRevealPhase.Front,
                    GachaRevealPhase.Readable,
                    GachaRevealPhase.Exploded,
                    GachaRevealPhase.PrizeOnly,
                    GachaRevealPhase.Sheen
                }));

            foreach (GachaRevealPhase phase in
                     GachaBuild42ShippingCapture.VisiblePhaseOrder)
            {
                float midpoint = GachaBuild42ShippingCapture.PhaseMidpoint(phase);
                Assert.That(GachaRevealTimeline.PhaseAt(midpoint),
                    Is.EqualTo(phase));
                Assert.That(GachaRevealTimeline.PhaseProgress(phase, midpoint),
                    Is.EqualTo(0.5f).Within(0.000001f));
            }
        }

        [Test]
        public void CaptureOutputIsPortraitVideoReadyAndExplicitlyOverrideable()
        {
            Assert.That(GachaBuild42ShippingCapture.FrameWidth,
                Is.LessThan(GachaBuild42ShippingCapture.FrameHeight));
            Assert.That(GachaBuild42ShippingCapture.FramesPerSecond,
                Is.EqualTo(30));
            string requested = GachaBuild42ShippingCapture.ResolveOutputRoot(
                new[]
                {
                    "Unity",
                    GachaBuild42ShippingCapture.OutputArgument,
                    "/tmp/gacha-build42-evidence"
                },
                new DateTime(2026, 8, 16, 0, 0, 0, DateTimeKind.Utc));
            Assert.That(requested,
                Is.EqualTo("/tmp/gacha-build42-evidence"));
        }

        [Test]
        public void VisiblePixelGateIgnoresNonRenderedBoundsButRejectsEdgeContact()
        {
            const int width = 12;
            const int height = 10;
            var background = new Color32(3, 3, 5, 255);
            var foreground = new Color32(96, 112, 140, 255);
            Color32[] pixels = Enumerable.Repeat(
                background,
                width * height).ToArray();
            for (int y = 2; y <= 7; y++)
            {
                for (int x = 3; x <= 8; x++)
                {
                    pixels[y * width + x] = foreground;
                }
            }

            GachaBuild42ShippingCapture.ViewportEvidence centered =
                GachaBuild42ShippingCapture.MeasureVisiblePixelViewport(
                    pixels,
                    width,
                    height,
                    background,
                    edgeGuardPixels: 2);

            Assert.That(centered.measurementMethod,
                Is.EqualTo("rendered-visible-pixels"));
            Assert.That(centered.measured, Is.True);
            Assert.That(centered.withinShippingCropTolerance, Is.True);
            Assert.That(centered.edgeContactPixelCount, Is.Zero);
            Assert.That(centered.xMin, Is.EqualTo(3f / width).Within(0.000001f));
            Assert.That(centered.xMax, Is.EqualTo(9f / width).Within(0.000001f));
            Assert.That(
                GachaBuild42ShippingCapture.CountVisibleEdgeContactPixels(
                    pixels,
                    width,
                    height,
                    background,
                    edgeGuardPixels: 2),
                Is.Zero);

            // This represents real shipping pixels touching the crop edge.
            // It must fail even when all other visible content remains centered.
            pixels[5 * width] = foreground;
            GachaBuild42ShippingCapture.ViewportEvidence clipped =
                GachaBuild42ShippingCapture.MeasureVisiblePixelViewport(
                    pixels,
                    width,
                    height,
                    background,
                    edgeGuardPixels: 2);

            Assert.That(clipped.measured, Is.True);
            Assert.That(clipped.withinShippingCropTolerance, Is.False);
            Assert.That(clipped.xMin, Is.Zero);
            Assert.That(clipped.edgeContactPixelCount, Is.EqualTo(1));
            Assert.That(
                GachaBuild42ShippingCapture.CountVisibleEdgeContactPixels(
                    pixels,
                    width,
                    height,
                    background,
                    edgeGuardPixels: 2),
                Is.EqualTo(1));
        }

        [Test]
        public void VisiblePixelGateFailsClosedWhenShippingRenderIsEmpty()
        {
            const int width = 8;
            const int height = 8;
            var background = new Color32(3, 3, 5, 255);
            Color32[] pixels = Enumerable.Repeat(
                background,
                width * height).ToArray();

            GachaBuild42ShippingCapture.ViewportEvidence result =
                GachaBuild42ShippingCapture.MeasureVisiblePixelViewport(
                    pixels,
                    width,
                    height,
                    background);

            Assert.That(result.measured, Is.False);
            Assert.That(result.foregroundPixelCount, Is.Zero);
            Assert.That(result.withinShippingCropTolerance, Is.False);
        }
    }
}
