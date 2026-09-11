using UnityEngine;

namespace FidgetingApp.EDC.Gate12R002
{
    [CreateAssetMenu(
        fileName = "MagneticSlideTileMechanismSettingsR002",
        menuName = "Fidgeting/EDC/Magnetic Slide Gate 12 Settings")]
    public sealed class MagneticSlideTileMechanismSettings : ScriptableObject
    {
        [SerializeField] private float maximumTravelMeters = 0.018076433f;
        [SerializeField] private float endpointToleranceMeters = 0.000001f;
        [SerializeField, Min(1)] private int slideStepCount = 4;
        [SerializeField] private int detentCount = 30;
        [SerializeField] private float detentStepDegrees = 12f;
        [SerializeField] private float breakawayDegrees = 2.4f;
        [SerializeField] private float captureRadiusDegrees = 5.4f;

        public float MaximumTravelMeters => maximumTravelMeters;
        public float EndpointToleranceMeters => endpointToleranceMeters;
        public int SlideStepCount => Mathf.Max(1, slideStepCount);
        public float SlideStepMeters => MaximumTravelMeters / SlideStepCount;
        public int DetentCount => detentCount;
        public float DetentStepDegrees => detentStepDegrees;
        public float BreakawayDegrees => breakawayDegrees;
        public float CaptureRadiusDegrees => captureRadiusDegrees;
    }
}
