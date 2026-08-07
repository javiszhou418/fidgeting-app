using CodexUnityLab;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEngine;

namespace FidgetingApp.Product
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(OrbitPresentationCamera))]
    public sealed class MetalDeviceMotionController : MonoBehaviour
    {
        private OrbitPresentationCamera orbitCamera;
        private float maximumInputAngle = 18f;
        private float response = 8f;
        private float gyroscopeLead = 0.035f;
        private float maximumMotionOrbit = 6.5f;
        private Vector3 referenceAttitude;
        private Vector2 filteredTilt;
        private bool hasReference;
        private bool motionAvailable;
        private RotorRigidbodyController rotor;
        private readonly FidgetShakeDetector shakeDetector = new FidgetShakeDetector();
        private readonly FidgetInertiaHapticDetector inertiaHapticDetector =
            new FidgetInertiaHapticDetector();

        private void Awake()
        {
            orbitCamera = GetComponent<OrbitPresentationCamera>();
            rotor = FindAnyObjectByType<RotorRigidbodyController>();
        }

        private void OnEnable()
        {
            ResumeMotion();
        }

        private void OnDisable()
        {
            orbitCamera?.ResetMotionTilt();
            SuspendMotion();
        }

        private void Update()
        {
            if (!motionAvailable
                || !IosDeviceMotion.TryRead(
                    out Vector3 attitude,
                    out Vector3 rotationRate,
                    out _,
                    out Vector3 userAcceleration))
            {
                return;
            }

            if (inertiaHapticDetector.Update(
                    userAcceleration,
                    Time.unscaledDeltaTime,
                    out float inertiaStrength))
            {
                FidgetHapticRouter.Emit(
                    FidgetSemanticEvent.InertiaShift,
                    inertiaStrength);
            }

            if (shakeDetector.Update(
                    userAcceleration,
                    Time.unscaledDeltaTime,
                    out float shakeStrength))
            {
                float directionSource = Mathf.Abs(rotationRate.z) > 0.2f
                    ? rotationRate.z
                    : userAcceleration.x;
                float direction = Mathf.Approximately(directionSource, 0f)
                    ? 1f
                    : Mathf.Sign(directionSource);
                rotor?.AddFlickVelocity(direction * Mathf.Lerp(4f, 10f, shakeStrength));
            }

            Vector3 attitudeDegrees = attitude * Mathf.Rad2Deg;
            if (!hasReference)
            {
                referenceAttitude = attitudeDegrees;
                hasReference = true;
            }

            float roll = Mathf.DeltaAngle(referenceAttitude.x, attitudeDegrees.x);
            float pitch = Mathf.DeltaAngle(referenceAttitude.y, attitudeDegrees.y);
            Vector2 targetTilt = new Vector2(roll, -pitch) / Mathf.Max(1f, maximumInputAngle);
            targetTilt += new Vector2(rotationRate.x, -rotationRate.y) * gyroscopeLead;

            float blend = 1f - Mathf.Exp(-response * Time.unscaledDeltaTime);
            filteredTilt = Vector2.Lerp(filteredTilt, targetTilt, blend);
            SceneParallaxInput.Publish(filteredTilt, maximumInputAngle);
            orbitCamera?.SetMotionTilt(filteredTilt, maximumMotionOrbit);
        }

        private void OnApplicationPause(bool paused)
        {
            if (paused)
            {
                SuspendMotion();
                return;
            }

            ResumeMotion();
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
            orbitCamera?.SetMotionTilt(filteredTilt, maximumMotionOrbit);
        }

        public void ResetReference()
        {
            hasReference = false;
            filteredTilt = Vector2.zero;
            shakeDetector.Reset();
            inertiaHapticDetector.Reset();
            SceneParallaxInput.Reset();
            orbitCamera?.ResetMotionTilt();
        }
    }
}
