using System;
using System.IO;
using System.Reflection;
using System.Text.RegularExpressions;
using FidgetingApp.Product;
using NUnit.Framework;
using UnityEngine;

namespace FidgetingApp.Tests.Editor
{
    /// <summary>
    /// Source-level release gates for the native-to-Unity transaction and
    /// reveal orchestration. These tests intentionally inspect the shipping
    /// coordinator: the private camera lease and native callback ordering
    /// cannot be exercised deterministically from an EditMode test assembly.
    /// PlayMode and XCUITest still own the actual two-frame camera proof.
    /// </summary>
    public sealed class GachaCoordinatorBuild42ContractTests
    {
        private const string CoordinatorPath =
            "Scripts/Product/FidgetAppCoordinator.cs";
        private const string RevealSessionPath =
            "Scripts/Product/Gacha/GachaRevealSession.cs";
        private const string InternalLaunchArgumentsSwiftPath =
            "Plugins/iOS/GachaInternalLaunchArguments.swift";

        [Test]
        public void PublicNativeEntrypointsExposeTheRecoverableTransactionChain()
        {
            Type coordinator = typeof(FidgetAppCoordinator);
            AssertPublicStringEntrypoint(coordinator, "RequestGachaStateFromNativeUi");
            AssertPublicStringEntrypoint(coordinator, "DrawGachaFromNativeUi");
            AssertPublicStringEntrypoint(coordinator, "QueryGachaTransactionFromNativeUi");
            AssertPublicStringEntrypoint(coordinator, "RequestGachaRevealFromNativeUi");
            AssertPublicStringEntrypoint(coordinator, "StartGachaRevealFromNativeUi");
            AssertPublicStringEntrypoint(coordinator, "AcknowledgeGachaRevealFromNativeUi");
        }

        [Test]
        public void InternalUnlimitedFactoryIsCompileTimeGatedWithProductionFallback()
        {
            string source = ReadAsset(CoordinatorPath);
            string factory = Slice(
                source,
                "private static Gacha.GachaInventoryRuntime CreateGachaInventoryRuntime()",
                "private void PublishGachaState(string receiptPayload");

            AssertOrdered(
                factory,
                "#if FIDGET_GACHA_INTERNAL_UNLIMITED",
                "Gacha.GachaInternalUnlimitedRuntimeFactory.Create(",
                "System.Environment.GetCommandLineArgs()",
                "#else",
                "new Gacha.GachaInventoryRuntime(",
                "Gacha.GachaRuntimeMode.Production",
                "#endif");
            Assert.That(
                CountOccurrences(source, "GachaInternalUnlimitedRuntimeFactory.Create("),
                Is.EqualTo(1),
                "The internal factory must have one auditable compile-time entrypoint.");
        }

        [Test]
        public void DrawPayloadRequiresFourFieldsAndUsesRequestIdAsIdempotencyKey()
        {
            string source = ReadAsset(CoordinatorPath);
            string draw = Slice(
                source,
                "public void DrawGachaFromNativeUi(string payload)",
                "public void QueryGachaTransactionFromNativeUi(string requestId)");
            string compact = Compact(draw);

            StringAssert.Contains("(payload ?? string.Empty).Split('|')", compact);
            StringAssert.Contains("parts.Length != 4", compact);
            StringAssert.Contains("parts.Length >= 4 ? parts[3] : string.Empty", compact);
            StringAssert.Contains(
                "(parts[2] != \"ticket\" && parts[2] != \"coin\")",
                compact);
            StringAssert.Contains(
                "GachaInventory.PrepareDraw( parts[0], count, method, parts[3])",
                compact);
            StringAssert.DoesNotContain("GachaInventory.Draw(", compact);
            AssertOrdered(
                draw,
                "PrepareDraw(",
                "PublishGachaState(result, isDirectDrawResponse: true)");
        }

