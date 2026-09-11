using UnityEngine;

namespace FidgetingApp.EDC.Gate12R002
{
    [DisallowMultipleComponent]
    public sealed class MagneticSlideTileShippingCoordinator : MonoBehaviour
    {
        [SerializeField] private MagneticSlideTileMechanismSettings settings;
        [SerializeField] private GameObject currentShippingModel;
        [SerializeField] private GameObject candidateModel;
        [SerializeField] private MagneticSlideTileShippingMechanism mechanism;
        [SerializeField] private bool candidatePreviewEnabled;

        public MagneticSlideTileMechanismSettings Settings => settings;
        public MagneticSlideTileShippingMechanism Mechanism => mechanism;
        public GameObject CandidateModel => candidateModel;
        public GameObject FallbackModel => currentShippingModel;
        public bool CandidatePreviewEnabled => candidatePreviewEnabled;
        public bool CandidateModelActive => candidateModel != null
            && candidateModel.activeSelf;
        public bool FallbackModelActive => currentShippingModel != null
            && currentShippingModel.activeSelf;
        public bool DeviceHapticAcceptancePending => true;

        public void Configure(
            MagneticSlideTileMechanismSettings sharedSettings,
            GameObject oldShippingModel,
            GameObject previewCandidate,
            MagneticSlideTileShippingMechanism candidateMechanism)
        {
            settings = sharedSettings;
            currentShippingModel = oldShippingModel;
            candidateModel = previewCandidate;
            mechanism = candidateMechanism;
            candidatePreviewEnabled = false;
            ApplyActivation();
        }

        private void Awake()
        {
            ApplyActivation();
            Debug.Log(
                "[MagneticSlideRuntime] shipping-coordinator-ready "
                + $"candidate={CandidateModelActive} fallback={FallbackModelActive}");
        }

        public void SetPreviewActive(bool active)
        {
            candidatePreviewEnabled = active;
            ApplyActivation();
            if (!active)
                mechanism?.ResetPose(false);
        }

        public bool TryApplySlideInput(
            float requestedTravelMeters,
            bool userAuthorized = true)
        {
            return candidatePreviewEnabled
                && mechanism != null
                && mechanism.TrySetTravel(
                    requestedTravelMeters,
                    userAuthorized);
        }

        public bool TryApplyRotationInput(
            float requestedAngleDegrees,
            bool userAuthorized = true)
        {
            if (!candidatePreviewEnabled || mechanism == null)
                return false;
            float dragDelta = requestedAngleDegrees
                - mechanism.UnwrappedAngleDegrees;
            return mechanism.TryBeginRotation(
                    dragDelta,
                    userAuthorized)
                && mechanism.TrySetAngle(
                    requestedAngleDegrees,
                    userAuthorized);
        }

        public bool TryCaptureRotationInput(
            float requestedAngleDegrees,
            bool userAuthorized = true)
        {
            return candidatePreviewEnabled
                && mechanism != null
                && mechanism.TryCaptureNearestDetent(
                    requestedAngleDegrees,
                    userAuthorized);
        }

        public void ResetShippingPose(bool emitSemantic = true)
        {
            if (candidatePreviewEnabled)
                mechanism?.ResetPose(emitSemantic);
        }

        private void ApplyActivation()
        {
            if (currentShippingModel != null)
                currentShippingModel.SetActive(!candidatePreviewEnabled);
            if (candidateModel != null)
                candidateModel.SetActive(candidatePreviewEnabled);
        }
    }
}
