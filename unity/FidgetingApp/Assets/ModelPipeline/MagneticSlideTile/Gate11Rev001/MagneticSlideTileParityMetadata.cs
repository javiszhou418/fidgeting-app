using UnityEngine;

namespace FidgetingApp.ModelPipeline
{
    public sealed class MagneticSlideTileParityMetadata : MonoBehaviour
    {
        public Vector3 PointAxisMeters = new(0f, 0f, 0.0095f);
        public Vector3 PointAxisDirection = Vector3.up;
        public Vector3 SlideDirection = Vector3.back;
        public float SlideTravelMeters = 0.021f;
        public int DetentCount = 30;
        public float DetentStepDegrees = 12f;
        public string DetentDeliveryState = "specified-only";
        public string UnityIntegrationState = "isolated-gate11-parity-only";
    }
}
