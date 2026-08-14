using System;
using System.IO;
using NUnit.Framework;

namespace FidgetingApp.DisplayCase.Tests
{
    public sealed class DisplayCasePresentationProtocolTests
    {
        [Test]
        public void SelectionPayload_RoundTripsModelAndEpoch()
        {
            var expected = new DisplayCaseModelSelection(
                "gold-four-wing",
                42);

            Assert.That(
                DisplayCaseModelSelection.TryParse(
                    expected.Encode(),
                    99,
                    out DisplayCaseModelSelection actual),
                Is.True);
            Assert.That(actual.ModelId, Is.EqualTo(expected.ModelId));
            Assert.That(actual.Epoch, Is.EqualTo(expected.Epoch));
        }

        [Test]
        public void PresentationPayload_RejectsMissingEpochOrRequestId()
        {
            Assert.That(
                DisplayCasePresentationRequest.TryParse(
                    "gold-four-wing",
                    out _),
                Is.False);
            Assert.That(
                DisplayCasePresentationRequest.TryParse(
                    "gold-four-wing|7|0",
                    out _),
                Is.False);
            Assert.That(
                DisplayCasePresentationRequest.TryParse(
                    "gold-four-wing|0|7",
                    out _),
                Is.False);
        }

        [Test]
        public void Gate_WaitsDuringLoadThenRequiresExactSceneAndCanonicalModel()
        {
            var request = new DisplayCasePresentationRequest(
                "gold-four-wing",
                12,
                3001);
            var gate = new DisplayCasePresentationGate();

            Assert.That(gate.Begin(request, out _), Is.True);
            Assert.That(
                gate.Evaluate(new DisplayCaseReadinessSnapshot(
                    "gold-four-wing",
                    12,
                    "metal-three-blade",
                    "metal-three-blade",
                    true)).Disposition,
                Is.EqualTo(DisplayCaseRequestDisposition.WaitingForScene));

            DisplayCaseRequestEvaluation wrongCanonical = gate.Evaluate(
                new DisplayCaseReadinessSnapshot(
                    "gold-four-wing",
                    12,
                    "gold-four-wing",
                    "metal-three-blade",
                    false));
            Assert.That(
                wrongCanonical.Disposition,
                Is.EqualTo(DisplayCaseRequestDisposition.Rejected));
            Assert.That(wrongCanonical.Reason, Is.EqualTo("canonical-prize-mismatch"));

            Assert.That(
                gate.Evaluate(new DisplayCaseReadinessSnapshot(
                    "gold-four-wing",
                    12,
                    "gold-four-wing",
                    "gold-four-wing",
                    false)).Disposition,
                Is.EqualTo(DisplayCaseRequestDisposition.ReadyToPresent));
        }

        [Test]
        public void Gate_RejectsLateRequestFromOlderSelectionEpoch()
        {
            var gate = new DisplayCasePresentationGate();
            gate.Begin(
                new DisplayCasePresentationRequest(
                    "metal-three-blade",
                    8,
                    3002),
                out _);

            DisplayCaseRequestEvaluation evaluation = gate.Evaluate(
                new DisplayCaseReadinessSnapshot(
                    "metal-three-blade",
                    9,
                    "metal-three-blade",
                    "metal-three-blade",
                    false));

            Assert.That(
                evaluation.Disposition,
                Is.EqualTo(DisplayCaseRequestDisposition.Rejected));
            Assert.That(evaluation.Reason, Is.EqualTo("selection-mismatch"));
        }

        [Test]
        public void Gate_SupersedesOldRequestAndOnlyMatchingCompletionCanClearNewOne()
        {
            var gate = new DisplayCasePresentationGate();
            var first = new DisplayCasePresentationRequest(
                "metal-three-blade",
                4,
                91);
            var second = new DisplayCasePresentationRequest(
                "metal-three-blade",
                4,
                92);
            gate.Begin(first, out _);

            Assert.That(gate.Begin(second, out DisplayCasePresentationRequest superseded),
                Is.True);
            Assert.That(superseded.RequestId, Is.EqualTo(first.RequestId));
            Assert.That(gate.Complete(first.RequestId), Is.False);
            Assert.That(gate.HasPendingRequest, Is.True);
            Assert.That(gate.Complete(second.RequestId), Is.True);
            Assert.That(gate.HasPendingRequest, Is.False);
        }