        [Test]
        public void LostResponseHookIsInternalOnlyAndQueriesTheOriginalTransaction()
        {
            string source = ReadAsset(CoordinatorPath);
            string publish = Slice(
                source,
                "private void PublishGachaState(\n            Gacha.GachaTransactionResult result,",
                "public void RequestGachaStateFromNativeUi(string unused)");

            AssertOrdered(
                publish,
                "#if FIDGET_GACHA_INTERNAL_UNLIMITED",
                "isDirectDrawResponse && ShouldDropNextInternalGachaDrawResponse()",
                "#endif",
                "PublishGachaState(Gacha.GachaNativeBridge.ReceiptPayload(result))");
            StringAssert.Contains("--fidget-gacha-drop-next-response", publish);
            StringAssert.Contains("draw", publish);

            AssertOrdered(
                publish,
                "#if FIDGET_GACHA_INTERNAL_UNLIMITED",
                "#if UNITY_IOS && !UNITY_EDITOR",
                "CodexProcessHasLaunchArgumentValue",
                "dropNextInternalGachaDrawResponse = armed",
                "dropNextInternalGachaDrawResponse = false");

            string nativeSource = ReadAsset(InternalLaunchArgumentsSwiftPath);
            StringAssert.Contains(
                "@_cdecl(\"CodexProcessHasLaunchArgumentValue\")",
                nativeSource);
            StringAssert.Contains(
                "ProcessInfo.processInfo.arguments",
                nativeSource,
                "XCUIApplication arguments must be read from NSProcessInfo on iOS.");
            StringAssert.Contains(
                "let joined = \"\\(name)=\\(value)\"",
                nativeSource,
                "The native bridge must accept name=value launch arguments.");
            StringAssert.Contains(
                "arguments[index] == name",
                nativeSource,
                "The native bridge must also accept name value argument pairs.");
        }

        [Test]
        public void LibraryAndGachaPresentationsCannotStealEachOthersCameraLease()
        {
            string source = ReadAsset(CoordinatorPath);
            string libraryPresent = Slice(
                source,
                "private bool TryPresentDisplayCaseExperience(",
                "private void DismissDisplayCaseExperience()");
            string libraryDismiss = Slice(
                source,
                "private void DismissDisplayCaseExperience()",
                "public void SetEnvironmentThemeFromNativeUi(string themeId)");
            string gachaSetup = Slice(
                source,
                "public void RequestGachaRevealFromNativeUi(string requestId)",
                "private IEnumerator ConfirmGachaRevealPresentationAfterTwoFrames(");

            StringAssert.Contains(
                "DisplayCasePresentationOwner.GachaReveal",
                libraryPresent);
            AssertOrdered(
                libraryDismiss,
                "DisplayCasePresentationOwner.GachaReveal",
                "return;",
                "displayCaseCameraLease?.Restore()");
            StringAssert.Contains("displayCasePresentationGate.HasPendingRequest", gachaSetup);
            AssertOrdered(
                gachaSetup,
                "DisplayCasePresentationOwner.GachaReveal",
                "PremiumDisplayCaseCameraLease.Acquire(camera)");
        }

        [Test]
        public void SetupAcknowledgementWaitsForTwoEndOfFrameCameraChecks()
        {
            string source = ReadAsset(CoordinatorPath);
            string request = Slice(
                source,
                "public void RequestGachaRevealFromNativeUi(string requestId)",
                "private IEnumerator ConfirmGachaRevealPresentationAfterTwoFrames(");
            string confirmation = Slice(
                source,
                "private IEnumerator ConfirmGachaRevealPresentationAfterTwoFrames(",
                "public void StartGachaRevealFromNativeUi(string requestId)");

            StringAssert.Contains(
                "ConfirmGachaRevealPresentationAfterTwoFrames(requestId)",
                request);
            StringAssert.Contains(
                "activeGachaRevealDirector.Prepare(\n                        revealRow.Outcome,\n                        revealRow.FirstObtainedAtUtc)",
                request);
            StringAssert.DoesNotContain(".StartReveal()", request);
            Assert.That(
                CountOccurrences(
                    confirmation,
                    "yield return new WaitForEndOfFrame();"),
                Is.EqualTo(2),
                "Native setup ACK requires two complete camera-author frames.");
            Assert.That(
                confirmation.LastIndexOf(
                    "yield return new WaitForEndOfFrame();",
                    StringComparison.Ordinal),
                Is.LessThan(confirmation.IndexOf(
                    "activeGachaRevealDirector.ActivePrize.IsChildOf(",
                    StringComparison.Ordinal)),
                "Both frame boundaries must precede hierarchy/camera validation.");
            AssertOrdered(
                confirmation,
                "yield return new WaitForEndOfFrame();",
                "activeGachaRevealDirector.ActivePrize.IsChildOf(",
                "displayCaseCameraLease.IsPresentationStable(",
                "gachaRevealSetupAcknowledged = true;",
                "Gacha.GachaPresentationNativeBridge.PublishSetup(requestId, true)");
        }

