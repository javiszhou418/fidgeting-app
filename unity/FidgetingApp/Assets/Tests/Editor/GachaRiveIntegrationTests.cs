using System;
using System.IO;
using System.Security.Cryptography;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaRiveIntegrationTests
    {
        private const string ExpectedRiveSha256 =
            "da5ba78f63c09ea538d214f7bcdd520a852fc77232bf47ef31606106136c7717";

        [Test]
        public void CanonicalRiveAssetIsBundledAndHashLocked()
        {
            string path = Path.Combine(
                Application.dataPath,
                "Plugins/iOS/Rive/gacha-single-draw-jumbotron.riv");

            Assert.That(File.Exists(path), Is.True, path);
            Assert.That(new FileInfo(path).Length, Is.EqualTo(357120));
            using (FileStream stream = File.OpenRead(path))
            using (SHA256 sha256 = SHA256.Create())
            {
                string actual = BitConverter.ToString(sha256.ComputeHash(stream))
                    .Replace("-", string.Empty)
                    .ToLowerInvariant();
                Assert.That(actual, Is.EqualTo(ExpectedRiveSha256));
            }
        }

        [Test]
        public void BuildPipelineCopiesAssetAndPinsOfficialRiveSwiftPackageRange()
        {
            string pipeline = ReadAsset("Editor/IosBuildPipeline.cs");

            StringAssert.Contains("ConfigureGachaRiveRuntime(projectRoot, outputPath)", pipeline);
            StringAssert.Contains("gacha-single-draw-jumbotron.riv", pipeline);
            StringAssert.Contains(ExpectedRiveSha256, pipeline);
            StringAssert.Contains("https://github.com/rive-app/rive-ios", pipeline);
            StringAssert.Contains("RiveMinimumVersion = \"6.23.1\"", pipeline);
            StringAssert.Contains("RiveMaximumVersion = \"6.24.0\"", pipeline);
            StringAssert.Contains("AddRemotePackageReferenceWithVersionRange", pipeline);
            StringAssert.Contains("frameworkTarget,\n                \"RiveRuntime\"", pipeline);
            StringAssert.Contains("mainTarget,\n                \"RiveRuntime\"", pipeline);
            StringAssert.Contains("project.AddFileToBuild(mainTarget, assetGuid)", pipeline);
        }

        [Test]
        public void SingleDrawRequiresPackCommitReceiptAndUnityReadiness()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string gate = ReadAsset("Plugins/iOS/FidgetGachaRiveGateRules.swift");
            string presentation = ReadAsset("Plugins/iOS/FidgetGachaRivePresentation.swift");

            int beginIndex = storefront.IndexOf(
                "singleDrawGate.begin(transactionID: transactionID)",
                StringComparison.Ordinal);
            int drawIndex = storefront.IndexOf(
                "model.draw(\n            requestID: transactionID",
                StringComparison.Ordinal);
            Assert.That(beginIndex, Is.GreaterThanOrEqualTo(0));
            Assert.That(drawIndex, Is.GreaterThan(beginIndex));

            StringAssert.Contains("unityCaseReady", gate);
            StringAssert.Contains("commitPackSelection", gate);
            StringAssert.Contains("markSelectionAnimationFinished", gate);
            StringAssert.Contains("markPackCommitted", gate);
            StringAssert.Contains("markUnityCaseReady", storefront);
            StringAssert.Contains("markReceiptArrived", storefront);
            StringAssert.Contains("markReceiptTimedOut", storefront);
            StringAssert.Contains("awaitingReceiptRecovery", storefront);
            StringAssert.Contains("decision(transactionID: transactionID) == .reveal", storefront);
            StringAssert.Contains("GachaSingleDrawRiveGate(", storefront);
            StringAssert.Contains("stage: .packSelection", storefront);
            StringAssert.DoesNotContain("stage: .magneticHolder", storefront);
            StringAssert.Contains("transactionID: transactionID", storefront);
            StringAssert.Contains(
                "preparePremiumDisplayCase",
                storefront);
            StringAssert.Contains(
                "revealSetupSucceeded",
                storefront);
            StringAssert.DoesNotContain("GachaReceiptRow", presentation);
            StringAssert.DoesNotContain("GachaRarityTier", presentation);
            StringAssert.DoesNotContain("receipt:", presentation);
            StringAssert.Contains("UIApplication.didBecomeActiveNotification", storefront);
            StringAssert.Contains("UIApplication.willResignActiveNotification", storefront);
            StringAssert.Contains("guard applicationIsActive", storefront);
            StringAssert.Contains("awaitingReceiptRecovery = true", gate);
            StringAssert.DoesNotContain("phase = .receiptRecovery", gate);
            StringAssert.Contains("accessibilityReduceMotion", presentation);
            StringAssert.Contains("GachaSingleDrawReceiptRecoveryView", presentation);
            StringAssert.Contains("if rows.count > 1", storefront);
            StringAssert.DoesNotContain("showMultiResults = !rows.isEmpty", storefront);
        }

        [Test]
        public void PackStaysVisibleUntilTheRealUnityCaseIsReady()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string gate = ReadAsset("Plugins/iOS/FidgetGachaRiveGateRules.swift");
            string presentation = ReadAsset(
                "Plugins/iOS/FidgetGachaRivePresentation.swift");
            string harness = ReadProjectFile(
                "Tools/GachaShippingNativePreview/GachaRiveGateRulesHarness.swift");

            StringAssert.Contains(
                "static let packToCaseTransitionSeconds: Double = 0.28",
                gate);
            StringAssert.Contains(
                "mutating func markUnityCaseReady(",
                gate);
            StringAssert.Contains(
                "phase = authoritativeReceiptArrived ? .preparingCase : .waitingForReceipt",
                gate);
            StringAssert.Contains(
                "case .tearPack, .preparingCase, .waitingForReceipt, .handoff:",
                storefront);
            StringAssert.Contains(
                "private var packToCaseSurface: some View",
                storefront);
            StringAssert.Contains(
                "[GachaSequence] pack-case-overlap-start request=",
                storefront);
            StringAssert.Contains(
                "[GachaSequence] pack-case-overlap-complete request=",
                storefront);

            int surfaceStart = storefront.IndexOf(
                "private var packToCaseSurface: some View",
                StringComparison.Ordinal);
            int tearStart = storefront.IndexOf(
                "private var tearSurface: some View",
                StringComparison.Ordinal);
            Assert.That(surfaceStart, Is.GreaterThanOrEqualTo(0));
            Assert.That(tearStart, Is.GreaterThan(surfaceStart));
            string sharedSurface = storefront.Substring(
                surfaceStart,
                tearStart - surfaceStart);
            StringAssert.Contains("tearSurface", sharedSurface);
            StringAssert.DoesNotContain("GachaSingleDrawRiveGate(", sharedSurface);
            StringAssert.Contains(
                "phase == .preparingCase || phase == .waitingForReceipt",
                sharedSurface);
            StringAssert.Contains(
                ".accessibilityIdentifier(\"gacha-pack-case-transition\")",
                sharedSurface);

            StringAssert.Contains("let playbackEnabled: Bool", presentation);
            StringAssert.Contains(
                "playback.setPresentationEnabled(playbackEnabled)",
                presentation);
            StringAssert.Contains(
                ".opacity(playbackEnabled ? 1 : 0)",
                presentation);
            StringAssert.Contains(
                ".animation(nil, value: playbackEnabled)",
                presentation);
            StringAssert.DoesNotContain(
                ".opacity(isPresented ? 1 : 0)",
                presentation);
            StringAssert.Contains(
                "private var isPresentationEnabled = false",
                presentation);
            StringAssert.Contains(
                "isPresentationEnabled,",
                presentation);
            StringAssert.Contains(
                "GachaSingleDrawGateState.packToCaseTransitionSeconds == 0.28",
                harness);
            StringAssert.Contains("markUnityCaseReady", harness);
        }

        [Test]
        public void HolderIdentityReplacesAuctionBrandingAndKeepsNeutralGradeAndSerial()
        {
            string source = ReadAsset(
                "Plugins/iOS/FidgetGachaRivePresentation.swift");
            string artworkPath = Path.Combine(
                Application.dataPath,
                "Plugins/iOS/Thumbnails/Models/product-thumbnail-metal-three-blade.png");

            Assert.That(File.Exists(artworkPath), Is.True, artworkPath);
            Assert.That(new FileInfo(artworkPath).Length, Is.GreaterThan(1_000));
            StringAssert.Contains("private enum GachaHolderIdentity", source);
            StringAssert.Contains(
                "artworkAssetName = \"product-thumbnail-metal-three-blade\"",
                source);
            StringAssert.Contains(
                "replacedRiveLogoAssetPrefix = \"colographih-\"",
                source);
            StringAssert.Contains("productName = \"METAL THREE-BLADE\"", source);
            StringAssert.Contains("gradeLabel = \"GEM/MINT\"", source);
            StringAssert.Contains("gradeValue = \"10\"", source);
            StringAssert.Contains("serialNumber = \"#00000001\"", source);
            StringAssert.Contains(
                "paletteMarker = \"neutralGraphiteSilver\"",
                source);
            StringAssert.Contains(
                "surfaceMarker = \"productOwnedMagneticHolderSurface\"",
                source);
            StringAssert.Contains(
                "hiddenRiveCompletionOpacity = 0.001",
                source);
            StringAssert.Contains(
                "entranceOffsetX: CGFloat = 96",
                source);
            StringAssert.Contains(
                "entranceTiltDegrees = -38.0",
                source);
            StringAssert.Contains(
                "accessibilityIdentifier = \"gacha-holder-product-identity\"",
                source);
            StringAssert.Contains(
                "holder-product-artwork-loaded asset=",
                source);
            StringAssert.Contains(
                "holder-product-surface-prepared asset=",
                source);
            StringAssert.Contains(
                "holder-product-surface-visible surface=",
                source);
            StringAssert.Contains(
                ".opacity(stage == .magneticHolder",
                source);
            StringAssert.DoesNotContain("Color.yellow", source);
            StringAssert.DoesNotContain("Color.green", source);
            StringAssert.DoesNotContain("WHATNOT", source);
            StringAssert.DoesNotContain("showsHolderProductIdentity", source);
            StringAssert.DoesNotContain("revealAfterActiveSeconds", source);
            StringAssert.DoesNotContain("fullCover", source);
            StringAssert.DoesNotContain(
                "GachaHolderProductIdentitySurface",
                source);

            int playbackSurfaceStart = source.IndexOf(
                "private struct GachaRivePlaybackSurface",
                StringComparison.Ordinal);
            int holderIdentitySurfaceStart = source.IndexOf(
                "private struct GachaProductOwnedMagneticHolderSurface",
                StringComparison.Ordinal);
            Assert.That(playbackSurfaceStart, Is.GreaterThanOrEqualTo(0));
            Assert.That(
                holderIdentitySurfaceStart,
                Is.GreaterThan(playbackSurfaceStart));
            string playbackSurface = source.Substring(
                playbackSurfaceStart,
                holderIdentitySurfaceStart - playbackSurfaceStart);
            StringAssert.Contains("if stage == .magneticHolder {", playbackSurface);
            StringAssert.Contains(
                "? GachaHolderIdentity.hiddenRiveCompletionOpacity",
                playbackSurface);
            StringAssert.Contains(
                "GachaProductOwnedMagneticHolderSurface(",
                playbackSurface);
            StringAssert.Contains(
                "playbackEnabled: playbackEnabled",
                playbackSurface);
            StringAssert.Contains(".zIndex(10)", playbackSurface);

            int identityLabelStart = source.IndexOf(
                "private struct GachaProductOwnedMagneticHolderSurface",
                StringComparison.Ordinal);
            int selectionHaloStart = source.IndexOf(
                "private enum GachaRiveLayer",
                StringComparison.Ordinal);
            Assert.That(identityLabelStart, Is.GreaterThanOrEqualTo(0));
            Assert.That(selectionHaloStart, Is.GreaterThan(identityLabelStart));
            string identityLabel = source.Substring(
                identityLabelStart,
                selectionHaloStart - identityLabelStart);
            StringAssert.Contains("let playbackEnabled: Bool", identityLabel);
            StringAssert.Contains("@State private var isPresented = false", identityLabel);
            StringAssert.Contains(".opacity(playbackEnabled ? 1 : 0)", identityLabel);
            StringAssert.Contains(
                ".animation(nil, value: playbackEnabled)",
                identityLabel);
            StringAssert.DoesNotContain(
                ".opacity(isPresented ? 1 : 0)",
                identityLabel);
            StringAssert.Contains(".rotation3DEffect(", identityLabel);
            StringAssert.Contains(".onChange(of: playbackEnabled)", identityLabel);
            StringAssert.Contains("guard playbackEnabled else { return }", identityLabel);
            StringAssert.Contains(
                ".accessibilityHidden(!playbackEnabled)",
                identityLabel);
            StringAssert.Contains("private func presentHolder()", identityLabel);
            StringAssert.Contains(
                "if let artwork = GachaHolderIdentity.artworkImage",
                identityLabel);
            StringAssert.Contains("Image(uiImage: artwork)", identityLabel);
            StringAssert.Contains(".frame(width: 148, height: 148)", identityLabel);
            StringAssert.DoesNotContain("Image(systemName:", identityLabel);
            StringAssert.Contains("Text(GachaHolderIdentity.productName)", identityLabel);
            StringAssert.Contains("Text(GachaHolderIdentity.gradeLabel)", identityLabel);
            StringAssert.Contains("Text(GachaHolderIdentity.gradeValue)", identityLabel);
            StringAssert.Contains("Text(GachaHolderIdentity.serialNumber)", identityLabel);
            StringAssert.Contains(".frame(width: 218, height: 318)", identityLabel);
            StringAssert.DoesNotContain("GeometryReader", identityLabel);
            StringAssert.DoesNotContain("transactionID", identityLabel);
            StringAssert.DoesNotContain("receipt", identityLabel);
            StringAssert.DoesNotContain("rarity", identityLabel);

            int loaderStart = source.IndexOf(
                "private func loadGachaRiveEmbeddedAsset(",
                StringComparison.Ordinal);
            int coordinatorStart = source.IndexOf(
                "private final class GachaRivePlaybackCoordinator",
                StringComparison.Ordinal);
            Assert.That(loaderStart, Is.GreaterThanOrEqualTo(0));
            Assert.That(coordinatorStart, Is.GreaterThan(loaderStart));
            string loader = source.Substring(
                loaderStart,
                coordinatorStart - loaderStart);
            StringAssert.Contains(
                "filename.hasPrefix(GachaHolderIdentity.replacedRiveLogoAssetPrefix)",
                loader);
            StringAssert.Contains(
                "guard let replacement = GachaHolderIdentity.artworkData else",
                loader);
            StringAssert.Contains("return false", loader);
            StringAssert.Contains("renderedData = replacement", loader);
            StringAssert.Contains(
                "imageAsset.renderImage(factory.decodeImage(renderedData))",
                loader);
        }

        [Test]
        public void RiveWrapperUsesOfflineSplitArtboardsAndAssetAuthoredCompletion()
        {
            string source = ReadAsset("Plugins/iOS/FidgetGachaRivePresentation.swift");

            StringAssert.Contains("#if canImport(RiveRuntime)", source);
            StringAssert.Contains("import RiveRuntime", source);
            StringAssert.Contains("375.0 / 812.0", source);
            StringAssert.Contains("case background = \"background/mint-slab\"", source);
            StringAssert.Contains("case foreground = \"foreground/mint-slab\"", source);
            StringAssert.Contains("stateMachineName: \"Main\"", source);
            StringAssert.Contains("loadCdn: false", source);
            StringAssert.Contains("customLoader: loadGachaRiveEmbeddedAsset", source);
            StringAssert.Contains("GachaRiveAssetLocator.resolveBundle()", source);
            StringAssert.Contains("Bundle.main", source);
            StringAssert.Contains("Bundle(for: GachaRiveBundleSentinel.self)", source);
            StringAssert.Contains(
                "imageAsset.renderImage(factory.decodeImage(renderedData))",
                source);
            StringAssert.Contains("enableAutoBind", source);
            StringAssert.Contains("T2_SPORTS_CARD_JUMBOTRON", source);
            StringAssert.Contains("T2_COIN_FLIP_JUMBOTRON", source);
            // The pack-selection stage no longer shows a visible halo/ring
            // around the Pack; the "rotate-line" artboard and its dedicated
            // playback model were removed along with it. Only the invisible
            // completion-signal surface remains.
            StringAssert.DoesNotContain("artboardName: \"rotate-line\"", source);
            StringAssert.DoesNotContain("gacha-selection-rive-visible-halo", source);
            StringAssert.Contains(".frame(width: 240, height: 240)", source);
            StringAssert.Contains("withName: \"Slab-rotate-v01\"", source);
            StringAssert.Contains("withName: \"Coin_Slab_v09-sm\"", source);
            StringAssert.Contains("fromPath: \"backgroundArtboard\"", source);
            StringAssert.Contains("fromPath: \"foregroundArtboard\"", source);
            StringAssert.Contains("internalViewModel/playBackground", source);
            StringAssert.Contains("internalViewModel/playForeground", source);
            StringAssert.Contains(
                "requiredLayers.isSubset(of: renderedLayers)",
                source);
            StringAssert.Contains(
                "purchase-trigger synchronizedLayers=\\(requiredLayers.count)",
                source);
            StringAssert.Contains("stateName.caseInsensitiveCompare(\"in\")", source);
            StringAssert.Contains("stateName.caseInsensitiveCompare(\"Idle\")", source);
            StringAssert.Contains("source: \"stateMachineCycle\"", source);
            StringAssert.Contains(
                "requiredLayers.isSubset(of: endedLayers)",
                source);
            StringAssert.Contains("triggerProperty(fromPath: \"animationEnded\")", source);
            StringAssert.Contains("animationEndedProperty.removeListener", source);
            StringAssert.Contains("riveModel?.disableAutoBind()", source);
            StringAssert.Contains("play()", source);
            StringAssert.Contains("pause()", source);
            StringAssert.Contains("finishFromWatchdog", source);
            StringAssert.Contains("UIApplication.didBecomeActiveNotification", source);
            StringAssert.Contains("UIApplication.willResignActiveNotification", source);
            StringAssert.Contains("setApplicationActive", source);
            StringAssert.DoesNotContain("@Environment(\\.scenePhase)", source);
            StringAssert.Contains("NSLog", source);
            StringAssert.Contains("FIDGET ARCHIVE", source);
            StringAssert.Contains("COLLECTION UNLOCKING", source);
            StringAssert.DoesNotContain(".font(.system", source);
            StringAssert.DoesNotContain(".tracking(", source);
            StringAssert.DoesNotContain(".kerning(", source);
            StringAssert.DoesNotContain("setViewModelInstance(instance)", source);
            StringAssert.DoesNotContain("triggerProperty(fromPath: \"purchase\")?.trigger()", source);
        }

        [Test]
        public void MetalThreeBladeReceiptOwnershipAndUnityRevealStayCanonical()
        {
            string catalog = ReadAsset("Scripts/Product/Gacha/GachaCatalog.cs");
            string inventory = ReadAsset("Scripts/Product/Gacha/GachaInventory.cs");
            string coordinator = ReadAsset("Scripts/Product/FidgetAppCoordinator.cs");
            string store = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string overlay = ReadAsset("Plugins/iOS/CodexSwiftUIOverlay.swift");

            StringAssert.Contains(
                "canyon-heir-metal-three-blade",
                catalog);
            StringAssert.Contains("GachaPrizeKind.Toy", catalog);
            StringAssert.Contains("toy/metal-three-blade", catalog);
            StringAssert.Contains(
                "DrawOnceForDevelopmentPreview",
                inventory);
            StringAssert.Contains("Debug.isDebugBuild", coordinator);
            StringAssert.Contains(
                "prize.Value.Id,\n                    Gacha.GachaCatalog.MetalThreeBladePrizeId",
                coordinator);
            StringAssert.Contains(
                "prize.Value.Kind != Gacha.GachaPrizeKind.Toy",
                coordinator);
            StringAssert.Contains(
                "prize.Value.ContentReference",
                coordinator);
            StringAssert.Contains(
                "activeGachaRevealDirector.revealCompleted +=",
                coordinator);
            StringAssert.Contains(
                "GachaInventory.AcknowledgePendingReceipt",
                coordinator);
            StringAssert.Contains(
                "--preview-authoritative-metal-three-blade",
                store);
            StringAssert.Contains(
                "--preview-gacha-funding-token=",
                store);
            StringAssert.Contains(
                "value: \"metal-three-blade-v1\"",
                store);
            StringAssert.Contains("Debug.isDebugBuild", coordinator);
            StringAssert.Contains(
                "CreditDevelopmentPreviewTicketOnce",
                coordinator);
            StringAssert.DoesNotContain(
                "Environment.GetCommandLineArgs",
                coordinator);
            StringAssert.Contains(
                "DevelopmentPreviewFundingToken",
                inventory);
            StringAssert.Contains(
                "PlayerPrefs.GetInt(\n                    Key(DevelopmentPreviewFundingKey)",
                inventory);
            StringAssert.Contains(
                "presentGachaPrizeDisplayCase(\n                requestID: requestID,\n                receipt: receipt)",
                overlay);
            StringAssert.Contains("gacha-3d-reveal-root", overlay);
            StringAssert.Contains("modelId=metal-three-blade;prizeId=", overlay);
            StringAssert.Contains(
                "ConfirmGachaRevealReadyAfterTwoFrames",
                coordinator);
            StringAssert.Contains(
                "awaitingUserAcceptance=true",
                coordinator);
            StringAssert.Contains("title: \"收下\"", overlay);
            StringAssert.Contains("state: acceptingGachaResult", overlay);
        }

        private static string ReadAsset(string relativePath)
        {
            return File.ReadAllText(Path.Combine(Application.dataPath, relativePath));
        }

        private static string ReadProjectFile(string relativePath)
        {
            return File.ReadAllText(Path.Combine(
                Application.dataPath,
                "..",
                relativePath));
        }
    }
}
