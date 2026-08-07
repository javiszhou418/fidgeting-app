using CodexUnityLab;
using FidgetingApp.EDC;
using UnityEngine;

namespace FidgetingApp.Product
{
    /// <summary>
    /// Gives the fifth product the same Core Motion presentation response as
    /// the four rotor scenes. It only publishes visual tilt and camera orbit;
    /// it never writes slide progress, physics, progression, or Haptics.
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

        private void Awake()
        {
            cameraFramer = GetComponent<EdcPortraitCameraFramer>();
        }

        private void OnEnable()
        {
            ResumeMotion();
        }

        private void OnDisable()
        {
            cameraFramer?.ResetMotionTilt();
            SuspendMotion();
        }

        private void Update()
        {
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

        private void ResumeMotion()
        {
            motionAvailable = IosDeviceMotion.Start();
            ResetReference();
        }

        private void SuspendMotion()
        {
            motionAvailable = false;
            IosDeviceMotion.Stop();
        }
    }
}
