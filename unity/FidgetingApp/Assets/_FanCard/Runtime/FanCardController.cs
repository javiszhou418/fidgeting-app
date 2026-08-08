using System;
using CodexUnityLab;
using FidgetingApp.EDC;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;
using UnityEngine.Serialization;

namespace FidgetingApp.FanCard
{
    [DisallowMultipleComponent]
    public sealed class FanCardController : MonoBehaviour
    {
        [SerializeField] private Transform middleLayer;
        [FormerlySerializedAs("topLayer")]
        [SerializeField] private Transform outerLayer;
        [SerializeField] private Camera interactionCamera;
        [SerializeField] private Collider interactionSurface;
        [SerializeField] private FanCardDetentProfile detentProfile;
        [SerializeField, Min(0f)] private float maximumRayDistance = 5f;

        [SerializeField, HideInInspector]
        private Quaternion middleClosedRotation = Quaternion.identity;
        [SerializeField, HideInInspector]
        private Quaternion outerClosedRotation = Quaternion.identity;
        private FanCardMagneticTrack track;
        private FanCardDetentProfile ownedRuntimeProfile;
        private bool pointerWasPressed;
        private bool dragging;
        private bool interactionHapticsAuthorized;
        private bool gestureBrokeAway;
        private Vector2 pointerStartPosition;
        private Vector2 previousPointerPosition;
        private float pointerStartAngle;
        private float pointerStartTarget;
        private float handTarget;
        private float openingScreenDirection = 1f;
        private float previousProgress;
        private float accumulatedActivityDegrees;
        private float activitySpeedRadians;
        private bool assistantDriveActive;
        private float assistantDirection = 1f;
        private float assistantSpeed = 0.20f;

        public event Action<float> InteractionGestureCompleted;
        public event Action<FidgetSemanticEvent, float> SemanticEventRaised;

        public float Progress => track?.Position ?? 0f;
        public int CapturedDetentIndex => track?.CapturedDetentIndex ?? 0;
        public float MaximumRelativeAngleDegrees =>
            detentProfile != null
                ? detentProfile.MaximumRelativeAngleDegrees
                : FanCardDetentProfile.ReferenceMaximumRelativeAngleDegrees;
        public float MaximumTotalAngleDegrees =>
            detentProfile != null
                ? detentProfile.MaximumTotalAngleDegrees
                : FanCardDetentProfile.ReferenceMaximumTotalAngleDegrees;
        public bool IsDragging => dragging;
        public bool IsSettling => assistantDriveActive
            || (track != null && track.State == MagneticDetentState.Capturing);
        public bool IsAssistantDriving => assistantDriveActive;
        public float AccumulatedActivityDegrees => accumulatedActivityDegrees;
        public float ActivitySpeedRadians => activitySpeedRadians;
        public MagneticDetentState MotionState =>
            track?.State ?? MagneticDetentState.Captured;
        public float MagneticLoad => track?.LoadNormalized ?? 0f;
        public Camera InteractionCamera => interactionCamera;
        public Collider InteractionSurface => interactionSurface;
        public FanCardDetentProfile Profile => detentProfile;

        public void Configure(
            Transform middle,
            Transform outer,
            Camera camera,
            Collider surface,
            FanCardDetentProfile profile)
        {
            middleLayer = middle;
            outerLayer = outer;
            interactionCamera = camera;
            interactionSurface = surface;
            detentProfile = profile;
            CacheClosedRotations();
            InitializeTrack(0f);
        }

        private void Awake()
        {
            EnsureProfile();
            CacheClosedRotations();
            InitializeTrack(0f);
        }

        private void Update()
        {
            if (TryReadTouch(out Vector2 touchPosition, out bool touchPressed))
            {
                UpdatePointer(touchPosition, touchPressed);
            }
            else
            {
                ReadMouse();
            }

            float deltaTime = Mathf.Max(0f, Time.unscaledDeltaTime);
            bool handActive = dragging;
            bool hapticAuthorized = interactionHapticsAuthorized;
            if (assistantDriveActive && !dragging && !pointerWasPressed)
            {
                AdvanceAssistantTarget(deltaTime);
                handActive = true;
                hapticAuthorized = false;
            }

            AdvancePhysics(deltaTime, handTarget, handActive, hapticAuthorized);
            UpdateActivity(deltaTime);
        }

