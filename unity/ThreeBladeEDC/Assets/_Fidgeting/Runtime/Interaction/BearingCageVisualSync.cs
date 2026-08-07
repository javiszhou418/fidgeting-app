using UnityEngine;

namespace ThreeBladeEDC.Interaction
{
    /// <summary>
    /// Drives a bearing-cage visual from the rotor's accumulated physical
    /// rotation. Assigning world rotation makes the result independent of
    /// whether the visual is a child or a sibling of RotorDynamic.
    /// </summary>
    [DisallowMultipleComponent]
    [DefaultExecutionOrder(100)]
    public sealed class BearingCageVisualSync : MonoBehaviour
    {
        [SerializeField] private RotorRigidbodyController rotor;
        [SerializeField] private Transform cageVisual;

        [Tooltip("Cage world rotation divided by rotor rotation. A typical visual value is 0.5.")]
        [SerializeField] private float worldRotationRatio = 0.5f;

        [SerializeField] private float angularOffsetDegrees;

        private Quaternion _baseWorldRotation;
        private float _rotorAngleAtCapture;
        private bool _hasCapturedPose;

        public RotorRigidbodyController Rotor => rotor;
        public Transform CageVisual => cageVisual;

        private void Awake()
        {
            ResolveReferences();
            CaptureVisualPose();
        }

        private void LateUpdate()
        {
            if (rotor == null || cageVisual == null)
            {
                ResolveReferences();
                if (rotor == null || cageVisual == null)
                {
                    return;
                }
            }

            if (!_hasCapturedPose)
            {
                CaptureVisualPose();
            }

            float rotorDelta = rotor.AccumulatedRotationDegrees
                - _rotorAngleAtCapture;
            float cageAngle = rotorDelta * worldRotationRatio
                + angularOffsetDegrees;
            cageVisual.rotation = Quaternion.AngleAxis(
                cageAngle,
                rotor.SpinAxisWorld) * _baseWorldRotation;
        }

        public void Configure(
            RotorRigidbodyController rotorController,
            Transform visual,
            float rotationRatio = 0.5f)
        {
            rotor = rotorController;
            cageVisual = visual != null ? visual : transform;
            worldRotationRatio = rotationRatio;
            CaptureVisualPose();
        }

        /// <summary>
        /// Uses the current visual orientation as the zero-angle reference.
        /// </summary>
        public void CaptureVisualPose()
        {
            ResolveReferences();
            if (rotor == null || cageVisual == null)
            {
                _hasCapturedPose = false;
                return;
            }

            _baseWorldRotation = cageVisual.rotation;
            _rotorAngleAtCapture = rotor.AccumulatedRotationDegrees;
            _hasCapturedPose = true;
        }

        private void ResolveReferences()
        {
            if (rotor == null)
            {
                rotor = GetComponentInParent<RotorRigidbodyController>();
            }

            if (cageVisual == null)
            {
                cageVisual = transform;
            }
        }
    }
}
