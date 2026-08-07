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
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            Screen.autorotateToPortrait = false;
            Screen.autorotateToPortraitUpsideDown = false;
            Screen.autorotateToLandscapeLeft = true;
            Screen.autorotateToLandscapeRight = true;
            Screen.orientation = ScreenOrientation.AutoRotation;
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
