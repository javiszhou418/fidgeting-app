using System;
using System.Globalization;
using FidgetingApp.Product;
using UnityEngine;
using UnityEngine.InputSystem;

namespace CodexUnityLab
{
    /// <summary>
    /// Core Motion input for the classic blue scene. Tilt drives parallax and
    /// framing only. Rotation about the spin axis couples into the classic
    /// rotor's real angular velocity, a shake above threshold becomes a rotor
    /// impulse, and twisting the phone turns the Device Twist dial. The rotor
    /// raises its own DetentCrossed / ShakeBurst; this component only raises
    /// the dial's TwistDetentCrossed as a mechanism event and never calls the
    /// haptic router for either. InertiaShift remains the legacy channel.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class DeviceMotionController : MonoBehaviour
    {
        [SerializeField] private PortraitCameraFramer cameraFramer;
        [SerializeField, Min(1f)] private float maximumInputAngle = 18f;
        [SerializeField, Min(0f)] private float response = 8f;
        [SerializeField, Min(0f)] private float gyroscopeLead = 0.035f;

        private AttitudeSensor attitudeSensor;
        private UnityEngine.InputSystem.Gyroscope gyroscope;
        private Quaternion referenceAttitude;
        private Vector3 nativeReferenceAttitude;
        private Vector2 filteredTilt;
        private bool hasReference;
        private bool hasNativeReference;
        private bool nativeMotionAvailable;
        private bool enabledAttitudeSensor;
        private bool enabledGyroscope;
        private readonly FidgetInertiaHapticDetector inertiaHapticDetector =
            new FidgetInertiaHapticDetector();
        private readonly DeviceTwistDial twistDial = new DeviceTwistDial();
        private readonly FidgetShakeDetector shakeDetector = new FidgetShakeDetector();
        private FidgetSpinnerController spinner;
        private bool mechanismDriveEnabled = true;

        /// <summary>Mechanism events from the Device Twist dial.</summary>
        public event Action<FidgetSemanticEvent, float> SemanticEventRaised;

        public float MaximumInputAngle => maximumInputAngle;
        public float Response => response;
        public float GyroscopeLead => gyroscopeLead;
        public DeviceTwistDial TwistDial => twistDial;
        public bool MechanismDriveEnabled => mechanismDriveEnabled;

        private void Awake()
        {
            if (cameraFramer == null)
            {
                cameraFramer = GetComponent<PortraitCameraFramer>();
            }
        }

        private void OnEnable()
        {
            ResumeMotion();
        }

        private void OnDisable()
        {
            cameraFramer?.SetMotionTilt(Vector2.zero);
            SuspendMotion();
        }

        private void Update()
        {
            if (nativeMotionAvailable
                && IosDeviceMotion.TryRead(
                    out Vector3 nativeAttitude,
                    out Vector3 nativeRotationRate,
                    out _,
                    out Vector3 userAcceleration))
            {
                UpdateFromNativeMotion(nativeAttitude, nativeRotationRate);
                if (inertiaHapticDetector.Update(
                        userAcceleration,
                        Time.unscaledDeltaTime,
                        out float inertiaStrength))
                {
                    FidgetHapticRouter.Emit(
                        FidgetSemanticEvent.InertiaShift,
                        inertiaStrength);
                }
                UpdateMechanismDrive(
                    nativeRotationRate,
                    userAcceleration,
                    Time.unscaledDeltaTime);
                return;
            }

            UpdateFromInputSystem();
        }

        private void UpdateFromNativeMotion(Vector3 attitudeRadians, Vector3 rotationRateRadians)
        {
            Vector3 attitudeDegrees = attitudeRadians * Mathf.Rad2Deg;
            if (!hasNativeReference)
            {
                nativeReferenceAttitude = attitudeDegrees;
                hasNativeReference = true;
            }

            float roll = Mathf.DeltaAngle(nativeReferenceAttitude.x, attitudeDegrees.x);
            float pitch = Mathf.DeltaAngle(nativeReferenceAttitude.y, attitudeDegrees.y);
            Vector2 targetTilt = new Vector2(roll, -pitch) / Mathf.Max(1f, maximumInputAngle);
            targetTilt += new Vector2(rotationRateRadians.x, -rotationRateRadians.y) * gyroscopeLead;
            ApplyTilt(targetTilt);
        }

        private void UpdateFromInputSystem()
        {
            if (attitudeSensor == null || !attitudeSensor.enabled)
            {
                return;
            }

            Quaternion currentAttitude = attitudeSensor.attitude.ReadValue();
            if (Quaternion.Dot(currentAttitude, currentAttitude) < 0.5f)
            {
                return;
            }

            currentAttitude = Quaternion.Normalize(currentAttitude);
            if (!hasReference)
            {
                referenceAttitude = currentAttitude;
                hasReference = true;
            }

            Quaternion relativeAttitude = Quaternion.Inverse(referenceAttitude) * currentAttitude;
            Vector3 angles = relativeAttitude.eulerAngles;
            float pitch = NormalizeAngle(angles.x);
            float roll = NormalizeAngle(angles.z);
            Vector2 targetTilt = new Vector2(-roll, pitch) / Mathf.Max(1f, maximumInputAngle);

            if (gyroscope != null && gyroscope.enabled)
            {
                Vector3 angularVelocity = gyroscope.angularVelocity.ReadValue();
                targetTilt += new Vector2(-angularVelocity.z, angularVelocity.x) * gyroscopeLead;
            }

            ApplyTilt(targetTilt);
        }

        private void UpdateMechanismDrive(
            Vector3 rotationRate,
            Vector3 userAcceleration,
            float deltaTime)
        {
            if (spinner == null)
            {
                spinner = FindAnyObjectByType<FidgetSpinnerController>();
            }

            float rateAboutSpinAxis = 0f;
            if (mechanismDriveEnabled && spinner != null)
            {
                Transform basis = cameraFramer != null ? cameraFramer.transform : transform;
                rateAboutSpinAxis = DeviceMotionMechanismCoupling.ResolvePhoneRateAboutAxis(
                    rotationRate,
                    basis.right,
                    basis.up,
                    basis.forward,
                    spinner.SpinAxisWorld);
                spinner.SetDeviceFrameRotationRate(rateAboutSpinAxis);
            }

            UpdateTwistDial(rotationRate.z, deltaTime);

            if (shakeDetector.Update(userAcceleration, deltaTime, out float shakeStrength)
                && mechanismDriveEnabled
                && spinner != null)
            {
                // A free rotor lags the phone, so the shake spins it against
                // the phone's own twist; fall back to lateral acceleration.
                float lagDirection = -rateAboutSpinAxis;
                float directionSource = Mathf.Abs(lagDirection) > 0.2f
                    ? lagDirection
                    : userAcceleration.x;
                float direction = Mathf.Approximately(directionSource, 0f)
                    ? 1f
                    : Mathf.Sign(directionSource);
                spinner.ApplyDeviceShakeImpulse(
                    direction * Mathf.Lerp(4f, 10f, shakeStrength),
                    shakeStrength);
            }
        }

        private void UpdateTwistDial(float rateAboutScreenNormal, float deltaTime)
        {
            if (!mechanismDriveEnabled)
            {
                return;
            }

            DeviceTwistDialStep twist = twistDial.Update(rateAboutScreenNormal, deltaTime);
            if (!twist.EmitTick)
            {
                return;
            }

            // The finger-driven ratchet owns ticks while a finger is down.
            if (spinner != null && spinner.IsFingerControlling)
            {
                return;
            }

            SemanticEventRaised?.Invoke(
                FidgetSemanticEvent.TwistDetentCrossed,
                twist.NormalizedIntensity);
        }

        /// <summary>
        /// Library browsing keeps parallax but must not let the phone spin,
        /// shake, or tick the mechanism.
        /// </summary>
        public void SetMechanismDriveEnabled(bool enabled)
        {
            mechanismDriveEnabled = enabled;
            if (!enabled)
            {
                ClearMechanismDrive();
            }
        }

        private void ClearMechanismDrive()
        {
            twistDial.Recenter();
            shakeDetector.Reset();
            spinner?.ClearDeviceFrameRotation();
        }

        private void ApplyTilt(Vector2 targetTilt)
        {
            float blend = 1f - Mathf.Exp(-response * Time.unscaledDeltaTime);
            filteredTilt = Vector2.Lerp(filteredTilt, targetTilt, blend);
            SceneParallaxInput.Publish(filteredTilt, maximumInputAngle);
            cameraFramer?.SetMotionTilt(filteredTilt);
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

        private void ResumeMotion()
        {
            nativeMotionAvailable = IosDeviceMotion.Start();
            if (nativeMotionAvailable)
            {
                // Core Motion is the iPhone source of truth. Running Unity's
                // attitude and gyro devices as well duplicates the same 60 Hz
                // sensor pipeline and wastes CPU/power without improving input.
                DisableFallbackSensors();
            }
            else
            {
                EnableFallbackSensors();
            }

            ResetReference();
        }

        private void SuspendMotion()
        {
            nativeMotionAvailable = false;
            IosDeviceMotion.Stop();
            DisableFallbackSensors();
            ClearMechanismDrive();
        }

        private void EnableFallbackSensors()
        {
            attitudeSensor = AttitudeSensor.current;
            gyroscope = UnityEngine.InputSystem.Gyroscope.current;

            if (attitudeSensor != null && !attitudeSensor.enabled)
            {
                InputSystem.EnableDevice(attitudeSensor);
                enabledAttitudeSensor = true;
            }

            if (gyroscope != null && !gyroscope.enabled)
            {
                InputSystem.EnableDevice(gyroscope);
                enabledGyroscope = true;
            }
        }

        private void DisableFallbackSensors()
        {
            if (enabledAttitudeSensor && attitudeSensor != null)
            {
                InputSystem.DisableDevice(attitudeSensor);
            }

            if (enabledGyroscope && gyroscope != null)
            {
                InputSystem.DisableDevice(gyroscope);
            }

            enabledAttitudeSensor = false;
            enabledGyroscope = false;
        }

        public void ResetReference()
        {
            hasReference = false;
            hasNativeReference = false;
            filteredTilt = Vector2.zero;
            inertiaHapticDetector.Reset();
            ClearMechanismDrive();
            SceneParallaxInput.Reset();
            cameraFramer?.SetMotionTilt(Vector2.zero);
        }

        public void SetMaximumInputAngleFromNativeUi(string value)
        {
            if (TryParseFloat(value, out float parsedValue))
            {
                maximumInputAngle = Mathf.Clamp(parsedValue, 4f, 45f);
            }
        }

        public void SetResponseFromNativeUi(string value)
        {
            if (TryParseFloat(value, out float parsedValue))
            {
                response = Mathf.Clamp(parsedValue, 1f, 30f);
            }
        }

        public void SetGyroscopeLeadFromNativeUi(string value)
        {
            if (TryParseFloat(value, out float parsedValue))
            {
                gyroscopeLead = Mathf.Clamp(parsedValue, 0f, 0.25f);
            }
        }

        private static bool TryParseFloat(string value, out float parsedValue)
        {
            return float.TryParse(
                value,
                NumberStyles.Float,
                CultureInfo.InvariantCulture,
                out parsedValue);
        }

        private static float NormalizeAngle(float degrees)
        {
            return Mathf.DeltaAngle(0f, degrees);
        }
    }
}
