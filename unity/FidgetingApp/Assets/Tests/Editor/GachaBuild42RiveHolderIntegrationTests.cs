using System;
using System.IO;
using System.Security.Cryptography;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaBuild42RiveHolderIntegrationTests
    {
        private const string ExpectedRiveSha256 =
            "da5ba78f63c09ea538d214f7bcdd520a852fc77232bf47ef31606106136c7717";

        [Test]
        public void CanonicalHolderClockIsHashLockedAndBundledByTheIosPipeline()
        {
            string assetPath = Path.Combine(
                Application.dataPath,
                "Plugins/iOS/Rive/gacha-single-draw-jumbotron.riv");
            Assert.That(File.Exists(assetPath), Is.True, assetPath);
            Assert.That(new FileInfo(assetPath).Length, Is.EqualTo(357120));

            using (FileStream stream = File.OpenRead(assetPath))
            using (SHA256 sha256 = SHA256.Create())
            {
                string actual = BitConverter.ToString(sha256.ComputeHash(stream))
                    .Replace("-", string.Empty)
                    .ToLowerInvariant();
                Assert.That(actual, Is.EqualTo(ExpectedRiveSha256));
            }

            string pipeline = ReadAsset("Editor/IosBuildPipeline.cs");
            StringAssert.Contains(
                "ConfigureGachaRiveRuntime(projectRoot, outputPath)",
                pipeline);
            StringAssert.Contains(ExpectedRiveSha256, pipeline);
            StringAssert.Contains(
                "https://github.com/rive-app/rive-ios",
                pipeline);
            StringAssert.Contains("RiveMinimumVersion = \"6.23.1\"", pipeline);
            StringAssert.Contains("RiveMaximumVersion = \"6.24.0\"", pipeline);
            StringAssert.Contains(
                "AddRemotePackageReferenceWithVersionRange",
                pipeline);
            StringAssert.Contains(
                "frameworkTarget,\n                \"RiveRuntime\"",
                pipeline);
            StringAssert.Contains(
                "mainTarget,\n                \"RiveRuntime\"",
                pipeline);
            StringAssert.Contains(
                "project.AddFileToBuild(mainTarget, assetGuid)",
                pipeline);
        }

        [Test]
        public void PreparedPackOverlapsTheProductHolderBeforeExactOnceBuild42Handoff()
        {
            string storefront = ReadAsset(
                "Plugins/iOS/FidgetGachaStorefront.swift");
            string model = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string gate = ReadAsset(
                "Plugins/iOS/FidgetGachaRiveGateRules.swift");

            string commitPack = Slice(
                storefront,
                "private func commitPackOpen(source: String)",
                "private func holderRiveFinished(");
            string holderFinished = Slice(
                storefront,
                "private func holderRiveFinished(",
                "private enum GachaPackInteractionTrace");
            string transactionIngestion = Slice(
                model,
                "private func parseTransactionPayload(",
                "public func receiveRevealSetup(");

            StringAssert.Contains(
                "static let packToHolderTransitionSeconds: Double = 0.28",
                gate);
            StringAssert.Contains("stage: .magneticHolder", storefront);
            StringAssert.Contains(
                "playbackEnabled: holderRevealStarted",
                storefront);
            StringAssert.Contains("packSurface", storefront);
            StringAssert.Contains(".zIndex(1)", storefront);
            StringAssert.Contains(".zIndex(2)", storefront);
            StringAssert.Contains(
                "[GachaSequence] pack-holder-overlap-start request=",
                commitPack);
            StringAssert.Contains(
                "GachaSingleDrawGateState\n                            .packToHolderTransitionSeconds",
                commitPack);
            StringAssert.Contains("holderRevealStarted = true", commitPack);
            StringAssert.Contains("packVisible = false", commitPack);
            StringAssert.DoesNotContain(
                "model.commitPackOpening(requestId:",
                commitPack);

            StringAssert.Contains(
                "holderCompletionDispatched = true",
                holderFinished);
            StringAssert.Contains(
                "GachaSingleDrawGateState.packToHolderTransitionSeconds - elapsed",
                holderFinished);
            StringAssert.Contains(
                "[GachaSequence] holder-rive-completed request=",
                holderFinished);
            // This build intentionally bypasses the Unity 3D
            // PremiumDisplayCase handoff: the holder marks the transaction
            // ready for acceptance directly and shows the real prize itself.
            StringAssert.Contains(
                "[GachaSequence] holder-reveal-accept-ready request=",
                holderFinished);
            StringAssert.Contains(
                "model.markHolderRevealed(requestId: transaction.requestId)",
                holderFinished);
            StringAssert.Contains(
                "holderRevealAcceptReady = true",
                holderFinished);
            StringAssert.DoesNotContain(
                "model.commitPackOpening(requestId:",
                holderFinished);

            StringAssert.Contains("if phase == .prepared", transactionIngestion);
            StringAssert.Contains(
                "packGateRequestId = requestId",
                transactionIngestion);
            StringAssert.Contains(
                "case .awaitingAcceptance:",
                transactionIngestion);
            StringAssert.Contains(
                "packGateRequestId = \"\"",
                transactionIngestion);
            StringAssert.Contains(
                "gacha-pack-holder-transition",
                storefront);
            StringAssert.Contains(
                "gacha-holder-playback-state",
                storefront);
            StringAssert.DoesNotContain("GachaCaseRevealVisual", storefront);
            StringAssert.DoesNotContain(
                "GachaShippingRevealContinuation",
                storefront);
            StringAssert.DoesNotContain(
                "presentPremiumDisplayCase",
                storefront);
        }

        [Test]
        public void VisibleHolderShowsTheRealDrawnPrizeAndTheRiveHolderIsOnlyAHiddenClock()
        {
            string source = ReadAsset(
                "Plugins/iOS/FidgetGachaRivePresentation.swift");
            string artworkPath = Path.Combine(
                Application.dataPath,
                "Plugins/iOS/Thumbnails/Models/product-thumbnail-metal-three-blade.png");

            // The hidden Rive layer still needs some valid embedded image to
            // decode; it is never seen, so any bundled PNG satisfies it.
            Assert.That(File.Exists(artworkPath), Is.True, artworkPath);
            Assert.That(new FileInfo(artworkPath).Length, Is.GreaterThan(1_000));
            StringAssert.Contains(
                "assetName = \"product-thumbnail-metal-three-blade\"",
                source);

            // The holder is built from the real receipt row rather than a
            // fixed placeholder; the old auction-branding identity constants
            // must be gone, not just hidden.
            StringAssert.DoesNotContain("productName = \"METAL THREE-BLADE\"", source);
            StringAssert.DoesNotContain("gradeLabel = \"GEM/MINT\"", source);
            StringAssert.DoesNotContain("gradeValue = \"10\"", source);
            StringAssert.DoesNotContain("serialNumber = \"#00000001\"", source);
            StringAssert.Contains(
                "private struct GachaHolderIdentity",
                source);
            StringAssert.Contains(
                "static func resolve(from row: GachaReceiptRow?) -> GachaHolderIdentity",
                source);
            StringAssert.Contains("row.name.uppercased()", source);
            StringAssert.Contains("row.rarity.tint", source);
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
                "private struct GachaProductOwnedMagneticHolderSurface",
                source);
            StringAssert.Contains(
                "GachaProductOwnedMagneticHolderSurface(",
                source);
            StringAssert.Contains(
                "? GachaHolderIdentity.hiddenRiveCompletionOpacity",
                source);
            StringAssert.Contains(
                "accessibilityIdentifier = \"gacha-holder-product-identity\"",
                source);
            StringAssert.Contains(
                "holder-product-surface-visible surface=",
                source);
            StringAssert.DoesNotContain("WHATNOT", source);
        }

        private static string ReadAsset(string relativePath)
        {
            string path = Path.Combine(Application.dataPath, relativePath);
            Assert.That(File.Exists(path), Is.True, $"Missing shipping source: {path}");
            return File.ReadAllText(path);
        }

        private static string Slice(string source, string start, string end)
        {
            int startIndex = source.IndexOf(start, StringComparison.Ordinal);
            Assert.That(startIndex, Is.GreaterThanOrEqualTo(0), $"Missing marker: {start}");
            int endIndex = source.IndexOf(
                end,
                startIndex + start.Length,
                StringComparison.Ordinal);
            Assert.That(endIndex, Is.GreaterThan(startIndex), $"Missing marker: {end}");
            return source.Substring(startIndex, endIndex - startIndex);
        }
    }
}
