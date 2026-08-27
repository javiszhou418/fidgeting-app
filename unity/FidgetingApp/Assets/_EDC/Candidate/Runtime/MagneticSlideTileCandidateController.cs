using System;
using UnityEngine;

namespace FidgetingApp.EDC.Candidate
{
    [DisallowMultipleComponent]
    public sealed class MagneticSlideTileCandidateController : MonoBehaviour
    {
        [SerializeField] private Transform upperPivot;
        [SerializeField] private MagneticSlideTileCandidateSettings settings;
        [SerializeField, Range(0f, 1f)] private float slideProgress;
        [SerializeField] private int capturedDetentIndex;

        [SerializeField, HideInInspector] private Vector3 closedLocalPosition;
        [SerializeField, HideInInspector] private Quaternion closedLocalRotation = Quaternion.identity;
        [SerializeField, HideInInspector] private bool hasClosedPose;

        public event Action<int> DetentCrossed;

        public MagneticSlideTileCandidateSettings Settings => settings;
        public float SlideProgress => slideProgress;
        public int CapturedDetentIndex => capturedDetentIndex;
        public float AngularVelocityDegreesPerSecond { get; private set; }
        public float LinearVelocityMetersPerSecond { get; private set; }
        public bool RuntimeInputIntegrated => false;
        public bool HapticsIntegrated => false;

        public void Configure(
            Transform pivot,
            MagneticSlideTileCandidateSettings sharedSettings)
        {
            upperPivot = pivot;
            settings = sharedSettings;
            closedLocalPosition = upperPivot != null
                ? upperPivot.localPosition
                : Vector3.zero;
            closedLocalRotation = upperPivot != null
                ? upperPivot.localRotation
                : Quaternion.identity;
            hasClosedPose = upperPivot != null;
            ResetPose();
        }

        private void Awake()
        {
            if (upperPivot != null && !hasClosedPose)
            {
                closedLocalPosition = upperPivot.localPosition;
                closedLocalRotation = upperPivot.localRotation;
                hasClosedPose = true;
            }
            ResetPose();
        }

        public void ResetPose()
        {
            slideProgress = 0f;
            capturedDetentIndex = 0;
            AngularVelocityDegreesPerSecond = 0f;
            LinearVelocityMetersPerSecond = 0f;
            ApplyPose();
        }

        public void SetSlideProgress(float progress)
        {
            slideProgress = Mathf.Clamp01(progress);
            LinearVelocityMetersPerSecond = 0f;
            ApplyPose();
        }

        public void SetDetentIndex(int index)
        {
            if (settings == null || settings.DetentCount <= 0)
            {
                capturedDetentIndex = 0;
                AngularVelocityDegreesPerSecond = 0f;
                ApplyPose();
                return;
            }

            int normalized = ((index % settings.DetentCount) + settings.DetentCount)
                % settings.DetentCount;
            if (normalized != capturedDetentIndex)
            {
                capturedDetentIndex = normalized;
                DetentCrossed?.Invoke(normalized);
            }
            AngularVelocityDegreesPerSecond = 0f;
            ApplyPose();
        }

        private void ApplyPose()
        {
            if (upperPivot == null || settings == null)
            {
                return;
            }

            Vector3 worldDelta = transform.TransformDirection(settings.SlideDirection)
                * settings.SlideTravelMeters
                * slideProgress;
            Vector3 localDelta = upperPivot.parent != null
                ? upperPivot.parent.InverseTransformVector(worldDelta)
                : worldDelta;
            upperPivot.localPosition = closedLocalPosition + localDelta;
            upperPivot.localRotation = closedLocalRotation
                * Quaternion.AngleAxis(
                    capturedDetentIndex * settings.DetentStepDegrees,
                    Vector3.up);
        }
    }
}
