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
            string storefront = ReadAsset(
                "Plugins/iOS/FidgetGachaShippingStorefront.swift");
            string legacyStorefront = ReadAsset(
                "Plugins/iOS/FidgetGachaStorefront.swift");
            string legacy = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string overlay = ReadAsset("Plugins/iOS/CodexSwiftUIOverlay.swift");
            string components = ReadAsset(
                "Plugins/iOS/FidgetProductUIComponents.swift");

            StringAssert.Contains("public struct GachaStoreView", storefront);
            StringAssert.Contains("@Environment(\\.dismiss) private var dismiss", storefront);
            StringAssert.Contains("ProductPrimaryActionButton", storefront);
            StringAssert.Contains("ProductBottomActionDock", storefront);
            StringAssert.Contains("ProductScreenHeading", storefront);
            StringAssert.Contains("ProductStatusTag", storefront);
            StringAssert.Contains("ProductPackHueBackdrop", storefront);
            StringAssert.Contains("ProductPackTierCaption", storefront);
            // Price line follows the live wallet (tickets, then coins) and the
            // storefront aborts a failed draw instead of waiting out the receipt timeout.
            StringAssert.Contains("GachaPackPaymentRules.priceLine(", storefront);
            StringAssert.Contains("GachaPackPaymentRules.method(tickets: model.tickets, coins: model.coins)", storefront);
            StringAssert.Contains("onChange(of: model.lastFailureReason)", storefront);
            StringAssert.Contains("handleDrawFailure", storefront);
            StringAssert.Contains("storefrontOddsLine", storefront);
            StringAssert.Contains(".productDesignSystem()", storefront);
            StringAssert.Contains("model.draw(", storefront);
            StringAssert.Contains("requestID: transactionID", storefront);
            StringAssert.Contains("markPackCommitted", storefront);
            StringAssert.Contains("markReceiptArrived", storefront);
            StringAssert.Contains("markUnityCaseReady", storefront);
            // R037: the Pack drops when Unity reports the case has cleared the
            // mouth, not on a fixed handoff duration.
            StringAssert.Contains("case-crossing-pack-lip", storefront);
            StringAssert.Contains("beginNativeHybridPackDeparture", storefront);
            StringAssert.DoesNotContain("model.revealHandoffDurationSeconds", storefront);
            StringAssert.Contains("model.presentReveal", storefront);
            StringAssert.Contains("model.startReveal", storefront);
            StringAssert.Contains("model.acknowledgeReveal", storefront);
            StringAssert.Contains("model.interruptReveal", storefront);
            StringAssert.Contains(".interactiveDismissDisabled", storefront);
            StringAssert.Contains(".onDisappear", storefront);
            StringAssert.Contains("receiptRequestID", legacy);
            StringAssert.Contains("collectibleId", legacy);
            StringAssert.DoesNotContain("exploded", storefront);
            StringAssert.DoesNotContain("prizeOnly", storefront);
            StringAssert.DoesNotContain(".font(.system", storefront);
            StringAssert.Contains("#if LEGACY_GACHA_PRESENTATION", legacyStorefront);

            StringAssert.Contains("struct LegacyGachaStoreView", legacy);
            StringAssert.DoesNotContain("LegacyGachaStoreView(", overlay);
            StringAssert.Contains("GachaStoreView()", overlay);
            // Leaving the storefront must unhide the library panel that
            // setGachaPresentationActive(true) hid; selectTab alone does not.
            StringAssert.Contains("panelController?.view.isHidden = false", overlay);
            StringAssert.Contains("enum ProductActionState", components);
            StringAssert.Contains(
                "struct ProductPrimaryActionButton",
                components);
            StringAssert.Contains("struct ProductBottomActionDock", components);
            StringAssert.Contains("struct ProductStatusTag", components);
            StringAssert.Contains("struct ProductPackHueBackdrop", components);
            StringAssert.Contains("struct ProductPackTierCaption", components);
        }

        [Test]
        public void PackHolographicSheenFollowsDeviceMotionWithShakeSweep()
        {
            string storefront = ReadAsset(
                "Plugins/iOS/FidgetGachaShippingStorefront.swift");
            string components = ReadAsset(
                "Plugins/iOS/FidgetProductUIComponents.swift");
            string rules = ReadAsset(
                "Plugins/iOS/FidgetGachaPackPresentation.swift");
            string feed = ReadAsset(
                "Plugins/iOS/FidgetGachaPackMotionFeed.swift");
            string bridge = ReadAsset("Plugins/iOS/CodexIosDeviceMotion.mm");

            // FDB-GAC-036: rules are pure and testable; shake uses user
            // acceleration with hysteresis + cooldown, never Euler deltas.
            StringAssert.Contains("public enum GachaPackHolographicSheenRules", rules);
            StringAssert.Contains("public struct GachaPackShakeDetector", rules);
            StringAssert.Contains("shakeEnterG", rules);
            StringAssert.Contains("shakeExitG", rules);
            StringAssert.Contains("sweepCooldownSeconds", rules);
            StringAssert.Contains("userAccelerationG magnitude", rules);
            StringAssert.DoesNotContain("attitude.yaw -", rules);

            // One shared CMMotionManager with two arbitrated clients.
            StringAssert.Contains("CodexIosDeviceMotionNativeUiStart", bridge);
            StringAssert.Contains("CodexIosDeviceMotionNativeUiStop", bridge);
            StringAssert.Contains("StopSharedUpdatesIfIdle", bridge);
            StringAssert.Contains("unityClientActive || nativeUiClientActive", bridge);
            StringAssert.DoesNotContain("CMMotionManager()", feed);
            StringAssert.DoesNotContain("import CoreMotion", feed);
            StringAssert.Contains(
                "@_silgen_name(\"CodexIosDeviceMotionNativeUiStart\")",
                feed);
            StringAssert.Contains(
                "@_silgen_name(\"CodexIosDeviceMotionRead\")",
                feed);
            StringAssert.Contains("public func start(preferScripted: Bool)", feed);
            StringAssert.Contains("public func stop()", feed);
            StringAssert.Contains("case scripted", feed);

            // Storefront lifecycle: start while a sealed Pack is on screen,
            // stop at handoff / disappear; sheen only on the selected Pack.
            StringAssert.Contains(
                "@StateObject private var motion = GachaPackMotionFeed()",
                storefront);
            StringAssert.Contains(
                "motion.start(preferScripted: isGate12Preview)",
                storefront);
            StringAssert.Contains(".onDisappear {\n            motion.stop()", storefront);
            StringAssert.Contains(
                "motion: index == selectedIndex ? motion : nil",
                storefront);
            StringAssert.Contains("sheenPose: sheen,", storefront);
            StringAssert.Contains("sheenMaskAssetName: tier.foilAssetName", storefront);
            StringAssert.Contains("? tier.foilAssetName", storefront);
            StringAssert.Contains("motion.simulateShake()", storefront);

            // 2026-09-07 17:22 review: foil only on the emblem and the text.
            // Masks are generated deterministically from the body rasters.
            StringAssert.Contains("public var foilAssetName: String", rules);
            foreach (string tier in new[] {
                "standard", "refined", "signature", "chase", "grail", "one-of-one" })
            {
                Assert.IsTrue(
                    File.Exists(Path.Combine(
                        Application.dataPath,
                        "Plugins/iOS/GachaPacks/gacha-pack-" + tier + "-foil.png")),
                    tier + " foil mask must ship next to its body raster");
                // R051q (2026-09-08 22:31): reversed-out emblem over the tier
                // name in the storefront heading.
                Assert.IsTrue(
                    File.Exists(Path.Combine(
                        Application.dataPath,
                        "Plugins/iOS/GachaPacks/gacha-pack-" + tier + "-emblem.png")),
                    tier + " heading emblem must ship next to its body raster");
                // R051y (2026-09-09 09:06): the print is its own raster so
                // the runtime can parallax it against the foil.
                Assert.IsTrue(
                    File.Exists(Path.Combine(
                        Application.dataPath,
                        "Plugins/iOS/GachaPacks/gacha-pack-" + tier + "-print.png")),
                    tier + " print layer must ship next to its body raster");
            }
            StringAssert.Contains("public var printAssetName: String", rules);
            StringAssert.Contains("printAssetName: tier.printAssetName", storefront);
            StringAssert.Contains("public var emblemAssetName: String", rules);
            StringAssert.Contains("emblemAssetName: selectedPack.emblemAssetName", storefront);
            Assert.IsTrue(
                File.Exists(Path.Combine(
                    Application.dataPath,
                    "../Tools/GachaPackFoilMask/build_pack_foil_masks.py")),
                "foil masks must stay reproducible from the generator");

            // Component library: masked additive sheen, tilt on both hosts.
            StringAssert.Contains("struct ProductPackHolographicSheen: View", components);
            StringAssert.Contains(
                ".mask(ProductRasterAssetImage(name: maskAssetName))",
                components);
            StringAssert.Contains(".blendMode(.plusLighter)", components);
            StringAssert.Contains("var sheenMaskAssetName: String? = nil", components);
            StringAssert.Contains(
                "maskAssetName: sheenMaskAssetName ?? bodyAssetName",
                components);
            StringAssert.Contains("var idlePitchDegrees: Double = 0", components);
            StringAssert.Contains(
                "var sheenPose: GachaPackHolographicSheenRules.SheenPose? = nil",
                components);
        }

        [Test]
        public void PackTearUsesLicensedSourceFaithfulArcBackdropFromComponentLibrary()
        {
            string storefront = ReadAsset(
                "Plugins/iOS/FidgetGachaShippingStorefront.swift");
            string components = ReadAsset(
                "Plugins/iOS/FidgetProductUIComponents.swift");
            string rules = ReadAsset(
                "Plugins/iOS/FidgetGachaPackPresentation.swift");
            string notice = ReadProjectFile(
                "Docs/OpenSourceUI-DarkArcBands-MIT.md");
            string bundledNotice = ReadAsset(
                "StreamingAssets/ThirdPartyNotices/" +
                "OpenSourceUI-DarkArcBands-MIT.txt");

            StringAssert.Contains(
                "struct ProductPackArcBandsBackdrop: View",
                components);
            StringAssert.Contains(
                "@Environment(\\.accessibilityReduceTransparency)",
                components);
            StringAssert.Contains(".allowsHitTesting(false)", components);
            StringAssert.Contains(".accessibilityHidden(true)", components);
            StringAssert.Contains(
                "GachaPackArcBackdropRules.primaryWidthFraction",
                components);
            StringAssert.Contains("xRadiusFraction:", components);
            StringAssert.Contains("yRadiusFraction:", components);
            StringAssert.Contains("path.addEllipse", components);

            StringAssert.Contains("usesPackArcBackdrop", storefront);
            StringAssert.Contains(
                "ProductPackArcBandsBackdrop(",
                storefront);
            // 2026-09-07 user amendment to FDB-GAC-035: the arc bands are the
            // carousel backdrop and take the selected Pack tier's hue. The
            // receipt / rarity must never reach the layer.
            StringAssert.Contains(
                "case .choosingPack, .selectionRive, .tearPack,",
                storefront);
            StringAssert.Contains(
                "colourway: GachaPackArcBackdropRules.Colourway",
                storefront);
            StringAssert.Contains(".forTier(selectedPack))", storefront);
            StringAssert.Contains(".id(selectedPack)", storefront);
            StringAssert.DoesNotContain("forTier(receipt", storefront);
            StringAssert.DoesNotContain("selectionBackdropOpacity:", storefront);
            StringAssert.Contains(
                "GachaPackArcBackdropRules.primaryStops(for: colourway)",
                components);
            StringAssert.Contains(
                "GachaPackArcBackdropRules.softStops(for: colourway)",
                components);
            StringAssert.Contains("public enum Colourway", rules);
            StringAssert.Contains("case .oneOfOne: return .source", rules);
            StringAssert.DoesNotContain("tonalColor", components);
            StringAssert.Contains(
                "GachaPackArcBackdropRules.primaryStops",
                components);
            StringAssert.Contains(
                "GachaPackArcBackdropRules.softStops",
                components);
            StringAssert.DoesNotContain("colorMode: .linear", components);
            StringAssert.Contains(
                "tearProgress: tearProgress",
                storefront);
            StringAssert.DoesNotContain(
                "accentRGB: receipt",
                storefront);

            StringAssert.Contains(
                "public enum GachaPackArcBackdropRules",
                rules);
            StringAssert.Contains(
                "d239c3463c984a099dd2cb67817a41fc0bcc876f",
                rules);
            StringAssert.Contains(
                "b13404dd73e02a4267b48ff1136aa3c1b2205827",
                rules);
            // Present from the carousel; only the seal flight fades it out.
            StringAssert.Contains(
                "return clamped(GachaPackOpeningRules.sealExitOpacity(",
                rules);
            StringAssert.DoesNotContain("entered * sealVisibility", rules);
            StringAssert.Contains("gradientStopsAreValid", rules);
            StringAssert.Contains("opacity: 0.34, location: 0.0", rules);
            StringAssert.Contains("opacity: 0.28, location: 0.18", rules);
            StringAssert.Contains("opacity: 0.22, location: 0.40", rules);
            StringAssert.Contains("opacity: 0.18, location: 0.62", rules);
            StringAssert.Contains("public static let baseOpacity = 1.0", rules);
            StringAssert.Contains("public static let liftPeakOpacity = 0.08", rules);
            StringAssert.Contains("public static let dotDiameterPoints = 2.0", rules);
            StringAssert.Contains("public static let dotColorOpacity = 0.70", rules);
            StringAssert.Contains("public static let dotLayerOpacity = 0.04", rules);

            StringAssert.Contains("Copyright (c) 2026 Bidyut Kundu", notice);
            StringAssert.Contains("MIT License", notice);
            StringAssert.Contains(
                "fixed source palette",
                notice);
            StringAssert.Contains(
                "Copyright (c) 2026 Bidyut Kundu",
                bundledNotice);
            StringAssert.Contains(
                "d239c3463c984a099dd2cb67817a41fc0bcc876f",
                bundledNotice);
        }

        private static string ReadAsset(string relativePath)
        {
            string path = Path.Combine(Application.dataPath, relativePath);
            Assert.That(File.Exists(path), Is.True, $"Missing shipping source: {path}");
            return File.ReadAllText(path);
        }

        private static string ReadProjectFile(string relativePath)
        {
            string path = Path.GetFullPath(Path.Combine(
                Application.dataPath,
                "..",
                relativePath));
            Assert.That(File.Exists(path), Is.True, $"Missing project file: {path}");
            return File.ReadAllText(path);
        }
    }
}
