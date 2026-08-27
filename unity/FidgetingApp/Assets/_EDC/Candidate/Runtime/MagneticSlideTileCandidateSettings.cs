using UnityEngine;

namespace FidgetingApp.EDC.Candidate
{
    [CreateAssetMenu(
        fileName = "MagneticSlideTileCandidateSettings",
        menuName = "Fidgeting/Magnetic Slide Tile Candidate Settings")]
    public sealed class MagneticSlideTileCandidateSettings : ScriptableObject
    {
        public const float LockedSlideTravelMeters = 0.021f;
        public const int LockedDetentCount = 30;
        public const float LockedDetentStepDegrees = 12f;

        [SerializeField] private float slideTravelMeters = LockedSlideTravelMeters;
        [SerializeField] private int detentCount = LockedDetentCount;
        [SerializeField] private float detentStepDegrees = LockedDetentStepDegrees;
        [SerializeField] private Vector3 pointAxisMeters = new(0f, 0f, 0.0095f);
        [SerializeField] private Vector3 slideDirection = Vector3.back;

        public float SlideTravelMeters => slideTravelMeters;
        public int DetentCount => detentCount;
        public float DetentStepDegrees => detentStepDegrees;
        public Vector3 PointAxisMeters => pointAxisMeters;
        public Vector3 SlideDirection => slideDirection.normalized;

        public bool IsLockedContractValid =>
            Mathf.Approximately(slideTravelMeters, LockedSlideTravelMeters)
            && detentCount == LockedDetentCount
            && Mathf.Approximately(detentStepDegrees, LockedDetentStepDegrees)
            && Mathf.Approximately(detentCount * detentStepDegrees, 360f);
    }
}
