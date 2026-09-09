using System;
using CodexUnityLab;
using ThreeBladeEDC.Interaction;
using ThreeBladeEDC.Presentation;
using UnityEngine;

namespace FidgetingApp.Product
{
    /// <summary>
    /// Core Motion input for the four rotor scenes. Tilt drives only the
    /// camera orbit and parallax. Rotation about the spin axis couples into
    /// the rotor's real angular velocity, a shake above threshold becomes a
    /// rotor impulse, and twisting the phone turns the Device Twist dial.
    /// Every haptic still originates from a mechanism: the rotor raises its
    /// own Breakaway / DetentCrossed / ShakeBurst events and the dial raises
    /// TwistDetentCrossed; this component never calls the haptic router for
    /// them. InertiaShift remains the one legacy direct-router channel.
    /// </summary>
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
        private bool mechanismDriveEnabled = true;
        private RotorRigidbodyController rotor;
        private readonly FidgetShakeDetector shakeDetector = new FidgetShakeDetector();
        private readonly FidgetInertiaHapticDetector inertiaHapticDetector =
            new FidgetInertiaHapticDetector();
        private readonly DeviceTwistDial twistDial = new DeviceTwistDial();

        /// <summary>Mechanism events from the Device Twist dial.</summary>
        public event Action<FidgetSemanticEvent, float> SemanticEventRaised;

        public DeviceTwistDial TwistDial => twistDial;
        public bool MechanismDriveEnabled => mechanismDriveEnabled;

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

            float deltaTime = Time.unscaledDeltaTime;
            if (inertiaHapticDetector.Update(
                    userAcceleration,
                    deltaTime,
                    out float inertiaStrength))
            {
                FidgetHapticRouter.Emit(
                    FidgetSemanticEvent.InertiaShift,
                    inertiaStrength);
            }

            if (rotor == null)
            {
                rotor = FindAnyObjectByType<RotorRigidbodyController>();
            }

            float rateAboutSpinAxis = 0f;
            if (mechanismDriveEnabled && rotor != null)
            {
                rateAboutSpinAxis = DeviceMotionMechanismCoupling.ResolvePhoneRateAboutAxis(
                    rotationRate,
                    transform.right,
                    transform.up,
                    transform.forward,
                    rotor.SpinAxisWorld);
                rotor.SetDeviceFrameRotationRate(rateAboutSpinAxis);
            }

            if (mechanismDriveEnabled)
            {
                DeviceTwistDialStep twist = twistDial.Update(rotationRate.z, deltaTime);
                bool rotorOwnsTicks = rotor != null && rotor.IsDetentTravelActive;
                if (twist.EmitTick && !rotorOwnsTicks)
                {
                    SemanticEventRaised?.Invoke(
                        FidgetSemanticEvent.TwistDetentCrossed,
                        twist.NormalizedIntensity);
                }
            }

            if (shakeDetector.Update(
                    userAcceleration,
                    deltaTime,
                    out float shakeStrength)
                && mechanismDriveEnabled)
            {
                // A free rotor lags the phone, so the shake spins it against
                // the phone's own twist. Without a twist, fall back to the
                // lateral acceleration sign.
                float lagDirection = -rateAboutSpinAxis;
                float directionSource = Mathf.Abs(lagDirection) > 0.2f
                    ? lagDirection
                    : userAcceleration.x;
                float direction = Mathf.Approximately(directionSource, 0f)
                    ? 1f
                    : Mathf.Sign(directionSource);
                rotor?.ApplyDeviceShakeImpulse(
                    direction * Mathf.Lerp(4f, 10f, shakeStrength),
                    shakeStrength);
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
            ClearMechanismDrive();
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

        /// <summary>
        /// Library browsing and other non-play states keep parallax but must
        /// not let the phone move, spin, or tick the mechanism.
        /// </summary>
        public void SetMechanismDriveEnabled(bool enabled)
        {
            mechanismDriveEnabled = enabled;
            if (!enabled)
            {
                ClearMechanismDrive();
            }
        }

        public void ResetReference()
        {
            hasReference = false;
            filteredTilt = Vector2.zero;
            shakeDetector.Reset();
            inertiaHapticDetector.Reset();
            ClearMechanismDrive();
            SceneParallaxInput.Reset();
            orbitCamera?.ResetMotionTilt();
        }

        private void ClearMechanismDrive()
        {
            twistDial.Recenter();
            rotor?.ClearDeviceFrameRotation();
        }
    }
}