        [Test]
        public void RevealCompletionPrecedesAwaitingAcceptanceAndNativeStatePublish()
        {
            string coordinator = ReadAsset(CoordinatorPath);
            string sessionSource = ReadAsset(RevealSessionPath);
            string advance = Slice(
                sessionSource,
                "public void Advance(float unscaledDeltaTime)",
                "public void Dismiss()");
            string completion = Slice(
                coordinator,
                "private void HandleGachaRevealCompleted()",
                "public void AcknowledgeGachaRevealFromNativeUi(string requestId)");

            AssertOrdered(
                advance,
                "while (Phase < target)",
                "SetPhase((GachaRevealPhase)((int)Phase + 1))",
                "target == GachaRevealPhase.Complete",
                "revealCompleted?.Invoke()");
            AssertOrdered(
                completion,
                "MarkRevealAwaitingAcceptance(requestId)",
                "PublishGachaState(result)");
            StringAssert.DoesNotContain("AcknowledgePending(", completion);
        }

        [Test]
        public void AcceptanceCommitsBeforePresentationDismissalAndCommittedStatePublish()
        {
            string source = ReadAsset(CoordinatorPath);
            string acknowledge = Slice(
                source,
                "public void AcknowledgeGachaRevealFromNativeUi(string requestId)",
                "private void DismissGachaRevealPresentation(");

            AssertOrdered(
                acknowledge,
                "GachaInventory.AcknowledgePending(requestId)",
                "if (result.Success)",
                "if (string.Equals(",
                "activeGachaRevealRequestId",
                "requestId",
                "System.StringComparison.Ordinal",
                "DismissGachaRevealPresentation(",
                "PublishGachaState(result)");
            StringAssert.DoesNotContain("PrepareDraw(", acknowledge);
        }

        [Test]
        public void SceneAndLifetimeCleanupDismissVisualsWithoutMutatingPendingTransaction()
        {
            string source = ReadAsset(CoordinatorPath);
            string configureScene = Slice(
                source,
                "private void ConfigureProductScene(string scenePath)",
                "private static void HandleRotorSemanticEvent(");
            string destroy = Slice(
                source,
                "private void OnDestroy()",
                "private void HandleSceneLoaded(Scene scene, LoadSceneMode mode)");
            string dismiss = Slice(
                source,
                "private void DismissGachaRevealPresentation(",
                "public void RedeemGachaShardsFromNativeUi(string prizeId)");

            StringAssert.Contains(
                "DismissGachaRevealPresentation(\"scene-changed\")",
                configureScene);
            StringAssert.Contains(
                "DismissGachaRevealPresentation(\"coordinator-destroyed\")",
                destroy);
            AssertOrdered(
                dismiss,
                "string interruptedRequestId = activeGachaRevealRequestId",
                "!string.IsNullOrEmpty(interruptionReason)",
                "if (gachaRevealSetupAcknowledged)",
                "Gacha.GachaPresentationNativeBridge.PublishPhase(",
                "else",
                "Gacha.GachaPresentationNativeBridge.PublishSetup(");
            AssertPendingTransactionIsUntouched(configureScene);
            AssertPendingTransactionIsUntouched(destroy);
            AssertPendingTransactionIsUntouched(dismiss);
        }

