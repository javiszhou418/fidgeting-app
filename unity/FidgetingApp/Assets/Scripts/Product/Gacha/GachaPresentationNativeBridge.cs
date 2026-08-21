using System;
#if UNITY_IOS && !UNITY_EDITOR
using System.Runtime.InteropServices;
#endif

namespace FidgetingApp.Product.Gacha
{
    /// <summary>
    /// Native notifications for the shipping, Unity-rendered single-draw
    /// presentation. Swift owns only the transparent controls; Unity owns the
    /// display case, prize and authoritative phase clock.
    /// </summary>
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
            GachaRevealPhase phase,
            string failureReason = "")
        {
            PublishPhase(requestId, PhaseToken(phase), failureReason);
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

        public static string PhaseToken(GachaRevealPhase phase)
        {
            return phase switch
            {
                GachaRevealPhase.Back => "back",
                GachaRevealPhase.Front => "front",
                GachaRevealPhase.Readable => "readable",
                GachaRevealPhase.Complete => "complete",
                _ => "idle"
            };
        }
    }
}
