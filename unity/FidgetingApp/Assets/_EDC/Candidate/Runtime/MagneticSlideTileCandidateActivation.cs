using UnityEngine;

namespace FidgetingApp.EDC.Candidate
{
    [DisallowMultipleComponent]
    public sealed class MagneticSlideTileCandidateActivation : MonoBehaviour
    {
        [SerializeField] private GameObject shippingModel;
        [SerializeField] private GameObject candidateModel;
        [SerializeField] private bool candidatePreviewEnabled;

        public bool CandidatePreviewEnabled => candidatePreviewEnabled;
        public GameObject ShippingModel => shippingModel;
        public GameObject CandidateModel => candidateModel;

        public void Configure(GameObject currentShippingModel, GameObject previewCandidate)
        {
            shippingModel = currentShippingModel;
            candidateModel = previewCandidate;
            candidatePreviewEnabled = false;
            Apply();
        }

        public void SetCandidatePreview(bool enabled)
        {
            candidatePreviewEnabled = enabled;
            Apply();
        }

        private void Awake()
        {
            Apply();
        }

        private void OnValidate()
        {
            if (!Application.isPlaying)
            {
                Apply();
            }
        }

        private void Apply()
        {
            if (shippingModel != null)
            {
                shippingModel.SetActive(!candidatePreviewEnabled);
            }
            if (candidateModel != null)
            {
                candidateModel.SetActive(candidatePreviewEnabled);
            }
        }
    }
}
