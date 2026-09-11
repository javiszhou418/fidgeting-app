using System;
#if UNITY_IOS && !UNITY_EDITOR
using System.Runtime.InteropServices;
#endif

namespace FidgetingApp.Product.Gacha
{
    public readonly struct GachaNativeHybridR029Trace
    {
        public GachaNativeHybridR029Trace(
            string checkpoint,
            string rawRequestUuid,
            string receiptUuid,
            int unityFrameCount,
            string caseRootName,
            string caseTypeName,
            string caseEntityId,
            int caseRendererCount,
            int foreignRendererCount,
            bool caseStableFrame,
            bool cameraStableFrame,
            bool setupSucceeded,
            string revealSetupFailure,
            float nativeHybridProgress,
            bool caseIsCanonical,
            bool caseIsOnlyUnityRenderable,
            bool unityClearBackdropIsolated)
        {
            Checkpoint = checkpoint ?? string.Empty;
            RawRequestUuid = rawRequestUuid ?? string.Empty;
            ReceiptUuid = receiptUuid ?? string.Empty;
            UnityFrameCount = unityFrameCount;
            CaseRootName = caseRootName ?? string.Empty;
            CaseTypeName = caseTypeName ?? string.Empty;
            CaseEntityId = caseEntityId ?? string.Empty;
            CaseRendererCount = Math.Max(0, caseRendererCount);
            ForeignRendererCount = foreignRendererCount;
            CaseStableFrame = caseStableFrame;
            CameraStableFrame = cameraStableFrame;
            SetupSucceeded = setupSucceeded;
            RevealSetupFailure = revealSetupFailure ?? string.Empty;
            NativeHybridProgress = Math.Max(0f, nativeHybridProgress);
            CaseIsCanonical = caseIsCanonical;
            CaseIsOnlyUnityRenderable = caseIsOnlyUnityRenderable;
            UnityClearBackdropIsolated = unityClearBackdropIsolated;
        }

        public string Checkpoint { get; }
        public string RawRequestUuid { get; }
        public string ReceiptUuid { get; }
        public int UnityFrameCount { get; }
        public string CaseRootName { get; }
        public string CaseTypeName { get; }
        public string CaseEntityId { get; }
        public int CaseRendererCount { get; }
        public int ForeignRendererCount { get; }
        public bool CaseStableFrame { get; }
        public bool CameraStableFrame { get; }
        public bool SetupSucceeded { get; }
        public string RevealSetupFailure { get; }
        public float NativeHybridProgress { get; }
        public bool CaseIsCanonical { get; }
        public bool CaseIsOnlyUnityRenderable { get; }
        public bool UnityClearBackdropIsolated { get; }
    }

