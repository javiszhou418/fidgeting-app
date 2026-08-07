using System;
using UnityEngine;

namespace ThreeBladeEDC.Interaction
{
    public enum RotorAxisSpace
    {
        Local,
        World
    }

    /// <summary>
    /// Owns the physical state of RotorDynamic. Angular speeds are expressed
    /// in radians per second, matching Rigidbody.angularVelocity.
    /// </summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Rigidbody))]
    [DefaultExecutionOrder(-100)]
    public sealed class RotorRigidbodyController : MonoBehaviour
    {
        [Header("Axis")]
        [SerializeField] private RotorAxisSpace axisSpace = RotorAxisSpace.Local;
        [SerializeField] private Vector3 spinAxis = Vector3.up;
        [SerializeField] private bool constrainToSpinAxis = true;

        [Header("Rigidbody Setup")]
        [Tooltip("Applies the values below in Awake. Disable this to preserve a preconfigured Rigidbody.")]
        [SerializeField] private bool configureBodyOnAwake = true;
        [SerializeField] private bool disableGravity = true;
        [SerializeField] private bool freezeCenterWithoutHinge = true;
        [SerializeField, Min(0f)] private float angularDamping = 0.55f;
        [SerializeField, Min(0.1f)] private float maxAngularSpeed = 24f;
        [SerializeField] private RigidbodyInterpolation interpolation = RigidbodyInterpolation.Interpolate;

        [Header("Stopping")]
        [SerializeField, Min(0.05f)] private float reversalStopDuration = 0.3f;
        [SerializeField, Min(0f)] private float stoppedSpeedThreshold = 0.08f;

        [Header("Swipe Flip")]
        [SerializeField, Min(0.05f)] private float flipDuration = 0.4f;
        [SerializeField, Range(0f, 0.25f)] private float flipOvershoot = 0.1f;

        [Header("Optional Hinge")]
        [Tooltip("When present, its local axis is aligned with the configured spin axis in Awake.")]
        [SerializeField] private HingeJoint hingeJoint;
        [SerializeField] private bool configureHingeAxis = true;

        [Header("Space Motor")]
        [SerializeField] private float motorDirection = 1f;
        [SerializeField, Min(0f)] private float motorTargetSpeed = 35f;
        [SerializeField, Min(0f)] private float motorAcceleration = 80f;

        private Rigidbody _body;
        private Vector3 _initialPosition;
        private Quaternion _initialRotation;
        private float _accumulatedRotationDegrees;
        private bool _motorActive;
        private bool _initialized;
        private bool _isSmoothStopping;
        private float _smoothStopElapsed;
        private float _smoothStopStartSpeed;
        private float _activeStopDuration;
        private bool _isFlipping;
        private float _flipElapsed;
        private float _previousFlipAngle;
        private float _flipDirection = 1f;
        private float _flipBackCoefficient;

        public event Action ResetPerformed;

        public Rigidbody Body => _body;
        public bool MotorActive => _motorActive;
        public bool IsSmoothStopping => _isSmoothStopping;
        public bool IsFlipping => _isFlipping;
        public Vector3 PivotWorld => _body != null ? _body.worldCenterOfMass : transform.position;
        public Vector3 SpinAxisWorld => ResolveSpinAxisWorld();
        public float AngularSpeedRadians =>
            _body != null ? Vector3.Dot(_body.angularVelocity, SpinAxisWorld) : 0f;
        public float AngularSpeedDegrees => AngularSpeedRadians * Mathf.Rad2Deg;
        public float AccumulatedRotationDegrees => _accumulatedRotationDegrees;

        private void Awake()
        {
            _body = GetComponent<Rigidbody>();
            CaptureInitialPose();

            if (hingeJoint == null)
            {
                TryGetComponent(out hingeJoint);
            }

            if (configureBodyOnAwake)
            {
                ConfigureBody();
            }

            if (hingeJoint != null && configureHingeAxis)
            {
                ConfigureHinge();
            }

            _flipBackCoefficient =
                global::ThreeBladeEDC.FidgetSpinnerMotion
                    .BackCoefficientForOvershoot(flipOvershoot);

            _initialized = true;
        }

        private void OnDisable()
        {
            _motorActive = false;
        }

