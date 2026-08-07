using System;
using CodexUnityLab;
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
        [SerializeField, Min(0.05f)] private float coastHalfLife =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultCoastHalfLife;
        [SerializeField, Min(0.1f)] private float maxAngularSpeed =
            global::ThreeBladeEDC.FidgetSpinnerMotion.DefaultMaximumAngularSpeed;
        [SerializeField] private RigidbodyInterpolation interpolation = RigidbodyInterpolation.Interpolate;

        [Header("Resistance Model")]
        [SerializeField] private global::ThreeBladeEDC.SpinnerResistanceMode resistanceMode =
            global::ThreeBladeEDC.SpinnerResistanceMode.Freewheel;
        [SerializeField, Range(1, 120)] private int magneticDetentsPerTurn =
            DetentFeelPresetCatalog.Default.Config.DetentsPerRevolution;
        [SerializeField, Min(0f)] private float magneticBreakawaySpeed = 2.2f;
        [SerializeField, Min(0f)] private float magneticCaptureSpeed = 1.2f;
        [SerializeField, Min(0.1f)] private float magneticSnapResponse = 16f;

        [Header("Stopping")]
        [SerializeField, Min(0.05f)] private float reversalStopDuration = 0.3f;
        [SerializeField, Min(0f)] private float stoppedSpeedThreshold = 0.08f;

        [Header("Swipe Flip")]
        [SerializeField, Min(0.05f)] private float flipDuration = 0.4f;
        [SerializeField, Range(0f, 0.25f)] private float flipOvershoot = 0.1f;

        [Header("Optional Hinge")]
        [Tooltip("Legacy scene reference. Runtime uses Rigidbody constraints as the single authority.")]
        [SerializeField] private HingeJoint hingeJoint;

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
        private float _flipDirection = 1f;
        private float _flipBackCoefficient;
        private Quaternion _flipStartRotation;
        private Vector3 _flipAxisWorld;
        private float _flipResumeSpeed;
        private bool _flipCollisionState;
        private bool _hasPendingSpinVelocity;
        private float _pendingSpinVelocity;
        private bool _fingerControlling;
        private bool _magneticLocked;
        private bool _magneticCapturePending;
        private float _magneticSnapTargetDegrees;
        private int _lastDetentIndex;
        private bool _hasDetentIndex;
        private float _ratchetInitialFlickForce;
        private int _ratchetInitialFlickClicksRemaining;
        private bool _assistantDriveActive;
        private float _assistantTargetSpeed;

        public event Action ResetPerformed;
        public event Action<FidgetSemanticEvent, float> SemanticEventRaised;
        public event Action<RatchetDetentAudioSignal> RatchetDetentCrossed;

        public Rigidbody Body => _body;
        public bool MotorActive => _motorActive;
        public bool IsSmoothStopping => _isSmoothStopping;
        public bool IsFlipping => _isFlipping;
        public bool IsFingerControlling => _fingerControlling;
        public bool IsMagneticLocked => _magneticLocked;
        public bool IsAssistantDriving => _assistantDriveActive;
        public global::ThreeBladeEDC.SpinnerResistanceMode ResistanceMode => resistanceMode;
        public Vector3 PivotWorld => _body != null ? _body.worldCenterOfMass : transform.position;
        public Vector3 SpinAxisWorld => ResolveSpinAxisWorld();
        public float AngularSpeedRadians =>
            _body != null ? Vector3.Dot(_body.angularVelocity, SpinAxisWorld) : 0f;
        public float AngularSpeedDegrees => AngularSpeedRadians * Mathf.Rad2Deg;
        public float AccumulatedRotationDegrees => _accumulatedRotationDegrees;
        public int DetentsPerTurn => magneticDetentsPerTurn;

        public void SetCoastHalfLife(float value)
        {
            coastHalfLife = Mathf.Clamp(value, 0.05f, 30f);
        }

        public void SetResistanceMode(global::ThreeBladeEDC.SpinnerResistanceMode mode)
        {
            resistanceMode = mode;
            _ratchetInitialFlickForce = 0f;
            _ratchetInitialFlickClicksRemaining = 0;
            if (mode == global::ThreeBladeEDC.SpinnerResistanceMode.MagneticDetent
                && Mathf.Abs(AngularSpeedRadians) <= magneticCaptureSpeed)
            {
                BeginMagneticCapture(false);
            }
            else
            {
                _magneticLocked = false;
                _magneticCapturePending = false;
            }
            ResetDetentTracking();
        }

        public void SetMagneticDetentsPerTurn(int value)
        {
            magneticDetentsPerTurn = Mathf.Clamp(value, 1, 120);
            ResetDetentTracking();
            if (_magneticLocked)
            {
                BeginMagneticCapture(false);
            }
        }

        public void SetMagneticBreakawaySpeed(float value)
        {
            magneticBreakawaySpeed = Mathf.Clamp(value, 0f, 20f);
        }

        public void SetMagneticCaptureSpeed(float value)
        {
            magneticCaptureSpeed = Mathf.Clamp(value, 0f, 12f);
        }

        public void SetMagneticSnapResponse(float value)
        {
            magneticSnapResponse = Mathf.Clamp(value, 0.1f, 40f);
        }

        public void SetMaximumAngularSpeed(float value)
        {
            maxAngularSpeed = Mathf.Clamp(value, 0.1f, 80f);
            if (_body != null)
            {
                _body.maxAngularVelocity = maxAngularSpeed;
            }
        }

        public void SetReversalStopDuration(float value)
        {
            reversalStopDuration = Mathf.Clamp(value, 0.05f, 1.5f);
        }

        public void SetFlipMotion(float duration, float overshoot)
        {
            flipDuration = Mathf.Clamp(duration, 0.05f, 2f);
            flipOvershoot = Mathf.Clamp(overshoot, 0f, 0.25f);
            _flipBackCoefficient =
                global::ThreeBladeEDC.FidgetSpinnerMotion
                    .BackCoefficientForOvershoot(flipOvershoot);
        }

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

            // The center is already fully constrained by Rigidbody constraints.
            // Keeping a HingeJoint active as a second positional solver makes the
            // small mobile model twitch when its rotation is updated quickly.
            if (hingeJoint != null)
            {
                Destroy(hingeJoint);
                hingeJoint = null;
            }

            _flipBackCoefficient =
                global::ThreeBladeEDC.FidgetSpinnerMotion
                    .BackCoefficientForOvershoot(flipOvershoot);

            _initialized = true;
        }

        private void OnDisable()
        {
            _motorActive = false;
            _assistantDriveActive = false;
            _fingerControlling = false;
            CancelFlip(false);
        }

        private void OnValidate()
        {
            if (spinAxis.sqrMagnitude <= Mathf.Epsilon)
            {
                spinAxis = Vector3.up;
            }

            coastHalfLife = Mathf.Max(0.05f, coastHalfLife);
            maxAngularSpeed = Mathf.Max(0.1f, maxAngularSpeed);
            magneticDetentsPerTurn = Mathf.Clamp(magneticDetentsPerTurn, 1, 120);
            magneticBreakawaySpeed = Mathf.Max(0f, magneticBreakawaySpeed);
            magneticCaptureSpeed = Mathf.Max(0f, magneticCaptureSpeed);
            magneticSnapResponse = Mathf.Max(0.1f, magneticSnapResponse);
            reversalStopDuration = Mathf.Max(0.05f, reversalStopDuration);
            stoppedSpeedThreshold = Mathf.Max(0f, stoppedSpeedThreshold);
            flipDuration = Mathf.Max(0.05f, flipDuration);
            flipOvershoot = Mathf.Clamp(flipOvershoot, 0f, 0.25f);
            _flipBackCoefficient =
                global::ThreeBladeEDC.FidgetSpinnerMotion
                    .BackCoefficientForOvershoot(flipOvershoot);
        }

        private void FixedUpdate()
        {
            if (_body == null)
            {
                return;
            }

            if (_isFlipping)
            {
                UpdateFlip();
                return;
            }

            if (_body.isKinematic)
            {
                return;
            }

            Vector3 axis = SpinAxisWorld;
            Vector3 angularVelocity = _body.angularVelocity;
            float previousAngle = _accumulatedRotationDegrees;
            float axialSpeed = Mathf.Clamp(
                Vector3.Dot(angularVelocity, axis),
                -maxAngularSpeed,
                maxAngularSpeed);

            if (_hasPendingSpinVelocity)
            {
                axialSpeed = Mathf.Clamp(
                    _pendingSpinVelocity,
                    -maxAngularSpeed,
                    maxAngularSpeed);
                _hasPendingSpinVelocity = false;
            }

            if (_assistantDriveActive && !_fingerControlling)
            {
                _isSmoothStopping = false;
                _magneticLocked = false;
                _magneticCapturePending = false;
                axialSpeed = Mathf.Lerp(
                    axialSpeed,
                    _assistantTargetSpeed,
                    1f - Mathf.Exp(-Time.fixedUnscaledDeltaTime * 2.8f));
            }
            else if (_isSmoothStopping)
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
            else if (!_fingerControlling)
            {
                if (resistanceMode == global::ThreeBladeEDC.SpinnerResistanceMode.MagneticDetent)
                {
                    if (!_magneticLocked && Mathf.Abs(axialSpeed) <= magneticCaptureSpeed)
                    {
                        BeginMagneticCapture(true);
                    }

                    if (_magneticLocked)
                    {
                        axialSpeed = CalculateMagneticSnapSpeed(axis);
                    }
                    else
                    {
                        axialSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion.ApplyCoastHalfLife(
                            axialSpeed,
                            Time.fixedUnscaledDeltaTime,
                            coastHalfLife);
                    }
                }
                else
                {
                    axialSpeed = global::ThreeBladeEDC.FidgetSpinnerMotion.ApplyCoastHalfLife(
                        axialSpeed,
                        Time.fixedUnscaledDeltaTime,
                        coastHalfLife);
                }

                if (!_magneticLocked && Mathf.Abs(axialSpeed) <= stoppedSpeedThreshold)
                {
                    axialSpeed = 0f;
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

            _accumulatedRotationDegrees +=
                axialSpeed * Mathf.Rad2Deg * Time.fixedDeltaTime;
            TrackDetentCrossing(previousAngle, _accumulatedRotationDegrees, axialSpeed);
        }

        public void BeginFingerControl()
        {
            _fingerControlling = true;
            _isSmoothStopping = false;
            _hasPendingSpinVelocity = false;
            _ratchetInitialFlickForce = 0f;
            _ratchetInitialFlickClicksRemaining = 0;
        }

        public bool DriveFromFinger(float radiansPerSecond)
        {
            BeginFingerControl();
            float clampedSpeed = Mathf.Clamp(
                radiansPerSecond,
                -maxAngularSpeed,
                maxAngularSpeed);

            if (resistanceMode == global::ThreeBladeEDC.SpinnerResistanceMode.MagneticDetent
                && _magneticLocked)
            {
                if (!global::ThreeBladeEDC.FidgetSpinnerMotion.BreaksMagneticDetent(
                        clampedSpeed,
                        magneticBreakawaySpeed))
                {
                    _pendingSpinVelocity = 0f;
                    _hasPendingSpinVelocity = true;
                    return false;
                }

                _magneticLocked = false;
                _magneticCapturePending = false;
                EmitSemantic(
                    FidgetSemanticEvent.Breakaway,
                    Mathf.Abs(clampedSpeed) / Mathf.Max(0.1f, maxAngularSpeed));
            }

            SetSpinVelocity(clampedSpeed);
            return true;
        }

        public void EndFingerControl()
        {
            _fingerControlling = false;
            if (resistanceMode == global::ThreeBladeEDC.SpinnerResistanceMode.MagneticDetent
                && Mathf.Abs(AngularSpeedRadians) <= magneticCaptureSpeed)
            {
                BeginMagneticCapture(true);
            }
        }

        private void BeginMagneticCapture(bool emitWhenSettled)
        {
            bool wasLocked = _magneticLocked;
            _magneticLocked = true;
            _magneticCapturePending = emitWhenSettled && !wasLocked;
            _magneticSnapTargetDegrees =
                global::ThreeBladeEDC.FidgetSpinnerMotion.NearestDetentDegrees(
                    _accumulatedRotationDegrees,
                    magneticDetentsPerTurn);
        }

        private float CalculateMagneticSnapSpeed(Vector3 axis)
        {
            float errorDegrees = _magneticSnapTargetDegrees - _accumulatedRotationDegrees;
            if (Mathf.Abs(errorDegrees) <= 0.12f)
            {
                if (Mathf.Abs(errorDegrees) > Mathf.Epsilon)
                {
                    _body.MoveRotation(
                        Quaternion.AngleAxis(errorDegrees, axis) * _body.rotation);
                }
                _accumulatedRotationDegrees = _magneticSnapTargetDegrees;
                ResetDetentTracking();
                if (_magneticCapturePending)
                {
                    _magneticCapturePending = false;
                    EmitSemantic(FidgetSemanticEvent.DetentCaptured, 0.5f);
                }
                return 0f;
            }

            float requested = errorDegrees * Mathf.Deg2Rad * magneticSnapResponse;
            float maximumSnapSpeed = Mathf.Max(0.25f, magneticCaptureSpeed * 1.5f);
            return Mathf.Clamp(requested, -maximumSnapSpeed, maximumSnapSpeed);
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
            _flipDirection = direction == 0f ? 1f : Mathf.Sign(direction);
            _flipStartRotation = _body.rotation;
            _flipAxisWorld = SpinAxisWorld;
            _flipResumeSpeed = AngularSpeedRadians;
            _flipCollisionState = _body.detectCollisions;
            _hasPendingSpinVelocity = false;
            _isSmoothStopping = false;
            _motorActive = false;
            _flipBackCoefficient =
                global::ThreeBladeEDC.FidgetSpinnerMotion
                    .BackCoefficientForOvershoot(flipOvershoot);
            _body.angularVelocity = Vector3.zero;
            _body.detectCollisions = false;
            _body.isKinematic = true;
        }

        private void UpdateFlip()
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
            Quaternion rotation = Quaternion.AngleAxis(angle, _flipAxisWorld);
            _body.MoveRotation(rotation * _flipStartRotation);

            if (progress >= 1f)
            {
                _accumulatedRotationDegrees += _flipDirection * 360f;
                CancelFlip(true);
            }
        }

        private void CancelFlip(bool restoreSpin)
        {
            if (!_isFlipping || _body == null)
            {
                return;
            }

            _isFlipping = false;
            _flipElapsed = 0f;
            _body.rotation = _flipStartRotation;
            _body.isKinematic = false;
            _body.detectCollisions = _flipCollisionState;
            _body.angularVelocity = restoreSpin
                ? _flipAxisWorld * Mathf.Clamp(_flipResumeSpeed, -maxAngularSpeed, maxAngularSpeed)
                : Vector3.zero;
            _body.WakeUp();
        }

        /// <summary>
        /// Adds a flick to the current axial speed. The requested change is
        /// clamped before being written to the Rigidbody.
        /// </summary>
        public void AddFlickVelocity(float deltaRadiansPerSecond)
        {
            SetSpinVelocity(AngularSpeedRadians + deltaRadiansPerSecond);
            RecordInitialFlickForce(
                Mathf.Abs(deltaRadiansPerSecond) / Mathf.Max(0.1f, maxAngularSpeed));
        }

        /// <summary>
        /// Captures input force for audio emphasis on the next few actual
        /// detent crossings. This metadata never changes angular velocity.
        /// </summary>
        public void RecordInitialFlickForce(float normalizedForce)
        {
            _ratchetInitialFlickForce = Mathf.Clamp01(normalizedForce);
            _ratchetInitialFlickClicksRemaining =
                RatchetAudioPhysicsModel.InitialFlickClickCount;
        }

        /// <summary>
        /// Sets only the axial component of Rigidbody.angularVelocity.
        /// </summary>
        public void SetSpinVelocity(float radiansPerSecond)
        {
            if (_body == null)
            {
                return;
            }

            _isSmoothStopping = false;
            float clampedSpeed = Mathf.Clamp(
                radiansPerSecond,
                -maxAngularSpeed,
                maxAngularSpeed);

            if (_isFlipping)
            {
                _flipResumeSpeed = clampedSpeed;
                return;
            }

            if (_body.isKinematic)
            {
                return;
            }

            _pendingSpinVelocity = clampedSpeed;
            _hasPendingSpinVelocity = true;
            _body.WakeUp();
        }

        public void SetMotorActive(bool active)
        {
            // Product builds are always finger-driven. The historical demo
            // motor is deliberately disabled so no code path can self-spin.
            _motorActive = false;
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
            _hasPendingSpinVelocity = false;
            _activeStopDuration = duration > 0f
                ? Mathf.Max(0.05f, duration)
                : reversalStopDuration;
            _isSmoothStopping = true;
            _body.WakeUp();
        }

        public void Stop()
        {
            _motorActive = false;
            _fingerControlling = false;
            _isSmoothStopping = false;
            _smoothStopElapsed = 0f;
            _hasPendingSpinVelocity = false;
            _ratchetInitialFlickForce = 0f;
            _ratchetInitialFlickClicksRemaining = 0;
            CancelFlip(false);

            if (_body != null && !_body.isKinematic)
            {
                Vector3 axis = SpinAxisWorld;
                Vector3 offAxisVelocity = constrainToSpinAxis
                    ? Vector3.zero
                    : _body.angularVelocity
                        - axis * Vector3.Dot(_body.angularVelocity, axis);
                _body.angularVelocity = offAxisVelocity;
            }

            if (resistanceMode == global::ThreeBladeEDC.SpinnerResistanceMode.MagneticDetent)
            {
                BeginMagneticCapture(true);
            }
        }

        public void ResetRotor()
        {
            if (!_initialized || _body == null)
            {
                return;
            }

            _motorActive = false;
            _assistantDriveActive = false;
            _isSmoothStopping = false;
            _smoothStopElapsed = 0f;
            _hasPendingSpinVelocity = false;
            _ratchetInitialFlickForce = 0f;
            _ratchetInitialFlickClicksRemaining = 0;
            _fingerControlling = false;
            CancelFlip(false);
            _body.position = _initialPosition;
            _body.rotation = _initialRotation;
            if (!_body.isKinematic)
            {
                _body.linearVelocity = Vector3.zero;
                _body.angularVelocity = Vector3.zero;
            }
            _accumulatedRotationDegrees = 0f;
            _magneticSnapTargetDegrees = 0f;
            _magneticLocked = resistanceMode
                == global::ThreeBladeEDC.SpinnerResistanceMode.MagneticDetent;
            _magneticCapturePending = false;
            ResetDetentTracking();
            if (!_body.isKinematic)
            {
                _body.Sleep();
            }
            ResetPerformed?.Invoke();
        }

        /// <summary>
        /// Explicit, user-controlled slow drive used by the assistant button.
        /// It is separate from the legacy motor state and always defaults off.
        /// </summary>
        public void SetAssistantDrive(bool active, float radiansPerSecond)
        {
            _assistantDriveActive = active;
            _assistantTargetSpeed = Mathf.Clamp(
                Mathf.Abs(radiansPerSecond),
                0.35f,
                Mathf.Max(0.35f, maxAngularSpeed));
            if (active)
            {
                _isSmoothStopping = false;
                _magneticLocked = false;
                _magneticCapturePending = false;
                _body?.WakeUp();
            }
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
            ResetDetentTracking();
        }

        private void TrackDetentCrossing(
            float previousAngle,
            float currentAngle,
            float angularSpeed)
        {
            int previousIndex = global::ThreeBladeEDC.FidgetSpinnerMotion.DetentIndex(
                previousAngle,
                magneticDetentsPerTurn);
            int currentIndex = global::ThreeBladeEDC.FidgetSpinnerMotion.DetentIndex(
                currentAngle,
                magneticDetentsPerTurn);

            if (!_hasDetentIndex)
            {
                _lastDetentIndex = previousIndex;
                _hasDetentIndex = true;
            }

            int crossedDetents = currentIndex - _lastDetentIndex;
            _lastDetentIndex = currentIndex;
            if (crossedDetents == 0
                || resistanceMode != global::ThreeBladeEDC.SpinnerResistanceMode.MagneticDetent
                || _magneticLocked)
            {
                return;
            }

            float normalizedSpeed = Mathf.Clamp01(
                Mathf.Abs(angularSpeed) / Mathf.Max(0.1f, maxAngularSpeed));
            int direction = Math.Sign(crossedDetents);
            int crossingCount = RatchetAudioPhysicsModel.CrossedDetentCount(
                _lastDetentIndex - crossedDetents,
                _lastDetentIndex);
            int firstCrossedIndex = currentIndex - crossedDetents + direction;
            for (int crossing = 0; crossing < crossingCount; crossing++)
            {
                int flickClickIndex = _ratchetInitialFlickClicksRemaining > 0
                    ? RatchetAudioPhysicsModel.InitialFlickClickCount
                        - _ratchetInitialFlickClicksRemaining
                    : -1;
                float flickForce = flickClickIndex >= 0
                    ? _ratchetInitialFlickForce
                    : 0f;

                EmitSemantic(FidgetSemanticEvent.DetentCrossed, normalizedSpeed);
                RatchetDetentCrossed?.Invoke(new RatchetDetentAudioSignal(
                    normalizedSpeed,
                    flickForce,
                    flickClickIndex,
                    firstCrossedIndex + crossing * direction));

                if (_ratchetInitialFlickClicksRemaining > 0)
                {
                    _ratchetInitialFlickClicksRemaining--;
                    if (_ratchetInitialFlickClicksRemaining == 0)
                    {
                        _ratchetInitialFlickForce = 0f;
                    }
                }
            }
        }

        private void ResetDetentTracking()
        {
            _lastDetentIndex = global::ThreeBladeEDC.FidgetSpinnerMotion.DetentIndex(
                _accumulatedRotationDegrees,
                magneticDetentsPerTurn);
            _hasDetentIndex = true;
        }

        private void EmitSemantic(FidgetSemanticEvent semanticEvent, float normalizedSignal)
        {
            SemanticEventRaised?.Invoke(semanticEvent, Mathf.Clamp01(normalizedSignal));
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
            _body.angularDamping = 0f;
            _body.maxAngularVelocity = maxAngularSpeed;
            _body.interpolation = interpolation;
            _body.collisionDetectionMode = CollisionDetectionMode.Discrete;
            _body.solverIterations = 12;
            _body.solverVelocityIterations = 4;

            _body.constraints = RigidbodyConstraints.FreezePosition
                | RigidbodyConstraints.FreezeRotationX
                | RigidbodyConstraints.FreezeRotationZ;

            if (freezeCenterWithoutHinge && hingeJoint == null)
            {
                _body.constraints |= RigidbodyConstraints.FreezePosition;
            }
        }
    }
}