    public readonly struct GachaNativeHybridR030Trace
    {
        public GachaNativeHybridR030Trace(
            string checkpoint,
            int stableFrameOrdinal,
            string rawRequestUuid,
            string receiptUuid,
            int unityFrameCount,
            long cameraInstanceId,
            string cameraName,
            string caseRootName,
            string caseTypeName,
            string caseEntityId,
            int caseRendererCount,
            int foreignRendererCount,
            bool caseStableFrame,
            bool cameraStableFrame,
            bool isolationActive,
            bool usesCavityClearBackdrop,
            bool publishSetupPublished,
            bool publishSetupSucceeded,
            string publishSetupFailure,
            float nativeHybridProgress,
            bool caseIsCanonical,
            bool caseIsOnlyUnityRenderable)
        {
            Checkpoint = checkpoint ?? string.Empty;
            StableFrameOrdinal = Math.Max(0, stableFrameOrdinal);
            RawRequestUuid = rawRequestUuid ?? string.Empty;
            ReceiptUuid = receiptUuid ?? string.Empty;
            UnityFrameCount = unityFrameCount;
            CameraInstanceId = cameraInstanceId;
            CameraName = cameraName ?? string.Empty;
            CaseRootName = caseRootName ?? string.Empty;
            CaseTypeName = caseTypeName ?? string.Empty;
            CaseEntityId = caseEntityId ?? string.Empty;
            CaseRendererCount = Math.Max(0, caseRendererCount);
            ForeignRendererCount = foreignRendererCount;
            CaseStableFrame = caseStableFrame;
            CameraStableFrame = cameraStableFrame;
            IsolationActive = isolationActive;
            UsesCavityClearBackdrop = usesCavityClearBackdrop;
            PublishSetupPublished = publishSetupPublished;
            PublishSetupSucceeded = publishSetupSucceeded;
            PublishSetupFailure = publishSetupFailure ?? string.Empty;
            NativeHybridProgress = Math.Max(0f, nativeHybridProgress);
            CaseIsCanonical = caseIsCanonical;
            CaseIsOnlyUnityRenderable = caseIsOnlyUnityRenderable;
        }

        public string Checkpoint { get; }
        public int StableFrameOrdinal { get; }
        public string RawRequestUuid { get; }
        public string ReceiptUuid { get; }
        public int UnityFrameCount { get; }
        public long CameraInstanceId { get; }
        public string CameraName { get; }
        public string CaseRootName { get; }
        public string CaseTypeName { get; }
        public string CaseEntityId { get; }
        public int CaseRendererCount { get; }
        public int ForeignRendererCount { get; }
        public bool CaseStableFrame { get; }
        public bool CameraStableFrame { get; }
        public bool IsolationActive { get; }
        public bool UsesCavityClearBackdrop { get; }
        public bool PublishSetupPublished { get; }
        public bool PublishSetupSucceeded { get; }
        public string PublishSetupFailure { get; }
        public float NativeHybridProgress { get; }
        public bool CaseIsCanonical { get; }
        public bool CaseIsOnlyUnityRenderable { get; }
    }

    public static class GachaPresentationNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexGachaRevealReceiveSetup(
            string requestId,
            int succeeded,
            string failureReason,
            float handoffDurationSeconds);

        [DllImport("__Internal")]
        private static extern void CodexGachaRevealReceivePhase(
            string requestId,
            string phase);

        [DllImport("__Internal")]
        private static extern void CodexGachaRevealReceiveComposition(
            string requestId,
            string caseRootName,
            string caseTypeName,
            string caseEntityId,
            int caseRendererCount,
            int caseIsCanonical,
            int caseIsOnlyUnityRenderable,
            int unityClearBackdropIsolated);

        [DllImport("__Internal")]
        private static extern void CodexGachaRevealReceiveR029Trace(
            string checkpoint,
            string rawRequestUuid,
            string receiptUuid,
            int unityFrameCount,
            string caseRootName,
            string caseTypeName,
            string caseEntityId,
            int caseRendererCount,
            int foreignRendererCount,
            int caseStableFrame,
            int cameraStableFrame,
            int setupSucceeded,
            string revealSetupFailure,
            float nativeHybridProgress,
            int caseIsCanonical,
            int caseIsOnlyUnityRenderable,
            int unityClearBackdropIsolated);

        [DllImport("__Internal")]
        private static extern void CodexGachaRevealReceiveR030Trace(
            string checkpoint,
            int stableFrameOrdinal,
            string rawRequestUuid,
            string receiptUuid,
            int unityFrameCount,
            long cameraInstanceId,
            string cameraName,
            string caseRootName,
            string caseTypeName,
            string caseEntityId,
            int caseRendererCount,
            int foreignRendererCount,
            int caseStableFrame,
            int cameraStableFrame,
            int isolationActive,
            int usesCavityClearBackdrop,
            int publishSetupPublished,
            int publishSetupSucceeded,
            string publishSetupFailure,
            float nativeHybridProgress,
            int caseIsCanonical,
            int caseIsOnlyUnityRenderable);
#endif

        public static event Action<string, bool, string, float> setupPublished;
        public static event Action<string, string> phasePublished;
        public static event Action<string, string, string, string, int, bool,
            bool, bool> compositionPublished;
        public static event Action<GachaNativeHybridR029Trace>
            r029TracePublished;
        public static event Action<GachaNativeHybridR030Trace>
            r030TracePublished;