        [Test]
        public void Readiness_IsFalseUntilAllFourIdentitiesMatch()
        {
            Assert.That(new DisplayCaseReadinessSnapshot(
                "magnetic-fan-card",
                6,
                "magnetic-fan-card",
                "magnetic-fan-card",
                false).IsExactModelReady, Is.True);
            Assert.That(new DisplayCaseReadinessSnapshot(
                "magnetic-fan-card",
                6,
                "magnetic-fan-card",
                "magnetic-slide-tile",
                false).IsExactModelReady, Is.False);
            Assert.That(new DisplayCaseReadinessSnapshot(
                "magnetic-fan-card",
                6,
                "magnetic-fan-card",
                "magnetic-fan-card",
                true).IsExactModelReady, Is.False);
        }

        [Test]
        public void StartGate_RequiresExactVersionedIdentityAndStartsOnlyOnce()
        {
            var request = new DisplayCasePresentationRequest(
                "magnetic-fan-card",
                18,
                7004);
            var gate = new DisplayCasePresentationStartGate();

            Assert.That(gate.Arm(request), Is.True);
            Assert.That(gate.IsArmed, Is.True);
            Assert.That(gate.HasStarted, Is.False);
            Assert.That(
                gate.Evaluate(request).Disposition,
                Is.EqualTo(DisplayCasePresentationStartDisposition.ReadyToStart));

            Assert.That(
                gate.Evaluate(new DisplayCasePresentationRequest(
                    "magnetic-slide-tile",
                    18,
                    7004)).Reason,
                Is.EqualTo("stale-start-request"));
            Assert.That(
                gate.Evaluate(new DisplayCasePresentationRequest(
                    "magnetic-fan-card",
                    17,
                    7004)).Reason,
                Is.EqualTo("stale-start-request"));
            Assert.That(
                gate.Evaluate(new DisplayCasePresentationRequest(
                    "magnetic-fan-card",
                    18,
                    7003)).Reason,
                Is.EqualTo("stale-start-request"));

            Assert.That(gate.MarkStarted(request), Is.True);
            Assert.That(gate.HasStarted, Is.True);
            Assert.That(gate.Arm(request), Is.True,
                "A duplicate setup ACK for the same identity is idempotent.");
            Assert.That(gate.HasStarted, Is.True,
                "Re-arming the same identity must not make its entrance replayable.");
            Assert.That(gate.Arm(new DisplayCasePresentationRequest(
                "magnetic-fan-card",
                18,
                7005)), Is.False,
                "An armed presentation cannot be replaced without dismissal.");
            Assert.That(
                gate.Evaluate(request).Disposition,
                Is.EqualTo(DisplayCasePresentationStartDisposition.AlreadyStarted));
            Assert.That(gate.MarkStarted(request), Is.False,
                "A repeated SwiftUI onAppear must never replay the entrance.");

            gate.Reset();
            Assert.That(gate.IsArmed, Is.False);
            Assert.That(
                gate.Evaluate(request).Reason,
                Is.EqualTo("presentation-not-armed"));
        }

