using System;
#if UNITY_IOS && !UNITY_EDITOR
using System.Runtime.InteropServices;
#endif

namespace FidgetingApp.Product.Gacha
{
    public static class GachaPresentationNativeBridge
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexGachaRevealReceiveSetup(
            string requestId,
            int succeeded,
            string failureReason);

        [DllImport("__Internal")]
        private static extern void CodexGachaRevealReceivePhase(
            string requestId,
            string phase,
            string failureReason);
#endif

        public static void PublishSetup(
            string requestId,
            bool succeeded,
            string failureReason = "")
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexGachaRevealReceiveSetup(
                requestId ?? string.Empty,
                succeeded ? 1 : 0,
                failureReason ?? string.Empty);
#endif
        }

        public static void PublishPhase(
            string requestId,
            string phase,
            string failureReason = "")
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexGachaRevealReceivePhase(
                requestId ?? string.Empty,
                phase ?? string.Empty,
                failureReason ?? string.Empty);
#endif
        }
    }
}
