using System.IO;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    public sealed class GachaStorefrontIntegrationTests
    {
        [Test]
        public void Build42StorefrontUsesRecoverableUnlimitedDrawAndUnity3dReveal()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string legacy = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string overlay = ReadAsset("Plugins/iOS/CodexSwiftUIOverlay.swift");
            string pack = ReadAsset("Plugins/iOS/FidgetGachaPackPresentation.swift");
            string pipeline = ReadAsset("Editor/IosBuildPipeline.cs");

            StringAssert.Contains("public struct GachaStoreView", storefront);
            StringAssert.Contains("@Environment(\\.dismiss) private var dismiss", storefront);
            StringAssert.Contains("Button(\"返回主页\")", storefront);
            StringAssert.Contains("model.draw(seriesId: series.id, count: 1, useCoins: false)", storefront);
            StringAssert.Contains(".interactiveDismissDisabled(", storefront);
            StringAssert.Contains("GachaRuntimeMode", legacy);
            StringAssert.Contains("case internalUnlimited", legacy);
            StringAssert.Contains("GachaPendingTransaction", legacy);
            StringAssert.Contains("seriesId)|1|ticket|\\(requestId)", legacy);
            StringAssert.Contains("QueryGachaTransactionFromNativeUi", legacy);
            StringAssert.Contains("AcknowledgeGachaRevealFromNativeUi", legacy);
            StringAssert.Contains("CodexGachaRevealReceiveSetup", legacy);
            StringAssert.Contains("CodexGachaRevealReceivePhase", legacy);
            StringAssert.Contains("Task.sleep(nanoseconds: 8_000_000_000)", legacy);
            StringAssert.Contains("scheduleRevealWatchdog", legacy);
            StringAssert.Contains("acceptedRequestIds", legacy);
            StringAssert.Contains("reveal-setup-timeout", legacy);
            StringAssert.Contains("reveal-start-timeout", legacy);
            StringAssert.Contains("reveal-complete-timeout", legacy);
            StringAssert.DoesNotContain("count: 10", storefront);
            StringAssert.DoesNotContain("GachaCoinShopView", storefront);
            StringAssert.DoesNotContain("StoreKit", storefront);
            StringAssert.DoesNotContain("可购买商品", storefront);
            StringAssert.Contains(".scaledToFill()", storefront);
            StringAssert.Contains(".clipped()", storefront);
            StringAssert.Contains("GachaThreeDRevealOverlay", storefront);
            StringAssert.Contains("GachaPackOpeningOverlay", storefront);
            StringAssert.Contains("GachaPackVisual", storefront);
            StringAssert.Contains("GachaPackOpeningRules.shouldCommit", storefront);
            StringAssert.Contains("model.commitPackOpening(requestId: transaction.requestId)", storefront);
            StringAssert.Contains("gacha-pack-tear-target", storefront);
            StringAssert.Contains("gacha-pack-entry", storefront);
            StringAssert.Contains("gacha-pack-state", storefront);
            StringAssert.Contains("gacha-pack-progress", storefront);
            StringAssert.Contains("gacha-pack-request-id", storefront);
            StringAssert.Contains("GachaTransparentPresentationBackground", storefront);
            StringAssert.DoesNotContain("GachaSingleDrawReveal", storefront);
            StringAssert.DoesNotContain("GachaCaseRevealVisual", storefront);
            StringAssert.DoesNotContain("GachaShippingRevealContinuation", storefront);
            StringAssert.DoesNotContain("presentPremiumDisplayCase", storefront);
            StringAssert.DoesNotContain("private func play() async", storefront);
            StringAssert.Contains("Button(\"收下\")", storefront);
            StringAssert.Contains("model.acknowledgeReveal()", storefront);
            StringAssert.Contains("gacha-store-root", storefront);
            StringAssert.Contains("gacha-runtime-mode", storefront);
            StringAssert.Contains("gacha-ticket-balance", storefront);
            StringAssert.Contains("gacha-request-status", storefront);
            StringAssert.Contains("gacha-active-request-id", storefront);
            StringAssert.Contains("gacha-pending-prize-id", storefront);
            StringAssert.Contains("gacha-owned-count", storefront);
            StringAssert.Contains("gacha-total-draws", storefront);
            StringAssert.Contains("gacha-3d-reveal-root", storefront);
            StringAssert.Contains("gacha-reveal-phase", storefront);
            StringAssert.Contains("gacha-reveal-phase-history", storefront);
            StringAssert.Contains("gacha-error", storefront);
            StringAssert.Contains("gacha-reveal-accept", storefront);

            StringAssert.Contains("case \"canyon-lode\": return .standard", pack);
            StringAssert.Contains("default: return .standard", pack);
            StringAssert.Contains("tearTravelPoints: Double = 220", pack);
            StringAssert.Contains("tearCommitProgress: Double = 0.62", pack);
            StringAssert.DoesNotContain("GachaRarityTier", pack);
            StringAssert.Contains("GachaPackAssetRootPath", pipeline);
            StringAssert.Contains(
                "Path.Combine(projectRoot, GachaPackAssetRootPath)",
                pipeline);

            StringAssert.Contains("struct LegacyGachaStoreView", legacy);
            StringAssert.DoesNotContain("LegacyGachaStoreView(", overlay);
            StringAssert.Contains("GachaStoreView()", overlay);
            StringAssert.Contains("gacha-store-entry", overlay);
            StringAssert.Contains("CodexSetGachaRevealNativeChromeHidden", overlay);
            StringAssert.Contains("guard state.canRequestDisplayCase else { return }", overlay);
            StringAssert.Contains(".disabled(!state.canRequestDisplayCase)", overlay);
        }

        [Test]
        public void PackGatesPreparedReceiptThenEntersOnlyTheBuild42RevealSession()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string model = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string requestSetup = Slice(
                model,
                "public func requestRevealSetupIfNeeded()",
                "public func commitPackOpening(requestId: String)");
            string commit = Slice(
                model,
                "public func commitPackOpening(requestId: String)",
                "public func startRevealIfNeeded(requestId: String)");
            string transactionIngestion = Slice(
                model,
                "private func parseTransactionPayload(",
                "public func receiveRevealSetup(");
            string setupAck = Slice(
                model,
                "public func receiveRevealSetup(",
                "public func receiveRevealPhase(");

            StringAssert.Contains(
                "transaction.phase == .awaitingAcceptance",
                requestSetup);
            StringAssert.Contains(
                "transaction.phase == .prepared",
                requestSetup);
            StringAssert.Contains(
                "packOpenedRequestId == transaction.requestId",
                requestSetup);
            StringAssert.Contains(
                "revealSetupRequestedId != transaction.requestId",
                requestSetup);
            Assert.That(
                CountOccurrences(requestSetup, "RequestGachaRevealFromNativeUi"),
                Is.EqualTo(1));

            StringAssert.Contains("packOpenedRequestId != requestId", commit);
            StringAssert.Contains("transaction.phase == .prepared", commit);
            StringAssert.Contains("requestRevealSetupIfNeeded()", commit);
            StringAssert.DoesNotContain("DrawGachaFromNativeUi", commit);
            StringAssert.DoesNotContain("AcknowledgeGachaRevealFromNativeUi", commit);

            StringAssert.Contains("if phase == .prepared", transactionIngestion);
            StringAssert.Contains("packGateRequestId = requestId", transactionIngestion);
            StringAssert.Contains("pack-awaiting-open", transactionIngestion);
            StringAssert.Contains("case .awaitingAcceptance:", transactionIngestion);
            StringAssert.Contains("packGateRequestId = \"\"", transactionIngestion);
            StringAssert.Contains("packGateRequestId = \"\"", setupAck);
            StringAssert.Contains("revealIsPresented = true", setupAck);

            StringAssert.Contains("release-rebound", storefront);
            StringAssert.Contains("rebound-complete", storefront);
            StringAssert.Contains("release-commit", storefront);
            StringAssert.Contains("unity-reveal-request", storefront);
            StringAssert.DoesNotContain("GachaCaseRevealVisual", storefront);
            StringAssert.DoesNotContain("GachaShippingRevealContinuation", storefront);

            string packRoot = Path.Combine(
                Application.dataPath,
                "Plugins/iOS/GachaPacks");
            string[] assets = Directory.GetFiles(
                packRoot,
                "*.png",
                SearchOption.TopDirectoryOnly);
            Assert.That(assets, Has.Length.EqualTo(12));
            foreach (string asset in assets)
            {
                byte[] bytes = File.ReadAllBytes(asset);
                Assert.That(bytes.Length, Is.GreaterThan(1_000), asset);
                Assert.That(bytes[0], Is.EqualTo(0x89), asset);
                Assert.That(bytes[1], Is.EqualTo(0x50), asset);
                Assert.That(bytes[2], Is.EqualTo(0x4E), asset);
                Assert.That(bytes[3], Is.EqualTo(0x47), asset);
            }
        }

        [Test]
        public void ClaimLeavesRevealBeforeBridgeAckAndCanRestoreSamePendingReward()
        {
            string model = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string acknowledge = Slice(
                model,
                "public func acknowledgeReveal()",
                "public func redeem(prizeId: String)");
            string transactionIngestion = Slice(
                model,
                "private func parseTransactionPayload(",
                "public func receiveRevealSetup(");
            string acknowledgementRecovery = Slice(
                model,
                "private func scheduleAcknowledgementRecovery(requestId: String)",
                "private func scheduleRevealWatchdog(requestId: String, stage: String)");

            int localDismiss = acknowledge.IndexOf(
                "revealIsPresented = false",
                System.StringComparison.Ordinal);
            int bridgeAck = acknowledge.IndexOf(
                "AcknowledgeGachaRevealFromNativeUi",
                System.StringComparison.Ordinal);
            Assert.That(localDismiss, Is.GreaterThanOrEqualTo(0));
            Assert.That(bridgeAck, Is.GreaterThan(localDismiss));
            StringAssert.Contains(
                "CodexSetGachaRevealNativeChromeHidden(false)",
                acknowledge);
            StringAssert.Contains(
                "scheduleAcknowledgementRecovery(requestId: transaction.requestId)",
                acknowledge);

            StringAssert.Contains(
                "let wasAcknowledgingHiddenReveal = transactionPhase == .acknowledging",
                transactionIngestion);
            StringAssert.Contains("revealIsPresented = true", transactionIngestion);
            StringAssert.Contains("revealPhase = .complete", transactionIngestion);
            StringAssert.Contains(
                "lastFailureReason = \"acceptance-response-timeout\"",
                transactionIngestion);
            StringAssert.Contains(
                "CodexSetGachaRevealNativeChromeHidden(true)",
                transactionIngestion);

            StringAssert.Contains(
                "Task.sleep(nanoseconds: 1_000_000_000)",
                acknowledgementRecovery);
            StringAssert.Contains(
                "QueryGachaTransactionFromNativeUi",
                acknowledgementRecovery);
            StringAssert.Contains(
                "self.transactionPhase == .acknowledging",
                acknowledgementRecovery);
            StringAssert.Contains(
                "!self.revealIsPresented",
                acknowledgementRecovery);
        }

        [Test]
        public void AccessibilityRootsUseDedicatedMarkersWithoutOverwritingChildren()
        {
            string storefront = ReadAsset("Plugins/iOS/FidgetGachaStorefront.swift");
            string model = ReadAsset("Plugins/iOS/FidgetGachaStore.swift");
            string stateMarkers = Slice(
                storefront,
                "private struct GachaAccessibilityStateMarkers: View",
                "private struct GachaTransparentPresentationBackground");
            string revealOverlay = Slice(
                storefront,
                "private struct GachaThreeDRevealOverlay: View",
                "private struct GachaAccessibilityStateMarkers: View");

            StringAssert.Contains("Text(\"3d-reveal-root\")", revealOverlay);
            StringAssert.Contains(".accessibilityIdentifier(identifier)", stateMarkers);
            StringAssert.Contains("value: model.ticketBalanceText", stateMarkers);
            StringAssert.Contains("identifier: \"gacha-reveal-phase-history\"", stateMarkers);
            StringAssert.Contains("model.revealPhaseHistory", stateMarkers);
            StringAssert.Contains(".joined(separator: \"|\")", stateMarkers);
            StringAssert.Contains(
                "@Published public private(set) var revealPhaseHistory: [GachaRevealPhase] = []",
                model);
            StringAssert.Contains("beginRevealPhaseHistory(requestId: transaction.requestId)", model);
            StringAssert.Contains("ensureRevealPhaseHistory(requestId: requestId)", model);
            StringAssert.Contains("recordRevealPhase(phase, requestId: requestId)", model);
            StringAssert.Contains("if revealPhaseHistory.last != phase", model);
            StringAssert.Contains("revealPhaseHistory.append(phase)", model);
            StringAssert.Contains("revealPhaseHistoryRequestId = \"\"", model);
            Assert.That(
                CountOccurrences(stateMarkers, "identifier: \"gacha-store-root\""),
                Is.EqualTo(1));
            Assert.That(
                CountOccurrences(stateMarkers, "identifier: \"gacha-ticket-balance\""),
                Is.EqualTo(1));
            Assert.That(
                CountOccurrences(
                    stateMarkers,
                    "identifier: \"gacha-reveal-phase-history\""),
                Is.EqualTo(1));
            Assert.That(
                CountOccurrences(revealOverlay, "accessibilityIdentifier(\"gacha-3d-reveal-root\")"),
                Is.EqualTo(1));
            Assert.That(CountOccurrences(storefront, "gacha-store-root"), Is.EqualTo(1));
            Assert.That(CountOccurrences(storefront, "gacha-ticket-balance"), Is.EqualTo(1));
            Assert.That(
                CountOccurrences(storefront, "gacha-reveal-phase-history"),
                Is.EqualTo(1));
            Assert.That(CountOccurrences(storefront, "gacha-3d-reveal-root"), Is.EqualTo(1));
        }

        private static string ReadAsset(string relativePath)
        {
            string path = Path.Combine(Application.dataPath, relativePath);
            Assert.That(File.Exists(path), Is.True, $"Missing shipping source: {path}");
            return File.ReadAllText(path);
        }

        private static int CountOccurrences(string source, string token)
        {
            int count = 0;
            int offset = 0;
            while ((offset = source.IndexOf(token, offset, System.StringComparison.Ordinal)) >= 0)
            {
                count++;
                offset += token.Length;
            }
            return count;
        }

        private static string Slice(string source, string start, string end)
        {
            int startIndex = source.IndexOf(start, System.StringComparison.Ordinal);
            Assert.That(startIndex, Is.GreaterThanOrEqualTo(0), $"Missing marker: {start}");
            int endIndex = source.IndexOf(
                end,
                startIndex + start.Length,
                System.StringComparison.Ordinal);
            Assert.That(endIndex, Is.GreaterThan(startIndex), $"Missing marker: {end}");
            return source.Substring(startIndex, endIndex - startIndex);
        }
    }
}