        private void OnValidate()
        {
            if (spinAxis.sqrMagnitude <= Mathf.Epsilon)
            {
                spinAxis = Vector3.up;
            }

            angularDamping = Mathf.Max(0f, angularDamping);
            maxAngularSpeed = Mathf.Max(0.1f, maxAngularSpeed);
            reversalStopDuration = Mathf.Max(0.05f, reversalStopDuration);
            stoppedSpeedThreshold = Mathf.Max(0f, stoppedSpeedThreshold);
            flipDuration = Mathf.Max(0.05f, flipDuration);
            flipOvershoot = Mathf.Clamp(flipOvershoot, 0f, 0.25f);
            _flipBackCoefficient =
                global::ThreeBladeEDC.FidgetSpinnerMotion
                    .BackCoefficientForOvershoot(flipOvershoot);
            motorTargetSpeed = Mathf.Max(0f, motorTargetSpeed);
            motorAcceleration = Mathf.Max(0f, motorAcceleration);
        }

        private void FixedUpdate()
        {
            if (_body == null || _body.isKinematic)
            {
                return;
            }

            Vector3 axis = SpinAxisWorld;
            Vector3 angularVelocity = _body.angularVelocity;
            float axialSpeed = Mathf.Clamp(
                Vector3.Dot(angularVelocity, axis),
                -maxAngularSpeed,
                maxAngularSpeed);

            if (_isSmoothStopping)
            {
                _smoothStopElapsed += Time.fixedUnscaledDeltaTime;
                axialSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion.DecelerateToStop(
                    _smoothStopStartSpeed,
                    _smoothStopElapsed,
                    _activeStopDuration);

                if (_smoothStopElapsed >= _activeStopDuration
                    || Mathf.Abs(axialSpeed) <= stoppedSpeedThreshold)
                {
                    axialSpeed = 0f;
                    _isSmoothStopping = false;
                }
            }

            if (constrainToSpinAxis)
            {
                _body.angularVelocity = axis * axialSpeed;
            }
            else if (Mathf.Abs(Vector3.Dot(angularVelocity, axis)) > maxAngularSpeed)
            {
                Vector3 offAxisVelocity = angularVelocity
                    - axis * Vector3.Dot(angularVelocity, axis);
                _body.angularVelocity = offAxisVelocity + axis * axialSpeed;
            }

            if (_motorActive && motorAcceleration > 0f)
            {
                float targetSpeed = Mathf.Sign(motorDirection) * motorTargetSpeed;
                float acceleration = Mathf.Clamp(
                    (targetSpeed - axialSpeed) / Mathf.Max(Time.fixedDeltaTime, 0.0001f),
                    -motorAcceleration,
                    motorAcceleration);

                _body.AddTorque(axis * acceleration, ForceMode.Acceleration);
            }

            UpdateFlip(axis);

            _accumulatedRotationDegrees +=
                axialSpeed * Mathf.Rad2Deg * Time.fixedDeltaTime;
        }

        /// <summary>
        /// Adds one tactile 360-degree turn over 400 ms. The ease-out-back
        /// curve reaches the configured peak overshoot and settles at a full
        /// revolution, so the final orientation remains continuous.
        /// </summary>
        public void TriggerFlip(float direction)
        {
            if (_body == null || _body.isKinematic)
            {
                return;
            }

            _isFlipping = true;
            _flipElapsed = 0f;
            _previousFlipAngle = 0f;
            _flipDirection = direction == 0f ? 1f : Mathf.Sign(direction);
            _flipBackCoefficient =
                global::ThreeBladeEDC.FidgetSpinnerMotion
                    .BackCoefficientForOvershoot(flipOvershoot);
            _body.WakeUp();
        }

        private void UpdateFlip(Vector3 axis)
        {
            if (!_isFlipping)
            {
                return;
            }

            _flipElapsed += Time.fixedUnscaledDeltaTime;
            float progress = Mathf.Clamp01(_flipElapsed / flipDuration);
            float eased = global::ThreeBladeEDC.FidgetSpinnerMotion.EaseOutBack(
                progress,
                _flipBackCoefficient);
            float angle = _flipDirection * 360f * eased;
            float deltaAngle = angle - _previousFlipAngle;
            _previousFlipAngle = angle;

            Quaternion rotation = Quaternion.AngleAxis(deltaAngle, axis);
            _body.MoveRotation(rotation * _body.rotation);
            _accumulatedRotationDegrees += deltaAngle;

            if (progress >= 1f)
            {
                _isFlipping = false;
                _previousFlipAngle = 0f;
            }
        }

        /// <summary>
        /// Adds a flick to the current axial speed. The requested change is
        /// clamped before being written to the Rigidbody.
        /// </summary>
        public void AddFlickVelocity(float deltaRadiansPerSecond)
        {
            SetSpinVelocity(AngularSpeedRadians + deltaRadiansPerSecond);
        }