        private void OnDisable()
        {
            dragging = false;
            pointerWasPressed = false;
            assistantDriveActive = false;
            interactionHapticsAuthorized = false;
            gestureBrokeAway = false;
            if (track != null && !track.IsAtRest)
            {
                track.Release();
            }
        }

        private void OnDestroy()
        {
            if (ownedRuntimeProfile == null)
            {
                return;
            }
#if UNITY_EDITOR
            if (!Application.isPlaying)
            {
                DestroyImmediate(ownedRuntimeProfile);
                return;
            }
#endif
            Destroy(ownedRuntimeProfile);
        }

        public bool ContainsScreenPoint(Vector2 screenPosition)
        {
            Camera camera = interactionCamera != null ? interactionCamera : Camera.main;
            if (camera == null || interactionSurface == null)
            {
                return false;
            }
            return interactionSurface.Raycast(
                camera.ScreenPointToRay(screenPosition),
                out _,
                maximumRayDistance);
        }

        public void ResetClosed()
        {
            EnsureTrack();
            dragging = false;
            pointerWasPressed = false;
            assistantDriveActive = false;
            interactionHapticsAuthorized = false;
            gestureBrokeAway = false;
            track.ResetToDetent(0);
            handTarget = 0f;
            previousProgress = 0f;
            accumulatedActivityDegrees = 0f;
            activitySpeedRadians = 0f;
            ApplyVisualPose();
        }

        public void SetFanProgress(float progress)
        {
            EnsureClosedRotations();
            EnsureTrack();
            dragging = false;
            pointerWasPressed = false;
            assistantDriveActive = false;
            interactionHapticsAuthorized = false;
            gestureBrokeAway = false;
            track.ResetToPosition(progress);
            handTarget = track.Position;
            previousProgress = track.Position;
            accumulatedActivityDegrees = 0f;
            activitySpeedRadians = 0f;
            ApplyVisualPose();
        }

        public void ReleaseDrag()
        {
            dragging = false;
            interactionHapticsAuthorized = false;
            track?.Release();
        }

        public void SetAssistantDrive(bool active, float sourceSpeedMetersPerSecond)
        {
            EnsureTrack();
            assistantDriveActive = active;
            interactionHapticsAuthorized = false;
            gestureBrokeAway = false;
            assistantSpeed = Mathf.Clamp(
                Mathf.Abs(sourceSpeedMetersPerSecond) / 0.030f * 0.20f,
                0.08f,
                0.55f);
            handTarget = track.Position;
            if (track.Position >= 0.88f)
            {
                assistantDirection = -1f;
            }
            else if (track.Position <= 0.12f)
            {
                assistantDirection = 1f;
            }
            if (!active && !track.IsAtRest)
            {
                track.Release();
            }
        }

        private void EnsureProfile()
        {
            if (detentProfile != null)
            {
                return;
            }
            ownedRuntimeProfile = ScriptableObject.CreateInstance<
                FanCardDetentProfile>();
            ownedRuntimeProfile.name = "Runtime_FanCardDetentProfile";
            ownedRuntimeProfile.hideFlags = HideFlags.HideAndDontSave;
            ownedRuntimeProfile.ApplyReferenceDefaults();
            detentProfile = ownedRuntimeProfile;
        }

        private void EnsureTrack()
        {
            if (track == null)
            {
                InitializeTrack(0f);
            }
        }

        private void InitializeTrack(float progress)
        {
            EnsureProfile();
            track = new FanCardMagneticTrack(detentProfile);
            track.ResetToPosition(progress);
            handTarget = track.Position;
            previousProgress = track.Position;
            ApplyVisualPose();
        }

        private void CacheClosedRotations()
        {
            middleClosedRotation = middleLayer != null
                ? middleLayer.localRotation
                : Quaternion.identity;
            outerClosedRotation = outerLayer != null
                ? outerLayer.localRotation
                : Quaternion.identity;
        }

        private void EnsureClosedRotations()
        {
            if (Quaternion.Dot(middleClosedRotation, middleClosedRotation)
                    < 0.5f
                || Quaternion.Dot(outerClosedRotation, outerClosedRotation) < 0.5f)
            {
                CacheClosedRotations();
            }
        }

