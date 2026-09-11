using UnityEngine;

namespace FidgetingApp.EDC.Candidates
{
    public sealed class MagneticSlideTileGate11R011Metadata : MonoBehaviour
    {
        [SerializeField] private string gate10GlbSha256 =
            "e9f90e9e77756b33857726f95a01194996469f16101dbad91fdb7024b679c2ca";
        [SerializeField] private string geometryDigest =
            "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952";
        [SerializeField] private string portabilityContractSha256 =
            "d172c64ce56f89170b9f072e8efe61c3c7e8277235228bac957229ea319ffd13";
        [SerializeField] private float maximumTravelMeters = 0.018076433f;
        [SerializeField] private int detentCount = 30;
        [SerializeField] private float detentStepDegrees = 12f;
        [SerializeField] private string deliveryState =
            "isolated-gate11-parity-only-not-shipping";

        public string Gate10GlbSha256 => gate10GlbSha256;
        public string GeometryDigest => geometryDigest;
        public string PortabilityContractSha256 => portabilityContractSha256;
        public float MaximumTravelMeters => maximumTravelMeters;
        public int DetentCount => detentCount;
        public float DetentStepDegrees => detentStepDegrees;
        public string DeliveryState => deliveryState;
    }
}
