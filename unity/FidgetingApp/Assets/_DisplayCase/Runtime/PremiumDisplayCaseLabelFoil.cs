using CodexUnityLab;
using UnityEngine;

namespace FidgetingApp.DisplayCase
{
    /// <summary>
    /// Drives the label plate's spectral band from device tilt (R053). The
    /// plate is a passive reflective surface: the band only moves when the
    /// phone moves, plus a slow idle drift so the foil never reads as a flat
    /// print when the device is at rest. No self-motion of the case.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class PremiumDisplayCaseLabelFoil : MonoBehaviour
    {
        public static readonly int SheenPhaseId = Shader.PropertyToID("_SheenPhase");

        /// <summary>Gravity X/Y (−1…1) to phase, in full hue cycles.</summary>
        public const float TiltPhaseGain = 1.35f;
        /// <summary>Idle drift, hue cycles per second.</summary>
        public const float IdleDriftCyclesPerSecond = 0.045f;
        /// <summary>Half-life for following the tilt target, seconds.</summary>
        public const float FollowHalfLifeSeconds = 0.09f;

        [SerializeField] private Renderer plate;

        private MaterialPropertyBlock properties;
        private float phase;
        private float tiltPhase;
        private float idleSeconds;

        public float Phase => phase;
        public Renderer Plate => plate;

        public void ConfigureAuthoring(Renderer plateRenderer)
        {
            plate = plateRenderer;
        }

        private void Update()
        {
            Step(Time.deltaTime);
        }

        /// <summary>Deterministic step; exposed for EditMode tests.</summary>
        public void Step(float deltaSeconds, bool hasMotion, Vector3 gravity)
        {
            idleSeconds += deltaSeconds;
            float target = hasMotion
                ? Mathf.Clamp(gravity.x, -1f, 1f) * TiltPhaseGain
                    + Mathf.Clamp(gravity.y, -1f, 1f) * TiltPhaseGain * 0.5f
                : 0f;
            float k = FollowHalfLifeSeconds <= 0f
                ? 1f
                : 1f - Mathf.Pow(0.5f, deltaSeconds / FollowHalfLifeSeconds);
            tiltPhase = Mathf.Lerp(tiltPhase, target, k);
            phase = tiltPhase + idleSeconds * IdleDriftCyclesPerSecond;
            Apply();
        }

        private void Step(float deltaSeconds)
        {
            bool hasMotion = IosDeviceMotion.TryRead(
                out _,
                out _,
                out Vector3 gravity,
                out _);
            Step(deltaSeconds, hasMotion, gravity);
        }

        private void Apply()
        {
            if (plate == null)
            {
                return;
            }
            properties ??= new MaterialPropertyBlock();
            plate.GetPropertyBlock(properties);
            properties.SetFloat(SheenPhaseId, phase);
            plate.SetPropertyBlock(properties);
        }
    }
}