        [Test]
        public void NativeShell_WaitsForExactUnityAckBeforeInstallingOverlay()
        {
            string swift = File.ReadAllText(
                "Assets/Plugins/iOS/CodexSwiftUIOverlay.swift");
            string coordinator = File.ReadAllText(
                "Assets/Scripts/Product/FidgetAppCoordinator.cs");

            StringAssert.Contains(
                "@_cdecl(\"CodexModelReadinessReceiveState\")",
                swift);
            StringAssert.Contains(
                "@_cdecl(\"CodexDisplayCaseReceiveResult\")",
                swift);
            StringAssert.Contains(
                "@_cdecl(\"CodexDisplayCaseReceiveStartResult\")",
                swift);
            StringAssert.Contains(
                "\"RequestDisplayCaseFromNativeUi\"",
                swift);
            StringAssert.Contains(
                "\"StartDisplayCasePresentationFromNativeUi\"",
                swift);
            StringAssert.Contains(
                ".disabled(!state.canRequestDisplayCase)",
                swift);
            StringAssert.Contains(
                ".accessibilityIdentifier(\"library-model-ready\")",
                swift);
            StringAssert.Contains(
                ".accessibilityIdentifier(\"display-case-presentation-ack\")",
                swift);
            StringAssert.Contains(
                ".accessibilityIdentifier(\n" +
                "                        \"display-case-presentation-start-ack\")",
                swift);
            StringAssert.Contains(
                ".accessibilityValue(lifecycle.request.payload)",
                swift);
            StringAssert.Contains(
                ".accessibilityIdentifier(\"display-case-root\")",
                swift);
            StringAssert.Contains(
                "Text(\"root\")",
                swift);
            const string RootAccessibilityIdentifier =
                ".accessibilityIdentifier(\"display-case-root\")";
            Assert.That(
                swift.IndexOf(
                    RootAccessibilityIdentifier,
                    StringComparison.Ordinal),
                Is.EqualTo(swift.LastIndexOf(
                    RootAccessibilityIdentifier,
                    StringComparison.Ordinal)),
                "The display-case root identifier must belong to a dedicated marker; " +
                "putting it on the parent container overrides descendant AX identifiers.");
            StringAssert.Contains(
                "guard pendingDisplayCaseRequest == result else { return }",
                swift);
            StringAssert.Contains(
                "guard succeeded else { return }",
                swift);
            StringAssert.Contains(
                "activeDisplayCaseRequest == lifecycle.request",
                swift);
            StringAssert.Contains(
                "lifecycle.claimStartRequest()",
                swift);
            StringAssert.Contains(
                "public void RequestDisplayCaseFromNativeUi",
                coordinator);
            StringAssert.Contains(
                "TryResolvePendingDisplayCaseRequest();",
                coordinator);
            StringAssert.Contains(
                "activeDisplayCasePrize.transform.IsChildOf",
                coordinator);
            StringAssert.Contains(
                "displayCaseCamera != null",
                coordinator);
            StringAssert.Contains(
                "yield return new WaitForEndOfFrame();",
                coordinator);
            StringAssert.Contains(
                "displayCaseCameraLease.IsPresentationStable(",
                coordinator);
            int confirmationStart = coordinator.IndexOf(
                "private IEnumerator ConfirmDisplayCasePresentationAfterEndOfFrame(",
                StringComparison.Ordinal);
            int confirmationEnd = coordinator.IndexOf(
                "private bool IsDisplayCasePresentationComplete(",
                confirmationStart,
                StringComparison.Ordinal);
            string confirmation = coordinator.Substring(
                confirmationStart,
                confirmationEnd - confirmationStart);
            int endOfFrame = confirmation.IndexOf(
                "yield return new WaitForEndOfFrame();",
                StringComparison.Ordinal);
            int postcondition = confirmation.IndexOf(
                "IsDisplayCasePresentationComplete(",
                endOfFrame,
                StringComparison.Ordinal);
            int armStart = confirmation.IndexOf(
                "displayCasePresentationStartGate.Arm(request)",
                postcondition,
                StringComparison.Ordinal);
            int successAck = confirmation.IndexOf(
                "PublishPresentationResult(request, true);",
                postcondition,
                StringComparison.Ordinal);
            int tryPresent = coordinator.IndexOf(
                "private bool TryPresentDisplayCaseExperience(",
                StringComparison.Ordinal);
            int dismiss = coordinator.IndexOf(
                "private void DismissDisplayCaseExperience()",
                tryPresent,
                StringComparison.Ordinal);
            int assembledForValidation = coordinator.IndexOf(
                "activeDisplayCaseInteraction.SetExplodedProgress(0f);",
                tryPresent,
                StringComparison.Ordinal);
            int preparedReveal = coordinator.IndexOf(
                "activeDisplayCase.SetRevealProgressForPreview(0f);",
                tryPresent,
                StringComparison.Ordinal);
            string setup = coordinator.Substring(tryPresent, dismiss - tryPresent);
            int startMethod = coordinator.IndexOf(
                "public void StartDisplayCasePresentationFromNativeUi(",
                StringComparison.Ordinal);
            int startMethodEnd = coordinator.IndexOf(
                "public void SetDisplayCasePresentedFromNativeUi(",
                startMethod,
                StringComparison.Ordinal);
            string visibleStart = coordinator.Substring(
                startMethod,
                startMethodEnd - startMethod);
            int exactRuntimePostcondition = visibleStart.IndexOf(
                "IsDisplayCasePresentationComplete(",
                StringComparison.Ordinal);
            int explodeAfterMount = visibleStart.IndexOf(
                "activeDisplayCaseInteraction.SetExplodedProgress(1f);",
                StringComparison.Ordinal);
            int revealAfterMount = visibleStart.IndexOf(
                "activeDisplayCase.play();",
                StringComparison.Ordinal);
            int assemblyAfterMount = visibleStart.IndexOf(
                "activeDisplayCaseInteraction.PlayAssembly();",
                StringComparison.Ordinal);
            int markedStarted = visibleStart.IndexOf(
                "displayCasePresentationStartGate.MarkStarted(request)",
                StringComparison.Ordinal);
            int startAck = visibleStart.LastIndexOf(
                "DisplayCaseNativeBridge.PublishPresentationStartResult(",
                StringComparison.Ordinal);
            Assert.That(endOfFrame, Is.GreaterThanOrEqualTo(0));
            Assert.That(postcondition, Is.GreaterThan(endOfFrame));
            Assert.That(armStart, Is.GreaterThan(postcondition));
            Assert.That(successAck, Is.GreaterThan(armStart),
                "Setup ACK must arm the versioned start before Swift mounts the overlay.");
            StringAssert.DoesNotContain("activeDisplayCase.play();", confirmation,
                "The EndOfFrame setup ACK must not consume reveal time.");
            StringAssert.DoesNotContain("PlayAssembly();", confirmation,
                "The EndOfFrame setup ACK must not consume assembly time.");
            Assert.That(assembledForValidation, Is.GreaterThan(tryPresent),
                "The EndOfFrame viewport postcondition must inspect the closed, assembled case.");
            Assert.That(assembledForValidation, Is.LessThan(dismiss));
            Assert.That(preparedReveal, Is.GreaterThan(tryPresent));
            Assert.That(preparedReveal, Is.LessThan(assembledForValidation));
            StringAssert.DoesNotContain("activeDisplayCase.play();", setup,
                "TryPresent may prepare frame zero but must not start the reveal.");
            Assert.That(successAck, Is.GreaterThan(postcondition),
                "The native success ACK must follow a real EndOfFrame camera/viewport postcondition.");
            Assert.That(exactRuntimePostcondition, Is.GreaterThanOrEqualTo(0));
            Assert.That(explodeAfterMount, Is.GreaterThan(exactRuntimePostcondition));
            Assert.That(revealAfterMount, Is.GreaterThan(explodeAfterMount));
            Assert.That(assemblyAfterMount, Is.GreaterThan(revealAfterMount));
            Assert.That(markedStarted, Is.GreaterThan(assemblyAfterMount));
            Assert.That(startAck, Is.GreaterThan(markedStarted),
                "AX may expose the start marker only after both shared animations start.");
        }
    }
}