        private bool TryReadTouch(out Vector2 position, out bool pressed)
        {
            Touchscreen touchscreen = Touchscreen.current;
            if (touchscreen != null)
            {
                TouchControl first = null;
                int count = 0;
                foreach (TouchControl touch in touchscreen.touches)
                {
                    if (!touch.press.isPressed)
                    {
                        continue;
                    }
                    first ??= touch;
                    count++;
                    if (count >= 2)
                    {
                        dragging = false;
                        pointerWasPressed = false;
                        interactionHapticsAuthorized = false;
                        gestureBrokeAway = false;
                        track?.Release();
                        position = first.position.ReadValue();
                        pressed = false;
                        return true;
                    }
                }
                if (first != null)
                {
                    position = first.position.ReadValue();
                    pressed = true;
                    return true;
                }
            }

            if (pointerWasPressed && Mouse.current == null)
            {
                position = previousPointerPosition;
                pressed = false;
                return true;
            }
            position = default;
            pressed = false;
            return false;
        }

        private void ReadMouse()
        {
            Mouse mouse = Mouse.current;
            if (mouse != null)
            {
                UpdatePointer(mouse.position.ReadValue(), mouse.leftButton.isPressed);
            }
        }

        private void UpdatePointer(Vector2 position, bool pressed)
        {
            if (pressed && !pointerWasPressed)
            {
                BeginPointer(position);
            }
            else if (pressed && pointerWasPressed && dragging)
            {
                float currentAngle = PointerAngle(position);
                float delta = Mathf.DeltaAngle(pointerStartAngle, currentAngle)
                    * openingScreenDirection;
                handTarget = Mathf.Clamp01(
                    pointerStartTarget
                        + delta / detentProfile.MaximumTotalAngleDegrees);
            }
            else if (!pressed && pointerWasPressed)
            {
                EndPointer(position);
            }

            previousPointerPosition = position;
            pointerWasPressed = pressed;
        }

        private void BeginPointer(Vector2 position)
        {
            if (EventSystem.current != null
                && EventSystem.current.IsPointerOverGameObject())
            {
                return;
            }
            if (!ContainsScreenPoint(position))
            {
                return;
            }

            EnsureTrack();
            dragging = true;
            assistantDriveActive = false;
            interactionHapticsAuthorized = true;
            gestureBrokeAway = false;
            handTarget = track.Position;
            pointerStartTarget = handTarget;
            pointerStartAngle = PointerAngle(position);
            openingScreenDirection = ResolveOpeningScreenDirection();
            pointerStartPosition = position;
            previousPointerPosition = position;
        }

        private void EndPointer(Vector2 position)
        {
            if (!dragging)
            {
                return;
            }
            dragging = false;
            track.Release();
            float travelPixels = Vector2.Distance(pointerStartPosition, position);
            float normalizedForce = Mathf.Clamp01(
                travelPixels / Mathf.Max(1f, Screen.width * 0.34f));
            InteractionGestureCompleted?.Invoke(Mathf.Max(0.18f, normalizedForce));
        }

        private float PointerAngle(Vector2 position)
        {
            Camera camera = interactionCamera != null ? interactionCamera : Camera.main;
            if (camera == null)
            {
                return 0f;
            }
            Vector3 pivot = camera.WorldToScreenPoint(transform.position);
            return Mathf.Atan2(position.y - pivot.y, position.x - pivot.x)
                * Mathf.Rad2Deg;
        }

        private float ResolveOpeningScreenDirection()
        {
            Camera camera = interactionCamera != null ? interactionCamera : Camera.main;
            if (camera == null || outerLayer == null)
            {
                return 1f;
            }

            Vector3 sample = interactionSurface is BoxCollider box
                ? box.center
                : new Vector3(-0.019f, 0f, -0.030f);
            Vector3 pivotScreen = camera.WorldToScreenPoint(transform.position);
            Vector3 currentScreen = camera.WorldToScreenPoint(
                outerLayer.TransformPoint(sample));
            Transform parent = outerLayer.parent;
            Quaternion testRotation = outerLayer.localRotation
                * Quaternion.Euler(
                    0f,
                    FanCardSpecifications.OpeningRotationSign,
                    0f);
            Vector3 testLocal = outerLayer.localPosition + testRotation * sample;
            Vector3 testWorld = parent != null
                ? parent.TransformPoint(testLocal)
                : testLocal;
            Vector3 testScreen = camera.WorldToScreenPoint(testWorld);
            float currentAngle = Mathf.Atan2(
                currentScreen.y - pivotScreen.y,
                currentScreen.x - pivotScreen.x) * Mathf.Rad2Deg;
            float testAngle = Mathf.Atan2(
                testScreen.y - pivotScreen.y,
                testScreen.x - pivotScreen.x) * Mathf.Rad2Deg;
            float direction = Mathf.Sign(Mathf.DeltaAngle(currentAngle, testAngle));
            return Mathf.Abs(direction) > Mathf.Epsilon ? direction : 1f;
        }