        public static void PublishSetup(
            string requestId,
            bool succeeded,
            string failureReason = "",
            float handoffDurationSeconds = 0f)
        {
            string id = requestId ?? string.Empty;
            string reason = failureReason ?? string.Empty;
            float duration = succeeded
                ? Math.Max(0f, handoffDurationSeconds)
                : 0f;
            setupPublished?.Invoke(id, succeeded, reason, duration);
#if UNITY_IOS && !UNITY_EDITOR
            CodexGachaRevealReceiveSetup(
                id,
                succeeded ? 1 : 0,
                reason,
                duration);
#endif
        }

        public static void PublishPhase(string requestId, string phase)
        {
            string id = requestId ?? string.Empty;
            string token = phase ?? string.Empty;
            phasePublished?.Invoke(id, token);
#if UNITY_IOS && !UNITY_EDITOR
            CodexGachaRevealReceivePhase(id, token);
#endif
        }

        public static void PublishComposition(
            string requestId,
            string caseRootName,
            string caseTypeName,
            string caseEntityId,
            int caseRendererCount,
            bool caseIsCanonical,
            bool caseIsOnlyUnityRenderable,
            bool unityClearBackdropIsolated)
        {
            string id = requestId ?? string.Empty;
            string root = caseRootName ?? string.Empty;
            string type = caseTypeName ?? string.Empty;
            string entity = caseEntityId ?? string.Empty;
            int rendererCount = Math.Max(0, caseRendererCount);
            compositionPublished?.Invoke(
                id,
                root,
                type,
                entity,
                rendererCount,
                caseIsCanonical,
                caseIsOnlyUnityRenderable,
                unityClearBackdropIsolated);
#if UNITY_IOS && !UNITY_EDITOR
            CodexGachaRevealReceiveComposition(
                id,
                root,
                type,
                entity,
                rendererCount,
                caseIsCanonical ? 1 : 0,
                caseIsOnlyUnityRenderable ? 1 : 0,
                unityClearBackdropIsolated ? 1 : 0);
#endif
        }

        public static void PublishR029Trace(
            GachaNativeHybridR029Trace trace)
        {
            r029TracePublished?.Invoke(trace);
#if UNITY_IOS && !UNITY_EDITOR
            CodexGachaRevealReceiveR029Trace(
                trace.Checkpoint,
                trace.RawRequestUuid,
                trace.ReceiptUuid,
                trace.UnityFrameCount,
                trace.CaseRootName,
                trace.CaseTypeName,
                trace.CaseEntityId,
                trace.CaseRendererCount,
                trace.ForeignRendererCount,
                trace.CaseStableFrame ? 1 : 0,
                trace.CameraStableFrame ? 1 : 0,
                trace.SetupSucceeded ? 1 : 0,
                trace.RevealSetupFailure,
                trace.NativeHybridProgress,
                trace.CaseIsCanonical ? 1 : 0,
                trace.CaseIsOnlyUnityRenderable ? 1 : 0,
                trace.UnityClearBackdropIsolated ? 1 : 0);
#endif
        }

        public static void PublishR030Trace(
            GachaNativeHybridR030Trace trace)
        {
            r030TracePublished?.Invoke(trace);
#if UNITY_IOS && !UNITY_EDITOR
            CodexGachaRevealReceiveR030Trace(
                trace.Checkpoint,
                trace.StableFrameOrdinal,
                trace.RawRequestUuid,
                trace.ReceiptUuid,
                trace.UnityFrameCount,
                trace.CameraInstanceId,
                trace.CameraName,
                trace.CaseRootName,
                trace.CaseTypeName,
                trace.CaseEntityId,
                trace.CaseRendererCount,
                trace.ForeignRendererCount,
                trace.CaseStableFrame ? 1 : 0,
                trace.CameraStableFrame ? 1 : 0,
                trace.IsolationActive ? 1 : 0,
                trace.UsesCavityClearBackdrop ? 1 : 0,
                trace.PublishSetupPublished ? 1 : 0,
                trace.PublishSetupSucceeded ? 1 : 0,
                trace.PublishSetupFailure,
                trace.NativeHybridProgress,
                trace.CaseIsCanonical ? 1 : 0,
                trace.CaseIsOnlyUnityRenderable ? 1 : 0);
#endif
        }
    }
}
