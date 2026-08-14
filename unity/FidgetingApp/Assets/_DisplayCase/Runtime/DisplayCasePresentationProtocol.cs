using System;
using System.Globalization;
using System.Runtime.InteropServices;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// Versioned selection sent by the native shell.  The epoch belongs to the
    /// native selection, so a late Unity scene callback can never make a newer
    /// page look ready.
    /// </summary>
    public readonly struct DisplayCaseModelSelection
    {
        public DisplayCaseModelSelection(string modelId, long epoch)
        {
            ModelId = modelId ?? string.Empty;
            Epoch = epoch;
        }

        public string ModelId { get; }
        public long Epoch { get; }
        public bool IsValid => !string.IsNullOrWhiteSpace(ModelId) && Epoch > 0;

        public string Encode()
        {
            return $"{ModelId}|{Epoch.ToString(CultureInfo.InvariantCulture)}";
        }

        public static bool TryParse(
            string payload,
            long legacyEpoch,
            out DisplayCaseModelSelection selection)
        {
            string[] fields = (payload ?? string.Empty).Split('|');
            string modelId = fields.Length > 0 ? fields[0].Trim() : string.Empty;
            long epoch;
            if (fields.Length == 1)
            {
                // Keep old native clients usable, while ensuring every legacy
                // request is still assigned a positive, monotonic epoch.
                epoch = legacyEpoch;
            }
            else if (fields.Length == 2
                && long.TryParse(
                    fields[1],
                    NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out long parsedEpoch))
            {
                epoch = parsedEpoch;
            }
            else
            {
                selection = default;
                return false;
            }

            selection = new DisplayCaseModelSelection(modelId, epoch);
            return selection.IsValid;
        }
    }

    /// <summary>
    /// A display-case request is bound both to the native selection epoch and
    /// to its own request id.  Both values must round-trip in the completion.
    /// </summary>
    public readonly struct DisplayCasePresentationRequest
    {
        public DisplayCasePresentationRequest(
            string modelId,
            long selectionEpoch,
            long requestId)
        {
            ModelId = modelId ?? string.Empty;
            SelectionEpoch = selectionEpoch;
            RequestId = requestId;
        }

        public string ModelId { get; }
        public long SelectionEpoch { get; }
        public long RequestId { get; }
        public bool IsValid => !string.IsNullOrWhiteSpace(ModelId)
            && SelectionEpoch > 0
            && RequestId > 0;

        public bool HasSameIdentity(DisplayCasePresentationRequest other)
        {
            return string.Equals(ModelId, other.ModelId, StringComparison.Ordinal)
                && SelectionEpoch == other.SelectionEpoch
                && RequestId == other.RequestId;
        }

        public string Encode()
        {
            return string.Join(
                "|",
                ModelId,
                SelectionEpoch.ToString(CultureInfo.InvariantCulture),
                RequestId.ToString(CultureInfo.InvariantCulture));
        }

        public static bool TryParse(
            string payload,
            out DisplayCasePresentationRequest request)
        {
            string[] fields = (payload ?? string.Empty).Split('|');
            if (fields.Length != 3
                || !long.TryParse(
                    fields[1],
                    NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out long selectionEpoch)
                || !long.TryParse(
                    fields[2],
                    NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out long requestId))
            {
                request = default;
                return false;
            }

            request = new DisplayCasePresentationRequest(
                fields[0].Trim(),
                selectionEpoch,
                requestId);
            return request.IsValid;
        }
    }

    public enum DisplayCaseRequestDisposition
    {
        None = 0,
        WaitingForScene = 1,
        ReadyToPresent = 2,
        Rejected = 3
    }

    public readonly struct DisplayCaseRequestEvaluation
    {
        public DisplayCaseRequestEvaluation(
            DisplayCaseRequestDisposition disposition,
            string reason)
        {
            Disposition = disposition;
            Reason = reason ?? string.Empty;
        }

        public DisplayCaseRequestDisposition Disposition { get; }
        public string Reason { get; }
    }

    public readonly struct DisplayCaseReadinessSnapshot
    {
        public DisplayCaseReadinessSnapshot(
            string selectedModelId,
            long selectedModelEpoch,
            string activeSceneModelId,
            string canonicalPrizeModelId,
            bool sceneLoadInProgress)
        {
            SelectedModelId = selectedModelId ?? string.Empty;
            SelectedModelEpoch = selectedModelEpoch;
            ActiveSceneModelId = activeSceneModelId ?? string.Empty;
            CanonicalPrizeModelId = canonicalPrizeModelId ?? string.Empty;
            SceneLoadInProgress = sceneLoadInProgress;
        }

        public string SelectedModelId { get; }
        public long SelectedModelEpoch { get; }
        public string ActiveSceneModelId { get; }
        public string CanonicalPrizeModelId { get; }
        public bool SceneLoadInProgress { get; }

        public bool IsExactModelReady => !SceneLoadInProgress
            && !string.IsNullOrEmpty(SelectedModelId)
            && SelectedModelEpoch > 0
            && string.Equals(
                SelectedModelId,
                ActiveSceneModelId,
                StringComparison.Ordinal)
            && string.Equals(
                SelectedModelId,
                CanonicalPrizeModelId,
                StringComparison.Ordinal);
    }

    /// <summary>
    /// Pure deterministic gate shared by runtime code and EditMode tests.
    /// It deliberately treats a scene mismatch as "waiting" only while Unity
    /// reports an in-flight scene load; once loading stops, the mismatch is a
    /// terminal failure and the native overlay must stay hidden.
    /// </summary>
    public sealed class DisplayCasePresentationGate
    {
        private bool hasPendingRequest;
        private DisplayCasePresentationRequest pendingRequest;

        public bool HasPendingRequest => hasPendingRequest;
        public DisplayCasePresentationRequest PendingRequest => pendingRequest;

        public bool Begin(
            DisplayCasePresentationRequest request,
            out DisplayCasePresentationRequest superseded)
        {
            superseded = hasPendingRequest ? pendingRequest : default;
            if (!request.IsValid)
            {
                return false;
            }

            pendingRequest = request;
            hasPendingRequest = true;
            return true;
        }

        public DisplayCaseRequestEvaluation Evaluate(
            DisplayCaseReadinessSnapshot readiness)
        {
            if (!hasPendingRequest)
            {
                return new DisplayCaseRequestEvaluation(
                    DisplayCaseRequestDisposition.None,
                    "no-request");
            }

            if (!string.Equals(
                    pendingRequest.ModelId,
                    readiness.SelectedModelId,
                    StringComparison.Ordinal)
                || pendingRequest.SelectionEpoch != readiness.SelectedModelEpoch)
            {
                return new DisplayCaseRequestEvaluation(
                    DisplayCaseRequestDisposition.Rejected,
                    "selection-mismatch");
            }

            if (readiness.SceneLoadInProgress)
            {
                return new DisplayCaseRequestEvaluation(
                    DisplayCaseRequestDisposition.WaitingForScene,
                    "scene-loading");
            }

            if (!string.Equals(
                    pendingRequest.ModelId,
                    readiness.ActiveSceneModelId,
                    StringComparison.Ordinal))
            {
                return new DisplayCaseRequestEvaluation(
                    DisplayCaseRequestDisposition.Rejected,
                    "active-scene-mismatch");
            }

            if (!string.Equals(
                    pendingRequest.ModelId,
                    readiness.CanonicalPrizeModelId,
                    StringComparison.Ordinal))
            {
                return new DisplayCaseRequestEvaluation(
                    DisplayCaseRequestDisposition.Rejected,
                    "canonical-prize-mismatch");
            }

            return new DisplayCaseRequestEvaluation(
                DisplayCaseRequestDisposition.ReadyToPresent,
                string.Empty);
        }

        public bool Complete(long requestId)
        {
            if (!hasPendingRequest || pendingRequest.RequestId != requestId)
            {
                return false;
            }

            hasPendingRequest = false;
            pendingRequest = default;
            return true;
        }

        public void Reset()
        {
            hasPendingRequest = false;
            pendingRequest = default;
        }
    }

    public enum DisplayCasePresentationStartDisposition
    {
        Rejected = 0,
        ReadyToStart = 1,
        AlreadyStarted = 2
    }

    public readonly struct DisplayCasePresentationStartEvaluation
    {
        public DisplayCasePresentationStartEvaluation(
            DisplayCasePresentationStartDisposition disposition,
            string reason)
        {
            Disposition = disposition;
            Reason = reason ?? string.Empty;
        }

        public DisplayCasePresentationStartDisposition Disposition { get; }
        public string Reason { get; }
    }

    /// <summary>
    /// Second half of the native presentation handshake. The case is armed only
    /// after its EndOfFrame shipping postcondition succeeds. Swift then mounts
    /// the acknowledged overlay and sends the exact request identity back from
    /// onAppear. Duplicate mounted callbacks are idempotent and can re-acknowledge
    /// the same start without replaying the reveal or assembly.
    /// </summary>
    public sealed class DisplayCasePresentationStartGate
    {
        private bool armed;
        private bool started;
        private DisplayCasePresentationRequest activeRequest;

        public bool IsArmed => armed;
        public bool HasStarted => armed && started;
        public DisplayCasePresentationRequest ActiveRequest => activeRequest;

        public bool Arm(DisplayCasePresentationRequest request)
        {
            if (!request.IsValid)
            {
                return false;
            }
            if (armed)
            {
                // A duplicate setup confirmation for the exact request is
                // harmless, but it must never clear HasStarted or replace the
                // active identity. A different request requires Reset through
                // the normal dismiss path first.
                return activeRequest.HasSameIdentity(request);
            }

            activeRequest = request;
            armed = true;
            started = false;
            return true;
        }

        public DisplayCasePresentationStartEvaluation Evaluate(
            DisplayCasePresentationRequest request)
        {
            if (!request.IsValid)
            {
                return new DisplayCasePresentationStartEvaluation(
                    DisplayCasePresentationStartDisposition.Rejected,
                    "invalid-start-request");
            }
            if (!armed)
            {
                return new DisplayCasePresentationStartEvaluation(
                    DisplayCasePresentationStartDisposition.Rejected,
                    "presentation-not-armed");
            }
            if (!activeRequest.HasSameIdentity(request))
            {
                return new DisplayCasePresentationStartEvaluation(
                    DisplayCasePresentationStartDisposition.Rejected,
                    "stale-start-request");
            }

            return new DisplayCasePresentationStartEvaluation(
                started
                    ? DisplayCasePresentationStartDisposition.AlreadyStarted
                    : DisplayCasePresentationStartDisposition.ReadyToStart,
                string.Empty);
        }

        public bool MarkStarted(DisplayCasePresentationRequest request)
        {
            if (!armed || started || !activeRequest.HasSameIdentity(request))
            {
                return false;
            }

            started = true;
            return true;
        }

        public void Reset()
        {
            armed = false;
            started = false;
            activeRequest = default;
        }
    }

    public static class DisplayCaseNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexModelReadinessReceiveState(
            string modelId,
            long selectionEpoch,
            int ready);

        [DllImport("__Internal")]
        private static extern void CodexDisplayCaseReceiveResult(
            string modelId,
            long selectionEpoch,
            long requestId,
            int succeeded,
            string failureReason);

        [DllImport("__Internal")]
        private static extern void CodexDisplayCaseReceiveStartResult(
            string modelId,
            long selectionEpoch,
            long requestId,
            int succeeded,
            string failureReason);
#endif

        public static void PublishModelReadiness(
            string modelId,
            long selectionEpoch,
            bool ready)
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexModelReadinessReceiveState(
                modelId ?? string.Empty,
                selectionEpoch,
                ready ? 1 : 0);
#endif
        }

        public static void PublishPresentationResult(
            DisplayCasePresentationRequest request,
            bool succeeded,
            string failureReason = "")
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexDisplayCaseReceiveResult(
                request.ModelId,
                request.SelectionEpoch,
                request.RequestId,
                succeeded ? 1 : 0,
                succeeded ? string.Empty : failureReason ?? "unknown");
#endif
        }

        public static void PublishPresentationStartResult(
            DisplayCasePresentationRequest request,
            bool succeeded,
            string failureReason = "")
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexDisplayCaseReceiveStartResult(
                request.ModelId,
                request.SelectionEpoch,
                request.RequestId,
                succeeded ? 1 : 0,
                succeeded ? string.Empty : failureReason ?? "unknown");
#endif
        }
    }
}
