using System.IO;
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

            StringAssert.Contains("public struct GachaStoreView", storefront);
            StringAssert.Contains("@Environment(\\.dismiss) private var dismiss", storefront);
            StringAssert.Contains("Button(\"返回主页\")", storefront);
            StringAssert.Contains("model.draw(seriesId: series.id, count: 1, useCoins: false)", storefront);
            StringAssert.Contains("@State private var drawRequestInFlight = false", storefront);
            StringAssert.Contains("guard !drawRequestInFlight else { return }", storefront);
            StringAssert.Contains("drawRequestInFlight = true", storefront);
            StringAssert.Contains(".interactiveDismissDisabled(", storefront);
            StringAssert.Contains(".onDisappear", storefront);
            StringAssert.Contains("pendingReceipt = rows", legacy);
            StringAssert.DoesNotContain("count: 10", storefront);
            StringAssert.DoesNotContain("GachaCoinShopView", storefront);
            StringAssert.DoesNotContain("可购买商品", storefront);
            StringAssert.Contains(".scaledToFill()", storefront);
            StringAssert.Contains(".clipped()", storefront);
            StringAssert.Contains("GachaSingleDrawReveal", storefront);
            StringAssert.Contains("case back", storefront);
            StringAssert.Contains("case front", storefront);
            StringAssert.Contains("case readable", storefront);
            StringAssert.Contains("case exploded", storefront);
            StringAssert.Contains("case prizeOnly", storefront);
            StringAssert.Contains("case sheen", storefront);
            StringAssert.Contains("case complete", storefront);
            StringAssert.Contains("Button(\"收下\")", storefront);

            StringAssert.Contains("struct LegacyGachaStoreView", legacy);
            StringAssert.DoesNotContain("LegacyGachaStoreView(", overlay);
            StringAssert.Contains("GachaStoreView()", overlay);
        }

        private static string ReadAsset(string relativePath)
        {
            string path = Path.Combine(Application.dataPath, relativePath);
            Assert.That(File.Exists(path), Is.True, $"Missing shipping source: {path}");
            return File.ReadAllText(path);
        }
    }
}