        [Test]
        public void SceneAndSelectionTeardownPublishARecoverableNativeAbort()
        {
            string source = ReadAsset(CoordinatorPath);
            StringAssert.Contains(
                "DismissGachaRevealPresentation(\"scene-changed\")",
                source);
            StringAssert.Contains(
                "DismissGachaRevealPresentation(\"model-selection-changed\")",
                source);
            string dismiss = Slice(
                source,
                "private void DismissGachaRevealPresentation(",
                "public void RedeemGachaShardsFromNativeUi(string prizeId)");
            StringAssert.Contains("PublishPhase(", dismiss);
            StringAssert.Contains("PublishSetup(", dismiss);
            StringAssert.Contains("interruptionReason", dismiss);
            AssertPendingTransactionIsUntouched(dismiss);
        }

        [Test]
        public void GachaRevealPathHasNoDirectHapticEmission()
        {
            string[] gachaSources = Directory.GetFiles(
                Path.Combine(Application.dataPath, "Scripts/Product/Gacha"),
                "*.cs",
                SearchOption.TopDirectoryOnly);
            Assert.That(gachaSources, Is.Not.Empty);
            foreach (string path in gachaSources)
            {
                string source = File.ReadAllText(path);
                StringAssert.DoesNotContain("IosHaptics", source, path);
                StringAssert.DoesNotContain("FidgetHapticRouter", source, path);
            }

            string coordinator = ReadAsset(CoordinatorPath);
            string revealRegion = Slice(
                coordinator,
                "public void RequestGachaRevealFromNativeUi(string requestId)",
                "public void RedeemGachaShardsFromNativeUi(string prizeId)");
            StringAssert.DoesNotContain("IosHaptics.", revealRegion);
            StringAssert.DoesNotContain("FidgetHapticRouter.Emit", revealRegion);
            StringAssert.DoesNotContain("PlaySystemPreset", revealRegion);
        }

        private static void AssertPublicStringEntrypoint(Type type, string name)
        {
            MethodInfo method = type.GetMethod(
                name,
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.DeclaredOnly,
                null,
                new[] { typeof(string) },
                null);
            Assert.That(method, Is.Not.Null, $"Missing native entrypoint {name}(string).");
            Assert.That(method.ReturnType, Is.EqualTo(typeof(void)), name);
        }

        private static void AssertPendingTransactionIsUntouched(string source)
        {
            StringAssert.DoesNotContain("PrepareDraw(", source);
            StringAssert.DoesNotContain("MarkRevealAwaitingAcceptance(", source);
            StringAssert.DoesNotContain("AcknowledgePending(", source);
            StringAssert.DoesNotContain("DeleteAllForTests(", source);
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
            int endIndex = source.IndexOf(end, startIndex + start.Length, StringComparison.Ordinal);
            Assert.That(endIndex, Is.GreaterThan(startIndex), $"Missing marker: {end}");
            return source.Substring(startIndex, endIndex - startIndex);
        }

        private static string Compact(string source)
        {
            return Regex.Replace(source, @"\s+", " ").Trim();
        }

        private static int CountOccurrences(string source, string token)
        {
            int count = 0;
            int offset = 0;
            while ((offset = source.IndexOf(token, offset, StringComparison.Ordinal)) >= 0)
            {
                count++;
                offset += token.Length;
            }
            return count;
        }

        private static void AssertOrdered(string source, params string[] tokens)
        {
            int offset = 0;
            foreach (string token in tokens)
            {
                int index = source.IndexOf(token, offset, StringComparison.Ordinal);
                Assert.That(index, Is.GreaterThanOrEqualTo(0),
                    $"Expected token after offset {offset}: {token}");
                offset = index + token.Length;
            }
        }
    }
}