        private void AdvanceAssistantTarget(float deltaTime)
        {
            handTarget = Mathf.Clamp01(
                handTarget + assistantDirection * assistantSpeed * deltaTime);
            if (track.IsAtRest)
            {
                if (track.CapturedDetentIndex >= detentProfile.DetentCount - 1)
                {
                    assistantDirection = -1f;
                }
                else if (track.CapturedDetentIndex <= 0)
                {
                    assistantDirection = 1f;
                }
            }
        }

        private void AdvancePhysics(
            float deltaTime,
            float target,
            bool handActive,
            bool hapticAuthorized)
        {
            EnsureTrack();
            FanCardStepResult result = track.Step(deltaTime, target, handActive);
            if (result.BrokeAway)
            {
                gestureBrokeAway = true;
                EmitSemanticIfAuthorized(
                    FidgetSemanticEvent.Breakaway,
                    1f,
                    hapticAuthorized);
            }
            for (int crossing = 0; crossing < result.CrossedDetentCount; crossing++)
            {
                EmitSemanticIfAuthorized(
                    FidgetSemanticEvent.DetentCrossed,
                    Mathf.Clamp01(Mathf.Abs(track.Velocity) / 1.5f),
                    hapticAuthorized);
            }
            if (result.Captured)
            {
                if (gestureBrokeAway)
                {
                    EmitSemanticIfAuthorized(
                        FidgetSemanticEvent.DetentCaptured,
                        1f,
                        hapticAuthorized);
                }
                gestureBrokeAway = false;
                if (!dragging && !assistantDriveActive)
                {
                    interactionHapticsAuthorized = false;
                }
            }
            ApplyVisualPose();
        }

        private void EmitSemanticIfAuthorized(
            FidgetSemanticEvent semanticEvent,
            float normalizedSignal,
            bool authorized)
        {
            if (authorized)
            {
                SemanticEventRaised?.Invoke(semanticEvent, normalizedSignal);
            }
        }

        private void ApplyVisualPose()
        {
            if (middleLayer == null || outerLayer == null || track == null)
            {
                return;
            }
            float visual = track.VisualPosition;
            middleLayer.localRotation = middleClosedRotation
                * Quaternion.Euler(
                    0f,
                    FanCardSpecifications.OpeningRotationSign
                        * detentProfile.MaximumRelativeAngleDegrees * visual,
                    0f);
            outerLayer.localRotation = outerClosedRotation
                * Quaternion.Euler(
                    0f,
                    FanCardSpecifications.OpeningRotationSign
                        * detentProfile.MaximumTotalAngleDegrees * visual,
                    0f);
        }

        private void UpdateActivity(float deltaTime)
        {
            float current = track?.Position ?? 0f;
            float delta = current - previousProgress;
            previousProgress = current;
            float safeDeltaTime = Mathf.Max(0.0001f, deltaTime);
            if (Mathf.Abs(delta) > 0.00001f)
            {
                float degrees = delta * detentProfile.MaximumTotalAngleDegrees;
                accumulatedActivityDegrees += degrees;
                float rawSpeed = degrees * Mathf.Deg2Rad / safeDeltaTime;
                activitySpeedRadians = Mathf.Lerp(
                    activitySpeedRadians,
                    rawSpeed,
                    1f - Mathf.Exp(-18f * safeDeltaTime));
                return;
            }
            activitySpeedRadians = Mathf.Lerp(
                activitySpeedRadians,
                0f,
                1f - Mathf.Exp(-safeDeltaTime / 0.22f));
            if (Mathf.Abs(activitySpeedRadians) < 0.02f)
            {
                activitySpeedRadians = 0f;
            }
        }
    }
}