        /// <summary>
        /// Sets only the axial component of Rigidbody.angularVelocity.
        /// </summary>
        public void SetSpinVelocity(float radiansPerSecond)
        {
            if (_body == null || _body.isKinematic)
            {
                return;
            }

            _isSmoothStopping = false;

            Vector3 axis = SpinAxisWorld;
            float clampedSpeed = Mathf.Clamp(
                radiansPerSecond,
                -maxAngularSpeed,
                maxAngularSpeed);
            Vector3 offAxisVelocity = constrainToSpinAxis
                ? Vector3.zero
                : _body.angularVelocity
                    - axis * Vector3.Dot(_body.angularVelocity, axis);

            _body.angularVelocity = offAxisVelocity + axis * clampedSpeed;
            _body.WakeUp();
        }

        public void SetMotorActive(bool active)
        {
            _motorActive = active;
            if (active)
            {
                _isSmoothStopping = false;
            }

            if (active && _body != null)
            {
                _body.WakeUp();
            }
        }

        /// <summary>
        /// Brakes the current axial motion to rest with an ease-out curve.
        /// Repeated calls while braking do not restart the timer.
        /// </summary>
        public void SmoothStop(float duration = -1f)
        {
            if (_body == null || _body.isKinematic || _isSmoothStopping)
            {
                return;
            }

            float currentSpeed = AngularSpeedRadians;
            if (Mathf.Abs(currentSpeed) <= stoppedSpeedThreshold)
            {
                Stop();
                return;
            }

            _motorActive = false;
            _smoothStopStartSpeed = currentSpeed;
            _smoothStopElapsed = 0f;
            _activeStopDuration = duration > 0f
                ? Mathf.Max(0.05f, duration)
                : reversalStopDuration;
            _isSmoothStopping = true;
            _body.WakeUp();
        }

        public void Stop()
        {
            _motorActive = false;
            _isSmoothStopping = false;
            _smoothStopElapsed = 0f;
            _isFlipping = false;
            _flipElapsed = 0f;
            _previousFlipAngle = 0f;

            if (_body != null && !_body.isKinematic)
            {
                Vector3 axis = SpinAxisWorld;
                Vector3 offAxisVelocity = constrainToSpinAxis
                    ? Vector3.zero
                    : _body.angularVelocity
                        - axis * Vector3.Dot(_body.angularVelocity, axis);
                _body.angularVelocity = offAxisVelocity;
            }
        }

        public void ResetRotor()
        {
            if (!_initialized || _body == null)
            {
                return;
            }

            _motorActive = false;
            _isSmoothStopping = false;
            _smoothStopElapsed = 0f;
            _isFlipping = false;
            _flipElapsed = 0f;
            _previousFlipAngle = 0f;
            _body.position = _initialPosition;
            _body.rotation = _initialRotation;
            _body.linearVelocity = Vector3.zero;
            _body.angularVelocity = Vector3.zero;
            _accumulatedRotationDegrees = 0f;
            _body.Sleep();
            ResetPerformed?.Invoke();
        }

        /// <summary>
        /// Replaces the pose used by ResetRotor. Intended for runtime assembly
        /// after the object has been positioned, before interaction begins.
        /// </summary>
        public void CaptureInitialPose()
        {
            if (_body == null)
            {
                _body = GetComponent<Rigidbody>();
            }

            _initialPosition = _body.position;
            _initialRotation = _body.rotation;
            _accumulatedRotationDegrees = 0f;
        }

        private Vector3 ResolveSpinAxisWorld()
        {
            Vector3 normalizedAxis = spinAxis.sqrMagnitude > Mathf.Epsilon
                ? spinAxis.normalized
                : Vector3.up;

            return axisSpace == RotorAxisSpace.Local
                ? transform.TransformDirection(normalizedAxis).normalized
                : normalizedAxis;
        }

        private void ConfigureBody()
        {
            _body.isKinematic = false;
            _body.useGravity = !disableGravity;
            _body.angularDamping = angularDamping;
            _body.maxAngularVelocity = maxAngularSpeed;
            _body.interpolation = interpolation;

            if (freezeCenterWithoutHinge && hingeJoint == null)
            {
                _body.constraints |= RigidbodyConstraints.FreezePosition;
            }
        }

        private void ConfigureHinge()
        {
            hingeJoint.axis = transform.InverseTransformDirection(SpinAxisWorld).normalized;
            hingeJoint.useMotor = false;
            hingeJoint.useSpring = false;
            hingeJoint.useLimits = false;
        }
    }
}
