using System.Runtime.InteropServices;
using UnityEngine;

namespace CodexUnityLab
{
    [DisallowMultipleComponent]
    public sealed class IosSwiftUiOverlayController : MonoBehaviour
    {
#if UNITY_IOS && !UNITY_EDITOR
        [DllImport("__Internal")]
        private static extern void CodexSwiftUiOverlayInstall();
#endif

        // The shipping catalog can boot into any product scene. Installing the
        // native UI must therefore be an application-level responsibility, not
        // something that depends on the legacy blue-spinner scene containing
        // this MonoBehaviour as a serialized component.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void InstallAtApplicationStartup()
        {
            Install();
        }

        private void Start()
        {
            Install();
        }

        private void OnApplicationFocus(bool focused)
        {
            if (focused)
            {
                Install();
            }
        }

        private static void Install()
        {
#if UNITY_IOS && !UNITY_EDITOR
            CodexSwiftUiOverlayInstall();
#endif
        }
    }
}
