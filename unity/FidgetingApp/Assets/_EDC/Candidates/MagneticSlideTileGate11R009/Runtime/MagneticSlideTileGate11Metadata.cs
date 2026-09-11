using UnityEngine;

namespace FidgetingApp.EDC.Candidates
{
    public sealed class MagneticSlideTileGate11Metadata : MonoBehaviour
    {
        [SerializeField] private string gate10GlbSha256 =
            "f95b1b2ebed5859aa185aa4e3ba81dcb7a8de266ac9244f4b3270b35c877cba6";
        [SerializeField] private string geometryDigest =
            "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe";
        [SerializeField] private string portabilityContractSha256 =
            "fce83a968df4f978e84ffbab7f026c57d7b60e762d70f7cdb2f2a1aa5cf22134";
        [SerializeField] private Vector3 mechanismAxisPointMeters =
            new(0f, -0.0095f, 0f);
        [SerializeField] private Vector3 blenderAxisObjectOriginMeters =
            new(0f, 0.005075f, 0.009f);
        [SerializeField] private float maximumTravelMeters = 0.018076433f;
        [SerializeField] private int detentCount = 30;
        [SerializeField] private float detentStepDegrees = 12f;
        [SerializeField] private bool provisionalDimensions = true;
        [SerializeField] private string deliveryState =
            "isolated-gate11-parity-only";

        public string Gate10GlbSha256 => gate10GlbSha256;
        public string GeometryDigest => geometryDigest;
        public string PortabilityContractSha256 => portabilityContractSha256;
        public Vector3 MechanismAxisPointMeters => mechanismAxisPointMeters;
        public Vector3 BlenderAxisObjectOriginMeters => blenderAxisObjectOriginMeters;
        public float MaximumTravelMeters => maximumTravelMeters;
        public int DetentCount => detentCount;
        public float DetentStepDegrees => detentStepDegrees;
        public bool ProvisionalDimensions => provisionalDimensions;
        public string DeliveryState => deliveryState;
    }
}
