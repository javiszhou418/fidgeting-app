using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaStorefrontIntegrationTests
    {
        [Test]
        public void ShippingStorefrontKeepsNavigationTicketEconomyAndRevealWiring()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string legacy = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string overlay = ReadAsset("Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = ReadAsset("Plugins/iOS/FidgetProductUIComponents.swift");

            StringAssert.Contains("public struct GachaStoreView", storefront);
            StringAssert.Contains("@Environment(\\.dismiss) private var dismiss", storefront);
            StringAssert.DoesNotContain(
                "Button(\"返回主页\")",
                storefront,
                "The storefront sheet dismisses via the native drag indicator, not a hand-drawn row.");
            StringAssert.Contains(".presentationDragIndicator(.visible)", storefront);
            StringAssert.Contains(".presentationBackground(.regularMaterial)", storefront);
            StringAssert.Contains("model.draw(\n            requestID: transactionID", storefront);
            StringAssert.Contains("@State private var drawRequestInFlight = false", storefront);
            StringAssert.Contains("singleDrawGate.commitPackSelection", storefront);
            StringAssert.Contains("drawRequestInFlight = true", storefront);
            StringAssert.Contains(".interactiveDismissDisabled(", storefront);
            StringAssert.Contains(".onDisappear", storefront);
            StringAssert.Contains("pendingReceipt = rows", legacy);
            StringAssert.DoesNotContain("count: 10", storefront);
            StringAssert.DoesNotContain("GachaCoinShopView", storefront);
            StringAssert.DoesNotContain("可购买商品", storefront);
            StringAssert.Contains(".scaledToFill()", storefront);
            StringAssert.Contains(".clipped()", storefront);
            StringAssert.Contains(
                "GachaBundleArtwork(name: \"product-banner-magnetic-fan-card\")",
                storefront);
            StringAssert.DoesNotContain(
                "product-banner-metal-three-blade",
                storefront);
            StringAssert.Contains(
                ".aspectRatio(1179.0 / 654.0, contentMode: .fit)",
                storefront);
            StringAssert.Contains("GachaSingleDrawSequenceOverlay", storefront);
            StringAssert.Contains("gacha-pack-carousel", storefront);
            StringAssert.Contains("presentationOnly=true", storefront);
            StringAssert.Contains("GachaPackVisual", storefront);
            StringAssert.Contains("gacha-pack-entry", storefront);
            StringAssert.Contains("gacha-pack-tear-target", storefront);
            StringAssert.Contains("gacha-pack-open", storefront);
            StringAssert.Contains("DragGesture(minimumDistance: 6", storefront);
            StringAssert.Contains("GachaPackOpeningRules.shouldCommit", storefront);
            StringAssert.Contains("commitPackOpen()", storefront);
            StringAssert.Contains(
                "GachaShippingRevealContinuation.preparePremiumDisplayCase",
                storefront);
            StringAssert.Contains("enum GachaShippingRevealContinuation", legacy);
            StringAssert.DoesNotContain(
                "enum GachaShippingRevealContinuation",
                components,
                "Business continuation wiring must not live in the visual component library.");
            StringAssert.Contains("release-rebound", storefront);
            StringAssert.Contains("rebound-complete", storefront);
            StringAssert.Contains("release-commit", storefront);
            StringAssert.Contains("stage: .packSelection", storefront);
            StringAssert.DoesNotContain("stage: .magneticHolder", storefront);
            StringAssert.Contains("gacha-pack-case-transition", storefront);
            StringAssert.Contains("gacha-pack-state", storefront);
            int advanceStart = storefront.IndexOf(
                "private func advanceSingleDrawIfReady",
                System.StringComparison.Ordinal);
            int abortStart = storefront.IndexOf(
                "private func abortSingleDraw",
                System.StringComparison.Ordinal);
            Assert.That(advanceStart, Is.GreaterThanOrEqualTo(0));
            Assert.That(abortStart, Is.GreaterThan(advanceStart));
            StringAssert.DoesNotContain(
                "acknowledgeReceipt",
                storefront.Substring(advanceStart, abortStart - advanceStart));

            StringAssert.Contains("struct LegacyGachaStoreView", legacy);
            StringAssert.DoesNotContain("LegacyGachaStoreView(", overlay);
            StringAssert.Contains("GachaStoreView()", overlay);
            StringAssert.Contains(
                "GachaShippingRevealContinuation.preparePremiumDisplayCase =",
                overlay);
            StringAssert.Contains("self?.presentGachaPrizeDisplayCase(", overlay);
            StringAssert.Contains("requestID: requestID", overlay);
            StringAssert.Contains("receipt: receipt", overlay);
            StringAssert.Contains("title: \"收下\"", overlay);
            StringAssert.Contains("state: acceptingGachaResult", overlay);
        }

        [Test]
        public void ApprovedFanCardBannerKeepsItsIntrinsicShippingAspect()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string captureScript = ReadProjectFile(
                "Tools/GachaShippingNativePreview/capture-pack-v7.sh");
            string pipeline = ReadAsset("Editor/IosBuildPipeline.cs");
            string path = Path.Combine(
                Application.dataPath,
                "Plugins/iOS/GachaBanners/product-banner-magnetic-fan-card.png");

            StringAssert.Contains(
                "product-banner-magnetic-fan-card",
                storefront);
            StringAssert.Contains(
                ".scaledToFit()",
                storefront);
            StringAssert.Contains(
                ".aspectRatio(1179.0 / 654.0, contentMode: .fit)",
                storefront);
            StringAssert.Contains(
                "Assets/Plugins/iOS/GachaBanners",
                captureScript);
            StringAssert.Contains(
                "GachaBannerAssetRootPath",
                pipeline);
            Assert.That(File.Exists(path), Is.True, path);

            byte[] png = File.ReadAllBytes(path);
            Assert.That(png.Length, Is.GreaterThan(100_000), path);
            var texture = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            try
            {
                Assert.That(ImageConversion.LoadImage(texture, png, false), Is.True);
                Assert.That(texture.width, Is.EqualTo(1179));
                Assert.That(texture.height, Is.EqualTo(654));
            }
            finally
            {
                Object.DestroyImmediate(texture);
            }
        }

        [Test]
        public void ApprovedPackAssetsAreLayeredCompleteAndIndependentFromPrizeRarity()
        {
            string presentation = ReadAsset("Plugins/iOS/FidgetGachaPackPresentation.swift");
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string previewApp = ReadProjectFile(
                "Tools/GachaShippingNativePreview/GachaShippingNativePreviewApp.swift");
            string captureScript = ReadProjectFile(
                "Tools/GachaShippingNativePreview/capture-pack-v7.sh");
            string pipeline = ReadAsset("Editor/IosBuildPipeline.cs");
            string packRoot = Path.Combine(Application.dataPath, "Plugins/iOS/GachaPacks");

            StringAssert.Contains("public enum GachaPackTier", presentation);
            StringAssert.Contains("case standard", presentation);
            StringAssert.Contains("case refined", presentation);
            StringAssert.Contains("case signature", presentation);
            StringAssert.Contains("case chase", presentation);
            StringAssert.Contains("case grail", presentation);
            StringAssert.Contains("case oneOfOne = \"one-of-one\"", presentation);
            StringAssert.Contains("forSeriesId", presentation);
            StringAssert.DoesNotContain("GachaRarityTier", presentation);
            StringAssert.Contains("GachaPackAssetRootPath", pipeline);
            StringAssert.Contains("Path.Combine(projectRoot, GachaPackAssetRootPath)", pipeline);
            StringAssert.Contains("struct GachaPackTierShippingComparison", storefront);
            StringAssert.Contains("ForEach(GachaPackTier.allCases", storefront);
            StringAssert.Contains(
                "GachaPackVisual(tier: tier, tearProgress: normalizedProgress)",
                storefront);
            StringAssert.Contains("--preview-all-pack-tiers=", previewApp);
            StringAssert.Contains(
                "GachaShippingRevealContinuation.preparePremiumDisplayCase =",
                previewApp);
            StringAssert.DoesNotContain(
                "GachaShippingRevealContinuation.presentPremiumDisplayCase",
                previewApp);
            StringAssert.Contains("GachaPackTierShippingComparison(tearProgress: progress)", previewApp);
            StringAssert.Contains("--preview-all-pack-tiers=0", captureScript);
            StringAssert.Contains("--preview-all-pack-tiers=0.68", captureScript);
            StringAssert.Contains("gacha-pack-six-tier-shipping-contact-sheet.png", captureScript);

            string[] tiers =
            {
                "standard", "refined", "signature", "chase", "grail", "one-of-one"
            };
            string[] layers = { "body", "flap" };
            string[] paths = Directory.GetFiles(packRoot, "*.png", SearchOption.TopDirectoryOnly);
            Assert.That(paths, Has.Length.EqualTo(tiers.Length * layers.Length));
            var alphaBoundsByLayer = new Dictionary<string, RectInt>();
            var bodyPixelsByTier = new Dictionary<string, Color32[]>();

            foreach (string tier in tiers)
            {
                foreach (string layer in layers)
                {
                    string path = Path.Combine(packRoot, $"gacha-pack-{tier}-{layer}.png");
                    Assert.That(File.Exists(path), Is.True, path);
                    byte[] png = File.ReadAllBytes(path);
                    Assert.That(png.Length, Is.GreaterThan(1_000), path);
                    Assert.That(png[0], Is.EqualTo(0x89), path);
                    Assert.That(png[1], Is.EqualTo(0x50), path);

                    var texture = new Texture2D(2, 2, TextureFormat.RGBA32, false);
                    try
                    {
                        Assert.That(ImageConversion.LoadImage(texture, png, false), Is.True, path);
                        Assert.That(texture.width, Is.EqualTo(384), path);
                        Assert.That(texture.height, Is.EqualTo(512), path);
                        Color32[] pixels = texture.GetPixels32();
                        Assert.That(pixels.Any(pixel => pixel.a == 0), Is.True, path);
                        Assert.That(pixels.Any(pixel => pixel.a > 0), Is.True, path);
                        Assert.That(pixels[0].a, Is.EqualTo(0), $"Top/bottom edge must stay transparent: {path}");
                        Assert.That(pixels[texture.width - 1].a, Is.EqualTo(0), path);
                        Assert.That(pixels[pixels.Length - texture.width].a, Is.EqualTo(0), path);
                        Assert.That(pixels[pixels.Length - 1].a, Is.EqualTo(0), path);

                        RectInt alphaBounds = FindAlphaBounds(
                            pixels,
                            texture.width,
                            texture.height);
                        if (alphaBoundsByLayer.TryGetValue(layer, out RectInt expectedBounds))
                        {
                            Assert.That(
                                alphaBounds,
                                Is.EqualTo(expectedBounds),
                                $"All {layer} layers must keep identical scale/alignment: {path}");
                        }
                        else
                        {
                            alphaBoundsByLayer[layer] = alphaBounds;
                        }

                        if (layer == "body")
                        {
                            bodyPixelsByTier[tier] = pixels;
                        }
                    }
                    finally
                    {
                        Object.DestroyImmediate(texture);
                    }
                }
            }

            for (int first = 0; first < tiers.Length; first++)
            {
                for (int second = first + 1; second < tiers.Length; second++)
                {
                    double differenceRatio = CalculateVisibleRgbDifferenceRatio(
                        bodyPixelsByTier[tiers[first]],
                        bodyPixelsByTier[tiers[second]],
                        minimumChannelDelta: 12);
                    Assert.That(
                        differenceRatio,
                        Is.GreaterThan(0.015),
                        $"Tier materials are not visually distinct enough: "
                        + $"{tiers[first]} vs {tiers[second]} = {differenceRatio:P2}");
                }
            }
        }

        private static string ReadAsset(string relativePath)
        {
            string path = Path.Combine(Application.dataPath, relativePath);
            Assert.That(File.Exists(path), Is.True, $"Missing shipping source: {path}");
            return File.ReadAllText(path);
        }

        private static string ReadProjectFile(string relativePath)
        {
            string projectRoot = Directory.GetParent(Application.dataPath).FullName;
            string path = Path.Combine(projectRoot, relativePath);
            Assert.That(File.Exists(path), Is.True, $"Missing project evidence source: {path}");
            return File.ReadAllText(path);
        }

        private static RectInt FindAlphaBounds(Color32[] pixels, int width, int height)
        {
            int minX = width;
            int minY = height;
            int maxX = -1;
            int maxY = -1;

            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    if (pixels[y * width + x].a == 0)
                    {
                        continue;
                    }

                    minX = Mathf.Min(minX, x);
                    minY = Mathf.Min(minY, y);
                    maxX = Mathf.Max(maxX, x);
                    maxY = Mathf.Max(maxY, y);
                }
            }

            Assert.That(maxX, Is.GreaterThanOrEqualTo(minX), "Layer has no visible alpha bounds.");
            Assert.That(maxY, Is.GreaterThanOrEqualTo(minY), "Layer has no visible alpha bounds.");
            return new RectInt(minX, minY, maxX - minX + 1, maxY - minY + 1);
        }

        private static double CalculateVisibleRgbDifferenceRatio(
            Color32[] first,
            Color32[] second,
            int minimumChannelDelta)
        {
            Assert.That(second.Length, Is.EqualTo(first.Length));
            int visible = 0;
            int different = 0;

            for (int index = 0; index < first.Length; index++)
            {
                if (first[index].a == 0 || second[index].a == 0)
                {
                    continue;
                }

                visible++;
                int delta = Mathf.Abs(first[index].r - second[index].r)
                    + Mathf.Abs(first[index].g - second[index].g)
                    + Mathf.Abs(first[index].b - second[index].b);
                if (delta >= minimumChannelDelta)
                {
                    different++;
                }
            }

            Assert.That(visible, Is.GreaterThan(0));
            return (double)different / visible;
        }
    }
}
