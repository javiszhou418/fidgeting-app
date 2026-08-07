using ThreeBladeEDC.Interaction;
using UnityEngine;

namespace ThreeBladeEDC.Presentation
{
    [DisallowMultipleComponent]
    public sealed class MobileRuntimeBootstrap : MonoBehaviour
    {
        [SerializeField] private RotorRigidbodyController rotor;
        [SerializeField] private MobileGestureController gestures;

        public void Configure(
            RotorRigidbodyController rotorController,
            MobileGestureController gestureController)
        {
            rotor = rotorController;
            gestures = gestureController;
        }

        private void Awake()
        {
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = 60;
            Screen.sleepTimeout = SleepTimeout.SystemSetting;
            Screen.autorotateToPortrait = true;
            Screen.autorotateToPortraitUpsideDown = false;
            Screen.autorotateToLandscapeLeft = false;
            Screen.autorotateToLandscapeRight = false;
            Screen.orientation = ScreenOrientation.Portrait;
        }

        private void OnApplicationPause(bool paused)
        {
            if (!paused)
            {
                return;
            }

            gestures?.CancelAll();
            rotor?.SetMotorActive(false);
        }
    }
}
