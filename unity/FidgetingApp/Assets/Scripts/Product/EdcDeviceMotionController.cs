using CodexUnityLab;
using FidgetingApp.EDC;
using FidgetingApp.FanCard;
using UnityEngine;

namespace FidgetingApp.Product
{
    /// <summary>
    /// Gives the linear slider and magnetic fan card the same Core Motion
    /// presentation response as the rotor scenes. It only publishes visual
    /// tilt and camera orbit; it never writes mechanism progress, physics,
    /// progression, or Haptics.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(EdcPortraitCameraFramer))]
    public sealed class EdcDeviceMotionController : MonoBehaviour
    {
        private EdcPortraitCameraFramer cameraFramer;
        private float maximumInputAngle = 18f;
        private float response = 8f;
        private float gyroscopeLead = 0.035f;
        private float maximumMotionOrbit = 6.5f;
        private Vector3 referenceAttitude;
        private Vector2 filteredTilt;
        private bool hasReference;
        private bool motionAvailable;
        private EdcSliderController sliderController;
        private FanCardController fanCardController;
        private bool productInteractionSuppressed;
        private bool motionSuspendedForInteraction;

        public bool IsProductInteractionSuppressed =>
            productInteractionSuppressed;

        private void Awake()
        {
            cameraFramer = GetComponent<EdcPortraitCameraFramer>();
            ResolveInteractionSources();
        }

        private void OnEnable()
        {
            ResolveInteractionSources();
            ResumeMotion();
        }

        private void OnDisable()
        {
            cameraFramer?.ResetMotionTilt();
            SuspendMotion();
        }

        private void Update()
        {
            if (sliderController == null && fanCardController == null)
            {
                ResolveInteractionSources();
            }
            bool shouldSuppress = ShouldSuppressForProductInteraction(
                sliderController != null && sliderController.IsDragging,
                fanCardController != null
                    && fanCardController.IsDirectInteractionActive);
            if (shouldSuppress)
            {
                // Keep the last camera pose perfectly still while the finger
                // resolves an angular or linear mechanism. Recomputing tilt
                // here would move the product pivot underneath that finger.
                productInteractionSuppressed = true;
                if (!motionSuspendedForInteraction)
                {
                    motionSuspendedForInteraction = true;
                    motionAvailable = false;
                    IosDeviceMotion.Stop();
                }
                // SpinnerSceneParallaxController treats an old sample as an
                // instruction to ease back to zero. Republishing the frozen
                // sample prevents that fallback movement from sliding the
                // pivot out from beneath the finger while Core Motion is off.
                SceneParallaxInput.Publish(filteredTilt, maximumInputAngle);
                cameraFramer?.SetMotionTilt(filteredTilt, maximumMotionOrbit);
                return;
            }

            if (productInteractionSuppressed)
            {
                // Rebase to the device's release attitude so resuming Core
                // Motion cannot introduce a one-frame jump after the drag.
                productInteractionSuppressed = false;
                motionSuspendedForInteraction = false;
                motionAvailable = IosDeviceMotion.Start();
                hasReference = false;
            }

            if (!motionAvailable
                || !IosDeviceMotion.TryRead(
                    out Vector3 attitude,
                    out Vector3 rotationRate))
            {
                return;
            }

            Vector3 attitudeDegrees = attitude * Mathf.Rad2Deg;
            if (!hasReference)
            {
                referenceAttitude = attitudeDegrees;
                hasReference = true;
            }

            float roll = Mathf.DeltaAngle(referenceAttitude.x, attitudeDegrees.x);
            float pitch = Mathf.DeltaAngle(referenceAttitude.y, attitudeDegrees.y);
            Vector2 targetTilt = new Vector2(roll, -pitch)
                / Mathf.Max(1f, maximumInputAngle);
            targetTilt += new Vector2(rotationRate.x, -rotationRate.y)
                * gyroscopeLead;

            float blend = 1f - Mathf.Exp(-response * Time.unscaledDeltaTime);
            filteredTilt = Vector2.Lerp(filteredTilt, targetTilt, blend);
            SceneParallaxInput.Publish(filteredTilt, maximumInputAngle);
            cameraFramer?.SetMotionTilt(filteredTilt, maximumMotionOrbit);
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                SuspendMotion();
            }
            else
            {
                ResumeMotion();
            }
        }

        private void OnApplicationFocus(bool focused)
        {
            if (focused)
            {
                ResumeMotion();
            }
            else
            {
                SuspendMotion();
            }
        }

        public void Configure(
            float inputAngle,
            float motionResponse,
            float lead,
            float orbitDegrees)
        {
            maximumInputAngle = Mathf.Clamp(inputAngle, 4f, 45f);
            response = Mathf.Clamp(motionResponse, 1f, 30f);
            gyroscopeLead = Mathf.Clamp(lead, 0f, 0.25f);
            maximumMotionOrbit = Mathf.Clamp(orbitDegrees, 0f, 24f);
            cameraFramer?.SetMotionTilt(filteredTilt, maximumMotionOrbit);
        }

        public void ResetReference()
        {
            hasReference = false;
            filteredTilt = Vector2.zero;
            SceneParallaxInput.Reset();
            cameraFramer?.ResetMotionTilt();
        }

        public static bool ShouldSuppressForProductInteraction(
            bool sliderDragging,
            bool fanCardDragging)
        {
            return sliderDragging || fanCardDragging;
        }

        private void ResumeMotion()
        {
            motionSuspendedForInteraction = false;
            motionAvailable = IosDeviceMotion.Start();
            ResetReference();
        }

        private void SuspendMotion()
        {
            motionAvailable = false;
            productInteractionSuppressed = false;
            motionSuspendedForInteraction = false;
            IosDeviceMotion.Stop();
        }

        private void ResolveInteractionSources()
        {
            sliderController = FindAnyObjectByType<EdcSliderController>();
            fanCardController = FindAnyObjectByType<FanCardController>();
        }
    }
}
